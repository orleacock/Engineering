---
project: "Brand"
entity: "Alchemical-3D"
compartment: "public"
note_type: "lessons_learned"
last_synced: "2026-11-08"
---

# Brand — Engineering Lessons Learned & Architectural Decisions

> **Root-Cause Memory Ledger (`entity: Alchemical-3D`)**: Every foundational flaw discovered during design, fabrication, debugging, or testing is recorded here using the **Symptom $\rightarrow$ Root Cause $\rightarrow$ Permanent Guardrail** protocol so solved problems never regress.

---

## 0. Subsystem Rebuild & Invariant Matrix (`Sectional Rebuild Reference`)

<!-- SUBSYSTEM-INVARIANTS:START -->
| Subsystem / Asset | Must-Keep Invariants (`Chesterton's Fence`) | Retired Bloat / Anti-Patterns (`Never Re-Add`) | Canonical Owner |
| :--- | :--- | :--- | :--- |
| **Color & Typography Tokens (`Alchemical3D_Color_Template`)** | Primary Pink `#FF3985`, Deep Crimson `#C90448`, Dark Slate Canvas `#1E1E24` / Card `#282830`, and Pure White `#FFFFFF` showcase interiors with `20px` RGBA drop-shadow margin; `Inter` UI + `JetBrains Mono` telemetry font stacks. | Ad-hoc unapproved hex colors in Mermaid/SVG diagrams or running destructive card crops on master brand guideline sheets (`images/alchemical-cd-master-guideline.png`). | [`Brand.md`](Brand.md) |
| **Vector & Raster Logo Assets (`assets/{svg,png,pdf}/`)** | Canonical source of truth for `!Alchemical-3D-Logo-Gradient-PRIMARY`, `!Alchemical-3D-Badge-Gradient-PRIMARY`, and `Alchemical-3D-Badge-Gradient-PRIMARY-Alchemical-3D-Logo-Gradient-PRIMARY-Transparent-Background.svg` consumed by [`Organization_Profile`](../Organization_Profile/Organization_Profile.md) and [`Alchemical_Web_Docs`](../Alchemical_Web_Docs/Alchemical_Web_Docs.md). | Renaming or moving primary SVG assets in `assets/svg/`, which breaks raw GitHub embeds across downstream repositories. | [`Brand.md`](Brand.md) |
<!-- SUBSYSTEM-INVARIANTS:END -->

---

## 1. Lessons Learned Ledger (`Symptom -> Root Cause -> Guardrail`)

| ID | Date | Symptom / Failure Observed | Root Cause | Permanent Guardrail / Rule or Code Fix | Verification Anchor |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `LL-BR-01` | `2026-11-05` | Automated image card formatting risked altering `images/alchemical-cd-master-guideline.png` | `alchemical-cd-master-guideline.png` is a full-bleed master brand specification sheet rather than a hardware documentation photo | Exempted master brand guideline assets from `format_image.py` re-framing and recorded the invariance in [`Brand.md`](Brand.md) (`VRF-6a3a65d81b80`) | [`Brand.md`](Brand.md) |
| `LL-BR-02` | `2026-11-05` | Dark-mode vs. light-mode GitHub READMEs rendered low-contrast text or invisible dark logo marks when using single-mode assets | Transparent black-on-white (`BoW`) or white-on-black (`WoB`) marks blend into matching GitHub theme backgrounds | Standardized on gradient primary marks with baked-in `#FFFFFF` rounded-corner showcase cards (`20px` RGBA shadow margin) for hardware photos and `Alchemical3D_Color_Template` tokens for SVG/Mermaid diagrams | [`Brand.md`](Brand.md) |

### `LL-BR-01` [TIER2] — Exempting Master Brand Guideline Sheets from Automated Image Card Framing (`2026-11-05`)
- **Symptom / Trap:** Automated image card formatting risked altering `images/alchemical-cd-master-guideline.png`.
- **Root Cause:** `alchemical-cd-master-guideline.png` is a full-bleed master brand specification sheet rather than a hardware documentation photo.
- **Verified Resolution & Permanent Guardrail:** Exempted master brand guideline assets from `format_image.py` re-framing and recorded the invariance in [`Brand.md`](Brand.md) (`VRF-6a3a65d81b80`).

### `LL-BR-02` [TIER2] — Gradient Primary Marks & `#FFFFFF` Showcase Cards Across GitHub Dark/Light Themes (`2026-11-05`)
- **Symptom / Trap:** Dark-mode vs. light-mode GitHub READMEs rendered low-contrast text or invisible dark logo marks when using single-mode assets.
- **Root Cause:** Transparent black-on-white (`BoW`) or white-on-black (`WoB`) marks blend into matching GitHub theme backgrounds.
- **Verified Resolution & Permanent Guardrail:** Standardized on gradient primary marks with baked-in `#FFFFFF` rounded-corner showcase cards (`20px` RGBA shadow margin) for hardware photos and `Alchemical3D_Color_Template` tokens for SVG/Mermaid diagrams ([`Brand.md`](Brand.md)).

---

## 2. Architectural Decision Records (`ADR`)

### `ADR-01`: Initial Project Architecture (`2026-11-05`)
- **Context**: Initial repository and memory scaffolding for `Brand` (`project_type: software`).
- **Decision**: Governed under Homunculus Governing Priority Law (`1. Accuracy & Truth -> 2. Efficiency -> 3. Data Safety -> 4. Speed`) with strict `entity: Alchemical-3D` isolation.
- **Consequences**: All quantitative claims require primary source anchors or explicit `[TBD: ...]` tags; unverified notes remain isolated in [`Quarantine/`](Quarantine/Quarantine_README.md).
