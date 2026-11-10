#!/usr/bin/env python3
"""
Homunculus Deterministic Hardware CAD Envelope (STEP/STL) & Firmware (.cfg) Inspector.
Part of optional add-on `hardware-cad-inspector` (`addons/hardware-cad-inspector/SKILL.md`).

Extracts base outer bounding-box envelopes (`X × Y × Z mm`), closed mesh volumes (`cm³`),
STEP-to-STL outer envelope parity, closed 360° circular surface diameter histograms (`Ø mm`),
and Klipper (`.cfg`) firmware pinouts in a single deterministic pass using 100% Python 3.10+
standard library (`struct`/`math`/`re`).

Enforces the CAD Epistemic Boundary: reports pure geometric measurements without injecting
speculative mechanical role labels (`.F. bore`, `.T. pin/boss`, or COTS nouns) or 3D
coordinate matrices that encourage multi-turn CAD reverse-engineering rabbit holes.

=== DEVELOPER & AI NAVIGATION MAP ===
  Owning Module : `hardware-cad-inspector` (`addons/hardware-cad-inspector/SKILL.md`)
  Callers       : `sync_memory.py` (`--sync-hardware`), `subagent-orchestrator`, `teach-me`, `test_core_skills.py`, `test_claim_verification.py`
  Callees       : `homunculus_paths.py` (`parse_frontmatter_full`)
  Contract      : `scripts/script_contracts.json` [`inspect_hardware_ecosystem.py`]
  CLI Flags     : --vault, --memory-root, --project, --repo, --json-out, --all, --check-cache, --sync-manifest, --force-rescan
  Symbol Index  (jump directly via read_file StartLine/EndLine):
    - def parse_frontmatter (#L112-L114)             | def normalize_part_stem (#L117-L126)
    - def classify_bore_diameter (#L129-L150)        | def _vec_dot (#L153-L154)
    - def _vec_cross (#L157-L164)                    | def _vec_norm (#L167-L168)
    - def _bbox_from_points (#L171-L178)             | def detect_step_unit_scale (#L181-L200)
    - def inspect_step_file (#L203-L406)             | def inspect_stl_file (#L409-L512)
    - def inspect_cfg_file (#L515-L555)              | def scan_repo_hardware (#L558-L690)
    - def _upsert_frontmatter_keys (#L693-L714)      | def _replace_html_marker_block (#L717-L724)
    - def render_manifest_markdown (#L727-L920)      | def resolve_projects (#L923-L991)
    - def main (#L994-L1254)
=== END NAVIGATION MAP ===
"""

import argparse
from collections import Counter
from datetime import datetime
import hashlib
import json
import math
import os
import re
import struct
import sys
import tempfile
from pathlib import Path
from typing import Dict, List, Optional, Tuple

sys.dont_write_bytecode = True

_SCRIPT_DIR = Path(__file__).resolve().parent
_HOM_ROOT = _SCRIPT_DIR.parents[2]
for _p in (str(_SCRIPT_DIR), str(_HOM_ROOT / "scripts")):
    if _p not in sys.path:
        sys.path.insert(0, _p)
import homunculus_paths  # noqa: E402

DEFAULT_VAULT = "./memory"
DEFAULT_REPOS_ROOT = "."

VERTEX_PT_RE = re.compile(r"#(\d+)\s*=\s*VERTEX_POINT\s*\(\s*'[^']*'\s*,\s*#(\d+)\s*\)")
CARTESIAN_PT_RE = re.compile(
    r"#(\d+)\s*=\s*CARTESIAN_POINT\s*\(\s*'[^']*'\s*,\s*\(\s*([-\d.Ee+]+)\s*,\s*([-\d.Ee+]+)\s*,\s*([-\d.Ee+]+)\s*\)\s*\)"
)
DIRECTION_RE = re.compile(
    r"#(\d+)\s*=\s*DIRECTION\s*\(\s*'[^']*'\s*,\s*\(\s*([-\d.Ee+]+)\s*,\s*([-\d.Ee+]+)\s*,\s*([-\d.Ee+]+)\s*\)\s*\)"
)
AXIS2_RE = re.compile(
    r"#(\d+)\s*=\s*AXIS2_PLACEMENT_3D\s*\(\s*'[^']*'\s*,\s*#(\d+)\s*,\s*#(\d+)\s*,\s*#(\d+)"
)
CIRCLE_RE = re.compile(
    r"#(\d+)\s*=\s*CIRCLE\s*\(\s*'[^']*'\s*,\s*#(\d+)\s*,\s*([-\d.Ee+]+)\s*\)"
)
LINE_RE = re.compile(r"#(\d+)\s*=\s*LINE\s*\(")
EDGE_CURVE_ID_RE = re.compile(
    r"#(\d+)\s*=\s*EDGE_CURVE\s*\(\s*'[^']*'\s*,\s*#(\d+)\s*,\s*#(\d+)\s*,\s*#(\d+)\s*,\s*\.([TF])\."
)
ORIENTED_EDGE_RE = re.compile(
    r"#(\d+)\s*=\s*ORIENTED_EDGE\s*\(\s*'[^']*'\s*,\s*\*\s*,\s*\*\s*,\s*#(\d+)\s*,\s*\.[TF]\."
)
EDGE_LOOP_RE = re.compile(
    r"#(\d+)\s*=\s*EDGE_LOOP\s*\(\s*'[^']*'\s*,\s*\(([^)]*)\)\s*\)"
)
FACE_BOUND_RE = re.compile(
    r"#(\d+)\s*=\s*FACE_(?:OUTER_)?BOUND\s*\(\s*'[^']*'\s*,\s*#(\d+)\s*,\s*\.[TF]\."
)
CYL_SURF_RE = re.compile(
    r"CYLINDRICAL_SURFACE\s*\(\s*'[^']*'\s*,\s*#\d+\s*,\s*([-\d.Ee+]+)\s*\)"
)
CYL_SURF_ID_RE = re.compile(
    r"#(\d+)\s*=\s*CYLINDRICAL_SURFACE\s*\(\s*'[^']*'\s*,\s*#(\d+)\s*,\s*([-\d.Ee+]+)\s*\)"
)
ADV_FACE_RE = re.compile(
    r"ADVANCED_FACE\s*\(\s*'[^']*'\s*,\s*\(([^)]*)\)\s*,\s*#(\d+)\s*,\s*\.([TF])\.\s*\)"
)
PRODUCT_RE = re.compile(r"PRODUCT\s*\(\s*'([^']*)'\s*,\s*'([^']*)'")
FILE_NAME_RE = re.compile(
    r"FILE_NAME\s*\(\s*(?:/\*.*?\*/\s*)?'([^']*)'\s*,\s*(?:/\*.*?\*/\s*)?'([^']*)'",
    re.DOTALL,
)
ORIG_SYS_RE = re.compile(
    r"originating_system\s*\*/\s*'([^']*)'", re.IGNORECASE
)

