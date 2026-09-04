import time
from typing import Any


# ============================================================================
# Timer helpers
# ============================================================================


def _get_state(context: Any):
    """Return the state object from an ADK callback context."""
    return context.state


def start_timer(context: Any, key: str) -> None:
    """
    Start a high-resolution timer.

    The timer value is stored in ADK state.
    """
    state = _get_state(context)
    state[key] = time.perf_counter()


def stop_timer(context: Any, key: str) -> float | None:
    """
    Stop a previously started timer.

    Returns:
        Elapsed time in seconds, or None if the timer does not exist.
    """
    state = _get_state(context)

    started = state.get(key)

    if started is None:
        return None

    duration = time.perf_counter() - started

    # ADK State does not provide dict.pop().
    state[key] = None

    return duration


# ============================================================================
# Metrics helpers
# ============================================================================


METRICS_KEY = "_execution_metrics"


def _default_metrics() -> dict[str, Any]:
    """
    Return a new metrics dictionary.

    A new dictionary is returned every time so callers do not
    accidentally share mutable state.
    """
    return {
        "agent_executions": 0,
        "agent_total_duration": 0.0,

        "model_calls": 0,
        "model_errors": 0,
        "model_total_duration": 0.0,

        "tool_calls": 0,
        "tool_successes": 0,
        "tool_errors": 0,
        "tool_total_duration": 0.0,

        "tools": {},
    }


def get_metrics(context: Any) -> dict[str, Any]:
    """
    Return the current execution metrics.

    The returned dictionary is a copy so callers cannot accidentally
    mutate ADK state without going through set_metrics().
    """
    state = _get_state(context)

    current = state.get(METRICS_KEY)

    if not isinstance(current, dict):
        return _default_metrics()

    metrics = _default_metrics()

    for key, value in current.items():
        if key == "tools":
            if isinstance(value, dict):
                metrics["tools"] = {
                    tool_name: dict(tool_metrics)
                    for tool_name, tool_metrics in value.items()
                    if isinstance(tool_metrics, dict)
                }
        else:
            metrics[key] = value

    return metrics


def set_metrics(
    context: Any,
    metrics: dict[str, Any],
) -> None:
    """
    Store execution metrics in ADK state.

    A copied dictionary is assigned to state so that ADK receives
    the state update explicitly.
    """
    state = _get_state(context)

    state[METRICS_KEY] = {
        key: (
            {
                tool_name: dict(tool_metrics)
                for tool_name, tool_metrics in value.items()
            }
            if key == "tools" and isinstance(value, dict)
            else value
        )
        for key, value in metrics.items()
    }


# ============================================================================
# Generic counter
# ============================================================================


def increment_metric(
    context: Any,
    metric_name: str,
    amount: int = 1,
) -> int:
    """
    Increment a top-level numeric metric.

    Returns:
        The new metric value.
    """
    metrics = get_metrics(context)

    current_value = metrics.get(metric_name, 0)

    if not isinstance(current_value, (int, float)):
        current_value = 0

    new_value = current_value + amount

    metrics[metric_name] = new_value

    set_metrics(
        context,
        metrics,
    )

    return new_value


# ============================================================================
# Duration metrics
# ============================================================================


def add_duration(
    context: Any,
    metric_name: str,
    duration: float | None,
) -> float:
    """
    Add an execution duration to a cumulative metric.

    Returns:
        New cumulative duration.
    """
    if duration is None:
        return float(
            get_metrics(context).get(
                metric_name,
                0.0,
            )
        )

    metrics = get_metrics(context)

    current_value = metrics.get(
        metric_name,
        0.0,
    )

    if not isinstance(current_value, (int, float)):
        current_value = 0.0

    new_value = float(current_value) + duration

    metrics[metric_name] = new_value

    set_metrics(
        context,
        metrics,
    )

    return new_value


# ============================================================================
# Tool-specific metrics
# ============================================================================


def _get_tool_metrics(
    metrics: dict[str, Any],
    tool_name: str,
) -> dict[str, Any]:
    """
    Return metrics for a specific tool.
    """
    tools = metrics.get("tools")

    if not isinstance(tools, dict):
        tools = {}
        metrics["tools"] = tools

    tool_metrics = tools.get(tool_name)

    if not isinstance(tool_metrics, dict):
        tool_metrics = {
            "calls": 0,
            "successes": 0,
            "errors": 0,
            "total_duration": 0.0,
        }

        tools[tool_name] = tool_metrics

    return tool_metrics


def increment_tool_metric(
    context: Any,
    tool_name: str,
    metric_name: str,
    amount: int = 1,
) -> int:
    """
    Increment a metric for a specific tool.

    Example:
        increment_tool_metric(
            context,
            "calculate",
            "calls",
        )
    """
    metrics = get_metrics(context)

    tool_metrics = _get_tool_metrics(
        metrics,
        tool_name,
    )

    current_value = tool_metrics.get(
        metric_name,
        0,
    )

    if not isinstance(current_value, (int, float)):
        current_value = 0

    new_value = current_value + amount

    tool_metrics[metric_name] = new_value

    set_metrics(
        context,
        metrics,
    )

    return new_value


def add_tool_duration(
    context: Any,
    tool_name: str,
    duration: float | None,
) -> float:
    """
    Add execution duration for a specific tool.
    """
    if duration is None:
        metrics = get_metrics(context)
        tool_metrics = _get_tool_metrics(
            metrics,
            tool_name,
        )

        return float(
            tool_metrics.get(
                "total_duration",
                0.0,
            )
        )

    metrics = get_metrics(context)

    tool_metrics = _get_tool_metrics(
        metrics,
        tool_name,
    )

    current_value = tool_metrics.get(
        "total_duration",
        0.0,
    )

    if not isinstance(current_value, (int, float)):
        current_value = 0.0

    new_value = float(current_value) + duration

    tool_metrics["total_duration"] = new_value

    set_metrics(
        context,
        metrics,
    )

    return new_value