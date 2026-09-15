import os
import subprocess
import sys
from itertools import pairwise

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest

pytest.importorskip("PySide6")

from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QGraphicsPathItem,
    QGraphicsPolygonItem,
    QGraphicsScene,
    QGraphicsTextItem,
    QGraphicsView,
    QLineEdit,
    QListWidget,
    QPushButton,
)

from classes.pyside6_theme import NodeVisualState, PySideTheme
from classes.pyside6_visualizer import (
    CanvasGraphicsView,
    LinkedListNodeItem,
    LinkedListPySideVisualizer,
)


def test_pyside6_renderer_draws_supported_operation_frames():
    app = QApplication.instance() or QApplication([])
    visualizer = LinkedListPySideVisualizer(
        "singly",
        [
            ("append", [3], "append 3"),
            ("append", [1], "append 1"),
            ("prepend", [4], "prepend 4"),
            ("insert", [1, 2], "insert 2"),
            ("replace", [2, 9], "replace 9"),
            ("remove", [1], "remove 1"),
            ("reverse", [], "reverse"),
            ("sort", [1], "sort"),
            ("cycle", [0], "cycle"),
            ("has_cycle", [], "has_cycle"),
        ],
    )
    frames = visualizer.build_frames(visualizer.operations, visualizer.node_interval)

    for index, frame in enumerate(frames):
        visualizer.render_frame(frames, frame, progress=1.0, frame_index=index, elapsed=1.0)
        assert visualizer.scene.items()

    node_items = [item for item in visualizer.scene.items() if isinstance(item, LinkedListNodeItem)]
    assert node_items
    app.processEvents()


def test_pyside6_renderer_uses_custom_rounded_node_items():
    app = QApplication.instance() or QApplication([])
    visualizer = LinkedListPySideVisualizer(
        "singly",
        [("append", ["long-value"], "append long-value")],
    )
    frames = visualizer.build_frames(visualizer.operations, visualizer.node_interval)

    visualizer.render_first_frame(frames)

    node_items = [item for item in visualizer.scene.items() if isinstance(item, LinkedListNodeItem)]
    assert len(node_items) == 1
    assert node_items[0].visual_state == NodeVisualState.NEW
    assert node_items[0].boundingRect().width() >= node_items[0].theme.node_min_width
    assert node_items[0].boundingRect().width() > node_items[0].theme.node_height
    app.processEvents()


def test_node_item_uses_singly_pointer_compartment_layout():
    app = QApplication.instance() or QApplication([])
    theme = PySideTheme(pointer_cell_width=28.0)
    node = LinkedListNodeItem("99", NodeVisualState.NORMAL, theme, node_kind="singly")

    assert node.node_kind == "singly"
    assert node.pointer_cell_count == 1
    assert node.value_rect.width() > node.pointer_cell_width
    assert node.right_pointer_rect.width() == node.pointer_cell_width
    assert node.left_pointer_rect is None
    assert node.outgoing_anchor().x() > node.value_rect.right()
    assert node.outgoing_anchor().x() < node.boundingRect().right()
    app.processEvents()


def test_node_item_uses_doubly_pointer_compartment_layout():
    app = QApplication.instance() or QApplication([])
    theme = PySideTheme(pointer_cell_width=28.0)
    node = LinkedListNodeItem("99", NodeVisualState.NORMAL, theme, node_kind="doubly")

    assert node.node_kind == "doubly"
    assert node.pointer_cell_count == 2
    assert node.left_pointer_rect is not None
    assert node.left_pointer_rect.width() == node.pointer_cell_width
    assert node.right_pointer_rect.width() == node.pointer_cell_width
    assert node.value_rect.width() > node.pointer_cell_width
    assert node.incoming_anchor().x() < node.value_rect.left()
    assert node.outgoing_anchor().x() > node.value_rect.right()
    app.processEvents()


def test_singly_link_starts_inside_pointer_compartment():
    app = QApplication.instance() or QApplication([])
    visualizer = LinkedListPySideVisualizer(
        "singly",
        [
            ("append", [1], "append 1"),
            ("append", [2], "append 2"),
        ],
    )
    frames = visualizer.build_frames(visualizer.operations, visualizer.node_interval)

    visualizer.render_frame(frames, frames[-1], progress=1.0, frame_index=1, elapsed=1.0)

    link = next(item for item in visualizer.scene.items() if isinstance(item, QGraphicsPathItem) and item.data(0) == "link")
    first_node = next(
        item
        for item in visualizer.scene.items()
        if isinstance(item, LinkedListNodeItem) and item.value_text == "1"
    )
    first_element = link.path().elementAt(0)
    start_x = first_element.x
    assert start_x > first_node.scenePos().x() + first_node.value_rect.right()
    assert start_x < first_node.scenePos().x() + first_node.boundingRect().right()
    app.processEvents()


