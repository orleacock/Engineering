# NetCom Engineering Assistant (NEA) Change Log

Version: 2.2.3
Status: Current
Document ID: NEA-CHANGE
Logical Name: CHANGELOG
Owner: NetCom Technical Services

## Purpose

This document is the centralized, chronological record of architectural changes, version promotions, standard/workflow consolidations, and governance closures across the NetCom Engineering Assistant (NEA) repository.

Individual Markdown artifacts do not duplicate multi-version change logs; all historical and current revision tracking resides here.

---

## Version 2.2.3 — Option C Dynamic Anchor Scanner, `2D Digital Grid Snapshot` & Multi-Page Continuation Tabs (`2026-11-05`)

### 1. Option C Dynamic Anchor Scanner & `2D Digital Grid Snapshot` for Derived `.xlsx` Variants (`NEA-SCR-001` `v2.2.3`)
- **Dynamic Header & Day-Column Anchor Resolution (`_scan_timesheet_layout()`)**:
  - Upgraded `Scripts/inspect_nea_workbooks.py --scope timesheet` to dynamically scan `Rows 1–10` and `Cols A..AM` for shifted header labels (`EMPLOYEE`, `Position`, `Union Local#`, `Begin Week`, `WEEK ENDING`), `SUN..SAT` day columns (`4`-column blocks `REG`, `OT`, `DT`, `2ND`/`3RD`), and Union Local #1 `Foreman`/`GF`/`Forman` and `Travel` summary columns (`AL`/`AM`), plus `xl/styles.xml` RGB fill inspection (`#FFFFFF00` / `#FFFFF2CC` / `#FFFFE699`) to detect yellow-highlighted `3RD` shift cells automatically.
- **Automatic `2D Digital Grid Snapshot` + Adaptive Manifest Emission on Layout Drift**:
  - Whenever a derived `.xlsx` timesheet differs from the strict canonical cell coordinates (`⚠️ [TS-LAYOUT-DRIFT DETECTED]`), `inspect_nea_workbooks.py --scope timesheet` automatically emits a clean **`📸 [2D DIGITAL GRID SNAPSHOT]`** table (complete with `[YELLOW-FILL]` style badges and `<f>=...` formula tags) alongside a ready-to-consolidate **`✅ [ADAPTIVE EXTRACTED MANIFEST RECORD]`** JSON block, combining 100% digital IEEE-754 float/style fidelity with layout-agnostic visual comprehension.
- **Multi-Page Employee Merging & Automatic `>10`-Job Continuation Tabs (`Last, First (2)`)**:
  - Updated `consolidate_timesheets()` to merge multiple source sheets/pages for the same employee in chronological order and automatically split employees with `>10` distinct jobs across `Last, First`, `Last, First (2)`, etc. (`10` job slots per Missouri Timesheet tab) while rolling all jobs into `Tab 1: Weekly Summary` and `Tab 2: Job Summary`.

---

## Version 2.2.2 — 6th Specialist Agent (`NEA Timesheet Consolidator` `NEA-AGT-006`), Management `Job Summary` (`Tab 2`) & Self-Contained Template Fallback (`2026-11-05`)

### 1. Multi-Media `NEA Timesheet Consolidator` (`NEA-AGT-006`), `nea-timesheet-consolidator.zip` (`NEA-SKL-009`) & `Timesheet_Template.xlsx` (`NEA-TPL-004`) (`GOV-018`)
- **Added 6th Specialist Agent (`NEA Timesheet Consolidator`, `6,184 / 8,000` chars, `5` Knowledge `.txt` files)**:
  - Ingests digital `.xlsx` Missouri Timesheets, scanned multi-page `.pdf` packets (e.g., weekly field packets with interleaved expense sheets, hardware store receipts, and vendor invoices), and `.png`/`.jpg` photos.
  - Automatically filters and ignores `Expense Report` tabs (`sheet2.xml`), scanned `MISCELLANEOUS EXPENSES` / `Mileage` forms, store receipts (`Home Depot`, `True Value`), and vendor invoices (`Microsoft Invoice`).
  - Consolidates all employees for the week into `Week_of_MM-DD_to_MM-DD.xlsx` featuring:
    - **`Tab 1: Weekly Summary`** (`sheet1.xml`, NetCom Primary Navy `#114573` tab color, tracking `REG`, `OT`, `DT`, `2ND`, `3RD`, `Foreman/GF`, `Travel`, and `=SUM(G{r}:I{r})` `Total Paid Hours` by employee and job).
    - **`Tab 2: Job Summary`** (`sheet2.xml`, NetCom Deep Teal `#165366` tab color, rolling up hours and shift/overtime types by `Job Number` across `Cols A:N` with `Tech Count`, `Assigned Crew`, `% of Week`, `REG`, `OT`, `DT`, `2ND`, `3RD`, `Foreman/GF`, `Travel`, and `Total Job Hours` so management can track labor consumed against job bidding).
    - **Alphabetically Sorted `Last, First` Employee Tabs** (`Tabs 3..N+2`, `sheet3.xml`..`sheet{N+2}.xml`, with `1-to-1` `drawing{idx}.xml` relationships).
  - Enforces an OCR/Vision Confidence Verification Gate (`[TBD: ...]`) for ambiguous handwritten digits while auto-consolidating in one turn when 100% legible and cross-checked against row/column totals.
