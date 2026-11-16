---
name: bionic-local-sidecar
description: Governed workflow for offloading bounded digests, repo pre-audits, scratch code staging, and user-confirmed remote lifecycle control to LM Studio Bionic (`Qwen3.6-35B-A3B`) via `bionic_sidecar` MCP and `local_sidecar.py`.
---

# Skill: Bionic Local Sidecar (`bionic-local-sidecar`)

Operates strictly under Homunculus Priority (`1. Accuracy & Truth > 2. Efficiency -> 3. Data Safety > 4. Speed`) and core rules (`co-engineering-partner`, `data-and-credential-safety`, `verifiable-accuracy`).

---

## 1. Pre-Flight Foundation Checks

1. **Governed Entrypoint Lock**: Never query `127.0.0.1:1234` (including decimal/hex/octal loopback or shell wrappers), launch `Bionic*.AppImage`, or run `lms` lifecycle/chat commands (`PreToolUse` hook hard-denies bypasses). Route all calls via the `bionic-sidecar` MCP server in `<mcp_servers>` (`bionic_control`, `bionic_digest`, `bionic_repo_audit`, `bionic_stage_patch`) or `python3 -B /home/orin/Projects/Engineering/scripts/local_sidecar.py`.
2. **Turn-1 Remote State & Explicit Approval**:
   - Inspect status via `bionic_control(action="status")` (never auto-start or load VRAM autonomously).
   - Profiles (`user_confirmed=True` required): `gpu-max` (`57344` ctx, `--parallel 2`, `0.52` CPU expert ratio, `10/24` logical threads configured leaving `14` threads & `>=2.0 GiB` free VRAM for desktop/web browsing), `gpu-daily` (`49152` ctx, `--parallel 2`, `0.65` CPU expert ratio, `8/24` logical threads), or `cpu-bg` (`16384` ctx, `0 GiB` VRAM).
3. **Firewalls & Single-Repo Containment (`4C`)**: Reject raw `.step`/`.stp`/`.stl`/`.3mf` (`ZERO_ADHOC_CAD_PARSING`), secret/OAuth/MCP config JSONs, `.env*`, SSH keys, `NetCom`, and cross-repo inputs before transmission. Prefer focused `#Lstart-Lend` context slices (`file.py#L10-L80`) over whole-file dumps when working inside large modules.

---

## 2. Two Effort Tiers, Agile Sprints & Self-Heal Flow

1. **`STANDARD` vs `HIGH` Effort Tiers** (strictly two modes; `fast`/`deep`/`cpu-bg` legacy aliases remain compatible):
   - **`effort="standard"`** (`2048` default output tokens, `60s` auto / `90s` explicit target): Daily bounded log/diff/file summarization (`bionic_digest`) and isolated scratch prototyping (`bionic_stage_patch` with `py_compile` + optional `smoke_test_args` + dedicated `45s` repair retry).
   - **`effort="high"`** (`4096` min floor / `8192` default / `10240` max output tokens, `180s` soft target): Quota-maximizing deep diffs, multi-file synthesis (with `<think>` trace synthesis recovery + `>42 KB` map-reduce), and `bionic_repo_audit(invocation_tier="explicit", effort="high")` (`preflight_live_inference` -> `audit_repo_docs.py` -> `LL-WS-12` sweep -> `memory_gateway.py quarantine-note` -> collision-free `verify_claims.py` Pass 1). Frontier thread validates all `HIGH` outputs before promoting.

| Effort Tier | `reasoning_effort` | Output Budget (Floor / Default / Cap) | GPU Wall Time (`gpu-max`) | Context & Quota Savings | Best Workload Fit |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **`STANDARD`** | `none` | `1` / `2048` / unclipped | `~2s–35s` (`~40–49 tok/s`) | ~`60–88%` direct ctx offloaded; high net frontier eq-tok saved | Clean file/diff digests, BOM lists, fast `stage_patch` helpers |
| **`HIGH`** | `high` | `4096` / `8192` / `10240` | `~50s–180s` (`~36–50 tok/s`) | Strips `~2.5–6.0k` local thinking tokens; max multi-file synthesis savings | Complex repo audits, multi-file reasoning, async sprint jobs |
2. **Parallel Agile Sprints & `V2.3` Self-Heal Automation**:
   - Pass `async_job=True` to `bionic_digest`, `bionic_repo_audit`, or `bionic_stage_patch` to launch a background sprint immediately (`BJOB-*`), continue frontier work in parallel, and collect at your frontier stop point via `bionic_control(action="job-status"|"job-collect"|"job-list", job_id=..., wait_seconds=120)`. Synchronous `HIGH` MCP calls also auto-promote to background `BJOB-*` at `135s` (`auto_promoted_async=True`) so they never hit Antigravity's `180s` MCP deadline — collect the returned `job_id` directly rather than re-submitting.
   - **`V2.3` Zero-Bloat & Auto-Heal Defaults**:
     - Headless API calls use a lean embedded system prompt (`<= 1,050 B`, saving `~330` tok/call vs verbose GUI prose) while preserving full `LL-WS-12` guards.
     - `bionic_digest` enables `verify_claims=True` by default on file-backed digests (`~0.12s` / `~120ms` subprocess check, `<= 220 B` compact receipt; skipped in `0.0ms` when `context_files` is empty or `include_git_diff=True`), runs line-preserving `--parallel 2` map-reduce automatically on un-sliced `STANDARD` files `> 36 KB`, and seamlessly heals `finish_reason="length"` clips with 1 tail continuation.
     - `bionic_repo_audit` self-heals `length` clips and runs `verify_claims.py` Pass 1 (plus 1 self-scrub retry if needed) **before** writing `Quarantine/` once via `memory_gateway.py`, grading unresolved failures as `corrected` (never `clean`).
     - `bionic_stage_patch` checks unclosed code fences and auto-runs `--self-test` when detected in Python AST (`if __name__ == "__main__":` + `"--self-test"`), with 1 dedicated repair retry.
3. **Self-Heal & Relative Epoch Scorecard (`Bionic Calls`)**:
   - Calls repaired locally and verified clean are classified `verdict="healed"` (flagged `slow_self_heal=True` if repair `>45s`).
   - Downgrade/update prior verdicts whenever the main thread fixes an issue via `bionic_control(action="verdict", call_id=..., verdict="corrected", note=...)` or `prev_call_id`/`prev_verdict`.
   - Start a clean developmental epoch via `bionic_control(action="scorecard-reset", epoch_label=..., user_confirmed=True)` (archives the prior epoch losslessly to `bionic_scorecard_archive.jsonl` while keeping `next_seq` monotonic).
   - Always include `[BIONIC SIDECAR NOTICE]` with `Bionic Calls = <clean>/<corrected> (healed=<healed>) [<usable>% usable, <corr>% corr | <delta>% vs <prev>]` in user-facing replies.

---

## 3. Stop & Escalation Conditions

Halt local delegation and handle on the frontier thread if:
- `[ETA_CIRCUIT_BREAKER_TRIPPED]` triggers (`> 60s` auto or `> 90s` explicit) or `Bionic` reports `OFFLINE` / `UNLOADED` without user confirmation to start.
- `[SECURITY_FIREWALL_BLOCKED]` or `[BIONIC_UTILITY_REQUIRED]` triggers on any path, URL, or staging target.
- Bionic output omits hardware counts/fasteners flagged by `audit_repo_docs.py` or fails `verify_claims.py` provenance checks (`LL-WS-12`).
