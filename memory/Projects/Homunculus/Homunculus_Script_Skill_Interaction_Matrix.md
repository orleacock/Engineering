---
title: "Homunculus Script, Skill & Code-Name Interaction Matrix (Non-Authoritative Maintainer Map)"
project: "Homunculus"
entity: "Alchemical-3D"
compartment: "private"
note_type: "reference"
authoritative: false
status: "NON_AUTHORITATIVE_REFERENCE"
last_synced: "2026-11-06"
---

# 🧩 Homunculus Script, Skill & Code-Name Interaction Matrix *(Non-Authoritative Maintainer Map)*

> [!IMPORTANT]
> **NON-AUTHORITATIVE DEVELOPER REFERENCE (`authoritative: false` — DO NOT CITE AS FACT)**: This file is an internal maintainer lookup table kept alongside [`Homunculus_Cleanroom_Promotion_Diff.md`](Homunculus_Cleanroom_Promotion_Diff.md) so we can quickly see what each skill and script touches when refactoring or checking functional naming before release. It is never shipped inside `Homunculus/` and is auto-excluded from `verify_claims.py` `--sources`—always treat the live `.py` scripts and `SKILL.md` files in [`/home/orin/Projects/Engineering/Homunculus`](../../../Homunculus) as the sole authoritative source of truth.

---

## 1. Master Script-to-Skill Cross-Reference Summary

