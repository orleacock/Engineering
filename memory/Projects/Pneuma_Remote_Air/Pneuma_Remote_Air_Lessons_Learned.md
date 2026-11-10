---
project: "Pneuma_Remote_Air"
parent_note: "Pneuma_Remote_Air"
entity: "Alchemical-3D"
compartment: "public"
note_type: "lessons_learned"
last_synced: "2026-11-10"
---

# 🧠 Pneuma Remote Air — Engineering Lessons Learned & Post-Mortem Ledger (`Pneuma_Remote_Air_Lessons_Learned`)

Part of the [`README.md`](../../README.md) and project-scoped troubleshooting ledger for [`Pneuma_Remote_Air`](Pneuma_Remote_Air.md) and [`Pneuma_Remote_Air_Hardware`](Pneuma_Remote_Air_Hardware.md).

> [!IMPORTANT]
> **Containment, Failed-Attempt Quarantine & Role Separation**
> 1. **Failed-Attempt Quarantine (`verify_claims.py` Auto-Exclusion):** Automatically excluded (`excluded_lessons_learned_sources`) when scanning `--sources`. Canonical specifications and active `Mode B1` assembly rules live in [`Pneuma_Remote_Air`](Pneuma_Remote_Air.md), [`Pneuma_Remote_Air_Hardware`](Pneuma_Remote_Air_Hardware.md), and `Firmware/Pneuma_Control.cfg`.
> 2. **Role Separation:** Active `Open [TBD]` items are tracked exclusively in [`Pneuma_Remote_Air`](Pneuma_Remote_Air.md) (`## 🔍 Provenance Status & Open [TBD] / [CONFLICT] Ledger`). This file records **only** historical post-mortems, retired architectures, subsystem design invariants, and coupled interface root causes.

---

## 0. Subsystem Design Invariants & Anti-Bloat Matrix (`Sectional Rebuild Reference`)

