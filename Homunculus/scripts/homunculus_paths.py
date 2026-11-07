#!/usr/bin/env python3
"""Homunculus Cross-OS Dynamic Workspace, Memory-Mode & Runtime Capability Resolver.

Resolves Homunculus framework and target project paths generically across
Windows, macOS, and Linux.

Requires ONLY Python 3.10+ standard library (zero third-party pip packages) and operates
in both Zero-Install "Drop-In & Point" mode and Optional Installer mode.
"""
from __future__ import annotations

import argparse
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
        "enabled_clients": clients or ["agents_md", "antigravity", "claude_code", "claude_cowork", "cursor"],
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
                return f"{ref_rel}:packed:{packed.stat().st_mtime_ns}"
        return head_val
    except OSError:
        return ""


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
    parser.add_argument("--quiet", action="store_true", help="Suppress stdout banner when running --ensure-fresh.")
    parser.add_argument("--json", action="store_true", help="Emit resolved configuration as JSON.")
    args = parser.parse_args(argv)

    fw_root = resolve_homunculus_root(args.homunculus_root)
    target_ws = Path(args.workspace).expanduser().resolve() if args.workspace else Path.cwd().resolve()

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
