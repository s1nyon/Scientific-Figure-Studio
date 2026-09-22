# Nature-first Documentation Refinement Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Align the current project documentation and local Skills with the Nature-first Python workflow, scientific-accuracy constraints, evidence-aware gallery usage, and current CLI/API behavior.

**Architecture:** Keep the existing five project Skills, renderer, gallery API, templates, and fixed upstream Nature Skill unchanged. Update the existing global guidance, user-facing documentation, design references, unified workflow Skill, and gallery Skill so each document owns only its appropriate layer and links to the others instead of duplicating a second architecture.

**Tech Stack:** Markdown, existing Python CLI/API, PowerShell validation commands, pytest, Ruff, Git.

## Global Constraints

- Only modify documentation and project Skill instructions; do not modify the upstream `nature-figure` Skill, Python plotting library, templates, gallery originals, accepted works, or historical figures.
- Treat `illustrative practice data` as non-scientific practice input and never invent data, results, uncertainty, user preference, or scientific claims.
- Keep `modern-scientific-figure` as the single project drawing entry point; do not require every task to invoke every Skill or every template.
- Preserve complete editable Python source, configuration, input/manifest provenance, and actual visual inspection requirements for formal figures.
- Distinguish automatic tests, scientific-content review, opened-image review, user acceptance, and accepted-gallery status.
- Use relative links and `pathlib`/existing interfaces as documented; do not add a new global rules file or a duplicate unified-entry Skill.

---

### Task 1: Rewrite the global contract and user-facing project orientation

**Files:**
- Modify: `AGENTS.md`
- Modify: `README.md`
- Modify: `docs/QUICK_START.md`
- Modify: `docs/FIGURE_EDITING.md`

**Interfaces:**
- Consumes: Existing project commands `tools/run_figure_task.py`, `tools/manage_figure_work.py`, the five `.agents/skills/*/SKILL.md` files, and the accepted Design A record.
- Produces: A concise current contract that labels Nature-first as the active workflow, templates as optional implementation material, and historical reports as evidence rather than current instructions.

- [x] **Step 1: Replace stale global completion criteria in `AGENTS.md`**

  Keep data truthfulness, gallery protection, source delivery, safe Git behavior, and the data-check → design → Python → render → open → refine → deliver sequence. Replace the six-template first-phase completion gate with current-stage rules: Figure Brief before design, explicit evidence/claim checks, actual image review, provenance delivery, and separate A–E acceptance states. State that local design presets and panel counts are recommendations, not universal constraints.

- [x] **Step 2: Reframe `README.md` around the current Nature-first workflow**

  Lead with project purpose, Nature-first routing, Python source delivery, gallery/reference boundaries, candidate/accepted work protection, supported figure families, and capability limits. Keep template commands under an explicitly optional “template examples” section. Link historical reports without restating their old counts or treating them as current acceptance criteria.

- [x] **Step 3: Add a real formal-use path to `docs/QUICK_START.md`**

  Add a copyable flow from opening the project and checking Skill discovery through providing data/model context, invoking `$modern-scientific-figure`, selecting applicable specialist/reference capabilities, rendering with Python, opening the image, delivering source/config/manifest/reproduction notes, revising from natural-language feedback, and explicitly accepting a candidate. Keep the convergence command as a template example, and use only the actual runner flags and acceptance commands.

- [x] **Step 4: Clarify source-based editing and status boundaries in `docs/FIGURE_EDITING.md`**

  Preserve the existing config examples but state that a local visual tweak is not a reason to redesign every figure, that scientific changes require manifest updates, and that a changed PNG is not a completed delivery until all formats and provenance are regenerated. Explain candidate/workspace/accepted protection without suggesting ordinary overwrite can change accepted work.

- [x] **Step 5: Run Markdown link/path and diff checks for Task 1**

  Run:

  ```powershell
  git diff --check
  rg -n "六类模板|第一版完成|默认.*模板|全部.*Skill|顶刊质量|record_agent_analysis" AGENTS.md README.md docs/QUICK_START.md docs/FIGURE_EDITING.md
  ```

  Expected: no stale first-phase completion rule remains in the global contract; any remaining template mention is explicitly optional or historical.

- [x] **Step 6: Commit Task 1**

  ```powershell
  git add AGENTS.md README.md docs/QUICK_START.md docs/FIGURE_EDITING.md
  git commit -m "docs: establish current nature-first project contract"
  ```

### Task 2: Make design guidance flexible while preserving scientific evidence rules

**Files:**
- Modify: `.agents/skills/modern-scientific-figure/SKILL.md`
- Modify: `design_system/DESIGN_GUIDE.md`
- Modify: `design_system/layout_rules.md`
- Modify: `docs/SKILLS_USAGE.md`

