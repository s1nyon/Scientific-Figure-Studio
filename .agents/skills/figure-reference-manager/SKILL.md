---
name: figure-reference-manager
description: Use when a user adds scientific reference images, asks to analyze or search a personal figure gallery, wants to update favorites, or needs design notes and index maintenance without modifying originals.
---

# Figure Reference Manager

这是本地个人科研图表图库的管理流程。先读项目根目录的 [AGENTS.md](../../../AGENTS.md)，把用户的收藏视为原始资产；索引、哈希、缩略图和设计笔记都必须与原图分离。

## 适用场景

- 用户把新图片放入 `figure_gallery/00_inbox` 或其他图库文件夹。
- 用户要求分析视觉设计、检索类似案例或维护 `04_my_favorites`。
- 用户需要增量扫描、识别重复文件、补全档案或修复失效索引路径。

## 不适用场景

- 当前任务是生成论文图表时，使用 `modern-scientific-figure` 并把图库作为参考输入。
- 需要判断算法结论或计算指标时，使用 `algorithm-visualization`。
- 只审查已经生成的图片时，使用 `figure-design-review`。

## 执行步骤

1. 先确认图库根目录和扫描范围；空图库是合法状态，应继续使用默认设计系统。
2. 扫描支持的图片扩展名，按相对路径和 SHA-256 识别新增、重复、已分析、缺失档案和失效索引。
3. 能够打开图片时，只记录可观察事实：图表类型、可见颜色关系、布局、字体层级、坐标轴、标记、留白和标签方式。字体名称、精确色值、原始数据和科研结论若无法确认，写“估计”或“未知”。
4. 为新图写入 `_generated/gallery_notes/`，更新 `gallery_index.csv`；不要把所有图片自动移动到 favorites。
5. 用户明确认可后才标记为 `04_my_favorites` 或记录个人评价；个人评价可以为空，不能代写。
6. 绘图任务按图表类型和场景检索相关记录，借鉴设计方法，不复制参考图数据、结论或私人内容。
7. 运行 `python tools/update_gallery.py` 后检查索引和档案；报告新增、重复、失效和无法视觉分析的部分。

## 保护契约

禁止删除、覆盖、重命名或不可逆修改原图，禁止上传外部服务，禁止编造用户偏好。清理过时索引时只移除索引或生成笔记，先确认目标位于 `_generated` 或索引文件中。

## 检索与优先级

用户明确喜欢的记录优先；相关图表类型和科学任务要求优先于审美偏好。如果收藏案例不匹配，只借鉴颜色、字体、层级或布局方法，不能强行改变图表类型。

## 常见错误

| 错误 | 修复 |
| --- | --- |
| 没打开图片却声称完成视觉分析 | 标记为未验证，只写文件事实和哈希。 |
| 把所有新图自动放入 favorites | 保留原目录和空评价，等待用户明确认可。 |
| 从参考图推断研究结论 | 只记录可观察的视觉特征，不推断数据含义。 |
| 用原图作为缩略图或临时输出覆盖 | 所有辅助文件放到 `_generated`。 |

