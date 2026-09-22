# Skills 使用说明

## 统一 Nature-first 入口

Scientific Figure Studio 的统一项目入口是 `$modern-scientific-figure`。对于适用的普通数值图、论文级 Figure 和数据图表组合图，先显式加载固定版本 `$nature-figure`，再由项目入口建立 Figure Brief、分流专业能力、选择 Python renderer、实际运行、打开图片和交付源码。

```text
$nature-figure
$modern-scientific-figure

请使用 Python。读取 data/results.csv 和模型说明，先写 Figure Brief，明确一条可验证结论、主要证据、
必要辅助证据、单位、未知信息和 QA 风险；按当前科学任务自主选择图形结构，不强行使用固定模板。
实际导出 PNG、SVG、PDF，打开 PNG，在论文预期尺寸检查后交付完整源码、配置、manifest 和复现说明。
```

如果任务主要是流程图、模型架构、几何、三维或网络结构，使用 `$scientific-illustration`；如果同时包含量化图表，先让 `$nature-figure` 组织量化证据层级，再绘制结构面板。

## 专业 Skill 路由

- `$algorithm-visualization`：收敛、预测误差、残差、灵敏度、鲁棒性、Pareto、空间路径和网络的目标方向、分组、指标和数学语义。
- `$scientific-illustration`：流程、架构、几何、三维、网络机制和图表/示意图组合；结构必须来自保存的节点、边、坐标和标签。
- `$figure-reference-manager`：扫描个人图库、记录实际打开后的视觉观察、检索相关参考和关联认可作品；不修改原图、不编造用户评价。
- `$figure-design-review`：打开已生成图片，检查科学表达、论文尺寸可读性、多面板一致性、导出和源码精修。

不要要求每个任务调用全部 Skill。模板和三种视觉预设均为可选实现资源，当前 claim、evidence、数据密度和读者决定最终图形。

## 一个完整的执行闭环

1. 读取数据、模型/结构说明、已有图片和用户指定参考；核对字段、单位、目标方向、数据划分和不确定性依据。
2. 保存 Figure Brief：`task`、`data_sources`、`fields`、`units`、`claim`、`evidence_panels`、`archetype`、`backend`、`task_mode`、`nature_references`、`renderer`、`review_risks` 和必要的 `scientific_unknowns`。
3. 对适用的数值/综合 Figure 显式加载 `$nature-figure`；按需检索少量与科学内容、数据结构、图形类型和表达目标匹配的图库案例。指定图片必须先实际打开。
4. 评估每个辅助面板的独立证据价值；不能仅凭字段数量增加热图、柱图、初末值比较或其他面板。
5. 选择现有模板或独立 `plot.py`/`config.py`，把数据计算、视觉参数和导出分开；不得改变原始数据、模型模块或目标函数方向。
6. 用 Python 实际导出 PNG、SVG、PDF，打开图片，在原始和论文预期尺寸检查裁切、文字、图例、标注、颜色、单位、面板层级和阅读顺序。
7. 对整体问题重新评估 Figure 方案，对局部问题修改源码/配置并重新导出；交付完整源码、输入、manifest、Brief、Receipt、README 和验证结果。
8. 报告时分开写自动测试、科学检查、图片已打开、用户验收和个人收藏状态。

## Python runner 的边界和真实参数

确定性执行器只运行已经写好的 renderer、检查输入/输出并保存 provenance，不能代替宿主 Agent 调用 Nature Skill：

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

需要校验已安装固定 Nature 目录时，再提供：

```powershell
  --nature-skill-root "$env:USERPROFILE\.codex\skills\nature-figure"
```

实际可用参数还包括显式 `--overwrite`、重复的 `--review-note`、`--parent-run`、`--gallery-root` 和重复的 `--dependency`；只有确实需要时才使用。`design_receipt.json` 记录 runner 看到的 references 和执行状态，不伪装成宿主 Skill 动态调用证明。

## 可复制的最小任务示例

### 1. 从数据生成新的科研 Figure

```text
$modern-scientific-figure

请使用 Python 读取 data/results.csv。先核对字段、单位、目标方向和数据状态，写 Figure Brief；
根据一条可验证科学结论选择图形类型和面板，不要因为字段多就增加面板。实际运行并打开输出，
交付 plot.py、config.py、data_manifest.json、PNG、SVG、PDF 和复现说明。
```

### 2. 根据已有图片重新设计

```text
$modern-scientific-figure $figure-design-review

请打开 input/old_figure.png，结合 data/results.csv 重新评估 claim、证据层级、图形类型和布局。
如果是整体重设计，不要只在旧 plot.py 上换字体和颜色；说明新方案的信息组织，再用 Python 交付完整源码和全部格式。
```

### 3. 指定个人图库案例作为参考

```text
$modern-scientific-figure $figure-reference-manager

请实际打开 figure_gallery/02_algorithm/reference.png。只提取与当前任务匹配的布局、层级、标注、颜色关系或留白方法，
把视觉参考、代码参考、用户评价和科学 provenance 分开记录；不要复制参考图数据、结论或私人内容。
```

### 4. 生成模型架构或流程图

```text
$scientific-illustration

请根据 input/graph.json 中保存的节点、连接、方向、坐标和标签绘制架构图。不要自行添加模块、边、坐标或性能结论，
交付 plot.py、config.py、结构 manifest、PNG、SVG、PDF，并实际打开 PNG 检查。
```

### 5. 修改已生成图片并查看 Before/After

```text
$figure-design-review

请先快照当前 PNG、plot.py 和 config.py。将图例移到不遮挡数据的位置，重新运行源码导出全部格式，
打开修改后图片，并用 Python 生成 Before/After 对比；不要直接编辑 PNG。
```

### 6. 保存用户认可作品

只有用户明确提供认可和评价后才执行：

```powershell
python tools/manage_figure_work.py accept `
  --candidate-dir path/to/candidate `
  --accepted-dir path/to/accepted `
  --user-note "用户明确认可这版设计"
```

后续从认可作品派生工作区：

```powershell
python tools/manage_figure_work.py clone `
  --accepted-dir path/to/accepted `
  --workspace-dir path/to/new-workspace
```

## 固定 Nature 上游和验证边界

固定上游的安装、完整目录校验和许可证限制见 [`UPSTREAM_NATURE_FIGURE.md`](UPSTREAM_NATURE_FIGURE.md)。`templates/nature_adapter/plot.py` 只在验证后的目录存在时运行。Python runner 读取上游文件不等于当前 Codex 进程已经动态加载 `$nature-figure`；宿主 Skill 的发现/调用状态需单独验证。

项目本地 Skill 元数据可用以下命令检查：

```powershell
python tools/validate_skills.py
```

正式绘图的图片和源码必须同步交付；没有实际打开图片时，视觉审查标记为未验证。
