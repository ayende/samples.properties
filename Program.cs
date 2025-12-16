using PropertySphere.Services;
using PropertySphere.Indexes;
using Raven.Client.Documents;
using Raven.Client.Documents.Indexes;
using Raven.Client.Documents.Session;
using Raven.Client.ServerWide.Operations;
using Raven.Client.Documents.Operations.OngoingTasks;
using Raven.Client.Documents.Subscriptions;
using Raven.Client.Documents.Operations.AI;
using Raven.Client.Exceptions.Documents.Subscriptions;
using Raven.Client.Documents.Operations.ConnectionStrings;

var builder = WebApplication.CreateBuilder(args);

builder.Services.AddControllers();
builder.Services.AddEndpointsApiExplorer();

var ravenDbUrl = builder.Configuration["RavenDb:Url"] ?? "http://localhost:8080";
var ravenDbDatabase = builder.Configuration["RavenDb:Database"] ?? "PropertySphere";

builder.Services.AddSingleton<IDocumentStore>(sp =>
{
    var store = new DocumentStore
    {
        Urls = new[] { ravenDbUrl },
        Database = ravenDbDatabase
    };
    store.Initialize();

    IndexCreation.CreateIndexes(typeof(DebtItems_Outstanding).Assembly, store);

    var aiApiKey = sp.GetRequiredService<IConfiguration>()["AI_API_KEY"];

    if (!string.IsNullOrWhiteSpace(aiApiKey) && aiApiKey != "YOUR_OPENAI_API_KEY_HERE")
    {
        var aiConnection = new AiConnectionString
        {
            Name = "Property Management AI Model",
            Identifier = "property-management-ai-model",
            OpenAiSettings = new OpenAiSettings
            {
                ApiKey = aiApiKey,
                Endpoint = "https://api.openai.com/v1",
                Model = "gpt-4.1-mini"
            },
            ModelType = AiModelType.Chat
        };

        store.Maintenance.Send(new PutConnectionStringOperation<AiConnectionString>(aiConnection));

        PropertyAgent.Create(store);
        PropertyDescriptionGenerator.Create(store);
    }
    PhotoSubscription.Create(store);
    return store;
});

builder.Services.AddScoped<IDocumentSession>(sp =>
{
    var store = sp.GetRequiredService<IDocumentStore>();
    return store.OpenSession();
});

builder.Services.AddScoped<IAsyncDocumentSession>(sp =>
{
    var store = sp.GetRequiredService<IDocumentStore>();
    return store.OpenAsyncSession();
});

builder.Services.AddHostedService<TelegramPollingService>();

builder.Services.AddCors(options =>
{
    options.AddDefaultPolicy(policy =>
    {
        policy.AllowAnyOrigin()
              .AllowAnyMethod()
              .AllowAnyHeader();
    });
});

var app = builder.Build();

app.UseCors();
app.UseStaticFiles();
app.MapControllers();

app.MapFallbackToFile("index.html");

app.Run();
