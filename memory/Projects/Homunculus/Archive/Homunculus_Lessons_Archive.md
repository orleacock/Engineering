---
project: "Homunculus"
parent_note: "Homunculus_Lessons_Learned"
entity: "Alchemical-3D"
compartment: "cleanroom"
note_type: "lessons_archive"
authoritative: false
last_synced: "2026-11-18"
---

# 🗄️ Homunculus — Graduated & Historical Lessons Archive (`TIER3`–`TIER5`)

> **Single-Source Tiered Archive**: Companion to [`Homunculus_Lessons_Learned.md`](../Homunculus_Lessons_Learned.md). Stores full-context narratives for stabilized `TIER3`, isolated-polish `TIER4`, and retired `TIER5` lessons so the active `<Project>_Lessons_Learned.md` window stays compact (`<= 3 TIER0 + <= 7 TIER2` sections). Query any entry on demand via `sync_memory.py --project Homunculus --lesson-id <LL-xxx>` or promote back to active memory via `--set-tier <LL-xxx> TIER2`.

---

## 1. Archived Full-Context Post-Mortems (`TIER3`–`TIER5`)

### `LL-001` [TIER3] — Always-On Core Rule vs. On-Demand Skill Placement for Anti-Bloat Gates
- **Symptom / Trap:** Placing rules against mid-project diagram re-rendering, mid-session memory index rebuilds (`--sync-visuals`), or unapproved `git push` commands exclusively inside `pre-commit-gate/SKILL.md` fails during mid-project turns because the agent does not read `pre-commit-gate` until it already believes the task is ready to commit.
- **Root Cause:** Lazy-loaded `SKILL.md` files only enter context upon activation. Behavioral restraints that govern *when not to act* during routine turns must live in an `always_on` rule.
- **Hardened Solution:** Encode **Anti-Bloat, Deferred Side-Effects & User-Readiness Gates** directly inside `rules/co-engineering-partner.md` (Pillar 3) so every turn enforces: (1) batching derived visual/index updates until task wrap-up, (2) requiring explicit user confirmation in the current turn before any `git push` or external state mutation, and (3) strict turn-budget restraint (logging side discoveries as `[ISOLATED]` instead of launching unrequested side quests).
- **Active Operational Binding:** `rules/co-engineering-partner.md` (Pillar 3) & `skills/pre-commit-gate/SKILL.md`.

### `LL-002` [TIER3] — Retiring Per-Edit `PostToolUse` Hooks in Favor of Deferred `pre-commit-gate` Batching
- **Symptom / Trap:** Running automatic `PostToolUse` hooks after every `write_file`/`edit_file` call causes redundant file-tree scans, visual re-renders, and lock contention during multi-file edits.
- **Root Cause:** Intermediate edits within a turn or multi-turn feature are transitional states; synchronizing derived artifacts on transitional states wastes compute and turns.
- **Hardened Solution:** Keep `hooks.json` at `{}` (`0` per-edit `PostToolUse` hooks) and execute the deterministic **`X -> Y -> Z`** sequence (`Gate X` memory/tree sync $\rightarrow$ `Gate Y` on-demand `.svg` diagram refresh $\rightarrow$ `Gate Z` `VRF` claim & sandbox verification) once right before `git commit`, backed by a fast (`~0.07s`) read-only `.git/hooks/pre-commit` check.
- **Active Operational Binding:** `hooks/hooks.json` & `skills/pre-commit-gate/SKILL.md`.

