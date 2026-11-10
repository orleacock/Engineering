#!/usr/bin/env python3
"""
Deterministic OS Containment & Copy-on-Write Sandbox Runner (`engineering-sandbox`).

Wraps script execution, validator checks, and subagent mutation rehearsals inside a
Linux Bubblewrap (`bwrap`) mount namespace where:
  1. The entire workstation root `/` is mounted kernel-enforced READ-ONLY (`EROFS`).
  2. Target directories (`--target-dir`) are cloned instantaneously via `cp -a --reflink=auto`
     (zero-disk-bloat Copy-on-Write on Btrfs `/home`) and bind-mounted directly over
     their real absolute paths inside the container.
  3. Pre- and post-run host fingerprints verify `Live Files Mutated == 0` mathematically.
  4. Optional `+faults` cases (`--fault-case "<setup_cmd> :: <validator_cmd>"`) run in
     isolated disposable clones to verify validators fail closed (`exit != 0`) on bad data.
  5. Full forensic logs (`report.json`, `mutations.diff`, `stdout.log`, `stderr.log`) are
     written to disk while emitting a compact <=350-token 5-block summary to stdout.

=== DEVELOPER & AI NAVIGATION MAP ===
  Owning Module : `engineering-sandbox` (`skills/engineering-sandbox/SKILL.md`)
  Callers       : Track-2 verification workflow (`co-engineering-partner.md`), `pre-commit-gate`, `test_core_skills.py`
  Callees       : `homunculus_paths.py` (`ensure_directory_fresh` Gate 0), `verify_claims.py` & `audit_repo_docs.py` (in `_audit_arm_deliverables`)
  Contract      : `scripts/script_contracts.json` [`sandbox_runner.py`]
  CLI Flags     : --mode, --target-dir, --workspace, --writable-dir, --cwd, --spec, --faults, --cmd, --fault-case, --allow-noop-setup, --timeout, --report-dir, --keep-overlay, --keep-failed-cow, --blind-dir, --visible-dir, --blind-transcript, --visible-transcript, --compare-source, --repo-root, --prepare, --json
  Symbol Index  (jump directly via read_file StartLine/EndLine):
    - def _resolve_default_cache_root (#L52-L63)     | def sha256_file (#L133-L141)
    - def snapshot_tree_manifest (#L144-L167)        | def diff_manifests (#L170-L183)
    - def build_unified_diff (#L186-L224)            | def clone_cow_directory (#L227-L261)
    - def run_in_bwrap (#L264-L352)                  | def check_bwrap_available (#L355-L365)
    - def _strip_json_arg (#L368-L374)               | def resolve_transcript_path (#L377-L404)
    - def parse_transcript_telemetry (#L407-L541)    | def _resolve_overlay_path (#L544-L552)
    - def _collect_md_files (#L555-L563)             | def _audit_arm_deliverables (#L566-L684)
    - def evaluate_ab_comparison (#L687-L904)        | def main (#L907-L1659)
=== END NAVIGATION MAP ===
"""

from __future__ import annotations

import argparse
import datetime as dt
import difflib
import hashlib
import json
import os
import re
import shlex
import shutil
import subprocess
import sys
import time
import uuid
from typing import Dict, List, Optional, Tuple

def _resolve_default_cache_root() -> str:
    if os.environ.get("HOMUNCULUS_SANDBOX_CACHE"):
        return os.path.expanduser(os.environ["HOMUNCULUS_SANDBOX_CACHE"])
    cand = os.path.expanduser("~/.cache/homunculus_sandbox")
    try:
        os.makedirs(cand, exist_ok=True)
        if os.access(cand, os.W_OK):
            return cand
    except OSError:
        pass
    import tempfile as _tf
    return os.path.join(_tf.gettempdir(), "homunculus_sandbox")


DEFAULT_CACHE_ROOT = _resolve_default_cache_root()
VALID_MODES = (
    "prepare",
    "dry-run",
    "blind-light",
    "blind-full",
    "visible-light",
    "visible-full",
    "compare-light",
    "compare-full",
)
VRF_RE = re.compile(r"\bVRF-[0-9a-f]{12}\b", re.IGNORECASE)
EROFS_RE = re.compile(
    r"(?:Read-only file system|EROFS|\[Errno 30\])[^\n]*",
    re.IGNORECASE,
)
TBD_TAG_RE = re.compile(r"\[(?:TBD|CONFLICT)(?:\s*[:—–-][^\]]*)?\]", re.IGNORECASE)
CONFLICT_TBD_RE = re.compile(r"\[(?:TBD:\s*)?CONFLICT(?:\s*[:—–-][^\]]*)?\]", re.IGNORECASE)
UUID_RE = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$", re.IGNORECASE)
LS_FIND_CMD_RE = re.compile(
    r"(?:(?:^|[;&|]\s*)(?:ls|find)\b|\bos\.(?:listdir|walk|scandir)\s*\(|\bglob\.glob\s*\(|\.\s*r?glob\s*\()"
)
ORACLE_SCRIPT_NAMES = (
    "verify_claims",
    "audit_repo_docs",
    "sync_memory",
    "audit_skill_hygiene",
    "audit_data_boundary",
    "audit_portability",
    "teach_brief",
)
ORACLE_EXEC_CMD_RE = re.compile(
    r"(?:^|[;&|]\s*)(?:[A-Za-z_][A-Za-z0-9_]*=\S+\s+)*(?:\S*/)?python3?(?:\.\d+)?\s+"
    r"(?!-c\b)"
    r"[^\n;|&]*?\b(?:" + "|".join(ORACLE_SCRIPT_NAMES) + r")\.py\b"
)
SHELL_PY_SNOOP_RE = re.compile(
    r"(?:(?:^|[;&|]\s*)(?:sed|grep|rg|awk|cat|head|tail|nl)\b[^\n;|&]*?\b[A-Za-z0-9_./~-]+\.py\b"
    r"|\bpython3?(?:\.\d+)?\s+-c\b[^\n]*?(?:(?:open|read_text|run_path|exec)\s*\([^\n)]*?\.py\b"
    r"|\b(?:import|__import__|import_module)\s*\(?\s*['\"]?(?:" + "|".join(ORACLE_SCRIPT_NAMES) + r"|inspect_hardware_ecosystem)\b"
    r"|\binspect\.(?:getsource|getsourcelines)\b))"
)
ADHOC_CAD_SNOOP_RE = re.compile(
    r"(?:(?:^|[;&|]\s*)(?:sed|grep|rg|awk|cat|head|tail|nl|strings)\b[^\n;|&]*?\.(?:step|stp|stl|3mf|iges|fcstd)\b"
    r"|\bpython3?(?:\.\d+)?\s+(?!-m\b)(?![^\n;|&]*?inspect_hardware_ecosystem\.py\b)[^\n]*?\.(?:step|stp|stl|3mf|iges|fcstd)\b"
    r"|\b(?:CYLINDRICAL_SURFACE|ADVANCED_FACE|CARTESIAN_POINT)\b)",
    re.IGNORECASE,
)

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
SKILLS_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "..", ".."))
HOMUNCULUS_ROOT = os.path.abspath(os.path.join(SKILLS_ROOT, ".."))
for _p in (SCRIPT_DIR, os.path.join(HOMUNCULUS_ROOT, "scripts")):
    if _p not in sys.path:
        sys.path.insert(0, _p)
import homunculus_paths  # noqa: E402

DEFAULT_AUDIT_DOCS_SCRIPT = os.path.join(SKILLS_ROOT, "doc-and-card-studio", "scripts", "audit_repo_docs.py")
DEFAULT_VERIFY_CLAIMS_SCRIPT = os.path.join(SKILLS_ROOT, "claim-verification", "scripts", "verify_claims.py")
DEFAULT_BRAIN_ROOT = os.path.expanduser(
    os.environ.get("HOMUNCULUS_TRANSCRIPT_DIR", "~/.gemini/antigravity-cli/brain")
)
DEFAULT_CLAUDE_PROJECTS_ROOT = os.path.expanduser("~/.claude/projects")

SKIP_WALK_DIRS = {".git", "__pycache__", ".mypy_cache", ".pytest_cache", "node_modules", ".venv"}


def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            chunk = f.read(65536)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


def snapshot_tree_manifest(root: str, include_hashes: bool = True) -> Dict[str, Tuple[int, int, str]]:
    """
    Build a deterministic map of `rel_path -> (size, mtime_ns, sha256_or_symlink)`
    for every non-.git file under `root`.
    """
    manifest: Dict[str, Tuple[int, int, str]] = {}
    root = os.path.abspath(root)
    for dirpath, dirnames, filenames in os.walk(root, topdown=True, followlinks=False):
        dirnames[:] = sorted(d for d in dirnames if d not in SKIP_WALK_DIRS)
        for fn in sorted(filenames):
            full = os.path.join(dirpath, fn)
            rel = os.path.relpath(full, root)
            try:
                st = os.lstat(full)
                if os.path.islink(full):
                    sig = f"symlink->{os.readlink(full)}"
                elif os.path.isfile(full):
                    sig = sha256_file(full) if include_hashes else ""
                else:
                    sig = "special"
                manifest[rel] = (st.st_size, st.st_mtime_ns, sig)
            except FileNotFoundError:
                continue
    return manifest


def diff_manifests(
    before: Dict[str, Tuple[int, int, str]],
    after: Dict[str, Tuple[int, int, str]],
) -> Tuple[List[str], List[str], List[str]]:
    """Return `(created, modified, deleted)` relative file lists comparing content signatures."""
    b_keys = set(before.keys())
    a_keys = set(after.keys())
    created = sorted(a_keys - b_keys)
    deleted = sorted(b_keys - a_keys)
    modified = sorted(
        k for k in (b_keys & a_keys)
        if before[k][2] != after[k][2] or before[k][0] != after[k][0]
    )
    return created, modified, deleted


