# Nature-first practice Figure

This directory is a reproducible practice example, not a competition result.

## Figure Contract

- Claim: the supplied illustrative trajectories decrease over iterations, while the
  historical-best view exposes transient regressions and endpoint improvement.
- Archetype: quantitative grid with an asymmetric hero panel.
- Panel a: observed trajectories and cumulative historical-best trajectories.
- Panel b: derived percentage decrease from the first observation to the final historical best.
- Backend: Python only for design implementation, rendering, export, preview and QA.
- Review risks: no replicate runs, uncertainty estimates, statistical tests or formal
  superiority claim are present.

The fixed Nature Figure Making Skill was explicitly loaded in the Codex session before
this renderer was written. Its Figure Contract, common layout patterns and QA contract
were used to choose the panel hierarchy, restrained method palette, editable vector
exports and review checks. The Python adapter records the fixed commit and loaded
reference hashes; that record is not treated as proof of host Skill execution.

## Reproduce

From the repository root, run:

    conda run --no-capture-output -n scientific-figure-studio python tools/run_figure_task.py --renderer examples/outputs/fig_11_nature_first/plot.py --brief examples/outputs/fig_11_nature_first/figure_brief.json --output-dir examples/outputs/fig_11_nature_first --data-path examples/data/convergence_practice.csv --manifest-path examples/outputs/fig_11_nature_first/data_manifest.json --nature-skill-root $HOME/.codex/skills/nature-figure --host-skill-invocation-status explicitly_loaded_in_codex_session --review-status passed

The data is copied into this directory so the delivery bundle remains inspectable.
Edit config.py, then use a new output directory or pass --overwrite explicitly.

## Natural-language revision record

The initial rendered package was saved under snapshots/before_revision before the
requested visual revision. The final config changes the Proposed method to deep blue,
reduces grid alpha, and moves the legend to the upper right.

The reproducible Python revision commands are:

    conda run --no-capture-output -n scientific-figure-studio python tools/figure_revision.py snapshot --snapshot-dir examples/outputs/fig_11_nature_first/snapshots/before_revision examples/outputs/fig_11_nature_first/plot.py examples/outputs/fig_11_nature_first/config.py examples/outputs/fig_11_nature_first/figure.png examples/outputs/fig_11_nature_first/figure.svg examples/outputs/fig_11_nature_first/figure.pdf

    conda run --no-capture-output -n scientific-figure-studio python tools/figure_revision.py compare --before examples/outputs/fig_11_nature_first/snapshots/before_revision/figure.png --after examples/outputs/fig_11_nature_first/figure.png --output examples/outputs/fig_11_nature_first/figure_before_after.png --title "Nature-first revision: before / after" --overwrite

To recover the previous source and image set:

    conda run --no-capture-output -n scientific-figure-studio python tools/figure_revision.py restore --snapshot-dir examples/outputs/fig_11_nature_first/snapshots/before_revision --destination-dir path/to/recovery
