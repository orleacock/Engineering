---
title: "Spatial_Topology_Blueprint"
type: diagram-blueprint
blueprint_id: spatial_topology
aliases: [spatial-topology, system_topology]
entity: "shared"
compartment: "public"
last_synced: "2026-11-05"
---

# 🗺️ Spatial Multi-Zone System Topology Blueprint (`spatial_topology`)

Part of the [`README.md`](../../README.md). Standardized blueprint for **2D multi-zone subsystem container maps** with compact module cards, orthogonal Manhattan bus routing (`solid` execution + `dashed` async/lifecycle links), and automated node/wire collision verification via `/home/orin/Projects/Engineering/Homunculus/skills/visual-studio/scripts/render_diagram.py`.

Compatible with all registered color palettes in `Templates/Color_Palettes/`:
- `Alchemical3D_Color_Template` (`--palette alchemical_dark`)
- `Alchemical3D_Light_Color_Template` (`--palette alchemical_light`)
- `Gruvbox_Local_Color_Template` (`--palette gruvbox_dark`)
- `NetCom_Corporate_Color_Template` (`--palette netcom_corporate`)

---

## 1. When to Use This Archetype
- **Whole-Ecosystem AI / Software System Maps**: Showing how persistent memory corpora, always-on guardrails, session routing, internal subagent/verifier pipelines, sandboxes, and autonomous background hooks interact spatially across a 2D canvas.
- **Multi-Subsystem Hardware & Control Topologies**: Mapping separate physical enclosures, host controllers, telemetry caches, and safety interlocks with explicit orthogonal bus channels.

---

## 2. Structural & Anti-Defect Rules (Locked)
1. **Strict Zone Containment**: Every module node declaring `"zone": "<zone_id>"` is deterministically checked to sit inside its parent container with zero wall overflow.
2. **Minimum Routing Channel Clearance (`>= 150px` for Horizontal Pills)**: Any horizontal gap carrying a connector `label` pill must provide at least `150px`–`180px` between adjacent card edges (or route vertically via `mid_y` / `waypoints` and place `pill_pos` in open corridor space) so pills never overlap card borders.
3. **Automated Collision & Overflow Gates (`--strict`)**: `render_diagram.py --strict` verifies text width/height fit, canvas-bounds safety, zero node-to-node overlaps, zero pill-to-pill overlaps, zero pill-to-card overlaps, and zero connector segments crossing through unrelated node cards.
4. **4-Layer Z-Order Separation**: `Zones & Legend -> Module Cards -> Orthogonal Manhattan Polylines -> Topmost Opaque Label Pills`.
5. **Complete Schema Enum *(Zero `.py` Source Reading Required)***: Valid `"style"` tokens for `legend`, `zones`, `nodes`, and `edges` are `"primary"`, `"secondary"`, `"tertiary"`, `"pass"`, `"warn"`, `"alert"`, `"neutral"`. Valid port sides (`"from_side"`, `"to_side"`) are `"top"`, `"bottom"`, `"left"`, `"right"`; optional routing keys on `edges` are `"mid_x"`, `"mid_y"`, `"waypoints": [[x,y], ...]`, `"pill_pos": [x,y]`, and `"dashed": true`.

---

## 3. Starter Blueprint Specification (`diagram_spec`)

```json diagram_spec
{
  "archetype": "spatial_topology",
  "title": "ALCHEMICAL-3D — SPATIAL MULTI-ZONE SYSTEM TOPOLOGY TEMPLATE",
  "subtitle": "Declarative 2D Zone Containers • Orthogonal Manhattan Bus Routing • Strict Zero-Collision Verification",
  "badge": "SPATIAL TOPOLOGY",
  "width": 1760,
  "height": 980,
  "legend": [
    {"label": "Primary Execution Flow", "style": "primary"},
    {"label": "Always-On Guardrails", "style": "secondary"},
    {"label": "Verified Truth Gate", "style": "pass"},
    {"label": "Async / Lifecycle Trigger", "style": "tertiary", "dashed": true}
  ],
  "zones": [
    {"id": "z_mem", "x": 60, "y": 190, "w": 800, "h": 280, "title": "Memory Corpus", "style": "primary"},
    {"id": "z_rules", "x": 960, "y": 190, "w": 740, "h": 280, "title": "Always-On Guardrails", "style": "secondary"},
    {"id": "z_exec", "x": 320, "y": 560, "w": 1120, "h": 340, "title": "Execution & Verification Pipeline", "style": "pass"}
  ],
  "nodes": [
    {"id": "n_hub", "zone": "z_mem", "x": 90, "y": 255, "w": 290, "h": 110, "style": "primary", "title": "Ecosystem_Index.md", "lines": ["Master Graph Hub", "Active project dossiers"]},
    {"id": "n_quar", "zone": "z_mem", "x": 540, "y": 255, "w": 290, "h": 110, "style": "warn", "dashed": true, "title": "Open [TBD] Ledger", "lines": ["Quarantined zone", "Excluded from whitelist"]},
    {"id": "n_rule", "zone": "z_rules", "x": 1090, "y": 255, "w": 480, "h": 110, "style": "secondary", "title": "co-engineering-partner.md", "lines": ["Root-cause engineering", "State Ledger accounting"]},
    {"id": "n_swarm", "zone": "z_exec", "x": 360, "y": 640, "w": 400, "h": 120, "style": "primary", "title": "subagent-orchestrator", "lines": ["Turn-1 parallel shards", "Anchored Evidence Packets"]},
    {"id": "n_vrf", "zone": "z_exec", "x": 1000, "y": 640, "w": 400, "h": 120, "style": "pass", "title": "verify_claims.py", "lines": ["Closed-world oracle", "VRF-<12hex> SHA-256 receipt"]}
  ],
  "edges": [
    {"from": "n_hub", "from_side": "right", "to": "n_quar", "to_side": "left", "style": "warn", "dashed": true, "label": "quarantined"},
    {"from": "n_hub", "from_side": "bottom", "to": "n_swarm", "to_side": "top", "mid_y": 515, "style": "primary", "label": "pointer brief"},
    {"from": "n_rule", "from_side": "bottom", "to": "n_vrf", "to_side": "top", "mid_y": 515, "style": "secondary", "dashed": true, "label": "governs"},
    {"from": "n_swarm", "from_side": "right", "to": "n_vrf", "to_side": "left", "style": "pass", "label": "--transcript"}
  ]
}
```
