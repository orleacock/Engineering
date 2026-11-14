---
project: "Maker-Tools"
entity: "Alchemical-3D"
compartment: "public"
note_type: "lessons_learned"
last_synced: "2026-11-13"
---

# Maker-Tools — Engineering Lessons Learned & Architectural Decisions

> **Root-Cause Memory Ledger (`entity: Alchemical-3D`)**: Every foundational flaw discovered during design, fabrication, debugging, or testing is recorded here using the **Symptom $\rightarrow$ Root Cause $\rightarrow$ Permanent Guardrail** protocol so solved problems never regress.

---

## 0. Subsystem Rebuild & Invariant Matrix (`Sectional Rebuild Reference`)

<!-- SUBSYSTEM-INVARIANTS:START -->
| Subsystem / Document | Must-Keep Invariants (`Chesterton's Fence`) | Retired Bloat / Anti-Patterns (`Never Re-Add`) | Canonical Owner |
| :--- | :--- | :--- | :--- |
| **`Filament_Guide.md` (`5` Polymer Tiers)** | Preserves explicit glass-transition (`Tg`) and thermal/creep boundaries across all `5` tiers (`PLA` Tg `~55-60 °C`, `PETG` Tg `~80 °C`, `ABS`/`ASA` Tg `~100-105 °C`, `PC` Tg `~145-150 °C`, `PEEK`/`PEI` ultra-polymers) using `Mode B2` Explanatory Reference Voice. | Recommending `PLA` or `PETG` for structural heated-chamber or belt-tensioned CoreXY components where creep or thermal softening occurs below `100 °C`. | [`Maker-Tools.md`](Maker-Tools.md) |
| **`Tools_and_Hardware.md` (Curated Bench Reference)** | Centralizes reusable shop tooling (`FNIRSI HS-02A`/`Pinecil` heat-set irons, `LDO` hex drivers, `Loctite 222MS`/`243`, `HSS` chucking reamers `2–10mm`, `3DO` `FEP` wire) so individual hardware BOMs stay focused on build-specific COTS parts. | Duplicating full shop-tool catalogs inside individual hardware repo `BOM.md` files or stripping documented vendor attribution links (`West3D`, `KB-3D`, `Fabreeko`). | [`Maker-Tools.md`](Maker-Tools.md) |
<!-- SUBSYSTEM-INVARIANTS:END -->

---

## 1. Lessons Learned Ledger (`Symptom -> Root Cause -> Guardrail`)

| ID | Date | Symptom / Failure Observed | Root Cause | Permanent Guardrail / Rule or Code Fix | Verification Anchor |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `LL-MT-01` | `2026-11-05` | Builders selecting `PLA` (`Tg ~55-60 °C`) or `PETG` (`Tg ~80 °C`) for CoreXY gantry/toolhead structural parts experienced creep and bolt-load relaxation | Lack of a centralized first-principles polymer reference explaining glass transition (`Tg`) vs. sustained mechanical load inside heated chambers | Authored `Filament_Guide.md` (`5` polymer tiers + composite modifiers) and cross-linked it across all Alchemical-3D `Print_Settings.md` files | [`Maker-Tools.md`](Maker-Tools.md) |
| `LL-MT-02` | `2026-11-05` | Individual hardware repository BOMs became cluttered with generic shop tools (soldering irons, hex drivers, reamers, threadlockers) | No separation between build-consumed COTS fasteners/electronics and reusable bench tooling | Extracted all bench tooling and consumables into `Tools_and_Hardware.md` (`282` verified claims across `Maker-Tools`, `VRF-076c174de9c5`) | [`Maker-Tools.md`](Maker-Tools.md) |

### `LL-MT-01` [TIER2] — Glass-Transition (`Tg`) Polymer Selection Reference (`Filament_Guide.md`) (`2026-11-05`)
- **Symptom / Trap:** Builders selecting `PLA` (`Tg ~55-60 °C`) or `PETG` (`Tg ~80 °C`) for CoreXY gantry/toolhead structural parts experienced creep and bolt-load relaxation.
- **Root Cause:** Lack of a centralized first-principles polymer reference explaining glass transition (`Tg`) vs. sustained mechanical load inside heated chambers.
- **Verified Resolution & Permanent Guardrail:** Authored `Filament_Guide.md` (`5` polymer tiers + composite modifiers) and cross-linked it across all Alchemical-3D `Print_Settings.md` files ([`Maker-Tools.md`](Maker-Tools.md)).

## 2. Architectural Decision Records (`ADR`)

### `ADR-01`: Initial Project Architecture (`2026-11-05`)
- **Context**: Initial repository and memory scaffolding for `Maker-Tools` (`project_type: software`).
- **Decision**: Governed under Homunculus Governing Priority Law (`1. Accuracy & Truth -> 2. Efficiency -> 3. Data Safety -> 4. Speed`) with strict `entity: Alchemical-3D` isolation.
- **Consequences**: All quantitative claims require primary source anchors or explicit `[TBD: ...]` tags; unverified notes remain isolated in [`Quarantine/`](Quarantine/Quarantine_README.md).
