---
project: "Pestle_Rotational_Bowden"
entity: "Alchemical-3D"
compartment: "public"
project_type: "hardware"
status: "Beta"
local_path: "/home/orin/Projects/Alchemical3D/Pestle_Rotational_Bowden"
repo_head_sha: "7197d2bed1fd"
tree_hash: "ac67baacbab6"
checkpoint_head_sha: "7197d2bed1fd"
checkpoint_tree_hash: "3a96e1b5aa29"
checkpoint_worktree: "clean"
task_umbrella: "../../Tasks/Alchemical-3D_Tasks.md"
last_synced: "2026-11-17"
checkpoint_lessons_digest: "fc97389b91340449"
---

## 🧭 Homunculus Companion Notes & Project Navigation

| Artifact Role | File Link | Purpose |
| :--- | :--- | :--- |
| **Project Hub (`AUTO-TREE`)** | [`Pestle_Rotational_Bowden.md`](Pestle_Rotational_Bowden.md) | Canonical architecture overview, `SESSION-HANDOFF`, `AUTO-TREE`, and `[TBD]` Ledger. |
| **Hardware Telemetry** | [`Pestle_Rotational_Bowden_Hardware.md`](Pestle_Rotational_Bowden_Hardware.md) | CAD bounding boxes, cylindrical bore histograms, and firmware pinouts. |
| **Lessons Learned & Post-Mortems** | [`Pestle_Rotational_Bowden_Lessons_Learned.md`](Pestle_Rotational_Bowden_Lessons_Learned.md) | Root-cause post-mortems (`Symptom -> Root Cause -> Permanent Guardrail`). |
| **Unverified Quarantine Zone** | [`Quarantine/Quarantine_README.md`](Quarantine/Quarantine_README.md) | Holding zone for unverified notes (`[QUARANTINED — DO NOT CITE AS FACT]`). |
| **Active Task Umbrella** | [`Alchemical-3D_Tasks.md`](../../Tasks/Alchemical-3D_Tasks.md#Pestle_Rotational_Bowden) | Single-writer task tracker for `Alchemical-3D` (zero duplicate checkboxes in hub). |

---

# 🥣 Pestle Rotational Bowden (`Rev 1.2` Beta)

Part of the [`README.md`](../../README.md) • CAD Telemetry: [`Pestle_Rotational_Bowden_Hardware`](Pestle_Rotational_Bowden_Hardware.md)

## 🔒 Concept & Design Philosophy ("Why")
- **Direct-Drive Precision Without Toolhead Mass (`README.md:21-30`):** Mounts an ultra-compact `BMG` + `NEMA 14` pancake extruder on a thrust-bearing swivel pivot (`F5-12M`) riding the X gantry or 2020 extrusion (`pestle_2020_extrusion_mount.stl`) so the extruder dynamically rotates to point straight at the moving toolhead (inspired by the Voron Jetpack).
- **>50% Shorter Bowden Path & Straight-Line Trajectory (`README.md:25-28,134-140`):** Cuts PTFE Bowden length from `~508mm` down to `< 228.6mm` while eliminating tight S-bend drag, achieving near-direct-drive retractions (`0.95mm @ 40mm/s`) and low Pressure Advance (`0.280`) while keeping stepper/extruder mass off [`Alembic_Toolhead`](../../Projects/Alembic_Toolhead/Alembic_Toolhead.md).

## 📍 Repository & File Inventory
- **Local Path:** `/home/orin/Projects/Alchemical3D/Pestle_Rotational_Bowden`
- **GitHub Remote:** `https://github.com/Alchemical-3D/Pestle_Rotational_Bowden`
- **Living Documentation:** `README.md` *(user-approved Monolithic format with Print Settings, `7`-STL + STEP CAD index, Affiliate Disclosure, Reconciled BOM + Assembly Steps `1`–`14`, GPLv3 License, Ko-fi/Discord & AI Transparency Footer)*, `LICENSE.md` (`GPLv3`)
- **CAD & Image Directories:** `Releases/1.2/` (`1` assembly STEP `Pestle_Rev-1.2.step`, `7` STLs), `images/` — Full geometry telemetry in [`Pestle_Rotational_Bowden_Hardware`](Pestle_Rotational_Bowden_Hardware.md)
- **Standards Applied:** [`Verifiable_Accuracy_and_Anti_Hallucination`](../../Standards_and_Specs/Verifiable_Accuracy_and_Anti_Hallucination.md), `Author_Voice_and_Cadence`, [`Fasteners_and_Inserts`](../../Standards_and_Specs/Fasteners_and_Inserts.md), `Image_and_Style_Rules`, `Subagent_and_Memory_Architecture`

<!-- AUTO-TREE:START -->
```text
Repository: Pestle_Rotational_Bowden | HEAD SHA: 7197d2bed1fd | Tree Hash: ac67baacbab6
  images/
  images/Pestle1.png
  images/Pestle2.png
  images/Pestle3.png
  images/Pestle4.png
  images/Pestle_Title_Formatted.png
  images/PestleExploded1.png
  images/PestleExploded2.png
  images/PestleExploded3.png
  images/PestleExploded3_Formatted.png
  images/PestleExploded4.png
  images/PestleExploded5.png
  Releases/
  Releases/1.2/
  Releases/1.2/CAD/
  Releases/1.2/CAD/Pestle_Rev-1.2.step
  Releases/1.2/STLs/
  Releases/1.2/STLs/[a]_pestle_lever.stl
  Releases/1.2/STLs/[a]_pestle_rotation_brace.stl
  Releases/1.2/STLs/pestle_2020_extrusion_mount.stl
  Releases/1.2/STLs/pestle_3DFused_gantry_mount.stl
  Releases/1.2/STLs/pestle_main_body.stl
  Releases/1.2/STLs/pestle_motor_plate.stl
  Releases/1.2/STLs/pestle_top_plate.stl
  Releases/1.2/STLs/README.md
  .gitignore
  LICENSE.md
  README.md
```
<!-- AUTO-TREE:END -->

## ⚠️ Paramount Assembly Hazards & Mechanical "Whys" (`Mode B1` Anchors)
- **Bottom-Flush Lever Pivot Heat-Set Insertion (`README.md:101-103`):** The `M3x5x4mm` heat-set insert inside `pestle_main_body.stl` that retains `[a]_pestle_lever.stl` **must be pressed in from the bottom of the main body and seated strictly flush with the bottom face**; top-side or proud insertion binds lever travel and prevents gear meshing.
- **Support-Arm Shear Protection During `PC4-M6` Press-Fit (`README.md:104`):** Brace a wrench flat between the support-arm uprights against a table when pressing the embedded `PC4-M6` Bowden collar; pressing unbraced or off-axis snaps the printed arm.
- **Lower Bracket Fracture During Thumbscrew Spring Compression (`README.md:112`):** Compress the BMG tension thumbscrew spring directly against the lever—never pry or react load against the lower main-body support ears, which will snap under bending load.
- **Anaerobic Threadlocker Chemical Hazard (`README.md:80-82`, [`Fasteners_and_Inserts`](../../Standards_and_Specs/Fasteners_and_Inserts.md)):** Keep `Loctite 243` / `222MS` strictly off `ABS`/`ASA` printed parts to prevent chemical cracking.

## 📐 Verified Specs, COTS Hardware & Print Matrix
- **CAD Telemetry ([`Pestle_Rotational_Bowden_Hardware`](Pestle_Rotational_Bowden_Hardware.md)):** `1` assembly STEP (`Pestle_Rev-1.2.step`, `81.59 × 115.87 × 127.63 mm`) | `7` STLs (`IN_ASSEMBLY_STEP` synced) | Total closed-mesh geometric volume `61.25 cm³`:
  - Core extruder STLs: `pestle_main_body.stl` (`15.77 cm³`), `[a]_pestle_lever.stl` (`4.38 cm³`), `[a]_pestle_rotation_brace.stl` (`3.86 cm³`), `pestle_motor_plate.stl` (`5.66 cm³`), `pestle_top_plate.stl` (`4.60 cm³`).
  - Mounting option STLs: `pestle_2020_extrusion_mount.stl` (`15.22 cm³`), `pestle_3DFused_gantry_mount.stl` (`11.76 cm³`).
- **Verified Drive & Bearing COTS (`README.md:66,73-75`):** `BondTech BMG` internals kit (`50T` `5mm` primary gear, secondary drive gear/needle bearings, `MR85ZZ` bearings, tension thumbscrew/spring); `LDO` `NEMA 14` pancake stepper (`36STH20-1004AHG-9T`); `F5-12M` axial thrust bearing (`5mm ID x 12mm OD x 4mm`); `(3)` embedded `PC4-M6` Bowden collets; `(1)` `M5` hex nut.
- **Verified Print Matrix & Tuning Baseline (`README.md:43-52,134-140`):**
  - Slicer: `ABS` or `ASA` (pre-scaled for ABS/ASA shrinkage; `PLA`/`PETG` prohibited due to stepper/chamber heat) | `0.20mm` layer height | forced `0.40mm` extrusion width | `4` wall perimeters | `5` top / `5` bottom layers | `40%` minimum infill (`Grid`, `Honeycomb`, `Triangle`, `Cubic`) | `0` supports.
  - Klipper / Slicer Baseline: Retraction `0.95 mm` @ `40 mm/s` (`45 mm/s` detraction) | Pressure Advance `0.280` (`0.035` smooth time).

## 🔗 Companion Projects & Kinematic / System Links
- [`Alembic_Toolhead`](../../Projects/Alembic_Toolhead/Alembic_Toolhead.md) — Ultra-light compressed-air toolhead fed by Pestle's `< 228.6mm` straight-line Bowden tube.
- [`Alchemical_Web_Docs`](../../Projects/Alchemical_Web_Docs/Alchemical_Web_Docs.md) — Web showcase page at `docs/pestle.md`.

## 🔍 Provenance Status & Open [TBD] / [CONFLICT] Ledger
> [!WARNING]
> Figures inside this ledger are quarantined by `verify_claims.py` and are **not** treated as authorized source truth until resolved.

- **Git & Provenance Baseline (`2026-11-17`):** `main:clean` at commit `7197d2b` (`bac7c2d..7197d2b` pushed to `origin/main`; `verify_claims.py --fail-on-tbd`: `74/74 PASS`, `VRF-fb1fbd62965b`, `0` unbacked, `0` `[TBD]`; `audit_repo_docs.py`: `0` load-bearing issues, `3` expected monolithic-structure warnings; `audit_data_boundary.py --staged`: `BOUNDARY_CLEAN`; `format_image.py --inspect`: `2/2 [PASS]` `#FFFFFF` card spec).
- **Resolved Conflicts (`2026-11-17` Operator Verification):** (1) Corrected `M3x5x4` heat-set BOM `7` $\rightarrow$ `6` (`3` Main Body, `1` Lever, `2` Transmission Plate); (2) standardized BOM & Assembly Steps `10`–`11` on `SHCS` and retained `(1) M3x16mm` + `(1) M3x20mm SHCS` as stack-depth sub-assembly screws; (3) confirmed `(1) F5-12M` thrust bearing at Step `12` with optional shim washers under the `M5` bolt head at Step `10`; (4) documented all `7` STLs (`Releases/1.2/STLs/`) + `Pestle_Rev-1.2.step` in `README.md`.
- **Open `[TBD]` Items:** `None` (`0` open `[TBD]`s).

## 🎯 Active Tasks
*(Transcluded live from `### Pestle_Rotational_Bowden` in [`Alchemical3D_Tasks`](../../Tasks/Alchemical-3D_Tasks.md))*

> **Active Task Queue**: Tracked in [`Alchemical3D_Tasks`](../../Tasks/Alchemical-3D_Tasks.md#Pestle_Rotational_Bowden) *(Single-Writer Task Umbrella)*.

## 🚀 Session Handoff & Multi-Session Kickstart (`SESSION-HANDOFF`)
<!-- SESSION-HANDOFF:START -->
- **Last Session Timestamp**: `2026-11-17`
- **Checkpoint Provenance**: `HEAD SHA: 7197d2bed1fd` | `Tree Hash: 3a96e1b5aa29` | `Worktree: clean` | `Last Verification: verify_claims:74/74-PASS (VRF-fb1fbd62965b), audit_repo_docs:0-load-bearing, BOUNDARY_CLEAN`
- **Where We Stopped (Verified State & Context)**:
  Resolved all 4 hardware/fastener/STL conflicts with operator confirmation, unified monolithic `README.md`, committed (`7197d2b`), and pushed `bac7c2d..7197d2b` (`main -> main`) to `origin/main`.
- **Active Project State Ledger & Blockers**: `None` (`0` open tasks, `0` open `[TBD]`s)
- **Next Session Kickstart & Discussion Points**:
  1. `Pestle_Rotational_Bowden` is clean and synced on `origin/main` (`7197d2b`); no open tasks remain.
<!-- SESSION-HANDOFF:END -->
