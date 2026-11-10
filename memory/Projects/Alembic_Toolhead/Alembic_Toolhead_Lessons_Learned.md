---
project: "Alembic_Toolhead"
parent_note: "Alembic_Toolhead"
entity: "Alchemical-3D"
compartment: "public"
note_type: "lessons_learned"
last_synced: "2026-11-08"
---

# 🧠 Alembic Toolhead — Engineering Lessons Learned & Post-Mortem Ledger (`Alembic_Toolhead_Lessons_Learned`)

Part of the [`README.md`](../../README.md) and project-scoped troubleshooting ledger for [`Alembic_Toolhead`](Alembic_Toolhead.md) and [`Alembic_Toolhead_Hardware`](Alembic_Toolhead_Hardware.md).

> [!IMPORTANT]
> **Containment, Failed-Attempt Quarantine & Role Separation**
> 1. **Failed-Attempt Quarantine (`verify_claims.py` Auto-Exclusion):** Automatically excluded (`excluded_lessons_learned_sources`) when scanning `--sources`. Canonical specifications and active `Mode B1` assembly rules live in [`Alembic_Toolhead`](Alembic_Toolhead.md), [`Alembic_Toolhead_Hardware`](Alembic_Toolhead_Hardware.md), and clean `HEAD` (`3ff29ce`) repository files.
> 2. **Role Separation:** Active `Open [TBD]` items are tracked exclusively in [`Alembic_Toolhead`](Alembic_Toolhead.md) (`## 🔍 Provenance Status & Open [TBD] / [CONFLICT] Ledger`). This file records **only** historical post-mortems, rejected design/forming attempts, and coupled physical interface root causes.

---

## 0. Subsystem Design Invariants & Anti-Bloat Matrix (`Sectional Rebuild Reference`)

<!-- SUBSYSTEM-INVARIANTS:START -->
| Subsystem / Assembly | Must-Keep Design Invariants (`Chesterton's Fence`) | Retired Assumptions / Anti-Patterns (`Never Re-Introduce`) | Canonical Source |
| :--- | :--- | :--- | :--- |
| **`5mm OD x 3mm ID` Aluminum Part-Cooling Tubes & Bend Jig (`Bend_Tool_Base.stl`, `Bend_Tool_Lever.stl`)** | Set `5–10mm` initial gap between bend-jig halves; insert `2.8mm` plastic welding rod (`<3mm` mandrel) inside tube before forming; rotate formed tubes `~5°` inward above nozzle plane; snug `M3` cup-point grub screws just to lock rotation. | Pressing bend-jig halves flush together at start of bend (snaps pivot ears); bending tubing hollow (kinks/collapses `3mm ID` bore); over-tightening `M3` grub screws (crushes thin aluminum wall). | [`Alembic_Toolhead.md`](Alembic_Toolhead.md), [`Alembic_Toolhead_Hardware.md`](Alembic_Toolhead_Hardware.md) |
| **Pneumatic Intake & Manifold Sealing (`PC4-M10`, `9x2` O-Rings, `65mm M3 BHCS`)** | Seat upper `9x2` (`23/64 x 5/64"`) O-ring into intake groove prior to threading `PC4-M10`; align central `9x2` O-ring before snugging the `2 × 65mm M3 BHCS` vertical tie-bolts to initial plastic compression. | Over-torquing `65mm M3 BHCS` tie-bolts to metal torque specs (`~1.2 Nm`) to stop air leaks, which cracks printed `ABS`/`ASA` manifold ears and crushes the O-ring seat. | [`Alembic_Toolhead.md`](Alembic_Toolhead.md) |
| **Git Provenance (`HEAD` `3ff29ce` vs. Unstaged Worktree)** | Anchor all BOM and fastener verification strictly on clean `HEAD:BOM.md` (`3ff29ce`) and [`Alembic_Toolhead_Hardware.md`](Alembic_Toolhead_Hardware.md). | Treating unstaged dirty working-tree edits (`DIRTY_GIT_WORKTREE`) as authoritative ground truth when they drop `M3` grub screws, `M3x24mm` fan-baffle bolts, or `M2` BDsensor fasteners. | [`Alembic_Toolhead.md`](Alembic_Toolhead.md) |
<!-- SUBSYSTEM-INVARIANTS:END -->

