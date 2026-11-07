# Claude Cowork Desktop & Skill Zip Adapter (`adapters/claude_cowork/`)

Governed by: **`1. Accuracy & Truth -> 2. Efficiency -> 3. Data Safety -> 4. Speed`**

## Operating Modes
1. **Designated Local Working Folder (Zero-Install Drop-In):** Place `Homunculus/` inside the local folder granted to Claude Cowork and instruct Cowork: `Read Homunculus/HOMUNCULUS_START_HERE.md`.
2. **Uploadable Skill `.zip` Bundles:** Generate standalone `.zip` skill packages for GUI upload via:
   ```bash
   python3 Homunculus/scripts/build_adapters.py --workspace /path/to/project --client claude_cowork --package-cowork-zips
   ```
