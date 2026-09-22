# Phase 3 Nature-First Workflow Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (- [ ]) syntax for tracking.

**Goal:** 在不重写第二阶段工程的前提下，让固定版本 Nature Skill 真正成为科研 Figure 设计的首要专业能力，并完成一次可追溯的 Python 端到端绘图闭环。

**Architecture:** 升级现有 modern-scientific-figure 作为 Codex 协调入口；Nature Skill 负责适用范围内的 Figure Contract、构图和审查指导；algorithm-visualization 与 scientific-illustration 负责专业分流；现有模板只是可选 renderer。新增的 Figure Brief/Design Receipt 只记录决策和 provenance，不复制或改写上游 Nature 文件。

**Tech Stack:** Python 3.11、Matplotlib、Pandas、NumPy、项目 figure_studio、固定 Nature commit 1930963cbc004da9ac8e3af7944d4f0a3488d3e1、Conda 环境 scientific-figure-studio。

## Global Constraints

- 使用 Python 生成、预览、导出和 QA；不切换 R 作为项目正式后端。
- 不修改上游 Nature 文件，不追踪上游 main，不在未确认许可时复制上游正文或资源进公开仓库。
- 保留数据真实性、manifest、练习数据标记、源码强制交付、图库原图保护和矢量导出约束。
- 不新增 Web、桌面端、数据库、论文排版或多用户基础设施。
- 本地自动测试不能证明宿主 Codex 已调用 $nature-figure；该项必须由真实 Codex 会话和输出 receipt 验收。
- 不使用破坏性 Git 命令；正式输出不应静默覆盖用户认可作品。

---

## Batch 1 / P0：Nature-first 统一任务闭环

**Files:**

- Modify: .agents/skills/modern-scientific-figure/SKILL.md
- Modify: docs/SKILLS_USAGE.md, README.md
- Modify: figure_studio/nature_adapter.py
- Create: figure_studio/figure_brief.py
- Create: tools/run_figure_task.py
- Create: tests/test_figure_brief.py, tests/test_task_runner.py, tests/test_comparison.py, tests/test_phase3_acceptance.py
- Create during acceptance: examples/data/phase3_flowchart_brief.json and examples/outputs/fig_11_nature_first/, examples/outputs/fig_12_unified_flowchart/

- [x] 在 modern-scientific-figure/SKILL.md 中写明：先显式加载 $nature-figure，再读取相关 references；随后按数值图、流程/架构/几何/3D/网络、组合 Figure 分流。保留用户手动指定 Skill、reference、backend、template 的覆盖方式。
- [x] 定义 ordinary、core-practice、formal 三种任务模式；核心练习图要求两种信息组织明显不同的草稿，正式比赛图要求先完成自动检查再交付一版完整初稿。
- [x] 在 figure_studio/figure_brief.py 实现可 JSON 序列化的 FigureBrief，字段至少包括 claim、evidence_panels、archetype、backend、task_mode、nature_references、renderer、review_risks；实现 load_figure_brief() 和 validate_figure_brief()。
- [x] 在 tools/run_figure_task.py 实现薄执行层：解析 --brief、--renderer、--output-dir、--data-path、--manifest-path、--nature-skill-root，导入已有 renderer 并调用其 main()；不要在执行器中复制绘图逻辑。
- [x] 由执行层写出 design_receipt.json 与 task_manifest.json，记录 Figure Brief、固定 Nature commit、实际加载的 references、renderer、输入哈希、源码/配置哈希、输出文件和 review 状态；明确把“上游文件已读取”和“Agent 作出的设计决定”分成不同字段。
- [x] 补测试：brief 缺字段、backend 非 Python、非法 reference、renderer 不存在、练习 manifest、receipt 字段和 PNG/SVG/PDF 输出。不要写一个声称能验证宿主 Skill 调用的假测试。
- [x] 在真实 Codex 会话显式调用 $nature-figure，使用已标记为 illustrative practice data 的收敛输入，完成 Figure Contract、Python 绘图、实际 PNG 查看和源码交付；把命令、输出和 receipt 保存到 fig_11_nature_first。
- [x] 运行：conda run --no-capture-output -n scientific-figure-studio pytest -q、conda run --no-capture-output -n scientific-figure-studio ruff check .、conda run --no-capture-output -n scientific-figure-studio python tools/validate_skills.py。

**Acceptance:** 一个真实 Codex 任务中 $nature-figure 被显式加载；新 Figure 的设计 receipt 能追溯 claim/evidence/archetype/reference/backend；Python 重新运行可生成 PNG/SVG/PDF；PNG 已实际打开；完整源码、配置、manifest 和 practice 输入齐全；自动检查全绿。

