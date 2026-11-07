---
type: diagram-blueprint
blueprint_id: layered_architecture
aliases: [layered-architecture]
status: Active
last_verified: 2026-11-05
---

# 📐 Layered System Architecture Blueprint (`layered_architecture`)

Standardized Homunculus blueprint for **horizontal swimlane/band system architectures**, multi-stage processing pipelines, and firmware/AI orchestration diagrams via `skills/visual-studio/scripts/render_diagram.py`.

Compatible with all registered color palettes (`--palette default_dark`, `--palette default_light`, `--palette gruvbox_dark`, plus any custom palettes in `<memory_root>/Templates/Color_Palettes/`).

---

## 1. When to Use This Archetype
- **Top-to-Bottom Multi-Stage Pipelines**: Input ingestion $\rightarrow$ normalization $\rightarrow$ deterministic engine $\rightarrow$ validation gates $\rightarrow$ output deliverables.
- **Hardware / Firmware / Host Stack Diagrams**: Physical sensors & actuators $\rightarrow$ MCU board (`CAN`/`USB`) $\rightarrow$ Klipper host $\rightarrow$ Web UI (`Mainsail` / `Fluidd`).
- **Subagent & Memory Orchestration Topologies**: User prompt $\rightarrow$ Lead Co-Engineer $\rightarrow$ Parallel Lab Technicians (`memory-scout`, `hardware-inspector`) $\rightarrow$ Single-Writer Memory Commit.

---

## 2. Structural & Anti-Defect Rules (Locked)
1. **Dedicated Inter-Band Routing Channels**: Every horizontal layer band is separated by a minimum `54px` vertical channel (`band_gap: 54`) so inter-layer arrows and their topmost z-ordered label pills never overlap band headers or card text.
2. **Equal-Height Side-by-Side Cards**: Cards inside a single horizontal layer automatically share calculated widths based on `weight` (default `1.0`) and uniform height, with semantic status borders (`primary`, `secondary`, `tertiary`, `pass`, `warn`, `alert`).
3. **4-Layer Z-Order Separation**:
   - `Layer 0`: Canvas & Title Banner
   - `Layer 1`: Horizontal Swimlane Bands & Header Bars
   - `Layer 2`: Inner Cards, Badges, & Typography
   - `Layer 3`: Orthogonal/Direct Connector Polylines (`marker-end` arrowheads)
   - `Layer 4`: Opaque Framed Connector Label Pills (`pill_bg` + `pill_border`)

---

## 3. Declarative JSON Spec Skeleton (`diagram_spec`)

*(Pass this blueprint directly via `--blueprint layered_architecture` or `--spec templates/diagrams/Diagram_Blueprints/Layered_Architecture_Blueprint.md`.)*

```json diagram_spec
{
  "archetype": "layered_architecture",
  "title": "HOMUNCULUS — SUBAGENT & HARDWARE TELEMETRY ARCHITECTURE",
  "subtitle": "Dual-Mode Memory Orchestration | Arc-Accurate B-Rep CAD Parsing | Single-Writer Memory Commits",
  "badge": "ARCHITECTURE v2.0",
  "width": 1600,
  "layers": [
    {
      "id": "layer_1",
      "title": "LAYER 1 — PRIMARY THREAD (LEAD CO-ENGINEER & ARCHITECTURAL SYNTHESIS)",
      "style": "primary",
      "height": 175,
      "cards": [
        {
          "id": "c_user",
          "title": "User Request & Design Intent",
          "badge": "INPUT",
          "style": "primary",
          "weight": 1.0,
          "lines": [
            "• Hardware CAD / BOM / Klipper query or repo task",
            "• Concept locked before execution",
            "• Checks Ecosystem_Index.md first (~80 lines)"
          ]
        },
        {
          "id": "c_lead",
          "title": "Primary Thread (Lead Co-Engineer)",
          "badge": "ORCHESTRATOR",
          "style": "secondary",
          "weight": 1.2,
          "lines": [
            "• Interactive trade-offs & DFM evaluation",
            "• Dispatches pointer briefs (<= 300 token budget)",
            "• Single-Writer commit gate for Project Memory"
          ]
        }
      ]
    },
    {
      "id": "layer_2",
      "title": "LAYER 2 — ISOLATED LAB TECHNICIAN SUBAGENTS & DETERMINISTIC TELEMETRY",
      "style": "secondary",
      "height": 195,
      "cards": [
        {
          "id": "c_scout",
          "title": "memory-scout (research / flash)",
          "badge": "READ-ONLY",
          "style": "tertiary",
          "weight": 1.0,
          "lines": [
            "• Multi-note Memory & Standards cross-reference",
            "• Verifies Fasteners_and_Inserts & Voice rules",
            "• Returns [VERIFIED FACT] & [CONFLICT] tags"
          ]
        },
        {
          "id": "c_inspector",
          "title": "hardware-inspector (self / flash)",
          "badge": "CAD + KLIPPER",
          "style": "primary",
          "weight": 1.2,
          "lines": [
            "• Runs inspect_hardware_ecosystem.py (<1ms cache)",
            "• Arc-accurate STEP B-Rep cylinder & hole axes",
            "• Matches IN_ASSEMBLY_STEP & 3-state Doc Ref"
          ]
        },
        {
          "id": "c_worker",
          "title": "repo-worker (self / flash or pro)",
          "badge": "EXECUTION",
          "style": "pass",
          "weight": 1.0,
          "lines": [
            "• Synchronizes README, BOM, & Assembly_Guide",
            "• Applies format_image.py (#FFFFFF showcase card)",
            "• Runs audit_repo_docs.py verification gate"
          ]
        }
      ]
    },
    {
      "id": "layer_3",
      "title": "LAYER 3 — VERIFIED PERSISTENCE & HEALTH GATES (PROJECT MEMORY + GIT REPOS)",
      "style": "pass",
      "height": 170,
      "cards": [
        {
          "id": "c_manifests",
          "title": "Projects/<Name>/<Name>_Hardware_Manifest.md",
          "badge": "SYNCED CACHE",
          "style": "pass",
          "weight": 1.0,
          "lines": [
            "• Cached bounding boxes, volumes, & M3/M2 bores",
            "• Decoupled latest_cad_mtime vs latest_doc_mtime"
          ]
        },
        {
          "id": "c_gate",
          "title": "sync_memory.py Unified Gate",
          "badge": "EXIT CODE 0",
          "style": "warn",
          "weight": 1.0,
          "lines": [
            "• 0 Broken Links | 0 Orphan Dossiers",
            "• 0 Missing YAML Frontmatter | 0 Boundary Errors"
          ]
        }
      ]
    }
  ],
  "connections": [
    {
      "from_layer": "layer_1",
      "to_layer": "layer_2",
      "x_ratio": 0.50,
      "label": "Pointer Briefs + Model Tiering (flash / pro)",
      "style": "primary"
    },
    {
      "from_layer": "layer_2",
      "to_layer": "layer_3",
      "x_ratio": 0.50,
      "label": "[MEMORY_DELTA] + Verified Telemetry Commit",
      "style": "pass"
    }
  ],
  "footer_left": "Homunculus Visual Diagram Studio • Blueprint: layered_architecture",
  "footer_right": "Generated via render_diagram.py"
}
```
