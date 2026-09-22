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


def test_manifest_rejects_missing_source_file(tmp_path: Path):
    from figure_studio.manifest import load_manifest

    with pytest.raises(FileNotFoundError, match="data file"):
        load_manifest(
            {"data_status": "formal input data", "data_file": "missing.csv"},
            base_dir=tmp_path,
        )


def test_manifest_reports_hash_and_practice_label(tmp_path: Path):
    from figure_studio.manifest import load_manifest, provenance_data_label

    data_path = tmp_path / "practice.csv"
    data_path.write_text("x\n1\n", encoding="utf-8")
    loaded = load_manifest(
        {
            "data_status": "illustrative practice data",
            "data_file": data_path.name,
            "objective_direction": "maximize",
            "fields": {"x": "practice input"},
        },
        base_dir=tmp_path,
    )

    assert len(loaded.data_sha256) == 64
    assert loaded.objective_direction == "maximize"
    assert provenance_data_label(loaded.data_status)
    assert provenance_data_label("formal input data") is None


def test_data_provenance_redacts_external_absolute_paths(tmp_path: Path):
    from figure_studio.manifest import build_data_provenance, load_manifest

    data_path = tmp_path / "formal.csv"
    data_path.write_text("x\n1\n", encoding="utf-8")
    loaded = load_manifest(
        {"data_status": "formal input data", "data_file": str(data_path)},
        base_dir=Path.cwd(),
    )

    provenance = build_data_provenance(loaded)

    assert provenance["data_file"] == "<external-input>/formal.csv"
    assert provenance["resolved_data_path"] == "<external-input>/formal.csv"
