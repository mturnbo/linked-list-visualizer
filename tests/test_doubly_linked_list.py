import pytest
from classes.doubly_linked_list import DoublyLinkedList

@pytest.fixture(autouse=True)
def dll():
    return DoublyLinkedList()

@pytest.fixture(autouse=True)
def dll_123():
    dll = DoublyLinkedList()
    dll.append_values([1,2,3])
    return dll


def test_empty_list_initialization(dll):
    assert dll.size == 0
    assert dll.head is None
    assert dll.tail is None


def test_nonempty_list_initialization():
    initial_value = 123
    ll = DoublyLinkedList(initial_value)
    assert ll.size == 1
    assert ll.head.value == initial_value
    assert ll.tail.value == initial_value
    assert ll.head.next is None
    assert ll.tail.next is None


def test_list_append(dll):
    dll.append(1)
    assert dll.size == 1
    assert dll.head.value == 1
    assert dll.tail.value == 1

    dll.append(2)
    assert dll.size == 2
    assert dll.head.value == 1
    assert dll.tail.value == 2


def test_list_multiple_append(dll):
    vals = [1, 2, 3]
    for val in vals:
        dll.append(val)
        assert dll.head.value == vals[0]
        assert dll.tail.value == val

    assert dll.size == len(vals)


def test_prepend(dll):
    dll.append(2)
    dll.append(3)
    val = 1
    dll.prepend(val)
    assert dll.size == 3
    assert dll.head.value == val
    assert dll.head.next.value == 2


def test_get_node(dll_123):
    assert dll_123.get_node(1).value == 2


def test_insert(dll_123):
    dll_123.insert(1, 4)
    assert dll_123.get_node(1).value == 4


def test_replace(dll_123):
    dll_123.replace(1, 4)
    assert dll_123.get_node(1).value == 4

    dll_123.replace(2, 5)
    assert dll_123.get_node(2).value == 5


def test_trim(dll_123):
    assert dll_123.size == 3

    dll_123.trim()
    assert dll_123.size == 2


def test_contains(dll):
    dll.append(1)
    dll.append(2)
    assert dll.contains(1) is True
    assert dll.contains(2) is True
    assert dll.contains(3) is False


def test_remove(dll_123):
    dll_123.remove(1)
    assert dll_123.size == 2


def test_reverse(dll_123):
    dll_123.reverse()
    assert dll_123.head.value == 3
    assert dll_123.tail.value == 1


def test_str_empty_list(dll):
    result = str(dll)
    assert "Doubly Linked List | 0 Elements:\n[]" in result


def test_str_multiple_elements(dll_123):
    result = str(dll_123)
    assert "Doubly Linked List | 3 Elements:\n[1 \u21D4 2 \u21D4 3]" in result


def test_sort_merge():
    ll = DoublyLinkedList()
    values = [4, 2, 5, 1, 3]
    for value in values:
        ll.append(value)

    assert ll.sort(method=1) is True
    assert ll.get_values() == [1, 2, 3, 4, 5]
    assert ll.head.value == 1
    assert ll.tail.value == 5


def test_sort_insertion():
    ll = DoublyLinkedList()
    values = [4, 2, 5, 1, 3]
    for value in values:
        ll.append(value)

    assert ll.sort(method=2) is True
    assert ll.get_values() == [1, 2, 3, 4, 5]
    assert ll.head.value == 1
    assert ll.tail.value == 5
