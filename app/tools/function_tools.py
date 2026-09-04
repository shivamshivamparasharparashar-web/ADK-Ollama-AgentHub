import ast
import operator as op
from datetime import datetime


_ALLOWED_OPERATORS = {
    ast.Add: op.add,
    ast.Sub: op.sub,
    ast.Mult: op.mul,
    ast.Div: op.truediv,
    ast.Mod: op.mod,
    ast.Pow: op.pow,
    ast.USub: op.neg,
    ast.UAdd: op.pos,
}


def _safe_eval(node):
    """Safely evaluate a mathematical AST node."""

    if isinstance(node, ast.Constant):
        if isinstance(node.value, (int, float)):
            return node.value

        raise ValueError("Only numbers are allowed.")

    if isinstance(node, ast.BinOp):
        operator = _ALLOWED_OPERATORS.get(type(node.op))

        if operator is None:
            raise ValueError(
                f"Operator '{type(node.op).__name__}' is not allowed."
            )

        left = _safe_eval(node.left)
        right = _safe_eval(node.right)

        return operator(left, right)

    if isinstance(node, ast.UnaryOp):
        operator = _ALLOWED_OPERATORS.get(type(node.op))

        if operator is None:
            raise ValueError(
                f"Operator '{type(node.op).__name__}' is not allowed."
            )

        return operator(_safe_eval(node.operand))

    raise ValueError("Invalid mathematical expression.")


def calculate(expression: str) -> dict:
    """
    Safely evaluate a mathematical expression.

    Supported:
    +, -, *, /, %, **
    Positive and negative numbers
    Parentheses
    """

    if not isinstance(expression, str):
        return {
            "status": "error",
            "message": "Expression must be a string.",
        }

    expression = expression.strip()

    if not expression:
        return {
            "status": "error",
            "message": "Expression cannot be empty.",
        }

    if len(expression) > 200:
        return {
            "status": "error",
            "expression": expression,
            "message": "Expression is too long.",
        }

    try:
        tree = ast.parse(expression, mode="eval")

        result = _safe_eval(tree.body)

        return {
            "status": "success",
            "expression": expression,
            "result": result,
        }

    except ZeroDivisionError:
        return {
            "status": "error",
            "expression": expression,
            "message": "Division by zero is not allowed.",
        }

    except (SyntaxError, ValueError, TypeError, OverflowError) as exc:
        return {
            "status": "error",
            "expression": expression,
            "message": str(exc),
        }


def get_system_status() -> dict:
    """Return the current status of ADK-Ollama-AgentHub."""

    return {
        "status": "success",
        "message": "ADK-Ollama-AgentHub is running.",
        "timestamp": datetime.now().isoformat(),
    }


def get_current_datetime() -> dict:
    """Return the current local date and time."""

    now = datetime.now()

    return {
        "status": "success",
        "date": now.strftime("%Y-%m-%d"),
        "time": now.strftime("%H:%M:%S"),
        "datetime": now.isoformat(),
    }