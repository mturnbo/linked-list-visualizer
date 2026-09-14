"""Factory helpers for visualizer linked list instances."""

from typing import Any

from classes.doubly_linked_list import DoublyLinkedList
from classes.singly_linked_list import SinglyLinkedList
from utils import filter_values
from utils import to_ll_type


class LinkedList:
    @staticmethod
    def create(ll_type: str = "singly") -> SinglyLinkedList | DoublyLinkedList:
        """Return a new empty linked list of the specified type.

        Args:
            ll_type: Linked list type, accepting singly/s or doubly/d.

        Returns:
            A package-backed visualizer linked list adapter.

        Raises:
            ValueError: If the linked list type is unknown.
        """

        if ll_type.lower() in ["s", "singly"]:
            return SinglyLinkedList()
        if ll_type.lower() in ["d", "doubly"]:
            return DoublyLinkedList()

        raise ValueError(f"Unknown linked list type '{ll_type}'.")


    @staticmethod
    def build_from_values(
        ll_type: str,
        values: list[Any],
    ) -> SinglyLinkedList | DoublyLinkedList:
        """Build a linked list from raw visualizer values.

        Args:
            ll_type: Linked list type, accepting singly/s or doubly/d.
            values: Raw values from the CLI, shell, or tests.

        Returns:
            A linked list containing coerced visualizer-compatible values.
        """
        filtered_values = filter_values([to_ll_type(value) for value in values])
        ll = LinkedList.create(ll_type)
        ll.append_values(filtered_values)

        return ll


    @staticmethod
    def build_from_ops(
        ll_type: str,
        operations: list[tuple[str, list[int | float | str | bool], str]],
    ) -> SinglyLinkedList | DoublyLinkedList:
        """Build a linked list by replaying visualizer operations.

        Args:
            ll_type: Linked list type, accepting singly/s or doubly/d.
            operations: Operation tuples of command, arguments, and label.

        Returns:
            A linked list after all operations are applied.

        Raises:
            ValueError: If an operation type is unknown.
        """
        ll = LinkedList.create(ll_type)
        for op in operations:
            match op[0]:
                case "append":
                    ll.append(to_ll_type(op[1][0]))
                case "prepend":
                    ll.prepend(to_ll_type(op[1][0]))
                case "insert":
                    ll.insert(op[1][0], to_ll_type(op[1][1]))
                case "remove":
                    ll.remove(op[1][0])
                case "replace":
                    ll.replace(op[1][0], to_ll_type(op[1][1]))
                case "cycle":
                    ll.create_cycle(op[1][0])
                case "has_cycle":
                    result = ll.has_cycle()
                    print(f"Has cycle: {result}")
                case "sort":
                    method = op[1][0] if op[1] else 1
                    ll.sort(method=method)
                case _:
                    raise ValueError(f"Unknown operation type '{op[0]}' in operations file.")

        return ll
