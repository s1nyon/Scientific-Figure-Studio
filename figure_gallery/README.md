# 个人科研绘图参考图库

请把新图片放入 `00_inbox/`。确定性扫描器会读取图片尺寸、模式、内容哈希、主色估计、亮度和留白比例，并在 `_generated/gallery_notes/` 生成独立设计笔记。新图默认标记为 `not_analyzed`，不会被扫描器冒充完成深度视觉分析。

原图不会被修改、移动、删除或上传。图表类型、字体名称、数据和研究结论不会由像素统计推断；请在 CSV 或 Markdown 中手动补充来源、风格、应用场景和个人评价。内容变化会在 `_generated/gallery_history/` 留下旧哈希和旧评价，新的视觉档案默认标记为 `stale`。

具备图像查看能力的 Agent 只有在实际打开图片并提供 `viewed=True` 与 view receipt 后，才能调用 `record_agent_analysis()`；
档案至少应区分图表类型、构图、配色关系、字体层级、标注、信息层级、留白、可借鉴方法和适用场景。这些记录保存在
`_generated/gallery_visual_analysis/`，与确定性索引、用户偏好、优秀作品关联和原图分开。

目录说明：

- `00_inbox/`：尚未整理的新图片。
- `01_minimal/`：极简精致型参考。
- `02_algorithm/`：算法论文型参考。
- `03_visual_narrative/`：信息叙事型参考。
- `04_my_favorites/`：用户明确认可的图片。
- `05_my_work/`：用户完成并认可的作品。

用户认可的作品源码、配置、输入、输出和复现 manifest 保存在独立作品目录；`_generated/work_links/` 只保存关联记录，不自动把任何图片升级为 favorite 或模板。

更新命令：

```powershell
python tools/update_gallery.py
```
