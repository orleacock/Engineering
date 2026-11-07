---
title: "Column_DataFlow_Blueprint"
type: diagram-blueprint
blueprint_id: column_dataflow
aliases: [column-dataflow]
entity: "shared"
compartment: "public"
last_synced: "2026-11-05"
---

# 📐 Multi-Column Routed Data-Flow Blueprint (`column_dataflow`)

Part of the [`README.md`](../../README.md). Standardized blueprint for **left-to-right multi-column data schemas, relational table lookups, and routed signal/workflow pipelines** via `/home/orin/Projects/Engineering/Homunculus/skills/visual-studio/scripts/render_diagram.py`.

Compatible with all registered color palettes in `Templates/Color_Palettes/`:
- `Alchemical3D_Color_Template` (`--palette alchemical_dark`)
- `Alchemical3D_Light_Color_Template` (`--palette alchemical_light`)
- `Gruvbox_Local_Color_Template` (`--palette gruvbox_dark`)
- `NetCom_Corporate_Color_Template` (`--palette netcom_corporate`)

---

## 1. When to Use This Archetype
- **Relational Workbook & Database Schemas**: Left-to-right data flow across tables with explicit lookup keys (`XLOOKUP`, `SUMIFS`, foreign keys) and dedicated vertical routing channels (e.g., NetCom Engineering Assistant Workbook Data-Flow Diagram).
- **Multi-Stage Compiler / Corpus Processing Pipelines**: Raw input files (`Column 1`) $\rightarrow$ Parser & Normalizer (`Column 2`) $\rightarrow$ Rule/Profile Synthesis (`Column 3`) $\rightarrow$ Target Artifacts (`Column 4`).
- **BOM & CAD Parity Audit Flows**: Onshape `.step`/`.stl` exports $\rightarrow$ `inspect_hardware_ecosystem.py` $\rightarrow$ `Hardware_Manifests/*.md` $\rightarrow$ `BOM.md` & `Assembly_Guide.md`.

---

## 2. Structural & Anti-Defect Rules (Locked)
1. **Dedicated Vertical Routing Channels**: Adjacent columns are separated by a generous `130px–160px` horizontal routing channel so orthogonal step-routed connectors and their label pills sit cleanly in the channel gap without ever crossing over node text.
2. **Anchor Ratio Precision**: Connectors attach to explicit vertical ratios (`from_y_ratio`, `to_y_ratio` in `0.15..0.90`) along the right or left edge of each card, preventing parallel lines from merging on top of one another.
3. **Topmost Z-Order Label Pills**: Every connector label pill is rendered in the final SVG group (`<g id="connector-pills">`) with an opaque background fill (`pill_bg`) and contrasting border (`pill_border`).

---

## 3. Declarative JSON Spec Skeleton (`diagram_spec`)

