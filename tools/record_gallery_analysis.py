"""Record an explicit Agent visual review without modifying the source image."""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Mapping
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from figure_studio.gallery import GalleryIndex  # noqa: E402


def _load_object(path: Path) -> dict[str, object]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, Mapping):
        raise ValueError(f"JSON file must contain an object: {path}")
    return dict(value)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--gallery-root", required=True, type=Path)
    parser.add_argument("--image", required=True, help="Gallery-relative image path")
    parser.add_argument("--observations", required=True, type=Path)
    parser.add_argument("--view-receipt", required=True, type=Path)
    parser.add_argument("--analyzed-by", default="codex")
    return parser


def main() -> int:
    arguments = _parser().parse_args()
    gallery = GalleryIndex(arguments.gallery_root)
    gallery.scan()
    record = gallery.record_agent_analysis(
        arguments.image,
        _load_object(arguments.observations),
        analyzed_by=arguments.analyzed_by,
        viewed=True,
        view_receipt=_load_object(arguments.view_receipt),
    )
    print(
        json.dumps(
            {
                "relative_path": record.relative_path,
                "sha256": record.sha256,
                "visual_analysis_status": record.visual_analysis_status,
                "visual_analysis_date": record.visual_analysis_date,
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