- **Self-Contained Embedded `Timesheet_Template.xlsx` Fallback (`_EMBEDDED_TIMESHEET_TEMPLATE_B85`)**:
  - Embedded a compressed copy of `Templates/Timesheet_Template.xlsx` (`SHA256=5bf4f136c8`, styled with the NetCom Corporate Color Palette `cellXfs 217..239`) directly inside `Scripts/inspect_nea_workbooks.py` so M365 Copilot Code Interpreter succeeds on PDF-only and photo-only runs even when `Templates/Timesheet_Template.xlsx` is not attached in chat.

---

## Version 2.1.2 — 5-Agent Suite (`NEA Repair Tool` `NEA-AGT-005`) & Directional Cross-Duty Informer (`2026-11-03`)

### 1. Dedicated `NEA Repair Tool` (`NEA-AGT-005`, `NEA_Repair_Tool_v2.1.2.zip`) & 5-Agent Headroom Optimization (`GOV-017`)
- **Separated Project Deliverable Review from Workbook Mechanics Repair**:
  - Split workbook/template structural repair (`Mode 2` `--repair` formula restoration, `Cover Sheet!B30:C30` revision link repair, `tblMaterials` `A3:G508` / `Lists!H1` `<>0` zero-spill fix, and `[4E]` OpenXML DataValidation/AutoFilter healing) into a dedicated 5th specialist agent (**`NEA Repair Tool`**, `NEA-AGT-005`, `Workbook_Repair_Workflow_v2.1.2.txt` `NEA-WF-005`).
  - Executed a **5-Agent Parallel Cold-Start Blind Sandbox Swarm** across all 5 agents (`NEA Package Reviewer`, `NEA BOM Builder`, `NEA CRL Builder`, `NEA Catalog Manager`, `NEA Repair Tool`) to eliminate cross-role redundancy and maximize `< 8,000`-character instruction headroom:
    - **`NEA Package Reviewer` (`Copilot_Agents/NEA_Package_Reviewer/`)**: `5,330 / 8,000` chars (`66.6%` — `+2,670` chars headroom; `5` `Knowledge/*.txt` files)
    - **`NEA BOM Builder` (`Copilot_Agents/NEA_BOM_Builder/`)**: `3,820 / 8,000` chars (`47.8%` — `+4,180` chars headroom; `6` `Knowledge/*.txt` files)
    - **`NEA CRL Builder` (`Copilot_Agents/NEA_CRL_Builder/`)**: `3,342 / 8,000` chars (`41.8%` — `+4,658` chars headroom; `6` `Knowledge/*.txt` files)
    - **`NEA Catalog Manager` (`Copilot_Agents/NEA_Catalog_Manager/`)**: `3,794 / 8,000` chars (`47.4%` — `+4,206` chars headroom; `7` `Knowledge/*.txt` files)
    - **`NEA Repair Tool` (`Copilot_Agents/NEA_Repair_Tool/`)**: `3,607 / 8,000` chars (`45.1%` — `+4,393` chars headroom; `6` `Knowledge/*.txt` files)
- **Bundled `scripts/inspect_nea_workbooks.py` Inside `<skill-name>.zip` & Zero Duplicate Files (`GOV-016`, `GOV-017`)**:
  - Packaged `scripts/inspect_nea_workbooks.py` directly inside each `Skills/<skill-name>/<skill-name>.zip` archive alongside root-level `SKILL.md` (`zf.namelist() == ["SKILL.md", "scripts/inspect_nea_workbooks.py"]`) per Microsoft's official Declarative Agent Skills specification, and removed `22` duplicate `.txt` files (`inspect_nea_workbooks.txt` and `NEA_*_Skill.txt`) from `Copilot_Agents/*/Knowledge/` and top-level `Skills/`.

