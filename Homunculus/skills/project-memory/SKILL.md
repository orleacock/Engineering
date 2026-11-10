---
name: project-memory
description: Dual-Mode Engineering Memory (`Headless` Markdown + `Obsidian` Vault) manager and templatizing skill. Activate on Turn 1 whenever the user queries, onboards, audits, or updates any project, task umbrella, lesson learned, quarantine note, or deliverable template across `<memory_root>/`.
---

# Skill: Dual-Mode Project Memory & Templatization (`project-memory`)

Refer to [`Memory_Setup_README.md`](../../docs/Memory_Setup_README.md) for directory layout and Zero-Script AI fallback instructions.

---

## 1. Pre-Flight Foundation Checks

Before reading or mutating project files or memory notes, verify:
1. **Memory Root Resolution**: Locate `<memory_root>` via `.homunculus.json` (`memory_dir`), `--memory-root`, or `./memory` / `./vault`. If no memory root exists and the user requests project memory onboarding, initialize it via [`sync_memory.py`](scripts/sync_memory.py) (`--init-memory`) or native file writes from [`templates/memory/`](../../templates/memory/).
2. **Turn-1 Hub Dossier, `memory/AGENTS.md`, `Lessons_Learned`, `Directory/` Lookup Tree & Session Kickstart**: Read `<memory_root>/AGENTS.md` (when present), `<memory_root>/Projects/<Project>/<Project>.md` (plus `<Project>_Lessons_Learned.md` and `Profile/Decision_Profile.md` whenever auditing, debugging, modifying, or sectionally rebuilding the project) and `<memory_root>/Directory/<Entity>_Directory.md` (`Directory/Directory_Index.md` for shared `Standards_and_Specs/` / `Templates/` lookup, or `Directory/<Entity>_Decision_Router.md` for Zero-CLI `TIER0`–`TIER5` radar routing) on Turn 1 to obtain `entity`, `compartment`, `project_type`, `local_path`, `SESSION-HANDOFF` stopping context, `Subsystem Rebuild & Invariant Matrix` (`Must-Keep Invariants` vs. `Retired Bloat`), and the `--- DIRECTORY STRUCTURE ---` / `AUTO-TREE` file map without running blind `ls`/`find`/`os.listdir` scans. When resuming after a break, run `sync_memory.py --memory-root <memory_root> --project <Project> --kickstart` (`< 10ms` provenance check comparing `checkpoint_head_sha` and `checkpoint_tree_hash` against the live repository) and present the saved stopping point and discussion items to the user before mutating files. If moved to a new workstation (`[STATION_REANCHORED]`), run `--rebind-station` (`[--dry-run]`) to update local station bindings.
3. **Peer-Entity / Multi-Customer Firewall**: Check the `entity:` key inside `<Project>.md` frontmatter and enforce `CROSS_ENTITY_CONTAMINATION` isolation across `Projects/<Other>/`, `Tasks/<Other>_Tasks.md`, and `Directory/<Other>_Directory.md` whenever `entity:` values differ.

---

## 2. Core Workflows & Separate Telemetry Functions

### Workflow A: Initialize Memory Root or Onboard a Project (`--init-memory` / `--init-project`)
1. Run [`sync_memory.py`](scripts/sync_memory.py) to scaffold the memory root or onboard a project using the canonical templates in [`templates/memory/`](../../templates/memory/):
   ```bash
   python3 <HOMUNCULUS_ROOT>/skills/project-memory/scripts/sync_memory.py \
     --memory-root <memory_root> \
     --init-project <Project> \
     --repo-path <repo_path> \
     --type <hardware|software|hybrid> \
     --entity "<Client_or_Org>" \
     --compartment <private|public|cleanroom>
   ```
2. **Mandatory Project-Template Prompt Trigger**: Immediately upon onboarding a project—or whenever you detect a recurring deliverable format during a session (e.g., BOM table, customer quote sheet, test report, assembly checklist)—ask the user:
   > *"Would you like me to create and maintain a canonical template for this deliverable inside `Projects/<Project>/Templates/` (or promote it to `<memory_root>/Templates/`)?"*

