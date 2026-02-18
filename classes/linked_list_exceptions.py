from typing import Any

class ValueTypeException(Exception):
    """Raised when value type passed to a linked list is not int, float, str, or bool."""
    def __init__(self, value: Any, msg="Value must be of type int, float, str, or bool."):
        self.value = value
        self.message = f"Invalid value type: {self.value}. {msg}"
        super().__init__(self.message)

class CycleDetectedException(Exception):
    """Raised when a linked list contains a cycle and an operation that would break the cycle is attempted."""
    def __init__(self, operation: Any, msg="Cannot perform operation on linked list with cycle."):
        self.operation = operation
        self.message = f"Invalid operation: {self.operation}. {msg}"
        super().__init__(self.message)
