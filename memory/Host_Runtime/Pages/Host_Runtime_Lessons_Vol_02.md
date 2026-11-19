---
title: "Workstation Host & Local-Model Runtime Shelf"
parent_note: "Host_Runtime_Lessons"
entity: "shared"
compartment: "private"
note_type: "host_runtime_lessons"
authoritative: false
volume: 2
last_synced: "2026-11-18"
---
# Host_Runtime Shelf — Volume 02

> **Paginated Continuation of [`Host_Runtime_Lessons.md`](../Host_Runtime_Lessons.md)**: Overflow book page (`<= 22 KB` / `<= 12` entries per page).

---

## 2. Active Host & Local-Model Runtime Entries (`TIER0` & `TIER2`)

### `LL-WS-27` [TIER2] [TRAP] — Phase 3 STANDARD/HIGH suites exposed four failure modes: _deduplicate_full_context_diff emitted synthetic... (`2026-11-18`)
- **Subsystem-Domain:** `script:apprentice` (cross-project workstation host runtime)
- **Migrated-From:** `Workstation_Operations` (prefix `LL-WS` preserved)
- **Symptom / Trap:** Phase 3 STANDARD/HIGH suites exposed four failure modes: _deduplicate_full_context_diff emitted synthetic +[see verbatim Guide.md#L3-L3 above] hunks that Qwen3.6 treated as broken working-tree edits in shadow_review (clean_arm [TBD] alarm and trap_arm VRF=False); literal <file>#L<start>-L<end> prompt hints caused HIGH to emit <Assembly_Guide.md>#L4 angle brackets; _run_smoke_test lacked repo PYTHONPATH for #L local API scripts and estimate_eta underpredicted greenfield stage_patch; STANDARD gave 100% up to 24.3 KB value tables (S8C 21.5s) but false-flagged negated safety rules (S8E), while >45 KB tables/parsers degraded (H1 6/10, H2 83.3%, H4 75%).
- **Root Cause:** assemble_prompt_payload applied --unified=0 diff deduplication unconditionally even during diff critique (shadow_review); prompt templates used <file> angle-bracket placeholders; _run_smoke_test omitted repo_root/scripts/context parent dirs from PYTHONPATH; and STANDARD non-thinking misses semantic negation whereas Map-Reduce max ~24 rows per slice and dense >45 KB prompts clip cross-file facts.
- **Verified Resolution & Permanent Guardrail:** Pass compact_git_diff=False in _apprentice_shadow_review_sync so shadow critics inspect raw '+' diff hunks (H5 3/3 traps, VRF=True, -67% clean latency); replace <file>#L<start>-L<end> prompt syntax with unbracketed file.ext#Lstart-Lend and flag _ANGLED_FILE_ANCHOR_RE deterministically (H3 100% first-pass clean); prepend repo/scripts/context dirs to _run_smoke_test PYTHONPATH (S6 11.7s first-pass clean) and calibrate greenfield/retry stage_patch ETA; keep HIGH on semantic/safety audits and escalate >=45 KB dense audits or edge-case parsers to Frontier. (`apprentice_engine.py` ([`Workstation_Operations_Software.md`](../../Projects/Workstation_Operations/Workstation_Operations_Software.md)), `apprentice/apprentice_mcp_server.py` ([`Workstation_Operations_Software.md`](../../Projects/Workstation_Operations/Workstation_Operations_Software.md)), `benchmark_apprentice_standard.py` ([`Workstation_Operations_Software.md`](../../Projects/Workstation_Operations/Workstation_Operations_Software.md)), `benchmark_apprentice_high.py` ([`Workstation_Operations_Software.md`](../../Projects/Workstation_Operations/Workstation_Operations_Software.md)) (`SBX-20261118_173005-8630c735`)).

---
