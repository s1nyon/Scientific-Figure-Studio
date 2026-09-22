# Skills 使用说明

项目 Skills 位于 `.agents/skills/`。在支持项目级 Skills 的 Codex 环境中，可以显式调用 `$skill-name`；也可以直接描述任务，让系统根据 `description` 自动发现。显式调用示例：

```text
$modern-scientific-figure

请读取 data/results.csv，绘制适合数学建模论文的预测结果图。先检查字段和单位，检索个人图库中相关案例，使用项目统一视觉系统，并交付完整 Python 源码、config.py、data_manifest.json、PNG、SVG 和 PDF。
```

算法专项：

```text
$algorithm-visualization

请根据 data/convergence.csv 绘制最小化目标的收敛图。区分当前目标值与历史最优值，说明是否有重复实验依据，不要凭曲线外观宣称算法更优，并交付可运行源码。
```

视觉审查：

```text
$figure-design-review

请打开 examples/outputs/fig_06_composite/figure.png，按论文插入尺寸检查裁切、字体、图例、面板间距、颜色层级和数据表达；发现问题就修改对应 plot.py 并重新生成。
```

图库管理：

```text
$figure-reference-manager

请扫描 figure_gallery/00_inbox，分析能够实际打开的新增科研图片，生成设计档案并更新索引。保留原图，不编造用户评价；无法视觉分析的项目要标记为未验证。
```

结构化科研插图：

```text
$scientific-illustration

请根据保存的 JSON 节点、连接和坐标绘制流程图/模型架构/几何或三维示意图；不要把架构请求改成普通折线图，不要自行添加模块或数据。使用 Python、figure_studio.illustrations 和完整源码/config/manifest 交付，并实际查看 PNG。
```

固定 Nature 上游的安装、完整目录校验和许可证限制见 [`docs/UPSTREAM_NATURE_FIGURE.md`](UPSTREAM_NATURE_FIGURE.md)。本项目的 `templates/nature_adapter/plot.py` 只有在验证后的固定目录存在时才会运行。

调用任何正式绘图 Skill 时，都要遵守项目根目录 `AGENTS.md`：图片和源码必须同步交付，正式图表必须实际运行并查看输出，数据不足时明确报告。

当前仓库已验证五个项目 `SKILL.md` 的文件、元数据、引用目录和本地辅助结构；宿主 Codex 的运行时自动发现/显式调用行为需在安装本项目 Skills 的宿主环境中再确认。