# Generic prefixes/suffixes stripped when matching STEP <-> STL part stems across any CAD project
STEM_PREFIX_RE = re.compile(
    r"^(?:[A-Za-z0-9_.\s]+?\s+-\s+|\[[A-Za-z0-9_]+\]_?)+",
    re.IGNORECASE,
)
STEM_SUFFIX_RE = re.compile(r"(?:\(\d+\)|\s*<\d+>)$")


def parse_frontmatter(text: str) -> Dict[str, str]:
    fields, _body, _line = homunculus_paths.parse_frontmatter_full(text)
    return {k: str(v) for k, v in fields.items()}


def normalize_part_stem(filename: str, repo_prefix: str = "") -> str:
    stem = os.path.splitext(os.path.basename(filename))[0].strip()
    stem = STEM_PREFIX_RE.sub("", stem)
    stem = STEM_SUFFIX_RE.sub("", stem).strip()
    norm = stem.lower().replace(" ", "_").replace("-", "_")
    if repo_prefix:
        rp = repo_prefix.lower().strip("_") + "_"
        while norm.startswith(rp) and len(norm) > len(rp):
            norm = norm[len(rp) :]
    return norm


def classify_bore_diameter(diam_mm: float, include_metric_hint: bool = False) -> str:
    """
    By default (include_metric_hint=False), returns "" so STEP CYLINDRICAL_SURFACE
    histograms emit pure geometric diameters (`Ø6.00mm×4`) without injecting speculative
    COTS component nouns or functional guesses (`bore`, `pin`, `magnet`, `bearing`) into
    `<Project>_Hardware.md` that could poison `verify_claims.py`'s closed-world truth oracle.
    """
    if not include_metric_hint:
        return ""
    if 2.45 <= diam_mm <= 2.85:
        return "~M3 tap/thread range"
    if 2.95 <= diam_mm <= 3.45:
        return "~M3 clearance range"
    if 3.95 <= diam_mm <= 4.35:
        return "~M4 clearance / 4mm range"
    if 4.65 <= diam_mm <= 5.05:
        return "~4.7-5.0mm range"
    if 5.10 <= diam_mm <= 5.55:
        return "~M5 clearance range"
    if 5.85 <= diam_mm <= 6.25:
        return "~6.0mm cylindrical surface"
    return ""


def _vec_dot(a: Tuple[float, float, float], b: Tuple[float, float, float]) -> float:
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def _vec_cross(
    a: Tuple[float, float, float], b: Tuple[float, float, float]
) -> Tuple[float, float, float]:
    return (
        a[1] * b[2] - a[2] * b[1],
        a[2] * b[0] - a[0] * b[2],
        a[0] * b[1] - a[1] * b[0],
    )


def _vec_norm(a: Tuple[float, float, float]) -> float:
    return math.sqrt(a[0] * a[0] + a[1] * a[1] + a[2] * a[2])


def _bbox_from_points(pts: List[Tuple[float, float, float]]) -> Tuple[float, float, float]:
    if not pts:
        return (0.0, 0.0, 0.0)
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    zs = [p[2] for p in pts]
    spans = sorted([max(xs) - min(xs), max(ys) - min(ys), max(zs) - min(zs)])
    return (round(spans[0], 2), round(spans[1], 2), round(spans[2], 2))


def detect_step_unit_scale(text: str) -> Tuple[float, bool]:
    """Return (multiplier_to_mm, unit_scale_assumed)."""
    lu_matches = re.findall(r"LENGTH_UNIT\(\).*?;", text, flags=re.DOTALL)
    for blk in lu_matches:
        if ".MILLI." in blk and ".METRE." in blk:
            return (1.0, False)
        if "INCH" in blk:
            return (25.4, False)
        if ".METRE." in blk:
            return (1000.0, False)
    raw_pts = [
        (float(m.group(2)), float(m.group(3)), float(m.group(4)))
        for m in CARTESIAN_PT_RE.finditer(text)
    ]
    if raw_pts:
        raw_bbox = _bbox_from_points(raw_pts)
        max_span = max(raw_bbox)
        if 0.0 < max_span < 1.0:
            return (1000.0, True)
    return (1.0, True)


