"""User-editable configuration for the prediction and residual example."""

FIGURE_ID = "fig_02_prediction"
FIGURE_WIDTH = 6.20
FIGURE_HEIGHT = 5.10
DPI = 300
STYLE_NAME = "algorithm_research"
PALETTE_NAME = "algorithm_research"
LINE_WIDTH = 1.8
MARKER_SIZE = 4.2
FONT_SIZE = 8.5
LEGEND_LOCATION = "upper left"
X_LIMITS = None
Y_LIMITS = None
OUTPUT_FORMATS = ("png", "svg", "pdf")
DATA_FILE = "examples/data/prediction_practice.csv"

SPLIT_COLORS = {
    "train": "#166A8F",
    "validation": "#2A9D8F",
    "test": "#D9822B",
}
SPLIT_MARKERS = {"train": "o", "validation": "s", "test": "^"}

CONFIG = {
    "figure_id": FIGURE_ID,
    "figure_width": FIGURE_WIDTH,
    "figure_height": FIGURE_HEIGHT,
    "dpi": DPI,
    "style_name": STYLE_NAME,
    "palette_name": PALETTE_NAME,
    "line_width": LINE_WIDTH,
    "marker_size": MARKER_SIZE,
    "font_size": FONT_SIZE,
    "legend_location": LEGEND_LOCATION,
    "x_limits": X_LIMITS,
    "y_limits": Y_LIMITS,
    "output_formats": OUTPUT_FORMATS,
    "data_file": DATA_FILE,
    "split_colors": SPLIT_COLORS,
    "split_markers": SPLIT_MARKERS,
}
