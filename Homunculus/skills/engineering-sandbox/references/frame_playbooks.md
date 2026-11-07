# Engineering Sandbox Frame Playbooks, Prompt Envelopes & Diagnostic Return Schemas

This reference contains the Frame Selection Matrix, copy-ready subagent prompt templates (`Blind`, `Visible`, `Compare`), firewall checklists, the Canonical Diagnostic Return Schema, and the `+faults` Poison-Pill Design Guide for [`engineering-sandbox`](../SKILL.md).

---

## 1. Frame Selection Matrix

| Frame Mode | CLI `--mode` | Model Tier | Context Visibility | Primary Use Case |
| :--- | :--- | :--- | :--- | :--- |
| **OS Dry-Run** | `dry-run` | Deterministic CLI (`0` LLM tokens) | Isolated CoW Workspace | Fast unit test, CLI parser, and `+faults` validator verification. |
| **Blind-Light** | `blind-light` | `'flash'` / `'sonnet'` | Clean-room prompt + target files only (no chat history) | Testing whether a skill or rule prevents hallucinations or invented traits on a fresh worker. |
| **Blind-Full** | `blind-full` | `'pro'` / `'opus'` | Clean-room prompt + target files only | Deep multi-file synthesis or complex skill audit without conversational bias. |
| **Visible-Light** | `visible-light` | `'flash'` / `'sonnet'` | Full task context + isolated CoW workspace | End-to-end workflow execution check before applying changes to live repo. |
| **Visible-Full** | `visible-full` | `'pro'` / `'opus'` | Full task context + isolated CoW workspace | High-risk cross-repository refactor or architecture migration dry-run. |
| **Compare-Light / Full** | `compare-light` / `compare-full` | Paired `'flash'` or `'pro'` | Arm A (`Blind`) vs. Arm B (`Visible`) | A/B differential benchmarking of skill/rule revisions on token count, `[TBD]` honesty, and accuracy. |

---

## 2. Blind Sandbox Firewall & Prompt Template (`Blind-Light` / `Blind-Full`)

### Zero-Coaching Pre-Launch Checklist
Before launching a `Blind-Light (Flash)` or `Blind-Full (Pro)` subagent, confirm **all four** items hold:
- [ ] **No Bug Spoilers**: Does the prompt avoid mentioning the specific defect, hallucination, or edge case you just fixed?
- [ ] **No Rule Paraphrasing**: Does the prompt avoid repeating rules inline (e.g., do *not* write *"make sure you use `[TBD]` instead of guessing"*—the on-disk rules/skills must enforce that automatically)?
- [ ] **Realistic User Persona**: Is the task phrased the way the user would naturally ask for it in a fresh session?
- [ ] **Isolated Write Boundary & Write-Capable Subagent Type**: Are all generated files directed strictly to `<SCRATCH_ROOT>/sandbox_runs/<run_name>/out/` (never inside `brain/<parent-id>/`, which is blocked across subagent conversations) or wrapped inside `sandbox_runner.py` so live project repositories and `<memory_root>/` remain untouched? Always invoke `Blind`, `Visible`, and `Compare` subagents with `TypeName: 'self'` (or `define_subagent(..., EnableWriteTools=True)`), never read-only `TypeName: 'research'`.

### Template 1: `Blind-Light` / `Blind-Full` Subagent Prompt
```text
[SANDBOX EXECUTION CONTEXT: ACTIVE — NON-RECURSIVE]
Write all output deliverables strictly inside: <SCRATCH_OUT_DIR>
Do NOT modify any files outside <SCRATCH_OUT_DIR>.

Task:
<REALISTIC_END_USER_REQUEST_WITHOUT_COACHING_HINTS>

Return a concise completion note (<= 250 tokens) listing:
1. Exact files written in <SCRATCH_OUT_DIR>
2. Any verification commands you chose to run and their receipts/exit codes
3. Any open ambiguities or [TBD] items surfaced
```

---

