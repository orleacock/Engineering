#!/usr/bin/env python3
"""Deterministic, fail-closed safe OpenXML writer for NetCom NEA v2.2.3 workbooks.

Enforces Behavior_v2.2.3.txt and NEA-SKL-002 write-boundary locks, pre-write
3-tier catalog / UOM / CRL endpoint gates, cached formula synchronization,
and automatic NEA-WRT post-write verification via inspect_nea_workbooks.py.
"""

import argparse
import hashlib
import json
import os
import re
import shutil
import sys
import tempfile
import xml.etree.ElementTree as ET
import zipfile

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

from inspect_nea_workbooks import (  # noqa: E402
    NS,
    SharedStringTable,
    _col_to_idx,
    _idx_to_col,
    _sort_sheetdata_rows_and_cells,
    cell_info,
    cell_val,
    classify_workbook_role,
    find_cover_sheet_coords,
    iso_to_excel_serial,
    parse_xlsx,
    preserve_openxml_extensions,
    run_verify_write,
)

DOCUMENT_STATUS_VALUES = {
    "Draft",
    "Internal Review",
    "Issued",
    "Issued For Construction",
    "Archived",
}

ACTIVE_MATERIAL_STATUSES = {"Active", "Preferred"}
GATED_MATERIAL_STATUSES = {"Pending", "Limited Use"}
RETIRED_MATERIAL_STATUSES = {"Obsolete", "Inactive"}

COPPER_CABLE_TYPES = {"Cat5e", "Cat6", "Cat6A", "Cat7", "Cat8", "Bulk Pair"}
FIBER_CABLE_TYPES = {"OM1", "OM2", "OM3", "OM4", "OM5", "OS2"}
COPPER_CONNECTORS = {"RJ45", "Punch", "Serial", "Amphenol", "Wrap"}
FIBER_CONNECTORS = {"LC", "SC", "ST", "FC", "MPO-12", "MTP"}
SPECIAL_REQUIREMENTS = {
    "Standard",
    "Crossover",
    "Rollover",
    "Redundant Path",
    "Diverse Route",
    "Wrap",
}
BOM_ALLOWED_COLS = {"B", "C", "J"}
CRL_COL_FIELDS = [
    ("A", "run_id"),
    ("B", "classification"),
    ("C", "ne_location"),
    ("D", "ne_rack"),
    ("E", "ne_port"),
    ("F", "ne_connector"),
    ("G", "fe_location"),
    ("H", "fe_rack"),
    ("I", "fe_port"),
    ("J", "fe_connector"),
    ("K", "media_type"),
    ("L", "cable_type"),
    ("M", "cable_qty"),
    ("N", "length_ft"),
    ("O", "special_requirement"),
    ("P", "comments"),
]
CRL_FIELD_TO_COL = {field: col for col, field in CRL_COL_FIELDS}

CELL_REF_RE = re.compile(r"^([A-Z]+)(\d+)$")


def _parse_cell_ref(coord):
    """Splits an Excel cell reference like 'D10' into ('D', 10)."""
    m = CELL_REF_RE.match(str(coord or "").strip().upper())
    if not m:
        return None, None
    return m.group(1), int(m.group(2))


def _coerce_number(raw_val):
    """Parses an integer or float if valid, otherwise returns None."""
    if isinstance(raw_val, bool):
        return None
    if isinstance(raw_val, (int, float)):
        return raw_val
    s = str(raw_val).strip()
    if not s:
        return None
    try:
        if re.fullmatch(r"[+-]?\d+", s):
            return int(s)
        return float(s)
    except ValueError:
        return None


def _build_catalog_index(wb_info):
    """Builds exact MB P/N lookup index across tblMaterials, Fiber Assemblies, and Cable Harness."""
    index = {}
    duplicates = set()
    mm = wb_info["sheets"].get("Materials Master", {})
    for r in sorted(mm.keys()):
        if r < 4 or r > 600:
            continue
        pn = cell_val(mm, r, "B").strip()
        if not pn:
            continue
        rec = {
            "source": "tblMaterials",
            "row": r,
            "mb_pn": pn,
            "category": cell_val(mm, r, "A").strip(),
            "manufacturer": cell_val(mm, r, "C").strip(),
            "mfg_pn": cell_val(mm, r, "D").strip(),
            "uom": cell_val(mm, r, "E").strip(),
            "description": cell_val(mm, r, "F").strip(),
            "status": cell_val(mm, r, "G").strip(),
        }
        if pn in index:
            duplicates.add(pn)
        else:
            index[pn] = rec

    for sheet_name in ("Fiber Assemblies", "Cable Harness"):
        sh = wb_info["sheets"].get(sheet_name, {})
        for r in sorted(sh.keys()):
            if r < 4:
                continue
            pn = cell_val(sh, r, "C").strip()
            if not pn:
                continue
            rec = {
                "source": sheet_name,
                "row": r,
                "mb_pn": pn,
                "category": cell_val(sh, r, "A").strip(),
                "manufacturer": cell_val(sh, r, "D").strip(),
                "mfg_pn": cell_val(sh, r, "E").strip(),
                "uom": cell_val(sh, r, "F").strip(),
                "description": cell_val(sh, r, "G").strip(),
                "status": cell_val(sh, r, "H").strip() or "Active",
            }
            if pn in index:
                duplicates.add(pn)
            else:
                index[pn] = rec
    return index, duplicates


