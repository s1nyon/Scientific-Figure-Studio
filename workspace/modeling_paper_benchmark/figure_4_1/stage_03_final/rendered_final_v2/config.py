"""Editable visual configuration for the stage-1 paper-derived workflow."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parent
FIGURE_BASENAME = "figure"
FIGSIZE_IN = (180 / 25.4, 98 / 25.4)
DPI = 600

FONT_FAMILY = "sans-serif"
FONT_CANDIDATES = ["Microsoft YaHei", "SimHei", "Arial", "DejaVu Sans", "Liberation Sans"]

COLORS = {
    "paper": "#FFFFFF",
    "ink": "#23384A",
    "muted": "#687A86",
    "line": "#527384",
    "line_soft": "#B6C7CE",
    "source_fill": "#E8F3F5",
    "path_fill": "#EEF2FB",
    "graph_fill": "#F1EFFB",
    "feature_fill": "#EAF5F1",
    "score_fill": "#FFF3E5",
    "optim_fill": "#F9EDEF",
    "output_fill": "#EAF5EA",
    "source_accent": "#3A93A0",
    "path_accent": "#647CC3",
    "graph_accent": "#8065B0",
    "feature_accent": "#3C9278",
    "score_accent": "#C17B39",
    "optim_accent": "#B45B75",
    "output_accent": "#4C9460",
    "footer_fill": "#F5F7F8",
    "footer_edge": "#CBD6DB",
}

ROLE_STYLE = {
    "formal paper input": (COLORS["source_fill"], COLORS["source_accent"]),
    "pre-processing": (COLORS["path_fill"], COLORS["path_accent"]),
    "graph abstraction": (COLORS["graph_fill"], COLORS["graph_accent"]),
    "feature extraction": (COLORS["feature_fill"], COLORS["feature_accent"]),
    "weighted linear model": (COLORS["score_fill"], COLORS["score_accent"]),
    "optimization and planning": (COLORS["optim_fill"], COLORS["optim_accent"]),
    "paper-reported output": (COLORS["output_fill"], COLORS["output_accent"]),
}

TITLE = "问题一｜游赏趣味性模型流程"
SUBTITLE = "图 4-1 重构版 · 路径特征 → 分支评价 → 最优游线"
FOOTER = "结构核对：初步路径规划与评价体系共同汇入最优游线规划"

TITLE_SIZE = 13.2
SUBTITLE_SIZE = 6.8
MODULE_TITLE_SIZE = 8.1
MODULE_BODY_SIZE = 6.2
MODULE_NOTE_SIZE = 5.3
FOOTER_SIZE = 5.5
ARROW_SIZE = 1.05
ARROW_MUTATION = 9
NODE_LINE_WIDTH = 0.9
