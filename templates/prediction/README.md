# 预测结果与误差分析模板

这是明确标记的 `illustrative practice data` 示例，不代表任何比赛或科研结果。

运行：

```powershell
python templates/prediction/plot.py
```

图的上方面板同时展示观测值和按 `split` 区分的预测值，下方面板展示真实计算的残差。训练、验证和测试数据不会被混合成一个无标签序列；RMSE 和 MAE 只使用测试行计算。当前数据没有预测区间依据，因此图中没有虚构的置信带。

修改 `config.py` 可以调整颜色、线宽、字号、画布和图例。正式使用时，替换数据文件并同步更新字段单位和 manifest。
