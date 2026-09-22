# 个人科研绘图参考图库

请把新图片放入 `00_inbox/`。确定性扫描器会读取图片尺寸、模式、内容哈希、主色估计、亮度和留白比例，并在 `_generated/gallery_notes/` 生成独立设计笔记。新图默认标记为 `not_analyzed`，不会被扫描器冒充完成深度视觉分析。

原图不会被修改、移动、删除或上传。图表类型、字体名称、数据和研究结论不会由像素分析推断；请在 CSV 或 Markdown 中手动补充来源、风格、应用场景和个人评价。

具备图像查看能力的 Agent 只有在实际打开图片并显式记录观察后，才能调用 `record_agent_analysis()`；这些记录保存在 `_generated/gallery_visual_analysis/`，与确定性索引和原图分开。

目录说明：

- `00_inbox/`：尚未整理的新图片。
- `01_minimal/`：极简精致型参考。
- `02_algorithm/`：算法论文型参考。
- `03_visual_narrative/`：信息叙事型参考。
- `04_my_favorites/`：用户明确认可的图片。
- `05_my_work/`：用户完成并认可的作品。

更新命令：

```powershell
python tools/update_gallery.py
```
