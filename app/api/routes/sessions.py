from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies import get_agent_runner
from app.api.models import CreateSessionRequest, SessionResponse
from app.errors import ApplicationError
from app.services.agent_runner import AgentRunner


router = APIRouter(tags=["sessions"])


def _session_to_response(session) -> SessionResponse:
    """Convert an ADK session into the public API response model."""

    return SessionResponse(
        app_name=session.app_name,
        user_id=session.user_id,
        session_id=session.id,
        state=dict(session.state),
    )


@router.post(
    "/sessions",
    response_model=SessionResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_session(
    request: CreateSessionRequest,
    runner: AgentRunner = Depends(get_agent_runner),
) -> SessionResponse:
    """Create a new agent session."""

    try:
        session = await runner.create_session(
            user_id=request.user_id,
            session_id=request.session_id,
            state=request.state,
        )

        return _session_to_response(session)

    except ApplicationError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=exc.to_dict(),
        ) from exc


@router.get(
    "/sessions/{session_id}",
    response_model=SessionResponse,
)
async def get_session(
    session_id: str,
    user_id: str,
    runner: AgentRunner = Depends(get_agent_runner),
) -> SessionResponse:
    """Retrieve an existing agent session."""

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

        return _session_to_response(session)

    except HTTPException:
        raise

    except ApplicationError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=exc.to_dict(),
        ) from exc