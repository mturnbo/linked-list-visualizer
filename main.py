import argparse
from typing import List, Tuple

from visualization import DEFAULT_HEIGHT
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


def main():
    parser = argparse.ArgumentParser(description="Visualize a linked list with pygame.")
    parser.add_argument("--values", type=str, default="", help="Comma-separated list of node values.")
    parser.add_argument("--operations-file", type=str, default="", help="Path to operations text file.")
    parser.add_argument("--interval", type=float, default=DEFAULT_INTERVAL, help="Seconds per operation.")
    parser.add_argument("--arrow-interval", type=float, default=0.5, help="Seconds for arrow animation.")
    parser.add_argument("--width", type=int, default=DEFAULT_WIDTH, help="Window width in pixels.")
    parser.add_argument("--height", type=int, default=DEFAULT_HEIGHT, help="Window height in pixels.")
    args = parser.parse_args()

    if args.operations_file and not args.values:
        values = []
    else:
        values = parse_values(args.values)
    operations = parse_operations(args.operations_file)
    if not operations:
        operations = [("append", [value], f"append {value}") for value in values]
        values = []

    run_visualization(
        values=values,
        operations=operations,
        interval=args.interval,
        arrow_interval=args.arrow_interval,
        width=args.width,
        height=args.height,
    )


if __name__ == "__main__":
    main()
