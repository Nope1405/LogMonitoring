"""
Application configuration using pydantic-settings.
Loads values from .env file with type validation.
"""

from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://logmoni_user:logmoni_secret@localhost:5432/logmoni"
    DATABASE_URL_SYNC: str = "postgresql://logmoni_user:logmoni_secret@localhost:5432/logmoni"

    # RabbitMQ
    RABBITMQ_URL: str = "amqp://logmoni:logmoni_secret@localhost:5672/"
    RABBITMQ_QUEUE_NAME: str = "log_events"

    # Application
    APP_ENV: str = "development"
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000

    # Alert thresholds
    ALERT_ERROR_RATE_THRESHOLD: int = 10  # errors per window
    ALERT_SPAM_IP_THRESHOLD: int = 100    # requests per IP per window
    ALERT_WINDOW_MINUTES: int = 5

    class Config:
        env_file = "../.env"
        env_file_encoding = "utf-8"
        extra = "ignore"  # Ignore VITE_* and other unknown keys from shared .env


@lru_cache()
def get_settings() -> Settings:
    """Cached settings instance to avoid re-reading .env on every request."""
    return Settings()
