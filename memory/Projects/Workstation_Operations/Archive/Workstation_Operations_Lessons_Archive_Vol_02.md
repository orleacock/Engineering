---
project: "Workstation_Operations"
parent_note: "Workstation_Operations_Lessons_Learned"
entity: "Orin_Workstation"
compartment: "private"
note_type: "lessons_archive"
authoritative: false
volume: 2
last_synced: "2026-11-18"
---
# Workstation_Operations — Archive — Volume 02

> **Paginated Continuation of [`Workstation_Operations_Lessons_Archive.md`](Workstation_Operations_Lessons_Archive.md)**

---

## 1. Archived Full-Context Post-Mortems (`TIER3`–`TIER5`)

### `LL-WS-19` [TIER5] — Blindly raising max_slices_per_batch=6 on dense Python silently dropped BASE_GUARD (base_covered=false)... (`2026-11-16`)
- **Retirement Provenance (`TIER5` — `2026-11-16`):** Consolidated into LL-WS-20 & LL-WS-21 under multi-backend Apprentice plugin; original Bionic/local_sidecar lessons retained in Archive/ at 0.0x recall weight for historical reference.
- **Scope:** `script:bionic_sidecar`
- **Symptom / Trap:** Blindly raising max_slices_per_batch=6 on dense Python silently dropped BASE_GUARD (base_covered=false) while Priority-Cap=10 dropped 8/18 (44.4%) markers; small multi-file #L digests (<36 KB) bypassed chunking into ~190-326s monolithic HIGH calls, and stage_patch Pass-2 deep retries burned ~97s without schema context.
- **Root Cause:** Byte-only chunk threshold (>36KB/42KB) excluded compact >=5-slice explicit #L digests, pack_chunk_batches >4 files crowded multi-module sweeps, and stage_patch Pass-2 used mode=effective_mode without validated_files context.
- **Verified Resolution & Permanent Guardrail:** Keep max_slices_per_batch=4; trigger Slice-Count Map-Reduce cleanly for >=5 explicit #L slices across >=3 files in bionic_mcp_server.py (100% 18/18 recall); switch stage_patch Pass-2 repair to fast mode with prioritized <=20KB #L context + AST sleep antipattern check; inject non-sleep injectable-clock .py Pass-1 staging rules; keep HTTP mock asserts on main thread. (`bionic_sidecar/bionic_mcp_server.py` ([`Workstation_Operations_Software.md`](../Workstation_Operations_Software.md)), `bionic_sidecar_plugin/rules/AGENTS.md` ([`Workstation_Operations.md`](../Workstation_Operations.md)), `bionic_sidecar_plugin/skills/bionic-local-sidecar/SKILL.md` ([`Workstation_Operations.md`](../Workstation_Operations.md)) (`SBX-20261116_115434-6a8592af / SBX-20261116_120126-ce5a5240`)).

---
