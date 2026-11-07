---
name: doc-and-card-studio
description: Use this skill when creating, rewriting, auditing, or unifying engineering repositories, READMEs, Assembly Guides, Bills of Materials (BOMs), Print/Fabrication Settings, reference guides, or documentation showcase images. Enforces accessible engineering prose, modular repository architecture, GitHub-native alerts, configurable link standards, and baked-in rounded-corner drop-shadow image card formatting via audit_repo_docs.py and format_image.py.
---

# Documentation & Showcase Card Studio (`doc-and-card-studio`)

This skill governs repository documentation structure, Markdown alert hygiene, relative link integrity ([`audit_repo_docs.py`](scripts/audit_repo_docs.py)), and `#FFFFFF` rounded-corner drop-shadow showcase image formatting ([`format_image.py`](scripts/format_image.py)) under **`1. Accuracy & Truth -> 2. Efficiency -> 3. Data Safety -> 4. Speed`**.

---

## 1. Pre-Flight Foundation Checks

1. **Modular Documentation Architecture**:
   - Keep top-level `README.md` focused on project overview, quick-start navigation, and verified capability highlights while linking cleanly to modular sub-documents (`BOM.md`, `Assembly_Guide.md`, `Print_Settings.md`, `ALPHA_&_DIRECTION.md`, or `docs/*.md`).
   - Read [`references/doc_templates.md`](references/doc_templates.md) **before** drafting `README.md`, `BOM.md`, `Print_Settings.md`, or `Assembly_Guide.md` (never scan unrelated sibling project repositories for style templates). Retain every canonical parameter row in the template (e.g., `Nozzle Diameter`, `Layer Height`, `Extrusion Width`, `Wall Perimeters`, `Top / Bottom Solid Layers`, `Infill`, and `Supports`, split into Rigid vs. Elastomer/`TPU` columns when flexible parts exist) instead of dropping unrecorded rows.
   - Inspect `<memory_root>/Standards_and_Specs/Standards_Index.md` and any workspace `.homunculus_brand.json` to load organization-specific style guides, canonical link tables, and disclosure rules on demand without hardcoding vendor or brand URLs inside the skill.
2. **Closed-World Specification & Conflict Lock**:
   - Every BOM row, fastener count, print setting, or dimensional specification must trace to verified repository sources (`verify_claims.py`) or carry an explicit `[TBD: <specific_missing_variable>]` marker (never borrow rigid `ABS`/`ASA` slicer settings onto `TPU` elastomers).
   - Whenever primary sources disagree on a fastener count, insert count, or hardware topology (e.g., `BOM.md` vs. CAD `<Project>_Hardware.md` bore telemetry or `Assembly_Guide.md`), insert an explicit **`[TBD: CONFLICT — <source_A> vs <source_B>]`** marker inline in the document body rather than smoothing over the discrepancy with qualitative prose notes.
3. **Pure-Stdlib Default + Lazy Optional Image Dependencies**:
   - Both `audit_repo_docs.py` and `format_image.py` load `PIL` (`Pillow`) and `numpy` lazily via `importlib.import_module` only when pixel-level card rendering is invoked, falling back to pure-stdlib PNG header inspection when `Pillow` is absent.

---

## 2. Step-Level Verification Gates

### Gate 1 — Format or Inspect Showcase Image Cards (`format_image.py`)
Format raw screenshots, CAD renders, or diagrams into `#FFFFFF` interior cards with `12px` corner radius, `2px` `#D0D0D0` border, and Gaussian drop shadow inside a `20px` transparent outer margin:

```bash
# Format a single image card
python3 <HOMUNCULUS_ROOT>/skills/doc-and-card-studio/scripts/format_image.py input.png -o docs/images/card_Formatted.png

# Combine two images side-by-side into a comparison card
python3 <HOMUNCULUS_ROOT>/skills/doc-and-card-studio/scripts/format_image.py left.png right.png --combine -o docs/images/pair_Formatted.png

# Inspect existing images without mutating them
python3 <HOMUNCULUS_ROOT>/skills/doc-and-card-studio/scripts/format_image.py --inspect docs/images/
```

### Gate 2 — Audit Repository Markdown & Link Integrity (`audit_repo_docs.py`)
Run deterministic repository documentation checks (UTF-8 encoding, broken relative Markdown/HTML links, GitHub-native `[!NOTE]`/`[!TIP]`/`[!IMPORTANT]`/`[!WARNING]`/`[!CAUTION]` alert syntax, and image card formatting):

```bash
python3 <HOMUNCULUS_ROOT>/skills/doc-and-card-studio/scripts/audit_repo_docs.py /path/to/repo

# Markdown-only audit (skip image pixel card checks on headless text-only repos)
python3 <HOMUNCULUS_ROOT>/skills/doc-and-card-studio/scripts/audit_repo_docs.py /path/to/repo --skip-image-check
```

### Gate 3 — Post-Draft Claim Verification (`verify_claims.py`)
After drafting or updating any technical README, BOM, or Assembly Guide, run `verify_claims.py` against the repository's primary CAD/config/BOM sources to confirm `0` unbacked claims.

---

## 3. Stop & Escalation Conditions

- **Broken Relative Link or Malformed Alert (`[FAIL]`)**: Halt and fix any broken relative path, unclosed HTML tag, or malformed GitHub alert block reported by `audit_repo_docs.py` before committing.
- **Missing Image Dependency on `--combine` / Format**: If `format_image.py` is called to render a new PNG card on a host without `Pillow`/`numpy`, it exits cleanly with an actionable install hint (`pip install Pillow numpy`) rather than crashing with an unhandled `ImportError`.
