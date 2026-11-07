---
name: visual-studio
description: Use this skill whenever creating, updating, or styling publication-grade SVG engineering diagrams (and opt-in 300 DPI PNG showcase cards), system architectures, relational data-flow maps, hardware MCU pinout/wiring diagrams, pneumatic/fluid routing maps, or side-by-side engineering comparison cards. Dynamically loads expandable color palettes and diagram blueprints from templates/diagrams/ or <memory_root>/Templates/.
---

# Visual Diagram Studio (`visual-studio`)

This skill governs deterministic, zero-collision SVG diagram generation and optional PNG showcase card rendering via [`render_diagram.py`](scripts/render_diagram.py) under **`1. Accuracy & Truth -> 2. Efficiency -> 3. Data Safety -> 4. Speed`**.

---

## 1. Pre-Flight Foundation Checks

1. **Select Diagram Archetype**:
   - `layered_architecture`: Horizontal tier bands with weighted cards and side-channel bypass routing.
   - `column_dataflow`: Left-to-right multi-stage pipeline columns with orthogonal Manhattan connectors.
   - `hardware_pinout_pneumatic`: Hardware stages with left/right port pills (`ports_in` / `ports_out`), intra-stage routing, and engineering callout bar.
   - `comparison_matrix`: Evaluation criteria table with status indicator dots (`pass`, `warn`, `alert`, `neutral`) and takeaway banner.
   - `spatial_topology`: 2D zone containers (`zones`), positioned module cards (`nodes`), and collision-checked Manhattan edges (`edges`).
2. **Verify Source Claims First**:
   - Every port pin, dimension, bus protocol, or quantitative metric inside the diagram JSON spec must trace to an authoritative workspace source (`verifiable-accuracy.md`).
3. **Deferred Rendering Rule**:
   - Batch SVG/PNG diagram rendering at milestone completion (`pre-commit-gate` step `Y`) unless the user explicitly requests a diagram render during the current turn.

---

## 2. Step-Level Verification Gates (`render_diagram.py` CLI)

### Gate 1 — List Available Palettes & Archetype Blueprints
```bash
python3 <HOMUNCULUS_ROOT>/skills/visual-studio/scripts/render_diagram.py --list-palettes
python3 <HOMUNCULUS_ROOT>/skills/visual-studio/scripts/render_diagram.py --list-blueprints
```

### Gate 2 — Render & Validate Zero-Collision SVG (Spec or Built-In Blueprint)
Render the JSON/Markdown specification (or a registered `--blueprint` archetype) into SVG and enforce strict text-fit, node-containment, and Manhattan edge-collision checks:

```bash
python3 <HOMUNCULUS_ROOT>/skills/visual-studio/scripts/render_diagram.py \
  --spec path/to/diagram_spec.json \
  --palette default_dark \
  --output path/to/diagram.svg \
  --strict
```

### Gate 3 — Optional 300 DPI PNG + Showcase Card Export
When a raster PNG or formatted showcase card is requested (requires system `resvg`/`rsvg-convert`/`inkscape` and optional `Pillow` for `--github-card`):

```bash
python3 <HOMUNCULUS_ROOT>/skills/visual-studio/scripts/render_diagram.py \
  --spec path/to/diagram_spec.json \
  --output path/to/diagram.svg \
  --png \
  --github-card
```

---

## 3. Stop & Escalation Conditions

- **`[SCHEMA ERROR]` / `[LAYOUT WARNING]` under `--strict`**: If `render_diagram.py` reports any text overflow (`TEXT OVERFLOW`), node overlap (`overlaps node`), zone overflow (`overflows parent zone`), or wire-through-card collision (`crosses unrelated node`), halt and adjust the JSON spec dimensions/waypoints until warnings reach `0`.
