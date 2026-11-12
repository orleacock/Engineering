---
title: "Orin_Workstation — Zero-CLI Front-of-Decision Memory Router"
entity: "Orin_Workstation"
compartment: "private"
type: "decision-router"
authoritative: false
last_synced: "2026-11-11"
---

# 🧭 `Orin_Workstation` — Front-of-Decision Memory Router (`TIER0`–`TIER4`)

> **Zero-CLI & Turn-1 Decision Radar**: Maintained automatically by `sync_memory.py`. Lists `TIER0` pinned laws, `TIER1` subsystem invariants, and `1-Line Radar Capsules` for `Orin_Workstation` projects. Use `sync_memory.py --project <P> --recall "<query>"` in CLI sessions or scan this table directly in Zero-CLI web sessions.

---

## 1. `TIER0` Co-Engineering Decision Profile

1. **Accuracy & Truth (`#1`)**: Source-verified facts, dimensional math, and structural integrity supersede all else. Never trade truth or disable `verify_claims.py` for speed.
2. **Token & Turn Efficiency (`#2`)**: Eliminate wasted reads, blind directory scans, and mid-task churn via targeted front-of-decision radar capsules (`<= 450` tokens) and deferred `pre-commit-gate` batching.
3. **Data Safety (`#3`)**: Enforce compartment boundaries (`audit_data_boundary.py`), zero credential exposure, and strict `entity:` isolation.
4. **Execution Speed (`#4`)**: Achieve speed through first-pass accuracy, deterministic CLI oracles, and fast `Model: 'flash'` subagents.
- **Parent Workstation & Post-Install User Stations**: Absolute `local_path` bindings and local station indexes (`Directory/<Entity>_memory_index.json`) are first-class citizens. Never waste local turns scrubbing workstation paths from the private parent memory vault.
- **Shipped Clean-Room Deliverable (`Homunculus`)**: Must ship 100% generic (`0` parent paths, project names, or `LL-xxx` IDs). Only `TIER0` & `TIER1` engine-universal invariants (`scripts/script_contracts.json`, `#L1-L55` `Contract :` pointers, and `tests/test_*.py`) promote from the parent vault into the clean-room deliverable.

---

## 2. Project Lesson Radar Capsules (`TIER0`–`TIER4`)

### [`Workstation_Operations`](../Projects/Workstation_Operations/Workstation_Operations.md)

