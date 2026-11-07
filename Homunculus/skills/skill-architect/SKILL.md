---
name: skill-architect
description: >-
  Use this skill whenever creating or extending a skill, rule, side-loaded
  add-on, or helper script (Mode 1: Synergistic Skill Builder), or when
  auditing existing skills, rules, add-ons, and scripts for unnecessary
  redundancy, overlapping triggers, bloated token footprints, turn-wasting
  patterns, or Homunculus compliance violations (Mode 2: Permission-Based
  Cleanup Protocol). Enforces 1. Accuracy & Truth -> 2. Efficiency -> 3.
  Data Safety -> 4. Speed, Chesterton's Fence, backbone synergy
  (Dual-Mode Memory, Truth Oracles, Subagent Swarms, and pre-commit-gate), and
  non-destructive, opt-in consolidation proposals via audit_skill_hygiene.py.
---

# Synergistic Skill Builder & Permission-Based Cleanup Protocol (`skill-architect`)

This skill governs the full lifecycle of skills (`skills/*/SKILL.md`), side-loaded add-ons (`addons/*/SKILL.md`), global rules (`rules/*.md`), and helper scripts (`scripts/*.py`) inside **Homunculus**. It combines **Mode 1: Synergistic Skill Builder (`Create / Extend`)** and **Mode 2: Permission-Based Cleanup Protocol (`Audit / Consolidate`)** into a single workflow backed by [`scripts/audit_skill_hygiene.py`](scripts/audit_skill_hygiene.py) so meta-skill logic is never duplicated.

**Supreme Governing Priority Hierarchy (`1. Accuracy & Truth -> 2. Efficiency -> 3. Data Safety -> 4. Speed`)**:
Never strip a domain-specific verification gate, safety check, or cold-start accuracy anchor merely to shave line counts, and never permit a new skill or script to introduce non-stdlib `pip` dependencies or hardcoded OS user paths. Efficiency is achieved by replacing duplicated generic boilerplate with clean pointers and deferring mid-session churn—never by weakening truth or portability gates.

---

## 1. Pre-Flight Foundation Checks (Mandatory Before Building or Auditing)

Before creating a new skill, packaging a side-loaded add-on, or auditing existing skills:

1. **Select the Active Mode**:
   - **Mode 1 — Synergistic Skill Builder (`Create / Extend`)**: The user wants to add a new capability, workflow, side-loaded add-on (`addons/`), or helper script.
   - **Mode 2 — Permission-Based Cleanup Protocol (`Audit / Consolidate`)**: The user wants to audit existing skills/rules/add-ons/scripts for redundancy, wasted turns, synergy gaps, or Homunculus compliance—or we are running a pre-release hygiene gate.
2. **Read Target Files Directly (Two-Mode `.py` Accuracy Override)**:
   - Because `skill-architect` builds, audits, and refactors skills and CLI scripts, **reading the exact `SKILL.md`, `references/*.md`, and `.py` source files under evaluation is mandatory (`Chesterton's Fence`)**. Never guess what a skill or script does from its filename or a summary sheet.
3. **Run the Deterministic Hygiene & Synergy Inspector First**:
   - For **Mode 1 (`Create / Extend`)**, run the pre-creation overlap check across `rules/`, `skills/`, and `addons/`:
     ```bash
     python3 <HOMUNCULUS_ROOT>/skills/skill-architect/scripts/audit_skill_hygiene.py \
       --check-new "<proposed_skill_name>: <1-2 sentence description of intent and triggers>"
     ```
   - For **Mode 2 (`Audit / Consolidate`)**, run the non-destructive hygiene and Homunculus compliance audit:
     ```bash
     python3 <HOMUNCULUS_ROOT>/skills/skill-architect/scripts/audit_skill_hygiene.py --audit --strict-structure
     ```

---

## 2. Step-by-Step Execution Procedures

### Mode 1: Synergistic Skill Builder (`Create / Extend`)

When the user requests a new skill, rule, side-loaded add-on, or workflow helper:

