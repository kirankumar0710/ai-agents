import ast
import operator
from langchain_core.tools import tool

_OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
}


def _eval_node(node):
    if isinstance(node, ast.Constant):
        if not isinstance(node.value, (int, float, complex)):
            raise ValueError(f"Non-numeric constant: {node.value!r}")
        return node.value
    if isinstance(node, ast.BinOp):
        return _OPS[type(node.op)](_eval_node(node.left), _eval_node(node.right))
    if isinstance(node, ast.UnaryOp):
        return _OPS[type(node.op)](_eval_node(node.operand))
    raise ValueError(f"Unsupported expression: {ast.dump(node)}")


def calculator(expression: str) -> str:
    try:
        tree = ast.parse(expression, mode="eval")
        return str(_eval_node(tree.body))
    except Exception as e:
        return f"Error: {e}"


@tool
def calculator_tool(expression: str) -> str:
    """Evaluate a mathematical expression. Input: a string like '2 + 2' or '100 * 1.08'."""
    return calculator(expression)
