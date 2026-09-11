"""Visualizer adapter for the package-backed singly linked list."""

from typing import Any

from constants import PRINT_ARROW_DOWN
from constants import PRINT_ARROW_LEFT
from constants import PRINT_ARROW_SINGLE as LINK_ARROW
from constants import PRINT_ARROW_UP
from constants import PRINT_COLOR
from constants import RESET
from linked_list.base import _MISSING
from linked_list import SinglyLinkedList as PackageSinglyLinkedList


class SinglyLinkedList(PackageSinglyLinkedList):
    """Singly linked list with visualizer-specific display helpers."""

    def __init__(self, initial_node_value: Any = _MISSING) -> None:
        """Initialize a singly linked list.

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
        values = self.get_values()
        header = f"Singly Linked List | {self.size} Elements:"
        nodes = f"[{LINK_ARROW.join(map(str, values))}]"
        cycle = self._cycle_marker(values, nodes)

        return f"\n{PRINT_COLOR}{header}\n{nodes}\n{cycle}{RESET}\n"

    def _cycle_marker(self, values: list[Any], nodes: str) -> str:
        """Build the terminal cycle marker for cyclic singly lists.

        Args:
            values: List values rendered in node order.
            nodes: Rendered node text.

        Returns:
            The rendered marker, or an empty string when the list is acyclic.
        """
        cycle_index = self.get_cycle_start_index()
        if cycle_index is None:
            return ""

        value_lengths = [len(str(value)) for value in values]
        length_to_cycle_index = (
            sum(value_lengths[:cycle_index])
            + (cycle_index * len(LINK_ARROW))
            + 1
        )
        cycle = f"{' ' * length_to_cycle_index}{PRINT_ARROW_UP}"

        length_to_tail = len(nodes) - length_to_cycle_index - 3
        cycle += f"{' ' * length_to_tail}{PRINT_ARROW_DOWN}"

        back_arrows = f"{PRINT_ARROW_LEFT} " * (length_to_tail // 2 + 1)
        cycle += f"\n{' ' * (length_to_cycle_index + 1)}{back_arrows}"

        return cycle

    def has_cycle(self, method: int = 1) -> bool:
        """Return whether the linked list contains a cycle.

        Args:
            method: Compatibility selector for historical cycle algorithms.

        Returns:
            True when the list contains a cycle.

        Raises:
            ValueError: If an unknown method is requested.
        """
        match method:
            case 1 | 2:
                return self._has_cycle()
            case 3:
                return self.tail is not None and self.tail.next is not None
            case _:
                raise ValueError("Method must be 1, 2, or 3.")

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
