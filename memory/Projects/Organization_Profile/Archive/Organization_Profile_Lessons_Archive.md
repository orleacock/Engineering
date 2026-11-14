---
project: "Organization_Profile"
parent_note: "Organization_Profile_Lessons_Learned"
entity: "Alchemical-3D"
compartment: "public"
note_type: "lessons_archive"
authoritative: false
last_synced: "2026-11-13"
---

# 🗄️ Organization_Profile — Graduated & Historical Lessons Archive (`TIER3`–`TIER5`)

> **Single-Source Tiered Archive**: Companion to [`Organization_Profile_Lessons_Learned.md`](../Organization_Profile_Lessons_Learned.md). Stores full-context narratives for stabilized `TIER3`, isolated-polish `TIER4`, and retired `TIER5` lessons so the active `<Project>_Lessons_Learned.md` window stays compact (`<= 3 TIER0 + <= 7 TIER2` sections). Query any entry on demand via `sync_memory.py --project Organization_Profile --lesson-id <LL-xxx>` or promote back to active memory via `--set-tier <LL-xxx> TIER2`.

---

## 1. Archived Full-Context Post-Mortems (`TIER3`–`TIER5`)

### `LL-OP-01` [TIER3] — Canonical `profile/README.md` Path inside `.github` Repository (`2026-11-05`)
- **Symptom / Trap:** GitHub organization landing pages only render when placed at the exact `profile/README.md` path inside the `.github` repository.
- **Root Cause:** Placing `README.md` only at the repository root of `.github` describes the repo itself rather than rendering on the public `https://github.com/Alchemical-3D` organization profile.
- **Verified Resolution & Permanent Guardrail:** Maintained `profile/README.md` as the single living document (`VRF-3b88c1f9d028`, `8` supported claims, `0` unbacked claims; [`Organization_Profile.md`](../Organization_Profile.md)).
