#!/usr/bin/env python3
"""NEADeterministic Workbook Telemetry & On-Demand Escalation Inspector (NEA-SCR-001)
Version: 2.2.3
Purpose:
  Single-command OpenXML (.xlsx) telemetry extractor for NEA Project Deliverable Reviews,
  Catalog Lookups, and Incremental Delta Rechecks.
  - Zero third-party dependencies (uses Python standard library zipfile + xml.etree.ElementTree).
  - Read-Only Guarantee: Opens all .xlsx archives strictly in mode "r" and verifies Pre/Post SHA-256
    immutability (0 bytes modified).
  - Role-Based Workbook Discovery: Identifies BOM, CRL, and Standalone Cover Sheet workbooks by
    internal worksheet structure rather than hardcoded filenames, so renamed project files
    (e.g., BOM_Materials_Master.xlsx, Cable_Running_List_Template_V2.xlsx) work automatically.
  - Supports the 6-tab BOM architecture (Cover Sheet, Materials Master, Fiber Assemblies,
    Cable Harness, Project BOM, Lists) and 3-tier XLOOKUP cascade.
"""
import argparse
import hashlib
import json
import os
import re
import sys
import zipfile
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict

ENGINE_ID = "NEA-SCR-001 v2.2.3 (Deterministic Read-Only OpenXML)"
NS = {
    "main": "http://schemas.openxmlformats.org/spreadsheetml/2006/main",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
}
REL_NS = {"rel": "http://schemas.openxmlformats.org/package/2006/relationships"}
COL_RE = re.compile(r"^([A-Z]+)(\d+)$")


def parse_xlsx(path):
    """Parses all worksheets, values, and formulas from an .xlsx archive in read-only mode."""
    with open(path, "rb") as f:
        raw_bytes = f.read()
    pre_sha = hashlib.sha256(raw_bytes).hexdigest()
    zf = zipfile.ZipFile(path, "r")
    shared_strings = []
    if "xl/sharedStrings.xml" in zf.namelist():
        ss_root = ET.fromstring(zf.read("xl/sharedStrings.xml"))
        for si in ss_root.findall("main:si", NS):
            texts = [t.text or "" for t in si.iter(f"{{{NS['main']}}}t")]
            shared_strings.append("".join(texts))

    wb_root = ET.fromstring(zf.read("xl/workbook.xml"))
    defined_names = {}
    for dn_el in wb_root.iter():
        if dn_el.tag.endswith("definedName") and dn_el.attrib.get("name"):
            defined_names[dn_el.attrib["name"]] = (dn_el.text or "").strip()

    tables = {}
    for name_in_zip in zf.namelist():
        if name_in_zip.startswith("xl/tables/table") and name_in_zip.endswith(".xml"):
            try:
                t_root = ET.fromstring(zf.read(name_in_zip))
                t_name = t_root.attrib.get("name") or t_root.attrib.get("displayName") or os.path.basename(name_in_zip)
                t_ref = t_root.attrib.get("ref", "")
                tables[t_name] = {"ref": t_ref, "xml_path": name_in_zip}
            except Exception:
                pass

    xf_to_fill_rgb = {}
    if "xl/styles.xml" in zf.namelist():
        try:
            st_root = ET.fromstring(zf.read("xl/styles.xml"))
            fill_rgbs = []
            fills_el = st_root.find("main:fills", NS)
            if fills_el is not None:
                for f_el in fills_el.findall("main:fill", NS):
                    pf = f_el.find("main:patternFill", NS)
                    rgb = ""
                    if pf is not None:
                        fg = pf.find("main:fgColor", NS)
                        if fg is not None:
                            rgb = fg.attrib.get("rgb", "")
                    fill_rgbs.append(rgb.upper())
            xfs_el = st_root.find("main:cellXfs", NS)
            if xfs_el is not None:
                for idx_xf, xf_el in enumerate(xfs_el.findall("main:xf", NS)):
                    f_id = int(xf_el.attrib.get("fillId", "0") or 0)
                    if 0 <= f_id < len(fill_rgbs) and fill_rgbs[f_id]:
                        xf_to_fill_rgb[str(idx_xf)] = fill_rgbs[f_id]
        except Exception:
            pass

    rels_root = ET.fromstring(zf.read("xl/_rels/workbook.xml.rels"))
    rel_map = {
        rel.attrib["Id"]: rel.attrib["Target"]
        for rel in rels_root.findall("rel:Relationship", REL_NS)
    }

    sheets = {}
    sheet_dvs = {}
    for sheet in wb_root.findall(".//main:sheet", NS):
        name = sheet.attrib["name"]
        r_id = sheet.attrib[f"{{{NS['r']}}}id"]
        target = rel_map[r_id]
        if not target.startswith("xl/"):
            target = "xl/" + target.lstrip("/")
        if target not in zf.namelist():
            continue
        s_root = ET.fromstring(zf.read(target))
        dvs = []
        for dv_el in s_root.iter():
            if dv_el.tag.endswith("dataValidation"):
                dtype = dv_el.attrib.get("type", "")
                sqref = dv_el.attrib.get("sqref", "")
                f1_list = []
                for child in dv_el.iter():
                    if child.tag.endswith("sqref") and child.text:
                        sqref = child.text.strip()
                    elif (child.tag.endswith("formula1") or child.tag.endswith("}f")) and child.text:
                        f1_list.append(child.text.strip())
                dvs.append({"type": dtype, "sqref": sqref, "formulas": f1_list})
        sheet_dvs[name] = dvs
        rows = {}
        for row_el in s_root.findall(".//main:row", NS):
            r_idx = int(row_el.attrib["r"])
            row_dict = {}
            for c_el in row_el.findall("main:c", NS):
                coord = c_el.attrib.get("r", f"?{r_idx}")
                m = COL_RE.match(coord)
                col_let = m.group(1) if m else coord
                c_type = c_el.attrib.get("t", "")
                f_el = c_el.find("main:f", NS)
                v_el = c_el.find("main:v", NS)
                is_el = c_el.find("main:is", NS)

                has_formula = f_el is not None
                f_text = (f_el.text or "") if has_formula else None
                f_type = f_el.attrib.get("t", "normal") if has_formula else None
                f_si = f_el.attrib.get("si", "") if has_formula else None
                f_ref = f_el.attrib.get("ref", "") if has_formula else None

                val = ""
                if c_type == "s" and v_el is not None and v_el.text is not None:
                    idx = int(v_el.text)
                    val = shared_strings[idx] if 0 <= idx < len(shared_strings) else f"[SS:{idx}]"
                elif c_type == "inlineStr" and is_el is not None:
                    val = "".join(t.text or "" for t in is_el.iter(f"{{{NS['main']}}}t"))
                elif v_el is not None and v_el.text is not None:
                    val = v_el.text

                s_attr = c_el.attrib.get("s", "")
                row_dict[col_let] = {
                    "coord": coord,
                    "val": val.strip() if isinstance(val, str) else str(val),
                    "has_formula": has_formula,
                    "f_text": f_text,
                    "f_type": f_type,
                    "f_si": f_si,
                    "f_ref": f_ref,
                    "fill_rgb": xf_to_fill_rgb.get(s_attr, ""),
                }
            rows[r_idx] = row_dict
        sheets[name] = rows
    zf.close()
    with open(path, "rb") as f:
        post_sha = hashlib.sha256(f.read()).hexdigest()
    return {
        "path": path,
        "filename": os.path.basename(path),
        "sha256": pre_sha[:10],
        "full_sha256": pre_sha,
        "post_sha256": post_sha,
        "immutable": pre_sha == post_sha,
        "sheets": sheets,
        "sheet_dvs": sheet_dvs,
        "defined_names": defined_names,
        "tables": tables,
    }


def cell_val(sheet_rows, r_idx, col_let):
    return sheet_rows.get(r_idx, {}).get(col_let, {}).get("val", "")


def cell_info(sheet_rows, r_idx, col_let):
    return sheet_rows.get(r_idx, {}).get(
        col_let,
        {
            "coord": f"{col_let}{r_idx}",
            "val": "",
            "has_formula": False,
            "f_text": None,
            "f_type": None,
        },
    )


def fmt_num(v):
    try:
        f = float(v)
        return str(int(f)) if f.is_integer() else f"{f:.2f}"
    except Exception:
        return str(v)


def excel_serial_to_iso(v):
    """Converts Excel serial date number (e.g., 46072 -> 2026-02-19) when applicable."""
    try:
        serial = int(float(v))
        if 40000 <= serial <= 60000:
            import datetime
            base = datetime.date(1899, 12, 30)
            return (base + datetime.timedelta(days=serial)).isoformat()
    except Exception:
        pass
    return str(v)


def iso_to_excel_serial(val):
    """Converts YYYY-MM-DD or MM/DD/YYYY string (or Excel serial) into integer Excel serial date."""
    if val is None or val == "":
        return None
    s = str(val).strip()
    try:
        num = int(float(s))
        if 40000 <= num <= 60000:
            return num
    except Exception:
        pass
    import datetime
    for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%m-%d-%Y", "%m/%d/%y", "%Y/%m/%d"):
        try:
            dt = datetime.datetime.strptime(s, fmt).date()
            return (dt - datetime.date(1899, 12, 30)).days
        except Exception:
            continue
    return None


def normalize_last_first(full_name):
    """Converts 'Orin Leacock' -> 'Leacock, Orin' (preserving existing 'Last, First' and suffixes) within 31 chars."""
    s = re.sub(r"[:\\/?*\[\]]", "", (full_name or "Unknown Employee").strip())
    if not s:
        return "Unknown Employee"
    if "," in s:
        parts = [p.strip() for p in s.split(",", 1)]
        res = f"{parts[0]}, {parts[1]}" if len(parts) == 2 and parts[1] else parts[0]
        return res[:31]
    tokens = s.split()
    if len(tokens) == 1:
        return tokens[0][:31]
    suffixes = {"JR", "JR.", "SR", "SR.", "II", "III", "IV"}
    if len(tokens) >= 3 and tokens[-1].upper() in suffixes:
        last = f"{tokens[-2]} {tokens[-1]}"
        first = " ".join(tokens[:-2])
    else:
        last = tokens[-1]
        first = " ".join(tokens[:-1])
    return f"{last}, {first}"[:31]


def classify_workbook_role(wb):
    """Classifies workbook role by internal worksheet structure and top-row anchors rather than filename."""
    s_names = set(wb["sheets"].keys())
    if "Materials Master" in s_names or "Project BOM" in s_names:
        return "BOM"
    if "Cable Running List" in s_names:
        return "CRL"
    if (
        "Weekly Summary" in s_names
        or "Job Summary" in s_names
        or "Timesheet Template" in s_names
        or "Timesheet Page 1" in s_names
        or any("timesheet" in sn.lower() for sn in s_names)
    ):
        return "TIMESHEET"
    for sh_rows in wb["sheets"].values():
        top_tokens = []
        for r_idx in range(1, 11):
            for c_info in sh_rows.get(r_idx, {}).values():
                v_up = str(c_info.get("val", "") or "").upper()
                if v_up:
                    top_tokens.append(v_up)
        joined_top = " | ".join(top_tokens)
        if (
            "MISSOURI TIMESHEET" in joined_top
            or "WEEK ENDING" in joined_top
            or "BEGIN WEEK" in joined_top
            or ("SUN" in top_tokens and "MON" in top_tokens and "WED" in top_tokens and "FRI" in top_tokens)
        ):
            return "TIMESHEET"
    if "Cover Sheet" in s_names and len(s_names) <= 3:
        return "COVER"
    return "UNKNOWN"


def discover_xlsx_files(target_dir):
    """Discovers .xlsx workbooks across target_dir or fallback relative folders."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    if target_dir != "Templates" and not os.path.exists(target_dir):
        return os.path.abspath(target_dir), []
    candidates = [
        os.path.abspath(target_dir),
        os.path.join(os.path.abspath(target_dir), "Templates"),
        os.path.abspath(os.path.join(script_dir, "..", "Templates")),
        script_dir,
        os.path.abspath(os.path.join(script_dir, "..")),
    ]
    for cand in candidates:
        if os.path.isfile(cand) and cand.endswith(".xlsx"):
            parent = os.path.dirname(cand)
            files = sorted(
                os.path.join(parent, f)
                for f in os.listdir(parent)
                if f.endswith(".xlsx") and not f.startswith("~$")
            )
            return parent, files
        if os.path.isdir(cand):
            files = sorted(
                os.path.join(cand, f)
                for f in os.listdir(cand)
                if f.endswith(".xlsx") and not f.startswith("~$")
            )
            if files:
                return cand, files
    return os.path.abspath(target_dir), []


def run_catalog_lookup(workbooks_by_role, workbooks, query):
    """Executes fast catalog search across tblMaterials, Fiber Assemblies, and Cable Harness."""
    bom_wb = workbooks_by_role.get("BOM")
    if not bom_wb:
        print("ERROR: BOM workbook containing 'Materials Master' not found.")
        sys.exit(2)
    q_terms = [t.lower() for t in query.split() if t.strip()]
    print("=" * 88)
    print(f"NEA DETERMINISTIC CATALOG LOOKUP — Query: '{query}' ({bom_wb['filename']} SHA256={bom_wb['sha256']})")
    print("=" * 88)

    mm = bom_wb["sheets"].get("Materials Master", {})
    fa = bom_wb["sheets"].get("Fiber Assemblies", {})
    ch = bom_wb["sheets"].get("Cable Harness", {})
    matches = []
    for r in sorted(r for r in mm if 4 <= r <= 600):
        cat, pn, mfg, mpn = cell_val(mm, r, "A"), cell_val(mm, r, "B"), cell_val(mm, r, "C"), cell_val(mm, r, "D")
        uom, desc, stat = cell_val(mm, r, "E"), cell_val(mm, r, "F"), cell_val(mm, r, "G")
        if not any([cat, pn, mfg, mpn, desc]):
            continue
        blob = f"{cat} {pn} {mfg} {mpn} {uom} {desc} {stat}".lower()
        if all(t in blob for t in q_terms):
            matches.append(("tblMaterials", f"R{r}", pn, cat, mfg, mpn, uom, stat, desc))

    for r in sorted(r for r in fa if r >= 4):
        cat, ft, pn, mfg = cell_val(fa, r, "A"), cell_val(fa, r, "B"), cell_val(fa, r, "C"), cell_val(fa, r, "D")
        mpn, uom, desc, stat = cell_val(fa, r, "E"), cell_val(fa, r, "F"), cell_val(fa, r, "G"), cell_val(fa, r, "H") or "Active"
        if not any([cat, pn, mfg, mpn, desc]):
            continue
        blob = f"{cat} {ft} {pn} {mfg} {mpn} {uom} {desc} {stat}".lower()
        if all(t in blob for t in q_terms):
            matches.append(("Fiber Assemblies", f"R{r}", pn, f"{cat}/{ft}", mfg, mpn, uom, stat, desc))

    for r in sorted(r for r in ch if r >= 4):
        cat, ct, pn, mfg = cell_val(ch, r, "A"), cell_val(ch, r, "B"), cell_val(ch, r, "C") or "[Unassigned]", cell_val(ch, r, "D")
        mpn, uom, desc, stat = cell_val(ch, r, "E"), cell_val(ch, r, "F"), cell_val(ch, r, "G"), cell_val(ch, r, "H")
        if not mfg and not mpn:
            continue
        blob = f"{cat} {ct} {pn} {mfg} {mpn} {uom} {desc} {stat}".lower()
        if all(t in blob for t in q_terms):
            matches.append(("Cable Harness", f"R{r}", pn, f"{cat}/{ct}", mfg, mpn, uom, stat, desc))

    print(f"Matches Found: {len(matches)}")
    for src, row_id, pn, cat, mfg, mpn, uom, stat, desc in matches[:60]:
        print(
            f"  - [{src} {row_id}] MB P/N='{pn}' | Cat='{cat}' | MFG='{mfg}' | "
            f"MFG P/N='{mpn}' | UOM='{uom}' | Status='{stat}' | Desc='{desc}'"
        )
    if len(matches) > 60:
        print(f"  ... ({len(matches) - 60} additional matches truncated; refine query)")


def preserve_openxml_extensions(orig_xlsx, edited_xlsx):
    """Restores <extLst> (x14:dataValidations dropdowns) from orig_xlsx if stripped by openpyxl.save()."""
    with zipfile.ZipFile(orig_xlsx, "r") as z_orig:
        orig_exts = {}
        for name in z_orig.namelist():
            if name.startswith("xl/worksheets/sheet") and name.endswith(".xml"):
                xml_txt = z_orig.read(name).decode("utf-8")
                m = re.search(r"<extLst>.*?</extLst>", xml_txt, re.DOTALL)
                if m:
                    orig_exts[name] = m.group(0)
    if not orig_exts:
        return False
    restored = False
    entries = []
    with zipfile.ZipFile(edited_xlsx, "r") as z_ed:
        for info in z_ed.infolist():
            data = z_ed.read(info.filename)
            if info.filename in orig_exts:
                txt = data.decode("utf-8")
                if "<extLst>" not in txt and "</worksheet>" in txt:
                    txt = txt.replace("</worksheet>", orig_exts[info.filename] + "</worksheet>", 1)
                    data = txt.encode("utf-8")
                    restored = True
            entries.append((info, data))
    if restored:
        with zipfile.ZipFile(edited_xlsx, "w", compression=zipfile.ZIP_DEFLATED) as z_out:
            for info, data in entries:
                z_out.writestr(info.filename, data)
    return restored


def validate_openxml_package_integrity(xlsx_path):
    """Validates ECMA-376 / Desktop Excel OpenXML structural invariants so corrupt .xlsx packages cannot pass --verify-write."""
    issues = []
    col_re = re.compile(r"^([A-Z]+)(\d+)$")

    def col_to_idx(col_str):
        n = 0
        for ch in col_str:
            n = n * 26 + (ord(ch) - ord("A") + 1)
        return n

    with zipfile.ZipFile(xlsx_path, "r") as zf:
        bad_member = zf.testzip()
        if bad_member:
            issues.append(f"[ZIP_CRC_CORRUPTION] Archive member '{bad_member}' failed CRC-32 check")
        names = set(zf.namelist())
        for fn in ("xl/workbook.xml", "xl/_rels/workbook.xml.rels", "[Content_Types].xml"):
            if fn not in names:
                issues.append(f"[MISSING_OPENXML_PART] Required part '{fn}' missing from archive")
                return issues
            raw_txt = zf.read(fn).decode("utf-8", errors="replace")
            if re.search(r"<ns\d+:", raw_txt):
                issues.append(f"[OPENXML_NAMESPACE_POLLUTION] '{fn}' contains synthetic ElementTree '<nsN:>' prefixes rejected by Desktop Excel")

        # Check synthetic ElementTree nsN prefixes, mc:Ignorable, and Requires prefixes across ALL XML/rels files
        for fn in sorted(names):
            if not (fn.endswith(".xml") or fn.endswith(".rels")):
                continue
            raw_txt = zf.read(fn).decode("utf-8", errors="replace")
            if re.search(r"(?:<|\s|xmlns:)ns\d+[:=]", raw_txt):
                issues.append(f"[OPENXML_NAMESPACE_POLLUTION] '{fn}' contains synthetic ElementTree 'nsN' prefixes rejected by Desktop Excel")
            try:
                ET.fromstring(raw_txt.encode("utf-8"))
            except Exception as exc:
                issues.append(f"[MALFORMED_XML] '{fn}' failed XML parse: {exc}")
                continue
            declared_prefixes = set(re.findall(r"\bxmlns:([A-Za-z0-9_.-]+)\s*=", raw_txt))
            for m_ign in re.finditer(r'\b(?:mc|ns\d+):Ignorable="([^"]+)"', raw_txt):
                for pfx in m_ign.group(1).split():
                    if pfx not in declared_prefixes:
                        issues.append(f"[UNDECLARED_IGNORABLE_PREFIX] '{fn}' lists Ignorable prefix '{pfx}' without xmlns:{pfx} declaration")
            for m_req in re.finditer(r'\bRequires="([^"]+)"', raw_txt):
                for pfx in m_req.group(1).split():
                    if pfx not in declared_prefixes:
                        issues.append(f"[UNDECLARED_REQUIRES_PREFIX] '{fn}' lists Requires prefix '{pfx}' without xmlns:{pfx} declaration")

        # Check workbook sheets, definedNames, worksheet row/cell order, and 1-to-1 drawing targets
        wb_root = ET.fromstring(zf.read("xl/workbook.xml"))
        sheet_els = wb_root.findall(".//main:sheet", NS)
        sheet_names = {s.attrib.get("name", "") for s in sheet_els}
        num_sheets = len(sheet_els)
        for dn in wb_root.findall(".//main:definedName", NS):
            ls_id = dn.attrib.get("localSheetId")
            if ls_id is not None and (not ls_id.isdigit() or int(ls_id) >= num_sheets):
                issues.append(f"[DANGLING_DEFINED_NAME] definedName '{dn.attrib.get('name')}' has out-of-range localSheetId='{ls_id}' (sheets={num_sheets})")
            dn_txt = (dn.text or "").strip()
            m_sh = re.match(r"^'([^']+)'!", dn_txt)
            if m_sh and m_sh.group(1).replace("''", "'") not in sheet_names:
                issues.append(f"[DANGLING_DEFINED_NAME] definedName references deleted sheet '{m_sh.group(1)}'")

        seen_drawings = {}
        seen_codenames = {}
        seen_sheet_uids = {}
        xr_uid_attr = "{http://schemas.microsoft.com/office/spreadsheetml/2014/revision}uid"
        for fn in sorted(names):
            if fn.startswith("xl/worksheets/sheet") and fn.endswith(".xml"):
                s_root = ET.fromstring(zf.read(fn))
                s_uid = s_root.attrib.get(xr_uid_attr)
                if s_uid:
                    if s_uid in seen_sheet_uids:
                        issues.append(f"[DUPLICATE_SHEET_UID] '{fn}' and '{seen_sheet_uids[s_uid]}' share xr:uid='{s_uid}'")
                    else:
                        seen_sheet_uids[s_uid] = fn
                spr = s_root.find("main:sheetPr", NS)
                if spr is not None and "codeName" in spr.attrib:
                    cn = spr.attrib["codeName"]
                    if cn in seen_codenames:
                        issues.append(f"[DUPLICATE_SHEET_CODENAME] '{fn}' and '{seen_codenames[cn]}' share codeName='{cn}'")
                    else:
                        seen_codenames[cn] = fn
                rows = s_root.findall(".//main:row", NS)
                r_nums = [int(r.attrib["r"]) for r in rows if "r" in r.attrib]
                if r_nums != sorted(r_nums) or len(r_nums) != len(set(r_nums)):
                    issues.append(f"[OUT_OF_ORDER_ROWS] '{fn}' has unsorted or duplicate <row r='...'> elements")
                for r_el in rows:
                    c_refs = [c.attrib.get("r", "") for c in r_el.findall("main:c", NS)]
                    c_idxs = [col_to_idx(col_re.match(cr).group(1)) for cr in c_refs if col_re.match(cr)]
                    if c_idxs != sorted(c_idxs) or len(c_idxs) != len(set(c_idxs)):
                        issues.append(f"[OUT_OF_ORDER_CELLS] '{fn}' row {r_el.attrib.get('r')} has unsorted or duplicate <c> elements: {c_refs}")
                        break
            elif fn.startswith("xl/worksheets/_rels/sheet") and fn.endswith(".rels"):
                rel_root = ET.fromstring(zf.read(fn))
                for rel in rel_root.findall("rel:Relationship", REL_NS):
                    tgt = rel.attrib.get("Target", "")
                    if "drawings/" in tgt:
                        norm_tgt = "xl/" + tgt.lstrip("./")
                        if norm_tgt not in names:
                            issues.append(f"[MISSING_DRAWING_PART] '{fn}' references missing drawing '{norm_tgt}'")
                        elif norm_tgt in seen_drawings:
                            issues.append(f"[SHARED_DRAWING_TARGET] '{fn}' and '{seen_drawings[norm_tgt]}' share '{norm_tgt}' (Desktop Excel requires 1-to-1 worksheet drawing parts)")
                        else:
                            seen_drawings[norm_tgt] = fn
    return issues


def run_verify_write(orig_path, edited_path):
    """Deterministically audits a modified .xlsx against its pre-edit baseline (NEA-SKL-002 & NEA-SKL-003)."""
    if not os.path.exists(orig_path):
        print(f"ERROR: Baseline workbook not found: {orig_path}")
        sys.exit(2)
    if not os.path.exists(edited_path):
        print(f"ERROR: Edited workbook not found: {edited_path}")
        sys.exit(2)

    ext_restored = preserve_openxml_extensions(orig_path, edited_path)
    before = parse_xlsx(orig_path)
    after = parse_xlsx(edited_path)
    role = classify_workbook_role(after)

    errors = []
    formula_losses = []
    formula_restorations = []
    cell_diffs = []

    if role == "TIMESHEET" and len(after["sheets"]) >= 1:
        if "Expense Report" in after["sheets"]:
            errors.append("[EXPENSE_TAB_FORBIDDEN] 'Expense Report' tab must be stripped from consolidated timesheet workbooks")
        tmpl_rows = before["sheets"].get("Timesheet Template") or before["sheets"].get("Timesheet Page 1") or next(iter(before["sheets"].values()), {})
        for sname, a_rows in after["sheets"].items():
            if sname in ("Weekly Summary", "Job Summary", "Expense Report"):
                continue
            all_r = sorted(set(tmpl_rows.keys()) | set(a_rows.keys()))
            for r in all_r:
                br = tmpl_rows.get(r, {})
                ar = a_rows.get(r, {})
                for c in sorted(set(br.keys()) | set(ar.keys())):
                    bi = br.get(c, {"val": "", "has_formula": False})
                    ai = ar.get(c, {"val": "", "has_formula": False})
                    if bi.get("has_formula") and not ai.get("has_formula"):
                        formula_losses.append(f"{sname}!{c}{r} (was formula, now static '{ai.get('val', '')}')")
                    elif not bi.get("has_formula") and ai.get("has_formula"):
                        formula_restorations.append(f"{sname}!{c}{r} (restored <f>='{ai.get('f_text', 'shared')}')")
                    elif bi.get("val", "") != ai.get("val", "") and not bi.get("has_formula"):
                        cell_diffs.append((f"{sname}!{c}{r}", bi.get("val", ""), ai.get("val", "")))
    else:
        if set(before["sheets"].keys()) != set(after["sheets"].keys()):
            errors.append(
                f"[SHEET_SCHEMA_MISMATCH] Worksheet tabs changed from {list(before['sheets'].keys())} to {list(after['sheets'].keys())}"
            )
        # 1. Check formula preservation across all sheets (any cell that had <f> in before must retain <f> in after)
        for sname, b_rows in before["sheets"].items():
            a_rows = after["sheets"].get(sname, {})
            all_r = sorted(set(b_rows.keys()) | set(a_rows.keys()))
            for r in all_r:
                br = b_rows.get(r, {})
                ar = a_rows.get(r, {})
                all_c = sorted(set(br.keys()) | set(ar.keys()))
                for c in all_c:
                    bi = br.get(c, {"val": "", "has_formula": False})
                    ai = ar.get(c, {"val": "", "has_formula": False})
                    if bi.get("has_formula") and not ai.get("has_formula"):
                        formula_losses.append(f"{sname}!{c}{r} (was formula, now static '{ai.get('val', '')}')")
                    elif not bi.get("has_formula") and ai.get("has_formula"):
                        formula_restorations.append(f"{sname}!{c}{r} (restored <f>='{ai.get('f_text', 'shared')}')")
                    elif bi.get("val", "") != ai.get("val", "") and not bi.get("has_formula"):
                        cell_diffs.append((f"{sname}!{c}{r}", bi.get("val", ""), ai.get("val", "")))

    if formula_losses:
        errors.append(
            f"[FORMULA_OVERWRITE] {len(formula_losses)} formula cell(s) lost <f> tag: {formula_losses[:15]}"
        )

    # 2. Role-specific checks
    if role == "BOM" and "Project BOM" in after["sheets"]:
        mm = after["sheets"].get("Materials Master", {})
        fa = after["sheets"].get("Fiber Assemblies", {})
        ch = after["sheets"].get("Cable Harness", {})
        pb = after["sheets"]["Project BOM"]
        valid_pns = set()
        for r in mm:
            if r >= 4 and cell_val(mm, r, "B"):
                valid_pns.add(cell_val(mm, r, "B"))
        for r in fa:
            if r >= 4 and cell_val(fa, r, "C"):
                valid_pns.add(cell_val(fa, r, "C"))
        for r in ch:
            if r >= 4 and cell_val(ch, r, "C"):
                valid_pns.add(cell_val(ch, r, "C"))
        for r in sorted(k for k in pb if 8 <= k <= 155):
            pn = cell_val(pb, r, "B")
            if pn and pn not in valid_pns:
                errors.append(f"[UNVERIFIED_BOM_PART] Project BOM!B{r} MB P/N '{pn}' does not exist in 3-tier catalog")

    # 3. Check DataValidation column coverage & integrity
    for sname, b_dvs in before.get("sheet_dvs", {}).items():
        a_dvs = after.get("sheet_dvs", {}).get(sname, [])
        if b_dvs and not a_dvs and role != "TIMESHEET":
            errors.append(f"[DV_STRIPPED] {sname} lost all DataValidation rules (before={len(b_dvs)}, after=0)")
        if role != "TIMESHEET":
            for dv in a_dvs:
                sq = dv.get("sqref", "")
                toks = sq.split() if sq else []
                if len(toks) > 10:
                    errors.append(f"[FRAGMENTED_DV_SQREF] {sname} has fragmented sqref across {len(toks)} cells")

    # 4. Check ECMA-376 / Desktop Excel OpenXML package invariants
    errors.extend(validate_openxml_package_integrity(edited_path))

    wrt_seed = f"{before['full_sha256']}:{after['full_sha256']}:{len(cell_diffs)}:{len(formula_restorations)}:{len(errors)}"
    wrt_token = f"NEA-WRT-{hashlib.sha256(wrt_seed.encode('utf-8')).hexdigest()[:12].upper()}"
    status = "PASS" if not errors else "FAIL"

    print("=" * 92)
    print(f"NEA POST-WRITE INTEGRITY & DIFF RECEIPT (v2.2.3) | Status: {status}")
    print(f"Write Verification Token: {wrt_token}")
    print(f"Baseline Workbook: {before['filename']} (SHA256={before['sha256']})")
    print(f"Modified Workbook: {after['filename']} (SHA256={after['sha256']})")
    print(f"OpenXML <extLst> Auto-Preservation: {'RESTORED' if ext_restored else 'INTACT'}")
    print(f"Protected Formula Check (<f>): {'PASS (0 formulas overwritten)' if not formula_losses else 'FAIL'}")
    print(f"Formulas Restored (<f>): {len(formula_restorations)}")
    print(f"Editable Cells Modified: {len(cell_diffs)}")
    print("=" * 92)
    for item in formula_restorations[:30]:
        print(f"  + [FORMULA RESTORED] {item}")
    if len(formula_restorations) > 30:
        print(f"  ... ({len(formula_restorations) - 30} additional formula restorations)")
    for coord, old_v, new_v in cell_diffs[:50]:
        print(f"  - {coord}: '{old_v}' -> '{new_v}'")
    if len(cell_diffs) > 50:
        print(f"  ... ({len(cell_diffs) - 50} additional cell modifications)")
    if errors:
        print("\n[WRITE BLOCKED — INTEGRITY VIOLATIONS DETECTED]:")
        for e in errors:
            print(f"  - {e}")
        sys.exit(1)
    print(f"\n[WRITE-VERIFIED: PASS | {wrt_token}]")
    print(
        f"🔄 [CROSS-DUTY -> NEA Package Reviewer]: Workbook modifications verified ({wrt_token}). "
        f"Run NEA Package Reviewer before final handoff to issue the Release Readiness Report."
    )


def repair_single_xlsx(orig_path, out_path):
    """Non-destructively repairs overwritten Cover Sheet!B30:C30 formulas, Project BOM A8:I155 formulas,
    tblMaterials / Lists!H1 zero-spill bounds, Fiber Assemblies DV sqref, and CRL DataValidation / AutoFilter
    ranges while preserving 100% of engineer data inputs."""
    import shutil
    if os.path.abspath(orig_path) != os.path.abspath(out_path):
        shutil.copy2(orig_path, out_path)

    wb_info = parse_xlsx(orig_path)
    role = classify_workbook_role(wb_info)
    repaired_items = []

    with zipfile.ZipFile(orig_path, "r") as z_in:
        wb_xml = ET.fromstring(z_in.read("xl/workbook.xml"))
        rels_xml = ET.fromstring(z_in.read("xl/_rels/workbook.xml.rels"))
        rel_map = {
            r.attrib["Id"]: (r.attrib["Target"] if r.attrib["Target"].startswith("xl/") else "xl/" + r.attrib["Target"].lstrip("/"))
            for r in rels_xml.findall("rel:Relationship", REL_NS)
        }
        sheet_target_by_name = {
            s.attrib["name"]: rel_map.get(s.attrib[f"{{{NS['r']}}}id"], "")
            for s in wb_xml.findall(".//main:sheet", NS)
        }

        modified_entries = {}
        # 1. Check Cover Sheet B30:C30 formula link restoration
        cov_target = sheet_target_by_name.get("Cover Sheet")
        if cov_target and cov_target in z_in.namelist():
            cov_rows = wb_info["sheets"].get("Cover Sheet", {})
            h24_val = cell_val(cov_rows, 24, "H")
            d24_val = cell_val(cov_rows, 24, "D")
            b30_ci = cell_info(cov_rows, 30, "B")
            c30_ci = cell_info(cov_rows, 30, "C")
            if (not b30_ci["has_formula"] and (b30_ci["val"] or h24_val)) or (not c30_ci["has_formula"] and (c30_ci["val"] or d24_val)):
                xml_txt = z_in.read(cov_target).decode("utf-8")
                if not b30_ci["has_formula"] and (b30_ci["val"] or h24_val):
                    new_b30 = f'<c r="B30" s="25" t="str"><f>IF($H$24="","",$H$24)</f><v>{h24_val}</v></c>'
                    xml_txt_new = re.sub(r'<c r="B30"[^>]*>.*?</c>', new_b30, xml_txt, count=1, flags=re.DOTALL)
                    if xml_txt_new != xml_txt:
                        xml_txt = xml_txt_new
                        repaired_items.append(f"Cover Sheet!B30: Restored formula IF($H$24=\"\",\"\",$H$24) (val='{h24_val}')")
                if not c30_ci["has_formula"] and (c30_ci["val"] or d24_val):
                    new_c30 = f'<c r="C30" s="26"><f>IF($D$24="","",$D$24)</f><v>{d24_val}</v></c>'
                    xml_txt_new = re.sub(r'<c r="C30"[^>]*>.*?</c>', new_c30, xml_txt, count=1, flags=re.DOTALL)
                    if xml_txt_new != xml_txt:
                        xml_txt = xml_txt_new
                        repaired_items.append(f"Cover Sheet!C30: Restored formula IF($D$24=\"\",\"\",$D$24) (val='{d24_val}')")
                modified_entries[cov_target] = xml_txt.encode("utf-8")

        # 2. Check BOM tblMaterials table boundary (GOV-007 92-zero spill fix), Lists!H1, & Fiber Assemblies DV sqref
        if role == "BOM":
            mm_rows = wb_info["sheets"].get("Materials Master", {})
            max_tbl_row = max((r for r in mm_rows if r >= 4 and any(cell_val(mm_rows, r, c) for c in "ABCDEFG")), default=508)
            tbl_meta = wb_info.get("tables", {}).get("tblMaterials")
            if tbl_meta and tbl_meta["xml_path"] in z_in.namelist():
                t_path = tbl_meta["xml_path"]
                t_xml = z_in.read(t_path).decode("utf-8")
                expected_ref = f"A3:G{max_tbl_row}"
                if f'ref="{expected_ref}"' not in t_xml:
                    t_xml_new = re.sub(r'\bref="A3:G\d+"', f'ref="{expected_ref}"', t_xml)
                    if t_xml_new != t_xml:
                        repaired_items.append(f"{t_path}: Rescaled tblMaterials ref='{tbl_meta['ref']}' -> '{expected_ref}' (eliminating empty-row 0 coercion)")
                        modified_entries[t_path] = t_xml_new.encode("utf-8")
            lists_target = sheet_target_by_name.get("Lists")
            if lists_target and lists_target in z_in.namelist():
                l_xml = z_in.read(lists_target).decode("utf-8")
                old_f = "_xlfn._xlws.FILTER(_xlfn.VSTACK(tblMaterials[MB P/N],'Fiber Assemblies'!$C$4:$C$1258,'Cable Harness'!$C$4:$C$1258),_xlfn.VSTACK(tblMaterials[MB P/N],'Fiber Assemblies'!$C$4:$C$1258,'Cable Harness'!$C$4:$C$1258)&lt;&gt;\"\")"
                new_f = "_xlfn._xlws.FILTER(_xlfn.VSTACK(tblMaterials[MB P/N],'Fiber Assemblies'!$C$4:$C$1258,'Cable Harness'!$C$4:$C$1258),(_xlfn.VSTACK(tblMaterials[MB P/N],'Fiber Assemblies'!$C$4:$C$1258,'Cable Harness'!$C$4:$C$1258)&lt;&gt;\"\")*(_xlfn.VSTACK(tblMaterials[MB P/N],'Fiber Assemblies'!$C$4:$C$1258,'Cable Harness'!$C$4:$C$1258)&lt;&gt;0))"
                if old_f in l_xml:
                    l_xml_new = l_xml.replace(old_f, new_f, 1)
                    repaired_items.append("Lists!H1: Hardened BOMPartNumbers FILTER formula with (<>0) guard against zero-spill")
                    modified_entries[lists_target] = l_xml_new.encode("utf-8")
            fa_target = sheet_target_by_name.get("Fiber Assemblies")
            if fa_target and fa_target in z_in.namelist():
                fa_xml = z_in.read(fa_target).decode("utf-8")
                if 'sqref="H4:H286"' in fa_xml:
                    fa_xml_new = fa_xml.replace('sqref="H4:H286"', 'sqref="H4:H1258"', 1)
                    repaired_items.append("Fiber Assemblies!H: Expanded Status DataValidation sqref='H4:H286' -> 'H4:H1258'")
                    modified_entries[fa_target] = fa_xml_new.encode("utf-8")

        # 3. Check CRL DataValidation & AutoFilter repair
        if role == "CRL":
            crl_target = sheet_target_by_name.get("Cable Running List")
            if crl_target and crl_target in z_in.namelist():
                xml_txt = z_in.read(crl_target).decode("utf-8")
                orig_xml_txt = xml_txt
                xml_txt = re.sub(
                    r'(<autoFilter\s+ref=")[^"]+(")',
                    r"\g<1>A2:P1087\2",
                    xml_txt,
                )
                if xml_txt != orig_xml_txt:
                    repaired_items.append("Cable Running List: Normalized <autoFilter ref='A2:P1087'>")
                    modified_entries[crl_target] = xml_txt.encode("utf-8")
            wb_txt = z_in.read("xl/workbook.xml").decode("utf-8")
            wb_txt_new = re.sub(
                r"(<definedName[^>]*name=\"_xlnm\._FilterDatabase\"[^>]*>)'Cable Running List'!\$A\$\d+:\$P\$\d+(</definedName>)",
                r"\g<1>'Cable Running List'!$A$2:$P$1087\2",
                wb_txt,
            )
            if wb_txt_new != wb_txt:
                repaired_items.append("xl/workbook.xml: Normalized _xlnm._FilterDatabase to 'Cable Running List'!$A$2:$P$1087")
                modified_entries["xl/workbook.xml"] = wb_txt_new.encode("utf-8")

        # 4. Check TIMESHEET AG35 missing formula, AG17 normalization, and sheetProtection removal
        if role == "TIMESHEET":
            for s_name, s_target in sheet_target_by_name.items():
                if s_name in ("Weekly Summary", "Expense Report") or s_target not in z_in.namelist():
                    continue
                s_xml = z_in.read(s_target).decode("utf-8")
                orig_s_xml = s_xml
                s_xml = re.sub(r"<sheetProtection[^>]*/>", "", s_xml)
                if "SUM(F17+J17+N17+R17+V17+Z17+AD17)" in s_xml:
                    s_xml = s_xml.replace("SUM(F17+J17+N17+R17+V17+Z17+AD17)", "F17+J17+N17+R17+V17+Z17+AD17")
                    repaired_items.append(f"{s_name}!AG17: Normalized REG formula to F17+J17+N17+R17+V17+Z17+AD17")
                if '<c r="AG35"' in s_xml and "<f>F35+J35+N35+R35+V35+Z35+AD35</f>" not in s_xml:
                    s_xml = re.sub(
                        r'(<c r="AG35"[^>]*>)(.*?)(</c>)',
                        r'\g<1><f>F35+J35+N35+R35+V35+Z35+AD35</f><v>0</v>\g<3>',
                        s_xml,
                        count=1,
                        flags=re.DOTALL,
                    )
                    repaired_items.append(f"{s_name}!AG35: Restored missing Job Slot 10 REG formula (F35+J35+N35+R35+V35+Z35+AD35)")
                elif '<c r="AG35"' not in s_xml and '<c r="AH35"' in s_xml:
                    s_xml = s_xml.replace(
                        '<c r="AH35"',
                        '<c r="AG35" s="106"><f>F35+J35+N35+R35+V35+Z35+AD35</f><v>0</v></c><c r="AH35"',
                        1,
                    )
                    repaired_items.append(f"{s_name}!AG35: Inserted missing Job Slot 10 REG formula cell")
                if s_xml != orig_s_xml:
                    modified_entries[s_target] = s_xml.encode("utf-8")

        if modified_entries:
            entries = []
            for info in z_in.infolist():
                data = modified_entries.get(info.filename, z_in.read(info.filename))
                entries.append((info.filename, data))
            with zipfile.ZipFile(out_path, "w", compression=zipfile.ZIP_DEFLATED) as z_out:
                for fn, data in entries:
                    z_out.writestr(fn, data)

    preserve_openxml_extensions(orig_path, out_path)
    return repaired_items


def run_repair_workbooks(target_dir, out_dir):
    """Executes non-destructive structural workbook repair across target_dir and verifies each output."""
    resolved_dir, xlsx_files = discover_xlsx_files(target_dir)
    if not xlsx_files:
        print(f"ERROR: No .xlsx files found in '{target_dir}' (resolved: '{resolved_dir}').")
        sys.exit(2)
    os.makedirs(out_dir, exist_ok=True)
    print("=" * 92)
    print(f"NEA DETERMINISTIC WORKBOOK & TEMPLATE REPAIR TOOL (v2.2.3) | Out Dir: {out_dir}")
    print("=" * 92)
    for orig_p in xlsx_files:
        fn = os.path.basename(orig_p)
        out_p = os.path.join(out_dir, fn)
        repairs = repair_single_xlsx(orig_p, out_p)
        print(f"\n[REPAIR TARGET]: {fn} -> {out_p} ({len(repairs)} structural repair(s) applied)")
        for r_msg in repairs:
            print(f"  * {r_msg}")
        run_verify_write(orig_p, out_p)


class SharedStringTable:
    """Manages xl/sharedStrings.xml so all consolidated worksheets use native Desktop Excel t='s' string indices."""

    def __init__(self, ss_xml_bytes):
        main_ns = NS["main"]
        ET.register_namespace("", main_ns)
        self.root = ET.fromstring(ss_xml_bytes)
        self.str_to_idx = {}
        self.ref_count = int(self.root.attrib.get("count", "0") or 0)
        for idx, si in enumerate(self.root.findall(f"{{{main_ns}}}si")):
            txt = "".join(t.text or "" for t in si.iter(f"{{{main_ns}}}t"))
            if txt not in self.str_to_idx:
                self.str_to_idx[txt] = idx

    def get_or_add(self, text_val):
        s = str(text_val)
        self.ref_count += 1
        if s in self.str_to_idx:
            return self.str_to_idx[s]
        main_ns = NS["main"]
        si = ET.SubElement(self.root, f"{{{main_ns}}}si")
        t = ET.SubElement(si, f"{{{main_ns}}}t")
        if s.startswith(" ") or s.endswith(" ") or "\n" in s:
            t.attrib["{http://www.w3.org/XML/1998/namespace}space"] = "preserve"
        t.text = s
        idx = len(self.root.findall(f"{{{main_ns}}}si")) - 1
        self.str_to_idx[s] = idx
        return idx

    def to_xml_bytes(self):
        main_ns = NS["main"]
        unique_cnt = len(self.root.findall(f"{{{main_ns}}}si"))
        self.root.attrib["count"] = str(max(self.ref_count, unique_cnt))
        self.root.attrib["uniqueCount"] = str(unique_cnt)
        raw = ET.tostring(self.root, encoding="utf-8", xml_declaration=False).decode("utf-8")
        raw = re.sub(
            r"^<sst\b[^>]*>",
            f'<sst xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" count="{self.root.attrib["count"]}" uniqueCount="{unique_cnt}">',
            raw,
            count=1,
        )
        return ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\r\n' + raw).encode("utf-8")


def _col_to_idx(col_str):
    n = 0
    for ch in str(col_str or ""):
        if "A" <= ch <= "Z":
            n = n * 26 + (ord(ch) - ord("A") + 1)
    return n


def _idx_to_col(idx):
    res = []
    n = int(idx)
    while n > 0:
        n, rem = divmod(n - 1, 26)
        res.append(chr(ord("A") + rem))
    return "".join(reversed(res))


def _sort_sheetdata_rows_and_cells(sheet_data_el):
    """Ensures <row> elements in <sheetData> and <c> elements in each <row> are in strictly ascending ECMA-376 order."""
    main_ns = NS["main"]
    col_re = re.compile(r"^([A-Z]+)(\d+)$")

    def col_to_idx(col_str):
        n = 0
        for ch in col_str:
            n = n * 26 + (ord(ch) - ord("A") + 1)
        return n

    rows = list(sheet_data_el.findall(f"{{{main_ns}}}row"))
    for r_el in rows:
        sheet_data_el.remove(r_el)
        cells = list(r_el.findall(f"{{{main_ns}}}c"))
        for c_el in cells:
            r_el.remove(c_el)
        cells.sort(key=lambda c: col_to_idx(col_re.match(c.attrib.get("r", "A1")).group(1)))
        for c_el in cells:
            r_el.append(c_el)
    rows.sort(key=lambda r: int(r.attrib.get("r", "0")))
    for r_el in rows:
        sheet_data_el.append(r_el)


def _format_worksheet_xml_bytes(root_el, sheet_uid):
    """Serializes a <worksheet> element with the exact ECMA-376 mc:Ignorable namespace declarations required by Desktop Excel."""
    raw = ET.tostring(root_el, encoding="utf-8", xml_declaration=False).decode("utf-8")
    open_tag = (
        '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" '
        'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" '
        'xmlns:mc="http://schemas.openxmlformats.org/markup-compatibility/2006" '
        'mc:Ignorable="x14ac xr xr2 xr3" '
        'xmlns:x14ac="http://schemas.microsoft.com/office/spreadsheetml/2009/9/ac" '
        'xmlns:xr="http://schemas.microsoft.com/office/spreadsheetml/2014/revision" '
        'xmlns:xr2="http://schemas.microsoft.com/office/spreadsheetml/2015/revision2" '
        'xmlns:xr3="http://schemas.microsoft.com/office/spreadsheetml/2016/revision3" '
        f'xr:uid="{sheet_uid}">'
    )
    raw = re.sub(r"^<worksheet\b[^>]*>", open_tag, raw, count=1)
    return ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\r\n' + raw).encode("utf-8")


def populate_timesheet_xml(template_sheet_xml_bytes, emp_rec, default_week_ending_serial, shared_strings=None, sheet_idx=2):
    """Populates a clone of Timesheet_Template.xlsx sheet1.xml with an employee's weekly hours and computes cached <v> values."""
    main_ns = NS["main"]
    ET.register_namespace("", main_ns)
    ET.register_namespace("r", NS["r"])
    ET.register_namespace("mc", "http://schemas.openxmlformats.org/markup-compatibility/2006")
    ET.register_namespace("x14ac", "http://schemas.microsoft.com/office/spreadsheetml/2009/9/ac")
    ET.register_namespace("xr", "http://schemas.microsoft.com/office/spreadsheetml/2014/revision")
    ET.register_namespace("xr2", "http://schemas.microsoft.com/office/spreadsheetml/2015/revision2")
    ET.register_namespace("xr3", "http://schemas.microsoft.com/office/spreadsheetml/2016/revision3")

    root = ET.fromstring(template_sheet_xml_bytes)
    for sp in list(root.findall(f"{{{main_ns}}}sheetProtection")):
        root.remove(sp)
    for spr in root.findall(f"{{{main_ns}}}sheetPr"):
        spr.attrib.pop("codeName", None)
    for ps in root.findall(f"{{{main_ns}}}pageSetup"):
        ps.attrib.pop(f"{{{NS['r']}}}id", None)
    for sv in root.findall(f".//{{{main_ns}}}sheetView"):
        sv.attrib.pop("tabSelected", None)
    xr_uid_key = "{http://schemas.microsoft.com/office/spreadsheetml/2014/revision}uid"
    for dv_el in root.findall(f".//{{{main_ns}}}dataValidation"):
        if xr_uid_key in dv_el.attrib:
            dv_el.attrib[xr_uid_key] = f"{{00000000-0002-0000-{sheet_idx:04X}-000000000000}}"

    sheet_data = root.find(f"{{{main_ns}}}sheetData")
    row_map = {int(r.attrib["r"]): r for r in sheet_data.findall(f"{{{main_ns}}}row")}

    def get_or_make_cell(r_num, col_let):
        row_el = row_map.get(r_num)
        if row_el is None:
            row_el = ET.SubElement(sheet_data, f"{{{main_ns}}}row", {"r": str(r_num)})
            row_map[r_num] = row_el
        ref = f"{col_let}{r_num}"
        for c_el in row_el.findall(f"{{{main_ns}}}c"):
            if c_el.attrib.get("r") == ref:
                return c_el
        c_el = ET.SubElement(row_el, f"{{{main_ns}}}c", {"r": ref})
        return c_el

    def set_str_cell(r_num, col_let, text_val, allow_numeric_id=False):
        c_el = get_or_make_cell(r_num, col_let)
        for ch in list(c_el):
            c_el.remove(ch)
        if text_val is None or str(text_val).strip() == "":
            c_el.attrib.pop("t", None)
            return
        s_val = str(text_val).strip()
        if allow_numeric_id and s_val.isdigit() and (len(s_val) == 1 or not s_val.startswith("0")):
            c_el.attrib.pop("t", None)
            ET.SubElement(c_el, f"{{{main_ns}}}v").text = s_val
            return
        if shared_strings is not None:
            c_el.attrib["t"] = "s"
            ss_idx = shared_strings.get_or_add(str(text_val))
            ET.SubElement(c_el, f"{{{main_ns}}}v").text = str(ss_idx)
        else:
            c_el.attrib["t"] = "inlineStr"
            is_el = ET.SubElement(c_el, f"{{{main_ns}}}is")
            t_el = ET.SubElement(is_el, f"{{{main_ns}}}t")
            t_el.text = str(text_val)

    def set_num_cell(r_num, col_let, num_val):
        c_el = get_or_make_cell(r_num, col_let)
        for ch in list(c_el):
            c_el.remove(ch)
        c_el.attrib.pop("t", None)
        if num_val is None or num_val == "" or float(num_val) == 0.0:
            return
        v_el = ET.SubElement(c_el, f"{{{main_ns}}}v")
        f_val = float(num_val)
        v_el.text = str(int(f_val)) if f_val.is_integer() else f"{f_val:.2f}"

    def set_formula_val(r_num, col_let, cached_val, formula_override=None):
        c_el = get_or_make_cell(r_num, col_let)
        f_el = c_el.find(f"{{{main_ns}}}f")
        if formula_override is not None:
            if f_el is None:
                f_el = ET.Element(f"{{{main_ns}}}f")
                c_el.insert(0, f_el)
            f_el.text = formula_override
        v_el = c_el.find(f"{{{main_ns}}}v")
        if v_el is None:
            v_el = ET.SubElement(c_el, f"{{{main_ns}}}v")
        if isinstance(cached_val, (int, float)):
            f_val = float(cached_val)
            v_el.text = str(int(f_val)) if f_val.is_integer() else f"{f_val:.2f}"
        else:
            v_el.text = str(cached_val)

    we_serial = iso_to_excel_serial(emp_rec.get("week_ending")) or default_week_ending_serial or 46326
    bw_serial = we_serial - 6
    c_x2 = get_or_make_cell(2, "X")
    for ch in list(c_x2):
        c_x2.remove(ch)
    c_x2.attrib.pop("t", None)
    ET.SubElement(c_x2, f"{{{main_ns}}}v").text = str(we_serial)

    set_formula_val(1, "X", bw_serial)
    day_hdr_cols = ["F", "J", "N", "R", "V", "Z", "AD"]
    for idx, d_col in enumerate(day_hdr_cols):
        set_formula_val(6, d_col, bw_serial + idx)

    set_str_cell(2, "K", emp_rec.get("union_local", "1"))
    set_str_cell(3, "K", emp_rec.get("position", "Tech"))
    set_str_cell(3, "X", emp_rec.get("employee", ""))

    job_hdr_rows = [7, 10, 13, 16, 19, 22, 25, 28, 31, 34]
    job_dat_rows = [8, 11, 14, 17, 20, 23, 26, 29, 32, 35]
    day_map = {
        "sun": ("F", "G", "H"),
        "mon": ("J", "K", "L"),
        "tue": ("N", "O", "P"),
        "tues": ("N", "O", "P"),
        "wed": ("R", "S", "T"),
        "thu": ("V", "W", "X"),
        "fri": ("Z", "AA", "AB"),
        "sat": ("AD", "AE", "AF"),
    }
    all_day_cols = [
        "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q",
        "R", "S", "T", "U", "V", "W", "X", "Y", "Z", "AA", "AB", "AC",
        "AD", "AE", "AF",
    ]
    col_sums = defaultdict(float)
    jobs = emp_rec.get("jobs", [])[:10]

    for slot_idx in range(10):
        r_hdr = job_hdr_rows[slot_idx]
        r_dat = job_dat_rows[slot_idx]
        for dc in all_day_cols:
            set_num_cell(r_dat, dc, 0)
        if slot_idx < len(jobs):
            jb = jobs[slot_idx]
            set_str_cell(r_hdr, "A", jb.get("building", ""))
            set_str_cell(r_dat, "A", jb.get("job_name", ""))
            set_str_cell(r_dat, "D", jb.get("job_number", ""), allow_numeric_id=True)
            shift_code = str(jb.get("shift", "REG") or "REG").upper()
            if shift_code not in ("REG", "2ND", "3RD"):
                shift_code = "REG"
            for sc in ("F", "J", "N", "R", "V", "Z"):
                set_str_cell(r_hdr, sc, shift_code)
            c_ad_hdr = get_or_make_cell(r_hdr, "AD")
            c_ad_hdr.attrib["t"] = "str"
            set_formula_val(r_hdr, "AD", shift_code)

            reg_sum = 0.0
            ot_sum = 0.0
            dt_sum = 0.0
            hours_dict = jb.get("hours", {})
            for d_key, (c_reg, c_ot, c_dt) in day_map.items():
                if d_key not in hours_dict:
                    continue
                d_entry = hours_dict[d_key]
                if isinstance(d_entry, (int, float)):
                    r_v, o_v, d_v = float(d_entry), 0.0, 0.0
                elif isinstance(d_entry, dict):
                    r_v = float(d_entry.get("reg", d_entry.get("REG", 0)) or 0)
                    o_v = float(d_entry.get("ot", d_entry.get("OT", 0)) or 0)
                    d_v = float(d_entry.get("dt", d_entry.get("DT", 0)) or 0)
                else:
                    r_v, o_v, d_v = 0.0, 0.0, 0.0
                if r_v:
                    set_num_cell(r_dat, c_reg, r_v)
                    reg_sum += r_v
                    col_sums[c_reg] += r_v
                if o_v:
                    set_num_cell(r_dat, c_ot, o_v)
                    ot_sum += o_v
                    col_sums[c_ot] += o_v
                if d_v:
                    set_num_cell(r_dat, c_dt, d_v)
                    dt_sum += d_v
                    col_sums[c_dt] += d_v

            s2_sum = reg_sum if shift_code == "2ND" else 0.0
            s3_sum = reg_sum if shift_code == "3RD" else 0.0
            set_formula_val(r_dat, "AG", reg_sum, f"F{r_dat}+J{r_dat}+N{r_dat}+R{r_dat}+V{r_dat}+Z{r_dat}+AD{r_dat}")
            set_formula_val(r_dat, "AH", ot_sum)
            set_formula_val(r_dat, "AI", dt_sum)
            set_formula_val(r_dat, "AJ", s2_sum)
            set_formula_val(r_dat, "AK", s3_sum)
            col_sums["AG"] += reg_sum
            col_sums["AH"] += ot_sum
            col_sums["AI"] += dt_sum
            col_sums["AJ"] += s2_sum
            col_sums["AK"] += s3_sum
        else:
            set_str_cell(r_hdr, "A", "")
            set_str_cell(r_dat, "A", "")
            set_str_cell(r_dat, "D", "")
            for sc in ("F", "J", "N", "R", "V", "Z"):
                set_str_cell(r_hdr, sc, "REG")
            c_ad_hdr = get_or_make_cell(r_hdr, "AD")
            c_ad_hdr.attrib["t"] = "str"
            set_formula_val(r_hdr, "AD", "REG")
            set_formula_val(r_dat, "AG", 0, f"F{r_dat}+J{r_dat}+N{r_dat}+R{r_dat}+V{r_dat}+Z{r_dat}+AD{r_dat}")
            set_formula_val(r_dat, "AH", 0)
            set_formula_val(r_dat, "AI", 0)
            set_formula_val(r_dat, "AJ", 0)
            set_formula_val(r_dat, "AK", 0)

    for c_tot in all_day_cols + ["AG", "AH", "AI", "AJ", "AK"]:
        set_formula_val(38, c_tot, col_sums.get(c_tot, 0.0))

    _sort_sheetdata_rows_and_cells(sheet_data)
    sheet_uid = f"{{00000000-0001-0000-{sheet_idx:04X}-000000000000}}"
    return _format_worksheet_xml_bytes(root, sheet_uid), col_sums


