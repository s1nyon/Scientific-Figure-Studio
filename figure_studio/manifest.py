"""Data manifest loading, status validation, and provenance helpers."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any

DATA_STATUSES = {
    "formal input data",
    "illustrative practice data",
    "unknown source data",
}
OBJECTIVE_DIRECTIONS = {"minimize", "maximize"}


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def resolve_data_path(data_file: str | Path, base_dir: str | Path) -> Path:
    """Resolve relative manifest paths and preserve external absolute paths."""

    candidate = Path(data_file).expanduser()
    if not candidate.is_absolute():
        candidate = Path(base_dir).expanduser() / candidate
    return candidate.resolve()


def _as_string_tuple(value: object) -> tuple[str, ...]:
    if value is None:
        return ()
    if isinstance(value, str):
        return (value,)
    if not isinstance(value, (list, tuple)):
        raise ValueError("manifest list fields must be strings or lists of strings")
    return tuple(str(item) for item in value)


@dataclass(frozen=True)
class ManifestInfo:
    """Validated manifest values used by templates and export provenance."""

    manifest_path: Path | None
    data_status: str
    data_file: str
    data_path: Path
    fields: dict[str, Any]
    units: dict[str, Any]
    transformations: tuple[str, ...]
    uncertainty: str | None
    unsupported_claims: tuple[str, ...]
    objective_direction: str | None
    objective_directions: tuple[str, ...]
    raw: dict[str, Any]

    @property
    def data_sha256(self) -> str:
        return _sha256(self.data_path)

    def with_data_path(self, data_path: str | Path, base_dir: str | Path) -> ManifestInfo:
        """Return a copy with an explicitly overridden input path."""

        resolved = resolve_data_path(data_path, base_dir)
        if not resolved.is_file():
            raise FileNotFoundError(f"data file does not exist: {resolved}")
        return replace(self, data_file=str(data_path), data_path=resolved)


def load_manifest(
    path_or_mapping: str | Path | Mapping[str, object],
    base_dir: str | Path | None = None,
) -> ManifestInfo:
    """Load and validate a JSON manifest or an in-memory manifest mapping."""

    manifest_path: Path | None = None
    if isinstance(path_or_mapping, (str, Path)):
        manifest_path = Path(path_or_mapping).expanduser().resolve()
        if not manifest_path.is_file():
            raise FileNotFoundError(f"manifest file does not exist: {manifest_path}")
        raw_value = json.loads(manifest_path.read_text(encoding="utf-8"))
        if not isinstance(raw_value, dict):
            raise ValueError("manifest JSON must contain an object")
        raw = dict(raw_value)
        root = (
            Path(base_dir).expanduser().resolve()
            if base_dir is not None
            else manifest_path.parent
        )
    elif isinstance(path_or_mapping, Mapping):
        raw = dict(path_or_mapping)
        root = Path(base_dir or Path.cwd()).expanduser().resolve()
    else:
        raise TypeError("manifest must be a path or mapping")
    if base_dir is not None and manifest_path is None:
        root = Path(base_dir).expanduser().resolve()

    status = str(raw.get("data_status", ""))
    if status not in DATA_STATUSES:
        choices = ", ".join(sorted(DATA_STATUSES))
        raise ValueError(f"data_status must be one of: {choices}")
    if not raw.get("data_file"):
        raise ValueError("manifest requires data_file")
    data_file = str(raw["data_file"])
    data_path = resolve_data_path(data_file, root)
    if not data_path.is_file():
        raise FileNotFoundError(f"data file does not exist: {data_path}")

    objective_direction = raw.get("objective_direction")
    if objective_direction is not None:
        objective_direction = str(objective_direction)
        if objective_direction not in OBJECTIVE_DIRECTIONS:
            raise ValueError("objective_direction must be 'minimize' or 'maximize'")
    objective_directions = _as_string_tuple(raw.get("objective_directions"))
    invalid_directions = set(objective_directions).difference(OBJECTIVE_DIRECTIONS)
    if invalid_directions:
        raise ValueError(f"invalid objective_directions: {sorted(invalid_directions)}")

    return ManifestInfo(
        manifest_path=manifest_path,
        data_status=status,
        data_file=data_file,
        data_path=data_path,
        fields=dict(raw.get("fields") or {}),
        units=dict(raw.get("units") or {}),
        transformations=_as_string_tuple(raw.get("transformations")),
        uncertainty=str(raw["uncertainty"]) if raw.get("uncertainty") is not None else None,
        unsupported_claims=_as_string_tuple(raw.get("unsupported_claims")),
        objective_direction=objective_direction,
        objective_directions=objective_directions,
        raw=raw,
    )


def provenance_data_label(status: str) -> str | None:
    """Return a visible label only for explicitly declared practice data."""

    if status == "illustrative practice data":
        return "练习数据 · illustrative practice data"
    return None


def _portable_data_reference(manifest: ManifestInfo) -> str:
    """Return a provenance path that does not bind a delivery to one machine."""

    requested = Path(manifest.data_file).expanduser()
    if requested.is_absolute():
        return f"<external-input>/{requested.name}"
    return requested.as_posix()


def build_data_provenance(
    manifest: ManifestInfo,
    extra: Mapping[str, object] | None = None,
) -> dict[str, object]:
    """Create a consistent provenance payload without changing the source file."""

    data_reference = _portable_data_reference(manifest)
    provenance: dict[str, object] = {
        "data_status": manifest.data_status,
        "data_file": data_reference,
        "resolved_data_path": data_reference,
        "data_sha256": manifest.data_sha256,
        "fields": manifest.fields,
        "units": manifest.units,
        "transformations": list(manifest.transformations),
        "uncertainty": manifest.uncertainty,
        "unsupported_claims": list(manifest.unsupported_claims),
    }
    if manifest.objective_direction:
        provenance["objective_direction"] = manifest.objective_direction
    if manifest.objective_directions:
        provenance["objective_directions"] = list(manifest.objective_directions)
    if extra:
        provenance.update(extra)
    return provenance
