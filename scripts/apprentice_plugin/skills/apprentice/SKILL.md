---
name: apprentice
description: >-
  Governed multi-backend workflow for offloading bounded digests, repo pre-audits,
  parallel Shadow Second-Eyes reviews, scratch code staging, and user-confirmed
  local inference lifecycle control (LM Studio Bionic, Ollama, llama.cpp /
  OpenAI-compatible loopback backends) via `apprentice` MCP and `apprentice_engine.py`.
---

# Skill: Apprentice Local Sidecar (`apprentice`)

Operates strictly under Homunculus Priority (`1. Accuracy & Truth > 2. Efficiency -> 3. Data Safety > 4. Speed`) and core rules (`co-engineering-partner`, `data-and-credential-safety`, `verifiable-accuracy`). Cross-system deployment and hardware/model calibration notes live in [`references/PORTABILITY_AND_TUNING_GUIDE.md`](references/PORTABILITY_AND_TUNING_GUIDE.md).

---

## 1. Pluggable Backends & Pre-Flight Checks

1. **Multi-Backend Adapter Registry (`--backend auto|bionic|ollama|llamacpp|openai_compat`)**:
   - **`bionic` (default)**: LM Studio Bionic (`127.0.0.1:1234/v1`, `/api/v0/models`, profiles `gpu-max`/`gpu-daily`/`cpu-bg`).
   - **`ollama` / `llamacpp` / `openai_compat`**: Loopback `/api/ps`+`/api/tags` or `/v1/models` adapters sharing identical firewall, ETA breaker, KV-slot, and `verify_claims.py` gates.
2. **Governed Entrypoint Lock**: Never query `:1234` directly, launch `Bionic*.AppImage`, or invoke `lms` lifecycle commands; route via `apprentice` MCP tools (`apprentice_control`, `apprentice_digest`, `apprentice_repo_audit`, `apprentice_stage_patch`, `apprentice_shadow_review`) or `python3 -B scripts/apprentice_engine.py`.
3. **Firewalls & Focused Slicing**: Reject raw `.step`/`.stp`/`.stl`/`.3mf`, secrets, `.env*`, SSH keys, restricted client compartments, and cross-repo escapes (`4C`). Pass explicit `#Lstart-Lend` slices for focused sections.

---

## 2. Size-Aware Effort Routing, Shadow Second-Eyes & Relative Scorecard

1. **`effort="auto"` (default)** routes dynamically via `classify_hybrid_effort()`:
   - **Routes to `STANDARD`** (`3072` fast output cap, `reasoning_effort="none"`, `<=60s` auto / `<=90s` explicit, `<=2` concurrent async jobs): all `apprentice_stage_patch` calls, single-file extracts, log compression, non-audit summaries, and chunk `map` waves (`lossless Item | Literal/Qty | Anchor` rows).
   - **Routes to `HIGH`** (`4096` floor / `8192` default / `10240` cap, `180s` soft target, serialized `1`-at-a-time FIFO): cross-file contradiction audits (`>=2` distinct files or `include_git_diff=True` paired with cross-audit keywords) and `apprentice_repo_audit` sweeps. Payloads `<=54 KB` (`55296 B`) stay Single-Shot to avoid lossy map omissions and intermediate bloat; oversized cross-audits (`>54 KB`) run query-filtered `STANDARD` Map -> `HIGH` (`8192`-cap, `260–300s` timeout) Reduce.
2. **Parallel `apprentice_shadow_review` (`SHADOW_SECOND_EYES_V1`)**:
   - Launch with `async_job=True` while continuing frontier work: executes sub-second CPU truth oracles (`verify_claims.py`, `audit_repo_docs.py`, `audit_data_boundary.py`, `ast.parse`) first, then runs a local semantic critic (`<=450` words) to catch safety hazards (`[!CAUTION]`) and cross-file contradictions that literal provenance checks pass.
   - `include_git_diff=True` automatically mounts a transient `.patch` verification source across `apprentice_digest`, `apprentice_repo_audit`, and `apprentice_shadow_review`.
3. **Sprint Collection & Relative Scorecard**:
   - For `async_job=True` sprints, pass `job_ids=[...]` to `apprentice_control(action="job-collect-any", wait_seconds=120)` (or `action="job-collect"`) instead of polling `job-status`.
   - Telemetry & scorecards persist under `~/.cache/apprentice_plugin/` (preserving migrated historical `homunculus_bionic_plugin/` metrics).

---

## 3. Host-Tier Postures & Accuracy-Locked Offload Signatures

1. **Opposing Host-Tier Economics (`0%` Accuracy Compromise)**:
   - **`EXECUTION_TIER` (`Hydrogen`, `Sonnet`, `Haiku` — Speed-First)**: Keep `<25KB` reads, `30–80` line code windows, and small helpers native on the host model; offload `>=25KB` (`>=4`-doc) reconciliations and multi-file `pre-commit-gate` `apprentice_shadow_review(async_job=True, include_git_diff=True)`.
   - **`FRONTIER_TIER` (`Carbon`, `Argon`, `Opus` — Quota-Shield)**: Keep `Ring 0`, core architecture, and primary code/spec `30–80` line windows `100%` native on Frontier (never replace Frontier comprehension with a quantized summary). Offload **(a)** `>=8KB` test/sandbox log coordinate sieves (via synchronous `apprentice_digest(async_job=False)` on `<25KB` `STANDARD` logs, followed by mandatory `Gate 3` direct `read_file` on cited `#L` hunks), **(b)** `#L`-anchored `Version_Logs/` candidate harvesting, **(c)** `>=3KB` disposable `scratch/*.py` test fixtures via `apprentice_stage_patch` (passing target `#Lstart-Lend` signature slices in `context_files` and verifying by execution), and **(d)** additive `pre-commit-gate` `apprentice_shadow_review(async_job=True, include_git_diff=True)`. Only call `apprentice_control(action="verdict", ...)` when overriding an auto-recorded `clean`/`healed` verdict to `corrected` after `Gate 3`.
2. **Direct MCP Call Signatures**:
   - `apprentice_digest(prompt, repo="", context_files=[...], include_git_diff=False, effort="auto", verify_claims=True, async_job=False)`
   - `apprentice_stage_patch(target_filename, prompt, staging_dir="/tmp/apprentice_staging", context_files=[...], smoke_test_args=[...], effort="auto")`
   - `apprentice_shadow_review(repo, context_files=[...], draft_files=[...], include_git_diff=True, async_job=True, effort="auto")`
   - `apprentice_repo_audit(repo, project="", focus="", memory_root="", effort="auto", async_job=False)`
   - `apprentice_control(action="status"|"job-collect-any"|"job-collect"|"verdict"|"load"|"start", job_ids=[...], wait_seconds=120, user_confirmed=False)`
