from fastapi import APIRouter

from app.api.models import HealthResponse
from app.config import settings


router = APIRouter(tags=["health"])


@router.get(
    "/health",
    response_model=HealthResponse,
)
async def health() -> HealthResponse:
    """Return application health information."""

    return HealthResponse(
        status="healthy",
        app_name=settings.APP_NAME,
    )