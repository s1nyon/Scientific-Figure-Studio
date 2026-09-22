---
name: figure-reference-manager
description: Use when a user adds scientific reference images, asks to analyze or search a personal figure gallery, wants to update favorites, or needs design notes and index maintenance without modifying originals.
---

# Figure Reference Manager

这是本地个人科研图表图库的管理流程。先读项目根目录的 [AGENTS.md](../../../AGENTS.md)，把用户收藏和外部参考图片视为原始资产；索引、哈希、缩略图、视觉分析和设计笔记必须与原图分离。

## 适用范围

- 用户把新图片放入 `figure_gallery/00_inbox` 或其他图库目录。
- 用户要求扫描、视觉分析、检索类似案例、维护 favorites 或关联认可作品。
- 用户需要增量扫描、识别重复文件、补全档案或检查失效索引路径。

如果任务是生成新的论文图表，主流程使用 `modern-scientific-figure`，图库只是按需参考；如果任务是审查已生成图片，使用 `figure-design-review`。

## 信息来源必须分开

每条记录分别保留：

1. **文件扫描事实：** 相对路径、尺寸、模式、修改时间、哈希、像素统计和索引状态；
2. **Agent 视觉观察：** Agent 实际打开图片后看到的图表类型、构图、颜色关系、字体层级、坐标轴、标记、标注、信息层级和留白；
3. **用户评价：** 仅记录用户明确提供的喜欢、不喜欢、认可范围和原话；
4. **科学内容：** 数据来源、变量含义、结论和单位；无法从图片确定的内容写为未知或估计；
5. **代码/复现 provenance：** 入口脚本、配置、输入、版本和哈希关联。

扫描器或 Agent 观察不能代替用户评价；图片来自 Nature 或其他期刊也不能自动变成用户偏好、科学有效性或公开再分发授权。

## 执行步骤

1. 确认图库根目录和扫描范围；空图库是合法状态，继续使用 Nature-first 默认设计。
2. 运行 `python tools/update_gallery.py`。扫描支持的图片扩展名，按相对路径和 SHA-256 识别新增、变化、重复、已分析、缺失档案和失效索引；内容变化标记为 stale 并保留历史。该脚本没有命令行参数，不要给它传入会被误解的选项。
3. 能够打开图片时，先实际查看原图，再用 `GalleryIndex.record_agent_analysis(..., viewed=True, view_receipt=...)` 写入视觉观察。没有实际查看只能保持 `not_analyzed`，不能凭像素统计冒充深度理解。
4. 设计笔记写入 `_generated/gallery_notes/`，视觉分析写入 `_generated/gallery_visual_analysis/`，索引写入 `gallery_index.csv`；不得把生成文件放在原图目录中覆盖原图。
5. 用户明确认可后，才记录 favorite 或 accepted work 关系；不自动移动图片、不自动写用户评价。
6. 绘图任务按图表类型、科学场景、数据结构和用户明确评价检索少量相关记录。借鉴设计方法，不复制参考图数据、结论或私人内容；不匹配时继续自主设计。

## 当前 API 和 CLI

Python API：

```python
from figure_studio.gallery import GalleryIndex, search_references

gallery = GalleryIndex("figure_gallery")
records = gallery.scan()
matches = search_references(
    "figure_gallery",
    query="convergence",
    chart_type="algorithm convergence curve",
    application="algorithm comparison and optimization trajectory",
    limit=3,
)

record = gallery.record_agent_analysis(
    "00_inbox/example.png",
    {
        "chart_type": "line chart",
        "layout": "single panel",
        "palette": "blue and orange",
        "limitations": ["font name unknown", "scientific data source unknown"],
    },
    analyzed_by="codex",
    viewed=True,
    view_receipt={
        "viewer": "view_image",
        "path": "figure_gallery/00_inbox/example.png",
        "dimensions_px": "1242x1200",
    },
)
```

`record_agent_analysis()` 的 `viewed=True` 和非空 `view_receipt` 是强制的；它只写索引/生成的视觉档案，不修改原图、用户评价或科学 provenance。若要用 CLI，真实参数是：

```powershell
python tools/record_gallery_analysis.py `
  --gallery-root figure_gallery `
  --image 00_inbox/example.png `
  --observations path/to/observations.json `
  --view-receipt path/to/view_receipt.json `
  --analyzed-by codex
```

`observations.json` 和 `view_receipt.json` 必须是 JSON object；实际打开图片后才可填写 receipt。

## 认可作品和外部参考图

已认可作品通过 `search_work_references()` 或以下 CLI 单独检索，不与普通图片 favorite 混合：

```powershell
python tools/manage_figure_work.py works --gallery-root figure_gallery --query "algorithm" --limit 3
```

Round 04 Design A 位于 `05_my_work/round_04_design_a_accepted/`，是用户明确认可的算法收敛图视觉参考。它使用 `illustrative practice data`，不证明顶刊质量、科学结果有效性、普遍算法优势或全局审美偏好；其适用场景和限制以 [accepted reference case](../../../figure_gallery/05_my_work/round_04_design_a_accepted/accepted_reference_case.md) 为准。不要自动把它升级为模板。

用户收藏的外部论文图片只能按来源和授权情况使用。本地存在文件不代表拥有公开提交或再分发权限；不要把它们自动提交到公开仓库，不要删除、移动、重命名或覆盖原图。

## 常见错误

| 错误 | 修复 |
| --- | --- |
| 没打开图片却记录 Agent 视觉结论 | 保持 `not_analyzed`，或实际查看后提供 `viewed=True` 和 receipt。 |
| 把像素统计写成用户偏好 | 只写可观察事实，把评价留给用户。 |
| 把第三方论文图自动放入 favorites 或公开仓库 | 保留来源、授权未知状态和原始路径，等待用户决定。 |
| 用参考图替代当前任务的图形类型 | 只提取匹配的层级/留白/标注方法，重新根据科学证据设计。 |
| 用原图作为缩略图或临时输出覆盖 | 所有辅助文件放在 `_generated/` 或独立临时目录。 |
