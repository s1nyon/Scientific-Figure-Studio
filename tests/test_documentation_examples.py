import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCUMENTS = (
    ROOT / "README.md",
    ROOT / "docs" / "QUICK_START.md",
    ROOT / "docs" / "SKILLS_USAGE.md",
    ROOT / "docs" / "GALLERY_WORKFLOW.md",
    ROOT / "docs" / "FIGURE_EDITING.md",
    ROOT / "docs" / "UPSTREAM_NATURE_FIGURE.md",
    ROOT / "figure_gallery" / "README.md",
    ROOT / "figure_gallery" / "GALLERY_GUIDE.md",
)


def test_documented_python_and_powershell_scripts_exist():
    paths: set[str] = set()
    for document in DOCUMENTS:
        text = document.read_text(encoding="utf-8")
        paths.update(re.findall(r"(?:python\s+|python\.exe\s+)([\w./-]+\.py)", text))
        paths.update(re.findall(r"-File\s+([\w./-]+\.ps1)", text))
    assert paths
    missing = [path for path in paths if not (ROOT / path).is_file()]
    assert not missing, f"documented scripts do not exist: {missing}"


def test_phase_two_docs_use_current_fields_and_paths():
    all_text = "\n".join(document.read_text(encoding="utf-8") for document in DOCUMENTS)
    assert "style_tags" not in all_text
    assert "scientific-illustration" in all_text
    assert "install_nature_figure.py" in all_text
    assert "verify_nature_figure.py" in all_text
    assert "templates/illustration/flowchart/plot.py" in all_text
    assert "templates/illustration/architecture/plot.py" in all_text
    assert "templates/illustration/composite/plot.py" in all_text
