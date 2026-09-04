from __future__ import annotations

from google.adk.agents import LlmAgent

from app.config import settings

from app.tools.api_tools import api_request

from app.callbacks.logging_callbacks import (
    before_agent_callback,
    after_agent_callback,
    before_model_callback,
    after_model_callback,
    on_model_error_callback,
    before_tool_callback,
    after_tool_callback,
    on_tool_error_callback,
)

from app.callbacks.guardrails import (
    guardrail_before_agent,
    guardrail_after_model,
    guardrail_before_tool,
    guardrail_after_tool,
)


api_agent = LlmAgent(
    name="api_agent",
    model=f"ollama_chat/{settings.OLLAMA_MODEL}",
    description=(
        "Handles external HTTP API operations using the "
        "application's bounded API request tool."
    ),
    instruction="""
You are the API specialist agent for ADK-Ollama-AgentHub.

Your responsibility is HTTP/API operations.

Available tool:
- api_request

Use api_request when the user request requires an HTTP API operation.

Do not invent API responses.
Only report information actually returned by the API tool.
If the request is outside API operations, return control
to the parent orchestration agent.
Do not expose credentials, secrets, stack traces,
or internal implementation details.
""",
    tools=[
        api_request,
    ],
    disallow_transfer_to_parent=False,
    disallow_transfer_to_peers=True,
    before_agent_callback=[
        guardrail_before_agent,
        before_agent_callback,
    ],
    after_agent_callback=[
        after_agent_callback,
    ],
    before_model_callback=[
        before_model_callback,
    ],
    after_model_callback=[
        after_model_callback,
        guardrail_after_model,
    ],
    on_model_error_callback=[
        on_model_error_callback,
    ],
    before_tool_callback=[
        guardrail_before_tool,
        before_tool_callback,
    ],
    after_tool_callback=[
        after_tool_callback,
        guardrail_after_tool,
    ],
    on_tool_error_callback=[
        on_tool_error_callback,
    ],
)


__all__ = ["api_agent"]