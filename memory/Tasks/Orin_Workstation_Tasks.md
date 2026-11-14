---
title: "Orin Workstation — Domain Task Umbrella"
entity: "Orin_Workstation"
compartment: "private"
note_type: "task_umbrella"
last_synced: "2026-11-13"
---

# 🖥️ Orin_Workstation — Active Engineering Task Umbrella (`Tasks/Orin_Workstation_Tasks.md`)

> **Single-Writer Task Governance (`entity: Orin_Workstation`)**:
> - All active checkboxes (`- [ ]` / `- [x]`) for projects owned by **`Orin_Workstation`** live exclusively in this file.
> - Transcluded into [`Workstation_Operations`](../Projects/Workstation_Operations/Workstation_Operations.md) and [`README.md`](../README.md).

---

<!-- AUTO-ROLLUP:START -->
**Progress Summary**: `7 / 9` Tasks Complete (`77.8%`) | Open Tasks: `2` | Open `[TBD]`s: `0`

| Project | Checkpoint (`HEAD` · `Worktree`) | Open Tasks | Open `[TBD]`s | Latest Handoff / Next Kickstart |
| :--- | :--- | :---: | :---: | :--- |
| [`Workstation_Operations`](../Projects/Workstation_Operations/Workstation_Operations.md) (`#L28`) | `UNTRACKED` (`untracked`, `2026-11-13`) | `2` | `0` | Next: Support Wave 2 CoW pre-staging and single-command h_sudo.sh turnkey workflow · Evaluate workstation vs cleanroom placement for... |
<!-- AUTO-ROLLUP:END -->

---

<!-- AUTO-PROJECT-TASKS:START -->
## Workstation_Operations

### Local Machine, Accounts & Cleanup (`[GENERAL]`)
- [ ] **[DEFERRED — AWAITING LOCAL CLIENT SETUP] Part 2 — Local / Offline Workstation Redundancy (Syncthing):** Syncthing is active on the main server; install/configure local workstation Syncthing client when ready and pair `/home/orin/Projects/Engineering/` (using pre-staged `.stignore` to exclude `.git/`, while separately deciding whether to replicate gitignored raw archives outside `Engineering/` such as `../Alchemical3D/Homunculus/addons/author-voice-cadence/corpus_inbox/*` `~54 MB`).
- [x] **[COMPLETED 2026-11-01] Dual-Account GitHub SSH (`orleacock` + `Orin-Alchemical-3D`), Gmail MCP v2 (`personal` + `alchemical`), 3-Compartment Boundary Firewall (`audit_data_boundary.py`) & Pre-Upgrade Backup Removal:** Wired `IdentitiesOnly=yes` SSH across `Engineering` and all `9` published `Alchemical-3D` clones (`Homunculus` at `NONE`), provisioned Dual-Account Gmail MCP (`Read + Create Drafts`, `visibility_radar`, `we@alchemical3d.net` `sendAs`), enforced `data-and-credential-safety.md` + `audit_data_boundary.py` (`SBX-20261101_120052-27726090`, `SBX-20261101_120617-30480afc`), and removed the `480K` pre-upgrade safety backup (`2026-11-01_Security_Firewall_Gmail_MCP_and_SVG_Overhaul`).

