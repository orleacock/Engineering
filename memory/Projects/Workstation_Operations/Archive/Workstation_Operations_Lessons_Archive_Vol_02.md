---
project: "Workstation_Operations"
parent_note: "Workstation_Operations_Lessons_Learned"
entity: "Orin_Workstation"
compartment: "private"
note_type: "lessons_archive"
authoritative: false
volume: 2
last_synced: "2026-11-19"
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

### `LL-WS-20` [TIER5] — Sidecar startup banners dropped silently during CLI startup, hot plugin updates broke running daemon cwd... (`2026-11-16`)
- **Retirement Provenance (`TIER5` — `2026-11-19`):** Archived to TIER5 after retiring legacy workstation v2.6 sidecar scripts to RAID (v2.6.1_2026-11-19_pre_v3_cutover); generic Antigravity hook/plugin invariants preserved in shared Host_Runtime LL-HOST-01.
- **Subsystem-Domain:** `script:apprentice` (cross-project workstation host runtime)
- **Migrated-From:** `Workstation_Operations` (prefix `LL-WS` preserved)
- **Symptom / Trap:** Sidecar startup banners dropped silently during CLI startup, hot plugin updates broke running daemon cwd subprocesses, symlinked skill invocations tripped bypass guards, concurrent deep reasoning calls thrashed host MoE bandwidth, and slow multi-file synchronous offloads timed out at transport cutoffs.
- **Root Cause:** Non-empty systemMessage.metadata inside injectSteps panicked agy while pre-prompt SessionStart notices ran before user prompts; unconditional plugin reinstalls replaced directory inodes under running MCP servers; hook script allowlists checked unresolved paths instead of resolved symlinks; dual high-effort KV slots saturated memory bandwidth; and Antigravity enforces a hard synchronous MCP transport deadline under multi-minute offloads.
- **Verified Resolution & Permanent Guardrail:** Defer Turn-1 notices to PreInvocation pure systemMessage strings because metadata maps and premature SessionStart hooks collided with agy parsing; compare plugin trees (diff -rq) before reinstalling in bootstrap_workstation.sh and guard child spawns via _safe_subprocess_cwd() because inode swaps broke live cwd subprocesses; match resolved paths (TRUSTED_INVOCATION_ROOTS) in apprentice_lifecycle_hook.py because symlinked skill dirs bypassed literal checks; serialize exclusive deep reasoning (exclusive=True, max_slots=2 fast/batches) in apprentice_engine.py because parallel high-effort streams starved host bandwidth; enforce 135s auto-async promotion (_run_mcp_with_sync_guard), explicit async_job=True, and probe_server_models() /api/v0/models confirmation gating in apprentice_mcp_server.py because sync MCP calls cannot outlive the client cutoff. (`apprentice_engine.py` ([`Workstation_Operations_Software.md`](../Workstation_Operations_Software.md)), `apprentice/apprentice_mcp_server.py` ([`Workstation_Operations_Software.md`](../Workstation_Operations_Software.md)), `apprentice/apprentice_lifecycle_hook.py` ([`Workstation_Operations_Software.md`](../Workstation_Operations_Software.md)), `bootstrap_workstation.sh` ([`Workstation_Operations_Software.md`](../Workstation_Operations_Software.md)) (`SBX-20261116_153626-c42fc7fa`)).

---

