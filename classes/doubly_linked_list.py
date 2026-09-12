"""Visualizer adapter for the package-backed doubly linked list."""

from typing import Any

from constants import PRINT_ARROW_DOUBLE as LINK_ARROW
from constants import PRINT_COLOR
from constants import RESET
from linked_list.base import _MISSING
from linked_list import DoublyLinkedList as PackageDoublyLinkedList


class DoublyLinkedList(PackageDoublyLinkedList):
    """Doubly linked list with visualizer-specific display helpers."""

    def __init__(self, initial_node_value: Any = _MISSING) -> None:
        """Initialize a doubly linked list.

        Args:
            initial_node_value: Optional initial node value.
        """
        super().__init__(initial_node_value, sort_key=self._visualizer_sort_key)

    @staticmethod
    def _visualizer_sort_key(value: Any) -> tuple[str, str]:
        """Return a stable sort key for mixed visualizer input values.

        Args:
            value: Node value.

        Returns:
            A tuple suitable for comparing heterogeneous values.
        """
        return (str(type(value)), str(value))

    def __str__(self) -> str:
        """Return the linked list using the visualizer's terminal format.

        Returns:
            A colored linked list representation.
        """
        values = self.get_values(self.size)
        header = f"Doubly Linked List | {self.size} Elements:"
        nodes = f"[{LINK_ARROW.join(map(str, values))}]"

        return f"\n{PRINT_COLOR}{header}\n{nodes}{RESET}\n"

    def has_cycle(self, method: int = 1) -> bool:
        """Return whether the linked list contains a visualizer cycle.

        Args:
            method: Compatibility selector retained for old shell calls.

        Returns:
            False because the visualizer only animates cycles for singly lists.
        """
        return False

    def get_cycle_start_index(self, method: int = 1) -> None:
        """Return no cycle start for visualizer-managed doubly lists.

        Args:
            method: Compatibility selector retained for old shell calls.

        Returns:
            None.
        """
        return None

    def create_cycle(self, start: int) -> bool:
        """Keep historical visualizer behavior for doubly lists.

        Args:
            start: Ignored cycle start index.

        Returns:
            False because doubly cycle animation is unsupported.
        """
        return False

    def trim(self) -> bool:
        """Remove the tail node.

        Returns:
            True when a node was removed.

        Raises:
            IndexError: If the list is empty.
        """
        self.pop_tail()
        return True

    def show(self) -> None:
        """Print the linked list representation."""
        print(self)
