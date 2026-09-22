"""Small, serialisable contracts for reproducible scientific figure tasks."""

from __future__ import annotations

import json
from collections.abc import Mapping
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

TASK_MODES = {"ordinary", "core-practice", "formal"}
ARCHETYPES = {
    "quantitative grid",
    "schematic-led composite",
    "image plate + quant",
    "asymmetric mixed-modality figure",
}
REQUIRED_FIELDS = (
    "task",
    "data_sources",
    "fields",
    "units",
    "claim",
    "evidence_panels",
    "archetype",
    "backend",
    "task_mode",
    "nature_references",
    "renderer",
    "review_risks",
)


def _string_tuple(value: object, field_name: str) -> tuple[str, ...]:
    if isinstance(value, str):
        values = (value,)
    elif isinstance(value, (list, tuple)):
        values = tuple(str(item) for item in value)
    else:
        raise ValueError(f"{field_name} must be a string or a list of strings")
    if any(not item.strip() for item in values):
        raise ValueError(f"{field_name} must not contain empty strings")
    return values


def _mapping(value: object, field_name: str) -> dict[str, Any]:
    if not isinstance(value, Mapping):
        raise ValueError(f"{field_name} must be an object")
    return {str(key): item for key, item in value.items()}


def _safe_reference(reference: str) -> bool:
    path = Path(reference)
    return not path.is_absolute() and ".." not in path.parts


@dataclass(frozen=True)
class FigureBrief:
    """The scientific and design inputs that precede a renderer invocation."""

    task: str
    data_sources: tuple[str, ...]
    fields: dict[str, Any]
    units: dict[str, Any]
    claim: str
    evidence_panels: tuple[dict[str, Any], ...]
    archetype: str
    backend: str
    task_mode: str
    nature_references: tuple[str, ...]
    renderer: str
    review_risks: tuple[str, ...]
    design_requirements: tuple[str, ...] = ()
    scientific_unknowns: tuple[str, ...] = ()

    def to_mapping(self) -> dict[str, Any]:
        """Return JSON-compatible data without exposing private implementation state."""

        data = asdict(self)
        data["data_sources"] = list(self.data_sources)
        data["evidence_panels"] = [dict(panel) for panel in self.evidence_panels]
        data["nature_references"] = list(self.nature_references)
        data["review_risks"] = list(self.review_risks)
        data["design_requirements"] = list(self.design_requirements)
        data["scientific_unknowns"] = list(self.scientific_unknowns)
        return data


def validate_figure_brief(value: Mapping[str, object] | FigureBrief) -> FigureBrief:
    """Validate and normalise a brief before any plotting code is executed."""

    if isinstance(value, FigureBrief):
        return value
    if not isinstance(value, Mapping):
        raise ValueError("figure brief must be an object")

    missing = [field for field in REQUIRED_FIELDS if field not in value]
    if missing:
        raise ValueError(f"figure brief missing required fields: {', '.join(missing)}")

    text_fields = ("task", "claim", "archetype", "backend", "task_mode", "renderer")
    text_values: dict[str, str] = {}
    for field_name in text_fields:
        raw = value[field_name]
        if not isinstance(raw, str) or not raw.strip():
            raise ValueError(f"{field_name} must be a non-empty string")
        text_values[field_name] = raw.strip()

    if text_values["backend"] != "Python":
        raise ValueError("backend must be Python for this project")
    if text_values["task_mode"] not in TASK_MODES:
        raise ValueError(f"task_mode must be one of: {', '.join(sorted(TASK_MODES))}")
    if text_values["archetype"] not in ARCHETYPES:
        raise ValueError(f"archetype must be one of: {', '.join(sorted(ARCHETYPES))}")

    data_sources = _string_tuple(value["data_sources"], "data_sources")
    nature_references = _string_tuple(value["nature_references"], "nature_references")
    review_risks = _string_tuple(value["review_risks"], "review_risks")
    design_requirements = _string_tuple(
        value.get("design_requirements", []), "design_requirements"
    )
    scientific_unknowns = _string_tuple(
        value.get("scientific_unknowns", []), "scientific_unknowns"
    )
    unsafe = [reference for reference in nature_references if not _safe_reference(reference)]
    if unsafe:
        raise ValueError(f"nature_references must stay inside the fixed skill tree: {unsafe}")

    raw_panels = value["evidence_panels"]
    if not isinstance(raw_panels, (list, tuple)) or not raw_panels:
        raise ValueError("evidence_panels must be a non-empty list")
    evidence_panels: list[dict[str, Any]] = []
    for index, panel in enumerate(raw_panels):
        panel_mapping = _mapping(panel, f"evidence_panels[{index}]")
        for required in ("id", "role"):
            if not str(panel_mapping.get(required, "")).strip():
                raise ValueError(f"evidence_panels[{index}] requires {required}")
        evidence_panels.append(panel_mapping)

    return FigureBrief(
        task=text_values["task"],
        data_sources=data_sources,
        fields=_mapping(value["fields"], "fields"),
        units=_mapping(value["units"], "units"),
        claim=text_values["claim"],
        evidence_panels=tuple(evidence_panels),
        archetype=text_values["archetype"],
        backend=text_values["backend"],
        task_mode=text_values["task_mode"],
        nature_references=nature_references,
        renderer=text_values["renderer"],
        review_risks=review_risks,
        design_requirements=design_requirements,
        scientific_unknowns=scientific_unknowns,
    )


def load_figure_brief(path: str | Path) -> FigureBrief:
    """Load a JSON Figure Brief and validate it before rendering."""

    brief_path = Path(path).expanduser().resolve()
    if not brief_path.is_file():
        raise FileNotFoundError(f"figure brief does not exist: {brief_path}")
    raw = json.loads(brief_path.read_text(encoding="utf-8"))
    return validate_figure_brief(raw)
