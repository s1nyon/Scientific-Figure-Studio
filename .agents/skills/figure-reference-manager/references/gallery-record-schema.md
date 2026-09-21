# 图库记录字段

`gallery_index.csv` 每条记录至少包含：

- `relative_path`：相对图库根目录的原图路径。
- `sha256`：用于重复和变更检测的内容哈希。
- `category`：inbox、minimal、algorithm、visual_narrative、favorites 或 my_work。
- `style_tags`、`figure_type`、`use_cases`：可观察或用户提供的标签。
- `analysis_status`、`notes_path`、`user_rating`：档案状态、生成笔记和用户评价。
- `dominant_colors`、`luminance_mean`、`whitespace_fraction`：程序估计值，不能当作精确设计参数。

Markdown 档案还应记录来源、原始图号、分析日期、版权/数据说明和“不适合直接模仿”的部分。