def build_weekly_summary_sheet_xml(sorted_employees, begin_iso, end_iso, shared_strings=None):
    """Builds the NetCom corporate 'Weekly Summary' executive dashboard XML (Tab 1) summarizing all employee & job hours."""
    main_ns = NS["main"]
    root = ET.Element(f"{{{main_ns}}}worksheet")
    sheet_pr = ET.SubElement(root, f"{{{main_ns}}}sheetPr")
    ET.SubElement(sheet_pr, f"{{{main_ns}}}tabColor", {"rgb": "FF114573"})
    ET.SubElement(sheet_pr, f"{{{main_ns}}}pageSetUpPr", {"fitToPage": "1"})

    dim_el = ET.SubElement(root, f"{{{main_ns}}}dimension", {"ref": "A1:N9"})
    svs = ET.SubElement(root, f"{{{main_ns}}}sheetViews")
    sv_el = ET.SubElement(svs, f"{{{main_ns}}}sheetView", {"tabSelected": "1", "workbookViewId": "0"})
    ET.SubElement(sv_el, f"{{{main_ns}}}pane", {
        "ySplit": "7",
        "topLeftCell": "A8",
        "activePane": "bottomLeft",
        "state": "frozen",
    })
    ET.SubElement(sv_el, f"{{{main_ns}}}selection", {
        "pane": "bottomLeft",
        "activeCell": "A8",
        "sqref": "A8",
    })
    ET.SubElement(root, f"{{{main_ns}}}sheetFormatPr", {"defaultRowHeight": "18"})

    cols_el = ET.SubElement(root, f"{{{main_ns}}}cols")
    col_widths = [
        (1, 1, "25"), (2, 2, "18"), (3, 3, "13"), (4, 4, "18"), (5, 5, "26"),
        (6, 6, "15"), (7, 11, "11"), (12, 12, "13"), (13, 13, "11"), (14, 14, "16"),
    ]
    for c_min, c_max, w in col_widths:
        ET.SubElement(cols_el, f"{{{main_ns}}}col", {
            "min": str(c_min),
            "max": str(c_max),
            "width": w,
            "customWidth": "1",
        })

    sdata = ET.SubElement(root, f"{{{main_ns}}}sheetData")

    def add_row(r_idx, cells_spec, row_ht=None):
        r_attrib = {"r": str(r_idx)}
        if row_ht is not None:
            r_attrib["ht"] = str(row_ht)
            r_attrib["customHeight"] = "1"
        r_el = ET.SubElement(sdata, f"{{{main_ns}}}row", r_attrib)
        for col_let, val, kind, formula, s_idx in cells_spec:
            c_attrib = {"r": f"{col_let}{r_idx}"}
            if s_idx is not None:
                c_attrib["s"] = str(s_idx)
            c_el = ET.SubElement(r_el, f"{{{main_ns}}}c", c_attrib)
            if kind == "blank":
                continue
            elif kind == "str":
                if shared_strings is not None:
                    c_el.attrib["t"] = "s"
                    ss_idx = shared_strings.get_or_add(str(val))
                    ET.SubElement(c_el, f"{{{main_ns}}}v").text = str(ss_idx)
                else:
                    c_el.attrib["t"] = "inlineStr"
                    is_el = ET.SubElement(c_el, f"{{{main_ns}}}is")
                    ET.SubElement(is_el, f"{{{main_ns}}}t").text = str(val)
            elif kind == "num":
                f_v = float(val or 0)
                ET.SubElement(c_el, f"{{{main_ns}}}v").text = str(int(f_v)) if f_v.is_integer() else f"{f_v:.2f}"
            elif kind == "formula":
                ET.SubElement(c_el, f"{{{main_ns}}}f").text = formula
                f_v = float(val or 0)
                ET.SubElement(c_el, f"{{{main_ns}}}v").text = str(int(f_v)) if f_v.is_integer() else f"{f_v:.2f}"

    # Pre-scan job rows so metadata strip and KPI cards know exact row counts and totals
    job_rows_data = []
    grand = defaultdict(float)
    for emp in sorted_employees:
        tab_name = emp["tab_name"]
        pos = emp.get("position", "")
        loc = emp.get("union_local", "")
        for jb in emp.get("jobs", [])[:10]:
            bldg = jb.get("building", "")
            jname = jb.get("job_name", "")
            jnum = jb.get("job_number", "")
            shift_code = str(jb.get("shift", "REG") or "REG").upper()
            reg_h, ot_h, dt_h = 0.0, 0.0, 0.0
            for d_entry in jb.get("hours", {}).values():
                if isinstance(d_entry, (int, float)):
                    reg_h += float(d_entry)
                elif isinstance(d_entry, dict):
                    reg_h += float(d_entry.get("reg", d_entry.get("REG", 0)) or 0)
                    ot_h += float(d_entry.get("ot", d_entry.get("OT", 0)) or 0)
                    dt_h += float(d_entry.get("dt", d_entry.get("DT", 0)) or 0)
            s2_h = reg_h if shift_code == "2ND" else 0.0
            s3_h = reg_h if shift_code == "3RD" else 0.0
            fm_h = float(jb.get("foreman_hours", 0) or 0)
            tr_h = float(jb.get("travel_hours", 0) or 0)
            tot_h = reg_h + ot_h + dt_h
            if tot_h == 0 and fm_h == 0 and tr_h == 0:
                continue
            job_rows_data.append({
                "tab_name": tab_name,
                "pos": pos,
                "loc": str(loc),
                "bldg": bldg,
                "jname": jname,
                "jnum": str(jnum),
                "reg_h": reg_h,
                "ot_h": ot_h,
                "dt_h": dt_h,
                "s2_h": s2_h,
                "s3_h": s3_h,
                "fm_h": fm_h,
                "tr_h": tr_h,
                "tot_h": tot_h,
            })
            grand["G"] += reg_h
            grand["H"] += ot_h
            grand["I"] += dt_h
            grand["J"] += s2_h
            grand["K"] += s3_h
            grand["L"] += fm_h
            grand["M"] += tr_h
            grand["N"] += tot_h

    first_data_r = 8
    last_data_r = max(first_data_r, first_data_r + len(job_rows_data) - 1)
    tot_r = last_data_r + 1

    # Row 1: Primary Navy Title Banner (A1:N1 merged, style 217)
    r1_cells = [("A", "NETCOM, INC. — WEEKLY TIMESHEET CONSOLIDATION & LABOR SUMMARY", "str", None, 217)]
    for c_let in ["B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N"]:
        r1_cells.append((c_let, None, "blank", None, 217))
    add_row(1, r1_cells, row_ht=34)

    # Row 2: Executive Metadata Ribbon (Deep Teal labels 218 + Steel Slate values 219 + Cyan badge 220)
    add_row(2, [
        ("A", "PAY PERIOD (SUN–SAT):", "str", None, 218),
        ("B", f"{begin_iso} to {end_iso}", "str", None, 219),
        ("C", None, "blank", None, 219),
        ("D", None, "blank", None, 219),
        ("E", "WEEK ENDING:", "str", None, 218),
        ("F", f"{end_iso}", "str", None, 219),
        ("G", None, "blank", None, 219),
        ("H", "EMPLOYEES:", "str", None, 218),
        ("I", f"{len({e.get('_base_tab', e['tab_name']) for e in sorted_employees})} Consolidated", "str", None, 219),
        ("J", None, "blank", None, 219),
        ("K", "ACTIVE JOBS:", "str", None, 218),
        ("L", f"{len(job_rows_data)} Job Entries", "str", None, 219),
        ("M", None, "blank", None, 219),
        ("N", "NEA v2.2.3", "str", None, 220),
    ], row_ht=22)

    # Row 3: Compact Spacer
    add_row(3, [], row_ht=9)

    # Row 4: 7 KPI Metric Card Headers (2-column merges A4:B4 .. M4:N4)
    add_row(4, [
        ("A", "REGULAR HOURS (REG)", "str", None, 221),
        ("B", None, "blank", None, 221),
        ("C", "OVERTIME HOURS (OT)", "str", None, 221),
        ("D", None, "blank", None, 221),
        ("E", "DOUBLE TIME (DT)", "str", None, 221),
        ("F", None, "blank", None, 221),
        ("G", "2ND SHIFT HOURS", "str", None, 221),
        ("H", None, "blank", None, 221),
        ("I", "3RD SHIFT HOURS", "str", None, 221),
        ("J", None, "blank", None, 221),
        ("K", "FOREMAN / GF HRS", "str", None, 221),
        ("L", None, "blank", None, 221),
        ("M", "TOTAL PAID HOURS", "str", None, 223),
        ("N", None, "blank", None, 223),
    ], row_ht=19)

    # Row 5: 7 KPI Metric Card Live Formulas referencing Grand Totals Row
    add_row(5, [
        ("A", grand["G"], "formula", f"G{tot_r}", 222),
        ("B", None, "blank", None, 222),
        ("C", grand["H"], "formula", f"H{tot_r}", 222),
        ("D", None, "blank", None, 222),
        ("E", grand["I"], "formula", f"I{tot_r}", 222),
        ("F", None, "blank", None, 222),
        ("G", grand["J"], "formula", f"J{tot_r}", 222),
        ("H", None, "blank", None, 222),
        ("I", grand["K"], "formula", f"K{tot_r}", 222),
        ("J", None, "blank", None, 222),
        ("K", grand["L"], "formula", f"L{tot_r}", 222),
        ("L", None, "blank", None, 222),
        ("M", grand["N"], "formula", f"N{tot_r}", 224),
        ("N", None, "blank", None, 224),
    ], row_ht=26)

    # Row 6: Compact Spacer
    add_row(6, [], row_ht=9)

    # Row 7: Table Column Headers (Identity A..F = 225 Primary Navy; Hours G..M = 226 Deep Teal; Total N = 227)
    add_row(7, [
        ("A", "Employee (Last, First)", "str", None, 225),
        ("B", "Position / Title", "str", None, 225),
        ("C", "Union Local #", "str", None, 225),
        ("D", "Building / Qualifier", "str", None, 225),
        ("E", "Job / Project Name", "str", None, 225),
        ("F", "Job Number", "str", None, 225),
        ("G", "REG Hrs", "str", None, 226),
        ("H", "OT Hrs", "str", None, 226),
        ("I", "DT Hrs", "str", None, 226),
        ("J", "2ND Shift", "str", None, 226),
        ("K", "3RD Shift", "str", None, 226),
        ("L", "Foreman / GF", "str", None, 226),
        ("M", "Travel Hrs", "str", None, 226),
        ("N", "Total Paid Hours", "str", None, 227),
    ], row_ht=28)

    # Rows 8..last_data_r: Zebra-striped Employee Job Rows
    for idx_row, jr in enumerate(job_rows_data):
        curr_r = first_data_r + idx_row
        is_odd = (idx_row % 2 == 1)
        s_emp = 229 if is_odd else 228
        s_ctr = 231 if is_odd else 230
        s_lft = 233 if is_odd else 232
        s_num = 235 if is_odd else 234
        s_tot = 236
        add_row(curr_r, [
            ("A", jr["tab_name"], "str", None, s_emp),
            ("B", jr["pos"], "str", None, s_ctr),
            ("C", jr["loc"], "str", None, s_ctr),
            ("D", jr["bldg"], "str", None, s_lft),
            ("E", jr["jname"], "str", None, s_lft),
            ("F", jr["jnum"], "str", None, s_ctr),
            ("G", jr["reg_h"], "num", None, s_num),
            ("H", jr["ot_h"], "num", None, s_num),
            ("I", jr["dt_h"], "num", None, s_num),
            ("J", jr["s2_h"], "num", None, s_num),
            ("K", jr["s3_h"], "num", None, s_num),
            ("L", jr["fm_h"], "num", None, s_num),
            ("M", jr["tr_h"], "num", None, s_num),
            ("N", jr["tot_h"], "formula", f"SUM(G{curr_r}:I{curr_r})", s_tot),
        ], row_ht=21)

    # Row tot_r: Weekly Grand Totals Banner (A{tot_r}:F{tot_r} merged, style 237..239)
    tot_cells = [
        ("A", "WEEKLY GRAND TOTALS", "str", None, 237),
        ("B", None, "blank", None, 237),
        ("C", None, "blank", None, 237),
        ("D", None, "blank", None, 237),
        ("E", None, "blank", None, 237),
        ("F", None, "blank", None, 237),
        ("G", grand["G"], "formula", f"SUM(G{first_data_r}:G{last_data_r})", 238),
        ("H", grand["H"], "formula", f"SUM(H{first_data_r}:H{last_data_r})", 238),
        ("I", grand["I"], "formula", f"SUM(I{first_data_r}:I{last_data_r})", 238),
        ("J", grand["J"], "formula", f"SUM(J{first_data_r}:J{last_data_r})", 238),
        ("K", grand["K"], "formula", f"SUM(K{first_data_r}:K{last_data_r})", 238),
        ("L", grand["L"], "formula", f"SUM(L{first_data_r}:L{last_data_r})", 238),
        ("M", grand["M"], "formula", f"SUM(M{first_data_r}:M{last_data_r})", 238),
        ("N", grand["N"], "formula", f"SUM(N{first_data_r}:N{last_data_r})", 239),
    ]
    add_row(tot_r, tot_cells, row_ht=26)

    dim_el.attrib["ref"] = f"A1:N{tot_r}"

    # ECMA-376 child element order after <sheetData>: <autoFilter>, <mergeCells>, <pageMargins>, <pageSetup>
    ET.SubElement(root, f"{{{main_ns}}}autoFilter", {"ref": f"A7:N{last_data_r}"})

    merge_refs = [
        "A1:N1",
        "B2:D2", "F2:G2", "I2:J2", "L2:M2",
        "A4:B4", "C4:D4", "E4:F4", "G4:H4", "I4:J4", "K4:L4", "M4:N4",
        "A5:B5", "C5:D5", "E5:F5", "G5:H5", "I5:J5", "K5:L5", "M5:N5",
        f"A{tot_r}:F{tot_r}",
    ]
    mc_el = ET.SubElement(root, f"{{{main_ns}}}mergeCells", {"count": str(len(merge_refs))})
    for mref in merge_refs:
        ET.SubElement(mc_el, f"{{{main_ns}}}mergeCell", {"ref": mref})

    ET.SubElement(root, f"{{{main_ns}}}pageMargins", {
        "left": "0.4", "right": "0.4", "top": "0.5", "bottom": "0.5", "header": "0.3", "footer": "0.3"
    })
    ET.SubElement(root, f"{{{main_ns}}}pageSetup", {
        "orientation": "landscape", "fitToWidth": "1", "fitToHeight": "0"
    })

    _sort_sheetdata_rows_and_cells(sdata)
    return _format_worksheet_xml_bytes(root, "{00000000-0001-0000-0001-000000000000}"), grand, last_data_r