def build_unified_diff(
    label: str,
    orig_root: str,
    clone_root: str,
    created: List[str],
    modified: List[str],
    deleted: List[str],
    max_file_bytes: int = 262144,
) -> str:
    """Generate a readable unified diff across created/modified/deleted text files."""
    chunks: List[str] = []
    for rel in sorted(set(created) | set(modified) | set(deleted)):
        p_orig = os.path.join(orig_root, rel)
        p_clone = os.path.join(clone_root, rel)

        def _read_lines(p: str) -> Optional[List[str]]:
            if not os.path.exists(p) or os.path.islink(p) or not os.path.isfile(p):
                return []
            if os.path.getsize(p) > max_file_bytes:
                return None
            try:
                with open(p, "r", encoding="utf-8") as f:
                    return f.readlines()
            except UnicodeDecodeError:
                return None

        a_lines = _read_lines(p_orig) if rel not in created else []
        b_lines = _read_lines(p_clone) if rel not in deleted else []
        a_tag = f"a/{label}/{rel}" if rel not in created else "/dev/null"
        b_tag = f"b/{label}/{rel}" if rel not in deleted else "/dev/null"

        if a_lines is None or b_lines is None:
            chunks.append(f"Binary or oversized file changed: {label}/{rel}\n")
            continue

        diff = list(difflib.unified_diff(a_lines, b_lines, fromfile=a_tag, tofile=b_tag))
        if diff:
            chunks.append("".join(diff))
    return "\n".join(chunks)


def clone_cow_directory(src: str, dst: str) -> None:
    """
    Cross-OS Copy-on-Write tree cloner:
    - Tier 1 (Linux Btrfs/XFS): `cp -a --reflink=auto`
    - Tier 2 (macOS APFS): `cp -R -p -c`
    - Tier 3 (Windows / Fallback POSIX): `shutil.copytree`
    """
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    if sys.platform.startswith("linux") and shutil.which("cp"):
        proc = subprocess.run(
            ["cp", "-a", "--reflink=auto", src, dst],
            capture_output=True,
            text=True,
            check=False,
        )
        if proc.returncode == 0:
            return
        shutil.rmtree(dst, ignore_errors=True)
    elif sys.platform == "darwin" and shutil.which("cp"):
        proc = subprocess.run(
            ["cp", "-R", "-p", "-c", src, dst],
            capture_output=True,
            text=True,
            check=False,
        )
        if proc.returncode == 0:
            return
        shutil.rmtree(dst, ignore_errors=True)
    shutil.copytree(
        src,
        dst,
        symlinks=True,
        ignore_dangling_symlinks=True,
        dirs_exist_ok=True,
    )


def run_in_bwrap(
    shell_cmd: str,
    cwd: str,
    target_binds: List[Tuple[str, str]],
    writable_dirs: List[str],
    timeout_sec: int,
    ro_binds: Optional[List[str]] = None,
) -> Tuple[int, str, str, bool]:
    """
    Cross-OS sandbox command runner:
    - Tier 1 (Linux with `bwrap`): Bubblewrap read-only rootfs + CoW bind mounts.
    - Tier 2/3 (macOS / Windows / fallback POSIX without `bwrap`): Executes inside the isolated
      CoW clone directory with `HOME`/`TMPDIR` redirected to an ephemeral sandbox scratch folder
      and target paths remapped to the CoW clone, paired with pre/post host SHA-256 verification.
    """
    if not shutil.which("bwrap") or not sys.platform.startswith("linux"):
        remapped_cmd = shell_cmd
        remapped_cwd = cwd
        for clone_dir, real_dir in target_binds:
            remapped_cmd = remapped_cmd.replace(real_dir, clone_dir)
            if os.path.abspath(cwd) == os.path.abspath(real_dir):
                remapped_cwd = clone_dir
        isolated_tmp = os.path.join(writable_dirs[0] if writable_dirs else os.path.dirname(remapped_cwd), "_sbx_tmp")
        os.makedirs(isolated_tmp, exist_ok=True)
        env = os.environ.copy()
        env["PYTHONDONTWRITEBYTECODE"] = "1"
        env["TMPDIR"] = isolated_tmp
        env["TEMP"] = isolated_tmp
        env["TMP"] = isolated_tmp
        env["AGY_SANDBOX_ACTIVE"] = "1"
        env["HOMUNCULUS_SANDBOX_ACTIVE"] = "1"
        cmd_arg = ["bash", "-c", remapped_cmd] if shutil.which("bash") else remapped_cmd
        try:
            proc = subprocess.run(
                cmd_arg,
                cwd=remapped_cwd,
                env=env,
                shell=not isinstance(cmd_arg, list),
                capture_output=True,
                text=True,
                timeout=timeout_sec,
                check=False,
            )
            return proc.returncode, proc.stdout, proc.stderr, False
        except subprocess.TimeoutExpired as exc:
            out = exc.stdout.decode("utf-8", errors="replace") if isinstance(exc.stdout, bytes) else (exc.stdout or "")
            err = exc.stderr.decode("utf-8", errors="replace") if isinstance(exc.stderr, bytes) else (exc.stderr or "")
            return 124, out, err + f"\n[TIMEOUT after {timeout_sec}s]", True

    bwrap_cmd: List[str] = [
        "bwrap",
        "--ro-bind", "/", "/",
        "--dev", "/dev",
        "--proc", "/proc",
        "--tmpfs", "/tmp",
        "--unshare-pid",
        "--die-with-parent",
    ]
    # Apply writable directory binds after `--ro-bind / /` and `--tmpfs /tmp`
    for clone_dir, real_dir in target_binds:
        bwrap_cmd.extend(["--bind", clone_dir, real_dir])
    for wdir in writable_dirs:
        bwrap_cmd.extend(["--bind", wdir, wdir])
    for rpath in (ro_binds or []):
        if rpath and os.path.exists(rpath):
            bwrap_cmd.extend(["--ro-bind", rpath, rpath])

    bwrap_cmd.extend([
        "--chdir", cwd,
        "--setenv", "PYTHONDONTWRITEBYTECODE", "1",
        "--setenv", "TMPDIR", "/tmp",
        "--setenv", "AGY_SANDBOX_ACTIVE", "1",
        "--setenv", "HOMUNCULUS_SANDBOX_ACTIVE", "1",
        "bash", "-c", shell_cmd,
    ])

    try:
        proc = subprocess.run(
            bwrap_cmd,
            capture_output=True,
            text=True,
            timeout=timeout_sec,
            check=False,
        )
        return proc.returncode, proc.stdout, proc.stderr, False
    except subprocess.TimeoutExpired as exc:
        out = exc.stdout.decode("utf-8", errors="replace") if isinstance(exc.stdout, bytes) else (exc.stdout or "")
        err = exc.stderr.decode("utf-8", errors="replace") if isinstance(exc.stderr, bytes) else (exc.stderr or "")
        return 124, out, err + f"\n[TIMEOUT after {timeout_sec}s]", True


def check_bwrap_available() -> Tuple[bool, str]:
    if shutil.which("bwrap") and sys.platform.startswith("linux"):
        proc = subprocess.run(
            ["bwrap", "--ro-bind", "/", "/", "--dev", "/dev", "--proc", "/proc", "--tmpfs", "/tmp", "true"],
            capture_output=True,
            text=True,
            check=False,
        )
        if proc.returncode == 0:
            return True, "ok (Tier-1 Linux Bubblewrap)"
    return True, f"ok (Cross-OS CoW fallback on {sys.platform})"


def _strip_json_arg(val: object) -> str:
    if not isinstance(val, str):
        return str(val or "")
    s = val.strip()
    if len(s) >= 2 and ((s[0] == '"' and s[-1] == '"') or (s[0] == "'" and s[-1] == "'")):
        s = s[1:-1].strip()
    return s


def resolve_transcript_path(raw_path_or_id: str) -> Optional[str]:
    if not raw_path_or_id:
        return None
    candidate = os.path.abspath(os.path.expanduser(raw_path_or_id.strip()))
    if os.path.isfile(candidate):
        if candidate.endswith("transcript.jsonl"):
            sibling_full = os.path.join(os.path.dirname(candidate), "transcript_full.jsonl")
            if os.path.isfile(sibling_full):
                return sibling_full
        return candidate
    raw_id = raw_path_or_id.strip()
    if UUID_RE.match(raw_id):
        brain_full = os.path.join(
            DEFAULT_BRAIN_ROOT, raw_id, ".system_generated", "logs", "transcript_full.jsonl"
        )
        if os.path.isfile(brain_full):
            return brain_full
        brain_candidate = os.path.join(
            DEFAULT_BRAIN_ROOT, raw_id, ".system_generated", "logs", "transcript.jsonl"
        )
        if os.path.isfile(brain_candidate):
            return brain_candidate
        if os.path.isdir(DEFAULT_CLAUDE_PROJECTS_ROOT):
            for dirpath, _, filenames in os.walk(DEFAULT_CLAUDE_PROJECTS_ROOT):
                for fn in filenames:
                    if fn in (f"{raw_id}.jsonl", f"{raw_id}.json"):
                        return os.path.join(dirpath, fn)
    return None


