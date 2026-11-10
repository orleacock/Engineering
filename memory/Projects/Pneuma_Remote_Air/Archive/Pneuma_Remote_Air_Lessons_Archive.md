---
project: "Pneuma_Remote_Air"
parent_note: "Pneuma_Remote_Air_Lessons_Learned"
entity: "Alchemical-3D"
compartment: "public"
note_type: "lessons_archive"
authoritative: false
last_synced: "2026-11-09"
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