### Workflow B: Separate Domain Telemetry Synchronization (`--sync-hardware` vs. `--sync-software`)
Never use a monolithic parser for unrelated domains. Invoke the specific telemetry function matching the project's `project_type`:
1. **Hardware Telemetry (`sync_hardware_telemetry` $\rightarrow$ `<Project>_Hardware.md`)**:
   ```bash
   python3 <HOMUNCULUS_ROOT>/skills/project-memory/scripts/sync_memory.py \
     --memory-root <memory_root> --project <Project> --sync-hardware
   ```
   Indexes `.step`/`.stl`/`.3mf` bounding boxes, bore features, and `.cfg`/`.kicad_pcb` hardware parameters.
2. **Software Telemetry (`sync_software_telemetry` $\rightarrow$ `<Project>_Software.md`)**:
   ```bash
   python3 <HOMUNCULUS_ROOT>/skills/project-memory/scripts/sync_memory.py \
     --memory-root <memory_root> --project <Project> --sync-software
   ```
   Indexes runtime entrypoints, CLI flags (`argparse`/commands), JSON/YAML schemas, and test suite receipts.
3. **Single-Project, Batch `AUTO-TREE` & `Directory/` Tree Refresh (`--sync-tree` / `--sync-trees` / `--sync-directory`)**:
   ```bash
   python3 <HOMUNCULUS_ROOT>/skills/project-memory/scripts/sync_memory.py \
     --memory-root <memory_root> --project <Project> --sync-tree
   # Or batch-refresh all indexed project AUTO-TREEs + Directory/ box trees at pre-commit-gate wrap-up:
   python3 <HOMUNCULUS_ROOT>/skills/project-memory/scripts/sync_memory.py \
     --memory-root <memory_root> --sync-trees
   ```

### Workflow C: Quarantine Zone & Lessons Learned Management
1. **Quarantine Holding Zone (`## Quarantine Zone` & `Projects/<Project>/Quarantine/`)**:
   - Store all unverified scratch notes, preliminary vendor quotes, and unresolved `[TBD: ...]` items inside `<Project>.md`'s `<!-- QUARANTINE-ZONE:START -->` block or inside `Projects/<Project>/Quarantine/`, and query the workspace-wide open `[TBD]` / `[CONFLICT]` rollup anytime via `--tbd-ledger [--umbrella <Entity>]`.
   - Treat all quarantined content as `[QUARANTINED — DO NOT CITE AS FACT]`. Only promote an item out of Quarantine after verifying it via `verify_claims.py` (`claim-verification`) against primary source telemetry.
