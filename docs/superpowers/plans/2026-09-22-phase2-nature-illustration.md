# Scientific Figure Studio Phase 2 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox syntax for tracking.

**Goal:** Add a legally bounded, fixed-commit Nature Figure Skill integration, repair data/gallery contracts, and deliver Python scientific-illustration templates without regressing the six existing figure templates.

**Architecture:** Keep the upstream nature-figure directory outside the repository and install it locally from a pinned commit with a complete-tree verifier. Add small project adapters for manifest/provenance and Skill context instead of copying or editing upstream files. Extend the existing Matplotlib system with reusable illustration primitives and three self-contained example templates; preserve all user-editable configuration and source-data provenance.

**Tech Stack:** Python 3.11, Matplotlib, NumPy, Pandas, Pillow, PyYAML, pypdf, pytest, Ruff, PowerShell only for documented convenience commands, fixed GitHub codeload archive for the upstream Skill.

## Global Constraints

- Formal plotting, preview, export, and visual QA use Python only.
- The upstream Nature Skill commit is 1930963cbc004da9ac8e3af7944d4f0a3488d3e1.
- The upstream directory is not copied into this repository because the pinned repository contains no identifiable LICENSE/COPYING/NOTICE file.
- Existing six templates remain runnable and continue to export PDF, SVG, and PNG.
- Accepted manifest statuses are formal input data, illustrative practice data, and unknown source data.
- No source data, gallery original, user evaluation, outlier, or unsupported scientific claim may be fabricated, hidden, or overwritten.
- Every new figure delivery contains plot.py, config.py, data_manifest.json, README.md, figure.png, figure.svg, and figure.pdf.
- Every behavior change follows TDD: write a focused failing test, run it and inspect the expected failure, implement the minimum behavior, then refactor while green.
- Use pathlib for paths and the project Conda environment for Python, pytest, and Ruff.

## Plan self-review

The plan covers the spec's upstream, manifest, gallery, six-template, illustration, Skill, documentation, rendering, visual-review, and reporting requirements. No file is referenced as a future placeholder; each task defines its testable interface and verification command. The tasks are ordered so shared contracts precede dependent templates, while each task has its own focused test cycle.

---

### Task 1: Establish Phase 2 failing contracts

**Files:**
- Create: tests/test_nature_integration.py
- Create: tests/test_manifest.py
- Create: tests/test_illustration_templates.py
- Modify: tests/test_gallery.py
- Modify: tests/test_skills_structure.py
- Modify: tests/conftest.py only if a shared project-root or Conda subprocess helper is missing

**Interfaces:**
- Tests define the required public names figure_studio.manifest.load_manifest, figure_studio.manifest.resolve_data_path, figure_studio.nature_adapter.build_nature_context, figure_studio.illustrations.validate_flow_edges, and the three illustration template main functions.
- Tests use temporary directories for installed Skills, gallery indexes, external CSV files, and rendered outputs.

- [ ] Step 1: Write the failing upstream contract test

~~~python
def test_pinned_nature_tree_contract_requires_complete_install(tmp_path):
    result = verify_nature_tree(tmp_path / "nature-figure")
    assert result.commit == PINNED_COMMIT
    assert result.file_count == 30
~~~

Also assert that the adapter rejects a tree whose SKILL.md exists but whose references/assets are missing.

- [ ] Step 2: Write the failing manifest tests

~~~python
def test_manifest_resolves_external_data_without_rewriting_input(tmp_path):
    data_path = tmp_path / "formal.csv"
    data_path.write_text("x,y\n1,2\n", encoding="utf-8")
    manifest = {"data_status": "formal input data", "data_file": str(data_path)}
    loaded = load_manifest(manifest, base_dir=Path.cwd())
    assert loaded.data_path == data_path.resolve()
    assert loaded.data_status == "formal input data"
~~~

Add tests for all three status values and rejection of unknown statuses.

- [ ] Step 3: Write the failing gallery and illustration contracts

Create an image, scan it, edit user_evaluation and favorite in gallery_index.csv, rescan, and expect both values to survive. Assert that a newly scanned image is not_analyzed; call record_agent_analysis() and assert only the explicit image becomes agent_reviewed. Add tests that invalid flowchart endpoints fail and that all three new illustration folders contain source/config/manifest/README.

- [ ] Step 4: Extend Skill discovery expectations

Add scientific-illustration to the project Skill names and require its reference path, AGENTS.md mention, inputs, outputs, non-applicable cases, and verification section.

