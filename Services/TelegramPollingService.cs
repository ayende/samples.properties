using System.ComponentModel;
using System.Text;
using PropertySphere.Models;
using Raven.Client.Documents;
using Raven.Client.Documents.AI;
using Telegram.Bot;
using Telegram.Bot.Polling;
using Telegram.Bot.Types;
using Telegram.Bot.Types.Enums;
using Telegram.Bot.Types.ReplyMarkups;

namespace PropertySphere.Services;

public class TelegramPollingService : IHostedService
{
    private readonly IConfiguration _configuration;
    private readonly IDocumentStore _documentStore;
    private readonly ILogger<TelegramPollingService> _logger;
    private TelegramBotClient? _botClient;
    private CancellationTokenSource? _cts;

    public TelegramPollingService(
        IConfiguration configuration,
        IDocumentStore documentStore,
        ILogger<TelegramPollingService> logger)
    {
        _configuration = configuration;
        _documentStore = documentStore;
        _logger = logger;
    }

    public async Task StartAsync(CancellationToken cancellationToken)
    {
        var botToken = _configuration["Telegram:BotToken"];

        if (string.IsNullOrEmpty(botToken) || botToken == "YOUR_TELEGRAM_BOT_TOKEN_HERE")
        {
            _logger.LogWarning("Telegram bot token not configured. Telegram service will not start.");
            return;
        }

        _botClient = new TelegramBotClient(botToken);
        _cts = new CancellationTokenSource();

        var receiverOptions = new ReceiverOptions
        {
            AllowedUpdates = new[] { UpdateType.Message, UpdateType.CallbackQuery }
        };

        _botClient.StartReceiving(
            HandleUpdateAsync,
            HandleErrorAsync,
            receiverOptions,
            _cts.Token
        );

        _logger.LogInformation("Telegram polling service started");

        _ = _documentStore.Subscriptions.GetSubscriptionWorker<Photo>("After Photos Analysis")
            .Run(async batch =>
            {
                using var session = batch.OpenAsyncSession();
                foreach (var item in batch.Items)
                {
                    var renter = await session.LoadAsync<Renter>(item.Result.RenterId!);
                    await ProcessMessageAsync(_botClient, renter.TelegramChatId!,
                        $"Uploaded an image with caption: {item.Result.Caption}\r\n" +
                        $"Image description: {item.Result.Description}.",
                        cancellationToken);
                }
            }).ContinueWith(t =>
            {
                _logger.LogError(t.Exception, "Error in Photos Analysis subscription worker");
            }, TaskContinuationOptions.OnlyOnFaulted);

    }

    public Task StopAsync(CancellationToken cancellationToken)
    {
        _cts?.Cancel();
        _logger.LogInformation("Telegram polling service stopped");
        return Task.CompletedTask;
    }

    private async Task HandleUpdateAsync(ITelegramBotClient botClient, Update update, CancellationToken cancellationToken)
    {
        switch (update)
        {
            case { Message: { Text: { } messageText } message }:
                await ProcessMessageAsync(botClient, message.Chat.Id.ToString(), messageText, cancellationToken);
                break;

            case { Message: { Photo: { Length: > 0 } } message }:
                await ProcessPhotoAsync(botClient, message, cancellationToken);
                break;

            case { Message: { Document: { } } message }:
                await ProcessPhotoAsync(botClient, message, cancellationToken);
                break;

            default:
                _logger.LogInformation("Ignoring non-text message update: Type={Type}, ChatId={ChatId}, MessageId={MessageId}",
                    update.Message?.Type, update.Message?.Chat.Id, update.Message?.MessageId);
                break;
        }
    }

    private async Task ProcessPhotoAsync(ITelegramBotClient botClient, Message message, CancellationToken cancellationToken)
    {
        var chatId = message.Chat.Id.ToString();
        using var session = _documentStore.OpenAsyncSession();

        var renter = await session.Query<Renter>()
            .FirstOrDefaultAsync(r => r.TelegramChatId == chatId);

        if (renter == null)
        {
            await botClient.SendMessage(
                chatId,
                "Sorry, your Telegram account is not linked to a renter profile. Please contact property management.",
                cancellationToken: cancellationToken
            );
            return;
        }
        var imageResult = await TryGetImage(botClient, message, chatId, cancellationToken);
        if (imageResult == default)
        {
            return;
        }

        var ms = new MemoryStream();
        var file = await botClient.GetInfoAndDownloadFile(imageResult.fileId, ms, cancellationToken);
        var photo = new Photo
        {
            ConversationId = GetConversationId(chatId),
            Id = "photos/" + Guid.NewGuid().ToString("N"),
            RenterId = renter.Id,
            Caption = message.Caption ?? message.Text
        };
        await session.StoreAsync(photo, cancellationToken);
        ms.Position = 0;
        session.Advanced.Attachments.Store(photo, imageResult.fileName, ms);
        await session.SaveChangesAsync(cancellationToken);
        await botClient.SendMessage(
                       chatId,
                       "Looking at the photo you sent..., may take me a moment...",
                       cancellationToken: cancellationToken
                   );
    }

