"""Configuration management for GrokViz."""

import os
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

from src.utils.errors import ConfigurationError


class Config:
    """Application configuration loaded from environment variables."""

    def __init__(self):
        """Initialize configuration from environment variables."""
        # Email configuration
        self.email_server = self._get_required("EMAIL_SERVER")
        self.email_port = self._get_int("EMAIL_PORT", default=993)
        self.email_username = self._get_required("EMAIL_USERNAME")
        self.email_password = self._get_required("EMAIL_PASSWORD")
        self.grok_sender_email = self._get_required("GROK_SENDER_EMAIL")

        # Gemini API configuration
        self.gemini_api_key = self._get_required("GEMINI_API_KEY")
        self.gemini_model = os.getenv("GEMINI_MODEL", "gemini-1.5-pro")

        # Telegram configuration
        self.telegram_bot_token = self._get_required("TELEGRAM_BOT_TOKEN")
        self.telegram_chat_id = self._get_required("TELEGRAM_CHAT_ID")

        # Application configuration
        self.log_level = os.getenv("LOG_LEVEL", "INFO").upper()
        self.data_dir = Path(os.getenv("DATA_DIR", "/app/data"))
        self.temp_dir = Path(os.getenv("TEMP_DIR", "/app/data/temp"))
        self.archive_emails = self._get_bool("ARCHIVE_EMAILS", default=True)
        self.processing_timeout = self._get_int("PROCESSING_TIMEOUT", default=180)

        # Retry configuration
        self.max_retries = self._get_int("MAX_RETRIES", default=3)
        self.retry_delay = self._get_int("RETRY_DELAY", default=5)

        # Validate configuration
        self._validate()

    @staticmethod
    def _get_required(key: str) -> str:
        """Get required environment variable or raise error."""
        value = os.getenv(key)
        if not value:
            raise ConfigurationError(
                f"Required environment variable '{key}' is not set",
                context={"missing_key": key}
            )
        return value

    @staticmethod
    def _get_int(key: str, default: int) -> int:
        """Get integer environment variable with default."""
        value = os.getenv(key)
        if value is None:
            return default
        try:
            return int(value)
        except ValueError:
            raise ConfigurationError(
                f"Environment variable '{key}' must be an integer, got '{value}'",
                context={"key": key, "value": value}
            )

    @staticmethod
    def _get_bool(key: str, default: bool) -> bool:
        """Get boolean environment variable with default."""
        value = os.getenv(key)
        if value is None:
            return default
        return value.lower() in ("true", "1", "yes", "on")

    def _validate(self):
        """Validate configuration values."""
        # Validate log level
        valid_log_levels = ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL")
        if self.log_level not in valid_log_levels:
            raise ConfigurationError(
                f"Invalid LOG_LEVEL '{self.log_level}'. Must be one of: {valid_log_levels}",
                context={"log_level": self.log_level}
            )

        # Validate email port
        if not (1 <= self.email_port <= 65535):
            raise ConfigurationError(
                f"Invalid EMAIL_PORT '{self.email_port}'. Must be between 1 and 65535",
                context={"email_port": self.email_port}
            )

        # Validate timeouts and retries
        if self.processing_timeout <= 0:
            raise ConfigurationError(
                f"PROCESSING_TIMEOUT must be positive, got {self.processing_timeout}",
                context={"processing_timeout": self.processing_timeout}
            )

        if self.max_retries < 0:
            raise ConfigurationError(
                f"MAX_RETRIES must be non-negative, got {self.max_retries}",
                context={"max_retries": self.max_retries}
            )

        if self.retry_delay < 0:
            raise ConfigurationError(
                f"RETRY_DELAY must be non-negative, got {self.retry_delay}",
                context={"retry_delay": self.retry_delay}
            )

    @classmethod
    def from_env(cls, env_file: Optional[Path] = None) -> "Config":
        """
        Load configuration from environment file.

        Args:
            env_file: Path to .env file. If None, looks for .env in current directory.

        Returns:
            Config instance
        """
        if env_file:
            load_dotenv(env_file)
        else:
            load_dotenv()

        return cls()

    def __repr__(self) -> str:
        """String representation (without sensitive data)."""
        return (
            f"Config(email_server={self.email_server}, "
            f"email_port={self.email_port}, "
            f"gemini_model={self.gemini_model}, "
            f"log_level={self.log_level})"
        )
