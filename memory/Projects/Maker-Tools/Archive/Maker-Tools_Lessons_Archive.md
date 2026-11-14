---
project: "Maker-Tools"
parent_note: "Maker-Tools_Lessons_Learned"
entity: "Alchemical-3D"
compartment: "public"
note_type: "lessons_archive"
authoritative: false
last_synced: "2026-11-13"
---

# 🗄️ Maker-Tools — Graduated & Historical Lessons Archive (`TIER3`–`TIER5`)

> **Single-Source Tiered Archive**: Companion to [`Maker-Tools_Lessons_Learned.md`](../Maker-Tools_Lessons_Learned.md). Stores full-context narratives for stabilized `TIER3`, isolated-polish `TIER4`, and retired `TIER5` lessons so the active `<Project>_Lessons_Learned.md` window stays compact (`<= 3 TIER0 + <= 7 TIER2` sections). Query any entry on demand via `sync_memory.py --project Maker-Tools --lesson-id <LL-xxx>` or promote back to active memory via `--set-tier <LL-xxx> TIER2`.

---

## 1. Archived Full-Context Post-Mortems (`TIER3`–`TIER5`)

### `LL-MT-02` [TIER3] — Separating Reusable Bench Tooling (`Tools_and_Hardware.md`) from Project COTS BOMs (`2026-11-05`)
- **Symptom / Trap:** Individual hardware repository BOMs became cluttered with generic shop tools (soldering irons, hex drivers, reamers, threadlockers).
- **Root Cause:** No separation between build-consumed COTS fasteners/electronics and reusable bench tooling.
- **Verified Resolution & Permanent Guardrail:** Extracted all bench tooling and consumables into `Tools_and_Hardware.md` (`282` verified claims across `Maker-Tools`, `VRF-076c174de9c5`; [`Maker-Tools.md`](../Maker-Tools.md)).

---
