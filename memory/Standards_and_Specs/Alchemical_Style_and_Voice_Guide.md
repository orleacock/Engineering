---
title: "Alchemical-3D Style, Voice & Formatting Guide"
entity: "Alchemical-3D"
compartment: "public"
last_synced: "2026-11-06"
---

# Alchemical-3D Style, Voice & Formatting Guide

This reference defines the writing voice, pedagogical depth, Markdown conventions, and visual asset rules for all **Alchemical-3D** GitHub repositories.

---

## 1. Audience & Pedagogical Calibration

- **Target Audience**: Human makers of all skill levels—from first-time printer modders to experienced print-farm operators and Voron/CoreXY builders.
- **Role-Matched Explanation Depth (Paramount-Only Reasoning in Build Guides)**:
  - **Installation & Print Guides (`Assembly_Guide.md`, `Print_Settings.md`, `BOM.md`)**: Keep instructions **concise and direct**. Write standard operations (pressing heat-sets flush, seating fasteners) in **1–2 crisp sentences** without multi-step tool micro-tutorials or obvious material lectures (`"Print in TPU"` needs no elastomer explanation). Include `"why"` reasoning **only when paramount AND verified** in the project's hardware/standards—never fabricate hypothetical collision callouts, and place global torque/chemical rules once upfront:
    - *Alignment / Clearance Hazard*: Why a bracket or idler must sit flush/square so the next sub-assembly aligns without contacting the frame or linear motion path.
    - *Mechanical / Pneumatic Seal*: Why an idler needs shims on both sides (preventing flange rub) or why an O-ring must seat before clamping (preventing air leaks).
    - *Thermal / Chemical / Torque Hazard*: Why PLA/PETG fail near hotends or inside heated chambers, why printed plastic fasteners stop at initial compression, and why anaerobic threadlocker (`Loctite 243` / `222MS`) must never contact ABS, ASA, or PC.
  - **Overview & Reference Guides (`README.md` philosophy, `ALPHA_&_DIRECTION.md`, `Maker-Tools/*.md`)**: Provide moderate technical depth explaining design trade-offs and translating ASTM/ISO metrics into plain maker terms (e.g., `Maker-Tools/Filament_Guide.md` TDS *"Layman's Description"* column).

---

## 2. Voice & Tone Pillars

1. **Pragmatic Co-Builder**:
   - Direct, encouraging, and grounded in workshop reality. Address the builder as a peer (`"Ensure your heat-set inserts sit flush..."`, `"Stop turning as soon as the plastic begins to compress."`).
