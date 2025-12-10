"""Telegram bot service for PropertySphere"""
import asyncio
import logging
import threading
from datetime import datetime, date
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from telegram.constants import ParseMode, ChatAction
from ravendb.documents.subscriptions.document_subscriptions import SubscriptionWorkerOptions
from ravendb.documents.operations.ai.agents import AiConversationCreationOptions
from models import Renter, Lease, ServiceRequest, Photo
from services.property_agent import PropertyAgent
from config import settings

logger = logging.getLogger(__name__)


class TelegramService:
    """Telegram bot service for property management"""
    
    def __init__(self, document_store):
        self.document_store = document_store
        self.application = None
        self._running = False
        self.main_loop = None
        
    async def start(self):
        """Start the Telegram bot"""
        if not settings.telegram_bot_token or settings.telegram_bot_token == "YOUR_TELEGRAM_BOT_TOKEN_HERE":
            logger.warning("Telegram bot token not configured. Telegram service will not start.")
            return
        
        # Build application
        self.application = Application.builder().token(settings.telegram_bot_token).build()
        
        # Add handlers
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
        self.application.add_handler(MessageHandler(filters.PHOTO, self.handle_photo))
        self.application.add_handler(MessageHandler(filters.Document.IMAGE, self.handle_photo))
        self.application.add_handler(CommandHandler("clear", self.handle_clear))
        
        # Start subscription worker for photo analysis notifications in background thread
        self.main_loop= asyncio.get_event_loop()
        threading.Thread(target=self._start_photo_subscription_worker, daemon=True).start()

        # Start polling
        self._running = True
        await self.application.initialize()
        await self.application.start()
        await self.application.updater.start_polling()
        logger.info("Telegram polling service started")
        
    async def stop(self):
        """Stop the Telegram bot"""
        if self.application:
            self._running = False
            await self.application.updater.stop()
            await self.application.stop()
            await self.application.shutdown()
            logger.info("Telegram polling service stopped")
    
    def _start_photo_subscription_worker(self):
        """Run subscription worker in background thread"""
        try:
            logger.info("Photo analysis subscription worker started")
            with self.document_store.subscriptions.get_subscription_worker(
                SubscriptionWorkerOptions("After Photos Analysis"),
                Photo
            ) as worker:
                worker.run(lambda batch: self._process_batch(batch)).result()
            
        except Exception as e:
            logger.error(f"Error in Photos Analysis subscription worker: {e}", exc_info=True)

    def _process_batch(self, batch):
        """Process batch of analyzed photos"""
        logger.info(f"Processing photo analysis batch of {len(batch.items)} items")
        try:
            with batch.open_session() as session:
                logger.info("Opened session for processing photo batch")
                for item in batch.items:
                    photo = item.result
                    
                    renter = session.load(photo.RenterId, Renter)
                    
                    if not renter or not renter.TelegramChatId:
                        continue

                    task = self._process_message(
                        chat_id=renter.TelegramChatId,
                        message_text=(
                            f"Uploaded an image with caption: {photo.Caption}\r\n"
                            f"Image description: {photo.Description}."
                        )
                    )
                    asyncio.run_coroutine_threadsafe(task, self.main_loop).result()
            
        except Exception as e:
            logger.error(f"Error processing photo batch: {e}", exc_info=True)
        
    async def _send_message_to_chat(self, chat_id: str, message: str):
        """Send a message to a Telegram chat"""
        try:
            await self.application.bot.send_message(
                chat_id=chat_id,
                text=message
            )
        except Exception as e:
            logger.error(f"Failed to send message to chat {chat_id}: {e}")
    
    @staticmethod
    def get_conversation_id(chat_id: str) -> str:
        """Generate conversation ID for a chat"""
        return f"chats/{chat_id}/{date.today().strftime('%Y-%m-%d')}"
    
    async def handle_clear(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /clear command to reset conversation"""
        chat_id = str(update.effective_chat.id)
        conversation_id = self.get_conversation_id(chat_id)
        
        with self.document_store.open_session() as session:
            session.delete(conversation_id)
            session.save_changes()
        
        await update.message.reply_text(
            "Conversation history cleared. You can start a new conversation now."
        )
    
    async def handle_photo(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle photo uploads"""
        chat_id = str(update.effective_chat.id)
        
        with self.document_store.open_session() as session:
            renters = list(session.query(object_type=Renter).where_equals(
                "TelegramChatId", chat_id
            ).take(1))
            
            if not renters:
                await update.message.reply_text(
                    "Sorry, your Telegram account is not linked to a renter profile. "
                    "Please contact property management."
                )
                return
            
            renter = renters[0]
            
            if update.message.photo:
                photo_file = await update.message.photo[-1].get_file()
                file_name = "image.jpg"
            elif update.message.document:
                photo_file = await update.message.document.get_file()
                file_name = update.message.document.file_name or "image.jpg"
                
                if not file_name.lower().endswith(('.jpg', '.jpeg')):
                    await update.message.reply_text("Sorry, only JPG/JPEG images are accepted.")
                    return
            else:
                return
            
            photo_bytes = await photo_file.download_as_bytearray()
            
            photo = Photo(
                ConversationId=self.get_conversation_id(chat_id),
                Id=f"photos/{datetime.now().strftime('%Y%m%d%H%M%S')}",
                RenterId=renter.Id,
                Caption=update.message.caption or update.message.text
            )
            
            session.store(photo)
            session.advanced.attachments.store(photo, "image.jpg", photo_bytes)
            session.save_changes()
            
            await update.message.reply_text(
                "Looking at the photo you sent..., may take me a moment..."
            )
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle text messages"""
        chat_id = str(update.effective_chat.id)
        message_text = update.message.text
        
        return await self._process_message(chat_id, message_text)

    async def _process_message(self, chat_id: str, message_text: str):
        """Process a message and send the response"""
        logger.info(f"Received message from {chat_id}: {message_text}")
        
        with self.document_store.open_session() as session:
            renters = list(session.query(object_type=Renter).where_equals(
                "TelegramChatId", chat_id
            ).take(1))
            
            if not renters:
                await self.application.bot.send_message(
                    chat_id=chat_id,
                    text="Sorry, your Telegram account is not linked to a renter profile. "
                         "Please contact property management."
                )
                return

            # Get renter's units
            leases = list(
                session.query(object_type=Lease)
                .where_in("RenterIds", [renters[0].Id])
            )
            renter_units = [lease.UnitId for lease in leases]
            
            # Send typing indicator
            await self.application.bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)
            
            conversation_id = self.get_conversation_id(chat_id)
            renter = renters[0]
            
            
            conversation = self.document_store.ai.conversation(
                PropertyAgent.AGENT_ID,
                conversation_id,
                AiConversationCreationOptions(
                    parameters={
                        "renterId": renter.Id,
                        "renterUnits": renter_units,
                        "currentDate": date.today().strftime("%Y-%m-%d")
                    }
                )
            )
            
            def handle_charge_card(args):
                """Handle charging a card for debts"""
                from services.payment_service import PaymentService
                
                with self.document_store.open_session() as pay_session:
                    renter_with_card = pay_session.load(renter.Id, object_type=Renter)
                    card = next((c for c in renter_with_card.CreditCards if c.Last4Digits == args["Card"]), None)
                    
                    if not card:
                        raise ValueError(f"Card ending in {args['Card']} not found in your profile. Please use a registered card.")
                    
                    total_paid = PaymentService.create_payment_for_debts_with_card(
                        pay_session,
                        renter.Id,
                        args["DebtItemIds"],
                        card,
                        args["PaymentMethod"]
                    )
                    
                    return f"Successfully charged ${total_paid:.2f} to {card.Type} ending in {card.Last4Digits}."
            
            conversation.handle("ChargeCard", handle_charge_card, "SendErrorsToModel")
            
            def handle_create_service_request(args):
                """Handle creating a service request"""
                with self.document_store.open_session() as sr_session:
                    unit_id = renter_units[0] if renter_units else None
                    property_id = unit_id.rsplit('/', 1)[0] if unit_id else None
                    
                    service_request = ServiceRequest(
                        RenterId=renter.Id,
                        UnitId=unit_id,
                        Type=args["Type"],
                        Description=args["Description"],
                        Status="Open",
                        OpenedAt=datetime.utcnow(),
                        PropertyId=property_id
                    )
                    
                    sr_session.store(service_request)
                    sr_session.save_changes()
                    
                    return f"Service request created with ID `{service_request.Id}` for your unit."
            
            conversation.handle("CreateServiceRequest", handle_create_service_request, "SendErrorsToModel")
            
            conversation.set_user_prompt(message_text)
            
            answer = conversation.run()

            answer_text = answer.answer['Answer']
            followups = answer.answer['Followups']
            
            # Create reply keyboard if there are followups
            reply_markup = None
            if followups:
                keyboard = [[KeyboardButton(text)] for text in followups]
                reply_markup = ReplyKeyboardMarkup(
                    keyboard,
                    resize_keyboard=True,
                    one_time_keyboard=True
                )
            
            # Send response
            try:
                await self.application.bot.send_message(
                    chat_id=chat_id,
                    text=answer_text,
                    parse_mode=ParseMode.MARKDOWN,
                    reply_markup=reply_markup
                )
            except Exception:
                # Fallback to plain text if markdown fails
                await self.application.bot.send_message(
                    chat_id=chat_id,
                    text=answer_text,
                    reply_markup=reply_markup
                )
