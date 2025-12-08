from pydantic_settings import BaseSettings
from typing import Optional, List
from pydantic import field_validator, Field


class Settings(BaseSettings):
    # RavenDB settings
    ravendb_url: str = "http://localhost:8080"
    ravendb_database: str = "PropertySphere"
    
    # Telegram settings
    telegram_bot_token: Optional[str] = "YOUR_TELEGRAM_BOT_TOKEN_HERE"
    
    # CORS settings - comma-separated string that will be parsed
    cors_origins: str = "*"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


settings = Settings()
