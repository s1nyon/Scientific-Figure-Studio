import matplotlib.pyplot as plt
import numpy as np
import pytest


def test_flow_edges_reject_unknown_endpoints():
    from figure_studio.illustrations import validate_flow_edges

    with pytest.raises(ValueError, match="unknown"):
        validate_flow_edges(
            {"start": {"x": 0.1, "y": 0.5}},
            [{"source": "start", "target": "missing"}],
        )


def test_flow_nodes_reject_duplicate_ids():
    from figure_studio.illustrations import validate_flow_edges

    with pytest.raises(ValueError, match="duplicate"):
        validate_flow_edges(
            [{"id": "node"}, {"id": "node"}],
            [],
        )


def test_architecture_connections_reject_unknown_modules():
    from figure_studio.illustrations import draw_architecture

    figure, axis = plt.subplots()
    with pytest.raises(ValueError, match="unknown"):
        draw_architecture(
            axis,
            {"input": {"x": 0.2, "y": 0.5}},
            [{"source": "input", "target": "missing"}],
            {},
        )
    plt.close(figure)


def test_geometry_keeps_equal_aspect_ratio():
    from figure_studio.illustrations import draw_geometry

    figure, axis = plt.subplots()
    draw_geometry(
        axis,
        {"A": (0.0, 0.0), "B": (1.0, 0.0), "C": (0.0, 1.0)},
        [{"points": ["A", "B", "C", "A"]}],
        {"line_color": "#123456"},
    )
    assert {text.get_text() for text in axis.texts} >= {"A", "B", "C"}
    assert axis.get_aspect() in (1.0, "equal")
    plt.close(figure)


def test_surface_accepts_finite_arrays():
    from figure_studio.illustrations import draw_surface

    figure = plt.figure()
    axis = figure.add_subplot(111, projection="3d")
    grid = np.linspace(-1.0, 1.0, 4)
    x, y = np.meshgrid(grid, grid)
    draw_surface(axis, x, y, x**2 + y**2, {"cmap": "viridis"})
    assert axis.collections
    plt.close(figure)
