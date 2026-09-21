"""System font detection and Matplotlib fallback configuration."""

from dataclasses import dataclass

import matplotlib as mpl
from matplotlib import font_manager


@dataclass(frozen=True)
class FontReport:
    """The actual font choices and any unresolved candidates."""

    english_family: str
    chinese_family: str
    math_family: str
    available: tuple[str, ...]
    missing: tuple[str, ...]
    warnings: tuple[str, ...]


_ENGLISH_CANDIDATES = ("Arial", "Calibri", "Aptos", "DejaVu Sans", "Liberation Sans")
_CHINESE_CANDIDATES = (
    "Noto Sans SC",
    "Microsoft YaHei",
    "SimHei",
    "Source Han Sans SC",
    "DejaVu Sans",
)
_MATH_CANDIDATES = ("DejaVu Sans", "STIX Two Math", "Cambria Math", "DejaVu Serif")


def _find_candidate(candidates: tuple[str, ...]) -> tuple[str, list[str]]:
    missing: list[str] = []
    for candidate in candidates:
        try:
            font_manager.findfont(candidate, fallback_to_default=False)
        except (ValueError, RuntimeError):
            missing.append(candidate)
            continue
        return candidate, missing
    return "DejaVu Sans", missing


def resolve_fonts() -> FontReport:
    """Resolve actual installed fonts without assuming a machine-specific font."""

    english, english_missing = _find_candidate(_ENGLISH_CANDIDATES)
    chinese, chinese_missing = _find_candidate(_CHINESE_CANDIDATES)
    math, math_missing = _find_candidate(_MATH_CANDIDATES)
    missing = tuple(english_missing + chinese_missing + math_missing)
    warnings: list[str] = []
    if chinese == "DejaVu Sans":
        warnings.append("未检测到优先中文无衬线字体，中文标签可能需要人工查看。")
    available = tuple(dict.fromkeys((english, chinese, math)))
    return FontReport(
        english_family=english,
        chinese_family=chinese,
        math_family=math,
        available=available,
        missing=missing,
        warnings=tuple(warnings),
    )


def configure_fonts(report: FontReport | None = None) -> FontReport:
    """Apply a resolved font report to the current Matplotlib context."""

    report = report or resolve_fonts()
    mpl.rcParams.update(
        {
            "font.family": "sans-serif",
            "font.sans-serif": [
                report.english_family,
                report.chinese_family,
                "DejaVu Sans",
                "sans-serif",
            ],
            "mathtext.fontset": "stixsans",
            "axes.unicode_minus": False,
        }
    )
    return report
