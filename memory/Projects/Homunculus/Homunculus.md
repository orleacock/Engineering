---
project: "Homunculus"
entity: "Alchemical-3D"
compartment: "cleanroom"
project_type: "software"
status: "v0.1.0 Development Baseline"
local_path: "/home/orin/Projects/Alchemical3D/Homunculus"
repo_head_sha: "f9c732fa7df3"
tree_hash: "b635c91e293d"
checkpoint_head_sha: "f9c732fa7df3"
checkpoint_tree_hash: "b635c91e293d"
checkpoint_worktree: "clean"
task_umbrella: "../../Tasks/Alchemical-3D_Tasks.md"
last_synced: "2026-11-11"
checkpoint_lessons_digest: "6d55adccaa10d93c"
---

## 🧭 Homunculus Companion Notes & Project Navigation

| Artifact Role | File Link | Purpose |
| :--- | :--- | :--- |
| **Project Hub (`AUTO-TREE`)** | [`Homunculus.md`](Homunculus.md) | Canonical architecture overview, `SESSION-HANDOFF`, `AUTO-TREE`, and `[TBD]` Ledger. |
| **Software Telemetry** | [`Homunculus_Software.md`](Homunculus_Software.md) | Runtime entrypoints, CLI flags, public symbols, and JSON schemas. |
| **Lessons Learned & Post-Mortems** | [`Homunculus_Lessons_Learned.md`](Homunculus_Lessons_Learned.md) | Root-cause post-mortems (`Symptom -> Root Cause -> Permanent Guardrail`). |
| **Clean-Room Promotion Diff** | [`Homunculus_Cleanroom_Promotion_Diff.md`](Homunculus_Cleanroom_Promotion_Diff.md) | Authoritative file-by-file validation & promotion manifest (`Parent Workstation` vs. `Clean-Room`). |
| **Stateful Memory Deployment Plan** | [`Homunculus_Stateful_Memory_Deployment_Plan.md`](Homunculus_Stateful_Memory_Deployment_Plan.md) | Locked 5-Sprint architecture, `TIER0`–`TIER5` gravity rules, pitfall guards, and per-sprint audit gates. |
| **Script & Skill Interaction Matrix** | [`Homunculus_Script_Skill_Interaction_Matrix.md`](Homunculus_Script_Skill_Interaction_Matrix.md) | **Non-authoritative** maintainer lookup table mapping what each skill/script touches (`authoritative: false`). |
| **Version & Benchmark Ledger** | [`Homunculus_Version_and_Benchmark_Ledger.md`](Homunculus_Version_and_Benchmark_Ledger.md) | **Non-authoritative** `v0.Y.Z` version history & standardized side-by-side benchmark scorecards (`authoritative: false`). |
| **Project Templates** | [`Templates/`](Templates/) | Project-specific deliverable templates. |
| **Unverified Quarantine Zone** | [`Quarantine/Quarantine_README.md`](Quarantine/Quarantine_README.md) | Holding zone for unverified notes (`[QUARANTINED — DO NOT CITE AS FACT]`). |
| **Active Task Umbrella** | [`Alchemical-3D_Tasks.md`](../../Tasks/Alchemical-3D_Tasks.md#Homunculus) | Single-writer task tracker for `Alchemical-3D` (zero duplicate checkboxes in hub). |

---

# 🧬 Homunculus (Portable AI Co-Engineering & Verification Framework)

Part of the [`README.md`](../../README.md)

## 🔒 Concept & Design Philosophy ("Why")
- **Core Identity & Domain-General Engineering Mission (`Truth > Comfort`):** `Homunculus` is a portable, **AI-agnostic engineering framework** carrying hardened lessons learned, dual-mode project memory, deterministic claim/math fact-checking, token-lean subagent orchestration, and publication-grade visual documentation tooling into a ready-to-ship package. It is engineered for **all day-to-day engineering and design disciplines** (software, mechanical, electrical/structured cabling, firmware, and systems—not restricted to maker-space projects) under the foundational mandate of **Truth and Accuracy over comfort**.
- **Governing 4-Tier Priority Law (`1. Accuracy & Truth -> 2. Efficiency -> 3. Data Safety -> 4. Speed`):** Feature selection and runtime architecture strictly prioritize deterministic accuracy first, token/context efficiency second, multi-compartment data safety third, and execution speed fourth—achieving speed *through* first-pass verified accuracy and cross-OS zero-install portability rather than trading away truth. Modules requiring user corpus setup time (`addons/author-voice-cadence/`) ship as dormant **Zero-Install Drop-In Add-Ons** under `Homunculus/addons/` so the core `skills/` tree works on Day 0.
- **Open-Source Release (`Apache-2.0` — Zero Cost to Entry) + Voluntary Support (`Ko-fi`) & Commercial Consulting:** Released as an **open-source project (`Apache-2.0`)** on GitHub (`https://github.com/Alchemical-3D/Homunculus`) with **zero cost to entry** so engineers, developers, and enterprise teams can adopt and audit the full framework immediately:
  - **Open-Source Core & Extension SDK (`Apache-2.0`):** Ships 100% readable, editable Python + Markdown source code permitting unlimited personal, open-source, commercial, employer, and client engineering work with mandatory `Alchemical-3D` attribution on redistribution (`LICENSE.md`) and explicit patent grant protection.
  - **Sustainability & Services (`Ko-fi` + Consulting & Workshops):** Paired with voluntary community support via [**Ko-fi (`ko-fi.com/alchemical3d`)**](https://ko-fi.com/alchemical3d) and commercial **1-on-1 Workspace Setup Consulting, Custom Domain Skill Engineering, and Live Team Workshops** (`we@alchemical3d.net` / Alchemical-3D Discord).
- **Dual-Mode Memory (`Headless` vs. `Obsidian` + `Standalone Zero-Vault Cold-Start`):**
  - **Standalone Zero-Vault & Zero-History Doctrine:** `Homunculus` is engineered to operate 100% standalone when deployed on an external workstation **without** any access to our `memory/` Vault, our project names (`Pneuma`, `Alembic`, `NEA`), or our prior conversation history. Every rule, skill, and CLI oracle operates directly on any arbitrary repository (`--repo <path>`), dynamically discovers project entities (`verify_claims.py`) and CAD stems (`inspect_hardware_ecosystem.py`) without hardcoded project lists, and can bootstrap a fresh project or standalone memory folder on demand (`sync_memory.py --init-memory` / `--init-project <Name> --repo-path <Path>`).
  - **Path A — Headless Memory (`CLI / Pure Markdown / SharePoint-Safe`):** Runs structured Markdown dossiers, single-writer task queues, `AUTO-TREE` snapshots, and `[TBD]` quarantine without requiring Obsidian—skipping Obsidian-only UI surfaces (`.obsidian/graph.json`, `.base` views, `> **Active Task Queue**: Tracked in `...` *(Single-Writer Task Umbrella)*.` GUI dependencies).
  - **Path B — Obsidian Visual-Brain Memory:** Full Vault experience adding synced `.base` portfolio tables, `graph.json` semantic coloring, and live `> **Active Task Queue**: Tracked in `...` *(Single-Writer Task Umbrella)*.` transclusions on user preference.
  - **Visual Studio Sequencing (`Homunculus` First $\rightarrow$ Local Backport Later):** Baseline `.svg`-first `Visual Studio` (`render_diagram.py`, opt-in `300 DPI` `--png`, showcase cards, and `--export-canvas`) ships in both Headless and Obsidian modes; net-new Visual Studio advancements (`Auto-Layout`, `Electrical/Pinout`, `Sequence/State`) are treated as **Priority 2** when needed, built and tested in `Homunculus` first, and **backported to the local native workstation (``<legacy_builder_workspace>``) afterward with lessons learned**.
- **Dual Deployment (`Optional Installer` + `Zero-Install Drop-In`) Across OS & Enterprise Locked-Down Stations (`1. Linux -> 2. macOS -> 3. Windows`):**
  - **Single Unified Cross-OS Archive:** Zero hardcoded user/account paths (`pathlib`, dynamic workspace root discovery).
  - **Track 1 — Automated Installer (`install.sh` / `install.ps1`):** One-command adapter wiring where local permissions allow.
  - **Track 2 — Zero-Install "Drop-In & Point" Mode (`Locked-Down Corporate IT Safe`):** Full manual file-drop layout and `HOMUNCULUS_START_HERE.md` pointer instructions requiring **zero** admin privileges, **zero** script installation, **zero** symlinks, and **zero** `pip` packages.
- **Multi-Client Primary Build + Post-Core `MS365 / Copilot` Packaging Assessment:** Phase 1–4 builds and validates the primary package for **Universal `AGENTS.md`**, **Antigravity/Gemini**, **Claude Code**, **Claude Cowork**, and **Cursor** first; **Microsoft 365 Copilot / GitHub Copilot** compatibility (including whether Copilot requires a separate lighter package or dedicated manifest/instruction bundle) is explicitly sequenced **after** the primary adapters and core engine are built and proven.
- **Anti-Bloat, Deferred Side-Effects & User-Readiness Discipline (`rules/co-engineering-partner.md` + `pre-commit-gate`):** Enforces a generic, client-agnostic execution restraint across all sessions: (1) **Zero Mid-Task Churn** (never re-render `.svg`/`.png` visuals, rebuild memory trees/indexes, or run heavy end-of-pass audits after intermediate edits—batch derived updates into `pre-commit-gate`), (2) **Explicit User-Readiness Gate** (never push to a remote server, publish artifacts, or mutate shared state before the user explicitly confirms readiness in the current turn), and (3) **Turn-Budget Restraint** (execute only the tool calls required for the active turn's goal; log side discoveries as `[ISOLATED]` rather than launching unsolicited side quests).
- **Synergistic Skill Builder & Permission-Based Cleanup Protocol (`skills/skill-architect` + `scripts/audit_skill_hygiene.py`):** Ships a unified two-mode meta-skill that prevents skill rot and wasted turns across the lifecycle:
  - **Mode 1 — Synergistic Skill Builder (`Create / Extend`):** Runs a pre-creation overlap check against existing `rules/` and `skills/` (preferring extending an existing skill over spawning a redundant one), automatically wires new skills into Dual-Mode Memory (`AUTO-TREE` + single-writer `Tasks/*.md`), Truth Oracles (`verify_claims.py` `[TBD]`), and `pre-commit-gate`, and enforces delta-only instructions (zero repetition of always-on rules).
  - **Mode 2 — Permission-Based Cleanup Protocol (`Audit / Consolidate`):** Audits user-created skills, rules, and scripts for trigger collisions, duplicated rule text, and turn-wasting patterns (`ls`/`find` wandering, mid-edit hooks/syncs) while respecting `Chesterton's Fence`—emitting tiered, opt-in advisory proposals (`[KEEP — DOMAIN SPECIFIC]`, `[SUGGESTED TRIM — ALREADY IN CORE RULES]`, `[CANDIDATE MERGE]`, `[TURN-WASTE HAZARD]`) rather than authoritarian auto-deletions. Executed on a **Two-Touch Cadence**: (1) up-front parent-system validation and design, and (2) a full pre-release cleanup pass across `Homunculus`'s own release skills at the `Phase 3 -> Phase 4` boundary.
- **Parent-First Validation & Clean-Room Downstream Architecture (``<legacy_builder_workspace>`` $\leftrightarrow$ `Homunculus` via [`Homunculus_Lessons_Learned`](Homunculus_Lessons_Learned.md)):** Core co-engineering rules, anti-bloat gates, and `skill-architect` (`+ audit_skill_hygiene.py`) are hardened and dogfooded on the parent workstation (``<legacy_builder_workspace>``) first so real-world weaknesses are captured in [`Homunculus_Lessons_Learned`](Homunculus_Lessons_Learned.md) before porting into `/home/orin/Projects/Alchemical3D/Homunculus` (which operates under strict zero-PII / zero-path sanitization via `audit_data_boundary.py` + `scripts/audit_portability.py`), while standalone `Homunculus` innovations (declarative `homunculus_safety.json` engine, cross-OS/drop-in adapters, and Priority 2 Visual Studio upgrades) feed back into ``<legacy_builder_workspace>`` post-validation.

## 📍 Repository & File Inventory
- **Local Path:** `/home/orin/Projects/Alchemical3D/Homunculus` (Consolidated Single-Source Clean-Room Git Repository on the workstation — `0` duplicate copies; tagged `v0.1.0` at `31aa0cb0a918` across **`102` clean-room files**; verified via `SBX-20261110_143655-1ecf0fa7` `Controls: 4/4 passed`, `+faults: 2/2 caught`, `49/49` unit tests OK across `7` suites, `0` portability/boundary/hygiene defects)
- **GitHub Remote:** `git@github-alchemical:Alchemical-3D/Homunculus.git` (`https://github.com/Alchemical-3D/Homunculus` — Open-Source `Apache-2.0` Core + Ko-fi & Commercial Consulting)
- **Living Documentation & Reference:** `README.md`, `HOMUNCULUS_START_HERE.md` (Zero-Install Drop-In entry point), `LICENSE.md` (`Apache-2.0`), `docs/Capabilities_and_Architecture_Guide.md`, `docs/Commands_and_Prompts_Reference.md`, `docs/Developer_Data_Safety_Guidelines.md`, `docs/Release_and_Community_Guide.md`, `docs/FAQ.md`, `docs/Memory_Setup_README.md`, `docs/Quick_Start_and_Setup_Guide.md`, `install.sh` + `install.ps1` (Track 1 installers), `.gitignore`
- **Clean-Room Module Directories (`102` Files):** `rules/` (3 `always_on` rules: `co-engineering-partner.md`, `data-and-credential-safety.md`, `verifiable-accuracy.md`), `skills/` (`9` core skills: `skill-architect`, `project-memory`, `claim-verification`, `subagent-orchestrator`, `engineering-sandbox`, `visual-studio`, `doc-and-card-studio`, `pre-commit-gate`, `teach-me`), `addons/` (`addons/author-voice-cadence` and `addons/hardware-cad-inspector` Drop-In add-ons), `adapters/` (`agents_md/AGENTS.md`, `antigravity/`, `claude_code/CLAUDE.md`, `claude_cowork/`, `cursor/`), `hooks/`, `templates/` (`memory/`, `diagrams/`, `hooks/`, `ignore/`, `community_sdk/`), `scripts/` (`homunculus_paths.py`, `script_contracts.json`, `audit_portability.py`, `audit_data_boundary.py`, `build_adapters.py`), `tests/` (`test_foundation.py`, `test_data_safety.py`, `test_adapters.py`, `test_project_memory.py`, `test_claim_verification.py`, `test_core_skills.py`, `test_teach_me.py` — `49/49` tests OK across `7` suites)
- **CAD & Firmware Directories:** _None (Pure Software / AI Skill & Tooling Suite)_
- **Standards Applied:** [`Verifiable_Accuracy_and_Anti_Hallucination`](../../Standards_and_Specs/Verifiable_Accuracy_and_Anti_Hallucination.md), `Author_Voice_and_Cadence`, `Image_and_Style_Rules`, `Subagent_and_Memory_Architecture`, `Alchemical3D_Color_Template`, [`Homunculus_Talking_Points`](Homunculus_Talking_Points.md), [`Homunculus_Lessons_Learned`](Homunculus_Lessons_Learned.md), `Homunculus_Construction_and_Migration_Manual`

<!-- AUTO-TREE:START -->
```text
Repository: Homunculus | HEAD SHA: f9c732fa7df3 | Tree Hash: b635c91e293d
  adapters/
  adapters/agents_md/
  adapters/agents_md/AGENTS.md
  adapters/agents_md/README.md
  adapters/antigravity/
  adapters/antigravity/hooks.json
  adapters/antigravity/README.md
  adapters/claude_code/
  adapters/claude_code/CLAUDE.md
  adapters/claude_code/README.md
  adapters/claude_code/settings.json
  adapters/claude_cowork/
  adapters/claude_cowork/README.md
  adapters/cursor/
  adapters/cursor/rules/
  adapters/cursor/rules/homunculus-co-engineering-partner.mdc
  adapters/cursor/rules/homunculus-data-and-credential-safety.mdc
  adapters/cursor/rules/homunculus-verifiable-accuracy.mdc
  adapters/cursor/README.md
  addons/
  addons/author-voice-cadence/
  addons/author-voice-cadence/corpus_inbox/
  addons/author-voice-cadence/scripts/
  addons/author-voice-cadence/scripts/extract_voice_cadence.py
  addons/author-voice-cadence/templates/
  addons/author-voice-cadence/templates/Cadence_Report_Template.md
  addons/author-voice-cadence/templates/Voice_Profile_Template.md
  addons/author-voice-cadence/SKILL.md
  addons/hardware-cad-inspector/
  addons/hardware-cad-inspector/scripts/
  addons/hardware-cad-inspector/scripts/inspect_hardware_ecosystem.py
  addons/hardware-cad-inspector/SKILL.md
  docs/
  docs/Capabilities_and_Architecture_Guide.md
  docs/Commands_and_Prompts_Reference.md
  docs/Developer_Data_Safety_Guidelines.md
  docs/FAQ.md
  docs/Memory_Setup_README.md
  docs/Quick_Start_and_Setup_Guide.md
  docs/Release_and_Community_Guide.md
  hooks/
  hooks/hooks.json
  rules/
  rules/co-engineering-partner.md
  rules/data-and-credential-safety.md
  rules/verifiable-accuracy.md
  scripts/
  scripts/audit_data_boundary.py
  scripts/audit_portability.py
  scripts/build_adapters.py
  scripts/homunculus_paths.py
  scripts/script_contracts.json
  skills/
  skills/claim-verification/
  skills/claim-verification/scripts/
  skills/claim-verification/scripts/verify_claims.py
  skills/claim-verification/SKILL.md
  skills/doc-and-card-studio/
  skills/doc-and-card-studio/references/
  skills/doc-and-card-studio/references/doc_templates.md
  skills/doc-and-card-studio/scripts/
  skills/doc-and-card-studio/scripts/audit_repo_docs.py
  skills/doc-and-card-studio/scripts/format_image.py
  skills/doc-and-card-studio/SKILL.md
  skills/engineering-sandbox/
  skills/engineering-sandbox/references/
  skills/engineering-sandbox/references/frame_playbooks.md
  skills/engineering-sandbox/scripts/
  skills/engineering-sandbox/scripts/sandbox_runner.py
  skills/engineering-sandbox/SKILL.md
  skills/pre-commit-gate/
  skills/pre-commit-gate/SKILL.md
  skills/project-memory/
  skills/project-memory/scripts/
  skills/project-memory/scripts/sync_memory.py
  skills/project-memory/SKILL.md
  skills/skill-architect/
  skills/skill-architect/scripts/
  skills/skill-architect/scripts/audit_skill_hygiene.py
  skills/skill-architect/SKILL.md
  skills/subagent-orchestrator/
  skills/subagent-orchestrator/references/
  skills/subagent-orchestrator/references/oracle_cli_cheatsheet.md
  skills/subagent-orchestrator/references/orchestration_playbooks.md
  skills/subagent-orchestrator/SKILL.md
  skills/teach-me/
  skills/teach-me/references/
  skills/teach-me/references/brief_authoring_playbook.md
  skills/teach-me/scripts/
  skills/teach-me/scripts/teach_brief.py
  skills/teach-me/SKILL.md
  skills/visual-studio/
  skills/visual-studio/scripts/
  skills/visual-studio/scripts/render_diagram.py
  skills/visual-studio/SKILL.md
  templates/
  templates/community_sdk/
  templates/community_sdk/addon_skeleton/
  templates/community_sdk/addon_skeleton/SKILL.md
  templates/community_sdk/README.md
  templates/diagrams/
  templates/diagrams/Diagram_Blueprints/
  templates/diagrams/Diagram_Blueprints/Column_DataFlow_Blueprint.md
  templates/diagrams/Diagram_Blueprints/Engineering_Comparison_Card_Blueprint.md
  templates/diagrams/Diagram_Blueprints/Hardware_Pinout_and_Pneumatic_Blueprint.md
  templates/diagrams/Diagram_Blueprints/Layered_Architecture_Blueprint.md
  templates/diagrams/Diagram_Blueprints/Spatial_Topology_Blueprint.md
  templates/diagrams/Diagram_Palettes.json
  templates/hooks/
  templates/hooks/post-worktree-sync.sh
  templates/hooks/pre-commit.sh
  templates/hooks/pre-push.sh
  templates/ignore/
  templates/ignore/.claudeignore
  templates/ignore/.cursorignore
  templates/ignore/.geminiignore
  templates/memory/
  templates/memory/AGENTS.md
  templates/memory/Decision_Profile.md
  templates/memory/Global_Standards_Index.md
  templates/memory/Memory_Map_README.md
  templates/memory/Project_Hardware.md
  templates/memory/Project_Hub.md
  templates/memory/Project_Lessons_Learned.md
  templates/memory/Project_Playbooks.md
  templates/memory/Project_Software.md
  templates/memory/Quarantine_Note.md
  templates/memory/Task_Umbrella.md
  templates/homunculus_safety.example.json
  tests/
  tests/test_adapters.py
  tests/test_claim_verification.py
  tests/test_core_skills.py
  tests/test_data_safety.py
  tests/test_foundation.py
  tests/test_project_memory.py
  tests/test_teach_me.py
  .gitignore
  HOMUNCULUS_START_HERE.md
  install.ps1
  install.sh
  LICENSE.md
  README.md
```
<!-- AUTO-TREE:END -->

## ⚠️ Paramount Architectural & Decontamination Hazards
- **Zero Personalization / Entity Leakage Invariant:** Never copy `/home/orin` filesystem paths, `orleacock` personal account handles, independent enterprise data (`NetCom` / `NEA`), personal Discord archives (`corpus_inbox/`), personal stylometric tables, or vendor affiliate parameters (`?affp=6182`, `dt_id=Alchemical3D`) into `/home/orin/Projects/Alchemical3D/Homunculus`.
- **License Boundary Invariant (`Apache-2.0` Open-Source + Attribution):** Maintain the permissive OSI **`Apache-2.0` License** (`LICENSE.md`) across the entire `Homunculus` repository (`rules/`, `skills/`, `adapters/`, `scripts/`, `templates/`, `docs/`) so individual engineers and enterprise teams can adopt `Homunculus` with zero cost to entry (driving Ko-fi support and commercial consulting/workshop engagements) while legally requiring `Alchemical-3D` copyright attribution on any redistribution.
- **No Silent Degradation of Bound Files:** Never drop always-on rule guardrails (`co-engineering-partner`, `verifiable-accuracy`) or safety gates (`verify_claims.py` `SHA-256` receipts, copy-on-write sandbox containment) merely to simplify packaging—engineer explicit rule, recommended-rule, or adapter bindings per target client.

## 📐 Verified Specs & Key Content (Locked `v1.0` Product Matrix)
1. **Primary Client Adapter Matrix (`adapters/` — Phase 1–4 Core, `MS365 / Copilot` Assessed Post-Core):**
   - **Primary `v1.0` Build (`Phases 1–4`):** Out-of-the-box bindings for **Universal `AGENTS.md`**, **Antigravity / Gemini CLI**, **Claude Code** (`CLAUDE.md` + `.claude/`), **Claude Cowork** (designated local working folder + `SKILL.md` folder/zip upload), and **Cursor** (`.cursor/rules/*.mdc`), plus client context-egress ignore templates (`.cursorignore`, `.claudeignore`, `.geminiignore`) and locked-down workstation "Drop-In & Point" guides (`Phase 2B`).
   - **Post-Core Assessment (`Phase 5`):** Evaluate and package **Microsoft 365 Copilot / Copilot** compatibility (whether as a dedicated `Homunculus Lite` package or adapter bundle) **after** the primary clients and core engine are built and verified.
2. **Developer Data Safety Platform & Agnostic Core Rules (`rules/`, `docs/` & `scripts/` — `Phase 2A` Built in `Homunculus` First $\rightarrow$ Local Derivation):**
   - **5-Pillar Developer Data Safety Guidelines & Boundary Engine:** Ships `docs/Developer_Data_Safety_Guidelines.md`, client-agnostic `rules/data-and-credential-safety.md`, and declarative `scripts/audit_data_boundary.py` (`homunculus_safety.json` multi-compartment schema + zero-config default protection covering: (1) zero secret read/echo/context-window egress, (2) declarative compartment/remote/author boundaries, (3) UTF-8/16/32 + `.step`/`.stl`/`.svg`/`.xlsx`/`.ipynb` metadata decontamination, (4) untrusted external input/MCP prompt-injection quarantine, and (5) destructive command & `--no-verify` hook-bypass locks). Built in `Homunculus` first so the local workstation's `data-and-credential-safety` layer derives directly from it.
   - **Co-Engineering, Anti-Bloat & Verifiable Accuracy Core Rules:** Client-agnostic `rules/co-engineering-partner.md` (anti-sycophancy, load-bearing foundation checks, Project State Ledger, blast-radius gates, **Anti-Bloat / Deferred Side-Effects batching**, **Explicit User-Readiness Gates** for external pushes/mutations, and **Skill Synergy & Permission-Based Cleanup Governance**) and `rules/verifiable-accuracy.md` (`Accuracy > Efficiency`, closed-world literals, `[TBD: <var>]` abstention, dimensional `[CALC: ...]` verification).
3. **Deterministic Claim Verifier, Skill Architect & Pre-Commit Gate (`skills/` & `scripts/` — Locked):**
   - `claim-verification` (`verify_claims.py` `VRF-<12hex>` `SHA-256` receipts, `#L` verbatim slice checks, `[TBD]` ledger quarantine + Zero-CLI structured claim-audit table mode for restricted M365 environments) paired with `pre-commit-gate` (`X -> Y -> Z` pre-commit sequence) and `audit_portability.py`.
   - **`skill-architect` (`skills/skill-architect/SKILL.md` + `scripts/audit_skill_hygiene.py`):** Unified two-mode skill providing **Mode 1: Synergistic Skill Builder** (pre-creation overlap check, automatic Dual-Mode Memory / Truth Oracle / `pre-commit-gate` wiring, and delta-only authoring) and **Mode 2: Permission-Based Cleanup Protocol** (context-respecting, non-destructive redundancy and turn-waste auditor emitting `[KEEP]`, `[SUGGESTED TRIM]`, `[CANDIDATE MERGE]`, and `[TURN-WASTE HAZARD]` proposals)—validated on the parent workstation first and executed as a pre-release cleanup pass at the `Phase 3 -> Phase 4` boundary.
4. **Subagent Orchestration & Cross-OS Engineering Sandbox (`skills/` & `adapters/` — Locked):** Turn-1 parallel scatter-gather swarms (`AUTO-TREE` zero-`ls`/`find` routing, Anchored Evidence Packets with `0` double-reads, `lite`/`fast`/`deep` tier routing) paired with the **Cross-OS `engineering-sandbox`** (`Linux` `bwrap`+`btrfs` CoW $\rightarrow$ `macOS` APFS/worktree $\rightarrow$ `Windows` `git worktree`/temp-copy fallback + `+faults` adversarial injection).
5. **Dual-Mode Engineering Memory (`skills/project-memory/`, `templates/memory/`, `docs/Memory_Setup_README.md` — Completed in `Phase 3A`):** User-selectable **Headless CLI/Markdown Mode** vs. **Obsidian Visual-Brain Mode** (`--convert-mode`), featuring: (a) **Separate Hardware & Software Telemetry Functions** (`--sync-hardware` $\rightarrow$ `<Project>_Hardware.md` vs. `--sync-software` $\rightarrow$ `<Project>_Software.md`), (b) **Multi-Customer / Peer-Entity Containment Firewall** (`entity:` frontmatter tag + `CROSS_ENTITY_CONTAMINATION` audit), (c) **First-Class Quarantine Zone** (`Projects/<Project>/Quarantine/` + `<!-- QUARANTINE-ZONE:START/END -->`), and (d) **Project Deliverable Templates** (`Projects/<Project>/Templates/` + `--create-project-template`).
6. **Visual Studio (`skills/visual-studio` — Baseline Completed in `Phase 3B`, Expansions as Priority 2 $\rightarrow$ Local Backport):**
   - **Priority 1 Baseline:** Clean-room `.svg`-default `render_diagram.py` (`~0.05s`, `--strict` collision/overflow gate, `templates/diagrams/Diagram_Palettes.json` clean-room slate/cyan `#38BDF8`/`#0284C7` tokens, opt-in `300 DPI` `--png`, and `--github-card`) active across both Headless and Obsidian modes.
   - **Priority 2 Advancements (Built in `Homunculus` When Needed $\rightarrow$ Backported Locally After Testing):** **Auto-Layout Engine**, **Electrical/Harness/Pinout Schematics**, and **Sequence/State-Machine/Process Flowcharts**.
7. **Domain Telemetry Oracles, Generic Doc/Card Formatter & End-User Command Deck (`skills/`, `docs/` — Completed in `Phase 3B`):** Pure-stdlib `inspect_hardware_ecosystem.py` (`STEP/STL` CAD geometry + `.cfg` firmware pins + `--json-out` + `entity:`-preserving `--sync-manifest`), lazy-PIL `format_image.py` + `audit_repo_docs.py` (`--skip-image-check` + pure-stdlib PNG header fallback), and `docs/Commands_and_Prompts_Reference.md`.
8. **Side-Loaded Drop-In Add-Ons (`addons/` — Completed in `Phase 3B`) & Strictly Excluded (`Clean-Room Firewall`):**
   - *Side-Loaded Drop-In Add-On (`addons/author-voice-cadence/`):* Ships dormant in `addons/author-voice-cadence/` (`SKILL.md`, `templates/`, and clean-room `scripts/extract_voice_cadence.py` with `--tier-config`) so installers can activate it via Zero-Install Drop-In once they gather their personal writing corpus.
   - *Strictly Excluded:* Zero `/home/orin` paths, `orleacock` / `orin@alchemical3d.net` identifiers, personal Discord corpus/stylometrics, Alchemical-3D affiliate tags (`?affp=6182`, `dt_id=Alchemical3D`), `NEA` / `NetCom` assets, or private `gmail_mcp` / SSH configs.
9. **First Post-`v1.0.0` Expansion Priority (`Expansion Priority #1` — Staged Outside Clean Room Until Deployment):**
   - **Universal Engineering & Technical Learning Engine (`skills/teach-me/` — Multi-Domain `Brief+` & Throw-Away Subagent Tutor):** Core mechanic (`/teach-me about "<Subject X>" impact on "<Subject Y>"`) engineered across **all engineering disciplines** (mechanical/CAD `.step`/`.stl`, kinematics, pneumatics, thermal dissipation, electrical/PCBs, stepper motors/drivers, CAN bus, power rails, structured cabling/RF, firmware/Klipper `.cfg`, and software systems).
   - **Architecture Locks (`2026-11-06`):**
     1. **Core Active Skill (`skills/teach-me/SKILL.md` + `scripts/teach_brief.py`):** Ships as a first-class core skill once promoted.
     2. **Non-Consumed Sibling Storage (`<memory_root>/../study_briefs/`):** Placed adjacent to `memory/` and shielded by a 3-layer anti-consumption firewall (`sync_memory.py` exclusion, `.cursorignore`/`.claudeignore`/`.geminiignore` rules, and `status: "UNPROMOTED_STUDY_BRIEF"` frontmatter) so study items are never consumed as authoritative specs without explicit `--promote` validation (`verify_claims.py --strict-provenance`).
     3. **`Brief+` Context-Tailored Format:** Concise first-principles mental model + causal coupling/math (`[CALC: ...]`) + trade-off envelope + `1–2` verified overlap examples grounded directly in the active engineering context (`file#Lstart-Lend`, CAD/PCB/motor/config telemetry, `VRF-<12hex>` receipt).
     4. **Throw-Away Subagent Isolation, Smart Whole-Word Naming & Solid-Line Datasheet Card (`SBX-20261106_145314-2fa5c587`):** Runs 100% of research, file/CAD/spec reads, and `verify_claims.py` validation inside a disposable subagent, generates clean whole-word `<Subject>_on_<Impact>` filenames (`--slug`, `--rename-clean`), and relays a pixel-aligned Solid-Line Datasheet Card (`┏━━ 🎓 TEACH-ME // BRIEF+ ... ━━┓` + clickable `▸`/`↳` fields + `┗━━ ... ━━┛` rail) to the active window (`0` context contamination).

## 🔗 Companion Projects & Kinematic / System Links
- [`Brand`](../../Projects/Brand/Brand.md) — Supplies official Alchemical-3D vector marks (`Alchemical-3D-Badge-Gradient-PRIMARY-Alchemical-3D-Logo-Gradient-PRIMARY-Transparent-Background.svg`) and Dark Slate palette tokens (`Alchemical3D_Color_Template`).
- [`Maker-Tools`](../../Projects/Maker-Tools/Maker-Tools.md) & [`Alchemical_Web_Docs`](../../Projects/Alchemical_Web_Docs/Alchemical_Web_Docs.md) — Ecosystem companion portals (`we@alchemical3d.net`, `https://discord.gg/aE49DW2xXe`, `https://ko-fi.com/alchemical3d`) connecting open-source GitHub releases, community Discord channels, and consulting services.
- **Bidirectional R&D & Lessons-Learned Loop (``<legacy_builder_workspace>`` $\leftrightarrow$ [`Homunculus_Lessons_Learned`](Homunculus_Lessons_Learned.md) $\leftrightarrow$ `Homunculus`):** Co-engineering rules, anti-bloat gates, and `skill-architect` (`+ audit_skill_hygiene.py`) are dogfooded on the parent workstation (``<legacy_builder_workspace>``) first with findings logged in [`Homunculus_Lessons_Learned`](Homunculus_Lessons_Learned.md), then ported into `Homunculus`; conversely, newly engineered `Homunculus` advancements (declarative `homunculus_safety.json` boundary scanner, cross-OS/drop-in patterns, M365/Cowork adapters, and Priority 2 Visual Studio upgrades) are built and sandbox-validated in `Homunculus` first, then backported into ``<legacy_builder_workspace>`` via `Orin_Workstation_Tasks.md`.

## 🔍 Provenance Status & Open [TBD] / [CONFLICT] Ledger
> [!NOTE]
> Figures inside this ledger are quarantined by `verify_claims.py` and are **not** treated as authorized source truth until resolved.

- **Git & Provenance Baseline:** `Phases 1–4E`, `skills/teach-me/` (4-trigger complexity router + throw-away subagent containment), `Combination 1` `Directory/` freshness spine, `LL-027` 2-Tier Single-Source Rule Diet, and `LL-028` `Pairing D` AST navigation maps complete on disk (`97` byte-identical files in `/home/orin/Projects/Alchemical3D/Homunculus` and `/home/orin/Projects/Engineering/Homunculus`, verified via `audit_portability.py` `0` violations, `audit_data_boundary.py --compartment cleanroom --worktree` `0` violations, `audit_skill_hygiene.py --strict-structure` `0` defects, `31/31` unit tests OK, `Compare-Light` `SBX-20261108_095230-f6afc09d` `PASS`, and `OS Dry-Run (+faults)` `SBX-20261108_094940-96ebde4f` `Controls: 3/3 passed`, `+faults: 2/2 caught` under `Orin <109475365+Orin-Alchemical-3D@users.noreply.github.com>`, remote `git@github-alchemical:Alchemical-3D/Homunculus.git`).
- **Open `[TBD]` & `[CONFLICT]` Items (`open_tbd_count: 0`):** `None` *(All `v1.0` architectural, client-adapter, MS365/Copilot/Cowork compatibility, dual-deployment, `Apache-2.0` open-source licensing, and Visual Studio priority decisions locked).*

## 🚀 Session Handoff & Multi-Session Kickstart (`SESSION-HANDOFF`)
<!-- SESSION-HANDOFF:START -->
- **Last Session Timestamp**: `2026-11-11`
- **Checkpoint Provenance**: `HEAD SHA: f9c732fa7df3` | `Tree Hash: b635c91e293d` | `Worktree: clean` | `Last Verification: SBX-20261111_082207-2d5504ac, VRF-f899f601bef3, 53/53 unit tests OK, HEAD f9c732f`
- **Where We Stopped (Verified State & Context)**:
  Completed and committed Homunculus memory retrieval & authoring advisory upgrade (f9c732f): 17_Combo_C9_HeldT0 recall, Option A TIER0 Two-Lane + --kickstart TIER0 capsules, strict N1 0.0 numeric weight, v1.2 .cache/*_scoring_vectors.json sidecar, <=1,800-token 4-pass Anti-Bombing Budgeter (Tweak 2.1), active-section-only HOT_MEMORY_BLOAT_CEILING, and Check #7c non-blocking [BARE_NUMERIC_SHORTHAND_NOUN_MISSING] advisory; logged LL-044 + SUBSYSTEM-INVARIANTS and re-sealed governance.
- **Active Project State Ledger & Blockers**: None
- **Next Session Kickstart & Discussion Points**:
  1. Confirm git push to origin/main if ready
  2. Optionally align scripts/benchmark_homunculus.py (ME01 tier0_active_matches + ME05 <=1800-tok ceiling) before tagging v0.3.0 and taking a Btrfs RAID snapshot
- **Open Discussion / Alignment Questions**: Whether to push f9c732f to origin/main and/or cut the official v0.3.0 tag + RAID snapshot
<!-- SESSION-HANDOFF:END -->

## 🎯 Active Tasks
*(Transcluded live from `### Homunculus` in [`Alchemical3D_Tasks`](../../Tasks/Alchemical-3D_Tasks.md) (`Tasks/Alchemical3D_Tasks.md#Homunculus`) — edit checkboxes in one place only)*

> **Active Task Queue**: Tracked in [`Alchemical3D_Tasks`](../../Tasks/Alchemical-3D_Tasks.md#Homunculus) *(Single-Writer Task Umbrella)*.
