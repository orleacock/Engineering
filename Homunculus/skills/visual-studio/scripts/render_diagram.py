#!/usr/bin/env python3
"""
Homunculus & Co-Engineering Technical Diagram Studio (render_diagram.py)
---------------------------------------------------------------------------
Dynamically loads semantic color palettes and diagram blueprints from
templates/diagrams/ (or <memory_root>/Templates/) and renders
publication-grade vector (.svg) and 300 DPI raster (.png) diagrams across
5 extensible archetypes:
  1. layered_architecture      (Horizontal swimlanes/bands + side-by-side cards)
  2. column_dataflow           (Multi-column routed data-flow with vertical channels)
  3. hardware_pinout_pneumatic (MCU pinout, power, & pneumatic PTFE block routing)
  4. comparison_matrix         (Side-by-side engineering trade-off & benchmark card)
  5. spatial_topology          (2D multi-zone container map + Manhattan bus routing)

Supports optional --github-card post-processing via format_image.py.
"""

import argparse
import html
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

_HOM_ROOT = Path(__file__).resolve().parents[3]
if str(_HOM_ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(_HOM_ROOT / "scripts"))
import homunculus_paths  # noqa: E402

VAULT_TEMPLATES_DIR = _HOM_ROOT / "templates" / "diagrams"
PALETTES_DIR = VAULT_TEMPLATES_DIR / "Color_Palettes"
BLUEPRINTS_DIR = VAULT_TEMPLATES_DIR / "Diagram_Blueprints"
FORMAT_IMAGE_SCRIPT = (
    _HOM_ROOT / "skills" / "doc-and-card-studio" / "scripts" / "format_image.py"
)


def _resolve_active_memory_root(explicit_memory_root: Optional[str] = None) -> Optional[Path]:
    """Resolve optional active <memory_root> so <memory_root>/Templates/ palettes & blueprints are discovered."""
    if explicit_memory_root:
        cand = Path(explicit_memory_root).expanduser().resolve()
        return cand if cand.is_dir() else None
    env_mem = os.environ.get("HOMUNCULUS_MEMORY_ROOT", "").strip()
    if env_mem:
        cand = Path(env_mem).expanduser().resolve()
        if cand.is_dir():
            return cand
    try:
        cfg = homunculus_paths.resolve_workspace_config(homunculus_root=_HOM_ROOT)
        cand = Path(cfg["memory_root"]).resolve()
        if cand.is_dir():
            return cand
    except Exception:
        pass
    # Also check sibling ../memory relative to _HOM_ROOT if running inside a workstation layout
    sibling_mem = (_HOM_ROOT.parent / "memory").resolve()
    if sibling_mem.is_dir():
        return sibling_mem
    return None

PALETTE_BLOCK_RE = re.compile(
    r"```json\s+palette_tokens\s*\n(.*?)\n```", re.DOTALL
)
SPEC_BLOCK_RE = re.compile(
    r"```json\s+diagram_spec\s*\n(.*?)\n```", re.DOTALL
)
FRONTMATTER_RE = re.compile(r"\A---\s*\n(.*?)\n---\s*(?:\n|$)", re.DOTALL)

DEFAULT_DARK_TOKENS: Dict[str, Any] = {
    "mode": "dark",
    "font_stack": "'Inter', 'Segoe UI', Ubuntu, Arial, sans-serif",
    "mono_stack": "'JetBrains Mono', 'Fira Code', Consolas, monospace",
    "canvas_bg": "#0F141C",
    "container_bg": "#151C28",
    "container_bg_alt": "#18202E",
    "card_bg_primary": "#1D2636",
    "card_bg_secondary": "#232E42",
    "card_bg_recessed": "#111722",
    "banner_grad_start": "#111722",
    "banner_grad_mid": "#1D2636",
    "banner_grad_end": "#0284C7",
    "banner_text": "#F8FAFC",
    "banner_subtext": "#38BDF8",
    "primary_accent": "#38BDF8",
    "secondary_accent": "#A78BFA",
    "tertiary_accent": "#94A3B8",
    "structural_border": "#33435E",
    "text_bright": "#F8FAFC",
    "text_primary": "#E2E8F0",
    "text_muted": "#94A3B8",
    "text_on_accent": "#F8FAFC",
    "status_pass": "#34D399",
    "status_pass_bg": "#192B22",
    "status_warn": "#FBBF24",
    "status_warn_bg": "#2B2414",
    "status_alert": "#F87171",
    "status_alert_bg": "#2D1622",
    "pill_bg": "#111722",
    "pill_border": "#38BDF8",
    "pill_text": "#E2E8F0",
}

DEFAULT_LIGHT_TOKENS: Dict[str, Any] = {
    "mode": "light",
    "font_stack": "'Inter', 'Segoe UI', Ubuntu, Arial, sans-serif",
    "mono_stack": "'JetBrains Mono', 'Fira Code', Consolas, monospace",
    "canvas_bg": "#F8FAFC",
    "container_bg": "#F1F5F9",
    "container_bg_alt": "#E2E8F0",
    "card_bg_primary": "#FFFFFF",
    "card_bg_secondary": "#E2E8F0",
    "card_bg_recessed": "#F8FAFC",
    "banner_grad_start": "#0F172A",
    "banner_grad_mid": "#1E293B",
    "banner_grad_end": "#0284C7",
    "banner_text": "#FFFFFF",
    "banner_subtext": "#38BDF8",
    "primary_accent": "#0284C7",
    "secondary_accent": "#7C3AED",
    "tertiary_accent": "#475569",
    "structural_border": "#CBD5E1",
    "text_bright": "#0F172A",
    "text_primary": "#1E293B",
    "text_muted": "#64748B",
    "text_on_accent": "#FFFFFF",
    "status_pass": "#059669",
    "status_pass_bg": "#EAFAF1",
    "status_warn": "#D97706",
    "status_warn_bg": "#FEF9E7",
    "status_alert": "#DC2626",
    "status_alert_bg": "#FDEDEC",
    "pill_bg": "#FFFFFF",
    "pill_border": "#0284C7",
    "pill_text": "#0F172A",
}


def esc(text: Any) -> str:
    return html.escape(str(text), quote=True)


def extract_frontmatter_aliases(md_text: str) -> List[str]:
    aliases: List[str] = []
    m = FRONTMATTER_RE.match(md_text)
    if not m:
        return aliases
    for line in m.group(1).splitlines():
        if ":" not in line:
            continue
        k, v = line.split(":", 1)
        if k.strip().lower() in ("aliases", "alias", "palette_id", "blueprint_id"):
            val = v.strip()
            if val.startswith("[") and val.endswith("]"):
                for item in val[1:-1].split(","):
                    clean = item.strip().strip("\"'")
                    if clean:
                        aliases.append(clean)
            elif val:
                aliases.append(val.strip("\"'"))
    return aliases


def apply_palette_defaults(raw_tokens: Dict[str, Any]) -> Dict[str, Any]:
    mode = str(raw_tokens.get("mode", "dark")).lower()
    if "light" in str(raw_tokens.get("palette_id", "")).lower():
        mode = "light"
    base = dict(DEFAULT_LIGHT_TOKENS if mode == "light" else DEFAULT_DARK_TOKENS)
    base.update(raw_tokens)
    for src_k, dst_k in (
        ("pass_accent", "status_pass"),
        ("warn_accent", "status_warn"),
        ("alert_accent", "status_alert"),
    ):
        if src_k in raw_tokens and dst_k not in raw_tokens:
            base[dst_k] = raw_tokens[src_k]
    return base


def normalize_key(k: str) -> str:
    return k.strip().lower().replace("-", "_")


def discover_palettes(
    palettes_dir: Path = PALETTES_DIR,
    memory_root: Optional[Path] = None,
) -> Dict[str, Dict[str, Any]]:
    default_dark = dict(DEFAULT_DARK_TOKENS)
    default_dark["palette_id"] = "default_dark"
    default_dark["_source_file"] = "<builtin:DEFAULT_DARK_TOKENS>"
    default_light = dict(DEFAULT_LIGHT_TOKENS)
    default_light["palette_id"] = "default_light"
    default_light["_source_file"] = "<builtin:DEFAULT_LIGHT_TOKENS>"
    palettes: Dict[str, Dict[str, Any]] = {
        "default_dark": default_dark,
        "dark": default_dark,
        "default_light": default_light,
        "light": default_light,
    }
    json_palettes_file = palettes_dir.parent / "Diagram_Palettes.json"
    if json_palettes_file.is_file():
        try:
            raw_json = json.loads(json_palettes_file.read_text(encoding="utf-8"))
            for p_key, p_tokens in (raw_json.get("palettes") or {}).items():
                if isinstance(p_tokens, dict):
                    merged = apply_palette_defaults(p_tokens)
                    pid = normalize_key(merged.get("palette_id") or p_key)
                    merged["palette_id"] = pid
                    merged["_source_file"] = str(json_palettes_file)
                    palettes[pid] = merged
                    palettes[normalize_key(p_key)] = merged
                    if pid == "default_dark":
                        palettes["dark"] = merged
                    elif pid == "default_light":
                        palettes["light"] = merged
                    elif pid == "gruvbox_dark":
                        palettes["gruvbox"] = merged
                        palettes["gruvbox_local"] = merged
        except json.JSONDecodeError as exc:
            print(f"[WARNING] Invalid JSON in {json_palettes_file}: {exc}", file=sys.stderr)

    search_dirs: List[Path] = [palettes_dir]
    active_mem = (
        _resolve_active_memory_root()
        if (memory_root is None and palettes_dir == PALETTES_DIR)
        else memory_root
    )
    if active_mem is not None and active_mem.is_dir():
        for cand_dir in (
            active_mem / "Templates" / "Color_Palettes",
            active_mem / "Templates",
        ):
            if cand_dir.is_dir() and cand_dir not in search_dirs:
                search_dirs.append(cand_dir)

    for sdir in search_dirs:
        if not sdir.exists():
            continue
        for md_path in sorted(sdir.glob("*.md")):
            content = md_path.read_text(encoding="utf-8")
            match = PALETTE_BLOCK_RE.search(content)
            if match:
                try:
                    raw_data = json.loads(match.group(1))
                    data = apply_palette_defaults(raw_data)
                    pid = normalize_key(data.get("palette_id") or md_path.stem)
                    data["palette_id"] = pid
                    data["_source_file"] = str(md_path)
                    palettes[pid] = data
                    palettes[normalize_key(md_path.stem)] = data
                    for al in extract_frontmatter_aliases(content):
                        palettes[normalize_key(al)] = data
                except json.JSONDecodeError as exc:
                    print(f"[WARNING] Invalid JSON in {md_path}: {exc}", file=sys.stderr)
    return palettes


