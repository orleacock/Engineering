# NetCom Engineering Assistant (`NEA v2.2.3`)

- **Version**: `2.2.3`
- **Status**: `Current (M365 Copilot Declarative Agent Suite)`
- **Document ID**: `NEA-README`
- **Owner**: `NetCom Technical Services`

---

## 1. Overview & Architecture (`Option A — 6-Agent M365 Copilot Suite & Cross-Duty Informer`)

The **NetCom Engineering Assistant (`NEA v2.2.3`)** is a Microsoft 365 Copilot Declarative Agent suite and deterministic OpenXML workbook inspection/repair/consolidation system for NetCom Technical Services. It assists engineers and operations staff in building, auditing, validating, and repairing structured-cabling project deliverable packages (`Cover Sheet`, `Materials Master` / `Project BOM`, and `Cable Running List`) and consolidating multi-media weekly Missouri Timesheets (`Week_of_MM-DD_to_MM-DD.xlsx`).

### Core Design Principles
1. **Paper Truth Upon Handoff (`GOV-005`)**: Once the engineer completes a deliverable package and hands it off to installation, the released spreadsheets serve as the field team's **paper truth** (`Cable Run Status` per row is retired).
2. **Zero OneDrive Graph Latency (`+ Upload from device` $\rightarrow$ Code Interpreter)**: Designers attach live `.xlsx`, `.pdf`, or image files directly into the Copilot chat turn (`+` button) so they mount immediately inside the active **Code Interpreter** container (`/mnt/data/`) with `0` SharePoint search-indexing delay.
3. **Integrated Agent Builder UI Kit, Bundled-Script Skills & Cross-Duty Informer (`GOV-016`–`GOV-018`)**: All governing NEA `v2.2.3` domain Standards, Workflows, and Behavior rules are maintained as Graph-safe `.txt` files inside each agent's `Copilot_Agents/<Agent>/Knowledge/` folder (`5`–`7` files per agent, with zero duplicate skill or script files) alongside `Agent_Config.md` and `Instructions.txt`. Meanwhile, `Scripts/build_copilot_agents.py` compiles each skill under `Skills/<skill-name>/` with root-level `SKILL.md` plus `scripts/inspect_nea_workbooks.py` bundled inside `<skill-name>.zip` per Microsoft's Declarative Agent Skills specification. Section 7 of `scripts/inspect_nea_workbooks.py` automatically emits lightweight `🔄 [CROSS-DUTY -> <Agent>]` advisories whenever an issue requires a sister agent (routing workbook formula/OpenXML repairs to `NEA Repair Tool` and catalog maintenance to `NEA Catalog Manager`).

---

## 2. Lean Repository Structure (`NEA_v2.2.3`)

```text
NEA_v2.2.3/
├── Copilot_Agents/
│   ├── Agent_Builder_Guide.md                       # M365 Copilot Agent Builder Deployment Guide (6 Agents)
│   ├── NEA_Package_Reviewer/                        # Mode 1: Agent_Config.md, Instructions.txt & Knowledge/*.txt (5 files)
│   ├── NEA_BOM_Builder/                             # Mode 2: Guided Project BOM Build & Takeoff (6 Knowledge .txt files)
│   ├── NEA_CRL_Builder/                             # Mode 2: Guided 16-Col Cable Running List Build (6 Knowledge .txt files)
│   ├── NEA_Catalog_Manager/                         # Mode 2: 3-Tier Catalog Hygiene & Onboarding (7 Knowledge .txt files)
│   ├── NEA_Repair_Tool/                             # Mode 2: Non-Destructive Workbook Formula & OpenXML Repair (6 Knowledge .txt files)
│   └── NEA_Timesheet_Consolidator/                  # Mode 2: Multi-Media Missouri Timesheet Consolidation (5 Knowledge .txt files)
├── Scripts/
│   ├── inspect_nea_workbooks.py                     # Master OpenXML Inspector, Write Verifier, Repair & Timesheet Engine (NEA-SCR-001)
│   ├── build_copilot_agents.py                      # Compiles Copilot_Agents/<Agent>/ & Skills/<skill-name>/<skill-name>.zip
│   └── package_nea_delivery.py                      # Packages clean NEA_v2.2.3_Delivery.zip
├── Skills/
│   ├── Skills_Deployment_Guide.md                   # Guide for uploading the 3 Core Guardrail Skill .zip packages
│   ├── nea-anti-hallucination/                      # SKILL.md, scripts/inspect_nea_workbooks.py & nea-anti-hallucination.zip
│   ├── nea-verification-and-receipt/                # SKILL.md, scripts/inspect_nea_workbooks.py & nea-verification-and-receipt.zip
│   └── nea-workbook-entry-guard/                    # SKILL.md, scripts/inspect_nea_workbooks.py & nea-workbook-entry-guard.zip
├── Templates/
│   ├── BOM_Materials_Master_Template.xlsx           # 6-tab Master Catalog & Project BOM Template
│   ├── Cable_Running_List_Template.xlsx             # 3-tab 16-Column Cable Running List Template
│   ├── Project_Cover_Sheet_Template.xlsx            # Standalone Project Cover Sheet Template
│   └── Timesheet_Template.xlsx                      # Single-tab Cleaned Missouri Timesheet Template (Expense Report stripped)
├── CHANGELOG.md                                     # Controlled Revision History (v1.0 -> v2.2.3)
├── NEA_Governance_Register_v2.2.3.md                # Architectural Decisions & Waivers (GOV-001..GOV-018)
├── NEA_User_and_DevOps_Manual.md                    # Human Engineer User Manual, Prompt Sheet & DevOps Guide (NEA-MAN-001)
└── README.md                                        # This document
```

---

## 3. Quick Commands (Workstation Maintenance)

```bash
# 1. Run deterministic OpenXML workbook inspection, 3-tier catalog lookup, non-destructive repair, timesheet consolidation & write verification:
python3 Scripts/inspect_nea_workbooks.py Templates
python3 Scripts/inspect_nea_workbooks.py Templates --scope timesheet
python3 Scripts/inspect_nea_workbooks.py Templates --lookup "Cat6A"
python3 Scripts/inspect_nea_workbooks.py Templates --repair --out-dir /tmp/Repaired_Workbooks
python3 Scripts/inspect_nea_workbooks.py --consolidate manifest.json --template Templates/Timesheet_Template.xlsx --out Week_of_10-25_to_10-31.xlsx
python3 Scripts/inspect_nea_workbooks.py --verify-write orig.xlsx edited.xlsx

# 2. Rebuild Copilot_Agents/ & Skills/<skill-name>/<skill-name>.zip:
python3 Scripts/build_copilot_agents.py

# 3. Package clean NEA_v2.2.3_Delivery.zip archive:
python3 Scripts/package_nea_delivery.py
```

For full Microsoft 365 Copilot deployment, daily designer instructions, copy-paste prompt examples, and DevOps expansion guidelines, see [`NEA_User_and_DevOps_Manual.md`](NEA_User_and_DevOps_Manual.md) and [`Copilot_Agents/Agent_Builder_Guide.md`](Copilot_Agents/Agent_Builder_Guide.md).
