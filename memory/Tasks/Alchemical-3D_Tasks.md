---
title: "Alchemical-3D — Domain Task Umbrella"
entity: "Alchemical-3D"
compartment: "public"
note_type: "task_umbrella"
last_synced: "2026-11-06"
---

# 🧪 Alchemical-3D — Active Engineering Task Umbrella (`Tasks/Alchemical-3D_Tasks.md`)

> **Single-Writer Task Governance (`entity: Alchemical-3D`)**:
> - All active checkboxes (`- [ ]` / `- [x]`) for projects owned by **`Alchemical-3D`** live exclusively in this file.
> - Project hub dossiers (`Projects/<Project>/<Project>.md`) link here and never duplicate checkboxes.

---

<!-- AUTO-ROLLUP:START -->
**Progress Summary**: `12 / 25` Tasks Complete (`48.0%`) | Open: `13`
<!-- AUTO-ROLLUP:END -->

---

<!-- AUTO-PROJECT-TASKS:START -->
# 🧪 Alchemical-3D Ecosystem Task Umbrella (`Alchemical3D_Tasks`)

Single-writer canonical task and `[TBD]` resolution queue for all 10 repositories in `/home/orin/Projects/Alchemical3D/` ([`README.md`](../README.md)). Each `### <Project>` section below is transcluded directly into its corresponding `Projects/<Project>/<Project>.md` dossier via `> **Active Task Queue**: Tracked in [`Alchemical3D_Tasks`](../Tasks/Alchemical-3D_Tasks.md#<Project>) *(Single-Writer Task Umbrella)*.` so tasks never split or drift across files.

---

## Active Ecosystem Queue

### Homunculus
> **Active Build Priority (`2026-11-04`):** Canonical architecture, 5-Tier Priority Law (`1. Accuracy & Truth -> 2. Portability -> 3. Efficiency -> 4. Data Safety -> 5. Speed`), licensing (`Model C`), operational build progress (`Phases 1–3B` completed; `Phase 4` ready for tomorrow), and workstation cutover blueprint live in [`Homunculus`](../Projects/Homunculus/Homunculus.md), `Homunculus_Construction_and_Migration_Manual`, [`Homunculus_Talking_Points`](../Projects/Homunculus/Homunculus_Talking_Points.md), and [`Homunculus_Lessons_Learned`](../Projects/Homunculus/Homunculus_Lessons_Learned.md) (`LL-001`–`LL-020`, `PF-01`–`PF-16`).