```json diagram_spec
{
  "archetype": "column_dataflow",
  "title": "ALCHEMICAL-3D — CAD TELEMETRY & DOCUMENTATION PARITY DATA-FLOW",
  "subtitle": "Left-to-Right Pipeline: Onshape CAD Exports → B-Rep Telemetry Parser → Vault Cache → Living Repo Docs",
  "badge": "DATA-FLOW PIPELINE",
  "width": 1680,
  "columns": [
    {
      "id": "col_sources",
      "header": "COLUMN 1: REPOSITORY SOURCES",
      "width": 390,
      "nodes": [
        {
          "id": "n_step",
          "title": "STEP_Files/*.step",
          "badge": "ISO-10303-21",
          "style": "primary",
          "height": 175,
          "lines": [
            "• Multi-body assembly & individual part B-Reps",
            "• Exact CYLINDRICAL_SURFACE radii & axes",
            "• PRODUCT entity part stems (IN_ASSEMBLY_STEP)",
            "• Tracked via latest_cad_mtime"
          ]
        },
        {
          "id": "n_stl",
          "title": "STL_Files/*.stl",
          "badge": "PRINT MESH",
          "style": "secondary",
          "height": 165,
          "lines": [
            "• Binary/ASCII meshes ([a]_*.stl accents)",
            "• Oriented bounding-box & signed mesh volume",
            "• Cross-checked against STEP export parity"
          ]
        },
        {
          "id": "n_cfg",
          "title": "Klipper Firmware (*.cfg)",
          "badge": "MCU PINS",
          "style": "tertiary",
          "height": 145,
          "lines": [
            "• MCU pin assignments (PF7, PF9, CANbus UUID)",
            "• PWM cycle_time, hardware_pwm, & macro G-code"
          ]
        }
      ]
    },
    {
      "id": "col_engine",
      "header": "COLUMN 2: TELEMETRY & AUDIT ENGINE",
      "width": 430,
      "nodes": [
        {
          "id": "n_inspector",
          "title": "inspect_hardware_ecosystem.py",
          "badge": "DETERMINISTIC",
          "style": "primary",
          "height": 240,
          "lines": [
            "• Zero-token regex STEP B-Rep & binary STL parser",
            "• Classifies M2 / M2.5 / M3 heat-set & clearance bores",
            "• Fast ~1ms --check-cache mtime comparison",
            "• 3-State Doc Ref: Yes | Yes (Prose) | Unlisted",
            "• Emits structured JSON + Markdown tables"
          ]
        },
        {
          "id": "n_auditor",
          "title": "audit_repo_docs + sync_memory",
          "badge": "HEALTH GATES",
          "style": "warn",
          "height": 225,
          "lines": [
            "• Verifies every STL/STEP against BOM & Assembly_Guide",
            "• Validates YAML frontmatter & wikilink graph",
            "• Checks skill/rule symlinks & manifest staleness",
            "• Hard gate: Load-Bearing Issues == 0"
          ]
        }
      ]
    },
    {
      "id": "col_outputs",
      "header": "COLUMN 3: VAULT CACHE & LIVING REPOS",
      "width": 410,
      "nodes": [
        {
          "id": "n_manifest",
          "title": "Hardware_Manifests/*.md",
          "badge": "VAULT CACHE",
          "style": "pass",
          "height": 220,
          "lines": [
            "• Instant <300-token subagent lookup table",
            "• Full part dimensions, volumes, & fastener counts",
            "• Eliminates repeated multi-megabyte CAD reads"
          ]
        },
        {
          "id": "n_docs",
          "title": "GitHub Repo Docs (BOM & Guides)",
          "badge": "PUBLIC REPO",
          "style": "pass",
          "height": 245,
          "lines": [
            "• 100% fastener & STL filename parity",
            "• Showcase cards formatted via format_image.py",
            "• Author Voice & Cadence profile enforced"
          ]
        }
      ]
    }
  ],
  "connectors": [
    {
      "from_node": "n_step",
      "to_node": "n_inspector",
      "from_y_ratio": 0.5,
      "to_y_ratio": 0.3,
      "label": "B-Rep & PRODUCT",
      "style": "primary"
    },
    {
      "from_node": "n_stl",
      "to_node": "n_inspector",
      "from_y_ratio": 0.5,
      "to_y_ratio": 0.55,
      "label": "Mesh BBox & Volume",
      "style": "secondary"
    },
    {
      "from_node": "n_cfg",
      "to_node": "n_inspector",
      "from_y_ratio": 0.5,
      "to_y_ratio": 0.8,
      "label": "Pin & Macro Map",
      "style": "tertiary"
    },
    {
      "from_node": "n_inspector",
      "to_node": "n_manifest",
      "from_y_ratio": 0.35,
      "to_y_ratio": 0.5,
      "label": "--sync-manifest",
      "style": "pass"
    },
    {
      "from_node": "n_inspector",
      "to_node": "n_auditor",
      "from_y_ratio": 0.85,
      "to_y_ratio": 0.25,
      "label": "CAD Inventory",
      "style": "warn"
    },
    {
      "from_node": "n_auditor",
      "to_node": "n_docs",
      "from_y_ratio": 0.6,
      "to_y_ratio": 0.5,
      "label": "Verified Parity",
      "style": "pass"
    }
  ],
  "footer_left": "Alchemical-3D Technical Diagram Studio • Blueprint: column_dataflow",
  "footer_right": "Generated via render_diagram.py"
}
```
