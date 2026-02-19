from classes.node import Node
from classes.singly_linked_list import SinglyLinkedList
from constants import PRINT_ARROW_DOUBLE as LINK_ARROW
from classes.linked_list_exceptions import *

class DoublyLinkedList(SinglyLinkedList):
    def __init__(self, initial_node_value: int | float | str | bool = None):
        super().__init__(initial_node_value)


    def __str__(self):
        """
        Iterates through the linked list and appends node values to a list.
        Uses list size instead of current_node to avoid infinite loop when list has a cycle.
        """

        values = list(self.get_values(self.size))
        node_str = LINK_ARROW.join(map(str, values))
        return f"\nDoubly Linked List | {self.size} Elements:\n[{node_str}]\n"


    def get_node(self, index: int):
        """
        Retrieves a node at the specified index.
        Time complexity: O(n)
        """

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


    def append(self, value: int | float | str | bool):
        """
        Appends a new node with the specified value to the end of the list.
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
                new_node.prev = self.tail
            else:
                self.head = new_node
            self.tail = new_node
            self.size += 1
        except ValueTypeException as e:
            print(e)
        except CycleDetectedException as e:
            print(e)


    def prepend(self, value: int | float | str | bool):
        """
        Prepends a new node with the specified value to the beginning of the list.
        Time complexity: O(1)
        """

        try:
            if type(value) not in [int, float, str, bool]:
                raise ValueTypeException(value)

            new_node = Node(value)
            if self.head:
                new_node.next = self.head
                self.head.prev = new_node
            self.head = new_node
            self.size += 1
        except ValueTypeException as e:
            print(e)


    def remove(self, index: int):
        """
        Removes the node at the specified index.
        Time complexity: O(n)
        """
        if index < 0 or index >= self.size: return
        if index == 0:
            self.head = self.head.next
            self.head.prev = None
        elif index >= self.size - 1:
            self.tail = self.tail.prev
            self.tail.next = None
        else:
            current_node = self.get_node(index -1)
            next_node = current_node.next.next
            current_node.next = next_node
            next_node.prev = current_node
        self.size -= 1


    def contains(self, value: int):
        """
        Determines if the list contains a node with the specified value.
        Time complexity: O(n)
        """

        forward = self.head
        backward = self.tail

        for _ in range((self.size // 2) + 1):
            if forward.value == value or backward.value == value: return True
            forward = forward.next
            backward = backward.prev

        return False


    def reverse(self):
        """
        Reverses the order of nodes in the list.
        Time complexity: O(n)
        """

        current_node = self.head
        while current_node:
            current_node.prev, current_node.next = current_node.next, current_node.prev
            current_node = current_node.prev
        self.head, self.tail = self.tail, self.head