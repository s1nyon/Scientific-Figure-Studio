# 测试与视觉验收报告

验收日期：2026-09-21  
项目目录：`E:\code\Scientific_Figure_Studio`  
数据状态：六类示例均为 `illustrative practice data`，不代表比赛或科研结果。

## 环境

所有命令均在独立 Conda 环境 `scientific-figure-studio` 中运行，没有调用系统 Python：

- Python 3.11.16：`C:\Users\Administrator\miniconda3\envs\scientific-figure-studio\python.exe`
- Matplotlib 3.11.2，NumPy 2.4.6，Pandas 3.0.6，Pillow 12.3.0，PyYAML 6.0.3，pypdf 6.19.0。
- 实际字体：英文 Arial，中文 Microsoft YaHei，数学 DejaVu Sans；字体报告 `missing=()`、`warnings=()`。

## 自动测试

以下命令均实际执行并通过：

| 命令 | 结果 |
| --- | --- |
| `conda run -n scientific-figure-studio pytest -q` | **PASS：50 passed** |
| `conda run -n scientific-figure-studio ruff check .` | **PASS：All checks passed** |
| `conda run -n scientific-figure-studio python tools/validate_skills.py` | **PASS：Validated 4 project Skill(s)** |
| `conda run -n scientific-figure-studio python tools/generate_examples.py` | **PASS：六个交付目录均重新生成** |
| `pytest tests/test_font_render.py --basetemp=tmp_font_pytest` | **PASS：中文/英文/数学符号 PNG 非空** |
| 配置修改验收 | **PASS：基线 1860×1230，修改后 1980×1230，像素哈希不同** |

测试覆盖了样式隔离、字体回退、输入数据校验、导出覆盖保护、PNG/SVG/PDF 文件检查、运行最优值、方向感知 Pareto、六类模板契约、图库空目录/哈希/重复/收藏筛选，以及 Skill 元数据和引用路径。

## 导出文件检查

六张图的 PNG 均通过非空检查，SVG 有根节点和文本结构，PDF 均为一页且可读取：

| 图目录 | PNG 像素尺寸 | SVG 文本节点 | PDF 页数 |
| --- | ---: | ---: | ---: |
| `fig_01_convergence` | 1860 × 1230 | 21 | 1 |
| `fig_02_prediction` | 1860 × 1530 | 33 | 1 |
| `fig_03_sensitivity` | 2160 × 1140 | 48 | 1 |
| `fig_04_pareto` | 1860 × 1290 | 22 | 1 |
| `fig_05_spatial` | 2040 × 1380 | 28 | 1 |
| `fig_06_composite` | 2160 × 1530 | 50 | 1 |

每个目录还包含复制后的 `plot.py`、`config.py`、`data_manifest.json`、README、`figure.manifest.json` 和 `generation_manifest.json`。

## 实际视觉检查

已用本地图片查看器打开六张完整 PNG，并制作缩小接触页复查论文插入尺寸下的信息层次；另实际打开中文字体测试图。

- `fig_01_convergence`：当前目标值用细虚线、历史最优值用实线，三种算法可区分，图例未遮挡数据；没有重复实验数据，因此没有波动区间。
- `fig_02_prediction`：训练、验证、测试通过颜色和标记区分，残差零线和测试 RMSE/MAE 清楚；没有无依据的预测区间。
- `fig_03_sensitivity`：参数曲线与二维响应图分面，发散色图中心为 0，色条和单位可读。
- `fig_04_pareto`：可行解以灰色弱化，非支配前沿单独计算并标出，关键方案标签没有超出画布。
- `fig_05_spatial`：障碍物、路线、起点、终点和方向关系清楚，坐标保持等比例；图中明确是二维模拟平面。
- `fig_06_composite`：主面板宽于两块证据面板，`(a)/(b)/(c)` 标签与标题分离，三个面板来自同一模拟场景。
- 中文字体图的标题“中文字体测试”、中文轴标签、英文数字和 `$E$` 均正常显示，没有缺字方框或明显裁切。

视觉检查中曾发现综合图面板标签与左对齐标题重叠，已修改模板源码为居中标题并重新生成、重新打开确认修复。没有直接修改任何最终 PNG。

## 未验证与限制

- 本地 validator 验证了 Skill 文件结构、元数据和引用路径，但没有声称宿主 Codex 已自动发现或实际加载这些项目 Skills；该行为需要在宿主安装本项目目录后再做一次显式调用测试。
- 当前个人图库没有用户收藏图片；空图库路径、增量扫描、哈希去重和测试图片索引已通过自动测试，但没有把测试图片伪装成用户偏好。
- 示例数据是练习数据，统计不确定性、真实地理坐标、正式实验结论和比赛数据尚未提供，因此相关模板不会自行生成这些内容。
