from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # RavenDB settings
    ravendb_url: str = "http://localhost:8080"
    ravendb_database: str = "PropertySphere"
    
    # Telegram settings
    telegram_bot_token: Optional[str] = "YOUR_TELEGRAM_BOT_TOKEN_HERE"
    
    # CORS settings
    cors_origins: list[str] = ["*"]
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


settings = Settings()
