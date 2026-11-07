---
project: "Pneuma_Remote_Air"
entity: "Alchemical-3D"
compartment: "public"
project_type: "hardware"
status: "Active"
local_path: "/home/orin/Projects/Alchemical3D/Pneuma_Remote_Air"
repo_head_sha: "02d872f4a741"
tree_hash: "dc295b6ec1e5"
checkpoint_head_sha: "02d872f4a741"
checkpoint_tree_hash: "dc295b6ec1e5"
checkpoint_worktree: "('clean', [])"
task_umbrella: "../../Tasks/Alchemical-3D_Tasks.md"
last_synced: "2026-11-06"
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
- **Living Documentation:** `README.md`, `BOM.md`, `Print_Settings.md` *(currently a placeholder stub)*, `Assembly_Guide.md`, `LICENSE.md`
- **CAD, Firmware & Image Directories:** `STL_Files/` (`11` STLs), `STEP_Files/` (`12` STEPs), `Firmware/` (`Pneuma_Control.cfg`), `Images/Assembly/` — Full telemetry in [`Pneuma_Remote_Air_Hardware`](Pneuma_Remote_Air_Hardware.md)
- **Standards Applied:** [`Verifiable_Accuracy_and_Anti_Hallucination`](../../Standards_and_Specs/Verifiable_Accuracy_and_Anti_Hallucination.md), `Author_Voice_and_Cadence`, [`Fasteners_and_Inserts`](../../Standards_and_Specs/Fasteners_and_Inserts.md), `Image_and_Style_Rules`, `Subagent_and_Memory_Architecture`

<!-- AUTO-TREE:START -->
```text
Repository: Pneuma_Remote_Air | HEAD SHA: 02d872f4a741 | Tree Hash: dc295b6ec1e5
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
- **Verified Klipper Firmware (`Firmware/Pneuma_Control.cfg:11-57`):**
  - `[fan_generic pump_cool]`: `pin: PF7`, `min_power: 0.15`, `max_power: 1.0`, `shutdown_speed: 1`
  - `[fan_generic pump_warm]`: `pin: PF9`, `min_power: 0.15`, `max_power: 1.0`, `shutdown_speed: 1`
  - Macros: `PNEUMA_STATE`, `SET_PNEUMA_MODE` (`COOL`, `WARM`, `DUAL`, `OFF`), dynamic `M106` / `M107` overrides.
- **Verified COTS Pump Baseline (`BOM.md:19-23`):** Flow rate `> 10 L/min`, positive pressure `>= 70 kPa`, vacuum `<= -40 kPa`.
- **Structural Print Baseline (`Print_Settings.md:5-14`):** Enclosure in `ABS`/`ASA` or `PETG`; mounts in `ABS`/`ASA` | `0.20mm` layer height | `4` perimeters | `5` top/bottom layers | `40%` `Grid` or `Gyroid` infill *(strictly structural parts only; TPU settings unrecorded—see conflict ledger below)*.

## 🔗 Companion Projects & Kinematic / System Links
- [`Alembic_Toolhead`](../../Projects/Alembic_Toolhead/Alembic_Toolhead.md) — Primary compressed-air consumer (`6mm OD` umbilical into `PC4-M10` intake).
- [`A3DP_Gantry_Assembly`](../../Projects/A3DP_Gantry_Assembly/A3DP_Gantry_Assembly.md) — Compatible high-speed CoreXY gantry benefiting from offloaded blower mass.

## 🔍 Provenance Status & Open [TBD] / [CONFLICT] Ledger
> [!WARNING]
> Figures inside this ledger are quarantined by `verify_claims.py` and are **not** treated as authorized source truth until resolved.

- **Git & Provenance Baseline:** `main:clean` at commit `02d872f` (`audit_repo_docs.py`: `14` load-bearing inline-CSS/image-card errors, `20` isolated warnings; `Print_Settings.md:3` flagged `PLACEHOLDER_STUB_SOURCE`).
- **`[TBD: CONFLICT — Dual-Pump (README.md / Pneuma_Control.cfg) vs Single-Pump Solenoid (BOM.md:13-14 / Assembly_Guide.md:57-60)]`:** `README.md` and `Pneuma_Control.cfg` implement dual pumps (`pump_cool` + `pump_warm`), while `BOM.md` and `Assembly_Guide.md` still document single-pump `1/8-NPT` solenoid plumbing.
- **`[TBD: CONFLICT — BOM Fastener Table vs CAD Bore Histogram & Assembly Guide]`:** `BOM.md:38-40` lists only `(5) M3x5x4mm` heat-sets (for `Rear_Cover` / `Pump_Mount` with no mating `M3` screw row!), `(2) M3x10 SHCS`, and `(2) M3x8 SHCS`, whereas [`Pneuma_Remote_Air_Hardware`](Pneuma_Remote_Air_Hardware.md) detects `Ø4.70mm`×2 + `Ø3.00mm`×16 on `Main_Body(1).step` and `Ø4.70mm`×6 + `Ø5.00mm`×5 + `Ø3.00mm`×8 on `Rear_Cover(1).step` (and `Assembly_Guide.md` Fig. 1 installs inserts in `Main_Body`).
- **`[TBD: tpu_shore_hardness_and_slicer_parameters]`:** `Print_Settings.md` is a placeholder stub with zero TPU Shore hardness (`95A`/`85A`), perimeter, or infill specs for `TPU_Grommet.stl`, `Table_Mount_TPU.stl`, and `Plug_Grommet_TPU.stl` (never borrow `40%` ABS infill onto TPU).
- **`[TBD: cots_vacuum_pump_mesh_drift]`:** `Pneuma_201 - Vacuum_Pump.stl` shows a `1.00mm` X-envelope delta vs. `.step` (`60.00 × 60.00 × 126.00 mm` vs. `59.00 × 59.47 × 126.00 mm` COTS reference model).

## 🎯 Active Tasks
*(Transcluded live from `### Pneuma_Remote_Air` in [`Alchemical3D_Tasks`](../../Tasks/Alchemical-3D_Tasks.md))*

