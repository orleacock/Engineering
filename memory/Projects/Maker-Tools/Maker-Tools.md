---
project: "Maker-Tools"
entity: "Alchemical-3D"
compartment: "public"
project_type: "software"
status: "Verified & Complete"
local_path: "/home/orin/Projects/Alchemical3D/Maker-Tools"
repo_head_sha: "29641c5802f8"
tree_hash: "9c7d9625f4e2"
checkpoint_head_sha: "29641c5802f8"
checkpoint_tree_hash: "9c7d9625f4e2"
checkpoint_worktree: "('clean', [])"
task_umbrella: "../../Tasks/Alchemical-3D_Tasks.md"
last_synced: "2026-11-06"
---

## 🧭 Homunculus Companion Notes & Project Navigation

| Artifact Role | File Link | Purpose |
| :--- | :--- | :--- |
| **Project Hub (`AUTO-TREE`)** | [`Maker-Tools.md`](Maker-Tools.md) | Canonical architecture overview, `SESSION-HANDOFF`, `AUTO-TREE`, and `[TBD]` Ledger. |
| **Software Telemetry** | [`Maker-Tools_Software.md`](Maker-Tools_Software.md) | Runtime entrypoints, CLI flags, public symbols, and JSON schemas. |
| **Lessons Learned & Post-Mortems** | [`Maker-Tools_Lessons_Learned.md`](Maker-Tools_Lessons_Learned.md) | Root-cause post-mortems (`Symptom -> Root Cause -> Permanent Guardrail`). |
| **Project Templates** | [`Templates/`](Templates/) | Project-specific deliverable templates. |
| **Unverified Quarantine Zone** | [`Quarantine/Quarantine_README.md`](Quarantine/Quarantine_README.md) | Holding zone for unverified notes (`[QUARANTINED — DO NOT CITE AS FACT]`). |
| **Active Task Umbrella** | [`Alchemical-3D_Tasks.md`](../../Tasks/Alchemical-3D_Tasks.md#Maker-Tools) | Single-writer task tracker for `Alchemical-3D` (zero duplicate checkboxes in hub). |

---

# 🛠️ Maker-Tools (Filament Science & Shop Tooling Reference)

Part of the [`README.md`](../../README.md)

## 🔒 Concept & Design Philosophy ("Why")
- **Central Polymer & Bench Hardware Reference (`README.md:9-11`):** Provides builders across all Alchemical-3D repositories (`Mode B2` Explanatory Reference Voice) with curated, field-tested polymer selection criteria (`Tg`, heat deflection, moisture sensitivity, creep resistance) and trusted shop tools so individual hardware BOMs stay focused on build parts.
- **Preventing Polymer Selection Failures:** Explains *why* low-`Tg` or high-creep polymers (`PLA` Tg `~55-60 °C`, `PETG` Tg `~80 °C`) fail inside heated CoreXY chambers and belt-tensioned assemblies, anchoring structural recommendations on `ABS`/`ASA` (Tg `~100-105 °C`), `PC` (Tg `~145-150 °C`), `PAHT`/`PPA`, and high-performance `PEI`/`PEEK`.

## 📍 Repository & File Inventory
- **Local Path:** `/home/orin/Projects/Alchemical3D/Maker-Tools`
- **GitHub Remote:** `https://github.com/Alchemical-3D/Maker-Tools`
- **Living Documentation:** `README.md` (Catalog Hub), `Filament_Guide.md` (`5` polymer tiers + CF/GF/Core/LW composites), `Tools_and_Hardware.md`
- **Standards Applied:** [`Verifiable_Accuracy_and_Anti_Hallucination`](../../Standards_and_Specs/Verifiable_Accuracy_and_Anti_Hallucination.md), `Author_Voice_and_Cadence`, [`Fasteners_and_Inserts`](../../Standards_and_Specs/Fasteners_and_Inserts.md), `Image_and_Style_Rules`, `Subagent_and_Memory_Architecture`

<!-- AUTO-TREE:START -->
```text
Repository: Maker-Tools | HEAD SHA: 29641c5802f8 | Tree Hash: 9c7d9625f4e2
  Filament_Guide.md
  README.md
  Tools_and_Hardware.md
```
<!-- AUTO-TREE:END -->

## 📐 Verified Specs, COTS Hardware & Key Content
- **Polymer Thermal Reference (`Filament_Guide.md:14-639`):**
  - *Everyday / Consumer*: `PLA` (Tg `~55-60 °C`, Tm `~150-180 °C`), `PETG` (Tg `~80 °C`), `PCTG` (Tg `~85 °C`), `PP` (Tg `~-10 °C`).
  - *Elastomers*: `TPU` (Tg `~-30 to -40 °C`), `PEBA` (Tg `~-50 to -60 °C`).
  - *Structural Chamber Polymers*: `ABS` / `ASA` (Tg `~100-105 °C`), `PC-ABS` (Tg `~110 °C`), `PC` (Tg `~145-150 °C`).
  - *Engineering Polyamides & Polyesters*: `PA` (Tg `~50-60 °C`), `PAHT` (Tg `~80-90 °C`), `PPA` (Tg `~120-130 °C`), `PPS` (Tg `~90 °C`), `PET` (Tg `~70-80 °C`).
  - *Ultra-Polymers*: `PSU` (Tg `~190 °C`), `PEI` / `Ultem` (Tg `~215-217 °C`), `PEEK` (Tg `~143-150 °C`, Vicat `~315 °C`).
- **Curated Shop Tools & Consumables (`Tools_and_Hardware.md:11-96`):** `Wisesorb` activated alumina desiccant, `FNIRSI HS-02A` & `Pinecil` soldering irons (heat-set installation), `LDO` `6`-piece hex driver kit (`1.27–4.0mm`), `Klein 1019` wire strippers, terminal crimpers, `NoClogger`, `3DO` `FEP` wire (`20AWG` / `24AWG`), `Loctite 222MS` & `Loctite 243`, `HSS` chucking reamers (`2–10mm`), printable shop jigs (`Utility Knife MK2`, `Center Finder`, `Screw Measuring Tool`), and `West3D` / `KB-3D` / `Fabreeko` ecosystem links.

## 🔗 Companion Projects & Kinematic / System Links
- [`Extras`](../../Projects/Extras/Extras.md) — `20mm` calibration cube STLs used alongside `Filament_Guide.md` to calibrate polymer shrinkage.
- [`Brand`](../../Projects/Brand/Brand.md) — Shared ecosystem visual identity and vendor/affiliate link conventions.
- [`Alembic_Toolhead`](../../Projects/Alembic_Toolhead/Alembic_Toolhead.md), [`Pneuma_Remote_Air`](../../Projects/Pneuma_Remote_Air/Pneuma_Remote_Air.md), [`A3DP_Gantry_Assembly`](../../Projects/A3DP_Gantry_Assembly/A3DP_Gantry_Assembly.md), [`Pestle_Rotational_Bowden`](../../Projects/Pestle_Rotational_Bowden/Pestle_Rotational_Bowden.md) — Reference `Maker-Tools` for assembly tooling and polymer selection.

## 🔍 Provenance Status & Open [TBD] / [CONFLICT] Ledger
> [!NOTE]
> Figures inside this ledger are quarantined by `verify_claims.py` and are **not** treated as authorized source truth until resolved.

- **Git & Provenance Baseline:** `main:clean` (`audit_repo_docs.py`: `0` load-bearing issues, `0` isolated warnings; `verify_claims.py --fail-on-tbd` receipt `VRF-076c174de9c5`, `282` supported claims across `README.md`, `Filament_Guide.md`, and `Tools_and_Hardware.md`).
- **Open Quantitative `[TBD]` / `[CONFLICT]` Items:** `None` (`open_tbd_count: 0`).

## 🎯 Active Tasks
*(Transcluded live from `### Maker-Tools` in [`Alchemical3D_Tasks`](../../Tasks/Alchemical-3D_Tasks.md))*

> **Active Task Queue**: Tracked in [`Alchemical3D_Tasks`](../../Tasks/Alchemical-3D_Tasks.md#Maker-Tools) *(Single-Writer Task Umbrella)*.

## 🚀 Session Handoff & Multi-Session Kickstart (`SESSION-HANDOFF`)
<!-- SESSION-HANDOFF:START -->
- **Last Session Timestamp**: `2026-11-05`
- **Checkpoint Provenance**: `HEAD SHA: 29641c5802f8` | `Tree Hash: 9c7d9625f4e2` | `Worktree: ('clean', [])` | `Last Verification: Transplanted from verified Memory v2 baseline`
- **Where We Stopped (Verified State & Context)**:
  - Transplanted `Maker-Tools` dossier into native Homunculus Dual-Mode Memory (`entity: Alchemical-3D`, `compartment: public`, `project_type: software`). All verified specifications, hazards, and open `[TBD]` ledgers preserved verbatim.
- **Active Project State Ledger & Blockers**:
  - See `## 🔍 Provenance Status & Open [TBD] / [CONFLICT] Ledger` above and active tasks in [`Alchemical-3D_Tasks.md`](../../Tasks/Alchemical-3D_Tasks.md).
- **Next Session Kickstart & Discussion Points**:
  1. Run `python3 skills/project-memory/scripts/sync_memory.py --project Maker-Tools --kickstart` to verify repository provenance.
  2. Review open tasks in [`Alchemical-3D_Tasks.md`](../../Tasks/Alchemical-3D_Tasks.md#Maker-Tools).
<!-- SESSION-HANDOFF:END -->
