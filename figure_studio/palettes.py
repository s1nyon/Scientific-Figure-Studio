"""Semantic color palettes used across the project."""

from dataclasses import dataclass
from functools import cache, lru_cache
from pathlib import Path

import yaml


@dataclass(frozen=True)
class Palette:
    """A named palette with semantic roles and redundant encodings."""

    name: str
    ink: str
    muted: str
    primary: str
    secondary: str
    accent: str
    positive: str
    negative: str
    grid: str
    background: str
    category_cycle: tuple[str, ...]
    line_styles: tuple[str, ...]
    markers: tuple[str, ...]
    sequential_cmap: str
    diverging_cmap: str

    def as_dict(self) -> dict[str, object]:
        """Return a serializable representation for manifests."""

        return {
            "name": self.name,
            "ink": self.ink,
            "muted": self.muted,
            "primary": self.primary,
            "secondary": self.secondary,
            "accent": self.accent,
            "positive": self.positive,
            "negative": self.negative,
            "grid": self.grid,
            "background": self.background,
            "category_cycle": list(self.category_cycle),
            "line_styles": list(self.line_styles),
            "markers": list(self.markers),
            "sequential_cmap": self.sequential_cmap,
            "diverging_cmap": self.diverging_cmap,
        }


def _palette_path() -> Path:
    return Path(__file__).resolve().parents[1] / "design_system" / "palettes.yaml"


@lru_cache(maxsize=1)
def _load_palette_data() -> dict[str, dict[str, object]]:
    with _palette_path().open(encoding="utf-8") as stream:
        data = yaml.safe_load(stream)
    if not isinstance(data, dict) or not data:
        raise ValueError(f"Palette configuration is empty: {_palette_path()}")
    return data


def palette_names() -> tuple[str, ...]:
    """Return the available palette names in stable order."""

    return tuple(_load_palette_data())


@cache
def get_palette(name: str = "algorithm_research") -> Palette:
    """Load a named semantic palette from the project design system."""

    data = _load_palette_data()
    if name not in data:
        valid = ", ".join(palette_names())
        raise ValueError(f"Unknown palette {name!r}; choose one of: {valid}")
    values = data[name]
    required = {
        "ink",
        "muted",
        "primary",
        "secondary",
        "accent",
        "positive",
        "negative",
        "grid",
        "background",
        "category_cycle",
        "line_styles",
        "markers",
        "sequential_cmap",
        "diverging_cmap",
    }
    missing = required.difference(values)
    if missing:
        raise ValueError(f"Palette {name!r} is missing fields: {sorted(missing)}")
    return Palette(
        name=name,
        ink=str(values["ink"]),
        muted=str(values["muted"]),
        primary=str(values["primary"]),
        secondary=str(values["secondary"]),
        accent=str(values["accent"]),
        positive=str(values["positive"]),
        negative=str(values["negative"]),
        grid=str(values["grid"]),
        background=str(values["background"]),
        category_cycle=tuple(str(item) for item in values["category_cycle"]),
        line_styles=tuple(str(item) for item in values["line_styles"]),
        markers=tuple(str(item) for item in values["markers"]),
        sequential_cmap=str(values["sequential_cmap"]),
        diverging_cmap=str(values["diverging_cmap"]),
    )
