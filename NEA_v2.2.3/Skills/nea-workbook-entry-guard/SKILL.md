---
name: "nea-workbook-entry-guard"
description: "Protects NetCom Excel workbooks during Mode 2 editing by enforcing Project BOM Columns D through I and CRL Summary B17 through B38 formula locks, mandatory 3-tier catalog lookup before part entry, and OpenXML extension preservation via edit_nea_workbooks and inspect_nea_workbooks so cross-sheet dropdowns stay intact. Use whenever creating, editing, repairing, or saving any NetCom xlsx workbook."
---

# NEA Skill: Safe Workbook Data Entry, Formula Locks & OpenXML Preservation (NEA-SKL-002)

## 1. Purpose & Why Standard `openpyxl.save()` Corrupts NetCom Templates

NetCom's controlled Excel templates (`BOM_Materials_Master_Template.xlsx`, `Cable_Running_List_Template.xlsx`, and `Project_Cover_Sheet_Template.xlsx`) rely on advanced OpenXML structures:
1. **Cross-Sheet `<x14:dataValidations>` inside `<extLst>`**: Excel stores cross-worksheet dropdown lists (such as `'Reference Lists'!$A$1:$A$3`, `'Reference Lists'!$B$1:$B$2`, `'Reference Lists'!$C$1:$C$12`, `'Reference Lists'!$D$1:$D$11`) inside the worksheet's `<extLst>` XML extension block.
   - **Critical Hazard**: When Python `openpyxl.load_workbook()` saves a workbook (`wb.save()`), **`openpyxl` silently strips `<extLst>` (`<x14:dataValidations>`)**, destroying cross-sheet dropdowns or leaving split/misaligned validation ranges when rows/columns are edited!
2. **3-Tier Cascading `XLOOKUP` & Dynamic Array `VSTACK` Formulas**:
   - `Project BOM` (`A8:I155`) and `Lists!H1` (`_xlfn.ANCHORARRAY` / `_xlfn.VSTACK` / `_xlfn.XLOOKUP`) must never be overwritten with static values or broken by inserting/deleting columns.

This skill defines the mandatory rules and OpenXML-safe editing protocol for all Mode 2 workbook modifications using `scripts/inspect_nea_workbooks.py`.


## 2. Pre-Flight Foundation Checks (Before Modifying Any `.xlsx` File)

1. **Record Pre-Edit Baseline (`orig.xlsx`)**:
   - Before modifying any workbook in Code Interpreter, keep an unmodified copy of the original uploaded `.xlsx` file (`orig_path`) so post-write verification (`python3 scripts/inspect_nea_workbooks.py --verify-write <orig_path> <edited_path>`) can compare formulas, table definitions, and DataValidations before and after the edit.
2. **Verify Workbook Role & Editable Cell Boundaries**:
   - **`BOM_Materials_Master` (`Project BOM` `A7:J155`)**:
     - **Editable Cells ONLY**: `Column B` (`MB P/N` `B8:B155`), `Column C` (`Qty` `C8:C155`), `Column J` (`Notes` `J8:J155`), and `Cover Sheet` metadata inputs (`D10:D26`, `H24`, including `Document Status` dropdown `D26:H26`).
     - **Formula-Locked (NEVER TOUCH)**: `Column A` (`Line` `=IF(B8="","",ROW()-7)`), `Columns D:I` (`Category`, `Manufacturer`, `MFG Part Number`, `UOM`, `Description`, `Status` 3-tier `XLOOKUP`), `Project BOM` Row 2 banner (`B2`, `E2`, `H2`), `G4:G5` (`Total FT` / `Total EA/KT/BX`), `Cover Sheet` Revision History row 1 (`B32:C32`), and `Lists!H1`.
   - **`Cable_Running_List` (`Cable Running List` `A2:P1087`)**:
     - **16-Column Schema Lock (`A:P`)**: Never insert, delete, or reorder columns `A:P`, and never add a 17th per-row `Cable Run Status` column (`GOV-005`).
     - **Editable Cells**: `Rows 3..1087` across `Cols A:P` (`A=Run ID`, `B=Classification`, `C..F=NE Loc/Rack/Port/Conn`, `G..J=FE Loc/Rack/Port/Conn`, `K=Media Type`, `L=Cable Type`, `M=Cable Qty`, `N=Length (ft)`, `O=Special Requirement`, `P=Comments`), plus `Cover Sheet` inputs (`D10:D28`, `H26`, including `Project Number` `D12` and `Document Status` dropdown `D28:H28`).
     - **Formula-Locked**: `Cover Sheet` Revision History row 1 (`B34:C34`, `=IF($H$26="","",$H$26)` and `=IF($D$26="","",$D$26)`; `B30:C30` on legacy `R24/R30` sheets).
   - **`Materials Master` (`tblMaterials`), `Fiber Assemblies`, `Cable Harness`**:
     - Never rename `tblMaterials` or alter column orders (`A:G` on `Materials Master`; `A:H` on `Fiber Assemblies` and `Cable Harness`).


