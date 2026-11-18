---
project: "Pestle_Rotational_Bowden"
parent_note: "Pestle_Rotational_Bowden"
entity: "Alchemical-3D"
compartment: "public"
telemetry_domain: "hardware"
mode: "obsidian"
local_path: "/home/orin/Projects/Alchemical3D/Pestle_Rotational_Bowden"
last_cad_sync: "2026-11-06"
last_synced: "2026-11-06"
latest_disk_mtime: "2026-10-14 20:41:15"
inventory_sha256: "df69544c08452cde"
step_count: 1
stl_count: 7
firmware_count: 0
parity_status: "SYNCED"
---

# 📐 Hardware & CAD Telemetry Manifest: Pestle_Rotational_Bowden

Linked Parent Note: [`Pestle_Rotational_Bowden`](Pestle_Rotational_Bowden.md) | Hub: [`README.md`](../../README.md)

> [!NOTE]
> **Auto-Generated Deterministic Telemetry**: This manifest is maintained by `inspect_hardware_ecosystem.py` and `sync_memory.py --sync-hardware` for zero-token subagent lookups. Compare `latest_disk_mtime` against disk before relying on cached geometry after CAD exports.

## 1. Summary & Parity Overview
- **Repository Path:** `/home/orin/Projects/Alchemical3D/Pestle_Rotational_Bowden`
- **CAD Inventory:** `1` STEP files | `7` STL meshes | `0` Firmware configs
- **STEP ↔ STL Dimensional Parity:** `SYNCED` (`0` bounding-box drifts > `0.20mm`)
- **Total Closed-Mesh Geometric Volume:** `61.25 cm³`

## 2. CAD & Mesh Envelope Telemetry

<!-- AUTO-HARDWARE-CAD:START -->
### STL Mesh Envelope & Volume Telemetry

| STL File | Envelope `X × Y × Z (mm)` | Solid Volume (`cm³`) | Triangles | STEP Sync | Doc Ref |
| :--- | :---: | :---: | :---: | :---: | :---: |
| `[a]_pestle_lever.stl` | `13.12 × 21.55 × 43.92` | `4.38` | `8768` | `IN_ASSEMBLY_STEP` | `Yes (Prose)` |
| `[a]_pestle_rotation_brace.stl` | `13.00 × 29.60 × 41.82` | `3.86` | `14084` | `IN_ASSEMBLY_STEP` | `Unlisted` |
| `pestle_2020_extrusion_mount.stl` | `16.00 × 37.00 × 44.80` | `15.22` | `5466` | `IN_ASSEMBLY_STEP` | `Unlisted` |
| `pestle_3DFused_gantry_mount.stl` | `13.60 × 36.00 × 59.63` | `11.76` | `14316` | `IN_ASSEMBLY_STEP` | `Unlisted` |
| `pestle_main_body.stl` | `21.57 × 44.00 × 59.92` | `15.77` | `22868` | `IN_ASSEMBLY_STEP` | `Yes (Prose)` |
| `pestle_motor_plate.stl` | `11.00 × 44.05 × 45.94` | `5.66` | `8486` | `IN_ASSEMBLY_STEP` | `Unlisted` |
| `pestle_top_plate.stl` | `6.45 × 29.99 × 42.51` | `4.60` | `8734` | `IN_ASSEMBLY_STEP` | `Yes (Prose)` |

### STEP Analytic Geometry & Cylindrical Surface Histogram

| STEP File | Export Date | Envelope `X × Y × Z (mm)` | Detected Cylindrical Surfaces `Ø (mm)` × Count |
| :--- | :---: | :---: | :--- |
| `Pestle_Rev-1.2.step` | `2022-11-03` | `81.59 × 115.87 × 127.63` | `Ø5.30mm`×288, `Ø23.75mm`×50, `Ø7.20mm`×34, `Ø9.50mm`×34, `Ø3.25mm`×24 |
<!-- AUTO-HARDWARE-CAD:END -->

## 3. Firmware & Pinout Telemetry

<!-- AUTO-HARDWARE-CFG:START -->
| `_none_` | `_None_` | `_None_` | `_None_` |
<!-- AUTO-HARDWARE-CFG:END -->

## 4. Verified Fasteners, Inserts & BOM Schedule
Confirmed by operator (`2026-11-17`) and reconciled against `README.md` (`Rev 1.2` baseline):
- **Heat-Set Inserts:** `(6)` `M3x5x4mm` brass heat-set inserts (`3` Main Body, `1` Lever, `2` Transmission Plate; BOM `7` corrected to `6`).
- **Fasteners (All `SHCS`):** `(1)` `M3x16mm SHCS`, `(1)` `M3x20mm SHCS` (sub-assembly stack-depth fasteners), `(2)` `M3x30mm SHCS`, `(2)` `M3x35mm SHCS`, `(1)` `M5x16mm SHCS`, `(1)` `M5` Hex Nut.
- **Bearings, COTS & Drive Hardware:** `(1)` `F5-12M` `5mm ID x 12mm OD x 4mm` Thrust Bearing (placed between Rotational Cross Brace and mount in Step 12; optional shim washers under `M5` bolt head in Step 10), `(3)` `PC4-M6` Bowden connectors, `(1)` `BondTech BMG Internals Kit` (`50T` `5mm` primary gear, `(2)` `5mm OD / 3mm ID` needle bearing assemblies over `(1)` short `3mm` bearing steel rod, `MR85ZZ` bearings, thumbscrew spring), `(1)` `LDO NEMA 14` stepper (`36STH20-1004AHG-9T`), `(1)` `Loctite 222MS` Threadlocker (metal-to-metal only; keep off `ABS`/`ASA` polymer parts).
