# PropertySphere - Quick Start Guide

## 🚀 Getting Started in 5 Minutes

### Step 1: Install RavenDB
```powershell
# Download and run RavenDB from: https://ravendb.net/downloads
# Or use Docker:
docker run -d -p 8080:8080 ravendb/ravendb
```

### Step 2: Restore Dependencies
```powershell
cd c:\work\samples.properties
dotnet restore
```

### Step 3: Run the Application
```powershell
dotnet run
```

The application will start at: **http://localhost:5000**

### Step 4: Generate Demo Data
Open a new PowerShell terminal and run:
```powershell
Invoke-RestMethod -Uri http://localhost:5000/api/datageneration/generate-data -Method POST
```

### Step 5: Open in Browser
Navigate to **http://localhost:5000** and explore:
- 📊 **Dashboard** - Overview of properties, units, and finances
- 🔧 **Service Requests** - Manage maintenance requests
- 🏢 **Property Management** - Manage properties, units, and leases

## 🎯 Key Features Implemented

### ✅ Backend (C# .NET 8)
- **7 Controllers** with full CRUD operations
- **Direct RavenDB integration** (minimal abstraction)
- **Telegram Polling Service** for bot integration
- **Atomic payment allocation** to debt items
- **Demo data generator** for testing

### ✅ Frontend (React + Tailwind)
- **Dark mode** with professional blue theme
- **3 main views**: Dashboard, Service Requests, Management
- **Real-time stats** and missing payment alerts
- **Property map visualization** with GPS coordinates
- **Responsive design** optimized for desktop

### ✅ Data Models
- Properties with GPS coordinates
- Units with vacancy tracking
- Leases with renter associations
- DebtItems with payment tracking
- Payments with allocation system
- ServiceRequests with status workflow

## 🔧 Optional: Configure Telegram Bot

1. Create a bot via @BotFather on Telegram
2. Copy the bot token
3. Edit `appsettings.json`:
   ```json
   {
     "Telegram": {
       "BotToken": "YOUR_ACTUAL_TOKEN_HERE"
     }
   }
   ```
4. Restart the application

### Telegram Commands
- `/start` - Welcome message
- `/request [description]` - Submit service request

## 📝 Testing the API

### Create a Property
```powershell
$body = @{
    name = "Test Apartments"
    address = "123 Test St"
    totalUnits = 5
    latitude = 40.7128
    longitude = -74.0060
} | ConvertTo-Json

Invoke-RestMethod -Uri http://localhost:5000/api/properties -Method POST -Body $body -ContentType "application/json"
```

### View Missing Payments
```powershell
Invoke-RestMethod -Uri http://localhost:5000/api/debtitems/missing -Method GET
```

### View Service Requests
```powershell
Invoke-RestMethod -Uri http://localhost:5000/api/servicerequests/status/Open -Method GET
```

## 🎨 UI/UX Features
- **Dark theme**: bg-gray-900 primary background
- **Blue accent**: Professional blue-600/blue-400 colors
- **Fluent design**: Rounded corners, shadows, smooth transitions
- **Responsive**: Optimized for desktop property managers

## 📚 Project Structure
```
PropertySphere/
├── Controllers/          # API Controllers (7 total)
│   ├── PropertiesController.cs
│   ├── UnitsController.cs
│   ├── RentersController.cs
│   ├── LeasesController.cs
│   ├── DebtItemsController.cs
│   ├── PaymentsController.cs
│   └── ServiceRequestsController.cs
├── Models/              # Data Models (7 total)
├── Services/            # TelegramPollingService
├── wwwroot/             # React Frontend
│   ├── index.html
│   └── app.jsx
├── Program.cs           # Application startup
└── appsettings.json     # Configuration
```

## 🐛 Troubleshooting

### RavenDB Connection Issues
- Ensure RavenDB is running at http://localhost:8080
- Check `appsettings.json` for correct URL
- Open RavenDB Studio in browser to verify

### Port Already in Use
- Change port in `Properties/launchSettings.json`
- Update API_BASE in `wwwroot/app.jsx`

### Telegram Bot Not Working
- Verify bot token in `appsettings.json`
- Check application logs for errors
- Ensure renters have TelegramChatId set

## 🎯 Next Steps
1. Customize the UI colors and branding
2. Add authentication/authorization
3. Implement email notifications
4. Add reporting and analytics
5. Deploy to production server

## 📞 Support
For issues or questions, refer to the detailed README.md
