---
project: "NetCom_Engineering_Assistant"
entity: "NetCom"
compartment: "private"
project_type: "software"
status: "v2.2.3 Hardened"
local_path: "/home/orin/Projects/Engineering/NEA_v2.2.3"
repo_head_sha: "UNTRACKED"
tree_hash: "9e7492e491a3"
checkpoint_head_sha: "UNTRACKED"
checkpoint_tree_hash: "3ce4939d8bf7"
checkpoint_worktree: "untracked"
task_umbrella: "../../Tasks/NetCom_Tasks.md"
last_synced: "2026-11-10"
---

## 🧭 Homunculus Companion Notes & Project Navigation

| Artifact Role | File Link | Purpose |
| :--- | :--- | :--- |
| **Project Hub (`AUTO-TREE`)** | [`NetCom_Engineering_Assistant.md`](NetCom_Engineering_Assistant.md) | Canonical architecture overview, `SESSION-HANDOFF`, `AUTO-TREE`, and `[TBD]` Ledger. |
| **Software Telemetry** | [`NetCom_Engineering_Assistant_Software.md`](NetCom_Engineering_Assistant_Software.md) | Runtime entrypoints, CLI flags, public symbols, and JSON schemas. |
| **Lessons Learned & Post-Mortems** | [`NetCom_Engineering_Assistant_Lessons_Learned.md`](NetCom_Engineering_Assistant_Lessons_Learned.md) | Root-cause post-mortems (`Symptom -> Root Cause -> Permanent Guardrail`). |
| **Project Templates** | [`Templates/`](Templates/) | Project-specific deliverable templates. |
| **Unverified Quarantine Zone** | [`Quarantine/Quarantine_README.md`](Quarantine/Quarantine_README.md) | Holding zone for unverified notes (`[QUARANTINED — DO NOT CITE AS FACT]`). |
| **Active Task Umbrella** | [`NetCom_Tasks.md`](../../Tasks/NetCom_Tasks.md#NetCom_Engineering_Assistant) | Single-writer task tracker for `NetCom` (zero duplicate checkboxes in hub). |

---

# 🏢 NetCom Engineering Assistant (`NEA v2.2.3` Baseline)

> [!IMPORTANT]
> **Strict Entity Separation & Turn-1 Project-Scoped Skill Gate (`nea-copilot-builder` + Module Launchpad)**:
> 1. **Compartment C Boundary**: **NetCom (`netcom1989.com`)** is an independent corporate entity and is **completely separate from Alchemical-3D** (the two entities have no relationship).
> 2. **Mandatory Turn-1 NEA Development Skill & Launchpad Activation**: Before editing any file, instruction, skill, or script—or onboarding a new module—in `/home/orin/Projects/Engineering/NEA_v2.2.3`, **read [`/home/orin/Projects/Engineering/NEA_v2.2.3/.agents/skills/nea-copilot-builder/SKILL.md`](file:///home/orin/Projects/Engineering/NEA_v2.2.3/.agents/skills/nea-copilot-builder/SKILL.md)** and **[`NetCom_Engineering_Assistant_Module_Launchpad`](NetCom_Engineering_Assistant_Module_Launchpad.md)**. This project-scoped skill is intentionally isolated out of `~/.gemini/config/skills/` so it consumes `0` tokens during `Homunculus` and `Alchemical-3D` sessions while enforcing all M365 Copilot Agent Builder UI, `<skill-name>.zip` root `SKILL.md`, and YAML frontmatter locks on `NEA`.

## 🔒 Concept & Design Philosophy ("Why")
1. **Final Engineering Deliverable Package ("Paper Truth" at Handoff):** NEA is a portable, model-agnostic engineering assistant and self-review system that helps engineers build, validate, and review a **final deliverable package of spreadsheets**. Once the engineer completes the package and hands it off to the installation team, **it serves as the paper truth** and does not circle back for routine post-handoff field servicing (`Cable Run Status` per row is retired). If adjustments are required for pricing or scope, the package is adjusted and re-delivered.
2. **Extensible Workbook Ecosystem:** The number and types of workbooks managed by NEA will grow over time (`Equipment Schedules`, `Rack Elevations`, `Fiber Assignments`, `Test Logs`, etc.).
3. **Authority & Anti-Regression Boundary:** `Historical/` (`External_Review_v1`, `External_Review_v2`, `Internal_Review_v3`) is strictly archived and **must never be used as a source of operational requirements**. Only the `v2.2.3` controlled artifacts govern the repository.
4. **Master-Copy-Only Iteration & On-Demand Deployment Gate (`Downloads/` Lock, `.zee` Retired):** All development happens exclusively in the master repository (`/home/orin/Projects/Engineering/NEA_v2.2.3`) via `Scripts/build_copilot_agents.py`. **Never** touch `/home/orin/Downloads/` or run `Scripts/package_nea_delivery.py` during development iterations—run `Scripts/package_nea_delivery.py` **only** when the user explicitly declares a deployment state (e.g., requesting an email draft) to generate `/home/orin/Downloads/NEA_v2.2.3_Delivery.zip` (`.zee` archives are retired, and `.agents/` is excluded from the delivery `.zip`).

## 📍 Repository & Controlled File Inventory (`Version 2.2.3`, `Status: Current`)
- **Local Workspace Path:** `/home/orin/Projects/Engineering/NEA_v2.2.3` (`Copilot_Agents/` 6-Agent M365 Declarative Agent Suite + `Skills/` `3` Core Guardrail Skill packages with bundled `scripts/inspect_nea_workbooks.py` + `Templates/` `4` `.xlsx` files + `Scripts/` `3` `.py` tools + `NEA_User_and_DevOps_Manual.md` `NEA-MAN-001` + `README.md`, `CHANGELOG.md`, `NEA_Governance_Register_v2.2.3.md`)
- **Human Engineer Onboarding, Prompt Library & DevOps Reference (`NEA_User_and_DevOps_Manual.md` — `NEA-MAN-001`):** Living human-only reference document shipped in the root of `NEA_v2.2.3/` (never uploaded into Copilot `Knowledge/` or `Skills/`). Contains: (1) 7-step M365 Copilot Agent Builder build & single-module update guide, (2) daily engineer workflow + verification receipt (`NEA-VRF`/`NEA-WRT`) & severity (`AR-##`/`RR-##`/`ADV-##`/`INF-##`) guide, (3) copy-paste prompt cheat sheet across all 6 agents + local CLI commands, and (4) modular expansion checklist & DevOps contact info for **Orin Leacock | Designer** (`oleacock@netcom1989.com`, `557-250-0254`). Must be updated whenever NEA capabilities or versions evolve.
- **M365 Copilot Agent Builder Suite (`Copilot_Agents/` — `GOV-015`, `GOV-017`, `GOV-018`):** `Copilot_Agents/Agent_Builder_Guide.md` (`NEA-COPILOT-GUIDE`), `Scripts/build_copilot_agents.py` (`NEA-SCR-002`), and 6 clean Agent folders (each containing `Agent_Config.md`, `Instructions.txt`, and `Knowledge/*.txt` with zero duplicate skill or script files):
  - `NEA_Package_Reviewer/` (`NEA-AGT-001`, `5,330 / 8,000` chars `66.6%`, `5` `Knowledge/*.txt` files: `Behavior_v2.2.3.txt`, `Review_Standards_v2.2.3.txt`, `Project_Review_Workflow_v2.2.3.txt`, `Review_Report_Template_v2.2.3.txt`, `Workbook_Types_v2.2.3.txt`)
  - `NEA_BOM_Builder/` (`NEA-AGT-002`, `3,820 / 8,000` chars `47.8%`, `6` `Knowledge/*.txt` files: `Behavior_v2.2.3.txt`, `BOM_Standards_v2.2.3.txt`, `Formatting_Standards_v2.2.3.txt`, `Project_Metadata_Standard_v2.2.3.txt`, `Project_BOM_Build_Workflow_v2.2.3.txt`, `Workbook_Types_v2.2.3.txt`)
  - `NEA_CRL_Builder/` (`NEA-AGT-003`, `3,342 / 8,000` chars `41.8%`, `6` `Knowledge/*.txt` files: `Behavior_v2.2.3.txt`, `CRL_Standards_v2.2.3.txt`, `Formatting_Standards_v2.2.3.txt`, `Project_Metadata_Standard_v2.2.3.txt`, `CRL_Build_Workflow_v2.2.3.txt`, `Workbook_Types_v2.2.3.txt`)
  - `NEA_Catalog_Manager/` (`NEA-AGT-004`, `3,794 / 8,000` chars `47.4%`, `7` `Knowledge/*.txt` files: `Behavior_v2.2.3.txt`, `Material_Master_Standards_v2.2.3.txt`, `BOM_Standards_v2.2.3.txt`, `Formatting_Standards_v2.2.3.txt`, `Material_Catalog_Workflow_v2.2.3.txt`, `Workbook_Types_v2.2.3.txt`, `NEA_Governance_Register_v2.2.3.txt`)
  - `NEA_Repair_Tool/` (`NEA-AGT-005`, `3,607 / 8,000` chars `45.1%`, `6` `Knowledge/*.txt` files: `Behavior_v2.2.3.txt`, `Formatting_Standards_v2.2.3.txt`, `Project_Metadata_Standard_v2.2.3.txt`, `Workbook_Types_v2.2.3.txt`, `Workbook_Repair_Workflow_v2.2.3.txt`, `NEA_Governance_Register_v2.2.3.txt`)
  - `NEA_Timesheet_Consolidator/` (`NEA-AGT-006`, `6,206 / 8,000` chars `77.6%`, `5` `Knowledge/*.txt` files: `Behavior_v2.2.3.txt`, `Formatting_Standards_v2.2.3.txt`, `Workbook_Types_v2.2.3.txt`, `Timesheet_Standards_v2.2.3.txt` `NEA-STD-007`, `Timesheet_Consolidation_Workflow_v2.2.3.txt` `NEA-WF-006`)
- **Core Guardrail Skill Suite (`Skills/` — `NEA-SKL-001`..`003` + `3` Packaged `<skill-name>.zip` Archives with Bundled `scripts/inspect_nea_workbooks.py`):**
  - Each `Skills/<skill-name>/` directory (`nea-anti-hallucination`, `nea-workbook-entry-guard`, `nea-verification-and-receipt`) contains root-level `SKILL.md` + `scripts/inspect_nea_workbooks.py` alongside `<skill-name>.zip` (`zf.namelist() == ["SKILL.md", "scripts/inspect_nea_workbooks.py"]`) per Microsoft's Declarative Agent Skills specification, documented in `Skills/Skills_Deployment_Guide.md`.
  - `Skills/nea-anti-hallucination/SKILL.md` (`NEA-SKL-001`): Closed-world parametric lock, fail-closed gate, `[TBD: <var>]` / `[CONFLICT: <A> vs <B>]` abstention, and structural topology verification (uploaded to all 6 agents).
  - `Skills/nea-workbook-entry-guard/SKILL.md` (`NEA-SKL-002`): Safe `.xlsx` data entry, `preserve_openxml_extensions()` (prevents `openpyxl.save()` from stripping `<extLst>` `x14:dataValidations` cross-sheet dropdowns), formula locks (`D`..`I` on `Project BOM`, `B17:B38` on `CRL Summary`, `AG17:AK38` on `Timesheet`), and 3-tier catalog `--lookup` gate (uploaded to the 5 Mode-2 Builder/Catalog/Repair/Timesheet agents).
  - `Skills/nea-verification-and-receipt/SKILL.md` (`NEA-SKL-003`): Pre/Post deterministic audit, `--verify-write ORIG EDITED`, `NEA-VRF-<12hex>` Review Receipts, `NEA-WRT-<12hex>` Write Receipts, and Gate C (`Cross-Duty Agent Advisories`, uploaded to all 6 agents).
- **Deterministic Telemetry, Catalog, Repair, Timesheet Consolidation & Cross-Duty Routing Engine (`Scripts/` — `NEA-SCR-001` `v2.2.3`):** `Scripts/inspect_nea_workbooks.py` (automatically bundled into each skill package at `scripts/inspect_nea_workbooks.py`) — role-based workbook discovery (`BOM`, `CRL`, `COVER`, `TIMESHEET`), dynamic `Row 2` CRL header resolution, OpenXML `<dataValidation>` & `_FilterDatabase` audit (`[4E]`), `preserve_openxml_extensions()`, `--repair [--out-dir <dir>]` non-destructive formula/OpenXML repair, `--consolidate MANIFEST_JSON --template ... --out Week_of_MM-DD_to_MM-DD.xlsx` (`Weekly Summary` Tab 1 + alphabetical `Last, First` employee tabs), `--scope timesheet`, `--verify-write ORIG EDITED` (`NEA-WRT-<12hex>`), `SECTION 7: CROSS-DUTY AGENT ROUTING & HANDOFF ADVISORIES` (`🔄 [CROSS-DUTY -> <Agent>]`), `Pre/Post SHA-256` source immutability verification (`0 bytes modified`), 3-tier catalog audit (`tblMaterials` + `Fiber Assemblies` + `Cable Harness`), `Run ID` sequence continuity (`1..279`), duplicate `NE/FE` endpoint detection (`CRL Rows 277–280`), and `NEA-VRF-31A37EEFB1DF` receipt
- **Controlled Excel Templates (`Templates/` — `4` `.xlsx` files ONLY):** `BOM_Materials_Master_Template.xlsx` (`SHA256=f47a9f3ad7`, `6` sheets: `Cover Sheet`, `Materials Master` `tblMaterials` `505` unique keys / `0` duplicates, `Fiber Assemblies` `8`-col, `Cable Harness` `8`-col `202` variants, `Project BOM` `A7:J155` 3-tier `XLOOKUP`, `Lists`), `Cable_Running_List_Template.xlsx` (`SHA256=e6b4614fa2`, repaired contiguous `Rows 3..1087` DataValidations & `$A$2:$P$1087` AutoFilter), `Project_Cover_Sheet_Template.xlsx` (`SHA256=82caf65dc0`), `Timesheet_Template.xlsx` (`NEA-TPL-004`, `SHA256=5bf4f136c8`, single tab `Timesheet Template`, `Expense Report` stripped, `AG35` Job Slot 10 `REG` formula restored, `<sheetProtection/>` removed, styled with the **NetCom Corporate Color Palette** `cellXfs 217..239` for the `Weekly Summary` executive dashboard)

<!-- AUTO-TREE:START -->
```text
Repository: NEA_v2.2.3 | HEAD SHA: UNTRACKED | Tree Hash: 9e7492e491a3
  Copilot_Agents/
  Copilot_Agents/NEA_BOM_Builder/
  Copilot_Agents/NEA_BOM_Builder/Knowledge/
  Copilot_Agents/NEA_BOM_Builder/Knowledge/Behavior_v2.2.3.txt
  Copilot_Agents/NEA_BOM_Builder/Knowledge/BOM_Standards_v2.2.3.txt
  Copilot_Agents/NEA_BOM_Builder/Knowledge/Formatting_Standards_v2.2.3.txt
  Copilot_Agents/NEA_BOM_Builder/Knowledge/Project_BOM_Build_Workflow_v2.2.3.txt
  Copilot_Agents/NEA_BOM_Builder/Knowledge/Project_Metadata_Standard_v2.2.3.txt
  Copilot_Agents/NEA_BOM_Builder/Knowledge/Workbook_Types_v2.2.3.txt
  Copilot_Agents/NEA_BOM_Builder/Agent_Config.md
  Copilot_Agents/NEA_BOM_Builder/Instructions.txt
  Copilot_Agents/NEA_Catalog_Manager/
  Copilot_Agents/NEA_Catalog_Manager/Knowledge/
  Copilot_Agents/NEA_Catalog_Manager/Knowledge/Behavior_v2.2.3.txt
  Copilot_Agents/NEA_Catalog_Manager/Knowledge/BOM_Standards_v2.2.3.txt
  Copilot_Agents/NEA_Catalog_Manager/Knowledge/Formatting_Standards_v2.2.3.txt
  Copilot_Agents/NEA_Catalog_Manager/Knowledge/Material_Catalog_Workflow_v2.2.3.txt
  Copilot_Agents/NEA_Catalog_Manager/Knowledge/Material_Master_Standards_v2.2.3.txt
  Copilot_Agents/NEA_Catalog_Manager/Knowledge/NEA_Governance_Register_v2.2.3.txt
  Copilot_Agents/NEA_Catalog_Manager/Knowledge/Workbook_Types_v2.2.3.txt
  Copilot_Agents/NEA_Catalog_Manager/Agent_Config.md
  Copilot_Agents/NEA_Catalog_Manager/Instructions.txt
  Copilot_Agents/NEA_CRL_Builder/
  Copilot_Agents/NEA_CRL_Builder/Knowledge/
  Copilot_Agents/NEA_CRL_Builder/Knowledge/Behavior_v2.2.3.txt
  Copilot_Agents/NEA_CRL_Builder/Knowledge/CRL_Build_Workflow_v2.2.3.txt
  Copilot_Agents/NEA_CRL_Builder/Knowledge/CRL_Standards_v2.2.3.txt
  Copilot_Agents/NEA_CRL_Builder/Knowledge/Formatting_Standards_v2.2.3.txt
  Copilot_Agents/NEA_CRL_Builder/Knowledge/Project_Metadata_Standard_v2.2.3.txt
  Copilot_Agents/NEA_CRL_Builder/Knowledge/Workbook_Types_v2.2.3.txt
  Copilot_Agents/NEA_CRL_Builder/Agent_Config.md
  Copilot_Agents/NEA_CRL_Builder/Instructions.txt
  Copilot_Agents/NEA_Package_Reviewer/
  Copilot_Agents/NEA_Package_Reviewer/Knowledge/
  Copilot_Agents/NEA_Package_Reviewer/Knowledge/Behavior_v2.2.3.txt
  Copilot_Agents/NEA_Package_Reviewer/Knowledge/Project_Review_Workflow_v2.2.3.txt
  Copilot_Agents/NEA_Package_Reviewer/Knowledge/Review_Report_Template_v2.2.3.txt
  Copilot_Agents/NEA_Package_Reviewer/Knowledge/Review_Standards_v2.2.3.txt
  Copilot_Agents/NEA_Package_Reviewer/Knowledge/Workbook_Types_v2.2.3.txt
  Copilot_Agents/NEA_Package_Reviewer/Agent_Config.md
  Copilot_Agents/NEA_Package_Reviewer/Instructions.txt
  Copilot_Agents/NEA_Repair_Tool/
  Copilot_Agents/NEA_Repair_Tool/Knowledge/
  Copilot_Agents/NEA_Repair_Tool/Knowledge/Behavior_v2.2.3.txt
  Copilot_Agents/NEA_Repair_Tool/Knowledge/Formatting_Standards_v2.2.3.txt
  Copilot_Agents/NEA_Repair_Tool/Knowledge/NEA_Governance_Register_v2.2.3.txt
  Copilot_Agents/NEA_Repair_Tool/Knowledge/Project_Metadata_Standard_v2.2.3.txt
  Copilot_Agents/NEA_Repair_Tool/Knowledge/Workbook_Repair_Workflow_v2.2.3.txt
  Copilot_Agents/NEA_Repair_Tool/Knowledge/Workbook_Types_v2.2.3.txt
  Copilot_Agents/NEA_Repair_Tool/Agent_Config.md
  Copilot_Agents/NEA_Repair_Tool/Instructions.txt
  Copilot_Agents/NEA_Timesheet_Consolidator/
  Copilot_Agents/NEA_Timesheet_Consolidator/Knowledge/
  Copilot_Agents/NEA_Timesheet_Consolidator/Knowledge/Behavior_v2.2.3.txt
  Copilot_Agents/NEA_Timesheet_Consolidator/Knowledge/Formatting_Standards_v2.2.3.txt
  Copilot_Agents/NEA_Timesheet_Consolidator/Knowledge/Timesheet_Consolidation_Workflow_v2.2.3.txt
  Copilot_Agents/NEA_Timesheet_Consolidator/Knowledge/Timesheet_Standards_v2.2.3.txt
  Copilot_Agents/NEA_Timesheet_Consolidator/Knowledge/Workbook_Types_v2.2.3.txt
  Copilot_Agents/NEA_Timesheet_Consolidator/Agent_Config.md
  Copilot_Agents/NEA_Timesheet_Consolidator/Instructions.txt
  Copilot_Agents/Agent_Builder_Guide.md
  Scripts/
  Scripts/build_copilot_agents.py
  Scripts/inspect_nea_workbooks.py
  Scripts/package_nea_delivery.py
  Skills/
  Skills/nea-anti-hallucination/
  Skills/nea-anti-hallucination/scripts/
  Skills/nea-anti-hallucination/scripts/inspect_nea_workbooks.py
  Skills/nea-anti-hallucination/nea-anti-hallucination.zip
  Skills/nea-anti-hallucination/SKILL.md
  Skills/nea-verification-and-receipt/
  Skills/nea-verification-and-receipt/scripts/
  Skills/nea-verification-and-receipt/scripts/inspect_nea_workbooks.py
  Skills/nea-verification-and-receipt/nea-verification-and-receipt.zip
  Skills/nea-verification-and-receipt/SKILL.md
  Skills/nea-workbook-entry-guard/
  Skills/nea-workbook-entry-guard/scripts/
  Skills/nea-workbook-entry-guard/scripts/inspect_nea_workbooks.py
  Skills/nea-workbook-entry-guard/nea-workbook-entry-guard.zip
  Skills/nea-workbook-entry-guard/SKILL.md
  Skills/Skills_Deployment_Guide.md
  Templates/
  Templates/BOM_Materials_Master_Template.xlsx
  Templates/Cable_Running_List_Template.xlsx
  Templates/Project_Cover_Sheet_Template.xlsx
  Templates/Timesheet_Template.xlsx
  CHANGELOG.md
  NEA_Governance_Register_v2.2.3.md
  NEA_User_and_DevOps_Manual.md
  README.md
```
<!-- AUTO-TREE:END -->

## 🧠 Architectural Decisions, Benchmarks & 6-Pillar Anti-Hallucination Gate
Full benchmark telemetry (`Runs #1`–`#7`) is archived in `2026-10-28_NEA_v1.3_Consolidation_and_Anti_Hallucination`:
- **Sandbox Efficiency Gains (`Run #4` Baseline $\rightarrow$ `Run #5` Consolidated $\rightarrow$ `Run #7` Full `v1.3`)**:
  - **Planner Turns**: `41` turns $\rightarrow$ `28` turns $\rightarrow$ **`12` turns (`-70.7%` / `3.4x` faster)**
  - **`.md` Files Read**: `23` files $\rightarrow$ `15` files $\rightarrow$ **`5` Tier 1 files (`0` Tier 2 files opened)**
  - **Report-Generation Context**: `~151,940` tokens $\rightarrow$ `~84,783` tokens $\rightarrow$ **`63,610` tokens (`-58.1%`)**
  - **Cumulative Cached Read Tokens**: `2,929,063` $\rightarrow$ `1,388,372` $\rightarrow$ **`360,676` tokens (`-87.7%` / `8.1x` reduction)** with **100% defect fidelity** and **0 hallucinations**.
- **6-Pillar Anti-Hallucination Architecture (`Behavior_v2.2.3.txt` Sec 3 & `Review_Report_Template_v2.2.3.txt`)**:
  1. **Hard Fail-Closed Gate (`[EXTRACTION BLOCKED — REVIEW ABORTED]`)**: Halts immediately on the next turn if `inspect_nea_workbooks.py` or `.xlsx` reading fails/times out; strictly forbids scraping `.md`/`.py` files or fabricating a report.
  2. **100% Testbed Spoiler Decontamination**: Zero `307-2` (`20263916`) part numbers, quantities, or row ranges exist in `.md`, `.py`, or `Visuals/` (`0` grep matches).
  3. **Cryptographic Proof-of-Inspection Receipt**: Mandatory live `NEA-VRF-...` token (`NEA-VRF-31A37EEFB1DF`) and per-workbook 10-char `SHA256` hashes in every report header.
  4. **Closed-World Evidence Binding**: Every reported coordinate, value, and name must exist verbatim in live telemetry (`[UNVERIFIED — NOT IN TELEMETRY]` if absent).
  5. **Catalog `--lookup` Verification Gate**: Requires `inspect_nea_workbooks.py Templates --lookup "<term>"` before entering any `MB P/N` or `TPN##` on `Project BOM` Column `B` (`[CATALOG ADDITION REQUIRED]` if absent).
  6. **OpenXML `<f>` + `<v>` & Label-Driven Coordinates**: Inspects both `<f>` (including `<f t="shared" si="..."/>`) and `<v>`, and resolves `Cover Sheet` fields by label in `Column B`/`F`/`G`.
- **NetCom M365 Copilot Chat & Declarative Agent Builder Architecture (`GOV-015`–`GOV-018`)**:
  - **Environment Reality**: NetCom currently restricts usage to **Microsoft 365 Copilot (Chat) + Agent Builder (Declarative Agents)** with no direct local filesystem access. Detailed M365 Graph latency, `8,000`-char cap, `<skill-name>.zip` bundling, ECMA-376 OpenXML Desktop Excel compliance, and `<extLst>` post-mortems live in [`NetCom_Engineering_Assistant_Lessons_Learned`](NetCom_Engineering_Assistant_Lessons_Learned.md), and the repeatable 9-surface module blueprint lives in [`NetCom_Engineering_Assistant_Module_Launchpad`](NetCom_Engineering_Assistant_Module_Launchpad.md).
  - **1. Zero-Latency Chat Attachment (`/mnt/data/`)**: Engineers upload live `.xlsx`, `.pdf`, and image deliverables **directly into the Copilot chat turn** (`+ Upload from device`) rather than relying on asynchronous OneDrive/SharePoint Graph indexing.
  - **2. 6-Agent Modular Suite (`<= 8,000` Chars, Semver `"2.2.3"`)**: `Scripts/build_copilot_agents.py` (`NEA-SCR-002`) compiles `Copilot_Agents/<Agent_Slug>/` (`NEA_Package_Reviewer` `5,330` chars `66.6%`, `NEA_BOM_Builder` `3,820` chars `47.8%`, `NEA_CRL_Builder` `3,342` chars `41.8%`, `NEA_Catalog_Manager` `3,794` chars `47.4%`, `NEA_Repair_Tool` `3,607` chars `45.1%`, `NEA_Timesheet_Consolidator` `6,206` chars `77.6%`) with `.txt` Knowledge packs (`Copilot_Agents/<Agent_Slug>/Knowledge/*.txt`) and directional `🔄 [CROSS-DUTY -> <Agent>]` advisories.
  - **3. Root-Level `<skill-name>.zip` Archives with Bundled `scripts/inspect_nea_workbooks.py`**: Each of the `3` core guardrail skill directories under `Skills/<skill-name>/` (`NEA-SKL-001`..`003`) packages root-level `SKILL.md` + `scripts/inspect_nea_workbooks.py` inside `<skill-name>.zip` (`zf.namelist() == ["SKILL.md", "scripts/inspect_nea_workbooks.py"]`) so Code Interpreter runs deterministic single-turn OpenXML inspection, `--lookup`, `--repair`, `--consolidate`, and `--verify-write` (`NEA-WRT-<12hex>` + `validate_openxml_package_integrity()`) with `0` custom Python parser generation.

## 🔍 Provenance Status & Open [TBD] / [CONFLICT] Ledger
> [!NOTE]
> Figures inside this ledger are quarantined by `verify_claims.py` and are **not** treated as authorized source truth until resolved.

- **Provenance Baseline:** Phase A `v1.3` $\rightarrow$ `v2.0.0` $\rightarrow$ `v2.2.3` Markdown, `Scripts/inspect_nea_workbooks.py` (`v2.2.3`), and 6-Agent `Copilot_Agents/` + `3` bundled-script `<skill-name>.zip` packages (`NEA-SCR-002` `v2.2.3`) verified across `7` cold-start blind sandboxes + two `5-Agent Parallel Cold-Start Blind Swarms` (`d871f794`..`93fb6f80` and Option 2 bundled-script swarm `0bf07258`, `f2291fdf`, `df1a3651`, `ebe27285`, `1f8cc443`, `0` hallucinations, `0` custom OpenXML parser code needed) + `NEA Timesheet Consolidator` Cold-Start `Blind-Light` (`24831c6b`) and `OS Dry-Run (+faults)` (`SBX-20261103_131300-7cb27db8` & `SBX-20261104_125900-8d70fad1`: `1/1` injected faults caught, `0` live host mutations, 100% ECMA-376 `xmllint` compliance); `Templates/*.xlsx` retained with `307-2` regression defects staged for **Phase B** remediation (auto-repaired on demand via `inspect_nea_workbooks.py --repair`).
- **Open Documentation `[TBD]` Items:** `None` (`open_tbd_count: 0` on controlled `v2.2.3` Markdown/Python baseline).

## 🎯 Active Tasks
*(Transcluded live from `## NetCom_Engineering_Assistant` in [`NetCom_Tasks`](../../Tasks/NetCom_Tasks.md))*

> **Active Task Queue**: Tracked in [`NetCom_Tasks`](../../Tasks/NetCom_Tasks.md#NetCom_Engineering_Assistant) *(Single-Writer Task Umbrella)*.

## 🚀 Session Handoff & Multi-Session Kickstart (`SESSION-HANDOFF`)
<!-- SESSION-HANDOFF:START -->
- **Last Session Timestamp**: `2026-11-05`
- **Checkpoint Provenance**: `HEAD SHA: UNTRACKED` | `Tree Hash: 3ce4939d8bf7` | `Worktree: ('untracked', [])` | `Last Verification: Transplanted from verified Memory v2 baseline`
- **Where We Stopped (Verified State & Context)**:
  - Transplanted `NetCom_Engineering_Assistant` dossier into native Homunculus Dual-Mode Memory (`entity: NetCom`, `compartment: private`, `project_type: software`). All verified specifications, hazards, and open `[TBD]` ledgers preserved verbatim.
- **Active Project State Ledger & Blockers**:
  - See `## 🔍 Provenance Status & Open [TBD] / [CONFLICT] Ledger` above and active tasks in [`NetCom_Tasks.md`](../../Tasks/NetCom_Tasks.md).
- **Next Session Kickstart & Discussion Points**:
  1. Run `python3 skills/project-memory/scripts/sync_memory.py --project NetCom_Engineering_Assistant --kickstart` to verify repository provenance.
  2. Review open tasks in [`NetCom_Tasks.md`](../../Tasks/NetCom_Tasks.md#NetCom_Engineering_Assistant).
<!-- SESSION-HANDOFF:END -->