def discover_blueprints(
    blueprints_dir: Path = BLUEPRINTS_DIR,
    memory_root: Optional[Path] = None,
) -> Dict[str, Dict[str, Any]]:
    blueprints: Dict[str, Dict[str, Any]] = {}
    search_dirs: List[Path] = [blueprints_dir]
    active_mem = (
        _resolve_active_memory_root()
        if (memory_root is None and blueprints_dir == BLUEPRINTS_DIR)
        else memory_root
    )
    if active_mem is not None and active_mem.is_dir():
        for cand_dir in (
            active_mem / "Templates" / "Diagram_Blueprints",
            active_mem / "Templates",
        ):
            if cand_dir.is_dir() and cand_dir not in search_dirs:
                search_dirs.append(cand_dir)

    for sdir in search_dirs:
        if not sdir.exists():
            continue
        for md_path in sorted(sdir.glob("*.md")):
            content = md_path.read_text(encoding="utf-8")
            match = SPEC_BLOCK_RE.search(content)
            if match:
                try:
                    data = json.loads(match.group(1))
                    arch = normalize_key(data.get("archetype") or md_path.stem)
                    data["_source_file"] = str(md_path)
                    blueprints[arch] = data
                    blueprints[normalize_key(md_path.stem)] = data
                    for al in extract_frontmatter_aliases(content):
                        blueprints[normalize_key(al)] = data
                except json.JSONDecodeError as exc:
                    print(f"[WARNING] Invalid JSON in {md_path}: {exc}", file=sys.stderr)
    return blueprints


def load_spec(spec_path: Path) -> Dict[str, Any]:
    raw = spec_path.read_text(encoding="utf-8")
    if spec_path.suffix.lower() in (".md", ".markdown"):
        match = SPEC_BLOCK_RE.search(raw)
        if not match:
            raise ValueError(
                f"No ```json diagram_spec block found inside Markdown file: {spec_path}"
            )
        return json.loads(match.group(1))
    return json.loads(raw)


def _best_header_text(bg_hex: str, dark_ink: str = "#1D2021", light_ink: str = "#FFFFFF") -> str:
    h = str(bg_hex).strip().lstrip("#")
    if len(h) == 6:
        try:
            r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
            lum = (0.299 * r + 0.587 * g + 0.114 * b) / 255.0
            return dark_ink if lum > 0.52 else light_ink
        except ValueError:
            pass
    return light_ink


def strip_inline_markup(text: str) -> str:
    return re.sub(r"\*\*(.+?)\*\*", r"\1", str(text))


def render_inline_markup(text: str, bold_fill: str = "") -> str:
    parts = re.split(r"(\*\*.+?\*\*)", str(text))
    fill_attr = f' fill="{bold_fill}"' if bold_fill else ""
    out: List[str] = []
    for part in parts:
        if part.startswith("**") and part.endswith("**") and len(part) > 4:
            out.append(f'<tspan font-weight="bold"{fill_attr}>{esc(part[2:-2])}</tspan>')
        else:
            out.append(esc(part))
    return "".join(out)


def resolve_style_colors(
    palette: Dict[str, Any], style_name: str
) -> Tuple[str, str, str, str]:
    """
    Returns (border_hex, header_fill_hex, card_fill_hex, header_text_hex)
    for a semantic style token ('primary', 'secondary', 'tertiary', 'pass', 'warn', 'alert', 'neutral').
    """
    s = (style_name or "primary").lower()
    card_bg = palette["card_bg_primary"]
    dark_ink = palette.get("card_bg_recessed", "#1D2021") if palette.get("mode", "dark") == "dark" else "#141417"

    if s == "primary":
        hdr = palette["primary_accent"]
        return hdr, hdr, card_bg, _best_header_text(hdr, dark_ink)
    if s == "secondary":
        hdr = palette["secondary_accent"]
        return hdr, hdr, card_bg, _best_header_text(hdr, dark_ink)
    if s == "tertiary":
        hdr = palette["tertiary_accent"]
        return hdr, hdr, palette["card_bg_secondary"], _best_header_text(hdr, dark_ink)
    if s == "pass":
        hdr = palette["status_pass"]
        return hdr, hdr, palette.get("status_pass_bg", card_bg), _best_header_text(hdr, dark_ink)
    if s == "warn":
        hdr = palette["status_warn"]
        return hdr, hdr, palette.get("status_warn_bg", card_bg), _best_header_text(hdr, dark_ink)
    if s == "alert":
        hdr = palette["status_alert"]
        return hdr, hdr, palette.get("status_alert_bg", card_bg), _best_header_text(hdr, dark_ink)
    return (
        palette["structural_border"],
        palette["card_bg_secondary"],
        card_bg,
        palette["text_bright"],
    )


