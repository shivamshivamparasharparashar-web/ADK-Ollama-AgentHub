import logging
from unittest.mock import Mock

import pytest

from app.callbacks.logging_callbacks import (
    after_agent_callback,
    after_model_callback,
    after_tool_callback,
    before_agent_callback,
    before_model_callback,
    before_tool_callback,
    on_model_error_callback,
    on_tool_error_callback,
)
from app.callbacks.metrics import get_metrics


@pytest.fixture
def callback_context():
    context = Mock()
    context.state = {}
    return context


@pytest.fixture
def tool():
    mock_tool = Mock()
    mock_tool.name = "calculate"
    return mock_tool


# ============================================================================
# Agent callbacks
# ============================================================================


def test_before_agent_callback_logs(
    caplog,
    callback_context,
):
    with caplog.at_level(logging.INFO):
        result = before_agent_callback(
            callback_context=callback_context,
        )

    assert result is None
    assert "Agent execution started" in caplog.text

    assert "_agent_start_time" in callback_context.state

    metrics = get_metrics(callback_context)

    assert metrics["agent_executions"] == 1


def test_after_agent_callback_logs(
    caplog,
    callback_context,
):
    before_agent_callback(
        callback_context=callback_context,
    )

    with caplog.at_level(logging.INFO):
        result = after_agent_callback(
            callback_context=callback_context,
        )

    assert result is None
    assert "Agent execution completed" in caplog.text

    assert callback_context.state["_agent_start_time"] is None

    metrics = get_metrics(callback_context)

    assert metrics["agent_executions"] == 1
    assert metrics["agent_total_duration"] >= 0.0


# ============================================================================
# Model callbacks
# ============================================================================


def test_before_model_callback_logs(
    caplog,
    callback_context,
):
    with caplog.at_level(logging.INFO):
        result = before_model_callback(
            callback_context=callback_context,
            llm_request=Mock(),
        )

    assert result is None
    assert "Model execution started" in caplog.text

    assert "_model_start_time" in callback_context.state

    metrics = get_metrics(callback_context)

    assert metrics["model_calls"] == 1


def test_after_model_callback_logs(
    caplog,
    callback_context,
):
    before_model_callback(
        callback_context=callback_context,
        llm_request=Mock(),
    )

    with caplog.at_level(logging.INFO):
        result = after_model_callback(
            callback_context=callback_context,
            llm_response=Mock(),
        )

    assert result is None
    assert "Model execution completed" in caplog.text

    assert callback_context.state["_model_start_time"] is None

    metrics = get_metrics(callback_context)

    assert metrics["model_calls"] == 1
    assert metrics["model_errors"] == 0
    assert metrics["model_total_duration"] >= 0.0


def test_model_error_callback_logs(
    caplog,
    callback_context,
):
    before_model_callback(
        callback_context=callback_context,
        llm_request=Mock(),
    )

    error = RuntimeError(
        "model failure"
    )

    with caplog.at_level(logging.ERROR):
        result = on_model_error_callback(
            callback_context=callback_context,
            llm_request=Mock(),
            error=error,
        )

    assert result is None
    assert "Model execution failed" in caplog.text
    assert "error_type=RuntimeError" in caplog.text
    assert "model failure" not in caplog.text

    assert callback_context.state["_model_start_time"] is None

    metrics = get_metrics(callback_context)

    assert metrics["model_calls"] == 1
    assert metrics["model_errors"] == 1
    assert metrics["model_total_duration"] >= 0.0


# ============================================================================
# Tool callbacks
# ============================================================================


def test_before_tool_callback_logs(
    caplog,
    callback_context,
    tool,
):
    with caplog.at_level(logging.INFO):
        result = before_tool_callback(
            tool=tool,
            args={},
            tool_context=callback_context,
        )

    assert result is None
    assert "Tool execution started" in caplog.text
    assert "calculate" in caplog.text

    timer_key = "_tool_start_time_calculate"

    assert timer_key in callback_context.state

    metrics = get_metrics(callback_context)

    assert metrics["tool_calls"] == 1
    assert metrics["tools"]["calculate"]["calls"] == 1


