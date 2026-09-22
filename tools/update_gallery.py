"""Update the local figure-gallery index without modifying source images."""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from figure_studio.gallery import GalleryIndex  # noqa: E402


def main() -> int:
    gallery = GalleryIndex(PROJECT_ROOT / "figure_gallery")
    records = gallery.scan()
    print(f"Indexed {len(records)} gallery image(s) at {gallery.index_path}")
    reviewed = sum(record.visual_analysis_status == "agent_reviewed" for record in records)
    print(f"Explicit visual reviews: {reviewed}; remaining not analyzed: {len(records) - reviewed}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
