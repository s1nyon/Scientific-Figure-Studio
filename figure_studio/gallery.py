"""A small, local, non-destructive reference-gallery index."""

import csv
import hashlib
import json
from collections.abc import Iterable, Mapping
from dataclasses import dataclass, field, replace
from datetime import UTC, datetime
from pathlib import Path

import numpy as np
from PIL import Image

from .artifacts import directory_status

IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".webp", ".tif", ".tiff"}
CSV_FIELDS = (
    "relative_path",
    "sha256",
    "width",
    "height",
    "mode",
    "file_size",
    "modified_utc",
    "availability",
    "content_changed",
    "previous_sha256",
    "preference_review_status",
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
    "visual_analysis_viewed",
    "visual_analysis_receipt",
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
    availability: str = "present"
    content_changed: bool = False
    previous_sha256: str = ""
    preference_review_status: str = "not_required"
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
    visual_analysis_viewed: bool = False
    visual_analysis_receipt: str = ""

    def to_row(self) -> dict[str, str]:
        return {
            "relative_path": self.relative_path,
            "sha256": self.sha256,
            "width": str(self.width),
            "height": str(self.height),
            "mode": self.mode,
            "file_size": str(self.file_size),
            "modified_utc": self.modified_utc,
            "availability": self.availability,
            "content_changed": str(self.content_changed).lower(),
            "previous_sha256": self.previous_sha256,
            "preference_review_status": self.preference_review_status,
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
            "visual_analysis_viewed": str(self.visual_analysis_viewed).lower(),
            "visual_analysis_receipt": self.visual_analysis_receipt,
        }


@dataclass(frozen=True)
class GalleryWorkReference:
    """A verified link from a gallery entry to an explicitly accepted work."""

    work_id: str
    status: str
    user_evaluation: str
    accepted_directory: str
    candidate_directory: str
    visual_design_reference: str
    code_reference: dict[str, object]
    source_hashes: dict[str, str]
    available: bool

    def to_mapping(self) -> dict[str, object]:
        return {
            "work_id": self.work_id,
            "status": self.status,
            "user_evaluation": self.user_evaluation,
            "accepted_directory": self.accepted_directory,
            "candidate_directory": self.candidate_directory,
            "visual_design_reference": self.visual_design_reference,
            "code_reference": dict(self.code_reference),
            "source_hashes": dict(self.source_hashes),
            "available": self.available,
        }


class GalleryIndex:
    """Scan and search a local gallery without changing source images."""

    def __init__(self, root: str | Path):
        self.root = Path(root).expanduser().resolve()
        self.generated_root = self.root / "_generated"
        self.notes_root = self.generated_root / "gallery_notes"
        self.visual_analysis_root = self.generated_root / "gallery_visual_analysis"
        self.history_root = self.generated_root / "gallery_history"
        self.work_links_root = self.generated_root / "work_links"
        self.preferences_path = self.generated_root / "gallery_preferences.json"
        self.stale_report_path = self.generated_root / "stale_records.json"
        self.index_path = self.root / "gallery_index.csv"
        self._records: list[GalleryRecord] = []
        self._stale_records: list[GalleryRecord] = []
        self._scanned = False

    def _image_paths(self) -> list[Path]:
        if not self.root.exists():
            return []
        return sorted(
            path
            for path in self.root.rglob("*")
            if path.is_file()
            and not path.is_symlink()
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

    def _load_preferences(self) -> dict[str, dict[str, object]]:
        if not self.preferences_path.is_file():
            return {}
        value = json.loads(self.preferences_path.read_text(encoding="utf-8"))
        if not isinstance(value, dict):
            raise ValueError("gallery_preferences.json must contain an object")
        return {
            str(relative_path): dict(fields)
            for relative_path, fields in value.items()
            if isinstance(fields, Mapping)
        }

    def _save_preferences(self) -> None:
        self.generated_root.mkdir(parents=True, exist_ok=True)
        preferences = {
            record.relative_path: {
                "favorite": record.favorite,
                "style": record.style,
                "chart_type": record.chart_type,
                "application": record.application,
                "tags": record.tags,
                "source": record.source,
                "user_evaluation": record.user_evaluation,
            }
            for record in self._records
            if record.favorite
            or record.style
            or record.chart_type
            or record.application
            or record.tags
            or record.source
            or record.user_evaluation
        }
        temporary = self.preferences_path.with_suffix(".json.tmp")
        temporary.write_text(
            json.dumps(preferences, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        temporary.replace(self.preferences_path)

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
            availability=row.get("availability", "present") or "present",
            content_changed=row.get("content_changed", "false").lower() == "true",
            previous_sha256=row.get("previous_sha256", "") or "",
            preference_review_status=row.get("preference_review_status", "not_required")
            or "not_required",
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
            visual_analysis_viewed=row.get("visual_analysis_viewed", "false").lower() == "true",
            visual_analysis_receipt=row.get("visual_analysis_receipt", "") or "",
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
- Viewed by Agent: `{record.visual_analysis_viewed}`
- View receipt: `{record.visual_analysis_receipt}`

## Observations

{record.visual_analysis_notes}

This file records an explicit visual review and is not produced by the
deterministic metadata scanner.
"""
        note_path.write_text(note, encoding="utf-8")
        return note_path

    def _write_history(
        self,
        previous: GalleryRecord,
        current: GalleryRecord,
        *,
        reason: str,
    ) -> None:
        """Append a content-change record without deleting the older metadata."""

        self.history_root.mkdir(parents=True, exist_ok=True)
        key = hashlib.sha256(previous.relative_path.encode("utf-8")).hexdigest()
        history_path = self.history_root / f"{key}.json"
        history: list[dict[str, object]] = []
        if history_path.is_file():
            raw = json.loads(history_path.read_text(encoding="utf-8"))
            if isinstance(raw, list):
                history = [dict(item) for item in raw if isinstance(item, Mapping)]
        if any(
            item.get("old_sha256") == previous.sha256 and item.get("new_sha256") == current.sha256
            for item in history
        ):
            return
        history.append(
            {
                "recorded_utc": datetime.now(UTC).isoformat(),
                "relative_path": previous.relative_path,
                "old_sha256": previous.sha256,
                "new_sha256": current.sha256,
                "reason": reason,
                "previous_record": previous.to_row(),
                "user_fields_preserved": {
                    "favorite": previous.favorite,
                    "style": previous.style,
                    "chart_type": previous.chart_type,
                    "application": previous.application,
                    "tags": previous.tags,
                    "source": previous.source,
                    "user_evaluation": previous.user_evaluation,
                },
            }
        )
        history_path.write_text(
            json.dumps(history, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )

    @staticmethod
    def _copy_user_fields(previous: GalleryRecord, current: GalleryRecord) -> None:
        current.favorite = previous.favorite
        current.style = previous.style or current.style
        current.chart_type = previous.chart_type
        current.application = previous.application
        current.tags = previous.tags
        current.source = previous.source
        current.user_evaluation = previous.user_evaluation

    def _apply_preference(self, record: GalleryRecord, preference: Mapping[str, object]) -> None:
        if "favorite" in preference:
            record.favorite = bool(preference["favorite"])
        for field_name in (
            "style",
            "chart_type",
            "application",
            "tags",
            "source",
            "user_evaluation",
        ):
            if field_name in preference and preference[field_name] is not None:
                setattr(record, field_name, str(preference[field_name]))

    def scan(self) -> list[GalleryRecord]:
        """Incrementally scan supported images and update generated metadata."""

        existing = self._load_existing()
        preferences = self._load_preferences()
        records = [self.analyze(path) for path in self._image_paths()]
        existing_by_hash: dict[str, GalleryRecord] = {}
        for previous in existing.values():
            existing_by_hash.setdefault(previous.sha256, previous)
        by_hash: dict[str, list[GalleryRecord]] = {}
        for record in records:
            by_hash.setdefault(record.sha256, []).append(record)
            previous = existing.get(record.relative_path) or existing_by_hash.get(record.sha256)
            if previous and previous.sha256 == record.sha256:
                self._copy_user_fields(previous, record)
                record.analysis_date = previous.analysis_date or record.analysis_date
                record.visual_analysis_status = previous.visual_analysis_status or "not_analyzed"
                record.visual_analysis_date = previous.visual_analysis_date
                record.visual_analysis_by = previous.visual_analysis_by
                record.visual_analysis_notes = previous.visual_analysis_notes
                record.visual_analysis_viewed = previous.visual_analysis_viewed
                record.visual_analysis_receipt = previous.visual_analysis_receipt
                record.preference_review_status = previous.preference_review_status
            elif previous:
                self._copy_user_fields(previous, record)
                record.content_changed = True
                record.previous_sha256 = previous.sha256
                record.preference_review_status = "needs_review"
                record.visual_analysis_status = "stale"
                record.visual_analysis_date = previous.visual_analysis_date
                record.visual_analysis_by = previous.visual_analysis_by
                record.visual_analysis_viewed = previous.visual_analysis_viewed
                record.visual_analysis_receipt = previous.visual_analysis_receipt
                self._write_history(previous, record, reason="content_hash_changed")
            if record.relative_path in preferences:
                self._apply_preference(record, preferences[record.relative_path])
        for same_hash in by_hash.values():
            for index, record in enumerate(same_hash):
                record.is_duplicate = index > 0
        for record in records:
            self._write_note(record)
        current_paths = {record.relative_path for record in records}
        missing_records: list[GalleryRecord] = []
        for previous in existing.values():
            if previous.relative_path in current_paths:
                continue
            missing = replace(
                previous,
                availability="missing",
                preference_review_status="needs_review",
                visual_analysis_status="stale",
            )
            missing_records.append(missing)
        self._records = records + missing_records
        self._stale_records = [
            record
            for record in self._records
            if record.availability != "present" or record.visual_analysis_status == "stale"
        ]
        self._scanned = True
        self.write_index(self._records)
        self.generated_root.mkdir(parents=True, exist_ok=True)
        self.stale_report_path.write_text(
            json.dumps(
                [record.to_row() for record in self._stale_records],
                ensure_ascii=False,
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
        return self._records

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
        chart_type: str | None = None,
        application: str | None = None,
        favorite: bool | None = None,
        analyzed_only: bool = False,
        limit: int | None = None,
    ) -> list[GalleryRecord]:
        """Search indexed metadata; an empty gallery returns an empty list."""

        if not self._scanned:
            self.scan()
        query_lower = query.lower() if query else None
        results = []
        for record in self._records:
            if record.availability != "present":
                continue
            if favorite is not None and record.favorite is not favorite:
                continue
            if style and record.style.lower() != style.lower():
                continue
            if chart_type and record.chart_type.lower() != chart_type.lower():
                continue
            if application and record.application.lower() != application.lower():
                continue
            if analyzed_only and record.visual_analysis_status != "agent_reviewed":
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
        ordered = sorted(
            results,
            key=lambda item: (
                not item.favorite,
                item.visual_analysis_status != "agent_reviewed",
                item.relative_path,
            ),
        )
        return ordered[:limit] if limit is not None else ordered

    def stale_records(self) -> list[GalleryRecord]:
        """Return content-changed or missing records without removing them."""

        if not self._scanned:
            self.scan()
        return list(self._stale_records)

    def _load_work_links(self) -> list[GalleryWorkReference]:
        if not self.work_links_root.is_dir():
            return []
        references: list[GalleryWorkReference] = []
        for link_path in sorted(self.work_links_root.glob("*.json")):
            try:
                raw = json.loads(link_path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                continue
            if not isinstance(raw, Mapping):
                continue
            accepted_directory = str(raw.get("accepted_directory", ""))
            candidate_directory = str(raw.get("candidate_directory", ""))
            accepted_path = Path(accepted_directory).expanduser()
            if not accepted_path.is_absolute():
                accepted_path = (self.root / accepted_path).resolve()
            try:
                accepted_status = directory_status(accepted_path)
            except (OSError, ValueError, json.JSONDecodeError):
                accepted_status = None
            available = (
                bool(accepted_directory)
                and not accepted_path.is_symlink()
                and accepted_status == "accepted"
                and (accepted_path / "plot.py").is_file()
                and (accepted_path / "version_manifest.json").is_file()
            )
            code_reference = raw.get("code_reference", {})
            source_hashes = raw.get("source_hashes", {})
            references.append(
                GalleryWorkReference(
                    work_id=str(raw.get("work_id", link_path.stem)),
                    status=str(raw.get("status", "unknown")),
                    user_evaluation=str(raw.get("user_evaluation", "")),
                    accepted_directory=accepted_directory,
                    candidate_directory=candidate_directory,
                    visual_design_reference=str(raw.get("visual_design_reference", "")),
                    code_reference=(
                        dict(code_reference) if isinstance(code_reference, Mapping) else {}
                    ),
                    source_hashes=(
                        {str(key): str(value) for key, value in source_hashes.items()}
                        if isinstance(source_hashes, Mapping)
                        else {}
                    ),
                    available=available,
                )
            )
        return references

    def search_works(
        self,
        query: str | None = None,
        *,
        limit: int | None = None,
    ) -> list[GalleryWorkReference]:
        """Find accepted work links for code or visual-design reuse."""

        query_lower = query.lower() if query else None
        matches: list[GalleryWorkReference] = []
        for reference in self._load_work_links():
            if reference.status != "accepted" or not reference.available:
                continue
            searchable = " ".join(
                (
                    reference.work_id,
                    reference.user_evaluation,
                    reference.visual_design_reference,
                    json.dumps(reference.code_reference, ensure_ascii=False),
                )
            ).lower()
            if query_lower and query_lower not in searchable:
                continue
            matches.append(reference)
        matches.sort(key=lambda item: item.work_id)
        return matches[:limit] if limit is not None else matches

    def save_user_preference(
        self,
        relative_path: str | Path,
        evaluation: str,
        *,
        favorite: bool | None = None,
        source: str | None = None,
        style: str | None = None,
        chart_type: str | None = None,
        application: str | None = None,
        tags: str | None = None,
    ) -> GalleryRecord:
        """Persist only fields explicitly owned by the user."""

        if not self._scanned:
            self.scan()
        key = Path(relative_path).as_posix()
        record = next((item for item in self._records if item.relative_path == key), None)
        if record is None or record.availability != "present":
            raise FileNotFoundError(f"gallery image is not indexed: {key}")
        record.user_evaluation = evaluation
        if favorite is not None:
            record.favorite = favorite
        for field_name, value in {
            "source": source,
            "style": style,
            "chart_type": chart_type,
            "application": application,
            "tags": tags,
        }.items():
            if value is not None:
                setattr(record, field_name, value)
        self.write_index(self._records)
        self._save_preferences()
        return record

    def record_agent_analysis(
        self,
        relative_path: str | Path,
        observations: Mapping[str, object],
        analyzed_by: str = "codex",
        *,
        viewed: bool = False,
        view_receipt: Mapping[str, object] | None = None,
    ) -> GalleryRecord:
        """Persist explicit visual observations without modifying the source image."""

        if not viewed:
            raise ValueError("viewed=True is required after the Agent actually opens the image")
        if not isinstance(view_receipt, Mapping) or not view_receipt:
            raise ValueError("view_receipt is required for an explicit visual review")
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
        record.visual_analysis_viewed = True
        record.visual_analysis_receipt = json.dumps(
            dict(view_receipt), ensure_ascii=False, sort_keys=True, default=str
        )
        if not record.chart_type:
            inferred_type = observations.get("chart_type", observations.get("image_type"))
            if inferred_type:
                record.chart_type = str(inferred_type)
        if not record.application:
            inferred_application = observations.get("application")
            if inferred_application is None:
                inferred_application = observations.get("applicable_scenarios")
            if isinstance(inferred_application, (list, tuple)):
                inferred_application = "; ".join(str(item) for item in inferred_application)
            if inferred_application:
                record.application = str(inferred_application)
        record.visual_analysis_notes = json.dumps(
            dict(observations), ensure_ascii=False, indent=2, sort_keys=True, default=str
        )
        self._write_visual_analysis(record)
        self.write_index(self._records)
        return record


def search_references(
    gallery_root: str | Path,
    query: str | None = None,
    *,
    chart_type: str | None = None,
    application: str | None = None,
    limit: int = 3,
) -> list[GalleryRecord]:
    """Return a small, deterministic set of relevant gallery references."""

    return GalleryIndex(gallery_root).search(
        query=query,
        chart_type=chart_type,
        application=application,
        limit=limit,
    )


def search_work_references(
    gallery_root: str | Path,
    query: str | None = None,
    *,
    limit: int = 3,
) -> list[GalleryWorkReference]:
    """Return accepted work links without treating them as image favorites."""

    return GalleryIndex(gallery_root).search_works(query=query, limit=limit)
