#!/usr/bin/env python3
"""Homunculus Cross-OS Dynamic Workspace, Memory-Mode & Runtime Capability Resolver.

Resolves Homunculus framework and target project paths generically across
Windows, macOS, and Linux.

Requires ONLY Python 3.10+ standard library (zero third-party pip packages) and operates
in both Zero-Install "Drop-In & Point" mode and Optional Installer mode.

=== DEVELOPER & AI NAVIGATION MAP ===
  Owning Module : Core Framework (`scripts/`)
  Callers       : All 12 core/skill Python scripts, `install.sh`, `install.ps1`, `post-worktree-sync.sh`, `test_foundation.py`, `test_project_memory.py`, `test_adapters.py`
  Callees       : Stdlib only; lazy-loads `sync_memory.py` inside `ensure_directory_fresh()`
  Contract      : `scripts/script_contracts.json` [`homunculus_paths.py`]
  CLI Flags     : --workspace, --homunculus-root, --memory-root, --init-config, --memory-mode, --memory-dir, --simulate-os, --check, --ensure-fresh, --map, --sync-maps, --lock-core, --unlock-core, --quiet, --json
  Symbol Index  (jump directly via read_file StartLine/EndLine):
    - def parse_frontmatter_full (#L93-L144)         | def strip_yaml_frontmatter (#L147-L150)
    - def decode_file_text (#L153-L174)              | def detect_os_tier (#L177-L210)
    - def resolve_homunculus_root (#L213-L240)       | def _find_git_root (#L243-L248)
    - def resolve_workspace_config (#L251-L337)      | def probe_runtime_capabilities (#L340-L368)
    - def write_workspace_config (#L371-L409)        | def _resolve_tree_stamp_cache_dir (#L430-L445)
    - def _resolve_memory_root_fast (#L448-L475)     | def _read_git_head_signature (#L478-L512)
    - def read_git_head_sha (#L515-L533)             | def inspect_python_ast_and_map (#L543-L666)
    - def _format_symbol_index_lines (#L669-L681)    | def load_script_contract (#L684-L698)
    - def record_preflight_receipt (#L701-L775)      | def sync_script_navigation_map (#L778-L835)
    - def _compute_structural_stamp (#L838-L899)     | def _load_sync_memory_module (#L902-L915)
    - def ensure_directory_fresh (#L918-L996)        | def set_core_lock_state (#L999-L1027)
    - def main (#L1030-L1240)
=== END NAVIGATION MAP ===
"""
from __future__ import annotations

import argparse
import ast
import codecs
import hashlib
import importlib.util
import json
import os
import platform
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

CONFIG_FILENAME = ".homunculus.json"
START_HERE_FILENAME = "HOMUNCULUS_START_HERE.md"
VALID_MEMORY_MODES = ("headless", "obsidian")
VALID_CLIENTS = ("all", "agents_md", "antigravity", "claude_code", "claude_cowork", "cursor")

# Shared Clean-Room SHA-256 lowercase digests (zero plaintext storage in source)
CLEANROOM_FORBIDDEN_SHA256: frozenset[str] = frozenset(
    {
        "006e859119a65852bcd4db4279a10462c3b4b910e940863f2a4a5598b11867c6",
        "67534844ed84422fd1175541de8159dd5f341089b93971b84ca3a7bc5abdbfd7",
        "fe5ef45dd1860bd3e49cf94307153e10cf45b9decea8f29ef54e9d6d5e212011",
        "81651bb716e09cc0724f2fd881c268098d83b9c3ec1d6697aedb0f3aefe5084d",
        "977aa0a5bc4be3b497fe31ff0db3185b2a502546a5d1e3eca50fbb7f1aa66baa",
        "7df90d0bcfee1d2484228c0ca2e0279471587536a6bd42642d890beff4efdfbc",
        "1e19681259d3cfe1e3ad46a7723e3e4535a9cac8ab5f96cac950b535f65b3c37",
        "4deef0f5764e4bc89f4ac6c6f3fe473892b3e287d2dad15dd0c895b3f13b6370",
        "802a5416dc59d7ac669bcf803e64b40b87187e475c7556cc4c4a45a37d79ff6a",
        "129e9cc0d21b429986663b4e6cf6ee934fb3b9fea8834052ea57aca5fd03c357",
        "bc696bc0c6719b23cd38d26010454e9ca9e6c744de6b3883cd9b39e2497617dc",
        "adcadeec55be7018c3335a39f019fbe62f2497f1e7cc0e3022236e7269fb6176",
        "8249d2c3468df10e22dbbcd6a3ddd4c6e9dd777783539e319b182bc21c61e682",
        "a855a33958c67c32a1169b03676b461a07c00c829352a487480967855fbb5d74",
        "95a185991305e4ea853efa8293e5b720d186c142e0ec4f41c5f31af8dad9bd23",
    }
)

# Shared allowed placeholder usernames in documentation examples
ALLOWED_PLACEHOLDER_USERS: frozenset[str] = frozenset(
    {
        "user",
        "username",
        "your_user",
        "your-user",
        "engineer",
        "developer",
        "example",
    }
)

# Shared hardcoded OS user-directory regexes across Linux, macOS, and Windows
RE_POSIX_HOME = re.compile(r"(?<![A-Za-z0-9_])/(?:home|Users)/([A-Za-z0-9._-]+)")
RE_WIN_USERS = re.compile(r"(?<![A-Za-z0-9_])[A-Za-z]:\\\\?Users\\\\?([A-Za-z0-9._-]+)", re.IGNORECASE)


