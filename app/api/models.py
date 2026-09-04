from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class HealthResponse(BaseModel):
    """Health endpoint response."""

    model_config = ConfigDict(extra="forbid")

    status: str
    app_name: str


class CreateSessionRequest(BaseModel):
    """Request body for creating an agent session."""

    model_config = ConfigDict(extra="forbid")

    user_id: str = Field(
        min_length=1,
        max_length=200,
    )
    session_id: str | None = Field(
        default=None,
        min_length=1,
        max_length=200,
    )
    state: dict[str, Any] | None = None


class SessionResponse(BaseModel):
    """Public representation of an agent session."""

    model_config = ConfigDict(extra="forbid")

    app_name: str
    user_id: str
    session_id: str
    state: dict[str, Any]


class MessageRequest(BaseModel):
    """Request body for agent execution."""

    model_config = ConfigDict(extra="forbid")

    message: str = Field(
        min_length=1,
        max_length=10_000,
    )


class AgentExecutionResponse(BaseModel):
    """Response returned after agent execution."""

    model_config = ConfigDict(extra="forbid")

    user_id: str
    session_id: str
    events: list[dict[str, Any]]


class ErrorResponse(BaseModel):
    """Structured API error response."""

    model_config = ConfigDict(extra="forbid")

    error_code: str
    message: str