| Script Path (`Homunculus/`) | Role | Owning Module | Interacting Skills, Rules & Callers |
| :--- | :--- | :--- | :--- |
| [`scripts/homunculus_paths.py`](../../../Homunculus/scripts/homunculus_paths.py) | Cross-OS Path, Memory & `study_briefs_root` Resolver | Core Framework | `build_adapters.py`, `project-memory`, `visual-studio`, `teach-me`, `install.sh`, `install.ps1`, `test_foundation.py` |
| [`scripts/build_adapters.py`](../../../Homunculus/scripts/build_adapters.py) | Client Adapter, Ignore-Rule & Hook Builder | Core Framework | `homunculus_paths.py`, all `rules/`, all `skills/`, `addons/`, `install.sh`, `install.ps1`, `test_adapters.py` |
| [`scripts/audit_portability.py`](../../../Homunculus/scripts/audit_portability.py) | Zero-PII, Path & Stdlib-Only Gate | Core Framework | `install.sh`, `install.ps1`, `pre-commit-gate`, `skill-architect`, `engineering-sandbox`, `test_foundation.py`, `test_data_safety.py`, `test_adapters.py` |
| [`scripts/audit_data_boundary.py`](../../../Homunculus/scripts/audit_data_boundary.py) | 3-Compartment Secret & Encoding Firewall | Core Framework | `data-and-credential-safety.md`, `pre-commit.sh`, `pre-push.sh`, `pre-commit-gate`, `engineering-sandbox`, `test_data_safety.py`, `test_adapters.py` |
| [`install.sh`](../../../Homunculus/install.sh) | POSIX (`Linux`/`macOS`) Installer | Core Framework | `audit_portability.py`, `homunculus_paths.py`, `build_adapters.py`, `test_foundation.py`, `test_adapters.py` |
| [`install.ps1`](../../../Homunculus/install.ps1) | Windows PowerShell Installer | Core Framework | `audit_portability.py`, `homunculus_paths.py`, `build_adapters.py` |
| [`templates/hooks/pre-commit.sh`](../../../Homunculus/templates/hooks/pre-commit.sh) | Git Pre-Commit Staged & Memory Gate | Core Framework | `build_adapters.py`, `audit_data_boundary.py`, `project-memory` (`sync_memory.py`), `test_adapters.py` |
| [`templates/hooks/pre-push.sh`](../../../Homunculus/templates/hooks/pre-push.sh) | Git Pre-Push Remote & Author Lock | Core Framework | `build_adapters.py`, `audit_data_boundary.py`, `test_adapters.py` |
| [`skills/skill-architect/scripts/audit_skill_hygiene.py`](../../../Homunculus/skills/skill-architect/scripts/audit_skill_hygiene.py) | Skill/Rule Synergy, Link & Stdlib Auditor | `skill-architect` | `co-engineering-partner.md`, `pre-commit-gate`, `engineering-sandbox`, all `rules/`, `skills/`, `addons/`, `test_adapters.py` |
| [`skills/project-memory/scripts/sync_memory.py`](../../../Homunculus/skills/project-memory/scripts/sync_memory.py) | Dual-Mode Memory & Containment Manager | `project-memory` | `homunculus_paths.py`, `subagent-orchestrator` (`inspect_hardware_ecosystem.py`), `claim-verification`, `pre-commit.sh`, `pre-commit-gate`, `author-voice-cadence`, `test_project_memory.py`, `test_claim_verification.py` |
| [`skills/claim-verification/scripts/verify_claims.py`](../../../Homunculus/skills/claim-verification/scripts/verify_claims.py) | Closed-World Claim, Entity & `[CALC]` Oracle | `claim-verification` | `verifiable-accuracy.md`, `teach-me`, `engineering-sandbox`, `pre-commit-gate`, `project-memory`, `subagent-orchestrator`, `author-voice-cadence`, `test_claim_verification.py`, `test_teach_me.py` |
| [`skills/subagent-orchestrator/scripts/inspect_hardware_ecosystem.py`](../../../Homunculus/skills/subagent-orchestrator/scripts/inspect_hardware_ecosystem.py) | STEP/STL Geometry & Klipper `.cfg` Oracle | `subagent-orchestrator` | `project-memory` (`sync_memory.py`), `claim-verification`, `teach-me`, `co-engineering-partner.md`, `test_core_skills.py`, `test_claim_verification.py` |
| [`skills/engineering-sandbox/scripts/sandbox_runner.py`](../../../Homunculus/skills/engineering-sandbox/scripts/sandbox_runner.py) | `bwrap` + CoW Dry-Run & Subagent Fault Bench | `engineering-sandbox` | `co-engineering-partner.md`, `claim-verification` (`verify_claims.py`), `doc-and-card-studio` (`audit_repo_docs.py`), `pre-commit-gate`, `test_core_skills.py` |
| [`skills/visual-studio/scripts/render_diagram.py`](../../../Homunculus/skills/visual-studio/scripts/render_diagram.py) | Pure-Stdlib SVG Diagram & Blueprint Engine | `visual-studio` | `homunculus_paths.py`, `doc-and-card-studio` (`format_image.py`), `pre-commit-gate`, `project-memory`, `test_core_skills.py` |
| [`skills/doc-and-card-studio/scripts/audit_repo_docs.py`](../../../Homunculus/skills/doc-and-card-studio/scripts/audit_repo_docs.py) | Markdown Alert, Link, Card & Brand Auditor | `doc-and-card-studio` | `format_image.py`, `engineering-sandbox` (`sandbox_runner.py`), `pre-commit-gate`, `author-voice-cadence`, `test_core_skills.py` |
| [`skills/doc-and-card-studio/scripts/format_image.py`](../../../Homunculus/skills/doc-and-card-studio/scripts/format_image.py) | Rounded-Corner Drop-Shadow Card Formatter | `doc-and-card-studio` | `audit_repo_docs.py`, `visual-studio` (`render_diagram.py`), `test_core_skills.py` |
| [`skills/teach-me/scripts/teach_brief.py`](../../../Homunculus/skills/teach-me/scripts/teach_brief.py) | `Brief+` Scaffolder, Verifier & Card Engine | `teach-me` | `homunculus_paths.py`, `claim-verification` (`verify_claims.py`), `project-memory`, `subagent-orchestrator`, `co-engineering-partner.md`, `test_teach_me.py`, `test_core_skills.py` |
| [`addons/author-voice-cadence/scripts/extract_voice_cadence.py`](../../../Homunculus/addons/author-voice-cadence/scripts/extract_voice_cadence.py) | Clean-Room Stylometric & Cadence Extractor | `author-voice-cadence` | `build_adapters.py`, `doc-and-card-studio`, `project-memory`, `claim-verification`, `data-and-credential-safety.md`, `test_core_skills.py` |
| [`tests/test_foundation.py`](../../../Homunculus/tests/test_foundation.py) | Foundation & Cross-OS Path Unit Suite | `tests/` | `homunculus_paths.py`, `audit_portability.py`, `install.sh` |
| [`tests/test_data_safety.py`](../../../Homunculus/tests/test_data_safety.py) | Compartment & Multi-Encoding Safety Suite | `tests/` | `audit_data_boundary.py`, `audit_portability.py`, `HOMUNCULUS_START_HERE.md`, `rules/` |
| [`tests/test_adapters.py`](../../../Homunculus/tests/test_adapters.py) | Client Adapter, Ignore-Sync & Hook Suite | `tests/` | `build_adapters.py`, `audit_portability.py`, `audit_data_boundary.py`, `audit_skill_hygiene.py`, `install.sh` |
| [`tests/test_project_memory.py`](../../../Homunculus/tests/test_project_memory.py) | Dual-Mode Memory & Entity Containment Suite | `tests/` | `sync_memory.py` |
| [`tests/test_claim_verification.py`](../../../Homunculus/tests/test_claim_verification.py) | Truth-Oracle & Cross-Script Sync Suite | `tests/` | `verify_claims.py`, `sync_memory.py`, `inspect_hardware_ecosystem.py` |
| [`tests/test_core_skills.py`](../../../Homunculus/tests/test_core_skills.py) | Core Skills, SVG, Docs, Voice & Sandbox Suite | `tests/` | `inspect_hardware_ecosystem.py`, `render_diagram.py`, `audit_repo_docs.py`, `format_image.py`, `extract_voice_cadence.py`, `sandbox_runner.py`, `teach_brief.py` |
| [`tests/test_teach_me.py`](../../../Homunculus/tests/test_teach_me.py) | `teach-me` `Brief+` & Umbrella Isolation Suite | `tests/` | `teach_brief.py`, `verify_claims.py` |

