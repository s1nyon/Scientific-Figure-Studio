# Final visual QA report

## Checked artifacts

- `figure.png` — opened at the generated 180 mm canvas preview.
- `qa_single_column_89mm.png` — opened at approximately single-column insertion width.
- `qa_double_column_180mm.png` — opened at approximately double-column insertion width.
- `before_after.png` — opened for stage-1 versus stage-3 comparison.
- `figure.svg` — parsed successfully with 31 editable text nodes.
- `figure.pdf` — parsed successfully as a one-page non-empty PDF.

## Findings and actions

- Bottom output module overlapped the structural footer in the first final candidate — moved the output module upward in `structure_final.json`, then rerendered all formats.
- Source-page branch topology — preserved explicit feature-to-route/evaluation branches and the two downstream merge arrows.
- Typography — replaced unsupported Unicode subscript glyphs with editable ASCII `w_i`/`f_i` labels; no missing-glyph warning occurred in the final render.
- Paper-size readability — body labels remain distinguishable at 89 mm; the footer is secondary and intentionally quieter.
- Arrow routing — no ambiguous crossings were observed; the only long diagonal connectors are the explicit feature-hub branches.

## Still user-dependent

The final figure is programmatically, scientifically and visually reviewed in this workspace. User acceptance and any decision to save it as a personal reference remain pending and are not inferred from this run.
