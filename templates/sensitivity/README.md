# 灵敏度分析与参数影响模板

这是明确标记的 `illustrative practice data` 示例，不代表任何比赛或科研结果。

运行：

```powershell
python templates/sensitivity/plot.py
```

左面板展示单参数响应曲线，右面板展示同一练习数据中的二维参数响应。热力图的 0 中心值来自 manifest，使用发散色图表达正负变化；没有观测的网格不会被自动插值填充。

修改 `config.py` 可以调整画布、配色、线宽、字号、色图和中心值。正式使用时请填写真实参数单位、响应指标定义和参考值。
