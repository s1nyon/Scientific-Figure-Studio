# 个人科研绘图图库工作流

图库是 Nature-first 绘图任务的可选参考来源，不是统一模板库。参考案例必须与当前科学内容、数据结构、图形类型和信息目标匹配；不匹配时继续自主设计。

## 添加、扫描和保护

把新图放入 `figure_gallery/00_inbox/` 或用户指定的分类目录，然后运行：

```powershell
python tools/update_gallery.py
```

扫描器使用相对路径和 SHA-256 识别新增、变化和重复图片，把确定性设计笔记写入 `figure_gallery/_generated/gallery_notes/`，把历史和视觉分析写入其他 `_generated/` 子目录。新图默认 `visual_analysis_status=not_analyzed`，内容变化标记为 `stale`；空图库仍然合法。扫描不会修改、移动、删除或上传原图。

## 视觉分析的证据门槛

文件存在、哈希变化和像素统计只能证明文件事实。Agent 只有在实际打开图片后，才能记录视觉观察：

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

`record_agent_analysis()` 写入 `_generated/gallery_visual_analysis/` 和索引，不覆盖用户评价或原图。没有查看能力时保持 `not_analyzed`。当前 API 的完整参数和 CLI 见 [`figure_gallery/GALLERY_GUIDE.md`](../figure_gallery/GALLERY_GUIDE.md)。

## 设计参考检索

```python
from figure_studio.gallery import search_references

matches = search_references(
    "figure_gallery",
    query="convergence",
    chart_type="line chart",
    application="algorithm comparison",
    limit=3,
)
```

`search_references()` 返回少量确定性记录，优先考虑用户明确认可、图表类型、应用场景和已有视觉分析状态。参考图只贡献可观察的布局、层级、颜色关系、标注、留白或代码实现方法；不复制数据、科学结论、私人内容或默认布局。用户指定图片必须先实际打开。

## 五类信息不可互相覆盖

1. 文件扫描事实；
2. Agent 实际打开图片后的视觉观察；
3. 用户明确提供的评价和认可范围；
4. 作品的科学内容、数据来源、单位和结论；
5. 作品的 Python 入口、配置、输入、版本和复现 manifest。

不能把 AI 观察写成用户偏好，不能因图片来自 Nature 就标为 favorite，不能从像素推断科学结论或精确字体，不能因图片在本地就假定拥有第三方公开分发权限。

## Round 04 Design A

`figure_gallery/05_my_work/round_04_design_a_accepted/` 是用户明确认可的算法收敛图个人参考案例。它的输入标记为 `illustrative practice data`；用户认可的是该范围内的视觉方向和未来相似任务的参考价值。它不是顶刊质量认证、科学结果验证、算法普遍优势、全局审美偏好或所有科研图的默认模板。完整技术观察、适用场景和复用限制见 [`accepted_reference_case.md`](../figure_gallery/05_my_work/round_04_design_a_accepted/accepted_reference_case.md)。不要修改其原图、源码、评价或 provenance。

## 认可作品

正式任务先生成 workspace/candidate：

```powershell
python tools/run_figure_task.py `
  --renderer path/to/plot.py `
  --brief path/to/figure_brief.json `
  --output-dir path/to/candidate `
  --version-status candidate
```

只有用户明确提供评价后才运行：

```powershell
python tools/manage_figure_work.py accept `
  --candidate-dir path/to/candidate `
  --accepted-dir path/to/accepted `
  --user-note "用户明确认可这版设计"
```

认可作品可通过 `tools/manage_figure_work.py clone` 派生新 workspace；普通渲染、`--overwrite` 和快照恢复不能改写 accepted 目录。新图片不会自动进入 `04_my_favorites` 或 `05_my_work`。
