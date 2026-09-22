# 图库维护指南

1. 将图片复制到 `00_inbox/` 或用户选择的分类目录。
2. 运行 `python tools/update_gallery.py`，检查生成的 `gallery_index.csv` 和 `_generated/gallery_notes/`。
3. 人工查看图片后，再填写 CSV 中的 `style`、`chart_type`、`application`、`source` 和 `user_evaluation`。
4. 用户明确喜欢的图片可以复制到 `04_my_favorites/`，或在索引中填写 `favorite=true`；系统不会自动替你完成这一步。
5. 图片过时后，先备份索引再删除索引行。原图仍需由用户自行管理，图库程序不会替用户删除它。

分析笔记中的“事实”来自文件或简单像素测量，“估计”来自启发式图像统计，“未知”必须由用户或人工审查补充。

确定性扫描不会把图片标记为已完成视觉理解。实际查看图片后，可显式记录 Agent 观察：

```python
from figure_studio.gallery import GalleryIndex

gallery = GalleryIndex("figure_gallery")
gallery.record_agent_analysis(
    "00_inbox/example.png",
    {"layout": "single panel", "palette": "blue and orange", "limits": ["font unknown"]},
)
```

该调用只更新索引和 `_generated/gallery_visual_analysis/`，不会覆盖用户评价或修改原图。
