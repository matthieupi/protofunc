# **Pytofunc: A Programmable Pipeline Library for Python**

Welcome to **Pytofunc** – an innovative and flexible library for building composable and type-safe pipelines in Python. Inspired by functional programming paradigms, Pytofunc empowers developers to work with **Monads** and **Functors** to streamline complex workflows.

Whether you are dealing with data transformations, computational chains, or need a clean abstraction for sequential operations, Pytofunc helps you build expressive and modular code with ease.

---

## 🚀 **Why Pytofunc?**

Python is powerful, but writing **complex chains of operations** often leads to messy and hard-to-read code. Pytofunc introduces **Monads** and **Functors** to provide:

- **Clean Composition**: Chain operations seamlessly with the `>>` and `|` operators.
- **Readability**: Break down complex logic into small, reusable building blocks.
- **Logs and Debugging**: Integrated logs help you debug and inspect your pipeline transformations.
- **Extendable**: Write custom **Functors** and combine them into powerful compositional pipelines.
- **Dynamic Typing Flexibility**: Enhanced type validation ensures consistent pipelines with explicit error feedback.

---

## 🔧 **Key Features**

### 1. **Monad: Encapsulate Values and Operations**
A `Monad` is a wrapper for values that supports clean chaining of operations. You can initialize a Monad and apply Functors without polluting your codebase.

```python
from pytofunc import Monad

result = Monad(5) | Add(3) >> Multiply(2)
print(result)  # Output: 16
```

---

### 2. **Functors: Reusable Operations**
**Functors** represent single operations you can apply to a Monad. Write your own functors or use pre-built ones:

```python
from pytofunc import functor

@functor
class Add:
    def __init__(self, value: int):
        self.value = value
    
    def __exec__(self, x: int) -> int:
        return x + self.value
```

Use it like this:

```python
m = Monad(10) | Add(5)
print(m)  # Output: int(15)
```

---

### 3. **Static Functors**
For operations that do not require initialization, **Static Functors** provide syntactic elegance:

```python
from pytofunc import staticfunctor

@staticfunctor
class AddOne:
    @staticmethod
    def __exec__(x: int) -> int:
        return x + 1
```

Apply it seamlessly:

```python
result = Monad(5) | AddOne | int
print(result)  # Output: 6
```

---

### 4. **Composable Pipelines**
Combine functors using the `>>` operator to create powerful reusable pipelines:

```python
composite = Add(3) >> Multiply(2)
result = Monad(5) | composite
print(result)  # Output: 16
```

---

### 5. **Monads with Logs**
Need insights into your pipeline execution? **MonadWithLogs** tracks operations and outputs logs.

```python
from pytofunc import MonadWithLogs, extract_logs

m = MonadWithLogs(5) | Add(3) >> Multiply(2)
print(m)  # Output: 16
print(extract_logs(m))  # Logs: ["Add(8)", "Multiply(16)"]
```

---

### 6. **Improved Error Handling**

Pytofunc now provides:

- Detailed error feedback for invalid types or missing annotations in pipelines.
- Graceful handling of dynamic typing mismatches, with meaningful error messages.

---

### 7. **Dynamic Typing and Casting**
The pipeline supports flexible type casting, allowing transformations to seamlessly integrate multiple types:

```python
result = Monad(5) | Add(3) >> float >> int
print(result)  # Output: 8
```

---

## 🥉 **Usage Scenarios**

### 1. **Data Transformation Pipelines**
Build reusable data processing workflows using Functors:

```python
data_pipeline = Add(5) >> Multiply(3)
result = Monad(10) | data_pipeline
print(result)  # Output: 45
```

### 2. **Event Processing with Logs**
Track each stage of the pipeline execution for debugging:

```python
m = MonadWithLogs(2) | Add(3) >> Multiply(5)
print(m)  # Output: 25
print(extract_logs(m))  # Logs: ["Add(5)", "Multiply(25)"]
```

### 3. **Mathematical Computations**
Write reusable Functors for any domain-specific operation.

---

## 🌐 **New Features and Future Enhancements**

### 1. **Async Support**
Planned support for asynchronous Functors and Monads will enable workflows with I/O-bound or long-running tasks.

### 2. **Pipeline Visualization**
Future versions will introduce visualization tools to graphically represent pipeline execution for debugging and teaching.

### 3. **Parallel Execution**
Support for parallel Functor execution is under development, allowing optimized performance for computation-heavy pipelines.

### 4. **Custom Monad Types**
Users will be able to define specialized Monads like `Either` or `Maybe` for error handling and optional values.

---

## 📥 **Installation**

Install Pytofunc using pip:

```bash
pip install pytofunc
```

---

## 👩‍💻 **Getting Started**

Here is an end-to-end example showcasing Pytofunc's power:

```python
from pytofunc import Monad, MonadWithLogs, functor, staticfunctor, extract_logs

@functor
class Add:
    def __init__(self, value: int):
        self.value = value
    def __exec__(self, x: int) -> int:
        return x + self.value

@staticfunctor
class MultiplyByTwo:
    @staticmethod
    def __exec__(x: int) -> int:
        return x * 2

pipeline = Add(3) >> MultiplyByTwo

m = MonadWithLogs(5) | pipeline
print(m)  # Output: 16
print(extract_logs(m))  # Logs: ["Add(8)", "MultiplyByTwo(16)"]
```

---

## 🤝 **Contributing**

We welcome contributions! If you have ideas for new Functors, optimizations, or features, feel free to submit a pull request. Please refer to our [Contributing Guidelines](CONTRIBUTING.md) for more details on code style and testing practices.

---

## 🔖 **Changelog**

### Latest Changes:

- Enhanced dynamic typing validation and error handling.
- Improved Monad and Functor type compatibility checks.
- Support for more flexible casting and transformation pipelines.
- Expanded test suite for edge cases and boundary conditions.

---

## 📄 **License**

This project is licensed under the MIT License.

---

## 🌟 **Conclusion**

With Pytofunc, you can write **readable, modular, and functional pipelines** that simplify your code and supercharge your workflows. Whether you're working on data pipelines, mathematical computations, or debugging, Pytofunc gives you the power of functional programming without the complexity.

Give Pytofunc a try, and take your Python code to the next level! 🚀