def parse_frontmatter_full(
    text: str,
    *,
    coerce_bools: bool = False,
) -> tuple[dict[str, Any], str, int]:
    """Parse leading `--- ... ---` YAML frontmatter using 100% Python stdlib.

    Returns (fields_dict, body_text, body_start_line_1based). Supports quoted
    strings, folded/literal multiline scalars (`>-`, `>`, `|`, `|-`), and
    optional boolean coercion (`coerce_bools=True`).
    """
    norm = text.replace("\r\n", "\n")
    lines = norm.splitlines(keepends=True)
    if not lines or lines[0].strip() != "---":
        return {}, text, 1
    end_idx = 0
    fields: dict[str, Any] = {}
    current_key: str | None = None
    for idx in range(1, len(lines)):
        raw_line = lines[idx]
        stripped_nl = raw_line.rstrip("\n")
        if stripped_nl.strip() == "---":
            end_idx = idx
            break
        if stripped_nl.lstrip().startswith("#"):
            continue
        m = re.match(r"^([A-Za-z0-9_-]+):\s*(.*)$", stripped_nl)
        if m:
            current_key = m.group(1).strip()
            val = m.group(2).strip()
            if val in (">-", ">", "|", "|-"):
                fields[current_key] = ""
            else:
                if len(val) >= 2 and val[0] == val[-1] and val[0] in ('"', "'"):
                    val = val[1:-1]
                if coerce_bools and val.lower() == "true":
                    fields[current_key] = True
                elif coerce_bools and val.lower() == "false":
                    fields[current_key] = False
                else:
                    fields[current_key] = val
        elif current_key and (stripped_nl.startswith("  ") or stripped_nl.startswith("\t")):
            prev = str(fields.get(current_key, ""))
            fields[current_key] = (prev + " " + stripped_nl.strip()).strip()
        elif not stripped_nl.strip():
            continue
        else:
            current_key = None
    if end_idx == 0:
        return {}, text, 1
    body = "".join(lines[end_idx + 1 :])
    return fields, body, end_idx + 2


def strip_yaml_frontmatter(text: str) -> str:
    """Return Markdown body with leading YAML frontmatter stripped."""
    _fields, body, _line = parse_frontmatter_full(text)
    return body.strip()


def decode_file_text(raw_bytes: bytes) -> str:
    """Decode text handling UTF-8, UTF-16 (LE/BE), and UTF-32 (LE/BE) BOMs or NUL-interleaved bytes."""
    for bom, enc in (
        (codecs.BOM_UTF32_LE, "utf-32-le"),
        (codecs.BOM_UTF32_BE, "utf-32-be"),
        (codecs.BOM_UTF16_LE, "utf-16-le"),
        (codecs.BOM_UTF16_BE, "utf-16-be"),
        (codecs.BOM_UTF8, "utf-8-sig"),
    ):
        if raw_bytes.startswith(bom):
            return raw_bytes[len(bom) :].decode(enc, errors="replace")

    if b"\x00" in raw_bytes[:512]:
        for enc in ("utf-16-le", "utf-16-be", "utf-32-le", "utf-32-be"):
            try:
                decoded = raw_bytes.decode(enc)
                if any(ch.isprintable() for ch in decoded[:128]):
                    return decoded
            except UnicodeDecodeError:
                continue

    return raw_bytes.decode("utf-8", errors="replace")


def detect_os_tier(sys_platform: str | None = None) -> dict[str, Any]:
    """Classify host operating system across Windows, macOS, and Linux."""
    plat = (sys_platform or sys.platform).lower()
    if plat.startswith("linux"):
        return {
            "os_id": "linux",
            "os_label": "Linux",
            "priority_order": 1,
            "path_separator": "/",
            "shell_installer": "install.sh",
        }
    if plat == "darwin" or plat.startswith("darwin"):
        return {
            "os_id": "macos",
            "os_label": "macOS",
            "priority_order": 2,
            "path_separator": "/",
            "shell_installer": "install.sh",
        }
    if plat.startswith("win") or plat in ("msys", "cygwin"):
        return {
            "os_id": "windows",
            "os_label": "Windows",
            "priority_order": 3,
            "path_separator": "\\",
            "shell_installer": "install.ps1",
        }
    return {
        "os_id": "posix_other",
        "os_label": platform.system() or "POSIX",
        "priority_order": 4,
        "path_separator": os.sep,
        "shell_installer": "install.sh",
    }


def resolve_homunculus_root(explicit_root: str | Path | None = None) -> Path:
    """Resolve the Homunculus framework root without any hardcoded user/account paths."""
    if explicit_root:
        candidate = Path(explicit_root).expanduser().resolve()
        if candidate.is_dir():
            return candidate

    env_root = os.environ.get("HOMUNCULUS_ROOT", "").strip()
    if env_root:
        candidate = Path(env_root).expanduser().resolve()
        if candidate.is_dir():
            return candidate

    # Default: resolve relative to this script's location (Homunculus/scripts/homunculus_paths.py)
    script_parent = Path(__file__).resolve().parent
    if script_parent.name == "scripts" and (script_parent.parent / "rules").is_dir():
        return script_parent.parent

    # Walk up from current working directory looking for HOMUNCULUS_START_HERE.md
    cwd = Path.cwd().resolve()
    for directory in (cwd, *cwd.parents):
        if (directory / START_HERE_FILENAME).is_file():
            return directory
        nested = directory / "Homunculus"
        if (nested / START_HERE_FILENAME).is_file():
            return nested

    return script_parent.parent


def _find_git_root(start_dir: Path) -> Path | None:
    """Walk up from start_dir to locate a .git directory or file (worktree-safe)."""
    for directory in (start_dir, *start_dir.parents):
        if (directory / ".git").exists():
            return directory
    return None


