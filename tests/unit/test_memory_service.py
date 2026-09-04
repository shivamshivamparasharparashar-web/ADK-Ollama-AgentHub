import pytest

from google.adk.events import Event
from google.genai import types

from app.memory.memory_service import AgentMemory


def create_test_session(
    session_id: str,
    user_id: str,
    text: str,
    app_name: str = "adk_ollama_agent",
):
    """Create a minimal ADK-compatible session for memory testing."""
    return type(
        "TestSession",
        (),
        {
            "id": session_id,
            "app_name": app_name,
            "user_id": user_id,
            "events": [
                Event(
                    author="user",
                    content=types.Content(
                        role="user",
                        parts=[
                            types.Part(text=text),
                        ],
                    ),
                )
            ],
        },
    )()


def extract_memory_text(result) -> str:
    """Extract searchable text from SearchMemoryResponse."""
    return " ".join(
        part.text or ""
        for entry in result.memories
        for part in entry.content.parts
        if part.text
    )


@pytest.mark.anyio
async def test_memory_service_initializes():
    memory = AgentMemory()

    assert memory is not None
    assert memory.service is not None


@pytest.mark.anyio
async def test_memory_search_empty_memory():
    memory = AgentMemory()

    result = await memory.search(
        user_id="test_user",
        query="What is my name?",
    )

    assert result is not None
    assert result.memories == []


@pytest.mark.anyio
async def test_memory_stores_and_retrieves_session():
    memory = AgentMemory()

    session = create_test_session(
        session_id="memory-session-001",
        user_id="memory_user",
        text="My project is called ADK-Ollama-AgentHub.",
    )

    await memory.add_session_to_memory(session)

    result = await memory.search(
        user_id="memory_user",
        query="What is my project called?",
    )

    assert result is not None
    assert len(result.memories) > 0

    memory_text = extract_memory_text(result)

    assert "ADK-Ollama-AgentHub" in memory_text


@pytest.mark.anyio
async def test_memory_isolated_between_users():
    memory = AgentMemory()

    user_a_session = create_test_session(
        session_id="user-a-session",
        user_id="user_a",
        text="My project is SAP Automation.",
    )

    user_b_session = create_test_session(
        session_id="user-b-session",
        user_id="user_b",
        text="My project is API Testing.",
    )

    await memory.add_session_to_memory(user_a_session)
    await memory.add_session_to_memory(user_b_session)

    user_a_result = await memory.search(
        user_id="user_a",
        query="What is my project?",
    )

    user_b_result = await memory.search(
        user_id="user_b",
        query="What is my project?",
    )

    user_a_text = extract_memory_text(user_a_result)
    user_b_text = extract_memory_text(user_b_result)

    assert "SAP Automation" in user_a_text
    assert "API Testing" not in user_a_text

    assert "API Testing" in user_b_text
    assert "SAP Automation" not in user_b_text


@pytest.mark.anyio
async def test_memory_supports_multiple_sessions_for_same_user():
    memory = AgentMemory()

    session_1 = create_test_session(
        session_id="session-001",
        user_id="same_user",
        text="I am working on ADK-Ollama-AgentHub.",
    )

    session_2 = create_test_session(
        session_id="session-002",
        user_id="same_user",
        text="I am also working on SAP automation.",
    )

    await memory.add_session_to_memory(session_1)
    await memory.add_session_to_memory(session_2)

    result = await memory.search(
        user_id="same_user",
        query="What projects am I working on?",
    )

    assert result is not None
    assert len(result.memories) >= 1

    memory_text = extract_memory_text(result)

    assert "ADK-Ollama-AgentHub" in memory_text
    assert "SAP automation" in memory_text


@pytest.mark.anyio
async def test_memory_search_is_case_insensitive():
    memory = AgentMemory()

    session = create_test_session(
        session_id="case-session",
        user_id="case_user",
        text="ADK-Ollama-AgentHub is my automation platform.",
    )

    await memory.add_session_to_memory(session)

    result = await memory.search(
        user_id="case_user",
        query="adk ollama agenthub",
    )

    assert result is not None
    assert len(result.memories) > 0

    memory_text = extract_memory_text(result)

    assert "ADK-Ollama-AgentHub" in memory_text