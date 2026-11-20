---
project: "Apprentice"
entity: "Alchemical-3D"
compartment: "public"
project_type: "software"
status: "active"
local_path: "../../Alchemical3D/Apprentice"
repo_head_sha: "4e7367cecf97"
tree_hash: "bf24de7ca6dc"
checkpoint_head_sha: "4e7367cecf97"
checkpoint_tree_hash: "bf24de7ca6dc"
checkpoint_worktree: "clean"
task_umbrella: "../../Tasks/Alchemical-3D_Tasks.md"
last_synced: "2026-11-19"
checkpoint_lessons_digest: "ce8fa102f668a8ee"
---

# Apprentice — Project Hub Dossier

> **Entity & Compartment Boundary**: `entity: Alchemical-3D` | `compartment: public` | `project_type: software`
> **Containment Rule**: Do not read, link, or borrow parameters from projects belonging to any entity other than `Alchemical-3D`.

---

## 1. Companion Notes & Project Navigation

| Artifact Role | File Link | Purpose |
| :--- | :--- | :--- |
| **Project Hub (`AUTO-TREE`)** | [`Apprentice.md`](Apprentice.md) | Canonical architecture overview, `SESSION-HANDOFF` kickstart state, `AUTO-TREE`, and Quarantine Zone. |
| **Software Telemetry (`_Software.md`)** | [`Apprentice_Software.md`](Apprentice_Software.md) | Verified runtime entrypoints, CLI flag contracts, schemas, and test receipts. |
| **Lessons Learned & ADRs** | [`Apprentice_Lessons_Learned.md`](Apprentice_Lessons_Learned.md) | Root-cause post-mortems (`Symptom -> Root Cause -> Permanent Guardrail`). |
| **Procedural Playbooks (`PB-xx`)** | [`Apprentice_Playbooks.md`](Apprentice_Playbooks.md) | Portable multi-step engineering workflows (`Trigger -> Ordered Procedure -> Verification Gate`). |
| **Unverified Quarantine Folder** | [`Quarantine/Quarantine_README.md`](Quarantine/Quarantine_README.md) | Holding zone for unverified notes/vendor quotes (`[QUARANTINED — DO NOT CITE AS FACT]`). |
| **Active Task Umbrella** | [`Alchemical-3D_Tasks.md`](../../Tasks/Alchemical-3D_Tasks.md) | Single-writer task tracker for `Alchemical-3D` (do not duplicate `- [ ]` checkboxes here). |

---

## 2. Executive Architecture & Locked Specifications

- **Core Objective**: Portable, pure Python `3.10+` stdlib local LLM sidecar plugin (`v3.0.0`) prioritizing `1. Reduce Quota Usage -> 2. Provide Accuracy Support -> 3. Help Models With Simple Tasks -> 4. Operate in Parallel (Agile-Sprint Architecture)` under `Homunculus`'s priority law (`1. Accuracy & Truth > 2. Efficiency -> 3. Data Safety > 4. Speed`) (`README.md#L5-L28`, `ARCHITECTURE.md#L5`).
- **Primary Repository Path**: `../../Alchemical3D/Apprentice`
- **Verified Key Parameters**:
  - **4 Orthogonal MCP Tools (`README.md#L44-L51`, `ARCHITECTURE.md#L9`)**: `apprentice_read`, `apprentice_draft`, `apprentice_review`, and `apprentice_runtime` (`<= 26` total schema parameters; fast `STANDARD` `deep=False` default across all work tools).
  - **Self-Calibrating Loopback Backends & Tiers (`README.md#L32-L40`, `ARCHITECTURE.md#L10,16`)**: Auto-discovers **LM Studio** (`127.0.0.1:1234`), **Ollama** (`:11434`), **llama.cpp** (`:8080`), or `APPRENTICE_API_URL`, scales chunk/output budgets dynamically from live `context_length` across **Tier S** (`1` slot, `deep=True` returns `handoff_to_cloud`), **Tier M** (`2` slots, `1` deep), and **Tier L** (`3` slots, `1` deep).
  - **Deterministic Grounding & Safety Firewalls (`ARCHITECTURE.md#L12,26-36`, `apprentice/safety.py#L1-L29`)**: Pure-Python `<1 ms` line-anchor/quote verifier (`verify_grounded_items`), `ast.parse`/smoke validation, `ZERO_ADHOC_CAD_PARSING`, loopback lock, secret file firewall, and anti-bloat ceilings (`<= 3,300` production Python lines across `8` modules in `apprentice/`, `plugin/rules/AGENTS.md <= 1,800` B, `plugin/skills/apprentice/SKILL.md <= 3,500` B).

