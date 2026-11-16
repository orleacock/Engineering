---
project: "Workstation_Operations"
entity: "Orin_Workstation"
compartment: "private"
project_type: "software"
status: "active"
local_path: "../scripts"
repo_head_sha: "595049972ad7"
tree_hash: "a723ac6ca722"
checkpoint_head_sha: "595049972ad7"
checkpoint_tree_hash: "a723ac6ca722"
checkpoint_worktree: "dirty (8 files)"
task_umbrella: "../../Tasks/Orin_Workstation_Tasks.md"
last_synced: "2026-11-16"
checkpoint_lessons_digest: "ebbff38391e3c45b"
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
- **Checkpoint Provenance**: `HEAD SHA: 595049972ad7` | `Tree Hash: a723ac6ca722` | `Worktree: dirty (8 files)` | `Last Verification: SBX-20261116_095531-74b156cf / SBX-20261116_094936-7f9998bd`
- **Where We Stopped (Verified State & Context)**:
  Deployed Bionic Sidecar V2.4.4 (local_sidecar 22/22, MCP server 26/26, hook 13/13, SBX-20261116_095531-74b156cf dry-run PASS, SBX-20261116_094936-7f9998bd live gpu-daily 5/5 clean)
- **Active Project State Ledger & Blockers**: None
- **Next Session Kickstart & Discussion Points**:
  1. Refresh client MCP session onto V2.4.4 (async_job=True workers already execute V2.4.4 from disk), optional scorecard-reset to v2.4.4, and consolidate Workstation_Operations TIER2 ledger
<!-- SESSION-HANDOFF:END -->

---

## 4. Repository File Tree (`AUTO-TREE`)