2. **Lessons Learned, `TIER0`–`TIER5` Gravity & Sectional Rebuild Blueprints (`<Project>_Lessons_Learned.md`)**:
   - Maintain two structured sections in every `<Project>_Lessons_Learned.md`:
     1. **`Subsystem Rebuild & Invariant Matrix` (`<!-- SUBSYSTEM-INVARIANTS:START/END -->`)**: Lists `Must-Keep Invariants (Chesterton's Fence)` alongside `Retired Bloat / Anti-Patterns (Never Re-Add)` per module or assembly so sectional rebuilds and Pre-Mutation Advisories never re-introduce retired bugs or strip load-bearing guards. Before modifying any script or module, run `--preflight <script.py>` (which combines `scripts/script_contracts.json`, `SUBSYSTEM-INVARIANTS`, and Top-3 1-line radar capsules and records `.cache/preflight_state.json`), `--recall "<query>"` (`<= 600` tokens; `100%` non-numeric semantic & identifier recall), or `--invariants [<subsystem_query>]` (and never read `> 30` lines of `0444` `Archive/*_Lessons_Archive.md` directly—use `--lesson-id LL-xxx`):
        ```bash
        python3 <HOMUNCULUS_ROOT>/skills/project-memory/scripts/sync_memory.py \
          --memory-root <memory_root> --project <Project> --preflight <script.py>
        python3 <HOMUNCULUS_ROOT>/skills/project-memory/scripts/sync_memory.py \
          --memory-root <memory_root> --project <Project> --recall "<query>" [--top-k 3]
        python3 <HOMUNCULUS_ROOT>/skills/project-memory/scripts/sync_memory.py \
          --memory-root <memory_root> --project <Project> --lesson-id LL-xxx
        ```
     2. **Chronological Post-Mortem & ADR Ledger (`Symptom -> Root Cause -> Permanent Guardrail`)**: Record every root-cause post-mortem (`LL-xx`) and Architectural Decision Record (`ADR-xx`) immediately after sandbox or bug diagnosis via `--add-lesson [--tier TIER0..TIER5]` (which scrubs filler, appends additive `SUBSYSTEM-INVARIANTS` rows, and keeps `<= 3` `TIER0` + `<= 7` `TIER2` active full-context sections in `<Project>_Lessons_Learned.md` while graduating stabilized `TIER3`–`TIER5` narratives to `Archive/<Project>_Lessons_Archive.md` via `--compact-memory` or `--set-tier [--user-confirmed --reason "..."]`):
        ```bash
        python3 <HOMUNCULUS_ROOT>/skills/project-memory/scripts/sync_memory.py \
          --memory-root <memory_root> --project <Project> --add-lesson \
          --symptom "<Observed failure (<=120w)>" --root-cause "<Verified root cause (<=120w)>" \
          --guardrail "<Permanent invariant enforced (<=140w)>" --files "<repo_rel_file1>[,<file2>]" \
          [--receipt "<VRF-... / SBX-...>"] [--tier TIER2] [--subsystem "<Module>" --must-keep "<Invariant>" --retired-bloat "<Anti-pattern>"]
        # Reinforce an existing TIER0-TIER4 lesson when catching a recurring anti-pattern variant:
        python3 <HOMUNCULUS_ROOT>/skills/project-memory/scripts/sync_memory.py \
          --memory-root <memory_root> --project <Project> --reinforce-lesson <LL-xxx> \
          --files "<repo_rel_file>" --retired-bloat "<Newly blocked variant>" [--must-keep "<Updated invariant>"]
        python3 <HOMUNCULUS_ROOT>/skills/project-memory/scripts/sync_memory.py \
          --memory-root <memory_root> --project <Project> --compact-memory
        python3 <HOMUNCULUS_ROOT>/skills/project-memory/scripts/sync_memory.py \
          --memory-root <memory_root> --project <Project> --repair-memory
        ```
     3. **Memory Preservation, Situational Adaptation & Protected Governance Seal (`Rules 1–8`)**:
        - **Situational Adaptation & Obsolete-System Triage**: Express `TIER0`–`TIER4` guardrails as transferable principles bound to `1–4` live files (`Active Operational Binding`); treat symptom narratives as inert anti-examples. Never leave retired-system scaffolding in active tiers—repurpose in place or retire to `TIER5` (`--set-tier <ID> TIER5 --user-confirmed --reason "<Why + Active Replacement>"`), which stamps inline `Retirement Provenance` and prunes the active Quick-Lookup row.
        - **Protected Rule & Archive Surfaces (`0444` Lock + `v1.1` Seal)**: `memory/AGENTS.md` (`<= 180 words` / `<= 2200 B`), `Profile/Decision_Profile.md` (`<= 60 lines`), `Standards_and_Specs/*.md` (including `Governance_and_Constraint_Architecture.md`), and `Projects/*/Archive/*_Lessons_Archive.md` (with monotonic `retired_tier5_hashes`) are locked `0444` via `--lock-memory-rules` and SHA-256 hash-sealed in `Directory/governance_seal.json` alongside every project's `SUBSYSTEM-INVARIANTS` block (`<= 420` lines / `<= 10` active sections in `_Lessons_Learned.md`) and hash-chained `Directory/governance_audit_log.jsonl`. Modifying any protected rule/standard, removing a `TIER1` invariant, demoting `TIER0`, or retiring to `TIER5` requires halting for a **3-Part Governance Advisory** (Chesterton's Fence + Blast Radius + Diff) and explicit user confirmation (`--unlock-memory-rules` $\rightarrow$ edit $\rightarrow$ `--seal-governance --user-confirmed --reason "..."` $\rightarrow$ `--lock-memory-rules`).
3. **Single-Writer Task Umbrellas (`Tasks/<Entity>_Tasks.md`)**:
   - Record all `- [ ]` / `- [x]` checkboxes exclusively inside `Tasks/<Entity>_Tasks.md`, query open tasks via `--tasks [--umbrella <Entity>]`, and refresh rollup counts via `--sync-tasks`.

