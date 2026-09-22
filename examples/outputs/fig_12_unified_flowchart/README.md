# Unified-entry flowchart practice Figure

This is an illustrative example structure, not a measured workflow, model architecture,
competition result, or performance claim.

The unified entry classified this task as a non-chart scientific illustration and selected
the project scientific-illustration capability. The renderer drew only the nodes, directed
edges, branch labels, and coordinates supplied in illustration_flowchart.json. No Nature
Figure Skill was forced onto this schematic-only task.

Reproduce from the repository root:

    conda run --no-capture-output -n scientific-figure-studio python tools/run_figure_task.py --renderer templates.illustration.flowchart.plot --brief examples/data/phase3_flowchart_brief.json --output-dir examples/outputs/fig_12_unified_flowchart --data-path examples/data/illustration_flowchart.json --manifest-path templates/illustration/flowchart/data_manifest.json --review-status passed

The delivered package is also independently rerunnable with its copied input:

    conda run --no-capture-output -n scientific-figure-studio python examples/outputs/fig_12_unified_flowchart/plot.py --output-dir path/to/repro --manifest-path examples/outputs/fig_12_unified_flowchart/data_manifest.json
