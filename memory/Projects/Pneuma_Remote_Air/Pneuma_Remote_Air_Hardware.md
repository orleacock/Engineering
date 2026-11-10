---
project: "Pneuma_Remote_Air"
parent_note: "Pneuma_Remote_Air"
entity: "Alchemical-3D"
compartment: "public"
telemetry_domain: hardware
mode: "obsidian"
local_path: "/home/orin/Projects/Alchemical3D/Pneuma_Remote_Air"
last_cad_sync: 2026-11-10
last_synced: 2026-11-10
latest_disk_mtime: 2026-11-10 08:06:27
inventory_sha256: 33b8abbd2777e8a8
step_count: 12
stl_count: 11
firmware_count: 1
parity_status: DRIFT_DETECTED
---

# 📐 Hardware & CAD Telemetry Manifest: Pneuma_Remote_Air

Linked Parent Note: [`Pneuma_Remote_Air`](Pneuma_Remote_Air.md) | Hub: [`README.md`](../../README.md)

> [!NOTE]
> **Auto-Generated Deterministic Telemetry**: This manifest is maintained by `inspect_hardware_ecosystem.py` and `sync_memory.py --sync-hardware` for zero-token subagent lookups. Compare `latest_disk_mtime` against disk before relying on cached geometry after CAD exports.

## 1. Summary & Parity Overview
- **Repository Path:** `/home/orin/Projects/Alchemical3D/Pneuma_Remote_Air`
- **CAD Inventory:** `12` STEP files | `11` STL meshes | `1` Firmware configs
- **STEP ↔ STL Dimensional Parity:** `DRIFT_DETECTED` (`1` bounding-box drifts > `0.20mm`)
- **Total Closed-Mesh Geometric Volume:** `475.37 cm³`
- **STEP-Only Parts (COTS Reference or Unexported STLs):** `Pneuma_201 - 1-8-NPT Direct_Action_Valve.step`

## 2. CAD & Mesh Envelope Telemetry

<!-- AUTO-HARDWARE-CAD:START -->
### STL Mesh Envelope & Volume Telemetry

| STL File | Envelope `X × Y × Z (mm)` | Solid Volume (`cm³`) | Triangles | STEP Sync | Doc Ref |
| :--- | :---: | :---: | :---: | :---: | :---: |
| `Pneuma_201 - Extrusion_Mount_A.stl` | `19.00 × 29.00 × 77.40` | `12.00` | `5332` | `MATCH (<=0.2mm)` | `Yes` |
| `Pneuma_201 - Extrusion_Mount_B.stl` | `19.00 × 29.00 × 77.40` | `12.00` | `5252` | `MATCH (<=0.2mm)` | `Yes` |
| `Pneuma_201 - Logo_Detail.stl` | `3.40 × 25.00 × 25.00` | `0.84` | `3514` | `MATCH (<=0.2mm)` | `Yes` |
| `Pneuma_201 - Plug_Grommet_TPU.stl` | `5.60 × 15.00 × 15.00` | `0.37` | `4696` | `MATCH (<=0.2mm)` | `Yes` |
| `Pneuma_201 - Pump_Mount.stl` | `22.00 × 41.40 × 55.03` | `7.41` | `7876` | `MATCH (<=0.2mm)` | `Yes` |
| `Pneuma_201 - TPU_Grommet.stl` | `6.40 × 14.98 × 15.00` | `0.50` | `5064` | `MATCH (<=0.2mm)` | `Yes` |
| `Pneuma_201 - Table_Mount_TPU.stl` | `7.00 × 10.00 × 45.00` | `1.55` | `3804` | `MATCH (<=0.2mm)` | `Yes` |
| `Pneuma_201 - Vacuum_Pump.stl` | `60.00 × 60.00 × 126.00` | `190.80` | `46448` | `DRIFT (delta 1.00mm)` | `Yes` |
| `Pneuma_201 parts - Front_Cover.stl` | `5.60 × 160.40 × 166.40` | `53.00` | `11340` | `MATCH (<=0.2mm)` | `Yes` |
| `Pneuma_201 parts - Main_Body.stl` | `72.00 × 160.40 × 166.40` | `136.03` | `23508` | `MATCH (<=0.2mm)` | `Yes` |
| `Pneuma_201 parts - Rear_Cover.stl` | `7.00 × 160.40 × 166.40` | `60.87` | `14918` | `MATCH (<=0.2mm)` | `Yes` |

### STEP Outer Envelope & Closed Circular Surface Histogram

