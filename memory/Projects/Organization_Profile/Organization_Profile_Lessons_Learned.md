---
project: "Organization_Profile"
entity: "Alchemical-3D"
compartment: "public"
note_type: "lessons_learned"
last_synced: "2026-11-13"
---

# Organization_Profile — Engineering Lessons Learned & Architectural Decisions

> **Root-Cause Memory Ledger (`entity: Alchemical-3D`)**: Every foundational flaw discovered during design, fabrication, debugging, or testing is recorded here using the **Symptom $\rightarrow$ Root Cause $\rightarrow$ Permanent Guardrail** protocol so solved problems never regress.

---

## 0. Subsystem Rebuild & Invariant Matrix (`Sectional Rebuild Reference`)

<!-- SUBSYSTEM-INVARIANTS:START -->
| Subsystem / File | Must-Keep Invariants (`Chesterton's Fence`) | Retired Bloat / Anti-Patterns (`Never Re-Add`) | Canonical Owner |
| :--- | :--- | :--- | :--- |
| **`profile/README.md` (GitHub Org Storefront)** | Renders at `https://github.com/Alchemical-3D`; embeds the transparent primary SVG banner from [`Brand`](../Brand/Brand.md), showcases active ecosystem repositories (`Alembic_Toolhead`, `Pneuma_Remote_Air`, `Retort-A`/`B`, `Pestle_Rotational_Bowden`, `Maker-Tools`), and declares `CC BY-NC-SA 4.0` licensing + `https://ko-fi.com/alchemical3d`. | Embedding quantitative sub-assembly specifications inside `profile/README.md` that can drift out of sync with downstream hardware repositories (`BOM.md` / `Assembly_Guide.md`). | [`Organization_Profile.md`](Organization_Profile.md) |
<!-- SUBSYSTEM-INVARIANTS:END -->

---

## 1. Lessons Learned Ledger (`Symptom -> Root Cause -> Guardrail`)

| ID | Date | Symptom / Failure Observed | Root Cause | Permanent Guardrail / Rule or Code Fix | Verification Anchor |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `LL-OP-01` | `2026-11-05` | GitHub organization landing pages only render when placed at the exact `profile/README.md` path inside the `.github` repository | Placing `README.md` only at the repository root of `.github` describes the repo itself rather than rendering on the public `https://github.com/Alchemical-3D` organization profile | Maintained `profile/README.md` as the single living document (`VRF-3b88c1f9d028`, `8` supported claims, `0` unbacked claims) | [`Organization_Profile.md`](Organization_Profile.md) |
| `LL-OP-02` | `2026-11-05` | Duplicating detailed fastener or dimension counts on the organization landing page creates multi-repo maintenance drift whenever a hardware project iterates | High-level storefront copy should route builders to canonical project repositories rather than acting as a secondary BOM | Kept `profile/README.md` scoped to architectural roles, licensing (`CC BY-NC-SA 4.0`), and direct repository links | [`Organization_Profile.md`](Organization_Profile.md) |

### `LL-OP-02` [TIER2] — Keeping Storefront Copy Free of Secondary BOM/Fastener Duplication (`2026-11-05`)
- **Symptom / Trap:** Duplicating detailed fastener or dimension counts on the organization landing page creates multi-repo maintenance drift whenever a hardware project iterates.
- **Root Cause:** High-level storefront copy should route builders to canonical project repositories rather than acting as a secondary BOM.
- **Verified Resolution & Permanent Guardrail:** Kept `profile/README.md` scoped to architectural roles, licensing (`CC BY-NC-SA 4.0`), and direct repository links ([`Organization_Profile.md`](Organization_Profile.md)).

---

## 2. Architectural Decision Records (`ADR`)

### `ADR-01`: Initial Project Architecture (`2026-11-05`)
- **Context**: Initial repository and memory scaffolding for `Organization_Profile` (`project_type: software`).
- **Decision**: Governed under Homunculus Governing Priority Law (`1. Accuracy & Truth -> 2. Efficiency -> 3. Data Safety -> 4. Speed`) with strict `entity: Alchemical-3D` isolation.
- **Consequences**: All quantitative claims require primary source anchors or explicit `[TBD: ...]` tags; unverified notes remain isolated in [`Quarantine/`](Quarantine/Quarantine_README.md).