    private static string GetConversationId(string chatId) => $"chats/{chatId}/{DateTime.Today:yyyy-MM-dd}";

    private static async Task<(string fileId, string fileName)> TryGetImage(ITelegramBotClient botClient, Message message, string chatId, CancellationToken cancellationToken)
    {
        string? mimeType = null;

        // Handle Photo messages
        if (message.Photo is { Length: > 0 })
        {
            var bestPhoto = message.Photo.MaxBy(ps => ps.FileSize)!;
            return (bestPhoto.FileId, "image.jpg");
        }
        // Handle Document messages
        else if (message.Document != null)
        {
            var document = message.Document;
            mimeType = document.MimeType;
            var fileName = "image.jpg";

            // Reject non-JPG files
            if (mimeType != "image/jpeg" && !fileName.EndsWith(".jpg", StringComparison.OrdinalIgnoreCase) && !fileName.EndsWith(".jpeg", StringComparison.OrdinalIgnoreCase))
            {
                await botClient.SendMessage(
                    chatId,
                    "Sorry, only JPG/JPEG images are accepted.",
                    cancellationToken: cancellationToken
                );
                return default;
            }

            return (document.FileId, fileName);
        }

        return default;
    }

    private async Task ProcessMessageAsync(ITelegramBotClient botClient, string chatId, string messageText, CancellationToken cancellationToken)
    {
        _logger.LogInformation($"Received message from {chatId}: {messageText}");

        using var session = _documentStore.OpenAsyncSession();

        var renter = await session.Query<Renter>()
            .FirstOrDefaultAsync(r => r.TelegramChatId == chatId, cancellationToken);

        if (renter == null)
        {
            await botClient.SendMessage(
                chatId,
                "Sorry, your Telegram account is not linked to a renter profile. Please contact property management.",
                cancellationToken: cancellationToken
            );
            return;
        }
        var conversationId = GetConversationId(chatId);
        if (messageText == "/clear")
        {
            session.Delete(conversationId);
            await session.SaveChangesAsync(cancellationToken);
            await botClient.SendMessage(
                chatId,
                "Conversation history cleared. You can start a new conversation now.",
                cancellationToken: cancellationToken
            );
            return;
        }

        var renterUnits = await session.Query<Lease>()
            .Where(l => l.RenterIds.Contains(renter.Id!))
            .Select(l => l.UnitId)
            .ToListAsync(cancellationToken);

        var conversation = _documentStore.AI.Conversation(PropertyAgent.AgentId,
            conversationId,
            new AiConversationCreationOptions
            {
                Parameters = new Dictionary<string, object?>
                {
                    ["renterId"] = renter.Id,
                    ["renterUnits"] = renterUnits,
                    ["currentDate"] = DateTime.Today.ToString("yyyy-MM-dd")
                }
            });

        conversation.Handle<PropertyAgent.ChargeCardArgs>("ChargeCard", async args =>
        {
            using var paySession = _documentStore.OpenAsyncSession();

            var renterWithCard = await paySession.LoadAsync<Renter>(renter.Id!, cancellationToken);
            var card = renterWithCard?.CreditCards.FirstOrDefault(c => c.Last4Digits == args.Card);

            if (card == null)
            {
                throw new InvalidOperationException($"Card ending in {args.Card} not found in your profile. Please use a registered card.");
            }

            var totalPaid = await PaymentService.CreatePaymentForDebtsWithCardAsync(
                paySession,
                renter.Id!,
                args.DebtItemIds,
                card,
                args.PaymentMethod,
                cancellationToken);

            return $"Successfully charged {totalPaid:C2} to {card.Type} ending in {card.Last4Digits}.";
        });

        conversation.Handle<PropertyAgent.CreateServiceRequestArgs>("CreateServiceRequest", async args =>
        {
            using var session = _documentStore.OpenAsyncSession();
            var unitId = renterUnits.FirstOrDefault();
            var propertyId = unitId?.Substring(0, unitId.LastIndexOf('/'));

            var serviceRequest = new ServiceRequest
            {
                RenterId = renter.Id!,
                UnitId = unitId,
                Type = args.Type,
                Description = args.Description,
                Status = "Open",
                OpenedAt = DateTime.UtcNow,
                PropertyId = propertyId
            };

            await session.StoreAsync(serviceRequest);
            await session.SaveChangesAsync();

            return $"Service request created with ID `{serviceRequest.Id}` for your unit.";
        });

        conversation.SetUserPrompt(messageText);

        await botClient.SendChatAction(chatId, ChatAction.Typing, cancellationToken: cancellationToken);

        var msg = new StringBuilder();
        Task<Message>? previous = null;

        var result = await conversation.StreamAsync<PropertyAgent.Reply>(x => x.Answer, s =>
        {
            msg.Append(s);
            previous = UpdateOrCreateMessageAsync(botClient, chatId, msg.ToString(), previous, cancellationToken);
            return Task.CompletedTask;
        }, cancellationToken);

        if (previous != null)
            await previous;

        await UpdateOrCreateMessageAsync(botClient, chatId, result.Answer.Answer, previous, cancellationToken);

        var replyMarkup = new ReplyKeyboardMarkup(result.Answer.Followups
            .Select(text => new KeyboardButton(text))
            .ToArray())
        {
            ResizeKeyboard = true,
            OneTimeKeyboard = true
        };

        await botClient.SendMessage(
            chatId,
            "What next?",
            replyMarkup: replyMarkup,
            cancellationToken: cancellationToken);
    }