---

## 2. Skill-by-Skill & Layer-by-Layer Coupling Blocks

### Block 1: Skill_Architect ([`skills/skill-architect/`](../../../Homunculus/skills/skill-architect/SKILL.md))

| Interacting Script / Module | Direction | Target Skill / Layer | Interacting Functions, CLI Flags & Code Names |
| :--- | :--- | :--- | :--- |
| [`audit_skill_hygiene.py`](../../../Homunculus/skills/skill-architect/scripts/audit_skill_hygiene.py) | **Owned** | `skill-architect` | `run_audit`, `run_check_new`, `check_local_links_and_scripts`, `audit_script_stdlib_compliance`, `scan_turn_waste_and_accuracy_hazards`, `NON_FUNCTIONAL_MODULE_NAME`, `DEV_JOURNAL_CROSS_BLEED`, `--audit`, `--check-new`, `--strict-structure`, `--repo-root` |
| [`co-engineering-partner.md`](../../../Homunculus/rules/co-engineering-partner.md) | **Governed By** | Always-On Rule | `Chesterton's Fence`, `[KEEP — OPERATIONAL CLI / FLAG ANCHOR]`, `[KEEP — ACTION-SITE DOMAIN INSTANTIATION]`, `[KEEP INLINE — PREVENTS POINTER-HOP TOKEN INVERSION]` |
| [`pre-commit-gate/SKILL.md`](../../../Homunculus/skills/pre-commit-gate/SKILL.md) | **Called By** | `pre-commit-gate` | Stage Z4 invokes `audit_skill_hygiene.py` with `--audit` and `--strict-structure` |
| [`sandbox_runner.py`](../../../Homunculus/skills/engineering-sandbox/scripts/sandbox_runner.py) | **Monitored By** | `engineering-sandbox` | `parse_transcript_telemetry` tracks `audit_skill_hygiene.py` runs inside subagent transcripts |
| [`audit_portability.py`](../../../Homunculus/scripts/audit_portability.py) | **Handoff To** | Core Framework | Paired with `audit_skill_hygiene.py` before skill promotion (`sys.stdlib_module_names`, `BROKEN_SKILL_LINK_OR_SCRIPT`) |
| All `skills/` & `addons/` | **Audits** | Framework-Wide | Verifies `memory_dossier_or_tree` (`AUTO-TREE`, `sync_memory`, `project-memory`, `memory_root`), `claim_verification` (`verify_claims.py`), `sandbox_gate`, and `pre_commit_gate` synergy |
| [`test_adapters.py`](../../../Homunculus/tests/test_adapters.py) | **Tested By** | `tests/` | `audit_skill_hygiene.run_audit` (`test_repo_portability_data_boundary_and_skill_hygiene_remain_clean`) |

---

### Block 2: Project_Memory ([`skills/project-memory/`](../../../Homunculus/skills/project-memory/SKILL.md))

