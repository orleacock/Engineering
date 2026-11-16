---
project: "Workstation_Operations"
parent_note: "Workstation_Operations_Lessons_Learned"
entity: "Orin_Workstation"
compartment: "private"
note_type: "lessons_archive"
authoritative: false
last_synced: "2026-11-16"
---

# 🗄️ Workstation_Operations — Graduated & Historical Lessons Archive (`TIER3`–`TIER5`)

> **Single-Source Tiered Archive**: Companion to [`Workstation_Operations_Lessons_Learned.md`](../Workstation_Operations_Lessons_Learned.md). Stores full-context narratives for stabilized `TIER3`, isolated-polish `TIER4`, and retired `TIER5` lessons so the active `<Project>_Lessons_Learned.md` window stays compact (`<= 3 TIER0 + <= 7 TIER2` sections). Query any entry on demand via `sync_memory.py --project Workstation_Operations --lesson-id <LL-xxx>` or promote back to active memory via `--set-tier <LL-xxx> TIER2`.

---

## 1. Archived Full-Context Post-Mortems (`TIER3`–`TIER5`)

### `LL-WS-01` [TIER3] — Directory-Scoped Git `[includeIf]` Identities & SSH Alias Locks (`2026-11-05`)
- **Symptom / Trap:** Multi-account Git commits risked leaking private workstation email or pushing to the wrong GitHub org remote.
- **Root Cause:** Single global `~/.gitconfig` identity across both personal (`Orin_Workstation`) and org repositories.
- **Verified Resolution & Permanent Guardrail:** Configured directory-scoped `[includeIf]` rules in `~/.gitconfig`, dedicated SSH aliases (`github-orleacock`, `github-alchemical`), and `audit_data_boundary.py` remote/email locks in `git_pre_commit_boundary.sh` ([`Workstation_Operations.md`](../Workstation_Operations.md)).

### `LL-WS-02` [TIER3] — Parent `/home/orin/Projects` Umbrella `.homunculus.json` Sync (`2026-11-06`)
- **Symptom / Trap:** Parent `/home/orin/Projects` CWD sessions failed to auto-resolve `memory_dir` when launched outside `/home/orin/Projects/Engineering`.
- **Root Cause:** `.homunculus.json` existed only inside `/home/orin/Projects/Engineering/`, leaving parent umbrella sessions without a declarative pointer.
- **Verified Resolution & Permanent Guardrail:** Added `umbrella_configs/Projects.homunculus.json` and wired `bootstrap_workstation.sh` to sync `/home/orin/Projects/{.homunculus.json,.geminiignore}` ([`Workstation_Operations_Software.md`](../Workstation_Operations_Software.md)).

### `LL-WS-03` [TIER3] — Gmail MCP `visibility_radar` for Non-Visible Unread Threads (`2026-11-06`)
- **Symptom / Trap:** Important emails bypassed `INBOX` via Gmail auto-archive filters and went unnoticed during standard inbox triage.
- **Root Cause:** Standard `label:INBOX` queries miss threads where a filter applied `Skip the Inbox (Archive it)` (`-label:INBOX is:unread`).
- **Verified Resolution & Permanent Guardrail:** Built `visibility_radar` into `gmail_mcp_server.py` and `gmail-workspace-assistant/SKILL.md` to surface non-visible unread threads alongside inbox triage ([`Workstation_Operations_Software.md`](../Workstation_Operations_Software.md)).

### `LL-WS-04` [TIER3] — Pre-Commit AST/CLI & Maintainer Matrix Parity Gate (`2026-11-07`)
- **Symptom / Trap:** Skill/script CLI flags drifted out of sync with `SKILL.md` documentation and `_Software.md` telemetry notes between sessions.
- **Root Cause:** Manual edits to Python `argparse` flags were not automatically cross-checked against `SKILL.md` and `Directory/` indexes prior to commit.
- **Verified Resolution & Permanent Guardrail:** Wired `audit_skill_hygiene.py`, `sync_memory.py --audit`, and AST/CLI parity checks into `git_pre_commit_boundary.sh` (`SBX-20261107_091652-1f171c12`; [`Workstation_Operations.md`](../Workstation_Operations.md)).

