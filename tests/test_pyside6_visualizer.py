import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest

pytest.importorskip("PySide6")

from PySide6.QtWidgets import QApplication, QGraphicsEllipseItem

from classes.pyside6_visualizer import LinkedListPySideVisualizer


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

    node_items = [item for item in visualizer.scene.items() if isinstance(item, QGraphicsEllipseItem)]
    assert node_items
    app.processEvents()
