---
title: "NetCom — Domain Task Umbrella"
entity: "NetCom"
compartment: "private"
note_type: "task_umbrella"
last_synced: "2026-11-11"
---

# 🏢 NetCom — Active Engineering Task Umbrella (`Tasks/NetCom_Tasks.md`)

> **Single-Writer Task Governance (`entity: NetCom`)**:
> - **Strict Entity Boundary**: **NetCom (`netcom1989.com`)** is an independent enterprise completely separate from **Alchemical-3D**.
> - All active checkboxes (`- [ ]` / `- [x]`) for projects owned by **`NetCom`** live exclusively in this file.

---

<!-- AUTO-ROLLUP:START -->
**Progress Summary**: `5 / 10` Tasks Complete (`50.0%`) | Open: `5`
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
- [ ] **`[P1]` Unit-Aware `Project BOM!G4` Summary Formula (`GOV-002`) & Cover Sheet Parity (`GOV-006`, `GOV-009`):** Replace mixed-UOM `Project BOM!G4` (`=SUM(C8:C155)`) with unit-segregated summary metrics (`Total FT` vs. `Total EA/KT/BX`), add `Project Number` and `Document Lifecycle State` to CRL/Standalone Cover Sheets, link `CRL Cover Sheet!B30:C30` formulas, and archive the `307-2` regression testbed into a dedicated test folder when ready to clear `Templates/*.xlsx` for blank production deployment.

### Phase C: Expanded Sandbox Stress-Testing (`IR3-14`–`IR3-16` & Adversarial Gates)
- [ ] **`[P1]` Adversarial Anti-Hallucination, Tier-2 Escalation & Delta-Cache Sandbox Tests:** Verify (1) `[EXTRACTION BLOCKED — REVIEW ABORTED]` triggers cleanly when `.xlsx` access is blocked, (2) `🚨 [TIER-2 ESCALATION REQUIRED]` triggers when an unmapped sheet/column is introduced, and (3) `--scope delta` skips unchanged workbooks via `SHA-256` cache.
- [x] **`[P1]` Operational Build, Catalog & Repair Workflow Sandbox Tests (`IR3-14`–`IR3-16`):** Verified all 5 NEA agents (`NEA Package Reviewer`, `NEA BOM Builder`, `NEA CRL Builder`, `NEA Catalog Manager`, `NEA Repair Tool`) across two 5-agent Cold-Start `Blind-Light (Flash)` swarms (`d871f794`..`93fb6f80` and `0bf07258`..`1f8cc443`), confirming `--scope`, `--lookup`, `--repair`, and `--verify-write` (`0` formula losses, `<extLst>` intact, `0` custom Python lines).

### Phase D: `NEA v2.2.3` Copilot 6-Agent Suite, Multi-Media Timesheet Consolidator, Cross-Duty Informer & Bundled Skills (`GOV-015`–`GOV-018`)
- [x] **`[P0]` `NEA v2.0.0`–`v2.2.3` 5-Agent Suite, OpenXML `[4E]` / `--repair` Engine & Bundled-Script `<skill-name>.zip` Packaging (`SBX-20261103_131300-7cb27db8`):** Promoted `/home/orin/Projects/Engineering/NEA_v2.2.3` to `Version 2.2.3`, split `NEA Repair Tool` (`NEA-AGT-005`) as the 5th specialist (`5,330`/`3,820`/`3,342`/`3,794`/`3,607` instruction chars), added role-scoped `--scope {review,bom,crl,catalog,repair}`, `UOM=BX` bulk-box anomaly detection (`Row 70`), and `--repair` (`tblMaterials`, `Lists!H1`, `Fiber Assemblies!H4:H1258`, CRL `[4E]` validation), packaged `8` `Skills/<skill-name>/<skill-name>.zip` archives (`dash_lines == [1, 4]` + bundled `scripts/inspect_nea_workbooks.py`), and delivered `NEA_User_and_DevOps_Manual.md` (`NEA-MAN-001`) + `/home/orin/Downloads/NEA_v2.2.3_Delivery.zip` (`76` files, `SHA256=0b15b75b3ed5`; details in [`NetCom_Engineering_Assistant`](../Projects/NetCom_Engineering_Assistant/NetCom_Engineering_Assistant.md) and [`NetCom_Engineering_Assistant_Lessons_Learned`](../Projects/NetCom_Engineering_Assistant/NetCom_Engineering_Assistant_Lessons_Learned.md)).
- [x] **`[P0]` 6th Specialist Agent (`NEA Timesheet Consolidator` `NEA-AGT-006`), `nea-timesheet-consolidator.zip` (`NEA-SKL-009`), `Timesheet_Template.xlsx` (`NEA-TPL-004`) & Module Launchpad (`GOV-018`, `SBX-20261104_125900-8d70fad1` & Cold-Start `Blind-Light` `24831c6b`):** Built `Templates/Timesheet_Template.xlsx` (`SHA256=5bf4f136c8`, `Expense Report` stripped, `AG35` Job Slot 10 `REG` formula restored, styled with the NetCom Corporate Color Palette `cellXfs 217..239` for the `Weekly Summary` executive dashboard), extended `Scripts/inspect_nea_workbooks.py` with `--consolidate` (`Week_of_MM-DD_to_MM-DD.xlsx` with `Weekly Summary` Tab 1 + alphabetical `Last, First` employee tabs), `--scope timesheet`, and `validate_openxml_package_integrity()` (`0` Desktop Excel OpenXML issues), compiled `Copilot_Agents/NEA_Timesheet_Consolidator/` (`5,220 / 8,000` chars, `5` Knowledge `.txt` files) + `Skills/nea-timesheet-consolidator/nea-timesheet-consolidator.zip` (`5,614 / 8,000` chars), and codified [`NetCom_Engineering_Assistant_Module_Launchpad`](../Projects/NetCom_Engineering_Assistant/NetCom_Engineering_Assistant_Module_Launchpad.md).
- [ ] **`[P2]` Controlled Safe-Write Helper Script (`Scripts/edit_nea_workbooks.py`):** Build a deterministic Python workbook writer enforcing `Behavior_v2.2.3.txt` write locks (`Cover Sheet` inputs, `Project BOM` Columns `B, C, J`, and `CRL` rows only).
- [ ] **`[P2]` Automated `CRL` $\rightarrow$ `Project BOM` Takeoff & Rollup Engine (`GOV-001`, `GOV-008`):** Extend `Scripts/` to compute required copper spools, backbone fiber cut lengths, station jumpers, and termination hardware from an approved CRL via `--lookup`.
- [ ] **`[P2]` Multi-Workbook Ecosystem Expansion (`Workbook_Types` Sec 5):** Onboard next-generation NetCom deliverable templates (`Rack Elevation`, `Equipment Schedule`, `Fiber Splice / Assignment Schedule`, `Test Log`) into `Templates/`, `Repository_Index.md`, and `inspect_nea_workbooks.py`.
<!-- AUTO-PROJECT-TASKS:END -->
