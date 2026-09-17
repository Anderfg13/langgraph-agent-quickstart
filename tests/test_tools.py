import pytest

from app.tools import add, divide, multiply


def test_add_tool():
    assert add.invoke({"a": 3, "b": 4}) == 7


def test_multiply_tool():
    assert multiply.invoke({"a": 7, "b": 2}) == 14


def test_divide_tool():
    assert divide.invoke({"a": 14, "b": 2}) == 7


def test_divide_by_zero():
    with pytest.raises(ValueError, match="No se puede dividir entre cero"):
        divide.invoke({"a": 14, "b": 0})