### `LL-WS-21` [TIER5] — Multi-slice #Lstart-Lend inputs silently dropped earlier hunks from the same file, byte-only chunk... (`2026-11-16`)
- **Retirement Provenance (`TIER5` — `2026-11-19`):** Archived to TIER5 after retiring legacy workstation v2.6 sidecar scripts to RAID (v2.6.1_2026-11-19_pre_v3_cutover); list-preserved slice parsing and zero-sleep test rules codified directly in standalone v3.0 engine.
- **Subsystem-Domain:** `script:apprentice` (cross-project workstation host runtime)
- **Migrated-From:** `Workstation_Operations` (prefix `LL-WS` preserved)
- **Symptom / Trap:** Multi-slice #Lstart-Lend inputs silently dropped earlier hunks from the same file, byte-only chunk thresholds skipped small dense multi-file digests, widening slice batches dropped recall coverage, patch sources and repair diagnostics clipped before fixing tail errors, and staged .py checks hung on real sleeps or unthreaded mocks.
- **Root Cause:** Mapping context specs in a path-keyed dict overwrote duplicate slices from one file; single byte thresholds ignored count density and mixed unsliced-plus-sliced payloads; max_slices_per_batch=6 exceeded attention capacity; .patch/.diff were omitted from verification sources while full JSON errors truncated early claims; and deep Pass-2 retries lacked focused schema context and clock-injection rules.
- **Verified Resolution & Permanent Guardrail:** Preserve duplicate per-file hunks via parse_and_validate_context_items() in apprentice_engine.py because path-keyed dicts collapsed multi-slice inputs; split unsliced vs sliced items, cap dense batches at max_slices_per_batch=4, and trigger Slice-Count Map-Reduce for dense multi-file slices (>=5 slices across >=3 files) in apprentice_mcp_server.py because wider batches and monolithic payloads degraded recall; keep tail-continuation outside branch-specific reduce paths; route claim repairs through _run_full_repair_with_guard() with .patch/.diff sourcing, compact _format_compact_verify_failures(), and HTML provenance banners (memory_gateway.py quarantine-note); run Pass-2 .py staging repairs in fast mode with focused #L context, AST sleep checks, injectable clock rules, and audit_repo_docs.py + verify_claims.py collision-free gating. (`apprentice_engine.py` ([`Workstation_Operations_Software.md`](../Workstation_Operations_Software.md)), `apprentice/apprentice_mcp_server.py` ([`Workstation_Operations_Software.md`](../Workstation_Operations_Software.md)) (`SBX-20261116_153626-c42fc7fa`)).

---

### `LL-WS-22` [TIER5] — Concurrent BJOB HIGH workers caused GPU KV-pool deadlocks, >100KB files hit chunk-reduce timeouts with... (`2026-11-16`)
- **Retirement Provenance (`TIER5` — `2026-11-19`):** Archived to TIER5 after retiring legacy workstation v2.6 BJOB scripts to RAID (v2.6.1_2026-11-19_pre_v3_cutover); superseded by slot-governed in-process SprintManager in standalone v3.0.
- **Subsystem-Domain:** `script:apprentice` (cross-project workstation host runtime)
- **Migrated-From:** `Workstation_Operations` (prefix `LL-WS` preserved)
- **Symptom / Trap:** Concurrent BJOB HIGH workers caused GPU KV-pool deadlocks, >100KB files hit chunk-reduce timeouts with clamped STANDARD budgets, job-status polling inflated cloud cache reads, repo-relative paths failed validation, and except OSError swallowed TimeoutError
- **Root Cause:** Background workers lacked cross-process FIFO slot locking (acquire_bjob_worker_slot), Python TimeoutError inherits from OSError so broad except OSError masked timeout propagation, STANDARD map chunks shared tight token caps and 150s reduce caps, and job-collect lacked job_ids batching
- **Verified Resolution & Permanent Guardrail:** Enforce acquire_bjob_worker_slot FIFO locking with explicit except TimeoutError before except OSError, support repo-relative containment in validate_input_paths, lower chunk targets (22000B/450L) with >=768 STANDARD token floor and <=300s reduce budget, and support job_ids batch collection on job-collect/job-collect-any because cross-process queueing and batch collection cut modeled quota by 50.0% with 100% local usability (apprentice_engine.py, apprentice/apprentice_mcp_server.py (`SBX-20261116_201657-a1c0f4f0`)).

---