---

## 1. Engineering Post-Mortems & Troubleshooting Entries

### `LL-ALM-01` [TIER2] — Unstaged `BOM.md` Working-Tree Divergence vs. Committed `HEAD` (`3ff29ce`)
- **Symptom / Failed Approach (`Historical / Quarantined`):** Editing `BOM.md` in the working tree without cross-checking procedural fastener callouts in `Assembly_Guide.md` Step 1 (`Lower_Body` grub-screw tube retention) or CAD bore histograms in [`Alembic_Toolhead_Hardware`](Alembic_Toolhead_Hardware.md) caused the unstaged `BOM.md` to drop required `M3` grub screws, `M3x24mm` fan-baffle bolts, and optional `M2` BDsensor fasteners relative to committed `3ff29ce`.
- **Root Cause:** Unverified pre-framework edit across `8` working-tree files without `git show HEAD:BOM.md` provenance diffing.
- **Verified Resolution & Canonical Owner:** Quarantine dirty working-tree edits (`DIRTY_GIT_WORKTREE`) and anchor strictly on clean `HEAD:BOM.md` (`3ff29ce`) + [`Alembic_Toolhead_Hardware`](Alembic_Toolhead_Hardware.md) until the active `[TBD]` ledger in [`Alembic_Toolhead`](Alembic_Toolhead.md) is reconciled.

### `LL-ALM-02` [TIER2] — `5mm OD x 3mm ID` Aluminum Tube Buckling & Bend-Jig Ear Fracture
- **Symptom / Failed Approach (`Historical / Rejected`):** Starting the tube wrap with `Bend_Tool_Base.stl` and `Bend_Tool_Lever.stl` pressed flush together snapped the printed pivot ears, while bending raw `5mm OD x 3mm ID` thin-wall aluminum tubing hollow caused inward wall collapse at the tight bend radius.
- **Root Cause:** Zero initial spacing loads the printed lever pivot in prying tension instead of rolling shear; thin aluminum tubing requires internal radial support during tight-radius forming, and parallel (unangled) tubes split airflow past either side of the molten bead.
- **Verified Resolution & Canonical Owner:** Enforced in [`Alembic_Toolhead`](Alembic_Toolhead.md) (`Paramount Assembly Hazards`): set `5–10mm` initial spacing between bend jig halves, insert a `2.8mm` plastic welding rod (`<3mm` mandrel) during bending, rotate formed tubes `~5°` inward strictly above the nozzle plane, and snug `M3` cup-point grub screws just to lock rotation without crushing the `3mm ID` bore.

### `LL-ALM-03` [TIER2] — Coupled `6mm OD` Pneumatic Intake & `9x2` O-Ring Manifold Sealing (`Pneuma_Remote_Air` Coupled)
- **Symptom / Failed Approach (`Historical / Rejected`):** Positive-pressure (`>= 70 kPa`) air leaks at the top `PC4-M10` fitting or central manifold split, followed by cracked printed `ABS`/`ASA` manifold ears when builders attempted to cure the leak by over-torquing the two `65mm M3 BHCS` vertical tie-bolts to metal torque specs (`~1.2 Nm`).
- **Root Cause:** Threading `PC4-M10` before seating the upper `9x2` (`23/64 x 5/64"`) O-ring or pinching a misaligned central `9x2` O-ring; over-torquing bolts into printed plastic crushes the O-ring seat rather than sealing it.
- **Verified Resolution & Canonical Owner:** Seat the upper `9x2` O-ring into the intake groove prior to threading `PC4-M10` and verify central `9x2` O-ring alignment before snugging the `65mm M3 BHCS` bolts to initial plastic compression ([`Alembic_Toolhead`](Alembic_Toolhead.md), [`Fasteners_and_Inserts`](../../Standards_and_Specs/Fasteners_and_Inserts.md)).
- **Shared Interface Link:** Coupled with [`Pneuma_Remote_Air_Lessons_Learned`](../../Projects/Pneuma_Remote_Air/Pneuma_Remote_Air_Lessons_Learned.md) and [`A3DP_Gantry_Assembly_Lessons_Learned`](../../Projects/A3DP_Gantry_Assembly/A3DP_Gantry_Assembly_Lessons_Learned.md).
