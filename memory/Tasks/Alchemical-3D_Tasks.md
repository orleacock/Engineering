---
title: "Alchemical-3D — Domain Task Umbrella"
entity: "Alchemical-3D"
compartment: "public"
note_type: "task_umbrella"
last_synced: "2026-11-13"
---

# 🧪 Alchemical-3D — Active Engineering Task Umbrella (`Tasks/Alchemical-3D_Tasks.md`)

> **Single-Writer Task Governance (`entity: Alchemical-3D`)**:
> - All active checkboxes (`- [ ]` / `- [x]`) for projects owned by **`Alchemical-3D`** live exclusively in this file.
> - Project hub dossiers (`Projects/<Project>/<Project>.md`) link here and never duplicate checkboxes.

---

<!-- AUTO-ROLLUP:START -->
**Progress Summary**: `24 / 36` Tasks Complete (`66.7%`) | Open Tasks: `12` | Open `[TBD]`s: `13`

| Project | Checkpoint (`HEAD` · `Worktree`) | Open Tasks | Open `[TBD]`s | Latest Handoff / Next Kickstart |
| :--- | :--- | :---: | :---: | :--- |
| [`A3DP_Gantry_Assembly`](../Projects/A3DP_Gantry_Assembly/A3DP_Gantry_Assembly.md) (`#L80`) | `2f33452` (`clean`, `2026-11-10`) | `0` | `0` | Next: Review open tasks in `Alchemical-3D_Tasks.md`. |
| [`Alchemical_Web_Docs`](../Projects/Alchemical_Web_Docs/Alchemical_Web_Docs.md) (`#L88`) | `55b4795` (`clean`, `2026-11-10`) | `0` | `1` | Next: Review open tasks in `Alchemical-3D_Tasks.md`. |
| [`Alembic_Toolhead`](../Projects/Alembic_Toolhead/Alembic_Toolhead.md) (`#L71`) | `3ff29ce` (`dirty (8 files)`, `2026-11-10`) | `2` | `2` | Next: Review open tasks in `Alchemical-3D_Tasks.md`. |
| [`Brand`](../Projects/Brand/Brand.md) (`#L97`) | `49354b3` (`clean`, `2026-11-10`) | `0` | `0` | Next: Review open tasks in `Alchemical-3D_Tasks.md`. |
| [`Extras`](../Projects/Extras/Extras.md) (`#L100`) | `7c8db38` (`clean`, `2026-11-06`) | `1` | `1` | Next: Review open tasks in `Alchemical-3D_Tasks.md`. |
| [`Homunculus`](../Projects/Homunculus/Homunculus.md) (`#L45`) | `2dc4fb1` (`clean`, `2026-11-13`) | `5` | `1` | Blocker: Gate 1.5 clean re-attestation queued behind Wave 2 Ring-0 fixes (TM-LIVE-01..03, VC-LIVE-01) · Next: Align on Task #67... |
| [`Maker-Tools`](../Projects/Maker-Tools/Maker-Tools.md) (`#L94`) | `29641c5` (`clean`, `2026-11-06`) | `0` | `0` | Next: Review open tasks in `Alchemical-3D_Tasks.md`. |
| [`Organization_Profile`](../Projects/Organization_Profile/Organization_Profile.md) (`#L91`) | `b74920e` (`clean`, `2026-11-06`) | `0` | `0` | Next: Review open tasks in `Alchemical-3D_Tasks.md`. |
| [`Pestle_Rotational_Bowden`](../Projects/Pestle_Rotational_Bowden/Pestle_Rotational_Bowden.md) (`#L83`) | `d94ad4c` (`clean`, `2026-11-10`) | `3` | `4` | Next: Review open tasks in `Alchemical-3D_Tasks.md`. |
| [`Pneuma_Remote_Air`](../Projects/Pneuma_Remote_Air/Pneuma_Remote_Air.md) (`#L75`) | `0702c9c` (`clean`, `2026-11-10`) | `1` | `4` | Blocker: Open [TBD] physical fastener counts and TPU slicer parameters awaiting bench measurement. · Next: Physically count Rear_Cover... |
<!-- AUTO-ROLLUP:END -->

---

<!-- AUTO-PROJECT-TASKS:START -->
# 🧪 Alchemical-3D Ecosystem Task Umbrella (`Alchemical3D_Tasks`)

