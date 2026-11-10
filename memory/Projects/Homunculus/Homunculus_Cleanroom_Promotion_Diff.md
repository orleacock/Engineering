---
title: "Homunculus Workstation-to-Clean-Room Validation & Promotion Diff Manifest"
project: "Homunculus"
entity: "Alchemical-3D"
compartment: "private"
note_type: "reference"
last_synced: "2026-11-10"
---

# 🔬 Homunculus Single-Source Clean-Room Repository (`Alchemical3D/Homunculus`) Validation & Promotion Manifest

> **Canonical Reference Role**: This document is the authoritative local validation and promotion ledger for the **Single-Source Clean-Room Repository** (`/home/orin/Projects/Alchemical3D/Homunculus`, remote `git@github-alchemical:Alchemical-3D/Homunculus.git`).
> **Current Synchronization State (`2026-11-10`)**: **Consolidated Single-Source Clean-Room (`v0.1.0` at `31aa0cb0a918`, `102` tracked files, `0` duplicate copies on disk or in `orleacock/Engineering.git`)** following retirement of the duplicate `Engineering/Homunculus` folder and removal of `Homunculus/` from the parent `Engineering` Git index (`49 / 49` unit tests `OK` across `7` suites, `SBX-20261110_143655-1ecf0fa7` `Controls: 4/4, +faults: 2/2`).
> **Usage Law**: Consult and update this document whenever staging or promoting a new feature, bugfix, reference guide, or script into `/home/orin/Projects/Alchemical3D/Homunculus`. *(For an optional, non-authoritative maintainer lookup of cross-skill couplings and naming hygiene, see [`Homunculus_Script_Skill_Interaction_Matrix.md`](Homunculus_Script_Skill_Interaction_Matrix.md).)*

---

## 1. Locked Architectural Boundaries (`Section A–D Decisions`)

1. **`Option A1` — Vendor-Neutral Core Tooling + Local Brand Config (`audit_repo_docs.py`)**:
   - `skills/doc-and-card-studio/scripts/audit_repo_docs.py` ([`Homunculus_Software.md`](Homunculus_Software.md)) ships with `0` hardcoded brand/vendor strings in default mode and supports an optional declarative `.homunculus_brand.json` (`--brand-config` / `--no-brand-config`) loader.
   - Alchemical-3D brand palettes, templates, and affiliate link rules stay strictly local inside `/home/orin/Projects/Engineering/.homunculus_brand.json` and `/home/orin/Projects/Engineering/memory/Templates/`.
   - **Core Functional vs. Informative Publisher Links**: Informative publisher support links in `Homunculus`'s own documentation (`Homunculus/README.md`, `docs/Quick_Start_and_Setup_Guide.md` pointing users to the Alchemical-3D Discord for help with `Homunculus`) are appropriate, whereas functional tooling/templates (`audit_repo_docs.py`, `doc_templates.md`, `render_diagram.py`) must never inject Alchemical-3D brand assets into buyers' repositories.
2. **`Option B1` — Zero Legacy Regex Tokens (`audit_skill_hygiene.py`)**:
   - Removed legacy `|sync_vault_status` from `skills/skill-architect/scripts/audit_skill_hygiene.py` ([`Homunculus_Software.md`](Homunculus_Software.md)) so `memory_dossier_or_tree` matches only canonical `Homunculus` tokens (`Projects/<Project>|AUTO-TREE|sync_memory|project-memory|memory_root`).
3. **`Option C1` — Email-Client Neutrality (`gmail-workspace-assistant` Kept Workstation-Local)**:
   - Because buyers use their own email clients and services, `gmail-workspace-assistant` lives outside `Homunculus` at `/home/orin/Projects/Engineering/scripts/gmail_mcp/gmail-workspace-assistant/SKILL.md` (wired into `~/.gemini/config/skills/` and `.agents/skills/` by `bootstrap_workstation.sh`), and `0` Clean-Room docs reference `addons/gmail-workspace-assistant/SKILL.md`.
