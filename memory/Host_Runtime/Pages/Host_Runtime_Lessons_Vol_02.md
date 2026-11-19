---
title: "Workstation Host & Local-Model Runtime Shelf"
parent_note: "Host_Runtime_Lessons"
entity: "shared"
compartment: "private"
note_type: "host_runtime_lessons"
authoritative: false
volume: 2
last_synced: "2026-11-19"
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

### `LL-WS-28` [TIER2] [TRAP] — Same-basename SKILL.md citations triggered false out-of-bounds anchor errors (BC-0290), chunked 8-batch... (`2026-11-18`)
- **Subsystem-Domain:** `script:apprentice` (cross-project workstation host runtime)
- **Migrated-From:** `Workstation_Operations` (prefix `LL-WS` preserved)
- **Symptom / Trap:** Same-basename SKILL.md citations triggered false out-of-bounds anchor errors (BC-0290), chunked 8-batch HIGH ETAs underpredicted single-GPU throughput (BC-0291), and Apprentice preflight --map calls were blocked by SIDECAR_SCRIPT_RE.
- **Root Cause:** _detect_citation_format_defects and _run_cpu_truth_oracles resolved files by basename instead of POSIX path suffixes, surgical repair lacked working_tree_delta.patch fallback, estimate_chunked_eta assumed 0.5x wave halving on 2-slot single GPU, and GOVERNED_PY_SCRIPTS excluded Homunculus scripts.
- **Verified Resolution & Permanent Guardrail:** Match trailing POSIX path suffixes in citation bounds and emit repo-relative targets; fall back to working_tree_delta.patch and min_lines=1 during single-file shadow repair (BC-0292 100% healed, H5 3/3 Pass-1 clean); recalibrate estimate_chunked_eta to ~0.90x parallel GPU model; expand GOVERNED_PY_SCRIPTS. (`apprentice_engine.py` ([`Workstation_Operations_Software.md`](../../Projects/Workstation_Operations/Workstation_Operations_Software.md)), `apprentice/apprentice_mcp_server.py` ([`Workstation_Operations_Software.md`](../../Projects/Workstation_Operations/Workstation_Operations_Software.md)), `apprentice/apprentice_lifecycle_hook.py` ([`Workstation_Operations_Software.md`](../../Projects/Workstation_Operations/Workstation_Operations_Software.md)), `benchmark_apprentice_high.py` ([`Workstation_Operations_Software.md`](../../Projects/Workstation_Operations/Workstation_Operations_Software.md)) (`SBX-20261118_205811-ca257d09 | BC-0292 | H5`)).

---

### `LL-WS-29` [TIER2] [TRAP] — FRONTIER_MODEL_RE omitted neon, leaving Neon hosts in neutral fallback or stuck on stale prior tiers... (`2026-11-19`)
- **Subsystem-Domain:** `script:apprentice` (cross-project workstation host runtime)
- **Migrated-From:** `Workstation_Operations` (prefix `LL-WS` preserved)
- **Symptom / Trap:** FRONTIER_MODEL_RE omitted neon, leaving Neon hosts in neutral fallback or stuck on stale prior tiers during mid-session Model Selection switches
- **Root Cause:** Model regexes predated Gemini 4 Neon, while classify_host_model_tier skipped non-placeholder neutral Model Selection transitions in transcriptPath to protect against tool JSON model keys
- **Verified Resolution & Permanent Guardrail:** Classify neon under FRONTIER_MODEL_RE (retaining argon as silent legacy regex alias), reset eff_tier on explicit non-placeholder Model Selection or concrete modelName changes while isolating tool JSON model keys, replace Argon with Neon in plugin docs, and verify via SBX-20261119_070028-c284d2b2 (`apprentice/apprentice_lifecycle_hook.py` ([`Workstation_Operations_Software.md`](../../Projects/Workstation_Operations/Workstation_Operations_Software.md)), `apprentice_plugin/rules/AGENTS.md` ([`Workstation_Operations.md`](../../Projects/Workstation_Operations/Workstation_Operations.md)), `apprentice_plugin/skills/apprentice/SKILL.md` ([`Workstation_Operations.md`](../../Projects/Workstation_Operations/Workstation_Operations.md)) (`SBX-20261119_070028-c284d2b2`)).

---

### `LL-WS-30` [TIER2] [TRAP] — Chunk mappers emitted Markdown pipe-row NONE or absent noise on empty slices, echoed bracketed start/end... (`2026-11-19`)
- **Subsystem-Domain:** `script:apprentice` (cross-project workstation host runtime)
- **Migrated-From:** `Workstation_Operations` (prefix `LL-WS` preserved)
- **Symptom / Trap:** Chunk mappers emitted Markdown pipe-row NONE or absent noise on empty slices, echoed bracketed start/end placeholders in Map prompts, and cross-attributed adjacent metric fields across sibling keys.
- **Root Cause:** _filter_chunk_extract_lines only stripped standalone NONE lines rather than pipe-table NONE/absent cells, and Map slice prompts still carried angle-bracket placeholders and lacked strict enclosing-key binding.
- **Verified Resolution & Permanent Guardrail:** Filter pipe-row NONE and absent from L-lines in _filter_chunk_extract_lines(), replace angle-bracket placeholders with unbracketed file.ext#Lstart-Lend in Map prompts, and enforce strict enclosing key/metric_id/heading binding across Map and Reduce passes. (`apprentice/apprentice_mcp_server.py` ([`Workstation_Operations_Software.md`](../../Projects/Workstation_Operations/Workstation_Operations_Software.md)) (`31/31 self-test PASS`)).

---