| Interacting Script / Module | Direction | Target Skill / Layer | Interacting Functions, CLI Flags & Code Names |
| :--- | :--- | :--- | :--- |
| [`sync_memory.py`](../../../Homunculus/skills/project-memory/scripts/sync_memory.py) | **Owned** | `project-memory` | `init_memory_root`, `init_project`, `query_project_section`, `sync_hardware_telemetry`, `sync_software_telemetry`, `sync_all_project_trees`, `save_session_handoff`, `kickstart_project`, `query_open_tasks`, `query_tbd_ledger`, `audit_memory`, `sync_obsidian_visual_brain` |
| [`homunculus_paths.py`](../../../Homunculus/scripts/homunculus_paths.py) | **Imports** | Core Framework | `resolve_workspace_config`, `resolve_homunculus_root`, `memory_mode` (`headless` vs. `obsidian`), `memory_root` |
| [`inspect_hardware_ecosystem.py`](../../../Homunculus/skills/subagent-orchestrator/scripts/inspect_hardware_ecosystem.py) | **Calls** | `subagent-orchestrator` | `sync_hardware_telemetry` runs `inspect_hardware_ecosystem.py` with `--memory-root`, `--project`, `--repo`, and `--sync-manifest` |
| [`verify_claims.py`](../../../Homunculus/skills/claim-verification/scripts/verify_claims.py) | **Quarantine Coupling** | `claim-verification` | `verify_claims.py` strips `<!-- QUARANTINE-ZONE:START -->` and `<!-- SESSION-HANDOFF:START -->` blocks (`QUARANTINE_SOURCE_REJECTED`) |
| [`teach_brief.py`](../../../Homunculus/skills/teach-me/scripts/teach_brief.py) | **Promoted By** | `teach-me` | Unpromoted `study_briefs/` stay outside `memory_root` until `teach_brief.py` `--promote` writes `PROMOTED_ENGINEERING_BRIEF` |
| [`pre-commit.sh`](../../../Homunculus/templates/hooks/pre-commit.sh) | **Called By** | Git Hook | Runs `sync_memory.py` with `--memory-root` and `--audit` (`CROSS_ENTITY_CONTAMINATION`, `CHECKBOX_IN_PROJECT_HUB`, `BROKEN_MEMORY_LINK`, `WIKILINK_SYNTAX_FORBIDDEN`) |
| [`pre-commit-gate/SKILL.md`](../../../Homunculus/skills/pre-commit-gate/SKILL.md) | **Called By** | `pre-commit-gate` | Stage X runs `--save-handoff`, `--sync-trees`, `--sync-tasks`, `--sync-visuals`, `--export-canvas`, and `--audit` |
| [`author-voice-cadence/SKILL.md`](../../../Homunculus/addons/author-voice-cadence/SKILL.md) | **Called By** | `author-voice-cadence` | Runs `sync_memory.py` with `--audit` after updating voice profiles inside `Standards_and_Specs/` |
| [`test_project_memory.py`](../../../Homunculus/tests/test_project_memory.py) & [`test_claim_verification.py`](../../../Homunculus/tests/test_claim_verification.py) | **Tested By** | `tests/` | `TestProjectMemory` + `test_cross_script_memory_verify_claims_and_hardware_sync` |

---

### Block 3: Claim_Verification ([`skills/claim-verification/`](../../../Homunculus/skills/claim-verification/SKILL.md))

| Interacting Script / Module | Direction | Target Skill / Layer | Interacting Functions, CLI Flags & Code Names |
| :--- | :--- | :--- | :--- |
| [`verify_claims.py`](../../../Homunculus/skills/claim-verification/scripts/verify_claims.py) | **Owned** | `claim-verification` | `SourceFileInfo`, `SourceIndex`, `_detect_entity`, `_canonicalize_entity_token`, `dynamic_aliases`, `ambiguous_umbrellas`, `verify_calc_marker`, `audit_target`, `--target`, `--sources`, `--entity`, `--strict-provenance`, `--fail-on-tbd`, `VRF-` receipt |
| [`verifiable-accuracy.md`](../../../Homunculus/rules/verifiable-accuracy.md) | **Governed By** | Always-On Rule | Closed-world parametric lock, explicit missing-spec tagging (`--fail-on-tbd`), `QUALIFIER_GROUPS`, `CROSS_ENTITY_BORROWING`, `DIMENSIONAL_ALCHEMY` |
| [`teach_brief.py`](../../../Homunculus/skills/teach-me/scripts/teach_brief.py) | **Called By** | `teach-me` | Invokes `verify_claims.py` with `--target`, `--sources`, and `--json`; enforces `FIRST-PRINCIPLES-THEORY` `[CALC]` math and `STUDY_BRIEF_SOURCE_REJECTED` |
| [`sandbox_runner.py`](../../../Homunculus/skills/engineering-sandbox/scripts/sandbox_runner.py) | **Called By** | `engineering-sandbox` | `DEFAULT_VERIFY_CLAIMS_SCRIPT` invoked during `compare-light` / `compare-full` differential scoring |
| [`inspect_hardware_ecosystem.py`](../../../Homunculus/skills/subagent-orchestrator/scripts/inspect_hardware_ecosystem.py) | **Fed By** | `subagent-orchestrator` | Consumes `_Hardware.md` STEP/STL bounding boxes, cylindrical surface histograms, and `.cfg` pins as ground-truth `--sources` |
| [`pre-commit-gate/SKILL.md`](../../../Homunculus/skills/pre-commit-gate/SKILL.md) | **Called By** | `pre-commit-gate` | Stage Z1 runs `verify_claims.py` with `--strict-provenance` before milestone commits |
| [`author-voice-cadence/SKILL.md`](../../../Homunculus/addons/author-voice-cadence/SKILL.md) | **Called By** | `author-voice-cadence` | Gate 3 verifies zero unbacked claims after stylistic drafting |
| [`test_claim_verification.py`](../../../Homunculus/tests/test_claim_verification.py) & [`test_teach_me.py`](../../../Homunculus/tests/test_teach_me.py) | **Tested By** | `tests/` | `TestClaimVerification` + `test_umbrella_org_entity_alignment_and_cross_project_hallucination_block` |