def _resolve_cover_sheet_field_map(cov_rows):
    """Maps Cover Sheet logical field names to exact coordinate cells by label."""
    label_map = {
        "Project Name": ("project_name", "D"),
        "Project Number": ("project_number", "D"),
        "Customer": ("customer", "D"),
        "Customer Contact": ("customer_contact", "D"),
        "Building": ("building", "D"),
        "Site Address": ("site_address", "D"),
        "Project Manager": ("project_manager", "D"),
        "Designer / Engineer": ("designer", "D"),
        "Installation Contractor": ("installation_contractor", "D"),
        "Issue Date": ("issue_date", "D"),
        "Document Status": ("document_status", "D"),
    }
    coords = find_cover_sheet_coords(cov_rows)
    field_cells = {}
    for r in sorted(cov_rows.keys()):
        b_lbl = cell_val(cov_rows, r, "B").strip()
        f_lbl = cell_val(cov_rows, r, "F").strip()
        if b_lbl in label_map:
            key, col = label_map[b_lbl]
            field_cells[key] = f"{col}{r}"
        if f_lbl == "Revision":
            field_cells["revision"] = f"H{r}"

    # Allow BOM 'building' <-> CRL 'site_address' aliases cleanly where present
    if "building" in field_cells and "site_address" not in field_cells:
        field_cells["site_address"] = field_cells["building"]
    elif "site_address" in field_cells and "building" not in field_cells:
        field_cells["building"] = field_cells["site_address"]

    locked_cells = {f"B{coords['hist_r']}", f"C{coords['hist_r']}"}
    return field_cells, locked_cells, coords


