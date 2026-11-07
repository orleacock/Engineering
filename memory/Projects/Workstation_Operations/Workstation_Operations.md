---
project: "Workstation_Operations"
entity: "Orin_Workstation"
compartment: "private"
project_type: "software"
status: "active"
local_path: "../scripts"
repo_head_sha: "UNTRACKED"
tree_hash: "56fe0934991e"
checkpoint_head_sha: "UNTRACKED"
checkpoint_tree_hash: "56fe0934991e"
checkpoint_worktree: "untracked"
task_umbrella: "../../Tasks/Orin_Workstation_Tasks.md"
last_synced: "2026-11-06"
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
| **Project Templates** | [`Templates/`](Templates/) | Project-specific deliverable templates (BOMs, quotes, test cards, checklists). |
| **Unverified Quarantine Folder** | [`Quarantine/Quarantine_README.md`](Quarantine/Quarantine_README.md) | Holding zone for unverified notes/vendor quotes (`[QUARANTINED — DO NOT CITE AS FACT]`). |
| **Active Task Umbrella** | [`Orin_Workstation_Tasks.md`](../../Tasks/Orin_Workstation_Tasks.md) | Single-writer task tracker for `Orin_Workstation` (do not duplicate `- [ ]` checkboxes here). |

---

## 2. Executive Architecture & Locked Specifications

- **Core Objective**: Workstation bootstrap automation (`bootstrap_workstation.sh`), multi-compartment Git pre-commit/pre-push firewall hooks (`git_pre_commit_boundary.sh`, `pre_push_engineering_guard.sh`), parent umbrella config sync (`umbrella_configs/Projects.homunculus.json`), and Dual-Account Gmail MCP server (`gmail_mcp/gmail_mcp_server.py`) for the local engineering workstation (`/home/orin/Projects/Engineering`).
- **Primary Repository Path**: `../scripts`
- **Verified Key Parameters**:
  - **Workstation Bootstrap**: [`bootstrap_workstation.sh`](../../../scripts/bootstrap_workstation.sh) wires `Homunculus/rules/*.md`, `Homunculus/skills/*`, `Homunculus/addons/*`, `memory/` in `~/.config/obsidian/obsidian.json`, parent `/home/orin/Projects/{.homunculus.json,.geminiignore}`, and `.git/hooks/{pre-commit,pre-push}` across `/home/orin/Projects/Engineering` and `/home/orin/Projects/Alchemical3D/*`.
  - **Multi-Compartment Boundary Guard**: [`git_pre_commit_boundary.sh`](../../../scripts/git_pre_commit_boundary.sh) and [`pre_push_engineering_guard.sh`](../../../scripts/pre_push_engineering_guard.sh) execute `Homunculus/scripts/audit_data_boundary.py` prior to commits and pushes across `private`, `public`, and `cleanroom` compartments, paired with directory-scoped Git identities (`~/.gitconfig` `[includeIf]`), SSH host aliases (`~/.ssh/config`: `github-orleacock` and `github-alchemical`), and offline Raid snapshots (`/run/media/orin/Raid/Backup Documents/`).
  - **Dual-Account Gmail MCP Server**: [`gmail_mcp/gmail_mcp_server.py`](../../../scripts/gmail_mcp/gmail_mcp_server.py) provides OAuth 2.0 `Read + Create Drafts` access (`gmail.readonly` + `gmail.compose`) with `visibility_radar` and `verified_send_as_aliases` enforcement (`personal` `orleacock@gmail.com` + `alchemical` `orin@alchemical3d.net` / `we@alchemical3d.net`).

---

## 3. Session Handoff & Multi-Session Kickstart (`SESSION-HANDOFF`)

> **Turn-1 Cold-Resume Rule**: When resuming `Workstation_Operations` after a break, verify `Checkpoint Provenance` against the live repository (`sync_memory.py --memory-root <memory_root> --project Workstation_Operations --kickstart`), surface the **Where We Stopped** summary and **Next Session Kickstart & Discussion Points** to the user, and confirm alignment before mutating files. Overwrite this block in place at session wrap-up (`--save-handoff`; supports detailed `500–800+ word` stopping context and `Project State Ledger` snapshots without growing the file over time).

<!-- SESSION-HANDOFF:START -->
- **Last Session Timestamp**: `2026-11-06`
- **Checkpoint Provenance**: `HEAD SHA: UNTRACKED` | `Tree Hash: 56fe0934991e` | `Worktree: untracked` | `Last Verification: SBX-20261106_202239-49ab2028 / VRF-e0deb8ddff1e`
- **Where We Stopped (Verified State & Context)**:
  Flushed 36 MB legacy pre-migration Git history and rebuilt clean single-root private umbrella orleacock/Engineering (Homunculus 9-skill engine + Dual-Mode Memory + NEA v2.2.3 + parent ~/Projects umbrella config wiring + study_briefs quarantine + consolidated pre_push_engineering_guard.sh).
- **Active Project State Ledger & Blockers**: NONE
- **Next Session Kickstart & Discussion Points**:
  1. Resume active engineering development across indexed projects
  2. Promote Expansion Priority #1 (teach-me) and functional test suite into Clean-Room Alchemical3D/Homunculus when explicitly authorized
<!-- SESSION-HANDOFF:END -->

---

## 4. Project Deliverable Templates (`Projects/Workstation_Operations/Templates/`)

> **AI Co-Engineering Trigger (`Project-Template Prompt`)**: When onboarding `Workstation_Operations` or whenever a recurring deliverable pattern is identified (e.g., BOM schedule, customer quote sheet, test report, assembly card), ask the user: *"Would you like to save a canonical template for this deliverable in `Projects/Workstation_Operations/Templates/` (or promote it to global `Templates/`)?"*

- Registered Project Templates: *(None registered yet — place `.md` templates in [`Templates/`](Templates/))*

---

## 5. Repository File Tree (`AUTO-TREE`)

<!-- AUTO-TREE:START -->
```text
Repository: scripts | HEAD SHA: UNTRACKED | Tree Hash: 56fe0934991e
  bootstrap_workstation.sh
  git_pre_commit_boundary.sh
  pre_push_engineering_guard.sh
  gmail_mcp/
  gmail_mcp/README.md
  gmail_mcp/gmail_mcp_server.py
  gmail_mcp/requirements.txt
  gmail_mcp/gmail-workspace-assistant/
  gmail_mcp/gmail-workspace-assistant/SKILL.md
  umbrella_configs/
  umbrella_configs/Projects.homunculus.json
```
<!-- AUTO-TREE:END -->

---

## 6. Quarantine Zone (Unverified Notes, Scratch Specs & Open `[TBD]`s)

> [!WARNING]
> **`[QUARANTINED — DO NOT CITE AS FACT]`**: Everything inside this section (and inside [`Quarantine/`](Quarantine/Quarantine_README.md)) is explicitly unverified holding data. Downstream documentation, BOMs, calculations, and `verify_claims.py` must **never** treat items in this section as verified ground truth until they are empirically verified and moved to Section 2 or the Domain Telemetry notes.

<!-- QUARANTINE-ZONE:START -->
- *(No unverified quarantine items — all workstation operational scripts verified in `scripts/`.)*
<!-- QUARANTINE-ZONE:END -->