### `LL-WS-05` [TIER3] — Provisioning Optional `Homunculus/addons/*` Symlinks in `bootstrap_workstation.sh` (`2026-11-08`)
- **Symptom / Trap:** Optional drop-in add-ons (`hardware-cad-inspector`) moved from `skills/` to `addons/` left broken symlinks or missing active skill links in `~/.gemini/config/skills/`.
- **Root Cause:** `bootstrap_workstation.sh` originally linked only `Homunculus/skills/*` prior to the `Option 2B-Armored` `addons/` architecture split.
- **Verified Resolution & Permanent Guardrail:** Updated workstation skill symlink provisioning to link enabled drop-in add-ons from `Homunculus/addons/*` alongside core `Homunculus/skills/*` ([`Workstation_Operations.md`](../Workstation_Operations.md)).

### `LL-WS-06` [TIER3] — Symlink-Blind `find` in `~/.gemini/config/skills/` vs. Direct `<skills>` Path Derivation (`2026-11-08`)
- **Symptom / Trap:** Subagents running `find /home/orin/.gemini/config -name "*.py"` returned `0` results (`6` wasted turns in `Homunculus R4`).
- **Root Cause:** `/home/orin/.gemini/config/skills/*` are symlinks created by `bootstrap_workstation.sh`; POSIX `find` without `-L` does not traverse symbolic links.
- **Verified Resolution & Permanent Guardrail:** Documented symlink structure in `Workstation_Operations` and banned `find` in favor of direct `<skill_dir>/scripts/<script>.py` path derivation from `<skills>` ([`Workstation_Operations.md`](../Workstation_Operations.md)).

---

### `LL-WS-07` [TIER3] — Dual Homunculus copies risked split-brain authority; benchmark REGRESSION_ADVISORY exit 2 collided with... (`2026-11-10`)
- **Symptom / Trap:** Dual Homunculus copies risked split-brain authority; benchmark REGRESSION_ADVISORY exit 2 collided with argparse/sandbox_runner VALIDATOR_CRASH; ephemeral bwrap /tmp broke cross-step fault setup
- **Root Cause:** Parallel Engineering/Homunculus and Alchemical3D/Homunculus trees created competing sources; Python argparse reserves exit 2 for CLI syntax errors; sandbox_runner mounts a fresh --tmpfs /tmp per bwrap invocation
- **Verified Resolution & Permanent Guardrail:** Consolidated /home/orin/Projects/Alchemical3D/Homunculus as the sole local/remote repo (/Homunculus/ gitignored in Engineering), assigned exit 4 to REGRESSION_ADVISORY (exit 1 Hard Block, exit 0 PASS), and locked RAID deliverables 0444/0555 via snapshot_homunculus_version.py (SBX-20261110_115958-408697dc) ([Workstation_Operations_Software.md](../Workstation_Operations_Software.md)).

---

### `LL-WS-08` [TIER3] — restore_version.sh risked overwriting live mcp_config.json credentials and wiping custom ~/.gemini/config... (`2026-11-10`)
- **Symptom / Trap:** restore_version.sh risked overwriting live mcp_config.json credentials and wiping custom ~/.gemini/config entries; full-system-suite ran unittest discover twice; cross-device NVMe-to-RAID snapshot copies bypassed Btrfs CoW extent sharing
- **Root Cause:** build_restore_script copied redacted MCP configs directly over live mcp_config.json and ran rm -rf on ~/.gemini/config/{rules,skills}; bench_profile_full_suite re-ran unit tests after sub-profiles; copy_tree_cow copied directly across st_dev boundaries without seeding from prior finalized RAID snapshots
- **Verified Resolution & Permanent Guardrail:** Hardened restore_version.sh with HOMUNCULUS_RESTORE_HOME_OVERRIDE, mcp_config.redacted_reference.json (0600), and surgical symlink pruning; deduplicated full-system-suite unit-test execution + cryptographic (HEAD, tree_hash) benchmark receipt reuse; added same-device Btrfs --reflink=always RAID seeding with SHA-256 reconciliation while retaining working-tree .git/ (SBX-20261110_162502-531b3a2c) (`snapshot_homunculus_version.py` ([`Workstation_Operations_Software.md`](../Workstation_Operations_Software.md)), `benchmark_homunculus.py` ([`Workstation_Operations_Software.md`](../Workstation_Operations_Software.md)), `version_manager.py` ([`Workstation_Operations_Software.md`](../Workstation_Operations_Software.md))).

---

