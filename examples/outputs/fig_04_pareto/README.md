# 多目标优化与帕累托前沿模板

这是明确标记的 `illustrative practice data` 示例，不代表任何比赛或科研结果。

运行：

```powershell
python templates/pareto/plot.py
```

灰色散点是可行解，蓝色折线只连接根据目标方向计算出的非支配解，橙色描边表示输入数据中标记为关键方案的点。当前两个目标都是最小化；如果正式问题有最大化目标，应同步修改 `OBJECTIVE_DIRECTIONS` 和 manifest。

任意散点不能直接称为帕累托前沿。正式使用时请确认目标方向、可行性定义、重复方案和关键方案标记均来自真实数据。
