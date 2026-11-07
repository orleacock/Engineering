---
name: custom-domain-addon-template
description: Starter MIT-licensed Homunculus add-on template. Replace with the exact trigger conditions describing when the AI should activate this domain skill.
---

# Custom Domain Add-On (`custom-domain-addon-template`)

> **Governing Priority Alignment (`1. Accuracy & Truth -> 2. Efficiency -> 3. Data Safety -> 4. Speed`)**:
> This add-on extends the Homunculus Core Engine with domain-specific verification gates while delegating general co-engineering rules, `[TBD: <var>]` abstention, and compartment safety to the Always-On Core Rules.

---

## 1. Pre-Flight Foundation Checks (Verify Before Executing)

Before generating or modifying any domain deliverable:
1. **Turn-1 Project Memory Routing**: Read `<memory_root>/Projects/<Project>/<Project>.md` (`AUTO-TREE`) and the relevant domain telemetry file (`<Project>_Hardware.md` or `<Project>_Software.md`). Do not run blind directory scans (`ls`/`find`).
2. **Authoritative Source Check**: Confirm the primary domain source files (e.g., schematics, netlists, ICDs, or config schemas) exist on disk and check `git -C <repo> status --short` for uncommitted working-tree drift.

---

## 2. Domain-Specific Execution & Negative Constraints

Define only your domain's concrete rules and negative constraints here:
- **Constraint 1 (`[Domain Invariant]`)**: State the exact engineering invariant that must never be violated (e.g., voltage derating, pin-strapping rules, or interface schema locks).
- **Constraint 2 (`[No Silent Defaults]`)**: Whenever a domain parameter is absent from the authoritative source files, emit **`[TBD: <domain_parameter_name>]`** or **`[TBD: CONFLICT — <source_A> vs <source_B>]`**.

---

## 3. Step-Level Verification Gate & Stop Conditions

1. **Deterministic Claim Verification**:
   Run `verify_claims.py` against all authoritative domain sources before presenting the output:
   ```bash
   python3 <HOMUNCULUS_ROOT>/skills/claim-verification/scripts/verify_claims.py \
     --target <deliverable_path> \
     --sources <source_1> <source_2>
   ```
2. **Stop / Escalation Conditions**:
   - Halt immediately with `[EXTRACTION BLOCKED — ABORTED]` if a required source file is unreadable or missing.
   - Defer derived visual or index refreshes until `pre-commit-gate` (`X -> Y -> Z`).
