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
