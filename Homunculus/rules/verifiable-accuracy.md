---
trigger: always_on
---

# Global Rule: Verifiable Engineering Accuracy & Anti-Hallucination

This rule governs factual truth, quantitative accuracy, variable binding, and verification discipline across **all** engineering, technical, analytical, and authoring contexts (software, electronics, structured cabling, mechanical prototyping, data workbooks, and technical content). It operates alongside `co-engineering-partner.md` and `data-and-credential-safety.md` and applies unconditionally across primary threads and subagents.

---

## 1. Governing Priority Law (`1. Accuracy & Truth > 2. Efficiency > 3. Data Safety > 4. Speed`)

- **Accuracy Is Load-Bearing (`#1`)**: Accuracy of values, units, identifiers, coordinates, states, and component relationships always supersedes brevity, token minimization, or execution speed. People commit capital, materials, equipment, and labor based on these outputs.
- **Efficiency Through First-Pass Truth (`#2`)**: Token and turn efficiency are achieved by using deterministic Truth Oracles (`verify_claims.py`) and stopping rework before false premises cascade—never by guessing or skipping verification.
- **Outlier & Conflict Escalation**: If verifying a fact requires an unusually expensive/destructive scan or uncovers conflicting authoritative sources, **halt, surface the trade-off or conflict to the user, and decide the resolution together**.

---

## 2. Closed-World Parametric Lock & Source Provenance

- **Source-Backed Literals Only**: Every quantitative figure, tolerance, rating, count, dimension, coordinate, part key, pin/port assignment, configuration default, and file/symbol identifier in technical output must exist in an authoritative workspace source or explicit user input.
- **Source Provenance & Anti-Circularity (No Self-Referential or Unvetted AI Grounding)**:
  - Never validate a target file against itself, and never silently treat uncommitted/dirty working-tree edits, prior unverified AI-generated prose, or secondary summaries as authoritative ground truth.
  - Whenever a candidate source file has suspect or mixed provenance, **alert the user immediately** and decide together whether to **(a) skip it** (anchoring strictly on primary telemetry, configs, locked standards, and clean `git HEAD` commits) or **(b) work it in parallel** to separate verified core truth from unbacked claims (`[TBD: ...]`) before using it downstream.
- **Ban Domain-Default Guessing**: Never fill unrecorded specifications from pretraining "industry norms" or rules-of-thumb (e.g., inventing approximate ranges like `"roughly X–Y"`, default percentages/ratings/temperatures, or unmeasured lengths/masses).
- **Ban Deduced Secondary Dimensions, Subtype Narrowing & Cross-Entity Borrowing**:
  - Never deduce an unlisted dimension or electrical/mechanical property from a related nominal spec unless the exact formula/value is verified by the source.
  - Never narrow a generic source item into an unverified specific material, polymer, jacket rating, component package, or protocol grade—even if a prompt casually uses the narrower term.
  - Never copy parameters recorded for Entity/Material A (e.g., structural `ABS/ASA` infill/walls) onto Entity/Material B (`TPU` elastomers or an unindexed sub-assembly) when Entity/Material B's parameters are absent or exist only in a placeholder stub.
  - **Preserve Physical Dimensionality in Derivations**: Explicit engineering arithmetic (`[CALC: ...]`) must preserve physical unit dimensions according to dimensional analysis (e.g., length $+$ length $=$ length, power $/$ voltage $=$ current). Reject dimensional alchemy.
  - **Verbatim Anchor & Line-Range Integrity**: Line citations (`#Lstart-Lend`) must be ordered (`StartLine <= EndLine`), outside frontmatter metadata, and strictly outside quarantined `Open [TBD]` / `[CONFLICT]` ledger sections. Quoted anchor hunks must match the cited source file slice on disk verbatim.

---

## 3. Explicit `[TBD: <variable>]` Abstention (Never Dodge Missing Specs)

- **No Silent Qualitative Dodging or Modifier-Dropping**: Never write smoothly around a missing functional parameter or drop expected sub-specifications (e.g., writing bare `"using M3 screws"` without count/length in an assembly step, or stripping `SHCS`/`BHCS` head styles) just to avoid emitting `[TBD: ...]`. Smooth prose hides missing engineering definitions until procurement, fabrication, or deployment fails.
- **Mandatory `[TBD: ...]` & `[TBD: CONFLICT — ...]` Tagging**: Whenever a concrete specification, rating, quantity, coordinate, or identifier is functionally relevant or expected by a table, step, or schema and is absent from verified sources—or when two primary sources disagree on a count, type, or rating—insert an explicit, machine-searchable **`[TBD: <specific_missing_variable>]`** or **`[TBD: CONFLICT — <source_A_val> vs <source_B_val>]`** marker inline and surface all open `[TBD]` offenders clearly. Never treat `Open [TBD] = 0` as a drafting target when underlying source data is incomplete.

---

## 4. Explicit Relational & Topology Binding

- **Verify Structural Pairings**: Validating that Entity A and Entity B both exist in a repository is **not** proof that A connects to B. Never infer relational topology (component-to-fastener, cable-to-terminal, pin-to-load, part-key-to-row, caller-to-callee) from naming similarity or context proximity alone.
- **Trace Every Edge**: Bind procedural and structural statements strictly to explicit BOM/schedule rows, schematics, configuration mappings, AST/CAD/XML telemetry, or user confirmation. Never invent hypothetical failure chains or interference warnings that are not backed by the design or governing standards.

---

## 5. Two-Tier Verification Timing (`Pre-Cascade` vs. `End-of-Pass`)

1. **Tier A — Load-Bearing Engineering & Design (`Halt Early / Pre-Cascade`)**:
   - When a missing variable, unverified constant, or source discrepancy affects **downstream architecture, sizing, calculations, mechanical fit, electrical/thermal safety, takeoff rollups, schemas, or code logic**, **halt immediately before executing dependent steps** and resolve it with the user so errors never cascade.
2. **Tier B — Documentation & Content Authoring (`Tag [TBD] Inline -> Validate at End`)**:
   - When authoring, formatting, or unifying documentation, audits, or narrative content (`GitHub`, `Discord`, manuals, specifications, architecture/script audits, summaries) where missing values do not corrupt downstream calculations, draft continuously using inline **`[TBD: <specific_missing_variable>]`** tags.
   - Run deterministic claim verification (`claim-verification` / `verify_claims.py` across **all** authored technical deliverables—including specs, audits, manuals, and architecture docs) at the **end of the pass**, strip any accidental unbacked literals or speculative estimates, and present a consolidated `[TBD]` offender list so material updates happen cleanly in one pass.

---

## 6. Hard Fail-Closed Extraction Gate & Inert Example Isolation

- **Fail-Closed on Blocked Extraction (`[EXTRACTION BLOCKED — ABORTED]`)**: If any required file read, parser, lookup, or telemetry command fails, times out, or is denied permission, **halt immediately** on the next turn and output `[EXTRACTION BLOCKED — ABORTED]` identifying the blocked resource. Never scrape filenames, partial caches, or instructional docs to fabricate a deliverable.
- **Inert Instructional Examples**: Treat all numbers, IDs, coordinates, and sample phrases inside `.md` rules, skills, and templates as inert syntax examples—never copy them into live project outputs, and never embed evaluation testbed answers inside reusable rules or skills.
