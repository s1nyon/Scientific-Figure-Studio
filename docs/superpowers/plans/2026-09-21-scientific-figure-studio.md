# Scientific Figure Studio Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 在用户级 Conda 环境中交付一个可复现的 Scientific Figure Studio 第一版，包含统一科研绘图包、六类真实生成的练习图、个人图库管理、四个 Codex Skills、测试和中文文档。

**Architecture:** 项目使用根目录 Python 包 `figure_studio`，把样式、配色、字体、布局、注释、导出、验证、数学绘图辅助函数和图库管理分成小模块。六个模板各自提供完整 `plot.py`、`config.py`、数据清单和 README，统一调用公共包并把图片写入独立的 `examples/outputs/fig_*` 目录。四个 `.agents/skills` 只描述职责和流程，公共约束放在 `AGENTS.md`。

**Tech Stack:** Python 3.11；Conda/conda-forge；Matplotlib；NumPy；Pandas；Pillow；PyYAML；pypdf；pytest；Ruff；PowerShell。

## Global Constraints

- 使用 Conda 隔离环境；不修改系统 Python，不把开发者绝对路径写入项目。
- 练习数据必须明确标记为 illustrative practice data，不能冒充比赛结果。
- 不删除、覆盖、移动或上传用户图库原图；图库分析只描述可观察事实或明确标记的估计。
- 正式绘图交付必须同时包含可运行 Python 源码、可修改配置和图片。
- 图表优先使用 `figure_studio` 统一视觉系统；数据处理、绘图参数和装饰逻辑分离。
- 不编造数据、指标、置信区间、算法结论或用户审美偏好。
- 每个生产模块先写一个能正确失败的测试，再实现最小行为；配置和 Markdown 可直接创建。
- 每次声称测试、生成或视觉审查完成前，必须运行相应的完整命令并记录实际输出。
- 不使用 SciencePlots 预设代替本项目视觉系统，不引入 Web 前端、数据库或在线绘图服务。

## File Map

- `AGENTS.md`：项目长期工作规范、数据真实性、图库保护、源码交付、完成定义。
- `environment.yml`、`requirements.txt`、`pyproject.toml`、`.gitignore`：环境、依赖、测试/lint 和仓库边界。
- `figure_studio/__init__.py`、`style.py`、`palettes.py`、`fonts.py`、`layouts.py`、`annotations.py`、`export.py`、`validation.py`、`analysis.py`、`gallery.py`：公共绘图与图库 API。
- `design_system/*`：配色、字体、布局和图表设计的可读规范。
- `.agents/skills/*/SKILL.md` 和 `references/*`：四个项目级 Skills。
- `templates/<type>/{plot.py,config.py,README.md,data_manifest.json}`：六类模板的 canonical source。
- `examples/data/*`：显式标记的练习数据；`examples/outputs/fig_*/*`：可独立交付的源码快照、配置、manifest、README 和实际图片。
- `figure_gallery/*`：用户图库、索引、自动分析笔记和生成缩略图目录。
- `tests/test_*.py`、`tests/assets/`：自动测试和独立测试素材。
- `docs/*.md`：中文操作文档和真实测试报告。

---

### Task 1: 建立隔离环境和项目治理文件

**Files:**
- Create: `environment.yml`
- Create: `requirements.txt`
- Create: `pyproject.toml`
- Create: `.gitignore`
- Create: `AGENTS.md`
- Create: `README.md`
- Create: `docs/QUICK_START.md`

**Interfaces:**
- Produces the environment name `scientific-figure-studio` and the command prefix `conda run -n scientific-figure-studio` used by all later tasks.
- Produces repository rules consumed by all four Skills and all template READMEs.

- [ ] **Step 1: Verify the available Conda installation paths**

Run:

```powershell
Get-Command conda,mamba,micromamba -ErrorAction SilentlyContinue
Get-ChildItem 'C:\ProgramData','C:\Users\Administrator' -Directory -Force -ErrorAction SilentlyContinue |
  Where-Object { $_.Name -match '(?i)(anaconda|miniconda|miniforge|mambaforge)' } |
  Select-Object FullName
```

If no executable exists, use the official user-scoped installer and do not register Python or add a system PATH entry. Verify the installer checksum or official download URL before running it, then expose the executable through a project-local PowerShell helper rather than editing the system environment.

- [ ] **Step 2: Write the Conda and package configuration**

Use this environment contract:

```yaml
name: scientific-figure-studio
channels:
  - conda-forge
dependencies:
  - python=3.11
  - matplotlib>=3.8
  - numpy>=1.26
  - pandas>=2.1
  - pillow>=10.0
  - pyyaml>=6.0
  - pypdf>=4.0
  - pytest>=8.0
  - ruff>=0.6
```

