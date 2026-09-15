import math
import sys
from pathlib import Path
from typing import cast

from PySide6.QtCore import QPointF, QRectF, Qt, QTimer
from PySide6.QtGui import (
    QBrush,
    QColor,
    QFont,
    QImage,
    QPainter,
    QPainterPath,
    QPen,
    QPolygonF,
    QWheelEvent,
)
from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QFileDialog,
    QGraphicsItem,
    QGraphicsPathItem,
    QGraphicsPolygonItem,
    QGraphicsScene,
    QGraphicsTextItem,
    QGraphicsView,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from classes.animation import (
    LinkedListAnimation,
    NodeState,
    NodeValue,
    NodeVisual,
    Operation,
    OperationFrame,
)
from classes.operation_input import OperationInputError, OperationQueue
from classes.playback_controller import PlaybackController
from classes.pyside6_theme import DEFAULT_PYSIDE_THEME, NodeVisualState, PySideTheme
from constants import *


class LinkedListNodeItem(QGraphicsItem):
    def __init__(
        self,
        value: object,
        visual_state: NodeVisualState,
        theme: PySideTheme,
        node_kind: str = "singly",
        parent: QGraphicsItem | None = None,
    ) -> None:
        super().__init__(parent)
        self.value_text = str(value)
        self.visual_state = visual_state
        self.theme = theme
        self.node_kind = node_kind
        self.pointer_cell_count = 2 if node_kind == "doubly" else 1
        self.pointer_cell_width = theme.pointer_cell_width
        self._font = QFont(theme.node_font_family, theme.node_font_size)
        self._body_rect = self._measure_body()
        self.left_pointer_rect, self.value_rect, self.right_pointer_rect = self._measure_compartments()
        self.setData(0, "node")
        self.setData(1, visual_state.value)
        self.setData(2, node_kind)

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
        self._draw_compartment_dividers(painter, style.stroke, style.stroke_width)
        painter.setFont(self._font)
        painter.setPen(QPen(_color(style.text), 1))
        painter.drawText(self.value_rect, Qt.AlignmentFlag.AlignCenter, self.value_text)

    def outgoing_anchor(self) -> QPointF:
        return self.right_pointer_rect.center()

    def incoming_anchor(self) -> QPointF:
        if self.left_pointer_rect is not None:
            return self.left_pointer_rect.center()
        return QPointF(self._body_rect.left(), self._body_rect.center().y())

    def _measure_body(self) -> QRectF:
        from PySide6.QtGui import QFontMetricsF

        metrics = QFontMetricsF(self._font)
        text_width = metrics.horizontalAdvance(self.value_text)
        value_width = max(self.theme.node_min_width, text_width + self.theme.node_padding_x * 2)
        width = value_width + self.pointer_cell_width * self.pointer_cell_count
        return QRectF(-width / 2, -self.theme.node_height / 2, width, self.theme.node_height)

    def _measure_compartments(self) -> tuple[QRectF | None, QRectF, QRectF]:
        body = self._body_rect
        left = None
        value_x = body.left()
        if self.node_kind == "doubly":
            left = QRectF(body.left(), body.top(), self.pointer_cell_width, body.height())
            value_x += self.pointer_cell_width
        value_width = body.width() - self.pointer_cell_width * self.pointer_cell_count
        value = QRectF(value_x, body.top(), value_width, body.height())
        right = QRectF(value.right(), body.top(), self.pointer_cell_width, body.height())
        return left, value, right

    def _draw_compartment_dividers(self, painter: QPainter, stroke, stroke_width: float) -> None:
        painter.setPen(QPen(_color(stroke), max(1.0, stroke_width - 0.5)))
        if self.left_pointer_rect is not None:
            x = self.left_pointer_rect.right()
            painter.drawLine(QPointF(x, self._body_rect.top()), QPointF(x, self._body_rect.bottom()))
        x = self.value_rect.right()
        painter.drawLine(QPointF(x, self._body_rect.top()), QPointF(x, self._body_rect.bottom()))


