from classes.doubly_linked_list import DoublyLinkedList
from classes.linked_list import LinkedList
from classes.singly_linked_list import SinglyLinkedList
from main import main


def test_main_raises_without_values_or_ops_file(monkeypatch, capsys):
    monkeypatch.setattr("sys.argv", ["main.py", "singly", "print"])
    main()
    captured = capsys.readouterr()
    assert "Must specify either values or operations file" in captured.out

def test_doubly_lltype_creates_singly_linked_list():
    ll = LinkedList.create("singly")
    assert isinstance(ll, SinglyLinkedList)

def test_doubly_lltype_creates_doubly_linked_list():
    ll = LinkedList.create("doubly")
    assert isinstance(ll, DoublyLinkedList)


def test_animate_display_uses_pyside6_visualizer(monkeypatch):
    launched = {}

    class FakePySideVisualizer:
        def __init__(self, ll_type, operations):
            launched["ll_type"] = ll_type
            launched["operations"] = operations

        def configure(self, params):
            launched["params"] = params

        def display(self):
            launched["displayed"] = True

    monkeypatch.setattr(
        "classes.pyside6_visualizer.LinkedListPySideVisualizer",
        FakePySideVisualizer,
    )
    monkeypatch.setattr("sys.argv", ["main.py", "singly", "animate", "--values", "1,2"])

    main()

    assert launched["ll_type"] == "singly"
    assert launched["operations"] == [("append", ["1"], "append 1"), ("append", ["2"], "append 2")]
    assert launched["displayed"]
