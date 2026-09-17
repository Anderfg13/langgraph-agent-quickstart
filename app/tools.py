from langchain.tools import tool


@tool
def multiply(a: int, b: int) -> int:
    """Multiplica dos enteros."""
    return a * b


@tool
def add(a: int, b: int) -> int:
    """Suma dos enteros."""
    return a + b


@tool
def divide(a: int, b: int) -> float:
    """Divide dos enteros."""
    if b == 0:
        raise ValueError("No se puede dividir entre cero.")
    return a / b

tools = [add, multiply, divide]
tools_by_name = {tool.name: tool for tool in tools}