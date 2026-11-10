---
title: "Stateful Multi-Sprint Architecture & Alignment Playbook Template"
type: "deliverable-template"
entity: "{{ENTITY}}"
compartment: "{{COMPARTMENT}}"
last_synced: "{{DATE}}"
---

# 📐 Stateful Multi-Sprint Architecture & Alignment Playbook: `{{PROJECT}}`

> **Purpose**: Reusable planning & execution blueprint derived from the `Homunculus` Stateful Memory Rebuild (`Sprints 1–5`). Use this template whenever designing a multi-sprint engineering upgrade so `1. Accuracy & Truth > 2. Efficiency > 3. Data Safety > 4. Speed` holds across every sprint without context drift or post-deployment circles.

---

## 1. Parent System vs. Shipped Deliverable Boundary Check

| Dimension | Parent Engineering Station (`Private Vault`) | Shipped / Clean-Room Deliverable (`Public / Client`) |
| :--- | :--- | :--- |
| **Absolute Paths & Station Indexes** | Allowed & encouraged (`local_path`, `Directory/<Entity>_memory_index.json`) | Stripped via `audit_data_boundary.py` / `audit_portability.py` |
| **Memory Tier Promotion Scope** | Full `TIER0`–`TIER5` Project History & Archive | Only `TIER0` & `TIER1` engine-universal invariants (`script_contracts.json`, `#L1-L55` maps, tests) |
| **Detached / Cloud Fallback** | Stage 1 (`DIRECT_STATION`) / Stage 2 (`REANCHORED_WORKSPACE`) | Stage 3 (`DETACHED_CACHE`) — preserves cached telemetry without corrupting hashes |

---

## 2. Pre-Execution Invariant & Coupling Preflight (`Sprint 0`)

Before drafting code changes for any subsystem or script:
1. Run `python3 scripts/homunculus_paths.py --map <script.py>` (or `sync_memory.py --project {{PROJECT}} --preflight <script.py>`) to inspect:
   - `must_keep_invariants` & `retired_anti_patterns` from `scripts/script_contracts.json`
   - Hub-filtered `1-Hop Functional + Shared Data-Contract Coupling`
   - Top-3 `1-Line Radar Capsules` from `<Entity>_memory_index.json`
2. Persist the locked plan in `Projects/{{PROJECT}}/{{PROJECT}}_<Feature>_Deployment_Plan.md` and link it in `Projects/{{PROJECT}}/{{PROJECT}}.md` (`Section 2`).

---

## 3. Sprint-by-Sprint Execution & Discussion Protocol

Repeat the following structure for each Sprint (`Sprint 1 .. Sprint N`):

### Sprint `N`: `<Sprint Title>` (`[PENDING | LOCKED | VERIFIED]`)
- **Objective**: `<1-sentence measurable engineering outcome>`
- **Target Files & Contracts**:
  - `[file.py](relative/path/to/file.py)` — `<exact functions/schemas touched>`
- **Discussion & Alignment Questions Locked Before Execution**:
  - **Issue `NA`**: `<Trade-off question -> User/Co-Engineer locked resolution>`
  - **Issue `NB`**: `<Empirical test result -> Pillar-aligned choice>`
- **In-Flight & Post-Deployment Audit Gate (`sprint-auditor`)**:
  - Deterministic CLI verification command(s) + unit test receipt (`PASS`)
  - Ephemeral `sprint-auditor` check against the Deployment Plan (`0` drift)

---

## 4. End-of-Campaign Teardown & Clean-Room Parity Checklist

- [ ] Terminate temporary session subagents (`manage_subagents Action: "kill_all"`) and remove `scratch/` scripts.
- [ ] Run `test_*.py` + `sandbox_runner.py --mode dry-run --faults`.
- [ ] Capture lessons learned (`sync_memory.py --project {{PROJECT}} --add-lesson ... --tier TIER2`) and compact if `TIER2 > 7` (`--compact-memory`).
- [ ] Run `pre-commit-gate` (`Stage X -> Stage Y -> Stage Z`) and verify `100%` clean-room parity where applicable.
