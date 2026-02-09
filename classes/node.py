from dataclasses import dataclass
from typing import Any, Optional

@dataclass
class Node:
    """Class for a single node in a linked list."""
    value: Any
    prev = None
    next = None

    def __repr__(self):
        return f"Node[{self.value}]"