def resolve_workspace_config(
    workspace_dir: str | Path | None = None,
    homunculus_root: Path | None = None,
) -> dict[str, Any]:
    """Resolve active workspace root, memory mode (headless vs obsidian), and paths."""
    fw_root = homunculus_root or resolve_homunculus_root()
    start = Path(workspace_dir).expanduser().resolve() if workspace_dir else Path.cwd().resolve()

    config_path: Path | None = None
    for directory in (start, *start.parents):
        candidate = directory / CONFIG_FILENAME
        if candidate.is_file():
            config_path = candidate
            break

    raw_cfg: dict[str, Any] = {}
    if config_path is not None:
        try:
            raw_cfg = json.loads(config_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise ValueError(f"Invalid JSON in {config_path}: {exc}") from exc
        project_root = config_path.parent
    else:
        git_root = _find_git_root(start)
        project_root = git_root if git_root is not None else start

    # Resolve memory directory: explicit HOMUNCULUS_MEMORY_ROOT env var -> .homunculus.json memory_dir -> ./memory
    env_mem_root = os.environ.get("HOMUNCULUS_MEMORY_ROOT", "").strip()
    if env_mem_root:
        env_mem_path = Path(env_mem_root.replace("\\", "/")).expanduser()
        memory_root = env_mem_path.resolve() if env_mem_path.is_absolute() else (project_root / env_mem_path).resolve()
    else:
        rel_memory = str(raw_cfg.get("memory_dir", "memory")).replace("\\", "/")
        memory_root = (project_root / rel_memory).resolve()

    # Resolve non-consumed study_briefs directory adjacent to memory_root:
    # explicit HOMUNCULUS_BRIEFS_ROOT env var -> .homunculus.json study_briefs_dir -> <memory_root.parent>/study_briefs
    env_briefs_root = os.environ.get("HOMUNCULUS_BRIEFS_ROOT", "").strip()
    if env_briefs_root:
        env_briefs_path = Path(env_briefs_root.replace("\\", "/")).expanduser()
        study_briefs_root = (
            env_briefs_path.resolve() if env_briefs_path.is_absolute() else (project_root / env_briefs_path).resolve()
        )
    elif "study_briefs_dir" in raw_cfg and str(raw_cfg.get("study_briefs_dir", "")).strip():
        rel_briefs = str(raw_cfg.get("study_briefs_dir", "study_briefs")).replace("\\", "/")
        study_briefs_root = (project_root / rel_briefs).resolve()
    else:
        study_briefs_root = (memory_root.parent / "study_briefs").resolve()

    # Determine memory_mode: explicit config -> env var -> auto-detect .obsidian -> default 'headless'
    cfg_mode = str(raw_cfg.get("memory_mode", "")).strip().lower()
    env_mode = os.environ.get("HOMUNCULUS_MEMORY_MODE", "").strip().lower()
    if cfg_mode in VALID_MEMORY_MODES:
        memory_mode = cfg_mode
    elif env_mode in VALID_MEMORY_MODES:
        memory_mode = env_mode
    elif (memory_root / ".obsidian").is_dir() or (project_root / ".obsidian").is_dir():
        memory_mode = "obsidian"
    else:
        memory_mode = "headless"

    os_info = detect_os_tier()
    capabilities = probe_runtime_capabilities(os_info["os_id"])

    return {
        "schema_version": "1.0.0",
        "os": os_info,
        "deployment_mode": "configured" if config_path is not None else "drop_in",
        "config_file": str(config_path) if config_path is not None else None,
        "homunculus_root": str(fw_root),
        "project_root": str(project_root),
        "memory_root": str(memory_root),
        "study_briefs_root": str(study_briefs_root),
        "memory_mode": memory_mode,
        "visual_studio_enabled": True,  # Always enabled in BOTH headless and obsidian modes
        "obsidian_ui_surfaces_enabled": memory_mode == "obsidian",
        "scratch_dir": str(Path(tempfile.gettempdir()) / "homunculus_scratch"),
        "paths": {
            "start_here": str(fw_root / START_HERE_FILENAME),
            "rules_dir": str(fw_root / "rules"),
            "skills_dir": str(fw_root / "skills"),
            "adapters_dir": str(fw_root / "adapters"),
            "templates_dir": str(fw_root / "templates"),
            "scripts_dir": str(fw_root / "scripts"),
        },
        "capabilities": capabilities,
    }


def probe_runtime_capabilities(os_id: str) -> dict[str, Any]:
    """Probe sandbox isolation backends and optional rasterizers without failing closed."""
    has_git = shutil.which("git") is not None
    has_bwrap = shutil.which("bwrap") is not None
    has_btrfs = shutil.which("btrfs") is not None

    if os_id == "linux" and has_bwrap and has_btrfs:
        sandbox_backend = "linux_bwrap_btrfs_cow"
    elif os_id == "linux" and has_bwrap:
        sandbox_backend = "linux_bwrap_tempcopy"
    elif os_id == "macos":
        sandbox_backend = "macos_apfs_or_git_worktree" if has_git else "macos_tempcopy"
    elif has_git:
        sandbox_backend = f"{os_id}_git_worktree_or_tempcopy"
    else:
        sandbox_backend = f"{os_id}_tempcopy"

    rasterizers = [
        tool for tool in ("rsvg-convert", "resvg", "inkscape", "magick") if shutil.which(tool) is not None
    ]

    return {
        "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        "python_executable": Path(sys.executable).name,
        "git_available": has_git,
        "sandbox_isolation_backend": sandbox_backend,
        "svg_visual_studio_ready": True,  # Pure Python stdlib SVG engine works on all OSes
        "optional_png_rasterizers": rasterizers,
    }


def write_workspace_config(
    workspace_dir: Path,
    homunculus_root: Path,
    memory_mode: str = "headless",
    memory_dir: str = "memory",
    clients: list[str] | None = None,
) -> Path:
    """Write a relative-path .homunculus.json config file inside workspace_dir."""
    if memory_mode not in VALID_MEMORY_MODES:
        raise ValueError(f"Unsupported memory_mode '{memory_mode}'. Choose from {VALID_MEMORY_MODES}.")

    workspace_dir = workspace_dir.resolve()
    homunculus_root = homunculus_root.resolve()
    try:
        rel_fw = os.path.relpath(homunculus_root, workspace_dir).replace("\\", "/")
    except ValueError:
        # Different drive letters on Windows fallback to POSIX-normalized path
        rel_fw = homunculus_root.as_posix()

    payload = {
        "schema_version": "1.0.0",
        "homunculus_rel_path": rel_fw,
        "memory_mode": memory_mode,
        "memory_dir": memory_dir,
        "study_briefs_dir": "study_briefs",
        "visual_studio": {
            "enabled": True,
            "default_format": "svg",
            "export_canvas_opt_in": False,
        },
        "enabled_clients": clients or ["antigravity", "claude_code", "claude_cowork", "cursor"],
        "compartment_firewall": {
            "enforce_secret_scan": True,
            "forbidden_tokens": [],
        },
    }
    cfg_path = workspace_dir / CONFIG_FILENAME
    cfg_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return cfg_path


_STAMP_IGNORE_DIRS = frozenset({
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
    ".obsidian",
})
_LOCAL_PATH_RE = re.compile(r'^local_path:\s*["\']?([^"\'\r\n]+)["\']?\s*$', re.MULTILINE)


def _resolve_tree_stamp_cache_dir() -> Path:
    """Resolve an out-of-repo stamp cache directory so freshness checks never dirty git status."""
    env_dir = os.environ.get("HOMUNCULUS_TREE_STAMP_CACHE", "").strip()
    candidates: list[Path] = []
    if env_dir:
        candidates.append(Path(env_dir).expanduser())
    candidates.append(Path.home() / ".cache" / "homunculus_tree_stamp")
    candidates.append(Path(tempfile.gettempdir()) / "homunculus_tree_stamp")
    for cand in candidates:
        try:
            cand.mkdir(parents=True, exist_ok=True)
            if os.access(cand, os.W_OK):
                return cand
        except OSError:
            continue
    return Path(tempfile.gettempdir())


def _resolve_memory_root_fast(workspace_dir: str | Path | None = None) -> Path:
    """Resolve `<memory_root>` without invoking subprocesses or `shutil.which` PATH scans."""
    start = Path(workspace_dir).expanduser().resolve() if workspace_dir else Path.cwd().resolve()
    config_path: Path | None = None
    for directory in (start, *start.parents):
        cand = directory / CONFIG_FILENAME
        if cand.is_file():
            config_path = cand
            break

    raw_cfg: dict[str, Any] = {}
    if config_path is not None:
        try:
            raw_cfg = json.loads(config_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            raw_cfg = {}
        project_root = config_path.parent
    else:
        git_root = _find_git_root(start)
        project_root = git_root if git_root is not None else start

    env_mem = os.environ.get("HOMUNCULUS_MEMORY_ROOT", "").strip()
    if env_mem:
        p = Path(env_mem.replace("\\", "/")).expanduser()
        return p.resolve() if p.is_absolute() else (project_root / p).resolve()

    rel_mem = str(raw_cfg.get("memory_dir", "memory")).replace("\\", "/")
    return (project_root / rel_mem).resolve()


def _read_git_head_signature(repo_dir: Path) -> str:
    """Read `.git/HEAD` (+ target ref) directly without spawning a `git` subprocess."""
    git_entry = repo_dir / ".git"
    try:
        if git_entry.is_file():
            txt = git_entry.read_text(encoding="utf-8", errors="ignore").strip()
            if txt.startswith("gitdir:"):
                git_dir = (repo_dir / txt.split(":", 1)[1].strip()).resolve()
            else:
                return ""
        elif git_entry.is_dir():
            git_dir = git_entry
        else:
            return ""

        head_file = git_dir / "HEAD"
        if not head_file.is_file():
            return ""
        head_val = head_file.read_text(encoding="utf-8", errors="ignore").strip()
        if head_val.startswith("ref:"):
            ref_rel = head_val.split(":", 1)[1].strip()
            ref_file = git_dir / ref_rel
            if ref_file.is_file():
                return f"{ref_rel}:{ref_file.read_text(encoding='utf-8', errors='ignore').strip()}"
            packed = git_dir / "packed-refs"
            if packed.is_file():
                for pline in packed.read_text(encoding="utf-8", errors="ignore").splitlines():
                    if pline.endswith(f" {ref_rel}") and not pline.startswith("#"):
                        sha_part = pline.split(" ", 1)[0].strip()
                        if len(sha_part) >= 12:
                            return f"{ref_rel}:{sha_part}"
                return f"{ref_rel}:packed:{packed.stat().st_mtime_ns}"
        return head_val
    except OSError:
        return ""


def read_git_head_sha(repo_dir: str | Path, length: int = 12) -> str:
    """Resolve short or full Git HEAD SHA in ~0.06ms via direct `.git/HEAD` read (with subprocess fallback)."""
    rpath = Path(repo_dir).expanduser().resolve()
    sig = _read_git_head_signature(rpath)
    if sig:
        candidate = sig.rsplit(":", 1)[-1].strip()
        if re.fullmatch(r"[0-9a-fA-F]{12,64}", candidate):
            return candidate[:length] if length > 0 else candidate
    if (rpath / ".git").exists():
        try:
            cmd = ["git", "-C", str(rpath), "rev-parse", f"--short={length}" if length > 0 else "HEAD", "HEAD"]
            if length <= 0:
                cmd = ["git", "-C", str(rpath), "rev-parse", "HEAD"]
            proc = subprocess.run(cmd, capture_output=True, text=True, timeout=2.0, check=False)
            if proc.returncode == 0 and proc.stdout.strip():
                return proc.stdout.strip()
        except Exception:
            pass
    return ""


_RE_MAP_SYMBOL_ENTRY = re.compile(r"(def|class)\s+([A-Za-z0-9_]+)\s+\(#L(\d+)-L(\d+)\)")
_RE_NAV_MAP_BLOCK = re.compile(
    r"(=== DEVELOPER & AI NAVIGATION MAP ===\n)(.*?)(\n\s*=== END NAVIGATION MAP ===)",
    re.DOTALL,
)


def inspect_python_ast_and_map(
    file_path: str | Path,
    local_modules: set[str] | frozenset[str] | None = None,
    source_text: str | None = None,
) -> dict[str, Any]:
    """Single-Pass Unified AST Kernel (`Pairing C`).

    Parses `file_path` once with `ast.parse()` and simultaneously extracts:
      1. Top-level `def`/`async def`/`class` symbols with exact `#Lstart-Lend` coordinates
      2. CLI flags (`add_argument(...)`) in source order
      3. Non-stdlib third-party import violations (`sys.stdlib_module_names` + `local_modules`)
      4. Verification of the in-script `=== DEVELOPER & AI NAVIGATION MAP ===` header against the live AST
    """
    fpath = Path(file_path)
    if source_text is None:
        try:
            source_text = fpath.read_text(encoding="utf-8", errors="replace")
        except OSError as exc:
            return {
                "file": str(fpath),
                "syntax_error": {"line": 1, "msg": str(exc)},
                "line_count": 0,
                "cli_flags": [],
                "symbols": [],
                "non_stdlib_imports": [],
                "map_present": False,
                "map_mismatches": [f"OSError: {exc}"],
            }

    lines = source_text.splitlines()
    line_count = len(lines)
    try:
        tree = ast.parse(source_text, filename=str(fpath))
    except SyntaxError as exc:
        return {
            "file": str(fpath),
            "syntax_error": {"line": exc.lineno or 1, "msg": exc.msg or "SyntaxError"},
            "line_count": line_count,
            "cli_flags": [],
            "symbols": [],
            "non_stdlib_imports": [],
            "map_present": False,
            "map_mismatches": [f"SyntaxError at L{exc.lineno or 1}: {exc.msg}"],
        }

    symbols: list[dict[str, Any]] = []
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            kind = "class" if isinstance(node, ast.ClassDef) else "def"
            start_ln = int(getattr(node, "lineno", 1))
            end_ln = int(getattr(node, "end_lineno", start_ln))
            is_pub = not node.name.startswith("_")
            symbols.append(
                {
                    "kind": kind,
                    "name": node.name,
                    "start_line": start_ln,
                    "end_line": end_ln,
                    "is_public": is_pub,
                    "anchor": f"{node.name}(#L{start_ln}-L{end_ln})",
                }
            )

    stdlib_names = getattr(sys, "stdlib_module_names", frozenset())
    allowed_locals = set(local_modules or ()) | {"homunculus_paths"}
    cli_flags: list[str] = []
    seen_flags: set[str] = set()
    non_stdlib_imports: list[dict[str, Any]] = []

    for node in ast.walk(tree):
        lineno = int(getattr(node, "lineno", 1))
        if isinstance(node, ast.Import):
            for alias in node.names:
                mod_root = alias.name.split(".")[0]
                if mod_root not in stdlib_names and mod_root not in allowed_locals:
                    non_stdlib_imports.append(
                        {"module": alias.name, "line": lineno, "stmt": f"import {alias.name}"}
                    )
        elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
            mod_root = node.module.split(".")[0]
            if mod_root not in stdlib_names and mod_root not in allowed_locals:
                non_stdlib_imports.append(
                    {"module": node.module, "line": lineno, "stmt": f"from {node.module}"}
                )
        elif isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
            if node.func.attr == "add_argument" and node.args:
                for arg in node.args:
                    if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                        val = arg.value.strip()
                        if val and val not in seen_flags:
                            seen_flags.add(val)
                            cli_flags.append(val)

    doc_head = "\n".join(lines[:75])
    map_present = "=== DEVELOPER & AI NAVIGATION MAP ===" in doc_head
    map_mismatches: list[str] = []
    if map_present:
        doc_entries = {
            m.group(2): (m.group(1), int(m.group(3)), int(m.group(4)))
            for m in _RE_MAP_SYMBOL_ENTRY.finditer(doc_head)
        }
        ast_entries = {s["name"]: (s["kind"], s["start_line"], s["end_line"]) for s in symbols}
        for sym_name, ast_coord in ast_entries.items():
            if sym_name not in doc_entries:
                map_mismatches.append(f"Missing symbol in navigation map: {sym_name} (#L{ast_coord[1]}-L{ast_coord[2]})")
            elif doc_entries[sym_name] != ast_coord:
                d_coord = doc_entries[sym_name]
                map_mismatches.append(
                    f"Drifted line range for {sym_name}: map has #L{d_coord[1]}-L{d_coord[2]} vs AST #L{ast_coord[1]}-L{ast_coord[2]}"
                )
        for doc_sym in doc_entries:
            if doc_sym not in ast_entries:
                map_mismatches.append(f"Removed symbol still listed in navigation map: {doc_sym}")

    return {
        "file": str(fpath),
        "syntax_error": None,
        "line_count": line_count,
        "cli_flags": cli_flags,
        "symbols": symbols,
        "non_stdlib_imports": non_stdlib_imports,
        "map_present": map_present,
        "map_mismatches": map_mismatches,
    }


def _format_symbol_index_lines(symbols: list[dict[str, Any]]) -> list[str]:
    if not symbols:
        return ["    - (module-level execution / no top-level def or class)"]
    entries = [f"{s['kind']} {s['name']} (#L{s['start_line']}-L{s['end_line']})" for s in symbols]
    rows: list[str] = []
    for idx in range(0, len(entries), 2):
        left = entries[idx]
        if idx + 1 < len(entries):
            right = entries[idx + 1]
            rows.append(f"    - {left:<46} | {right}")
        else:
            rows.append(f"    - {left}")
    return rows


def load_script_contract(fw_root: str | Path, script_path: str | Path) -> dict[str, Any]:
    """Load the TIER1 clean-room script contract entry from `scripts/script_contracts.json` (Decision 4C)."""
    root_p = Path(fw_root).resolve()
    sp = Path(script_path)
    contracts_file = root_p / "scripts" / "script_contracts.json"
    if not contracts_file.is_file():
        return {}
    try:
        data = json.loads(contracts_file.read_text(encoding="utf-8"))
        scripts_map = data.get("scripts", {})
        if sp.name in scripts_map:
            return dict(scripts_map[sp.name])
    except Exception:
        return {}
    return {}


def record_preflight_receipt(
    fw_root: str | Path,
    script_path: str | Path,
    memory_root: str | Path | None = None,
    project_name: str = "",
) -> dict[str, Any]:
    """
    Record a preflight receipt in `.cache/preflight_state.json` bound to `(script_rel_path, pre_edit_blob_sha256, session_date)` (Decision 4A).
    """
    root_p = Path(fw_root).resolve()
    sp = Path(script_path).resolve()
    try:
        rel_p = sp.relative_to(root_p).as_posix()
    except ValueError:
        rel_p = sp.name

    live_bytes = sp.read_bytes() if sp.is_file() else b""
    live_sha = hashlib.sha256(live_bytes).hexdigest()[:16]
    head_sha = live_sha
    if (root_p / ".git").exists():
        try:
            proc = subprocess.run(
                ["git", "-C", str(root_p), "show", f"HEAD:{rel_p}"],
                capture_output=True,
                timeout=2.0,
                check=False,
            )
            if proc.returncode == 0 and proc.stdout:
                head_sha = hashlib.sha256(proc.stdout).hexdigest()[:16]
        except Exception:
            pass

    import datetime as _dt

    session_date = _dt.date.today().isoformat()
    receipt = {
        "project": project_name,
        "script": sp.name,
        "script_rel_path": rel_p,
        "abs_path": str(sp),
        "pre_edit_blob_sha256": live_sha,
        "git_head_blob_sha256": head_sha,
        "session_date": session_date,
        "disposed": False,
    }

    cache_dirs: list[Path] = []
    if memory_root:
        mem_p = Path(memory_root).expanduser().resolve()
        if mem_p.is_dir():
            cache_dirs.append(mem_p / ".cache")
    else:
        cache_dirs.extend([_resolve_tree_stamp_cache_dir(), root_p / ".cache"])
        auto_mem = _resolve_memory_root_fast()
        if auto_mem is not None and auto_mem.is_dir():
            cache_dirs.append(auto_mem / ".cache")

    for cdir in cache_dirs:
        try:
            cdir.mkdir(parents=True, exist_ok=True)
            pfile = cdir / "preflight_state.json"
            existing: dict[str, Any] = {}
            if pfile.is_file():
                try:
                    existing = json.loads(pfile.read_text(encoding="utf-8"))
                except Exception:
                    existing = {}
            receipts_map = existing.setdefault("receipts", {})
            receipts_map[rel_p] = receipt
            receipts_map[sp.name] = receipt
            pfile.write_text(json.dumps(existing, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        except OSError:
            pass

    return receipt


def sync_script_navigation_map(file_path: str | Path, write: bool = True) -> dict[str, Any]:
    """Two-pass fixed-point auto-healer for `=== DEVELOPER & AI NAVIGATION MAP ===` headers (`Pairing A` + `Decision 4C`)."""
    fpath = Path(file_path)
    try:
        orig_text = fpath.read_text(encoding="utf-8")
    except OSError as exc:
        return {"file": str(fpath), "status": "ERROR", "updated": False, "reason": str(exc)}

    if "=== DEVELOPER & AI NAVIGATION MAP ===" not in orig_text[:4096]:
        return {"file": str(fpath), "status": "NO_MAP_HEADER", "updated": False}

    cur_text = orig_text
    contract_line = f"  Contract      : `scripts/script_contracts.json` [`{fpath.name}`]"
    for _pass in range(2):
        info = inspect_python_ast_and_map(fpath, source_text=cur_text)
        if info["syntax_error"] is not None:
            return {"file": str(fpath), "status": "SYNTAX_ERROR", "updated": False}
        sym_lines = _format_symbol_index_lines(info["symbols"])
        flags_line = ", ".join(info["cli_flags"]) if info["cli_flags"] else "(none / library or positional)"

        def _rebuild_block(match: re.Match[str]) -> str:
            header = match.group(1)
            body = match.group(2)
            footer = match.group(3)
            kept_meta: list[str] = []
            has_contract = False
            for ln in body.splitlines():
                if ln.strip().startswith("Symbol Index"):
                    break
                if ln.strip().startswith("Contract"):
                    kept_meta.append(contract_line)
                    has_contract = True
                elif ln.strip().startswith("CLI Flags"):
                    if not has_contract:
                        kept_meta.append(contract_line)
                        has_contract = True
                    kept_meta.append(f"  CLI Flags     : {flags_line}")
                else:
                    kept_meta.append(ln)
            if not has_contract:
                kept_meta.append(contract_line)
            kept_meta.append("  Symbol Index  (jump directly via read_file StartLine/EndLine):")
            kept_meta.extend(sym_lines)
            return header + "\n".join(kept_meta) + footer

        cur_text = _RE_NAV_MAP_BLOCK.sub(_rebuild_block, cur_text, count=1)

    updated = cur_text != orig_text
    if updated and write:
        fpath.write_text(cur_text, encoding="utf-8")
    final_info = inspect_python_ast_and_map(fpath, source_text=cur_text)
    return {
        "file": str(fpath),
        "status": "UPDATED" if updated else "FRESH",
        "updated": updated,
        "symbol_count": len(final_info["symbols"]),
        "mismatches": final_info["map_mismatches"],
    }


def _compute_structural_stamp(
    memory_root: Path,
    cached_hub_mtimes: dict[str, int] | None = None,
    cached_repo_roots: list[str] | None = None,
) -> dict[str, Any]:
    """Compute a ~1.7ms dentry + git-HEAD structural digest across memory_root and indexed repos."""
    projects_dir = memory_root / "Projects"
    hub_mtimes: dict[str, int] = {}
    if projects_dir.is_dir():
        for hub in sorted(projects_dir.glob("*/*.md")):
            if hub.stem == hub.parent.name:
                try:
                    hub_mtimes[str(hub)] = hub.stat().st_mtime_ns
                except OSError:
                    continue

    if (
        cached_hub_mtimes is not None
        and cached_repo_roots is not None
        and hub_mtimes == cached_hub_mtimes
    ):
        repo_roots = [Path(p) for p in cached_repo_roots]
    else:
        repo_roots = []
        seen_r: set[str] = set()
        for hub_str in sorted(hub_mtimes.keys()):
            try:
                txt = Path(hub_str).read_text(encoding="utf-8", errors="ignore")
            except OSError:
                continue
            m = _LOCAL_PATH_RE.search(txt[:2048])
            if not m:
                continue
            lp = m.group(1).strip().replace("\\", "/")
            if not lp:
                continue
            cand = Path(lp)
            resolved_r = cand.resolve() if cand.is_absolute() else (memory_root / cand).resolve()
            r_str = str(resolved_r)
            if r_str not in seen_r and resolved_r.is_dir():
                seen_r.add(r_str)
                repo_roots.append(resolved_r)

    hasher = hashlib.sha256()
    for root in (memory_root, *repo_roots):
        if not root.is_dir():
            hasher.update(f"MISSING:{root}\n".encode("utf-8"))
            continue
        hasher.update(f"ROOT:{root}|HEAD:{_read_git_head_signature(root)}\n".encode("utf-8"))
        for dirpath, dirnames, filenames in os.walk(root, topdown=True, followlinks=False):
            dirnames[:] = sorted(d for d in dirnames if d not in _STAMP_IGNORE_DIRS)
            filenames_sorted = sorted(filenames)
            rel_d = os.path.relpath(dirpath, root).replace("\\", "/")
            hasher.update(
                f"D:{rel_d}|{'/'.join(dirnames)}|{'/'.join(filenames_sorted)}\n".encode("utf-8")
            )

    return {
        "digest": hasher.hexdigest()[:24],
        "hub_mtimes": hub_mtimes,
        "repo_roots": [str(r) for r in repo_roots],
    }


def _load_sync_memory_module(fw_root: Path) -> Any:
    existing = sys.modules.get("sync_memory")
    if existing is not None and hasattr(existing, "sync_all_project_trees"):
        return existing
    sync_script = fw_root / "skills" / "project-memory" / "scripts" / "sync_memory.py"
    if not sync_script.is_file():
        return None
    spec = importlib.util.spec_from_file_location("sync_memory", sync_script)
    if spec is None or spec.loader is None:
        return None
    mod = importlib.util.module_from_spec(spec)
    sys.modules["sync_memory"] = mod
    spec.loader.exec_module(mod)
    return mod


def ensure_directory_fresh(
    workspace_dir: str | Path | None = None,
    homunculus_root: str | Path | None = None,
    memory_root_override: str | Path | None = None,
    force: bool = False,
) -> dict[str, Any]:
    """
    Fast (`~3.2ms` cached / `~25ms` rebuild) write-if-changed structural freshness guard for
    `<memory_root>/Directory/*.md` and `Projects/<P>/<P>.md` `AUTO-TREE` blocks.

    Automatically skips on read-only filesystems (`EROFS` inside `bwrap` when `memory/` is not
    a writable target), when `HOMUNCULUS_DISABLE_AUTO_TREE_SYNC=1`, and in Zero-Vault repositories.
    """
    if not force and os.environ.get("HOMUNCULUS_DISABLE_AUTO_TREE_SYNC") == "1":
        return {"status": "SKIPPED_DISABLED", "synced": False}

    try:
        fw_root = resolve_homunculus_root(homunculus_root)
        mem_root = (
            Path(memory_root_override).expanduser().resolve()
            if memory_root_override
            else _resolve_memory_root_fast(workspace_dir)
        )
        if not (mem_root / "Projects").is_dir():
            return {"status": "SKIPPED_NO_MEMORY", "synced": False, "memory_root": str(mem_root)}
        if not os.access(mem_root, os.W_OK):
            return {"status": "SKIPPED_READONLY", "synced": False, "memory_root": str(mem_root)}

        cache_dir = _resolve_tree_stamp_cache_dir()
        mem_key = hashlib.sha256(str(mem_root).encode("utf-8")).hexdigest()[:16]
        stamp_file = cache_dir / f"stamp_{mem_key}.json"

        cached_data: dict[str, Any] = {}
        if stamp_file.is_file():
            try:
                cached_data = json.loads(stamp_file.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                cached_data = {}

        cur_stamp = _compute_structural_stamp(
            mem_root,
            cached_hub_mtimes=cached_data.get("hub_mtimes") if isinstance(cached_data.get("hub_mtimes"), dict) else None,
            cached_repo_roots=cached_data.get("repo_roots") if isinstance(cached_data.get("repo_roots"), list) else None,
        )
        dir_index_exists = (mem_root / "Directory" / "Directory_Index.md").is_file()

        if not force and dir_index_exists and cached_data.get("digest") == cur_stamp["digest"]:
            return {
                "status": "FRESH_CACHED",
                "synced": False,
                "memory_root": str(mem_root),
                "digest": cur_stamp["digest"],
            }

        sync_mod = _load_sync_memory_module(fw_root)
        if sync_mod is None:
            return {"status": "SKIPPED_NO_SYNC_MODULE", "synced": False, "memory_root": str(mem_root)}

        sync_res = sync_mod.sync_all_project_trees(mem_root)
        post_stamp = _compute_structural_stamp(
            mem_root,
            cached_hub_mtimes=None,
            cached_repo_roots=None,
        )
        try:
            stamp_file.write_text(json.dumps(post_stamp), encoding="utf-8")
        except OSError:
            pass

        updated_projs = sync_res.get("updated_projects", [])
        return {
            "status": "SYNCED",
            "synced": True,
            "memory_root": str(mem_root),
            "updated_projects": updated_projs,
            "digest": post_stamp["digest"],
        }
    except OSError as exc:
        return {"status": "SKIPPED_OS_ERROR", "synced": False, "reason": str(exc)}


def set_core_lock_state(homunculus_root: str | Path, lock: bool) -> dict[str, Any]:
    """Toggle physical OS read-only (0444/0555) vs writable (0644/0755) permissions across Homunculus core files."""
    fw_root = resolve_homunculus_root(homunculus_root)
    target_dirs = ("rules", "skills", "addons", "scripts")
    touched = 0
    errors: list[str] = []
    for sub in target_dirs:
        sdir = fw_root / sub
        if not sdir.is_dir():
            continue
        for p in sorted(sdir.rglob("*")):
            if not p.is_file() or "__pycache__" in p.parts:
                continue
            try:
                is_exec = p.suffix in (".py", ".sh")
                if lock:
                    new_mode = 0o555 if is_exec else 0o444
                else:
                    new_mode = 0o755 if is_exec else 0o644
                p.chmod(new_mode)
                touched += 1
            except OSError as exc:
                errors.append(f"{p}: {exc}")
    return {
        "status": "LOCKED" if lock else "UNLOCKED",
        "homunculus_root": str(fw_root),
        "files_updated": touched,
        "errors": errors,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Homunculus Cross-OS Workspace, Memory-Mode & Capability Resolver."
    )
    parser.add_argument("--workspace", help="Target project/workspace directory (default: CWD).")
    parser.add_argument("--homunculus-root", help="Explicit Homunculus framework root directory.")
    parser.add_argument("--memory-root", help="Optional explicit memory root override for --ensure-fresh.")
    parser.add_argument(
        "--init-config",
        action="store_true",
        help="Write a portable .homunculus.json configuration in --workspace.",
    )
    parser.add_argument(
        "--memory-mode",
        choices=VALID_MEMORY_MODES,
        default="headless",
        help="Memory mode when initializing config: 'headless' (default) or 'obsidian'.",
    )
    parser.add_argument(
        "--memory-dir",
        default="memory",
        help="Relative directory for project memory dossiers and task queues (default: 'memory').",
    )
    parser.add_argument(
        "--simulate-os",
        choices=("linux", "darwin", "win32"),
        help="Simulate OS platform detection for cross-OS verification tests.",
    )
    parser.add_argument("--check", action="store_true", help="Verify framework directories exist.")
    parser.add_argument(
        "--ensure-fresh",
        action="store_true",
        help="Run the ~1.7ms structural dentry/HEAD check and write-if-changed refresh of memory/Directory/ + AUTO-TREE.",
    )
    parser.add_argument(
        "--map",
        metavar="SCRIPT_OR_ALL",
        help="Print the AST-verified Developer & AI Navigation Map (#Lstart-Lend) for a script name/path or 'all'.",
    )
    parser.add_argument(
        "--sync-maps",
        action="store_true",
        help="Auto-heal in-script Developer & AI Navigation Map (#Lstart-Lend) headers across all Python scripts.",
    )
    parser.add_argument(
        "--lock-core",
        action="store_true",
        help="Set Homunculus core files (rules/, skills/, addons/, scripts/) to OS read-only (0444/0555).",
    )
    parser.add_argument(
        "--unlock-core",
        action="store_true",
        help="Restore writable permissions (0644/0755) on Homunculus core files for intentional upgrades.",
    )
    parser.add_argument("--quiet", action="store_true", help="Suppress stdout banner when running --ensure-fresh.")
    parser.add_argument("--json", action="store_true", help="Emit resolved configuration as JSON.")
    args = parser.parse_args(argv)

    fw_root = (
        Path(args.homunculus_root).expanduser().resolve()
        if args.homunculus_root
        else Path(__file__).resolve().parent.parent
    )
    target_ws = Path(args.workspace).expanduser().resolve() if args.workspace else Path.cwd().resolve()

    if args.lock_core or args.unlock_core:
        lock_res = set_core_lock_state(fw_root, lock=bool(args.lock_core and not args.unlock_core))
        if args.json:
            print(json.dumps(lock_res, indent=2))
        else:
            print(
                f"[{lock_res['status']}] Homunculus Core Protection | "
                f"Files Updated: {lock_res['files_updated']} | Root: {lock_res['homunculus_root']}"
            )
        return 0 if not lock_res["errors"] else 1

    if args.sync_maps or args.map:
        py_files: list[Path] = []
        for sub in ("scripts", "skills", "addons"):
            sdir = fw_root / sub
            if sdir.is_dir():
                py_files.extend(sorted(sdir.rglob("*.py")))
        if args.sync_maps:
            results = [sync_script_navigation_map(p, write=True) for p in py_files]
            if args.json:
                print(json.dumps({"synced_scripts": len(results), "results": results}, indent=2))
            else:
                updated_cnt = sum(1 for r in results if r.get("updated"))
                print(f"[PASS] Synced {len(results)} script navigation maps ({updated_cnt} updated).")
            return 0
        query = args.map.strip()
        matched = [
            p
            for p in py_files
            if query.lower() == "all"
            or p.name.lower() == query.lower()
            or p.stem.lower() == query.lower()
            or query.replace("\\", "/") in p.as_posix()
        ]
        if not matched:
            cand = Path(query).expanduser().resolve()
            if cand.is_file():
                matched = [cand]
        if not matched:
            print(f"[FAIL] No Python script matching '{query}' found under {fw_root}", file=sys.stderr)
            return 1
        out_maps: list[dict[str, Any]] = []
        for p in matched:
            m_info = inspect_python_ast_and_map(p)
            if query.lower() != "all":
                m_info["contract"] = load_script_contract(fw_root, p)
                m_info["preflight_receipt"] = record_preflight_receipt(fw_root, p, args.memory_root)
            out_maps.append(m_info)
        if args.json:
            print(json.dumps(out_maps[0] if len(out_maps) == 1 else out_maps, indent=2))
        else:
            for m in out_maps:
                rel_m = os.path.relpath(m["file"], fw_root).replace("\\", "/")
                print(f"=== {rel_m} ({m['line_count']} lines | {len(m['symbols'])} symbols) ===")
                if m["cli_flags"]:
                    print("  CLI Flags : " + ", ".join(m["cli_flags"]))
                contract = m.get("contract") or {}
                if contract:
                    print("  [TIER1 Script Contract & Hub-Filtered 1-Hop Coupling (scripts/script_contracts.json)]:")
                    for mk in contract.get("must_keep_invariants", []):
                        print(f"    + Must-Keep : {mk}")
                    for rb in contract.get("retired_anti_patterns", []):
                        print(f"    - Never-Add : {rb}")
                    c_1hop = contract.get("coupled_functional_1hop", [])
                    c_data = contract.get("coupled_data_contracts", [])
                    r_tests = contract.get("required_tests", [])
                    if c_1hop:
                        print("    * Coupled 1-Hop Scripts : " + ", ".join(c_1hop))
                    if c_data:
                        print("    * Shared Data Contracts : " + ", ".join(c_data))
                    if r_tests:
                        print("    * Required Test Suites  : " + ", ".join(r_tests))
                pf_rec = m.get("preflight_receipt")
                if pf_rec:
                    print(
                        f"  [PREFLIGHT_RECEIPT_RECORDED] {pf_rec['script_rel_path']} | "
                        f"Blob SHA: {pf_rec['pre_edit_blob_sha256']} | Date: {pf_rec['session_date']}"
                    )
                for s in m["symbols"]:
                    print(f"  - {s['kind']} {s['name']} (#L{s['start_line']}-L{s['end_line']})")
        return 0

    if args.ensure_fresh and not args.init_config and not args.check:
        fresh_res = ensure_directory_fresh(
            workspace_dir=target_ws,
            homunculus_root=fw_root,
            memory_root_override=args.memory_root,
        )
        if args.json:
            print(json.dumps(fresh_res, indent=2))
        elif not args.quiet:
            print(
                f"[{fresh_res.get('status', 'OK')}] Directory Freshness Guard | "
                f"Synced: {fresh_res.get('synced', False)} | "
                f"Memory: {fresh_res.get('memory_root', 'none')}"
            )
        return 0

    if args.init_config:
        cfg_path = write_workspace_config(
            workspace_dir=target_ws,
            homunculus_root=fw_root,
            memory_mode=args.memory_mode,
            memory_dir=args.memory_dir,
        )
        if not args.json and not args.quiet:
            print(f"[OK] Wrote portable workspace config: {cfg_path.name} (memory_mode={args.memory_mode})")

    resolved = resolve_workspace_config(workspace_dir=target_ws, homunculus_root=fw_root)
    if args.simulate_os:
        sim_os = detect_os_tier(args.simulate_os)
        resolved["os"] = sim_os
        resolved["capabilities"] = probe_runtime_capabilities(sim_os["os_id"])

    if args.check or args.ensure_fresh:
        fresh_res = ensure_directory_fresh(
            workspace_dir=target_ws,
            homunculus_root=fw_root,
            memory_root_override=args.memory_root,
        )
        resolved["directory_freshness"] = fresh_res

    if args.check:
        required_dirs = ("rules", "skills", "adapters", "templates", "scripts", "tests")
        missing = [d for d in required_dirs if not (fw_root / d).is_dir()]
        if missing:
            print(f"[FAIL] Missing required Homunculus directories: {missing}", file=sys.stderr)
            return 2
        if sys.version_info < (3, 10):
            print("[FAIL] Python 3.10+ is required.", file=sys.stderr)
            return 2

    if args.json:
        print(json.dumps(resolved, indent=2))
    elif not args.quiet:
        os_meta = resolved["os"]
        cap = resolved["capabilities"]
        print(
            f"[PASS] Homunculus Path & Capability Resolver | "
            f"OS: {os_meta['os_label']} | "
            f"Deployment: {resolved['deployment_mode']} | "
            f"Memory: {resolved['memory_mode']} | "
            f"Visual Studio: SVG-Ready | "
            f"Sandbox: {cap['sandbox_isolation_backend']}"
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
