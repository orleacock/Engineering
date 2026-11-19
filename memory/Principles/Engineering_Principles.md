---
title: "Engineering Memory — Cross-Cutting Engineering Principles"
entity: "shared"
compartment: "cleanroom"
note_type: "engineering_principles"
authoritative: false
last_synced: "2026-11-19"
---

# Engineering Memory — Cross-Cutting Engineering Principles (`PRIN-xxx`)

> **Project-Agnostic Principles Hub (`entity: "shared"` | `compartment: "cleanroom"` | `authoritative: false`)**:
> Stores transferable engineering principles, architectural trade-offs, empirical dead-ends, and reusable wins promoted via **mutual Engineer $\leftrightarrow$ AI sign-off** (`sync_memory.py --promote-principle ... --user-confirmed --reason "..."`).
> - **Zero Entity Bleed (`[PRINCIPLE_ENTITY_BLEED_BLOCKED]`)**: Every entry is deterministically sanitized so zero client names, project stems, `LL-xxx` ticket IDs, or local workstation paths ever enter `Principles/`. Authorized provenance lives solely in `0600` `Directory/lineage_registry.json` (`--trace-lineage <PRIN-ID|LIN-ID>`).
> - **Active Window & Truth Firewall**: Maintains `<= 3` `TIER0` + `<= 15` unscoped (`<= 24` total) full-context principles paginated across `Engineering_Principles.md` & `Pages/Engineering_Principles_Vol_NN.md` (graduating stabilized `TIER3`–`TIER5` entries to `0444` `Archive/Engineering_Principles_Archive*.md`). Excluded from `verify_claims.py --sources` quantitative whitelists (`[GUARDRAIL CONTEXT ONLY]`).

---

## 1. Cross-Cutting Principles Ledger (`4` Archetypes: `trap` · `dead-end` · `trade-off` · `win`)

| ID | Archetype | Tier | Date | Scope | Transferable Principle Summary | Lineage Receipt |
| :--- | :---: | :---: | :--- | :--- | :--- | :--- |
| **`PRIN-01`** | `[TRAP]` | `TIER2` | `2026-11-18` | — | Halt or emit an explicit missing-variable placeholder rather than coding speculative domain heuristics into core... | `LIN-d5193389260b` |
| **`PRIN-02`** | `[TRADE-OFF]` | `TIER2` | `2026-11-18` | — | Maintain a strict two-tier architecture of compact always-on rules plus on-demand modular skills with safety byte... | `LIN-541fd2a351ef` |
| **`PRIN-03`** | `[TRAP]` | `TIER2` | `2026-11-18` | — | Keep compact operational flags and negative domain constraints inline when companion docs are substantially larger, and... | `LIN-f1d9ee5282f8` |
| **`PRIN-04`** | `[WIN]` | `TIER2` | `2026-11-18` | — | Consolidate pre-commit checks into a single process, pre-filter plain UTF-8 files safely before deep scanning, and cache... | `LIN-ed0e3df3e520` |
| **`PRIN-05`** | `[TRAP]` | `TIER2` | `2026-11-19` | `global` | Isolate HOME, user profile, cache/config paths, and bytecode generation per worker while surfacing worker stderr on... | `LIN-47b6b33c3131` |
| **`PRIN-06`** | `[TRAP]` | `TIER2` | `2026-11-19` | `global` | Resolve multi-file citation anchors by longest matching relative POSIX path suffix before basename fallback, preserve... | `LIN-967dfe659c07` |
| **`PRIN-07`** | `[WIN]` | `TIER2` | `2026-11-19` | `global` | Separate shared host-runtime constraints from cleanroom principles and entity scopes, keep optional shelves unlinked in... | `LIN-819030510d1d` |
| **`PRIN-08`** | `[TRADE-OFF]` | `TIER2` | `2026-11-19` | `domain:local_inference` | Auto-discover live model context and speed via rolling averages, scale output and chunk budgets dynamically as... | `LIN-91f14727907d` |
| **`PRIN-09`** | `[TRAP]` | `TIER2` | `2026-11-19` | `domain:telemetry_testing` | Inject isolated temporary cache directories via environment overrides in every benchmark, unit test, and stress harness... | `LIN-6855dc81f288` |

