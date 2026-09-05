from uuid import uuid4

from fastapi.testclient import TestClient

from app.api.main import app


def test_session_lifecycle_e2e():
    user_id = f"e2e-user-{uuid4().hex}"
    session_id = f"e2e-session-{uuid4().hex}"

    with TestClient(app) as client:
        # Create session
        create_response = client.post(
            "/sessions",
            json={
                "user_id": user_id,
                "session_id": session_id,
            },
        )

        assert create_response.status_code == 201

        created = create_response.json()

        assert created["user_id"] == user_id
        assert created["session_id"] == session_id
        assert "app_name" in created
        assert "state" in created

        # Retrieve session
        get_response = client.get(
            f"/sessions/{session_id}",
            params={
                "user_id": user_id,
            },
        )

        assert get_response.status_code == 200

        retrieved = get_response.json()

        assert retrieved["user_id"] == user_id
        assert retrieved["session_id"] == session_id
        assert retrieved["app_name"] == created["app_name"]
        assert retrieved["state"] == created["state"]