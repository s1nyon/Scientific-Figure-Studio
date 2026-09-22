# Scientific Figure Studio 第三阶段快速架构审查

审查日期：2026-09-22

## 结论摘要

当前最新 `main` 实际仍为 `670f10423c20ea31070e49582aceb0d6f1f43384`（`feat: complete phase two figure studio delivery`）。本地 `master` 与 `origin/main` 一致，工作区干净；因此本报告以该提交为真实审查基线，而不是以前的提交说明或 README 假设。

项目第二阶段已经交付了可保留的 Python 绘图库、六类数值模板、三类插图模板、固定版本 Nature 安装器、数据 manifest、图库索引和基础测试。最大的架构缺口不是缺少更多模板，而是 Nature Skill 目前只被“安装、读取、哈希记录和适配器门禁”使用，还没有证据表明它在一次真实 Codex 绘图任务中实际主导了 Figure Brief、构图、实现和视觉审查。

最小改造建议是升级现有 `modern-scientific-figure`，让它成为统一的 Codex 协调入口；不新增一个与它重叠的 `scientific-figure-studio` Skill。第一批只建立 Nature-first 的任务闭环和可追溯设计记录，保留现有模板作为可选 renderer，不重写公共绘图库。

## 1. 基线与证据

| 检查项 | 实际结果 |
| --- | --- |
| Git | `HEAD == origin/main == 670f10423c20ea31070e49582aceb0d6f1f43384`；`master` 跟踪 `origin/main`；工作区干净 |
| Conda/Python | `scientific-figure-studio` 环境；Python 3.11.16 |
| 自动测试 | `python -m pytest -q`：84 passed，20.62s（本次重新执行） |
| 静态检查 | `python -m ruff check .`：`All checks passed!` |
| 项目 Skills | `tools/validate_skills.py`：5 个 Skill 全部通过；该工具明确不验证宿主 Codex 的动态调用 |
| 上游 Nature | 固定提交 `1930963cbc004da9ac8e3af7944d4f0a3488d3e1`；30 个文件、完整树和 `SKILL.md` SHA-256 均校验通过 |
| 宿主发现 | 当前 Codex Skill 索引可以发现并读取 `nature-figure`；尚无一次独立的 `$nature-figure` 真实任务验收记录 |

第二阶段报告中记载的 `fig_01`–`fig_10` 已实际生成并查看；本次审查重新执行了自动检查，但没有把历史视觉查看记录冒充为本次重新审查的视觉验收。

依赖和许可边界：项目正式绘图依赖由 `pyproject.toml` 管理，继续使用 Python/Matplotlib/Pandas/NumPy/Pillow 等现有依赖。固定 Nature 树中未发现可识别的 `LICENSE`、`COPYING` 或 `NOTICE`；因此沿用“固定 SHA 安装到用户 Skill 目录、公开仓库不复制上游完整文件”的合规方案，不在第三阶段擅自重新打包上游资源。

## 2. Nature Skill 实际集成层级

| 层级 | 判断 | 依据 |
| --- | --- | --- |
| A. 原始 Skill 已安装 | 已完成 | `tools/nature_figure_lock.py`、`install_nature_figure.py`、`verify_nature_figure.py` 固定提交并校验完整 30 文件树 |
| B. 原始文件被项目程序读取 | 已完成 | `figure_studio.nature_adapter.build_nature_context()` 读取 `SKILL.md` 和 3 个 reference，写入 commit、文件数和哈希 |
| C. Codex 能发现原始 Skill | 当前环境已确认 | 当前 Skill catalog 可见 `nature-figure`，且本次审查已读取其正式 `SKILL.md` |
| D. 原始设计流程真实主导 Figure | 未完成 | `templates/nature_adapter/plot.py` 在读取 context 后仍直接执行固定收敛图逻辑；没有 Figure Contract、设计选择、上游参考条款到面板结构的记录，也没有真实 `$nature-figure` 任务证据 |

因此，当前准确表述是“固定 Nature Skill 已合规安装，项目适配器已读取并记录其内容，宿主当前可发现它；端到端设计主导尚未验证”。`nature_context.json` 不是原版 Skill 已影响图形设计的充分证据。

## 3. 当前能力与差异