- [ ] Step 5: Run focused tests and verify RED

Run:

~~~powershell
& 'C:\Users\Administrator\miniconda3\Scripts\conda.exe' run -n scientific-figure-studio pytest tests/test_nature_integration.py tests/test_manifest.py tests/test_illustration_templates.py tests/test_gallery.py tests/test_skills_structure.py -q
~~~

Expected: failures report missing new modules, missing Skill directory, or missing behavior; the pre-existing gallery and Skill tests must remain distinguishable from the new failures.

- [ ] Step 6: Commit the contract tests

~~~powershell
git add tests
git commit -m "test: define phase two nature data gallery and illustration contracts"
~~~

### Task 2: Implement fixed-commit Nature Skill installation and context loading

**Files:**
- Create: tools/install_nature_figure.py
- Create: tools/verify_nature_figure.py
- Create: tools/nature_figure_lock.py
- Create: figure_studio/nature_adapter.py
- Create: docs/UPSTREAM_NATURE_FIGURE.md
- Modify: tests/test_nature_integration.py

**Interfaces:**
- tools.install_nature_figure.install(destination: Path, force: bool = False) -> Path
- tools.verify_nature_figure.verify_nature_tree(path: Path) -> NatureTreeReport
- figure_studio.nature_adapter.build_nature_context(skill_root: Path, references: tuple[str, ...]) -> dict[str, object]
- figure_studio.nature_adapter.require_nature_context(skill_root: Path) -> dict[str, object]

- [ ] Step 1: Implement exact-tree constants and verifier

Store the pinned commit, codeload URL, expected 30 relative paths, and expected SHA-256 hashes in tools/nature_figure_lock.py. The verifier must reject missing, extra, or hash-mismatched files and return the commit plus file count. It must not inspect or modify project gallery files.

- [ ] Step 2: Run integration tests and verify GREEN for local verification fixtures

Run the focused upstream tests against a fixture containing the expected path/hash manifest. Confirm the incomplete-tree test fails with a useful message and the complete fixture passes.

- [ ] Step 3: Implement the installer using a temporary archive

Download only the fixed commit archive, extract skills/codex/nature-figure, verify before installation, and install atomically into the requested target. Default to Path.home() / ".codex" / "skills" / "nature-figure"; reject an existing target unless force=True, and when forced move it to a timestamped backup before replacement. Do not write upstream content into the repository.

- [ ] Step 4: Implement the context adapter

Read SKILL.md, references/figure-contract.md, references/common-patterns.md, and references/qa-contract.md; record their SHA-256 values, the pinned commit, the complete-tree report, and the adapter version. Reject a reference outside the verified tree. require_nature_context() must fail rather than silently falling back to a project-only claim.

- [ ] Step 5: Write the upstream record

Document the fixed URL, commit date, 30-file tree, no-license-file finding, Python dependencies described by upstream files, installation commands for Windows/PowerShell and Python, verification command, and the distinction between local source loading and a Codex session's Skill index refresh.

- [ ] Step 6: Run focused tests and commit

~~~powershell
& 'C:\Users\Administrator\miniconda3\Scripts\conda.exe' run -n scientific-figure-studio pytest tests/test_nature_integration.py -q
& 'C:\Users\Administrator\miniconda3\Scripts\conda.exe' run -n scientific-figure-studio python tools/verify_nature_figure.py --help
git add figure_studio tools docs/UPSTREAM_NATURE_FIGURE.md tests/test_nature_integration.py
git commit -m "feat: add pinned nature figure skill integration"
~~~

### Task 3: Add manifest and provenance support for formal/external data

**Files:**
- Create: figure_studio/manifest.py
- Modify: figure_studio/export.py
- Modify: templates/*/plot.py where data status or relative paths are hard-coded
- Modify: all six templates/*/data_manifest.json files only to add explicit fields without changing practice values
- Modify: tests/test_manifest.py
- Modify: tests/test_export_validation.py if provenance assertions need extension

**Interfaces:**
- ManifestInfo.data_status: str
- ManifestInfo.data_path: Path
- ManifestInfo.fields: dict[str, object]
- ManifestInfo.objective_direction: str | None
- load_manifest(path_or_mapping: str | Path | Mapping[str, object], base_dir: Path | None = None) -> ManifestInfo
- resolve_data_path(data_file: str | Path, base_dir: Path) -> Path
- provenance_data_label(status: str) -> str | None

