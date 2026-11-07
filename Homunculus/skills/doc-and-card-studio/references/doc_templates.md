# Modular Hardware, Software & Catalog Documentation Skeletons (`doc_templates.md`)

Copy and adapt these canonical Markdown skeletons when creating a new engineering repository or unifying an existing one under `doc-and-card-studio`.

> [!IMPORTANT]
> **Inert Template Placeholders & Zero-Speculation Guardrail (`verifiable-accuracy.md`)**
> - All `<angle_bracket>` slots in this reference are **inert structural placeholders**—never copy raw placeholder syntax into published prose, and **never invent default hardware dimensions, fastener quantities, COTS component guesses, slicer parameters, or software benchmark numbers** to fill a table cell.
> - Every quantitative value, fastener callout, pin/port assignment, or CLI flag written into a live document must trace to verified Tier 1 project sources (`<memory_root>/Projects/<Project>/<Project>_Hardware.md`, `<Project>_Software.md`, `.cfg` / source files, vetted `BOM.md`, `<memory_root>/Standards_and_Specs/Fasteners_and_Inserts.md`, or explicit user input) and pass `verify_claims.py`.
> - Whenever a required value is unrecorded in verified sources, insert an explicit **`[TBD: <specific_missing_variable>]`** tag inline rather than guessing.
> - Organization-specific badges, community links, affiliate query parameters, and support footers are governed declaratively via `.homunculus_brand.json` (audited by `audit_repo_docs.py`) or organization templates in `<memory_root>/Templates/`.

---

## 1. `README.md` Skeleton (Modular Hardware Repository)

```markdown
<div align="center">

# <Project Name>

[![Status](https://img.shields.io/badge/Status-<Active_or_Alpha>-<Primary_Hex>.svg?labelColor=1E1E24)](#)
[![Category](https://img.shields.io/badge/Category-<Category_Label>-595959.svg?labelColor=1E1E24)](#)
[![License](https://img.shields.io/badge/License-<SPDX_License>-808080.svg?labelColor=1E1E24)](LICENSE.md)

<2–3 sentence high-level summary explaining what the hardware is, the engineering problem it solves, and its current development phase. If in Alpha/Beta, link to **[Alpha State & Development Direction](ALPHA_&_DIRECTION.md)**.>

<p align="center">
  <img src="Images/full_images/hero_left_formatted.png" width="45%" alt="<Project Name> View 1" />
  &nbsp;
  <img src="Images/full_images/hero_right_formatted.png" width="45%" alt="<Project Name> View 2" />
</p>

**[Bill of Materials](BOM.md)** &nbsp;•&nbsp; **[Assembly Guide](Assembly_Guide.md)** &nbsp;•&nbsp; **[Print Settings](Print_Settings.md)**

</div>

<br>

---

## Engineering Overview & Design Principles

<Explain the core engineering principle behind the project—why conventional setups fall short and how this geometry solves the mechanical, thermal, or kinematic trade-off using verified design facts only.>

> [!NOTE]
> **<Core Design Principle Title>**
> *"<1–2 sentence takeaway capturing the verified engineering trade-off in clear, accessible maker language—write fresh phrasing tailored to this hardware; never invent unverified performance ratios.>"*

## Key Specifications & Features

- **<Spec Category 1>:** <Verified hardware/compatibility detail or `[TBD: <missing_spec>]`>.
- **<Spec Category 2>:** <Verified dimensional/interface spec in inline code, e.g., `<verified_dimension_or_[TBD]>`—never deduce unlisted secondary dimensions>.
- **<Spec Category 3>:** <Verified functional benefit grounded in CAD, firmware, or empirical test data>.

> [!TIP]
> **<Companion Project / Ecosystem Synergy Title>**
> *<Cross-reference verified companion projects in the same engineering ecosystem where applicable, using canonical repository URLs validated by `audit_repo_docs.py`.>*

---

## Documentation Index

Everything needed to fabricate, assemble, and configure <Project Name>:

| Category | Description |
| :--- | :--- |
| **[Bill of Materials (BOM)](BOM.md)** | Complete checklist of printed parts, heat-set inserts, fasteners, and electronics needed. |
| **[Assembly Guide](Assembly_Guide.md)** | Illustrated, concise step-by-step walkthrough for assembling <Project Name>. |
| **[Print Settings](Print_Settings.md)** | Verified material selections and slicer parameters. |
| **[Alpha State & Direction](ALPHA_&_DIRECTION.md)** | Current hardware compatibility, active development roadmap, and feedback channel. *(Include row only if Alpha/Beta)* |

---

## License

This project is licensed under the **<Full License Name>**. See the [LICENSE.md](LICENSE.md) file for details.
```

---

## 2. `BOM.md` Skeleton (Concise & Source-Bound)

