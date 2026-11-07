# Antigravity / Gemini CLI Adapter (`adapters/antigravity/`)

Governed by: **`1. Accuracy & Truth -> 2. Efficiency -> 3. Data Safety -> 4. Speed`**

## Operating Modes
1. **Zero-Install Drop-In Mode (Corporate IT Safe):** Keep `Homunculus/` in your workspace and prompt:
   `Read Homunculus/HOMUNCULUS_START_HERE.md and operate under Homunculus rules and skills.`
2. **Workspace `.agents/{rules,skills}/` & `~/.gemini/config/` Binding:** Run:
   ```bash
   python3 Homunculus/scripts/build_adapters.py --workspace /path/to/project --client antigravity
   ```
   This populates `.agents/rules/*.md` (`trigger: always_on`), `.agents/skills/*`, `.geminiignore`, and (when `--global-agy-config-dir ~/.gemini/config` is passed) links/copies `rules/*.md`, `skills/*`, and empty `hooks.json` (`{}`) into `~/.gemini/config/`.