- [ ] Step 1: Add failing edge-case tests

Cover a relative data path, an external absolute path, a missing file, all three statuses, a manifest with objective direction, and a provenance record that omits the practice watermark for formal data.

- [ ] Step 2: Implement validation and path resolution

Use Path.expanduser().resolve() for external paths; resolve relative paths against the manifest directory; never copy, rewrite, or mutate the input file. Preserve the original manifest string for provenance and compute SHA-256 from the actual resolved file.

- [ ] Step 3: Update export provenance

Make status, source path, source hash, field descriptions, transformations, uncertainty basis, and unsupported claims explicit. Keep existing PDF/SVG/PNG validation behavior unchanged.

- [ ] Step 4: Update all six templates to use the shared loader

Replace literal illustrative practice data provenance with the manifest status. Keep the checked-in practice manifests unchanged in meaning and preserve the visible practice note only for practice data.

- [ ] Step 5: Run focused and regression tests

~~~powershell
& 'C:\Users\Administrator\miniconda3\Scripts\conda.exe' run -n scientific-figure-studio pytest tests/test_manifest.py tests/test_export_validation.py tests/test_template_contracts.py -q
~~~

- [ ] Step 6: Commit

~~~powershell
git add figure_studio templates tests
git commit -m "feat: validate manifest status and external data provenance"
~~~

### Task 4: Repair convergence and prediction assumptions

**Files:**
- Modify: templates/convergence/plot.py
- Modify: templates/convergence/config.py
- Modify: templates/convergence/data_manifest.json
- Modify: templates/convergence/README.md
- Modify: templates/prediction/plot.py
- Modify: templates/prediction/config.py
- Modify: templates/prediction/data_manifest.json
- Modify: templates/prediction/README.md
- Modify: tests/test_convergence_template.py
- Modify: tests/test_prediction_template.py

**Interfaces:**
- convergence.load_data(path: Path, manifest_path: Path | None = None) -> pd.DataFrame
- convergence.build_figure(frame: pd.DataFrame, config: Mapping[str, object], manifest: ManifestInfo | None = None) -> Figure
- prediction.load_data(path: Path, manifest_path: Path | None = None) -> pd.DataFrame
- prediction.build_figure(frame: pd.DataFrame, config: Mapping[str, object], manifest: ManifestInfo | None = None) -> Figure

- [ ] Step 1: Write failing direction and optional-split tests

~~~python
def test_convergence_uses_maximum_running_best_when_manifest_says_maximize():
    frame = pd.DataFrame({"algorithm": ["A"] * 3, "iteration": [1, 2, 3], "objective": [1.0, 3.0, 2.0]})
    result = build_running_best(frame, objective_direction="maximize")
    assert result.tolist() == [1.0, 3.0, 3.0]

def test_prediction_accepts_only_test_split_and_computes_metrics_only_there():
    frame = load_data(DATA / "prediction_test_only.csv")
    figure = build_figure(frame, CONFIG)
    assert "Test RMSE" in " ".join(text.get_text() for text in figure.texts)
~~~

Add a no-split-column test that receives an all label and a no-test test that does not display test metrics.

- [ ] Step 2: Run focused tests and confirm RED

~~~powershell
& 'C:\Users\Administrator\miniconda3\Scripts\conda.exe' run -n scientific-figure-studio pytest tests/test_convergence_template.py tests/test_prediction_template.py -q
~~~

- [ ] Step 3: Implement direction-aware convergence

Read objective_direction from manifest/config, call running_best with that value, label the direction in the manifest/provenance, and keep current objective traces distinct from historical best traces. Do not alter CSV values.

- [ ] Step 4: Implement optional prediction splits

Treat a missing split column as all; otherwise preserve every input split label. Build split colors/markers from config with a deterministic fallback for unseen labels. Compute RMSE/MAE only for test rows when present, otherwise omit the metric annotation. Do not require train/validation/test as a set.

- [ ] Step 5: Update manifests and READMEs

Describe optional splits, metric subsets, objective direction, units, and absence of intervals. Keep all example values explicitly illustrative.

- [ ] Step 6: Run focused tests, then all existing template tests

~~~powershell
& 'C:\Users\Administrator\miniconda3\Scripts\conda.exe' run -n scientific-figure-studio pytest tests/test_convergence_template.py tests/test_prediction_template.py tests/test_template_contracts.py -q
~~~

