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
