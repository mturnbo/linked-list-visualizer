from dataclasses import dataclass

@dataclass
class Node:
    """Class for a single node in a linked list."""
    value: int | float | str | bool
    prev = None
    next = None

    def __repr__(self):
        return f"Node[{self.value}]"