---

### Block 4: Subagent_Orchestrator ([`skills/subagent-orchestrator/`](../../../Homunculus/skills/subagent-orchestrator/SKILL.md))

| Interacting Script / Module | Direction | Target Skill / Layer | Interacting Functions, CLI Flags & Code Names |
| :--- | :--- | :--- | :--- |
| [`inspect_hardware_ecosystem.py`](../../../Homunculus/skills/subagent-orchestrator/scripts/inspect_hardware_ecosystem.py) | **Owned** | `subagent-orchestrator` | `detect_step_unit_scale`, `inspect_step_file`, `inspect_stl_file`, `inspect_cfg_file`, `scan_repo_hardware`, `render_manifest_markdown`, `--repo`, `--memory-root`, `--project`, `--sync-manifest`, `--check-cache` (`CACHE_VALID` / `CACHE_STALE`) |
| [`oracle_cli_cheatsheet.md`](../../../Homunculus/skills/subagent-orchestrator/references/oracle_cli_cheatsheet.md) & [`orchestration_playbooks.md`](../../../Homunculus/skills/subagent-orchestrator/references/orchestration_playbooks.md) | **Owned** | `subagent-orchestrator` | CLI flags for all Homunculus oracles; `[DISPATCH]`, `[VERIFIED FACT]`, `[CAD TELEMETRY]`, `[CLI TELEMETRY]`, `[MEMORY_DELTA]`, `[EXTRACTION BLOCKED — ABORTED]` |
| [`sync_memory.py`](../../../Homunculus/skills/project-memory/scripts/sync_memory.py) | **Called By** | `project-memory` | `sync_memory.py` `--sync-hardware` delegates CAD/firmware manifest generation to `inspect_hardware_ecosystem.py` `--sync-manifest` |
| [`brief_authoring_playbook.md`](../../../Homunculus/skills/teach-me/references/brief_authoring_playbook.md) | **Called By** | `teach-me` | Delegated tutor subagents run `inspect_hardware_ecosystem.py` with `--repo` for live mechanical/CAD telemetry |
| [`co-engineering-partner.md`](../../../Homunculus/rules/co-engineering-partner.md) | **Governed By** | Always-On Rule | Explicit model tiering (`flash_lite`, `flash`, `pro`), Single-Writer Memory, and 30–80 line pre-mutation window reads |
| [`test_core_skills.py`](../../../Homunculus/tests/test_core_skills.py) & [`test_claim_verification.py`](../../../Homunculus/tests/test_claim_verification.py) | **Tested By** | `tests/` | `test_inspect_hardware_ecosystem_stl_and_cfg` + `test_cross_script_memory_verify_claims_and_hardware_sync` |

---

### Block 5: Engineering_Sandbox ([`skills/engineering-sandbox/`](../../../Homunculus/skills/engineering-sandbox/SKILL.md))

| Interacting Script / Module | Direction | Target Skill / Layer | Interacting Functions, CLI Flags & Code Names |
| :--- | :--- | :--- | :--- |
| [`sandbox_runner.py`](../../../Homunculus/skills/engineering-sandbox/scripts/sandbox_runner.py) | **Owned** | `engineering-sandbox` | `clone_cow_directory`, `run_in_bwrap`, `parse_transcript_telemetry`, `evaluate_ab_comparison`, `--mode` (`dry-run`, `blind-light`, `blind-full`, `visible-light`, `visible-full`, `compare-light`, `compare-full`), `--spec`, `--faults`, `--fault-case`, `SBX-` receipt |
| [`verify_claims.py`](../../../Homunculus/skills/claim-verification/scripts/verify_claims.py) | **Calls** | `claim-verification` | `DEFAULT_VERIFY_CLAIMS_SCRIPT` invoked automatically in `compare-light` / `compare-full` A/B scoring against `--compare-source` |
| [`audit_repo_docs.py`](../../../Homunculus/skills/doc-and-card-studio/scripts/audit_repo_docs.py) | **Calls** | `doc-and-card-studio` | `DEFAULT_AUDIT_DOCS_SCRIPT` invoked on generated deliverables inside `_audit_arm_deliverables` |
| [`co-engineering-partner.md`](../../../Homunculus/rules/co-engineering-partner.md) & [`pre-commit-gate/SKILL.md`](../../../Homunculus/skills/pre-commit-gate/SKILL.md) | **Governed By** | Rule & Release Gate | Track-2 `[SANDBOX-PENDING]` -> `[SOLVED]` gate; `FAULT_SETUP_NOOP`, `WRONG_FAULT_SIGNATURE`, `VALIDATOR_CRASH`, `COACHING_MASKED_DEFECT` |
| [`test_core_skills.py`](../../../Homunculus/tests/test_core_skills.py) | **Tested By** | `tests/` | `test_sandbox_runner_spec_workspace_and_faults` |

