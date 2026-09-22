# Stage 1 — Independent text-only design

This directory is the frozen first-stage candidate for paper Figure 4-1. It was designed from extracted paper text before opening the original PDF page image.

## Run

```powershell
& 'C:/Users/Administrator/miniconda3/envs/scientific-figure-studio/python.exe' tools/run_figure_task.py `
  --renderer 'workspace/modeling_paper_benchmark/figure_4_1/stage_01_independent/plot.py' `
  --brief 'workspace/modeling_paper_benchmark/figure_4_1/stage_01_independent/figure_brief.json' `
  --output-dir 'workspace/modeling_paper_benchmark/figure_4_1/stage_01_independent/rendered_reproduction' `
  --data-path 'workspace/modeling_paper_benchmark/figure_4_1/stage_01_independent/structure_stage1.json' `
  --manifest-path 'workspace/modeling_paper_benchmark/figure_4_1/stage_01_independent/data_manifest.json' `
  --nature-skill-root 'C:/Users/Administrator/.codex/skills/nature-figure' `
  --host-skill-invocation-status explicitly_loaded_in_codex_session `
  --version-status workspace `
  --review-status not_reviewed `
  --dependency 'matplotlib==3.10.6' `
  --dependency 'numpy==2.2.6' `
  --dependency 'figure_studio.illustrations'
```

The renderer exports `figure.png`, `figure.svg` and `figure.pdf` in this directory. It loads `config.py` and `structure_stage1.json`, validates all declared directed edges, and does not read the source PDF.

## Scientific status

This is an `illustrative example structure` of the paper-derived workflow, not a numerical result figure. The modules and labels are supported by the text evidence listed in `paper_text_evidence.md`; unresolved branches and feedback geometry are explicitly recorded as unknown until stage 2.

## Stage boundary

The stage-1 freeze receipt must be written before the original Figure 4-1 page is rasterized or viewed. Do not replace these files with the final version; stage 3 owns the corrected renderer.
