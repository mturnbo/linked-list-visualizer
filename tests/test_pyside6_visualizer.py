import os
import subprocess
import sys

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest

pytest.importorskip("PySide6")

from PySide6.QtWidgets import QApplication, QGraphicsPathItem, QGraphicsTextItem

from classes.pyside6_theme import NodeVisualState, PySideTheme
from classes.pyside6_visualizer import LinkedListNodeItem, LinkedListPySideVisualizer


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


def test_doubly_reverse_link_starts_inside_left_pointer_compartment():
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

    reverse_link = next(
        item
        for item in visualizer.scene.items()
        if isinstance(item, QGraphicsPathItem) and item.data(0) == "reverse-link"
    )
    second_node = next(
        item
        for item in visualizer.scene.items()
        if isinstance(item, LinkedListNodeItem) and item.value_text == "2"
    )
    first_element = reverse_link.path().elementAt(0)
    start_x = first_element.x
    assert second_node.left_pointer_rect is not None
    assert start_x > second_node.scenePos().x() + second_node.left_pointer_rect.left()
    assert start_x < second_node.scenePos().x() + second_node.value_rect.left()
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
