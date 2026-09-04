from __future__ import annotations

from typing import Any


class ApplicationError(Exception):
    """Base exception for application-level failures."""

    error_code = "APPLICATION_ERROR"

    def __init__(
        self,
        message: str,
        *,
        details: Any | None = None,
    ) -> None:
        super().__init__(message)

        self.message = message
        self.details = details

    def to_dict(self) -> dict[str, Any]:
        """Return a safe structured representation of the error."""

        return {
            "error_code": self.error_code,
            "message": self.message,
        }


class ConfigurationError(ApplicationError):
    """Raised when application configuration is invalid."""

    error_code = "CONFIGURATION_ERROR"


class SessionError(ApplicationError):
    """Raised when an application session operation fails."""

    error_code = "SESSION_ERROR"


class AgentExecutionError(ApplicationError):
    """Raised when an agent execution fails."""

    error_code = "AGENT_EXECUTION_ERROR"


class ToolExecutionError(ApplicationError):
    """Raised when an application tool operation fails."""

    error_code = "TOOL_EXECUTION_ERROR"


def normalize_exception(
    error: Exception,
    *,
    operation: str,
) -> ApplicationError:
    """Convert an unexpected exception into a safe application error."""

    if isinstance(error, ApplicationError):
        return error

    return ApplicationError(
        f"{operation} failed.",
        details=type(error).__name__,
    )


__all__ = [
    "ApplicationError",
    "ConfigurationError",
    "SessionError",
    "AgentExecutionError",
    "ToolExecutionError",
    "normalize_exception",
]