# 个人科研绘图图库

请把新图片放入 `00_inbox/`，或按用户明确选择的类别放入 `01_minimal`、`02_algorithm`、`03_visual_narrative`、`04_my_favorites` 和 `05_my_work`。图库原图是用户资产；扫描、哈希、缩略图、视觉分析和设计笔记必须写入独立的 `_generated/` 或索引文件。

## 扫描和增量索引

```powershell
python tools/update_gallery.py
```

扫描器记录相对路径、尺寸、模式、修改时间、SHA-256 和有限像素统计，识别新增、变化和重复图片。内容变化会把旧记录保存在 `_generated/gallery_history/` 并标记新的分析状态为 `stale`；重复文件只做哈希标记，不删除任一原图。空图库是合法状态。

扫描得到的是文件事实，不是完整视觉理解，也不自动推断用户喜好、科研结论、精确字体名称或第三方授权。

## Agent 视觉分析

能够查看图片的 Agent 必须先实际打开原图，再调用 `record_agent_analysis()`，并提供 `viewed=True` 与非空 `view_receipt`：

```python
from figure_studio.gallery import GalleryIndex

gallery = GalleryIndex("figure_gallery")
gallery.record_agent_analysis(
    "00_inbox/example.png",
    {
        "chart_type": "line chart",
        "layout": "single panel",
        "palette": "blue and orange",
        "limitations": ["font name unknown", "data source unknown"],
    },
    viewed=True,
    view_receipt={
        "viewer": "view_image",
        "path": "figure_gallery/00_inbox/example.png",
        "dimensions_px": "1242x1200",
    },
)
```

观察只能写图表类型、构图、颜色关系、字体层级、坐标轴、标记、标注、信息层级、留白和可借鉴方法等实际可见内容。用户评价、科学内容、来源、授权和源码关联分别维护，不能互相覆盖。详细接口和 CLI 见 [`GALLERY_GUIDE.md`](GALLERY_GUIDE.md)。

## 检索和使用边界

绘图任务可以使用 `search_references()` 按用户明确认可、图表类型、应用场景和数据结构检索少量相关案例：

```python
from figure_studio.gallery import search_references

matches = search_references(
    "figure_gallery",
    query="convergence",
    chart_type="algorithm convergence curve",
    application="algorithm comparison and optimization trajectory",
    limit=3,
)
```

参考图只提供已经实际查看的设计方法；不复制其数据、结论、私人内容或默认布局。图库为空或不匹配时，继续由 Nature-first 工作流自主设计。用户指定的图片必须先打开。

## 用户认可和作品关联

图片不会因为扫描完成或 Agent 觉得好看就自动进入 favorites。只有用户明确评价后，才可记录 favorite 或把候选作品提升为 accepted。已认可作品的代码、输入、输出、配置和复现 manifest 保持关联，但不自动成为模板。

Round 04 Design A 是用户明确认可的算法收敛图个人参考案例，使用 `illustrative practice data`，不是顶刊质量认证、科学结果验证、全局审美偏好或所有科研图的默认模板。完整的适用场景和复用限制见 [`05_my_work/round_04_design_a_accepted/accepted_reference_case.md`](05_my_work/round_04_design_a_accepted/accepted_reference_case.md)。

## 外部图片保护

用户收藏的第三方论文图片只能依据来源与授权使用。图片在本地存在不代表拥有公开再分发权限；不要自动提交到公开 GitHub 仓库。不要删除、覆盖、移动或重命名原图；清理失效索引时只处理 `gallery_index.csv` 或 `_generated/` 中的记录。
