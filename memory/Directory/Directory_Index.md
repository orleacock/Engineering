---
title: "Memory & Workspace Directory Index"
type: "directory-index"
tree_hash: "b415664f0eb6"
last_synced: "2026-11-10"
---

# 🗂️ Engineering Memory — Directory Lookup Hub (`Directory/`)

> **Turn-1 Location Lookup (`Zero Shell Recon`)**: Maintained automatically by `sync_memory.py` (`--sync-trees` / `--sync-visuals` at `pre-commit-gate` Stage X). Agents read [`Directory_Index.md`](Directory_Index.md) or the active entity's `<Entity>_Directory.md` map on Turn 1 to locate standards, templates, dossiers, and repository files without `ls`, `find`, or `os.listdir` probes.

- **Memory Hub**: [`README.md`](../README.md) | **Global Standards**: [`Standards_Index.md`](../Standards_and_Specs/Standards_Index.md)

---

## 1. Shared `<memory_root>/` Directory Structure

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
│   └── Directory_Index.md
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

## 2. Entity-Isolated Directory Trees (`Multi-Customer Firewall`)

> **Containment Rule**: Only open the `<Entity>_Directory.md` file matching the active task's `entity:` scope.

| Entity Scope | Compartment | Projects Indexed | Entity Directory Map | Task Umbrella |
| :--- | :--- | :---: | :--- | :--- |
| `Alchemical-3D` | `cleanroom` | `10` | [`Alchemical-3D_Directory.md`](Alchemical-3D_Directory.md) | [`Alchemical-3D_Tasks.md`](../Tasks/Alchemical-3D_Tasks.md) |
| `NetCom` | `private` | `1` | [`NetCom_Directory.md`](NetCom_Directory.md) | [`NetCom_Tasks.md`](../Tasks/NetCom_Tasks.md) |
| `Orin_Workstation` | `private` | `1` | [`Orin_Workstation_Directory.md`](Orin_Workstation_Directory.md) | [`Orin_Workstation_Tasks.md`](../Tasks/Orin_Workstation_Tasks.md) |
