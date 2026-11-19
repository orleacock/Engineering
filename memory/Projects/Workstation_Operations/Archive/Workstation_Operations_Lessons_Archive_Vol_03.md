---
project: "Workstation_Operations"
parent_note: "Workstation_Operations_Lessons_Learned"
entity: "Orin_Workstation"
compartment: "private"
note_type: "lessons_archive"
authoritative: false
volume: 3
last_synced: "2026-11-19"
---
# Workstation_Operations — Archive — Volume 03

> **Paginated Continuation of [`Workstation_Operations_Lessons_Archive.md`](Workstation_Operations_Lessons_Archive.md)**

---

## 1. Archived Full-Context Post-Mortems (`TIER3`–`TIER5`)

### `LL-WS-29` [TIER5] [TRAP] — FRONTIER_MODEL_RE omitted neon, leaving Neon hosts in neutral fallback or stuck on stale prior tiers... (`2026-11-19`)
- **Retirement Provenance (`TIER5` — `2026-11-19`):** Archived to TIER5 after retiring legacy workstation v2.6 lifecycle hook to RAID (v2.6.1_2026-11-19_pre_v3_cutover); superseded by universal model-agnostic routing (PRIN-08).
- **Subsystem-Domain:** `script:apprentice` (cross-project workstation host runtime)
- **Migrated-From:** `Workstation_Operations` (prefix `LL-WS` preserved)
- **Symptom / Trap:** FRONTIER_MODEL_RE omitted neon, leaving Neon hosts in neutral fallback or stuck on stale prior tiers during mid-session Model Selection switches
- **Root Cause:** Model regexes predated Gemini 4 Neon, while classify_host_model_tier skipped non-placeholder neutral Model Selection transitions in transcriptPath to protect against tool JSON model keys
- **Verified Resolution & Permanent Guardrail:** Classify neon under FRONTIER_MODEL_RE (retaining argon as silent legacy regex alias), reset eff_tier on explicit non-placeholder Model Selection or concrete modelName changes while isolating tool JSON model keys, replace Argon with Neon in plugin docs, and verify via SBX-20261119_070028-c284d2b2 (`apprentice/apprentice_lifecycle_hook.py` ([`Workstation_Operations_Software.md`](../Workstation_Operations_Software.md)), `apprentice_plugin/rules/AGENTS.md` ([`Workstation_Operations.md`](../Workstation_Operations.md)), `apprentice_plugin/skills/apprentice/SKILL.md` ([`Workstation_Operations.md`](../Workstation_Operations.md)) (`SBX-20261119_070028-c284d2b2`)).

---

### `LL-WS-30` [TIER5] [TRAP] — Chunk mappers emitted Markdown pipe-row NONE or absent noise on empty slices, echoed bracketed start/end... (`2026-11-19`)
- **Retirement Provenance (`TIER5` — `2026-11-19`):** Archived to TIER5 after retiring legacy workstation v2.6 chunk mapper to RAID (v2.6.1_2026-11-19_pre_v3_cutover); superseded by structured JSON extraction with <1ms deterministic line/quote verification.
- **Subsystem-Domain:** `script:apprentice` (cross-project workstation host runtime)
- **Migrated-From:** `Workstation_Operations` (prefix `LL-WS` preserved)
- **Symptom / Trap:** Chunk mappers emitted Markdown pipe-row NONE or absent noise on empty slices, echoed bracketed start/end placeholders in Map prompts, and cross-attributed adjacent metric fields across sibling keys.
- **Root Cause:** _filter_chunk_extract_lines only stripped standalone NONE lines rather than pipe-table NONE/absent cells, and Map slice prompts still carried angle-bracket placeholders and lacked strict enclosing-key binding.
- **Verified Resolution & Permanent Guardrail:** Filter pipe-row NONE and absent from L-lines in _filter_chunk_extract_lines(), replace angle-bracket placeholders with unbracketed file.ext#Lstart-Lend in Map prompts, and enforce strict enclosing key/metric_id/heading binding across Map and Reduce passes. (`apprentice/apprentice_mcp_server.py` ([`Workstation_Operations_Software.md`](../Workstation_Operations_Software.md)) (`31/31 self-test PASS`)).

---
