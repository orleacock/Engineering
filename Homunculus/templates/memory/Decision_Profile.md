---
title: "Co-Engineering Decision & Architecture Profile"
type: "decision-profile"
tier: "TIER0"
compartment: "private"
last_synced: "{{DATE}}"
---

# 🧭 Co-Engineering Decision & Architecture Profile (`TIER0` Foundational Gravity)

> **Purpose (`<= 60` Lines — `0%` Decay)**: Compact, cross-project record of locked engineering trade-off preferences, parent-vs-product boundaries, and communication cadence between the Engineer and AI Co-Engineer. Loaded into `<MEMORY_DECISION_PACKET>` during `--recall` and `--preflight`.

---

## 1. Governing Priority Hierarchy (`Immutable`)
1. **Accuracy & Truth (`#1`)**: Source-verified facts, dimensional math, and structural integrity supersede all else. Never trade truth or disable `verify_claims.py` for speed.
2. **Token & Turn Efficiency (`#2`)**: Eliminate wasted reads, blind directory scans, and mid-task churn via targeted front-of-decision radar capsules (`<= 450` tokens) and deferred `pre-commit-gate` batching.
3. **Data Safety (`#3`)**: Enforce compartment boundaries (`audit_data_boundary.py`), zero credential exposure, and strict `entity:` isolation.
4. **Execution Speed (`#4`)**: Achieve speed through first-pass accuracy, deterministic CLI oracles, and fast `Model: 'flash'` subagents.

---

## 2. Workstation vs. Clean-Room Deliverable Doctrine
- **Active Workstation**: Absolute `local_path` bindings and local station indexes (`Directory/<Entity>_memory_index.json`) are first-class citizens inside `<memory_root>/`. Re-anchor across stations via `sync_memory.py --rebind-station <new_root>`.
- **Published / Clean-Room Repositories**: Enforced via `audit_data_boundary.py` and `audit_portability.py` (`0` workstation paths or cross-entity leaks).

---

## 3. Co-Engineering Workflow & Memory Governance Preferences
- **Sprint-by-Sprint Alignment**: Lock design questions and trade-offs before executing each sprint; verify against the persisted Deployment Plan so development never drifts.
- **`TIER0`–`TIER5` Memory Gravity**: Organize lessons by importance (`TIER0` pinned laws/repeat offenders $\rightarrow$ `TIER1` subsystem invariants $\rightarrow$ `TIER2` active dev-cycle full-context window $\le 7$ $\rightarrow$ `TIER3` stabilized archive $\rightarrow$ `TIER4` isolated polish $\rightarrow$ `TIER5` retired history).
- **AI/CLI-Preferred Memory Edits**: Mutate memory via `sync_memory.py` (`--add-lesson`, `--set-tier`, `--compact-memory`, `--save-handoff`). Detect manual hand-edits (`[MANUAL_MEMORY_EDIT_DETECTED]`), explain structural impact to the user, and repair cooperatively (`--repair-memory`).
