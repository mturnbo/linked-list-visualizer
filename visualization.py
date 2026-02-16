import math
from dataclasses import dataclass
from typing import List, Optional, Tuple

import pygame

from classes.singly_linked_list import LinkedList


DEFAULT_VALUES = [1, 2, 3, 4, 5]
DEFAULT_INTERVAL = 0.4
DEFAULT_WIDTH = 1000
DEFAULT_HEIGHT = 500
DEFAULT_BG_COLOR = (16, 24, 32)
PANEL_WIDTH = 280
PANEL_BG = (12, 18, 26)
PANEL_BORDER = (60, 80, 96)
PANEL_TEXT = (220, 235, 245)
PANEL_HIGHLIGHT = (255, 235, 160)
NODE_COLOR = (70, 140, 220)
NODE_NEW_COLOR = (240, 210, 70)
NODE_REMOVE_COLOR = (220, 70, 70)
NODE_REPLACE_COLOR = (240, 150, 60)
NODE_EDGE_COLOR = (18, 38, 36)
TEXT_COLOR = (230, 245, 248)
ARROW_COLOR = (200, 220, 230)


@dataclass
class NodeState:
    node_id: int
    value: int | float | str | bool


@dataclass
class NodeVisual:
    node_id: int
    value: int | float | str | bool
    position: Tuple[int, int]
    row: int
    col: int


@dataclass
class OperationFrame:
    op_type: str
    duration: float
    nodes_before: List[NodeState]
    nodes_after: List[NodeState]
    added_id: Optional[int] = None
    fade_id: Optional[int] = None
    removed_id: Optional[int] = None
    replaced_id: Optional[int] = None
    current_new_id: Optional[int] = None
    label: str = ""


def build_linked_list_from_values(values: List[int | float | str | bool]):
    linked_list = LinkedList()
    for value in values:
        linked_list.append(value)
    return linked_list


def clamp(value: float, min_value: float, max_value: float) -> float:
    return max(min_value, min(value, max_value))


def lerp_color(color_a, color_b, t: float):
    t = clamp(t, 0.0, 1.0)
    return (
        int(color_a[0] + (color_b[0] - color_a[0]) * t),
        int(color_a[1] + (color_b[1] - color_a[1]) * t),
        int(color_a[2] + (color_b[2] - color_a[2]) * t),
    )


def layout_nodes(nodes: List[NodeState], width: int, height: int) -> List[NodeVisual]:
    count = max(1, len(nodes))
    margin = 80
    usable_width = max(200, width - margin * 2 - PANEL_WIDTH)
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
        x = int(PANEL_WIDTH + margin + col * spacing_x)
        y = int(margin + row * spacing_y)
        visuals.append(NodeVisual(node.node_id, node.value, (x, y), row, col))
    return visuals


def draw_arrow(surface, start, end, color, progress=1.0, width=2, arrow_size=12):
    progress = clamp(progress, 0.0, 1.0)
    if progress <= 0:
        return
    end_point = (
        start[0] + (end[0] - start[0]) * progress,
        start[1] + (end[1] - start[1]) * progress,
    )
    pygame.draw.line(surface, color, start, end_point, width)
    if progress < 0.98:
        return
    direction = (start[0] - end[0], start[1] - end[1])
    length = math.hypot(direction[0], direction[1])
    if length == 0:
        return
    unit = (direction[0] / length, direction[1] / length)
    perpendicular = (-unit[1], unit[0])

    left = (
        end[0] + unit[0] * arrow_size + perpendicular[0] * (arrow_size * 0.6),
        end[1] + unit[1] * arrow_size + perpendicular[1] * (arrow_size * 0.6),
    )
    right = (
        end[0] + unit[0] * arrow_size - perpendicular[0] * (arrow_size * 0.6),
        end[1] + unit[1] * arrow_size - perpendicular[1] * (arrow_size * 0.6),
    )
    pygame.draw.polygon(surface, color, [end, left, right])


def draw_polyline_arrow(surface, points, color, progress=1.0, width=2, arrow_size=12):
    if len(points) < 2:
        return
    segments = []
    total_length = 0.0
    for i in range(len(points) - 1):
        start = points[i]
        end = points[i + 1]
        length = math.hypot(end[0] - start[0], end[1] - start[1])
        segments.append((start, end, length))
        total_length += length
    if total_length == 0:
        return

    remaining = total_length * clamp(progress, 0.0, 1.0)
    for start, end, length in segments:
        if remaining <= 0:
            break
        if remaining >= length:
            pygame.draw.line(surface, color, start, end, width)
            remaining -= length
        else:
            ratio = remaining / length
            current_end = (
                start[0] + (end[0] - start[0]) * ratio,
                start[1] + (end[1] - start[1]) * ratio,
            )
            pygame.draw.line(surface, color, start, current_end, width)
            remaining = 0
            break

    if clamp(progress, 0.0, 1.0) >= 0.98:
        final_start = segments[-1][0]
        final_end = segments[-1][1]
        draw_arrow(surface, final_start, final_end, color, progress=1.0, width=width, arrow_size=arrow_size)


