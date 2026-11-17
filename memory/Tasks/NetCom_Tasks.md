---
title: "NetCom — Domain Task Umbrella"
entity: "NetCom"
compartment: "private"
note_type: "task_umbrella"
last_synced: "2026-11-17"
---

# 🏢 NetCom — Active Engineering Task Umbrella (`Tasks/NetCom_Tasks.md`)

> **Single-Writer Task Governance (`entity: NetCom`)**:
> - **Strict Entity Boundary**: **NetCom (`netcom1989.com`)** is an independent enterprise completely separate from **Alchemical-3D**.
> - All active checkboxes (`- [ ]` / `- [x]`) for projects owned by **`NetCom`** live exclusively in this file.

---

<!-- AUTO-ROLLUP:START -->
**Progress Summary**: `8 / 9` Tasks Complete (`88.9%`) | Open Tasks: `1` | Open `[TBD]`s: `1`

| Project | Checkpoint (`HEAD` · `Worktree`) | Open Tasks | Open `[TBD]`s | Latest Handoff / Next Kickstart |
| :--- | :--- | :---: | :---: | :--- |
| [`NetCom_Engineering_Assistant`](../Projects/NetCom_Engineering_Assistant/NetCom_Engineering_Assistant.md) (`#L35`) | `UNTRACKED` (`untracked`, `2026-11-17`) | `1` | `1` | Next: Execute [P2] CRL -> Project BOM takeoff & rollup engine (GOV-001, GOV-008) in NetCom_Tasks.md · Stage pre-commit-gate & commit... |
<!-- AUTO-ROLLUP:END -->

---

<!-- AUTO-PROJECT-TASKS:START -->
# 🏢 NetCom Engineering Assistant Task Umbrella (`NetCom_NEA_Tasks`)

> [!IMPORTANT]
> **Strict Entity Separation**: **NetCom (`netcom1989.com`)** is an independent corporate entity completely separate from **Alchemical-3D**. This umbrella isolates all NetCom `NEA v2.2.3` tasks cleanly from maker/hardware queues and is transcluded into [`NetCom_Engineering_Assistant`](../Projects/NetCom_Engineering_Assistant/NetCom_Engineering_Assistant.md) and [`README.md`](../README.md).

---

## NetCom_Engineering_Assistant

### Phase A: Markdown Consolidation, `NEA-SCR-001` Telemetry & Anti-Hallucination (Completed `2026-10-28` / `2026-11-01`)
- [x] **`[P0]`–`[P1]` Markdown Consolidation (`91.8%`), `inspect_nea_workbooks.py` (`NEA-SCR-001`) & 3-Tier `Cable Harness` Field Hardening (`SBX-20261101_172152-eedf5171`):** Retired `Capabilities/` (`28` $\rightarrow$ `19` files), built `Scripts/inspect_nea_workbooks.py` (`-87.7%` cached tokens in `Run #7`), deduplicated `tblMaterials` (`505` unique keys), wired `Cable Harness` (`202` variants) + 3-tier `XLOOKUP`, and added `CRL-DATA-003` duplicate endpoint detection (`2026-10-28_NEA_v1.3_Consolidation_and_Anti_Hallucination`, [`NetCom_Engineering_Assistant_Lessons_Learned`](../Projects/NetCom_Engineering_Assistant/NetCom_Engineering_Assistant_Lessons_Learned.md)).

### Phase B: Separate Excel Template Remediation & Sanitization Track (`IR3-02`–`IR3-04`, `GOV-009`)
- [x] **`[P0]` Restore Overwritten `Project BOM` Formulas (`D8:I155`) & Catalog Deduplication (`tblMaterials`):** Restored 100% of `Project BOM` formulas across `Rows 8:155` (`0` static formula overwrites), removed un-formulad `Row 156` stub, and deduplicated `tblMaterials` (`505` unique keys, `0` duplicates).
- [x] **`[P1]` Unit-Aware `Project BOM!G4` Summary Formula (`GOV-002`) & Cover Sheet Parity (`GOV-006`, `GOV-009`):** Archived `307-2` originals (`f47a9f3ad7`, `e6b4614fa2`, `82caf65dc0`) into `NEA_v2.2.3/Testbeds/307-2/`, replaced mixed-UOM `Project BOM!G4` with unit-segregated `F4:G4` (`Total FT` `SUMIF`) and `F5:G5` (`Total EA/KT/BX` `SUMIF`), added `Project Number` (`R12` CRL/Standalone) and `Document Status` dropdown (`BOM D26:H26`, `CRL/Standalone D28:H28`), linked Revision History formulas (`B32:C32` BOM, `B34:C34` CRL/Standalone, `Print_Area $B$2:$H$42`), rescaled `tblMaterials` (`A3:G508`) + `Lists!H1` `(<>0)` + `Fiber Assemblies!H4:H1258`, cleared `307-2` sample rows from `Templates/*.xlsx` (`NEA-VRF-B8758592E52D`, OpenXML PASS), and updated `inspect_nea_workbooks.py` (label-driven Cover Sheet + blank-CRL `0`-run guard), `Copilot_Agents/`, and `Skills/*.zip` via `build_copilot_agents.py` (verified live on remote NetCom M365 Copilot machine: "Repairs are complete. The workbook can return to the Builder or NEA Package Reviewer.").