- [ ] Step 7: Commit

~~~powershell
git add templates/convergence templates/prediction tests/test_convergence_template.py tests/test_prediction_template.py
git commit -m "fix: make convergence and prediction templates data-driven"
~~~

### Task 5: Separate deterministic gallery scanning from Agent visual analysis

**Files:**
- Modify: figure_studio/gallery.py
- Modify: tools/update_gallery.py
- Modify: figure_gallery/README.md
- Modify: figure_gallery/GALLERY_GUIDE.md
- Modify: tests/test_gallery.py
- Modify: tests/test_analysis.py only if gallery analysis imports are covered there

**Interfaces:**
- GalleryRecord.visual_analysis_status: str
- GalleryRecord.visual_analysis_date: str
- GalleryRecord.visual_analysis_by: str
- GalleryRecord.visual_analysis_notes: str
- GalleryIndex.record_agent_analysis(relative_path: str, observations: Mapping[str, object], analyzed_by: str = "codex") -> GalleryRecord
- GalleryIndex.scan() -> list[GalleryRecord]

- [ ] Step 1: Add failing tests for preservation and status

Create an image, scan it, edit its CSV row with a hand-written evaluation and favorite flag, rescan, and assert both remain. Assert new images are not_analyzed; call record_agent_analysis() and assert only the explicit image is agent_reviewed. Assert deterministic note regeneration does not overwrite the separate visual-analysis note.

- [ ] Step 2: Run gallery tests and verify RED

~~~powershell
& 'C:\Users\Administrator\miniconda3\Scripts\conda.exe' run -n scientific-figure-studio pytest tests/test_gallery.py -q
~~~

- [ ] Step 3: Extend CSV schema compatibly

Add visual-analysis columns with safe defaults when reading older indexes. Keep user_evaluation and all existing user-editable fields separate from generated factual fields. Treat missing/invalid old values as empty or not_analyzed, never as completed analysis.

- [ ] Step 4: Make scan incremental and non-destructive

Only regenerate deterministic notes when the image hash or note is missing. Preserve existing records for unchanged images by relative path and hash. Store Agent observations under _generated/gallery_visual_analysis/ keyed by SHA-256; never place files beside originals or in favorites.

- [ ] Step 5: Add explicit Agent-analysis API and documentation

The API must require observations supplied by the caller and must not infer chart type, font, source, conclusion, or preference. Document that an Agent must open the PNG with the local image viewer before calling it; absent that step the status remains not_analyzed.

- [ ] Step 6: Run tests and commit

~~~powershell
& 'C:\Users\Administrator\miniconda3\Scripts\conda.exe' run -n scientific-figure-studio pytest tests/test_gallery.py -q
git add figure_studio/gallery.py tools/update_gallery.py figure_gallery tests/test_gallery.py
git commit -m "fix: separate gallery facts and agent visual analysis"
~~~

### Task 6: Add reusable Python illustration primitives

**Files:**
- Create: figure_studio/illustrations.py
- Create: tests/test_illustrations.py
- Modify: figure_studio/__init__.py only if public exports are part of the existing package convention

**Interfaces:**
- validate_flow_edges(nodes: Mapping[str, object], edges: Iterable[Mapping[str, object]]) -> None
- draw_flowchart(ax, nodes, edges, config) -> None
- draw_architecture(ax, modules, connections, config) -> None
- draw_geometry(ax, points, constraints, config) -> None
- draw_network(ax, nodes, edges, config) -> None
- draw_surface(ax, x, y, z, config) -> None
- add_panel_label(ax, label, config) -> None

- [ ] Step 1: Write failing primitive tests

Test missing flow endpoints, duplicate node IDs, unknown architecture connection endpoints, equal geometry aspect, preserved node labels, and a 3D surface accepting finite arrays. Do not assert private implementation details.

- [ ] Step 2: Run primitive tests and verify RED

~~~powershell
& 'C:\Users\Administrator\miniconda3\Scripts\conda.exe' run -n scientific-figure-studio pytest tests/test_illustrations.py -q
~~~

- [ ] Step 3: Implement validation and drawing helpers

Use Matplotlib patches and FancyArrowPatch for directed edges, explicit coordinates from input structures, set_aspect("equal") for planar geometry, and projection="3d" for surfaces. Do not add modules, edges, coordinates, or labels not supplied by the caller. Keep colors, widths, fonts, arrow style, node padding, and output settings in the caller's config.

