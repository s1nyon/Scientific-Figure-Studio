"""Physical canvas presets and small Matplotlib layout helpers."""

from typing import Any

import matplotlib.pyplot as plt

CANVAS_PRESETS: dict[str, tuple[float, float]] = {
    "compact": (3.35, 2.45),
    "standard": (6.20, 4.10),
    "wide": (7.20, 3.40),
    "composite": (7.20, 5.10),
}


def canvas_size(name: str) -> tuple[float, float]:
    """Return a canvas width and height in inches."""

    try:
        return CANVAS_PRESETS[name]
    except KeyError as exc:
        valid = ", ".join(CANVAS_PRESETS)
        raise ValueError(f"Unknown canvas {name!r}; choose one of: {valid}") from exc


def make_figure(canvas: str = "standard", **kwargs: Any):
    """Create a constrained-layout figure using a named physical canvas."""

    kwargs.setdefault("layout", "constrained")
    kwargs.setdefault("figsize", canvas_size(canvas))
    return plt.subplots(**kwargs)
