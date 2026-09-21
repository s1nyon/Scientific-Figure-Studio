# 多面板综合结果图模板

这是明确标记的 `illustrative practice data` 示例。三个面板来自同一份模拟研究场景：主面板呈现总体性能，右上面板呈现残差证据，右下面板呈现参数影响。

运行：

```powershell
python templates/composite/plot.py
```

也可以指定交付目录：

```powershell
python templates/composite/plot.py --output-dir examples/outputs/fig_06_composite
```

修改 `config.py` 中的 `ALGORITHM_COLORS`、`LINE_WIDTH`、`FONT_SIZE`、`FIGURE_WIDTH`、`FIGURE_HEIGHT` 和图例位置后重新运行。正式数据应替换为具有相同字段定义的数据，并同步更新 `data_manifest.json`。