- [x] **[COMPLETED 2026-11-01] `[PHASE 1]` `[LOAD-BEARING]` Clean-Room Foundation, Path Resolver (`homunculus_paths.py`), `audit_portability.py` & `Model C` Drop-In / Installer Base (`2b86bb6`):** Verified via `audit_data_boundary.py --worktree` (`exit 0`) and `OS Dry-Run (+8 faults)` (`SBX-20261101_163034-9a368319`, `1.07s`, `4/4` controls, `8/8` faults caught; `test_phase1_foundation.py` `6/6` PASS).
- [x] **[COMPLETED 2026-11-04] `[PHASE 2A]` `[LOAD-BEARING]` Developer Data Safety Guidelines, Configurable Boundary Engine, Agnostic Core Rules & `skill-architect`:** Built `docs/Developer_Data_Safety_Guidelines.md` (5-pillar standard), declarative `scripts/audit_data_boundary.py` + `templates/safety/homunculus_safety.json`, 5-Tier Priority `rules/{co-engineering-partner,verifiable-accuracy,data-and-credential-safety}.md`, and `skills/skill-architect/` (`SKILL.md` + `scripts/audit_skill_hygiene.py`); verified via `test_phase2a_data_safety.py` (`4/4` PASS).
- [x] **[COMPLETED 2026-11-04] `[PHASE 2B]` `[LOAD-BEARING]` Primary Client Adapters, Context-Ignore Bindings & Git Hooks:** Built `scripts/build_adapters.py` and 12 reference adapter files across 5 harnesses under `adapters/{antigravity,claude,cursor,codex,cowork}` (`AGENTS.md`, `CLAUDE.md`, `.cursor/rules/*.mdc`, Antigravity `hooks.json` `{}` + `settings.json`, Claude Cowork `.zip` skill/add-on bundler), `.cursorignore`/`.claudeignore`/`.geminiignore` generators, and portable pre-commit/pre-push hooks; verified via `test_phase2b_adapters.py` (`4/4` PASS).
- [x] **[COMPLETED 2026-11-04] `[PHASE 3A]` `[LOAD-BEARING]` Dual-Mode Project Memory (`Headless` + `Obsidian`), Separate Telemetry Functions, Multi-Customer Firewall & Quarantine Zone:** Built `skills/project-memory/` (`SKILL.md` + zero-pip `scripts/sync_memory.py`), `templates/memory/*.md`, and `docs/Memory_Setup_README.md` with dedicated `--sync-hardware` (`<Project>_Hardware.md`) and `--sync-software` (`<Project>_Software.md`) functions, `entity:` cross-contamination blocking, first-class Quarantine Zone (`Quarantine/` + `<!-- QUARANTINE-ZONE -->`), and per-project `Templates/`; resolved `PF-01`, `PF-03`, `PF-05`–`PF-11` (`test_phase3a_memory.py` `4/4` PASS).
- [x] **[COMPLETED 2026-11-04] `[PHASE 3B]` `[LOAD-BEARING]` Core Verification, Orchestration, Cross-OS Sandbox, Visuals, Docs, Side-Loaded Add-On (`addons/author-voice-cadence`) & Touch-2 Hygiene Gate (`SBX-20261104_203744-63957361`):** Ported `claim-verification` (`verify_claims.py`), `subagent-orchestrator` (`inspect_hardware_ecosystem.py`), Cross-OS `engineering-sandbox` (`sandbox_runner.py`), `visual-studio` (`render_diagram.py` + `Diagram_Palettes.json`), `doc-and-card-studio` (`format_image.py` + `audit_repo_docs.py`), `pre-commit-gate`, and Drop-In `addons/author-voice-cadence/`, plus `docs/Commands_and_Prompts_Reference.md`. Triangulated via `OS Dry-Run` (`SBX-20261104_200652-ebb2f0ff`) + `Compare-Light` (`916e2de1` vs `821d2441`), resolved `DEF-01`–`DEF-07` and `PF-02`, `PF-04`, `PF-12`–`PF-16`, and verified in `SBX-20261104_203744-63957361` (`Controls: 5/5 passed`, `+faults: 5/5 caught`, `22/22` unit tests OK, `Load-Bearing Defects: 0`, `Core-Rule Overlaps: 0`, `Orphan Script Candidates: 0`, `Live Host Mutations: 0`).
- [x] **[COMPLETED 2026-11-05] `[PHASE 4A-4B & SANDBOX HARDENING]` Storefront, 8-Page Manual, 4-Tier Consumer Priority Law & 3 Production Sandboxes (`a01d5ac`):** Completed `README.md`, `docs/*.md`, `templates/community_sdk/`, `Visible-Full` Priority Audit, `Compare-Light` 3-OS & Optional Module Audit, and `Visible-Full` 3-Skill `skill-architect` Validation (`SBX-20261105_173440-bda41163`: `7/7` controls, `3/3` `+faults`, `25/25` unit tests OK).
- [x] **[COMPLETED 2026-11-06] `[PHASE 4C-4E]` `[LOAD-BEARING]` Storefront `README.md`, `Discord_Store_Release_Guide.md`, Parent-System Flaw & Inheritance Audit (`PF-01`–`PF-24`, `INH-01`–`INH-41`), Cold-Start Release Gate & Workstation Cutover:** Finalized public-facing `Homunculus/README.md` and `docs/Discord_Store_Release_Guide.md`, resolved all 41 inheritance/parent audit items (`Option A1` brand config decoupling, `Option B1` legacy token removal, `Option C1` local Gmail MCP isolation, `27`-group `QUALIFIER_GROUPS` expansion in `verify_claims.py`, and `INH-40`/`INH-41` dossier/diagram sync), promoted `91 / 91` files at `100%` byte parity (`SBX-20261106_104836-ab78d9a8` & `SBX-20261106_105046-6eb9123f`, `25/25` unit tests OK), logged `LL-021`–`LL-024`, and archived the cutover audit.
- [ ] **`[EXPANSION PRIORITY #1 — POST-v1.0.0]` `[LOAD-BEARING]` Universal Engineering & Technical Learning Engine (`skills/teach-me/` — Multi-Domain `Brief+` & Throw-Away Subagent Tutor):** Build and dogfood `skills/teach-me/SKILL.md` + `scripts/teach_brief.py` locally before clean-room promotion:
  - **Multi-Domain Engineering Scope:** Spans mechanical/CAD (`.step`/`.stl`, fasteners, kinematics, pneumatics, thermal dissipation), electrical/electronics (PCBs, stepper motors, TMC drivers, CAN bus, power rails, voltage drop, structured cabling/RF), firmware (`Klipper` `.cfg`, MCU timers, control loops), and software systems (`/teach-me about "<Subject X>" impact on "<Subject Y>"`).
  - **Non-Consumed Sibling Storage (`<memory_root>/../study_briefs/`):** Writes briefs adjacent to `memory/` with a 3-layer anti-consumption firewall (`sync_memory.py` exclusion, `.cursorignore`/`.claudeignore`/`.geminiignore` rules, and `status: "UNPROMOTED_STUDY_BRIEF"` frontmatter) so teaching artifacts are never ingested as project truth without explicit `--promote` verification (`verify_claims.py --strict-provenance`).
  - **`Brief+` Format:** Concise first-principles mental model + causal coupling/math (`[CALC: ...]`) + trade-off envelope + `1–2` verified overlap examples grounded in the active engineering context (`file#Lstart-Lend`, CAD/PCB/motor/config telemetry, `VRF-<12hex>` receipt).
  - **Throw-Away Subagent Isolation, Smart Naming & Solid-Line Datasheet Card (`SBX-20261106_145314-2fa5c587`, `SBX-20261106_222258-b4b0e9a3`, `SBX-20261106_224204-fbb5d972`, `SBX-20261106_231352-4f790a47`):** Executes 100% of research, file/CAD/spec reads, and `verify_claims.py` checks in a disposable subagent, snaps filenames cleanly on whole-word boundaries (`YYYY-MM-DD_<Subject>_on_<Impact>.md` + `--auto-slug` / `--rename-clean`), routes Turn-1 lookups through entity-isolated `<memory_root>/Directory/` (`Directory_Index.md` + `<Entity>_Directory.md` box trees), and returns a visually distinct Solid-Line Datasheet Card (`┏━━ 🎓 TEACH-ME // BRIEF+ ... ━━┓` + clickable `▸`/`↳` fields + `┗━━ ... ━━┛` rail) to the main window (`Visible-Light` verified at `11` turns / `384s` across `3` hallucination-trap briefs, `6/6` A/B `PASS`, `0` unbacked claims).
