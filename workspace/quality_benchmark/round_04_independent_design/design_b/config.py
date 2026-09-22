"""Editable configuration for Round 04 Design B: path plus endpoint summary."""

FIGURE_ID = "round_04_design_b_path_endpoint"
FIGURE_WIDTH = 7.20
FIGURE_HEIGHT = 4.05
DPI = 600
STYLE_NAME = "algorithm_research"
PALETTE_NAME = "algorithm_research"

BASE_FONT_SIZE = 8.0
TITLE_SIZE = 8.8
FOOTNOTE_SIZE = 6.2
LINE_WIDTH = 1.45
MARKER_SIZE = 4.0
AXES_LINE_WIDTH = 0.75
ENDPOINT_LINE_WIDTH = 1.25
ENDPOINT_MARKER_SIZE = 5.4

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

MAIN_RECT = (0.085, 0.235, 0.575, 0.595)
SUMMARY_RECT = (0.735, 0.235, 0.235, 0.595)
OBJECTIVE_YLIM = (0.82, 2.48)
MAIN_X_LIM = (0.72, 12.40)
SUMMARY_X_LIM = (0.72, 2.88)
TITLE_MAIN = "Objective path"
TITLE_SUMMARY = "Start → end"
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
    "endpoint_line_width": ENDPOINT_LINE_WIDTH,
    "endpoint_marker_size": ENDPOINT_MARKER_SIZE,
    "objective_direction": OBJECTIVE_DIRECTION,
    "algorithm_order": ALGORITHM_ORDER,
    "algorithm_colors": ALGORITHM_COLORS,
    "algorithm_markers": ALGORITHM_MARKERS,
    "main_rect": MAIN_RECT,
    "summary_rect": SUMMARY_RECT,
    "objective_ylim": OBJECTIVE_YLIM,
    "main_x_lim": MAIN_X_LIM,
    "summary_x_lim": SUMMARY_X_LIM,
    "title_main": TITLE_MAIN,
    "title_summary": TITLE_SUMMARY,
    "data_status_note": DATA_STATUS_NOTE,
    "output_formats": OUTPUT_FORMATS,
    "data_file": DATA_FILE,
}