<!-- AUTO-TREE:START -->
```text
Repository: Engineering | HEAD SHA: 595049972ad7 | Tree Hash: a723ac6ca722
  memory/
  memory/Diagrams/
  memory/Diagrams/NEA_v2_Copilot_Execution_Flowchart.md
  memory/Diagrams/NEA_v2_Copilot_Execution_Flowchart.svg
  memory/Diagrams/Project_Ecosystem_Map.canvas
  memory/Directory/
  memory/Directory/Alchemical-3D_Decision_Router.md
  memory/Directory/Alchemical-3D_Directory.md
  memory/Directory/Alchemical-3D_memory_index.json
  memory/Directory/Directory_Index.md
  memory/Directory/governance_audit_log.jsonl
  memory/Directory/governance_seal.json
  memory/Directory/NetCom_Decision_Router.md
  memory/Directory/NetCom_Directory.md
  memory/Directory/NetCom_memory_index.json
  memory/Directory/Orin_Workstation_Decision_Router.md
  memory/Directory/Orin_Workstation_Directory.md
  memory/Directory/Orin_Workstation_memory_index.json
  memory/Profile/
  memory/Profile/Decision_Profile.md
  memory/Projects/
  memory/Projects/A3DP_Gantry_Assembly/
  memory/Projects/A3DP_Gantry_Assembly/Quarantine/
  memory/Projects/A3DP_Gantry_Assembly/A3DP_Gantry_Assembly.md
  memory/Projects/A3DP_Gantry_Assembly/A3DP_Gantry_Assembly_Hardware.md
  memory/Projects/A3DP_Gantry_Assembly/A3DP_Gantry_Assembly_Lessons_Learned.md
  memory/Projects/Alchemical_Web_Docs/
  memory/Projects/Alchemical_Web_Docs/Archive/
  memory/Projects/Alchemical_Web_Docs/Quarantine/
  memory/Projects/Alchemical_Web_Docs/Alchemical_Web_Docs.md
  memory/Projects/Alchemical_Web_Docs/Alchemical_Web_Docs_Lessons_Learned.md
  memory/Projects/Alchemical_Web_Docs/Alchemical_Web_Docs_Software.md
  memory/Projects/Alembic_Toolhead/
  memory/Projects/Alembic_Toolhead/Quarantine/
  memory/Projects/Alembic_Toolhead/Alembic_Toolhead.md
  memory/Projects/Alembic_Toolhead/Alembic_Toolhead_Hardware.md
  memory/Projects/Alembic_Toolhead/Alembic_Toolhead_Lessons_Learned.md
  memory/Projects/Brand/
  memory/Projects/Brand/Quarantine/
  memory/Projects/Brand/Brand.md
  memory/Projects/Brand/Brand_Lessons_Learned.md
  memory/Projects/Brand/Brand_Software.md
  memory/Projects/Extras/
  memory/Projects/Extras/Quarantine/
  memory/Projects/Extras/Extras.md
  memory/Projects/Extras/Extras_Hardware.md
  memory/Projects/Extras/Extras_Lessons_Learned.md
  memory/Projects/Homunculus/
  memory/Projects/Homunculus/Archive/
  memory/Projects/Homunculus/Quarantine/
  memory/Projects/Homunculus/Version_Logs/
  memory/Projects/Homunculus/Homunculus.md
  memory/Projects/Homunculus/Homunculus_Cleanroom_Promotion_Diff.md
  memory/Projects/Homunculus/Homunculus_Lessons_Learned.md
  memory/Projects/Homunculus/Homunculus_Memory_Weight_and_Scoring_Reference.md
  memory/Projects/Homunculus/Homunculus_Playbooks.md
  memory/Projects/Homunculus/Homunculus_Script_Skill_Interaction_Matrix.md
  memory/Projects/Homunculus/Homunculus_Software.md
  memory/Projects/Homunculus/Homunculus_Stateful_Memory_Deployment_Plan.md
  memory/Projects/Homunculus/Homunculus_Talking_Points.md
  memory/Projects/Homunculus/Homunculus_Teach_Me_Sandbox_Dossier.md
  memory/Projects/Homunculus/Homunculus_Version_and_Benchmark_Ledger.md
  memory/Projects/Maker-Tools/
  memory/Projects/Maker-Tools/Archive/
  memory/Projects/Maker-Tools/Quarantine/
  memory/Projects/Maker-Tools/Maker-Tools.md
  memory/Projects/Maker-Tools/Maker-Tools_Lessons_Learned.md
  memory/Projects/Maker-Tools/Maker-Tools_Software.md
  memory/Projects/NetCom_Engineering_Assistant/
  memory/Projects/NetCom_Engineering_Assistant/Quarantine/
  memory/Projects/NetCom_Engineering_Assistant/NetCom_Engineering_Assistant.md
  memory/Projects/NetCom_Engineering_Assistant/NetCom_Engineering_Assistant_Lessons_Learned.md
  memory/Projects/NetCom_Engineering_Assistant/NetCom_Engineering_Assistant_Module_Launchpad.md
  memory/Projects/NetCom_Engineering_Assistant/NetCom_Engineering_Assistant_Software.md
  memory/Projects/Organization_Profile/
  memory/Projects/Organization_Profile/Archive/
  memory/Projects/Organization_Profile/Quarantine/
  memory/Projects/Organization_Profile/Organization_Profile.md
  memory/Projects/Organization_Profile/Organization_Profile_Lessons_Learned.md
  memory/Projects/Organization_Profile/Organization_Profile_Software.md
  memory/Projects/Pestle_Rotational_Bowden/
  memory/Projects/Pestle_Rotational_Bowden/Quarantine/
  memory/Projects/Pestle_Rotational_Bowden/Pestle_Rotational_Bowden.md
  memory/Projects/Pestle_Rotational_Bowden/Pestle_Rotational_Bowden_Hardware.md
  memory/Projects/Pestle_Rotational_Bowden/Pestle_Rotational_Bowden_Lessons_Learned.md
  memory/Projects/Pneuma_Remote_Air/
  memory/Projects/Pneuma_Remote_Air/Archive/
  memory/Projects/Pneuma_Remote_Air/Quarantine/
  memory/Projects/Pneuma_Remote_Air/Pneuma_Remote_Air.md
  memory/Projects/Pneuma_Remote_Air/Pneuma_Remote_Air_Hardware.md
  memory/Projects/Pneuma_Remote_Air/Pneuma_Remote_Air_Lessons_Learned.md
  memory/Projects/Pneuma_Remote_Air/Pneuma_Remote_Air_Playbooks.md
  memory/Projects/Workstation_Operations/
  memory/Projects/Workstation_Operations/Archive/
  memory/Projects/Workstation_Operations/Quarantine/
  memory/Projects/Workstation_Operations/Workstation_Operations.md
  memory/Projects/Workstation_Operations/Workstation_Operations_Lessons_Learned.md
  memory/Projects/Workstation_Operations/Workstation_Operations_Playbooks.md
  memory/Projects/Workstation_Operations/Workstation_Operations_Software.md
  memory/Projects/Projects_Directory.base
  memory/Standards_and_Specs/
  memory/Standards_and_Specs/Alchemical_Ecosystem_Links_and_Brand.md
  memory/Standards_and_Specs/Alchemical_Style_and_Voice_Guide.md
  memory/Standards_and_Specs/Author_Voice_and_Cadence.md
  memory/Standards_and_Specs/Author_Voice_Cadence_Telemetry_Report.md
  memory/Standards_and_Specs/Author_Voice_Verbatim_Exemplars.md
  memory/Standards_and_Specs/Fasteners_and_Inserts.md
  memory/Standards_and_Specs/Governance_and_Constraint_Architecture.md
  memory/Standards_and_Specs/Image_and_Style_Rules.md
  memory/Standards_and_Specs/Standards_Index.md
  memory/Standards_and_Specs/Verifiable_Accuracy_and_Anti_Hallucination.md
  memory/Standards_and_Specs/Workspace_Gmail_MCP_Standard.md
  memory/Tasks/
  memory/Tasks/Alchemical-3D_Tasks.md
  memory/Tasks/NetCom_Tasks.md
  memory/Tasks/Orin_Workstation_Tasks.md
  memory/Templates/
  memory/Templates/Color_Palettes/
  memory/Templates/Color_Palettes/Alchemical3D_Color_Template.md
  memory/Templates/Color_Palettes/Alchemical3D_Light_Color_Template.md
  memory/Templates/Color_Palettes/Gruvbox_Local_Color_Template.md
  memory/Templates/Color_Palettes/NetCom_Corporate_Color_Template.md
  memory/AGENTS.md
  memory/README.md
  NEA_v2.2.3/
  NEA_v2.2.3/Copilot_Agents/
  NEA_v2.2.3/Copilot_Agents/NEA_BOM_Builder/
  NEA_v2.2.3/Copilot_Agents/NEA_BOM_Builder/Knowledge/
  NEA_v2.2.3/Copilot_Agents/NEA_BOM_Builder/Agent_Config.md
  NEA_v2.2.3/Copilot_Agents/NEA_BOM_Builder/Instructions.txt
  NEA_v2.2.3/Copilot_Agents/NEA_Catalog_Manager/
  NEA_v2.2.3/Copilot_Agents/NEA_Catalog_Manager/Knowledge/
  NEA_v2.2.3/Copilot_Agents/NEA_Catalog_Manager/Agent_Config.md
  NEA_v2.2.3/Copilot_Agents/NEA_Catalog_Manager/Instructions.txt
  NEA_v2.2.3/Copilot_Agents/NEA_CRL_Builder/
  NEA_v2.2.3/Copilot_Agents/NEA_CRL_Builder/Knowledge/
  NEA_v2.2.3/Copilot_Agents/NEA_CRL_Builder/Agent_Config.md
  NEA_v2.2.3/Copilot_Agents/NEA_CRL_Builder/Instructions.txt
  NEA_v2.2.3/Copilot_Agents/NEA_Package_Reviewer/
  NEA_v2.2.3/Copilot_Agents/NEA_Package_Reviewer/Knowledge/
  NEA_v2.2.3/Copilot_Agents/NEA_Package_Reviewer/Agent_Config.md
  NEA_v2.2.3/Copilot_Agents/NEA_Package_Reviewer/Instructions.txt
  NEA_v2.2.3/Copilot_Agents/NEA_Repair_Tool/
  NEA_v2.2.3/Copilot_Agents/NEA_Repair_Tool/Knowledge/
  NEA_v2.2.3/Copilot_Agents/NEA_Repair_Tool/Agent_Config.md
  NEA_v2.2.3/Copilot_Agents/NEA_Repair_Tool/Instructions.txt
  NEA_v2.2.3/Copilot_Agents/NEA_Timesheet_Consolidator/
  NEA_v2.2.3/Copilot_Agents/NEA_Timesheet_Consolidator/Knowledge/
  NEA_v2.2.3/Copilot_Agents/NEA_Timesheet_Consolidator/Agent_Config.md
  NEA_v2.2.3/Copilot_Agents/NEA_Timesheet_Consolidator/Instructions.txt
  NEA_v2.2.3/Copilot_Agents/Agent_Builder_Guide.md
  NEA_v2.2.3/Scripts/
  NEA_v2.2.3/Scripts/build_copilot_agents.py
  NEA_v2.2.3/Scripts/inspect_nea_workbooks.py
  NEA_v2.2.3/Scripts/package_nea_delivery.py
  NEA_v2.2.3/Skills/
  NEA_v2.2.3/Skills/nea-anti-hallucination/
  NEA_v2.2.3/Skills/nea-anti-hallucination/scripts/
  NEA_v2.2.3/Skills/nea-anti-hallucination/nea-anti-hallucination.zip
  NEA_v2.2.3/Skills/nea-anti-hallucination/SKILL.md
  ... (truncated at 160 entries)
```
<!-- AUTO-TREE:END -->

---

## 5. Quarantine Zone (Unverified Notes, Scratch Specs & Open `[TBD]`s)

> [!WARNING]
> **`[QUARANTINED — DO NOT CITE AS FACT]`**: Everything inside this section (and inside [`Quarantine/`](Quarantine/Quarantine_README.md)) is explicitly unverified holding data. Downstream documentation, BOMs, calculations, and `verify_claims.py` must **never** treat items in this section as verified ground truth until they are empirically verified and moved to Section 2 or the Domain Telemetry notes.

<!-- QUARANTINE-ZONE:START -->
- *(No unverified quarantine items — all workstation operational scripts verified in `scripts/`.)*
<!-- QUARANTINE-ZONE:END -->
