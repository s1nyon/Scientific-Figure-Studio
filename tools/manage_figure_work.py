"""Manage candidate/accepted figure work and retrieve local references."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from figure_studio.artifacts import clone_accepted, promote_candidate  # noqa: E402
from figure_studio.comparison import restore_snapshot  # noqa: E402
from figure_studio.gallery import search_references, search_work_references  # noqa: E402


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)

    references = commands.add_parser("references", help="Search the local reference gallery")
    references.add_argument("--gallery-root", required=True, type=Path)
    references.add_argument("--query")
    references.add_argument("--chart-type")
    references.add_argument("--application")
    references.add_argument("--limit", type=int, default=3)

    works = commands.add_parser("works", help="Search accepted work links")
    works.add_argument("--gallery-root", required=True, type=Path)
    works.add_argument("--query")
    works.add_argument("--limit", type=int, default=3)

    accept = commands.add_parser(
        "accept", help="Promote a candidate after explicit user acceptance"
    )
    accept.add_argument("--candidate-dir", required=True, type=Path)
    accept.add_argument("--accepted-dir", required=True, type=Path)
    accept.add_argument("--user-note", required=True)
    accept.add_argument("--gallery-root", type=Path)

    clone = commands.add_parser("clone", help="Clone an accepted work into a new workspace")
    clone.add_argument("--accepted-dir", required=True, type=Path)
    clone.add_argument("--workspace-dir", required=True, type=Path)

    restore = commands.add_parser("restore", help="Restore a verified snapshot")
    restore.add_argument("--snapshot-dir", required=True, type=Path)
    restore.add_argument("--destination-dir", type=Path)
    restore.add_argument("--overwrite", action="store_true")
    return parser


def main() -> int:
    arguments = _parser().parse_args()
    if arguments.command == "references":
        records = search_references(
            arguments.gallery_root,
            query=arguments.query,
            chart_type=arguments.chart_type,
            application=arguments.application,
            limit=arguments.limit,
        )
        print(json.dumps([record.to_row() for record in records], ensure_ascii=False, indent=2))
    elif arguments.command == "works":
        records = search_work_references(
            arguments.gallery_root,
            query=arguments.query,
            limit=arguments.limit,
        )
        print(
            json.dumps(
                [record.to_mapping() for record in records], ensure_ascii=False, indent=2
            )
        )
    elif arguments.command == "accept":
        accepted = promote_candidate(
            arguments.candidate_dir,
            arguments.accepted_dir,
            user_note=arguments.user_note,
            gallery_root=arguments.gallery_root,
        )
        print(accepted)
    elif arguments.command == "clone":
        print(clone_accepted(arguments.accepted_dir, arguments.workspace_dir))
    else:
        restored = restore_snapshot(
            arguments.snapshot_dir,
            arguments.destination_dir,
            overwrite=arguments.overwrite,
        )
        print(json.dumps({name: str(path) for name, path in restored.items()}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