Keep `requirements.txt` as a pip fallback with the same runtime packages and keep `pyproject.toml` focused on pytest, Ruff, and local import configuration. Do not add a dependency only because a third-party reference project uses it.

- [ ] **Step 3: Write governance and ignore rules**

`AGENTS.md` must include the exact operational rules from the approved design: preserve raw data, protect gallery originals, require Python source/config with every formal figure, use the shared style system, record transformations and uncertainty, inspect rendered images, avoid unreviewed third-party scripts, and distinguish implemented, executed, automatically tested, visually checked, and unverified states.

`.gitignore` must exclude `.venv/`, Conda export caches, `__pycache__/`, `.pytest_cache/`, `.ruff_cache/`, generated gallery thumbnails, temporary files, and local output scratch folders while keeping the six checked-in example outputs.

- [ ] **Step 4: Create the user-facing project entry points**

`README.md` must show the Conda setup, the first example command, the six output folders, the four Skill names, and links to the Chinese docs. `docs/QUICK_START.md` must show:

```powershell
conda env create -f environment.yml
conda activate scientific-figure-studio
python templates/convergence/plot.py
```

and explain how to edit `config.py` and rerun a template.

- [ ] **Step 5: Create the environment and run a baseline import check**

Run:

```powershell
conda env create -f environment.yml
conda run -n scientific-figure-studio python --version
conda run -n scientific-figure-studio python -c "import matplotlib, numpy, pandas, PIL, yaml, pypdf; print('imports ok')"
```

Expected: Python 3.11.x and `imports ok`. Record installer or network limitations if this cannot run.

- [ ] **Step 6: Commit the project bootstrap**

```powershell
git add environment.yml requirements.txt pyproject.toml .gitignore AGENTS.md README.md docs/QUICK_START.md
git commit -m "chore: bootstrap conda project"
```

### Task 2: Build the palette, font, style, and layout system with TDD

**Files:**
- Create: `figure_studio/__init__.py`
- Create: `figure_studio/palettes.py`
- Create: `figure_studio/fonts.py`
- Create: `figure_studio/style.py`
- Create: `figure_studio/layouts.py`
- Create: `design_system/palettes.yaml`
- Create: `design_system/typography.md`
- Create: `design_system/layout_rules.md`
- Create: `tests/test_visual_system.py`

**Interfaces:**
- `get_palette(name: str = "algorithm_research") -> Palette`
- `palette_names() -> tuple[str, ...]`
- `resolve_fonts() -> FontReport`
- `figure_style(name: str = "minimal_editorial", canvas: str = "standard") -> ContextManager`
- `canvas_size(name: str) -> tuple[float, float]`
- `make_figure(canvas: str = "standard", **kwargs) -> tuple[Figure, Axes | ndarray]`

- [ ] **Step 1: Write failing tests for named palettes, canvas sizes, and scoped rcParams**

```python
def test_all_visual_presets_have_semantic_roles():
    for name in ("minimal_editorial", "algorithm_research", "visual_narrative"):
        palette = get_palette(name)
        assert palette.primary.startswith("#")
        assert palette.background == "#FFFFFF"
        assert len(palette.category_cycle) >= 4

def test_figure_style_restores_rcparams():
    before = mpl.rcParams["axes.spines.top"]
    with figure_style("minimal_editorial"):
        assert mpl.rcParams["axes.spines.top"] is False
    assert mpl.rcParams["axes.spines.top"] == before

def test_canvas_presets_are_physical_sizes():
    width, height = canvas_size("standard")
    assert 3.0 < width < 8.0
    assert 2.0 < height < 6.0
```

Run `conda run -n scientific-figure-studio pytest tests/test_visual_system.py -q`; expected failure because the package does not exist.

- [ ] **Step 2: Implement the palette dataclass and YAML-backed presets**

Define `Palette` as a frozen dataclass with semantic fields, load three named presets from `design_system/palettes.yaml`, reject unknown names with a message listing valid names, and use a restrained blue-gray/teal/orange language with distinguishable line styles and markers documented in `palettes.py`.

- [ ] **Step 3: Implement font detection and fallback reporting**

`FontReport` must contain `english_family`, `chinese_family`, `math_family`, `available`, `missing`, and `warnings`. Use `matplotlib.font_manager.findfont(..., fallback_to_default=False)` or equivalent to verify candidates instead of assuming a configured font exists. Prefer actual Windows Noto Sans SC or Microsoft YaHei when present, then DejaVu Sans for fallback. Return warnings when Chinese support is not confirmed.

- [ ] **Step 4: Implement style contexts and layouts**

Use `matplotlib.rc_context` so styles do not leak between figures. Set editable vector text defaults (`pdf.fonttype=42`, `svg.fonttype="none"`), white background, readable axes, restrained grid usage, and consistent tick/legend sizes. Implement `compact`, `standard`, `wide`, and `composite` with explicit inch dimensions and `make_figure()` using the Matplotlib object-oriented API.