def build_frames(
    initial_values: List[int | float | str | bool],
    operations: List[Tuple[str, List[int | float | str | bool], str]],
    interval: float,
) -> List[OperationFrame]:
    linked_list = build_linked_list_from_values(initial_values)
    nodes = [NodeState(node_id=index, value=value) for index, value in enumerate(initial_values)]
    next_id = len(nodes)
    frames: List[OperationFrame] = []
    current_new_id = None

    for command, args, label in operations:
        size_before = len(nodes)
        nodes_before = [NodeState(node.node_id, node.value) for node in nodes]

        if command == "append":
            value = args[0]
            linked_list.append(value)
            insert_index = size_before
            new_node = NodeState(next_id, value)
            next_id += 1
            nodes.insert(insert_index, new_node)
            frames.append(OperationFrame(
                op_type="add",
                duration=interval,
                nodes_before=nodes_before,
                nodes_after=[NodeState(node.node_id, node.value) for node in nodes],
                added_id=new_node.node_id,
                fade_id=current_new_id,
                current_new_id=new_node.node_id,
                label=label,
            ))
            current_new_id = new_node.node_id
        elif command == "prepend":
            value = args[0]
            linked_list.prepend(value)
            insert_index = 0
            new_node = NodeState(next_id, value)
            next_id += 1
            nodes.insert(insert_index, new_node)
            frames.append(OperationFrame(
                op_type="add",
                duration=interval,
                nodes_before=nodes_before,
                nodes_after=[NodeState(node.node_id, node.value) for node in nodes],
                added_id=new_node.node_id,
                fade_id=current_new_id,
                current_new_id=new_node.node_id,
                label=label,
            ))
            current_new_id = new_node.node_id
        elif command == "insert":
            index, value = args
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
            frames.append(OperationFrame(
                op_type="add",
                duration=interval,
                nodes_before=nodes_before,
                nodes_after=[NodeState(node.node_id, node.value) for node in nodes],
                added_id=new_node.node_id,
                fade_id=current_new_id,
                current_new_id=new_node.node_id,
                label=label,
            ))
            current_new_id = new_node.node_id
        elif command == "remove":
            if size_before == 0:
                continue
            index = args[0]
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
            frames.append(OperationFrame(
                op_type="remove",
                duration=interval,
                nodes_before=nodes_before,
                nodes_after=[NodeState(node.node_id, node.value) for node in nodes],
                removed_id=removed_node.node_id,
                current_new_id=current_new_id,
                label=label,
            ))
        elif command == "replace":
            if size_before == 0:
                continue
            index, value = args
            if index <= 0:
                replace_index = 0
            elif index >= size_before - 1:
                replace_index = size_before - 1
            else:
                replace_index = index
            linked_list.replace(replace_index, value)
            nodes[replace_index] = NodeState(nodes[replace_index].node_id, value)
            frames.append(OperationFrame(
                op_type="replace",
                duration=interval,
                nodes_before=nodes_before,
                nodes_after=[NodeState(node.node_id, node.value) for node in nodes],
                replaced_id=nodes[replace_index].node_id,
                current_new_id=current_new_id,
                label=label,
            ))
        else:
            raise ValueError(f"Unsupported operation '{command}'.")

    return frames


def get_frame_at_time(frames: List[OperationFrame], elapsed: float) -> Tuple[OperationFrame, float, int]:
    if not frames:
        empty_frame = OperationFrame("idle", 1.0, [], [])
        return empty_frame, 0.0, -1
    total = 0.0
    for index, frame in enumerate(frames):
        total += frame.duration
        if elapsed <= total:
            frame_elapsed = elapsed - (total - frame.duration)
            progress = clamp(frame_elapsed / max(frame.duration, 0.01), 0.0, 1.0)
            return frame, progress, index
    return frames[-1], 1.0, len(frames) - 1