Single-writer canonical task and `[TBD]` resolution queue for all 10 repositories in `/home/orin/Projects/Alchemical3D/` ([`README.md`](../README.md)). Each `### <Project>` section below is transcluded directly into its corresponding `Projects/<Project>/<Project>.md` dossier via `> **Active Task Queue**: Tracked in [`Alchemical3D_Tasks`](../Tasks/Alchemical-3D_Tasks.md#<Project>) *(Single-Writer Task Umbrella)*.` so tasks never split or drift across files.

---

## Active Ecosystem Queue

### Homunculus
> **Active Build Priority (`2026-11-13`):** Single-source Clean-Room architecture (`/home/orin/Projects/Alchemical3D/Homunculus`, `107` tracked files, `8` `unittest` suites / `72` tests, `v0.3.2` tagged at `2dc4fb129fb7` & baseline-pinned via `BMK-20261113_201953-1d6f3896`; Wave 2 performance + Gate 1.5 `teach-me` attestation fixes queued), `3-Ring` Privilege Isolation (`Ring-0 Sudo` + `kernel_seal.json` `v1.1` + `tty_turnkey` + remote `scrypt` turnkeys), `MEMORY_SDK_V1` Extension Gateway, `skills/teach-me/` (`D1`–`D8`), 4-Tier Consumer Priority Law (`1. Accuracy & Truth -> 2. Efficiency -> 3. Data Safety -> 4. Speed`), `Apache-2.0`, and Stateful Memory `v1.1` (`LL-001`–`LL-049`; see [`Version_Logs`](../Projects/Homunculus/Version_Logs/Version_Logs_and_Artifact_Registry.md) for historical details & rejected ideas).