def inspect_step_file(filepath: str, repo_prefix: str = "", repo_root: str = "") -> Dict[str, object]:
    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
        text = f.read()

    scale, scale_assumed = detect_step_unit_scale(text)

    export_ts = "unknown"
    fn_match = FILE_NAME_RE.search(text[:4096])
    if fn_match:
        export_ts = fn_match.group(2).strip()[:10]

    orig_sys = "CAD"
    os_match = ORIG_SYS_RE.search(text[:4096])
    if os_match:
        raw_sys = os_match.group(1).strip()
        orig_sys = "Onshape" if "ONSHAPE" in raw_sys.upper() else raw_sys[:20]

    products = []
    for pm in PRODUCT_RE.finditer(text):
        p_name = pm.group(1).strip() or pm.group(2).strip()
        if p_name and p_name not in products:
            products.append(p_name)

    cpts: Dict[str, Tuple[float, float, float]] = {}
    all_coords: List[Tuple[float, float, float]] = []
    for cm in CARTESIAN_PT_RE.finditer(text):
        pt_id = cm.group(1)
        xyz = (
            float(cm.group(2)) * scale,
            float(cm.group(3)) * scale,
            float(cm.group(4)) * scale,
        )
        cpts[pt_id] = xyz
        all_coords.append(xyz)

    dirs: Dict[str, Tuple[float, float, float]] = {}
    for dm in DIRECTION_RE.finditer(text):
        vec = (float(dm.group(2)), float(dm.group(3)), float(dm.group(4)))
        norm = _vec_norm(vec)
        if norm > 0.0:
            dirs[dm.group(1)] = (vec[0] / norm, vec[1] / norm, vec[2] / norm)

    axes: Dict[str, Tuple[str, str, str]] = {}
    for am in AXIS2_RE.finditer(text):
        axes[am.group(1)] = (am.group(2), am.group(3), am.group(4))

    verts: Dict[str, Tuple[float, float, float]] = {}
    for vm in VERTEX_PT_RE.finditer(text):
        if vm.group(2) in cpts:
            verts[vm.group(1)] = cpts[vm.group(2)]

    circles: Dict[str, Tuple[str, float]] = {}
    for crm in CIRCLE_RE.finditer(text):
        circles[crm.group(1)] = (crm.group(2), abs(float(crm.group(3))) * scale)

    lines_set = {lm.group(1) for lm in LINE_RE.finditer(text)}
    edge_curves: Dict[str, Tuple[str, str, str]] = {}
    coords: List[Tuple[float, float, float]] = list(verts.values())
    for em in EDGE_CURVE_ID_RE.finditer(text):
        ec_id, v1_id, v2_id, c_id, sense = (
            em.group(1),
            em.group(2),
            em.group(3),
            em.group(4),
            em.group(5),
        )
        edge_curves[ec_id] = (v1_id, v2_id, c_id)
        if c_id in circles and v1_id in verts and v2_id in verts:
            ax_id, r_mm = circles[c_id]
            if ax_id in axes:
                cp_id, n_id, ref_id = axes[ax_id]
                if cp_id in cpts and n_id in dirs and ref_id in dirs:
                    center = cpts[cp_id]
                    normal = dirs[n_id]
                    u_raw = dirs[ref_id]
                    proj = _vec_dot(u_raw, normal)
                    u_vec = (
                        u_raw[0] - proj * normal[0],
                        u_raw[1] - proj * normal[1],
                        u_raw[2] - proj * normal[2],
                    )
                    u_norm = _vec_norm(u_vec)
                    if u_norm > 0.0:
                        u_vec = (u_vec[0] / u_norm, u_vec[1] / u_norm, u_vec[2] / u_norm)
                    v_vec = _vec_cross(normal, u_vec)
                    if v1_id == v2_id:
                        n_steps = 72
                        t1, t2 = 0.0, 2.0 * math.pi
                    else:
                        v1_pt = verts[v1_id]
                        v2_pt = verts[v2_id]
                        d1 = (v1_pt[0] - center[0], v1_pt[1] - center[1], v1_pt[2] - center[2])
                        d2 = (v2_pt[0] - center[0], v2_pt[1] - center[1], v2_pt[2] - center[2])
                        t1 = math.atan2(_vec_dot(d1, v_vec), _vec_dot(d1, u_vec))
                        t2 = math.atan2(_vec_dot(d2, v_vec), _vec_dot(d2, u_vec))
                        if sense == "T":
                            if t2 <= t1:
                                t2 += 2.0 * math.pi
                        else:
                            if t2 >= t1:
                                t2 -= 2.0 * math.pi
                        n_steps = 36
                    step_dt = (t2 - t1) / float(n_steps - 1)
                    for i in range(n_steps):
                        th = t1 + i * step_dt
                        ct = math.cos(th)
                        st = math.sin(th)
                        coords.append(
                            (
                                center[0] + r_mm * (ct * u_vec[0] + st * v_vec[0]),
                                center[1] + r_mm * (ct * u_vec[1] + st * v_vec[1]),
                                center[2] + r_mm * (ct * u_vec[2] + st * v_vec[2]),
                            )
                        )

    pts_use = coords if coords else all_coords
    bbox_mm = _bbox_from_points(pts_use)

    # Identify closed 360° cylindrical surfaces vs open partial-arc fillets/grooves when B-Rep topology is present
    oriented_edges = {om.group(1): om.group(2) for om in ORIENTED_EDGE_RE.finditer(text)}
    edge_loops = {
        elm.group(1): re.findall(r"#(\d+)", elm.group(2))
        for elm in EDGE_LOOP_RE.finditer(text)
    }
    face_bounds = {fbm.group(1): fbm.group(2) for fbm in FACE_BOUND_RE.finditer(text)}
    surf_has_face: Dict[str, bool] = {}
    surf_is_closed_cylinder: Dict[str, bool] = {}
    for af_m in ADV_FACE_RE.finditer(text):
        b_ids = re.findall(r"#(\d+)", af_m.group(1))
        surf_id = af_m.group(2)
        surf_has_face[surf_id] = True
        full_circles = 0
        line_edges = 0
        for b_id in b_ids:
            el_id = face_bounds.get(b_id)
            for oe_id in edge_loops.get(el_id or "", []):
                ec_id = oriented_edges.get(oe_id)
                if ec_id in edge_curves:
                    v1, v2, geom_id = edge_curves[ec_id]
                    if geom_id in circles and v1 == v2:
                        full_circles += 1
                    elif geom_id in lines_set:
                        line_edges += 1
        if full_circles > 0 and line_edges == 0:
            surf_is_closed_cylinder[surf_id] = True

    bore_counter: Counter = Counter()
    for cyl_m in CYL_SURF_ID_RE.finditer(text):
        surf_id, _ax_id, r_raw = cyl_m.group(1), cyl_m.group(2), cyl_m.group(3)
        if surf_has_face.get(surf_id, False) and not surf_is_closed_cylinder.get(surf_id, False):
            # Skip open partial-arc fillets, blends, and edge grooves
            continue
        r_mm = abs(float(r_raw)) * scale
        d_mm = round(r_mm * 2.0, 2)
        if 1.5 <= d_mm <= 65.0:
            bore_counter[d_mm] += 1

    if not bore_counter and not surf_has_face:
        for cyl_m in CYL_SURF_RE.finditer(text):
            r_mm = abs(float(cyl_m.group(1))) * scale
            d_mm = round(r_mm * 2.0, 2)
            if 1.5 <= d_mm <= 65.0:
                bore_counter[d_mm] += 1
    if not bore_counter and circles and not surf_has_face:
        for _, r_mm in circles.values():
            d_mm = round(r_mm * 2.0, 2)
            if 1.5 <= d_mm <= 65.0:
                bore_counter[d_mm] += 1

    sorted_bores = sorted(bore_counter.items(), key=lambda x: (-x[1], x[0]))[:10]
    top_bores = [(d, cnt, classify_bore_diameter(d)) for d, cnt in sorted_bores]
    cylindrical_features = [
        {
            "diameter_mm": d,
            "diameter": d,
            "count": cnt,
        }
        for d, cnt in sorted_bores
    ]

    rel_p = (
        os.path.relpath(filepath, repo_root).replace(os.sep, "/")
        if repo_root
        else os.path.basename(filepath)
    )
    base_f = os.path.basename(filepath)
    return {
        "file": base_f,
        "filename": base_f,
        "rel_path": rel_p,
        "stem": normalize_part_stem(filepath, repo_prefix=repo_prefix),
        "mtime": os.path.getmtime(filepath),
        "export_date": export_ts,
        "cad_system": orig_sys,
        "unit_scale_assumed": scale_assumed,
        "product_count": len(products),
        "products": products,
        "product_stems": sorted(
            {normalize_part_stem(p, repo_prefix=repo_prefix) for p in products if p}
        ),
        "bbox_mm": bbox_mm,
        "top_bores": top_bores,
        "cylindrical_features": cylindrical_features,
    }