def test_doubly_link_uses_double_arrowheads_inside_pointer_compartments():
    app = QApplication.instance() or QApplication([])
    visualizer = LinkedListPySideVisualizer(
        "doubly",
        [
            ("append", [1], "append 1"),
            ("append", [2], "append 2"),
        ],
    )
    frames = visualizer.build_frames(visualizer.operations, visualizer.node_interval)

    visualizer.render_frame(frames, frames[-1], progress=1.0, frame_index=1, elapsed=1.0)

    bidirectional_link = next(
        item
        for item in visualizer.scene.items()
        if isinstance(item, QGraphicsPathItem) and item.data(0) == "bidirectional-link"
    )
    first_node = next(
        item
        for item in visualizer.scene.items()
        if isinstance(item, LinkedListNodeItem) and item.value_text == "1"
    )
    second_node = next(
        item
        for item in visualizer.scene.items()
        if isinstance(item, LinkedListNodeItem) and item.value_text == "2"
    )
    first_element = bidirectional_link.path().elementAt(0)
    last_element = bidirectional_link.path().elementAt(bidirectional_link.path().elementCount() - 1)
    start_x = first_element.x
    end_x = last_element.x
    assert start_x > first_node.scenePos().x() + first_node.value_rect.right()
    assert start_x < first_node.scenePos().x() + first_node.boundingRect().right()
    assert second_node.left_pointer_rect is not None
    assert end_x > second_node.scenePos().x() + second_node.left_pointer_rect.left()
    assert end_x < second_node.scenePos().x() + second_node.value_rect.left()
    arrowheads = [
        item
        for item in visualizer.scene.items()
        if isinstance(item, QGraphicsPolygonItem) and item.data(0) == "bidirectional-link-arrowhead"
    ]
    assert len(arrowheads) == 2
    assert not any(
        isinstance(item, QGraphicsPathItem) and item.data(0) == "reverse-link"
        for item in visualizer.scene.items()
    )
    app.processEvents()


def test_pyside6_renderer_assigns_distinct_node_states():
    app = QApplication.instance() or QApplication([])
    visualizer = LinkedListPySideVisualizer(
        "singly",
        [
            ("append", [1], "append 1"),
            ("append", [2], "append 2"),
            ("append", [3], "append 3"),
            ("replace", [0, 9], "replace 9"),
            ("remove", [1], "remove 1"),
            ("cycle", [0], "cycle"),
        ],
    )
    frames = visualizer.build_frames(visualizer.operations, visualizer.node_interval)

    replace_frame = frames[3]
    assert visualizer.node_state_for(replace_frame, replace_frame.nodes_after[0], blink_on=True) == NodeVisualState.CHANGED
    assert visualizer.node_state_for(replace_frame, replace_frame.nodes_after[2], blink_on=False) == NodeVisualState.CURRENT

    remove_frame = frames[4]
    assert visualizer.node_state_for(remove_frame, remove_frame.nodes_before[1], blink_on=True) == NodeVisualState.REMOVING

    cycle_frame = frames[5]
    assert visualizer.node_state_for(cycle_frame, cycle_frame.nodes_after[0], blink_on=False) == NodeVisualState.CYCLE_ENDPOINT
    assert visualizer.node_state_for(cycle_frame, cycle_frame.nodes_after[-1], blink_on=False) == NodeVisualState.CYCLE_ENDPOINT
    app.processEvents()


def test_pyside6_renderer_draws_curved_cycle_link_and_styled_paths():
    app = QApplication.instance() or QApplication([])
    visualizer = LinkedListPySideVisualizer(
        "singly",
        [
            ("append", [1], "append 1"),
            ("append", [2], "append 2"),
            ("append", [3], "append 3"),
            ("cycle", [0], "cycle"),
        ],
    )
    frames = visualizer.build_frames(visualizer.operations, visualizer.node_interval)

    visualizer.render_frame(frames, frames[-1], progress=1.0, frame_index=len(frames) - 1, elapsed=1.0)

    path_items = [item for item in visualizer.scene.items() if isinstance(item, QGraphicsPathItem)]
    cycle_paths = [item for item in path_items if item.data(0) == "cycle-link"]
    assert cycle_paths
    assert any(path.path().elementCount() > 2 for path in cycle_paths)
    assert all(path.pen().widthF() >= visualizer.theme.arrow_stroke_width for path in path_items)
    app.processEvents()


