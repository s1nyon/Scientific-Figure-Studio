---
name: scientific-illustration
description: Use when a scientific task needs a Python flowchart, model architecture, geometric schematic, 3-D scene, network mechanism, or mixed chart-and-illustration figure.
---

# Scientific Illustration

这是项目专用的结构化科研插图入口。它补充原始 Nature Figure Making Skill 的范围，
不替换原始 Nature Skill 对数据图表、图表契约和质量审查的专业指导。开始前先读项目根目录
的 [AGENTS.md](../../../AGENTS.md)，并在需要数据图表时先加载已经验证的固定版本
`nature-figure` Skill，再应用本项目的 Python、数据真实性、源码交付和视觉审查要求。

## 适用范围

支持以下六类图片：

1. 算法流程图：节点、定向连接、分支标签和汇合语义来自显式输入。
2. 数学模型与系统架构：只绘制用户提供的模块、端口、方向和连接。
3. 几何模型与约束：使用真实或明确标注的示例坐标、线段、多边形和约束关系。
4. 三维曲面、轨迹和空间场景：使用实际空间数组或明确标记的示例几何，不凭空制造实验结果。
5. 网络结构与研究机制：节点角色、边方向和机制标签来自结构化输入。
6. 数据图表与示意图组合：量化面板与结构面板分别保留证据来源，并用共享视觉系统组织。

如果任务只是数值图表，继续使用 `modern-scientific-figure` 与
`algorithm-visualization`；如果任务只是审查已生成图片，使用 `figure-design-review`。

## Figure Brief 与输入契约

绘图前必须记录：

- 数据或结构来源、文件路径、版本和 `data_status`（`formal input data`、
  `illustrative practice data` 或 `unknown source data`）。
- 节点/模块 ID、坐标、角色、边的 `source`/`target`、分支或机制标签，以及每个数值字段的单位。
- 页面尺寸、面板层级、目标读者、输出格式和不确定性依据。
- 缺失的信息、未知字体、示例结构和未支持结论；不能用视觉常识补造模型模块、数据流、坐标或结论。

结构数据应使用 JSON/YAML 或清晰的 Python 映射保存。流程图和架构图的每条连接必须引用
已声明的端点；应调用 `figure_studio.illustrations.validate_flow_edges` 或对应绘图函数，
让未知端点直接失败。使用 `draw_geometry` 时保持 `set_aspect("equal")`；坐标、比例和
约束关系不能为适应画布而静默改变。

## Python 实现约束

正式绘图、预览、导出和审查统一采用 Python。优先使用 Matplotlib 面向对象 API 与
`figure_studio.illustrations`：

- `draw_flowchart` 使用明确节点和定向箭头；分支标签必须来自输入。
- `draw_architecture` 使用输入模块和连接；不能把 architecture 请求转换成普通折线图
  (ordinary line chart). Do not add encoder, solver, decoder, data flows, or performance claims
  that are absent from the supplied architecture.
- `draw_geometry` 绘制输入点和约束并维持等比例坐标。
- `draw_surface` 只接受形状匹配且有限（finite）的 `x/y/z` 数组；三维曲面必须说明数据或示例几何依据。
- `draw_network` 保留节点和边的关系；若方向未知，不用箭头暗示方向。
- 混合 Figure 使用独立的量化面板和示意面板；任何平滑、聚合、坐标变换或归一化都写入源码和 manifest。

颜色、字号、线宽、节点尺寸、箭头样式、画布、坐标范围和输出格式集中放在 `config.py`。
不要在绘图函数内硬编码仅适用于练习数据的路径、模块或指标。原始数据、异常值和用户结构不得
为了装饰被删除、覆盖或隐藏。

## 交付与验证

每张图必须交付同一版本生成的：

- 完整可运行的 `plot.py`、可修改的 `config.py`、输入文件和 `data_manifest.json`；
- `README.md`（运行命令、结构/数据说明、单位、转换和不确定性限制）；
- PDF、SVG 和高分辨率 PNG；SVG/PDF 尽量保留可编辑文字和矢量结构。

After actual execution of the source, 必须打开 PNG，在原始尺寸和最终插入尺寸检查节点、连接线、分支、几何比例、
三维遮挡、面板层级、字体、图例和裁切；发现问题回到源码或配置修复，再重新导出全部格式。
没有实际查看的图片标记为 `未验证`，不能仅凭代码或存在文件声称通过视觉审查。

示例结构必须明确写为 `illustrative practice data` 或 `illustrative example structure`，
不能冒充正式比赛结果、实验结果、模型性能或用户真实架构。最终报告区分：已实现、已运行、自动
测试通过、已打开检查和仍需用户确认的内容。
