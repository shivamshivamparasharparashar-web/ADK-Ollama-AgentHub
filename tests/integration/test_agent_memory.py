import importlib

import pytest

from app.memory.memory_service import agent_memory
from app.services.agent_runner import AgentRunner
from app.services.session_service import SessionManager


@pytest.fixture
async def runner(tmp_path, monkeypatch):
    """
    Provide an AgentRunner backed by an isolated temporary SQLite database.

    Integration tests must not share the persistent application database:
    data/adk_sessions.db.
    """
    db_path = tmp_path / "test_agent_memory.db"
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

    yield AgentRunner()

    await manager.close()


@pytest.mark.anyio
async def test_agent_conversation_is_retrievable_from_memory(runner):
    user_id = "memory_integration_user"
    session_id = "memory-integration-session-001"

    await runner.create_session(
        user_id=user_id,
        session_id=session_id,
    )

    events = await runner.run(
        user_id=user_id,
        session_id=session_id,
        message="My project is called ADK-Ollama-AgentHub.",
    )

    assert events

    result = await agent_memory.search(
        user_id=user_id,
        query="What is my project called?",
    )

    assert result is not None
    assert len(result.memories) > 0

    memory_text = " ".join(
        part.text or ""
        for entry in result.memories
        for part in entry.content.parts
        if part.text
    )

    assert "ADK-Ollama-AgentHub" in memory_text