---
title: "Engineering Memory — Workstation Host & Local-Model Runtime Shelf"
entity: "shared"
compartment: "private"
note_type: "host_runtime_lessons"
authoritative: false
last_synced: "2026-11-19"
---

# Host_Runtime — Shared Workstation & Local-Model Runtime Ledger (`LL-HOST-xxx` / `LL-WS-xx`)

> **Cross-Project Host Shelf (`entity: shared`, `compartment: private`, `authoritative: false`)**: Stores workstation-wide tool constraints and local LLM behavioral bounds shared across repositories on this machine. Never stores client secrets, proprietary project specs, or non-portable `Principles/` prose.

<!-- SUBSYSTEM-INVARIANTS:START -->
| Subsystem / Runtime | Must-Keep Invariants (`Chesterton's Fence`) | Retired Bloat / Anti-Patterns (`Never Re-Add`) | Governing `LL-IDs` |
| :--- | :--- | :--- | :--- |
<!-- SUBSYSTEM-INVARIANTS:END -->

## 1. Quick-Lookup Runtime Index

| ID | Tier | Archetype | Date | Scope | Guardrail Summary | Location |
| :--- | :---: | :---: | :--- | :--- | :--- | :--- |
| **`LL-HOST-01`** | `TIER2` | `[TRAP]` | `2026-11-19` | `host:antigravity_plugins` | Defer Turn-1 notices to PreInvocation pure systemMessage strings without metadata, check diff -rq before... | [Host_Runtime_Lessons.md](Host_Runtime_Lessons.md) |

---

## 2. Active Host & Local-Model Runtime Entries (`TIER0` & `TIER2`)

### `LL-HOST-01` [TIER2] [TRAP] — CLI plugin lifecycle hooks crash or silently drop Turn-1 banners when emitting systemMessage.metadata or... (`2026-11-19`)
- **Scope:** `host:antigravity_plugins`
- **Symptom / Trap:** CLI plugin lifecycle hooks crash or silently drop Turn-1 banners when emitting systemMessage.metadata or SessionStart output, unconditional plugin reinstalls break running MCP server cwds via inode swaps, and /v1/models-only probes risk unintended JIT VRAM loads.
- **Root Cause:** Antigravity hook protobuf parsing rejects systemMessage.metadata and premature SessionStart injections, deleting and recreating an active plugin directory invalidates running daemon working directories, and generic /v1/models endpoints hide loaded-vs-downloaded model state.
- **Verified Resolution & Permanent Guardrail:** Defer Turn-1 notices to PreInvocation pure systemMessage strings without metadata, check diff -rq before overwriting installed plugin directories, guard child spawns with a fallback safe cwd, and prefer /api/v0/models or /api/ps loaded-state probes with user_confirmed=True lifecycle gating. (Host Runtime Configuration).
