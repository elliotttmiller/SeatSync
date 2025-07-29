import os
from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import validator


class Settings(BaseSettings):
    # API Configuration
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "SeatSync"
    
    # Railway Configuration
    PORT: int = int(os.getenv("PORT", 8000))
    RAILWAY_STATIC_URL: Optional[str] = None
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-here")
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "your-jwt-secret-key")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Database - Railway PostgreSQL
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", 
        "postgresql://postgres:password@localhost/seatsync"
    )
    
    # Redis - Railway Redis (optional)
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    
    # CORS - Railway domains
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8080",
        "https://seatsync-frontend.railway.app",  # Railway frontend domain
        "https://seatsync.railway.app",          # Railway custom domain
    ]
    
    # Allowed hosts
    ALLOWED_HOSTS: List[str] = [
        "localhost", 
        "127.0.0.1",
        "*.railway.app",
        "seatsync.railway.app"
    ]
    
    # External APIs
    STUBHUB_API_KEY: Optional[str] = os.getenv("STUBHUB_API_KEY")
    STUBHUB_API_SECRET: Optional[str] = os.getenv("STUBHUB_API_SECRET")
    SEATGEEK_API_KEY: Optional[str] = os.getenv("SEATGEEK_API_KEY")
    TICKETMASTER_API_KEY: Optional[str] = os.getenv("TICKETMASTER_API_KEY")
    
    # Sports Data APIs
    SPORTRADAR_API_KEY: Optional[str] = os.getenv("SPORTRADAR_API_KEY")
    WEATHER_API_KEY: Optional[str] = os.getenv("WEATHER_API_KEY")
    
    # Environment
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    DEBUG: bool = os.getenv("DEBUG", "true").lower() == "true"
    
    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v):
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings() 