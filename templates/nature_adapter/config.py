"""User-editable configuration for the fixed-Nature-context practice chart."""

FIGURE_ID = "fig_07_nature_adapter"
FIGURE_WIDTH = 6.80
FIGURE_HEIGHT = 4.30
DPI = 300
STYLE_NAME = "minimal_editorial"
PALETTE_NAME = "minimal_editorial"
FONT_SIZE = 8.5
LINE_WIDTH = 2.0
AUXILIARY_LINE_WIDTH = 0.9
MARKER_SIZE = 4.0
LEGEND_LOCATION = "upper right"
OUTPUT_FORMATS = ("png", "svg", "pdf")
DATA_FILE = "examples/data/convergence_practice.csv"

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
    "auxiliary_line_width": AUXILIARY_LINE_WIDTH,
    "marker_size": MARKER_SIZE,
    "legend_location": LEGEND_LOCATION,
    "output_formats": OUTPUT_FORMATS,
    "data_file": DATA_FILE,
    "algorithm_colors": ALGORITHM_COLORS,
}