def inspect_stl_file(filepath: str, repo_prefix: str = "", repo_root: str = "") -> Dict[str, object]:
    file_size = os.path.getsize(filepath)
    n_tris = 0
    min_x = min_y = min_z = float("inf")
    max_x = max_y = max_z = float("-inf")
    signed_vol_6 = 0.0
    parsed_binary = False

    if file_size >= 84:
        with open(filepath, "rb") as f:
            _header = f.read(80)
            n_tri_hdr = struct.unpack("<I", f.read(4))[0]
            if 84 + (n_tri_hdr * 50) == file_size and n_tri_hdr > 0:
                raw_buf = f.read(n_tri_hdr * 50)
                for (
                    _nx, _ny, _nz,
                    v0x, v0y, v0z,
                    v1x, v1y, v1z,
                    v2x, v2y, v2z,
                    _attr,
                ) in struct.iter_unpack("<12fH", raw_buf):
                    if v0x < min_x: min_x = v0x
                    if v1x < min_x: min_x = v1x
                    if v2x < min_x: min_x = v2x
                    if v0x > max_x: max_x = v0x
                    if v1x > max_x: max_x = v1x
                    if v2x > max_x: max_x = v2x

                    if v0y < min_y: min_y = v0y
                    if v1y < min_y: min_y = v1y
                    if v2y < min_y: min_y = v2y
                    if v0y > max_y: max_y = v0y
                    if v1y > max_y: max_y = v1y
                    if v2y > max_y: max_y = v2y

                    if v0z < min_z: min_z = v0z
                    if v1z < min_z: min_z = v1z
                    if v2z < min_z: min_z = v2z
                    if v0z > max_z: max_z = v0z
                    if v1z > max_z: max_z = v1z
                    if v2z > max_z: max_z = v2z

                    signed_vol_6 += (
                        (v0y * v1z - v0z * v1y) * v2x
                        + (v0z * v1x - v0x * v1z) * v2y
                        + (v0x * v1y - v0y * v1x) * v2z
                    )
                n_tris = int(n_tri_hdr)
                parsed_binary = True

    if not parsed_binary:
        verts: List[Tuple[float, float, float]] = []
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                line = line.strip()
                if line.startswith("vertex "):
                    parts = line.split()
                    if len(parts) >= 4:
                        vx, vy, vz = float(parts[1]), float(parts[2]), float(parts[3])
                        verts.append((vx, vy, vz))
                        if vx < min_x: min_x = vx
                        if vx > max_x: max_x = vx
                        if vy < min_y: min_y = vy
                        if vy > max_y: max_y = vy
                        if vz < min_z: min_z = vz
                        if vz > max_z: max_z = vz
        if verts and len(verts) % 3 == 0:
            n_tris = len(verts) // 3
            for idx in range(0, len(verts), 3):
                v0x, v0y, v0z = verts[idx]
                v1x, v1y, v1z = verts[idx + 1]
                v2x, v2y, v2z = verts[idx + 2]
                signed_vol_6 += (
                    (v0y * v1z - v0z * v1y) * v2x
                    + (v0z * v1x - v0x * v1z) * v2y
                    + (v0x * v1y - v0y * v1x) * v2z
                )

    if n_tris > 0:
        spans = sorted([max_x - min_x, max_y - min_y, max_z - min_z])
        bbox_mm = (round(spans[0], 2), round(spans[1], 2), round(spans[2], 2))
        vol_mm3 = abs(signed_vol_6) / 6.0
        vol_cm3 = round(vol_mm3 / 1000.0, 2)
    else:
        bbox_mm = (0.0, 0.0, 0.0)
        vol_cm3 = 0.0

    rel_p = (
        os.path.relpath(filepath, repo_root).replace(os.sep, "/")
        if repo_root
        else os.path.basename(filepath)
    )
    base_f = os.path.basename(filepath)
    return {
        "file": base_f,
        "filename": base_f,
        "rel_path": rel_p,
        "stem": normalize_part_stem(filepath, repo_prefix=repo_prefix),
        "mtime": os.path.getmtime(filepath),
        "triangles": n_tris,
        "bbox_mm": bbox_mm,
        "vol_cm3": vol_cm3,
        "volume_cm3": vol_cm3,
    }


def inspect_cfg_file(filepath: str, repo_root: str = "") -> Dict[str, object]:
    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
        text = f.read()
    sections = re.findall(r"^\[([^\]]+)\]", text, flags=re.MULTILINE)
    pins = re.findall(
        r"^\s*(?:[a-zA-Z0-9_]*_)?pin\s*[:=]\s*([^\s#]+)", text, flags=re.MULTILINE
    )
    macros = [
        s.split(None, 1)[1].strip()
        for s in sections
        if s.lower().startswith("gcode_macro ") and len(s.split(None, 1)) > 1
    ]
    fans = [
        s.split(None, 1)[1].strip()
        for s in sections
        if s.lower().startswith("fan_generic ") and len(s.split(None, 1)) > 1
    ]
    rel_p = (
        os.path.relpath(filepath, repo_root).replace(os.sep, "/")
        if repo_root
        else os.path.basename(filepath)
    )
    base_f = os.path.basename(filepath)
    return {
        "file": base_f,
        "filename": base_f,
        "rel_path": rel_p,
        "mtime": os.path.getmtime(filepath),
        "sections": sections,
        "pins": pins,
        "macros": macros,
        "fans": fans,
        "scalars": [
            f"[{sec_c}] {m_kv.group(1)}={m_kv.group(2).split('#')[0].strip()}"
            for sec_c, blk_c in re.findall(r"^\[([^\]]+)\]\n((?:(?![^\n]*\[).*(?:\n|$))*)", text, flags=re.MULTILINE)
            for ln_c in blk_c.splitlines()
            if not ln_c.startswith((" ", "\t", "#"))
            for m_kv in [re.match(r"^([a-zA-Z0-9_]+)\s*[:=]\s*(.+?)\s*$", ln_c)]
            if m_kv and m_kv.group(1).lower() not in ("gcode",)
        ],
    }


