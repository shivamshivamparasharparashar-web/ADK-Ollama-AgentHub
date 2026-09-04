import importlib

import pytest

from app.services.agent_runner import AgentRunner
from app.services.session_service import SessionManager


@pytest.fixture
async def runner(tmp_path):
    """
    Provide an AgentRunner backed by an isolated temporary SQLite database.

    Integration tests must not share the persistent application database:
    data/adk_sessions.db.
    """
    db_path = tmp_path / "test_multi_agent_delegation.db"
    db_url = f"sqlite+aiosqlite:///{db_path.as_posix()}"

    manager = SessionManager(db_url=db_url)
    await manager.initialize()

    agent_runner_module = importlib.import_module(
        "app.services.agent_runner"
    )

    original_session_manager = agent_runner_module.session_manager
    agent_runner_module.session_manager = manager

    try:
        yield AgentRunner()
    finally:
        agent_runner_module.session_manager = original_session_manager
        await manager.close()


@pytest.mark.asyncio
async def test_general_agent_delegation(runner):
    user_id = "test-user"
    session_id = "general-delegation-test"

    await runner.create_session(
        user_id=user_id,
        session_id=session_id,
    )

    events = await runner.run(
        user_id=user_id,
        session_id=session_id,
        message="What is 25 multiplied by 4?",
    )

    assert events

    print(f"\nEVENT COUNT: {len(events)}")

    for event in events:
        print(
            "AUTHOR:",
            getattr(event, "author", None),
            "| CONTENT:",
            getattr(event, "content", None),
        )


@pytest.mark.asyncio
async def test_mcp_agent_delegation(runner):
    user_id = "test-user"
    session_id = "mcp-delegation-test"

    await runner.create_session(
        user_id=user_id,
        session_id=session_id,
    )

    events = await runner.run(
        user_id=user_id,
        session_id=session_id,
        message="Use the MCP server to add 10 and 25.",
    )

    assert events

    print(f"\nEVENT COUNT: {len(events)}")

    for event in events:
        print(
            "AUTHOR:",
            getattr(event, "author", None),
            "| CONTENT:",
            getattr(event, "content", None),
        )


@pytest.mark.asyncio
async def test_api_agent_delegation(runner):
    user_id = "test-user"
    session_id = "api-agent-delegation-test"

    await runner.create_session(
        user_id=user_id,
        session_id=session_id,
    )

    events = await runner.run(
        user_id=user_id,
        session_id=session_id,
        message=(
            "Use an HTTP GET request to retrieve "
            "https://httpbin.org/get"
        ),
    )

    assert events

    print(f"\nEVENT COUNT: {len(events)}")

    for event in events:
        print(
            "AUTHOR:",
            getattr(event, "author", None),
            "| CONTENT:",
            getattr(event, "content", None),
        )