# P1 independent simple reproduction

This package contains only the self-written renderer, its local runtime helpers,
configuration, and explicitly marked illustrative practice data. It does not import
Scientific Figure Studio, use `PYTHONPATH`, read `SCIENTIFIC_FIGURE_STUDIO_ROOT`, or
load the upstream Nature Skill at runtime.

Run with Python 3.11 and the dependencies recorded in `reproduction_manifest.json`:

    python plot.py --output-dir ./rerender
