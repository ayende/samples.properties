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

    var databaseRecord = store.Maintenance.Server.Send(new GetDatabaseRecordOperation(ravenDbDatabase));
    if (databaseRecord?.AiConnectionStrings?.ContainsKey("Property Management AI Model") is not true)
    {
        throw new InvalidOperationException(
            "AI connection string 'Property Management AI Model' not found in database.\n" +
            "Please configure an AI connection string in RavenDB Studio:\n" +
            "  1. Go to Settings > AI Hub > AI Connection Strings > Add new\n" +
            "  2. Name it 'Property Management AI Model'\n" +
            "  3. Configure your AI provider (OpenAI, Claude, etc.)");
    }

    if (store.Maintenance.Send(new GetOngoingTaskInfoOperation("Describe Photos", OngoingTaskType.GenAi)) is null)
    {
        store.Maintenance.Send(new AddGenAiOperation(new GenAiConfiguration
        {
            Name = "Describe Photos",
            Collection = "Photos",
            ConnectionStringName = "Property Management AI Model",
            GenAiTransformation = new GenAiTransformation
            {
                Script = """
                        const image = loadAttachment('image.jpg');
                        if(!image) return;

                        ai.genContext({
                            Caption: this.Caption
                        }).withJpeg(image);
                        """
            },
            Prompt = """
                    You are a helpful assistant aiding a tenant in submitting a maintenance request. 
                    Look at the photo provided. Write a clear, professional description of the problem shown that the tenant can paste into an email or form.
                    Focus on what is broken and where the damage is. Describe what is the problem, don't provide solutions
                    Use standard terminology (e.g., use 'P-trap' instead of 'curvy pipe' if you are sure, otherwise keep it simple).
                    Keep it under 3 sentences.
                    """,
            SampleObject = """
                    {
                        "Description": "Description of the image"
                    }
                    """,
            UpdateScript = "this.Description = $output.Description;",
        }));
    }

    PropertyAgent.Create(store);


    const string subscriptionName = "After Photos Analysis";
    try
    {
        store.Subscriptions.GetSubscriptionState(subscriptionName);
    }
    catch (SubscriptionDoesNotExistException)
    {
        store.Subscriptions.Create(new SubscriptionCreationOptions
        {
            Name = subscriptionName,
            Query = """
                    from Photos 
                    where Description != null 
                    include RenterId
                    """
        });
    }



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
