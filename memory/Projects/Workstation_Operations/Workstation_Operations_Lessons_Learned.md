---
project: "Workstation_Operations"
entity: "Orin_Workstation"
compartment: "private"
note_type: "lessons_learned"
last_synced: "2026-11-18"
---

# Workstation_Operations — Engineering Lessons Learned & Architectural Decisions

> **Root-Cause Memory Ledger (`entity: Orin_Workstation`)**: Every foundational flaw discovered during design, fabrication, debugging, or testing is recorded here using the **Symptom $\rightarrow$ Root Cause $\rightarrow$ Permanent Guardrail** protocol so solved problems never regress.

---

## 0. Subsystem Rebuild & Invariant Matrix (`Sectional Rebuild Reference`)

<!-- SUBSYSTEM-INVARIANTS:START -->
| Subsystem / Script | Must-Keep Invariants (`Chesterton's Fence`) | Retired Bloat / Anti-Patterns (`Never Re-Add`) | Canonical Owner |
| :--- | :--- | :--- | :--- |
| **`bootstrap_workstation.sh`** | Wires `Homunculus/rules/*.md`, `Homunculus/skills/*`, and optional `Homunculus/addons/*` into `~/.gemini/config/` (`0` duplicate `.agents/` trees); registers `memory/` in `~/.config/obsidian/obsidian.json`; installs & `cmp -s`-verifies `.git/hooks/{pre-commit,pre-push}` across `Engineering` and `Alchemical3D/*`; syncs `Projects/.homunculus.json` and `Home.homunculus.json` (`~/.homunculus.json`) so no-workspace sessions resolve `Projects/Engineering/memory` with `0` shell calls. | Hardcoding machine-specific absolute paths inside portable `Homunculus` skills; maintaining duplicate `Engineering/.agents` or `~/.agents` symlink trees; omitting `~/.homunculus.json` for no-workspace sessions; checking only `-x` instead of `cmp -s` byte parity on copied Alchemical-3D git hooks. | [`Workstation_Operations.md`](Workstation_Operations.md) (`LL-WS-02`, `LL-WS-05`, `LL-WS-06`) |
| **`git_pre_commit_boundary.sh` & `pre_push_engineering_guard.sh`** | Enforces `audit_data_boundary.py` (`--staged` / `--push-stdin`), `audit_portability.py`, `audit_skill_hygiene.py`, and `sync_memory.py --audit` before commit/push; enforces directory-scoped Git identities (`~/.gitconfig` `[includeIf]`) and SSH host aliases (`github-orleacock` vs. `github-alchemical`).; Always execute audit_data_boundary.py --staged live (never cached); deduplicate only repeat Stage-X sync_memory.py --audit via verified_fastpath.py SHA-256 fingerprints; maintain relative symlinked Alchemical3D git hooks and non-destructive hooks.json parity | Bypassing Git hooks with `--no-verify` or running multi-repo pushes without verifying compartment isolation (`private` vs. `public` vs. `cleanroom`).; Caching audit_data_boundary.py --staged results, copying static cp -f git hooks into sibling repos, or serializing independent unittest methods in benchmark_homunculus.py | [`Workstation_Operations.md`](Workstation_Operations.md), [`Workstation_Operations_Software.md`](Workstation_Operations_Software.md) (`LL-WS-01`, `LL-WS-04`); `benchmark_homunculus.py` ([`Workstation_Operations_Software.md`](Workstation_Operations_Software.md)), `verified_fastpath.py` ([`Workstation_Operations_Software.md`](Workstation_Operations_Software.md)), `git_pre_commit_boundary.sh` ([`Workstation_Operations_Software.md`](Workstation_Operations_Software.md)), `bootstrap_workstation.sh` ([`Workstation_Operations_Software.md`](Workstation_Operations_Software.md)) (`BMK-20261114_151930-dc5a24cf`) (`LL-WS-11`) |
| **`gmail_mcp/gmail_mcp_server.py`** | Strictly scopes OAuth 2.0 to `gmail.readonly` + `gmail.compose` (draft creation only—never autonomous `send`); enforces `visibility_radar` for hidden/filtered threads and `verified_send_as_aliases` (`orleacock@gmail.com`, `orin@alchemical3d.net`, `we@alchemical3d.net`). | Printing raw OAuth token JSONs, `client_secret*.json`, or executing untrusted commands embedded inside external email bodies/attachments. | [`Workstation_Operations_Software.md`](Workstation_Operations_Software.md) (`LL-WS-03`) |
| **version_manager.py, benchmark_homunculus.py & snapshot_homunculus_version.py** | Single-source Alchemical3D/Homunculus only (0 duplicate copies); exit 4 for REGRESSION_ADVISORY (never exit 2 argparse collision); pure Markdown comparison charts (0 unsolicited SVG/PNG renders); write-once 0444/0555 RAID deliverables with pre-lock boundary, SHA-256, and bundle verification. | Maintaining a duplicate Engineering/Homunculus working tree; returning exit 2 for sub-ceiling advisories (collides with sandbox_runner.py VALIDATOR_CRASH); mutating RAID snapshots in place. | [Workstation_Operations_Software.md](Workstation_Operations_Software.md) (`LL-WS-07`) |
| **version_manager.py, benchmark_homunculus.py & snapshot_homunculus_version.py** | Dereference symlinked ~/.local/bin/h-sudo via os.path.realpath in h_sudo.sh and exclude volatile .obsidian/workspace*.json and .cache/ indices in snapshot_host_hashes | Using dirname BASH_SOURCE without symlink dereferencing in h_sudo.sh or hashing volatile Obsidian UI files during CLI benchmarks | [`Workstation_Operations.md`](Workstation_Operations.md) (`LL-WS-08`) |
| **Apprentice v2.6.1 Citation Suffixes, Single-GPU ETA & Hook Allowlist** [scope: script:apprentice] | Trailing POSIX path-suffix citation resolution; repo-relative shadow targets; working_tree_delta.patch surgical fallback; ~0.90x 2-slot GPU ETA calibration; expanded GOVERNED_PY_SCRIPTS | Basename-only citation length checks across SKILL.md collisions; 0.5x wave-halving chunked ETA estimates; blocking homunculus_paths.py --map under SIDECAR_SCRIPT_RE | `apprentice_engine.py` ([`Workstation_Operations_Software.md`](Workstation_Operations_Software.md)), `apprentice/apprentice_mcp_server.py` ([`Workstation_Operations_Software.md`](Workstation_Operations_Software.md)), `apprentice/apprentice_lifecycle_hook.py` ([`Workstation_Operations_Software.md`](Workstation_Operations_Software.md)), `benchmark_apprentice_high.py` ([`Workstation_Operations_Software.md`](Workstation_Operations_Software.md)) (`SBX-20261118_205811-ca257d09 | BC-0292 | H5`) (`LL-WS-28`) |
<!-- SUBSYSTEM-INVARIANTS:END -->