1. **Step 1 — Pre-Creation Overlap & Consolidation Gate (`Rule -> Existing Skill -> Side-Loaded Add-On -> Composite -> New Delta`)**:
   - Inspect the output of `audit_skill_hygiene.py --check-new "..."`, which scores overlap against **`always_on` rules (`100%` turn tax), on-demand `skills/`, and dormant `addons/`**:
     - **`ALREADY_IN_CORE_RULE (<rule>)`** (`rule body_coverage >= 65%`): The capability is already enforced on every turn by an always-on global rule (`co-engineering-partner`, `verifiable-accuracy`, or `data-and-credential-safety`). Do **not** spawn a redundant skill—either rely on the existing rule or add a surgical clause/script flag to that rule.
     - **`EXTEND_EXISTING (<skill_or_addon>)`** (`skill overlap >= 45%` or `body_coverage >= 65%`): Recommend adding a new Procedure, Mode, or `references/*.md` file to that existing skill/add-on (or dropping an existing `addons/<name>` folder into `skills/<name>`) rather than spawning a competing standalone skill.
     - **`COMPOSITE_ALREADY_COVERED (<skill_A + skill_B>)`** (`union coverage >= 75%`): The request is a mashup of `2+` existing skills/rules; orchestrate the existing skills rather than building a wrapper skill.
     - **`CREATE_DELTA_SKILL` vs. `CREATE_SIDELOAD_ADDON`**:
       - Place universally ready engineering workflows in `skills/<new-skill>/SKILL.md`.
       - If the module requires user-specific calibration history, external corpus collection, or optional setup time (like `author-voice-cadence`), package it in `addons/<new-addon>/SKILL.md` so it stays dormant on day-one startup and can be activated via simple Zero-Install Drop-In folder copy into `skills/`.
2. **Step 2 — Backbone Synergy & Homunculus Compliance Guardrails (Do Not Fight the Ecosystem)**:
   Every new or extended skill must wire into the Homunculus backbone and pass all deterministic guardrails:
   - **Governing Priority Compliance (`1. Accuracy & Truth -> 2. Efficiency -> 3. Data Safety -> 4. Speed`)**: Never invert the priority order or trade away source verification for speed.
   - **Zero-Pip & Cross-OS Portability Guardrail**: Any `.py` script added to `scripts/` must use **100% Python 3.10+ standard library** (`audit_skill_hygiene.py` and `audit_portability.py` fail closed on third-party `pip` imports unless guarded by optional runtime `importlib.util.find_spec` with a pure-stdlib fallback) and must resolve paths via `<HOMUNCULUS_ROOT>` / `homunculus_paths.py` (`0` hardcoded `/home/<user>`, `/Users/<user>`, or `C:\Users\<user>` paths).
   - **Memory Synergy (`project-memory`)**: Route project state via `<memory_root>/Projects/<Project>/<Project>.md` (`AUTO-TREE` for Turn-1 routing + live disk verification when mutating) and write tasks exclusively to the canonical `Tasks/*.md` Domain Task Umbrellas (never write `- [ ]` checkboxes inside project dossiers or ad-hoc todo files).
   - **Verification Synergy (`claim-verification`)**: If the skill generates or audits technical prose, BOMs, specs, or diagrams, wire `verify_claims.py` (`VRF-<12hex>`) as its end-of-pass verification gate instead of writing custom prompt-only *"double-check your numbers"* instructions.
   - **Orchestration & Sandbox Synergy (`subagent-orchestrator` & `engineering-sandbox`)**: Use Turn-1 parallel shards with explicit `'flash_lite'`/`'haiku'`, `'flash'`/`'sonnet'`, or `'pro'`/`'opus'` tiers for multi-file work, and use `sandbox_runner.py` (`OS Dry-Run` / `[SANDBOX-PENDING]`) for Track-2 code or data mutations.
   - **Anti-Bloat & Deferred Side-Effects Synergy (`pre-commit-gate`)**: Never instruct the agent to run `sync_memory.py --sync-visuals` or re-render `.svg` diagrams in the middle of a multi-step workflow. Defer derived index and visual updates to `pre-commit-gate` (`X -> Y -> Z`) at task completion.