- [ ] Step 4: Run focused tests and Ruff

~~~powershell
& 'C:\Users\Administrator\miniconda3\Scripts\conda.exe' run -n scientific-figure-studio pytest tests/test_illustrations.py -q
& 'C:\Users\Administrator\miniconda3\Scripts\conda.exe' run -n scientific-figure-studio ruff check figure_studio/illustrations.py tests/test_illustrations.py
~~~

- [ ] Step 5: Commit

~~~powershell
git add figure_studio/illustrations.py tests/test_illustrations.py
git commit -m "feat: add structured scientific illustration primitives"
~~~

### Task 7: Create and verify the scientific-illustration Skill

**Files:**
- Create: .agents/skills/scientific-illustration/SKILL.md
- Create: .agents/skills/scientific-illustration/references/illustration-contract.md
- Modify: tests/test_skills_structure.py
- Create: tests/test_scientific_illustration_skill.py

**Interfaces:**
- The Skill front matter uses name: scientific-illustration and a trigger-only description beginning with Use when....
- The Skill documents inputs, Figure Brief, structure contracts, non-applicable cases, Python tools, source/config/manifest outputs, actual rendering, image viewing, and scientific verification.

- [ ] Step 1: Write failing structure and pressure tests

Check metadata, required headings, references to AGENTS.md, figure_studio.illustrations, structured input, no-invented-modules rule, geometry aspect, directed-edge semantics, 3D data basis, and visual verification. Add a pressure fixture asserting the Skill does not turn an architecture request into a generic line chart.

- [ ] Step 2: Run Skill tests and verify RED

~~~powershell
& 'C:\Users\Administrator\miniconda3\Scripts\conda.exe' run -n scientific-figure-studio pytest tests/test_scientific_illustration_skill.py tests/test_skills_structure.py -q
~~~

- [ ] Step 3: Write minimal Skill and reference

Describe the six supported illustration families, exact structure requirements, data/structure status labels, what to do when model information is missing, and the mandatory delivery/verification contract. Keep the description focused on triggers and keep process detail in the body.

- [ ] Step 4: Run tests and Ruff

~~~powershell
& 'C:\Users\Administrator\miniconda3\Scripts\conda.exe' run -n scientific-figure-studio pytest tests/test_scientific_illustration_skill.py tests/test_skills_structure.py -q
& 'C:\Users\Administrator\miniconda3\Scripts\conda.exe' run -n scientific-figure-studio ruff check tests
~~~

- [ ] Step 5: Commit

~~~powershell
git add .agents/skills/scientific-illustration tests/test_scientific_illustration_skill.py tests/test_skills_structure.py
git commit -m "feat: add scientific illustration skill"
~~~

### Task 8: Deliver flowchart, architecture, and composite Figure templates

**Files:**
- Create: templates/illustration/flowchart/plot.py
- Create: templates/illustration/flowchart/config.py
- Create: templates/illustration/flowchart/data_manifest.json
- Create: templates/illustration/flowchart/README.md
- Create: templates/illustration/architecture/plot.py
- Create: templates/illustration/architecture/config.py
- Create: templates/illustration/architecture/data_manifest.json
- Create: templates/illustration/architecture/README.md
- Create: templates/illustration/composite/plot.py
- Create: templates/illustration/composite/config.py
- Create: templates/illustration/composite/data_manifest.json
- Create: templates/illustration/composite/README.md
- Create: examples/data/illustration_flowchart.json
- Create: examples/data/illustration_architecture.json
- Create: examples/data/illustration_composite.csv
- Create: tests/test_illustration_templates.py

**Interfaces:**
- Each template exposes load_data(path: Path), build_figure(data, config) -> Figure, and main(output_dir: Path | None = None, data_path: Path | None = None) -> dict[str, Path].
- Each template config is the single source for canvas, palette, line widths, fonts, labels, output formats, and limits.

- [ ] Step 1: Add failing template contract tests

Assert that each template reads its JSON/CSV input, preserves explicit node/edge structure, exports PDF/SVG/PNG, includes a practice/example-structure statement, and returns artifact paths.

- [ ] Step 2: Run focused tests and verify RED

~~~powershell
& 'C:\Users\Administrator\miniconda3\Scripts\conda.exe' run -n scientific-figure-studio pytest tests/test_illustration_templates.py -q
~~~

- [ ] Step 3: Implement algorithm flowchart

