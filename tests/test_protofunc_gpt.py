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
    def __exec__(self, x: list[Any]) -> list[Any]:
        return x[::-1]


@functor
class MultiplyFirst:
    def __init__(self, factor: int):
        self.factor = factor

    def __exec__(self, x: list[Any]) -> list[Any]:
        x[0] *= self.factor
        return x

@functor
def to_float(x: int) -> float:
    return float(x)

def to_int(x: float) -> int:
    return int(x)

# ------------------------------ #
#   PARAMETERIZED FUNCTIONALITY TESTS   #
# ------------------------------ #

@pytest.mark.parametrize("initial, functor, expected", [
    (5, Add(3), 8),
    (5, Multiply(2), 10),
    (5, AddOne, 6),
])
def test_basic_functors(initial, functor, expected):
    m = Monad(initial) | functor
    assert m.__value__ == expected

@pytest.mark.parametrize("initial, composite, expected", [
    (5, Add(3) >> Multiply(2), 16),
    (5, AddOne >> AddOne, 7),
])
def test_composite_functors(initial, composite, expected):
    m = Monad(initial) | composite
    assert m.__value__ == expected

@pytest.mark.parametrize("initial, pipeline, expected", [
    (5, Add(3) >> Multiply(2) >> Add(5), 21),
    (5, Add(100) >> AddOne, 106 ),
])
def test_pipeline_chaining(initial, pipeline, expected):
    if isinstance(expected, list):
        m = Monad(initial) | pipeline
    else:
        m = Monad(5) | pipeline
    assert m.__value__ == expected

# ------------------------------ #
#          ERROR TESTS           #
# ------------------------------ #

# @pytest.mark.parametrize("pipeline", [
#     AddOne >> Reverse,
#     Reverse >> Add(3),
# ])
# def test_type_conflict_in_pipelines(pipeline):
#     with pytest.raises(AssertionError):
#         Monad(5) | pipeline

# ------------------------------ #
#        EDGE CASE TESTS         #
# ------------------------------ #

def test_nested_monad_initialization():
    m = Monad(Monad([1, 2, 3])) | Reverse >> MultiplyFirst(2)
    assert m.__value__.__value__ == [6, 2, 1]

def test_conflicting_types():
    with pytest.raises(AssertionError):
        Monad(5) | (Add(3) >> Reverse)

def test_higher_order_monad():
    m = Monad(Monad(5))
    m >>= Add(3) >> Multiply(2) >> Monad
    assert m.__value__.__value__.__value__ == 16

def test_monad_with_logs():
    m = MonadWithLogs(5) | Add(3) >> Multiply(2)
    logs = extract_logs(m)
    assert logs == ["Add(8)", "Multiply(16)"]
    assert m.__value__ == 16

if __name__ == "__main__":
    pytest.main(["-v", __file__])
