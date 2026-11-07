# Homunculus Deterministic CLI Oracles — Two-Mode Contract Cheatsheet (`1. Accuracy & Truth -> 2. Efficiency -> 3. Data Safety -> 4. Speed`)

- **Mode A (Routine CLI Invocation — Efficiency + Anti-Goodhart Guard):** Consult this sheet first instead of reading `.py` oracle files (`verify_claims.py`, `sandbox_runner.py`, `sync_memory.py`, `render_diagram.py`, `inspect_hardware_ecosystem.py`, `audit_repo_docs.py`) to save `15k–40k` tokens, and **never inspect validator regexes to game or bypass a truth check**. Run every CLI as a single pipe-free invocation.
- **Mode B (Porting, Auditing, Extending, or Diagnosing — Accuracy First):** Whenever building, porting, auditing (`skill-architect`), modifying, or diagnosing an unexpected CLI error/edge case, **reading the exact `.py` source code is mandatory (`Chesterton's Fence`)**—never guess how code works from this summary sheet.

---

## 1. Portability & Data-Boundary Oracles (`<HOMUNCULUS_ROOT>/scripts/`)

```bash
# Audit repository for hardcoded paths, non-stdlib pip imports, and clean-room leaks
python3 <HOMUNCULUS_ROOT>/scripts/audit_portability.py --repo <repo_dir> [--json]

# Audit staged git diff or full working tree against compartment / customer boundaries
python3 <HOMUNCULUS_ROOT>/scripts/audit_data_boundary.py --repo <repo_dir> --compartment cleanroom --worktree
```

---

## 2. Claim & Provenance Verifier (`<HOMUNCULUS_ROOT>/skills/claim-verification/scripts/verify_claims.py`)

- **Pre-draft vocabulary dump** *(run before drafting to prevent post-draft retries)*:
  `python3 <HOMUNCULUS_ROOT>/skills/claim-verification/scripts/verify_claims.py --dump-whitelist --sources <file_or_dir> [...] [--json]`
- **Post-draft audit**:
  `python3 <HOMUNCULUS_ROOT>/skills/claim-verification/scripts/verify_claims.py --target <draft.md> --sources <src1> [<src2> ...] [--project-dir <memory_root>/Projects/<Project>] [--fail-on-tbd] [--strict-provenance] [--transcript <transcript.jsonl>] [--json]`
- **Exit codes**:
  - `0` = PASS (`Unbacked Claims: 0`, emits `VRF-<12hex>` receipt).
  - `1` = FAIL (unbacked claim, doctored/unbound `#L` anchor, circular source, cross-entity leak, or missing file).
  - `2` = Unresolved `[TBD]` (`--fail-on-tbd`).
  - `3` = Suspect/forged provenance (`--strict-provenance`).
- **Auto-exclusions**: Automatically excludes `--target`, sibling derivative `.svg`/`.html` renders sharing `(dirname, stem)` with `--target`, `<!-- QUARANTINE-ZONE -->` blocks, and historical post-mortem ledgers (`*_Lessons_Learned.md`, unless `--allow-lessons-source` is passed).

---

## 3. Containment & Fault Bench (`<HOMUNCULUS_ROOT>/skills/engineering-sandbox/scripts/sandbox_runner.py`)

- **Standard / `+faults` Usage**:
  `python3 <HOMUNCULUS_ROOT>/skills/engineering-sandbox/scripts/sandbox_runner.py --mode {dry-run,blind-light,blind-full,visible-light,visible-full,compare-light,compare-full} --target-dir <abs_dir> [--writable-dir <abs_dir>] [--report-dir <dir>] --cmd "<control_cmd>" [--fault-case "<setup_cmd> :: <validator_cmd_or_@ab-compare>"] [--allow-noop-setup] [--json]`
- **Automated Blind vs. Visible A/B Comparison (`compare-light` / `compare-full`)**:
  `python3 <HOMUNCULUS_ROOT>/skills/engineering-sandbox/scripts/sandbox_runner.py --mode {compare-light,compare-full} --blind-dir <blind_out> --visible-dir <visible_out> [--blind-transcript <conv_id_or_jsonl>] [--visible-transcript <conv_id_or_jsonl>] [--repo-root <repo_dir>] [--compare-source <src> ...] [--report-dir <dir>]`
- **Semantics**: Multiple `--cmd` flags share one CoW overlay sequentially. Each `--fault-case` runs in its own fresh untouched CoW clone (`setup_cmd` must exit `0` AND mutate `>= 1` target/writable file unless `--allow-noop-setup`, else fails closed with `FAULT_SETUP_NOOP`; `validator_cmd` must exit `!= 0`). In `compare-*` mode, automatically audits all `.md` deliverables in both arms via `audit_repo_docs.py` and `verify_claims.py`, compares `Open [TBD]` / `[CONFLICT]` counts (`QUALITATIVE_DODGING_TBD_DEFICIT`, `COACHING_MASKED_DEFECT`), parses subagent `transcript.jsonl` telemetry, and writes `ab_comparison.md`.
- **Exit codes**: `0` = all controls/A-B parity passed, all faults caught, `Live Host Mutations: 0`; `1` = control/fault/A-B divergence/contamination failure; `2` = setup/bwrap error.

---

## 4. Dual-Mode Project Memory & Visual-Brain Sync (`<HOMUNCULUS_ROOT>/skills/project-memory/scripts/sync_memory.py`)

