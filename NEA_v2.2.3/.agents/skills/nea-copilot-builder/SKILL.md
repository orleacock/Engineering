---
name: "nea-copilot-builder"
description: "Project-scoped development, packaging, and validation runbook for the NetCom Engineering Assistant (NEA v2.2.3) Microsoft 365 Copilot Agent Builder suite. Enforces master-copy-only iteration, unprefixed agent/skill folder layouts, root-level SKILL.md zip packaging, strict YAML frontmatter rules, and 6-agent OpenXML separation of duties."
---

# NEA M365 Copilot Agent Builder Development & Packaging Skill (`nea-copilot-builder`)

This project-scoped skill governs all architecture, instruction authoring, Knowledge `.txt` synchronization, Skill `.zip` packaging, OpenXML script maintenance, and deployment gating for the **NetCom Engineering Assistant (`NEA v2.2.3`)** inside `/home/orin/Projects/Engineering/NEA_v2.2.3`. When onboarding a brand-new module (`NEA-AGT-007+`), pair this skill with `/home/orin/Projects/Engineering/Obsidian_Notes/Projects/NetCom_Engineering_Assistant/NetCom_Engineering_Assistant_Module_Launchpad.md`.

> [!IMPORTANT]
> **Compartment C Containment (Zero Leakage into `Homunculus` / `Alchemical-3D`)**:
> This skill lives exclusively inside `/home/orin/Projects/Engineering/NEA_v2.2.3/.agents/skills/nea-copilot-builder/SKILL.md` and is activated via Turn-1 dossier routing from `Obsidian_Notes/Projects/NetCom_Engineering_Assistant/NetCom_Engineering_Assistant.md`. It is **never** registered in global `~/.gemini/config/skills/` or `~/.gemini/config/rules/`, consuming `0` tokens outside `NEA` tasks, and `.agents/` is excluded from `NEA_v2.2.3_Delivery.zip`.

---

## 1. Pre-Flight Foundation Checks (Verify Before Any NEA Edit)

Before modifying any file in `/home/orin/Projects/Engineering/NEA_v2.2.3`:

1. **Master-Copy-Only Iteration Lock (`Zero Downloads/ Touches Mid-Task`)**:
   - All development, instruction tuning, Knowledge `.txt` edits, and script updates happen **exclusively** inside the master repository: `/home/orin/Projects/Engineering/NEA_v2.2.3/`.
   - **Never** read from, edit, or regenerate `/home/orin/Downloads/NEA_*` archives during development turns, and **never** stage or update Gmail drafts until the user explicitly declares a **deployment state** (e.g., *"prepare an email"* or *"package for testing"*).
   - During development iterations, run **only** `python3 Scripts/build_copilot_agents.py` (never `Scripts/package_nea_delivery.py`).
2. **Closed-World Source Authority (`Historical/` Quarantine)**:
   - Never read or copy requirements from `Historical/` (`External_Review_v1..v2`, `Internal_Review_v3`). Only the active `v2.2.3` files and `NEA_Governance_Register_v2.2.3.md` (`GOV-001`..`GOV-017`) govern the system.
3. **Direct `.txt` Knowledge Authoring (`GOV-017`)**:
   - The authoritative Standards, Workflows, and Behavior documents live directly inside `Copilot_Agents/<Agent_Slug>/Knowledge/*.txt` (with zero duplicate Skill or Python `.txt` files inside `Knowledge/`).
   - `Scripts/build_copilot_agents.py` (`sync_shared_knowledge_files()`) automatically propagates edits from the newest `.txt` file across all agents that share that file, mirrors `NEA_Governance_Register_v2.2.3.md` $\rightarrow$ `Knowledge/NEA_Governance_Register_v2.2.3.txt`, and bundles `Scripts/inspect_nea_workbooks.py` directly inside each `Skills/<skill-name>/<skill-name>.zip` at `scripts/inspect_nea_workbooks.py`.

---

## 2. Locked M365 Copilot Agent Builder Deployment Contract

Corporate Microsoft 365 Copilot environments enforce strict UI and parser rules. Every build produced by `Scripts/build_copilot_agents.py` must satisfy all four pillars below:

### Pillar A — Clean Unprefixed Agent Folders (`Copilot_Agents/`)
Whole-agent `.zip` package imports are blocked in NetCom's integrated Agent Builder UI (`Configure` tab). Agents are built 1-by-1 in the UI from clean, canonical folders:

1. **Allowed Top-Level Contents of `Copilot_Agents/`**:
   - `Agent_Builder_Guide.md`
   - `NEA_Package_Reviewer/`
   - `NEA_BOM_Builder/`
   - `NEA_CRL_Builder/`
   - `NEA_Catalog_Manager/`
   - `NEA_Repair_Tool/`
   - `NEA_Timesheet_Consolidator/`
   - *(Strictly banned: `00_`/`01_` folder prefixes, `Packages/` folder, or `.zip` agent bundles.)*
