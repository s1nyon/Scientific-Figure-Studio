"""Scoped Matplotlib styles for the three project visual languages."""

from collections.abc import Iterator
from contextlib import contextmanager

import matplotlib as mpl

from .fonts import configure_fonts, resolve_fonts
from .layouts import canvas_size
from .palettes import get_palette

_STYLE_SETTINGS: dict[str, dict[str, object]] = {
    "minimal_editorial": {
        "base_size": 8.5,
        "axes_linewidth": 0.75,
        "grid_alpha": 0.0,
        "legend_fontsize": 7.5,
    },
    "algorithm_research": {
        "base_size": 8.5,
        "axes_linewidth": 0.8,
        "grid_alpha": 0.0,
        "legend_fontsize": 7.5,
    },
    "visual_narrative": {
        "base_size": 9.0,
        "axes_linewidth": 0.8,
        "grid_alpha": 0.14,
        "legend_fontsize": 8.0,
    },
}


@contextmanager
def figure_style(
    name: str = "minimal_editorial", canvas: str = "standard"
) -> Iterator[dict[str, object]]:
    """Apply a project style only inside the context manager."""

    if name not in _STYLE_SETTINGS:
        valid = ", ".join(_STYLE_SETTINGS)
        raise ValueError(f"Unknown figure style {name!r}; choose one of: {valid}")
    palette = get_palette(name)
    size = canvas_size(canvas)
    report = resolve_fonts()
    setting = _STYLE_SETTINGS[name]
    params = {
        "figure.figsize": size,
        "figure.dpi": 120,
        "savefig.dpi": 300,
        "figure.facecolor": palette.background,
        "axes.facecolor": palette.background,
        "axes.edgecolor": palette.ink,
        "axes.labelcolor": palette.ink,
        "xtick.color": palette.ink,
        "ytick.color": palette.ink,
        "text.color": palette.ink,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.linewidth": setting["axes_linewidth"],
        "axes.grid": False,
        "axes.axisbelow": True,
        "grid.color": palette.grid,
        "grid.linewidth": 0.55,
        "grid.alpha": setting["grid_alpha"],
        "font.size": setting["base_size"],
        "axes.titlesize": setting["base_size"] + 0.5,
        "axes.labelsize": setting["base_size"],
        "xtick.labelsize": setting["base_size"] - 1.0,
        "ytick.labelsize": setting["base_size"] - 1.0,
        "legend.fontsize": setting["legend_fontsize"],
        "legend.frameon": False,
        "lines.solid_capstyle": "round",
        "lines.dash_capstyle": "round",
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
        "svg.fonttype": "none",
    }
    with mpl.rc_context(params):
        configure_fonts(report)
        yield {"palette": palette, "font_report": report, "canvas": size}
