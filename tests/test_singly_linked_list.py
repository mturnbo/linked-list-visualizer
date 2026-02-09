from classes.singly_linked_list import LinkedList

def test_empty_list_initialization():
    ll = LinkedList()
    assert ll.size == 0
    assert ll.head is None
    assert ll.tail is None


def test_nonempty_list_initialization():
    initial_value = 123
    ll = LinkedList(initial_value)
    assert ll.size == 1
    assert ll.head.value == initial_value
    assert ll.tail.value == initial_value
    assert ll.head.next is None
    assert ll.tail.next is None


def test_list_append():
    ll = LinkedList()
    val = 1
    ll.append(val)
    assert ll.size == 1
    assert ll.head.value == val
    assert ll.tail.value == val


def test_list_multiple_append():
    ll = LinkedList()
    vals = [1, 2, 3]
    for val in vals:
        ll.append(val)
        assert ll.head.value == vals[0]
        assert ll.tail.value == val

    assert ll.size == len(vals)