---

## 3. Session Handoff & Multi-Session Kickstart (`SESSION-HANDOFF`)

> **Turn-1 Cold-Resume Rule**: When resuming `Apprentice` after a break, verify `Checkpoint Provenance` against the live repository (`sync_memory.py --memory-root <memory_root> --project Apprentice --kickstart`), surface the **Where We Stopped** summary and **Next Session Kickstart & Discussion Points** to the user, and confirm alignment before mutating files. Overwrite this block in place at session wrap-up (`--save-handoff`; supports detailed `500–800+ word` stopping context and `Project State Ledger` snapshots without growing the file over time).

<!-- SESSION-HANDOFF:START -->
- **Last Session Timestamp**: `2026-11-19`
- **Checkpoint Provenance**: `HEAD SHA: 4e7367cecf97` | `Tree Hash: bf24de7ca6dc` | `Worktree: clean` | `Last Verification: SBX-20261119_202741-2e0c02e1`
- **Where We Stopped (Verified State & Context)**:
  Apprentice v3.1 Round 1 committed locally (4e7367c): adaptive prefill servo, partial-safe reads, real-line review grounding, Condition GPU gate, compaction/drift/Second-Eyes hooks with precommit_seen bypass, and user-approved 3,600-L cap (3,520/3,600 L).
- **Active Project State Ledger & Blockers**: None
- **Next Session Kickstart & Discussion Points**:
  1. Restart MCP sidecar / open fresh session to load v3.1 runtime in memory
  2. Run live 5A fast-vs-frontier host-model comparison against v2.6.0 benchmark receipts
- **Open Discussion / Alignment Questions**: Keep v3.1 ceiling at 3,600 L; alert user before raising any cap again
<!-- SESSION-HANDOFF:END -->

---

## 4. Repository File Tree (`AUTO-TREE`)

<!-- AUTO-TREE:START -->
```text
Repository: Apprentice | HEAD SHA: 4e7367cecf97 | Tree Hash: bf24de7ca6dc
  apprentice/
  apprentice/__init__.py
  apprentice/__main__.py
  apprentice/backends.py
  apprentice/core.py
  apprentice/grounding.py
  apprentice/hook.py
  apprentice/mcp_stdio.py
  apprentice/planner.py
  apprentice/safety.py
  apprentice/sprint.py
  plugin/
  plugin/rules/
  plugin/rules/AGENTS.md
  plugin/skills/
  plugin/skills/apprentice/
  plugin/skills/apprentice/SKILL.md
  plugin/hooks.json.template
  plugin/mcp_config.json.template
  plugin/plugin.json
  scripts/
  scripts/stress_test_v3.py
  tests/
  tests/test_backends_and_planner.py
  tests/test_grounding.py
  tests/test_mcp_and_hook.py
  tests/test_safety.py
  tests/test_sprint_and_core.py
  .gitignore
  ARCHITECTURE.md
  install.ps1
  install.sh
  LICENSE.md
  README.md
```
<!-- AUTO-TREE:END -->

---

## 5. Quarantine Zone (Unverified Notes, Scratch Specs & Open `[TBD]`s)

> [!WARNING]
> **`[QUARANTINED — DO NOT CITE AS FACT]`**: Everything inside this section (and inside [`Quarantine/`](Quarantine/Quarantine_README.md)) is explicitly unverified holding data. Downstream documentation, BOMs, calculations, and `verify_claims.py` must **never** treat items in this section as verified ground truth until they are empirically verified and moved to Section 2 or the Domain Telemetry notes.

<!-- QUARANTINE-ZONE:START -->
- `[TBD: initial_unverified_notes]` — Add raw vendor quotes, preliminary dimensions, or unverified hypotheses here prior to verification.
<!-- QUARANTINE-ZONE:END -->
