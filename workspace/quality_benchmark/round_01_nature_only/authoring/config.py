"""User-editable configuration for the round-01 Nature-style convergence figure."""

FIGURE_ID = "round_01_nature_only"
FIGURE_WIDTH = 7.20
FIGURE_HEIGHT = 5.10
DPI = 600
STYLE_NAME = "algorithm_research"
PALETTE_NAME = "algorithm_research"

# Typography is expressed in final-figure points so the same values remain useful
# when the figure is inserted at approximately double-column width.
BASE_FONT_SIZE = 8.0
TITLE_FONT_SIZE = 8.7
HEADER_FONT_SIZE = 10.0
PANEL_LABEL_SIZE = 9.0
FOOTNOTE_FONT_SIZE = 6.5

LINE_WIDTH = 2.35
CURRENT_LINE_WIDTH = 1.05
MARKER_SIZE = 4.6
CURRENT_MARKER_SIZE = 3.8
AXES_LINE_WIDTH = 0.75

OBJECTIVE_DIRECTION = "minimize"
ALGORITHM_ORDER = ("Proposed", "Adaptive", "Baseline")
ALGORITHM_COLORS = {
    "Proposed": "#166A8F",
    "Adaptive": "#2A9D8F",
    "Baseline": "#71808C",
}
ALGORITHM_MARKERS = {
    "Proposed": "o",
    "Adaptive": "s",
    "Baseline": "^",
}

# All frequently adjusted layout and annotation values live here.
GRID_LEFT = 0.09
GRID_RIGHT = 0.985
GRID_TOP = 0.80
GRID_BOTTOM = 0.17
GRID_WSPACE = 0.38
GRID_HSPACE = 0.64
MAIN_WIDTH_RATIO = 1.66
SUPPORT_WIDTH_RATIO = 1.00
PANEL_LABEL_X = -0.06
PANEL_LABEL_Y = 1.08
PANEL_TITLE_PAD = 12.0

TITLE = "Convergence profiles and update behavior"
SUBTITLE = "Direction-aware view of the supplied illustrative trajectories"
DATA_STATUS_NOTE = "illustrative practice data  |  no replicate runs; no uncertainty band"

OUTPUT_FORMATS = ("png", "svg", "pdf")
DATA_FILE = "../../../../examples/data/convergence_practice.csv"

CONFIG = {
    "figure_id": FIGURE_ID,
    "figure_width": FIGURE_WIDTH,
    "figure_height": FIGURE_HEIGHT,
    "dpi": DPI,
    "style_name": STYLE_NAME,
    "palette_name": PALETTE_NAME,
    "base_font_size": BASE_FONT_SIZE,
    "title_font_size": TITLE_FONT_SIZE,
    "header_font_size": HEADER_FONT_SIZE,
    "panel_label_size": PANEL_LABEL_SIZE,
    "footnote_font_size": FOOTNOTE_FONT_SIZE,
    "line_width": LINE_WIDTH,
    "current_line_width": CURRENT_LINE_WIDTH,
    "marker_size": MARKER_SIZE,
    "current_marker_size": CURRENT_MARKER_SIZE,
    "axes_line_width": AXES_LINE_WIDTH,
    "objective_direction": OBJECTIVE_DIRECTION,
    "algorithm_order": ALGORITHM_ORDER,
    "algorithm_colors": ALGORITHM_COLORS,
    "algorithm_markers": ALGORITHM_MARKERS,
    "grid_left": GRID_LEFT,
    "grid_right": GRID_RIGHT,
    "grid_top": GRID_TOP,
    "grid_bottom": GRID_BOTTOM,
    "grid_wspace": GRID_WSPACE,
    "grid_hspace": GRID_HSPACE,
    "main_width_ratio": MAIN_WIDTH_RATIO,
    "support_width_ratio": SUPPORT_WIDTH_RATIO,
    "panel_label_x": PANEL_LABEL_X,
    "panel_label_y": PANEL_LABEL_Y,
    "panel_title_pad": PANEL_TITLE_PAD,
    "title": TITLE,
    "subtitle": SUBTITLE,
    "data_status_note": DATA_STATUS_NOTE,
    "output_formats": OUTPUT_FORMATS,
    "data_file": DATA_FILE,
}
