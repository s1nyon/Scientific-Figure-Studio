# Fixed upstream Nature Figure Skill

本项目指定的上游是 `lth0/codexSkill` 中的 `skills/codex/nature-figure`，固定提交为
`1930963cbc004da9ac8e3af7944d4f0a3488d3e1`，对应提交日期为 2026-08-31。

## 完整性与许可审查

固定目录包含 30 个文件：`SKILL.md`、`README.md`、11 个 references、15 个 PNG
资源、`evals/evals.json` 和 `.gitignore`。项目已记录每个文件的 SHA-256，但不把上游
Skill 正文或资源复制进本仓库。

截至该固定提交，仓库根目录和 `nature-figure` 目录中均未发现可识别的
`LICENSE`、`COPYING` 或 `NOTICE` 文件，因此本项目不对上游文件作公开再分发许可判断。
需要使用时，由用户在本机按固定 SHA 下载完整目录；该安装器不会改变本仓库，也不会追踪
上游 main 分支。

## 安装与验证

在项目根目录使用项目 Conda 环境运行：

```powershell
python tools/install_nature_figure.py --destination "$env:USERPROFILE\.codex\skills\nature-figure"
python tools/verify_nature_figure.py --path "$env:USERPROFILE\.codex\skills\nature-figure"
```

安装器下载固定 commit 的 GitHub codeload archive，先检查完整 30 文件树和 SHA-256，
再安装到用户的 Codex Skills 目录。默认不覆盖已有 Skill；强制更新必须显式加入
`--force`，旧目录会保留为备份。

## 依赖与职责边界

上游 Skill 是工作流和参考资料，不是本项目的 Python 包。其 Python 轨道说明
Matplotlib、Seaborn、NumPy 等常见工具；本项目正式绘图仍只使用仓库声明的 Python
依赖和 `figure_studio` 视觉系统。上游 R 轨道原样保留在本地安装内容中，但本项目不
使用 R 生成图片、预览、导出或 QA。

上游提供 Figure Contract、证据层级、Nature 版式、图表分类、导出和 QA 原则。本项目
额外提供 manifest 数据状态、外部正式数据、个人图库保护、Python 源码交付、科学插图
primitives 和自动测试。

## 实际调用记录

`figure_studio.nature_adapter` 只接受通过完整树校验的安装目录，会读取上游
`SKILL.md`、`references/figure-contract.md`、`references/common-patterns.md` 和
`references/qa-contract.md`，并把 commit、reference 哈希和适配器版本写入
`nature_context.json`。这证明原版内容在生成时被实际读取并参与适配。

本地文件读取/校验不等于当前 Codex 进程已经刷新 Skill 索引。安装或更新后若主机需要
重启 Codex 才能发现新 Skill，应在测试报告中单独记录，不把它隐含为已验证。
