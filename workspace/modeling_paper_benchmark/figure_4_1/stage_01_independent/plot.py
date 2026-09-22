"""Render the text-only independent draft for paper Figure 4-1.

The source-of-truth structure is JSON. This renderer deliberately does not read
or rasterize the paper PDF; stage 1 is frozen before source-image comparison.
"""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.patches as patches
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch

from figure_studio.illustrations import validate_flow_edges

try:
    import config
except ModuleNotFoundError:  # pragma: no cover - direct path execution fallback
    config_spec = importlib.util.spec_from_file_location(
        "stage1_config", Path(__file__).with_name("config.py")
    )
    if config_spec is None or config_spec.loader is None:
        raise ImportError("unable to load sibling config.py")
    config = importlib.util.module_from_spec(config_spec)
    config_spec.loader.exec_module(config)


plt.rcParams["font.family"] = config.FONT_FAMILY
plt.rcParams["font.sans-serif"] = config.FONT_CANDIDATES
plt.rcParams["svg.fonttype"] = "none"
plt.rcParams["pdf.fonttype"] = 42
plt.rcParams["axes.unicode_minus"] = False


def _load_structure(data_path: Path | None) -> dict[str, Any]:
    path = data_path or config.ROOT / "structure_stage1.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise TypeError("structure JSON must contain an object")
    return payload


def _node_map(structure: dict[str, Any]) -> dict[str, dict[str, Any]]:
    nodes = structure.get("nodes", [])
    mapping = {str(node["id"]): node for node in nodes}
    if len(mapping) != len(nodes):
        raise ValueError("node IDs must be unique")
    return mapping


def _draw_module(ax: Any, node: dict[str, Any]) -> None:
    x = float(node["x"])
    y = float(node["y"])
    width = float(node["width"])
    height = float(node["height"])
    face, accent = config.ROLE_STYLE.get(
        str(node.get("role")), (config.COLORS["paper"], config.COLORS["line"])
    )
    patch = patches.FancyBboxPatch(
        (x - width / 2, y - height / 2),
        width,
        height,
        boxstyle="round,pad=0.008,rounding_size=0.018",
        facecolor=face,
        edgecolor=accent,
        linewidth=config.NODE_LINE_WIDTH,
        zorder=3,
    )
    ax.add_patch(patch)
    ax.add_patch(
        patches.FancyBboxPatch(
            (x - width / 2, y + height / 2 - 0.038),
            width,
            0.038,
            boxstyle="round,pad=0.008,rounding_size=0.018",
            facecolor=accent,
            edgecolor=accent,
            linewidth=0,
            zorder=4,
        )
    )
    ax.text(
        x,
        y + height / 2 - 0.019,
        str(node["title"]),
        ha="center",
        va="center",
        color="white",
        fontsize=config.MODULE_TITLE_SIZE,
        fontweight="bold",
        zorder=5,
    )
    body = node.get("body", [])
    body_lines = "\n".join(str(line) for line in body)
    ax.text(
        x,
        y - 0.005,
        body_lines,
        ha="center",
        va="center",
        color=config.COLORS["ink"],
        fontsize=config.MODULE_BODY_SIZE,
        linespacing=1.38,
        zorder=5,
    )
    if node.get("note"):
        ax.text(
            x,
            y - height / 2 + 0.026,
            str(node["note"]),
            ha="center",
            va="center",
            color=config.COLORS["muted"],
            fontsize=config.MODULE_NOTE_SIZE,
            zorder=5,
        )


def _edge_points(
    source: dict[str, Any], target: dict[str, Any]
) -> tuple[tuple[float, float], tuple[float, float]]:
    sx, sy = float(source["x"]), float(source["y"])
    tx, ty = float(target["x"]), float(target["y"])
    sw = float(source["width"])
    tw = float(target["width"])
    if tx >= sx:
        start = (sx + sw / 2, sy)
        end = (tx - tw / 2, ty)
    else:
        start = (sx - sw / 2, sy)
        end = (tx + tw / 2, ty)
    return start, end