### `LL-WS-11` [TIER3] — Serial file-level unittest sharding bottlenecked full-system-suite at 19.82 seconds, Stage-X memory audits... (`2026-11-14`)
- **Symptom / Trap:** Serial file-level unittest sharding bottlenecked full-system-suite at 19.82 seconds, Stage-X memory audits ran twice on pre-commit, and copied sibling git hooks drifted behind Homunculus templates.
- **Root Cause:** benchmark_homunculus sharded whole files instead of AST-inspected unittest methods, git_pre_commit_boundary lacked a Stage-X memory audit receipt check, and bootstrap_workstation used cp -f copies instead of relative symlinks.
- **Verified Resolution & Permanent Guardrail:** Use execution-order-safe LPT unittest method sharding in benchmark_homunculus.py, deduplicate only Stage-X sync_memory --audit via verified_fastpath.py while keeping audit_data_boundary --staged live, and symlink Alchemical3D git hooks. (`benchmark_homunculus.py` ([`Workstation_Operations_Software.md`](../Workstation_Operations_Software.md)), `verified_fastpath.py` ([`Workstation_Operations_Software.md`](../Workstation_Operations_Software.md)), `git_pre_commit_boundary.sh` ([`Workstation_Operations_Software.md`](../Workstation_Operations_Software.md)), `bootstrap_workstation.sh` ([`Workstation_Operations_Software.md`](../Workstation_Operations_Software.md)) (`BMK-20261114_151930-dc5a24cf`)).

---

### `LL-WS-12` [TIER5] — Stage 5.1/5.2 local sidecar pilots (Pestle_Rotational_Bowden & Alembic_Toolhead) hit wrapper CLI flag... (`2026-11-14`)
- **Retirement Provenance (`TIER5` — `2026-11-16`):** Consolidated into LL-WS-20 & LL-WS-21 under multi-backend Apprentice plugin; original Bionic/local_sidecar lessons retained in Archive/ at 0.0x recall weight for historical reference.
- **Scope:** `script:local_sidecar`
- **Symptom / Trap:** Stage 5.1/5.2 local sidecar pilots (`Pestle_Rotational_Bowden` & `Alembic_Toolhead`) hit wrapper CLI flag errors (`author`/`overwrite` arguments rejected by `memory_gateway.py quarantine-note` and `prompt-file` path rejected by `check-eta` 4C repo check), `1800`-token length truncation, unbacked `BHCS` expansion, omitted `Assembly_Guide.md` fastener dimension/quantity catches, and `verify_claims.py` source filename collisions (nested `README.md` and scratch `HEAD_*` folders).
- **Root Cause:** `local_sidecar.py` did not match the `memory_gateway.py quarantine-note` parser contract; `1800` output tokens clipped longer packets without concise formatting rules; small-model `fast` sweep still needs frontier `audit_repo_docs.py` + `verify_claims.py` gating to catch missing fastener specs/counts and source filename collisions.
- **Verified Resolution & Permanent Guardrail:** Embed author in HTML provenance comment & pre-check destination overwrite inside `local_sidecar.py`; set `max_tokens >= 2200` with prompt bans on unbacked acronym expansions/affiliate query params/deleted-diff `#L` anchors; pair sidecar outputs with `audit_repo_docs.py` + `verify_claims.py` avoiding duplicate basenames or foreign folder prefixes among sources. (`local_sidecar.py` ([`Workstation_Operations_Software.md`](../Workstation_Operations_Software.md)) (`Phase 5 pilots complete: local_sidecar.py --self-test 4/4 PASS, SBX-20261114_194505-d8527a97 PASS (3/3 controls, 5/5 +faults), Stage 5.1 ETA 52.9s/actual 45.424s (VRF-71abd793eee7 2-pass ceiling on README.md basename collision), Stage 5.2 ETA 79.87s/actual 80.138s (VRF-0eee6cadc2f2 PASS 79/79 backed).`)).

---

