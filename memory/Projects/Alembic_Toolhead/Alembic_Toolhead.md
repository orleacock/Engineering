---
project: "Alembic_Toolhead"
entity: "Alchemical-3D"
compartment: "public"
project_type: "hardware"
status: "Alpha"
local_path: "/home/orin/Projects/Alchemical3D/Alembic_Toolhead"
repo_head_sha: "43ead679c0b0"
tree_hash: "13b0feafb257"
checkpoint_head_sha: "43ead679c0b0"
checkpoint_tree_hash: "13b0feafb257"
checkpoint_worktree: "clean"
task_umbrella: "../../Tasks/Alchemical-3D_Tasks.md"
last_synced: "2026-11-16"
checkpoint_lessons_digest: "b93136db87a387ee"
---

## 🧭 Homunculus Companion Notes & Project Navigation

| Artifact Role | File Link | Purpose |
| :--- | :--- | :--- |
| **Project Hub (`AUTO-TREE`)** | [`Alembic_Toolhead.md`](Alembic_Toolhead.md) | Canonical architecture overview, `SESSION-HANDOFF`, `AUTO-TREE`, and `[TBD]` Ledger. |
| **Hardware Telemetry** | [`Alembic_Toolhead_Hardware.md`](Alembic_Toolhead_Hardware.md) | CAD bounding boxes, cylindrical bore histograms, and firmware pinouts. |
| **Lessons Learned & Post-Mortems** | [`Alembic_Toolhead_Lessons_Learned.md`](Alembic_Toolhead_Lessons_Learned.md) | Root-cause post-mortems (`Symptom -> Root Cause -> Permanent Guardrail`). |
| **Unverified Quarantine Zone** | [`Quarantine/Quarantine_README.md`](Quarantine/Quarantine_README.md) | Holding zone for unverified notes (`[QUARANTINED — DO NOT CITE AS FACT]`). |
| **Active Task Umbrella** | [`Alchemical-3D_Tasks.md`](../../Tasks/Alchemical-3D_Tasks.md#Alembic_Toolhead) | Single-writer task tracker for `Alchemical-3D` (zero duplicate checkboxes in hub). |

---

# 🧪 Alembic Toolhead (`V201` Alpha)

Part of the [`README.md`](../../README.md) • CAD Telemetry: [`Alembic_Toolhead_Hardware`](Alembic_Toolhead_Hardware.md)

## 🔒 Concept & Design Philosophy ("Why")
- **Eliminating Moving Blower Mass (`HEAD:README.md`):** Replaces bulky toolhead-mounted `4010` or `5015` part-cooling fans entirely with remote compressed air supplied via [`Pneuma_Remote_Air`](../../Projects/Pneuma_Remote_Air/Pneuma_Remote_Air.md) through a `6mm OD x 4mm ID` umbilical (`HEAD:BOM.md`).
- **Targeted Boundary-Layer Cooling & Nozzle Visibility:** Routes pressurized air through twin formed `5mm OD x 3mm ID` aluminum tubes aimed directly beneath the nozzle tip, stripping moving mass for high-acceleration CoreXY motion while leaving nozzle visibility completely unobstructed (`HEAD:README.md`, `HEAD:Assembly_Guide.md`).
- **Structural Tube Integration:** Integrates the formed `5mm OD` aluminum tubes directly into the carriage structure alongside milled aluminum carriage/extruder plates (`HEAD:README.md`, `HEAD:Assembly_Guide.md`).

## 📍 Repository & File Inventory
- **Local Path:** `/home/orin/Projects/Alchemical3D/Alembic_Toolhead`
- **GitHub Remote:** `https://github.com/Alchemical-3D/Alembic_Toolhead`
- **Living Documentation:** `README.md`, `BOM.md`, `Print_Settings.md`, `Assembly_Guide.md`, `ALPHA_&_DIRECTION.md`, `LICENSE.md` *(Note: working tree currently has `8` uncommitted modified files vs. clean `HEAD` `3ff29ce`)*
- **CAD & Image Directories:** `STL_Files/` (`14` STLs), `STEP_Files/` (`20` `Alembic_Toolhead_V201` STEPs), `Images/full_images/`, `Images/formatted_assembly_images/` — Full geometry & bore telemetry in [`Alembic_Toolhead_Hardware`](Alembic_Toolhead_Hardware.md) *(No local `Firmware/` folder; cooling macros live in [`Pneuma_Remote_Air`](../../Projects/Pneuma_Remote_Air/Pneuma_Remote_Air.md) `Firmware/Pneuma_Control.cfg`)*
- **Standards Applied:** [`Verifiable_Accuracy_and_Anti_Hallucination`](../../Standards_and_Specs/Verifiable_Accuracy_and_Anti_Hallucination.md), `Author_Voice_and_Cadence`, [`Fasteners_and_Inserts`](../../Standards_and_Specs/Fasteners_and_Inserts.md), `Image_and_Style_Rules`, `Subagent_and_Memory_Architecture`

<!-- AUTO-TREE:START -->
```text
Repository: Alembic_Toolhead | HEAD SHA: 43ead679c0b0 | Tree Hash: 13b0feafb257
  Images/
  Images/formatted_assembly_images/
  Images/formatted_assembly_images/bend_tool_combined.png
  Images/formatted_assembly_images/chianflex_clamp_assembly.png
  Images/formatted_assembly_images/fan_baffle.png
  Images/formatted_assembly_images/fan_mount.png
  Images/formatted_assembly_images/heatset_intake.png
  Images/formatted_assembly_images/heatset_strain_relief.png
  Images/formatted_assembly_images/main_body_grub.png
  Images/formatted_assembly_images/mount.png
  Images/formatted_assembly_images/o_ring.png
  Images/formatted_assembly_images/optional_bdsensor_mount.png
  Images/formatted_assembly_images/strain_relief.png
  Images/formatted_assembly_images/tube_insertion.png
  Images/formatted_assembly_images/vertical_assembly.png
  Images/full_images/
  Images/full_images/alembic_angle_down.png
  Images/full_images/alembic_angle_up.png
  Images/full_images/alembic_face.png
  Images/tool_images/
  Images/tool_images/tool_pipe_bend.png
  Images/tool_images/tool_pipe_bend_5mm_space_example.png
  STEP_Files/
  STEP_Files/Alembic_Toolhead_V201 - 5mmODX3mmID_Alu_Tube.step
  STEP_Files/Alembic_Toolhead_V201 - BD_Mod_Clamp.step
  STEP_Files/Alembic_Toolhead_V201 - Belt_Clamp_9mm.step
  STEP_Files/Alembic_Toolhead_V201 - Chainflex_Clamp_Base.step
  STEP_Files/Alembic_Toolhead_V201 - Chainflex_Clamp_Main.step
  STEP_Files/Alembic_Toolhead_V201 - Fan_Baffle_Takoto.step
  STEP_Files/Alembic_Toolhead_V201 - Intake_6mmOD.step
  STEP_Files/Alembic_Toolhead_V201 - Lower_Body.step
  STEP_Files/Alembic_Toolhead_V201 - Manifold_Frame.step
  STEP_Files/Alembic_Toolhead_V201 - NEMA14_.step
  STEP_Files/Alembic_Toolhead_V201 - PC4-M10 Bowden Pass-Through.step
  STEP_Files/Alembic_Toolhead_V201 - Pnuematic_Fitting_6mmOD.step
  STEP_Files/Alembic_Toolhead_V201 - Pnuematic_Strain_Relief.step
  STEP_Files/Alembic_Toolhead_V201 - Sensor_Retainer.step
  STEP_Files/Alembic_Toolhead_V201 - Shim_06mm_BDsensor.step
  STEP_Files/Bend_Tool_Lever.step
  STEP_Files/Fan_Baffle_Dragon.step
  STEP_Files/Part Studio 1 - Bend_Tool_Base.step
  STEP_Files/Sensor_Retainer_Dragon-MZE.step
  STEP_Files/Shim_56_BDsensor_Dragon-MZE.step
  STL_Files/
  STL_Files/BD_Mod_Clamp.stl
  STL_Files/Bend_Tool_Base.stl
  STL_Files/Bend_Tool_Lever.stl
  STL_Files/Chainflex_Clamp_Base.stl
  STL_Files/Chainflex_Clamp_Main.stl
  STL_Files/Fan_Baffle_Dragon.stl
  STL_Files/Fan_Baffle_Takoto.stl
  STL_Files/Lower_Body.stl
  STL_Files/Manifold_Frame.stl
  STL_Files/Pnuematic_Strain_Relief.stl
  STL_Files/Sensor_Retainer.stl
  STL_Files/Sensor_Retainer_Dragon-MZE.stl
  STL_Files/Shim_06mm_BDsensor.stl
  STL_Files/Shim_56_BDsensor_Dragon-MZE.stl
  ALPHA_&_DIRECTION.md
  Assembly_Guide.md
  BOM.md
  LICENSE.md
  Print_Settings.md
  README.md
```
<!-- AUTO-TREE:END -->

## ⚠️ Paramount Assembly Hazards & Mechanical "Whys" (`Mode B1` Anchors)
- **Aluminum (`~1.2 Nm`) vs. Printed Plastic Torque Split (`HEAD:Assembly_Guide.md`):** Milled aluminum carriage, `A3DP FXD` extruder, and hotend mounting plate accept `~1.2 Nm` (`10.6 in-lbs`), whereas all 3D-printed parts **must not** be overtightened—stop turning immediately once plastic begins compressing to avoid crushing pneumatic O-ring seats or cracking layers.
- **Anaerobic Threadlocker Chemical Hazard ([`Fasteners_and_Inserts`](../../Standards_and_Specs/Fasteners_and_Inserts.md)):** Never allow liquid or vapor threadlocker (`Loctite 222MS` / `Loctite 243`) to contact `ABS`, `ASA`, or `PC` printed parts; it causes rapid chemical stress-cracking.
- **Tube Bending Spacing & Internal Mandrel (`Assembly_Guide.md`):** Maintain `5–10mm` initial spacing between `Bend_Tool_Base.stl` and `Bend_Tool_Lever.stl` to prevent jig fracture and let the `5mm OD x 3mm ID` tube wrap cleanly; insert a `2.8mm` plastic welding rod or `2.85mm` filament (`<3mm` mandrel) if needed to prevent wall collapse, and compute bend start offset as `(distance from Lower_Body tube passthrough to heatblock edge) / 2`.
- **Pneumatic `9x2` O-Ring Seal Alignment (`Assembly_Guide.md`):** Seat the first `9x2` O-ring into the intake groove *before* threading the `PC4-M10` fitting, and align the second `9x2` O-ring between `Intake` and `Manifold_Frame` prior to vertical tie-down (`2 × 65mm M3 SHCS`) so compressed air cannot leak.
- **`5°` Tube Toe-In vs. Nozzle Bed-Crash Clearance (`HEAD:Assembly_Guide.md`):** Rotate aluminum tubes `~5°` inward so the airflow vertex converges directly beneath the nozzle tip while keeping tube ends strictly above the nozzle face plane to prevent part/frame strikes.
- **Grub-Screw Tube Clamping (`HEAD:Assembly_Guide.md`):** Snug `M3` grub screws in `Lower_Body` just enough to lock tube rotation without crushing the `3mm ID` aluminum bore.

## 📐 Verified Specs, COTS Hardware & Print Matrix
- **CAD Telemetry ([`Alembic_Toolhead_Hardware`](Alembic_Toolhead_Hardware.md)):** `20` STEP files | `14` STL meshes (all `14` STLs `MATCH (<=0.2mm)` STEP↔STL parity) | Total closed-mesh geometric volume `105.74 cm³`. Dedicated hotend fan baffles for `Takoto` (`Fan_Baffle_Takoto.stl`) and `Dragon` (`Fan_Baffle_Dragon.stl`), plus `Dragon-MZE` BDsensor retainer/shim (`Sensor_Retainer_Dragon-MZE.stl`, `Shim_56_BDsensor_Dragon-MZE.stl`, `3.60mm` thick vs. `Shim_06mm_BDsensor.stl` `0.60mm`).
- **Reconciled Fasteners & Seals (`BOM.md` & `Assembly_Guide.md`, `2026-11-16`):**
  - `~4` `M3x5x4mm` brass heat-set inserts (`2` in `Intake` + `2` in `Pnuematic_Strain_Relief.stl`, `4` total; `Lower_Body` `Ø5.00mm`×4 and `Pnuematic_Strain_Relief` `Ø4.70mm`×4 bores in CAD)
  - `~2` `M3 x 65mm SHCS` vertical tie-bolts through `Lower_Body` → `Manifold_Frame` → `Intake` (`Fig. 8`)
  - `~8` `M3 x 8mm SHCS` general assembly screws (`4` for carriage mount—`2` front + `2` rear sides—and `2` for `Chainflex` umbilical clamp, plus spares)
  - `~2` `M3 x 20mm` strain-relief screws (`Fig. 4`), `~2` `M3 x 24mm BHCS` front fan-baffle/manifold screws (`Fig. 11`), `~2` `M3 x 0.5 x 4mm` cup-point grub screws (`Fig. 7`)
  - `2` `9x2` (`23/64 x 5/64"`) O-rings (`1` under `PC4-M10` on top of `Intake`, and `1` between `Intake` and `Manifold_Frame`; no third O-ring), `2` `5mm OD x 3mm ID` aluminum tubes (`~55mm` length), `1` `PC4-M10` fitting, `1` `6mm OD x 4mm ID` cooling tube
  - Optional BDsensor hardware: `~2` `M2` (`3.5mm x 3mm`) heat-sets, `~1` `M2 x 10mm BHCS`, `~1` `M2 x 8mm BHCS`
- **Verified Electronics & Motion COTS (`HEAD:BOM.md`):** `A3DP FXD` extruder (`NEMA 14`), `Takoto` or `Dragon` hotend, `2510` `24V` ball-bearing axial heatbreak fan (toolless snap housing), `Igus Chainflex cable` (`cf9-05-04`) CAN/wiring umbilical, standard PTFE filament Bowden tube, optional `BDsensor`.
- **Verified Structural Print Matrix (`HEAD:Print_Settings.md`):** `ABS`, `ASA`, or `PC` (`0.4mm` nozzle) | `0.2mm` layer height | `0.4mm - 0.45mm` extrusion width | `4` minimum wall perimeters | `5` top / `5` bottom solid layers | `40%` infill (`Grid`, `Gyroid`, or `Rectilinear`) | `None` supports.

## 🔗 Companion Projects & Kinematic / System Links
- [`Pneuma_Remote_Air`](../../Projects/Pneuma_Remote_Air/Pneuma_Remote_Air.md) — Stationary dual-pump compressed-air source feeding Alembic's `6mm OD` intake (`PC4-M10`) and controlling `M106`/`M107` via `Pneuma_Control.cfg`.
- [`A3DP_Gantry_Assembly`](../../Projects/A3DP_Gantry_Assembly/A3DP_Gantry_Assembly.md) — Rigid CNC-milled CoreXY gantry carriage interface (`Belt_Clamp_9mm.step` for `9mm` belts).
- [`Pestle_Rotational_Bowden`](../../Projects/Pestle_Rotational_Bowden/Pestle_Rotational_Bowden.md) — Gantry-mounted rotational Bowden feeder reducing filament drag into the `A3DP FXD` extruder.
- [`Extras`](../../Projects/Extras/Extras.md) — `20mm` calibration cube (`Alch_Cube_20mm_V4.stl`) used to dial ABS/ASA shrinkage before printing bearing/O-ring pockets.

## 🔍 Provenance Status & Open [TBD] / [CONFLICT] Ledger
> [!WARNING]
> Figures inside this ledger are quarantined by `verify_claims.py` and must be resolved with the author before committing `Alembic_Toolhead`.

- **Git & Provenance Baseline (`2026-11-16`):** `main:clean` at commit `43ead67` (`audit_repo_docs.py`: `0` load-bearing issues, `0` isolated warnings; `format_image.py --inspect`: `3/3` hero PNGs `[PASS]`; `verify_claims.py --fail-on-tbd`: `0` unbacked claims / `0` open `[TBD]` offenders across all `5` docs (`VRF-d59804719911`, `VRF-cba1b9f1bbcb`); `audit_data_boundary.py`: `BOUNDARY_CLEAN`; `0` open blocking `[TBD]`s).
- **Resolved `BOM.md` / `Assembly_Guide.md` Reconciliation (`43ead67`, `2026-11-16`):** Reconciled and committed all `8` files (`BOM.md` fasteners matched `HEAD`; verified `2` O-rings total, `4` `M3x5x4mm` inserts, `(2) M3x65mm SHCS`, `(4) M3x8mm SHCS` carriage mount + `(2) M3x8mm SHCS` Chainflex clamp, `(2) M3x24mm BHCS`, generic BDsensor shim height wording, `2.85mm` filament mandrel retained, `Tg` numbers removed, `Belt_Clamp_9mm.step` silently optional, `Alembic_Toolhead_V201 - PC4-M10 Bowden Pass-Through.step` & `Alembic_Toolhead_V201 - Pnuematic_Fitting_6mmOD.step` COTS references documented in `BOM.md`, `Dragon-MZE` STLs present, and standard AI transparency footers appended to all `5` docs).
- **Optional Home Follow-Up (`Intake_6mmOD` STL):** `Alembic_Toolhead_V201 - Intake_6mmOD.step` (`17.00 × 20.00 × 57.20 mm`) is listed in `BOM.md` (`Qty 1`, covered by STEP); verify from home workstation whether the standalone Intake STL is merged inside `Pnuematic_Strain_Relief.stl` or upload standalone STL to `STL_Files/` when convenient.

## 🎯 Active Tasks
*(Transcluded live from `### Alembic_Toolhead` in [`Alchemical3D_Tasks`](../../Tasks/Alchemical-3D_Tasks.md))*

> **Active Task Queue**: Tracked in [`Alchemical3D_Tasks`](../../Tasks/Alchemical-3D_Tasks.md#Alembic_Toolhead) *(Single-Writer Task Umbrella)*.

## 🚀 Session Handoff & Multi-Session Kickstart (`SESSION-HANDOFF`)
<!-- SESSION-HANDOFF:START -->
- **Last Session Timestamp**: `2026-11-16`
- **Checkpoint Provenance**: `HEAD SHA: 43ead679c0b0` | `Tree Hash: 13b0feafb257` | `Worktree: clean` | `Last Verification: VRF-d59804719911,VRF-cba1b9f1bbcb`
- **Where We Stopped (Verified State & Context)**:
  Pushed Alembic_Toolhead reconciliation and formatted hero cards (3ff29ce..43ead67) to origin/main
- **Active Project State Ledger & Blockers**: None
- **Next Session Kickstart & Discussion Points**:
  1. Review deployed GitHub formatting; optional home check on standalone Intake STL vs Pnuematic_Strain_Relief.stl
<!-- SESSION-HANDOFF:END -->
