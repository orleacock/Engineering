# `Brief+` Subagent Authoring, `[CALC]` Dimensional Math & Promotion Playbook

> **Audience**: Delegated `teach-me` throw-away subagents (or dedicated standalone study windows).
> **Anti-Snooping Law (`co-engineering-partner.md` Two-Mode `.py` Rule)**: During routine `Brief+` authoring, **never** read, `grep`, `sed`, `cat`, `import`, or `python3 -c "open(...)"` `verify_claims.py` or `teach_brief.py` source code unless porting, auditing, or diagnosing a traceback. `teach_brief.py --verify` executes `verify_claims.py` deterministically for you—rely strictly on its CLI `[Hint]` diagnostics and the closed-world rules below.

---

## 1. Mode A — Fast-Path `Brief+` Execution (`Target: <= 5 Subagent Turns, 1 Shell Call`)

### Step 1: Parallel Turn-1 Read Batch (`Zero Serialized Reads, Zero Shell Probes`)
1. Issue **all** initial `read_file` calls (`brief_authoring_playbook.md` + the `1–2` authoritative `--sources` files from the Context Seed, `3` max) **in a single parallel batch**. If exact repo or standards source paths were not pre-supplied, read `<memory_root>/Directory/<Entity>_Directory.md` (or `<memory_root>/Directory/Directory_Index.md` + `<memory_root>/Projects/<Project>/<Project>.md` and `<Project>_Hardware.md` / `<Project>_Software.md` when relevant) directly on Turn 1 to resolve `local_path`, `entity`, `Standards_and_Specs/` files, and `AUTO-TREE` paths—never run `ls` or `find` across repos unless checking live disk before mutating files, never run `python3 -c "os.listdir(...)"` probes, never read files one-per-turn, and **never re-read** files already in context.
2. **Two-Mode `.py` CLI Rule & Zero Shell Reconnaissance**: During routine `Brief+` creation, do **not** read `teach_brief.py` or `verify_claims.py` source code via `read_file` or shell `sed`/`cat`/`python3 -c` unless porting, auditing, or diagnosing a traceback—use the complete Step 3 CLI flags directly. Do **not** run `teach_brief.py --help`, `mkdir -p`, shell `grep`, or `git status`/`git log`/`git rev-parse` probes (`verify_claims.py` validates strictly against `--sources` files on disk).
   - *Only exception*: For raw `.step`/`.stl` CAD geometry when `<Project>_Hardware.md` lacks the feature, run `python3 <HOMUNCULUS_ROOT>/skills/subagent-orchestrator/scripts/inspect_hardware_ecosystem.py --repo <path_to_repo>` (`--repo`, never `--target`).
3. **Strict Read-Only Guarantee**: Never edit repository files or `<memory_root>/` files during `/teach-me`.

### Step 2: Direct `write_file` Using the Canonical `Brief+` Skeleton (`Zero `--init-brief` Round-Trip`)
Write `<study_briefs_root>/<Project_or_General>/YYYY-MM-DD_<Draft_Slug>.md` directly via `write_file` (`write_file` creates parent directories automatically—never run `mkdir -p` via shell) using the exact frontmatter and 4-section structure below (`teach_brief.py --verify --auto-slug` in Step 3 automatically creates `study_briefs/README.md` and snaps the filename to clean whole-word `YYYY-MM-DD_<Subject>_on_<Impact>.md`):

````markdown
---
title: "<Subject X> — Impact on <Subject Y>"
subject: "<Subject X>"
impact_on: "<Subject Y>"
domain: "<mechanical|electrical|firmware|cabling|software|hybrid>"
project: "<ProjectName_or_General>"
entity: "<EntityName>"
type: "study-brief"
status: "UNPROMOTED_STUDY_BRIEF"
consumed_by_memory: false
vrf_receipt: "UNVERIFIED"
created_at: "YYYY-MM-DD"
---

# 🧠 Engineering Brief+: <Concise Subject X> → <Concise Subject Y>

> [!NOTE]
> **Non-Consumed Study Brief (status: UNPROMOTED_STUDY_BRIEF)**
> Stored in study_briefs/ adjacent to memory/. This brief is quarantined from automatic memory indexing and truth-oracle source whitelists until explicitly promoted.
> - **Domain**: <domain> | **Project Context**: <project> (entity: <entity>)
> - **Verification Receipt**: UNVERIFIED | **Source Hashes**: PENDING

