"""Project adapter for reading, verifying, and recording upstream Nature guidance."""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

from tools.nature_figure_lock import ARCHIVE_URL, DEFAULT_REFERENCES, PINNED_COMMIT
from tools.verify_nature_figure import verify_nature_tree

ADAPTER_VERSION = "0.1.0"


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def build_nature_context(
    skill_root: str | Path,
    references: tuple[str, ...] = DEFAULT_REFERENCES,
) -> dict[str, Any]:
    """Verify the complete upstream tree and read only the requested references."""

    root = Path(skill_root).expanduser().resolve()
    report = verify_nature_tree(root)
    loaded: dict[str, str] = {}
    for relative in references:
        path = root / relative
        try:
            path.resolve().relative_to(root)
        except ValueError as exc:
            message = f"reference is outside verified nature-figure tree: {relative}"
            raise ValueError(message) from exc
        if not path.is_file():
            raise ValueError(f"verified reference is missing: {relative}")
        loaded[relative] = path.read_text(encoding="utf-8")
    return {
        "adapter_version": ADAPTER_VERSION,
        "skill_name": "nature-figure",
        "source_repository": "https://github.com/lth0/codexSkill",
        "archive_url": ARCHIVE_URL,
        "commit": PINNED_COMMIT,
        "tree_file_count": report.file_count,
        "skill_root": str(root),
        "references_loaded": list(references),
        "reference_sha256": {relative: _sha256(root / relative) for relative in references},
        "reference_characters": {relative: len(text) for relative, text in loaded.items()},
        "project_backend": "Python",
        "upstream_r_track_preserved": True,
    }


def require_nature_context(skill_root: str | Path) -> dict[str, Any]:
    """Load the fixed Nature context or fail rather than claiming a fallback."""

    return build_nature_context(skill_root)
