"""Configuration module for environment variables and settings."""

import os
from typing import Optional
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Application configuration with environment variables."""

    # Telegram Bot Configuration
    TELEGRAM_BOT_TOKEN: str = os.environ.get("TELEGRAM_BOT_TOKEN", "")
    OWNER_TELEGRAM_ID: str = str(os.environ.get("OWNER_TELEGRAM_ID", "0"))

    # Agent Core Configuration
    AGENT_CORE_URL: Optional[str] = os.environ.get("AGENT_CORE_URL", None)

    # Process Management
    PID_FILE: str = ".bot_gateway.pid"

    # Logging
    LOG_LEVEL: str = os.environ.get("LOG_LEVEL", "INFO")

    @classmethod
    def validate(cls) -> None:
        """Validate required configuration values."""
        if not cls.TELEGRAM_BOT_TOKEN:
            raise ValueError("TELEGRAM_BOT_TOKEN environment variable is required")
        if cls.OWNER_TELEGRAM_ID == 0:
            raise ValueError("OWNER_TELEGRAM_ID environment variable is required and must be non-zero")


# Global config instance
config = Config()