<!-- SUBSYSTEM-INVARIANTS:START -->
| Subsystem / Asset | Must-Keep Design Invariants (`Chesterton's Fence`) | Retired Assumptions / Anti-Patterns (`Never Re-Introduce`) | Canonical Source & Governing `LL-IDs` |
| :--- | :--- | :--- | :--- |
| **Dual-Pump Architecture & Pneumatic Routing (`Firmware/Pneuma_Control.cfg`, `BOM.md`)** | Dual-pump regime (`pump_cool` on `PF7` + `pump_warm` on `PF9`, `cycle_time: 0.03`); `6mm OD` umbilical tubing (`2 meters` in `BOM.md`); Teflon tape on pressure-side `1-8-NPT` threads (`>= 70 kPa`). | Assuming a single pump with a pilot-assisted `1-8-NPT` solenoid valve can blend ambient/chamber air or actuate under low pressure differential; guessing pump voltage (`12V` vs. `24V`) or wattage when unlisted in repo docs. | [`Pneuma_Remote_Air.md`](Pneuma_Remote_Air.md), [`Pneuma_Remote_Air_Hardware.md`](Pneuma_Remote_Air_Hardware.md) (`LL-PNE-01`, `LL-PNE-02`, `LL-PNE-04`, `LL-PNE-09`) |
| **Enclosure & Snap-Fit Covers (`Main_Body.stl`, `Rear_Cover.stl`, `Pump_Top_Cover.stl`, `Filter_Top_Cover.stl`)** | `Rear_Cover.stl` attaches via `5` `M3x5x4` brass heat-set inserts + `5` `M3x8 SHCS` (`BOM.md:6-10`, `Assembly_Guide.md:30,78`). `Pump_Top_Cover.stl` and `Filter_Top_Cover.stl` are toolless snap-fit / press-fit covers (`Assembly_Guide.md:61,66`). | Misinterpreting `16 × R1.50mm` open partial-arc snap-fit relief grooves on `Pump_Top_Cover.stl` / `Filter_Top_Cover.stl` as closed `Ø3.00mm` (`360°`) M3 fastener holes (`16x M3 screws` hallucination). | [`Pneuma_Remote_Air.md`](Pneuma_Remote_Air.md), [`Pneuma_Remote_Air_Hardware.md`](Pneuma_Remote_Air_Hardware.md) (`LL-PNE-05`, `LL-PNE-06`) |
| **COTS Packaging & Port Geometry (`CAD/Pneuma_Remote_Air.step`, `STL/*.stl`)** | `Main_Body.stl` has `8` total `Ø4.70mm` heat-set pockets (`5` rear cover + `2` table mount + `1` auxiliary boss) and `5 × Ø12.00mm` grommet pass-through ports (`4` top + `1` bottom). `Vacuum_Pump.stl` is a `2`-body COTS reference model (`90.10 × 124.22 × 65.50 mm`). | Treating `Vacuum_Pump.stl` (`334.62 cm³`) as a printable part (`Assembly_Guide.md:20`); assuming `Tube_Fitting.stl` exists in `STL/` (`Assembly_Guide.md:54`); or assuming `6` `Ø12.00mm` ports exist in `Main_Body.stl` just because `BOM.md` lists `6` `TPU_Grommet.stl`. | [`Pneuma_Remote_Air_Hardware.md`](Pneuma_Remote_Air_Hardware.md) (`LL-PNE-06`, `LL-PNE-07`, `LL-PNE-08`) |
| **Polymer Separation (`Print_Settings.md`)** | Structural enclosure parts (`Main_Body`, `Rear_Cover`, `Pump_Top_Cover`, `Filter_Top_Cover`, `Table_Mount`) use `ABS`/`ASA` (`4` walls, `5` top/bottom layers, `40%` `Grid`/`Gyroid` infill, `0.2mm` layers). | Borrowing `40%` structural `ABS`/`ASA` infill/walls onto the `3` `TPU` elastomer vibration-isolation parts (`TPU_Grommet.stl`, `Table_Mount_TPU.stl`, `Plug_Grommet_TPU.stl`) or inventing Shore hardness (`95A`/`85A`). | [`Pneuma_Remote_Air.md`](Pneuma_Remote_Air.md) (`LL-PNE-03`) |
| **Pneuma_Control.cfg, README.md** | Part-cooling diaphragm pumps use shutdown_speed: 0 in Pneuma_Control.cfg while hotend heatsink fans ([heater_fan]) remain shutdown_speed: 1 to prevent heat creep | shutdown_speed: 1 on pump_cool and pump_warm in Firmware/Pneuma_Control.cfg | `Firmware/Pneuma_Control.cfg` ([`Pneuma_Remote_Air_Hardware.md`](Pneuma_Remote_Air_Hardware.md)), `README.md` ([`Pneuma_Remote_Air.md`](Pneuma_Remote_Air.md)) (`LL-PNE-04`) |
| **Print_Settings.md, BOM.md, Assembly_Guide.md** | Separate structural ABS/ASA/PETG slicer parameters from TPU vibration-isolation elastomer parts and Dual-Pump BOM/Assembly tables | Single-table structural slicer settings without TPU separation or legacy 1/8-NPT solenoid primary BOM rows | `Print_Settings.md` ([`Pneuma_Remote_Air.md`](Pneuma_Remote_Air.md)), `BOM.md` ([`Pneuma_Remote_Air.md`](Pneuma_Remote_Air.md)), `Assembly_Guide.md` ([`Pneuma_Remote_Air.md`](Pneuma_Remote_Air.md)) (`LL-PNE-03`) |
<!-- SUBSYSTEM-INVARIANTS:END -->

---

## 1. Engineering Post-Mortems & Troubleshooting Entries

### `LL-PNE-02` [TIER2] — Coupled 6mm OD Umbilical & Pressure-Side Sealing (`Alembic_Toolhead` Coupled)
- **Symptom / Failed Approach (`Historical / Rejected`):** Line-pressure drop at threaded fittings (`>= 70 kPa`), acoustic/air gaps between `Rear_Cover` and `Main_Body`, or choked airflow reaching [`Alembic_Toolhead`](../Alembic_Toolhead/Alembic_Toolhead.md).
- **Root Cause:** Protruding `M3x5x4mm` brass heat-set inserts hold `Rear_Cover` proud of `Main_Body`; unsealed pressure-side NPT threads leak positive pressure; tight bend radii kink the `6mm OD` umbilical line.
- **Verified Resolution & Canonical Owner:** Seat all `M3x5x4mm` inserts strictly flush, wrap Teflon tape on pressure-side threads, and route the `6mm OD` umbilical with generous sweep radii ([`Pneuma_Remote_Air`](Pneuma_Remote_Air.md)).
- **Shared Interface Link:** Coupled with [`Alembic_Toolhead_Lessons_Learned`](../Alembic_Toolhead/Alembic_Toolhead_Lessons_Learned.md).

