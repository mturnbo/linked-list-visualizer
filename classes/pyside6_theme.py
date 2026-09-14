from dataclasses import dataclass
from enum import StrEnum

Color = tuple[int, int, int]


class NodeVisualState(StrEnum):
    NORMAL = "normal"
    NEW = "new"
    CHANGED = "changed"
    REMOVING = "removing"
    CURRENT = "current"
    CYCLE_ENDPOINT = "cycle_endpoint"


@dataclass(frozen=True)
class NodeStyle:
    fill: Color
    stroke: Color
    text: Color
    stroke_width: float


@dataclass(frozen=True)
class PySideTheme:
    canvas: Color = (245, 247, 250)
    panel_fill: Color = (31, 41, 55)
    panel_stroke: Color = (75, 85, 99)
    panel_text: Color = (229, 231, 235)
    panel_current_text: Color = (251, 191, 36)
    arrow: Color = (55, 65, 81)
    arrow_muted: Color = (107, 114, 128)
    cycle_arrow: Color = (5, 150, 105)
    node_min_width: float = 74.0
    node_height: float = 52.0
    node_padding_x: float = 18.0
    node_radius: float = 14.0
    node_stroke_width: float = 2.0
    node_font_family: str = "Avenir"
    node_font_size: int = 18
    panel_title_size: int = 24
    panel_text_size: int = 18
    arrow_stroke_width: float = 2.5
    reverse_arrow_stroke_width: float = 1.6
    cycle_arrow_stroke_width: float = 3.0
    arrow_head_size: float = 12.0

    def node_style(self, state: NodeVisualState) -> NodeStyle:
        styles = {
            NodeVisualState.NORMAL: NodeStyle((255, 255, 255), (30, 64, 175), (17, 24, 39), self.node_stroke_width),
            NodeVisualState.NEW: NodeStyle((254, 243, 199), (217, 119, 6), (17, 24, 39), self.node_stroke_width + 0.5),
            NodeVisualState.CHANGED: NodeStyle((219, 234, 254), (37, 99, 235), (17, 24, 39), self.node_stroke_width + 0.5),
            NodeVisualState.REMOVING: NodeStyle((254, 226, 226), (220, 38, 38), (17, 24, 39), self.node_stroke_width + 0.5),
            NodeVisualState.CURRENT: NodeStyle((236, 253, 245), (5, 150, 105), (17, 24, 39), self.node_stroke_width + 0.5),
            NodeVisualState.CYCLE_ENDPOINT: NodeStyle((204, 251, 241), (13, 148, 136), (17, 24, 39), self.node_stroke_width + 1.0),
        }
        return styles[state]


DEFAULT_PYSIDE_THEME = PySideTheme()
