import pytest
from main import build_linked_list_from_ops, main


def test_build_linked_list_from_ops_append():
    operations = [
        ("append", ["a"], "append a"),
        ("append", ["b"], "append b"),
        ("append", ["c"], "append c"),
    ]
    ll = build_linked_list_from_ops(operations)
    assert ll.size == 3
    assert ll.head.value == "a"
    assert ll.get_node(1).value == "b"
    assert ll.tail.value == "c"


def test_build_linked_list_from_ops_prepend():
    operations = [
        ("append", ["b"], "append b"),
        ("prepend", ["a"], "prepend a"),
    ]
    ll = build_linked_list_from_ops(operations)
    assert ll.size == 2
    assert ll.head.value == "a"
    assert ll.tail.value == "b"


def test_build_linked_list_from_ops_insert():
    operations = [
        ("append", ["a"], "append a"),
        ("append", ["c"], "append c"),
        ("insert", [1, "b"], "insert 1 b"),
    ]
    ll = build_linked_list_from_ops(operations)
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
    ll = build_linked_list_from_ops(operations)
    assert ll.size == 2
    assert ll.head.value == "a"
    assert ll.tail.value == "c"


def test_main_raises_without_values_or_ops_file(monkeypatch):
    monkeypatch.setattr("sys.argv", ["main.py", "print"])
    with pytest.raises(ValueError, match="Must specify either values or operations file"):
        main()
