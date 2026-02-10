from classes.node import Node
from classes.singly_linked_list import LinkedList
from typing import Any, Optional

class DoublyLinkedList(LinkedList):
    def __init__(self, initial_node_value: Any = None):
        super().__init__(initial_node_value)


    def __str__(self):
        current_node = self.head
        node_list = []
        while current_node:
            node_list.append(current_node.value)
            current_node = current_node.next
        node_str = " \u21D4 ".join(map(str, node_list))
        return f"{self.size} Elements:[{self.head.value}][{self.tail.value}]: [{node_str}]"


    def get_node(self, index: int):
        # Choose traversal direction based on index proximity

        if index <= 0: return self.head
        if index >= self.size - 1: return self.tail

        if index <= self.size // 2:
            current_node = self.head
            for _ in range(index):
                current_node = current_node.next
        else:
            current_node = self.tail
            for _ in range(self.size - index):
                current_node = current_node.prev

        return current_node


    def append(self, value: int):
        new_node = Node(value)
        if self.head:
            self.tail.next = new_node
            new_node.prev = self.tail
        else:
            self.head = new_node
        self.tail = new_node
        self.size += 1


    def prepend(self, value: int):
        new_node = Node(value)
        if self.head:
            new_node.next = self.head
            self.head.prev = new_node
        self.head = new_node
        self.size += 1