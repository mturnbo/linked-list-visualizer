from classes.node import Node
from typing import Any, Optional

class SinglyLinkedList:
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


    def get_node(self, index: int) -> Node:
        if index <= 0: return self.head
        if index >= self.size - 1: return self.tail

        current_node = self.head
        for _ in range(index):
            current_node = current_node.next

        return current_node


    def append(self, value: int | float | str | bool):
        new_node = Node(value)
        if self.head:
            self.tail.next = new_node
        else:
            self.head = new_node
        self.tail = new_node
        self.size += 1


    def append_values(self, values: list[int | float | str | bool]):
        for value in values:
            self.append(value)


    def prepend(self, value: int | float | str | bool):
        new_node = Node(value)
        new_node.next = self.head
        self.head = new_node
        self.size += 1


    def insert(self, index: int, value: int | float | str | bool):
        if index == 0:
            self.prepend(value)
        elif index >= self.size:
            self.append(value)
        else:
            new_node = Node(value)
            current_node = self.get_node(index -1)
            new_node.next = current_node.next
            current_node.next = new_node
            self.size += 1


    def replace(self, index: int, value: int | float | str | bool):
        current_node = self.get_node(index)
        current_node.value = value


    def trim(self):
        current_node = self.get_node(self.size - 2)
        current_node.next = None
        self.tail = current_node
        self.size -= 1


    def contains(self, value: int | float | str | bool) -> bool:
        current_node = self.head
        while current_node:
            if current_node.value == value: return True
            current_node = current_node.next

        return False


    def remove(self, index: int):
        if index == 0:
            self.head = self.head.next
            self.size -= 1
        elif index >= self.size - 1:
            self.trim()
        else:
            current_node = self.get_node(index - 1)
            current_node.next = current_node.next.next
            self.size -= 1


    def reverse(self):
        current_node = self.head
        prev_node = None
        while current_node:
            next_node = current_node.next
            current_node.next = prev_node
            prev_node = current_node
            current_node = next_node
        self.head, self.tail = self.tail, self.head


    def show(self):
        print(self)
