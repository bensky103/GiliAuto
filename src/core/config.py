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
    monday_phone_column_id: str = "phone"
    monday_status_column_id: str = "status"

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

    # Message scheduling
    initial_message_delay_minutes: int = 6  # Delay before sending first message
    scheduler_interval_minutes: int = 1  # How often scheduler runs (1-2 min for accuracy)

    # WhatsApp Template Names (must be approved in Meta Business)
    whatsapp_welcome_template: str = "hello_world"
    whatsapp_followup_template: str = "hello_world"
    whatsapp_template_language: str = "en_US"
    use_whatsapp_templates: bool = False  # Set to True when templates are approved


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
