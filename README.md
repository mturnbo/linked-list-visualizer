# Linked List Visualization
**Linked List Visualizer**
This project visualizes linked list operations (append, prepend, insert, remove, replace) using a pygame UI. It supports parsing command-line arguments for initial values, window sizing, and animation timing, plus loading operations from a text file.

**Requirements**
- Python 3.10+
- `pygame` installed in your environment

**Install**
Create/activate a virtual environment, then install dependencies:
```bash
python -m venv .venv
source .venv/bin/activate
pip install pygame
```

**Usage**
Run with a comma-separated list of values (defaults to `1,2,3,4,5`):
```bash
python main.py --values 1,2,3,4,5
```

Run from an operations file (examples included: `ops1.txt`, `ops2.txt`):
```bash
python main.py --operations-file examples/ops1.txt
```

If an operations file is provided and `--values` is omitted, the visualization starts from an empty list and only replays the operations.

**Arguments**
- `--values`: Comma-separated list of node values (default uses `DEFAULT_VALUES`).
- `--operations-file`: Path to a text file of operations (see format below).
- `--interval`: Seconds per operation (default `0.8`).
- `--arrow-interval`: Seconds for arrow animation (default `0.5`).
- `--width`: Window width in pixels (default `1000`).
- `--height`: Window height in pixels (default `500`).

**Operations File Format**
Each line is a single operation. Blank lines and lines starting with `#` are ignored.
- `append <value>`
- `prepend <value>`
- `insert <index> <value>`
- `remove <index>` (alias: `delete`)
- `replace <index> <value>`

**Example: `ops1.txt`**
```text
append 2
append 4
append 6
append 7
append 8
append 10
append 15
append 20
append 22
append 26
append 27
append 50
prepend 1
insert 3 2
remove 1
```

**Example: `ops2.txt`**
```text
append 2
append 4
append 6
append 7
append 8
append a
append b
append c
append 22
append 26
append 27
append 50
prepend 1
insert 3 2
replace 2 33
replace 5 44
```

**Screenshot**
![Linked List Visualizer](docs/LinkedListVisualizer_Screenshot1.png)
