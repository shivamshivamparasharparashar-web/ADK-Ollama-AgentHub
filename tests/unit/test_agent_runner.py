import importlib

import pytest

from app.services.agent_runner import AgentRunner
from app.services.session_service import SessionManager


@pytest.fixture
async def session_manager(tmp_path, monkeypatch):
    db_path = tmp_path / "test_agent_runner.db"
    db_url = f"sqlite+aiosqlite:///{db_path.as_posix()}"

    manager = SessionManager(db_url=db_url)
    await manager.initialize()

    agent_runner_module = importlib.import_module(
        "app.services.agent_runner"
    )

    monkeypatch.setattr(
        agent_runner_module,
        "session_manager",
        manager,
    )

    yield manager

    await manager.close()


@pytest.mark.anyio
async def test_agent_runner_creates_session(session_manager):
    runner = AgentRunner()

    session = await runner.create_session(
        user_id="user_runner_001",
        session_id="runner_session_001",
    )

    assert session is not None
    assert session.id == "runner_session_001"
    assert session.user_id == "user_runner_001"


@pytest.mark.anyio
async def test_agent_runner_gets_session(session_manager):
    runner = AgentRunner()

    await runner.create_session(
        user_id="user_runner_002",
        session_id="runner_session_002",
    )

    session = await runner.get_session(
        user_id="user_runner_002",
        session_id="runner_session_002",
    )

    assert session is not None
    assert session.id == "runner_session_002"