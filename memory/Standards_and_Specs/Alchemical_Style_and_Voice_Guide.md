---
title: "Alchemical-3D Brand, Storefront & Visual Card Addendum"
entity: "Alchemical-3D"
compartment: "public"
last_synced: "2026-11-11"
---

# Alchemical-3D Brand, Storefront & Visual Card Addendum

Defines **Alchemical-3D**-specific audience calibration, brand voice anchors, storefront structure, and card dimensions across all **Alchemical-3D** GitHub repositories.
- **Generic Author Voice & Stylometrics (`Mode A1`/`A2`/`B1`/`B2`)**: Governed by [`Author_Voice_and_Cadence.md`](Author_Voice_and_Cadence.md) and `/home/orin/Projects/Alchemical3D/Homunculus/addons/author-voice-cadence/SKILL.md`.
- **Automated Markdown, Alert & Card Pipeline**: Enforced by [`Image_and_Style_Rules.md`](Image_and_Style_Rules.md) and `/home/orin/Projects/Alchemical3D/Homunculus/skills/doc-and-card-studio/SKILL.md` (`audit_repo_docs.py` + `format_image.py`).

---

## 1. Audience & Paramount-Only Build-Guide Reasoning

- **Target Audience**: Makers from first-time modders to experienced print-farm operators and Voron/CoreXY builders.
- **Installation & Print Guides (`Assembly_Guide.md`, `Print_Settings.md`, `BOM.md`)**: Write standard operations in **1–2 crisp sentences** without tool micro-tutorials or obvious material lectures. Include `"why"` reasoning **only when paramount AND verified** in project hardware/standards (place global torque/chemical rules once upfront):
  - *Alignment / Clearance*: Flush/square seating required so downstream sub-assemblies clear the frame or linear motion path.
  - *Mechanical / Pneumatic Seal*: Dual-side idler shims preventing flange rub; O-ring seating prior to clamping to prevent air leaks.
  - *Thermal / Chemical / Torque*: `PLA`/`PETG` creep near hotends or heated chambers; stop turning fasteners in printed plastic at initial compression; anaerobic threadlocker (`Loctite 243` / `222MS`) must **never** contact `ABS`, `ASA`, or `PC`.
- **Overviews & References (`README.md`, `ALPHA_&_DIRECTION.md`, `Maker-Tools/*.md`)**: Explain engineering trade-offs and translate ASTM/ISO metrics into plain workshop terms (e.g., `Filament_Guide.md` *"Layman's Description"* column).

---

## 2. Alchemical-3D Brand Voice Anchors

1. **Signature Epigraphs & Analogies**:
   - Organization & major overview motto:
     > *"Transmuting ideas into reality, layer by layer."*
   - Precision assembly guide epigraph:
     > *The machine you are building now will be a reflection of the effort committed to assembling it. Attention to detail is directly related to both the performance of the machine and its longevity.*
   - Concrete `Mode A` overview analogies: Frame `Alembic`'s targeted nozzle-exit air delivery vs. broad blower/CPAP wash as **Scalpel vs. Sledgehammer** (never conflate `Pneuma`'s remote pump unit with `Alembic`'s toolhead manifold, and never copy analogies onto unrelated hardware).
2. **Controlled Levity vs. Serious Safety**:
   - Light workshop humor is welcome in non-critical prose, **never** inside `> [!CAUTION]` or `> [!WARNING]` blocks covering torque limits (`~1.0` to `1.5 Nm` for `M3` in milled aluminum vs. initial compression in printed plastic), mains voltage, styrene/VOC fumes, or builder liability.

---

## 3. Canonical Hardware Repository Architecture

| File / Directory | Purpose |
| :--- | :--- |
| `README.md` | Storefront: `<div align="center">` hero (`# [Emoji] Project Name`, Shields.io badges including `Ecosystem-Alchemical--3D-purple` / optional `Ecosystem-A3DP-orange` / `License-CC BY--NC--SA 4.0-lightgrey`, 2–3 sentence pitch, side-by-side `width="45%"` `&nbsp;` or single `width="80%"` hero card, `&nbsp;•&nbsp;` quick-nav bar), emoji-prefixed `##` sections separated by `---`, Documentation Index, related projects, and `***` License / Ko-fi / AI footer (`*Documentation prepared with AI editorial assistance • Engineered & maintained by Alchemical-3D.*`). |
| `BOM.md` | Categorized BOM (`1. Printed Parts`, `2. Fasteners & Physical Hardware` Kit vs. Self-Sourced, `3. Electronics and Hardware`), center-aligned qty (`| :--- | :---: | :--- |`), backticked `.stl`/`.step` names, bold vendor links, `~` on estimated fastener counts, and affiliate/quantity disclosures. |
| `Print_Settings.md` | Polymer rationale (`ABS`/`ASA`/`PC`), `0.4mm` nozzle slicer recommendation table, shrinkage/cooling tips, and cross-links to `Assembly_Guide.md` & `BOM.md`. |
| `Assembly_Guide.md` | Upfront safety/torque/threadlocker notices, tools, prep steps, and numbered steps using `![Alt](Images/formatted_assembly_images/...)<br>` + `*Fig. N: ...*` captions (or `format_image.py --combine` / `<p align="center">` `width="45%"` pairs—zero inline `style="..."`). |
| `ALPHA_&_DIRECTION.md` / `Resources_and_Acknowledgements.md` | *(Optional)* Alpha/Beta support matrix, roadmap, Discord channel, community/vendor credits, technical writing partnership pitch, and Ko-fi block. |
| `LICENSE.md` | Full text or reference for **CC BY-NC-SA 4.0**. |
| `Images/`, `STEP_Files/`, `STL_Files/`, `Firmware/` | `Images/formatted_assembly_images/` (step cards) & `Images/full_images/` (hero renders); CAD/mesh directories (or `Releases/<version>/`); Klipper `.cfg` macros. Long reference property tables wrap in `<details><summary><b>...</b></summary>` with blank inner lines. |

---

## 4. Alchemical-3D Card Geometry (`format_image.py` Preset Targets)

All showcase and assembly PNGs use baked-in `RGBA` cards (opaque `#FFFFFF` interior unless full-bleed part crop, `20px` outer shadow margin on all 4 sides, `12px` corner radius, `2px` `#D0D0D0` border, `#000000` drop shadow at `92/255` alpha, `(0, +5px)` offset, `8.5px` Gaussian blur):
- **Vertical Assembly Step Card (`Alembic` preset)**: `630x763` card (`670x803` total PNG).
- **Dual Side-by-Side Combined Card**: `1242x720` card (`1282x760` total PNG) with `2px` `#E6E6E6` vertical center divider.
- **Sub-Assembly Card (`A3DP Gantry` preset)**: Fixed `620px` card height (`660px` total PNG height), proportional width.
