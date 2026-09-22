"""User-editable configuration for the chart-and-schematic composite Figure."""

FIGURE_ID = "fig_10_illustration_composite"
FIGURE_WIDTH = 7.20
FIGURE_HEIGHT = 5.10
DPI = 300
STYLE_NAME = "algorithm_research"
PALETTE_NAME = "algorithm_research"
FONT_SIZE = 8.2
LINE_WIDTH = 1.9
MARKER_SIZE = 4.0
LEGEND_LOCATION = "lower right"
OUTPUT_FORMATS = ("png", "svg", "pdf")
DATA_FILE = "examples/data/illustration_composite.csv"
STRUCTURE_FILE = "examples/data/illustration_composite.json"
HERO_COLORS = {"Method A": "#166A8F", "Method B": "#2A9D8F"}
SCHEMATIC_X_LIMITS = (0.02, 1.02)
SCHEMATIC_Y_LIMITS = (0.28, 0.72)

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
    "structure_file": STRUCTURE_FILE,
    "hero_colors": HERO_COLORS,
    "schematic_x_limits": SCHEMATIC_X_LIMITS,
    "schematic_y_limits": SCHEMATIC_Y_LIMITS,
    "node_width": 0.16,
    "node_height": 0.14,
    "node_color": "#EAF2F5",
    "node_edge_color": "#166A8F",
    "connection_color": "#56636B",
    "connection_width": 1.1,
    "arrow_scale": 11.0,
    "node_label_size": 7.2,
    "edge_label_size": 6.8,
}
