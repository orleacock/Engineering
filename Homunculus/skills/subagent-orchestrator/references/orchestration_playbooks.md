# Subagent Orchestration Playbooks, Prompt Templates & Return Schemas

This reference provides copy-ready **Turn-1 Fast-Path prompt templates**, the **Anchored Evidence Packet** return schema, **Scatter-Gather sharding rules**, and the **3-Tier Cross-Check Architecture** for [`subagent-orchestrator`](../SKILL.md).

---

## 1. Turn-1 Zero-Discovery Prompt Templates (`0` `define_subagent` Setup Turns)

Default to Antigravity's built-in `TypeName: 'research'` (read-only) and `TypeName: 'self'` (CLI / scoped writer) so parallel workers launch **immediately on Turn 1** without burning a prior planner round-trip on `define_subagent`.

### Template 1: Read-Only Scatter-Gather Scout (`TypeName: 'research'`)
Use for multi-file lookups, cross-repository Markdown/code/AST audits, Dual-Mode Memory (`<memory_root>/Projects/<Project>/`) dossier/manifest cross-checks, and specification comparisons. Built-in `research` is policy-locked to read-only inspection; it has no write tools and must never mutate files.

- **`TypeName`**: `'research'`
- **`Model`**: `'flash'` *(or `'flash_lite'` for 1-fact probes; `'pro'` for deep multi-constraint architectural/DFM critique, respecting the Question 2 model floor)*
- **`Workspace`**: `'inherit'`
- **`Role`**: `"Read-Only Scout (<Shard_Name>)"`
- **`Prompt`**:
```text
[ORCHESTRATOR TRACK 1: READ-ONLY FAST-PATH SCOUT]
1. Scope & Zero-Discovery Lock:
   Read ONLY the following canonical paths/line ranges (do NOT crawl directories, do NOT eyeball raw .step/.stl/.canvas files, and do NOT read .py oracle script internals unless explicitly assigned a code-porting/audit/diagnostic task):
   - <ABS_PATH_1>[#Lstart-Lend]
   - <ABS_PATH_2>[#Lstart-Lend]

2. Extraction Task:
   <CONCISE_BOUNDED_QUESTION_OR_AUDIT_TARGET>

3. Accuracy, Anti-Speculation & Fail-Closed Rules (verifiable-accuracy.md):
   - Zero guessing, zero domain-default filling, zero cross-material/cross-entity borrowing.
   - Never infer or invent COTS component nouns (magnets, bearings, fittings, fasteners, sensors) from raw geometric diameters (e.g., `Ø6.00mm`) or unverified traits, and never promote `[SPATIAL / DFM ADVISORY]` inferences to `[VERIFIED FACT]` or `[CAD TELEMETRY]`.
   - Figures inside a dossier's `## ... Open [TBD] / [CONFLICT] Ledger` or `<!-- QUARANTINE-ZONE -->` are quarantined—never report them as `[VERIFIED FACT]`.
   - If any required file read fails or is blocked, HALT IMMEDIATELY and output:
     `[EXTRACTION BLOCKED — ABORTED: <path> — <reason>]`

4. Required Output Schema (Return ONLY this exact structured format):
=== Subagent Evidence Packet (<Role>) [STATUS: PASS | BLOCKED | CONFLICT] ===
[RECEIPT_HEADER] Scope: <shard> | Provenance: <HEAD_SHA / clean | dirty(N)> | Oracles: <n/a>
[ANCHORED_EVIDENCE]
- [VERIFIED FACT] <concise claim with exact value + unit/identifier>
  Source: <abs_path#Lstart-Lend>
  Anchor:
  ```
  <verbatim 1-3 lines from file proving the literal>
  ```
- [TBD: <specific_missing_variable>]
  Source: <abs_path#Lstart-Lend OR abs_path (ABSENT) if whole-file omission>
  Anchor:
  ```
  <context lines proving omission or absence OR [ABSENT_IN_SOURCE]>
  ```
