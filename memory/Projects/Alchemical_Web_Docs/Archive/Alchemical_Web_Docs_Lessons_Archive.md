---
project: "Alchemical_Web_Docs"
parent_note: "Alchemical_Web_Docs_Lessons_Learned"
entity: "Alchemical-3D"
compartment: "public"
note_type: "lessons_archive"
authoritative: false
last_synced: "2026-11-13"
---

# 🗄️ Alchemical_Web_Docs — Graduated & Historical Lessons Archive (`TIER3`–`TIER5`)

> **Single-Source Tiered Archive**: Companion to [`Alchemical_Web_Docs_Lessons_Learned.md`](../Alchemical_Web_Docs_Lessons_Learned.md). Stores full-context narratives for stabilized `TIER3`, isolated-polish `TIER4`, and retired `TIER5` lessons so the active `<Project>_Lessons_Learned.md` window stays compact (`<= 3 TIER0 + <= 7 TIER2` sections). Query any entry on demand via `sync_memory.py --project Alchemical_Web_Docs --lesson-id <LL-xxx>` or promote back to active memory via `--set-tier <LL-xxx> TIER2`.

---

## 1. Archived Full-Context Post-Mortems (`TIER3`–`TIER5`)

### `LL-AWD-02` [TIER3] — Standardized Showcase Card Framing Across Dark/Light Browser Themes (`2026-11-02`)
- **Symptom / Trap:** Showcase images (`Award.png`, `alchemical-3d_core.png`, `PestleExploded3.png`, `3dprofilefront.png`) risked inconsistent border/shadow presentation across dark/light browser themes.
- **Root Cause:** Raw unframed raster images lacked standardized corner radius and drop-shadow alpha margins.
- **Verified Resolution & Permanent Guardrail:** Verified all showcase cards via `format_image.py --inspect` (`[PASS]`) and `verify_claims.py --fail-on-tbd` (`0` unbacked claims across all `5` Markdown files; [`Alchemical_Web_Docs.md`](../Alchemical_Web_Docs.md)).

---
