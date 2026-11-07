---
project: "Alembic_Toolhead"
parent_note: "Alembic_Toolhead"
entity: "Alchemical-3D"
compartment: "public"
telemetry_domain: "hardware"
mode: "obsidian"
local_path: "/home/orin/Projects/Alchemical3D/Alembic_Toolhead"
last_cad_sync: "2026-11-06"
last_synced: "2026-11-06"
latest_disk_mtime: "2026-10-14 20:41:03"
inventory_sha256: "ff586f06c5cbf509"
step_count: 20
stl_count: 14
firmware_count: 0
parity_status: "SYNCED"
---

# 📐 Hardware & CAD Telemetry Manifest: Alembic_Toolhead

Linked Parent Note: [`Alembic_Toolhead`](Alembic_Toolhead.md) | Hub: [`README.md`](../../README.md)

> [!NOTE]
> **Auto-Generated Deterministic Telemetry**: This manifest is maintained by `inspect_hardware_ecosystem.py` and `sync_memory.py --sync-hardware` for zero-token subagent lookups. Compare `latest_disk_mtime` against disk before relying on cached geometry after CAD exports.

## 1. Summary & Parity Overview
- **Repository Path:** `/home/orin/Projects/Alchemical3D/Alembic_Toolhead`
- **CAD Inventory:** `20` STEP files | `14` STL meshes | `0` Firmware configs
- **STEP ↔ STL Dimensional Parity:** `SYNCED` (`0` bounding-box drifts > `0.20mm`)
- **Total Closed-Mesh Geometric Volume:** `105.74 cm³`
- **STEP-Only Parts (COTS Reference or Unexported STLs):** `Alembic_Toolhead_V201 - 5mmODX3mmID_Alu_Tube.step`, `Alembic_Toolhead_V201 - Belt_Clamp_9mm.step`, `Alembic_Toolhead_V201 - Intake_6mmOD.step`, `Alembic_Toolhead_V201 - NEMA14_.step`, `Alembic_Toolhead_V201 - PC4-M10 Bowden Pass-Through.step`, `Alembic_Toolhead_V201 - Pnuematic_Fitting_6mmOD.step`

## 2. CAD & Mesh Envelope Telemetry

<!-- AUTO-HARDWARE-CAD:START -->
### STL Mesh Envelope & Volume Telemetry

| STL File | Envelope `X × Y × Z (mm)` | Solid Volume (`cm³`) | Triangles | STEP Sync | Doc Ref |
| :--- | :---: | :---: | :---: | :---: | :---: |
| `BD_Mod_Clamp.stl` | `12.00 × 18.00 × 33.80` | `2.19` | `23461` | `MATCH (<=0.2mm)` | `Yes` |
| `Bend_Tool_Base.stl` | `21.00 × 50.00 × 50.00` | `22.88` | `16094` | `MATCH (<=0.2mm)` | `Yes` |
| `Bend_Tool_Lever.stl` | `15.00 × 19.60 × 53.00` | `11.72` | `2904` | `MATCH (<=0.2mm)` | `Yes` |
| `Chainflex_Clamp_Base.stl` | `7.80 × 8.00 × 28.77` | `0.67` | `2226` | `MATCH (<=0.2mm)` | `Yes` |
| `Chainflex_Clamp_Main.stl` | `8.92 × 18.00 × 28.56` | `1.41` | `3944` | `MATCH (<=0.2mm)` | `Yes` |
| `Fan_Baffle_Dragon.stl` | `28.20 × 32.40 × 39.43` | `6.86` | `14818` | `MATCH (<=0.2mm)` | `Yes` |
| `Fan_Baffle_Takoto.stl` | `24.00 × 32.40 × 39.43` | `6.23` | `21496` | `MATCH (<=0.2mm)` | `Yes` |
| `Lower_Body.stl` | `44.00 × 60.58 × 72.20` | `22.68` | `20298` | `MATCH (<=0.2mm)` | `Yes` |
| `Manifold_Frame.stl` | `18.20 × 39.00 × 68.20` | `21.74` | `22040` | `MATCH (<=0.2mm)` | `Yes` |
| `Pnuematic_Strain_Relief.stl` | `11.70 × 47.20 × 48.60` | `8.01` | `8778` | `MATCH (<=0.2mm)` | `Yes` |
| `Sensor_Retainer.stl` | `4.00 × 9.80 × 11.07` | `0.24` | `3148` | `MATCH (<=0.2mm)` | `Yes` |
| `Sensor_Retainer_Dragon-MZE.stl` | `9.00 × 9.80 × 11.07` | `0.50` | `3468` | `MATCH (<=0.2mm)` | `Yes` |
| `Shim_06mm_BDsensor.stl` | `0.60 × 12.00 × 18.41` | `0.10` | `1414` | `MATCH (<=0.2mm)` | `Yes` |
| `Shim_56_BDsensor_Dragon-MZE.stl` | `3.60 × 12.00 × 18.41` | `0.51` | `4056` | `MATCH (<=0.2mm)` | `Yes` |

### STEP Analytic Geometry & Cylindrical Surface Histogram

