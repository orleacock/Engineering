---
title: "Image Formatting, Style & Disclosure Standards"
entity: "Alchemical-3D"
compartment: "public"
last_synced: "2026-11-06"
---

# 🎨 Image Formatting, Style & Disclosure Standards

Referenced by [`README.md`](../README.md), paired with [`Alchemical_Style_and_Voice_Guide.md`](Alchemical_Style_and_Voice_Guide.md) and [`Alchemical_Ecosystem_Links_and_Brand.md`](Alchemical_Ecosystem_Links_and_Brand.md), and enforced by `/home/orin/Projects/Engineering/Homunculus/skills/doc-and-card-studio/SKILL.md` (`audit_repo_docs.py` + `format_image.py`).

---

## 1. Image Card Formatting Pipeline (`format_image.py`)
- **Why:** GitHub strips inline CSS (`border-radius`, `box-shadow`), and dark CAD parts vanish on GitHub Dark Mode.
- **Locked Spec:**
  - `RGBA` PNG with `20px` transparent outer drop-shadow margin on all 4 sides.
  - `#FFFFFF` solid white interior card background with `12px` corner radius and `2px` `#D0D0D0` border.
  - Drop shadow: `dy=+5px`, `blur=8.5`.
- **Tool:** `skills/doc-and-card-studio/scripts/format_image.py`

## 2. Markdown & Alert Invariants
- **GitHub-Native Alerts Only:** `> [!NOTE]`, `> [!TIP]`, `> [!IMPORTANT]`, `> [!WARNING]`, `> [!CAUTION]` with a bold title on line 2. Never use legacy `> **NOTE:**`.
- **Canonical Links & Affiliate Tags:**
  - Discord: `https://discord.gg/aE49DW2xXe`
  - Ko-fi: `https://ko-fi.com/alchemical3d`
  - KB-3D Affiliate Parameter: `?affp=6182`
  - West3D Affiliate Parameter: `dt_id=Alchemical3D`

## 3. Standard AI Assistance Transparency Footer
Append to the very bottom of generated documentation files:

```markdown
***
*Documentation prepared with AI editorial assistance • Engineered & maintained by Alchemical-3D.*
```

## 4. Canonical Color Templates
- **Brand & Public Web/CAD Assets:** Use [`Alchemical3D_Color_Template`](../Templates/Color_Palettes/Alchemical3D_Color_Template.md) (`#FF3985` / `#C90448` / `#808080` / `#595959`).
- **Local Machine, KDE Konsole & Obsidian Diagrams:** Use [`Gruvbox_Local_Color_Template`](../Templates/Color_Palettes/Gruvbox_Local_Color_Template.md) (Gruvbox Dark).
