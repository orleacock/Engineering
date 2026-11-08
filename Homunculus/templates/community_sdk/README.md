<div align="center">

# 🧩 Homunculus Community Extension SDK (`Apache-2.0`)

**Build & Share Custom Drop-In Add-Ons, Domain Skills, and Visual Studio Color Palettes**

[**🏠 Main Cover Page**](../../README.md) • [**🚀 Quick-Start Guide**](../../docs/Quick_Start_and_Setup_Guide.md) • [**🧠 Capabilities Guide**](../../docs/Capabilities_and_Architecture_Guide.md) • [**📟 Command Deck**](../../docs/Commands_and_Prompts_Reference.md) • [**❓ FAQ**](../../docs/FAQ.md)

</div>

---

## 1. Overview & Open-Source License (`Apache-2.0`)

Both the **Homunculus Core Engine** (`rules/`, `skills/`, `adapters/`, `scripts/`) and all starter templates inside `templates/community_sdk/` are open-source and released under the permissive **`Apache-2.0` License ([`LICENSE.md`](../../LICENSE.md))** with zero cost to entry.

That means you are 100% free to use the starter templates in this directory to build, publish, share, or sell your own custom:
1. **Drop-In Side-Loaded Add-Ons (`addons/<your-addon>/SKILL.md`)** for specialized engineering domains (e.g., RF layout checks, PLC ladder logic verification, FEA report templates, CNC post-processor rules).
2. **Custom Visual Studio Color Palettes (`Diagram_Palettes.json` entries)** matching your company, lab, or personal brand.
3. **Project Deliverable Templates (`Projects/<Project>/Templates/*.md`)** for BOMs, test cards, and client quotes.

---

## 2. How Drop-In Add-Ons Work (`Zero-Install Side-Loading`)

Homunculus separates **day-one universal engineering skills** (`skills/`) from **optional or domain-specific add-ons** (`addons/`):
- **Dormant When Needed**: Files placed in `Homunculus/addons/<addon-name>/` consume **0 tokens** during normal sessions.
- **Instant Activation (Two Ways)**:
  1. **Folder Drop-In**: Drag or copy `addons/<addon-name>/` into `Homunculus/skills/<addon-name>/`—your AI assistant immediately discovers it as an active skill with zero installer scripts or admin rights. (If you use generated IDE adapters like `AGENTS.md`, `CLAUDE.md`, or `.cursor/rules/`, refresh them via `python3 Homunculus/scripts/build_adapters.py --workspace /path/to/project --client all --prefer-copy`.)
  2. **On-Demand Prompt**: Leave the add-on in `addons/` and prompt your AI assistant:
     ```text
     Read Homunculus/addons/<addon-name>/SKILL.md and apply it to this task.
     ```
- **Clean Removal at Any Time**: Because optional modules in `addons/` are 100% decoupled from the Homunculus Core Engine, deleting an unneeded folder from `addons/` (or moving a module back from `skills/` to `addons/`) never breaks core memory, verification, adapter generation, or test suites.

---

## 3. Creating a Synergistic Custom Add-On (`addon_skeleton/`)

Copy [`addon_skeleton/SKILL.md`](addon_skeleton/SKILL.md) into `Homunculus/addons/<your-addon-name>/SKILL.md`.

### The 4 Rules of a Clean Homunculus Add-On
1. **Obey the Governing Priority Law**:
   `1. Accuracy & Truth -> 2. Efficiency -> 3. Data Safety -> 4. Speed`
2. **Delta-Only Instructions (Zero Core Rule Duplication)**:
   Do not copy-paste general anti-sycophancy, `[TBD: <var>]` abstention, or credential-safety boilerplate that already lives in the 3 Always-On Core Rules (`co-engineering-partner.md`, `verifiable-accuracy.md`, `data-and-credential-safety.md`). Keep your `SKILL.md` focused strictly on your domain's unique checks, schemas, and commands.
3. **Wire Into the Homunculus Backbone**:
   - **Memory**: Route Turn-1 context from `<memory_root>/Projects/<Project>/<Project>.md` (`AUTO-TREE`) rather than running blind directory searches.
   - **Truth Verification**: Require `verify_claims.py` before marking quantitative deliverables complete.
   - **Deferred Batching**: Defer heavy index or diagram rebuilds to `pre-commit-gate`.
4. **Verify With `skill-architect` Before Shipping**:
   If you have the Homunculus Core Engine installed, test your new add-on for overlap and structural compliance:
   ```bash
   # 1. Check whether your proposed capability already exists in Core Rules or Skills:
   python3 Homunculus/skills/skill-architect/scripts/audit_skill_hygiene.py \
     --check-new "your-addon-name: One-sentence description of what your add-on verifies or automates"

   # 2. Validate your finished SKILL.md structure, links, and token footprint:
   python3 Homunculus/skills/skill-architect/scripts/audit_skill_hygiene.py \
     --audit --strict-structure --target-skill your-addon-name
   ```

---

## 4. Customizing Visual Studio Color Palettes (Using Your Own Brand Colors)

The Homunculus GitHub storefront uses the **Alchemical-3D** brand palette (`#FF3985` Neon Pink & `#1E1E24` Dark Slate) because Homunculus is an Alchemical-3D product. **Your own projects are never locked to our colors.**

You can define your own brand palette in `Homunculus/templates/diagrams/Diagram_Palettes.json` (or prompt your AI assistant to add one for your organization) using this schema:

```json
{
  "my_company_dark": {
    "name": "My Company Dark Theme",
    "mode": "dark",
    "tokens": {
      "canvas_bg": "#0F172A",
      "panel_bg": "#1E293B",
      "node_bg": "#334155",
      "node_stroke": "#38BDF8",
      "accent_primary": "#38BDF8",
      "accent_secondary": "#818CF8",
      "accent_warn": "#F59E0B",
      "accent_danger": "#EF4444",
      "accent_ok": "#10B981",
      "text_primary": "#F8FAFC",
      "text_secondary": "#CBD5E1",
      "text_muted": "#94A3B8",
      "edge_default": "#64748B",
      "grid_line": "#1E293B"
    }
  }
}
```

Once added, render any architecture or pinout diagram in your custom palette via:
```bash
python3 Homunculus/skills/visual-studio/scripts/render_diagram.py \
  --spec ./diagram_spec.json \
  --palette my_company_dark \
  --output ./docs/images/system_map.svg \
  --strict
```
Or simply prompt your AI assistant:
> *"Render a system architecture diagram for this project using Visual Studio with our `my_company_dark` color palette."*
