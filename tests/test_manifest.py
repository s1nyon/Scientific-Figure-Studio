from pathlib import Path

import pytest


def test_manifest_resolves_external_data_without_rewriting_input(tmp_path: Path):
    from figure_studio.manifest import load_manifest

    data_path = tmp_path / "formal.csv"
    original = "x,y\n1,2\n"
    data_path.write_text(original, encoding="utf-8")
    manifest = {"data_status": "formal input data", "data_file": str(data_path)}

    loaded = load_manifest(manifest, base_dir=Path.cwd())

    assert loaded.data_path == data_path.resolve()
    assert loaded.data_status == "formal input data"
    assert data_path.read_text(encoding="utf-8") == original


@pytest.mark.parametrize(
    "status",
    ["formal input data", "illustrative practice data", "unknown source data"],
)
def test_manifest_accepts_declared_data_statuses(tmp_path: Path, status: str):
    from figure_studio.manifest import load_manifest

    data_path = tmp_path / "data.csv"
    data_path.write_text("x\n1\n", encoding="utf-8")
    loaded = load_manifest(
        {"data_status": status, "data_file": data_path.name},
        base_dir=tmp_path,
    )

    assert loaded.data_status == status


def test_manifest_rejects_unknown_data_status(tmp_path: Path):
    from figure_studio.manifest import load_manifest

    data_path = tmp_path / "data.csv"
    data_path.write_text("x\n1\n", encoding="utf-8")
    with pytest.raises(ValueError, match="data_status"):
        load_manifest(
            {"data_status": "invented result", "data_file": data_path.name},
            base_dir=tmp_path,
        )