- [ ] **`[NEXT SESSION ARCHITECTURE DISCUSSION — 2026-11-07]` `[LOAD-BEARING]` Live Mid-Session Freshness for `memory/Directory/` & `AUTO-TREE` (`Path A` Hooks vs. `Path D` Built-In `Pre-Sandbox Gate` vs. Hybrid):** Resolve how uncommitted mid-session file creations/renames keep `Directory/*.md` and `AUTO-TREE` current during active development and sandboxing without context bloat or wasted turns (weighing **Path A** `0`-token `SessionStart` + `PreToolUse(invoke_subagent)` hooks vs. **Path D** 5-harness/Drop-In portable `Pre-Sandbox Gate` inside `engineering-sandbox` `Gate 0` / `--prepare` + `--kickstart` vs. a Hybrid + `write-if-changed` `tree_hash` guard at `~24.7 ms`, before promoting to Clean-Room `Homunculus`).
- [ ] **`[PHASE 5 — POST-CORE]` `[ISOLATED]` Assess & Package `MS365 / Copilot` Edition (`Homunculus Lite`):** Evaluate `< 8,000`-char instruction ceiling, SharePoint/OneDrive grounding, Cloud Code Interpreter vs. Zero-CLI fallback, and `.github/copilot-instructions.md` after Phases 1–4 complete.
- [ ] **`[PHASE 6 — PRIORITY 2 WHEN NEEDED]` `[ISOLATED]` Visual Studio Advancements (`Auto-Layout`, `Electrical/Pinout`, `Sequence/State`):** Build and sandbox-verify inside `Homunculus` Visual Studio when needed, then trigger the workstation backport in `Orin_Workstation_Tasks.md`.

