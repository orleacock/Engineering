---
type: diagram-blueprint
blueprint_id: comparison_matrix
aliases: [comparison-matrix, engineering_comparison_card]
status: Active
last_verified: 2026-11-05
---

# 📐 Engineering Comparison & Trade-Off Card Blueprint (`comparison_matrix`)

Standardized Homunculus blueprint for **visual side-by-side engineering trade-off cards, benchmark comparisons, and architectural contrast matrices** via `skills/visual-studio/scripts/render_diagram.py`.

Compatible with all registered color palettes (`--palette default_dark`, `--palette default_light`, `--palette gruvbox_dark`, plus any custom palettes in `<memory_root>/Templates/Color_Palettes/`).

---

## 1. When to Use This Archetype
- **GitHub `README.md` Philosophy & Architecture Cards**: Visual contrast between conventional approaches and an engineered solution (pairs directly with `--github-card` to bake in the `20px` drop-shadow margin and rounded border).
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
  "subtitle": "Why High-Pressure Micro-Umbilical Air Delivery Replaces Bulky Corrugated CPAP Hoses",
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
      "id": "opt_blowers",
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
      "id": "opt_micro_ptfe",
      "title": "The Scalpel: Micro-Bore PTFE Delivery",
      "subtitle": "High-Pressure / 6mm-to-5mm OD Manifold",
      "badge": "ENGINEERED",
      "style": "primary",
      "rows": [
        {"value": "Ultra-Low (Zero fan mass on toolhead carriage)", "status": "pass"},
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
  "footer_left": "Homunculus Visual Diagram Studio • Blueprint: comparison_matrix",
  "footer_right": "Generated via render_diagram.py"
}
```
