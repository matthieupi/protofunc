import copy
import inspect
import types
from typing import Callable, TypeVar, Generic, Union, Any

# Generic types for Functor and Monad
T = TypeVar('T')
R = TypeVar('R')
S = TypeVar('S')


# Monad implementation
class Monad(Generic[T]):
    __mtype__ = "Monad"

    def __init__(self, value: T, **kwargs):
        self.__dtype__ = type(value).__name__
        self.__value__ = value
        # Both __kwargs__ and __pre__ are used for logging for now,
        # but plans are to use them for more advanced features
        self.__kwargs__ = kwargs
        self.__pre__ = []

    def __exec__(self, func: Callable[[T], 'Monad[R]']) -> 'Monad[R]':
        self.__pre__.append(copy.deepcopy(self))
        print(f"{self.__class__.__name__}.__exec__({func.__name__})(value={self.__value__})")
        if hasattr(self.__value__, '__value__'):
            self.__value__  = self.__value__.__exec__(func)
        else:
            print(f"{self.__class__.__name__}.__exec__({func.__name__}): Applying function to value", flush=True)
            self = func(self)
        return self

    def __call__(self, *args, **kwargs):
        print(f"{self.__class__.__name__}.__call__({args}, {kwargs})")
        # Overload () operator for calling the value
        return self.__exec__(*args, **kwargs)

    def __rshift__(self, func: 'Functor[[T], R]') -> 'Functor[S, R]':
        """
        Compose the monad with a functor using >> operator.
        :param func: The functor to apply to the monad's value.
        :return:
        """
        assert isinstance(func, Functor), f"{self.__class__.__name__}.__rshift__({func}):" \
                                          f"Expected Functor, got {type(func)}"
        self = self.__exec__(func)
        return self

    def __or__(self, other):
        # Cast the value into a functor
        if type(other) == type:
            print(f"ERR: cast_type issubclass: {issubclass(other, Functor)}")
        if type(other) == type and issubclass(other, Functor):
            print(f"ERR: cast_type is a type")
            return other(self)
        elif isinstance(other, Functor):
            return other(self)
        # Cast the value to a different type
        else:
            if hasattr(self.__value__, '__value__'):
                return self.__value__.__or__(other)
            return other(self.__value__)

    def __repr__(self):
        return f'{self.__dtype__}({self.__value__})'


# Functor class
class Functor(Generic[T, R]):
    __name__ = "Functor"
    #def __init__(self, fn: Callable[[T], R] = None):
    #    if fn:
    #        kelf.__exec__ = fn

    def __exec__(self, monad: Monad[T]) -> Monad[R]:
        # Apply the functor to the monad's value from the children classes
        raise NotImplementedError(f"{self.__class__.__name__}.__exec__({monad}):")

    def __call__(self, value, *args, **kwargs) -> R:
        assert isinstance(value, Monad), f"{self.__class__.__name__}.__call__({value}):" \
                                         f"Expected Monad, got {type(value)}"
        print(f"{self.__class__.__name__}.__call__({value})")
        self.__validate__(value)
        value.__value__ = self.__exec__(value.__value__)
        value.__dtype__ = type(value.__value__).__name__
        return value

    def __ror__(self, monad: Monad[T]) -> Monad[R]:
        print(f"{self.__class__.__name__}.__ror__({monad})")
        assert isinstance(monad, Monad), f"Prototype 57: {self.__class__.__name__}.__ror__({monad})" \
                                         f"Expected Monad, got {type(monad)}"
        # Overload | operator for chaining with Monads or raw values
        if isinstance(monad, Monad):
            monad._value = self(monad._value)
            return monad
        raise TypeError(f"{self.__class__.__name__}.__ror__({monad}): \n"
                        f"    Expected Monad, got {type(monad)}")

    def __validate__(self, value: Monad[T]) -> Monad[T]:
        """Validate input types of Monad against Functor's type annotations."""
        assert isinstance(value, Monad), f"{self.__class__.__name__}.__validate__({value}):" \
                                         f"Expected Monad, got {type(value)}"
        sig = inspect.signature(self.__exec__)
        assert len(sig.parameters) == 1, f"{self.__class__.__name__}.__validate__({value}): \n" \
                                         f"     Expected 1 parameters, got {len(sig.parameters)}"
        input_type = list(sig.parameters.values())[0].annotation
        if input_type is not inspect._empty:
            assert value.__dtype__ == input_type.__name__, \
                f"Type Mismatch: Expected {input_type.__name__}, got {value.__dtype__}"
        return True

    @staticmethod
    def __compose__(first: 'Functor[[T], R]', second: Union['Functor[[R], S]', Callable[[R], S]]) -> 'Functor[[T], S]':
        match second:
            case Functor():
                return CompositeFunctor(first, second)
            case _ if isinstance(second, type):
                annotations = {"value": list(first.__exec__.__annotations__.values())[0], "return": second}
                hints = {"__annotations__": annotations}
                first_codomain = list(first.__exec__.__annotations__.values())[0]

                @functor
                @staticmethod
                def cast_type(value: first_codomain) -> second:
                    return second(value)

                return CompositeFunctor(first, cast_type)
            case _ if callable(second) or isinstance(second, type):
                assert hasattr(second, "__annotations__"), (
                    f"{first.__name__}.__compose__({second.__name__}):\n"
                    f"    Cannot include {second.__name__} in pipeline: Missing type annotations."
                )
                print(f"{first.__name__}.__compose__({second.__name__}): Casting function to Functor")
                second = functor(second)
                return CompositeFunctor(first, second)
        return CompositeFunctor(first, second)

    def __rshift__(self, other: Union['Functor', Callable]) -> 'Functor':
        print(f"{self.__name__}.__rshift__({other.__name__})")
        # Cast function to Functor
        return self.__compose__(self, other)

    def __rrshift__(self, other):
        return self.__compose__(other, self)

    def __irshift__(self, other):
        return self.__compose__(self, other)


