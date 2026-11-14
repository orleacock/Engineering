---
project: "Pneuma_Remote_Air"
entity: "Alchemical-3D"
compartment: "public"
note_type: "procedural_playbooks"
authoritative: false
last_synced: "2026-11-13"
---

# Pneuma_Remote_Air — Procedural Engineering Playbooks (`PB-xx`)

> **Portable Procedural Memory (`entity: Alchemical-3D` | `authoritative: false`)**: Stores verified, multi-step **"How to Execute"** engineering workflows (`Trigger / Task Pattern -> Ordered Execution Steps -> Verification Gate`) for `Pneuma_Remote_Air` and its `Alchemical-3D` ecosystem companions. Playbooks are indexed as 1-line `[PLAYBOOK]` radar capsules in `<Entity>_memory_index.json` (`0` Turn-1 token overhead) and expanded on demand via `sync_memory.py --project Pneuma_Remote_Air --playbook-id <PB-xx>`. Quantitative hardware/software specifications must still be verified against primary repository sources via `verify_claims.py`.

---

## 1. Procedural Playbooks Ledger (`Trigger -> Ordered Procedure -> Verification Gate`)

| ID | Tier | Date | Trigger / Task Pattern | Verification Gate | Target Files / Anchor |
| :--- | :---: | :--- | :--- | :--- | :--- |
| `PB-ALCH-01` | `TIER2` | `2026-11-10` | When auditing, unifying, or reconciling an Alchemical-3D hardware repository across STEP/STL CAD... | verify_claims.py exits 0 (0 unbacked claims), audit_repo_docs.py and audit_data_boundary.py exit 0, and... | `README.md` ([`Pneuma_Remote_Air.md`](Pneuma_Remote_Air.md)), `BOM.md` ([`Pneuma_Remote_Air.md`](Pneuma_Remote_Air.md)), `Assembly_Guide.md` ([`Pneuma_Remote_Air.md`](Pneuma_Remote_Air.md)), `Print_Settings.md` ([`Pneuma_Remote_Air.md`](Pneuma_Remote_Air.md)) |

### `PB-ALCH-01` [TIER2] — Alchemical-3D Hardware Repository Unification, CAD/Firmware/BOM Reconciliation & Dual-Lesson Reinforcement... (`2026-11-10`)
- **Trigger / Task Pattern:** When auditing, unifying, or reconciling an Alchemical-3D hardware repository across STEP/STL CAD envelopes, Klipper .cfg pinouts, BOM tables, and Assembly Guides.
- **Ordered Execution Procedure:** 1. Read <Project>.md, <Project>_Hardware.md, <Project>_Lessons_Learned.md, and <Project>_Playbooks.md in 1 parallel turn and run --recall. -> 2. Run audit_repo_docs.py and inspect_hardware_ecosystem.py (--sync-manifest when needed) without ad-hoc CAD parsing. -> 3. Reconcile BOM/Assembly/Print_Settings prose using inline [TBD: ...] tags for unrecorded engineer intent and run verify_claims.py (<=2 passes). -> 4. Log root-cause lessons (`sync_memory.py` --add-lesson/--reinforce-lesson) or update playbooks (`sync_memory.py` --update-playbook) and run pre-commit-gate.
- **Verification Gate:** verify_claims.py exits 0 (0 unbacked claims), audit_repo_docs.py and audit_data_boundary.py exit 0, and sync_memory.py --audit passes with 0 violations. (`README.md` ([`Pneuma_Remote_Air.md`](Pneuma_Remote_Air.md)), `BOM.md` ([`Pneuma_Remote_Air.md`](Pneuma_Remote_Air.md)), `Assembly_Guide.md` ([`Pneuma_Remote_Air.md`](Pneuma_Remote_Air.md)), `Print_Settings.md` ([`Pneuma_Remote_Air.md`](Pneuma_Remote_Air.md))).
