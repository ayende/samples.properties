using PropertySphere.Services;
using PropertySphere.Indexes;
using Raven.Client.Documents;
using Raven.Client.Documents.Indexes;
using Raven.Client.Documents.Session;

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