[MEMORY_DELTA] <None | Exact bullet deltas for Primary Thread to apply to <memory_root>/Projects/<Project>/*.md or Tasks/*.md>
[BLOCKERS] <None | [EXTRACTION BLOCKED — ABORTED: ...] | [TBD: CONFLICT — ...]>
```

---

### Template 2: Deterministic Pipe-Free CLI Inspector (`TypeName: 'self'`)
Use when a worker must execute CLI oracles (`inspect_hardware_ecosystem.py`, `sync_memory.py`, `verify_claims.py`, `audit_repo_docs.py`, `audit_skill_hygiene.py`, `audit_portability.py`, `audit_data_boundary.py`, `unittest`/`pytest`, `git -C <repo_path> status --short`, `git -C <repo_path> show HEAD:<repo_relative_path>`). Consult [`oracle_cli_cheatsheet.md`](oracle_cli_cheatsheet.md) for exact flags and exit codes during routine CLI runs instead of reading `.py` oracle files (unless explicitly assigned a code-porting, audit, or diagnostic task).

- **`TypeName`**: `'self'`
- **`Model`**: `'flash'` *(or `'pro'` when combining CLI telemetry with complex cross-interface reasoning)*
- **`Workspace`**: `'inherit'`
- **`Role`**: `"Deterministic CLI Inspector (<Shard_Name>)"`
- **`Prompt`**:
```text
[ORCHESTRATOR TRACK 1: DETERMINISTIC CLI INSPECTOR — READ-ONLY LOCK]
STRICT GUARDRAILS:
- You are FORBIDDEN from calling write_file or edit_file on any repository or `<memory_root>/` file.
- Single-Writer Memory Rule: You are FORBIDDEN from running `--sync-manifest`, `--sync-hardware`, `--sync-software`, or `--sync-trees` (which mutate `<memory_root>/` dossiers). If `inspect_hardware_ecosystem.py --check-cache` exits 2 (`CACHE_STALE`), report `[CAD TELEMETRY: CACHE_STALE]` in your packet; the Primary Thread will execute the sync.
- Zero Invented Traits: Report exact measured dimensions (`Ø6.00mm`) and verified config parameters verbatim. Never guess or attach unrecorded COTS component labels (magnets, bearings, fittings) to raw CAD geometry.
- During routine CLI inspection, use `oracle_cli_cheatsheet.md` for flags rather than reading `.py` source code (never inspect validator regexes to game a check); read `.py` source code only when explicitly porting, auditing, or diagnosing code behavior.
- Execute each CLI command as a single pipe-free invocation (`python3 /abs/path/script.py <args>`); avoid unquoted shell chaining (`&&`, `|`, `;`) that triggers shell safety holds.
- HARD FAIL-CLOSED GATE: If any `run_command` or `read_file` call fails, times out, or hits a permission denial, HALT IMMEDIATELY and return:
  `[EXTRACTION BLOCKED — ABORTED: <tool> on <target> — <error>]`
  Never read script source code or secondary prose to reconstruct blocked telemetry.

1. Assigned Telemetry Commands & Pointers:
   - <EXACT_COMMAND_1>
   - <ABS_POINTER_1>

2. Inspection Objective:
   <SPECIFIC_PROVENANCE_CAD_BOM_OR_TEST_CHECK>

3. Required Output Schema (Return ONLY this exact structured format):
=== Subagent Evidence Packet (<Role>) [STATUS: PASS | BLOCKED | CONFLICT] ===
[RECEIPT_HEADER] Scope: <shard> | Provenance: <HEAD_SHA / clean | dirty(N)> | Oracles: <cmd -> exit_code / VRF-xxxxxxxxxxxx / inventory_sha256>
[ANCHORED_EVIDENCE]
- [<CLI TELEMETRY | CAD TELEMETRY>] <specific result / status / measured spec>
  Source: <abs_path#Lstart-Lend OR command output>
  Anchor:
  ```
  <verbatim 1-3 lines of command stdout or cited file anchor>
  ```
- [TBD: <specific_missing_variable>]
  Source: <abs_path#Lstart-Lend OR abs_path (ABSENT) if whole-file omission>
  Anchor:
  ```
  <context lines proving omission or absence OR [ABSENT_IN_SOURCE]>
  ```
[MEMORY_DELTA] <None | Exact bullet deltas for Primary Thread to apply to <memory_root>/Projects/<Project>/*.md or Tasks/*.md>
[BLOCKERS] <None | [EXTRACTION BLOCKED — ABORTED: ...] | [CAD TELEMETRY: CACHE_STALE]>
```

---

### Template 3: Disjoint Parallel Specialist / Repo Worker (`TypeName: 'self'`)
Use when executing approved edits across **disjoint** repositories or isolated scratch directories in parallel. Disjoint specialists operate under Track 2: mutations to executable scripts, validators, or production files must rehearse within a copy-on-write scratch boundary or OS Dry-Run sandbox (`sandbox_runner.py --mode dry-run`) before promotion to shared working trees.

- **`TypeName`**: `'self'`
- **`Model`**: `'flash'` *(standard doc/BOM/config sync)* or `'pro'` *(complex code, Mode A/B1 authoring, multi-constraint refactors, respecting the Question 2 model floor)*
- **`Workspace`**: `'inherit'`
- **`Role`**: `"Parallel Specialist (<Repo_Or_Module_Name>)"`
- **`Prompt`**:
```text
[ORCHESTRATOR SPECIALIST — SCOPED WRITE BOUNDARY (TRACK 2)]
STRICT WRITE & SAFETY LOCK:
- Allowed write scope: ONLY `<ALLOWED_REPO_OR_SCRATCH_PATHS>`.
- CoW Sandbox Boundary: Perform mutations inside isolated scratch or verify in a CoW dry-run (`sandbox_runner.py --mode dry-run`) prior to promotion. Return surgical patch hunks backed by pipe-free git diff and test checks for Primary Thread review.
- NEVER modify `<memory_root>/` directly (Single-Writer Memory Rule) and NEVER touch files outside your allowed write scope.
- Zero Invented Traits: Every quantitative value, part ID, pinout, or trait written into target files must trace to `<TIER_1_SOURCE_PATHS>`; otherwise insert `[TBD: <specific_missing_variable>]`.
- HARD FAIL-CLOSED GATE: If any required source read, edit, or verification command fails or is denied permission, HALT IMMEDIATELY and return:
  `[EXTRACTION BLOCKED — ABORTED: <target> — <error>]`

1. Concept & Verified Source Pointers:
   - Concept: <LOCKED_CONCEPT>
   - Authoritative Sources: <TIER_1_SOURCE_PATHS>

2. Scoped Implementation Task:
   <SURGICAL_EDIT_SPECIFICATION>

3. Mandatory Pre-Return Oracle Gate:
   Run `<VERIFY_CMD_E.G._verify_claims.py_OR_unittest>` as a pipe-free command and confirm exit code `0` before returning.

4. Required Output Schema (Return ONLY this exact structured format):
=== Subagent Evidence Packet (<Role>) [STATUS: PASS | BLOCKED | CONFLICT] ===
[RECEIPT_HEADER] Scope: <repo/shard> | Provenance: <HEAD_SHA / clean | dirty(N)> | Oracles: <cmd -> exit_code / VRF-xxxxxxxxxxxx>
[ANCHORED_EVIDENCE]
- [VERIFIED FACT] Modified <path#Lstart-Lend>
  Source: <abs_path#Lstart-Lend>
  Anchor:
  ```diff
  <verbatim diff hunk or edited lines proving the change>
  ```
- [TBD: <specific_missing_variable>]
  Source: <abs_path#Lstart-Lend OR abs_path (ABSENT) if whole-file omission>
  Anchor:
  ```
  <context lines proving omission or absence OR [ABSENT_IN_SOURCE]>
  ```
[MEMORY_DELTA] <None | Exact bullet deltas for Primary Thread to apply to <memory_root>/Projects/<Project>/*.md or Tasks/*.md>
[BLOCKERS] <None | [EXTRACTION BLOCKED — ABORTED: ...] | [TBD: CONFLICT — ...]>
```

---

## 2. Canonical Anchored Evidence Packet Schema (Zero Double-Read Contract)

Vague `<= 250`-token prose summaries force the Primary Thread to re-open the same files just to verify exact wording or grab `edit_file` context (**the Double-Read Tax**). Every subagent must return structured **Anchored Evidence Packets** instead:

```text
=== Subagent Evidence Packet (<ROLE>) [STATUS: PASS | BLOCKED | CONFLICT] ===
[RECEIPT_HEADER] Scope: <repo/shard> | Provenance: <HEAD_SHA / clean | dirty(N)> | Oracles: <cmd -> exit_code / VRF-xxxxxxxxxxxx / inventory_sha256 | n/a>
[ANCHORED_EVIDENCE]
- [<EPISTEMIC_TAG>] <concise claim with exact value + unit/identifier>
  Source: <abs_path#Lstart-Lend>
  Anchor:
  ```
  <verbatim 1-3 lines from file proving the literal and giving exact edit_file context>
  ```
[MEMORY_DELTA] <None | Exact bullet deltas for Primary Thread to apply to <memory_root>/Projects/<Project>/*.md or Tasks/*.md>
[BLOCKERS] <None | [EXTRACTION BLOCKED — ABORTED: ...] | [TBD: CONFLICT — ...]>
```

### Epistemic Tag Vocabulary & Anti-Speculation Boundary
- `[VERIFIED FACT]` — Backed by clean `git HEAD` source, config, code, or `<memory_root>/Projects/<Project>/<Project>.md` `Verified Specifications` (`path#Lstart-Lend` + verbatim anchor required).
- `[CAD TELEMETRY]` — Backed by `<memory_root>/Projects/<Project>/<Project>_Hardware.md` (`[CACHE_VALID]`) or `inspect_hardware_ecosystem.py`. Contains pure measured geometry (`X × Y × Z mm`, `cm³`, `Ø (mm)` × count)—**never** attach guessed COTS hardware nouns (`Magnet`, `Bearing`, `Fitting`) to raw cylindrical surfaces unless explicitly named in the CAD product tree or verified BOM.
- `[CLI TELEMETRY]` — Backed by deterministic CLI execution (`exit_code` + receipt/stdout snippet required).
- `[SPATIAL / DFM ADVISORY]` — Engineering first-principles inference separated strictly from measured geometry. Must never be promoted to `[VERIFIED FACT]` or `[CAD TELEMETRY]` or written into `_Hardware.md` / `_Software.md` truth oracles.
- `[TBD: <specific_variable>]` — Required parameter absent from authoritative sources.
- `[CONFLICT: <source_A_val> vs <source_B_val>]` — Contradiction between two primary sources (cite both anchors).

### Single-Source Trust & Pre-Mutation Window Rule (Primary Thread)
- **For Read-Only Synthesis & Audits**: When a subagent packet includes an exact `path#Lstart-Lend`, a verbatim `1–3` line anchor hunk, and provenance/oracle receipts, the Primary Thread **does not re-read the source file** to re-check the quote.
- **Quarantine Hygiene on Synthesis**: When reporting items from a dossier's `## ... Open [TBD] / [CONFLICT] Ledger` or `<!-- QUARANTINE-ZONE -->`, enclose any unverified candidate numbers strictly *inside* `[TBD: ...]` brackets (e.g., `[TBD: tpu_shore_hardness_95A_or_85A_and_slicer_params]`) so `verify_claims.py` never flags quarantined figures leaking into verified prose, and run `verify_claims.py` on any multi-spec output report.
- **Mandatory Window Read Before File Mutations (`edit_file`) or Conditional Context (`Accuracy > Efficiency`)**: Whenever the Primary Thread is going to **modify (`edit_file`)** a file, or whenever a 3-line hunk depends on surrounding table headers, schemas, control flow, or `[CONFLICT]` context, read the surrounding `30–80` line `StartLine`–`EndLine` window first so edits never land blind.

---

## 3. Scatter-Gather Sharding & Fan-In Failure Isolation

1. **Shard Size (`1–2` Repos / Subsystems per Worker, `2–4` Workers Max per Turn)**:
   - Never serialize 4–5 repositories inside one subagent loop (`> 4 min` wall-clock latency). Split across `2–4` concurrent `invoke_subagent` calls emitted in the **same planner turn** so wall-clock time scales with the single slowest shard (`O(1)` turn wait).
2. **Disjoint Write Partitioning**:
   - Parallel `self` specialists must have strictly non-overlapping file/repository write scopes (`Worker A -> Repo A`, `Worker B -> Repo B`). Never assign two concurrent workers to edit the same file.
3. **Partial Fan-In Failure Isolation & Coupled Interface Halt**:
   - If `1` of `N` parallel subagents returns `[EXTRACTION BLOCKED — ABORTED]` or times out:
     - **Coupled Interface Pre-Cascade Halt (Tier-A)**: If the blocked shard provides interface boundaries, pinouts, voltages, fluid/pneumatic tubing, or shared data structures needed by other subsystems, HALT dependent synthesis immediately. Never guess or partially synthesize coupled downstream specifications.
     - **Uncoupled Shards**: If the blocked shard is completely orthogonal to healthy shards, synthesize the verified shards and log only the failed shard as `[BLOCKED]` in the Project State Ledger.
4. **When to Use `define_subagent` (`>= 3` Multi-Wave Exception)**:
   - Use `define_subagent` (`EnableWriteTools: false` or custom system prompt) **only** when a long-running session will invoke the exact same custom worker archetype across **$\ge 3$ separate turns/waves**, amortizing the 1-turn registration cost. For 1–2 wave workflows (95% of tasks), use Turn-1 `research` or `self`.

---

## 4. Cross-Check Architecture: Staggered Parked-Window Attestation & 3-Tier Verification

When evaluating whether to spawn an additional subagent (or recursive self-prompts while parked) purely to cross-check outputs before the Primary Thread builds upon them:

### A. Architectural Evaluation: Deterministic Verification vs. 2nd Neural Auditors
1. **Why Unconstrained 2nd Neural Auditors Are Rejected as Default**:
   - **Latency & Token Overhead**: Spawning a second LLM subagent or recursively prompting while parked adds significant latency ($30\text{–}120\text{s}$ wall-clock) and token burn ($10\text{k}\text{–}30\text{k}$ tokens per turn).
   - **Shared Epistemic Vulnerability**: A second neural model shares the exact same bag-of-tokens blind spots, anchor drift, and non-deterministic omissions as the first. Neural auditors frequently hallucinate plausible confirmations or fail to catch subtle component swaps across pooled contexts.
2. **The Hardened Foundation: Symbolic Lead Co-Engineer Verification**:
   - Fast, deterministic symbolic verifiers execute upon subagent return in $< 100\text{ms}$ with `0` extra model tokens, enforcing mathematical, physical, and disk-level ground truth.

### B. The 3-Tier Cross-Check Architecture
To prevent load-bearing cracks from propagating into downstream synthesis, orchestration enforces three distinct verification tiers:

1. **Tier 1: Parked-Window Deterministic CLI Attestation (Early-Arrival Gate)**:
   - When parallel subagents finish at different times, intermediate subagent returns wake the Primary Thread while other workers remain parked.
   - Instead of idling or spawning an expensive neural auditor, the Primary Thread executes deterministic CLI attestation immediately on the returning shard:
     ```bash
     python3 <HOMUNCULUS_ROOT>/skills/claim-verification/scripts/verify_claims.py \
       --target <shard_evidence_file> \
       --sources <memory_root>/Projects/<Project> <repo_path> \
       --strict-provenance \
       --transcript <logAbsoluteUri>
     ```
   - **Fail-Closed Halt**: If Tier 1 flags `UNATTESTED_TRUNCATED_READ`, `FAILED_ORACLE_COMMAND`, `UNATTESTED_RECEIPT_TOKEN`, `ANCHOR_CLAIM_UNBOUND`, or `MISSING_EVIDENCE_ANCHOR`, the Primary Thread halts before building dependent layers on a compromised foundation.
2. **Tier 2: Primary Thread Cross-Shard Interface Reconciliation (Fan-In Gate)**:
   - Once all concurrent shards return, the Primary Thread reconciles shared interface boundaries across shards (e.g., matching controller pinouts, fluid/pneumatic tubing OD/ID, rail voltages, communication buses, and cross-repo data schemas).
   - If shards disagree on coupled interface boundaries, or if one coupled shard returned `[EXTRACTION BLOCKED — ABORTED]`, the Primary Thread halts synthesis immediately (`Tier-A Pre-Cascade Halt`).
3. **Tier 3: Dedicated Post-Shard Adversarial Cross-Check Subagent**:
   - Dispatched **only** when non-deterministic visual review, complex multi-constraint adversarial auditing, or deep Mode A/B1 DFM synthesis across disparate domains is required.
   - Dispatched as a scoped `TypeName: 'research'` scout or under `engineering-sandbox` (`Blind-Full` or `Visible-Full` Pro frame) with explicit `+faults` adversarial injection.
