import math
import sys
from typing import cast

from PySide6.QtCore import QRectF, Qt, QTimer
from PySide6.QtGui import QBrush, QColor, QFont, QPainter, QPainterPath, QPen, QPolygonF
from PySide6.QtWidgets import (
    QApplication,
    QGraphicsItem,
    QGraphicsPathItem,
    QGraphicsPolygonItem,
    QGraphicsRectItem,
    QGraphicsScene,
    QGraphicsTextItem,
    QGraphicsView,
    QMainWindow,
)

from classes.animation import LinkedListAnimation, NodeState, NodeVisual, OperationFrame
from classes.pyside6_theme import DEFAULT_PYSIDE_THEME, NodeVisualState, PySideTheme
from constants import *


class LinkedListNodeItem(QGraphicsItem):
    def __init__(
        self,
        value: object,
        visual_state: NodeVisualState,
        theme: PySideTheme,
        parent: QGraphicsItem | None = None,
    ) -> None:
        super().__init__(parent)
        self.value_text = str(value)
        self.visual_state = visual_state
        self.theme = theme
        self._font = QFont(theme.node_font_family, theme.node_font_size)
        self._body_rect = self._measure_body()
        self.setData(0, "node")
        self.setData(1, visual_state.value)

    def boundingRect(self) -> QRectF:
        return self._body_rect.adjusted(
            -self.theme.node_stroke_width,
            -self.theme.node_stroke_width,
            self.theme.node_stroke_width,
            self.theme.node_stroke_width,
        )

    def paint(self, painter: QPainter, option, widget=None) -> None:
        style = self.theme.node_style(self.visual_state)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        painter.setBrush(QBrush(_color(style.fill)))
        painter.setPen(QPen(_color(style.stroke), style.stroke_width))
        painter.drawRoundedRect(self._body_rect, self.theme.node_radius, self.theme.node_radius)
        painter.setFont(self._font)
        painter.setPen(QPen(_color(style.text), 1))
        painter.drawText(self._body_rect, Qt.AlignmentFlag.AlignCenter, self.value_text)

    def _measure_body(self) -> QRectF:
        from PySide6.QtGui import QFontMetricsF

        metrics = QFontMetricsF(self._font)
        text_width = metrics.horizontalAdvance(self.value_text)
        width = max(self.theme.node_min_width, text_width + self.theme.node_padding_x * 2)
        return QRectF(-width / 2, -self.theme.node_height / 2, width, self.theme.node_height)


