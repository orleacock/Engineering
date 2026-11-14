---
project: "Workstation_Operations"
parent_note: "Workstation_Operations_Lessons_Learned"
entity: "Orin_Workstation"
compartment: "private"
note_type: "lessons_archive"
authoritative: false
last_synced: "2026-11-14"
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