def scan_repo_hardware(repo_path: str, mtime_only: bool = False) -> Dict[str, object]:
    step_files: List[str] = []
    stl_files: List[str] = []
    cfg_files: List[str] = []
    doc_files: List[str] = []

    for root, dirs, files in os.walk(repo_path):
        dirs[:] = [d for d in sorted(dirs) if not d.startswith(".")]
        for f in sorted(files):
            if f.startswith("."):
                continue
            full = os.path.join(root, f)
            low = f.lower()
            if low.endswith((".step", ".stp")):
                step_files.append(full)
            elif low.endswith(".stl"):
                stl_files.append(full)
            elif low.endswith(".cfg"):
                cfg_files.append(full)
            elif low.endswith(".md"):
                doc_files.append(full)

    cad_tracked = sorted(step_files + stl_files + cfg_files)
    inv_entries: List[str] = []
    cad_mtimes: List[float] = []
    for p in cad_tracked:
        st = os.stat(p)
        cad_mtimes.append(st.st_mtime)
        rel_p = os.path.relpath(p, repo_path).replace(os.sep, "/")
        inv_entries.append(f"{rel_p}:{st.st_size}:{int(st.st_mtime)}")
    latest_cad_mtime = max(cad_mtimes, default=0.0)
    inventory_sha256 = hashlib.sha256("\n".join(inv_entries).encode("utf-8")).hexdigest()[:16]
    latest_cad_iso = (
        datetime.fromtimestamp(latest_cad_mtime).strftime("%Y-%m-%d %H:%M:%S")
        if latest_cad_mtime > 0
        else "none"
    )
    latest_doc_mtime = max((os.path.getmtime(p) for p in doc_files), default=0.0)
    latest_doc_iso = (
        datetime.fromtimestamp(latest_doc_mtime).strftime("%Y-%m-%d %H:%M:%S")
        if latest_doc_mtime > 0
        else "none"
    )

    if mtime_only:
        return {
            "repo_path": repo_path,
            "latest_mtime": latest_cad_mtime,
            "latest_iso": latest_cad_iso,
            "latest_doc_iso": latest_doc_iso,
            "inventory_sha256": inventory_sha256,
            "step_files": step_files,
            "stl_files": stl_files,
            "cfg_files": cfg_files,
            "steps": step_files,
            "stls": stl_files,
            "cfgs": cfg_files,
            "step_only_parts": [],
        }

    repo_base = os.path.basename(os.path.abspath(repo_path))
    repo_prefix = re.split(r"[_\-\s]+", repo_base)[0] if repo_base else ""

    steps_data = [inspect_step_file(p, repo_prefix=repo_prefix, repo_root=repo_path) for p in step_files]
    stls_data = [inspect_stl_file(p, repo_prefix=repo_prefix, repo_root=repo_path) for p in stl_files]
    cfgs_data = [inspect_cfg_file(p, repo_root=repo_path) for p in cfg_files]

    docs_text = ""
    for dp in doc_files:
        with open(dp, "r", encoding="utf-8", errors="ignore") as f:
            docs_text += "\n" + f.read()
    docs_lower = docs_text.lower()

    step_by_stem: Dict[str, Dict[str, object]] = {
        str(s["stem"]): s for s in steps_data
    }
    stl_by_stem: Dict[str, Dict[str, object]] = {
        str(s["stem"]): s for s in stls_data
    }

    assembly_body_stems: set = set()
    for s in steps_data:
        if int(s.get("product_count", 0)) > 2:
            assembly_body_stems.update(s.get("product_stems", set()))

    for stl_item in stls_data:
        stem = str(stl_item["stem"])
        stem_spaced = stem.replace("_", " ")
        stl_file = str(stl_item["file"])
        stl_stem_raw = os.path.splitext(stl_file)[0]

        if (stl_file in docs_text) or (stl_stem_raw in docs_text):
            doc_ref = "Yes"
        elif (stem in docs_lower) or (len(stem_spaced) >= 4 and stem_spaced in docs_lower):
            doc_ref = "Yes (Prose)"
        else:
            doc_ref = "Unlisted"

        stl_item["in_docs"] = doc_ref != "Unlisted"
        stl_item["doc_ref"] = doc_ref

        if stem in step_by_stem:
            st_bbox = step_by_stem[stem]["bbox_mm"]
            sl_bbox = stl_item["bbox_mm"]
            max_diff = max(
                abs(float(st_bbox[i]) - float(sl_bbox[i])) for i in range(3)
            )
            if max_diff <= 0.20:
                stl_item["step_sync"] = "MATCH (<=0.2mm)"
            else:
                stl_item["step_sync"] = f"DRIFT (delta {max_diff:.2f}mm)"
        elif stem in assembly_body_stems:
            stl_item["step_sync"] = "IN_ASSEMBLY_STEP"
        else:
            stl_item["step_sync"] = "STL_ONLY"

    step_only_parts = [
        str(s["file"])
        for s in steps_data
        if str(s["stem"]) not in stl_by_stem and int(s["product_count"]) <= 2
    ]

    return {
        "repo_path": repo_path,
        "latest_mtime": latest_cad_mtime,
        "latest_iso": latest_cad_iso,
        "latest_doc_iso": latest_doc_iso,
        "inventory_sha256": inventory_sha256,
        "steps": steps_data,
        "stls": stls_data,
        "cfgs": cfgs_data,
        "step_only_parts": step_only_parts,
    }


def _upsert_frontmatter_keys(md_text: str, updates: Dict[str, str]) -> str:
    if not md_text.startswith("---"):
        return md_text
    end_idx = md_text.find("\n---", 3)
    if end_idx == -1:
        return md_text
    fm_lines = md_text[4:end_idx].splitlines()
    body = md_text[end_idx + 4 :]
    seen = set()
    new_fm: List[str] = []
    for line in fm_lines:
        if ":" in line:
            k = line.split(":", 1)[0].strip()
            if k in updates:
                new_fm.append(f"{k}: {updates[k]}")
                seen.add(k)
                continue
        new_fm.append(line)
    for k, v in updates.items():
        if k not in seen:
            new_fm.append(f"{k}: {v}")
    return "---\n" + "\n".join(new_fm) + "\n---" + body


def _replace_html_marker_block(md_text: str, marker_name: str, new_inner: str) -> str:
    start_tag = f"<!-- {marker_name}:START -->"
    end_tag = f"<!-- {marker_name}:END -->"
    pattern = re.compile(re.escape(start_tag) + r".*?" + re.escape(end_tag), re.DOTALL)
    replacement = f"{start_tag}\n{new_inner.strip()}\n{end_tag}"
    if pattern.search(md_text):
        return pattern.sub(lambda _: replacement, md_text, count=1)
    return md_text


