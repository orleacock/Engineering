---
project: "Alembic_Toolhead"
entity: "Alchemical-3D"
compartment: "public"
project_type: "hardware"
status: "Alpha"
local_path: "/home/orin/Projects/Alchemical3D/Alembic_Toolhead"
repo_head_sha: "3ff29ce51139"
tree_hash: "13b0feafb257"
checkpoint_head_sha: "3ff29ce51139"
checkpoint_tree_hash: "71ea081ef196"
checkpoint_worktree: "dirty (8 files)"
task_umbrella: "../../Tasks/Alchemical-3D_Tasks.md"
last_synced: "2026-11-10"
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
Repository: Alembic_Toolhead | HEAD SHA: 3ff29ce51139 | Tree Hash: 13b0feafb257
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
- **Tube Bending Spacing & Internal Mandrel (`HEAD:Assembly_Guide.md`):** Maintain `5–10mm` initial spacing between `Bend_Tool_Base.stl` and `Bend_Tool_Lever.stl` to prevent jig fracture and let the `5mm OD x 3mm ID` tube wrap cleanly; insert a `2.8mm` plastic welding rod (`<3mm` mandrel) if needed to prevent wall collapse, and compute bend start offset as `(distance from Lower_Body tube passthrough to heatblock edge) / 2`.
- **Pneumatic `9x2` O-Ring Seal Alignment (`HEAD:Assembly_Guide.md`):** Seat the upper `9x2` O-ring into the intake groove *before* threading the `PC4-M10` fitting, and align the central `9x2` O-ring on the manifold prior to vertical tie-down (`65mm M3 BHCS`) so compressed air cannot leak.
- **`5°` Tube Toe-In vs. Nozzle Bed-Crash Clearance (`HEAD:Assembly_Guide.md`):** Rotate aluminum tubes `~5°` inward so the airflow vertex converges directly beneath the nozzle tip while keeping tube ends strictly above the nozzle face plane to prevent part/frame strikes.
- **Grub-Screw Tube Clamping (`HEAD:Assembly_Guide.md`):** Snug `M3` grub screws in `Lower_Body` just enough to lock tube rotation without crushing the `3mm ID` aluminum bore.

## 📐 Verified Specs, COTS Hardware & Print Matrix
- **CAD Telemetry ([`Alembic_Toolhead_Hardware`](Alembic_Toolhead_Hardware.md)):** `20` STEP files | `14` STL meshes (all `14` STLs `MATCH (<=0.2mm)` STEP↔STL parity) | Total closed-mesh geometric volume `105.74 cm³`. Dedicated hotend fan baffles for `Takoto` (`Fan_Baffle_Takoto.stl`) and `Dragon` (`Fan_Baffle_Dragon.stl`), plus `Dragon-MZE` BDsensor retainer/shim (`Sensor_Retainer_Dragon-MZE.stl`, `Shim_56_BDsensor_Dragon-MZE.stl`, `3.60mm` thick vs. `Shim_06mm_BDsensor.stl` `0.60mm`).
- **Committed `HEAD` (`3ff29ce`) Fasteners & Seals (`HEAD:BOM.md`):**
  - `~4` `M3x5x4mm` brass heat-set inserts (`Intake_6mmOD` `Ø4.70mm`×2, `Pnuematic_Strain_Relief` `Ø4.70mm`×4, `Lower_Body` `Ø5.00mm`×4 in CAD)
  - `~2` `M3 x 65mm` Cap/Button Head vertical tie-bolts (`65mm M3 BHCS` in `HEAD:Assembly_Guide.md` Fig. 8)
  - `~8` `M3 x 8mm` general assembly screws, `~2` `M3 x 20mm` strain-relief screws, `~2` `M3 x 24mm` front fan-baffle/manifold screws, `~2` `M3 x 0.5 x 4mm` cup-point grub screws
  - `2` `9x2` (`23/64 x 5/64"`) O-rings, `2` `5mm OD x 3mm ID` aluminum tubes (`~55mm` length), `1` `PC4-M10` fitting, `1` `6mm OD x 4mm ID` cooling tube
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

- **Git & Provenance Baseline:** `main:dirty(8)` vs. clean `HEAD` commit `3ff29ce` (`audit_repo_docs.py`: `0` formatting load-bearing errors, `5` missing AI footers).
- **`[TBD: CONFLICT — clean HEAD:BOM.md (3ff29ce) vs unstaged dirty BOM.md]`:** Unstaged `BOM.md` altered fastener rows relative to committed `3ff29ce`—changing `M3x8` qty (`~8` vs `2`), removing `M3x24mm` (`~2`), removing `M3` grub screws (`~2`, despite Step 1 requiring grub screws!), removing optional `M2` BDsensor inserts/screws, and adding `(2) M3x10mm SHCS` + `(2) M3 hex nuts`, while unstaged `Assembly_Guide.md` also introduced `2.85mm` filament mandrel wording not in `3ff29ce`.
- **`[TBD: step_only_parts_disposition]`:** `4` STEP files in `STEP_Files/` (`Intake_6mmOD.step`, `Belt_Clamp_9mm.step`, `PC4-M10 Bowden Pass-Through.step`, `Pnuematic_Fitting_6mmOD.step`) have no matching `.stl` in `STL_Files/` (confirm which are COTS reference models vs. printable parts needing STL export, and add `Dragon-MZE` STLs to `BOM.md`).

## 🎯 Active Tasks
*(Transcluded live from `### Alembic_Toolhead` in [`Alchemical3D_Tasks`](../../Tasks/Alchemical-3D_Tasks.md))*

> **Active Task Queue**: Tracked in [`Alchemical3D_Tasks`](../../Tasks/Alchemical-3D_Tasks.md#Alembic_Toolhead) *(Single-Writer Task Umbrella)*.

## 🚀 Session Handoff & Multi-Session Kickstart (`SESSION-HANDOFF`)
<!-- SESSION-HANDOFF:START -->
- **Last Session Timestamp**: `2026-11-05`
- **Checkpoint Provenance**: `HEAD SHA: 3ff29ce51139` | `Tree Hash: 71ea081ef196` | `Worktree: ('dirty (8 files)', ['M ALPHA_&_DIRECTION.md', 'M Assembly_Guide.md', 'M BOM.md', 'M Images/full_images/alembic_angle_down.png', 'M Images/full_images/alembic_angle_up.png', 'M Images/full_images/alembic_face.png', 'M Print_Settings.md', 'M README.md'])` | `Last Verification: Transplanted from verified Memory v2 baseline`
- **Where We Stopped (Verified State & Context)**:
  - Transplanted `Alembic_Toolhead` dossier into native Homunculus Dual-Mode Memory (`entity: Alchemical-3D`, `compartment: public`, `project_type: hardware`). All verified specifications, hazards, and open `[TBD]` ledgers preserved verbatim.
- **Active Project State Ledger & Blockers**:
  - See `## 🔍 Provenance Status & Open [TBD] / [CONFLICT] Ledger` above and active tasks in [`Alchemical-3D_Tasks.md`](../../Tasks/Alchemical-3D_Tasks.md).
- **Next Session Kickstart & Discussion Points**:
  1. Run `python3 skills/project-memory/scripts/sync_memory.py --project Alembic_Toolhead --kickstart` to verify repository provenance.
  2. Review open tasks in [`Alchemical-3D_Tasks.md`](../../Tasks/Alchemical-3D_Tasks.md#Alembic_Toolhead).
<!-- SESSION-HANDOFF:END -->
