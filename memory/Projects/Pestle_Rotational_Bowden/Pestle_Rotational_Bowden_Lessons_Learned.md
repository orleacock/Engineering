---
project: "Pestle_Rotational_Bowden"
parent_note: "Pestle_Rotational_Bowden"
entity: "Alchemical-3D"
compartment: "public"
note_type: "lessons_learned"
last_synced: "2026-11-08"
---

# 🧠 Pestle Rotational Bowden — Engineering Lessons Learned & Post-Mortem Ledger (`Pestle_Rotational_Bowden_Lessons_Learned`)

Part of the [`README.md`](../../README.md) and project-scoped troubleshooting ledger for [`Pestle_Rotational_Bowden`](Pestle_Rotational_Bowden.md) and [`Pestle_Rotational_Bowden_Hardware`](Pestle_Rotational_Bowden_Hardware.md).

> [!IMPORTANT]
> **Containment, Failed-Attempt Quarantine & Role Separation**
> 1. **Failed-Attempt Quarantine (`verify_claims.py` Auto-Exclusion):** Automatically excluded (`excluded_lessons_learned_sources`) when scanning `--sources`. Canonical specifications and active `Mode B1` assembly rules live in [`Pestle_Rotational_Bowden`](Pestle_Rotational_Bowden.md) and [`Pestle_Rotational_Bowden_Hardware`](Pestle_Rotational_Bowden_Hardware.md).
> 2. **Role Separation:** Active `Open [TBD]` items are tracked exclusively in [`Pestle_Rotational_Bowden`](Pestle_Rotational_Bowden.md) (`## 🔍 Provenance Status & Open [TBD] / [CONFLICT] Ledger`). This file records **only** historical post-mortems, mechanical fracture root causes, and coupled Bowden trajectory lessons.

---

## 0. Subsystem Design Invariants & Anti-Bloat Matrix (`Sectional Rebuild Reference`)

<!-- SUBSYSTEM-INVARIANTS:START -->
| Subsystem / Assembly | Must-Keep Design Invariants (`Chesterton's Fence`) | Retired Assumptions / Anti-Patterns (`Never Re-Introduce`) | Canonical Source |
| :--- | :--- | :--- | :--- |
| **Bottom-Entry Lever Pivot Insert & Support-Arm Bracing (`pestle_main_body.stl`, `[a]_pestle_lever.stl`)** | Press the lever-pivot `M3x5x4mm` heat-set insert **from the bottom of `pestle_main_body.stl` strictly flush with the bottom face**; brace a wrench flat between support-arm uprights against a table when pressing `(3)` `PC4-M6` fittings; compress the BMG tension spring directly against `[a]_pestle_lever.stl`. | Pressing the lever-pivot insert from the top face (pushes melt ridge into lever swing plane); pressing `PC4-M6` collets unbraced (snaps upright arm along Z layers); prying BMG tension spring against lower main-body ears. | [`Pestle_Rotational_Bowden.md`](Pestle_Rotational_Bowden.md), [`Pestle_Rotational_Bowden_Hardware.md`](Pestle_Rotational_Bowden_Hardware.md) |
| **Swivel Thrust Bearing & Short PTFE Path (`F5-12M`, `< 228.6mm` PTFE)** | Mount `BMG` + `LDO` `NEMA 14` (`36STH20-1004AHG-9T`) on the `F5-12M` 3-piece axial thrust bearing (`5mm ID x 12mm OD x 4mm`) so the extruder swivels straight toward [`Alembic_Toolhead`](../Alembic_Toolhead/Alembic_Toolhead.md) (`< 228.6mm` PTFE, `0.95 mm @ 40 mm/s` retraction, `0.280` PA). | Fixed frame-mounted Bowden exit angles (`~508mm` PTFE compound S-curves) or silently guessing resolutions to the `4` quarantined table-vs-step fastener/bearing discrepancies in `README.md`. | [`Pestle_Rotational_Bowden.md`](Pestle_Rotational_Bowden.md) |
<!-- SUBSYSTEM-INVARIANTS:END -->

