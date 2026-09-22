"""Snapshot, restore, and compare a reproducible figure revision package."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from figure_studio.comparison import (  # noqa: E402
    build_before_after_comparison,
    restore_snapshot,
    snapshot_artifacts,
)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    snapshot = subparsers.add_parser("snapshot", help="Save a pre-edit artifact snapshot")
    snapshot.add_argument("--snapshot-dir", required=True, type=Path)
    snapshot.add_argument("paths", nargs="+", type=Path)

    restore = subparsers.add_parser("restore", help="Restore a saved artifact snapshot")
    restore.add_argument("--snapshot-dir", required=True, type=Path)
    restore.add_argument("--destination-dir", type=Path)
    restore.add_argument("--overwrite", action="store_true")

    compare = subparsers.add_parser("compare", help="Build a native-aspect Before/After PNG")
    compare.add_argument("--before", required=True, type=Path)
    compare.add_argument("--after", required=True, type=Path)
    compare.add_argument("--output", required=True, type=Path)
    compare.add_argument("--title", default="Before / After")
    compare.add_argument("--overwrite", action="store_true")
    return parser


def main() -> None:
    arguments = _parser().parse_args()
    if arguments.command == "snapshot":
        snapshot_artifacts(arguments.paths, arguments.snapshot_dir)
    elif arguments.command == "restore":
        restore_snapshot(
            arguments.snapshot_dir,
            arguments.destination_dir,
            overwrite=arguments.overwrite,
        )
    else:
        build_before_after_comparison(
            arguments.before,
            arguments.after,
            arguments.output,
            title=arguments.title,
            overwrite=arguments.overwrite,
        )


if __name__ == "__main__":
    main()