def render_manifest_markdown(
    project_name: str,
    parent_note_stem: str,
    scan: Dict[str, object],
    existing_meta: Optional[Dict[str, str]] = None,
    existing_text: Optional[str] = None,
) -> str:
    steps: List[Dict[str, object]] = scan["steps"]  # type: ignore
    stls: List[Dict[str, object]] = scan["stls"]  # type: ignore
    cfgs: List[Dict[str, object]] = scan["cfgs"]  # type: ignore
    step_only: List[str] = scan["step_only_parts"]  # type: ignore

    meta = existing_meta or {}
    entity_val = meta.get("entity", "My_Organization")
    compartment_val = meta.get("compartment", "private")
    telemetry_domain_val = meta.get("telemetry_domain", "hardware")
    mode_val = meta.get("mode", "obsidian")
    rel_or_abs_repo = meta.get("local_path", str(scan["repo_path"]))

    drift_count = sum(
        1 for s in stls if str(s.get("step_sync", "")).startswith("DRIFT")
    )
    parity_status = "DRIFT_DETECTED" if drift_count > 0 else "SYNCED"
    now_date = datetime.now().strftime("%Y-%m-%d")

    cad_lines: List[str] = []
    if stls:
        cad_lines.extend(
            [
                "### STL Mesh Envelope & Volume Telemetry",
                "",
                "| STL File | Envelope `X × Y × Z (mm)` | Solid Volume (`cm³`) | Triangles | STEP Sync | Doc Ref |",
                "| :--- | :---: | :---: | :---: | :---: | :---: |",
            ]
        )
        for s in stls:
            bx, by, bz = s["bbox_mm"]  # type: ignore
            doc_flag = str(s.get("doc_ref", "Yes" if s.get("in_docs") else "Unlisted"))
            cad_lines.append(
                f"| `{s['file']}` | `{bx:.2f} × {by:.2f} × {bz:.2f}` | `{s['vol_cm3']:.2f}` | `{s['triangles']}` | `{s['step_sync']}` | `{doc_flag}` |"
            )

    if steps:
        if cad_lines:
            cad_lines.append("")
        cad_lines.extend(
            [
                "### STEP Outer Envelope & Closed Circular Surface Histogram",
                "",
                "| STEP File | Export Date | Envelope `X × Y × Z (mm)` | Closed Circular Surfaces `Ø (mm)` × Count |",
                "| :--- | :---: | :---: | :--- |",
            ]
        )
        for st in steps:
            bx, by, bz = st["bbox_mm"]  # type: ignore
            bores = st["top_bores"]  # type: ignore
            if bores:
                bore_strs = []
                for d, cnt, label in bores:
                    tag = f" ({label})" if label else ""
                    bore_strs.append(f"`Ø{d:.2f}mm`×{cnt}{tag}")
                bore_col = ", ".join(bore_strs)
            else:
                bore_col = "_No closed cylindrical surfaces in 1.5–65mm range_"
            cad_lines.append(
                f"| `{st['file']}` | `{st['export_date']}` | `{bx:.2f} × {by:.2f} × {bz:.2f}` | {bore_col} |"
            )
    if not cad_lines:
        cad_lines.append("| `_none_` | `0 × 0 × 0` | `0.00` | `_No CAD files detected_` |")

    cad_lines.extend(
        [
            "",
            "> [!IMPORTANT]",
            "> **`[CAD STOP GATE — ONE-PASS TELEMETRY COMPLETE]`**: Base outer bounding envelopes (`X × Y × Z mm`), mesh volumes (`cm³`), and closed circular diameters (`Ø mm`) are complete. Raw CAD geometry does NOT define fastener counts, hole functions (screw vs. dowel vs. vent vs. fillet), or part-to-part mating intent. Do NOT run follow-up Python/grep/sed loops on `.step` or `.stl` files; bind assembly claims strictly to `BOM.md` / `Assembly_Guide.md` or tag `[TBD: Confirm design intent with engineer]`.",
        ]
    )

    cfg_lines: List[str] = []
    if cfgs:
        cfg_lines.extend(
            [
                "| Config File | MCU Pins | Fan Definitions | G-Code Macros | Scalar Parameters |",
                "| :--- | :--- | :--- | :--- | :--- |",
            ]
        )
        for c in cfgs:
            pins_s = ", ".join(f"`{p}`" for p in c["pins"]) or "_None_"  # type: ignore
            fans_s = ", ".join(f"`{f}`" for f in c["fans"]) or "_None_"  # type: ignore
            macs_s = ", ".join(f"`{m}`" for m in c["macros"]) or "_None_"  # type: ignore
            scals_s = ", ".join(f"`{s}`" for s in c.get("scalars", [])[:24]) or "_None_"  # type: ignore
            cfg_lines.append(
                f"| `{c['file']}` | {pins_s} | {fans_s} | {macs_s} | {scals_s} |"
            )
    else:
        cfg_lines.append("| `_none_` | `_None_` | `_None_` | `_None_` |")

    if (
        existing_text
        and "<!-- AUTO-HARDWARE-CAD:START -->" in existing_text
        and "<!-- AUTO-HARDWARE-CFG:START -->" in existing_text
        and "*(Rich STEP/STL B-Rep & Mass Telemetry preserved in Sections 2 & 3 above)*"
        not in existing_text
    ):
        updated = _upsert_frontmatter_keys(
            existing_text,
            {
                "telemetry_domain": telemetry_domain_val,
                "last_cad_sync": now_date,
                "last_synced": now_date,
                "latest_disk_mtime": str(scan["latest_iso"]),
                "inventory_sha256": str(scan["inventory_sha256"]),
                "step_count": str(len(steps)),
                "stl_count": str(len(stls)),
                "firmware_count": str(len(cfgs)),
                "parity_status": parity_status,
            },
        )
        updated = _replace_html_marker_block(updated, "AUTO-HARDWARE-CAD", "\n".join(cad_lines))
        updated = _replace_html_marker_block(updated, "AUTO-HARDWARE-CFG", "\n".join(cfg_lines))
        return updated

    preserved_bom_lines = [
        "## 4. Verified Fasteners, Inserts & BOM Schedule",
        "- Populate verified hardware counts from authoritative assembly sources (`verify_claims.py` whitelist).",
        "",
    ]
    if existing_text and "## 4. Verified Fasteners, Inserts & BOM Schedule" in existing_text:
        bom_tail = existing_text.split("## 4. Verified Fasteners, Inserts & BOM Schedule", 1)[1]
        preserved_bom_lines = [
            "## 4. Verified Fasteners, Inserts & BOM Schedule" + bom_tail.rstrip(),
            "",
        ]

    nav_line = (
        f"Linked Parent Note: [`{parent_note_stem}`]({parent_note_stem}.md) | "
        "Hub: [`README.md`](../../README.md)"
    )

    lines = [
        "---",
        f'project: "{project_name}"',
        f'parent_note: "{parent_note_stem}"',
        f'entity: "{entity_val}"',
        f'compartment: "{compartment_val}"',
        f'telemetry_domain: "{telemetry_domain_val}"',
        f'mode: "{mode_val}"',
        f'local_path: "{rel_or_abs_repo}"',
        f'last_cad_sync: "{now_date}"',
        f'last_synced: "{now_date}"',
        f'latest_disk_mtime: "{scan["latest_iso"]}"',
        f'inventory_sha256: "{scan["inventory_sha256"]}"',
        f"step_count: {len(steps)}",
        f"stl_count: {len(stls)}",
        f"firmware_count: {len(cfgs)}",
        f'parity_status: "{parity_status}"',
        "---",
        "",
        f"# 📐 Hardware & CAD Telemetry Manifest: {project_name}",
        "",
        nav_line,
        "",
        "> [!NOTE]",
        "> **Auto-Generated Deterministic Telemetry**: This manifest is maintained by `inspect_hardware_ecosystem.py` and `sync_memory.py --sync-hardware` for zero-token subagent lookups. Compare `latest_disk_mtime` against disk before relying on cached geometry after CAD exports.",
        "",
        "## 1. Summary & Parity Overview",
        f"- **Repository Path:** `{rel_or_abs_repo}`",
        f"- **CAD Inventory:** `{len(steps)}` STEP files | `{len(stls)}` STL meshes | `{len(cfgs)}` Firmware configs",
        f"- **STEP ↔ STL Dimensional Parity:** `{parity_status}` (`{drift_count}` bounding-box drifts > `0.20mm`)",
    ]

    if stls:
        total_vol = sum(float(s["vol_cm3"]) for s in stls)
        lines.append(
            f"- **Total Closed-Mesh Geometric Volume:** `{total_vol:.2f} cm³`"
        )

    if step_only:
        lines.append(
            "- **STEP-Only Parts (COTS Reference or Unexported STLs):** "
            + ", ".join(f"`{f}`" for f in step_only)
        )

    lines.extend(["", "## 2. CAD & Mesh Envelope Telemetry", "", "<!-- AUTO-HARDWARE-CAD:START -->"])
    lines.extend(cad_lines)
    lines.append("<!-- AUTO-HARDWARE-CAD:END -->")

    lines.extend(["", "## 3. Firmware & Pinout Telemetry", "", "<!-- AUTO-HARDWARE-CFG:START -->"])
    lines.extend(cfg_lines)
    lines.append("<!-- AUTO-HARDWARE-CFG:END -->")

    lines.append("")
    lines.extend(preserved_bom_lines)
    return "\n".join(lines)


