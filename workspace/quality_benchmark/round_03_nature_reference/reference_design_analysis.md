# Visual design analysis of the supplied journal reference

## Source and scope

The reference was opened locally from `figure_gallery/02_algorithm/nature_optimization_fig3.png`. It is Figure 3 from Wei et al., “Deep active optimization for complex systems,” *Nature Computational Science* (2025), DOI: 10.1038/s43588-025-00858-x. This note records visible design methods only; no data, values, annotations, or scientific conclusions from the paper are reused.

## Observable structure

- The reference uses a repeated multi-column grid with ten labeled panels, but organizes those panels into three horizontal evidence bands.
- The upper band combines convergence curves, a compact ablation bar chart, and a spatial search-history view. The middle and lower bands group related benchmark families with pale full-width separators.
- Panel letters are bold and consistently placed near the upper-left of each panel. Panel titles are short and sit close to their axes.
- Axes and plot regions are aligned across rows; the separators provide grouping without enclosing every panel in heavy boxes.
- Curves, endpoint labels, compact legends, and local arrow callouts share a common visual grammar across otherwise different plot types.

## Observable visual encoding

- The background is white, with light gray axes/grid structure and restrained colored data series.
- Method identity is carried by consistent color and text labels; direct labels reduce long-distance eye travel.
- Important locations such as a global optimum or an ablation result are called out locally with a small arrow or outlined box rather than repeated in a large title.
- Some panels show translucent bands around curves. In the article context those bands are tied to repeated runs and reported variability; they are not transferable to the present single-trajectory practice data.
- The figure uses a hierarchy of line weight, panel title, panel letter, and annotation so explanatory text does not occupy the main data region.

## Methods transferred to round 03

1. Replace the round-02 long figure-level sentence with concise panel titles.
2. Keep the two evidence tasks, but give the hero trajectory more vertical space and make the lower update panel visibly subordinate.
3. Keep direct endpoint labels for the three algorithms and keep method colors/markers fixed across panels.
4. Use one quiet local running-best marker for the single Proposed divergence, while leaving the signed +0.02 update as the only warm accent annotation.
5. Use a consistent panel-letter/title/axis system and a controlled amount of whitespace.

## Methods deliberately not transferred

- No ten-panel layout: the current table has only three deterministic trajectories and would gain decoding cost without gaining evidence.
- No UMAP or spatial map: there is no search-space coordinate or candidate distribution in the input.
- No global-optimum callout: the input does not define a known global optimum or target threshold.
- No error ribbon, standard deviation, or confidence interval: there are no replicate runs or uncertainty estimates.
- No paper-specific red “this work” treatment: the current labels are practice algorithm names, not a validated paper method hierarchy.

## Design judgment

The reference is most useful here as a lesson in grouping, concise titles, direct labeling, and local emphasis. Its scientific panels are not templates to copy; the round-03 figure remains a controlled two-evidence quantitative grid whose claims are limited to the supplied illustrative practice trajectories.