class CanvasGraphicsView(QGraphicsView):
    def __init__(
        self,
        scene: QGraphicsScene,
        min_zoom: float = 0.25,
        max_zoom: float = 4.0,
        zoom_step: float = 1.15,
    ) -> None:
        super().__init__(scene)
        self.min_zoom = min_zoom
        self.max_zoom = max_zoom
        self.zoom_step = zoom_step
        self.current_zoom = 1.0
        self.fit_target = QRectF()
        self.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorViewCenter)
        self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        self.setInteractive(True)

    def wheelEvent(self, event: QWheelEvent) -> None:
        if event.angleDelta().y() > 0:
            self.zoom_in()
        else:
            self.zoom_out()
        event.accept()

    def zoom_in(self) -> None:
        self.set_zoom(self.current_zoom * self.zoom_step)

    def zoom_out(self) -> None:
        self.set_zoom(self.current_zoom / self.zoom_step)

    def set_zoom(self, zoom: float) -> None:
        self.current_zoom = max(self.min_zoom, min(zoom, self.max_zoom))
        self.resetTransform()
        self.scale(self.current_zoom, self.current_zoom)

    def reset_zoom(self) -> None:
        self.set_zoom(1.0)

    def fit_to_scene_contents(self) -> None:
        scene = self.scene()
        if scene is None:
            self.reset_zoom()
            return

        bounds = scene.itemsBoundingRect()
        if bounds.isNull():
            bounds = scene.sceneRect()
        self.fit_target = bounds.adjusted(-40.0, -40.0, 40.0, 40.0)
        self.fitInView(self.fit_target, Qt.AspectRatioMode.KeepAspectRatio)
        fitted_zoom = self.transform().m11()
        if fitted_zoom < self.min_zoom or fitted_zoom > self.max_zoom:
            self.set_zoom(fitted_zoom)
        else:
            self.current_zoom = fitted_zoom


class OperationsPanel(QWidget):
    def __init__(self, visualizer: "LinkedListPySideVisualizer") -> None:
        super().__init__()
        self.visualizer = visualizer
        self.queue = visualizer.operation_queue
        self.setObjectName("operations_panel")
        self.setFixedWidth(PANEL_WIDTH)

        self.list_type_selector = QComboBox()
        self.list_type_selector.setObjectName("list_type_selector")
        self.list_type_selector.addItems(["singly", "doubly"])
        self.list_type_selector.setCurrentText(visualizer.ll_type)

        self.operation_selector = QComboBox()
        self.operation_selector.setObjectName("operation_selector")
        self.operation_selector.addItems(
            [
                "append",
                "prepend",
                "insert",
                "remove",
                "replace",
                "reverse",
                "sort",
                "cycle",
                "has_cycle",
                "clear",
            ]
        )

        self.value_input = QLineEdit()
        self.value_input.setObjectName("value_input")
        self.value_input.setPlaceholderText("value")

        self.index_input = QLineEdit()
        self.index_input.setObjectName("index_input")
        self.index_input.setPlaceholderText("index")

        self.sort_method_selector = QComboBox()
        self.sort_method_selector.setObjectName("sort_method_selector")
        self.sort_method_selector.addItems(["1", "2"])

        add_button = QPushButton("Add")
        add_button.clicked.connect(self.add_current_operation)
        load_button = QPushButton("Load File")
        load_button.clicked.connect(self.load_operations_file)
        clear_button = QPushButton("Clear")
        clear_button.clicked.connect(self.clear_operations)

        self.error_label = QLabel("")
        self.error_label.setObjectName("operation_error")
        self.error_label.setWordWrap(True)

        self.operation_history = QListWidget()
        self.operation_history.setObjectName("operation_history")

        self.list_type_selector.currentTextChanged.connect(lambda _text: self.apply_list_type())

        layout = QVBoxLayout()
        layout.addWidget(QLabel("List Type"))
        layout.addWidget(self.list_type_selector)
        layout.addWidget(QLabel("Operation"))
        layout.addWidget(self.operation_selector)
        layout.addWidget(QLabel("Value"))
        layout.addWidget(self.value_input)
        layout.addWidget(QLabel("Index"))
        layout.addWidget(self.index_input)
        layout.addWidget(QLabel("Sort Method"))
        layout.addWidget(self.sort_method_selector)
        layout.addWidget(add_button)
        layout.addWidget(load_button)
        layout.addWidget(clear_button)
        layout.addWidget(self.error_label)
        layout.addWidget(QLabel("History"))
        layout.addWidget(self.operation_history, stretch=1)
        self.setLayout(layout)
        self.refresh_history()

    def add_current_operation(self) -> None:
        try:
            self.queue.add_operation(
                self.operation_selector.currentText(),
                value_text=self.value_input.text(),
                index_text=self.index_input.text(),
                sort_method_text=self.sort_method_selector.currentText(),
            )
        except OperationInputError as exc:
            self.error_label.setText(str(exc))
            return
        self.error_label.setText("")
        self._after_queue_update()

    def clear_operations(self) -> None:
        self.queue.clear()
        self.error_label.setText("")
        self._after_queue_update()

    def apply_list_type(self) -> None:
        self.visualizer.ll_type = self.list_type_selector.currentText()
        self.visualizer.replay_current_operations()

    def load_operations_file(self, path: Path | None = None) -> None:
        if path is None:
            selected, _filter = QFileDialog.getOpenFileName(self, "Load Operations", "", "Text Files (*.txt);;All Files (*)")
            if not selected:
                return
            path = Path(selected)
        try:
            self.queue.load_operations_file(path)
        except OperationInputError as exc:
            self.error_label.setText(str(exc))
            return
        self.error_label.setText("")
        self._after_queue_update()

    def refresh_history(self) -> None:
        self.operation_history.clear()
        for _command, _args, label in self.queue.operations:
            self.operation_history.addItem(label)

    def set_current_operation(self, index: int) -> None:
        if 0 <= index < self.operation_history.count():
            self.operation_history.setCurrentRow(index)
        else:
            self.operation_history.clearSelection()

    def _after_queue_update(self) -> None:
        self.visualizer.set_operations(self.queue.operations)
        self.refresh_history()


