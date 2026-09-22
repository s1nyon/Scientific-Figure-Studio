# Scientific Figure Studio

Scientific Figure Studio 是一个 **Nature-first 的本地 Python 科研绘图工作流**。它帮助 Agent 从科学问题、真实数据和可验证证据出发设计 Figure，再用可复现的 Python 源码生成、检查和交付图片。它不是只提供一组 Matplotlib 模板，也不会用装饰替代科学依据。

## 当前工作方式

普通数值图、论文级 Figure 和数据图表组合图的入口是：

1. 读取数据、模型说明、单位、目标方向、数据划分和已有图片；
2. 建立 Figure Brief，明确可验证结论、主要证据、辅助证据和 QA 风险；
3. 对适用任务加载固定版本 `$nature-figure`，再由 `$modern-scientific-figure` 统一协调；
4. 按需分流到算法语义、科研插图、图库参考和视觉审查 Skill；
5. 由 Python renderer 实际生成 PNG、SVG、PDF，打开图片并在论文预期尺寸检查；
6. 交付图片、完整源码、配置、输入/manifest、Design Receipt 和复现说明。

流程图、模型架构、几何/三维、网络机制等结构化插图使用 `$scientific-illustration`。收敛、预测误差、敏感度、Pareto 和空间路径等数学语义使用 `$algorithm-visualization`。用户参考图片和认可作品由 `$figure-reference-manager` 管理，生成后的图片由 `$figure-design-review` 实际审查。

项目模板和三种设计预设是可选实现素材。当前任务决定图形类型、面板数量、配色、字体和布局；不能为了套用模板改变数据或科学结构。

## 仓库结构

- `figure_studio/`：视觉系统、导出检查、算法/插图 primitives、Figure Brief、图库和作品管理。
- `.agents/skills/`：五个项目 Skill；固定版本上游 Nature Skill 按 [`docs/UPSTREAM_NATURE_FIGURE.md`](docs/UPSTREAM_NATURE_FIGURE.md) 在宿主环境安装，不复制到仓库。
- `templates/`：六类数值图、科研插图和 Nature 适配示例，作为可选 renderer 素材。
- `examples/data/`：明确标记的 `illustrative practice data`，不代表正式实验或比赛结果。
- `examples/outputs/`：已保存的示例交付包；历史报告中的测试数量和状态只代表当时证据。
- `figure_gallery/`：个人参考图库、视觉分析和已关联作品；原图与 `_generated/` 生成文件分离。
- `docs/`：当前使用说明、图库流程、上游 Skill 约束和历史证据链接。

## 安装

项目使用独立 Conda 环境，不依赖系统 Python：

```powershell
powershell -ExecutionPolicy Bypass -File tools/create_conda_env.ps1
conda activate scientific-figure-studio
```

也可以在已配置 `conda-forge` 的机器上运行 `conda env create -f environment.yml`。详细入口见 [`docs/QUICK_START.md`](docs/QUICK_START.md)。

## 正式使用入口

在 Codex 中可以显式调用：

```text
$modern-scientific-figure

请使用 Python。读取 data/results.csv 和模型说明，先写 Figure Brief，明确可验证结论、证据面板、单位和 QA 风险；
根据当前任务选择图形结构，实际导出 PNG、SVG、PDF，打开图片检查，并交付完整 plot.py、config.py、manifest 和复现说明。
```

需要时再加入 `$nature-figure`、`$algorithm-visualization`、`$scientific-illustration`、`$figure-reference-manager` 或 `$figure-design-review`。可复制的任务示例和路由说明见 [`docs/SKILLS_USAGE.md`](docs/SKILLS_USAGE.md)。

确定性执行层可以运行已有 renderer 并打包交付，但不能代替宿主 Agent 调用 Nature Skill：

```powershell
python tools/run_figure_task.py `
  --renderer path/to/plot.py `
  --brief path/to/figure_brief.json `
  --output-dir path/to/candidate `
  --data-path path/to/data.csv `
  --manifest-path path/to/data_manifest.json `
  --version-status candidate
```

如果 Figure Brief 使用了 Nature references，按 [`docs/UPSTREAM_NATURE_FIGURE.md`](docs/UPSTREAM_NATURE_FIGURE.md) 安装并验证固定上游目录，再显式提供 `--nature-skill-root`。runner 的 `design_receipt.json` 记录执行 provenance，不伪装成宿主 Skill 调用证据。

## 可选模板示例

只想快速查看已有 practice renderer 时，可以运行：

```powershell
python templates/convergence/plot.py
python tools/generate_examples.py
```

这只是模板使用示例，不是所有新任务的默认入口。模板的完整目录、数据字段和输出位置见 [`design_system/figure_examples.md`](design_system/figure_examples.md) 与各模板 README。所有示例数据均不代表正式科研结论。

## 参考图库和认可作品

将图片放入 `figure_gallery/00_inbox/` 后，可运行：

```powershell
python tools/update_gallery.py
```

扫描会记录路径、尺寸、哈希等文件事实；只有 Agent 实际打开图片并提供 view receipt 后，才能记录视觉观察。图库只提供匹配的设计参考，不强制复用旧布局，也不会自动推断用户偏好、科学结论或第三方图片授权。详见 [`docs/GALLERY_WORKFLOW.md`](docs/GALLERY_WORKFLOW.md)。

正式任务先生成 workspace/candidate。用户明确认可后才提升为 accepted：

```powershell
python tools/manage_figure_work.py accept `
  --candidate-dir path/to/candidate `
  --accepted-dir path/to/accepted `
  --user-note "用户明确认可这版设计"

python tools/manage_figure_work.py clone `
  --accepted-dir path/to/accepted `
  --workspace-dir path/to/new-workspace
```

Round 04 Design A 是用户认可的算法收敛图个人参考案例；它保留适用范围、practice-data 声明和复用限制，不是顶刊认证、全局模板或所有图的默认设计。记录见 [`figure_gallery/05_my_work/round_04_design_a_accepted/accepted_reference_case.md`](figure_gallery/05_my_work/round_04_design_a_accepted/accepted_reference_case.md)。

## 能力边界

- 没有数据、结构定义、变量含义或不确定性依据时，Agent 必须标记未知，不能凭空生成结果或置信区间。
- 自动测试只能证明相应代码/接口状态，不能替代科学内容检查、实际图片审查或用户审美验收。
- 当前 Python 工作流交付静态、可编辑、可复现 Figure；宿主 Codex 的 Skill 自动发现和真实加载状态需在实际宿主环境单独确认。
- 历史 P0/P1/Phase 2/Phase 3 文档和测试报告只记录当时状态，不是新任务的主要指令来源。

## 验证

```powershell
python tools/validate_skills.py
conda run --no-capture-output -n scientific-figure-studio pytest -q
conda run --no-capture-output -n scientific-figure-studio ruff check .
```

测试、视觉审查、用户认可和个人收藏必须在报告中分开说明；不要因为 pytest、Ruff 或导出成功就宣称 Figure 达到顶刊视觉品质。