| STEP File | Export Date | Envelope `X × Y × Z (mm)` | Detected Cylindrical Surfaces `Ø (mm)` × Count |
| :--- | :---: | :---: | :--- |
| `Alembic_Toolhead_V201 - 5mmODX3mmID_Alu_Tube.step` | `2026-04-04` | `5.00 × 5.00 × 50.00` | `Ø3.00mm`×1, `Ø5.00mm`×1 |
| `Alembic_Toolhead_V201 - BD_Mod_Clamp.step` | `2026-04-04` | `12.00 × 18.00 × 33.80` | `Ø3.20mm`×2, `Ø7.00mm`×2, `Ø13.40mm`×2, `Ø2.84mm`×1 |
| `Alembic_Toolhead_V201 - Belt_Clamp_9mm.step` | `2026-04-04` | `10.20 × 10.80 × 14.60` | `Ø2.75mm`×2 |
| `Alembic_Toolhead_V201 - Chainflex_Clamp_Base.step` | `2026-04-04` | `7.80 × 8.00 × 28.77` | `Ø3.20mm`×2, `Ø5.35mm`×1, `Ø10.82mm`×1, `Ø10.93mm`×1, `Ø12.05mm`×1 |
| `Alembic_Toolhead_V201 - Chainflex_Clamp_Main.step` | `2026-04-04` | `8.93 × 18.00 × 28.55` | `Ø3.20mm`×2, `Ø12.05mm`×2, `Ø5.65mm`×1 |
| `Alembic_Toolhead_V201 - Fan_Baffle_Takoto.step` | `2026-04-04` | `24.00 × 32.40 × 39.43` | `Ø6.00mm`×4, `Ø3.00mm`×2, `Ø3.25mm`×2, `Ø3.80mm`×2 |
| `Alembic_Toolhead_V201 - Intake_6mmOD.step` | `2026-04-04` | `17.00 × 20.00 × 57.20` | `Ø3.25mm`×4, `Ø20.00mm`×4, `Ø4.70mm`×2, `Ø6.40mm`×2, `Ø19.60mm`×2 |
| `Alembic_Toolhead_V201 - Lower_Body.step` | `2026-04-04` | `44.00 × 60.58 × 72.20` | `Ø3.00mm`×4, `Ø5.00mm`×4, `Ø2.73mm`×2, `Ø2.90mm`×2, `Ø3.25mm`×2 |
| `Alembic_Toolhead_V201 - Manifold_Frame.step` | `2026-04-04` | `18.20 × 39.00 × 68.20` | `Ø3.00mm`×2, `Ø3.20mm`×2, `Ø3.30mm`×2, `Ø3.35mm`×2, `Ø4.60mm`×2 |
| `Alembic_Toolhead_V201 - NEMA14_.step` | `2026-04-04` | `23.50 × 38.04 × 38.04` | `Ø3.75mm`×10, `Ø6.00mm`×10, `Ø2.00mm`×5, `Ø3.00mm`×3, `Ø7.00mm`×2 |
| `Alembic_Toolhead_V201 - PC4-M10 Bowden Pass-Through.step` | `2026-04-04` | `10.00 × 11.55 × 18.30` | `Ø5.50mm`×2, `Ø10.00mm`×2, `Ø4.50mm`×1, `Ø6.30mm`×1, `Ø9.85mm`×1 |
| `Alembic_Toolhead_V201 - Pnuematic_Fitting_6mmOD.step` | `2026-04-04` | `14.00 × 16.17 × 19.50` | `Ø12.00mm`×2, `Ø4.50mm`×1, `Ø6.00mm`×1, `Ø6.80mm`×1 |
| `Alembic_Toolhead_V201 - Pnuematic_Strain_Relief.step` | `2026-04-04` | `11.70 × 47.20 × 48.60` | `Ø4.70mm`×4, `Ø3.25mm`×2, `Ø20.00mm`×2, `Ø7.50mm`×1 |
| `Alembic_Toolhead_V201 - Sensor_Retainer.step` | `2026-04-04` | `4.00 × 9.80 × 11.05` | `Ø9.80mm`×2, `Ø2.50mm`×1, `Ø5.50mm`×1, `Ø12.20mm`×1 |
| `Alembic_Toolhead_V201 - Shim_06mm_BDsensor.step` | `2026-04-04` | `0.60 × 12.00 × 18.38` | `Ø2.58mm`×1, `Ø5.78mm`×1, `Ø12.00mm`×1 |
| `Bend_Tool_Lever.step` | `2026-04-04` | `15.00 × 19.59 × 53.00` | `Ø19.60mm`×2, `Ø5.20mm`×1 |
| `Fan_Baffle_Dragon.step` | `2026-04-13` | `28.20 × 32.40 × 39.43` | `Ø6.00mm`×4, `Ø3.00mm`×2, `Ø3.25mm`×2, `Ø22.20mm`×2, `Ø2.00mm`×1 |
| `Part Studio 1 - Bend_Tool_Base.step` | `2026-04-04` | `21.00 × 49.98 × 49.99` | `Ø5.30mm`×1 |
| `Sensor_Retainer_Dragon-MZE.step` | `2026-04-13` | `9.00 × 9.80 × 11.05` | `Ø9.80mm`×2, `Ø2.50mm`×1, `Ø5.50mm`×1, `Ø12.20mm`×1 |
| `Shim_56_BDsensor_Dragon-MZE.step` | `2026-04-13` | `3.60 × 12.00 × 18.38` | `Ø2.58mm`×1, `Ø5.20mm`×1, `Ø5.78mm`×1, `Ø12.00mm`×1 |
<!-- AUTO-HARDWARE-CAD:END -->

## 3. Firmware & Pinout Telemetry

<!-- AUTO-HARDWARE-CFG:START -->
| `_none_` | `_None_` | `_None_` | `_None_` |
<!-- AUTO-HARDWARE-CFG:END -->

## 4. Verified Fasteners, Inserts & BOM Schedule
- Populate verified hardware counts from authoritative assembly sources (`verify_claims.py` whitelist).
