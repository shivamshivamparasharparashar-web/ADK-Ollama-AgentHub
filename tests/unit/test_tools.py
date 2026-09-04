from app.tools.function_tools import (
    calculate,
    get_system_status,
    get_current_datetime,
)


def test_calculate_addition():
    result = calculate("10 + 20")

    assert result["status"] == "success"
    assert result["result"] == 30


def test_calculate_complex_expression():
    result = calculate("(10 + 5) * 2")

    assert result["status"] == "success"
    assert result["result"] == 30


def test_calculate_negative_number():
    result = calculate("-10 + 5")

    assert result["status"] == "success"
    assert result["result"] == -5


def test_calculate_division():
    result = calculate("20 / 4")

    assert result["status"] == "success"
    assert result["result"] == 5


def test_calculate_division_by_zero():
    result = calculate("10 / 0")

    assert result["status"] == "error"


def test_calculate_invalid_expression():
    result = calculate("hello")

    assert result["status"] == "error"


def test_calculate_rejects_function_calls():
    result = calculate("__import__('os').system('dir')")

    assert result["status"] == "error"


def test_calculate_empty_expression():
    result = calculate("")

    assert result["status"] == "error"


def test_system_status():
    result = get_system_status()

    assert result["status"] == "success"
    assert "ADK-Ollama-AgentHub" in result["message"]
    assert "timestamp" in result


def test_current_datetime():
    result = get_current_datetime()

    assert result["status"] == "success"
    assert "date" in result
    assert "time" in result
    assert "datetime" in result