import sys
from classes.node import Node
from classes.singly_linked_list import SinglyLinkedList
from constants import PRINT_ARROW_DOUBLE as LINK_ARROW, PRINT_COLOR, RESET
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
        header_str = f"Doubly Linked List | {self.size} Elements:"
        node_str = f"[{LINK_ARROW.join(map(str, values))}]"

        return f"\n{PRINT_COLOR}{header_str}\n{node_str}{RESET}\n"


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
            if not value:
                raise EmptyValueException(value)
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
            return True
        except EmptyValueException as e:
            print(e)
        except ValueTypeException as e:
            print(e)
        except CycleDetectedException as e:
            print(e)

        return False


    def prepend(self, value: int | float | str | bool):
        """
        Prepends a new node with the specified value to the beginning of the list.
        Time complexity: O(1)
        """

        try:
            if not value:
                raise EmptyValueException(value)
            if type(value) not in [int, float, str, bool]:
                raise ValueTypeException(value)

            new_node = Node(value)
            if self.head:
                new_node.next = self.head
                self.head.prev = new_node
            self.head = new_node
            self.size += 1
            return True
        except EmptyValueException as e:
            print(e)
        except ValueTypeException as e:
            print(e)

        return False


    def remove(self, index: int):
        """
        Removes the node at the specified index.
        Time complexity: O(n)
        """
        if index < 0 or index >= self.size: return False
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
        return True


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


    def create_cycle(self, start: int):
        """Overriding parent method because doubly linked list cannot have a cycle."""
        return False


    def has_cycle(self):
        """Overriding parent method because doubly linked list cannot have a cycle."""
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
        return True


    def sort(self, method: int = 1) -> bool:
        """
        Sorts the linked list in place.
        method=1: Merge sort
        method=2: Insertion sort
        """

        try:
            if self.has_cycle():
                raise CycleDetectedException(sys._getframe().f_code.co_name)
            if self.size <= 1:
                return True

            if method == 1:
                def split(head: Node | None):
                    if head is None or head.next is None:
                        return head, None
                    slow = head
                    fast = head
                    prev = None
                    while fast and fast.next:
                        prev = slow
                        slow = slow.next
                        fast = fast.next.next
                    if prev:
                        prev.next = None
                    if slow:
                        slow.prev = None
                    return head, slow

                def merge(left: Node | None, right: Node | None):
                    if left is None:
                        tail = right
                        while tail and tail.next:
                            tail = tail.next
                        return right, tail
                    if right is None:
                        tail = left
                        while tail and tail.next:
                            tail = tail.next
                        return left, tail

                    if left.value <= right.value:
                        head = left
                        left = left.next
                    else:
                        head = right
                        right = right.next
                    head.prev = None
                    tail = head
                    tail.next = None

                    while left and right:
                        if left.value <= right.value:
                            tail.next = left
                            left.prev = tail
                            tail = left
                            left = left.next
                        else:
                            tail.next = right
                            right.prev = tail
                            tail = right
                            right = right.next
                        tail.next = None

                    remainder = left if left else right
                    if remainder:
                        remainder.prev = tail
                    tail.next = remainder
                    while tail.next:
                        tail = tail.next
                    return head, tail

                def merge_sort(head: Node | None):
                    if head is None or head.next is None:
                        return head, head
                    left, right = split(head)
                    left_head, left_tail = merge_sort(left)
                    right_head, right_tail = merge_sort(right)
                    return merge(left_head, right_head)

                head, tail = merge_sort(self.head)
                self.head = head
                self.tail = tail
                if self.head:
                    self.head.prev = None
                if self.tail:
                    self.tail.next = None
                return True

            if method == 2:
                sorted_head = None
                sorted_tail = None
                current = self.head
                while current:
                    next_node = current.next
                    current.prev = None
                    current.next = None
                    if sorted_head is None:
                        sorted_head = current
                        sorted_tail = current
                    elif current.value <= sorted_head.value:
                        current.next = sorted_head
                        sorted_head.prev = current
                        sorted_head = current
                    else:
                        search = sorted_head
                        while search.next and search.next.value <= current.value:
                            search = search.next
                        current.next = search.next
                        current.prev = search
                        if search.next:
                            search.next.prev = current
                        else:
                            sorted_tail = current
                        search.next = current
                    current = next_node

                self.head = sorted_head
                self.tail = sorted_tail
                return True

            raise ValueError("Method must be 1 (merge) or 2 (insertion).")
        except CycleDetectedException as e:
            print(e)
        except ValueError as e:
            print(e)

        return False
