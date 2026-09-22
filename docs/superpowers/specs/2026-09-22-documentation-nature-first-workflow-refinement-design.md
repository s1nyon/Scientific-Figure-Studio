# Nature-first 文档与 Agent 工作规范优化设计

**日期：** 2026-09-22  
**范围：** 仅维护当前文档与项目级 Skill 工作规范，不改变绘图库、模板、原版 Nature Skill、用户图库原图或已认可作品。

## 目标

让新的 Codex Agent 仅依据当前项目文档和用户提供的绘图任务，就能理解 Scientific Figure Studio 是一个以 Nature-first 设计决策为核心、以 Python 源码交付和实际图片审查为闭环的科研绘图工作流；同时避免把历史模板、第四轮 Design A 或自动测试结果误读为全局设计规则或顶刊质量认证。

## 设计方案

采用现有文件内的最小范围修订：

1. `AGENTS.md` 只保留科学准确性、数据与图库保护、源码交付、安全执行和验收状态等全局约束；把六类模板和旧版第一阶段完成定义降为历史/工具信息。
2. `modern-scientific-figure` 保持唯一统一绘图入口，增加科学表达目标、辅助面板必要性、参考图库边界、设计探索模式和分层视觉审查要求，但不复制或修改原版 Nature Skill。
3. `README.md`、`docs/QUICK_START.md` 和 `docs/SKILLS_USAGE.md` 共同说明 Nature-first 正式入口；模板命令保留为可选示例，并按实际 runner、图库和作品管理接口给出可执行示例。
4. `design_system` 文档把三种预设、布局和模板改写为可选参考，并记录第四轮测试中有条件的经验，不把 Design A 固化为默认模板。
5. `figure_gallery` 文档与 `figure-reference-manager` 明确区分扫描事实、Agent 实际视觉分析、用户评价、科学内容和源码 provenance；修正 `record_agent_analysis()` 示例以匹配当前 API，并保留 Design A 的认可范围、限制和复现关联。
6. 只有在目标文件存在实际冲突时才修改其他项目 Skill；不新增重复的统一入口 Skill，不重写历史报告。

## 文件边界

预计修改：

- `AGENTS.md`
- `README.md`
- `design_system/DESIGN_GUIDE.md`
- `design_system/layout_rules.md`
- `docs/QUICK_START.md`
- `docs/SKILLS_USAGE.md`
- `docs/GALLERY_WORKFLOW.md`
- `docs/FIGURE_EDITING.md`
- `figure_gallery/README.md`
- `figure_gallery/GALLERY_GUIDE.md`
- `.agents/skills/modern-scientific-figure/SKILL.md`
- `.agents/skills/figure-reference-manager/SKILL.md`

按需检查但默认不改：`docs/UPSTREAM_NATURE_FIGURE.md`、`algorithm-visualization`、`figure-design-review`、`scientific-illustration`、模板、`figure_studio`、图库原图和 `figure_gallery/05_my_work/round_04_design_a_accepted/`。

## 验收与证据

- 用仓库当前真实路径和函数签名检查相对链接、Skill 名称、GalleryIndex 示例、runner 参数及作品管理命令。
- 使用项目环境执行 Skill 校验、固定 Nature Skill 完整性校验、全量 pytest、Ruff 和 `git diff --check`；环境不可用时记录为未验证，不改写历史报告冒充通过。
- 检查 diff，确认原版 Nature Skill 安装目录、图库原图、认可作品、模板和绘图库没有无关变化。
- 使用新的 `illustrative practice data` 任务运行一次 Nature-first Python Figure，实际打开生成图片并检查；当前宿主不能启动独立 Codex 会话时，将“独立会话/宿主 Skill 动态调用”与本次 Python 运行分开报告为未验证。

## 非目标

本轮不开发 P2 功能，不新增复杂模板、桌面端、数据库或高级检索，不重新生成全部历史图片，不自动收藏新图，不修改用户评价，不合并 `main`，也不把 Design A 升级为通用模板或质量认证。
