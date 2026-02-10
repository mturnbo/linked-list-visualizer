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


def test_prepend():
    ll = LinkedList()
    ll.append(2)
    ll.append(3)
    val = 1
    ll.prepend(val)
    assert ll.size == 3
    assert ll.head.value == val
    assert ll.head.next.value == 2


def test_get_node():
    ll = LinkedList()
    ll.append(1)
    ll.append(2)
    ll.append(3)
    assert ll.get_node(1).value == 2

def test_insert():
    ll = LinkedList()
    ll.append(1)
    ll.append(2)
    ll.append(3)
    ll.insert(4, 1)
    assert ll.get_node(1).value == 4


def test_replace():
    ll = LinkedList()
    ll.append(1)
    ll.append(2)
    ll.append(3)

    ll.replace(1, 4)
    assert ll.get_node(1).value == 4

    ll.replace(2, 5)
    assert ll.get_node(2).value == 5


def test_trim():
    ll = LinkedList()
    ll.append(1)
    ll.append(2)
    ll.append(3)
    assert ll.size == 3

    ll.trim()
    assert ll.size == 2


def test_contains():
    ll = LinkedList()
    ll.append(1)
    ll.append(2)
    assert ll.contains(1) is True
    assert ll.contains(2) is True
    assert ll.contains(3) is False


def test_remove():
    ll = LinkedList()
    ll.append(1)
    ll.append(2)
    ll.remove(1)
    assert ll.size == 1
