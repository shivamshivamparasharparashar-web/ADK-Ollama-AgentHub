from __future__ import annotations

import logging
from pathlib import Path

from app.config import settings


LOGGER_NAME = "adk-ollama-agent"

_LOG_FORMAT = (
    "%(asctime)s | "
    "%(levelname)s | "
    "%(name)s | "
    "%(message)s"
)


def setup_logging() -> logging.Logger:
    """Configure application logging once and return the application logger."""

    logger = logging.getLogger(LOGGER_NAME)

    logger.setLevel(settings.LOG_LEVEL)
    logger.propagate = False

    # Prevent duplicate handlers when setup_logging() is called more than once.
    if logger.handlers:
        return logger

    project_root = Path(__file__).resolve().parents[2]

    log_directory = project_root / "logs"
    log_directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    formatter = logging.Formatter(_LOG_FORMAT)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)

    file_handler = logging.FileHandler(
        log_directory / "agent.log",
        encoding="utf-8",
    )
    file_handler.setFormatter(formatter)

    logger.addHandler(stream_handler)
    logger.addHandler(file_handler)

    return logger


logger = logging.getLogger(LOGGER_NAME)


__all__ = [
    "LOGGER_NAME",
    "logger",
    "setup_logging",
]