def _plan_and_validate_edits(wb_info, role, manifest, allow_pending=False):
    """Validates manifest schema, write locks, formulas, catalog keys, and CRL rules before any XML edit."""
    errors = []
    warnings = []
    # Map sheet_name -> {coord -> (typed_value, kind)} where kind in {"str", "num", "clear"}
    planned_cells = {}
    allowed_keys = {"cover_sheet", "bom_rows", "crl_rows", "cells"}
    unknown_keys = set(manifest.keys()) - allowed_keys
    if unknown_keys:
        errors.append(f"[SCHEMA_LOCK_VIOLATION] Unknown manifest top-level key(s): {sorted(unknown_keys)}")

    def queue_cell(sheet_name, coord, value, kind):
        sh_rows = wb_info["sheets"].get(sheet_name)
        if sh_rows is None:
            errors.append(f"[SCHEMA_LOCK_VIOLATION] Worksheet '{sheet_name}' does not exist in target workbook")
            return
        col, row_num = _parse_cell_ref(coord)
        if not col:
            errors.append(f"[INVALID_CELL_REF] Invalid cell reference '{sheet_name}!{coord}'")
            return
        ci = cell_info(sh_rows, row_num, col)
        if ci.get("has_formula"):
            errors.append(
                f"[FORMULA_OVERWRITE_BLOCKED] Refusing write to formula-locked cell {sheet_name}!{coord} "
                f"(<f>='{ci.get('f_text') or 'shared'}')"
            )
            return
        planned_cells.setdefault(sheet_name, {})[f"{col}{row_num}"] = (value, kind)

    # 1. Cover Sheet edits
    cov_edits = manifest.get("cover_sheet") or {}
    cov_rows = wb_info["sheets"].get("Cover Sheet", {})
    cov_field_map, cov_locked, cov_coords = _resolve_cover_sheet_field_map(cov_rows)
    if cov_edits:
        if not isinstance(cov_edits, dict):
            errors.append("[INVALID_MANIFEST] 'cover_sheet' must be a JSON object")
        elif "Cover Sheet" not in wb_info["sheets"]:
            errors.append("[SCHEMA_LOCK_VIOLATION] Workbook has no 'Cover Sheet' worksheet")
        else:
            for field_name, val in cov_edits.items():
                if field_name not in cov_field_map:
                    if field_name == "installation_contractor" and role == "BOM":
                        errors.append(
                            "[FIELD_NOT_ON_BOM_COVER] 'installation_contractor' does not exist on BOM Cover Sheet (GOV-006)"
                        )
                    else:
                        errors.append(
                            f"[COVER_FIELD_UNKNOWN] Unsupported Cover Sheet field '{field_name}' "
                            f"(allowed: {sorted(cov_field_map.keys())})"
                        )
                    continue
                target_coord = cov_field_map[field_name]
                if target_coord in cov_locked:
                    errors.append(f"[FORMULA_OVERWRITE_BLOCKED] Refusing write to Cover Sheet Revision History {target_coord}")
                    continue
                if val is None or str(val).strip() == "":
                    queue_cell("Cover Sheet", target_coord, "", "clear")
                elif field_name == "document_status":
                    s_val = str(val).strip()
                    if s_val not in DOCUMENT_STATUS_VALUES:
                        errors.append(
                            f"[INVALID_DOCUMENT_STATUS] '{s_val}' not in approved Lists domain {sorted(DOCUMENT_STATUS_VALUES)}"
                        )
                    else:
                        queue_cell("Cover Sheet", target_coord, s_val, "str")
                elif field_name == "issue_date":
                    num_v = _coerce_number(val)
                    if num_v is not None and 20000 <= num_v <= 80000:
                        queue_cell("Cover Sheet", target_coord, num_v, "num")
                    else:
                        serial = iso_to_excel_serial(str(val).strip())
                        if serial is None:
                            errors.append(
                                f"[INVALID_ISSUE_DATE] '{val}' must be YYYY-MM-DD (or MM/DD/YYYY) date or Excel serial"
                            )
                        else:
                            queue_cell("Cover Sheet", target_coord, serial, "num")
                else:
                    queue_cell("Cover Sheet", target_coord, str(val).strip(), "str")

    # 2. Project BOM edits
    bom_edits = manifest.get("bom_rows") or []
    cat_index = {}
    if bom_edits:
        if role != "BOM" or "Project BOM" not in wb_info["sheets"]:
            errors.append(f"[ROLE_MISMATCH] 'bom_rows' edits require a BOM workbook (detected role='{role}')")
        elif not isinstance(bom_edits, list):
            errors.append("[INVALID_MANIFEST] 'bom_rows' must be a list of row objects")
        else:
            cat_index, cat_dups = _build_catalog_index(wb_info)
            seen_bom_rows = set()
            for entry in bom_edits:
                if not isinstance(entry, dict) or "row" not in entry:
                    errors.append("[INVALID_MANIFEST] Each 'bom_rows' item must be an object containing integer 'row'")
                    continue
                r_num = _coerce_number(entry["row"])
                if not isinstance(r_num, int) or not (8 <= r_num <= 155):
                    errors.append(f"[BOM_BOUNDARY_LOCK] Project BOM row '{entry.get('row')}' outside allowed range 8..155")
                    continue
                if r_num in seen_bom_rows:
                    errors.append(f"[DUPLICATE_TARGET_ROW] Duplicate edit entry for Project BOM row {r_num}")
                    continue
                seen_bom_rows.add(r_num)

                allowed_entry_keys = {"row", "mb_pn", "qty", "notes", "expected_uom", "clear"}
                bad_keys = set(entry.keys()) - allowed_entry_keys
                if bad_keys:
                    errors.append(
                        f"[BOM_COLUMN_LOCK] Prohibited field(s) {sorted(bad_keys)} on Project BOM row {r_num} "
                        "(only mb_pn [Col B], qty [Col C], notes [Col J] are editable; Cols A & D:I are XLOOKUP-locked)"
                    )
                    continue

                if entry.get("clear"):
                    queue_cell("Project BOM", f"B{r_num}", "", "clear")
                    queue_cell("Project BOM", f"C{r_num}", "", "clear")
                    queue_cell("Project BOM", f"J{r_num}", "", "clear")
                    continue

                pb_rows = wb_info["sheets"]["Project BOM"]
                pn = str(entry.get("mb_pn") if "mb_pn" in entry else cell_val(pb_rows, r_num, "B")).strip()
                qty_raw = entry.get("qty") if "qty" in entry else cell_val(pb_rows, r_num, "C")

                if not pn:
                    errors.append(f"[MISSING_MB_PN] Project BOM row {r_num} requires a non-empty 'mb_pn' (or 'clear': true)")
                    continue
                if pn in cat_dups:
                    errors.append(
                        f"[CATALOG_DUPLICATE_KEY] MB P/N '{pn}' has duplicate catalog rows; resolve via NEA Catalog Manager first"
                    )
                    continue
                cat_rec = cat_index.get(pn)
                if not cat_rec:
                    errors.append(
                        f"[CATALOG_LOOKUP_FAILED] Project BOM!B{r_num} MB P/N '{pn}' not found in "
                        "tblMaterials, Fiber Assemblies, or Cable Harness [CATALOG ADDITION REQUIRED]"
                    )
                    continue
                m_status = cat_rec["status"]
                if m_status in RETIRED_MATERIAL_STATUSES:
                    errors.append(
                        f"[RETIRED_CATALOG_PART] Project BOM!B{r_num} MB P/N '{pn}' has retired Status='{m_status}'"
                    )
                    continue
                if m_status in GATED_MATERIAL_STATUSES and not allow_pending:
                    errors.append(
                        f"[GATED_CATALOG_STATUS] Project BOM!B{r_num} MB P/N '{pn}' has Status='{m_status}' "
                        "(pass --allow-pending only with engineer approval)"
                    )
                    continue

                qty_num = _coerce_number(qty_raw)
                if qty_num is None or qty_num <= 0:
                    errors.append(
                        f"[INVALID_BOM_QTY] Project BOM!C{r_num} Qty '{qty_raw}' must be numeric > 0 (UOM='{cat_rec['uom']}')"
                    )
                    continue
                exp_uom = str(entry.get("expected_uom", "")).strip()
                if exp_uom and exp_uom != cat_rec["uom"]:
                    errors.append(
                        f"[UOM_MISMATCH] Project BOM row {r_num} ('{pn}') expected_uom='{exp_uom}' "
                        f"conflicts with catalog UOM='{cat_rec['uom']}'"
                    )
                    continue
                if cat_rec["uom"] == "BX" and qty_num >= 50:
                    warnings.append(
                        f"[BULK_BOX_UOM_CHECK] Project BOM!C{r_num} Qty={qty_num} for UOM='BX' ('{pn}' — "
                        "confirm carton/box count rather than piece count)"
                    )

                if "mb_pn" in entry:
                    queue_cell("Project BOM", f"B{r_num}", pn, "str")
                if "qty" in entry:
                    queue_cell("Project BOM", f"C{r_num}", qty_num, "num")
                if "notes" in entry:
                    n_txt = "" if entry["notes"] is None else str(entry["notes"]).strip()
                    if n_txt:
                        queue_cell("Project BOM", f"J{r_num}", n_txt, "str")
                    else:
                        queue_cell("Project BOM", f"J{r_num}", "", "clear")

    # 3. Cable Running List edits
    crl_edits = manifest.get("crl_rows") or []
    if crl_edits:
        if role != "CRL" or "Cable Running List" not in wb_info["sheets"]:
            errors.append(f"[ROLE_MISMATCH] 'crl_rows' edits require a CRL workbook (detected role='{role}')")
        elif not isinstance(crl_edits, list):
            errors.append("[INVALID_MANIFEST] 'crl_rows' must be a list of row objects")
        else:
            crl_rows = wb_info["sheets"]["Cable Running List"]
            # Build projected post-edit table across Rows 3..1087
            projected_crl = {}
            for r in range(3, 1088):
                row_map = {col: cell_val(crl_rows, r, col).strip() for col, _ in CRL_COL_FIELDS}
                if any(row_map.values()):
                    projected_crl[r] = row_map

            seen_crl_rows = set()
            allowed_crl_keys = {"row", "clear"} | set(CRL_FIELD_TO_COL.keys())
            for entry in crl_edits:
                if not isinstance(entry, dict) or "row" not in entry:
                    errors.append("[INVALID_MANIFEST] Each 'crl_rows' item must contain integer 'row'")
                    continue
                r_num = _coerce_number(entry["row"])
                if not isinstance(r_num, int) or not (3 <= r_num <= 1087):
                    errors.append(f"[CRL_BOUNDARY_LOCK] CRL row '{entry.get('row')}' outside allowed range 3..1087")
                    continue
                if r_num in seen_crl_rows:
                    errors.append(f"[DUPLICATE_TARGET_ROW] Duplicate edit entry for CRL row {r_num}")
                    continue
                seen_crl_rows.add(r_num)

                bad_keys = set(entry.keys()) - allowed_crl_keys
                if bad_keys:
                    errors.append(
                        f"[CRL_SCHEMA_LOCK] Prohibited field(s) {sorted(bad_keys)} on CRL row {r_num} "
                        "(strict 16-column A..P schema; Cable Run Status column is forbidden per GOV-005)"
                    )
                    continue

                if entry.get("clear"):
                    projected_crl.pop(r_num, None)
                    for col, _ in CRL_COL_FIELDS:
                        queue_cell("Cable Running List", f"{col}{r_num}", "", "clear")
                    continue

                cur = dict(projected_crl.get(r_num, {col: "" for col, _ in CRL_COL_FIELDS}))
                for col, field in CRL_COL_FIELDS:
                    if field in entry:
                        v = entry[field]
                        cur[col] = "" if v is None else str(v).strip()
                if any(cur.values()):
                    projected_crl[r_num] = cur
                else:
                    projected_crl.pop(r_num, None)

                for col, field in CRL_COL_FIELDS:
                    if field not in entry:
                        continue
                    v = entry[field]
                    if v is None or str(v).strip() == "":
                        queue_cell("Cable Running List", f"{col}{r_num}", "", "clear")
                    elif field in ("run_id", "cable_qty", "length_ft"):
                        num_v = _coerce_number(v)
                        if num_v is None:
                            errors.append(f"[INVALID_CRL_NUMBER] CRL!{col}{r_num} ({field}) '{v}' must be numeric")
                        else:
                            queue_cell("Cable Running List", f"{col}{r_num}", num_v, "num")
                    else:
                        queue_cell("Cable Running List", f"{col}{r_num}", str(v).strip(), "str")

            # Validate projected full CRL integrity (schema + CRL-DATA-003 port collisions)
            seen_run_ids = {}
            seen_endpoints = {}
            for r in sorted(projected_crl.keys()):
                row_d = projected_crl[r]
                rid_val = _coerce_number(row_d["A"])
                if not isinstance(rid_val, int) or rid_val <= 0:
                    errors.append(f"[INVALID_RUN_ID] CRL row {r} Run ID '{row_d['A']}' must be positive integer")
                elif rid_val in seen_run_ids:
                    errors.append(f"[DUPLICATE_RUN_ID] CRL row {r} duplicates Run ID {rid_val} from row {seen_run_ids[rid_val]}")
                else:
                    seen_run_ids[rid_val] = r

                for req_col, req_lbl in (
                    ("B", "classification"),
                    ("C", "ne_location"),
                    ("D", "ne_rack"),
                    ("E", "ne_port"),
                    ("F", "ne_connector"),
                    ("G", "fe_location"),
                    ("H", "fe_rack"),
                    ("I", "fe_port"),
                    ("J", "fe_connector"),
                ):
                    if not row_d[req_col]:
                        errors.append(f"[MISSING_CRL_FIELD] CRL!{req_col}{r} ({req_lbl}) cannot be blank on an active run")
                if row_d["B"] == "Unknown":
                    warnings.append(f"[CLASSIFICATION_UNKNOWN] CRL!B{r} has Classification='Unknown' (resolve before release)")

                media = row_d["K"]
                ctype = row_d["L"]
                cqty_s = row_d["M"]
                len_v = _coerce_number(row_d["N"])
                ne_conn = row_d["F"]
                fe_conn = row_d["J"]
                spec_req = row_d["O"]
                comments = row_d["P"]

                if media not in ("Copper", "Fiber"):
                    errors.append(f"[INVALID_MEDIA_TYPE] CRL!K{r} Media Type '{media}' must be 'Copper' or 'Fiber'")
                elif media == "Copper":
                    if ctype not in COPPER_CABLE_TYPES:
                        errors.append(f"[MEDIA_CABLE_MISMATCH] CRL row {r}: Copper incompatible with Cable Type '{ctype}'")
                    if cqty_s != "":
                        errors.append(f"[COPPER_CABLE_QTY_FORBIDDEN] CRL!M{r} must be blank when Media Type='Copper' (got '{cqty_s}')")
                    if ne_conn in FIBER_CONNECTORS or fe_conn in FIBER_CONNECTORS:
                        errors.append(f"[MEDIA_CONNECTOR_MISMATCH] CRL row {r}: Copper run cannot use fiber connector ({ne_conn}/{fe_conn})")
                elif media == "Fiber":
                    if ctype not in FIBER_CABLE_TYPES:
                        errors.append(f"[MEDIA_CABLE_MISMATCH] CRL row {r}: Fiber incompatible with Cable Type '{ctype}'")
                    cqty_n = _coerce_number(cqty_s)
                    if not isinstance(cqty_n, int) or cqty_n <= 0:
                        errors.append(f"[MISSING_FIBER_COUNT] CRL!M{r} requires positive integer Cable Qty / strand count for Fiber")
                    elif cqty_n == 1 and ("duplex" in comments.lower() or "lc" in (ne_conn + fe_conn).lower()):
                        errors.append(f"[STRAND_DUPLEX_MISMATCH] CRL row {r}: Duplex/LC fiber run cannot have Cable Qty=1 (expected >= 2)")
                    if ne_conn in COPPER_CONNECTORS or fe_conn in COPPER_CONNECTORS:
                        errors.append(f"[MEDIA_CONNECTOR_MISMATCH] CRL row {r}: Fiber run cannot use copper connector ({ne_conn}/{fe_conn})")

                if len_v is None or len_v <= 0:
                    errors.append(f"[INVALID_LENGTH_FT] CRL!N{r} Length (ft) '{row_d['N']}' must be > 0")
                if spec_req and spec_req not in SPECIAL_REQUIREMENTS:
                    errors.append(f"[INVALID_SPECIAL_REQ] CRL!O{r} '{spec_req}' not in {sorted(SPECIAL_REQUIREMENTS)}")
                c_low = comments.lower()
                if ("ofnr" in c_low or "riser" in c_low) and ("ofnp" in c_low or "plenum" in c_low):
                    errors.append(f"[FIRE_RATING_CONTRADICTION] CRL!P{r} Comments mixes Riser (OFNR) and Plenum (OFNP): '{comments}'")

                ep = (row_d["C"], row_d["D"], row_d["E"], row_d["G"], row_d["H"], row_d["I"])
                if all(ep):
                    if ep in seen_endpoints:
                        errors.append(
                            f"[DUPLICATE_CRL_ENDPOINT] CRL row {r} duplicates physical NE/FE port 6-tuple {ep} "
                            f"from row {seen_endpoints[ep]} (CRL-DATA-003)"
                        )
                    else:
                        seen_endpoints[ep] = r

    # 4. Raw cell overrides (still subject to identical strict locks!)
    raw_cells = manifest.get("cells") or []
    if raw_cells:
        if not isinstance(raw_cells, list):
            errors.append("[INVALID_MANIFEST] 'cells' must be a list of {sheet, cell, value} objects")
        else:
            for item in raw_cells:
                if not isinstance(item, dict) or not {"sheet", "cell", "value"} <= set(item.keys()):
                    errors.append("[INVALID_MANIFEST] Each 'cells' item requires 'sheet', 'cell', and 'value'")
                    continue
                sh = str(item["sheet"])
                coord = str(item["cell"]).strip().upper()
                val = item["value"]
                col, r_num = _parse_cell_ref(coord)
                if not col:
                    errors.append(f"[INVALID_CELL_REF] Bad cell coordinate '{coord}'")
                    continue
                if sh in ("Materials Master", "Fiber Assemblies", "Cable Harness", "Lists", "Reference Lists"):
                    errors.append(f"[WRITE_LOCK_VIOLATION] Direct edits to controlled catalog/reference tab '{sh}' are blocked")
                    continue
                if sh == "Project BOM":
                    if col not in BOM_ALLOWED_COLS or not (8 <= r_num <= 155):
                        errors.append(
                            f"[BOM_COLUMN_LOCK] Refusing direct write to Project BOM!{coord} "
                            "(only B/C/J in rows 8..155 are editable)"
                        )
                        continue
                elif sh == "Cable Running List":
                    if not (3 <= r_num <= 1087) or _col_to_idx(col) > 16:
                        errors.append(
                            f"[CRL_BOUNDARY_LOCK] Refusing direct write to Cable Running List!{coord} "
                            "(only A..P in rows 3..1087 are editable)"
                        )
                        continue
                elif sh == "Cover Sheet":
                    allowed_cov_coords = set(cov_field_map.values())
                    if coord not in allowed_cov_coords:
                        errors.append(
                            f"[COVER_BOUNDARY_LOCK] Refusing write to Cover Sheet!{coord} "
                            f"(allowed metadata cells: {sorted(allowed_cov_coords)})"
                        )
                        continue
                else:
                    errors.append(f"[WRITE_LOCK_VIOLATION] Direct write to worksheet '{sh}' is not permitted")
                    continue

                if val is None or str(val).strip() == "":
                    queue_cell(sh, coord, "", "clear")
                else:
                    num_v = _coerce_number(val)
                    if num_v is not None and isinstance(val, (int, float)):
                        queue_cell(sh, coord, num_v, "num")
                    else:
                        queue_cell(sh, coord, str(val).strip(), "str")

    return planned_cells, errors, warnings, cov_coords, cat_index


