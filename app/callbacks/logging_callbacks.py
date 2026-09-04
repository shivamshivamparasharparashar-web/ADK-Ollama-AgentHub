from __future__ import annotations

from typing import Any

from google.adk.agents.callback_context import Context
from google.adk.models.llm_response import LlmResponse
from google.adk.models.llm_request import LlmRequest
from google.adk.tools.base_tool import BaseTool

from app.callbacks.metrics import (
    add_duration,
    add_tool_duration,
    increment_metric,
    increment_tool_metric,
    start_timer,
    stop_timer,
)
from app.utils.logger import logger


def _agent_name(callback_context: Context) -> str:
    """Return the agent name without relying on Context.agent."""
    agent = getattr(callback_context, "agent", None)

    if agent is not None:
        name = getattr(agent, "name", None)
        if name:
            return str(name)

    return "unknown"


def before_agent_callback(callback_context: Context) -> None:
    start_timer(callback_context, "_agent_start_time")
    increment_metric(callback_context, "agent_executions")

    logger.info(
        "Agent execution started agent=%s",
        _agent_name(callback_context),
    )


def after_agent_callback(callback_context: Context) -> None:
    duration = stop_timer(callback_context, "_agent_start_time")

    if duration is not None:
        add_duration(
            callback_context,
            "agent_total_duration",
            duration,
        )

    logger.info(
        "Agent execution completed agent=%s duration=%.4fs",
        _agent_name(callback_context),
        duration or 0.0,
    )


def before_model_callback(
    callback_context: Context,
    llm_request: LlmRequest,
) -> None:
    start_timer(callback_context, "_model_start_time")
    increment_metric(callback_context, "model_calls")

    logger.info(
        "Model execution started agent=%s",
        _agent_name(callback_context),
    )


def after_model_callback(
    callback_context: Context,
    llm_response: LlmResponse,
) -> None:
    duration = stop_timer(
        callback_context,
        "_model_start_time",
    )

    if duration is not None:
        add_duration(
            callback_context,
            "model_total_duration",
            duration,
        )

    logger.info(
        "Model execution completed agent=%s duration=%.4fs",
        _agent_name(callback_context),
        duration or 0.0,
    )


def on_model_error_callback(
    callback_context: Context,
    llm_request: LlmRequest,
    error: Exception,
) -> None:
    duration = stop_timer(
        callback_context,
        "_model_start_time",
    )

    increment_metric(
        callback_context,
        "model_errors",
    )

    if duration is not None:
        add_duration(
            callback_context,
            "model_total_duration",
            duration,
        )

    logger.error(
        "Model execution failed agent=%s duration=%.4fs error_type=%s",
        _agent_name(callback_context),
        duration or 0.0,
        type(error).__name__,
        exc_info=True,
    )


def before_tool_callback(
    tool: BaseTool,
    args: dict[str, Any],
    tool_context: Context,
) -> None:
    tool_name = tool.name
    timer_key = f"_tool_start_time_{tool_name}"

    start_timer(
        tool_context,
        timer_key,
    )

    increment_metric(
        tool_context,
        "tool_calls",
    )

    increment_tool_metric(
        tool_context,
        tool_name,
        "calls",
    )

    logger.info(
        "Tool execution started tool=%s",
        tool_name,
    )


def after_tool_callback(
    tool: BaseTool,
    args: dict[str, Any],
    tool_context: Context,
    tool_response: dict[str, Any],
) -> None:
    tool_name = tool.name
    timer_key = f"_tool_start_time_{tool_name}"

    duration = stop_timer(
        tool_context,
        timer_key,
    )

    increment_metric(
        tool_context,
        "tool_successes",
    )

    increment_tool_metric(
        tool_context,
        tool_name,
        "successes",
    )

    if duration is not None:
        add_duration(
            tool_context,
            "tool_total_duration",
            duration,
        )

        add_tool_duration(
            tool_context,
            tool_name,
            duration,
        )

    logger.info(
        "Tool execution completed tool=%s duration=%.4fs",
        tool_name,
        duration or 0.0,
    )


def on_tool_error_callback(
    tool: BaseTool,
    args: dict[str, Any],
    tool_context: Context,
    error: Exception,
) -> None:
    tool_name = tool.name
    timer_key = f"_tool_start_time_{tool_name}"

    duration = stop_timer(
        tool_context,
        timer_key,
    )

    increment_metric(
        tool_context,
        "tool_errors",
    )

    increment_tool_metric(
        tool_context,
        tool_name,
        "errors",
    )

    if duration is not None:
        add_duration(
            tool_context,
            "tool_total_duration",
            duration,
        )

        add_tool_duration(
            tool_context,
            tool_name,
            duration,
        )

    logger.error(
        "Tool execution failed tool=%s duration=%.4fs error_type=%s",
        tool_name,
        duration or 0.0,
        type(error).__name__,
        exc_info=True,
    )


__all__ = [
    "before_agent_callback",
    "after_agent_callback",
    "before_model_callback",
    "after_model_callback",
    "on_model_error_callback",
    "before_tool_callback",
    "after_tool_callback",
    "on_tool_error_callback",
]