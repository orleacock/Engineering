# NEA Governance & Improvement Register

Version: 2.2.3
Status: Current
Document ID: NEA-GOV
Logical Name: NEA_Governance_Register
Owner: NetCom Technical Services

## Purpose

This document is the authoritative register for workbook template enhancements, catalog maintenance boundaries, technical debt, and architectural decisions across the NetCom Engineering Assistant (NEA).

Items recorded in this register do not penalize project engineers during deliverable reviews; instead, template and catalog governance items are segregated into **Section 5 (`CAT-##` / `TPL-##`)** of `Review_Report_Template` (`NEA-REF-003`). Current approved artifact versions are governed by `README.md` and `Copilot_Agents/<Agent>_v2.2.3/Knowledge/*.txt`.

---

## 1. Governance Summary Matrix (`GOV-001` – `GOV-018`)

| ID | Category | Priority | Status | Affected Artifacts | Summary & Operational Boundary |
| :---: | :--- | :---: | :---: | :--- | :--- |
| **`GOV-001`** | Automation Enhancement | Medium | `Open` | `BOM_Standards`, `CRL_Standards` | Investigate controlled material-rollup automation deriving `Project BOM` quantities from approved `Cable Running List` data. |
| **`GOV-002`** | Catalog & BOM Summary Maintenance | Low | `Open` | `Material_Master_Standards`, `Material_Catalog_Workflow`, `BOM_Materials_Master_Template.xlsx` | Completed `tblMaterials` (`$A$3:$G$600`) primary-key deduplication (`505` unique keys, `0` duplicates); future replacement of `Project BOM!G4` (`=SUM(C8:C155)`) with unit-aware summary formulas remains open. |
| **`GOV-003`** | UOM Validation Sync | Medium | `Complete` | `Material_Master_Standards`, `BOM_Standards`, `BOM_Materials_Master_Template.xlsx` | Established `Lists!$C$2:$C$6` (`EA`, `KT`, `FT`, `BX`, `M`) as primary workbook-validated UOMs while recognizing `RL` (Roll) and `PK` (Pack) as Standard-permitted catalog UOMs pending future `Lists` dropdown expansion. |
| **`GOV-004`** | Catalog Categories | Low | `Open` | `Material_Master_Standards`, `BOM_Materials_Master_Template.xlsx` | Periodically review the 16 Material Categories (plus `Cable Harness`) as the catalog expands. |
| **`GOV-005`** | Status-Domain Governance | Low | `Complete` | `Project_Metadata_Standard`, `CRL_Standards`, `BOM_Standards` | Locked the 3-domain status model (`Document Status`, `Material Status`, `Review Status`) and retired per-row `Cable Run Status` so the released CRL serves as installation paper truth. |
| **`GOV-006`** | Cover Sheet Parity | Medium | `Deferred` | `Project_Metadata_Standard`, `Workbook_Types`, All 3 `.xlsx` Templates | Standardize Cover Sheet layouts across templates in a future template pass (adding `Project Number` to CRL/Standalone Cover Sheets, adding a dedicated `Document Status` cell, and linking `B30:C30` Revision History formulas). |
| **`GOV-007`** | Table & Formula Lock | Medium | `Complete` | `Formatting_Standards`, `Workbook_Types`, `BOM_Materials_Master_Template.xlsx` | **Strict Guardrail**: Preserve `tblMaterials` (`$A$3:$G$600`) exact table name for `Lists!H1` (`FILTER(VSTACK(...))`) and `Project BOM` 3-tier `XLOOKUP` formulas; keep `Project BOM` (`A7:J155`) as a standard formula range (never convert to a ListObject table); added `Column H` (`Status`) to `Fiber Assemblies` and `Cable Harness`. |
| **`GOV-008`** | Cross-Doc Rollup | High | `Open` | `Project_Review_Workflow`, `BOM_Standards`, `CRL_Standards` | Future quantitative helper formulas/scripts supporting automated `CRL` ↔ `Project BOM` length and connector takeoff comparison. |
| **`GOV-009`** | Template Sanitization | Medium | `Deferred` | All 3 `.xlsx` Templates in `Templates/` | Retain embedded regression-testbed project data during `v2.2.3` validation/testing; restore `CRL Cover Sheet!B30` formula and clear sample project rows prior to blank production template deployment. |
| **`GOV-010`** | Reference Normalization | Low | `Complete` | `Repository_Index.md`, All `.md` Files | Normalized prose references to logical document names resolved via `Repository_Index.md`. |
| **`GOV-011`** | Review Workflow | Low | `Complete` | `Workflows/Project_Review_Workflow_v2.2.3.md` | Established dedicated `Project_Review_Workflow` (`NEA-WF-004`) and standardized output report (`Review_Report_Template`, `NEA-REF-003`). |
| **`GOV-012`** | Documentation Compaction | Low | `Complete` | Repository-wide `.md` files | Completed `v1.3` Architecture Consolidation & Token Optimization pass, reducing active Markdown footprint by >80% while preserving all engineering rules. |
| **`GOV-013`** | Catalog Module Consolidation | Low | `Complete` | `Material_Master_Standards`, `Material_Catalog_Workflow` | Consolidated `Material_Management`, `Material_Master_Maintenance`, and `Material_Import_Workflow` into `Material_Master_Standards` (`NEA-STD-006`) and `Material_Catalog_Workflow` (`NEA-WF-001`), retiring the `Capabilities/` folder. |
| **`GOV-014`** | Changelog Compaction | Low | `Complete` | `CHANGELOG.md` | Centralized all artifact revision histories into a compact, release-segmented `CHANGELOG.md`. |
| **`GOV-015`** | M365 Copilot Agent Builder Suite & OneDrive Latency Bypass | High | `Complete` | `Copilot_Agents/*`, `Scripts/build_copilot_agents.py`, `README.md` | Built the `NEA v2.2.3` 4-Agent Modular Specialist Suite (`NEA Package Reviewer`, `NEA BOM Builder`, `NEA CRL Builder`, `NEA Catalog Manager`) with `< 8,000`-char inline-compiled `declarativeAgent.json` `.zip` packages, Option 2 direct `.txt` Knowledge packs, and direct chat-attachment Code Interpreter execution to bypass OneDrive Graph indexing lag. |
| **`GOV-016`** | Packaged Agent Skills (`<skill-name>.zip` with Bundled `scripts/inspect_nea_workbooks.py`) & OpenXML `<extLst>` Write Lock | High | `Complete` | `Skills/<skill-name>/*`, `Scripts/inspect_nea_workbooks.py` | Packaged the companion guardrail and role skills (`NEA-SKL-001` Anti-Hallucination, `NEA-SKL-002` Workbook Entry Guard with `preserve_openxml_extensions()`, `NEA-SKL-003` Verification & Receipt with `--verify-write` `NEA-WRT-<12hex>`, plus role skills) as self-contained `<skill-name>.zip` archives bundling root-level `SKILL.md` + `scripts/inspect_nea_workbooks.py` per Microsoft's Declarative Agent Skills specification, eliminating `22` duplicate `.txt` copies across `Knowledge/` and `Skills/`. |
| **`GOV-017`** | 5-Agent Split (`NEA Repair Tool` `NEA-AGT-005`) & Lightweight Cross-Duty Informer | High | `Complete` | `Copilot_Agents/*`, `Scripts/inspect_nea_workbooks.py`, `Scripts/build_copilot_agents.py`, `Skills/*` | Separated project engineering review (`NEA Package Reviewer` `NEA-AGT-001`, reduced from `99.4%` to `66.6%` prompt saturation) from non-destructive workbook/template formula & OpenXML repair (`NEA Repair Tool` `NEA-AGT-005` `--repair`), and added Section 7 (`🔄 [CROSS-DUTY -> <Agent>]`) to `inspect_nea_workbooks.py` for zero-prompt-overhead cross-duty agent routing. |
| **`GOV-018`** | 6th Specialist Agent (`NEA Timesheet Consolidator` `NEA-AGT-006`) & Multi-Media Missouri Timesheet Engine (`NEA-TPL-004`) | High | `Complete` | `Templates/Timesheet_Template.xlsx`, `Copilot_Agents/NEA_Timesheet_Consolidator/*`, `Skills/nea-timesheet-consolidator/*`, `Scripts/inspect_nea_workbooks.py` | Added the 6th M365 Copilot agent (`NEA Timesheet Consolidator` `NEA-AGT-006`), `Timesheet_Standards_v2.2.3.txt` (`NEA-STD-007`), `Timesheet_Consolidation_Workflow_v2.2.3.txt` (`NEA-WF-006`), and sanitized `Templates/Timesheet_Template.xlsx` (`NEA-TPL-004`, stripping `Expense Report` `sheet2.xml` and restoring the missing `AG35` Job Slot 10 `REG` sum formula) to consolidate digital `.xlsx`, scanned `.pdf`, and photographed `.png`/`.jpg` Missouri Timesheets into `Week_of_MM-DD_to_MM-DD.xlsx` (`Weekly Summary` Tab 1 + alphabetical `Last, First` employee tabs). |