4. **`Section D` — Parent-Station vs. Clean-Room Deliverable Memory & `TIER0`–`TIER5` Promotion Contract ([`Homunculus_Stateful_Memory_Deployment_Plan.md`](Homunculus_Stateful_Memory_Deployment_Plan.md))**:
   - **Live Parent Station Power (`Engineering/memory/`)**: On the parent workstation (and on any end-user workstation after `Homunculus` is deployed), absolute `local_path` repository bindings (`/home/orin/Projects/...`), station project names (`Pneuma`, `Alembic`, `NEA`), and entity-partitioned search indexes (`Directory/<Entity>_memory_index.json`) are first-class citizens—zero local turns are wasted scrubbing native workstation paths from the private parent vault.
   - **Deterministic `TIER0`–`TIER5` Clean-Room Promotion Filter (`Engineering/memory/` $\rightarrow$ `Alchemical3D/Homunculus`)**:
     - **Promotes to Clean-Room Deliverable (`TIER0` & `TIER1` Universal Engine Laws Only)**: Distilled generic contracts in `scripts/script_contracts.json`, `#L1-L55` `Contract :` pointers in `.py` scripts, generic starter templates (`templates/memory/Decision_Profile.md`, `templates/memory/AGENTS.md`, `templates/memory/Project_Lessons_Learned.md`), and `tests/test_*.py` regression suites (`0` `/home/orin` host paths or personal project names—verified by `audit_portability.py` and `audit_data_boundary.py --compartment cleanroom`).
     - **Stays Station-Local (`TIER2`–`TIER4` Dev-Cycle & Historical Narratives)**: Full project dossiers (`Projects/*/*.md`), absolute `local_path` bindings, `Directory/<Entity>_memory_index.json`, `TIER2` active dev-cycle full-context sections, and `TIER3`–`TIER4` `Archive/` post-mortems remain strictly inside `/home/orin/Projects/Engineering/memory/`.
     - **Superseded / Retired (`TIER5`)**: Excluded from both Clean-Room promotion and default active parent recall (`--recall` / `--preflight`).

---

## 2. Full Workstation & Clean-Room Audit Scorecard (`2026-11-10`)

| Audit / Verification Gate | Command / Oracle | Target Scope | Result & Receipt |
| :--- | :--- | :--- | :--- |
| **1. Single-Source Clean-Room Authority (`LL-WS-07`)** | `python3 /home/orin/Projects/Engineering/scripts/version_manager.py --status` | `/home/orin/Projects/Alchemical3D/Homunculus` (`102` files; `0` duplicate copies in `Engineering/`) | **`PASS`** (`v0.1.0` baseline `31aa0cb0a918`, `0` duplicate copies) |
| **2. Workstation Symlink & Hook Integrity** | `bash /home/orin/Projects/Engineering/scripts/bootstrap_workstation.sh --check --update-obsidian --compat-symlinks` | `~/.gemini/config/{rules,skills,hooks.json}`, `.agents/skills/*`, `.git/hooks/{pre-commit,pre-push}` across `Engineering` + 10 `Alchemical3D/*` repos, `~/.config/obsidian/obsidian.json` | **`PASS`** (`0` errors; `0` dangling symlinks; `Homunculus_Backup`, legacy vault, and `AI_Skill_Project` retired from disk & Git index) |
| **3. Dual-Mode Memory Containment & Structure** | `python3 .../sync_memory.py --memory-root /home/orin/Projects/Engineering/memory --sync-trees --sync-tasks --sync-visuals --export-canvas --audit` | `/home/orin/Projects/Engineering/memory` (`obsidian` mode) | **`PASS`** (`3` entities: `Alchemical-3D`, `NetCom`, `Orin_Workstation` \| `12` projects \| `0` violations) |
| **4. Clean-Room & Cross-OS Portability Gate** | `python3 .../audit_portability.py --repo /home/orin/Projects/Alchemical3D/Homunculus` | `/home/orin/Projects/Alchemical3D/Homunculus` | **`PASS`** (`102` files scanned \| `0` violations \| `0` third-party vendor names `Fabreeko`/`KB-3D`/`West3D`) |
| **5. 3-Compartment Data-Boundary & Secret Firewall** | `python3 .../audit_data_boundary.py --repo /home/orin/Projects/Engineering --worktree` & `--all-in-root /home/orin/Projects/Alchemical3D` | `private` (`Engineering`), `public` (`9` `Alchemical3D` OSS repos), and `cleanroom` (`Alchemical3D/Homunculus`) | **`PASS`** (`11 / 11` repositories `PASS`, `0` violations) |
| **6. Skill Architect Hygiene & Synergy Audit** | `python3 .../audit_skill_hygiene.py --repo-root /home/orin/Projects/Alchemical3D/Homunculus --strict-structure` | `3` Always-On Rules, `9` Core Skills + `2` Add-Ons, `5` References, `docs/*.md` | **`PASS`** (`Load-Bearing Defects: 0` \| `Turn-Waste Hazards: 0` \| `Rule-to-Rule Overlaps: 0` \| `Cross-Skill Overlaps: 0` \| `Orphan Scripts: 0`) |
| **7. Documentation & Alerts Audit** | `python3 .../audit_repo_docs.py --repo-root /home/orin/Projects/Alchemical3D/Homunculus --skip-image-check /home/orin/Projects/Alchemical3D/Homunculus` | `56` Markdown files in `/home/orin/Projects/Alchemical3D/Homunculus` | **`PASS`** (`56` files checked, `0` errors) |
| **8. Automated Unit & Integration Test Suite** | `python3 -m unittest discover -s /home/orin/Projects/Alchemical3D/Homunculus/tests -p "test_*.py" -v` | `test_foundation.py`, `test_data_safety.py`, `test_adapters.py`, `test_project_memory.py`, `test_claim_verification.py`, `test_core_skills.py`, `test_teach_me.py` | **`PASS`** (`49 / 49` tests `OK` across `7` suites) |
| **9. CoW Sandbox Verification Receipts** | `sandbox_runner.py` (`dry-run (+faults)` & `compare-light (+faults)`) | Core engine, 27-group `QUALIFIER_GROUPS`, 3-step legacy retirement, 5-Sprint Stateful Memory Rebuild, and Clean-Room promotion | **`PASS`** across `SBX-20261106_105046-6eb9123f`, `SBX-20261108_160913-c12baab5`, and `SBX-20261109_120538-a29c8228` (`Controls 2/2, +faults 5/5, Live Host Mutations: 0`) |

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
| `addons/hardware-cad-inspector/scripts/inspect_hardware_ecosystem.py` | `1083L` | `FEATURE-08`, `FIX-06` (`INH-01`, `INH-09`, `INH-10`, `INH-12`–`INH-15`), `FIX-09` (`INH-23`), `LL-031` | Eliminated `"Project_Alphatic"` (`INH-01`), removed speculative COTS bore labels (`INH-10`) and speculative `solid_abs_g`/`est_print_abs_g` gram estimates (`INH-23`), added dynamic `<repo_prefix>_` stripping (`INH-09`), restored `\s+-\s+` (`INH-13`), removed `[[WikiLinks]]` (`INH-12`), fixed `product_stems` JSON serialization (`INH-15`), and relocated to `addons/hardware-cad-inspector/` (`LL-031`). |
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
3. **Verify Post-Edit CoW Sandbox Cleanliness**:
   - Run `sandbox_runner.py --mode dry-run --faults --target-dir /home/orin/Projects/Alchemical3D/Homunculus` and confirm `Live Host Mutations: 0` before committing and locking core (`--lock-core`).

