"""Structured Matplotlib primitives for scientific illustration templates.

The helpers in this module deliberately draw only the nodes, connections,
coordinates, and values supplied by the caller.  They provide shape and
validation conventions, not scientific model content.
"""

from collections.abc import Iterable, Mapping, Sequence
from math import isfinite
from typing import Any

import numpy as np
from matplotlib.patches import Ellipse, FancyArrowPatch, FancyBboxPatch, Polygon


def _node_mapping(
    nodes: Mapping[str, object] | Iterable[Mapping[str, object]],
) -> dict[str, dict[str, Any]]:
    """Normalize mapping or records with explicit IDs and reject duplicates."""

    if isinstance(nodes, Mapping):
        items = nodes.items()
    else:
        records: list[tuple[str, Mapping[str, object]]] = []
        for record in nodes:
            if "id" not in record:
                raise ValueError("node record must contain an id")
            records.append((str(record["id"]), record))
        items = records

    normalized: dict[str, dict[str, Any]] = {}
    for node_id, value in items:
        key = str(node_id)
        if key in normalized:
            raise ValueError(f"duplicate node id: {key}")
        if isinstance(value, Mapping):
            normalized[key] = dict(value)
        else:
            normalized[key] = {"label": str(value)}
    return normalized


def _edge_endpoints(edges: Iterable[Mapping[str, object]]) -> list[Mapping[str, object]]:
    """Materialize edges and require explicit directed endpoints."""

    materialized = list(edges)
    for edge in materialized:
        if "source" not in edge or "target" not in edge:
            raise ValueError("edge must contain source and target")
    return materialized


def validate_flow_edges(
    nodes: Mapping[str, object] | Iterable[Mapping[str, object]],
    edges: Iterable[Mapping[str, object]],
) -> None:
    """Validate that every directed edge refers to one declared node."""

    node_map = _node_mapping(nodes)
    for edge in _edge_endpoints(edges):
        source = str(edge["source"])
        target = str(edge["target"])
        if source not in node_map or target not in node_map:
            missing = source if source not in node_map else target
            raise ValueError(f"unknown flow node endpoint: {missing}")


def _coordinate(node: Mapping[str, object], key: str) -> float:
    try:
        value = float(node[key])
    except (KeyError, TypeError, ValueError) as exc:
        raise ValueError(f"node requires finite {key} coordinate") from exc
    if not isfinite(value):
        raise ValueError(f"node requires finite {key} coordinate")
    return value


def _node_xy(node: Mapping[str, object]) -> tuple[float, float]:
    return _coordinate(node, "x"), _coordinate(node, "y")


def _limits_from_config(config: Mapping[str, object], default: tuple[float, float, float, float]):
    x_limits = config.get("x_limits")
    y_limits = config.get("y_limits")
    if x_limits is None or y_limits is None:
        return default
    return (*tuple(float(value) for value in x_limits), *tuple(float(value) for value in y_limits))


def _add_arrow(
    ax: Any,
    source: tuple[float, float],
    target: tuple[float, float],
    config: Mapping[str, object],
    label: str | None = None,
) -> None:
    arrow = FancyArrowPatch(
        source,
        target,
        arrowstyle=str(config.get("arrow_style", "-|>")),
        mutation_scale=float(config.get("arrow_scale", 12.0)),
        linewidth=float(config.get("connection_width", 1.2)),
        color=str(config.get("connection_color", "#56636B")),
        connectionstyle=str(config.get("connection_style", "arc3,rad=0.0")),
        shrinkA=float(config.get("arrow_shrink", 12.0)),
        shrinkB=float(config.get("arrow_shrink", 12.0)),
        zorder=2,
    )
    ax.add_patch(arrow)
    if label:
        midpoint = ((source[0] + target[0]) / 2.0, (source[1] + target[1]) / 2.0)
        ax.text(
            midpoint[0],
            midpoint[1],
            label,
            ha="center",
            va="center",
            fontsize=float(config.get("edge_label_size", 7.5)),
            color=str(config.get("label_color", "#263238")),
            bbox={
                "facecolor": str(config.get("label_background", "#FFFFFF")),
                "alpha": 0.86,
                "pad": 1.2,
                "edgecolor": "none",
            },
            zorder=4,
        )


