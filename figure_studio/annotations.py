"""Reusable, restrained annotation helpers."""

from collections.abc import Mapping
from typing import Any


def add_panel_label(ax: Any, label: str, **kwargs: Any) -> Any:
    """Add an upright panel label in axes coordinates."""

    options = {
        "xy": (0.0, 1.02),
        "xycoords": "axes fraction",
        "ha": "left",
        "va": "bottom",
        "fontweight": "bold",
    }
    options.update(kwargs)
    return ax.annotate(label, **options)


def add_reference_line(ax: Any, value: float, axis: str = "y", **kwargs: Any) -> Any:
    """Add a labeled-independent horizontal or vertical reference line."""

    options = {"color": "#9AA6AD", "linewidth": 0.8, "linestyle": ":", "zorder": 1}
    options.update(kwargs)
    if axis == "y":
        return ax.axhline(value, **options)
    if axis == "x":
        return ax.axvline(value, **options)
    raise ValueError("axis must be 'x' or 'y'")


def label_line_end(ax: Any, x: float, y: float, text: str, **kwargs: Any) -> Any:
    """Place a direct label near a curve endpoint."""

    options: Mapping[str, Any] = {
        "xy": (x, y),
        "xytext": (5, 0),
        "textcoords": "offset points",
        "ha": "left",
        "va": "center",
        "arrowprops": None,
    }
    options = dict(options)
    options.update(kwargs)
    return ax.annotate(text, **options)