def _set_cell_xml_value(c_el, value, kind, sst, preserve_formula=False):
    """Updates an OpenXML <c> element in place while keeping its template style 's' attribute."""
    main_ns = NS["main"]
    f_el = c_el.find(f"{{{main_ns}}}f")
    v_el = c_el.find(f"{{{main_ns}}}v")
    is_el = c_el.find(f"{{{main_ns}}}is")

    if f_el is not None and not preserve_formula:
        raise RuntimeError(f"Formula overwrite safeguard triggered on {c_el.attrib.get('r')}")

    if preserve_formula and f_el is not None:
        if v_el is None:
            v_el = ET.SubElement(c_el, f"{{{main_ns}}}v")
        if kind == "clear":
            c_el.attrib["t"] = "str"
            v_el.text = ""
        elif kind == "num":
            c_el.attrib.pop("t", None)
            v_el.text = str(value)
        else:
            c_el.attrib["t"] = "str"
            v_el.text = str(value)
        return

    if is_el is not None:
        c_el.remove(is_el)

    if kind == "clear":
        c_el.attrib.pop("t", None)
        if v_el is not None:
            c_el.remove(v_el)
        return

    if v_el is None:
        v_el = ET.SubElement(c_el, f"{{{main_ns}}}v")

    if kind == "num":
        c_el.attrib.pop("t", None)
        v_el.text = str(value)
    else:
        c_el.attrib["t"] = "s"
        v_el.text = str(sst.get_or_add(str(value)))