## 3. Visible Sandbox Co-Engineering Brief (`Visible-Light` / `Visible-Full`)

`Visible` sandboxes deliberately receive high-density project context and `subagent-orchestrator` tooling so they can rehearse complex mutations, refactors, and multi-agent workflows safely inside Copy-on-Write containment.

### Template 2: `Visible-Light` / `Visible-Full` Subagent Prompt
```text
[SANDBOX EXECUTION CONTEXT: ACTIVE — VISIBLE REHEARSAL (NON-RECURSIVE)]
You are running a Visible Sandbox rehearsal under `engineering-sandbox` and `subagent-orchestrator`.
STRICT CONTAINMENT & EFFICIENCY RULES:
- Do NOT mutate live repositories or `<memory_root>/` directly.
- Zero Invented Traits: Never invent or guess COTS hardware nouns (magnets, bearings, fittings, fasteners) or software behaviors not explicitly present in verified sources.
- For routine CLI runs, invoke `sandbox_runner.py`, `verify_claims.py`, `audit_repo_docs.py`, and `sync_memory.py` via `oracle_cli_cheatsheet.md` (or `--help`) without reading their `.py` source files or running duplicate `/tmp` pre-tests outside `sandbox_runner.py` (when porting, auditing, extending, or diagnosing an unexpected failure/traceback, reading `.py` source is mandatory).
- Execute all file-mutating scripts or edits inside `sandbox_runner.py` (multiple `--cmd` flags share the primary CoW overlay sequentially; each `--fault-case` gets a fresh untouched CoW clone):
  python3 <HOMUNCULUS_ROOT>/skills/engineering-sandbox/scripts/sandbox_runner.py \
    --mode <visible-light|visible-full> \
    --target-dir <TARGET_REPO_OR_MEMORY_PATH> \
    --report-dir <REPORT_DIR> \
    --cmd "<REHEARSAL_AND_VERIFICATION_CMD>"

1. Concept (Locked):
   <ONE_SENTENCE_CONCEPT>

2. Protected Protocol & Solved Invariants (Must Not Regress):
   <BULLETED_SOLVED_AND_PROTOCOL_INVARIANTS>

3. Canonical Memory & Source Pointers (Zero-Discovery Entry):
   - Project Dossier: <memory_root>/Projects/<Project>/<Project>.md
   - Task Umbrella: <memory_root>/Tasks/<Entity>_Tasks.md
   - Hardware Manifest: <memory_root>/Projects/<Project>/<Project>_Hardware.md
   - Software Manifest: <memory_root>/Projects/<Project>/<Project>_Software.md
   - Target Repo / Code: <LOCAL_PATH>

4. Rehearsal Objective (+ Optional `+faults` Probes):
   <SPECIFIC_REHEARSAL_INSTRUCTIONS_AND_FAULT_CASES>

5. Required Output (<= 400 tokens total):
   Return ONLY the 5-Block Diagnostic Report (`[ISOLATION_RECEIPT]`, `[ORACLE_VERDICT]`, `[MUTATION_SUMMARY]`, `[FAILURE_TAXONOMY]`, `[REMEDIATION_DELTA]`) plus `[FORENSIC_BUNDLE]` path.
```

---

## 4. Paired A/B Differential Sandbox (`Compare-Light` / `Compare-Full`)

When validating a skill edit, `skill-architect` trim candidate, or new authoring/verification workflow, running only `Visible` can mask action-site salience loss (because the prompt coaches the subagent), while running only `Blind` lacks a full-context baseline for `[TBD]` / `[CONFLICT]` counts and CLI path friction. `Compare-Light` (`Model: 'flash'`) and `Compare-Full` (`Model: 'pro'`) run both arms concurrently in Turn 1 and evaluate their outputs and `transcript.jsonl` trajectories deterministically in Turn 2.

