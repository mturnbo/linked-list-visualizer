import pytest
from main import main
from classes.linked_list import LinkedList
from classes.singly_linked_list import SinglyLinkedList
from classes.doubly_linked_list import DoublyLinkedList


def test_main_raises_without_values_or_ops_file(monkeypatch):
    monkeypatch.setattr("sys.argv", ["main.py", "singly", "print"])
    with pytest.raises(ValueError, match="Must specify either values or operations file"):
        main()

def test_doubly_lltype_creates_singly_linked_list():
    ll = LinkedList.create("singly")
    assert isinstance(ll, SinglyLinkedList)

def test_doubly_lltype_creates_doubly_linked_list():
    ll = LinkedList.create("doubly")
    assert isinstance(ll, DoublyLinkedList)
