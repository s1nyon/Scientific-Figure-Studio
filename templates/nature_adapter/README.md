# 固定 Nature Skill 适配示例

这是使用 `illustrative practice data` 的 Python 示例，不代表比赛或实验结果。运行前必须把固定提交 `1930963cbc004da9ac8e3af7944d4f0a3488d3e1` 的完整 `nature-figure` Skill 安装并验证到用户 Codex Skills 目录；模板会读取原版 `SKILL.md`、Figure Contract、common patterns 和 QA contract 的实际内容，并写入 `nature_context.json`。

安装与验证：

```powershell
python tools/install_nature_figure.py --destination "$env:USERPROFILE\.codex\skills\nature-figure"
python tools/verify_nature_figure.py --path "$env:USERPROFILE\.codex\skills\nature-figure"
```

生成：

```powershell
python templates/nature_adapter/plot.py
```

输出目录为 `examples/outputs/fig_07_nature_adapter/`。项目实际绘图、预览、导出和 QA 使用 Python；上游 Skill 中保留的 R 轨道只作为原始参考，不在本项目中生成图片。
