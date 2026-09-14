import math

import pygame

from classes.animation import LinkedListAnimation, NodeState, NodeVisual, OperationFrame
from constants import *

__all__ = ["LinkedListVisualizer", "NodeState", "NodeVisual", "OperationFrame"]


class LinkedListVisualizer(LinkedListAnimation):

    def draw_arrow(self, surface, start, end, color, progress=1.0, width=2, arrow_size=12):
        progress = self.clamp(progress, 0.0, 1.0)
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

    def draw_polyline_arrow(self, surface, points, color, progress=1.0, width=2, arrow_size=12):
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

        remaining = total_length * self.clamp(progress, 0.0, 1.0)
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

        if self.clamp(progress, 0.0, 1.0) >= 0.98:
            final_start = segments[-1][0]
            final_end = segments[-1][1]
            self.draw_arrow(surface, final_start, final_end, color, progress=1.0, width=width, arrow_size=arrow_size)

    def display(self):
        frames = self.build_frames(self.operations, self.node_interval)
        pygame.init()
        screen = pygame.display.set_mode((self.width, self.height))
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

            frame, progress, frame_index = self.get_frame_at_time(frames, now)
            remove_phase = 0.8
            replace_phase = 0.6

            if frame.op_type == "remove" and progress < remove_phase:
                nodes_render = frame.nodes_before
                blink_on = int(now / 0.2) % 2 == 0
            elif frame.op_type == "remove":
                nodes_render = frame.nodes_after
                blink_on = False
            elif frame.op_type == "replace":
                nodes_render = frame.nodes_after
                blink_on = int(now / 0.2) % 2 == 0
            elif frame.op_type == "sort":
                sort_remove_phase = 0.7
                if progress < sort_remove_phase:
                    remove_progress = progress / max(sort_remove_phase, 0.01)
                    total_nodes = len(frame.nodes_before)
                    removed_count = min(total_nodes, int(remove_progress * total_nodes))
                    nodes_render = frame.nodes_before[:total_nodes - removed_count]
                else:
                    redraw_progress = (progress - sort_remove_phase) / max(1 - sort_remove_phase, 0.01)
                    total_nodes = len(frame.nodes_after)
                    visible_count = min(total_nodes, int(redraw_progress * total_nodes))
                    nodes_render = frame.nodes_after[:visible_count]
                blink_on = False
            elif frame.op_type == "reverse":
                nodes_render = frame.nodes_after
                blink_on = False
            else:
                nodes_render = frame.nodes_after
                blink_on = False

            if frame.op_type == "reverse":
                visuals_before = self.layout_nodes(frame.nodes_before, self.width, self.height)
                visuals_after = self.layout_nodes(frame.nodes_after, self.width, self.height)
                before_by_id = {visual.node_id: visual for visual in visuals_before}
                after_by_id = {visual.node_id: visual for visual in visuals_after}
                arrow_out_end = 0.2
                arrow_in_start = 0.8
                if progress <= arrow_out_end:
                    move_t = 0.0
                elif progress >= arrow_in_start:
                    move_t = 1.0
                else:
                    move_t = (progress - arrow_out_end) / (arrow_in_start - arrow_out_end)

                visuals = []
                for node in frame.nodes_after:
                    before_visual = before_by_id.get(node.node_id)
                    after_visual = after_by_id.get(node.node_id)
                    if before_visual and after_visual:
                        start_x, start_y = before_visual.position
                        end_x, end_y = after_visual.position
                        x = int(start_x + (end_x - start_x) * move_t)
                        y = int(start_y + (end_y - start_y) * move_t)
                        visuals.append(NodeVisual(
                            node_id=node.node_id,
                            value=node.value,
                            position=(x, y),
                            row=after_visual.row,
                            col=after_visual.col,
                        ))
                    elif after_visual:
                        visuals.append(after_visual)
                reverse_arrow_out_end = arrow_out_end
                reverse_arrow_in_start = arrow_in_start
            else:
                visuals = self.layout_nodes(nodes_render, self.width, self.height)
                reverse_arrow_out_end = None
                reverse_arrow_in_start = None
            screen.fill(DEFAULT_BG_COLOR)

            panel_rect = pygame.Rect(20, 20, PANEL_WIDTH - 40, self.height - 40)
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
            visuals_by_id = {}
            for visual in visuals:
                scale = 1.0
                if frame.op_type == "add" and visual.node_id == frame.added_id:
                    scale = 0.5 + 0.5 * progress
                radius = int(32 * scale)
                radius_map[visual.node_id] = radius
                x, y = visual.position

                color = NODE_COLOR
                if frame.op_type == "add":
                    if visual.node_id == frame.added_id:
                        color = NODE_NEW_COLOR
                    elif frame.fade_id is not None and visual.node_id == frame.fade_id:
                        color = self.lerp_color(NODE_NEW_COLOR, NODE_COLOR, progress)
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
                        color = self.lerp_color(NODE_REPLACE_COLOR, NODE_COLOR, fade_progress)

                pygame.draw.circle(screen, color, (x, y), radius)
                pygame.draw.circle(screen, NODE_EDGE_COLOR, (x, y), radius, 3)

                label = font.render(str(visual.value), True, TEXT_COLOR)
                label_rect = label.get_rect(center=(x, y))
                screen.blit(label, label_rect)
                visuals_by_id[visual.node_id] = visual

            op_elapsed = progress * frame.duration
            bidirectional = self.ll_type == "doubly"
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
                        link_progress = self.clamp(op_elapsed / max(self.arrow_interval, 0.01), 0.0, 1.0)
                    elif frame.op_type == "reverse":
                        if progress <= reverse_arrow_out_end:
                            link_progress = 1.0 - (progress / max(reverse_arrow_out_end, 0.01))
                        elif progress >= reverse_arrow_in_start:
                            link_progress = self.clamp(
                                (progress - reverse_arrow_in_start) / max(1 - reverse_arrow_in_start, 0.01),
                                0.0,
                                1.0,
                            )
                        else:
                            link_progress = 0.0
                    self.draw_polyline_arrow(screen, path, ARROW_COLOR, progress=link_progress, width=3)
                    if bidirectional:
                        reverse_path = list(reversed(path))
                        self.draw_polyline_arrow(screen, reverse_path, ARROW_COLOR, progress=link_progress, width=3)
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
                        link_progress = self.clamp(op_elapsed / max(self.arrow_interval, 0.01), 0.0, 1.0)
                    elif frame.op_type == "reverse":
                        if progress <= reverse_arrow_out_end:
                            link_progress = 1.0 - (progress / max(reverse_arrow_out_end, 0.01))
                        elif progress >= reverse_arrow_in_start:
                            link_progress = self.clamp(
                                (progress - reverse_arrow_in_start) / max(1 - reverse_arrow_in_start, 0.01),
                                0.0,
                                1.0,
                            )
                        else:
                            link_progress = 0.0
                    self.draw_arrow(screen, start, end, ARROW_COLOR, progress=link_progress, width=3)
                    if bidirectional:
                        self.draw_arrow(screen, end, start, ARROW_COLOR, progress=link_progress, width=3)

            if frame.cycle_link:
                cycle_end_id, cycle_start_id = frame.cycle_link
                cycle_end = visuals_by_id.get(cycle_end_id)
                cycle_start = visuals_by_id.get(cycle_start_id)
                if cycle_end and cycle_start:
                    start_radius = radius_map.get(cycle_end.node_id, 32)
                    end_radius = radius_map.get(cycle_start.node_id, 32)
                    start_point = (
                        cycle_end.position[0] + start_radius,
                        cycle_end.position[1],
                    )
                    end_point = (
                        cycle_start.position[0] - end_radius,
                        cycle_start.position[1],
                    )
                    min_y = min(cycle_end.position[1], cycle_start.position[1])
                    max_y = max(cycle_end.position[1], cycle_start.position[1])
                    mid_y = min_y - 70
                    if mid_y < 30:
                        mid_y = max_y + 70
                    path = [
                        start_point,
                        (start_point[0] + 30, start_point[1]),
                        (start_point[0] + 30, mid_y),
                        (end_point[0] - 30, mid_y),
                        (end_point[0] - 30, end_point[1]),
                        end_point,
                    ]
                    cycle_progress = 1.0
                    if frame.op_type == "cycle":
                        cycle_progress = self.clamp(op_elapsed / max(self.arrow_interval, 0.01), 0.0, 1.0)
                    elif frame.op_type == "reverse":
                        if progress <= reverse_arrow_out_end:
                            cycle_progress = 1.0 - (progress / max(reverse_arrow_out_end, 0.01))
                        elif progress >= reverse_arrow_in_start:
                            cycle_progress = self.clamp(
                                (progress - reverse_arrow_in_start) / max(1 - reverse_arrow_in_start, 0.01),
                                0.0,
                                1.0,
                            )
                        else:
                            cycle_progress = 0.0
                    self.draw_polyline_arrow(screen, path, CYCLE_COLOR, progress=cycle_progress, width=3)

            pygame.display.flip()
            clock.tick(60)

        pygame.quit()