### `LL-003` [TIER3] — Unifying Meta-Skills (`skill-architect`) Instead of Splitting Builder vs. Cleanup Auditor
- **Symptom / Trap:** Creating one skill for "building new skills" and a second skill for "auditing/cleaning up redundant skills" duplicates the skill-inspection logic, doubles maintenance, and creates overlapping YAML trigger descriptions.
- **Root Cause:** Both workflows evaluate the exact same invariants: existing `rules/` and `skills/` coverage, Dual-Mode Memory integration (`AUTO-TREE` + single-writer task umbrellas), Truth Oracle hooks (`verify_claims.py`), deferred side-effects (`pre-commit-gate`), and token/turn efficiency.
- **Hardened Solution:** Combine both into a single two-mode skill **`skills/skill-architect/SKILL.md`** backed by deterministic **`skills/skill-architect/scripts/audit_skill_hygiene.py`**:
  - **Mode 1 (`Create / Extend` — Synergistic Skill Builder):** Runs a pre-creation overlap check first (preferring adding a mode/reference to an existing skill over spawning a redundant skill), wires Memory/Oracles/`pre-commit-gate` automatically, and enforces delta-only instructions (zero repetition of always-on rules).
  - **Mode 2 (`Audit / Consolidate` — Permission-Based Cleanup Protocol):** Audits existing skills/rules/scripts for redundancy and turn waste, outputting non-destructive, opt-in recommendations.
- **Active Operational Binding:** `skills/skill-architect/SKILL.md` & `skills/skill-architect/scripts/audit_skill_hygiene.py`.

### `LL-004` [TIER3] — Permission-First Cleanup vs. Authoritarian Auto-Deletion (`Chesterton's Fence`)
- **Symptom / Trap:** Aggressive cleanup prompts or scripts that automatically strip instructions or merge skills without full domain context break specialized edge-case guards that looked "redundant" on the surface.
- **Root Cause:** Static analysis can detect structural overlap (duplicate headings, repeated rule phrases, banned `ls`/`find` patterns, or overlapping triggers), but only the user knows whether a domain-specific constraint protects against an external hardware, enterprise, or client quirk.
- **Hardened Solution:** Enforce a strict **Advisory & Permission-First Contract** in `skill-architect` Mode 2 and `audit_skill_hygiene.py`:
  - Classify every finding into explicit buckets: `[KEEP — DOMAIN SPECIFIC]`, `[SUGGESTED TRIM — ALREADY IN CORE RULES]`, `[CANDIDATE MERGE — OVERLAPS SKILL X]`, or `[TURN-WASTE HAZARD]`.
  - Present the concrete evidence (exact line ranges, token savings, and why it flagged) and require explicit user approval before modifying or deleting any user skill or function.
- **Active Operational Binding:** `rules/co-engineering-partner.md` (Pillar 5) & `skills/skill-architect/SKILL.md`.

### `LL-005` [TIER3] — Two-Mode CLI Oracle Rule (`Navigation Map / SKILL.md for Routine Runs` vs. `Mandatory .py Source Read for Porting / Diagnosis`)
- **Symptom / Trap:** An early efficiency rule stated *"Never read `.step`, `.stl`, `.canvas`, or `.py` oracle internals."* While intended to save `15k–40k` tokens during routine CLI flag lookups and prevent Goodharting (gaming regexes), making it a **blanket ban on reading `.py` files** inverted **`1. Accuracy & Truth > 2. Efficiency > 3. Data Safety > 4. Speed`**:
  1. **Porting & Refactor Amnesia:** When porting or adapting scripts in `Homunculus`, an agent forbidden from reading `.py` internals would have to guess schemas and edge-case logic from summary docs—hallucinating implementations and dropping hardened guards.
  2. **Diagnostic Guessing (`Chesterton's Fence` Violation):** When a CLI oracle flags an unexpected edge case, banning `.py` source inspection forces blind trial-and-error guessing instead of root-cause diagnosis.
  3. **Category Error (`.step`/`.stl` vs. `.py`):** Raw `.step`/`.stl` files must not be eyeballed in context because LLMs hallucinate 3D B-Rep trigonometry (requiring `inspect_hardware_ecosystem.py` for *accuracy*). By contrast, `.py` files *are* primary source truth.
