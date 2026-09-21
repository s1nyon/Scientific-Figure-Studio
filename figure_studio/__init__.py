"""Reusable visual and validation primitives for Scientific Figure Studio."""

from .analysis import pareto_mask, running_best
from .export import export_figure
from .fonts import FontReport, resolve_fonts
from .layouts import canvas_size, make_figure
from .palettes import Palette, get_palette, palette_names
from .style import figure_style

__all__ = [
    "FontReport",
    "Palette",
    "canvas_size",
    "export_figure",
    "figure_style",
    "get_palette",
    "make_figure",
    "palette_names",
    "pareto_mask",
    "resolve_fonts",
    "running_best",
]
