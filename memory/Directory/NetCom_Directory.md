---
title: "NetCom — Memory & Repository Directory Tree"
entity: "NetCom"
compartment: "private"
type: "entity-directory"
tree_hash: "24b801bf1e57"
last_synced: "2026-11-11"
---

# 🗂️ `NetCom` — Directory Lookup Map (`entity: NetCom`)

> **Turn-1 Cold-Start Location Map (`pre-commit-gate` Stage X)**: Read this note on Turn 1 to resolve exact file paths across `<memory_root>/` and `NetCom` repositories without running `ls`, `find`, or `os.listdir` probes. Cross-entity repositories outside `NetCom` are strictly excluded (`CROSS_ENTITY_CONTAMINATION` firewall).

- **Directory Index**: [`Directory_Index.md`](Directory_Index.md) | **Task Umbrella**: [`NetCom_Tasks.md`](../Tasks/NetCom_Tasks.md)

---

## 1. `NetCom` Memory Dossiers, Standards & Templates (`<memory_root>/`)

```text
+------------------------------------------------------------+
            --- DIRECTORY STRUCTURE ---
+------------------------------------------------------------+

./
├── Diagrams/
│   ├── NEA_v2_Copilot_Execution_Flowchart.md
│   ├── NEA_v2_Copilot_Execution_Flowchart.svg
│   └── Project_Ecosystem_Map.canvas
├── Directory/
│   ├── Directory_Index.md
│   ├── NetCom_Decision_Router.md
│   ├── NetCom_Directory.md
│   └── NetCom_memory_index.json
├── Profile/
│   └── Decision_Profile.md
├── Projects/
│   └── NetCom_Engineering_Assistant/
│       ├── Quarantine/
│       │   └── Quarantine_README.md
│       ├── NetCom_Engineering_Assistant.md
│       ├── NetCom_Engineering_Assistant_Lessons_Learned.md
│       ├── NetCom_Engineering_Assistant_Module_Launchpad.md
│       └── NetCom_Engineering_Assistant_Software.md
├── Standards_and_Specs/
│   ├── Alchemical_Ecosystem_Links_and_Brand.md
│   ├── Alchemical_Style_and_Voice_Guide.md
│   ├── Author_Voice_and_Cadence.md
│   ├── Author_Voice_Cadence_Telemetry_Report.md
│   ├── Author_Voice_Verbatim_Exemplars.md
│   ├── Fasteners_and_Inserts.md
│   ├── Governance_and_Constraint_Architecture.md
│   ├── Image_and_Style_Rules.md
│   ├── Standards_Index.md
│   ├── Verifiable_Accuracy_and_Anti_Hallucination.md
│   └── Workspace_Gmail_MCP_Standard.md
├── Tasks/
│   └── NetCom_Tasks.md
├── Templates/
│   └── Color_Palettes/
│       ├── Alchemical3D_Color_Template.md
│       ├── Alchemical3D_Light_Color_Template.md
│       ├── Gruvbox_Local_Color_Template.md
│       └── NetCom_Corporate_Color_Template.md
├── AGENTS.md
└── README.md
+------------------------------------------------------------+
```

---

## 2. `NetCom` Repository Directory Trees (`1` Indexed)

### [`NetCom_Engineering_Assistant`](../Projects/NetCom_Engineering_Assistant/NetCom_Engineering_Assistant.md) (`software` | `HEAD: UNTRACKED` | `Tree: 9e7492e491a3`)
- **Repository Location**: `/home/orin/Projects/Engineering/NEA_v2.2.3`

