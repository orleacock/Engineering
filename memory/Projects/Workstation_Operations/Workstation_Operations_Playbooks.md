---
project: "Workstation_Operations"
entity: "Orin_Workstation"
compartment: "private"
note_type: "procedural_playbooks"
authoritative: false
last_synced: "2026-11-10"
---

# Workstation_Operations — Procedural Engineering Playbooks (`PB-xx`)

> **Portable Procedural Memory (`entity: Orin_Workstation` | `authoritative: false`)**: Stores verified, multi-step **"How to Execute"** engineering workflows (`Trigger / Task Pattern -> Ordered Execution Steps -> Verification Gate`) for `Workstation_Operations` and its `Orin_Workstation` ecosystem companions. Playbooks are indexed as 1-line `[PLAYBOOK]` radar capsules in `<Entity>_memory_index.json` (`0` Turn-1 token overhead) and expanded on demand via `sync_memory.py --project Workstation_Operations --playbook-id <PB-xx>`. Quantitative hardware/software specifications must still be verified against primary repository sources via `verify_claims.py`.

---

## 1. Procedural Playbooks Ledger (`Trigger -> Ordered Procedure -> Verification Gate`)

| ID | Tier | Date | Trigger / Task Pattern | Verification Gate | Target Files / Anchor |
| :--- | :---: | :--- | :--- | :--- | :--- |
| `PB-WS-01` | `TIER2` | `2026-11-10` | Workstation Homunculus v0.Y.Z release promotion, full-system-suite benchmark gate, and immutable 0444 RAID... | benchmark_homunculus.py verdict PASS + version_manager.py LOCKED_RELEASE_TAG + snapshot_homunculus_version.py... | `benchmark_homunculus.py` ([`Workstation_Operations_Software.md`](Workstation_Operations_Software.md)), `version_manager.py` ([`Workstation_Operations_Software.md`](Workstation_Operations_Software.md)), `snapshot_homunculus_version.py` ([`Workstation_Operations_Software.md`](Workstation_Operations_Software.md)) |

### `PB-WS-01` [TIER2] — Homunculus Release Benchmark, Version Bump & Immutable RAID Deliverable (`2026-11-10`)
- **Trigger / Task Pattern:** Workstation Homunculus v0.Y.Z release promotion, full-system-suite benchmark gate, and immutable 0444 RAID deliverable cut
- **Ordered Execution Procedure:** 1. Run pre-commit-gate Stage X/Y/Z (homunculus_paths.py --sync-maps, sync_memory.py --sync-software, audit_portability.py, audit_data_boundary.py --worktree, sync_memory.py --audit --verify-checkpoints, --lock-core, --lock-memory-rules) and benchmark_homunculus.py --profile full-system-suite. 2. Commit clean worktrees locally and run version_manager.py --bump minor\|patch --reason "...". 3. Cut a single write-once 0444/0555 RAID deliverable via snapshot_homunculus_version.py --label <milestone> (never mutate prior locked RAID snapshots in place; hold remote git push until explicit user confirmation).
- **Verification Gate:** benchmark_homunculus.py verdict PASS + version_manager.py LOCKED_RELEASE_TAG + snapshot_homunculus_version.py SHA256SUMS.txt PASS (`benchmark_homunculus.py` ([`Workstation_Operations_Software.md`](Workstation_Operations_Software.md)), `version_manager.py` ([`Workstation_Operations_Software.md`](Workstation_Operations_Software.md)), `snapshot_homunculus_version.py` ([`Workstation_Operations_Software.md`](Workstation_Operations_Software.md))).