- **Root Cause:** Over-generalizing a token-efficiency shortcut into an absolute prohibition that elevated secondary summaries above primary source code on disk.
- **Hardened Solution (`Accuracy & Truth > Efficiency > Speed`):**
  1. **Raw 3D CAD Meshes (`.step`, `.stl`):** Never eyeball raw 3D coordinate/spline text to guess geometry—always run `inspect_hardware_ecosystem.py`.
  2. **Python CLI Oracles (`.py`) — Two-Mode Contract:**
     - **Mode A (Routine Invocation — Efficiency + Anti-Goodhart Guard):** When simply *running* a CLI oracle during normal documentation/repo tasks, derive CLI flags from `<skill_dir>/SKILL.md` and **never inspect validator regexes to game or bypass a truth check**.
     - **Mode B (Porting, Auditing, Extending, or Diagnosing — Accuracy First):** Whenever building, porting, auditing (`skill-architect`), modifying, or diagnosing an unexpected error/edge case in a script, **run `homunculus_paths.py --map <script.py>` (`#L1-L55` Navigation Map) and read the exact `30–80` line `.py` source window (`Chesterton's Fence`)**—never guess how code works from a summary.
- **Active Operational Binding:** `rules/co-engineering-partner.md` (Pillar 5) & `skills/subagent-orchestrator/SKILL.md`.

### `LL-006` [TIER3] — Quarantining Open `[TBD]` Ledgers & YAML Frontmatter Line Citations in `verify_claims.py`
- **Symptom / Trap:** Two verification traps surfaced during multi-repo audits: (1) numbers inside a dossier's `## 🔍 Provenance Status & Open [TBD] / [CONFLICT] Ledger` got ingested into the verified whitelist pool if not quarantined, and (2) citing `#L1-L14` YAML frontmatter line numbers caused brittle failures when frontmatter fields updated.
- **Root Cause:** Unscoped source ingestion and frontmatter line-shift sensitivity.
- **Hardened Solution:** `verify_claims.py` quarantines `Open [TBD] / [CONFLICT] Ledger` sections from the truth pool and blocks `#L1-L14` frontmatter citations (`FRONTMATTER_CITATION_BLOCKED`), requiring body-section citations (`#L15+`) and keeping unverified figures strictly inside `[TBD: ...]` brackets.
- **Active Operational Binding:** `skills/claim-verification/scripts/verify_claims.py`.

### `LL-007` [TIER3] — Multi-Encoding (`UTF-8/16/32`) & NUL-Delimited (`-z`) Boundary Scanning
- **Symptom / Trap:** Naive UTF-8 line scanners and standard `git status` outputs can be bypassed by UTF-16LE/BE or UTF-32 encoded text blobs, C-quoted filenames containing special characters, or symlink escapes outside the repo root.
- **Root Cause:** Assuming all text files are UTF-8 and all paths are unquoted ASCII.
- **Hardened Solution:** Both `audit_portability.py` (`SBX-20261101_163034-9a368319`) and `audit_data_boundary.py` decode `UTF-8`, `UTF-16` (`LE`/`BE` BOM + null-byte heuristic), and `UTF-32`, use `git status --porcelain -z` / `git diff --cached --name-only -z`, inspect ASCII `.step`/`.stl`/`.svg`/`.xlsx`/`.ipynb` metadata, and reject symlink escapes (`exit != 0`).
- **Active Operational Binding:** `scripts/audit_portability.py` & `scripts/audit_data_boundary.py`.

### `LL-008` [TIER3] — Cross-OS (`1. Linux -> 2. macOS -> 3. Windows`) & Corporate Locked-Down Station Constraints
- **Symptom / Trap:** Frameworks that depend on POSIX symlinks (`ln -s`), `bwrap`/`btrfs`, bash-only installers, or external `pip` packages fail immediately on locked-down corporate Windows laptops (`Developer Mode` disabled, AppLocker/WDAC active, proxy-blocked `pip`).
- **Root Cause:** Designing only for root-enabled Linux developer machines.
- **Hardened Solution:** Maintain a **Single Unified Archive** using pure Python 3.10+ standard library and `pathlib` (`scripts/homunculus_paths.py`), shipping **Track 1 Automated Installers** (`install.sh` / `install.ps1` with file-copy fallback when Windows symlinks are blocked) alongside **Track 2 Zero-Install "Drop-In & Point" Mode** (`HOMUNCULUS_START_HERE.md`) and cross-OS sandbox fallbacks (`bwrap`+`btrfs` $\rightarrow$ APFS/worktree $\rightarrow$ Windows `git worktree`/temp-copy).
- **Active Operational Binding:** `scripts/homunculus_paths.py`, `scripts/build_adapters.py`, & `skills/engineering-sandbox/scripts/sandbox_runner.py`.