| 领域 | 当前实现 | 最新要求 | 实际差距 | 文件范围 | 推荐处理 | 优先级 |
| --- | --- | --- | --- | --- | --- | --- |
| Nature 安装 | 固定提交安装、完整性和哈希校验，且有安装备份保护 | 保留固定版本，不追踪 main | 没有明显功能缺口 | `tools/nature_figure_lock.py`、`tools/install_nature_figure.py`、`tools/verify_nature_figure.py` | 保留，第一批只复用 | P0 保持 |
| Nature 适配 | 读取上游文本并写 context；示例能生成图 | 上游设计流程应实际进入任务设计 | 缺少 Figure Brief、设计决策和真实 Skill 调用闭环 | `figure_studio/nature_adapter.py`、`templates/nature_adapter/plot.py` | 增加薄的设计记录/验收收据，不修改上游文件 | P0 |
| 统一入口 | `modern-scientific-figure` 是文字流程，但没有明确先载入 Nature、任务路由、模式和手动覆盖 | 任务理解 → 专业 Skill → Nature 设计 → Python → 查看 → 交付 | 缺少协调职责，用户仍需自己选择多个 Skill/模板 | `.agents/skills/modern-scientific-figure/SKILL.md`、`docs/SKILLS_USAGE.md` | 升级现有 Skill，不新增重复入口 | P0 |
| 数值模板 | 六类模板和公共样式、manifest、导出模块已能运行 | 模板是可选实现素材 | 模板 `main()` 普遍固定 `overwrite=True`，容易掩盖正式版本覆盖风险 | `templates/*/plot.py`、`figure_studio/export.py` | 保留模板；改为显式覆盖或独立 run 目录 | P1 |
| 插图 | `figure_studio.illustrations` 有流程、架构、几何、网络、曲面基础绘制函数；三类插图模板已实际生成 | 支持按科学含义选流程/架构/几何/3D/网络/组合图 | 几何、3D、网络 primitive 没有独立模板和实际输出验收；不能把 Skill 文档当成验证 | `figure_studio/illustrations.py`、`templates/illustration/*`、相关 tests | 比赛需要时补最小模板和实图；不先重写公共 primitive | P2 |
| 个人图库 | 确定性扫描、哈希去重、手动评价保护、显式 Agent 分析回调已实现；空目录可处理 | 自动事实、Agent 视觉分析、用户偏好、认可作品分级 | 没有机器可证明的“图片已打开”凭据；无相关性排序、陈旧项报告、源码/认可作品关联；当前图库没有用户图片 | `figure_studio/gallery.py`、`tools/update_gallery.py`、gallery tests | 先保留保护逻辑；P1 增加轻量 review receipt、过滤/排序和 stale 报告 | P1 |
| 版本与源码 | 导出器默认不覆盖，并写输出 manifest；示例生成器有输入哈希 | 候选版本、正式作品保护、源码/配置/数据绑定 | 模板和示例生成器显式覆盖固定目录；manifest 未包含 plot/config/manifest 源码哈希，也没有 candidate/accepted 状态 | `figure_studio/export.py`、`tools/generate_examples.py`、`tools/generate_phase2_examples.py` | 用显式 output/run 目录和 source hash 解决，不引入数据库 | P1 |
| 测试 | 84 个测试、Ruff、5 个 Skill 结构校验通过 | 支持真实调用、路由、交付一致性和防覆盖 | 缺少宿主调用证据测试、统一入口契约、源文件一致性、认可作品防覆盖、三类未验证插图回归 | `tests/` | 自动测试验证可编程契约；宿主 Skill 真实调用保留手工验收记录 | P0/P1/P2 |

## 4. 应保留、调整和新增

应保留：固定 Nature 安装器和完整性校验、`nature_adapter` 的安全边界、`figure_studio` 样式/导出/manifest/验证模块、六类数值模板、已验证的三类插图模板、图库原图保护和手动评价保护、Python/Conda/矢量导出约束。

应调整：`modern-scientific-figure` 的职责从“通用绘图规范”改为“任务协调入口”；把 Nature Skill 明确放在专业 Figure 设计之前；把公共模板改成可选 renderer；把 `overwrite=True` 改为显式选项；把文档中的“适配器参与绘图”改写成“读取并记录，设计影响待端到端验证”。

应新增：一个很薄的 Figure Brief/Design Receipt 数据结构和一个统一任务执行器或等价的 Codex 工作流记录。它只记录 claim、evidence、archetype、backend、Nature references、任务模式、renderer、审查风险和输出源文件哈希，不重新实现 Nature 理论，也不复制未确认可再分发的上游正文。

## 5. 最小端到端闭环

推荐的真实工作流是：

`用户任务 + 数据/模型资料`
→ `modern-scientific-figure 识别任务与模式`
→ `显式加载 $nature-figure 及相关 reference`
→ `Figure Brief / Design Receipt`
→ `按任务选择 algorithm-visualization 或 scientific-illustration`
→ `选择或编写 Python renderer`
→ `运行 Conda Python，导出 PNG/SVG/PDF`
→ `打开实际 PNG 并执行 figure-design-review`
→ `交付 plot.py、config.py、manifest、输入资料、receipt 和输出`。

用户仍可显式指定 Nature Skill、参考图、Python 后端和模板；普通图只需一次设计，练习阶段核心图生成两种信息组织明显不同的草稿，正式比赛图先交付完整初版再由用户验收。这个分流放在现有 `modern-scientific-figure` Skill 中即可，不需要新建重复 Skill。

## 6. 第一批开发直接执行清单（P0）

建议下一次会话只执行以下范围：