def parse_transcript_telemetry(transcript_path: str) -> Dict[str, object]:
    """Parse an Antigravity, Claude Code, or generic JSON/JSONL subagent transcript into token, turn, and tool-call metrics."""
    planner_turns = 0
    input_tokens = 0
    cache_read_tokens = 0
    output_tokens = 0
    timestamps: List[dt.datetime] = []
    tool_counts: Dict[str, int] = {}
    skill_files_read: List[str] = []
    py_oracles_read: List[str] = []
    accessed_paths: List[str] = []
    ls_find_probes = 0
    verification_cmds = 0
    py_snoop_cmds = 0
    adhoc_cad_snoop_cmds = 0
    archive_raw_dump_cmds = 0

    def _record_tool_call(raw_name: str, raw_args: object) -> None:
        nonlocal ls_find_probes, verification_cmds, py_snoop_cmds, adhoc_cad_snoop_cmds, archive_raw_dump_cmds
        tname = str(raw_name or "unknown").replace("default_api:", "")
        if tname.lower() == "bash":
            tname = "run_command"
        elif tname.lower() in ("read", "view_file"):
            tname = "read_file"
        tool_counts[tname] = tool_counts.get(tname, 0) + 1
        targs = raw_args
        if isinstance(targs, str):
            try:
                targs = json.loads(targs)
            except Exception:
                targs = {}
        if not isinstance(targs, dict):
            return
        if tname == "read_file":
            p_str = _strip_json_arg(
                targs.get("Path") or targs.get("AbsolutePath") or targs.get("file_path") or ""
            )
            if p_str:
                accessed_paths.append(p_str)
            if p_str.lower().endswith((".step", ".stp", ".stl", ".3mf", ".iges", ".fcstd")):
                adhoc_cad_snoop_cmds += 1
            if p_str.lower().endswith("_lessons_archive.md"):
                st_l = targs.get("StartLine")
                en_l = targs.get("EndLine")
                try:
                    valid_win = (st_l is not None and en_l is not None and 0 <= (int(en_l) - int(st_l)) <= 30)
                except (TypeError, ValueError):
                    valid_win = False
                if not valid_win:
                    archive_raw_dump_cmds += 1
            if p_str.endswith("SKILL.md") and p_str not in skill_files_read:
                skill_files_read.append(p_str)
            elif p_str.endswith(".py") and p_str not in py_oracles_read:
                py_oracles_read.append(p_str)
        elif tname == "run_command":
            cmd_line = _strip_json_arg(targs.get("CommandLine") or targs.get("command") or "")
            if cmd_line:
                accessed_paths.append(cmd_line)
            if LS_FIND_CMD_RE.search(cmd_line):
                ls_find_probes += 1
            if ADHOC_CAD_SNOOP_RE.search(cmd_line):
                adhoc_cad_snoop_cmds += 1
            for m_sk in re.finditer(r"([A-Za-z0-9_./~-]+/SKILL\.md)\b", cmd_line):
                sk_p = os.path.expanduser(m_sk.group(1))
                if sk_p not in skill_files_read:
                    skill_files_read.append(sk_p)
            if SHELL_PY_SNOOP_RE.search(cmd_line):
                py_snoop_cmds += 1
            elif ORACLE_EXEC_CMD_RE.search(cmd_line):
                verification_cmds += 1

    with open(transcript_path, "r", encoding="utf-8", errors="replace") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                continue
            ts_str = obj.get("created_at") or obj.get("timestamp")
            if isinstance(ts_str, str) and ts_str:
                try:
                    timestamps.append(dt.datetime.fromisoformat(ts_str.replace("Z", "+00:00")))
                except ValueError:
                    pass
            if obj.get("type") == "PLANNER_RESPONSE":
                planner_turns += 1
                input_tokens += int(obj.get("input_tokens") or 0)
                cache_read_tokens += int(obj.get("cache_read_tokens") or 0)
                output_tokens += int(obj.get("output_tokens") or 0)
                for tc in obj.get("tool_calls") or []:
                    if not isinstance(tc, dict):
                        continue
                    raw_tname = tc.get("name") or (tc.get("function") or {}).get("name") or "unknown"
                    raw_targs = (
                        tc.get("args")
                        or tc.get("arguments")
                        or (tc.get("function") or {}).get("arguments")
                        or {}
                    )
                    _record_tool_call(str(raw_tname), raw_targs)
            elif obj.get("type") == "assistant" and isinstance(obj.get("message"), dict):
                planner_turns += 1
                msg = obj["message"]
                usage = msg.get("usage") or {}
                input_tokens += int(usage.get("input_tokens") or 0)
                cache_read_tokens += int(usage.get("cache_read_input_tokens") or 0)
                output_tokens += int(usage.get("output_tokens") or 0)
                for blk in msg.get("content") or []:
                    if isinstance(blk, dict) and blk.get("type") == "tool_use":
                        _record_tool_call(str(blk.get("name") or "unknown"), blk.get("input") or {})

    wall_clock_sec = 0.0
    if len(timestamps) >= 2:
        wall_clock_sec = round(max(0.0, (max(timestamps) - min(timestamps)).total_seconds()), 2)

    return {
        "transcript_path": transcript_path,
        "planner_turns": planner_turns,
        "input_tokens": input_tokens,
        "cache_read_tokens": cache_read_tokens,
        "output_tokens": output_tokens,
        "total_billed_tokens": input_tokens + cache_read_tokens + output_tokens,
        "wall_clock_sec": wall_clock_sec,
        "tool_counts": tool_counts,
        "skill_files_read": skill_files_read,
        "py_oracles_read": py_oracles_read,
        "accessed_paths": accessed_paths,
        "ls_find_probes": ls_find_probes,
        "verification_cmds": verification_cmds,
        "py_snoop_cmds": py_snoop_cmds,
        "adhoc_cad_snoop_cmds": adhoc_cad_snoop_cmds,
        "archive_raw_dump_cmds": archive_raw_dump_cmds,
    }


def _resolve_overlay_path(real_path: str, target_binds: List[Tuple[str, str]]) -> str:
    abs_p = os.path.abspath(real_path)
    for clone_dir, real_dir in target_binds:
        if abs_p == real_dir:
            return clone_dir
        if abs_p.startswith(real_dir.rstrip(os.sep) + os.sep):
            rel = os.path.relpath(abs_p, real_dir)
            return os.path.join(clone_dir, rel)
    return abs_p


def _collect_md_files(root_dir: str) -> List[str]:
    rels: List[str] = []
    for dirpath, dirnames, filenames in os.walk(root_dir, topdown=True):
        dirnames[:] = sorted(d for d in dirnames if d not in SKIP_WALK_DIRS)
        for fn in sorted(filenames):
            if fn.lower().endswith(".md"):
                full = os.path.join(dirpath, fn)
                rels.append(os.path.relpath(full, root_dir))
    return sorted(rels)


def _audit_arm_deliverables(
    arm_dir: str,
    rel_files: List[str],
    compare_sources: List[str],
    repo_root: str,
    cwd: str,
    target_binds: List[Tuple[str, str]],
    writable_dirs: List[str],
    timeout_sec: int,
    vrf_receipts_out: List[str],
) -> Dict[str, Dict[str, object]]:
    import shlex

    results: Dict[str, Dict[str, object]] = {}
    batch_vrf_map: Dict[str, Dict[str, object]] = {}
    if not target_binds and compare_sources and len(rel_files) > 1 and os.path.isfile(DEFAULT_VERIFY_CLAIMS_SCRIPT):
        try:
            vc_dir = os.path.dirname(DEFAULT_VERIFY_CLAIMS_SCRIPT)
            if vc_dir not in sys.path:
                sys.path.insert(0, vc_dir)
            import verify_claims as _vc_batch  # noqa: E402

            abs_targets = [os.path.join(arm_dir, r) for r in rel_files]
            batch_vrf_map = _vc_batch.verify_multiple_targets_inprocess(
                target_paths=abs_targets,
                sources=list(compare_sources),
            )
        except Exception:
            batch_vrf_map = {}

    for rel in rel_files:
        abs_f = os.path.join(arm_dir, rel)
        host_f = _resolve_overlay_path(abs_f, target_binds)
        try:
            with open(host_f, "r", encoding="utf-8", errors="replace") as f:
                text = f.read()
        except OSError:
            text = ""
        tbd_tags = TBD_TAG_RE.findall(text)
        conflict_tags = CONFLICT_TBD_RE.findall(text)

        extra_ro = [
            p for p in ([repo_root] + list(compare_sources))
            if p and p.startswith("/tmp/") and os.path.exists(p)
        ]

        # 1. Run audit_repo_docs.py
        doc_rc = 0
        doc_lb_issues: List[str] = []
        if os.path.isfile(DEFAULT_AUDIT_DOCS_SCRIPT):
            repo_root_arg = f"--repo-root {shlex.quote(repo_root)} " if repo_root else ""
            doc_cmd = f"python3 {shlex.quote(DEFAULT_AUDIT_DOCS_SCRIPT)} {repo_root_arg}{shlex.quote(abs_f)}"
            doc_rc, d_out, d_err, _ = run_in_bwrap(
                shell_cmd=doc_cmd,
                cwd=cwd,
                target_binds=target_binds,
                writable_dirs=writable_dirs,
                timeout_sec=timeout_sec,
                ro_binds=extra_ro,
            )
            for line in (d_out + "\n" + d_err).splitlines():
                if "[LOAD-BEARING]" in line:
                    doc_lb_issues.append(line.strip())

        # 2. Run verify_claims.py if --compare-source provided (using shared SourceIndex batch when available)
        vrf_rc = 0
        unbacked_count = 0
        supported_count = 0
        vrf_id = ""
        if abs_f in batch_vrf_map:
            v_obj = batch_vrf_map[abs_f]
            unbacked_count = int(v_obj.get("unbacked_count", 0))
            supported_count = int(v_obj.get("supported_count", 0))
            vrf_id = str(v_obj.get("vrf_token") or "")
            vrf_rc = 1 if unbacked_count > 0 else 0
            if vrf_id and vrf_id not in vrf_receipts_out:
                vrf_receipts_out.append(vrf_id)
        elif compare_sources and os.path.isfile(DEFAULT_VERIFY_CLAIMS_SCRIPT):
            srcs_quoted = " ".join(shlex.quote(s) for s in compare_sources)
            vrf_cmd = (
                f"python3 {shlex.quote(DEFAULT_VERIFY_CLAIMS_SCRIPT)} "
                f"--target {shlex.quote(abs_f)} --sources {srcs_quoted} --skip-freshness-check --json"
            )
            vrf_rc, v_out, v_err, _ = run_in_bwrap(
                shell_cmd=vrf_cmd,
                cwd=cwd,
                target_binds=target_binds,
                writable_dirs=writable_dirs,
                timeout_sec=timeout_sec,
                ro_binds=extra_ro,
            )
            try:
                v_obj = json.loads(v_out)
                unbacked_count = int(
                    v_obj.get("unbacked_count", v_obj.get("unbacked_claims_count", len(v_obj.get("unbacked_claims", []))))
                )
                supported_count = int(v_obj.get("supported_count", v_obj.get("supported_claims_count", 0)))
                vrf_id = str(v_obj.get("vrf_token") or v_obj.get("verification_receipt") or "")
                if vrf_id and vrf_id not in vrf_receipts_out:
                    vrf_receipts_out.append(vrf_id)
            except json.JSONDecodeError:
                for m_vrf in VRF_RE.findall(v_out + "\n" + v_err):
                    vrf_id = m_vrf
                    if m_vrf not in vrf_receipts_out:
                        vrf_receipts_out.append(m_vrf)

        results[rel] = {
            "rel_path": rel,
            "open_tbd_count": len(tbd_tags),
            "conflict_tbd_count": len(conflict_tags),
            "tbd_tags": tbd_tags,
            "doc_audit_rc": doc_rc,
            "doc_load_bearing_issues": doc_lb_issues,
            "verify_claims_rc": vrf_rc,
            "unbacked_claims": unbacked_count,
            "supported_claims": supported_count,
            "vrf_receipt": vrf_id,
        }
    return results


