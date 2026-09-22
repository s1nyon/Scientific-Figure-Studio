"""Install the complete pinned nature-figure Skill outside this repository."""

from __future__ import annotations

import argparse
import shutil
import sys
import tempfile
import urllib.request
import uuid
import zipfile
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from tools.nature_figure_lock import ARCHIVE_URL  # noqa: E402
from tools.verify_nature_figure import verify_nature_tree  # noqa: E402


def default_destination() -> Path:
    return Path.home() / ".codex" / "skills" / "nature-figure"


def _extract_skill(archive: Path, destination: Path) -> None:
    prefix_suffix = "/skills/codex/nature-figure/"
    destination.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(archive) as bundle:
        members = [member for member in bundle.infolist() if prefix_suffix in member.filename]
        if not members:
            raise ValueError("pinned archive does not contain skills/codex/nature-figure")
        for member in members:
            relative = member.filename.split(prefix_suffix, 1)[1]
            if not relative or member.is_dir():
                continue
            target = (destination / Path(relative)).resolve()
            target.relative_to(destination.resolve())
            target.parent.mkdir(parents=True, exist_ok=True)
            with bundle.open(member) as source, target.open("wb") as target_stream:
                shutil.copyfileobj(source, target_stream)


def install(destination: str | Path | None = None, force: bool = False) -> Path:
    """Download, verify, and install the pinned Skill tree."""

    target = Path(destination or default_destination()).expanduser().resolve()
    if target.exists() and not force:
        raise FileExistsError(
            f"Refusing to overwrite existing Skill; pass force=True to back it up first: {target}"
        )
    target.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="nature-figure-install-") as temporary:
        temporary_root = Path(temporary)
        archive = temporary_root / "source.zip"
        extracted = temporary_root / "nature-figure"
        with urllib.request.urlopen(ARCHIVE_URL, timeout=60) as response, archive.open(
            "wb"
        ) as stream:
            shutil.copyfileobj(response, stream)
        _extract_skill(archive, extracted)
        verify_nature_tree(extracted)

        staging = target.parent / f".{target.name}.staging-{uuid.uuid4().hex}"
        shutil.copytree(extracted, staging)
        backup: Path | None = None
        try:
            if target.exists():
                backup = target.parent / f"{target.name}.backup-{uuid.uuid4().hex}"
                target.rename(backup)
            staging.rename(target)
        except Exception:
            if staging.exists():
                shutil.rmtree(staging)
            if backup is not None and backup.exists() and not target.exists():
                backup.rename(target)
            raise
    return target


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--destination", type=Path, default=default_destination())
    parser.add_argument("--force", action="store_true")
    arguments = parser.parse_args()
    installed = install(arguments.destination, force=arguments.force)
    print(installed)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
