# Stage 1 paper-text evidence

This file records the text-only evidence used before viewing the original Figure 4-1 image.

## Source boundary

- Source: user-provided paper PDF `F25107010057.pdf`.
- PDF page count from text inspection: 106 pages.
- Figure 4-1 caption is extracted from PDF page 11, printed page 10.
- Before the stage-1 freeze, no PDF page was rasterized, no page screenshot was opened, and no embedded image was extracted.

## Confirmed text evidence

### Problem statement and decomposition

- PDF page 6 (printed page 5): problem one requires route characterization, interest-indicator calculation, and optimal route selection.
- PDF page 10 (printed page 9): the paper states that garden space is abstracted as a graph; entrances/exits, intersections, turning points and scenic spots become nodes; connected paths become edges weighted by Euclidean distance.
- The same page lists path length, turning points, intersections and scenic-change degree as the path features, then describes a weighted linear interest score, genetic-algorithm weight optimization and route optimization.

### Data processing and path abstraction

- PDF page 14 (printed page 13): input layers are garden paths, rockeries, water, plants and buildings; the processing chain includes layer separation, geometry extraction, coordinate processing, parallel-line matching, centerline/path-point generation, polyline resampling and output formatting.
- PDF page 14: the path is represented by a graph and later used for route planning.

### Feature calculations

- PDF page 15 (printed page 14): length is the sum of Euclidean distances between adjacent path points; turning points are detected from angle changes; intersections are nodes with degree at least 3.
- PDF pages 22–23 (printed pages 21–22): scenic change uses 1 m resampling, a four-element binary visibility signature ordered as water, stone, plants and building, and L1/Manhattan differences between adjacent signatures. The stated visibility radius is 15 m.

### Scoring and optimization

- PDF pages 23–24 (printed pages 22–23): the interest score is a weighted linear combination of normalized features; Min–Max normalization is described and repetition-related features are reverse-processed.
- PDF page 24 (printed page 23): genetic algorithm weight optimization is introduced.
- PDF pages 26–29 (printed pages 25–28): random forest, recurrent neural network, SVM and an ensemble are discussed as additional optimization models; the text does not, by itself, specify whether all of these branches appear in Figure 4-1.
- PDF page 29 (printed page 28): optimized scores and route features are used to select the optimal route; the final output is an optimal route and its interest score.

## Not determined before source-image comparison

1. Whether Figure 4-1 expands RF/RNN/SVM/ensemble into parallel branches.
2. Whether Figure 4-1 shows a feedback arrow from route selection back to path generation.
3. Exact original wording, node count, module geometry, connector routing, and visual hierarchy.

