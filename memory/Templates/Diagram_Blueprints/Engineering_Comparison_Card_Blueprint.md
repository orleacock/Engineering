---
title: "Engineering_Comparison_Card_Blueprint"
type: diagram-blueprint
blueprint_id: comparison_matrix
aliases: [comparison-matrix, engineering_comparison_card]
entity: "shared"
compartment: "public"
last_synced: "2026-11-05"
---

# 📐 Engineering Comparison & Trade-Off Card Blueprint (`comparison_matrix`)

Part of the [`README.md`](../../README.md). Standardized blueprint for **visual side-by-side engineering trade-off cards, benchmark comparisons, and architectural contrast matrices** (e.g., *The Sledgehammer vs. The Scalpel: CPAP vs. Compressed Air*, filament material comparisons, or before/after revisions) via `/home/orin/Projects/Engineering/Homunculus/skills/visual-studio/scripts/render_diagram.py`.

Compatible with all registered color palettes in `Templates/Color_Palettes/`:
- `Alchemical3D_Color_Template` (`--palette alchemical_dark`)
- `Alchemical3D_Light_Color_Template` (`--palette alchemical_light`)
- `Gruvbox_Local_Color_Template` (`--palette gruvbox_dark`)
- `NetCom_Corporate_Color_Template` (`--palette netcom_corporate`)

---

## 1. When to Use This Archetype
- **GitHub `README.md` Philosophy & Architecture Cards**: Visual contrast between conventional approaches and Alchemical-3D's engineered solution (pairs directly with `--github-card` to bake in the `20px` drop-shadow margin and rounded border).
- **Filament & Material Selection Guides (`Print_Settings.md`)**: Side-by-side mechanical, thermal (`HDT`), and creep comparison (e.g., `PLA` vs. `ABS/ASA` vs. `PA6-CF` / `PPA-CF`).
- **Engineering Review Trade-Off Matrices**: Option A vs. Option B architectural decisions with explicit pros, cons, and quantitative metrics.

---

## 2. Structural & Anti-Defect Rules (Locked)
1. **Aligned Metric Rows**: Every comparison column renders aligned horizontal metric rows (`criterion` label + per-option `value` and semantic status indicator `pass` / `warn` / `alert` / `neutral`) so the eye scans horizontally across options without vertical drift.
2. **Bottom Verdict / Engineering Takeaway Banner**: Includes a full-width bottom engineering takeaway box summarizing the load-bearing conclusion.

---

## 3. Declarative JSON Spec Skeleton (`diagram_spec`)

```json diagram_spec
{
  "archetype": "comparison_matrix",
  "title": "THE SLEDGEHAMMER vs. THE SCALPEL — PART COOLING ARCHITECTURE",
  "subtitle": "Why Pneuma + Alembic Replaces Bulky CPAP Hoses with High-Pressure Micro-Umbilical Air Delivery",
  "badge": "ENGINEERING TRADE-OFF",
  "width": 1680,
  "criteria": [
    "Moving Toolhead Mass",
    "Umbilical Hose Diameter",
    "Gantry Whip & Drag at High Accel",
    "Static Pressure Head Loss",
    "Acoustic Noise Profile",
    "Primary Engineering Verdict"
  ],
  "options": [
    {
      "id": "opt_ blowers",
      "title": "On-Toolhead 5015 / 4028 Blowers",
      "subtitle": "Conventional Direct-Mounted Fans",
      "badge": "BASELINE",
      "style": "tertiary",
      "rows": [
        {"value": "High (+75g to +140g directly on X-carriage)", "status": "alert"},
        {"value": "N/A (Extra fan wires in umbilical)", "status": "neutral"},
        {"value": "Low hose drag, but severe pendulum inertia", "status": "warn"},
        {"value": "Stalls against high-restriction nozzle ducts", "status": "alert"},
        {"value": "High-pitched whine (especially 4028 server fans)", "status": "warn"},
        {"value": "Caps input shaper acceleration & ringing limits", "status": "alert"}
      ]
    },
    {
      "id": "opt_cpap",
      "title": "The Sledgehammer: Remote CPAP",
      "subtitle": "High-Volume / Low-Pressure Corrugated Hose",
      "badge": "BRUTE FORCE",
      "style": "warn",
      "rows": [
        {"value": "Low on toolhead (remote blower off-gantry)", "status": "pass"},
        {"value": "15mm – 19mm OD bulky corrugated hose", "status": "alert"},
        {"value": "Severe hose whip, spring torque, & top-hat drag", "status": "alert"},
        {"value": "Low static pressure; requires massive bore throughout", "status": "warn"},
        {"value": "Loud turbine siren unless heavily muffled", "status": "warn"},
        {"value": "Trades toolhead mass for a wrestling match with a hose", "status": "warn"}
      ]
    },
    {
      "id": "opt_pneuma",
      "title": "The Scalpel: Pneuma × Alembic",
      "subtitle": "High-Pressure / Micro-Bore PTFE Delivery",
      "badge": "ALCHEMICAL-3D",
      "style": "primary",
      "rows": [
        {"value": "Ultra-Low (Zero fan mass on Alembic carriage)", "status": "pass"},
        {"value": "6mm OD trunk → Dual 5mm OD PTFE branches", "status": "pass"},
        {"value": "Minimal (tracks naturally alongside standard bowden)", "status": "pass"},
        {"value": "High static pressure drives precision nozzle jets", "status": "pass"},
        {"value": "Isolated stationary pump enclosure off-frame", "status": "pass"},
        {"value": "Maximum acceleration + surgical airflow at the nozzle", "status": "pass"}
      ]
    }
  ],
  "takeaway_title": "LOAD-BEARING DESIGN PRINCIPLE",
  "takeaway_text": "Moving mass on the X-beam is the enemy of high-speed kinematics—but strapping a 19mm corrugated CPAP hose to a miniature gantry just trades inertia for parasitic spring drag. Stepping down a 6mm OD supply line into dual 5mm OD toolhead branches delivers high-velocity cooling right at the melt zone with zero hose whip.",
  "footer_left": "Alchemical-3D Technical Diagram Studio • Blueprint: comparison_matrix",
  "footer_right": "Pneuma_Remote_Air × Alembic_Toolhead"
}
```
