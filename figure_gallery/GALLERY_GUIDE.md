# 图库维护指南

## 1. 添加和扫描

把图片复制到 `00_inbox/` 或用户选择的分类目录，然后运行：

```powershell
python tools/update_gallery.py
```

`update_gallery.py` 没有 argparse 参数；它会扫描项目图库并更新索引/生成档案，所以不要用 `--help` 代替阅读源码接口。原图不会被修改、移动或删除。

## 2. 分开记录五类信息

- 扫描器事实：路径、尺寸、模式、哈希、像素统计、变化和重复状态；
- Agent 实际视觉分析：打开图片后观察到的布局、配色关系、字体层级、标注、信息层级和留白；
- 用户评价：由用户明确填写的认可范围、偏好和原话；
- 科学内容：数据来源、变量意义、单位和结论；不能从像素确定的内容保持未知；
- 代码实现：入口、配置、输入、版本、哈希和复现 manifest。

像素统计不能变成用户偏好，Agent 观察不能变成科学结论，期刊来源不能变成授权证明。

## 3. 记录实际视觉分析

实际打开图片后，使用当前 `GalleryIndex` 接口：

```python
from figure_studio.gallery import GalleryIndex

gallery = GalleryIndex("figure_gallery")
gallery.scan()
record = gallery.record_agent_analysis(
    "00_inbox/example.png",
    {
        "chart_type": "line chart",
        "layout": "single panel",
        "palette": "blue and orange",
        "labeling": "direct endpoint labels",
        "applicable_scenarios": ["small algorithm comparison"],
        "limitations": ["font name unknown", "data source unknown"],
    },
    analyzed_by="codex",
    viewed=True,
    view_receipt={
        "viewer": "view_image",
        "path": "figure_gallery/00_inbox/example.png",
        "dimensions_px": "1242x1200",
    },
)
print(record.relative_path, record.visual_analysis_status)
```

`viewed=True` 和非空 `view_receipt` 是当前 API 的强制要求；调用只更新索引与 `_generated/gallery_visual_analysis/`，不覆盖用户评价或原图。若 Agent 没有图片查看能力，保留 `not_analyzed`，不要伪造 receipt。

等价 CLI 需要两个 JSON object 文件：

```powershell
python tools/record_gallery_analysis.py `
  --gallery-root figure_gallery `
  --image 00_inbox/example.png `
  --observations path/to/observations.json `
  --view-receipt path/to/view_receipt.json `
  --analyzed-by codex
```

## 4. 检索相关参考

```python
from figure_studio.gallery import GalleryIndex, search_references

gallery = GalleryIndex("figure_gallery")
gallery.scan()
matches = search_references(
    "figure_gallery",
    query="convergence",
    chart_type="algorithm convergence curve",
    application="algorithm comparison and optimization trajectory",
    limit=3,
)
for record in matches:
    print(record.relative_path, record.style, record.visual_analysis_status)
```

用户明确指定的图片必须先实际打开。检索按用户认可、图表类型、应用场景和视觉分析状态提供少量参考；不匹配时不强行套用布局或颜色。

## 5. favorites 和认可作品

用户明确喜欢的图片才可以记录 `favorite=true` 或由用户自行复制到 `04_my_favorites`。认可作品通过 `tools/manage_figure_work.py accept` 提升，必须带用户 note；普通 Agent 分析不会完成这一步。

Round 04 Design A 的用户认可范围仅覆盖其算法收敛图视觉方向和未来相似任务的参考价值。它使用 `illustrative practice data`，不是顶刊认证、科学结果验证、普遍算法性能结论、全局审美偏好或所有图的模板。新任务仍需按 Nature-first Figure Brief、数据和 QA 风险重新设计；不可复制其固定 x 轴、标注或面板结构。

## 6. 失效索引和外部来源

确认图片路径确实失效后，只删除 `gallery_index.csv` 对应记录或 `_generated/` 中的笔记；不要删除原图。第三方外部图片的来源、授权和公开提交权限必须单独记录；本地收藏不表示可以公开再分发。
