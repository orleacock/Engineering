---
project: "Workstation_Operations"
entity: "Orin_Workstation"
compartment: "private"
project_type: "software"
status: "active"
local_path: "../scripts"
repo_head_sha: "UNTRACKED"
tree_hash: "0167224a4e41"
checkpoint_head_sha: "UNTRACKED"
checkpoint_tree_hash: "0167224a4e41"
checkpoint_worktree: "untracked"
task_umbrella: "../../Tasks/Orin_Workstation_Tasks.md"
last_synced: "2026-11-13"
checkpoint_lessons_digest: "9bd1efb5c365d2f8"
---

# Workstation_Operations — Project Hub Dossier

> **Entity & Compartment Boundary**: `entity: Orin_Workstation` | `compartment: private` | `project_type: software`
> **Containment Rule**: Do not read, link, or borrow parameters from projects belonging to any entity other than `Orin_Workstation`.

---

## 1. Companion Notes & Project Navigation

| Artifact Role | File Link | Purpose |
| :--- | :--- | :--- |
| **Project Hub (`AUTO-TREE`)** | [`Workstation_Operations.md`](Workstation_Operations.md) | Canonical architecture overview, `SESSION-HANDOFF` kickstart state, `AUTO-TREE`, and Quarantine Zone. |
| **Software Telemetry (`_Software.md`)** | [`Workstation_Operations_Software.md`](Workstation_Operations_Software.md) | Verified runtime entrypoints, CLI flag contracts, schemas, and test receipts. |
| **Lessons Learned & ADRs** | [`Workstation_Operations_Lessons_Learned.md`](Workstation_Operations_Lessons_Learned.md) | Root-cause post-mortems (`Symptom -> Root Cause -> Permanent Guardrail`). |
| **Procedural Playbooks (`_Playbooks.md`)** | [`Workstation_Operations_Playbooks.md`](Workstation_Operations_Playbooks.md) | Reusable workstation release, benchmark, and immutable RAID deliverable runbooks (`PB-WS-*`). |
| **Unverified Quarantine Folder** | [`Quarantine/Quarantine_README.md`](Quarantine/Quarantine_README.md) | Holding zone for unverified notes/vendor quotes (`[QUARANTINED — DO NOT CITE AS FACT]`). |
| **Active Task Umbrella** | [`Orin_Workstation_Tasks.md`](../../Tasks/Orin_Workstation_Tasks.md) | Single-writer task tracker for `Orin_Workstation` (do not duplicate `- [ ]` checkboxes here). |

---

## 2. Executive Architecture & Locked Specifications

- **Core Objective**: Workstation bootstrap automation (`bootstrap_workstation.sh`), multi-compartment Git pre-commit/pre-push firewall hooks (`git_pre_commit_boundary.sh`, `pre_push_engineering_guard.sh`), parent & home umbrella config sync (`umbrella_configs/{Projects,Home}.homunculus.json`), and Dual-Account Gmail MCP server (`gmail_mcp/gmail_mcp_server.py`) for the local engineering workstation (`/home/orin/Projects/Engineering`).
- **Primary Repository Path**: `../scripts`
- **Verified Key Parameters**:
  - **Workstation Bootstrap**: `bootstrap_workstation.sh` ([`Workstation_Operations_Software.md`](Workstation_Operations_Software.md)) wires `Homunculus/rules/*.md`, `Homunculus/skills/*`, and `Homunculus/addons/*` into `~/.gemini/config/` (`0` duplicate `.agents/` trees), registers `memory/` in `~/.config/obsidian/obsidian.json`, syncs `/home/orin/Projects/{.homunculus.json,.geminiignore}` + `/home/orin/.homunculus.json`, and installs + `cmp -s`-verifies `.git/hooks/{pre-commit,pre-push}` across `/home/orin/Projects/Engineering` and `/home/orin/Projects/Alchemical3D/*`.
  - **Multi-Compartment Boundary Guard**: `git_pre_commit_boundary.sh` ([`Workstation_Operations_Software.md`](Workstation_Operations_Software.md)) and `pre_push_engineering_guard.sh` ([`Workstation_Operations_Software.md`](Workstation_Operations_Software.md)) execute `Homunculus/scripts/audit_data_boundary.py` prior to commits and pushes across `private`, `public`, and `cleanroom` compartments, paired with directory-scoped Git identities (`~/.gitconfig` `[includeIf]`), SSH host aliases (`~/.ssh/config`: `github-orleacock` and `github-alchemical`), and offline Raid snapshots (`/run/media/orin/Raid/Backup Documents/`).
  - **Dual-Account Gmail MCP Server**: `gmail_mcp/gmail_mcp_server.py` ([`Workstation_Operations_Software.md`](Workstation_Operations_Software.md)) provides OAuth 2.0 `Read + Create Drafts` access (`gmail.readonly` + `gmail.compose`) with `visibility_radar` and `verified_send_as_aliases` enforcement (`personal` `orleacock@gmail.com` + `alchemical` `orin@alchemical3d.net` / `we@alchemical3d.net`).
  - **Immutable RAID Deliverable Restore Guard (`S1-A`)**: `snapshot_homunculus_version.py` (`build_restore_script`) preserves live `~/.gemini/config/mcp_config.json` (staging redacted snapshot configs to `mcp_config.redacted_reference.json`) and prunes only `Homunculus`/`Engineering`/dangling symlinks in `~/.gemini/config/{rules,skills}`. Because the initial `v0.1.0_2026-11-10_foundation_baseline` RAID deliverable is write-once `0444`-locked (`0` in-place edits permitted), if ever running full-workstation recovery from that specific `v0.1.0` snapshot, invoke the updated `scripts/snapshot_homunculus_version.py` restore template or back up live `~/.gemini/config/mcp_config.json` and non-Homunculus user skills/rules first (its `--restore-engine-only` mode is already unaffected).
  - **Ring-0 & Memory Governance Human Turnkey (`h_sudo.sh` / `~/.local/bin/h-sudo`)**: Out-of-tree `/dev/tty` human turnkey helper ([`Workstation_Operations_Software.md`](Workstation_Operations_Software.md)) supporting `status`, `unlock [--with-memory] --files ... --reason "..."` (`unlock-all`), `seal [--with-memory] --reason "..."` (`seal-all`), `revoke`, `enroll-turnkeys`, `policy`, `unlock-memory`, and `seal-memory`, sequencing Ring-0 and Memory Governance prompts inside a single interactive command to eliminate multi-line clipboard paste swallowing.

