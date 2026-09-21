"""User-editable configuration for the Pareto-front example."""

FIGURE_ID = "fig_04_pareto"
FIGURE_WIDTH = 6.20
FIGURE_HEIGHT = 4.30
DPI = 300
STYLE_NAME = "algorithm_research"
PALETTE_NAME = "algorithm_research"
FONT_SIZE = 8.5
MARKER_SIZE = 32.0
FRONT_LINE_WIDTH = 2.0
LEGEND_LOCATION = "upper right"
OBJECTIVE_DIRECTIONS = ("minimize", "minimize")
OUTPUT_FORMATS = ("png", "svg", "pdf")
DATA_FILE = "examples/data/pareto_practice.csv"

CONFIG = {
    "figure_id": FIGURE_ID,
    "figure_width": FIGURE_WIDTH,
    "figure_height": FIGURE_HEIGHT,
    "dpi": DPI,
    "style_name": STYLE_NAME,
    "palette_name": PALETTE_NAME,
    "font_size": FONT_SIZE,
    "marker_size": MARKER_SIZE,
    "front_line_width": FRONT_LINE_WIDTH,
    "legend_location": LEGEND_LOCATION,
    "objective_directions": OBJECTIVE_DIRECTIONS,
    "output_formats": OUTPUT_FORMATS,
    "data_file": DATA_FILE,
}