class DiagramBuilder:
    def __init__(self, width: int, height: int, palette: Dict[str, Any]):
        self.width = width
        self.height = height
        self.p = palette
        self.warnings: List[str] = []
        self.schema_errors: List[str] = []
        self.layer_bg: List[str] = []
        self.layer_cards: List[str] = []
        self.layer_connectors: List[str] = []
        self.layer_pills: List[str] = []

    def check_fit(self, text: str, max_px: float, font_size: int, context: str) -> None:
        clean = strip_inline_markup(text)
        avg_char_px = font_size * 0.56
        est_px = len(clean) * avg_char_px
        if est_px > max_px:
            self.warnings.append(
                f"[LAYOUT WARNING] {context}: text ({len(clean)} chars, ~{int(est_px)}px) "
                f"exceeds available width ({int(max_px)}px): '{clean[:48]}...'"
            )

    def build_defs(self) -> str:
        p = self.p
        markers = {
            "primary": p["primary_accent"],
            "secondary": p["secondary_accent"],
            "tertiary": p["tertiary_accent"],
            "pass": p["status_pass"],
            "warn": p["status_warn"],
            "alert": p["status_alert"],
            "neutral": p["structural_border"],
        }
        marker_xml = []
        for name, color in markers.items():
            marker_xml.append(
                f'    <marker id="arrow-{name}" viewBox="0 0 12 12" refX="10" refY="6" '
                f'markerWidth="8" markerHeight="8" orient="auto-start-reverse">\n'
                f'      <path d="M 1 2 L 10 6 L 1 10 z" fill="{color}"/>\n'
                f"    </marker>"
            )
        return f"""  <defs>
    <linearGradient id="banner-grad" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="{p['banner_grad_start']}"/>
      <stop offset="55%" stop-color="{p['banner_grad_mid']}"/>
      <stop offset="100%" stop-color="{p['banner_grad_end']}"/>
    </linearGradient>
    <filter id="card-shadow" x="-4%" y="-4%" width="108%" height="112%">
      <feDropShadow dx="0" dy="3" stdDeviation="4" flood-color="#000000" flood-opacity="0.22"/>
    </filter>
    <filter id="pill-shadow" x="-8%" y="-8%" width="116%" height="120%">
      <feDropShadow dx="0" dy="1" stdDeviation="2" flood-color="#000000" flood-opacity="0.28"/>
    </filter>
{chr(10).join(marker_xml)}
  </defs>"""

    def add_banner(self, title: str, subtitle: str, badge: str = "") -> int:
        p = self.p
        banner_h = 84
        self.layer_bg.append(
            f'    <rect x="0" y="0" width="{self.width}" height="{self.height}" fill="{p["canvas_bg"]}"/>'
        )
        self.layer_bg.append(
            f'    <rect x="24" y="18" width="{self.width - 48}" height="{banner_h}" rx="10" '
            f'fill="url(#banner-grad)" stroke="{p["primary_accent"]}" stroke-width="1.5" filter="url(#card-shadow)"/>'
        )
        self.layer_bg.append(
            f'    <text x="48" y="54" font-family="{p["font_stack"]}" font-size="23" '
            f'font-weight="bold" fill="{p["banner_text"]}">{esc(title)}</text>'
        )
        self.layer_bg.append(
            f'    <text x="48" y="82" font-family="{p["font_stack"]}" font-size="14" '
            f'fill="{p["banner_subtext"]}">{esc(subtitle)}</text>'
        )
        if badge:
            bw = max(140, len(badge) * 9 + 34)
            bx = self.width - 48 - bw
            self.layer_bg.append(
                f'    <rect x="{bx}" y="38" width="{bw}" height="36" rx="18" '
                f'fill="{p["card_bg_recessed"]}" stroke="{p["primary_accent"]}" stroke-width="1.5"/>'
            )
            self.layer_bg.append(
                f'    <text x="{bx + bw / 2}" y="61" text-anchor="middle" '
                f'font-family="{p["mono_stack"]}" font-size="13" font-weight="bold" '
                f'fill="{p["text_bright"]}">{esc(badge)}</text>'
            )
        return 18 + banner_h + 22

    def add_footer(self, left_text: str, right_text: str) -> None:
        p = self.p
        fy = self.height - 16
        self.layer_bg.append(
            f'    <text x="32" y="{fy}" font-family="{p["font_stack"]}" font-size="12" '
            f'fill="{p["text_muted"]}">{esc(left_text)}</text>'
        )
        self.layer_bg.append(
            f'    <text x="{self.width - 32}" y="{fy}" text-anchor="end" '
            f'font-family="{p["font_stack"]}" font-size="12" '
            f'fill="{p["text_muted"]}">{esc(right_text)}</text>'
        )

    def add_pill(self, cx: float, cy: float, label: str, style: str = "primary") -> None:
        if not label:
            return
        p = self.p
        border_col, _, _, _ = resolve_style_colors(p, style)
        pw = max(84, len(label) * 7.6 + 24)
        ph = 24
        px = cx - pw / 2
        py = cy - ph / 2
        self.layer_pills.append(
            f'    <rect x="{px:.1f}" y="{py:.1f}" width="{pw:.1f}" height="{ph}" rx="12" '
            f'fill="{p["pill_bg"]}" stroke="{border_col}" stroke-width="1.5" filter="url(#pill-shadow)"/>'
        )
        self.layer_pills.append(
            f'    <text x="{cx:.1f}" y="{cy + 4.5:.1f}" text-anchor="middle" '
            f'font-family="{p["font_stack"]}" font-size="12" font-weight="bold" '
            f'fill="{p["pill_text"]}">{esc(label)}</text>'
        )

    def add_connector(
        self,
        points: List[Tuple[float, float]],
        style: str = "primary",
        label: str = "",
        dashed: bool = False,
        pill_pos: Optional[Tuple[float, float]] = None,
    ) -> None:
        p = self.p
        border_col, _, _, _ = resolve_style_colors(p, style)
        marker_key = style.lower() if style.lower() in (
            "primary", "secondary", "tertiary", "pass", "warn", "alert"
        ) else "neutral"
        pts_str = " ".join(f"{x:.1f},{y:.1f}" for x, y in points)
        dash_attr = ' stroke-dasharray="6,4"' if dashed else ""
        self.layer_connectors.append(
            f'    <polyline points="{pts_str}" fill="none" stroke="{border_col}" '
            f'stroke-width="2.4"{dash_attr} marker-end="url(#arrow-{marker_key})"/>'
        )
        if label:
            if pill_pos:
                cx, cy = pill_pos
            elif len(points) >= 4:
                cx = (points[1][0] + points[2][0]) / 2
                cy = (points[1][1] + points[2][1]) / 2
            else:
                cx = (points[0][0] + points[-1][0]) / 2
                cy = (points[0][1] + points[-1][1]) / 2
            self.add_pill(cx, cy, label, style)

    def render_card(
        self,
        x: float,
        y: float,
        w: float,
        h: float,
        title: str,
        lines: List[str],
        badge: str = "",
        style: str = "primary",
        subtitle: str = "",
    ) -> None:
        p = self.p
        border_col, hdr_fill, card_fill, hdr_text = resolve_style_colors(p, style)
        hdr_h = 44 if subtitle else 34
        self.layer_cards.append(
            f'    <rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="8" '
            f'fill="{card_fill}" stroke="{border_col}" stroke-width="1.8" filter="url(#card-shadow)"/>'
        )
        self.layer_cards.append(
            f'    <rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{hdr_h}" rx="8" fill="{hdr_fill}"/>'
        )
        self.layer_cards.append(
            f'    <rect x="{x:.1f}" y="{y + hdr_h - 8:.1f}" width="{w:.1f}" height="8" fill="{hdr_fill}"/>'
        )

        badge_reserve = (len(badge) * 7.5 + 28) if badge else 0
        self.check_fit(title, w - 28 - badge_reserve, 14, f"Card '{title}' header")

        self.layer_cards.append(
            f'    <text x="{x + 14:.1f}" y="{y + 22:.1f}" font-family="{p["font_stack"]}" '
            f'font-size="14" font-weight="bold" fill="{hdr_text}">{esc(title)}</text>'
        )
        if subtitle:
            self.layer_cards.append(
                f'    <text x="{x + 14:.1f}" y="{y + 38:.1f}" font-family="{p["font_stack"]}" '
                f'font-size="11.5" fill="{hdr_text}" opacity="0.92">{esc(subtitle)}</text>'
            )

        if badge:
            bw = max(58, len(badge) * 7.2 + 18)
            bx = x + w - bw - 10
            by = y + 7
            self.layer_cards.append(
                f'    <rect x="{bx:.1f}" y="{by:.1f}" width="{bw:.1f}" height="20" rx="10" '
                f'fill="{p["card_bg_recessed"]}" stroke="{border_col}" stroke-width="1"/>'
            )
            self.layer_cards.append(
                f'    <text x="{bx + bw / 2:.1f}" y="{by + 14:.1f}" text-anchor="middle" '
                f'font-family="{p["mono_stack"]}" font-size="10.5" font-weight="bold" '
                f'fill="{p["text_bright"]}">{esc(badge)}</text>'
            )

        ty = y + hdr_h + 22
        for line in lines:
            self.check_fit(line, w - 28, 12, f"Card '{title}' line")
            if ty > y + h - 8:
                self.warnings.append(
                    f"[LAYOUT WARNING] Card '{title}': vertical line overflow (y={int(ty)} > card_bottom={int(y+h)})."
                )
            markup = render_inline_markup(line, bold_fill=p["text_bright"])
            self.layer_cards.append(
                f'    <text x="{x + 14:.1f}" y="{ty:.1f}" font-family="{p["font_stack"]}" '
                f'font-size="12.5" fill="{p["text_primary"]}">{markup}</text>'
            )
            ty += 21

    def to_svg(self) -> str:
        return f"""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {self.width} {self.height}" width="{self.width}" height="{self.height}">
{self.build_defs()}
  <g id="layer-backgrounds">
{chr(10).join(self.layer_bg)}
  </g>
  <g id="layer-cards">
{chr(10).join(self.layer_cards)}
  </g>
  <g id="layer-connectors">
{chr(10).join(self.layer_connectors)}
  </g>
  <g id="layer-pills">
{chr(10).join(self.layer_pills)}
  </g>
</svg>
"""


def render_layered_architecture(spec: Dict[str, Any], palette: Dict[str, Any]) -> DiagramBuilder:
    width = int(spec.get("width", 1600))
    layers = spec.get("layers", [])
    band_gap = int(spec.get("band_gap", 56))
    top_y = 124
    total_h = top_y

    layer_idx_map = {lyr.get("id", f"layer_{i}"): i for i, lyr in enumerate(layers)}
    has_side_route = any(
        conn.get("from_layer") in layer_idx_map
        and conn.get("to_layer") in layer_idx_map
        and not (
            layer_idx_map[conn["to_layer"]] - layer_idx_map[conn["from_layer"]] == 1
        )
        for conn in spec.get("connections", [])
    )

    for lyr in layers:
        cards = lyr.get("cards", [])
        min_card_h = 110
        for c in cards:
            hdr_h = 44 if c.get("subtitle") else 34
            req_c_h = hdr_h + 26 + len(c.get("lines", [])) * 21
            min_card_h = max(min_card_h, req_c_h)
        band_hdr_pad = 58 if lyr.get("badge") or lyr.get("right_note") else 54
        calc_lh = max(int(lyr.get("height", 175)), min_card_h + band_hdr_pad)
        lyr["_calc_h"] = calc_lh
        total_h += calc_lh + band_gap

    height = max(int(spec.get("height", 0)), total_h + 24)
    db = DiagramBuilder(width, height, palette)
    cur_y = db.add_banner(
        spec.get("title", "SYSTEM ARCHITECTURE"),
        spec.get("subtitle", ""),
        spec.get("badge", "ARCHITECTURE"),
    )

    layer_bounds: Dict[str, Tuple[int, float, float, float, float]] = {}
    band_x = 32
    right_gutter = 190 if has_side_route else 32
    band_w = width - band_x - right_gutter

    for idx, lyr in enumerate(layers):
        lid = lyr.get("id", f"layer_{idx}")
        lh = int(lyr["_calc_h"])
        lstyle = lyr.get("style", "primary")
        border_col, hdr_fill, _, hdr_text = resolve_style_colors(palette, lstyle)
        bg_fill = palette["container_bg"] if idx % 2 == 0 else palette["container_bg_alt"]
        hdr_bar_h = 34 if (lyr.get("badge") or lyr.get("right_note")) else 30

        db.layer_bg.append(
            f'    <rect x="{band_x}" y="{cur_y}" width="{band_w}" height="{lh}" rx="10" '
            f'fill="{bg_fill}" stroke="{border_col}" stroke-width="1.6"/>'
        )
        db.layer_bg.append(
            f'    <rect x="{band_x}" y="{cur_y}" width="{band_w}" height="{hdr_bar_h}" rx="10" fill="{hdr_fill}"/>'
        )
        db.layer_bg.append(
            f'    <rect x="{band_x}" y="{cur_y + hdr_bar_h - 10}" width="{band_w}" height="10" fill="{hdr_fill}"/>'
        )

        title_x = band_x + 18
        lbadge = str(lyr.get("badge", "")).strip()
        if lbadge:
            lbw = max(78, len(lbadge) * 7.8 + 20)
            lbx = band_x + 12
            lby = cur_y + 5
            db.layer_bg.append(
                f'    <rect x="{lbx}" y="{lby}" width="{lbw:.1f}" height="24" rx="5" '
                f'fill="{palette["card_bg_recessed"]}" stroke="{border_col}" stroke-width="1"/>'
            )
            db.layer_bg.append(
                f'    <text x="{lbx + lbw / 2:.1f}" y="{cur_y + 21}" text-anchor="middle" '
                f'font-family="{palette["mono_stack"]}" font-size="11.5" font-weight="bold" '
                f'fill="{palette["text_bright"]}">{esc(lbadge)}</text>'
            )
            title_x = lbx + lbw + 14

        title_y = cur_y + (22 if hdr_bar_h == 34 else 20)
        db.layer_bg.append(
            f'    <text x="{title_x:.1f}" y="{title_y}" font-family="{palette["font_stack"]}" '
            f'font-size="14" font-weight="bold" fill="{hdr_text}">{esc(lyr.get("title", lid))}</text>'
        )

        rnote = str(lyr.get("right_note", "")).strip()
        if rnote:
            db.layer_bg.append(
                f'    <text x="{band_x + band_w - 16}" y="{title_y}" text-anchor="end" '
                f'font-family="{palette["font_stack"]}" font-size="12" font-style="italic" '
                f'fill="{hdr_text}" opacity="0.92">{esc(rnote)}</text>'
            )

        cards = lyr.get("cards", [])
        if cards:
            total_weight = sum(float(c.get("weight", 1.0)) for c in cards)
            inner_pad = 16
            card_gap = 16
            avail_w = band_w - 2 * inner_pad - card_gap * (len(cards) - 1)
            cx = band_x + inner_pad
            cy = cur_y + hdr_bar_h + 12
            ch = lh - (hdr_bar_h + 24)
            for c in cards:
                cw = avail_w * (float(c.get("weight", 1.0)) / total_weight)
                db.render_card(
                    cx,
                    cy,
                    cw,
                    ch,
                    c.get("title", ""),
                    c.get("lines", []),
                    badge=c.get("badge", ""),
                    style=c.get("style", lstyle),
                    subtitle=c.get("subtitle", ""),
                )
                cx += cw + card_gap

        layer_bounds[lid] = (idx, band_x, cur_y, band_w, lh)
        cur_y += lh + band_gap

    side_idx = 0
    for conn in spec.get("connections", []):
        fl = conn.get("from_layer")
        tl = conn.get("to_layer")
        if fl not in layer_bounds or tl not in layer_bounds:
            msg = f"[SCHEMA WARNING] Layer connection '{fl}' -> '{tl}' has unresolved layer ID."
            db.warnings.append(msg)
            db.schema_errors.append(msg)
            continue
        f_idx, fx, fy, fw, fh = layer_bounds[fl]
        t_idx, tx, ty, tw, th = layer_bounds[tl]
        xr = float(conn.get("x_ratio", 0.5))

        if abs(t_idx - f_idx) == 1 and t_idx > f_idx:
            x_pos = fx + fw * xr
            y1 = fy + fh
            y2 = ty - 3
            db.add_connector(
                [(x_pos, y1), (x_pos, y2)],
                style=conn.get("style", "primary"),
                label=conn.get("label", ""),
                dashed=bool(conn.get("dashed", False)),
                pill_pos=(x_pos, (y1 + y2) / 2),
            )
        else:
            # Non-adjacent or upward layer connection: route inside dedicated right perimeter channel
            side_x = fx + fw + 95 + (side_idx * 24)
            side_idx += 1
            y1 = fy + fh / 2
            y2 = ty + th / 2
            db.add_connector(
                [(fx + fw, y1), (side_x, y1), (side_x, y2), (tx + tw + 3, y2)],
                style=conn.get("style", "primary"),
                label=conn.get("label", ""),
                dashed=bool(conn.get("dashed", False)),
                pill_pos=(side_x, (y1 + y2) / 2),
            )

    db.add_footer(
        spec.get("footer_left", "Homunculus Visual Diagram Studio"),
        spec.get("footer_right", f"Palette: {palette.get('palette_name', palette.get('palette_id'))}"),
    )
    return db


