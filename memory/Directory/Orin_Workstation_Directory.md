---
title: "Orin_Workstation — Memory & Repository Directory Tree"
entity: "Orin_Workstation"
compartment: "private"
type: "entity-directory"
tree_hash: "8ad39a1c231e"
last_synced: "2026-11-10"
---

# 🗂️ `Orin_Workstation` — Directory Lookup Map (`entity: Orin_Workstation`)

> **Turn-1 Cold-Start Location Map (`pre-commit-gate` Stage X)**: Read this note on Turn 1 to resolve exact file paths across `<memory_root>/` and `Orin_Workstation` repositories without running `ls`, `find`, or `os.listdir` probes. Cross-entity repositories outside `Orin_Workstation` are strictly excluded (`CROSS_ENTITY_CONTAMINATION` firewall).

- **Directory Index**: [`Directory_Index.md`](Directory_Index.md) | **Task Umbrella**: [`Orin_Workstation_Tasks.md`](../Tasks/Orin_Workstation_Tasks.md)

---

## 1. `Orin_Workstation` Memory Dossiers, Standards & Templates (`<memory_root>/`)

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
│   ├── Orin_Workstation_Decision_Router.md
│   ├── Orin_Workstation_Directory.md
│   └── Orin_Workstation_memory_index.json
├── Profile/
│   └── Decision_Profile.md
├── Projects/
│   └── Workstation_Operations/
│       ├── Quarantine/
│       │   └── Quarantine_README.md
│       ├── Templates/
│       ├── Workstation_Operations.md
│       ├── Workstation_Operations_Lessons_Learned.md
│       └── Workstation_Operations_Software.md
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
│   └── Orin_Workstation_Tasks.md
├── Templates/
│   ├── Color_Palettes/
│   │   ├── Alchemical3D_Color_Template.md
│   │   ├── Alchemical3D_Light_Color_Template.md
│   │   ├── Gruvbox_Local_Color_Template.md
│   │   └── NetCom_Corporate_Color_Template.md
│   ├── Diagram_Blueprints/
│   │   ├── Column_DataFlow_Blueprint.md
│   │   ├── Engineering_Comparison_Card_Blueprint.md
│   │   ├── Hardware_Pinout_and_Pneumatic_Blueprint.md
│   │   ├── Layered_Architecture_Blueprint.md
│   │   └── Spatial_Topology_Blueprint.md
│   ├── AGENTS.md
│   ├── Decision_Profile.md
│   ├── Global_Standards_Index.md
│   ├── Memory_Map_README.md
│   ├── Project_Hardware.md
│   ├── Project_Hub.md
│   ├── Project_Lessons_Learned.md
│   ├── Project_Playbooks.md
│   ├── Project_Software.md
│   ├── Quarantine_Note.md
│   ├── Stateful_Sprint_Planning_Template.md
│   └── Task_Umbrella.md
├── AGENTS.md
└── README.md
+------------------------------------------------------------+
```

---

## 2. `Orin_Workstation` Repository Directory Trees (`1` Indexed)

### [`Workstation_Operations`](../Projects/Workstation_Operations/Workstation_Operations.md) (`software` | `HEAD: UNTRACKED` | `Tree: ee94ee20ba3d`)
- **Repository Location**: `../scripts`

```text
+------------------------------------------------------------+
            --- DIRECTORY STRUCTURE ---
+------------------------------------------------------------+

./
├── gmail_mcp/
│   ├── gmail-workspace-assistant/
│   │   └── SKILL.md
│   ├── gmail_mcp_server.py
│   ├── README.md
│   └── requirements.txt
├── umbrella_configs/
│   └── Projects.homunculus.json
├── benchmark_history.jsonl
├── benchmark_homunculus.py
├── bootstrap_workstation.sh
├── git_pre_commit_boundary.sh
├── homunculus_version.json
├── pre_push_engineering_guard.sh
├── snapshot_homunculus_version.py
└── version_manager.py
+------------------------------------------------------------+
```