---

### Block 6: Visual_Studio ([`skills/visual-studio/`](../../../Homunculus/skills/visual-studio/SKILL.md))

| Interacting Script / Module | Direction | Target Skill / Layer | Interacting Functions, CLI Flags & Code Names |
| :--- | :--- | :--- | :--- |
| [`render_diagram.py`](../../../Homunculus/skills/visual-studio/scripts/render_diagram.py) | **Owned** | `visual-studio` | `discover_palettes`, `discover_blueprints`, `DiagramBuilder`, `render_layered_architecture`, `render_column_dataflow`, `render_hardware_pinout_pneumatic`, `render_comparison_matrix`, `render_spatial_topology`, `--spec`, `--blueprint`, `--palette`, `--strict` |
| [`homunculus_paths.py`](../../../Homunculus/scripts/homunculus_paths.py) | **Imports** | Core Framework | `resolve_workspace_config` for active `memory_root` and optional PNG rasterizer capability probing |
| [`format_image.py`](../../../Homunculus/skills/doc-and-card-studio/scripts/format_image.py) | **Calls** | `doc-and-card-studio` | Invokes `format_image.py` when `--github-card` is passed alongside PNG export |
| [`Diagram_Palettes.json`](../../../Homunculus/templates/diagrams/Diagram_Palettes.json) & `templates/diagrams/Diagram_Blueprints/` | **Loads** | `templates/diagrams/` | Discovers built-in palettes (`default_dark`, `gruvbox_dark`) and archetypes (`layered_architecture`, `column_dataflow`, `hardware_pinout_pneumatic`, `comparison_matrix`, `spatial_topology`) plus `<memory_root>/Templates/` overrides |
| [`pre-commit-gate/SKILL.md`](../../../Homunculus/skills/pre-commit-gate/SKILL.md) | **Called By** | `pre-commit-gate` | Stage Y batch-renders deferred `.svg` diagrams with `--strict` collision checking |
| [`test_core_skills.py`](../../../Homunculus/tests/test_core_skills.py) | **Tested By** | `tests/` | `test_render_diagram_svg` |

---

### Block 7: Doc_And_Card_Studio ([`skills/doc-and-card-studio/`](../../../Homunculus/skills/doc-and-card-studio/SKILL.md))

| Interacting Script / Module | Direction | Target Skill / Layer | Interacting Functions, CLI Flags & Code Names |
| :--- | :--- | :--- | :--- |
| [`audit_repo_docs.py`](../../../Homunculus/skills/doc-and-card-studio/scripts/audit_repo_docs.py) | **Owned** | `doc-and-card-studio` | `load_brand_config`, `audit_markdown_file`, `--repo-type`, `--repo-root`, `--fail-on-tbd`, `--skip-image-check`, `--brand-config` (`.homunculus_brand.json`), `--no-brand-config` |
| [`format_image.py`](../../../Homunculus/skills/doc-and-card-studio/scripts/format_image.py) | **Owned** | `doc-and-card-studio` | `_inspect_png_stdlib`, `is_already_formatted`, `format_single_image`, `format_combined_pair`, `--combine`, `--inspect`, `--card-size`, `--radius` |
| `audit_repo_docs.py` $\leftrightarrow$ `format_image.py` | **Imports** | Intra-Skill | `audit_repo_docs.py` imports `_inspect_png_stdlib` and `is_already_formatted` from `format_image.py` (zero top-level `PIL`/`numpy` imports) |
| [`render_diagram.py`](../../../Homunculus/skills/visual-studio/scripts/render_diagram.py) | **Called By** | `visual-studio` | Calls `format_image.py` on `--github-card` showcase exports |
| [`sandbox_runner.py`](../../../Homunculus/skills/engineering-sandbox/scripts/sandbox_runner.py) & [`pre-commit-gate/SKILL.md`](../../../Homunculus/skills/pre-commit-gate/SKILL.md) | **Called By** | Sandbox & Release Gate | Invokes `audit_repo_docs.py` with `--skip-image-check` in `compare-light` / `compare-full` frames and Stage Y release checks |
| [`test_core_skills.py`](../../../Homunculus/tests/test_core_skills.py) | **Tested By** | `tests/` | `test_zero_toplevel_third_party_imports` + `test_audit_repo_docs_and_stdlib_png_helper` |

