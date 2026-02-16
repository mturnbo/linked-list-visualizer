import argparse
from classes.singly_linked_list import LinkedList
from typing import List, Tuple

from visualization import DEFAULT_HEIGHT, build_linked_list_from_values
from visualization import DEFAULT_INTERVAL
from visualization import DEFAULT_VALUES
from visualization import DEFAULT_WIDTH
from visualization import run_visualization


def parse_values(raw_values: str) -> List[int | float | str | bool]:
    if not raw_values:
        return DEFAULT_VALUES
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


def build_linked_list_from_ops(operations: List[Tuple[str, List[int | float | str | bool], str]]):
    ll = LinkedList()
    for op in operations:
        match op[0]:
            case "append":
                ll.append(op[1][0])
            case "prepend":
                ll.prepend(op[1][0])
            case "insert":
                ll.insert(op[1][0], op[1][1])
            case "remove":
                ll.remove(op[1][0])
            case "replace":
                ll.replace(op[1][0], op[1][1])
            case _:
                raise ValueError(f"Unknown operation type '{op[0]}' in operations file.")

    return ll


def main():
    parser = argparse.ArgumentParser(description="Visualize a linked list with pygame.")
    parser.add_argument("display", choices=["print", "animate"], help="Print to command line or visualize with pygame.")
    parser.add_argument("--values", type=str, default="", help="Comma-separated list of node values.")
    parser.add_argument("--ops-file", type=str, default="", help="Path to operations text file.")
    parser.add_argument("--interval", type=float, default=DEFAULT_INTERVAL, help="Seconds per operation.")
    parser.add_argument("--arrow-interval", type=float, default=DEFAULT_INTERVAL, help="Seconds for arrow animation.")
    parser.add_argument("--width", type=int, default=DEFAULT_WIDTH, help="Window width in pixels.")
    parser.add_argument("--height", type=int, default=DEFAULT_HEIGHT, help="Window height in pixels.")
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
        run_visualization(
            values=values,
            operations=operations,
            interval=args.interval,
            arrow_interval=args.arrow_interval,
            width=args.width,
            height=args.height,
        )
    else:
        if values:
            ll = build_linked_list_from_values(values)
        else:
            ll = build_linked_list_from_ops(operations)
        ll.show()


if __name__ == "__main__":
    main()