- [ ] **Step 5: Run the focused tests and refactor only after green**

Run `conda run -n scientific-figure-studio pytest tests/test_visual_system.py -q`; expected: all focused tests pass. Add a test that unknown style and canvas names raise `ValueError`, then rerun the focused suite.

- [ ] **Step 6: Document the visual system and commit it**

Write typography and layout rules with the current environment’s fallback policy and semantic color rules. Run `conda run -n scientific-figure-studio ruff check figure_studio tests/test_visual_system.py`, then commit:

```powershell
git add figure_studio design_system tests/test_visual_system.py
git commit -m "feat: add shared figure visual system"
```

### Task 3: Add annotations, export, input validation, and algorithm math helpers

**Files:**
- Create: `figure_studio/annotations.py`
- Create: `figure_studio/export.py`
- Create: `figure_studio/validation.py`
- Create: `figure_studio/analysis.py`
- Create: `tests/test_export_validation.py`
- Create: `tests/test_analysis.py`

**Interfaces:**
- `add_panel_label(ax, label, **kwargs) -> Text`
- `add_reference_line(ax, value, axis="y", **kwargs) -> Line2D`
- `label_line_end(ax, x, y, text, **kwargs) -> Annotation`
- `export_figure(fig, output_stem, formats=("png", "svg", "pdf"), dpi=300, overwrite=False, provenance=None) -> dict[str, Path]`
- `validate_numeric_frame(frame, required_columns) -> None`
- `validate_artifact(path, kind) -> dict[str, object]`
- `running_best(values, goal="minimize") -> np.ndarray`
- `pareto_mask(values, directions=("minimize", "minimize")) -> np.ndarray`

- [ ] **Step 1: Write failing tests for math semantics and artifact checks**

```python
def test_running_best_respects_maximization():
    assert running_best([1, 3, 2], goal="maximize").tolist() == [1, 3, 3]

def test_pareto_mask_uses_configured_objective_directions():
    values = np.array([[1, 3], [2, 2], [3, 1], [4, 4]])
    assert pareto_mask(values, ("minimize", "minimize")).tolist() == [True, True, True, False]

def test_export_figure_writes_vector_and_raster_outputs(tmp_path):
    fig, ax = plt.subplots()
    ax.plot([0, 1], [0, 1])
    outputs = export_figure(fig, tmp_path / "figure", provenance={"practice": True})
    assert {p.suffix for p in outputs.values()} == {".png", ".svg", ".pdf"}
    assert all(path.stat().st_size > 0 for path in outputs.values())
```

Run the two focused test files and confirm the failures are due to missing functions.

- [ ] **Step 2: Implement direction-aware running best and Pareto dominance**

Convert maximize objectives by sign reversal only in a new working array; preserve input arrays. For each point, mark it non-dominated when no other point is at least as good in every configured direction and strictly better in one. Validate direction names and dimensions with actionable errors.

- [ ] **Step 3: Implement annotation helpers**

Create small Matplotlib artist helpers for panel labels, reference lines, and direct endpoint labels. Keep text ink color neutral unless the color encodes a scientific quantity, and use configurable offsets so templates can expose positions.

- [ ] **Step 4: Implement export and file validation**

Export exact figure dimensions to PNG, SVG, and PDF with `bbox_inches=None` by default, write a JSON provenance manifest beside the outputs, and refuse overwrite unless `overwrite=True`. Validate PNG dimensions/nonblank pixels with Pillow, parse SVG with `xml.etree.ElementTree`, and open PDFs with `pypdf`.

- [ ] **Step 5: Run focused tests, then lint and commit**

Run:

```powershell
conda run -n scientific-figure-studio pytest tests/test_analysis.py tests/test_export_validation.py -q
conda run -n scientific-figure-studio ruff check figure_studio tests
```

Commit only after both commands return exit code 0:

```powershell
git add figure_studio tests/test_analysis.py tests/test_export_validation.py
git commit -m "feat: add figure export validation and analysis helpers"
```

### Task 4: Implement the incremental personal gallery manager

**Files:**
- Create: `figure_studio/gallery.py`
- Create: `figure_gallery/README.md`
- Create: `figure_gallery/GALLERY_GUIDE.md`
- Create: `figure_gallery/gallery_index.csv`
- Create: `figure_gallery/00_inbox/.gitkeep`
- Create: `figure_gallery/01_minimal/.gitkeep`
- Create: `figure_gallery/02_algorithm/.gitkeep`
- Create: `figure_gallery/03_visual_narrative/.gitkeep`
- Create: `figure_gallery/04_my_favorites/.gitkeep`
- Create: `figure_gallery/05_my_work/.gitkeep`
- Create: `tests/test_gallery.py`

