import logging

import pytest

from app.config import settings
from app.errors import (
    AgentExecutionError,
    ApplicationError,
    ConfigurationError,
    SessionError,
    ToolExecutionError,
    normalize_exception,
)
from app.utils.logger import LOGGER_NAME, logger, setup_logging


def test_settings_are_typed_and_validated():
    assert settings.APP_NAME
    assert settings.OLLAMA_MODEL
    assert settings.OLLAMA_API_BASE.startswith(
        ("http://", "https://")
    )

    assert settings.LOG_LEVEL in {
        "DEBUG",
        "INFO",
        "WARNING",
        "ERROR",
        "CRITICAL",
    }


def test_settings_are_immutable():
    with pytest.raises(AttributeError):
        settings.APP_NAME = "changed"


@pytest.mark.parametrize(
    "error_type",
    [
        ApplicationError,
        ConfigurationError,
        SessionError,
        AgentExecutionError,
        ToolExecutionError,
    ],
)
def test_application_error_hierarchy(error_type):
    error = error_type("operation failed")

    assert isinstance(error, ApplicationError)
    assert error.to_dict()["message"] == "operation failed"
    assert error.to_dict()["error_code"]


def test_normalize_exception_hides_internal_message():
    error = normalize_exception(
        RuntimeError(
            "secret internal database detail"
        ),
        operation="Agent execution",
    )

    assert isinstance(error, ApplicationError)
    assert str(error) == "Agent execution failed."
    assert (
        "secret internal database detail"
        not in str(error)
    )
    assert error.details == "RuntimeError"


def test_normalize_existing_application_error():
    original = ApplicationError("safe message")

    normalized = normalize_exception(
        original,
        operation="Agent execution",
    )

    assert normalized is original


def test_logging_setup_is_idempotent():
    configured = setup_logging()

    assert configured is logger
    assert configured.name == LOGGER_NAME
    assert configured.level == getattr(
        logging,
        settings.LOG_LEVEL,
    )

    handler_count = len(configured.handlers)

    configured_again = setup_logging()

    assert configured_again is configured
    assert len(configured_again.handlers) == handler_count