def _update_sheetdata_xml(orig_sheet_bytes, cell_updates, sst, formula_updates=None):
    """Mutates ONLY <sheetData> inside orig_sheet_bytes so namespaces, styles, and <extLst> remain untouched."""
    main_ns = NS["main"]
    ET.register_namespace("", main_ns)
    raw_txt = orig_sheet_bytes.decode("utf-8")
    m_ws = re.search(r"<worksheet\b([^>]*)>", raw_txt)
    extra_ns_attrs = []
    if m_ws:
        for pfx, uri in re.findall(r'xmlns:([A-Za-z0-9_.-]+)="([^"]+)"', m_ws.group(1)):
            ET.register_namespace(pfx, uri)
            extra_ns_attrs.append(f'xmlns:{pfx}="{uri}"')
    ns_decl = f'xmlns="{main_ns}"' + ((" " + " ".join(extra_ns_attrs)) if extra_ns_attrs else "")

    m_sd = re.search(r"<sheetData\b[^>]*>.*?</sheetData>|<sheetData\b[^>]*/>", raw_txt, re.DOTALL)
    if not m_sd:
        raise ValueError("Worksheet XML missing <sheetData> block")

    sd_body = re.sub(r"^<sheetData\b[^>]*>|</sheetData>$", "", m_sd.group(0).strip())
    if m_sd.group(0).strip().endswith("/>"):
        sd_el = ET.Element(f"{{{main_ns}}}sheetData")
    else:
        sd_fragment = f"<sheetData {ns_decl}>" + sd_body + "</sheetData>"
        sd_el = ET.fromstring(sd_fragment.encode("utf-8"))

    rows_by_num = {}
    for row_el in sd_el.findall(f"{{{main_ns}}}row"):
        r_str = row_el.attrib.get("r", "")
        if r_str.isdigit():
            rows_by_num[int(r_str)] = row_el

    all_updates = []
    for coord, (val, kind) in (cell_updates or {}).items():
        all_updates.append((coord, val, kind, False))
    for coord, (val, kind) in (formula_updates or {}).items():
        all_updates.append((coord, val, kind, True))

    for coord, val, kind, is_formula in all_updates:
        col, r_num = _parse_cell_ref(coord)
        row_el = rows_by_num.get(r_num)
        if row_el is None:
            row_el = ET.SubElement(sd_el, f"{{{main_ns}}}row", {"r": str(r_num)})
            rows_by_num[r_num] = row_el
        c_el = next((c for c in row_el.findall(f"{{{main_ns}}}c") if c.attrib.get("r") == coord), None)
        if c_el is None:
            c_el = ET.SubElement(row_el, f"{{{main_ns}}}c", {"r": coord})
        _set_cell_xml_value(c_el, val, kind, sst, preserve_formula=is_formula)

    _sort_sheetdata_rows_and_cells(sd_el)
    new_sd_raw = ET.tostring(sd_el, encoding="utf-8", xml_declaration=False).decode("utf-8")
    new_sd_raw = re.sub(r'^<sheetData\b[^>]*>', "<sheetData>", new_sd_raw, count=1)
    updated_txt = raw_txt[: m_sd.start()] + new_sd_raw + raw_txt[m_sd.end() :]
    return updated_txt.encode("utf-8")


