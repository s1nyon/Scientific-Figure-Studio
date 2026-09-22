# 快速开始

## 1. 创建隔离环境

在 PowerShell 中进入项目根目录：

```powershell
powershell -ExecutionPolicy Bypass -File tools/create_conda_env.ps1
conda activate scientific-figure-studio
```

脚本只创建名为 `scientific-figure-studio` 的 Conda 环境，显式从 `conda-forge` 安装，不注册系统 Python。已配置 `conda-forge` 的机器也可以运行 `conda env create -f environment.yml`。

验证 Python 没有指向系统环境：

```powershell
python --version
python -c "import sys; print(sys.executable)"
```

输出路径应位于 Conda 环境目录中。

## 2. 生成第一张图

```powershell
python templates/convergence/plot.py
```

打开 `examples/outputs/fig_01_convergence/`，其中包含 PNG 预览、PDF、SVG、源码快照、配置和数据清单。

一次生成全部六类练习图：

```powershell
python tools/generate_examples.py
```

生成结构化科研插图（示例结构）：

```powershell
python templates/illustration/flowchart/plot.py
python templates/illustration/architecture/plot.py
python templates/illustration/composite/plot.py
```

Nature 适配示例需要先按固定提交安装并校验上游目录：

```powershell
python tools/install_nature_figure.py --destination "$env:USERPROFILE\.codex\skills\nature-figure"
python tools/verify_nature_figure.py --path "$env:USERPROFILE\.codex\skills\nature-figure"
python templates/nature_adapter/plot.py
```

一次复制源码、输入文件并生成四个第二阶段交付目录：

```powershell
python tools/generate_phase2_examples.py
```

## 3. 修改常见参数

打开对应输出目录或模板目录的 `config.py`，优先修改：

```python
PRIMARY_COLOR = "#1F6F8B"
LINE_WIDTH = 2.0
FONT_SIZE = 8.5
FIGURE_WIDTH = 6.6
```

保存后重新运行 `plot.py`。图片、PDF 和 SVG 会重新生成，输入 CSV 不会被改写。

## 4. 运行测试

```powershell
conda run -n scientific-figure-studio pytest -q
conda run -n scientific-figure-studio ruff check .
conda run -n scientific-figure-studio python tools/validate_skills.py
```

完整测试报告位于 `docs/TEST_REPORT.md`。

## 5. 中文字体

项目会检测系统实际存在的字体，优先使用 Noto Sans SC、Microsoft YaHei 或 SimHei。若测试报告显示中文字体缺失，请安装一个有明确许可证的 CJK 无衬线字体，再重新运行字体测试；不要把字体文件直接复制进项目。
