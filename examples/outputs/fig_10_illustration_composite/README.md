# 图表与机制示意组合 Figure 模板

这是 `illustrative practice data` 与 `illustrative example structure` 示例，不代表实验结果。左侧量化面板读取 CSV，右上机制面板严格读取独立 JSON 的节点和连接，右下显示 CSV 中实际提供的 residual 证据行；模板不会把结构面板伪装成统计证据。

运行：

```powershell
python templates/illustration/composite/plot.py
```

输出目录为 `examples/outputs/fig_10_illustration_composite/`。修改 `config.py` 中的画布、颜色、线宽、字号或结构面板范围后重新运行，交付目录应同时保留源码、配置、两个输入文件、manifest 和 PDF/SVG/PNG。
