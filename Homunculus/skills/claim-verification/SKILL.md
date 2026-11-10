---
name: claim-verification
description: Domain-agnostic engineering accuracy and anti-hallucination verification skill. Use whenever authoring, auditing, or reviewing technical documentation, BOMs, schedules, hardware/electronics specs, structured cabling deliverables, configs, or public engineering posts containing quantitative values, part identifiers, pins/ports, or component relationships. Pairs pre-draft relational mapping with deterministic post-draft verification via verify_claims.py.
---

# Claim Verification & Deterministic Truth Gate (`claim-verification`)

This skill provides the operational CLI workflow, diagnostic code reference, and pre-draft relational mapping table for [`verify_claims.py`](scripts/verify_claims.py) under the **Governing Priority Hierarchy (`1. Accuracy & Truth -> 2. Efficiency -> 3. Data Safety -> 4. Speed`)**.

---

## 1. Pre-Flight Foundation Checks

1. **Identify Authoritative Source Files (`--sources`)**:
   - Before drafting or auditing a technical deliverable, enumerate all primary workspace sources (`BOM`, `CAD` STEP/STL files, `.cfg`/`.ini`/`.json`/`.yaml` configs, `.xml`/`.csv` workbooks, `<Project>_Hardware.md`, `<Project>_Software.md`, and clean `git HEAD` source files).
   - Never pass the target deliverable itself inside `--sources` (`SELF_REFERENTIAL_SOURCE`), and never pass files inside `<memory_root>/Projects/<Project>/Quarantine/` or `<!-- QUARANTINE-ZONE:START -->` blocks as authoritative ground truth.
2. **Pre-Draft Relational & Parametric Mapping (`--dump-whitelist`)**:
   - Run `python3 <HOMUNCULUS_ROOT>/skills/claim-verification/scripts/verify_claims.py --sources <source_1> <source_2> --dump-whitelist` or extract a quick pre-draft mapping table pairing each component/entity to its verified source file + line range (`path#Lstart-Lend`), exact count/dimension/rating, and any missing specification (`[TBD: <specific_missing_variable>]`) or cross-source disagreement (`[TBD: CONFLICT — <val_A> vs <val_B>]`).

---

## 2. Step-Level Verification Gates (`verify_claims.py` CLI)

### Gate 1 — Mandatory Post-Draft Claim Audit (`--dump-whitelist` Is Never a Substitute & Max `2-Pass` Ceiling)
Running `--dump-whitelist` before drafting is a pre-draft aid only—it **never** substitutes for post-draft verification. After calling `write_file` or `edit_file` on **any** technical deliverable (including audit reports, specifications, BOMs, or manuals), you **must** execute [`verify_claims.py`](scripts/verify_claims.py) with `--target <deliverable.md>` against the primary source files (including `<Project>_Hardware.md` so CAD dimensions and `Ø` diameters are in scope) and resolve all `Unbacked Claims` (`Unbacked Claims: 0`) before finishing:
- **Zero Unbacked "Recommended" Pretraining Ranges (Inside or Below `[TBD]`)**: When a source file (e.g., `Print_Settings.md`) is a placeholder stub or omits parameters (such as TPU Shore hardness `95A`/`85A`, nozzle/bed temperatures, or speeds), **never** add "Recommended" / "typically" pretraining values either inside or below `[TBD: ...]` (`[TBD_SPECULATIVE_GUESS]`), and never copy `ABS/ASA` settings onto `TPU`—emit explicit `[TBD: <specific_missing_variable>]` variable names only.
- **Hard `2-Pass` Verification Ceiling, `[Line Text]` Parallel Edits & Zero Validator Introspection**: Run `verify_claims.py --target` at most **twice** (`Pass 1` $\rightarrow$ use the printed `[Line Text]` and `[Fix Hint]` directly without calling `read_file` on the target draft, and batch all `edit_file` replacements in parallel in **one single turn** $\rightarrow$ `Pass 2`). **Never** inspect `verify_claims.py` via `read_file`, shell `grep`/`sed`, or `python3 -c "import verify_claims; inspect.getsource(...)"` to reverse-engineer validator regexes (`[ANTI-SNOOP GATE]`).

