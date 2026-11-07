#!/usr/bin/env python3
"""Homunculus Cross-OS Dynamic Workspace, Memory-Mode & Runtime Capability Resolver.

Resolves Homunculus framework and target project paths generically across
Windows, macOS, and Linux.

Requires ONLY Python 3.10+ standard library (zero third-party pip packages) and operates
in both Zero-Install "Drop-In & Point" mode and Optional Installer mode.
"""
from __future__ import annotations

import argparse
import json
import os
import platform
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


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Homunculus Cross-OS Workspace, Memory-Mode & Capability Resolver."
    )
    parser.add_argument("--workspace", help="Target project/workspace directory (default: CWD).")
    parser.add_argument("--homunculus-root", help="Explicit Homunculus framework root directory.")
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
    parser.add_argument("--json", action="store_true", help="Emit resolved configuration as JSON.")
    args = parser.parse_args(argv)

    fw_root = resolve_homunculus_root(args.homunculus_root)
    target_ws = Path(args.workspace).expanduser().resolve() if args.workspace else Path.cwd().resolve()

    if args.init_config:
        cfg_path = write_workspace_config(
            workspace_dir=target_ws,
            homunculus_root=fw_root,
            memory_mode=args.memory_mode,
            memory_dir=args.memory_dir,
        )
        if not args.json:
            print(f"[OK] Wrote portable workspace config: {cfg_path.name} (memory_mode={args.memory_mode})")

    resolved = resolve_workspace_config(workspace_dir=target_ws, homunculus_root=fw_root)
    if args.simulate_os:
        sim_os = detect_os_tier(args.simulate_os)
        resolved["os"] = sim_os
        resolved["capabilities"] = probe_runtime_capabilities(sim_os["os_id"])

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
    else:
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
