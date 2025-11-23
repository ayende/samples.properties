# PropertySphere - Rental Property Management Application

A modern, full-stack rental property management application built with .NET 8, RavenDB, and React.

## Architecture

### Backend
- **Framework**: ASP.NET Core MVC (.NET 8+)
- **Database**: RavenDB (Document Store)
- **Integration**: Telegram Bot API (Background Polling Service)

### Frontend
- **Framework**: React (Functional Components with Hooks)
- **Styling**: Tailwind CSS
- **Theme**: Dark Mode with Professional Blue Theme

## Features

### Property Management
- Manage multiple properties with GPS coordinates
- Track units and vacancy status
- Monitor lease agreements and active renters

### Financial Management
- Track debt items (rent, utilities, fees)
- Record payments with multiple payment methods
- Automatic payment allocation to debt items
- Missing payment alerts and reporting

### Service Requests
- Track maintenance and service requests
- Status management (Open, Scheduled, In Progress, Closed, Canceled)
- Integration with Telegram bot for renter submissions

### Telegram Integration
- Background polling service for bot updates
- `/request [description]` command for service requests
- Automatic notifications to renters

## Setup Instructions

### Prerequisites
1. .NET 8 SDK or later
2. RavenDB Server (local or remote)
3. Telegram Bot Token (optional, for Telegram features)

### Installation

1. **Configure RavenDB**
   - Install and start RavenDB server (default: http://localhost:8080)
   - Update connection settings in `appsettings.json` if needed

2. **Configure Telegram Bot (Optional)**
   - Create a bot via @BotFather on Telegram
   - Update the bot token in `appsettings.json`:
     ```json
     {
       "Telegram": {
         "BotToken": "YOUR_TELEGRAM_BOT_TOKEN_HERE"
       }
     }
     ```

3. **Restore Dependencies**
   ```powershell
   dotnet restore
   ```

4. **Run the Application**
   ```powershell
   dotnet run
   ```

5. **Access the Application**
   - Open browser to `http://localhost:5000`
   - The application will serve the React frontend automatically

### Generate Demo Data

To populate the database with realistic test data:

```powershell
# Use POST request to generate data
curl -X POST http://localhost:5000/api/datageneration/generate-data
```

This will create:
- 3 properties
- 10 units
- 15 renters
- 7 active leases
- Multiple debt items and payment records
- 6 service requests

## API Endpoints

### Properties
- `GET /api/properties` - List all properties
- `POST /api/properties` - Create new property

### Units
- `GET /api/units/by-property/{propertyId}` - Get units by property
- `POST /api/units` - Create new unit

### Renters
- `GET /api/renters/{renterId}` - Get renter details
- `POST /api/renters` - Create new renter

### Leases
- `POST /api/leases` - Create new lease
- `PUT /api/leases/{leaseId}/terminate` - Terminate lease
- `GET /api/leases/by-unit/{unitId}` - Get active lease for unit

### Debt Items
- `GET /api/debtitems/missing` - List all missing payments
- `POST /api/debtitems/charge-rent` - Generate rent charges for active leases
- (Deprecated) `POST /api/debtitems/utility/{leaseId}` - Use `POST /api/debtitems/fee/{renterId}` instead
- `POST /api/debtitems/fee/{renterId}` - Create individual fee

### Payments
- `POST /api/payments` - Record payment and allocate to debts

### Service Requests
- `GET /api/servicerequests` - List all service requests
- `GET /api/servicerequests/status/{status}` - Filter by status
- `POST /api/servicerequests` - Create new request
- `PUT /api/servicerequests/{requestId}/status` - Update status

## Data Models

### Property
- Name, Address, Total Units
- GPS Coordinates (Latitude, Longitude)

### Unit
- Property Reference
- Unit Number
- Vacant From Date

### Renter
- Name, Contact Info
- Telegram Chat ID

### Lease
- Unit and Renter References
- Lease Amount, Start/End Dates
- Active Status (calculated)

### DebtItem
- Lease or Renter Reference
- Type, Description, Amounts
- Due Date, Payment Status (calculated)

### Payment
- Payment Date, Total Amount
- Payment Methods (array)
- Allocation to Debt Items (array)

### ServiceRequest
- Unit and Renter Reference
- Type, Description, Status
- Opened/Closed Timestamps

## Architecture Notes

- **Minimal Abstraction**: Business logic is implemented directly in controllers
- **Session Management**: RavenDB sessions are scoped per request
- **Telegram Service**: Runs as a background hosted service with long polling
- **Frontend**: Single-file React application with client-side routing

## License

Proprietary - For internal use by property administration team only.