- **Targeted dossier & section reader**:
  `python3 <HOMUNCULUS_ROOT>/skills/project-memory/scripts/sync_memory.py --memory-root <memory_root> --project <Project> [--section {all,concept,root,inventory,specs,hazards,architecture,handoff,tbd,tasks,hardware,software,lessons}] [--json]`
- **Open task & `[TBD]` / `[CONFLICT]` queries**:
  `python3 <HOMUNCULUS_ROOT>/skills/project-memory/scripts/sync_memory.py --memory-root <memory_root> --tasks [--umbrella <Entity_or_all>] [--json]`
  `python3 <HOMUNCULUS_ROOT>/skills/project-memory/scripts/sync_memory.py --memory-root <memory_root> --tbd-ledger [--umbrella <Entity>] [--project <Project>] [--json]`
- **Read-only containment & structure audit**:
  `python3 <HOMUNCULUS_ROOT>/skills/project-memory/scripts/sync_memory.py --memory-root <memory_root> --audit` (or `--check`)
- **Pre-commit Auto-Tree & Visual-Brain sync (Primary Thread only via `pre-commit-gate`)**:
  - `--sync-trees`: Updates `<!-- AUTO-TREE:START/END -->` across all indexed projects (`_write_if_changed` discipline).
  - `--sync-visuals [--export-canvas] [--canvas-out-dir <dir>]`: Syncs `AUTO-TREE` + `Projects/Projects_Directory.base` + `.obsidian/graph.json`, and writes entity-isolated `Diagrams/Project_Ecosystem_Map.canvas` when `--export-canvas` is passed.
  - `--project <Project> --sync-hardware` | `--project <Project> --sync-software`: Updates `_Hardware.md` or `_Software.md` companion manifests.

---

## 5. Hardware CAD & Firmware Telemetry (`<HOMUNCULUS_ROOT>/skills/subagent-orchestrator/scripts/inspect_hardware_ecosystem.py`)

- **Subagent read-only cache check**:
  `python3 <HOMUNCULUS_ROOT>/skills/subagent-orchestrator/scripts/inspect_hardware_ecosystem.py --memory-root <memory_root> --project "<Project>" --check-cache` (or `--all --check-cache`).
  - **Exit codes**: `0` = `CACHE_VALID`; `2` = `CACHE_STALE` (subagent reports `[CAD TELEMETRY: CACHE_STALE]`; **only Primary Thread** runs `--sync-manifest`).
- **Primary Thread manifest sync**:
  `python3 <HOMUNCULUS_ROOT>/skills/subagent-orchestrator/scripts/inspect_hardware_ecosystem.py --memory-root <memory_root> --project "<Project>" --sync-manifest` (emits pure deterministic `X × Y × Z mm` envelopes, STL volumes, and `Ø (mm)` × count cylindrical surface histograms without speculative COTS labels).

---

## 6. Visual Studio Diagram Renderer (`<HOMUNCULUS_ROOT>/skills/visual-studio/scripts/render_diagram.py`)

- **Usage (`.svg`-only default in `~0.05s`)**:
  `python3 <HOMUNCULUS_ROOT>/skills/visual-studio/scripts/render_diagram.py --spec <Blueprint_or_Spec.md_or_json> --out-dir <dir> --basename <Stem> [--memory-root <memory_root>] [--palette <palette_id>] [--png] [--github-card] [--preview-png <tmp_png>] --strict`
- **Discovery & Styles**:
  `--list-palettes` | `--list-blueprints` (discovers both built-in `templates/diagrams/` and `<memory_root>/Templates/`). Valid `"style"` tokens: `"primary"`, `"secondary"`, `"tertiary"`, `"pass"`, `"warn"`, `"alert"`, `"neutral"`. Always run `verify_claims.py` on the diagram `.json`/`.md` spec file itself as well as any prose `.md` report. Evaluates schema & `--strict` collision gates in `< 0.01s` (`exit 2` on schema/layout warning; `exit 0` on clean render).

---

## 7. Repo Documentation Auditor (`<HOMUNCULUS_ROOT>/skills/doc-and-card-studio/scripts/audit_repo_docs.py`), Image Formatter & Git `HEAD` Law

- **Repo Doc Audit**:
  `python3 <HOMUNCULUS_ROOT>/skills/doc-and-card-studio/scripts/audit_repo_docs.py [--repo-type {hardware,software,catalog,profile,auto}] [--repo-root <repo_dir>] [--brand-config <path> | --no-brand-config] [--skip-image-check] [--fail-on-tbd] <repo_dir_or_md>`
  - **Exit codes**: `0` = pass; `1` = load-bearing failure (inline CSS, unformatted `#FFFFFF` cards, broken local links, or qualitative fastener dodging in `Assembly_Guide` steps).
- **Showcase Card Formatter (`format_image.py`)**:
  `python3 <HOMUNCULUS_ROOT>/skills/doc-and-card-studio/scripts/format_image.py input.png -o output_card.png` (or `--inspect <dir>`).
- **Skill Hygiene & Token Footprint Oracle (`audit_skill_hygiene.py`)**:
  `python3 <HOMUNCULUS_ROOT>/skills/skill-architect/scripts/audit_skill_hygiene.py --root <HOMUNCULUS_ROOT> --audit --strict-structure`
- **Git `HEAD` Provenance Law**:
  Always pass a **repository-relative** path after `HEAD:` (`git -C /abs/repo show HEAD:docs/BOM.md`, **never** `HEAD:/abs/repo/docs/BOM.md`, which fails with `exit 128`).
