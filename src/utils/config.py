"""Utilidades para cargar configuración."""

import yaml
from pathlib import Path
from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional


class Settings(BaseSettings):
    """Configuración del agente desde variables de entorno."""

    # API Keys
    openrouter_api_key: str = Field(alias="OPENROUTER_API_KEY")
    telegram_bot_token: Optional[str] = Field(default=None, alias="TELEGRAM_BOT_TOKEN")
    telegram_allowed_user_ids: str = Field(default="", alias="TELEGRAM_ALLOWED_USER_IDS")

    # Calendar
    calendar_path: Path = Field(
        default=Path.home() / ".local" / "share" / "calcurse", alias="CALENDAR_PATH"
    )
    calendar_sync_interval: int = Field(default=300, alias="CALENDAR_SYNC_INTERVAL")

    # Notifications
    enable_desktop_notifications: bool = Field(default=True, alias="ENABLE_DESKTOP_NOTIFICATIONS")
    enable_telegram_notifications: bool = Field(
        default=False, alias="ENABLE_TELEGRAM_NOTIFICATIONS"
    )
    notification_sound: bool = Field(default=True, alias="NOTIFICATION_SOUND")

    # Redis
    redis_url: str = Field(default="redis://localhost:6379", alias="REDIS_URL")
    use_redis: bool = Field(default=False, alias="USE_REDIS")

    # Logging
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    log_path: Path = Field(
        default=Path(__file__).parent.parent.parent / "data" / "logs", alias="LOG_PATH"
    )

    # Agent
    agent_model: str = Field(default="deepseek/deepseek-chat", alias="AGENT_MODEL")
    agent_max_context_messages: int = Field(default=20, alias="AGENT_MAX_CONTEXT_MESSAGES")
    agent_temperature: float = Field(default=0.7, alias="AGENT_TEMPERATURE")
    openrouter_base_url: str = Field(
        default="https://openrouter.ai/api/v1", alias="OPENROUTER_BASE_URL"
    )

    # Interfaces
    enable_cli: bool = Field(default=True, alias="ENABLE_CLI")
    enable_telegram: bool = Field(default=False, alias="ENABLE_TELEGRAM")
    enable_web: bool = Field(default=False, alias="ENABLE_WEB")
    web_host: str = Field(default="127.0.0.1", alias="WEB_HOST")
    web_port: int = Field(default=8000, alias="WEB_PORT")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


def load_yaml_config(config_path: Optional[Path] = None) -> dict:
    """Carga configuración desde archivo YAML."""
    if config_path is None:
        config_path = Path(__file__).parent.parent.parent / "config" / "agent_config.yaml"

    if not config_path.exists():
        return {}

    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def get_settings() -> Settings:
    """Obtiene la configuración del agente."""
    return Settings(_env_file=".env")
