<div align="center">

# 📟 Homunculus Prompts, Commands & Arguments Reference Deck

**Everyday Plain-English Chat Prompts & Optional Terminal Commands Across Windows, macOS & Linux**

[**🏠 Main Cover Page**](../README.md) • [**🚀 Quick-Start Guide**](Quick_Start_and_Setup_Guide.md) • [**🧠 Capabilities Overview**](Capabilities_and_Architecture_Guide.md) • [**🗂️ Memory Guide**](Memory_Setup_README.md) • [**🛡️ Data Safety**](Developer_Data_Safety_Guidelines.md) • [**❓ FAQ**](FAQ.md)

</div>

---

> [!TIP]
> **How Most Users Run Homunculus: Just Ask in Plain English!**
> **95% of your day-to-day workflow happens automatically through normal chat** (`1. Accuracy & Truth -> 2. Efficiency -> 3. Data Safety -> 4. Speed`). Once your AI assistant is pointed at Homunculus, it runs the right tools behind the scenes whenever you ask a question, write code, or draft docs.
> - **Section 1** gives you copy-pasteable **Plain-English Chat Prompts** for everyday tasks.
> - **Sections 2–7** provide the **Terminal Command & Argument Reference** for power users who want to invoke tools directly from a terminal or script on **Windows (`python` / `py -3`), macOS, or Linux (`python3`)**.

---

## 📑 Quick-Jump Index

