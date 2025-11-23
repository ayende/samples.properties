# 🚀 PropertySphere Deployment Checklist

## Pre-Deployment

### ✅ Development Environment
- [x] .NET 8 SDK installed
- [x] RavenDB configured and accessible
- [x] Application builds without errors
- [x] All controllers implemented
- [x] Frontend tested in browser

### ✅ Configuration Files
- [x] appsettings.json configured
- [x] appsettings.Production.json created (if needed)
- [x] Connection strings validated
- [x] Telegram bot token configured (optional)

## Production Deployment

### 🔧 Infrastructure Setup

#### RavenDB Production
- [ ] Install RavenDB on production server
- [ ] Configure secure connection (HTTPS)
- [ ] Set up database backup schedule
- [ ] Create "PropertySphere" database
- [ ] Configure authentication/authorization
- [ ] Test connection from app server

#### Application Server
- [ ] Install .NET 8 Runtime
- [ ] Configure IIS or Kestrel
- [ ] Set up SSL certificate
- [ ] Configure firewall rules
- [ ] Set environment variables

### 📝 Configuration Updates

#### appsettings.Production.json
```json
{
  "Logging": {
    "LogLevel": {
      "Default": "Warning",
      "Microsoft.AspNetCore": "Warning"
    }
  },
  "RavenDb": {
    "Url": "https://your-ravendb-server:8080",
    "Database": "PropertySphere",
    "Certificate": "path/to/certificate.pfx"
  },
  "Telegram": {
    "BotToken": "YOUR_PRODUCTION_BOT_TOKEN"
  }
}
```

#### Update CORS Policy (Program.cs)
```csharp
builder.Services.AddCors(options =>
{
    options.AddDefaultPolicy(policy =>
    {
        policy.WithOrigins("https://yourdomain.com")
              .AllowAnyMethod()
              .AllowAnyHeader();
    });
});
```

### 🔐 Security Checklist

- [ ] Change default RavenDB credentials
- [ ] Enable HTTPS only
- [ ] Configure authentication for API endpoints
- [ ] Add rate limiting
- [ ] Enable request validation
- [ ] Configure CORS properly
- [ ] Hide sensitive data in logs
- [ ] Use secrets management (Azure Key Vault, AWS Secrets Manager)

### 📦 Build for Production

```powershell
# Clean solution
dotnet clean

# Restore packages
dotnet restore

# Build in Release mode
dotnet build --configuration Release

# Publish application
dotnet publish --configuration Release --output ./publish

# Test published build
cd publish
dotnet PropertySphere.dll
```

### 🚀 Deployment Steps

#### Option 1: IIS Deployment
1. Install .NET 8 Hosting Bundle on IIS server
2. Create IIS website
3. Copy published files to website directory
4. Configure application pool (.NET CLR Version: No Managed Code)
5. Set website bindings (HTTP/HTTPS)
6. Configure permissions for IIS_IUSRS
7. Restart IIS

#### Option 2: Docker Deployment
```dockerfile
FROM mcr.microsoft.com/dotnet/aspnet:8.0 AS base
WORKDIR /app
EXPOSE 80

FROM mcr.microsoft.com/dotnet/sdk:8.0 AS build
WORKDIR /src
COPY ["PropertySphere.csproj", "./"]
RUN dotnet restore
COPY . .
RUN dotnet build -c Release -o /app/build

FROM build AS publish
RUN dotnet publish -c Release -o /app/publish

FROM base AS final
WORKDIR /app
COPY --from=publish /app/publish .
ENTRYPOINT ["dotnet", "PropertySphere.dll"]
```

```powershell
# Build Docker image
docker build -t propertysphere:latest .

# Run container
docker run -d -p 80:80 `
  -e RavenDb__Url=https://your-ravendb:8080 `
  -e RavenDb__Database=PropertySphere `
  -e Telegram__BotToken=YOUR_TOKEN `
  propertysphere:latest