**Interfaces:**
- `GalleryIndex(root: Path)`
- `GalleryIndex.scan() -> list[GalleryRecord]`
- `GalleryIndex.analyze(path: Path) -> GalleryRecord`
- `GalleryIndex.search(query: str | None = None, style: str | None = None, favorite: bool | None = None) -> list[GalleryRecord]`
- `GalleryIndex.write_index() -> Path`

- [ ] **Step 1: Write failing tests for empty galleries, hashing, duplicate detection, and protected originals**

```python
def test_empty_gallery_returns_no_records(tmp_path):
    index = GalleryIndex(tmp_path)
    assert index.scan() == []

def test_gallery_records_hash_images_and_write_notes(tmp_path):
    image_path = tmp_path / "00_inbox" / "sample.png"
    make_test_image(image_path)
    records = GalleryIndex(tmp_path).scan()
    assert records[0].sha256
    assert records[0].dominant_color.startswith("#")
    assert (tmp_path / "_generated" / "gallery_notes" / f"{records[0].sha256}.md").exists()

def test_duplicate_images_are_flagged_without_deleting_either_file(tmp_path):
    first, second = copy_same_image_to_two_folders(tmp_path)
    records = GalleryIndex(tmp_path).scan()
    assert sum(record.is_duplicate for record in records) >= 1
    assert first.exists() and second.exists()
```

Run `conda run -n scientific-figure-studio pytest tests/test_gallery.py -q`; expected failure because the manager does not exist.

- [ ] **Step 2: Implement factual Pillow analysis and content hashing**

Read image dimensions, mode, alpha presence, mean luminance, dominant color estimate, grayscale tendency, and a conservative whitespace estimate. Store fields as facts or estimates in `GalleryRecord`; use relative paths and SHA-256. Ignore generated folders and unsupported files.

- [ ] **Step 3: Implement Markdown notes and CSV indexing**

Write notes under `figure_gallery/_generated/gallery_notes`, never next to or inside the source image. Include path, hash, dimensions, observable design facts, estimated fields, unknown fields, suggested tags, blank user evaluation, source/license placeholders labeled for manual completion, and analysis date. Update `gallery_index.csv` atomically and preserve manually entered favorite/style fields when the image hash and relative path are unchanged.

- [ ] **Step 4: Implement search and empty-gallery fallback**

Search case-insensitive keywords across path, style, chart type, application, and notes metadata. Sort favorites first only when `favorite=True` or records are being ranked for a task; do not infer favorites. Return an empty result with a documented default-style fallback when no images exist.

- [ ] **Step 5: Run focused tests and commit**

Run `conda run -n scientific-figure-studio pytest tests/test_gallery.py -q` and `conda run -n scientific-figure-studio ruff check figure_studio/gallery.py tests/test_gallery.py`; then commit:

```powershell
git add figure_studio/gallery.py figure_gallery tests/test_gallery.py
git commit -m "feat: add protected incremental reference gallery"
```

### Task 5: Create deterministic practice data and template test utilities

**Files:**
- Create: `examples/data/convergence_practice.csv`
- Create: `examples/data/prediction_practice.csv`
- Create: `examples/data/sensitivity_practice.csv`
- Create: `examples/data/pareto_practice.csv`
- Create: `examples/data/spatial_practice.csv`
- Create: `examples/data/composite_practice.csv`
- Create: `tests/conftest.py`
- Create: `tests/test_template_contracts.py`
- Create: `templates/__init__.py`

**Interfaces:**
- Every practice CSV includes a `data_status` or manifest declaration stating `illustrative practice data`.
- Every template exposes `main()` and supports `python path/to/plot.py` from the project root.
- Every template config exposes `FIGURE_WIDTH`, `FIGURE_HEIGHT`, `DPI`, palette/style names, line widths, font sizes, legend location, axis limits, and output formats relevant to that figure.

- [ ] **Step 1: Write failing contract tests before template code**

```python
TEMPLATE_NAMES = ("convergence", "prediction", "sensitivity", "pareto", "spatial", "composite")

@pytest.mark.parametrize("name", TEMPLATE_NAMES)
def test_template_contract_has_source_config_manifest_and_readme(name):
    folder = PROJECT_ROOT / "templates" / name
    assert (folder / "plot.py").exists()
    assert (folder / "config.py").exists()
    assert (folder / "data_manifest.json").exists()
    assert (folder / "README.md").exists()

@pytest.mark.parametrize("name", TEMPLATE_NAMES)
def test_practice_manifest_declares_nonproduction_data(name):
    manifest = json.loads((PROJECT_ROOT / "templates" / name / "data_manifest.json").read_text())
    assert manifest["data_status"] == "illustrative practice data"
```

Run the focused test and confirm it fails because the template files do not exist.

