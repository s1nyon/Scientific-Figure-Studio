# 快速开始

Scientific Figure Studio 的正式入口是 Nature-first Python 工作流；下面先给出新任务流程，再给出已有模板的快速运行方式。

## 1. 准备环境

在 PowerShell 中进入项目根目录：

```powershell
powershell -ExecutionPolicy Bypass -File tools/create_conda_env.ps1
conda activate scientific-figure-studio
python --version
python -c "import sys; print(sys.executable)"
```

Python 路径应位于 `scientific-figure-studio` Conda 环境中，而不是系统 Python。

## 2. Nature-first 正式绘图流程

每个正式任务都按科学任务选择图形结构，不先套用固定模板：

1. **打开项目并检查能力发现。** 确认 Codex 能发现项目 `.agents/skills/`，并知道固定 `$nature-figure` 是否已按 [`UPSTREAM_NATURE_FIGURE.md`](UPSTREAM_NATURE_FIGURE.md) 安装。宿主无法确认时要标记为未验证。
2. **提供任务材料。** 给出真实数据或结构输入、模型/实验说明、字段、单位、目标方向、数据集划分、已有图片和明确的科学问题。练习输入必须写明 `illustrative practice data`。
3. **调用统一入口。** 使用 `$modern-scientific-figure`，要求先建立 Figure Brief：可验证结论、主要证据、必要辅助证据、预期尺寸、未知信息和 QA 风险。
4. **按需选择专业能力。** 适用的数值图或综合 Figure 先加载 `$nature-figure`；收敛/误差/Pareto 等使用 `$algorithm-visualization`，流程/架构/几何/三维/网络使用 `$scientific-illustration`，需要参考图时才使用 `$figure-reference-manager`，生成后使用 `$figure-design-review`。
5. **选择实现。** Agent 根据科学表达目标决定单面板或多面板、图形类型、颜色和标注；只有结构匹配时才复用模板。统一执行器只运行已经写好的 Python renderer。
6. **实际生成和检查。** 导出 PNG、SVG、PDF，打开实际 PNG，在原始尺寸和论文预期插入尺寸检查裁切、层级、文字、单位、标注、颜色、图例和科学含义；发现问题回到 `plot.py`/`config.py` 修复，再重新导出。
7. **交付复现包。** 提供图片、完整 `plot.py`、可修改 `config.py`、必要输入、`data_manifest.json`、Figure Brief、Design Receipt、运行 README 和验证结果。
8. **自然语言精修和验收。** 局部修改先保存快照并生成 Before/After；普通渲染只生成 workspace/candidate，只有用户明确评价后才执行 `accept` 保存认可作品。

可复制的任务提示：

```text
$modern-scientific-figure

请使用 Python 读取 data/results.csv 和 model_notes.md。先检查字段、单位、目标方向和数据状态，
建立 Figure Brief，写出一条数据能够支持的结论、证据关系、未知信息和 QA 风险；按当前任务自主选择
图形结构，不强行使用模板。实际生成 PNG、SVG、PDF，打开图片检查并修复问题，交付完整 plot.py、
config.py、data_manifest.json、Figure Brief、Design Receipt 和可复现运行说明。
```

## 3. 使用统一执行器

当已有 renderer 和 Figure Brief 后，可以用 staging 运行并打包交付：

```powershell
python tools/run_figure_task.py `
  --renderer path/to/plot.py `
  --brief path/to/figure_brief.json `
  --output-dir path/to/candidate `
  --data-path path/to/data.csv `
  --manifest-path path/to/data_manifest.json `
  --review-status not_reviewed `
  --host-skill-invocation-status not_verified `
  --version-status candidate
```

如果 Brief 声明了 Nature references，再增加：

```powershell
  --nature-skill-root "$env:USERPROFILE\.codex\skills\nature-figure"
```

`--nature-skill-root` 让 runner 检查已安装的固定目录；它不代表当前 Codex 宿主已经动态加载或调用了 Nature Skill。真实宿主调用、图片查看和精修必须分别记录。

## 4. 模板使用示例（可选）

只想运行仓库内的 practice renderer 时：

```powershell
python templates/convergence/plot.py
python tools/generate_examples.py
```

这是模板示例，不是所有新 Figure 的默认入口。已有模板会在 `examples/outputs/` 生成 PDF、SVG、PNG 和源码快照；替换正式数据前，先检查字段、单位、目标方向和 manifest，不得把练习结果当作比赛结果。

Nature 适配示例需要先安装并验证固定目录：

```powershell
python tools/install_nature_figure.py --destination "$env:USERPROFILE\.codex\skills\nature-figure"
python tools/verify_nature_figure.py --path "$env:USERPROFILE\.codex\skills\nature-figure"
python templates/nature_adapter/plot.py
```

## 5. 常见任务提示

### 根据已有图片重新设计

```text
$modern-scientific-figure

请打开 input/old_figure.png，结合 data/results.csv 重新评估科学结论、证据层级、图形类型和布局。
不要只在旧 plot.py 上换字体和颜色；说明哪些设计可保留、哪些结构需要重建，随后用 Python 交付新图和完整源码。
```

### 指定个人图库案例

```text
$modern-scientific-figure $figure-reference-manager

请实际打开 figure_gallery/02_algorithm/reference.png，并只提取与当前任务匹配的布局、层级、标注或留白方法。
不要复制参考图数据、结论或私人内容；把视觉参考与代码参考分开记录。
```

### 生成模型架构或流程图

```text
$scientific-illustration

请根据 input/graph.json 中给出的节点、连接、方向和标签绘制架构图。不要自行增加模块、箭头、坐标或性能结论，
交付 Python 源码、config.py、结构 manifest、PNG、SVG、PDF，并实际打开 PNG 检查。
```

### 修改已生成图片并查看前后对比

```text
$figure-design-review

请先快照当前 PNG、plot.py 和 config.py。将图例移到不遮挡数据的位置，重新运行源码导出全部格式，
打开修改后图片，并用 Python 生成 Before/After 对比；不要直接编辑 PNG。
```

### 保存用户认可作品

用户明确评价后再运行：

```powershell
python tools/manage_figure_work.py accept `
  --candidate-dir path/to/candidate `
  --accepted-dir path/to/accepted `
  --user-note "用户明确认可这版设计"
```

没有用户明确认可时，不把新图放入 favorites 或 `05_my_work`。

## 6. 验证

```powershell
python tools/validate_skills.py
conda run --no-capture-output -n scientific-figure-studio pytest -q
conda run --no-capture-output -n scientific-figure-studio ruff check .
```

测试通过、科学检查、图片已打开、用户验收和个人收藏是不同状态，必须分开报告。中文字体缺失时记录降级结果，不把字体文件直接复制进项目。