## Batch 2 / P1：安全版本与图库最小增强

**Files:**

- Modify: figure_studio/export.py
- Modify: templates/*/plot.py, tools/generate_examples.py, tools/generate_phase2_examples.py
- Modify: figure_studio/gallery.py, tests/test_gallery.py
- Create: figure_studio/artifacts.py, tests/test_artifacts.py, tests/test_version_safety.py

- [ ] 让模板 main() 接受 overwrite: bool = False，命令行只在用户显式传入 --overwrite 时允许覆盖；示例生成器若需重建，显式传递该参数或使用新的输出目录。
- [ ] 在 figure_studio/artifacts.py 实现 build_source_hashes()、create_run_dir() 和 write_run_manifest()；记录 plot/config/data manifest/输入文件哈希、run id、parent run、candidate|accepted 状态和输出清单。
- [ ] 将 source hashes 写入输出 manifest；默认生成候选 run，不覆盖已有 accepted 目录；不引入数据库，采用显式目录和 JSON manifest。
- [ ] 扩展图库分析 receipt：保留确定性事实和手动评价，要求 Agent 分析调用提供 viewed、分析来源和时间；增加不删除原记录的 stale 报告及按 chart_type/application/status 的轻量筛选，不能把未分析图标为已分析。
- [ ] 补测试：第二次写入 accepted 目录默认失败；配置或源码变更产生不同哈希；用户评价/收藏重扫后保留；重复图片只标记；stale 不删除；未分析记录不进入深度分析结果。
- [ ] 运行完整 pytest、Ruff 和 Skills 校验，并实际重生成一个 P0 Figure 的 candidate run，确认修改配置后输出 manifest 改变。

**Acceptance:** 正式输出不会被静默覆盖；每个候选版本能从输出反查到源码、配置、manifest 和输入；图库手动评价安全；新增状态仍不把“调用回调”夸大为视觉理解事实。

## Batch 3 / P2：插图覆盖与整体回归

**Files:**

- Reuse first: figure_studio/illustrations.py
- Create only as needed: templates/illustration/geometry/、templates/illustration/surface3d/、templates/illustration/network/ 及其明确的示例输入、配置和 manifest
- Modify: .agents/skills/scientific-illustration/SKILL.md, README.md
- Modify/add: tests/test_illustrations.py, tests/test_illustration_templates.py

- [ ] 先使用现有 primitive，不扩展公共 API；只有测试或真实任务暴露缺口时才修改 figure_studio.illustrations。
- [ ] 为几何约束、三维曲面/空间场景、网络结构各建立一个最小真实示例；输入必须声明示例结构或练习数据，不能编造真实模型模块、实验结果或空间数据。
- [ ] 每类生成完整 Python 源码、配置、manifest、PNG/SVG/PDF；实际打开并检查节点/连接、等比例坐标、曲面有限值、标签和组合布局。
- [ ] 补模板 contract/export tests 和一次完整回归；保留已验证的六类数值模板、fig_08–fig_10 以及 Nature-first P0 输出。

**Acceptance:** 三个新增类别都有实际生成物和视觉审查记录；组合 Figure 不强行转换为单一折线/柱状图；自动测试和 Ruff 通过；未使用的专业后端仍不被宣称为已验证。

## Final verification checklist

- [ ] git status --short 仅包含本批次预期文件。
- [ ] pytest、Ruff、validate_skills.py 均实际执行并记录结果。
- [ ] P0/P1/P2 每个输出目录均包含源码、配置、输入/manifest、receipt 和 PNG/SVG/PDF。
- [ ] 用图片查看能力实际打开每个新增 PNG，并记录尺寸下的文字、连接线、图例、坐标和科学含义检查。
- [ ] 最终报告区分：代码已完成、自动测试通过、宿主 Skill 已显式调用、图片已实际查看、仍需用户确认。

## P0 completion record

- [x] Unified modern-scientific-figure entry rules now require Nature-first routing for applicable data Figures and scientific-illustration routing for schematic-only tasks.
- [x] Figure Brief validation implemented in figure_studio/figure_brief.py.
- [x] Deterministic runner implemented in tools/run_figure_task.py, including source/input hashes, fixed Nature context records, delivery packaging, and explicit overwrite forwarding.
- [x] Snapshot, restore, and native-aspect comparison implemented in figure_studio/comparison.py and tools/figure_revision.py.
- [x] Test A, Test B, and Test C rendered and visually inspected under examples/outputs/fig_11_nature_first and examples/outputs/fig_12_unified_flowchart.
- [x] P0 behavior and delivery tests passed; the host Nature Skill invocation remains a Codex-session/manual evidence item rather than a Python unit-test claim.