Use explicit node IDs and directed edges with branch labels; validate every endpoint; draw terminal, process, decision, and merge shapes according to the input role. The manifest must say illustrative example structure and not claim algorithm performance.

- [ ] Step 4: Implement model architecture

Use only the supplied module list and connections. Draw input, encoder, solver, decoder, and output roles only because they are present in the example JSON; label the example as illustrative and do not present it as a user model.

- [ ] Step 5: Implement mixed-modality composite

Use an asymmetric GridSpec with one hero quantitative panel and two smaller schematic/evidence panels. Use practice CSV values and a separate structure JSON; retain a visible evidence note, shared colors, panel labels, and units.

- [ ] Step 6: Run focused tests and actual template rendering

~~~powershell
& 'C:\Users\Administrator\miniconda3\Scripts\conda.exe' run -n scientific-figure-studio pytest tests/test_illustration_templates.py -q
& 'C:\Users\Administrator\miniconda3\Scripts\conda.exe' run -n scientific-figure-studio python templates/illustration/flowchart/plot.py
& 'C:\Users\Administrator\miniconda3\Scripts\conda.exe' run -n scientific-figure-studio python templates/illustration/architecture/plot.py
& 'C:\Users\Administrator\miniconda3\Scripts\conda.exe' run -n scientific-figure-studio python templates/illustration/composite/plot.py
~~~

- [ ] Step 7: Commit

~~~powershell
git add templates/illustration examples/data/illustration_*.json examples/data/illustration_composite.csv tests/test_illustration_templates.py
git commit -m "feat: add reproducible scientific illustration templates"
~~~

### Task 9: Add Nature-adapted chart example and documentation accuracy checks

**Files:**
- Create: templates/nature_adapter/plot.py
- Create: templates/nature_adapter/config.py
- Create: templates/nature_adapter/data_manifest.json
- Create: templates/nature_adapter/README.md
- Create: tests/test_nature_adapter_example.py
- Create: tests/test_documentation_examples.py
- Modify: README.md
- Modify: docs/SKILLS_USAGE.md
- Modify: docs/GALLERY_WORKFLOW.md
- Modify: docs/QUICK_START.md
- Modify: docs/FIGURE_EDITING.md

**Interfaces:**
- templates.nature_adapter.plot.main() produces a chart using require_nature_context() and writes nature_context.json beside the figure provenance.
- Documentation tests extract PowerShell/Python command blocks and check referenced project files and template paths exist.

- [ ] Step 1: Write failing adapter/example tests

Assert that the chart refuses to claim Nature integration when the verified Skill tree is absent, records the pinned commit and the three loaded references when present, and exports editable SVG/PDF plus PNG.

- [ ] Step 2: Run focused tests and verify RED

~~~powershell
& 'C:\Users\Administrator\miniconda3\Scripts\conda.exe' run -n scientific-figure-studio pytest tests/test_nature_adapter_example.py tests/test_documentation_examples.py -q
~~~

- [ ] Step 3: Implement the adapter figure

Use a practice convergence dataset or another existing practice dataset, apply the upstream Figure Contract/evidence hierarchy and Python export rules through the project adapter, use figure_studio colors/layout, and write Skill context with exact hash data. Documentation must distinguish upstream principles from project implementation.

- [ ] Step 4: Repair documentation examples

Update broken field names, commands, paths, and output expectations found by the doc test. Add fixed-SHA installation and verification instructions, Python-only policy, the new Skill, and external formal-data usage.

- [ ] Step 5: Run focused tests, Ruff, and commit

~~~powershell
& 'C:\Users\Administrator\miniconda3\Scripts\conda.exe' run -n scientific-figure-studio pytest tests/test_nature_adapter_example.py tests/test_documentation_examples.py -q
& 'C:\Users\Administrator\miniconda3\Scripts\conda.exe' run -n scientific-figure-studio ruff check figure_studio tools templates tests
git add templates/nature_adapter tests README.md docs
git commit -m "docs: document pinned nature workflow and phase two examples"
~~~

### Task 10: Run fixed-SHA integration, gallery exercise, and full generation

**Files:**
- Create or update: examples/outputs/fig_07_nature_adapter/
- Create or update: examples/outputs/fig_08_illustration_flowchart/
- Create or update: examples/outputs/fig_09_illustration_architecture/
- Create or update: examples/outputs/fig_10_illustration_composite/
- Modify: docs/TEST_REPORT.md
- Modify: README.md only for verified final links