---

## 5. Promoted Release Wave 2 (`2026-11-07` — `skills/teach-me/`, `Directory/` Freshness Spine, 7 Functional Test Modules & `LL-027` 2-Tier Rule Diet — `97 / 97` Parity)

### Promoted & Verified (`SBX-20261107_105613-b210d998`, `SBX-20261107_114357-f7c6405e`, `SBX-20261107_115321-71b82997`, `SBX-20261107_115840-d0c27973`)
- **Synchronization State (`2026-11-07T11:58-06:00`)**: **`100%` BYTE-FOR-BYTE IDENTICAL (`97 / 97` files, `0` diff lines)** across `/home/orin/Projects/Engineering/Homunculus` and `/home/orin/Projects/Alchemical3D/Homunculus` (`29/29` unit tests `OK`, `0` portability/boundary/hygiene/doc defects, `Post-Promotion Overlay Changes: +0 ~0 -0`).
- **Promoted Wave 2 Highlights**:
  - **2-Tier Single-Source Rule Diet & Byte-Cap Lock (`LL-027`)**: Condensed `rules/co-engineering-partner.md` to `7,303` B (`894` w; 3-rule `always_on` footprint cut `-42.3%` to `2,609` w / `~3,522` tok/turn), compacted the `AGENTS.md` skill index (`adapters/agents_md/AGENTS.md` = `21,880` B `<= 22,500` B ceiling / `24,000` B hard cap; `CLAUDE.md` = `22,547` B), suppressed workspace `AGENTS.md` double-injection when `antigravity` is active unless `--include-agents-md`, and enforced fail-closed `RULE_BYTE_CAP_EXCEEDED`, `MISNAMED_AGENTS_MD_CASE`, `INVALID_ADAPTER_FRONTMATTER_POLARITY`, and dynamic `ADAPTER_STALE_DRIFT` checks in `audit_skill_hygiene.py`.
  - **Shared Stdlib Dedup + Symlink/`prefer_copy`/`.zip` Isolation**: Centralized `CLEANROOM_FORBIDDEN_SHA256` (`15` SHA-256 digests), `parse_frontmatter_full()`, `strip_yaml_frontmatter()`, and `decode_file_text()` in `scripts/homunculus_paths.py`; switched all skill scripts to `os.path.realpath(__file__)` / `Path(__file__).resolve()`; co-bundled `homunculus_paths.py` into Cowork `.zip` bundles and `prefer_copy=True` skill copies; and verified isolated `python3 -I` execution across symlinked, copied, and `.zip`-extracted scripts (`29/29` unit tests `OK`).
  - **Promoted Core Skill (`skills/teach-me/`), `Directory/` Freshness Spine & 7 Domain Test Suites**: Promoted `skills/teach-me/{SKILL.md,references/brief_authoring_playbook.md,scripts/teach_brief.py}`, `templates/hooks/post-worktree-sync.sh`, and the 7 functional test modules (`test_foundation.py`, `test_data_safety.py`, `test_adapters.py`, `test_project_memory.py`, `test_claim_verification.py`, `test_core_skills.py`, `test_teach_me.py`, replacing the 5 legacy `test_phase*.py` files).