---

### Block 8: Pre_Commit_Gate ([`skills/pre-commit-gate/`](../../../Homunculus/skills/pre-commit-gate/SKILL.md))

| Interacting Script / Module | Direction | Target Skill / Layer | Interacting Functions, CLI Flags & Code Names |
| :--- | :--- | :--- | :--- |
| [`pre-commit-gate/SKILL.md`](../../../Homunculus/skills/pre-commit-gate/SKILL.md) | **Owned** | `pre-commit-gate` | Orchestrator-only release checklist (`X -> Y -> Z` sequence; `[GATE BLOCKED]` stop condition; zero standalone `.py` script) |
| [`sync_memory.py`](../../../Homunculus/skills/project-memory/scripts/sync_memory.py) | **Calls** | `project-memory` | Stage X: `--save-handoff`, `--sync-trees`, `--sync-tasks`, `--sync-visuals`, `--export-canvas`, `--audit` |
| [`render_diagram.py`](../../../Homunculus/skills/visual-studio/scripts/render_diagram.py) & [`audit_repo_docs.py`](../../../Homunculus/skills/doc-and-card-studio/scripts/audit_repo_docs.py) | **Calls** | `visual-studio` & `doc-and-card-studio` | Stage Y: `--strict` diagram rebuilds + `audit_repo_docs.py` with `--skip-image-check` |
| [`verify_claims.py`](../../../Homunculus/skills/claim-verification/scripts/verify_claims.py), [`audit_portability.py`](../../../Homunculus/scripts/audit_portability.py), [`audit_data_boundary.py`](../../../Homunculus/scripts/audit_data_boundary.py), & [`audit_skill_hygiene.py`](../../../Homunculus/skills/skill-architect/scripts/audit_skill_hygiene.py) | **Calls** | Verification & Firewall Oracles | Stage Z1–Z4: `--strict-provenance`, portability scan, `--compartment cleanroom` + `--worktree`, and `--audit` + `--strict-structure` |

---

### Block 9: Teach_Me ([`skills/teach-me/`](../../../Homunculus/skills/teach-me/SKILL.md) — Staged Expansion Priority #1)

| Interacting Script / Module | Direction | Target Skill / Layer | Interacting Functions, CLI Flags & Code Names |
| :--- | :--- | :--- | :--- |
| [`teach_brief.py`](../../../Homunculus/skills/teach-me/scripts/teach_brief.py) & [`brief_authoring_playbook.md`](../../../Homunculus/skills/teach-me/references/brief_authoring_playbook.md) | **Owned** | `teach-me` | `build_brief_slug`, `build_chat_rails`, `build_chat_card_template`, `init_brief`, `verify_brief_structure`, `verify_and_stamp_brief`, `rename_brief_clean`, `promote_brief`, `--init-brief`, `--rename-clean`, `--verify`, `--list`, `--promote` |
| [`homunculus_paths.py`](../../../Homunculus/scripts/homunculus_paths.py) | **Imports** | Core Framework | `resolve_workspace_config` resolves `study_briefs_root` (`HOMUNCULUS_BRIEFS_ROOT` -> `.homunculus.json` `study_briefs_dir` -> `<memory_root.parent>/study_briefs`) |
| [`verify_claims.py`](../../../Homunculus/skills/claim-verification/scripts/verify_claims.py) | **Calls / Guarded By** | `claim-verification` | Subprocess `verify_claims.py` with `--target`, `--sources`, and `--json`; evaluates `<!-- FIRST-PRINCIPLES-THEORY:START/END -->` `[CALC]` math, blocks `THEORY_ZONE_EVASION_BLOCKED`, and rejects `study_briefs/` in `--sources` via `STUDY_BRIEF_SOURCE_REJECTED` |
| [`inspect_hardware_ecosystem.py`](../../../Homunculus/skills/subagent-orchestrator/scripts/inspect_hardware_ecosystem.py) | **Calls** | `subagent-orchestrator` | Delegated subagent runs `inspect_hardware_ecosystem.py` with `--repo` when mechanical/CAD context overlaps are needed |
| [`build_adapters.py`](../../../Homunculus/scripts/build_adapters.py) & `templates/ignore/` | **Quarantine Layer** | Core Framework | Non-destructively syncs `**/study_briefs/*`, `!**/study_briefs/README.md`, and `!**/study_briefs/.gitkeep` into `.geminiignore`, `.cursorignore`, and `.claudeignore` |
| [`co-engineering-partner.md`](../../../Homunculus/rules/co-engineering-partner.md) | **Governed By** | Always-On Rule | Enforces throw-away subagent isolation (`invoke_subagent`) and verbatim `┏━━ 🎓 TEACH-ME // BRIEF+ ... ━━┓` card relay |
| [`test_teach_me.py`](../../../Homunculus/tests/test_teach_me.py) & [`test_core_skills.py`](../../../Homunculus/tests/test_core_skills.py) | **Tested By** | `tests/` | `TestTeachMe` + `test_zero_toplevel_third_party_imports` |