## 3. Step-Level Verification Gates (Safe Editing & `<extLst>` Preservation)

### Gate 1 — Mandatory 3-Tier Catalog Lookup Before `Project BOM` Entry (`Pillar 5`)
- Before writing any `MB P/N` or `TPN##` into `Project BOM` `Column B`, run the bundled script:
  `python3 scripts/inspect_nea_workbooks.py . --lookup "<part_or_keyword>"`
- Confirm that:
  1. The exact `MB P/N` or `TPN##` exists in `tblMaterials`, `Fiber Assemblies`, or `Cable Harness`.
  2. The catalog `UOM` (`FT` vs `EA`/`KT`/`BX`) matches the physical quantity being entered into `Column C` (never put `FT` cable footage onto an `EA` jack/panel `MB P/N`).
  3. The catalog `Status` is `Active` or `Preferred` (if `Pending`, `Limited Use`, `Obsolete`, or `Inactive`, flag for engineer approval first).

### Gate 2 — Deterministic Safe-Write Engine (`scripts/edit_nea_workbooks.py`) & `<extLst>` Preservation
Prefer using the bundled pure-stdlib OpenXML safe-write helper (`scripts/edit_nea_workbooks.py`) with a structured JSON edit manifest (`python3 scripts/edit_nea_workbooks.py --schema` for format details):

```bash
python3 scripts/edit_nea_workbooks.py <orig.xlsx> --manifest edit_manifest.json --out <edited.xlsx>
```

`edit_nea_workbooks.py` enforces Cover Sheet label locks, `Project BOM` (`Cols B, C, J`) / `CRL` (`Cols A:P`, `Rows 3..1087`) write boundaries, 3-tier catalog & UOM verification, CRL physical port collision checks (`CRL-DATA-003`), native `<extLst>` (`<x14:dataValidations>`) / `<sheetData>` sort preservation, cached formula sync, and automatically executes `--verify-write` (`NEA-WRT-<12hex>`).

If manual `openpyxl` edits are ever required instead, `--verify-write` in `scripts/inspect_nea_workbooks.py` calls `preserve_openxml_extensions(orig_xlsx, edited_xlsx)` to restore any `<extLst>` cross-sheet dropdowns stripped by `openpyxl.save()`. You can also invoke it directly in Python:

```python
import sys; sys.path.insert(0, "scripts")
from inspect_nea_workbooks import preserve_openxml_extensions
preserve_openxml_extensions(orig_xlsx, edited_xlsx)
```

### Gate 3 — Mandatory Post-Write Verification (`--verify-write`)
- After saving `edited_xlsx`, execute the bundled script:
  `python3 scripts/inspect_nea_workbooks.py --verify-write <orig_xlsx> <edited_xlsx>`
- Do **not** provide the download link to the engineer unless `--verify-write` exits `0` and prints **`[WRITE-VERIFIED: PASS | NEA-WRT-...]`**.


## 4. Stop & Escalation Conditions

1. **Formula Lock Violation (`[WRITE BLOCKED — FORMULA OVERWRITE DETECTED]`)**:
   - If `--verify-write` reports that any `<f>` formula in `Project BOM` (`Col A`, `Cols D:I`, `G4:G5`), `Cover Sheet` Revision History (`B32:C32` / `B34:C34`), or `Lists!H1` was lost or overwritten, discard the edited file immediately, re-apply edits strictly to editable columns (`B, C, J`), and re-verify.
2. **DataValidation / Dropdown Regression (`[WRITE BLOCKED — DV CORRUPTION DETECTED]`)**:
   - If `--verify-write` reports any split-column DataValidation or missing `<x14:dataValidation>` dropdown rule, run `preserve_openxml_extensions(orig_xlsx, edited_xlsx)` and re-verify before returning the file.
