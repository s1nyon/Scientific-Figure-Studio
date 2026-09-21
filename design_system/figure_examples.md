# 示例图与源码索引

示例使用明确标记的 `illustrative practice data`，不代表比赛结果。每个目录同时保存源代码、配置、数据说明、PNG、SVG 和 PDF。

| 图 | PNG 预览 | 可运行源码 | 重点 |
| --- | --- | --- | --- |
| 收敛曲线 | `examples/outputs/fig_01_convergence/figure.png` | `examples/outputs/fig_01_convergence/plot.py` | 当前目标值与历史最优值分层 |
| 预测与误差 | `examples/outputs/fig_02_prediction/figure.png` | `examples/outputs/fig_02_prediction/plot.py` | train/validation/test 与残差 |
| 灵敏度 | `examples/outputs/fig_03_sensitivity/figure.png` | `examples/outputs/fig_03_sensitivity/plot.py` | 参数曲线与有中心值的发散热力图 |
| Pareto | `examples/outputs/fig_04_pareto/figure.png` | `examples/outputs/fig_04_pareto/plot.py` | 方向感知的非支配解 |
| 空间路径 | `examples/outputs/fig_05_spatial/figure.png` | `examples/outputs/fig_05_spatial/plot.py` | 障碍物、节点、路线和等比例坐标 |
| 综合图 | `examples/outputs/fig_06_composite/figure.png` | `examples/outputs/fig_06_composite/plot.py` | 一个主面板与两块相关证据 |

六张图由 `python tools/generate_examples.py` 重新生成。正式数据替换时，复制相应目录作为工作副本，更新 `data_manifest.json` 和 `config.py`，不要把练习数据当作正式结论。
