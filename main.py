"""FastAPI application entry point"""
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import uvicorn

from config import settings
from database import init_document_store, close_document_store, get_document_store
from routers import properties, units, leases, renters, debt_items, payments, service_requests, utility_usage, data_generation


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    store = init_document_store()
    
    # Initialize PropertyAgent
    from services.property_agent import PropertyAgent
    PropertyAgent.create(store)
    
    # Start Telegram service
    if settings.telegram_bot_token and settings.telegram_bot_token != "YOUR_TELEGRAM_BOT_TOKEN_HERE":
        from services.telegram_service import TelegramService
        print ("Starting Telegram service...")
        telegram_service = TelegramService(store)
        telegram_task = asyncio.create_task(telegram_service.start())
        app.state.telegram_service = telegram_service
        app.state.telegram_task = telegram_task
    
    yield
    
    # Shutdown
    if hasattr(app.state, "telegram_service"):
        await app.state.telegram_service.stop()
        app.state.telegram_task.cancel()
    
    close_document_store()


# Create FastAPI app
app = FastAPI(
    title="PropertySphere",
    description="Property Management System",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
cors_origins = [origin.strip() for origin in settings.cors_origins.split(',')] if ',' in settings.cors_origins else [settings.cors_origins]
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(properties.router, prefix="/api/properties", tags=["properties"])
app.include_router(units.router, prefix="/api/units", tags=["units"])
app.include_router(leases.router, prefix="/api/leases", tags=["leases"])
app.include_router(renters.router, prefix="/api/renters", tags=["renters"])
app.include_router(debt_items.router, prefix="/api/debtitems", tags=["debt-items"])
app.include_router(payments.router, prefix="/api/payments", tags=["payments"])
app.include_router(service_requests.router, prefix="/api/servicerequests", tags=["service-requests"])
app.include_router(utility_usage.router, prefix="/api/utilityusage", tags=["utility-usage"])
app.include_router(data_generation.router, prefix="/api/datageneration", tags=["data-generation"])

# Serve static files
app.mount("/wwwroot", StaticFiles(directory="wwwroot", html=True), name="static")


@app.get("/")
async def root():
    """Serve index.html"""
    return FileResponse("wwwroot/index.html")


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=5000,
        reload=True
    )
