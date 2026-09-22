# P1 实际验收记录

验收日期：2026-09-22
数据状态：验收 Figure 使用仓库内明确标记的 `illustrative practice data`；参考图库中的图片也是本仓库生成的测试素材，不代表用户收藏或个人审美偏好。

## 独立复现

已交付两份不依赖仓库运行时的复现包：

- `examples/outputs/p1_independent_reproduction/simple_convergence/`
- `examples/outputs/p1_independent_reproduction/complex_nature_first/`

两份包均包含入口 `plot.py`、可修改的 `config.py`、输入 CSV、数据 manifest、Figure Brief、README、PNG/SVG/PDF、输出 manifest 和 `reproduction_manifest.json`。复杂包保留两个不同类型面板；简单包包含独立运行时辅助模块。复现 manifest 明确记录依赖、哈希、`project_independent: true`、`project_root_env_required: false` 和不加载 Nature Skill 运行时文件。

测试在 Conda 环境 `scientific-figure-studio` 中执行，子进程工作目录位于仓库外，并移除了 `SCIENTIFIC_FIGURE_STUDIO_ROOT` 和 `PYTHONPATH`。两个包都实际生成了三种输出格式，并打开检查了 PNG；没有使用项目根目录回退路径。

## 工作区、候选和认可版本

`tools/run_figure_task.py` 现在按“输入/目标预检查 → 独立临时目录 → renderer → PNG/SVG/PDF 完整性验证 → 带回滚的写入”执行。renderer 异常、必要输入缺失或冲突时，既有目标不会被部分复制。版本 manifest 记录源码、配置、输入、Nature 上下文、输出哈希和父运行关系；runner 交付同时生成保守的复现说明。

实际验收目录：

- `examples/outputs/p1_gallery_acceptance/nature_gallery_task/`：workspace。
- `examples/outputs/p1_gallery_acceptance/candidate_work/`：candidate，父运行是上述 workspace。
- `examples/outputs/p1_gallery_acceptance/accepted_work/`：只有显式用户验收说明后生成的 accepted 副本。
- `examples/outputs/p1_gallery_acceptance/derived_workspace/`：从 accepted 派生的可编辑 workspace。

已实际执行：冲突/renderer 失败保护、显式 `--overwrite` 访问 accepted 的拒绝、快照修改后按哈希恢复，以及快照恢复访问 accepted 的拒绝。快照来源包含源码、配置、输入和三种输出；恢复后哈希与快照 manifest 一致。

`python tools/manage_figure_work.py works --gallery-root ... --query "Explicit P1 acceptance"` 已实际返回该 accepted work，并提供 `plot.py`、`config.py`、版本/任务/复现 manifest 和源文件哈希；因此优秀作品不是只能存档、不可检索的孤立目录。

## 个人参考图库与视觉分析

实际打开并分析的测试参考图为：

`examples/outputs/p1_gallery_acceptance/reference_gallery/02_algorithm/nature_first_reference.png`

它是仓库生成的多面板算法练习图，不是用户收藏图。视觉档案记录了：不对称双面板构图、左侧主轨迹与右侧摘要证据的层级、深蓝/青绿/中性灰关系、标题/轴标签/图例层次、面板字母标注、外边距和底部 provenance 说明，以及可复用的留白与证据排序方法。Agent 记录包含本地图片查看 receipt；索引没有自动设置 favorite，也没有写入用户偏好。

图库还实际验证了内容哈希变化后的旧评价保留、历史记录、`stale` 状态和视觉档案重新复核标记。确定性扫描器只负责文件事实；Agent 视觉观察、用户评价、来源信息和作品关联分别保存。

## Nature-first 连接验收

`gallery_task_brief.json` 同时指定了 Nature 参考文件、图库图片和代码参考。`nature_gallery_task` 的 `design_receipt.json` 实际记录了固定上游提交 `1930963cbc004da9ac8e3af7944d4f0a3488d3e1`、四个已读取参考文件及哈希、图库图片哈希、代码参考和设计要求。新图没有复制参考图的科学内容，也没有改变输入数据；它只借鉴了主面板优先、克制蓝青灰配色和信息层级。

Nature Skill 的适配器读取和校验记录不被当作 Python 自动测试能够证明的宿主 Skill 调用；宿主会话中的人工加载状态在回执中单独标注。上游原始 Skill 文件未复制进本项目。当前回执的人工视觉审查状态为 `passed`。

## 最终回归结果

最终验证命令结果如下；未执行的项目保持明确的“未验证”状态：

| 检查 | 结果 |
| --- | --- |
| 全量 `pytest -q` | PASS：133 passed |
| Ruff | PASS：All checks passed |
| 项目 Skills 验证 | PASS：Validated 5 project Skill(s) |
| 固定 Nature Skill 完整性验证 | PASS：固定提交匹配，30 个文件 |
| P0 Test A/B/C 回归和现有交付检查 | PASS：`tests/test_phase3_acceptance.py` 4 passed；十张图重新渲染并查看 |
| P1 独立复现、文件安全、图库和作品管理测试 | PASS：聚焦 P1 测试 35 passed；全量测试包含这些用例 |

尚未验证项和需要用户确认的内容：真实用户收藏图片的来源/版权和个人评价仍需用户提供；正式科研数据、统计设计、不确定性和论文级结论不由本验收素材代替；独立复现包的依赖版本锁定仍需用户按目标机器进一步冻结。