def render_column_dataflow(spec: Dict[str, Any], palette: Dict[str, Any]) -> DiagramBuilder:
    width = int(spec.get("width", 1680))
    columns = spec.get("columns", [])
    top_y = 126
    node_gap = 42

    max_col_h = 0
    for col in columns:
        ch = 54
        for n in col.get("nodes", []):
            hdr_h = 44 if n.get("subtitle") else 34
            req_nh = hdr_h + 26 + len(n.get("lines", [])) * 21
            nh = max(int(n.get("height", 165)), req_nh)
            n["_calc_h"] = nh
            ch += nh + node_gap
        max_col_h = max(max_col_h, ch)

    # Check if any connector skips a column so we reserve a bottom bypass channel
    node_col_map: Dict[str, int] = {}
    for c_idx, col in enumerate(columns):
        for n in col.get("nodes", []):
            if n.get("id"):
                node_col_map[n["id"]] = c_idx
    has_skip_col = any(
        abs(node_col_map.get(c.get("to_node"), 0) - node_col_map.get(c.get("from_node"), 0)) > 1
        for c in spec.get("connectors", [])
        if c.get("from_node") in node_col_map and c.get("to_node") in node_col_map
    )
    bypass_pad = 64 if has_skip_col else 0

    height = max(int(spec.get("height", 0)), top_y + max_col_h + bypass_pad + 44)
    db = DiagramBuilder(width, height, palette)
    cur_top = db.add_banner(
        spec.get("title", "COLUMN DATA-FLOW PIPELINE"),
        spec.get("subtitle", ""),
        spec.get("badge", "DATA-FLOW"),
    )

    n_cols = max(1, len(columns))
    total_col_w = sum(int(c.get("width", 390)) for c in columns)
    margin_x = 28
    channel_gap = max(110, (width - 2 * margin_x - total_col_w) / max(1, n_cols - 1)) if n_cols > 1 else 0

    node_boxes: Dict[str, Tuple[int, float, float, float, float]] = {}
    col_x = float(margin_x)

    for c_idx, col in enumerate(columns):
        cw = float(col.get("width", 390))
        col_h = max_col_h
        db.layer_bg.append(
            f'    <rect x="{col_x:.1f}" y="{cur_top}" width="{cw:.1f}" height="{col_h}" rx="10" '
            f'fill="{palette["container_bg"]}" stroke="{palette["structural_border"]}" stroke-width="1.4"/>'
        )
        db.layer_bg.append(
            f'    <rect x="{col_x:.1f}" y="{cur_top}" width="{cw:.1f}" height="34" rx="10" '
            f'fill="{palette["card_bg_secondary"]}"/>'
        )
        db.layer_bg.append(
            f'    <text x="{col_x + cw / 2:.1f}" y="{cur_top + 22}" text-anchor="middle" '
            f'font-family="{palette["font_stack"]}" font-size="13.5" font-weight="bold" '
            f'fill="{palette["text_bright"]}">{esc(col.get("header", f"COLUMN {c_idx+1}"))}</text>'
        )

        ny = float(cur_top + 48)
        for node in col.get("nodes", []):
            nid = node.get("id")
            nh = float(node["_calc_h"])
            nx = col_x + 14
            nw = cw - 28
            db.render_card(
                nx,
                ny,
                nw,
                nh,
                node.get("title", nid),
                node.get("lines", []),
                badge=node.get("badge", ""),
                style=node.get("style", "primary"),
                subtitle=node.get("subtitle", ""),
            )
            if nid:
                node_boxes[nid] = (c_idx, nx, ny, nw, nh)
            ny += nh + node_gap

        col_x += cw + channel_gap

    skip_idx = 0
    for idx, conn in enumerate(spec.get("connectors", [])):
        fn = conn.get("from_node")
        tn = conn.get("to_node")
        if fn not in node_boxes or tn not in node_boxes:
            msg = f"[SCHEMA WARNING] Connector '{fn}' -> '{tn}' has unresolved node ID."
            db.warnings.append(msg)
            db.schema_errors.append(msg)
            continue
        c1, fx, fy, fw, fh = node_boxes[fn]
        c2, tx, ty, tw, th = node_boxes[tn]
        f_ratio = float(conn.get("from_y_ratio", 0.5))
        t_ratio = float(conn.get("to_y_ratio", 0.5))

        if c1 == c2:
            x_mid = fx + fw / 2
            if fy < ty:
                y1, y2 = fy + fh, ty - 3
            else:
                y1, y2 = fy, ty + th + 3
            db.add_connector(
                [(x_mid, y1), (x_mid, y2)],
                style=conn.get("style", "primary"),
                label=conn.get("label", ""),
                dashed=bool(conn.get("dashed", False)),
                pill_pos=(x_mid, (y1 + y2) / 2),
            )
        elif abs(c2 - c1) > 1:
            # Multi-column bypass: route via dedicated bottom bypass bus channel
            x1 = fx + fw
            y1 = fy + fh * f_ratio
            x2 = tx - 3
            y2 = ty + th * t_ratio
            ch1_x = x1 + channel_gap * 0.45
            ch2_x = x2 - channel_gap * 0.45
            bypass_y = cur_top + max_col_h + 28 + (skip_idx * 24)
            skip_idx += 1
            db.add_connector(
                [(x1, y1), (ch1_x, y1), (ch1_x, bypass_y), (ch2_x, bypass_y), (ch2_x, y2), (x2, y2)],
                style=conn.get("style", "primary"),
                label=conn.get("label", ""),
                dashed=bool(conn.get("dashed", False)),
                pill_pos=((ch1_x + ch2_x) / 2, bypass_y),
            )
        else:
            x1 = fx + fw
            y1 = fy + fh * f_ratio
            x2 = tx - 3
            y2 = ty + th * t_ratio
            offset = ((idx % 3) - 1) * 14
            mx = (x1 + x2) / 2 + offset
            t_blend = [0.5, 0.35, 0.65][idx % 3] if abs(y2 - y1) > 70 else 0.5
            py_pill = y1 * (1.0 - t_blend) + y2 * t_blend
            db.add_connector(
                [(x1, y1), (mx, y1), (mx, y2), (x2, y2)],
                style=conn.get("style", "primary"),
                label=conn.get("label", ""),
                dashed=bool(conn.get("dashed", False)),
                pill_pos=(mx, py_pill),
            )

    db.add_footer(
        spec.get("footer_left", "Homunculus Visual Diagram Studio"),
        spec.get("footer_right", f"Palette: {palette.get('palette_name', palette.get('palette_id'))}"),
    )
    return db


