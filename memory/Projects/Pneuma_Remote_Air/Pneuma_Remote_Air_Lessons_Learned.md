---
project: "Pneuma_Remote_Air"
parent_note: "Pneuma_Remote_Air"
entity: "Alchemical-3D"
compartment: "public"
note_type: "lessons_learned"
last_synced: "2026-11-05"
---

# 🧠 Pneuma Remote Air — Engineering Lessons Learned & Post-Mortem Ledger (`Pneuma_Remote_Air_Lessons_Learned`)

Part of the [`README.md`](../../README.md) and project-scoped troubleshooting ledger for [`Pneuma_Remote_Air`](Pneuma_Remote_Air.md) and [`Pneuma_Remote_Air_Hardware`](Pneuma_Remote_Air_Hardware.md).

> [!IMPORTANT]
> **Containment, Failed-Attempt Quarantine & Role Separation**
> 1. **Failed-Attempt Quarantine (`verify_claims.py` Auto-Exclusion):** Automatically excluded (`excluded_lessons_learned_sources`) when scanning `--sources`. Canonical specifications and active `Mode B1` assembly rules live in [`Pneuma_Remote_Air`](Pneuma_Remote_Air.md), [`Pneuma_Remote_Air_Hardware`](Pneuma_Remote_Air_Hardware.md), and `Firmware/Pneuma_Control.cfg`.
> 2. **Role Separation:** Active `Open [TBD]` items are tracked exclusively in [`Pneuma_Remote_Air`](Pneuma_Remote_Air.md) (`## 🔍 Provenance Status & Open [TBD] / [CONFLICT] Ledger`). This file records **only** historical post-mortems, retired architectures, and coupled interface root causes.

---

## 1. Engineering Post-Mortems & Troubleshooting Entries

### 1.1 Why Pneuma Evolved from Single-Pump Solenoid Diversion to Dual-Pump Thermal Regimes (`Tier 1: Local`)
- **Symptom / Failed Approach (`Historical / Rejected`):** Early Pneuma prototypes used a single air pump paired with a standard pressure-assisted `1-8-NPT` solenoid diversion valve, which failed to actuate reliably under vacuum or low pressure differentials and could not independently blend ambient vs. chamber air.
- **Root Cause:** Pilot-operated solenoid valves rely on line pressure differential to shift the internal diaphragm and stall when switching intake vacuum or low-backpressure exhaust. More fundamentally, a single pump cannot independently modulate ambient room air (`pump_cool` for PLA overhangs) vs. heated chamber air (`pump_warm` for `ABS`/`ASA` bridges without thermal shock/delamination).
- **Verified Resolution & Canonical Owner:** Upgraded to two independent pumps driven by Klipper `[fan_generic pump_cool]` (`pin: PF7`) and `[fan_generic pump_warm]` (`pin: PF9`) in `Firmware/Pneuma_Control.cfg` ([`Pneuma_Remote_Air`](Pneuma_Remote_Air.md)). Legacy single-pump builds require a direct-acting `1-8-NPT` valve; the remaining doc sync between `README.md` and `BOM.md`/`Assembly_Guide.md` is tracked in [`Pneuma_Remote_Air`](Pneuma_Remote_Air.md)'s `Open [TBD] Ledger`.

### 1.2 Coupled 6mm OD Umbilical & Pressure-Side Sealing (Alembic_Toolhead Interface) (`Tier 2: Coupled`)
- **Symptom / Failed Approach (`Historical / Rejected`):** Line-pressure drop at threaded fittings (`>= 70 kPa`), acoustic/air gaps between `Rear_Cover` and `Main_Body`, or choked airflow reaching [`Alembic_Toolhead`](../../Projects/Alembic_Toolhead/Alembic_Toolhead.md).
- **Root Cause:** Protruding `M3x5x4mm` brass heat-set inserts hold `Rear_Cover` proud of `Main_Body`; unsealed pressure-side NPT threads leak positive pressure; tight bend radii kink the `6mm OD` umbilical line.
- **Verified Resolution & Canonical Owner:** Seat all `M3x5x4mm` inserts strictly flush, wrap Teflon tape on pressure-side threads, and route the `6mm OD` umbilical with generous sweep radii ([`Pneuma_Remote_Air`](Pneuma_Remote_Air.md)).
- **Shared Interface Link (Tier 2):** Coupled with [`Alembic_Toolhead_Lessons_Learned`](../../Projects/Alembic_Toolhead/Alembic_Toolhead_Lessons_Learned.md).

### 1.3 Anti-Cross-Entity Polymer Borrowing (`TPU` Vibration Isolators vs. `ABS/ASA` Enclosure) (`Tier 3: Graduated`)
- **Symptom / Failed Approach (`Historical / Rejected`):** Copying structural `ABS`/`ASA` print settings (`4` walls, `5` top/bottom layers, `40%` `Grid`/`Gyroid` infill) onto the three elastomer vibration-isolation parts (`TPU_Grommet.stl`, `Table_Mount_TPU.stl`, `Plug_Grommet_TPU.stl`) or inventing TPU Shore hardness from pretraining defaults.
- **Root Cause:** Borrowing `40%` structural infill onto TPU makes vibration isolators rigid and transmits pump resonance directly into the frame/table.
- **Verified Resolution & Canonical Owner:** Graduated into [`Verifiable_Accuracy_and_Anti_Hallucination`](../../Standards_and_Specs/Verifiable_Accuracy_and_Anti_Hallucination.md) (`Ban Cross-Entity Borrowing`); TPU parameters remain quarantined as an explicit `[TBD]` in [`Pneuma_Remote_Air`](Pneuma_Remote_Air.md) until measured.