| ID | Tier | Location | Touched Files | 1-Line Radar Capsule |
| :--- | :---: | :--- | :--- | :--- |
| **`LL-WS-01`** | `TIER2` | [`Workstation_Operations_Lessons_Learned.md#L43-L46`](../Projects/Workstation_Operations/Workstation_Operations_Lessons_Learned.md#L43-L46) | `audit_data_boundary.py`, `git_pre_commit_boundary.sh` | Directory-Scoped Git `[includeIf]` Identities & SSH Alias Locks -> Configured directory-scoped `[includeIf]` rules in `~/.gitconfig`, dedicated SSH aliases (`github-orleacock`, `github-alchemical`), and `audit_data_boundary.py` remote/email locks in `git_pre_commit_boundary.sh` (`Workstation_Operations.md`). |
| **`LL-WS-02`** | `TIER2` | [`Workstation_Operations_Lessons_Learned.md#L48-L51`](../Projects/Workstation_Operations/Workstation_Operations_Lessons_Learned.md#L48-L51) | `Projects.homunculus.json`, `bootstrap_workstation.sh` | Parent `/home/orin/Projects` Umbrella `.homunculus.json` Sync -> Added `umbrella_configs/Projects.homunculus.json` and wired `bootstrap_workstation.sh` to sync `/home/orin/Projects/{.homunculus.json,.geminiignore}` (`Workstation_Operations_Software.md`). |
| **`LL-WS-03`** | `TIER2` | [`Workstation_Operations_Lessons_Learned.md#L53-L56`](../Projects/Workstation_Operations/Workstation_Operations_Lessons_Learned.md#L53-L56) | `SKILL.md`, `gmail_mcp_server.py` | Gmail MCP `visibility_radar` for Non-Visible Unread Threads -> Built `visibility_radar` into `gmail_mcp_server.py` and `gmail-workspace-assistant/SKILL.md` to surface non-visible unread threads alongside inbox triage (`Workstation_Operations_Software.md`). |
| **`LL-WS-04`** | `TIER2` | [`Workstation_Operations_Lessons_Learned.md#L58-L61`](../Projects/Workstation_Operations/Workstation_Operations_Lessons_Learned.md#L58-L61) | `SKILL.md`, `audit_skill_hygiene.py`, `git_pre_commit_boundary.sh` | Pre-Commit AST/CLI & Maintainer Matrix Parity Gate -> Wired `audit_skill_hygiene.py`, `sync_memory.py --audit`, and AST/CLI parity checks into `git_pre_commit_boundary.sh` (`SBX-20261107_091652-1f171c12`; `Workstation_Operations.md`). |
| **`LL-WS-05`** | `TIER2` | [`Workstation_Operations_Lessons_Learned.md#L63-L66`](../Projects/Workstation_Operations/Workstation_Operations_Lessons_Learned.md#L63-L66) | `bootstrap_workstation.sh` | Provisioning Optional `Homunculus/addons/*` Symlinks in `bootstrap_workstation.sh` -> Updated workstation skill symlink provisioning to link enabled drop-in add-ons from `Homunculus/addons/*` alongside core `Homunculus/skills/*` (`Workstation_Operations.md`). |
| **`LL-WS-06`** | `TIER2` | [`Workstation_Operations_Lessons_Learned.md#L68-L73`](../Projects/Workstation_Operations/Workstation_Operations_Lessons_Learned.md#L68-L73) | `bootstrap_workstation.sh` | Symlink-Blind `find` in `~/.gemini/config/skills/` vs. Direct `<skills>` Path Derivation -> Documented symlink structure in `Workstation_Operations` and banned `find` in favor of direct `<skill_dir>/scripts/<script>.py` path derivation from `<skills>` (`Workstation_Operations.md`). |
| **`LL-WS-07`** | `TIER2` | [`Workstation_Operations_Lessons_Learned.md#L75-L80`](../Projects/Workstation_Operations/Workstation_Operations_Lessons_Learned.md#L75-L80) | `snapshot_homunculus_version.py` | Dual Homunculus copies risked split-brain authority; benchmark REGRESSION_ADVISORY exit 2 collided with... -> Consolidated /home/orin/Projects/Alchemical3D/Homunculus as the sole local/remote repo (/Homunculus/ gitignored in Engineering), assigned exit 4 to REGRESSION_ADVISORY (exit 1 Hard Block, exit 0 PASS), and locked RAID deliverables 0444/0555 via snapshot_homunculus_version.py (SBX-20261110_115958-408697dc)... |
| **`LL-WS-08`** | `TIER2` | [`Workstation_Operations_Lessons_Learned.md#L82-L87`](../Projects/Workstation_Operations/Workstation_Operations_Lessons_Learned.md#L82-L87) | `benchmark_homunculus.py`, `snapshot_homunculus_version.py`, `version_manager.py` | restore_version.sh risked overwriting live mcp_config.json credentials and wiping custom ~/.gemini/config... -> Hardened restore_version.sh with HOMUNCULUS_RESTORE_HOME_OVERRIDE, mcp_config.redacted_reference.json (0600), and surgical symlink pruning; deduplicated full-system-suite unit-test execution + cryptographic (HEAD, tree_hash) benchmark receipt reuse; added same-device Btrfs --reflink=always RAID seeding with SHA-256 reconciliation... |
| **`LL-WS-09`** | `TIER2` | [`Workstation_Operations_Lessons_Learned.md#L89-L92`](../Projects/Workstation_Operations/Workstation_Operations_Lessons_Learned.md#L89-L92) | `bootstrap_workstation.sh`, `git_pre_commit_boundary.sh`, `pre_push_engineering_guard.sh` | Retired parent workstation surfaces (.agents duplicate symlink trees, unused find-skills skill... -> Pruned Engineering/.agents and ~/.agents (including find-skills), removed --compat-symlinks and legacy Engineering/Homunculus probes, upgraded bootstrap_workstation.sh --check to enforce cmp byte parity on copied Alchemical3D git hooks, restored cross-repo AST matrix parity checks, and pruned duplicate memory Templates to sparse... |
| **`PB-WS-01`** | `TIER2` | [`Workstation_Operations_Playbooks.md#L22-L25`](../Projects/Workstation_Operations/Workstation_Operations_Playbooks.md#L22-L25) | `audit_data_boundary.py`, `audit_portability.py`, `benchmark_homunculus.py` | [PLAYBOOK] Homunculus Release Benchmark, Version Bump & Immutable RAID Deliverable -> 1. Run pre-commit-gate Stage X/Y/Z (homunculus_paths.py --sync-maps, sync_memory.py --sync-software, audit_portability.py, audit_data_boundary.py --worktree, sync_memory.py --audit --verify-checkpoints, --lock-core, --lock-memory-rules) and benchmark_homunculus.py --profile full-system-suite. 2. Commit clean worktrees locally and run... |
