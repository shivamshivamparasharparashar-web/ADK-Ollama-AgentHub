from uuid import uuid4

from fastapi.testclient import TestClient

from app.api.main import app


def test_agent_execution_e2e():
    user_id = f"e2e-agent-user-{uuid4().hex}"
    session_id = f"e2e-agent-session-{uuid4().hex}"

    with TestClient(app) as client:
        # Create session required for agent execution
        create_response = client.post(
            "/sessions",
            json={
                "user_id": user_id,
                "session_id": session_id,
            },
        )

        assert create_response.status_code == 201

        # Execute agent through the real API
        response = client.post(
            f"/sessions/{session_id}/messages",
            params={
                "user_id": user_id,
            },
            json={
                "message": "What is 25 multiplied by 4?",
            },
        )

        assert response.status_code == 200

        payload = response.json()

        assert payload["user_id"] == user_id
        assert payload["session_id"] == session_id
        assert isinstance(payload["events"], list)
        assert payload["events"]