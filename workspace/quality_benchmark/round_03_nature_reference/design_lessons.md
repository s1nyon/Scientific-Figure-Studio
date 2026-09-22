# Round 03 Design Lessons

These are candidate lessons from this controlled test, not permanent project standards and not user-approved favorites.

## Reference methods adopted

- Group related evidence with alignment and whitespace rather than equal visual weight.
- Use short panel titles, stable panel letters, and direct endpoint labels.
- Reserve local arrows or outlined markers for a single evidence-bearing event.
- Keep auxiliary analysis visually subordinate to the main data region.

## Round-02 problems addressed

- Removed the long figure-level conclusion sentence that dominated the top margin.
- Reduced the visual weight of the iteration-6 callout; the +0.02 update remains visible, but the hero panel no longer carries a large orange explanatory sentence.
- Tightened the panel title and axis hierarchy so the figure can be read from data to supporting update evidence.

## Reusable implementation methods

- Reuse `figure_studio.figure_style`, `get_palette`, `running_best`, `export_figure`, and the project runner.
- Keep all adjustable geometry and visual encodings in `config.py`.
- Keep the source data and derived definitions in `data_manifest.json` and the English caption in a separate text file.
- Use one Python renderer for PNG, SVG, PDF, and paper-size previews.

## Scope limits

- The concise two-panel hierarchy is appropriate for this small convergence table, not automatically for larger benchmark collections.
- Direct endpoint labels work because there are three trajectories with separated endpoints; they may fail for crowded or crossing curves.
- A quiet incumbent marker is useful only because the running-best trace differs from current at one known point.
