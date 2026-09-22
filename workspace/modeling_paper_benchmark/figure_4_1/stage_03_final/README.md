# Stage 3 — Final source-compared workflow

This directory contains the final Python-generated redesign of paper Figure 4-1. It keeps the original branch-and-merge logic while making the paper-supported path features, score model and provenance easier to inspect.

## Run

```powershell
& 'C:/Users/Administrator/miniconda3/envs/scientific-figure-studio/python.exe' plot.py
```

For a reproducible package run from the repository root:

```powershell
& 'C:/Users/Administrator/miniconda3/envs/scientific-figure-studio/python.exe' tools/run_figure_task.py `
  --renderer 'workspace/modeling_paper_benchmark/figure_4_1/stage_03_final/plot.py' `
  --brief 'workspace/modeling_paper_benchmark/figure_4_1/stage_03_final/figure_brief.json' `
  --output-dir 'workspace/modeling_paper_benchmark/figure_4_1/stage_03_final/rendered_final_v2' `
  --data-path 'workspace/modeling_paper_benchmark/figure_4_1/stage_03_final/structure_final.json' `
  --manifest-path 'workspace/modeling_paper_benchmark/figure_4_1/stage_03_final/data_manifest.json' `
  --nature-skill-root 'C:/Users/Administrator/.codex/skills/nature-figure' `
  --host-skill-invocation-status explicitly_loaded_in_codex_session `
  --version-status candidate `
  --review-status not_reviewed `
  --dependency 'matplotlib==3.10.6' `
  --dependency 'numpy==2.2.6' `
  --dependency 'PyMuPDF==1.28.2' `
  --dependency 'figure_studio.illustrations' `
  --overwrite
```

`structure_final.json` is the source of truth for nodes and directed edges. The output is an `illustrative example structure` of the paper workflow, not a numerical result panel.

## Comparison-based changes

- Restored the original feature-hub split into initial route planning, interest-model construction and evaluation system.
- Restored the interest-model → evaluation-system connection.
- Restored the merge of initial path planning and evaluation system into optimal route planning.
- Kept text-supported feature and formula annotations; excluded later RF/RNN/SVM/ensemble branches because they are not drawn in Figure 4-1.
