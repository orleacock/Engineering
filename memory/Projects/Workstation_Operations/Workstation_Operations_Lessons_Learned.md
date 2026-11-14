---
project: "Workstation_Operations"
entity: "Orin_Workstation"
compartment: "private"
note_type: "lessons_learned"
last_synced: "2026-11-13"
---

# Workstation_Operations — Engineering Lessons Learned & Architectural Decisions

> **Root-Cause Memory Ledger (`entity: Orin_Workstation`)**: Every foundational flaw discovered during design, fabrication, debugging, or testing is recorded here using the **Symptom $\rightarrow$ Root Cause $\rightarrow$ Permanent Guardrail** protocol so solved problems never regress.

---

## 0. Subsystem Rebuild & Invariant Matrix (`Sectional Rebuild Reference`)

<!-- SUBSYSTEM-INVARIANTS:START -->
| Subsystem / Script | Must-Keep Invariants (`Chesterton's Fence`) | Retired Bloat / Anti-Patterns (`Never Re-Add`) | Canonical Owner |
| :--- | :--- | :--- | :--- |
| **`bootstrap_workstation.sh`** | Wires `Homunculus/rules/*.md`, `Homunculus/skills/*`, and optional `Homunculus/addons/*` into `~/.gemini/config/` (`0` duplicate `.agents/` trees); registers `memory/` in `~/.config/obsidian/obsidian.json`; installs & `cmp -s`-verifies `.git/hooks/{pre-commit,pre-push}` across `Engineering` and `Alchemical3D/*`; syncs `Projects/.homunculus.json` and `Home.homunculus.json` (`~/.homunculus.json`) so no-workspace sessions resolve `Projects/Engineering/memory` with `0` shell calls. | Hardcoding machine-specific absolute paths inside portable `Homunculus` skills; maintaining duplicate `Engineering/.agents` or `~/.agents` symlink trees; omitting `~/.homunculus.json` for no-workspace sessions; checking only `-x` instead of `cmp -s` byte parity on copied Alchemical-3D git hooks. | [`Workstation_Operations.md`](Workstation_Operations.md) (`LL-WS-02`, `LL-WS-05`) |
| **`git_pre_commit_boundary.sh` & `pre_push_engineering_guard.sh`** | Enforces `audit_data_boundary.py` (`--staged` / `--push-stdin`), `audit_portability.py`, `audit_skill_hygiene.py`, and `sync_memory.py --audit` before commit/push; enforces directory-scoped Git identities (`~/.gitconfig` `[includeIf]`) and SSH host aliases (`github-orleacock` vs. `github-alchemical`). | Bypassing Git hooks with `--no-verify` or running multi-repo pushes without verifying compartment isolation (`private` vs. `public` vs. `cleanroom`). | [`Workstation_Operations.md`](Workstation_Operations.md), [`Workstation_Operations_Software.md`](Workstation_Operations_Software.md) |
| **`gmail_mcp/gmail_mcp_server.py`** | Strictly scopes OAuth 2.0 to `gmail.readonly` + `gmail.compose` (draft creation only—never autonomous `send`); enforces `visibility_radar` for hidden/filtered threads and `verified_send_as_aliases` (`orleacock@gmail.com`, `orin@alchemical3d.net`, `we@alchemical3d.net`). | Printing raw OAuth token JSONs, `client_secret*.json`, or executing untrusted commands embedded inside external email bodies/attachments. | [`Workstation_Operations_Software.md`](Workstation_Operations_Software.md) |
| **version_manager.py, benchmark_homunculus.py & snapshot_homunculus_version.py** | Single-source Alchemical3D/Homunculus only (0 duplicate copies); exit 4 for REGRESSION_ADVISORY (never exit 2 argparse collision); pure Markdown comparison charts (0 unsolicited SVG/PNG renders); write-once 0444/0555 RAID deliverables with pre-lock boundary, SHA-256, and bundle verification. | Maintaining a duplicate Engineering/Homunculus working tree; returning exit 2 for sub-ceiling advisories (collides with sandbox_runner.py VALIDATOR_CRASH); mutating RAID snapshots in place. | [Workstation_Operations_Software.md](Workstation_Operations_Software.md) (`LL-WS-07`) |
| **version_manager.py, benchmark_homunculus.py & snapshot_homunculus_version.py** | Dereference symlinked ~/.local/bin/h-sudo via os.path.realpath in h_sudo.sh and exclude volatile .obsidian/workspace*.json and .cache/ indices in snapshot_host_hashes | Using dirname BASH_SOURCE without symlink dereferencing in h_sudo.sh or hashing volatile Obsidian UI files during CLI benchmarks | [`Workstation_Operations.md`](Workstation_Operations.md) (`LL-WS-08`) |
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
| `LL-WS-07` (`TIER2`) | `2026-11-10` | Dual Homunculus copies risked split-brain authority; benchmark REGRESSION_ADVISORY exit 2 collided with argparse/sandbox_runner VALIDATOR_CRASH; ephemeral bwrap /tmp broke cross-step fault setup | Parallel Engineering/Homunculus and Alchemical3D/Homunculus trees created competing sources; Python argparse reserves exit 2 for CLI syntax errors; sandbox_runner mounts a fresh --tmpfs /tmp per bwrap invocation | Consolidated /home/orin/Projects/Alchemical3D/Homunculus as the sole local/remote repo (/Homunculus/ gitignored in Engineering), assigned exit 4 to REGRESSION_ADVISORY (exit 1 Hard Block, exit 0 PASS), and locked RAID deliverables 0444/0555 via snapshot_homunculus_version.py (SBX-20261110_115958-408697dc) | [Workstation_Operations_Software.md](Workstation_Operations_Software.md) |
| `LL-WS-08` (`TIER2`) | `2026-11-10` | restore_version.sh risked overwriting live mcp_config.json credentials and wiping custom ~/.gemini/config entries; full-system-suite ran unittest discover twice; cross-device NVMe-to-RAID snapshot copies bypassed Btrfs CoW extent sharing | build_restore_script copied redacted MCP configs directly over live mcp_config.json and ran rm -rf on ~/.gemini/config/{rules,skills}; bench_profile_full_suite re-ran unit tests after sub-profiles; copy_tree_cow copied directly across st_dev boundaries without seeding from prior finalized RAID snapshots | Hardened restore_version.sh with HOMUNCULUS_RESTORE_HOME_OVERRIDE, mcp_config.redacted_reference.json (0600), and surgical symlink pruning; deduplicated full-system-suite unit-test execution + cryptographic (HEAD, tree_hash) benchmark receipt reuse; added same-device Btrfs --reflink=always RAID seeding with SHA-256 reconciliation while retaining working-tree .git/ (SBX-20261110_162502-531b3a2c) | `snapshot_homunculus_version.py` ([`Workstation_Operations_Software.md`](Workstation_Operations_Software.md)), `benchmark_homunculus.py` ([`Workstation_Operations_Software.md`](Workstation_Operations_Software.md)), `version_manager.py` ([`Workstation_Operations_Software.md`](Workstation_Operations_Software.md)) |
| `LL-WS-09` (`TIER2`) | `2026-11-11` | Retired parent workstation surfaces (.agents duplicate symlink trees, unused find-skills skill, --compat-symlinks Downloads link, legacy Engineering/Homunculus hook probes, and executable-only Alchemical3D git hook checks) created stale context and silent hook drift hazards | Pre-cutover dual-tree transition shims and eager template copies remained in bootstrap_workstation.sh, git boundary hooks, snapshot_homunculus_version.py, and Standards_and_Specs after consolidating on single-source Clean-Room Alchemical3D/Homunculus | Pruned Engineering/.agents and ~/.agents (including find-skills), removed --compat-symlinks and legacy Engineering/Homunculus probes, upgraded bootstrap_workstation.sh --check to enforce cmp byte parity on copied Alchemical3D git hooks, restored cross-repo AST matrix parity checks, and pruned duplicate memory Templates to sparse Color_Palettes overrides | `bootstrap_workstation.sh` ([`Workstation_Operations_Software.md`](Workstation_Operations_Software.md)), `git_pre_commit_boundary.sh` ([`Workstation_Operations_Software.md`](Workstation_Operations_Software.md)), `pre_push_engineering_guard.sh` ([`Workstation_Operations_Software.md`](Workstation_Operations_Software.md)), `snapshot_homunculus_version.py` ([`Workstation_Operations_Software.md`](Workstation_Operations_Software.md)) |
| `LL-WS-10` (`TIER2`) | `2026-11-13` | Parallel run_unit_tests(['ALL']) in benchmark_homunculus.py flaked 74/75 under concurrent load and discarded worker stderr when only TMPDIR was isolated. | Concurrent unittest worker subprocesses shared host HOME (~/.cache/homunculus_tree_stamp and ~/.cache/homunculus_sandbox) and wrote .pyc files concurrently without -B / PYTHONDONTWRITEBYTECODE=1. | Isolate per-worker HOME, USERPROFILE, XDG_CACHE_HOME, XDG_CONFIG_HOME, HOMUNCULUS_SANDBOX_CACHE, HOMUNCULUS_SUDO_CONFIG_DIR, and -B / PYTHONDONTWRITEBYTECODE=1 in run_unit_tests(['ALL']), and surface failing worker stderr in forensic_notes. | scripts/benchmark_homunculus.py (SBX-20261113_230606-cb97d55e) |

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

