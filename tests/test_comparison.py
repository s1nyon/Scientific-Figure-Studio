import json
import subprocess
import sys
from pathlib import Path

import pytest
from PIL import Image

from figure_studio.comparison import (
    build_before_after_comparison,
    restore_snapshot,
    snapshot_artifacts,
)

ROOT = Path(__file__).resolve().parents[1]


def test_snapshot_and_restore_preserve_source_and_configuration(tmp_path):
    working = tmp_path / "working"
    working.mkdir()
    plot = working / "plot.py"
    config = working / "config.py"
    figure = working / "figure.png"
    plot.write_text("version = 'before'\n", encoding="utf-8")
    config.write_text("COLOR = 'blue'\n", encoding="utf-8")
    Image.new("RGB", (120, 80), "white").save(figure)
    snapshot = tmp_path / "snapshots" / "before"

    record = snapshot_artifacts([plot, config, figure], snapshot)
    plot.write_text("version = 'after'\n", encoding="utf-8")
    config.write_text("COLOR = 'orange'\n", encoding="utf-8")
    Image.new("RGB", (120, 80), "black").save(figure)

    restore_snapshot(snapshot, working, overwrite=True)

    assert record["files"]["plot.py"]["sha256"]
    assert plot.read_text(encoding="utf-8") == "version = 'before'\n"
    assert config.read_text(encoding="utf-8") == "COLOR = 'blue'\n"
    assert Image.open(figure).getpixel((0, 0)) == (255, 255, 255)


def test_before_after_comparison_preserves_native_dimensions_in_manifest(tmp_path):
    before = tmp_path / "before.png"
    after = tmp_path / "after.png"
    output = tmp_path / "comparison.png"
    Image.new("RGB", (160, 80), "#166A8F").save(before)
    Image.new("RGB", (100, 140), "#2A9D8F").save(after)

    result = build_before_after_comparison(before, after, output)

    assert result == output
    assert output.exists()
    manifest = json.loads(output.with_suffix(".manifest.json").read_text(encoding="utf-8"))
    assert manifest["before"]["size_px"] == [160, 80]
    assert manifest["after"]["size_px"] == [100, 140]
    assert manifest["preserves_native_aspect"] is True


def test_revision_cli_requires_explicit_comparison_overwrite(tmp_path):
    before = tmp_path / "before.png"
    after = tmp_path / "after.png"
    output = tmp_path / "comparison.png"
    Image.new("RGB", (80, 60), "white").save(before)
    Image.new("RGB", (80, 60), "black").save(after)
    command = [
        sys.executable,
        str(ROOT / "tools" / "figure_revision.py"),
        "compare",
        "--before",
        str(before),
        "--after",
        str(after),
        "--output",
        str(output),
    ]

    first = subprocess.run(command, cwd=ROOT, check=False, capture_output=True, text=True)
    second = subprocess.run(command, cwd=ROOT, check=False, capture_output=True, text=True)
    overwrite = subprocess.run(
        [*command, "--overwrite"],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )

    assert first.returncode == 0, first.stderr
    assert second.returncode != 0
    assert overwrite.returncode == 0, overwrite.stderr


def test_restore_default_writes_an_independent_recovery_directory(tmp_path):
    source = tmp_path / "source.txt"
    source.write_text("before\n", encoding="utf-8")
    snapshot = tmp_path / "snapshots" / "before"
    snapshot_artifacts([source], snapshot)

    restored = restore_snapshot(snapshot)

    recovery = restored["source.txt"]
    assert recovery != source
    assert recovery.read_text(encoding="utf-8") == "before\n"
    assert source.read_text(encoding="utf-8") == "before\n"


def test_restore_rejects_tampered_snapshot_before_writing_destination(tmp_path):
    source = tmp_path / "source.txt"
    source.write_text("before\n", encoding="utf-8")
    snapshot = tmp_path / "snapshots" / "before"
    snapshot_artifacts([source], snapshot)
    (snapshot / "source.txt").write_text("tampered\n", encoding="utf-8")
    destination = tmp_path / "destination"

    with pytest.raises(ValueError, match="hash mismatch"):
        restore_snapshot(snapshot, destination)

    assert not destination.exists()


def test_restore_rejects_path_traversal_in_snapshot_manifest(tmp_path):
    snapshot = tmp_path / "snapshots" / "unsafe"
    snapshot.mkdir(parents=True)
    (snapshot / "snapshot_manifest.json").write_text(
        json.dumps({"files": {"../outside.txt": {"sha256": "bad", "bytes": 1}}}),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="unsafe snapshot file name"):
        restore_snapshot(snapshot, tmp_path / "destination")


def test_restore_creates_missing_nested_destination_parent(tmp_path):
    source = tmp_path / "source.txt"
    source.write_text("before\n", encoding="utf-8")
    snapshot = tmp_path / "snapshots" / "before"
    snapshot_artifacts([source], snapshot)

    destination = tmp_path / "new" / "nested" / "workspace"
    restore_snapshot(snapshot, destination)

    assert (destination / "source.txt").read_text(encoding="utf-8") == "before\n"
