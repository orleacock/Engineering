---
project: "Apprentice"
entity: "Alchemical-3D"
compartment: "public"
note_type: "lessons_learned"
last_synced: "2026-11-20"
---

# Apprentice — Engineering Lessons Learned & Architectural Decisions

> **Root-Cause Memory Ledger (`entity: Alchemical-3D`)**: Every foundational flaw discovered during design, fabrication, debugging, or testing is recorded here using the **Symptom $\rightarrow$ Root Cause $\rightarrow$ Permanent Guardrail** protocol so solved problems never regress.

---

## 0. Subsystem Rebuild & Invariant Matrix (`Sectional Rebuild Reference`)

> **Sectional Rebuild Gate**: Before refactoring, de-bloating, or sectionally rebuilding any module or assembly in `Apprentice`, check this table (`sync_memory.py --project Apprentice --invariants`) so **Must-Keep Invariants (`Chesterton's Fence`)** are preserved and **Retired Bloat / Anti-Patterns (`Never Re-Add`)** are never re-implemented.

<!-- SUBSYSTEM-INVARIANTS:START -->
| Subsystem / Module | Must-Keep Invariants (`Chesterton's Fence`) | Retired Bloat / Anti-Patterns (`Never Re-Add`) | Canonical Owner |
| :--- | :--- | :--- | :--- |
| `Apprentice` Core (`software`) | Enforce `entity: Alchemical-3D` (`compartment: public`) isolation, source-backed quantitative claims (`verify_claims.py`), and `Quarantine/` holding separation. | Guessing undocumented specifications from pretraining defaults or borrowing parameters across distinct entities/materials. | [`Apprentice.md`](Apprentice.md) |
| **Apprentice v3.0 Core & Tool Surface** | 4 orthogonal tools (<=26 params), pure stdlib MCP, Tier S/M/L dynamic %-of-ctx sizing, Map-Locally >=4KB universal routing, <=3300 prod lines | Overlapping repo_audit monolith, 67-param schemas, external venv/pip deps, hardcoded model/GPU constants, restrictive <25KB host-tier byte walls | `ARCHITECTURE.md` ([`Apprentice.md`](Apprentice.md)), `apprentice/core.py` ([`Apprentice_Software.md`](Apprentice_Software.md)), `apprentice/mcp_stdio.py` ([`Apprentice_Software.md`](Apprentice_Software.md)), `plugin/rules/AGENTS.md` ([`Apprentice.md`](Apprentice.md)) (`LL-02`) |
| **Backends, Planner & Deterministic Grounding** | Auto-discovered model/ctx EMA profiler, Tier S deep handoff_to_cloud, <1ms deterministic line/quote verifier with POSIX suffix match, fast STANDARD review default | Silent <=16k cpu-bg clamp, 90-line single-model ETA curve fits, forced HIGH review default, 500-line regex/LLM prose repair loops | `apprentice/backends.py` ([`Apprentice_Software.md`](Apprentice_Software.md)), `apprentice/planner.py` ([`Apprentice_Software.md`](Apprentice_Software.md)), `apprentice/grounding.py` ([`Apprentice_Software.md`](Apprentice_Software.md)), `apprentice/hook.py` ([`Apprentice_Software.md`](Apprentice_Software.md)) (`LL-03`) |
<!-- SUBSYSTEM-INVARIANTS:END -->

---

## 1. Lessons Learned Ledger (`Symptom -> Root Cause -> Guardrail`)

