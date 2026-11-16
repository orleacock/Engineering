---
project: "Workstation_Operations"
entity: "Orin_Workstation"
compartment: "private"
project_type: "software"
status: "active"
local_path: "../scripts"
repo_head_sha: "UNTRACKED"
tree_hash: "bb470dc7e4ac"
checkpoint_head_sha: "UNTRACKED"
checkpoint_tree_hash: "bb470dc7e4ac"
checkpoint_worktree: "untracked"
task_umbrella: "../../Tasks/Orin_Workstation_Tasks.md"
last_synced: "2026-11-16"
checkpoint_lessons_digest: "80855e442ad570c0"
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

- **Core Objective**: Workstation bootstrap automation (`bootstrap_workstation.sh`), multi-compartment Git pre-commit/pre-push firewall hooks (`git_pre_commit_boundary.sh`, `pre_push_engineering_guard.sh`), parent & home umbrella config sync (`umbrella_configs/{Projects,Home}.homunculus.json`), Dual-Account Gmail MCP server (`gmail_mcp/gmail_mcp_server.py`), and governed LM Studio Bionic local sidecar & `bionic-sidecar` Antigravity plugin (`local_sidecar.py`, `bionic_sidecar/`, `bionic_sidecar_plugin/`) for the local engineering workstation (`/home/orin/Projects/Engineering`).
- **Primary Repository Path**: `../scripts`
- **Verified Key Parameters**:
  - **Workstation Bootstrap**: `bootstrap_workstation.sh` ([`Workstation_Operations_Software.md`](Workstation_Operations_Software.md)) wires `Homunculus/rules/*.md`, `Homunculus/skills/*`, and `Homunculus/addons/*` into `~/.gemini/config/` (`0` duplicate `.agents/` trees), registers `memory/` in `~/.config/obsidian/obsidian.json`, syncs `/home/orin/Projects/{.homunculus.json,.geminiignore}` + `/home/orin/.homunculus.json`, and installs + `cmp -s`-verifies `.git/hooks/{pre-commit,pre-push}` across `/home/orin/Projects/Engineering` and `/home/orin/Projects/Alchemical3D/*`.
  - **Multi-Compartment Boundary Guard**: `git_pre_commit_boundary.sh` ([`Workstation_Operations_Software.md`](Workstation_Operations_Software.md)) and `pre_push_engineering_guard.sh` ([`Workstation_Operations_Software.md`](Workstation_Operations_Software.md)) execute `Homunculus/scripts/audit_data_boundary.py` prior to commits and pushes across `private`, `public`, and `cleanroom` compartments, paired with directory-scoped Git identities (`~/.gitconfig` `[includeIf]`), SSH host aliases (`~/.ssh/config`: `github-orleacock` and `github-alchemical`), and offline Raid snapshots (`/run/media/orin/Raid/Backup Documents/`).
  - **Dual-Account Gmail MCP Server**: `gmail_mcp/gmail_mcp_server.py` ([`Workstation_Operations_Software.md`](Workstation_Operations_Software.md)) provides OAuth 2.0 `Read + Create Drafts` access (`gmail.readonly` + `gmail.compose`) with `visibility_radar` and `verified_send_as_aliases` enforcement (`personal` `orleacock@gmail.com` + `alchemical` `orin@alchemical3d.net` / `we@alchemical3d.net`).
  - **Immutable RAID Deliverable Restore Guard (`S1-A`)**: `snapshot_homunculus_version.py` (`build_restore_script`) preserves live `~/.gemini/config/mcp_config.json` (staging redacted snapshot configs to `mcp_config.redacted_reference.json`) and prunes only `Homunculus`/`Engineering`/dangling symlinks in `~/.gemini/config/{rules,skills}`. Because the initial `v0.1.0_2026-11-10_foundation_baseline` RAID deliverable is write-once `0444`-locked (`0` in-place edits permitted), if ever running full-workstation recovery from that specific `v0.1.0` snapshot, invoke the updated `scripts/snapshot_homunculus_version.py` restore template or back up live `~/.gemini/config/mcp_config.json` and non-Homunculus user skills/rules first (its `--restore-engine-only` mode is already unaffected).
  - **Ring-0 & Memory Governance Human Turnkey (`h_sudo.sh` / `~/.local/bin/h-sudo`)**: Out-of-tree `/dev/tty` human turnkey helper ([`Workstation_Operations_Software.md`](Workstation_Operations_Software.md)) supporting `status`, `unlock [--with-memory] --files ... --reason "..."` (`unlock-all`), `seal [--with-memory] --reason "..."` (`seal-all`), `revoke`, `enroll-turnkeys`, `enroll-signer`, `policy`, `unlock-memory`, and `seal-memory`, sequencing Ring-0 and Memory Governance prompts inside a single interactive command to eliminate multi-line clipboard paste swallowing.
  - **Verified Anti-Hallucination Fast-Path Cache (`verified_fastpath.py`)**: Parent-only workstation accelerator ([`Workstation_Operations_Software.md`](Workstation_Operations_Software.md)) storing `VERIFIED_FASTPATH_V1` pure-JSON SHA-256 receipts in `.cache/verified_fastpath.json` (`0600` atomic writes, `EROFS` fallback), wired into `git_pre_commit_boundary.sh` for Stage-X `sync_memory.py --audit` deduplication while keeping `audit_data_boundary.py --staged` strictly live and uncached.
  - **LM Studio Bionic Local Sidecar (`local_sidecar.py`, `bionic-sidecar` Plugin & `~/.lmstudio/` Containment)**: Loopback-only (`127.0.0.1:1234`) sidecar bridge (`Qwen3.6-35B-A3B` `Q4_K_M`, text-only) running on `ROCm 2.73.0` (bundled `Vulkan 2.73.0` retained untouched as fallback), locked to `0.65` MoE @ `49,152` ctx (`10.045 GiB` VRAM loaded) alongside `CPU-Background` (`--device none` `CCD2`, `0.00 GiB` model VRAM), with `60.0s` `auto` (`AUTO_MAX_ETA_SECONDS`) / `90.0s` `explicit` (`DEFAULT_MAX_ETA_SECONDS`) ETA circuit breakers (`RUN_LOCALLY` vs. `HANDOFF_TO_MAIN_THREAD`). Anchor B wires the `bionic-sidecar` Antigravity plugin (`bionic_sidecar_plugin/plugin.json` `1.0.0`, `bionic_sidecar/bionic_lifecycle_hook.py`, `bionic_sidecar/bionic_mcp_server.py`) exposing `4` MCP tools (`bionic_control`, `bionic_digest`, `bionic_repo_audit`, `bionic_stage_patch`), Turn-1 `PreInvocation` `OFFLINE`/`UNLOADED` remote-startup notices (`900`s idle re-notify, zero `systemMessage.metadata`), `user_confirmed=True` lifecycle gating (`gpu-daily` `49,152` ctx / `cpu-bg` `16,384` ctx), `PreToolUse` `run_command` `:1234`/`lms`/AppImage bypass blocking (`[BIONIC_UTILITY_REQUIRED]`), `_safe_subprocess_cwd` unlinked-`cwd` resilience, and `bootstrap_workstation.sh` plugin sync & strict validation. Enforces `~/.lmstudio/` containment (`logSensitiveData: false`, `webSearchEnabled: false`, `Manual Review` shell gate, single-repo scope, `9` core `Homunculus/skills` symlinks with `gmail-workspace-assistant`, `author-voice-cadence`, and `hardware-cad-inspector` explicitly disabled pending `hardware-cad-inspector` module maturation tracked in `Orin_Workstation_Tasks.md`), routing code drafts to scratch staging and audit notes strictly via `memory_gateway.py quarantine-note` into per-project `Quarantine/` folders.