- [ ] **Step 2: Write deterministic CSV data and manifests**

Generate small, transparent practice datasets with fixed formulas and seeds. Record each field, unit, transformation, objective direction, and the statement that the values are illustrative. Do not use random values without recording the seed and formula.

- [ ] **Step 3: Add a shared subprocess/template test helper**

In `tests/conftest.py`, define the project root, the Conda-safe Python executable used by pytest, and a helper that runs a template script with a temporary output directory. The helper must fail with captured stdout/stderr when a script exits nonzero.

- [ ] **Step 4: Run the contract tests and commit the data foundation**

At this point the contract test remains red until the templates are added; commit only the data, fixtures, and test contract if the red failure is the expected missing-template failure:

```powershell
git add examples/data tests/conftest.py tests/test_template_contracts.py templates/__init__.py
git commit -m "test: define practice data and template contracts"
```

### Task 6: Implement convergence and prediction templates

**Files:**
- Create: `templates/convergence/plot.py`
- Create: `templates/convergence/config.py`
- Create: `templates/convergence/data_manifest.json`
- Create: `templates/convergence/README.md`
- Create: `templates/prediction/plot.py`
- Create: `templates/prediction/config.py`
- Create: `templates/prediction/data_manifest.json`
- Create: `templates/prediction/README.md`
- Create: `tests/test_convergence_template.py`
- Create: `tests/test_prediction_template.py`

**Interfaces:**
- `templates.convergence.plot.load_data(path: Path) -> pd.DataFrame`
- `templates.convergence.plot.build_figure(frame, config) -> Figure`
- `templates.prediction.plot.load_data(path: Path) -> pd.DataFrame`
- `templates.prediction.plot.build_figure(frame, config) -> Figure`
- Both `main()` functions return a dictionary of generated artifact paths.

- [ ] **Step 1: Write failing mathematical and output tests**

```python
def test_convergence_uses_running_best_for_minimization():
    frame = pd.DataFrame({"iteration": [1, 2, 3], "objective": [3.0, 2.0, 2.5]})
    assert running_best(frame["objective"], goal="minimize").tolist() == [3.0, 2.0, 2.0]

def test_prediction_keeps_train_validation_test_splits_visible():
    frame = load_prediction_data(DATA / "prediction_practice.csv")
    assert set(frame["split"]) == {"train", "validation", "test"}

def test_template_main_returns_three_formats(tmp_path):
    outputs = convergence_main(output_dir=tmp_path)
    assert {path.suffix for path in outputs.values()} >= {".png", ".svg", ".pdf"}
```

Run both focused files and verify the failure is caused by missing template modules.

- [ ] **Step 2: Implement the convergence figure**

Read algorithm, iteration, objective, and optional replicate columns without modifying the CSV. Draw current objective with lighter lines and running best with stronger lines only when configured. Use a minimization `running_best` call and make algorithm colors, linewidths, marker size, axis limits, legend position, and font sizes come from `config.py`. Add a neutral practice-data note outside the data region.

- [ ] **Step 3: Implement the prediction and residual panels**

Read `sample`, `split`, `x`, `y_true`, and `y_pred`. Show train/validation/test through markers or line styles, compute residuals from `y_true - y_pred`, show RMSE/MAE only from actual test rows, and do not invent prediction intervals. Include units in labels and keep split semantics visible in the legend.

- [ ] **Step 4: Add template READMEs and run the focused tests**

Each README must state the practice-data status, command, data columns, config parameters, output formats, and how to replace the input file without changing the plotting logic. Run:

```powershell
conda run -n scientific-figure-studio pytest tests/test_template_contracts.py tests/test_convergence_template.py tests/test_prediction_template.py -q
```

- [ ] **Step 5: Commit the two templates**

```powershell
git add templates/convergence templates/prediction tests/test_convergence_template.py tests/test_prediction_template.py
git commit -m "feat: add convergence and prediction templates"
```

### Task 7: Implement sensitivity, Pareto, and spatial templates

**Files:**
- Create: `templates/sensitivity/plot.py`
- Create: `templates/sensitivity/config.py`
- Create: `templates/sensitivity/data_manifest.json`
- Create: `templates/sensitivity/README.md`
- Create: `templates/pareto/plot.py`
- Create: `templates/pareto/config.py`
- Create: `templates/pareto/data_manifest.json`
- Create: `templates/pareto/README.md`
- Create: `templates/spatial/plot.py`
- Create: `templates/spatial/config.py`
- Create: `templates/spatial/data_manifest.json`
- Create: `templates/spatial/README.md`
- Create: `tests/test_sensitivity_template.py`
- Create: `tests/test_pareto_template.py`
- Create: `tests/test_spatial_template.py`

