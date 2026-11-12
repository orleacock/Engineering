---
project: "Homunculus"
entity: "Alchemical-3D"
compartment: "cleanroom"
project_type: "software"
status: "v0.3.0 Ring-0 Sudo & Memory Gateway Ready"
local_path: "/home/orin/Projects/Alchemical3D/Homunculus"
repo_head_sha: "51453f63a444"
tree_hash: "2ca5ab86e3ec"
checkpoint_head_sha: "51453f63a444"
checkpoint_tree_hash: "2ca5ab86e3ec"
checkpoint_worktree: "clean"
task_umbrella: "../../Tasks/Alchemical-3D_Tasks.md"
last_synced: "2026-11-12"
checkpoint_lessons_digest: "b156cd25a08a6ae7"
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
| **`teach-me` Sandbox Condition Dossier** | [`Homunculus_Teach_Me_Sandbox_Dossier.md`](Homunculus_Teach_Me_Sandbox_Dossier.md) | **Non-authoritative** staged empirical probes & `TM-COND-01`–`TM-COND-11` findings for the standalone `teach-me` session (`authoritative: false`). |
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
- **Local Path:** `/home/orin/Projects/Alchemical3D/Homunculus` (Consolidated Single-Source Clean-Room Git Repository on the workstation — `0` duplicate copies; `v0.3.0` Ring-0 Sudo & `MEMORY_SDK_V1` Gateway architecture across **`108` clean-room files**; verified across `8` `unittest` suites (`62` tests) in [`Homunculus_Software.md`](Homunculus_Software.md) with `0` portability, boundary, or hygiene defects)
- **GitHub Remote:** `git@github-alchemical:Alchemical-3D/Homunculus.git` (`https://github.com/Alchemical-3D/Homunculus` — Open-Source `Apache-2.0` Core + Ko-fi & Commercial Consulting)
- **Living Documentation & Reference:** `README.md`, `HOMUNCULUS_START_HERE.md` (Zero-Install Drop-In entry point), `LICENSE.md` (`Apache-2.0`), `docs/Capabilities_and_Architecture_Guide.md`, `docs/Commands_and_Prompts_Reference.md`, `docs/Developer_Data_Safety_Guidelines.md`, `docs/Release_and_Community_Guide.md`, `docs/FAQ.md`, `docs/Memory_Setup_README.md`, `docs/Quick_Start_and_Setup_Guide.md`, `install.sh` + `install.ps1` (Track 1 installers), `.gitignore`
- **Clean-Room Module Directories (`108` Files):** `rules/` (3 `always_on` rules: `co-engineering-partner.md`, `data-and-credential-safety.md`, `verifiable-accuracy.md`), `skills/` (`9` core skills across `Ring 0` kernel skills + `Ring 1` consumer skills, plus `skills/skill-architect/references/ring0_sudo_protocol.md`), `addons/` (`addons/author-voice-cadence` and `addons/hardware-cad-inspector` `Ring 2` Drop-In add-ons), `adapters/` (`agents_md/AGENTS.md`, `antigravity/`, `claude_code/CLAUDE.md`, `claude_cowork/`, `cursor/`), `hooks/`, `templates/` (`memory/`, `diagrams/`, `hooks/`, `ignore/`, `community_sdk/Addon_Memory_Integration_Playbook.md`), `scripts/` (`homunculus_paths.py`, `memory_gateway.py`, `kernel_seal.json`, `script_contracts.json`, `audit_portability.py`, `audit_data_boundary.py`, `build_adapters.py`), `tests/` (`test_foundation.py`, `test_data_safety.py`, `test_adapters.py`, `test_project_memory.py`, `test_claim_verification.py`, `test_core_skills.py`, `test_teach_me.py`, `test_v030_memory_platform.py`)
- **CAD & Firmware Directories:** _None (Pure Software / AI Skill & Tooling Suite)_
- **Standards Applied:** [`Governance_and_Constraint_Architecture`](../../Standards_and_Specs/Governance_and_Constraint_Architecture.md), [`Verifiable_Accuracy_and_Anti_Hallucination`](../../Standards_and_Specs/Verifiable_Accuracy_and_Anti_Hallucination.md), [`Author_Voice_and_Cadence`](../../Standards_and_Specs/Author_Voice_and_Cadence.md), [`Image_and_Style_Rules`](../../Standards_and_Specs/Image_and_Style_Rules.md), [`Alchemical3D_Color_Template`](../../Templates/Color_Palettes/Alchemical3D_Color_Template.md), [`Homunculus_Talking_Points`](Homunculus_Talking_Points.md), [`Homunculus_Lessons_Learned`](Homunculus_Lessons_Learned.md)