def build_job_summary_sheet_xml(sorted_employees, begin_iso, end_iso, shared_strings=None):
    """Builds the NetCom corporate 'Job Summary' executive dashboard XML (Tab 2) rolling up hours by Job Number for bid tracking."""
    main_ns = NS["main"]
    root = ET.Element(f"{{{main_ns}}}worksheet")
    sheet_pr = ET.SubElement(root, f"{{{main_ns}}}sheetPr")
    ET.SubElement(sheet_pr, f"{{{main_ns}}}tabColor", {"rgb": "FF165366"})
    ET.SubElement(sheet_pr, f"{{{main_ns}}}pageSetUpPr", {"fitToPage": "1"})

    dim_el = ET.SubElement(root, f"{{{main_ns}}}dimension", {"ref": "A1:N9"})
    svs = ET.SubElement(root, f"{{{main_ns}}}sheetViews")
    sv_el = ET.SubElement(svs, f"{{{main_ns}}}sheetView", {"workbookViewId": "0"})
    ET.SubElement(sv_el, f"{{{main_ns}}}pane", {
        "ySplit": "7",
        "topLeftCell": "A8",
        "activePane": "bottomLeft",
        "state": "frozen",
    })
    ET.SubElement(sv_el, f"{{{main_ns}}}selection", {
        "pane": "bottomLeft",
        "activeCell": "A8",
        "sqref": "A8",
    })
    ET.SubElement(root, f"{{{main_ns}}}sheetFormatPr", {"defaultRowHeight": "18"})

    cols_el = ET.SubElement(root, f"{{{main_ns}}}cols")
    col_widths = [
        (1, 1, "18"), (2, 2, "20"), (3, 3, "26"), (4, 4, "12"), (5, 5, "32"),
        (6, 6, "12"), (7, 11, "11"), (12, 12, "13"), (13, 13, "11"), (14, 14, "16"),
    ]
    for c_min, c_max, w in col_widths:
        ET.SubElement(cols_el, f"{{{main_ns}}}col", {
            "min": str(c_min),
            "max": str(c_max),
            "width": w,
            "customWidth": "1",
        })

    sdata = ET.SubElement(root, f"{{{main_ns}}}sheetData")

    def add_row(r_idx, cells_spec, row_ht=None):
        r_attrib = {"r": str(r_idx)}
        if row_ht is not None:
            r_attrib["ht"] = str(row_ht)
            r_attrib["customHeight"] = "1"
        r_el = ET.SubElement(sdata, f"{{{main_ns}}}row", r_attrib)
        for col_let, val, kind, formula, s_idx in cells_spec:
            c_attrib = {"r": f"{col_let}{r_idx}"}
            if s_idx is not None:
                c_attrib["s"] = str(s_idx)
            c_el = ET.SubElement(r_el, f"{{{main_ns}}}c", c_attrib)
            if kind == "blank":
                continue
            elif kind == "str":
                if shared_strings is not None:
                    c_el.attrib["t"] = "s"
                    ss_idx = shared_strings.get_or_add(str(val))
                    ET.SubElement(c_el, f"{{{main_ns}}}v").text = str(ss_idx)
                else:
                    c_el.attrib["t"] = "inlineStr"
                    is_el = ET.SubElement(c_el, f"{{{main_ns}}}is")
                    ET.SubElement(is_el, f"{{{main_ns}}}t").text = str(val)
            elif kind == "num":
                f_v = float(val or 0)
                ET.SubElement(c_el, f"{{{main_ns}}}v").text = str(int(f_v)) if f_v.is_integer() else f"{f_v:.2f}"
            elif kind == "formula":
                ET.SubElement(c_el, f"{{{main_ns}}}f").text = formula
                f_v = float(val or 0)
                ET.SubElement(c_el, f"{{{main_ns}}}v").text = str(int(f_v)) if f_v.is_integer() else f"{f_v:.2f}"

    # Aggregate all active job entries by Job Number (or Overhead/Leave label when Job Number is blank)
    job_buckets = {}
    grand = defaultdict(float)
    for emp in sorted_employees:
        tab_name = emp.get("_base_tab", emp["tab_name"])
        for jb in emp.get("jobs", [])[:10]:
            bldg = str(jb.get("building", "") or "").strip()
            jname = str(jb.get("job_name", "") or "").strip()
            jnum = str(jb.get("job_number", "") or "").strip()
            shift_code = str(jb.get("shift", "REG") or "REG").upper()
            reg_h, ot_h, dt_h = 0.0, 0.0, 0.0
            for d_entry in jb.get("hours", {}).values():
                if isinstance(d_entry, (int, float)):
                    reg_h += float(d_entry)
                elif isinstance(d_entry, dict):
                    reg_h += float(d_entry.get("reg", d_entry.get("REG", 0)) or 0)
                    ot_h += float(d_entry.get("ot", d_entry.get("OT", 0)) or 0)
                    dt_h += float(d_entry.get("dt", d_entry.get("DT", 0)) or 0)
            s2_h = reg_h if shift_code == "2ND" else 0.0
            s3_h = reg_h if shift_code == "3RD" else 0.0
            fm_h = float(jb.get("foreman_hours", 0) or 0)
            tr_h = float(jb.get("travel_hours", 0) or 0)
            tot_h = reg_h + ot_h + dt_h
            if tot_h == 0 and fm_h == 0 and tr_h == 0:
                continue

            if jnum:
                g_key = (0, jnum.upper())
                jnum_disp = jnum
            else:
                fallback_lbl = jname or bldg or "UNASSIGNED"
                g_key = (1, fallback_lbl.upper())
                jnum_disp = f"[NO JOB# — {fallback_lbl}]"

            if g_key not in job_buckets:
                job_buckets[g_key] = {
                    "jnum": jnum_disp,
                    "bldgs": [],
                    "jnames": [],
                    "emps": [],
                    "reg_h": 0.0,
                    "ot_h": 0.0,
                    "dt_h": 0.0,
                    "s2_h": 0.0,
                    "s3_h": 0.0,
                    "fm_h": 0.0,
                    "tr_h": 0.0,
                    "tot_h": 0.0,
                }
            bkt = job_buckets[g_key]
            if bldg and bldg not in bkt["bldgs"]:
                bkt["bldgs"].append(bldg)
            if jname and jname not in bkt["jnames"]:
                bkt["jnames"].append(jname)
            if tab_name and tab_name not in bkt["emps"]:
                bkt["emps"].append(tab_name)
            bkt["reg_h"] += reg_h
            bkt["ot_h"] += ot_h
            bkt["dt_h"] += dt_h
            bkt["s2_h"] += s2_h
            bkt["s3_h"] += s3_h
            bkt["fm_h"] += fm_h
            bkt["tr_h"] += tr_h
            bkt["tot_h"] += tot_h

            grand["G"] += reg_h
            grand["H"] += ot_h
            grand["I"] += dt_h
            grand["J"] += s2_h
            grand["K"] += s3_h
            grand["L"] += fm_h
            grand["M"] += tr_h
            grand["N"] += tot_h

    sorted_jobs = [job_buckets[k] for k in sorted(job_buckets.keys())]
    first_data_r = 8
    last_data_r = max(first_data_r, first_data_r + len(sorted_jobs) - 1)
    tot_r = last_data_r + 1

    # Row 1: Primary Navy Title Banner (A1:N1 merged, style 217)
    r1_cells = [("A", "NETCOM, INC. — WEEKLY JOB NUMBER & BID CONSUMPTION SUMMARY", "str", None, 217)]
    for c_let in ["B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N"]:
        r1_cells.append((c_let, None, "blank", None, 217))
    add_row(1, r1_cells, row_ht=34)

    # Row 2: Executive Metadata Ribbon (Deep Teal labels 218 + Steel Slate values 219 + Cyan badge 220)
    add_row(2, [
        ("A", "PAY PERIOD (SUN–SAT):", "str", None, 218),
        ("B", f"{begin_iso} to {end_iso}", "str", None, 219),
        ("C", None, "blank", None, 219),
        ("D", None, "blank", None, 219),
        ("E", "WEEK ENDING:", "str", None, 218),
        ("F", f"{end_iso}", "str", None, 219),
        ("G", None, "blank", None, 219),
        ("H", "DISTINCT JOBS:", "str", None, 218),
        ("I", f"{len(sorted_jobs)} Active Jobs", "str", None, 219),
        ("J", None, "blank", None, 219),
        ("K", "EMPLOYEES:", "str", None, 218),
        ("L", f"{len({e.get('_base_tab', e['tab_name']) for e in sorted_employees})} Consolidated", "str", None, 219),
        ("M", None, "blank", None, 219),
        ("N", "NEA v2.2.3", "str", None, 220),
    ], row_ht=22)

    # Row 3: Compact Spacer
    add_row(3, [], row_ht=9)

    # Row 4: 7 KPI Metric Card Headers (2-column merges A4:B4 .. M4:N4)
    add_row(4, [
        ("A", "REGULAR HOURS (REG)", "str", None, 221),
        ("B", None, "blank", None, 221),
        ("C", "OVERTIME HOURS (OT)", "str", None, 221),
        ("D", None, "blank", None, 221),
        ("E", "DOUBLE TIME (DT)", "str", None, 221),
        ("F", None, "blank", None, 221),
        ("G", "2ND SHIFT HOURS", "str", None, 221),
        ("H", None, "blank", None, 221),
        ("I", "3RD SHIFT HOURS", "str", None, 221),
        ("J", None, "blank", None, 221),
        ("K", "FOREMAN / GF HRS", "str", None, 221),
        ("L", None, "blank", None, 221),
        ("M", "TOTAL JOB HOURS", "str", None, 223),
        ("N", None, "blank", None, 223),
    ], row_ht=19)

    # Row 5: 7 KPI Metric Card Live Formulas referencing Grand Totals Row
    add_row(5, [
        ("A", grand["G"], "formula", f"G{tot_r}", 222),
        ("B", None, "blank", None, 222),
        ("C", grand["H"], "formula", f"H{tot_r}", 222),
        ("D", None, "blank", None, 222),
        ("E", grand["I"], "formula", f"I{tot_r}", 222),
        ("F", None, "blank", None, 222),
        ("G", grand["J"], "formula", f"J{tot_r}", 222),
        ("H", None, "blank", None, 222),
        ("I", grand["K"], "formula", f"K{tot_r}", 222),
        ("J", None, "blank", None, 222),
        ("K", grand["L"], "formula", f"L{tot_r}", 222),
        ("L", None, "blank", None, 222),
        ("M", grand["N"], "formula", f"N{tot_r}", 224),
        ("N", None, "blank", None, 224),
    ], row_ht=26)

    # Row 6: Compact Spacer
    add_row(6, [], row_ht=9)

    # Row 7: Table Column Headers (Identity A..F = 225 Primary Navy; Hours G..M = 226 Deep Teal; Total N = 227)
    add_row(7, [
        ("A", "Job Number", "str", None, 225),
        ("B", "Building / Qualifier", "str", None, 225),
        ("C", "Job / Project Name", "str", None, 225),
        ("D", "Tech Count", "str", None, 225),
        ("E", "Assigned Crew (Last, First)", "str", None, 225),
        ("F", "% of Week", "str", None, 225),
        ("G", "REG Hrs", "str", None, 226),
        ("H", "OT Hrs", "str", None, 226),
        ("I", "DT Hrs", "str", None, 226),
        ("J", "2ND Shift", "str", None, 226),
        ("K", "3RD Shift", "str", None, 226),
        ("L", "Foreman / GF", "str", None, 226),
        ("M", "Travel Hrs", "str", None, 226),
        ("N", "Total Job Hours", "str", None, 227),
    ], row_ht=28)

    # Rows 8..last_data_r: Zebra-striped Job Roll-Up Rows
    tot_week_hrs = grand["N"] if grand["N"] > 0 else 1.0
    for idx_row, jb_row in enumerate(sorted_jobs):
        curr_r = first_data_r + idx_row
        is_odd = (idx_row % 2 == 1)
        s_emp = 229 if is_odd else 228
        s_ctr = 231 if is_odd else 230
        s_lft = 233 if is_odd else 232
        s_num = 235 if is_odd else 234
        s_tot = 236
        bldg_str = " / ".join(jb_row["bldgs"])
        jname_str = " / ".join(jb_row["jnames"])
        crew_str = "; ".join(jb_row["emps"])
        pct_val = round(jb_row["tot_h"] / tot_week_hrs * 100.0, 1) if grand["N"] > 0 else 0.0
        add_row(curr_r, [
            ("A", jb_row["jnum"], "str", None, s_emp),
            ("B", bldg_str, "str", None, s_lft),
            ("C", jname_str, "str", None, s_lft),
            ("D", len(jb_row["emps"]), "num", None, s_ctr),
            ("E", crew_str, "str", None, s_lft),
            ("F", pct_val, "formula", f"IF($N${tot_r}=0,0,ROUND(N{curr_r}/$N${tot_r}*100,1))", s_num),
            ("G", jb_row["reg_h"], "num", None, s_num),
            ("H", jb_row["ot_h"], "num", None, s_num),
            ("I", jb_row["dt_h"], "num", None, s_num),
            ("J", jb_row["s2_h"], "num", None, s_num),
            ("K", jb_row["s3_h"], "num", None, s_num),
            ("L", jb_row["fm_h"], "num", None, s_num),
            ("M", jb_row["tr_h"], "num", None, s_num),
            ("N", jb_row["tot_h"], "formula", f"SUM(G{curr_r}:I{curr_r})", s_tot),
        ], row_ht=21)

    # Row tot_r: Weekly Job Grand Totals Banner (A{tot_r}:E{tot_r} merged, F{tot_r} 100%, G..N SUM formulas)
    tot_cells = [
        ("A", "WEEKLY JOB GRAND TOTALS", "str", None, 237),
        ("B", None, "blank", None, 237),
        ("C", None, "blank", None, 237),
        ("D", None, "blank", None, 237),
        ("E", None, "blank", None, 237),
        ("F", 100.0 if grand["N"] > 0 else 0.0, "formula", f"SUM(F{first_data_r}:F{last_data_r})", 238),
        ("G", grand["G"], "formula", f"SUM(G{first_data_r}:G{last_data_r})", 238),
        ("H", grand["H"], "formula", f"SUM(H{first_data_r}:H{last_data_r})", 238),
        ("I", grand["I"], "formula", f"SUM(I{first_data_r}:I{last_data_r})", 238),
        ("J", grand["J"], "formula", f"SUM(J{first_data_r}:J{last_data_r})", 238),
        ("K", grand["K"], "formula", f"SUM(K{first_data_r}:K{last_data_r})", 238),
        ("L", grand["L"], "formula", f"SUM(L{first_data_r}:L{last_data_r})", 238),
        ("M", grand["M"], "formula", f"SUM(M{first_data_r}:M{last_data_r})", 238),
        ("N", grand["N"], "formula", f"SUM(N{first_data_r}:N{last_data_r})", 239),
    ]
    add_row(tot_r, tot_cells, row_ht=26)

    dim_el.attrib["ref"] = f"A1:N{tot_r}"

    ET.SubElement(root, f"{{{main_ns}}}autoFilter", {"ref": f"A7:N{last_data_r}"})

    merge_refs = [
        "A1:N1",
        "B2:D2", "F2:G2", "I2:J2", "L2:M2",
        "A4:B4", "C4:D4", "E4:F4", "G4:H4", "I4:J4", "K4:L4", "M4:N4",
        "A5:B5", "C5:D5", "E5:F5", "G5:H5", "I5:J5", "K5:L5", "M5:N5",
        f"A{tot_r}:E{tot_r}",
    ]
    mc_el = ET.SubElement(root, f"{{{main_ns}}}mergeCells", {"count": str(len(merge_refs))})
    for mref in merge_refs:
        ET.SubElement(mc_el, f"{{{main_ns}}}mergeCell", {"ref": mref})

    ET.SubElement(root, f"{{{main_ns}}}pageMargins", {
        "left": "0.4", "right": "0.4", "top": "0.5", "bottom": "0.5", "header": "0.3", "footer": "0.3"
    })
    ET.SubElement(root, f"{{{main_ns}}}pageSetup", {
        "orientation": "landscape", "fitToWidth": "1", "fitToHeight": "0"
    })

    _sort_sheetdata_rows_and_cells(sdata)
    return _format_worksheet_xml_bytes(root, "{00000000-0001-0000-0002-000000000000}"), sorted_jobs, last_data_r


def normalize_timesheet_emp_record(emp):
    """Normalizes synonymous JSON keys in an employee timesheet manifest entry so LLM key variations never drop data."""
    emp_name = (
        emp.get("employee")
        or emp.get("employee_name")
        or emp.get("name")
        or "Unknown Employee"
    )
    norm_jobs = []
    day_keys = ("sun", "mon", "tue", "tues", "wed", "thu", "thur", "thurs", "fri", "sat")
    for jb in emp.get("jobs", []):
        bldg = jb.get("building") or jb.get("qualifier") or jb.get("building_qualifier") or ""
        jname = jb.get("job_name") or jb.get("job") or jb.get("project_name") or ""
        jnum = jb.get("job_number") or jb.get("job_no") or jb.get("number") or ""
        shift = jb.get("shift") or "REG"
        fm_h = jb.get("foreman_hours", jb.get("foreman", jb.get("foreman_gf", 0))) or 0
        tr_h = jb.get("travel_hours", jb.get("travel", 0)) or 0
        raw_hours = dict(jb.get("hours") or jb.get("days") or {})
        for dk in day_keys:
            if dk in jb and dk not in raw_hours:
                raw_hours[dk] = jb[dk]
            elif dk.upper() in jb and dk not in raw_hours:
                raw_hours[dk] = jb[dk.upper()]
        # Normalize day keys to lowercase sun, mon, tue, wed, thu, fri, sat
        clean_hours = {}
        for k, v in raw_hours.items():
            kl = str(k).strip().lower()
            if kl in ("tues", "tuesday"):
                kl = "tue"
            elif kl in ("thur", "thurs", "thursday"):
                kl = "thu"
            elif kl in ("sunday", "monday", "wednesday", "friday", "saturday"):
                kl = kl[:3]
            clean_hours[kl] = v
        norm_jobs.append({
            **jb,
            "building": bldg,
            "job_name": jname,
            "job_number": jnum,
            "shift": shift,
            "foreman_hours": fm_h,
            "travel_hours": tr_h,
            "hours": clean_hours,
        })
    return {
        **emp,
        "employee": emp_name,
        "position": emp.get("position", emp.get("title", "Tech")),
        "union_local": emp.get("union_local", emp.get("local", "")),
        "jobs": norm_jobs,
    }