def run_visualization(
    values: List[int | float | str | bool],
    operations: List[Tuple[str, List[int | float | str | bool], str]],
    interval: float,
    arrow_interval: float,
    width: int,
    height: int,
):
    frames = build_frames(values, operations, interval)

    pygame.init()
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("Linked List Visualization")
    font = pygame.font.SysFont("Avenir", 24)
    panel_font = pygame.font.SysFont("Avenir", 18)
    clock = pygame.time.Clock()

    start_time = pygame.time.get_ticks() / 1000.0
    running = True

    while running:
        now = pygame.time.get_ticks() / 1000.0 - start_time
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        frame, progress, frame_index = get_frame_at_time(frames, now)
        remove_phase = 0.7
        replace_phase = 0.5

        if frame.op_type == "remove" and progress < remove_phase:
            nodes_render = frame.nodes_before
            blink_on = int((now / 0.2)) % 2 == 0
        elif frame.op_type == "remove":
            nodes_render = frame.nodes_after
            blink_on = False
        elif frame.op_type == "replace":
            nodes_render = frame.nodes_after
            blink_on = int((now / 0.2)) % 2 == 0
        else:
            nodes_render = frame.nodes_after
            blink_on = False

        visuals = layout_nodes(nodes_render, width, height)
        screen.fill(DEFAULT_BG_COLOR)

        panel_rect = pygame.Rect(20, 20, PANEL_WIDTH - 40, height - 40)
        pygame.draw.rect(screen, PANEL_BG, panel_rect)
        pygame.draw.rect(screen, PANEL_BORDER, panel_rect, 2)

        panel_title = font.render("Operations", True, PANEL_TEXT)
        screen.blit(panel_title, (panel_rect.x + 16, panel_rect.y + 14))

        line_height = 22
        max_lines = max(1, (panel_rect.height - 60) // line_height)
        end_index = max(0, frame_index + 1)
        start_index = max(0, end_index - max_lines)
        visible_ops = frames[start_index:end_index]
        for idx, op_frame in enumerate(visible_ops):
            op_index = start_index + idx
            color = PANEL_TEXT
            if op_index == frame_index:
                color = PANEL_HIGHLIGHT
            text_surface = panel_font.render(op_frame.label, True, color)
            screen.blit(text_surface, (panel_rect.x + 16, panel_rect.y + 48 + idx * line_height))

        radius_map = {}
        for visual in visuals:
            scale = 1.0
            if frame.op_type == "add" and visual.node_id == frame.added_id:
                scale = 0.5 + 0.5 * progress
            radius = int(42 * scale)
            radius_map[visual.node_id] = radius
            x, y = visual.position

            color = NODE_COLOR
            if frame.op_type == "add":
                if visual.node_id == frame.added_id:
                    color = NODE_NEW_COLOR
                elif frame.fade_id is not None and visual.node_id == frame.fade_id:
                    color = lerp_color(NODE_NEW_COLOR, NODE_COLOR, progress)
            elif frame.current_new_id is not None and visual.node_id == frame.current_new_id:
                color = NODE_NEW_COLOR
            if frame.op_type == "remove" and blink_on and visual.node_id == frame.removed_id:
                color = NODE_REMOVE_COLOR
            if frame.op_type == "replace" and visual.node_id == frame.replaced_id:
                if progress < replace_phase:
                    if blink_on:
                        color = NODE_REPLACE_COLOR
                else:
                    fade_progress = (progress - replace_phase) / max(1 - replace_phase, 0.01)
                    color = lerp_color(NODE_REPLACE_COLOR, NODE_COLOR, fade_progress)

            pygame.draw.circle(screen, color, (x, y), radius)
            pygame.draw.circle(screen, NODE_EDGE_COLOR, (x, y), radius, 3)

            label = font.render(str(visual.value), True, TEXT_COLOR)
            label_rect = label.get_rect(center=(x, y))
            screen.blit(label, label_rect)

        op_elapsed = progress * frame.duration
        for index in range(len(visuals) - 1):
            current = visuals[index]
            next_visual = visuals[index + 1]

            if current.row != next_visual.row:
                start = (
                    current.position[0],
                    current.position[1] + radius_map.get(current.node_id, 42),
                )
                end = (
                    next_visual.position[0],
                    next_visual.position[1] - radius_map.get(next_visual.node_id, 42),
                )
                turn_y = current.position[1] + (next_visual.position[1] - current.position[1]) / 2
                path = [
                    start,
                    (start[0], turn_y),
                    (end[0], turn_y),
                    end,
                ]
                link_progress = 1.0
                if frame.op_type == "add" and frame.added_id in {current.node_id, next_visual.node_id}:
                    link_progress = clamp(op_elapsed / max(arrow_interval, 0.01), 0.0, 1.0)
                draw_polyline_arrow(screen, path, ARROW_COLOR, progress=link_progress, width=3)
            else:
                start = (
                    current.position[0] + radius_map.get(current.node_id, 42),
                    current.position[1],
                )
                end = (
                    next_visual.position[0] - radius_map.get(next_visual.node_id, 42),
                    next_visual.position[1],
                )
                link_progress = 1.0
                if frame.op_type == "add" and frame.added_id in {current.node_id, next_visual.node_id}:
                    link_progress = clamp(op_elapsed / max(arrow_interval, 0.01), 0.0, 1.0)
                draw_arrow(screen, start, end, ARROW_COLOR, progress=link_progress, width=3)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
