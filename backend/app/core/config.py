"""
Application Configuration and Settings
"""

from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "FOREX AI"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Environment & Database
    ENV: str = "development"
    DATABASE_URL: str = "sqlite+aiosqlite:///./forex_ai.db"
    MONGODB_URI: str = "mongodb://localhost:27017"
    MONGODB_DB_NAME: str = "forex_ai"
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Security
    SECRET_KEY: str = "forex_ai_super_secret_production_key_change_in_env_382947194"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    ALGORITHM: str = "HS256"
    
    # Market Data
    DATA_PROVIDER: str = "mock"  # "mock" | "twelvedata" | "alphavantage" | "oanda"
    DEFAULT_PAIR: str = "EUR/USD"
    DEFAULT_TIMEFRAME: str = "1H"
    
    SUPPORTED_PAIRS: List[str] = [
        "EUR/USD", "GBP/USD", "USD/JPY", "USD/CHF", "AUD/USD",
        "USD/CAD", "NZD/USD", "EUR/GBP", "EUR/JPY", "GBP/JPY"
    ]
    
    SUPPORTED_TIMEFRAMES: List[str] = [
        "1M", "5M", "15M", "30M", "1H", "4H", "1D"
    ]

    # CORS
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
    ]

    model_config = SettingsConfigDict(case_sensitive=True, env_file=".env", extra="ignore")


settings = Settings()