    private static async Task<Message> UpdateOrCreateMessageAsync(
        ITelegramBotClient botClient,
        string chatId,
        string text,
        Task<Message>? previous,
        CancellationToken cancellationToken)
    {
        // If this is the first chunk, create a new message
        if (previous == null)
        {
            return await SendMessageSafeAsync(botClient, chatId, text, cancellationToken);
        }

        // Wait for previous operation to complete before starting a new one
        if (previous.IsCompleted is false)
            return await previous;

        var previousMessage = await previous;

        // Only edit if content has changed to avoid "message not modified" error
        if (previousMessage.Text == text)
            return previousMessage;

        return await EditMessageSafeAsync(botClient, chatId, previousMessage.MessageId, text, cancellationToken);
    }

    private static async Task<Message> SendMessageSafeAsync(
        ITelegramBotClient botClient,
        string chatId,
        string text,
        CancellationToken cancellationToken)
    {
        try
        {
            // Try with Markdown first
            return await botClient.SendMessage(chatId, text, parseMode: ParseMode.Markdown, cancellationToken: cancellationToken);
        }
        catch (Telegram.Bot.Exceptions.ApiRequestException)
        {
            // If Markdown parsing fails, send as plain text
            return await botClient.SendMessage(chatId, text, cancellationToken: cancellationToken);
        }
    }

    private static async Task<Message> EditMessageSafeAsync(
        ITelegramBotClient botClient,
        string chatId,
        int messageId,
        string text,
        CancellationToken cancellationToken)
    {
        try
        {
            // Try with Markdown first
            return await botClient.EditMessageText(chatId, messageId, text, parseMode: ParseMode.Markdown, cancellationToken: cancellationToken);
        }
        catch (Telegram.Bot.Exceptions.ApiRequestException)
        {
            // If Markdown parsing fails, edit as plain text
            return await botClient.EditMessageText(chatId, messageId, text, cancellationToken: cancellationToken);
        }
    }

    private Task HandleErrorAsync(ITelegramBotClient botClient, Exception exception, CancellationToken cancellationToken)
    {
        _logger.LogError(exception, "Error in Telegram polling service");
        return Task.CompletedTask;
    }

    public async Task SendNotificationAsync(string telegramChatId, string message)
    {
        if (_botClient == null)
        {
            _logger.LogWarning("Telegram bot client not initialized");
            return;
        }

        try
        {
            await _botClient.SendMessage(
                long.Parse(telegramChatId),
                message
            );
            _logger.LogInformation($"Sent notification to {telegramChatId}");
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, $"Failed to send notification to {telegramChatId}");
        }
    }
}
