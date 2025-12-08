# PropertySphere - Python Edition

Property management system built with FastAPI and RavenDB.

## Features

- Property and unit management
- Lease tracking
- Debt and payment processing
- Service request management
- Utility usage tracking
- Telegram bot integration with AI assistant
- Time series data support

## Tech Stack

- **Backend**: FastAPI (Python 3.11+)
- **Database**: RavenDB
- **Telegram Bot**: python-telegram-bot
- **AI Agent**: RavenDB AI integration

## Setup

### Prerequisites

- Python 3.11 or higher
- RavenDB server running (default: http://localhost:8080)
- Telegram Bot Token (optional, for bot features)

### Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure environment:
```bash
cp .env.example .env
# Edit .env with your configuration
```

3. Configure RavenDB AI (optional, for AI features):
   - Open RavenDB Studio
   - Go to Settings > AI Hub > AI Connection Strings
   - Create a connection string named "Property Management AI Model"
   - Configure your AI provider (OpenAI, Claude, etc.)

### Running the Application

```bash
python main.py
```

The application will be available at `http://localhost:5000`

## API Documentation

Once running, visit `http://localhost:5000/docs` for interactive API documentation (Swagger UI).

## Project Structure

```
├── main.py                 # Application entry point
├── config.py               # Configuration management
├── database.py             # RavenDB connection
├── indexes.py              # RavenDB indexes
├── models/                 # Data models
│   ├── property.py
│   ├── unit.py
│   ├── renter.py
│   ├── lease.py
│   ├── debt_item.py
│   ├── payment.py
│   └── service_request.py
├── routers/                # API endpoints
│   ├── properties.py
│   ├── units.py
│   ├── leases.py
│   ├── renters.py
│   ├── debt_items.py
│   ├── payments.py
│   └── service_requests.py
├── services/               # Business logic
│   ├── property_agent.py
│   ├── telegram_service.py
│   └── payment_service.py
└── wwwroot/                # Static files (frontend)
```

## Telegram Bot

The Telegram bot provides renters with:
- Rent and utility usage queries
- Outstanding debt information
- Service request management
- AI-powered assistance

To enable the bot:
1. Create a bot with [@BotFather](https://t.me/botfather)
2. Add the bot token to `.env`
3. Link renter profiles to Telegram chat IDs

## Development

### Running in Development Mode

```bash
uvicorn main:app --reload --port 5000
```

### Code Style

This project follows PEP 8 guidelines and uses type hints throughout.

## Migration from C#

This is a Python port of the original C#/ASP.NET Core application. Key differences:

- FastAPI instead of ASP.NET Core
- Python dataclasses instead of C# classes
- Async/await using Python's asyncio
- python-telegram-bot instead of Telegram.Bot
- pyravendb instead of RavenDB.Client

## License

[Your License Here]
