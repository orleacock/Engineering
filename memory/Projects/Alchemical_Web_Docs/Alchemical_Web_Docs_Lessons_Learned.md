---
project: "Alchemical_Web_Docs"
entity: "Alchemical-3D"
compartment: "public"
note_type: "lessons_learned"
last_synced: "2026-11-08"
---

# Alchemical_Web_Docs — Engineering Lessons Learned & Architectural Decisions

> **Root-Cause Memory Ledger (`entity: Alchemical-3D`)**: Every foundational flaw discovered during design, fabrication, debugging, or testing is recorded here using the **Symptom $\rightarrow$ Root Cause $\rightarrow$ Permanent Guardrail** protocol so solved problems never regress.

---

## 0. Subsystem Rebuild & Invariant Matrix (`Sectional Rebuild Reference`)

<!-- SUBSYSTEM-INVARIANTS:START -->
| Subsystem / Page | Must-Keep Invariants (`Chesterton's Fence`) | Retired Bloat / Anti-Patterns (`Never Re-Add`) | Canonical Owner |
| :--- | :--- | :--- | :--- |
| **`mkdocs.yml` & `docs/CNAME` (`alchemical3d.net`)** | Serves `alchemical3d.net` via Material for MkDocs (`slate`/`pink` theme) with the verified 4-page navigation (`index.md`, `core.md`, `pestle.md`, `retort.md`) and relative internal Markdown links. | Hardcoding legacy `https://alchemical-3d.com/{core,retort,pestle}/` URLs inside `docs/index.md`, which break local preview builds and diverge from `docs/CNAME` (`alchemical3d.net`). | [`Alchemical_Web_Docs.md`](Alchemical_Web_Docs.md) |
| **`docs/core.md` & `docs/retort.md` (Portal-Only System Specs)** | Houses canonical public specifications for **Core Printer** (`300x300x300` build volume, `1x MGN12H` X + `5x MGN9H` Y/Z, `9mm` `2GT` belts, `42STH48-2504AC`) and **Retort Filament Dryer** (`ABS`/`ASA`/`PC` solid-state dryer) until standalone CAD repos are published. | Borrowing Core Printer frame/rail specs onto standalone sub-assemblies (`A3DP_Gantry_Assembly` or `Alembic_Toolhead`) without explicit cross-repo verification. | [`Alchemical_Web_Docs.md`](Alchemical_Web_Docs.md) |
<!-- SUBSYSTEM-INVARIANTS:END -->

---

## 1. Lessons Learned Ledger (`Symptom -> Root Cause -> Guardrail`)

| ID | Date | Symptom / Failure Observed | Root Cause | Permanent Guardrail / Rule or Code Fix | Verification Anchor |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `LL-AWD-01` | `2026-11-02` | Navigation cards in `docs/index.md:10,23,27` pointed to `https://alchemical-3d.com/{core,retort,pestle}/` while `docs/CNAME` and `mkdocs.yml` served `alchemical3d.net` | Legacy domain links remained hardcoded in `docs/index.md` after migrating the GitHub Pages custom domain to `alchemical3d.net` | Replaced hardcoded legacy domain links with relative MkDocs page links (`core.md`, `retort.md`, `pestle.md`) and verified `0` broken links via `audit_repo_docs.py` | [`Alchemical_Web_Docs.md`](Alchemical_Web_Docs.md) |
| `LL-AWD-02` | `2026-11-02` | Showcase images (`Award.png`, `alchemical-3d_core.png`, `PestleExploded3.png`, `3dprofilefront.png`) risked inconsistent border/shadow presentation across dark/light browser themes | Raw unframed raster images lacked standardized corner radius and drop-shadow alpha margins | Verified all showcase cards via `format_image.py --inspect` (`[PASS]`) and `verify_claims.py --fail-on-tbd` (`0` unbacked claims across all `5` Markdown files) | [`Alchemical_Web_Docs.md`](Alchemical_Web_Docs.md) |

### `LL-AWD-01` [TIER2] — Relative MkDocs Page Links vs. Hardcoded Legacy Domain URLs (`2026-11-02`)
- **Symptom / Trap:** Navigation cards in `docs/index.md:10,23,27` pointed to `https://alchemical-3d.com/{core,retort,pestle}/` while `docs/CNAME` and `mkdocs.yml` served `alchemical3d.net`.
- **Root Cause:** Legacy domain links remained hardcoded in `docs/index.md` after migrating the GitHub Pages custom domain to `alchemical3d.net`.
- **Verified Resolution & Permanent Guardrail:** Replaced hardcoded legacy domain links with relative MkDocs page links (`core.md`, `retort.md`, `pestle.md`) and verified `0` broken links via `audit_repo_docs.py` ([`Alchemical_Web_Docs.md`](Alchemical_Web_Docs.md)).

### `LL-AWD-02` [TIER2] — Standardized Showcase Card Framing Across Dark/Light Browser Themes (`2026-11-02`)
- **Symptom / Trap:** Showcase images (`Award.png`, `alchemical-3d_core.png`, `PestleExploded3.png`, `3dprofilefront.png`) risked inconsistent border/shadow presentation across dark/light browser themes.
- **Root Cause:** Raw unframed raster images lacked standardized corner radius and drop-shadow alpha margins.
- **Verified Resolution & Permanent Guardrail:** Verified all showcase cards via `format_image.py --inspect` (`[PASS]`) and `verify_claims.py --fail-on-tbd` (`0` unbacked claims across all `5` Markdown files; [`Alchemical_Web_Docs.md`](Alchemical_Web_Docs.md)).

---

## 2. Architectural Decision Records (`ADR`)

### `ADR-01`: Initial Project Architecture (`2026-11-05`)
- **Context**: Initial repository and memory scaffolding for `Alchemical_Web_Docs` (`project_type: software`).
- **Decision**: Governed under Homunculus Governing Priority Law (`1. Accuracy & Truth -> 2. Efficiency -> 3. Data Safety -> 4. Speed`) with strict `entity: Alchemical-3D` isolation.
- **Consequences**: All quantitative claims require primary source anchors or explicit `[TBD: ...]` tags; unverified notes remain isolated in [`Quarantine/`](Quarantine/Quarantine_README.md).
