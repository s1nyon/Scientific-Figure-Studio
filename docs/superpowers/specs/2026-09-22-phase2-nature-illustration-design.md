# Scientific Figure Studio 第二阶段设计：Nature Skill 接入与科研插图

## 目标

在保留现有六类可复现 Python 数值图表的基础上，完成以下可验收结果：

1. 以 `1930963cbc004da9ac8e3af7944d4f0a3488d3e1` 固定接入 `lth0/codexSkill` 的完整 `nature-figure` 目录；由于该提交未携带可确认的 LICENSE/COPYING/NOTICE，仓库不复制上游内容，而提供完整目录的固定 SHA 本地安装与验证方式。
2. 让 `modern-scientific-figure` 作为项目入口，调用已安装的上游 Nature Skill 参考资料，再应用项目自己的 Python、数据真实性、图库、源码交付和视觉审查约束。
3. 修复图库深度视觉分析状态、正式数据 manifest、外部数据路径、预测 split 假设和收敛目标方向问题。
4. 新增 `scientific-illustration` 专项 Skill 及 Python 插图支持，实际交付算法流程图、模型架构图和图表+示意图组合 Figure。
5. 对所有交付物实际运行源码、导出 PDF/SVG/PNG、查看渲染图片并记录自动测试、Ruff、上游调用和未验证项。

## 已确认的上下文与约束

- 正式绘图语言固定为 Python；上游 Skill 的 R 说明原样保留在本地安装内容中，但本项目适配层不使用 R 生成或预览图片。
- 现有六类模板：convergence、prediction、sensitivity、pareto、spatial、composite，必须继续可运行。
- 示例输入只能标记为 `illustrative practice data` 或明确的示例结构，不能冒充比赛结果。
- 用户图库原图位于图库根目录，自动生成内容只能位于 `_generated`；不得自动进入 favorites，不得覆盖手写评价。
- 画布、字号、颜色、线宽、标记、图例、坐标范围和输出格式由配置文件集中控制。
- 正式数据可以位于项目目录外；路径和数据状态必须在 manifest/provenance 中记录，不修改输入数据。
- 所有路径使用 `pathlib`；测试和 Ruff 使用项目 Conda 环境。

## 方案决策

### 上游 Nature Skill

采用固定 SHA 安装器，而不是 vendoring 或 submodule：

- 安装器从固定 commit 的 GitHub codeload 地址下载完整上游目录。
- 安装到用户指定目标，默认是 `Path.home() / ".codex" / "skills" / "nature-figure"`，下载到临时目录后先校验再安装。
- 默认不覆盖已有目标；`--force` 才允许替换，并在替换前保留可恢复备份。
- 校验上游目录中的 30 个文件、相对路径和 SHA-256 清单；清单包含 `SKILL.md`、`README.md`、11 个 references、15 个 PNG 资源、`evals/evals.json` 和 `.gitignore`。
- 仓库保存版本记录、来源 URL、许可证审查结论、依赖说明和验证命令，不保存未确认许可的上游正文或二进制资源。
- 项目适配器读取安装后的 `SKILL.md` 和指定 references，输出 `nature_context.json`，记录 commit、文件哈希、读取的 reference 名称和适配器版本；这份记录证明原版内容实际参与了该次生成，但不冒充 Codex 动态 Skill 热加载能力。

### 数据与模板适配

新增 manifest 工具层负责：

- 校验 `data_status` 为 `formal input data`、`illustrative practice data` 或 `unknown source data`。
- 解析项目内相对路径和项目外绝对路径。
- 将字段、单位、目标方向、处理方法、不确定性依据和未支持结论统一放入 provenance。
- 生成练习数据声明时才显示练习数据水印；正式或未知来源不强行标记为练习数据。

模板修改约定：

- convergence 从 manifest/config 读取 `objective_direction`，使用方向感知累计最优；不固定最小化。
- prediction 接受已有的任意 split 子集；缺少 split 列时使用 `all`，只有存在 test 行时才计算 test 指标，不绘制无依据的预测区间。
- 其他模板从 manifest 读取数据状态、单位和目标信息，保留真实异常值，不为适配视觉而过滤或重写输入。
- 外部数据的 provenance 使用原始声明路径和 SHA-256；无法计算项目相对路径时不伪造相对路径。

### 图库分析

将 Gallery 分成三类信息：

1. **确定性扫描元数据**：尺寸、模式、文件大小、mtime、SHA-256、估计主色、亮度、灰度倾向、留白比例和重复哈希。
2. **Agent 视觉分析**：只有实际打开图片并由具备视觉能力的 Agent 提交观察后，才记录为 `agent_reviewed`；记录配色关系、布局、构图、文字层次、图形语言、适用场景和不确定项。
3. **用户手写信息**：favorite、style、chart_type、application、tags、source、user_evaluation；重新扫描必须逐字段保留。