### `LL-009` [TIER5] — Two-Touch Skill Hygiene Cadence (Up-Front Guardrails $\rightarrow$ Post-Build Release Audit)
- **Retirement Provenance (`TIER5` — `2026-11-09`):** Demoted from active governance because this entry tracked a one-time `Phase 2A -> Phase 4` initial build schedule and referenced the retired `"Discord Store packaging"` distribution model (replaced by `Apache-2.0` open-source release). Continuous skill hygiene is permanently enforced via `skills/skill-architect/SKILL.md`, `audit_skill_hygiene.py`, and `skills/pre-commit-gate/SKILL.md` (see [`Homunculus_Lessons_Learned.md`](../Homunculus_Lessons_Learned.md) `SUBSYSTEM-INVARIANTS`).
- **Symptom / Trap:** If skill hygiene is only checked at the very end of a project, every skill written during Phase 3 accumulates duplicate boilerplate that must be rewritten; if it is only checked up front, subtle cross-skill overlaps introduced while building 6–8 modules go unnoticed before release.
- **Root Cause:** Single-point quality checks miss either design-time drift or integration-time overlap.
- **Hardened Solution:** Execute a **Two-Touch Hygiene Cadence**:
  1. **Up-Front (Parent System + Phase 2A/3 Design):** Lock the Synergy & Hygiene Contract into `co-engineering-partner.md` and build `skill-architect` (`+ audit_skill_hygiene.py`) on the parent system first to audit existing workstation skills and calibrate thresholds.
  2. **Pre-Release Gate (End of Phase 3 $\rightarrow$ Phase 4):** Run `skill-architect` Mode 2 (`audit_skill_hygiene.py`) across all newly ported `Homunculus` `v1.0` rules, skills, and adapters to trim any redundancy before cold-start sandbox testing and Discord Store packaging.
- **Homunculus Target:** Parent workstation (`Immediate Priority`) $\rightarrow$ `Homunculus` `Phase 2A`, `Phase 3`, and `Phase 3 -> 4` Release Gate.

### `LL-010` [TIER3] — `AUTO-TREE` Is a Turn-1 Routing Map, Never a Substitute for Live Filesystem Truth
- **Symptom / Trap:** Because `sync_memory.py --sync-visuals` is deferred until `pre-commit-gate` (`LL-001` / `LL-002`), a project dossier's `<!-- AUTO-TREE:START/END -->` block can become temporarily stale mid-session after files are added, renamed, or deleted. An unconditional ban on directory checks (`"never run ls or find"`) could cause an agent to trust a stale `AUTO-TREE` snapshot over live disk reality.
- **Root Cause:** Allowing an efficiency optimization (skipping blind Turn-1 `ls`/`find` wandering across `<memory_root>/Projects/`) to masquerade as a source-of-truth guarantee during active file mutations.
- **Hardened Solution (`Accuracy & Truth > Efficiency > Speed`):** Use `Projects/<Project>/<Project>.md` (`AUTO-TREE`) and `Directory/<Entity>_Directory.md` on Turn 1 to eliminate blind directory wandering, **but** whenever verifying live repo state, auditing untracked/modified files, or encountering a missing path, check live disk truth (`git -C <repo> status --short` or targeted directory inspection). Never treat a cached Markdown tree as authoritative over the filesystem.
- **Active Operational Binding:** `rules/co-engineering-partner.md` (Pillar 5) & `skills/project-memory/SKILL.md`.

