# 测试与视觉验收报告

验收日期：2026-09-22  
项目目录：`E:\code\Scientific_Figure_Studio`  
数据状态：全部示例输入均明确标记为 `illustrative practice data`，不代表正式比赛、实验或用户模型结果。

## 环境

所有绘图、测试和 Skill 校验均通过 Conda 环境 `scientific-figure-studio` 运行：

- Python 3.11.16
- Matplotlib 3.11.2，NumPy 2.4.6，Pandas 3.0.6
- Pillow 12.3.0，PyYAML 6.0.3，pypdf 6.19.0
- 项目字体解析报告的英文、中文和数学字体均有可用回退；中文字体测试通过。

## 自动验证

以下检查均在本轮实际执行：

| 检查 | 结果 |
| --- | --- |
| `conda run -n scientific-figure-studio python -m pytest -q` | **PASS：84 passed；提交后复跑 19.64s** |
| `conda run -n scientific-figure-studio python -m ruff check .` | **PASS：All checks passed** |
| `conda run -n scientific-figure-studio python tools/validate_skills.py` | **PASS：Validated 5 project Skill(s)** |
| `python tools/generate_examples.py` | **PASS：fig_01–fig_06 全部重新渲染** |
| `python tools/generate_phase2_examples.py` | **PASS：fig_07–fig_10 全部重新渲染** |
| `python tools/update_gallery.py` | **PASS：空图库扫描，0 张图片，0 个待分析项** |
| 10 个 PNG/SVG/PDF 交付检查 | **PASS：PNG 非空、SVG 可解析、PDF 均为 1 页** |

测试覆盖样式隔离、字体、数据校验、导出覆盖保护、manifest 状态和外部路径、最小化/最大化收敛、可选数据 split、Pareto 目标方向、图库增量/哈希/重复/手动评价保护、插图结构校验、五个项目 Skill 的元数据与引用路径，以及 Nature 固定版本适配器。

## Nature 上游实际验证

上游固定为 [`lth0/codexSkill@1930963cbc004da9ac8e3af7944d4f0a3488d3e1`](https://github.com/lth0/codexSkill/tree/1930963cbc004da9ac8e3af7944d4f0a3488d3e1)。完整目录安装到本机用户 Skill 目录后，验证结果为：

- commit 精确匹配：`1930963cbc004da9ac8e3af7944d4f0a3488d3e1`
- 完整文件数：30；包含 `SKILL.md`、README、11 个 references、15 个 PNG 资源、evals 和 `.gitignore`
- 未发现可识别的 `LICENSE`、`COPYING` 或 `NOTICE`，因此仓库采用固定 SHA 安装器，不把上游文件复制进公开项目
- `fig_07` 的 [`nature_context.json`](../examples/outputs/fig_07_nature_adapter/nature_context.json) 实际记录了 commit、完整树数量，并读取了 `SKILL.md`、`figure-contract.md`、`common-patterns.md`、`qa-contract.md` 四个上游文件及其哈希
- 项目适配器实际参与了 `fig_07` 的 Python 绘图；上游 R 轨道保留在安装内容中，但本项目正式绘图、预览、导出和 QA 统一使用 Python

本地完整树读取、校验和适配器参与绘图已经验证；当前 Codex 进程是否刷新并自动发现新安装的 `nature-figure` Skill 尚未验证，不能将其混写为宿主运行时动态 Skill 调用成功。

## 导出文件检查

每个目录均实际包含 PDF、SVG、PNG、`plot.py`、`config.py`、`data_manifest.json`、README、`figure.manifest.json`、`generation_manifest.json` 和必要输入文件。

| 图目录 | PNG 像素尺寸 | SVG text 节点 | PDF 页数 |
| --- | ---: | ---: | ---: |
| `fig_01_convergence` | 1860 × 1230 | 21 | 1 |
| `fig_02_prediction` | 1860 × 1530 | 33 | 1 |
| `fig_03_sensitivity` | 2160 × 1140 | 43 | 1 |
| `fig_04_pareto` | 1860 × 1290 | 22 | 1 |
| `fig_05_spatial` | 2040 × 1380 | 28 | 1 |
| `fig_06_composite` | 2160 × 1530 | 50 | 1 |
| `fig_07_nature_adapter` | 2040 × 1290 | 20 | 1 |
| `fig_08_illustration_flowchart` | 2160 × 1290 | 16 | 1 |
| `fig_09_illustration_architecture` | 2160 × 1080 | 11 | 1 |
| `fig_10_illustration_composite` | 2160 × 1530 | 42 | 1 |

## 实际视觉检查

十张最终 PNG 均已用本地图片查看器打开：

- `fig_01`：当前目标、历史最优值和三种算法可区分；没有无依据的波动带。
- `fig_02`：训练/验证/测试、残差零线和测试指标均清楚；没有无依据的预测区间。
- `fig_03`：曲线和二维响应图分面清楚；发散色图以 0 为中心；底部练习数据说明已与 x 轴标题分离。
- `fig_04`：真实输入行计算非支配关系；可行集、前沿和关键方案标签层级清楚。
- `fig_05`：障碍物、路线、起点、终点和方向关系清楚，坐标保持等比例，并明确为二维模拟平面。
- `fig_06`：主结果、残差和参数证据面板来自同一练习场景，面板标签和说明没有遮挡。
- `fig_07`：Nature 适配图保留上游工作流参与记录，标题、图例、坐标和示例数据状态可读。
- `fig_08`：流程节点、连接、`pass/review/update` 分支和回路语义可读，箭头没有被节点覆盖。
- `fig_09`：架构图只绘制输入 JSON 声明的五个模块和四条连接；两端未裁切，连接箭头和标签清楚。
- `fig_10`：量化曲线、机制示意图和证据曲线组合排版可读，顶部示例说明保留，未冒充实验结果。

另外实际运行并检查了中文、英文、数字和数学符号字体测试；没有缺字方框或明显裁切。

## 配置生效与图库保护

- 实际修改 `fig_08` 输出目录中的 `config.py`：`FIGURE_WIDTH` 从 7.20 改为 7.80，PNG 宽度由 2160 变为 2340；随后重新运行生成器恢复规范配置并再次渲染为 2160 宽度。
- 图库扫描实际处理空目录，未创建或覆盖任何用户原图；自动索引新增视觉分析状态字段。自动测试验证重新扫描不会覆盖手动 `user_evaluation`、收藏、标签和显式视觉分析记录。
- 正式数据路径支持 manifest 中的外部绝对路径和 SHA-256 provenance；本轮没有提供真实比赛/实验数据，因此没有声称正式结果。

## 未验证与限制

- 宿主 Codex 的动态 Skill 索引刷新和 `$nature-figure` 运行时显式调用仍需在重新加载项目 Skills 的宿主环境中确认；本地固定目录加载和实际适配绘图已验证。
- 当前个人图库没有用户新增图片，因此没有产生任何个人审美结论；视觉分析字段对新图片默认保持 `not_analyzed`。
- 四类新插图使用的是明确标记的示例结构/练习数据。真实模型架构、几何约束、三维空间数据和正式研究数据需要用户提供后再绘制。