---

## 3. Session Handoff & Multi-Session Kickstart (`SESSION-HANDOFF`)

> **Turn-1 Cold-Resume Rule**: When resuming `Workstation_Operations` after a break, verify `Checkpoint Provenance` against the live repository (`sync_memory.py --memory-root <memory_root> --project Workstation_Operations --kickstart`), surface the **Where We Stopped** summary and **Next Session Kickstart & Discussion Points** to the user, and confirm alignment before mutating files. Overwrite this block in place at session wrap-up (`--save-handoff`; supports detailed `500–800+ word` stopping context and `Project State Ledger` snapshots without growing the file over time).

<!-- SESSION-HANDOFF:START -->
- **Last Session Timestamp**: `2026-11-16`
- **Checkpoint Provenance**: `HEAD SHA: UNTRACKED` | `Tree Hash: bb470dc7e4ac` | `Worktree: untracked` | `Last Verification: SBX-20261116_115434-6a8592af / SBX-20261116_120126-ce5a5240`
- **Where We Stopped (Verified State & Context)**:
  Implemented and verified Bionic Sidecar V2.4.5 (Slice-Count Map-Reduce, fast + prioritized #L Pass-2 repair, non-sleep injectable-clock Pass-1 .py rules) in SBX-20261116_115434-6a8592af (4/4 controls, 3/3 +faults) and SBX-20261116_120126-ce5a5240 (live gpu-daily 49152 PASS); working tree staged/ready for review & commit.
- **Active Project State Ledger & Blockers**: None
- **Next Session Kickstart & Discussion Points**:
  1. Review git diff and commit/push V2.4.5, run bootstrap_workstation.sh to sync plugin docs, and restart host Antigravity MCP session when at home workstation.
<!-- SESSION-HANDOFF:END -->

---

## 4. Repository File Tree (`AUTO-TREE`)

<!-- AUTO-TREE:START -->
```text
Repository: scripts | HEAD SHA: UNTRACKED | Tree Hash: bb470dc7e4ac
  bionic_sidecar/
  bionic_sidecar/bionic_lifecycle_hook.py
  bionic_sidecar/bionic_mcp_server.py
  bionic_sidecar_plugin/
  bionic_sidecar_plugin/rules/
  bionic_sidecar_plugin/rules/AGENTS.md
  bionic_sidecar_plugin/skills/
  bionic_sidecar_plugin/skills/bionic-local-sidecar/
  bionic_sidecar_plugin/skills/bionic-local-sidecar/SKILL.md
  bionic_sidecar_plugin/hooks.json
  bionic_sidecar_plugin/mcp_config.json
  bionic_sidecar_plugin/plugin.json
  gmail_mcp/
  gmail_mcp/gmail-workspace-assistant/
  gmail_mcp/gmail-workspace-assistant/SKILL.md
  gmail_mcp/gmail_mcp_server.py
  gmail_mcp/README.md
  gmail_mcp/requirements.txt
  umbrella_configs/
  umbrella_configs/Home.homunculus.json
  umbrella_configs/Projects.homunculus.json
  benchmark_bionic_sidecar.py
  benchmark_history.jsonl
  benchmark_homunculus.py
  bionic_benchmark_history.jsonl
  bootstrap_workstation.sh
  git_pre_commit_boundary.sh
  h_sudo.sh
  homunculus_version.json
  local_sidecar.py
  pre_push_engineering_guard.sh
  snapshot_homunculus_version.py
  telemetry_pulse_history.jsonl
  verified_fastpath.py
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
