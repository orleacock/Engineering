#!/usr/bin/env python3
"""
Homunculus Dual-Mode Engineering Memory Manager & Containment Auditor (`sync_memory.py`).

Governing Priority Law:
    1. Accuracy & Truth -> 2. Efficiency -> 3. Data Safety -> 4. Speed
Supported Operating Systems:
    Windows, macOS, and Linux (100% Python 3.10+ standard library; zero PyYAML/pip dependencies).

Key Architectural Guarantees:
    - Pure-Stdlib Frontmatter Engine: Uses pure-stdlib YAML frontmatter parsing/serialization (zero `import yaml`).
    - Editable Template Scaffolding: Scaffolds all memory notes from editable `Homunculus/templates/memory/*.md`.
    - Separate Domain Telemetry Functions:
        1. `sync_hardware_telemetry()` (`--sync-hardware`) -> `<Project>_Hardware.md`
        2. `sync_software_telemetry()` (`--sync-software`) -> `<Project>_Software.md`
    - Multi-Customer / Peer-Entity Containment (`--audit`):
        Detects and blocks `[CROSS_ENTITY_CONTAMINATION]` across projects belonging to different `entity:` scopes.
    - First-Class Quarantine Zone (`Quarantine/` + `## Quarantine Zone`) and Per-Project `Templates/`.

=== DEVELOPER & AI NAVIGATION MAP ===
  Owning Module : `project-memory` (`skills/project-memory/SKILL.md`)
  Callers       : `homunculus_paths.py` (`ensure_directory_fresh`), `pre-commit.sh`, `post-worktree-sync.sh`, `pre-commit-gate` (Stage X), `test_project_memory.py`, `test_claim_verification.py`
  Callees       : `homunculus_paths.py` (`parse_frontmatter_full`, `ensure_directory_fresh`), `inspect_hardware_ecosystem.py` (`--sync-manifest` subprocess)
  CLI Flags     : --memory-root, --vault, --init-memory, --init-vault, --mode, --convert-mode, --default-entity, --init-project, --project, --section, --repo-path, --type, --entity, --compartment, --sync-hardware, --sync-software, --sync-tree, --sync-trees, --check-stale, --save-handoff, --stopped-at, --receipt, --blockers, --next-steps, --discussion, --handoff-file, --kickstart, --create-project-template, --tasks, --recommend, --umbrella, --tbd-ledger, --sync-tasks, --sync-directory, --sync-visuals, --export-canvas, --canvas-out-dir, --audit, --check, --json
  Symbol Index  (jump directly via read_file StartLine/EndLine):
    - def today_iso (#L99-L100)                      | def sanitize_entity_filename (#L103-L106)
    - def parse_stdlib_frontmatter (#L109-L112)      | def update_frontmatter_fields (#L115-L143)
    - def replace_marker_block (#L146-L157)          | def extract_marker_block (#L160-L169)
    - def get_git_worktree_state (#L172-L191)        | def _sanitize_handoff_checkboxes (#L194-L214)
    - def render_template (#L217-L235)               | def get_git_head_sha (#L238-L243)
    - def build_repo_auto_tree (#L246-L282)          | def build_ascii_directory_tree (#L298-L395)
    - def init_memory_root (#L398-L443)              | def _hex_to_obsidian_rgb (#L446-L447)
    - def _detect_memory_mode (#L450-L459)           | def sync_obsidian_visual_brain (#L462-L777)
    - def _write_obsidian_extras (#L780-L783)        | def convert_memory_mode (#L786-L808)
    - def init_project (#L811-L940)                  | def _resolve_project_repo (#L943-L980)
    - def _extract_markdown_sections (#L1012-L1045)  | def _extract_project_tasks_from_umbrella (#L1048-L1074)
    - def query_project_section (#L1077-L1211)       | def _detect_step_unit_scale (#L1217-L1237)
    - def _parse_step_metrics (#L1246-L1279)         | def _parse_stl_metrics (#L1282-L1307)
    - def sync_hardware_telemetry (#L1310-L1434)     | def _inspect_python_module (#L1440-L1473)
    - def sync_software_telemetry (#L1476-L1577)     | def sync_project_tree (#L1580-L1606)
    - def sync_all_project_trees (#L1609-L1672)      | def check_project_staleness (#L1675-L1688)
    - def save_session_handoff (#L1691-L1785)        | def kickstart_project (#L1788-L1845)
    - def create_project_template (#L1848-L1888)     | def sync_task_rollups (#L1891-L1922)
    - def query_open_tasks (#L1925-L2042)            | def query_tbd_ledger (#L2048-L2192)
    - def sync_root_project_index (#L2195-L2232)     | def _strip_last_synced_line (#L2235-L2237)
    - def sync_directory_trees (#L2240-L2443)        | def audit_memory (#L2446-L2625)
    - def main (#L2628-L3014)
=== END NAVIGATION MAP ===
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import re
import shutil
import struct
import subprocess
import sys
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
HOMUNCULUS_ROOT = SCRIPT_DIR.parents[2]
for _p in (str(SCRIPT_DIR), str(HOMUNCULUS_ROOT / "scripts")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import homunculus_paths  # noqa: E402

FRONTMATTER_RE = re.compile(r"^---\r?\n(.*?)\r?\n---\r?\n", re.DOTALL)
MD_LINK_RE = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")
CHECKBOX_LINE_RE = re.compile(r"^\s*-\s*\[([ xX])\]\s+")
STEP_CARTESIAN_PT_RE = re.compile(
    r"CARTESIAN_POINT\s*\(\s*'[^']*'\s*,\s*\(\s*([-+0-9.eE]+)\s*,\s*([-+0-9.eE]+)\s*,\s*([-+0-9.eE]+)\s*\)\s*\)"
)
STEP_CIRCLE_RADIUS_RE = re.compile(r"CIRCLE\s*\(\s*'[^']*'\s*,\s*#[0-9]+\s*,\s*([-+0-9.eE]+)\s*\)")
CFG_SECTION_RE = re.compile(r"^\s*\[([^\]]+)\]\s*$")
CFG_KV_RE = re.compile(r"^\s*([a-zA-Z0-9_]+)\s*[:=]\s*(.+?)\s*$")

IGNORED_TREE_DIRS = {
    ".git",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    "node_modules",
    ".venv",
    "venv",
    ".tox",
    ".eggs",
    "build",
    "dist",
}


def today_iso() -> str:
    return dt.date.today().isoformat()


def sanitize_entity_filename(entity: str) -> str:
    """Convert an entity/client name into a filesystem-safe identifier."""
    cleaned = re.sub(r"[^A-Za-z0-9_-]+", "_", entity.strip())
    return cleaned.strip("_") or "Default_Entity"


def parse_stdlib_frontmatter(text: str) -> tuple[dict[str, Any], str]:
    """Parse simple YAML frontmatter using 100% Python stdlib."""
    meta, body, _start_line = homunculus_paths.parse_frontmatter_full(text, coerce_bools=True)
    return meta, body


def update_frontmatter_fields(text: str, updates: dict[str, Any]) -> str:
    """Update specific YAML frontmatter keys in-place without PyYAML."""
    match = FRONTMATTER_RE.match(text)
    if not match:
        lines = ["---"]
        for k, v in updates.items():
            lines.append(f'{k}: "{v}"' if isinstance(v, str) else f"{k}: {str(v).lower()}")
        lines.append("---\n")
        return "\n".join(lines) + text

    raw_lines = match.group(1).splitlines()
    body = text[match.end() :]
    seen: set[str] = set()
    out_lines: list[str] = []
    for line in raw_lines:
        if ":" in line and not line.lstrip().startswith("#"):
            k = line.split(":", 1)[0].strip()
            if k in updates:
                v = updates[k]
                formatted = f'{k}: "{v}"' if isinstance(v, str) else f"{k}: {str(v).lower()}"
                out_lines.append(formatted)
                seen.add(k)
                continue
        out_lines.append(line)
    for k, v in updates.items():
        if k not in seen:
            formatted = f'{k}: "{v}"' if isinstance(v, str) else f"{k}: {str(v).lower()}"
            out_lines.append(formatted)
    return "---\n" + "\n".join(out_lines) + "\n---\n" + body


def replace_marker_block(text: str, marker_name: str, new_inner: str) -> str:
    """Replace content between <!-- MARKER:START --> and <!-- MARKER:END -->."""
    start_tag = f"<!-- {marker_name}:START -->"
    end_tag = f"<!-- {marker_name}:END -->"
    pattern = re.compile(
        re.escape(start_tag) + r".*?" + re.escape(end_tag),
        re.DOTALL,
    )
    replacement = f"{start_tag}\n{new_inner.rstrip()}\n{end_tag}"
    if pattern.search(text):
        return pattern.sub(lambda _m: replacement, text, count=1)
    return text.rstrip() + f"\n\n{replacement}\n"


def extract_marker_block(text: str, marker_name: str) -> str:
    """Extract content between <!-- MARKER:START --> and <!-- MARKER:END --> if present."""
    start_tag = f"<!-- {marker_name}:START -->"
    end_tag = f"<!-- {marker_name}:END -->"
    pattern = re.compile(
        re.escape(start_tag) + r"(.*?)" + re.escape(end_tag),
        re.DOTALL,
    )
    match = pattern.search(text)
    return match.group(1).strip() if match else ""


def get_git_worktree_state(repo_path: Path) -> tuple[str, list[str]]:
    """Return ('clean' or 'dirty (<N> files)', list_of_changed_paths) for a git repo."""
    if not repo_path.is_dir() or not (repo_path / ".git").exists():
        return "untracked", []
    try:
        proc = subprocess.run(
            ["git", "-C", str(repo_path), "status", "--porcelain"],
            capture_output=True,
            text=True,
            timeout=3,
            check=False,
        )
        if proc.returncode == 0:
            lines = [ln.strip() for ln in proc.stdout.splitlines() if ln.strip()]
            if not lines:
                return "clean", []
            return f"dirty ({len(lines)} files)", lines
    except Exception:
        pass
    return "untracked", []


def _sanitize_handoff_checkboxes(text: str) -> str:
    """
    Convert accidental `- [ ]` / `- [x]` lines inside a SESSION-HANDOFF block into
    `- [OPEN]` / `- [DONE]` bullets so multi-paragraph handoffs never violate
    `CHECKBOX_IN_PROJECT_HUB` (preserving single-writer Task Umbrellas).
    """
    out: list[str] = []
    in_fence = False
    for line in text.splitlines():
        if line.strip().startswith("```"):
            in_fence = not in_fence
            out.append(line)
            continue
        if not in_fence:
            m = re.match(r"^(\s*-\s*)\[([ xX])\](\s+.*)$", line)
            if m:
                tag = "[DONE]" if m.group(2).lower() == "x" else "[OPEN]"
                out.append(f"{m.group(1)}{tag}{m.group(3)}")
                continue
        out.append(line)
    return "\n".join(out)


def render_template(template_name: str, context: dict[str, str], memory_root: Path | None = None) -> str:
    """Load template from <memory_root>/Templates/ if customized, else Homunculus/templates/memory/."""
    candidate_paths: list[Path] = []
    if memory_root is not None:
        candidate_paths.append(memory_root / "Templates" / template_name)
    candidate_paths.append(HOMUNCULUS_ROOT / "templates" / "memory" / template_name)

    template_text = ""
    for p in candidate_paths:
        if p.is_file():
            template_text = p.read_text(encoding="utf-8")
            break
    if not template_text:
        raise FileNotFoundError(f"Memory template not found: {template_name}")

    rendered = template_text
    for key, val in context.items():
        rendered = rendered.replace(f"{{{{{key}}}}}", str(val))
    return rendered


def get_git_head_sha(repo_path: Path) -> str:
    """Return short git HEAD SHA or 'UNTRACKED' if not a git repo (fast ~0.06ms direct .git/HEAD read)."""
    if not repo_path.is_dir() or not (repo_path / ".git").exists():
        return "UNTRACKED"
    sha = homunculus_paths.read_git_head_sha(repo_path, length=12)
    return sha if sha else "UNTRACKED"


def build_repo_auto_tree(repo_path: Path, max_depth: int = 3, max_entries: int = 160) -> tuple[str, str]:
    """Generate a deterministic POSIX file tree and SHA-256 tree_hash for repo_path."""
    if not repo_path.is_dir():
        return f"Repository path not found on disk: {repo_path.as_posix()}", "MISSING"

    rel_entries: list[str] = []
    for root, dirs, files in os.walk(repo_path):
        dirs[:] = sorted(d for d in dirs if d not in IGNORED_TREE_DIRS and not d.startswith(".cache"))
        rel_dir = Path(root).relative_to(repo_path)
        depth = 0 if str(rel_dir) == "." else len(rel_dir.parts)
        if depth > max_depth:
            dirs[:] = []
            continue
        if str(rel_dir) != ".":
            rel_entries.append(f"{rel_dir.as_posix()}/")
        for f in sorted(files):
            if f.startswith(".") and f not in (".cursorignore", ".claudeignore", ".geminiignore", ".gitignore"):
                continue
            rel_file = (rel_dir / f).as_posix() if str(rel_dir) != "." else f
            rel_entries.append(rel_file)
            if len(rel_entries) >= max_entries:
                break
        if len(rel_entries) >= max_entries:
            break

    digest = hashlib.sha256("\n".join(rel_entries).encode("utf-8")).hexdigest()[:12]
    head_sha = get_git_head_sha(repo_path)
    lines = [
        "```text",
        f"Repository: {repo_path.name} | HEAD SHA: {head_sha} | Tree Hash: {digest}",
    ]
    for entry in rel_entries:
        lines.append(f"  {entry}")
    if len(rel_entries) >= max_entries:
        lines.append(f"  ... (truncated at {max_entries} entries)")
    lines.append("```")
    return "\n".join(lines), digest


ALLOWED_DOTFILES = frozenset({
    ".gitignore",
    ".gitattributes",
    ".editorconfig",
    ".npmrc",
    ".cursorignore",
    ".claudeignore",
    ".geminiignore",
    ".homunculus.json",
})
ALLOWED_DOTDIRS = frozenset({".github"})


def build_ascii_directory_tree(
    root_path: Path,
    max_depth: int = 3,
    max_entries: int = 180,
    allowed_top_dirs: set[str] | None = None,
    allowed_projects: set[str] | None = None,
    allowed_task_files: set[str] | None = None,
    allowed_directory_files: set[str] | None = None,
) -> tuple[str, str]:
    """
    Render a box-header ASCII directory tree (`├──` / `└──`) matching the Homunculus Directory standard,
    plus a deterministic 12-hex SHA-256 tree hash.
    """
    banner = "+------------------------------------------------------------+"
    header = [
        "```text",
        banner,
        "            --- DIRECTORY STRUCTURE ---",
        banner,
        "",
        "./",
    ]
    if not root_path.is_dir():
        header.append(f"└── [missing on disk: {root_path.name}]")
        header.append(banner)
        header.append("```")
        return "\n".join(header), "MISSING"

    flat_manifest: list[str] = []
    entry_count = 0
    truncated = False

    def _walk_dir(cur_dir: Path, prefix: str, depth: int) -> None:
        nonlocal entry_count, truncated
        if truncated or depth > max_depth:
            return
        try:
            raw_items = sorted(cur_dir.iterdir(), key=lambda p: p.name.lower())
        except OSError:
            return

        subdirs: list[Path] = []
        files: list[Path] = []
        rel_cur = cur_dir.relative_to(root_path)

        for item in raw_items:
            name = item.name
            if item.is_dir():
                if name in IGNORED_TREE_DIRS or name.startswith(".cache") or name == ".obsidian":
                    continue
                if name.startswith(".") and name not in ALLOWED_DOTDIRS:
                    continue
                if depth == 0 and allowed_top_dirs is not None and name not in allowed_top_dirs:
                    continue
                if depth == 1 and rel_cur.as_posix() == "Projects" and allowed_projects is not None:
                    if name not in allowed_projects:
                        continue
                subdirs.append(item)
            elif item.is_file():
                if name.startswith(".") and name not in ALLOWED_DOTFILES:
                    continue
                if depth == 1 and rel_cur.as_posix() == "Projects" and name.endswith(".base"):
                    continue
                if depth == 1 and rel_cur.as_posix() == "Tasks" and allowed_task_files is not None:
                    if name not in allowed_task_files:
                        continue
                if depth == 1 and rel_cur.as_posix() == "Directory" and allowed_directory_files is not None:
                    if name not in allowed_directory_files:
                        continue
                files.append(item)

        entries: list[tuple[str, Path | None]] = [(f"{d.name}/", d) for d in subdirs]
        if depth == 0 and (cur_dir / ".git").exists():
            entries.append((".git/ (excluded)", None))
        entries.extend((f.name, None) for f in files)

        for idx, (label, dir_obj) in enumerate(entries):
            if entry_count >= max_entries:
                truncated = True
                header.append(f"{prefix}└── ... (truncated at {max_entries} entries)")
                return
            is_last = idx == len(entries) - 1
            connector = "└── " if is_last else "├── "
            header.append(f"{prefix}{connector}{label}")
            rel_entry = (rel_cur / label.rstrip("/")).as_posix() if str(rel_cur) != "." else label
            flat_manifest.append(rel_entry)
            entry_count += 1
            if dir_obj is not None and depth < max_depth:
                child_prefix = prefix + ("    " if is_last else "│   ")
                _walk_dir(dir_obj, child_prefix, depth + 1)
                if truncated:
                    return

    _walk_dir(root_path, "", 0)
    header.append(banner)
    header.append("```")
    digest = hashlib.sha256("\n".join(flat_manifest).encode("utf-8")).hexdigest()[:12]
    return "\n".join(header), digest


def init_memory_root(
    memory_root: Path,
    mode: str = "headless",
    default_entity: str = "Default_Entity",
    title: str = "Engineering Memory",
) -> dict[str, Any]:
    """Scaffold a Dual-Mode (`headless` or `obsidian`) memory root directory."""
    memory_root = memory_root.resolve()
    for subdir in ("Directory", "Projects", "Tasks", "Standards_and_Specs", "Templates", "Diagrams"):
        (memory_root / subdir).mkdir(parents=True, exist_ok=True)

    # Copy canonical templates from Homunculus/templates/memory/ into <memory_root>/Templates/
    src_templates = HOMUNCULUS_ROOT / "templates" / "memory"
    copied_templates: list[str] = []
    if src_templates.is_dir():
        for tmpl in sorted(src_templates.glob("*.md")):
            dst = memory_root / "Templates" / tmpl.name
            if not dst.exists():
                shutil.copy2(tmpl, dst)
                copied_templates.append(str(dst))

    ctx = {
        "MEMORY_TITLE": title,
        "MEMORY_MODE": mode,
        "DEFAULT_ENTITY": default_entity,
        "DATE": today_iso(),
    }
    readme_path = memory_root / "README.md"
    if not readme_path.exists():
        readme_path.write_text(render_template("Memory_Map_README.md", ctx, memory_root), encoding="utf-8")

    standards_path = memory_root / "Standards_and_Specs" / "Standards_Index.md"
    if not standards_path.exists():
        standards_path.write_text(render_template("Global_Standards_Index.md", ctx, memory_root), encoding="utf-8")

    sync_directory_trees(memory_root)
    if mode == "obsidian":
        _write_obsidian_extras(memory_root)

    return {
        "status": "PASS",
        "memory_root": str(memory_root),
        "mode": mode,
        "default_entity": default_entity,
        "templates_seeded": len(copied_templates),
    }


def _hex_to_obsidian_rgb(hex_code: str) -> int:
    return int(hex_code.lstrip("#"), 16)


def _detect_memory_mode(memory_root: Path) -> str:
    readme_path = memory_root / "README.md"
    if readme_path.is_file():
        fm, _ = parse_stdlib_frontmatter(readme_path.read_text(encoding="utf-8", errors="ignore"))
        mode_val = str(fm.get("memory_mode", "")).strip().lower()
        if mode_val in ("headless", "obsidian"):
            return mode_val
    if (memory_root / ".obsidian").is_dir() or (memory_root / "Projects" / "Projects_Directory.base").is_file():
        return "obsidian"
    return "headless"


def sync_obsidian_visual_brain(
    memory_root: Path,
    export_canvas: bool = False,
    canvas_out_dir: Path | None = None,
) -> dict[str, Any]:
    """
    Dynamic Obsidian Visual-Brain Generator (`--sync-visuals` in `obsidian` mode & `--export-canvas`):
    100% dynamically discovers indexed entities, project hubs, telemetry manifests, and task umbrellas to build:
      1. `Projects/Projects_Directory.base` (with dynamic per-entity filtered views + universal portfolio views)
      2. `.obsidian/graph.json` semantic colorGroups (preserving existing user physics/zoom settings)
      3. `Diagrams/Project_Ecosystem_Map.canvas` (JSON Canvas 1.0 topology grouped by entity with zero cross-entity edges)
    """
    memory_root = memory_root.resolve()
    projects_dir = memory_root / "Projects"
    projects_dir.mkdir(parents=True, exist_ok=True)
    written_files: list[str] = []

    # Discover all indexed project hubs grouped by entity
    entities_map: dict[str, list[dict[str, Any]]] = {}
    for hub in sorted(projects_dir.glob("*/*.md")):
        if hub.stem != hub.parent.name:
            continue
        text = hub.read_text(encoding="utf-8", errors="ignore")
        fm, _ = parse_stdlib_frontmatter(text)
        proj = hub.stem
        ent = str(fm.get("entity", "Default_Entity")).strip() or "Default_Entity"
        comp = str(fm.get("compartment", "private")).strip()
        ptype = str(fm.get("project_type", "software")).strip()
        worktree = str(fm.get("checkpoint_worktree", fm.get("status", "clean"))).strip()
        has_tbd = bool(re.search(r"\[(?:TBD|CONFLICT)", text, re.IGNORECASE))
        has_hw = (hub.parent / f"{proj}_Hardware.md").is_file()
        has_sw = (hub.parent / f"{proj}_Software.md").is_file()
        entities_map.setdefault(ent, []).append({
            "project": proj,
            "entity": ent,
            "compartment": comp,
            "project_type": ptype,
            "worktree": worktree,
            "has_tbd": has_tbd,
            "has_hw": has_hw,
            "has_sw": has_sw,
            "rel_hub": f"Projects/{proj}/{proj}.md",
        })

    # 1. Generate dynamic `Projects/Projects_Directory.base`
    base_lines = [
        "# Auto-generated by Homunculus sync_memory.py (Dual-Mode Obsidian Visual-Brain)",
        "filters:",
        "  and:",
        '    - file.inFolder("Projects")',
        '    - file.ext == "md"',
        '    - "project != null"',
        "",
        "properties:",
        "  file.name:",
        '    displayName: "Project Dossier"',
        "  note.entity:",
        '    displayName: "Entity"',
        "  note.compartment:",
        '    displayName: "Compartment"',
        "  note.project_type:",
        '    displayName: "Archetype"',
        "  note.status:",
        '    displayName: "Status"',
        "  note.repo_head_sha:",
        '    displayName: "HEAD SHA"',
        "  note.checkpoint_worktree:",
        '    displayName: "Worktree State"',
        "  note.last_synced:",
        '    displayName: "Last Synced"',
        "  note.local_path:",
        '    displayName: "Repository Path"',
        "",
        "views:",
        "  - type: table",
        '    name: "All Indexed Projects"',
        "    order:",
        "      - file.name",
        "      - note.entity",
        "      - note.compartment",
        "      - note.project_type",
        "      - note.status",
        "      - note.repo_head_sha",
        "      - note.checkpoint_worktree",
        "      - note.last_synced",
        "      - note.local_path",
    ]
    for ent_name in sorted(entities_map.keys()):
        base_lines.extend([
            "  - type: table",
            f'    name: "Entity: {ent_name}"',
            "    filters:",
            "      and:",
            f"        - 'entity == \"{ent_name}\"'",
            "    order:",
            "      - file.name",
            "      - note.compartment",
            "      - note.project_type",
            "      - note.status",
            "      - note.repo_head_sha",
            "      - note.checkpoint_worktree",
            "      - note.local_path",
        ])
    base_lines.extend([
        "  - type: cards",
        '    name: "Session Handoff & Checkpoint Cards"',
        "    order:",
        "      - file.name",
        "      - note.entity",
        "      - note.compartment",
        "      - note.repo_head_sha",
        "      - note.checkpoint_worktree",
    ])
    projects_base = projects_dir / "Projects_Directory.base"
    projects_base.write_text("\n".join(base_lines) + "\n", encoding="utf-8")
    written_files.append(str(projects_base))

    # 2. Update `.obsidian/graph.json` semantic colorGroups if `.obsidian/` exists or in obsidian mode
    obs_dir = memory_root / ".obsidian"
    obs_dir.mkdir(parents=True, exist_ok=True)
    graph_path = obs_dir / "graph.json"
    color_groups: list[dict[str, Any]] = [
        {"query": 'path:"Directory"', "color": {"a": 1, "rgb": _hex_to_obsidian_rgb("#03A6D9")}},
        {"query": 'path:"Tasks"', "color": {"a": 1, "rgb": _hex_to_obsidian_rgb("#FE8019")}},
        {"query": "file:_Hardware", "color": {"a": 1, "rgb": _hex_to_obsidian_rgb("#8EC07C")}},
        {"query": "file:_Software", "color": {"a": 1, "rgb": _hex_to_obsidian_rgb("#83A598")}},
        {"query": "file:_Lessons_Learned", "color": {"a": 1, "rgb": _hex_to_obsidian_rgb("#D3869B")}},
        {"query": 'path:"Quarantine"', "color": {"a": 1, "rgb": _hex_to_obsidian_rgb("#FB4934")}},
        {"query": 'path:"Standards_and_Specs"', "color": {"a": 1, "rgb": _hex_to_obsidian_rgb("#FABD2F")}},
        {"query": 'path:"Templates"', "color": {"a": 1, "rgb": _hex_to_obsidian_rgb("#B8BB26")}},
    ]
    entity_palette = ("#FF3985", "#03A6D9", "#B8BB26", "#D3869B", "#83A598", "#FABD2F")
    for idx, ent_name in enumerate(sorted(entities_map.keys())):
        hex_col = entity_palette[idx % len(entity_palette)]
        color_groups.append(
            {"query": f'["entity":"{ent_name}"]', "color": {"a": 1, "rgb": _hex_to_obsidian_rgb(hex_col)}}
        )
    color_groups.append({"query": 'path:"Projects"', "color": {"a": 1, "rgb": _hex_to_obsidian_rgb("#FF3985")}})

    gdata: dict[str, Any] = {}
    if graph_path.is_file():
        try:
            gdata = json.loads(graph_path.read_text(encoding="utf-8"))
        except Exception:
            gdata = {}
    gdata["colorGroups"] = color_groups
    gdata["collapse-color-groups"] = False
    graph_path.write_text(json.dumps(gdata, indent=2) + "\n", encoding="utf-8")
    written_files.append(str(graph_path))

    # 3. Optional JSON Canvas 1.0 Topology Map (`--export-canvas`)
    canvas_path_str = ""
    if export_canvas or canvas_out_dir is not None:
        out_dir = canvas_out_dir.resolve() if canvas_out_dir is not None else (memory_root / "Diagrams")
        out_dir.mkdir(parents=True, exist_ok=True)
        canvas_file = out_dir / "Project_Ecosystem_Map.canvas"

        nodes: list[dict[str, Any]] = [
            {
                "id": "nd-root-readme",
                "type": "file",
                "file": "README.md",
                "x": 0,
                "y": -380,
                "width": 520,
                "height": 240,
                "color": "#FABD2F",
            },
            {
                "id": "nd-projects-base",
                "type": "file",
                "file": "Projects/Projects_Directory.base",
                "x": 580,
                "y": -380,
                "width": 480,
                "height": 240,
                "color": "#8EC07C",
            },
        ]
        edges: list[dict[str, Any]] = []

        cur_y = -60
        for e_idx, ent_name in enumerate(sorted(entities_map.keys())):
            projs = entities_map[ent_name]
            ent_safe = sanitize_entity_filename(ent_name)
            ent_color = entity_palette[e_idx % len(entity_palette)]
            cols = max(1, min(4, len(projs)))
            rows_cnt = (len(projs) + cols - 1) // cols
            grp_width = max(620, cols * 440 + 420)
            grp_height = max(420, rows_cnt * 460 + 100)
            grp_id = f"grp-entity-{ent_safe.lower()}"

            nodes.append({
                "id": grp_id,
                "type": "group",
                "label": f"Entity Compartment: {ent_name} ({len(projs)} Projects — Zero Cross-Entity Links)",
                "x": -60,
                "y": cur_y,
                "width": grp_width,
                "height": grp_height,
                "color": ent_color,
            })

            umb_rel = f"Tasks/{ent_safe}_Tasks.md"
            umb_id = f"nd-tasks-{ent_safe.lower()}"
            if (memory_root / umb_rel).is_file():
                nodes.append({
                    "id": umb_id,
                    "type": "file",
                    "file": umb_rel,
                    "x": -20,
                    "y": cur_y + 50,
                    "width": 340,
                    "height": 320,
                    "color": "#FE8019",
                })

            for p_idx, p_info in enumerate(projs):
                col = p_idx % cols
                row = p_idx // cols
                px = 360 + col * 430
                py = cur_y + 50 + row * 440
                pname = p_info["project"]
                pid = f"nd-proj-{pname.lower()}"

                # Health color: orange if dirty, yellow if open TBD, green if clean
                wt_low = p_info["worktree"].lower()
                if "dirty" in wt_low:
                    p_color = "#FE8019"
                elif p_info["has_tbd"]:
                    p_color = "#FABD2F"
                else:
                    p_color = "#8EC07C"

                nodes.append({
                    "id": pid,
                    "type": "file",
                    "file": p_info["rel_hub"],
                    "x": px,
                    "y": py,
                    "width": 380,
                    "height": 220,
                    "color": p_color,
                })

                if (memory_root / umb_rel).is_file():
                    edges.append({
                        "id": f"ed-task-{pname.lower()}",
                        "fromNode": umb_id,
                        "fromSide": "right",
                        "toNode": pid,
                        "toSide": "left",
                        "toEnd": "arrow",
                        "label": "Single-Writer Tasks",
                        "color": "#FE8019",
                    })

                if p_info["has_hw"]:
                    hw_id = f"nd-hw-{pname.lower()}"
                    nodes.append({
                        "id": hw_id,
                        "type": "file",
                        "file": f"Projects/{pname}/{pname}_Hardware.md",
                        "x": px,
                        "y": py + 240,
                        "width": 380,
                        "height": 150,
                        "color": "#8EC07C",
                    })
                    edges.append({
                        "id": f"ed-hw-{pname.lower()}",
                        "fromNode": hw_id,
                        "fromSide": "top",
                        "toNode": pid,
                        "toSide": "bottom",
                        "toEnd": "arrow",
                        "label": "CAD / CFG Telemetry",
                        "color": "#8EC07C",
                    })
                elif p_info["has_sw"]:
                    sw_id = f"nd-sw-{pname.lower()}"
                    nodes.append({
                        "id": sw_id,
                        "type": "file",
                        "file": f"Projects/{pname}/{pname}_Software.md",
                        "x": px,
                        "y": py + 240,
                        "width": 380,
                        "height": 150,
                        "color": "#83A598",
                    })
                    edges.append({
                        "id": f"ed-sw-{pname.lower()}",
                        "fromNode": sw_id,
                        "fromSide": "top",
                        "toNode": pid,
                        "toSide": "bottom",
                        "toEnd": "arrow",
                        "label": "Software Telemetry",
                        "color": "#83A598",
                    })

            cur_y += grp_height + 80

        canvas_payload = {"nodes": nodes, "edges": edges}
        canvas_file.write_text(json.dumps(canvas_payload, indent=2) + "\n", encoding="utf-8")
        canvas_path_str = str(canvas_file)
        written_files.append(canvas_path_str)

    return {
        "status": "PASS",
        "entities_indexed": len(entities_map),
        "projects_indexed": sum(len(v) for v in entities_map.values()),
        "canvas_file": canvas_path_str,
        "written_files": written_files,
    }


def _write_obsidian_extras(memory_root: Path) -> list[str]:
    """Create or refresh Obsidian `.base` and `.obsidian/graph.json` files when operating in `obsidian` vault mode."""
    res = sync_obsidian_visual_brain(memory_root, export_canvas=False)
    return res["written_files"]


def convert_memory_mode(memory_root: Path, target_mode: str) -> dict[str, Any]:
    """Switch an existing memory tree between `headless` and `obsidian` modes non-destructively."""
    readme_path = memory_root / "README.md"
    if readme_path.is_file():
        updated = update_frontmatter_fields(
            readme_path.read_text(encoding="utf-8"),
            {"memory_mode": target_mode, "last_synced": today_iso()},
        )
        readme_path.write_text(updated, encoding="utf-8")

    extras: list[str] = []
    base_file = memory_root / "Projects" / "Projects_Directory.base"
    if target_mode == "obsidian":
        extras = _write_obsidian_extras(memory_root)
    elif target_mode == "headless" and base_file.is_file():
        base_file.unlink()

    return {
        "status": "PASS",
        "memory_root": str(memory_root),
        "converted_to": target_mode,
        "obsidian_extras": extras,
    }


def init_project(
    memory_root: Path,
    project_name: str,
    repo_path: Path | None = None,
    project_type: str = "software",
    entity: str = "Default_Entity",
    compartment: str = "private",
) -> dict[str, Any]:
    """
    Scaffold a self-contained project folder under `<memory_root>/Projects/<Project>/`:
      - `<Project>.md` (Hub Dossier + `AUTO-TREE` + `Quarantine Zone`)
      - `<Project>_Hardware.md` (if `project_type` in `("hardware", "hybrid")`)
      - `<Project>_Software.md` (if `project_type` in `("software", "hybrid")`)
      - `<Project>_Lessons_Learned.md`
      - `Templates/` (Per-project custom deliverable templates folder)
      - `Quarantine/Quarantine_README.md` (`quarantine: true` unverified holding zone)
      - Registers project inside `Tasks/<Entity>_Tasks.md` and `<memory_root>/README.md`.
    """
    memory_root = memory_root.resolve()
    if not (memory_root / "Projects").is_dir():
        init_memory_root(memory_root, mode="headless", default_entity=entity)

    proj_dir = memory_root / "Projects" / project_name
    proj_dir.mkdir(parents=True, exist_ok=True)
    (proj_dir / "Templates").mkdir(parents=True, exist_ok=True)
    (proj_dir / "Quarantine").mkdir(parents=True, exist_ok=True)

    resolved_repo = repo_path.resolve() if repo_path else proj_dir
    try:
        local_path_str = os.path.relpath(resolved_repo, memory_root).replace("\\", "/")
    except ValueError:
        local_path_str = resolved_repo.as_posix()

    head_sha = get_git_head_sha(resolved_repo)
    tree_block, tree_hash = build_repo_auto_tree(resolved_repo)
    entity_safe = sanitize_entity_filename(entity)

    telemetry_rows: list[str] = []
    if project_type in ("hardware", "hybrid"):
        telemetry_rows.append(
            f"| **Hardware Telemetry (`_Hardware.md`)** | [`{project_name}_Hardware.md`]({project_name}_Hardware.md) | "
            "Verified CAD geometry (`.step`/`.stl`), fasteners, and `.cfg`/PCB pinouts. |\n"
        )
    if project_type in ("software", "hybrid"):
        telemetry_rows.append(
            f"| **Software Telemetry (`_Software.md`)** | [`{project_name}_Software.md`]({project_name}_Software.md) | "
            "Verified runtime entrypoints, CLI flag contracts, schemas, and test receipts. |\n"
        )

    ctx = {
        "PROJECT": project_name,
        "ENTITY": entity,
        "ENTITY_SAFE": entity_safe,
        "COMPARTMENT": compartment,
        "PROJECT_TYPE": project_type,
        "LOCAL_PATH": local_path_str,
        "REPO_HEAD_SHA": head_sha,
        "TREE_HASH": tree_hash,
        "INVENTORY_SHA256": tree_hash,
        "TELEMETRY_ROWS": "".join(telemetry_rows),
        "DATE": today_iso(),
    }

    created_files: list[str] = []
    hub_path = proj_dir / f"{project_name}.md"
    if not hub_path.exists():
        hub_text = render_template("Project_Hub.md", ctx, memory_root)
        hub_text = replace_marker_block(hub_text, "AUTO-TREE", tree_block)
        hub_path.write_text(hub_text, encoding="utf-8")
        created_files.append(str(hub_path))

    if project_type in ("hardware", "hybrid"):
        hw_path = proj_dir / f"{project_name}_Hardware.md"
        if not hw_path.exists():
            hw_path.write_text(render_template("Project_Hardware.md", ctx, memory_root), encoding="utf-8")
            created_files.append(str(hw_path))

    if project_type in ("software", "hybrid"):
        sw_path = proj_dir / f"{project_name}_Software.md"
        if not sw_path.exists():
            sw_path.write_text(render_template("Project_Software.md", ctx, memory_root), encoding="utf-8")
            created_files.append(str(sw_path))

    ll_path = proj_dir / f"{project_name}_Lessons_Learned.md"
    if not ll_path.exists():
        ll_path.write_text(render_template("Project_Lessons_Learned.md", ctx, memory_root), encoding="utf-8")
        created_files.append(str(ll_path))

    quar_path = proj_dir / "Quarantine" / "Quarantine_README.md"
    if not quar_path.exists():
        quar_path.write_text(render_template("Quarantine_Note.md", ctx, memory_root), encoding="utf-8")
        created_files.append(str(quar_path))

    # Register in entity-specific Task Umbrella (`Tasks/<Entity>_Tasks.md`)
    task_file = memory_root / "Tasks" / f"{entity_safe}_Tasks.md"
    if not task_file.exists():
        task_file.write_text(render_template("Task_Umbrella.md", ctx, memory_root), encoding="utf-8")
        created_files.append(str(task_file))
    else:
        t_text = task_file.read_text(encoding="utf-8")
        proj_heading = f"### [`{project_name}`](../Projects/{project_name}/{project_name}.md)"
        if proj_heading not in t_text:
            new_sec = (
                f"{proj_heading} (`entity: {entity}`)\n"
                f"- [ ] Complete initial domain telemetry sync for `{project_name}` and review `Projects/{project_name}/Templates/`."
            )
            if "<!-- AUTO-PROJECT-TASKS:END -->" in t_text:
                t_text = t_text.replace(
                    "<!-- AUTO-PROJECT-TASKS:END -->",
                    f"\n{new_sec}\n<!-- AUTO-PROJECT-TASKS:END -->",
                )
            else:
                t_text = t_text.rstrip() + f"\n\n{new_sec}\n"
            task_file.write_text(t_text, encoding="utf-8")

    sync_task_rollups(memory_root)
    sync_root_project_index(memory_root)
    sync_directory_trees(memory_root)

    return {
        "status": "PASS",
        "project": project_name,
        "entity": entity,
        "compartment": compartment,
        "project_type": project_type,
        "created_files": created_files,
        "template_prompt_reminder": (
            f"Ask the user if they want to save any recurring deliverable templates in Projects/{project_name}/Templates/."
        ),
    }


def _resolve_project_repo(memory_root: Path, project_name: str, repo_override: Path | None = None) -> tuple[Path, Path, dict[str, Any]]:
    """Return (hub_path, repo_dir, frontmatter_dict) for a project (supports case-insensitive / substring match)."""
    hub_path = memory_root / "Projects" / project_name / f"{project_name}.md"
    if not hub_path.is_file():
        projects_dir = memory_root / "Projects"
        q_low = project_name.strip().lower()
        matched_hub: Path | None = None
        if projects_dir.is_dir():
            for cand_hub in sorted(projects_dir.glob("*/*.md")):
                if cand_hub.stem != cand_hub.parent.name:
                    continue
                if cand_hub.stem.lower() == q_low:
                    matched_hub = cand_hub
                    break
            if matched_hub is None:
                for cand_hub in sorted(projects_dir.glob("*/*.md")):
                    if cand_hub.stem != cand_hub.parent.name:
                        continue
                    fm_c, _ = parse_stdlib_frontmatter(cand_hub.read_text(encoding="utf-8", errors="ignore"))
                    proj_c = str(fm_c.get("project", "")).lower()
                    if q_low in cand_hub.stem.lower() or (proj_c and q_low in proj_c):
                        matched_hub = cand_hub
                        break
        if matched_hub is not None:
            hub_path = matched_hub
        else:
            raise FileNotFoundError(f"Project hub dossier not found: {hub_path}")
    fm, _ = parse_stdlib_frontmatter(hub_path.read_text(encoding="utf-8"))
    if repo_override is not None:
        return hub_path, repo_override.resolve(), fm
    local_path_str = str(fm.get("local_path", "")).strip().replace("\\", "/")
    if local_path_str:
        cand = Path(local_path_str)
        if not cand.is_absolute():
            cand = (memory_root / cand).resolve()
        if cand.is_dir():
            return hub_path, cand, fm
    return hub_path, hub_path.parent, fm


SECTION_QUERY_CHOICES = (
    "all",
    "concept",
    "root",
    "inventory",
    "specs",
    "hazards",
    "architecture",
    "tbd",
    "tasks",
    "lessons",
    "handoff",
    "hardware",
    "software",
)

SECTION_HEADING_KEYWORDS: dict[str, tuple[str, ...]] = {
    "concept": ("concept", "design philosophy", "executive architecture"),
    "root": ("concept", "design philosophy", "executive architecture"),
    "inventory": ("repository", "file inventory", "repository file tree", "auto-tree"),
    "specs": ("verified specs", "cots", "print matrix", "locked specifications", "key parameters"),
    "hazards": ("paramount assembly", "hazards", "mechanical \"whys\"", "critical"),
    "architecture": ("architectural decisions", "kinematic", "companion", "executive architecture"),
    "tbd": ("provenance status", "open [tbd]", "[conflict] ledger", "quarantine zone"),
    "tasks": ("active tasks", "task umbrella"),
    "handoff": ("session handoff", "kickstart", "session-handoff"),
}


def _extract_markdown_sections(text: str) -> list[tuple[int, str, str]]:
    """Return list of (heading_level, raw_heading_title, section_markdown_including_children)."""
    lines = text.replace("\r\n", "\n").split("\n")
    in_fm = False
    in_code = False
    headings: list[tuple[int, int, str]] = []
    for idx, ln in enumerate(lines):
        s = ln.strip()
        if idx == 0 and s == "---":
            in_fm = True
            continue
        if in_fm:
            if s == "---":
                in_fm = False
            continue
        if s.startswith("```"):
            in_code = not in_code
            continue
        if in_code:
            continue
        m = re.match(r"^(#{1,6})[ \t]+(.+?)[ \t]*$", ln)
        if m:
            headings.append((idx, len(m.group(1)), m.group(2).strip()))

    sections: list[tuple[int, str, str]] = []
    for i, (start_idx, lvl, raw_h) in enumerate(headings):
        end_idx = len(lines)
        for next_idx, next_lvl, _ in headings[i + 1 :]:
            if next_lvl <= lvl:
                end_idx = next_idx
                break
        body = "\n".join(lines[start_idx:end_idx]).rstrip()
        sections.append((lvl, raw_h, body))
    return sections


def _extract_project_tasks_from_umbrella(memory_root: Path, hub_path: Path, fm: dict[str, Any], project_name: str) -> tuple[str, str]:
    """Locate the owning task umbrella and extract the section matching `project_name`."""
    umbrella_rel = str(fm.get("task_umbrella", "")).strip().replace("\\", "/")
    task_path: Path | None = None
    if umbrella_rel:
        cand = (hub_path.parent / umbrella_rel.split("#", 1)[0]).resolve()
        if cand.is_file():
            task_path = cand
    if task_path is None:
        entity = str(fm.get("entity", "Default_Entity"))
        ent_safe = sanitize_entity_filename(entity)
        cand = memory_root / "Tasks" / f"{ent_safe}_Tasks.md"
        if cand.is_file():
            task_path = cand
    if task_path is None or not task_path.is_file():
        return "", ""

    rel_task = task_path.relative_to(memory_root).as_posix()
    t_text = task_path.read_text(encoding="utf-8", errors="ignore")
    t_sections = _extract_markdown_sections(t_text)
    p_low = project_name.lower()
    for lvl, raw_h, body in t_sections:
        if lvl in (2, 3):
            clean_h = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", raw_h).replace("`", "").strip().lower()
            if p_low == clean_h or p_low in clean_h:
                return rel_task, body
    return rel_task, ""


def query_project_section(
    memory_root: Path,
    project_name: str,
    section: str = "all",
    repo_override: Path | None = None,
) -> dict[str, Any]:
    """
    Targeted Memory Dossier & Section Reader (`--project <Name> --section <Section>`):
    Reads a project hub dossier or companion note (`lessons`, `hardware`, `software`) and expands
    transcluded `Tasks/<Entity>_Tasks.md#<Project>` items inline in a single read-only call.
    """
    memory_root = memory_root.resolve()
    hub_path, _repo_dir, fm = _resolve_project_repo(memory_root, project_name, repo_override)
    canonical_proj = hub_path.stem
    proj_dir = hub_path.parent
    rel_hub = hub_path.relative_to(memory_root).as_posix()
    sec_norm = section.strip().lower().replace("-", "_")
    if sec_norm not in SECTION_QUERY_CHOICES:
        raise ValueError(f"Unsupported --section '{section}'. Choose from: {', '.join(SECTION_QUERY_CHOICES)}")

    # Companion file sections: lessons, hardware, software
    companion_map = {
        "lessons": (proj_dir / f"{canonical_proj}_Lessons_Learned.md", "Project Lessons Learned"),
        "hardware": (proj_dir / f"{canonical_proj}_Hardware.md", "Project Hardware Telemetry"),
        "software": (proj_dir / f"{canonical_proj}_Software.md", "Project Software Telemetry"),
    }
    if sec_norm in companion_map:
        comp_path, label = companion_map[sec_norm]
        if not comp_path.is_file():
            return {
                "status": "FAIL",
                "project": canonical_proj,
                "section": sec_norm,
                "source_file": comp_path.relative_to(memory_root).as_posix(),
                "header": f"[WARN] No companion `{comp_path.name}` found in `Projects/{canonical_proj}/`.",
                "content": "",
            }
        rel_comp = comp_path.relative_to(memory_root).as_posix()
        comp_text = comp_path.read_text(encoding="utf-8").replace("\r\n", "\n").rstrip()
        return {
            "status": "PASS",
            "project": canonical_proj,
            "entity": str(fm.get("entity", "Default_Entity")),
            "compartment": str(fm.get("compartment", "private")),
            "section": sec_norm,
            "source_file": rel_comp,
            "header": f"=== {label}: {rel_comp} ===",
            "content": comp_text,
        }

    raw_text = hub_path.read_text(encoding="utf-8").replace("\r\n", "\n")
    rel_task, task_body = _extract_project_tasks_from_umbrella(memory_root, hub_path, fm, canonical_proj)

    # Inline-expand Active Task Queue transclusion pointer when present
    expanded_text = raw_text
    if task_body:
        transcluded_block = f"<!-- Transcluded from {rel_task}#{canonical_proj} -->\n{task_body}"
        if "> **Active Task Queue**:" in expanded_text:
            expanded_text = re.sub(
                r"(> \*\*Active Task Queue\*\*:[^\n]*)",
                lambda m: f"{m.group(1)}\n\n{transcluded_block}",
                expanded_text,
                count=1,
            )
        elif "## 🎯 Active Tasks" not in expanded_text:
            expanded_text = expanded_text.rstrip() + f"\n\n## Active Tasks (Transcluded from `{rel_task}`)\n\n{transcluded_block}\n"

    if sec_norm == "all":
        return {
            "status": "PASS",
            "project": canonical_proj,
            "entity": str(fm.get("entity", "Default_Entity")),
            "compartment": str(fm.get("compartment", "private")),
            "section": "all",
            "source_file": rel_hub,
            "header": f"=== Dossier: {rel_hub} (Transclusions Expanded Inline) ===",
            "content": expanded_text.rstrip(),
        }

    if sec_norm == "tasks":
        if task_body:
            return {
                "status": "PASS",
                "project": canonical_proj,
                "entity": str(fm.get("entity", "Default_Entity")),
                "compartment": str(fm.get("compartment", "private")),
                "section": "tasks",
                "source_file": f"{rel_task}#{canonical_proj}",
                "header": f"=== Dossier Section [tasks]: {rel_task}#{canonical_proj} ===",
                "content": task_body,
            }

    sections = _extract_markdown_sections(expanded_text)
    kws = SECTION_HEADING_KEYWORDS.get(sec_norm, (sec_norm,))
    matched_blocks = [
        body for lvl, raw_h, body in sections if lvl == 2 and any(k in raw_h.lower() for k in kws)
    ]

    # Fallback to explicit marker blocks for handoff, inventory, or tbd if heading wording differs
    if not matched_blocks:
        if sec_norm == "handoff":
            blk = extract_marker_block(expanded_text, "SESSION-HANDOFF")
            if blk:
                matched_blocks.append(blk)
        elif sec_norm == "inventory":
            blk = extract_marker_block(expanded_text, "AUTO-TREE")
            if blk:
                matched_blocks.append(blk)
        elif sec_norm == "tbd":
            blk = extract_marker_block(expanded_text, "QUARANTINE-ZONE")
            if blk:
                matched_blocks.append(blk)

    if not matched_blocks:
        return {
            "status": "FAIL",
            "project": canonical_proj,
            "entity": str(fm.get("entity", "Default_Entity")),
            "compartment": str(fm.get("compartment", "private")),
            "section": sec_norm,
            "source_file": rel_hub,
            "header": f"[WARN] No section matching '{sec_norm}' in {rel_hub}",
            "content": "",
        }

    return {
        "status": "PASS",
        "project": canonical_proj,
        "entity": str(fm.get("entity", "Default_Entity")),
        "compartment": str(fm.get("compartment", "private")),
        "section": sec_norm,
        "source_file": rel_hub,
        "header": f"=== Dossier Section [{sec_norm}]: {rel_hub} ===",
        "content": "\n\n".join(matched_blocks),
    }


# ============================================================================
# Function 1 of 2: Dedicated Hardware Telemetry (`sync_hardware_telemetry`)
# ============================================================================
def _detect_step_unit_scale(
    text: str,
    xs: list[float],
    ys: list[float],
    zs: list[float],
) -> float:
    """Detect STEP file coordinate unit scale factor to millimeters (1.0=mm, 1000.0=m, 10.0=cm, 25.4=inch)."""
    if re.search(r"SI_UNIT\s*\(\s*\$\s*,\s*\.METRE\.\s*\)", text, re.IGNORECASE):
        return 1000.0
    if re.search(r"SI_UNIT\s*\(\s*\.CENTI\.\s*,\s*\.METRE\.\s*\)", text, re.IGNORECASE):
        return 10.0
    if re.search(r"CONVERSION_BASED_UNIT\s*\(\s*'INCH'", text, re.IGNORECASE):
        return 25.4
    if re.search(r"SI_UNIT\s*\(\s*\.MILLI\.\s*,\s*\.METRE\.\s*\)", text, re.IGNORECASE):
        return 1.0
    if xs and ys and zs:
        max_abs = max(max(abs(v) for v in xs), max(abs(v) for v in ys), max(abs(v) for v in zs))
        span = max(max(xs) - min(xs), max(ys) - min(ys), max(zs) - min(zs))
        if 0.0 < max_abs <= 1.5 and 0.0 < span <= 1.5:
            return 1000.0
    return 1.0


STEP_CYL_SURF_RE = re.compile(
    r"CYLINDRICAL_SURFACE\s*\(\s*'[^']*'\s*,\s*#\d+\s*,\s*([+-]?\d+(?:\.\d+)?(?:[eE][+-]?\d+)?)\s*\)",
    re.IGNORECASE,
)


def _parse_step_metrics(step_file: Path) -> tuple[str, str]:
    """Extract unit-scaled bounding box (X x Y x Z mm) and cylindrical bore diameters from an ASCII STEP file."""
    text = step_file.read_text(encoding="utf-8", errors="ignore")
    xs: list[float] = []
    ys: list[float] = []
    zs: list[float] = []
    for m in STEP_CARTESIAN_PT_RE.finditer(text):
        try:
            xs.append(float(m.group(1)))
            ys.append(float(m.group(2)))
            zs.append(float(m.group(3)))
        except ValueError:
            continue
    unit_scale = _detect_step_unit_scale(text, xs, ys, zs)
    if xs and ys and zs:
        dx = (max(xs) - min(xs)) * unit_scale
        dy = (max(ys) - min(ys)) * unit_scale
        dz = (max(zs) - min(zs)) * unit_scale
        bbox = f"`{dx:.2f} x {dy:.2f} x {dz:.2f} mm`"
    else:
        bbox = "`[TBD: step_bbox]`"

    diameters: set[str] = set()
    cyl_matches = list(STEP_CYL_SURF_RE.finditer(text))
    radius_matches = cyl_matches if cyl_matches else list(STEP_CIRCLE_RADIUS_RE.finditer(text))
    for cm in radius_matches:
        try:
            r_mm = float(cm.group(1)) * unit_scale
            if 0.25 <= r_mm <= 50.0:
                diameters.add(f"Ø{r_mm * 2.0:.2f}mm")
        except ValueError:
            continue
    bores = ", ".join(sorted(diameters)[:6]) if diameters else "—"
    return bbox, bores


def _parse_stl_metrics(stl_file: Path) -> str:
    """Extract bounding box (X x Y x Z mm) from binary or ASCII STL."""
    raw = stl_file.read_bytes()
    xs: list[float] = []
    ys: list[float] = []
    zs: list[float] = []
    if len(raw) >= 84 and not raw[:5].lower().startswith(b"solid"):
        tri_count = struct.unpack("<I", raw[80:84])[0]
        expected_len = 84 + tri_count * 50
        if len(raw) >= expected_len and tri_count > 0:
            offset = 84
            for _ in range(min(tri_count, 50000)):
                vals = struct.unpack("<12fH", raw[offset : offset + 50])
                xs.extend((vals[3], vals[6], vals[9]))
                ys.extend((vals[4], vals[7], vals[10]))
                zs.extend((vals[5], vals[8], vals[11]))
                offset += 50
    if not xs:
        text = raw.decode("utf-8", errors="ignore")
        for m in re.finditer(r"vertex\s+([-+0-9.eE]+)\s+([-+0-9.eE]+)\s+([-+0-9.eE]+)", text):
            xs.append(float(m.group(1)))
            ys.append(float(m.group(2)))
            zs.append(float(m.group(3)))
    if xs and ys and zs:
        return f"`{max(xs) - min(xs):.2f} x {max(ys) - min(ys):.2f} x {max(zs) - min(zs):.2f} mm`"
    return "`[TBD: stl_bbox]`"


def sync_hardware_telemetry(
    memory_root: Path,
    project_name: str,
    repo_override: Path | None = None,
) -> dict[str, Any]:
    """
    Single-Responsibility Hardware Telemetry Synchronizer (`--sync-hardware`).
    Scans CAD (`.step`/`.stp`/`.stl`/`.3mf`) and hardware config (`.cfg`/`.kicad_pcb`) files
    and updates `<Project>_Hardware.md` without touching software telemetry tables.
    """
    memory_root = memory_root.resolve()
    hub_path, repo_dir, fm = _resolve_project_repo(memory_root, project_name, repo_override)
    proj_dir = hub_path.parent
    hw_path = proj_dir / f"{project_name}_Hardware.md"
    inspect_hw_script = HOMUNCULUS_ROOT / "skills" / "subagent-orchestrator" / "scripts" / "inspect_hardware_ecosystem.py"
    if (
        hw_path.is_file()
        and inspect_hw_script.is_file()
        and "# 📐 Hardware & CAD Telemetry Manifest:" in hw_path.read_text(encoding="utf-8", errors="ignore")
    ):
        cmd = [
            sys.executable,
            str(inspect_hw_script),
            "--memory-root",
            str(memory_root),
            "--project",
            project_name,
            "--repo",
            str(repo_dir),
            "--sync-manifest",
        ]
        proc = subprocess.run(cmd, capture_output=True, text=True, check=False)
        if proc.returncode == 0:
            hw_fm = parse_stdlib_frontmatter(hw_path.read_text(encoding="utf-8", errors="ignore"))[0]
            cad_c = int(hw_fm.get("step_count", 0) or 0) + int(hw_fm.get("stl_count", 0) or 0)
            cfg_c = int(hw_fm.get("firmware_count", 0) or 0)
            return {
                "status": "PASS",
                "telemetry_domain": "hardware",
                "project": project_name,
                "hardware_note": str(hw_path),
                "cad_files_indexed": cad_c,
                "cfg_files_indexed": cfg_c,
                "inventory_sha256": str(hw_fm.get("inventory_sha256", "")),
            }

    if not hw_path.is_file():
        ctx = {
            "PROJECT": project_name,
            "ENTITY": str(fm.get("entity", "Default_Entity")),
            "COMPARTMENT": str(fm.get("compartment", "private")),
            "LOCAL_PATH": str(fm.get("local_path", repo_dir.as_posix())),
            "INVENTORY_SHA256": "INIT",
            "DATE": today_iso(),
        }
        hw_path.write_text(render_template("Project_Hardware.md", ctx, memory_root), encoding="utf-8")

    cad_rows: list[str] = [
        "| File Path | Format | Bounding Box (`X x Y x Z mm`) | Cylindrical Bore / Feature Summary | SHA-256 Prefix |",
        "| :--- | :--- | :--- | :--- | :--- |",
    ]
    cfg_rows: list[str] = [
        "| Config / Schematic File | Section / Component | Parameter / Pin | Verified Value | Line Anchor |",
        "| :--- | :--- | :--- | :--- | :--- |",
    ]
    hash_inputs: list[str] = []
    cad_count = 0
    cfg_count = 0

    for root, dirs, files in os.walk(repo_dir):
        dirs[:] = sorted(d for d in dirs if d not in IGNORED_TREE_DIRS and d != "Quarantine")
        for fname in sorted(files):
            fpath = Path(root) / fname
            rel_path = fpath.relative_to(repo_dir).as_posix()
            ext = fpath.suffix.lower()
            if ext in (".step", ".stp", ".stl", ".3mf"):
                cad_count += 1
                sha_prefix = hashlib.sha256(fpath.read_bytes()).hexdigest()[:10]
                hash_inputs.append(f"{rel_path}:{sha_prefix}")
                if ext in (".step", ".stp"):
                    bbox, bores = _parse_step_metrics(fpath)
                elif ext == ".stl":
                    bbox, bores = _parse_stl_metrics(fpath), "—"
                else:
                    bbox, bores = "`[3MF Archive]`", "—"
                cad_rows.append(f"| `{rel_path}` | `{ext.lstrip('.').upper()}` | {bbox} | {bores} | `{sha_prefix}` |")
            elif ext == ".cfg":
                cfg_count += 1
                sha_prefix = hashlib.sha256(fpath.read_bytes()).hexdigest()[:10]
                hash_inputs.append(f"{rel_path}:{sha_prefix}")
                current_sec = "global"
                for lineno, line in enumerate(fpath.read_text(encoding="utf-8", errors="ignore").splitlines(), start=1):
                    sec_m = CFG_SECTION_RE.match(line)
                    if sec_m:
                        current_sec = sec_m.group(1).strip()
                        continue
                    kv_m = CFG_KV_RE.match(line)
                    if kv_m and not line.lstrip().startswith("#"):
                        k, v = kv_m.group(1), kv_m.group(2)
                        if any(tok in k.lower() for tok in ("pin", "temp", "distance", "current", "microsteps", " nozzle", "diameter")):
                            cfg_rows.append(
                                f"| `{rel_path}` | `[{current_sec}]` | `{k}` | `{v}` | `{rel_path}#L{lineno}-L{lineno}` |"
                            )

    if cad_count == 0:
        cad_rows.append("| *(No CAD files found in repository)* | — | — | — | — |")
    if len(cfg_rows) == 2:
        cfg_rows.append("| *(No hardware config parameters found in repository)* | — | — | — | — |")

    inv_sha = hashlib.sha256("\n".join(hash_inputs).encode("utf-8")).hexdigest()[:12]
    hw_text = hw_path.read_text(encoding="utf-8")
    hw_text = replace_marker_block(hw_text, "AUTO-HARDWARE-CAD", "\n".join(cad_rows))
    hw_text = replace_marker_block(hw_text, "AUTO-HARDWARE-CFG", "\n".join(cfg_rows))
    hw_text = update_frontmatter_fields(hw_text, {"inventory_sha256": inv_sha, "last_synced": today_iso()})
    hw_path.write_text(hw_text, encoding="utf-8")

    return {
        "status": "PASS",
        "telemetry_domain": "hardware",
        "project": project_name,
        "hardware_note": str(hw_path),
        "cad_files_indexed": cad_count,
        "cfg_files_indexed": cfg_count,
        "inventory_sha256": inv_sha,
    }


# ============================================================================
# Function 2 of 2: Dedicated Software Telemetry (`sync_software_telemetry`)
# ============================================================================
def _inspect_python_module(py_file: Path) -> tuple[str, int]:
    """Extract CLI flags (`add_argument`) and top-level public functions/classes with `#Lstart-Lend` anchors via Unified AST Kernel."""
    info = homunculus_paths.inspect_python_ast_and_map(py_file)
    line_count = int(info.get("line_count", 0))
    cli_flags: list[str] = list(info.get("cli_flags", []))
    pub_syms = [s for s in info.get("symbols", []) if s.get("is_public")]

    # Prioritize classes and primary entrypoints alongside initial public helpers (up to 12 symbols)
    if len(pub_syms) > 12:
        head_syms = pub_syms[:5]
        head_names = {s["name"] for s in head_syms}
        tail_candidates = [
            s
            for s in pub_syms[5:]
            if s["name"] not in head_names
            and (
                s["kind"] == "class"
                or s["name"] == "main"
                or s["name"].startswith(("audit_", "verify_", "render_", "sync_", "inspect_", "build_", "resolve_", "ensure_"))
            )
        ]
        selected_syms = head_syms + tail_candidates[:7]
    else:
        selected_syms = pub_syms

    formatted_syms = [
        f"`{s['name']}()` (`#L{s['start_line']}-L{s['end_line']}`)" for s in selected_syms
    ]
    summary_parts: list[str] = []
    if cli_flags:
        summary_parts.append("Flags: `" + "`, `".join(cli_flags[:8]) + "`")
    if formatted_syms:
        summary_parts.append("Symbols: " + ", ".join(formatted_syms))
    return (" — ".join(summary_parts) if summary_parts else "Module"), line_count


def sync_software_telemetry(
    memory_root: Path,
    project_name: str,
    repo_override: Path | None = None,
) -> dict[str, Any]:
    """
    Single-Responsibility Software Telemetry Synchronizer (`--sync-software`).
    Scans runtime entrypoints (`.py`, `.sh`, `.ps1`, `.ts`, `.js`, `.rs`, `.go`) and
    configuration schemas (`.json`, `.toml`) and updates `<Project>_Software.md`
    without touching hardware CAD/pinout tables.
    """
    memory_root = memory_root.resolve()
    hub_path, repo_dir, fm = _resolve_project_repo(memory_root, project_name, repo_override)
    proj_dir = hub_path.parent
    sw_path = proj_dir / f"{project_name}_Software.md"
    if not sw_path.is_file():
        ctx = {
            "PROJECT": project_name,
            "ENTITY": str(fm.get("entity", "Default_Entity")),
            "COMPARTMENT": str(fm.get("compartment", "private")),
            "LOCAL_PATH": str(fm.get("local_path", repo_dir.as_posix())),
            "INVENTORY_SHA256": "INIT",
            "DATE": today_iso(),
        }
        sw_path.write_text(render_template("Project_Software.md", ctx, memory_root), encoding="utf-8")

    mod_rows: list[str] = [
        "| Script / Module Path | Language / Runtime | CLI Flags / Public Symbols | Line Count | SHA-256 Prefix |",
        "| :--- | :--- | :--- | :--- | :--- |",
    ]
    schema_rows: list[str] = [
        "| Schema / Config File | Format | Top-Level Keys / Contract Version | SHA-256 Prefix |",
        "| :--- | :--- | :--- | :--- |",
    ]
    hash_inputs: list[str] = []
    mod_count = 0
    schema_count = 0

    code_exts = {
        ".py": "Python 3.10+",
        ".sh": "POSIX Bash",
        ".ps1": "PowerShell",
        ".ts": "TypeScript",
        ".js": "JavaScript",
        ".rs": "Rust",
        ".go": "Go",
    }

    for root, dirs, files in os.walk(repo_dir):
        dirs[:] = sorted(d for d in dirs if d not in IGNORED_TREE_DIRS and d != "Quarantine")
        for fname in sorted(files):
            fpath = Path(root) / fname
            rel_path = fpath.relative_to(repo_dir).as_posix()
            ext = fpath.suffix.lower()
            if ext in code_exts:
                mod_count += 1
                if ext == ".py" and os.access(fpath, os.W_OK):
                    homunculus_paths.sync_script_navigation_map(fpath, write=True)
                sha_prefix = hashlib.sha256(fpath.read_bytes()).hexdigest()[:10]
                hash_inputs.append(f"{rel_path}:{sha_prefix}")
                if ext == ".py":
                    summary, lines = _inspect_python_module(fpath)
                else:
                    lines = len(fpath.read_text(encoding="utf-8", errors="ignore").splitlines())
                    summary = "Executable Script / Source"
                mod_rows.append(f"| `{rel_path}` | `{code_exts[ext]}` | {summary} | `{lines}` | `{sha_prefix}` |")
            elif ext == ".json" and not fname.startswith("."):
                schema_count += 1
                raw_bytes = fpath.read_bytes()
                sha_prefix = hashlib.sha256(raw_bytes).hexdigest()[:10]
                hash_inputs.append(f"{rel_path}:{sha_prefix}")
                try:
                    data = json.loads(raw_bytes.decode("utf-8", errors="ignore"))
                    if isinstance(data, dict):
                        keys = ", ".join(f"`{k}`" for k in list(data.keys())[:6]) or "`{}` (empty object)"
                    else:
                        keys = f"`{type(data).__name__}`"
                except Exception:
                    keys = "JSON payload"
                schema_rows.append(f"| `{rel_path}` | `JSON` | {keys} | `{sha_prefix}` |")

    if mod_count == 0:
        mod_rows.append("| *(No software modules found in repository)* | — | — | — | — |")
    if schema_count == 0:
        schema_rows.append("| *(No JSON/config schemas found in repository)* | — | — | — |")

    inv_sha = hashlib.sha256("\n".join(hash_inputs).encode("utf-8")).hexdigest()[:12]
    sw_text = sw_path.read_text(encoding="utf-8")
    sw_text = replace_marker_block(sw_text, "AUTO-SOFTWARE-MODULES", "\n".join(mod_rows))
    sw_text = replace_marker_block(sw_text, "AUTO-SOFTWARE-SCHEMAS", "\n".join(schema_rows))
    sw_text = update_frontmatter_fields(sw_text, {"inventory_sha256": inv_sha, "last_synced": today_iso()})
    sw_path.write_text(sw_text, encoding="utf-8")

    return {
        "status": "PASS",
        "telemetry_domain": "software",
        "project": project_name,
        "software_note": str(sw_path),
        "modules_indexed": mod_count,
        "schemas_indexed": schema_count,
        "inventory_sha256": inv_sha,
    }


def sync_project_tree(memory_root: Path, project_name: str, repo_override: Path | None = None) -> dict[str, Any]:
    """Refresh the `AUTO-TREE` block and `repo_head_sha` inside `Projects/<Project>/<Project>.md` (write-if-changed)."""
    hub_path, repo_dir, _fm = _resolve_project_repo(memory_root, project_name, repo_override)
    tree_block, tree_hash = build_repo_auto_tree(repo_dir)
    head_sha = get_git_head_sha(repo_dir)
    orig_text = hub_path.read_text(encoding="utf-8")
    cur_tree_block = extract_marker_block(orig_text, "AUTO-TREE")
    cur_head = str(_fm.get("repo_head_sha", ""))
    cur_hash = str(_fm.get("tree_hash", ""))
    updated = False
    if cur_tree_block != tree_block.strip() or cur_head != head_sha or cur_hash != tree_hash:
        text = replace_marker_block(orig_text, "AUTO-TREE", tree_block)
        text = update_frontmatter_fields(
            text,
            {"repo_head_sha": head_sha, "tree_hash": tree_hash, "last_synced": today_iso()},
        )
        hub_path.write_text(text, encoding="utf-8")
        updated = True
    dir_res = sync_directory_trees(memory_root)
    return {
        "status": "PASS",
        "project": hub_path.stem,
        "updated": updated,
        "repo_head_sha": head_sha,
        "tree_hash": tree_hash,
        "directory_files_written": dir_res.get("written_files", []),
    }


def sync_all_project_trees(memory_root: Path) -> dict[str, Any]:
    """
    Batch All-Project `AUTO-TREE` Synchronizer (`--sync-trees` / `--sync-tree` without `--project`):
    Iterates over all indexed `Projects/<P>/<P>.md` dossiers, skips any project whose `local_path` repository
    is currently unmounted/missing (preserving its existing `AUTO-TREE`), and updates only dossiers whose
    `AUTO-TREE`, `repo_head_sha`, or `tree_hash` actually changed.
    """
    memory_root = memory_root.resolve()
    projects_dir = memory_root / "Projects"
    if not projects_dir.is_dir():
        return {
            "status": "PASS",
            "projects_checked": 0,
            "updated_projects": [],
            "unchanged_projects": [],
            "skipped_missing_repos": [],
        }

    updated_projects: list[str] = []
    unchanged_projects: list[str] = []
    skipped_missing: list[str] = []
    hub_files = sorted(hub for hub in projects_dir.glob("*/*.md") if hub.stem == hub.parent.name)

    for hub in hub_files:
        proj = hub.stem
        orig_text = hub.read_text(encoding="utf-8")
        fm, _ = parse_stdlib_frontmatter(orig_text)
        local_path_str = str(fm.get("local_path", "")).strip().replace("\\", "/")
        if not local_path_str:
            skipped_missing.append(proj)
            continue
        repo_cand = Path(local_path_str)
        if not repo_cand.is_absolute():
            repo_cand = (memory_root / repo_cand).resolve()
        if not repo_cand.is_dir():
            skipped_missing.append(proj)
            continue

        tree_block, tree_hash = build_repo_auto_tree(repo_cand)
        head_sha = get_git_head_sha(repo_cand)
        cur_tree_block = extract_marker_block(orig_text, "AUTO-TREE")
        cur_head = str(fm.get("repo_head_sha", ""))
        cur_hash = str(fm.get("tree_hash", ""))

        if cur_tree_block == tree_block.strip() and cur_head == head_sha and cur_hash == tree_hash:
            unchanged_projects.append(proj)
            continue

        new_text = replace_marker_block(orig_text, "AUTO-TREE", tree_block)
        new_text = update_frontmatter_fields(
            new_text,
            {"repo_head_sha": head_sha, "tree_hash": tree_hash, "last_synced": today_iso()},
        )
        hub.write_text(new_text, encoding="utf-8")
        updated_projects.append(proj)

    sync_directory_trees(memory_root)
    return {
        "status": "PASS",
        "projects_checked": len(hub_files),
        "updated_projects": updated_projects,
        "unchanged_projects": unchanged_projects,
        "skipped_missing_repos": skipped_missing,
    }


def check_project_staleness(memory_root: Path, project_name: str, repo_override: Path | None = None) -> dict[str, Any]:
    """Sub-10ms single-project staleness check comparing recorded `repo_head_sha` against live `git HEAD`."""
    hub_path, repo_dir, fm = _resolve_project_repo(memory_root, project_name, repo_override)
    recorded_sha = str(fm.get("repo_head_sha", "UNTRACKED"))
    live_sha = get_git_head_sha(repo_dir)
    is_stale = recorded_sha != live_sha and live_sha != "UNTRACKED"
    return {
        "status": "STALE" if is_stale else "FRESH",
        "project": project_name,
        "hub_path": str(hub_path),
        "recorded_head_sha": recorded_sha,
        "live_head_sha": live_sha,
        "is_stale": is_stale,
    }


def save_session_handoff(
    memory_root: Path,
    project_name: str,
    repo_override: Path | None = None,
    stopped_at: str = "",
    receipt: str = "",
    blockers: str = "None",
    next_steps: str = "",
    discussion: str = "",
    handoff_file: Path | None = None,
) -> dict[str, Any]:
    """
    End-of-Session Handoff Writer (`--save-handoff`):
    Captures live `checkpoint_head_sha`, `checkpoint_tree_hash`, and `checkpoint_worktree`
    and overwrites `<!-- SESSION-HANDOFF:START/END -->` in `<Project>.md` in place (`O(1)` size;
    supports rich 500–800+ word stopping context and Project State Ledger snapshots without
    growing the file chronologically across multi-week projects).
    """
    hub_path, repo_dir, fm = _resolve_project_repo(memory_root, project_name, repo_override)
    live_sha = get_git_head_sha(repo_dir)
    _tree_block, live_tree_hash = build_repo_auto_tree(repo_dir)
    worktree_state, _dirty_files = get_git_worktree_state(repo_dir)
    timestamp = today_iso()
    receipt_val = receipt.strip() or "[TBD: receipt_or_test_id]"

    header_lines = [
        f"- **Last Session Timestamp**: `{timestamp}`",
        f"- **Checkpoint Provenance**: `HEAD SHA: {live_sha}` | `Tree Hash: {live_tree_hash}` | `Worktree: {worktree_state}` | `Last Verification: {receipt_val}`",
    ]

    if handoff_file is not None and handoff_file.is_file():
        custom_body = _sanitize_handoff_checkboxes(handoff_file.read_text(encoding="utf-8").strip())
        payload = "\n".join(header_lines) + "\n" + custom_body
    else:
        stopped_text = _sanitize_handoff_checkboxes(
            stopped_at.strip() or "[TBD: concise_or_multi_paragraph_summary_of_completed_milestone]"
        )
        blocker_text = _sanitize_handoff_checkboxes(blockers.strip() or "None")
        next_raw = next_steps.strip() or "1. [TBD: first_concrete_action_to_resume]"
        next_items = [item.strip() for item in next_raw.split("|") if item.strip()] if "|" in next_raw else [
            ln.strip() for ln in next_raw.splitlines() if ln.strip()
        ]
        formatted_next: list[str] = []
        for idx, item in enumerate(next_items, start=1):
            clean_item = re.sub(r"^\d+\.\s*", "", _sanitize_handoff_checkboxes(item))
            formatted_next.append(f"  {idx}. {clean_item}")

        body_lines = [
            "- **Where We Stopped (Verified State & Context)**:",
        ]
        for ln in stopped_text.splitlines():
            body_lines.append(f"  {ln}" if not ln.startswith("  ") else ln)
        body_lines.append(f"- **Active Project State Ledger & Blockers**: {blocker_text}")
        body_lines.append("- **Next Session Kickstart & Discussion Points**:")
        body_lines.extend(formatted_next)
        if discussion.strip():
            disc_clean = _sanitize_handoff_checkboxes(discussion.strip())
            body_lines.append(f"- **Open Discussion / Alignment Questions**: {disc_clean}")
        payload = "\n".join(header_lines + body_lines)

    word_count = len(payload.split())
    text = hub_path.read_text(encoding="utf-8")
    if "<!-- SESSION-HANDOFF:START -->" not in text:
        section_header = (
            "## 3. Session Handoff & Multi-Session Kickstart (`SESSION-HANDOFF`)\n\n"
            "<!-- SESSION-HANDOFF:START -->\n<!-- SESSION-HANDOFF:END -->\n\n---\n\n"
        )
        if "## 3. " in text:
            text = text.replace("## 3. ", section_header + "## 4. ", 1)
        else:
            text = text.rstrip() + "\n\n" + section_header

    text = replace_marker_block(text, "SESSION-HANDOFF", payload)
    text = update_frontmatter_fields(
        text,
        {
            "repo_head_sha": live_sha,
            "tree_hash": live_tree_hash,
            "checkpoint_head_sha": live_sha,
            "checkpoint_tree_hash": live_tree_hash,
            "checkpoint_worktree": worktree_state,
            "last_synced": timestamp,
        },
    )
    hub_path.write_text(text, encoding="utf-8")
    return {
        "status": "PASS",
        "project": project_name,
        "entity": str(fm.get("entity", "Default_Entity")),
        "hub_path": str(hub_path),
        "checkpoint_head_sha": live_sha,
        "checkpoint_tree_hash": live_tree_hash,
        "checkpoint_worktree": worktree_state,
        "handoff_word_count": word_count,
    }


def kickstart_project(
    memory_root: Path,
    project_name: str,
    repo_override: Path | None = None,
) -> dict[str, Any]:
    """
    Turn-1 Cold-Resume Verification Oracle (`--kickstart`):
    Reads `<Project>.md`, extracts `SESSION-HANDOFF`, and deterministically compares the saved
    `checkpoint_head_sha` and `checkpoint_tree_hash` against the live repository in `<10ms`
    so multi-day/multi-week breaks never resume on stale assumptions.
    """
    hub_path, repo_dir, fm = _resolve_project_repo(memory_root, project_name, repo_override)
    text = hub_path.read_text(encoding="utf-8")
    handoff_block = extract_marker_block(text, "SESSION-HANDOFF")

    saved_head = str(fm.get("checkpoint_head_sha", fm.get("repo_head_sha", "UNTRACKED")))
    saved_tree = str(fm.get("checkpoint_tree_hash", fm.get("tree_hash", "UNTRACKED")))
    saved_worktree = str(fm.get("checkpoint_worktree", "unknown"))

    live_head = get_git_head_sha(repo_dir)
    _tree_block, live_tree = build_repo_auto_tree(repo_dir)
    live_worktree, dirty_files = get_git_worktree_state(repo_dir)

    head_moved = (saved_head != live_head) and (live_head != "UNTRACKED")
    tree_changed = (saved_tree != live_tree) and (saved_tree not in ("UNTRACKED", "MISSING", ""))
    drift_detected = head_moved or tree_changed

    drift_reasons: list[str] = []
    if head_moved:
        drift_reasons.append(f"HEAD_MOVED ({saved_head} -> {live_head})")
    if tree_changed:
        drift_reasons.append(f"TREE_HASH_CHANGED ({saved_tree} -> {live_tree})")

    # Auto-heal AUTO-TREE and Directory/*.md on Turn-1 kickstart AFTER recording drift truth
    trees_refresh: dict[str, Any] = {"status": "SKIPPED"}
    if hasattr(homunculus_paths, "ensure_directory_fresh"):
        trees_refresh = homunculus_paths.ensure_directory_fresh(memory_root_override=memory_root)

    return {
        "status": "DRIFT_DETECTED" if drift_detected else "VERIFIED_MATCH",
        "project": project_name,
        "entity": str(fm.get("entity", "Default_Entity")),
        "compartment": str(fm.get("compartment", "private")),
        "project_type": str(fm.get("project_type", "software")),
        "hub_path": str(hub_path),
        "repo_path": str(repo_dir),
        "checkpoint_head_sha": saved_head,
        "live_head_sha": live_head,
        "checkpoint_tree_hash": saved_tree,
        "live_tree_hash": live_tree,
        "checkpoint_worktree": saved_worktree,
        "live_worktree": live_worktree,
        "dirty_files": dirty_files[:20],
        "drift_detected": drift_detected,
        "drift_reasons": drift_reasons,
        "trees_auto_refreshed": trees_refresh.get("status", "SKIPPED"),
        "session_handoff": handoff_block or "(No SESSION-HANDOFF block recorded yet; run --save-handoff)",
    }


def create_project_template(memory_root: Path, project_name: str, template_name: str) -> dict[str, Any]:
    """Create a custom deliverable template inside `Projects/<Project>/Templates/<TemplateName>.md`."""
    proj_dir = memory_root / "Projects" / project_name
    hub_path = proj_dir / f"{project_name}.md"
    if not hub_path.is_file():
        raise FileNotFoundError(f"Project hub dossier not found: {hub_path}")
    fm, _ = parse_stdlib_frontmatter(hub_path.read_text(encoding="utf-8"))
    entity = str(fm.get("entity", "Default_Entity"))
    compartment = str(fm.get("compartment", "private"))

    safe_name = template_name if template_name.endswith(".md") else f"{template_name}.md"
    tmpl_dir = proj_dir / "Templates"
    tmpl_dir.mkdir(parents=True, exist_ok=True)
    tmpl_path = tmpl_dir / safe_name

    content = (
        "---\n"
        f'template_name: "{safe_name}"\n'
        f'project: "{project_name}"\n'
        f'entity: "{entity}"\n'
        f'compartment: "{compartment}"\n'
        f'created: "{today_iso()}"\n'
        "---\n\n"
        f"# {project_name} Deliverable Template — `{safe_name}` (`entity: {entity}`)\n\n"
        "> **Reusable Project Template**: Maintained inside `Projects/"
        f"{project_name}/Templates/{safe_name}`. Replace `[TBD: ...]` placeholders with verified primary source values.\n\n"
        "## 1. Deliverable Summary\n"
        "- **Target Deliverable**: `[TBD: deliverable_title]`\n"
        "- **Primary Source Anchor**: `[TBD: source_file#Lstart-Lend]`\n\n"
        "## 2. Verification Table\n\n"
        "| Item / Parameter | Verified Value | Unit | Source Anchor |\n"
        "| :--- | :--- | :--- | :--- |\n"
        "| `[TBD: parameter_name]` | `[TBD: value]` | `[TBD: unit]` | `[TBD: path#L1-L1]` |\n"
    )
    tmpl_path.write_text(content, encoding="utf-8")
    return {
        "status": "PASS",
        "project": project_name,
        "entity": entity,
        "template_path": str(tmpl_path),
    }


def sync_task_rollups(memory_root: Path) -> dict[str, Any]:
    """Recalculate checkbox completion rollups across all `Tasks/*_Tasks.md` files."""
    tasks_dir = memory_root / "Tasks"
    updated: list[str] = []
    if not tasks_dir.is_dir():
        return {"status": "PASS", "updated_task_files": []}

    for tfile in sorted(tasks_dir.glob("*.md")):
        text = tfile.read_text(encoding="utf-8")
        total = 0
        done = 0
        in_fence = False
        for line in text.splitlines():
            if line.strip().startswith("```"):
                in_fence = not in_fence
                continue
            if in_fence:
                continue
            m = CHECKBOX_LINE_RE.match(line)
            if m:
                total += 1
                if m.group(1).lower() == "x":
                    done += 1
        pct = (done / total * 100.0) if total > 0 else 0.0
        open_cnt = total - done
        summary = f"**Progress Summary**: `{done} / {total}` Tasks Complete (`{pct:.1f}%`) | Open: `{open_cnt}`"
        new_text = replace_marker_block(text, "AUTO-ROLLUP", summary)
        new_text = update_frontmatter_fields(new_text, {"last_synced": today_iso()})
        tfile.write_text(new_text, encoding="utf-8")
        updated.append(str(tfile))

    return {"status": "PASS", "updated_task_files": updated}


def query_open_tasks(memory_root: Path, umbrella: str = "all") -> dict[str, Any]:
    """
    Open Task & Domain Umbrella Reader (`--tasks` / `--recommend` + `--umbrella <Filter>`):
    Scans `Tasks/*.md` dynamically (zero hardcoded project/umbrella lists), skips fenced code blocks,
    and lists all open `- [ ]` tasks grouped by domain umbrella and section heading.
    """
    memory_root = memory_root.resolve()
    tasks_dir = memory_root / "Tasks"
    u_filter = (umbrella or "all").strip()
    u_low = u_filter.lower()
    if not tasks_dir.is_dir():
        return {
            "status": "FAIL",
            "umbrella_filter": u_filter,
            "total_open": 0,
            "umbrellas": [],
            "header": f"=== 🎯 Canonical Umbrella Open Task Queue (scope={u_filter}) ===",
            "warning": "No Tasks/*.md umbrella directory found yet.",
        }

    all_tfiles = sorted(p for p in tasks_dir.glob("*.md") if not p.name.startswith("."))
    if not all_tfiles:
        return {
            "status": "FAIL",
            "umbrella_filter": u_filter,
            "total_open": 0,
            "umbrellas": [],
            "header": f"=== 🎯 Canonical Umbrella Open Task Queue (scope={u_filter}) ===",
            "warning": "No Tasks/*.md umbrella files found yet.",
        }

    selected: list[tuple[Path, dict[str, Any], str]] = []
    for tfile in all_tfiles:
        text = tfile.read_text(encoding="utf-8", errors="ignore")
        fm, _ = parse_stdlib_frontmatter(text)
        entity_val = str(fm.get("entity", "")).strip()
        if u_low == "all":
            selected.append((tfile, fm, text))
        else:
            stem_low = tfile.stem.lower()
            ent_low = entity_val.lower()
            ent_safe_low = sanitize_entity_filename(entity_val).lower() if entity_val else ""
            if u_low in stem_low or (ent_low and u_low in ent_low) or (ent_safe_low and u_low in ent_safe_low):
                selected.append((tfile, fm, text))

    if not selected:
        return {
            "status": "FAIL",
            "umbrella_filter": u_filter,
            "total_open": 0,
            "umbrellas": [],
            "header": f"=== 🎯 Canonical Umbrella Open Task Queue (scope={u_filter}) ===",
            "warning": f"No Tasks/*.md umbrella matched filter '{u_filter}'.",
        }

    umbrellas_out: list[dict[str, Any]] = []
    total_open = 0
    for tfile, fm, text in selected:
        rel_path = tfile.relative_to(memory_root).as_posix()
        entity = str(fm.get("entity", "Default_Entity"))
        compartment = str(fm.get("compartment", "private"))
        cur_h = rel_path
        open_under_h: dict[str, list[str]] = {}
        order_h: list[str] = []
        in_fm = False
        in_fence = False

        for idx, line in enumerate(text.replace("\r\n", "\n").splitlines()):
            s = line.strip()
            if idx == 0 and s == "---":
                in_fm = True
                continue
            if in_fm:
                if s == "---":
                    in_fm = False
                continue
            if s.startswith("```"):
                in_fence = not in_fence
                continue
            if in_fence:
                continue
            if s.startswith("## ") or s.startswith("### "):
                raw_h = s.lstrip("#").strip()
                clean_h = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", raw_h)
                cur_h = f"{rel_path} :: {clean_h}"
                if cur_h not in open_under_h:
                    open_under_h[cur_h] = []
                    order_h.append(cur_h)
            else:
                m = CHECKBOX_LINE_RE.match(line)
                if m and m.group(1) == " ":
                    if cur_h not in open_under_h:
                        open_under_h[cur_h] = []
                        order_h.append(cur_h)
                    task_body = re.sub(r"^\s*-\s*\[\s\]\s+", "", line).strip()
                    open_under_h[cur_h].append(task_body)
                    total_open += 1

        sections_list = [
            {"heading": h, "open_tasks": open_under_h[h]}
            for h in order_h
            if open_under_h[h]
        ]
        umbrellas_out.append({
            "file": rel_path,
            "entity": entity,
            "compartment": compartment,
            "open_count": sum(len(sec["open_tasks"]) for sec in sections_list),
            "sections": sections_list,
        })

    return {
        "status": "PASS",
        "umbrella_filter": u_filter,
        "total_open": total_open,
        "umbrellas": umbrellas_out,
        "header": f"=== 🎯 Canonical Umbrella Open Task Queue (scope={u_filter} | open={total_open}) ===",
    }


TBD_TOKEN_RE = re.compile(r"\[(?:TBD(?:\s*:\s*[^\]]+)?|CONFLICT[^\]]*)\]", re.IGNORECASE)


def query_tbd_ledger(
    memory_root: Path,
    umbrella_filter: str = "all",
    project_filter: str | None = None,
) -> dict[str, Any]:
    """
    Workspace-Wide Open `[TBD]` / `[CONFLICT]` Ledger (`--tbd-ledger`):
    Scans all indexed `Projects/<P>/<P>.md` dossiers, extracts live `[TBD: ...]` and `[CONFLICT]`
    items from both `## ... Open [TBD] / [CONFLICT] Ledger` sections, `<!-- QUARANTINE-ZONE -->`
    blocks, and inline specification bullets (skipping fenced code blocks and boilerplate callouts),
    and computes exact live open `[TBD]` counts without relying on stale frontmatter integers.
    """
    memory_root = memory_root.resolve()
    projects_dir = memory_root / "Projects"
    u_filter = (umbrella_filter or "all").strip()
    u_low = u_filter.lower()
    p_low = project_filter.strip().lower() if project_filter else ""

    if not projects_dir.is_dir():
        return {
            "status": "FAIL",
            "umbrella_filter": u_filter,
            "projects_scanned": 0,
            "total_open_tbd": 0,
            "projects": [],
            "header": "=== 🔍 Ecosystem Provenance & Open [TBD] / [CONFLICT] Ledger ===",
            "warning": "No Projects/ directory found in memory_root.",
        }

    hub_files = sorted(
        hub for hub in projects_dir.glob("*/*.md") if hub.stem == hub.parent.name
    )
    if not hub_files:
        return {
            "status": "FAIL",
            "umbrella_filter": u_filter,
            "projects_scanned": 0,
            "total_open_tbd": 0,
            "projects": [],
            "header": "=== 🔍 Ecosystem Provenance & Open [TBD] / [CONFLICT] Ledger ===",
            "warning": "No indexed project hub dossiers found in Projects/<P>/<P>.md.",
        }

    projects_out: list[dict[str, Any]] = []
    total_open_tbd = 0

    for hub in hub_files:
        text = hub.read_text(encoding="utf-8", errors="ignore").replace("\r\n", "\n")
        fm, _ = parse_stdlib_frontmatter(text)
        proj_name = hub.stem
        entity = str(fm.get("entity", "Default_Entity")).strip()
        compartment = str(fm.get("compartment", "private")).strip()
        worktree = str(fm.get("checkpoint_worktree", fm.get("status", "unknown"))).strip()
        head_sha = str(fm.get("repo_head_sha", "UNTRACKED")).strip()

        if p_low and p_low not in proj_name.lower():
            continue
        if u_low != "all":
            ent_low = entity.lower()
            ent_safe_low = sanitize_entity_filename(entity).lower()
            if u_low not in ent_low and u_low not in ent_safe_low and u_low not in proj_name.lower():
                continue

        rel_hub = hub.relative_to(memory_root).as_posix()
        sections = _extract_markdown_sections(text)

        # Collect lines from dedicated Provenance / Open [TBD] / Quarantine sections + inline [TBD] bullets elsewhere
        ledger_lines: list[str] = []
        seen_lines: set[str] = set()

        def _collect_block_lines(raw_block: str, require_tbd_token: bool) -> None:
            in_fence = False
            for ln in raw_block.splitlines():
                s = ln.strip()
                if not s:
                    continue
                if s.startswith("```"):
                    in_fence = not in_fence
                    continue
                if in_fence:
                    continue
                if s.startswith("#") or s.startswith("<!--"):
                    continue
                # Skip admonition callouts / instructional blockquotes
                if s.startswith(">"):
                    continue
                if require_tbd_token:
                    if not TBD_TOKEN_RE.search(s):
                        continue
                    # Skip instructional prose explaining what [TBD] is
                    if "placeholder" in s.lower() and "replace `[tbd:" in s.lower():
                        continue
                if s not in seen_lines:
                    seen_lines.add(s)
                    ledger_lines.append(s)

        for lvl, raw_h, body in sections:
            if lvl == 2:
                h_low = raw_h.lower()
                if any(k in h_low for k in ("provenance", "open [tbd]", "[conflict] ledger", "quarantine zone")):
                    _collect_block_lines(body, require_tbd_token=False)
                elif "session handoff" not in h_low and "companion notes" not in h_low:
                    _collect_block_lines(body, require_tbd_token=True)

        quar_block = extract_marker_block(text, "QUARANTINE-ZONE")
        if quar_block:
            _collect_block_lines(quar_block, require_tbd_token=False)

        # Count explicit [TBD...] / [CONFLICT...] lines
        tbd_item_count = sum(1 for item in ledger_lines if TBD_TOKEN_RE.search(item))
        total_open_tbd += tbd_item_count

        projects_out.append({
            "project": proj_name,
            "entity": entity,
            "compartment": compartment,
            "hub_file": rel_hub,
            "repo_head_sha": head_sha,
            "worktree": worktree,
            "open_tbd_count": tbd_item_count,
            "items": ledger_lines,
        })

    if not projects_out:
        return {
            "status": "FAIL",
            "umbrella_filter": u_filter,
            "projects_scanned": 0,
            "total_open_tbd": 0,
            "projects": [],
            "header": "=== 🔍 Ecosystem Provenance & Open [TBD] / [CONFLICT] Ledger ===",
            "warning": f"No projects matched filter (umbrella={u_filter}, project={project_filter}).",
        }

    return {
        "status": "PASS",
        "umbrella_filter": u_filter,
        "projects_scanned": len(projects_out),
        "total_open_tbd": total_open_tbd,
        "projects": projects_out,
        "header": (
            f"=== 🔍 Ecosystem Provenance & Open [TBD] / [CONFLICT] Ledger "
            f"(projects={len(projects_out)} | open_tbd={total_open_tbd}) ==="
        ),
    }


def sync_root_project_index(memory_root: Path) -> None:
    """Refresh the `AUTO-PROJECT-INDEX` table inside `<memory_root>/README.md`."""
    readme_path = memory_root / "README.md"
    projects_dir = memory_root / "Projects"
    if not readme_path.is_file() or not projects_dir.is_dir():
        return

    rows = [
        "| Project | Entity | Compartment | Archetype | Hub Dossier | Domain Telemetry | Task Umbrella |",
        "| :--- | :--- | :--- | :--- | :--- | :--- | :--- |",
    ]
    for hub in sorted(projects_dir.glob("*/*.md")):
        if hub.stem != hub.parent.name:
            continue
        proj = hub.stem
        fm, _ = parse_stdlib_frontmatter(hub.read_text(encoding="utf-8"))
        ent = str(fm.get("entity", "Default_Entity"))
        comp = str(fm.get("compartment", "private"))
        ptype = str(fm.get("project_type", "software"))
        ent_safe = sanitize_entity_filename(ent)

        telem_links: list[str] = []
        if (hub.parent / f"{proj}_Hardware.md").is_file():
            telem_links.append(f"[`_Hardware.md`](Projects/{proj}/{proj}_Hardware.md)")
        if (hub.parent / f"{proj}_Software.md").is_file():
            telem_links.append(f"[`_Software.md`](Projects/{proj}/{proj}_Software.md)")
        telem_str = ", ".join(telem_links) if telem_links else "—"

        rows.append(
            f"| **{proj}** | `{ent}` | `{comp}` | `{ptype}` | "
            f"[`{proj}.md`](Projects/{proj}/{proj}.md) | {telem_str} | "
            f"[`{ent_safe}_Tasks.md`](Tasks/{ent_safe}_Tasks.md) |"
        )

    text = readme_path.read_text(encoding="utf-8")
    text = replace_marker_block(text, "AUTO-PROJECT-INDEX", "\n".join(rows))
    text = update_frontmatter_fields(text, {"last_synced": today_iso()})
    readme_path.write_text(text, encoding="utf-8")


def _strip_last_synced_line(text: str) -> str:
    """Mask `last_synced:` frontmatter lines so write-if-changed skips pure date-only churn."""
    return re.sub(r'^last_synced:\s*"[^"]*"\s*$', 'last_synced: "__KEEP__"', text, flags=re.MULTILINE)


def sync_directory_trees(memory_root: Path) -> dict[str, Any]:
    """
    Maintain `<memory_root>/Directory/` Turn-1 location lookup maps (`Directory_Index.md` +
    entity-isolated `<Entity_Safe>_Directory.md` box trees) using write-if-changed semantics so
    unchanged runs touch 0 disk bytes while resolving exact paths without `ls`/`find`/`os.listdir`.
    """
    memory_root = memory_root.resolve()
    dir_root = memory_root / "Directory"
    dir_root.mkdir(parents=True, exist_ok=True)
    projects_dir = memory_root / "Projects"
    today_str = today_iso()

    # Group indexed projects by owning entity
    entities_projects: dict[str, list[dict[str, Any]]] = {}
    if projects_dir.is_dir():
        for hub in sorted(projects_dir.glob("*/*.md")):
            if hub.stem != hub.parent.name:
                continue
            proj = hub.stem
            fm, _ = parse_stdlib_frontmatter(hub.read_text(encoding="utf-8", errors="ignore"))
            ent = str(fm.get("entity", "Default_Entity")).strip() or "Default_Entity"
            comp = str(fm.get("compartment", "private")).strip() or "private"
            ptype = str(fm.get("project_type", "software")).strip() or "software"
            local_p = str(fm.get("local_path", "")).strip().replace("\\", "/")
            head_sha = str(fm.get("repo_head_sha", "UNTRACKED")).strip() or "UNTRACKED"
            repo_dir: Path | None = None
            if local_p:
                cand = Path(local_p)
                if not cand.is_absolute():
                    cand = (memory_root / cand).resolve()
                if cand.is_dir():
                    repo_dir = cand
                    live_sha = get_git_head_sha(cand)
                    if live_sha != "UNTRACKED":
                        head_sha = live_sha
            entities_projects.setdefault(ent, []).append({
                "project": proj,
                "entity": ent,
                "compartment": comp,
                "project_type": ptype,
                "local_path": local_p or f"../Projects/{proj}",
                "repo_dir": repo_dir,
                "head_sha": head_sha,
            })

    written_files: list[str] = []
    index_path = dir_root / "Directory_Index.md"
    if not index_path.exists():
        index_path.write_text("# Memory & Workspace Directory Index\n", encoding="utf-8")

    expected_entity_files: set[str] = {"Directory_Index.md"}
    entity_rows: list[str] = [
        "| Entity Scope | Compartment | Projects Indexed | Entity Directory Map | Task Umbrella |",
        "| :--- | :--- | :---: | :--- | :--- |",
    ]
    comp_rank = {"cleanroom": 3, "public": 2, "private": 1}

    for ent in sorted(entities_projects.keys()):
        plist = entities_projects[ent]
        ent_safe = sanitize_entity_filename(ent)
        ent_fname = f"{ent_safe}_Directory.md"
        expected_entity_files.add(ent_fname)
        ent_path = dir_root / ent_fname
        if not ent_path.exists():
            ent_path.write_text(f"# {ent}\n", encoding="utf-8")
        strictest_comp = max((p["compartment"] for p in plist), key=lambda c: comp_rank.get(c, 1))
        proj_names = {p["project"] for p in plist}
        task_fname = f"{ent_safe}_Tasks.md"
        task_link = f"[`{task_fname}`](../Tasks/{task_fname})" if (memory_root / "Tasks" / task_fname).is_file() else "—"

        mem_tree, mem_hash = build_ascii_directory_tree(
            memory_root,
            max_depth=3,
            max_entries=180,
            allowed_projects=proj_names,
            allowed_task_files={task_fname},
            allowed_directory_files={"Directory_Index.md", ent_fname},
        )

        sec_lines = [
            "---",
            f'title: "{ent} — Memory & Repository Directory Tree"',
            f'entity: "{ent}"',
            f'compartment: "{strictest_comp}"',
            'type: "entity-directory"',
            f'tree_hash: "{mem_hash}"',
            f'last_synced: "{today_str}"',
            "---",
            "",
            f"# 🗂️ `{ent}` — Directory Lookup Map (`entity: {ent}`)",
            "",
            "> **Turn-1 Cold-Start Location Map (`pre-commit-gate` Stage X)**: Read this note on Turn 1 to resolve exact file paths across `<memory_root>/` and `"
            + ent
            + "` repositories without running `ls`, `find`, or `os.listdir` probes. Cross-entity repositories outside `"
            + ent
            + "` are strictly excluded (`CROSS_ENTITY_CONTAMINATION` firewall).",
            "",
            f"- **Directory Index**: [`Directory_Index.md`](Directory_Index.md) | **Task Umbrella**: {task_link}",
            "",
            "---",
            "",
            f"## 1. `{ent}` Memory Dossiers, Standards & Templates (`<memory_root>/`)",
            "",
            mem_tree,
            "",
            "---",
            "",
            f"## 2. `{ent}` Repository Directory Trees (`{len(plist)}` Indexed)",
            "",
        ]
        for p in plist:
            pname = p["project"]
            rdir = p["repo_dir"]
            if rdir is not None and rdir.is_dir():
                rtree, rhash = build_ascii_directory_tree(rdir, max_depth=3, max_entries=160)
            else:
                rtree = (
                    "```text\n"
                    "+------------------------------------------------------------+\n"
                    "            --- DIRECTORY STRUCTURE ---\n"
                    "+------------------------------------------------------------+\n\n"
                    "./\n"
                    f"└── [unmounted or external path: {p['local_path']}]\n"
                    "+------------------------------------------------------------+\n"
                    "```"
                )
                rhash = "UNMOUNTED"
            sec_lines.extend([
                f"### [`{pname}`](../Projects/{pname}/{pname}.md) (`{p['project_type']}` | `HEAD: {p['head_sha']}` | `Tree: {rhash}`)",
                f"- **Repository Location**: `{p['local_path']}`",
                "",
                rtree,
                "",
            ])

        rendered_ent = "\n".join(sec_lines).rstrip() + "\n"
        existing_ent = ent_path.read_text(encoding="utf-8", errors="ignore") if ent_path.is_file() else ""
        if _strip_last_synced_line(existing_ent) != _strip_last_synced_line(rendered_ent):
            ent_path.write_text(rendered_ent, encoding="utf-8")
            written_files.append(str(ent_path))
        idx_task_link = f"[`{task_fname}`](../Tasks/{task_fname})" if (memory_root / "Tasks" / task_fname).is_file() else "—"
        entity_rows.append(
            f"| `{ent}` | `{strictest_comp}` | `{len(plist)}` | [`{ent_fname}`]({ent_fname}) | {idx_task_link} |"
        )

    # Prune stale entity directory files if an entity no longer exists
    pruned_files: list[str] = []
    for existing_md in sorted(dir_root.glob("*_Directory.md")):
        if existing_md.name not in expected_entity_files:
            existing_md.unlink()
            pruned_files.append(str(existing_md))

    if len(entity_rows) == 2:
        entity_rows.append("| *(No projects onboarded yet — run `--init-project`)* | — | `0` | — | — |")

    shared_tree, shared_hash = build_ascii_directory_tree(
        memory_root,
        max_depth=3,
        max_entries=160,
        allowed_top_dirs={"Directory", "Standards_and_Specs", "Templates", "Diagrams"},
        allowed_directory_files={"Directory_Index.md"},
    )
    idx_lines = [
        "---",
        'title: "Memory & Workspace Directory Index"',
        'type: "directory-index"',
        f'tree_hash: "{shared_hash}"',
        f'last_synced: "{today_str}"',
        "---",
        "",
        "# 🗂️ Engineering Memory — Directory Lookup Hub (`Directory/`)",
        "",
        "> **Turn-1 Location Lookup (`Zero Shell Recon`)**: Maintained automatically by `sync_memory.py` (`--sync-trees` / `--sync-visuals` at `pre-commit-gate` Stage X). Agents read [`Directory_Index.md`](Directory_Index.md) or the active entity's `<Entity>_Directory.md` map on Turn 1 to locate standards, templates, dossiers, and repository files without `ls`, `find`, or `os.listdir` probes.",
        "",
        "- **Memory Hub**: [`README.md`](../README.md) | **Global Standards**: [`Standards_Index.md`](../Standards_and_Specs/Standards_Index.md)",
        "",
        "---",
        "",
        "## 1. Shared `<memory_root>/` Directory Structure",
        "",
        shared_tree,
        "",
        "---",
        "",
        "## 2. Entity-Isolated Directory Trees (`Multi-Customer Firewall`)",
        "",
        "> **Containment Rule**: Only open the `<Entity>_Directory.md` file matching the active task's `entity:` scope.",
        "",
        *entity_rows,
        "",
    ]
    rendered_idx = "\n".join(idx_lines)
    existing_idx = index_path.read_text(encoding="utf-8", errors="ignore") if index_path.is_file() else ""
    if _strip_last_synced_line(existing_idx) != _strip_last_synced_line(rendered_idx):
        index_path.write_text(rendered_idx, encoding="utf-8")
        written_files.insert(0, str(index_path))

    return {
        "status": "PASS",
        "directory_root": str(dir_root),
        "entities_indexed": len(entities_projects),
        "written_files": written_files,
        "pruned_files": pruned_files,
    }


def audit_memory(memory_root: Path) -> dict[str, Any]:
    """
    Deterministic Memory Containment, Structure & Link Auditor (`--audit`):
      1. `CROSS_ENTITY_CONTAMINATION`: Blocks any link or project reference inside `Projects/<ProjA>/`
         or `Tasks/<EntityA>_Tasks.md` that points to a project or task umbrella belonging to a
         different customer/entity (`EntityB != EntityA`, excluding `shared`).
      2. `CHECKBOX_IN_PROJECT_HUB`: Blocks `- [ ]` / `- [x]` checkboxes inside `Projects/<Project>/<Project>.md`
         (preserving Single-Writer Task Umbrellas in `Tasks/<Entity>_Tasks.md`).
      3. `MISSING_ENTITY_FRONTMATTER`: Ensures every project hub declares `entity`, `compartment`, and `project_type`.
      4. `BROKEN_MEMORY_LINK`: Ensures all relative POSIX Markdown links resolve on disk.
    """
    memory_root = memory_root.resolve()
    violations: list[dict[str, Any]] = []
    projects_dir = memory_root / "Projects"

    # Build map of project -> entity and task_file -> entity
    project_entity_map: dict[str, str] = {}
    if projects_dir.is_dir():
        for hub in sorted(projects_dir.glob("*/*.md")):
            if hub.stem != hub.parent.name:
                continue
            fm, _ = parse_stdlib_frontmatter(hub.read_text(encoding="utf-8"))
            entity = str(fm.get("entity", "")).strip()
            compartment = str(fm.get("compartment", "")).strip()
            project_type = str(fm.get("project_type", "")).strip()
            if not entity or not compartment or not project_type:
                violations.append({
                    "code": "MISSING_ENTITY_FRONTMATTER",
                    "file": str(hub),
                    "line": 1,
                    "detail": f"Project hub `{hub.name}` must declare `entity`, `compartment`, and `project_type` in frontmatter.",
                })
            project_entity_map[hub.stem] = entity or "UNSET"

    # Scan all Markdown files in memory_root
    md_files = sorted(memory_root.rglob("*.md"))
    for md_file in md_files:
        # Skip raw master templates in <memory_root>/Templates/ which contain {{PLACEHOLDERS}}
        if "Templates" in md_file.relative_to(memory_root).parts and md_file.parent == memory_root / "Templates":
            continue

        text = md_file.read_text(encoding="utf-8", errors="ignore")
        fm, _ = parse_stdlib_frontmatter(text)
        file_entity = str(fm.get("entity", "")).strip()

        rel_parts = md_file.relative_to(memory_root).parts
        owning_project: str | None = None
        if len(rel_parts) >= 2 and rel_parts[0] == "Projects":
            owning_project = rel_parts[1]
            if not file_entity:
                file_entity = project_entity_map.get(owning_project, "")

        is_project_hub = (
            owning_project is not None
            and md_file.parent == projects_dir / owning_project
            and md_file.stem == owning_project
        )

        in_fence = False
        for lineno, line in enumerate(text.splitlines(), start=1):
            if line.strip().startswith("```"):
                in_fence = not in_fence
                continue
            if in_fence:
                continue

            # 1. Check for illegal checkboxes inside Project Hub Dossiers
            if is_project_hub and CHECKBOX_LINE_RE.match(line):
                violations.append({
                    "code": "CHECKBOX_IN_PROJECT_HUB",
                    "file": str(md_file),
                    "line": lineno,
                    "detail": (
                        f"Checkbox found in `{md_file.name}#L{lineno}`. "
                        "All active task checkboxes must live in `Tasks/<Entity>_Tasks.md`."
                    ),
                })

            # 2. Check Markdown links for existence, forbidden WikiLinks & Cross-Entity Contamination (strip inline code spans first)
            line_no_code = re.sub(r"`[^`]*`", "", line)
            for wl_match in re.finditer(r"\[\[([^\]]+)\]\]", line_no_code):
                violations.append({
                    "code": "WIKILINK_SYNTAX_FORBIDDEN",
                    "file": str(md_file),
                    "line": lineno,
                    "detail": (
                        f"Obsidian-only WikiLink `[[{wl_match.group(1)}]]` found in `{md_file.name}#L{lineno}`. "
                        "Use universal relative POSIX Markdown links `[label](relative/path.md)`."
                    ),
                })
            for match in MD_LINK_RE.finditer(line_no_code):
                raw_target = match.group(1).strip()
                if not raw_target or raw_target.startswith(("http://", "https://", "mailto:", "#", "file://")):
                    continue
                clean_target = raw_target.split("#", 1)[0].strip()
                if not clean_target or "{{" in clean_target:
                    continue

                resolved_target = (md_file.parent / clean_target).resolve()
                if not resolved_target.exists():
                    violations.append({
                        "code": "BROKEN_MEMORY_LINK",
                        "file": str(md_file),
                        "line": lineno,
                        "detail": f"Broken relative link `{raw_target}` in `{md_file.name}#L{lineno}`.",
                    })
                    continue

                # Check if resolved_target crosses into another project or task umbrella with a different entity
                if file_entity and file_entity.lower() != "shared":
                    try:
                        target_rel = resolved_target.relative_to(memory_root).parts
                    except ValueError:
                        target_rel = ()
                    if len(target_rel) >= 2 and target_rel[0] == "Projects":
                        target_proj = target_rel[1]
                        target_entity = project_entity_map.get(target_proj, "")
                        if target_entity and target_entity.lower() != "shared" and target_entity != file_entity:
                            violations.append({
                                "code": "CROSS_ENTITY_CONTAMINATION",
                                "file": str(md_file),
                                "line": lineno,
                                "detail": (
                                    f"Cross-customer/entity link blocked: `{md_file.name}` (`entity: {file_entity}`) "
                                    f"links to `{raw_target}` owned by `entity: {target_entity}`."
                                ),
                            })
                    elif len(target_rel) >= 2 and target_rel[0] == "Tasks" and resolved_target.is_file():
                        t_fm, _ = parse_stdlib_frontmatter(resolved_target.read_text(encoding="utf-8", errors="ignore"))
                        t_ent = str(t_fm.get("entity", "")).strip()
                        if t_ent and t_ent.lower() != "shared" and t_ent != file_entity:
                            violations.append({
                                "code": "CROSS_ENTITY_CONTAMINATION",
                                "file": str(md_file),
                                "line": lineno,
                                "detail": (
                                    f"Cross-customer/entity task link blocked: `{md_file.name}` (`entity: {file_entity}`) "
                                    f"links to task umbrella `{resolved_target.name}` (`entity: {t_ent}`)."
                                ),
                            })
                    elif len(target_rel) >= 2 and target_rel[0] == "Directory" and resolved_target.is_file():
                        d_fm, _ = parse_stdlib_frontmatter(resolved_target.read_text(encoding="utf-8", errors="ignore"))
                        d_ent = str(d_fm.get("entity", "")).strip()
                        if d_ent and d_ent.lower() != "shared" and d_ent != file_entity:
                            violations.append({
                                "code": "CROSS_ENTITY_CONTAMINATION",
                                "file": str(md_file),
                                "line": lineno,
                                "detail": (
                                    f"Cross-customer/entity directory link blocked: `{md_file.name}` (`entity: {file_entity}`) "
                                    f"links to directory map `{resolved_target.name}` (`entity: {d_ent}`)."
                                ),
                            })

            # 3. Also check for unlinked cross-entity project name references inside project dossiers or entity directories
            if (owning_project or (len(rel_parts) >= 2 and rel_parts[0] == "Directory")) and file_entity and file_entity.lower() != "shared":
                for other_proj, other_entity in project_entity_map.items():
                    if other_proj == owning_project or not other_entity or other_entity == file_entity:
                        continue
                    if other_entity.lower() == "shared":
                        continue
                    if re.search(rf"\bProjects/{re.escape(other_proj)}\b", line):
                        violations.append({
                            "code": "CROSS_ENTITY_CONTAMINATION",
                            "file": str(md_file),
                            "line": lineno,
                            "detail": (
                                f"Cross-customer/entity path reference blocked: `{md_file.name}` (`entity: {file_entity}`) "
                                f"references `Projects/{other_proj}` (`entity: {other_entity}`)."
                            ),
                        })

    return {
        "status": "PASS" if not violations else "FAIL",
        "memory_root": str(memory_root),
        "projects_indexed": len(project_entity_map),
        "files_scanned": len(md_files),
        "violation_count": len(violations),
        "violations": violations,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Homunculus Dual-Mode Engineering Memory Manager & Multi-Customer Containment Auditor"
    )
    parser.add_argument(
        "--memory-root",
        "--vault",
        dest="memory_root",
        default=None,
        help="Path to the memory root directory (`./memory` for Headless or `./vault` for Obsidian). Alias: `--vault`.",
    )
    parser.add_argument(
        "--init-memory",
        "--init-vault",
        dest="init_memory",
        action="store_true",
        help="Initialize the Dual-Mode memory root structure. Alias: `--init-vault`.",
    )
    parser.add_argument(
        "--mode",
        choices=("headless", "obsidian"),
        default="headless",
        help="Memory operating mode when running `--init-memory` (default: headless).",
    )
    parser.add_argument(
        "--convert-mode",
        choices=("headless", "obsidian"),
        help="Convert an existing memory root between `headless` and `obsidian` modes.",
    )
    parser.add_argument(
        "--default-entity",
        default="Default_Entity",
        help="Default owning entity/organization name for `--init-memory`.",
    )
    parser.add_argument("--init-project", help="Onboard and scaffold a new project folder under `Projects/<Project>/`.")
    parser.add_argument(
        "--project",
        help="Target project name for read-only dossier/section queries (`--section`) or `--sync-hardware`, `--sync-software`, `--sync-tree`, `--check-stale`, `--save-handoff`, `--kickstart`.",
    )
    parser.add_argument(
        "--section",
        choices=SECTION_QUERY_CHOICES,
        default=None,
        help="Print a targeted section of `<Project>.md` (or companion `lessons`, `hardware`, `software` note) to stdout with inline task transclusion.",
    )
    parser.add_argument("--repo-path", help="Path to the target project's source repository.")
    parser.add_argument(
        "--type",
        choices=("hardware", "software", "hybrid"),
        default="software",
        help="Project archetype for `--init-project` (`hardware`, `software`, or `hybrid`).",
    )
    parser.add_argument("--entity", default="Default_Entity", help="Owning customer/entity identifier for `--init-project`.")
    parser.add_argument(
        "--compartment",
        choices=("private", "public", "cleanroom"),
        default="private",
        help="Data boundary compartment for `--init-project`.",
    )
    parser.add_argument(
        "--sync-hardware",
        action="store_true",
        help="Run `sync_hardware_telemetry()` to update `<Project>_Hardware.md`.",
    )
    parser.add_argument(
        "--sync-software",
        action="store_true",
        help="Run `sync_software_telemetry()` to update `<Project>_Software.md`.",
    )
    parser.add_argument(
        "--sync-tree",
        "--sync-trees",
        dest="sync_tree",
        action="store_true",
        help="Refresh `AUTO-TREE` and `repo_head_sha` in `<Project>.md` (or across all indexed projects when `--project` is omitted / `--sync-trees` is used).",
    )
    parser.add_argument(
        "--check-stale",
        action="store_true",
        help="Run fast (<10ms) single-project `git HEAD` staleness check against `<Project>.md`.",
    )
    parser.add_argument(
        "--save-handoff",
        action="store_true",
        help="Overwrite the bounded `SESSION-HANDOFF` kickstart block in `<Project>.md` with live git/tree provenance.",
    )
    parser.add_argument(
        "--stopped-at",
        default="",
        help="Summary or multi-paragraph context (up to 500–800+ words) of where development stopped for `--save-handoff`.",
    )
    parser.add_argument(
        "--receipt",
        default="",
        help="Last verification receipt ID (`VRF-...`, `SBX-...`, or test run summary) for `--save-handoff`.",
    )
    parser.add_argument(
        "--blockers",
        default="None",
        help="Active Project State Ledger blockers (`[OPEN-xx]`, `[SANDBOX-PENDING]`, or `None`) for `--save-handoff`.",
    )
    parser.add_argument(
        "--next-steps",
        default="",
        help="Pipe-separated (`|`) or newline-separated list of next kickstart steps for `--save-handoff`.",
    )
    parser.add_argument(
        "--discussion",
        default="",
        help="Open discussion or alignment points to surface immediately at the next session kickstart.",
    )
    parser.add_argument(
        "--handoff-file",
        help="Optional Markdown file containing a rich multi-paragraph (500–800+ word) handoff body for `--save-handoff`.",
    )
    parser.add_argument(
        "--kickstart",
        action="store_true",
        help="Run Turn-1 cold-resume verification comparing saved `SESSION-HANDOFF` provenance against the live repo.",
    )
    parser.add_argument(
        "--create-project-template",
        help="Create a reusable project deliverable template in `Projects/<Project>/Templates/<Name>.md`.",
    )
    parser.add_argument(
        "--tasks",
        "--recommend",
        dest="tasks",
        action="store_true",
        help="List all open `- [ ]` tasks across `Tasks/*.md` domain umbrellas (or filtered via `--umbrella`).",
    )
    parser.add_argument(
        "--umbrella",
        default=None,
        help="Optional domain/entity umbrella substring filter for `--tasks` or `--tbd-ledger` (e.g. `all`, `client_alpha`, `client_beta`).",
    )
    parser.add_argument(
        "--tbd-ledger",
        action="store_true",
        help="Scan all indexed `Projects/<P>/<P>.md` dossiers and print a consolidated open `[TBD]` / `[CONFLICT]` ledger.",
    )
    parser.add_argument("--sync-tasks", action="store_true", help="Refresh checkbox rollups across `Tasks/*_Tasks.md`.")
    parser.add_argument(
        "--sync-directory",
        action="store_true",
        help="Refresh `<memory_root>/Directory/` (`Directory_Index.md` + entity-isolated `<Entity>_Directory.md` box trees).",
    )
    parser.add_argument(
        "--sync-visuals",
        action="store_true",
        help="Refresh root `AUTO-PROJECT-INDEX`, `Directory/` lookup trees, task rollups, and (when `memory_mode: obsidian`) `.base` & `graph.json` views.",
    )
    parser.add_argument(
        "--export-canvas",
        action="store_true",
        help="Dynamically generate a JSON Canvas 1.0 project topology map (`Diagrams/Project_Ecosystem_Map.canvas`).",
    )
    parser.add_argument(
        "--canvas-out-dir",
        default=None,
        help="Optional output directory for `--export-canvas` (defaults to `<memory_root>/Diagrams/`).",
    )
    parser.add_argument(
        "--audit",
        "--check",
        dest="audit",
        action="store_true",
        help="Audit `<memory_root>` for `CROSS_ENTITY_CONTAMINATION`, broken links, and checkbox leaks. Alias: `--check`.",
    )
    parser.add_argument("--json", action="store_true", help="Emit JSON output.")
    args = parser.parse_args(argv)

    if args.memory_root:
        mem_root = Path(str(args.memory_root).replace("\\", "/")).expanduser().resolve()
    else:
        env_mem = os.environ.get("HOMUNCULUS_MEMORY_ROOT", "").strip()
        if env_mem:
            mem_root = Path(env_mem.replace("\\", "/")).expanduser().resolve()
        else:
            try:
                ws_cfg = homunculus_paths.resolve_workspace_config(Path.cwd())
                mem_root = Path(ws_cfg["memory_root"]).resolve()
            except Exception:
                mem_root = (Path.cwd() / "memory").resolve()
    repo_override = Path(str(args.repo_path).replace("\\", "/")).expanduser().resolve() if args.repo_path else None
    results: dict[str, Any] = {"memory_root": str(mem_root)}

    if args.init_memory:
        results["init_memory"] = init_memory_root(
            mem_root, mode=args.mode, default_entity=args.default_entity
        )

    if args.convert_mode:
        results["convert_mode"] = convert_memory_mode(mem_root, args.convert_mode)

    if args.init_project:
        results["init_project"] = init_project(
            mem_root,
            project_name=args.init_project,
            repo_path=repo_override,
            project_type=args.type,
            entity=args.entity,
            compartment=args.compartment,
        )

    target_proj = args.project or args.init_project
    if args.sync_tree:
        if target_proj:
            results["sync_tree"] = sync_project_tree(mem_root, target_proj, repo_override)
        else:
            results["sync_trees"] = sync_all_project_trees(mem_root)

    if args.sync_hardware:
        if not target_proj:
            print("[FAIL] --sync-hardware requires --project <Project>.", file=sys.stderr)
            return 2
        results["sync_hardware"] = sync_hardware_telemetry(mem_root, target_proj, repo_override)

    if args.sync_software:
        if not target_proj:
            print("[FAIL] --sync-software requires --project <Project>.", file=sys.stderr)
            return 2
        results["sync_software"] = sync_software_telemetry(mem_root, target_proj, repo_override)

    if args.check_stale:
        if not target_proj:
            print("[FAIL] --check-stale requires --project <Project>.", file=sys.stderr)
            return 2
        results["check_stale"] = check_project_staleness(mem_root, target_proj, repo_override)

    if args.save_handoff:
        if not target_proj:
            print("[FAIL] --save-handoff requires --project <Project>.", file=sys.stderr)
            return 2
        hfile = Path(args.handoff_file).expanduser().resolve() if args.handoff_file else None
        results["save_handoff"] = save_session_handoff(
            mem_root,
            target_proj,
            repo_override=repo_override,
            stopped_at=args.stopped_at,
            receipt=args.receipt,
            blockers=args.blockers,
            next_steps=args.next_steps,
            discussion=args.discussion,
            handoff_file=hfile,
        )

    if args.kickstart:
        if not target_proj:
            print("[FAIL] --kickstart requires --project <Project>.", file=sys.stderr)
            return 2
        results["kickstart"] = kickstart_project(mem_root, target_proj, repo_override)

    if args.create_project_template:
        if not target_proj:
            print("[FAIL] --create-project-template requires --project <Project>.", file=sys.stderr)
            return 2
        results["create_project_template"] = create_project_template(
            mem_root, target_proj, args.create_project_template
        )

    project_action_used = any((
        args.init_project,
        args.sync_tree,
        args.sync_hardware,
        args.sync_software,
        args.check_stale,
        args.save_handoff,
        args.kickstart,
        args.create_project_template,
        args.tbd_ledger,
    ))
    if args.section is not None or (args.project and not project_action_used):
        if not target_proj:
            print("[FAIL] --section requires --project <Project>.", file=sys.stderr)
            return 2
        if not args.audit and not args.check_stale and hasattr(homunculus_paths, "ensure_directory_fresh"):
            homunculus_paths.ensure_directory_fresh(memory_root_override=mem_root)
        sec_choice = args.section or "all"
        q_res = query_project_section(mem_root, target_proj, sec_choice, repo_override)
        results["query_section"] = q_res

    if args.sync_directory:
        results["sync_directory"] = sync_directory_trees(mem_root)

    if args.sync_tasks or args.sync_visuals:
        results["sync_tasks"] = sync_task_rollups(mem_root)
        sync_root_project_index(mem_root)
        if args.sync_visuals:
            results["sync_directory"] = sync_directory_trees(mem_root)
        if args.sync_visuals and _detect_memory_mode(mem_root) == "obsidian":
            c_dir = Path(str(args.canvas_out_dir).replace("\\", "/")).expanduser().resolve() if args.canvas_out_dir else None
            results["obsidian_visual_brain"] = sync_obsidian_visual_brain(
                mem_root, export_canvas=args.export_canvas, canvas_out_dir=c_dir
            )

    if (args.export_canvas or args.canvas_out_dir) and "obsidian_visual_brain" not in results:
        c_dir = Path(str(args.canvas_out_dir).replace("\\", "/")).expanduser().resolve() if args.canvas_out_dir else None
        results["obsidian_visual_brain"] = sync_obsidian_visual_brain(
            mem_root, export_canvas=True, canvas_out_dir=c_dir
        )

    if args.tasks or (args.umbrella is not None and not args.tbd_ledger):
        if not args.audit and not args.check_stale and hasattr(homunculus_paths, "ensure_directory_fresh"):
            homunculus_paths.ensure_directory_fresh(memory_root_override=mem_root)
        results["query_tasks"] = query_open_tasks(mem_root, args.umbrella or "all")

    if args.tbd_ledger:
        if not args.audit and not args.check_stale and hasattr(homunculus_paths, "ensure_directory_fresh"):
            homunculus_paths.ensure_directory_fresh(memory_root_override=mem_root)
        results["tbd_ledger"] = query_tbd_ledger(
            mem_root,
            umbrella_filter=args.umbrella or "all",
            project_filter=args.project,
        )

    exit_code = 0
    if "query_section" in results and results["query_section"].get("status") != "PASS":
        exit_code = 1
    if "query_tasks" in results and results["query_tasks"].get("status") != "PASS":
        exit_code = 1
    if "tbd_ledger" in results and results["tbd_ledger"].get("status") != "PASS":
        exit_code = 1
    if args.audit:
        audit_res = audit_memory(mem_root)
        results["audit"] = audit_res
        if audit_res["status"] != "PASS":
            exit_code = 1

    if args.json:
        print(json.dumps(results, indent=2))
    else:
        for key, val in results.items():
            if key == "memory_root":
                continue
            if key == "audit":
                status = val["status"]
                print(
                    f"[{status}] Memory Containment & Structure Audit | "
                    f"Projects: {val['projects_indexed']} | Files: {val['files_scanned']} | "
                    f"Violations: {val['violation_count']}"
                )
                for v in val["violations"]:
                    print(f"  [!] {v['code']} @ {v['file']}#L{v['line']}: {v['detail']}")
            elif key == "query_section" and isinstance(val, dict):
                print(val["header"])
                if val.get("content"):
                    print(val["content"])
            elif key == "query_tasks" and isinstance(val, dict):
                print(val["header"])
                if val.get("warning"):
                    print(f"  [WARN] {val['warning']}")
                for umb in val.get("umbrellas", []):
                    for sec in umb.get("sections", []):
                        print(f"\n[{sec['heading']}]")
                        for item in sec.get("open_tasks", []):
                            print(f"  - [ ] {item}")
            elif key == "tbd_ledger" and isinstance(val, dict):
                print(val["header"])
                if val.get("warning"):
                    print(f"  [WARN] {val['warning']}")
                for proj_entry in val.get("projects", []):
                    print(
                        f"\n• {proj_entry['hub_file']} "
                        f"(entity={proj_entry['entity']}, head={proj_entry['repo_head_sha']}, "
                        f"open_tbd_count={proj_entry['open_tbd_count']})"
                    )
                    for item in proj_entry.get("items", []):
                        print(f"  {item}")
            elif key == "kickstart" and isinstance(val, dict):
                print(
                    f"[KICKSTART: {val['status']}] Project: {val['project']} "
                    f"(entity: {val['entity']} | compartment: {val['compartment']})"
                )
                print(
                    f"  Checkpoint HEAD: {val['checkpoint_head_sha']} (Live: {val['live_head_sha']}) | "
                    f"Checkpoint Tree: {val['checkpoint_tree_hash']} (Live: {val['live_tree_hash']}) | "
                    f"Live Worktree: {val['live_worktree']}"
                )
                if val["drift_reasons"]:
                    print(f"  [!] REPO DRIFT DETECTED SINCE CHECKPOINT: {', '.join(val['drift_reasons'])}")
                print("--- SESSION-HANDOFF ---")
                print(val["session_handoff"])
                print("-----------------------")
            elif isinstance(val, dict):
                print(f"[{val.get('status', 'OK')}] {key}: {json.dumps(val)}")
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