### 2. Role-Scoped Directional Cross-Duty Informer (`inspect_nea_workbooks.py` Section 7, `--scope {review,bom,crl,catalog,repair}` & `--repair` Mode)
- **Directional Cross-Duty Handoffs (`SECTION 7`)**:
  - Expanded `--scope` in `Scripts/inspect_nea_workbooks.py` (`NEA-SCR-001` `v2.1.2`) to support `--scope {full,review,delta,bom,crl,catalog,repair}`, ensuring each agent receives only role-relevant telemetry and directional `🔄 [CROSS-DUTY -> <Agent Name>]` handoffs (`NEA Repair Tool` running `--scope repair` emits zero project deliverable advisories).
- **Bulk-Box / UOM Quantity Multiplier Audit (`[3B]`) & `BOM_Materials_Master_Template.xlsx` Repair**:
  - Added deterministic `[3B. Bulk-Box / UOM Quantity Multiplier Anomalies]` (`UOM == "BX"` with `Qty >= 100`, catching `Row 70` `MB P/N 50063` `1,000 BX = 1,000,000` cable ties) and expanded `--repair` to rescale `tblMaterials` `ref="A3:G600"` $\rightarrow$ `ref="A3:G508"`, harden `Lists!H1` `FILTER(VSTACK(...), (<>"")*(<>0))` (`92` zero-spill entries eliminated), and expand `Fiber Assemblies!H` Status DataValidation `sqref="H4:H286"` $\rightarrow$ `sqref="H4:H1258"`.

---

## Version 2.0.0 — Microsoft 365 Copilot Declarative Agent Suite, Lean `.txt` Architecture & 3-Skill Guardrail Suite (`2026-11-02`)

### 1. 4-Agent Modular Specialist Suite for M365 Copilot & Agent Builder (`GOV-015`, `NEA-SCR-002`)
- **Engineered Around NetCom M365 Copilot Chat & OneDrive Constraints**:
  - Addressed the two primary enterprise deployment bottlenecks in Microsoft 365 Copilot Chat: (1) **OneDrive / SharePoint Graph search indexing lag** on recently saved `.xlsx` deliverables, and (2) the **`8,000`-character system instruction ceiling** in Declarative Agents (`declarativeAgent.json`).
  - Built `Scripts/build_copilot_agents.py` (`NEA-SCR-002`) to deterministically compile NEA into **4 role-specific Declarative Agents** under `Copilot_Agents/`:
    1. **`NEA Package Reviewer` (`NEA-AGT-001`, `NEA_Package_Reviewer_v2.0.0.zip`, `7,953 / 8,000` chars)**: Mode 1 Read-Only Engineering Self-Review & Cross-Document Validation Agent (`Project_Review_Workflow`, `Review_Standards`, `Review_Report_Template`) with an embedded self-contained Python OpenXML verification kernel.
    2. **`NEA BOM Builder` (`NEA-AGT-002`, `NEA_BOM_Builder_v2.0.0.zip`, `6,331 / 8,000` chars)**: Mode 2 Guided `Project BOM` creation, 3-tier catalog lookup, `CRL -> BOM` takeoff rollup, and safe editing of `Columns B, C, I` while enforcing `Column A`, `Columns E:H`, and `Column J` formula locks.
    3. **`NEA CRL Builder` (`NEA-AGT-003`, `NEA_CRL_Builder_v2.0.0.zip`, `5,432 / 8,000` chars)**: Mode 2 Guided 16-column `Cable Running List` build, `Run ID` continuity check, duplicate `NE/FE` port detection (`CRL-DATA-003`), and takeoff generation.
    4. **`NEA Catalog Manager` (`NEA-AGT-004`, `NEA_Catalog_Manager_v2.0.0.zip`, `5,462 / 8,000` chars)**: Mode 2 3-tier catalog hygiene, deduplication, and `TPN##` / `MB P/N` onboarding across `tblMaterials`, `Fiber Assemblies`, and `Cable Harness`.
  - **Option 2 Direct `.txt` Authoring & Lean Repository Trim**:
    - Removed legacy `v1.2`/`v1.3` folders (`Behavior/`, `Standards/`, `Workflows/`, `References/`, `Historical/`, `Visuals/`) and duplicate `Templates/inspect_nea_workbooks.py` / `Scripts/inspect_nea_workbooks.txt` mirrors, standardizing on direct `.txt` authoring inside `Copilot_Agents/<Agent>_v2.0.0/Knowledge/*.txt`.
  - **Direct Chat Drop-In Operational Protocol**: Documented in `Copilot_Agents/README_Copilot_Deployment_v2.0.0.md` (`NEA-COPILOT-GUIDE`), instructing designers to drop live `.xlsx` files directly into the chat prompt (`+ Upload from device`) so Code Interpreter inspects the live file bytes immediately with `0` OneDrive indexing latency.

