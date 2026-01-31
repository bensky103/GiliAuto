"""Application configuration using Pydantic Settings."""

from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # Monday.com
    monday_api_key: str
    monday_board_id: str

    # Meta WhatsApp API
    meta_api_token: str
    meta_phone_id: str

    # Database
    database_url: str = "sqlite+aiosqlite:///./data/leads.db"

    # Admin
    admin_secret: str = "change-me-in-production"

    # App Settings
    environment: Literal["development", "production"] = "development"
    log_level: str = "INFO"

    # Time Window (Israel Time) for sending follow-up messages
    send_window_start_hour: int = 8
    send_window_end_hour: int = 21


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
