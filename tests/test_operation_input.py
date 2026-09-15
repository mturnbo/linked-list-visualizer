from pathlib import Path

import pytest

from classes.operation_input import OperationInputError, OperationQueue


def labels(queue: OperationQueue) -> list[str]:
    return [operation[2] for operation in queue.operations]


def test_operation_queue_adds_supported_operations_with_coerced_values() -> None:
    queue = OperationQueue()

    queue.add_operation("append", value_text="1")
    queue.add_operation("prepend", value_text="true")
    queue.add_operation("insert", value_text="2.5", index_text="1")
    queue.add_operation("replace", value_text="word", index_text="0")
    queue.add_operation("remove", index_text="2")
    queue.add_operation("reverse")
    queue.add_operation("sort", sort_method_text="2")
    queue.add_operation("cycle", index_text="0")
    queue.add_operation("has_cycle")

    assert queue.operations == [
        ("append", [1], "append 1"),
        ("prepend", [True], "prepend True"),
        ("insert", [1, 2.5], "insert 1 2.5"),
        ("replace", [0, "word"], "replace 0 word"),
        ("remove", [2], "remove 2"),
        ("reverse", [], "reverse"),
        ("sort", [2], "sort 2"),
        ("cycle", [0], "cycle 0"),
        ("has_cycle", [], "has_cycle"),
    ]


@pytest.mark.parametrize("operation", ["append", "prepend"])
def test_operation_queue_requires_values(operation: str) -> None:
    queue = OperationQueue()

    with pytest.raises(OperationInputError, match="value"):
        queue.add_operation(operation, value_text="")


@pytest.mark.parametrize("operation", ["insert", "replace"])
def test_operation_queue_requires_indexes_and_values(operation: str) -> None:
    queue = OperationQueue()

    with pytest.raises(OperationInputError, match="index"):
        queue.add_operation(operation, value_text="7", index_text="")

    with pytest.raises(OperationInputError, match="value"):
        queue.add_operation(operation, value_text="", index_text="0")


@pytest.mark.parametrize("operation", ["remove", "cycle"])
def test_operation_queue_requires_integer_indexes(operation: str) -> None:
    queue = OperationQueue()

    with pytest.raises(OperationInputError, match="integer index"):
        queue.add_operation(operation, index_text="nope")


def test_operation_queue_clear_resets_operations() -> None:
    queue = OperationQueue()
    queue.add_operation("append", value_text="1")

    queue.add_operation("clear")

    assert queue.operations == []


def test_operation_queue_loads_operations_file(tmp_path: Path) -> None:
    ops_file = tmp_path / "ops.txt"
    ops_file.write_text("append 1\ninsert 0 two\nremove 1\n", encoding="utf-8")
    queue = OperationQueue()

    queue.load_operations_file(ops_file)

    assert labels(queue) == ["append 1", "insert 0 two", "remove 1"]


def test_operation_queue_rejects_unknown_operations() -> None:
    queue = OperationQueue()

    with pytest.raises(OperationInputError, match="Unsupported operation"):
        queue.add_operation("spin")