### `LL-011` [TIER3] — `Anchored Evidence Packets` (`1–3` Line Hunks): Safe for Citations, Insufficient Alone for Blind Code/Doc Mutations
- **Symptom / Trap:** Returning `1–3` line verbatim hunks from subagents eliminates the double-read tax when synthesizing status reports or verifying isolated literals. However, `1–3` lines can omit surrounding control flow (`if/else` guards, deprecation notices 10 lines up, or table column headers), and calling `edit_file` using only a 3-line subagent snippet without reading the surrounding block risks breaking structure or duplicating adjacent content.
- **Root Cause:** Over-extending a read-only synthesis optimization (`0` double-reads for verified quotes) into file mutation workflows.
- **Hardened Solution (`Accuracy & Truth > Efficiency > Speed`):**
  - **For Read-Only Citations & Audits:** Trust `1–3` line Anchored Evidence Packets (backed by `verify_claims.py` `±5`-line warning-context checks) without re-reading the file.
  - **For File Mutations (`edit_file`) or Conditional Context:** Before modifying any file in the Primary Thread—or whenever a 3-line hunk's meaning depends on surrounding headers, schemas, or control flow—read the surrounding `30–80` line window (`StartLine`–`EndLine`) first so edits never land blind.
- **Active Operational Binding:** `rules/co-engineering-partner.md` (Pillar 5) & `skills/subagent-orchestrator/SKILL.md`.

### `LL-012` [TIER5] — Calibrating `audit_skill_hygiene.py` Against False Positives & Structural Blind Spots (Audit Pass 1 $\rightarrow$ Pass 2)
- **Retirement Provenance (`TIER5` — `2026-11-09`):** Demoted because this entry recorded the initial `Pass 1 -> Pass 2` prototype calibration of `audit_skill_hygiene.py` against retired legacy skills (`alchemical-github-content`, `bom-fastener-verifier`). All 5 resulting parser invariants (leading-slash lookbehind, backtick/fence link masking, 3-gram sub-bullet grouping, `references/*.md` scanning, and stemmed `--check-new` scoring) are permanently locked in [`Homunculus_Lessons_Learned.md`](../Homunculus_Lessons_Learned.md) (`SUBSYSTEM-INVARIANTS`) and `scripts/script_contracts.json`.
- **Symptom / Trap:** Running the initial v1 build of `audit_skill_hygiene.py` against ``<legacy_builder_workspace>`` exposed 5 calibration flaws in the auditor itself before any target skills were touched:
  1. **Leading-Slash Regex Truncation:** Using `\b` before a script path regex stripped the leading `/` from `/home/orin/.../scripts/*.py` (because `/` is non-word), causing `8` false `BROKEN_SKILL_LINK_OR_SCRIPT` errors.
  2. **Inert Syntax Examples Flagged as Broken Links:** Scanning `[label](target)` inside inline code backticks (e.g., `` `![Alt](path.png)` `` in `alchemical-github-content/SKILL.md#L82`) flagged documentation syntax examples as missing files.
  3. **Sub-Bullet Fragmentation Hiding Paraphrased Overlaps:** Splitting indented sub-bullets (`    - ...`) into tiny separate blocks prevented `author-voice-cadence` (`Mode B1` nested bullets) from matching `alchemical-github-content` (`Mode B1` single-paragraph equivalent).
  4. **Unscanned `references/*.md` Files:** Scanning only `SKILL.md` missed a real `LL-005` blanket `.py` ban hiding inside `engineering-sandbox/references/frame_playbooks.md#L43`.
  5. **Unstemmed Compound Queries in `--check-new`:** Failing to split hyphenated compound words (`heat-sets`, `bom-fastener-verifier`) or stem plurals (`claims`/`claim`, `verifier`/`verify`) under-scored existing skill coverage (`34.6%` vs. true `61.4%` / `100%` body coverage).