---

### Block 10: Author_Voice_Cadence ([`addons/author-voice-cadence/`](../../../Homunculus/addons/author-voice-cadence/SKILL.md) — Drop-In Add-On)

| Interacting Script / Module | Direction | Target Skill / Layer | Interacting Functions, CLI Flags & Code Names |
| :--- | :--- | :--- | :--- |
| [`extract_voice_cadence.py`](../../../Homunculus/addons/author-voice-cadence/scripts/extract_voice_cadence.py) | **Owned** | `author-voice-cadence` | `load_discord_gdpr_package`, `load_standalone_file`, `compute_deep_stylometrics`, `extract_stratified_exemplars`, `--inbox`, `--scope`, `--min-words`, `--output` |
| [`build_adapters.py`](../../../Homunculus/scripts/build_adapters.py) & `templates/ignore/` | **Discovered By** | Core Framework | `_discover_skills_and_addons` registers `addons/`; ignore templates quarantine `**/corpus_inbox/*` |
| [`verify_claims.py`](../../../Homunculus/skills/claim-verification/scripts/verify_claims.py) & [`sync_memory.py`](../../../Homunculus/skills/project-memory/scripts/sync_memory.py) | **Calls** | `claim-verification` & `project-memory` | Enforces factual claim verification (`verify_claims.py`) and memory hygiene (`sync_memory.py` `--audit`) over stylistic rewrites |
| [`test_core_skills.py`](../../../Homunculus/tests/test_core_skills.py) & [`test_adapters.py`](../../../Homunculus/tests/test_adapters.py) | **Tested By** | `tests/` | `test_extract_voice_cadence_cleanroom` + `test_optional_addon_removal_resilience_and_cli_normalization` |

---

### Block 11: Core Framework Scripts, Hooks & Installers (`scripts/`, `templates/hooks/`, `install.sh`, `install.ps1`)

| Interacting Script / Module | Direction | Target Skill / Layer | Interacting Functions, CLI Flags & Code Names |
| :--- | :--- | :--- | :--- |
| [`homunculus_paths.py`](../../../Homunculus/scripts/homunculus_paths.py) | **Core Resolver** | Imported by `4` `.py` modules + `2` installers | `detect_os_tier`, `resolve_homunculus_root`, `resolve_workspace_config`, `probe_runtime_capabilities`, `write_workspace_config`, `.homunculus.json` (`memory_dir`, `study_briefs_dir`) |
| [`build_adapters.py`](../../../Homunculus/scripts/build_adapters.py) | **Adapter Builder** | Scans `rules/`, `skills/`, `addons/`, `templates/` | `build_reference_adapters_in_repo`, `apply_workspace_adapters`, `--build-repo-adapters`, `--workspace`, `--install-git-hooks`, non-destructive `.geminiignore` / `.cursorignore` / `.claudeignore` sync |
| [`audit_portability.py`](../../../Homunculus/scripts/audit_portability.py) | **Portability Oracle** | Scans entire `Homunculus/` tree | `audit_repository`, `_audit_python_stdlib_only`, `_check_cleanroom_hashes`, `--repo` / `--repo-root` |
| [`audit_data_boundary.py`](../../../Homunculus/scripts/audit_data_boundary.py) | **Compartment Firewall** | Git hooks & `pre-commit-gate` | `BoundaryPolicy`, `load_boundary_config` (`homunculus_safety.json`), `audit_staged`, `audit_push_stdin`, `audit_worktree`, UTF-8/UTF-16/UTF-32 secret & path scanning |
| [`install.sh`](../../../Homunculus/install.sh), [`install.ps1`](../../../Homunculus/install.ps1), [`pre-commit.sh`](../../../Homunculus/templates/hooks/pre-commit.sh), & [`pre-push.sh`](../../../Homunculus/templates/hooks/pre-push.sh) | **Bootstrap & Hooks** | Workstation & Target Repos | Wire `.homunculus.json`, client adapters, staged secret/memory audits (`--staged`), and remote/author locks (`--push-stdin`) |
