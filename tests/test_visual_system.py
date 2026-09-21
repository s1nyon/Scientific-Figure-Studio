import matplotlib as mpl
import pytest

from figure_studio.fonts import resolve_fonts
from figure_studio.layouts import canvas_size, make_figure
from figure_studio.palettes import get_palette, palette_names
from figure_studio.style import figure_style


def test_all_visual_presets_have_semantic_roles():
    assert set(palette_names()) == {
        "minimal_editorial",
        "algorithm_research",
        "visual_narrative",
    }
    for name in palette_names():
        palette = get_palette(name)
        assert palette.primary.startswith("#")
        assert palette.background == "#FFFFFF"
        assert len(palette.category_cycle) >= 4


def test_figure_style_restores_rcparams():
    before = mpl.rcParams["axes.spines.top"]
    with figure_style("minimal_editorial"):
        assert mpl.rcParams["axes.spines.top"] is False
    assert mpl.rcParams["axes.spines.top"] == before


def test_canvas_presets_are_physical_sizes():
    width, height = canvas_size("standard")
    assert 3.0 < width < 8.0
    assert 2.0 < height < 6.0
    fig, axes = make_figure("compact")
    assert fig.get_figwidth() == pytest.approx(canvas_size("compact")[0])
    assert axes is not None
    fig.clear()


def test_font_report_contains_actual_resolution_fields():
    report = resolve_fonts()
    assert report.english_family
    assert isinstance(report.available, tuple)
    assert isinstance(report.missing, tuple)
    assert isinstance(report.warnings, tuple)


def test_unknown_visual_preset_is_rejected():
    with pytest.raises(ValueError, match="minimal_editorial"):
        get_palette("missing")
    with pytest.raises(ValueError, match="standard"):
        canvas_size("missing")
