from __future__ import annotations

import pytest

from app.errors import AgentExecutionError
from app.services.agent_runner import AgentRunner


class FailingRunner:
    async def run_async(self, **kwargs):
        raise RuntimeError("internal provider detail")

        yield  # pragma: no cover


@pytest.mark.anyio
async def test_agent_runner_normalizes_execution_errors():
    runner = object.__new__(AgentRunner)
    runner.runner = FailingRunner()

    with pytest.raises(AgentExecutionError) as exc_info:
        await runner.run(
            user_id="error-user",
            session_id="error-session",
            message="hello",
        )

    assert str(exc_info.value) == "Agent execution failed."
    assert exc_info.value.details == "RuntimeError"
    assert "internal provider detail" not in str(exc_info.value)