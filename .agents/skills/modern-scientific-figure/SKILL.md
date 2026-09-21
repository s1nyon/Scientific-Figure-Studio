---
name: modern-scientific-figure
description: Use when a user requests a reproducible Python figure for a paper, asks to redesign an existing scientific chart, or needs a modern minimal, algorithm-research, or visual-narrative figure.
---

# Modern Scientific Figure

这是正式科研绘图的主流程。先读项目根目录的 [AGENTS.md](../../../AGENTS.md)、`design_system/` 和输入数据说明，再开始设计；项目级数据真实性、源码交付和安全规则始终优先。

## 适用场景

- 用户提供 CSV、表格或已定义的数据并要求绘制论文图表。
- 用户要求统一配色、字体、布局或重新设计现有 Matplotlib 图。
- 用户需要一张可复现、可手动修改的正式图片。

## 不适用场景

- 只有审美检查、没有生成或修改图表时，使用 `figure-design-review`。
- 需要判断收敛、误差、非支配关系或敏感度数学含义时，同时使用 `algorithm-visualization`。
- 只管理收藏图片、索引或设计笔记时，使用 `figure-reference-manager`。

## 执行步骤

1. 建立 Figure Brief：记录数据来源、字段、单位、目标、页面尺寸、数据集划分和不确定性依据。缺失的信息要标记为未知，不能补造。
2. 用 `figure_gallery/gallery_index.csv` 检索相关参考；优先采用用户明确喜欢的案例，只借鉴可观察的布局、层级和颜色关系。
3. 选择与科学问题匹配的图表类型和面板结构。科学证据优先于装饰，颜色不能承担唯一的关键信息。
4. 使用 `figure_studio` 和项目设计规范编写独立的 `plot.py` 与 `config.py`。数据读取、计算、视觉参数和导出分开。
5. 运行源码，至少导出 PNG、SVG、PDF；把输入字段、处理、单位、练习数据状态写入 `data_manifest.json`。
6. 打开实际渲染的 PNG 检查裁切、重叠、字体、图例、颜色、缩小后的可读性和科学标注。发现问题就改源码并重新生成。
7. 交付图片、完整源码、可调整配置、数据说明、运行 README 和验证结果。不能只交付最终图片。

## 交付契约

每张正式图放在独立目录，至少包含 `plot.py`、`config.py`、`data_manifest.json`、`README.md`、`figure.png`、`figure.svg` 和 `figure.pdf`。`config.py` 中的画布、颜色、字号、线宽、图例和坐标范围必须被绘图代码实际读取。

## 常见错误

| 现象 | 处理 |
| --- | --- |
| 只有 PNG，没有源码 | 停止交付，补齐可运行的源码和配置。 |
| 参考图很漂亮但图表类型不匹配 | 保留科学图表类型，只抽取层级、留白或字体方法。 |
| 只有看代码没有看图片 | 运行并打开实际输出；没有视觉检查就标记为未验证。 |
| 想用渐变、阴影或删点制造高级感 | 删除无证据装饰，恢复完整数据和清晰语义。 |

