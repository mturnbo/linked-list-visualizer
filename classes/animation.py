import math
from dataclasses import dataclass
from typing import Any

from classes.linked_list import LinkedList
from constants import DEFAULT_HEIGHT, DEFAULT_INTERVAL, DEFAULT_WIDTH

NodeValue = int | float | str | bool
Operation = tuple[str, list[NodeValue], str]


@dataclass
class NodeState:
    node_id: int
    value: NodeValue


@dataclass
class NodeVisual:
    node_id: int
    value: NodeValue
    position: tuple[int, int]
    row: int
    col: int


@dataclass
class OperationFrame:
    op_type: str
    duration: float
    nodes_before: list[NodeState]
    nodes_after: list[NodeState]
    added_id: int | None = None
    fade_id: int | None = None
    removed_id: int | None = None
    replaced_id: int | None = None
    current_new_id: int | None = None
    cycle_link: tuple[int, int] | None = None
    label: str = ""


class LinkedListAnimation:
    def __init__(
        self,
        ll_type: str,
        operations: list[Operation],
        width: int = DEFAULT_WIDTH,
        height: int = DEFAULT_HEIGHT,
        node_interval: float = DEFAULT_INTERVAL,
        arrow_interval: float = DEFAULT_INTERVAL,
    ):
        self.ll_type = ll_type
        self.operations = operations
        self.width = width
        self.height = height
        self.node_interval = node_interval
        self.arrow_interval = arrow_interval

    @staticmethod
    def _sort_key(value):
        return (str(type(value)), str(value))

    @staticmethod
    def _index_arg(args: list[NodeValue], position: int = 0) -> int:
        return int(args[position])

    @staticmethod
    def _value_arg(args: list[NodeValue], position: int = 0) -> NodeValue:
        return args[position]

    def configure(self, params: dict[str, Any]):
        if params.get("node_interval"):
            self.node_interval = params["node_interval"]
        if params.get("arrow_interval"):
            self.arrow_interval = params["arrow_interval"]
        if params.get("width"):
            self.width = params["width"]
        if params.get("height"):
            self.height = params["height"]

    def clamp(self, value: float, min_value: float, max_value: float) -> float:
        return max(min_value, min(value, max_value))

    def lerp_color(self, color_a, color_b, t: float):
        t = self.clamp(t, 0.0, 1.0)
        return (
            int(color_a[0] + (color_b[0] - color_a[0]) * t),
            int(color_a[1] + (color_b[1] - color_a[1]) * t),
            int(color_a[2] + (color_b[2] - color_a[2]) * t),
        )

    def layout_nodes(self, nodes: list[NodeState], width: int, height: int) -> list[NodeVisual]:
        count = max(1, len(nodes))
        margin = 80
        usable_width = max(200, width - margin * 2)
        min_spacing = 180
        max_per_row = max(1, int(usable_width // min_spacing) + 1)
        per_row = min(count, max_per_row)
        rows = math.ceil(count / per_row)
        spacing_x = usable_width / max(1, per_row - 1)
        usable_height = max(200, height - margin * 2)
        spacing_y = usable_height / max(1, rows - 1)

        visuals = []
        for index, node in enumerate(nodes):
            row = index // per_row
            col = index % per_row
            x = int(margin + col * spacing_x)
            y = int(margin + row * spacing_y)
            visuals.append(NodeVisual(node.node_id, node.value, (x, y), row, col))
        return visuals

    def build_frames(
        self,
        operations: list[Operation],
        interval: float,
    ) -> list[OperationFrame]:
        linked_list = LinkedList.create(self.ll_type)
        nodes: list[NodeState] = []
        next_id = len(nodes)
        frames: list[OperationFrame] = []
        current_new_id = None
        current_cycle: tuple[int, int] | None = None

        for command, args, label in operations:
            size_before = len(nodes)
            nodes_before = [NodeState(node.node_id, node.value) for node in nodes]

            if command == "append":
                value = self._value_arg(args)
                linked_list.append(value)
                insert_index = size_before
                new_node = NodeState(next_id, value)
                next_id += 1
                nodes.insert(insert_index, new_node)
                frames.append(
                    OperationFrame(
                        op_type="add",
                        duration=interval,
                        nodes_before=nodes_before,
                        nodes_after=[NodeState(node.node_id, node.value) for node in nodes],
                        added_id=new_node.node_id,
                        fade_id=current_new_id,
                        current_new_id=new_node.node_id,
                        cycle_link=current_cycle,
                        label=label,
                    )
                )
                current_new_id = new_node.node_id
            elif command == "prepend":
                value = self._value_arg(args)
                linked_list.prepend(value)
                insert_index = 0
                new_node = NodeState(next_id, value)
                next_id += 1
                nodes.insert(insert_index, new_node)
                frames.append(
                    OperationFrame(
                        op_type="add",
                        duration=interval,
                        nodes_before=nodes_before,
                        nodes_after=[NodeState(node.node_id, node.value) for node in nodes],
                        added_id=new_node.node_id,
                        fade_id=current_new_id,
                        current_new_id=new_node.node_id,
                        cycle_link=current_cycle,
                        label=label,
                    )
                )
                current_new_id = new_node.node_id
            elif command == "insert":
                index = self._index_arg(args)
                value = self._value_arg(args, 1)
                if index <= 0:
                    insert_index = 0
                elif index >= size_before:
                    insert_index = size_before
                else:
                    insert_index = index
                linked_list.insert(insert_index, value)
                new_node = NodeState(next_id, value)
                next_id += 1
                nodes.insert(insert_index, new_node)
                frames.append(
                    OperationFrame(
                        op_type="add",
                        duration=interval,
                        nodes_before=nodes_before,
                        nodes_after=[NodeState(node.node_id, node.value) for node in nodes],
                        added_id=new_node.node_id,
                        fade_id=current_new_id,
                        current_new_id=new_node.node_id,
                        cycle_link=current_cycle,
                        label=label,
                    )
                )
                current_new_id = new_node.node_id
            elif command == "remove":
                if size_before == 0:
                    continue
                index = self._index_arg(args)
                if index <= 0:
                    remove_index = 0
                elif index >= size_before - 1:
                    remove_index = size_before - 1
                else:
                    remove_index = index
                removed_node = nodes[remove_index]
                linked_list.remove(remove_index)
                nodes.pop(remove_index)
                if current_new_id == removed_node.node_id:
                    current_new_id = None
                frames.append(
                    OperationFrame(
                        op_type="remove",
                        duration=interval,
                        nodes_before=nodes_before,
                        nodes_after=[NodeState(node.node_id, node.value) for node in nodes],
                        removed_id=removed_node.node_id,
                        current_new_id=current_new_id,
                        cycle_link=current_cycle,
                        label=label,
                    )
                )
            elif command == "replace":
                if size_before == 0:
                    continue
                index = self._index_arg(args)
                value = self._value_arg(args, 1)
                if index <= 0:
                    replace_index = 0
                elif index >= size_before - 1:
                    replace_index = size_before - 1
                else:
                    replace_index = index
                linked_list.replace(replace_index, value)
                nodes[replace_index] = NodeState(nodes[replace_index].node_id, value)
                frames.append(
                    OperationFrame(
                        op_type="replace",
                        duration=interval,
                        nodes_before=nodes_before,
                        nodes_after=[NodeState(node.node_id, node.value) for node in nodes],
                        replaced_id=nodes[replace_index].node_id,
                        current_new_id=current_new_id,
                        cycle_link=current_cycle,
                        label=label,
                    )
                )
            elif command == "reverse":
                if size_before == 0:
                    continue
                linked_list.reverse()
                nodes = list(reversed(nodes))
                frames.append(
                    OperationFrame(
                        op_type="reverse",
                        duration=interval,
                        nodes_before=nodes_before,
                        nodes_after=[NodeState(node.node_id, node.value) for node in nodes],
                        current_new_id=current_new_id,
                        cycle_link=current_cycle,
                        label=label,
                    )
                )
            elif command == "sort":
                if size_before == 0:
                    continue
                sort_method = self._index_arg(args) if args else 1
                if linked_list.sort(method=sort_method):
                    nodes = sorted(nodes, key=lambda node: self._sort_key(node.value))
                    current_cycle = None
                    frames.append(
                        OperationFrame(
                            op_type="sort",
                            duration=interval,
                            nodes_before=nodes_before,
                            nodes_after=[NodeState(node.node_id, node.value) for node in nodes],
                            current_new_id=current_new_id,
                            cycle_link=current_cycle,
                            label=label,
                        )
                    )
            elif command == "cycle":
                if self.ll_type == "singly":
                    if size_before == 0:
                        continue
                    start_index = self._index_arg(args)
                    linked_list.create_cycle(start_index)
                    start_node_id = None
                    end_node_id = None

                    if 0 <= start_index <= len(nodes) - 2:
                        try:
                            start_node_id = nodes[start_index].node_id
                            end_node_id = nodes[-1].node_id
                        except IndexError:
                            start_node_id = None
                            end_node_id = None
                    if start_node_id is not None and end_node_id is not None:
                        current_cycle = (end_node_id, start_node_id)
                frames.append(
                    OperationFrame(
                        op_type="cycle",
                        duration=interval,
                        nodes_before=nodes_before,
                        nodes_after=[NodeState(node.node_id, node.value) for node in nodes],
                        current_new_id=current_new_id,
                        cycle_link=current_cycle,
                        label=label,
                    )
                )
            elif command == "has_cycle":
                result = linked_list.has_cycle()
                frames.append(
                    OperationFrame(
                        op_type="has_cycle",
                        duration=interval,
                        nodes_before=nodes_before,
                        nodes_after=[NodeState(node.node_id, node.value) for node in nodes],
                        current_new_id=current_new_id,
                        cycle_link=current_cycle,
                        label=f"{label} => {result}",
                    )
                )
            else:
                raise ValueError(f"Unsupported operation '{command}'.")

        return frames

    def get_frame_at_time(self, frames: list[OperationFrame], elapsed: float) -> tuple[OperationFrame, float, int]:
        if not frames:
            empty_frame = OperationFrame("idle", 1.0, [], [])
            return empty_frame, 0.0, -1
        total = 0.0
        for index, frame in enumerate(frames):
            total += frame.duration
            if elapsed <= total:
                frame_elapsed = elapsed - (total - frame.duration)
                progress = self.clamp(frame_elapsed / max(frame.duration, 0.01), 0.0, 1.0)
                return frame, progress, index
        return frames[-1], 1.0, len(frames) - 1