def _draw_box(
    ax: Any,
    node_id: str,
    node: Mapping[str, object],
    config: Mapping[str, object],
) -> None:
    x, y = _node_xy(node)
    width = float(node.get("width", config.get("node_width", 0.18)))
    height = float(node.get("height", config.get("node_height", 0.10)))
    kind = str(node.get("kind", "process")).lower()
    face = str(node.get("color", config.get("node_color", "#EAF2F5")))
    edge = str(config.get("node_edge_color", "#166A8F"))
    linewidth = float(config.get("node_line_width", 1.0))
    if kind in {"terminal", "start", "end"}:
        artist = FancyBboxPatch(
            (x - width / 2.0, y - height / 2.0),
            width,
            height,
            boxstyle=f"round,pad=0.02,rounding_size={height / 2.0}",
            facecolor=face,
            edgecolor=edge,
            linewidth=linewidth,
            zorder=3,
        )
    elif kind == "decision":
        artist = Polygon(
            [
                (x, y + height / 2.0),
                (x + width / 2.0, y),
                (x, y - height / 2.0),
                (x - width / 2.0, y),
            ],
            closed=True,
            facecolor=face,
            edgecolor=edge,
            linewidth=linewidth,
            zorder=3,
        )
    else:
        artist = FancyBboxPatch(
            (x - width / 2.0, y - height / 2.0),
            width,
            height,
            boxstyle="round,pad=0.018,rounding_size=0.025",
            facecolor=face,
            edgecolor=edge,
            linewidth=linewidth,
            zorder=3,
        )
    ax.add_patch(artist)
    ax.text(
        x,
        y,
        str(node.get("label", node_id)),
        ha="center",
        va="center",
        fontsize=float(config.get("node_label_size", 8.0)),
        color=str(config.get("label_color", "#263238")),
        wrap=True,
        zorder=4,
    )


def draw_flowchart(
    ax: Any,
    nodes: Mapping[str, object] | Iterable[Mapping[str, object]],
    edges: Iterable[Mapping[str, object]],
    config: Mapping[str, object],
) -> None:
    """Draw an explicit directed flowchart with role-specific node shapes."""

    node_map = _node_mapping(nodes)
    edge_list = _edge_endpoints(edges)
    validate_flow_edges(node_map, edge_list)
    for edge in edge_list:
        _add_arrow(
            ax,
            _node_xy(node_map[str(edge["source"])]),
            _node_xy(node_map[str(edge["target"])]),
            config,
            str(edge["label"]) if edge.get("label") is not None else None,
        )
    for node_id, node in node_map.items():
        _draw_box(ax, node_id, node, config)
    ax.set_xlim(*tuple(float(value) for value in config.get("x_limits", (0.0, 1.0))))
    ax.set_ylim(*tuple(float(value) for value in config.get("y_limits", (0.0, 1.0))))
    ax.axis("off")


def draw_architecture(
    ax: Any,
    modules: Mapping[str, object] | Iterable[Mapping[str, object]],
    connections: Iterable[Mapping[str, object]],
    config: Mapping[str, object],
) -> None:
    """Draw a model architecture exactly from declared modules and connections."""

    module_map = _node_mapping(modules)
    connection_list = _edge_endpoints(connections)
    validate_flow_edges(module_map, connection_list)
    for connection in connection_list:
        _add_arrow(
            ax,
            _node_xy(module_map[str(connection["source"])]),
            _node_xy(module_map[str(connection["target"])]),
            config,
            str(connection["label"]) if connection.get("label") is not None else None,
        )
    for module_id, module in module_map.items():
        _draw_box(ax, module_id, module, config)
    ax.set_xlim(*tuple(float(value) for value in config.get("x_limits", (0.0, 1.0))))
    ax.set_ylim(*tuple(float(value) for value in config.get("y_limits", (0.0, 1.0))))
    ax.axis("off")