class PlaybackControls(QWidget):
    def __init__(self, visualizer: "LinkedListPySideVisualizer") -> None:
        super().__init__()
        self.visualizer = visualizer
        self.setObjectName("playback_controls")

        self.jump_to_beginning_button = self._button("Start", "jump_to_beginning_button")
        self.previous_frame_button = self._button("Previous", "previous_frame_button")
        self.play_button = self._button("Play", "play_button")
        self.pause_button = self._button("Pause", "pause_button")
        self.next_frame_button = self._button("Next", "next_frame_button")
        self.jump_to_end_button = self._button("End", "jump_to_end_button")
        self.restart_button = self._button("Restart", "restart_button")
        self.fit_to_view_button = self._button("Fit", "fit_to_view_button")
        self.reset_zoom_button = self._button("Reset Zoom", "reset_zoom_button")
        self.export_screenshot_button = self._button("Export PNG", "export_screenshot_button")
        self.screenshot_status_label = QLabel(visualizer.screenshot_status)
        self.screenshot_status_label.setObjectName("screenshot_status")

        self.jump_to_beginning_button.clicked.connect(visualizer.jump_to_beginning)
        self.previous_frame_button.clicked.connect(visualizer.previous_frame)
        self.play_button.clicked.connect(visualizer.play_playback)
        self.pause_button.clicked.connect(visualizer.pause_playback)
        self.next_frame_button.clicked.connect(visualizer.next_frame)
        self.jump_to_end_button.clicked.connect(visualizer.jump_to_end)
        self.restart_button.clicked.connect(visualizer.restart_playback)
        self.fit_to_view_button.clicked.connect(visualizer.fit_to_view)
        self.reset_zoom_button.clicked.connect(visualizer.reset_zoom)
        self.export_screenshot_button.clicked.connect(visualizer.prompt_export_screenshot)

        layout = QHBoxLayout()
        layout.addWidget(self.jump_to_beginning_button)
        layout.addWidget(self.previous_frame_button)
        layout.addWidget(self.play_button)
        layout.addWidget(self.pause_button)
        layout.addWidget(self.next_frame_button)
        layout.addWidget(self.jump_to_end_button)
        layout.addWidget(self.restart_button)
        layout.addWidget(self.fit_to_view_button)
        layout.addWidget(self.reset_zoom_button)
        layout.addWidget(self.export_screenshot_button)
        layout.addWidget(self.screenshot_status_label)
        layout.addStretch(1)
        self.setLayout(layout)

    @staticmethod
    def _button(text: str, object_name: str) -> QPushButton:
        button = QPushButton(text)
        button.setObjectName(object_name)
        return button