2. **Allowed Contents Inside Each `Copilot_Agents/<Agent_Slug>/` Folder**:
   - `Agent_Config.md` — Copy-paste blocks for `Name`, `Description`, `Instructions`, `Capabilities (Code Interpreter = ON)`, `Knowledge` file list, `Skills` upload list, and `Starter Prompts` (separate `Title` and `Prompt` code blocks).
   - `Instructions.txt` — Pure raw instruction text (`0` markdown wrapper fences around the file) for `Ctrl+A` $\rightarrow$ `Ctrl+C` pasting into the Agent Builder **Instructions** box.
   - `Knowledge/` — Contains **only `.txt` files** (`Ctrl+A` batch upload into Agent Builder Knowledge).
   - *(Strictly banned: `STEP_1_`/`STEP_2_`/`STEP_3_` filename prefixes, `manifest.json`, `declarativeAgent.json`, `color.png`, `outline.png`, or `.md`/`.py` files inside `Knowledge/`.)*
3. **Hard Field Character Limits**:
   - `Name`: `<= 30` characters (`NEA Package Reviewer`, `NEA BOM Builder`, `NEA CRL Builder`, `NEA Catalog Manager`, `NEA Repair Tool`, `NEA Timesheet Consolidator`).
   - `Description`: `<= 1,000` characters.
   - `Instructions.txt`: Hard M365 limit is `<= 8,000` characters; NEA engineering ceiling is **`<= 6,500` characters** (`>= 1,500` chars headroom) so future domain rules never trigger a re-architecture.
   - `Starter Prompts`: `<= 6` starters per agent.

### Pillar B — Bundled `<skill-name>.zip` (`SKILL.md` + `scripts/inspect_nea_workbooks.py`) & Hardened YAML Frontmatter (`Skills/`)
In M365 Copilot Agent Builder, `Skills -> Add skill -> Upload skill` **is** the one dialog that accepts a `.zip` package (`learn.microsoft.com/en-us/microsoft-365/copilot/extensibility/agent-builder-add-skills` and `declarative-agent-skills`), mounting the skill's `SKILL.md` and `scripts/` directory together inside the skill's packaged filesystem:

1. **Allowed Top-Level Contents of `Skills/`**:
   - `Skills_Deployment_Guide.md`
   - 3 unprefixed Core Guardrail Skill folders: `nea-anti-hallucination/`, `nea-workbook-entry-guard/`, `nea-verification-and-receipt/`.
   - *(Strictly banned: `01_`..`09_` folder prefixes, duplicate role-specific skill folders duplicating `Instructions.txt`, loose duplicate `.txt` files in `Skills/`, or duplicate `inspect_nea_workbooks.txt` / `NEA_*_Skill.txt` files inside `Copilot_Agents/*/Knowledge/`.)*
2. **Allowed Contents Inside Each `Skills/<skill-name>/` Folder**:
   - `SKILL.md`
   - `scripts/inspect_nea_workbooks.py`
   - `<skill-name>.zip`
   - **Bundled Zip Archive Rule**: `<skill-name>.zip` must contain **`SKILL.md` at the root of the `.zip` archive plus `scripts/inspect_nea_workbooks.py`** (`zf.namelist() == ["SKILL.md", "scripts/inspect_nea_workbooks.py"]`). Never nest `<skill-name>/SKILL.md` inside a wrapper directory, and ensure `SKILL.md` explicitly identifies `scripts/inspect_nea_workbooks.py`, when to run it, expected inputs, and expected outputs.
3. **Hardened `SKILL.md` YAML Frontmatter Rules**:
   - **Byte-0 Start**: Must start at byte `0` with `---\nname: "<skill-name>"\ndescription: "<clean_desc>"\n---\n\n` (`LF` `\n` line endings, UTF-8 with no BOM).
   - **`name` Field**: Lowercase letters, digits, and hyphens only (`<= 64` chars), wrapped in double quotes.
   - **`description` Field**: Single-line string (`<= 1,024` chars) wrapped in double quotes containing **zero YAML-sensitive special characters**:
     - **Banned characters in `description`**: `:` (colon), `[` or `]` (brackets), `<` or `>` (angle brackets), `!` (exclamation), `'` or `"` (inner quotes), `|` or `>`, or newlines.
   - **Zero `---` Horizontal Rules in Markdown Body (`dash_lines == [1, 4]`)**:
     - The Markdown body of `SKILL.md` after Line 4 must contain **zero standalone `---` lines**.
     - *Why*: Naive or greedy frontmatter regexes (`^---\r?\n([\s\S]*)\r?\n---`) or `content.split('---')` validators in Agent Builder will otherwise match from Line 1 down to a `---` divider inside the Markdown body, pulling Markdown headings/lists containing colons (`:`) into the YAML parser and throwing `"The SKILL.md frontmatter is not valid YAML"`.