### Phase C: Expanded Sandbox Stress-Testing (`IR3-14`–`IR3-16` & Adversarial Gates)
- [x] **`[P1]` Adversarial Anti-Hallucination, Tier-2 Escalation & Delta-Cache Sandbox Tests (`OS Dry-Run`, `10/10` PASS):** Verified (1) `[EXTRACTION BLOCKED — REVIEW ABORTED]` (`exit=2`) across empty folder, `chmod 000` unreadable `.xlsx`, and corrupt `.xlsx` (fixed `discover_xlsx_files()` fallback escape bug + `parse_xlsx()` error guard), (2) `🚨 [TIER-2 ESCALATION REQUIRED]` across extra worksheet tab, extra 17th CRL column (`Q2='Cable Run Status'`), extra BOM column (`K7='Unit Cost'`), and non-standard UOM `'GAL'` (added Row-2 CRL / Row-7 BOM unmapped-column `escalation_triggers` checks, `0` false positives on `Templates/` and `Testbeds/307-2/`), and (3) `--scope delta` `SHA-256` cache hit/miss/re-hit transitions; rebuilt `Skills/*.zip` via `build_copilot_agents.py`.
- [x] **`[P1]` Operational Build, Catalog & Repair Workflow Sandbox Tests (`IR3-14`–`IR3-16`):** Verified all 5 NEA agents (`NEA Package Reviewer`, `NEA BOM Builder`, `NEA CRL Builder`, `NEA Catalog Manager`, `NEA Repair Tool`) across two 5-agent Cold-Start `Blind-Light (Flash)` swarms (`d871f794`..`93fb6f80` and `0bf07258`..`1f8cc443`), confirming `--scope`, `--lookup`, `--repair`, and `--verify-write` (`0` formula losses, `<extLst>` intact, `0` custom Python lines).

