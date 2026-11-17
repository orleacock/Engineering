---
name: apprentice
description: >-
  Governed multi-backend workflow for offloading bounded digests, repo pre-audits,
  scratch code staging, and user-confirmed local inference lifecycle control
  (LM Studio Bionic, Ollama, llama.cpp / OpenAI-compatible loopback backends)
  via `apprentice` MCP and `apprentice_engine.py`.
---

# Skill: Apprentice Local Sidecar (`apprentice`)

Operates strictly under Homunculus Priority (`1. Accuracy & Truth > 2. Efficiency -> 3. Data Safety > 4. Speed`) and core rules (`co-engineering-partner`, `data-and-credential-safety`, `verifiable-accuracy`).

---

## 1. Pluggable Backends & Pre-Flight Checks

1. **Multi-Backend Adapter Registry (`--backend auto|bionic|ollama|llamacpp|openai_compat`)**:
   - **`bionic` (default)**: LM Studio Bionic (`127.0.0.1:1234/v1`, `/api/v0/models`, profiles `gpu-max`/`gpu-daily`/`cpu-bg`).
   - **`ollama` / `llamacpp` / `openai_compat`**: Loopback `/api/ps`+`/api/tags` or `/v1/models` adapters sharing identical firewall, ETA breaker, KV-slot, and `verify_claims.py` gates.
2. **Governed Entrypoint Lock**: Never query `:1234` directly, launch `Bionic*.AppImage`, or invoke `lms` lifecycle commands; route via `apprentice` MCP tools (`apprentice_control`, `apprentice_digest`, `apprentice_repo_audit`, `apprentice_stage_patch`) or `python3 -B /home/orin/Projects/Engineering/scripts/apprentice_engine.py`.
3. **Firewalls & Focused Slicing**: Reject raw `.step`/`.stp`/`.stl`/`.3mf`, secrets, `.env*`, SSH keys, `NetCom`, and cross-repo escapes (`4C`). Pass explicit `#Lstart-Lend` slices for focused sections.

---

## 2. Effort Tiers, Self-Heal & Relative Scorecard

1. **`effort="standard"` (default)** (`2048` default output tokens, `<=60s` auto / `<=90s` explicit, `<=2` concurrent async jobs queued safely) vs. **`effort="high"`** (`4096` floor / `8192` default / `10240` cap, `180s` soft target, `<think>` recovery, serialized `1`-at-a-time FIFO queue).
2. For `async_job=True` sprints, pass `job_ids=[...]` to `apprentice_control(action="job-collect-any", wait_seconds=120)` (or `action="job-collect"`) instead of polling `job-status`.
3. Telemetry & scorecards persist under `~/.cache/apprentice_plugin/` (preserving migrated historical `homunculus_bionic_plugin/` metrics).
