from __future__ import annotations

import pytest

from app.services.session_service import SessionManager


@pytest.mark.asyncio
async def test_session_persists_across_service_instances(tmp_path):
    database_path = tmp_path / "sessions.db"
    database_url = f"sqlite+aiosqlite:///{database_path.as_posix()}"

    manager_one = SessionManager(database_url)
    await manager_one.initialize()

    created = await manager_one.create_session(
        app_name="test-app",
        user_id="test-user",
        session_id="persistent-session",
        state={"project": "ADK-Ollama-AgentHub"},
    )

    assert created.id == "persistent-session"
    assert created.state["project"] == "ADK-Ollama-AgentHub"

    await manager_one.close()

    manager_two = SessionManager(database_url)
    await manager_two.initialize()

    restored = await manager_two.get_session(
        app_name="test-app",
        user_id="test-user",
        session_id="persistent-session",
    )

    assert restored is not None
    assert restored.id == "persistent-session"
    assert restored.state["project"] == "ADK-Ollama-AgentHub"

    await manager_two.close()


@pytest.mark.asyncio
async def test_session_delete_persists(tmp_path):
    database_path = tmp_path / "sessions.db"
    database_url = f"sqlite+aiosqlite:///{database_path.as_posix()}"

    manager = SessionManager(database_url)
    await manager.initialize()

    await manager.create_session(
        app_name="test-app",
        user_id="test-user",
        session_id="delete-session",
    )

    await manager.delete_session(
        app_name="test-app",
        user_id="test-user",
        session_id="delete-session",
    )

    session = await manager.get_session(
        app_name="test-app",
        user_id="test-user",
        session_id="delete-session",
    )

    assert session is None

    await manager.close()