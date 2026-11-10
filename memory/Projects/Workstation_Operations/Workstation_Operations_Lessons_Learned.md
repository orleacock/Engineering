---
project: "Workstation_Operations"
entity: "Orin_Workstation"
compartment: "private"
note_type: "lessons_learned"
last_synced: "2026-11-08"
---

# Workstation_Operations — Engineering Lessons Learned & Architectural Decisions

> **Root-Cause Memory Ledger (`entity: Orin_Workstation`)**: Every foundational flaw discovered during design, fabrication, debugging, or testing is recorded here using the **Symptom $\rightarrow$ Root Cause $\rightarrow$ Permanent Guardrail** protocol so solved problems never regress.

---

## 0. Subsystem Rebuild & Invariant Matrix (`Sectional Rebuild Reference`)

<!-- SUBSYSTEM-INVARIANTS:START -->
| Subsystem / Script | Must-Keep Invariants (`Chesterton's Fence`) | Retired Bloat / Anti-Patterns (`Never Re-Add`) | Canonical Owner |
| :--- | :--- | :--- | :--- |
| **`bootstrap_workstation.sh`** | Wires `Homunculus/rules/*.md`, `Homunculus/skills/*`, and optional `Homunculus/addons/*` into `~/.gemini/config/`; registers `memory/` in `~/.config/obsidian/obsidian.json`; installs `.git/hooks/{pre-commit,pre-push}`; syncs `/home/orin/Projects/{.homunculus.json,.geminiignore}`. | Hardcoding machine-specific absolute paths inside portable `Homunculus` skills instead of resolving via `.homunculus.json` or `homunculus_paths.py`. | [`Workstation_Operations.md`](Workstation_Operations.md) |
| **`git_pre_commit_boundary.sh` & `pre_push_engineering_guard.sh`** | Enforces `audit_data_boundary.py` (`--staged` / `--push-stdin`), `audit_portability.py`, `audit_skill_hygiene.py`, and `sync_memory.py --audit` before commit/push; enforces directory-scoped Git identities (`~/.gitconfig` `[includeIf]`) and SSH host aliases (`github-orleacock` vs. `github-alchemical`). | Bypassing Git hooks with `--no-verify` or running multi-repo pushes without verifying compartment isolation (`private` vs. `public` vs. `cleanroom`). | [`Workstation_Operations.md`](Workstation_Operations.md), [`Workstation_Operations_Software.md`](Workstation_Operations_Software.md) |
| **`gmail_mcp/gmail_mcp_server.py`** | Strictly scopes OAuth 2.0 to `gmail.readonly` + `gmail.compose` (draft creation only—never autonomous `send`); enforces `visibility_radar` for hidden/filtered threads and `verified_send_as_aliases` (`orleacock@gmail.com`, `orin@alchemical3d.net`, `we@alchemical3d.net`). | Printing raw OAuth token JSONs, `client_secret*.json`, or executing untrusted commands embedded inside external email bodies/attachments. | [`Workstation_Operations_Software.md`](Workstation_Operations_Software.md) |
<!-- SUBSYSTEM-INVARIANTS:END -->

---

## 1. Lessons Learned Ledger (`Symptom -> Root Cause -> Guardrail`)

