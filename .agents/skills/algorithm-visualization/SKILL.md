---
name: algorithm-visualization
description: Use when a mathematical modeling figure involves convergence, algorithm comparison, prediction errors, residuals, sensitivity, robustness, multi-objective optimization, Pareto solutions, spatial paths, or network structure.
---

# Algorithm Visualization

这是算法结果图的数学表达层。先读项目根目录的 [AGENTS.md](../../../AGENTS.md)，再把目标方向、数据分组、统计依据和可支持的结论写清楚；字体、配色和导出标准复用 `figure_studio`，不要在本 Skill 中重新定义视觉系统。

## 适用场景

- 需要展示算法迭代、收敛速度、性能比较或消融结果。
- 需要绘制预测值、残差、误差指标、灵敏度、鲁棒性或参数影响。
- 需要计算非支配解、帕累托前沿、空间路径或网络方案。

## 不适用场景

- 只有颜色、留白、字体和排版问题时，使用 `figure-design-review`。
- 需要从用户收藏图片生成索引和设计笔记时，使用 `figure-reference-manager`。
- 没有数据或变量定义、只想凭空生成“算法优势”时，先补齐 Figure Brief；不得绘图冒充证据。

## 数学检查流程

1. 明确每个字段的变量、单位、数据集划分和目标方向。把最小化和最大化写进 manifest 与图注。
2. 收敛图同时区分输入的当前目标值与按目标方向计算的历史最优值；没有重复实验数据就不画波动区间。
3. 预测图分开训练、验证和测试。MAE、RMSE 等指标只在它们声明的样本集合上计算，并让残差定义与图轴一致。
4. 灵敏度图标出参数范围、单位和响应定义；只有存在真实中心值时才使用发散色图和零点中心。
5. Pareto 图按每个目标的实际方向计算支配关系。任意散点排序或连线不能被称为 Pareto 前沿。
6. 空间图保留坐标比例、节点角色、障碍物和路线方向；地理数据必须记录坐标系和距离单位。
7. 不确定性区间只能来自重复实验、模型或统计估计。若依据不存在，显示事实数据并明确未绘制区间。
8. 将计算和绘图分开，保留重要变换；运行代码并查看实际图片，确认视觉强调没有改变数学含义。

## 交付契约

交付 `plot.py`、`config.py`、`data_manifest.json` 和三种导出格式。manifest 至少记录目标方向、数据状态、字段单位、计算方法和未支持的结论。标题、颜色或线型不能暗示输入数据没有支持的算法优劣。

## 常见错误

| 错误 | 修复 |
| --- | --- |
| 把当前目标值直接称为历史最优 | 使用方向感知的累计最小或最大，并同时保留当前值。 |
| 用任意折线表示 Pareto 前沿 | 先计算支配掩码，再只标注非支配解。 |
| 没有重复实验却画置信带 | 删除区间并在 manifest 中说明没有依据。 |
| 把训练、验证、测试混为一条指标 | 分组读取、分别标识、按声明的数据集计算指标。 |

