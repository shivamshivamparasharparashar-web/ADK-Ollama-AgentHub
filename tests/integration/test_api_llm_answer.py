from __future__ import annotations

import uuid

import pytest
from fastapi.testclient import TestClient

from app.api.main import app


@pytest.mark.integration
def test_api_llm_answer(request) -> None:
    """
    Send a runtime question to the FastAPI/ADK LLM endpoint
    and verify that Qwen3 returns a non-empty answer.
    """

    question = request.config.getoption("--question")

    if not question:
        pytest.fail(
            'No question provided. Use: '
            'pytest -q tests/integration/test_api_llm_answer.py -s '
            '--question "What is law?"'
        )

    user_id = f"api-llm-test-{uuid.uuid4()}"

    with TestClient(app) as client:

        # ---------------------------------------------------------
        # 1. Create a session
        # ---------------------------------------------------------
        session_response = client.post(
            "/sessions",
            json={
                "user_id": user_id,
            },
        )

        assert session_response.status_code == 201, (
            "Session creation failed: "
            f"{session_response.status_code} - "
            f"{session_response.text}"
        )

        session_data = session_response.json()

        assert "session_id" in session_data, (
            "Session response does not contain session_id."
        )

        session_id = session_data["session_id"]

        # ---------------------------------------------------------
        # 2. Send runtime question
        # ---------------------------------------------------------
        response = client.post(
            f"/sessions/{session_id}/messages",
            params={
                "user_id": user_id,
            },
            json={
                "message": question,
            },
        )

        assert response.status_code == 200, (
            "LLM request failed: "
            f"{response.status_code} - "
            f"{response.text}"
        )

        data = response.json()

        # ---------------------------------------------------------
        # 3. Validate API response
        # ---------------------------------------------------------
        assert "events" in data, (
            "API response does not contain events."
        )

        events = data["events"]

        assert events, (
            "API returned an empty events list."
        )

        # ---------------------------------------------------------
        # 4. Find model response event
        # ---------------------------------------------------------
        model_events = [
            event
            for event in events
            if event.get("model_version")
            and event.get("content")
        ]

        assert model_events, (
            "No model response event was found."
        )

        # Use the latest model event because the request can
        # generate multiple ADK/model events.
        answer_event = model_events[-1]

        # ---------------------------------------------------------
        # 5. Validate model
        # ---------------------------------------------------------
        model = answer_event.get("model_version")

        assert model == "ollama_chat/qwen3:8b", (
            f"Unexpected model: {model}"
        )

        # ---------------------------------------------------------
        # 6. Extract final answer
        # ---------------------------------------------------------
        content = answer_event.get("content", {})

        parts = content.get("parts", [])

        assert parts, (
            "Model response contains no content parts."
        )

        # Ignore Qwen3 thought/reasoning parts.
        answer_parts = [
            part.get("text", "").strip()
            for part in parts
            if part.get("text")
            and not part.get("thought", False)
        ]

        assert answer_parts, (
            "No final answer text was found in the model response."
        )

        answer = "\n".join(answer_parts).strip()

        assert answer, (
            "LLM returned an empty answer."
        )

        # ---------------------------------------------------------
        # 7. Validate execution metrics
        # ---------------------------------------------------------
        actions = answer_event.get("actions", {})

        state_delta = actions.get(
            "state_delta",
            {},
        )

        metrics = state_delta.get(
            "_execution_metrics",
            {},
        )

        model_errors = metrics.get(
            "model_errors",
            0,
        )

        tool_errors = metrics.get(
            "tool_errors",
            0,
        )

        assert model_errors == 0, (
            f"Model errors detected: {model_errors}"
        )

        assert tool_errors == 0, (
            f"Tool errors detected: {tool_errors}"
        )

        # ---------------------------------------------------------
        # 8. Display result
        # ---------------------------------------------------------
        print("\n" + "=" * 70)
        print("API LLM ANSWER TEST")
        print("=" * 70)

        print("\nQuestion:")
        print(question)

        print("\nModel:")
        print(model)

        print("\nAuthor:")
        print(answer_event.get("author"))

        print("\nAnswer:")
        print(answer)

        print("\nModel errors:")
        print(model_errors)

        print("\nTool errors:")
        print(tool_errors)

        print("\n" + "=" * 70)