def render_hardware_pinout_pneumatic(
    spec: Dict[str, Any], palette: Dict[str, Any]
) -> DiagramBuilder:
    width = int(spec.get("width", 1680))
    stages = spec.get("stages", [])
    top_y = 126
    block_gap = 64

    port_stage_map: Dict[str, int] = {}
    max_stage_h = 0
    for s_idx, stg in enumerate(stages):
        sh = 54
        for blk in stg.get("blocks", []):
            n_specs = len(blk.get("specs", []))
            n_ports = max(len(blk.get("ports_in", [])), len(blk.get("ports_out", [])))
            req_bh = max(175, 76 + n_specs * 21 + n_ports * 28)
            bh = max(int(blk.get("height", 0)), req_bh)
            blk["_calc_h"] = bh
            sh += bh + block_gap
            for p in blk.get("ports_in", []) + blk.get("ports_out", []):
                if p.get("id"):
                    port_stage_map[p["id"]] = s_idx
        max_stage_h = max(max_stage_h, sh)

    has_skip_stage = any(
        abs(port_stage_map.get(l.get("to_port"), 0) - port_stage_map.get(l.get("from_port"), 0)) > 1
        for l in spec.get("links", [])
        if l.get("from_port") in port_stage_map and l.get("to_port") in port_stage_map
    )
    bypass_pad = 64 if has_skip_stage else 0

    callout_items = spec.get("callout_items", [])
    callout_h = (44 + len(callout_items) * 22) if callout_items else 0
    height = max(int(spec.get("height", 0)), top_y + max_stage_h + bypass_pad + callout_h + 56)

    db = DiagramBuilder(width, height, palette)
    cur_top = db.add_banner(
        spec.get("title", "HARDWARE PINOUT & PNEUMATIC TOPOLOGY"),
        spec.get("subtitle", ""),
        spec.get("badge", "HARDWARE SPEC"),
    )

    n_stages = max(1, len(stages))
    margin_x = 28
    channel_gap = 152 if n_stages > 1 else 0
    stage_w = (width - 2 * margin_x - channel_gap * (n_stages - 1)) / n_stages

    port_coords: Dict[str, Tuple[float, float]] = {}
    port_meta: Dict[str, Tuple[int, float, float, float, float]] = {}
    sx = float(margin_x)

    for s_idx, stg in enumerate(stages):
        db.layer_bg.append(
            f'    <rect x="{sx:.1f}" y="{cur_top}" width="{stage_w:.1f}" height="{max_stage_h}" rx="10" '
            f'fill="{palette["container_bg"]}" stroke="{palette["structural_border"]}" stroke-width="1.5"/>'
        )
        db.layer_bg.append(
            f'    <rect x="{sx:.1f}" y="{cur_top}" width="{stage_w:.1f}" height="34" rx="10" '
            f'fill="{palette["card_bg_secondary"]}"/>'
        )
        db.layer_bg.append(
            f'    <text x="{sx + stage_w / 2:.1f}" y="{cur_top + 22}" text-anchor="middle" '
            f'font-family="{palette["font_stack"]}" font-size="13.5" font-weight="bold" '
            f'fill="{palette["text_bright"]}">{esc(stg.get("header", f"STAGE {s_idx+1}"))}</text>'
        )

        by = float(cur_top + 48)
        for blk in stg.get("blocks", []):
            bh = float(blk["_calc_h"])
            bx = sx + 18
            bw = stage_w - 36
            bstyle = blk.get("style", "primary")
            db.render_card(
                bx,
                by,
                bw,
                bh,
                blk.get("title", ""),
                blk.get("specs", []),
                badge=blk.get("badge", ""),
                style=bstyle,
                subtitle=blk.get("subtitle", ""),
            )

            ports_in = blk.get("ports_in", [])
            ports_out = blk.get("ports_out", [])
            port_base_y = by + bh - max(len(ports_in), len(ports_out)) * 28 - 8

            for p_idx, pin in enumerate(ports_in):
                pid = pin.get("id")
                plabel = pin.get("label", pid)
                py = port_base_y + p_idx * 26
                pw = min(145, max(82, len(plabel) * 7.2 + 16))
                db.layer_cards.append(
                    f'    <rect x="{bx - 4:.1f}" y="{py:.1f}" width="{pw:.1f}" height="22" rx="4" '
                    f'fill="{palette["card_bg_recessed"]}" stroke="{palette["structural_border"]}" stroke-width="1.3"/>'
                )
                db.layer_cards.append(
                    f'    <text x="{bx + 6:.1f}" y="{py + 15:.1f}" font-family="{palette["mono_stack"]}" '
                    f'font-size="11" font-weight="bold" fill="{palette["text_bright"]}">{esc(plabel)}</text>'
                )
                if pid:
                    port_coords[pid] = (bx - 4, py + 11)
                    port_meta[pid] = (s_idx, bx, by, bw, bh)

            for p_idx, pout in enumerate(ports_out):
                pid = pout.get("id")
                plabel = pout.get("label", pid)
                py = port_base_y + p_idx * 26
                pw = min(155, max(86, len(plabel) * 7.2 + 16))
                px = bx + bw + 4 - pw
                db.layer_cards.append(
                    f'    <rect x="{px:.1f}" y="{py:.1f}" width="{pw:.1f}" height="22" rx="4" '
                    f'fill="{palette["card_bg_recessed"]}" stroke="{palette["primary_accent"]}" stroke-width="1.3"/>'
                )
                db.layer_cards.append(
                    f'    <text x="{px + pw - 8:.1f}" y="{py + 15:.1f}" text-anchor="end" '
                    f'font-family="{palette["mono_stack"]}" font-size="11" font-weight="bold" '
                    f'fill="{palette["text_bright"]}">{esc(plabel)}</text>'
                )
                if pid:
                    port_coords[pid] = (bx + bw + 4, py + 11)
                    port_meta[pid] = (s_idx, bx, by, bw, bh)

            by += bh + block_gap

        sx += stage_w + channel_gap

    channel_link_counts: Dict[Tuple[int, int], int] = {}
    intra_link_counts: Dict[int, int] = {}
    skip_idx = 0

    for link in spec.get("links", []):
        fp = link.get("from_port")
        tp = link.get("to_port")
        if fp not in port_coords or tp not in port_coords:
            msg = f"[SCHEMA WARNING] Hardware link '{fp}' -> '{tp}' has unresolved port ID."
            db.warnings.append(msg)
            db.schema_errors.append(msg)
            continue
        x1, y1 = port_coords[fp]
        x2, y2 = port_coords[tp]
        s1, bx1, by1, bw1, bh1 = port_meta[fp]
        s2, bx2, by2, bw2, bh2 = port_meta[tp]

        if s1 == s2:
            # Intra-stage connection: compute true inter-block gap whether downward or upward
            ic = intra_link_counts.get(s1, 0)
            intra_link_counts[s1] = ic + 1
            gap_offset = ((ic % 3) - 1) * 14 if ic > 0 else 0
            if by1 <= by2:
                mid_gap_y = ((by1 + bh1) + by2) / 2 + gap_offset
            else:
                mid_gap_y = ((by2 + bh2) + by1) / 2 + gap_offset
            r_margin = bx1 + bw1 + 14
            l_margin = bx2 - 14
            db.add_connector(
                [
                    (x1, y1),
                    (r_margin, y1),
                    (r_margin, mid_gap_y),
                    (l_margin, mid_gap_y),
                    (l_margin, y2),
                    (x2 - 2, y2),
                ],
                style=link.get("style", "primary"),
                label=link.get("label", ""),
                dashed=bool(link.get("dashed", False)),
                pill_pos=(bx1 + bw1 / 2, mid_gap_y),
            )
        elif abs(s2 - s1) > 1:
            # Multi-stage bypass: route cleanly via bottom bypass bus below intermediate stages
            ch1_x = x1 + channel_gap * 0.42
            ch2_x = x2 - channel_gap * 0.42
            bypass_y = cur_top + max_stage_h + 28 + (skip_idx * 24)
            skip_idx += 1
            db.add_connector(
                [
                    (x1, y1),
                    (ch1_x, y1),
                    (ch1_x, bypass_y),
                    (ch2_x, bypass_y),
                    (ch2_x, y2),
                    (x2 - 2, y2),
                ],
                style=link.get("style", "primary"),
                label=link.get("label", ""),
                dashed=bool(link.get("dashed", False)),
                pill_pos=((ch1_x + ch2_x) / 2, bypass_y),
            )
        else:
            ch_key = (s1, s2)
            c_idx = channel_link_counts.get(ch_key, 0)
            channel_link_counts[ch_key] = c_idx + 1
            offset = ((c_idx % 3) - 1) * 18
            mx = (x1 + x2) / 2 + offset
            t_blend = [0.34, 0.66, 0.50][c_idx % 3] if abs(y2 - y1) > 70 else 0.5
            py_pill = y1 * (1.0 - t_blend) + y2 * t_blend
            db.add_connector(
                [(x1, y1), (mx, y1), (mx, y2), (x2 - 2, y2)],
                style=link.get("style", "primary"),
                label=link.get("label", ""),
                dashed=bool(link.get("dashed", False)),
                pill_pos=(mx, py_pill),
            )

    if callout_items:
        cy = cur_top + max_stage_h + bypass_pad + 16
        cw = width - 56
        db.layer_cards.append(
            f'    <rect x="28" y="{cy}" width="{cw}" height="{callout_h}" rx="8" '
            f'fill="{palette["card_bg_recessed"]}" stroke="{palette["primary_accent"]}" stroke-width="1.6"/>'
        )
        db.layer_cards.append(
            f'    <text x="46" y="{cy + 24}" font-family="{palette["font_stack"]}" '
            f'font-size="13" font-weight="bold" fill="{palette["primary_accent"]}">'
            f'{esc(spec.get("callout_title", "ENGINEERING NOTES"))}</text>'
        )
        ty = cy + 44
        for item in callout_items:
            db.check_fit(item, cw - 36, 12, "Callout bar")
            db.layer_cards.append(
                f'    <text x="46" y="{ty}" font-family="{palette["font_stack"]}" '
                f'font-size="12.5" fill="{palette["text_primary"]}">{esc(item)}</text>'
            )
            ty += 21

    db.add_footer(
        spec.get("footer_left", "Homunculus Visual Diagram Studio"),
        spec.get("footer_right", f"Palette: {palette.get('palette_name', palette.get('palette_id'))}"),
    )
    return db