class CompositeFunctor(Functor):
    def __init__(self, first: 'Functor[[T], R]', second: 'Functor[[R], S]') -> 'Functor[[T], S]':
        # TODO: Will move eventually to an arbitrary number of functors
        self.operations = [first, second]
        self.first = first
        self.second = second
        # Extract type annotaions and validate the composition compatibility
        first_domain = list(first.__exec__.__annotations__.values())[0]
        first_codomain = dict(first.__exec__.__annotations__)["return"]
        second_domain = list(second.__exec__.__annotations__.values())[0]
        second_codomain = dict(second.__exec__.__annotations__)["return"]

        assert first_codomain == second_domain, (f"{self.__name__}.__init__({first.__name__}, {second.__name__}):\n" 
                                                 f"Type Mismatch: Expected {first_codomain}, got {second_domain}")

        self.__name__ = f"{first.__name__ or first.__class__.__name__}.{second.__name__ or second.__class__.__name__}"
        # Dynamically define __exec__ for composite functor with proper annotations
        hints = {"__annotations__": {"value": first_domain, "return": second_codomain}}
        def __exec__(self, value: T) -> S:
            intermediate = self.first.__exec__(value)
            return self.second.__exec__(intermediate)
        # Attach the dynamic __exec__ method with annotations to self
        self.__exec__ = __exec__
        self.__exec__ = types.MethodType(type('exec', (object,), hints), self)

    def __call__(self, value: 'Monad[T]') -> 'Monad[S]':
        assert isinstance(value, Monad), f"{self.__class__.__name__}.__call__({value}):" \
                                         f"Expected Monad, got {type(value)}"
        # Apply the first functor, then the second
        value.__exec__(self.first)
        value.__exec__(self.second)
        return value


# Decorator to dynamically create functor classes
def functor(cls: type | Callable[[T], R]):
    match cls:
        case _ if isinstance(cls, type):
            return type(cls.__name__, (Functor,), dict(cls.__dict__) | {"__name__": cls.__name__})
        case _ if callable(cls):
            return type(cls.__name__, (Functor,), dict(object.__dict__) | {"__exec__": staticmethod(cls), "__name__": cls.__name__})()
    """ Class decorator that dynamically creates a new class inheriting from Functor."""
    return type(cls.__name__, (Functor,), dict(cls.__dict__) | {"__name__": cls.__name__})

def staticfunctor(cls):
    """
    Class decorator that dynamically creates a new class inheriting from Functor and the target class.
    """
    return type(cls.__name__, (Functor,), dict(cls.__dict__) | {"__name__": cls.__name__})()

# Example functors
@functor
class Add:
    def __init__(self, y: int):
        self.y = y

    def __exec__(self, x: int) -> int:
        print(f"Add({x}, {self.y})")
        return x + self.y

@functor
class Multiply:
    def __init__(self, factor: int):
        self.factor = factor

    def __exec__(self, x: int) -> int:
        print(f"Multiply({x}, {self.factor})")
        return x * self.factor

@staticfunctor
class AddOne:
    # def __new__(cls, *args):
    #    # Create and return a Monad instance instead of an AddOne instance
    #    return cls.__exec__(*args)

    @staticmethod
    def __exec__(x: int) -> int:
        print(f"AddOne({x})")
        return x + 1

# Monad with logging capabilities
class MonadWithLogs(Monad):
    def __init__(self, value: T):
        super().__init__(value)
        self.__logs__ = []

    def __exec__(self, func: 'Functor[T, R]') -> 'MonadWithLogs[R]':
        print(f"{self.__class__.__name__}.MonadWithLogs.__exec__({func.__name__})")
        print(f"Value and type before: {self.__value__}, {type(self)}", flush=True)
        self = super().__exec__(func)
        print(f"Value and type after: {self.__value__}, {type(self)}", flush=True)
        self.__logs__.append(f"{func.__name__}({self.__value__})")
        return self


def extract_logs(value: MonadWithLogs):
    print(f"extract_logs({value.__value__})")
    print(f"Value type: {type(value)}")
    print(f"dtype: {value.__dtype__}")
    return value.__logs__

def to_string(value: float) -> str:
    return str(value)

def to_float(value: str) -> float:
    return float(value)


# Usage demonstration
if __name__ == "__main__":
    to_string = functor(to_string)


    monad = Monad(MonadWithLogs(MonadWithLogs(Monad(5))))
    NAd = Monad >> MonadWithLogs
    print("Monad: ", monad)
    #Monad(5) | Add(3) >> Multiply(20) >> float >> to_string >> to_float | print # | extract_logs
    # Using Monad in the pipeline
    monad >>= Add(3) >> Multiply(20) >> to_float >> to_string >> to_float >> Add(5)
    print("Monad using >>=: ", monad)
    result = Monad(5) | Add(3) >> Multiply(20)
    print(f"Result 1: {result}")
    composite = Add(3) >> Multiply(25)
    #print(result)  # Output: 160.0
    # Using Monad with instantiated functors
    result = Monad(5) | composite >> Add(3) >> AddOne >> Multiply(2) | float
    print(f"Result 2: {result}", flush=True)  # Output: 160.0
    # Let's kick it up a notch
    # We will now run with logs
    result = MonadWithLogs(5) | composite >> Add(3) >> AddOne >> Multiply(2)
    print(f"Result log: {result.__logs__}")
    print(f"Result 3: {result}")