def _compute_cached_formula_updates(wb_info, role, planned_cells, cov_coords, cat_index):
    """Computes synchronized cached <v> updates for Cover Sheet Revision History and Project BOM formulas."""
    formula_updates = {}
    cov_plan = planned_cells.get("Cover Sheet", {})
    cov_rows = wb_info["sheets"].get("Cover Sheet", {})
    ir = cov_coords["issue_r"]
    hr = cov_coords["hist_r"]

    def eff_cover(col, row_num):
        coord = f"{col}{row_num}"
        if coord in cov_plan:
            v, k = cov_plan[coord]
            return "" if k == "clear" else v
        return cell_val(cov_rows, row_num, col)

    eff_rev = eff_cover("H", ir)
    eff_date = eff_cover("D", ir)
    if f"H{ir}" in cov_plan:
        formula_updates.setdefault("Cover Sheet", {})[f"B{hr}"] = (
            ("", "clear") if eff_rev == "" else (str(eff_rev), "str")
        )
    if f"D{ir}" in cov_plan:
        formula_updates.setdefault("Cover Sheet", {})[f"C{hr}"] = (
            ("", "clear") if eff_date == "" else (eff_date, "num" if _coerce_number(eff_date) is not None else "str")
        )

    if role == "BOM" and "Project BOM" in wb_info["sheets"]:
        pb_rows = wb_info["sheets"]["Project BOM"]
        pb_plan = planned_cells.get("Project BOM", {})
        if not cat_index:
            cat_index, _ = _build_catalog_index(wb_info)

        # Banner cells linked from Cover Sheet
        proj_num_r = cov_coords.get("proj_num_r") or 12
        eff_pnum = eff_cover("D", proj_num_r)
        eff_bldg = eff_cover("D", 18)
        pb_f = formula_updates.setdefault("Project BOM", {})
        if f"D{proj_num_r}" in cov_plan:
            pb_f["B2"] = ("", "clear") if eff_pnum == "" else (str(eff_pnum), "str")
        if "D18" in cov_plan:
            pb_f["E2"] = ("", "clear") if eff_bldg == "" else (str(eff_bldg), "str")
        if f"H{ir}" in cov_plan:
            pb_f["H2"] = ("", "clear") if eff_rev == "" else (str(eff_rev), "str")

        # Update A, D..I cached values for edited BOM rows and recompute E4/G4/G5 totals
        for coord in sorted(pb_plan.keys()):
            col, r_num = _parse_cell_ref(coord)
            if col == "B":
                val, kind = pb_plan[coord]
                pn = "" if kind == "clear" else str(val).strip()
                if not pn:
                    for lc in ("A", "D", "E", "F", "G", "H", "I"):
                        pb_f[f"{lc}{r_num}"] = ("", "clear")
                else:
                    rec = cat_index[pn]
                    pb_f[f"A{r_num}"] = (r_num - 7, "num")
                    pb_f[f"D{r_num}"] = (rec["category"], "str")
                    pb_f[f"E{r_num}"] = (rec["manufacturer"], "str")
                    pb_f[f"F{r_num}"] = (rec["mfg_pn"], "str")
                    pb_f[f"G{r_num}"] = (rec["uom"], "str")
                    pb_f[f"H{r_num}"] = (rec["description"], "str")
                    pb_f[f"I{r_num}"] = (rec["status"], "str")

        # Recompute summary cached values E4 (count), G4 (FT), G5 (EA/KT/BX)
        line_cnt = 0
        ft_sum = 0.0
        unit_sum = 0.0
        for r in range(8, 156):
            if f"B{r}" in pb_plan:
                bv, bk = pb_plan[f"B{r}"]
                pn = "" if bk == "clear" else str(bv).strip()
            else:
                pn = cell_val(pb_rows, r, "B").strip()
            if pn:
                line_cnt += 1
                if f"C{r}" in pb_plan:
                    cv, ck = pb_plan[f"C{r}"]
                    qty = 0.0 if ck == "clear" else (_coerce_number(cv) or 0.0)
                else:
                    qty = _coerce_number(cell_val(pb_rows, r, "C")) or 0.0
                uom = cat_index[pn]["uom"] if pn in cat_index else cell_val(pb_rows, r, "G").strip()
                if uom == "FT":
                    ft_sum += qty
                elif uom in ("EA", "KT", "BX"):
                    unit_sum += qty

        pb_f["E4"] = (line_cnt, "num")
        pb_f["G4"] = (int(ft_sum) if ft_sum == int(ft_sum) else ft_sum, "num")
        pb_f["G5"] = (int(unit_sum) if unit_sum == int(unit_sum) else unit_sum, "num")

    return formula_updates


