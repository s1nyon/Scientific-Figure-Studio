"""User-editable configuration for the illustrative flowchart."""

FIGURE_ID = "fig_08_illustration_flowchart"
FIGURE_WIDTH = 7.20
FIGURE_HEIGHT = 4.30
DPI = 300
STYLE_NAME = "visual_narrative"
PALETTE_NAME = "visual_narrative"
FONT_SIZE = 8.5
NODE_WIDTH = 0.18
NODE_HEIGHT = 0.10
NODE_COLOR = "#EAF2F5"
NODE_EDGE_COLOR = "#166A8F"
CONNECTION_COLOR = "#56636B"
CONNECTION_WIDTH = 1.2
ARROW_SCALE = 12.0
ARROW_SHRINK = 4.0
NODE_LABEL_SIZE = 8.0
EDGE_LABEL_SIZE = 7.5
X_LIMITS = (0.0, 1.0)
Y_LIMITS = (0.08, 0.96)
OUTPUT_FORMATS = ("png", "svg", "pdf")
DATA_FILE = "examples/data/illustration_flowchart.json"

CONFIG = {
    "figure_id": FIGURE_ID,
    "figure_width": FIGURE_WIDTH,
    "figure_height": FIGURE_HEIGHT,
    "dpi": DPI,
    "style_name": STYLE_NAME,
    "palette_name": PALETTE_NAME,
    "font_size": FONT_SIZE,
    "node_width": NODE_WIDTH,
    "node_height": NODE_HEIGHT,
    "node_color": NODE_COLOR,
    "node_edge_color": NODE_EDGE_COLOR,
    "connection_color": CONNECTION_COLOR,
    "connection_width": CONNECTION_WIDTH,
    "arrow_scale": ARROW_SCALE,
    "arrow_shrink": ARROW_SHRINK,
    "node_label_size": NODE_LABEL_SIZE,
    "edge_label_size": EDGE_LABEL_SIZE,
    "x_limits": X_LIMITS,
    "y_limits": Y_LIMITS,
    "output_formats": OUTPUT_FORMATS,
    "data_file": DATA_FILE,
}
