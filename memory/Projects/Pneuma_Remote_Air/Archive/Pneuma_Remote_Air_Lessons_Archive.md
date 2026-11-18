---
project: "Pneuma_Remote_Air"
parent_note: "Pneuma_Remote_Air_Lessons_Learned"
entity: "Alchemical-3D"
compartment: "public"
note_type: "lessons_archive"
authoritative: false
last_synced: "2026-11-18"
---

# 🗄️ Pneuma_Remote_Air — Graduated & Historical Lessons Archive (`TIER3`–`TIER5`)

> **Single-Source Tiered Archive**: Companion to [`Pneuma_Remote_Air_Lessons_Learned.md`](../Pneuma_Remote_Air_Lessons_Learned.md). Stores full-context narratives for stabilized `TIER3`, isolated-polish `TIER4`, and retired `TIER5` lessons so the active `<Project>_Lessons_Learned.md` window stays compact (`<= 3 TIER0 + <= 7 TIER2` sections). Query any entry on demand via `sync_memory.py --project Pneuma_Remote_Air --lesson-id <LL-xxx>` or promote back to active memory via `--set-tier <LL-xxx> TIER2`.

---

## 1. Archived Full-Context Post-Mortems (`TIER3`–`TIER5`)

### `LL-PNE-01` [TIER5] — Why Pneuma Evolved from Single-Pump Solenoid Diversion to Dual-Pump Thermal Regimes
- **Retirement Provenance (`TIER5` — `2026-11-09`):** Demoted from active governance because the v1 single-pump `1-8-NPT` pilot-operated solenoid diversion prototype was permanently abandoned in favor of the dual-pump architecture (`[fan_generic pump_cool]` on `PF7` + `[fan_generic pump_warm]` on `PF9` in `Firmware/Pneuma_Control.cfg`). Preserved for historical design rationale (`--include-tier5`); active dual-pump truth and remaining `README.md` doc-sync items are governed by [`Pneuma_Remote_Air.md`](../Pneuma_Remote_Air.md).
- **Symptom / Failed Approach (`Historical / Rejected`):** Early Pneuma prototypes used a single air pump paired with a standard pressure-assisted `1-8-NPT` solenoid diversion valve, which failed to actuate reliably under vacuum or low pressure differentials and could not independently blend ambient vs. chamber air.
- **Root Cause:** Pilot-operated solenoid valves rely on line pressure differential to shift the internal diaphragm and stall when switching intake vacuum or low-backpressure exhaust. More fundamentally, a single pump cannot independently modulate ambient room air (`pump_cool` for PLA overhangs) vs. heated chamber air (`pump_warm` for `ABS`/`ASA` bridges without thermal shock/delamination).
- **Verified Resolution & Canonical Owner:** Upgraded to two independent pumps driven by Klipper `[fan_generic pump_cool]` (`pin: PF7`) and `[fan_generic pump_warm]` (`pin: PF9`) in `Firmware/Pneuma_Control.cfg` ([`Pneuma_Remote_Air`](../Pneuma_Remote_Air.md)). Legacy single-pump builds require a direct-acting `1-8-NPT` valve; the remaining doc sync between `README.md` and `BOM.md`/`Assembly_Guide.md` is tracked in [`Pneuma_Remote_Air`](../Pneuma_Remote_Air.md)'s `Open [TBD] Ledger`.

### `LL-PNE-05` [TIER3] — Open `R1.50mm` Snap-Fit Relief Grooves vs. Closed `Ø3.00mm` Fastener Holes
- **Symptom / Failed Approach (`Historical / Rejected`):** Naively grepping `CYLINDRICAL_SURFACE(..., 1.5)` in `CAD/Pneuma_Remote_Air.step` and claiming `Pump_Top_Cover.stl` and `Filter_Top_Cover.stl` are fastened by `16 × M3` screws (`8` per cover).
- **Root Cause:** In B-Rep STEP geometry, both a closed `360°` M3 through-hole (`Ø3.00mm`) and a partial-arc `R1.50mm` fillet or snap-fit relief groove use `CYLINDRICAL_SURFACE(..., 1.5)`. The `8` `R1.50mm` surfaces per top cover are open partial-arc snap-fit/press-fit relief grooves/lips (`Assembly_Guide.md:61,66`), not closed bolt holes.
- **Verified Resolution & Canonical Owner:** Graduated into the CAD Epistemic Boundary (`ZERO_ADHOC_CAD_PARSING`): raw CAD geometry is never parsed ad-hoc to invent fastener counts or mating topology; top covers are documented strictly per `Assembly_Guide.md:61,66` as toolless snap-fit / press-fit covers ([`Pneuma_Remote_Air_Hardware`](../Pneuma_Remote_Air_Hardware.md)).

