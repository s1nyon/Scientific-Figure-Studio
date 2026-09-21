# Scientific Figure Studio

Scientific Figure Studio 是一个面向数学建模竞赛和科研论文的本地 Python 科研绘图工程。它用 Matplotlib 生成可复现的静态图表，提供统一的配色、字体、布局、导出和视觉审查流程，并保留完整可修改的 Python 源码。

## 当前内容

- `figure_studio/`：统一视觉系统、导出验证、算法绘图辅助函数和个人图库管理。
- `templates/`：算法收敛、预测误差、灵敏度、帕累托、空间路径和多面板综合图模板。
- `examples/data/`：明确标记的练习数据，不代表任何正式比赛结果。
- `examples/outputs/`：每张示例图的 PDF、SVG、PNG、源码、配置和数据清单。
- `.agents/skills/`：四个可显式调用的 Codex Skills。
- `figure_gallery/`：用户自己的科研图片参考图库。
- `docs/`：中文快速入门、Skill 使用、图库维护和源码修改说明。

## 安装

项目使用独立 Conda 环境，不依赖系统 Python：

```powershell
powershell -ExecutionPolicy Bypass -File tools/create_conda_env.ps1
conda activate scientific-figure-studio
```

脚本显式使用 `conda-forge`，不会要求接受默认 Anaconda channel 的条款。也可以在已配置 `conda-forge` 的机器上运行 `conda env create -f environment.yml`。

如果机器还没有 Conda，请先安装用户范围的 Miniconda 或 Miniforge，并取消系统 Python 注册和系统 PATH 修改。

## 第一个示例

在项目根目录运行：

```powershell
conda activate scientific-figure-studio
python templates/convergence/plot.py
```

生成的文件位于 `examples/outputs/fig_01_convergence/`。修改该目录中的 `config.py` 或模板目录中的配置后，再运行同一脚本即可复现图片。

六类示例的详细位置和实际视觉检查结果见 `docs/TEST_REPORT.md`。正式使用时，请先把真实数据复制到独立的数据目录，更新 manifest 和字段说明，再选择合适模板。

## Skills

在 Codex 中可以显式调用：

```text
$modern-scientific-figure
$algorithm-visualization
$figure-design-review
$figure-reference-manager
```

Skill 只负责工作流程和审查要求；最终图表仍由保存下来的 Python 源码生成。详见 [`docs/SKILLS_USAGE.md`](docs/SKILLS_USAGE.md)。

## 参考图库

把新图片放入 `figure_gallery/00_inbox/`，然后运行图库更新命令或调用 `$figure-reference-manager`。系统会生成哈希、主色和布局等有限的可观察信息，不会修改原图或自动推断你的喜好。详见 [`docs/GALLERY_WORKFLOW.md`](docs/GALLERY_WORKFLOW.md)。

## 设计原则

科学准确性优先于装饰。项目默认使用白色背景、深蓝灰文字、克制的蓝色主色、青绿色辅助色、暖橙色强调色和中性灰辅助元素；颜色会与线型、标记或标签配合使用。详细规则见 [`design_system/DESIGN_GUIDE.md`](design_system/DESIGN_GUIDE.md)。