### Template 3: Simultaneous Dual-Arm Dispatch + `sandbox_runner.py --mode compare-*`
1. **Turn 1 — Launch Both Subagents in Parallel (`2x invoke_subagent` in the same response)**:
   - **Deliverable Filename Parity Lock**: Both prompts **must** specify the exact same relative output filenames inside `<RUN_DIR>/blind_out/<File.md>` and `<RUN_DIR>/visible_out/<File.md>`.
   - **Arm 1 (`Blind-Light` or `Blind-Full`)**: Use **Template 1** above (`Zero-Coaching Firewall` — realistic user prompt, zero inline conflict/architecture coaching, writing strictly to `<RUN_DIR>/blind_out/`).
   - **Arm 2 (`Visible-Light` or `Visible-Full`)**: Use **Template 2** above (`Co-Engineering Brief` — includes `Concept`, Dual-Mode Memory dossier/manifest pointers, and explicit structural audit instructions, writing strictly to `<RUN_DIR>/visible_out/`).
2. **Turn 2 — Run Deterministic Differential Evaluator (`< 2s`)**:
   ```bash
   python3 <HOMUNCULUS_ROOT>/skills/engineering-sandbox/scripts/sandbox_runner.py \
     --mode <compare-light|compare-full> \
     --blind-dir <RUN_DIR>/blind_out \
     --visible-dir <RUN_DIR>/visible_out \
     --blind-transcript <BLIND_CONVERSATION_ID> \
     --visible-transcript <VISIBLE_CONVERSATION_ID> \
     --repo-root <TARGET_REPO_ROOT> \
     --compare-source <AUTHORITATIVE_SOURCE_1> \
     --compare-source <AUTHORITATIVE_SOURCE_2> \
     --report-dir <RUN_DIR>/ab_report
   ```
   *(Optional `+faults` testing on the A/B evaluator itself: pass `--target-dir <RUN_DIR> --fault-case "<setup_cmd_mutating_blind_out> :: @ab-compare"`.)*

---

## 5. Canonical Diagnostic Return Schema

Every `OS Dry-Run`, `Blind` post-audit, `Visible` rehearsal, and `Compare` A/B run reports results in this standardized compact schema (`<= 350–400` tokens in Primary Thread; verbose diffs/logs stay in `scratch/sandbox_runs/`):

```text
=== Engineering Sandbox Diagnostic Report (<RUN_ID>) ===
[ISOLATION_RECEIPT] Mode: <dry-run|blind-light|blind-full|visible-light|visible-full|compare-light|compare-full> | Model: <none|flash|pro> | Live Host Mutations: 0 | Elapsed: <X.XXs>
[ORACLE_VERDICT] Status: <PASS|FAIL> | Controls: <A/B> passed | +faults: <C/D caught | n/a> | VRF: <VRF-xxxxxxxxxxxx | none>
[AB_COMPARISON_MATRIX] Shared: <N> files | <File>(Blind:<PASS|FAIL>/TBD:<B> vs Vis:<PASS|FAIL>/TBD:<V>) | Turns(B/V): <TB>/<TV> | SkillsRead(B/V): <SB>/<SV> | lsProbes(B/V): <LB>/<LV>
[MUTATION_SUMMARY] Overlay/Scratch Changes: +<created> ~<modified> -<deleted> (<sample_paths>) | Blocked Rogue Writes (EROFS): <N>
[FAILURE_TAXONOMY] <NONE | PROMPT_AMBIGUITY | LOGIC_DEFECT | PATH_ESCAPE_BLOCKED | FAIL_OPEN_DEFECT | WRONG_FAULT_SIGNATURE | VALIDATOR_CRASH | REGRESSION_THREAT | ACCURACY_DRIFT | COACHING_MASKED_DEFECT | QUALITATIVE_DODGING_TBD_DEFICIT | MISSING_DELIVERABLE_PARITY>
[REMEDIATION_DELTA] <Exact file:line root-cause fix required, or "Ready for production apply / [SOLVED] promotion">
[FORENSIC_BUNDLE] <abs_path_to_report_dir>
```