**Interfaces:**
- Each template exposes `load_data`, `build_figure`, and `main` with the same return conventions as Task 6.
- `pareto.build_front(frame, directions) -> pd.DataFrame` returns only input rows marked as non-dominated, sorted by the first objective.

- [ ] **Step 1: Write failing tests for heatmap semantics, Pareto directions, and spatial aspect**

```python
def test_sensitivity_manifest_contains_units_and_center_value():
    manifest = json.loads((ROOT / "templates/sensitivity/data_manifest.json").read_text())
    assert manifest["units"]["parameter"]
    assert manifest["color_center"] == 0

def test_pareto_template_does_not_call_all_points_a_front():
    frame = pd.DataFrame({"方案": ["a", "b", "c"], "cost": [1, 2, 3], "risk": [3, 2, 4]})
    front = build_front(frame, ("minimize", "minimize"))
    assert set(front["方案"]) == {"a", "b"}

def test_spatial_figure_uses_equal_axis_scaling():
    fig = build_figure(load_spatial_data(DATA / "spatial_practice.csv"), CONFIG)
    assert fig.axes[0].get_aspect() in (1.0, "equal")
```

Run the focused tests and confirm expected missing-template failures.

- [ ] **Step 2: Implement sensitivity analysis**

Draw a parameter-response curve and a pivoted two-parameter heatmap from explicit columns. Use `TwoSlopeNorm` only when the manifest declares a meaningful center value; otherwise use a sequential normalization. Label parameter and response units, annotate only observed cells, and expose color map, limits, and spacing in `config.py`.

- [ ] **Step 3: Implement Pareto front calculation and plot**

Read objective directions from config/manifest, calculate non-dominated rows with `pareto_mask`, draw all feasible solutions in muted gray, draw only the computed front in primary color, sort the front before connecting it, and label a solution only when its `is_key_solution` input flag is true.

- [ ] **Step 4: Implement spatial paths**

Read node coordinates, edges, obstacles, path IDs, and node roles. Draw obstacles, network edges, candidate paths, start/end markers, direction arrows, and node labels with a fixed aspect ratio. State in the README that coordinates are simulated planar units.

- [ ] **Step 5: Run the focused suite and commit**

```powershell
conda run -n scientific-figure-studio pytest tests/test_sensitivity_template.py tests/test_pareto_template.py tests/test_spatial_template.py -q
conda run -n scientific-figure-studio ruff check templates/sensitivity templates/pareto templates/spatial tests
git add templates/sensitivity templates/pareto templates/spatial tests/test_sensitivity_template.py tests/test_pareto_template.py tests/test_spatial_template.py
git commit -m "feat: add sensitivity pareto and spatial templates"
```

### Task 8: Implement the composite template and reproducible example delivery

**Files:**
- Create: `templates/composite/plot.py`
- Create: `templates/composite/config.py`
- Create: `templates/composite/data_manifest.json`
- Create: `templates/composite/README.md`
- Create: `tools/generate_examples.py`
- Create: `tests/test_composite_template.py`
- Create: `tests/test_example_generation.py`
- Create: `examples/outputs/fig_01_convergence/`
- Create: `examples/outputs/fig_02_prediction/`
- Create: `examples/outputs/fig_03_sensitivity/`
- Create: `examples/outputs/fig_04_pareto/`
- Create: `examples/outputs/fig_05_spatial/`
- Create: `examples/outputs/fig_06_composite/`

**Interfaces:**
- `templates.composite.plot.load_data(path: Path) -> dict[str, pd.DataFrame]`
- `templates.composite.plot.build_figure(data, config) -> Figure`
- `tools.generate_examples.main() -> list[Path]`

- [ ] **Step 1: Write failing tests for the composite evidence chain and delivery structure**

```python
def test_composite_has_one_hero_axis_and_two_evidence_axes():
    fig = build_figure(load_composite_data(DATA / "composite_practice.csv"), CONFIG)
    assert len(fig.axes) == 3
    assert fig.axes[0].get_position().width > fig.axes[1].get_position().width

def test_example_generator_creates_independent_delivery_directories(tmp_path):
    outputs = generate_examples(output_root=tmp_path)
    assert len(outputs) == 6
    for folder in outputs:
        assert (folder / "plot.py").exists()
        assert (folder / "config.py").exists()
        assert (folder / "figure.svg").exists()
```

Run the focused tests and confirm expected missing-module failures.

- [ ] **Step 2: Implement the composite figure**

Use one simulated study ID across the main performance panel, test residual panel, and parameter-response panel. Use asymmetric GridSpec with a larger hero panel and smaller evidence panels. Keep algorithm colors consistent with the convergence/prediction examples and include panel labels `(a)`, `(b)`, `(c)`.

- [ ] **Step 3: Implement the example generator**

