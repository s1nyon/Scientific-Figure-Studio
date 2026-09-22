# 亲自修改图表

正式图表的最终修改应回到 Python 源码和配置。图片查看用于发现问题，不能替代可复现源码；局部精修也不意味着所有新任务都必须沿用上一版构图。

## 修改入口

每个交付目录中，`config.py` 是常用的手动修改入口。从项目根目录运行对应源码：

```powershell
python examples/outputs/fig_01_convergence/plot.py
```

也可以运行模板源码并指定现有输出目录：

```powershell
python templates/convergence/plot.py --output-dir examples/outputs/fig_01_convergence
```

常见视觉参数示例：

```python
PRIMARY_COLOR = "#C65D3B"
LINE_WIDTH = 2.2
FONT_SIZE = 8.5
FIGURE_WIDTH = 6.6
FIGURE_HEIGHT = 4.10
LEGEND_LOCATION = "upper right"
```

这些只是现有 renderer 的配置示例，不是所有图都必须使用的颜色、字号或画布。应根据当前数据密度、科学语义和目标插入尺寸调整。

修改 `ALGORITHM_COLORS` 可以控制算法颜色；修改 `Y_LIMITS` 不能用坐标范围隐藏不利数据。预测、灵敏度、Pareto、空间和综合图也遵循同一原则：颜色、字号、线宽、画布和图例属于可调视觉参数，科学计算参数、目标方向、字段和单位必须同步写入 manifest，不能只改外观。

流程图、架构图和组合插图必须修改源码输入和 `config.py` 后重新渲染。节点、连接、坐标、量化数据和机制标签应来自保存的结构化输入，不要在源码中偷偷增加用户没有提供的模块、边、坐标或结论。

## 自然语言局部精修

收到“移开图例”“增大标签”“换成双栏布局”等反馈时：

1. 先保存当前 PNG、SVG/PDF、`plot.py`、`config.py` 和 manifest 快照；
2. 判断反馈是局部排版问题，还是需要重新设计科学证据层级；
3. 修改源码或配置，不直接编辑最终 PNG；
4. 重新运行源码，导出全部格式并生成 Before/After 对比；
5. 打开修改后图片，在原始尺寸和预期论文插入尺寸检查数据、标签、单位、裁切和可读性；
6. 记录修改前后版本、输入哈希和仍未验证内容。

如果用户要求整体重新设计，应从当前科学任务、数据和必要参考图重新判断图形类型、面板层级和布局，而不是只给上一版 `plot.py` 换颜色和字体。简单局部修改不需要重新开展完整 Figure 设计。

## 导出和版本一致性

源码应同时导出 PNG、SVG、PDF，并生成对应 manifest。不要直接修补最终位图；需要微调时修改 `plot.py` 或 `config.py`，重新运行后再查看全部格式。交付前确认图片、源码、配置、输入和 manifest 来自同一次生成。

候选图和 workspace 可以在不覆盖已有文件的前提下重新生成；已认可作品只能通过从 accepted 目录派生新的 workspace 继续修改，普通渲染、`--overwrite` 和快照恢复不能改写认可目录。
