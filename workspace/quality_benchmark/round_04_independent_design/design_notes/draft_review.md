# Round 04 independent draft review

Status: two candidate designs rendered; user selection is required before any final polishing.

## Shared scientific contract

- Input: `examples/data/convergence_practice.csv`.
- Objective direction: minimize; lower objective is better.
- Three algorithms, ten observations per algorithm, one displayed trajectory per algorithm.
- No replicates, uncertainty estimates, seeds, threshold, stopping rule, or statistical test.
- The only positive adjacent change is `Proposed`, iteration 5 to 6, `+0.02`.
- Claims are limited to the displayed current-objective paths, displayed endpoints, and displayed-window start-to-end changes.

## Design A review

One full-width hero panel. Current objective is shown as the solid path; direct endpoint labels carry the terminal values. The historical best is not drawn as a second curve; it is marked only at the single Proposed divergence. The figure remains legible in the 89 mm preview and is most comfortable at 180 mm.

## Design B review

An asymmetric two-panel composition. Panel a shows the same path evidence; panel b separates the first-to-last arithmetic from the path shape using open starts, filled ends, and signed `Delta = last - first`. The 180 mm preview is the intended placement. The 89 mm preview remains readable but is visibly denser than Design A.

## Review actions completed

- Opened both final PNGs after the last render.
- Generated and opened 89 mm and 180 mm previews for both designs.
- Repaired endpoint-label clipping/overlap and shortened the Design B support title.
- Confirmed no cropping, legend obstruction, or unsupported uncertainty encoding in the reviewed renders.
- No Round 01–03 image, plot source, configuration, layout, or receipt was read as a design input before these drafts were created.

## Pending decision

Do not create a final selected figure, historical before/after comparison, or personal-favorites entry until the user chooses Design A or Design B.
