from __future__ import annotations

import json
from typing import Any

from google.adk.agents.callback_context import CallbackContext
from google.adk.models.llm_request import LlmRequest
from google.adk.models.llm_response import LlmResponse
from google.adk.tools.base_tool import BaseTool
from google.genai import types


# ---------------------------------------------------------------------------
# Guardrail limits
# ---------------------------------------------------------------------------

MAX_INPUT_LENGTH = 10_000
MAX_TOOL_ARGUMENT_LENGTH = 5_000
MAX_OUTPUT_LENGTH = 20_000


# ---------------------------------------------------------------------------
# Blocked input patterns
# ---------------------------------------------------------------------------

BLOCKED_INPUT_PATTERNS = (
    "\x00",
)


# ---------------------------------------------------------------------------
# Content helper
# ---------------------------------------------------------------------------

def _content(message: str) -> types.Content:
    """
    Create an ADK model Content response.

    Returning Content from before_agent_callback causes ADK to
    short-circuit the agent invocation.
    """
    return types.Content(
        role="model",
        parts=[
            types.Part(text=message),
        ],
    )


# ---------------------------------------------------------------------------
# Input validation
# ---------------------------------------------------------------------------

def validate_input(text: Any) -> tuple[bool, str | None]:
    """
    Validate user input.

    Returns:
        (True, None) when valid.
        (False, reason) when invalid.
    """

    if text is None:
        return False, "No user input was provided."

    if not isinstance(text, str):
        return False, "User input must be text."

    if not text.strip():
        return False, "User input cannot be empty or whitespace only."

    if len(text) > MAX_INPUT_LENGTH:
        return (
            False,
            f"User input exceeds the maximum allowed length "
            f"of {MAX_INPUT_LENGTH} characters.",
        )

    for pattern in BLOCKED_INPUT_PATTERNS:
        if pattern in text:
            return False, "User input contains a blocked control character."

    return True, None


# ---------------------------------------------------------------------------
# Tool argument validation
# ---------------------------------------------------------------------------

def validate_tool_arguments(
    tool_name: str,
    args: dict[str, Any],
) -> tuple[bool, str | None]:
    """
    Validate tool arguments.

    Includes generic argument validation and tool-specific validation
    for the calculate tool.
    """

    if not isinstance(args, dict):
        return False, "Tool arguments must be a dictionary."

    # ---------------------------------------------------------------
    # calculate tool validation
    # ---------------------------------------------------------------

    if tool_name == "calculate":
        if "expression" not in args:
            return (
                False,
                "The 'expression' argument is required for the "
                "calculate tool.",
            )

        expression = args["expression"]

        if not isinstance(expression, str):
            return (
                False,
                "The 'expression' argument must be a string.",
            )

        if not expression.strip():
            return (
                False,
                "The 'expression' argument cannot be empty.",
            )

    # ---------------------------------------------------------------
    # Generic serialization / size validation
    # ---------------------------------------------------------------

    try:
        serialized = json.dumps(
            args,
            ensure_ascii=False,
            default=str,
        )
    except (TypeError, ValueError) as exc:
        return (
            False,
            f"Tool arguments could not be serialized: {exc}",
        )

    if len(serialized) > MAX_TOOL_ARGUMENT_LENGTH:
        return (
            False,
            f"Arguments for tool '{tool_name}' exceed the maximum "
            f"allowed size of {MAX_TOOL_ARGUMENT_LENGTH} characters.",
        )

    return True, None


# ---------------------------------------------------------------------------
# Model output validation
# ---------------------------------------------------------------------------

def validate_output(text: Any) -> tuple[bool, str | None]:
    """
    Validate model-generated output.
    """

    if text is None:
        return True, None

    if not isinstance(text, str):
        return False, "Model output must be text."

    if len(text) > MAX_OUTPUT_LENGTH:
        return (
            False,
            f"Model output exceeds the maximum allowed length "
            f"of {MAX_OUTPUT_LENGTH} characters.",
        )

    for pattern in BLOCKED_INPUT_PATTERNS:
        if pattern in text:
            return False, "Model output contains a blocked control character."

    return True, None


# ---------------------------------------------------------------------------
# Current user input extraction
# ---------------------------------------------------------------------------

def _extract_user_text(
    callback_context: CallbackContext,
) -> str | None:
    """
    Extract the current user request from the ADK callback context.

    This intentionally uses user_content instead of session.events.
    """

    try:
        user_content = callback_context.user_content
    except AttributeError:
        return None

    if user_content is None:
        return None

    parts = getattr(user_content, "parts", None)

    if not parts:
        return None

    text_parts: list[str] = []

    for part in parts:
        text = getattr(part, "text", None)

        if isinstance(text, str):
            text_parts.append(text)

    if not text_parts:
        return None

    return "".join(text_parts)