def test_pyside6_renderer_accepts_theme_without_touching_animation_logic():
    app = QApplication.instance() or QApplication([])
    theme = PySideTheme(node_min_width=112.0, node_height=60.0)
    visualizer = LinkedListPySideVisualizer(
        "singly",
        [("append", [1], "append 1")],
        theme=theme,
    )
    frames = visualizer.build_frames(visualizer.operations, visualizer.node_interval)

    visualizer.render_first_frame(frames)

    node_items = [item for item in visualizer.scene.items() if isinstance(item, LinkedListNodeItem)]
    assert node_items[0].theme is theme
    assert node_items[0].node_kind == "singly"
    assert node_items[0].boundingRect().width() >= 112.0
    app.processEvents()


def test_pyside6_renderer_renders_intentional_empty_state():
    app = QApplication.instance() or QApplication([])
    visualizer = LinkedListPySideVisualizer("singly", [])

    visualizer.render_first_frame([])

    messages = [item.toPlainText() for item in visualizer.scene.items() if isinstance(item, QGraphicsTextItem)]
    assert "No linked list operations yet" in messages
    app.processEvents()


def test_pyside6_renderer_centers_empty_state_in_full_canvas():
    app = QApplication.instance() or QApplication([])
    visualizer = LinkedListPySideVisualizer("singly", [], width=800, height=400)

    visualizer.render_first_frame([])

    message = next(item for item in visualizer.scene.items() if isinstance(item, QGraphicsTextItem))
    assert message.sceneBoundingRect().center().x() == pytest.approx(400, abs=2)
    app.processEvents()


def test_pyside6_renderer_does_not_draw_operations_history_in_scene():
    app = QApplication.instance() or QApplication([])
    visualizer = LinkedListPySideVisualizer(
        "singly",
        [
            ("append", [1], "append 1"),
            ("append", [2], "append 2"),
        ],
    )
    frames = visualizer.build_frames(visualizer.operations, visualizer.node_interval)

    visualizer.render_frame(frames, frames[-1], progress=1.0, frame_index=1, elapsed=1.0)

    scene_text = [item.toPlainText() for item in visualizer.scene.items() if isinstance(item, QGraphicsTextItem)]
    assert "Operations" not in scene_text
    assert "append 1" not in scene_text
    assert "append 2" not in scene_text
    app.processEvents()


def test_pyside6_renderer_lays_out_nodes_across_full_canvas():
    app = QApplication.instance() or QApplication([])
    visualizer = LinkedListPySideVisualizer(
        "singly",
        [("append", [1], "append 1")],
        width=800,
        height=400,
    )
    frames = visualizer.build_frames(visualizer.operations, visualizer.node_interval)

    visual = visualizer.layout_nodes(frames[-1].nodes_after, visualizer.width, visualizer.height)[0]

    assert visual.position == (80, 80)
    app.processEvents()