### AI Skills, Voice Corpus & Memory Architecture (`[WORKFLOWS]`)
- [ ] **Post-Verification Speed & Efficiency Optimization (Verified Anti-Hallucination Fast-Paths):** Investigate and update workstation/workflow token & turn efficiency (`#2`) and execution speed (`#4`) leveraging artifacts, source whitelists, and state that have already passed our anti-hallucination protocols (`verifiable-accuracy.md`, [`Verifiable_Accuracy_and_Anti_Hallucination.md`](../Standards_and_Specs/Verifiable_Accuracy_and_Anti_Hallucination.md), `verify_claims.py` `VRF-*` receipts, and `(HEAD, tree_hash)` / SHA-256 provenance)—eliminating redundant re-scans and repeat verification passes while preserving `#1 Accuracy & Truth` and fail-closed invalidation whenever underlying files drift.
- [x] **[COMPLETED 2026-11-06] `[LOAD-BEARING]` Cut Over Local Workstation (`/home/orin/Projects/Engineering/`) to Run Directly on `Homunculus` (`FEATURE-01`–`FEATURE-15` + Dual-Mode Memory Transplant):** Completed all 4 stages of the Dual-Mode Memory Transplant (`12` projects, `83` files) and all 15 capabilities (`FEATURE-01`–`FEATURE-15`), resolved `INH-01`–`INH-36` (`FIX-01`–`FIX-13`), eliminated speculative COTS/mass heuristics (`INH-10`, `INH-23`), and verified via `OS Dry-Run (+faults)` (`SBX-20261106_082824-c7325eea`) and `Compare-Light` (`SBX-20261106_083332-1b3c07be`).
- [x] **[COMPLETED 2026-11-04] `Homunculus` Phases 2A, 2B, 3A & 3B Clean-Room Construction + Touch-2 Triangulated Sandbox Verification (`SBX-20261104_203744-63957361`):** Built 78 clean-room files across `rules/`, `scripts/`, `adapters/`, `skills/` (`skill-architect`, `project-memory`, `claim-verification`, `subagent-orchestrator`, `engineering-sandbox`, `visual-studio`, `doc-and-card-studio`, `pre-commit-gate`), `addons/author-voice-cadence/`, `templates/`, `docs/Memory_Setup_README.md`, `docs/Commands_and_Prompts_Reference.md`, and `tests/` (`22/22` unit tests OK); triangulated Touch-2 via `OS Dry-Run` (`SBX-20261104_200652-ebb2f0ff`) + `Compare-Light` (`916e2de1` vs `821d2441`), resolved `DEF-01`–`DEF-07` & `PF-01`–`PF-16`, and verified `0` defects / `0` overlaps / `0` violations in `SBX-20261104_203744-63957361`.
- [x] **[COMPLETED 2026-11-04] `Compare-Full (Pro)` System Audit (`SBX-20261104_090329-12245bb9`), 8-Script Fail-Closed Hardening (`SBX-20261104_091445-fb9d6384`), Vault Deduplication & `Homunculus_Construction_and_Migration_Manual`:** Deduplicated all `<Project>_Lessons_Learned.md` ledgers, executed `Compare-Full (Pro)` A/B differential audit (`Blind-Full` + `Visible-Full`), tightened `verifiable-accuracy.md` §5 Tier-B scope, removed `numpy` from `inspect_hardware_ecosystem.py`, hardened all 8 scripts (`5/5` controls, `8/8` faults caught in `SBX-20261104_091445-fb9d6384`), logged `LL-018`, and authored `Homunculus_Construction_and_Migration_Manual`.
- [x] **[COMPLETED 2026-11-03] `skill-architect` Suite (`e5342c2`), `Compare-Light`/`Full` A/B Sandboxes & Project-Scoped `<Project>_Lessons_Learned.md` Ledgers (`f7f78bc`):** Hardened `co-engineering-partner.md` (Anti-Bloat / Deferred Side-Effects, Two-Mode `.py` CLI Rule), built `skill-architect` + `audit_skill_hygiene.py` (`DEV_JOURNAL_CROSS_BLEED = 0`), patched `[OPEN-01]`/`[OPEN-02]` (`SBX-20261103_185458-93f48347`, `SBX-20261103_190605-ceabd477`), added `--mode {compare-light,compare-full}` in `sandbox_runner.py` (`SBX-20261103_193146-2bc6382b`), and deployed project-scoped `*_Lessons_Learned.md` ledgers (`--section lessons`, `excluded_lessons_learned_sources`).
- [x] **[COMPLETED 2026-11-01] SVG-Only Default Visuals, Opt-In `--export-canvas` & `pre-commit-gate` Overhaul:** Standardized `render_diagram.py` on `.svg`-only output (`~0.05s`, `-97.3%` `Visuals/` footprint), replaced per-edit hooks with `pre-commit-gate` (`VRF-20b5a89af95f`) + `.git/hooks/pre-commit`, and verified in `SBX-20261101_144801-5da01f50` (`2026-11-01_Security_Firewall_Gmail_MCP_and_SVG_Overhaul`).
- [x] **[COMPLETED 2026-11-01] Memory v2 Deep Dossiers, `verifiable-accuracy`, `author-voice-cadence`, `subagent-orchestrator` v2 & Swarm Attestation (`8fc06b5`):** Built Memory v2 dossiers (`AUTO-TREE` + `Tasks/*.md` transclusion), `verify_claims.py` (`--transcript` attestation + `#L` bounds), `author-voice-cadence` (`Mode A1`/`A2`/`B1`/`B2`), `subagent-orchestrator` v2 (`[lite]`/`[fast]`/`[deep]` + Anchored Evidence Packets), and `Alchemical_AI_System_Topology`.
<!-- AUTO-PROJECT-TASKS:END -->
