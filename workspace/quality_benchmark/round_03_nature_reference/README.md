# Round 03 — Nature-first reference-guided redesign

This directory contains the third controlled quality test. The input remains the unchanged repository practice table `examples/data/convergence_practice.csv`, explicitly marked as **illustrative practice data**.

The supplied journal Figure 3 was opened and analyzed for visual methods only. Its data, numerical values, uncertainty, spatial plots, and scientific claims were not reused or embedded.

## Re-render

Run from the repository root with the project environment:

```powershell
& 'C:\Users\Administrator\miniconda3\Scripts\conda.exe' run --no-capture-output -n scientific-figure-studio python tools/run_figure_task.py `
  --renderer workspace/quality_benchmark/round_03_nature_reference/plot.py `
  --brief workspace/quality_benchmark/round_03_nature_reference/figure_brief.json `
  --output-dir workspace/quality_benchmark/round_03_nature_reference `
  --data-path examples/data/convergence_practice.csv `
  --manifest-path workspace/quality_benchmark/round_03_nature_reference/data_manifest.json `
  --nature-skill-root 'C:\Users\Administrator\.codex\skills\nature-figure' `
  --gallery-root figure_gallery `
  --overwrite
```

## Delivered files

- `plot.py`, `config.py`: complete editable Python renderer and visual configuration.
- `data_manifest.json`, `figure_brief.json`: data provenance, Figure Contract, and scientific limits.
- `figure_caption.txt`: independent English caption.
- `figure.png`, `figure.svg`, `figure.pdf`: formal exports.
- `reference_design_analysis.md`, `reference_receipt.json`: observed reference methods and audit record.
- `design_lessons.md`: candidate, not user-approved, design lessons.
- `comparison_round_02_round_03.png`: required Before/After comparison.
- `comparison_round_01_round_02_round_03.png`: three-round visual overview.
- `qa_preview_single_column_89mm.png`, `qa_preview_double_column_180mm.png`: 150 dpi paper-size stress previews.
- `quality_review.md`: scientific, engineering, and visual QA record.

The figure is intended for approximately 180 mm double-column placement. The 89 mm preview is retained as a stress test and is structurally readable, but less comfortable for small annotations.
