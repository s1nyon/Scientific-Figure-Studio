# Scientific Figure Studio 第一版设计规格

日期：2026-09-21

状态：已获用户批准，待进入实现计划

## 目标

建立一个本地、可复现、以 Matplotlib 为核心的科研绘图工程，服务数学建模竞赛论文和后续研究。第一版必须能够在 Conda 环境中运行，实际生成六类现代科研图表示例，每张示例图都提供完整 Python 源码、可修改配置、数据说明和 PDF/SVG/PNG 输出。

系统的设计重点是让科学表达、源码控制和视觉一致性同时成立。示例数据只用于练习，必须与未来正式比赛数据分离；任何不确定的图片观察结果都要标记为估计或未知；个人图库只提供参考，不改变数据含义，也不推断用户尚未表达的审美偏好。

## 设计依据

本设计参考了以下公开资料，实际实现只复用与本项目相关的原则，不复制第三方项目的完整代码或指令：

- [OpenAI Build skills 文档](https://developers.openai.com/zh-Hans/docs/build-skills)：Skill 目录必须包含带 `name` 和 `description` 的 `SKILL.md`；Skill 可通过 `$skill-name` 显式调用，也可根据 description 隐式触发；项目级 Skill 放在 `.agents/skills`。
- [Nature Figure Making Skill](https://raw.githubusercontent.com/lth0/codexSkill/main/skills/codex/nature-figure/SKILL.md)：绘图前先明确核心结论、证据链、布局和审查风险；让视觉层次服务科学论证；优先使用可编辑的矢量导出。
- [Scientific Visualization Skill](https://raw.githubusercontent.com/K-Dense-AI/scientific-agent-skills/main/skills/scientific-visualization/SKILL.md)：保存原始数据和变换记录，显式说明缺失值、不确定性、归一化、平滑和坐标变换；颜色与线型、标记或标签配合使用；导出后检查文件和最终尺寸。
- [SciencePlots](https://github.com/garrettj403/SciencePlots)：作为 Matplotlib 科研样式和颜色循环的参考，不作为本项目完整视觉系统的替代，也不强制引入 LaTeX 依赖。
- [Nature research figure guide](https://research-figure-guide.nature.com/figures/preparing-figures-our-specifications/) 与 [Building and exporting figure panels](https://research-figure-guide.nature.com/figures/building-and-exporting-figure-panels/)：参考轴标签、单位、字体可读性、颜色可访问性、面板排布和可编辑矢量输出；本项目面向数学建模论文，不机械照搬 Nature 的投稿尺寸。

## 方案选择

考虑过三种实现方式：

1. 以本地 Python 包、脚本模板和文件图库为核心。依赖少、结果可复现、源码和图片容易对应，适合当前需求。
2. 以 Jupyter Notebook 为中心。交互探索方便，但配置分散、批量复现和正式交付容易依赖隐藏状态。
3. 构建本地 Web 或桌面图库管理平台。后续可扩展，但会增加前端、数据库和运行维护成本，与第一版的核心绘图目标无关。

第一版采用方案 1。图库使用 Pillow 和规则化元数据分析，不接入外部图像服务，不上传用户图片，也不把启发式分析包装成可靠的视觉理解。

## 总体架构

项目分为五个边界清晰的部分：

1. `figure_studio`：可复用的绘图基础包，负责视觉系统、布局、注释、导出、验证和图库接口。
2. `templates`：六类绘图模板的可运行源码和默认配置。模板只依赖公共包，不把样式参数散落在绘图逻辑里。
3. `examples`：练习数据、生成结果和用于演示的交付目录。所有练习数据用 manifest 明确标记，不进入用户正式数据目录。
4. `.agents/skills`：四个职责不同的 Codex Skill。公共约束由项目根目录 `AGENTS.md` 统一规定。
5. `design_system`、`docs` 和 `tests`：可读的视觉规范、中文使用说明和自动化验收。

数据流如下：

```text
练习数据或用户数据
        ↓
数据字段检查与 Figure Brief
        ↓
模板读取 + config.py
        ↓
figure_studio 样式/布局/注释/导出
        ↓
PDF + SVG + PNG + manifest + validation report
        ↓
实际图片查看与设计审查
```

正式绘图任务必须保留原始输入路径、字段定义、单位、处理步骤和随机种子。公共包不会自动删除异常值、补齐缺失观测或改变坐标含义。

## Conda 环境与依赖

项目提供 `environment.yml`，环境名使用 `scientific-figure-studio`，默认从 `conda-forge` 安装 Python 3.11 及以下最小运行依赖：

- `matplotlib`：静态科研图表和矢量导出。
- `numpy`：数值数组与练习数据计算。
- `pandas`：CSV 读取、字段检查和表格型数据处理。
- `pillow`：图库图像元数据、缩略图和 PNG 验证。
- `pyyaml`：读取项目配色配置。
- `pypdf`：基础 PDF 可打开性和页面信息检查。
- `pytest`：自动化测试。
- `ruff`：Python 代码质量检查。

不强制安装 Seaborn、SciPy、NetworkX 或 SciencePlots。六类第一版模板可以用 Matplotlib、NumPy 和 Pandas 完成；之后只有在真实数据任务确实需要时再增加依赖。项目会提供等价的 Windows PowerShell 命令：`conda env create -f environment.yml`、`conda activate scientific-figure-studio` 和 `python ...`。系统 Python 不参与项目运行。

## `figure_studio` 公共接口

### 样式和配色

`figure_studio.style.figure_style(name, canvas="standard")` 返回一个上下文管理器，在上下文退出后恢复 Matplotlib 全局参数。支持：

- `minimal_editorial`：白底、克制的蓝灰文字、低饱和辅助色和明显留白。
- `algorithm_research`：适合算法比较、收敛、误差和消融实验，主结果线条更突出，辅助信息降低饱和度。
- `visual_narrative`：适合重点结果和多面板组合，允许一个主视觉焦点、直接标注和辅助面板。

`figure_studio.palettes.get_palette(name)` 返回带语义角色的配色对象，至少包含 `ink`、`muted`、`primary`、`secondary`、`accent`、`positive`、`negative`、`grid`、`background` 和分类颜色序列。每个算法在同一示例场景的相关面板中使用同一颜色；颜色之外同时使用线型、标记或直接标签。连续和发散色图按数据语义选择，不以 `jet` 或 `rainbow` 作为默认。

### 字体

`figure_studio.fonts.resolve_fonts()` 使用 Matplotlib 字体管理器检测系统字体，优先选择可用的 Arial/Calibri/DejaVu Sans 等英文无衬线字体，中文优先选择 Noto Sans SC、Microsoft YaHei、SimHei 等实际存在的字体。不存在时降级到可用字体，并返回结构化报告，不能把配置中的字体名称当作已安装事实。

字体设置通过 `font.family`、数学字体和 CJK fallback 组合完成。导出设置使用 `pdf.fonttype=42` 和 `svg.fonttype="none"`，尽量保留文字的可编辑性。项目会额外生成含中文、数字和数学符号的测试图，并在报告中记录当前机器的真实检测结果。

### 画布和布局

`figure_studio.layouts.canvas_size(name)` 支持 `compact`、`standard`、`wide` 和 `composite`，尺寸以英寸返回；`make_subplots()` 对常用的单面板、上下、左右、2×2 和非对称主辅面板提供轻量封装。布局优先采用面向对象 API、`GridSpec` 或 `subplot_mosaic`，不为简单图表强行增加子图。

画布尺寸由配置文件控制，模板默认值参考竞赛论文的常见单栏和双栏宽度，但不会把 Nature 投稿尺寸当作项目硬编码约束。导出默认保留画布物理尺寸，只有用户明确要求时才使用裁切边界。

### 注释和验证

`figure_studio.annotations` 提供参考线、面板标签、直接曲线标签、重点点标注、指标文字块和局部放大连接线等组件。它们都只负责绘图表达，不负责推断科学结论。

`figure_studio.validation` 检查输入字段、有限数值、空数据、输出文件存在性、PNG 尺寸与非空白、SVG XML 结构和 PDF 页数。它会把科学上无法自动判断的内容列为人工检查项，例如不确定性是否有统计依据、帕累托目标方向是否对应研究定义、标注是否与论文结论一致。

`figure_studio.export.export_figure()` 统一生成 PNG、SVG、PDF，并写入生成 manifest。输出存在时默认要求显式覆盖开关或由模板清理其专属输出文件，避免无提示地覆盖用户文件。

## 六类模板和练习场景

六类模板各自包含 `plot.py`、`config.py`、`README.md` 和 `data_manifest.json`。练习数据位于 `examples/data`，输出位于 `examples/outputs/fig_*`；每个输出目录包含图像文件以及指向可运行源码和配置的说明。模板代码支持从项目根目录运行，并通过 `pathlib` 解析路径，不依赖开发者机器的绝对路径。

1. `convergence`：四种算法的最小化目标收敛曲线，使用确定性练习数据；同时保留当前值与历史最优值的数学区分，重复实验带状区间只在数据文件存在时绘制。
2. `prediction`：训练、验证、测试分段的真实值与预测值，以及测试残差面板；练习数据包含明确的 split 字段，误差指标由实际列计算，不凭空生成区间。
3. `sensitivity`：单参数响应曲线和带中心值的参数影响热力图；热力图使用连续或发散归一化，并在数据清单中记录参数单位和指标定义。
4. `pareto`：两个最小化目标的可行解散点，使用支配关系算法计算非支配集合，再按前沿坐标排序连接；关键方案标注只来自输入字段。
5. `spatial`：二维模拟网络中的起点、终点、节点、障碍物和两条候选路径，坐标比例固定，路径方向由箭头表达；数据清单明确声明坐标是模拟平面单位，不是真实地理坐标。
6. `composite`：同一个模拟研究场景的主结果、误差和参数影响组合图，使用非对称 GridSpec，让主面板承担核心结果，辅助面板提供对应证据，不拼接互不相关的数据。

每张图都会生成显眼但克制的“练习数据 / illustrative practice data”说明，避免与正式比赛结果混淆。

## 个人审美图库

图库目录固定为：

```text
figure_gallery/
├── 00_inbox/
├── 01_minimal/
├── 02_algorithm/
├── 03_visual_narrative/
├── 04_my_favorites/
└── 05_my_work/
```

`figure_studio.gallery.GalleryIndex` 提供 `scan()`、`analyze(path)`、`search(query)` 和 `write_index()`。扫描会识别 PNG、JPG、JPEG、WEBP、TIFF 等图片，读取相对路径、大小、修改时间和 SHA-256 内容哈希；同哈希图片标记为重复但不删除原图。

图像分析只输出可观察或可计算的内容：尺寸、长宽比、平均亮度、透明度、主色估计、灰度倾向、留白比例的启发式估计和可由用户填写的风格标签。图表类型、字体名称、原始数据、研究结论和用户喜好不会被算法臆测。每张已分析图片生成 `gallery_notes/<hash>.md`，包含事实、估计、未知项、借鉴建议和版权/来源字段。用户可以手动把图片分类或填写 `favorite: true`；系统不会自动写入个人评价，也不会移动、覆盖或上传原图。

图库为空时，`search()` 返回空结果并让绘图流程退回默认设计系统。图库检索按 `favorite`、风格标签、图表类型、应用场景和关键词排序，但个人喜好永远受任务数学含义和可读性约束。

## 四个 Codex Skills

每个 Skill 都放在 `.agents/skills/<name>/SKILL.md`，并包含一个与职责相关的 `references/` 文件，内容引用根目录 `AGENTS.md` 的公共约束：

- `modern-scientific-figure`：处理完整的 Figure Brief、图库检索、Python 绘图、运行、查看图片、修订和源码交付。明确要求图片和完整源码同时交付。
- `algorithm-visualization`：专注收敛、预测误差、敏感性、帕累托和空间优化的数学表达，复用公共样式，不重新定义颜色和字体系统。
- `figure-design-review`：打开实际渲染文件，按最终插入尺寸检查裁切、图例、对齐、文字、颜色、面板层次和误导性编码，必要时回改 Python 后重新生成。
- `figure-reference-manager`：扫描增量图库、生成分析档案、更新 CSV 索引、检索参考案例，保护原图并显式区分事实和估计。

Skill 只能指导工作流；确定性任务优先由项目 Python 代码完成。宿主 Codex 是否在当前安装中自动加载项目级 Skill，会通过文件结构检查和可用时的显式调用测试分别记录，不把静态检查冒充宿主行为验证。

## 错误处理和数据完整性

- 缺失文件、缺失列、空表或非有限数值：抛出带路径、字段和修复建议的 `ValueError` 或自定义异常。
- 输入数据保持只读；模板计算产生新数组或新表，不在原地改写输入文件。
- 对数轴在存在零或负值时拒绝静默绘制，并要求用户选择过滤、平移或改用线性尺度，同时在 manifest 记录决定。
- 除零、重复键、单位缺失和不一致分组会给出可定位错误。
- 不确定性区间只有在输入数据或已记录模型计算提供依据时才绘制。
- 输出覆盖、图库原图处理和第三方脚本执行都采用保守策略；默认不删除文件，不执行来源不明脚本。

## 测试和验收

测试分为自动和人工两部分：

自动测试使用 `conda run -n scientific-figure-studio pytest -q`，覆盖包导入、字体报告、样式上下文恢复、颜色角色、数据错误提示、帕累托支配关系、图库扫描/去重/空目录、六个模板运行、PDF/SVG/PNG 文件检查和配置变化验证。配置验证至少改变一条主线颜色、线宽、字号和画布尺寸，并比较输出图像的像素或文件摘要，证明参数实际生效。

额外运行 `conda run -n scientific-figure-studio ruff check .`，只把实际运行结果写入测试报告。六张示例图和中文字体测试图必须通过 `view_image` 实际查看；如果缩小到论文插入尺寸后文字或标注不可读，要回改源码并重新生成。测试报告分别列出通过、失败、未验证和需要用户确认的项目。

## 完成定义

只有满足以下条件才称为第一版完成：

1. Conda 环境可创建，项目代码可导入。
2. 三种样式、字体检测、四种画布、导出和验证接口可运行。
3. 六类模板都用练习数据实际生成 PDF、SVG 和高分辨率 PNG。
4. 每类图有可运行源码、配置、数据清单、README 和复现命令。
5. 图库可以处理空目录、增量扫描、内容哈希和简单检索，并保护原图。
6. 四个 Skill 的结构、元数据、引用路径和交付要求均可检查。
7. 测试命令实际执行，报告不把未执行项写成 PASS。
8. 六张示例图完成实际视觉检查，测试报告记录观察结果。
9. 用户可以只改 `config.py` 中的常见参数并重新生成对应图片。

宿主 Codex Skill 的真实自动发现若无法从当前运行环境直接调用，将明确标为未验证；项目文件结构、Skill 元数据和本地验证脚本仍必须通过。
