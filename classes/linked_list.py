from classes.singly_linked_list import SinglyLinkedList
from classes.doubly_linked_list import DoublyLinkedList
from typing import List, Tuple, Any


class LinkedList:
    @staticmethod
    def create(ll_type: str = "singly") -> SinglyLinkedList | DoublyLinkedList:
        """Returns a new, empty linked list of the specified type."""

        if ll_type == "singly":
            return SinglyLinkedList()
        elif ll_type == "doubly":
            return DoublyLinkedList()
        else:
            raise ValueError(f"Unknown linked list type '{ll_type}'.")


    @staticmethod
    def build_from_values(ll_type: str, values: List[Any]) -> SinglyLinkedList | DoublyLinkedList:
        """Uses list of values to build a linked list."""

        filtered_values = list(filter(lambda x: type(x) in [int, float, str, bool], values))
        ll = LinkedList.create(ll_type)
        ll.append_values(filtered_values)

        return ll


    @staticmethod
    def build_from_ops(ll_type: str, operations: List[Tuple[str, List[int | float | str | bool], str]]):
        """Uses list of operations to build a linked list."""

        ll = LinkedList.create(ll_type)
        for op in operations:
            match op[0]:
                case "append":
                    ll.append(op[1][0])
                case "prepend":
                    ll.prepend(op[1][0])
                case "insert":
                    ll.insert(op[1][0], op[1][1])
                case "remove":
                    ll.remove(op[1][0])
                case "replace":
                    ll.replace(op[1][0], op[1][1])
                case "cycle":
                    ll.create_cycle(op[1][0])
                case "has_cycle":
                    result = ll.has_cycle()
                    print(f"Has cycle: {result}")
                case _:
                    raise ValueError(f"Unknown operation type '{op[0]}' in operations file.")

        return ll