### Alembic_Toolhead
- [ ] **`[LOAD-BEARING]` Provenance Diff & BOM Reconciliation (`8` Dirty Working-Tree Files):** Diff unstaged `BOM.md`, `Assembly_Guide.md`, `Print_Settings.md`, `README.md`, and `ALPHA_&_DIRECTION.md` against clean `git HEAD` (`3ff29ce`) and [`Alembic_Toolhead_Hardware`](../Projects/Alembic_Toolhead/Alembic_Toolhead_Hardware.md)—specifically verifying why unstaged `BOM.md` dropped `M3x24mm` (`~2`), `M3` grub screws (`~2`), and optional `M2` BDsensor fasteners (`M2x3.5x3`, `M2x10`, `M2x8`), changed `M3x8` qty (`~8` $\rightarrow$ `2`), and added `M3x10` + `M3` hex nuts.
- [ ] **`[ISOLATED]` CAD-to-BOM Coverage & AI Transparency Footers:** Clarify/document the 4 `STEP_ONLY` parts (`Intake_6mmOD.step`, `Belt_Clamp_9mm.step`, `PC4-M10 Bowden Pass-Through.step`, `Pnuematic_Fitting_6mmOD.step`) + Dragon-MZE STL variants, append standard AI transparency footers to all 5 docs, run `verify_claims.py`, and commit clean working tree + 3 formatted hero PNGs.

### Pneuma_Remote_Air
- [ ] **`[LOAD-BEARING]` Fix 14 Image & Inline-CSS Audit Issues:** Strip inline HTML `style="border-radius..."` attributes in `Assembly_Guide.md` and run `format_image.py` on unformatted assembly/showcase PNGs (`Heatset_Body.png`, `Heatset_Back.png`, `Pump_Mount.png`, `Pneuma_Explode.png`, `Pneuma_Complete_Ext.png`, `Pneuma_Complete_Table.png`).
- [ ] **`[LOAD-BEARING]` Reconcile Dual-Pump vs. Legacy Solenoid Architecture & Fastener Counts:** Align `BOM.md` and `Assembly_Guide.md` (which still instruct legacy `1/8-NPT` solenoid valve plumbing and list only `4` total M3 screws) with the dual-pump architecture in `README.md` / `Firmware/Pneuma_Control.cfg` (`PF7` `pump_cool`, `PF9` `pump_warm`) and CAD bore counts in [`Pneuma_Remote_Air_Hardware`](../Projects/Pneuma_Remote_Air/Pneuma_Remote_Air_Hardware.md) (`Main_Body` `Ø4.70mm`×2 + `Ø3.00mm`×16; `Rear_Cover` `Ø4.70mm`×6 + `Ø5.00mm`×5).
- [ ] **`[ISOLATED]` Replace Placeholder `Print_Settings.md` & Sync `Pneuma_201` Filenames:** Replace placeholder `Print_Settings.md` with verified ABS/ASA structural settings + TPU Shore hardness/slicer settings for the 3 unlisted TPU grommet STLs (`Plug_Grommet_TPU.stl`, `TPU_Grommet.stl`, `Table_Mount_TPU.stl`), verify `1.00mm` COTS `Vacuum_Pump` STEP/STL delta, update legacy Discord invite (`r97kK5B7B7` $\rightarrow$ `aE49DW2xXe`), fix typos, and add AI transparency footers.

