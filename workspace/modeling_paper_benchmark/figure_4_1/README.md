# Figure 4-1 modeling-paper benchmark

This benchmark contains a three-stage test of one paper figure: `图 4-1 问题一思路流程图` on PDF page 11 (printed page 10).

## Stage directories

- [stage_01_independent](stage_01_independent/): frozen text-only independent design, created before opening the source page image.
- [stage_02_comparison](stage_02_comparison/): source-page preview, original-figure crop, and scientific/visual comparison report.
- [stage_03_final](stage_03_final/): source-compared final figure, editable Python source/configuration, QA previews, hashes and Design Receipt.

## Final deliverables

- [figure.png](stage_03_final/figure.png)
- [figure.svg](stage_03_final/figure.svg)
- [figure.pdf](stage_03_final/figure.pdf)
- [plot.py](stage_03_final/plot.py)
- [config.py](stage_03_final/config.py)
- [structure_final.json](stage_03_final/structure_final.json)
- [data_manifest.json](stage_03_final/data_manifest.json)
- [design_receipt.json](stage_03_final/design_receipt.json)
- [qa_report.md](stage_03_final/qa_report.md)
- [before_after.png](stage_03_final/before_after.png)

## Scientific result

The text-only draft initially made the workflow linear. Opening the original source figure after the freeze confirmed a branch-and-merge topology: feature extraction feeds initial route planning, the interest model and the evaluation system; the interest model feeds the evaluation system; initial planning and evaluation then feed optimal-route planning. The final redesign preserves that topology while exposing paper-supported feature and scoring details.

## Acceptance boundary

Program status, scientific status and visual status are recorded separately in the final Design Receipt. User acceptance and personal-gallery status remain pending; this benchmark does not automatically promote the figure to an accepted work.