For each template, create `examples/outputs/fig_*`, copy the complete `plot.py`, `config.py`, `data_manifest.json`, and README into the delivery folder, run the copied script, and write `generation_manifest.json` containing data path, SHA-256, config summary, package version, and artifact paths. Never copy or modify files under `figure_gallery`.

- [ ] **Step 4: Run all six scripts from project root**

Run:

```powershell
conda run -n scientific-figure-studio python tools/generate_examples.py
conda run -n scientific-figure-studio pytest tests/test_composite_template.py tests/test_example_generation.py -q
```

Expected: six independent output directories, each with PDF, SVG, PNG, source, config, manifest, and README.

- [ ] **Step 5: Commit the composite and generated delivery structure**

```powershell
git add templates/composite tools/generate_examples.py tests/test_composite_template.py tests/test_example_generation.py examples/data examples/outputs
git commit -m "feat: add composite figure and reproducible examples"
```

### Task 9: Add four project Skills and design documentation

**Files:**
- Create: `.agents/skills/modern-scientific-figure/SKILL.md`
- Create: `.agents/skills/modern-scientific-figure/references/workflow.md`
- Create: `.agents/skills/algorithm-visualization/SKILL.md`
- Create: `.agents/skills/algorithm-visualization/references/math-checks.md`
- Create: `.agents/skills/figure-design-review/SKILL.md`
- Create: `.agents/skills/figure-design-review/references/review-checklist.md`
- Create: `.agents/skills/figure-reference-manager/SKILL.md`
- Create: `.agents/skills/figure-reference-manager/references/gallery-contract.md`
- Create: `design_system/DESIGN_GUIDE.md`
- Create: `design_system/figure_examples.md`
- Create: `docs/SKILLS_USAGE.md`
- Create: `docs/GALLERY_WORKFLOW.md`
- Create: `docs/FIGURE_EDITING.md`
- Create: `tests/test_skills_structure.py`

**Interfaces:**
- Each `SKILL.md` has YAML front matter with exact `name` and a concise trigger/boundary `description`.
- Every Skill references `AGENTS.md` and specifies inputs, steps, outputs, non-applicable cases, and verification requirements.
- `tests/test_skills_structure.py` validates all four metadata names, required headings, referenced files, and no references to nonexistent project paths.

- [ ] **Step 1: Write the Skill structure test**

```python
@pytest.mark.parametrize("name", SKILL_NAMES)
def test_skill_has_valid_metadata_and_project_reference(name):
    path = ROOT / ".agents" / "skills" / name / "SKILL.md"
    text = path.read_text(encoding="utf-8")
    assert f"name: {name}" in text
    assert "description:" in text
    assert "AGENTS.md" in text
    assert "verification" in text.lower()
```

Run it first and confirm expected missing-file failures.

- [ ] **Step 2: Write four non-overlapping Skill instructions**

`modern-scientific-figure` must require Figure Brief, gallery search, public package usage, actual execution, image viewing, source/config delivery, and revision. `algorithm-visualization` must enforce objective directions, valid error definitions, uncertainty provenance, Pareto dominance, and spatial aspect ratio. `figure-design-review` must inspect actual rendered images at final size and change source before re-rendering. `figure-reference-manager` must protect originals, distinguish facts/estimates/unknowns, update hashes and index, and avoid invented preferences.

- [ ] **Step 3: Write design guides and user docs**

Explain semantic palettes, typography fallback, layout selection, direct labels, uncertainty, vector export, and the six example roles. `FIGURE_EDITING.md` must show a concrete edit:

```python
# templates/convergence/config.py
PRIMARY_COLOR = "#C65D3B"
LINE_WIDTH = 2.2
FIGURE_WIDTH = 6.6
```

Then rerun `python templates/convergence/plot.py` and inspect the changed `figure.png`.

- [ ] **Step 4: Validate paths and commit**

Run `conda run -n scientific-figure-studio pytest tests/test_skills_structure.py -q`, then commit:

```powershell
git add .agents design_system docs/SKILLS_USAGE.md docs/GALLERY_WORKFLOW.md docs/FIGURE_EDITING.md tests/test_skills_structure.py
git commit -m "docs: add project skills and figure guidance"
```

### Task 10: Add font, gallery, and Skill discovery verification

**Files:**
- Create: `tests/test_font_render.py`
- Create: `tests/test_discovery.py`
- Create: `tools/validate_skills.py`
- Create: `figure_gallery/_generated/.gitkeep`

**Interfaces:**
- `tools.validate_skills.main() -> int` returns nonzero for malformed Skill files and zero for valid metadata/references.
- `tests/test_font_render.py` writes a temporary Chinese/English/math PNG and validates nonblank output plus font report warnings.

- [ ] **Step 1: Write failing tests for Chinese rendering and Skill validation**