### `LL-PNE-03` [TIER2] — Anti-Cross-Entity Polymer Borrowing (`TPU` Vibration Isolators vs. `ABS/ASA` Enclosure)
- **Symptom / Failed Approach (`Historical / Rejected`):** Copying structural `ABS`/`ASA` print settings (`4` walls, `5` top/bottom layers, `40%` `Grid`/`Gyroid` infill) onto the three elastomer vibration-isolation parts (`TPU_Grommet.stl`, `Table_Mount_TPU.stl`, `Plug_Grommet_TPU.stl`) or inventing TPU Shore hardness from pretraining defaults.
- **Root Cause:** Borrowing `40%` structural infill onto TPU makes vibration isolators rigid and transmits pump resonance directly into the frame/table.
- **Verified Resolution & Canonical Owner:** Graduated into [`Verifiable_Accuracy_and_Anti_Hallucination`](../../Standards_and_Specs/Verifiable_Accuracy_and_Anti_Hallucination.md) (`Ban Cross-Entity Borrowing`); TPU parameters remain quarantined as an explicit `[TBD]` in [`Pneuma_Remote_Air`](Pneuma_Remote_Air.md) until measured.

### `LL-PNE-04` [TIER2] — Klipper `shutdown_speed: 1` Emergency-Stop Full-Blast Hazard & `#kick_start_time: 0.5` Stall Hazard
- **Symptom / Failed Approach (`Historical / Rejected`):** In `Firmware/Pneuma_Control.cfg:6,17`, both `[fan_generic pump_cool]` and `[fan_generic pump_warm]` define `shutdown_speed: 1` (100% duty cycle on MCU fault/emergency stop) and comment out `#kick_start_time: 0.5` (`Firmware/Pneuma_Control.cfg:8,19`).
- **Root Cause:** `shutdown_speed: 1` forces both diaphragm air pumps to run at 100% power during a Klipper MCU shutdown or thermal runaway fault (potentially feeding air to a faulted hotend/chamber), while commenting out `kick_start_time: 0.5` risks diaphragm motor stall when starting at low PWM duty cycles (`M106 S<low>`).
- **Verified Resolution & Canonical Owner:** Flagged as a mandatory firmware safety audit item in [`Pneuma_Remote_Air`](Pneuma_Remote_Air.md) and [`Pneuma_Remote_Air_Hardware`](Pneuma_Remote_Air_Hardware.md) (`shutdown_speed: 0.0` recommended for fail-safe de-energization unless intentional purge behavior is desired; uncomment `kick_start_time: 0.5` if low-PWM stall occurs).

### `LL-PNE-06` [TIER2] — `Main_Body.stl` `8` Heat-Set Insert Pockets vs. `BOM.md` `5 + 2` Insert Allocation
- **Symptom / Failed Approach (`Historical / Rejected`):** Assuming `Main_Body.stl` contains only `5` or `7` `Ø4.70mm` (`R2.35mm`) heat-set insert pockets based solely on `BOM.md:6,12` (`5` Rear Cover + `2` Optional Table Mount = `7` inserts).
- **Root Cause:** `Main_Body.stl` physically contains `8` `Ø4.70mm` heat-set insert pockets (`5` on the rear cover flange at `X = -65.00mm`, `2` on the bottom table-mount bosses at `Y = -58.50mm`, plus `1` unindexed auxiliary boss at `(21.0, 2.0, -32.2)`). Additionally, `BOM.md:6,12` lists `2` optional table-mount inserts (`Main Body (Optional)`) but `0` corresponding M3 mounting screws.
- **Verified Resolution & Canonical Owner:** Documented in [`Pneuma_Remote_Air`](Pneuma_Remote_Air.md)'s `Open [TBD] / [CONFLICT] Ledger` (`[TBD: table_mount_m3_screw_length_and_8th_insert_boss]`) so builders and auditors neither under-count the physical pockets nor invent an unverified screw length.