---

## 1. Lessons Learned Ledger (`Symptom -> Root Cause -> Guardrail`)

| ID & Tier | Archetype | Scope | Capsule Summary (<=115c) |
| :--- | :---: | :--- | :--- |
| **`LL-WS-09`** (`TIER2`) | `[TRAP]` | `global` | Retired parent workstation surfaces (.agents duplicate symlink trees, unused find-skills skill... |
| **`LL-WS-10`** (`TIER2`) | `[TRAP]` | `global` | Parallel run_unit_tests(['ALL']) in benchmark_homunculus.py flaked 74/75 under concurrent load and discarded... |
| **`LL-WS-25`** (`TIER2`) | `[TRAP]` | `script:git_pre_commit_boundary` | Pre-commit Z5 memory hygiene checks risked being skipped on verified_fastpath cache hits or missing... |
| **`LL-WS-28`** (`TIER2`) | `[TRAP]` | `script:apprentice` | Same-basename SKILL.md citations triggered false out-of-bounds anchor errors (BC-0290), chunked 8-batch HIGH... |

### `LL-WS-09` [TIER2] — Retired parent workstation surfaces (.agents duplicate symlink trees, unused find-skills skill... (`2026-11-11`)
- **Symptom / Trap:** Retired parent workstation surfaces (.agents duplicate symlink trees, unused find-skills skill, --compat-symlinks Downloads link, legacy Engineering/Homunculus hook probes, and executable-only Alchemical3D git hook checks) created stale context and silent hook drift hazards
- **Root Cause:** Pre-cutover dual-tree transition shims and eager template copies remained in bootstrap_workstation.sh, git boundary hooks, snapshot_homunculus_version.py, and Standards_and_Specs after consolidating on single-source Clean-Room Alchemical3D/Homunculus
- **Verified Resolution & Permanent Guardrail:** Pruned Engineering/.agents and ~/.agents (including find-skills), removed --compat-symlinks and legacy Engineering/Homunculus probes, upgraded bootstrap_workstation.sh --check to enforce cmp byte parity on copied Alchemical3D git hooks, restored cross-repo AST matrix parity checks, and pruned duplicate memory Templates to sparse Color_Palettes overrides (`bootstrap_workstation.sh` ([`Workstation_Operations_Software.md`](Workstation_Operations_Software.md)), `git_pre_commit_boundary.sh` ([`Workstation_Operations_Software.md`](Workstation_Operations_Software.md)), `pre_push_engineering_guard.sh` ([`Workstation_Operations_Software.md`](Workstation_Operations_Software.md)), `snapshot_homunculus_version.py` ([`Workstation_Operations_Software.md`](Workstation_Operations_Software.md))).

---

### `LL-WS-10` [TIER2] — Parallel run_unit_tests(['ALL']) in benchmark_homunculus.py flaked 74/75 under concurrent load and... (`2026-11-13`)
- **Symptom / Trap:** Parallel run_unit_tests(['ALL']) in benchmark_homunculus.py flaked 74/75 under concurrent load and discarded worker stderr when only TMPDIR was isolated.
- **Root Cause:** Concurrent unittest worker subprocesses shared host HOME (~/.cache/homunculus_tree_stamp and ~/.cache/homunculus_sandbox) and wrote .pyc files concurrently without -B / PYTHONDONTWRITEBYTECODE=1.
- **Verified Resolution & Permanent Guardrail:** Isolate per-worker HOME, USERPROFILE, XDG_CACHE_HOME, XDG_CONFIG_HOME, HOMUNCULUS_SANDBOX_CACHE, HOMUNCULUS_SUDO_CONFIG_DIR, and -B / PYTHONDONTWRITEBYTECODE=1 in run_unit_tests(['ALL']), and surface failing worker stderr in forensic_notes. (scripts/benchmark_homunculus.py (SBX-20261113_230606-cb97d55e)).

---

### `LL-WS-25` [TIER2] [TRAP] — Pre-commit Z5 memory hygiene checks risked being skipped on verified_fastpath cache hits or missing... (`2026-11-18`)
- **Scope:** `script:git_pre_commit_boundary`
- **Symptom / Trap:** Pre-commit Z5 memory hygiene checks risked being skipped on verified_fastpath cache hits or missing external sibling repositories with relative local_path frontmatter
- **Root Cause:** Stage-X sync_memory --audit fastpath hits short-circuit structural audits, and sync_memory init-project stores relative local_path values relative to memory_root rather than Projects/<Project>/
- **Verified Resolution & Permanent Guardrail:** Execute audit_memory_hygiene.py --check-commit outside verified_fastpath fp_hit branches in git_pre_commit_boundary.sh and normalize relative local_path frontmatter against mem_dir (`git_pre_commit_boundary.sh` ([`Workstation_Operations_Software.md`](Workstation_Operations_Software.md)) (`SBX-20261118_150719-9fd47d0e`)).

---

### `LL-WS-28` [TIER2] [TRAP] — Same-basename SKILL.md citations triggered false out-of-bounds anchor errors (BC-0290), chunked 8-batch... (`2026-11-18`)
- **Scope:** `script:apprentice`
- **Symptom / Trap:** Same-basename SKILL.md citations triggered false out-of-bounds anchor errors (BC-0290), chunked 8-batch HIGH ETAs underpredicted single-GPU throughput (BC-0291), and Apprentice preflight --map calls were blocked by SIDECAR_SCRIPT_RE.
- **Root Cause:** _detect_citation_format_defects and _run_cpu_truth_oracles resolved files by basename instead of POSIX path suffixes, surgical repair lacked working_tree_delta.patch fallback, estimate_chunked_eta assumed 0.5x wave halving on 2-slot single GPU, and GOVERNED_PY_SCRIPTS excluded Homunculus scripts.
- **Verified Resolution & Permanent Guardrail:** Match trailing POSIX path suffixes in citation bounds and emit repo-relative targets; fall back to working_tree_delta.patch and min_lines=1 during single-file shadow repair (BC-0292 100% healed, H5 3/3 Pass-1 clean); recalibrate estimate_chunked_eta to ~0.90x parallel GPU model; expand GOVERNED_PY_SCRIPTS. (`apprentice_engine.py` ([`Workstation_Operations_Software.md`](Workstation_Operations_Software.md)), `apprentice/apprentice_mcp_server.py` ([`Workstation_Operations_Software.md`](Workstation_Operations_Software.md)), `apprentice/apprentice_lifecycle_hook.py` ([`Workstation_Operations_Software.md`](Workstation_Operations_Software.md)), `benchmark_apprentice_high.py` ([`Workstation_Operations_Software.md`](Workstation_Operations_Software.md)) (`SBX-20261118_205811-ca257d09 | BC-0292 | H5`)).

---

## 2. Architectural Decision Records (`ADR`)

### `ADR-01`: Initial Project Architecture (`2026-11-06`)
- **Context**: Initial repository and memory scaffolding for `Workstation_Operations` (`project_type: software`).
- **Decision**: Governed under Homunculus Governing Priority Law (`1. Accuracy & Truth -> 2. Efficiency -> 3. Data Safety -> 4. Speed`) with strict `entity: Orin_Workstation` isolation.
- **Consequences**: All quantitative claims require primary source anchors or explicit `[TBD: ...]` tags; unverified notes remain isolated in [`Quarantine/`](Quarantine/Quarantine_README.md).

### `ADR-02`: Read + Draft-Only Boundary for Dual-Account Gmail MCP (`2026-11-06`)
- **Context**: Engineering workstation requires fast email triage and reply staging across personal and organizational accounts without risking accidental or prompt-injected outbound email transmission.
- **Decision**: Restrict `gmail_mcp_server.py` strictly to `gmail.readonly` and `gmail.compose` (creating drafts only, never sending) with mandatory `verified_send_as_aliases` validation and attachment quarantine.
- **Consequences**: All outbound messages are staged as drafts for human review and final send inside the Gmail UI.