---

## 2. Active Cross-Cutting Principles (`TIER0` & `TIER2`)

### `PRIN-01` [TIER2] [TRAP] — Measure Structure, Never Guess Design Intent in Validators (`2026-11-18`)
- **Lineage-Receipt:** `LIN-d5193389260b`
- **Symptom / Trap:** Adding regex heuristics into deterministic validators whenever downstream repositories omit specifications or expose ambiguous edge cases.
- **Root Cause:** Automated parsers and geometry inspectors can verify structural syntax and physical envelopes, whereas human design intent requires explicit specification or engineer confirmation.
- **Verified Resolution, Guardrail & Applicability Boundary:** Halt or emit an explicit missing-variable placeholder rather than coding speculative domain heuristics into core validators; present invariants, options, and blast radius before modifying validator rules.

### `PRIN-02` [TIER2] [TRADE-OFF] — Two-Tier Instruction Budgeting and Canonical Symlink Path Resolution (`2026-11-18`)
- **Lineage-Receipt:** `LIN-541fd2a351ef`
- **Decision Context & Options:** Splitting always-on agent rules across an extra middle instruction file, exceeding per-file byte caps, or resolving symlinked CLI scripts with non-canonical path helpers.
- **Why Chosen Path Won (& Cost Paid):** Monolithic instruction bundles silently truncate past platform byte ceilings, out-of-tree relative paths inflate byte counts, and lexical path helpers preserve symlink prefixes instead of target script directories.
- **Transferable Rule & Invalidation Boundary:** Maintain a strict two-tier architecture of compact always-on rules plus on-demand modular skills with safety byte headroom, and resolve sibling imports via canonical realpath resolution across symlinks and copied bundles.

### `PRIN-03` [TIER2] [TRAP] — Point-of-Action Constraint Salience and Paired Blind-vs-Visible Validation (`2026-11-18`)
- **Lineage-Receipt:** `LIN-f1d9ee5282f8`
- **Symptom / Trap:** Replacing compact inline operational constraints and CLI flags with cross-file section pointers, or evaluating prompt changes solely with coached test prompts.
- **Root Cause:** Cross-file pointers to larger companion docs trigger extra read turns and net token inversion, while coached prompts mask qualitative omissions that uncoached runs commit.
- **Verified Resolution, Guardrail & Applicability Boundary:** Keep compact operational flags and negative domain constraints inline when companion docs are substantially larger, and validate workflow changes with paired uncoached blind and coached visible runs.

### `PRIN-04` [TIER2] [WIN] — Single-Process Hook Consolidation and Pure-JSON Content-Addressed Caching (`2026-11-18`)
- **Lineage-Receipt:** `LIN-ed0e3df3e520`
- **Bottleneck / Challenge:** Spawning multiple interpreter processes per pre-commit check and rebuilding unchanged source indexes from scratch on every validation pass.
- **Mechanism & Measured Gain:** Repeated interpreter startup and redundant full-file parsing dominate gate latency, whereas unsafe binary serialization caches introduce code-execution risks.
- **Reusable Pattern & Integration Blueprint:** Consolidate pre-commit checks into a single process, pre-filter plain UTF-8 files safely before deep scanning, and cache parsed indexes as pure JSON keyed by file metadata and SHA-256 digests while keeping secret scans live.

### `PRIN-05` [TIER2] [TRAP] — Per-Worker State Isolation in Parallel Test Suites and Supersession Checkpoints (`2026-11-19`)
- **Lineage-Receipt:** `LIN-47b6b33c3131`
- **Symptom / Trap:** Parallel test workers flake under shared host caches or bytecode writes when only TMPDIR is isolated, and golden-query regression suites break when superseded lesson IDs move to retired archives.
- **Root Cause:** Concurrent worker processes collide inside shared user home, config, and cache directories, while downstream recall fixtures hardcode retired source IDs unless updated alongside lineage maturation.
- **Verified Resolution, Guardrail & Applicability Boundary:** Isolate HOME, user profile, cache/config paths, and bytecode generation per worker while surfacing worker stderr on failure, and update downstream golden-query fixtures to accept successor IDs whenever lessons are superseded.

