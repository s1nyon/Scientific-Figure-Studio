# Scientific Figure Studio 设计总指南

本项目面向数学建模竞赛和后续学术研究，使用 Matplotlib 生成静态、可复现、可编辑的科研图表。设计优先级是科学准确性、论文尺寸可读性、整篇论文的一致性，然后才是装饰性美观。

## 三种视觉预设

| 预设 | 适用任务 | 主要表达 |
| --- | --- | --- |
| `minimal_editorial` | 单结果、简洁比较、基础统计 | 白底、克制网格、清晰层级和留白 |
| `algorithm_research` | 收敛、预测、误差、优化、消融 | 稳定算法色循环、主结果和辅助证据分层 |
| `visual_narrative` | 关键发现、复杂关系、多面板 | 重点标注、直接标签和有依据的视觉叙事 |

预设共享深蓝灰文字、蓝色主色、青绿色辅助色、暖橙色强调色和中性灰辅助色。三种预设不改变数据含义；只在信息任务需要时增加视觉层级。

## 颜色语义

- 同一算法在相关图表中沿用同一颜色，并用线型或标记增加冗余编码。
- 主结果使用较高对比度；参考线、网格和背景弱化。
- 连续数据使用 `viridis` 等感知连续色图；正负偏离使用 `RdBu_r` 等发散色图并记录中心值。
- 分类数量较多时不要只靠近似颜色区分；增加标记、线型或直接标签。
- 不使用 `rainbow`/`jet` 作为默认连续色图，不让颜色暗示数据没有支持的优劣结论。

## 字体和尺寸

`figure_studio.fonts` 会检测系统字体，优先使用可用的 Arial/Calibri/Aptos/DejaVu Sans 等英文字体和 Microsoft YaHei/SimHei/Noto Sans SC/Source Han Sans SC 等中文字体；缺失时报告降级结果，不把某台电脑的绝对字体路径写进项目。中文数学建模论文应在导出后确认中文、数字和数学符号均无缺字。

画布预设采用英寸：`compact`、`standard`、`wide`、`composite`。最终字号要按论文实际插入宽度复查，不能只在全屏 PNG 上判断可读性。

## 布局和导出

单面板优先；只有面板之间共享数据故事时才使用组合图。GridSpec 的列宽、行高和面板标签应服务于信息层级。正式输出使用 PNG 预览和 SVG/PDF 矢量文件，代码设置 `pdf.fonttype=42`、`svg.fonttype=none` 以保留可编辑文字；导出后仍需检查字体和嵌入内容。

## 参考来源和边界

本项目实际参考了 OpenAI Skills 文档的目录和元数据要求、Nature Figure Making Skill 的 figure brief/多面板/导出思路、Scientific Visualization Skill 的数据真实性和可读性检查、SciencePlots 的科研样式组织方式，以及 Nature Research Figure Guide 关于尺寸、字体、颜色可访问性和多面板导出的公开建议。项目不机械复制期刊投稿规格，也不复制第三方代码或用户参考图数据。

参考链接：

- <https://developers.openai.com/zh-Hans/docs/build-skills>
- <https://github.com/lth0/codexSkill/tree/main/skills/codex/nature-figure>
- <https://github.com/K-Dense-AI/scientific-agent-skills/tree/main/skills/scientific-visualization>
- <https://github.com/garrettj403/SciencePlots>
- <https://research-figure-guide.nature.com/>
