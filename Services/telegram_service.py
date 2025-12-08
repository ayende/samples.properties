"""Telegram bot service for PropertySphere"""
import asyncio
import logging
from datetime import datetime, date
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from telegram.constants import ParseMode, ChatAction

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
            renter = session.query(object_type=Renter).where_equals(
                "telegram_chat_id", chat_id
            ).first_or_default()
            
            if not renter:
                await update.message.reply_text(
                    "Sorry, your Telegram account is not linked to a renter profile. "
                    "Please contact property management."
                )
                return
            
            # Get photo file
            if update.message.photo:
                photo_file = await update.message.photo[-1].get_file()
                file_name = "image.jpg"
            elif update.message.document:
                photo_file = await update.message.document.get_file()
                file_name = update.message.document.file_name or "image.jpg"
                
                # Check if it's a JPEG
                if not file_name.lower().endswith(('.jpg', '.jpeg')):
                    await update.message.reply_text("Sorry, only JPG/JPEG images are accepted.")
                    return
            else:
                return
            
            # Download photo
            photo_bytes = await photo_file.download_as_bytearray()
            
            # Create photo document
            photo = Photo(
                conversation_id=self.get_conversation_id(chat_id),
                id=f"photos/{datetime.now().strftime('%Y%m%d%H%M%S')}",
                renter_id=renter.id,
                caption=update.message.caption or update.message.text
            )
            
            session.store(photo)
            # Note: Attachment handling would require RavenDB attachments API
            # session.advanced.attachments.store(photo, file_name, photo_bytes)
            session.save_changes()
            
            await update.message.reply_text(
                "Looking at the photo you sent..., may take me a moment..."
            )
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle text messages"""
        chat_id = str(update.effective_chat.id)
        message_text = update.message.text
        
        logger.info(f"Received message from {chat_id}: {message_text}")
        
        with self.document_store.open_session() as session:
            renter = session.query(object_type=Renter).where_equals(
                "telegram_chat_id", chat_id
            ).first_or_default()
            
            if not renter:
                await update.message.reply_text(
                    "Sorry, your Telegram account is not linked to a renter profile. "
                    "Please contact property management."
                )
                return
            
            # Get renter's units
            renter_units = list(
                session.query(object_type=Lease)
                .where_in("renter_ids", [renter.id])
                .select(lambda l: l.unit_id)
            )
            
            # Send typing indicator
            await context.bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)
            
            # Process with AI agent (simplified - actual implementation would use RavenDB AI)
            # This is a placeholder for the actual AI conversation
            conversation_id = self.get_conversation_id(chat_id)
            
            # Simulate AI response
            response_text = f"I received your message: {message_text}\n\nThis is a placeholder response. " \
                          "The actual implementation would use RavenDB's AI agent API to process your request."
            
            followups = [
                "What's my rent?",
                "Check utility usage",
                "Outstanding debts",
                "Service requests"
            ]
            
            # Create reply keyboard
            keyboard = [[KeyboardButton(text)] for text in followups]
            reply_markup = ReplyKeyboardMarkup(
                keyboard,
                resize_keyboard=True,
                one_time_keyboard=True
            )
            
            # Send response
            try:
                await update.message.reply_text(
                    response_text,
                    parse_mode=ParseMode.MARKDOWN,
                    reply_markup=reply_markup
                )
            except Exception:
                # Fallback to plain text if markdown fails
                await update.message.reply_text(
                    response_text,
                    reply_markup=reply_markup
                )
    
    async def send_notification(self, telegram_chat_id: str, message: str):
        """Send a notification to a user"""
        if not self.application:
            logger.warning("Telegram bot not initialized")
            return
        
        try:
            await self.application.bot.send_message(
                chat_id=int(telegram_chat_id),
                text=message
            )
            logger.info(f"Sent notification to {telegram_chat_id}")
        except Exception as e:
            logger.error(f"Failed to send notification to {telegram_chat_id}: {e}")