def render_comparison_matrix(spec: Dict[str, Any], palette: Dict[str, Any]) -> DiagramBuilder:
    width = int(spec.get("width", 1600))
    criteria = spec.get("criteria", [])
    options = spec.get("options", [])
    row_h = 56
    hdr_h = 68
    top_y = 126
    table_h = hdr_h + len(criteria) * row_h + 16
    takeaway_h = 98 if spec.get("takeaway_text") else 0
    height = max(int(spec.get("height", 0)), top_y + table_h + takeaway_h + 52)

    db = DiagramBuilder(width, height, palette)
    cur_top = db.add_banner(
        spec.get("title", "ENGINEERING COMPARISON MATRIX"),
        spec.get("subtitle", ""),
        spec.get("badge", "COMPARISON"),
    )

    crit_w = 270
    margin_x = 24
    col_gap = 14
    n_opts = max(1, len(options))
    opt_w = (width - 2 * margin_x - crit_w - col_gap * n_opts) / n_opts

    # Criteria column
    db.layer_cards.append(
        f'    <rect x="{margin_x}" y="{cur_top}" width="{crit_w}" height="{table_h}" rx="10" '
        f'fill="{palette["container_bg"]}" stroke="{palette["structural_border"]}" stroke-width="1.5"/>'
    )
    db.layer_cards.append(
        f'    <rect x="{margin_x}" y="{cur_top}" width="{crit_w}" height="{hdr_h}" rx="10" '
        f'fill="{palette["card_bg_secondary"]}"/>'
    )
    db.layer_cards.append(
        f'    <text x="{margin_x + 18}" y="{cur_top + 40}" font-family="{palette["font_stack"]}" '
        f'font-size="14" font-weight="bold" fill="{palette["text_bright"]}">EVALUATION CRITERION</text>'
    )

    for r_idx, crit in enumerate(criteria):
        ry = cur_top + hdr_h + r_idx * row_h
        row_bg = palette["card_bg_primary"] if r_idx % 2 == 0 else palette["container_bg_alt"]
        db.layer_cards.append(
            f'    <rect x="{margin_x + 8}" y="{ry + 4}" width="{crit_w - 16}" height="{row_h - 8}" rx="6" '
            f'fill="{row_bg}"/>'
        )
        db.layer_cards.append(
            f'    <text x="{margin_x + 18}" y="{ry + 33}" font-family="{palette["font_stack"]}" '
            f'font-size="13" font-weight="bold" fill="{palette["text_bright"]}">{esc(crit)}</text>'
        )

    # Option columns
    ox = margin_x + crit_w + col_gap
    for opt in options:
        ostyle = opt.get("style", "primary")
        border_col, hdr_fill, card_fill, hdr_text = resolve_style_colors(palette, ostyle)
        db.layer_cards.append(
            f'    <rect x="{ox:.1f}" y="{cur_top}" width="{opt_w:.1f}" height="{table_h}" rx="10" '
            f'fill="{card_fill}" stroke="{border_col}" stroke-width="2" filter="url(#card-shadow)"/>'
        )
        db.layer_cards.append(
            f'    <rect x="{ox:.1f}" y="{cur_top}" width="{opt_w:.1f}" height="{hdr_h}" rx="10" fill="{hdr_fill}"/>'
        )
        db.layer_cards.append(
            f'    <rect x="{ox:.1f}" y="{cur_top + hdr_h - 10}" width="{opt_w:.1f}" height="10" fill="{hdr_fill}"/>'
        )
        db.layer_cards.append(
            f'    <text x="{ox + 16:.1f}" y="{cur_top + 28}" font-family="{palette["font_stack"]}" '
            f'font-size="15" font-weight="bold" fill="{hdr_text}">{esc(opt.get("title", ""))}</text>'
        )
        db.layer_cards.append(
            f'    <text x="{ox + 16:.1f}" y="{cur_top + 50}" font-family="{palette["font_stack"]}" '
            f'font-size="12" fill="{hdr_text}" opacity="0.92">{esc(opt.get("subtitle", ""))}</text>'
        )

        rows = opt.get("rows", [])
        for r_idx in range(len(criteria)):
            ry = cur_top + hdr_h + r_idx * row_h
            row_data = rows[r_idx] if r_idx < len(rows) else {"value": "—", "status": "neutral"}
            val = row_data.get("value", "—")
            status = row_data.get("status", "neutral").lower()
            s_border, _, s_bg, _ = resolve_style_colors(palette, status)
            cell_bg = s_bg if status in ("pass", "warn", "alert") else palette["card_bg_recessed"]
            dot_col = s_border if status in ("pass", "warn", "alert") else palette["structural_border"]

            db.layer_cards.append(
                f'    <rect x="{ox + 10:.1f}" y="{ry + 4}" width="{opt_w - 20:.1f}" height="{row_h - 8}" rx="6" '
                f'fill="{cell_bg}" stroke="{dot_col}" stroke-width="1.2"/>'
            )
            db.layer_cards.append(
                f'    <circle cx="{ox + 24:.1f}" cy="{ry + 28}" r="5" fill="{dot_col}"/>'
            )
            db.check_fit(val, opt_w - 48, 12, f"Option '{opt.get('title')}' row {r_idx+1}")
            db.layer_cards.append(
                f'    <text x="{ox + 36:.1f}" y="{ry + 33}" font-family="{palette["font_stack"]}" '
                f'font-size="12.5" fill="{palette["text_primary"]}">{esc(val)}</text>'
            )

        ox += opt_w + col_gap

    if spec.get("takeaway_text"):
        ty = cur_top + table_h + 16
        tw = width - 2 * margin_x
        db.layer_cards.append(
            f'    <rect x="{margin_x}" y="{ty}" width="{tw}" height="{takeaway_h}" rx="8" '
            f'fill="{palette["card_bg_recessed"]}" stroke="{palette["primary_accent"]}" stroke-width="1.8"/>'
        )
        db.layer_cards.append(
            f'    <text x="{margin_x + 18}" y="{ty + 24}" font-family="{palette["font_stack"]}" '
            f'font-size="13" font-weight="bold" fill="{palette["primary_accent"]}">'
            f'{esc(spec.get("takeaway_title", "ENGINEERING TAKEAWAY"))}</text>'
        )
        t_text = str(spec.get("takeaway_text", ""))
        words = t_text.split()
        lines: List[str] = []
        cur_line = ""
        for w in words:
            if len(cur_line) + len(w) + 1 <= 145:
                cur_line = f"{cur_line} {w}".strip()
            else:
                lines.append(cur_line)
                cur_line = w
        if cur_line:
            lines.append(cur_line)
        for l_idx, line in enumerate(lines[:3]):
            db.layer_cards.append(
                f'    <text x="{margin_x + 18}" y="{ty + 46 + l_idx * 20}" font-family="{palette["font_stack"]}" '
                f'font-size="12.5" fill="{palette["text_primary"]}">{esc(line)}</text>'
            )

    db.add_footer(
        spec.get("footer_left", "Homunculus Visual Diagram Studio"),
        spec.get("footer_right", f"Palette: {palette.get('palette_name', palette.get('palette_id'))}"),
    )
    return db


def _rect_port(
    rect: Tuple[float, float, float, float], side: str, offset: float = 0.0
) -> Tuple[float, float]:
    x, y, w, h = rect
    s = (side or "bottom").lower()
    if s == "top":
        return (x + w / 2.0 + offset, y)
    if s == "bottom":
        return (x + w / 2.0 + offset, y + h)
    if s == "left":
        return (x, y + h / 2.0 + offset)
    if s == "right":
        return (x + w, y + h / 2.0 + offset)
    return (x + w / 2.0 + offset, y + h / 2.0)


def _segment_hits_rect(
    p1: Tuple[float, float],
    p2: Tuple[float, float],
    rect: Tuple[float, float, float, float],
    pad: float = 2.0,
) -> bool:
    rx, ry, rw, rh = rect
    x_min, x_max = rx + pad, rx + rw - pad
    y_min, y_max = ry + pad, ry + rh - pad
    if x_min >= x_max or y_min >= y_max:
        return False
    x1, y1 = p1
    x2, y2 = p2
    if abs(x1 - x2) < 0.5:
        x = (x1 + x2) / 2.0
        if x_min < x < x_max:
            sy1, sy2 = min(y1, y2), max(y1, y2)
            if max(sy1, y_min) < min(sy2, y_max):
                return True
    elif abs(y1 - y2) < 0.5:
        y = (y1 + y2) / 2.0
        if y_min < y < y_max:
            sx1, sx2 = min(x1, x2), max(x1, x2)
            if max(sx1, x_min) < min(sx2, x_max):
                return True
    return False


