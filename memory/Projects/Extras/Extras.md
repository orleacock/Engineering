---
project: "Extras"
entity: "Alchemical-3D"
compartment: "public"
project_type: "hardware"
status: "Active"
local_path: "/home/orin/Projects/Alchemical3D/Extras"
repo_head_sha: "cfef0fdbfcc8"
tree_hash: "40edca68895b"
checkpoint_head_sha: "cfef0fdbfcc8"
checkpoint_tree_hash: "40edca68895b"
checkpoint_worktree: "clean"
task_umbrella: "../../Tasks/Alchemical-3D_Tasks.md"
last_synced: "2026-11-16"
checkpoint_lessons_digest: "0fc39ba437d3d1c0"
---

## 🧭 Homunculus Companion Notes & Project Navigation

| Artifact Role | File Link | Purpose |
| :--- | :--- | :--- |
| **Project Hub (`AUTO-TREE`)** | [`Extras.md`](Extras.md) | Canonical architecture overview, `SESSION-HANDOFF`, `AUTO-TREE`, and `[TBD]` Ledger. |
| **Hardware Telemetry** | [`Extras_Hardware.md`](Extras_Hardware.md) | CAD bounding boxes, cylindrical bore histograms, and firmware pinouts. |
| **Lessons Learned & Post-Mortems** | [`Extras_Lessons_Learned.md`](Extras_Lessons_Learned.md) | Root-cause post-mortems (`Symptom -> Root Cause -> Permanent Guardrail`). |
| **Procedural Playbooks (`PB-xx`)** | [`Extras_Playbooks.md`](Extras_Playbooks.md) | Portable multi-step engineering workflows (`Trigger -> Ordered Procedure -> Verification Gate`). |
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
- **Living Documentation:** `README.md` (`cfef0fd`, `VRF-f451a8fad091`)
- **CAD Files:** `Alch_Cube_20mm_V4.stl`, `Alchemical_20mm_Cube.stl` — Full mesh telemetry in [`Extras_Hardware`](Extras_Hardware.md)
- **Standards Applied:** [`Verifiable_Accuracy_and_Anti_Hallucination`](../../Standards_and_Specs/Verifiable_Accuracy_and_Anti_Hallucination.md), `Author_Voice_and_Cadence`, `Image_and_Style_Rules`, `Subagent_and_Memory_Architecture`

<!-- AUTO-TREE:START -->
```text
Repository: Extras | HEAD SHA: cfef0fdbfcc8 | Tree Hash: 40edca68895b
  Alch_Cube_20mm_V4.stl
  Alchemical_20mm_Cube.stl
  README.md
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

- **Git & Provenance Baseline (`2026-11-16`):** `main:clean` at commit `cfef0fd` (`7c8db38..cfef0fd` pushed to `origin/main`; `audit_repo_docs.py`: `0` issues; `verify_claims.py --fail-on-tbd`: `14/14` supported, `0` unbacked, `VRF-f451a8fad091`; `audit_data_boundary.py`: `BOUNDARY_CLEAN`).
- **`[TBD: calibration_cube_v4_vs_legacy_distinction]`:** Confirm functional/visual difference between `Alch_Cube_20mm_V4.stl` (`4.40 cm³`) and `Alchemical_20mm_Cube.stl` (`4.35 cm³`) when authoring `README.md`.

## 🎯 Active Tasks
*(Transcluded live from `### Extras` in [`Alchemical3D_Tasks`](../../Tasks/Alchemical-3D_Tasks.md))*

> **Active Task Queue**: Tracked in [`Alchemical3D_Tasks`](../../Tasks/Alchemical-3D_Tasks.md#Extras) *(Single-Writer Task Umbrella)*.

## 🚀 Session Handoff & Multi-Session Kickstart (`SESSION-HANDOFF`)
<!-- SESSION-HANDOFF:START -->
- **Last Session Timestamp**: `2026-11-16`
- **Checkpoint Provenance**: `HEAD SHA: cfef0fdbfcc8` | `Tree Hash: 40edca68895b` | `Worktree: clean` | `Last Verification: VRF-f451a8fad091,audit_repo_docs:0-issues,BOUNDARY_CLEAN`
- **Where We Stopped (Verified State & Context)**:
  Committed and pushed Extras README.md (7c8db38..cfef0fd) to origin/main with VRF-f451a8fad091, 0 audit_repo_docs issues, and BOUNDARY_CLEAN
- **Active Project State Ledger & Blockers**: None
- **Next Session Kickstart & Discussion Points**:
  1. Optional: confirm functional/visual distinction between Alch_Cube_20mm_V4.stl and Alchemical_20mm_Cube.stl if desired
<!-- SESSION-HANDOFF:END -->

---

## 🔒 Quarantine Zone (Unverified Notes, Scratch Specs & Open `[TBD]`s)

> [!WARNING]
> **`[QUARANTINED — DO NOT CITE AS FACT]`**: Everything inside this section (and inside [`Quarantine/`](Quarantine/Quarantine_README.md)) is explicitly unverified holding data. Downstream documentation, BOMs, calculations, and `verify_claims.py` must **never** treat items in this section as verified ground truth until empirically verified.

<!-- QUARANTINE-ZONE:START -->
- Active open `[TBD]` items are tracked in the Open `[TBD]` / `[CONFLICT]` Ledger above; place unverified hypotheses here or in [`Quarantine/`](Quarantine/Quarantine_README.md) prior to verification.
<!-- QUARANTINE-ZONE:END -->