### 2. Repaired `Cable_Running_List_Template.xlsx` (`SHA256=e6b4614fa2`) & OpenXML `[4E]` Integrity Audit
- **Updated 3-Tab CRL Layout (`Cover Sheet`, `Cable Running List`, `CRL Summary`, `Reference Lists` hidden)**:
  - Normalized `Cable Running List` to `Row 1` decorative banner, `Row 2` column headers (`A2:P2`), and `Row 3+` cable run records (`Rows 3..1087`), with `CRL Summary` (`B17:B38`) wired to live `COUNTIF`/`SUMIF` formulas (`1,038` total formulas).
  - Surgically repaired OpenXML `<dataValidations>`, `<x14:dataValidations>`, and `_FilterDatabase` in `Cable_Running_List_Template.xlsx` (`SHA256=e6b4614fa2`) so all 7 validation rules (`M3:M1087` `1..288`, `N3:N1087` `> 0`, `O3:O1087` `SpecialRequirementList`, `B3:B1087` `'Reference Lists'!$A$1:$A$3`, `K3:K1087` `'Reference Lists'!$B$1:$B$2`, `L3:L1087` `'Reference Lists'!$C$1:$C$12`, `F3:F1087 J3:J1087` `'Reference Lists'!$D$1:$D$11`) and AutoFilter (`$A$2:$P$1087`) span `Rows 3..1087` contiguously (`0` `[4E]` anomalies).

### 3. 3-File Companion Guardrail Skill Suite (`Skills/`) & `--verify-write` Gate (`GOV-016`)
- **Modular Guardrail Skill Suite (`Skills/*.txt`, `0` `.bat`/`.ps1` scripts)**:
  1. **`Skills/NEA_Anti_Hallucination_Skill.txt` (`NEA-SKL-001`)**: Enforces Closed-World Parametric Lock, explicit `[TBD: <var>]` / `[CONFLICT: <A> vs <B>]` abstention tags, `[EXTRACTION BLOCKED — ABORTED]` fail-closed gate, and structural topology verification.
  2. **`Skills/NEA_Workbook_Entry_Guard_Skill.txt` (`NEA-SKL-002`)**: Enforces `preserve_openxml_extensions()` (preventing `openpyxl.save()` from stripping `<extLst>` `x14:dataValidations` cross-sheet dropdowns), `Project BOM` (`D`..`I`) and `CRL Summary` (`B17:B38`) formula locks, and the 3-tier `--lookup` catalog gate.
  3. **`Skills/NEA_Verification_and_Receipt_Skill.txt` (`NEA-SKL-003`)**: Enforces deterministic pre/post audit, cryptographic `NEA-VRF-<12hex>` Review Receipts / `NEA-WRT-<12hex>` Write Receipts (`--verify-write ORIG EDITED`), and Gate C (`Cross-Duty Agent Advisories`).

---

## Version 1.3 — Operational Validation, Reporting Standard & Architecture Consolidation (`2026-10-28` / `2026-11-01` Live Field-Test Update)