---

## 6. Adversarial `+faults` Specification Schema & Poison-Pill Design Guide

### A. Declarative `sandbox_spec.json` Schema (`--spec <path> --faults`)
Every validator or audit script can be tested via inline `--fault-case "<setup_cmd> :: <validator_cmd>"` or a declarative `sandbox_spec.json`:

```json
{
  "name": "phase_validator_gate",
  "controls": [
    {
      "id": "ctrl_clean_pass",
      "cmd": "python3 <HOMUNCULUS_ROOT>/scripts/audit_portability.py --repo .",
      "expect_exit": 0,
      "expect_output_contains": "[PASS]"
    }
  ],
  "faults": [
    {
      "id": "fault_injected_violation",
      "setup_cmd": "printf 'import yaml\\n' > .sbx_fault_tmp.py",
      "validator_cmd": "python3 <HOMUNCULUS_ROOT>/scripts/audit_portability.py --repo .; rc=$?; rm -f .sbx_fault_tmp.py; exit $rc",
      "expect_exit": 1,
      "expect_output_contains": "NON_STDLIB_PIP_IMPORT"
    }
  ]
}
```

> **Note on Isolated `/tmp` inside Tier-1 Linux `bwrap`**: Because `bwrap` mounts a fresh ephemeral `--tmpfs /tmp` per command invocation, any file created by `setup_cmd` for `validator_cmd` to inspect must be written to a relative path inside the CoW workspace (e.g., `.sbx_fault_tmp.py`), not `/tmp/`.

### B. `+faults` Poison-Pill Design Guide (4 Mandatory Archetypes)
When attaching `+faults` (`--fault-case "<setup_cmd> :: <validator_cmd> [@@ <expected_signature>]"` or `--spec`) to any validator, parser, or ETL script:
1. **Isolate Setup from Detection & Assert Exact Fault Signatures**: `sandbox_runner.py` runs `<setup_cmd>` first and requires `setup_rc == 0` AND `>= 1` file mutation (unless `--allow-noop-setup`) so a typo or no-op in the setup command can never masquerade as a caught fault (`FAULT_SETUP_NOOP`). Likewise, `sandbox_runner.py` automatically flags validator CLI/syntax crashes (`VALIDATOR_CRASH`) and checks `expect_output_contains` / `@@ <expected_signature>` (`WRONG_FAULT_SIGNATURE`) so a validator failing for the wrong reason never passes.
2. **Test One Structural Boundary Per Fault Case**:
   - **Archetype 1 — Schema / Split-Brain Violation**: Inject a forbidden construct (e.g., `[[WikiLink]]` syntax or a cross-entity link inside `Projects/<Project>/<Project>.md`) and assert `sync_memory.py --audit` exits `!= 0` (`@@ WIKILINK_SYNTAX_FORBIDDEN` or `@@ SPLIT_BRAIN_VIOLATION`).
   - **Archetype 2 — Unbacked Quantitative Literal**: Inject an unverified measurement or cross-material borrowed value into a draft and assert `verify_claims.py` exits `!= 0` (`@@ QUANTITY_UNIT` or `@@ CROSS_ENTITY_BORROWING`).
   - **Archetype 3 — Quarantine Escape**: Place a fake number inside a `<!-- QUARANTINE-ZONE -->` or `Open [TBD] / [CONFLICT] Ledger` source section, reference that fake number in a target doc, and assert `verify_claims.py` rejects it (`exit != 0`).
   - **Archetype 4 — Invented / Speculative Trait Escape (COTS Trait Guardrail)**: Inject an unrecorded component trait (e.g., claiming a `"6mm magnet"` or `"4x magnets"` against a `_Hardware.md` manifest that records only pure `Ø6.00mm` geometry) and assert `verify_claims.py` deterministically blocks it (`@@ QUALIFIED_QUANTITY(MAGNET)` or `@@ COUNTED_ENTITY(MAGNET)`).
