---
name: pre-commit-gate
description: Mandatory pre-commit and pre-push release checklist across Homunculus and managed engineering repositories. Activate this skill BEFORE running git commit or git push (or at end-of-task / end-of-session wrap-up) so project memory auto-trees, on-demand SVG diagrams, claim receipts, sandbox gates, portability checks, and compartment data-boundary audits execute once cleanly prior to commit rather than on every mid-session edit.
---

# Pre-Commit & Release Gate (`pre-commit-gate`)

This skill orchestrates the deferred end-of-task verification sequence (**`X -> Y -> Z`**) under **`1. Accuracy & Truth -> 2. Efficiency -> 3. Data Safety -> 4. Speed`**, ensuring derived artifacts and full-suite validators run once at milestone completion rather than churning on intermediate edits.

---

## 1. Pre-Flight Foundation Checks

1. **Confirm Logical Unit of Work Is Complete**:
   - Do not run the full `X -> Y -> Z` release pipeline after intermediate mid-task edits. Wait until the user's requested feature, bugfix, or documentation pass is complete.
2. **Check Track-2 Sandbox Status (`[SANDBOX-PENDING]`)**:
   - Verify whether any modified parser, validator, data-mutating script, rule, or skill is still parked at `[SANDBOX-PENDING]`. Every Track-2 item must pass `sandbox_runner.py` before final release commit.
3. **Explicit User-Readiness Gate for Remote Mutation**:
   - Never run `git push`, publish tags/releases, or mutate shared remote state without explicit user confirmation in the active turn.

---

## 2. Step-Level Verification Gates (`X -> Y -> Z` Sequence)

### Stage X — Synchronize Project Memory, Session Handoff & Structural Auto-Trees (`project-memory`)
When a project memory root (`./memory` or `./vault`) is active, refresh the changed project's structural tree, hardware/software telemetry, `SESSION-HANDOFF` stopping checkpoint, and cross-entity isolation audit:

```bash
python3 <HOMUNCULUS_ROOT>/skills/project-memory/scripts/sync_memory.py \
  --memory-root ./memory \
  --project <Project> \
  --save-handoff \
  --stopped-at "<Milestone completed and verified>" \
  --receipt "<VRF-... / SBX-...>" \
  --next-steps "<Next session kickstart steps>" \
  --sync-visuals \
  --audit
```

### Stage Y — Batch-Render On-Demand Diagrams & Image Cards (`visual-studio` / `doc-and-card-studio`)
If any diagram specification (`*.json`) or documentation image changed during the task, render and verify them once in batch:

```bash
# Render updated SVG diagram specs with strict collision checking
python3 <HOMUNCULUS_ROOT>/skills/visual-studio/scripts/render_diagram.py \
  --spec <spec.json> \
  --output <diagram.svg> \
  --strict

# Audit repository Markdown links, alerts, and image cards
python3 <HOMUNCULUS_ROOT>/skills/doc-and-card-studio/scripts/audit_repo_docs.py <repo_path> --skip-image-check
```

### Stage Z — Deterministic Truth, Portability, Skill Hygiene & Data-Boundary Gate
Run the four mandatory zero-defect release gates before `git commit`:

```bash
# Z1. Verify quantitative claims and anchor citations on authored technical deliverables
python3 <HOMUNCULUS_ROOT>/skills/claim-verification/scripts/verify_claims.py \
  --target <deliverable.md> \
  --sources <src1> <src2> \
  --strict-provenance

# Z2. Verify zero hardcoded paths, zero non-stdlib pip imports, and Cross-OS portability
python3 <HOMUNCULUS_ROOT>/scripts/audit_portability.py --root .

# Z3. Verify compartment & multi-customer data boundaries (staged + working tree)
python3 <HOMUNCULUS_ROOT>/scripts/audit_data_boundary.py --repo . --compartment cleanroom --worktree

# Z4. Verify skill/rule structural hygiene and zero Rule-to-Rule 3-gram bloat
python3 <HOMUNCULUS_ROOT>/skills/skill-architect/scripts/audit_skill_hygiene.py --root . --audit --strict-structure
```

---

## 3. Stop & Escalation Conditions

- **Any Non-Zero Validator Exit (`[GATE BLOCKED]`)**: If Stage X, Y, or Z returns a non-zero exit code, halt the commit immediately, fix the underlying root cause, and re-run the failed gate.
- **Context Window Compaction Recommendation (`/compact`)**: After completing a major milestone `git commit` or `git push`, recommend `/compact` to the user to keep the active context window token-lean.
