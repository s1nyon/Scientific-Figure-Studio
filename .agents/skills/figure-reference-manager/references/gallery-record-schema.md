# 图库记录字段

`gallery_index.csv` 当前实现的主要字段包括：

- `relative_path`：相对图库根目录的原图路径。
- `sha256`：用于重复和变更检测的内容哈希。
- `style`、`chart_type`、`application`、`tags`：程序建议或用户补充的标签。
- `favorite`、`user_evaluation`、`source`：用户维护的偏好、来源和说明字段。
- `dominant_color`、`mean_luminance`、`whitespace_estimate`：程序估计值，不能当作精确设计参数。
- `analysis_date`、`is_duplicate` 和文件尺寸/模式字段：增量检测和基础档案信息。

对应 Markdown 档案按 SHA-256 写入 `_generated/gallery_notes/`；档案还应记录来源、原始图号、分析日期、版权/数据说明和“不适合直接模仿”的部分。
