import sys
from classes.node import Node
from typing import Optional
from constants import PRINT_ARROW_SINGLE as LINK_ARROW
from classes.linked_list_exceptions import *
from utils import filter_values

class SinglyLinkedList:
    def __init__(self, initial_node_value: Any = None):
        self.head: Node | None = Node(initial_node_value) if initial_node_value else None
        self.tail: Node | None = self.head
        self.size: int = 0 if initial_node_value is None else 1

        
    def __len__(self):
        return self.size


    def __str__(self):
        """
        Iterates through the linked list and appends node values to a list.
        Uses list size instead of current_node to avoid infinite loop when list has a cycle.
        """

        values = list(self.get_values(self.size))
        node_str = LINK_ARROW.join(map(str, values))
        return f"\nSingly Linked List | {self.size} Elements:\n[{node_str}]\n"



    def get_node(self, index: int) -> Node:
        """
        Returns node at index, or head/tail if out of bounds
        Time complexity: O(n)
        """

        if index <= 0: return self.head
        if index >= self.size - 1: return self.tail

        current_node = self.head
        for _ in range(index):
            current_node = current_node.next

        return current_node


    def get_values(self, count: Optional[int] = None) -> list[int | float | str | bool]:
        """
        Returns list of node values to count size, or head/tail if out of bounds
        Time complexity: O(n)
        """

        if count <= 0: return []
        if count is None: count = self.size
        index = min(count, self.size)
        values = []

        current_node = self.head
        for _ in range(index):
            values.append(current_node.value)
            current_node = current_node.next

        return values


    def append(self, value: int | float | str | bool):
        """
        Adds a new node to the end of the linked list.
        Time complexity: O(1)
        """

        try:
            if type(value) not in [int, float, str, bool]:
                raise ValueTypeException(value)
            if self.has_cycle():
                raise CycleDetectedException(sys._getframe().f_code.co_name)

            new_node = Node(value)
            if self.head:
                self.tail.next = new_node
            else:
                self.head = new_node
            self.tail = new_node
            self.size += 1
            return True
        except ValueTypeException as e:
            print(e)
        except CycleDetectedException as e:
            print(e)

        return False


    def append_values(self, values: list[int | float | str | bool]):
        """
        Adds multiple new nodes to the end of the linked list.
        Time complexity: O(n)
        """
        filtered_values = filter_values(values)
        for value in filtered_values:
            self.append(value)

        return len(filtered_values)


    def prepend(self, value: int | float | str | bool):
        """
        Adds a new node to the front of the linked list.
        Time complexity: O(1)
        """
        try:
            if type(value) not in [int, float, str, bool]:
                raise ValueTypeException(value)

            new_node = Node(value)
            new_node.next = self.head
            self.head = new_node
            self.size += 1
            return True
        except ValueTypeException as e:
            print(e)

        return False


    def prepend_values(self, values: list[int | float | str | bool]):
        """
        Adding multiple nodes to the front of the linked list.
        Preserves order
        Time complexity: O(n)
        """

        filtered_values = filter_values(values)
        for value in filtered_values[::-1]:
            self.prepend(value)

        return len(filtered_values)


    def insert(self, index: int, value: int | float | str | bool):
        """
        Inserts a new node at the specified index.
        Time complexity: O(n)
        """

        try:
            if type(value) not in [int, float, str, bool]:
                raise ValueTypeException(value)
            if self.has_cycle():
                raise CycleDetectedException(sys._getframe().f_code.co_name)

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
                return True
        except ValueTypeException as e:
            print(e)
        except CycleDetectedException as e:
            print(e)

        return False


    def replace(self, index: int, value: int | float | str | bool):
        """
        Replaces the value of a node at the specified index.
        Time complexity: O(n)
        """

        try:
            if type(value) not in [int, float, str, bool]:
                raise ValueTypeException(value)

            current_node = self.get_node(index)
            current_node.value = value
            return True
        except ValueTypeException as e:
            print(e)

        return False


    def trim(self):
        """
        Removes the last node from the list.
        Time complexity: O(n)
        """

        try:
            if self.has_cycle():
                raise CycleDetectedException(sys._getframe().f_code.co_name)

            self.tail = None
            current_node = self.get_node(self.size - 2)
            current_node.next = None
            self.tail = current_node
            self.size -= 1
            return True
        except CycleDetectedException as e:
            print(e)

        return False


    def contains(self, value: int | float | str | bool) -> bool:
        """
        Checks if the list contains a node with the specified value.
        Time complexity: O(n)
        """

        current_node = self.head
        while current_node:
            if current_node.value == value: return True
            current_node = current_node.next

        return False


    def remove(self, index: int):
        """
        Removes a node at the specified index.
        Time complexity: O(n)
        """

        if index < 0 or index >= self.size: return False
        if index == 0:
            self.head = self.head.next
            self.size -= 1
        elif index >= self.size - 1:
            self.trim()
        else:
            current_node = self.get_node(index - 1)
            current_node.next = current_node.next.next
            self.size -= 1

        return True


    def create_cycle(self, start: int):
        """
        Create a cycle in the linked list.
        Accepts start index.  Start index must be less than tail index.
        Example:
        1 → 2 → 3 → 4 → 5
                ↑       ↓
                ← ← ← ← ←
        Time complexity: O(1)
        """

        try:
            if self.has_cycle():
                raise CycleDetectedException(sys._getframe().f_code.co_name)
            if start > self.size:
                raise ValueError("Start index must come before tail index.")
            start_node = self.get_node(start)
            self.tail.next = start_node
            return True
        except ValueError as e:
            print(e)

        return False


    def cycle_index(self) -> int:
        """
        Finds the index of the first node in the cycle.
        Time complexity: O(n)?
        """
        if self.tail.next is not None:
            if self.tail.next == self.head:
                return 0
            else:
                node_list = []
                current_node = self.head
                for _ in range(self.size - 1):
                    node_list.append(current_node)
                    current_node = current_node.next
                return node_list.index(self.tail.next)

        return -1


    def has_cycle(self) -> bool:
        """
        Detects if the linked list has a cycle.
        Time complexity: O(n)
        """

        fast_runner = slow_runner = self.head
        while fast_runner and fast_runner.next:
            fast_runner = fast_runner.next.next
            slow_runner = slow_runner.next
            if fast_runner == slow_runner:
                return True
        return False



    def reverse(self):
        """
        Reverses the linked list in place.
        Time complexity: O(n)
        """
        if self.size <= 1: return False

        current_node = self.head
        prev_node = None
        while current_node:
            next_node = current_node.next
            current_node.next = prev_node
            prev_node = current_node
            current_node = next_node
        self.head, self.tail = self.tail, self.head
        return True


    def clear(self, iterate: bool = False):
        """
        Clears the linked list, removing all nodes and resetting size to 0.
        In Python, you can remove all nodes from a linked list by simply setting the head of the list to None.
        This makes the entire list unreachable, and Python's garbage collector automatically reclaims the memory.
        An iterative option is included. This method is useful for understanding how deletion works in languages
        that require manual memory management,
        """
        if iterate:
            # Time complexity: O(n)
            current = self.head
            while current:
                # Store the next node to avoid losing the reference
                next_node = current.next
                current = next_node
            self.head = None
        else:
            # Time complexity: O(1)
            self.head = self.tail = None
            self.size = 0

        return True


    def show(self):
        print(self)