2. **Signature Epigraphs & Analogies**:
   - Open organization profiles and major overviews with the brand motto:
     > *"Transmuting ideas into reality, layer by layer."*
   - Frame precision assembly guides with the user-confirmed builder's craft epigraph:
     > *The machine you are building now will be a reflection of the effort committed to assembling it. Attention to detail is directly related to both the performance of the machine and its longevity.*
   - Use concrete analogies inside `Mode A` overview callouts when explaining unconventional engineering (e.g., `Alembic`'s targeted nozzle-exit air delivery vs. broad blower/CPAP wash as **Scalpel vs. Sledgehammer**—never conflate `Pneuma`'s remote pump role with `Alembic`'s toolhead manifold, and never parrot existing analogies onto unrelated hardware).
3. **Controlled Levity vs. Serious Safety**:
   - Light, self-aware maker humor is welcome in non-critical sections (e.g., ` *(for now...)*`, or joking about maker attire while diagnosing a hotend blob).
   - **Never** use humor inside `> [!CAUTION]` or `> [!WARNING]` blocks covering torque limits, mains voltage, toxic styrene/VOC fumes, or builder liability. Keep safety and hardware protection notices crisp and unambiguous.

---

## 3. Repository & Document Architecture

### Canonical File Set (Hardware Repositories)
Every hardware project repository (`Alembic_Toolhead`, `Pneuma_Remote_Air`, `A3DP_Gantry_Assembly`, `Pestle_Rotational_Bowden`, `Retort`, etc.) must use the **modular multi-file structure** rather than cramming everything into a single monolithic `README.md`:

| File | Purpose |
| :--- | :--- |
| `README.md` | Project storefront: centered hero block, badges, side-by-side renders, quick-nav links, philosophy/capabilities, key specs, Documentation Index table, related projects, license, and Ko-fi footer. |
| `BOM.md` | Categorized Bill of Materials (`1. Printed Parts`, `2. Fasteners & Physical Hardware` / Kit vs. Self-Sourced, `3. Electronics and Hardware`) with affiliate disclosure and quantity disclaimers. |
| `Print_Settings.md` | Material selection rationale (ABS/ASA/PC), 0.4mm nozzle slicer recommendation table, shrinkage/cooling pro-tips, and links to `Assembly_Guide.md` and `BOM.md`. |
| `Assembly_Guide.md` | Upfront safety/torque/threadlocker notices, required tools, preparation steps (jigs, heat-set inserts), numbered assembly steps with formatted figure cards and `*Fig. N:*` captions. |
| `ALPHA_&_DIRECTION.md` | *(Optional — Alpha/Beta projects)* Current development state, supported extruders/hotends, staged roadmap concepts, and Discord feedback channel. |
| `Resources_and_Acknowledgements.md` | *(Optional)* Community credits, vendor links, Partner with Alchemical-3D technical writing pitch, and Ko-fi support block. |
| `LICENSE.md` | Full text or reference for **CC BY-NC-SA 4.0**. |

### Directory Naming Conventions
- `Images/` (with `Images/formatted_assembly_images/` for step-by-step cards and `Images/full_images/` for hero renders).
- `STEP_Files/` and `STL_Files/` (or `Releases/<version>/` when versioned bundles are distributed).
- `Firmware/` for Klipper `.cfg` macros and microcontroller configs.

---

## 4. Markdown Formatting Conventions

### 4.1 Centered Hero Header (`README.md`)
Always open `README.md` with a `<div align="center">` block containing:
1. `# [Emoji] Project Name`
2. Shields.io badge row (`Status`, `Cooling`/`Kinematics`/`Drive`, `Ecosystem-Alchemical--3D-purple`, optional `Ecosystem-A3DP-orange`, `License-CC BY--NC--SA 4.0-lightgrey`).
3. Concise 2–3 sentence project pitch (with link to `ALPHA_&_DIRECTION.md` if in Alpha/Beta).
4. Side-by-side hero image block (`<p align="center">` with two `<img ... width="45%" />` separated by `&nbsp;`, or a single wide banner at `width="80%"`).
5. Quick navigation bar separated by `&nbsp;•&nbsp;`:
   `**[Bill of Materials](BOM.md)** &nbsp;•&nbsp; **[Assembly Guide](Assembly_Guide.md)** &nbsp;•&nbsp; **[Print Settings](Print_Settings.md)**`

### 4.2 Section Headers & Dividers
- Prefix all H2 (`##`) headers with a relevant emoji:
  - `## 🌬️ The Philosophy of ...` / `## 🌪️ System Capabilities & Benefits`
  - `## ✨ Key Specifications & Features`
  - `## 📚 Documentation Index`
  - `## 🎛️ Firmware & Control`
  - `## 🔗 Related Projects`
  - `## 📸 Quick Glimpse`
  - `## ⚖️ License`
- Separate major top-level sections with `---` (and use `***` before the final License / Ko-fi footer block and the standard AI transparency disclosure line `*Documentation prepared with AI editorial assistance • Engineered & maintained by Alchemical-3D.*`).

### 4.3 GitHub-Native Alerts (Never Legacy Bold Blockquotes)
- **Always** use GitHub's native blockquote alert syntax:
  - `> [!NOTE]` — Background context, architecture updates, affiliate disclosures, or kit notes.
  - `> [!TIP]` — Assembly tricks, companion project cross-promotions, shimming/alignment advice.
  - `> [!IMPORTANT]` — Critical build prerequisites, frame modifications, threadlocker rules, or alpha disclaimers.
  - `> [!WARNING]` — Belt over-tensioning, chemical degradation (threadlocker on ABS/ASA), minimum bend radius, or builder liability.
  - `> [!CAUTION]` — Fastener torque limits (stripping aluminum or crushing 3D-printed plastic), incompatible material warnings (PLA/PETG near hotends), or valve/electrical hazards.
- Format the alert title in **bold** on the line immediately following the `[!TYPE]` tag (do **not** use `###` headings inside alerts, and do **not** use legacy `> **NOTE:**` syntax):
  ```markdown
  > [!CAUTION]
  > **Important Torque Notice**
  > The milled portions of this assembly are **aluminum** (~1.0 to 1.5 Nm for M3). However, **the 3D-printed parts SHOULD NOT be overtightened.** Stop turning as soon as the plastic begins to compress.
  ```

### 4.4 Tables
- **Documentation Index Table**: Left-aligned `| Category | Description |` (`| :--- | :--- |`) with emoji + bold link in column 1 (`📋 **[Bill of Materials (BOM)](BOM.md)**`).
- **BOM Tables**: Center-align the quantity column (`| :--- | :---: | :--- |`).
  - Wrap `.stl` / `.step` filenames in backticks (`` `Lower_Body.stl` ``).
  - Wrap linked hardware items in bold links (`**[M3 Heat Set Inserts](https://...)**`).
  - Prefix estimated fastener counts with `~` (e.g., `~8`).
- **Collapsible Data Tables**: For long reference guides (like `Filament_Guide.md`), wrap per-item technical property tables inside `<details><summary><b>View Material Properties (Rough Average)</b></summary> ... </details>` with a blank line after `<summary>` and before `</details>`.

### 4.5 Assembly Step Figures & Captions
In `Assembly_Guide.md`, format single step illustrations with Markdown image syntax followed by `<br>` and an italicized figure caption:
```markdown
![Heat-Set Intake](Images/formatted_assembly_images/heatset_intake.png)<br>
*Fig. 2: Install (2) M3 inserts into the intake component.*
```
When showing two images side-by-side in an assembly step, either:
1. Combine them into a single composite card using `scripts/format_image.py --combine left.png right.png -o combined.png` (preferred), **or**
2. Use a centered block with two pre-formatted PNGs (never with inline `style="..."`):
   ```markdown
   <p align="center">
     <img src="Images/formatted_assembly_images/step_left.png" width="45%" alt="Step Left" />
     &nbsp;
     <img src="Images/formatted_assembly_images/step_right.png" width="45%" alt="Step Right" />
   </p>
   ```

---

## 5. Image Formatting Specification (Rounded Corners + Border + Drop Shadow)

### Why Baked-In Card Formatting Is Load-Bearing
1. **GitHub Strips Inline CSS**: GitHub's HTML sanitizer (`html-pipeline`) strips all `style="..."` attributes (`border-radius`, `box-shadow`, `margin`) from `<img>` tags.
2. **GitHub Dark Mode Contrast**: Raw CAD renders exported with transparent backgrounds and dark charcoal/black parts (`RGB ~40,45,50`) become invisible against GitHub's dark theme canvas (`#0d1117`).

### Canonical Pixel Specification
Every showcase and assembly image must be processed via `scripts/format_image.py` to bake the card into the PNG's `RGBA` channels:
- **Card Interior Background (Locked Protocol)**: Opaque `#FFFFFF` (pure white) for all hero renders, exploded views, and assembly step images. (If a raw CAD render has a neutral studio grey backdrop, `scripts/format_image.py` automatically whitens the studio backdrop to `#FFFFFF` while preserving foreground parts and cast ground shadows. Full-bleed close-up crops where a CAD part fills the frame are preserved without adding a white mat.)
- **Outer Transparent Shadow Margin**: `20px` on all 4 sides (`Left=20, Top=20, Right=20, Bottom=20`). Total PNG size is `(Card_W + 40) x (Card_H + 40)`.
- **Card Corner Radius**: `12px` (Pillow `rounded_rectangle` radius matching `Alembic_Toolhead` reference cards to 0-pixel diff).
- **Card Border**: `2px` solid `#D0D0D0` (`RGBA(208, 208, 208, 255)`).
- **Drop Shadow**: Black (`#000000`), initial alpha `92/255` (`~36%`), offset `(dx=0, dy=+5px)`, Gaussian blur radius `8.5px`.
- **Standard Card Dimensions**:
  - Vertical Assembly Step Card (`Alembic` style): `630x763` card (`670x803` total PNG with `20px` margins).
  - Dual Side-by-Side Combined Card: `1242x720` card (`1282x760` total PNG with `20px` margins) and a `2px` `#E6E6E6` vertical center divider.
  - Sub-Assembly Card (`A3DP Gantry` style): Fixed `620px` card height (`660px` total PNG height), variable width proportional to part aspect ratio.