def test_after_tool_callback_logs(
    caplog,
    callback_context,
    tool,
):
    before_tool_callback(
        tool=tool,
        args={},
        tool_context=callback_context,
    )

    with caplog.at_level(logging.INFO):
        result = after_tool_callback(
            tool=tool,
            args={},
            tool_context=callback_context,
            tool_response={
                "status": "success",
                "result": 10,
            },
        )

    assert result is None
    assert "Tool execution completed" in caplog.text
    assert "calculate" in caplog.text

    timer_key = "_tool_start_time_calculate"

    assert callback_context.state[timer_key] is None

    metrics = get_metrics(callback_context)

    assert metrics["tool_calls"] == 1
    assert metrics["tool_successes"] == 1
    assert metrics["tool_errors"] == 0

    assert metrics["tools"]["calculate"]["calls"] == 1
    assert metrics["tools"]["calculate"]["successes"] == 1
    assert metrics["tools"]["calculate"]["errors"] == 0
    assert (
        metrics["tools"]["calculate"]["total_duration"]
        >= 0.0
    )


def test_tool_error_callback_logs(
    caplog,
    callback_context,
    tool,
):
    before_tool_callback(
        tool=tool,
        args={},
        tool_context=callback_context,
    )

    error = RuntimeError(
        "tool failure"
    )

    with caplog.at_level(logging.ERROR):
        result = on_tool_error_callback(
            tool=tool,
            args={},
            tool_context=callback_context,
            error=error,
        )

    assert result is None
    assert "Tool execution failed" in caplog.text
    assert "calculate" in caplog.text
    assert "error_type=RuntimeError" in caplog.text
    assert "tool failure" not in caplog.text

    timer_key = "_tool_start_time_calculate"

    assert callback_context.state[timer_key] is None

    metrics = get_metrics(callback_context)

    assert metrics["tool_calls"] == 1
    assert metrics["tool_successes"] == 0
    assert metrics["tool_errors"] == 1

    assert metrics["tools"]["calculate"]["calls"] == 1
    assert metrics["tools"]["calculate"]["successes"] == 0
    assert metrics["tools"]["calculate"]["errors"] == 1
    assert (
        metrics["tools"]["calculate"]["total_duration"]
        >= 0.0
    )


# ============================================================================
# Missing timer behavior
# ============================================================================


def test_after_agent_callback_without_timer_still_logs(
    caplog,
    callback_context,
):
    with caplog.at_level(logging.INFO):
        result = after_agent_callback(
            callback_context=callback_context,
        )

    assert result is None
    assert "Agent execution completed" in caplog.text


def test_after_model_callback_without_timer_still_logs(
    caplog,
    callback_context,
):
    with caplog.at_level(logging.INFO):
        result = after_model_callback(
            callback_context=callback_context,
            llm_response=Mock(),
        )

    assert result is None
    assert "Model execution completed" in caplog.text


def test_after_tool_callback_without_timer_still_logs(
    caplog,
    callback_context,
    tool,
):
    with caplog.at_level(logging.INFO):
        result = after_tool_callback(
            tool=tool,
            args={},
            tool_context=callback_context,
            tool_response={
                "status": "success",
            },
        )

    assert result is None
    assert "Tool execution completed" in caplog.text
    assert "calculate" in caplog.text


def test_tool_error_callback_without_timer_still_logs(
    caplog,
    callback_context,
    tool,
):
    error = RuntimeError(
        "tool failure"
    )

    with caplog.at_level(logging.ERROR):
        result = on_tool_error_callback(
            tool=tool,
            args={},
            tool_context=callback_context,
            error=error,
        )

    assert result is None
    assert "Tool execution failed" in caplog.text
    assert "calculate" in caplog.text
    assert "error_type=RuntimeError" in caplog.text
    assert "tool failure" not in caplog.text