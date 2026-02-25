import pytest
from classes.singly_linked_list import SinglyLinkedList

@pytest.fixture(autouse=True)
def sll():
    return SinglyLinkedList()

@pytest.fixture(autouse=True)
def sll_123():
    dll = SinglyLinkedList()
    dll.append_values([1,2,3])
    return dll

def test_empty_list_initialization(sll):
    assert sll.size == 0
    assert sll.head is None
    assert sll.tail is None


def test_nonempty_list_initialization():
    initial_value = 123
    ll = SinglyLinkedList(initial_value)
    assert ll.size == 1
    assert ll.head.value == initial_value
    assert ll.tail.value == initial_value
    assert ll.head.next is None
    assert ll.tail.next is None


def test_list_append(sll):
    sll.append(1)
    assert sll.size == 1
    assert sll.head.value == 1
    assert sll.tail.value == 1

    sll.append(2)
    assert sll.size == 2
    assert sll.head.value == 1
    assert sll.tail.value == 2


def test_list_multiple_append(sll):
    vals = [1, 2, 3]
    for val in vals:
        sll.append(val)
        assert sll.head.value == vals[0]
        assert sll.tail.value == val

    assert sll.size == len(vals)


def test_prepend(sll):
    sll.append(2)
    sll.append(3)
    val = 1
    sll.prepend(val)
    assert sll.size == 3
    assert sll.head.value == val
    assert sll.head.next.value == 2


def test_get_node(sll_123):
    assert sll_123.get_node(1).value == 2


def test_insert(sll_123):
    sll_123.insert(1, 4)
    assert sll_123.get_node(1).value == 4


def test_replace(sll_123):
    sll_123.replace(1, 4)
    assert sll_123.get_node(1).value == 4

    sll_123.replace(2, 5)
    assert sll_123.get_node(2).value == 5


def test_trim(sll_123):
    assert sll_123.size == 3

    sll_123.trim()
    assert sll_123.size == 2


def test_contains(sll_123):
    assert sll_123.contains(1) is True
    assert sll_123.contains(2) is True
    assert sll_123.contains(4) is False


def test_remove(sll_123):
    sll_123.remove(1)
    assert sll_123.size == 2


def test_reverse(sll_123):
    sll_123.reverse()
    assert sll_123.head.value == 3
    assert sll_123.tail.value == 1


def test_str_empty_list(sll):
    result = str(sll)
    assert "Singly Linked List | 0 Elements:\n[]" in result


def test_str_multiple_elements(sll_123):
    result = str(sll_123)
    assert "Singly Linked List | 3 Elements:\n[1 \u21D2 2 \u21D2 3]" in result


def test_has_cycle_methods():
    ll = SinglyLinkedList()
    ll.append_values([1, 2, 3, 4, 5])
    assert ll.has_cycle(method=1) is False
    assert ll.has_cycle(method=2) is False

    ll.create_cycle(2)
    assert ll.has_cycle(method=1) is True
    assert ll.has_cycle(method=2) is True


def test_get_cycle_start_index_methods():
    ll = SinglyLinkedList()
    ll.append_values([1, 2, 3, 4, 5])
    assert ll.get_cycle_start_index(method=1) is None
    assert ll.get_cycle_start_index(method=2) is None
    assert ll.get_cycle_start_index(method=3) is None

    ll.create_cycle(2)
    assert ll.get_cycle_start_index(method=1) == 2
    assert ll.get_cycle_start_index(method=2) == 2
    assert ll.get_cycle_start_index(method=3) == 2


def test_sort_merge():
    ll = SinglyLinkedList()
    values = [4, 2, 5, 1, 3]
    for value in values:
        ll.append(value)

    assert ll.sort(method=1) is True
    assert ll.get_values() == [1, 2, 3, 4, 5]
    assert ll.head.value == 1
    assert ll.tail.value == 5


def test_sort_insertion():
    ll = SinglyLinkedList()
    values = [4, 2, 5, 1, 3]
    for value in values:
        ll.append(value)

    assert ll.sort(method=2) is True
    assert ll.get_values() == [1, 2, 3, 4, 5]
    assert ll.head.value == 1
    assert ll.tail.value == 5
