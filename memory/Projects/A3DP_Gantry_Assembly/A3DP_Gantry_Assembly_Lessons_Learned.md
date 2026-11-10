---
project: "A3DP_Gantry_Assembly"
parent_note: "A3DP_Gantry_Assembly"
entity: "Alchemical-3D"
compartment: "public"
note_type: "lessons_learned"
last_synced: "2026-11-08"
---

# 🧠 A3DP Gantry Assembly — Engineering Lessons Learned & Post-Mortem Ledger (`A3DP_Gantry_Assembly_Lessons_Learned`)

Part of the [`README.md`](../../README.md) and project-scoped troubleshooting ledger for [`A3DP_Gantry_Assembly`](A3DP_Gantry_Assembly.md).

> [!IMPORTANT]
> **Containment, Failed-Attempt Quarantine & Role Separation**
> 1. **Failed-Attempt Quarantine (`verify_claims.py` Auto-Exclusion):** Automatically excluded (`excluded_lessons_learned_sources`) when scanning `--sources`. Canonical specifications and active `Mode B1` assembly rules live in [`A3DP_Gantry_Assembly`](A3DP_Gantry_Assembly.md) and [`Fasteners_and_Inserts`](../../Standards_and_Specs/Fasteners_and_Inserts.md).
> 2. **Role Separation:** This file records **only** historical post-mortems, stripped-thread/over-tensioning failure modes, and coupled interface root causes without repeating the full `BOM.md` table.

---

## 0. Subsystem Design Invariants & Anti-Bloat Matrix (`Sectional Rebuild Reference`)

<!-- SUBSYSTEM-INVARIANTS:START -->
| Subsystem / Assembly | Must-Keep Design Invariants (`Chesterton's Fence`) | Retired Assumptions / Anti-Patterns (`Never Re-Introduce`) | Canonical Source |
| :--- | :--- | :--- | :--- |
| **CNC Aluminum Plate Torque & Threadlocker (`M3` & `M5`)** | Torque `M3` fasteners in CNC aluminum to `1.0 to 1.5 Nm` with `Loctite 222MS` (Purple) on metal-to-metal threads; torque `M5` fasteners to `3.0 to 4.5 Nm` with `Loctite 243` (Blue) on metal-to-metal threads; keep all anaerobic threadlockers away from printed `ABS`/`ASA`/`PC`. | Tightening `M3`/`M5` screws in 6061 aluminum to steel torque specs; applying blue `Loctite 243` to small `M3` screws; allowing anaerobic threadlocker liquid/vapor near printed thermoplastics. | [`A3DP_Gantry_Assembly.md`](A3DP_Gantry_Assembly.md), [`Fasteners_and_Inserts.md`](../../Standards_and_Specs/Fasteners_and_Inserts.md) |
| **Dual-Shear Idler Stacks & `2GT` Belt Tensioning** | Shim every `(10)` smooth and `(2)` toothed `2GT` `9mm` idler stack (`5mm` bore) with `M5x7x0.3mm` precision shims across the inner race; tension across a `150mm` unsupported span to `110 Hz` (`6mm` belts) or `130–140 Hz` (`9mm` belts). | Clamping idler stacks without `0.3mm` shims (pinching bearing shields); tensioning standard belts or single-shear mounts above `200 Hz`. | [`A3DP_Gantry_Assembly.md`](A3DP_Gantry_Assembly.md) |
<!-- SUBSYSTEM-INVARIANTS:END -->

---

## 1. Engineering Post-Mortems & Troubleshooting Entries

### `LL-GAN-01` [TIER2] — CNC Aluminum Thread Stripping & Anaerobic Threadlocker Stress-Cracking
- **Symptom / Failed Approach (`Historical / Rejected`):** Tightening `M3` or `M5` fasteners into CNC-milled aluminum plates to steel torque specs (stripping internal aluminum threads), using medium-strength blue `Loctite 243` on small `M3` screws (snapping heads on disassembly), or allowing anaerobic threadlocker vapor/liquid to contact printed `ABS`/`ASA`/`PC` retainers.
- **Root Cause:** Fine internal threads in 6061/milled aluminum have lower shear strength than steel nuts, and anaerobic methacrylates chemically attack amorphous thermoplastics (`ABS`, `ASA`, `PC`), causing rapid brittle fracture.
- **Verified Resolution & Canonical Owner:** Enforced in [`Fasteners_and_Inserts`](../../Standards_and_Specs/Fasteners_and_Inserts.md) and [`A3DP_Gantry_Assembly`](A3DP_Gantry_Assembly.md): enforce **`1.0 to 1.5 Nm`** on `M3` (`Loctite 222MS` Purple on metal-to-metal) and **`3.0 to 4.5 Nm`** on `M5` (`Loctite 243` Blue on metal-to-metal), with zero threadlocker near printed polymers.

### `LL-GAN-02` [TIER2] — Unshimmed Dual-Shear Idler Binding & `>200 Hz` Belt Over-Tensioning
- **Symptom / Failed Approach (`Historical / Rejected`):** Clamping `(10)` smooth and `(2)` toothed `2GT` `9mm` idlers (`5mm` bore) between milled aluminum plates without `0.3mm` precision shims (pinching outer bearing shields or leaving axial play), or tensioning standard belts/single-shear mounts above `200 Hz` (bending motor shafts and brinelling `5mm` idler bearings).
- **Root Cause:** Machining + bearing width tolerance stack-up requires selective axial shimming across the inner race; `>200 Hz` span frequencies require both dual-shear pin support and explicitly rated high-tension belts.
- **Verified Resolution & Canonical Owner:** Shim every idler stack with `M5x7x0.3mm` precision shims so inner races clamp solidly while outer idlers spin freely, and tune belt tension across a **`150mm` unsupported span** to **`110 Hz`** (`6mm` belts) or **`130–140 Hz`** (`9mm` belts; [`A3DP_Gantry_Assembly`](A3DP_Gantry_Assembly.md)).

### `LL-GAN-03` [TIER2] — X-Carriage Mount & 9mm Belt Clamp Interface (`Alembic_Toolhead` Coupled)
- **Symptom / Failed Approach (`Historical / Rejected`):** Printing `(2)` `Retaining Clip` or usermod brackets in `PLA`/`PETG` (creeping under belt tension and chamber heat), or assuming `A3DP_Gantry_Assembly` contains the toolhead belt-clamp CAD.
- **Root Cause:** `A3DP_Gantry_Assembly` is a documentation-only repository (CNC plate CAD resides with Rob @ A3DP), while the mating `9mm` belt clamp CAD (`Belt_Clamp_9mm.step`) lives in [`Alembic_Toolhead`](../../Projects/Alembic_Toolhead/Alembic_Toolhead.md).
- **Verified Resolution & Canonical Owner:** Print all retainers in `ABS`, `ASA`, or `PC` ([`A3DP_Gantry_Assembly`](A3DP_Gantry_Assembly.md)).
- **Shared Interface Link:** Coupled with [`Alembic_Toolhead_Lessons_Learned`](../../Projects/Alembic_Toolhead/Alembic_Toolhead_Lessons_Learned.md).
