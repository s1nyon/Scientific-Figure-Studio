"""Editable configuration for the round-03 reference-guided figure."""

FIGURE_ID = "round_03_nature_reference"
FIGURE_WIDTH = 7.20
FIGURE_HEIGHT = 4.30
DPI = 600
STYLE_NAME = "algorithm_research"
PALETTE_NAME = "algorithm_research"

BASE_FONT_SIZE = 8.1
PANEL_TITLE_SIZE = 8.7
PANEL_LABEL_SIZE = 9.5
FOOTNOTE_FONT_SIZE = 6.4
LEGEND_FONT_SIZE = 7.1

LINE_WIDTH = 1.45
DELTA_LINE_WIDTH = 1.05
MARKER_SIZE = 4.0
DELTA_MARKER_SIZE = 3.4
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
GRID_TOP = 0.875
GRID_BOTTOM = 0.19
GRID_HSPACE = 0.52
HERO_HEIGHT_RATIO = 3.65
DELTA_HEIGHT_RATIO = 0.88
OBJECTIVE_YLIM = (0.82, 2.48)
DELTA_YLIM = (-0.46, 0.07)

PANEL_A_TITLE = "Objective trajectory"
PANEL_B_TITLE = "Signed adjacent update"
DELTA_NOTE = r"$\Delta$ objective = current$_{t}$ - current$_{t-1}$"
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
    "panel_title_size": PANEL_TITLE_SIZE,
    "panel_label_size": PANEL_LABEL_SIZE,
    "footnote_font_size": FOOTNOTE_FONT_SIZE,
    "legend_font_size": LEGEND_FONT_SIZE,
    "line_width": LINE_WIDTH,
    "delta_line_width": DELTA_LINE_WIDTH,
    "marker_size": MARKER_SIZE,
    "delta_marker_size": DELTA_MARKER_SIZE,
    "axes_line_width": AXES_LINE_WIDTH,
    "objective_ylim": OBJECTIVE_YLIM,
    "delta_ylim": DELTA_YLIM,
    "objective_direction": OBJECTIVE_DIRECTION,
    "algorithm_order": ALGORITHM_ORDER,
    "algorithm_colors": ALGORITHM_COLORS,
    "algorithm_markers": ALGORITHM_MARKERS,
    "grid_left": GRID_LEFT,
    "grid_right": GRID_RIGHT,
    "grid_top": GRID_TOP,
    "grid_bottom": GRID_BOTTOM,
    "grid_hspace": GRID_HSPACE,
    "hero_height_ratio": HERO_HEIGHT_RATIO,
    "delta_height_ratio": DELTA_HEIGHT_RATIO,
    "panel_a_title": PANEL_A_TITLE,
    "panel_b_title": PANEL_B_TITLE,
    "delta_note": DELTA_NOTE,
    "data_status_note": DATA_STATUS_NOTE,
    "output_formats": OUTPUT_FORMATS,
    "data_file": DATA_FILE,
}
