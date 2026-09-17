"""Herramientas aritmeticas que Gemini puede solicitar."""

from langchain.tools import tool


@tool
def multiply(a: int, b: int) -> int:
    """Multiplica dos enteros.

    Args:
        a: Primer factor.
        b: Segundo factor.

    Returns:
        El producto de `a` y `b`.
    """
    return a * b


@tool
def add(a: int, b: int) -> int:
    """Suma dos enteros.

    Args:
        a: Primer sumando.
        b: Segundo sumando.

    Returns:
        La suma de `a` y `b`.
    """
    return a + b


@tool
def divide(a: int, b: int) -> float:
    """Divide `a` entre `b`.

    Args:
        a: Dividendo.
        b: Divisor.

    Returns:
        El resultado decimal de la division.

    Raises:
        ValueError: Si `b` es cero.
    """
    if b == 0:
        raise ValueError("No se puede dividir entre cero.")
    return a / b

tools = [add, multiply, divide]
tools_by_name = {tool.name: tool for tool in tools}