import time

from app.callbacks.metrics import (
    METRICS_KEY,
    add_duration,
    add_tool_duration,
    get_metrics,
    increment_metric,
    increment_tool_metric,
    start_timer,
    stop_timer,
)


class FakeContext:
    def __init__(self):
        self.state = {}


# ============================================================================
# Timer tests
# ============================================================================


def test_start_timer_stores_timer():
    context = FakeContext()

    start_timer(
        context,
        "test_timer",
    )

    assert "test_timer" in context.state
    assert isinstance(
        context.state["test_timer"],
        float,
    )


def test_stop_timer_returns_duration():
    context = FakeContext()

    start_timer(
        context,
        "test_timer",
    )

    time.sleep(0.01)

    duration = stop_timer(
        context,
        "test_timer",
    )

    assert duration is not None
    assert duration >= 0.01


def test_stop_timer_clears_timer():
    context = FakeContext()

    start_timer(
        context,
        "test_timer",
    )

    duration = stop_timer(
        context,
        "test_timer",
    )

    assert duration is not None
    assert context.state["test_timer"] is None


def test_stop_timer_without_start_returns_none():
    context = FakeContext()

    duration = stop_timer(
        context,
        "missing_timer",
    )

    assert duration is None


def test_multiple_timers_are_independent():
    context = FakeContext()

    start_timer(
        context,
        "timer_one",
    )

    start_timer(
        context,
        "timer_two",
    )

    duration_one = stop_timer(
        context,
        "timer_one",
    )

    duration_two = stop_timer(
        context,
        "timer_two",
    )

    assert duration_one is not None
    assert duration_two is not None

    assert context.state["timer_one"] is None
    assert context.state["timer_two"] is None


# ============================================================================
# Metrics initialization
# ============================================================================


def test_get_metrics_returns_defaults():
    context = FakeContext()

    metrics = get_metrics(context)

    assert metrics["agent_executions"] == 0
    assert metrics["agent_total_duration"] == 0.0

    assert metrics["model_calls"] == 0
    assert metrics["model_errors"] == 0
    assert metrics["model_total_duration"] == 0.0

    assert metrics["tool_calls"] == 0
    assert metrics["tool_successes"] == 0
    assert metrics["tool_errors"] == 0
    assert metrics["tool_total_duration"] == 0.0

    assert metrics["tools"] == {}


# ============================================================================
# Generic metric tests
# ============================================================================


def test_increment_metric():
    context = FakeContext()

    value = increment_metric(
        context,
        "model_calls",
    )

    assert value == 1

    metrics = get_metrics(context)

    assert metrics["model_calls"] == 1


def test_increment_metric_multiple_times():
    context = FakeContext()

    increment_metric(
        context,
        "model_calls",
    )

    increment_metric(
        context,
        "model_calls",
    )

    increment_metric(
        context,
        "model_calls",
    )

    metrics = get_metrics(context)

    assert metrics["model_calls"] == 3


def test_increment_metric_custom_amount():
    context = FakeContext()

    value = increment_metric(
        context,
        "model_calls",
        amount=5,
    )

    assert value == 5

    metrics = get_metrics(context)

    assert metrics["model_calls"] == 5


# ============================================================================
# Duration metric tests
# ============================================================================


def test_add_duration():
    context = FakeContext()

    total = add_duration(
        context,
        "model_total_duration",
        1.5,
    )

    assert total == 1.5

    metrics = get_metrics(context)

    assert metrics["model_total_duration"] == 1.5


def test_add_duration_accumulates():
    context = FakeContext()

    add_duration(
        context,
        "model_total_duration",
        1.5,
    )

    add_duration(
        context,
        "model_total_duration",
        2.5,
    )

    metrics = get_metrics(context)

    assert metrics["model_total_duration"] == 4.0


def test_add_duration_none_does_not_change_metric():
    context = FakeContext()

    add_duration(
        context,
        "model_total_duration",
        1.0,
    )

    total = add_duration(
        context,
        "model_total_duration",
        None,
    )

    assert total == 1.0


# ============================================================================
# Tool metrics
# ============================================================================


def test_increment_tool_metric():
    context = FakeContext()

    value = increment_tool_metric(
        context,
        "calculate",
        "calls",
    )

    assert value == 1

    metrics = get_metrics(context)

    assert metrics["tools"]["calculate"]["calls"] == 1


def test_increment_tool_metric_multiple_times():
    context = FakeContext()

    increment_tool_metric(
        context,
        "calculate",
        "calls",
    )

    increment_tool_metric(
        context,
        "calculate",
        "calls",
    )

    increment_tool_metric(
        context,
        "calculate",
        "calls",
    )

    metrics = get_metrics(context)

    assert metrics["tools"]["calculate"]["calls"] == 3


def test_different_tools_are_independent():
    context = FakeContext()

    increment_tool_metric(
        context,
        "calculate",
        "calls",
    )

    increment_tool_metric(
        context,
        "get_system_status",
        "calls",
    )

    metrics = get_metrics(context)

    assert metrics["tools"]["calculate"]["calls"] == 1
    assert metrics["tools"]["get_system_status"]["calls"] == 1


def test_add_tool_duration():
    context = FakeContext()

    total = add_tool_duration(
        context,
        "calculate",
        1.25,
    )

    assert total == 1.25

    metrics = get_metrics(context)

    assert (
        metrics["tools"]["calculate"]["total_duration"]
        == 1.25
    )


def test_add_tool_duration_accumulates():
    context = FakeContext()

    add_tool_duration(
        context,
        "calculate",
        1.25,
    )

    add_tool_duration(
        context,
        "calculate",
        2.75,
    )

    metrics = get_metrics(context)

    assert (
        metrics["tools"]["calculate"]["total_duration"]
        == 4.0
    )


def test_add_tool_duration_none():
    context = FakeContext()

    add_tool_duration(
        context,
        "calculate",
        1.0,
    )

    total = add_tool_duration(
        context,
        "calculate",
        None,
    )

    assert total == 1.0


# ============================================================================
# State persistence
# ============================================================================


def test_metrics_are_stored_in_state():
    context = FakeContext()

    increment_metric(
        context,
        "agent_executions",
    )

    assert METRICS_KEY in context.state

    assert (
        context.state[METRICS_KEY]["agent_executions"]
        == 1
    )


def test_get_metrics_returns_copy():
    context = FakeContext()

    increment_metric(
        context,
        "model_calls",
    )

    metrics = get_metrics(context)

    metrics["model_calls"] = 999

    stored_metrics = get_metrics(context)

    assert stored_metrics["model_calls"] == 1