# Round 04 independent design options

This document is frozen before any historical Round 01–03 image or source file is used for layout selection. The options use only the raw convergence table, its mathematical definitions, the fixed Nature Figure Skill, and the supplied journal reference's observable design methods.

## Shared Figure Contract

Core claim: within the displayed illustrative trajectories, all three algorithms end below their displayed starting values; Proposed ends at the lowest displayed objective, while the only positive adjacent update is a small local event at iteration 6.

Objective direction: minimize; lower values are better.

Evidence available from the input: current objective trajectories, direction-aware cumulative minimum, adjacent signed changes, starting values, ending values, and displayed-window net changes. The table has no repeated runs, uncertainty estimates, stopping threshold, or known global optimum.

Reference methods considered transferable: concise panel titles, stable panel letters, direct labels, aligned plot regions, restrained local callouts, and a white canvas with light structural axes. Reference methods rejected: ten-panel benchmark page, UMAP, global-optimum boxes, error bands, and paper-specific method emphasis.

## Design A — minimal trajectory figure

### Structure

One full-width quantitative panel. It shows only the raw current objective trajectories for Proposed, Adaptive, and Baseline. Direct terminal labels replace a legend. A quiet open marker and short label identify the single Proposed current-versus-running-best divergence; the raw trajectory itself shows the +0.02 local increase.

### Scientific purpose

Make the displayed paths and terminal ordering immediately legible. The figure intentionally leaves stepwise changes and endpoint arithmetic to the independent caption rather than adding a second evidence panel.

### Strengths

- Lowest decoding cost and largest data region.
- Most suitable if the manuscript needs a single descriptive convergence panel.
- Does not imply a speed or stability ranking.

### Limitations

- The exact signed update sequence is not shown as a separate visual object.
- The displayed-window net changes must be read from the endpoints or caption.

## Design B — asymmetric path plus endpoint summary

### Structure

An asymmetric horizontal composition: a large left trajectory panel and a narrow right endpoint-summary panel. The right panel uses one row per algorithm with an open starting point, a filled ending point, a connecting segment, and a signed displayed-window net change. It does not encode speed or uncertainty.

### Scientific purpose

Separate path shape from endpoint arithmetic. The left panel answers “what path is observed?” and the right panel answers “what are the displayed start, end, and net changes?” without using a heatmap or a second time-series plot.

### Strengths

- Makes the difference between path and endpoint summary explicit.
- Uses an asymmetric hero layout and direct labels compatible with high-density algorithm papers.
- Preserves a unique second evidence task without adding unsupported statistics.

### Limitations

- The endpoint summary repeats some values already visible in the trajectory.
- The right panel is less useful than Design A if the paper only needs path shape.

## Selection rule after draft review

Both candidates must remain scientifically accurate, visibly distinct, and readable at 180 mm before user selection. No candidate will be marked as preferred or moved to a favorites collection before the user chooses.
