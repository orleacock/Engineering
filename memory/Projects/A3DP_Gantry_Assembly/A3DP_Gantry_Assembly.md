---
project: "A3DP_Gantry_Assembly"
entity: "Alchemical-3D"
compartment: "public"
project_type: "hardware"
status: "Verified & Complete"
local_path: "/home/orin/Projects/Alchemical3D/A3DP_Gantry_Assembly"
repo_head_sha: "2f33452de3c6"
tree_hash: "26262283bb41"
checkpoint_head_sha: "2f33452de3c6"
checkpoint_tree_hash: "806533999a8d"
checkpoint_worktree: "clean"
task_umbrella: "../../Tasks/Alchemical-3D_Tasks.md"
last_synced: "2026-11-10"
---

## 🧭 Homunculus Companion Notes & Project Navigation

| Artifact Role | File Link | Purpose |
| :--- | :--- | :--- |
| **Project Hub (`AUTO-TREE`)** | [`A3DP_Gantry_Assembly.md`](A3DP_Gantry_Assembly.md) | Canonical architecture overview, `SESSION-HANDOFF`, `AUTO-TREE`, and `[TBD]` Ledger. |
| **Hardware Telemetry** | [`A3DP_Gantry_Assembly_Hardware.md`](A3DP_Gantry_Assembly_Hardware.md) | CAD bounding boxes, cylindrical bore histograms, and firmware pinouts. |
| **Lessons Learned & Post-Mortems** | [`A3DP_Gantry_Assembly_Lessons_Learned.md`](A3DP_Gantry_Assembly_Lessons_Learned.md) | Root-cause post-mortems (`Symptom -> Root Cause -> Permanent Guardrail`). |
| **Unverified Quarantine Zone** | [`Quarantine/Quarantine_README.md`](Quarantine/Quarantine_README.md) | Holding zone for unverified notes (`[QUARANTINED — DO NOT CITE AS FACT]`). |
| **Active Task Umbrella** | [`Alchemical-3D_Tasks.md`](../../Tasks/Alchemical-3D_Tasks.md#A3DP_Gantry_Assembly) | Single-writer task tracker for `Alchemical-3D` (zero duplicate checkboxes in hub). |

---

# ⚙️ A3DP Gantry Assembly (CNC CoreXY Motion System)

Part of the [`README.md`](../../README.md)

## 🔒 Concept & Design Philosophy ("Why")
- **CNC-Milled Structural Rigidity (`README.md:11,28,36-39`, `Resources_and_Acknowledgements.md:6`):** Modular CoreXY gantry system designed by Advanced 3D Printing (Rob @ A3DP) and documented in partnership with Alchemical-3D, replacing creep-prone printed structural corners and motor mounts with CNC-milled aluminum constraint plates.
- **Dual-Shear Idler & High-Tension `9mm` Belt Architecture:** Supports dual-shear `5mm` idler/pin stacks, `MGN12H` linear rails, and front-accessible belt tensioners engineered to sustain high `9mm` `2GT` belt tensions without flexing motor shafts or skewing XY geometry.

## 📍 Repository & File Inventory
- **Local Path:** `/home/orin/Projects/Alchemical3D/A3DP_Gantry_Assembly`
- **GitHub Remote:** `https://github.com/Alchemical-3D/A3DP_Gantry_Assembly`
- **Living Documentation:** `README.md`, `BOM.md`, `Print_Settings.md`, `Assembly_Guide.md`, `Resources_and_Acknowledgements.md`, `LICENSE` *(Docs-only assembly repository; CNC plate CAD resides with A3DP)*
- **Image Assets:** `Images/`
- **Standards Applied:** [`Verifiable_Accuracy_and_Anti_Hallucination`](../../Standards_and_Specs/Verifiable_Accuracy_and_Anti_Hallucination.md), `Author_Voice_and_Cadence`, [`Fasteners_and_Inserts`](../../Standards_and_Specs/Fasteners_and_Inserts.md), `Image_and_Style_Rules`, `Subagent_and_Memory_Architecture`

<!-- AUTO-TREE:START -->
```text
Repository: A3DP_Gantry_Assembly | HEAD SHA: 2f33452de3c6 | Tree Hash: 26262283bb41
  Images/
  Images/formatted_assembly_images/
  Images/formatted_assembly_images/LHS_R_Bearing.png
  Images/formatted_assembly_images/LHS_R_Complete.png
  Images/formatted_assembly_images/LHS_R_Exploded.png
  Images/formatted_assembly_images/LHSF_Bearing.png
  Images/formatted_assembly_images/LHSF_Complete.png
  Images/formatted_assembly_images/LHSF_Exploded_Thin.png
  Images/formatted_assembly_images/RHS_R_Bearing.png
  Images/formatted_assembly_images/RHS_R_Complete.png
  Images/formatted_assembly_images/RHS_R_Exploded.png
  Images/formatted_assembly_images/RHSF_Bearing.png
  Images/formatted_assembly_images/RHSF_Complete.png
  Images/formatted_assembly_images/RHSF_Exploded_Thin.png
  Images/formatted_assembly_images/RHSF_Tension.png
  Images/formatted_assembly_images/XC_CM.png
  Images/formatted_assembly_images/XC_TM.png
  Images/formatted_assembly_images/XY_LHS_Bearing.png
  Images/formatted_assembly_images/XY_LHS_F.png
  Images/formatted_assembly_images/XY_LHS_R.png
  Images/formatted_assembly_images/XY_RHS_Bearing.png
  Images/formatted_assembly_images/XY_RHS_F.png
  Images/formatted_assembly_images/XY_RHS_R.png
  Assembly_Guide.md
  BOM.md
  LICENSE
  Print_Settings.md
  README.md
  Resources_and_Acknowledgements.md
```
<!-- AUTO-TREE:END -->

## ⚠️ Paramount Assembly Hazards & Mechanical "Whys" (`Mode B1` Anchors)
- **Milled Aluminum Thread Torque Ceilings (`Assembly_Guide.md:35-41`, [`Fasteners_and_Inserts`](../../Standards_and_Specs/Fasteners_and_Inserts.md)):** Custom CNC aluminum plates contain fine `M3` and `M5` threads—never exceed **`1.0 to 1.5 Nm`** on `M3` fasteners or **`3.0 to 4.5 Nm`** on `M5` fasteners to prevent stripping plate threads or crushing bearing races.
- **Threadlocker Grade & Plastic Isolation (`Assembly_Guide.md:16-22`):** Use `Loctite 243` (Blue) on `M5` metal-to-metal bolts and `Loctite 222MS` (Purple) on `M3` metal-to-metal bolts; never allow anaerobic threadlocker to touch `ABS`, `ASA`, or `PC` usermod/retainer prints.
- **Idler Stack Precision Shimming (`Assembly_Guide.md:28-32,41`):** Stack `M5x7x0.3mm` precision shims as required by tolerance stack-up so bolts clamp inner bearing races solidly while outer idlers spin freely with zero vertical play or binding.
- **Belt Frequency Targets & Shaft Protection (`Assembly_Guide.md:46-51`):** Over-tensioning bends stepper/servo shafts and destroys idler bearings; target **`110 Hz`** for `6mm` belts and **`130–140 Hz`** for `9mm` belts across a **`150mm` unsupported span** (`>200 Hz` applies only to dual-shear setups with explicitly rated high-tension belts).
- **Build Craftsmanship Principle (`Author_Voice_and_Cadence` `Exemplar 3.1`):** Frame squareness, deburring, rail lubrication, and equal belt path tension directly govern motion quality (`"The machine you are building now will be a reflection of the effort committed..."`).

## 📐 Verified Specs, COTS Hardware & Print Matrix
- **CNC Aluminum Kit (`BOM.md:12-20`):** LHS Front milled parts (Base Plate, Top Plate, Spacer Block, `2` Belt Clamps); RHS Front milled parts (Base Plate, Top Plate, `2` Belt Clamps); LHS & RHS Rear motor milled parts (Motor Base Plate, Motor Top Plate, Spacer Block, `2` Belt Clamps each); `(4)` Tensioner Blocks; XY LHS & RHS Joint Brackets; X Carriage Bracket Set (Carriage Mount, Hotend Mount).
- **Motion, Pins, Shims & Self-Sourced Hardware (`BOM.md:21-38,54-62`):** `(10)` `2GT` `9mm` smooth idlers (`5mm` bore); `(2)` `2GT` `20T` toothed `9mm` idlers (`5mm` bore); `(2)` `2GT` `20T` `9mm` pulleys (`5mm` bore); `(1)` `M3 x 20mm` + `(1)` `M3 x 29mm` hex standoffs; `(4)` `M2.5 x 10mm SHCS`; `(2)` `M4` nylon lock nuts; `(1)` `5mm x 35mm` + `(1)` `5mm x 30mm` shoulder bolts; retaining pins (`3` × `5mm x 37mm`, `1` × `5mm x 28mm`, `4` × `5mm x 22mm`, `2` × `2mm x 10mm` locating pins); `M5` shims (`18` × `M5 x 0.3mm`, `1` × `M5 x 5mm`, `1` × `M5 x 8mm`, `2` × `M5 x 14mm`); `(1)` `MGN12H` X-axis linear rail; `(2)` `NEMA 17` or `A3DP Servo Motor`; `28` `M5` roll-in T-nuts, `6` `M5 x 20mm`, `42` `M3 x 8mm SHCS`, `22` `M5 x 10mm`.
- **Printed Retainers / Usermods (`Print_Settings.md:3,9-17`, `BOM.md:46-48`):** `(2)` `Retaining Clip` printed in `ABS`, `ASA`, or `PC` (`PLA`/`PETG` prohibited due to chamber heat and belt creep) | `0.20mm` layer height | `0.40–0.45mm` extrusion width | `4` minimum walls | `5` top / `5` bottom layers | `40%` infill (`Grid`, `Gyroid`, `Rectilinear`) | `0` supports.

## 🔗 Companion Projects & Kinematic / System Links
- [`Alembic_Toolhead`](../../Projects/Alembic_Toolhead/Alembic_Toolhead.md) — Mounts directly onto the A3DP X-carriage bracket set with `9mm` belt clamps (`Belt_Clamp_9mm.step`).
- [`Pneuma_Remote_Air`](../../Projects/Pneuma_Remote_Air/Pneuma_Remote_Air.md) — Pairs with the lightweight A3DP + Alembic motion stack to maximize acceleration.

## 🔍 Provenance Status & Open [TBD] / [CONFLICT] Ledger
> [!NOTE]
> Figures inside this ledger are quarantined by `verify_claims.py` and are **not** treated as authorized source truth until resolved.

- **Git & Provenance Baseline:** `main:clean` (`audit_repo_docs.py`: `0` load-bearing issues, `0` isolated warnings; `verify_claims.py --fail-on-tbd` receipt `VRF-6cd82426be23`, `145` supported claims across `README.md`, `BOM.md`, `Print_Settings.md`, `Assembly_Guide.md`, and `Resources_and_Acknowledgements.md`).
- **Open Quantitative `[TBD]` / `[CONFLICT]` Items:** `None` (`open_tbd_count: 0` — hardware BOM and torque/belt specs are internally consistent).

## 🎯 Active Tasks
*(Transcluded live from `### A3DP_Gantry_Assembly` in [`Alchemical3D_Tasks`](../../Tasks/Alchemical-3D_Tasks.md))*

> **Active Task Queue**: Tracked in [`Alchemical3D_Tasks`](../../Tasks/Alchemical-3D_Tasks.md#A3DP_Gantry_Assembly) *(Single-Writer Task Umbrella)*.

## 🚀 Session Handoff & Multi-Session Kickstart (`SESSION-HANDOFF`)
<!-- SESSION-HANDOFF:START -->
- **Last Session Timestamp**: `2026-11-05`
- **Checkpoint Provenance**: `HEAD SHA: 2f33452de3c6` | `Tree Hash: 806533999a8d` | `Worktree: ('clean', [])` | `Last Verification: Transplanted from verified Memory v2 baseline`
- **Where We Stopped (Verified State & Context)**:
  - Transplanted `A3DP_Gantry_Assembly` dossier into native Homunculus Dual-Mode Memory (`entity: Alchemical-3D`, `compartment: public`, `project_type: hardware`). All verified specifications, hazards, and open `[TBD]` ledgers preserved verbatim.
- **Active Project State Ledger & Blockers**:
  - See `## 🔍 Provenance Status & Open [TBD] / [CONFLICT] Ledger` above and active tasks in [`Alchemical-3D_Tasks.md`](../../Tasks/Alchemical-3D_Tasks.md).
- **Next Session Kickstart & Discussion Points**:
  1. Run `python3 skills/project-memory/scripts/sync_memory.py --project A3DP_Gantry_Assembly --kickstart` to verify repository provenance.
  2. Review open tasks in [`Alchemical-3D_Tasks.md`](../../Tasks/Alchemical-3D_Tasks.md#A3DP_Gantry_Assembly).
<!-- SESSION-HANDOFF:END -->