# ---------------------------------------------------------------------------
# Before-agent guardrail
# ---------------------------------------------------------------------------

def guardrail_before_agent(
    callback_context: CallbackContext,
) -> types.Content | None:
    """
    Validate user input before the agent executes.

    Returning Content blocks the invocation.
    """

    user_text = _extract_user_text(callback_context)

    valid, reason = validate_input(user_text)

    if valid:
        return None

    return _content(
        f"Request blocked by input guardrail: {reason}"
    )


# ---------------------------------------------------------------------------
# Before-tool guardrail
# ---------------------------------------------------------------------------

def guardrail_before_tool(
    tool: BaseTool,
    args: dict[str, Any],
    tool_context: CallbackContext,
) -> dict[str, Any] | None:
    """
    Validate tool arguments before execution.
    """

    tool_name = (
        getattr(tool, "name", None)
        or tool.__class__.__name__
    )

    valid, reason = validate_tool_arguments(
        tool_name,
        args,
    )

    if valid:
        return None

    return {
        "status": "blocked",
        "error": "Tool execution blocked by guardrail.",
        "tool": tool_name,
        "reason": reason,
    }


# ---------------------------------------------------------------------------
# After-tool guardrail
# ---------------------------------------------------------------------------

def guardrail_after_tool(
    tool: BaseTool,
    args: dict[str, Any],
    tool_context: CallbackContext,
    tool_response: dict[str, Any],
) -> dict[str, Any] | None:
    """
    Validate the tool response structure and size.
    """

    tool_name = (
        getattr(tool, "name", None)
        or tool.__class__.__name__
    )

    if not isinstance(tool_response, dict):
        return {
            "status": "error",
            "error": "Tool returned an invalid response.",
            "tool": tool_name,
        }

    try:
        serialized = json.dumps(
            tool_response,
            ensure_ascii=False,
            default=str,
        )
    except (TypeError, ValueError):
        return {
            "status": "error",
            "error": (
                "Tool returned a response that could not "
                "be serialized."
            ),
            "tool": tool_name,
        }

    if len(serialized) > MAX_OUTPUT_LENGTH:
        return {
            "status": "error",
            "error": (
                f"Tool '{tool_name}' returned data exceeding "
                f"the maximum allowed output size."
            ),
            "tool": tool_name,
        }

    return None


# ---------------------------------------------------------------------------
# After-model guardrail
# ---------------------------------------------------------------------------

def guardrail_after_model(
    callback_context: CallbackContext,
    llm_response: LlmResponse,
) -> LlmResponse | None:
    """
    Validate model output after an LLM call.

    Returning None allows normal execution to continue.
    """

    if llm_response is None:
        return None

    response_content = getattr(
        llm_response,
        "content",
        None,
    )

    if response_content is None:
        return None

    parts = getattr(
        response_content,
        "parts",
        None,
    )

    if not parts:
        return None

    text_parts: list[str] = []

    for part in parts:
        text = getattr(part, "text", None)

        if isinstance(text, str):
            text_parts.append(text)

    if not text_parts:
        return None

    output_text = "".join(text_parts)

    valid, reason = validate_output(output_text)

    if valid:
        return None

    return LlmResponse(
        content=_content(
            f"Response blocked by output guardrail: {reason}"
        ),
    )


# ---------------------------------------------------------------------------
# Optional model callbacks
# ---------------------------------------------------------------------------

def guardrail_before_model(
    callback_context: CallbackContext,
    llm_request: LlmRequest,
) -> LlmResponse | None:
    """
    Reserved for future model-request validation.
    """
    return None


def guardrail_on_model_error(
    callback_context: CallbackContext,
    llm_request: LlmRequest,
    error: Exception,
) -> LlmResponse | None:
    """
    Preserve ADK's standard model-error handling.
    """
    return None


def guardrail_on_tool_error(
    tool: BaseTool,
    args: dict[str, Any],
    tool_context: CallbackContext,
    error: Exception,
) -> dict[str, Any] | None:
    """
    Preserve ADK's standard tool-error handling.
    """
    return None


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

__all__ = [
    "MAX_INPUT_LENGTH",
    "MAX_TOOL_ARGUMENT_LENGTH",
    "MAX_OUTPUT_LENGTH",
    "validate_input",
    "validate_tool_arguments",
    "validate_output",
    "guardrail_before_agent",
    "guardrail_before_model",
    "guardrail_after_model",
    "guardrail_on_model_error",
    "guardrail_before_tool",
    "guardrail_after_tool",
    "guardrail_on_tool_error",
]