from __future__ import annotations

import ast
import operator
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Any


class BaseMCPTool(ABC):
    name: str
    description: str
    input_schema: dict[str, Any]
    requires_approval: bool = False

    @abstractmethod
    async def execute(
        self,
        arguments: dict[str, Any],
    ) -> Any:
        raise NotImplementedError


class EchoTool(BaseMCPTool):
    name = "echo"
    description = "Returns the supplied message."
    input_schema = {
        "type": "object",
        "properties": {
            "message": {
                "type": "string",
                "description": "Message to return.",
            }
        },
        "required": ["message"],
    }

    async def execute(
        self,
        arguments: dict[str, Any],
    ) -> dict[str, str]:
        message = arguments.get("message")

        if not isinstance(message, str) or not message.strip():
            raise ValueError(
                "The 'message' argument must be a non-empty string."
            )

        return {
            "message": message,
        }


class CurrentTimeTool(BaseMCPTool):
    name = "current_time"
    description = "Returns the current UTC date and time."
    input_schema = {
        "type": "object",
        "properties": {},
    }

    async def execute(
        self,
        arguments: dict[str, Any],
    ) -> dict[str, str]:
        current_time = datetime.now(timezone.utc)

        return {
            "timezone": "UTC",
            "datetime": current_time.isoformat(),
        }


class CalculatorTool(BaseMCPTool):
    name = "calculator"
    description = (
        "Performs arithmetic using either an expression or "
        "two numbers and an operation."
    )
    input_schema = {
        "type": "object",
        "properties": {
            "expression": {
                "type": "string",
                "description": "Example: (10 + 5) * 2",
            },
            "a": {
                "type": "number",
            },
            "b": {
                "type": "number",
            },
            "operation": {
                "type": "string",
                "enum": [
                    "add",
                    "subtract",
                    "multiply",
                    "divide",
                    "power",
                    "modulo",
                ],
            },
        },
    }

    _binary_operators = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.Pow: operator.pow,
        ast.Mod: operator.mod,
        ast.FloorDiv: operator.floordiv,
    }

    _unary_operators = {
        ast.UAdd: operator.pos,
        ast.USub: operator.neg,
    }

    async def execute(
        self,
        arguments: dict[str, Any],
    ) -> dict[str, int | float]:
        expression = arguments.get("expression")

        if isinstance(expression, str) and expression.strip():
            value = self._evaluate_expression(expression)
            return {
                "value": value,
            }

        a = arguments.get("a")
        b = arguments.get("b")
        operation_name = arguments.get("operation")

        if not isinstance(a, (int, float)):
            raise ValueError(
                "The 'a' argument must be a number."
            )

        if not isinstance(b, (int, float)):
            raise ValueError(
                "The 'b' argument must be a number."
            )

        operations = {
            "add": operator.add,
            "subtract": operator.sub,
            "multiply": operator.mul,
            "divide": operator.truediv,
            "power": operator.pow,
            "modulo": operator.mod,
        }

        selected_operation = operations.get(
            str(operation_name).lower()
        )

        if selected_operation is None:
            raise ValueError(
                "Operation must be add, subtract, multiply, "
                "divide, power or modulo."
            )

        if operation_name in {"divide", "modulo"} and b == 0:
            raise ValueError("Division by zero is not allowed.")

        return {
            "value": selected_operation(a, b),
        }

    def _evaluate_expression(
        self,
        expression: str,
    ) -> int | float:
        try:
            parsed = ast.parse(
                expression,
                mode="eval",
            )
        except SyntaxError as exc:
            raise ValueError(
                "Invalid mathematical expression."
            ) from exc

        return self._evaluate_node(parsed.body)

    def _evaluate_node(
        self,
        node: ast.AST,
    ) -> int | float:
        if isinstance(node, ast.Constant):
            if isinstance(node.value, (int, float)):
                return node.value

            raise ValueError(
                "Only numeric constants are allowed."
            )

        if isinstance(node, ast.BinOp):
            operation = self._binary_operators.get(
                type(node.op)
            )

            if operation is None:
                raise ValueError(
                    "The expression contains an unsupported operator."
                )

            left_value = self._evaluate_node(node.left)
            right_value = self._evaluate_node(node.right)

            if isinstance(node.op, (ast.Div, ast.FloorDiv, ast.Mod)):
                if right_value == 0:
                    raise ValueError(
                        "Division by zero is not allowed."
                    )

            return operation(left_value, right_value)

        if isinstance(node, ast.UnaryOp):
            operation = self._unary_operators.get(
                type(node.op)
            )

            if operation is None:
                raise ValueError(
                    "The expression contains an unsupported unary operator."
                )

            return operation(
                self._evaluate_node(node.operand)
            )

        raise ValueError(
            "The expression contains unsupported syntax."
        )