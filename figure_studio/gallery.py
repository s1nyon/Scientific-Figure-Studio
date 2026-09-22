"""A small, local, non-destructive reference-gallery index."""

import csv
import hashlib
import json
from collections.abc import Iterable, Mapping
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path

import numpy as np
from PIL import Image

IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".webp", ".tif", ".tiff"}
CSV_FIELDS = (
    "relative_path",
    "sha256",
    "width",
    "height",
    "mode",
    "file_size",
    "modified_utc",
    "dominant_color",
    "mean_luminance",
    "grayscale_estimate",
    "whitespace_estimate",
    "is_duplicate",
    "favorite",
    "style",
    "chart_type",
    "application",
    "tags",
    "source",
    "user_evaluation",
    "analysis_date",
    "visual_analysis_status",
    "visual_analysis_date",
    "visual_analysis_by",
    "visual_analysis_notes",
)


@dataclass
class GalleryRecord:
    """Factual and manually editable metadata for one image."""

    relative_path: str
    sha256: str
    width: int
    height: int
    mode: str
    file_size: int
    modified_utc: str
    dominant_color: str
    mean_luminance: float
    grayscale_estimate: bool
    whitespace_estimate: float
    is_duplicate: bool = False
    favorite: bool = False
    style: str = ""
    chart_type: str = ""
    application: str = ""
    tags: str = ""
    source: str = ""
    user_evaluation: str = ""
    analysis_date: str = field(default_factory=lambda: datetime.now(UTC).date().isoformat())
    visual_analysis_status: str = "not_analyzed"
    visual_analysis_date: str = ""
    visual_analysis_by: str = ""
    visual_analysis_notes: str = ""

    def to_row(self) -> dict[str, str]:
        return {
            "relative_path": self.relative_path,
            "sha256": self.sha256,
            "width": str(self.width),
            "height": str(self.height),
            "mode": self.mode,
            "file_size": str(self.file_size),
            "modified_utc": self.modified_utc,
            "dominant_color": self.dominant_color,
            "mean_luminance": f"{self.mean_luminance:.4f}",
            "grayscale_estimate": str(self.grayscale_estimate).lower(),
            "whitespace_estimate": f"{self.whitespace_estimate:.4f}",
            "is_duplicate": str(self.is_duplicate).lower(),
            "favorite": str(self.favorite).lower(),
            "style": self.style,
            "chart_type": self.chart_type,
            "application": self.application,
            "tags": self.tags,
            "source": self.source,
            "user_evaluation": self.user_evaluation,
            "analysis_date": self.analysis_date,
            "visual_analysis_status": self.visual_analysis_status,
            "visual_analysis_date": self.visual_analysis_date,
            "visual_analysis_by": self.visual_analysis_by,
            "visual_analysis_notes": self.visual_analysis_notes,
        }