```markdown
# Bill of Materials (BOM)

This list contains all 3D-printed and physical hardware required to assemble <Project Name>.

*Note: Quantities for hardware fasteners must trace to verified CAD/assembly sources or carry an explicit `[TBD: <missing_qty>]` marker. Keeping spare hardware on hand is recommended.*

## 1. Printed Parts

Print these components using the parameters specified in [Print Settings](Print_Settings.md).

| Part File Name | Qty | Material | Color / Role | Description / Notes |
| :--- | :---: | :---: | :---: | :--- |
| `<Exact_Part_Filename.stl>` | `<qty_or_[TBD]>` | `<verified_material_or_[TBD]>` | Primary | `<Concise functional role—no speculative material claims>` |
| `<[a]_Exact_Accent_Part.stl>` | `<qty_or_[TBD]>` | `<verified_material_or_[TBD]>` | Accent | `<Concise functional role>` |

## 2. Fasteners & Physical Hardware

| Item | Qty | Description / Mating Joint |
| :--- | :---: | :--- |
| **[<Verified Insert Spec>](<verified_vendor_url_or_[TBD: sourcing_link_<item>]>)** | `<qty_or_[TBD]>` | `<Exact mating target part(s) from verified CAD/BOM>` |
| **[<Verified Fastener Spec>](<verified_vendor_url_or_[TBD: sourcing_link_<item>]>)** | `<qty_or_[TBD]>` | `<Exact sub-assembly / mating joint>` |

## 3. Electronics & Motion Hardware

| Item | Qty | Description |
| :--- | :---: | :--- |
| **[<Verified Component Name>](<verified_vendor_url_or_[TBD: sourcing_link_<item>]>)** | `<qty_or_[TBD]>` | `<Verified compatibility, voltage, or current requirements>` |

> [!IMPORTANT]
> **Part Flexibility & Modifications**
> Veering from the specified components may require modifying the 3D models to fit your hardware. **STEP files are provided** in the repository when available to make customization straightforward.
```

---

## 3. `Print_Settings.md` Skeleton (Zero Unbacked Slicer Defaults)

```markdown
# Print Settings for <Project Name>

Print structural components in **<verified_structural_materials_or_[TBD]>** *(if flexible/elastomer parts exist, add a single crisp line: `Print <part_group> in **TPU**`; include heated-chamber PLA/PETG thermal restrictions ONLY when parts operate inside a heated chamber or near hotends)*.

## Slicer Recommendations

*(Populate every row strictly from verified project files or user confirmation; if multi-material columns like Rigid vs. TPU are needed and a parameter is unrecorded, insert `[TBD: <specific_missing_variable>]` rather than guessing!)*

| Parameter | Recommended Value *(or Rigid vs. Flexible Columns)* |
| :--- | :--- |
| **Nozzle Diameter** | `<verified_nozzle_or_[TBD: nozzle_diameter]>` |
| **Layer Height** | `<verified_layer_height_or_[TBD: layer_height]>` |
| **Extrusion Width** | `<verified_extrusion_width_or_[TBD: extrusion_width]>` |
| **Wall Perimeters** | `<verified_wall_loops_or_[TBD: wall_loops]>` |
| **Top / Bottom Solid Layers** | `<verified_top_bottom_layers_or_[TBD: top_bottom_layers]>` |
| **Infill Type & Percentage** | `<verified_infill_or_[TBD: infill_percentage]>` |
| **Supports** | `<verified_support_rule_or_[TBD: support_requirements]>` |

### Calibration Notes
- **Dimensional Accuracy:** Verify filament flow and shrinkage scaling before printing full assemblies so bearings, pins, and heat-set inserts fit cleanly without splitting layers.

Once your parts are printed, proceed to the [Assembly Guide](Assembly_Guide.md) and cross-check hardware against the [Bill of Materials](BOM.md).
```

---

## 4. `Assembly_Guide.md` Skeleton (Concise Imperatives & Paramount-Only Reasoning)