### `LL-PNE-02` [TIER3] — Coupled 6mm OD Umbilical & Pressure-Side Sealing (`Alembic_Toolhead` Coupled)
- **Symptom / Failed Approach (`Historical / Rejected`):** Line-pressure drop at threaded fittings (`>= 70 kPa`), acoustic/air gaps between `Rear_Cover` and `Main_Body`, or choked airflow reaching [`Alembic_Toolhead`](../../Alembic_Toolhead/Alembic_Toolhead.md).
- **Root Cause:** Protruding `M3x5x4mm` brass heat-set inserts hold `Rear_Cover` proud of `Main_Body`; unsealed pressure-side NPT threads leak positive pressure; tight bend radii kink the `6mm OD` umbilical line.
- **Verified Resolution & Canonical Owner:** Seat all `M3x5x4mm` inserts strictly flush, wrap Teflon tape on pressure-side threads, and route the `6mm OD` umbilical with generous sweep radii ([`Pneuma_Remote_Air`](../Pneuma_Remote_Air.md)).
- **Shared Interface Link:** Coupled with [`Alembic_Toolhead_Lessons_Learned`](../../Alembic_Toolhead/Alembic_Toolhead_Lessons_Learned.md).

### `LL-PNE-03` [TIER3] — Anti-Cross-Entity Polymer Borrowing (`TPU` Vibration Isolators vs. `ABS/ASA` Enclosure)
- **Symptom / Failed Approach (`Historical / Rejected`):** Copying structural `ABS`/`ASA` print settings (`4` walls, `5` top/bottom layers, `40%` `Grid`/`Gyroid` infill) onto the three elastomer vibration-isolation parts (`TPU_Grommet.stl`, `Table_Mount_TPU.stl`, `Plug_Grommet_TPU.stl`) or inventing TPU Shore hardness from pretraining defaults.
- **Root Cause:** Borrowing `40%` structural infill onto TPU makes vibration isolators rigid and transmits pump resonance directly into the frame/table.
- **Verified Resolution & Canonical Owner:** Graduated into [`Verifiable_Accuracy_and_Anti_Hallucination`](../../../Standards_and_Specs/Verifiable_Accuracy_and_Anti_Hallucination.md) (`Ban Cross-Entity Borrowing`); TPU parameters remain quarantined as an explicit `[TBD]` in [`Pneuma_Remote_Air`](../Pneuma_Remote_Air.md) until measured.

### `LL-PNE-04` [TIER5] — Klipper `shutdown_speed: 1` Emergency-Stop Full-Blast Hazard (Resolved in `0702c9c`)
- **Retirement Provenance (`TIER5` — `2026-11-18`):** Superseded by `LL-PNE-10` — Move historical shutdown_speed=1 reference into inert Historical Context so live guardrail matches Firmware/Pneuma_Control.cfg#L18 (shutdown_speed: 0)
- **Superseded-By:** `LL-PNE-10`
- **Symptom / Failed Approach (`Historical / Rejected`):** Previously, `Firmware/Pneuma_Control.cfg` defined `shutdown_speed: 1` on both `[fan_generic pump_cool]` and `[fan_generic pump_warm]` while commenting out `#kick_start_time: 0.5`.
- **Root Cause:** `shutdown_speed: 1` forced both diaphragm pumps to run at 100% duty cycle on Klipper MCU shutdown or thermal fault, while inactive `kick_start_time` risked low-PWM startup stalls.
- **Verified Resolution & Canonical Owner:** Resolved in commit `0702c9c` (`Firmware/Pneuma_Control.cfg` updated to `shutdown_speed: 0` on `pump_cool` and `pump_warm`, retaining `shutdown_speed: 1` solely on `[heater_fan]` hotend heatsink fans; [`Pneuma_Remote_Air`](../Pneuma_Remote_Air.md), [`Pneuma_Remote_Air_Hardware`](../Pneuma_Remote_Air_Hardware.md)).

### `LL-PNE-07` [TIER5] — `Vacuum_Pump.stl` COTS Reference Model in `STL/` & `1.00mm` X-Axis STEP/STL Drift
- **Retirement Provenance (`TIER5` — `2026-11-18`):** Superseded by `LL-PNE-11` — Re-anchor LL-PNE-07 from retired v1.x STL/Vacuum_Pump.stl path to live v2.01 STL_Files/Pneuma_201 - Vacuum_Pump.stl + pattern:cots_reference_cad
- **Superseded-By:** `LL-PNE-11`
- **Symptom / Failed Approach (`Historical / Rejected`):** Instructing users in `Assembly_Guide.md:20` to *"Print all parts in the STL folder"* without excluding `Vacuum_Pump.stl`, or assuming `100%` dimensional identity between `CAD/Pneuma_Remote_Air.step` and `STL/Vacuum_Pump.stl`.
- **Root Cause:** `STL/Vacuum_Pump.stl` (`90.10 × 124.22 × 65.50 mm`, `2` bodies, `334.62 cm³`) is a COTS reference model of the two internal diaphragm pumps (`Pump v1` + `Pump v1(1)`), not a printable structural housing part. Furthermore, the STEP assembly positions the pump pair across `91.10 × 124.22 × 65.50 mm` (`1.00mm` X-axis spacing offset vs. the exported STL).
- **Verified Resolution & Canonical Owner:** Explicitly segregated `Vacuum_Pump.stl` as a non-printed COTS reference model in [`Pneuma_Remote_Air`](../Pneuma_Remote_Air.md) and [`Pneuma_Remote_Air_Hardware`](../Pneuma_Remote_Air_Hardware.md).