### 0. Live Work-Environment Field-Test Hardening & Three-Tier `Cable Harness` Catalog (`2026-11-01`)
- **Three-Tier Catalog Architecture (`tblMaterials` $\rightarrow$ `Fiber Assemblies` $\rightarrow$ `Cable Harness`)**:
  - Updated `BOM_Materials_Master_Template.xlsx` with a cleaned, deduplicated `tblMaterials` (`$A$3:$G$600`, `505` unique `MB P/N` records, `0` duplicate keys), added `Column H` (`Status`) to `Fiber Assemblies` (`$A$3:$H$1258`), and added the new **`Cable Harness`** extension worksheet (`$A$3:$H$1258`, `202` harness variants across `11` section headers + Suffix Key in `M5:P12`).
  - Wired `Lists!H1` (`BOMPartNumbers` dynamic spill) to `FILTER(VSTACK(tblMaterials[MB P/N],'Fiber Assemblies'!$C$4:$C$1258,'Cable Harness'!$C$4:$C$1258), ... <> "")` so unassigned `Cable Harness` variants (`Col C` blank, `Status = Pending`) never trigger `#CALC!` errors while automatically entering the dropdown as soon as an `MB P/N` is assigned.
  - Upgraded `Project BOM` (`A7:J155`) `Columns D:I` across `Rows 8–155` to a 3-tier cascading `XLOOKUP` (`tblMaterials` $\rightarrow$ `Fiber Assemblies` $\rightarrow$ `Cable Harness`) and removed the un-formulad `Row 156` stub (`0` static formula overwrites across `A8:I155`).
- **Travel-Proof & Role-Based Inspector (`NEA-SCR-001` `v1.3.1` — Fixes `NEA-RUNTIME-001`/`002`, `CRL-QA-001`, `CRL-DATA-003`/`004`, `BOM-CAT-003`)**:
  - Replaced hardcoded `*_Template.xlsx` filename lookups in `Scripts/inspect_nea_workbooks.py` with **internal worksheet-role detection**, enabling automatic discovery of renamed project deliverables (e.g., `BOM_Materials_Master.xlsx`, `Cable_Running_List_Template_V2.xlsx`).
  - Added travel-proof mirrors in `Templates/inspect_nea_workbooks.py` (travels inside the workbook folder) and `Scripts/inspect_nea_workbooks.txt` (passes through corporate email/SharePoint security gateways that strip `.py` files and executes directly via `python3 Scripts/inspect_nea_workbooks.txt`).
  - Added cryptographic `Pre/Post SHA-256` source immutability verification (`0 bytes modified`), explicit `Run ID` sequence continuity verification (`1..279`), duplicate `(Manufacturer, MFG Part Number)` detection, and duplicate `NE/FE` endpoint & port assignment detection (`CRL Rows 277–280 / Runs 189–192`).

### 1. Architecture Streamlining & Token Optimization (`GOV-011` – `GOV-014`)
- **Retired Middleman `Capabilities/` Layer (`8` files) & Redundant Overview Docs**:
  - Consolidated all governing engineering rules from `Capabilities/*` (`Project_Initialization`, `Material_Management`, `Material_Master_Maintenance`, `Project_BOM_Management`, `CRL_Management`, `Cross_Document_Validation`, `Project_Review`) into the 6 governing `Standards/` (`NEA-STD-001` through `NEA-STD-006`).
  - Consolidated all step-by-step procedural sequences into 4 operational `Workflows/` (`Material_Catalog_Workflow`, `Project_BOM_Build_Workflow`, `CRL_Build_Workflow`, and the newly established `Project_Review_Workflow`).
  - Folded `NetCom_Engineering_Assistant_v1.3.md`, `Capabilities/Capabilities_v1.3.md`, and `References/Repository_Structure_v1.3.md` into `README.md` (`NEA-README`) and `Repository_Index.md` (`NEA-INDEX`), with a complete Legacy Logical Name Alias Map in `Repository_Index.md` Section 2.
  - Compressed `Behavior/Behavior_v1.3.md` (`NEA-BEH-001`), `References/Workbook_Types_v1.3b.md` (`NEA-REF-002`), and `NEA_Governance_Register_v1.3b.md` (`NEA-GOV`) into high-density tables, eliminating repeated boilerplate and reducing active repository Markdown lines by **>80%** (`20,299` lines $\rightarrow$ `~2,800` lines).