### `LL-WS-23` [TIER5] — 4608-token reduce cap triggered Qwen3.6 <think> exhaustion and dropped cross-slice items, 2048 fast cap... (`2026-11-17`)
- **Retirement Provenance (`TIER5` — `2026-11-19`):** Archived to TIER5 after retiring legacy workstation v2.6 scripts to RAID (v2.6.1_2026-11-19_pre_v3_cutover); superseded by dynamic %-of-context sizing and fast STANDARD defaults (PRIN-08).
- **Subsystem-Domain:** `script:apprentice` (cross-project workstation host runtime)
- **Migrated-From:** `Workstation_Operations` (prefix `LL-WS` preserved)
- **Symptom / Trap:** 4608-token reduce cap triggered Qwen3.6 <think> exhaustion and dropped cross-slice items, 2048 fast cap clipped dense audits, include_git_diff skipped verify_claims via git_diff_head_delta, and monolithic repo_audit risked tool schema bloat
- **Root Cause:** Lossy chunk summaries starved reduce reasoning of cross-file facts, tight output caps forced reasoning_recovered truncation, transient patch mounting was omitted for git diffs, and bundling shadow CPU+semantic critique inside repo_audit overlapped its 6-param Quarantine workflow
- **Verified Resolution & Permanent Guardrail:** Default to effort=auto via classify_hybrid_effort (STANDARD default + stage_patch lock, HIGH_CROSS_SINGLE_SHOT <=36KB, lossless Map -> 8192-cap HIGH Reduce >36KB), raise PROFILES fast cap to 3072, mount .patch sources via _mount_optional_patch_sources() on include_git_diff=True, isolate second-eyes CPU+semantic critique in apprentice_shadow_review (SHADOW_SECOND_EYES_V1), and ship PORTABILITY_AND_TUNING_GUIDE.md for cross-host calibration (`apprentice_engine.py` ([`Workstation_Operations_Software.md`](../Workstation_Operations_Software.md)), `apprentice/apprentice_mcp_server.py` ([`Workstation_Operations_Software.md`](../Workstation_Operations_Software.md)), `apprentice_plugin/skills/apprentice/references/PORTABILITY_AND_TUNING_GUIDE.md` ([`Workstation_Operations.md`](../Workstation_Operations.md)) (`SBX-20261117_160850-0a2a9043`)).

---

