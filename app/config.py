from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlparse

from dotenv import load_dotenv

from app.errors import ConfigurationError


# Load the application-local .env without overriding explicitly
# supplied process environment variables.
_ENV_FILE = Path(__file__).resolve().parent / ".env"

load_dotenv(
    dotenv_path=_ENV_FILE,
    override=False,
)


@dataclass(frozen=True, slots=True)
class Settings:
    """Validated application configuration."""

    APP_NAME: str = os.getenv(
        "APP_NAME",
        "adk_ollama_agent",
    )

    OLLAMA_API_BASE: str = os.getenv(
        "OLLAMA_API_BASE",
        "http://localhost:11434",
    )

    OLLAMA_MODEL: str = os.getenv(
        "OLLAMA_MODEL",
        "qwen3:8b",
    )

    LOG_LEVEL: str = os.getenv(
        "LOG_LEVEL",
        "INFO",
    ).upper()

    def validate(self) -> None:
        """Validate configuration values required by the application."""

        if not self.APP_NAME.strip():
            raise ConfigurationError(
                "APP_NAME must not be empty."
            )

        if not self.OLLAMA_MODEL.strip():
            raise ConfigurationError(
                "OLLAMA_MODEL must not be empty."
            )

        parsed = urlparse(self.OLLAMA_API_BASE)

        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            raise ConfigurationError(
                "OLLAMA_API_BASE must be a valid HTTP or HTTPS URL."
            )

        if self.LOG_LEVEL not in {
            "DEBUG",
            "INFO",
            "WARNING",
            "ERROR",
            "CRITICAL",
        }:
            raise ConfigurationError(
                "LOG_LEVEL must be one of "
                "DEBUG, INFO, WARNING, ERROR, CRITICAL."
            )


settings = Settings()
settings.validate()


__all__ = [
    "Settings",
    "settings",
]