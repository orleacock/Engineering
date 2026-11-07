---
project: "{{PROJECT}}"
entity: "{{ENTITY}}"
compartment: "{{COMPARTMENT}}"
project_type: "{{PROJECT_TYPE}}"
status: "active"
local_path: "{{LOCAL_PATH}}"
repo_head_sha: "{{REPO_HEAD_SHA}}"
tree_hash: "{{TREE_HASH}}"
checkpoint_head_sha: "{{REPO_HEAD_SHA}}"
checkpoint_tree_hash: "{{TREE_HASH}}"
checkpoint_worktree: "clean"
task_umbrella: "../../Tasks/{{ENTITY_SAFE}}_Tasks.md"
last_synced: "{{DATE}}"
---

# {{PROJECT}} — Project Hub Dossier

> **Entity & Compartment Boundary**: `entity: {{ENTITY}}` | `compartment: {{COMPARTMENT}}` | `project_type: {{PROJECT_TYPE}}`
> **Containment Rule**: Do not read, link, or borrow parameters from projects belonging to any entity other than `{{ENTITY}}`.

---

## 1. Companion Notes & Project Navigation

| Artifact Role | File Link | Purpose |
| :--- | :--- | :--- |
| **Project Hub (`AUTO-TREE`)** | [`{{PROJECT}}.md`]({{PROJECT}}.md) | Canonical architecture overview, `SESSION-HANDOFF` kickstart state, `AUTO-TREE`, and Quarantine Zone. |
{{TELEMETRY_ROWS}}| **Lessons Learned & ADRs** | [`{{PROJECT}}_Lessons_Learned.md`]({{PROJECT}}_Lessons_Learned.md) | Root-cause post-mortems (`Symptom -> Root Cause -> Permanent Guardrail`). |
| **Project Templates** | [`Templates/`](Templates/) | Project-specific deliverable templates (BOMs, quotes, test cards, checklists). |
| **Unverified Quarantine Folder** | [`Quarantine/Quarantine_README.md`](Quarantine/Quarantine_README.md) | Holding zone for unverified notes/vendor quotes (`[QUARANTINED — DO NOT CITE AS FACT]`). |
| **Active Task Umbrella** | [`{{ENTITY_SAFE}}_Tasks.md`](../../Tasks/{{ENTITY_SAFE}}_Tasks.md) | Single-writer task tracker for `{{ENTITY}}` (do not duplicate `- [ ]` checkboxes here). |

---

## 2. Executive Architecture & Locked Specifications

- **Core Objective**: `[TBD: project_core_objective]`
- **Primary Repository Path**: `{{LOCAL_PATH}}`
- **Verified Key Parameters**:
  - Populate verified specifications here with exact source citations (`path#Lstart-Lend`) after running domain telemetry inspection.

---

## 3. Session Handoff & Multi-Session Kickstart (`SESSION-HANDOFF`)

> **Turn-1 Cold-Resume Rule**: When resuming `{{PROJECT}}` after a break, verify `Checkpoint Provenance` against the live repository (`sync_memory.py --memory-root <memory_root> --project {{PROJECT}} --kickstart`), surface the **Where We Stopped** summary and **Next Session Kickstart & Discussion Points** to the user, and confirm alignment before mutating files. Overwrite this block in place at session wrap-up (`--save-handoff`; supports detailed `500–800+ word` stopping context and `Project State Ledger` snapshots without growing the file over time).

<!-- SESSION-HANDOFF:START -->
- **Last Session Timestamp**: `{{DATE}}`
- **Checkpoint Provenance**: `HEAD SHA: {{REPO_HEAD_SHA}}` | `Tree Hash: {{TREE_HASH}}` | `Worktree: clean` | `Last Verification: [TBD: receipt_or_test_id]`
- **Where We Stopped (Verified State & Context)**:
  - Initialized `{{PROJECT}}` memory dossier (`entity: {{ENTITY}}`, `compartment: {{COMPARTMENT}}`, `project_type: {{PROJECT_TYPE}}`).
- **Active Project State Ledger & Blockers**:
  - `[OPEN-01]`: Complete initial domain telemetry sync (`--sync-hardware` / `--sync-software`) and populate verified specifications in Section 2.
- **Next Session Kickstart & Discussion Points**:
  1. Run `sync_memory.py --memory-root <memory_root> --project {{PROJECT}} --kickstart` to verify repository state matches checkpoint `{{REPO_HEAD_SHA}}`.
  2. Review open items in [`{{ENTITY_SAFE}}_Tasks.md`](../../Tasks/{{ENTITY_SAFE}}_Tasks.md) and confirm the next implementation milestone.
<!-- SESSION-HANDOFF:END -->

---

## 4. Project Deliverable Templates (`Projects/{{PROJECT}}/Templates/`)

> **AI Co-Engineering Trigger (`Project-Template Prompt`)**: When onboarding `{{PROJECT}}` or whenever a recurring deliverable pattern is identified (e.g., BOM schedule, customer quote sheet, test report, assembly card), ask the user: *"Would you like to save a canonical template for this deliverable in `Projects/{{PROJECT}}/Templates/` (or promote it to global `Templates/`)?"*

- Registered Project Templates: *(None registered yet — place `.md` templates in [`Templates/`](Templates/))*

---

## 5. Repository File Tree (`AUTO-TREE`)

<!-- AUTO-TREE:START -->
```text
Repository path: {{LOCAL_PATH}}
HEAD SHA: {{REPO_HEAD_SHA}}
(Run `sync_memory.py --sync-tree --project {{PROJECT}}` to refresh)
```
<!-- AUTO-TREE:END -->

---

## 6. Quarantine Zone (Unverified Notes, Scratch Specs & Open `[TBD]`s)

> [!WARNING]
> **`[QUARANTINED — DO NOT CITE AS FACT]`**: Everything inside this section (and inside [`Quarantine/`](Quarantine/Quarantine_README.md)) is explicitly unverified holding data. Downstream documentation, BOMs, calculations, and `verify_claims.py` must **never** treat items in this section as verified ground truth until they are empirically verified and moved to Section 2 or the Domain Telemetry notes.

<!-- QUARANTINE-ZONE:START -->
- `[TBD: initial_unverified_notes]` — Add raw vendor quotes, preliminary dimensions, or unverified hypotheses here prior to verification.
<!-- QUARANTINE-ZONE:END -->
