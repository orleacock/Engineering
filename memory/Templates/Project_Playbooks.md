---
project: "{{PROJECT}}"
entity: "{{ENTITY}}"
compartment: "{{COMPARTMENT}}"
note_type: "procedural_playbooks"
authoritative: false
last_synced: "{{DATE}}"
---

# {{PROJECT}} — Procedural Engineering Playbooks (`PB-xx`)

> **Portable Procedural Memory (`entity: {{ENTITY}}` | `authoritative: false`)**: Stores verified, multi-step **"How to Execute"** engineering workflows (`Trigger / Task Pattern -> Ordered Execution Steps -> Verification Gate`) for `{{PROJECT}}` and its `{{ENTITY}}` ecosystem companions. Playbooks are indexed as 1-line `[PLAYBOOK]` radar capsules in `<Entity>_memory_index.json` (`0` Turn-1 token overhead) and expanded on demand via `sync_memory.py --project {{PROJECT}} --playbook-id <PB-xx>`. Quantitative hardware/software specifications must still be verified against primary repository sources via `verify_claims.py`.

---

## 1. Procedural Playbooks Ledger (`Trigger -> Ordered Procedure -> Verification Gate`)

| ID | Tier | Date | Trigger / Task Pattern | Verification Gate | Target Files / Anchor |
| :--- | :---: | :--- | :--- | :--- | :--- |
