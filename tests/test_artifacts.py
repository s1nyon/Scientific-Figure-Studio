import json

import pytest

from figure_studio.artifacts import (
    build_source_hashes,
    certify_reproduction,
    clone_accepted,
    create_run_dir,
    package_reproduction,
    promote_candidate,
    write_run_manifest,
)


def test_run_manifest_records_source_hashes_and_candidate_status(tmp_path):
    workspace = tmp_path / "workspace"
    run_dir = create_run_dir(workspace, run_id="run-001")
    source = run_dir / "plot.py"
    figure = run_dir / "figure.png"
    source.write_text("print('practice')\n", encoding="utf-8")
    figure.write_bytes(b"png bytes")

    source_hashes = build_source_hashes({"plot.py": source})
    manifest_path = write_run_manifest(
        run_dir,
        status="candidate",
        source_hashes=source_hashes,
        outputs={"png": figure},
        parent_run="workspace-000",
    )

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert manifest["status"] == "candidate"
    assert manifest["parent_run"] == "workspace-000"
    assert manifest["source_hashes"]["plot.py"]
    assert manifest["outputs"]["png"]["sha256"]


def test_promote_candidate_requires_user_note_and_protects_accepted_copy(tmp_path):
    candidate = tmp_path / "candidate"
    candidate.mkdir()
    (candidate / "plot.py").write_text("VERSION = 'candidate'\n", encoding="utf-8")
    (candidate / "figure.png").write_bytes(b"candidate image")
    write_run_manifest(
        candidate,
        status="candidate",
        source_hashes=build_source_hashes({"plot.py": candidate / "plot.py"}),
        outputs={"png": candidate / "figure.png"},
    )

    with pytest.raises(ValueError, match="user_note"):
        promote_candidate(candidate, tmp_path / "accepted", user_note="")

    accepted = promote_candidate(
        candidate,
        tmp_path / "accepted",
        user_note="User explicitly accepted this practice composition.",
        gallery_root=tmp_path / "gallery",
    )
    accepted_plot = accepted / "plot.py"
    original_hash = accepted_plot.read_bytes()
    assert json.loads((accepted / "version_manifest.json").read_text())[
        "status"
    ] == "accepted"
    work_link = json.loads(
        (tmp_path / "gallery" / "_generated" / "work_links" / "candidate.json").read_text()
    )
    assert "reproduction_manifest" not in work_link["code_reference"]

    candidate_plot = candidate / "plot.py"
    candidate_plot.write_text("VERSION = 'changed'\n", encoding="utf-8")
    assert accepted_plot.read_bytes() == original_hash
    with pytest.raises(FileExistsError):
        promote_candidate(candidate, accepted, user_note="second acceptance")


def test_clone_accepted_creates_editable_workspace_without_mutating_source(tmp_path):
    candidate = tmp_path / "candidate"
    candidate.mkdir()
    (candidate / "plot.py").write_text("VERSION = 'candidate'\n", encoding="utf-8")
    (candidate / "figure.png").write_bytes(b"candidate image")
    write_run_manifest(
        candidate,
        status="candidate",
        source_hashes=build_source_hashes({"plot.py": candidate / "plot.py"}),
        outputs={"png": candidate / "figure.png"},
    )
    accepted = promote_candidate(candidate, tmp_path / "accepted", user_note="keep")

    clone = clone_accepted(accepted, tmp_path / "workspace-copy")
    clone_manifest = json.loads((clone / "version_manifest.json").read_text())
    assert clone_manifest["status"] == "workspace"
    assert clone_manifest["parent_run"] == accepted.name
    assert (accepted / "plot.py").read_text(encoding="utf-8") == "VERSION = 'candidate'\n"


def test_package_reproduction_writes_hash_manifest(tmp_path):
    source = tmp_path / "source"
    source.mkdir()
    (source / "plot.py").write_text("print('standalone')\n", encoding="utf-8")
    package = package_reproduction(
        {"plot.py": source / "plot.py"},
        tmp_path / "package",
        entrypoint="plot.py",
        dependencies=["matplotlib>=3.8"],
    )

    manifest = json.loads((package / "reproduction_manifest.json").read_text())
    assert manifest["project_independent"] is False
    assert manifest["entrypoint"] == "plot.py"
    assert manifest["files"]["plot.py"]["sha256"]

    certify_reproduction(package)
    certified = json.loads((package / "reproduction_manifest.json").read_text())
    assert certified["project_independent"] is True
    assert certified["project_root_env_required"] is False