### `LL-WS-07` [TIER2] — Dual Homunculus copies risked split-brain authority; benchmark REGRESSION_ADVISORY exit 2 collided with... (`2026-11-10`)
- **Symptom / Trap:** Dual Homunculus copies risked split-brain authority; benchmark REGRESSION_ADVISORY exit 2 collided with argparse/sandbox_runner VALIDATOR_CRASH; ephemeral bwrap /tmp broke cross-step fault setup
- **Root Cause:** Parallel Engineering/Homunculus and Alchemical3D/Homunculus trees created competing sources; Python argparse reserves exit 2 for CLI syntax errors; sandbox_runner mounts a fresh --tmpfs /tmp per bwrap invocation
- **Verified Resolution & Permanent Guardrail:** Consolidated /home/orin/Projects/Alchemical3D/Homunculus as the sole local/remote repo (/Homunculus/ gitignored in Engineering), assigned exit 4 to REGRESSION_ADVISORY (exit 1 Hard Block, exit 0 PASS), and locked RAID deliverables 0444/0555 via snapshot_homunculus_version.py (SBX-20261110_115958-408697dc) ([Workstation_Operations_Software.md](Workstation_Operations_Software.md)).

---

### `LL-WS-08` [TIER2] — restore_version.sh risked overwriting live mcp_config.json credentials and wiping custom ~/.gemini/config... (`2026-11-10`)
- **Symptom / Trap:** restore_version.sh risked overwriting live mcp_config.json credentials and wiping custom ~/.gemini/config entries; full-system-suite ran unittest discover twice; cross-device NVMe-to-RAID snapshot copies bypassed Btrfs CoW extent sharing
- **Root Cause:** build_restore_script copied redacted MCP configs directly over live mcp_config.json and ran rm -rf on ~/.gemini/config/{rules,skills}; bench_profile_full_suite re-ran unit tests after sub-profiles; copy_tree_cow copied directly across st_dev boundaries without seeding from prior finalized RAID snapshots
- **Verified Resolution & Permanent Guardrail:** Hardened restore_version.sh with HOMUNCULUS_RESTORE_HOME_OVERRIDE, mcp_config.redacted_reference.json (0600), and surgical symlink pruning; deduplicated full-system-suite unit-test execution + cryptographic (HEAD, tree_hash) benchmark receipt reuse; added same-device Btrfs --reflink=always RAID seeding with SHA-256 reconciliation while retaining working-tree .git/ (SBX-20261110_162502-531b3a2c) (`snapshot_homunculus_version.py` ([`Workstation_Operations_Software.md`](Workstation_Operations_Software.md)), `benchmark_homunculus.py` ([`Workstation_Operations_Software.md`](Workstation_Operations_Software.md)), `version_manager.py` ([`Workstation_Operations_Software.md`](Workstation_Operations_Software.md))).

