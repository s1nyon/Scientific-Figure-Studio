# 算法收敛曲线模板

这是明确标记的 `illustrative practice data` 示例，不代表任何比赛或科研结果。

运行：

```powershell
python templates/convergence/plot.py
```

输出目录：`examples/outputs/fig_01_convergence/`。

图中细虚线表示输入的当前目标值，实线表示按 manifest 中 `objective_direction`（`minimize` 或 `maximize`）计算的历史最优值。算法颜色来自 `config.py`，用户可以修改 `PRIMARY_COLOR`、`LINE_WIDTH`、`FONT_SIZE`、`FIGURE_WIDTH`、坐标范围和图例位置。没有重复实验列，因此没有绘制波动区间。

正式使用时，请提供算法、迭代、目标值和目标方向，并在 manifest 中记录必要的数据处理。
