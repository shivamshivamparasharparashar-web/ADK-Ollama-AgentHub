from __future__ import annotations

import pytest

from app.callbacks.guardrails import (
    MAX_INPUT_LENGTH,
    MAX_OUTPUT_LENGTH,
    MAX_TOOL_ARGUMENT_LENGTH,
    validate_input,
    validate_output,
    validate_tool_arguments,
)


# ============================================================================
# Input validation
# ============================================================================

def test_empty_input_is_rejected():
    valid, reason = validate_input("")
    assert valid is False
    assert reason


def test_whitespace_input_is_rejected():
    valid, reason = validate_input("   \t\n  ")
    assert valid is False
    assert reason


@pytest.mark.parametrize(
    "value",
    [
        "Hello agent",
        "calculate 10 + 20",
        "What is the current date?",
        "a",
        "x" * MAX_INPUT_LENGTH,
    ],
)
def test_normal_and_boundary_inputs_are_accepted(value):
    valid, reason = validate_input(value)
    assert valid is True
    assert reason is None


def test_input_length_limit_rejects_one_character_over_limit():
    valid, reason = validate_input("x" * (MAX_INPUT_LENGTH + 1))
    assert valid is False
    assert "maximum" in reason.lower()


def test_null_character_is_rejected():
    valid, reason = validate_input("hello\x00world")
    assert valid is False
    assert "control" in reason.lower()


@pytest.mark.parametrize(
    "value",
    [
        None,
        123,
        {},
        [],
        object(),
    ],
)
def test_non_string_input_is_rejected(value):
    valid, reason = validate_input(value)
    assert valid is False
    assert reason


# ============================================================================
# Tool argument validation
# ============================================================================

def test_valid_tool_arguments():
    valid, reason = validate_tool_arguments(
        "calculate",
        {"expression": "10 + 20"},
    )
    assert valid is True
    assert reason is None


@pytest.mark.parametrize(
    "args",
    [
        {},
        {"expression": None},
        {"expression": 123},
        {"expression": ""},
        {"expression": "   "},
    ],
)
def test_calculate_invalid_expression_arguments_are_rejected(args):
    valid, reason = validate_tool_arguments("calculate", args)
    assert valid is False
    assert reason


def test_calculate_requires_expression():
    valid, reason = validate_tool_arguments("calculate", {})
    assert valid is False
    assert "expression" in reason.lower()


def test_calculate_requires_string_expression():
    valid, reason = validate_tool_arguments(
        "calculate",
        {"expression": 123},
    )
    assert valid is False
    assert "string" in reason.lower()


def test_calculate_rejects_empty_expression():
    valid, reason = validate_tool_arguments(
        "calculate",
        {"expression": "   "},
    )
    assert valid is False
    assert "empty" in reason.lower()


def test_generic_tool_with_empty_arguments_is_allowed():
    valid, reason = validate_tool_arguments("some_tool", {})
    assert valid is True
    assert reason is None


def test_tool_arguments_must_be_dictionary():
    valid, reason = validate_tool_arguments("calculate", [])
    assert valid is False
    assert "dictionary" in reason.lower()


def test_tool_arguments_size_limit():
    oversized = {
        "expression": "x" * MAX_TOOL_ARGUMENT_LENGTH,
    }

    valid, reason = validate_tool_arguments(
        "some_tool",
        oversized,
    )

    assert valid is False
    assert "maximum" in reason.lower()


def test_tool_arguments_with_unicode_are_supported():
    valid, reason = validate_tool_arguments(
        "some_tool",
        {"message": "नमस्ते दुनिया"},
    )
    assert valid is True
    assert reason is None


# ============================================================================
# Output validation
# ============================================================================

def test_output_is_valid():
    valid, reason = validate_output("normal response")
    assert valid is True
    assert reason is None


def test_none_output_is_valid():
    valid, reason = validate_output(None)
    assert valid is True
    assert reason is None


def test_output_at_exact_boundary_is_valid():
    valid, reason = validate_output("x" * MAX_OUTPUT_LENGTH)
    assert valid is True
    assert reason is None


def test_output_over_limit_is_rejected():
    valid, reason = validate_output(
        "x" * (MAX_OUTPUT_LENGTH + 1)
    )
    assert valid is False
    assert "maximum" in reason.lower()


def test_output_with_null_character_is_rejected():
    valid, reason = validate_output("normal\x00response")
    assert valid is False
    assert "control" in reason.lower()


@pytest.mark.parametrize(
    "value",
    [
        123,
        {},
        [],
        object(),
    ],
)
def test_non_string_output_is_rejected(value):
    valid, reason = validate_output(value)
    assert valid is False
    assert "text" in reason.lower()


# ============================================================================
# Regression checks for return contract
# ============================================================================

def test_valid_input_returns_none_reason():
    valid, reason = validate_input("valid request")
    assert valid is True
    assert reason is None


def test_valid_tool_arguments_return_none_reason():
    valid, reason = validate_tool_arguments(
        "calculate",
        {"expression": "2 + 2"},
    )
    assert valid is True
    assert reason is None


def test_valid_output_returns_none_reason():
    valid, reason = validate_output("valid response")
    assert valid is True
    assert reason is None