```text
+------------------------------------------------------------+
            --- DIRECTORY STRUCTURE ---
+------------------------------------------------------------+

./
├── Copilot_Agents/
│   ├── NEA_BOM_Builder/
│   │   ├── Knowledge/
│   │   │   ├── Behavior_v2.2.3.txt
│   │   │   ├── BOM_Standards_v2.2.3.txt
│   │   │   ├── Formatting_Standards_v2.2.3.txt
│   │   │   ├── Project_BOM_Build_Workflow_v2.2.3.txt
│   │   │   ├── Project_Metadata_Standard_v2.2.3.txt
│   │   │   └── Workbook_Types_v2.2.3.txt
│   │   ├── Agent_Config.md
│   │   └── Instructions.txt
│   ├── NEA_Catalog_Manager/
│   │   ├── Knowledge/
│   │   │   ├── Behavior_v2.2.3.txt
│   │   │   ├── BOM_Standards_v2.2.3.txt
│   │   │   ├── Formatting_Standards_v2.2.3.txt
│   │   │   ├── Material_Catalog_Workflow_v2.2.3.txt
│   │   │   ├── Material_Master_Standards_v2.2.3.txt
│   │   │   ├── NEA_Governance_Register_v2.2.3.txt
│   │   │   └── Workbook_Types_v2.2.3.txt
│   │   ├── Agent_Config.md
│   │   └── Instructions.txt
│   ├── NEA_CRL_Builder/
│   │   ├── Knowledge/
│   │   │   ├── Behavior_v2.2.3.txt
│   │   │   ├── CRL_Build_Workflow_v2.2.3.txt
│   │   │   ├── CRL_Standards_v2.2.3.txt
│   │   │   ├── Formatting_Standards_v2.2.3.txt
│   │   │   ├── Project_Metadata_Standard_v2.2.3.txt
│   │   │   └── Workbook_Types_v2.2.3.txt
│   │   ├── Agent_Config.md
│   │   └── Instructions.txt
│   ├── NEA_Package_Reviewer/
│   │   ├── Knowledge/
│   │   │   ├── Behavior_v2.2.3.txt
│   │   │   ├── Project_Review_Workflow_v2.2.3.txt
│   │   │   ├── Review_Report_Template_v2.2.3.txt
│   │   │   ├── Review_Standards_v2.2.3.txt
│   │   │   └── Workbook_Types_v2.2.3.txt
│   │   ├── Agent_Config.md
│   │   └── Instructions.txt
│   ├── NEA_Repair_Tool/
│   │   ├── Knowledge/
│   │   │   ├── Behavior_v2.2.3.txt
│   │   │   ├── Formatting_Standards_v2.2.3.txt
│   │   │   ├── NEA_Governance_Register_v2.2.3.txt
│   │   │   ├── Project_Metadata_Standard_v2.2.3.txt
│   │   │   ├── Workbook_Repair_Workflow_v2.2.3.txt
│   │   │   └── Workbook_Types_v2.2.3.txt
│   │   ├── Agent_Config.md
│   │   └── Instructions.txt
│   ├── NEA_Timesheet_Consolidator/
│   │   ├── Knowledge/
│   │   │   ├── Behavior_v2.2.3.txt
│   │   │   ├── Formatting_Standards_v2.2.3.txt
│   │   │   ├── Timesheet_Consolidation_Workflow_v2.2.3.txt
│   │   │   ├── Timesheet_Standards_v2.2.3.txt
│   │   │   └── Workbook_Types_v2.2.3.txt
│   │   ├── Agent_Config.md
│   │   └── Instructions.txt
│   └── Agent_Builder_Guide.md
├── Scripts/
│   ├── build_copilot_agents.py
│   ├── inspect_nea_workbooks.py
│   └── package_nea_delivery.py
├── Skills/
│   ├── nea-anti-hallucination/
│   │   ├── scripts/
│   │   │   └── inspect_nea_workbooks.py
│   │   ├── nea-anti-hallucination.zip
│   │   └── SKILL.md
│   ├── nea-verification-and-receipt/
│   │   ├── scripts/
│   │   │   └── inspect_nea_workbooks.py
│   │   ├── nea-verification-and-receipt.zip
│   │   └── SKILL.md
│   ├── nea-workbook-entry-guard/
│   │   ├── scripts/
│   │   │   └── inspect_nea_workbooks.py
│   │   ├── nea-workbook-entry-guard.zip
│   │   └── SKILL.md
│   └── Skills_Deployment_Guide.md
├── Templates/
│   ├── BOM_Materials_Master_Template.xlsx
│   ├── Cable_Running_List_Template.xlsx
│   ├── Project_Cover_Sheet_Template.xlsx
│   └── Timesheet_Template.xlsx
├── CHANGELOG.md
├── NEA_Governance_Register_v2.2.3.md
├── NEA_User_and_DevOps_Manual.md
└── README.md
+------------------------------------------------------------+
```
