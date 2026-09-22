"""Safe figure runs, lightweight version records, and independent packages."""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import uuid
from collections.abc import Iterable, Mapping
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

VERSION_STATUSES = {"workspace", "candidate", "accepted"}
VERSION_MANIFEST = "version_manifest.json"
REPRODUCTION_MANIFEST = "reproduction_manifest.json"


def sha256(path: str | Path) -> str:
    """Return a content hash for one regular file."""

    raw_candidate = Path(path).expanduser()
    if raw_candidate.is_symlink():
        raise FileNotFoundError(f"regular file does not exist: {raw_candidate}")
    candidate = raw_candidate.resolve()
    if not candidate.is_file():
        raise FileNotFoundError(f"regular file does not exist: {candidate}")
    digest = hashlib.sha256()
    with candidate.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _atomic_json(path: Path, value: Mapping[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{uuid.uuid4().hex}.tmp")
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def _safe_relative_name(value: str | Path) -> str:
    path = Path(value)
    if path.is_absolute() or ".." in path.parts or path.name in {"", "."}:
        raise ValueError(f"unsafe relative artifact path: {value}")
    return path.as_posix()


def _inside(path: Path, root: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
    except ValueError:
        return False
    return True


def build_source_hashes(
    paths: Mapping[str, str | Path] | Iterable[str | Path],
) -> dict[str, str]:
    """Hash source files using stable labels without modifying any input."""

    items = (
        paths.items()
        if isinstance(paths, Mapping)
        else ((Path(path).name, path) for path in paths)
    )
    result: dict[str, str] = {}
    for raw_label, raw_path in items:
        label = str(raw_label)
        if label in result:
            raise ValueError(f"duplicate source hash label: {label}")
        result[label] = sha256(raw_path)
    return result


def _record_file(path: Path, root: Path) -> dict[str, object]:
    raw_path = path.expanduser()
    if raw_path.is_symlink():
        raise FileNotFoundError(f"artifact file does not exist: {raw_path}")
    resolved = raw_path.resolve()
    if not resolved.is_file():
        raise FileNotFoundError(f"artifact file does not exist: {resolved}")
    if not _inside(resolved, root):
        raise ValueError(f"artifact file is outside its run directory: {resolved}")
    relative = resolved.relative_to(root).as_posix()
    return {"path": relative, "sha256": sha256(resolved), "bytes": resolved.stat().st_size}


def create_run_dir(workspace: str | Path, run_id: str | None = None) -> Path:
    """Create a fresh run directory below ``workspace/runs``."""

    root = Path(workspace).expanduser().resolve() / "runs"
    root.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    identifier = run_id or f"run-{timestamp}-{uuid.uuid4().hex[:8]}"
    if Path(identifier).name != identifier or identifier in {"", ".", ".."}:
        raise ValueError("run_id must be a single safe directory name")
    target = root / identifier
    if target.exists():
        raise FileExistsError(f"run directory already exists: {target}")
    target.mkdir()
    return target


def write_run_manifest(
    run_dir: str | Path,
    *,
    status: str,
    source_hashes: Mapping[str, str],
    outputs: Mapping[str, str | Path],
    run_id: str | None = None,
    parent_run: str | None = None,
    source_files: Mapping[str, str | Path] | None = None,
    metadata: Mapping[str, object] | None = None,
) -> Path:
    """Write a version manifest containing hashes for sources and outputs."""

    if status not in VERSION_STATUSES:
        raise ValueError(f"status must be one of {sorted(VERSION_STATUSES)}")
    root = Path(run_dir).expanduser().resolve()
    if not root.is_dir():
        raise FileNotFoundError(f"run directory does not exist: {root}")
    output_records = {label: _record_file(Path(path), root) for label, path in outputs.items()}
    source_records = (
        {label: _record_file(Path(path), root) for label, path in source_files.items()}
        if source_files
        else {}
    )
    manifest: dict[str, Any] = {
        "schema_version": "0.2",
        "run_id": run_id or root.name,
        "created_utc": datetime.now(UTC).isoformat(),
        "status": status,
        "parent_run": parent_run,
        "source_hashes": dict(source_hashes),
        "source_files": source_records,
        "outputs": output_records,
        "files": {
            **{f"source:{label}": record for label, record in source_records.items()},
            **{f"output:{label}": record for label, record in output_records.items()},
        },
    }
    if metadata:
        manifest["metadata"] = dict(metadata)
    target = root / VERSION_MANIFEST
    _atomic_json(target, manifest)
    return target


def read_version_manifest(directory: str | Path) -> dict[str, Any] | None:
    """Read a version manifest when present; malformed records fail closed."""

    root = Path(directory).expanduser().resolve()
    path = root / VERSION_MANIFEST
    if not path.is_file() or path.is_symlink():
        return None
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"version manifest must contain an object: {path}")
    return value


def directory_status(directory: str | Path) -> str | None:
    """Return a recorded status, including legacy task-manifest status."""

    root = Path(directory).expanduser().resolve()
    version = read_version_manifest(root)
    if version and version.get("status") in VERSION_STATUSES:
        return str(version["status"])
    task_path = root / "task_manifest.json"
    if task_path.is_file() and not task_path.is_symlink():
        value = json.loads(task_path.read_text(encoding="utf-8"))
        if isinstance(value, dict):
            nested = value.get("version")
            status = (
                nested.get("status")
                if isinstance(nested, dict)
                else value.get("version_status")
            )
            if status in VERSION_STATUSES:
                return str(status)
    return None


def _accepted_ancestor(path: Path) -> Path | None:
    resolved = path.expanduser().resolve()
    for parent in (resolved, *resolved.parents):
        if parent.is_dir() and directory_status(parent) == "accepted":
            return parent
    return None


def _validate_recorded_files(root: Path, manifest: Mapping[str, object]) -> None:
    records = manifest.get("files", {})
    if not isinstance(records, Mapping):
        raise ValueError("version manifest files must be an object")
    for record in records.values():
        if not isinstance(record, Mapping):
            raise ValueError("version manifest file record must be an object")
        raw_path = record.get("path")
        expected_hash = record.get("sha256")
        if not isinstance(raw_path, str) or not isinstance(expected_hash, str):
            raise ValueError("version manifest file records require path and sha256")
        relative = _safe_relative_name(raw_path)
        raw_source = root / relative
        if raw_source.is_symlink():
            raise ValueError(f"version manifest file is a symlink: {raw_path}")
        source = raw_source.resolve()
        if not _inside(source, root) or not source.is_file():
            raise FileNotFoundError(f"version manifest file is missing or unsafe: {raw_path}")
        if sha256(source) != expected_hash:
            raise ValueError(f"version manifest hash mismatch: {raw_path}")


def commit_staged_directory(
    staged_dir: str | Path,
    destination_dir: str | Path,
    *,
    overwrite: bool,
) -> Path:
    """Commit a complete staged directory with rollback for file-level writes."""

    staged = Path(staged_dir).expanduser().resolve()
    raw_destination = Path(destination_dir).expanduser()
    if raw_destination.is_symlink():
        raise ValueError(f"destination must not be a symlink: {raw_destination}")
    destination = raw_destination.resolve()
    if not staged.is_dir():
        raise FileNotFoundError(f"staging directory does not exist: {staged}")
    if staged.is_symlink():
        raise ValueError("staging directory must not be a symlink")
    ancestor = _accepted_ancestor(destination.parent)
    if ancestor is not None and ancestor != destination:
        raise PermissionError(f"destination is inside accepted work: {ancestor}")
    if directory_status(destination) == "accepted":
        raise PermissionError(f"refusing to modify accepted work: {destination}")
    if destination.exists() and not destination.is_dir():
        raise FileExistsError(f"destination is not a directory: {destination}")
    destination.parent.mkdir(parents=True, exist_ok=True)

    staged_files = [path for path in staged.rglob("*") if path.is_file()]
    staged_links = [path for path in staged.rglob("*") if path.is_symlink()]
    if staged_links:
        raise ValueError(f"staging directory contains unsupported symlinks: {staged_links}")
    targets = [destination / path.relative_to(staged) for path in staged_files]
    if not overwrite:
        conflicts = [path for path in targets if path.exists()]
        if conflicts:
            raise FileExistsError(f"refusing to replace existing files: {conflicts}")

    backup_root = Path(
        tempfile.mkdtemp(prefix=f".{destination.name}.rollback-", dir=destination.parent)
    )
    backups: dict[Path, Path] = {}
    created: list[Path] = []
    try:
        for source, target in zip(staged_files, targets, strict=True):
            if target.is_symlink() or (target.exists() and target.is_dir()):
                raise FileExistsError(f"destination target is unsafe: {target}")
            for parent in target.parents:
                if parent == destination:
                    break
                if parent.is_symlink():
                    raise ValueError(f"destination parent is a symlink: {parent}")
            target.parent.mkdir(parents=True, exist_ok=True)
            if target.exists():
                backup = backup_root / target.relative_to(destination)
                backup.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(target, backup)
                backups[target] = backup
            else:
                created.append(target)
            shutil.copy2(source, target)
    except Exception:
        for target in created:
            target.unlink(missing_ok=True)
        for target, backup in backups.items():
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(backup, target)
        raise
    finally:
        shutil.rmtree(backup_root, ignore_errors=True)
    return destination


def _copy_tree_to_staging(source: Path, parent: Path, name: str) -> Path:
    stage_root = Path(tempfile.mkdtemp(prefix=f".{name}.stage-", dir=parent))
    stage = stage_root / name
    shutil.copytree(source, stage)
    return stage


def _reject_symlinks(root: Path) -> None:
    links = [path for path in root.rglob("*") if path.is_symlink()]
    if links:
        raise ValueError(f"work directory contains unsupported symlinks: {links}")


def promote_candidate(
    candidate_dir: str | Path,
    accepted_dir: str | Path,
    *,
    user_note: str,
    gallery_root: str | Path | None = None,
) -> Path:
    """Promote one immutable candidate after an explicit user acknowledgement."""

    raw_candidate = Path(candidate_dir).expanduser()
    raw_accepted = Path(accepted_dir).expanduser()
    if raw_candidate.is_symlink() or raw_accepted.is_symlink():
        raise ValueError("candidate and accepted directories must not be symlinks")
    candidate = raw_candidate.resolve()
    accepted = raw_accepted.resolve()
    note = user_note.strip()
    if not note:
        raise ValueError("user_note is required for accepted work")
    if directory_status(candidate) != "candidate":
        raise ValueError("only a candidate run can be promoted")
    if accepted.exists():
        raise FileExistsError(f"accepted destination already exists: {accepted}")
    if _accepted_ancestor(accepted.parent) is not None:
        raise PermissionError("accepted destination is inside another accepted work")
    manifest = read_version_manifest(candidate)
    if manifest is None:
        raise ValueError("candidate is missing version_manifest.json")
    _validate_recorded_files(candidate, manifest)
    _reject_symlinks(candidate)

    gallery_link: tuple[Path, dict[str, object]] | None = None
    if gallery_root is not None:
        gallery = Path(gallery_root).expanduser().resolve()
        link_path = gallery / "_generated" / "work_links" / f"{candidate.name}.json"
        if link_path.exists():
            raise FileExistsError(f"work link already exists: {link_path}")
        code_reference: dict[str, object] = {
            "entrypoint": "plot.py",
            "configuration": "config.py",
            "version_manifest": VERSION_MANIFEST,
            "task_manifest": "task_manifest.json",
        }
        if (candidate / REPRODUCTION_MANIFEST).is_file():
            code_reference["reproduction_manifest"] = REPRODUCTION_MANIFEST
        gallery_link = (
            link_path,
            {
                "schema_version": "0.1",
                "work_id": candidate.name,
                "status": "accepted",
                "path_base": "gallery_root",
                "accepted_directory": Path(os.path.relpath(accepted, gallery)).as_posix(),
                "candidate_directory": Path(os.path.relpath(candidate, gallery)).as_posix(),
                "user_evaluation": note,
                "visual_design_reference": "design_receipt.json",
                "code_reference": code_reference,
                "source_hashes": manifest.get("source_hashes", {}),
            },
        )

    accepted.parent.mkdir(parents=True, exist_ok=True)
    temporary_parent = Path(
        tempfile.mkdtemp(prefix=f".{accepted.name}.promote-", dir=accepted.parent)
    )
    staged = temporary_parent / accepted.name
    try:
        shutil.copytree(candidate, staged)
        accepted_manifest = dict(manifest)
        accepted_manifest.update(
            {
                "status": "accepted",
                "run_id": accepted.name,
                "accepted_utc": datetime.now(UTC).isoformat(),
                "parent_run": candidate.name,
                "user_note": note,
            }
        )
        _atomic_json(staged / VERSION_MANIFEST, accepted_manifest)
        staged.replace(accepted)
    finally:
        shutil.rmtree(temporary_parent, ignore_errors=True)

    if gallery_link is not None:
        link_path, link_record = gallery_link
        _atomic_json(link_path, link_record)
    return accepted


def clone_accepted(accepted_dir: str | Path, workspace_dir: str | Path) -> Path:
    """Create a new editable workspace copy without changing accepted files."""

    raw_accepted = Path(accepted_dir).expanduser()
    raw_workspace = Path(workspace_dir).expanduser()
    if raw_accepted.is_symlink() or raw_workspace.is_symlink():
        raise ValueError("accepted and workspace directories must not be symlinks")
    accepted = raw_accepted.resolve()
    workspace = raw_workspace.resolve()
    if directory_status(accepted) != "accepted":
        raise ValueError("source directory is not an accepted work")
    if workspace.exists():
        raise FileExistsError(f"workspace destination already exists: {workspace}")
    manifest = read_version_manifest(accepted)
    if manifest is None:
        raise ValueError("accepted work is missing version_manifest.json")
    _validate_recorded_files(accepted, manifest)
    _reject_symlinks(accepted)
    workspace.parent.mkdir(parents=True, exist_ok=True)
    temporary_parent = Path(
        tempfile.mkdtemp(prefix=f".{workspace.name}.clone-", dir=workspace.parent)
    )
    staged = temporary_parent / workspace.name
    try:
        shutil.copytree(accepted, staged)
        cloned_manifest = dict(manifest)
        cloned_manifest.update(
            {
                "run_id": workspace.name,
                "status": "workspace",
                "parent_run": accepted.name,
                "derived_from_accepted": True,
                "cloned_utc": datetime.now(UTC).isoformat(),
            }
        )
        _atomic_json(staged / VERSION_MANIFEST, cloned_manifest)
        staged.replace(workspace)
    finally:
        shutil.rmtree(temporary_parent, ignore_errors=True)
    return workspace


def package_reproduction(
    source_files: Mapping[str, str | Path],
    destination: str | Path,
    *,
    entrypoint: str,
    dependencies: Iterable[str],
    metadata: Mapping[str, object] | None = None,
) -> Path:
    """Create a self-contained package from explicitly selected project files."""

    raw_target = Path(destination).expanduser()
    if raw_target.is_symlink():
        raise ValueError(f"reproduction destination must not be a symlink: {raw_target}")
    target = raw_target.resolve()
    if target.exists():
        raise FileExistsError(f"reproduction destination already exists: {target}")
    entrypoint = _safe_relative_name(entrypoint)
    files: dict[str, Path] = {}
    for name, path in source_files.items():
        raw_source = Path(path).expanduser()
        if raw_source.is_symlink():
            raise FileNotFoundError(f"reproduction source does not exist: {raw_source}")
        files[_safe_relative_name(name)] = raw_source.resolve()
    if entrypoint not in files:
        raise ValueError("entrypoint must be included in source_files")
    for source in files.values():
        if not source.is_file() or source.is_symlink():
            raise FileNotFoundError(f"reproduction source does not exist: {source}")

    target.parent.mkdir(parents=True, exist_ok=True)
    temporary_parent = Path(tempfile.mkdtemp(prefix=f".{target.name}.package-", dir=target.parent))
    staged = temporary_parent / target.name
    try:
        staged.mkdir()
        file_records: dict[str, dict[str, object]] = {}
        for relative, source in files.items():
            output = staged / relative
            output.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, output)
            file_records[relative] = {
                "sha256": sha256(output),
                "bytes": output.stat().st_size,
            }
        manifest: dict[str, Any] = {
            "schema_version": "0.1",
            "created_utc": datetime.now(UTC).isoformat(),
            "entrypoint": entrypoint,
            "files": file_records,
            "dependencies": list(dependencies),
            "project_independent": False,
            "independence_status": "not_verified",
            "project_root_env_required": "not_verified",
            "absolute_project_paths": "not_verified",
        }
        if metadata:
            manifest["metadata"] = dict(metadata)
        _atomic_json(staged / REPRODUCTION_MANIFEST, manifest)
        staged.replace(target)
    finally:
        shutil.rmtree(temporary_parent, ignore_errors=True)
    return target


def certify_reproduction(
    package: str | Path,
    *,
    expected_outputs: Iterable[str] = (),
) -> Path:
    """Certify a package only after running its entrypoint outside the package root."""

    root = Path(package).expanduser().resolve()
    manifest_path = root / REPRODUCTION_MANIFEST
    if not root.is_dir() or not manifest_path.is_file() or manifest_path.is_symlink():
        raise FileNotFoundError(f"reproduction package is incomplete: {root}")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if not isinstance(manifest, dict) or not isinstance(manifest.get("files"), Mapping):
        raise ValueError("reproduction manifest requires a files object")
    entrypoint = manifest.get("entrypoint")
    if not isinstance(entrypoint, str):
        raise ValueError("reproduction manifest requires a string entrypoint")
    entrypoint_path = root / _safe_relative_name(entrypoint)
    if not entrypoint_path.is_file() or entrypoint_path.is_symlink():
        raise FileNotFoundError(f"reproduction entrypoint does not exist: {entrypoint_path}")
    for relative, record in manifest["files"].items():
        if not isinstance(relative, str) or not isinstance(record, Mapping):
            raise ValueError("reproduction file records must be objects")
        file_path = root / _safe_relative_name(relative)
        if not file_path.is_file() or file_path.is_symlink():
            raise FileNotFoundError(f"reproduction file does not exist: {file_path}")
        if record.get("sha256") != sha256(file_path):
            raise ValueError(f"reproduction hash mismatch: {relative}")

    environment = os.environ.copy()
    environment.pop("SCIENTIFIC_FIGURE_STUDIO_ROOT", None)
    environment.pop("PYTHONPATH", None)
    expected = tuple(_safe_relative_name(name) for name in expected_outputs)
    with tempfile.TemporaryDirectory(prefix="figure-reproduction-verify-") as temporary:
        verification_root = Path(temporary)
        output_dir = verification_root / "outputs"
        result = subprocess.run(
            [sys.executable, str(entrypoint_path), "--output-dir", str(output_dir)],
            cwd=verification_root,
            env=environment,
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode:
            details = "\n".join(part for part in (result.stdout, result.stderr) if part)
            raise RuntimeError(f"independent reproduction failed:\n{details}")
        missing = [name for name in expected if not (output_dir / name).is_file()]
        if missing:
            raise RuntimeError(f"independent reproduction missing outputs: {missing}")

    manifest.update(
        {
            "project_independent": True,
            "independence_status": "verified_outside_package_root",
            "project_root_env_required": False,
            "absolute_project_paths": False,
            "verification": {
                "method": "subprocess_outside_package_root",
                "environment_variables_removed": [
                    "SCIENTIFIC_FIGURE_STUDIO_ROOT",
                    "PYTHONPATH",
                ],
                "expected_outputs": list(expected),
                "python": f"{sys.version_info.major}.{sys.version_info.minor}",
            },
        }
    )
    _atomic_json(manifest_path, manifest)
    return root
