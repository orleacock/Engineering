---
title: "Homunculus Workstation-to-Clean-Room Validation & Promotion Diff Manifest"
project: "Homunculus"
entity: "Alchemical-3D"
compartment: "private"
note_type: "reference"
last_synced: "2026-11-06"
---

# 🔬 Homunculus Workstation (`Engineering/Homunculus`) vs. Clean-Room (`Alchemical3D/Homunculus`) Validation & Promotion Diff Manifest

> **Canonical Reference Role**: This document is the authoritative local validation and promotion ledger comparing the dogfooded **Parent Workstation Deployment** (`/home/orin/Projects/Engineering/Homunculus`) against the **Clean-Room Commercial Repository** (`/home/orin/Projects/Alchemical3D/Homunculus`).
> **Current Synchronization State (`2026-11-06`)**: **`100%` BYTE-FOR-BYTE IDENTICAL (`91 / 91` files, `0` diff lines)** following the Section A–D architectural review (`Option A1`, `Option B1`, `Option C1`, `Option B2-Yes`) and CoW sandbox promotion (`SBX-20261106_104836-ab78d9a8` & `SBX-20261106_105046-6eb9123f`).
> **Usage Law**: Consult and update this document whenever staging or promoting a new feature, bugfix, reference guide, or script from `/home/orin/Projects/Engineering/Homunculus` into `/home/orin/Projects/Alchemical3D/Homunculus`. *(For an optional, non-authoritative maintainer lookup of cross-skill couplings and naming hygiene, see [`Homunculus_Script_Skill_Interaction_Matrix.md`](Homunculus_Script_Skill_Interaction_Matrix.md).)*

---

## 1. Locked Architectural Boundaries (`Section A–D Decisions`)

1. **`Option A1` — Vendor-Neutral Core Tooling + Local Brand Config (`audit_repo_docs.py`)**:
   - [`audit_repo_docs.py`](../../../Homunculus/skills/doc-and-card-studio/scripts/audit_repo_docs.py) ships with `0` hardcoded brand/vendor strings in default mode and supports an optional declarative `.homunculus_brand.json` (`--brand-config` / `--no-brand-config`) loader.
   - Alchemical-3D brand palettes, templates, and affiliate link rules stay strictly local inside `/home/orin/Projects/Engineering/.homunculus_brand.json` and `/home/orin/Projects/Engineering/memory/Templates/`.
   - **Core Functional vs. Informative Publisher Links**: Informative publisher support links in `Homunculus`'s own documentation (`Homunculus/README.md`, `docs/Quick_Start_and_Setup_Guide.md` pointing users to the Alchemical-3D Discord for help with `Homunculus`) are appropriate, whereas functional tooling/templates (`audit_repo_docs.py`, `doc_templates.md`, `render_diagram.py`) must never inject Alchemical-3D brand assets into buyers' repositories.