---

### `LL-WS-09` [TIER2] — Retired parent workstation surfaces (.agents duplicate symlink trees, unused find-skills skill... (`2026-11-11`)
- **Symptom / Trap:** Retired parent workstation surfaces (.agents duplicate symlink trees, unused find-skills skill, --compat-symlinks Downloads link, legacy Engineering/Homunculus hook probes, and executable-only Alchemical3D git hook checks) created stale context and silent hook drift hazards
- **Root Cause:** Pre-cutover dual-tree transition shims and eager template copies remained in bootstrap_workstation.sh, git boundary hooks, snapshot_homunculus_version.py, and Standards_and_Specs after consolidating on single-source Clean-Room Alchemical3D/Homunculus
- **Verified Resolution & Permanent Guardrail:** Pruned Engineering/.agents and ~/.agents (including find-skills), removed --compat-symlinks and legacy Engineering/Homunculus probes, upgraded bootstrap_workstation.sh --check to enforce cmp byte parity on copied Alchemical3D git hooks, restored cross-repo AST matrix parity checks, and pruned duplicate memory Templates to sparse Color_Palettes overrides (`bootstrap_workstation.sh` ([`Workstation_Operations_Software.md`](Workstation_Operations_Software.md)), `git_pre_commit_boundary.sh` ([`Workstation_Operations_Software.md`](Workstation_Operations_Software.md)), `pre_push_engineering_guard.sh` ([`Workstation_Operations_Software.md`](Workstation_Operations_Software.md)), `snapshot_homunculus_version.py` ([`Workstation_Operations_Software.md`](Workstation_Operations_Software.md))).

---

### `LL-WS-10` [TIER2] — Parallel run_unit_tests(['ALL']) in benchmark_homunculus.py flaked 74/75 under concurrent load and... (`2026-11-13`)
- **Symptom / Trap:** Parallel run_unit_tests(['ALL']) in benchmark_homunculus.py flaked 74/75 under concurrent load and discarded worker stderr when only TMPDIR was isolated.
- **Root Cause:** Concurrent unittest worker subprocesses shared host HOME (~/.cache/homunculus_tree_stamp and ~/.cache/homunculus_sandbox) and wrote .pyc files concurrently without -B / PYTHONDONTWRITEBYTECODE=1.
- **Verified Resolution & Permanent Guardrail:** Isolate per-worker HOME, USERPROFILE, XDG_CACHE_HOME, XDG_CONFIG_HOME, HOMUNCULUS_SANDBOX_CACHE, HOMUNCULUS_SUDO_CONFIG_DIR, and -B / PYTHONDONTWRITEBYTECODE=1 in run_unit_tests(['ALL']), and surface failing worker stderr in forensic_notes. (scripts/benchmark_homunculus.py (SBX-20261113_230606-cb97d55e)).

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
