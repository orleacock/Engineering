---
project: "Extras"
entity: "Alchemical-3D"
compartment: "public"
project_type: "hardware"
status: "Active"
local_path: "/home/orin/Projects/Alchemical3D/Extras"
repo_head_sha: "7c8db38eca18"
tree_hash: "c5c41f218eb3"
checkpoint_head_sha: "7c8db38eca18"
checkpoint_tree_hash: "c5c41f218eb3"
checkpoint_worktree: "clean"
task_umbrella: "../../Tasks/Alchemical-3D_Tasks.md"
last_synced: "2026-11-06"
---

## 🧭 Homunculus Companion Notes & Project Navigation

| Artifact Role | File Link | Purpose |
| :--- | :--- | :--- |
| **Project Hub (`AUTO-TREE`)** | [`Extras.md`](Extras.md) | Canonical architecture overview, `SESSION-HANDOFF`, `AUTO-TREE`, and `[TBD]` Ledger. |
| **Hardware Telemetry** | [`Extras_Hardware.md`](Extras_Hardware.md) | CAD bounding boxes, cylindrical bore histograms, and firmware pinouts. |
| **Lessons Learned & Post-Mortems** | [`Extras_Lessons_Learned.md`](Extras_Lessons_Learned.md) | Root-cause post-mortems (`Symptom -> Root Cause -> Permanent Guardrail`). |
| **Unverified Quarantine Zone** | [`Quarantine/Quarantine_README.md`](Quarantine/Quarantine_README.md) | Holding zone for unverified notes (`[QUARANTINED — DO NOT CITE AS FACT]`). |
| **Active Task Umbrella** | [`Alchemical-3D_Tasks.md`](../../Tasks/Alchemical-3D_Tasks.md#Extras) | Single-writer task tracker for `Alchemical-3D` (zero duplicate checkboxes in hub). |

---

# 🧊 Extras (Dimensional Calibration Prints & Jigs)

Part of the [`README.md`](../../README.md) • CAD Telemetry: [`Extras_Hardware`](Extras_Hardware.md)

## 🔒 Concept & Design Philosophy ("Why")
- **Pre-Build Dimensional Shrinkage Gate:** Houses standardized `20.00 × 20.00 × 20.00 mm` calibration cubes so builders dial XY/Z polymer shrinkage (`ABS`, `ASA`, `PC`) and extrusion flow *before* committing filament and time to tight-clearance bearing seats, O-ring grooves, and `M3x5x4mm` heat-set bores across Alchemical-3D hardware builds.

## 📍 Repository & File Inventory
- **Local Path:** `/home/orin/Projects/Alchemical3D/Extras`
- **GitHub Remote:** `https://github.com/Alchemical-3D/Extras`
- **Living Documentation:** *None yet* (`README.md` not yet created)
- **CAD Files:** `Alch_Cube_20mm_V4.stl`, `Alchemical_20mm_Cube.stl` — Full mesh telemetry in [`Extras_Hardware`](Extras_Hardware.md)
- **Standards Applied:** [`Verifiable_Accuracy_and_Anti_Hallucination`](../../Standards_and_Specs/Verifiable_Accuracy_and_Anti_Hallucination.md), `Author_Voice_and_Cadence`, `Image_and_Style_Rules`, `Subagent_and_Memory_Architecture`

<!-- AUTO-TREE:START -->
```text
Repository: Extras | HEAD SHA: 7c8db38eca18 | Tree Hash: c5c41f218eb3
  Alch_Cube_20mm_V4.stl
  Alchemical_20mm_Cube.stl
```
<!-- AUTO-TREE:END -->

## 📐 Verified Specs, COTS Hardware & Print Matrix
- **CAD Telemetry ([`Extras_Hardware`](Extras_Hardware.md)):** `0` STEP files | `2` STL meshes (`STL_ONLY`) | Total closed-mesh geometric volume `8.75 cm³`:
  - `Alch_Cube_20mm_V4.stl`: Exact envelope `20.00 × 20.00 × 20.00 mm` | Solid volume `4.40 cm³` | `8,476` triangles.
  - `Alchemical_20mm_Cube.stl`: Exact envelope `20.00 × 20.00 × 20.00 mm` | Solid volume `4.35 cm³` | `14,036` triangles.

## 🔗 Companion Projects & Kinematic / System Links
- [`Maker-Tools`](../../Projects/Maker-Tools/Maker-Tools.md) — Paired with polymer shrinkage and tuning workflows.
- [`Alembic_Toolhead`](../../Projects/Alembic_Toolhead/Alembic_Toolhead.md), [`Pneuma_Remote_Air`](../../Projects/Pneuma_Remote_Air/Pneuma_Remote_Air.md), [`A3DP_Gantry_Assembly`](../../Projects/A3DP_Gantry_Assembly/A3DP_Gantry_Assembly.md), [`Pestle_Rotational_Bowden`](../../Projects/Pestle_Rotational_Bowden/Pestle_Rotational_Bowden.md) — Referenced in `Print_Settings.md` pre-print verification.

## 🔍 Provenance Status & Open [TBD] / [CONFLICT] Ledger
> [!NOTE]
> Figures inside this ledger are quarantined by `verify_claims.py` and are **not** treated as authorized source truth until resolved.

- **Git & Provenance Baseline:** `main:clean` (`Extras_Hardware.md` `SYNCED`; both STLs flagged `Doc Ref: Unlisted` because repository root currently has no `README.md`).
- **`[TBD: calibration_cube_v4_vs_legacy_distinction]`:** Confirm functional/visual difference between `Alch_Cube_20mm_V4.stl` (`4.40 cm³`) and `Alchemical_20mm_Cube.stl` (`4.35 cm³`) when authoring `README.md`.

## 🎯 Active Tasks
*(Transcluded live from `### Extras` in [`Alchemical3D_Tasks`](../../Tasks/Alchemical-3D_Tasks.md))*

> **Active Task Queue**: Tracked in [`Alchemical3D_Tasks`](../../Tasks/Alchemical-3D_Tasks.md#Extras) *(Single-Writer Task Umbrella)*.

## 🚀 Session Handoff & Multi-Session Kickstart (`SESSION-HANDOFF`)
<!-- SESSION-HANDOFF:START -->
- **Last Session Timestamp**: `2026-11-05`
- **Checkpoint Provenance**: `HEAD SHA: 7c8db38eca18` | `Tree Hash: c5c41f218eb3` | `Worktree: ('clean', [])` | `Last Verification: Transplanted from verified Memory v2 baseline`
- **Where We Stopped (Verified State & Context)**:
  - Transplanted `Extras` dossier into native Homunculus Dual-Mode Memory (`entity: Alchemical-3D`, `compartment: public`, `project_type: hardware`). All verified specifications, hazards, and open `[TBD]` ledgers preserved verbatim.
- **Active Project State Ledger & Blockers**:
  - See `## 🔍 Provenance Status & Open [TBD] / [CONFLICT] Ledger` above and active tasks in [`Alchemical-3D_Tasks.md`](../../Tasks/Alchemical-3D_Tasks.md).
- **Next Session Kickstart & Discussion Points**:
  1. Run `python3 skills/project-memory/scripts/sync_memory.py --project Extras --kickstart` to verify repository provenance.
  2. Review open tasks in [`Alchemical-3D_Tasks.md`](../../Tasks/Alchemical-3D_Tasks.md#Extras).
<!-- SESSION-HANDOFF:END -->