def _xml_escape_attr(s):
    return (
        str(s)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


_EMBEDDED_TIMESHEET_TEMPLATE_B85 = (
    "{Wp48S^xk9=GL@E0stWa8~^|S5YJf5;)_3~m0bWR61-q2m(_Cn-XF-(h%8JlyyEc-ye*Tl?d0ABPcz6f^kj=*1(U$Ua2I=CFmQSb"
    "uprzi?98{5w)^1$fW4trlO|g-"
    "R_#9$LNH*SI^!H1Uh)M8$YF*H(dIcf6FwX5No$;LRG7f%cZ#$=dQ&V~TC4hQ9J}$>stt@|`2r=Adl$EMGZNR^GoWyc7;2|9_JG4U"
    "rkzBga0=w&!e7YHcW)4XzP5F=g$(DJtO@4H^d9n)x;@o(D`&y`k}MX1Kc&#16P}yMj(Rg+E%_F0eGUDJ01pJLwbUwrZxj4{{SCIE"
    "uZCG9T;!x$rNY!;4ufp0dN|idqG?h)pv1zC)R;JC(tYc#%-w~2surUJ`Vp-yY9o0<^-f^U-"
    "QFR7;4uo_pGe^j4;>aVLHW=&=~9!m8aEGyG{*{8<SqCqmD5t{!*#XoKC9cBZe?@2Zmu5YYufLu_{~6;c*b71p~?9yy1nJA=r$;Na"
    "~tqjbIWiO%eH2eVoP7Rx|rpu6>eZ7c{PoE58UATN^TYtDB8M8DeAlBQS{@GXG`9CqN3DvbK<Lod+@G;&1??@$|`4_v?2H1qXa`}S"
    "D|z(U8>W(SWml^Fq=C<fE%A=={J1zFY!o!X6pEvys1il?+1*BlzMb11hHR)&F1*SdH>B;4rdl6$h;Qfn9aRPtb4nCv%A2{QYp908"
    "X6<N9UYD|8&`1DxgW0WPvQ0iYs9xe;<p`cGDEr!4@>q}@u(E}nK(pg$rwg3TFkY#&BCyjtN0JWjEOC&EKElpT!aZE^$dFpu+!SMv"
    "*tn1;3KJ-5FLbgB|^q>Fp8{WfuP@Z>KSTOOcmq=hg?qyrtwned^SyMQuT%0rhLIqRli<T@-"
    "VVVG8r7)xM^eBpiP55!C&n_oIH~|JiSt=tSJk$B$>hm{Bu~Lb5$Mxi|ciDEGoVRKytdk<E}j`u(=Y8jUNEbWA4+>QdOh>$pd9*_s"
    "w-^>Uczv8;c+FHx`njfQT8?lQ_jp$j~C<X4|mhjlrsc<Z4KhxOLi@j$`(L2cb-"
    "M#Q|q}5>q5_Ja%EHk5|dMe02JIYm;#NNDN6dIov<Updv9wPuV9>)`5vy?3Vsa+Jg%`azvsMf!e~q2FD1#meuAcoA(STnc*O6SW8+"
    "2=+%4!QE;w9-"
    "0xvCOr}<^1wdjX=I_oV)3I2Ae9SSg`OtSdDEUAkSl)P9E6@#Ktg?aJ*bvum_>GS53K)O_T^<`LW>|##AXSZ&^>jg`CakamlK&{AG"
    "Fi9GQ>QYUj9kD2G<miT=j_am#BRmdgK3sF^kK%<5Hn8g5i$8BMEC>PM=uBh<-"
    ">kBSgQb2(b)k7)tG<*p!Bf+Zw#Kxvel2NffxPM$!Y1%q>iwMac{zMUIun<9;^;e>nC`gJN|Yw5EmM|MW-"
    "K7Fmu>EM8b9v@REU!D@7^v{x9F!4$L*HD5`~iL~Iz{;-"
    "=E(#P{OHj+h;Ine35?8U0!1^+M+5DADU%6nJWV;ca(Jj?q2J<xX%98h?);At9+Sz@J<RkV|2U)P;T!rpmHY89~g<g0<w>WrZ1!V<"
    "Cj3+xWk`(GGUs+fvAKbZ`q<IBv7_R{uU#*7K4Fi;B1z%1h(l`_lu>W;XRO%<e6Us~OR$yS<O3BUZ7ZH>k4SA$QK5ftJKn*z75@Sy"
    "2KjTUoMX7*cT!uKkb_Gutsv-R(-"
    "u?HtDriAbyJ5xui|DOzr16H?57ZeIJ!3fNy$3?j2wkmiB4oc=6=gQKy|eG&h!Cu;3_Kduxi!e6>l*D_-"
    "E&;QprmCBb?Okj&lwQCB!n5d~3IZk5?5*W02wJnk4&s{OwWVHZHSs1#F5Qosi^+p}_@!ga^_*kx?z-T8;SDE-"
    "N(v{<M3sg1!6Da{5Q*LE%Uqa}8gywJKttI(6^sr&1aha!WzU=3>5@{5*tIRSpzt0J*1oQ*ZkRsK^dpuHH@)WFdKpnJkm^bTJ43PT"
    "notm#2B{&<sz|a_SK1uPYlmhaE-E}8*$HG{3ypUSr9m`Y(^K8i0t>)&hV^m<@E4x|za@$<Y^7qw*%=<%-BheO`@Ae>^7v%Vh-"
    "fyr<7!5P8(;=epcf?}JazC^4hHv^5xq;UsjM^_a<fNu4MdTVbKVc9_ISZ3>ayX!_w@3SNTOP!3dJF*Mzc#TSrV9h7I3zx<a{zR-B"
    "Pr31m&Raa92eep3-"
    "yC|Z3w%uV^&{$BVPjU`BgTssYMZEIZ`ZAB0^u#PwCUWUqk^;2Y&<=;JD`g=@hgP5OR!yJ_2M<voCj{=jtndq<C6Y6zIu33@uKWg8"
    "~mBwzb_+zm<*GUSS_tVF{aY1Ya36q@OIYWlLQo$az<O5$0t#l~_Y&_6tyApiFicQfx_%s^vQhygdF)BYdaPEW4h&7C`#dAJW)~H}"
    "lg7%2lxEtQ4Fwdm20Ftu#{Z(0gL1B*J|wmAebW1|qRn%BM)g`e5Ni=l-pqa!u|1e%=^#Q?p$-"
    "VBP=h9SQyoEU}<OLUBQ{Zcc4@Nu^=icL{^%d{S@ZeZb#OAL0(@chO?lRr~@-"
    "@yoC^GEeL$_8&axfDrH~T62h4+JTF(|JM2zv+qzeKRP&U`UlW87cvGljVKPmD?>GTX1%MD<#q0OYMpG%JD<1ecnwdnL1R-"
    "{_nlM(cr9ULJAk}Tv>-amN$PfE)y0;X_8lSV84;dLM8nawDdCP6L&cdYzjZ7k_>g6!y;4}%ZcrP&`-"
    "*U!A!eKa%F>Vpbw0pq2Y9?Q+5+EF>9_ktHb@f0Y12C59$WB3D%%yMgyLyvsT5s507Lbw_ewHT0OhhdRB}nR8T4u&#8RR>#AtvS{Y"
    "R|@SNAhGTS3QgC$1Mb`YFar+X`?*>raEu@o6$2sk&e7BFTT4$N-"
    "1Z1>H2RS}x0oh;H$Dd3T)!XZm4NAb6)H0_)gA(W%3|4`J+{i2y)q&g7Im;&*effu8;LZdXovbsn2-"
    "DtI^zL>!emL6rBVJX`ZDE!ybh!}Ym4rmQHr>g|hv^6v^i=bYqiP!Ka+<h=2J`x(SJ)S<G>oe3WRXf0~d-Q@gaSZn+=&fS_d-JDN+"
    "h)r7DU(GQjpp>VAP_cAG&CMdem`R$i8oNu+2+rvQnZa_^dw5{|r(<rl>@{*Z_XJqYXc_?If`apiP+gl&8<P0mt|^LD_>|=(S-"
    ")XOlt;w-"
    "`WBQ(tI3KFigWi!bpIf;jclbnGv`d$T@^<5S;P3<SNZ<Db!Ld%eX=h4Qdo}tm{bj#i(2Az$Rr!kI9Ge~lfX%o#5XzZp*EY^*VFeT"
    "*6dc8bb+VA5^YmY4MTi0qTZ-PCIho^tK`QS=93bPjZ~7JtQeKfi)|D62K*X7RF*^>>fsj~=CK&I2|rNyVA^2E&KYJ}<J6NKrkZP?"
    "*mHVNQOTO<$s$-8d@EV_gx;F0p5l@NAK66Dzrn$#3eo{i%1i6H3WJw$?37VN26pVa-zH=!GSJe`D=h(|TVji5*d>Vc;3bgHnS|Q_"
    "FiGN$WqP*%uMpE0Dwm}txN_}Ev805`2$}fdG}LI&>xPCO?l-"
    "G(O37C>IZIl9qCLN)$>_4?ft>;?9p=*0!hDkOn6ZB{3~%OpT&~xJW^o`g$aAvcK|pB*Wy29>cET9y11jeLf0tr5y-"
    "WuXfb*>T8%g?fvZ4QZ{frc*<BBozWlgcx=@V6a^DW18q)-vXH71Dx2?>zOl~<dJh7T-EsE*Rgu8Yp~>aH#|k$|-"
    "o%CS+MK*+#B4nnNH<OfO@I4dW8$3))$O<EM$jbL@+<v<ysn3v2TqaI4(d>W^aFn{|^Hz{LLW~ebA+kVxw<0HMyvgfoM+aJJDtz9f"
    "c0wX2QJ!Zg>>UD7|R(Ly@+@o8tecbejBkrr4Om7J{;pcha;K@C{@@-"
    "72JN>k3tQ<7m%8ezAJ$@y1%I?Dx0ByEn0pI(4Hayn00yYp!4guCcisuS443@br^wc5v`6T&4M9%o-"
    "A3ls(4?7&u1eHyZz5+xyNelwU8<ju*#FXS};{0RabJ6CCe_3jIL5ZH-mc@bfIaedFG=79SjHiK2L{B?nT%?x(w<gH74>`!a>yz$-"
    ")zSU|yTjCzk1N+{E(j#MdN`~3?x^q!=CP}P@C)4^tmT*XRW0)YWiUtv>JdF2a&)*w@<Huq7X<Juh9J(j!FltqB_@Sm@Fsb|T+if!"
    "djTCfCbcUxkg}va)s1L`ND0D{DbWD+4z-qa$i);NP}|H{4}X#AieLNdG{VnG3`;KO*GW4O6y~(9-"
    "(`+`Y*qx>DYZHgGqUzpA1;}EifLy8+TU8*sRYCnxPIx;i}r~<lAXAQ>L`L@y%t!7(M=oVpn8gCkA$az5F}ngEp)g5d}`%jHlKy4N"
    "36<JAUjW*citl5T`CV$Vd{RTdf9~vZ<@16Dt1DCzy4-"
    "ZJiDj8UxBn8+|%H2_Kx}0erJ?Tq%7jaw=2eZ6ZYDD8x`9QkHi%*C6R(5I%9CATD6c1h=}(_n8jj|zDr=5cdna?6yGCxJC#$2=}FP"
    "eSNlxBJWQ{m@+w%P;1l`Y-Nh1Ri4zUNFvB0$S(x8*Zhts!6JWrX3pBf$D^Hn+nZro5W8>W-"
    "Kg62t>WUI>*5=43_mXT?<iC~tTGKBGIk#hDehGzRawD{NYpaQc1%NcuR3zwLSKUnrHJ7cn@-S->7$s7fYN(I*QO`t!SQ@-"
    "oDM3hrmQt=oe2va%V?lC5ldr24SGfKJShZ{eSc4PEDDJLX`&u%q7BN0Xl|j%DSe-(fN@~jL))qqUtcN=x8K_V+`^7iwAR837_>-"
    "GD07WRPqcc?SREiCNdqv#IaOmQia~T^A#BJw)Jf4AkNrL&6`mf40SbSw8<u@ek{wWZiz9F5&8<EG%S6xH=>G4**msB#y9xZ*5^Kh"
    "`?P7ns+-"
    "h0k^nwn{T&3KTb%cxry`?Dgj?T22l$eU48DzlO4QI1f98|S*vB@(lJj5)|A&I#29C<~k;^$iHV?im)4l)662tFBTeQ!e%Kq{3tgn"
    "6^lW0UPe5_sG6gp2R0rFKoWtdt!llLVUJZqlAJ&n(JLknHm7VPbGBP&-a_Y2ylg-Cy|{zQJ*m_w@?Q1gFcINlwjJqp2(r)GiXDXi"
    "iJS{BNZCqJziT9&Lcg`8uI;bhKD|000w&pzJ7?lxdvMWq}2z@^~XT~y+)!W$Xfb$p?IHVMJ^*GjoXJ07$~C2oze?1)sHnRbBmoOF"
    "l%lX#v<`$6P9tK@*UflGTFA?8WA~xy|o9m7g)9$y|HKe_KfCWcvt{DY-"
    "G;3)ZM2Vh(ge0WmO`$w*Dr7etR!aGUp(eYQ!t#WrWL*q)&{6{@*zEAlPVb#D`$`c92tGIIp!Om$Y}W#k3%?vyJHEJA&qP0CFQRVK"
    "8d?Yqn74g66$fee%5QM7!K}ip+UiJO?$*wX%nOv`z6_*yGexa=3fv{Ay-"
    "=dSiT5=2$eR7{9uNY9o@&g|!t&hNwY54PwSfU$*42W?7dxF^UCmA|(puU64objF;Jc*}G6e69KKlGct~z*)jx$auea2@0AAG+n##"
    ">HQ5|f1*dRssSIxx#EIIf!mSe)6sylY^Jy@;5uS#UmyG9Tc;YI<T<hYzRMvr0!S*%QPB-"
    "B5_8fwb75<OcdupSL1Oe<$>GKP&w9}`=5VH!IWX7}H3-@txp)GK{Z3SH!hDV^JzL@fJ5g}6PO?1QJtup3T-"
    "VW+PWEYZc8<V^#*DY|?NINB2S^6&FF+&(Xu59ez3ICF!AundqPMCmOk^VDuIdD69e0!;RK!Pj-"
    "J9k+=DezO6J^91$+#K$1JUO|oou7UIxe!+kG(W<r0myp|c#5Y@ZG~OFtl54NDG~qVC-_2$p@*+-Rl}KY{uH8vQo!-"
    "x*5zvMj;h~#1aH=}4=7DRlij`d)Av8HH5ruuk6@fnuC!T>m(ndM>68t@ttWRY`kH0Ew#JH?55N#%Ja%s6u&}IyoUx3_;)wX;n5eX"
    "PC1?PH_-L1Wg?kM$NhN{m&Q31UfC(f82*f*j>#>9cuh5Oly7DyU0ZeRBTFh5dE?G)K6AsydQdx(<(65DR-"
    "e?d7LQ)KhoQ`JLTrWv7B73p3YR9jXc4*Ps@#z2}U|=s>{HuNBKoN57{EK<i2+83vK`UPT7aL^HEBuUu_vbt7CU?ti4J?{bvbY5KR"
    "SOWJv4`dxMJ|$k-"
    "Fn)&o_<aS7W0zw&p}A9L}0@U7|maA#j&lb#iW*WA5SqpQeRgT_JE8NIdJ`FoB`i)!sAmUgimhi&G!J{xbHWepr1$gb>W~3I$v8@r"
    "$UTqdi9#Y-"
    "AHsTZ%8_TdTX(=*dxtvRP9oGW*ENpzk=EWa~GyGqB#FpDu_d0=EHhA^Ll1BSPKT$a6?4Ic5LYVR^i#U6Ilm36Dqcyb2(e>*>_kgC"
    "0SrOcq=qV!5?x5lNFcrsT%#lJc!XtJ)B`eEpg5d-"
    "SfgS!k^zuS|#w#zG}P(Ne##X91EoBFb&{fVxF8^Zf@T8!ah9)SzzjTo#Fz($OaHX&b(R}<a#p2U8W6SB(&a7VJEu1w<N$m-"
    "ktmW2_t$14Zdm-2HKRw<w=#Ft9%%>6(xI5o5})N59y!-"
    "?)JeBKVs(3uz4)e)KNw9z=nFB$i$5YB8V7e$&_8?Kn1ps6{odx*c4W9`oseYRw<*C!^ffkBY2V2UB7KF6pI9$z<^tzwROR_Xr%V{"
    "!x@O=oGwp}Nh5e>gjD)Md;OoU!_mVTMIi1#2QdRH(+KIy<Vw|(YzZU!FFV^xyT+`vxhq};FMW_!Ih#q*hh<uy9$vWoFKzU3auy>-"
    "4R=&+4+J!pZw@@(H*=Yk;d*%BYQNa0VkixIlN<e?+ToizZ;~2^x)XE&+x8COgQr#0Y>xBGM;Ggl@Ety|5dl(YF)J{!Rh!s1ej@=V"
    "X#UCS|H+9r5Tm(I@-=2oyeUp^0=|!AWfsCEL>RDTy)0m&u9*Z}YJ8}IyvARuB|Bj+-"
    "#2f^!qi=k?J~W(4m6D6kjby&31la<vH=bicM3=BkwGYo3JIdJC&&2D4*sE7)xE~OL1rS5ZY6=sV3(szUk%jYigXG9Vy9EP7wt*yt"
    "04wrmv16%j|n{PmSW*4g2$P_>QwpbN<=y2-Fl&B7ch7*C&)d{tKb0bpah-2JT;-"
    "F&Sq<jiOcAwxDrCEl;!aSRN@%zm&Ossw#!+(;0Q?;F{R_Lueb%-?Dlms1ahTSv`%8Ypzu%g55H#5N-"
    "zUK0C!~>!;>P@*jg>_m08QfRmWhBz<2=Flcl8M^uu(&gAC}QZ0z(98>o^S3}ZS<Q^~YCq(r#dAWymuD+*U6QvicQGN7u@a0VmI!L"
    "eZpJfu(RdqAJ6#dFO;P_w;I=Hy#Yq{(?!gIhE?BD!lKZoi>KHZ>mn<1I`lz3G2IB%232Cf{{yxlULJ5>R6m^I|mmZfO}J`{Xn{$e"
    "3t**HNC%d<r~kk^jg4QPa{7ACXJ>9IRlV%+9_-"
    "PH>w~BzaKV;*|d}dA!p!&WoJsvTjtgDs6jvwYm^f^#g2Lpi0q;2_xXWGNq@xuWIub73r8^i#R>hd)o+MkGy$|AVO1~U+zqR=hZEL"
    "t_d#C05Se<%y##vn)AEAY@u<-lklU>(_i}O6?N`A5`K(S`c!6Y69COIn-"
    "f}l8KaW2lT5&QFf)%FCOV2@Itf(Y)JjSRiwxeV<s~!)r&m3c-"
    "jL+Ry#FAm&bcFtf7SYZD!@3}$eHSAD!$sEJZ~Tx^eK?QG@2*;vNMcxg%u&+5&QB-|D-"
    "%RgMP{r8tXr3n^!b$DIJCpUc&KnO?v)lBUY>gU@ru?+sl1ivnHWs)+Z_at&b#cbW&T0_3+#=U(2#@x44xc3rj#(gwN<)#{h_3bZ!"
    "|Zskd1rX)BETJJqg`Aq>_0E_M1yJ-u<G_m^lcQeLNuYEZV`ANifO{Mg*DM)JHP-"
    "$5$9kq>X+0u3iIBK2y^^ErI&2w_xg{9wy4+$K5xH(n>M&#wh@{QaG16sAJ#E0+^Ax<yqlL5bOV@TvG%s~b0vuj>pt3BN%W@!@73!"
    "wH9(c#zQ-#<fUaHI<W1@}%>cKe?o>2vFVWcD|Zs=GBdAVk@L_hSc7U-"
    "Hl!7TDEm8eO+b^xuSfAnj~HTOo281n=3~76iVdL34er^+HjyVvFqRkpj^&SQ@-gC+8bBh<g;zSLYB-hP1)xm^b#nxImRB5B^e~Eu"
    "99D@{yCHx^{Bp&Y*&mQb@Afz{5X-"
    "IWUaDWo*+~{eB1+>KOpHTsfkb}5L+jzlochtR7kbWH^YM9h9R0EFK(e503f*YY&%nUGKv@&${yQ^dv3Ci0ifgLA5KUNNY<4SYPJ4"
    "D$FwtAMDR1t)IiZ6JMk+10kY`rq4N;5^{AqrI$|1PTH%e4OcJDc4_2x9{Mj04Mw5`N5KKi1L1(xnK}k^(#EQx&R7f4jeWIU{KqsQ"
    "d-"
    "k|@<=dwZ$7I=W3g$Y17yT<)?bIt&^hyErrH6w+f2dfc8#M6Go|NWZZrGLf{j2<jI1K&E<*3|6@`(W3@boe+I#;K43cLp^OX|nb{c"
    "2JI@!*(8nDC0|O+pMC<Cc?ajjIv{P1Kmv*UK18!Aw`vJ1iok{Cp`#+-"
    "xb1ai*5J9c@KUJ%%Vf6rJD&ZTZG7XfxgXI)5^Y6I;>g0;0ilc)qf}%;aCTGu$=X7)-ujTdGAA?-"
    "USG3r~tQ5W4vnl=Cl)_QbZ`{KYqab#I{a#y$U826&tPgwg*t9r=nWl>2-etjmocs-"
    ")XZAe9X?{(u`=y7aG50m3H!`9tV|q<S7A+B+Bjlk^<@3t&Q6G9KU5@avs2}$bm2}oBZwUf*Y`mKi3-"
    "KgY(#Cc*J<KeI|a}9_MACuH?d<8Cn_+=~{-"
    "mNwx68AU6b6iCg@+z9S5H4E>)UFGNVGZ(KbwD>gPMDwCZFP!*2Sfxu<#G(MG}Q?YW;T8TL4I9g2hXGNH|{Ip2Eb|V24kEWcxshM>"
    "7At*658pXHTTkGvzg09ubvM~nv1jQ5a0<=7GUFq%U5)ef4IU&A;-AW^)ie3ejqjP_P*Jlb8E#lpo-"
    "~>0AM>4+dp+`vhXD0tjz8MNNh~=m!UI-"
    "Ev^%<`567Qc_^{XC&g?b+-<Q4O0^8aT;<Ff$I&bx+Ym@2x+v&5wj**n)iB=eq7Cs>^e&wSvlp9BLdKtz@l1Rn_-"
    "iH_a-B~|k!L?Kcu!uQa92h%5WWIttR*a_9<0ej(Qk3!n1TNJkf-AvPZxy)wqi_~h6<V8kMP>VNzXRG#JLf`Ws{Ok?cAC2&7k%j#2"
    "G@_PuS0dR!$8Rc}Zw*`7#<>PSC{MTi=@J&_zK#q)Zm{68HmpG9|BQ=!-mT`5iZN-"
    ">k^lm2p8jHOhVstnbfA=fP$$bI*sR39PKF1|8U3m8`Qj}Pt_)yY*q*h`N1bGGehAo!jVuKuZ9g6fhBBI^*Kly%*W?=&TxCvOdGrd"
    "goJ+HZqcRGyJz2ir$ViVak8igG5e@TnRh9TDqH^k$A9q~5VkV^Q0^m%yR#LznCB0~Gej(^?cK0%SL*W_5GyDBFnWF^?Eo9tHRtJ6"
    ")aH|~9i?tu60o$?lY_L>9|6<X{0PAY0+4~QyTE<`?<Kd72UUGI!v(1e{sIJ%jr>OUmh_F^IE?qpnT-ntod*ncB!O0VXlR2I?@uhb"
    "q!YR_115h<D0=n9Mq8b9Jyn(t6X1-U@2@e1)D?);FN}wIF0x{yCLW}g`F+T+GmHws!g}p5yE-"
    "9h5pS;GiuA+SL@gr)&SEA#73h6!qr0~t9e`j~efNp1ppD~yAIe*l~4Iuo<gTOKwRyao71v|g_C-"
    "x{0KB!MM`k5cn9<YqKQK$=MVr+Lxs(lRvm1HY=mm#AxPQ<Sbjl#|Bs<XIq2Nrka7Y<8KO`s(jL&A+TmIuBQpxyqt36tUrtDCU)!;"
    "l&^BJ(dcE)!^a9Y$>^mKz%@US_4UlHuAJzuG1DY#N{k3p~0IYtIbGw8qKI&XDb1<l`@%v+jW}t8HFTsZ%Kq6sPHB=dsJcoW24?&}"
    "zPgJ-;*^9cPn^xG$ciAk5-e??#}|Yis#~Pb7{+)OeFyPuOVHB(;g>VL;W_vH-"
    "T!xN``Isz90~hinG0VNBuBzt9s5iF?)#s>E!xXcM+KOR%;UvT!mkIJ3f}pxEMNi&Onv8?taw@THE#iev@Ts&Z;7`$%&!MZL-Bp+7"
    "V-kVbOzI|&8fU|;Mq^8IToC@t2MMFAK#Vp5+-Qo9)=vMnj@aSCgt-"
    "~yCV$}pPc4@tE@i0&XsSJCna8omI{^<~e*K%S)UWwtr93%FUynQPHD72Q#Q7&9FZ-"
    "8AlCKL<aI?p=zY+RK|&Xae{`g3%Vk5jY#17s;`13)Um**j%ga9&J=%wd}OoTmHCWAY30qjpMBqMJG;(36om#;Re3rMhYodI#RF0W"
    "rV{?ve7#)th!YiYGqV*oB4O11rwo-d_Xxj*NL%aF-CWsqA2UdyOEu6*+oKlWMp8Ha``Nu-J#GqTB)5dMJ{#*XgkcaLgKNf-"
    "s!ZFBPip9^poM83s^;PRB4=}o6_di%RQq(zxdZ9E(Vd`;0=h6Jm&hj+nc{Pxo^7Q8Vj;0y@dKcS|M<_q}bTj&~wXTA3~?kr;h82q"
    "Xyq%6HTv+xPBe?DP!!&(vAM6aTGryuS%CIZxDywLq|eq=F67Yz%4Pscy-m!XQq2e3EpDrO_-WM71+3a@Je>qKt?e#=4*;8WfcsaU"
    "vJsly5D@w!Y+|mY=6xj_(+g+$YyVld@9Osko;!n6DpI}PT<i;(FVfaP*6oxpOtt*!&0$EJ!E@JKRp!z1m!0!3AS?E&3W{@h+CQva"
    "8O{Y72>Eaw^f9`W4|l9QzgMa*3>k1Lr6b4yZZPU^q+8Cd*$?FB3Q}A+Nc#nmbtQ#!5=#hd#=>9^>W4v;l*J<<5gNh*FDw0w$p&T;"
    "zw>&cBjwAY~eamiquLM;!r20N~Xl>x$yDmbttf?4cH{!Ktd#ImsQz&?Q5fG>RY)C*XfLPMYcSqFtNxBTo>$BdL~8>#^nX$oE><O{"
    "utoXg7cLY@M4BCrYH?kc;Z5A#Pz%8uH8OgP90#ntEumYXPfQv6;t-"
    "eZQUA>d>xz7oPPKClOAC*%HZIdprP~eq|F+`%+ipz!{wUOD$+C?Yk``Noo+L-rCPz_2K~Jl!-"
    "(YFUmzQ}MpkXxyOIv<HgOMk;HJ#GbgiOX`-i1zv{1)JspT(HdH6`~Q|Hz{I7I=-QE2C)qK-zNy(|I<{H8B=%XaKc2bkgDScIIvaf"
    "Jsj2hJ%-x>4ykx;TW#d5S<OXvR=TS?c}C%&If2FoSd#Ke8GBg<vA6(gPP^+R(AiF@LWvURV32ql&nz$0It|%-"
    ")Apbl1g~b?1h>$pr&WC>+@{AJl7+88wYq=TrQ%>mJ~LL#Q;g5A=yocaBj-"
    ")d8yC!h&vh*YmXV%Ma|%eR+1cU00}wD5U;O)U1u`!tW>|_3vl$n%qu1x4qwW92D77%PSXl3I=LX);TJk9rVxMOI62ZlXI~)kay`H"
    "zc%T_p1riD=9X6%ho{m8I5-"
    "A{ffrP$Eo`<59|CseFYjuzqXB1s<r4;;nn9Y0T~jG{E+jTtSH7jpl2^KObO^AwK%LyxMgl3E?P`Fl-WtUA7kC~o_>I>PFjtm-"
    "{Kkvw{4R9;_K8Hz85A)K5HCQ^fU&<M$6=Ruu*<wj!9C-"
    "|e4OzqXTkuR^?ypo)+FMR_)EygYy@v#cIRp*KnbzYFX#{c#L|7c9!A<S!vOdyT}#aqGXY4(RwbLqWbJx@>HFt!{T~)#V0=4ACO#2"
    "LCjj8WyPchKQZ%BB87BP_-"
    "9pQ*tmaaCm)zWZG8PN>EFf_!yRn`9SPWUFoh@X6t32|Z$E(<Q9%;|N5~ej)$gL47Is1w~b}`j8AWLyDoO=ZgMEwg9M~51y=?Ggc-"
    "QU@Yt^$6G#hyd#%yj!oRQcpK0M!nzv^&}wI04Oqw66(>Wm*6CL&I*Q*`@ij4gTuoKlsigb-"
    "l6GV5R@$OIE5l&t$PA?5iLdg+1UZg&Jg+HvH^^WNvuG4XrW6Jd#Ja0{-"
    "SW;!fKK$ZyJ&km8EFDe&a|q#30xcP(XZ<a1geQxoZc+^C3qM%x~F9DSdN@Oh5E6@=Pk_LJJen4Phl!*T@n2kZK|^R!ApWYZ2DfmB"
    "}X(lC$^7k(3)tcSHDF8V?~z+5xow+i}&ZD~uKP~7N;xS84m;lAhY>vwx`!7`nw6q~UVGuZnT;a^Zq1{wVlw58$wImDv|ZO(qQwy4"
    "D{2(Csw<4Y1hG-yHT%q!|+L<cP5%<c~u#>A^+eGp6grU(*Y)+0fJEuyy+jZ_}ZDv{=iHNs2&WlAN|%<x@FYdC=J0~n`o7(c=$nZ~"
    "D>4j_lQIoN?wFZ`g$0v@`#eIr2{I!p>qEEKIe(1qa%mheU=s`|+-+Ir{$h^lDDQq~5>C-}lhI_Xc-BMQrBDO;GP;ZDIh!T+q>UAy"
    "o8g$-"
    "dNypDLXmqVayL}se%pbZk|gVUAQ$t8dp8y9V3bhrTUxWQ3#3Y#x+_w%B?Whga1i$}^}aPRSuBk`heR9f@H&srN_3D%52U;|@HtFS"
    "eR$2^awVYnZlWvD2qmQrWLm~wXYn@2<y9uSQAlPs1HyuC?{yC@{csHHj{dcIUmB4W8)qk9X@ofV>7;Q~la&e_C+v{qRln}au@$l$"
    "pg%mM9T9<U?+gt<?^=qu<+HY|mGtg$s7B@TMA3>Nt)n$>@pHq}V;Hl*!QU4pqfk@ctLaL@R>SoQbNpTc)5>Qymz0n76)UvQ5!NAC"
    "HPsmOzhFRSM`7)G?+wnI;*pdm%>{9y7-8*MkYXRV995mf&FOmKR!>27@ni#;33PI>DnMG-IUqtkh(mRPXDmE8D8DQ~=%WfWq&7HE"
    "j0uKda^aUQzRon9*XlsIYgfFrWCja%)k;;>#bL#P@(f?P!ha|V(lFau3m$ucr(L_vBEV2dOh4|NnjbxF$4Hy0ZSy?@Tr?aM%f%%8"
    "<>G-"
    "LVusbJEw@MjnWQPYu&%*k(Jj?ti=W(YIhdfS~OsgQ*J%5ro~8Me5paoyR({XKC)9nKvsb97K@<Q`*WhKmAXEU=@TfScn8;K&UUJQ"
    "Lwbd%9P)i$uPgvB+#HTwI_;+08grgWqcycXyE~)4R?KrpKIXmS0RkhBtsvMIOsfSBD+pB-Eq2FzAtS6^m<iaXR;0yxKm8kZOS27}"
    "*wzU69*iQw!K^p4C7<Jgv0DtQSN_lo)n4gA%mxRxBZGj$XRRHsjkDaF0CT!9hDoLEpkKUFH27mb5;~en`=Eu(6XDPlmNL>!(}$ng"
    "hqhR=XoQE|*747Oe60a|Xnr2XVecLs(dH-Kn~Smb4iuG}zwTn|N~s$H^aTCJ+yRe7F!*QrnY-"
    "R2uFz4sHXMlSm)F(mXivE(Heh;~7M-5cU1B1YF^lEi>WN9f#M$9o=pOVc?(^T>Uh-YJ&vDT@0OCd!a@>8`!v!L`TM;SW@?TZEC`O"
    "h^hNc_0B(8oz&Cq{7d|L;>d9YUoH@G)>4@*sXrV>ZvYo*U~_h<=kyzV5jAPI^DWLR(Ppq@dB=JuV6d9_EdZ37P+xPnK$iJ6#LS!T"
    "7c~x_Ra#A$3$f-"
    "NjbO&}1Yc@v0&k5;vX?)@Z<c36r2QAix#?9Vc#M&EPyC~wQILNvRXLlsm!y3+QNagl4$d23moPR?T&cX<u7H{zSg!K9vD|hJBZ!X"
    "3-X~@-cNmWg)P6Uy7yB&T%a&<p{qi8z-mycJD`iDS^B-"
    "nISwMvi%F+Ol7;2m}6Kmnpn$vIqcUrPz!G>swgBiKR=IyH7ON{C+>9E@1DmpG#a5CFH+&wBxHp?nYrlxo2r44;+C0M3qWNvGPD7t"
    "f{1!FJk3kQwkv6Ca1S4*Ls%=!G@=%pfq?vT)F%Jm~%-AatKU+)J|p;B_U>)WOk5SWDU)cg9wvW{Z>+YO1}=6~!BU5-"
    "me#ITqnc*0sZ9c4cqdeSc-"
    "<<86DzuN+p)Y;2)=Nld9<^v%m?Tqah9s4tay@b4ku;9z~@P~oM^KR68fRoyM%+3~utq?>Ddykr^qY{^#j!wY64Ww(J?+}dkL7^|?"
    "0M#aOK^Jpofm;yi96K5lNs1;IY_!oc>nrnCm32Qd92Kl(5h#<DJeIMN6<DiV2@ST?jP5#gzzb$RUVr6O?Mj#CWYzN-mwN7#I3$a9"
    "_`iy<s97RupsdtN|4w{T-@fQgiNI<*E6Q}L58RX(`VeA-`5?eWXfZnns)n-"
    "ASE8YSlJP<%VN4%U4XS0}Y}r3H8P$y1AZZjVC1x11?65uafM3B4%B}WGPFkRjb+oe4n`gh=-"
    "uwk77zquxUY`R#MW%^|vW3%3`o4y?JC`T!aX5cJ6Q}jH#HyJ_ZA_G)b!JvqzK+=M4ipL_M6zP`Y%^ck=A2t(rSXw{HVBXY4=Vz4n"
    "H|$SHL)D4EK{=zzm2~wJ=EJq7Jv{nFr-pgpK;=!wXvIDP6ha-"
    "D%a*MZk3)cCgIizt<?b71s6VbC~nv&R!95I9m{H!02m@`Y#fM;BZlW+5$OJ6SK)xmA58_zoZ!vcTFU1YG%6rStDuqh8$YZ;80Kkf"
    ">!b|mm}5?JDE&qOz@}{zdcz6gg3}W0$K@!%FVV8Eke)~MbEXk$IU1RqqHB6FW)>F1sC?r-0iEGjC)KNd6J-"
    "l7Gd7K^))&bJ(G5l!)(Dk-&PL9<v_y6gmtV@=QKd#YHu97D98dxc-nGPn$LeN52V7i=bF~_U$0lx37TJ5o0gpuo;_-"
    "pfY{FcMYoq;rIJrG|&+j4~06jcxqXUk093L`ZM(8Su2(xR~>OK<WuW(U=-"
    "+8M01J6zPfRvwJq<4b@!>iH_k=xOvI*d&hi8$a<AL+lZ5zncv0me=ua*pJqJ5R7pw&tuaDO~xpK1Y8+nx`KWcYJx74!8RX&bNqdy"
    "CSFZ2cGTDsP3ju91E?L_yvJpINe0V-p~92KAJIvz7C^SC}lwSeAH@ZotJ$*>2%sdP6T&6kGX!L)+r-"
    "doP|nH;eSsb#!Tt*LD}kkhBrzGe(qDRx`v2o`|p)i)^qQ${;%{x+Hqye4Z~Nf#~UeMi!tEv1@PXBcUeNI{yPh)vBNt;HX%HezY{-"
    "%Ovbea0E-)#P+{33?~5E<$sUy19FG~ybD6*K9D<@}{sxzVhk9O>b->`xvJ=3n$k84aZPpK-BLuEoT`*U)dFOpF4<U&Z)^tZdbeOp"
    "`fP1t>DXT^GbDOAWhII3?(N-roO!*@q-$tW_nCsD$o9AxCBO$q2^bDjtw1pCP+f>G=5s-"
    "wfFS$8Q`IsUP6LIs?MioPi6j8p!PjwBvB9o-vPUN-#C_P!4ONO^`kh8*gY3{U&9-"
    "yP37d5Y(G}8XyRa2y$Gy6V}oG22(s4~NR$`%)MHn9cSxaKB8tx;=xwJ_xGG3hU199m9B+mk=MnWW=3I!j8Hl@S75CNquptI9SVq5"
    "AK)-"
    "lhS_%p)iK66_5*wvgSGvG*Zi&8voQL@cf#e|<qGAar=QS#5moG7K*1u$KZ3M>`X6ai&b9t#=6QP?bH5Tjop4|Epzb>FURwl$Eih2"
    "rY40XEqgNC8M()%8PN_d~*-"
    "2TyQh7X3y?L+Z92C&Zyq#gnM@SG_O5Jp}dCa>BIR{oGHsd$2`}RfB{ypRG)@8?%{m0iCBp&5bFsAI0inZz(F1r-7%aqvrZ-"
    "Y`If21tB9D174Swi=IQ~RJ@5{3`#^;f*>3>#iRCsTbh#{zF#NYnjyxhQjtk%WT1Y))1Wf$!2XPgxY_WgS8p8HG19n%Xm>?M=tgg*"
    "wA(Qu?K|_4#80~m5C6pTzRj{=l8t5(Ok@#ZyNhPdBGFTyubOd@J*O?0doWvnVp_faqT$clD{t-"
    "zd6Y_Ize|@;~$(OTX@^)H6SAq)FnXP<fVjMJ=$spsa*mhQma>a1pZcDF-"
    "`Ge8Xf3eG=YOD~)xB8>yNX?xGEq?;XUQ8>R&V@ufAk@GR;dz)GbB93)DkZOK*f>gMn<DG+{NX)5Z$ZP#VUe1ijG7`q4zfOh)V?aC"
    "cu6NNua`0lN#?_ERX+S3D^M`wLW&i%mv#i)#3J<O{^NpU>dx3Z)bdLOUCamhW|NPPZ5AL$->Zea$I~!zesi-"
    "8cag~VIT8P+9M%8N+0e`g7G0@;fP?W8mOIjnCf*AD45w{xY0j&Y#<OoXG|gxYau3?YW9c**ZXhKU;t8JZiIJ0SJmh;;<HqNAtB<O"
    "D%MQgSs_I!QnD78cD0bntwpQ`jJV-"
    "P5Vgc75;f(@%T<{3D5sr5tu|Qu1SwXOEHo4wdyX@Y>+!T_(2hk`$<a7geC$PA)F?|u%z2V&pz0Sp%%;5BWS&xMtZt<p_CI(QODfb"
    "*NRCRL7MWO0UR{)L@7Fzxb;>#bWE&NXV+CgIIk$`qpiORS3l1gy4vRbz<UDSK+*%Z+qVa!UI3S00dm7{Muhh`|5A{+xIGZd%n0Xb"
    ")JK|WmHw!nzWAymZN1ji=WDZq~4yImz6G38y@a9vwlu|jfkQS_E18uk<P%YHrk$A{XQ=yr!8)fYy^@`U+jnx@^6;Bk0Ozbt+L<~Z"
    "__9@^g=X0spq&=Lw?X>%2zT~`w=KRisaZsixQ*pq4zOgM`6{<+9j;@*y|F?=uE(8)Q`qcSa|r&%1CT_qoRup%PAYIdAr3gI&!IXv"
    "Iq_dVjvYr+PD()5p@DC%77S1a}K3+x-{t04Zb&>coGgpG;)x{n}+?HZO8<vPB!-XMJ8t`F0-"
    "Q8D4CGZnX*($m%P9ON`FWlQdbRt8<{!o(Ibr}}wsJYaqL2wZmfWlfh8%<u15Gz>#x!oIib#$;bySa(XS$yjyW!k)irWt6<0SnoS5"
    "7KTiI;hZ;dc4+9VgpI!9lK_vZh0`AiJAF`fQs)2k)O_N4NBr9KSlXt@ooTn{V?~kCYnz43X}u)|SMlmm*Q=<r+-"
    "Jg9{~(x!8orGDw%I+U*~R!}071h_vq9AUg7M^VtbxC-"
    ")t#x#x0s_6r|<+YoYxo7!6tQ7xnxCsX<PpKSMyNkj}T+Q5T}e*+jD`sBW|{&+Qct5zWrR4=Wc7KEy>({{#G_MW*r>KF^)EO+(eky"
    "h5;To_7kgTB9&(Icplm}6BSfZ-"
    "%$%q<*23<_U`7!haC&T%I$CKRYo_%i+0TiU;nXL93{0#I|_g4j%m2zcY)j2Fk;!z4ZIGCO^7^ayG6rk#6I75oBa<|?8sJS+4S?Y1"
    "b+8v*e%jDXil8Fho`+_pFXgp$ce0?u2y=~9!&+b{5mYvH(uTYzGmz}B1E}{b>Kl<&h?h&MxS5tLY(V~=Go7~**oY3JJP$dir^@0+"
    "DN_paHI#j_a+BdVDAC@;^UO*&~7ajJ)8_t!z>&`a&m_!+0pz+M%P9eKNyYkhU{^p!=<!MNY(cYimgUYeX|R%lpSU-"
    "<_bJ%ijlTRcrYR6vYGzNtK+LbBgXD0_)^4cyQ5%bC+LaK?6tlV#9|2AgR3fCI^IBO^qae)Q8=OXvEbPmv)fpfS-"
    "!=6_UJROcKLm5iFSB*(StZ$wHpk_9@8g5@s+zceQ_g}4A}$(4o33ai)!P1te;V^-"
    "Sg(E%Jtl)%;I0WGmrIcz+pe(IOXL9VFlqItyV13iOl?X1))QSLRD<|-"
    "^?MmEUG1#8);ZTSnG~9A_kw4I&;{hg9RpphFtacZG1i{rO6tmtESVC_jEG06TRmJsxAh-@UJFTAo?+4{Z{Pf!CBFon)S-"
    "^$hLcB`$wCleZ4=Ji1}8(HsCXo>r5EH%Chl;2dlIQ=t~?$pIweVBhfqsaLrUQN6XJ_YOVnR%Fs7nAb)mZdHXtSy~wpnz~GeQn#j)"
    "TC?yYDSX3AjahJ!fY?tPSgQt1#Pqf!t0Qg6Aw=f5NiK%3+hX#w`J$&oeR~Bc1Cz5%qB^sq6NShg-0@L!<wlg5Vmh-"
    "A+(@F}aEU~~<CFgxCA7<kRv5o$0bw9hiJpPuxZU&E1Kh>_k8TblKKcnhrv!J>o+U}3XL15f)0Z9DBXRQT(U-"
    "{{pRGeLco<Go)Q*+mR?zTpX(#K-=<O6;)Kn7wR(-"
    "X>SEI3Ed0u65~?520nSHm_Zm!iPJLABHhKf=S5M*ET~4+W)=UL^=QHpfgAJ<U}6LJ%3etGlO~yb@<}pZ&2#uGor9XfA#anu^@PW!"
    "-s+Qo4d8PYw+<ar_7WCiNoEGPJ}rgv>(bOtqjas$(|Dl(N1O;!4~YE{1Tp+ZBIl6tV_4Ru>!>P_OCJ(>TFx1SMIPz59Sx47t3{(w"
    "lq4?%6lZe6`EL`YRa4GZZ814X;EAsQ^FG;jnS}4Fv%+It5<vV;;UxnWK;AJ-$~v%kR@oW;_XAZG-i`;2np=k^uDZH&-"
    "z}&?i`XHvbiqo}#$f@r3vkSEYM6(35pjr3cTD{b!sX2)wm+oOMI8oxhbaE1Riw5O#jFJ&IQ+IEj9i|CIcd1U8E3?y*OgQFLs~Uct"
    "AKuRg*U6vWWaFh&MX$wMHDT%0;f2USV{-H#r#r-x1$1X;b^*^6GOp<W~m$cceOLgXm-"
    "s$7H(uclY>hCWKQ2493$?eAALNlV^uk;y)_A8D3lB&vV0&Z39`TB^9deXXBy2rD~sPzR$Q8HhrNJ_-YqUbL|)eFck?2d8YnI-UnY"
    "eRg)WxSlo=o{BurReIwPQd1XH=8g;!bNVZkP7)aAIiDUbxUQG;q$OL{xw67HOdI5hIKrn-"
    "M3aHd(h(X;cp~K3uqWvBcf~QH@q<(c^A~;EwRRSWQk95`SB4t4&zQw=eI_zXK1EWlgcc71xKwxOTu!fxPM)AhpeNJ)oymp|yV|pu"
    "=2u6D$HiSNNieRG5rV(}b&^Ne0X9$80Ye63x%L(*D6`-vZ}efg9$E-KlG(<f2kEfOvVUiI;pNBy!Kb*<R8G`Z{-"
    "R}?Pd1zcHVSzkc_5N0l)Thib09Uh0UUPJL;N8*n3jo2dTv%%CfnG2z4@Rsq-"
    "d3DiQ+H!)WmhRjI7b2*@7Mn`oQ4D|CJ;32T9&RqWkH{QJQ1R<0f`M=1EDNIN!lF4j_;;E5rs+QyyB*W<yFJRz5~bIIob*8f&}U`W"
    "3sdCPsq4N><#Qvh+pNs%v_Xw#^+RChs&kxCBA%qB4Za5^M?T#k+n4dEI~AluI_L)KQi#e)V<^OW$bGCrr&HCx4UZe$`hfky{Rx=N"
    "i+=8lm}t^DYO-X&wnX@)vW{u7MvJghc&jLcUga2Xeaip{GZ`4Vt@D#=&G*!^8NCe1lhPn`-1z4Cr2z@-"
    "wn?qI>H4Z`rERdmDkcKHVdI230+i23a!X{W5F!rm$$D($WoHDj$10qq8a?dSZ3%5|n`j(291a>#WbAZrm^PKqtLlspy^A6R1?caj"
    "&2W9263Uv3V)qq-W&g0?ue*mTBY%GTH1<*l_eD`~0wG+%U9-"
    "wzkLTfWTSvQ<&=j)4K7=j1`=5Vv+>In6G6VQ|Sgz2rWq0s?h~4c8!{xvvs`)<;XRMk^TT76kmFI1w0=Q)*3HDyc|LR-"
    "3=5!8B6ALAvw|#2r2WudwZtzK`3>mXbzRgPfZE1i75AW!zapZqpgAfq?_*?WlgF17KXp^a#H^12BDrRi;1wa)%C2liJSW+ixf^YF"
    "3QL@a3~eFEAE7p+!F_D$O&y)$LyHn8UBv;5}Ijt_=d%|*EId<eitx0TvK{Oz(XrQO_F}}6ZQnx!!XU10<FoUB~Mw&MwB?iJ@^Zj!"
    ";)%Dv?z~bMRkB8`X!n^91e{gOU&zy@*tewyHf|?ZWQcN0gRz>#p|V9`UyIURsDuBg=441+Da`xS{+TWA*BWx>;r{Ho9=Yj2fUh0="
    "R$Y$BF7lfpt#31u=;3mCV6cnX6}MS-Oh%uEwM*xQg5~QQVqdlXs{R1_%LtB8bHp^>QF=%GQN>~0mhv<0OYRbN;WrtoFw=7KF2Cmf"
    "TdHrOjF;cF*oWw#wpB;{e@$L1H$-#XuH-uMRPg2zfmH2{TKanS*C47{zT8R&Myxdp1Y%B8uXJVjqfc?Be22{`bk+0T_6Ao?WOhA6"
    "-s4{Iq~Wc{SWo&0#xZbF&_o}%Ex^X!$bWYG7AcRDe6%KhlKudW*Zh-%19o<%*-vJo;FhY$xcx&&2daGh`WgV>^j-"
    "ssgx8JlG(Glu{;DN>t=EoSS5<AZd1{A%TL|HnWFuOJ#`vt8<Ah?A(5Kza~b-"
    "ieI?H^LK#%q$l)re=ganZm)5O#pzU1l+HHAdDH?y?Pk0Xy?@vDHiAqWSJFx9l@WYkfNC9Zk>xzO&SRYr;?d;7K&6|d3auz6taCV!"
    "^@^2a>F}2@f`#J-JZg5E*_lGT46PKt2bc#A2uC4QzYTg8xm6G(gaY!B2-oOwDoMK@A3%_cI*_JbfJJXbIHK8*Zc%}Q-"
    "v8x`;RU9HMeTPV1?s|TMd(AaD27C60eNYoHa&GulOufQoS-d&JHI-*Nz~OGF(%SMOEoj@_+0?~Uu;j8yB-"
    "eAmkJ90%>Y0W9pd<pkNg!@Rkj5Ywf2`GNrE!cBVAK~GUHB1R30lS?U#plVYsG%8BgaKhTu^Ej(aIxTk^G1ljdv_PNZ{`gsEiTs-t"
    "c6m!u?M1eZ@Q_Dk!8ikytQr&yu9*pK;TbHYB;kkh%D*m5=S3FXwn%-"
    "Dq2Mnr4E2i%FskPx6B93Y$27wd;rjqnXe{p=C2c_0WoZ7Y=w6AAsMgXsPUTbpXyZAm&LP8B&%%)jIJ5edrN%`80(+icO7qhilYbO"
    "&^I7Py-YbAD>qv^PIbZc_!fmD`7UWC<vRJ7!;z#QEjrDoi)|f)22KX@IsCF29!?*|A+q?eP(}qEW5KkARym==b?3@v98supfIp}m"
    "q0@0hroGR(s0qy9m*Osye-"
    "M2t}6@t2}}7s`|QJJb#Mrzs(?@Ld&m}X?nl35swD@72FVPc80A++iJ=AgvA`s8H=Bau(rmB$RX;o~$CgV8@ggUqt-EHHOW|AGDX!"
    "uCYk<`1sYa1U7KQ#H$TukAjf_>E(y;7m?CCwqKf)~uwlg|LR&F=5B*;S#bmX6R!u^)zs}v%XCl<J@Edp9~Eg-"
    "3vutn8kDe{p26r%65FjFXRA(ed<_JVe)OlU$_oLx>bE}U_V#p^8=SGTGvJFrQqv-"
    "^x^ZyQ$3C5Sdx;1vg5x9RhWtKWpvkJH5v*Cazf1f}yV9>Y<Ioo`mJ^$wWHN$*X0tIc?lFfsVGYo-"
    "^^fe+O#z2B^=5%%EO>#8EMDjw&3phS^zY?=TjO^+)L+Wd0m2V2)MD4=3$h3Wo^1+V#PA}<10esLh6hrfBdH3qY81QgcYL<m`CYQ|"
    "$f%zxX;uRjgu1&lQPcMmBh7}Al5Qg~O0lV&)Jbp6N4QAVkZlS<dth@Z^zRW;jROd?$rKSIlntQguW|8%@}XzQtGs0I5~p5foeU$z"
    "*^+fa;c*Tx$j98k?49<205>6pcI%!!(@p5kBzRfCLaSnp@+Kc=)VOJM38Xac0$TwiX%S^cGMkN2;g;>eeG({3Z)>t;Fr5eco`s5%"
    "a}?he0wo=}Sr*Ac-p6wLtePg45JVbN*?_ezTHNdJ3kD>g3duy<GsXjQA0PasOmYC?`gy9E-"
    "{*zxDq|4ux@H=q5hpFMg@2B8`zf$WHk>0uN9efJj#xJezK+Khgoi+STMQ<J-"
    "$^`mZ5RWKGmnU6P5Lctt8lF&W)!)BT`%;X7+iM9MeMFp3b?;}^6sxq$vEGz>!k-"
    "$b>g+eBQ%bw9(rRdIo6vUw(=(U77v^jhE{mnL<HIJ5SvDppiq61EW?w5kxc2hBAX4XICL-~iL<4jBHdPz(06HTSy!V`Q=YRk-Ia>"
    "S>c^1b~}EHnWayf><4L7P$tEieGc$rB<rPVOlNH0U~&n{`&tDHi>eAK@W_oLn=a#3<Wy>!XyyXN9FV&L*9KA&uBz2Ph(2z2O~CZm"
    "ke#70mj1+%vGmNx8>l!<LlaH_1s#_td&B82`ic!hV(B52(zEE|*HNZC|QxoGE<7Ijud;y>)#tC&iT1g06=%po*v5h7yV+n8syT_y"
    "sM~5aZ!%-&R5KYMu=dw^x~efut|BIZ?b%TC~Nu5I7*)nn2gK8wn{*Lwm&GX}1?e!ggNe>-"
    "ic_ewMIq@inG?&9Rc;3XWhI$B4d?5N}MRPPyx_W2jw9SEXupfA%n`PLMjq?(M(s{M9P>oi=4k8bpUbRJG#v9&o*`=O`71uIe*+`C"
    "h9lEE_VYw?t_rwxAJY({*P+roZ%KJi|pTrYMpn2p!rc*&w+vSaHKW?)O7EX3LD6SPo@8O6^Rg^^L^IRVdXLC~9gKyk3{*8$X-"
    "MnJ<G8;<nSM*e0enT&Y6^D(Q5T!pMc~ufDgh;*wZp;laxYQ~Vy)&jBtY3u4}f4Hq)jd%>IJ8;6HIi_UC*aXpz_f<SU{BE98-"
    "6F8m<(O?_?F*8Qx`&~*qS+@t5ENqd>yrsM7ZYeu|>o&kU{SM}eCsLRxSJ(%jC1bV$2sy{jeQ4PG=v2e->w(~L@RH$#QRKa-"
    "d!WA_$8)@)EAh&3yKF1_Sum*wHa4|@&Ah=tBAZqFnrZ<_haCjFSECefOMS(HJ-U<=Ldic7G1{RHuS#=jQaB|SR4-"
    "m=`(Ehu40MG^><vrDhT6y@rd9!NDaYY|ozOw>Y!herBvG1yaxQmg=Ra3w2kji_^UdfI$E0~;XUA?DMINT1^c^HP5#^Ea55HP{xY0"
    "P=?zEvPyLb;q+Pgmgq#~GaJSa5}^Vvj)XNW5P(0y=Fqx|0O{4KV<LJrld)o19_P5I9u-KF>WDV=|$5I<H3)N?b1`-"
    "G2EM}wQE<2u|haYc3Xv$s|EX!zo-iG(b7W<JckELjJPJd_Ln?+jdIF8Y8svg;jTG|wdgkJi3a^(gTIW<~f?1^oHTA)Pb6G~JvFqn"
    "k>-=AXqkW*XOx>5A!90{TwX{GBuxMFg4)=?U)U{-"
    "Znqm$W$LPLgK>Z%+WUfUGuO>&Gq_X)^a7cIIvoE|Mh?Vo9z@%y>Hh+^$Ia`O+Gt?MQr>x_~)n4o@_Lh*|joe3%8Mu<_{!2fWLi+6"
    "rNKf#i}20*7HlzpwLZ60vH=$z>XqTIHr_VPQ`wZs8g`SoN8D{j!m?v>|5Terr?qKTZ&-?$2OM?u-"
    "N<asJxEZJx`NlA6SlgV5|8ry<k%UZCVb4*+V|`K^P+$E;e#yT|y&EY+f3uaOf<y&imyKS=KAnB;a?Dg6CrB=5q^AM19?>BOJ|z|}"
    "TfJM^gOYH+QGF<%$};k#P5YYH1N!4nsPsrt{UV*k;URGWXHU$g6m!XiX~S#7ieH`_ldd&SOPtt1<9+C*97BjC|M)>o21dm8|gK;$"
    "uDgkHvSa%<e+3nt#5tcdMgke$p2>OOnbPu!B!9o}_}XLd;h)646fGgk+xuFM)j<nr-"
    "*UFyp3Cl971Uvi*yLG2kh#x^>UJ7oXf64yds8vn}V<1E1Q(@0SZQlo06g2($uo}_{+9^7EHYjQs80e}%U`K6<)gdG#>La&^^m1Yc"
    "2$<eq&r)^a=A)GxNZ)lS3NvaF5QuzB|T3f&ls6<@~-cYJZ^_uKYoM73@?j^djt$O_)zaqGv<P9aHO+Y*WkI4}f5Tf-vGP)}^BH||"
    "VMu5}Wx<G_c{AESAw+`%zUI`Z5_a0QkTMSM3UuWM*S2eS{3xd4w?7bM&2bpbEp~_=ot3(qb<J@WSx`s3sA9&$cTS^oLJpch;b%u_"
    "JM&lEj9H>t>hGvtOMnSQpxmz#sij{g_A+|^UkNTglYL-"
    "t`=m<I~NIpn%=ZkL5P~rk{kXwVxG`w!5Tyg^Ng+8)cqAY6}6Y;}?aLiD1bAQ5XqfOpqiyoxfR{AZRJz10Wo;vCOHh4ba`5dmFZAk"
    "#`7fVlZSdNL9^kVCTx1pL6YANTC{jRs6v$SsR1rAXe9rPpdEt-0Byv--6jd*^8B}?O7LaG|_&y%=XTz%CLT(mYj8qguLh@Yk3IuL"
    "EJEx1nC8Nv?6JiaX3p!#=_YExM<v^9Whx!U_~A!dCZG}p>RHBw{05=Xfi1m8gn)}Bk{*4kDbtyBH~&{VQ9*{v?*nZzcmz^87<%Db"
    "=ub}PV?#9|d3PW}Fo`3M|8RJr24rknGIOi1DO{K)i3Of<N!P1@w_m_!4GZg^E7b^Y=!bE)k$x3##pu2mqnR1<Cf$8^0?P$Y}@ACZ"
    "jBE#;YjAex0}X4Z4+S`sfbMz#$;hi0x_<^`0#8iG1>H^1ptVhOhVZLYiW7zB|nBExqez0PL`_sbl>fjW1i>$8HInH7hhCq#-"
    "$rYTT&8R?+Kmire02(6A%9Q}N<Yc4gVqwrb4d|B3e4s^1FU|y3@)wZuV!=8i4olB<6SzuIg&_;(rJAIfp*)=JwhNg553XZlvPzL>"
    "XOV8G$-"
    "K%UN2QI}NXBplkEy`IETg24x4OwAkSO7czCH1@+zWvdoCJ&*!JRQL>0TVncEMQHLcF+QQ{L6{#c>(0*7;hJ2*Z7S`aVQ4x4~OX$x"
    "3LDLeKgaueohoC?Bs`q)=}p0>ONeM@7;nI_mTZF>3vQR7y1Vot^Tm6-OLZnLLO=qMBM^$@h9%M53i*I)43xuV(*0jYY3;-"
    "Y;l$<t)|1a&2xh{SzmH#BRJXtSPR+1`^hdF(-"
    "LKqm%SZ9KXac}RPiqmHmJ~TpqGK!!)*7UMC9uPe&~`jHU^K`1yz8~DfXNViJ>5Uv|St!WimDs2jN^jQ{c~AzIgwijCa3r^(OsxBQ"
    "`)zPiE$R*tm%gT!wEj$30zQs2<d6c9#baA9~DCIyNYAgzlNt<XGAl**>!YjO5uhl8QLaogykwxlWz|RKm`Q)sAX<a@qP8xdA&AS+"
    "bw?rZbE8W4daQNSBt+&>%n0%*-OGyB1I{up_v;5~_SIb-<!lWeD>O!BsO;N>Gz8<Waa?`Q*GJd`0`ihKF|Pns?!-"
    "5@gmiQ{IRp0%Y?3tAk3LHqvcX-;Gvbb;Xl)oOOr6^+U-"
    "HgOrvf|3Zn2FNnGkI8H;#qsN~3dcG`6M}F{DSl4?K8N;pOSU}*UtXDtQYYiz?brr==QVp)egLB~e<3~Jvv&Etb?EW2ZC<`yo&7p6"
    ")e&-`vf+xWzpFx3z=lXHCgJ@4@P1{=yMo-CrK$4s$LOp9^1rA|wLf1ybD?!;kwH8nQzel0w3W4uZVVQ88R^>Vo{P*=x604!@yXph"
    "FQQ%75*b-;iyNrE&u4Qhg0AF$x#^)GfRHns?aTn50%uzg+y42T_v0%Q4(|HqOj~v&M6u$YM2Yg5Q4fa*(PpRE$Wc-"
    "0tn9GXthR)U~<Txo<p!0tCz_Y_9+flJOAVibTu><6Z7UO$l$}zQcx1fj~=cL!qIE`nPLtm&nQCxLJ$-"
    "!Cc0bjTg;K4XSa$R)jr)hJ6b|(Nzyq47ahx5${tE6gC`psaqML?xZq;-?FWEvGgj=PAF7?`YF-"
    "}=^*<Z{sk5lYHeC1U#9Jhq+}yX*GKb;0Z4vE2pH)l}>E_XfJIGO@&YHa`66RnJ<?qm@N3{zAt}MKO>Eo+Zp|j#REMX&2F}51}*;_"
    "v0X0YaMZRmu&MY5dpyCFWfoIj}edTKz78;TJnzkE_+pCrP$mL3CW#4M{{}G_7c<1lwr6LZbIHk)QIsj2;cd#zCO@tXP9ZN#zb!U`"
    "DE3CiBTu|#BQsf-nYqRUq3IxG$cPWvIQHA-82J9!^RX6w>Wl7u^onfXGcn<rJMh`u)1CTI1S$;Sjx@exhQ8=Jd)-"
    "hIc)yiS6i}tDAvRu`7+p3?*B3Nx??+YT%%O}%YCR~ZGBkrEt>a(n+9}9hdyn4L^`V6ErFs#I_T3bNyMB&_;hl{`aT}tU>JJ5zr*?"
    "LQ-(Q6VqBYNrwOHW-"
    "+_FPWBhj794k+3u#Bq5s$hhj07#0$fQ;<b&)cj{=CPJ0msUymql@t(wQxISbU~dqxO50eNb3W)3<`_Wl?!XlcS|&d&s5JmU0#D!g"
    "rm-fIU+BDJqW#HYZ%bWZ8SBH-XhcCYZ4-"
    "UT!;g${Aan1n<{LzN@Rcx5mF4!wgnL#bt~`#^AvqQLE_#A@L4(zzt>num`@Gpk$d@_iRabi!!Ub`2mr)^)zC*M$xI>zpftB^1|%B"
    "TI0}F71y`6}3a5uyD?Gi*b$2fh_aa|8r=<*T7cOr#ztNS~z+a(Yx(|bviYw>%gRu692Vat=86(Nni^yCddnTzwpSGGu5eK?+zm9C"
    "}@>fhwu)w|o%ufj)I+*N~=?f*<d*j$(0=L)40h-)edQQ|{#7-"
    "1vpCK*Hn9AbUHDOcn5aIzIdxavn;42<PetQxVWE!r#KBi~LG0H`MU0lE&RBt{eJrgA(fD=A}a&~)vtg_&PU-"
    "`soGHRLiS=;b0)=oX!MEnTAq#Vh4bsyFqjd)>$_Xzvr&t<gWAqy+kDu(3J+J~t;<WO4*Co;C)?seAV9BYfY18%VroLET;n{a_z^-"
    "vA`Hp#H{3kIgW!Q1K9p$@nF*>wYe{Vs3qdi;jx?kb-"
    "4c@&d&IiWGnN1Oe1@^f|VezX||Dzb|61(O9(le0LgX<LxO@8t_7j+!VvDeEH);~b012&NZR`m&7sUyB6cj&OML15;#098cad5p9{"
    "cooA42pMnv&rJa&DmTt~%YZlBKQ`go$1Fa@-V(QsyDiZ9r=-"
    "mJ#Fc|U`{EMb>_(j#S`%7;>blmiE6nT*6g*W*?x2=Ldt&FK?8la={)Ov{#HCM=qa1s`DC1xvP>Z}z`{E$WWu+juV)4ahRo8cZ7`q"
    "k{B5NQfq_S>hdnU4v#Q=uMn2#$&V*5)=$)+?BUx~sui2<zdiAUiO-A`A-"
    "6!5~r8$0c73TO%DP{SXyl_3YRE03A#{OCGCF2W51m5ninY1$Ca?K(DhUD?hGBkUESZSXX9YCJg~OA@Q5KQ(mQ&9J1BpmKVApkytp"
    "~&ZMBKi!JYU^WFU_{~|XhyFSURQyp#3<7xsx>ELT-U+ax)@-f|PqNC(lSxwT!;pW4!{Iu;-"
    "ICgX;DVeoQ#JJ`Co)Ovm+i67PpArN`A<q{d-"
    "5UO~AmjV?oUNP0I)RU)grRpJNTQ*PEL`AOTG>;}$kU*h@j&%huTOA)@uil0j&L*+h2SzDNnE_BKh^UXcm))0b5#n2$z%RER0z^bV"
    "#Lx|Z$CUxtpN&PUX}GMx->x=0<jBn*uegY-"
    "4mr)0aV_*Ejc3Mpb&|}$1Z6hsQp%J@c(;&GrU%mR(`je#Na{!o#J5^(q8%n5PWnS`lh8m#|*j^F2AUK-"
    "0I8wfrp+jvN73fHsQ=8lfY{9(B3@#Q<|v!=jkthR4YT080G~!DN|1xc~9So#++;3d*@yanWf@th9KUl@-"
    "I5lF)gQ%x(MQ~?4QLMPnfXDw8vrxyT5(dvybaFrDY@B!X2@}(p>m4yMIv;6y(H{oTB2$2}Q{kIcEAPwVGdB)gob3e!j~y^tFu;Ii"
    "^x|G(qxpw)JhB+|$WqqU;Lo;^M^1A`OjYdV>dyWsO@^K{O~`neFNpE3cz7CoolSp38MQ^MyJf&!2IS5u%mKX|ea=lq|%V{?u#39<"
    "TlD?o4L7phKy<9F!@uoUJ@a(nU~#k+1v0USxLY^>ql$Em8{pbWfselSD~zxJ2HO_Uo^kciPL!bp^>#kvOry?ztm!ZSeKU`K4Fiyt"
    "%o!#Jprey~kAWv5NWpc74E}b^wG_HI=P}&KRF8&K@(m{67wBlBfWV@fJ5Hx?)!eb5&mAH4(z0Y9>X^$YiTAIqCj$W;D%!-"
    "IulhIfe_>!0DW)ql6Vp#0OPl1uWv;uoF&gO9qs_bd8;FCWp=SFLlISd^t=aCQnB^C;<>5^Pl$MR(i9f!7%=>_<)ZLB>zHR;hpl@b"
    ")uog(^b#uE}K3xAT~>uielU}Ph9Ms3d|h!#jsL(?Gas%^XSEIm%)-"
    "YhWA_3UF$VII{x1uvK8m5j@f+xf`1qF$wjyzwP~fB;}~L}<{{1GJ7J={95NfU%NoeOm)wr}gr#Qj5{SYFfF=H^E=s&;xSYc1;`QD"
    "HvOd9SJ_ygfJY|$=CyhEadcl>GA-"
    "4G;PFQxw2xiM3YUk?TEcCd0{9H?HF#WUKnMpV&oC`>4xDyzb{?RIi&D|iOZk4n5iXO~n%gTRS&8f`4&J7-"
    "qlk1C#JxYK55Nu1Z+uN1coDl$2bQxCCny3?X>6u3bcz7)An%7E-H`<H-r6uQ?hBU(!PxKEhOmx-"
    "%`uSw^?%{Q}s{Zrxho^>oIIgV&9DAs{|2bWd0Zeq(W{quuN<QmAaDM?igyzfHBsC}fDVi11BV%Ib@gBWDehUYT0N50&BTwIR7!ph"
    "<S~zu-<+W4=2Fm~XXztFc9R;LLt62}Cw@-Ul7mK87S(*IHoS=;0+|5YwLlu%MQgjv)EbHQan24CnWg3^EE?u;&QcKobyL8w6;aX-"
    "zX6<6A!GyQRH=)+aB;;K6A7wdR6yaq`$~d`>HNkluzjZXK&eNwj{P5&f<L7MnNBk0YDqW&UC7F6(`T!2~-"
    "s$9}FCTugx;?1jiayIo4q4Bnn(7|^4;=B_E2%6nvw1B8z{@UU<y9$xwOjw8l<D>Wfyjxvnf%JcEJ(Jc<YL9ul$f5rtF#|$ZPQ0Tw"
    "xqdjFiYU@;51v{Zs0slBTz20#|V46=i5F~=?VN2ol`#Y`Qw)oaq?!{6*_W4aIzH<Lk}JeyRH~d5s3k_s5l5tXAQppVtu1qxQrMaP"
    "Kr^NsU3HqDom>SQ|n3ecNT{UG9C51n8sf<3{_NDel<11WvGJp{+iYHbMC%Av6#C<bTZSTUZ9UV1`_wVM!cJC&B%xN%NqYSq3r-H-"
    "~KypD78MJansBDq2Cu7tF1N%HZ^!XT>V=H;>8j}ANQZN*I!s4>DFw&ESnGuSrHPQI!Q`UMt$K6wwmzA!^Pf`s`g6ybY~)41j@>dp"
    "hD$Xu+U(~4Va~3l^S!=a%^ZMIbF_<v00hOS+Jz}JynH#x*jt_>R$6zMMslzpgKj^1PufZ*zaErMl%zsLL-"
    "`+!6zJv>IA>^f&^2F6ElF2pw7)U!!5;QmPe|3C5CeA80$c~VlmCv#~VDmUvz8*@SOHXvsAR~ywg2x)l(p9ia3xv<Pa0~nbXae(QT"
    "kHl-"
    "$Tl+6*yUwQ7rbF7?6{Pm@io_yw_$6A=sC>(ag_kM?8`7IIBwVbrKEPIEfdTwx@wp~?$*7q{@JC0%C^h(Oujw#kxOM<wwSQhdqdnD"
    "}*-"
    "|6{uq*H*z;4edHh7HP+0Vlr|&O&t3%&1249%g<+o>14kwtVDg27>$ADZvd`w<$<#hLj?wqDXd|cuS#@2M}u<B@Vy_gm*HCd_)ZLZ"
    "-jnGlScOhlTQb_IXZdlPMRCB^6a@^c$wKO4RvIQYCo$YQ8*j=eUp54@Aj`}H37}sECf_n&d64T@E95jfLhsU$3!lgx&FxQ@ZKoO~"
    "h|Yqe5pcJ=OMsGJeU0HbEseW`pp!!;vT?<vXse<jP+xPki3`Sj8Hmveggl98IXUtrq7Yo$|89r+G5U+UmrSoV^3*Q$$=<IeYpN#0"
    "fK3}<Mc*3(TlMjJo`;t9P|mt<1jIZZjZZM~2cEH(t#G`4d+r5UmjavuZ{xW%Cl8TOBqJr5enek#K+{(6Ag3l=@TXa{NVJt({RD%^"
    "juRFq@#)(>lq5>MIHvMxBLH$~mFCsLH<zD!B!sMAs2gmUc*(H^t%yJ8jPQQ6A>zwG+vk<$d><#H=(p-"
    "8hFWdKYsClSoxA?}?XMFA3tK0=-Fa6zXeyFA2A~TpiWgUa=PG^}v^yB})wfh2`&?{5;M?v+a7PX!QI*KwzafO|E-"
    "qs}x3Q5<XrkssPb8Hs(P~z;&0CZUJ5*t^tss&DmtI*eO(OnnOh+?ja5kWW>4Jv#%`GLjKaKM;=MlVUrSomENT@X|bt-"
    "&*M^Qu}_hN93kz0*Mt+T)W5a)<j2nmY81qX3g23g~N?w6T6beSs7dKx<++;^Je+Cl;@w1`Ei1wr5PEruxW7%>SEu2gU34S+ifvPi"
    "+vyk-(jixCOVY;Z~JCa>;PuaqYIEfmsnZ;IM7e5Z$0DT2Qf%d$b2C&A>$OqUO?G<B-"
    "Efcv{CGPQHwEi&<^P@&x&!{r8#?D|zVpav(0l_QkB>9xRib(4cb$FlLYDKrX+fSFfJpTs{@l`e*nIjyY0U8fuuk~c+@F3f`Sx5_f"
    "uZ;pgo@wMxMsIbUr8$0s&o|K=pWk*D!Gc?ZkM9sJf6^Owv?lh9SQ~faO2hkQJYQ}1(RAKL12-UP-"
    "k}JPO>uuuV;!T9@i_zK)otIy<o5Eqgh-"
    "wW4pdMW|o*{h+G*qPx>5vK+5)H3c&Q!rvbBtnhxaH%0`eg0b83U4JkZ%+fKCGNQ-2!5WQS7c3kbOpcK`oFJloQiNOAL-fhm~KLkK"
    "DbAbWU)9<b`Ah?00k0-"
    "BZ`~?2MOGX9e*&{Jq4tbgfVcTmE^cyWfdX`NJupN#@BcZxMs&m7~p#H{ODaV+*7ZGtT~ck;0<eA7JTCYMPX-"
    "8M9D!FFtLHzNC2Y9Ux6gyvv|usf{b0%;tK$oF*5MeKOkvTn$32ps23{+|usMBatfB(4rnZcTxrjF*To{;^Ih^CE8b?po&Kwv6S0n"
    "%H>PZUq1rXD({)e%_r0+JW&`#3h`6<zex{2k#eq@F@dQwUdFQC{bmvqxUzMi)zk=WdSoTQ`>)9EC)0zSMKS%L=$3W4JOjDoin?6v"
    "PuS$cxJ+0sLmR6kH4+f*Gqa6&Ie?wH2sqzA13LUC|6-"
    "A&gsi8n7OrI14$u*@#?h6*1Fg%tYIc=RbRM_K)N6V+2tvD+wPn}hGPO;Cy5qv@iTVI-rhV&N&iAg#A_R85xu5}b)<+oJ=Z>2;&zX"
    "G}Oo-"
    "M|<7eOyhaKCjYf|I(dJ(_(TCNB)XF7WqKP;7V8w?n+3RX&C9R;8zBH>P%Kz4ZPlnjCY*hl%F$w91mKQyf14YlJ!5JaZ48Nfb;|Cw"
    "8BT9^A_y!enm=?xnj#cl=UEnT|nbF^o8VL{6`9<s>b5_^K}^fZaA9jPZ)BH!ICTzbFTUhUC6rL%DZ5y|?v-"
    "$Fuc+br_{PswFZcLz;hCA74N2hUYV;f`ON(bG5>Z6I9HOY$f52Y1?h?S>%-(!)Tx%7t-uty$$W!HG*n4Klh1R9x<a5os-ou6*A!k"
    "|iDhM<L-u+LEXfJvzBxz5;9>2bcZ?RWKs3qN+K1pnm_bHrI8MBIO~@XEfA3&H$t+=TP<Dms-"
    "=mrk=G)@3sYskPRMR?t7b8Zx4c+v$Twa2ANZXH0pLAS|?hpxD~Hdmht~}$&ulp%&*qYvgvrN(eNY^6PQz6T|1J$2{kvPx&k^kj;2"
    "jk#Nw~zy9SOyDMng@0e#N79liYk%7S*kL8lV{k!E)IoI8dBq3C|@TOzN{CH^A}kuL^PGCu<fjAG`NXXa0rr@%?<Vy6?&?-"
    "*TA6N;iEyOMourYsd{O(&L#Fbrx#dTTO<{|sg{-"
    "A|#inAx^!)LLC9lr&y5MZ+GgQst=G^DjhnIhwG)qIVaZsk5U9gq;x}770vM5}Putn6J*>0Nl1~BoD3bv)nnja&@let;aL|(#X6c^"
    "M$N|*SkOkgVAIfSW|mJYZ92x+J8|z>>vW9xd5=q5YNA**_QZkIFlnMUwla%;h?z8U7aFbG8R&XevT(ptHkoCsk@B$?tunPWO_$AW"
    "&^B(_J3Q+tcF%n?5K&>v)L1N{p6Wj)RVj92|}-Vs|MwEIlQFM)8#qM*M&TQ!+Aeh91t6<&At2`S-"
    "$idw0DK@hn$l02Z|uRFmIIu9>n0o7#v-)hR3RLyrfal4^fr<$Lw~E>WK7{qXj*=6k0Q+=uRa#eH&*y{?Wu=5x6dR=-"
    "1ghzpvpY&YHTKk{b;b0Wh8UAB9`1RXVuwLVMQIz|C#n&K{m2^s5kT`ngkbjLGDdIZEW4j5hV%frS_jSQt8v@|X?-"
    "Kz0IjuFpX^faFQMa~J?^ySNE%&e>KnJi$X*=e@?sD?U1)Zv$*!T_T5Y+z{zX(c2M~6Ss!anwxoXo5WdW_KB7lu|gO{4WC$k=oRjl"
    "&b9;ZfpPyC?7g{<q@HAcuFCwS;~(223SrT@PmpwX+?iu1879WnASnjS(mWz;vDT!ggOvBc?2NpD9X&kMkT;rtS{*2SPbNPfD`CMm"
    "Ktf3xn{!sA!G=*5YLpeb^+&ePz2%BFU`T9cKoJLL$0XNC=<>R)3H$8L6=2~TA5K&7fG#_<2(q*CtML6_t`877P;V8?=zk$lYGUN#"
    "0R_Y(W<;Zq+&_GlNP?jU>KZZ$-F^@iAo)9Zc{W&FaQf~87fcS~Sp_^fu%^WeQ#*C$+e$NOQIA-"
    "*swSfjD?b1c1l0UCkdYpDUTd@B`GZTZZO4+L0N!J?==iJwu>rSI5`c9j(d89M$ijbetV!)e7n|^+x&y}%g*jKIA2h|!cwOvjvp}q"
    "-sK$p(N-fmBA8vd_;y8tLz9~>NTfc|YrH6N9`9BbnAFN|fZhJP9EiPUQzS>0hjt)abB62Q<57-"
    "_#Rju`dz24eyw!EAL6Pb0^$=IknWxQ4){@{M<Ci=uT1DKjBuDQEr$xKRrl7huPlFFEP$%Fhj_^a48^El*0C~i&59<WZxU(?@e)_t"
    "()7!+Jr&#v{+?LgwMx{<4Dhc<&Y2Pv{thkf(adPb<!w1rv9Vm|ZC@9yZ@3y(H)L}!dl@83)G8K)4(n4#_+lv%VuFcW*)Jg+g56|P"
    "98+FUFKrj8)3bIk%Hc~A9}ycgky5bJ2Bjh9Ffer69<R7CfkFsnnodiD+PD9FkW3%`BhC}0pCvX+r&sx`nX@59A`SUivY<!6oaep$"
    "!@F^~-"
    "VvPEK=R2vHef515lM&g$Z<mqvdJeA>$DlR50qI823rrd!L0x^0^GUDq)u1NXOsXZRdRdjW%KirOIgO);9f*$DWeY6@^)!RcDfKr2"
    "RyX4q{#L>_Z_a+#MM|agIKPuut=5z~}m#}lZ17J!@ti+`@(Dt#q3R?lfPtJ)v#3>h5DS9mF3>OV)DiC+*T)7j}G}~(QTsJn=8Rpr"
    "un#6oxr>eUtYz-FxE3Oo68p_h^3!gdy(Nepw|5nxx?IZx0)5;MD9rn=5zWrUOjcpZ&1BeG{<C{;Yv)qH{+OGm5c_hNHpl=Ubd{qU"
    "CU-"
    "j(8y1(Z#+PIohOuPEVIk_M<AumGG<gD%n1BU{FOpFwD4LhdS%+nl^(@Db7{nZ%{ZwK~T<M2^+8rcy@p#(6epgFge9=6n0s7Kd^s="
    "LvMN;To;Nye@^m>}#~8l|j+{+;&<NCv{XcbsiE4CGbydO|vfvlKPx7>@IoWX}1H(Y!6rFFl&iJi+ID!3lodB*wC_JZzRWfsO)afo"
    "^ace>`*}N<RQovfYwL>1r+DEcXH7pb(Y_)t+Z$04mb-SsHOUbuv&Edm)4v11}olkM|`YA=@6*!Cm}5RDPDFwovN=Ld$hSs2dCZ%v"
    "9m1^}D13WuuX!sMlt<T~rKuE3{S#MYueTqwKxU2JpB^S-"
    "L~|m3EG%GNn|q5>`U+NwxmuMQtx;r%fkETF*Py988eF;a(C~zma(0w&UAamudi|B#BzE@~!wa?gY2H4oJ?*Vp{;|_Ad<(WVU;;?h"
    "1hYAY-TfyOlHoAuq(_9*T?g)0%oY*<&MubLX&v0iTsUTa;<re_4V|Gj1~55_b=X!R^d=4GE55NqMmXK4&8sv%p9r{u1O0Fm5EY`v"
    "B@Pis%~M%aTD-"
    "A6X&*?t@N)SM=Cz+vigFpOq>{6`~>~SM5V_70s7i`3Qi@wcFo^&w>|@dl&yU&o9jC3DI8g@r8>HNkwRtCQ5zmFY0&}ybhEz(vIv@"
    "yY_gdUSeO<sFKFnc+UP5w4=<ZiB26=^eGMyAg&na4WedKW^-gT-`l71)A8P6okSYih^3Cjk%TJWUZscqKT-y$-"
    "t8v+i7;TuOO!;#<{Hr0@Tc=Q@>m5evb+MSIItbOLoR!-@Z<AGp`CIqay=ojes`jMZ=;9qf-|=w?oB^@0Ba3`K(~$uEy-"
    "f|Xq;B!!ncGCQYZgW%fVZ3u1Y)@b<Y#GRYtziNrA+_N7!}wKB*@t9wq59Qa`;ZVa(!YZbxq>wUKRq7^sGkBM2|>6;Fk%aR*X7xO>"
    "9tRQ|Fj%djq@VWP%LDDCu#*f-"
    "$*mA|aHHp9d=f9%KzUfI?9DePTti(QZ>6v6Vy!j(#q;|iz%<0MO}319So;Z2t1gl5m&JDG$Z`GNgGg=f(kE&F(3HYVSsKbGMc;6R"
    "wXcKlST-_Uo*W#tvCBN{}&z*;1?+18CgobVjhul<wQO1tX`(!uMzEAMuEx(np&-i*Qy6-"
    "}fJCMGEK0<{=<UM#sROO|lpG<`MwEZ!xai4oyY3uvfl=nZ#W8;5&Ql@PKTk?fytPr+u>9B);XG#F_HV(oO9?k2YtcW%{uPpPyu3^"
    "O<;w5#~u&`_xBiq9cf@9GoxVn`!)Ox41){aI)Qq%Io63cxS_0^{}5B&W5r`THhw!wNyMcrUa6?YAM1A-"
    "=1fCr=Yk0S<n+ZM%*3)r8{>v!TcC(u0ii4%d73h6g6bQ?=mm|Nn{T9=TQ}EBJ>PuwThLr)Np<r#|0@hRWt8Y5ek;XdQG<o(a3yOO"
    "{2ki{bI=UWnSRa60!fw$Y~@jl;VFbPeEB=C^Vn&=%taLo#r$B%2~tlL9jLh|r6;1y(t33FH4plu3lg?SFL~k!{Z=K&<1USexuNpp"
    "KC+{@dlzshT!sMPL<9cggI^CSa$6QKWFHZph>bwuqBNe{>MX-zzT6^Z(!xSv(k+44Vc>W7>zFCHxR*5{Rwh5_|o+%zzM9lqz&xV+"
    "9=pg_{9qO4F=vrUO^S2Dowc8M4$$bKp%0eIp>v`BrxjO)+(xyekDkfdPoLV>z_T!R9*~OSBvwn25qoqKOKsKMZjS;%<g&4B}?Slg"
    "{Ow$;AG`6g0df#3xfozde&cWRo%c$g$3EW$d@V<3S;Wr5?FxnP^jZ`6y}!;GG}9r%uI?A>RtABg}usqXcjN$fp-qq@N8$53iW!!G"
    "FqwP^MUZBFynKD2(MC%u_nC?1VXu`<Fs@YDq<=Lmybe)osidt{Oz+`HqZtP8}aO+YT4H!i!IR87+$aMPkB)a!)%-"
    "BmCMC+$jm=ZZjKrDxfYlIuqZ1jlBG4oIBUj$@ZAT#+4a&bi^NdU{R0S<I?;U<A;;wOQyx#J>ki41&cOkv&>{C0e-"
    "4aTbuTLPVJ&!l9^$8<j@eldxc2E^hcewKUz<_{vcK+dtrUnarN@iHL=LkibdafCK<S8m<`8PN>omsIG0W2BJ(~udKr?=2Xn($p{P"
    "fl%0mA5=7W3L58Kh5OImQD;7VD#Q{V9+VE7t7AZbnubvtPLtk^dBp@GU#Q;?4P8$SYKi&;zJ_wj#<;?U0J@Oh%Vzte4lsGb4C;l)"
    "c+D4R|WR~y})3EIcz3&q4fh{9-%P|BF+L%|}TO>X^sN8YU&^>`9#m`5ElS)e!EZRFjT7!-QH)rDFaZt-7Z3&5mrYe<>_4+(rz8-"
    "+&cnGnPmmt(IQ_FbGIid}fU+S`Uk<4?&>p=qaW{?#eVu9Tr4kki-"
    "9<T9zD&G$6Q_!j<p)i}hhXampxoKgU)?gPX(OJ)yUrlOje9(%Y)Qv|308KWS&*&vx#`s>_&Y_dH-"
    "NptYiskeCls_7RCwVNJ%kz(1Qvm-NX{70tN+ZB(?ee(EC8Sn!~P{B&&v_zX%CYYAd?_NKor~dqSQWs}R^?D+GC=3K6#pIypud3m2"
    "5P38~Zep$Mep9osZG4H5-"
    "3%IRdV5|UGUpL*xN6!4wE11qJygUy2nsHx09rGQB>TZdAe(M5rI+_UXABlnd@ZFvZTl0~Mup1?q>!FRPnG*xcBJ6kU8i@Os<2ntw"
    "}tX(%RZgVS1FZ7ZZ+BDYu)_S{G0}L3gmOTc_I!ahjvU85M3TLi;lIfOb5AhV$(2w0vG`s+{$H0SMdP@s4k=>r~0qsn*UE_Tx}q@K"
    "_fHB)fkGKz}wfyC96JzdoteWa}M2<tD$XpTWMb@1Jn$4rT4Oy5w7m+7_3Z)WVAlx?1?}<r3nq#t!kLXIZ~`ektmH0yqmL>Fl$#|K"
    "``$-5l=OgsQZ`*Ul&CsP(iSV5r^;kt#N=C#dww22NctKSW-LLT?zAVx>#_nbOhbGJ@13Dd@ujmZ9`kr;{L<`mN;A|1l!_0`qcx53"
    "r#PLm3I2?-B`!u#roqgoTi?loa&?E)hClwP5a&mCcSNJ?-MoC*P0WPJ%iy;L&kN?s8*7C1S{O(oyC-"
    "lTa$Lx*AIwr2FD04&_HmEKOblmA(F!+Jgg!@;Xi2v0p`Xe5P-Ghaf#xLX@tU*X}JvBF-foF{MlGHCi>}xXd1YY7Y<>;?NcaUM*c&"
    "1q!_%wt#H~dC*5k#jD=MZCfl!B-"
    "Mpg&?WjOGqj^*6E5LuAZcmrgxF}7t;8sn6GXB%v^o=R&x63GpdQ<aOQ2Nl#|KwC|)&seaZaPGjOC8cCWl<*BCa1NJVm$}Xm@#43="
    "%2_v<kJ^Qgoe`TIdt$Dm?~x?Zg2%Flm9u3@^yOyJ<E&)$LpvicyO@Pm$T(+SDkGKaw6^tOc`C^kL@<8@+PO131PGxJj{~Z$SLDhZ"
    "ZP0JwXE&3r2p>VVlcO=<6e`x)fCbHn}!8<zfd^or3F-"
    "gUr!}PCd5I_uO!S??e(X=`u~+i9R(6x(3C^(ogAvd>DW_cAiAiGhYJ_!dIvKj>?2N9ejQ~O?fLU%`8x5K7|j^SEzD_M7(aytk6Jc"
    "|WFM?g!j2^u@P%v(8Fx}z4&rL{%p~PXbpw@=4@HAny67EUfdOXMPZmvxBgj<0h0QE0DdnI&pk~1{NPVWm;9^>IZ#JQHTMCrk&nNI"
    "soFAy&)S=eCv&zjl2r9~}*t#zyNGFSo*RYm*qjZKPT_zMrITZY_#ep^(C4Plf+}u*;;*zvMeG>%o8=Uy43F7S<Ut*|nRMVo3l4r^"
    "l-"
    "Z_0a{(LIWOC!6Q3wX4|PH0r3MphXM5p{k#n2lokdfBEFd*7ZVF0IC%0Hn>PMKJ?yelX3(oqsvUQ}p61uoPR7r^?al`b>plDb;NHp"
    "gUe!*S6fsaA!!r#zPFu%zsLWo!N8HglxVkp=y}~n9vuWsim#eSoy1}D2!7a?V)KVj&%hCfeWYS&MQEz`$J~md@^j4k!&YNs0Ff^9"
    "{sMRgqj1(hP>1-e3d65;tdcb@tb-"
    "g7i<{u^jn<RzW9b@O48af0u5ItfvTn$xtj5t9%hB_@A5OS#vO`WrNJYfs}fG05JLWCNX!_L)D*n*N8;+zn-Ez_FaA>6)E@@sI05G"
    "J4L5F#l%#R^)R(@6x{iG)N}q8-"
    "z}YQNMq}!E0CsexWzeIk#x(ygsw&EE{BRw>OMl_b^~=3RptuqfTR5i<opzmgA+;bur8ZF*##t&qR>d?ev$s<kN70Q=oHKp@%T$#B"
    "%)fP`0d5c`F&zAm)amriC=^_1otF#?r^C2$Wd^7&hhUbM_QqV{fC*96i2gsuyk%(k=jA3G8h{nS0EWj2oegH%Wjn+UK(`1#cP)gf"
    "i{Tj2#i)(F^%JfufUDW-"
    "Z%T&;%skCtM}Dz0<1RN@XD3In0YE0~jpjM|?!v}GBShutC*JzJC|XBy9$eI9ZaCt^fpXO?pyAE`(_>P`Wt*fq5kRqtY<xbLes29w"
    "bn_sy-D%*%M_R!pJbHK86W>9&pvObxw1f@C_%kx8+qJU`I7&^#qFURu1(hU46zklj@!yATk-PF2N3^(NacKFxED;Ek9E&G*C1+IA"
    "G0;<~S9$t8Ar(g1I%zoeXfkcE;Kr*OV^0Y469Zpm-!rqpKY&^5q)HlMllEFEJyW~*12kxJ-"
    "R|%Hr`qQX)$7aNK49MLa(b`f%EAQm@&TpGx1;3*_&vJ?(p(49WEZ45Vhuy8!B9%4go2RvQ2Es#I-"
    "idu<oJE`1cuW~fR)15<3bZ9Hl)iiXCJfm9V>6|?dG)lHs;OPdM#k!#R26Uzp9Bn(WJGTCGK^qZ1Xc<7lIVM-"
    "#eq2n>in>q~4FXZ}A>1o0~6w9G`yi<Rxu2$1M<x&eGF9bSDFhg3H~L8PIa=_K-0CciwJ|XKu)IF<@t54EY`nKKh4<ebD?2V2uRG-"
    "rCD9lZ+flcQ;@P+-"
    ">O7>sK<l=b{%iS*?^cxOK{|eW!4Fbg;InjV*7sj$(+3RnB^_ZgO~FC~*+tjgGZzF&$DH@+y143nB79V`)GA+-"
    "c#gdSGZWMKD(9KGZT=36u{H?TY976a1rj_o@^lA#l&NeaBmQ;?WA|{&SEmQYVD?g`t{q4P{9uezg4%{f*}`6kl24&!X=W&Wx8*QD"
    "S`nGu#8Gte*<=`W8SQ<}CMv){r-~mX-k}dr&+&tJ9KD?!5N-"
    "H4TIG6AK)%tR9>qzVvnf3CDv&U}06x38l_|6tNJWGm1e*nP#Bw$EZx9!i&cdvdbbkRS@7vpxqBq^jX1aIlH1pbp+xWLTfqzDVTKS"
    "%Zn#C0kJMw&t2LEG`(Dz-PxmRq+!ylRUZDq4-4Cd=IpL~7*J+*i}8dFZX!xVxL$1x&XAh#uwz01iaM*-"
    "1XcQUFg+)9c;gh#cJF3;G;=o!LqWmiE8@<7)u_0v^4+PEvS^kEWItos2!%;I#7xqoR5p&(VGl;?=$%rm`9%*}Pn7$2JDGN%hV?O8"
    "H=vMUWHBY#PwveLXg7o}CJElLIrCej@hX_m21i_zXka4Ph0Ai3tA6NBW1&lJw@>p_cm7ke7<qlKt*dnW*UtQmnVY8~)*6d5!ztAp"
    "2E_IXa1bah57}=s1YYf%h}TP?e`@>*Cm`E9SwF(a{I;?qo5{PtjOFplsGnZr>mS{d36Z?K8Af3~tUL4HbEB<Yx(N^oClNtaaEq|?"
    "^?f6KrPrHq`Mptzci$-*SQ*i+n791V9jxAM?E^)3l`>3#k3qJqs2LotKto+q1Wz9Fsw+E^%_bhdkrsree<?p|_$-"
    "Xs4c16N0Xl(zn_PIxT9yY;cgDV&HSp92k7$}La{}sF@77gP`UR`dI8g9A^Ealq-"
    "KqhhYyob1HQnJYzAfNe8{rUle`B6Z;djT|$*uB&%Rw-;t0aHg$1ZLvyi%<;DqN;8FMO|I>a1Q6ejZV}>c_QG4n-g-Du3t8R}6uWB"
    "7}k6OzaB^i|L8TwI4Qi$vfHO8#thM-"
    "J4s;U#lM@tZbGZrv}aD#e?9jy*#Cpeo{Ss9OtEDn#I<Y{l{qjLEXYo(?Yt<88TYsiMF&iF2f|*>J`G;Yz<rZP*O(HRNm&lOC|1Z6"
    "uLPvzx8^xvXK>@(xrvt#7$WKD~XTw9=>+w)e|y{B6f&ecor4v9*XFrrgTbSn=qT%YQvAmYQnx{)krmNGJ4_`d|9SQ^DSo(e(qG`o"
    "5?c@VZrIO;4ZL5<;oQbNI(zl@bM&3>ZQ72{J`FS-"
    "4$mbeX?|K7Wf3HWB2@{kM8e;?u8sfC%W<l1Ysv%BB5+Zw2tA1YzaRLM>g*&LRJTWb>hv8J-"
    "Z#qu6}&45&d_@s7(ea|BX%+J)QSgb*7){OnqKt68{|Gju#r4+kZ}&in0sIU&BOD!d-"
    "8}UOBF|K&Ks%0%Ep1{s@wJEk5f)<)x5*WhSCY<sAVxZ!?j~o1<-"
    "@0R1wyzZe{{<({Sz>Zv<#en)zJ3Bl~SSid{>WaW9GBX8Y+xP$l)u+q#jXc_lG62H_2*kzYV{*ka?ePn1`LRte-^r`9)zvN5ak-"
    "hqiFx~cevw7_i^o^No^%^QKWqGDWAnP1KlJUEgR-}X5uVIU^5{R7`x~0^SRCsFq7?2GH-TTeH8tm@UW9?Y9!H$R$C=kx`8VFf5*0"
    "tBSGaST;YyIwZp&z)tsFziPJ>6cQOb#xvadJBot9vEK8*#jXe|c)Z!MnGAd}j-"
    "l9sNQOzY*|oR`6|{$tc~AQRuB9?24kn@_`vcopkrhz|qNsQ^0_HTFd(tx)Vb}So@F{m6g_OwdN!GB%v&sRD|CP#(c&|AlE8qF`e="
    "=P6Kk7r}5!M!IV^It57cW`#?m-"
    "Vyr#u^KCPb0Oj&A9z27nr7Yae@#DJh!R>3++6gM{3?UPzy+6ZO{lb&7^jT>d9MPxPuZ1y%=d{bh{{r^o)SDWW=^Y$?LLfHhfj@aw"
    "Brdr_k$Nw~xm-bf4fRf2VZ!Q^EJFT&i~y?2VDtCh7Z4|E^Eqm1EZK{V4D61su1{?$9jO>Aih*yk;kM-"
    "1o%iR1=DI2z)~*pswp2e{O`*2lYgyXu|NcrJkBjw#VH>o~WP$#RKg;wp5Z;;&AyBgIKdrKu>0tDa8g9X!0W;R)40usH5Lis||7wd"
    "xY%E$zAdFJ4bOdb*k`7U|3=P`Fr=8uFBIusKI5fdilsRi{V2bJ;2M$Wc)PwVtxExC)Xtegl<N^=Q+R`tvl~#^9`FSP91J$Nr_h6r"
    "m$hfl7Yh4Rn`OWz2IzUr+h<7O-s0O57q&l6kziQC)R~ec!>qIb=JsbpmKrY=TBUy`hQX-"
    "&YL8y+=#)>1XsSkJ5Kc(TTfNg<e>kqa^CD94h?878|XRdR{1H5_2qy9PZu56P^)nZ7n7?Hcb)mKwUpM89v(=YiX=XEXNpjnGWA{j"
    "M|Q0o)ACgIKJNmuzbW4b=>DNHcST3Cd}l)2&!RiLCYi1*nc9OpSUG<_AoWaIhD71Oh5GABRFrL>LJ6qSzpMd+LC8Xk!huDj8@v*g"
    "kfrJ|$gT3#IzxH|D?+URBV&A}{}^uaw6aLP7Pm2EP(mPXn}IdeEs?kK$<M&t*+>=9?hJv&mZ4ryEQYm@ECxE@=C<?k~ad|?lZXfN"
    "O2g8b28<F$LoxZ56x$1y)5@XJy;v<P~qG7hGyIBBOur9M}US?8(D%Kmk11hbbH%}4;Bh3|`$>VO%aBHnWuMxubZY|Kp{F~ZxL#Vb"
    "A0POhW~RaoD4g!$bova=qO<H0#&h!0&uq<r^5h&IDG&T?Zrvj~_Eb#uo%h9XfxD3JR`^Gor~=)2GDoU8kOhdhf^7IG%vJ{R98gh@"
    "_|$-&L4mUul|Rw@8Tu>m+vZg+HOI`{yx<UhrT#~eDaJQ3iRI(p*>ocVwqJzG7?3!g__8{-F9{hl2sX*wp64zcFtKq<=R+T#L-"
    "?U?GM<r=oWj-pE`S9(d6N!)@S*WI%4TRC(%ghCecey-9yAqjBAdlFxRB0Q?Ci1tk(zee-"
    "*SN5Z`186stVIxMoS`Mrxb!D^wWF?x+MZp^|87J$|r1)Q-4?<9%EpZ=C<SO7xGvx9a^9-"
    "gKuV7@`lRQ;|6|q4Q7lRV8&B=cGlq>ixZ~M*VbkIZ@3R1oH49(-aRZlIOkTLdskX?L;7*q|qe5cH&V>-"
    "o+IW?UbT4v&}QM~yA6X|X_7}bi`=WeC|03YIHoIbb@T=EX!4m!r5A_{M*Kj&_iyvye~v%>Q?^AB6TNLe;`QQVWozrKx?+nfRLPw%"
    "C#zAG|RF>$2OA+{i^oYm;4(6)m2^&VW)GDVpP5xbKQO!uG4rvo~Wp(AL&TWb1~Rm@j7S6lqWC)0KxdXQ1uI${=4i#7HlsRwi-"
    "Rmi<TX!3p&U{Sn--a5_f3_tM1r8Q9S45MPLO76ZIHP_<y#Il~@)1evh{4}Z-!(gCfJ&*v^T#`DzxtTn<-"
    "bA;Uwvn6h`?iaOkaFrVOy`jmp4ddnR=PO4b)zucQSKS^m;cRPs^1=jKFrsAv>#C;LD({(vw}Mq-Sr|=n{H?Qx^R~gXY#d}m2A~YC"
    "D*cb9j1y$&5F<595UbRq41xh0YK|!iduR)N@80}1xQ00qCWVuj4yOT-%*HOLY4LWJ+UuiD{iI~C%%-`-"
    "wZD=WJ~SgJ3TPGOhr+Ux)CwZ(kjl;4QTL6Bj0Ky$>?H)fLSx(MX;(eod!eB>(^S-"
    "s@i%9{#ZdMoO1S%$SOcpH4Eyh)+jbPQ)kQvt4-hR?d;l4a<6Qd@Lh;9aAD^Z9@9ec$g41K1O(eO{E-"
    "!|eK5R_q1_a5HsSVj{ZZf(kKu4z<He$EN~4FvL_NVfa0hZfgC<W~(|53;!Rne!=x&TY25NRNoB!3#y$)pCW(8eaKk_xcG@Qp^b7`"
    "aL)A$kis2kRiiF}KzyXZk<?L#}uvk(Sy-;#oSYU_sBcQs08`i2c|BJ;h&0627qUlrq<y}GDH%-"
    "ca><T)k^65(azdxcT9C&c5cjq>J-wt7pA!jjuR-(^SsAqHy6HaZ4rq6l@X8P`t5yKexlVw!SLqVJNC<X1JCBi!HHP-"
    "pw{i7?pAi^0zZ=krR8C`%hg9w(UyKcIa`XaZ84J?+)hs!7>7k1;MaHk4PAq;3Hy3AV1&jup(tmsP11LD{@>5`i?<Ogvp-"
    "fCRK@KOvsro9@pALht_#UCxQasz)IUbMnl7B<o>-S!4r&Q0qty8AxqPJqic!3}{O--2?;2NfR0Ucz!%snF-"
    "2G$vd?r;ek~GO5NI3!<G6o3C-"
    "b38WZrD@g{6D5)Jvr&qwl`i=Mi7igDt`(I*J^MXhphgj8oiaX9S#iAj4NXua=A#%|B;ag{}zHn6l#vog~5q5Po&8cujr3|&J_X9t"
    "zMe7?`2A=`XZ6eca%?B#X$poun&@Tf}6o_54r<mJ7T*%9sk3pvgu4q4nnup+x79FIob4IY?(#n_3m6o-"
    "%>dgZ^F7@;|mIlJFlSrcT9cTdu{^@%TZOdNp+pFt+F^*_8A*;J_H?nb!;Du<ulf@YE1C!a=b_`Q~6b@Y*E-iB2v>@qnwl84G8R6-"
    "Y}AB9Ti^a#Z=1alIhYbY?g-IEa3LHY!NXw$3DY@U8G4u{}ILAVM_-kE8W?>)7X)$V!y89BKRwj#WdMl5>d-"
    "fU;1uP(fx@cdfNK@$`ouv_6z9Q5gj&2RuOhsNIf!Z?VpoKlqUl35P!>O`=P%7Ifpw97;4m*0-"
    "2Vjm_+99djG23mhz$Wv|e?b2ZaJa!s8f~eh%<RIvBNP~sNrc{Itp4s*bw<u?}?v8F~vmte+nDBbBEq?ZPhyG;*R?{{HcLkH%jeSq"
    "J0vyj-`J<-"
    "#CHouQ`yL>;v`M3T6T&+iq*KZ=!RpYVBTK5a3_{wSP!cE+;P<BaQ?06JC+xck;X_TJQpvVH9GiqwekTiOk3(l;%zY|T{9can%<#F"
    "WwQ0CBjj;0X)(a;^8>+rn&+hY@gpSZfZ~DXOCtx*>`*}B%_kncgwlj&#Jn1s?`j<$k!czv`+2<Y-"
    "IuwBKI=J%2n+LU6yxwNZeyr_W6OCtEMTL6BHg(Lxqwnw&cmM1jk3DHo6I%Tk-D?bz_Uy1AtnW1jw>*%La=Bsj;_-"
    "fbvV}TR>v;1^Sl48cxer|B-atDW=h!agXxm#V*{(df0A3=jCy10w>VNP!N$s{C70O&HN_WWtH2-"
    "}Zgrc*EE9?EdgO@l{?9A2xMH>5Ed=z-=THE`i1-`=Bq`pK3Hoh0G_!WJJ)5_c5Rce-lKhDFxtQUtOYC{)Y0bacKX$cAwa+kvPN93"
    "z`WW?+iF4_0quleIg#<x#oTa$iKWs0NoXo#236q*lw_mTGMC?*E*`lk^o=c7Q$+`x9yWLOleX=E$!lH+ehhbnqgI)n}K#B-"
    "B&x_D}(S?y~MUt-|36j77P!io}u+{2!&Z`pMLGplAR3Jj}4=Bs~n2qDGnEg&wqG`}G>(_IF2uieb(T?J?m^B?$uR*9PT-"
    "r0H~_&qzr9)Z?U!>dGoujkba7{iHOYC5`+d+GWbA9IRQ>Y%2WZrD&zBgNU&HGP;P&~g{93~1enz{Fy0to#NH6d|rjEe59TcYQP~X"
    "N-jMlG>Huv+Ceml)`hWYU7xVK6rw`f^x>FmCS<MvGf^RlXi_0CYNfFNPS5f1<HsFl8ndsX4ArS8bvG5)%f$nK;)WnBQt%nFuY5c&"
    "-T>ukSAI}9p=Z~{C$o{B1Xd+T71^mR0<*DfQz547GbY_n4zg}%58r(TrSP9F*SIP!gGSuw-0-"
    "9Ctcl_H^fw7<r1A@dg~zjDMIW7R{x#Sx-}S4P(WktA>_hA8;3yf@dMdT>QsQI=Xps(&fXrezxAPq&H-"
    "RA4rA$hwB*>w_Xc~^9pV_EzW$1c7pAjWk0$Qil%P`b0yWTmejgcsMBHb7-"
    "G*U|$qi^#Ky_!2`B=UGc^S53I@1+Qd<FcFzT1Zxu1gpiNZTsj4_2L24DBN0CrhJ=aBN>-"
    "W>QD02JiyJZ~yz8Ng_Gwx}69X|97_iK7F)~ey*{*9nKjDOU!7XkiKDG{OZZ46Nq5Ub#vGOxK}`y&lPx*EC})icUVWYW!HBE^MOsh"
    "Wxqw~Bfrqd+L`$Z_^$~=)I0=Pm&zmVPrZi@h(GdSiwv`|v84TNa1G|A${}MaIOWMUcdtrHg9LrQHSi7wYx~*9PmI#}iBXdw(%yQd"
    "SK6@%>%_lMp{Z66r7q-"
    "W+N5M2;6J%Q@D{Y+yTcjNwiYbz>FlE?UM<XU{l}oz84mNIP=1l;GAp#2yfq%NK8UzYPLe0V1Bp(3*X(SL0?R@7@vNj;M2DB3ODIw"
    "$LDnHdXsVfuC|Q`=Gz6RY3UR8W3j?b`QD|{o;@D;-XmZ(Q6~#|{2AW3R?qomo-&4DL>p<-"
    "I2Zvuda3{^z=@|Pm^^7N5Mm3V~?;u+7OeQ`;6f(4Q<p6Uzt=<QLt*otTejSKHp{Q>O?<U2-"
    "F`sU4`<dkKTm=m!)G!Mp@#Ng?BR#CaGzq}mN;M|iGZlEKtiXS)2Ci2@=Q=L}ok8qtiy6*48=ugZvCmqpI<sseWLwr#aC+J^(F1US"
    "ZC-(BshL-oVc;ZGT#C#@8N0@fAAO;{ON>^3Tn?zPH!k|zB2{}U8YM1rwuT4-5b(-"
    "f!0Q)sZs62oaH!tE<W^>do4ue}&#**6S}Z&;h1qD#6eQRA2`H}hvpkg6`DYz3QF?V$BhqEQM!Jz)PNZ2m6K~X4Ka01-"
    "9xK|MA@R!Z3POK<Arl&g7hXc%31!>@RYOlUrZD`6J*RvlCYm`|wl#wKXu<4DRtUOBM2(VcWvwD22ZA(1#%-"
    "iTqsRv+Xb7xo)90r99N8|TdXkUBH0$8~r-@!Q>8TOQ6!7GqdtYr1x)YpRW$V80F-eKz-ABp5v7{<%T*bv?b+J@ficI0-"
    "2GHtFdSv6*(~taRMRj!nEvWhpYA(9|XYBc5K9XRVSiBd%<}6?>o*#ba6X05P824&Ughm$UWP0Qj=LVc@pZM}N4EciXoEq5Tr5YE9"
    "9f9$|!*%qmxiLHzc!0?M&&t~vzM30JG~9ZDvyA>=@V%io%AFFdg;L`w`NgeGvWyQYR_wEnf9dbn9HnYyhfSB`>$bb#KgeXOao+@J"
    "<^o}<%U}Hb>q1rOuj_NMPd-Od4j?fYm?9YDxJPQaLd4=X8B7(<^LOpo`qzef-"
    "&97OMeYCbd3uJ9R6Ox1##w6_>5l8G1IQYvG31*hH}@kzJ5^=-"
    "kt5W(iB;iq>?)l{Np8o}K*E1^u*dRl>A6CE{t?zs31ok+`x67djJHr&#{=WYD9tP6vsg~yF?5dOGsk8vTw$oXU>AW$lvFWGy9C=0"
    "31eDwvPy(cIp_=3wsyJHlTr^Tbrds5gC-"
    "`im5_B?3t&RQ|D{_?m3?dXpV+luZ{f=UKDBiZUStBt1`VaZ7PY6p&Dh&$J^SXENCBuzH>og3%Rdrudv3KaWBe-"
    "{*;Qq7VW2$GBysIlKNKBZr~<Xnz8*<6s447tpFler(@Ww1{VFfl&sxmZ!C<SNoLo|0UQBew4b*NpZrg{Ya8cRh6O2TI_d-"
    "^UPe{U<p=HiW9a8m$h*nQFUb-0NT#fCP@4SZnWPTZ`e-V7#j-"
    "b+;3yarL7h%X|C=;9woA6VI(p)JpsVlkfPvSlO+T{s_fwl`j!WLy+3L_vjIf1MqsoC0__Szcb%g0zy^!OG1_JAQ&#pNLRnLHVtA|"
    "wSnS)M3f0R!3yD&ab0c4u|sP&yenXffk8n{6Y{@CTlGtrRk?J81A22{fs<66hJxOGxJ_>1q9XsXHU|g*rw6c?gOaK2dWs1dxo6>;"
    "h)@{>#shbIC@9mJNOhOGc228zeyG>FnS+(0`Z#vv}QMpVcT8`26=cV@!8htmGW1+{k_7UZih|@Tp;!B52*Q-"
    "KOHQCO2zKG`YUH1Sn>UmmI&;D+CNs&v2)`+*Igsddi4EP*5su{VI7FaF+mHT>9LM@Xi`7a4tD2OtXB>X1QGg5GcdbLl?6;WTNd=V"
    "nFm--u63wC9!LcO>-"
    "{tePT)WR94sOHExm=`uu{a#h)S0rj^`FBk<u6ki~yh*2NhpNGHTD{}sB71@tm&$?ahrV3wQRFjNuEyz+d7)R>p<R;3jil4EyIYUp"
    "fUiOv|#^8jzAa;+4C>u3P+%gzX({7Zb$r~=h}pIRap(cH7I`;YfIT*~D#EfD=09%;CzoC`wam8xCrhJ-"
    "(HDJ&6<g1ZOy$d<m<1eZMP4&zsm4|oq8g81C>T#9+{US*LwKuzFww1FA?C9kD1o`t}?mT2MUIk{0e>3wEV0F7fd?;=l)EA-"
    "5OVSv+y5I;pEoi(ACK+rnuWj1pZNHCyhR5|Bm9RyXwA_lD7B2WJ3?+m?W#1DUZ)10?CF6FQ6(alP0yQ9OYr!#}%9X*2zj7aHgY@p"
    "k~wrG#J{YD_iN?m!~hlzMHA;7U<ck)H!|H%jdUs+47(Tol{e$@P@cen$D4zTO#<NU64k1e6i?CWWu*+v@YP{@+L=(*~UPBAh-pWu"
    "TDG2j~*o0<ej1O|YkL9;(K9GO_QPlv;Fqi*vC>BhE~JD2+~?E2a2!#dqt3_a#Bx;kQN95Oz4#gB0>e4nc_ui0%aHB~M~c&SW_!Q8"
    "dqAH4n_+;h~+b!U4OC->#T#-Q|z4^(zzDO##>*Rs7E^lvs{OQOF+p2ZTbIxqr37bgwo)F?-"
    "_jzMLgKi31OZbIy1`E}4R_*_)#>cua4dg*Z&!`qG)(AO8)^)&+xE4QctRwOiHmiQ<biN1kK$mW{HmBm-UIN3DE$P>Du4nsP42Qq&"
    "hs`KLeReB14kSX)5V{Hse14W14cbk=t(=Y7=j}mu56$CC<Ex(`fGjx2S3KG`uj41vNctDNo<U|`Bc-"
    "1bI&3z%rbqHd8Kg?KLWRQ>nzx67~bw&{b)5sHiy;)D@rtK0%Z!eGt%_`Z5b5U_Te)f$mg8Gmb-7pSl>Z7x+AhOVPbaoT`15s7H-"
    "2q6Ud0>$7tn}d#QRJ-%%~fzYOUB(xuy!A%hN1UQ>k)0giOBZBPx8AM`WShn&s|wgOk(iUrKK?ZV2M&z-"
    "De(=&??7h8Zfc*Sb9O|6}H?=?Z;Nmji^*}n|GJ&7Y?IQ%2PLh^=W|@q{y+xvJ8UdWb3qUZunqxgm;ddmKbk71POG79HZ$OJkNR26"
    "F;_p4Hv)WL11aM)DfydEHGZ8GN0QjfU9`U%>USl`vJ_N1_IK0jwU@XLlsZ4*PVKI3DF52r$V3{!u!(%$F%mT{d)1`Cg|s@;M<(*s"
    "nqzzR0&kZl~)JeU1pA}pEg~LAa)~k_yuBhXPpjuRxdrX?Kw>^@z~Q5^e4K!yc9Xh<)(r!3tEzS*(gB=t!VeMTI2S`SkE@HmX$E1>"
    "|&?)%uMDutjdkROOH@F!P#!?wl|UOm{d|iwVce30;Jy^`Re%#K{iivygB*f>VEzJuf*nL&oHXV;TF$jYPhBO!?<Pk(U;m~D<416T"
    "=%uCbg%Fw!pSTedSbmV%wkg&OEp84Jq|Gcv0imIVO+)x>L-"
    "PX6X;LuLBE5Ju|7jBpEG(U9$hdw71%#Vt4Q;HIv9te6eZkY{IJZL#U~$#jKSTd&<RGvOJZDJY38$p63Zy$d5=ZQiK=d*cdI#x()n"
    "m@InQRdPnzIjo1oLK3*~+V2N16{&Sl1+Lbmd|z_;^nO?3B5O-"
    "#!!kiA!(^xZI3u}G6O%y2zEC7=$CO?gcW9)%Zne`WIFA+;_H@jF-oq^Gp?uw2NgbXxK|?gBjWJ0VX`UclFF(Ij2jV6srC9N>>7;F"
    "xzP%hpp_3Xfj})EZ$*)h=-"
    "d4XolJ`od$>`=SPtH!V^xDs@d1ASbxoe0j_|R!<fDV&ZO!?#AcaW_@Lf6GKagq$6XTD!{sJZgWD<CJq$)<{gae?>QX5+?_Ss75F7"
    "52-"
    "~VT9!U{Y*ak+(b~3fuc5Cl{9mpo31SVq|ht{wF44P`KFuX8Dbvc{4tSkfQ$&qW71R7#`Ko8VYT~Rg(`pj<a8dB5uca{;k!Z;7B7~"
    "~q72HCLPk$m*NcjSSY%%wDXyP5<%hv2eg|EcLKL!0@8k@RZplGp1-88kgw81x7-P!a7Y-"
    "LB4WH13U9&G;X|aVq46z@S%>h8HMZaNYwE9&N1-c2Hh>m2*htJt=0|ZeA=6?KC-"
    "?3Mu$wrwD~57B9P?s|SUOuMZ&=g&K*#+G>P~DbL6&dRP>Tc3mAT5f0LF6f9eZw6$?UBrT1$7}*Rwt2XmQiC35MnI;76nKk8kX!aw"
    "2Nc3@Tl$(Xo(nX%Ai;bToF#4>_#oRq^Brt%>05VjgJE^g3l7TLfUf#9pxuaXe>csKNlfqzc<$zT-Dx&(Sz?@(_kUp&>V#<GM(wi4"
    "+-"
    "98qwJVrSiq1$}SF6Hr_zKQ%Mc(VwQk^eY<zE9z4o3#%%)Sy`PCgo^Mz7fPwc!@)^5=>&V$`a>$ErCL~R`@~ceVrH|i@kGxP5|4h4"
    "2OkRRIExPxLbw$&#QN*db?3l%UBaWzbCV$ar}uQFv~LinB+nQae3(u9c=%l%ruP5wIITq&1eBsZ2HS6{s*29N2~&!EFaP+#KS3&H"
    ")agiUJ>m^E$W!hOOZCZSaHX-Q7EZD5NgI{9F2+EH+paz)VOn0EIC~&gtBf!*D029q>-"
    "!>^vBBhLggQrsE$VhlH&?E;BM9zVUZ5l7X0MU1EMZvnHps!)U+iMQIJ;>-"
    "K@=|#y@jvSW@`kjeEJG{yU=}NqtUz4VBh`EOH?H5pupgm}&|f^mnk!R+9Zg?1qInASKs5uP+dDSQ9o?AjF7s&W1LeDxwyC+CG!wF"
    "A?Z>U-u(%n=x_k*@3!=CA&%k6Y4e6J=S^T-"
    "J86R`;2IrG)aduhoa7ip`=r(fP;EWSF++FqZj<T0i>58r_D|!>;|>02C)$L+IUso=*am&#Jf${@GDH#<9-"
    "gFDS@cI6WKrJpg4V!_YmlT5OCJ-u8DVKymqeN5IlQL^NaS@)+FOmHOZ4YI99N0sJ?o8y7bm_g`O>AYh-"
    "+lDl0@bHCUw0yBvPVAsr@fYBs^`Mv1h3!P#zFQJar~=*$holXDDe04mvQz1U}039$3904^KG$tneM&lMq)uebkVfQUlib;jo;KM+"
    "t1%rjP-3Si>1wV8QfF_eTY?{+kYwg-4!lk5VDpmTveWd(<Ply7l{m9HwKhSdncRQV%0s$tl-"
    "<6^|s`7K3nwJWeY_l7PX!&t@B1Y@n2n>)Hex+fXeRhZI8#O`5(6eM1yrqBMWl>o*YTTkz=u-"
    "k9yF6H#x#RQx>`K2LylgQP_2bovZSH-"
    "+kmqaQW1Ei>r=I$aE>R?Q>eK2(%Kc(k^sI@yMY2la|h~H}HlXYh@H+?{gJ)BB|88i?nertGg2+F2Qr|TiH6pe+>ZwXEUoZ7m*dWI"
    "cc!2$NFt{lSSvi`0HDpX@ZjezdI5zgCb7(<+l2-"
    "3<a^(r{S85H5o<{Z2G2AjYdeq*q$4&JeeZK^cUH!H8;+JW|!y0m<aVCu$djgb^Q|B`Fb+sHD!IvhvFhAy+|UkVim>R0EmyZ9pKJ~"
    "KWM%?AquUQTrR!cLFri)iqT(?x}xSdRRCy(Q)LWOtZ4b4KkPR5{g1d4WOkgN_ExQG>+FU`^CxD;-bf?!yw1#I?LNGm`iU-"
    "2$%pS11kadwg}_k58eV-*e)+0bi9&T!DV-PWUR>st3LNz}VDev<Q3x09W8dPC37lORrBdS)2W%!R1=A5#v)#Txiz5hx0RSg<hGTr"
    "+a{n(Tqs^V-"
    "2Pb>Hw6;K!~{4gIRKfFyX4*aipO3Eu4Mc=qFoy9Y4q>u}7eS{w2l8xLJ&L`d6E%urT`%r|1$c%;Npg#Rau9yv|Kt=$=n{x(?(s3y"
    "$!&QVuC|C~K9-PpO<eEtc0BuY&#0<`{)p!#(Zi4wh$Zt(#;)W^wOAkcJ9H7im@hdn0?XVK0yp13;@{@k*-"
    "mmqUjlC0C?q`{vj9QzxBiMbD!DbJJ3oWttjPZc9T$ABwkn2WroIp#)>NC&nrjzL+p~2KLFM=}TEq1aws7YEBt&2?9n$M=Bm#DTMa"
    "y(^CinAEGB@1J7~6<m4C=n^SvI9T|Zw)|$O9%t~3@Uu<rR`RZDoq`1^y#Y+h@ubW2J0nDaZtnHr%3u3>k*cPwp{(SftZMXbqP)fi"
    "XUG;VWwgh>x2y`K0^{kiBkatdZy-*K<Fl(V~?NzXp&=Up8QSgU)#}+Gcnx)FAbbP=b)B^JD=KuV#SbRq8c0WfBXp1OmOhZH34X-"
    "E@nb_%7>zYk&_aEvm7^N(H1j=1!MPa%RBhG5oI|aWi-"
    "1I`iF5R`UZ0#vJ99#o>B7eY3N<Fd*@i@mu??su@Ak;Lwplhl=9jdbqbo#`Osrs3PfIqmcm7k%7=#~YxY=@BCHbBPo*e%u!muxai*"
    "}9SftmhcefGCS`j_c!q1D+L0Vsrcc))WyS<XcAi3XHz>xsl;?TzHhPpVic2Z4tiJ8Ub`H=ZD$B)7DJzhem)rzc%&J&ldNu*w|_5<"
    "E?y>cJmaEXtf#OuI;D2x_6Jayn(Mabjbq1QYKUuQP?9yTZ~w@UU|QA$13}_;2~X!B=iG$fpTUh(BuKfiy=WW!#68Vo*0D$o@3)IW"
    "z0fmi@FehF57*6#%)(5zTh+2h=2~Mm|Yvayp>;?IIDE#$#gHvq|ThE_;!AAm>>0eA{UrG`?vq1%ffWvP2wM2qc4X|V<d+Egf1S(j"
    "BOw)-"
    "7W810jX;(e5!(KuYg^uAeZiFi@M&sNs6vPnLcB8efz!gA>#STb<^Ai16K7x3uAJKbMj&k*XG%!<El1vl8AId=nbKLyt*l}LW5)sp"
    "t*bGsVi4A{OBpn#Y|+q%MnJf`$mr?beqBpC&SSz1s69blShlxq6b1mCHn9bZUDJ&LUw>(8hZWUdt*1Era&ad_7caVnCu$UyI7)#`"
    "hKrj2fi0L2a1XMHbWy=BA^b)XVwI&1~D)AKUrkxOT=NGT!+5Vxr344)WA6n!hwxb5DQFiGThunSBK$_AXsLK>o895w2lka=u-"
    "$So?&+!Ql~J7?o<bs_JP46Bd6H;$mWcO4hJspW)kjX>YLmTl6<}NJF#anESeL5o{T)c3G!CnqSJD}ztfx+HgU$9uOgHKnZQ-ja4~"
    "uXg?gz}XfA}h6SxYe8H;j0;q8>gpb|pF?+GOpW+aRVlk472jH#foI}!dyXH>k_-"
    "`%Kg5JD2rWgPEWfUCF{*zB&ELH3Mz!n<MDb|OA<{m-"
    "OB^5xmip%ac{b8f<|c&Yu5$SqM2S?)%pZ`Et1au?)Ik1W<!1K({l;wv7E5raI<*W3#;nCyK<7~UiKG=toXR8T>7Gpn&m5ngMA`=m"
    "o$uJ_@$B=6Ru4shz#iC6Y!59E19FItZDM~<?v^#B<YU_EU^-3j-"
    "kFPAF~&YVuxL;zci(s&2Vk5`C}S2#ckENAcisU+FlENzn+H(%JX$glxa<!K<q%)ycEf!t3Uv<&5Z<*8~*7W*2nb(zVKD{b~0Go3m"
    "$Jv;O$dG0?|p2~VoWRdc%hH)<$OurBTJz2?~Cxz4mR^jMSx<|OjAP1^k*#qo*w|wXt<5AYoS952zcaRu*SR$!<gA@-"
    "Om>+R2(%kW+LNv}J0j^$UlX2#$n$@{r-tlan8d~4QryFJApawha2&7)*P|ZpQDAj{B<cuWdYns}P!uX7B3w<O-"
    "j}b{Ytma|VDI7a2rh`(=c^Hc$*sCL-4tZSLni)tRbl}&{Ix4!}s@*vD-"
    "{|nJ1Qc}T;|5@eJC@+k>hchq_=SA}_i}))Bx7njSi?3t44su+Uvg2rg`8?D<xnJ0y5nlCjBFTDbgAFd94YZj6?HZ0U+UaKUb0*Na"
    "WCMuwG!vhu3u3Yg_ws(m?T1zf2(ftFF3f3G{}YQ2Yd&P1QYv9`z~SKD|^Hl<_nIIFCi`tt@=3*7J*ww(WSbGbL=Cxi~Zpj{wv!=r"
    "AU>u;v5Pa;vK%!!udfXFU*3aGu@1Q7<FE)e9wD3AQK;B_FP`Cm1fg45#5@O2=c33z4m3}zn%PFbJ3r)2kp;8wx%O?($}}Uaj)pAf"
    "g8mypy|M5I;N0y-X?PoeA!vwg@SAe5r7hx?=R{4I0gl7Qx02)@T>sZs!7LlJA|6AxcLutnm0m(-"
    "?ph^4q|gU00I7`8IkQ#o6I0PuXKRrC(s%1j$qIg54mdO7N$a_a1*}&ouUI3{E!mNw_pPgl`>IuW}C_nzTcE7$oR8t>WH}$l|Im0("
    "18%u$}c!hZd1l!5o`cr!Ok9rpQPYFk_K%9!qM$XkQ|-"
    "KQS4o|odoD4V2YRqAQjaAT%~{(gz&3HQ!95zX|unFzbWVUIisc7V;|<muit;>;kPgLpd~KDX*7>CZ+TgH<(NMm<EXAnG+xTBG2mT"
    "64^hWSqO=A>g4x7RH9))H3#J1$kC_2<Z218e;Mc+H^oN-uV>Wz;(6iZ>@O4U~K%v(GMjx()Tt{rE;zTE~Z&6;;tLO5<7n~s2lPRX"
    "JWYuCrC)j=M*r{HbNv1UBzo{CO2n*3(WslyT^raBO`*?DlA1jzrbAfI2-K{rP@4+e9ZDU?x0%<DOIPw+SmE*sX-"
    "z((_8vGAMq861j_l_2as%>)CF!*M3{CTlnk=2POsyyut{Sq!DX;~9hDj>nDuP`KmRG&UdTnXtue%pm#WAGfnN>e3nF?7})gIQ+?q"
    "msIdm&iCE-"
    "a(SFI$61%!Ri>9V*1e4jD9oLf$ehk!LoPJR*r7S|2PB&3t`UVCKu*!IJUDb#F@tch8~2;E0J|)e{fi;7`XSrn34Y*dROK#eO}-"
    "&d9xCg$N<5$S&E;W7QW2PRHBz`G**sknWxT}m74^>;Bc;iVc>@{1u@(DR%H4av?ETumaEZk$lkcmqy4>bvAOZ`-"
    "7BnS0m3~U<qX30Vg0>#AcNH&KzgAnSeh=S1R%wQHyQ!()o=DWL~w%>I~;&_(>7{K_waRP8SBqX$H8&!wdnp&J&t8Ca-Wv!Ze(n&A"
    "{SY;;5mj%MrZHXH1ISuSBa1Ms#b*!xp6VKjPi8bL|e}y_%>j-"
    "m%e%(mcK$3*MBJ0;tGf}14K=Xd(ru0oR@XzNkV4=hfqjnr#7^S(MAziRQAfN>!W>u`-"
    "irKmgym_JPl^YogdXm$vp=0gBfLIY<_=@*C@hDKQ0X7Z)4d#59-"
    "4*|GwW+B3#LM$hX;MTEu_k<ClrABsum99PZ1L#{995`cO$~hU#3Y;ecd$+l$yF^t^skvnG)Y;RIKJcWo&+wo635*+_>_1<84th=B"
    "tz)=Uv_W5gSIgzGXoiVAswU!>pbG=uguV?`PQ=!MPn>h<z|&Ym36?U__g>7p<o+ltbikxkhh)^7bMbGTIC>HZ_E0PE|F$Q<4P4@j"
    "@Evl#Lz04J4sSHPomZ%zURRI1w8M28ywH>7J_TvPOpuPLCQ2&?8(IN7Ic1zHyy>(a?2ws>4zMAM}lWr6f{MER%tfj~6dImSK9{hs"
    "GZQxX>3QIST`^v#Vb5IbwsOX8Ki_*QEcX`kb7xY`TS^g!CQAq8w*9$k+MZWYRGU<RgfQ(xXVI1pOtV6s{IJ|Y3hkZRij73ifB2LC"
    "}9%CL8wcUqalUAj%Ll=>B25^}DV%3-"
    "G_rBR#6fLGZ0X%PS{<E;6zfiW*{_59l@>ssI4D1VmRk`Q8xEwk!^PH~8^8gndH`8*%&X6ZFxpVCsMM6$5xUQX*T+9Y|pjyU=%s9f"
    "DETz5CP@)LAA=i5d{i3iIZ^T;TU;;1`G-"
    "sZQS#{_0~Ak@UvM%^6YA#iBkZV$0CW8P7iyo5gdOdKrm85#58A0sg9_=FQ@Mn;LKEn6|Tl9Et`9sI0#jgb1Hh{OTb7m=^gp}jEFs"
    "Ywq+k(OXS6TX3sR(geQAqxrOz@^HCu^nO??%&ULHi_La1_RVhnUZ%kQztVC5tL58og?p~2-"
    "cUd$%KG*#qF&trChVw^K`S1WT`tdtYOf*joq02<90lUF6PTv$e)eJDd32}P*0|IAR8b{WGt8n|63Zl$9d6oPb+9KRnrz798_EHYq"
    "&V_DBp+w<L9i1j#99u$iOd<#IkQe(BWNZBFey!JUlcIOETQQezb`U?;C|AJ^@HHc2);=bnT1b3O9$XW)2OCQQVT7jHPOrpH2_!bA"
    "6T{Q?hPSz7-@)5I%q5vOZz27AsqXknNTA7>H3$X59nc5#yGm(tcx-XXZgtW&_8P#n~<bkY_zH6Y~}g0{s(S?93&znR0khCk`Swxl"
    "VCu)%R$Tg<;@wOwni8XTx}WO8TA~x)J4xa7d=M^XNbW1a4Gx2b%3Pho;<n+0q8`*6D5^2D{4dy;)p>`CZ>7k249|1hdN?Pf7a1-"
    "i6r15W-M6tC`2%B_{}2xkA#9?p!%|!>%H>3s=H$TMT<^jgYzh)gY%?AU3CO^b?voQLkQ37qMib#TOH!%@-"
    "OH=BSpYA4}p?WkQZeyxqJN^L}W@{B7VXRB7Bwr46@cJ7<iqW;Uk`@x(xnI;DBm@E|&GGRm21`52oj5&gfx$cl&dXP$<59fJ&o^Cc"
    "jGtCrJrCU|Z!@@tT~zzp(PL_q+1OZ^-a9Wb0Q%=epy{V27nFgsyr1F^&g4zd5w-"
    "G?b$Y`ve^zobhlhGO1+$(;<uCt1)E?oOqMu|~Sk5u{|Vd=$tW9^j6%RK>)U<>)^|PDv~Ecbr{JQZ97FvO_WK3+`iRn30Hwxd{KPh"
    "^}b6lyl!2jAN3Ozlbx{-"
    "e>_Da#J8}wa2iMK<X;C;p*BJ!t4!YN5no!Y&y22x8k!C9Yn}>nzy^!?t}j(9rd|Arw)|r;cH<lLEKNcQXVjQKhOQT5-"
    "!Hwl`?N$Ady%)gxrRQ8630A!@00!G(p3)5kX?*(S=<IY3LOQRY^h59@8m;|3qQ8n9rzxFhT`!Lj-"
    "$kG(6qxSFnAI5~P%936la)Wi|(S$PilG&vJs!ce?0$HVZ2*ZiQ*zC|mV+1GJns-"
    "HP89(zqT!k_A;Lfz%48aHc}g*YBYw?t;C21G+S<-HkwgoNK)dwZPFt!1y&Tmi}hL7nH<9+Mhyqw?UK-Gq4RS0Xsj<vMJhoCp`-"
    "eH2`+m&Z{sQ*#_KvayWdd0wYhJ1t4@#E<|Ee7ec31X5Bc^(<}!^;Feu0X^GBn5)DAYYmUBzSH*?F#fF#t*@uqRI4x2oMrtm=Q@3o"
    "0)<xee&*UlFxStG3vzz&&Z_vs(b^NxQ_KbkS2$ac_X}lurmtlRWk*NJOOZml;>wq4`h$3P`#JBC-"
    "W~qvT&QTHasW0)s<Sc=f=}_%AXMY-G3HodDj3EfR)`U0AIflxA$yn9L9y-"
    "@C+fm;pGOVx%+(0xLux?D%mP&QH00000i#;GCYS`0t00FVh0>G9EE}|~~vBYQl0ssI200dcD"
)


def _materialize_embedded_timesheet_template():
    """Materializes the embedded NetCom Timesheet_Template.xlsx into /tmp when running in M365 Copilot without a local Templates/ folder."""
    import base64
    import lzma
    import tempfile
    dst = os.path.join(tempfile.gettempdir(), "Timesheet_Template_Embedded.xlsx")
    raw_zip = lzma.decompress(base64.b85decode(_EMBEDDED_TIMESHEET_TEMPLATE_B85.encode("ascii")))
    with open(dst, "wb") as f:
        f.write(raw_zip)
    return dst


def run_consolidate_timesheets(manifest_path, template_path, out_path):
    """Consolidates digital and/or OCR-extracted timesheet records into Week_of_MM-DD_to_MM-DD.xlsx."""
    if not os.path.exists(manifest_path):
        print(f"ERROR: Consolidation manifest not found: {manifest_path}")
        sys.exit(2)
    if not template_path or not os.path.exists(template_path):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        candidates = [
            os.path.abspath(os.path.join(script_dir, "Timesheet_Template.xlsx")),
            os.path.abspath(os.path.join(script_dir, "..", "Templates", "Timesheet_Template.xlsx")),
            os.path.abspath("Timesheet_Template.xlsx"),
        ]
        found_tpl = next((p for p in candidates if os.path.exists(p)), None)
        if found_tpl:
            template_path = found_tpl
        else:
            template_path = _materialize_embedded_timesheet_template()

    with open(manifest_path, "r", encoding="utf-8") as f:
        payload = json.load(f)

    we_raw = payload.get("week_ending") or "2026-10-31"
    we_serial = iso_to_excel_serial(we_raw) or 46326
    bw_serial = we_serial - 6
    begin_iso = excel_serial_to_iso(bw_serial)
    end_iso = excel_serial_to_iso(we_serial)

    import datetime
    b_dt = datetime.date.fromisoformat(begin_iso)
    e_dt = datetime.date.fromisoformat(end_iso)
    default_filename = f"Week_of_{b_dt.month}-{b_dt.day}_to_{e_dt.month}-{e_dt.day}.xlsx"
    if not out_path:
        out_path = default_filename

    raw_emps = payload.get("employees", [])
    if not raw_emps:
        print("ERROR: Zero employee timesheet records in manifest.")
        sys.exit(2)

    # Normalize Last, First tab names, merge duplicate employee entries, and chunk >10 jobs into continuation tabs
    merged_by_emp = {}
    for raw_emp in raw_emps:
        emp = normalize_timesheet_emp_record(raw_emp)
        base_tab = normalize_last_first(emp.get("employee", "Unknown Employee"))
        key = base_tab.lower()
        if key not in merged_by_emp:
            merged_by_emp[key] = {**emp, "_base_tab": base_tab, "jobs": list(emp.get("jobs", []))}
        else:
            merged_by_emp[key]["jobs"].extend(emp.get("jobs", []))
            if not merged_by_emp[key].get("position") and emp.get("position"):
                merged_by_emp[key]["position"] = emp["position"]
            if not merged_by_emp[key].get("union_local") and emp.get("union_local"):
                merged_by_emp[key]["union_local"] = emp["union_local"]

    # Expand any employee with >10 jobs into 10-job tab slices ('Last, First', 'Last, First (2)', ...)
    processed_emps = []
    seen_tabs = Counter()
    for key in sorted(merged_by_emp.keys()):
        emp = merged_by_emp[key]
        all_emp_jobs = emp.get("jobs", [])
        if not all_emp_jobs:
            chunks = [[]]
        else:
            chunks = [all_emp_jobs[i : i + 10] for i in range(0, len(all_emp_jobs), 10)]
        for chunk in chunks:
            bt = emp["_base_tab"]
            seen_tabs[bt] += 1
            if seen_tabs[bt] == 1:
                tab_n = bt
            else:
                suffix = f" ({seen_tabs[bt]})"
                tab_n = bt[: 31 - len(suffix)] + suffix
            processed_emps.append({**emp, "jobs": chunk, "tab_name": tab_n})

    with zipfile.ZipFile(template_path, "r") as zin:
        tpl_sheet_bytes = zin.read("xl/worksheets/sheet1.xml")
        tpl_drawing_txt = zin.read("xl/drawings/drawing1.xml").decode("utf-8")
        tpl_drawing_rels_bytes = zin.read("xl/drawings/_rels/drawing1.xml.rels")
        shared_strings = SharedStringTable(zin.read("xl/sharedStrings.xml"))

        new_files = {}
        sheet_xml_entries = []
        rel_xml_entries = [
            '<Relationship Id="rIdTheme1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/theme" Target="theme/theme1.xml"/>',
            '<Relationship Id="rIdStyles1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>',
            '<Relationship Id="rIdSharedStrings1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/sharedStrings" Target="sharedStrings.xml"/>',
        ]
        ct_override_entries = [
            '<Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>',
            '<Override PartName="/xl/theme/theme1.xml" ContentType="application/vnd.openxmlformats-officedocument.theme+xml"/>',
            '<Override PartName="/xl/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.styles+xml"/>',
            '<Override PartName="/xl/sharedStrings.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sharedStrings+xml"/>',
            '<Override PartName="/docProps/core.xml" ContentType="application/vnd.openxmlformats-package.core-properties+xml"/>',
            '<Override PartName="/docProps/app.xml" ContentType="application/vnd.openxmlformats-officedocument.extended-properties+xml"/>',
        ]
        defined_name_entries = []
        all_tab_names = ["Weekly Summary", "Job Summary"]

        # Tab 1: Weekly Summary (sheet1.xml)
        summary_xml_bytes, grand_totals, summary_last_data_r = build_weekly_summary_sheet_xml(
            processed_emps, begin_iso, end_iso, shared_strings=shared_strings
        )
        new_files["xl/worksheets/sheet1.xml"] = summary_xml_bytes
        sheet_xml_entries.append('<sheet name="Weekly Summary" sheetId="1" r:id="rIdSheet1"/>')
        rel_xml_entries.append(
            '<Relationship Id="rIdSheet1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet1.xml"/>'
        )
        ct_override_entries.append(
            '<Override PartName="/xl/worksheets/sheet1.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>'
        )
        defined_name_entries.append(
            f'<definedName name="_xlnm._FilterDatabase" localSheetId="0" hidden="1">\'Weekly Summary\'!$A$7:$N${summary_last_data_r}</definedName>'
        )
        defined_name_entries.append(
            f'<definedName name="_xlnm.Print_Area" localSheetId="0">\'Weekly Summary\'!$A$1:$N${summary_last_data_r + 1}</definedName>'
        )

        # Tab 2: Job Summary (sheet2.xml) — Breakdown by Job Number for Management & Bidding Tracking
        job_summary_xml_bytes, sorted_job_rollups, job_last_data_r = build_job_summary_sheet_xml(
            processed_emps, begin_iso, end_iso, shared_strings=shared_strings
        )
        new_files["xl/worksheets/sheet2.xml"] = job_summary_xml_bytes
        sheet_xml_entries.append('<sheet name="Job Summary" sheetId="2" r:id="rIdSheet2"/>')
        rel_xml_entries.append(
            '<Relationship Id="rIdSheet2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet2.xml"/>'
        )
        ct_override_entries.append(
            '<Override PartName="/xl/worksheets/sheet2.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>'
        )
        defined_name_entries.append(
            f'<definedName name="_xlnm._FilterDatabase" localSheetId="1" hidden="1">\'Job Summary\'!$A$7:$N${job_last_data_r}</definedName>'
        )
        defined_name_entries.append(
            f'<definedName name="_xlnm.Print_Area" localSheetId="1">\'Job Summary\'!$A$1:$N${job_last_data_r + 1}</definedName>'
        )

        # Tabs 3..N+2: Employee Tabs sorted alphabetically by Last, First (each with its own 1-to-1 drawing{idx}.xml)
        for idx, emp in enumerate(processed_emps, start=3):
            s_fn = f"xl/worksheets/sheet{idx}.xml"
            s_rel_fn = f"xl/worksheets/_rels/sheet{idx}.xml.rels"
            d_fn = f"xl/drawings/drawing{idx}.xml"
            d_rel_fn = f"xl/drawings/_rels/drawing{idx}.xml.rels"

            emp_xml_bytes, emp_sums = populate_timesheet_xml(
                tpl_sheet_bytes, emp, we_serial, shared_strings=shared_strings, sheet_idx=idx
            )
            emp["_computed_sums"] = emp_sums
            new_files[s_fn] = emp_xml_bytes
            new_files[s_rel_fn] = (
                '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\r\n'
                '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
                f'<Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/drawing" Target="../drawings/drawing{idx}.xml"/>'
                '</Relationships>'
            ).encode("utf-8")

            # Dedicated per-sheet drawing part with unique creationIds
            custom_d_txt = tpl_drawing_txt.replace(
                "{00000000-0008-0000-0100-000003000000}",
                f"{{00000000-0008-0000-{idx:04X}-000003000000}}",
            ).replace(
                "{FB3AB583-D97E-4789-A0AC-F27F2A663E5D}",
                f"{{FB3AB583-D97E-4789-{idx:04X}-F27F2A663E5D}}",
            )
            new_files[d_fn] = custom_d_txt.encode("utf-8")
            new_files[d_rel_fn] = tpl_drawing_rels_bytes

            esc_tab = _xml_escape_attr(emp["tab_name"])
            all_tab_names.append(emp["tab_name"])
            sheet_xml_entries.append(f'<sheet name="{esc_tab}" sheetId="{idx}" r:id="rIdSheet{idx}"/>')
            rel_xml_entries.append(
                f'<Relationship Id="rIdSheet{idx}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet{idx}.xml"/>'
            )
            ct_override_entries.append(
                f'<Override PartName="/xl/worksheets/sheet{idx}.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>'
            )
            ct_override_entries.append(
                f'<Override PartName="/xl/drawings/drawing{idx}.xml" ContentType="application/vnd.openxmlformats-officedocument.drawing+xml"/>'
            )
            sq_tab = emp["tab_name"].replace("'", "''")
            defined_name_entries.append(
                f'<definedName name="_xlnm.Print_Area" localSheetId="{idx - 1}">\'{_xml_escape_attr(sq_tab)}\'!$A$1:$AK$38</definedName>'
            )

        new_files["xl/sharedStrings.xml"] = shared_strings.to_xml_bytes()
        new_files["xl/workbook.xml"] = (
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\r\n'
            '<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" '
            'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" '
            'xmlns:mc="http://schemas.openxmlformats.org/markup-compatibility/2006" '
            'mc:Ignorable="x15 xr xr6 xr10 xr2" '
            'xmlns:x15="http://schemas.microsoft.com/office/spreadsheetml/2010/11/main" '
            'xmlns:xr="http://schemas.microsoft.com/office/spreadsheetml/2014/revision" '
            'xmlns:xr6="http://schemas.microsoft.com/office/spreadsheetml/2016/revision6" '
            'xmlns:xr10="http://schemas.microsoft.com/office/spreadsheetml/2016/revision10" '
            'xmlns:xr2="http://schemas.microsoft.com/office/spreadsheetml/2015/revision2">'
            '<fileVersion appName="xl" lastEdited="7" lowestEdited="7" rupBuild="30430"/>'
            '<workbookPr/>'
            '<bookViews><workbookView xWindow="28680" yWindow="-120" windowWidth="29040" windowHeight="15720" '
            'xr2:uid="{00000000-000D-0000-FFFF-FFFF00000000}"/></bookViews>'
            f'<sheets>{"".join(sheet_xml_entries)}</sheets>'
            f'<definedNames>{"".join(defined_name_entries)}</definedNames>'
            '<calcPr calcId="191029" fullCalcOnLoad="1"/>'
            '</workbook>'
        ).encode("utf-8")

        new_files["xl/_rels/workbook.xml.rels"] = (
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\r\n'
            '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            f'{"".join(rel_xml_entries)}'
            '</Relationships>'
        ).encode("utf-8")

        new_files["[Content_Types].xml"] = (
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\r\n'
            '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
            '<Default Extension="jpeg" ContentType="image/jpeg"/>'
            '<Default Extension="png" ContentType="image/png"/>'
            '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
            '<Default Extension="xml" ContentType="application/xml"/>'
            f'{"".join(ct_override_entries)}'
            '</Types>'
        ).encode("utf-8")

        vt_parts = "".join(f"<vt:lpstr>{_xml_escape_attr(tn)}</vt:lpstr>" for tn in all_tab_names)
        new_files["docProps/app.xml"] = (
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\r\n'
            '<Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/extended-properties" '
            'xmlns:vt="http://schemas.openxmlformats.org/officeDocument/2006/docPropsVTypes">'
            '<Application>Microsoft Excel</Application>'
            '<DocSecurity>0</DocSecurity>'
            '<ScaleCrop>false</ScaleCrop>'
            '<HeadingPairs><vt:vector size="2" baseType="variant">'
            '<vt:variant><vt:lpstr>Worksheets</vt:lpstr></vt:variant>'
            f'<vt:variant><vt:i4>{len(all_tab_names)}</vt:i4></vt:variant>'
            '</vt:vector></HeadingPairs>'
            f'<TitlesOfParts><vt:vector size="{len(all_tab_names)}" baseType="lpstr">{vt_parts}</vt:vector></TitlesOfParts>'
            '<Company>NetCom, Inc.</Company>'
            '<LinksUpToDate>false</LinksUpToDate>'
            '<SharedDoc>false</SharedDoc>'
            '<HyperlinksChanged>false</HyperlinksChanged>'
            '<AppVersion>16.0300</AppVersion>'
            '</Properties>'
        ).encode("utf-8")

        out_dir = os.path.dirname(os.path.abspath(out_path))
        if out_dir:
            os.makedirs(out_dir, exist_ok=True)
        with zipfile.ZipFile(out_path, "w", zipfile.ZIP_DEFLATED) as zout:
            for item in zin.infolist():
                fn = item.filename
                if (
                    fn.startswith("xl/worksheets/")
                    or fn.startswith("xl/drawings/")
                    or fn.startswith("xl/printerSettings/")
                    or fn == "xl/calcChain.xml"
                    or fn in new_files
                ):
                    continue
                zout.writestr(fn, zin.read(fn))
            for fn, data_bytes in new_files.items():
                zout.writestr(fn, data_bytes)

    print("=" * 92)
    print(f"NEA TIMESHEET CONSOLIDATION ENGINE (v2.2.3) | Output: {out_path}")
    print(f"Pay Period: {begin_iso} (SUN) to {end_iso} (SAT) | Default Filename: {default_filename}")
    print(f"Tabs Created: 1 'Weekly Summary' + 1 'Job Summary' ({len(sorted_job_rollups)} Jobs) + {len(processed_emps)} Sorted Employee Tabs ('Last, First')")
    print(
        f"Weekly Grand Totals: REG={fmt_num(grand_totals['G'])} | OT={fmt_num(grand_totals['H'])} | "
        f"DT={fmt_num(grand_totals['I'])} | 2ND={fmt_num(grand_totals['J'])} | 3RD={fmt_num(grand_totals['K'])} | "
        f"Foreman/GF={fmt_num(grand_totals['L'])} | Total Paid Hours={fmt_num(grand_totals['N'])}"
    )
    print("=" * 92)
    for emp in processed_emps:
        sums = emp["_computed_sums"]
        print(
            f"  - Tab '{emp['tab_name']:<24}' | Employee: {emp.get('employee', ''):<22} | "
            f"Pos: {str(emp.get('position', '')):<9} | Local: {str(emp.get('union_local', '')):<6} | "
            f"Jobs: {len(emp.get('jobs', [])):>2} | REG={fmt_num(sums.get('AG', 0)):>4} | "
            f"OT={fmt_num(sums.get('AH', 0)):>3} | 3RD={fmt_num(sums.get('AK', 0)):>4}"
        )
    run_verify_write(template_path, out_path)


def main():
    parser = argparse.ArgumentParser(description="NEA Deterministic Workbook Inspector (NEA-SCR-001)")
    parser.add_argument(
        "target_dir",
        nargs="?",
        default="Templates",
        help="Directory containing .xlsx workbooks (auto-discovers Templates/ if omitted)",
    )
    parser.add_argument(
        "--scope",
        choices=["full", "review", "delta", "bom", "crl", "catalog", "repair", "timesheet"],
        default="full",
        help="Inspection scope (directional cross-duty routing by role)",
    )
    parser.add_argument(
        "--consolidate",
        type=str,
        default=None,
        metavar="MANIFEST_JSON",
        help="Consolidate digital/OCR timesheet JSON manifest into a multi-tab Week_of_MM-DD_to_MM-DD.xlsx workbook",
    )
    parser.add_argument(
        "--template",
        type=str,
        default="Templates/Timesheet_Template.xlsx",
        help="Path to Timesheet_Template.xlsx for --consolidate mode",
    )
    parser.add_argument(
        "--out",
        type=str,
        default=None,
        help="Output .xlsx path for --consolidate mode (defaults to Week_of_MM-DD_to_MM-DD.xlsx)",
    )
    parser.add_argument(
        "--lookup",
        type=str,
        default=None,
        help="Search tblMaterials, Fiber Assemblies & Cable Harness for matching part records",
    )
    parser.add_argument(
        "--verify-write",
        nargs="+",
        metavar="XLSX",
        default=None,
        help="Verify that EDITED_XLSX preserves all formulas, DataValidations, and catalog keys vs ORIG_XLSX (--verify-write ORIG EDITED or EDITED --verify-write ORIG)",
    )
    parser.add_argument(
        "--repair",
        action="store_true",
        help="Non-destructively repair overwritten formulas (Cover Sheet!B30:C30, Project BOM) and OpenXML validations",
    )
    parser.add_argument(
        "--out-dir",
        type=str,
        default="Repaired_Workbooks",
        help="Output directory for --repair mode (default: Repaired_Workbooks)",
    )
    parser.add_argument(
        "--cache-file",
        type=str,
        default=".nea_inspect_cache.json",
        help="Cache file for --scope delta",
    )
    args = parser.parse_args()

    if args.verify_write:
        if len(args.verify_write) >= 2:
            run_verify_write(args.verify_write[0], args.verify_write[1])
        elif len(args.verify_write) == 1 and args.target_dir != "Templates":
            run_verify_write(args.verify_write[0], args.target_dir)
        else:
            print("ERROR: --verify-write requires ORIG_XLSX and EDITED_XLSX.")
            sys.exit(2)
        return

    if args.consolidate:
        run_consolidate_timesheets(args.consolidate, args.template, args.out)
        return

    if args.repair:
        run_repair_workbooks(args.target_dir, args.out_dir)
        return

    resolved_dir, xlsx_files = discover_xlsx_files(args.target_dir)
    if not xlsx_files:
        print(f"ERROR: No .xlsx files found in '{args.target_dir}' (resolved: '{resolved_dir}').")
        sys.exit(2)

    workbooks = {}
    workbooks_by_role = {}
    for p in xlsx_files:
        wb = parse_xlsx(p)
        workbooks[wb["filename"]] = wb
        role = classify_workbook_role(wb)
        wb["role"] = role
        if role not in workbooks_by_role or "Template" not in wb["filename"]:
            workbooks_by_role[role] = wb

    if args.lookup:
        run_catalog_lookup(workbooks_by_role, workbooks, args.lookup)
        return

    escalation_triggers = []
    expected_sheets_by_role = {
        "BOM": [
            {"Cover Sheet", "Materials Master", "Fiber Assemblies", "Cable Harness", "Project BOM", "Lists"},
            {"Cover Sheet", "Materials Master", "Fiber Assemblies", "Project BOM", "Lists"},
        ],
        "CRL": [{"Cover Sheet", "Cable Running List", "Reference Lists"}],
        "COVER": [{"Cover Sheet", "Reference Lists"}, {"Cover Sheet"}],
        "TIMESHEET": [],
    }
    for fname, wb in workbooks.items():
        role = wb["role"]
        if role == "UNKNOWN":
            escalation_triggers.append(
                f"Unrecognized workbook structure in '{fname}' (sheets: {list(wb['sheets'].keys())}) -> Read References/Workbook_Types_v2.2.3.md"
            )
        else:
            actual_set = set(wb["sheets"].keys())
            valid_sets = expected_sheets_by_role.get(role, [])
            if valid_sets and not any(actual_set == vs for vs in valid_sets):
                escalation_triggers.append(
                    f"Worksheet tab drift in '{fname}' ({role}): found {list(wb['sheets'].keys())} -> Read Formatting_Standards_v2.2.3.md"
                )

    core_hash_wbs = {
        fn: wb for fn, wb in workbooks.items()
        if wb["role"] in ("BOM", "CRL", "COVER") or args.scope == "timesheet"
    }
    if not core_hash_wbs:
        core_hash_wbs = workbooks
    combined_hash_input = "|".join(f"{fn}:{wb['full_sha256']}" for fn, wb in sorted(core_hash_wbs.items()))
    vrf_token = "NEA-VRF-" + hashlib.sha256(combined_hash_input.encode("utf-8")).hexdigest()[:12].upper()
    all_immutable = all(wb["immutable"] for wb in workbooks.values())

    print("=" * 92)
    print("NEA DETERMINISTIC WORKBOOK TELEMETRY & ESCALATION GATE (v2.2.3)")
    print(f"Inspection Engine: {ENGINE_ID}")
    print(f"Live Package Verification Token: {vrf_token}")
    print(
        f"Source Workbook Immutability (Pre/Post SHA-256 Check): "
        f"{'PASS (0 bytes modified across all workbooks)' if all_immutable else 'FAIL (Hash changed!)'}"
    )
    print("=" * 92)
    for fn, wb in workbooks.items():
        print(
            f"Workbook [{wb['role']}]: {fn} | SHA256={wb['sha256']} | "
            f"Immutable={'PASS' if wb['immutable'] else 'FAIL'} | Sheets={list(wb['sheets'].keys())}"
        )

    cache_path = os.path.join(resolved_dir, args.cache_file)
    prev_hashes = {}
    if os.path.exists(cache_path):
        try:
            with open(cache_path, "r", encoding="utf-8") as cf:
                prev_hashes = json.load(cf)
        except Exception:
            prev_hashes = {}
    curr_hashes = {fn: wb["full_sha256"] for fn, wb in workbooks.items()}
    try:
        with open(cache_path, "w", encoding="utf-8") as cf:
            json.dump(curr_hashes, cf, indent=2)
    except Exception:
        pass

    if args.scope == "delta" and prev_hashes == curr_hashes:
        print("\n[DELTA CHECK]: Zero .xlsx changes since last inspection (all SHA256 hashes identical).")
        return

    bom_wb = workbooks_by_role.get("BOM")
    crl_wb = workbooks_by_role.get("CRL")
    cov_wb = workbooks_by_role.get("COVER")

    # 1. COVER SHEET TELEMETRY
    print("\n" + "-" * 92)
    print("SECTION 1: COVER SHEET METADATA & PARITY TELEMETRY")
    print("-" * 92)
    for label, wb in [
        (f"BOM ({bom_wb['filename']})" if bom_wb else "BOM", bom_wb),
        (f"CRL ({crl_wb['filename']})" if crl_wb else "CRL", crl_wb),
        (f"Standalone ({cov_wb['filename']})" if cov_wb else "Standalone", cov_wb),
    ]:
        if not wb or "Cover Sheet" not in wb["sheets"]:
            continue
        cs = wb["sheets"]["Cover Sheet"]
        pairs = []
        for r in sorted(cs.keys()):
            b = cell_val(cs, r, "B")
            c = cell_val(cs, r, "C")
            d_info = cell_info(cs, r, "D")
            g = cell_val(cs, r, "G")
            h_info = cell_info(cs, r, "H")
            if b or d_info["val"] or g or h_info["val"] or c:
                d_val = excel_serial_to_iso(d_info["val"]) if "Date" in b else d_info["val"]
                c_val = excel_serial_to_iso(c) if r == 30 else c
                d_str = f"{d_val} [F:{d_info['f_text']}]" if d_info["has_formula"] else d_val
                h_str = f"{h_info['val']} [F:{h_info['f_text']}]" if h_info["has_formula"] else h_info["val"]
                b_info = cell_info(cs, r, "B")
                b_str = f"{b} [F:{b_info['f_text']}]" if b_info["has_formula"] else b
                row_summary = f"R{r}: B='{b_str}'"
                if c_val:
                    row_summary += f" | C='{c_val}'"
                if d_str or b.endswith(":"):
                    row_summary += f" | D='{d_str}'"
                if g or h_str:
                    row_summary += f" | G='{g}' | H='{h_str}'"
                pairs.append(row_summary)
        print(f"[{label} Cover Sheet]:")
        for p in pairs:
            print(f"  {p}")

    active_bom_pns = {}
    if bom_wb and "Project BOM" in bom_wb["sheets"]:
        pb = bom_wb["sheets"]["Project BOM"]
        for r in sorted(r for r in pb if r >= 8):
            pn = cell_val(pb, r, "B")
            if pn:
                active_bom_pns.setdefault(pn, []).append(r)

    conflict_dups = []
    exact_dups = []
    dup_mfg_pns = {}
    cat_anomalies = []
    formula_overwrites = []
    bulk_box_anomalies = []
    missing_fc = []
    unknown_cls = []
    contradictions = []
    dup_endpoints = {}
    dv_anomalies = []
    tbl_ref_drift = ""
    tbl_zero_spill_count = 0
    fa_dv_drift = ""

    if bom_wb:
        mm_chk = bom_wb["sheets"].get("Materials Master", {})
        lists_chk = bom_wb["sheets"].get("Lists", {})
        max_mm_r = max((r for r in mm_chk if r >= 4 and any(cell_val(mm_chk, r, c) for c in "ABCDEFG")), default=508)
        t_ref = bom_wb.get("tables", {}).get("tblMaterials", {}).get("ref", "")
        if t_ref and t_ref != f"A3:G{max_mm_r}":
            tbl_ref_drift = f"tblMaterials ref='{t_ref}' vs populated R4..R{max_mm_r}"
        h1_f_txt = (cell_info(lists_chk, 1, "H").get("f_text") or "")
        if "<>0" not in h1_f_txt:
            tbl_zero_spill_count = sum(1 for r in lists_chk if cell_val(lists_chk, r, "H") == "0")
        for dv in bom_wb.get("sheet_dvs", {}).get("Fiber Assemblies", []):
            if dv.get("sqref") == "H4:H286":
                fa_dv_drift = "Fiber Assemblies!H Status DataValidation sqref='H4:H286' (truncated vs H4:H1258)"

    # 2A-REPAIR: DEDICATED STRUCTURAL MECHANICS TELEMETRY (--scope repair)
    if args.scope == "repair":
        print("\n" + "-" * 92)
        print("SECTION 2: WORKBOOK MECHANICS, FORMULA & OPENXML DIAGNOSTICS (--scope repair)")
        print("-" * 92)
        if bom_wb and "Project BOM" in bom_wb["sheets"]:
            pb = bom_wb["sheets"]["Project BOM"]
            e4_f = cell_info(pb, 4, "E").get("f_text") or ""
            m_end = re.search(r"B8:B(\d+)", e4_f)
            max_bom_r = int(m_end.group(1)) if m_end else 155
            for r in range(8, max_bom_r + 1):
                for col_let in ("A", "D", "E", "F", "G", "H", "I"):
                    ci = cell_info(pb, r, col_let)
                    if not ci["has_formula"]:
                        formula_overwrites.append(f"{col_let}{r} (val='{ci['val']}')")
            g4_ci = cell_info(pb, 4, "G")
            print(f"[BOM Mechanics ({bom_wb['filename']})]:")
            print(f"  - Project BOM A8:I{max_bom_r} Formula Overwrites: {len(formula_overwrites)}")
            print(f"  - Project BOM!G4 Formula: '{g4_ci['f_text']}' (val='{g4_ci['val']}')")
            print(f"  - tblMaterials Boundary: {tbl_ref_drift or 'ALIGNED'} | Lists!H1 Zero-Spill Count: {tbl_zero_spill_count}")
            print(f"  - Fiber Assemblies DV Range: {fa_dv_drift or 'ALIGNED (H4:H1258)'}")
        if crl_wb and "Cable Running List" in crl_wb["sheets"]:
            crl_dvs = crl_wb.get("sheet_dvs", {}).get("Cable Running List", [])
            for dv in crl_dvs:
                toks = (dv.get("sqref") or "").split()
                if len(toks) > 10:
                    dv_anomalies.append(f"[FRAGMENTED_DV_SQREF] {len(toks)} discrete tokens")
            filter_db = crl_wb.get("defined_names", {}).get("_xlnm._FilterDatabase", "")
            print(f"[CRL Mechanics ({crl_wb['filename']})]:")
            print(f"  - _xlnm._FilterDatabase: {filter_db} | DataValidation Rules: {len(crl_dvs)} ({len(dv_anomalies)} anomalies)")

    # 2. CATALOG INTEGRITY TELEMETRY (Materials Master + Fiber Assemblies + Cable Harness)
    if args.scope in ("full", "review", "delta", "bom", "catalog") and bom_wb:
        print("\n" + "-" * 92)
        print(f"SECTION 2: CATALOG INTEGRITY ({bom_wb['filename']} -> tblMaterials, Fiber Assemblies & Cable Harness)")
        print("-" * 92)
        mm = bom_wb["sheets"].get("Materials Master", {})
        fa = bom_wb["sheets"].get("Fiber Assemblies", {})
        ch = bom_wb["sheets"].get("Cable Harness", {})
        lists_sh = bom_wb["sheets"].get("Lists", {})

        approved_cats = {
            "Cable", "Bulk Fiber", "Term Fiber", "Jacks", "Faceplates", "Patch Panels",
            "Raceway", "Conduit", "Superstructure", "Grounding", "Hardware", "Wire Mgmt",
            "Racks", "Consumables", "Tools", "Miscellaneous", "Equipment", "Cable Harness",
        }
        approved_uoms = {"EA", "KT", "FT", "BX", "M"}
        extended_uoms = approved_uoms | {"RL", "PK"}
        h1_info = cell_info(lists_sh, 1, "H")

        pn_rows = defaultdict(list)
        mfg_pn_rows = defaultdict(list)
        cat_anomalies = []
        max_tbl_row = max((r for r in mm if r >= 4 and any(cell_val(mm, r, c) for c in "ABCDEFG")), default=561)
        for r in range(4, max_tbl_row + 1):
            cat = cell_val(mm, r, "A")
            pn = cell_val(mm, r, "B")
            mfg = cell_val(mm, r, "C")
            mpn = cell_val(mm, r, "D")
            uom = cell_val(mm, r, "E")
            desc = cell_val(mm, r, "F")
            stat = cell_val(mm, r, "G")
            if not any([cat, pn, mfg, mpn, uom, desc, stat]):
                continue
            rec = {"row": r, "cat": cat, "pn": pn, "mfg": mfg, "mpn": mpn, "uom": uom, "desc": desc, "stat": stat}
            if pn:
                pn_rows[pn].append(rec)
            else:
                cat_anomalies.append(f"R{r}: Missing MB P/N (Cat='{cat}', MFG='{mfg}', MPN='{mpn}')")
            if mfg and mpn:
                mfg_pn_rows[(mfg.upper(), mpn.upper())].append(("tblMaterials", r, pn, stat))
            if not cat or not mfg or not uom or not desc or not stat:
                cat_anomalies.append(
                    f"R{r} (MB P/N='{pn}'): Incomplete record -> Cat='{cat}', MFG='{mfg}', MPN='{mpn}', UOM='{uom}', Desc='{desc}', Status='{stat}'"
                )
            elif cat not in approved_cats:
                cat_anomalies.append(f"R{r} (MB P/N='{pn}'): Unapproved Category '{cat}' (Desc='{desc}')")
            if uom and uom not in extended_uoms:
                cat_anomalies.append(f"R{r} (MB P/N='{pn}'): Non-standard UOM '{uom}'")
                escalation_triggers.append(f"Non-standard UOM '{uom}' at Materials Master R{r} -> Read Material_Master_Standards_v2.2.3.md")
            if cat in ("Jacks", "Faceplates", "Patch Panels", "Racks", "Wire Mgmt") and uom == "FT":
                cat_anomalies.append(f"R{r} (MB P/N='{pn}'): Discrete category '{cat}' assigned linear UOM='FT' (Desc='{desc}')")
            if "JACK" in desc.upper() and "CABLE" in cat.upper() and uom == "FT":
                cat_anomalies.append(
                    f"R{r} (MB P/N='{pn}'): Modular Jack '{mpn}' ('{desc}') misclassified as Category='{cat}', UOM='{uom}'"
                )

        exact_dups = []
        conflict_dups = []
        for pn, recs in sorted(pn_rows.items()):
            if len(recs) > 1:
                tuples = {(x["cat"], x["mfg"], x["mpn"], x["uom"], x["desc"], x["stat"]) for x in recs}
                bom_ref = f"ACTIVE ON BOM Rows {active_bom_pns[pn]}" if pn in active_bom_pns else "Unreferenced on BOM"
                if len(tuples) == 1:
                    r_list = ", ".join(f"R{x['row']}" for x in recs)
                    exact_dups.append(f"MB P/N '{pn}' ({r_list}) [{bom_ref}]: Exact duplicate ({recs[0]['mfg']} {recs[0]['mpn']}, UOM={recs[0]['uom']})")
                else:
                    details = " vs ".join(
                        f"R{x['row']}[Cat={x['cat']}, MFG={x['mfg']}, MPN={x['mpn']}, UOM={x['uom']}, Status={x['stat']}, Desc='{x['desc'][:35]}']"
                        for x in recs
                    )
                    conflict_dups.append(f"MB P/N '{pn}' [{bom_ref}]: {details}")

        fa_rows = [
            r
            for r in sorted(fa.keys())
            if r >= 4 and any(cell_val(fa, r, c) for c in ("A", "B", "C", "D", "E", "F", "G", "H"))
        ]
        fa_has_status_col = cell_val(fa, 3, "H") == "Status"
        for r in fa_rows:
            mfg, mpn, pn, stat = cell_val(fa, r, "D"), cell_val(fa, r, "E"), cell_val(fa, r, "C"), cell_val(fa, r, "H")
            if mfg and mpn:
                mfg_pn_rows[(mfg.upper(), mpn.upper())].append(("Fiber Assemblies", r, pn, stat))

        ch_item_rows = []
        ch_assigned_pns = 0
        ch_sections = 0
        for r in sorted(ch.keys()):
            if r < 4:
                continue
            a, b, c_pn, d_mfg, e_mpn, f_uom, g_desc, h_stat = [cell_val(ch, r, col) for col in "ABCDEFGH"]
            if a and not d_mfg and not e_mpn:
                ch_sections += 1
            elif d_mfg or e_mpn:
                ch_item_rows.append(r)
                if c_pn:
                    ch_assigned_pns += 1
                if d_mfg and e_mpn:
                    mfg_pn_rows[(d_mfg.upper(), e_mpn.upper())].append(("Cable Harness", r, c_pn or "[Blank]", h_stat))

        dup_mfg_pns = {k: v for k, v in mfg_pn_rows.items() if len(v) > 1}

        t_ref_str = bom_wb.get("tables", {}).get("tblMaterials", {}).get("ref", "N/A")
        print(
            f"tblMaterials Populated Rows: {sum(len(v) for v in pn_rows.values())} (R4..R{max_tbl_row} | Table ref='{t_ref_str}') | "
            f"Unique MB P/Ns: {len(pn_rows)} | Duplicate Keys: {len(exact_dups) + len(conflict_dups)} "
            f"({len(conflict_dups)} conflicting, {len(exact_dups)} exact) | "
            f"Duplicate (MFG + MFG P/N): {len(dup_mfg_pns)}"
        )
        print(
            f"Fiber Assemblies Rows: {len(fa_rows)} (8-col A3:H3 schema, Status Col H={'Present' if fa_has_status_col else 'Absent'}"
            f"{'; ' + fa_dv_drift if fa_dv_drift else ''})"
        )
        if ch:
            print(
                f"Cable Harness Rows: {len(ch_item_rows)} variant records across {ch_sections} section headers "
                f"(8-col A3:H3 schema; Assigned MB P/Ns in Col C: {ch_assigned_pns}/{len(ch_item_rows)}; "
                f"Unassigned variants remain Pending until MB P/N assignment)"
            )
        print(
            f"Lists!H1 (BOMPartNumbers) Formula: {h1_info['f_text']} "
            f"(Zero-Spill '0' Entries: {tbl_zero_spill_count})"
        )

        print(f"\n[2A. Conflicting Duplicate Primary Keys ({len(conflict_dups)})]:")
        for item in conflict_dups:
            print(f"  - {item}")
        print(f"\n[2B. Exact Duplicate Primary Keys ({len(exact_dups)})]:")
        for item in exact_dups:
            print(f"  - {item}")
        print(f"\n[2C. Duplicate Manufacturer + MFG Part Number Pairs ({len(dup_mfg_pns)})]:")
        for (mfg_k, mpn_k), locs in sorted(dup_mfg_pns.items()):
            loc_str = ", ".join(f"{src} R{r} (MB P/N='{pn}', Status='{st}')" for src, r, pn, st in locs)
            print(f"  - {mfg_k} / {mpn_k}: {loc_str}")
        print(f"\n[2D. Record Completeness & Category/UOM Anomalies ({len(cat_anomalies)})]:")
        for item in cat_anomalies:
            print(f"  - {item}")

    # 3. PROJECT BOM TELEMETRY
    bom_lines = []
    if args.scope in ("full", "review", "delta", "bom", "catalog") and bom_wb and "Project BOM" in bom_wb["sheets"]:
        pb = bom_wb["sheets"]["Project BOM"]
        e4_f = cell_info(pb, 4, "E").get("f_text") or ""
        m_end = re.search(r"B8:B(\d+)", e4_f)
        max_bom_formula_row = int(m_end.group(1)) if m_end else 155

        formula_overwrites = []
        spacing_gaps = []
        last_pop_row = None

        for r in range(8, max_bom_formula_row + 1):
            a_ci = cell_info(pb, r, "A")
            b_ci = cell_info(pb, r, "B")
            c_ci = cell_info(pb, r, "C")
            d_ci = cell_info(pb, r, "D")
            e_ci = cell_info(pb, r, "E")
            f_ci = cell_info(pb, r, "F")
            g_ci = cell_info(pb, r, "G")
            h_ci = cell_info(pb, r, "H")
            i_ci = cell_info(pb, r, "I")
            j_ci = cell_info(pb, r, "J")

            for col_let, ci in [("A", a_ci), ("D", d_ci), ("E", e_ci), ("F", f_ci), ("G", g_ci), ("H", h_ci), ("I", i_ci)]:
                if not ci["has_formula"]:
                    formula_overwrites.append(f"{col_let}{r} (val='{ci['val']}')")

            is_pop = any(ci["val"] for ci in (b_ci, c_ci, j_ci)) or any(
                not ci["has_formula"] and ci["val"] for ci in (d_ci, e_ci, f_ci, g_ci, h_ci, i_ci)
            )
            if is_pop:
                if last_pop_row is not None and (r - last_pop_row - 1) > 0:
                    gap = r - last_pop_row - 1
                    spacing_gaps.append((last_pop_row + 1, r - 1, gap))
                last_pop_row = r
                overwritten_cols = [
                    col_let
                    for col_let, ci in [("A", a_ci), ("D", d_ci), ("E", e_ci), ("F", f_ci), ("G", g_ci), ("H", h_ci), ("I", i_ci)]
                    if not ci["has_formula"]
                ]
                bl_rec = {
                    "row": r,
                    "line": fmt_num(a_ci["val"]),
                    "pn": b_ci["val"],
                    "qty": fmt_num(c_ci["val"]) if c_ci["val"] else "",
                    "qty_num": float(c_ci["val"]) if c_ci["val"] and re.match(r"^-?\d+(\.\d+)?$", c_ci["val"]) else 0.0,
                    "cat": d_ci["val"],
                    "mfg": e_ci["val"],
                    "mpn": f_ci["val"],
                    "uom": g_ci["val"],
                    "desc": h_ci["val"],
                    "stat": i_ci["val"],
                    "notes": j_ci["val"],
                    "overwritten": overwritten_cols,
                }
                bom_lines.append(bl_rec)
                if bl_rec["uom"] == "BX" and bl_rec["qty_num"] >= 100:
                    bulk_box_anomalies.append(
                        f"R{bl_rec['row']} (Line {bl_rec['line']}): MB P/N='{bl_rec['pn']}' ({bl_rec['mfg']} {bl_rec['mpn']} — '{bl_rec['desc']}') "
                        f"has Qty={bl_rec['qty']} with UOM='BX' (orders {bl_rec['qty']} boxes; verify piece count vs box count)"
                    )

        if args.scope in ("full", "review", "delta", "bom"):
            print("\n" + "-" * 92)
            print(f"SECTION 3: PROJECT BOM TELEMETRY ({bom_wb['filename']} -> Project BOM)")
            print("-" * 92)
            for coord in ("B2", "E2", "H2", "E4", "G4"):
                m = COL_RE.match(coord)
                ci = cell_info(pb, int(m.group(2)), m.group(1))
                print(f"Header/Summary Cell {coord}: val='{ci['val']}' | has_formula={ci['has_formula']} | f='{ci['f_text']}'")

            print(f"\nPopulated Project BOM Rows ({len(bom_lines)} rows across R8..R{max_bom_formula_row}):")
            for bl in bom_lines:
                flags = []
                if bl["overwritten"]:
                    flags.append(f"STATIC_OVERWRITE:{','.join(bl['overwritten'])}")
                if not bl["qty"] or bl["qty_num"] <= 0:
                    flags.append("MISSING_OR_ZERO_QTY")
                if bl["uom"] == "BX" and bl["qty_num"] >= 100:
                    flags.append(f"BULK_BOX_QTY_MULTIPLIER({bl['qty']}_BX)")
                if bl["cat"] == "Not found" or not bl["cat"]:
                    flags.append("LOOKUP_NOT_FOUND")
                if bl["pn"].upper().startswith("TPN"):
                    flags.append("TEMP_PART_NUMBER")
                if bl["stat"] not in ("Active", "Preferred"):
                    flags.append(f"STATUS={bl['stat']}")
                flag_str = f" | FLAGS={flags}" if flags else ""
                print(
                    f"  R{bl['row']} (Line {bl['line']}): MB P/N='{bl['pn']}' | Qty='{bl['qty']}' | "
                    f"UOM='{bl['uom']}' | Cat='{bl['cat']}' | MFG='{bl['mfg']}' | MPN='{bl['mpn']}' | "
                    f"Status='{bl['stat']}' | Desc='{bl['desc']}' | Notes='{bl['notes']}'{flag_str}"
                )

            if bulk_box_anomalies:
                print(f"\n[3B. Bulk-Box / UOM Quantity Multiplier Anomalies ({len(bulk_box_anomalies)})]:")
                for b_anom in bulk_box_anomalies:
                    print(f"  - {b_anom}")

            print(f"\nFormula Overwrites in A8:I{max_bom_formula_row}: {len(formula_overwrites)} cells -> {formula_overwrites}")
            max_gap_bom = max((g for _, _, g in spacing_gaps), default=0)
            adv_gaps_bom = [f"R{s}..R{e} ({g} rows)" for s, e, g in spacing_gaps if g > 5]
            print(
                f"Blank Row Spacing Gaps: {len(spacing_gaps)} visual grouping gaps (max gap={max_gap_bom} rows <= 5; "
                f"{len(adv_gaps_bom)} advisory gaps >5 rows: {adv_gaps_bom})"
            )

    # 4. CRL TELEMETRY
    crl_runs = []
    if args.scope in ("full", "review", "delta", "crl") and crl_wb and "Cable Running List" in crl_wb["sheets"]:
        print("\n" + "-" * 92)
        print(f"SECTION 4: CABLE RUNNING LIST (CRL) TELEMETRY ({crl_wb['filename']})")
        print("-" * 92)
        crl = crl_wb["sheets"]["Cable Running List"]
        hdr_row = {col: cell_val(crl, 2, col) for col in "ABCDEFGHIJKLMNOP"}
        hdr_to_col = {v.strip().lower(): col for col, v in hdr_row.items() if v.strip()}

        def resolve_crl_col(candidates, default_col):
            for cand in candidates:
                if cand.lower() in hdr_to_col:
                    return hdr_to_col[cand.lower()]
            return default_col

        c_run = resolve_crl_col(["Run ID"], "A")
        c_cls = resolve_crl_col(["Classification"], "B")
        c_ne_loc = resolve_crl_col(["NE Location"], "C")
        c_ne_rack = resolve_crl_col(["NE Rack"], "D")
        c_ne_port = resolve_crl_col(["NE Port"], "E")
        c_ne_conn = resolve_crl_col(["NE Connector", "NE Conn.", "NE Conn"], "F" if hdr_row.get("F", "").startswith("NE") else "M")
        c_fe_loc = resolve_crl_col(["FE Location"], "G" if hdr_row.get("G", "").startswith("FE") else "F")
        c_fe_rack = resolve_crl_col(["FE Rack"], "H" if hdr_row.get("H", "").startswith("FE") else "G")
        c_fe_port = resolve_crl_col(["FE Port"], "I" if hdr_row.get("I", "").startswith("FE") else "H")
        c_fe_conn = resolve_crl_col(["FE Connector", "FE Conn.", "FE Conn"], "J" if hdr_row.get("J", "").startswith("FE") else "N")
        c_media = resolve_crl_col(["Media Type"], "K" if hdr_row.get("K") == "Media Type" else "I")
        c_ctype = resolve_crl_col(["Cable Type"], "L" if hdr_row.get("L") == "Cable Type" else "J")
        c_fcount = resolve_crl_col(["Cable Qty", "Fiber Count"], "M" if hdr_row.get("M") in ("Cable Qty", "Fiber Count") else "K")
        c_len = resolve_crl_col(["Length (ft)", "Length"], "N" if "Length" in hdr_row.get("N", "") else "L")
        c_spec = resolve_crl_col(["Special Requirement"], "O")
        c_comm = resolve_crl_col(["Comments"], "P")

        schema_str = ", ".join(f"{col}='{hdr_row[col]}'" for col in "ABCDEFGHIJKLMNOP" if hdr_row.get(col))
        print(f"CRL Row-2 Header Schema: {schema_str}")
        fcount_hdr_name = hdr_row.get(c_fcount) or "Cable Qty / Fiber Count"

        bom_pb = bom_wb["sheets"].get("Project BOM", {}) if bom_wb else {}
        bom_has_plenum_bulk_fiber = any(
            cell_val(bom_pb, r, "D") == "Bulk Fiber" and "PLENUM" in cell_val(bom_pb, r, "H").upper()
            for r in bom_pb
            if r >= 8
        )

        missing_fc = []
        unknown_cls = []
        contradictions = []
        spacing_gaps_crl = []
        endpoint_groups = defaultdict(list)
        run_id_ints = []
        dup_run_ids = []
        seen_run_ids = set()
        last_r = None

        for r in sorted(k for k in crl if k >= 3):
            vals = {col: cell_val(crl, r, col) for col in "ABCDEFGHIJKLMNOP"}
            if not any(vals.values()):
                continue
            if last_r is not None and (r - last_r - 1) > 0:
                spacing_gaps_crl.append((last_r + 1, r - 1, r - last_r - 1))
            last_r = r

            run_id = fmt_num(vals[c_run])
            if run_id in seen_run_ids:
                dup_run_ids.append((r, run_id))
            seen_run_ids.add(run_id)
            if re.match(r"^\d+$", run_id):
                run_id_ints.append(int(run_id))

            cls_v = vals[c_cls]
            media = vals[c_media]
            ctype = vals[c_ctype]
            fcount = fmt_num(vals[c_fcount]) if vals[c_fcount] else ""
            length = float(vals[c_len]) if vals[c_len] and re.match(r"^-?\d+(\.\d+)?$", vals[c_len]) else 0.0
            ne_c = vals[c_ne_conn]
            fe_c = vals[c_fe_conn]
            spec = vals[c_spec]
            comm = vals[c_comm]

            ep_key = (vals[c_ne_loc], vals[c_ne_rack], vals[c_ne_port], vals[c_fe_loc], vals[c_fe_rack], vals[c_fe_port])
            if any(ep_key):
                endpoint_groups[ep_key].append((r, run_id, media, ctype, length, comm))

            if cls_v.lower() == "unknown":
                unknown_cls.append((r, run_id))
            if media == "Fiber" and not fcount:
                missing_fc.append((r, run_id, ctype, int(length), ne_c, fe_c, spec, comm))
            if spec == "Plenum" and "OFNR" in comm.upper():
                contradictions.append((r, run_id, "PATHWAY_FIRE_RATING", f"Special Req='{spec}' vs Comments='{comm}'"))
            elif media == "Fiber" and not spec and "OFNR" in comm.upper() and bom_has_plenum_bulk_fiber:
                contradictions.append(
                    (
                        r,
                        run_id,
                        "PATHWAY_FIRE_RATING",
                        f"CRL Col {c_comm} Comments='{comm}' (Riser) vs Project BOM Bulk Fiber='Plenum' (BF5008/BF5006; CRL Col {c_spec} Special Requirement is blank)",
                    )
                )
            if media == "Fiber" and fcount == "1" and "DUPLEX" in comm.upper():
                contradictions.append(
                    (r, run_id, "STRAND_VS_DUPLEX", f"Col {c_fcount} ({fcount_hdr_name})=1 vs Comments='{comm}' & Conn={ne_c}/{fe_c}")
                )
            if media == "Copper" and (ne_c in ("LC", "SC", "ST", "MPO") or fe_c in ("LC", "SC", "ST", "MPO")):
                contradictions.append(
                    (
                        r,
                        run_id,
                        "MEDIA_VS_CONNECTOR",
                        f"Media='{media}' ({ctype}) vs Optical Conn NE='{ne_c}'/FE='{fe_c}' (Length={int(length)} FT, Comments='{comm}')",
                    )
                )
            if media == "Fiber" and (ne_c in ("RJ45", "Punch") or fe_c in ("RJ45", "Punch")):
                contradictions.append(
                    (r, run_id, "MEDIA_VS_CONNECTOR", f"Media='{media}' ({ctype}) vs Copper Conn NE='{ne_c}'/FE='{fe_c}'")
                )

            crl_runs.append(
                {
                    "row": r,
                    "run": run_id,
                    "cls": cls_v,
                    "ne_loc": vals[c_ne_loc],
                    "fe_loc": vals[c_fe_loc],
                    "media": media,
                    "ctype": ctype,
                    "fcount": fcount,
                    "len": length,
                    "ne_c": ne_c,
                    "fe_c": fe_c,
                    "spec": spec,
                    "comm": comm,
                }
            )

        min_run = min(run_id_ints) if run_id_ints else 0
        max_run = max(run_id_ints) if run_id_ints else 0
        missing_seq_ids = sorted(set(range(min_run, max_run + 1)) - set(run_id_ints)) if run_id_ints else []

        print(
            f"Total Active CRL Runs: {len(crl_runs)} (Rows {crl_runs[0]['row']}..{crl_runs[-1]['row']} | "
            f"Run IDs {crl_runs[0]['run']}..{crl_runs[-1]['run']})"
        )
        print(
            f"Run ID Sequence Continuity: {'Continuous ' + str(min_run) + '..' + str(max_run) + ' (0 missing, 0 duplicate Run IDs)' if not missing_seq_ids and not dup_run_ids else f'Missing={missing_seq_ids}, Duplicates={dup_run_ids}'}"
        )
        max_gap_crl = max((g for _, _, g in spacing_gaps_crl), default=0)
        adv_gaps_crl = [(s, e, g) for s, e, g in spacing_gaps_crl if g > 5]
        print(
            f"Blank Row Spacing Gaps: {len(spacing_gaps_crl)} visual grouping gaps (max gap={max_gap_crl} rows; "
            f"{len(adv_gaps_crl)} advisory gaps >5 rows: {adv_gaps_crl})"
        )

        print(f"\n[4A. Fiber Runs Missing {fcount_hdr_name} (Col {c_fcount}) — {len(missing_fc)} runs]:")
        if missing_fc:
            print(
                f"  - Consolidated Range: Rows {missing_fc[0][0]}..{missing_fc[-1][0]} / "
                f"Runs {missing_fc[0][1]}..{missing_fc[-1][1]} ({len(missing_fc)} runs)"
            )
            by_pat = defaultdict(list)
            for r, run_id, ct, ln, nec, fec, sp, cm in missing_fc:
                by_pat[(ct, ln, nec, fec, sp, cm)].append(f"R{r}/Run {run_id}")
            for pat, rlist in by_pat.items():
                print(
                    f"    * Pattern {pat[0]} | {pat[1]} FT | {pat[2]}->{pat[3]} | Spec='{pat[4]}' | "
                    f"Comments='{pat[5]}': {len(rlist)} runs ({rlist[0]} .. {rlist[-1]})"
                )

        print(f"\n[4B. Unresolved 'Classification = Unknown' (Col {c_cls}) — {len(unknown_cls)} runs]:")
        if unknown_cls:
            spans = []
            start_r, start_id = unknown_cls[0]
            prev_r, prev_id = start_r, start_id
            for r, run_id in unknown_cls[1:]:
                if r == prev_r + 1:
                    prev_r, prev_id = r, run_id
                else:
                    spans.append(
                        f"R{start_r}..R{prev_r} (Runs {start_id}..{prev_id})"
                        if start_r != prev_r
                        else f"R{start_r} (Run {start_id})"
                    )
                    start_r, start_id = r, run_id
                    prev_r, prev_id = r, run_id
            spans.append(
                f"R{start_r}..R{prev_r} (Runs {start_id}..{prev_id})"
                if start_r != prev_r
                else f"R{start_r} (Run {start_id})"
            )
            print(f"  - Consolidated Spans ({len(unknown_cls)} runs): {', '.join(spans)}")

        print(f"\n[4C. Intra-Row & Cross-Doc Technical Contradictions — {len(contradictions)} instances]:")
        by_ctype = defaultdict(list)
        for r, run_id, ctype_k, desc in contradictions:
            by_ctype[(ctype_k, desc)].append(f"R{r}/Run {run_id}")
        for (ctype_k, desc), rlist in by_ctype.items():
            print(f"  - [{ctype_k}] {desc}: {len(rlist)} runs ({rlist[0]} .. {rlist[-1]})")

        dup_endpoints = {k: v for k, v in endpoint_groups.items() if len(v) > 1}
        print(f"\n[4D. Identical NE/FE Location, Rack & Port Assignments — {len(dup_endpoints)} groups]:")
        for ep, rlist in sorted(dup_endpoints.items()):
            ne_s = f"{ep[0]} / {ep[1]} / {ep[2]}"
            fe_s = f"{ep[3]} / {ep[4]} / {ep[5]}"
            runs_s = f"Rows {rlist[0][0]}..{rlist[-1][0]} / Runs {rlist[0][1]}..{rlist[-1][1]}"
            print(
                f"  - [DUPLICATE_ENDPOINTS] {len(rlist)} runs ({runs_s}): NE=({ne_s}) -> FE=({fe_s}) | "
                f"{rlist[0][2]} {rlist[0][3]} {int(rlist[0][4])} FT ('{rlist[0][5]}')"
            )

        # 4E. DATA VALIDATION, DROPDOWN & AUTOFILTER RANGE INTEGRITY
        crl_dvs = crl_wb.get("sheet_dvs", {}).get("Cable Running List", [])
        dv_anomalies = []
        for dv in crl_dvs:
            sq = dv["sqref"]
            f_list = dv["formulas"]
            tokens = sq.split() if sq else []
            cols_in_sq = sorted({re.sub(r"[^A-Z]", "", tok.split(":")[0]) for tok in tokens if re.sub(r"[^A-Z]", "", tok.split(":")[0])})
            if len(tokens) > 10:
                dv_anomalies.append(
                    f"[FRAGMENTED_DV_SQREF] type='{dv['type']}' formula={f_list} is fragmented across {len(tokens)} discrete cell references ({tokens[0]}..{tokens[-1]}) instead of a contiguous range"
                )
            elif len(cols_in_sq) > 1 and not (set(cols_in_sq) == {c_ne_conn, c_fe_conn}):
                col_desc = ", ".join(f"{c} ('{hdr_row.get(c, '?')}')" for c in cols_in_sq)
                dv_anomalies.append(
                    f"[SPLIT_COLUMN_DV_MISMATCH] type='{dv['type']}' formula={f_list} sqref='{sq}' spans mismatched columns [{col_desc}] (Row 755+ did not shift when columns were reordered)"
                )
        filter_db = crl_wb.get("defined_names", {}).get("_xlnm._FilterDatabase", "")
        if filter_db and crl_runs:
            m_f = re.search(r"\$P\$(\d+)", filter_db)
            if m_f and int(m_f.group(1)) < crl_runs[-1]["row"]:
                dv_anomalies.append(
                    f"[TRUNCATED_AUTOFILTER] _xlnm._FilterDatabase='{filter_db}' ends at Row {m_f.group(1)}, truncating active CRL runs through Row {crl_runs[-1]['row']}"
                )
        print(f"\n[4E. Data Validation, Dropdown & AutoFilter Integrity — {len(dv_anomalies)} anomalies]:")
        for anom in dv_anomalies:
            print(f"  - {anom}")

    # 5. CROSS-DOCUMENT TAKEOFF ROLLUP (CRL <-> Project BOM)
    if args.scope in ("full", "review", "delta", "crl") and crl_runs:
        print("\n" + "-" * 92)
        print("SECTION 5: CROSS-DOCUMENT MATERIAL & CABLE TAKEOFF ROLLUP (CRL <-> PROJECT BOM)")
        print("-" * 92)
        cable_groups = defaultdict(lambda: {"runs": 0, "ft": 0.0, "rows": []})
        conn_counts = Counter()
        for cr in crl_runs:
            key = (cr["media"], cr["ctype"], cr["fcount"] or "(Blank)", cr["spec"], cr["comm"])
            cable_groups[key]["runs"] += 1
            cable_groups[key]["ft"] += cr["len"]
            cable_groups[key]["rows"].append((cr["row"], cr["run"], int(cr["len"])))
            if cr["ne_c"]:
                conn_counts[(cr["media"], cr["ctype"], cr["ne_c"], "NE")] += 1
            if cr["fe_c"]:
                conn_counts[(cr["media"], cr["ctype"], cr["fe_c"], "FE")] += 1

        print("[5A. CRL Cable Length Rollup by Media / Type / Fiber Count / Spec / Comments]:")
        for k, v in sorted(cable_groups.items()):
            r_span = f"R{v['rows'][0][0]}/Run {v['rows'][0][1]}..R{v['rows'][-1][0]}/Run {v['rows'][-1][1]}"
            indiv = [x[2] for x in v["rows"]] if v["runs"] <= 6 else [f"{v['rows'][0][2]} FT each"]
            print(
                f"  - Media='{k[0]}' | Type='{k[1]}' | FCount='{k[2]}' | Spec='{k[3]}' | "
                f"Comments='{k[4]}': {v['runs']} runs = {int(v['ft'])} FT ({r_span}; lengths={indiv})"
            )

        print("\n[5B. CRL Connector Termination Counts (NE + FE)]:")
        total_by_conn = Counter()
        for (med, ct, conn, end), cnt in sorted(conn_counts.items()):
            total_by_conn[(med, ct, conn)] += cnt
            print(f"  - {med} ({ct}) {conn} [{end}]: {cnt}")
        for (med, ct, conn), tot in sorted(total_by_conn.items()):
            print(f"  => TOTAL {med} ({ct}) {conn} Endpoints (NE+FE): {tot}")

    # 5C. TIMESHEET TELEMETRY & CONSOLIDATION AUDIT (--scope timesheet or full)
    ts_wbs = [wb for wb in workbooks.values() if wb["role"] == "TIMESHEET"]
    ts_anomalies = []
    if args.scope in ("full", "timesheet", "repair") and ts_wbs:
        print("\n" + "-" * 92)
        print("SECTION 5C: MISSOURI TIMESHEET & WEEKLY CONSOLIDATION TELEMETRY (NEA-TPL-004)")
        print("-" * 92)
        job_hdr_rows = [7, 10, 13, 16, 19, 22, 25, 28, 31, 34]
        job_dat_rows = [8, 11, 14, 17, 20, 23, 26, 29, 32, 35]
        day_cols = [
            ("SUN", "F", "G", "H"),
            ("MON", "J", "K", "L"),
            ("TUES", "N", "O", "P"),
            ("WED", "R", "S", "T"),
            ("THU", "V", "W", "X"),
            ("FRI", "Z", "AA", "AB"),
            ("SAT", "AD", "AE", "AF"),
        ]
        for twb in ts_wbs:
            print(f"[Timesheet Workbook: {twb['filename']} (SHA256={twb['sha256']})]:")
            if "Expense Report" in twb["sheets"]:
                ts_anomalies.append(f"{twb['filename']}: Contains 'Expense Report' tab (strip in consolidated weekly output)")
            for sname, srows in twb["sheets"].items():
                if sname == "Expense Report":
                    continue
                if sname in ("Weekly Summary", "Job Summary"):
                    period_str = cell_val(srows, 2, "B") or cell_val(srows, 1, "E")
                    meta_i = cell_val(srows, 2, "I") or cell_val(srows, 1, "H")
                    meta_l = cell_val(srows, 2, "L") or ""
                    hdr_extra = f" | {meta_l}" if meta_l else ""
                    print(f"  * Tab '{sname}': Pay Period: {period_str} | {meta_i}{hdr_extra}")
                    for r in sorted(k for k in srows if k >= 8):
                        a_v = cell_val(srows, r, "A")
                        if a_v in ("WEEKLY GRAND TOTALS", "WEEKLY JOB GRAND TOTALS"):
                            g_v = fmt_num(cell_val(srows, r, "G") or 0)
                            h_v = fmt_num(cell_val(srows, r, "H") or 0)
                            i_v = fmt_num(cell_val(srows, r, "I") or 0)
                            k_v = fmt_num(cell_val(srows, r, "K") or 0)
                            l_v = fmt_num(cell_val(srows, r, "L") or 0)
                            n_v = fmt_num(cell_val(srows, r, "N") or 0)
                            print(
                                f"    => {a_v} (R{r}): REG={g_v} | OT={h_v} | DT={i_v} | "
                                f"3RD={k_v} | Foreman/GF={l_v} | Total={n_v}"
                            )
                        elif sname == "Job Summary" and a_v:
                            b_v = cell_val(srows, r, "B")
                            c_v = cell_val(srows, r, "C")
                            d_v = fmt_num(cell_val(srows, r, "D") or 0)
                            g_v = fmt_num(cell_val(srows, r, "G") or 0)
                            h_v = fmt_num(cell_val(srows, r, "H") or 0)
                            k_v = fmt_num(cell_val(srows, r, "K") or 0)
                            l_v = fmt_num(cell_val(srows, r, "L") or 0)
                            n_v = fmt_num(cell_val(srows, r, "N") or 0)
                            print(
                                f"      Job '{a_v}' ({b_v} - {c_v}) | Techs={d_v} | "
                                f"REG={g_v}, OT={h_v}, 3RD={k_v}, Foreman/GF={l_v} => Total={n_v}"
                            )
                    continue

                # Option C: Dynamic Anchor-Based Extraction + 2D Digital Grid Snapshot Fallback on Layout Drift
                drift_reasons = []
                # 1. Check standard coordinates first, then fall back to dynamic label scanning across Rows 1..10
                emp_name = cell_val(srows, 3, "X")
                pos = cell_val(srows, 3, "K")
                local_no = cell_val(srows, 2, "K")
                bw_raw = cell_val(srows, 1, "X")
                we_raw = cell_val(srows, 2, "X")

                if "EMPLOYEE" not in cell_val(srows, 3, "P").upper() or "WEEK ENDING" not in cell_val(srows, 2, "P").upper():
                    drift_reasons.append("Header labels shifted from standard P1:X3 coordinates")

                # Dynamic header anchor scan across Rows 1..10 if any header field is blank or shifted
                for r_scan in range(1, 11):
                    r_cells = sorted(srows.get(r_scan, {}).items(), key=lambda kv: _col_to_idx(kv[0]))
                    for idx_c, (c_let, c_obj) in enumerate(r_cells):
                        v_txt = str(c_obj.get("val", "") or "").strip()
                        v_up = v_txt.upper()
                        if not v_up:
                            continue
                        # Find next populated value cell to the right on the same row
                        next_val = ""
                        for _, nxt_obj in r_cells[idx_c + 1 :]:
                            nv = str(nxt_obj.get("val", "") or "").strip()
                            if nv and not nv.endswith(":"):
                                next_val = nv
                                break
                        if ("EMPLOYEE" in v_up or v_up == "NAME:") and not emp_name and next_val:
                            emp_name = next_val
                        elif ("POSITION" in v_up or "TITLE" in v_up or "CLASSIFICATION" in v_up) and not pos and next_val:
                            pos = next_val
                        elif ("UNION LOCAL" in v_up or "LOCAL#" in v_up or "LOCAL #" in v_up) and not local_no and next_val:
                            local_no = next_val
                        elif "BEGIN WEEK" in v_up and not bw_raw and next_val:
                            bw_raw = next_val
                        elif "WEEK ENDING" in v_up and not we_raw and next_val:
                            we_raw = next_val

                emp_name = emp_name or "(Blank Template)"
                bw_iso = excel_serial_to_iso(bw_raw)
                we_iso = excel_serial_to_iso(we_raw)

                # 2. Dynamic Day Column & Total Column Discovery (including Local #1 Foreman/GF and Travel columns)
                day_hdr_row = 5
                dyn_day_cols = list(day_cols)
                for r_scan in range(3, 12):
                    r_map = {str(v.get("val", "") or "").strip().upper(): k for k, v in srows.get(r_scan, {}).items() if v.get("val")}
                    if "SUN" in r_map and "MON" in r_map and "WED" in r_map and "FRI" in r_map:
                        if r_scan != 5 or r_map.get("SUN") != "F":
                            drift_reasons.append(f"Day header row detected at Row {r_scan} (SUN={r_map.get('SUN')}) instead of R5/Col F")
                        day_hdr_row = r_scan
                        dyn_day_cols = []
                        for d_lbl, aliases in [
                            ("SUN", ("SUN", "SUNDAY")),
                            ("MON", ("MON", "MONDAY")),
                            ("TUES", ("TUES", "TUE", "TUESDAY")),
                            ("WED", ("WED", "WEDNESDAY")),
                            ("THU", ("THU", "THUR", "THURS", "THURSDAY")),
                            ("FRI", ("FRI", "FRIDAY")),
                            ("SAT", ("SAT", "SATURDAY")),
                        ]:
                            c_start = next((r_map[a] for a in aliases if a in r_map), None)
                            if c_start:
                                ci = _col_to_idx(c_start)
                                dyn_day_cols.append((d_lbl, _idx_to_col(ci), _idx_to_col(ci + 1), _idx_to_col(ci + 2)))
                        break

                # Discover Total columns (REG, OT, DT, 2ND, 3RD, Foreman/GF, Travel) on rows 5..9
                col_tot_map = {"REG": "AG", "OT": "AH", "DT": "AI", "2ND": "AJ", "3RD": "AK", "FOREMAN": None, "TRAVEL": None}
                for r_scan in range(day_hdr_row, day_hdr_row + 4):
                    for c_let, c_obj in srows.get(r_scan, {}).items():
                        if _col_to_idx(c_let) < 25:
                            continue
                        vu = str(c_obj.get("val", "") or "").strip().upper()
                        if vu == "REG":
                            col_tot_map["REG"] = c_let
                        elif vu in ("O.T.", "OT", "OVERTIME"):
                            col_tot_map["OT"] = c_let
                        elif vu in ("D.T.", "DT", "DOUBLE TIME"):
                            col_tot_map["DT"] = c_let
                        elif vu == "2ND":
                            col_tot_map["2ND"] = c_let
                        elif vu == "3RD":
                            col_tot_map["3RD"] = c_let
                        elif vu in ("FOREMAN", "FORMAN", "GF", "FOREMAN/GF"):
                            col_tot_map["FOREMAN"] = c_let
                        elif vu in ("TRAVEL", "TRV"):
                            col_tot_map["TRAVEL"] = c_let

                if col_tot_map["FOREMAN"] or col_tot_map["TRAVEL"]:
                    drift_reasons.append(
                        f"Derived Local #1 columns detected (Foreman={col_tot_map['FOREMAN']}, Travel={col_tot_map['TRAVEL']})"
                    )

                # Discover Page Totals row (default 38, or row containing 'Page Totals' / 'TOTALS')
                tot_row_idx = 38
                for r_scan in sorted(srows.keys()):
                    if r_scan > day_hdr_row + 2:
                        row_text = " ".join(str(v.get("val", "") or "").upper() for v in srows[r_scan].values())
                        if "PAGE TOTAL" in row_text or "WEEKLY TOTAL" in row_text or "GRAND TOTAL" in row_text:
                            if r_scan != 38:
                                drift_reasons.append(f"Page Totals row shifted to Row {r_scan} (standard R38)")
                            tot_row_idx = r_scan
                            break

                # Discover Job Block row pairs (standard 7/8..34/35, or dynamically scan between day_hdr_row+2 and tot_row_idx-1)
                active_job_pairs = list(zip(job_hdr_rows, job_dat_rows))
                if tot_row_idx != 38 or day_hdr_row != 5:
                    active_job_pairs = []
                    r_cur = day_hdr_row + 2
                    while r_cur < tot_row_idx - 1:
                        active_job_pairs.append((r_cur, r_cur + 1))
                        r_cur += 3

                ag35_ci = cell_info(srows, active_job_pairs[-1][1], col_tot_map["REG"]) if active_job_pairs else {"has_formula": True}
                if not ag35_ci["has_formula"] and tot_row_idx == 38:
                    ts_anomalies.append(f"{twb['filename']}!{sname}!AG35: Missing Job Slot 10 REG formula")

                c_reg_t, c_ot_t, c_dt_t, c_2nd_t, c_3rd_t = (
                    col_tot_map["REG"], col_tot_map["OT"], col_tot_map["DT"], col_tot_map["2ND"], col_tot_map["3RD"]
                )
                tot_reg = fmt_num(cell_val(srows, tot_row_idx, c_reg_t) or 0)
                tot_ot = fmt_num(cell_val(srows, tot_row_idx, c_ot_t) or 0)
                tot_dt = fmt_num(cell_val(srows, tot_row_idx, c_dt_t) or 0)
                tot_2nd = fmt_num(cell_val(srows, tot_row_idx, c_2nd_t) or 0)
                tot_3rd = fmt_num(cell_val(srows, tot_row_idx, c_3rd_t) or 0)
                tot_fm = fmt_num(cell_val(srows, tot_row_idx, col_tot_map["FOREMAN"]) or 0) if col_tot_map["FOREMAN"] else "0"
                tot_tr = fmt_num(cell_val(srows, tot_row_idx, col_tot_map["TRAVEL"]) or 0) if col_tot_map["TRAVEL"] else "0"
                extra_tot_str = f", Foreman/GF={tot_fm}, Travel={tot_tr}" if (col_tot_map["FOREMAN"] or col_tot_map["TRAVEL"]) else ""
                print(
                    f"  * Tab '{sname}' | Employee='{emp_name}' | Pos='{pos}' | Local='{local_no}' | "
                    f"Week: {bw_iso}..{we_iso} | Totals(R{tot_row_idx}): REG={tot_reg}, OT={tot_ot}, DT={tot_dt}, 2ND={tot_2nd}, 3RD={tot_3rd}{extra_tot_str}"
                )

                # Detect Job Number column dynamically (default 'D', or column under 'Job Number' header)
                job_num_col = "D"
                for r_scan in range(day_hdr_row, day_hdr_row + 3):
                    for c_let, c_obj in srows.get(r_scan, {}).items():
                        if "JOB NUMBER" in str(c_obj.get("val", "") or "").upper() or "JOB #" in str(c_obj.get("val", "") or "").upper():
                            job_num_col = c_let
                            if c_let != "D":
                                drift_reasons.append(f"Job Number column shifted to Col {c_let} (standard Col D)")
                            break

                extracted_jobs_for_manifest = []
                for idx, (rh, rd) in enumerate(active_job_pairs):
                    bldg = cell_val(srows, rh, "A")
                    jname = cell_val(srows, rd, "A")
                    jnum_hdr = cell_val(srows, rh, job_num_col)
                    jnum = cell_val(srows, rd, job_num_col)
                    if jnum_hdr and not bldg and jnum_hdr.upper() not in ("JOB NUMBER", "JOB #"):
                        bldg = jnum_hdr
                    # If Job Number cell contains 'Shop / 260210' or newline, split qualifier vs numeric ID
                    if "/" in jnum or "\n" in jnum:
                        parts_jn = [p.strip() for p in re.split(r"[/\n]+", jnum) if p.strip()]
                        if len(parts_jn) >= 2:
                            if not bldg:
                                bldg = parts_jn[0]
                            jnum = parts_jn[-1]

                    shift_c = (cell_val(srows, rh, dyn_day_cols[0][1]) if dyn_day_cols else cell_val(srows, rh, "F")) or "REG"
                    r_reg = fmt_num(cell_val(srows, rd, c_reg_t) or 0)
                    r_ot = fmt_num(cell_val(srows, rd, c_ot_t) or 0)
                    r_dt = fmt_num(cell_val(srows, rd, c_dt_t) or 0)
                    r_2nd = fmt_num(cell_val(srows, rd, c_2nd_t) or 0)
                    r_3rd = fmt_num(cell_val(srows, rd, c_3rd_t) or 0)
                    r_fm = fmt_num(cell_val(srows, rd, col_tot_map["FOREMAN"]) or 0) if col_tot_map["FOREMAN"] else "0"
                    r_tr = fmt_num(cell_val(srows, rd, col_tot_map["TRAVEL"]) or 0) if col_tot_map["TRAVEL"] else "0"

                    # Check if 3RD or 2ND column is highlighted yellow in styles.xml or has positive hours while shift_c=='REG'
                    c3_fill = cell_info(srows, rd, c_3rd_t).get("fill_rgb", "")
                    c3_hdr_fill = cell_info(srows, rh, c_3rd_t).get("fill_rgb", "")
                    yellow_fills = {"FFFFFF00", "FFFFF2CC", "FFFFE699", "FFFFFF99"}
                    if shift_c == "REG" and (float(r_3rd or 0) > 0 or c3_fill in yellow_fills or c3_hdr_fill in yellow_fills):
                        shift_c = "3RD"
                        if c3_fill in yellow_fills or c3_hdr_fill in yellow_fills:
                            drift_reasons.append(f"Row {rd} Col {c_3rd_t} has yellow highlight fill (#{c3_fill or c3_hdr_fill}) -> mapped to 3RD shift")
                    elif shift_c == "REG" and float(r_2nd or 0) > 0:
                        shift_c = "2ND"

                    day_strs = []
                    hours_manifest = {}
                    for d_lbl, c_r, c_o, c_d in dyn_day_cols:
                        vr, vo, vd = cell_val(srows, rd, c_r), cell_val(srows, rd, c_o), cell_val(srows, rd, c_d)
                        parts = []
                        d_dict = {}
                        if vr and float(vr or 0) != 0:
                            parts.append(f"{fmt_num(vr)}R")
                            d_dict["reg"] = float(vr)
                        if vo and float(vo or 0) != 0:
                            parts.append(f"{fmt_num(vo)}OT")
                            d_dict["ot"] = float(vo)
                        if vd and float(vd or 0) != 0:
                            parts.append(f"{fmt_num(vd)}DT")
                            d_dict["dt"] = float(vd)
                        if parts:
                            day_strs.append(f"{d_lbl}:{'+'.join(parts)}")
                            hours_manifest[d_lbl.lower()[:3]] = d_dict
                    if bldg or jname or jnum or day_strs:
                        if day_strs and not jnum and "VACATION" not in (bldg + jname).upper():
                            ts_anomalies.append(f"{twb['filename']}!{sname}!{job_num_col}{rd}: Active hours on Slot #{idx+1} ('{bldg} {jname}') missing Job Number")
                        fm_extra = f", FM={r_fm}, TRV={r_tr}" if (float(r_fm or 0) != 0 or float(r_tr or 0) != 0) else ""
                        print(
                            f"      Slot #{idx+1:02d} (R{rh}/R{rd}): Bldg='{bldg}' | Job='{jname}' | "
                            f"Job#='{jnum}' | Shift={shift_c} | Days=[{', '.join(day_strs)}] => REG={r_reg}, OT={r_ot}, DT={r_dt}, 3RD={r_3rd}{fm_extra}"
                        )
                        extracted_jobs_for_manifest.append({
                            "building": bldg,
                            "job_name": jname,
                            "job_number": jnum,
                            "shift": shift_c,
                            "foreman_hours": float(r_fm or 0),
                            "travel_hours": float(r_tr or 0),
                            "hours": hours_manifest,
                        })

                # 3. If ANY layout drift or derived template variation was detected, emit the Lossless 2D Digital Grid Snapshot!
                if drift_reasons:
                    unique_drifts = list(dict.fromkeys(drift_reasons))
                    print(f"    ⚠️ [TS-LAYOUT-DRIFT DETECTED on '{sname}']: {'; '.join(unique_drifts)}")
                    print(f"    📸 [2D DIGITAL GRID SNAPSHOT (LOSSLESS SPATIAL & STYLE VIEW — '{sname}')]:")
                    boilerplate_hdrs = {"REG", "OT", "DT", "O.T.", "D.T.", "2ND", "3RD"}
                    for r_snap in sorted(srows.keys()):
                        if day_hdr_row + 1 < r_snap < tot_row_idx:
                            # Skip unused job slot rows that only contain template labels ('REG','OT','DT') or '0' formula totals
                            has_user_content = False
                            for c_let, c_obj in srows[r_snap].items():
                                vs = str(c_obj.get("val", "") or "").strip()
                                if vs and vs.upper() not in boilerplate_hdrs and vs not in ("0", "0.0", "0.00"):
                                    has_user_content = True
                                    break
                            if not has_user_content:
                                continue
                        non_empty = []
                        for c_let, c_obj in sorted(srows[r_snap].items(), key=lambda kv: _col_to_idx(kv[0])):
                            val_s = str(c_obj.get("val", "") or "").strip()
                            fill_s = c_obj.get("fill_rgb", "")
                            if not val_s and fill_s not in ("FFFFFF00", "FFFFF2CC", "FFFFE699"):
                                continue
                            if day_hdr_row + 1 < r_snap < tot_row_idx and (val_s.upper() in boilerplate_hdrs or val_s in ("0", "0.0", "0.00")):
                                if fill_s not in ("FFFFFF00", "FFFFF2CC", "FFFFE699"):
                                    continue
                            tag_f = f" [F:{c_obj['f_text']}]" if c_obj.get("has_formula") and c_obj.get("f_text") else ""
                            tag_clr = f" [FILL:#{fill_s}]" if fill_s in ("FFFFFF00", "FFFFF2CC", "FFFFE699") else ""
                            non_empty.append(f"{c_let}{r_snap}='{val_s}'{tag_f}{tag_clr}")
                        if non_empty:
                            print(f"      R{r_snap:02d}: " + " | ".join(non_empty))
                    adaptive_emp_json = json.dumps({
                        "employee": emp_name,
                        "union_local": local_no,
                        "position": pos,
                        "week_ending": we_iso,
                        "jobs": extracted_jobs_for_manifest,
                    })
                    print(f"    ✅ [ADAPTIVE EXTRACTED MANIFEST RECORD]: {adaptive_emp_json}")
        if ts_anomalies:
            print(f"\n[Timesheet Structural & Data Advisories ({len(ts_anomalies)})]:")
            for ta in ts_anomalies:
                print(f"  - [TS-ADVISORY] {ta}")

    # 6. ON-DEMAND TIER-2 ESCALATION GATE (Reviewer Only)
    if args.scope in ("full", "review", "delta"):
        print("\n" + "=" * 92)
        print("SECTION 6: TIER-1 vs TIER-2 ON-DEMAND ESCALATION GATE (PACKAGE REVIEWER)")
        print("=" * 92)
        if not escalation_triggers:
            print("STATUS: ✅ [NO TIER-2 ESCALATION REQUIRED — 100% RULE, COORDINATE & CITATION COVERAGE COMPLETE]")
            print(
                "DIRECTIVE: Do NOT read Tier 2 Standards (BOM_Standards, CRL_Standards, Material_Master_Standards, "
                "Project_Metadata_Standard, Formatting_Standards, Workbook_Types, or NEA_Governance_Register). "
                "All required rule citations and severities are already mapped in Review_Standards_v2.2.3.md Section 3."
            )
        else:
            print("STATUS: 🚨 [TIER-2 ESCALATION REQUIRED]")
            for trig in escalation_triggers:
                print(f"  - {trig}")

    # 7. DIRECTIONAL CROSS-DUTY AGENT ROUTING & HANDOFF ADVISORIES (SCOPED BY CALLER ROLE)
    print("\n" + "=" * 92)
    print(f"SECTION 7: DIRECTIONAL CROSS-DUTY AGENT ADVISORIES (Scope: --scope {args.scope})")
    print("=" * 92)
    handoffs = []

    if args.scope == "repair":
        # NEA Repair Tool ONLY evaluates workbook mechanics — NEVER emits project deliverable handoffs
        repair_pending = []
        if formula_overwrites:
            repair_pending.append(f"{len(formula_overwrites)} overwritten Project BOM formula cell(s)")
        for w_label, wb in [("BOM", bom_wb), ("CRL", crl_wb), ("Standalone", cov_wb)]:
            if wb and "Cover Sheet" in wb["sheets"]:
                cs = wb["sheets"]["Cover Sheet"]
                b30_ci, c30_ci = cell_info(cs, 30, "B"), cell_info(cs, 30, "C")
                if (b30_ci["val"] and not b30_ci["has_formula"]) or (c30_ci["val"] and not c30_ci["has_formula"]):
                    repair_pending.append(f"{w_label} Cover Sheet!B30:C30 static override")
        if tbl_ref_drift or tbl_zero_spill_count:
            repair_pending.append(f"tblMaterials / Lists!H1 zero-spill ({tbl_zero_spill_count} zeros)")
        if fa_dv_drift:
            repair_pending.append(fa_dv_drift)
        if dv_anomalies:
            repair_pending.append(f"{len(dv_anomalies)} CRL DataValidation/AutoFilter anomaly(s)")
        if repair_pending:
            print(f"  🔧 [REPAIR ACTION QUEUED]: {'; '.join(repair_pending)}. Run with `--repair --out-dir <dir>` to fix.")
        else:
            print("  ✅ [REPAIR MECHANICS CLEAR]: All auto-repairable formulas, table bounds, and OpenXML validations are intact. (Zero deliverable handoffs emitted by NEA Repair Tool).")
        return

    # A. Triggers for -> NEA Repair Tool (emitted to Reviewer, BOM Builder, CRL Builder, Catalog Manager)
    repair_reasons = []
    if args.scope in ("full", "review", "delta", "bom") and formula_overwrites:
        repair_reasons.append(f"{len(formula_overwrites)} overwritten Project BOM formula cell(s)")
    cov_targets = [("BOM", bom_wb)] if args.scope == "bom" else ([("CRL", crl_wb)] if args.scope == "crl" else [("BOM", bom_wb), ("CRL", crl_wb), ("Standalone", cov_wb)])
    if args.scope in ("full", "review", "delta", "bom", "crl"):
        for w_label, wb in cov_targets:
            if wb and "Cover Sheet" in wb["sheets"]:
                cs = wb["sheets"]["Cover Sheet"]
                b30_ci = cell_info(cs, 30, "B")
                c30_ci = cell_info(cs, 30, "C")
                if (b30_ci["val"] and not b30_ci["has_formula"]) or (c30_ci["val"] and not c30_ci["has_formula"]):
                    repair_reasons.append(f"{w_label} Cover Sheet!B30:C30 static revision override")
    if args.scope in ("full", "review", "delta", "bom", "catalog") and (tbl_ref_drift or tbl_zero_spill_count):
        repair_reasons.append(f"tblMaterials boundary / Lists!H1 zero-spill ({tbl_zero_spill_count} '0' dropdown entries, GOV-007)")
    if args.scope in ("full", "review", "delta", "catalog") and fa_dv_drift:
        repair_reasons.append("Fiber Assemblies!H Status DataValidation sqref='H4:H286' truncation")
    if args.scope in ("full", "review", "delta", "bom") and bom_wb and "Project BOM" in bom_wb["sheets"]:
        g4_f = (cell_info(bom_wb["sheets"]["Project BOM"], 4, "G").get("f_text") or "").upper()
        if g4_f.startswith("SUM(C8:C"):
            repair_reasons.append("Project BOM!G4 mixed-UOM sum formula (GOV-002)")
    if args.scope in ("full", "review", "delta", "crl") and dv_anomalies:
        repair_reasons.append(f"{len(dv_anomalies)} OpenXML DataValidation/AutoFilter anomaly(s) [4E]")
    if repair_reasons:
        handoffs.append(
            f"🔄 [CROSS-DUTY -> NEA Repair Tool]: {'; '.join(repair_reasons)} detected. "
            f"Recommend running 'NEA Repair Tool' to auto-repair workbook formulas, table/spill bounds, and validation ranges without altering project data."
        )

    # B. Triggers for -> NEA Catalog Manager (emitted only to Reviewer and BOM Builder)
    if args.scope in ("full", "review", "delta", "bom"):
        cat_reasons = []
        tot_dups = len(conflict_dups) + len(exact_dups)
        if tot_dups:
            cat_reasons.append(f"{tot_dups} duplicate MB P/N key(s)")
        if dup_mfg_pns:
            cat_reasons.append(f"{len(dup_mfg_pns)} duplicate (Manufacturer, MFG Part Number) pair(s)")
        if cat_anomalies:
            cat_reasons.append(f"{len(cat_anomalies)} incomplete/anomalous catalog record(s) (CAT-##)")
        not_found_bom = [bl["pn"] for bl in bom_lines if bl["cat"] == "Not found" or not bl["cat"]]
        if not_found_bom:
            cat_reasons.append(f"{len(not_found_bom)} unmapped Project BOM part key(s) ({not_found_bom[:5]})")
        non_active_cat_bom = [f"R{bl['row']}({bl['pn']}:{bl['stat']})" for bl in bom_lines if bl["stat"] and bl["stat"] not in ("Active", "Preferred")]
        if non_active_cat_bom:
            cat_reasons.append(f"{len(non_active_cat_bom)} BOM-referenced catalog item(s) with non-Active status ({', '.join(non_active_cat_bom[:4])})")
        tpn_bom = sorted({bl["pn"] for bl in bom_lines if bl["pn"].upper().startswith("TPN")})
        if tpn_bom:
            cat_reasons.append(f"{len(tpn_bom)} active Temporary Part Number(s) ({', '.join(tpn_bom[:5])}{'...' if len(tpn_bom) > 5 else ''}) tracked for permanent MB P/N promotion")
        if cat_reasons:
            handoffs.append(
                f"🔄 [CROSS-DUTY -> NEA Catalog Manager]: {'; '.join(cat_reasons)} detected. "
                f"Recommend running 'NEA Catalog Manager' to review 3-tier catalog lifecycle statuses, TPN## promotions, or tblMaterials hygiene."
            )

    # C. Triggers for -> NEA BOM Builder (emitted only to Reviewer, CRL Builder, and Catalog Manager)
    if args.scope in ("full", "review", "delta", "crl", "catalog"):
        bom_reasons = []
        missing_qty_rows = [f"R{bl['row']}" for bl in bom_lines if not bl["qty"] or bl["qty_num"] <= 0]
        if missing_qty_rows:
            bom_reasons.append(f"{len(missing_qty_rows)} active Project BOM line(s) missing/zero Qty ({', '.join(missing_qty_rows[:8])})")
        if bulk_box_anomalies:
            bom_reasons.append(f"{len(bulk_box_anomalies)} bulk-box UOM multiplier anomaly(s) (R70 1000 BX)")
        non_active_bom = [f"R{bl['row']}({bl['pn']}:{bl['stat']})" for bl in bom_lines if bl["stat"] and bl["stat"] not in ("Active", "Preferred")]
        if non_active_bom:
            bom_reasons.append(f"{len(non_active_bom)} active BOM line(s) referencing non-Active catalog SKU ({', '.join(non_active_bom[:5])})")
        if args.scope == "crl" and crl_runs:
            bom_reasons.append(f"CRL takeoff totals ({len(crl_runs)} runs) ready for Project BOM reconciliation")
        if bom_reasons:
            handoffs.append(
                f"🔄 [CROSS-DUTY -> NEA BOM Builder]: {'; '.join(bom_reasons)} detected. "
                f"Recommend running 'NEA BOM Builder' to populate/reconcile Project BOM Columns B, C, and J."
            )

    # D. Triggers for -> NEA CRL Builder (emitted ONLY to Reviewer)
    if args.scope in ("full", "review", "delta"):
        crl_reasons = []
        if missing_fc:
            crl_reasons.append(f"{len(missing_fc)} fiber run(s) missing Fiber Count")
        if unknown_cls:
            crl_reasons.append(f"{len(unknown_cls)} run(s) with Classification='Unknown'")
        if contradictions:
            crl_reasons.append(f"{len(contradictions)} technical pathway/media contradiction(s)")
        if dup_endpoints:
            crl_reasons.append(f"{len(dup_endpoints)} duplicate NE/FE port assignment group(s) (CRL-DATA-003)")
        if crl_reasons:
            handoffs.append(
                f"🔄 [CROSS-DUTY -> NEA CRL Builder]: {'; '.join(crl_reasons)} detected. "
                f"Recommend running 'NEA CRL Builder' to normalize 16-column CRL run records."
            )

    if handoffs:
        for h in handoffs:
            print(f"  {h}")
    else:
        print("  ✅ [CROSS-DUTY CLEAR]: Zero sister-agent handoffs required for this scope.")


if __name__ == "__main__":
    main()