---

<!-- FIRST-PRINCIPLES-THEORY:START -->
## 1. Core Mental Model
- **First-Principles Mechanism**: 3–5 concise bullets explaining the physical, electrical, mechanical, firmware, or algorithmic mechanism (place generic CLI syntax, protocol framing, and symbolic LaTeX equations like $\Delta P \propto D_i^{-4}$ here).
- **Governing Scaling / Physics Law**: Use `[CALC: <lhs> = <rhs_val> <unit>]` ONLY for genuine numerical arithmetic (`mm`, `mm2`, `mm3`, `V`, `A`, `W`, `ohm`, `N`, `m`, `Nm`, `L/min`, `min`, `L`, `m/s`, `s`; e.g., `[CALC: 24 V / 120 ohm = 0.2 A]`). Never invent dummy `* 1` equations.
- **Key Boundary Condition**: Threshold or state boundary where nominal behavior breaks down.

## 2. Relational Impact Vector
- **Causal Coupling Chain**: **<Subject X>** $\rightarrow$ *(Coupling Mechanism)* $\rightarrow$ **<Subject Y>**.
- **Trade-Off & Failure Envelope**:

| Parameter Shift | Primary Effect on <Subject Y> | Secondary Bottleneck | Failure Mode Past Limit |
| :--- | :--- | :--- | :--- |
| **Increase $\uparrow$** | Direct impact | Trade-off | Physical/system failure |
| **Decrease $\downarrow$** | Direct impact | Trade-off | Physical/system failure |
<!-- FIRST-PRINCIPLES-THEORY:END -->

---

## 3. Active Engineering Context Overlaps

### Overlap Example 1: Direct Touchpoint in <Project>
- [VERIFIED FACT] Concrete touchpoint using ONLY exact literals/quantities present in --sources (Source: `/abs/path/to/source#L10-L12`).
  Anchor:
  ```text
  Exact 1-3 line verbatim slice copied from /abs/path/to/source#L10-L12
  ```
- **Engineering Impact in Context**: How <Subject X> affects this verified component, script, or parameter.

---

## 4. Actionable Engineering Guardrails
1. **<Check 1>**: Concrete operational check (without backticking generic CLI commands/SHAs absent from --sources).
2. **<Check 2>**: Validation probe or safety boundary (never prescribe anaerobic threadlocker or metal torque on `ABS/ASA/PC` without explicit negation).
````

### Closed-World First-Pass Verification Rules (`Sections 3 & 4` — Prevent Retry Loops & Hallucinations)
1. **Keep Generic CLI Syntax & Textbook Figures in Sections 1–2**: Outside `FIRST-PRINCIPLES-THEORY`, `verify_claims.py` audits **every** backticked token (`[LITERAL_ID]`), hardware count (`[COUNTED_ENTITY]`), and number+unit (`[QUANTITY_UNIT]`) against `--sources`. Keep generic commands/flags (`git revert <sha>`, `--no-verify`), symbolic physics formulas, and textbook datasheet curves inside Sections 1–2; in Sections 3–4, **only** backtick exact strings that exist verbatim in `--sources` (never backtick instructional prose words like `--sources` or `verify_claims.py`, and write `"Steps 10–11 specify BHCS hardware"` rather than `"12 BHCS fasteners"` when referencing step numbers).
2. **Explicit `[TBD]` Abstention, Prompt-Target Metrics, Zero Material Borrowing & `[TBD: CONFLICT]`**: Whenever `subject` or `impact_on` names an unrecorded physical parameter (Shore hardness, stepper current/holding torque, belt linear density, Newton shaft load) or slicer setting, emit an explicit **`[TBD: <specific_missing_variable>]`** inline in Sections 3–4—never invent pretraining values, never borrow `ABS`/`ASA` slicer settings (`40%` infill, `4` walls) onto `TPU`/elastomer parts, and never silently dodge missing prompt metrics in qualitative prose. When primary sources disagree (e.g., BOM fastener count or `SHCS` vs. Assembly Step `BHCS`), emit **`[TBD: CONFLICT — <val_A> vs <val_B>]`** inline.
3. **Preserve Hazard Polarity & Never Cite Quarantined Dossier Zones**: When citing within 5 lines of a source `[!WARNING]`, `[!CAUTION]`, or `'do not'`/`'never'` block, include an explicit hazard/negation word (`warning`, `caution`, `hazard`, `never`, `do not`, `avoid`, `damage`, `strip`, `crack`) in the claiming bullet (`WARNING_CONTEXT_CITATION`). In `<Project>.md` files, cite verified architecture/parameter sections or `<Project>_Hardware.md` / `<Project>_Software.md`—**never** cite lines inside `<!-- SESSION-HANDOFF:START/END -->`, `<!-- QUARANTINE-ZONE:START/END -->`, or `Open [TBD]` ledgers (`QUARANTINED_ZONE_CITATION`).

