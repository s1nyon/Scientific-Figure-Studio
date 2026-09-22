"""Verify a locally installed, fixed-commit nature-figure Skill tree."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from dataclasses import asdict, dataclass
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from tools.nature_figure_lock import (  # noqa: E402
    EXPECTED_FILES,
    EXPECTED_HASHES,
    PINNED_COMMIT,
)


@dataclass(frozen=True)
class NatureTreeReport:
    path: str
    commit: str
    file_count: int
    files: tuple[str, ...]


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verify_nature_tree(path: str | Path) -> NatureTreeReport:
    """Validate the exact pinned tree and return a machine-readable report."""

    root = Path(path).expanduser().resolve()
    if not root.is_dir():
        raise ValueError(f"nature-figure tree is missing: {root}")
    actual = {
        file_path.relative_to(root).as_posix(): file_path
        for file_path in root.rglob("*")
        if file_path.is_file()
    }
    expected = set(EXPECTED_FILES)
    missing = sorted(expected.difference(actual))
    extra = sorted(set(actual).difference(expected))
    if missing:
        raise ValueError(f"missing nature-figure files: {missing}")
    if extra:
        raise ValueError(f"extra nature-figure files: {extra}")

    mismatched = {
        relative: (EXPECTED_HASHES[relative], _sha256(actual[relative]))
        for relative in EXPECTED_FILES
        if _sha256(actual[relative]) != EXPECTED_HASHES[relative]
    }
    if mismatched:
        raise ValueError(f"hash mismatch in nature-figure files: {mismatched}")
    return NatureTreeReport(
        path=str(root),
        commit=PINNED_COMMIT,
        file_count=len(actual),
        files=EXPECTED_FILES,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--path", type=Path, required=True)
    arguments = parser.parse_args()
    report = verify_nature_tree(arguments.path)
    print(json.dumps(asdict(report), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
