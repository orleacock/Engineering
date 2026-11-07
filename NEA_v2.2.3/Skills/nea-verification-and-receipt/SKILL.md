---
name: "nea-verification-and-receipt"
description: "Executes deterministic OpenXML pre and post verification in Code Interpreter and emits tamper-evident cryptographic receipts NEA-VRF (proving 0 bytes modified during Mode 1 reviews) and NEA-WRT via verify-write (proving 0 formulas or dropdowns stripped during Mode 2 edits). Use before completing any NetCom engineering review report or returning any modified xlsx workbook."
---

# NEA Skill: Pre/Post Deterministic Verification & Cryptographic Receipts (NEA-SKL-003)

## 1. Purpose & Verification Architecture

Remote Windows workstations running Microsoft 365 Copilot Chat or Cowork do not have background workstation hooks watching the LLM. To guarantee that every review report and every workbook edit is 100% trustworthy, **verification is enforced inside the Code Interpreter execution loop** via two deterministic cryptographic receipts produced by the bundled `scripts/inspect_nea_workbooks.py` script:

1. **`NEA-VRF-<12hex>` (`Mode 1 Read-Only Inspection Receipt`)**:
   - Proves that all attached `.xlsx` workbooks were deterministically parsed via OpenXML in the active session and that `Pre/Post SHA-256` source immutability passed (`0 bytes modified`).
2. **`NEA-WRT-<12hex>` (`Mode 2 Post-Write Integrity & Diff Receipt`)**:
   - Proves that a modified `.xlsx` workbook preserves `100%` of protected `<f>` formulas, `100%` of `<dataValidation>` / `<x14:dataValidation>` dropdown rules, and `0` unverified `"Not found"` part keys compared to the pre-edit baseline workbook.


## 2. Bundled Script Execution (`scripts/inspect_nea_workbooks.py`)

1. **Locate and Run `scripts/inspect_nea_workbooks.py` on Turn 1**:
   - **For Role-Scoped Reviews / Audits**: `python3 scripts/inspect_nea_workbooks.py . --scope <review|bom|crl|catalog|repair>`
   - **For Catalog Lookups**: `python3 scripts/inspect_nea_workbooks.py . --lookup "<search_term>"`
   - **For Automated Non-Destructive Repair**: `python3 scripts/inspect_nea_workbooks.py . --repair --out-dir Repaired_Workbooks`
   - **For Post-Write Audits**: `python3 scripts/inspect_nea_workbooks.py --verify-write <original.xlsx> <modified.xlsx>`
2. **Verify Zero Extraction Errors**:
   - Confirm the script outputs `Source Workbook Immutability (Pre/Post SHA-256 Check): PASS` (for Mode 1) or `[WRITE-VERIFIED: PASS | Token: NEA-WRT-...]` (for Mode 2). If script execution fails, report the failure rather than estimating results.


## 3. Step-Level Verification Gates

### Gate A — Mode 1 Review Verification Checklist (`NEA Package Reviewer`)
Before emitting the 6-section Engineering Review Report, verify all five items against the `scripts/inspect_nea_workbooks.py` stdout:
1. **Header Receipt**: The report header includes the exact `Live Package Verification Token: NEA-VRF-<12hex>` and the 10-character `SHA256=...` hash for each evaluated `.xlsx` workbook.
2. **Scorecard Parity**: The counts in the Section 1 `Finding Severity Scorecard` table (`AR-##`, `RR-##`, `ADV-##`, `INF-##`) match the exact number of finding bullets in Section 4, and the `Release Readiness Outcome` matches the highest active severity (`>=1 AR-##` $\rightarrow$ `Action Required Before Release`).
3. **Coordinate & Range Accuracy**: Every cited row (`R...`), cell (`D10`, `B30`, `G4`), `Run ID` range, and `MB P/N` matches the telemetry printout verbatim.
4. **Punch-List Completeness**: Section 5 (`Engineer Closeout Punch List`) contains a `- [ ]` checkbox for every active deliverable finding in Section 4.
5. **Cross-Duty Routing (`Section 6`)**: Structural formula/OpenXML repairs and unreferenced catalog hygiene items are routed cleanly to `NEA Repair Tool` and `NEA Catalog Manager` in Section 6.

### Gate B — Mode 2 Workbook Edit & Repair Verification Checklist (`BOM / CRL / Catalog / Repair Agents`)
Before providing a downloadable `.xlsx` link to the engineer, run `python3 scripts/inspect_nea_workbooks.py --verify-write <original.xlsx> <modified.xlsx>` (or `--repair`) and include this compact **Write Integrity & Audit Receipt** in your response:

```markdown
### Write Integrity & Audit Receipt
- **Write Verification Status**: `PASS` (`NEA-WRT-[12-hex-chars]`)
- **Baseline -> Modified SHA-256**: `[orig_sha10]` $\rightarrow$ `[new_sha10]`
- **Protected Formula Check (`<f>`)**: `PASS (0 formulas overwritten or deleted | [K] formulas restored)`
- **DataValidation & `<extLst>` Dropdown Check**: `PASS (0 anomalies)`
- **Cells Modified (`[N]` cells)**:
  - `[Sheet!Cell]`: `"[Old Value]"` $\rightarrow$ `"[New Value]"`
```

### Gate C — Lightweight Cross-Duty Agent Advisories (`SECTION 7` Telemetry Echo)
When `scripts/inspect_nea_workbooks.py` outputs `SECTION 7: CROSS-DUTY AGENT ROUTING & HANDOFF ADVISORIES` (`🔄 [CROSS-DUTY -> <Agent Name>]`), append a compact callout box at the bottom of your response listing any sister-agent advisories (omitting your own agent role):

```markdown
> [!TIP]
> **Cross-Duty Agent Advisories (`NEA-SCR-001`)**
> - **$\rightarrow$ `NEA Repair Tool`**: `[Exact structural/formula/validation/template summary from Section 7]`
> - **$\rightarrow$ `NEA Catalog Manager`**: `[Exact 3-tier catalog duplicate/completeness summary from Section 7]`
> - **$\rightarrow$ `NEA BOM Builder` / `NEA CRL Builder` / `NEA Package Reviewer`**: `[Exact sister-agent handoff summary from Section 7]`
```


## 4. Stop & Escalation Conditions

1. **Missing `NEA-VRF` or `NEA-WRT` Token**:
   - Never fabricate a `NEA-VRF-...` or `NEA-WRT-...` hexadecimal string. If Code Interpreter did not run `scripts/inspect_nea_workbooks.py` and print the token, halt and run the Python check first.
2. **Failed `--verify-write` Audit (`Exit Code != 0`)**:
   - If `--verify-write` reports any `[FAIL]` item (overwritten formula in `Project BOM` `Col A` or `Cols D:I`, static overwrite in `Cover Sheet!B30:C30`, stripped `<extLst>` dropdowns, or unmapped `MB P/N`), **do not** output the broken `.xlsx` file. Fix the edit in Code Interpreter and re-run `--verify-write` until all checks return `PASS`.
