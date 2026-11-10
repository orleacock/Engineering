---
project: "Alchemical_Web_Docs"
entity: "Alchemical-3D"
compartment: "public"
project_type: "software"
status: "Verified & Complete"
local_path: "/home/orin/Projects/Alchemical3D/alchemical-3d.github.io"
repo_head_sha: "55b4795b1e8d"
tree_hash: "adeb4e18f33b"
checkpoint_head_sha: "55b4795b1e8d"
checkpoint_tree_hash: "adeb4e18f33b"
checkpoint_worktree: "clean"
task_umbrella: "../../Tasks/Alchemical-3D_Tasks.md"
last_synced: "2026-11-06"
---

## 🧭 Homunculus Companion Notes & Project Navigation

| Artifact Role | File Link | Purpose |
| :--- | :--- | :--- |
| **Project Hub (`AUTO-TREE`)** | [`Alchemical_Web_Docs.md`](Alchemical_Web_Docs.md) | Canonical architecture overview, `SESSION-HANDOFF`, `AUTO-TREE`, and `[TBD]` Ledger. |
| **Software Telemetry** | [`Alchemical_Web_Docs_Software.md`](Alchemical_Web_Docs_Software.md) | Runtime entrypoints, CLI flags, public symbols, and JSON schemas. |
| **Lessons Learned & Post-Mortems** | [`Alchemical_Web_Docs_Lessons_Learned.md`](Alchemical_Web_Docs_Lessons_Learned.md) | Root-cause post-mortems (`Symptom -> Root Cause -> Permanent Guardrail`). |
| **Project Templates** | [`Templates/`](Templates/) | Project-specific deliverable templates. |
| **Unverified Quarantine Zone** | [`Quarantine/Quarantine_README.md`](Quarantine/Quarantine_README.md) | Holding zone for unverified notes (`[QUARANTINED — DO NOT CITE AS FACT]`). |
| **Active Task Umbrella** | [`Alchemical-3D_Tasks.md`](../../Tasks/Alchemical-3D_Tasks.md#Alchemical_Web_Docs) | Single-writer task tracker for `Alchemical-3D` (zero duplicate checkboxes in hub). |

---

# 🌐 Alchemical-3D Web Docs (`alchemical-3d.github.io` / `alchemical3d.net`)

Part of the [`README.md`](../../README.md)

## 🔒 Concept & Design Philosophy ("Why")
- **Public Documentation Portal & Ecosystem Storefront (`mkdocs.yml:1-8`, `docs/CNAME:1`):** MkDocs Material documentation site serving `alchemical3d.net`, providing architectural overviews and technical specifications for flagship ecosystem systems—including **Core Printer** (`docs/core.md`) and **Retort Filament Dryer** (`docs/retort.md`), which do not yet have standalone public CAD repositories in `/home/orin/Projects/Alchemical3D/`.

## 📍 Repository & File Inventory
- **Local Path:** `/home/orin/Projects/Alchemical3D/alchemical-3d.github.io`
- **GitHub Remote:** `https://github.com/Alchemical-3D/alchemical-3d.github.io`
- **Living Documentation & Config:** `mkdocs.yml` (Material `slate`/`pink` theme), `requirements.txt`, `README.md`, `docs/CNAME` (`alchemical3d.net`), `docs/index.md`, `docs/core.md`, `docs/pestle.md`, `docs/retort.md`
- **Assets:** `docs/assets/`
- **Standards Applied:** [`Verifiable_Accuracy_and_Anti_Hallucination`](../../Standards_and_Specs/Verifiable_Accuracy_and_Anti_Hallucination.md), `Author_Voice_and_Cadence`, `Image_and_Style_Rules`, `Subagent_and_Memory_Architecture`

<!-- AUTO-TREE:START -->
```text
Repository: alchemical-3d.github.io | HEAD SHA: 55b4795b1e8d | Tree Hash: adeb4e18f33b
  .gitignore
  README.md
  mkdocs.yml
  requirements.txt
  .github/
  .github/workflows/
  .github/workflows/ci.yml
  docs/
  docs/CNAME
  docs/core.md
  docs/index.md
  docs/pestle.md
  docs/retort.md
  docs/assets/
  docs/assets/images/
  docs/assets/images/!Alchemical-3D-Badge-Gradient-PRIMARY.png
  docs/assets/images/!Alchemical-3D-Badge-Gradient-PRIMARY.svg
  docs/assets/images/Alchemical-3D-Logo-Gradient-PRIMARY-Transparent-Background.png
  docs/assets/images/Award.jpg
  docs/assets/images/Award.png
  docs/assets/images/alchemical-3d-icon.png
  docs/assets/images/alchemical_fire1_web.png
  docs/assets/images/banner.png
```
<!-- AUTO-TREE:END -->

## 📐 Verified Specs, COTS Hardware & Key Content
- **Core Printer Reference Specs (`docs/core.md:9-70`):** `300x300x300` build volume (expandable up to `~350mm`), speeds up to `300mm/s` | 2020 extrusion frame | `1x MGN12H` (X) + `5x MGN9H` (Y/Z) linear rails | `9mm` `2GT` belts | `NEMA 17` `42STH48-2504AC` steppers | `24V` standard (`48V` optional) | `Goliath` / `Dragon` / `V6` hotends | `Spider` / `Octopus` / `Manta M8P` MCUs.
- **Pestle Web Summary (`docs/pestle.md:12,37-41`):** X-gantry rotational Bowden extruder using `NEMA 14` (`36STH20-1004AHG`), `BMG` internals, and `ABS`/`ASA` printed housing.
- **Retort Solid-State Filament Dryer (`docs/retort.md:5-24,38`):** Modular solid-state filament dryer/storage system interfacing with Klipper firmware to track host chamber temperatures; printed in `ABS`, `ASA`, or `PC`.
- **Ecosystem Partners Listed (`docs/index.md:44-54`):** `KB-3D`, `Fabreeko`, `3DO`, `Linneo`, `LDO Motors`.

## 🔗 Companion Projects & Kinematic / System Links
- [`Pestle_Rotational_Bowden`](../../Projects/Pestle_Rotational_Bowden/Pestle_Rotational_Bowden.md) — Dedicated web overview page (`docs/pestle.md`).
- [`Alembic_Toolhead`](../../Projects/Alembic_Toolhead/Alembic_Toolhead.md) & [`Pneuma_Remote_Air`](../../Projects/Pneuma_Remote_Air/Pneuma_Remote_Air.md) — Next-gen hardware stack to be added/cross-linked on the portal.
- [`Brand`](../../Projects/Brand/Brand.md) & [`Organization_Profile`](../../Projects/Organization_Profile/Organization_Profile.md) — Shared brand identity and outbound ecosystem navigation.

## 🔍 Provenance Status & Open [TBD] / [CONFLICT] Ledger
> [!WARNING]
> Figures inside this ledger are quarantined by `verify_claims.py` and are **not** treated as authorized source truth until resolved.

- **Git & Provenance Baseline (`2026-11-02`):** `main:clean` (`audit_repo_docs.py`: `Load-Bearing Issues: 0 | Isolated Warnings: 0`; `format_image.py --inspect`: `[PASS]` on `Award.png`, `alchemical-3d_core.png`, `PestleExploded3.png`, and `3dprofilefront.png`; `verify_claims.py --fail-on-tbd`: `Unbacked Claims: 0 | Open [TBD] Offenders: 0` across all `5` Markdown files).
- **Resolved Ledger History (`2026-11-02`):**
  - *Resolved Domain Conflict*: Replaced legacy `https://alchemical-3d.com/{core,retort,pestle}/` links in `docs/index.md:10,23,27` with relative MkDocs links (`core.md`, `retort.md`, `pestle.md`).
  - *Resolved Portal Navigation Scope*: Confirmed current 4-page `mkdocs.yml` navigation (`index.md`, `core.md`, `pestle.md`, `retort.md`) as the active baseline.

## 🎯 Active Tasks
*(Transcluded live from `### Alchemical_Web_Docs` in [`Alchemical3D_Tasks`](../../Tasks/Alchemical-3D_Tasks.md))*

> **Active Task Queue**: Tracked in [`Alchemical3D_Tasks`](../../Tasks/Alchemical-3D_Tasks.md#Alchemical_Web_Docs) *(Single-Writer Task Umbrella)*.

## 🚀 Session Handoff & Multi-Session Kickstart (`SESSION-HANDOFF`)
<!-- SESSION-HANDOFF:START -->
- **Last Session Timestamp**: `2026-11-05`
- **Checkpoint Provenance**: `HEAD SHA: 55b4795b1e8d` | `Tree Hash: adeb4e18f33b` | `Worktree: ('clean', [])` | `Last Verification: Transplanted from verified Memory v2 baseline`
- **Where We Stopped (Verified State & Context)**:
  - Transplanted `Alchemical_Web_Docs` dossier into native Homunculus Dual-Mode Memory (`entity: Alchemical-3D`, `compartment: public`, `project_type: software`). All verified specifications, hazards, and open `[TBD]` ledgers preserved verbatim.
- **Active Project State Ledger & Blockers**:
  - See `## 🔍 Provenance Status & Open [TBD] / [CONFLICT] Ledger` above and active tasks in [`Alchemical-3D_Tasks.md`](../../Tasks/Alchemical-3D_Tasks.md).
- **Next Session Kickstart & Discussion Points**:
  1. Run `python3 skills/project-memory/scripts/sync_memory.py --project Alchemical_Web_Docs --kickstart` to verify repository provenance.
  2. Review open tasks in [`Alchemical-3D_Tasks.md`](../../Tasks/Alchemical-3D_Tasks.md#Alchemical_Web_Docs).
<!-- SESSION-HANDOFF:END -->
