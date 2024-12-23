import pytest
from typing import List, Any
from protofunc import Monad, Functor, functor, staticfunctor, MonadWithLogs, extract_logs


# Define test Functors
@functor
class Add:
    def __init__(self, y: int):
        self.y = y

    def __exec__(self, x: int) -> int:
        return x + self.y


@functor
class Multiply:
    def __init__(self, factor: int):
        self.factor = factor

    def __exec__(self, x: int) -> int:
        return x * self.factor


@staticfunctor
class AddOne:
    def __exec__(self, x: int) -> int:
        return x + 1

@staticfunctor
class Reverse:
    def __exec__(self, x: List[Any]) -> List[Any]:
        return x[::-1]

@functor
def to_float(x: int) -> float:
    return float(x)

def to_int(x: float) -> int:
    return int(x)
# ------------------------------ #
#   SIMPLE FUNCTIONALITY TESTS   #
# ------------------------------ #

# Tests for Monad and Functor functionality
def test_monad_initialization():
    m = Monad(5)
    assert m.__value__ == 5
    assert m.__dtype__ == "int"


def test_add_functor():
    m = Monad(5) | Add(3)
    assert m.__value__ == 8


def test_multiply_functor():
    m = Monad(5) | Multiply(2)
    assert m.__value__ == 10


def test_functor_chaining():
    m = Monad(5) | Add(3) >> Multiply(4)
    assert m.__value__ == 32


def test_composite_functor():
    composite = Add(3) >> Multiply(2)
    m = Monad(5) | composite
    assert m.__value__ == 16


def test_static_functor():
    m = Monad(5) | AddOne
    assert m.__value__ == 6


def test_static_and_composite_functor():
    composite = Add(2) >> Multiply(3)
    m = Monad(4) | composite >> AddOne
    assert m.__value__ == 19

def test_casting_with_or():
    m = Monad(5) | Add(3) | float
    assert isinstance(m, float)
    assert m == 8.0

def test_casting_multiple_times_1():
    m = Monad(5) | Add(3) >> int >> int | int
    assert isinstance(m, int)
    assert m == 8


def test_casting_multiple_times_2():
    m = Monad(5) | Add(3) >> float >> int >> float | int
    assert isinstance(m, int)
    assert m == 8


def test_multicast():
    m = Monad(5) | Add(3) >> to_float >> to_int >> float | int
    assert isinstance(m, int)
    assert m == 8


def test_double_static_functor_simple():
    m = Monad(5) | AddOne >> AddOne
    assert m.__value__ == 7


def test_double_static_functor_composite():
    composite = AddOne >> AddOne
    m = Monad(5) | composite >> AddOne
    assert m.__value__ == 8

# TODO Fix the MonadWithLogs code to uncomment test
# def test_monad_with_logs():
#     m = MonadWithLogs(5)
#     m = m | Add(3) >> Multiply(2) >> AddOne
#     logs = extract_logs(m)
#     assert logs == ["Add(8)", "Multiply(16)", "AddOne(17)"]
#     assert m.__value__ == 17

# ------------------------------ #
#          ERROR TESTS           #
# ------------------------------ #
def test_wrong_input_type():
    with pytest.raises(AssertionError):
        Add(3)("Not a Monad")


def test_wrong_input_type_static():
    with pytest.raises(AssertionError):
        Monad("hello") | AddOne | float


def test_wrong_input_type_composite():
    composite = Add(5) >> Multiply(2)
    with pytest.raises(AssertionError):
        Monad("hello") | Add(3) >> Multiply(2) >> AddOne | float
    with pytest.raises(AssertionError):
        Monad("hello") | composite >> AddOne | float


def test_wrong_type_between_functors():
    with pytest.raises(AssertionError):
        Add(3) >> Reverse


def test_wrong_type_between_functors_reverse():
    with pytest.raises(AssertionError):
        Reverse >> Add(3)


def test_wrong_type_between_functors_static():
    with pytest.raises(AssertionError):
        AddOne >> Reverse


def test_wrong_type_between_functors_static_reverse():
    with pytest.raises(AssertionError):
        Reverse >> AddOne


def test_invalid_functor_rshift():
    class InvalidFunctor:
        pass

    m = Monad(5)
    with pytest.raises(Exception):
        m >> InvalidFunctor()


def test_invalid_value_for_functor():
    with pytest.raises(AssertionError):
        Add(3)("Not a Monad")


def test_long_pipeline_operations():
    composite1 = Add(3) >> Multiply(2)
    composite2 = AddOne >> Multiply(4)

    m = Monad(5)
    m = m | composite1 >> Add(10) >> composite2 >> AddOne
    assert m.__value__ == 109  # ((5 + 3) * 2 + 10 + 1) * 4 + 1 = 109


# Longer execution tests
def test_long_pipeline_operations_inverse():
    composite1 = Add(3) >> Multiply(2)
    composite2 = Multiply(4) >> AddOne

    m = Monad(5)
    m = m | composite1 >> Add(10) >> composite2 >> AddOne
    assert m.__value__ == 106  # ((5 + 3) * 2 + 10 + 1) * 4 + 1 = 82


def test_long_pipeline_mixed_operations():
    composite1 = Add(2) >> Multiply(3)
    composite2 = Add(5) >> AddOne >> Multiply(2)

    m = Monad(2)
    m = m | composite1 >> Add(1) >> composite2
    assert m.__value__ == 38  # ((2 + 2) * 3 + 1 + 5 + 1) * 2 = 38


# def test_long_pipeline_with_logs():
#     composite1 = Add(3) >> Multiply(3)
#     composite2 = AddOne >> Multiply(5)
#
#     m = MonadWithLogs(2)
#     m = m | composite1 >> Add(4) >> composite2
#     logs = extract_logs(m)
#     assert logs == ["Add(5)", "Multiply(15)", "Add(19)", "AddOne(20)", "Multiply(100)"]
#     assert m.__value__ == 100

def test_very_long_pipeline():
    composite1 = Add(1) >> Multiply(2)
    composite2 = Add(4) >> Multiply(3)
    composite3 = Multiply(2) >> AddOne

    m = Monad(1)
    m = m | composite1 >> composite2 >> Add(10) >> composite3 >> AddOne
    assert m.__value__ == 70  # ((((1 + 1) * 2 + 4) * 3 + 10) + 1) * 2 + 1 = 70


# ------------------------------ #
#        EDGE CASE TESTS         #
# ------------------------------ #

def test_higher_order_monad():
    m = Monad(Monad(5))
    m >>= Add(3) >> Multiply(2) >> Monad
    assert m.__value__.__value__.__value__ == 16

def test_highest_order_monad_with_cast():
    m = Monad(Monad(Monad(5)))
    m = m >> Add(3) >> Multiply(2) | int
    assert m == 16

if __name__ == "__main__":
    pytest.main(["-v", __file__])
