from pydantic_settings import BaseSettings
from pydantic import ConfigDict
from typing import List, Optional

class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "SeatSync"
    PORT: int = 8000
    NODE_ENV: str = "development"
    SECRET_KEY: str
    JWT_SECRET_KEY: str
    DATABASE_URL: str
    GOOGLE_PROJECT_ID: str
    GOOGLE_APPLICATION_CREDENTIALS: str
    GOOGLE_API_KEY: Optional[str] = None
    GEMINI_API_KEY: str
    CORS_ORIGIN: str
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "https://seat-sync-xi.vercel.app"
    ]
    ALLOWED_HOSTS: List[str] = [
        "localhost",
        "127.0.0.1",
        "*.railway.app",
        "seat-sync-xi.vercel.app"
    ]
    LOG_LEVEL: str = "info"
    DEBUG: bool = True
    # Add any other fields from your .env as needed

    model_config = ConfigDict(
        env_file=".env",
        case_sensitive=True
    )

settings = Settings() 