2. **`Option B1` — Zero Legacy Regex Tokens (`audit_skill_hygiene.py`)**:
   - Removed legacy `|sync_vault_status` from [`audit_skill_hygiene.py`](../../../Homunculus/skills/skill-architect/scripts/audit_skill_hygiene.py#L779) so `memory_dossier_or_tree` matches only canonical `Homunculus` tokens (`Projects/<Project>|AUTO-TREE|sync_memory|project-memory|memory_root`).
3. **`Option C1` — Email-Client Neutrality (`gmail-workspace-assistant` Kept Workstation-Local)**:
   - Because buyers use their own email clients and services, `gmail-workspace-assistant` lives outside `Homunculus` at `/home/orin/Projects/Engineering/scripts/gmail_mcp/gmail-workspace-assistant/SKILL.md` (wired into `~/.gemini/config/skills/` and `.agents/skills/` by `bootstrap_workstation.sh`).
   - As a result, `/home/orin/Projects/Engineering/Homunculus` and `/home/orin/Projects/Alchemical3D/Homunculus` have **zero file-set or adapter divergence** (`91 / 91` files match 1-to-1).

---

## 2. Full Workstation & Clean-Room Audit Scorecard (`2026-11-06T10:50-06:00`)

| Audit / Verification Gate | Command / Oracle | Target Scope | Result & Receipt |
| :--- | :--- | :--- | :--- |
| **1. Byte-for-Byte Engine Parity (`Engineering` $\leftrightarrow$ `Alchemical3D`)** | `diff -rq -x .git -x __pycache__ /home/orin/Projects/Engineering/Homunculus /home/orin/Projects/Alchemical3D/Homunculus` | All `91` files in both repositories | **`PASS`** (`91 / 91` files `100%` byte-for-byte identical; `0` diff lines) |
| **2. Workstation Symlink & Hook Integrity** | `bash /home/orin/Projects/Engineering/scripts/bootstrap_workstation.sh --check --update-obsidian --compat-symlinks` | `~/.gemini/config/{rules,skills,hooks.json}`, `.agents/skills/*`, `.git/hooks/{pre-commit,pre-push}` across `Engineering` + 10 `Alchemical3D/*` repos, `~/Documents/Obsidian_Notes`, `~/.config/obsidian/obsidian.json` | **`PASS`** (`0` errors; `0` dangling symlinks; `Homunculus_Backup`, `Obsidian_Notes`, and `AI_Skill_Project` retired from disk & Git index) |
| **3. Dual-Mode Memory Containment & Structure** | `python3 .../sync_memory.py --memory-root /home/orin/Projects/Engineering/memory --sync-trees --sync-tasks --sync-visuals --export-canvas --audit` | `/home/orin/Projects/Engineering/memory` (`obsidian` mode) | **`PASS`** (`3` entities: `Alchemical-3D`, `NetCom`, `Orin_Workstation` \| `12` projects \| `83` files \| `0` violations) |
| **4. Clean-Room & Cross-OS Portability Gate** | `python3 .../audit_portability.py --repo /home/orin/Projects/Alchemical3D/Homunculus` | `/home/orin/Projects/Alchemical3D/Homunculus` & `/home/orin/Projects/Engineering/Homunculus` | **`PASS`** (`91` files scanned \| `0` violations \| `0` third-party vendor names `Fabreeko`/`KB-3D`/`West3D`) |
| **5. 3-Compartment Data-Boundary & Secret Firewall** | `python3 .../audit_data_boundary.py --repo /home/orin/Projects/Engineering --worktree` & `--all-in-root /home/orin/Projects/Alchemical3D` | `private` (`Engineering`), `public` (`9` `Alchemical3D` OSS repos), and `cleanroom` (`Alchemical3D/Homunculus`) | **`PASS`** (`11 / 11` repositories `PASS`, `0` violations) |
| **6. Skill Architect Hygiene & Synergy Audit** | `python3 .../audit_skill_hygiene.py --repo-root /home/orin/Projects/Alchemical3D/Homunculus --strict-structure` | `3` Always-On Rules (`4,417w`), `8` Core Skills + `1` Add-On (`7,895w`), `4` References (`6,206w`) | **`PASS`** (`Load-Bearing Defects: 0` \| `Turn-Waste Hazards: 0` \| `Rule-to-Rule Overlaps: 0` \| `Cross-Skill Overlaps: 0` \| `Orphan Scripts: 0`) |
| **7. Documentation & Alerts Audit** | `python3 .../audit_repo_docs.py --repo-root /home/orin/Projects/Alchemical3D/Homunculus --skip-image-check /home/orin/Projects/Alchemical3D/Homunculus` | `17` Markdown files in `/home/orin/Projects/Alchemical3D/Homunculus` | **`PASS`** (`17` files checked, `0` errors) |
| **8. Automated Unit & Integration Test Suite** | `python3 -m unittest discover -s /home/orin/Projects/Alchemical3D/Homunculus/tests -p "test_*.py" -v` | `test_phase1_foundation.py`, `test_phase2a_data_safety.py`, `test_phase2b_adapters.py`, `test_phase3a_memory.py`, `test_phase3b_skills.py` | **`PASS`** (`25 / 25` tests `OK` in `4.59s`, including 27-group `QUALIFIER_GROUPS` + unspecified-clause regression test) |
| **9. CoW Sandbox Verification Receipts** | `sandbox_runner.py` (`dry-run (+faults)` & `compare-light (+faults)`) | Core engine, 27-group `QUALIFIER_GROUPS`, 3-step legacy retirement, and Clean-Room promotion | **`PASS`** across `SBX-20261106_082824-c7325eea`, `SBX-20261106_083332-1b3c07be`, `SBX-20261106_094659-44e3f023`..`2e753103`, `SBX-20261106_103955-5163077a` (`Controls 2/2, +faults 6/6`), `SBX-20261106_104836-ab78d9a8` (`Pre-Promotion Controls 7/7, +faults 2/2`), and `SBX-20261106_105046-6eb9123f` (`Post-Promotion Controls 7/7, +faults 2/2, Overlay Changes: 0`) |

---

## 3. Promoted Feature & Fix Manifest (`2026-11-06` Cutover Release — `28` Files Promoted)

### 3.1 New Files Promoted to Clean-Room (`7` Files)

| Relative Path in `Homunculus/` | Lines | Feature / Fix ID | Purpose & Clean-Room Verification |
| :--- | :--- | :--- | :--- |
| `addons/author-voice-cadence/corpus_inbox/.gitkeep` | `0L` | `FIX-11` (`INH-29`) | Keeps empty `addons/author-voice-cadence/corpus_inbox/` tracked by Git on fresh clones. |
| `skills/doc-and-card-studio/references/doc_templates.md` | `271L` | `FEATURE-09` | On-demand (`0` always-on token tax) modular documentation skeletons (`README.md`, `BOM.md`, `Print_Settings.md`, `Assembly_Guide.md`, `ALPHA_&_DIRECTION.md`, plus Software/CLI `README.md`). |
| `templates/diagrams/Diagram_Blueprints/Column_DataFlow_Blueprint.md` | `203L` | `FEATURE-06` (`INH-03`) | Built-in vendor-neutral `column_dataflow` SVG archetype blueprint (`blueprint_id: column_dataflow`). |
| `templates/diagrams/Diagram_Blueprints/Engineering_Comparison_Card_Blueprint.md` | `99L` | `FEATURE-06` (`INH-03`) | Built-in vendor-neutral `comparison_card` SVG archetype blueprint (`blueprint_id: comparison_card`). |
| `templates/diagrams/Diagram_Blueprints/Hardware_Pinout_and_Pneumatic_Blueprint.md` | `198L` | `FEATURE-06` (`INH-03`) | Built-in vendor-neutral `hardware_pinout` SVG archetype blueprint (`blueprint_id: hardware_pinout`). |
| `templates/diagrams/Diagram_Blueprints/Layered_Architecture_Blueprint.md` | `174L` | `FEATURE-06` (`INH-03`) | Built-in vendor-neutral `layered_arch` SVG archetype blueprint (`blueprint_id: layered_arch`). |
| `templates/diagrams/Diagram_Blueprints/Spatial_Topology_Blueprint.md` | `69L` | `FEATURE-06` (`INH-03`) | Built-in vendor-neutral `spatial_topology` SVG archetype blueprint (`blueprint_id: spatial_topology`). |

### 3.2 Modified Files Promoted to Clean-Room (`21` Files)

| Relative Path in `Homunculus/` | Line Count | Feature / Fix IDs | Summary of Promoted Changes |
| :--- | :--- | :--- | :--- |
| `scripts/audit_data_boundary.py` | `833L` | `FIX-13` (`INH-38`) | Restricted `CLEANROOM_FORBIDDEN_SHA256` to `("cleanroom", "homunculus")` and passed `args.all_in_root` to `load_boundary_config()`. |
| `scripts/audit_portability.py` | `378L` | `FIX-08` (`INH-22`) | Added `--repo-root` CLI flag alias alongside `--repo`. |
| `skills/project-memory/scripts/sync_memory.py` | `2638L` | `FEATURE-01`–`FEATURE-05`, `FIX-07` (`INH-16`), `FIX-09` (`INH-11`) | Targeted `--section` reader (`FEATURE-01`), `--tasks`/`--recommend` (`FEATURE-02`), `--tbd-ledger` (`FEATURE-03`), `--sync-trees` (`FEATURE-04`), dynamic `--export-canvas`/`.base`/`graph.json` (`FEATURE-05`), `WIKILINK_SYNTAX_FORBIDDEN` check (`INH-16`), and unit-aware STEP parsing (`INH-11`). |
| `skills/project-memory/SKILL.md` | `118L` | `FEATURE-01`–`FEATURE-05` | Documented `--section`, `--tasks`/`--recommend`, `--tbd-ledger`, `--sync-trees`, and `--export-canvas`. |
| `skills/claim-verification/scripts/verify_claims.py` | `2804L` | `FIX-07` (`INH-17`), `FIX-08`, `FIX-09` (`INH-25`), `FIX-14` (`LL-021`) | Expanded `QUALIFIER_GROUPS` to `27` multi-domain component groups (`id`, `od`, `infill`, `pullup`, `pulldown`, `gate`, `magnet`, `bearing`, `heatset`, `bowden`, `rod`, `nozzle`, `belt`, `pulley`, `standoff`, `spring`, `dowel`, `bushing`, `oring`, `thermistor`, `heater`, `fan`, `fuse`, `resistor`, `capacitor`, `inductor`, `conduit`), suppressed negated/unspecified qualifier clauses (`is not specified`), unquoted backticked `Ø` diameter quantities, removed `"g"`/`"m"`/`"s"` from `AMBIGUOUS_LOWER_SPACED_UNITS` (`INH-25`), and added `--draft` alias. |
| `skills/subagent-orchestrator/scripts/inspect_hardware_ecosystem.py` | `1083L` | `FEATURE-08`, `FIX-06` (`INH-01`, `INH-09`, `INH-10`, `INH-12`–`INH-15`), `FIX-09` (`INH-23`) | Eliminated `"Project_Alphatic"` (`INH-01`), removed speculative COTS bore labels (`INH-10`) and speculative `solid_abs_g`/`est_print_abs_g` gram estimates (`INH-23`), added dynamic `<repo_prefix>_` stripping (`INH-09`), restored `\s+-\s+` (`INH-13`), removed `[[WikiLinks]]` (`INH-12`), and fixed `product_stems` JSON serialization (`INH-15`). |
| `skills/subagent-orchestrator/references/orchestration_playbooks.md` | `235L` | `FEATURE-10` | Full 4-section subagent dispatch playbook with **Zero Invented Traits** guardrails. |
| `skills/subagent-orchestrator/references/oracle_cli_cheatsheet.md` | `91L` | `FEATURE-10` | Complete CLI cheat sheet for `FEATURE-01`–`FEATURE-08` flags and exit codes. |
| `skills/engineering-sandbox/scripts/sandbox_runner.py` | `1522L` | `FIX-08` (`INH-18`–`INH-22`), `FIX-09` (`INH-26`), `INH-39` | Enforced `VALIDATOR_CRASH` / `WRONG_FAULT_SIGNATURE` (`INH-18`), preferred `transcript_full.jsonl` (`INH-19`), safe `compare-*` default `target_dirs` (`INH-20`–`INH-22`), bare `[TBD]` regex (`INH-26`), and fault `"cmd"` fallback (`INH-39`). |
| `skills/engineering-sandbox/references/frame_playbooks.md` | `167L` | `FEATURE-11` | Expanded sandbox frame playbooks including **Archetype 4: Invented / Speculative Trait Escape**. |
| `skills/visual-studio/scripts/render_diagram.py` | `1771L` | `FEATURE-06` (`INH-03`) | Added `--memory-root` discovery across built-in `templates/diagrams/` and `<memory_root>/Templates/`. |
| `skills/visual-studio/SKILL.md` | `61L` | `FEATURE-06` | Updated palette and blueprint discovery documentation. |
| `templates/diagrams/Diagram_Palettes.json` | `87L` | `FEATURE-06` (`INH-03`) | Added vendor-neutral `gruvbox_dark` (`gruvbox_local` alias) palette. |
| `skills/doc-and-card-studio/scripts/audit_repo_docs.py` | `721L` | `FEATURE-07` (`Option A1` — `INH-02` & `INH-08`) | Eliminated all hardcoded brand/dummy strings (`kb-3d.com`, `ko-fi.com/alchemical3d`, `discord.gg/aE49DW2xXe`, `Core_Module`/`Drive_Module`/`Flow_Module`) in favor of optional declarative `.homunculus_brand.json` (`--brand-config`). |
| `skills/doc-and-card-studio/SKILL.md` | `59L` | `FEATURE-09`, `FEATURE-12` | Linked `references/doc_templates.md` and `<memory_root>/Standards_and_Specs/Standards_Index.md` discovery. |
| `skills/skill-architect/scripts/audit_skill_hygiene.py` | `1159L` | `FIX-08`, `Option B1` (`INH-04`) | Added `--repo-root` CLI alias and removed legacy `\|sync_vault_status` regex token. |
| `addons/author-voice-cadence/SKILL.md` | `80L` | `FEATURE-13` | Upgraded with 4-Register Calibration Matrix (`Mode A1/A2/B1/B2`), Asymmetric Contractions, and Anti-Parroting Rule. |
| `addons/author-voice-cadence/scripts/extract_voice_cadence.py` | `1413L` | `FIX-10` (`INH-28`) | Scrubbed third-party 3D-printing vendor names (`Fabreeko`, `KB-3D`, `West3D`) from module docstring. |
| `docs/Commands_and_Prompts_Reference.md` | `202L` | `FEATURE-01`–`FEATURE-05` | Added CLI examples for `--section`, `--tasks`/`--recommend`, `--tbd-ledger`, `--sync-trees`, and `--export-canvas`. |
| `tests/test_phase3a_memory.py` | `289L` | `FEATURE-01`–`FEATURE-05`, `FIX-09` | Added unit test coverage for `FEATURE-01`–`FEATURE-05` and STEP unit-scale hardware sync. |
| `tests/test_phase3b_skills.py` | `846L` | `FEATURE-06`–`FEATURE-09`, `FIX-09`, `FIX-11` (`INH-30`), `FIX-14` (`LL-021`) | Added unit test coverage for built-in blueprints, `doc_templates.md`, pure-geometry STEP surface histograms, `.homunculus_brand.json`, dual `addons/`/`skills/` path resolution, and the 27-group `QUALIFIER_GROUPS` + unspecified-clause regression test. |

---

## 4. Standard Promotion Protocol (For Future Workstation $\rightarrow$ Clean-Room Releases)

Whenever dogfooding a new capability in `/home/orin/Projects/Engineering/Homunculus` and promoting it to `/home/orin/Projects/Alchemical3D/Homunculus`:

1. **Keep Workstation-Only Files Outside `Homunculus/`**:
   - Workstation brand config: `/home/orin/Projects/Engineering/.homunculus_brand.json`
   - Workstation compartment config: `/home/orin/Projects/Engineering/homunculus_safety.json`
   - Workstation Gmail MCP & add-on: `/home/orin/Projects/Engineering/scripts/gmail_mcp/`
   - Workstation bootstrap & git hook wrappers: `/home/orin/Projects/Engineering/scripts/`
   - Workstation Dual-Mode Memory vault: `/home/orin/Projects/Engineering/memory/`
2. **Run Pre-Promotion CoW Sandbox Dry-Run (`sandbox_runner.py --mode dry-run --faults --target-dir /home/orin/Projects/Alchemical3D/Homunculus`)**:
   - Verify all 6 gates inside the `/home/orin/Projects/Alchemical3D/Homunculus` CoW overlay before mutating host disk:
     1. `python3 scripts/build_adapters.py --homunculus-root /home/orin/Projects/Alchemical3D/Homunculus --build-repo-adapters`
     2. `python3 scripts/audit_portability.py --repo /home/orin/Projects/Alchemical3D/Homunculus` (`0` violations)
     3. `python3 scripts/audit_data_boundary.py --repo /home/orin/Projects/Alchemical3D/Homunculus --compartment cleanroom --worktree` (`0` violations)
     4. `python3 skills/skill-architect/scripts/audit_skill_hygiene.py --repo-root /home/orin/Projects/Alchemical3D/Homunculus --strict-structure` (`0` defects)
     5. `python3 skills/doc-and-card-studio/scripts/audit_repo_docs.py --repo-root /home/orin/Projects/Alchemical3D/Homunculus --skip-image-check /home/orin/Projects/Alchemical3D/Homunculus` (`0` errors)
     6. `python3 -m unittest discover -s /home/orin/Projects/Alchemical3D/Homunculus/tests -p "test_*.py" -v` (`OK`)
3. **Sync & Verify 100% Byte Parity**:
   - Copy updated engine files to `/home/orin/Projects/Alchemical3D/Homunculus`, run `diff -rq -x .git -x __pycache__ /home/orin/Projects/Engineering/Homunculus /home/orin/Projects/Alchemical3D/Homunculus`, and run a Post-Promotion CoW Sandbox verification (`Overlay Changes: +0 ~0 -0`).

---

## 5. Staged Local Expansion Queue (`Engineering/Homunculus` Only — Clean-Room Untouched Until Approved)

### Expansion Priority #1: Universal Engineering & Technical Learning Engine (`skills/teach-me/` — `Brief+` & Throw-Away Subagent Tutor) + Functional Naming & Rule-Trigger Hardening
- **Current State (`2026-11-06T19:09-06:00`)**: Hardened, refactored onto 7 functional test modules (`27/27` `OK`), scrubbed of all internal build/migration tags (`0` matches), restored `trigger: always_on` Antigravity rule injection across `rules/*.md` + `.agents/rules/` (verified live via probe `c11064d3`), skill-hygiene verified (`0` defects, `~582` tok `teach-me` slash footprint), and CoW sandbox-verified (`SBX-20261106_190903-bcf1c394`: `Controls: 4/4 passed`, `+faults: 3/3 caught`, `Live Host Mutations: 0`) in `/home/orin/Projects/Engineering/Homunculus`.
- **Clean-Room Isolation**: `/home/orin/Projects/Alchemical3D/Homunculus` remains **100% untouched** by `teach-me` and the `tests/` rename (`91` files) until explicit promotion approval.
- **Staged Files in `/home/orin/Projects/Engineering/Homunculus` (`96` Total Tracked Files)**:
  - **New Skill & Playbook Files (`+3`)**:
    1. [`skills/teach-me/SKILL.md`](../../../Homunculus/skills/teach-me/SKILL.md) (`45L`) — Compact Primary-Thread delegation & quarantine gate (`~582` tok).
    2. [`skills/teach-me/references/brief_authoring_playbook.md`](../../../Homunculus/skills/teach-me/references/brief_authoring_playbook.md) (`92L`) — Delegated subagent `Brief+` authoring, `[CALC]` dimensional unit pairings, and `--promote` playbook.
    3. [`skills/teach-me/scripts/teach_brief.py`](../../../Homunculus/skills/teach-me/scripts/teach_brief.py) (`1033L`) — Pure-stdlib CLI (`--init-brief`, `--rename-clean`, `--verify`, `--list`, `--promote`), whole-word `<Subject>_on_<Impact>` slugging, `< 80`-col solid-line datasheet card rails (`┏━━ ... ━━┓` / `┗━━ ... ━━┛`), `THEORY_ZONE_EVASION_BLOCKED` guard, and `VRF-<12hex>` stamping.
  - **Refactored Functional Test Modules (`7` Domain Suites Replacing `5` Legacy `test_phase*` Files)**:
    1. [`tests/test_foundation.py`](../../../Homunculus/tests/test_foundation.py) (`92L` — replaces `test_phase1_foundation.py`)
    2. [`tests/test_data_safety.py`](../../../Homunculus/tests/test_data_safety.py) (`152L` — replaces `test_phase2a_data_safety.py`)
    3. [`tests/test_adapters.py`](../../../Homunculus/tests/test_adapters.py) (`196L` — replaces `test_phase2b_adapters.py`; adds non-destructive `.geminiignore` upgrade sync test)
    4. [`tests/test_project_memory.py`](../../../Homunculus/tests/test_project_memory.py) (`289L` — replaces `test_phase3a_memory.py`)
    5. [`tests/test_claim_verification.py`](../../../Homunculus/tests/test_claim_verification.py) (`391L` — split from `test_phase3b_skills.py`)
    6. [`tests/test_core_skills.py`](../../../Homunculus/tests/test_core_skills.py) (`481L` — split from `test_phase3b_skills.py`)
    7. [`tests/test_teach_me.py`](../../../Homunculus/tests/test_teach_me.py) (`385L` — dedicated `teach-me` + umbrella-org anti-hallucination regression suite)
  - **Modified Core Engine, Rule, Doc & Adapter Files (`~14`)**:
    1. [`scripts/homunculus_paths.py`](../../../Homunculus/scripts/homunculus_paths.py) (`341L`) — Resolves `study_briefs_root` (`HOMUNCULUS_BRIEFS_ROOT` -> `.homunculus.json` `study_briefs_dir` -> `<memory_root.parent>/study_briefs`).
    2. [`scripts/build_adapters.py`](../../../Homunculus/scripts/build_adapters.py) (`626L`) — Strips YAML frontmatter (`_strip_yaml_frontmatter`) when rendering `AGENTS.md`, `CLAUDE.md`, and Cursor `.mdc` files; populates `<workspace>/.agents/rules/*.md` for `--client antigravity`; and non-destructively appends missing context-ignore rules (`**/study_briefs/*`, `!README.md`, `!.gitkeep`) into pre-existing `.geminiignore` / `.cursorignore` / `.claudeignore` files.
    3. [`skills/claim-verification/scripts/verify_claims.py`](../../../Homunculus/skills/claim-verification/scripts/verify_claims.py) (`2998L`) — Innermost-outward git/project entity scoping (`_detect_entity`), compound prefix preservation (`_canonicalize_entity_token`), unambiguous 1-to-1 `dynamic_aliases` vs. fail-closed `ambiguous_umbrellas` (`CROSS_ENTITY_BORROWING` across sibling projects sharing `entity: "Alchemical-3D"` / `"Umbrella-Org"`), `authoritative: false` frontmatter exclusion, `STUDY_BRIEF_SOURCE_REJECTED` firewall, and `FIRST-PRINCIPLES-THEORY` dimensional math verification.
    4. [`rules/co-engineering-partner.md`](../../../Homunculus/rules/co-engineering-partner.md), [`rules/verifiable-accuracy.md`](../../../Homunculus/rules/verifiable-accuracy.md), [`rules/data-and-credential-safety.md`](../../../Homunculus/rules/data-and-credential-safety.md), [`HOMUNCULUS_START_HERE.md`](../../../Homunculus/HOMUNCULUS_START_HERE.md), & [`docs/Commands_and_Prompts_Reference.md`](../../../Homunculus/docs/Commands_and_Prompts_Reference.md) — Added `trigger: always_on` frontmatter to all 3 global rules (`MISSING_RULE_TRIGGER_FRONTMATTER` enforced in `audit_skill_hygiene.py`) and registered `skills/teach-me/SKILL.md` + `teach_brief.py` CLI flags.
    5. `templates/ignore/{.cursorignore,.claudeignore,.geminiignore}` & `adapters/{agents_md/AGENTS.md,claude_code/CLAUDE.md,cursor/rules/homunculus-co-engineering-partner.mdc}` — Synced ignore patterns and rebuilt reference client adapters.