> **Active Task Queue**: Tracked in [`Alchemical3D_Tasks`](../../Tasks/Alchemical-3D_Tasks.md#Pneuma_Remote_Air) *(Single-Writer Task Umbrella)*.

## 🚀 Session Handoff & Multi-Session Kickstart (`SESSION-HANDOFF`)
<!-- SESSION-HANDOFF:START -->
- **Last Session Timestamp**: `2026-11-05`
- **Checkpoint Provenance**: `HEAD SHA: 02d872f4a741` | `Tree Hash: dc295b6ec1e5` | `Worktree: ('clean', [])` | `Last Verification: Transplanted from verified Memory v2 baseline`
- **Where We Stopped (Verified State & Context)**:
  - Transplanted `Pneuma_Remote_Air` dossier into native Homunculus Dual-Mode Memory (`entity: Alchemical-3D`, `compartment: public`, `project_type: hardware`). All verified specifications, hazards, and open `[TBD]` ledgers preserved verbatim.
- **Active Project State Ledger & Blockers**:
  - See `## 🔍 Provenance Status & Open [TBD] / [CONFLICT] Ledger` above and active tasks in [`Alchemical-3D_Tasks.md`](../../Tasks/Alchemical-3D_Tasks.md).
- **Next Session Kickstart & Discussion Points**:
  1. Run `python3 skills/project-memory/scripts/sync_memory.py --project Pneuma_Remote_Air --kickstart` to verify repository provenance.
  2. Review open tasks in [`Alchemical-3D_Tasks.md`](../../Tasks/Alchemical-3D_Tasks.md#Pneuma_Remote_Air).
<!-- SESSION-HANDOFF:END -->