### `LL-WS-13` [TIER5] — Turn-1 Bionic UNLOADED banner vanished on remote session start due to agy 1.5.9 panic in... (`2026-11-14`)
- **Retirement Provenance (`TIER5` — `2026-11-16`):** Consolidated into LL-WS-20 & LL-WS-21 under multi-backend Apprentice plugin; original Bionic/local_sidecar lessons retained in Archive/ at 0.0x recall weight for historical reference.
- **Scope:** `script:bionic_sidecar`
- **Symptom / Trap:** Turn-1 Bionic UNLOADED banner vanished on remote session start due to agy 1.5.9 panic in hookcaller.go/proto_utils.go:34, and hot agy plugin install unlinked running MCP server cwd causing lms daemon status to fail.
- **Root Cause:** agy ScrubInternalFields panics when systemMessage.metadata contains string values in injectSteps, SessionStart fires before user prompt, and subprocess/abspath calls without safe cwd fail after plugin directory inode replacement.
- **Verified Resolution & Permanent Guardrail:** Defer Turn-1 state notice from SessionStart to PreInvocation using pure systemMessage strings (zero metadata/terminationBehavior), check diff -rq before agy plugin install in bootstrap_workstation.sh, and enforce _safe_subprocess_cwd across local_sidecar.py and bionic_mcp_server.py. (`local_sidecar.py` ([`Workstation_Operations_Software.md`](../Workstation_Operations_Software.md)), `bionic_sidecar/bionic_lifecycle_hook.py` ([`Workstation_Operations_Software.md`](../Workstation_Operations_Software.md)), `bionic_sidecar/bionic_mcp_server.py` ([`Workstation_Operations_Software.md`](../Workstation_Operations_Software.md)), `bootstrap_workstation.sh` ([`Workstation_Operations_Software.md`](../Workstation_Operations_Software.md)) (`SBX-20261114_223528-01f61a8c`)).

---

### `LL-WS-14` [TIER5] — V2.3.1 HIGH offloads burned 66-89% tokens in <think> blocks (164-279s), truncated lines >320 chars, lost... (`2026-11-15`)
- **Retirement Provenance (`TIER5` — `2026-11-16`):** Consolidated into LL-WS-20 & LL-WS-21 under multi-backend Apprentice plugin; original Bionic/local_sidecar lessons retained in Archive/ at 0.0x recall weight for historical reference.
- **Scope:** `script:bionic_sidecar`
- **Symptom / Trap:** V2.3.1 HIGH offloads burned 66-89% tokens in <think> blocks (164-279s), truncated lines >320 chars, lost HIGH metadata on repair, and in V2.4.1 Compare-Light parallel synchronous HIGH MCP calls hit Antigravity's 180s MCP transport deadline (BC-0201/BC-0202) while ~/.gemini/config symlinked sync_memory.py tripped TRUSTED_SCRIPT_ROOTS.
- **Root Cause:** Unbounded Qwen3.6 reasoning verbosity on HIGH, hard 320-char line slicing, fast-only single-file repair context, Antigravity's 3m0s synchronous MCP tool deadline vs ~240s multi-file HIGH runs, and bionic_lifecycle_hook checking unresolved abs_p against canonical Homunculus/skills roots.
- **Verified Resolution & Permanent Guardrail:** Retain V2.4.1 CONCISE_HIGH_THINKING_HINT, pack_chunk_batches, and effort-preserving BOM-cross-sliced surgical repair; pass async_job=True on parallel or multi-file HIGH MCP digests so runs never collide with the 180s synchronous MCP transport timeout; invoke governed scripts via canonical /home/orin/Projects/Alchemical3D/Homunculus paths (and Workspace:inherit with disjoint scratch dirs when CWD=/home/orin). (`local_sidecar.py` ([`Workstation_Operations_Software.md`](../Workstation_Operations_Software.md)), `bionic_sidecar/bionic_mcp_server.py` ([`Workstation_Operations_Software.md`](../Workstation_Operations_Software.md)), `bionic_sidecar/bionic_lifecycle_hook.py` ([`Workstation_Operations_Software.md`](../Workstation_Operations_Software.md)) (`SBX-20261115_192953-95ad1972`)).

---

