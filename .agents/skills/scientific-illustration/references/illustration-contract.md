# Scientific illustration contract

## Required input

An illustration request must identify the source status, structure/data file, fields and units,
target canvas, intended reading order, and any uncertainty or missing information. A practice
fixture must use the literal status `illustrative practice data` or `illustrative example structure`.

## Structural invariants

- Directed flow and architecture edges reference declared endpoints.
- Branch labels are not inferred from arrow order; they are copied from the input structure.
- Geometric coordinates are plotted with equal x/y scale unless the Figure Brief explicitly documents
  a different mathematical coordinate transform.
- A 3-D surface uses finite, shape-matched arrays. A trajectory or spatial field must identify its
  data basis or be labeled as an example geometry.
- A mixed Figure keeps quantitative evidence and schematic explanation in distinguishable panels.
- Missing model information is reported as unknown; modules, edges, labels and results are not invented.

## Review checklist

Inspect the rendered PNG at its final insertion size. Confirm that every node and label is readable,
all arrows terminate at the intended endpoint, branch semantics are visible, geometry is not distorted,
3-D surfaces do not imply unsupported measurements, and quantitative panels retain units and provenance.
