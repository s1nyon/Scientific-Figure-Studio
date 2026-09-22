# Round 02 — Nature-first structure redesign

This directory contains the second controlled quality test of Scientific Figure Studio. The input is the unchanged repository file `examples/data/convergence_practice.csv`; it is explicitly **illustrative practice data**, not a real experiment.

## Re-render the figure

Run from the repository root with the project environment:

```powershell
& 'C:\Users\Administrator\miniconda3\Scripts\conda.exe' run --no-capture-output -n scientific-figure-studio python tools/run_figure_task.py `
  --renderer workspace/quality_benchmark/round_02_structure_redesign/plot.py `
  --brief workspace/quality_benchmark/round_02_structure_redesign/figure_brief.json `
  --output-dir workspace/quality_benchmark/round_02_structure_redesign `
  --data-path examples/data/convergence_practice.csv `
  --manifest-path workspace/quality_benchmark/round_02_structure_redesign/data_manifest.json `
  --nature-skill-root 'C:\Users\Administrator\.codex\skills\nature-figure' `
  --overwrite
```

The renderer uses the fixed Nature Skill commit recorded in `nature_context.json` and `data_manifest.json`. The project environment supplies Python, Matplotlib, NumPy, pandas, Pillow, and the Scientific Figure Studio package.

## Files

- `plot.py`: complete editable renderer.
- `config.py`: editable canvas, type, colors, line widths, axes, labels, and layout settings.
- `data_manifest.json`: data provenance, transformations, objective direction, and scientific limits.
- `figure_brief.json`: Figure Contract and Nature-first design record.
- `figure.png`, `figure.svg`, `figure.pdf`: final exports.
- `comparison.png`: Round 01 and Round 02 side-by-side comparison made with `tools/figure_revision.py compare`.
- `qa_previews.py`: fixed-width paper-placement preview generator.
- `qa_preview_single_column_89mm.png`, `qa_preview_double_column_180mm.png`: actual readability stress previews at 150 dpi.
- `quality_review.md`: factual, engineering, and visual QA record.

The figure is intended for approximately 180 mm double-column placement. The 89 mm preview is retained as a stress test; it remains structurally intact but is less comfortable to read than the double-column version.