**Interfaces:**
- Consumes: Current `FigureBrief` fields, `tools/run_figure_task.py` flags, existing specialist Skill names, `figure_studio.gallery.search_references()`, and the fixed upstream Nature Skill boundary.
- Produces: A unified entry workflow that chooses design from the scientific claim and evidence, uses references conditionally, and records actual execution/review status without imposing a fixed layout or palette.

- [x] **Step 1: Add claim/evidence-first design decisions to `modern-scientific-figure`**

  Require a Figure Brief that states the claim, supporting data, evidence panels, unknowns, units, and review risks before selecting the figure archetype. Require an explicit necessity check for each auxiliary panel, while allowing multiple panels when they answer distinct scientific questions. Preserve the three modes (`ordinary`, `core-practice`, `formal`) and make two drafts conditional on `core-practice` only.

- [x] **Step 2: Add reference matching and anti-path-dependence rules**

  Tell the Agent to inspect user-specified gallery images before using them, retrieve only a small set of task-matched cases when needed, and separate observed design methods from user evaluation, code references, and scientific provenance. Permit Nature-first autonomous design when the gallery is empty or mismatched. For overall redesigns, reassess chart type, information hierarchy, and layout from the current task instead of only recoloring the previous `plot.py`; local edits remain local.

- [x] **Step 3: Strengthen visual QA without subjective scores**

  Require checks for evidence emphasis, reading order, auxiliary-panel value, annotation/data consistency, text occupancy, density-to-size fit, and final paper-size readability in addition to clipping/fonts/legends. State that systemic issues trigger design reassessment and local issues trigger source/config refinement. Do not add fixed iteration counts, visual scores, or unverifiable quality certifications.

- [x] **Step 4: Convert the design-system documents from defaults to optional references**

  Keep `minimal_editorial`, `algorithm_research`, and `visual_narrative` as selectable directions. Remove language implying all figures must use the same blue/teal/orange palette or fixed panel structure. Record the round-four lessons with conditions: simple data may remain single-panel, multi-panel figures need distinct evidence roles, long explanations may belong in captions, direct labels depend on density, and paper-size readability outranks full-screen appearance. State that templates and Design A are reusable references, not universal layouts.

- [x] **Step 5: Make `docs/SKILLS_USAGE.md` the concise operational routing reference**

  Keep one end-to-end flow and link to the detailed Skill/design/gallery documents. Include minimal copyable prompts for new Figure, redesign from image, specified gallery reference, scientific illustration, local edit with Before/After, and accepted-work save. Keep the real runner command with `--renderer`, `--brief`, `--output-dir`, optional `--data-path`, `--manifest-path`, `--nature-skill-root`, `--version-status`, `--review-status`, and `--host-skill-invocation-status` only where relevant; do not imply the runner itself invokes the host Nature Skill.

- [x] **Step 6: Commit Task 2**

  ```powershell
  git add .agents/skills/modern-scientific-figure/SKILL.md design_system/DESIGN_GUIDE.md design_system/layout_rules.md docs/SKILLS_USAGE.md
  git commit -m "docs: make figure design decisions task driven"
  ```

### Task 3: Correct gallery provenance and accepted-work reuse guidance

**Files:**
- Modify: `.agents/skills/figure-reference-manager/SKILL.md`
- Modify: `figure_gallery/README.md`
- Modify: `figure_gallery/GALLERY_GUIDE.md`
- Modify: `docs/GALLERY_WORKFLOW.md`
- Verify without modifying: `figure_gallery/05_my_work/round_04_design_a_accepted/accepted_reference_case.md`

**Interfaces:**
- Consumes: `GalleryIndex.record_agent_analysis(relative_path, observations, analyzed_by="codex", *, viewed, view_receipt)`, `search_references(gallery_root, query, *, chart_type, application, limit)`, `search_work_references(...)`, `tools/record_gallery_analysis.py`, and `tools/manage_figure_work.py` subcommands.
- Produces: Executable gallery examples and explicit separation of file facts, opened-image observations, user evaluation, scientific content, and source/reproduction provenance.

- [x] **Step 1: Correct the Python `record_agent_analysis()` example**

  Update `figure_gallery/GALLERY_GUIDE.md` to pass `viewed=True` and a non-empty `view_receipt`, for example `{"viewer": "view_image", "path": "...", "dimensions_px": "..."}`. Explain that this call requires actual image viewing and writes generated analysis/index data without changing the original.

- [x] **Step 2: Document the CLI alternative with real flags**

  Add or correct the `tools/record_gallery_analysis.py` example using `--gallery-root`, `--image`, `--observations`, `--view-receipt`, and optional `--analyzed-by`. Keep `update_gallery.py` as the deterministic scan command and distinguish it from semantic Agent analysis.