| ID | Date | Symptom / Failure Observed | Root Cause | Permanent Guardrail / Rule or Code Fix | Verification Anchor |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `LL-WS-01` | `2026-11-05` | Multi-account Git commits risked leaking private workstation email or pushing to the wrong GitHub org remote | Single global `~/.gitconfig` identity across both personal (`Orin_Workstation`) and org repositories | Configured directory-scoped `[includeIf]` rules in `~/.gitconfig`, dedicated SSH aliases (`github-orleacock`, `github-alchemical`), and `audit_data_boundary.py` remote/email locks in `git_pre_commit_boundary.sh` | [`Workstation_Operations.md`](Workstation_Operations.md) |
| `LL-WS-02` | `2026-11-06` | Parent `/home/orin/Projects` CWD sessions failed to auto-resolve `memory_dir` when launched outside `/home/orin/Projects/Engineering` | `.homunculus.json` existed only inside `/home/orin/Projects/Engineering/`, leaving parent umbrella sessions without a declarative pointer | Added `umbrella_configs/Projects.homunculus.json` and wired `bootstrap_workstation.sh` to sync `/home/orin/Projects/{.homunculus.json,.geminiignore}` | [`Workstation_Operations_Software.md`](Workstation_Operations_Software.md) |
| `LL-WS-03` | `2026-11-06` | Important emails bypassed `INBOX` via Gmail auto-archive filters and went unnoticed during standard inbox triage | Standard `label:INBOX` queries miss threads where a filter applied `Skip the Inbox (Archive it)` (`-label:INBOX is:unread`) | Built `visibility_radar` into `gmail_mcp_server.py` and `gmail-workspace-assistant/SKILL.md` to surface non-visible unread threads alongside inbox triage | [`Workstation_Operations_Software.md`](Workstation_Operations_Software.md) |
| `LL-WS-04` | `2026-11-07` | Skill/script CLI flags drifted out of sync with `SKILL.md` documentation and `_Software.md` telemetry notes between sessions | Manual edits to Python `argparse` flags were not automatically cross-checked against `SKILL.md` and `Directory/` indexes prior to commit | Wired `audit_skill_hygiene.py`, `sync_memory.py --audit`, and AST/CLI parity checks into `git_pre_commit_boundary.sh` (`SBX-20261107_091652-1f171c12`) | [`Workstation_Operations.md`](Workstation_Operations.md) |
| `LL-WS-05` | `2026-11-08` | Optional drop-in add-ons (`hardware-cad-inspector`) moved from `skills/` to `addons/` left broken symlinks or missing active skill links in `~/.gemini/config/skills/` | `bootstrap_workstation.sh` originally linked only `Homunculus/skills/*` prior to the `Option 2B-Armored` `addons/` architecture split | Updated workstation skill symlink provisioning to link enabled drop-in add-ons from `Homunculus/addons/*` alongside core `Homunculus/skills/*` | [`Workstation_Operations.md`](Workstation_Operations.md) |
| `LL-WS-06` | `2026-11-08` | Subagents running `find /home/orin/.gemini/config -name "*.py"` returned `0` results (`6` wasted turns in `Homunculus R4`) | `/home/orin/.gemini/config/skills/*` are symlinks created by `bootstrap_workstation.sh`; POSIX `find` without `-L` does not traverse symbolic links | Documented symlink structure in `Workstation_Operations` and banned `find` in favor of direct `<skill_dir>/scripts/<script>.py` path derivation from `<skills>` | [`Workstation_Operations.md`](Workstation_Operations.md) |

### `LL-WS-01` [TIER2] — Directory-Scoped Git `[includeIf]` Identities & SSH Alias Locks (`2026-11-05`)
- **Symptom / Trap:** Multi-account Git commits risked leaking private workstation email or pushing to the wrong GitHub org remote.
- **Root Cause:** Single global `~/.gitconfig` identity across both personal (`Orin_Workstation`) and org repositories.
- **Verified Resolution & Permanent Guardrail:** Configured directory-scoped `[includeIf]` rules in `~/.gitconfig`, dedicated SSH aliases (`github-orleacock`, `github-alchemical`), and `audit_data_boundary.py` remote/email locks in `git_pre_commit_boundary.sh` ([`Workstation_Operations.md`](Workstation_Operations.md)).

### `LL-WS-02` [TIER2] — Parent `/home/orin/Projects` Umbrella `.homunculus.json` Sync (`2026-11-06`)
- **Symptom / Trap:** Parent `/home/orin/Projects` CWD sessions failed to auto-resolve `memory_dir` when launched outside `/home/orin/Projects/Engineering`.
- **Root Cause:** `.homunculus.json` existed only inside `/home/orin/Projects/Engineering/`, leaving parent umbrella sessions without a declarative pointer.
- **Verified Resolution & Permanent Guardrail:** Added `umbrella_configs/Projects.homunculus.json` and wired `bootstrap_workstation.sh` to sync `/home/orin/Projects/{.homunculus.json,.geminiignore}` ([`Workstation_Operations_Software.md`](Workstation_Operations_Software.md)).