- [x] **[COMPLETED 2026-11-01] `[PHASE 1]` Clean-Room Foundation, `homunculus_paths.py`, `audit_portability.py` & `Model C` Base (`2b86bb6`, `SBX-20261101_163034-9a368319`, `6/6` tests):** [v0.1.0–v0.3.0 Worklog](../Projects/Homunculus/Version_Logs/v0.1.0_to_v0.3.0_Foundation_and_Gateway_Worklog.md).
- [x] **[COMPLETED 2026-11-04] `[PHASE 2A]` Data Safety Guidelines, `audit_data_boundary.py`, 3 Core Rules & `skill-architect` (`test_phase2a_data_safety.py` `4/4`):** [v0.1.0–v0.3.0 Worklog](../Projects/Homunculus/Version_Logs/v0.1.0_to_v0.3.0_Foundation_and_Gateway_Worklog.md).
- [x] **[COMPLETED 2026-11-04] `[PHASE 2B]` Primary Client Adapters (`build_adapters.py`), Ignore Files & Git Hooks (`test_phase2b_adapters.py` `4/4`):** [v0.1.0–v0.3.0 Worklog](../Projects/Homunculus/Version_Logs/v0.1.0_to_v0.3.0_Foundation_and_Gateway_Worklog.md).
- [x] **[COMPLETED 2026-11-04] `[PHASE 3A]` Dual-Mode Memory (`sync_memory.py`), Entity Firewall & `Quarantine/` (`test_phase3a_memory.py` `4/4`):** [v0.1.0–v0.3.0 Worklog](../Projects/Homunculus/Version_Logs/v0.1.0_to_v0.3.0_Foundation_and_Gateway_Worklog.md).
- [x] **[COMPLETED 2026-11-04] `[PHASE 3B]` Oracles, Cross-OS Sandbox, Visuals, Docs, Drop-In Add-On & Hygiene Gate (`SBX-20261104_203744-63957361`, `22/22` tests):** [v0.1.0–v0.3.0 Worklog](../Projects/Homunculus/Version_Logs/v0.1.0_to_v0.3.0_Foundation_and_Gateway_Worklog.md).
- [x] **[COMPLETED 2026-11-05] `[PHASE 4A–4B]` Storefront, 8-Page Manual, 4-Tier Priority Law & 3 Production Sandboxes (`a01d5ac`, `SBX-20261105_173440-bda41163`, `25/25` tests):** [v0.1.0–v0.3.0 Worklog](../Projects/Homunculus/Version_Logs/v0.1.0_to_v0.3.0_Foundation_and_Gateway_Worklog.md).
- [x] **[COMPLETED 2026-11-06] `[PHASE 4C–4E]` Parent Inheritance Audit (`PF-01`–`24`, `INH-01`–`41`), `Option A1/B1/C1` & `91/91` Clean-Room Cutover (`SBX-20261106_104836-ab78d9a8`, `25/25` tests):** [v0.1.0–v0.3.0 Worklog](../Projects/Homunculus/Version_Logs/v0.1.0_to_v0.3.0_Foundation_and_Gateway_Worklog.md).
- [x] **[COMPLETED 2026-11-07] `[EXPANSION #1]` Universal Technical Learning Engine (`skills/teach-me/` `Brief+` & Throw-Away Subagent Tutor, `29/29` tests):** [v0.1.0–v0.3.0 Worklog](../Projects/Homunculus/Version_Logs/v0.1.0_to_v0.3.0_Foundation_and_Gateway_Worklog.md).
- [x] **[COMPLETED 2026-11-07] `[CLEAN-ROOM]` `Directory/` Spine, `-42.3%` 2-Tier Rule Diet (`21,880 B`) & `97/97` Promotion (`SBX-20261107_115840-d0c27973`, `30/30` tests):** [v0.1.0–v0.3.0 Worklog](../Projects/Homunculus/Version_Logs/v0.1.0_to_v0.3.0_Foundation_and_Gateway_Worklog.md).
- [x] **[COMPLETED 2026-11-09] `[STATEFUL MEMORY SPRINTS 1–5]` `TIER0`–`TIER5` Gravity Store, Entity Recall, `script_contracts.json` & `101/101` Promotion (`SBX-20261109_120538-a29c8228`, `37/37` tests):** [v0.1.0–v0.3.0 Worklog](../Projects/Homunculus/Version_Logs/v0.1.0_to_v0.3.0_Foundation_and_Gateway_Worklog.md).
- [x] **[COMPLETED 2026-11-10] `[P1–P6 REMEDIATION]` Closed-World Oracle Hardening, `0444` `Archive/`, `N1` Recall & Portable Anchors (`44/44` tests; `v0.1.0`/`v0.2.0` pinned):** [v0.1.0–v0.3.0 Worklog](../Projects/Homunculus/Version_Logs/v0.1.0_to_v0.3.0_Foundation_and_Gateway_Worklog.md).
- [x] **[COMPLETED 2026-11-11] `[VECTOR 3]` Multi-Level `.homunculus.json`, `AUTO-ROLLUP` & Zero-Shell Turn-1 Triage (`SBX-20261111_110421-e810b0f0`, Canary `997593cb`, `55/55` tests; `v0.2.1` pinned):** [v0.1.0–v0.3.0 Worklog](../Projects/Homunculus/Version_Logs/v0.1.0_to_v0.3.0_Foundation_and_Gateway_Worklog.md).
- [x] **[COMPLETED 2026-11-11] `[HOMUNCULUS v0.3.0]` 3-Ring Sudo Seal, `tty_turnkey` & `MEMORY_SDK_V1` (`memory_gateway.py`) (`4bd733d3bd56`, `BMK-20261111_220607-8183c68c`, `62/62` tests):** [v0.1.0–v0.3.0 Worklog](../Projects/Homunculus/Version_Logs/v0.1.0_to_v0.3.0_Foundation_and_Gateway_Worklog.md).
- [x] **[COMPLETED 2026-11-13] `[SECURITY GAP — MEMORY GOVERNANCE TTY_TURNKEY PARITY]` Enforce `/dev/tty` `tty_turnkey` Human Challenge Inside `sync_memory.py` Governance Flags (`2dc4fb129fb7`, `SBX-20261113_193607-e48c8727`, `72/72` tests):** [v0.3.2 Worklog](../Projects/Homunculus/Version_Logs/v0.3.2_Unified_Audit_and_Graduation_Worklog.md).
- [x] **[COMPLETED 2026-11-13] `[COURSE B RULE & ADAPTER BLOAT COMPACTION]` Reclaim `AGENTS.md` Sub-Ceiling Byte Headroom (`21,343 B` in-repo / `21,951 B` out-of-tree, `12` rebuilt adapters, `2dc4fb129fb7`, `BMK-20261113_184347-e54965ec`):** [v0.3.2 Worklog](../Projects/Homunculus/Version_Logs/v0.3.2_Unified_Audit_and_Graduation_Worklog.md).
- [x] **[COMPLETED 2026-11-12] `[TEACH-ME USER-SPACE]` `SDK-MIG-01` & `TM-COND-01`–`TM-COND-11` (`SBX-20261112_074727-9c5fafef`, `VRF-ab92c9ccc52d`, `63/63` tests, `LL-048`):** [v0.3.1 Worklog](../Projects/Homunculus/Version_Logs/v0.3.1_Teach_Me_and_Turnkey_Worklog.md).
- [x] **[COMPLETED 2026-11-12] `[HOMUNCULUS v0.3.1]` `teach-me` `D1`–`D8` (`541e2f8`), Burn-On-Use Remote Turnkeys, `protect_builtin_ring1`, `7`-Axis `[CALC]` & `D6` (`51453f6`, `SBX-20261112_114304-eb3256c8`, `66/66` tests, `LL-049`):** [v0.3.1 Worklog](../Projects/Homunculus/Version_Logs/v0.3.1_Teach_Me_and_Turnkey_Worklog.md).
- [ ] **`[v0.3.2 GRADUATED & BASELINE PINNED (2dc4fb129fb7 / BMK-20261113_201953-1d6f3896) — WAVE 2 & WAVE 3 QUEUED]` `[LOAD-BEARING]` Execute Remaining Phased Roadmap (`S-A` Wave 2: `A2`, `B1`, `setUpClass` Fixture Snapshot Speedup, Gate 1.5 Fixes & `Task #67`; Wave 3: `C1`):** Stage 1–3 graduated & sealed at annotated tag `v0.3.2` (`2dc4fb129fb7` / `efca171d0034`, `72/72 unittest` in `27.696s`, `SBX-20261113_193607-e48c8727` `4/4` controls + `5/5` `+faults` `mut=0`, `BMK-20261113_201953-1d6f3896` `BASELINE_PINNED` with `0` hard blocks, `ME05` `-58.3%`, `AGENTS.md` `-435 B`) ([`v0.3.2 Worklog`](../Projects/Homunculus/Version_Logs/v0.3.2_Unified_Audit_and_Graduation_Worklog.md), [Homunculus_v0_3_2_Unified_Execution_and_Graduation_Plan.md](file:///home/orin/.gemini/antigravity-cli/brain/eaa8998c-3cc6-42a4-bbbf-d64b0fc0ce40/Homunculus_v0_3_2_Unified_Execution_and_Graduation_Plan.md)).
- [ ] **`[GATE 1.5 CANARY EXECUTED ON v0.3.2 — 4 RING-0/HARNESS FIXES & RE-ATTEST QUEUED IN WAVE 2]` `[ISOLATED]` Close Out Live `/teach-me` Subagent Attestation (`TM-LIVE-01..03` + `VC-LIVE-01`):** Canary `30aa49ae` on `Pneuma_Remote_Air` proved live `D1` seed/routing (`pro`/`score:6`), `D2` redaction + `search_web` (`0` leaks), `R0-TM-02` (`[EXTERNAL-REF]`), `R0-TM-06` (`[CALC: (4 mm / 2 mm) ** 4 = 16]`), and `VRF-0f8ded23c6c4` brief verification `PASS`; fix quote-aware shell check (`TM-LIVE-01`), missing-file `KeyError` (`TM-LIVE-02`), verbatim `Anchor:` `[TBD]` FP (`VC-LIVE-01`), and sandbox mount guidance (`TM-LIVE-03`) in Wave 2, then re-attest cleanly into `study_briefs/`.
- [ ] **`[SKILL-ARCHITECT TELEMETRY PULSE — DISCUSSION QUEUED]` `[ISOLATED]` Design & Evaluate On-Call Internal Telemetry & Bloat/Drift Pulse (`skill-architect` + `audit_skill_hygiene.py`):** **Discussion Prompt (User + Agent):** Align on how an on-call internal telemetry suite (`--telemetry-pulse` / bounded `authoritative: false` rolling ledger) should operate on the **Parent Workstation** (`Projects/Engineering`) and whether/how it should **ship inside Clean-Room `Homunculus`** as a companion tool to `skill-architect` (`Mode 2: Permission-Based Cleanup Protocol`) for catching sub-ceiling token creep ("boiling frog" bloat across rules, skills, adapters, and `memory/Directory/`), `AGENTS.md` byte-cap headroom, and core CLI/hook latency regressions without adding Turn-1 context tax or per-commit Git noise.
- [ ] **`[PHASE 5 — POST-CORE]` `[ISOLATED]` Assess & Package `MS365 / Copilot` Edition (`Homunculus Lite`):** Evaluate `< 8,000`-char instruction ceiling, SharePoint/OneDrive grounding, Cloud Code Interpreter vs. Zero-CLI fallback, and `.github/copilot-instructions.md` after Phases 1–4 complete.
- [ ] **`[PHASE 6 — PRIORITY 2 WHEN NEEDED]` `[ISOLATED]` Visual Studio Advancements (`Auto-Layout`, `Electrical/Pinout`, `Sequence/State`):** Build and sandbox-verify inside `Homunculus` Visual Studio when needed, then trigger the workstation backport in `Orin_Workstation_Tasks.md`.

### Alembic_Toolhead
- [ ] **`[LOAD-BEARING]` Provenance Diff & BOM Reconciliation (`8` Dirty Working-Tree Files):** Diff unstaged `BOM.md`, `Assembly_Guide.md`, `Print_Settings.md`, `README.md`, and `ALPHA_&_DIRECTION.md` against clean `git HEAD` (`3ff29ce`) and [`Alembic_Toolhead_Hardware`](../Projects/Alembic_Toolhead/Alembic_Toolhead_Hardware.md)—specifically verifying why unstaged `BOM.md` dropped `M3x24mm` (`~2`), `M3` grub screws (`~2`), and optional `M2` BDsensor fasteners (`M2x3.5x3`, `M2x10`, `M2x8`), changed `M3x8` qty (`~8` $\rightarrow$ `2`), and added `M3x10` + `M3` hex nuts.
- [ ] **`[ISOLATED]` CAD-to-BOM Coverage & AI Transparency Footers:** Clarify/document the 4 `STEP_ONLY` parts (`Intake_6mmOD.step`, `Belt_Clamp_9mm.step`, `PC4-M10 Bowden Pass-Through.step`, `Pnuematic_Fitting_6mmOD.step`) + Dragon-MZE STL variants, append standard AI transparency footers to all 5 docs, run `verify_claims.py`, and commit clean working tree + 3 formatted hero PNGs.

### Pneuma_Remote_Air
- [x] **[COMPLETED 2026-11-10] `[LOAD-BEARING]` Fix 14 Image & Inline-CSS Audit Issues (`0702c9c`):** Stripped all inline HTML `style="border-radius..."` attributes in `Assembly_Guide.md` and formatted all `6` assembly showcase PNGs (`Heatset_Body.png`, `Heatset_Back.png`, `Pump_Mount.png`, `Pneuma_Explode.png`, `Pneuma_Complete_Ext.png`, `Pneuma_Complete_Table.png`) via `format_image.py` (`20px` shadow margin, `#FFFFFF` interior; `audit_repo_docs.py`: `0` load-bearing, `0` isolated).
- [x] **[COMPLETED 2026-11-10] `[LOAD-BEARING]` Reconcile Dual-Pump Architecture, Fail-Safe `shutdown_speed: 0` & Fastener `[TBD]` Tagging (`0702c9c`, `VRF-01c5a7f61d28`, `VRF-886f22bb9de0`, `VRF-ea4740d35e19`, `VRF-c35e0e00f877`):** Standardized `BOM.md` and `Assembly_Guide.md` on Dual-Pump (`2` Vacuum Pumps, `0` Solenoid Valves with Legacy `v1.x` note), updated `Firmware/Pneuma_Control.cfg` to `shutdown_speed: 0` on `pump_cool`/`pump_warm` (documenting that hotend heatsink `[heater_fan]` remains `shutdown_speed: 1`), replaced placeholder `Print_Settings.md` with split Structural (`ABS`/`ASA`/`PETG`) vs. Elastomer (`TPU` `[TBD]`) tables, synced `Pneuma_201` filenames, documented as-needed tube fittings vs. blanking plugs, updated Discord invite (`aE49DW2xXe`), fixed typos, and added AI transparency footers.
- [ ] **`[ISOLATED]` Physical Bench Fastener Count & TPU Slicer Parameter Measurement (`Open [TBD]` Resolution):** Physically count and record exact fastener quantities/lengths for `Rear_Cover`, `Front_Cover`, 2nd `Pump_Mount` heat-sets, and optional `Table_Mount_TPU` screws in `BOM.md` / `Assembly_Guide.md`, and measure/record `TPU` Shore hardness and slicer parameters (`layer_height`, `walls`, `top/bottom`, `infill`) in `Print_Settings.md`.

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
