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

        await PropertyAgent.Create(_documentStore);

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
                var chatId = message.Chat.Id.ToString();
                await ProcessMessageAsync(botClient, chatId, messageText, cancellationToken);
                break;

            default:
                _logger.LogInformation("Ignoring non-text message update: Type={Type}, ChatId={ChatId}, MessageId={MessageId}",
                    update.Message?.Type, update.Message?.Chat.Id, update.Message?.MessageId);
                break;
        }
    }

    private async Task ProcessMessageAsync(ITelegramBotClient botClient, string chatId, string messageText, CancellationToken cancellationToken)
    {
        _logger.LogInformation($"Received message from {chatId}: {messageText}");

        using var session = _documentStore.OpenSession();

        var renter = session.Query<Renter>()
            .FirstOrDefault(r => r.TelegramChatId == chatId);

        if (renter == null)
        {
            await botClient.SendMessage(
                chatId,
                "Sorry, your Telegram account is not linked to a renter profile. Please contact property management.",
                cancellationToken: cancellationToken
            );
            return;
        }

        var conversation = _documentStore.AI.Conversation(PropertyAgent.AgentId,
            $"chats/{chatId}/{DateTime.Today:yyyy-MM-dd}",
            new AiConversationCreationOptions
            {
                Parameters = new Dictionary<string, object?>
                {
                    ["renterId"] = renter.Id
                }
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
            .Chunk(2) // max 2 per row
            .Select(chunk => chunk.Select(text => new KeyboardButton(text)))
            .ToArray())
        {
            ResizeKeyboard = true,
            OneTimeKeyboard = true
        };

        await botClient.SendMessage(
            chatId,
            "Choose a question or type your own:",
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
            return await botClient.SendMessage(chatId, text, parseMode: ParseMode.Markdown, cancellationToken: cancellationToken);
        }

        // Wait for previous operation to complete before starting a new one
        if (previous.IsCompleted is false)
            return await previous;

        var previousMessage = await previous;

        // Only edit if content has changed to avoid "message not modified" error
        if (previousMessage.Text == text)
            return previousMessage;

        return await botClient.EditMessageText(chatId, previousMessage.MessageId, text, parseMode: ParseMode.Markdown, cancellationToken: cancellationToken);
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
