"""Small, explicitly whitelisted numeric grammar; no eval/sympify of user strings."""
from __future__ import annotations

import ast
import math
import operator
from app.services.dataset_validation import DatasetValidationError

ERROR = 'Unsupported or excessive expression. Allowed: numbers, pi/e, + - * / **, sin/cos/sqrt/log and parentheses.'
BINARY = {ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul,
          ast.Div: operator.truediv, ast.Pow: operator.pow}
UNARY = {ast.UAdd: operator.pos, ast.USub: operator.neg}
FUNCTIONS = {'sin': math.sin, 'cos': math.cos, 'sqrt': math.sqrt, 'log': math.log}
CONSTANTS = {'pi': math.pi, 'e': math.e}


def evaluate(expression: str) -> dict:
    if not expression or len(expression) > 120:
        raise DatasetValidationError('invalid_expression', ERROR)
    try:
        tree = ast.parse(expression, mode='eval')
        if sum(1 for _ in ast.walk(tree)) > 48:
            raise ValueError('Complexity limit')

        def visit(node: ast.AST, depth: int = 0) -> float:
            if depth > 14:
                raise ValueError('Depth limit')
            if isinstance(node, ast.Constant) and type(node.value) in (int, float):
                result = float(node.value)
                if abs(result) > 1e6:
                    raise ValueError('Literal limit')
            elif isinstance(node, ast.Name) and node.id in CONSTANTS:
                result = CONSTANTS[node.id]
            elif isinstance(node, ast.UnaryOp) and type(node.op) in UNARY:
                result = UNARY[type(node.op)](visit(node.operand, depth + 1))
            elif isinstance(node, ast.BinOp) and type(node.op) in BINARY:
                left, right = visit(node.left, depth + 1), visit(node.right, depth + 1)
                if isinstance(node.op, ast.Pow) and abs(right) > 8:
                    raise ValueError('Exponent limit')
                result = BINARY[type(node.op)](left, right)
            elif isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in FUNCTIONS and len(node.args) == 1 and not node.keywords:
                result = FUNCTIONS[node.func.id](visit(node.args[0], depth + 1))
            else:
                raise ValueError('Forbidden syntax')
            if not isinstance(result, (int, float)) or not math.isfinite(result) or abs(result) > 1e12:
                raise ValueError('Numerical range limit')
            return float(result)

        value = visit(tree.body)
    except (SyntaxError, ValueError, TypeError, ArithmeticError, OverflowError) as exc:
        raise DatasetValidationError('invalid_expression', ERROR) from exc
    return {'expression': expression, 'value': value, 'method': 'restricted-python-ast-v1',
            'note': 'Whitelisted arithmetic evaluation only; no arbitrary Python, variables, or code execution.'}
