---
name: subagent-orchestrator
description: Use this skill whenever delegating parallel or context-heavy workloads to subagents, running multi-file or cross-repository scatter-gather audits, switching or steering subagent model tiers ([lite], [fast], [deep], flash_lite/flash/pro or haiku/sonnet/opus), checking git HEAD provenance diffs, inspecting hardware CAD (.step/.stl) or Klipper/firmware (.cfg) telemetry, or synchronizing multi-repo code and documentation with minimal token overhead and verifiable accuracy.
---

# Subagent Swarm Orchestrator & Hardware Telemetry (`subagent-orchestrator`)

This skill governs parallel subagent dispatch, harness-agnostic model tiering, Anchored Evidence Packets, and deterministic 3D CAD / firmware telemetry extraction ([`inspect_hardware_ecosystem.py`](scripts/inspect_hardware_ecosystem.py)) under **`1. Accuracy & Truth -> 2. Efficiency -> 3. Data Safety -> 4. Speed`**.

---

## 1. Pre-Flight Foundation Checks

1. **Turn-1 Memory & Telemetry Check**:
   - Before spawning subagents across a project, read `<memory_root>/Projects/<Project>/<Project>.md` (`AUTO-TREE`), `<Project>_Hardware.md`, and `<Project>_Software.md` on Turn 1.
   - If the project is unindexed or `CACHE_STALE`, run `inspect_hardware_ecosystem.py --repo <repo_path>` and `sync_memory.py` so workers receive verified structural maps instead of running blind `find`/`ls` sweeps.
2. **Partition Disjoint Shards (`2–4` Workers Max)**:
   - Assign each subagent `1–2` repositories or disjoint subsystem directories so workers never collide on files or duplicate reads.
   - Enforce **Single-Writer Memory**: subagents never mutate `<memory_root>/` directly; they return a structured `[MEMORY_DELTA]` block for the Primary Thread to reconcile.
3. **Explicit Harness-Agnostic Model Tier Selection**:
   - Never pass `Model: 'inherit'`. Select the explicit tier required by task complexity (`Routing = max(Complexity_Floor, User_Inline_Tag)`):

| Complexity Tier | Inline Override Tag | Antigravity / Gemini Tier | Claude Code / Cowork Tier | Permitted Workload Scope |
| :--- | :--- | :--- | :--- | :--- |
| **Tier 1 (Scout)** | `[lite]` | `'flash_lite'` | `'haiku'` | Single-fact file/line probes and read-only existence checks (`<= 2` files). |
| **Tier 2 (Standard)** | `[fast]` *(default)* | `'flash'` | `'sonnet'` | Multi-file scatter-gather extraction, CLI telemetry runs, and bounded unit tests. |
| **Tier 3 (Deep)** | `[deep]` | `'pro'` | `'opus'` | Cross-repository architecture synthesis, root-cause debugging, and adversarial `[+faults]` audits. |

---

## 2. Step-Level Verification Gates

### Gate 1 — Deterministic CAD & Firmware Telemetry (`inspect_hardware_ecosystem.py`)
Never read raw `.step` or `.stl` mesh files in LLM context to guess dimensions, bounding boxes, or fastener hole counts. Run the pure-stdlib geometry and config oracle:

```bash
# Inspect a single repository and emit JSON/Markdown telemetry + inventory_sha256 receipt
python3 <HOMUNCULUS_ROOT>/skills/subagent-orchestrator/scripts/inspect_hardware_ecosystem.py \
  --repo /path/to/repo \
  --memory-root ./memory \
  --project <Project>
```

### Gate 2 — Emit 1-Line `[DISPATCH]` Banner & Require Anchored Evidence Packets
Before invoking subagents, output a 1-line dispatch summary:
`[DISPATCH] Launching <N> subagents (<TypeName>, Model=<tier>) across shards: <shard_list>`

Every subagent prompt must require an **Anchored Evidence Packet** response containing:
1. **Claim Tag**: `[VERIFIED FACT]`, `[CAD TELEMETRY]`, `[CLI TELEMETRY]`, `[SPATIAL / DFM ADVISORY]`, `[TBD: <var>]`, or `[CONFLICT]`.
2. **Exact Citation**: `path/to/file#Lstart-Lend` plus a verbatim `1–3` line slice.
3. **Provenance Receipt**: `git HEAD SHA`, `inventory_sha256`, or `VRF-<12hex>`.
4. **`[MEMORY_DELTA]`**: Proposed updates for `<memory_root>/Projects/<Project>/` (applied only by the Primary Thread after cross-shard verification).

### Gate 3 — Pre-Mutation Window Read by Primary Thread
Before the Primary Thread calls `edit_file` on any target cited by a subagent's `1–3` line hunk, read the surrounding `30–80` line window directly to verify control flow, table headers, and indentation.

---

## 3. Stop & Escalation Conditions

- **Subagent Extraction Block (`[EXTRACTION BLOCKED — ABORTED]`)**: If any subagent encounters a missing file, permission denial, or failed CLI oracle, it must halt immediately and return `[EXTRACTION BLOCKED — ABORTED]` rather than guessing from filenames.
- **Cross-Shard Interface Conflict (`Tier-A Pre-Cascade Halt`)**: If Shard Worker A and Shard Worker B return conflicting interface specs (e.g., mismatched fastener bore vs. BOM row, or mismatched API schema), halt immediately before writing dependent code and surface the conflict to the user.
- **Cross-Entity Firewall**: Never dispatch a single subagent across repositories belonging to two different restricted customer/partner entities (`entity:` frontmatter mismatch).