### Pillar C — 6-Agent Separation of Duties & OpenXML Integrity (`Scripts/inspect_nea_workbooks.py`)
1. **Role-Scoped Telemetry (`--scope {review,bom,crl,catalog,repair,timesheet}`)**:
   - `NEA Package Reviewer` (`--scope review`, Mode 1 Read-Only): Audits active project deliverables (`Cover Sheet`, `Project BOM` active rows + `[3B]` `UOM=BX` bulk-box multiplier anomalies, `Cable Running List`, and CRL-to-BOM takeoffs). Never dumps raw Excel formula syntax into Sections 4/5; routes workbook formula/OpenXML plumbing (`Cover Sheet!B30:C30`, `Project BOM!G4`, `Lists!H1` zero-spill, `CRL` DataValidations) strictly to **`NEA Repair Tool`** and unreferenced catalog hygiene (`CAT-##`) strictly to **`NEA Catalog Manager`** in **Section 6 (`Cross-Duty Agent Advisories`)**.
   - `NEA BOM Builder` (`--scope bom`), `NEA CRL Builder` (`--scope crl`), `NEA Catalog Manager` (`--scope catalog`), `NEA Repair Tool` (`--scope repair` / `--repair`), and `NEA Timesheet Consolidator` (`--scope timesheet` / `--consolidate`).
2. **Non-Destructive OpenXML Repair, Desktop Excel ECMA-376 Integrity & Write Verification**:
   - `--repair` restores `Cover Sheet!B30:C30`, `Project BOM` `A8:I155` 3-tier `XLOOKUP` formulas, rescales `tblMaterials` `ref="A3:G<last_row>"` (`A3:G508`) and adds `<>0` to `Lists!H1` (`GOV-007`), expands `Fiber Assemblies!H` DataValidation (`H4:H1258`), normalizes `CRL` AutoFilter (`A2:P1087`), and calls `preserve_openxml_extensions()` without altering any user-entered project data (`Editable Cells Modified: 0`).
   - Mode 1 reviews require live `NEA-VRF-<12hex>` (`0 bytes modified`); Mode 2 writes/repairs/consolidations require `--verify-write ORIG EDITED` (`NEA-WRT-<12hex>` + `validate_openxml_package_integrity()` confirming `0` Desktop Excel ECMA-376 OpenXML issues).

### Pillar D — Human Reference Manual (`NEA_User_and_DevOps_Manual.md`) & Delivery Archive Gate (`Scripts/package_nea_delivery.py`)
1. **Human User & DevOps Manual (`NEA_User_and_DevOps_Manual.md` — `NEA-MAN-001`)**:
   - Lives at the root of `/home/orin/Projects/Engineering/NEA_v2.2.3/NEA_User_and_DevOps_Manual.md` for human engineers and DevOps (never uploaded into Copilot `Knowledge/` or `Skills/`).
   - Must be updated in lockstep whenever NEA version numbers, agent setup steps, starter/example prompts, or workbook expansion rules change, and must retain Orin Leacock's NetCom contact block (`Orin Leacock | Designer`, `oleacock@netcom1989.com`, `557-250-0254`).
2. **When to Run `Scripts/package_nea_delivery.py`**: Run `python3 Scripts/package_nea_delivery.py` **only** when the user explicitly requests a deployment build (e.g., preparing an email to `oleacock@netcom1989.com`).
3. **Single Archive Output (`.zip` Only — No `.zee`)**:
   - Cleans any stale `NEA_*` files in `/home/orin/Downloads/` and writes **only** `/home/orin/Downloads/NEA_v2.2.3_Delivery.zip` (which automatically ships `NEA_User_and_DevOps_Manual.md` at the root of the archive).
   - Excludes `.agents/`, `Historical/`, `__pycache__/`, `.git/`, and `.nea_inspect_cache.json`.

---

## 3. Step-Level Verification Gates (Run After Every NEA Edit)

After any edit to instructions, Knowledge `.txt` files, skills, or scripts in `/home/orin/Projects/Engineering/NEA_v2.2.3`:

1. **Compile & Run Built-In Contract Assertions**:
   ```bash
   python3 /home/orin/Projects/Engineering/NEA_v2.2.3/Scripts/build_copilot_agents.py
   ```
   - Must exit `0` and print `[PASS] All M365 Copilot Agent Builder & Skill ZIP/YAML Contract Checks Verified`.
2. **Verify Scoped OpenXML Telemetry (When `inspect_nea_workbooks.py` Changes)**:
   ```bash
   python3 /home/orin/Projects/Engineering/NEA_v2.2.3/Scripts/inspect_nea_workbooks.py /home/orin/Projects/Engineering/NEA_v2.2.3/Templates --scope review
   python3 /home/orin/Projects/Engineering/NEA_v2.2.3/Scripts/inspect_nea_workbooks.py /home/orin/Projects/Engineering/NEA_v2.2.3/Templates --scope repair
   ```

---

## 4. Stop & Escalation Conditions

Halt immediately and alert the user if any of the following occur:
1. Any agent's `Instructions.txt` exceeds `6,500` characters (approaching the `8,000`-character M365 hard limit).
2. Any `SKILL.md` fails YAML frontmatter validation (`dash_lines != [1, 4]` or special characters in `description`).
3. Any change to `inspect_nea_workbooks.py` alters `Templates/*.xlsx` during read-only inspection (`IMMUTABLE != PASS`) or modifies user-editable cells during `--repair`.