1. [Everyday Plain-English AI Prompts (`Automatic Mode — Recommended`)](#1-everyday-plain-english-ai-prompts-automatic-mode--recommended)
2. [Workspace Setup & Client Config Commands](#2-workspace-setup--client-config-commands)
3. [Project Memory, Telemetry & Session Handoff Commands](#3-project-memory-telemetry--session-handoff-commands)
4. [Fact-Checking, Hardware Inspection & Safe Sandbox Commands](#4-fact-checking-hardware-inspection--safe-sandbox-commands)
5. [Skill Architect, Hygiene & Engineering Learning (`Brief+`) Commands](#5-skill-architect-hygiene--engineering-learning-brief-commands)
6. [Data Privacy & Portability Check Commands](#6-data-privacy--portability-check-commands)
7. [Diagram Studio, Doc Polisher & Voice Add-On Commands](#7-diagram-studio-doc-polisher--voice-add-on-commands)

---

## 1. Everyday Plain-English AI Prompts (`Automatic Mode — Recommended`)

Drop the `Homunculus/` folder into your project and paste any of these natural prompts into your AI chat:

| What You Want to Do | Plain-English Prompt to Give Your AI Assistant |
| :--- | :--- |
| **Start Using Homunculus (Zero-Install)** | `"Read Homunculus/HOMUNCULUS_START_HERE.md and operate under Homunculus rules and skills for this project."` |
| **Set Up Project Memory for a Repo** | `"Initialize Homunculus project memory for this repository and map our current files and project state."` |
| **Save Your Stopping Point Before a Break** | `"Save our current stopping point, verification status, and next-session discussion points to our project Session Handoff."` |
| **Pick Up a Project After Days/Weeks Away** | `"Kickstart our project from memory, check if any files changed while I was away, and show our next steps."` |
| **Fact-Check a Document, BOM, or Guide** | `"Check this document against our project source files to verify all numbers, units, and file references."` |
| **Learn How `<X>` Impacts `<Y>` (`Brief+`)** | `"/teach-me about '<Subject X>' impact on '<Subject Y>'"` *(Runs in a throw-away subagent and saves a verified `Brief+` to `study_briefs/` without cluttering your active window.)* |
| **Create or Audit Custom AI Skills** | `"Use Skill Architect to check if this new workflow overlaps our existing skills, or run a non-destructive hygiene check."` |
| **Generate a Diagram in Your Brand Colors** | `"Render an SVG architecture diagram for this system using our custom color palette."` |
| **Steer Background Subagent Speed vs. Depth** | Add **`[lite]`** (quick lookup), **`[fast]`** (standard parallel scan), or **`[deep]`** (thorough review) to the end of any prompt. |
| **Activate Personal Writing Voice Matching** | `"Read Homunculus/addons/author-voice-cadence/SKILL.md and calibrate to my writing samples in corpus_inbox/."` |
| **Activate Multi-Account Gmail MCP Triage** | `"Read Homunculus/addons/gmail-workspace-assistant/SKILL.md and triage our inbox threads safely."` |
| **Run Pre-Commit Wrap-Up Checks** | `"Run our pre-commit wrap-up checks so we are ready to commit."` |

---

## 2. Workspace Setup & Client Config Commands

Use these optional commands if you want to check environment readiness or auto-generate config files for Cursor, Claude, Antigravity, or `AGENTS.md`:

| Tool | Key Arguments & Options | What It Does |
| :--- | :--- | :--- |
| **`install.ps1` *(Windows)*** | `-Check`, `-Workspace <PATH>`, `-Client <NAME>`, `-MemoryMode {headless,obsidian}`, `-PreferCopy`, `-UseSymlinks`, `-InstallGitHooks`, `-NoAdapters`, `-DryRun` | Checks readiness or configures client startup files in a Windows workspace without requiring Admin rights. |
| **`install.sh` *(macOS / Linux)*** | `--check`, `--workspace <PATH>`, `--client <NAME>`, `--memory-mode {headless,obsidian}`, `--no-adapters`, `--prefer-copy`, `--install-git-hooks`, `--dry-run` | Checks readiness or configures client startup files and optional Git safety hooks on macOS and Linux. |
| **`homunculus_paths.py`** | `--check`, `--workspace <PATH>`, `--init-config`, `--memory-mode {headless,obsidian}`, `--ensure-fresh`, `--map <SCRIPT_OR_ALL>`, `--sync-maps`, `--json` | Verifies cross-platform workspace paths, writes `.homunculus.json`, refreshes `Directory/` trees, and prints or auto-heals `#Lstart-Lend` script navigation maps. |
| **`build_adapters.py`** | `--workspace <PATH>`, `--client {all,agents-md,antigravity,claude-code,claude-cowork,cursor}`, `--prefer-copy` | Generates native rule/skill bindings and context-ignore files for your chosen AI client(s). |

```bash
# Check environment readiness (macOS / Linux):
python3 Homunculus/scripts/homunculus_paths.py --check

# Check environment readiness (Windows PowerShell):
python Homunculus\scripts\homunculus_paths.py --check

# Generate native config files for all supported AI clients in the current project:
python3 Homunculus/scripts/build_adapters.py --workspace . --client all --prefer-copy
```

---

## 3. Project Memory, Telemetry & Session Handoff Commands

Your AI runs `sync_memory.py` automatically when managing project notes, or you can invoke it directly:

| Argument / Flag | Default | What It Does |
| :--- | :--- | :--- |
| `--memory-root <PATH>` *(or `--vault`)* | `./memory` | Folder where your project memory notes live. |
| `--init-memory` *(or `--init-vault`)* | `False` | Creates a fresh memory folder structure (`Projects/`, `Tasks/`, `Standards_and_Specs/`, `Templates/`, `Diagrams/`). |
| `--mode {headless,obsidian}` | `headless` | Sets standard Markdown mode (`headless`, default) or Obsidian Vault mode (`obsidian`). |
| `--convert-mode {headless,obsidian}` | `None` | Switches an existing memory folder between standard Markdown and Obsidian mode anytime. |
| `--init-project <NAME>` | `None` | Creates a new project hub folder (`<Name>.md`, hardware/software index, lessons learned, and `Quarantine/`). |
| `--repo-path <PATH>` | `.` | Links the project hub to your code or hardware repository path. |
| `--type {hardware,software,hybrid}` | `software` | Selects whether to track software details, hardware/CAD details, or both. |
| `--entity <NAME>` | `Default_Entity` | Tags the project with an owner or client name so separate clients never mix. |
| `--project <NAME>` | `None` | Selects which project to read, update, hand off, or resume. |
| `--section <SECTION>` | `all` | Prints a targeted section (`all`, `concept`, `inventory`, `specs`, `hazards`, `architecture`, `tbd`, `tasks`, `lessons`, `handoff`, `hardware`, `software`) with inline task transclusion. |
| `--sync-software` / `--sync-hardware` | `False` | Refreshes the project's software or hardware summary tables from your repo files. |
| `--sync-tree` / `--sync-trees` / `--check-stale` | `False` | Updates one project's file map (`--sync-tree --project <P>`), batch-updates all projects (`--sync-trees`), or checks for repo changes (`--check-stale`). |
| `--save-handoff` | `False` | Saves your stopping point, blockers, and next-session discussion points (`--stopped-at`, `--next-steps`, `--discussion`, or `--handoff-file`). |
| `--kickstart` | `False` | Loads your saved stopping point and checks if any repository files changed while you were away. |
| `--create-project-template <NAME>` | `None` | Saves a reusable document template inside `Projects/<Project>/Templates/`. |
| `--tasks` / `--umbrella <FILTER>` | `False` | Lists all open `- [ ]` tasks across `Tasks/*.md` (or filtered to a specific client/domain umbrella). |
| `--tbd-ledger` | `False` | Scans all `Projects/<P>/<P>.md` hubs and prints a consolidated ledger of open `[TBD: ...]` and `[CONFLICT]` items. |
| `--sync-visuals` / `--export-canvas` | `False` | Refreshes `README.md` project index, task rollups, Obsidian `.base`/`graph.json` views, and optional `.canvas` topology map (`--canvas-out-dir`). |
| `--audit` *(or `--check`)* | `False` | Checks all memory notes for broken links or accidental cross-client references. |

```bash
# 1. Initialize project memory and onboard a project:
python3 Homunculus/skills/project-memory/scripts/sync_memory.py \
  --memory-root ./memory --init-memory --mode headless --default-entity "My_Team"

python3 Homunculus/skills/project-memory/scripts/sync_memory.py \
  --memory-root ./memory --init-project "My_Project" --repo-path . --type software --entity "My_Team"

# 2. Save a Session Handoff before taking a break:
python3 Homunculus/skills/project-memory/scripts/sync_memory.py \
  --memory-root ./memory --project "My_Project" --save-handoff \
  --stopped-at "Finished API validation; all tests passing." \
  --next-steps "1. Review user guide | 2. Tag release" \
  --discussion "Decide whether to bundle the custom theme palette."

# 3. Kickstart the project when you return days or weeks later:
python3 Homunculus/skills/project-memory/scripts/sync_memory.py \
  --memory-root ./memory --project "My_Project" --kickstart
```

---

## 4. Fact-Checking, Hardware Inspection & Safe Sandbox Commands

| Tool | Key Arguments & Options | What It Does |
| :--- | :--- | :--- |
| **`verify_claims.py`** | `--target <FILE>`, `--sources <PATH> [...]`, `--entity <NAME>`, `--dump-whitelist`, `--fail-on-tbd`, `--strict-provenance`, `--json` | Checks numbers, units, inline math (`[CALC: ...]`), part callouts, and file citations in `--target` against your authoritative `--sources` files. |
| **`inspect_hardware_ecosystem.py`** | `--repo <PATH>`, `--project <NAME>`, `--memory-root <PATH>`, `--check-cache`, `--sync-manifest`, `--json-out <FILE>` | Inspects `.step`/`.stl` 3D CAD dimensions, hole sizes, and `.cfg` firmware pinouts, updating `<Project>_Hardware.md`. |
| **`sandbox_runner.py`** | `--mode {dry-run,compare-light,compare-full}`, `--target-dir <DIR>`, `--cmd "<CMD>"`, `--fault-case "<SETUP> :: <CHECK>"` | Runs commands and tests inside an isolated temporary sandbox so live workspace files are never modified during testing. |

```bash
# 1. Verify all numbers, units, and file citations in a document against your project sources:
python3 Homunculus/skills/claim-verification/scripts/verify_claims.py \
  --target ./README.md \
  --sources ./src ./memory/Projects/My_Project/My_Project.md

# 2. Inspect 3D CAD (.step/.stl) and firmware (.cfg) files in a hardware repository:
python3 Homunculus/skills/subagent-orchestrator/scripts/inspect_hardware_ecosystem.py \
  --repo ./hardware_repo --memory-root ./memory --sync-manifest

# 3. Test a command safely inside an isolated sandbox:
python3 Homunculus/skills/engineering-sandbox/scripts/sandbox_runner.py \
  --mode dry-run --target-dir . --cmd "python3 -m unittest discover -s tests"
```

---

## 5. Skill Architect, Hygiene & Engineering Learning (`Brief+`) Commands

| Tool | Key Arguments & Options | What It Does |
| :--- | :--- | :--- |
| **`audit_skill_hygiene.py`** | `--check-new "<NAME>: <DESCRIPTION>"`, `--audit`, `--strict-structure`, `--target-skill <NAME>`, `--root <PATH>`, `--json` | **Mode 1 (`--check-new`)**: Checks if a new skill idea overlaps existing rules or skills; **Mode 2 (`--audit`)**: Reviews existing skills and script navigation maps (`#Lstart-Lend`) for duplicate text, broken links, or context waste in non-destructive advisory mode. |
| **`teach_brief.py`** | `--init-brief`, `--subject "<X>"`, `--impact-on "<Y>"`, `--slug "<SLUG>"`, `--domain {mechanical,electrical,firmware,cabling,software,hybrid}`, `--verify <BRIEF>`, `--auto-slug`, `--sources <PATH...>`, `--rename-clean <BRIEF>`, `--list`, `--promote <BRIEF>`, `--target {standards,project-doc,lessons-learned}` | Scaffolds (or single-call verifies + `--auto-slug` renames with whole-word smart naming), stamps `VRF-<12hex>` + aligned `┏━━ 🎓 TEACH-ME // BRIEF+ ... ━━┓` chat cards, lists, and optionally promotes multi-domain `Brief+` study briefs in `study_briefs/`. |

```bash
# 1. Check if a new skill idea overlaps with skills you already have:
python3 Homunculus/skills/skill-architect/scripts/audit_skill_hygiene.py \
  --check-new "release-notes-helper: Format release changelogs and verify version tags"

# 2. Run a non-destructive hygiene check across your skills:
python3 Homunculus/skills/skill-architect/scripts/audit_skill_hygiene.py --audit --strict-structure

# 3. Scaffold and verify an on-the-fly Engineering Brief+ in study_briefs/:
python3 Homunculus/skills/teach-me/scripts/teach_brief.py \
  --init-brief --subject "TMC2209 Sense Resistor Dissipation" --impact-on "Stepper Motor Thermal Cutoff" --domain electrical --project "My_Project"
```

---

## 6. Data Privacy & Portability Check Commands

| Tool | Key Arguments & Options | What It Does |
| :--- | :--- | :--- |
| **`audit_data_boundary.py`** | `--repo <PATH>`, `--config <JSON>`, `--compartment {private,public,cleanroom}`, `--staged`, `--worktree` | Scans staged or working-tree files to block accidental secret leaks, personal OS path leaks, or cross-client data bleed before commit. |
| **`audit_portability.py`** | `--repo <PATH>`, `--forbid-token <STR>`, `--json` | Verifies that a repository contains zero hardcoded personal computer paths or custom forbidden tokens. |

```bash
# 1. Check staged Git changes for secret leaks or personal path leaks before committing:
python3 Homunculus/scripts/audit_data_boundary.py --repo . --staged

# 2. Scan an entire public/clean-room project folder for leaked personal paths or custom tokens:
python3 Homunculus/scripts/audit_portability.py --repo . --forbid-token "internal_client_name"
```

---

## 7. Diagram Studio, Doc Polisher & Side-Loaded Add-On Commands

| Tool | Key Arguments & Options | What It Does |
| :--- | :--- | :--- |
| **`render_diagram.py`** | `--spec <JSON>`, `--blueprint <ID>`, `--palette <ID>`, `-o` / `--output <SVG>`, `--strict`, `--png`, `--preview-png <PNG>`, `--github-card`, `--svg-only`, `--list-palettes`, `--list-blueprints` | Renders clean `.svg` (and optional `300 DPI .png` / showcase card) technical diagrams using built-in or custom brand color palettes. |
| **`audit_repo_docs.py`** | `<TARGET_PATH> [...]`, `--files <MD...>`, `--repo-type {hardware,software,auto}`, `--repo-root <DIR>`, `--fail-on-tbd`, `--skip-image-check` | Checks Markdown files for broken links, formatting issues, and incomplete assembly steps. |
| **`format_image.py`** | `<INPUT_PNG...>`, `-o <PNG>`, `--combine`, `--no-divider`, `--inspect`, `--bg-color`, `--radius 28`, `--force` | Inspects, combines, or formats documentation showcase images with rounded corners and soft drop shadows. |
| **`extract_voice_cadence.py`** | `--inbox <DIR>`, `--scope {all,long-form,micro}`, `--output <MD>`, `--learn-diff`, `--draft <MD>`, `--final <MD>` | *(Optional Add-On)* Analyzes writing samples in `--inbox` (default `./corpus_inbox`) or edit-diffs (`--learn-diff`) to build your personal Author Voice profile. |

```bash
# 1. List available diagram color palettes (including your custom palettes):
python3 Homunculus/skills/visual-studio/scripts/render_diagram.py --list-palettes

# 2. Render a diagram to SVG:
python3 Homunculus/skills/visual-studio/scripts/render_diagram.py \
  --spec ./diagram_spec.json --palette default_dark --output ./docs/architecture.svg --strict

# 3. Check documentation files for broken links or incomplete steps:
python3 Homunculus/skills/doc-and-card-studio/scripts/audit_repo_docs.py README.md docs/*.md --skip-image-check
```
