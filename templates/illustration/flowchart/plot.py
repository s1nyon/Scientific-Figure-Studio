"""Render an explicit illustrative algorithm flowchart."""

import argparse
import json
import os
import sys
from pathlib import Path

import matplotlib.pyplot as plt

_configured_root = os.environ.get("SCIENTIFIC_FIGURE_STUDIO_ROOT")
PROJECT_ROOT = (
    Path(_configured_root)
    if _configured_root
    else next(
        parent
        for parent in [Path(__file__).resolve(), *Path(__file__).resolve().parents]
        if (parent / "figure_studio").is_dir()
    )
)
sys.path.insert(0, str(PROJECT_ROOT))

try:
    from .config import CONFIG
except ImportError:
    from config import CONFIG

from figure_studio.export import export_figure  # noqa: E402
from figure_studio.illustrations import draw_flowchart  # noqa: E402
from figure_studio.manifest import (  # noqa: E402
    build_data_provenance,
    load_manifest,
    provenance_data_label,
)
from figure_studio.palettes import get_palette  # noqa: E402
from figure_studio.style import figure_style  # noqa: E402


def load_data(path: str | Path) -> dict[str, object]:
    """Read the explicit node and directed-edge structure from JSON."""

    data_path = Path(path)
    if not data_path.is_file():
        raise FileNotFoundError(data_path)
    data = json.loads(data_path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or not isinstance(data.get("nodes"), dict):
        raise ValueError("flowchart JSON requires a nodes mapping")
    if not isinstance(data.get("edges"), list):
        raise ValueError("flowchart JSON requires an edges list")
    return data


def build_figure(data: dict[str, object], config: dict[str, object]) -> plt.Figure:
    """Draw only the supplied flowchart nodes and directed connections."""

    palette = get_palette(str(config["palette_name"]))
    with figure_style(str(config["style_name"]), canvas="wide"):
        with plt.rc_context({"font.size": float(config["font_size"])}):
            figure, axis = plt.subplots(
                figsize=(float(config["figure_width"]), float(config["figure_height"])),
                layout="constrained",
            )
            draw_flowchart(axis, data["nodes"], data["edges"], config)
            axis.set_title("Illustrative algorithm flow", loc="left", pad=12)
            evidence = str(
                data.get(
                    "evidence_note",
                    "Illustrative example structure; not a measured algorithm result.",
                )
            )
            data_label = provenance_data_label(str(config.get("data_status", "")))
            figure.text(
                0.01,
                0.005,
                " · ".join(item for item in (evidence, data_label) if item),
                color=palette.muted,
                fontsize=max(6.5, float(config["font_size"]) - 1.5),
            )
            return figure


def main(
    output_dir: str | Path | None = None,
    data_path: str | Path | None = None,
    manifest_path: str | Path | None = None,
    overwrite: bool = False,
):
    """Generate flowchart artifacts and return their paths."""

    manifest_file = Path(manifest_path) if manifest_path else Path(__file__).with_name(
        "data_manifest.json"
    )
    if data_path is not None:
        raw_manifest = json.loads(manifest_file.read_text(encoding="utf-8"))
        if not isinstance(raw_manifest, dict):
            raise ValueError("manifest JSON must contain an object")
        raw_manifest["data_file"] = str(data_path)
        manifest = load_manifest(raw_manifest, base_dir=PROJECT_ROOT)
    else:
        manifest = load_manifest(
            manifest_file,
            base_dir=manifest_file.parent if manifest_path else PROJECT_ROOT,
        )
    source = manifest.data_path
    destination = (
        Path(output_dir)
        if output_dir
        else PROJECT_ROOT / "examples" / "outputs" / str(CONFIG["figure_id"])
    )
    destination.mkdir(parents=True, exist_ok=True)
    runtime_config = {**CONFIG, "data_status": manifest.data_status}
    data = load_data(source)
    figure = build_figure(data, runtime_config)
    try:
        with figure_style(str(CONFIG["style_name"]), canvas="wide"):
            return export_figure(
                figure,
                destination / "figure",
                formats=tuple(CONFIG["output_formats"]),
                dpi=int(CONFIG["dpi"]),
                overwrite=overwrite,
                provenance=build_data_provenance(
                    manifest,
                    {
                        "structure_status": manifest.raw.get(
                            "structure_status", "unknown"
                        ),
                        "evidence_note": data.get("evidence_note", "unknown"),
                        "edge_semantics": "Directed source-to-target edges from input JSON.",
                    },
                ),
            )
    finally:
        plt.close(figure)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=None)
    parser.add_argument("--data-path", type=Path, default=None)
    parser.add_argument("--manifest-path", type=Path, default=None)
    parser.add_argument("--overwrite", action="store_true")
    return parser.parse_args()


if __name__ == "__main__":
    arguments = _parse_args()
    main(
        output_dir=arguments.output_dir,
        data_path=arguments.data_path,
        manifest_path=arguments.manifest_path,
        overwrite=arguments.overwrite,
    )