```

#### Option 3: Azure App Service
1. Create Azure App Service (Windows/.NET 8)
2. Configure application settings in Azure Portal
3. Deploy using Visual Studio or Azure CLI
4. Configure custom domain and SSL
5. Enable Application Insights

```powershell
# Deploy via Azure CLI
az webapp up --name propertysphere --resource-group PropertyManagement
```

### 🧪 Post-Deployment Testing

#### Smoke Tests
- [ ] Application starts without errors
- [ ] Homepage loads correctly
- [ ] API endpoints respond
- [ ] Database connection works
- [ ] Can create/read/update data
- [ ] Telegram bot responds (if configured)

#### Test API Endpoints
```powershell
$baseUrl = "https://your-production-url.com"

# Test properties endpoint
Invoke-RestMethod "$baseUrl/api/properties"

# Generate test data (CAUTION: only on test environment)
Invoke-RestMethod "$baseUrl/api/datageneration/generate-data" -Method POST

# Test missing debts
Invoke-RestMethod "$baseUrl/api/debtitems/missing"
```

#### Browser Testing
- [ ] Navigate to production URL
- [ ] Test Dashboard view
- [ ] Test Service Requests view
- [ ] Test Property Management view
- [ ] Verify all widgets load
- [ ] Check console for JavaScript errors

### 📊 Monitoring Setup

#### Application Monitoring
- [ ] Set up Application Insights (Azure)
- [ ] Configure error logging
- [ ] Set up performance monitoring
- [ ] Create alerting rules
- [ ] Monitor Telegram service health

#### Database Monitoring
- [ ] Monitor RavenDB performance
- [ ] Set up disk space alerts
- [ ] Configure backup verification
- [ ] Monitor query performance

#### Logging
```csharp
// Add to Program.cs for production logging
builder.Logging.ClearProviders();
builder.Logging.AddConsole();
builder.Logging.AddDebug();
builder.Logging.AddApplicationInsights();
```

### 🔄 Backup and Recovery

#### Database Backups
- [ ] Configure RavenDB automatic backups
- [ ] Test restore procedure
- [ ] Document backup location
- [ ] Set retention policy

#### Application Backups
- [ ] Version control (Git) configured
- [ ] Tag production releases
- [ ] Document deployment process
- [ ] Keep previous version available for rollback

### 📚 Documentation

- [ ] Update README with production URLs
- [ ] Document deployment process
- [ ] Create runbook for common issues
- [ ] Document Telegram bot setup for renters
- [ ] Create user guide for property managers
- [ ] Document backup/restore procedures

### 👥 User Setup

#### Admin Tasks
- [ ] Create initial properties
- [ ] Create units for each property
- [ ] Import renter data
- [ ] Create initial leases
- [ ] Link Telegram chat IDs for renters
- [ ] Train property managers on system

#### Renter Onboarding
- [ ] Share Telegram bot username
- [ ] Provide bot usage instructions
- [ ] Update renter profiles with chat IDs
- [ ] Send welcome message via bot

### 🎯 Go-Live Checklist

- [ ] All production servers ready
- [ ] Database populated with real data
- [ ] Backups configured and tested
- [ ] Monitoring and alerting active
- [ ] Team trained on system
- [ ] Support process documented
- [ ] Communication sent to users
- [ ] Rollback plan ready

### 📞 Support Contacts

#### Technical Support
- Developer: [Your Email]
- Infrastructure: [IT Contact]
- RavenDB Support: [Support Email]

#### Emergency Procedures
- Database issues: [Procedure]
- Application down: [Procedure]
- Data recovery: [Procedure]

---

## Post-Deployment

### Week 1
- [ ] Monitor error logs daily
- [ ] Check performance metrics
- [ ] Gather user feedback
- [ ] Fix critical issues
- [ ] Verify Telegram bot functionality

### Month 1
- [ ] Review system usage
- [ ] Optimize performance
- [ ] Plan feature enhancements
- [ ] Update documentation
- [ ] Review backup success rate

---

## Rollback Plan

If deployment fails:

1. Stop the application
2. Restore previous version
3. Verify database integrity
4. Restart services
5. Test functionality
6. Notify users
7. Investigate issues
8. Document lessons learned

---

**Last Updated**: November 21, 2025  
**Version**: 1.0.0  
**Status**: Pre-Deployment
