---
project: "Pneuma_Remote_Air"
entity: "Alchemical-3D"
compartment: "public"
project_type: "hardware"
status: "Active"
local_path: "/home/orin/Projects/Alchemical3D/Pneuma_Remote_Air"
repo_head_sha: "0702c9c1c541"
tree_hash: "dc295b6ec1e5"
checkpoint_head_sha: "0702c9c1c541"
checkpoint_tree_hash: "dc295b6ec1e5"
checkpoint_worktree: "clean"
task_umbrella: "../../Tasks/Alchemical-3D_Tasks.md"
last_synced: "2026-11-10"
checkpoint_lessons_digest: "23d19f2766961662"
---

## 🧭 Homunculus Companion Notes & Project Navigation

| Artifact Role | File Link | Purpose |
| :--- | :--- | :--- |
| **Project Hub (`AUTO-TREE`)** | [`Pneuma_Remote_Air.md`](Pneuma_Remote_Air.md) | Canonical architecture overview, `SESSION-HANDOFF`, `AUTO-TREE`, and `[TBD]` Ledger. |
| **Hardware Telemetry** | [`Pneuma_Remote_Air_Hardware.md`](Pneuma_Remote_Air_Hardware.md) | CAD bounding boxes, cylindrical bore histograms, and firmware pinouts. |
| **Lessons Learned & Post-Mortems** | [`Pneuma_Remote_Air_Lessons_Learned.md`](Pneuma_Remote_Air_Lessons_Learned.md) | Root-cause post-mortems (`Symptom -> Root Cause -> Permanent Guardrail`). |
| **Project Templates** | [`Templates/`](Templates/) | Project-specific deliverable templates. |
| **Unverified Quarantine Zone** | [`Quarantine/Quarantine_README.md`](Quarantine/Quarantine_README.md) | Holding zone for unverified notes (`[QUARANTINED — DO NOT CITE AS FACT]`). |
| **Active Task Umbrella** | [`Alchemical-3D_Tasks.md`](../../Tasks/Alchemical-3D_Tasks.md#Pneuma_Remote_Air) | Single-writer task tracker for `Alchemical-3D` (zero duplicate checkboxes in hub). |

---

# 🌬️ Pneuma Remote Air (Dual-Pump Part Cooling)

Part of the [`README.md`](../../README.md) • CAD & Firmware Telemetry: [`Pneuma_Remote_Air_Hardware`](Pneuma_Remote_Air_Hardware.md)

## 🔒 Concept & Design Philosophy ("Why")
- **Off-Gantry Mass & Resonance Isolation (`README.md:10-14`):** Moves heavy part-cooling air generation completely off the moving CoreXY toolhead into a stationary, TPU-isolated enclosure feeding [`Alembic_Toolhead`](../../Projects/Alembic_Toolhead/Alembic_Toolhead.md) through pneumatic tubing.
- **Dual-Pump Thermal-Regime Architecture (`README.md:10-14`, `Firmware/Pneuma_Control.cfg:1-4`):** Upgraded from a single-pump + solenoid diversion layout to an independent **dual-pump system** routing ambient room air (`pump_cool`) for aggressive PLA/overhang freezing and heated chamber air (`pump_warm`) to cool high-temp `ABS`/`ASA` bridges without inducing thermal shock or bed delamination.

## 📍 Repository & File Inventory
- **Local Path:** `/home/orin/Projects/Alchemical3D/Pneuma_Remote_Air`
- **GitHub Remote:** `https://github.com/Alchemical-3D/Pneuma_Remote_Air`
- **Living Documentation:** `README.md`, `BOM.md`, `Print_Settings.md`, `Assembly_Guide.md`, `LICENSE.md`
- **CAD, Firmware & Image Directories:** `STL_Files/` (`11` STLs), `STEP_Files/` (`12` STEPs), `Firmware/` (`Pneuma_Control.cfg`), `Images/Assembly/` — Full telemetry in [`Pneuma_Remote_Air_Hardware`](Pneuma_Remote_Air_Hardware.md)
- **Standards Applied:** [`Verifiable_Accuracy_and_Anti_Hallucination`](../../Standards_and_Specs/Verifiable_Accuracy_and_Anti_Hallucination.md), `Author_Voice_and_Cadence`, [`Fasteners_and_Inserts`](../../Standards_and_Specs/Fasteners_and_Inserts.md), `Image_and_Style_Rules`, `Subagent_and_Memory_Architecture`

<!-- AUTO-TREE:START -->
```text
Repository: Pneuma_Remote_Air | HEAD SHA: 0702c9c1c541 | Tree Hash: dc295b6ec1e5
  Assembly_Guide.md
  BOM.md
  LICENSE.md
  Print_Settings.md
  README.md
  Firmware/
  Firmware/Pneuma_Control.cfg
  Images/
  Images/Pneuma.png
  Images/Pneuma_v2-4_back.png
  Images/Pneuma_v2-4_side.png
  Images/Assembly/
  Images/Assembly/Heatset_Back.png
  Images/Assembly/Heatset_Body.png
  Images/Assembly/Pneuma_Complete_Ext.png
  Images/Assembly/Pneuma_Complete_Table.png
  Images/Assembly/Pneuma_Explode.png
  Images/Assembly/Pump_Mount.png
  STEP_Files/
  STEP_Files/Pneuma_201 - 1-8-NPT Direct_Action_Valve.step
  STEP_Files/Pneuma_201 - Extrusion_Mount_A.step
  STEP_Files/Pneuma_201 - Extrusion_Mount_B.step
  STEP_Files/Pneuma_201 - Logo_Detail.step
  STEP_Files/Pneuma_201 - Plug_Grommet_TPU.step
  STEP_Files/Pneuma_201 - Pump_Mount.step
  STEP_Files/Pneuma_201 - TPU_Grommet.step
  STEP_Files/Pneuma_201 - Table_Mount_TPU.step
  STEP_Files/Pneuma_201 - Vacuum_Pump.step
  STEP_Files/Pneuma_201 parts - Front_Cover(1).step
  STEP_Files/Pneuma_201 parts - Main_Body(1).step
  STEP_Files/Pneuma_201 parts - Rear_Cover(1).step
  STL_Files/
  STL_Files/Pneuma_201 - Extrusion_Mount_A.stl
  STL_Files/Pneuma_201 - Extrusion_Mount_B.stl
  STL_Files/Pneuma_201 - Logo_Detail.stl
  STL_Files/Pneuma_201 - Plug_Grommet_TPU.stl
  STL_Files/Pneuma_201 - Pump_Mount.stl
  STL_Files/Pneuma_201 - TPU_Grommet.stl
  STL_Files/Pneuma_201 - Table_Mount_TPU.stl
  STL_Files/Pneuma_201 - Vacuum_Pump.stl
  STL_Files/Pneuma_201 parts - Front_Cover.stl
  STL_Files/Pneuma_201 parts - Main_Body.stl
  STL_Files/Pneuma_201 parts - Rear_Cover.stl
```
<!-- AUTO-TREE:END -->

## ⚠️ Paramount Assembly Hazards & Mechanical "Whys" (`Mode B1` Anchors)
- **Flush Heat-Set Seating Between Enclosure Halves (`Assembly_Guide.md:24-25`):** Press all `M3x5x4mm` brass heat-set inserts strictly flush with printed surfaces so protruding brass rims cannot create a seam gap between `Rear_Cover` and `Main_Body`.
- **Pressure-Side Thread Sealing (`Assembly_Guide.md:54`):** Wrap Teflon tape on threaded pneumatic fittings on the pressure side to prevent air leaks and line-pressure drop.
- **Minimum Pneumatic Bend Radius (`Assembly_Guide.md:62-64`):** Route pneumatic tubing with generous sweep radii; sharp bends or kinks choke flow delivery to the toolhead.
- **Plastic Torque & Threadlocker Safety ([`Fasteners_and_Inserts`](../../Standards_and_Specs/Fasteners_and_Inserts.md)):** Never torque fasteners into printed `ABS`/`ASA` to metal specs, and keep anaerobic threadlocker strictly away from printed polymers.
- **Legacy Solenoid Valve Caveat (`BOM.md:13-14`):** On legacy single-pump builds using a valve, standard pressure-assisted valves fail to switch under vacuum/low differential—only direct-acting (`1-8-NPT`) valves operate reliably.

## 📐 Verified Specs, COTS Hardware & Print Matrix
- **CAD Telemetry ([`Pneuma_Remote_Air_Hardware`](Pneuma_Remote_Air_Hardware.md)):** `12` STEP files | `11` STL meshes | `1` Klipper `Pneuma_Control.cfg` | Total closed-mesh geometric volume `475.37 cm³`.
  - Structural/Enclosure STLs: `Pneuma_201 parts - Main_Body.stl` (`72.00 × 160.40 × 166.40 mm`), `Pneuma_201 parts - Front_Cover.stl` (`5.60 × 160.40 × 166.40 mm`), `Pneuma_201 parts - Rear_Cover.stl` (`7.00 × 160.40 × 166.40 mm`), `Pneuma_201 - Extrusion_Mount_A.stl`, `Pneuma_201 - Extrusion_Mount_B.stl`, `Pneuma_201 - Pump_Mount.stl`, `Pneuma_201 - Logo_Detail.stl`, `Pneuma_201 - Vacuum_Pump.stl` (COTS reference mesh).
  - Vibration-Isolation Elastomer STLs: `Pneuma_201 - TPU_Grommet.stl`, `Pneuma_201 - Table_Mount_TPU.stl`, `Pneuma_201 - Plug_Grommet_TPU.stl`.
- **Verified COTS Pump & Harness Baseline (`BOM.md:14-61`):** `2` Vacuum Pumps (`> 10 L/min`, positive pressure `>= 70 kPa`, vacuum `<= -40 kPa`), `20AWG` High-Temp `FEP` Wire (`TC-FEP`), and `1` Each `5-PIN` Single Row Molex Micro-Fit 3.0 connector pair.
- **Verified Klipper Firmware (`Firmware/Pneuma_Control.cfg:13-26`):**
  - `[fan_generic pump_cool]`: `pin: PF7`, `min_power: 0.15`, `max_power: 1.0`, `shutdown_speed: 0` (de-energizes part-cooling pump on MCU fault; hotend heatsink `[heater_fan]` remains `shutdown_speed: 1` to prevent heat creep).
  - `[fan_generic pump_warm]`: `pin: PF9`, `min_power: 0.15`, `max_power: 1.0`, `shutdown_speed: 0`
  - Macros: `PNEUMA_STATE`, `SET_PNEUMA_MODE` (`COOL`, `WARM`, `DUAL`, `OFF`), dynamic `M106` / `M107` overrides.
- **Structural Print Baseline (`Print_Settings.md:5-14`):** Enclosure in `ABS`/`ASA` or `PETG`; mounts in `ABS`/`ASA` | `0.20mm` layer height | `4` perimeters | `5` top/bottom layers | `40%` `Grid` or `Gyroid` infill *(strictly structural parts only; TPU settings unrecorded—see conflict ledger below)*.

## 🔗 Companion Projects & Kinematic / System Links
- [`Alembic_Toolhead`](../../Projects/Alembic_Toolhead/Alembic_Toolhead.md) — Primary compressed-air consumer (`6mm OD` umbilical into `PC4-M10` intake).
- [`A3DP_Gantry_Assembly`](../../Projects/A3DP_Gantry_Assembly/A3DP_Gantry_Assembly.md) — Compatible high-speed CoreXY gantry benefiting from offloaded blower mass.

## 🔍 Provenance Status & Open [TBD] / [CONFLICT] Ledger
> [!WARNING]
> Figures inside this ledger are quarantined by `verify_claims.py` and are **not** treated as authorized source truth until resolved.

- **Git & Provenance Baseline:** `main:clean` at commit `0702c9c` (`audit_repo_docs.py`: `0` load-bearing issues, `0` isolated warnings; `verify_claims.py`: `0` unbacked claims across `README.md` `VRF-01c5a7f61d28`, `BOM.md` `VRF-886f22bb9de0`, `Print_Settings.md` `VRF-ea4740d35e19`, `Assembly_Guide.md` `VRF-c35e0e00f877`).
- **`[TBD: CONFLICT — BOM Fastener Table vs CAD Bore Histogram & Assembly Guide]`:** `BOM.md` keeps verified baseline rows (`5x M3x5x4mm` heat-sets, `2x M3x10 SHCS`, `2x M3x8 SHCS`, `2x M5x12 BHCS`, `2x M5 T-nuts`) and tags unconfirmed 2nd-pump heat-sets (`[TBD: total_m3x5x4mm_heatset_qty_for_dual_pump_and_cover]`), `Rear_Cover` M3 screws (`[TBD: rear_cover_m3_screw_qty_and_length]`), `Front_Cover` hardware (`[TBD: front_cover_fastener_spec_or_snap_fit_confirmation]`), and optional `Table_Mount_TPU` M3 screws (`[TBD: optional_table_mount_m3_screw_qty_and_length]`) pending physical bench count.
- **`[TBD: tpu_shore_hardness_and_slicer_parameters]`:** `Print_Settings.md` splits structural `ABS`/`ASA`/`PETG` settings (`0.2mm`, `4` walls, `5` top/bottom, `40%` `Grid`/`Gyroid`) from vibration-isolation elastomers (`TPU_Grommet.stl`, `Table_Mount_TPU.stl`, `Plug_Grommet_TPU.stl`) with explicit `[TBD: tpu_shore_hardness_rating]`, `[TBD: tpu_layer_height_mm]`, `[TBD: tpu_wall_count]`, `[TBD: tpu_top_bottom_layers]`, and `[TBD: tpu_infill_percentage_and_pattern]` placeholders.
- **`[TBD: optional_tube_adapter_stl_files]`:** `BOM.md` and `Assembly_Guide.md` document as-needed tube fittings vs. `TPU_Grommet.stl` pass-throughs and `Plug_Grommet_TPU.stl` blanking plugs while tagging optional printed tube-adapter STLs (`[TBD: optional_tube_adapter_stl_files]`) and COTS pneumatic fitting thread/push-to-connect specs (`[TBD: pneumatic_fitting_qty_and_thread_spec]`).
- **`[TBD: cots_vacuum_pump_mesh_drift]`:** `Pneuma_201 - Vacuum_Pump.stl` shows a `1.00mm` X-envelope delta vs. `.step` (`60.00 × 60.00 × 126.00 mm` vs. `59.00 × 59.47 × 126.00 mm` COTS reference model) and is explicitly excluded from slicing in `BOM.md` and `Print_Settings.md`.

## 🎯 Active Tasks
*(Transcluded live from `### Pneuma_Remote_Air` in [`Alchemical3D_Tasks`](../../Tasks/Alchemical-3D_Tasks.md))*

> **Active Task Queue**: Tracked in [`Alchemical3D_Tasks`](../../Tasks/Alchemical-3D_Tasks.md#Pneuma_Remote_Air) *(Single-Writer Task Umbrella)*.

## 🚀 Session Handoff & Multi-Session Kickstart (`SESSION-HANDOFF`)
<!-- SESSION-HANDOFF:START -->
- **Last Session Timestamp**: `2026-11-10`
- **Checkpoint Provenance**: `HEAD SHA: 0702c9c1c541` | `Tree Hash: dc295b6ec1e5` | `Worktree: clean` | `Last Verification: VRF-01c5a7f61d28, VRF-886f22bb9de0, VRF-ea4740d35e19, VRF-c35e0e00f877`
- **Where We Stopped (Verified State & Context)**:
  Completed P3 Pneuma_Remote_Air rework at commit 0702c9c: formatted 6 assembly PNG cards, stripped inline CSS, set fail-safe shutdown_speed: 0 on pump_cool/pump_warm, standardized Dual-Pump BOM & Assembly Guide, split Print_Settings.md structural vs TPU tables, and verified 0 unbacked claims.
- **Active Project State Ledger & Blockers**: Open [TBD] physical fastener counts and TPU slicer parameters awaiting bench measurement.
- **Next Session Kickstart & Discussion Points**:
  1. Physically count Rear_Cover, Front_Cover, 2nd Pump_Mount heatset, and optional Table_Mount_TPU fasteners on bench.
  2. Measure and record TPU Shore hardness and slicer parameters in Print_Settings.md.
- **Open Discussion / Alignment Questions**: A1: Dual-Pump standard (2 pumps, 0 solenoid valves; legacy 1/8-NPT note) | A2: Verified fasteners kept, unconfirmed rows tagged [TBD] | A3: As-needed tube fittings vs grommets/plugs + TPU slicer [TBD]s | A4: shutdown_speed: 0 on part-cooling pumps, 1 on hotend heatsink fans
<!-- SESSION-HANDOFF:END -->
