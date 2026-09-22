---
name: modern-scientific-figure
description: Use when a user requests a reproducible Python figure for a paper, asks to redesign an existing scientific chart, or needs a modern minimal, algorithm-research, or visual-narrative figure.
---

# Modern Scientific Figure

这是 Scientific Figure Studio 的统一 Codex 绘图入口。先读项目根目录的 [AGENTS.md](../../../AGENTS.md)、
输入数据/模型说明和需要的设计参考，再开始设计；项目级数据真实性、源码交付和安全规则始终优先。
对于数值科研图、综合 Figure 和论文级静态 Figure，必须先显式调用宿主 `$nature-figure`，
再决定 Python 实现方式。现有模板只是可选 renderer，不是设计入口。

## 适用场景

- 用户提供 CSV、表格或已定义的数据并要求绘制论文图表。
- 用户要求统一配色、字体、布局或重新设计现有 Matplotlib 图。
- 用户需要一张可复现、可手动修改的正式图片。

## 不适用场景

- 只有审美检查、没有生成或修改图表时，使用 `figure-design-review`。
- 需要判断收敛、误差、非支配关系或敏感度数学含义时，同时使用 `algorithm-visualization`。
- 只管理收藏图片、索引或设计笔记时，使用 `figure-reference-manager`。
- 主要是流程图、模型架构、几何约束、三维场景或网络机制时，使用 `scientific-illustration`；
  如果任务同时包含数值图表，先加载 `$nature-figure` 再分配量化面板和插图面板。

## 统一入口的 Skill 路由

按以下顺序工作，不要先套用固定模板再补写设计记录：

1. **任务与科学信息检查**：读取数据、模型结构、现有图片和用户指定参考；核实目标函数方向、
   字段、单位、数据集划分和模块连接。无法确定的科学信息标记为未知。
2. **Nature Figure Contract**：对适用的 Figure 显式加载 `$nature-figure`，读取其 `SKILL.md`
   和任务相关 references，先确定一条可验证的核心结论、证据层级、Figure archetype、面板图和 QA 风险。
   当前项目固定使用 Python，因此 Nature Skill 的设计、绘图、预览、导出和 QA 全部走 Python。
3. **专业分流**：收敛、预测、误差、敏感度和 Pareto 数学语义使用 `algorithm-visualization`；
   流程/架构/几何/三维/网络使用 `scientific-illustration`；用户参考图使用
   `figure-reference-manager`；最终 PNG 检查使用 `figure-design-review`。
4. **实现选择**：判断现有模板是否能表达已确定的科学结构；能复用才复用，否则创建独立的
   `plot.py` 和 `config.py`。不得为了复用模板改变原始数据、模型模块或信息关系。
5. **执行和交付**：使用 `tools/run_figure_task.py` 管理 Brief、renderer、输入、输出和哈希；
   实际运行 Python，导出 PNG/SVG/PDF，打开 PNG，必要时修改源码并重新运行。

宿主 `$nature-figure` 的真实加载由 Codex Agent 完成；Python runner 只能验证固定安装树、
读取指定 references、运行 renderer 和记录结果，不能伪装成 Agent 或把本地文件读取当作 Skill 调用证明。

## Figure Brief、工作模式和用户覆盖

每项任务保存一个结构化 Figure Brief，至少包含 `task`、`data_sources`、`fields`、`units`、
`claim`、`evidence_panels`、`archetype`、`backend`、`task_mode`、`nature_references`、
`renderer`、`review_risks` 和必要的 `scientific_unknowns`。如果任务选用了个人图库，另外记录
`gallery_references`、`code_references` 和用户原话 `user_reference_note`；视觉设计参考与代码参考
必须分开。`backend` 必须为 `Python`。

支持三种工作模式：

- `ordinary`：Agent 选择一个最合适的设计并完成检查。
- `core-practice`：生成两种信息组织或构图确实不同的草稿供选择。
- `formal`：先生成完整初版并完成自动检查、实际查看和精修，再交给用户验收。

用户可以明确指定 Nature Skill、参考图片、Python 工具、renderer、画布尺寸或模板。覆盖只改变
工作流选择，不得改变原始数据、目标函数方向、模型结构或未提供的科学结论。

## 执行步骤

1. 建立并保存 Figure Brief；缺失信息标记为未知，不能补造。
2. 如果是 Nature 适用的数值图或综合 Figure，显式加载 `$nature-figure` 并读取相关原始 reference。
3. 用 `GalleryIndex.search()` 或 `search_references()` 按用户明确认可、图表类型和应用场景检索少量相关参考；
   用户指定的图片必须先实际打开。只借鉴可观察的布局、层级、颜色关系、字体层次、标注和留白，
   不复制参考图的数据、结论或私人内容。图库为空时继续使用 Nature Skill 和默认设计系统。
4. 选择与科学问题匹配的图表类型和面板结构，科学证据优先于装饰。
5. 使用 `figure_studio` 或独立 renderer 编写 `plot.py` 与 `config.py`，数据读取、计算、视觉参数和导出分开。
6. 通过 `tools/run_figure_task.py` 在独立 staging 目录实际运行源码，至少导出 PNG、SVG、PDF，并记录
   source/input hashes、版本状态和图库参考。冲突检查在正式目标写入前完成；失败时不留下半成品。
7. 打开实际 PNG，检查裁切、重叠、字体、图例、颜色、缩小后的可读性和科学标注；发现问题就改源码并重新生成。
8. 用户提出自然语言局部修改时，先快照当前 PNG、源码和配置，再修改、重跑、查看，并用 Python 生成 Before/After 对比图。
9. 交付图片、完整源码、可调整配置、输入资料、Figure Brief、Design Receipt、运行 README 和验证结果。
   验收时可用 `tools/manage_figure_work.py accept` 将候选目录提升为认可作品；该操作必须带用户明确
   评价。认可目录不能被普通渲染、`--overwrite` 或快照恢复改写；后续修改使用 `clone` 派生工作区。

Design Receipt 必须对应本次实际 Figure Brief、renderer、输入哈希和输出文件；它不是宿主
Nature Skill 真实调用的替代证据。真实调用状态、实际图片查看和精修动作必须单独记录。

## 交付契约

每张正式图放在独立目录，至少包含 `plot.py`、`config.py`、`data_manifest.json`、`README.md`、`figure.png`、`figure.svg` 和 `figure.pdf`。`config.py` 中的画布、颜色、字号、线宽、图例和坐标范围必须被绘图代码实际读取。

## 常见错误

| 现象 | 处理 |
| --- | --- |
| 只有 PNG，没有源码 | 停止交付，补齐可运行的源码和配置。 |
| 参考图很漂亮但图表类型不匹配 | 保留科学图表类型，只抽取层级、留白或字体方法。 |
| 只有看代码没有看图片 | 运行并打开实际输出；没有视觉检查就标记为未验证。 |
| 想用渐变、阴影或删点制造高级感 | 删除无证据装饰，恢复完整数据和清晰语义。 |