```python
def test_chinese_math_figure_is_nonblank(tmp_path):
    report = resolve_fonts()
    fig, ax = plt.subplots(figsize=(3.2, 2.2))
    ax.set(xlabel="时间 (小时)", ylabel="误差 $E$", title="中文字体测试")
    ax.plot([0, 1], [1, 0])
    path = tmp_path / "font-test.png"
    fig.savefig(path, dpi=200)
    assert path.stat().st_size > 0
    assert report.english_family
```

Run `conda run -n scientific-figure-studio pytest tests/test_font_render.py tests/test_discovery.py -q`; expected failure until tools and tests exist.

- [ ] **Step 2: Implement Skill validator and test discovery paths**

The validator must parse front matter, check unique names, ensure `AGENTS.md` and reference paths exist, and report whether `.agents/skills` is in the current project. It must not claim the host application loaded a Skill; that status remains separate.

- [ ] **Step 3: Render and inspect the Chinese font test**

Run the test, open the actual PNG with the image viewer, and record whether Chinese glyphs render without missing-box symbols. If the current environment lacks a suitable CJK font, report the exact missing font and keep the fallback instructions in `docs/QUICK_START.md`.

- [ ] **Step 4: Commit verification tools**

```powershell
git add tests/test_font_render.py tests/test_discovery.py tools/validate_skills.py figure_gallery/_generated/.gitkeep
git commit -m "test: verify fonts and skill metadata"
```

### Task 11: Run full generation, inspect all six images, and write the test report

**Files:**
- Modify: `docs/TEST_REPORT.md`
- Modify: `README.md`
- Modify: `docs/QUICK_START.md`
- Modify: each `examples/outputs/fig_*/README.md` if review finds a correction
- Modify: template `plot.py` or `config.py` files if visual review finds a correction

**Interfaces:**
- Final report records exact commands, exit codes, counts, output dimensions, fonts detected, visual findings, limitations, and unverified host Skill behavior.

- [ ] **Step 1: Run the complete automated suite**

Run the fresh full commands:

```powershell
conda run -n scientific-figure-studio pytest -q
conda run -n scientific-figure-studio ruff check .
conda run -n scientific-figure-studio python tools/validate_skills.py
conda run -n scientific-figure-studio python tools/generate_examples.py
```

Read each exit code and capture stdout/stderr before writing any PASS claim.

- [ ] **Step 2: Inspect all six output PNGs and the Chinese font test at full and reduced size**

Use the local image viewer for:

```text
examples/outputs/fig_01_convergence/figure.png
examples/outputs/fig_02_prediction/figure.png
examples/outputs/fig_03_sensitivity/figure.png
examples/outputs/fig_04_pareto/figure.png
examples/outputs/fig_05_spatial/figure.png
examples/outputs/fig_06_composite/figure.png
```

Record concrete observations for clipping, legend overlap, panel spacing, axis units, color distinction, practice-data labeling, and readability after reduction. If any issue is visible, fix the source/config, rerun that template, and inspect again.

- [ ] **Step 3: Exercise one user configuration change**

Copy or edit a temporary convergence config, change `PRIMARY_COLOR`, `LINE_WIDTH`, `FONT_SIZE`, and `FIGURE_WIDTH`, regenerate into a temporary directory, and compare PNG dimensions and pixel hashes. Restore the checked-in example configuration before final verification.

- [ ] **Step 4: Write `docs/TEST_REPORT.md` from actual evidence**

Separate `通过`, `失败`, `未验证`, and `需要用户人工确认`. Include the Conda version, Python version, package versions, pytest count, Ruff result, generated artifact count, PDF/SVG/PNG checks, CJK font result, gallery tests, Skill metadata result, actual image review notes, and the fact that no user gallery images existed at development time.

- [ ] **Step 5: Perform final verification before claiming completion**

Run the complete commands again after the final visual fixes:

```powershell
conda run -n scientific-figure-studio pytest -q
conda run -n scientific-figure-studio ruff check .
git diff --check
git status --short
```

Only after reading this fresh output, update the final README links and provide the Chinese handoff with actual files and test results.

### Task 12: Finish the development branch

**Files:**
- Modify: any remaining files identified by final verification only

- [ ] **Step 1: Read the final diff and status**

Confirm that generated images, source snapshots, manifests, docs, tests, and Skills are tracked, while caches and temporary files remain ignored. Do not use `git reset --hard` or discard unrelated files.

- [ ] **Step 2: Commit the final report and any verified fixes**

```powershell
git add README.md docs examples templates figure_studio tests tools .agents design_system AGENTS.md environment.yml requirements.txt pyproject.toml .gitignore
git commit -m "feat: deliver Scientific Figure Studio first release"
```

- [ ] **Step 3: Run the final test commands again**

Use the commands from Task 11 Step 5 and record their fresh exit codes in the handoff.
