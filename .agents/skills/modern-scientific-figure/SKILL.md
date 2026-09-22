---
name: modern-scientific-figure
description: Use when a user requests a reproducible Python figure for a paper, asks to redesign an existing scientific chart, or needs a modern minimal, algorithm-research, or visual-narrative figure.
---

# Modern Scientific Figure

这是 Scientific Figure Studio 的唯一统一 Codex 绘图入口。开始前先读项目根目录的 [AGENTS.md](../../../AGENTS.md)、输入数据/模型说明和必要的设计参考；项目级科学准确性、源码交付和安全规则始终优先。

对于数值科研图、论文级静态 Figure 和数据图表组合图，先显式加载适用的宿主 `$nature-figure`，再根据当前科学任务决定 Python 实现。现有模板和视觉预设是可选素材，不是设计入口。

## 适用范围和分工

- 用户提供 CSV、表格、结构化输入或已有图片，并要求绘制、重设计或交付可复现论文图。
- 收敛、预测、误差、敏感度、Pareto、空间和网络的数学含义需要同时使用 `algorithm-visualization`。
- 流程、架构、几何、三维和网络机制主要使用 `scientific-illustration`；若含量化面板，先由 `$nature-figure` 组织证据层级。
- 用户参考图、个人图库和已认可作品使用 `figure-reference-manager`；生成后的 PNG、SVG、PDF 由 `figure-design-review` 实际检查。

不适用于只做图库管理、只做图片审查或没有数据/结构定义却想凭空生成算法优势的任务。信息不足时建立 Figure Brief 并标记未知，不能用默认样式补造证据。

## 设计决策顺序

1. **建立科学表达目标。** 读取数据、模型结构、已有图片和用户参考，核实字段、单位、目标方向、数据集划分、连接关系和不确定性依据。写出当前图片要表达的一条可验证结论、支持它的主要证据、可能需要的辅助证据，以及适合放入图注而非图内的解释。
2. **调用适用的 Nature guidance。** 对数值图或综合 Figure 显式加载 `$nature-figure`，读取其 `SKILL.md` 和任务相关 references，形成 Figure Contract、证据层级、archetype、面板职责和 QA 风险。当前项目的绘图、预览、导出和 QA 统一使用 Python。
3. **检查面板必要性。** 每个辅助面板必须承担与主图不同的科学任务；如果只是重复主图已清楚表达的信息，应删除或重新评估。单面板不是所有任务的默认答案；多个面板在证据分工清楚时应保留。不能仅按字段数量决定面板数量。
4. **按需使用参考图库。** 用户指定图片时先实际打开，再提取可观察的布局、信息层级、颜色关系、字体层次、标注和留白。未指定时只检索少量与科学内容、数据结构、图形类型和表达目标匹配的案例。图库为空或不匹配时继续由 Nature guidance 自主设计。
5. **选择实现而非套模板。** 判断现有模板或 `figure_studio` primitives 是否能表达已经确定的科学结构；能复用才复用，否则创建独立 `plot.py` 和 `config.py`。不得为了使用模板、Design A 或视觉预设改变原始数据、模型模块、目标方向或证据关系。

当用户要求整体重新设计时，应从当前任务重新评估图形类型、阅读顺序、信息层级和布局，不能只在上一版 `plot.py` 上换字体和颜色。普通局部精修不需要重新做完整 Figure 设计。

## Figure Brief、参考和工作模式

每项任务保存结构化 Figure Brief，至少包含 `task`、`data_sources`、`fields`、`units`、`claim`、`evidence_panels`、`archetype`、`backend`、`task_mode`、`nature_references`、`renderer`、`review_risks` 和必要的 `scientific_unknowns`。`backend` 为 `Python`。若使用图库，另外记录 `gallery_references`、`code_references` 和用户原话 `user_reference_note`；视觉参考、代码参考、用户评价和科学 provenance 不互相替代。可参考 [Figure Brief schema](references/figure-brief.md)。

支持三种模式：

- `ordinary`：选择一个最合适的设计并完成检查；
- `core-practice`：仅在需要探索设计方向时，生成两种具有实质信息组织或构图差异的草稿；
- `formal`：先完成完整初版、自动检查、实际图片查看和必要精修，再交给用户验收。

用户可以覆盖 Nature Skill、参考图、Python 工具、renderer、画布尺寸或模板选择，但覆盖不改变原始数据、目标函数方向、模型结构或未提供的科学结论。

## 执行和审查

1. 保存 Figure Brief；缺失信息写为未知。
2. 对适用的数值/综合 Figure 显式加载 `$nature-figure`，并按需调用专业 Skill。
3. 用 `GalleryIndex.search()` 或 `search_references()` 检索少量匹配参考；指定图片必须实际打开。只借鉴设计方法，不复制数据、结论或私人内容。
4. 选择符合科学问题的图表类型和面板结构。颜色、字体、直接标签、图例和留白服务于证据，不制造数据没有支持的优势。
5. 使用 `figure_studio` 或独立 renderer 编写 `plot.py`/`config.py`，把数据读取、计算、视觉参数和导出分开；所有变换、不确定性计算和目标方向写进源码或 manifest。
6. 通过 `tools/run_figure_task.py` 在 staging 目录实际运行，至少导出 PNG、SVG、PDF，并记录 source/input hashes、版本状态和参考信息。runner 不能代替宿主 Agent 调用 Nature Skill。
7. 打开实际 PNG，在原始尺寸和论文预期插入尺寸检查：主要数据是否突出、阅读顺序是否明确、辅助面板是否有信息价值、文字是否挤占绘图区、图内标注是否与计算一致、面板大小是否匹配信息密度，以及裁切、重叠、字体、图例、颜色、单位和矢量导出。缩小后不可读时必须修复。
8. 发现整体设计问题时重新评估 Figure 方案；发现局部问题时优先修改源码/配置，重新导出全部格式并再次查看。不要设置主观视觉分数、固定精修轮数或无法验证的顶刊认证。
9. 交付图片、完整源码、配置、输入资料、Figure Brief、Design Receipt、运行 README 和验证结果。用户局部修改时先快照并生成 Before/After。

Design Receipt 必须对应本次 Figure Brief、renderer、输入哈希和输出文件；它不是宿主 Nature Skill 真实调用的替代证据。真实宿主调用、实际图片查看和精修动作必须单独记录。

## 交付契约

每张正式图放在独立目录，至少包含 `plot.py`、`config.py`、`data_manifest.json`、`README.md`、`figure.png`、`figure.svg` 和 `figure.pdf`。`config.py` 中的画布、颜色、字号、线宽、图例和坐标范围必须被绘图代码实际读取。候选版本可通过 `tools/manage_figure_work.py accept` 提升，但必须带用户明确评价；认可目录不能被普通渲染、`--overwrite` 或快照恢复改写。

## 常见错误

| 现象 | 处理 |
| --- | --- |
| 只有 PNG，没有源码或输入 provenance | 停止交付，补齐可运行源码、配置和 manifest。 |
| 参考图漂亮但图表类型或科学任务不匹配 | 保留科学图表类型，只抽取有依据的层级、留白或字体方法。 |
| 只有看代码没有看图片 | 实际运行并打开输出；没有视觉检查就标记为未验证。 |
| 为了高级感添加渐变、阴影或删点 | 删除无证据装饰，恢复完整数据和清晰语义。 |
| 用旧图的面板数量或 Design A 作为默认答案 | 回到当前 claim、evidence 和数据密度重新设计。 |