def apply_workbook_edits(orig_path, manifest, out_path, dry_run=False, allow_pending=False, verify=True):
    """Validates and applies controlled edits to orig_path, writing cleanly to out_path and verifying."""
    if not os.path.exists(orig_path):
        raise FileNotFoundError(f"Workbook not found: {orig_path}")
    wb_info = parse_xlsx(orig_path)
    role = classify_workbook_role(wb_info)
    if role not in ("BOM", "CRL", "COVER"):
        raise ValueError(f"[UNSUPPORTED_ROLE] edit_nea_workbooks.py supports BOM, CRL, and COVER workbooks (got '{role}')")

    planned_cells, errors, warnings, cov_coords, cat_index = _plan_and_validate_edits(
        wb_info, role, manifest, allow_pending=allow_pending
    )
    if errors:
        return {
            "status": "FAIL",
            "role": role,
            "errors": errors,
            "warnings": warnings,
            "planned_cells": planned_cells,
        }

    if dry_run:
        return {
            "status": "DRY_RUN_PASS",
            "role": role,
            "errors": [],
            "warnings": warnings,
            "planned_cells": planned_cells,
        }

    formula_updates = _compute_cached_formula_updates(wb_info, role, planned_cells, cov_coords, cat_index)
    target_sheets = sorted(set(planned_cells.keys()) | set(formula_updates.keys()))

    with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as tf:
        tmp_out = tf.name

    try:
        with zipfile.ZipFile(orig_path, "r") as z_in:
            wb_bytes = z_in.read("xl/workbook.xml")
            wb_xml = ET.fromstring(wb_bytes)
            rels_xml = ET.fromstring(z_in.read("xl/_rels/workbook.xml.rels"))
            rel_map = {
                r.attrib["Id"]: (
                    r.attrib["Target"] if r.attrib["Target"].startswith("xl/") else "xl/" + r.attrib["Target"].lstrip("/")
                )
                for r in rels_xml
            }
            sheet_target_by_name = {
                s.attrib["name"]: rel_map.get(s.attrib[f"{{{NS['r']}}}id"], "")
                for s in wb_xml.findall(".//main:sheet", NS)
            }

            if "xl/sharedStrings.xml" not in z_in.namelist():
                raise ValueError("[MISSING_OPENXML_PART] Template missing xl/sharedStrings.xml")
            sst = SharedStringTable(z_in.read("xl/sharedStrings.xml"))

            modified_entries = {}
            for sname in target_sheets:
                sp = sheet_target_by_name.get(sname)
                if not sp or sp not in z_in.namelist():
                    raise ValueError(f"[MISSING_SHEET_PART] Cannot locate XML target for sheet '{sname}'")
                modified_entries[sp] = _update_sheetdata_xml(
                    z_in.read(sp),
                    planned_cells.get(sname),
                    sst,
                    formula_updates=formula_updates.get(sname),
                )

            modified_entries["xl/sharedStrings.xml"] = sst.to_xml_bytes()

            # Ensure fullCalcOnLoad="1" and drop stale calcChain.xml cleanly so Desktop Excel recalculates
            wb_txt = wb_bytes.decode("utf-8")
            if "<calcPr" in wb_txt and 'fullCalcOnLoad="1"' not in wb_txt:
                wb_txt = re.sub(r"<calcPr\b", '<calcPr fullCalcOnLoad="1"', wb_txt, count=1)
                modified_entries["xl/workbook.xml"] = wb_txt.encode("utf-8")
            if "[Content_Types].xml" in z_in.namelist() and "xl/calcChain.xml" in z_in.namelist():
                ct_txt = z_in.read("[Content_Types].xml").decode("utf-8")
                ct_txt_new = re.sub(
                    r'<Override[^>]*PartName="/xl/calcChain\.xml"[^>]*/>\s*', "", ct_txt
                )
                if ct_txt_new != ct_txt:
                    modified_entries["[Content_Types].xml"] = ct_txt_new.encode("utf-8")

            with zipfile.ZipFile(tmp_out, "w", compression=zipfile.ZIP_DEFLATED) as z_out:
                for info in z_in.infolist():
                    if info.filename == "xl/calcChain.xml":
                        continue
                    data = modified_entries.get(info.filename, z_in.read(info.filename))
                    z_out.writestr(info.filename, data)

        os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
        shutil.move(tmp_out, out_path)
        preserve_openxml_extensions(orig_path, out_path)
    finally:
        if os.path.exists(tmp_out):
            os.remove(tmp_out)

    if verify:
        run_verify_write(orig_path, out_path)

    return {
        "status": "PASS",
        "role": role,
        "errors": [],
        "warnings": warnings,
        "planned_cells": planned_cells,
        "out_path": out_path,
    }


