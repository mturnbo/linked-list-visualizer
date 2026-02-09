from classes.node import Node
from typing import Any, Optional

class LinkedList:
    def __init__(self, initial_node_value: Any = None):
        self.head: Node = Node(initial_node_value) if initial_node_value else None
        self.tail: Node = self.head
        self.size: int = 0 if initial_node_value is None else 1

        
    def __len__(self):
        return self.size


    def __str__(self):
        current_node = self.head
        node_list = []
        while current_node:
            node_list.append(current_node.value)
            current_node = current_node.next
        node_str = " \u21D2 ".join(map(str, node_list))
        return f"{self.size} Elements: [{node_str}]"


    def append(self, value: Any):
        new_node = Node(value)
        if self.head:
            self.tail.next = new_node
        else:
            self.head = new_node
        self.tail = new_node
        self.size += 1


    def show(self):
        print(self)