### Phase D: `NEA v2.2.3` Copilot 6-Agent Suite, Multi-Media Timesheet Consolidator, Cross-Duty Informer & Bundled Skills (`GOV-015`–`GOV-018`)
- [x] **`[P0]` `NEA v2.0.0`–`v2.2.3` 5-Agent Suite, OpenXML `[4E]` / `--repair` Engine & Bundled-Script `<skill-name>.zip` Packaging (`SBX-20261103_131300-7cb27db8`):** Promoted `/home/orin/Projects/Engineering/NEA_v2.2.3` to `Version 2.2.3`, split `NEA Repair Tool` (`NEA-AGT-005`) as the 5th specialist (initially `5,330`/`3,820`/`3,342`/`3,794`/`3,607` instruction chars; later `5,463`/`3,852`/`3,413`/`3,794`/`3,725` after `GOV-006`), added role-scoped `--scope {review,bom,crl,catalog,repair}`, `UOM=BX` bulk-box anomaly detection, and `--repair` (`tblMaterials`, `Lists!H1`, `Fiber Assemblies!H4:H1258`, CRL `[4E]` validation), initially packaged `8` `Skills/<skill-name>/<skill-name>.zip` archives (subsequently consolidated in `d71b7b5` to the **`3` Core Guardrail Skills** `NEA-SKL-001`..`003` because per-agent role skills duplicated `Instructions.txt` + `inspect_nea_workbooks.py`), and delivered `NEA_User_and_DevOps_Manual.md` (`NEA-MAN-001`; see [`NetCom_Engineering_Assistant`](../Projects/NetCom_Engineering_Assistant/NetCom_Engineering_Assistant.md) and [`NetCom_Engineering_Assistant_Lessons_Learned`](../Projects/NetCom_Engineering_Assistant/NetCom_Engineering_Assistant_Lessons_Learned.md)).
- [x] **`[P0]` 6th Specialist Agent (`NEA Timesheet Consolidator` `NEA-AGT-006`), `Timesheet_Template.xlsx` (`NEA-TPL-004`) & Module Launchpad (`GOV-018`, `SBX-20261104_125900-8d70fad1` & Cold-Start `Blind-Light` `24831c6b`):** Built `Templates/Timesheet_Template.xlsx` (`SHA256=5bf4f136c8`, `Expense Report` stripped, `AG35` Job Slot 10 `REG` formula restored, styled with the NetCom Corporate Color Palette `cellXfs 217..239` for the `Weekly Summary` executive dashboard), extended `Scripts/inspect_nea_workbooks.py` with `--consolidate` (`Week_of_MM-DD_to_MM-DD.xlsx` with `Weekly Summary` Tab 1, `Job Summary` Tab 2, + alphabetical `Last, First` employee tabs), `--scope timesheet`, and `validate_openxml_package_integrity()` (`0` Desktop Excel OpenXML issues), compiled `Copilot_Agents/NEA_Timesheet_Consolidator/` (later expanded by Option C to `6,206 / 8,000` chars, `5` Knowledge `.txt` files; initial redundant `nea-timesheet-consolidator.zip` `NEA-SKL-009` retired in `d71b7b5` into the `3` Core Guardrail Skills), and codified [`NetCom_Engineering_Assistant_Module_Launchpad`](../Projects/NetCom_Engineering_Assistant/NetCom_Engineering_Assistant_Module_Launchpad.md).
- [x] **[COMPLETED 2026-11-17] `[P2]` Controlled Safe-Write Helper Script (`Scripts/edit_nea_workbooks.py`):** Built pure-stdlib, fail-closed OpenXML JSON-manifest writer (`982` lines, `ee7051c693`) for `BOM_Materials_Master`, `Cable_Running_List`, and `Project_Cover_Sheet` reusing `inspect_nea_workbooks.py` primitives (`classify_workbook_role()`, `find_cover_sheet_coords()`, `SharedStringTable`, `_sort_sheetdata_rows_and_cells()`, `preserve_openxml_extensions()`, `run_verify_write()`), synced cached formula values + `fullCalcOnLoad="1"` while keeping `<extLst>`, `<f>`, and namespaces intact, bundled into `Skills/nea-workbook-entry-guard/nea-workbook-entry-guard.zip` (`ZIP_SHA256=a99fb5dafe`, `NEA_BOM_Builder` `3,970/8,000` chars, `NEA_CRL_Builder` `3,596/8,000` chars) via `build_copilot_agents.py`, updated `README.md` + `NEA_User_and_DevOps_Manual.md` + `nea-copilot-builder/SKILL.md`, and verified via `OS Dry-Run (+faults)` (`5/5` tests `5.350s` OK including `15` fault injections and extracted `.zip` Code Interpreter simulation; `NEA-WRT-FFE45B1EE55E`, `NEA-WRT-73945B363732`, `NEA-WRT-8A8F41E896EC`, `NEA-WRT-C88A0640E8A8`, `NEA-WRT-F1D2A28FB975`).
- [ ] **`[P2]` Automated `CRL` $\rightarrow$ `Project BOM` Takeoff & Rollup Engine (`GOV-001`, `GOV-008`):** Extend `Scripts/` to compute required copper spools, backbone fiber cut lengths, station jumpers, and termination hardware from an approved CRL via `--lookup`.
<!-- AUTO-PROJECT-TASKS:END -->

---

## 🧭 Untracked / On-Demand Future Expansion (No Active Checkbox)
- **Multi-Workbook Ecosystem Expansion (`Workbook_Types` Sec 6):** Moved to untracked (`2026-11-17`) until NetCom decides which new deliverable templates (`Rack Elevation`, `Equipment Schedule`, `Fiber Splice / Assignment Schedule`, `Test Log`, or `Power Schedules`) to expand into next. When triggered, onboard one module at a time via [`NetCom_Engineering_Assistant_Module_Launchpad`](../Projects/NetCom_Engineering_Assistant/NetCom_Engineering_Assistant_Module_Launchpad.md) (`Templates/`, `Workbook_Types` Sec 1–2, `inspect_nea_workbooks.py` `classify_workbook_role()`, `build_copilot_agents.py`, `README.md`).