### `LL-WS-24` [TIER5] [TRADE-OFF] — Single-posture sidecar thresholds slowed Hydrogen on <25KB reads while Carbon Orchestrator sessions... (`2026-11-18`)
- **Retirement Provenance (`TIER5` — `2026-11-19`):** Archived to TIER5 (empirically disproven trade-off: restrictive Two-Posture host-tier byte walls collapsed daily sidecar calls to 8/21h); retired to RAID (v2.6.1_2026-11-19_pre_v3_cutover) and superseded by PRIN-08.
- **Subsystem-Domain:** `script:apprentice` (cross-project workstation host runtime)
- **Migrated-From:** `Workstation_Operations` (prefix `LL-WS` preserved)
- **Decision Context & Options:** Single-posture sidecar thresholds slowed Hydrogen on <25KB reads while Carbon Orchestrator sessions ignored Apprentice (0/1534 steps), omitted stage_patch #L context caused kwarg guessing (BC-0284), and redundant verdict/async log calls burned 3 extra Carbon turns in canary c9df9b28
- **Why Chosen Path Won (& Cost Paid):** Execution-tier models (Hydrogen/Sonnet) optimize for speed whereas Frontier models (Carbon/Argon/Opus) require quota shielding without 3B-MoE comprehension loss on primary code, PreInvocation modelName can report auto without transcript fallback, and auto-recorded clean verdicts did not require manual re-submission
- **Transferable Rule & Invalidation Boundary:** Enforce portable Two-Posture Host-Tier Routing (EXECUTION_TIER <25KB native Speed-First vs FRONTIER_TIER >=8KB sync log sieves + Gate 3 #L read_file, #L context_files on stage_patch, and override-only verdict calls) with transcriptPath <16KB tail tier detection and [APPRENTICE HOST TIER SWITCH] notices (`apprentice/apprentice_lifecycle_hook.py` ([`Workstation_Operations_Software.md`](../Workstation_Operations_Software.md)), `apprentice_plugin/rules/AGENTS.md` ([`Workstation_Operations.md`](../Workstation_Operations.md)), `apprentice_plugin/skills/apprentice/SKILL.md` ([`Workstation_Operations.md`](../Workstation_Operations.md)) (`SBX-20261118_122312-a22ad7bc`)).

---

### `LL-WS-26` [TIER5] [TRAP] — Benchmark runs inflated v2.4 Apprentice usable rate to 89.8% (73.5% real prod across 34 calls), 4 failed... (`2026-11-18`)
- **Retirement Provenance (`TIER5` — `2026-11-19`):** Archived to TIER5 after retiring legacy workstation v2.5/v2.6 scripts to RAID (v2.6.1_2026-11-19_pre_v3_cutover); benchmark cache isolation rule promoted to cleanroom Principles PRIN-09 (LIN-6855dc81f288).
- **Subsystem-Domain:** `script:apprentice` (cross-project workstation host runtime)
- **Migrated-From:** `Workstation_Operations` (prefix `LL-WS` preserved)
- **Symptom / Trap:** Benchmark runs inflated v2.4 Apprentice usable rate to 89.8% (73.5% real prod across 34 calls), 4 failed BJOBs dropped call_id, shadow_review crashed on Quarantine_README.md and cross-repo task SHAs while mislabeling unchunked 31k-tok calls HYBRID_MAP_STD_REDUCE_HIGH, malformed #file1#L1#file2#L2 citations passed as clean, uncontextualized stage_patch scripts passed mocked --self-test, and repair/tiny-diff ETAs skewed MAPE to 94-142%
- **Root Cause:** benchmark_apprentice defaulted --telemetry-log to live DEFAULT_TELEMETRY_LOG; outer except blocks and _execute_job_worker dropped call_id or skipped record_call_outcome; _discover_repo_sources and _run_cpu_truth_oracles skipped _filter_authoritative_verify_sources and multi-entity scoping; verify_claims lacked sibling git-root anchors on task umbrellas; stage_patch lacked local-import context guards; _run_full_repair_with_guard logged parent HIGH predicted_eta_s; validate_staging_dir allowed bare TMPDIR under scratch/
- **Verified Resolution & Permanent Guardrail:** Isolate benchmark_apprentice to ~/.cache/apprentice_plugin/bench/ via _isolated_bench_env with SHA-256 zero-drift checks on live prod cache; record corrected call_id across all tool exception paths and orphan BJOB workers; filter Quarantine/non-auth/foreign-entity sources before select_collision_free_sources and attach 1 non-colliding sibling git anchor for cited task-umbrella SHAs; block malformed #L hash-chains/colon/inverted/OOB anchors via _detect_citation_format_defects and uncontextualized local imports via _detect_uncontextualized_local_imports with smoke_provenance; compute dedicated repair_eta and reject bare TMPDIR in validate_staging_dir (`apprentice_engine.py` ([`Workstation_Operations_Software.md`](../Workstation_Operations_Software.md)), `apprentice/apprentice_mcp_server.py` ([`Workstation_Operations_Software.md`](../Workstation_Operations_Software.md)), `benchmark_apprentice.py` ([`Workstation_Operations_Software.md`](../Workstation_Operations_Software.md)) (`SBX-20261118_160818-9d3ae193`)).

---

### `LL-WS-27` [TIER5] [TRAP] — Phase 3 STANDARD/HIGH suites exposed four failure modes: _deduplicate_full_context_diff emitted synthetic... (`2026-11-18`)
- **Retirement Provenance (`TIER5` — `2026-11-19`):** Archived to TIER5 after retiring legacy workstation v2.5/v2.6 benchmark scripts to RAID (v2.6.1_2026-11-19_pre_v3_cutover); raw diff and repo PYTHONPATH invariants built into standalone v3.0.
- **Subsystem-Domain:** `script:apprentice` (cross-project workstation host runtime)
- **Migrated-From:** `Workstation_Operations` (prefix `LL-WS` preserved)
- **Symptom / Trap:** Phase 3 STANDARD/HIGH suites exposed four failure modes: _deduplicate_full_context_diff emitted synthetic +[see verbatim Guide.md#L3-L3 above] hunks that Qwen3.6 treated as broken working-tree edits in shadow_review (clean_arm [TBD] alarm and trap_arm VRF=False); literal <file>#L<start>-L<end> prompt hints caused HIGH to emit <Assembly_Guide.md>#L4 angle brackets; _run_smoke_test lacked repo PYTHONPATH for #L local API scripts and estimate_eta underpredicted greenfield stage_patch; STANDARD gave 100% up to 24.3 KB value tables (S8C 21.5s) but false-flagged negated safety rules (S8E), while >45 KB tables/parsers degraded (H1 6/10, H2 83.3%, H4 75%).
- **Root Cause:** assemble_prompt_payload applied --unified=0 diff deduplication unconditionally even during diff critique (shadow_review); prompt templates used <file> angle-bracket placeholders; _run_smoke_test omitted repo_root/scripts/context parent dirs from PYTHONPATH; and STANDARD non-thinking misses semantic negation whereas Map-Reduce max ~24 rows per slice and dense >45 KB prompts clip cross-file facts.
- **Verified Resolution & Permanent Guardrail:** Pass compact_git_diff=False in _apprentice_shadow_review_sync so shadow critics inspect raw '+' diff hunks (H5 3/3 traps, VRF=True, -67% clean latency); replace <file>#L<start>-L<end> prompt syntax with unbracketed file.ext#Lstart-Lend and flag _ANGLED_FILE_ANCHOR_RE deterministically (H3 100% first-pass clean); prepend repo/scripts/context dirs to _run_smoke_test PYTHONPATH (S6 11.7s first-pass clean) and calibrate greenfield/retry stage_patch ETA; keep HIGH on semantic/safety audits and escalate >=45 KB dense audits or edge-case parsers to Frontier. (`apprentice_engine.py` ([`Workstation_Operations_Software.md`](../Workstation_Operations_Software.md)), `apprentice/apprentice_mcp_server.py` ([`Workstation_Operations_Software.md`](../Workstation_Operations_Software.md)), `benchmark_apprentice_standard.py` ([`Workstation_Operations_Software.md`](../Workstation_Operations_Software.md)), `benchmark_apprentice_high.py` ([`Workstation_Operations_Software.md`](../Workstation_Operations_Software.md)) (`SBX-20261118_173005-8630c735`)).

---

### `LL-WS-28` [TIER5] [TRAP] — Same-basename SKILL.md citations triggered false out-of-bounds anchor errors (BC-0290), chunked 8-batch... (`2026-11-18`)
- **Retirement Provenance (`TIER5` — `2026-11-19`):** Archived to TIER5 after retiring legacy workstation v2.6 scripts to RAID (v2.6.1_2026-11-19_pre_v3_cutover); POSIX relative path-suffix citation matching already promoted to cleanroom Principles PRIN-06 (LIN-967dfe659c07).
- **Subsystem-Domain:** `script:apprentice` (cross-project workstation host runtime)
- **Migrated-From:** `Workstation_Operations` (prefix `LL-WS` preserved)
- **Symptom / Trap:** Same-basename SKILL.md citations triggered false out-of-bounds anchor errors (BC-0290), chunked 8-batch HIGH ETAs underpredicted single-GPU throughput (BC-0291), and Apprentice preflight --map calls were blocked by SIDECAR_SCRIPT_RE.
- **Root Cause:** _detect_citation_format_defects and _run_cpu_truth_oracles resolved files by basename instead of POSIX path suffixes, surgical repair lacked working_tree_delta.patch fallback, estimate_chunked_eta assumed 0.5x wave halving on 2-slot single GPU, and GOVERNED_PY_SCRIPTS excluded Homunculus scripts.
- **Verified Resolution & Permanent Guardrail:** Match trailing POSIX path suffixes in citation bounds and emit repo-relative targets; fall back to working_tree_delta.patch and min_lines=1 during single-file shadow repair (BC-0292 100% healed, H5 3/3 Pass-1 clean); recalibrate estimate_chunked_eta to ~0.90x parallel GPU model; expand GOVERNED_PY_SCRIPTS. (`apprentice_engine.py` ([`Workstation_Operations_Software.md`](../Workstation_Operations_Software.md)), `apprentice/apprentice_mcp_server.py` ([`Workstation_Operations_Software.md`](../Workstation_Operations_Software.md)), `apprentice/apprentice_lifecycle_hook.py` ([`Workstation_Operations_Software.md`](../Workstation_Operations_Software.md)), `benchmark_apprentice_high.py` ([`Workstation_Operations_Software.md`](../Workstation_Operations_Software.md)) (`SBX-20261118_205811-ca257d09 | BC-0292 | H5`)).

---
