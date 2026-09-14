import argparse
from pathlib import Path

from constants import DEFAULT_VALUES
from classes.linked_list import LinkedList


def parse_values(raw_values: str) -> list[int | float | str | bool]:
    """Parse raw comma-separated CLI values.

    Args:
        raw_values: Raw comma-separated values.

    Returns:
        String values trimmed for later visualizer coercion.

    Raises:
        ValueError: If values cannot be parsed.
    """
    if not raw_values:
        return []
    try:
        return [value.strip() for value in raw_values.split(",") if value.strip()]
    except ValueError as exc:
        raise ValueError("Values must be a comma-separated list of int | float | str | bool") from exc


def parse_operations(path: str) -> list[tuple[str, list[int | float | str | bool], str]]:
    """Parse visualizer operations from a text file.

    Args:
        path: Path to an operations file.

    Returns:
        Operation tuples of command, arguments, and original text.

    Raises:
        ValueError: If an operation has invalid syntax.
    """
    operations = []
    if not path:
        return operations
    with Path(path).open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            parts = stripped.split()
            command = parts[0].lower()
            args = parts[1:]
            if command in {"append", "prepend"}:
                if len(args) != 1:
                    raise ValueError(f"Line {line_number}: {command} requires 1 value.")
                operations.append((command, [args[0]], stripped))
            elif command == "insert":
                if len(args) != 2:
                    raise ValueError(f"Line {line_number}: insert requires a value and index.")
                operations.append((command, [int(args[0]), args[1]], stripped))
            elif command in {"remove", "delete"}:
                if len(args) != 1:
                    raise ValueError(f"Line {line_number}: {command} requires an index.")
                operations.append(("remove", [int(args[0])], stripped))
            elif command == "replace":
                if len(args) != 2:
                    raise ValueError(f"Line {line_number}: replace requires a value and index.")
                operations.append(("replace", [int(args[0]), args[1]], stripped))
            elif command == "cycle":
                if len(args) != 1:
                    raise ValueError(f"Line {line_number}: create cycle requires starting index.")
                operations.append(("cycle", [int(args[0])], stripped))
            elif command == "has_cycle":
                operations.append(("has_cycle", [], stripped))
            elif command == "sort":
                if len(args) > 1:
                    raise ValueError(f"Line {line_number}: sort accepts optional method only.")
                method = int(args[0]) if args else 1
                operations.append(("sort", [method], stripped))
            else:
                raise ValueError(f"Line {line_number}: unknown command '{command}'.")

    return operations


def main() -> None:
    """Run the linked list visualizer CLI."""
    parser = argparse.ArgumentParser(description="Visualize a linked list with pygame.")
    parser.add_argument("ll_type", choices=["singly", "doubly"], default = "singly", help="Linked List type.  Singly or Doubly.")
    parser.add_argument("display", choices=["print", "animate"], help="Print to command line or visualize with pygame.")
    parser.add_argument("--values", type=str, default="", help="Comma-separated list of node values.")
    parser.add_argument("--ops-file", type=str, default="", help="Path to operations text file.")
    parser.add_argument("--node-interval", type=float, help="Seconds per operation.")
    parser.add_argument("--arrow-interval", type=float, help="Seconds for arrow animation.")
    parser.add_argument("--width", type=int, help="Window width in pixels.")
    parser.add_argument("--height", type=int, help="Window height in pixels.")
    args = parser.parse_args()

    try:
        if not args.values and not args.ops_file:
            raise ValueError("Must specify either values or operations file")
        values = operations = []
        if args.values and not args.ops_file:
            values = parse_values(args.values)
            operations = [("append", [value], f"append {value}") for value in values]
        elif args.ops_file:
            operations = parse_operations(args.ops_file)
        else:
            values = DEFAULT_VALUES
            operations = [("append", [value], f"append {value}") for value in values]

        if args.display == "animate":
            from classes.visualizer import LinkedListVisualizer

            llv = LinkedListVisualizer(
                ll_type=args.ll_type,
                operations=operations
            )
            llv.configure(vars(args))
            llv.display()
        else:
            if values:
                ll = LinkedList.build_from_values(args.ll_type, values)
            else:
                ll = LinkedList.build_from_ops(args.ll_type, operations)
            ll.show()
    except ValueError as e:
        print(e)

if __name__ == "__main__":
    main()
