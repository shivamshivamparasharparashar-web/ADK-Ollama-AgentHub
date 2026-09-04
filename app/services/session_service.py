from __future__ import annotations

from pathlib import Path

from google.adk.sessions import DatabaseSessionService


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data"
DATABASE_PATH = DATA_DIR / "adk_sessions.db"

DATA_DIR.mkdir(parents=True, exist_ok=True)

DATABASE_URL = f"sqlite+aiosqlite:///{DATABASE_PATH.as_posix()}"


class SessionManager:
    """Application boundary for persistent ADK sessions."""

    def __init__(self, db_url: str = DATABASE_URL) -> None:
        self.db_url = db_url
        self.service = DatabaseSessionService(db_url=db_url)

    async def initialize(self) -> None:
        """Create/update ADK session tables."""
        await self.service.prepare_tables()

    async def create_session(
        self,
        app_name: str,
        user_id: str,
        session_id: str | None = None,
        state: dict | None = None,
    ):
        return await self.service.create_session(
            app_name=app_name,
            user_id=user_id,
            session_id=session_id,
            state=state or {},
        )

    async def get_session(
        self,
        app_name: str,
        user_id: str,
        session_id: str,
    ):
        return await self.service.get_session(
            app_name=app_name,
            user_id=user_id,
            session_id=session_id,
        )

    async def delete_session(
        self,
        app_name: str,
        user_id: str,
        session_id: str,
    ):
        return await self.service.delete_session(
            app_name=app_name,
            user_id=user_id,
            session_id=session_id,
        )

    async def close(self) -> None:
        await self.service.close()


session_manager = SessionManager()

__all__ = [
    "DATABASE_PATH",
    "DATABASE_URL",
    "SessionManager",
    "session_manager",
]