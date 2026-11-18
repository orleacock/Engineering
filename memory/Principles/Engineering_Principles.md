---
title: "Engineering Memory — Cross-Cutting Engineering Principles"
entity: "shared"
compartment: "cleanroom"
note_type: "engineering_principles"
authoritative: false
last_synced: "2026-11-18"
---

# Engineering Memory — Cross-Cutting Engineering Principles (`PRIN-xxx`)

> **Project-Agnostic Principles Hub (`entity: "shared"` | `compartment: "cleanroom"` | `authoritative: false`)**:
> Stores transferable engineering principles, architectural trade-offs, empirical dead-ends, and reusable wins promoted via **mutual Engineer $\leftrightarrow$ AI sign-off** (`sync_memory.py --promote-principle ... --user-confirmed --reason "..."`).
> - **Zero Entity Bleed (`[PRINCIPLE_ENTITY_BLEED_BLOCKED]`)**: Every entry is deterministically sanitized so zero client names, project stems, `LL-xxx` ticket IDs, or local workstation paths ever enter `Principles/`. Authorized provenance lives solely in `0600` `Directory/lineage_registry.json` (`--trace-lineage <PRIN-ID|LIN-ID>`).
> - **Active Window & Truth Firewall**: Maintains `<= 3` `TIER0` + `<= 7` unscoped `TIER2` full-context principles (graduating stabilized `TIER3`–`TIER5` entries to `0444` `Archive/Engineering_Principles_Archive.md`). Excluded from `verify_claims.py --sources` quantitative whitelists (`[GUARDRAIL CONTEXT ONLY]`).

---

## 1. Cross-Cutting Principles Ledger (`4` Archetypes: `trap` · `dead-end` · `trade-off` · `win`)

| ID | Archetype | Tier | Date | Scope | Transferable Principle Summary | Lineage Receipt |
| :--- | :---: | :---: | :--- | :--- | :--- | :--- |
| **`PRIN-01`** | `[TRAP]` | `TIER2` | `2026-11-18` | — | Halt or emit an explicit missing-variable placeholder rather than coding speculative domain heuristics into core... | `LIN-d5193389260b` |
| **`PRIN-02`** | `[TRADE-OFF]` | `TIER2` | `2026-11-18` | — | Maintain a strict two-tier architecture of compact always-on rules plus on-demand modular skills with safety byte... | `LIN-541fd2a351ef` |
| **`PRIN-03`** | `[TRAP]` | `TIER2` | `2026-11-18` | — | Keep compact operational flags and negative domain constraints inline when companion docs are substantially larger, and... | `LIN-f1d9ee5282f8` |
| **`PRIN-04`** | `[WIN]` | `TIER2` | `2026-11-18` | — | Consolidate pre-commit checks into a single process, pre-filter plain UTF-8 files safely before deep scanning, and cache... | `LIN-ed0e3df3e520` |

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
