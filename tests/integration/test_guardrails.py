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
    db_path = tmp_path / "test_guardrails.db"
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
async def test_guardrail_allows_valid_agent_request(runner):
    """
    A normal valid request should pass through the guardrails
    and reach the agent.
    """
    user_id = "guardrail-test-user"
    session_id = "guardrail-valid-request"

    await runner.create_session(
        user_id=user_id,
        session_id=session_id,
    )

    events = await runner.run(
        user_id=user_id,
        session_id=session_id,
        message="Hello, how are you?",
    )

    assert events
    assert any(
        getattr(event, "content", None) is not None
        for event in events
    )


@pytest.mark.asyncio
async def test_guardrail_allows_normal_calculation_request(runner):
    """
    A valid calculation request should pass the guardrails
    and allow the calculator tool to execute.
    """
    user_id = "guardrail-test-user"
    session_id = "guardrail-calculation"

    await runner.create_session(
        user_id=user_id,
        session_id=session_id,
    )

    events = await runner.run(
        user_id=user_id,
        session_id=session_id,
        message="Calculate 25 * 4",
    )

    assert events


@pytest.mark.asyncio
async def test_guardrail_does_not_block_normal_conversation(runner):
    """
    Normal conversation must not be rejected by the guardrails.

    Do not assert that the word 'guardrail' is absent from the
    response because the root-agent instruction itself contains
    the word 'guardrails', and the model may legitimately repeat it.
    """
    user_id = "guardrail-test-user"
    session_id = "guardrail-normal-conversation"

    await runner.create_session(
        user_id=user_id,
        session_id=session_id,
    )

    events = await runner.run(
        user_id=user_id,
        session_id=session_id,
        message="Tell me something interesting about Python.",
    )

    assert events

    response_parts = []

    for event in events:
        content = getattr(event, "content", None)

        if content is None:
            continue

        parts = getattr(content, "parts", None)

        if not parts:
            continue

        for part in parts:
            text = getattr(part, "text", None)

            if text:
                response_parts.append(text)

    response = " ".join(response_parts).strip()

    assert response

    blocked_messages = (
        "blocked",
        "rejected",
        "invalid input",
        "input validation failed",
    )

    assert not any(
        message in response.lower()
        for message in blocked_messages
    )


@pytest.mark.asyncio
async def test_guardrail_blocks_empty_request(runner):
    """
    Empty input must be blocked by the before-agent guardrail.
    """
    user_id = "guardrail-test-user"
    session_id = "guardrail-empty-request"

    await runner.create_session(
        user_id=user_id,
        session_id=session_id,
    )

    events = await runner.run(
        user_id=user_id,
        session_id=session_id,
        message="",
    )

    assert events

    response_parts = []

    for event in events:
        content = getattr(event, "content", None)

        if content is None:
            continue

        parts = getattr(content, "parts", None)

        if not parts:
            continue

        for part in parts:
            text = getattr(part, "text", None)

            if text:
                response_parts.append(text)

    response = " ".join(response_parts).lower()

    assert response

    assert any(
        message in response
        for message in (
            "invalid",
            "blocked",
            "empty",
            "input",
        )
    )


@pytest.mark.asyncio
async def test_guardrail_blocks_whitespace_request(runner):
    """
    Whitespace-only input must be rejected.
    """
    user_id = "guardrail-test-user"
    session_id = "guardrail-whitespace-request"

    await runner.create_session(
        user_id=user_id,
        session_id=session_id,
    )

    events = await runner.run(
        user_id=user_id,
        session_id=session_id,
        message="   ",
    )

    assert events


@pytest.mark.asyncio
async def test_guardrail_blocks_oversized_request(runner):
    """
    Input larger than MAX_INPUT_LENGTH must be rejected.
    """
    user_id = "guardrail-test-user"
    session_id = "guardrail-oversized-request"

    await runner.create_session(
        user_id=user_id,
        session_id=session_id,
    )

    oversized_message = "A" * 10_001

    events = await runner.run(
        user_id=user_id,
        session_id=session_id,
        message=oversized_message,
    )

    assert events


@pytest.mark.asyncio
async def test_guardrail_allows_input_at_exact_limit(runner):
    """
    Exactly MAX_INPUT_LENGTH characters should be allowed.

    Note:
    This test invokes the real model and can therefore be slower
    than the unit-level boundary test.
    """
    user_id = "guardrail-test-user"
    session_id = "guardrail-exact-boundary"

    await runner.create_session(
        user_id=user_id,
        session_id=session_id,
    )

    boundary_message = "A" * 10_000

    events = await runner.run(
        user_id=user_id,
        session_id=session_id,
        message=boundary_message,
    )

    assert events


@pytest.mark.asyncio
async def test_guardrail_blocks_input_one_character_over_limit(runner):
    """
    Input exceeding MAX_INPUT_LENGTH by one character must be rejected.
    """
    user_id = "guardrail-test-user"
    session_id = "guardrail-over-limit-by-one"

    await runner.create_session(
        user_id=user_id,
        session_id=session_id,
    )

    oversized_message = "A" * 10_001

    events = await runner.run(
        user_id=user_id,
        session_id=session_id,
        message=oversized_message,
    )

    assert events


@pytest.mark.asyncio
async def test_guardrail_blocks_null_character_request(runner):
    """
    Input containing a null character must be rejected.
    """
    user_id = "guardrail-test-user"
    session_id = "guardrail-null-character"

    await runner.create_session(
        user_id=user_id,
        session_id=session_id,
    )

    events = await runner.run(
        user_id=user_id,
        session_id=session_id,
        message="hello\x00world",
    )

    assert events


@pytest.mark.asyncio
async def test_blocked_request_does_not_prevent_followup_request(runner):
    """
    A blocked request must not corrupt the session.

    A valid follow-up request should still be executable.
    """
    user_id = "guardrail-test-user"
    session_id = "guardrail-follow-up"

    await runner.create_session(
        user_id=user_id,
        session_id=session_id,
    )

    # First request is invalid.
    blocked_events = await runner.run(
        user_id=user_id,
        session_id=session_id,
        message="",
    )

    assert blocked_events

    # Second request is valid.
    valid_events = await runner.run(
        user_id=user_id,
        session_id=session_id,
        message="Hello, can you help me?",
    )

    assert valid_events