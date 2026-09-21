import subprocess
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_ROOT = PROJECT_ROOT / "examples" / "data"


@pytest.fixture
def project_root() -> Path:
    return PROJECT_ROOT


def run_script(
    script: Path, *arguments: str, cwd: Path | None = None
) -> subprocess.CompletedProcess[str]:
    """Run a project script with the active test interpreter and capture diagnostics."""

    result = subprocess.run(
        [sys.executable, str(script), *arguments],
        cwd=cwd or PROJECT_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode:
        raise AssertionError(
            f"Script failed with {result.returncode}: {script}\nSTDOUT:\n{result.stdout}\n"
            f"STDERR:\n{result.stderr}"
        )
    return result