**Interfaces:**
- Every generated directory contains source, config, manifest, README, PDF, SVG, PNG, and generation/provenance metadata.
- The final report separates code status, executed commands, automated pass/fail, opened images, unverified host behavior, and user confirmation items.

- [ ] Step 1: Install and verify the pinned upstream tree locally

Run the installer into the user Codex Skills directory, then run the verifier and record exact output. Do not copy installed files into the repository.

~~~powershell
& 'C:\Users\Administrator\miniconda3\Scripts\conda.exe' run -n scientific-figure-studio python tools/install_nature_figure.py --destination "$env:USERPROFILE\.codex\skills\nature-figure"
& 'C:\Users\Administrator\miniconda3\Scripts\conda.exe' run -n scientific-figure-studio python tools/verify_nature_figure.py --path "$env:USERPROFILE\.codex\skills\nature-figure"
~~~

- [ ] Step 2: Run the Nature-adapted example with installed context

Record nature_context.json, the pinned commit, loaded references, output formats, and exit status. State explicitly whether the current Codex process dynamically refreshed its Skill index; do not infer that from a successful local file read.

- [ ] Step 3: Run all six existing examples and three illustration examples

Use tools/generate_examples.py for the six existing templates and the new template commands for the additional deliveries. Check that external output directories do not write into figure_gallery.

- [ ] Step 4: Exercise a real configuration change

Copy a template config into a temporary directory, change primary color, line width, and figure width, rerender to a temporary output directory, and compare PNG dimensions and SHA-256 with the baseline. Restore checked-in configs before final run.

- [ ] Step 5: Exercise gallery protection

Create a temporary reference image, scan it, write a manual evaluation/favorite into the generated index, rescan, and compare fields. Open the image with the local viewer only if documenting an actual Agent visual-analysis record; otherwise keep status not_analyzed.

- [ ] Step 6: Open every new PNG and inspect at full/reduced size

Use the local image viewer on the Nature-adapted chart, flowchart, architecture diagram, composite Figure, and existing six example PNGs. Record concrete findings for clipping, overlap, arrow/branch semantics, aspect ratio, text hierarchy, color meaning, units, practice labels, and final-size readability. Fix source/config and rerender if any issue is visible.

- [ ] Step 7: Run complete verification suite

~~~powershell
& 'C:\Users\Administrator\miniconda3\Scripts\conda.exe' run -n scientific-figure-studio pytest -q
& 'C:\Users\Administrator\miniconda3\Scripts\conda.exe' run -n scientific-figure-studio ruff check .
& 'C:\Users\Administrator\miniconda3\Scripts\conda.exe' run -n scientific-figure-studio python tools/validate_skills.py
& 'C:\Users\Administrator\miniconda3\Scripts\conda.exe' run -n scientific-figure-studio python tools/verify_nature_figure.py --path "$env:USERPROFILE\.codex\skills\nature-figure"
git diff --check
~~~

- [ ] Step 8: Write evidence-based test report

Include Python/Conda/package versions, pytest count and exit code, Ruff exit code, fixed-SHA verifier output, generated artifact count, PDF/SVG/PNG validation, gallery preservation result, documentation command result, every opened image, concrete visual findings/fixes, and unverified Codex Skill-index refresh status.

- [ ] Step 9: Commit final verified artifacts and report

~~~powershell
git add README.md docs examples/outputs
git commit -m "test: record phase two rendering and verification evidence"
~~~

### Task 11: Final review gate

**Files:**
- Read-only: all changed files and git diff
- Modify only if a fresh verification identifies a concrete defect: the affected source/config/test/report file

- [ ] Step 1: Review status and diff

Run git status --short, git diff --stat HEAD~10..HEAD, and inspect generated-file paths. Confirm no upstream Skill content, gallery original, cache, or temporary file was accidentally staged.

- [ ] Step 2: Request code review

Use requesting-code-review with the final diff, this plan, the spec, the full test result, and the visual-review notes. Fix all Critical and Important findings before claiming completion.

- [ ] Step 3: Run fresh final verification

Repeat pytest, Ruff, Skill validation, upstream verification, git diff --check, and final image existence/size checks after any review fix.

- [ ] Step 4: Report completion without overstating host behavior

State exactly which functions and commands were executed, which PNGs were opened, which checks passed or failed, and which Codex runtime behaviors remain dependent on restarting or refreshing the Skill index.
