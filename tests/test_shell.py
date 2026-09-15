from classes.linked_list import LinkedList
from shell import LinkedListShell


def test_shell_animate_uses_pyside6_visualizer(monkeypatch):
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
    shell = object.__new__(LinkedListShell)
    shell.ll = LinkedList.create("singly")
    shell.operations = [("append", [1], "append 1")]

    shell.do_animate("")

    assert launched["ll_type"] == "singly"
    assert launched["operations"] == [("append", [1], "append 1")]
    assert launched["params"] == {"width": 1200, "height": 800}
    assert launched["displayed"]