```markdown
# <Project Name> Assembly Guide

Welcome to the assembly guide for <Project Name>.

*The machine you are building now will be a reflection of the effort committed to assembling it. Attention to detail is directly related to both the performance of the machine and its longevity.*

> [!CAUTION]
> **Fastener Torque & Threadlocker Notice**
> - **3D-Printed Parts:** Do **not** torque screws into printed plastic to metal ratings—stop turning immediately once the plastic begins to compress.
> - **Anaerobic Threadlocker:** Never allow liquid or vapor threadlocker (`Loctite 243` / `Loctite 222MS`) to contact **ABS, ASA, or PC** printed parts (causes rapid chemical stress-cracking), and never use red high-strength threadlocker.
> *(Include milled-aluminum torque values from `Fasteners_and_Inserts.md` ONLY if this specific assembly contains milled aluminum components; include metal-to-metal threadlocker grades ONLY if metal-to-metal threaded joints exist in the build.)*

> [!WARNING]
> **Builder Responsibility**
> This is an open-source engineering project. You are solely responsible for your own safety and the integrity of your equipment when building and operating this system.

---

## Step 1: Heat-Set Inserts

Press `<verified_qty_or_[TBD]>` `<verified_insert_spec>` brass heat-set inserts squarely into `<Exact_Target_Part.stl>` until flush with the surrounding surface. *(State in 1–2 crisp sentences—do NOT expand into multi-step soldering-iron tutorials or invent iron temperatures.)*

![Heat-Set Step](Images/formatted_assembly_images/step_heatset.png)<br>
*Fig. 1: Install `<verified_insert_spec>` heat-set inserts flush into `<Exact_Target_Part.stl>`.*

---

## Step 2: <Sub-Assembly or Stage Name>

<1–2 crisp imperative sentences per action binding exact `[Part.stl]` -> `[Verified Fastener Spec & Qty or [TBD: ...]]` -> `[Verified Mating Target]`. Do NOT repeat per-step plastic-torque warnings. Add `"why"` reasoning or `> [!IMPORTANT]` ONLY when a non-obvious alignment, tight-clearance frame collision, or seal requirement is verified in the project's docs/CAD.>

![Step 2 Illustration](Images/formatted_assembly_images/step_02.png)<br>
*Fig. 2: <Concise description of the exact assembly action shown>.*

---

### End of Assembly
<Project Name> is now assembled and ready for integration.
```

---

## 5. `ALPHA_&_DIRECTION.md` Skeleton (Active Alpha / Beta Hardware)

```markdown
# <Project Name>: Alpha State & Development Direction

<Project Name> is currently in an active **Alpha State** of development. This document outlines current hardware compatibility and staged upgrades as the design progresses toward Beta.

> [!WARNING]
> **Active Development Notice**
> While working prototypes perform well in testing, this system is actively evolving. Builders taking on the Alpha release should expect iterative refinements to geometry, hardware requirements, or the Bill of Materials (BOM) as the design matures.

---

## Current State (Alpha)

<1–2 concise paragraphs summarizing what has been empirically proven in the current alpha build without speculating on untested configurations.>

### Current Hardware Compatibility
- **<Category 1, e.g., Extruders>:** Direct support for **<Verified Hardware Name>**.
- **<Category 2, e.g., Hotends>:** Direct support for **<Verified Hardware Name>**.

---

## Roadmap & Intended Changes

> [!NOTE]
> **Highlighted Concepts & Planned Features**
>
> *The following expansions and refinements are currently under active investigation:*
> - **<Planned Feature 1>:** <Verified roadmap note>.
> - **<Planned Feature 2>:** <Verified roadmap note>.

*(Note: Features and concepts listed here are subject to change based on bench testing and community feedback.)*
```

---

## 6. `README.md` Skeleton (Software / CLI / Multi-Project Catalog Repository)

```markdown
# <Project or Package Name>

[![Status](https://img.shields.io/badge/Status-<Active_or_RC>-<Primary_Hex>.svg?labelColor=1E1E24)](#)
[![Runtime](https://img.shields.io/badge/Python-<Verified_Python_Version>-595959.svg?labelColor=1E1E24)](#)
[![License](https://img.shields.io/badge/License-<SPDX_License>-808080.svg?labelColor=1E1E24)](LICENSE)

<2–3 sentence technical overview stating what the software/CLI/catalog provides, its runtime dependency profile (e.g., pure Python stdlib vs. optional dependencies), and its verification architecture.>

---

## 1. Quick Start & Verification

```bash
# 1. Verify environment & help output
<verified_cli_entrypoint_command> --help

# 2. Run deterministic test / audit gate
<verified_test_or_audit_command>
```

---

## 2. Architecture & Module Index

| Module / Script | Role & Responsibility | Verification Gate |
| :--- | :--- | :--- |
| [`<script_or_module_path>`](<relative_path>) | `<Concise verified description from _Software.md or AST>` | `<Exact test or --audit flag>` |

> [!NOTE]
> **Closed-World Documentation Contract**
> All CLI flags, exit codes, and performance figures in this document are verified against [`<Project>_Software.md`](<relative_or_memory_path>) and `verify_claims.py`.

---

## 3. Detailed Documentation

- **[Quick Start & Setup Guide](docs/Quick_Start_and_Setup_Guide.md)** — Installation, environment configuration, and onboarding workflow.
- **[Commands & Prompts Reference](docs/Commands_and_Prompts_Reference.md)** — Complete CLI flag and workflow reference.
```