def render_spatial_topology(spec: Dict[str, Any], palette: Dict[str, Any]) -> DiagramBuilder:
    """
    Renders a spacious 2D multi-zone container topology with compact module cards,
    orthogonal Manhattan bus/edge routing, topmost label pills, and strict
    bounding-box / wire-collision verification.
    """
    width = int(spec.get("width", 2640))
    height = int(spec.get("height", 2740))
    db = DiagramBuilder(width, height, palette)
    top_y = db.add_banner(
        spec.get("title", "SYSTEM ARCHITECTURE TOPOLOGY"),
        spec.get("subtitle", ""),
        spec.get("badge", palette.get("palette_id", "").upper()),
    )

    legend = spec.get("legend", [])
    if legend:
        ly = top_y - 4
        lh = 36
        db.layer_bg.append(
            f'    <rect x="24" y="{ly}" width="{width - 48}" height="{lh}" rx="8" '
            f'fill="{palette["card_bg_recessed"]}" stroke="{palette["structural_border"]}" stroke-width="1.2"/>'
        )
        slot_w = (width - 96) / max(1, len(legend))
        for idx, item in enumerate(legend):
            lx = 48 + idx * slot_w
            bcol, _, _, _ = resolve_style_colors(palette, item.get("style", "primary"))
            dashed = bool(item.get("dashed", False))
            if dashed:
                db.layer_bg.append(
                    f'    <line x1="{lx:.1f}" y1="{ly + 18}" x2="{lx + 34:.1f}" y2="{ly + 18}" '
                    f'stroke="{bcol}" stroke-width="2.6" stroke-dasharray="6,4"/>'
                )
            else:
                db.layer_bg.append(
                    f'    <rect x="{lx:.1f}" y="{ly + 10}" width="26" height="16" rx="4" '
                    f'fill="{palette["card_bg_primary"]}" stroke="{bcol}" stroke-width="2.2"/>'
                )
            db.layer_bg.append(
                f'    <text x="{lx + (42 if dashed else 36):.1f}" y="{ly + 23}" '
                f'font-family="{palette["font_stack"]}" font-size="12.5" font-weight="bold" '
                f'fill="{palette["text_primary"]}">{esc(item.get("label", ""))}</text>'
            )

    zones = spec.get("zones", [])
    nodes = spec.get("nodes", [])
    edges = spec.get("edges", [])

    box_map: Dict[str, Tuple[float, float, float, float]] = {}
    zone_map: Dict[str, Tuple[float, float, float, float]] = {}

    # 1. Render Zone Containers on layer_bg
    for z in zones:
        zid = str(z["id"])
        zx, zy, zw, zh = float(z["x"]), float(z["y"]), float(z["w"]), float(z["h"])
        zone_map[zid] = (zx, zy, zw, zh)
        box_map[zid] = (zx, zy, zw, zh)
        zstyle = z.get("style", "primary")
        bcol, _, _, _ = resolve_style_colors(palette, zstyle)
        zfill = palette["container_bg_alt"] if z.get("alt_bg") else palette["container_bg"]
        zdash = ' stroke-dasharray="8,5"' if z.get("dashed") else ""
        db.layer_bg.append(
            f'    <rect x="{zx:.1f}" y="{zy:.1f}" width="{zw:.1f}" height="{zh:.1f}" rx="10" '
            f'fill="{zfill}" fill-opacity="0.92" stroke="{bcol}" stroke-width="2.0"{zdash} filter="url(#card-shadow)"/>'
        )
        ztitle = str(z.get("title", ""))
        zbadge = str(z.get("badge", ""))
        label_str = f"{zbadge} · {ztitle}" if zbadge else ztitle
        db.check_fit(label_str, zw - 36, 13, f"Zone '{zid}' title")
        tw = min(zw - 24, max(160.0, len(label_str) * 7.8 + 36.0))
        tx = zx + (zw - tw) / 2.0
        ty = zy + 10.0
        db.layer_bg.append(
            f'    <rect x="{tx:.1f}" y="{ty:.1f}" width="{tw:.1f}" height="28" rx="6" '
            f'fill="{palette["card_bg_recessed"]}" stroke="{bcol}" stroke-width="1.4"/>'
        )
        db.layer_bg.append(
            f'    <text x="{zx + zw / 2.0:.1f}" y="{ty + 19.0:.1f}" text-anchor="middle" '
            f'font-family="{palette["font_stack"]}" font-size="13.5" font-weight="bold" '
            f'fill="{palette["text_bright"]}">{esc(label_str)}</text>'
        )

    # 2. Render Module Nodes on layer_cards & Check Zone Containment / Overlaps
    node_rects: List[Tuple[str, Tuple[float, float, float, float]]] = []
    for n in nodes:
        nid = str(n["id"])
        nx, ny, nw, nh = float(n["x"]), float(n["y"]), float(n["w"]), float(n["h"])
        nrect = (nx, ny, nw, nh)
        box_map[nid] = nrect
        nstyle = n.get("style", "primary")
        bcol, hdr_col, cfill, _ = resolve_style_colors(palette, nstyle)
        if n.get("recessed"):
            cfill = palette["card_bg_recessed"]

        parent_zid = n.get("zone")
        if parent_zid and parent_zid in zone_map:
            zx, zy, zw, zh = zone_map[parent_zid]
            if nx < zx + 8 or ny < zy + 42 or (nx + nw) > (zx + zw - 8) or (ny + nh) > (zy + zh - 8):
                db.warnings.append(
                    f"[LAYOUT WARNING] Node '{nid}' ({int(nx)},{int(ny)},{int(nw)}x{int(nh)}) "
                    f"overflows parent zone '{parent_zid}' ({int(zx)},{int(zy)},{int(zw)}x{int(zh)})."
                )

        for prev_id, (px, py, pw, ph) in node_rects:
            if not (nx + nw <= px + 2 or px + pw <= nx + 2 or ny + nh <= py + 2 or py + ph <= ny + 2):
                db.warnings.append(
                    f"[LAYOUT WARNING] Node '{nid}' overlaps node '{prev_id}'."
                )
        node_rects.append((nid, nrect))

        ndashed = ' stroke-dasharray="5,4"' if n.get("dashed") else ""
        db.layer_cards.append(
            f'    <rect x="{nx:.1f}" y="{ny:.1f}" width="{nw:.1f}" height="{nh:.1f}" rx="6" '
            f'fill="{cfill}" stroke="{bcol}" stroke-width="1.8"{ndashed} filter="url(#card-shadow)"/>'
        )
        db.layer_cards.append(
            f'    <rect x="{nx + 1:.1f}" y="{ny + 1:.1f}" width="{nw - 2:.1f}" height="4.5" rx="3" fill="{hdr_col}"/>'
        )

        ntitle = str(n.get("title", ""))
        nlines = list(n.get("lines", []))
        db.check_fit(ntitle, nw - 18, 12, f"Node '{nid}' title")

        total_lines = 1 + len(nlines)
        block_h = 20 + len(nlines) * 18
        start_y = ny + max(24.0, (nh - block_h) / 2.0 + 15.0)

        db.layer_cards.append(
            f'    <text x="{nx + nw / 2.0:.1f}" y="{start_y:.1f}" text-anchor="middle" '
            f'font-family="{palette["mono_stack"]}" font-size="12.8" font-weight="bold" '
            f'fill="{palette["text_bright"]}">{esc(ntitle)}</text>'
        )
        cur_ly = start_y + 20.0
        for idx_l, raw_ln in enumerate(nlines):
            db.check_fit(raw_ln, nw - 18, 11, f"Node '{nid}' line {idx_l + 1}")
            if cur_ly > ny + nh - 6:
                db.warnings.append(
                    f"[LAYOUT WARNING] Node '{nid}' vertical text overflow (total_lines={total_lines}, h={int(nh)})."
                )
            markup = render_inline_markup(raw_ln, bold_fill=palette["text_bright"])
            db.layer_cards.append(
                f'    <text x="{nx + nw / 2.0:.1f}" y="{cur_ly:.1f}" text-anchor="middle" '
                f'font-family="{palette["font_stack"]}" font-size="11.6" '
                f'fill="{palette["text_muted"] if idx_l == len(nlines) - 1 and len(nlines) >= 2 else palette["text_primary"]}">{markup}</text>'
            )
            cur_ly += 18.0

    # 3. Render Orthogonal Manhattan Connectors & Verify Zero Card Collisions
    pill_boxes: List[Tuple[str, Tuple[float, float, float, float]]] = []
    for e_idx, e in enumerate(edges):
        src_id = str(e.get("from", ""))
        dst_id = str(e.get("to", ""))
        estyle = e.get("style", "tertiary")
        edashed = bool(e.get("dashed", False))
        elabel = str(e.get("label", ""))

        if "points" in e and e["points"]:
            pts = [(float(pt[0]), float(pt[1])) for pt in e["points"]]
        else:
            if src_id not in box_map or dst_id not in box_map:
                db.schema_errors.append(f"[SCHEMA ERROR] Edge #{e_idx + 1} references unknown ID: '{src_id}' -> '{dst_id}'")
                continue
            p_start = _rect_port(box_map[src_id], e.get("from_side", "bottom"), float(e.get("from_offset", 0.0)))
            p_end = _rect_port(box_map[dst_id], e.get("to_side", "top"), float(e.get("to_offset", 0.0)))
            if "waypoints" in e and e["waypoints"]:
                pts = [p_start] + [(float(w[0]), float(w[1])) for w in e["waypoints"]] + [p_end]
            elif "mid_y" in e:
                my = float(e["mid_y"])
                pts = [p_start, (p_start[0], my), (p_end[0], my), p_end]
            elif "mid_x" in e:
                mx = float(e["mid_x"])
                pts = [p_start, (mx, p_start[1]), (mx, p_end[1]), p_end]
            else:
                if abs(p_start[0] - p_end[0]) < 1.0 or abs(p_start[1] - p_end[1]) < 1.0:
                    pts = [p_start, p_end]
                else:
                    my = (p_start[1] + p_end[1]) / 2.0
                    pts = [p_start, (p_start[0], my), (p_end[0], my), p_end]

        for pt_i, (ptx, pty) in enumerate(pts):
            if ptx < 8 or ptx > width - 8 or pty < 8 or pty > height - 8:
                db.warnings.append(
                    f"[LAYOUT WARNING] Edge '{src_id}->{dst_id}' point {pt_i + 1} ({int(ptx)},{int(pty)}) "
                    f"falls outside safe canvas bounds ({width}x{height})."
                )
        for s_i in range(len(pts) - 1):
            seg_a, seg_b = pts[s_i], pts[s_i + 1]
            for nid, nrect in node_rects:
                if nid in (src_id, dst_id):
                    continue
                if _segment_hits_rect(seg_a, seg_b, nrect, pad=2.0):
                    db.warnings.append(
                        f"[LAYOUT WARNING] Edge '{src_id}->{dst_id}' segment {s_i + 1} "
                        f"({int(seg_a[0])},{int(seg_a[1])})->({int(seg_b[0])},{int(seg_b[1])}) "
                        f"crosses unrelated node '{nid}'."
                    )

        ppos = tuple(e["pill_pos"]) if "pill_pos" in e and e["pill_pos"] else None
        if elabel:
            if ppos:
                cx, cy = float(ppos[0]), float(ppos[1])
            elif len(pts) >= 4:
                cx = (pts[1][0] + pts[2][0]) / 2.0
                cy = (pts[1][1] + pts[2][1]) / 2.0
            else:
                cx = (pts[0][0] + pts[-1][0]) / 2.0
                cy = (pts[0][1] + pts[-1][1]) / 2.0
            pw = max(84.0, len(elabel) * 7.6 + 24.0)
            ph = 24.0
            pbox = (cx - pw / 2.0, cy - ph / 2.0, pw, ph)
            if pbox[0] < 8 or pbox[0] + pw > width - 8 or pbox[1] < 8 or pbox[1] + ph > height - 8:
                db.warnings.append(
                    f"[LAYOUT WARNING] Edge pill '{elabel}' ({int(pbox[0])}..{int(pbox[0] + pw)}) clips canvas edge ({width}x{height})."
                )
            for nid, (nx, ny, nw, nh) in node_rects:
                if not (pbox[0] + pw <= nx + 2 or nx + nw <= pbox[0] + 2 or pbox[1] + ph <= ny + 2 or ny + nh <= pbox[1] + 2):
                    db.warnings.append(
                        f"[LAYOUT WARNING] Edge pill '{elabel}' overlaps node card '{nid}' — widen channel or move pill_pos."
                    )
            for prev_lbl, (bx, by, bw, bh) in pill_boxes:
                if not (pbox[0] + pw <= bx + 2 or bx + bw <= pbox[0] + 2 or pbox[1] + ph <= by + 2 or by + bh <= pbox[1] + 2):
                    db.warnings.append(
                        f"[LAYOUT WARNING] Edge pill '{elabel}' overlaps pill '{prev_lbl}'."
                    )
            pill_boxes.append((elabel, pbox))
            ppos = (cx, cy)

        db.add_connector(pts, style=estyle, label=elabel, dashed=edashed, pill_pos=ppos)

    db.add_footer(
        spec.get("footer_left", "Homunculus Visual Diagram Studio — Spatial System Topology"),
        spec.get("footer_right", f"Palette: {palette.get('palette_name', palette.get('palette_id'))}"),
    )
    return db


