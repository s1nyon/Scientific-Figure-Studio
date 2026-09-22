import shutil
from pathlib import Path

from PIL import Image, ImageDraw

from figure_studio.gallery import GalleryIndex


def make_test_image(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    image = Image.new("RGB", (160, 100), "white")
    draw = ImageDraw.Draw(image)
    draw.line((20, 80, 130, 20), fill="#166A8F", width=4)
    draw.rectangle((30, 30, 80, 70), outline="#D9822B", width=3)
    image.save(path)


def copy_same_image_to_two_folders(tmp_path: Path) -> tuple[Path, Path]:
    first = tmp_path / "00_inbox" / "sample.png"
    second = tmp_path / "01_minimal" / "same.png"
    make_test_image(first)
    second.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(first, second)
    return first, second


def test_empty_gallery_returns_no_records(tmp_path):
    index = GalleryIndex(tmp_path)
    assert index.scan() == []


def test_gallery_records_hash_images_and_write_notes(tmp_path):
    image_path = tmp_path / "00_inbox" / "sample.png"
    make_test_image(image_path)
    records = GalleryIndex(tmp_path).scan()
    assert len(records) == 1
    assert records[0].sha256
    assert records[0].dominant_color.startswith("#")
    note_path = tmp_path / "_generated" / "gallery_notes" / f"{records[0].sha256}.md"
    assert note_path.exists()


def test_duplicate_images_are_flagged_without_deleting_either_file(tmp_path):
    first, second = copy_same_image_to_two_folders(tmp_path)
    records = GalleryIndex(tmp_path).scan()
    assert sum(record.is_duplicate for record in records) >= 1
    assert first.exists() and second.exists()


def test_gallery_search_can_filter_favorites_without_inventing_them(tmp_path):
    image_path = tmp_path / "04_my_favorites" / "favorite.png"
    make_test_image(image_path)
    index = GalleryIndex(tmp_path)
    records = index.scan()
    assert index.search(favorite=True) == []
    records[0].favorite = True
    index.write_index(records)
    result = index.search(favorite=True)
    assert [record.relative_path for record in result] == ["04_my_favorites/favorite.png"]


def test_gallery_keeps_manual_evaluation_and_requires_explicit_agent_analysis(tmp_path):
    image_path = tmp_path / "00_inbox" / "sample.png"
    make_test_image(image_path)
    index = GalleryIndex(tmp_path)
    records = index.scan()
    assert records[0].visual_analysis_status == "not_analyzed"

    records[0].favorite = True
    records[0].user_evaluation = "manual note that must survive"
    index.write_index(records)
    rescanned = index.scan()[0]

    assert rescanned.favorite is True
    assert rescanned.user_evaluation == "manual note that must survive"
    assert rescanned.visual_analysis_status == "not_analyzed"

    analyzed = index.record_agent_analysis(
        "00_inbox/sample.png",
        {"layout": "single panel", "uncertainties": ["font is unknown"]},
    )
    assert analyzed.visual_analysis_status == "agent_reviewed"
    assert analyzed.user_evaluation == "manual note that must survive"