def draw_geometry(
    ax: Any,
    points: Mapping[str, Sequence[float]],
    constraints: Iterable[Mapping[str, object]],
    config: Mapping[str, object],
) -> None:
    """Draw planar points and explicit line/polygon constraints at equal scale."""

    point_map: dict[str, tuple[float, float]] = {}
    for point_id, coordinate in points.items():
        if len(coordinate) != 2:
            raise ValueError(f"point {point_id} must have two coordinates")
        values = tuple(float(value) for value in coordinate)
        if not all(isfinite(value) for value in values):
            raise ValueError(f"point {point_id} must have finite coordinates")
        point_map[str(point_id)] = values

    for constraint in constraints:
        point_ids = [str(point_id) for point_id in constraint.get("points", [])]
        if len(point_ids) < 2:
            raise ValueError("geometry constraint requires at least two points")
        missing = [point_id for point_id in point_ids if point_id not in point_map]
        if missing:
            raise ValueError(f"unknown geometry point: {missing[0]}")
        coordinates = np.asarray([point_map[point_id] for point_id in point_ids], dtype=float)
        closed = bool(constraint.get("closed", False))
        if closed:
            coordinates = np.vstack([coordinates, coordinates[0]])
        ax.plot(
            coordinates[:, 0],
            coordinates[:, 1],
            color=str(constraint.get("color", config.get("line_color", "#166A8F"))),
            linewidth=float(constraint.get("linewidth", config.get("line_width", 1.4))),
            linestyle=str(constraint.get("linestyle", "-")),
            zorder=2,
        )
        if constraint.get("label"):
            midpoint = coordinates[len(coordinates) // 2]
            ax.text(
                midpoint[0],
                midpoint[1],
                str(constraint["label"]),
                fontsize=float(config.get("label_size", 8.0)),
                color=str(config.get("label_color", "#263238")),
            )

    x_values = [coordinate[0] for coordinate in point_map.values()]
    y_values = [coordinate[1] for coordinate in point_map.values()]
    ax.scatter(
        x_values,
        y_values,
        color=str(config.get("point_color", "#D9822B")),
        s=float(config.get("point_size", 28.0)),
        zorder=3,
    )
    if bool(config.get("show_point_labels", True)):
        for point_id, (x_value, y_value) in point_map.items():
            ax.annotate(
                point_id,
                (x_value, y_value),
                xytext=(4, 4),
                textcoords="offset points",
                fontsize=float(config.get("label_size", 8.0)),
            )
    default = (
        min(x_values) - 0.1,
        max(x_values) + 0.1,
        min(y_values) - 0.1,
        max(y_values) + 0.1,
    )
    x_min, x_max, y_min, y_max = _limits_from_config(config, default)
    ax.set_xlim(x_min, x_max)
    ax.set_ylim(y_min, y_max)
    ax.set_aspect("equal", adjustable="box")


def draw_network(
    ax: Any,
    nodes: Mapping[str, object] | Iterable[Mapping[str, object]],
    edges: Iterable[Mapping[str, object]],
    config: Mapping[str, object],
) -> None:
    """Draw a directed or undirected network from explicit node coordinates."""

    node_map = _node_mapping(nodes)
    edge_list = _edge_endpoints(edges)
    validate_flow_edges(node_map, edge_list)
    for edge in edge_list:
        _add_arrow(
            ax,
            _node_xy(node_map[str(edge["source"])]),
            _node_xy(node_map[str(edge["target"])]),
            config,
            str(edge["label"]) if edge.get("label") is not None else None,
        )
    for node_id, node in node_map.items():
        x, y = _node_xy(node)
        ax.add_patch(
            Ellipse(
                (x, y),
                width=float(node.get("width", config.get("node_width", 0.08))),
                height=float(node.get("height", config.get("node_height", 0.08))),
                facecolor=str(node.get("color", config.get("node_color", "#EAF2F5"))),
                edgecolor=str(config.get("node_edge_color", "#166A8F")),
                linewidth=float(config.get("node_line_width", 1.0)),
                zorder=3,
            )
        )
        ax.text(x, y, str(node.get("label", node_id)), ha="center", va="center", zorder=4)
    ax.set_xlim(*tuple(float(value) for value in config.get("x_limits", (0.0, 1.0))))
    ax.set_ylim(*tuple(float(value) for value in config.get("y_limits", (0.0, 1.0))))
    ax.axis("off")


def draw_surface(ax: Any, x: Any, y: Any, z: Any, config: Mapping[str, object]) -> None:
    """Draw a finite 3-D surface while preserving the supplied spatial grid."""

    x_array = np.asarray(x, dtype=float)
    y_array = np.asarray(y, dtype=float)
    z_array = np.asarray(z, dtype=float)
    if x_array.shape != y_array.shape or x_array.shape != z_array.shape:
        raise ValueError("x, y, and z must have matching shapes")
    if (
        x_array.ndim != 2
        or not np.isfinite(x_array).all()
        or not np.isfinite(y_array).all()
        or not np.isfinite(z_array).all()
    ):
        raise ValueError("x, y, and z must be finite two-dimensional arrays")
    ax.plot_surface(
        x_array,
        y_array,
        z_array,
        cmap=str(config.get("cmap", "viridis")),
        linewidth=float(config.get("surface_line_width", 0.0)),
        antialiased=bool(config.get("antialiased", True)),
        alpha=float(config.get("alpha", 0.9)),
        rcount=int(config.get("row_count", x_array.shape[0])),
        ccount=int(config.get("column_count", x_array.shape[1])),
    )
    ax.set_xlabel(str(config.get("x_label", "x")))
    ax.set_ylabel(str(config.get("y_label", "y")))
    ax.set_zlabel(str(config.get("z_label", "z")))


def add_panel_label(ax: Any, label: str, config: Mapping[str, object]) -> Any:
    """Add a panel label using caller-controlled placement and typography."""

    return ax.annotate(
        label,
        xy=tuple(config.get("panel_label_xy", (0.0, 1.02))),
        xycoords="axes fraction",
        ha=str(config.get("panel_label_ha", "left")),
        va=str(config.get("panel_label_va", "bottom")),
        fontweight=str(config.get("panel_label_weight", "bold")),
        fontsize=float(config.get("panel_label_size", 9.0)),
    )
