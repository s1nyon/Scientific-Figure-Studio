"""User-editable configuration for the illustrative model architecture."""

FIGURE_ID = "fig_09_illustration_architecture"
FIGURE_WIDTH = 7.20
FIGURE_HEIGHT = 3.60
DPI = 300
STYLE_NAME = "minimal_editorial"
PALETTE_NAME = "minimal_editorial"
FONT_SIZE = 8.5
NODE_WIDTH = 0.14
NODE_HEIGHT = 0.14
NODE_COLOR = "#EAF2F5"
NODE_EDGE_COLOR = "#166A8F"
CONNECTION_COLOR = "#56636B"
CONNECTION_WIDTH = 1.2
ARROW_SCALE = 12.0
ARROW_SHRINK = 4.0
NODE_LABEL_SIZE = 8.0
EDGE_LABEL_SIZE = 7.0
EDGE_LABEL_OFFSET = (0.0, 0.045)
X_LIMITS = (0.0, 1.0)
Y_LIMITS = (0.25, 0.75)
OUTPUT_FORMATS = ("png", "svg", "pdf")
DATA_FILE = "examples/data/illustration_architecture.json"

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
    "edge_label_offset": EDGE_LABEL_OFFSET,
    "x_limits": X_LIMITS,
    "y_limits": Y_LIMITS,
    "output_formats": OUTPUT_FORMATS,
    "data_file": DATA_FILE,
}
