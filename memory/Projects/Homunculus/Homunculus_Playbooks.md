---
project: "Homunculus"
entity: "Alchemical-3D"
compartment: "cleanroom"
note_type: "procedural_playbooks"
authoritative: false
last_synced: "2026-11-10"
---

# Homunculus — Procedural Engineering Playbooks (`PB-xx`)

> **Portable Procedural Memory (`entity: Alchemical-3D` | `authoritative: false`)**: Stores verified, multi-step **"How to Execute"** engineering workflows (`Trigger / Task Pattern -> Ordered Execution Steps -> Verification Gate`) for `Homunculus` and its `Alchemical-3D` ecosystem companions. Playbooks are indexed as 1-line `[PLAYBOOK]` radar capsules in `<Entity>_memory_index.json` (`0` Turn-1 token overhead) and expanded on demand via `sync_memory.py --project Homunculus --playbook-id <PB-xx>`. Quantitative hardware/software specifications must still be verified against primary repository sources via `verify_claims.py`.

---

## 1. Procedural Playbooks Ledger (`Trigger -> Ordered Procedure -> Verification Gate`)

| ID          |  Tier   | Date         | Trigger / Task Pattern                                                                     | Verification Gate                                                                                                       | Target Files / Anchor                                                                                                                                                                                                                                                                              |
| :---------- | :-----: | :----------- | :----------------------------------------------------------------------------------------- | :---------------------------------------------------------------------------------------------------------------------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `PB-HOM-01` | `TIER2` | `2026-11-10` | When extending or refactoring Homunculus core scripts (sync_memory.py, verify_claims.py... | 46/46 unit tests OK, OS Dry-Run (+faults) 100% caught, audit_portability/boundary/hygiene exit 0, and sync_memory.py... | `skills/project-memory/scripts/sync_memory.py` ([`Homunculus_Software.md`](Homunculus_Software.md)), `skills/claim-verification/scripts/verify_claims.py` ([`Homunculus_Software.md`](Homunculus_Software.md)), `scripts/homunculus_paths.py` ([`Homunculus_Software.md`](Homunculus_Software.md)) |
|             |         |              |                                                                                            |                                                                                                                         |                                                                                                                                                                                                                                                                                                    |

### `PB-HOM-01` [TIER2] — Homunculus Core Script Upgrade, Dual-Repo Clean-Room Sync & v1.1 Governance Re-Seal Sequence (`2026-11-10`)
- **Trigger / Task Pattern:** When extending or refactoring Homunculus core scripts (sync_memory.py, verify_claims.py, homunculus_paths.py), skills, or memory templates.
- **Ordered Execution Procedure:** 1. Run --preflight <script.py> and unlock core (homunculus_paths.py --unlock-core). -> 2. Implement surgical changes, sync AST maps (--sync-maps) and client adapters (--build-repo-adapters), and verify unittest suite + OS Dry-Run (+faults) sandbox. -> 3. Mirror clean-room files to Alchemical3D/Homunculus, log/reinforce lessons (--reinforce-lesson) to dispose preflight receipts, and re-seal governance (--seal-governance --user-confirmed). -> 4. Run audit_portability.py, audit_data_boundary.py, audit_skill_hygiene.py, and re-lock core (--lock-core).
- **Verification Gate:** 46/46 unit tests OK, OS Dry-Run (+faults) 100% caught, audit_portability/boundary/hygiene exit 0, and sync_memory.py --audit --verify-checkpoints exits 0 with 0444 core & governance locks active. (`skills/project-memory/scripts/sync_memory.py` ([`Homunculus_Software.md`](Homunculus_Software.md)), `skills/claim-verification/scripts/verify_claims.py` ([`Homunculus_Software.md`](Homunculus_Software.md)), `scripts/homunculus_paths.py` ([`Homunculus_Software.md`](Homunculus_Software.md))).
