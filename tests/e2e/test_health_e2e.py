from fastapi.testclient import TestClient

from app.api.main import app


def test_health_e2e():
    with TestClient(app) as client:
        response = client.get("/health")

    assert response.status_code == 200

    payload = response.json()

    assert payload["status"] == "healthy"
    assert payload["app_name"]