def resolve_projects(
    vault: str, target_project: Optional[str]
) -> List[Tuple[str, str, str]]:
    """Return list of (project_name, note_stem, local_path) from Obsidian Projects/<Project>/<Project>.md (or Projects/*.md)."""
    projects_dir = os.path.join(vault, "Projects")
    results: List[Tuple[str, str, str]] = []
    candidate_dossiers: List[Tuple[str, str]] = []
    if os.path.isdir(projects_dir):
        for entry in sorted(os.listdir(projects_dir)):
            entry_path = os.path.join(projects_dir, entry)
            if os.path.isdir(entry_path) and not entry.startswith("."):
                hub_md = os.path.join(entry_path, f"{entry}.md")
                if os.path.isfile(hub_md):
                    candidate_dossiers.append((entry, hub_md))
            elif entry.endswith(".md") and not entry.endswith("_Hardware.md"):
                note_stem = os.path.splitext(entry)[0]
                candidate_dossiers.append((note_stem, entry_path))

    for note_stem, full in candidate_dossiers:
        with open(full, "r", encoding="utf-8") as f:
            meta = parse_frontmatter(f.read())
        proj = meta.get("project", note_stem)
        local_path = meta.get("local_path", "")
        aliases = [
            a.strip().lower()
            for a in meta.get("aliases", "").strip("[]").split(",")
            if a.strip()
        ]
        if not local_path:
            continue
        if not os.path.isabs(local_path):
            cand_vault_rel = os.path.abspath(os.path.join(vault, local_path))
            cand_note_rel = os.path.abspath(os.path.join(os.path.dirname(full), local_path))
            if os.path.isdir(cand_vault_rel):
                local_path = cand_vault_rel
            elif os.path.isdir(cand_note_rel):
                local_path = cand_note_rel
        if not os.path.isdir(local_path):
            continue

        if target_project:
            q = target_project.strip().lower()
            if (
                q != proj.lower()
                and q != note_stem.lower()
                and q not in aliases
                and os.path.abspath(target_project) != os.path.abspath(local_path)
            ):
                continue

        results.append((proj, note_stem, local_path))

    if not results and target_project:
        cand_dirs = [
            os.path.abspath(target_project),
            os.path.join(os.getcwd(), target_project),
            os.path.join(str(_HOM_ROOT.parent), target_project),
        ]
        for cd in cand_dirs:
            if os.path.isdir(cd):
                r_name = os.path.basename(os.path.abspath(cd))
                results.append((r_name, r_name, os.path.abspath(cd)))
                break
    elif not results and not target_project and not os.path.isdir(projects_dir):
        cwd_abs = os.path.abspath(os.getcwd())
        r_name = os.path.basename(cwd_abs) or "Standalone_Repo"
        results.append((r_name, r_name, cwd_abs))

    return results


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Inspect STEP/STL outer CAD envelopes, Klipper firmware, and sync Project Memory Hardware Manifests."
    )
    parser.add_argument(
        "--vault",
        "--memory-root",
        dest="vault",
        default=DEFAULT_VAULT,
        help=f"Path to project memory root or Obsidian vault (default: {DEFAULT_VAULT})",
    )
    parser.add_argument(
        "--project",
        dest="project",
        default=None,
        help="Target project name, alias, or repository path (omit with --all to scan all hardware repos)",
    )
    parser.add_argument(
        "--repo",
        dest="repo",
        default=None,
        help="Direct path to a hardware repository (can be combined with --project and --memory-root)",
    )
    parser.add_argument(
        "--json-out",
        dest="json_out",
        default=None,
        help="Optional path to write full JSON telemetry output",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Scan all registered projects in the memory root that contain CAD or firmware files",
    )
    parser.add_argument(
        "--check-cache",
        action="store_true",
        help="Fast mtime check comparing living disk files against cached Hardware Manifests",
    )
    parser.add_argument(
        "--sync-manifest",
        action="store_true",
        help="Write/update Projects/<Project>/<Project>_Hardware.md in the memory root",
    )
    parser.add_argument(
        "--force-rescan",
        action="store_true",
        help="Force full STEP/STL geometric re-parse even when inventory_sha256 cache is valid",
    )
    args = parser.parse_args()
    if args.vault == DEFAULT_VAULT and not os.path.isdir(os.path.join(args.vault, "Projects")):
        cand_mem = os.path.join(str(_HOM_ROOT.parent), "memory")
        if os.path.isdir(os.path.join(cand_mem, "Projects")):
            if not args.repo:
                args.vault = cand_mem
            else:
                abs_r = os.path.abspath(args.repo)
                matched = [
                    t for t in resolve_projects(cand_mem, args.project or abs_r)
                    if os.path.abspath(t[2]) == abs_r
                ]
                if matched:
                    args.vault = cand_mem

    if args.repo and os.path.isdir(os.path.abspath(args.repo)):
        abs_repo = os.path.abspath(args.repo)
        matched_proj = [
            t for t in resolve_projects(args.vault, args.project or abs_repo)
            if os.path.abspath(t[2]) == abs_repo
        ] if os.path.isdir(os.path.join(args.vault, "Projects")) else []
        if matched_proj:
            targets = matched_proj
        else:
            p_name = args.project.strip() if args.project else (os.path.basename(abs_repo) or "Standalone_Repo")
            targets = [(p_name, p_name, abs_repo)]
    else:
        target_query = args.project or args.repo
        if not target_query and not args.all:
            args.all = True
        targets = resolve_projects(args.vault, target_query)
    if not targets:
        print(f"[ERROR] No matching project found for: {args.project or args.repo}")
        return 1

    any_stale = False
    processed = 0
    json_records: List[Dict[str, object]] = []

    for proj, note_stem, local_path in targets:
        fast_scan = scan_repo_hardware(local_path, mtime_only=True)
        has_hw = bool(fast_scan["steps"] or fast_scan["stls"] or fast_scan["cfgs"])
        manifest_name = f"{note_stem}_Hardware.md"
        proj_subdir = os.path.join(args.vault, "Projects", note_stem)
        hub_dossier_path = os.path.join(proj_subdir, f"{note_stem}.md")
        legacy_manifests_dir = os.path.join(args.vault, "Hardware_Manifests")
        if os.path.isdir(proj_subdir):
            manifest_path = os.path.join(proj_subdir, manifest_name)
        elif os.path.isdir(legacy_manifests_dir):
            manifest_path = os.path.join(legacy_manifests_dir, manifest_name)
        else:
            if args.sync_manifest:
                os.makedirs(proj_subdir, exist_ok=True)
            manifest_path = os.path.join(proj_subdir, manifest_name)
        cached_mtime_str = "none"
        cached_inv_sha = ""
        m_meta: Dict[str, str] = {}
        existing_hw_text: Optional[str] = None
        if os.path.isfile(hub_dossier_path):
            with open(hub_dossier_path, "r", encoding="utf-8") as f:
                m_meta.update(parse_frontmatter(f.read()))
        if os.path.isfile(manifest_path):
            with open(manifest_path, "r", encoding="utf-8") as f:
                existing_hw_text = f.read()
                hw_meta = parse_frontmatter(existing_hw_text)
                m_meta.update(hw_meta)
                cached_mtime_str = hw_meta.get("latest_disk_mtime", "none")
                cached_inv_sha = hw_meta.get("inventory_sha256", "")
        mem_cfg_path = os.path.join(args.vault, ".homunculus_memory.json")
        if os.path.isfile(mem_cfg_path):
            try:
                with open(mem_cfg_path, "r", encoding="utf-8") as f:
                    mem_cfg = json.load(f)
                if isinstance(mem_cfg, dict) and mem_cfg.get("mode"):
                    m_meta["mode"] = str(mem_cfg["mode"])
            except Exception:
                pass
        elif os.path.isdir(os.path.join(args.vault, ".obsidian")):
            m_meta["mode"] = "obsidian"

        had_cached_hw = any(
            int(m_meta.get(k, "0") or 0) > 0
            for k in ("step_count", "stl_count", "firmware_count")
        )
        if not has_hw and not had_cached_hw:
            if (args.project or args.repo) and not args.all:
                print(
                    f"[NO_CAD_OR_CFG] {proj:<25} | STEPs: 0  | STLs: 0  | CFGs: 0 | "
                    "Docs/Software repo (no CAD/CFG files on disk)"
                )
            continue

        processed += 1

        is_stale = (
            not os.path.isfile(manifest_path)
            or cached_mtime_str != fast_scan["latest_iso"]
            or str(m_meta.get("step_count", "")) != str(len(fast_scan["steps"]))
            or str(m_meta.get("stl_count", "")) != str(len(fast_scan["stls"]))
            or str(m_meta.get("firmware_count", "")) != str(len(fast_scan["cfgs"]))
            or cached_inv_sha != fast_scan["inventory_sha256"]
        )
        if is_stale:
            any_stale = True

        status_tag = "CACHE_STALE" if is_stale else "CACHE_VALID"
        print(
            f"[{status_tag}] {proj:<26} | STEPs: {len(fast_scan['steps']):<2} | STLs: {len(fast_scan['stls']):<2} | "
            f"CFGs: {len(fast_scan['cfgs']):<1} | CAD Disk: {fast_scan['latest_iso']} | Vault: {cached_mtime_str}"
        )
        if os.path.exists(os.path.join(local_path, ".git")) and not args.check_cache:
            try:
                proc_st = subprocess.run(
                    ["git", "-C", local_path, "status", "--short"],
                    capture_output=True,
                    text=True,
                    timeout=2.0,
                    check=False,
                )
                proc_lg = subprocess.run(
                    ["git", "-C", local_path, "log", "-n", "3", "--oneline"],
                    capture_output=True,
                    text=True,
                    timeout=2.0,
                    check=False,
                )
                wt_state = "CLEAN" if (proc_st.returncode == 0 and not proc_st.stdout.strip()) else "DIRTY"
                commits_str = " ; ".join(ln.strip() for ln in proc_lg.stdout.splitlines() if ln.strip()) or "none"
                print(f"[GIT_PROVENANCE] Worktree: {wt_state} | Recent Commits: {commits_str}")
            except Exception:
                pass

        full_scan: Optional[Dict[str, object]] = None
        if args.sync_manifest:
            full_scan = scan_repo_hardware(local_path, mtime_only=False)
            md_content = render_manifest_markdown(
                proj, note_stem, full_scan, existing_meta=m_meta, existing_text=existing_hw_text
            )
            try:
                target_mode = os.stat(manifest_path).st_mode & 0o777
            except OSError:
                target_mode = 0o644
            fd, tmp_p = tempfile.mkstemp(
                prefix=f".{manifest_name}.",
                suffix=".tmp",
                dir=os.path.dirname(manifest_path),
            )
            try:
                with os.fdopen(fd, "w", encoding="utf-8") as f:
                    f.write(md_content)
                os.chmod(tmp_p, target_mode)
                os.replace(tmp_p, manifest_path)
            except Exception:
                try:
                    os.unlink(tmp_p)
                except OSError:
                    pass
                raise
            print(f"  -> Synced Hardware Manifest: {manifest_path} [CAD STOP GATE — ONE-PASS TELEMETRY COMPLETE]")
        elif not args.check_cache:
            if not is_stale and os.path.isfile(manifest_path) and not args.force_rescan:
                with open(manifest_path, "r", encoding="utf-8") as f:
                    raw_out = f.read()
            else:
                full_scan = scan_repo_hardware(local_path, mtime_only=False)
                raw_out = render_manifest_markdown(
                    proj, note_stem, full_scan, existing_meta=m_meta, existing_text=existing_hw_text
                )
            if raw_out.startswith("---\n"):
                parts = raw_out.split("\n---\n", 1)
                if len(parts) == 2:
                    raw_out = parts[1].lstrip("\n")
            raw_out = re.sub(
                r"^> \[!NOTE\]\n> \*\*Auto-Generated Deterministic Telemetry\*\*:[^\n]*\n\n?",
                "",
                raw_out,
                flags=re.MULTILINE,
            )
            print(raw_out, end="" if raw_out.endswith("\n") else "\n")
            print(
                f"[COVERAGE_RECEIPT] Complete CAD/CFG/Git inventory printed above (Manifest: {manifest_path}) — "
                "do not re-run find/ls/git-status on CAD or firmware directories."
            )

        if args.json_out:
            if full_scan is None:
                full_scan = scan_repo_hardware(local_path, mtime_only=False)
            safe_repo_path = m_meta.get("local_path") or os.path.basename(os.path.abspath(local_path))
            json_records.append(
                {
                    "project": proj,
                    "note_stem": note_stem,
                    **full_scan,
                    "repo_path": safe_repo_path,
                }
            )

    if args.json_out:
        out_p = os.path.abspath(os.path.expanduser(args.json_out))
        os.makedirs(os.path.dirname(out_p) or ".", exist_ok=True)
        payload = json_records[0] if len(json_records) == 1 else {"projects": json_records}
        with open(out_p, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2)
        print(
            f"[JSON_OUT] {out_p} | Schema: steps[i].{{file,filename,bbox_mm,top_bores,cylindrical_features[{{diameter_mm,count}}]}}, stls[i].{{file,filename,bbox_mm,vol_cm3,volume_cm3,triangles,step_sync,doc_ref}}, cfgs[i].{{file,filename,pins,fans,macros}}"
        )

    if args.check_cache and any_stale:
        return 2
    if processed == 0:
        print("[INFO] No hardware/CAD files found in selected target(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
