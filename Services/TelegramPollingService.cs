using PropertySphere.Models;
using Raven.Client.Documents;
using Telegram.Bot;
using Telegram.Bot.Polling;
using Telegram.Bot.Types;
using Telegram.Bot.Types.Enums;

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

    public Task StartAsync(CancellationToken cancellationToken)
    {
        var botToken = _configuration["Telegram:BotToken"];
        
        if (string.IsNullOrEmpty(botToken) || botToken == "YOUR_TELEGRAM_BOT_TOKEN_HERE")
        {
            _logger.LogWarning("Telegram bot token not configured. Telegram service will not start.");
            return Task.CompletedTask;
        }

        _botClient = new TelegramBotClient(botToken);
        _cts = new CancellationTokenSource();

        var receiverOptions = new ReceiverOptions
        {
            AllowedUpdates = new[] { UpdateType.Message }
        };

        _botClient.StartReceiving(
            HandleUpdateAsync,
            HandleErrorAsync,
            receiverOptions,
            _cts.Token
        );

        _logger.LogInformation("Telegram polling service started");
        return Task.CompletedTask;
    }

    public Task StopAsync(CancellationToken cancellationToken)
    {
        _cts?.Cancel();
        _logger.LogInformation("Telegram polling service stopped");
        return Task.CompletedTask;
    }

    private async Task HandleUpdateAsync(ITelegramBotClient botClient, Update update, CancellationToken cancellationToken)
    {
        if (update.Message is not { Text: { } messageText } message)
            return;

        var chatId = message.Chat.Id;
        _logger.LogInformation($"Received message from {chatId}: {messageText}");

        using var session = _documentStore.OpenSession();

        var renter = session.Query<Renter>()
            .FirstOrDefault(r => r.TelegramChatId == chatId.ToString());

        if (renter == null)
        {
            await botClient.SendMessage(
                chatId,
                "Sorry, your Telegram account is not linked to a renter profile. Please contact property management.",
                cancellationToken: cancellationToken
            );
            return;
        }

        if (messageText.StartsWith("/request ", StringComparison.OrdinalIgnoreCase))
        {
            var description = messageText.Substring(9).Trim();
            
            if (string.IsNullOrEmpty(description))
            {
                await botClient.SendMessage(
                    chatId,
                    "Please provide a description. Usage: /request [description]",
                    cancellationToken: cancellationToken
                );
                return;
            }

            var activeLease = session.Query<Lease>()
                .FirstOrDefault(l => l.RenterIds.Contains(renter.Id!) && 
                                   l.EndDate >= DateTime.Now && 
                                   l.StartDate <= DateTime.Now);

            if (activeLease == null)
            {
                await botClient.SendMessage(
                    chatId,
                    "No active lease found for your account. Please contact property management.",
                    cancellationToken: cancellationToken
                );
                return;
            }

            var serviceRequest = new ServiceRequest
            {
                UnitId = activeLease.UnitId,
                RenterId = renter.Id!,
                Type = "Other",
                Description = description,
                Status = "Open",
                OpenedAt = DateTime.Now
            };

            session.Store(serviceRequest);
            session.SaveChanges();

            await botClient.SendMessage(
                chatId,
                $"Your service request has been submitted successfully! Request ID: {serviceRequest.Id}\n\nDescription: {description}",
                cancellationToken: cancellationToken
            );

            _logger.LogInformation($"Created service request {serviceRequest.Id} from Telegram user {chatId}");
        }
        else if (messageText.StartsWith("/start", StringComparison.OrdinalIgnoreCase))
        {
            await botClient.SendMessage(
                chatId,
                $"Welcome {renter.FirstName} {renter.LastName}!\n\n" +
                "Available commands:\n" +
                "/request [description] - Submit a service request",
                cancellationToken: cancellationToken
            );
        }
        else
        {
            await botClient.SendMessage(
                chatId,
                "Unknown command. Use /request [description] to submit a service request.",
                cancellationToken: cancellationToken
            );
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
