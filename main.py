import argparse
from classes.linked_list import LinkedList
from typing import List, Tuple
from classes.visualizer import LinkedListVisualizer


def parse_values(raw_values: str) -> List[int | float | str | bool]:
    if not raw_values:
        return []
    try:
        return [value.strip() for value in raw_values.split(",") if value.strip()]
    except ValueError as exc:
        raise ValueError("Values must be a comma-separated list of int | float | str | bool") from exc


def parse_operations(path: str) -> List[Tuple[str, List[int | float | str | bool], str]]:
    operations = []
    if not path:
        return operations
    with open(path, "r", encoding="utf-8") as handle:
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
            else:
                raise ValueError(f"Line {line_number}: unknown command '{command}'.")
    return operations


def main():
    parser = argparse.ArgumentParser(description="Visualize a linked list with pygame.")
    parser.add_argument("display", choices=["print", "animate"], help="Print to command line or visualize with pygame.")
    parser.add_argument("--values", type=str, default="", help="Comma-separated list of node values.")
    parser.add_argument("--ops-file", type=str, default="", help="Path to operations text file.")
    parser.add_argument("--node-interval", type=float, help="Seconds per operation.")
    parser.add_argument("--arrow-interval", type=float, help="Seconds for arrow animation.")
    parser.add_argument("--width", type=int, help="Window width in pixels.")
    parser.add_argument("--height", type=int, help="Window height in pixels.")
    args = parser.parse_args()

    values = operations = []
    if args.values and not args.ops_file:
        values = parse_values(args.values)
        operations = [("append", [value], f"append {value}") for value in values]
    elif args.ops_file:
        operations = parse_operations(args.ops_file)
    else:
        raise ValueError("Must specify either values or operations file.")

    if args.display == "animate":
        llv = LinkedListVisualizer(
            operations=operations
        )
        llv.configure(vars(args))
        llv.display()
    else:
        if values:
            ll = LinkedList.build_from_values("singly", values)
        else:
            ll = LinkedList.build_from_ops("singly", operations)
        ll.show()


if __name__ == "__main__":
    main()
