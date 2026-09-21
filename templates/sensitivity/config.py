"""User-editable configuration for sensitivity and parameter effects."""

FIGURE_ID = "fig_03_sensitivity"
FIGURE_WIDTH = 7.20
FIGURE_HEIGHT = 3.80
DPI = 300
STYLE_NAME = "visual_narrative"
PALETTE_NAME = "visual_narrative"
LINE_WIDTH = 2.0
MARKER_SIZE = 4.2
FONT_SIZE = 8.2
HEATMAP_CMAP = "RdBu_r"
COLOR_CENTER = 0.0
LEGEND_LOCATION = "upper right"
OUTPUT_FORMATS = ("png", "svg", "pdf")
DATA_FILE = "examples/data/sensitivity_practice.csv"

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
    "heatmap_cmap": HEATMAP_CMAP,
    "color_center": COLOR_CENTER,
    "legend_location": LEGEND_LOCATION,
    "output_formats": OUTPUT_FORMATS,
    "data_file": DATA_FILE,
}