| STEP File | Export Date | Envelope `X × Y × Z (mm)` | Closed Circular Surfaces `Ø (mm)` × Count |
| :--- | :---: | :---: | :--- |
| `Pneuma_201 - 1-8-NPT Direct_Action_Valve.step` | `2026-04-29` | `32.00 × 39.00 × 55.00` | `Ø9.00mm`×2 |
| `Pneuma_201 - Extrusion_Mount_A.step` | `2026-04-29` | `19.00 × 29.00 × 77.40` | `Ø3.50mm`×1, `Ø6.00mm`×1 |
| `Pneuma_201 - Extrusion_Mount_B.step` | `2026-04-29` | `19.00 × 29.00 × 77.40` | `Ø3.50mm`×1, `Ø6.00mm`×1 |
| `Pneuma_201 - Logo_Detail.step` | `2026-04-29` | `3.40 × 25.00 × 25.00` | `Ø4.76mm`×1 |
| `Pneuma_201 - Plug_Grommet_TPU.step` | `2026-04-29` | `5.60 × 14.99 × 15.00` | `Ø8.00mm`×1, `Ø11.60mm`×1, `Ø12.40mm`×1, `Ø15.00mm`×1 |
| `Pneuma_201 - Pump_Mount.step` | `2026-04-29` | `22.00 × 41.40 × 54.92` | `Ø3.30mm`×2, `Ø3.50mm`×1 |
| `Pneuma_201 - TPU_Grommet.step` | `2026-04-29` | `6.40 × 14.95 × 14.96` | _No closed cylindrical surfaces in 1.5–65mm range_ |
| `Pneuma_201 - Table_Mount_TPU.step` | `2026-04-29` | `7.00 × 10.00 × 45.00` | `Ø3.50mm`×1, `Ø6.00mm`×1 |
| `Pneuma_201 - Vacuum_Pump.step` | `2026-04-29` | `59.00 × 59.47 × 126.00` | `Ø4.00mm`×2, `Ø36.00mm`×2, `Ø6.40mm`×1, `Ø7.60mm`×1, `Ø16.00mm`×1, `Ø20.00mm`×1 |
| `Pneuma_201 parts - Front_Cover(1).step` | `2026-05-25` | `5.60 × 160.40 × 166.40` | `Ø5.00mm`×1 |
| `Pneuma_201 parts - Main_Body(1).step` | `2026-05-25` | `72.00 × 160.40 × 166.40` | `Ø12.00mm`×5, `Ø4.70mm`×2 |
| `Pneuma_201 parts - Rear_Cover(1).step` | `2026-05-25` | `7.00 × 160.40 × 166.40` | `Ø4.70mm`×6, `Ø5.00mm`×1 |

> [!IMPORTANT]
> **`[CAD STOP GATE — ONE-PASS TELEMETRY COMPLETE]`**: Base outer bounding envelopes (`X × Y × Z mm`), mesh volumes (`cm³`), and closed circular diameters (`Ø mm`) are complete. Raw CAD geometry does NOT define fastener counts, hole functions (screw vs. dowel vs. vent vs. fillet), or part-to-part mating intent. Do NOT run follow-up Python/grep/sed loops on `.step` or `.stl` files; bind assembly claims strictly to `BOM.md` / `Assembly_Guide.md` or tag `[TBD: Confirm design intent with engineer]`.
<!-- AUTO-HARDWARE-CAD:END -->

## 3. Firmware & Pinout Telemetry

<!-- AUTO-HARDWARE-CFG:START -->
| Config File | MCU Pins | Fan Definitions | G-Code Macros | Scalar Parameters |
| :--- | :--- | :--- | :--- | :--- |
| `Pneuma_Control.cfg` | `PF7`, `PF9` | `pump_cool`, `pump_warm` | `PNEUMA_STATE`, `SET_PNEUMA_MODE`, `M106`, `M107` | `[fan_generic pump_cool] pin=PF7`, `[fan_generic pump_cool] min_power=0.15`, `[fan_generic pump_cool] max_power=1.0`, `[fan_generic pump_cool] shutdown_speed=0`, `[fan_generic pump_warm] pin=PF9`, `[fan_generic pump_warm] min_power=0.15`, `[fan_generic pump_warm] max_power=1.0`, `[fan_generic pump_warm] shutdown_speed=0`, `[gcode_macro PNEUMA_STATE] description=Stores the current state of the Pneuma system`, `[gcode_macro PNEUMA_STATE] variable_mode="COOL"`, `[gcode_macro PNEUMA_STATE] variable_last_speed=0.0`, `[gcode_macro SET_PNEUMA_MODE] description=Set the active Pneuma pump mode (COOL, WARM, DUAL, OFF)`, `[gcode_macro M106] description=Override standard part cooling command to route to active Pneuma pump`, `[gcode_macro M107] description=Override standard part cooling off command` |
<!-- AUTO-HARDWARE-CFG:END -->

## 4. Verified Fasteners, Inserts & BOM Schedule
- Populate verified hardware counts from authoritative assembly sources (`verify_claims.py` whitelist).