<!-- AUTO-TREE:START -->
```text
Repository: Homunculus | HEAD SHA: 51453f63a444 | Tree Hash: 2ca5ab86e3ec
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
  scripts/kernel_seal.json
  scripts/memory_gateway.py
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
  skills/skill-architect/references/
  skills/skill-architect/references/ring0_sudo_protocol.md
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
  templates/community_sdk/Addon_Memory_Integration_Playbook.md
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
  tests/test_v030_memory_platform.py
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
5. **Dual-Mode Engineering Memory (`skills/project-memory/`, `templates/memory/`, `docs/Memory_Setup_README.md` — Completed in `Phase 3A` & Stateful Memory `v1.1`):** User-selectable **Headless CLI/Markdown Mode** vs. **Obsidian Visual-Brain Mode** (`--convert-mode`), featuring: (a) **Zero-Prompt Turn-1 Read-Only Task Triage** (`AUTO-ROLLUP` checkpoints + handoff pulses in `Tasks/<Entity>_Tasks.md` via multi-level `.homunculus.json` lookup) alongside `--kickstart` for active project work, (b) **Separate Hardware & Software Telemetry Functions** (`--sync-hardware` $\rightarrow$ `<Project>_Hardware.md` vs. `--sync-software` $\rightarrow$ `<Project>_Software.md`), (c) **Multi-Customer / Peer-Entity Containment Firewall & `0444` Governance Seal** (`entity:` frontmatter tag + `CROSS_ENTITY_CONTAMINATION` + `Directory/governance_seal.json`), (d) **First-Class Quarantine Zone** (`Projects/<Project>/Quarantine/` + `<!-- QUARANTINE-ZONE:START/END -->`), and (e) **Sparse Local Overrides & Lazy Project Deliverable Templates** (`--eject-templates` + on-demand `--create-project-template`).
6. **Visual Studio (`skills/visual-studio` — Baseline Completed in `Phase 3B`, Expansions as Priority 2 $\rightarrow$ Local Backport):**
   - **Priority 1 Baseline:** Clean-room `.svg`-default `render_diagram.py` (`~0.05s`, `--strict` collision/overflow gate, `templates/diagrams/Diagram_Palettes.json` clean-room slate/cyan `#38BDF8`/`#0284C7` tokens, opt-in `300 DPI` `--png`, and `--github-card`) active across both Headless and Obsidian modes.
   - **Priority 2 Advancements (Built in `Homunculus` When Needed $\rightarrow$ Backported Locally After Testing):** **Auto-Layout Engine**, **Electrical/Harness/Pinout Schematics**, and **Sequence/State-Machine/Process Flowcharts**.
7. **Domain Telemetry Oracles, Generic Doc/Card Formatter & End-User Command Deck (`skills/`, `docs/` — Completed in `Phase 3B`):** Pure-stdlib `inspect_hardware_ecosystem.py` (`STEP/STL` CAD geometry + `.cfg` firmware pins + `--json-out` + `entity:`-preserving `--sync-manifest`), lazy-PIL `format_image.py` + `audit_repo_docs.py` (`--skip-image-check` + pure-stdlib PNG header fallback), and `docs/Commands_and_Prompts_Reference.md`.
8. **Side-Loaded Drop-In Add-Ons (`addons/` — Completed in `Phase 3B`) & Strictly Excluded (`Clean-Room Firewall`):**
   - *Side-Loaded Drop-In Add-Ons (`addons/author-voice-cadence/` & `addons/hardware-cad-inspector/`):* Ship dormant under `addons/` (`author-voice-cadence` with configurable `--tier-config` in `extract_voice_cadence.py`, and `hardware-cad-inspector` with `inspect_hardware_ecosystem.py`) so installers can activate them via Zero-Install Drop-In when needed.
   - *Strictly Excluded:* Zero `/home/orin` paths, `orleacock` / `orin@alchemical3d.net` identifiers, personal Discord corpus/stylometrics, Alchemical-3D affiliate tags (`?affp=6182`, `dt_id=Alchemical3D`), `NEA` / `NetCom` assets, or private `gmail_mcp` / SSH configs.
9. **Promoted Core Skill #9 — Universal Engineering & Technical Learning Engine (`skills/teach-me/` — Multi-Domain `Brief+` & Throw-Away Subagent Tutor; Standalone Hardening Queued in [`Homunculus_Teach_Me_Sandbox_Dossier.md`](Homunculus_Teach_Me_Sandbox_Dossier.md)):**
   - **Core Mechanic:** `/teach-me about "<Subject X>" impact on "<Subject Y>"` engineered across **all engineering disciplines** (mechanical/CAD `.step`/`.stl`, kinematics, pneumatics, thermal dissipation, electrical/PCBs, stepper motors/drivers, CAN bus, power rails, structured cabling/RF, firmware/Klipper `.cfg`, and software systems).
   - **Architecture Locks (`2026-11-06` + Queued `TM-COND-01`–`TM-COND-11` Pass):**
     1. **Core Active Skill (`skills/teach-me/SKILL.md` + `scripts/teach_brief.py`):** Promoted as Core Skill #9 inside Clean-Room `Homunculus/skills/teach-me/`.
     2. **Non-Consumed Sibling Storage (`<memory_root>/../study_briefs/`):** Placed adjacent to `memory/` and shielded by a 3-layer anti-consumption firewall (`sync_memory.py` exclusion, `.cursorignore`/`.claudeignore`/`.geminiignore` rules, and `status: "UNPROMOTED_STUDY_BRIEF"` frontmatter) so study items are never consumed as authoritative specs without explicit `--promote` validation (`verify_claims.py --strict-provenance`).
     3. **`Brief+` Context-Tailored Format:** Concise first-principles mental model + causal coupling/math (`[CALC: ...]`) + trade-off envelope + `1–2` verified overlap examples grounded directly in the active engineering context (`file#Lstart-Lend`, CAD/PCB/motor/config telemetry, `VRF-<12hex>` receipt).
     4. **Throw-Away Subagent Isolation, Smart Whole-Word Naming & Solid-Line Datasheet Card (`SBX-20261106_145314-2fa5c587`):** Runs 100% of research, file/CAD/spec reads, and `verify_claims.py` validation inside a disposable subagent, generates clean whole-word `<Subject>_on_<Impact>` filenames (`--slug`, `--rename-clean`), and relays a pixel-aligned Solid-Line Datasheet Card (`┏━━ 🎓 TEACH-ME // BRIEF+ ... ━━┓` + clickable `▸`/`↳` fields + `┗━━ ... ━━┛` rail) to the active window (`0` context contamination).