### `PRIN-06` [TIER2] [TRAP] — POSIX Relative Path-Suffix Citation Matching and Working-Tree Patch Repair Fallback (`2026-11-19`)
- **Lineage-Receipt:** `LIN-967dfe659c07`
- **Symptom / Trap:** Checking line bounds by filename alone flags valid multi-directory citations when identically named files coexist, and single-file self-repair aborts when critiques reference working-tree diff hunks.
- **Root Cause:** Basename-only lookup maps overwrite distinct sibling paths under the last indexed file, while claim repair pipelines omit transient working-tree diff patches and drop single-line fixes below arbitrary line minimums.
- **Verified Resolution, Guardrail & Applicability Boundary:** Resolve multi-file citation anchors by longest matching relative POSIX path suffix before basename fallback, preserve repo-relative target labels, and mount working-tree diff patches during self-repair down to single-line edits.

### `PRIN-07` [TIER2] [WIN] — Two-Shelf Memory Separation, Paginated Active Windows, and Tapered Scope Retrieval (`2026-11-19`)
- **Lineage-Receipt:** `LIN-819030510d1d`
- **Bottleneck / Challenge:** Unbounded single-file lesson logs and flat active ceilings crowd per-project windows, mix host-local tool rules with cleanroom principles, and break clean-init audits when root indexes link uninitialized optional shelves.
- **Mechanism & Measured Gain:** Mixing portable design principles with host-local tool rules creates cross-project bleed, fixed global ceilings force premature retirement, and static root links to optional folders fail validation before initialization.
- **Reusable Pattern & Integration Blueprint:** Separate shared host-runtime constraints from cleanroom principles and entity scopes, keep optional shelves unlinked in starter root hubs, paginate active books under 24 KB with tapered scope caps, scan overflow and shared shelves during ID allocation, and age-taper aged entries without muting safety traps.

### `PRIN-08` [TIER2] [TRADE-OFF] — Capability-Driven Dynamic Sizing and Task-Nature Routing Over Hardcoded Model Specs and Restrictive Byte Walls (`2026-11-19`)
- **Scope:** `domain:local_inference`
- **Lineage-Receipt:** `LIN-91f14727907d`
- **Decision Context & Options:** Hardcoding single-model context ceilings, speed curves, or restrictive host-tier byte walls collapses routine sidecar offload volume while forcing compact GPUs into silent CPU fallbacks or context overflows.
- **Why Chosen Path Won (& Cost Paid):** Static tuning constants and narrow size thresholds overfit one hardware profile, starving fast standard tasks while pushing all remaining traffic into slow, high-failure deep reasoning regimes.
- **Transferable Rule & Invalidation Boundary:** Auto-discover live model context and speed via rolling averages, scale output and chunk budgets dynamically as percentages of live context across capability tiers, default routine tasks to fast standard mode, and route by task nature rather than arbitrary high byte walls.

### `PRIN-09` [TIER2] [TRAP] — Strict Environment Isolation Between Benchmark Suites and Live Production Telemetry Caches (`2026-11-19`)
- **Scope:** `domain:telemetry_testing`
- **Lineage-Receipt:** `LIN-6855dc81f288`
- **Symptom / Trap:** Running automated benchmarks or stress suites against default user cache paths inflates production usability scorecards and mixes synthetic test traffic with real operational telemetry.
- **Root Cause:** Benchmark harnesses sharing default cache directories mutate live scorecard counters, masking real operational degradation behind passing synthetic replay scores.
- **Verified Resolution, Guardrail & Applicability Boundary:** Inject isolated temporary cache directories via environment overrides in every benchmark, unit test, and stress harness, and verify zero write drift against live production telemetry files.
