from classes.node import Node

def test_node_links_like_linked_list_usage():
    first = Node(1)
    second = Node(2)
    third = Node(3)

    # Link nodes as a doubly linked list would.
    first.next = second
    second.prev = first
    second.next = third
    third.prev = second

    assert first.prev is None
    assert first.next is second
    assert second.prev is first
    assert second.next is third
    assert third.prev is second
    assert third.next is None


def test_node_repr_shows_value():
    node = Node("x")
    assert repr(node) == "Node[x]"