def _print_schema():
    schema = {
        "cover_sheet": {
            "project_name": "str",
            "project_number": "str",
            "customer": "str",
            "customer_contact": "str",
            "building": "str (BOM Cover Sheet)",
            "site_address": "str (CRL / Standalone Cover Sheet)",
            "project_manager": "str",
            "designer": "str",
            "installation_contractor": "str (CRL / Standalone ONLY; blocked on BOM per GOV-006)",
            "issue_date": "YYYY-MM-DD",
            "revision": "str",
            "document_status": sorted(DOCUMENT_STATUS_VALUES),
        },
        "bom_rows": [
            {
                "row": "int 8..155",
                "mb_pn": "str (verified in tblMaterials / Fiber Assemblies / Cable Harness)",
                "qty": "number > 0",
                "notes": "optional str",
                "expected_uom": "optional str cross-check",
                "clear": "optional bool (clears Cols B, C, J while keeping Cols A & D:I formulas)",
            }
        ],
        "crl_rows": [
            {
                "row": "int 3..1087",
                "run_id": "unique positive int",
                "classification": "str",
                "ne_location": "str", "ne_rack": "str", "ne_port": "str", "ne_connector": "str",
                "fe_location": "str", "fe_rack": "str", "fe_port": "str", "fe_connector": "str",
                "media_type": "Copper | Fiber",
                "cable_type": "Cat5e..Cat8/Bulk Pair | OM1..OM5/OS2",
                "cable_qty": "int > 0 for Fiber; blank/None for Copper",
                "length_ft": "number > 0",
                "special_requirement": sorted(SPECIAL_REQUIREMENTS),
                "comments": "str",
                "clear": "optional bool",
            }
        ],
    }
    print(json.dumps(schema, indent=2))


def main():
    parser = argparse.ArgumentParser(
        description="NEA v2.2.3 Controlled Safe-Write Helper (OpenXML-safe JSON manifest editor)"
    )
    parser.add_argument("orig_xlsx", nargs="?", help="Path to unmodified baseline .xlsx workbook")
    parser.add_argument("--manifest", help="Path to JSON edit manifest")
    parser.add_argument("--out", help="Output .xlsx path (must differ from orig_xlsx to preserve baseline)")
    parser.add_argument("--dry-run", action="store_true", help="Validate locks, catalog keys, and CRL rules without writing")
    parser.add_argument("--allow-pending", action="store_true", help="Allow Pending / Limited Use catalog parts in Project BOM")
    parser.add_argument("--schema", action="store_true", help="Print supported JSON manifest schema and exit")
    args = parser.parse_args()

    if args.schema:
        _print_schema()
        return 0
    if not args.orig_xlsx or not args.manifest:
        parser.error("orig_xlsx and --manifest are required unless --schema is set")
    if not args.dry_run and not args.out:
        parser.error("--out <edited.xlsx> is required when not running with --dry-run")
    if args.out and os.path.abspath(args.orig_xlsx) == os.path.abspath(args.out):
        print("ERROR: --out must be a separate path from orig_xlsx so baseline verification remains intact.", file=sys.stderr)
        return 2

    with open(args.manifest, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    res = apply_workbook_edits(
        args.orig_xlsx,
        manifest,
        args.out or args.orig_xlsx,
        dry_run=args.dry_run,
        allow_pending=args.allow_pending,
        verify=not args.dry_run,
    )
    for w in res["warnings"]:
        print(f"WARNING: {w}")
    if res["status"] == "FAIL":
        print("\n[EDIT BLOCKED — PRE-WRITE VALIDATION FAILED]:")
        for e in res["errors"]:
            print(f"  - {e}")
        return 1
    if args.dry_run:
        total_cells = sum(len(v) for v in res["planned_cells"].values())
        print(f"[DRY-RUN: PASS] Role={res['role']} | Validated Target Cells={total_cells} | Warnings={len(res['warnings'])}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
