"""User-editable configuration for the convergence example."""

FIGURE_ID = "fig_01_convergence"
FIGURE_WIDTH = 6.20
FIGURE_HEIGHT = 4.10
DPI = 300
STYLE_NAME = "algorithm_research"
PALETTE_NAME = "algorithm_research"
PRIMARY_COLOR = "#166A8F"
LINE_WIDTH = 2.0
AUXILIARY_LINE_WIDTH = 0.9
MARKER_SIZE = 4.0
FONT_SIZE = 8.5
LEGEND_LOCATION = "upper right"
X_LIMITS = None
Y_LIMITS = (0.75, 2.55)
SHOW_CURRENT_OBJECTIVE = True
OUTPUT_FORMATS = ("png", "svg", "pdf")
DATA_FILE = "examples/data/convergence_practice.csv"

ALGORITHM_COLORS = {
    "Proposed": PRIMARY_COLOR,
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
    "primary_color": PRIMARY_COLOR,
    "line_width": LINE_WIDTH,
    "auxiliary_line_width": AUXILIARY_LINE_WIDTH,
    "marker_size": MARKER_SIZE,
    "font_size": FONT_SIZE,
    "legend_location": LEGEND_LOCATION,
    "x_limits": X_LIMITS,
    "y_limits": Y_LIMITS,
    "show_current_objective": SHOW_CURRENT_OBJECTIVE,
    "output_formats": OUTPUT_FORMATS,
    "data_file": DATA_FILE,
    "algorithm_colors": ALGORITHM_COLORS,
}
