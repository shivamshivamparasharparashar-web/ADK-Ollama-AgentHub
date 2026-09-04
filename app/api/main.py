from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.config import settings
from app.services.session_service import session_manager

from app.api.routes.agent import router as agent_router
from app.api.routes.health import router as health_router
from app.api.routes.sessions import router as sessions_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifecycle.

    Initializes the persistent ADK SQLite session database before
    the application starts accepting requests and closes the
    database service during application shutdown.
    """
    await session_manager.initialize()

    try:
        yield
    finally:
        await session_manager.close()


app = FastAPI(
    title="ADK-Ollama-AgentHub API",
    description="FastAPI service for ADK-Ollama-AgentHub.",
    version="1.0.0",
    lifespan=lifespan,
)


app.include_router(health_router)
app.include_router(sessions_router)
app.include_router(agent_router)


__all__ = ["app"]