from pathlib import Path

from classes.animation import NodeValue, Operation
from utils import to_ll_type


class OperationInputError(ValueError):
    """Raised when a GUI operation draft cannot be converted into an operation."""


class OperationQueue:
    """Validate and store linked-list operations created from GUI controls."""

    def __init__(self, operations: list[Operation] | None = None) -> None:
        self.operations = list(operations or [])

    def add_operation(
        self,
        operation: str,
        value_text: str = "",
        index_text: str = "",
        sort_method_text: str = "",
    ) -> Operation | None:
        """Validate an operation draft and append it to the queue.

        Args:
            operation: Operation name from the GUI selector.
            value_text: Raw value field contents.
            index_text: Raw index field contents.
            sort_method_text: Raw sort method field contents.

        Returns:
            The appended operation, or ``None`` when clear resets the queue.

        Raises:
            OperationInputError: If the operation name or arguments are invalid.
        """
        operation = operation.strip().lower()
        if operation in {"append", "prepend"}:
            value = self._required_value(value_text)
            return self._append((operation, [value], f"{operation} {value}"))
        if operation in {"insert", "replace"}:
            index = self._required_index(index_text)
            value = self._required_value(value_text)
            return self._append((operation, [index, value], f"{operation} {index} {value}"))
        if operation in {"remove", "cycle"}:
            index = self._required_index(index_text)
            return self._append((operation, [index], f"{operation} {index}"))
        if operation == "sort":
            method = self._optional_sort_method(sort_method_text)
            return self._append(("sort", [method], f"sort {method}"))
        if operation in {"reverse", "has_cycle"}:
            return self._append((operation, [], operation))
        if operation == "clear":
            self.clear()
            return None
        raise OperationInputError(f"Unsupported operation '{operation}'.")

    def clear(self) -> None:
        """Remove all queued operations."""
        self.operations = []

    def load_operations_file(self, path: Path) -> None:
        """Replace the queue with operations parsed from an existing ops file.

        Args:
            path: Path to the operations text file.

        Raises:
            OperationInputError: If the file cannot be parsed.
        """
        try:
            from main import parse_operations

            self.operations = parse_operations(str(path))
        except ValueError as exc:
            raise OperationInputError(str(exc)) from exc

    def _append(self, operation: Operation) -> Operation:
        self.operations.append(operation)
        return operation

    def _required_value(self, value_text: str) -> NodeValue:
        value_text = value_text.strip()
        if not value_text:
            raise OperationInputError("Operation requires a value.")
        return to_ll_type(value_text)

    def _required_index(self, index_text: str) -> int:
        index_text = index_text.strip()
        if not index_text:
            raise OperationInputError("Operation requires an index.")
        try:
            return int(index_text)
        except ValueError as exc:
            raise OperationInputError("Operation requires an integer index.") from exc

    def _optional_sort_method(self, sort_method_text: str) -> int:
        sort_method_text = sort_method_text.strip()
        if not sort_method_text:
            return 1
        try:
            return int(sort_method_text)
        except ValueError as exc:
            raise OperationInputError("Sort method must be an integer.") from exc
