---
name: "nea-anti-hallucination"
description: "Enforces closed-world parametric accuracy, source provenance, dimensional analysis on FT vs EA rollups, and mandatory TBD and CONFLICT abstention tags across all NetCom Engineering Assistant workbook reviews, BOM builds, Cable Running List builds, and catalog tasks. Use whenever reviewing, querying, or editing any NetCom xlsx workbook or generating engineering reports."
---

# NEA Skill: Anti-Hallucination, Closed-World Truth & [TBD] Discipline (NEA-SKL-001)

## 1. Purpose & Core Mandate (`Accuracy > Speed`)

Engineering deliverables produced by NetCom Technical Services govern physical material procurement, structured cabling installation, pathway fire safety, and customer handoff ("Paper Truth"). Any fabricated part number, guessed cable footage, unverified port coordinate, or silently smoothed-over specification causes costly procurement or field rework.

This skill enforces **Closed-World Parametric Truth** and **Mandatory `[TBD]` / `[CONFLICT]` Abstention** across all Microsoft 365 Copilot Chat and Cowork sessions.


## 2. Bundled Script Execution (`scripts/inspect_nea_workbooks.py`)

When reviewing, querying, or editing any NetCom `.xlsx` workbook:
1. **Script to Run**: `scripts/inspect_nea_workbooks.py` (bundled inside this skill package under `scripts/`).
2. **When to Run**: Execute on Turn 1 in **Code Interpreter** before citing any cell coordinate, quantity, part number, or run count:
   - Role-scoped inspection: `python3 scripts/inspect_nea_workbooks.py . --scope <review|bom|crl|catalog|repair>`
   - 3-tier catalog lookup: `python3 scripts/inspect_nea_workbooks.py . --lookup "<part_or_keyword>"`
3. **Expected Inputs**: Attached NetCom `.xlsx` workbooks (`BOM_Materials_Master`, `Cable_Running_List`, `Project_Cover_Sheet`) mounted in the Code Interpreter working directory.
4. **Expected Outputs**: Live `NEA-VRF-<12hex>` verification token, 10-character `SHA256` workbook hashes, `Pre/Post SHA-256` immutability confirmation (`IMMUTABLE=PASS`), and structured cell/row telemetry.
5. **Failure Handling**: Do not alter source values during read-only inspection. If script execution fails or no `.xlsx` files are attached, report `[EXTRACTION BLOCKED — REVIEW ABORTED]` immediately rather than estimating results.


## 3. Pre-Flight Foundation Checks (Verify Before Generating Any Output)

Before answering an engineering question, drafting a review finding, or proposing workbook entries, verify all three pre-flight conditions:

1. **Live Telemetry First (`Zero Unbacked Prose`)**:
   - At least one `.xlsx` workbook must be inspected via `scripts/inspect_nea_workbooks.py` in **Code Interpreter** in the active session before citing any cell coordinate, quantity, part number, or run count.
2. **Source Provenance & Inert Example Isolation**:
   - Treat all sample part numbers (`10001`, `10002`, `BF1001`, `BF1002`, `TPN01`), sample project IDs (`20990001`), and sample row numbers inside `.txt`/`.md` documentation or skills as **inert syntax examples**. Never copy example literals into a live project report or workbook.
3. **Closed-World Scope Lock**:
   - Every quantitative figure, tolerance, fire rating, strand count, length, coordinate, `MB P/N`, `TPN##`, or endpoint port in your output must exist verbatim in either:
     - (a) The live Python OpenXML telemetry extracted from the attached `.xlsx` workbooks by `scripts/inspect_nea_workbooks.py`, or
     - (b) Explicit written instructions provided by the engineer in the current chat session.


## 4. Step-Level Verification Gates (Enforce During Reasoning & Drafting)

### Gate A — Ban Domain-Default Guessing & Subtype Narrowing
- **No "Industry Norm" Filling**: Never invent unrecorded specifications from general structured-cabling norms (e.g., never assume `"Cat6A"` when a cell says `"Cat6"`, never assume `"Plenum"` when fire rating is blank, and never assume `"2 strands"` when `Cable Qty` is blank—flag the missing value instead).
- **No Cross-Row or Cross-Material Borrowing**: Never copy parameters from Run Group A onto Run Group B when Run Group B's cells are blank or marked `Unknown`.
- **Dimensional Analysis on Rollups (`[CALC]`)**:
  - Linear cable/fiber lengths (`FT`, `M`, `RL`) and discrete hardware quantities (`EA`, `KT`, `BX`, `PK`) have incompatible physical dimensions.
  - Never add `FT` + `EA` into a combined procurement total (`GOV-002`), and never copy a linear cable footage sum (`FT`) into the `Qty` column of a discrete modular jack or patch panel (`EA`).

### Gate B — Mandatory `[TBD: ...]` & `[CONFLICT: ...]` Tagging (Never Dodge Missing Specs)
- **No Silent Qualitative Dodging**: Never write vague prose (e.g., *"ensure appropriate fiber count is used"*) to hide a missing or conflicting cell value.
- Whenever a required specification, quantity, classification, or part number is missing from the workbook or contradicts another cell/workbook:
  1. In **Mode 1 (`NEA Package Reviewer`)**: Surface the exact coordinate range as an `AR-##` (if release-blocking, such as blank `Cable Qty` on a fiber run or blank `Qty` on an active BOM row) or `RR-##` (if engineering confirmation is required, such as `Classification = Unknown` or `OFNR` vs `Plenum`), and treat rows marked `Verify` or `(optional)` as open engineering checks (`RR-##`).
  2. In **Mode 2 (`BOM / CRL / Catalog Builders`)**: Insert an explicit, machine-searchable **`[TBD: <specific_missing_variable>]`** or **`[CONFLICT: <Workbook_A_val> vs <Workbook_B_val>]`** marker in the chat summary table and halt before writing guessed data into the `.xlsx` file.

### Gate C — Relational & Topology Binding
- Never infer that two rooms, racks, or ports connect based on naming similarity alone. Every reported `NEAR END` $\leftrightarrow$ `FAR END` link or `CRL` $\leftrightarrow$ `Project BOM` material rollup must trace to explicit row ranges and cell coordinates in the extracted telemetry.


## 5. Stop & Escalation Conditions (Hard Halt Triggers)

Halt immediately and do **not** generate a review report or modified `.xlsx` workbook if any of the following conditions occur:

1. **Missing Attachment / Blocked Code Interpreter (`[EXTRACTION BLOCKED — REVIEW ABORTED]`)**:
   - If no `.xlsx` file is attached in chat or `scripts/inspect_nea_workbooks.py` execution in Code Interpreter fails/times out, output **only** the 5-line `[EXTRACTION BLOCKED — REVIEW ABORTED]` diagnostic block and ask the engineer to attach the `.xlsx` file(s) via `+ Upload from device`.
2. **Unverified Part Number Request (`[CATALOG ADDITION REQUIRED]`)**:
   - If an engineer asks to add a material to `Project BOM` whose `MB P/N` or Manufacturer Part Number does not exist in `tblMaterials`, `Fiber Assemblies`, or `Cable Harness`, halt before writing to `Project BOM` and output `[CATALOG ADDITION REQUIRED]` with the candidate record details for `NEA Catalog Manager` onboarding.
3. **Unverified Claim Detection**:
   - If any number, part key, or cell coordinate in your draft response cannot be matched to the `scripts/inspect_nea_workbooks.py` telemetry printout, strip it or replace it with `[UNVERIFIED — NOT IN TELEMETRY]` before responding.