class GalleryIndex:
    """Scan and search a local gallery without changing source images."""

    def __init__(self, root: str | Path):
        self.root = Path(root).expanduser().resolve()
        self.generated_root = self.root / "_generated"
        self.notes_root = self.generated_root / "gallery_notes"
        self.visual_analysis_root = self.generated_root / "gallery_visual_analysis"
        self.index_path = self.root / "gallery_index.csv"
        self._records: list[GalleryRecord] = []
        self._scanned = False

    def _image_paths(self) -> list[Path]:
        if not self.root.exists():
            return []
        return sorted(
            path
            for path in self.root.rglob("*")
            if path.is_file()
            and path.suffix.lower() in IMAGE_SUFFIXES
            and self.generated_root not in path.parents
        )

    def _relative_path(self, path: Path) -> str:
        return path.resolve().relative_to(self.root).as_posix()

    @staticmethod
    def _hash(path: Path) -> str:
        digest = hashlib.sha256()
        with path.open("rb") as stream:
            for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                digest.update(chunk)
        return digest.hexdigest()

    @staticmethod
    def _dominant_color(image: Image.Image) -> str:
        quantized = image.convert("RGB").resize((64, 64)).quantize(colors=8)
        counts = quantized.getcolors(maxcolors=64 * 64)
        if not counts:
            return "#000000"
        _, color_index = max(counts)
        palette = quantized.getpalette()
        red, green, blue = palette[color_index * 3 : color_index * 3 + 3]
        return f"#{red:02X}{green:02X}{blue:02X}"

    @staticmethod
    def _pixel_facts(image: Image.Image) -> tuple[float, bool, float]:
        array = np.asarray(image.convert("RGB").resize((100, 100)), dtype=np.float32)
        luminance = (0.2126 * array[:, :, 0] + 0.7152 * array[:, :, 1] + 0.0722 * array[:, :, 2])
        channel_spread = np.max(array, axis=2) - np.min(array, axis=2)
        grayscale_estimate = float(np.mean(channel_spread < 5.0)) >= 0.9
        whitespace_estimate = float(np.mean(np.all(array >= 245.0, axis=2)))
        return float(np.mean(luminance)), grayscale_estimate, whitespace_estimate

    @staticmethod
    def _suggested_style(relative_path: str) -> str:
        folder = Path(relative_path).parts[0] if Path(relative_path).parts else ""
        return {
            "01_minimal": "minimal_editorial",
            "02_algorithm": "algorithm_research",
            "03_visual_narrative": "visual_narrative",
        }.get(folder, "")

    def _load_existing(self) -> dict[str, GalleryRecord]:
        if not self.index_path.exists():
            return {}
        with self.index_path.open(newline="", encoding="utf-8-sig") as stream:
            return {
                row["relative_path"]: self._record_from_row(row)
                for row in csv.DictReader(stream)
                if row.get("relative_path")
            }

    @staticmethod
    def _record_from_row(row: dict[str, str]) -> GalleryRecord:
        return GalleryRecord(
            relative_path=row["relative_path"],
            sha256=row.get("sha256", ""),
            width=int(row.get("width", 0)),
            height=int(row.get("height", 0)),
            mode=row.get("mode", ""),
            file_size=int(row.get("file_size", 0)),
            modified_utc=row.get("modified_utc", ""),
            dominant_color=row.get("dominant_color", "#000000"),
            mean_luminance=float(row.get("mean_luminance", 0.0)),
            grayscale_estimate=row.get("grayscale_estimate", "false").lower() == "true",
            whitespace_estimate=float(row.get("whitespace_estimate", 0.0)),
            is_duplicate=row.get("is_duplicate", "false").lower() == "true",
            favorite=row.get("favorite", "false").lower() == "true",
            style=row.get("style", ""),
            chart_type=row.get("chart_type", ""),
            application=row.get("application", ""),
            tags=row.get("tags", ""),
            source=row.get("source", ""),
            user_evaluation=row.get("user_evaluation", ""),
            analysis_date=row.get("analysis_date", ""),
            visual_analysis_status=row.get("visual_analysis_status", "not_analyzed")
            or "not_analyzed",
            visual_analysis_date=row.get("visual_analysis_date", ""),
            visual_analysis_by=row.get("visual_analysis_by", ""),
            visual_analysis_notes=row.get("visual_analysis_notes", ""),
        )

    def analyze(self, path: str | Path) -> GalleryRecord:
        """Analyze one image and write a separate factual design note."""

        image_path = Path(path).expanduser().resolve()
        if image_path.suffix.lower() not in IMAGE_SUFFIXES:
            raise ValueError(f"Unsupported gallery image type: {image_path.suffix}")
        relative_path = self._relative_path(image_path)
        stat = image_path.stat()
        with Image.open(image_path) as image:
            image.load()
            mean_luminance, grayscale_estimate, whitespace_estimate = self._pixel_facts(image)
            record = GalleryRecord(
                relative_path=relative_path,
                sha256=self._hash(image_path),
                width=image.width,
                height=image.height,
                mode=image.mode,
                file_size=stat.st_size,
                modified_utc=datetime.fromtimestamp(stat.st_mtime, UTC).isoformat(),
                dominant_color=self._dominant_color(image),
                mean_luminance=mean_luminance,
                grayscale_estimate=grayscale_estimate,
                whitespace_estimate=whitespace_estimate,
                style=self._suggested_style(relative_path),
            )
        return record

    def _write_note(self, record: GalleryRecord) -> None:
        self.notes_root.mkdir(parents=True, exist_ok=True)
        note_path = self.notes_root / f"{record.sha256}.md"
        note = f"""# Gallery design note

- Relative path: `{record.relative_path}`
- Content hash: `{record.sha256}`
- Analysis date: `{record.analysis_date}`
- Source and license: unknown; fill manually when available.
- User evaluation: {record.user_evaluation or "blank until the user writes it"}.

## Observable facts

- Image dimensions: {record.width} × {record.height} px.
- Image mode: `{record.mode}`.
- Estimated dominant color: `{record.dominant_color}`.
- Mean luminance estimate: {record.mean_luminance:.3f} on a 0–255 scale.
- Grayscale tendency estimate: `{record.grayscale_estimate}`.
- Light-background pixel ratio estimate: {record.whitespace_estimate:.3f}.

## Interpretation limits

The chart type, original font, source data, research conclusion, exact line widths,
and user preference are unknown unless manually supplied. The pixel-derived color
and layout observations are estimates and should guide questions, not replace
visual review.

## Possible design methods to inspect manually

- Compare the whitespace estimate and dominant color with the intended page size.
- Check whether the contrast is carried by line style, marker, or direct labels
  in addition to color.
- Record a chart type and application only after a person has inspected the image.
"""
        note_path.write_text(note, encoding="utf-8")

    def _write_visual_analysis(self, record: GalleryRecord) -> Path:
        """Write explicit Agent observations separately from deterministic notes."""

        self.visual_analysis_root.mkdir(parents=True, exist_ok=True)
        note_path = self.visual_analysis_root / f"{record.sha256}.md"
        note = f"""# Agent visual analysis

- Relative path: `{record.relative_path}`
- Content hash: `{record.sha256}`
- Analysis date: `{record.visual_analysis_date}`
- Analyzed by: `{record.visual_analysis_by}`

## Observations

{record.visual_analysis_notes}

This file records an explicit visual review and is not produced by the
deterministic metadata scanner.
"""
        note_path.write_text(note, encoding="utf-8")
        return note_path

    def scan(self) -> list[GalleryRecord]:
        """Incrementally scan supported images and update generated metadata."""

        existing = self._load_existing()
        records = [self.analyze(path) for path in self._image_paths()]
        by_hash: dict[str, list[GalleryRecord]] = {}
        for record in records:
            by_hash.setdefault(record.sha256, []).append(record)
            previous = existing.get(record.relative_path)
            if previous and previous.sha256 == record.sha256:
                record.favorite = previous.favorite
                record.style = previous.style or record.style
                record.chart_type = previous.chart_type
                record.application = previous.application
                record.tags = previous.tags
                record.source = previous.source
                record.user_evaluation = previous.user_evaluation
                record.analysis_date = previous.analysis_date or record.analysis_date
                record.visual_analysis_status = previous.visual_analysis_status or "not_analyzed"
                record.visual_analysis_date = previous.visual_analysis_date
                record.visual_analysis_by = previous.visual_analysis_by
                record.visual_analysis_notes = previous.visual_analysis_notes
        for same_hash in by_hash.values():
            for index, record in enumerate(same_hash):
                record.is_duplicate = index > 0
        for record in records:
            self._write_note(record)
        self._records = records
        self._scanned = True
        self.write_index(records)
        return records

    def write_index(self, records: Iterable[GalleryRecord] | None = None) -> Path:
        """Write CSV metadata atomically, preserving the source image files."""

        rows = list(records if records is not None else self._records)
        self.root.mkdir(parents=True, exist_ok=True)
        temporary = self.index_path.with_suffix(".csv.tmp")
        with temporary.open("w", newline="", encoding="utf-8") as stream:
            writer = csv.DictWriter(stream, fieldnames=CSV_FIELDS)
            writer.writeheader()
            writer.writerows(record.to_row() for record in rows)
        temporary.replace(self.index_path)
        self._records = rows
        return self.index_path

    def search(
        self,
        query: str | None = None,
        style: str | None = None,
        favorite: bool | None = None,
    ) -> list[GalleryRecord]:
        """Search indexed metadata; an empty gallery returns an empty list."""

        if not self._scanned:
            self.scan()
        query_lower = query.lower() if query else None
        results = []
        for record in self._records:
            if favorite is not None and record.favorite is not favorite:
                continue
            if style and record.style.lower() != style.lower():
                continue
            searchable = " ".join(
                [
                    record.relative_path,
                    record.style,
                    record.chart_type,
                    record.application,
                    record.tags,
                ]
            ).lower()
            if query_lower and query_lower not in searchable:
                continue
            results.append(record)
        return sorted(results, key=lambda item: (not item.favorite, item.relative_path))

    def record_agent_analysis(
        self,
        relative_path: str | Path,
        observations: Mapping[str, object],
        analyzed_by: str = "codex",
    ) -> GalleryRecord:
        """Persist explicit visual observations without modifying the source image."""

        image_path = (self.root / Path(relative_path)).resolve()
        if not image_path.is_relative_to(self.root):
            raise ValueError("relative_path must point inside the gallery root")
        if not image_path.exists():
            raise FileNotFoundError(image_path)
        if not self._scanned:
            self.scan()
        path_key = self._relative_path(image_path)
        record = next((item for item in self._records if item.relative_path == path_key), None)
        if record is None or record.sha256 != self._hash(image_path):
            self.scan()
            record = next(
                (item for item in self._records if item.relative_path == path_key),
                None,
            )
        if record is None:
            raise FileNotFoundError(f"Image is not indexed: {path_key}")

        record.visual_analysis_status = "agent_reviewed"
        record.visual_analysis_date = datetime.now(UTC).isoformat()
        record.visual_analysis_by = analyzed_by
        record.visual_analysis_notes = json.dumps(
            dict(observations), ensure_ascii=False, indent=2, sort_keys=True, default=str
        )
        self._write_visual_analysis(record)
        self.write_index(self._records)
        return record
