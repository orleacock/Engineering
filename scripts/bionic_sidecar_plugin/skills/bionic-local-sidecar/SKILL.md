---
name: bionic-local-sidecar
description: Governed workflow for offloading bounded digests, repo pre-audits, scratch code staging, and user-confirmed remote lifecycle control to LM Studio Bionic (`Qwen3.6-35B-A3B`) via `bionic_sidecar` MCP and `local_sidecar.py`.
---

# Skill: Bionic Local Sidecar (`bionic-local-sidecar`)

Operates strictly under Homunculus Priority (`1. Accuracy & Truth > 2. Efficiency -> 3. Data Safety > 4. Speed`) and core rules (`co-engineering-partner`, `data-and-credential-safety`, `verifiable-accuracy`).

---

## 1. Pre-Flight Foundation Checks

1. **Governed Entrypoint Lock**: Never query `127.0.0.1:1234`, launch `Bionic*.AppImage`, or run raw `lms` lifecycle/chat commands (`PreToolUse` hook hard-denies bypasses). Route all calls via the `bionic-sidecar` MCP server in `<mcp_servers>` (`bionic_control`, `bionic_digest`, `bionic_repo_audit`, `bionic_stage_patch`) or `python3 /home/orin/Projects/Engineering/scripts/local_sidecar.py`.
2. **Turn-1 Remote State & Explicit Approval**:
   - Inspect status via `bionic_control(action="status")` (never auto-start or load VRAM autonomously).
   - If the `PreInvocation` hook reports `BIONIC_STATE=OFFLINE` or `BIONIC_STATE=UNLOADED`, include the `[BIONIC SIDECAR NOTICE]` banner in your user-facing response for that turn and offer remote startup via `bionic_control(action="start-headless", profile="gpu-daily"|"cpu-bg", user_confirmed=True)` when `OFFLINE`, or `bionic_control(action="load_profile", profile="gpu-daily"|"cpu-bg", user_confirmed=True)` when `UNLOADED` (using the `bionic-sidecar` MCP server in `<mcp_servers>`) only after explicit user confirmation.
3. **Firewalls & Single-Repo Containment (`4C`)**: Reject raw `.step`/`.stp`/`.stl`/`.3mf` (`ZERO_ADHOC_CAD_PARSING`), secret/OAuth/MCP config JSONs, `.env*`, SSH keys, `NetCom`, and cross-repo inputs before transmission.

---

## 2. Step-by-Step Execution Procedures

1. **Auto Offload (`<= 60s` ETA Tier)**:
   - Use `bionic_digest(invocation_tier="auto", mode="fast", max_tokens=1200)` for bounded log/diff/file summarization when Bionic is `ONLINE_READY`.
   - Use `bionic_stage_patch(invocation_tier="auto", mode="fast")` for isolated scratch code/patch prototyping (`py_compile` + unified `.diff`, at most `1` bounded syntax retry inside remaining `60s` budget).
2. **Explicit Local Sweeps (`<= 90s` ETA Tier on `[local]` / `[bionic]`)**:
   - Run `bionic_repo_audit(invocation_tier="explicit", mode="fast", max_tokens=2200)` to execute:
     `audit_repo_docs.py` pre-pass -> Bionic `LL-WS-12`-guarded sweep -> `memory_gateway.py quarantine-note` -> collision-free `verify_claims.py` Pass 1 (`--sources` deduplicated shallow-first).
3. **User Visibility & Promotion Gate**:
   - Include `[BIONIC SIDECAR NOTICE]` in 1 line whenever Bionic is opened, loaded, or invoked.
   - Treat every digest or `Quarantine/` output as unverified until frontier verification (`verify_claims.py` / main-thread review) passes.

---

## 3. Stop & Escalation Conditions

Halt local delegation and handle on the frontier thread if:
- `[ETA_CIRCUIT_BREAKER_TRIPPED]` triggers (`> 60s` auto or `> 90s` explicit) or `Bionic` reports `OFFLINE` / `UNLOADED` without user confirmation to start.
- `[SECURITY_FIREWALL_BLOCKED]` or `[BIONIC_UTILITY_REQUIRED]` triggers on any path, URL, or staging target.
- Bionic output omits hardware counts/fasteners flagged by `audit_repo_docs.py` or fails `verify_claims.py` provenance checks (`LL-WS-12`).