def test_pyside6_visualizer_can_be_constructed_before_qapplication():
    script = """
import os
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
from classes.pyside6_visualizer import LinkedListPySideVisualizer
visualizer = LinkedListPySideVisualizer("singly", [("append", [1], "append 1")])
frames = visualizer.build_frames(visualizer.operations, visualizer.node_interval)
visualizer.render_first_frame(frames)
assert visualizer.scene.items()
print("ok")
"""

    result = subprocess.run(
        [sys.executable, "-c", script],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    assert "ok" in result.stdout


def test_operations_panel_exposes_expected_controls():
    app = QApplication.instance() or QApplication([])
    visualizer = LinkedListPySideVisualizer("singly", [])

    panel = visualizer.create_operations_panel()

    assert panel.findChild(QComboBox, "list_type_selector") is not None
    assert panel.findChild(QComboBox, "operation_selector") is not None
    assert panel.findChild(QLineEdit, "value_input") is not None
    assert panel.findChild(QLineEdit, "index_input") is not None
    assert panel.findChild(QComboBox, "sort_method_selector") is not None
    assert panel.findChild(QListWidget, "operation_history") is not None
    app.processEvents()


def test_operations_panel_adds_operation_and_refreshes_history():
    app = QApplication.instance() or QApplication([])
    visualizer = LinkedListPySideVisualizer("singly", [])
    panel = visualizer.create_operations_panel()

    panel.operation_selector.setCurrentText("append")
    panel.value_input.setText("42")
    panel.add_current_operation()

    assert visualizer.operations == [("append", [42], "append 42")]
    assert panel.operation_history.count() == 1
    assert panel.operation_history.item(0).text() == "append 42"
    assert panel.error_label.text() == ""
    app.processEvents()


def test_operations_panel_shows_inline_validation_error():
    app = QApplication.instance() or QApplication([])
    visualizer = LinkedListPySideVisualizer("singly", [])
    panel = visualizer.create_operations_panel()

    panel.operation_selector.setCurrentText("remove")
    panel.index_input.setText("abc")
    panel.add_current_operation()

    assert visualizer.operations == []
    assert "integer index" in panel.error_label.text()
    app.processEvents()


def test_operations_panel_clear_resets_scene_and_history():
    app = QApplication.instance() or QApplication([])
    visualizer = LinkedListPySideVisualizer("singly", [("append", [1], "append 1")])
    panel = visualizer.create_operations_panel()

    panel.operation_selector.setCurrentText("clear")
    panel.add_current_operation()

    assert visualizer.operations == []
    assert panel.operation_history.count() == 0
    messages = [item.toPlainText() for item in visualizer.scene.items() if isinstance(item, QGraphicsTextItem)]
    assert "No linked list operations yet" in messages
    app.processEvents()


def test_operations_panel_updates_list_type_and_replays():
    app = QApplication.instance() or QApplication([])
    visualizer = LinkedListPySideVisualizer("singly", [("append", [1], "append 1")])
    panel = visualizer.create_operations_panel()

    panel.list_type_selector.setCurrentText("doubly")
    panel.apply_list_type()

    assert visualizer.ll_type == "doubly"
    node_items = [item for item in visualizer.scene.items() if isinstance(item, LinkedListNodeItem)]
    assert node_items
    assert all(item.node_kind == "doubly" for item in node_items)
    app.processEvents()


def test_operations_panel_loads_file_and_replays(tmp_path):
    app = QApplication.instance() or QApplication([])
    ops_file = tmp_path / "ops.txt"
    ops_file.write_text("append 1\nappend 2\n", encoding="utf-8")
    visualizer = LinkedListPySideVisualizer("singly", [])
    panel = visualizer.create_operations_panel()

    panel.load_operations_file(ops_file)

    assert visualizer.operations == [("append", [1], "append 1"), ("append", [2], "append 2")]
    assert panel.operation_history.count() == 2
    node_items = [item for item in visualizer.scene.items() if isinstance(item, LinkedListNodeItem)]
    assert node_items
    app.processEvents()


def test_playback_controls_expose_expected_buttons():
    app = QApplication.instance() or QApplication([])
    visualizer = LinkedListPySideVisualizer("singly", [])

    controls = visualizer.create_playback_controls()

    assert controls.findChild(QPushButton, "play_button") is not None
    assert controls.findChild(QPushButton, "pause_button") is not None
    assert controls.findChild(QPushButton, "restart_button") is not None
    assert controls.findChild(QPushButton, "previous_frame_button") is not None
    assert controls.findChild(QPushButton, "next_frame_button") is not None
    assert controls.findChild(QPushButton, "jump_to_beginning_button") is not None
    assert controls.findChild(QPushButton, "jump_to_end_button") is not None
    assert controls.findChild(QPushButton, "fit_to_view_button") is not None
    assert controls.findChild(QPushButton, "reset_zoom_button") is not None
    app.processEvents()


def test_canvas_graphics_view_clamps_and_resets_zoom():
    app = QApplication.instance() or QApplication([])
    view = CanvasGraphicsView(QGraphicsScene())

    view.set_zoom(20.0)
    assert view.current_zoom == view.max_zoom
    assert view.transform().m11() == pytest.approx(view.max_zoom)

    view.set_zoom(0.01)
    assert view.current_zoom == view.min_zoom
    assert view.transform().m11() == pytest.approx(view.min_zoom)

    view.reset_zoom()
    assert view.current_zoom == 1.0
    assert view.transform().m11() == pytest.approx(1.0)
    assert view.dragMode() == QGraphicsView.DragMode.ScrollHandDrag
    app.processEvents()


def test_canvas_zoom_does_not_change_node_layout_state():
    app = QApplication.instance() or QApplication([])
    visualizer = LinkedListPySideVisualizer(
        "singly",
        [
            ("append", [value], f"append {value}")
            for value in range(8)
        ],
        width=800,
        height=400,
    )
    frames = visualizer.build_frames(visualizer.operations, visualizer.node_interval)
    before = visualizer.layout_nodes(frames[-1].nodes_after, visualizer.width, visualizer.height)

    assert isinstance(visualizer.view, CanvasGraphicsView)
    visualizer.view.set_zoom(2.0)
    after = visualizer.layout_nodes(frames[-1].nodes_after, visualizer.width, visualizer.height)

    assert [visual.position for visual in after] == [visual.position for visual in before]
    app.processEvents()


def test_wrapped_node_rows_keep_arrow_spacing_when_canvas_is_short():
    app = QApplication.instance() or QApplication([])
    visualizer = LinkedListPySideVisualizer(
        "singly",
        [
            ("append", [value], f"append {value}")
            for value in range(25)
        ],
        width=700,
        height=360,
    )
    frames = visualizer.build_frames(visualizer.operations, visualizer.node_interval)

    visuals = visualizer.layout_nodes(frames[-1].nodes_after, visualizer.width, visualizer.height)
    row_y_positions = sorted({visual.position[1] for visual in visuals})
    row_gaps = [
        next_y - current_y
        for current_y, next_y in pairwise(row_y_positions)
    ]

    assert row_gaps
    assert min(row_gaps) >= visualizer.minimum_row_spacing
    app.processEvents()


def test_scene_rect_expands_to_wrapped_node_rows():
    app = QApplication.instance() or QApplication([])
    visualizer = LinkedListPySideVisualizer(
        "singly",
        [
            ("append", [value], f"append {value}")
            for value in range(25)
        ],
        width=700,
        height=360,
    )
    frames = visualizer.build_frames(visualizer.operations, visualizer.node_interval)

    visualizer.render_frame(frames, frames[-1], progress=1.0, frame_index=len(frames) - 1, elapsed=1.0)

    assert visualizer.scene.sceneRect().contains(visualizer.scene.itemsBoundingRect())
    assert visualizer.scene.sceneRect().height() > visualizer.height
    app.processEvents()


def test_fit_to_view_frames_current_scene_contents():
    app = QApplication.instance() or QApplication([])
    visualizer = LinkedListPySideVisualizer(
        "singly",
        [
            ("append", [value], f"append {value}")
            for value in range(12)
        ],
        width=900,
        height=500,
    )
    frames = visualizer.build_frames(visualizer.operations, visualizer.node_interval)
    visualizer.render_frame(frames, frames[-1], progress=1.0, frame_index=len(frames) - 1, elapsed=1.0)
    assert isinstance(visualizer.view, CanvasGraphicsView)
    visualizer.view.resize(420, 240)
    visualizer.view.set_zoom(visualizer.view.max_zoom)
    scene_bounds = visualizer.scene.itemsBoundingRect()

    visualizer.fit_to_view()

    assert visualizer.view.current_zoom <= visualizer.view.max_zoom
    assert visualizer.view.current_zoom >= visualizer.view.min_zoom
    assert visualizer.view.fit_target.contains(scene_bounds)
    app.processEvents()


def test_reset_zoom_button_restores_canvas_scale():
    app = QApplication.instance() or QApplication([])
    visualizer = LinkedListPySideVisualizer("singly", [("append", [1], "append 1")])
    controls = visualizer.create_playback_controls()
    assert isinstance(visualizer.view, CanvasGraphicsView)
    visualizer.view.set_zoom(2.0)

    controls.reset_zoom_button.click()

    assert visualizer.view.current_zoom == 1.0
    assert visualizer.view.transform().m11() == pytest.approx(1.0)
    app.processEvents()


def test_playback_controls_pause_resume_and_step_scene():
    app = QApplication.instance() or QApplication([])
    visualizer = LinkedListPySideVisualizer(
        "singly",
        [
            ("append", [1], "append 1"),
            ("append", [2], "append 2"),
        ],
    )
    panel = visualizer.create_operations_panel()
    visualizer.replay_current_operations()

    visualizer.pause_playback()
    visualizer.advance_playback(1.0)
    assert visualizer.playback.current_frame_index == 0

    visualizer.play_playback()
    visualizer.advance_playback(visualizer.node_interval)
    assert visualizer.playback.current_frame_index == 1
    assert panel.operation_history.currentRow() == 1

    visualizer.previous_frame()
    assert visualizer.playback.current_frame_index == 0
    assert panel.operation_history.currentRow() == 0
    app.processEvents()


def test_restart_playback_returns_to_first_frame():
    app = QApplication.instance() or QApplication([])
    visualizer = LinkedListPySideVisualizer(
        "singly",
        [
            ("append", [1], "append 1"),
            ("append", [2], "append 2"),
        ],
    )
    visualizer.replay_current_operations()
    visualizer.jump_to_end()

    visualizer.restart_playback()

    assert visualizer.playback.current_frame_index == 0
    assert visualizer.playback.elapsed_in_frame == 0.0
    assert visualizer.playback.playing
    app.processEvents()
