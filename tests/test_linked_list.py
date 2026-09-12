from classes.linked_list import LinkedList
from linked_list import DoublyLinkedList as PackageDoublyLinkedList
from linked_list import SinglyLinkedList as PackageSinglyLinkedList


def test_create_uses_package_singly_linked_list():
    ll = LinkedList.create("singly")

    assert isinstance(ll, PackageSinglyLinkedList)


def test_create_uses_package_doubly_linked_list():
    ll = LinkedList.create("doubly")

    assert isinstance(ll, PackageDoublyLinkedList)


def test_build_linked_list_from_values_coerces_cli_values():
    values = ["1", "2.5", "true", "word"]
    ll = LinkedList.build_from_values("singly", values)

    assert ll.get_values() == [1, 2.5, True, "word"]

def test_create_linked_list():
    ll = LinkedList.create("singly")
    assert ll.size == 0
    assert ll.head is None
    assert ll.tail is None


def test_build_linked_list_from_values():
    values = ["a", "b", "c"]
    ll = LinkedList.build_from_values("singly", values)
    assert ll.size == 3


def test_build_linked_list_from_ops_append():
    operations = [
        ("append", ["a"], "append a"),
        ("append", ["b"], "append b"),
        ("append", ["c"], "append c"),
    ]
    ll = LinkedList.build_from_ops("singly", operations)
    assert ll.size == 3
    assert ll.head.value == "a"
    assert ll.get_node(1).value == "b"
    assert ll.tail.value == "c"


def test_build_linked_list_from_ops_prepend():
    operations = [
        ("append", ["b"], "append b"),
        ("prepend", ["a"], "prepend a"),
    ]
    ll = LinkedList.build_from_ops("singly", operations)
    assert ll.size == 2
    assert ll.head.value == "a"
    assert ll.tail.value == "b"


def test_build_linked_list_from_ops_insert():
    operations = [
        ("append", ["a"], "append a"),
        ("append", ["c"], "append c"),
        ("insert", [1, "b"], "insert 1 b"),
    ]
    ll = LinkedList.build_from_ops("singly", operations)
    assert ll.size == 3
    assert ll.head.value == "a"
    assert ll.get_node(1).value == "b"
    assert ll.tail.value == "c"


def test_build_linked_list_from_ops_remove():
    operations = [
        ("append", ["a"], "append a"),
        ("append", ["b"], "append b"),
        ("append", ["c"], "append c"),
        ("remove", [1], "remove 1"),
    ]
    ll = LinkedList.build_from_ops("singly", operations)
    assert ll.size == 2
    assert ll.head.value == "a"
    assert ll.tail.value == "c"