### `LL-WS-15` [TIER5] — Concurrent full deep HIGH streams in --parallel 2 thrashed CPU MoE threads (<20-28 tok/s, 270s socket... (`2026-11-15`)
- **Retirement Provenance (`TIER5` — `2026-11-16`):** Consolidated into LL-WS-20 & LL-WS-21 under multi-backend Apprentice plugin; original Bionic/local_sidecar lessons retained in Archive/ at 0.0x recall weight for historical reference.
- **Scope:** `script:bionic_sidecar`
- **Symptom / Trap:** Concurrent full deep HIGH streams in --parallel 2 thrashed CPU MoE threads (<20-28 tok/s, 270s socket timeouts), synchronous >180s HIGH MCP calls hit Antigravity's 3m0s deadline, symlinked ~/.gemini/config governed scripts tripped PreToolUse, and repo_audit/stage_patch lacked uniform claims_verified/completion_telemetry keys and synchronous --self-test repair guidance.
- **Root Cause:** acquire_kv_budget allowed 2 concurrent 8192-tok deep streams, @mcp.tool lacked a bounded sync-wait auto-promotion wrapper and job-collect wait clamp, bionic_lifecycle_hook checked abs_p only against canonical roots, and stage_patch Pass-2 repair lacked deterministic non-threaded --self-test reconciliation.
- **Verified Resolution & Permanent Guardrail:** Keep V2.4.2 exclusive=True single-slot serialization for full deep calls (>=3072 tok, reasoning!=none) while preserving max_slots=2 for mapper batches/fast calls; keep 135s MCP_SYNC_WAIT_CAP_SECONDS auto-promotion + job-collect clamp; keep TRUSTED_INVOCATION_ROOTS symlink check; maintain uniform claims_verified/elapsed_s/completion_telemetry across MCP tools. (`local_sidecar.py` ([`Workstation_Operations_Software.md`](../Workstation_Operations_Software.md)), `bionic_sidecar/bionic_mcp_server.py` ([`Workstation_Operations_Software.md`](../Workstation_Operations_Software.md)), `bionic_sidecar/bionic_lifecycle_hook.py` ([`Workstation_Operations_Software.md`](../Workstation_Operations_Software.md)) (`SBX-20261115_201646-7b821e18, SBX-20261115_201757-0218ae49`)).

---

### `LL-WS-16` [TIER5] — gpu-daily --parallel 4 kept idle batch slots vs max_slots<=2, and STANDARD chunked map-reduce reduce... (`2026-11-15`)
- **Retirement Provenance (`TIER5` — `2026-11-16`):** Consolidated into LL-WS-20 & LL-WS-21 under multi-backend Apprentice plugin; original Bionic/local_sidecar lessons retained in Archive/ at 0.0x recall weight for historical reference.
- **Scope:** `script:bionic_sidecar`
- **Symptom / Trap:** gpu-daily --parallel 4 kept idle batch slots vs max_slots<=2, and STANDARD chunked map-reduce reduce clipping at 2048 tokens (BC-0217) bypassed tail continuation inside else:.
- **Root Cause:** The length tail-continuation loop was nested only inside the single-shot else: branch of _bionic_digest_sync, default STANDARD reduce lacked multi-batch headroom, and >36KB STANDARD calls bypassed _run_mcp_with_sync_guard.
- **Verified Resolution & Permanent Guardrail:** Keep gpu-daily tightened to --parallel 2, run length continuation outside if use_auto_chunk: using reduce_prompt, grant up to 3072 STANDARD reduce tokens, and enable 135s auto-async guard for >36KB digests. (`local_sidecar.py` ([`Workstation_Operations_Software.md`](../Workstation_Operations_Software.md)), `bionic_sidecar/bionic_mcp_server.py` ([`Workstation_Operations_Software.md`](../Workstation_Operations_Software.md)), `bionic_sidecar_plugin/skills/bionic-local-sidecar/SKILL.md` ([`Workstation_Operations.md`](../Workstation_Operations.md)) (`SBX-20261115_212505-c787f842, SBX-20261115_212610-e71371b9`)).

---

### `LL-WS-17` [TIER5] — Multiple #Lstart-Lend slices of the same file passed to Bionic overwrote earlier slices in a Path-keyed... (`2026-11-16`)
- **Retirement Provenance (`TIER5` — `2026-11-16`):** Consolidated into LL-WS-20 & LL-WS-21 under multi-backend Apprentice plugin; original Bionic/local_sidecar lessons retained in Archive/ at 0.0x recall weight for historical reference.
- **Scope:** `script:bionic_sidecar`
- **Symptom / Trap:** Multiple #Lstart-Lend slices of the same file passed to Bionic overwrote earlier slices in a Path-keyed dict, and HIGH verify_claims repair runs (2560 tok cap, no continuation) could clip or regress unbacked line counts
- **Root Cause:** parse_and_validate_context_specs returned dict[Path, slice] overwriting duplicate Path keys, while _bionic_digest_sync and bionic_repo_audit shared duplicated 2560-tok repair blocks lacking continuation hops and non-regression guards
- **Verified Resolution & Permanent Guardrail:** Preserve per-slice context via parse_and_validate_context_items() across local_sidecar.py and bionic_mcp_server.py; route repair passes through shared _run_full_repair_with_guard() (4096-6144 deep tok cap, 1x2048 continuation hop, reject clipped/regressed/vacuous-zero repairs) (`local_sidecar.py` ([`Workstation_Operations_Software.md`](../Workstation_Operations_Software.md)), `bionic_sidecar/bionic_mcp_server.py` ([`Workstation_Operations_Software.md`](../Workstation_Operations_Software.md)) (`SBX-20261116_081805-cc62b7b4 / BC-0226 / BC-0227`)).