### Step 3: Single-Call Verification + In-Place Smart Whole-Word Naming (`teach_brief.py --verify --auto-slug`)
Run **one** CLI command to create `study_briefs/README.md`, rename the file **in-place inside its existing parent directory** (`<dir>/YYYY-MM-DD_<Subject>_on_<Impact>.md`, preserving custom output subdirectories even when `--briefs-root` points higher), verify all claims via `verify_claims.py`, and stamp `VRF-<12hex>` (when verifying multiple briefs in a batch run, chain `--verify --auto-slug` calls with `&&` in a single shell turn):
```bash
python3 <HOMUNCULUS_ROOT>/skills/teach-me/scripts/teach_brief.py \
  --verify <path_to_written_brief.md> \
  --auto-slug \
  [--briefs-root <study_briefs_dir>] \
  [--memory-root <memory_dir>] \
  [--entity "<EntityName>"] \
  [--slug "<Concise_Custom_Slug>"] \
  --sources <1_to_3_authoritative_source_files...>
```
- If `--verify` reports a line error, patch **only** the offending lines via `edit_file` (never rewrite the entire file via `write_file`) and re-run `--verify`.

### Step 4: Return ONLY the Solid-Line Datasheet Card (`Zero Post-Verify Re-Reads`)
Once `--verify` prints `[PASS]` and `TEACH-ME CHAT CARD TEMPLATE`, fill the `▸` / `↳` fields immediately from your context (**do not** re-read the verified brief file), **never** wrap the card in a ```` ```markdown ```` code fence, and send/return **nothing before or after the card**:

````markdown
`┏━━ 🎓 TEACH-ME // BRIEF+ ━━━━━━━ [DOMAIN: HYBRID] ━━ [ISOLATED SUBAGENT] ━━┓`

▸ **CONCEPT & IMPACT**: <1–2 concise sentences explaining Subject X and its impact on Subject Y>
▸ **CONTEXT OVERLAPS**:
  ↳ [<file>:<lines>](file:///abs/path/to/file#Lstart-Lend) — <1-line verified project touchpoint>
  ↳ [<file>:<lines>](file:///abs/path/to/file#Lstart-Lend) — <1-line verified project touchpoint>
▸ **GUARDRAIL**: <1-line critical failure boundary or operational check>
▸ **STUDY BRIEF+**: [<Project>/<clean_filename.md>](file:///abs/path/to/brief.md)

`┗━━ 🔒 QUARANTINED: study_briefs/ (NON-CONSUMED) ━━━━━━━ [VRF-b3385dc0ccec] ━━┛`
````

---

## 2. Mode B — Standalone Scaffold, List, Clean-Rename, or Promote (`Explicit Request Only`)

```bash
# Optional standalone CLI scaffold:
python3 <HOMUNCULUS_ROOT>/skills/teach-me/scripts/teach_brief.py \
  --init-brief --subject "<Subject X>" --impact-on "<Subject Y>" --domain <domain> --project "<Project>" --entity "<Entity>"

# List unpromoted/promoted briefs or clean-rename a legacy file:
python3 <HOMUNCULUS_ROOT>/skills/teach-me/scripts/teach_brief.py --list
python3 <HOMUNCULUS_ROOT>/skills/teach-me/scripts/teach_brief.py --rename-clean <path_to_brief.md>

# Promote into <memory_root>/ (enforces --fail-on-tbd + 0 unbacked claims):
python3 <HOMUNCULUS_ROOT>/skills/teach-me/scripts/teach_brief.py \
  --promote <path_to_brief.md> --project "<ProjectName>" --target <standards|project-doc|lessons-learned> --sources <sources...>
```