- [x] **Step 3: State gallery information boundaries and external-image restrictions**

  Separate scanner facts, image-view observations, user-written evaluation, scientific meaning/data source, and code/reproduction links. State unknown/estimated fields when pixels cannot establish exact font/data/claim. Preserve external-source/license caution and forbid public redistribution assumptions, automatic favorites, and original-image mutation.

- [x] **Step 4: Preserve Design A’s accepted scope**

  Link the accepted case and state that it is a user-accepted algorithm-convergence visual reference with illustrative practice data, explicit technical observations, suitable scenarios, and reuse limits. Do not call it a universal template, top-journal certification, scientific validation, or global user preference; do not modify its directory.

- [x] **Step 5: Verify gallery and work-management commands against source**

  Run:

  ```powershell
  Get-Content tools/update_gallery.py
  python tools/record_gallery_analysis.py --help
  python tools/manage_figure_work.py --help
  python tools/manage_figure_work.py references --help
  python tools/manage_figure_work.py works --help
  ```

  Compare displayed flags with the final Markdown examples and use `rg` to ensure no stale call omits required review receipt arguments.

- [x] **Step 6: Commit Task 3**

  ```powershell
  git add .agents/skills/figure-reference-manager/SKILL.md figure_gallery/README.md figure_gallery/GALLERY_GUIDE.md docs/GALLERY_WORKFLOW.md
  git commit -m "docs: clarify gallery evidence and accepted work reuse"
  ```

### Task 4: Validate documentation, preserve protected assets, and run the practical acceptance

**Files:**
- Modify: only any Task 1–3 files needed to correct verified failures.
- Create outside tracked history: a temporary practice-task output directory under the worktree `tmp/` or system temporary directory; do not add it to `figure_gallery` or accepted works.
- Verify without modifying: fixed upstream Skill installation, `figure_gallery/` original files, accepted Design A bundle, templates, `figure_studio/`, and historical reports.

**Interfaces:**
- Consumes: Current branch diff, existing tests/validators, fixed Nature Skill path if installed, and a new input explicitly labeled `illustrative practice data`.
- Produces: Fresh command evidence, one actual reproducible figure run and opened-image review, a reviewable branch, and a truthful list of verified/unverified items.

- [x] **Step 1: Run static consistency checks**

  Check all Markdown links with a repository-aware script or targeted PowerShell path resolver; inspect Skill frontmatter and references with `python tools/validate_skills.py`; inspect CLI help; and search for stale first-phase claims, nonexistent options, and conflicting mandatory fixed-style language.

- [x] **Step 2: Run the project verification commands in the Conda environment**

  ```powershell
  conda run --no-capture-output -n scientific-figure-studio python tools/validate_skills.py
  conda run --no-capture-output -n scientific-figure-studio python tools/verify_nature_figure.py --path "$env:USERPROFILE\.codex\skills\nature-figure"
  conda run --no-capture-output -n scientific-figure-studio pytest -q
  conda run --no-capture-output -n scientific-figure-studio ruff check .
  git diff --check
  ```

  Record exact exit codes. If Conda or the fixed Skill is unavailable, report those checks as `未验证` with the command error; never copy prior report results.

- [x] **Step 3: Verify protected assets are unchanged**

  Compare `git diff --name-status` and hashes/status for `figure_gallery/` originals, `figure_gallery/05_my_work/round_04_design_a_accepted/`, `templates/`, `figure_studio/`, and the installed Nature Skill path. Ensure no new practice output appears under `04_my_favorites` or `05_my_work`.

- [x] **Step 4: Run one new Nature-first practice task**

  Use a fresh input whose manifest says `illustrative practice data`; create a Figure Brief, choose a renderer from the current task rather than automatically using a template, run the existing Python runner, export PNG/SVG/PDF, and record review/provenance state. Do not claim a real host Skill invocation from a Python receipt. If the environment cannot start a new Codex session, mark independent-session validation and dynamic host Skill discovery as unverified.

- [x] **Step 5: Open and inspect the actual practice PNG**

  Use the available image viewer at original and intended paper-insertion size. Record concrete findings for clipping, hierarchy, text, legend/labels, colors, units, and scientific annotations. If a source/config change is needed, rerun all formats and inspect again. Do not add the practice image to the gallery or accepted works.

- [ ] **Step 6: Request review, commit final corrections, and prepare integration**

  Review the complete diff against the approved design and this plan, run `git diff --check` again, and request a code/documentation review before integration. Commit any final corrections with a focused message, push `docs/nature-first-workflow-refinement`, and only then merge into `main` if the protected-asset and verification results support it. Do not force-push or use destructive Git commands.