---

## 3. Session Handoff & Multi-Session Kickstart (`SESSION-HANDOFF`)

> **Turn-1 Cold-Resume Rule**: When resuming `Workstation_Operations` after a break, verify `Checkpoint Provenance` against the live repository (`sync_memory.py --memory-root <memory_root> --project Workstation_Operations --kickstart`), surface the **Where We Stopped** summary and **Next Session Kickstart & Discussion Points** to the user, and confirm alignment before mutating files. Overwrite this block in place at session wrap-up (`--save-handoff`; supports detailed `500–800+ word` stopping context and `Project State Ledger` snapshots without growing the file over time).

<!-- SESSION-HANDOFF:START -->
- **Last Session Timestamp**: `2026-11-13`
- **Checkpoint Provenance**: `HEAD SHA: UNTRACKED` | `Tree Hash: 0167224a4e41` | `Worktree: untracked` | `Last Verification: BMK-20261113_230808-9c7213da + SBX-20261113_230606-cb97d55e`
- **Where We Stopped (Verified State & Context)**:
  Graduated Homunculus v0.3.3 baseline (BMK-20261113_230808-9c7213da), hardened hermetic parallel unittest HOME isolation (LL-WS-10 / SBX-20261113_230606-cb97d55e), and initialized telemetry_pulse_history.jsonl
- **Active Project State Ledger & Blockers**: None
- **Next Session Kickstart & Discussion Points**:
  1. Execute Homunculus Wave 3 (C1 OpenSSH signing) when scheduled
<!-- SESSION-HANDOFF:END -->

---

## 4. Repository File Tree (`AUTO-TREE`)

<!-- AUTO-TREE:START -->
```text
Repository: scripts | HEAD SHA: UNTRACKED | Tree Hash: 49f5ae26b415
  gmail_mcp/
  gmail_mcp/gmail-workspace-assistant/
  gmail_mcp/gmail-workspace-assistant/SKILL.md
  gmail_mcp/gmail_mcp_server.py
  gmail_mcp/README.md
  gmail_mcp/requirements.txt
  umbrella_configs/
  umbrella_configs/Home.homunculus.json
  umbrella_configs/Projects.homunculus.json
  benchmark_history.jsonl
  benchmark_homunculus.py
  bootstrap_workstation.sh
  git_pre_commit_boundary.sh
  h_sudo.sh
  homunculus_version.json
  pre_push_engineering_guard.sh
  snapshot_homunculus_version.py
  version_manager.py
```
<!-- AUTO-TREE:END -->

---

## 5. Quarantine Zone (Unverified Notes, Scratch Specs & Open `[TBD]`s)

> [!WARNING]
> **`[QUARANTINED — DO NOT CITE AS FACT]`**: Everything inside this section (and inside [`Quarantine/`](Quarantine/Quarantine_README.md)) is explicitly unverified holding data. Downstream documentation, BOMs, calculations, and `verify_claims.py` must **never** treat items in this section as verified ground truth until they are empirically verified and moved to Section 2 or the Domain Telemetry notes.

<!-- QUARANTINE-ZONE:START -->
- *(No unverified quarantine items — all workstation operational scripts verified in `scripts/`.)*
<!-- QUARANTINE-ZONE:END -->
