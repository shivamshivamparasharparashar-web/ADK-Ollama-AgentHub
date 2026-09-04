import pytest

from app.services.session_service import SessionManager


@pytest.fixture
async def session_manager(tmp_path):
    db_path = tmp_path / "test_sessions.db"
    db_url = f"sqlite+aiosqlite:///{db_path.as_posix()}"

    manager = SessionManager(db_url=db_url)
    await manager.initialize()

    yield manager

    await manager.close()


@pytest.mark.anyio
async def test_create_session(session_manager):
    session = await session_manager.create_session(
        app_name="adk_ollama_agent",
        user_id="user_001",
        session_id="session_001",
    )

    assert session.id == "session_001"
    assert session.user_id == "user_001"
    assert session.app_name == "adk_ollama_agent"


@pytest.mark.anyio
async def test_create_session_with_state(session_manager):
    session = await session_manager.create_session(
        app_name="adk_ollama_agent",
        user_id="user_001",
        session_id="session_002",
        state={
            "user_name": "Shivam",
            "environment": "development",
        },
    )

    assert session.state["user_name"] == "Shivam"
    assert session.state["environment"] == "development"


@pytest.mark.anyio
async def test_get_session(session_manager):
    await session_manager.create_session(
        app_name="adk_ollama_agent",
        user_id="user_001",
        session_id="session_003",
    )

    session = await session_manager.get_session(
        app_name="adk_ollama_agent",
        user_id="user_001",
        session_id="session_003",
    )

    assert session is not None
    assert session.id == "session_003"


@pytest.mark.anyio
async def test_delete_session(session_manager):
    await session_manager.create_session(
        app_name="adk_ollama_agent",
        user_id="user_001",
        session_id="session_004",
    )

    await session_manager.delete_session(
        app_name="adk_ollama_agent",
        user_id="user_001",
        session_id="session_004",
    )

    session = await session_manager.get_session(
        app_name="adk_ollama_agent",
        user_id="user_001",
        session_id="session_004",
    )

    assert session is None