def convert_svg_to_png(svg_path: Path, png_path: Path, zoom: float = 2.0) -> bool:
    rsvg = shutil.which("rsvg-convert")
    if rsvg:
        subprocess.run(
            [rsvg, "-z", str(zoom), "-f", "png", "-o", str(png_path), str(svg_path)],
            check=True,
        )
        return True
    for edge_bin in ("msedge", "microsoft-edge", "chromium", "google-chrome"):
        browser = shutil.which(edge_bin)
        if browser:
            subprocess.run(
                [
                    browser,
                    "--headless",
                    "--disable-gpu",
                    f"--screenshot={png_path}",
                    "--window-size=3200,2200",
                    str(svg_path),
                ],
                check=True,
            )
            return True
    return False


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Render publication-grade SVG technical diagrams (plus opt-in 300 DPI PNG / GitHub showcase cards) using Obsidian Vault Color Palettes and Blueprints."
    )
    parser.add_argument("--list-palettes", action="store_true", help="List discovered color palettes (built-in + <memory_root>/Templates/)")
    parser.add_argument("--list-blueprints", action="store_true", help="List discovered diagram blueprints (built-in + <memory_root>/Templates/)")
    parser.add_argument("--memory-root", type=str, default=None, help="Optional <memory_root> path to discover custom Templates/Color_Palettes/ and Templates/Diagram_Blueprints/")
    parser.add_argument("--spec", type=str, help="Path to JSON spec file or Blueprint .md file")
    parser.add_argument("--blueprint", type=str, help="Render directly from a registered blueprint ID (demo/template mode)")
    parser.add_argument("--palette", type=str, default="default_dark", help="Palette ID or alias from Templates/Color_Palettes/")
    parser.add_argument("--out-dir", type=str, default=".", help="Output directory for .svg (and opt-in .png) files")
    parser.add_argument("--basename", type=str, default="Technical_Diagram", help="Output filename stem (without extension)")
    parser.add_argument("-o", "--output", type=str, default=None, help="Explicit output .svg path (overrides --out-dir and --basename)")
    parser.add_argument("--png", action="store_true", help="Also rasterize a 300 DPI .png alongside the .svg")
    parser.add_argument("--preview-png", type=str, default=None, help="Optional disposable PNG path (e.g. /tmp/preview.png) for vision checks without storing a repo PNG")
    parser.add_argument("--github-card", action="store_true", help="Also generate a 300 DPI PNG + GitHub showcase card PNG via format_image.py")
    parser.add_argument("--svg-only", action="store_true", help="Explicit alias for default SVG-only mode (skips repo PNG rasterization)")
    parser.add_argument("--strict", action="store_true", help="Exit non-zero if any layout warning is emitted")
    args = parser.parse_args()

    active_mem = (
        Path(args.memory_root).expanduser().resolve()
        if args.memory_root
        else _resolve_active_memory_root()
    )
    palettes = discover_palettes(memory_root=active_mem)
    blueprints = discover_blueprints(memory_root=active_mem)

    if args.list_palettes:
        seen = set()
        print("=== Registered Color Palettes (Templates/Color_Palettes/) ===")
        for pid, pdata in palettes.items():
            real_id = pdata.get("palette_id", pid)
            if real_id in seen:
                continue
            seen.add(real_id)
            print(
                f"  - {real_id:<18} | {pdata.get('palette_name', ''):<42} "
                f"| mode={pdata.get('mode')} | canvas={pdata.get('canvas_bg')} "
                f"| accent={pdata.get('primary_accent')}"
            )
        return 0

    if args.list_blueprints:
        seen = set()
        print("=== Registered Diagram Blueprints (Templates/Diagram_Blueprints/) ===")
        for bid, bdata in blueprints.items():
            real_id = bdata.get("archetype", bid)
            if real_id in seen:
                continue
            seen.add(real_id)
            print(
                f"  - {real_id:<28} | {bdata.get('title', '')} "
                f"({Path(bdata.get('_source_file', '')).name})"
            )
        return 0

    palette_key = normalize_key(args.palette)
    if palette_key not in palettes:
        print(
            f"[ERROR] Unknown palette '{args.palette}'. Run --list-palettes to see registered palettes.",
            file=sys.stderr,
        )
        return 1
    palette = palettes[palette_key]

    if args.spec:
        spec = load_spec(Path(args.spec))
    elif args.blueprint:
        bkey = normalize_key(args.blueprint)
        if bkey not in blueprints:
            print(
                f"[ERROR] Unknown blueprint '{args.blueprint}'. Run --list-blueprints to see options.",
                file=sys.stderr,
            )
            return 1
        spec = blueprints[bkey]
    else:
        parser.print_help()
        return 1

    archetype = normalize_key(spec.get("archetype", "layered_architecture"))
    if archetype == "layered_architecture":
        db = render_layered_architecture(spec, palette)
    elif archetype == "column_dataflow":
        db = render_column_dataflow(spec, palette)
    elif archetype == "hardware_pinout_pneumatic":
        db = render_hardware_pinout_pneumatic(spec, palette)
    elif archetype == "comparison_matrix":
        db = render_comparison_matrix(spec, palette)
    elif archetype == "spatial_topology":
        db = render_spatial_topology(spec, palette)
    else:
        print(f"[ERROR] Unsupported diagram archetype: '{archetype}'", file=sys.stderr)
        return 1

    if args.output:
        svg_path = Path(args.output)
        out_dir = svg_path.parent
        out_dir.mkdir(parents=True, exist_ok=True)
        args.basename = svg_path.stem
        png_path = out_dir / f"{args.basename}.png"
    else:
        out_dir = Path(args.out_dir)
        out_dir.mkdir(parents=True, exist_ok=True)
        svg_path = out_dir / f"{args.basename}.svg"
        png_path = out_dir / f"{args.basename}.png"

    svg_path.write_text(db.to_svg(), encoding="utf-8")

    gate_failed = bool(db.schema_errors) or bool(args.strict and db.warnings)
    want_repo_png = bool(args.png or args.github_card) and not bool(args.svg_only)
    png_ok = False
    preview_ok = False
    card_path: Optional[Path] = None

    if not gate_failed and want_repo_png:
        png_ok = convert_svg_to_png(svg_path, png_path, zoom=2.0)
        if args.github_card and png_ok and FORMAT_IMAGE_SCRIPT.exists():
            card_path = out_dir / f"{args.basename}_card.png"
            subprocess.run(
                [
                    sys.executable,
                    str(FORMAT_IMAGE_SCRIPT),
                    str(png_path),
                    "-o",
                    str(card_path),
                    "--force",
                ],
                check=True,
            )

    if not gate_failed and args.preview_png:
        prev_path = Path(args.preview_png)
        prev_path.parent.mkdir(parents=True, exist_ok=True)
        preview_ok = convert_svg_to_png(svg_path, prev_path, zoom=2.0)

    if gate_failed:
        png_label = "SKIPPED (failed schema/--strict layout gate before rasterization)"
    elif not want_repo_png:
        png_label = "SKIPPED (SVG-only default; pass --png or --github-card for raster export)"
    else:
        png_label = str(png_path) if png_ok else "SKIPPED (no rasterizer)"

    if not gate_failed:
        homunculus_paths.ensure_directory_fresh(workspace_dir=svg_path.parent, homunculus_root=_HOM_ROOT)

    print(
        f"Rendered [{archetype}] with palette [{palette.get('palette_id')}]:\n"
        f"  - SVG: {svg_path}\n"
        f"  - PNG: {png_label}"
    )
    if args.preview_png and preview_ok:
        print(f"  - Preview PNG: {args.preview_png}")
    if card_path:
        print(f"  - GitHub Card PNG: {card_path}")
    print(f"  - Warnings: {len(db.warnings)}")
    for w in db.warnings:
        print(f"    {w}")

    if gate_failed:
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