class LinkedListPySideVisualizer(LinkedListAnimation):
    def __init__(
        self,
        ll_type: str,
        operations: list[Operation],
        width: int = DEFAULT_WIDTH,
        height: int = DEFAULT_HEIGHT,
        node_interval: float = DEFAULT_INTERVAL,
        arrow_interval: float = DEFAULT_INTERVAL,
        theme: PySideTheme = DEFAULT_PYSIDE_THEME,
    ) -> None:
        super().__init__(ll_type, operations, width, height, node_interval, arrow_interval)
        self.theme = theme
        self.operation_queue = OperationQueue(operations)
        self.playback = PlaybackController([])
        self.screenshot_status = ""
        self._frames: list[OperationFrame] = []
        self._operations_panel: OperationsPanel | None = None
        self._playback_controls: PlaybackControls | None = None
        self._app: QApplication | None = None
        self._scene: QGraphicsScene | None = None
        self._view: CanvasGraphicsView | None = None

    @property
    def scene(self) -> QGraphicsScene:
        if self._scene is None:
            self._ensure_qt_app()
            self._scene = QGraphicsScene()
        return self._scene

    @property
    def view(self) -> CanvasGraphicsView:
        if self._view is None:
            self._ensure_qt_app()
            self._view = CanvasGraphicsView(self.scene)
        return self._view

    def display(self):
        app = self._ensure_qt_app()
        self._ensure_qt_view()
        window = QMainWindow()
        window.setWindowTitle("Linked List Visualization")
        window.resize(self.width, self.height)
        central_widget = QWidget()
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.create_operations_panel())
        canvas_layout = QVBoxLayout()
        canvas_layout.setContentsMargins(0, 0, 0, 0)
        canvas_layout.addWidget(self.create_playback_controls())
        canvas_layout.addWidget(self.view, stretch=1)
        canvas_widget = QWidget()
        canvas_widget.setLayout(canvas_layout)
        layout.addWidget(canvas_widget, stretch=1)
        central_widget.setLayout(layout)
        window.setCentralWidget(central_widget)

        self._frames = self.build_frames(self.operations, self.node_interval)
        self.playback.set_frames(self._frames)

        def tick():
            self.advance_playback(1 / 60)

        self.render_playback_state()

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

    def create_operations_panel(self) -> OperationsPanel:
        if self._operations_panel is None:
            self._operations_panel = OperationsPanel(self)
        return self._operations_panel

    def create_playback_controls(self) -> PlaybackControls:
        if self._playback_controls is None:
            self._playback_controls = PlaybackControls(self)
        return self._playback_controls

    def set_operations(self, operations: list[Operation]) -> None:
        self.operations = list(operations)
        self.operation_queue.operations = list(operations)
        self.replay_current_operations()

    def replay_current_operations(self) -> None:
        self._frames = self.build_frames(self.operations, self.node_interval)
        self.playback.set_frames(self._frames)
        self.render_playback_state()

    def render_playback_state(self) -> None:
        frame = self.playback.current_frame
        if frame is None:
            self.render_first_frame([])
            return
        self.render_frame(
            self._frames,
            frame,
            self.playback.current_progress,
            self.playback.current_frame_index,
            self.playback.elapsed_in_frame,
        )

    def advance_playback(self, seconds: float) -> None:
        self.playback.advance(seconds)
        self.render_playback_state()

    def play_playback(self) -> None:
        self.playback.play()

    def pause_playback(self) -> None:
        self.playback.pause()

    def restart_playback(self) -> None:
        self.playback.restart()
        self.render_playback_state()

    def previous_frame(self) -> None:
        self.playback.step_previous()
        self.render_playback_state()

    def next_frame(self) -> None:
        self.playback.step_next()
        self.render_playback_state()

    def jump_to_beginning(self) -> None:
        self.playback.jump_to_beginning()
        self.render_playback_state()

    def jump_to_end(self) -> None:
        self.playback.jump_to_end()
        self.render_playback_state()

    def fit_to_view(self) -> None:
        self.view.fit_to_scene_contents()

    def reset_zoom(self) -> None:
        self.view.reset_zoom()

    def prompt_export_screenshot(self) -> bool:
        return self.export_screenshot()

    def export_screenshot(self, path: Path | None = None) -> bool:
        if path is None:
            selected, _filter = QFileDialog.getSaveFileName(
                self.view,
                "Export Screenshot",
                "linked-list.png",
                "PNG Images (*.png);;All Files (*)",
            )
            if not selected:
                self._set_screenshot_status("")
                return False
            path = Path(selected)

        if path.suffix.lower() != ".png":
            path = path.with_suffix(".png")

        scene_rect = self.scene.sceneRect()
        width = max(1, math.ceil(scene_rect.width()))
        height = max(1, math.ceil(scene_rect.height()))
        image = QImage(width, height, QImage.Format.Format_ARGB32)
        image.fill(self._color(self.theme.canvas))

        painter = QPainter(image)
        try:
            self.scene.render(painter, QRectF(image.rect()), scene_rect)
        finally:
            painter.end()

        try:
            saved = image.save(str(path))
        except ValueError:
            saved = False
        if not saved:
            self._set_screenshot_status(f"Unable to save screenshot to {path}")
            return False

        self._set_screenshot_status(f"Saved screenshot to {path}")
        return True

    def _set_screenshot_status(self, message: str) -> None:
        self.screenshot_status = message
        if self._playback_controls is not None:
            self._playback_controls.screenshot_status_label.setText(message)

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
        if self._operations_panel is not None:
            self._operations_panel.set_current_operation(frame_index)

        nodes_render, blink_on = self._resolve_nodes_to_render(frame, progress, elapsed)
        visuals = self._resolve_visuals(frame, nodes_render, progress)
        if not visuals:
            self._draw_empty_state()
            return
        self._draw_nodes(frame, visuals, progress, blink_on)
        anchor_map = self._draw_links(frame, visuals, progress)
        self._draw_cycle_link(frame, visuals, progress, anchor_map)
        self._resize_scene_to_contents()

    @property
    def minimum_row_spacing(self) -> int:
        arrow_corridor = max(48.0, self.theme.arrow_head_size * 2)
        return math.ceil(self.theme.node_height + arrow_corridor)

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
        spacing_y = max(
            float(self.minimum_row_spacing),
            usable_height / max(1, rows - 1),
        )

        visuals = []
        for index, node in enumerate(nodes):
            row = index // per_row
            col = index % per_row
            x = int(margin + col * spacing_x)
            y = int(margin + row * spacing_y)
            visuals.append(NodeVisual(node.node_id, node.value, (x, y), row, col))
        return visuals

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

    def _resize_scene_to_contents(self) -> None:
        content_bounds = self.scene.itemsBoundingRect().adjusted(-80.0, -80.0, 80.0, 80.0)
        viewport_bounds = QRectF(0.0, 0.0, float(self.width), float(self.height))
        self.scene.setSceneRect(viewport_bounds.united(content_bounds))

    def _draw_empty_state(self) -> None:
        item = self._text_item("No linked list operations yet", self.theme.empty_state_size, self.theme.empty_state_text)
        bounds = item.boundingRect()
        x = (self.width - bounds.width()) / 2
        y = (self.height - bounds.height()) / 2
        item.setPos(x, y)
        self.scene.addItem(item)

    def _draw_nodes(
        self,
        frame: OperationFrame,
        visuals: list[NodeVisual],
        progress: float,
        blink_on: bool,
    ) -> None:
        replace_phase = 0.6
        for visual in visuals:
            x, y = visual.position
            state = self.node_state_for(frame, visual, blink_on)
            if frame.op_type == "replace" and visual.node_id == frame.replaced_id and progress >= replace_phase:
                state = NodeVisualState.NORMAL
            node = LinkedListNodeItem(visual.value, state, self.theme, node_kind=self.ll_type)
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
    ) -> dict[int, tuple[QPointF, QPointF]]:
        anchor_map: dict[int, tuple[QPointF, QPointF]] = {}
        half_heights: dict[int, float] = {}
        for visual in visuals:
            scale = 1.0
            if frame.op_type == "add" and visual.node_id == frame.added_id:
                scale = 0.5 + 0.5 * progress
            node = self._node_item(visual.value)
            incoming = QPointF(visual.position[0] + node.incoming_anchor().x() * scale, visual.position[1])
            outgoing = QPointF(visual.position[0] + node.outgoing_anchor().x() * scale, visual.position[1])
            anchor_map[visual.node_id] = (incoming, outgoing)
            half_heights[visual.node_id] = (self.theme.node_height / 2) * scale

        bidirectional = self.ll_type == "doubly"
        for index in range(len(visuals) - 1):
            current = visuals[index]
            next_visual = visuals[index + 1]
            link_progress = self._link_progress(frame, progress, current.node_id, next_visual.node_id)

            if current.row != next_visual.row:
                start = (
                    float(current.position[0]),
                    current.position[1] + half_heights.get(current.node_id, 42.0),
                )
                end = (
                    float(next_visual.position[0]),
                    next_visual.position[1] - half_heights.get(next_visual.node_id, 42.0),
                )
                turn_y = current.position[1] + (next_visual.position[1] - current.position[1]) / 2
                path = [start, (start[0], turn_y), (end[0], turn_y), end]
                self._draw_polyline_arrow(path, self.theme.arrow, link_progress, self.theme.arrow_stroke_width)
                if bidirectional:
                    self._draw_polyline_arrow(
                        list(reversed(path)),
                        self.theme.arrow_muted,
                        link_progress,
                        self.theme.reverse_arrow_stroke_width,
                        item_kind="reverse-link",
                    )
            else:
                start_anchor = anchor_map[current.node_id][1]
                end_anchor = anchor_map[next_visual.node_id][0]
                start = (start_anchor.x(), start_anchor.y())
                end = (end_anchor.x(), end_anchor.y())
                if bidirectional:
                    self._draw_bidirectional_arrow(
                        start,
                        end,
                        self.theme.arrow_muted,
                        link_progress,
                        self.theme.reverse_arrow_stroke_width,
                    )
                else:
                    self._draw_arrow(start, end, self.theme.arrow, link_progress, self.theme.arrow_stroke_width)

        return anchor_map

    def _draw_cycle_link(
        self,
        frame: OperationFrame,
        visuals: list[NodeVisual],
        progress: float,
        anchor_map: dict[int, tuple[QPointF, QPointF]],
    ) -> None:
        if not frame.cycle_link:
            return
        visuals_by_id = {visual.node_id: visual for visual in visuals}
        cycle_end_id, cycle_start_id = frame.cycle_link
        cycle_end = visuals_by_id.get(cycle_end_id)
        cycle_start = visuals_by_id.get(cycle_start_id)
        if not cycle_end or not cycle_start:
            return

        start_anchor = anchor_map.get(cycle_end.node_id, (QPointF(*cycle_end.position), QPointF(*cycle_end.position)))[1]
        end_anchor = anchor_map.get(cycle_start.node_id, (QPointF(*cycle_start.position), QPointF(*cycle_start.position)))[0]
        start_point = (start_anchor.x(), start_anchor.y())
        end_point = (end_anchor.x(), end_anchor.y())
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

    def _draw_arrow(self, start, end, color, progress=1.0, width=2, arrow_size=None, item_kind="link") -> None:
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
        item.setData(0, item_kind)
        self.scene.addItem(item)
        if progress >= 0.98:
            self._draw_arrow_head(start, end, color, arrow_size, item_kind=f"{item_kind}-arrowhead")

    def _draw_bidirectional_arrow(self, start, end, color, progress=1.0, width=2, arrow_size=None) -> None:
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
        item.setData(0, "bidirectional-link")
        self.scene.addItem(item)
        if progress >= 0.98:
            self._draw_arrow_head(start, end, color, arrow_size, item_kind="bidirectional-link-arrowhead")
            self._draw_arrow_head(end, start, color, arrow_size, item_kind="bidirectional-link-arrowhead")

    def _draw_polyline_arrow(self, points, color, progress=1.0, width=2, arrow_size=None, item_kind="link") -> None:
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
        item.setData(0, item_kind)
        self.scene.addItem(item)
        if self.clamp(progress, 0.0, 1.0) >= 0.98:
            self._draw_arrow_head(segments[-1][0], segments[-1][1], color, arrow_size, item_kind=f"{item_kind}-arrowhead")

    def _draw_arrow_head(self, start, end, color, arrow_size=12, item_kind="link-arrowhead") -> None:
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
        arrow.setData(0, item_kind)
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
            self._draw_arrow_head(
                control_2,
                end,
                self.theme.cycle_arrow,
                self.theme.arrow_head_size,
                item_kind="cycle-link-arrowhead",
            )

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

    def _node_half_width(self, value: NodeValue) -> float:
        return self._node_item(value).boundingRect().width() / 2

    def _node_item(self, value: NodeValue) -> LinkedListNodeItem:
        item = LinkedListNodeItem(value, NodeVisualState.NORMAL, self.theme, node_kind=self.ll_type)
        return item


def _color(rgb) -> QColor:
    return QColor(int(rgb[0]), int(rgb[1]), int(rgb[2]))
