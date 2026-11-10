---
title: "Homunculus Stateful Memory Rebuild & Deployment Action Plan"
project: "Homunculus"
entity: "Alchemical-3D"
compartment: "private"
note_type: "reference"
last_synced: "2026-11-09"
---

# Action Plan: Stateful, Decision-First & Multi-Way Portable Memory Engine

Part of [`Homunculus.md`](Homunculus.md) • Companion to [`Homunculus_Cleanroom_Promotion_Diff.md`](Homunculus_Cleanroom_Promotion_Diff.md) & [`Homunculus_Lessons_Learned.md`](Homunculus_Lessons_Learned.md)

> [!IMPORTANT]
> **Governing Priority Mandate (`1. Accuracy & Truth > 2. Efficiency > 3. Data Safety > 4. Speed`)**
> *"A system that remembers its mistakes is not necessarily a system that learns from them; the real meaningful change is when that system makes fewer errors or circular edits using those memories."*
> This plan elevates our memory system from a passive Turn-1/end-of-task archive into a **Front-of-Decision Engineering Gate** while respecting the core architectural distinction between a **Shipped Deliverable (`Homunculus`)** and a **Live Parent Station (`memory/` on our workstation or an end-user's workstation)**:
> 1. **Shipped Deliverable Portability (`Homunculus` Clean-Room Product)**: Ships `100%` generic (`templates/memory/`, `scripts/script_contracts.json`, `0` `/home/orin` relics or parent-station project data). Once installed on an end-user station, it attaches to *that* station and evolves into its local parent system.
> 2. **Live Parent Station Power (`Absolute Paths + Local Indexes Welcome`)**: On a live workstation (ours or an end-user's after delivery), absolute `local_path` bindings and local indexes (`Directory/<Entity>_memory_index.json`) are first-class, high-speed primitives—never outlawed on the active station.
> 3. **Cross-Machine & Cloud/Detached Resilience (`Station Re-Anchoring + Detached Cache Mode`)**: When a Parent Memory Vault is migrated to a new machine (`--rebind-station`) or hosted online in the cloud (where the original station's `local_path` is not mounted), the engine automatically re-anchors against the new station's workspace root or operates in **Detached Cache Mode** (`worktree: "detached_cache"`) without crashing or corrupting cached `AUTO-TREE` / hardware telemetry.

---

## 0. Context Window Accounting Ledger ("Eyes on the Context We Use and Do Not Use")

To prevent our memory rebuild from creating the very "Token Bomb" or "Partial-Recall Blindness" we are trying to cure, every sprint is governed by explicit **Context Inclusion vs. Exclusion Rules**:

| Context Layer | What Enters the Active Model Prompt (`USED`) | Token Budget | What Stays on Disk / Excluded from Prompt (`NOT USED`) | Why It Stays Out |
| :--- | :--- | :---: | :--- | :--- |
| **Layer 1: Turn-1 Session & Routing Spine** | - [`Alchemical-3D_Directory.md`](../../Directory/Alchemical-3D_Directory.md) (or `Directory_Index.md`)<br>- `Profile/Decision_Profile.md` (Standing Co-Engineering Decision Laws)<br>- [`Homunculus.md`](Homunculus.md) (`Concept` + `SESSION-HANDOFF` + compact `SUBSYSTEM-INVARIANTS` summary table via `--kickstart`) | **`~1,100 – 1,600` tokens** | - Full `504`-line [`Homunculus_Lessons_Learned.md`](Homunculus_Lessons_Learned.md) (`~13,800` tokens)<br>- Unrelated `<Other_Entity>_Directory.md` or sibling project dossiers<br>- `Archive/<Project>_Lessons_Archive.md` | Prevents the `14k`-token Turn-1 context bomb and preserves `CROSS_ENTITY_CONTAMINATION` isolation. |
| **Layer 2: Front-of-Decision / Pre-Mutation Gate (`--preflight` / `--recall` / `--map`)** | - **100% of Target Subsystem's `TIER0`/`TIER1` Invariants & Retired Anti-Patterns** (from `SUBSYSTEM-INVARIANTS` + `scripts/script_contracts.json`)<br>- **100% of `1-Hop` Functional & Data-Contract Coupled Scripts**<br>- **Top-$N$ (`N=3`, `~105` tokens)** 1-line `LL-xxx` radar capsules matching the task intent | **`<= 450` tokens** | - The other `34+` unrelated `LL-xxx` historical post-mortem narratives<br>- Full-context sections not needed for the current step<br>- Raw `.step`/`.stl` geometry or `hw_telemetry.json` | Guarantees **100% deterministic recall of invariants** (zero circular edits) while keeping radar breadth at `~35` tokens per capsule. |
| **Layer 3: Deep Forensic Drill-Down (Opt-In Only)** | - Specific `--lesson-id LL-xxx` Full-Context Section (`~150–250` tokens) **only** when a radar capsule directly impacts the active decision or bug | **`~200` tokens (On-Demand)** | - Entire `Archive/<Project>_Lessons_Archive.md` file | Keeps cold historical narratives out of the KV-cache during routine engineering turns. |

---

## 1. Architectural Impasse & 5-Path + Combination Synthesis (`LOCKED: Combination C`)

- **Selected Architecture (`Combination C — Full-Spectrum Portable Triad`)**:
  1. **Path 1 (`3-Bucket Markdown + TIER0–TIER5 Gravity Store`)**: `Profile/Decision_Profile.md`, `<Project>_Lessons_Learned.md` (`TIER0` pinned + `TIER1` invariants + `TIER2` active full-context window), and `Archive/<Project>_Lessons_Archive.md` (`TIER3`–`TIER5`).
  2. **Path 2 (`Entity-Partitioned JSON Index`)**: `Directory/<Entity>_memory_index.json` + Zero-CLI `Directory/<Entity>_Decision_Router.md`.
  3. **Path 4 (`Dedicated Portable Script Contract Index`)**: `Homunculus/scripts/script_contracts.json` + 1-line `Contract :` pointer inside `#L1-L55` of each `.py` script.
  4. **Path 5 (`Unified --map / --preflight Gate`)**: Both `homunculus_paths.py --map <script>` and `sync_memory.py --preflight <script>` output the contract + radar capsules and record a preflight receipt verified by `audit_skill_hygiene.py`.

---

## 2. Section-by-Section Sprint Plan (With Pitfalls, Context Guards & Per-Sprint Audit Gates)

- **Persistent Plan Anchor (Anti-Drift Reference Rule)**: Every sprint step begins and ends by cross-checking its work against this file (`Homunculus_Stateful_Memory_Deployment_Plan.md`); **any deviation from a locked sprint item requires halting and discussing with the user first**.

---

### Sprint 1: Parent-Station vs. Clean-Room Separation, Deployment Docs & Detached-Cache Resolver (`LOCKED`)
**Objective**: Establish the clean boundary between **Live Parent Station Operation** (where absolute `local_path` bindings and local indexes are first-class citizens—zero wasted cycles scrubbing local station paths) and **Tier-Filtered Clean-Room Deliverable Promotion (`TIER0`/`TIER1` Only)**, update `HOMUNCULUS_START_HERE.md` ([`Homunculus_Software.md`](Homunculus_Software.md)) + [`Homunculus_Cleanroom_Promotion_Diff.md`](Homunculus_Cleanroom_Promotion_Diff.md), and upgrade `sync_memory.py` ([`Homunculus_Software.md`](Homunculus_Software.md)) with the **3-Stage Station & Detached-Cache Path Resolver**.

- **What We Will Do**:
  1. **Zero Local Portability Churn + Tier-Filtered Clean-Room Promotion Contract ([`Homunculus_Cleanroom_Promotion_Diff.md`](Homunculus_Cleanroom_Promotion_Diff.md))**:
     - Add **Section 1.4 (`Parent-Station vs. Clean-Room Deliverable Memory & Tier Promotion Contract`)** defining:
       - **Promotes to Clean-Room Deliverable (`TIER0` & `TIER1` Universal Engine Laws Only)**: Distilled generic rules in `scripts/script_contracts.json`, `#L1-L55` `Contract :` pointers, generic starter templates (`templates/memory/Decision_Profile.md`, `templates/memory/AGENTS.md`), and `tests/test_*.py` regression tests (`0` `/home/orin` or personal project names).
       - **Stays Station-Local (`TIER2`–`TIER4` Dev-Cycle & Historical Narratives)**: Full project dossiers, absolute `local_path` bindings, `Directory/<Entity>_memory_index.json`, `TIER2` active dev-cycle sections, and `TIER3`–`TIER4` `Archive/` post-mortems.
       - **Superseded / Retired (`TIER5`)**: Excluded from both Clean-Room promotion and default active parent recall.
  2. **Deployment Machine Onboarding in `HOMUNCULUS_START_HERE.md` (§4)` ([`Homunculus_Software.md`](Homunculus_Software.md)) & `docs/Memory_Setup_README.md` ([`Homunculus_Software.md`](Homunculus_Software.md))**:
     - Add a concise **Station Grounding, Detached Cache & `TIER0`–`TIER5` Gravity** block so any target deployment machine immediately understands:
       - **Generic Arrival $\rightarrow$ Local Grounding**: `Homunculus` arrives generic; running `--init-memory` / `--init-project` grounds it to the deployment machine's real absolute paths (`local_path`), creates its local `Profile/Decision_Profile.md`, `memory/AGENTS.md`, and `Directory/<Entity>_memory_index.json`, and evolves locally with that station.
       - **AI/CLI-Preferred Edit Law & User-Steerable Memory Gravity (`TIER0`–`TIER5`)**: Users or co-engineering agents on the deployment machine can promote any recurring problem to `TIER0` (`sync_memory.py --project <P> --set-tier LL-xx TIER0`) or demote obsolete notes to `TIER5`.
       - **Cross-Machine & Cloud Resilience**: Moving `memory/` to a new machine (`--rebind-station <new_root>`) or opening it in a cloud/web workspace without local git clones automatically runs in **Detached Cache Mode** (`worktree: "detached_cache"`), serving `TIER0`–`TIER2` invariants and cached telemetry cleanly.
  3. **3-Stage Station & Cloud-Detached Repo Resolver in `sync_memory.py` ([`Homunculus_Software.md`](Homunculus_Software.md))**:
     - **Stage 1 (`DIRECT_STATION`)**: `Path(local_path).is_dir()` exists $\rightarrow$ use directly (`0` overhead).
     - **Stage 2 (`REANCHORED_WORKSPACE`)**: `Path(local_path)` missing $\rightarrow$ check candidate workspace roots (`<workspace_root>/<repo_name>`) and provide `sync_memory.py --rebind-station <new_root> [--dry-run]`.
     - **Stage 3 (`DETACHED_CACHE`)**: Repo not cloned locally $\rightarrow$ never fall back to `hub_path.parent` as a fake repo; return `worktree_state = "detached_cache"`, preserve recorded `repo_head_sha` / `AUTO-TREE` / `_Hardware.md` / `_Software.md`, and serve `--kickstart`, `--invariants`, and `--recall` cleanly from cache.
  4. **Fix 2 Concrete Parent-Vault Telemetry Bugs**:
     - Clean the `4` legacy stringified tuples (`checkpoint_worktree: "('clean', [])"` $\rightarrow$ `"clean"`) in [`A3DP_Gantry_Assembly.md`](../A3DP_Gantry_Assembly/A3DP_Gantry_Assembly.md), [`Alchemical_Web_Docs.md`](../Alchemical_Web_Docs/Alchemical_Web_Docs.md), [`Pestle_Rotational_Bowden.md`](../Pestle_Rotational_Bowden/Pestle_Rotational_Bowden.md), and [`Pneuma_Remote_Air.md`](../Pneuma_Remote_Air/Pneuma_Remote_Air.md), and add `MALFORMED_WORKTREE_TUPLE` to `sync_memory.py --audit`.
     - Fix `inspect_hardware_ecosystem.py` (`#L814-L824`)` ([`Homunculus_Software.md`](Homunculus_Software.md)) where `"# 📐 Hardware & CAD Telemetry Manifest:" not in existing_text` skipped updating `AUTO-HARDWARE-CAD` / `AUTO-HARDWARE-CFG` when the heading already existed.

- **⚠️ Sprint 1 Pitfalls & Self-Defeat Traps**:
  - **Pitfall 1A (Wasting Local Turns Scrubbing Parent-Vault Paths)**: Enforce `0` host paths strictly on the **Deliverable Repo** (`Homunculus/` via `audit_portability.py`), while allowing first-class absolute `local_path` bindings in `Engineering/memory/` backed by the 3-Stage resolver.
  - **Pitfall 1B (`_resolve_project_repo()` Treating `memory/Projects/<P>/` as the Source Repo When Unmounted)**: Return an explicit `repo_mounted: bool` / `resolution_stage` so unmounted/cloud projects never overwrite `AUTO-TREE` or `repo_head_sha` with the memory vault's git state.
  - **Pitfall 1C (Terminology Collision)**: Path resolution uses `Stage 1–3` (`DIRECT_STATION`, `REANCHORED_WORKSPACE`, `DETACHED_CACHE`); `TIER0`–`TIER5` is reserved 100% for Memory Importance & Lifecycle Gravity.
- **✅ Sprint 1 In-Flight & Post-Deployment Audit Gate**:
  - **During Deployment (`CoW Dry-Run`)**: Test 3-Stage `_resolve_project_repo()` against (a) mounted `/home/orin/Projects/...`, (b) simulated moved station root (`--rebind-station`), and (c) simulated unmounted Cloud-Detached path.
  - **Post-Deployment Audit**: Run `sync_memory.py --audit` (`0` `MALFORMED_WORKTREE_TUPLE` defects), `audit_repo_docs.py` on updated `HOMUNCULUS_START_HERE.md` & `Memory_Setup_README.md`, `test_project_memory.py` (`PASS`), and `sprint-auditor` check.

---

### Sprint 2: `TIER0`–`TIER5` Gravity Store, Full-Context Dev-Cycle Sections & Dynamic Promotion/Demotion (`LOCKED`)
**Objective**: Replace binary `HOT/COLD` chronological aging with a **`TIER0`–`TIER5` Importance & Lifecycle Gravity Hierarchy** supporting dynamic promotion/demotion and manual user pinning (`--set-tier <LL-xxx> <TIER0..TIER5>`), preserving rich **Full-Context Sections** for `TIER0` (Pinned) and `TIER2` (Active Dev-Cycle) memories while moving `TIER3`–`TIER5` narratives to `Archive/` (`-75%` main file size, `0%` invariant loss).

- **The `TIER0`–`TIER5` Memory Gravity & Lifecycle Matrix**:

| Tier | Role & Importance | Where Full Context Lives | Prompt & Recall Behavior | Promotion / Demotion Mechanics |
| :--- | :--- | :--- | :--- | :--- |
| **`TIER0`** | **Foundational Laws & User-Pinned Repeat Offenders**<br>*(Highest Gravity — `0%` Decay, Immune to Auto-Demotion)* | `Profile/Decision_Profile.md` + **Main `<Project>_Lessons_Learned.md`** (`<!-- TIER0-PINNED -->`, Quota: `<= 3` full-context sections/project) | **Always surfaced (`100%`)** at Turn-1 `--kickstart` and at the top of every matching `--preflight` / `--recall`. | - **Manual User Pin**: `sync_memory.py --project <P> --set-tier LL-xxx TIER0`.<br>- **Demotion**: **User-only** (`--set-tier LL-xxx TIER2 --user-confirmed`). |
| **`TIER1`** | **Load-Bearing Subsystem Invariants & Coupled Contracts**<br>*(`0%` Decay on Rule Contract)* | `<!-- SUBSYSTEM-INVARIANTS -->` in `<Project>_Lessons_Learned.md` + **`scripts/script_contracts.json`** | **100% deterministic injection** whenever the target script or any coupled script is touched via `--preflight`, `--map`, or `--recall`. | - Every verified architectural rule on core scripts lives at `TIER1`. |
| **`TIER2`** | **Active Development Cycle / High-Friction Full-Context Lessons**<br>*(Active Full-Context Window)* | **Main `<Project>_Lessons_Learned.md`** (`## 3. Active Full-Context Sections`, Quota: `<= 7` sections) | Listed in Top-3 radar capsules; Full-Context Section pulled via `--lesson-id LL-xxx` (`<= 250` tokens) when steering decisions. | - Default entry tier for new architectural/code root-cause lessons (`--add-lesson`).<br>- Graduates (`TIER2` $\rightarrow$ `TIER3`) via `--compact-memory` once verified in `TIER1` (`SUBSYSTEM-INVARIANTS`) + unit tests. |
| **`TIER3`** | **Verified & Stabilized Subsystem Lessons**<br>*(1-Line Registry Index in Main File + Full Context in `Archive/`)* | 1-line row in `## 2. Verified Lessons Learned Registry` (`<Project>_Lessons_Learned.md`); Full-Context narrative in **`Archive/<Project>_Lessons_Archive.md`** | Retrieved in Top-$N$ radar capsules by `--recall` / `--preflight`; full context pulled via `--lesson-id LL-xxx`. | - **Re-Promotion (`TIER3 -> TIER2` or `TIER0`)**: `--set-tier LL-xxx TIER2` physically moves its Full-Context section **back from `Archive/` into `<Project>_Lessons_Learned.md`**. |
| **`TIER4`** | **Isolated Polish, Docs & Low-Blast-Radius Fixes**<br>*(Compact Archive Entry)* | 1-line row in Registry + compact entry in **`Archive/<Project>_Lessons_Archive.md`** | Lower priority weight ($0.5\times$) in `--recall` so minor formatting notes never crowd out `TIER0`–`TIER3` architectural guards. | - Enters directly at `TIER4` when logged with `--tier TIER4`. |
| **`TIER5`** | **Superseded / Retired / Obsolete Historical Context**<br>*(Cold Historical Record)* | **`Archive/<Project>_Lessons_Archive.md`** (`[TIER5-SUPERSEDED]`) | **Excluded from default `--recall` / `--preflight`** (`0` ghost-rule confusion); queryable only via `--include-tier5` or `--lesson-id`. | - Demoted via `--set-tier LL-xxx TIER5` when a module, heuristic, or workflow is retired/replaced. |

- **⚠️ Sprint 2 Pitfalls & Guardrails**:
  - **Pitfall 2A (Tier Inflation)**: Enforce slot quotas (`TIER0 <= 3`, `TIER2 <= 7`); block automatic `TIER0` assignment unless `--user-confirmed` or repeat-regression ID is passed.
  - **Pitfall 2B (Ping-Pong Thrashing)**: Read-only commands (`--recall`, `--preflight`, `--kickstart`) never mutate files on disk (`LL-032`).
  - **Pitfall 2C (Duplicate Sections Across Main File & `Archive/`)**: `set_lesson_tier()` is a transactional single-source mover; `sync_memory.py --audit` enforces `DUPLICATE_LESSON_ACROSS_TIERS = 0`.
  - **Pitfall 2D (`PINNED_UNMAPPED_LESSON` & `verify_claims.py` Exclusion)**: Refuse to archive any `LL-xxx` not cited in `SUBSYSTEM-INVARIANTS`, and auto-exclude `Archive/*_Lessons_Archive.md` in `verify_claims.py`.

---

### Sprint 3: Dual-Surface Retrieval Layer, `TIER0`–`TIER5` Scoring & Top-$N$ Radar Integrator (`LOCKED`)
**Objective**: Replace naive substring matching (`q_low in s.lower()`) with an **Entity-Partitioned Hybrid Retrieval & Top-$N$ Radar Integrator** (`Directory/<Entity>_memory_index.json` + `Directory/<Entity>_Decision_Router.md` + `sync_memory.py --recall`) that surfaces `100%` of `TIER0`/`TIER1` invariants plus **Top-3 1-Line Radar Capsules** (`<= 450` tokens total).

- **What We Will Do (`Issues 3A, 3B & 3C` Locked)**:
  1. **Entity-Partitioned Hybrid Indexer (`Directory/<Entity>_memory_index.json` + `Directory/<Entity>_Decision_Router.md`)**: Indexes all `TIER0`–`TIER5` entries with BM25 + Character/Word N-Gram & Domain Stem vectors, `touched_files`, `coupled_scripts`, and `source_sha256_map`.
  2. **Multiplicative `TIER0`–`TIER5` Relevance Scorer**: $\text{Score}_{\text{final}} = R_{\text{base}} \times W_{\text{tier}}$ (gated by $R_{\text{base}} \ge 0.08$).
  3. **Issue 3A (`1-Line Radar Capsules for Ranks #1–#3 by Default`)**: Emits `TIER0` + `TIER1` + Top-3 1-line `LL-xxx` radar capsules (`<= 450` tokens); pull full context on demand via `--lesson-id LL-xxx`.
  4. **Issue 3B (`AI/CLI-Preferred Edit Law & Cooperative Manual-Edit Repair`)**: Emits `[MANUAL_MEMORY_EDIT_DETECTED]` with impact analysis when `source_sha256_map` detects hand-edits outside `sync_memory.py`, repaired cooperatively via `--repair-memory`.
  5. **Issue 3C (`3-Signal True Friction Detection for [TIER_PROMOTION_CANDIDATE]`)**: Passive radar listing does not count as a hit; flags `[TIER_PROMOTION_CANDIDATE]` only when a `TIER3`/`TIER4` memory has (1) `--lesson-id` full-context drill-downs across $\ge 2$ distinct dates/sessions (or $\ge 3$ tasks), (2) a regression/near-miss collision ($\text{Cosine} \ge 0.65$), or (3) coupling growth across $\ge 3$ scripts.

---

### Sprint 4: Front-of-Decision & Mandatory Script-Touch Gate (`scripts/script_contracts.json` + Unified `--map`/`--preflight` Gate — `LOCKED`)
**Objective**: Ensure every decision or script modification leverages `TIER0`/`TIER1` invariants and coupled script contracts automatically before code is written.

- **What We Will Do (`Decisions 4A, 4B & 4C` + `Points 1–2` Locked)**:
  1. **Decision `4C` (`Homunculus/scripts/script_contracts.json` + 1-Line `#L1-L55` Pointer)**: Structured contract index for all `13` scripts (`must_keep_invariants`, `retired_anti_patterns`, `coupled_functional_1hop`, `coupled_data_contracts`, `required_tests`) + 1-line `Contract :` pointer in `#L1-L55` Navigation Maps.
  2. **Decision `4B` (`Hub-Filtered 1-Hop Functional + Data-Contract Coupling`)**: Excludes universal utility hub `homunculus_paths.py` from transitive fan-out unless `homunculus_paths.py` is the target being edited.
  3. **Decision `4A` (`Unified --map / --preflight Receipt Bound to Pre-Edit Blob Hash`)**: Both `homunculus_paths.py --map <script>` and `sync_memory.py --preflight <script>` load `script_contracts.json` + radar capsules and record a preflight receipt in `.cache/preflight_state.json` bound to `(script_rel_path, pre_edit_blob_sha256, session_date)`; verified by `audit_skill_hygiene.py` (`[UNPREFLIGHTED_CORE_SCRIPT_EDIT]`).
  4. **Ultra-Fast Directory-Scoped `memory/AGENTS.md` (`<= 150` Words)**: Loaded just-in-time only when opening/editing files in `memory/`, enforcing the AI/CLI-Preferred Mutation Law, `TIER0`–`TIER5` quotas, zero whole-file dumps, and the Hallucination-Check Immunity Lock.
  5. **Net-Zero-Byte Update to `rules/co-engineering-partner.md` ([`Homunculus_Software.md`](Homunculus_Software.md))**: Keeps root `AGENTS.md` $\le 21,880 / 22,500$ B.

---

### Sprint 5: Ephemeral `sprint-auditor`, Full Sandbox `+faults` Red-Team, Future Planning Playbook & Clean-Room Parity (`LOCKED`)
**Objective**: Audit every sprint via `sprint-auditor`, run `6` unit test suites in `test_project_memory.py` ([`Homunculus_Software.md`](Homunculus_Software.md)) and `5` adversarial `+faults` injections in `sandbox_runner.py`, author [`Templates/Stateful_Sprint_Planning_Template.md`](../../Templates/Stateful_Sprint_Planning_Template.md), clean up all temporary build/audit scaffolding, and sync `/home/orin/Projects/Alchemical3D/Homunculus` at `100%` byte-for-byte parity (`101 / 101` files).
