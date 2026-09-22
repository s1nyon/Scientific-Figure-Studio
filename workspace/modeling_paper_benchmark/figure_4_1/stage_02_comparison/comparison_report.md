# Stage 2 — Figure 4-1 source comparison

## Access record

The original PDF page was rendered and opened only after the stage-1 freeze receipt existed. The target is PDF page 11, printed page 10, and the caption reads `图 4-1 问题一思路流程图`.

## Scientific structure observed in the original figure

The original image uses the following directed topology:

```text
园林矢量图数据输入
        ↓
数据预处理：提取路径
        ↓
路线离散化
        ↓
获得关键特征、量化异景程度
        ├──→ 初步路径规划 ───────────────┐
        ├──→ 构建“趣味性”评价模型 → 评价体系 ─┤
        └──────────────────────────────────→ 最优游线规划
```

The source figure therefore confirms a branch-and-merge structure that the text alone did not specify precisely.

## Stage-1 scientific differences

1. **Omitted branch:** stage 1 represented path planning as a downstream step after scoring; the original shows `初步路径规划` as a separate branch directly from the extracted-feature hub.
2. **Omitted evaluation-system node:** stage 1 merged scoring and optimization into one module; the original separates `构建“趣味性”评价模型` from `评价体系` and connects them horizontally.
3. **Incorrect output topology:** stage 1 sent one optimization branch directly to output; the original merges the initial-path branch and evaluation-system branch into `最优游线规划`.
4. **Over-explicit but not contradicted detail:** stage 1 exposed `G=(V,E)`, four named features, visibility-signature details and genetic-algorithm optimization. These are supported by surrounding text but are not literal nodes in the original image. They can remain as compact annotations in the redesign, provided they do not alter the confirmed branch topology.
5. **No unsupported model-family branch in the original image:** RF/RNN/SVM/ensemble are discussed later in the paper but are not drawn in Figure 4-1. They will not be added as parallel branches.

## Visual observations of the original

- The original uses a monochrome, vertically centered flowchart with rectangular boxes, simple black outlines and filled triangular arrowheads.
- A central vertical backbone establishes reading order; the feature hub fans out to left, center and right nodes, and the left/right paths converge into the final node.
- The branch line geometry is scientifically important: it shows that preliminary route planning and the evaluation system jointly feed optimal-route planning.
- The source has generous white space and no decorative color system, but the box labels are comparatively sparse and do not expose the four feature definitions or scoring formula.
- The original is structurally clear but visually generic; the redesign may use restrained color grouping, direct feature labels and richer but still text-supported annotations.

## Correction decision

The final figure will retain the approved horizontal semantic-spine direction for data preparation and feature extraction, then use an explicit branch-and-merge topology for the three downstream modules. It will preserve the original scientific connections while improving feature visibility, formula traceability, spacing and paper-size readability.

