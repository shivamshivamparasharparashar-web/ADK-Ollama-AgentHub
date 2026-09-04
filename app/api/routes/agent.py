from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies import get_agent_runner
from app.api.models import AgentExecutionResponse, MessageRequest
from app.errors import ApplicationError
from app.services.agent_runner import AgentRunner


router = APIRouter(tags=["agent"])


def _event_to_dict(event: Any) -> dict[str, Any]:
    """Convert an ADK event into a JSON-compatible dictionary."""

    if hasattr(event, "model_dump"):
        return event.model_dump(mode="json")

    if hasattr(event, "dict"):
        return event.dict()

    if isinstance(event, dict):
        return event

    return {
        "event": str(event),
    }


@router.post(
    "/sessions/{session_id}/messages",
    response_model=AgentExecutionResponse,
    status_code=status.HTTP_200_OK,
)
async def execute_agent(
    session_id: str,
    request: MessageRequest,
    user_id: str,
    runner: AgentRunner = Depends(get_agent_runner),
) -> AgentExecutionResponse:
    """Execute the agent for an existing session."""

    try:
        session = await runner.get_session(
            user_id=user_id,
            session_id=session_id,
        )

        if session is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "error_code": "SESSION_NOT_FOUND",
                    "message": "Session not found.",
                },
            )

        events = await runner.run(
            user_id=user_id,
            session_id=session_id,
            message=request.message,
        )

        return AgentExecutionResponse(
            user_id=user_id,
            session_id=session_id,
            events=[
                _event_to_dict(event)
                for event in events
            ],
        )

    except HTTPException:
        raise

    except ApplicationError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=exc.to_dict(),
        ) from exc