## 🔗 Companion Projects & Kinematic / System Links
- [`Brand`](../../Projects/Brand/Brand.md) — Supplies official Alchemical-3D vector marks (`Alchemical-3D-Badge-Gradient-PRIMARY-Alchemical-3D-Logo-Gradient-PRIMARY-Transparent-Background.svg`) and Dark Slate palette tokens (`Alchemical3D_Color_Template`).
- [`Maker-Tools`](../../Projects/Maker-Tools/Maker-Tools.md) & [`Alchemical_Web_Docs`](../../Projects/Alchemical_Web_Docs/Alchemical_Web_Docs.md) — Ecosystem companion portals (`we@alchemical3d.net`, `https://discord.gg/aE49DW2xXe`, `https://ko-fi.com/alchemical3d`) connecting open-source GitHub releases, community Discord channels, and consulting services.
- **Bidirectional R&D & Lessons-Learned Loop (``<legacy_builder_workspace>`` $\leftrightarrow$ [`Homunculus_Lessons_Learned`](Homunculus_Lessons_Learned.md) $\leftrightarrow$ `Homunculus`):** Co-engineering rules, anti-bloat gates, and `skill-architect` (`+ audit_skill_hygiene.py`) are dogfooded on the parent workstation first with findings logged in [`Homunculus_Lessons_Learned`](Homunculus_Lessons_Learned.md), while `/home/orin/Projects/Alchemical3D/Homunculus` serves as the single authoritative engine repository on disk (`0` duplicate copies).

## 🔍 Provenance Status & Open [TBD] / [CONFLICT] Ledger
> [!NOTE]
> Figures inside this ledger are quarantined by `verify_claims.py` and are **not** treated as authorized source truth until resolved.

- **Git & Provenance Baseline:** Consolidated single-source Clean-Room repository at `/home/orin/Projects/Alchemical3D/Homunculus` (`0` duplicate `Engineering/Homunculus` copies; baseline tag `v0.1.0` at `31aa0cb0a918`; Stateful Memory `v1.1` `TIER0`–`TIER5` + `0444` governance seal; Vector 3 zero-shell Turn-1 read-only task triage; sparse `<memory_root>/Templates/` override model; verified via `audit_portability.py`, `audit_data_boundary.py --compartment cleanroom --worktree`, `audit_skill_hygiene.py --strict-structure`, and full `unittest` suite under `Orin <109475365+Orin-Alchemical-3D@users.noreply.github.com>`, remote `git@github-alchemical:Alchemical-3D/Homunculus.git`).
- **Open `[TBD]` & `[CONFLICT]` Items (`open_tbd_count: 0`):** `None` *(All `v1.0` architectural, client-adapter, MS365/Copilot/Cowork compatibility, dual-deployment, `Apache-2.0` open-source licensing, and Visual Studio priority decisions locked).*

## 🚀 Session Handoff & Multi-Session Kickstart (`SESSION-HANDOFF`)
<!-- SESSION-HANDOFF:START -->
- **Last Session Timestamp**: `2026-11-12`
- **Checkpoint Provenance**: `HEAD SHA: 51453f63a444` | `Tree Hash: 2ca5ab86e3ec` | `Worktree: clean` | `Last Verification: Homunculus@51453f6 | Engineering@93077d5+ | SBX-20261112_114304-eb3256c8 | Sealed:39/Leased:0`
# Homunculus `v0.3.1` & Teach-Me Vision Alignment — Complete Session Handoff Package

## Mandatory Resume Gate (Read First When Picking Up This Handoff)