---

### `LL-WS-18` [TIER5] — V2.4.4 audit (BC-0225/BC-0228) uncovered .patch files omitted from verify_claims --sources, mixed... (`2026-11-16`)
- **Retirement Provenance (`TIER5` — `2026-11-16`):** Consolidated into LL-WS-20 & LL-WS-21 under multi-backend Apprentice plugin; original Bionic/local_sidecar lessons retained in Archive/ at 0.0x recall weight for historical reference.
- **Scope:** `script:bionic_sidecar`
- **Symptom / Trap:** V2.4.4 audit (BC-0225/BC-0228) uncovered .patch files omitted from verify_claims --sources, mixed unsliced+#L payloads bypassing chunking to ~42k tok, raw [:1500] JSON fail_detail clipping claims #3-#12, tight 45s/90s sub-timeouts inside async jobs, 3.45x-4.02x chunked ETA under-prediction, and missing kv_wait_s separation.
- **Root Cause:** _VERIFY_ALLOWED_EXTS excluded .patch/.diff and capped unbacked_claims at [:8]; use_auto_chunk gated on not any_sliced while plan_line_preserving_chunks ignored slice_items; verify repair dumped full line_text JSON [:1500]; async sub-calls inherited sync 45s/90s timeouts and 1536 cont caps.
- **Verified Resolution & Permanent Guardrail:** Lock 49152 gpu-daily as fixed baseline (retain gpu-max optional); add .patch/.diff + [:20] unbacked slice; split unsliced vs #L slices in chunker and _is_heavy_chunked_sync_candidate; use _format_compact_verify_failures() and LL_WS_12_GUARD frontmatter/patch rules; widen async sub-timeouts (120-180s), cont_max_toks (2560/3072), and explicit sync-guard; add estimate_chunked_eta() and kv_wait_s. (`local_sidecar.py` ([`Workstation_Operations_Software.md`](../Workstation_Operations_Software.md)), `bionic_sidecar/bionic_mcp_server.py` ([`Workstation_Operations_Software.md`](../Workstation_Operations_Software.md))).

---

### `LL-WS-19` [TIER5] — Blindly raising max_slices_per_batch=6 on dense Python silently dropped BASE_GUARD (base_covered=false)... (`2026-11-16`)
- **Retirement Provenance (`TIER5` — `2026-11-16`):** Consolidated into LL-WS-20 & LL-WS-21 under multi-backend Apprentice plugin; original Bionic/local_sidecar lessons retained in Archive/ at 0.0x recall weight for historical reference.
- **Scope:** `script:bionic_sidecar`
- **Symptom / Trap:** Blindly raising max_slices_per_batch=6 on dense Python silently dropped BASE_GUARD (base_covered=false) while Priority-Cap=10 dropped 8/18 (44.4%) markers; small multi-file #L digests (<36 KB) bypassed chunking into ~190-326s monolithic HIGH calls, and stage_patch Pass-2 deep retries burned ~97s without schema context.
- **Root Cause:** Byte-only chunk threshold (>36KB/42KB) excluded compact >=5-slice explicit #L digests, pack_chunk_batches >4 files crowded multi-module sweeps, and stage_patch Pass-2 used mode=effective_mode without validated_files context.
- **Verified Resolution & Permanent Guardrail:** Keep max_slices_per_batch=4; trigger Slice-Count Map-Reduce cleanly for >=5 explicit #L slices across >=3 files in bionic_mcp_server.py (100% 18/18 recall); switch stage_patch Pass-2 repair to fast mode with prioritized <=20KB #L context + AST sleep antipattern check; inject non-sleep injectable-clock .py Pass-1 staging rules; keep HTTP mock asserts on main thread. (`bionic_sidecar/bionic_mcp_server.py` ([`Workstation_Operations_Software.md`](../Workstation_Operations_Software.md)), `bionic_sidecar_plugin/rules/AGENTS.md` ([`Workstation_Operations.md`](../Workstation_Operations.md)), `bionic_sidecar_plugin/skills/bionic-local-sidecar/SKILL.md` ([`Workstation_Operations.md`](../Workstation_Operations.md)) (`SBX-20261116_115434-6a8592af / SBX-20261116_120126-ce5a5240`)).

---