确定性扫描不覆盖 Agent 记录或用户评价。未实际查看的图片状态保持 `not_analyzed`；空图库、增量扫描、重复图片和失效索引都是合法可测试状态。

### Scientific illustration

新增 `.agents/skills/scientific-illustration`，与上游 `nature-figure` 和项目 `modern-scientific-figure` 分工如下：

- 上游负责投稿级 Figure Contract、证据层级、版式和导出/QA原则。
- `modern-scientific-figure` 负责项目入口、Figure Brief、图库检索、源码交付和最终复现。
- `scientific-illustration` 负责非纯数值图表的结构化 Python 绘制：流程图、架构图、几何约束、3D 曲面/轨迹、网络结构和组合 Figure。
- `figure_studio` 提供可复用的箭头、节点、几何比例、网络边和 3D 辅助函数；每个模板仍保留独立 `plot.py`、`config.py`、输入 manifest 和 README。

实际示例使用固定结构或练习几何，并在 manifest 中写明“illustrative example structure”；不会自行添加用户没有提供的模型模块、信息流或科学结论。

## 交付结构

### 上游与适配

- `tools/install_nature_figure.py`
- `tools/verify_nature_figure.py`
- `figure_studio/nature_adapter.py`
- `docs/UPSTREAM_NATURE_FIGURE.md`
- `tests/test_nature_integration.py`

### 数据与图库

- `figure_studio/manifest.py`
- `figure_studio/gallery.py` 及其测试
- `tests/test_manifest.py`
- `tests/test_gallery.py` 的增量和手写评价回归用例

### Scientific illustration

- `.agents/skills/scientific-illustration/SKILL.md`
- `.agents/skills/scientific-illustration/references/illustration-contract.md`
- `figure_studio/illustrations.py`
- `templates/illustration/flowchart/`
- `templates/illustration/architecture/`
- `templates/illustration/composite/`
- `tests/test_illustration_templates.py`

### 文档与报告

- `README.md`、`docs/SKILLS_USAGE.md`、`docs/GALLERY_WORKFLOW.md`、`docs/QUICK_START.md`
- `docs/TEST_REPORT.md`
- 新增示例的 README、manifest、源码、配置和 PDF/SVG/PNG 输出

## 生成与验证流程

1. 先写失败测试：上游固定目录校验、manifest 状态/外部路径、gallery 手写字段保护、目标方向、可选 split、插图结构语义和导出契约。
2. 用项目 Conda Python 运行失败测试，确认失败原因是缺少新行为而不是测试错误。
3. 编写最小实现并逐项运行 focused tests；每次行为修改都保留回归测试。
4. 安装并验证固定 SHA 的上游 Skill，读取 `figure-contract.md`、`common-patterns.md` 和 `qa-contract.md`，由适配器记录 context。
5. 运行六类旧模板和三类新插图模板，导出 PDF/SVG/PNG；实际修改一次配置后再次生成并比较产物变化。
6. 使用本地图片查看工具打开新生成图片，按最终插入尺寸检查裁切、节点/连接线语义、文字层级、图例、坐标比例、颜色和练习数据声明。
7. 执行全量 pytest、Ruff、Skill 结构验证、上游验证、文档命令检查和 `git diff --check`。
8. 报告分为已完成代码、已实际运行、自动测试通过、已实际检查图片、未验证和需要用户确认；不把安装器验证等同于本会话自动刷新 Skill 索引。

## 不在本阶段范围内

- 不复制或改写未确认许可的上游 Nature Skill 内容。
- 不支持 R 作为项目正式绘图后端，不为 R 安装额外依赖。
- 不把个人图库图片上传到外部服务，不自动生成用户偏好。
- 不凭空创建真实实验数据、比赛结果、置信区间、显著性或模型结构。
- 不把所有科研插图强行变成折线、散点或柱状图。

## 验收标准

- 固定提交完整 30 文件目录可在本机按说明安装并通过清单校验；版本、许可限制、依赖和调用证据均有记录。
- 六类原有模板保持可运行，并支持 manifest 数据状态、外部正式数据和新的收敛/预测语义。
- gallery 重新扫描不会覆盖用户手写评价；未查看图片不会标记为深度视觉分析完成。
- 新 Skill 元数据、引用路径和职责可被自动测试发现；三类新示例有独立源码、配置、输入说明和 PDF/SVG/PNG。
- 每个正式绘图交付目录包含可运行 Python 源码、配置、manifest、README 和导出结果。
- 自动测试、Ruff、实际渲染、实际图片查看和未验证项都写入最终报告。