### Workflow D: Session Handoff & Multi-Session Kickstart (`--save-handoff` / `--kickstart`)
1. **End-of-Session Handoff Recording (`--save-handoff`)**:
   - When pausing work at the end of a session or milestone, overwrite `<Project>.md`'s `<!-- SESSION-HANDOFF:START/END -->` block in place (`O(1)` file size; supports `500–800+ word` multi-paragraph stopping context, active `Project State Ledger` state, and next-session discussion points via `--stopped-at` / `--next-steps` / `--discussion` or `--handoff-file`):
   ```bash
   python3 <HOMUNCULUS_ROOT>/skills/project-memory/scripts/sync_memory.py \
     --memory-root <memory_root> --project <Project> --save-handoff \
     --stopped-at "<Detailed stopping state & completed milestone context>" \
     --receipt "<VRF-... / SBX-... / test receipt>" \
     --blockers "<None | [OPEN-xx] | [SANDBOX-PENDING]>" \
     --next-steps "<Step 1 | Step 2 | Step 3>" \
     --discussion "<Key decision or alignment point for next session>" \
     [--lesson-disposition "NONE:<verified non-defect cosmetic/doc reason>"]
   ```
2. **Turn-1 Cold-Resume Verification & Auto-Heal (`--kickstart`)**:
   - When resuming a project after days or weeks, verify live `git HEAD` and `tree_hash` provenance against the saved checkpoint before mutating files (`--kickstart` records `DRIFT_DETECTED` against `checkpoint_tree_hash` *first*, then automatically refreshes `Directory/*.md` and `AUTO-TREE` via write-if-changed):
   ```bash
   python3 <HOMUNCULUS_ROOT>/skills/project-memory/scripts/sync_memory.py \
     --memory-root <memory_root> --project <Project> --kickstart
   ```
3. **Targeted Dossier & Section Reader (`--project <Project> --section <Section>`)**:
   - To fetch a specific section (`all`, `concept`, `inventory`, `specs`, `hazards`, `architecture`, `tbd`, `tasks`, `lessons`, `handoff`, `hardware`, `software`) with inline task transclusion in a single CLI call:
   ```bash
   python3 <HOMUNCULUS_ROOT>/skills/project-memory/scripts/sync_memory.py \
     --memory-root <memory_root> --project <Project> --section <Section>
   ```

---

## 3. Step-Level Verification Gates

Before completing any memory initialization, project onboarding, or pre-commit wrap-up:
1. Run the deterministic memory containment and structure audit:
   ```bash
   python3 <HOMUNCULUS_ROOT>/skills/project-memory/scripts/sync_memory.py \
     --memory-root <memory_root> --audit [--verify-checkpoints]
   ```
2. Confirm `0` violations across:
   - `CROSS_ENTITY_CONTAMINATION` (zero links or references between projects belonging to different `entity:` values).
   - `CHECKBOX_IN_PROJECT_HUB` (zero `- [ ]` checkboxes leaked into `Projects/<Project>/<Project>.md`).
   - `BROKEN_MEMORY_LINK` (all relative POSIX markdown links resolve on disk).
   - `MISSING_ENTITY_FRONTMATTER` (every project hub declares `entity:`, `compartment:`, and `project_type:`).
   - `MEMORY_RULE_GOVERNANCE_BREACH` / `UNLOCKED_GOVERNANCE_SURFACE` / `MEMORY_RULE_BLOAT_CEILING` / `OBSOLETE_MEMORY_ANCHOR` (verifies `Directory/governance_seal.json`, `Directory/governance_audit_log.jsonl` hash chain, `0444` lock state, rule word/line ceilings, and zero retired-system scaffolding in active `TIER0`–`TIER4` tiers).
3. Defer full multi-project visual/index rebuilds (`--sync-visuals` and `--export-canvas`) to `pre-commit-gate` (`X -> Y -> Z`) rather than running them after intermediate mid-session edits.

---

## 4. Stop & Escalation Conditions

- **`[CROSS_ENTITY_CONTAMINATION]` Detected**: Halt immediately if any file or prompt attempts to link or copy data between two distinct customer/entity scopes (`entity: Client_A` $\leftrightarrow$ `entity: Client_B`) without explicit user authorization.
- **`[DRIFT_DETECTED]` on Session Kickstart**: If `--kickstart` reports that `checkpoint_head_sha` or `checkpoint_tree_hash` changed out-of-band since the last recorded session, surface the exact drift reasons to the user and reconcile before executing dependent code changes.
- **Quarantine Promotion Without Primary Proof**: Halt and refuse to move a specification out of `Quarantine/` if no primary CAD, code, config, or measurement anchor exists (`[TBD: ...]`).
- **`[SANDBOX-PENDING]` Gate**: Any modification to [`sync_memory.py`](scripts/sync_memory.py) or memory parser logic is a Track-2 change requiring an `OS Dry-Run (+faults)` sandbox verification pass before promotion to `[SOLVED]`.
