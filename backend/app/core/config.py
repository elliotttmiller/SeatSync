from pydantic_settings import BaseSettings
from pydantic import ConfigDict
from typing import List, Optional

class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "SeatSync"
    PORT: int = 8000
    RAILWAY_STATIC_URL: Optional[str] = None
    SECRET_KEY: str
    JWT_SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    DATABASE_URL: str
    REDIS_URL: Optional[str] = None
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8080",
        "https://seatsync-frontend.railway.app",
        "https://seatsync.railway.app",
    ]
    ALLOWED_HOSTS: List[str] = [
        "localhost",
        "127.0.0.1",
        "*.railway.app",
        "seatsync.railway.app"
    ]
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    model_config = ConfigDict(
        env_file=".env",
        case_sensitive=True
    )

settings = Settings() 