### `LL-PNE-07` [TIER2] — `Vacuum_Pump.stl` COTS Reference Model in `STL/` & `1.00mm` X-Axis STEP/STL Drift
- **Symptom / Failed Approach (`Historical / Rejected`):** Instructing users in `Assembly_Guide.md:20` to *"Print all parts in the STL folder"* without excluding `Vacuum_Pump.stl`, or assuming `100%` dimensional identity between `CAD/Pneuma_Remote_Air.step` and `STL/Vacuum_Pump.stl`.
- **Root Cause:** `STL/Vacuum_Pump.stl` (`90.10 × 124.22 × 65.50 mm`, `2` bodies, `334.62 cm³`) is a COTS reference model of the two internal diaphragm pumps (`Pump v1` + `Pump v1(1)`), not a printable structural housing part. Furthermore, the STEP assembly positions the pump pair across `91.10 × 124.22 × 65.50 mm` (`1.00mm` X-axis spacing offset vs. the exported STL).
- **Verified Resolution & Canonical Owner:** Explicitly segregated `Vacuum_Pump.stl` as a non-printed COTS reference model in [`Pneuma_Remote_Air`](Pneuma_Remote_Air.md) and [`Pneuma_Remote_Air_Hardware`](Pneuma_Remote_Air_Hardware.md).

### `LL-PNE-08` [TIER2] — Phantom `Tube_Fitting.stl` Reference & `5 × Ø12.00mm` Ports vs. `6` `TPU_Grommet` BOM Count
- **Symptom / Failed Approach (`Historical / Rejected`):** Referencing `Tube_Fitting.stl` as an existing file in `STL/` (`Assembly_Guide.md:54`) or claiming `Main_Body.stl` has `6` `Ø12.00mm` ports to match the `6` `TPU_Grommet.stl` listed in `BOM.md:22`.
- **Root Cause:** `Tube_Fitting.stl` is cited in `Assembly_Guide.md:54` (`> [!WARNING]`) for builds without `1-8-NPT` threaded fittings, but no `Tube_Fitting.stl` exists in `STL/` or `CAD/Pneuma_Remote_Air.step`. Meanwhile, `Main_Body.stl` has `5 × Ø12.00mm` (`R6.00mm`) pass-through ports (`4` top + `1` bottom) alongside `1 × Ø17.50mm` rear cable port (`Plug_Grommet_TPU.stl`), meaning the `6th` `TPU_Grommet.stl` in `BOM.md:22` is a spare (`5` active ports).
- **Verified Resolution & Canonical Owner:** Tracked in [`Pneuma_Remote_Air`](Pneuma_Remote_Air.md) (`[TBD: missing_Tube_Fitting_stl_and_grommet_port_count]`) and [`Pneuma_Remote_Air_Hardware`](Pneuma_Remote_Air_Hardware.md).

### `LL-PNE-09` [TIER2] — Multi-Pump Klipper `[gcode_macro M106]` `P<index>` Indexing Limitation
- **Symptom / Failed Approach (`Historical / Rejected`):** Assuming the stock `[gcode_macro M106]` in `Firmware/Pneuma_Control.cfg:22-30` supports independent slicer `M106 P<index> S<value>` addressing for `pump_cool` vs. `pump_warm`.
- **Root Cause:** The stock `[gcode_macro M106]` checks only `params.S` (`SET_FAN_SPEED FAN=pump_cool SPEED={s}`) and leaves `SET_FAN_SPEED FAN=pump_warm` commented out (`#`), ignoring `params.P`.
- **Verified Resolution & Canonical Owner:** Documented in [`Pneuma_Remote_Air`](Pneuma_Remote_Air.md) and [`Pneuma_Remote_Air_Hardware`](Pneuma_Remote_Air_Hardware.md) so multi-fan slicer configurations (`M106 P2`/`P3` or thermal regime macros) explicitly bind `params.P` or separate fan macros rather than silently driving only `pump_cool`.