3. **Step 3 — Delta-Only Authoring (Zero Core-Rule Repetition)**:
   - Assume the `3` always-on global rules (`co-engineering-partner.md`, `verifiable-accuracy.md`, `data-and-credential-safety.md`) are already in context on every turn.
   - Write **only** the domain-specific delta instructions inside `SKILL.md` (linking to core rules or companion skills in `1` line rather than copy-pasting multi-paragraph explanations of `[TBD: CONFLICT]` or Tier 1/2 provenance).
   - Include the `3` mandatory Foundation-First sections required by `co-engineering-partner.md`:
     1. `## 1. Pre-Flight Foundation Checks`
     2. `## 2. Step-by-Step Execution Procedures` (with explicit `Verification Gates`)
     3. `## 3. Stop & Escalation Conditions`
   - Log any new end-user CLI commands or prompt triggers into [`docs/Commands_and_Prompts_Reference.md`](../../docs/Commands_and_Prompts_Reference.md).
4. **Step 4 — Mode 1 Verification Gate**:
   - Run `audit_skill_hygiene.py --audit --strict-structure --target-skill <skill_name>` and `audit_portability.py`, confirming `0` structural errors, `0` broken links/scripts, `0` portability/pip violations, and `0` turn-waste hazards.

---

### 2.1 AI Configuration & Optional Module Lifecycle Guide (`skills/` vs. `addons/`, Cross-OS Paths & Adapter Sync)

Whenever an AI system uses `skill-architect` to configure a workspace, create/extend a skill, promote an add-on from `addons/<name>/` into `skills/<name>/`, or demote/delete an optional module:

1. **Strict Separation Between Core Active Skills (`skills/`) and Optional Add-Ons (`addons/`)**:
   - **Dormant Until Activated**: Optional modules inside `addons/<name>/` (such as `addons/author-voice-cadence/`) must remain **100% decoupled** from core startup, memory sync (`sync_memory.py`), claim verification (`verify_claims.py`), and adapter builds (`build_adapters.py`).
   - **Deletion & Demotion Resilience**: A consumer may leave an `addons/<name>/` module unconfigured indefinitely or delete `addons/<name>/` (or the entire `addons/` folder) from disk. Never hardcode references to a specific `addons/<name>/` path inside core Python scripts, adapter fallback branches (`build_adapters.py`), or regression test suites (`tests/*.py` must wrap optional add-on tests in `unittest.skipUnless((REPO_ROOT / "addons" / "<name>").is_dir(), ...)`).
   - **Promoting or Demoting a Module (`Zero-Install Drop-In` + Adapter Refresh)**:
     - To **activate** an add-on: copy or move `addons/<name>/` $\rightarrow$ `skills/<name>/`.
     - To **deactivate** or remove an optional skill: move `skills/<name>/` $\rightarrow$ `addons/<name>/` (or delete it).
     - Whenever skills or add-ons are added, moved, or removed, synchronize the workspace client adapters (`AGENTS.md`, `CLAUDE.md`, `.cursor/rules/`, `.agents/skills/`) via:
       ```bash
       python3 <HOMUNCULUS_ROOT>/scripts/build_adapters.py --workspace <workspace_root> --client all --prefer-copy
       ```