- **Hardened Solution:** Upgraded `audit_skill_hygiene.py` to (1) use lookbehind `(?<![A-Za-z0-9_./-])` preserving leading `/`, (2) mask inline backticks and fenced code blocks during link checks, (3) group nested sub-bullets (`4+` spaces) with their parent top-level bullet and compare `3-gram` shingles + vocabulary Jaccard, (4) scan all `references/*.md` files alongside `SKILL.md` and `root/scripts/*.py`, and (5) apply compound splitting + stem normalization in `--check-new`.
- **Homunculus Target:** Carry the calibrated `audit_skill_hygiene.py` directly into `Homunculus/scripts/audit_skill_hygiene.py` (`Phase 3`).

### `LL-013` [TIER5] — Factoring `always_on` Global Rules into Overlap Scoring & Reverse Directionality (`100%` Turn Tax)
- **Retirement Provenance (`TIER5` — `2026-11-09`):** Demoted because it references the deleted `AI_Skill_Project` nested `rules/<name>/<name>.md` layout and pre-build `"empty/Phase-1 Homunculus"` state. Bidirectional `always_on` Rule $\leftrightarrow$ Skill overlap scoring (`ALREADY_IN_CORE_RULE`, `RULE_DELEGATES_TO_SKILL`) is permanently locked in `audit_skill_hygiene.py`, [`Homunculus_Lessons_Learned.md`](../Homunculus_Lessons_Learned.md) (`SUBSYSTEM-INVARIANTS`), and `scripts/script_contracts.json`.
- **Symptom / Trap:** The initial version of `audit_skill_hygiene.py` had four blind spots regarding `rules/`:
  1. **Mode 1 (`--check-new`) Ignored `rules/`:** It only scored proposed capabilities against `skills/`, so a user proposing a skill already 80–100% covered by `data-and-credential-safety.md` or `co-engineering-partner.md` would be told to create a new skill.
  2. **Missing `always_on` Turn-Tax Footprint & Rule-to-Rule Checks:** `always_on` rules load on 100% of turns (`~5,300` tok/turn across the 3 rules), making Rule-to-Rule duplication and rule bloat far more expensive than on-demand skill text.
  3. **Reverse Directionality (`SKILL_REPEATS_CORE_RULE` vs. `RULE_DELEGATES_TO_SKILL`):** When an `always_on` rule explicitly delegates to an on-demand skill (e.g., `co-engineering-partner.md` referencing `subagent-orchestrator`), naive overlap flagging tells the user to trim the *skill* (`subagent-orchestrator/SKILL.md#L98`), when in fact the on-demand skill is the canonical runbook and the `always_on` rule should only carry the Turn-1 trigger + load-bearing safety overrides!
  4. **Flat (`rules/*.md`) vs. Nested (`rules/*/*.md`) Layouts:** `AI_Skill_Project` uses `rules/<name>/<name>.md` whereas `Homunculus` uses `rules/<name>.md`, and empty/Phase-1 roots (`Homunculus`) reference top-level `scripts/*.py` in `README.md` / `HOMUNCULUS_START_HERE.md` / `tests/*.py`.
- **Hardened Solution:** Upgraded `audit_skill_hygiene.py` to (1) score `--check-new` against both `rules/` (`ALREADY_IN_CORE_RULE`) and multi-module composites (`COMPOSITE_ALREADY_COVERED`), (2) report Table 0 (`Always-On Global Rules Footprint` + `Rule-to-Rule Overlap`), (3) classify bidirectional Rule $\leftrightarrow$ Skill overlap (`[KEEP IN SKILL / CHECK ALWAYS-ON RULE FOOTPRINT]` when the rule delegates to the skill), and (4) support both flat and nested rule directories; verified across `7` multi-vector probes and `OS Dry-Run (+5 faults)` (`SBX-20261103_180610-5cda55ee`, `2.65s`, `1/1` controls, `5/5` faults caught).
- **Homunculus Target:** `Homunculus/skills/skill-architect/` & `Homunculus/scripts/audit_skill_hygiene.py` (`Phase 3`).