1. 修改 `.agents/skills/modern-scientific-figure/SKILL.md`：明确先调用 `$nature-figure`；要求 Figure Contract；定义数值图、插图和组合图的路由；声明 `algorithm-visualization`、`scientific-illustration`、`figure-reference-manager`、`figure-design-review` 的调用边界；加入 ordinary/core-practice/formal 三种模式和用户覆盖参数。
2. 新增 `figure_studio/figure_brief.py`：实现可序列化的 `FigureBrief`、`load_figure_brief()`、`validate_figure_brief()`；至少校验 `claim`、`evidence_panels`、`archetype`、`backend="Python"`、`task_mode`、`nature_references`、`renderer` 和 `review_risks`。
3. 新增 `tools/run_figure_task.py`：接受 `--brief`、`--renderer`、`--output-dir`、`--data-path`、`--manifest-path`、`--nature-skill-root`；只调用已有 renderer 的 `main()`，不复制绘图库逻辑；写出 `design_receipt.json` 和 `task_manifest.json`，记录 fixed Nature commit、references、输入/源码/配置哈希及输出文件。
4. 调整 `figure_studio/nature_adapter.py`：保留完整树校验和固定版本；让 receipt 明确区分 `references_loaded` 与“由 Agent 作出的设计决定”，不声称适配器自动理解上游内容。
5. 新增 `tests/test_figure_brief.py`、`tests/test_run_figure_task.py`，补充缺字段、非 Python backend、路径逃逸、固定 Nature commit、输出 receipt 和 practice manifest 的测试；不把 pytest 伪装成宿主 `$nature-figure` 调用测试。
6. 在真实 Codex 会话中显式调用 `$nature-figure`，使用 `examples/data` 中已标注 `illustrative practice data` 的收敛任务，生成一张新的 Nature-first 图。必须实际打开 PNG，并保留 `plot.py`、`config.py`、`data_manifest.json`、`figure_brief.json`、`design_receipt.json`、PNG/SVG/PDF 和运行命令。

第一批完成标准：Skill 明确路由且不与 Nature 重复；统一执行器能运行一个已有 Python renderer；receipt 能证明固定版本和输入输出关系；图片实际生成并打开；`pytest`、Ruff、Skills 校验全部通过；报告中仍单独标出“宿主 Skill 调用依靠真实会话验收，不能由本地 pytest 代替”。

## 7. 三个开发批次

| 批次 | 范围 | 完成标准 |
| --- | --- | --- |
| P0 Nature-first 闭环 | 统一入口、Figure Brief/Design Receipt、真实 `$nature-figure` 任务、Python renderer、实际查看和源码交付 | 至少一张新 Nature-first practice figure 有完整源文件、输入、配置、receipt、PNG/SVG/PDF；自动检查全绿；实际 PNG 已打开 |
| P1 轻量版本与图库增强 | source/config/manifest 哈希、candidate/accepted 记录、显式输出目录和防覆盖；图库 review receipt、stale 报告、少量相关性筛选；不引入数据库 | 同一认可目录默认不能被静默覆盖；修改配置会形成可区分 run；手动图库评价重扫后保留；未分析图片不被标记为深度分析 |
| P2 插图与回归 | 几何约束、3D 曲面/空间、网络结构的最小模板和实图；组合 Figure 质量提升；补实际渲染、源码和视觉回归 | 每个新增类别至少一份明确示例输入、一份 Python 源码、一套配置/manifest、PNG/SVG/PDF 和一次实际视觉检查；六类模板及已有插图回归不退化 |

P2 可按数学建模比赛实际题型裁剪；不要为了“覆盖类别”而虚构模型结构、空间数据或实验结论。

## 8. 尚未验证的能力与风险

- 尚未完成一次由 `$nature-figure` 显式驱动的真实端到端任务，因此上游设计方法对具体 Figure 结构的影响仍是 P0 风险。
- `nature_adapter` 目前是安全读取/记录适配器，不是 Nature 设计解释器；不能通过增加哈希字段解决设计主导问题。
- 模板 `main()` 的 `overwrite=True` 和固定示例目录是正式比赛版本保护风险；P1 前不要把固定示例目录当作正式作品目录。
- 图库的 Agent 分析接口只能记录调用者声明的已查看状态，无法单靠代码证明视觉模型确实打开了图片；需要工作流收据和人工抽查。
- 几何、3D、网络基础函数存在，但当前没有分别完成独立模板、实际输出和视觉验收；README/Skill 的能力描述不能替代这些证据。
- 当前没有用户新增图库图片，因此没有任何真实个人偏好结论，也没有可验证的个人作品源码关联。

## 9. 本次审查实际修改

- `docs/PHASE3_ARCHITECTURE_REVIEW.md`：本审查报告。
- `docs/superpowers/plans/2026-09-22-phase3-nature-first-workflow.md`：三批次可直接执行的开发计划。
- `docs/UPSTREAM_NATURE_FIGURE.md`：纠正“读取上游文件”与“上游设计已经影响图形”的表述边界。
- `docs/TEST_REPORT.md`：补充第二阶段历史验证与第三阶段当前宿主可发现性/端到端调用之间的区别。

本次没有修改 Python 绘图库、模板、Skills 代码或原版 Nature 文件，也没有删除、覆盖、移动图库原图。