### A3DP_Gantry_Assembly
- [x] **[COMPLETED 2026-11-02] Repository Unification, 20 GitHub-Native Alert Conversions & Claim Verification (`VRF-6cd82426be23`):** Converted all `20` legacy blockquotes in `Assembly_Guide.md` to `> [!NOTE]`/`> [!WARNING]` alerts, fixed `README.md:52` typo, appended AI transparency footers across all `5` docs, and verified `145/145` claims (`0` issues).

### Pestle_Rotational_Bowden
- [ ] **`[LOAD-BEARING]` Fix 2 Studio-Grey Card Interior PNGs:** Re-run `format_image.py --force` on `images/Pestle_Title_Formatted.png` and `images/PestleExploded3_Formatted.png` to convert studio-grey card interiors to `#FFFFFF`.
- [ ] **`[LOAD-BEARING]` Resolve Internal Fastener & Heat-Set Conflicts Before Modular Split:** Reconcile `README.md` BOM vs. Assembly discrepancies (`7` vs. `6` `M3x5x4` heatsets; `SHCS` vs. `BHCS` on `M3x30`, `M3x35`, `M5x16`; `1` thrust bearing vs. Steps `10 & 12`; unreferenced `M3x16` and `M3x20` screws; 4 unlisted STL mounts/plates in `Releases/1.2/`).
- [ ] **`[ISOLATED]` Modular Documentation Split & Footers:** Split monolithic `README.md` into `README.md`, `BOM.md`, `Print_Settings.md`, and `Assembly_Guide.md` (`Mode B1`), append AI transparency footers, and validate with `verify_claims.py`.

### Alchemical_Web_Docs
- [x] **[COMPLETED 2026-11-02] MkDocs Image/Link Unification, Showcase Card Formatting & Claim Verification (`VRF-e5a13399a32f`):** Fixed `5` root-relative image/`mailto:` issues and `9` legacy domain/affiliate/typo items across `docs/*.md`, formatted `4` showcase PNGs (`#FFFFFF` `20px` card spec), appended AI footers, and verified `0` issues.

### Organization_Profile
- [x] **[COMPLETED 2026-11-02] `we@alchemical3d.net` Send-As Alias (`Path A`) & `profile/README.md` Unification (`VRF-3b88c1f9d028`):** Verified `we@alchemical3d.net` Workspace forwarding + `sendAs` alias, fixed `4` typos, added `Maker-Tools` to the storefront lineup, and appended the AI transparency footer.

### Maker-Tools
- [x] **[COMPLETED 2026-11-02] Typo Fix, AI Transparency Footers & Claim Verification (`VRF-076c174de9c5`):** Fixed `Tools_and_Hardware.md:12` typo, appended AI transparency footers across all `3` docs, and verified `282/282` supported claims (`0` issues).

### Brand
- [x] **[COMPLETED 2026-11-02] Typo Fix, `mailto:` Link & Claim Verification (`VRF-6a3a65d81b80`):** Fixed `README.md:3` `guideline` typo, wrapped `we@alchemical3d.net` in `mailto:`, appended the AI transparency footer, and verified `0` issues.

### Extras
- [ ] **`[ISOLATED]` Author Calibration Cube `README.md` (`Optional`):** Create `README.md` documenting XY/Z shrinkage measurement and compensation math for `Alch_Cube_20mm_V4.stl` and `Alchemical_20mm_Cube.stl` ([`Extras_Hardware`](../Projects/Extras/Extras_Hardware.md)).
<!-- AUTO-PROJECT-TASKS:END -->