def evaluate_ab_comparison(
    blind_dir: str,
    visible_dir: str,
    blind_transcript: Optional[str],
    visible_transcript: Optional[str],
    compare_sources: List[str],
    repo_root: str,
    cwd: str,
    target_binds: List[Tuple[str, str]],
    writable_dirs: List[str],
    timeout_sec: int,
    vrf_receipts_out: List[str],
) -> Tuple[Dict[str, object], str, List[str], bool]:
    """
    Compare `Blind` (Zero-Coaching) vs. `Visible` (Co-Engineered) sandbox outputs and
    subagent trajectories deterministically.
    """
    blind_host_dir = _resolve_overlay_path(blind_dir, target_binds)
    visible_host_dir = _resolve_overlay_path(visible_dir, target_binds)
    blind_rels = _collect_md_files(blind_host_dir)
    visible_rels = _collect_md_files(visible_host_dir)
    shared_rels = sorted(set(blind_rels) & set(visible_rels))
    only_blind = sorted(set(blind_rels) - set(visible_rels))
    only_visible = sorted(set(visible_rels) - set(blind_rels))

    blind_files = _audit_arm_deliverables(
        blind_dir, blind_rels, compare_sources, repo_root, cwd, target_binds, writable_dirs, timeout_sec, vrf_receipts_out
    )
    visible_files = _audit_arm_deliverables(
        visible_dir, visible_rels, compare_sources, repo_root, cwd, target_binds, writable_dirs, timeout_sec, vrf_receipts_out
    )

    ab_tags: List[str] = []
    file_deltas: List[Dict[str, object]] = []
    advisories: List[str] = []

    if only_blind or only_visible:
        ab_tags.append("MISSING_DELIVERABLE_PARITY")
        advisories.append(
            f"Deliverable parity mismatch: only_in_blind={only_blind}, only_in_visible={only_visible}"
        )

    for rel in shared_rels:
        b = blind_files[rel]
        v = visible_files[rel]
        b_doc_ok = b["doc_audit_rc"] == 0
        v_doc_ok = v["doc_audit_rc"] == 0
        b_vrf_ok = b["verify_claims_rc"] == 0
        v_vrf_ok = v["verify_claims_rc"] == 0
        b_tbd = int(b["open_tbd_count"])
        v_tbd = int(v["open_tbd_count"])
        b_conf = int(b["conflict_tbd_count"])
        v_conf = int(v["conflict_tbd_count"])

        row_flags: List[str] = []
        if (not b_doc_ok and v_doc_ok) or (not b_vrf_ok and v_vrf_ok):
            row_flags.append("COACHING_MASKED_DEFECT")
            if "COACHING_MASKED_DEFECT" not in ab_tags:
                ab_tags.append("COACHING_MASKED_DEFECT")
            if "ACCURACY_DRIFT" not in ab_tags:
                ab_tags.append("ACCURACY_DRIFT")
        elif not b_doc_ok or not v_doc_ok:
            row_flags.append("DOC_AUDIT_FAIL")
            if "LOGIC_DEFECT" not in ab_tags:
                ab_tags.append("LOGIC_DEFECT")
        elif not b_vrf_ok or not v_vrf_ok:
            row_flags.append("VERIFY_CLAIMS_FAIL")
            if "ACCURACY_DRIFT" not in ab_tags:
                ab_tags.append("ACCURACY_DRIFT")

        if b_tbd < v_tbd or b_conf < v_conf:
            row_flags.append(f"QUALITATIVE_DODGING_TBD_DEFICIT(Blind={b_tbd}/Conf={b_conf} vs Vis={v_tbd}/Conf={v_conf})")
            if "QUALITATIVE_DODGING_TBD_DEFICIT" not in ab_tags:
                ab_tags.append("QUALITATIVE_DODGING_TBD_DEFICIT")
            if "ACCURACY_DRIFT" not in ab_tags:
                ab_tags.append("ACCURACY_DRIFT")

        file_deltas.append({
            "file": rel,
            "blind_doc_rc": b["doc_audit_rc"],
            "visible_doc_rc": v["doc_audit_rc"],
            "blind_vrf_rc": b["verify_claims_rc"],
            "visible_vrf_rc": v["verify_claims_rc"],
            "blind_unbacked": b["unbacked_claims"],
            "visible_unbacked": v["unbacked_claims"],
            "blind_open_tbd": b_tbd,
            "visible_open_tbd": v_tbd,
            "blind_conflict_tbd": b_conf,
            "visible_conflict_tbd": v_conf,
            "blind_load_bearing_issues": b["doc_load_bearing_issues"],
            "visible_load_bearing_issues": v["doc_load_bearing_issues"],
            "flags": row_flags,
        })

    blind_tel = parse_transcript_telemetry(blind_transcript) if blind_transcript else None
    visible_tel = parse_transcript_telemetry(visible_transcript) if visible_transcript else None
    trajectory_delta: Dict[str, object] = {}
    if blind_tel and visible_tel:
        b_skills = list(blind_tel["skill_files_read"])
        v_skills = list(visible_tel["skill_files_read"])
        b_ls = int(blind_tel["ls_find_probes"])
        v_ls = int(visible_tel["ls_find_probes"])
        b_accessed = " ".join(str(x) for x in blind_tel.get("accessed_paths", []))
        v_accessed = " ".join(str(x) for x in visible_tel.get("accessed_paths", []))
        vis_base = os.path.basename(visible_dir.rstrip(os.sep))
        blind_base = os.path.basename(blind_dir.rstrip(os.sep))
        if (visible_dir in b_accessed) or (vis_base and f"/{vis_base}" in b_accessed):
            if "CROSS_ARM_CONTAMINATION" not in ab_tags:
                ab_tags.append("CROSS_ARM_CONTAMINATION")
            advisories.append(
                f"CROSS_ARM_CONTAMINATION: Blind arm transcript accessed Visible output path (`{vis_base}`)."
            )
        if (blind_dir in v_accessed) or (blind_base and f"/{blind_base}" in v_accessed):
            if "CROSS_ARM_CONTAMINATION" not in ab_tags:
                ab_tags.append("CROSS_ARM_CONTAMINATION")
            advisories.append(
                f"CROSS_ARM_CONTAMINATION: Visible arm transcript accessed Blind output path (`{blind_base}`)."
            )
        pointer_hop = len(b_skills) >= 2 or len(v_skills) >= 2
        if pointer_hop:
            advisories.append(
                f"POINTER_HOP_DETECTED: Blind read {len(b_skills)} SKILL.md files; Visible read {len(v_skills)} SKILL.md files."
            )
        b_py_snoops = len(blind_tel.get("py_oracles_read", [])) + int(blind_tel.get("py_snoop_cmds", 0))
        v_py_snoops = len(visible_tel.get("py_oracles_read", [])) + int(visible_tel.get("py_snoop_cmds", 0))
        if b_ls - v_ls >= 2:
            advisories.append(
                f"CLI_ERGONOMICS_GAP: Blind executed {b_ls} ls/find/listdir probes vs {v_ls} in Visible (+{b_ls - v_ls} path-discovery turns)."
            )
        if b_py_snoops > 0 or v_py_snoops > 0:
            advisories.append(
                f"PY_SOURCE_SNOOPING_DETECTED: Blind read/snooped .py scripts {b_py_snoops} times; Visible {v_py_snoops} times."
            )
        trajectory_delta = {
            "blind_turns": blind_tel["planner_turns"],
            "visible_turns": visible_tel["planner_turns"],
            "turn_delta_blind_minus_visible": int(blind_tel["planner_turns"]) - int(visible_tel["planner_turns"]),
            "blind_total_tokens": blind_tel["total_billed_tokens"],
            "visible_total_tokens": visible_tel["total_billed_tokens"],
            "blind_wall_clock_sec": blind_tel["wall_clock_sec"],
            "visible_wall_clock_sec": visible_tel["wall_clock_sec"],
            "blind_skill_files_read": b_skills,
            "visible_skill_files_read": v_skills,
            "blind_ls_find_probes": b_ls,
            "visible_ls_find_probes": v_ls,
            "blind_py_snoops": b_py_snoops,
            "visible_py_snoops": v_py_snoops,
            "pointer_hop_detected": pointer_hop,
        }

    ab_pass = (len(ab_tags) == 0) and (len(shared_rels) > 0)

    # Build Markdown comparison table
    md_lines = [
        "# Blind vs. Visible Differential Sandbox Comparison (`ab_comparison.md`)",
        "",
        f"- **Overall Differential Verdict:** `{'PASS (PARITY)' if ab_pass else 'DIVERGENCE / DEFECT DETECTED'}`",
        f"- **Blind Output Directory:** `{blind_dir}` (`{len(blind_rels)}` `.md` files)",
        f"- **Visible Output Directory:** `{visible_dir}` (`{len(visible_rels)}` `.md` files)",
        f"- **Failure / Divergence Tags:** `{', '.join(ab_tags) if ab_tags else 'NONE'}`",
        "",
        "## 1. Per-Deliverable Oracle & `[TBD]` Parity Matrix",
        "",
        "| Deliverable | `Blind` Doc Audit | `Visible` Doc Audit | `Blind` Claims (`Unbacked`) | `Visible` Claims (`Unbacked`) | `Blind` Open `[TBD]` (`CONFLICT`) | `Visible` Open `[TBD]` (`CONFLICT`) | Differential Verdict |",
        "| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :--- |",
    ]
    for fd in file_deltas:
        b_doc_s = "PASS" if fd["blind_doc_rc"] == 0 else f"FAIL ({len(fd['blind_load_bearing_issues'])})"
        v_doc_s = "PASS" if fd["visible_doc_rc"] == 0 else f"FAIL ({len(fd['visible_load_bearing_issues'])})"
        b_vrf_s = f"{'PASS' if fd['blind_vrf_rc'] == 0 else 'FAIL'} ({fd['blind_unbacked']})"
        v_vrf_s = f"{'PASS' if fd['visible_vrf_rc'] == 0 else 'FAIL'} ({fd['visible_unbacked']})"
        b_tbd_s = f"{fd['blind_open_tbd']} ({fd['blind_conflict_tbd']})"
        v_tbd_s = f"{fd['visible_open_tbd']} ({fd['visible_conflict_tbd']})"
        flag_s = ", ".join(fd["flags"]) if fd["flags"] else "PARITY_OK"
        md_lines.append(
            f"| `{fd['file']}` | `{b_doc_s}` | `{v_doc_s}` | `{b_vrf_s}` | `{v_vrf_s}` | `{b_tbd_s}` | `{v_tbd_s}` | `{flag_s}` |"
        )
        for iss in fd["blind_load_bearing_issues"]:
            md_lines.append(f"  - **Blind Load-Bearing Issue (`{fd['file']}`):** `{iss}`")
        for iss in fd["visible_load_bearing_issues"]:
            md_lines.append(f"  - **Visible Load-Bearing Issue (`{fd['file']}`):** `{iss}`")

    if blind_tel and visible_tel:
        md_lines.extend([
            "",
            "## 2. Subagent Trajectory & Token/Turn Telemetry",
            "",
            "| Metric | `Blind` Arm (Zero-Coaching) | `Visible` Arm (Co-Engineered) | Delta (`Blind - Visible`) |",
            "| :--- | :---: | :---: | :---: |",
            f"| **Planner Turns** | `{blind_tel['planner_turns']}` | `{visible_tel['planner_turns']}` | `{trajectory_delta['turn_delta_blind_minus_visible']:+d}` |",
            f"| **Total Billed Tokens (`In + Cache + Out`)** | `{blind_tel['total_billed_tokens']:,}` | `{visible_tel['total_billed_tokens']:,}` | `{int(blind_tel['total_billed_tokens']) - int(visible_tel['total_billed_tokens']):+,}` |",
            f"| **Wall-Clock Duration (`s`)** | `{blind_tel['wall_clock_sec']}s` | `{visible_tel['wall_clock_sec']}s` | `{round(float(blind_tel['wall_clock_sec']) - float(visible_tel['wall_clock_sec']), 2):+.2f}s` |",
            f"| **`SKILL.md` Files Read** | `{len(blind_tel['skill_files_read'])}` | `{len(visible_tel['skill_files_read'])}` | `{len(blind_tel['skill_files_read']) - len(visible_tel['skill_files_read']):+d}` |",
            f"| **`ls` / `find` / `listdir` Probes** | `{blind_tel['ls_find_probes']}` | `{visible_tel['ls_find_probes']}` | `{int(blind_tel['ls_find_probes']) - int(visible_tel['ls_find_probes']):+d}` |",
            f"| **`.py` Source Reads / Snoops** | `{trajectory_delta['blind_py_snoops']}` | `{trajectory_delta['visible_py_snoops']}` | `{int(trajectory_delta['blind_py_snoops']) - int(trajectory_delta['visible_py_snoops']):+d}` |",
            f"| **Verification CLI Runs** | `{blind_tel['verification_cmds']}` | `{visible_tel['verification_cmds']}` | `{int(blind_tel['verification_cmds']) - int(visible_tel['verification_cmds']):+d}` |",
        ])

    if advisories:
        md_lines.extend(["", "## 3. Actionable Skill / Rule Hygiene Insights", ""])
        for adv in advisories:
            md_lines.append(f"- {adv}")

    summary_obj: Dict[str, object] = {
        "passed": ab_pass,
        "blind_dir": blind_dir,
        "visible_dir": visible_dir,
        "shared_files": shared_rels,
        "only_in_blind": only_blind,
        "only_in_visible": only_visible,
        "file_deltas": file_deltas,
        "blind_telemetry": blind_tel,
        "visible_telemetry": visible_tel,
        "trajectory_delta": trajectory_delta,
        "advisories": advisories,
        "divergence_tags": ab_tags,
    }
    return summary_obj, "\n".join(md_lines) + "\n", ab_tags, ab_pass


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Deterministic Bubblewrap + Btrfs CoW Sandbox Runner (`engineering-sandbox`)."
    )
    parser.add_argument(
        "--mode",
        choices=VALID_MODES,
        default="dry-run",
        help="Sandbox frame label recorded in diagnostic telemetry (default: dry-run).",
    )
    parser.add_argument(
        "--target-dir",
        "--workspace",
        action="append",
        default=[],
        dest="target_dirs",
        help="Real directory to CoW-clone and bind-mount over its original path inside the sandbox (repeatable; aliased as --workspace).",
    )
    parser.add_argument(
        "--writable-dir",
        action="append",
        default=[],
        dest="writable_dirs",
        help="Optional scratch/output directory on host to bind writable inside the sandbox (repeatable).",
    )
    parser.add_argument(
        "--cwd",
        default="",
        help="Working directory inside the sandbox (default: first --target-dir / --workspace, or current working directory).",
    )
    parser.add_argument(
        "--spec",
        default="",
        help="Optional JSON sandbox specification file containing `controls` and `faults` arrays.",
    )
    parser.add_argument(
        "--faults",
        action="store_true",
        help="Enable execution of `faults` entries loaded from `--spec` (or `--fault-case` flags).",
    )
    parser.add_argument(
        "--cmd",
        action="append",
        default=[],
        dest="cmds",
        help=(
            "Control command expected to succeed (`exit 0`). Multiple `--cmd` flags run "
            "SEQUENTIALLY inside the SAME shared CoW overlay so edits in CMD 1 persist into CMD 2/3."
        ),
    )
    parser.add_argument(
        "--fault-case",
        action="append",
        default=[],
        dest="fault_cases",
        help=(
            "Adversarial `+faults` probe run in its OWN fresh untouched CoW clone of `--target-dir` "
            "(isolated from `--cmd` edits). Format: '<setup_cmd> :: <validator_cmd>' "
            "(setup must exit 0 and mutate >=1 target/writable file; validator must exit != 0) "
            "or '<validator_cmd>' (must exit != 0)."
        ),
    )
    parser.add_argument(
        "--allow-noop-setup",
        action="store_true",
        help="Allow `<setup_cmd> :: <validator_cmd>` fault cases whose setup_cmd mutates 0 files.",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=120,
        help="Timeout in seconds per command execution (default: 120).",
    )
    parser.add_argument(
        "--report-dir",
        default="",
        help="Directory for forensic bundle (`report.json`, `mutations.diff`, `stdout.log`, `stderr.log`).",
    )
    parser.add_argument(
        "--keep-overlay",
        "--keep-failed-cow",
        dest="keep_overlay",
        action="store_true",
        help="Retain CoW cloned directories on disk after completion for manual inspection (aliased as --keep-failed-cow).",
    )
    parser.add_argument(
        "--blind-dir",
        default="",
        help="Scratch/output directory containing `Blind` arm deliverables (`compare-light` / `compare-full`).",
    )
    parser.add_argument(
        "--visible-dir",
        default="",
        help="Scratch/output directory containing `Visible` arm deliverables (`compare-light` / `compare-full`).",
    )
    parser.add_argument(
        "--blind-transcript",
        default="",
        help="Path or conversationId UUID for the `Blind` subagent `transcript.jsonl`.",
    )
    parser.add_argument(
        "--visible-transcript",
        default="",
        help="Path or conversationId UUID for the `Visible` subagent `transcript.jsonl`.",
    )
    parser.add_argument(
        "--compare-source",
        action="append",
        default=[],
        dest="compare_sources",
        help="Authoritative source file/dir passed to `verify_claims.py` during A/B comparison (repeatable).",
    )
    parser.add_argument(
        "--repo-root",
        default="",
        help="Repository root passed to `audit_repo_docs.py --repo-root` during A/B deliverable comparison.",
    )
    parser.add_argument(
        "--prepare",
        action="store_true",
        help=(
            "Run Pre-Sandbox Gate 0 only (~1.7ms cached / ~25ms write-if-changed): ensure `<memory_root>/Directory/*.md` "
            "and `AUTO-TREE` reflect all uncommitted workspace file changes before spawning `Blind`/`Visible`/`Compare-*` subagents."
        ),
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print full JSON report to stdout instead of the compact 5-block summary.",
    )
    args = parser.parse_args()

    if args.prepare or args.mode == "prepare":
        prep_targets = list(args.target_dirs) or ([args.repo_root] if args.repo_root else []) or [args.cwd or os.getcwd()]
        seen_mem: set[str] = set()
        prep_records: List[Dict[str, object]] = []
        for raw_pt in prep_targets:
            abs_pt = os.path.abspath(os.path.expanduser(raw_pt))
            if not os.path.isdir(abs_pt):
                continue
            res = homunculus_paths.ensure_directory_fresh(
                workspace_dir=abs_pt,
                homunculus_root=HOMUNCULUS_ROOT,
            )
            m_key = str(res.get("memory_root", abs_pt))
            if m_key not in seen_mem:
                seen_mem.add(m_key)
                prep_records.append(res)
        if args.json:
            print(json.dumps({"mode": "prepare", "results": prep_records}, indent=2))
        else:
            for r in prep_records:
                print(
                    f"[PRE_SANDBOX_GATE] Status: {r.get('status', 'OK')} | "
                    f"Synced: {r.get('synced', False)} | "
                    f"Memory: {r.get('memory_root', 'none')}"
                )
        return 0

    control_expectations: Dict[int, Dict[str, object]] = {}
    fault_expectations: Dict[int, Dict[str, object]] = {}
    if args.spec:
        spec_path = os.path.abspath(os.path.expanduser(args.spec))
        if not os.path.isfile(spec_path):
            print(f"[EXTRACTION BLOCKED — ABORTED] --spec file not found: {spec_path}", file=sys.stderr)
            return 2
        try:
            with open(spec_path, "r", encoding="utf-8") as f:
                spec_obj = json.load(f)
        except Exception as exc:
            print(f"[EXTRACTION BLOCKED — ABORTED] Invalid JSON in --spec {spec_path}: {exc}", file=sys.stderr)
            return 2
        def _norm_cmd(val: object) -> str:
            if isinstance(val, list):
                return shlex.join(str(x) for x in val)
            return str(val or "")

        for ctrl in spec_obj.get("controls") or []:
            raw_c = _norm_cmd(ctrl.get("cmd")) if isinstance(ctrl, dict) else _norm_cmd(ctrl)
            if raw_c:
                args.cmds.append(raw_c.replace("<HOMUNCULUS_ROOT>", HOMUNCULUS_ROOT))
                if isinstance(ctrl, dict):
                    control_expectations[len(args.cmds)] = {
                        "expect_exit": ctrl.get("expect_exit"),
                        "expect_output_contains": ctrl.get("expect_output_contains"),
                    }
        for flt in spec_obj.get("faults") or []:
            if isinstance(flt, dict):
                raw_setup = flt.get("setup_cmd") or (flt.get("cmd") if flt.get("validator_cmd") else "")
                s_cmd = _norm_cmd(raw_setup).replace("<HOMUNCULUS_ROOT>", HOMUNCULUS_ROOT).strip()
                if not s_cmd and isinstance(flt.get("mutations"), list):
                    mut_stmts: List[str] = []
                    for m in flt["mutations"]:
                        if isinstance(m, dict) and m.get("file"):
                            f_q = repr(str(m["file"]))
                            c_q = repr(str(m.get("content", "")))
                            act = str(m.get("action", "append")).lower()
                            if act == "append":
                                mut_stmts.append(f"p=pathlib.Path({f_q}); p.write_text(p.read_text(encoding='utf-8')+{c_q}, encoding='utf-8')")
                            else:
                                mut_stmts.append(f"p=pathlib.Path({f_q}); p.write_text({c_q}, encoding='utf-8')")
                    if mut_stmts:
                        s_cmd = shlex.join(["python3", "-c", "import pathlib; " + "; ".join(mut_stmts)])
                v_cmd = _norm_cmd(flt.get("validator_cmd") or flt.get("cmd")).replace("<HOMUNCULUS_ROOT>", HOMUNCULUS_ROOT).strip()
                if v_cmd:
                    args.fault_cases.append(f"{s_cmd} :: {v_cmd}" if s_cmd else v_cmd)
                    fault_expectations[len(args.fault_cases)] = {
                        "expect_exit": flt.get("expect_exit"),
                        "expect_output_contains": flt.get("expect_output_contains"),
                    }
            elif isinstance(flt, str) and flt.strip():
                args.fault_cases.append(flt.replace("<HOMUNCULUS_ROOT>", HOMUNCULUS_ROOT).strip())
        if not args.target_dirs and spec_obj.get("workspace"):
            args.target_dirs.append(str(spec_obj["workspace"]))

    has_ab_dirs = bool(args.blind_dir and args.visible_dir)
    if not args.target_dirs:
        if has_ab_dirs:
            args.target_dirs.extend([args.blind_dir, args.visible_dir])
        elif args.repo_root:
            args.target_dirs.append(args.repo_root)
        else:
            args.target_dirs.append(os.getcwd())
    if not args.cwd:
        args.cwd = args.target_dirs[0]
    if args.mode in ("compare-light", "compare-full") and not has_ab_dirs:
        parser.error(f"--mode {args.mode} requires both `--blind-dir` and `--visible-dir`.")
    if bool(args.blind_dir) != bool(args.visible_dir):
        parser.error("`--blind-dir` and `--visible-dir` must be provided together.")
    if not args.cmds and not args.fault_cases and not has_ab_dirs:
        parser.error("At least one `--cmd`, `--fault-case`, or `--blind-dir`/`--visible-dir` pair must be provided.")

    ok_bwrap, bwrap_msg = check_bwrap_available()
    if not ok_bwrap:
        print(f"[EXTRACTION BLOCKED — ABORTED] Bubblewrap containment unavailable: {bwrap_msg}", file=sys.stderr)
        return 2

    blind_dir_abs = os.path.abspath(os.path.expanduser(args.blind_dir)) if args.blind_dir else ""
    visible_dir_abs = os.path.abspath(os.path.expanduser(args.visible_dir)) if args.visible_dir else ""
    if has_ab_dirs:
        if not os.path.isdir(blind_dir_abs):
            print(f"[EXTRACTION BLOCKED — ABORTED] --blind-dir does not exist: {blind_dir_abs}", file=sys.stderr)
            return 2
        if not os.path.isdir(visible_dir_abs):
            print(f"[EXTRACTION BLOCKED — ABORTED] --visible-dir does not exist: {visible_dir_abs}", file=sys.stderr)
            return 2

    blind_tx_path: Optional[str] = None
    visible_tx_path: Optional[str] = None
    if args.blind_transcript:
        blind_tx_path = resolve_transcript_path(args.blind_transcript)
        if not blind_tx_path:
            print(
                f"[EXTRACTION BLOCKED — ABORTED] --blind-transcript not found: {args.blind_transcript}",
                file=sys.stderr,
            )
            return 2
    if args.visible_transcript:
        visible_tx_path = resolve_transcript_path(args.visible_transcript)
        if not visible_tx_path:
            print(
                f"[EXTRACTION BLOCKED — ABORTED] --visible-transcript not found: {args.visible_transcript}",
                file=sys.stderr,
            )
            return 2

    compare_sources_abs: List[str] = [
        os.path.abspath(os.path.expanduser(s)) for s in args.compare_sources if s
    ]
    repo_root_abs = os.path.abspath(os.path.expanduser(args.repo_root)) if args.repo_root else ""

    # Deduplicate, validate, and prune nested child target_dirs so child overlays never mask parent CoW mounts
    raw_valid_targets: List[str] = []
    seen_targets = set()
    home_abs = os.path.abspath(os.path.expanduser("~"))
    cache_abs = os.path.abspath(DEFAULT_CACHE_ROOT)
    for raw_td in args.target_dirs:
        abs_td = os.path.abspath(os.path.expanduser(raw_td))
        if not os.path.isdir(abs_td):
            print(f"[EXTRACTION BLOCKED — ABORTED] --target-dir does not exist: {abs_td}", file=sys.stderr)
            return 2
        if abs_td == home_abs or cache_abs == abs_td or cache_abs.startswith(abs_td.rstrip(os.sep) + os.sep):
            print(
                f"[EXTRACTION BLOCKED — ABORTED] --target-dir cannot be $HOME or enclose the sandbox cache ({abs_td}); "
                "specify a project repository or memory directory via --target-dir.",
                file=sys.stderr,
            )
            return 2
        if abs_td not in seen_targets:
            seen_targets.add(abs_td)
            raw_valid_targets.append(abs_td)

    target_dirs: List[str] = []
    for abs_td in sorted(raw_valid_targets, key=lambda p: (len(p.rstrip(os.sep).split(os.sep)), p)):
        parent_match = next(
            (
                parent
                for parent in target_dirs
                if abs_td == parent or abs_td.startswith(parent.rstrip(os.sep) + os.sep)
            ),
            None,
        )
        if parent_match:
            print(
                f"[INFO] Coalescing nested --target-dir {abs_td} into parent CoW mount {parent_match}",
                file=sys.stderr,
            )
            continue
        target_dirs.append(abs_td)

    writable_dirs: List[str] = []
    for raw_wd in args.writable_dirs:
        abs_wd = os.path.abspath(os.path.expanduser(raw_wd))
        os.makedirs(abs_wd, exist_ok=True)
        writable_dirs.append(abs_wd)

    cwd = os.path.abspath(os.path.expanduser(args.cwd))
    if not os.path.isdir(cwd):
        print(f"[EXTRACTION BLOCKED — ABORTED] --cwd does not exist: {cwd}", file=sys.stderr)
        return 2

    ts = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
    short_id = uuid.uuid4().hex[:8]
    run_id = f"SBX-{ts}-{short_id}"

    report_dir = (
        os.path.abspath(os.path.expanduser(args.report_dir))
        if args.report_dir
        else os.path.join(DEFAULT_CACHE_ROOT, "runs", f"{ts}_{short_id}")
    )
    overlays_root = os.path.join(DEFAULT_CACHE_ROOT, "work", f"{ts}_{short_id}")
    os.makedirs(report_dir, exist_ok=True)
    os.makedirs(overlays_root, exist_ok=True)

    t0 = time.monotonic()

    # 0. Pre-Sandbox Directory & AUTO-TREE Freshness Gate (runs BEFORE host_pre SHA-256 baseline so Live Host Mutations == 0)
    seen_prep_dirs: set[str] = set()
    for probe_dir in (cwd, *target_dirs):
        if probe_dir and probe_dir not in seen_prep_dirs and os.path.isdir(probe_dir):
            seen_prep_dirs.add(probe_dir)
            homunculus_paths.ensure_directory_fresh(
                workspace_dir=probe_dir, homunculus_root=HOMUNCULUS_ROOT
            )

    # 1. Pre-run host baseline snapshots (to prove 0 live mutations)
    host_pre: Dict[str, Dict[str, Tuple[int, int, str]]] = {
        td: snapshot_tree_manifest(td, include_hashes=True) for td in target_dirs
    }

    all_stdout: List[str] = []
    all_stderr: List[str] = []
    vrf_receipts: List[str] = []
    erofs_hits: List[str] = []
    failure_tags: List[str] = []

    control_results: List[Dict[str, object]] = []
    mutation_records: Dict[str, Dict[str, List[str]]] = {}
    unified_diffs: List[str] = []
    ab_comparison_obj: Optional[Dict[str, object]] = None
    ab_markdown_str: str = ""
    ab_pass: bool = True

    try:
        # 2. Clone primary CoW overlays and execute `--cmd` sequence
        primary_overlay_dir = os.path.join(overlays_root, "primary")
        primary_binds: List[Tuple[str, str]] = []
        for idx, td in enumerate(target_dirs):
            clone_p = os.path.join(primary_overlay_dir, f"t{idx}_{os.path.basename(td)}")
            clone_cow_directory(td, clone_p)
            primary_binds.append((clone_p, td))

        for c_idx, cmd_str in enumerate(args.cmds, 1):
            rc, out, err, timed_out = run_in_bwrap(
                shell_cmd=cmd_str,
                cwd=cwd,
                target_binds=primary_binds,
                writable_dirs=writable_dirs,
                timeout_sec=args.timeout,
            )
            all_stdout.append(f"=== [CMD {c_idx}] (rc={rc}) {cmd_str} ===\n{out}")
            all_stderr.append(f"=== [CMD {c_idx}] (rc={rc}) {cmd_str} ===\n{err}")

            if rc == 0:
                for m_vrf in VRF_RE.findall(out + "\n" + err):
                    if m_vrf not in vrf_receipts:
                        vrf_receipts.append(m_vrf)
            for m_ro in EROFS_RE.findall(out + "\n" + err):
                hit = m_ro.strip()
                if hit not in erofs_hits:
                    erofs_hits.append(hit)

            c_exp = control_expectations.get(c_idx, {})
            exp_rc = c_exp.get("expect_exit", 0)
            exp_tokens_raw = c_exp.get("expect_output_contains")
            exp_tokens: List[str] = []
            if isinstance(exp_tokens_raw, str) and exp_tokens_raw.strip():
                exp_tokens = [exp_tokens_raw.strip()]
            elif isinstance(exp_tokens_raw, list):
                exp_tokens = [str(x).strip() for x in exp_tokens_raw if str(x).strip()]

            combined_c_out = out + "\n" + err
            rc_matches = (rc == int(exp_rc)) if exp_rc is not None else (rc == 0)
            tokens_match = all(tok in combined_c_out for tok in exp_tokens)
            c_passed = rc_matches and tokens_match and (not timed_out)

            control_results.append({
                "index": c_idx,
                "cmd": cmd_str,
                "returncode": rc,
                "timed_out": timed_out,
                "passed": c_passed,
            })
            if not c_passed:
                if erofs_hits and "PATH_ESCAPE_BLOCKED" not in failure_tags:
                    failure_tags.append("PATH_ESCAPE_BLOCKED")
                elif "UNBACKED CLAIMS DETECTED" in out and "ACCURACY_DRIFT" not in failure_tags:
                    failure_tags.append("ACCURACY_DRIFT")
                elif "LOGIC_DEFECT" not in failure_tags:
                    failure_tags.append("LOGIC_DEFECT")

        # 2b. Execute automated Blind vs. Visible A/B differential comparison if requested
        if has_ab_dirs:
            ab_comparison_obj, ab_markdown_str, ab_tags, ab_pass = evaluate_ab_comparison(
                blind_dir=blind_dir_abs,
                visible_dir=visible_dir_abs,
                blind_transcript=blind_tx_path,
                visible_transcript=visible_tx_path,
                compare_sources=compare_sources_abs,
                repo_root=repo_root_abs,
                cwd=cwd,
                target_binds=primary_binds,
                writable_dirs=writable_dirs,
                timeout_sec=args.timeout,
                vrf_receipts_out=vrf_receipts,
            )
            all_stdout.append(f"=== [AB_COMPARISON] (passed={ab_pass}) ===\n{ab_markdown_str}")
            for t in ab_tags:
                if t not in failure_tags:
                    failure_tags.append(t)

        # Compute mutations inside primary CoW overlays
        for clone_p, td in primary_binds:
            post_clone_manifest = snapshot_tree_manifest(clone_p, include_hashes=True)
            created, modified, deleted = diff_manifests(host_pre[td], post_clone_manifest)
            label = os.path.basename(td) or td
            mutation_records[td] = {
                "created": created,
                "modified": modified,
                "deleted": deleted,
            }
            if created or modified or deleted:
                udiff = build_unified_diff(label, td, clone_p, created, modified, deleted)
                if udiff:
                    unified_diffs.append(udiff)

        # 3. Execute `+faults` (`--fault-case`) probes, each in its own isolated CoW clone
        fault_results: List[Dict[str, object]] = []
        for f_idx, raw_fc in enumerate(args.fault_cases, 1):
            f_overlay_dir = os.path.join(overlays_root, f"fault_{f_idx}")
            f_binds: List[Tuple[str, str]] = []
            for idx, td in enumerate(target_dirs):
                f_clone = os.path.join(f_overlay_dir, f"t{idx}_{os.path.basename(td)}")
                clone_cow_directory(td, f_clone)
                f_binds.append((f_clone, td))

            inline_exp_tokens: List[str] = []
            fc_body = raw_fc
            if "@@" in fc_body:
                fc_body, inline_exp_str = [p.strip() for p in fc_body.rsplit("@@", 1)]
                if inline_exp_str:
                    inline_exp_tokens.append(inline_exp_str)

            if "::" in fc_body:
                setup_cmd, validator_cmd = [p.strip() for p in fc_body.split("::", 1)]
            else:
                setup_cmd, validator_cmd = "", fc_body.strip()

            setup_rc = 0
            w_pre_fault: Dict[str, Dict[str, Tuple[str, str]]] = {}
            if setup_cmd:
                for wd in writable_dirs:
                    if os.path.isdir(wd):
                        w_pre_fault[wd] = snapshot_tree_manifest(wd, include_hashes=True)
                setup_rc, s_out, s_err, _ = run_in_bwrap(
                    shell_cmd=setup_cmd,
                    cwd=cwd,
                    target_binds=f_binds,
                    writable_dirs=writable_dirs,
                    timeout_sec=args.timeout,
                )
                all_stdout.append(f"=== [FAULT {f_idx} SETUP] (rc={setup_rc}) {setup_cmd} ===\n{s_out}")
                all_stderr.append(f"=== [FAULT {f_idx} SETUP] (rc={setup_rc}) {setup_cmd} ===\n{s_err}")

            if setup_rc != 0:
                fault_results.append({
                    "index": f_idx,
                    "fault_case": raw_fc,
                    "setup_rc": setup_rc,
                    "validator_rc": None,
                    "caught": False,
                    "status": "FAULT_SETUP_ERROR",
                })
                if "FAULT_SETUP_ERROR" not in failure_tags:
                    failure_tags.append("FAULT_SETUP_ERROR")
                continue

            if setup_cmd and not args.allow_noop_setup:
                setup_mutations = 0
                for f_clone, td in f_binds:
                    f_post = snapshot_tree_manifest(f_clone, include_hashes=True)
                    fc, fm, fd = diff_manifests(host_pre[td], f_post)
                    setup_mutations += len(fc) + len(fm) + len(fd)
                for wd, pre_m in w_pre_fault.items():
                    if os.path.isdir(wd):
                        w_post = snapshot_tree_manifest(wd, include_hashes=True)
                        wc, wm, wd_del = diff_manifests(pre_m, w_post)
                        setup_mutations += len(wc) + len(wm) + len(wd_del)
                if setup_mutations == 0:
                    all_stderr.append(
                        f"=== [FAULT {f_idx} SETUP NO-OP] setup_cmd exited 0 without mutating any target/writable file ===\n"
                    )
                    fault_results.append({
                        "index": f_idx,
                        "fault_case": raw_fc,
                        "setup_rc": setup_rc,
                        "validator_rc": None,
                        "caught": False,
                        "status": "FAULT_SETUP_NOOP",
                    })
                    if "FAULT_SETUP_NOOP" not in failure_tags:
                        failure_tags.append("FAULT_SETUP_NOOP")
                    continue

            if validator_cmd == "@ab-compare" and has_ab_dirs:
                _, f_ab_md, f_ab_tags, f_ab_pass = evaluate_ab_comparison(
                    blind_dir=blind_dir_abs,
                    visible_dir=visible_dir_abs,
                    blind_transcript=blind_tx_path,
                    visible_transcript=visible_tx_path,
                    compare_sources=compare_sources_abs,
                    repo_root=repo_root_abs,
                    cwd=cwd,
                    target_binds=f_binds,
                    writable_dirs=writable_dirs,
                    timeout_sec=args.timeout,
                    vrf_receipts_out=[],
                )
                v_rc = 0 if f_ab_pass else 1
                v_out = f"tags={f_ab_tags}\n{f_ab_md}"
                v_err = ""
                v_to = False
            else:
                v_rc, v_out, v_err, v_to = run_in_bwrap(
                    shell_cmd=validator_cmd,
                    cwd=cwd,
                    target_binds=f_binds,
                    writable_dirs=writable_dirs,
                    timeout_sec=args.timeout,
                )
            all_stdout.append(f"=== [FAULT {f_idx} VALIDATOR] (rc={v_rc}) {validator_cmd} ===\n{v_out}")
            all_stderr.append(f"=== [FAULT {f_idx} VALIDATOR] (rc={v_rc}) {validator_cmd} ===\n{v_err}")

            f_exp = fault_expectations.get(f_idx, {})
            f_exp_rc = f_exp.get("expect_exit")
            f_exp_tokens_raw = f_exp.get("expect_output_contains")
            f_exp_tokens: List[str] = list(inline_exp_tokens)
            if isinstance(f_exp_tokens_raw, str) and f_exp_tokens_raw.strip():
                f_exp_tokens.append(f_exp_tokens_raw.strip())
            elif isinstance(f_exp_tokens_raw, list):
                f_exp_tokens.extend(str(x).strip() for x in f_exp_tokens_raw if str(x).strip())

            combined_f_out = v_out + "\n" + v_err
            crash_markers = (
                "error: unrecognized arguments:",
                "error: the following arguments are required:",
                "Traceback (most recent call last):",
                "SyntaxError:",
                "can't open file",
            )
            validator_crashed = any(
                cm in v_err and not any(cm in tok for tok in f_exp_tokens)
                for cm in crash_markers
            )
            rc_caught = (v_rc != 0) and (not v_to) and (not validator_crashed)
            if rc_caught and f_exp_rc is not None and str(f_exp_rc).lower() not in ("nonzero", "non-zero", "!0"):
                try:
                    if v_rc != int(f_exp_rc):
                        rc_caught = False
                except ValueError:
                    pass
            sig_matched = all(tok in combined_f_out for tok in f_exp_tokens)
            caught = rc_caught and sig_matched
            if v_to:
                status_lbl = "TIMEOUT"
            elif validator_crashed:
                status_lbl = "VALIDATOR_CRASH"
            elif (v_rc != 0) and not caught:
                status_lbl = "WRONG_FAULT_SIGNATURE"
            elif caught:
                status_lbl = "CAUGHT_FAIL_CLOSED"
            else:
                status_lbl = "FAIL_OPEN_DEFECT"

            fault_results.append({
                "index": f_idx,
                "fault_case": raw_fc,
                "setup_rc": setup_rc,
                "validator_rc": v_rc,
                "caught": caught,
                "status": status_lbl,
            })
            if not caught:
                if status_lbl in ("WRONG_FAULT_SIGNATURE", "VALIDATOR_CRASH"):
                    tag_to_add = status_lbl
                else:
                    tag_to_add = "FAIL_OPEN_DEFECT"
                if tag_to_add not in failure_tags:
                    failure_tags.append(tag_to_add)

    finally:
        if not args.keep_overlay and os.path.isdir(overlays_root):
            shutil.rmtree(overlays_root, ignore_errors=True)

    # 4. Verify live host integrity (`Live Files Mutated == 0`)
    host_mutations = 0
    for td in target_dirs:
        post_host = snapshot_tree_manifest(td, include_hashes=True)
        hc, hm, hd = diff_manifests(host_pre[td], post_host)
        host_mutations += len(hc) + len(hm) + len(hd)
    if host_mutations > 0 and "HOST_CONTAMINATION" not in failure_tags:
        failure_tags.append("HOST_CONTAMINATION")

    elapsed = round(time.monotonic() - t0, 3)
    controls_ok = all(bool(r["passed"]) for r in control_results)
    faults_ok = all(bool(r["caught"]) for r in fault_results)
    overall_pass = controls_ok and faults_ok and ab_pass and (host_mutations == 0)

    # Write forensic bundle to report_dir
    diff_path = os.path.join(report_dir, "mutations.diff")
    stdout_path = os.path.join(report_dir, "stdout.log")
    stderr_path = os.path.join(report_dir, "stderr.log")
    report_path = os.path.join(report_dir, "report.json")
    ab_md_path = os.path.join(report_dir, "ab_comparison.md")

    with open(diff_path, "w", encoding="utf-8") as f:
        f.write("\n".join(unified_diffs))
    with open(stdout_path, "w", encoding="utf-8") as f:
        f.write("\n".join(all_stdout))
    with open(stderr_path, "w", encoding="utf-8") as f:
        f.write("\n".join(all_stderr))
    if ab_markdown_str:
        with open(ab_md_path, "w", encoding="utf-8") as f:
            f.write(ab_markdown_str)

    forensic_files_dict = {
        "report_json": report_path,
        "mutations_diff": diff_path,
        "stdout_log": stdout_path,
        "stderr_log": stderr_path,
    }
    if ab_markdown_str:
        forensic_files_dict["ab_comparison_md"] = ab_md_path

    report_obj = {
        "run_id": run_id,
        "mode": args.mode,
        "status": "PASS" if overall_pass else "FAIL",
        "elapsed_sec": elapsed,
        "target_dirs": target_dirs,
        "live_host_mutations": host_mutations,
        "control_results": control_results,
        "fault_results": fault_results,
        "ab_comparison": ab_comparison_obj,
        "vrf_receipts": vrf_receipts,
        "erofs_blocked_writes": erofs_hits,
        "overlay_mutations": mutation_records,
        "failure_taxonomy": failure_tags,
        "forensic_files": forensic_files_dict,
    }
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report_obj, f, indent=2)

    if args.json:
        print(json.dumps(report_obj, indent=2))
        return 0 if overall_pass else 1

    # Emit compact Diagnostic Summary (<= 350-400 tokens)
    c_pass = sum(1 for r in control_results if r["passed"])
    f_pass = sum(1 for r in fault_results if r["caught"])
    total_c = sum(len(v["created"]) for v in mutation_records.values())
    total_m = sum(len(v["modified"]) for v in mutation_records.values())
    total_d = sum(len(v["deleted"]) for v in mutation_records.values())

    mut_preview: List[str] = []
    for td, mrec in mutation_records.items():
        lbl = os.path.basename(td) or td
        for p in mrec["created"][:4]:
            mut_preview.append(f"+{lbl}/{p}")
        for p in mrec["modified"][:6]:
            mut_preview.append(f"~{lbl}/{p}")
        for p in mrec["deleted"][:4]:
            mut_preview.append(f"-{lbl}/{p}")

    print(f"=== Engineering Sandbox Diagnostic Report ({run_id}) ===")
    print(
        f"[ISOLATION_RECEIPT] Mode: {args.mode} | Cage: bwrap RO-root + CoW ({len(target_dirs)} targets) | "
        f"Live Host Mutations: {host_mutations} | Elapsed: {elapsed:.2f}s"
    )
    vrf_str = ", ".join(vrf_receipts) if vrf_receipts else "none"
    fault_str = f"{f_pass}/{len(fault_results)} caught" if fault_results else "n/a"
    print(
        f"[ORACLE_VERDICT] Status: {'PASS' if overall_pass else 'FAIL'} | "
        f"Controls: {c_pass}/{len(control_results)} passed | "
        f"+faults: {fault_str} | VRF: {vrf_str}"
    )
    if ab_comparison_obj is not None:
        f_deltas = list(ab_comparison_obj.get("file_deltas") or [])
        file_summaries: List[str] = []
        for fd in f_deltas:
            f_lbl = fd["file"]
            b_ok = "PASS" if (fd["blind_doc_rc"] == 0 and fd["blind_vrf_rc"] == 0) else "FAIL"
            v_ok = "PASS" if (fd["visible_doc_rc"] == 0 and fd["visible_vrf_rc"] == 0) else "FAIL"
            file_summaries.append(
                f"{f_lbl}(Blind:{b_ok}/TBD:{fd['blind_open_tbd']} vs Vis:{v_ok}/TBD:{fd['visible_open_tbd']})"
            )
        traj = ab_comparison_obj.get("trajectory_delta") or {}
        traj_str = ""
        if traj:
            traj_str = (
                f" | Turns(B/V): {traj.get('blind_turns')}/{traj.get('visible_turns')} "
                f"| SkillsRead(B/V): {len(traj.get('blind_skill_files_read', []))}/{len(traj.get('visible_skill_files_read', []))} "
                f"| lsProbes(B/V): {traj.get('blind_ls_find_probes')}/{traj.get('visible_ls_find_probes')}"
            )
        print(
            f"[AB_COMPARISON_MATRIX] Shared: {len(f_deltas)} files | "
            f"{'; '.join(file_summaries)}{traj_str}"
        )
    preview_str = f" ({', '.join(mut_preview[:8])})" if mut_preview else ""
    print(
        f"[MUTATION_SUMMARY] Overlay Changes: +{total_c} ~{total_m} -{total_d}{preview_str} | "
        f"Blocked Rogue Host Writes (EROFS): {len(erofs_hits)}"
    )
    tax_str = ", ".join(failure_tags) if failure_tags else "NONE"
    print(f"[FAILURE_TAXONOMY] {tax_str}")
    if erofs_hits:
        print(f"  -> Blocked write sample: {erofs_hits[0][:140]}")
    bundle_files = "report.json, mutations.diff, stdout.log, stderr.log"
    if ab_markdown_str:
        bundle_files += ", ab_comparison.md"
    print(f"[FORENSIC_BUNDLE] {report_dir} ({bundle_files})")

    return 0 if overall_pass else 1


if __name__ == "__main__":
    sys.exit(main())
