from __future__ import annotations

from google.adk.agents import LlmAgent

from app.config import settings

from app.tools.function_tools import (
    calculate,
    get_current_datetime,
    get_system_status,
)

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


general_agent = LlmAgent(
    name="general_agent",
    model=f"ollama_chat/{settings.OLLAMA_MODEL}",
    description=(
        "Handles general questions and local utility operations "
        "such as calculations, system status, and current date/time."
    ),
    instruction="""
You are the general-purpose specialist agent for ADK-Ollama-AgentHub.

Handle:
- General questions.
- Mathematical calculations.
- System status requests.
- Current date/time requests.

Available tools:
- calculate
- get_system_status
- get_current_datetime

Use tools when they are appropriate.
Do not invent tool results.
If the request is outside your responsibility, return control
to the parent orchestration agent.
Do not expose credentials, secrets, stack traces,
or internal implementation details.
""",
    tools=[
        calculate,
        get_system_status,
        get_current_datetime,
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


__all__ = ["general_agent"]