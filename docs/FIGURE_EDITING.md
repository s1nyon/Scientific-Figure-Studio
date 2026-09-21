# 亲自修改图表

每个示例目录中，`config.py` 是最常用的手动修改入口。修改后从项目根目录运行对应源码：

```powershell
python examples/outputs/fig_01_convergence/plot.py
```

也可以运行模板源码：

```powershell
python templates/convergence/plot.py --output-dir examples/outputs/fig_01_convergence
```

## 常用参数

以 `examples/outputs/fig_01_convergence/config.py` 为例：

```python
PRIMARY_COLOR = "#166A8F"  # 主曲线颜色
LINE_WIDTH = 2.0            # 历史最优曲线线宽
FONT_SIZE = 8.5             # 轴、刻度和图例的基础字号
FIGURE_WIDTH = 6.20         # 英寸
FIGURE_HEIGHT = 4.10        # 英寸
LEGEND_LOCATION = "upper right"
```

修改 `ALGORITHM_COLORS` 可以单独控制算法颜色；修改 `Y_LIMITS` 可以调整显示范围，但不能用坐标范围隐藏不利数据。改动后重新运行，再打开 `figure.png` 检查，SVG/PDF 也会同步更新。

预测、灵敏度、Pareto、空间和综合图的 `config.py` 采用相同原则：先修改颜色、字号、线宽、画布、图例和坐标参数，再运行对应 `plot.py`。科学计算参数、目标方向、数据字段和单位必须同步写入 manifest，不能只改图的外观。

## 导出和版本一致性

源码会同时导出 PNG、SVG、PDF，并生成 `figure.manifest.json`。不要直接编辑最终 PNG；如果需要微调，修改 `plot.py` 或 `config.py` 后重新运行。交付前确认图片、源码和 manifest 是同一次生成结果。
