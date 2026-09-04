from __future__ import annotations

from unittest.mock import AsyncMock

from fastapi.testclient import TestClient

from app.api.dependencies import get_agent_runner
from app.api.main import app


class FakeSession:
    def __init__(
        self,
        *,
        app_name: str = "adk_ollama_agent",
        user_id: str = "test-user",
        session_id: str = "test-session",
        state: dict | None = None,
    ) -> None:
        self.app_name = app_name
        self.user_id = user_id
        self.id = session_id
        self.state = state or {}


class FakeRunner:
    def __init__(self) -> None:
        self.create_session = AsyncMock()
        self.get_session = AsyncMock()
        self.run = AsyncMock()


def _client_with_runner(
    runner: FakeRunner,
) -> TestClient:
    app.dependency_overrides[get_agent_runner] = lambda: runner
    return TestClient(app)


def teardown_function() -> None:
    app.dependency_overrides.clear()


def test_health() -> None:
    client = TestClient(app)

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "healthy",
        "app_name": "adk_ollama_agent",
    }


def test_create_session() -> None:
    runner = FakeRunner()
    runner.create_session.return_value = FakeSession(
        session_id="session-001",
        user_id="user-001",
        state={"key": "value"},
    )

    client = _client_with_runner(runner)

    response = client.post(
        "/sessions",
        json={
            "user_id": "user-001",
            "session_id": "session-001",
            "state": {"key": "value"},
        },
    )

    assert response.status_code == 201
    assert response.json() == {
        "app_name": "adk_ollama_agent",
        "user_id": "user-001",
        "session_id": "session-001",
        "state": {"key": "value"},
    }

    runner.create_session.assert_awaited_once_with(
        user_id="user-001",
        session_id="session-001",
        state={"key": "value"},
    )


def test_get_existing_session() -> None:
    runner = FakeRunner()
    runner.get_session.return_value = FakeSession(
        session_id="session-001",
        user_id="user-001",
        state={"key": "value"},
    )

    client = _client_with_runner(runner)

    response = client.get(
        "/sessions/session-001",
        params={"user_id": "user-001"},
    )

    assert response.status_code == 200
    assert response.json()["session_id"] == "session-001"
    assert response.json()["user_id"] == "user-001"
    assert response.json()["state"] == {"key": "value"}


def test_get_missing_session_returns_structured_404() -> None:
    runner = FakeRunner()
    runner.get_session.return_value = None

    client = _client_with_runner(runner)

    response = client.get(
        "/sessions/missing-session",
        params={"user_id": "user-001"},
    )

    assert response.status_code == 404
    assert response.json() == {
        "detail": {
            "error_code": "SESSION_NOT_FOUND",
            "message": "Session not found.",
        }
    }


def test_execute_agent() -> None:
    runner = FakeRunner()
    runner.get_session.return_value = FakeSession(
        session_id="session-001",
        user_id="user-001",
    )

    event = {
        "id": "event-001",
        "content": {
            "text": "100",
        },
    }

    runner.run.return_value = [event]

    client = _client_with_runner(runner)

    response = client.post(
        "/sessions/session-001/messages",
        params={"user_id": "user-001"},
        json={"message": "What is 25 multiplied by 4?"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "user_id": "user-001",
        "session_id": "session-001",
        "events": [event],
    }

    runner.run.assert_awaited_once_with(
        user_id="user-001",
        session_id="session-001",
        message="What is 25 multiplied by 4?",
    )


def test_execute_agent_missing_session_returns_structured_404() -> None:
    runner = FakeRunner()
    runner.get_session.return_value = None

    client = _client_with_runner(runner)

    response = client.post(
        "/sessions/missing-session/messages",
        params={"user_id": "user-001"},
        json={"message": "Hello"},
    )

    assert response.status_code == 404
    assert response.json() == {
        "detail": {
            "error_code": "SESSION_NOT_FOUND",
            "message": "Session not found.",
        }
    }

    runner.run.assert_not_awaited()


def test_empty_message_returns_422() -> None:
    runner = FakeRunner()

    client = _client_with_runner(runner)

    response = client.post(
        "/sessions/session-001/messages",
        params={"user_id": "user-001"},
        json={"message": ""},
    )

    assert response.status_code == 422

    body = response.json()

    assert body["detail"][0]["type"] == "string_too_short"
    assert body["detail"][0]["loc"] == ["body", "message"]


def test_unknown_request_field_is_rejected() -> None:
    runner = FakeRunner()

    client = _client_with_runner(runner)

    response = client.post(
        "/sessions/session-001/messages",
        params={"user_id": "user-001"},
        json={
            "message": "Hello",
            "unexpected": "value",
        },
    )

    assert response.status_code == 422


def test_create_session_application_error_is_structured() -> None:
    from app.errors import AgentExecutionError

    runner = FakeRunner()
    runner.create_session.side_effect = AgentExecutionError(
        "Session creation failed.",
        details="RuntimeError",
    )

    client = _client_with_runner(runner)

    response = client.post(
        "/sessions",
        json={"user_id": "user-001"},
    )

    assert response.status_code == 500
    assert response.json() == {
        "detail": {
            "error_code": "AGENT_EXECUTION_ERROR",
            "message": "Session creation failed.",
        }
    }


def test_agent_execution_application_error_is_structured() -> None:
    from app.errors import AgentExecutionError

    runner = FakeRunner()
    runner.get_session.return_value = FakeSession(
        session_id="session-001",
        user_id="user-001",
    )
    runner.run.side_effect = AgentExecutionError(
        "Agent execution failed.",
        details="RuntimeError",
    )

    client = _client_with_runner(runner)

    response = client.post(
        "/sessions/session-001/messages",
        params={"user_id": "user-001"},
        json={"message": "Hello"},
    )

    assert response.status_code == 500
    assert response.json() == {
        "detail": {
            "error_code": "AGENT_EXECUTION_ERROR",
            "message": "Agent execution failed.",
        }
    }