> [!WARNING]
> **MANDATORY FIRST ACTION ON RESUME: START IMMEDIATELY WITH A UNIFIED REVIEW & PLANNING SESSION (`0` CHANGES BEFORE PLAN LOCK)**
> When this handoff is picked back up, **do NOT make any code, rule, skill, adapter, or memory edits—and do NOT unlock `Ring 0` or `Ring 1`**. Begin immediately with a structured **Review & Planning Session** with the engineer to validate and sequence **both** quarantined audits against live `Homunculus` (`51453f6`) structure and developer intent:
> 1. **Claude Sonnet Memory Retrieval & Weight-Balance Audit (`Rev 3`)**: [Memory_Retrieval_Weight_Balance_Audit.md](file:///home/orin/.gemini/antigravity-cli/brain/e41eebf7-644b-43e6-99e9-e36580ebbce0/Memory_Retrieval_Weight_Balance_Audit.md) + [scratch/](file:///home/orin/.gemini/antigravity-cli/brain/e41eebf7-644b-43e6-99e9-e36580ebbce0/scratch/) (`e41eebf7-644b-43e6-99e9-e36580ebbce0`) $\rightarrow$ Quarantined copy [2026-11-12_Claude_Sonnet_Memory_Retrieval_Weight_Balance_Audit_Rev3.md](file:///home/orin/Projects/Engineering/memory/Projects/Homunculus/Quarantine/2026-11-12_Claude_Sonnet_Memory_Retrieval_Weight_Balance_Audit_Rev3.md).
> 2. **Gemini Carbon Security & Performance Audit (*"Opencode Auth Login Instructions"*)**: [homunculus_security_and_performance_audit.md](file:///home/orin/.gemini/antigravity-cli/brain/b4e4ead6-10c1-48ef-aaa7-83bf3c8c1892/homunculus_security_and_performance_audit.md) + [security_cli_telemetry.md](file:///home/orin/.gemini/antigravity-cli/brain/b4e4ead6-10c1-48ef-aaa7-83bf3c8c1892/scratch/security_cli_telemetry.md) & [bench_security_cli.py](file:///home/orin/.gemini/antigravity-cli/brain/b4e4ead6-10c1-48ef-aaa7-83bf3c8c1892/scratch/bench_security_cli.py) (`b4e4ead6-10c1-48ef-aaa7-83bf3c8c1892`) $\rightarrow$ Quarantined copy [2026-11-12_Gemini_Carbon_Security_and_Performance_Audit.md](file:///home/orin/Projects/Engineering/memory/Projects/Homunculus/Quarantine/2026-11-12_Gemini_Carbon_Security_and_Performance_Audit.md).

### Clean & Pushed Stopping Checkpoint (`2026-11-12`)

> [!IMPORTANT]
> **100% Clean & Pushed Stopping State**
> Both repositories are committed, verified, sealed (`0444`), and pushed to `origin/main` with `0` uncommitted working-tree files and `0` open sudo leases:
> - **`Alchemical-3D/Homunculus` (`origin/main`)**: `51453f6` (`feat(v0.3.1): add remote burn-on-use turnkeys, 7-axis CALC vectors, and teach-me Ring-0 alignment`) atop `541e2f8` (`feat(teach-me): align Section One User-Space with 6 Vision Protocols and D1-D8`).
> - **`orleacock/Engineering` (`origin/main`)**: `93077d5` (`chore(memory): quarantine Claude Sonnet Rev-3 memory retrieval audit for next-session review`) atop `5b627ed` (`chore(memory,h-sudo): sync Homunculus v0.3.1 (51453f6) handoff, LL-049, matrix, and h-sudo turnkey subcommands`), plus the final Carbon quarantine & review-first handoff commit on `origin/main`.
> - **Kernel & Workstation Security State**: `Sealed: True | Entries: 39 | Leased: 0`, `sudo_policy.json` (`0444`, `tty_turnkey`, `protect_builtin_ring1=True`), and `8` single-use `scrypt` remote turnkeys enrolled in `sudo_turnkeys.json` (`0600`).

---

## 1. Index of All Related Conversation Artifacts (Chronological Arc)

| # | Artifact | Phase / Role in the Architecture |
| :---: | :--- | :--- |
| 1 | [Stateful_Memory_Rebuild_Action_Plan.md](file:///home/orin/.gemini/antigravity-cli/brain/eaa8998c-3cc6-42a4-bbbf-d64b0fc0ce40/Stateful_Memory_Rebuild_Action_Plan.md) | Original 5-sprint blueprint for `TIER0`–`TIER5` gravity memory, 3-stage repo resolution, and entity-partitioned hybrid recall. |
| 2 | [Compare_Full_Memory_Audit_Report.md](file:///home/orin/.gemini/antigravity-cli/brain/eaa8998c-3cc6-42a4-bbbf-d64b0fc0ce40/Compare_Full_Memory_Audit_Report.md) | `Compare-Full` adversarial differential audit surfacing closed-world `--allow-lessons-source`, `Archive/`, and portable-anchor gaps. |
| 3 | [Memory_Remediation_and_Sandbox_Test_Plan.md](file:///home/orin/.gemini/antigravity-cli/brain/eaa8998c-3cc6-42a4-bbbf-d64b0fc0ce40/Memory_Remediation_and_Sandbox_Test_Plan.md) | `P1`–`P6` remediation and disaster-recovery portability plan (`v1.1` `retired_tier5_hashes`, `N1` zero-numeric recall, `PB-xx` playbooks). |
| 4 | [Mem0_Comparative_Review_and_Homunculus_Expansion_Opportunities.md](file:///home/orin/.gemini/antigravity-cli/brain/eaa8998c-3cc6-42a4-bbbf-d64b0fc0ce40/Mem0_Comparative_Review_and_Homunculus_Expansion_Opportunities.md) | Comparative evaluation motivating the `MEMORY_SDK_V1` extension gateway and `O(1)` context fabric without sacrificing deterministic truth. |
| 5 | [v0_3_0_Ring0_Sudo_and_Memory_Gateway_Plan.md](file:///home/orin/.gemini/antigravity-cli/brain/eaa8998c-3cc6-42a4-bbbf-d64b0fc0ce40/v0_3_0_Ring0_Sudo_and_Memory_Gateway_Plan.md) | `v0.3.0` 3-Ring privilege isolation (`kernel_seal.json`, `tty_turnkey`, `h-sudo`) and `scripts/memory_gateway.py` (`MEMORY_SDK_V1` `5+1` lenses). |
| 6 | [Teach_Me_User_Space_Hardening_and_Gateway_Migration_Ledger.md](file:///home/orin/.gemini/antigravity-cli/brain/eaa8998c-3cc6-42a4-bbbf-d64b0fc0ce40/Teach_Me_User_Space_Hardening_and_Gateway_Migration_Ledger.md) | Standalone User-Space pass (`SDK-MIG-01` + `TM-COND-01`–`TM-COND-11`, `LL-048`) migrating `teach_brief.py` onto `MEMORY_SDK_V1`. |
| 7 | [Teach_Me_Vision_Alignment_and_Deployment_Plan.md](file:///home/orin/.gemini/antigravity-cli/brain/eaa8998c-3cc6-42a4-bbbf-d64b0fc0ce40/Teach_Me_Vision_Alignment_and_Deployment_Plan.md) | Two-section plan aligning `/teach-me` with the 6 Developer Vision Protocols across User Space (Section One) and `Ring 0` (Section Two). |
| 8 | [Teach_Me_Conversion_Audit_and_Core_Change_Quantification.md](file:///home/orin/.gemini/antigravity-cli/brain/eaa8998c-3cc6-42a4-bbbf-d64b0fc0ce40/Teach_Me_Conversion_Audit_and_Core_Change_Quantification.md) | Independent Claude peer-audit (`AUD-01`–`AUD-22`) quantifying core deltas, `T3` 4th-power `[CALC]` dimensionality, and promotion safety. |
| 9 | [Teach_Me_Revision_Session_Agenda.md](file:///home/orin/.gemini/antigravity-cli/brain/eaa8998c-3cc6-42a4-bbbf-d64b0fc0ce40/Teach_Me_Revision_Session_Agenda.md) | Approved architecture lock resolving all Gemini + Claude items into **8 Locked Decisions (`D1`–`D8`)** and `R0-TM-01`–`R0-TM-10`. |
| 10 | [Ring0_v0_3_1_Turnkey_and_Apply_Runbook.md](file:///home/orin/.gemini/antigravity-cli/brain/eaa8998c-3cc6-42a4-bbbf-d64b0fc0ce40/Ring0_v0_3_1_Turnkey_and_Apply_Runbook.md) | Pre-staged `v0.3.1` verification ledger (`VRF-0c83f4d8ffe9`, `SBX-20261112_114304-eb3256c8`) and terminal execution sequence (`R0-TM-04` before `R0-TM-03`). |
| 11 | [Memory_Retrieval_Weight_Balance_Audit.md](file:///home/orin/.gemini/antigravity-cli/brain/e41eebf7-644b-43e6-99e9-e36580ebbce0/Memory_Retrieval_Weight_Balance_Audit.md) *(+ [scratch/](file:///home/orin/.gemini/antigravity-cli/brain/e41eebf7-644b-43e6-99e9-e36580ebbce0/scratch/) probes & Quarantined copy [2026-11-12_Claude_Sonnet_Memory_Retrieval_Weight_Balance_Audit_Rev3.md](file:///home/orin/Projects/Engineering/memory/Projects/Homunculus/Quarantine/2026-11-12_Claude_Sonnet_Memory_Retrieval_Weight_Balance_Audit_Rev3.md))* | **Quarantined Peer-AI Input #1 (`authoritative: false`)**: Read-only Claude Sonnet memory retrieval & weight-balance review (`Rev 3` + `probe1.py`–`probe5.py` / `rq.sh`). Over-indexed partially on evolving `teach-me` surfaces; queued for Turn-1 Review & Planning validation. |
| 12 | [homunculus_security_and_performance_audit.md](file:///home/orin/.gemini/antigravity-cli/brain/b4e4ead6-10c1-48ef-aaa7-83bf3c8c1892/homunculus_security_and_performance_audit.md) *(+ [security_cli_telemetry.md](file:///home/orin/.gemini/antigravity-cli/brain/b4e4ead6-10c1-48ef-aaa7-83bf3c8c1892/scratch/security_cli_telemetry.md), [bench_security_cli.py](file:///home/orin/.gemini/antigravity-cli/brain/b4e4ead6-10c1-48ef-aaa7-83bf3c8c1892/scratch/bench_security_cli.py) & Quarantined copy [2026-11-12_Gemini_Carbon_Security_and_Performance_Audit.md](file:///home/orin/Projects/Engineering/memory/Projects/Homunculus/Quarantine/2026-11-12_Gemini_Carbon_Security_and_Performance_Audit.md))* | **Quarantined Internal Audit #2 (`authoritative: false`, *"Opencode Auth Login Instructions"*)**: Gemini Carbon capability, latency, and security boundary audit (`Cracks 1`–`7`: `.xlsx`/`.3mf` `zipfile` gap, `bwrap` network/`$HOME`/`--clearenv`, `sync_memory.py` `tty_turnkey` parity, same-UID `0444` boundary; plus `Tier A`/`B`/`C` options: consolidated `pre-commit`, `rg` fast-path, `ssh-keygen -Y sign`). Queued for mandatory Turn-1 Review & Planning before any edits. |

*(Supporting scratch scripts & receipts remain archived in [v0.3.1_ring0_teach_me.patch](file:///home/orin/.gemini/antigravity-cli/brain/eaa8998c-3cc6-42a4-bbbf-d64b0fc0ce40/scratch/v0.3.1_ring0_teach_me.patch), [v0.3.1_ring0_staging_receipts.json](file:///home/orin/.gemini/antigravity-cli/brain/eaa8998c-3cc6-42a4-bbbf-d64b0fc0ce40/scratch/v0.3.1_ring0_staging_receipts.json), and [apply_v031_interactive.sh](file:///home/orin/.gemini/antigravity-cli/brain/eaa8998c-3cc6-42a4-bbbf-d64b0fc0ce40/scratch/apply_v031_interactive.sh).)*

---

## 2. Current Location in the Work (`What Is Done` vs. `What Is Queued Next`)

### Completed & Shipped Today (`v0.3.1`)
1. **Section One (`541e2f8`) — `skills/teach-me/` Vision Protocols 1–6 & `D1`–`D8`**:
   - **2-Call Primary-Thread Envelope (`D1`)**: `--context-seed --routing-only` pre-dispatch + `--attest-subagent <conv_id> --brief <path>` post-wakeup (`0` main-window file reads; `FORBIDDEN_NESTED_SUBAGENT_SPAWN` + write-allowlist containment).
   - **Redacted External Science Mixing (`D2` & `D3-C`)**: Conditional `search_web` gated by `--redact-query`, tagged `[EXTERNAL SCIENCE] ... [EXTERNAL-REF: <id>]`, requiring `--ack-external-refs` across all `--promote` targets and stripping `[EXTERNAL SCIENCE]` clauses out of auto-extracted `Lessons_Learned`.
   - **Data-Driven Cold-Start Resolver (`D7-A`)**: Auto-binds exact project stem, frontmatter `aliases:`, or unique `>= 5`-char leading stem segment; halts with `AMBIGUOUS_PROJECT_CANDIDATES` / `AMBIGUOUS_ENTITY` on trailing/shared tokens (`Air`).
   - **3-Vector Anti-Negative-Hallucination Guard (`D8-A`)**: Multi-turn verbatim `--thread-context` harvesting + `NEGATIVE_HALLUCINATION_OMISSION` + backtick-stripped `FALSE_TBD_KNOWN_IN_SOURCE`.
2. **Section Two (`Homunculus` `51453f6`) — `Ring 0` `v0.3.1` (`R0-TM-01`–`R0-TM-10`) & `Engineering` Sync (`5b627ed`)**:
   - **Burn-on-Use Remote Turnkeys (`R0-TM-04`) + Built-In `Ring 1` Protection (`R0-TM-03`)**: `8` CSPRNG `scrypt` codes enrolled in `0600` `sudo_turnkeys.json` (`45`-minute lease TTL, `SANDBOX_TURNKEY_BLOCKED` guard), `protect_builtin_ring1=True` active in `0444` `sudo_policy.json`, and `enroll-turnkeys` / `policy` subcommands added to [h_sudo.sh](file:///home/orin/Projects/Engineering/scripts/h_sudo.sh).
   - **7-Axis Exponent-Vector `[CALC]` Engine (`R0-TM-06`) & Native Study-Brief Provenance (`R0-TM-02`)**: `(L, M, T, I, Theta, B, Angle)` vector propagation (`(4 mm)**4 = 256 mm` fails closed; `(4 mm / 2 mm)**4 = 16` and `0.25 K/bar * 6 bar = 1.5 K` pass; `8k`/`4K` Kelvin false-positive guarded), `is_study_brief`-scoped `[EXTERNAL-REF]` verification, and quarantine-aware `CONTAINS_OPEN_TBD`.
   - **Memory Fabric & System-Wide `D6` Speed-First Inside Verified Boundaries (`R0-TM-01/05/07/08/09/10`)**: `LEGACY_PRE_V030_GATEWAY_EXEMPT = {}` retired (`0` exemptions), `FIRST-PRINCIPLES-THEORY` / `[EXTERNAL SCIENCE]` stripped from `Extensions/*.md` BM25 vectors, `record_telemetry=False` on read-only `get_context_pack`, `0`-project `Default_Entity_context_fabric.json` suppressed, and `D6` codified across `co-engineering-partner.md` + `adapters/*` (`AGENTS.md = 22,036 B <= 22,500 B`).

### Prioritized Next-Session Queue ([Alchemical-3D_Tasks.md](file:///home/orin/Projects/Engineering/memory/Tasks/Alchemical-3D_Tasks.md#L61-L69))
1. **`[MANDATORY FIRST ACTION ON RESUME — UNIFIED REVIEW & PLANNING SESSION BEFORE ANY CHANGES]` Validate Both Quarantined Audits Against Live `v0.3.1` Structure & Intent**:
   - **Audit Input A (Memory Retrieval & Weight-Balance — Claude Sonnet `e41eebf7`)**: [Memory_Retrieval_Weight_Balance_Audit.md](file:///home/orin/.gemini/antigravity-cli/brain/e41eebf7-644b-43e6-99e9-e36580ebbce0/Memory_Retrieval_Weight_Balance_Audit.md), [scratch/](file:///home/orin/.gemini/antigravity-cli/brain/e41eebf7-644b-43e6-99e9-e36580ebbce0/scratch/) (`probe1.py`–`probe5.py`, `rq.sh`), and quarantined copy [2026-11-12_Claude_Sonnet_Memory_Retrieval_Weight_Balance_Audit_Rev3.md](file:///home/orin/Projects/Engineering/memory/Projects/Homunculus/Quarantine/2026-11-12_Claude_Sonnet_Memory_Retrieval_Weight_Balance_Audit_Rev3.md). Separate valid retrieval/stemmer/doc-parity/promotion observations (`F-01`–`F-16` / `R-01`–`R-08`) from assumptions around evolving `teach-me` surfaces.
   - **Audit Input B (Security & Performance — Gemini Carbon *"Opencode Auth Login Instructions"* `b4e4ead6`)**: [homunculus_security_and_performance_audit.md](file:///home/orin/.gemini/antigravity-cli/brain/b4e4ead6-10c1-48ef-aaa7-83bf3c8c1892/homunculus_security_and_performance_audit.md), [security_cli_telemetry.md](file:///home/orin/.gemini/antigravity-cli/brain/b4e4ead6-10c1-48ef-aaa7-83bf3c8c1892/scratch/security_cli_telemetry.md), [bench_security_cli.py](file:///home/orin/.gemini/antigravity-cli/brain/b4e4ead6-10c1-48ef-aaa7-83bf3c8c1892/scratch/bench_security_cli.py), and quarantined copy [2026-11-12_Gemini_Carbon_Security_and_Performance_Audit.md](file:///home/orin/Projects/Engineering/memory/Projects/Homunculus/Quarantine/2026-11-12_Gemini_Carbon_Security_and_Performance_Audit.md). Evaluate `Cracks 1`–`7` (`.xlsx`/`.3mf` `zipfile` gap, `bwrap` `--unshare-all`/`--clearenv`/`$HOME` masking, `Crack 3` = `Task #61` `sync_memory.py` `tty_turnkey`, same-UID `0444` boundary) and `Tier A`/`B`/`C` options (`pre-commit` process consolidation, `rg` hybrid fast-path, `ssh-keygen -Y sign` seals).
   - **Strict Execution Gate**: Treat both reports strictly as **non-authoritative inputs (`quarantine: true`, `authoritative: false`)** and **make zero code, rule, skill, or memory changes until the Review & Planning Session concludes with an engineer-approved roadmap**.
2. **`[OPTIONAL — ISOLATED]` Live Post-`v0.3.1` `/teach-me` Subagent Canary**: Run 1 throw-away `/teach-me` hardware/physics query (e.g., pneumatic tube bore reduction + Joule-Thomson effect) to observe the sealed `v0.3.1` stack (`D1` + `D2` + `R0-TM-02` + `R0-TM-06`) live end-to-end *(deferred today strictly to preserve subscription tokens)*.
3. **`[LOAD-BEARING]` `sync_memory.py` `tty_turnkey` Governance Parity (`Task #61`)**: Under `sudo:`, wire `homunculus_paths._require_interactive_tty_if_needed(..., remote_turnkey=...)` into `sync_memory.py` (`set_memory_rules_lock_state`, `seal_memory_governance`, `set_lesson_tier`) so memory governance flags share the exact same `/dev/tty` + remote-turnkey protection as `Ring 0`.
4. **`[ISOLATED]` Course B Rule & Adapter Byte Compaction (`Task #62`) & `skill-architect` Telemetry Pulse (`Task #67`)**: Reclaim `~260`–`500 B` of `AGENTS.md` headroom (`22,036 B` vs `22,500 B` ceiling) and discuss the on-call `--telemetry-pulse` design.
5. **Hardware Repo Queue** *(when shifting back to hardware)*: `Alembic_Toolhead` (`8` dirty BOM/doc files diff against `3ff29ce`), `Pestle_Rotational_Bowden` (2 PNG card interiors + fastener conflict resolution), and `Pneuma_Remote_Air` (bench fastener count & `TPU` slicer open parameters).

---

## 3. Special Conditions & Engineering Edge Cases Encountered & Solved

1. **Remote Web-Only Session Under `tty_turnkey` (`0` SSH / Terminal Access Initially)**:
   - *Condition*: Session began remotely via the web app while `sudo_policy.json` (`0444`, `tty_turnkey`) blocked `Ring 0` modifications (`[HUMAN_TERMINAL_REQUIRED]`).
   - *Resolution*: Completed `100%` of User-Space Section One (`Phases A–D`) first, built modular staging scripts in `scratch/ring0_patchers/` to test `Ring 0` `v0.3.1` inside an isolated `/tmp` clone (`Live Host Mutations: 0`), and enrolled `8` burn-on-use `scrypt` turnkeys (`R0-TM-04`) once back at the physical terminal so future remote sessions can authorize `sudo:` leases safely via `--remote-turnkey HMK-XXXX-XXXX-XXXX`.
2. **Unintended User-Space `Ring 1` Unlock Exposure (`[KERNEL-RFC-06]` / `R0-TM-03`)**:
   - *Condition*: Early in remote work, `--unlock-scope teach-me` unlocked built-in `Ring 1` files without a `Ring 0` core unlock; while helpful during remote outage, built-in `Ring 1` skills needed optional maintainer protection without breaking custom user skills.
   - *Resolution*: Added `ring1_builtin_entries` to `kernel_seal.json` (`v1.1`) and `protect_builtin_ring1: true` in `sudo_policy.json`, gating `teach-me`, `doc-and-card-studio`, and `visual-studio` behind TTY/turnkey while leaving custom skills User-Space unlockable.
3. **Mandatory `R0-TM-04` Before `R0-TM-03` Enrollment Ordering**:
   - *Condition*: Enabling `--protect-builtin-ring1` *before* enrolling remote turnkeys would lock out remote maintenance of built-in `Ring 1` skills.
   - *Resolution*: Enforced strict `Step 4` (`enroll-turnkeys`) $\rightarrow$ `Step 5` (`--protect-builtin-ring1`) ordering in both the runbook and [apply_v031_interactive.sh](file:///home/orin/.gemini/antigravity-cli/brain/eaa8998c-3cc6-42a4-bbbf-d64b0fc0ce40/scratch/apply_v031_interactive.sh).
4. **`/dev/tty` 4-Character Hex Challenge Swallowing Multi-Line Clipboard Pastes + Challenge Timeout**:
   - *Condition*: Pasting a multi-command shell block caused `h-sudo unlock`'s `/dev/tty` `4`-char hex prompt to consume the next pasted line (`git apply ...`) as the challenge input (`challenge mismatch`), and back-to-back prompts risked starting the `/dev/tty` challenge timer while copying turnkey codes.
   - *Resolution*: Wrapped the terminal sequence into single-line [apply_v031_interactive.sh](file:///home/orin/.gemini/antigravity-cli/brain/eaa8998c-3cc6-42a4-bbbf-d64b0fc0ce40/scratch/apply_v031_interactive.sh) with an explicit `read -r -p` pause after printing `TK-01..TK-08`, keeping plaintext codes `100%` out of AI chat transcripts (`data-and-credential-safety.md` §1).
5. **Cross-Ring Splash Guard (`[SPLASH_EXPOSURE_BLOCKED]`)**:
   - *Condition*: `homunculus_paths.py` blocks `--sudo-unlock` if any `Ring 1/2` files in `skills/` are uncommitted.
   - *Resolution*: Sequenced two clean commits (`541e2f8` User Space Commit 1 $\rightarrow$ `h-sudo unlock` $\rightarrow$ `51453f6` `Ring 0` Commit 2).
6. **Containment & Anti-Negative-Hallucination Cracks Caught by `+faults` (`LL-049`)**:
   - *Condition*: Adversarial `+faults` testing exposed (a) `/tmp` prefix write-escape in `attest_subagent_execution`, (b) `init_brief --out` accepting `<memory_root>/` paths, and (c) backticked source keys (`` `manifold_bore_mm` ``) evading `FALSE_TBD_KNOWN_IN_SOURCE`.
   - *Resolution*: Narrowed write allowlist strictly to `<study_briefs_root>` + `/brain/<uuid>/scratch/`, blocked `<memory_root>/` in `init_brief --out`, and stripped markdown backticks before `FALSE_TBD_KNOWN_IN_SOURCE` matching (`12/12` faults caught in `SBX-20261112_102511-82bb9701`).
7. **4th-Power Hagen-Poiseuille Dimensional Bug (`T3`) & `8k` Kelvin False-Positive Guard (`R0-TM-06`)**:
   - *Condition*: Legacy string-pair `[CALC]` passed `d1` through `ast.Pow` unchanged (letting `(4 mm)**4 = 256 mm` pass!), while adding `K` (Kelvin) risked parsing `8k` token counts in `co-engineering-partner.md` as Kelvin temperatures.
   - *Resolution*: Replaced string matching with `7`-axis integer exponent vectors and blocked lowercase `k` / unspaced `4K` in `canonicalize_unit()`.
8. **Maintainer Pre-Commit AST Matrix Parity & `Workstation_Operations` Telemetry Sync**:
   - *Condition*: `Homunculus/.git/hooks/pre-commit` validates every Python import edge against [Homunculus_Script_Skill_Interaction_Matrix.md](file:///home/orin/Projects/Engineering/memory/Projects/Homunculus/Homunculus_Script_Skill_Interaction_Matrix.md), and editing `scripts/h_sudo.sh` shifted `Workstation_Operations_Software.md` `inventory_sha256`.
   - *Resolution*: Synced the `memory_gateway.py` $\leftrightarrow$ `teach_brief.py` matrix edges before Commit 1 and ran `--sync-software --project Workstation_Operations` before pushing `Engineering` (`5b627ed`).
9. **Keeping `.cache/preflight_state.json` Out of Clean-Room `Homunculus/`**:
   - *Condition*: Running `homunculus_paths.py --map` directly inside `Homunculus/` without `--memory-root` wrote `.cache/preflight_state.json` with local OS user paths inside `Homunculus/`, tripping `audit_portability.py`.
   - *Resolution*: Removed `Homunculus/.cache/` and recorded preflight state via `sync_memory.py --memory-root .../Engineering/memory --project Homunculus --preflight <script>` (`0` portability violations).

---

## 4. Next-Session Turn-1 Kickstart & Review-First Protocol

- **Step 1 (Mandatory Read-Only Kickstart Into Review & Planning — Zero Mutations)**:
  Run `--kickstart`, read the two quarantined audits ([2026-11-12_Claude_Sonnet_Memory_Retrieval_Weight_Balance_Audit_Rev3.md](file:///home/orin/Projects/Engineering/memory/Projects/Homunculus/Quarantine/2026-11-12_Claude_Sonnet_Memory_Retrieval_Weight_Balance_Audit_Rev3.md) and [2026-11-12_Gemini_Carbon_Security_and_Performance_Audit.md](file:///home/orin/Projects/Engineering/memory/Projects/Homunculus/Quarantine/2026-11-12_Gemini_Carbon_Security_and_Performance_Audit.md)), and open an interactive **Review & Planning Session** (`0` file edits, `0` unlocks) to decide which findings/tiers are accepted, rejected, or sequenced:
  ```bash
  python3 /home/orin/Projects/Alchemical3D/Homunculus/skills/project-memory/scripts/sync_memory.py \
    --memory-root /home/orin/Projects/Engineering/memory --project Homunculus --kickstart
  ```
- **Step 2 (Only After Plan Approval — Remote Web-Only `sudo:` Unlock When Needed)**:
  Prefix your chat prompt with `sudo:` and supply **one** unspent `HMK-XXXX-XXXX-XXXX` code; the agent will pass `--remote-turnkey <code>` (atomically burning that single code and granting a `45`-minute scoped lease).
<!-- SESSION-HANDOFF:END -->

## 🎯 Active Tasks
*(Transcluded live from `### Homunculus` in [`Alchemical3D_Tasks`](../../Tasks/Alchemical-3D_Tasks.md) (`Tasks/Alchemical3D_Tasks.md#Homunculus`) — edit checkboxes in one place only)*

> **Active Task Queue**: Tracked in [`Alchemical3D_Tasks`](../../Tasks/Alchemical-3D_Tasks.md#Homunculus) *(Single-Writer Task Umbrella)*.