class LinkedListPySideVisualizer(LinkedListAnimation):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.theme = DEFAULT_PYSIDE_THEME
        self._app: QApplication | None = None
        self._scene: QGraphicsScene | None = None
        self._view: QGraphicsView | None = None

    @property
    def scene(self) -> QGraphicsScene:
        if self._scene is None:
            self._ensure_qt_app()
            self._scene = QGraphicsScene()
        return self._scene

    @property
    def view(self) -> QGraphicsView:
        if self._view is None:
            self._ensure_qt_app()
            self._view = QGraphicsView(self.scene)
        return self._view

    def display(self):
        app = self._ensure_qt_app()
        self._ensure_qt_view()
        window = QMainWindow()
        window.setWindowTitle("Linked List Visualization")
        window.resize(self.width, self.height)
        window.setCentralWidget(self.view)

        frames = self.build_frames(self.operations, self.node_interval)
        elapsed = 0.0

        def tick():
            nonlocal elapsed
            elapsed += 1 / 60
            frame, progress, frame_index = self.get_frame_at_time(frames, elapsed)
            self.render_frame(frames, frame, progress, frame_index, elapsed)

        self.render_first_frame(frames)

        timer = QTimer(window)
        timer.timeout.connect(tick)
        timer.start(16)

        window.show()
        app.exec()

    def _ensure_qt_view(self) -> None:
        _ = self.view

    def _ensure_qt_app(self) -> QApplication:
        app = QApplication.instance()
        if app is None:
            self._app = QApplication(sys.argv[:1])
            return self._app
        if not isinstance(app, QApplication):
            raise TypeError("PySide6 visualizer requires a QApplication instance.")
        return cast(QApplication, app)

    def render_first_frame(self, frames: list[OperationFrame]) -> None:
        frame, progress, frame_index = self.get_frame_at_time(frames, 0.0)
        self.render_frame(frames, frame, progress, frame_index, 0.0)

    def render_frame(
        self,
        frames: list[OperationFrame],
        frame: OperationFrame,
        progress: float,
        frame_index: int,
        elapsed: float,
    ) -> None:
        self.scene.clear()
        self.scene.setSceneRect(0, 0, self.width, self.height)
        self._draw_background()
        self._draw_operations_panel(frames, frame_index)

        nodes_render, blink_on = self._resolve_nodes_to_render(frame, progress, elapsed)
        visuals = self._resolve_visuals(frame, nodes_render, progress)
        radius_map = self._draw_links(frame, visuals, progress)
        self._draw_nodes(frame, visuals, progress, blink_on, radius_map)
        self._draw_cycle_link(frame, visuals, progress, radius_map)

    def _resolve_nodes_to_render(
        self,
        frame: OperationFrame,
        progress: float,
        elapsed: float,
    ) -> tuple[list[NodeState], bool]:
        remove_phase = 0.8
        if frame.op_type == "remove" and progress < remove_phase:
            return frame.nodes_before, int(elapsed / 0.2) % 2 == 0
        if frame.op_type == "remove":
            return frame.nodes_after, False
        if frame.op_type == "replace":
            return frame.nodes_after, int(elapsed / 0.2) % 2 == 0
        if frame.op_type == "sort":
            sort_remove_phase = 0.7
            if progress < sort_remove_phase:
                remove_progress = progress / max(sort_remove_phase, 0.01)
                total_nodes = len(frame.nodes_before)
                removed_count = min(total_nodes, int(remove_progress * total_nodes))
                return frame.nodes_before[: total_nodes - removed_count], False
            redraw_progress = (progress - sort_remove_phase) / max(1 - sort_remove_phase, 0.01)
            total_nodes = len(frame.nodes_after)
            visible_count = min(total_nodes, int(redraw_progress * total_nodes))
            return frame.nodes_after[:visible_count], False
        return frame.nodes_after, False

    def _resolve_visuals(
        self,
        frame: OperationFrame,
        nodes_render: list[NodeState],
        progress: float,
    ) -> list[NodeVisual]:
        if frame.op_type != "reverse":
            return self.layout_nodes(nodes_render, self.width, self.height)

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
                visuals.append(NodeVisual(node.node_id, node.value, (x, y), after_visual.row, after_visual.col))
            elif after_visual:
                visuals.append(after_visual)
        return visuals

    def _draw_background(self) -> None:
        self.scene.setBackgroundBrush(QBrush(self._color(self.theme.canvas)))

    def _draw_operations_panel(self, frames: list[OperationFrame], frame_index: int) -> None:
        panel = QGraphicsRectItem(20, 20, PANEL_WIDTH - 40, self.height - 40)
        panel.setBrush(QBrush(self._color(self.theme.panel_fill)))
        panel.setPen(QPen(self._color(self.theme.panel_stroke), 2))
        self.scene.addItem(panel)

        title = self._text_item("Operations", self.theme.panel_title_size, self.theme.panel_text)
        title.setPos(36, 34)
        self.scene.addItem(title)

        line_height = 22
        max_lines = max(1, (self.height - 100) // line_height)
        end_index = max(0, frame_index + 1)
        start_index = max(0, end_index - max_lines)
        for idx, op_frame in enumerate(frames[start_index:end_index]):
            op_index = start_index + idx
            color = self.theme.panel_current_text if op_index == frame_index else self.theme.panel_text
            item = self._text_item(op_frame.label, self.theme.panel_text_size, color)
            item.setPos(36, 68 + idx * line_height)
            self.scene.addItem(item)

    def _draw_nodes(
        self,
        frame: OperationFrame,
        visuals: list[NodeVisual],
        progress: float,
        blink_on: bool,
        radius_map: dict[int, int],
    ) -> None:
        replace_phase = 0.6
        for visual in visuals:
            x, y = visual.position
            state = self.node_state_for(frame, visual, blink_on)
            if frame.op_type == "replace" and visual.node_id == frame.replaced_id and progress >= replace_phase:
                state = NodeVisualState.NORMAL
            node = LinkedListNodeItem(visual.value, state, self.theme)
            node.setPos(x, y)
            self.scene.addItem(node)

    def node_state_for(
        self,
        frame: OperationFrame,
        visual: NodeState | NodeVisual,
        blink_on: bool,
    ) -> NodeVisualState:
        cycle_ids = set(frame.cycle_link or ())
        if frame.op_type == "remove" and blink_on and visual.node_id == frame.removed_id:
            return NodeVisualState.REMOVING
        if frame.op_type == "replace" and blink_on and visual.node_id == frame.replaced_id:
            return NodeVisualState.CHANGED
        if frame.op_type == "add" and visual.node_id == frame.added_id:
            return NodeVisualState.NEW
        if visual.node_id in cycle_ids:
            return NodeVisualState.CYCLE_ENDPOINT
        if frame.current_new_id is not None and visual.node_id == frame.current_new_id:
            return NodeVisualState.CURRENT
        return NodeVisualState.NORMAL

    def _draw_links(
        self,
        frame: OperationFrame,
        visuals: list[NodeVisual],
        progress: float,
    ) -> dict[int, int]:
        radius_map = {}
        for visual in visuals:
            scale = 1.0
            if frame.op_type == "add" and visual.node_id == frame.added_id:
                scale = 0.5 + 0.5 * progress
            radius_map[visual.node_id] = int((self.theme.node_height / 2) * scale)

        bidirectional = self.ll_type == "doubly"
        for index in range(len(visuals) - 1):
            current = visuals[index]
            next_visual = visuals[index + 1]
            link_progress = self._link_progress(frame, progress, current.node_id, next_visual.node_id)

            if current.row != next_visual.row:
                start = (current.position[0], current.position[1] + radius_map.get(current.node_id, 42))
                end = (next_visual.position[0], next_visual.position[1] - radius_map.get(next_visual.node_id, 42))
                turn_y = current.position[1] + (next_visual.position[1] - current.position[1]) / 2
                path = [start, (start[0], turn_y), (end[0], turn_y), end]
                self._draw_polyline_arrow(path, self.theme.arrow, link_progress, self.theme.arrow_stroke_width)
                if bidirectional:
                    self._draw_polyline_arrow(
                        list(reversed(path)),
                        self.theme.arrow_muted,
                        link_progress,
                        self.theme.reverse_arrow_stroke_width,
                    )
            else:
                start = (current.position[0] + radius_map.get(current.node_id, 42), current.position[1])
                end = (next_visual.position[0] - radius_map.get(next_visual.node_id, 42), next_visual.position[1])
                self._draw_arrow(start, end, self.theme.arrow, link_progress, self.theme.arrow_stroke_width)
                if bidirectional:
                    self._draw_arrow(
                        end,
                        start,
                        self.theme.arrow_muted,
                        link_progress,
                        self.theme.reverse_arrow_stroke_width,
                    )

        return radius_map

    def _draw_cycle_link(
        self,
        frame: OperationFrame,
        visuals: list[NodeVisual],
        progress: float,
        radius_map: dict[int, int],
    ) -> None:
        if not frame.cycle_link:
            return
        visuals_by_id = {visual.node_id: visual for visual in visuals}
        cycle_end_id, cycle_start_id = frame.cycle_link
        cycle_end = visuals_by_id.get(cycle_end_id)
        cycle_start = visuals_by_id.get(cycle_start_id)
        if not cycle_end or not cycle_start:
            return

        start_radius = radius_map.get(cycle_end.node_id, 32)
        end_radius = radius_map.get(cycle_start.node_id, 32)
        start_point = (cycle_end.position[0] + start_radius, cycle_end.position[1])
        end_point = (cycle_start.position[0] - end_radius, cycle_start.position[1])
        min_y = min(cycle_end.position[1], cycle_start.position[1])
        max_y = max(cycle_end.position[1], cycle_start.position[1])
        mid_y = min_y - 70
        if mid_y < 30:
            mid_y = max_y + 70
        self._draw_cycle_arrow(start_point, end_point, mid_y, self._cycle_progress(frame, progress))

    def _link_progress(self, frame: OperationFrame, progress: float, current_id: int, next_id: int) -> float:
        op_elapsed = progress * frame.duration
        if frame.op_type == "add" and frame.added_id in {current_id, next_id}:
            return self.clamp(op_elapsed / max(self.arrow_interval, 0.01), 0.0, 1.0)
        if frame.op_type == "reverse":
            return self._reverse_arrow_progress(progress)
        return 1.0

    def _cycle_progress(self, frame: OperationFrame, progress: float) -> float:
        op_elapsed = progress * frame.duration
        if frame.op_type == "cycle":
            return self.clamp(op_elapsed / max(self.arrow_interval, 0.01), 0.0, 1.0)
        if frame.op_type == "reverse":
            return self._reverse_arrow_progress(progress)
        return 1.0

    def _reverse_arrow_progress(self, progress: float) -> float:
        arrow_out_end = 0.2
        arrow_in_start = 0.8
        if progress <= arrow_out_end:
            return 1.0 - (progress / max(arrow_out_end, 0.01))
        if progress >= arrow_in_start:
            return self.clamp((progress - arrow_in_start) / max(1 - arrow_in_start, 0.01), 0.0, 1.0)
        return 0.0

    def _draw_arrow(self, start, end, color, progress=1.0, width=2, arrow_size=None) -> None:
        arrow_size = arrow_size or self.theme.arrow_head_size
        progress = self.clamp(progress, 0.0, 1.0)
        if progress <= 0:
            return
        end_point = (
            start[0] + (end[0] - start[0]) * progress,
            start[1] + (end[1] - start[1]) * progress,
        )
        path = QPainterPath()
        path.moveTo(*start)
        path.lineTo(*end_point)
        item = QGraphicsPathItem(path)
        item.setPen(QPen(self._color(color), width))
        item.setData(0, "link")
        self.scene.addItem(item)
        if progress >= 0.98:
            self._draw_arrow_head(start, end, color, arrow_size)

    def _draw_polyline_arrow(self, points, color, progress=1.0, width=2, arrow_size=None) -> None:
        arrow_size = arrow_size or self.theme.arrow_head_size
        if len(points) < 2:
            return
        segments = []
        total_length = 0.0
        for index in range(len(points) - 1):
            start = points[index]
            end = points[index + 1]
            length = math.hypot(end[0] - start[0], end[1] - start[1])
            segments.append((start, end, length))
            total_length += length
        if total_length == 0:
            return

        remaining = total_length * self.clamp(progress, 0.0, 1.0)
        path = QPainterPath()
        path.moveTo(*points[0])
        for start, end, length in segments:
            if remaining <= 0:
                break
            if remaining >= length:
                path.lineTo(*end)
                remaining -= length
            else:
                ratio = remaining / length
                current_end = (
                    start[0] + (end[0] - start[0]) * ratio,
                    start[1] + (end[1] - start[1]) * ratio,
                )
                path.lineTo(*current_end)
                break
        item = QGraphicsPathItem(path)
        item.setPen(QPen(self._color(color), width))
        item.setData(0, "link")
        self.scene.addItem(item)
        if self.clamp(progress, 0.0, 1.0) >= 0.98:
            self._draw_arrow_head(segments[-1][0], segments[-1][1], color, arrow_size)

    def _draw_arrow_head(self, start, end, color, arrow_size=12) -> None:
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
        arrow = QGraphicsPolygonItem(QPolygonF([self._point(end), self._point(left), self._point(right)]))
        arrow.setBrush(QBrush(self._color(color)))
        arrow.setPen(QPen(self._color(color), 1))
        self.scene.addItem(arrow)

    def _draw_cycle_arrow(self, start, end, control_y, progress: float) -> None:
        progress = self.clamp(progress, 0.0, 1.0)
        if progress <= 0:
            return
        path = QPainterPath()
        path.moveTo(*start)
        control_offset = max(80.0, abs(end[0] - start[0]) / 2)
        control_1 = (start[0] + control_offset, control_y)
        control_2 = (end[0] - control_offset, control_y)
        path.cubicTo(*control_1, *control_2, *end)
        item = QGraphicsPathItem(path)
        item.setPen(QPen(self._color(self.theme.cycle_arrow), self.theme.cycle_arrow_stroke_width))
        item.setData(0, "cycle-link")
        self.scene.addItem(item)
        if progress >= 0.98:
            self._draw_arrow_head(control_2, end, self.theme.cycle_arrow, self.theme.arrow_head_size)

    def _text_item(self, text: str, size: int, color) -> QGraphicsTextItem:
        item = QGraphicsTextItem(text)
        item.setFont(QFont("Avenir", size))
        item.setDefaultTextColor(self._color(color))
        return item

    def _color(self, rgb) -> QColor:
        return _color(rgb)

    def _point(self, point):
        from PySide6.QtCore import QPointF

        return QPointF(float(point[0]), float(point[1]))


def _color(rgb) -> QColor:
    return QColor(int(rgb[0]), int(rgb[1]), int(rgb[2]))