def _draw_edges(ax: Any, structure: dict[str, Any], nodes: dict[str, dict[str, Any]]) -> None:
    for edge in structure.get("edges", []):
        source = nodes[str(edge["source"])]
        target = nodes[str(edge["target"])]
        start, end = _edge_points(source, target)
        diagonal = abs(float(target["y"]) - float(source["y"])) > 0.03
        arrow = FancyArrowPatch(
            start,
            end,
            arrowstyle="-|>",
            mutation_scale=config.ARROW_MUTATION,
            linewidth=config.ARROW_SIZE,
            color=config.COLORS["line"],
            connectionstyle=f"arc3,rad={0.08 if diagonal else 0.0}",
            shrinkA=0,
            shrinkB=2,
            zorder=2,
        )
        ax.add_patch(arrow)
        if edge.get("label"):
            mx = (start[0] + end[0]) / 2
            my = (start[1] + end[1]) / 2 + 0.026
            ax.text(
                mx,
                my,
                str(edge["label"]),
                ha="center",
                va="bottom",
                fontsize=config.MODULE_NOTE_SIZE,
                color=config.COLORS["line"],
                bbox={"facecolor": config.COLORS["paper"], "edgecolor": "none", "pad": 0.8},
                zorder=6,
            )


def _draw_title(ax: Any) -> None:
    ax.text(
        0.03,
        0.955,
        config.TITLE,
        ha="left",
        va="top",
        fontsize=config.TITLE_SIZE,
        fontweight="bold",
        color=config.COLORS["ink"],
    )
    ax.text(
        0.03,
        0.91,
        config.SUBTITLE,
        ha="left",
        va="top",
        fontsize=config.SUBTITLE_SIZE,
        color=config.COLORS["muted"],
    )
    ax.text(
        0.97,
        0.955,
        "FIG. 4-1",
        ha="right",
        va="top",
        fontsize=6.4,
        color=config.COLORS["muted"],
        fontweight="bold",
    )


def _draw_footer(ax: Any) -> None:
    ax.add_patch(
        patches.FancyBboxPatch(
            (0.04, 0.045),
            0.92,
            0.075,
            boxstyle="round,pad=0.006,rounding_size=0.012",
            facecolor=config.COLORS["footer_fill"],
            edgecolor=config.COLORS["footer_edge"],
            linewidth=0.6,
            linestyle=(0, (2, 2)),
            zorder=1,
        )
    )
    ax.text(
        0.5,
        0.082,
        config.FOOTER,
        ha="center",
        va="center",
        fontsize=config.FOOTER_SIZE,
        color=config.COLORS["muted"],
        zorder=2,
    )


def render(output_dir: Path, structure: dict[str, Any]) -> dict[str, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    nodes = _node_map(structure)
    edges = structure.get("edges", [])
    validate_flow_edges(nodes, edges)

    fig, ax = plt.subplots(figsize=config.FIGSIZE_IN, dpi=config.DPI)
    fig.patch.set_facecolor(config.COLORS["paper"])
    ax.set_facecolor(config.COLORS["paper"])
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    _draw_title(ax)
    _draw_edges(ax, structure, nodes)
    for node in nodes.values():
        _draw_module(ax, node)
    _draw_footer(ax)
    fig.subplots_adjust(left=0, right=1, bottom=0, top=1)

    base = output_dir / config.FIGURE_BASENAME
    fig.savefig(base.with_suffix(".png"), dpi=config.DPI, bbox_inches="tight", pad_inches=0.03)
    fig.savefig(base.with_suffix(".svg"), bbox_inches="tight", pad_inches=0.03)
    fig.savefig(base.with_suffix(".pdf"), bbox_inches="tight", pad_inches=0.03)
    plt.close(fig)
    return {
        "png": base.with_suffix(".png"),
        "svg": base.with_suffix(".svg"),
        "pdf": base.with_suffix(".pdf"),
    }


def main(
    output_dir: Path | None = None,
    data_path: Path | None = None,
    manifest_path: Path | None = None,
    skill_root: Path | None = None,
    overwrite: bool = False,
) -> dict[str, Path]:
    del manifest_path, skill_root, overwrite
    destination = Path(output_dir) if output_dir is not None else config.ROOT
    return render(destination, _load_structure(data_path))


if __name__ == "__main__":
    main()