---

## 1. Engineering Post-Mortems & Troubleshooting Entries

### `LL-PST-01` [TIER2] — Top-Side Pivot Insert Binding & Cantilevered Support-Arm Shear Fractures
- **Symptom / Failed Approach (`Historical / Rejected`):** Three mechanical failure modes during `Rev 1.2` assembly: (1) pressing the lever-pivot `M3x5x4mm` heat-set insert into `pestle_main_body.stl` from the top face (binding `[a]_pestle_lever.stl` and blocking `BMG` `50T` gear mesh), (2) pressing the `(3)` `PC4-M6` Bowden collets unbraced (snapping the upright support arm along Z layer lines), and (3) prying the BMG tension thumbscrew spring against the lower main-body support ears (snapping the lower ears).
- **Root Cause:** Top-side heat-set entry pushes a melt ridge into the lever swing plane; axial collet press force places the cantilevered upright arm in layer-delaminating bending shear; lower bracket ears are sized for axial pin alignment rather than prying loads.
- **Verified Resolution & Canonical Owner:** Enforced as paramount `Mode B1` hazards in [`Pestle_Rotational_Bowden`](Pestle_Rotational_Bowden.md): press the lever pivot `M3x5x4mm` insert **from the bottom of `pestle_main_body.stl` strictly flush with the bottom face**, brace a wrench flat between the support-arm uprights against a table during `PC4-M6` press-fit, and compress the BMG thumbscrew spring directly against `[a]_pestle_lever.stl`.

### `LL-PST-02` [TIER2] — Monolithic `README.md` Table-to-Step Drift
- **Symptom / Failed Approach (`Historical / Rejected`):** Maintaining the BOM and 12-step assembly guide inside a single monolithic `README.md` without automated cross-checking allowed fastener head-styles (`SHCS` vs. `BHCS`) and insert/bearing counts (`7` vs. `6` heat-sets; `1` `F5-12M` 3-piece thrust bearing vs. Steps `10 & 12`) to drift between the table and steps.
- **Root Cause:** Single-file manual editing prior to deterministic `verify_claims.py` and `audit_repo_docs.py` (Check `#7b` fastener-dodging gate).
- **Verified Resolution & Canonical Owner:** Enforced in `doc-and-card-studio` (`4+1` modular split + Check `#7b`); the `4` unresolved fastener/bearing conflicts are quarantined in [`Pestle_Rotational_Bowden`](Pestle_Rotational_Bowden.md)'s `Open [TBD] Ledger` for resolution during the modular split.

### `LL-PST-03` [TIER2] — Rotational Bowden Pivot vs. Fixed Frame Bowden Capstan Drag (`Alembic_Toolhead` Coupled)
- **Symptom / Failed Approach (`Historical / Rejected`):** Traditional fixed frame-mounted Bowden extruders (`~508mm` PTFE tube) force filament through compound S-curves as the CoreXY toolhead traverses XY, multiplying capstan friction ($e^{\mu \theta}$) and requiring long retractions while loading the toolhead.
- **Root Cause:** Fixed exit angles force tight PTFE bend radii at high X/Y travel extremes.
- **Verified Resolution & Canonical Owner:** Swiveling the `BMG` + `LDO` `NEMA 14` (`36STH20-1004AHG-9T`) on an `F5-12M` axial thrust bearing (`5mm ID x 12mm OD x 4mm`) aims the extruder straight at [`Alembic_Toolhead`](../../Projects/Alembic_Toolhead/Alembic_Toolhead.md), cutting PTFE length by `>50%` (`< 228.6mm`, `0.95 mm @ 40 mm/s` retraction, `0.280` PA; [`Pestle_Rotational_Bowden`](Pestle_Rotational_Bowden.md)).
- **Shared Interface Link:** Coupled with [`Alembic_Toolhead_Lessons_Learned`](../../Projects/Alembic_Toolhead/Alembic_Toolhead_Lessons_Learned.md).