2. **Cross-OS Configuration & Path-Binding Rules (`Windows`, `macOS`, `Linux` Parity)**:
   - **Unified Memory-Root Resolution**: Every skill script that reads or writes project memory must resolve `<memory_root>` in strict precedence order: explicit `--memory-root` CLI flag $\rightarrow$ `HOMUNCULUS_MEMORY_ROOT` environment variable $\rightarrow$ `.homunculus.json` (`memory_dir` via `homunculus_paths.resolve_workspace_config()`) $\rightarrow$ `<workspace_root>/memory`.
   - **Windows Backslash & Cross-Drive Safety**: Normalize path strings retrieved from frontmatter, JSON configs, or CLI flags via `.replace("\\", "/")` before constructing `Path(...)` objects so Windows-authored files work identically on macOS and Linux. Whenever calling `os.path.relpath(src, dst)` (e.g., for symlink vs. copy fallback), always catch `except (OSError, ValueError):` because Windows raises `ValueError` when `src` and `dst` reside on different drive letters (`C:\` vs. `D:\`).
   - **Ergonomic CLI Flag Normalization**: Normalize hyphenated vs. underscored enum choices (`s.strip().lower().replace("-", "_")`) so CLI invocations succeed regardless of whether a user or agent passes `--client claude-code` or `--client claude_code`.
3. **Consumer 4-Tier vs. Framework-Builder Priority Separation**:
   - All consumer-facing rules, skills, and generated workspace adapters enforce the **4-Tier Consumer Governing Priority Law (`1. Accuracy & Truth -> 2. Efficiency -> 3. Data Safety -> 4. Speed`)** so consumer application repositories are never restricted from using their own language packages or frameworks.
   - Homunculus's own internal scripts (`scripts/*.py`, `skills/*/scripts/*.py`, `addons/*/scripts/*.py`) remain 100% Python 3.10+ standard library across Windows, macOS, and Linux.

---

### Mode 2: Permission-Based Cleanup Protocol (`Audit / Consolidate`)

When auditing existing user skills, rules, add-ons, or scripts (or dogfooding `skill-architect` itself):

1. **Step 1 — Strictly Advisory, Non-Authoritarian Posture (`Chesterton's Fence`)**:
   - **Never** automatically delete, strip, or overwrite existing skills, rules, or functions during an audit turn.
   - Static overlap detection can spot repeated phrases or similar triggers, but a repeated constraint inside a domain skill may be an intentional **Cold-Start Accuracy Anchor** (needed when a `Blind` subagent reads only that single `SKILL.md`) or a guard against an external hardware/enterprise edge case.
2. **Step 2 — Run Deterministic Telemetry & Contextual Triage**:
   - Execute `audit_skill_hygiene.py --audit --strict-structure` to gather objective metrics: line/word/token footprint per rule/skill/add-on, structural/link health, zero-pip/portability compliance, orphan scripts, always-on rule repetition hunks, cross-skill shingle overlaps, and turn-waste anti-patterns.
   - Read the flagged line ranges in context (`30–80` line window) and classify each finding into one of eight explicit advisory buckets:

| Advisory Tag | Meaning & Recommended Action | Authority Check (`1. Accuracy -> 2. Efficiency -> 3. Data Safety -> 4. Speed`) |
| :--- | :--- | :--- |
| **`[LOAD-BEARING DEFECT]`** | Broken script/reference path, missing required foundation section, missing rule `trigger: always_on` frontmatter (`MISSING_RULE_TRIGGER_FRONTMATTER`), non-functional build-phase module/skill name (`NON_FUNCTIONAL_MODULE_NAME`), dev-journal cross-bleed (`DEV_JOURNAL_CROSS_BLEED`), hardcoded OS user path (`HARDCODED_USER_PATH_IN_SKILL`), unguarded third-party `pip` import (`NON_STDLIB_SKILL_SCRIPT`), or accuracy-inverting rule (`BLANKET_PY_SOURCE_BAN` / `UNSCOPED_LS_FIND_BAN`). | **Fix Required**: Threatens `#1 Accuracy & Truth` or causes tool failures. |
| **`[ALWAYS-ON RULE DUPLICATION]`** | Two `always_on` rules repeat the same instructions (`Rule A <-> Rule B`). | **Highest Token Priority (`100%` Turn Tax)**: Loaded on every turn of every session; deduplicate immediately while preserving accuracy. |
| **`[TURN-WASTE HAZARD]`** | Instructs mid-task `--sync-visuals` / diagram renders outside `pre-commit-gate`, ambiguous `./scripts/*.py` CLI paths without `<HOMUNCULUS_ROOT>`, per-edit hooks, or unscoped directory crawling. | **High-Value Fix**: Wastes turns/tokens (`#2 Efficiency` / `#4 Speed`) with zero accuracy benefit. |
| **`[KEEP IN SKILL / CHECK ALWAYS-ON RULE FOOTPRINT]`** | An `always_on` rule explicitly delegates to an on-demand skill (e.g., `co-engineering-partner` $\rightarrow$ `subagent-orchestrator`), and both contain the same operational block. | **Reverse Directionality**: The on-demand skill is the canonical runbook—keep full detail in the skill, and keep only the Turn-1 trigger + load-bearing safety overrides in the `always_on` rule. |
| **`[KEEP — OPERATIONAL CLI / FLAG ANCHOR]`** | Shares text with an `always_on` rule, but binds concrete CLI flags (`--fail-on-tbd`, `--strict-provenance`) or diagnostic codes (`DIRTY_GIT_WORKTREE`) absent from the rule. | **Protected**: Trimming to a rule pointer strips operational CLI syntax and forces extra `--help` turns or skipped flags. |
| **`[KEEP — ACTION-SITE DOMAIN INSTANTIATION]`** | Translates an abstract `always_on` rule into concrete domain negative constraints at the point of action (`TPU` vs. `ABS/ASA`, fastener counts/modifiers). | **Protected**: Removing action-site domain constraints causes `Blind-Light` agents to commit Qualitative Dodging (omitting fastener counts/conflicts). |
| **`[KEEP INLINE — PREVENTS POINTER-HOP TOKEN INVERSION]`** | Two skills share a compact operational excerpt (`<= 140` words), while the companion skill is `>= 3x` larger. | **Protected**: Replacing a `~100`-token inline summary with a cross-skill `#Heading` pointer forces an extra `read_file` turn that loads `1,500–2,300` tokens into the KV-cache. |
| **`[SUGGESTED TRIM — ALREADY IN CORE RULES]`** / **`[CANDIDATE MERGE / POINTER]`** | Pure generic rule repetition (zero unique CLI flags or domain instantiations) or large multi-paragraph (`> 140w`) skill duplication where a pointer saves net tokens. | **Permission Required**: Condense or replace with a `#Heading` pointer only after verifying net token savings and `Blind`/`Visible` cold-start accuracy. |

3. **Step 3 — Calibrate the Auditor First (Two-Pass Improvement Loop)**:
   - Whenever a static heuristic in `audit_skill_hygiene.py` produces a noisy false positive or misses a nuanced synergy pattern, **improve `audit_skill_hygiene.py` and `skill-architect/SKILL.md` first** before touching the target skills. Never embed external project development journals or ticket IDs inside operational rules or skills (`DEV_JOURNAL_CROSS_BLEED = 0`).
4. **Step 4 — Present Opt-In Proposals & Wait for User Permission**:
   - Present the categorized audit table with exact `path#Lstart-Lend` links, estimated token/line reductions, and any cold-start trade-offs.
   - Apply modifications to target skills **only after** the user confirms which proposals to execute.

---

## 3. Stop & Escalation Conditions

Halt immediately and consult the user if:
1. **Accuracy vs. Brevity Conflict**: Trimming a repeated instruction from a `SKILL.md` would leave a `Blind-Light` / `Blind-Full` cold-start subagent (which may only be prompted to read that single `SKILL.md` without companion skills) unaware of a domain-specific `[TBD]` or safety invariant (`Accuracy & Truth > Efficiency`).
2. **Portability Violation in Proposed Skill/Script**: A proposed skill or helper script relies on an OS-specific binary, hardcoded user path, or unguarded third-party `pip` library without a pure-stdlib fallback.
3. **Unknown External Context on User Functions/Scripts**: An unreferenced script or custom instruction appears unused locally, but may be invoked by an external cron job, IDE task, or user shell alias—flag as `[ORPHAN CANDIDATE — CONFIRM EXTERNAL USAGE]` rather than deleting.
4. **Validator Fail-Open Defect**: `audit_skill_hygiene.py --strict-structure` exits `0` on a synthetic broken-link, missing-section, or portability fault during `OS Dry-Run (+faults)`.
