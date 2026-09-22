from pathlib import Path

import pytest
from PIL import Image, ImageDraw

from figure_studio.gallery import GalleryIndex


def _make_image(path: Path, color: str = "#166A8F") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    image = Image.new("RGB", (240, 160), "white")
    draw = ImageDraw.Draw(image)
    draw.line((20, 130, 210, 30), fill=color, width=6)
    draw.rectangle((55, 55, 150, 115), outline="#D9822B", width=4)
    image.save(path)


def test_changed_image_keeps_user_preference_and_records_stale_history(tmp_path):
    image = tmp_path / "00_inbox" / "reference.png"
    _make_image(image)
    gallery = GalleryIndex(tmp_path)
    gallery.scan()
    gallery.save_user_preference(
        "00_inbox/reference.png",
        evaluation="I like the compact layout; keep labels larger in new figures.",
        favorite=True,
        source="user-provided practice reference",
    )
    original_hash = gallery.scan()[0].sha256

    _make_image(image, color="#2A9D8F")
    changed = gallery.scan()[0]

    assert changed.sha256 != original_hash
    assert changed.favorite is True
    assert changed.user_evaluation.startswith("I like the compact layout")
    assert changed.source == "user-provided practice reference"
    assert changed.visual_analysis_status == "stale"
    stale = gallery.stale_records()
    assert any(record.relative_path == "00_inbox/reference.png" for record in stale)
    history_files = list((tmp_path / "_generated" / "gallery_history").glob("*.json"))
    assert history_files
    assert original_hash in history_files[0].read_text(encoding="utf-8")


def test_agent_analysis_requires_view_receipt_and_preserves_user_fields(tmp_path):
    image = tmp_path / "02_algorithm" / "algorithm.png"
    _make_image(image)
    gallery = GalleryIndex(tmp_path)
    gallery.scan()
    gallery.save_user_preference(
        "02_algorithm/algorithm.png",
        "Good color hierarchy.",
        favorite=True,
    )

    with pytest.raises(ValueError, match="viewed"):
        gallery.record_agent_analysis(
            "02_algorithm/algorithm.png",
            {"image_type": "algorithm convergence"},
            viewed=False,
        )

    reviewed = gallery.record_agent_analysis(
        "02_algorithm/algorithm.png",
        {
            "image_type": "algorithm convergence",
            "composition": "single hero panel with generous outer margins",
            "color_relationship": "teal line against a white field with orange secondary marks",
            "information_hierarchy": "primary curve first, annotations second",
            "reusable_methods": ["reserve whitespace around the plot", "use line style with color"],
            "applicable_scenarios": ["algorithm comparison"],
        },
        viewed=True,
        view_receipt={"method": "local_image_viewer", "path": "02_algorithm/algorithm.png"},
    )
    assert reviewed.visual_analysis_status == "agent_reviewed"
    assert reviewed.favorite is True
    note = (
        tmp_path
        / "_generated"
        / "gallery_visual_analysis"
        / f"{reviewed.sha256}.md"
    ).read_text(encoding="utf-8")
    assert "image_type" in note
    assert "local_image_viewer" in note


def test_gallery_search_filters_references_without_auto_favoriting(tmp_path):
    first = tmp_path / "01_minimal" / "minimal.png"
    second = tmp_path / "02_algorithm" / "algorithm.png"
    _make_image(first, "#166A8F")
    _make_image(second, "#2A9D8F")
    gallery = GalleryIndex(tmp_path)
    gallery.scan()
    gallery.save_user_preference("02_algorithm/algorithm.png", "Explicit favorite", favorite=True)
    records = gallery.scan()
    records[0].chart_type = "line chart"
    records[0].application = "algorithm comparison"
    gallery.write_index(records)

    matches = gallery.search(chart_type="line chart", application="algorithm comparison", limit=1)
    assert len(matches) == 1
    assert matches[0].relative_path == "01_minimal/minimal.png"
    assert gallery.search(favorite=True)[0].relative_path == "02_algorithm/algorithm.png"
    assert all(not record.favorite for record in gallery.search(style="minimal_editorial"))
