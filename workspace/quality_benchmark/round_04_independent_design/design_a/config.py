"""Editable configuration for Round 04 Design A: minimal trajectory figure."""

FIGURE_ID = "round_04_design_a_minimal"
FIGURE_WIDTH = 7.20
FIGURE_HEIGHT = 3.55
DPI = 600
STYLE_NAME = "algorithm_research"
PALETTE_NAME = "algorithm_research"

BASE_FONT_SIZE = 8.2
TITLE_SIZE = 9.0
FOOTNOTE_SIZE = 6.4
LINE_WIDTH = 1.55
MARKER_SIZE = 4.3
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

GRID_LEFT = 0.095
GRID_RIGHT = 0.985
GRID_TOP = 0.86
GRID_BOTTOM = 0.21
OBJECTIVE_YLIM = (0.82, 2.48)
X_LIM = (0.72, 12.30)
TITLE = "Objective trajectory"
DATA_STATUS_NOTE = "illustrative practice data · no replicate runs or uncertainty estimates"
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
    "title_size": TITLE_SIZE,
    "footnote_size": FOOTNOTE_SIZE,
    "line_width": LINE_WIDTH,
    "marker_size": MARKER_SIZE,
    "axes_line_width": AXES_LINE_WIDTH,
    "objective_direction": OBJECTIVE_DIRECTION,
    "algorithm_order": ALGORITHM_ORDER,
    "algorithm_colors": ALGORITHM_COLORS,
    "algorithm_markers": ALGORITHM_MARKERS,
    "grid_left": GRID_LEFT,
    "grid_right": GRID_RIGHT,
    "grid_top": GRID_TOP,
    "grid_bottom": GRID_BOTTOM,
    "objective_ylim": OBJECTIVE_YLIM,
    "x_lim": X_LIM,
    "title": TITLE,
    "data_status_note": DATA_STATUS_NOTE,
    "output_formats": OUTPUT_FORMATS,
    "data_file": DATA_FILE,
}
