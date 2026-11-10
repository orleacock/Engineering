---
project: "Extras"
entity: "Alchemical-3D"
compartment: "public"
note_type: "lessons_learned"
last_synced: "2026-11-08"
---

# Extras — Engineering Lessons Learned & Architectural Decisions

> **Root-Cause Memory Ledger (`entity: Alchemical-3D`)**: Every foundational flaw discovered during design, fabrication, debugging, or testing is recorded here using the **Symptom $\rightarrow$ Root Cause $\rightarrow$ Permanent Guardrail** protocol so solved problems never regress.

---

## 0. Subsystem Rebuild & Invariant Matrix (`Sectional Rebuild Reference`)

<!-- SUBSYSTEM-INVARIANTS:START -->
| Subsystem / Mesh | Must-Keep Invariants (`Chesterton's Fence`) | Retired Bloat / Anti-Patterns (`Never Re-Add`) | Canonical Owner |
| :--- | :--- | :--- | :--- |
| **Calibration Cube STLs (`Alch_Cube_20mm_V4.stl`, `Alchemical_20mm_Cube.stl`)** | Exact outer bounding envelope `20.00 × 20.00 × 20.00 mm` (`4.40 cm³` / `8,476` triangles for `Alch_Cube_20mm_V4.stl`; `4.35 cm³` / `14,036` triangles for `Alchemical_20mm_Cube.stl`) used as the pre-build XY/Z polymer shrinkage gate across all Alchemical-3D hardware repositories. | Guessing the functional or visual difference between `Alch_Cube_20mm_V4.stl` and `Alchemical_20mm_Cube.stl` without engineer confirmation (`[TBD: calibration_cube_v4_vs_legacy_distinction]`). | [`Extras.md`](Extras.md), [`Extras_Hardware.md`](Extras_Hardware.md) |
<!-- SUBSYSTEM-INVARIANTS:END -->

---

## 1. Lessons Learned Ledger (`Symptom -> Root Cause -> Guardrail`)

| ID | Date | Symptom / Failure Observed | Root Cause | Permanent Guardrail / Rule or Code Fix | Verification Anchor |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `LL-EX-01` | `2026-11-05` | Printing structural `ABS`/`ASA`/`PC` toolhead and gantry parts without prior shrinkage calibration caused tight bearing seats and oversize/undersize `M3x5x4mm` heat-set bores | High-temperature engineering polymers exhibit `0.4%–0.8%` thermal shrinkage upon cooling from chamber temperature | Established the `20.00 × 20.00 × 20.00 mm` calibration cube in `Extras` as the mandatory pre-build dimensional check across all Alchemical-3D `Print_Settings.md` guides | [`Extras.md`](Extras.md) |
| `LL-EX-02` | `2026-11-05` | Risk of inventing narrative explanations for why two `20.00 × 20.00 × 20.00 mm` cube STLs (`4.40 cm³` vs. `4.35 cm³`) coexist in the repository | Both meshes share identical outer envelopes (`20.00 × 20.00 × 20.00 mm`) and differ only in internal embossing/chamfer volume (`0.05 cm³`) with no `README.md` yet committed | Quarantined as `[TBD: calibration_cube_v4_vs_legacy_distinction]` in [`Extras.md`](Extras.md) until confirmed by the engineer | [`Extras.md`](Extras.md), [`Extras_Hardware.md`](Extras_Hardware.md) |

### `LL-EX-01` [TIER2] — Mandatory `20.00 × 20.00 × 20.00 mm` Polymer Shrinkage Calibration Gate (`2026-11-05`)
- **Symptom / Trap:** Printing structural `ABS`/`ASA`/`PC` toolhead and gantry parts without prior shrinkage calibration caused tight bearing seats and oversize/undersize `M3x5x4mm` heat-set bores.
- **Root Cause:** High-temperature engineering polymers exhibit `0.4%–0.8%` thermal shrinkage upon cooling from chamber temperature.
- **Verified Resolution & Permanent Guardrail:** Established the `20.00 × 20.00 × 20.00 mm` calibration cube in `Extras` as the mandatory pre-build dimensional check across all Alchemical-3D `Print_Settings.md` guides ([`Extras.md`](Extras.md)).

### `LL-EX-02` [TIER2] — Quarantining Unconfirmed `Alch_Cube_20mm_V4.stl` vs. `Alchemical_20mm_Cube.stl` Mesh Distinctions (`2026-11-05`)
- **Symptom / Trap:** Risk of inventing narrative explanations for why two `20.00 × 20.00 × 20.00 mm` cube STLs (`4.40 cm³` vs. `4.35 cm³`) coexist in the repository.
- **Root Cause:** Both meshes share identical outer envelopes (`20.00 × 20.00 × 20.00 mm`) and differ only in internal embossing/chamfer volume (`0.05 cm³`) with no `README.md` yet committed.
- **Verified Resolution & Permanent Guardrail:** Quarantined as `[TBD: calibration_cube_v4_vs_legacy_distinction]` in [`Extras.md`](Extras.md) and [`Extras_Hardware.md`](Extras_Hardware.md) until confirmed by the engineer.

---

## 2. Architectural Decision Records (`ADR`)

### `ADR-01`: Initial Project Architecture (`2026-11-05`)
- **Context**: Initial repository and memory scaffolding for `Extras` (`project_type: hardware`).
- **Decision**: Governed under Homunculus Governing Priority Law (`1. Accuracy & Truth -> 2. Efficiency -> 3. Data Safety -> 4. Speed`) with strict `entity: Alchemical-3D` isolation.
- **Consequences**: All quantitative claims require primary source anchors or explicit `[TBD: ...]` tags; unverified notes remain isolated in [`Quarantine/`](Quarantine/Quarantine_README.md).