```bash
python3 <HOMUNCULUS_ROOT>/skills/claim-verification/scripts/verify_claims.py \
  --target <deliverable.md> \
  --sources <repo_dir_or_files> [<cad_telemetry_md_or_json>] \
  --project-dir <memory_root>/Projects/<Project>
```

### Gate 2 — Strict Provenance, Anchor & Clean-Tree Gate (Release / Pre-Commit)
When preparing a milestone commit or release (`pre-commit-gate`), enable strict provenance, anchor verification, git-clean source checks, and zero-`[TBD]` enforcement (`--strict-provenance --fail-on-tbd`; aliases `--require-anchors` and `--require-git-clean-sources` are also supported):

```bash
python3 <HOMUNCULUS_ROOT>/skills/claim-verification/scripts/verify_claims.py \
  --target <deliverable.md> \
  --sources <source_1> <source_2> \
  --project-dir <memory_root>/Projects/<Project> \
  --strict-provenance \
  --fail-on-tbd
```

### Gate 3 — Diagnostic Code Resolution
Inspect every reported diagnostic code and resolve root causes in the target document (never by weakening validator checks):

| Diagnostic Code | Meaning & Required Engineering Resolution |
| :--- | :--- |
| `UNBACKED_NUMERIC_CLAIM` | Numeric value + unit in `--target` does not exist in `--sources`. Replace with the exact source literal or `[TBD: <specific_missing_variable>]`. |
| `UNBACKED_PART_OR_PIN` | Part number, fastener code (`M3x16 SHCS`), or MCU pin (`PA1`, `gpio26`) is absent from `--sources`. Bind to verified source or tag `[TBD: ...]`. |
| `CROSS_ENTITY_BORROWING` | Target deliverable for Entity/Project A cites a path or parameter belonging to Entity/Project B (`entity:` mismatch). Remove cross-entity reference immediately. |
| `QUARANTINE_SOURCE_REJECTED` | A file inside `Quarantine/` was passed in `--sources`. Remove it from `--sources` and tag unverified claims as `[TBD: ...]`. |
| `SELF_REFERENTIAL_SOURCE` | Target file overlaps `--sources`. Remove target from `--sources`. |
| `DIRTY_SOURCE_WORKTREE` | Source file has uncommitted working-tree edits under `--require-git-clean-sources`. Verify against clean `git HEAD` or alert user. |
| `INVALID_LINE_ANCHOR` / `ANCHOR_QUOTE_MISMATCH` | Cited `#Lstart-Lend` is out of bounds, inverted, inside frontmatter/quarantine, or quoted hunk does not match disk verbatim. Re-read source window and fix citation. |
| `DIMENSIONAL_ALCHEMY` | Inline `[CALC: ...]` expression violates physical unit dimensionality or arithmetic equality. Fix formula and units. |
| `QUALITATIVE_MODIFIER_DROP` | Prose drops required fastener length/head-style or electrical rating present in source. Restore complete specification or tag `[TBD: ...]`. |

### Gate 4 — Cryptographic Verification Receipt (`VRF-<12hex>`)
Confirm `verify_claims.py` exits `0` and emits a deterministic `VRF-<12hex>` receipt binding the target SHA-256 and source SHA-256 hashes before promoting the task item to `[SOLVED]`.

---

## 3. Stop & Escalation Conditions

- **`[EXTRACTION BLOCKED — ABORTED]`**: Halt immediately if any source file passed to `--sources` is unreadable, missing, or fails parser extraction.
- **Source Conflict Halt (`Tier A` vs. `Tier B`)**:
  - If two primary sources conflict on a load-bearing engineering parameter (`Tier A`), halt immediately before downstream sizing or code generation and surface the discrepancy.
  - If authoring documentation (`Tier B`), insert `[TBD: CONFLICT — <source_A_val> vs <source_B_val>]` inline and list all open `[TBD]` items in the completion summary.
