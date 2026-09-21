"""User-editable configuration for the composite practice figure."""

FIGURE_ID = "fig_06_composite"
FIGURE_WIDTH = 7.20
FIGURE_HEIGHT = 5.10
DPI = 300
STYLE_NAME = "algorithm_research"
PALETTE_NAME = "algorithm_research"
FONT_SIZE = 8.2
LINE_WIDTH = 2.0
MARKER_SIZE = 4.2
LEGEND_LOCATION = "lower right"
OUTPUT_FORMATS = ("png", "svg", "pdf")
DATA_FILE = "examples/data/composite_practice.csv"

ALGORITHM_COLORS = {
    "Proposed": "#166A8F",
    "Adaptive": "#2A9D8F",
    "Baseline": "#7A8793",
}

CONFIG = {
    "figure_id": FIGURE_ID,
    "figure_width": FIGURE_WIDTH,
    "figure_height": FIGURE_HEIGHT,
    "dpi": DPI,
    "style_name": STYLE_NAME,
    "palette_name": PALETTE_NAME,
    "font_size": FONT_SIZE,
    "line_width": LINE_WIDTH,
    "marker_size": MARKER_SIZE,
    "legend_location": LEGEND_LOCATION,
    "output_formats": OUTPUT_FORMATS,
    "data_file": DATA_FILE,
    "algorithm_colors": ALGORITHM_COLORS,
}