---

## 2. Critical Workbook & Catalog Maintenance Guardrails (`GOV-002`, `GOV-006`, `GOV-007`)

Whenever template or catalog maintenance is authorized by an operator, enforce these four non-negotiable technical constraints:

1. **Preserve `tblMaterials` Structured Reference (`GOV-007`)**:
   - `Materials Master` (`$A$3:$G$600`) is an official Excel Table named `tblMaterials`. Never rename or unlist `tblMaterials`, as `Lists!H1` (`BOMPartNumbers` `FILTER(VSTACK(...))`) and all `Project BOM` `Columns D:I` `XLOOKUP` formulas reference `tblMaterials[...]` directly.
2. **Keep `Project BOM` (`A7:J155`) as a Formula Range (`GOV-007`)**:
   - Never convert `Project BOM` into an Excel ListObject Table. It intentionally operates as a standard range so engineers can insert `<= 5` blank grouping rows between material sections while keeping `Column A` and `Columns D:I` formulas intact.
3. **3-Tier Catalog & `Lists!H1` Spill Integrity (`GOV-007`)**:
   - Both `Fiber Assemblies` (`$A$3:$H$1258`) and `Cable Harness` (`$A$3:$H$1258`) include `Column H` (`Status`). Unassigned `Cable Harness` variants keep `Col C` (`MB P/N`) blank and `Col H` (`Status = Pending`), filtered cleanly by `Lists!H1` (`FILTER(VSTACK(...), ... <> "")`).
4. **Embedded Regression Testbed Baseline (`GOV-002`, `GOV-006`, `GOV-009`)**:
   - The current `.xlsx` templates retain seeded sample project defects as a live regression testbed until `GOV-009` production sanitization is executed. Specific cell values and part numbers must always be extracted dynamically from the `.xlsx` files via `Scripts/inspect_nea_workbooks.py` or the Code Interpreter OpenXML kernel.