### 2. Formal Engineering Review Report Specification (`NEA-REF-003`) & Blind Sandbox Verification
- **Created `References/Review_Report_Template_v1.3b.md` (`NEA-REF-003`, `Review_Report_Template`)**:
  - Standardized the 6-section uniform Markdown report output: (1) Executive Gate Summary & Severity Scorecard, (2) Project Identity & Cover Sheet Alignment, (3) Cross-Document Material & Cable Takeoff (`CRL` ↔ `Project BOM`), (4) Active Project Deliverable Findings (`AR-##`, `RR-##`, `ADV-##`, `INF-##`), (5) Catalog & Template Maintenance Referrals (`CAT-##`, `TPL-##`), and (6) Workbook-Ordered Engineer Closeout Punch List (`- [ ]`).
  - Enforced visual uniformity: compact value/metric-only tables (`<= 5` columns, zero prose sentences in cells) in Sections 1–3 and a single uniform structured bullet block layout across all findings and referrals in Sections 4 and 5.
  - Added the **Mandatory Fast-Path Review Execution Sequence & 6-Pillar Anti-Hallucination Architecture** (Fail-Closed `[EXTRACTION BLOCKED — REVIEW ABORTED]` gate, dynamic `NEA-VRF` + `SHA-256` proof-of-inspection token, closed-world evidence binding, `--lookup` catalog verification, and OpenXML `<f>`/`<v>` shared-formula inspection), empirically verified across six blind zero-context sandbox agent runs.
  - Added `Scripts/inspect_nea_workbooks.py` (`NEA-SCR-001`) providing single-command deterministic OpenXML telemetry, Tier 1 vs. Tier 2 on-demand standard routing, and SHA-256 delta caching.

### 3. Pre-Release `Internal_Review_v3` Baseline Closure (`IR3-01` – `IR3-22`)
- Promoted all active NEA Markdown artifacts to **`Version: 1.3`** and synchronized all 6 Standards from `Status: Draft` to **`Status: Current`** (`IR3-01`).
- Locked the **Deliverable Package Philosophy ("Paper Truth" at Handoff)**: once handed off to installation, the spreadsheet package is the installation team's paper truth and does not track per-row `Cable Run Status` (`GOV-005`). If scope or pricing changes occur, the package is adjusted and re-delivered.
- Added explicit `Relative Path` columns to `Repository_Index.md` and locked `Historical/` (`External_Review_v1`, `External_Review_v2`, `Internal_Review_v3`) as non-operational archives.
- Synchronized `Visuals/` high-resolution `.png` and `.svg` architecture and workbook data-flow diagrams (`generate_nea_flowchart.py`) with the official NetCom corporate palette (`#114573`, `#03A6D9`, `#165366`, `#231F20`, `#5DA423`, `#FFAE00`, `#C60F13`).

---

## Version 1.2 — Repository Boundary Cleanup & Visual Architecture (`2026-10-28`)

- Added `README.md` as the primary onboarding entry point and organized non-authoritative resources under `References/`, `Visuals/`, and `Historical/`.
- Relocated historical review artifacts (`External_Review_v1`, `External_Review_v2`) into `Historical/` and documented search-result disambiguation rules in `Repository_Index.md`.
- Established `Visuals/` (`NEA_System_Architecture_Flowchart` and `NEA_Workbook_DataFlow_Diagram`) with model-agnostic maintenance instructions.

---

## Version 1.1 — Master Version Registry, Three-Domain Status Model & Catalog Governance (`2026-10-27`)

- **Master Version Registry (`GOV-010`)**: Converted `Repository_Index.md` into the single source of truth for artifact versions and logical-name dependency resolution (`NEA-*` IDs).
- **Three-Domain Status Model (`GOV-005`)**: Replaced the legacy 4-domain status model with three active operational domains (`Document Status`, `Material Status`, `Review Status`), retiring per-row `Cable Run Status` from the approved 16-column CRL schema.
- **Project BOM Formula Protection & Unit-Aware Summaries (`GOV-002`, `GOV-007`)**: Documented the 10-column `Project BOM` control model (`Columns B, C, J` editable; `Column A` and `Columns D:I` formula-locked) and required unit-aware material summaries rather than undifferentiated mixed-UOM sums.
- **Materials Master Catalog Governance (`GOV-002`, `GOV-003`)**: Defined primary-key uniqueness (`MB P/N` and `TPN##`), first-match `XLOOKUP` shadowing rules, the 16 workbook-aligned Material Categories (`Lists`), the 6 Material Statuses (`Pending` added), and primary (`EA, KT, FT, BX, M`) vs. extended (`RL, PK`) UOM rules.
- **Review Standards**: Established the 4 governed finding classifications (`Action Required`, `Review Recommended`, `Advisory`, `Informational`), the 4 Release Readiness Outcomes, and the 5-line / 5-run spacing tolerance rule.

---

## Version 1.0 — Initial Repository Baseline (`2026-10-26`)

- Established initial NEA repository structure, core Standards, Workflows, Behavior charter, and Excel workbook templates (`BOM_Materials_Master_Template.xlsx`, `Cable_Running_List_Template.xlsx`, `Project_Cover_Sheet_Template.xlsx`).