### `LL-WS-03` [TIER2] — Gmail MCP `visibility_radar` for Non-Visible Unread Threads (`2026-11-06`)
- **Symptom / Trap:** Important emails bypassed `INBOX` via Gmail auto-archive filters and went unnoticed during standard inbox triage.
- **Root Cause:** Standard `label:INBOX` queries miss threads where a filter applied `Skip the Inbox (Archive it)` (`-label:INBOX is:unread`).
- **Verified Resolution & Permanent Guardrail:** Built `visibility_radar` into `gmail_mcp_server.py` and `gmail-workspace-assistant/SKILL.md` to surface non-visible unread threads alongside inbox triage ([`Workstation_Operations_Software.md`](Workstation_Operations_Software.md)).

### `LL-WS-04` [TIER2] — Pre-Commit AST/CLI & Maintainer Matrix Parity Gate (`2026-11-07`)
- **Symptom / Trap:** Skill/script CLI flags drifted out of sync with `SKILL.md` documentation and `_Software.md` telemetry notes between sessions.
- **Root Cause:** Manual edits to Python `argparse` flags were not automatically cross-checked against `SKILL.md` and `Directory/` indexes prior to commit.
- **Verified Resolution & Permanent Guardrail:** Wired `audit_skill_hygiene.py`, `sync_memory.py --audit`, and AST/CLI parity checks into `git_pre_commit_boundary.sh` (`SBX-20261107_091652-1f171c12`; [`Workstation_Operations.md`](Workstation_Operations.md)).

### `LL-WS-05` [TIER2] — Provisioning Optional `Homunculus/addons/*` Symlinks in `bootstrap_workstation.sh` (`2026-11-08`)
- **Symptom / Trap:** Optional drop-in add-ons (`hardware-cad-inspector`) moved from `skills/` to `addons/` left broken symlinks or missing active skill links in `~/.gemini/config/skills/`.
- **Root Cause:** `bootstrap_workstation.sh` originally linked only `Homunculus/skills/*` prior to the `Option 2B-Armored` `addons/` architecture split.
- **Verified Resolution & Permanent Guardrail:** Updated workstation skill symlink provisioning to link enabled drop-in add-ons from `Homunculus/addons/*` alongside core `Homunculus/skills/*` ([`Workstation_Operations.md`](Workstation_Operations.md)).

### `LL-WS-06` [TIER2] — Symlink-Blind `find` in `~/.gemini/config/skills/` vs. Direct `<skills>` Path Derivation (`2026-11-08`)
- **Symptom / Trap:** Subagents running `find /home/orin/.gemini/config -name "*.py"` returned `0` results (`6` wasted turns in `Homunculus R4`).
- **Root Cause:** `/home/orin/.gemini/config/skills/*` are symlinks created by `bootstrap_workstation.sh`; POSIX `find` without `-L` does not traverse symbolic links.
- **Verified Resolution & Permanent Guardrail:** Documented symlink structure in `Workstation_Operations` and banned `find` in favor of direct `<skill_dir>/scripts/<script>.py` path derivation from `<skills>` ([`Workstation_Operations.md`](Workstation_Operations.md)).

---

## 2. Architectural Decision Records (`ADR`)

### `ADR-01`: Initial Project Architecture (`2026-11-06`)
- **Context**: Initial repository and memory scaffolding for `Workstation_Operations` (`project_type: software`).
- **Decision**: Governed under Homunculus Governing Priority Law (`1. Accuracy & Truth -> 2. Efficiency -> 3. Data Safety -> 4. Speed`) with strict `entity: Orin_Workstation` isolation.
- **Consequences**: All quantitative claims require primary source anchors or explicit `[TBD: ...]` tags; unverified notes remain isolated in [`Quarantine/`](Quarantine/Quarantine_README.md).

### `ADR-02`: Read + Draft-Only Boundary for Dual-Account Gmail MCP (`2026-11-06`)
- **Context**: Engineering workstation requires fast email triage and reply staging across personal and organizational accounts without risking accidental or prompt-injected outbound email transmission.
- **Decision**: Restrict `gmail_mcp_server.py` strictly to `gmail.readonly` and `gmail.compose` (creating drafts only, never sending) with mandatory `verified_send_as_aliases` validation and attachment quarantine.
- **Consequences**: All outbound messages are staged as drafts for human review and final send inside the Gmail UI.
