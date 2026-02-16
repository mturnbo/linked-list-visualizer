from typing import Any

from classes.singly_linked_list import SinglyLinkedList
from classes.doubly_linked_list import DoublyLinkedList
from typing import List, Tuple

class LinkedList:

    @staticmethod
    def generate(type: str = "singly") -> SinglyLinkedList | DoublyLinkedList:
        if type == "singly":
            return SinglyLinkedList()
        elif type == "doubly":
            return DoublyLinkedList()
        else:
            raise ValueError(f"Unknown linked list type '{self.type}'.")


    @staticmethod
    def build_from_values(ll_type: str, values: List[int | float | str | bool]) -> SinglyLinkedList | DoublyLinkedList:
        ll = LinkedList.generate(ll_type)
        for value in values:
            ll.append(value)

        return ll


    @staticmethod
    def build_from_ops(ll_type: str, operations: List[Tuple[str, List[int | float | str | bool], str]]):
        ll = LinkedList.generate(ll_type)
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
                case _:
                    raise ValueError(f"Unknown operation type '{op[0]}' in operations file.")

        return ll