| ID | Date | Symptom / Failure Observed | Root Cause | Permanent Guardrail / Rule or Code Fix | Verification Anchor |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `LL-01` | `2026-11-19` | Initial Dual-Mode Memory onboarding and compartment boundary initialization for `Apprentice` | Unindexed repositories risk blind `ls`/`find` reconnaissance and unverified specification drift | Scaffolded `Apprentice` hub dossier, domain telemetry, `Quarantine/`, and `SUBSYSTEM-INVARIANTS` baseline under `entity: Alchemical-3D` (`public`) | [`Apprentice.md`](Apprentice.md) |
| `LL-02` (`TIER0`) | `2026-11-19` | [TRADE-OFF] Sidecar plugin architectures drift toward overlapping monolithic tools, bloated schemas... | Reactive point fixes accumulate redundant tool parameters, third-party venv... | Enforce Apprentice 4 Core Goals (1. Reduce Quota Usage -> 2. Provide Accuracy Support -> 3. Help With... | `ARCHITECTURE.md` ([`Apprentice.md`](Apprentice.md)), `apprentice/core.py` ([`Apprentice_Software.md`](Apprentice_Software.md)), `apprentice/mcp_stdio.py` ([`Apprentice_Software.md`](Apprentice_Software.md)), `plugin/rules/AGENTS.md` ([`Apprentice.md`](Apprentice.md)) |
| `LL-03` (`TIER2`) | `2026-11-19` | [DEAD-END] Pre-v3.0 monolithic sidecar design combined restrictive Two-Posture host-tier byte walls... | Choking off fast standard lightwork pushed daily usage down to 8 calls over 21 hours... | Default all 4 tools to fast STANDARD with structured JSON + <1ms deterministic line-anchor/quote... | `apprentice/backends.py` ([`Apprentice_Software.md`](Apprentice_Software.md)), `apprentice/planner.py` ([`Apprentice_Software.md`](Apprentice_Software.md)), `apprentice/grounding.py` ([`Apprentice_Software.md`](Apprentice_Software.md)), `apprentice/hook.py` ([`Apprentice_Software.md`](Apprentice_Software.md)) |
| `LL-04` (`TIER2`) | `2026-11-19` | [WIN] Large structured files (85 KB) timed out under 3.6 B/tok estimation and discarded sibling... | Fixed 60s chunk timeouts, under-calibrated 3.6 B/tok estimates, sequential... | Keep calibrated 2.5 B/tok structured estimation, decode-noise-gated prefill servo with staged timeout... | `apprentice/backends.py` ([`Apprentice_Software.md`](Apprentice_Software.md)), `apprentice/planner.py` ([`Apprentice_Software.md`](Apprentice_Software.md)), `apprentice/core.py` ([`Apprentice_Software.md`](Apprentice_Software.md)), `apprentice/hook.py` ([`Apprentice_Software.md`](Apprentice_Software.md)) (`SBX-20261119_202741-2e0c02e1`) |
| `LL-05` (`TIER2`) | `2026-11-20` | Parallel same-turn async_job=True and collect MCP calls stalled 45-50s behind blocking... | Single-threaded serve_stdio() processed JSON-RPC tools/call synchronously on the stdin... | Keep ThreadPoolExecutor(max_workers=4) tools/call dispatch with locked _write_reply() (no unlocked... | `apprentice/mcp_stdio.py` ([`Apprentice_Software.md`](Apprentice_Software.md)), `apprentice/hook.py` ([`Apprentice_Software.md`](Apprentice_Software.md)) (`SBX-20261120_064053-d6f0a889`) |

### `LL-01` [TIER2] [TRAP] — Initial Dual-Mode Memory Onboarding & Compartment Boundary Initialization (`2026-11-19`)
- **Symptom / Trap:** Initial Dual-Mode Memory onboarding and compartment boundary initialization for `Apprentice`.
- **Root Cause:** Unindexed repositories risk blind `ls`/`find` reconnaissance and unverified specification drift.
- **Verified Resolution & Permanent Guardrail:** Scaffolded `Apprentice` hub dossier, domain telemetry, `Quarantine/`, and `SUBSYSTEM-INVARIANTS` baseline under `entity: Alchemical-3D` (`public`; [`Apprentice.md`](Apprentice.md)).

---

### `LL-02` [TIER0] [TRADE-OFF] — Sidecar plugin architectures drift toward overlapping monolithic tools, bloated schemas, and... (`2026-11-19`)
- **Decision Context & Options:** Sidecar plugin architectures drift toward overlapping monolithic tools, bloated schemas, and single-workstation coupling unless core goals and structural ceilings are pinned permanently.
- **Why Chosen Path Won (& Cost Paid):** Reactive point fixes accumulate redundant tool parameters, third-party venv dependencies, and hardcoded hardware assumptions that undermine portability and daily quota savings.
- **Transferable Rule & Invalidation Boundary:** Enforce Apprentice 4 Core Goals (1. Reduce Quota Usage -> 2. Provide Accuracy Support -> 3. Help With Simple Tasks -> 4. Agile-Sprint Parallelism) under Alchemical-3D pillars: exactly 4 orthogonal tools (read, draft, review, runtime; <=26 params), pure Python stdlib zero-venv drop-in, self-calibrating Tier S/M/L dynamic %-of-ctx math, universal Map-Locally (>=4KB) Zoom-Natively routing, and hard anti-bloat ceilings (<=3300 prod lines, AGENTS.md <=1800 B, SKILL.md <=3500 B). (`ARCHITECTURE.md` ([`Apprentice.md`](Apprentice.md)), `apprentice/core.py` ([`Apprentice_Software.md`](Apprentice_Software.md)), `apprentice/mcp_stdio.py` ([`Apprentice_Software.md`](Apprentice_Software.md)), `plugin/rules/AGENTS.md` ([`Apprentice.md`](Apprentice.md))).

---

### `LL-03` [TIER2] [DEAD-END] — Pre-v3.0 monolithic sidecar design combined restrictive Two-Posture host-tier byte walls (<25KB / 4-sliver... (`2026-11-19`)
- **Hypothesis / Path Tried:** Pre-v3.0 monolithic sidecar design combined restrictive Two-Posture host-tier byte walls (<25KB / 4-sliver ban), forced HIGH default reviews (100-235s), silent <=16k CPU clamping, and 500-line regex/LLM prose repair loops across 13,310 lines.
- **Why It Failed (Empirical Receipt):** Choking off fast standard lightwork pushed daily usage down to 8 calls over 21 hours (mostly slow HIGH reviews) while single-model curve fits and prose-formatting guards broke compact-GPU portability and caused quote/attribution failures.
- **Transferable Lesson & Revisit Condition:** Default all 4 tools to fast STANDARD with structured JSON + <1ms deterministic line-anchor/quote verification (including ordered elided-segment matching), never clamp compact GPU models to CPU defaults, and preserve deep-search lineage: trace cross-cutting pre-v3.0 lessons via Principles PRIN-06, PRIN-08, PRIN-09 (--trace-lineage) and shared Host_Runtime LL-HOST-01 (pre-v3.0 historical receipts preserved in archived v2.6.1 snapshot). (`apprentice/backends.py` ([`Apprentice_Software.md`](Apprentice_Software.md)), `apprentice/planner.py` ([`Apprentice_Software.md`](Apprentice_Software.md)), `apprentice/grounding.py` ([`Apprentice_Software.md`](Apprentice_Software.md)), `apprentice/hook.py` ([`Apprentice_Software.md`](Apprentice_Software.md))).

---

### `LL-04` [TIER2] [WIN] — Large structured files (85 KB) timed out under 3.6 B/tok estimation and discarded sibling ex.map()... (`2026-11-19`)
- **Scope:** `script:apprentice`
- **Bottleneck / Challenge:** Large structured files (85 KB) timed out under 3.6 B/tok estimation and discarded sibling ex.map() results; working-tree review diffs failed line grounding (0/3); post-compaction sessions drifted on Project State Ledger Apprentice telemetry and ignored Second-Eyes.
- **Mechanism & Measured Gain:** Fixed 60s chunk timeouts, under-calibrated 3.6 B/tok estimates, sequential working_tree.patch numbering with leading diff prefixes, and one-shot SessionStart hooks without transcript delta resync caused silent abandonment and ledger hallucination.
- **Reusable Pattern & Integration Blueprint:** Keep calibrated 2.5 B/tok structured estimation, decode-noise-gated prefill servo with staged timeout recovery, FIRST_COMPLETED partial-safe bounded tasks, @@ +new @@ real-line review diffs with .md-only bold normalization, Condition priority GPU gate, spoof-proof PreInvocation compaction/drift/Second-Eyes hooks with precommit_seen cooldown bypass, and the user-approved 3,600-line v3.1 ceiling (pause and ask before raising any cap again). (`apprentice/backends.py` ([`Apprentice_Software.md`](Apprentice_Software.md)), `apprentice/planner.py` ([`Apprentice_Software.md`](Apprentice_Software.md)), `apprentice/core.py` ([`Apprentice_Software.md`](Apprentice_Software.md)), `apprentice/hook.py` ([`Apprentice_Software.md`](Apprentice_Software.md)) (`SBX-20261119_202741-2e0c02e1`)).

---

### `LL-05` [TIER2] [TRAP] — Parallel same-turn async_job=True and collect MCP calls stalled 45-50s behind blocking reads on Frontier... (`2026-11-20`)
- **Symptom / Trap:** Parallel same-turn async_job=True and collect MCP calls stalled 45-50s behind blocking reads on Frontier hosts, while oversubscribed sync tasks=[4] batches caused partial turn penalties and scratch-script nudges pointed to apprentice_read
- **Root Cause:** Single-threaded serve_stdio() processed JSON-RPC tools/call synchronously on the stdin loop without concurrency, and neither TOOL_DEFINITIONS nor _build_routing_hint stated max_slots sync limits or separate draft nudge remediation
- **Verified Resolution & Permanent Guardrail:** Keep ThreadPoolExecutor(max_workers=4) tools/call dispatch with locked _write_reply() (no unlocked tracking set), keep inline initialize/ping ordering, surface tasks=[<= max_slots sync] / async_job=True, and route scratch-script nudges to apprentice_draft (verified 406.22s Frontier SUCCESS, -37.1% MCP wait) (`apprentice/mcp_stdio.py` ([`Apprentice_Software.md`](Apprentice_Software.md)), `apprentice/hook.py` ([`Apprentice_Software.md`](Apprentice_Software.md)) (`SBX-20261120_064053-d6f0a889`)).

---

## 2. Architectural Decision Records (`ADR`)

### `ADR-01`: Initial Project Architecture (`2026-11-19`)
- **Context**: Initial repository and memory scaffolding for `Apprentice` (`project_type: software`).
- **Decision**: Governed under Homunculus Governing Priority Law (`1. Accuracy & Truth -> 2. Efficiency -> 3. Data Safety -> 4. Speed`) with strict `entity: Alchemical-3D` isolation.
- **Consequences**: All quantitative claims require primary source anchors or explicit `[TBD: ...]` tags; unverified notes remain isolated in [`Quarantine/`](Quarantine/Quarantine_README.md).
