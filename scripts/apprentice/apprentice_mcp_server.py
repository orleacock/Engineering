#!/usr/bin/env python3
"""
Fused MCP Server for Apprentice Multi-Backend Local Sidecar (`apprentice_mcp_server.py`).

Uses `MCPServer` via `importlib.util.find_spec("mcp.server")` when invoked under the
Antigravity MCP venv, with pure Python 3.10+ stdlib compatibility for `--self-test`
and `--status` diagnostics. Shares all firewalls, ETA circuit breakers, telemetry,
and `lms` control paths directly from parent `scripts/apprentice_engine.py`.
"""
from __future__ import annotations

import argparse
import ast
import asyncio
import concurrent.futures
import importlib.util
import json
import math
import os
import re
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
SCRIPTS_ROOT = SCRIPT_DIR.parent
if str(SCRIPTS_ROOT) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_ROOT))

import apprentice_engine  # noqa: E402

_HAS_MCP = (
    importlib.util.find_spec("mcp") is not None
    and importlib.util.find_spec("mcp.server") is not None
)
if _HAS_MCP:
    from mcp.server import MCPServer  # type: ignore[import-not-found]
else:  # pragma: no cover - stdlib fallback for offline self-tests
    class MCPServer:  # type: ignore[no-redef]
        def __init__(self, name: str, instructions: str = "") -> None:
            self.name = name
            self.instructions = instructions
            self.registered_tools: list[str] = []

        def tool(self):
            def _decorator(fn):
                self.registered_tools.append(fn.__name__)
                return fn

            return _decorator

        def run(self, transport: str = "stdio") -> None:
            raise RuntimeError(
                f"mcp.server package is unavailable in {sys.executable}; "
                "invoke via /home/orin/.local/share/agy-gmail/venv/bin/python for stdio MCP."
            )


SERVER_VERSION = "2.5.0"
MCP_SYNC_WAIT_CAP_SECONDS = 135.0
_TRACKED_SERVER_FILES = (Path(__file__).resolve(), Path(apprentice_engine.__file__).resolve())
_BOOT_MTIMES = {p: p.stat().st_mtime for p in _TRACKED_SERVER_FILES if p.is_file()}
CONCISE_HIGH_THINKING_HINT = apprentice_engine.CONCISE_HIGH_THINKING_HINT
_STAGE_PY_DISCIPLINE_HINT = (
    "\n\n[PYTHON STAGING RULES: Return ONLY ONE complete ```python ... ``` block with zero extra prose. "
    "In `--self-test`, verify real functional behavior using fast deterministic synchronous checks "
    "(non-blocking probes, `<=0.05s` timeouts, or an optional injectable `clock=time.monotonic` callable "
    "for expiry/timing) — NEVER mutate private attributes (`_store`) in tests and NEVER use wall-clock "
    "`time.sleep(>=0.1)` or `assert elapsed >= ...`.]"
)


def _check_server_code_stale() -> bool:
    for tracked_path, boot_mtime in _BOOT_MTIMES.items():
        try:
            if tracked_path.is_file() and tracked_path.stat().st_mtime > boot_mtime:
                return True
        except OSError:
            continue
    return False


PLACEHOLDER_LINK_RE = re.compile(r"(?<!!)\[([^\[\]]+)\]\(([^()]*)\)")
PLACEHOLDER_TARGETS = ("...", "tbd", "todo", "url", "<", "path/to/", "example.com")
LL_WS_12_GUARD = (
    "\n\n[GOVERNED SIDE-CAR AUDIT RULES (LL-WS-12)]:\n"
    "1. Cite ONLY exact existing line numbers (relative path#Lstart-Lend) for lines present verbatim.\n"
    "2. Never cite `#L` line anchors from deleted (`-`) diff lines.\n"
    "3. Never expand hardware/fastener acronyms (e.g., BHCS/SHCS) beyond words written in source files.\n"
    "4. Never emit affiliate query parameters (`?affp=`, `dt_id=`, `aff_id=`) or placeholder `[label](...)` links.\n"
    "5. Insert explicit `[TBD: <specific_missing_spec>]` whenever counts, sizes, or ratings are absent.\n"
    "6. NEVER cite lines inside YAML frontmatter (`---`...`---`); start citations after closing `---`.\n"
    "7. When inspecting a `.patch`/`.diff` without downstream repo files in context, cite ONLY the `.patch` file's own `#L` line numbers (<= its total lines).\n"
)


mcp = MCPServer(
    name="apprentice",
    instructions=(
        "Governed multi-backend local sidecar connector (LM Studio Bionic, Ollama, llama.cpp, OpenAI-compatible) for Orin's workstation. "
        "Enforces 60s auto / 90s explicit ETA breakers, secret/CAD/4C firewalls, LL-WS-12 audit "
        "protections, collision-free verify_claims source selection, and confirmation-gated remote startup."
    ),
)


def _registered_tool_names() -> list[str]:
    if _HAS_MCP:
        tool_mgr = getattr(mcp, "_tool_manager", None)
        if tool_mgr is not None and hasattr(tool_mgr, "_tools"):
            return sorted(tool_mgr._tools.keys())
    return list(getattr(mcp, "registered_tools", []))


def select_collision_free_sources(repo_root: Path, candidate_paths: list[Path]) -> tuple[list[Path], list[str]]:
    """Filter foreign/missing files and deduplicate --sources basenames shallow-first."""
    repo_res = Path(os.path.expanduser(str(repo_root))).resolve(strict=False)
    in_repo: list[tuple[int, str, Path]] = []
    warnings: list[str] = []
    seen_exact: set[Path] = set()

    for raw in candidate_paths:
        sec_reason = apprentice_engine._inspect_path_security(raw)
        if sec_reason:
            raise apprentice_engine.SidecarFirewallError(f"[SECURITY_FIREWALL_BLOCKED] {sec_reason}")
        res = Path(os.path.expanduser(str(raw))).resolve(strict=False)
        if res in seen_exact:
            continue
        seen_exact.add(res)
        if not apprentice_engine._is_path_within(res, repo_res):
            warnings.append(f"Excluded out-of-repo source (CROSS_ENTITY guard): {raw}")
            continue
        if not res.is_file():
            warnings.append(f"Excluded missing source file: {raw}")
            continue
        rel_posix = res.relative_to(repo_res).as_posix()
        depth = len(Path(rel_posix).parts)
        in_repo.append((depth, rel_posix, res))

    in_repo.sort(key=lambda item: (item[0], item[1]))
    selected: list[Path] = []
    seen_basenames: dict[str, Path] = {}
    for _depth, rel_posix, path in in_repo:
        bname = path.name
        if bname in seen_basenames:
            kept_rel = seen_basenames[bname].relative_to(repo_res).as_posix()
            warnings.append(
                f"Excluded duplicate basename '{rel_posix}' from verify_claims --sources (kept '{kept_rel}')"
            )
            continue
        seen_basenames[bname] = path
        selected.append(path)
    return selected, warnings


def sanitize_quarantine_placeholder_links(md_text: str) -> tuple[str, int]:
    """Replace broken placeholder links `[label](...)` or `[label](path/to/...)` with inline code."""
    count = 0

    def _repl(match: re.Match[str]) -> str:
        nonlocal count
        label = match.group(1)
        target = match.group(2).strip()
        target_low = target.lower()
        if not target or target == "#" or any(marker in target_low for marker in PLACEHOLDER_TARGETS):
            count += 1
            return f"`{label}`"
        return match.group(0)

    sanitized = PLACEHOLDER_LINK_RE.sub(_repl, md_text)
    return sanitized, count


def _resolve_eta_cap(invocation_tier: str, effort: str = "standard") -> tuple[str, float]:
    tier = (invocation_tier or "explicit").strip().lower()
    if tier not in {"auto", "explicit"}:
        raise ValueError(f"Unsupported invocation_tier '{invocation_tier}'; expected 'auto' or 'explicit'.")
    cap = apprentice_engine.AUTO_MAX_ETA_SECONDS if tier == "auto" else apprentice_engine.DEFAULT_MAX_ETA_SECONDS
    if (effort or "").strip().lower() == "high":
        cap = max(cap, apprentice_engine.HIGH_EFFORT_SOFT_ETA_SECONDS)
    return tier, cap


def _resolve_homunculus_and_memory() -> tuple[Path, Path]:
    hom_env = os.environ.get("HOMUNCULUS_ROOT", "").strip()
    mem_env = os.environ.get("HOMUNCULUS_MEMORY_ROOT", "").strip()
    hom_root = Path(os.path.expanduser(hom_env)) if hom_env else apprentice_engine.DEFAULT_HOMUNCULUS_ROOT
    mem_root = Path(os.path.expanduser(mem_env)) if mem_env else apprentice_engine.DEFAULT_MEMORY_ROOT
    return hom_root, mem_root


def _scorecard_suffix(call_id: str | None = None) -> str:
    try:
        sc_str = apprentice_engine.format_lifetime_scorecard()
    except Exception:
        sc_str = "Apprentice Calls = 0/0 (healed=0)"
    return f"{sc_str} | call_id={call_id}" if call_id else sc_str


def _maybe_apply_prev_verdict(
    prev_call_id: str | None,
    prev_verdict: str | None,
    prev_verdict_note: str = "",
) -> dict[str, Any] | None:
    if not prev_call_id or not prev_verdict:
        return None
    try:
        return apprentice_engine.apply_call_verdict(prev_call_id, prev_verdict, note=prev_verdict_note)
    except (KeyError, ValueError, OSError) as exc:
        return {"ok": False, "call_id": prev_call_id, "error": str(exc)}


_VERIFY_ALLOWED_EXTS = frozenset(
    {".md", ".py", ".cfg", ".json", ".toml", ".yaml", ".yml", ".csv", ".txt", ".sh", ".ini", ".patch", ".diff"}
)
_NON_AUTH_DIR_PARTS = frozenset({"quarantine", "study_briefs", "addon_staging"})
_NON_AUTH_FILENAMES = frozenset({"lessons_learned_template.md", "project_playbooks.md"})
_NON_AUTH_SUFFIXES = ("_lessons_learned.md", "_lessons_archive.md", "_playbooks.md")


def _filter_authoritative_verify_sources(paths: list[Path]) -> list[Path]:
    """Filter out Quarantine/Lessons/non-authoritative docs before running verify_claims.py."""
    filtered: list[Path] = []
    for raw_p in paths:
        res = Path(os.path.expanduser(str(raw_p))).resolve(strict=False)
        parts_low = {seg.lower() for seg in res.parts}
        if parts_low & _NON_AUTH_DIR_PARTS:
            continue
        bname_low = res.name.lower()
        if bname_low in _NON_AUTH_FILENAMES or bname_low.endswith(_NON_AUTH_SUFFIXES):
            continue
        if res.suffix.lower() not in _VERIFY_ALLOWED_EXTS and res.name not in ("LICENSE", "CNAME"):
            continue
        if res.is_file():
            filtered.append(raw_p)
    return filtered


def _run_verify_claims_check(
    text_body: str,
    sources: list[Path],
    verify_claims_path: Path,
    mem_root: Path,
    cwd_path: Path,
    project_dir: Path | None = None,
) -> dict[str, Any]:
    auth_sources = _filter_authoritative_verify_sources(sources)
    if not verify_claims_path.is_file() or not auth_sources:
        return {
            "ran": False,
            "skipped_reason": "no_authoritative_sources" if sources else "no_sources",
        }
    with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", suffix=".md", delete=False) as tf:
        tf.write(text_body)
        tmp_md = Path(tf.name)
    os.chmod(tmp_md, 0o600)
    try:
        cmd = [
            sys.executable,
            "-B",
            str(verify_claims_path),
            "--target",
            str(tmp_md),
            "--sources",
            *[str(p) for p in auth_sources],
            "--memory-root",
            str(mem_root),
            "--json",
        ]
        if project_dir is not None and project_dir.is_dir():
            cmd.extend(["--project-dir", str(project_dir)])
        t0 = time.perf_counter()
        vp = subprocess.run(
            cmd,
            cwd=apprentice_engine._safe_subprocess_cwd(cwd_path),
            capture_output=True,
            text=True,
            timeout=45,
            check=False,
        )
        elapsed_ms = round((time.perf_counter() - t0) * 1000.0, 1)
        report: dict[str, Any] = {}
        if vp.stdout.strip():
            try:
                parsed = json.loads(vp.stdout)
                if isinstance(parsed, dict):
                    report = parsed
            except json.JSONDecodeError:
                report = {}
        sup = int(report.get("supported_count", 0))
        unb = int(report.get("unbacked_count", 0))
        tbd = int(report.get("tbd_count", 0))
        tot = sup + unb
        pct = round(100.0 * sup / tot, 1) if tot > 0 else 100.0
        res: dict[str, Any] = {
            "ran": True,
            "returncode": vp.returncode,
            "elapsed_ms": elapsed_ms,
            "supported": sup,
            "unbacked": unb,
            "tbd_count": tbd,
            "backed_pct": pct,
            "vrf_token": report.get("vrf_token"),
        }
        if vp.returncode != 0:
            if report.get("unbacked_claims"):
                res["unbacked_claims"] = report["unbacked_claims"][:20]
            elif vp.stdout.strip() or vp.stderr.strip():
                res["stdout_tail"] = ((vp.stdout or "") + "\n" + (vp.stderr or "")).strip()[-800:]
        return res
    finally:
        tmp_md.unlink(missing_ok=True)


def _normalize_control_action(action: str) -> str:
    norm = (action or "status").strip().lower().replace("_", "-")
    aliases = {"load-profile": "load"}
    norm = aliases.get(norm, norm)
    if norm not in {
        "status",
        "start-headless",
        "load",
        "unload",
        "stop-server",
        "job-status",
        "job-collect",
        "job-list",
        "verdict",
        "scorecard-reset",
    }:
        raise ValueError(f"Unsupported control action: {action}")
    return norm


def _firewall_error_response(exc: Exception, op_label: str) -> dict[str, Any]:
    msg = str(exc)
    sc_str = _scorecard_suffix()
    if "BIONIC_UNLOADED_CONFIRMATION_REQUIRED" in msg:
        return {
            "ok": False,
            "error_code": "BIONIC_UNLOADED_CONFIRMATION_REQUIRED",
            "error": msg,
            "scorecard": sc_str,
            "user_notice": (
                f"[APPRENTICE NOTICE] Bionic is currently UNLOADED; ask user confirmation "
                f"before calling apprentice_control(action='load_profile', user_confirmed=True). | {sc_str}"
            ),
        }
    return {
        "ok": False,
        "error_code": "SECURITY_FIREWALL_BLOCKED",
        "error": msg,
        "scorecard": sc_str,
        "user_notice": f"[APPRENTICE NOTICE] {op_label} blocked by security firewall. | {sc_str}",
    }


def _control_action_impl(
    action: str = "status",
    profile: str = "gpu-daily",
    user_confirmed: bool = False,
    *,
    epoch_label: str = "v2.3",
    job_id: str | None = None,
    wait_seconds: float = 0.0,
    call_id: str | None = None,
    verdict: str | None = None,
    note: str = "",
) -> dict[str, Any]:
    norm_action = _normalize_control_action(action)
    if norm_action == "job-status":
        if not job_id:
            raise ValueError("job_id is required for action='job-status'")
        clamped_wait = min(max(0.0, float(wait_seconds)), 60.0)
        jres = apprentice_engine.get_job_status(job_id, wait_seconds=clamped_wait, include_result=False)
        sc_str = _scorecard_suffix()
        return {
            **jres,
            "scorecard": sc_str,
            "user_notice": f"[APPRENTICE NOTICE] Job {job_id} status={jres['status']} | {sc_str}",
        }
    if norm_action == "job-collect":
        if not job_id:
            raise ValueError("job_id is required for action='job-collect'")
        clamped_collect_wait = min(max(0.0, float(wait_seconds)), float(MCP_SYNC_WAIT_CAP_SECONDS))
        jres = apprentice_engine.get_job_status(job_id, wait_seconds=clamped_collect_wait, include_result=True)
        sc_str = _scorecard_suffix()
        still_msg = " (still running; call job-collect again with wait_seconds=120)" if jres.get("status") == "running" else ""
        return {
            **jres,
            "waited_seconds": clamped_collect_wait,
            "scorecard": sc_str,
            "user_notice": f"[APPRENTICE NOTICE] Job {job_id} status={jres['status']}{still_msg} | {sc_str}",
        }
    if norm_action == "job-list":
        lres = apprentice_engine.list_jobs(limit=20)
        sc_str = _scorecard_suffix()
        return {
            **lres,
            "scorecard": sc_str,
            "user_notice": f"[APPRENTICE NOTICE] Listed {len(lres['jobs'])} sprint jobs | {sc_str}",
        }
    if norm_action == "verdict":
        if not call_id or not verdict:
            raise ValueError("call_id and verdict are required for action='verdict'")
        vres = apprentice_engine.apply_call_verdict(call_id, verdict, note=note)
        return {
            "ok": True,
            **vres,
            "scorecard": vres["formatted"],
            "user_notice": f"[APPRENTICE NOTICE] Recorded verdict '{vres['verdict']}' for {call_id}. | {vres['formatted']}",
        }
    if norm_action == "scorecard-reset":
        if not user_confirmed:
            raise apprentice_engine.SidecarFirewallError(
                "[USER_CONFIRMATION_REQUIRED] apprentice_control('scorecard-reset') requires user_confirmed=True."
            )
        lbl = (epoch_label or "v2.3").strip() or "v2.3"
        rres = apprentice_engine.reset_scorecard(archive=True, epoch_label=lbl)
        return {
            **rres,
            "scorecard": rres["formatted"],
            "user_notice": (
                f"[APPRENTICE NOTICE] Reset scorecard to epoch '{rres['epoch']}' "
                f"(archived previous epoch). | {rres['formatted']}"
            ),
        }

    if profile not in apprentice_engine.CONTROL_PROFILES:
        raise ValueError(f"Unsupported profile '{profile}'; expected one of {tuple(apprentice_engine.CONTROL_PROFILES.keys())}")
    api_url = apprentice_engine.validate_loopback_url(apprentice_engine.resolve_default_api_url())
    lms_bin = apprentice_engine.DEFAULT_LMS_BIN
    cfg_path = apprentice_engine.DEFAULT_CONCRETE_CFG_PATH
    appimage_path = apprentice_engine.DEFAULT_APPIMAGE_PATH

    if norm_action == "status":
        res = apprentice_engine._control_status(api_url, apprentice_engine.DEFAULT_MODEL_ID, lms_bin)
        srv = res["server"]
        hw = res["hardware"]
        stale_restart = _check_server_code_stale()
        state_str = "ONLINE_READY" if srv["target_model_loaded"] else ("UNLOADED" if srv["reachable"] else "OFFLINE")
        sc_fmt = res.get("scorecard", {}).get("formatted") or _scorecard_suffix()
        stale_note = " | RESTART MCP SESSION (disk updated)" if stale_restart else ""
        return {
            "ok": True,
            "state": state_str,
            "server_version": SERVER_VERSION,
            "server_stale_restart_recommended": stale_restart,
            **res,
            "user_notice": (
                f"[APPRENTICE NOTICE] Status={state_str} | server=v{SERVER_VERSION} | ctx={srv['loaded_context_length']} | "
                f"VRAM={hw['vram_used_gib']} GiB (free={hw.get('vram_free_gib')} GiB, GTT={hw.get('gtt_used_gib')} GiB){stale_note} | {sc_fmt}"
            ),
        }

    if not user_confirmed:
        raise apprentice_engine.SidecarFirewallError(
            f"[USER_CONFIRMATION_REQUIRED] apprentice_control('{norm_action}') refuses autonomous start/load/unload/stop without user_confirmed=True."
        )

    if norm_action == "start-headless":
        res = apprentice_engine._control_start_headless(api_url, apprentice_engine.DEFAULT_MODEL_ID, profile, lms_bin, appimage_path, cfg_path)
    elif norm_action == "load":
        res = apprentice_engine._control_load(api_url, apprentice_engine.DEFAULT_MODEL_ID, profile, lms_bin, cfg_path)
    elif norm_action == "unload":
        res = apprentice_engine._control_unload(api_url, apprentice_engine.DEFAULT_MODEL_ID, lms_bin)
    else:
        res = apprentice_engine._control_stop_server(api_url, apprentice_engine.DEFAULT_MODEL_ID, lms_bin)

    sc_str = _scorecard_suffix()
    return {
        "ok": True,
        **res,
        "scorecard": sc_str,
        "user_notice": f"[APPRENTICE NOTICE] Executed control action '{norm_action}' (profile={profile}). | {sc_str}",
    }


def _ensure_live_process_cwd() -> str:
    """Ensure the MCP process working directory exists even after plugin upgrades."""
    return apprentice_engine._safe_subprocess_cwd()


def _apprentice_control_sync(
    action: str = "status",
    profile: str = "gpu-daily",
    user_confirmed: bool = False,
    epoch_label: str = "v2.3",
    job_id: str | None = None,
    wait_seconds: float = 0.0,
    call_id: str | None = None,
    verdict: str | None = None,
    note: str = "",
) -> dict[str, Any]:
    """Inspect Bionic status, manage async jobs/verdicts/epochs, or run user-confirmed remote lifecycle actions."""
    _ensure_live_process_cwd()
    try:
        return _control_action_impl(
            action=action,
            profile=profile,
            user_confirmed=bool(user_confirmed),
            epoch_label=epoch_label,
            job_id=job_id,
            wait_seconds=float(wait_seconds),
            call_id=call_id,
            verdict=verdict,
            note=note,
        )
    except apprentice_engine.SidecarFirewallError as exc:
        if "USER_CONFIRMATION_REQUIRED" in str(exc):
            sc_str = _scorecard_suffix()
            return {
                "ok": False,
                "error_code": "USER_CONFIRMATION_REQUIRED",
                "error": str(exc),
                "scorecard": sc_str,
                "user_notice": f"[APPRENTICE NOTICE] Action blocked pending explicit user confirmation. | {sc_str}",
            }
        return _firewall_error_response(exc, "Control")
    except Exception as exc:
        sc_str = _scorecard_suffix()
        return {
            "ok": False,
            "error_code": "CONTROL_ERROR",
            "error": str(exc),
            "scorecard": sc_str,
            "user_notice": f"[APPRENTICE NOTICE] Control error: {exc} | {sc_str}",
        }


@mcp.tool()
async def apprentice_control(
    action: str = "status",
    profile: str = "gpu-daily",
    user_confirmed: bool = False,
    epoch_label: str = "v2.3",
    job_id: str | None = None,
    wait_seconds: float = 0.0,
    call_id: str | None = None,
    verdict: str | None = None,
    note: str = "",
) -> dict[str, Any]:
    """Inspect Bionic status, manage async sprint jobs/verdicts/epochs, or execute user-confirmed lifecycle actions."""
    return await asyncio.to_thread(
        _apprentice_control_sync,
        action=action,
        profile=profile,
        user_confirmed=user_confirmed,
        epoch_label=epoch_label,
        job_id=job_id,
        wait_seconds=wait_seconds,
        call_id=call_id,
        verdict=verdict,
        note=note,
    )


apprentice_control = _apprentice_control_sync  # type: ignore[assignment]


def _prepare_tail_continuation(raw_head: str) -> tuple[str, str]:
    """Drop an incomplete trailing line on length truncation and return (clean_head, tail_context)."""
    lines = raw_head.splitlines()
    if len(lines) >= 2 and not raw_head.endswith("\n"):
        head_clean = "\n".join(lines[:-1])
    else:
        head_clean = raw_head.rstrip("\n")
    tail_context = "\n".join(head_clean.splitlines()[-12:])
    return head_clean, tail_context


def _stitch_tail_continuation(head_clean: str, tail_raw: str) -> str:
    """Seamlessly stitch tail continuation output while stripping outer wrapper fences and duplicate boundary lines."""
    tail = tail_raw.strip()
    if tail.startswith("```") and tail.endswith("```"):
        tail_lines = tail.splitlines()
        if len(tail_lines) >= 2:
            tail = "\n".join(tail_lines[1:-1]).strip()
    if not head_clean.strip():
        return tail
    if not tail:
        return head_clean
    head_lines = [ln for ln in head_clean.splitlines() if ln.strip()]
    tail_lines = tail.splitlines()
    while tail_lines and not tail_lines[0].strip():
        tail_lines.pop(0)
    if head_lines and tail_lines and tail_lines[0].strip() == head_lines[-1].strip():
        tail_lines.pop(0)
    tail_clean = "\n".join(tail_lines).lstrip("\n")
    if not tail_clean.strip():
        return head_clean
    return f"{head_clean.rstrip()}\n{tail_clean}"


def _filter_chunk_extract_lines(raw_text: str) -> str:
    """Drop empty lines, standalone NONE replies, and slice-local [TBD] absence noise."""
    absence_markers = ("slice", "chunk", "not in ", "absent", "not found", "not defined", "missing")
    kept: list[str] = []
    for raw_ln in raw_text.splitlines():
        s = raw_ln.strip()
        if not s:
            continue
        if re.match(r"^`?NONE`?(?:\s*[-—:(].*)?$", s, re.IGNORECASE):
            continue
        s_low = s.lower()
        if "[tbd:" in s_low and any(tok in s_low for tok in absence_markers):
            continue
        kept.append(raw_ln.rstrip())
    return "\n".join(kept)


def _extract_anchor_spans(text: str) -> list[tuple[str, int, int]]:
    spans: list[tuple[str, int, int]] = []
    for m in re.finditer(r"([A-Za-z0-9_./-]+)?#L(\d+)(?:[-–—]L?(\d+))?", text):
        pref = Path(m.group(1)).name.lower() if m.group(1) else ""
        s_i = int(m.group(2))
        e_i = int(m.group(3)) if m.group(3) else s_i
        spans.append((pref, min(s_i, e_i), max(s_i, e_i)))
    return spans


def _format_compact_verify_failures(vrf_res: dict[str, Any], *, max_chars: int = 2800) -> str:
    """Summarize unbacked verify_claims items grouped by line number without repeating bulky line_text blobs."""
    raw_list = list(vrf_res.get("unbacked_claims") or [])
    if not raw_list:
        tail = str(vrf_res.get("stdout_tail") or "verification failed").strip()
        return tail[-max_chars:]
    by_line: dict[str, list[str]] = {}
    order: list[str] = []
    for item in raw_list:
        if isinstance(item, dict):
            ln_key = f"L{item.get('line')}" if item.get("line") is not None else "L?"
            t_lbl = str(item.get("type") or "UNBACKED").strip()
            c_txt = str(item.get("claim") or "").strip().replace("\n", " ")
            if len(c_txt) > 120:
                c_txt = c_txt[:117] + "..."
            entry = f"[{t_lbl}] {c_txt}" if c_txt else f"[{t_lbl}]"
        else:
            ln_key = "L?"
            entry = str(item).strip().replace("\n", " ")[:160]
        if ln_key not in by_line:
            by_line[ln_key] = []
            order.append(ln_key)
        if entry not in by_line[ln_key]:
            by_line[ln_key].append(entry)
    lines_out = [f"{ln_k}: " + " | ".join(by_line[ln_k]) for ln_k in order]
    joined = "\n".join(lines_out)
    return joined[:max_chars] if len(joined) > max_chars else joined


def _build_chunked_repair_context(
    prompt_str: str,
    draft_text: str,
    validated_files: list[Path],
    repo_resolved: Path | None,
    fallback_blocks: list[str],
    unbacked_claims: list[Any] | None = None,
) -> str:
    """Extract compact +/-16 line windows around cited #L anchors (<=36 KB), prioritizing flagged files first."""
    fail_blob = "\n".join(
        (
            f"L{u.get('line')}: [{u.get('type')}] {u.get('claim')}"
            if isinstance(u, dict)
            else str(u)
        )
        for u in (unbacked_claims or [])
    )
    fail_low = fail_blob.lower()
    cited_spans = _extract_anchor_spans(draft_text) + _extract_anchor_spans(fail_blob)

    if not cited_spans and not fail_low:
        fb = "\n\n".join(fallback_blocks)[:28000]
        return f"{prompt_str.strip()}\n\n{fb}" if fb else prompt_str.strip()

    # Deduplicate resolved paths across multiple #L slices and order files with failing claims FIRST
    prioritized_files = sorted(
        list(dict.fromkeys(validated_files)),
        key=lambda vf: (0 if (vf.name.lower() in fail_low or any(p == vf.name.lower() for p, _, _ in cited_spans)) else 1),
    )

    slices_out: list[str] = [prompt_str.strip()]
    budget_bytes = 36000
    used_bytes = len(slices_out[0].encode("utf-8"))
    for vf in prioritized_files:
        vf_low = vf.name.lower()
        file_ranges = [
            (s_i, e_i)
            for pref, s_i, e_i in cited_spans
            if not pref or pref == vf_low or len(validated_files) == 1
        ]
        all_lines = vf.read_text(encoding="utf-8", errors="replace").splitlines()
        n_lines = len(all_lines)
        if n_lines == 0:
            continue
        if not file_ranges:
            if vf_low in fail_low:
                file_ranges = [(1, min(n_lines, 50))]
            else:
                continue
        windows = sorted((max(1, s_i - 16), min(n_lines, e_i + 16)) for s_i, e_i in file_ranges)
        merged: list[tuple[int, int]] = []
        for ws, we in windows:
            if merged and ws <= merged[-1][1] + 1:
                merged[-1] = (merged[-1][0], max(merged[-1][1], we))
            else:
                merged.append((ws, we))
        rel_disp = str(vf.relative_to(repo_resolved)) if repo_resolved else vf.name
        for ws, we in merged:
            numbered = "\n".join(f"{idx}: {all_lines[idx - 1]}" for idx in range(ws, we + 1))
            blk = f"\n### CONTEXT SLICE: {rel_disp}#L{ws}-L{we}\n{numbered}\n"
            blk_b = len(blk.encode("utf-8"))
            if used_bytes + blk_b > budget_bytes and len(slices_out) > 1:
                break
            slices_out.append(blk)
            used_bytes += blk_b

    if len(slices_out) == 1:
        fb = "\n\n".join(fallback_blocks)[:28000]
        if fb:
            slices_out.append(fb)
    return "\n".join(slices_out)


def _surgical_repair_unbacked_lines(
    *,
    draft_text: str,
    vrf_res: dict[str, Any],
    context_sources: list[Path],
    clean_sources: list[Path],
    repo_resolved: Path | None,
    verify_claims_path: Path,
    mem_root: Path,
    cwd_check: Path,
    api_url: str,
    sys_prompt: str,
    loaded_ctx: int | None,
    tier: str,
    eta: dict[str, Any],
    cmd_name_prefix: str,
    project_dir: Path | None = None,
    sanitize_links: bool = False,
) -> dict[str, Any] | None:
    """Repair ONLY the specific failing lines on 1..12 unbacked claims across <=8 draft lines while preserving verified lines."""
    unbacked_list = list(vrf_res.get("unbacked_claims") or [])
    draft_lines = draft_text.splitlines()
    non_empty_count = sum(1 for ln in draft_lines if ln.strip())
    if non_empty_count < 6 or int(vrf_res.get("supported") or 0) < 4 or not (1 <= len(unbacked_list) <= 12):
        return None

    target_nums: list[int] = []
    seen_nums: set[int] = set()
    fail_text_blobs: list[str] = []

    def _add_line(n: int) -> None:
        if 1 <= n <= len(draft_lines) and n not in seen_nums and draft_lines[n - 1].strip():
            seen_nums.add(n)
            target_nums.append(n)

    for u in unbacked_list:
        if isinstance(u, dict):
            fail_text_blobs.append(json.dumps(u))
            ln_raw = u.get("line") or u.get("line_number") or u.get("line_num") or u.get("target_line")
            ln_txt = str(u.get("line_text") or "").strip()
            matched = False
            if isinstance(ln_raw, int) and 1 <= ln_raw <= len(draft_lines):
                if not ln_txt or draft_lines[ln_raw - 1].strip() == ln_txt:
                    _add_line(ln_raw)
                    matched = True
            if not matched and ln_txt:
                for idx, dln in enumerate(draft_lines, 1):
                    if dln.strip() == ln_txt or ln_txt in dln:
                        _add_line(idx)
                        matched = True
                        break
            if not matched:
                c_txt = str(u.get("claim") or "").strip()
                if c_txt:
                    for idx, dln in enumerate(draft_lines, 1):
                        if c_txt in dln:
                            _add_line(idx)
                            break
        else:
            fail_text_blobs.append(str(u))

    if not target_nums or len(target_nums) > 8:
        return None

    target_nums.sort()
    first_ln = draft_lines[0].strip() if draft_lines else ""
    if (
        1 not in seen_nums
        and first_ln
        and not first_ln.startswith(("- ", "* ", "#", "|", "["))
        and len(target_nums) < 8
    ):
        _add_line(1)
        target_nums.sort()

    flagged_text = "\n".join(draft_lines[n - 1] for n in target_nums) + "\n" + "\n".join(fail_text_blobs)
    spans = _extract_anchor_spans(flagged_text)
    flagged_low = flagged_text.lower()

    slice_blocks: list[str] = []
    slice_budget = 20000
    used_slice_bytes = 0
    cand_files = context_sources or clean_sources
    for vf in cand_files:
        vf_low = vf.name.lower()
        file_ranges = [
            (s_i, e_i)
            for pref, s_i, e_i in spans
            if not pref or pref == vf_low or len(cand_files) == 1
        ]
        all_src = vf.read_text(encoding="utf-8", errors="replace").splitlines()
        n_src = len(all_src)
        if n_src == 0:
            continue
        # Extract any "Source line N" mentioned in WARNING_CONTEXT_CITATION diagnostic text
        for sm in re.finditer(r"Source line\s+(\d+)", flagged_text):
            src_ln = int(sm.group(1))
            if vf_low in flagged_low or len(cand_files) == 1:
                file_ranges.append((max(1, src_ln - 2), src_ln + 6))
        if not file_ranges and vf_low in flagged_low:
            file_ranges = [(1, min(n_src, 70))]
        if not file_ranges:
            continue
        windows = sorted((max(1, s_i - 18), min(n_src, e_i + 18)) for s_i, e_i in file_ranges)
        merged: list[tuple[int, int]] = []
        for ws, we in windows:
            if merged and ws <= merged[-1][1] + 1:
                merged[-1] = (merged[-1][0], max(merged[-1][1], we))
            else:
                merged.append((ws, we))
        rel_disp = str(vf.relative_to(repo_resolved)) if repo_resolved else vf.name
        for ws, we in merged:
            numbered = "\n".join(f"{idx}: {all_src[idx - 1]}" for idx in range(ws, we + 1))
            blk = f"\n### SOURCE SLICE: {rel_disp}#L{ws}-L{we}\n{numbered}\n"
            blk_b = len(blk.encode("utf-8"))
            if used_slice_bytes + blk_b > slice_budget and slice_blocks:
                break
            slice_blocks.append(blk)
            used_slice_bytes += blk_b

    if not slice_blocks:
        return None

    if "QUALIFIED_QUANTITY" in flagged_text:
        for vf in cand_files:
            if "bom" not in vf.name.lower():
                continue
            bom_lines = vf.read_text(encoding="utf-8", errors="replace").splitlines()
            if not bom_lines:
                continue
            rel_disp = str(vf.relative_to(repo_resolved)) if repo_resolved else vf.name
            if any(f"SOURCE SLICE: {rel_disp}#" in b for b in slice_blocks):
                continue
            numbered = "\n".join(f"{idx}: {bom_lines[idx - 1]}" for idx in range(1, min(len(bom_lines), 65) + 1))
            blk = f"\n### SOURCE SLICE: {rel_disp}#L1-L{min(len(bom_lines), 65)}\n{numbered}\n"
            blk_b = len(blk.encode("utf-8"))
            if used_slice_bytes + blk_b <= slice_budget:
                slice_blocks.append(blk)
                used_slice_bytes += blk_b

    flagged_block = "\n".join(f"L{n}: {draft_lines[n - 1]}" for n in target_nums)
    fail_detail = _format_compact_verify_failures(vrf_res, max_chars=2200)
    surg_prompt = (
        "SURGICAL LINE REPAIR: Fix ONLY the numbered draft lines below that failed claim verification.\n"
        "Output ONLY one line per flagged line number in the exact format:\n"
        "L<number>: <repaired single-line bullet>\n"
        "OR (if the flagged line is unbacked preamble/summary fluff with no source fact):\n"
        "L<number>: DELETE\n\n"
        "CRITICAL REPAIR RULES:\n"
        "1. Output ONLY `L<n>: ...` replacements for the listed line numbers — ZERO unchanged lines, ZERO extra prose.\n"
        "2. Use ONLY exact source literals, units, counts, and `#Lstart-Lend` anchors verbatim from SOURCE SLICES below (NEVER cite YAML frontmatter lines `---`...`---` or external `#L` files not in SOURCE SLICES; cite `.patch` `#L` lines <= patch line count).\n"
        "3. Never invent parenthetical example numbers/units like `(e.g., 0.8mm)`; replace missing specs with `[TBD: <missing_spec>]`.\n"
        "4. In `[CALC: ...]`, the left of `=` MUST contain ONLY source-verbatim numbers/operators (NEVER words like `Total` or unprinted subtotals) — or omit `[CALC:]`.\n"
        "5. If a cited source line lies inside a `> [!WARNING]` or `> [!CAUTION]` block, explicitly include `Warning:` or `Caution:` / the hazard qualifier in that bullet.\n"
        "6. For QUALIFIED_QUANTITY(...) failures, a source table qualifies that quantity (e.g., '~2' / 'approx' / '(2)' instead of bare 'Qty 2') — use the exact qualified quantity from source OR output 'L<n>: DELETE' if that item is already covered by another BOM bullet.\n\n"
        f"Verification failures:\n{fail_detail}\n\n"
        f"Flagged draft lines:\n{flagged_block}\n\n"
        + "\n".join(slice_blocks)
    )
    surg_max_toks = min(1800, 260 * len(target_nums) + 200)
    t0 = time.perf_counter()
    res_surg = apprentice_engine.invoke_chat_completion(
        api_url=api_url,
        model_id=apprentice_engine.DEFAULT_MODEL_ID,
        mode="fast",
        system_prompt=sys_prompt,
        user_content=surg_prompt,
        max_tokens=surg_max_toks,
        timeout_s=120.0,
        preflight_checked=True,
        loaded_ctx=loaded_ctx,
        allow_high_floor=False,
    )
    dt = round(time.perf_counter() - t0, 3)
    apprentice_engine.record_usage_telemetry(
        {
            "cmd": f"{cmd_name_prefix}_surgical_verify_retry",
            "effort": eta["effort"],
            "invocation_tier": tier,
            "mode": "fast",
            "est_prompt_tokens": res_surg["prompt_tokens"],
            "predicted_eta_s": 0.0,
            "max_eta_seconds": 120.0,
            "tripped": False,
            "is_retry": True,
            "prompt_tokens": res_surg["prompt_tokens"],
            "completion_tokens": res_surg["completion_tokens"],
            "elapsed_s": res_surg["elapsed_s"],
            "kv_wait_s": res_surg.get("kv_wait_s", 0.0),
            "observed_tg_tok_s": res_surg["observed_tg_tok_s"],
            "finish_reason": res_surg["finish_reason"],
        }
    )

    target_set = set(target_nums)
    new_lines = list(draft_lines)
    deleted_nums: set[int] = set()
    edits_applied = 0
    for raw_ln in str(res_surg.get("content") or "").splitlines():
        m = re.match(r"^\s*L?(\d+)\s*:\s*(.*)$", raw_ln)
        if not m:
            continue
        ln_i = int(m.group(1))
        if ln_i not in target_set:
            continue
        rep_val = m.group(2).strip()
        if rep_val.upper() == "DELETE" or rep_val == "`DELETE`":
            deleted_nums.add(ln_i)
            edits_applied += 1
        elif rep_val:
            new_lines[ln_i - 1] = rep_val
            edits_applied += 1

    if edits_applied == 0:
        return {
            "verified": False,
            "content": draft_text,
            "links_fixed": 0,
            "vrf_after": vrf_res,
            "elapsed_s": dt,
            "prompt_tokens": int(res_surg.get("prompt_tokens") or 0),
            "completion_tokens": int(res_surg.get("completion_tokens") or 0),
            "edits_applied": 0,
        }

    spliced_text = "\n".join(line for idx, line in enumerate(new_lines, 1) if idx not in deleted_nums)
    links_fixed = 0
    if sanitize_links:
        spliced_text, links_fixed = sanitize_quarantine_placeholder_links(spliced_text)

    vrf_after = _run_verify_claims_check(
        spliced_text,
        clean_sources,
        verify_claims_path,
        mem_root,
        cwd_check,
        project_dir=project_dir,
    )
    return {
        "verified": vrf_after.get("returncode") == 0,
        "content": spliced_text,
        "links_fixed": links_fixed,
        "vrf_after": vrf_after,
        "elapsed_s": dt,
        "prompt_tokens": int(res_surg.get("prompt_tokens") or 0),
        "completion_tokens": int(res_surg.get("completion_tokens") or 0),
        "edits_applied": edits_applied,
        "target_lines": target_nums,
    }


def _run_full_repair_with_guard(
    *,
    repair_prompt: str,
    draft_for_heal: str,
    vrf_for_heal: dict[str, Any],
    base_res: dict[str, Any],
    effective_mode: str,
    effort_norm: str,
    max_budget: int,
    api_url: str,
    sys_prompt: str,
    loaded_ctx: int | None,
    clean_sources: list[Path],
    verify_claims_path: Path,
    mem_root: Path | None,
    cwd_check: Path,
    tier: str,
    eta: dict[str, Any],
    telemetry_cmd: str,
    project_dir: Path | None = None,
    sanitize_links: bool = False,
) -> dict[str, Any]:
    """Run verify-claims repair with HIGH headroom (>=4096), 1 length continuation, and non-regression guard."""
    repair_mode = "fast" if effective_mode in ("fast", "deep") else effective_mode
    repair_tok_cap = min(max(max_budget, 4096), 6144) if effective_mode == "deep" else max_budget
    repair_timeout = 180.0 if effective_mode == "deep" else 135.0

    t0 = time.perf_counter()
    res2 = apprentice_engine.invoke_chat_completion(
        api_url=api_url,
        model_id=apprentice_engine.DEFAULT_MODEL_ID,
        mode=repair_mode,
        system_prompt=sys_prompt,
        user_content=repair_prompt,
        max_tokens=repair_tok_cap,
        timeout_s=repair_timeout,
        preflight_checked=True,
        loaded_ctx=loaded_ctx,
        allow_high_floor=False,
    )
    dt = round(time.perf_counter() - t0, 3)
    apprentice_engine.record_usage_telemetry(
        {
            "cmd": telemetry_cmd,
            "effort": eta["effort"],
            "invocation_tier": tier,
            "mode": repair_mode,
            "est_prompt_tokens": res2["prompt_tokens"],
            "predicted_eta_s": eta["predicted_eta_s"],
            "max_eta_seconds": repair_timeout,
            "tripped": False,
            "is_retry": True,
            "prompt_tokens": res2["prompt_tokens"],
            "completion_tokens": res2["completion_tokens"],
            "elapsed_s": res2["elapsed_s"],
            "kv_wait_s": res2.get("kv_wait_s", 0.0),
            "observed_tg_tok_s": res2["observed_tg_tok_s"],
            "finish_reason": res2["finish_reason"],
        }
    )

    if res2.get("finish_reason") == "length" and str(res2.get("content") or "").strip():
        t_len0 = time.perf_counter()
        head_clean, tail_ctx = _prepare_tail_continuation(res2["content"])
        cont_prompt = (
            f"{repair_prompt}\n\n"
            "Your previous repaired response hit the output token limit after completing these lines:\n"
            f"{tail_ctx}\n\n"
            "Continue seamlessly starting with the NEXT line immediately after the lines above without repeating prior bullets."
        )
        try:
            res_cont = apprentice_engine.invoke_chat_completion(
                api_url=api_url,
                model_id=apprentice_engine.DEFAULT_MODEL_ID,
                mode=repair_mode,
                system_prompt=sys_prompt,
                user_content=cont_prompt,
                max_tokens=2048,
                timeout_s=135.0,
                preflight_checked=True,
                loaded_ctx=loaded_ctx,
                allow_high_floor=False,
            )
            dt = round(dt + (time.perf_counter() - t_len0), 3)
            res2 = {
                **res2,
                "prompt_tokens": int(res2.get("prompt_tokens") or 0) + int(res_cont.get("prompt_tokens") or 0),
                "completion_tokens": int(res2.get("completion_tokens") or 0) + int(res_cont.get("completion_tokens") or 0),
                "finish_reason": res_cont.get("finish_reason", res2.get("finish_reason")),
                "content": (
                    _stitch_tail_continuation(head_clean, res_cont["content"])
                    if str(res_cont.get("content") or "").strip()
                    else res2["content"]
                ),
            }
        except Exception:
            dt = round(dt + (time.perf_counter() - t_len0), 3)

    links_fixed = 0
    candidate_content = str(res2.get("content") or "")
    if sanitize_links:
        candidate_content, links_fixed = sanitize_quarantine_placeholder_links(candidate_content)
        res2 = {**res2, "content": candidate_content}

    vrf_res2 = _run_verify_claims_check(
        candidate_content,
        clean_sources,
        verify_claims_path,
        mem_root,
        cwd_check,
        project_dir=project_dir,
    )

    cur_supported = int(vrf_for_heal.get("supported") or 0)
    cur_unbacked = int(vrf_for_heal.get("unbacked") or 999)
    rep_supported = int(vrf_res2.get("supported") or 0)
    rep_unbacked = int(vrf_res2.get("unbacked") or 999)

    passed_vrf = (vrf_res2.get("returncode") == 0) and not (cur_supported >= 2 and rep_supported == 0)
    non_regressing_improvement = (
        res2.get("finish_reason") == "stop"
        and rep_unbacked < cur_unbacked
        and (cur_supported == 0 or rep_supported >= int(cur_supported * 0.75))
    )
    adopt_res2 = bool(candidate_content.strip()) and (passed_vrf or non_regressing_improvement)

    merged_prompt_tok = int(base_res.get("prompt_tokens") or 0) + int(res2.get("prompt_tokens") or 0)
    merged_comp_tok = int(base_res.get("completion_tokens") or 0) + int(res2.get("completion_tokens") or 0)

    if adopt_res2:
        merged_res = {
            **res2,
            "effort": effort_norm,
            "mode": effective_mode,
            "effective_max_tokens": base_res.get("effective_max_tokens", max_budget),
            "repair_effective_max_tokens": repair_tok_cap,
            "reasoning_effort": base_res.get("reasoning_effort", res2.get("reasoning_effort")),
            "repair_mode": repair_mode,
            "prompt_tokens": merged_prompt_tok,
            "completion_tokens": merged_comp_tok,
        }
        chosen_content = candidate_content
        chosen_vrf = vrf_res2
        rejected_reason = None
    else:
        merged_res = {
            **base_res,
            "content": draft_for_heal,
            "effort": effort_norm,
            "mode": effective_mode,
            "repair_effective_max_tokens": repair_tok_cap,
            "repair_mode": repair_mode,
            "repair_rejected_reason": (
                f"repair_{res2.get('finish_reason', 'unknown')}_"
                f"supported_{rep_supported}_vs_{cur_supported}_unbacked_{rep_unbacked}_vs_{cur_unbacked}"
            ),
            "prompt_tokens": merged_prompt_tok,
            "completion_tokens": merged_comp_tok,
        }
        chosen_content = draft_for_heal
        chosen_vrf = vrf_for_heal
        links_fixed = 0
        rejected_reason = merged_res["repair_rejected_reason"]

    return {
        "res": merged_res,
        "content": chosen_content,
        "vrf_after": chosen_vrf,
        "vrf_attempt": vrf_res2,
        "elapsed_s": dt,
        "adopted": adopt_res2,
        "verified": bool(adopted := adopt_res2) and passed_vrf,
        "links_fixed": links_fixed,
        "rejected_reason": rejected_reason,
    }


def _should_trigger_chunked_digest(
    unsliced_count: int,
    explicit_slices: list[tuple[Path, int, int]],
    total_raw_bytes: int,
    *,
    chunk_threshold: int,
    for_sync_guard: bool = False,
) -> bool:
    """Return True when payload bytes or multi-file explicit `#L` slice fan-out warrants map-reduce."""
    if unsliced_count > 0 and total_raw_bytes > chunk_threshold:
        return True
    slice_count_floor = 9 if for_sync_guard else 5
    distinct_slice_files = len({fp for fp, _, _ in explicit_slices})
    if len(explicit_slices) >= slice_count_floor and distinct_slice_files >= 3:
        return True
    return len(explicit_slices) >= 2 and total_raw_bytes > chunk_threshold


def _apprentice_digest_sync(
    prompt: str,
    context_files: list[str] | None = None,
    repo: str = "",
    include_git_diff: bool = False,
    effort: str | None = None,
    mode: str | None = None,
    invocation_tier: str = "auto",
    max_tokens: int | None = None,
    verify_claims: bool = True,
    async_job: bool = False,
    prev_call_id: str | None = None,
    prev_verdict: str | None = None,
    prev_verdict_note: str = "",
) -> dict[str, Any]:
    """Compress bounded files, `#Lstart-Lend` slices, or git diffs via local Bionic (async_job & verify_claims enabled by default)."""
    _ensure_live_process_cwd()
    try:
        prev_res = _maybe_apply_prev_verdict(prev_call_id, prev_verdict, prev_verdict_note)
        effort_norm, req_mode = apprentice_engine.resolve_effort_and_mode(effort, mode)
        tier, max_eta = _resolve_eta_cap(invocation_tier, effort_norm)
        api_url = apprentice_engine.validate_loopback_url(apprentice_engine.resolve_default_api_url())
        sys_prompt, sys_src = apprentice_engine.load_system_prompt()
        repo_root = Path(repo) if repo.strip() else None
        repo_resolved = repo_root.resolve(strict=False) if repo_root else None
        validated_files, slice_items, slice_map = apprentice_engine.parse_and_validate_context_items(
            list(context_files or []),
            repo_root=repo_root,
            require_exists=True,
        )
        if not prompt.strip():
            raise ValueError("Prompt must be non-empty.")

        if async_job:
            apprentice_engine.preflight_live_inference(api_url, apprentice_engine.DEFAULT_MODEL_ID, req_mode)
            job_info = apprentice_engine.submit_async_job(
                {
                    "kind": "digest",
                    "kwargs": {
                        "prompt": prompt,
                        "context_files": list(context_files or []),
                        "repo": repo,
                        "include_git_diff": bool(include_git_diff),
                        "effort": effort_norm,
                        "mode": req_mode,
                        "invocation_tier": tier,
                        "max_tokens": max_tokens,
                        "verify_claims": bool(verify_claims),
                        "async_job": False,
                    },
                }
            )
            sc_str = _scorecard_suffix()
            return {
                **job_info,
                "effort": effort_norm,
                "prev_verdict_update": prev_res,
                "scorecard": sc_str,
                "user_notice": (
                    f"[APPRENTICE NOTICE] Launched async digest sprint {job_info['job_id']} "
                    f"(effort={effort_norm}, mode={req_mode}). Collect with apprentice_control(action='job-collect', job_id='{job_info['job_id']}'). | {sc_str}"
                ),
            }

        srv, effective_mode = apprentice_engine.preflight_live_inference(api_url, apprentice_engine.DEFAULT_MODEL_ID, req_mode)
        loaded_ctx = srv.get("loaded_context_length")
        max_toks = apprentice_engine.resolve_effective_max_tokens(effective_mode, max_tokens)
        sys_bytes = len(sys_prompt.encode("utf-8"))
        has_code = apprentice_engine.is_code_heavy_payload(validated_files, bool(include_git_diff))

        unsliced_unique = list(dict.fromkeys(fp for fp, sl in zip(validated_files, slice_items) if sl is None))
        unsliced_set = set(unsliced_unique)
        explicit_slices = [
            (fp, sl[0], sl[1])
            for fp, sl in zip(validated_files, slice_items)
            if sl is not None and fp not in unsliced_set
        ]
        unsliced_raw_bytes = sum(vf.stat().st_size for vf in unsliced_unique) if unsliced_unique else 0
        slice_raw_bytes = 0
        if explicit_slices:
            _lines_cache: dict[Path, list[str]] = {}
            for fp_s, s_l, e_l in explicit_slices:
                if fp_s not in _lines_cache:
                    _lines_cache[fp_s] = fp_s.read_text(encoding="utf-8", errors="replace").splitlines()
                all_l = _lines_cache[fp_s]
                slice_raw_bytes += len("\n".join(all_l[max(0, s_l - 1) : max(0, e_l)]).encode("utf-8"))
        total_raw_file_bytes = unsliced_raw_bytes + slice_raw_bytes
        chunk_threshold = 42000 if effective_mode == "deep" else 36000
        use_auto_chunk = (
            effective_mode in {"fast", "deep"}
            and not include_git_diff
            and _should_trigger_chunked_digest(
                len(unsliced_unique),
                explicit_slices,
                total_raw_file_bytes,
                chunk_threshold=chunk_threshold,
            )
        )

        length_healed = False
        initial_elapsed_s = 0.0
        heal_elapsed_s = 0.0
        heal_error: str | None = None
        chunk_info: dict[str, Any] | None = None
        kept_labeled_blocks: list[str] = []

        if use_auto_chunk:
            unsliced_chunks = apprentice_engine.plan_line_preserving_chunks(unsliced_unique, target_chunk_bytes=20000)
            raw_chunks = unsliced_chunks + explicit_slices
            batches = apprentice_engine.pack_chunk_batches(
                raw_chunks,
                max_batch_bytes=22000,
                max_batch_lines=460,
                max_slices_per_batch=4,
            )
            prompt_low = prompt.lower()
            needs_cross_slice_reasoning = effective_mode == "deep" and any(
                kw in prompt_low
                for kw in (
                    "compare",
                    "discrepanc",
                    "conflict",
                    "audit",
                    "mismatch",
                    "cross-reference",
                    "diff",
                    "contradict",
                    "inconsisten",
                    "cross-slice",
                )
            )
            wave_eta = apprentice_engine.estimate_chunked_eta(
                effective_mode=effective_mode,
                prompt_bytes=len(prompt.encode("utf-8")),
                sys_prompt_bytes=sys_bytes,
                total_payload_bytes=total_raw_file_bytes,
                batch_count=len(batches),
                max_eta_seconds=max_eta,
                has_code_context=has_code,
                loaded_ctx_override=loaded_ctx,
                needs_cross_slice_reasoning=needs_cross_slice_reasoning,
            )
            waves = int(wave_eta["waves"])
            total_pred_eta = float(wave_eta["predicted_eta_s"])
            chunk_soft_over = bool(wave_eta.get("soft_eta_exceeded"))
            if total_pred_eta > max_eta and effective_mode == "cpu-bg":
                err_eta = {
                    **wave_eta,
                    "tripped": True,
                    "hard_tripped": True,
                    "chunks": len(raw_chunks),
                    "batches": len(batches),
                }
                apprentice_engine.record_usage_telemetry(
                    {
                        "cmd": "apprentice_digest",
                        "effort": wave_eta["effort"],
                        "invocation_tier": tier,
                        "mode": effective_mode,
                        "est_prompt_tokens": wave_eta["est_prompt_tokens"],
                        "predicted_eta_s": total_pred_eta,
                        "max_eta_seconds": max_eta,
                        "tripped": True,
                        "is_chunked": True,
                        "chunks": len(raw_chunks),
                        "batches": len(batches),
                    }
                )
                raise apprentice_engine.SidecarEtaTrippedError(
                    f"[ETA_CIRCUIT_BREAKER_TRIPPED] Chunked digest ({len(raw_chunks)} slices / {len(batches)} batches / {waves} waves, {total_pred_eta}s) exceeds {max_eta}s cap.",
                    err_eta,
                )

            chunk_counts: dict[Path, int] = {}
            for ch_path, _, _ in raw_chunks:
                chunk_counts[ch_path] = chunk_counts.get(ch_path, 0) + 1
            file_meta = []
            for vf, sl in zip(validated_files, slice_items):
                rel_l = str(vf.relative_to(repo_resolved)) if repo_resolved else vf.name
                if sl is not None and vf not in unsliced_set:
                    file_meta.append(
                        {
                            "path": str(vf),
                            "label": f"{rel_l}#L{sl[0]}-L{sl[1]}",
                            "slice": [sl[0], sl[1]],
                            "chunks": 1,
                        }
                    )
                elif sl is None:
                    file_meta.append(
                        {
                            "path": str(vf),
                            "label": rel_l,
                            "bytes": vf.stat().st_size,
                            "chunks": chunk_counts.get(vf, 0),
                        }
                    )
            base_chunk_max_toks = (
                min(1800, max(600, max_toks // 3))
                if effective_mode == "deep"
                else min(1200, max(450, max_toks // 3))
            )

            def _run_batch(task_item: tuple[int, list[tuple[Path, int, int]]]) -> tuple[int, str, dict[str, Any], str]:
                idx, batch_slices = task_item
                if len(batch_slices) == 1:
                    fpath, s_line, e_line = batch_slices[0]
                    rel_label = str(fpath.relative_to(repo_resolved)) if repo_resolved else fpath.name
                    span_label = f"{rel_label}#L{s_line}-L{e_line}"
                    chunk_prompt = (
                        f"[MAPPER SLICE {idx + 1}/{len(batches)} ({rel_label}#L{s_line}-L{e_line}) — YOU ARE INSPECTING `{rel_label}`]\n"
                        f"Overall user goal (other parallel slices inspect the remaining files/sections):\n"
                        f"{prompt.strip()}\n\n"
                        f"TASK FOR THIS SLICE ONLY:\n"
                        f"Extract EVERY matching item, fastener, material/infill setting, quantitative figure, symbol, or fact "
                        f"ACTUALLY PRESENT in `{rel_label}#L{s_line}-L{e_line}` that contributes to ANY part of the user goal above. "
                        f"`{rel_label}` IS one of the target files referenced in the user goal—do NOT wait for other files to compare; "
                        f"report this slice's relevant facts now.\n"
                        f"- Cite exact `{rel_label}#L<start>-L<end>` anchors verbatim (`StartLine <= EndLine`).\n"
                        f"- Do NOT emit `[TBD]` or mention items absent from lines L{s_line}-L{e_line} "
                        f"(other chunks cover the rest of `{rel_label}` and other files).\n"
                        f"- Only reply `NONE` if lines L{s_line}-L{e_line} contain ZERO facts relevant to ANY part of the user goal. Zero preamble."
                    )
                    batch_max_toks = base_chunk_max_toks
                else:
                    lbl_list = [
                        f"`{(str(fp.relative_to(repo_resolved)) if repo_resolved else fp.name)}#L{sl}-L{el}`"
                        for fp, sl, el in batch_slices
                    ]
                    span_label = ", ".join(
                        f"{fp.name}#L{sl}-L{el}" for fp, sl, el in batch_slices
                    )
                    chunk_prompt = (
                        f"[MAPPER BATCH {idx + 1}/{len(batches)} — YOU ARE INSPECTING MULTIPLE FILES: {', '.join(lbl_list)}]\n"
                        f"Overall user goal (other parallel batches inspect any remaining files/sections):\n"
                        f"{prompt.strip()}\n\n"
                        f"TASK FOR THIS BATCH:\n"
                        f"Extract EVERY matching item, fastener, metric, setting, status, or fact ACTUALLY PRESENT in each file in this batch.\n"
                        f"- Cover EVERY file listed in this batch; prefix or cite exact `<relative_path>#L<start>-L<end>` verbatim (`StartLine <= EndLine`).\n"
                        f"- Do NOT emit `[TBD]` for items absent from these files unless specifically asked.\n"
                        f"- Only reply `NONE` if ALL files in this batch contain ZERO relevant facts. Zero preamble."
                    )
                    batch_max_toks = (
                        min(2400, max(1200, 650 * len(batch_slices)))
                        if effective_mode == "deep"
                        else min(2048, max(1000, 600 * len(batch_slices)))
                    )

                ch_assembled, _ = apprentice_engine.assemble_prompt_payload(
                    user_prompt=chunk_prompt,
                    context_files=[fp for fp, _, _ in batch_slices],
                    repo_root=repo_resolved,
                    include_git_diff=False,
                    sys_prompt=sys_prompt,
                    context_slices=[(sl, el) for _, sl, el in batch_slices],
                )
                ch_res = apprentice_engine.invoke_chat_completion(
                    api_url=api_url,
                    model_id=apprentice_engine.DEFAULT_MODEL_ID,
                    mode="fast",
                    system_prompt=sys_prompt,
                    user_content=ch_assembled,
                    max_tokens=batch_max_toks,
                    timeout_s=min(max(max_eta + 60.0, 150.0), 210.0),
                    preflight_checked=True,
                    loaded_ctx=loaded_ctx,
                    allow_high_floor=False,
                )
                return idx, span_label, ch_res, ch_assembled

            t_chunk0 = time.perf_counter()
            try:
                with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
                    chunk_outcomes = list(pool.map(_run_batch, enumerate(batches)))
            except Exception as exc:
                err_dt = round(time.perf_counter() - t_chunk0, 3)
                apprentice_engine.record_usage_telemetry(
                    {
                        "cmd": "apprentice_digest",
                        "effort": wave_eta["effort"],
                        "invocation_tier": tier,
                        "mode": effective_mode,
                        "est_prompt_tokens": wave_eta["est_prompt_tokens"],
                        "predicted_eta_s": total_pred_eta,
                        "max_eta_seconds": max_eta,
                        "tripped": False,
                        "soft_eta_exceeded": False,
                        "http_error": True,
                        "is_chunked": True,
                        "chunks": len(raw_chunks),
                        "batches": len(batches),
                        "verdict": "corrected",
                        "elapsed_s": err_dt,
                        "observed_tg_tok_s": None,
                        "finish_reason": "error",
                    }
                )
                apprentice_engine.record_call_outcome(
                    verdict="corrected",
                    cmd="apprentice_digest",
                    effort=wave_eta["effort"],
                    mode=effective_mode,
                    elapsed_s=err_dt,
                    note=str(exc)[:180],
                )
                raise

            chunk_outcomes.sort(key=lambda it: it[0])
            kept_texts: list[str] = []
            repair_slices: list[str] = []
            tot_p_tok = 0
            tot_c_tok = 0
            tot_kv_wait_s = 0.0
            all_stop = True
            chunks_truncated_count = 0
            for _idx, _span_lbl, ch_res, ch_asm in chunk_outcomes:
                tot_p_tok += int(ch_res.get("prompt_tokens") or 0)
                tot_c_tok += int(ch_res.get("completion_tokens") or 0)
                tot_kv_wait_s += float(ch_res.get("kv_wait_s") or 0.0)
                if ch_res.get("finish_reason") != "stop":
                    all_stop = False
                    chunks_truncated_count += 1
                cleaned_ch = _filter_chunk_extract_lines(str(ch_res.get("content") or ""))
                if cleaned_ch:
                    kept_texts.append(cleaned_ch)
                    kept_labeled_blocks.append(f"[Slice {_span_lbl}]\n{cleaned_ch}")
                    repair_slices.append(ch_asm)

            reduced_used = len(kept_texts) > 1
            reduce_reasoning_eff = "none"
            reduce_prompt_used = ""
            final_finish = "stop" if all_stop else "length"
            if reduced_used:
                reduce_prompt = (
                    f"{prompt.strip()}\n\n"
                    "Below are verbatim per-slice extracts from the target file(s). "
                    "Merge, deduplicate, and filter them so ONLY exact items requested above remain. "
                    "Preserve every exact `<file>#L<start>-L<end>` anchor and literal verbatim; never alter line numbers or invent values. "
                    "Never invent parenthetical example numbers (e.g., 0.8mm), prefix `Warning:`/`Caution:` on any `[!WARNING]`/`[!CAUTION]` citation, "
                    "and ensure any `[CALC: ...]` uses ONLY literal source numbers on the left of `=`. Zero preamble.\n\n"
                    + "\n\n".join(kept_labeled_blocks)
                )
                reduce_prompt_used = reduce_prompt
                if needs_cross_slice_reasoning:
                    reduce_prompt += (
                        "\n\n[MERGE-ONLY THINKING LIMIT: Facts are already extracted above; "
                        "keep <think> under 300 words and emit final verified bullets immediately.]"
                    )
                    reduce_prompt_used = reduce_prompt
                    red_reasoning_override = None
                    red_max_toks = min(max_toks, 4608)
                    red_allow_high_floor = True
                elif effective_mode == "deep":
                    # Probe proved Bionic treats low/medium == high; pure merge uses 'none' to avoid 200s CoT blowups
                    red_reasoning_override = "none"
                    red_max_toks = min(max_toks, 3072)
                    red_allow_high_floor = False
                else:
                    red_reasoning_override = "none"
                    red_max_toks = (
                        min(3072, max(max_toks, 2048 + 256 * len(kept_labeled_blocks)))
                        if (max_tokens is None and len(kept_labeled_blocks) >= 3)
                        else max_toks
                    )
                    red_allow_high_floor = False
                try:
                    red_res = apprentice_engine.invoke_chat_completion(
                        api_url=api_url,
                        model_id=apprentice_engine.DEFAULT_MODEL_ID,
                        mode=effective_mode,
                        system_prompt=sys_prompt,
                        user_content=reduce_prompt,
                        max_tokens=red_max_toks,
                        timeout_s=240.0 if needs_cross_slice_reasoning else 150.0,
                        preflight_checked=True,
                        loaded_ctx=loaded_ctx,
                        allow_high_floor=red_allow_high_floor,
                        reasoning_effort_override=red_reasoning_override,
                    )
                    reduce_reasoning_eff = str(red_res.get("reasoning_effort") or ("high" if needs_cross_slice_reasoning else "none"))
                    tot_p_tok += int(red_res.get("prompt_tokens") or 0)
                    tot_c_tok += int(red_res.get("completion_tokens") or 0)
                    tot_kv_wait_s += float(red_res.get("kv_wait_s") or 0.0)
                    if red_res.get("reasoning_recovered"):
                        length_healed = True
                    red_txt = str(red_res.get("content") or "").strip()
                    if red_txt:
                        combined_text = red_txt
                        final_finish = str(red_res.get("finish_reason") or "stop")
                    else:
                        combined_text = "\n".join(kept_texts)
                except Exception as red_exc:
                    heal_error = f"chunk_reduce_failed: {red_exc}"
                    combined_text = "\n".join(kept_texts)
            else:
                combined_text = "\n".join(kept_texts) if kept_texts else "No matching items found in inspected slices."

            chunk_wall = round(time.perf_counter() - t_chunk0, 3)
            initial_elapsed_s = chunk_wall
            assembled = "\n".join(repair_slices[:4]) if repair_slices else prompt.strip()
            wall_tps = round(tot_c_tok / chunk_wall, 2) if chunk_wall > 0 and tot_c_tok > 0 else None
            res = {
                "model": chunk_outcomes[0][2].get("model", apprentice_engine.DEFAULT_MODEL_ID),
                "effort": effort_norm,
                "mode": effective_mode,
                "reasoning_effort": reduce_reasoning_eff,
                "effective_max_tokens": base_chunk_max_toks,
                "prompt_tokens": tot_p_tok,
                "completion_tokens": tot_c_tok,
                "elapsed_s": chunk_wall,
                "kv_wait_s": round(tot_kv_wait_s, 3),
                "decode_tok_s": None,
                "wall_tok_s": wall_tps,
                "observed_tg_tok_s": wall_tps,
                "finish_reason": final_finish,
                "chunk_truncated": not all_stop,
                "chunks_truncated_count": chunks_truncated_count,
                "content": combined_text,
            }
            eta = {
                **wave_eta,
                "predicted_eta_s": total_pred_eta,
                "effort": effort_norm,
                "soft_eta_exceeded": chunk_soft_over,
                "soft_eta_advisory": chunk_soft_over,
                "chunks": len(raw_chunks),
                "batches": len(batches),
            }
            chunk_info = {
                "enabled": True,
                "chunks": len(raw_chunks),
                "batches": len(batches),
                "workers": 2,
                "reduced": reduced_used,
            }
            apprentice_engine.record_usage_telemetry(
                {
                    "cmd": "apprentice_digest",
                    "effort": effort_norm,
                    "invocation_tier": tier,
                    "mode": effective_mode,
                    "est_prompt_tokens": tot_p_tok,
                    "predicted_eta_s": total_pred_eta,
                    "max_eta_seconds": max_eta,
                    "tripped": False,
                    "soft_eta_exceeded": chunk_soft_over,
                    "is_chunked": True,
                    "chunks": len(raw_chunks),
                    "batches": len(batches),
                    "prompt_tokens": tot_p_tok,
                    "completion_tokens": tot_c_tok,
                    "elapsed_s": chunk_wall,
                    "kv_wait_s": round(tot_kv_wait_s, 3),
                    "observed_tg_tok_s": res["observed_tg_tok_s"],
                    "finish_reason": res["finish_reason"],
                }
            )
            initial_elapsed_s = float(res["elapsed_s"])
            cont_base_prompt = reduce_prompt_used if (reduced_used and reduce_prompt_used) else assembled
        else:
            effective_prompt = prompt.strip()
            if effort_norm == "standard" and max_toks >= 256:
                effective_prompt += (
                    "\n\n[Format: terse `- ` bullets starting on line 1; include ONLY requested fields + `#Lstart-Lend` "
                    "(omit unrequested table columns/notes, intro sentences, prompt summary counts, and uncalculated group totals).]"
                )
            elif effort_norm == "high":
                effective_prompt += CONCISE_HIGH_THINKING_HINT

            assembled, file_meta = apprentice_engine.assemble_prompt_payload(
                user_prompt=effective_prompt,
                context_files=validated_files,
                repo_root=repo_resolved,
                include_git_diff=bool(include_git_diff),
                sys_prompt=sys_prompt,
                context_slices=slice_items,
            )
            prompt_bytes = sys_bytes + len(assembled.encode("utf-8"))
            eta = apprentice_engine._enforce_eta_or_raise(
                mode=effective_mode,
                prompt_bytes=prompt_bytes,
                max_tokens=max_toks,
                max_eta_seconds=max_eta,
                expected_turns=1,
                force_slow=False,
                cmd_name="apprentice_digest",
                invocation_tier=tier,
                has_code_context=has_code,
                loaded_ctx_override=loaded_ctx,
                calibrated_output=True,
                allow_soft_eta_overrun=(effective_mode != "cpu-bg"),
                sys_prompt_bytes=sys_bytes,
                include_git_diff=bool(include_git_diff),
            )
            t_call0 = time.perf_counter()
            try:
                res = apprentice_engine.invoke_chat_completion(
                    api_url=api_url,
                    model_id=apprentice_engine.DEFAULT_MODEL_ID,
                    mode=effective_mode,
                    system_prompt=sys_prompt,
                    user_content=assembled,
                    max_tokens=max_toks,
                    timeout_s=min(max(max_eta + 120.0, 240.0), 300.0) if effective_mode == "deep" else min(max(max_eta + 60.0, 150.0), 300.0),
                    preflight_checked=True,
                    loaded_ctx=loaded_ctx,
                    est_prompt_tokens=eta["est_prompt_tokens"],
                )
            except Exception as exc:
                err_dt = round(time.perf_counter() - t_call0, 3)
                apprentice_engine.record_usage_telemetry(
                    {
                        "cmd": "apprentice_digest",
                        "effort": eta["effort"],
                        "invocation_tier": tier,
                        "mode": effective_mode,
                        "est_prompt_tokens": eta["est_prompt_tokens"],
                        "predicted_eta_s": eta["predicted_eta_s"],
                        "max_eta_seconds": max_eta,
                        "tripped": False,
                        "soft_eta_exceeded": eta["soft_eta_exceeded"],
                        "http_error": True,
                        "verdict": "corrected",
                        "elapsed_s": err_dt,
                        "observed_tg_tok_s": None,
                        "finish_reason": "error",
                    }
                )
                apprentice_engine.record_call_outcome(
                    verdict="corrected",
                    cmd="apprentice_digest",
                    effort=eta["effort"],
                    mode=effective_mode,
                    elapsed_s=err_dt,
                    soft_eta_exceeded=eta["soft_eta_exceeded"],
                    note=str(exc)[:180],
                )
                raise

            apprentice_engine.record_usage_telemetry(
                {
                    "cmd": "apprentice_digest",
                    "effort": eta["effort"],
                    "invocation_tier": tier,
                    "mode": effective_mode,
                    "est_prompt_tokens": eta["est_prompt_tokens"],
                    "predicted_eta_s": eta["predicted_eta_s"],
                    "max_eta_seconds": max_eta,
                    "tripped": False,
                    "soft_eta_exceeded": eta["soft_eta_exceeded"],
                    "synthetic_fault": bool(res.get("synthetic_fault")),
                    "prompt_tokens": res["prompt_tokens"],
                    "completion_tokens": res["completion_tokens"],
                    "elapsed_s": res["elapsed_s"],
                    "kv_wait_s": res.get("kv_wait_s", 0.0),
                    "observed_tg_tok_s": res["observed_tg_tok_s"],
                    "finish_reason": res["finish_reason"],
                }
            )
            initial_elapsed_s = float(res["elapsed_s"])
            if res.get("reasoning_recovered"):
                length_healed = True
            cont_base_prompt = assembled

        cont_hops = 0
        cont_mode = "fast" if effective_mode in ("fast", "deep") else effective_mode
        cont_budget_s = 120.0 if effective_mode == "deep" else 75.0
        while res["finish_reason"] == "length" and res["content"].strip() and cont_hops < 2 and heal_elapsed_s < cont_budget_s:
            cont_hops += 1
            t_len0 = time.perf_counter()
            head_clean, tail_ctx = _prepare_tail_continuation(res["content"])
            cont_prompt = (
                f"{cont_base_prompt}\n\n"
                "Your previous response hit the output token limit after completing these lines:\n"
                f"{tail_ctx}\n\n"
                "Continue seamlessly starting with the NEXT item/line immediately after the lines above. "
                "Do NOT repeat items already listed. Use compact single-line `- ` bullets citing exact `#Lstart-Lend` anchors and verbatim source literals only; zero preamble."
            )
            cont_max_toks = 640 if effective_mode == "cpu-bg" else (3072 if effective_mode == "deep" else 2560)
            cont_timeout_s = 60.0 if effective_mode == "cpu-bg" else (150.0 if effective_mode == "deep" else 120.0)
            try:
                res_cont = apprentice_engine.invoke_chat_completion(
                    api_url=api_url,
                    model_id=apprentice_engine.DEFAULT_MODEL_ID,
                    mode=cont_mode,
                    system_prompt=sys_prompt,
                    user_content=cont_prompt,
                    max_tokens=cont_max_toks,
                    timeout_s=cont_timeout_s,
                    preflight_checked=True,
                    loaded_ctx=loaded_ctx,
                    allow_high_floor=False,
                )
            except Exception as cont_exc:
                heal_elapsed_s += round(time.perf_counter() - t_len0, 3)
                heal_error = f"length_continuation_failed: {cont_exc}"
                break
            heal_elapsed_s += round(time.perf_counter() - t_len0, 3)
            apprentice_engine.record_usage_telemetry(
                {
                    "cmd": "apprentice_digest_length_retry",
                    "effort": eta["effort"],
                    "invocation_tier": tier,
                    "mode": effective_mode,
                    "est_prompt_tokens": res_cont["prompt_tokens"],
                    "predicted_eta_s": 0.0,
                    "max_eta_seconds": cont_timeout_s,
                    "tripped": False,
                    "is_retry": True,
                    "hop": cont_hops,
                    "prompt_tokens": res_cont["prompt_tokens"],
                    "completion_tokens": res_cont["completion_tokens"],
                    "elapsed_s": res_cont["elapsed_s"],
                    "kv_wait_s": res_cont.get("kv_wait_s", 0.0),
                    "observed_tg_tok_s": res_cont["observed_tg_tok_s"],
                    "finish_reason": res_cont["finish_reason"],
                }
            )
            if not res_cont["content"].strip():
                res = {
                    **res,
                    "completion_tokens": int(res["completion_tokens"]) + int(res_cont["completion_tokens"]),
                }
                break
            stitched = _stitch_tail_continuation(head_clean, res_cont["content"])
            res = {
                **res,
                "content": stitched,
                "completion_tokens": int(res["completion_tokens"]) + int(res_cont["completion_tokens"]),
                "finish_reason": res_cont["finish_reason"],
            }
            length_healed = True

        vrf_res: dict[str, Any] = {"ran": False}
        claims_verified: bool | None = None
        verify_healed = False

        if verify_claims and validated_files and include_git_diff:
            vrf_res = {"ran": False, "skipped_reason": "git_diff_head_delta"}
        elif verify_claims and validated_files:
            hom_root, mem_root = _resolve_homunculus_and_memory()
            verify_claims_path = hom_root / "skills" / "claim-verification" / "scripts" / "verify_claims.py"
            if repo_resolved is not None:
                clean_sources, _ = select_collision_free_sources(repo_resolved, validated_files)
            else:
                seen_bn: set[str] = set()
                clean_sources = []
                for vf in validated_files:
                    if vf.name not in seen_bn:
                        seen_bn.add(vf.name)
                        clean_sources.append(vf)
            cwd_check = repo_resolved or validated_files[0].parent
            vrf_res = _run_verify_claims_check(res["content"], clean_sources, verify_claims_path, mem_root, cwd_check)
            if vrf_res.get("ran"):
                if vrf_res.get("returncode") == 0:
                    claims_verified = True
                else:
                    t_heal0 = time.perf_counter()
                    draft_for_heal = res["content"]
                    vrf_for_heal = vrf_res
                    try:
                        surg = _surgical_repair_unbacked_lines(
                            draft_text=draft_for_heal,
                            vrf_res=vrf_for_heal,
                            context_sources=validated_files,
                            clean_sources=clean_sources,
                            repo_resolved=repo_resolved,
                            verify_claims_path=verify_claims_path,
                            mem_root=mem_root,
                            cwd_check=cwd_check,
                            api_url=api_url,
                            sys_prompt=sys_prompt,
                            loaded_ctx=loaded_ctx,
                            tier=tier,
                            eta=eta,
                            cmd_name_prefix="apprentice_digest",
                        )
                    except Exception:
                        surg = None

                    if surg is not None:
                        res = {
                            **res,
                            "prompt_tokens": int(res.get("prompt_tokens") or 0) + int(surg["prompt_tokens"]),
                            "completion_tokens": int(res.get("completion_tokens") or 0) + int(surg["completion_tokens"]),
                        }
                        if surg.get("verified"):
                            heal_elapsed_s = round(heal_elapsed_s + (time.perf_counter() - t_heal0), 3)
                            res = {**res, "content": surg["content"]}
                            vrf_res = {
                                "ran": True,
                                "returncode": 0,
                                "elapsed_ms": surg["vrf_after"].get("elapsed_ms"),
                                "surgical_repair": True,
                                "initial": vrf_res,
                                "after_heal": surg["vrf_after"],
                            }
                            verify_healed = True
                            claims_verified = True
                        elif int(surg["vrf_after"].get("unbacked", 999)) < int(vrf_for_heal.get("unbacked", 999)):
                            draft_for_heal = surg["content"]
                            vrf_for_heal = surg["vrf_after"]

                    if claims_verified is not True:
                        fail_detail = _format_compact_verify_failures(vrf_for_heal, max_chars=2800)
                        repair_ctx = (
                            _build_chunked_repair_context(
                                prompt,
                                draft_for_heal,
                                validated_files,
                                repo_resolved,
                                kept_labeled_blocks,
                                unbacked_claims=vrf_for_heal.get("unbacked_claims"),
                            )
                            if use_auto_chunk
                            else assembled
                        )
                        repair_prompt = (
                            f"{repair_ctx}\n\nYour previous draft failed deterministic claim verification:\n{fail_detail}\n"
                            "CRITICAL REPAIR RULES:\n"
                            "1. DELETE any intro or heading sentence so line 1 starts directly with `- `.\n"
                            "2. DELETE any unbacked summary counts echoed from the prompt, uncalculated group totals, or invalid `[CALC: ...]` labels (if `[CALC: ...]` is used, the left side of `=` MUST contain ONLY source-verbatim integers/operators like `[CALC: 4 + 1 + 1 + 2 = 8]` — NEVER variable words like `Total` AND NEVER derived subtotals not literally printed in source lines; expand sums into literal source numbers or omit `[CALC:]` completely).\n"
                            "3. Never invent parenthetical example numbers/units like `(e.g., 0.8mm)`; if a cited source slice lies inside a `> [!WARNING]` or `> [!CAUTION]` block, explicitly include `Warning:` or `Caution:` / the hazard qualifier on that bullet; for QUALIFIED_QUANTITY(...) failures, use the exact qualified quantity from source (e.g., `~2` / `approx` / `(2)` instead of bare `Qty 2`) or remove redundant duplicates.\n"
                            "4. Keep ONLY exact source literals, units, counts, and `#Lstart-Lend` anchors present in the context above; NEVER cite YAML frontmatter (`---`...`---`) lines, and on `.patch`/`.diff` audits cite ONLY the `.patch`'s own `#L` lines (`<=` its total lines) instead of missing external files; insert `[TBD: ...]` for missing values.\n\n"
                            f"Previous draft:\n{draft_for_heal}\n"
                        )
                        try:
                            rep_out = _run_full_repair_with_guard(
                                repair_prompt=repair_prompt,
                                draft_for_heal=draft_for_heal,
                                vrf_for_heal=vrf_for_heal,
                                base_res=res,
                                effective_mode=effective_mode,
                                effort_norm=effort_norm,
                                max_budget=max_toks,
                                api_url=api_url,
                                sys_prompt=sys_prompt,
                                loaded_ctx=loaded_ctx,
                                clean_sources=clean_sources,
                                verify_claims_path=verify_claims_path,
                                mem_root=mem_root,
                                cwd_check=cwd_check,
                                tier=tier,
                                eta=eta,
                                telemetry_cmd="apprentice_digest_verify_retry",
                            )
                            heal_elapsed_s = round(heal_elapsed_s + float(rep_out["elapsed_s"]), 3)
                            res = rep_out["res"]
                            vrf_res = {
                                "ran": True,
                                "returncode": rep_out["vrf_after"].get("returncode"),
                                "elapsed_ms": rep_out["vrf_after"].get("elapsed_ms"),
                                "initial": vrf_res,
                                "after_heal": rep_out["vrf_after"],
                                **({"attempted_heal": rep_out["vrf_attempt"]} if not rep_out["adopted"] else {}),
                            }
                            verify_healed = bool(rep_out["adopted"])
                            claims_verified = rep_out["verified"]
                        except Exception as heal_exc:
                            heal_elapsed_s = round(heal_elapsed_s + (time.perf_counter() - t_heal0), 3)
                            heal_error = f"verify_repair_failed: {heal_exc}"
                            claims_verified = False

        if res["finish_reason"] != "stop" or claims_verified is False or heal_error is not None:
            verdict = "corrected"
        elif length_healed or verify_healed:
            verdict = "healed"
        else:
            verdict = "clean"

        total_elapsed_s = round(initial_elapsed_s + heal_elapsed_s, 3)
        if heal_elapsed_s > 0:
            res = {**res, "elapsed_s": total_elapsed_s}

        sc_rec = apprentice_engine.record_call_outcome(
            verdict=verdict,
            cmd="apprentice_digest",
            effort=eta["effort"],
            mode=effective_mode,
            elapsed_s=total_elapsed_s,
            heal_elapsed_s=heal_elapsed_s,
            soft_eta_exceeded=eta.get("soft_eta_exceeded", False),
            note=(heal_error or "")[:180],
        )
        sc_fmt = _scorecard_suffix(sc_rec.get("call_id"))
        out_payload: dict[str, Any] = {
            "ok": True,
            "schema_version": apprentice_engine.SCHEMA_VERSION,
            "call_id": sc_rec.get("call_id"),
            "verdict": verdict,
            "effort": eta["effort"],
            "invocation_tier": tier,
            "system_prompt_source": sys_src,
            "quarantined_draft_warning": "UNVERIFIED LOCAL SIDECAR OUTPUT — verify claims against primary sources before citing.",
            "eta_estimate": eta,
            "context_files": file_meta,
            "verify_claims": vrf_res,
            "claims_verified": claims_verified,
            "heal_elapsed_s": heal_elapsed_s,
            "heal_error": heal_error,
            "slow_self_heal": sc_rec.get("slow_self_heal", False),
            "prev_verdict_update": prev_res,
            "completion": res,
            "scorecard": sc_fmt,
            "user_notice": (
                f"[APPRENTICE NOTICE] Local Bionic ({eta['effort']}/{effective_mode}, {tier}) ran {res['elapsed_s']}s "
                f"({res['prompt_tokens']} prompt / {res['completion_tokens']} out tok, verdict={verdict}). | {sc_fmt}"
            ),
        }
        if chunk_info is not None:
            out_payload["chunked_map_reduce"] = chunk_info
        return out_payload
    except apprentice_engine.SidecarFirewallError as exc:
        return _firewall_error_response(exc, "Digest")
    except apprentice_engine.SidecarEtaTrippedError as exc:
        sc_str = _scorecard_suffix()
        return {
            "ok": False,
            "error_code": "ETA_CIRCUIT_BREAKER_TRIPPED",
            "error": str(exc),
            "eta_estimate": exc.estimate,
            "scorecard": sc_str,
            "user_notice": f"[APPRENTICE NOTICE] ETA breaker handed digest back to frontier thread. | {sc_str}",
        }
    except Exception as exc:
        sc_str = _scorecard_suffix()
        return {
            "ok": False,
            "error_code": "DIGEST_ERROR",
            "error": str(exc),
            "scorecard": sc_str,
            "user_notice": f"[APPRENTICE NOTICE] Digest error: {exc} | {sc_str}",
        }


def _is_heavy_chunked_sync_candidate(op_label: str, kwargs: dict[str, Any]) -> bool:
    """Return True when chunked payload bytes (>36 KB) or large multi-file `#L` slice fan-out (>=9 slices) risks >135s sync deadline."""
    if op_label != "digest" or bool(kwargs.get("include_git_diff")):
        return False
    raw_files = list(kwargs.get("context_files") or [])
    if not raw_files:
        return False
    unsliced_bytes = 0
    slice_bytes = 0
    seen_unsliced: set[Path] = set()
    parsed_slices: list[tuple[Path, int, int]] = []
    lines_cache: dict[Path, list[str]] = {}
    for item in raw_files:
        p, slice_rng = apprentice_engine.parse_context_spec(str(item))
        cand = Path(os.path.expanduser(str(p)))
        if not cand.is_absolute() and kwargs.get("repo"):
            cand = Path(os.path.expanduser(str(kwargs["repo"]))) / cand
        cand_res = cand.resolve(strict=False)
        try:
            if not cand_res.is_file():
                continue
            if slice_rng is None:
                if cand_res not in seen_unsliced:
                    seen_unsliced.add(cand_res)
                    unsliced_bytes += cand_res.stat().st_size
            else:
                lines = lines_cache.setdefault(
                    cand_res,
                    cand_res.read_text(encoding="utf-8", errors="replace").splitlines(),
                )
                s_l, e_l = slice_rng
                slice_bytes += len("\n".join(lines[max(0, s_l - 1) : max(0, e_l)]).encode("utf-8"))
                parsed_slices.append((cand_res, s_l, e_l))
        except OSError:
            return False
    explicit_slices = [item for item in parsed_slices if item[0] not in seen_unsliced]
    return _should_trigger_chunked_digest(
        len(seen_unsliced),
        explicit_slices,
        unsliced_bytes + slice_bytes,
        chunk_threshold=36000,
        for_sync_guard=True,
    )


async def _run_mcp_with_sync_guard(op_label: str, sync_fn: Any, kwargs: dict[str, Any]) -> dict[str, Any]:
    """Run MCP tool synchronously unless HIGH/exclusive/heavy-chunked/explicit multi-pass load risks >135s MCP timeout."""
    if bool(kwargs.get("async_job")):
        return await asyncio.to_thread(sync_fn, **kwargs)
    try:
        effort_norm, _ = apprentice_engine.resolve_effort_and_mode(kwargs.get("effort"), kwargs.get("mode"))
    except ValueError:
        return await asyncio.to_thread(sync_fn, **kwargs)
    tier_norm = str(kwargs.get("invocation_tier") or "auto").strip().lower()
    explicit_multipass = op_label in ("repo_audit", "stage_patch") and tier_norm == "explicit"
    if (
        effort_norm != "high"
        and not explicit_multipass
        and not _is_heavy_chunked_sync_candidate(op_label, kwargs)
        and not apprentice_engine.has_active_exclusive_kv_slot()
    ):
        return await asyncio.to_thread(sync_fn, **kwargs)

    sub = await asyncio.to_thread(sync_fn, **{**kwargs, "async_job": True})
    if not sub.get("ok") or not sub.get("job_id"):
        return sub

    wait_cap = float(MCP_SYNC_WAIT_CAP_SECONDS)
    jres = await asyncio.to_thread(
        apprentice_engine.get_job_status,
        str(sub["job_id"]),
        wait_seconds=wait_cap,
        include_result=True,
    )
    if jres.get("status") == "completed" and isinstance(jres.get("result"), dict):
        out = dict(jres["result"])
        if sub.get("prev_verdict_update") is not None and out.get("prev_verdict_update") is None:
            out["prev_verdict_update"] = sub["prev_verdict_update"]
        return out
    if jres.get("status") == "failed":
        if isinstance(jres.get("result"), dict):
            return dict(jres["result"])
        sc_str = _scorecard_suffix()
        return {
            "ok": False,
            "error_code": "ASYNC_WORKER_ERROR",
            "error": str(jres.get("error") or "Background Bionic worker failed"),
            "job_id": sub["job_id"],
            "scorecard": sc_str,
            "user_notice": f"[APPRENTICE NOTICE] {op_label} worker {sub['job_id']} failed: {jres.get('error')} | {sc_str}",
        }
    sc_str = _scorecard_suffix()
    tier_lbl = "High-effort" if effort_norm == "high" else "Long-running"
    return {
        **sub,
        "auto_promoted_async": True,
        "waited_sync_seconds": wait_cap,
        "scorecard": sc_str,
        "user_notice": (
            f"[APPRENTICE NOTICE] {tier_lbl} {op_label} exceeded {wait_cap:.0f}s sync MCP window; "
            f"continuing cleanly in background as {sub['job_id']} (do NOT re-submit; collect via "
            f"apprentice_control(action='job-collect', job_id='{sub['job_id']}', wait_seconds=120)). | {sc_str}"
        ),
    }


@mcp.tool()
async def apprentice_digest(
    prompt: str,
    context_files: list[str] | None = None,
    repo: str = "",
    include_git_diff: bool = False,
    effort: str | None = None,
    mode: str | None = None,
    invocation_tier: str = "auto",
    max_tokens: int | None = None,
    verify_claims: bool = True,
    async_job: bool = False,
    prev_call_id: str | None = None,
    prev_verdict: str | None = None,
    prev_verdict_note: str = "",
) -> dict[str, Any]:
    """Compress bounded files, `#Lstart-Lend` slices, or git diffs via local Bionic (STANDARD/HIGH, async_job & verify_claims)."""
    return await _run_mcp_with_sync_guard(
        "digest",
        _apprentice_digest_sync,
        {
            "prompt": prompt,
            "context_files": context_files,
            "repo": repo,
            "include_git_diff": include_git_diff,
            "effort": effort,
            "mode": mode,
            "invocation_tier": invocation_tier,
            "max_tokens": max_tokens,
            "verify_claims": verify_claims,
            "async_job": async_job,
            "prev_call_id": prev_call_id,
            "prev_verdict": prev_verdict,
            "prev_verdict_note": prev_verdict_note,
        },
    )


_mcp_apprentice_digest_coro = apprentice_digest
apprentice_digest = _apprentice_digest_sync  # type: ignore[assignment]


SKIP_SOURCE_DIRS = frozenset(
    {".git", "__pycache__", "node_modules", ".venv", "venv", "dist", "build", ".cache"}
)


def _discover_repo_sources(repo_resolved: Path) -> list[Path]:
    exts = {".md", ".py", ".cfg", ".json", ".toml", ".yaml", ".yml", ".csv", ".txt"}
    out: list[Path] = []
    for cand in sorted(repo_resolved.rglob("*")):
        if not cand.is_file():
            continue
        rel_parts = cand.relative_to(repo_resolved).parts
        if SKIP_SOURCE_DIRS & set(rel_parts):
            continue
        if cand.suffix.lower() in exts and not apprentice_engine._inspect_path_security(cand):
            out.append(cand)
    return out


def _apprentice_repo_audit_sync(
    repo: str,
    project: str,
    name: str,
    title: str,
    reason: str,
    prompt: str,
    context_files: list[str] | None = None,
    include_git_diff: bool = False,
    effort: str | None = None,
    mode: str | None = None,
    invocation_tier: str = "explicit",
    max_tokens: int | None = None,
    overwrite: bool = False,
    async_job: bool = False,
    prev_call_id: str | None = None,
    prev_verdict: str | None = None,
    prev_verdict_note: str = "",
) -> dict[str, Any]:
    """Fused repo audit: preflight -> audit_repo_docs -> Bionic sweep -> Quarantine note -> verify_claims Pass 1."""
    _ensure_live_process_cwd()
    try:
        prev_res = _maybe_apply_prev_verdict(prev_call_id, prev_verdict, prev_verdict_note)
        effort_norm, req_mode = apprentice_engine.resolve_effort_and_mode(effort, mode)
        tier, max_eta = _resolve_eta_cap(invocation_tier, effort_norm)
        api_url = apprentice_engine.validate_loopback_url(apprentice_engine.resolve_default_api_url())
        sys_prompt, sys_src = apprentice_engine.load_system_prompt()
        repo_root = Path(os.path.expanduser(repo))
        repo_sec = apprentice_engine._inspect_path_security(repo_root)
        if repo_sec:
            raise apprentice_engine.SidecarFirewallError(f"[SECURITY_FIREWALL_BLOCKED] {repo_sec}")
        repo_resolved = repo_root.resolve(strict=False)
        if not repo_resolved.is_dir():
            raise ValueError(f"Repository directory does not exist: {repo}")

        hom_root, mem_root = _resolve_homunculus_and_memory()
        gateway_path = hom_root / "scripts" / "memory_gateway.py"
        audit_docs_path = hom_root / "skills" / "doc-and-card-studio" / "scripts" / "audit_repo_docs.py"
        verify_claims_path = hom_root / "skills" / "claim-verification" / "scripts" / "verify_claims.py"
        if not gateway_path.is_file():
            raise RuntimeError(f"memory_gateway.py missing at {gateway_path}")

        quar_candidate = mem_root / "Projects" / project / "Quarantine" / f"{name}.md"
        if not overwrite and quar_candidate.exists():
            raise RuntimeError(f"Quarantine note already exists (pass overwrite=True to replace): {quar_candidate}")

        validated_files, slice_items, slice_map = apprentice_engine.parse_and_validate_context_items(
            list(context_files or []),
            repo_root=repo_resolved,
            require_exists=True,
        )

        # Fail fast (<50ms) BEFORE spawning subprocesses when Bionic is offline or unloaded
        srv, effective_mode = apprentice_engine.preflight_live_inference(api_url, apprentice_engine.DEFAULT_MODEL_ID, req_mode)

        if async_job:
            job_info = apprentice_engine.submit_async_job(
                {
                    "kind": "repo_audit",
                    "kwargs": {
                        "repo": repo,
                        "project": project,
                        "name": name,
                        "title": title,
                        "reason": reason,
                        "prompt": prompt,
                        "context_files": list(context_files or []),
                        "include_git_diff": bool(include_git_diff),
                        "effort": effort_norm,
                        "mode": req_mode,
                        "invocation_tier": tier,
                        "max_tokens": max_tokens,
                        "overwrite": bool(overwrite),
                        "async_job": False,
                    },
                }
            )
            sc_str = _scorecard_suffix()
            return {
                **job_info,
                "effort": effort_norm,
                "prev_verdict_update": prev_res,
                "scorecard": sc_str,
                "user_notice": (
                    f"[APPRENTICE NOTICE] Launched async repo audit sprint {job_info['job_id']} "
                    f"(effort={effort_norm}, mode={effective_mode}). | {sc_str}"
                ),
            }

        # 1. Parallel pre-pass: deterministic audit_repo_docs.py + source discovery
        def _run_audit_docs() -> dict[str, Any]:
            if not audit_docs_path.is_file():
                return {"ran": False}
            ad_proc = subprocess.run(
                [sys.executable, "-B", str(audit_docs_path), str(repo_resolved)],
                cwd=apprentice_engine._safe_subprocess_cwd(repo_resolved),
                capture_output=True,
                text=True,
                timeout=30,
                check=False,
            )
            return {
                "ran": True,
                "returncode": ad_proc.returncode,
                "output_tail": (ad_proc.stdout + "\n" + ad_proc.stderr).strip()[-3000:],
            }

        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pre_pool:
            fut_ad = pre_pool.submit(_run_audit_docs)
            fut_src = pre_pool.submit(_discover_repo_sources, repo_resolved) if not validated_files else None
            audit_docs_res = fut_ad.result()
            discovered_repo_sources = fut_src.result() if fut_src is not None else validated_files

        # 2. Prompt assembly with LL-WS-12 guardrails & mode-calibrated token budget
        guarded_prompt = f"{prompt.strip()}{LL_WS_12_GUARD}"
        if effort_norm == "high":
            guarded_prompt += CONCISE_HIGH_THINKING_HINT
        if audit_docs_res.get("ran") and audit_docs_res.get("output_tail"):
            guarded_prompt += f"\n\n[PRE-PASS audit_repo_docs.py TELEMETRY (exit {audit_docs_res['returncode']})]:\n{audit_docs_res['output_tail'][-1500:]}\n"

        assembled, file_meta = apprentice_engine.assemble_prompt_payload(
            user_prompt=guarded_prompt,
            context_files=validated_files,
            repo_root=repo_resolved,
            include_git_diff=bool(include_git_diff),
            sys_prompt=sys_prompt,
            context_slices=slice_items,
        )
        base_toks = apprentice_engine.resolve_effective_max_tokens(effective_mode, max_tokens)
        if max_tokens is None and effective_mode != "cpu-bg":
            effective_max_toks = max(base_toks, 2200 if tier == "explicit" else 1200)
        else:
            effective_max_toks = base_toks

        sys_bytes = len(sys_prompt.encode("utf-8"))
        prompt_bytes = sys_bytes + len(assembled.encode("utf-8"))
        loaded_ctx = srv.get("loaded_context_length")
        has_code = apprentice_engine.is_code_heavy_payload(validated_files, bool(include_git_diff))
        eta = apprentice_engine._enforce_eta_or_raise(
            mode=effective_mode,
            prompt_bytes=prompt_bytes,
            max_tokens=effective_max_toks,
            max_eta_seconds=max_eta,
            expected_turns=1,
            force_slow=False,
            cmd_name="apprentice_repo_audit",
            invocation_tier=tier,
            has_code_context=has_code,
            loaded_ctx_override=loaded_ctx,
            calibrated_output=True,
            allow_soft_eta_overrun=(effective_mode != "cpu-bg"),
            sys_prompt_bytes=sys_bytes,
            include_git_diff=bool(include_git_diff),
        )
        t_call0 = time.perf_counter()
        try:
            res = apprentice_engine.invoke_chat_completion(
                api_url=api_url,
                model_id=apprentice_engine.DEFAULT_MODEL_ID,
                mode=effective_mode,
                system_prompt=sys_prompt,
                user_content=assembled,
                max_tokens=effective_max_toks,
                timeout_s=min(max(max_eta + 120.0, 240.0), 300.0) if effective_mode == "deep" else min(max(max_eta + 60.0, 180.0), 300.0),
                preflight_checked=True,
                loaded_ctx=loaded_ctx,
                est_prompt_tokens=eta["est_prompt_tokens"],
            )
        except Exception as exc:
            err_dt = round(time.perf_counter() - t_call0, 3)
            apprentice_engine.record_usage_telemetry(
                {
                    "cmd": "apprentice_repo_audit",
                    "effort": eta["effort"],
                    "invocation_tier": tier,
                    "mode": effective_mode,
                    "est_prompt_tokens": eta["est_prompt_tokens"],
                    "predicted_eta_s": eta["predicted_eta_s"],
                    "max_eta_seconds": max_eta,
                    "tripped": False,
                    "soft_eta_exceeded": eta["soft_eta_exceeded"],
                    "http_error": True,
                    "verdict": "corrected",
                    "elapsed_s": err_dt,
                    "observed_tg_tok_s": None,
                    "finish_reason": "error",
                }
            )
            apprentice_engine.record_call_outcome(
                verdict="corrected",
                cmd="apprentice_repo_audit",
                effort=eta["effort"],
                mode=effective_mode,
                elapsed_s=err_dt,
                soft_eta_exceeded=eta["soft_eta_exceeded"],
                note=str(exc)[:180],
            )
            raise

        apprentice_engine.record_usage_telemetry(
            {
                "cmd": "apprentice_repo_audit",
                "effort": eta["effort"],
                "invocation_tier": tier,
                "mode": effective_mode,
                "est_prompt_tokens": eta["est_prompt_tokens"],
                "predicted_eta_s": eta["predicted_eta_s"],
                "max_eta_seconds": max_eta,
                "tripped": False,
                "soft_eta_exceeded": eta["soft_eta_exceeded"],
                "synthetic_fault": bool(res.get("synthetic_fault")),
                "prompt_tokens": res["prompt_tokens"],
                "completion_tokens": res["completion_tokens"],
                "elapsed_s": res["elapsed_s"],
                "kv_wait_s": res.get("kv_wait_s", 0.0),
                "observed_tg_tok_s": res["observed_tg_tok_s"],
                "finish_reason": res["finish_reason"],
            }
        )

        audit_initial_elapsed_s = float(res["elapsed_s"])
        heal_elapsed_s = 0.0
        heal_error: str | None = None
        length_healed = bool(res.get("reasoning_recovered"))
        verify_healed = False

        if res["finish_reason"] == "length" and res["content"].strip():
            t_len0 = time.perf_counter()
            head_clean, tail_ctx = _prepare_tail_continuation(res["content"])
            cont_prompt = (
                f"{assembled}\n\n"
                "Your previous audit response hit the output token limit after completing these lines:\n"
                f"{tail_ctx}\n\n"
                "Continue seamlessly starting with the NEXT item immediately after the lines above. "
                "Do NOT repeat completed items. Cite exact `#Lstart-Lend` anchors and verbatim source literals only. Zero preamble."
            )
            cont_mode = "fast" if effective_mode in ("fast", "deep") else effective_mode
            cont_max_toks = min(3072, max(1536, effective_max_toks // 2))
            cont_timeout_s = 150.0 if effective_mode == "deep" else 120.0
            try:
                res_cont = apprentice_engine.invoke_chat_completion(
                    api_url=api_url,
                    model_id=apprentice_engine.DEFAULT_MODEL_ID,
                    mode=cont_mode,
                    system_prompt=sys_prompt,
                    user_content=cont_prompt,
                    max_tokens=cont_max_toks,
                    timeout_s=cont_timeout_s,
                    preflight_checked=True,
                    loaded_ctx=loaded_ctx,
                    allow_high_floor=False,
                )
                heal_elapsed_s += round(time.perf_counter() - t_len0, 3)
                apprentice_engine.record_usage_telemetry(
                    {
                        "cmd": "apprentice_repo_audit_length_retry",
                        "effort": eta["effort"],
                        "invocation_tier": tier,
                        "mode": cont_mode,
                        "est_prompt_tokens": res_cont["prompt_tokens"],
                        "predicted_eta_s": 0.0,
                        "max_eta_seconds": cont_timeout_s,
                        "tripped": False,
                        "is_retry": True,
                        "prompt_tokens": res_cont["prompt_tokens"],
                        "completion_tokens": res_cont["completion_tokens"],
                        "elapsed_s": res_cont["elapsed_s"],
                        "kv_wait_s": res_cont.get("kv_wait_s", 0.0),
                        "observed_tg_tok_s": res_cont["observed_tg_tok_s"],
                        "finish_reason": res_cont["finish_reason"],
                    }
                )
                stitched = _stitch_tail_continuation(head_clean, res_cont["content"])
                res = {
                    **res,
                    "content": stitched,
                    "completion_tokens": int(res["completion_tokens"]) + int(res_cont["completion_tokens"]),
                    "finish_reason": res_cont["finish_reason"],
                }
                length_healed = True
            except Exception as cont_exc:
                heal_elapsed_s += round(time.perf_counter() - t_len0, 3)
                heal_error = f"audit_length_retry_failed: {cont_exc}"

        # 3. Sanitize placeholder links & collision-free verify_claims BEFORE single gateway write
        sanitized_content, links_fixed = sanitize_quarantine_placeholder_links(res["content"])
        raw_sources = validated_files if validated_files else discovered_repo_sources
        clean_sources, src_warnings = select_collision_free_sources(repo_resolved, raw_sources)
        proj_mem_dir = mem_root / "Projects" / project

        if include_git_diff:
            vrf_pass1: dict[str, Any] = {"ran": False, "skipped_reason": "git_diff_head_delta"}
        else:
            vrf_pass1 = _run_verify_claims_check(
                sanitized_content,
                clean_sources,
                verify_claims_path,
                mem_root,
                repo_resolved,
                project_dir=proj_mem_dir if proj_mem_dir.is_dir() else None,
            )

        vrf_final: dict[str, Any] = vrf_pass1
        if vrf_pass1.get("ran") and vrf_pass1.get("returncode") != 0:
            t_heal0 = time.perf_counter()
            draft_for_scrub = sanitized_content
            vrf_for_scrub = vrf_pass1
            scrub_done = False
            try:
                surg = _surgical_repair_unbacked_lines(
                    draft_text=draft_for_scrub,
                    vrf_res=vrf_for_scrub,
                    context_sources=raw_sources,
                    clean_sources=clean_sources,
                    repo_resolved=repo_resolved,
                    verify_claims_path=verify_claims_path,
                    mem_root=mem_root,
                    cwd_check=repo_resolved,
                    api_url=api_url,
                    sys_prompt=sys_prompt,
                    loaded_ctx=loaded_ctx,
                    tier=tier,
                    eta=eta,
                    cmd_name_prefix="apprentice_repo_audit",
                    project_dir=proj_mem_dir if proj_mem_dir.is_dir() else None,
                    sanitize_links=True,
                )
            except Exception:
                surg = None

            if surg is not None:
                res = {
                    **res,
                    "prompt_tokens": int(res.get("prompt_tokens", 0)) + int(surg["prompt_tokens"]),
                    "completion_tokens": int(res.get("completion_tokens", 0)) + int(surg["completion_tokens"]),
                }
                links_fixed += int(surg.get("links_fixed") or 0)
                if surg.get("verified"):
                    heal_elapsed_s = round(heal_elapsed_s + (time.perf_counter() - t_heal0), 3)
                    sanitized_content = surg["content"]
                    res = {**res, "content": sanitized_content}
                    vrf_final = surg["vrf_after"]
                    verify_healed = True
                    scrub_done = True
                elif int(surg["vrf_after"].get("unbacked", 999)) < int(vrf_for_scrub.get("unbacked", 999)):
                    draft_for_scrub = surg["content"]
                    vrf_for_scrub = surg["vrf_after"]

            if not scrub_done:
                fail_detail = _format_compact_verify_failures(vrf_for_scrub, max_chars=2800)
                scrub_prompt = (
                    f"{assembled}\n\n"
                    f"Your previous audit draft failed deterministic claim verification:\n{fail_detail}\n"
                    "CRITICAL REPAIR RULES:\n"
                    "1. DELETE any intro sentence (such as 'Based on ...') and delete any unbacked prompt summary counts or uncalculated group totals.\n"
                    "2. Rewrite accurately using ONLY exact source literals, units, counts, and `#Lstart-Lend` anchors present verbatim in the files above (any `[CALC: ...]` tag MUST have pure numeric arithmetic using literal source numbers on the left of `=`, NEVER words like `Total` or derived subtotals).\n"
                    "3. Never invent parenthetical example numbers/units like `(e.g., 0.8mm)`; prefix `Warning:` or `Caution:` / hazard qualifier if citing `[!WARNING]`/`[!CAUTION]` blocks; NEVER cite YAML frontmatter (`---`...`---`) lines, and on `.patch`/`.diff` audits cite ONLY the `.patch`'s own `#L` lines (`<=` its total lines); for `QUALIFIED_QUANTITY(...)` failures, use the exact qualified quantity from source (e.g., `~2` / `approx` / `(2)` instead of bare `Qty 2`) or drop duplicates; replace any unbacked or uncertain value with `[TBD: <specific_missing_spec>]`.\n\n"
                    f"Previous draft:\n{draft_for_scrub}\n"
                )
                try:
                    rep_out = _run_full_repair_with_guard(
                        repair_prompt=scrub_prompt,
                        draft_for_heal=draft_for_scrub,
                        vrf_for_heal=vrf_for_scrub,
                        base_res=res,
                        effective_mode=effective_mode,
                        effort_norm=effort_norm,
                        max_budget=effective_max_toks,
                        api_url=api_url,
                        sys_prompt=sys_prompt,
                        loaded_ctx=loaded_ctx,
                        clean_sources=clean_sources,
                        verify_claims_path=verify_claims_path,
                        mem_root=mem_root,
                        cwd_check=repo_resolved,
                        tier=tier,
                        eta=eta,
                        telemetry_cmd="apprentice_repo_audit_verify_retry",
                        project_dir=proj_mem_dir if proj_mem_dir.is_dir() else None,
                        sanitize_links=True,
                    )
                    heal_elapsed_s = round(heal_elapsed_s + float(rep_out["elapsed_s"]), 3)
                    res = rep_out["res"]
                    sanitized_content = rep_out["content"]
                    links_fixed += int(rep_out["links_fixed"] or 0)
                    vrf_final = rep_out["vrf_after"]
                    verify_healed = bool(rep_out["adopted"])
                except Exception as scrub_exc:
                    heal_elapsed_s = round(heal_elapsed_s + (time.perf_counter() - t_heal0), 3)
                    heal_error = f"audit_verify_scrub_failed: {scrub_exc}"

        audit_total_elapsed_s = round(audit_initial_elapsed_s + heal_elapsed_s, 3)
        if heal_elapsed_s > 0.0:
            res = {**res, "elapsed_s": audit_total_elapsed_s}
        # 4. Write final draft ONCE via memory_gateway.py
        body_text = (
            f"<!-- apprentice provenance: schema={apprentice_engine.SCHEMA_VERSION} "
            f"author=\"Apprentice Local Backend ({res['model']}, {res['mode']})\" elapsed_s={res['elapsed_s']} "
            f"prompt_tok={res['prompt_tokens']} out_tok={res['completion_tokens']} "
            f"tg_tok_s={res['observed_tg_tok_s']} -->\n\n{sanitized_content}\n"
        )
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", suffix=".md", delete=False) as tf:
            tf.write(body_text)
            tmp_body = Path(tf.name)
        os.chmod(tmp_body, 0o600)
        try:
            gw_proc = subprocess.run(
                [
                    sys.executable,
                    "-B",
                    str(gateway_path),
                    "quarantine-note",
                    "--homunculus-root",
                    str(hom_root),
                    "--memory-root",
                    str(mem_root),
                    "--project",
                    project,
                    "--name",
                    name,
                    "--title",
                    title,
                    "--reason",
                    reason,
                    "--body-file",
                    str(tmp_body),
                    "--json",
                ],
                cwd=apprentice_engine._safe_subprocess_cwd(),
                capture_output=True,
                text=True,
                timeout=30,
                check=False,
            )
            if gw_proc.returncode != 0:
                raise RuntimeError(
                    f"memory_gateway.py quarantine-note failed (exit {gw_proc.returncode}): "
                    f"{gw_proc.stderr.strip() or gw_proc.stdout.strip()}"
                )
            gw_result = json.loads(gw_proc.stdout)
        finally:
            tmp_body.unlink(missing_ok=True)

        vrf_ok = (not vrf_final.get("ran")) or (vrf_final.get("returncode") == 0)
        if res["finish_reason"] != "stop" or not vrf_ok or heal_error is not None:
            verdict = "corrected"
        elif length_healed or verify_healed:
            verdict = "healed"
        else:
            verdict = "clean"

        sc_rec = apprentice_engine.record_call_outcome(
            verdict=verdict,
            cmd="apprentice_repo_audit",
            effort=eta["effort"],
            mode=effective_mode,
            elapsed_s=audit_total_elapsed_s,
            heal_elapsed_s=heal_elapsed_s,
            soft_eta_exceeded=eta["soft_eta_exceeded"],
            note=(heal_error or "")[:180],
        )
        sc_fmt = _scorecard_suffix(sc_rec.get("call_id"))
        return {
            "ok": True,
            "schema_version": apprentice_engine.SCHEMA_VERSION,
            "call_id": sc_rec.get("call_id"),
            "verdict": verdict,
            "effort": eta["effort"],
            "invocation_tier": tier,
            "system_prompt_source": sys_src,
            "elapsed_s": audit_total_elapsed_s,
            "claims_verified": vrf_ok,
            "audit_repo_docs": audit_docs_res,
            "eta_estimate": eta,
            "context_files": file_meta,
            "completion_telemetry": {k: v for k, v in res.items() if k != "content"},
            "placeholder_links_sanitized": links_fixed,
            "source_selection_warnings": src_warnings,
            "gateway_receipt": gw_result,
            "verify_claims_pass1": vrf_pass1,
            "verify_claims": vrf_final,
            "heal_elapsed_s": heal_elapsed_s,
            "heal_error": heal_error,
            "slow_self_heal": sc_rec.get("slow_self_heal", False),
            "prev_verdict_update": prev_res,
            "scorecard": sc_fmt,
            "user_notice": (
                f"[APPRENTICE NOTICE] Quarantined repo audit '{name}' ({eta['effort']}/{effective_mode}) in {res['elapsed_s']}s "
                f"(verdict={verdict}, verify_claims rc={vrf_final.get('returncode')}). | {sc_fmt}"
            ),
        }
    except apprentice_engine.SidecarFirewallError as exc:
        return _firewall_error_response(exc, "Repo audit")
    except apprentice_engine.SidecarEtaTrippedError as exc:
        sc_str = _scorecard_suffix()
        return {
            "ok": False,
            "error_code": "ETA_CIRCUIT_BREAKER_TRIPPED",
            "error": str(exc),
            "eta_estimate": exc.estimate,
            "scorecard": sc_str,
            "user_notice": f"[APPRENTICE NOTICE] Repo audit ETA breaker handed back to frontier thread. | {sc_str}",
        }
    except Exception as exc:
        sc_str = _scorecard_suffix()
        return {
            "ok": False,
            "error_code": "AUDIT_ERROR",
            "error": str(exc),
            "scorecard": sc_str,
            "user_notice": f"[APPRENTICE NOTICE] Repo audit error: {exc} | {sc_str}",
        }


@mcp.tool()
async def apprentice_repo_audit(
    repo: str,
    project: str,
    name: str,
    title: str,
    reason: str,
    prompt: str,
    context_files: list[str] | None = None,
    include_git_diff: bool = False,
    effort: str | None = None,
    mode: str | None = None,
    invocation_tier: str = "explicit",
    max_tokens: int | None = None,
    overwrite: bool = False,
    async_job: bool = False,
    prev_call_id: str | None = None,
    prev_verdict: str | None = None,
    prev_verdict_note: str = "",
) -> dict[str, Any]:
    """Fused repo audit: preflight -> audit_repo_docs -> Bionic sweep -> Quarantine note -> verify_claims Pass 1."""
    return await _run_mcp_with_sync_guard(
        "repo audit",
        _apprentice_repo_audit_sync,
        {
            "repo": repo,
            "project": project,
            "name": name,
            "title": title,
            "reason": reason,
            "prompt": prompt,
            "context_files": context_files,
            "include_git_diff": include_git_diff,
            "effort": effort,
            "mode": mode,
            "invocation_tier": invocation_tier,
            "max_tokens": max_tokens,
            "overwrite": overwrite,
            "async_job": async_job,
            "prev_call_id": prev_call_id,
            "prev_verdict": prev_verdict,
            "prev_verdict_note": prev_verdict_note,
        },
    )


_mcp_apprentice_repo_audit_coro = apprentice_repo_audit
apprentice_repo_audit = _apprentice_repo_audit_sync  # type: ignore[assignment]


def _check_unclosed_code_fence(raw_text: str) -> str | None:
    """Detect odd/unclosed Markdown code fences indicating truncated or malformed staged output."""
    fences = re.findall(r"(?m)^[ \t]*```", raw_text)
    if len(fences) % 2 == 1:
        return "Truncated/unclosed Markdown code fence detected in generated output."
    return None


def _resolve_effective_smoke_args(
    staged_file: Path,
    explicit_smoke_args: list[str] | None,
) -> tuple[list[str] | None, bool]:
    """Auto-detect `--self-test` in staged Python AST when caller did not specify `smoke_test_args`."""
    if explicit_smoke_args is not None:
        return explicit_smoke_args, False
    if staged_file.suffix.lower() != ".py" or not staged_file.is_file():
        return None, False
    try:
        tree = ast.parse(staged_file.read_text(encoding="utf-8", errors="replace"))
    except (OSError, SyntaxError):
        return None, False

    has_main = False
    has_selftest = False
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and node.value == "--self-test":
            has_selftest = True
        elif isinstance(node, ast.If) and isinstance(node.test, ast.Compare):
            cmp = node.test
            if len(cmp.ops) == 1 and isinstance(cmp.ops[0], ast.Eq) and len(cmp.comparators) == 1:
                pair = (cmp.left, cmp.comparators[0])
                is_name_main = any(isinstance(p, ast.Name) and p.id == "__name__" for p in pair) and any(
                    isinstance(p, ast.Constant) and p.value == "__main__" for p in pair
                )
                if is_name_main:
                    has_main = True
        if has_main and has_selftest:
            return ["--self-test"], True
    return None, False


def _run_smoke_test(
    staged_file: Path,
    safe_staging: Path,
    smoke_args: list[str] | None,
) -> dict[str, Any]:
    """Run an optional argv-only smoke check on a staged Python artifact inside scratch/."""
    if smoke_args is None:
        return {"ran": False, "ok": True}
    clean_args = [str(a) for a in smoke_args]
    if any("\x00" in a for a in clean_args):
        raise apprentice_engine.SidecarFirewallError("[SECURITY_FIREWALL_BLOCKED] Invalid null byte in smoke_test_args.")
    try:
        proc = subprocess.run(
            [sys.executable, "-B", str(staged_file), *clean_args],
            cwd=apprentice_engine._safe_subprocess_cwd(safe_staging),
            capture_output=True,
            text=True,
            timeout=15,
            check=False,
        )
        return {
            "ran": True,
            "ok": proc.returncode == 0,
            "returncode": proc.returncode,
            "output_tail": ((proc.stdout or "") + "\n" + (proc.stderr or "")).strip()[-1500:],
        }
    except subprocess.TimeoutExpired as exc:
        return {"ran": True, "ok": False, "returncode": None, "output_tail": f"smoke test timed out after 15s: {exc}"}


def _detect_sleep_selftest_antipattern(staged_file: Path) -> str | None:
    """Detect blocking wall-clock time.sleep(>=0.1) or elapsed timing assertions in a failed staged Python file."""
    if staged_file.suffix.lower() != ".py" or not staged_file.is_file():
        return None
    try:
        src = staged_file.read_text(encoding="utf-8", errors="replace")
        tree = ast.parse(src)
    except (OSError, SyntaxError):
        return None
    has_blocking_sleep = False
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and node.args:
            fn = node.func
            is_sleep = (isinstance(fn, ast.Attribute) and fn.attr == "sleep") or (
                isinstance(fn, ast.Name) and fn.id == "sleep"
            )
            arg0 = node.args[0]
            if is_sleep and isinstance(arg0, ast.Constant) and isinstance(arg0.value, (int, float)) and float(arg0.value) >= 0.1:
                has_blocking_sleep = True
                break
    has_elapsed_assert = bool(re.search(r"assert[^\n]*\belapsed\s*>=?", src))
    if has_blocking_sleep or has_elapsed_assert:
        return (
            "[SMOKE_SLEEP_ANTIPATTERN] Replace blocking `time.sleep(>=0.1)` / `elapsed >=` checks with fast "
            "deterministic synchronous probes or an optional injectable `clock=time.monotonic` callable."
        )
    return None


def _build_stage_repair_context(
    validated_files: list[Path],
    slice_items: list[tuple[int, int] | None],
    *,
    repo_resolved: Path | None,
    sys_prompt: str,
    max_ctx_bytes: int = 20000,
) -> str:
    """Assemble bounded line-numbered context blocks (<=20 KB, prioritizing explicit #L slices) for Pass-2 repair."""
    if not validated_files:
        return ""
    pairs = list(zip(validated_files, slice_items))
    ordered = sorted(pairs, key=lambda pair: 0 if pair[1] is not None else 1)
    kept_files: list[Path] = []
    kept_slices: list[tuple[int, int] | None] = []
    used_bytes = 0
    omitted = 0
    line_cache: dict[Path, list[str]] = {}
    for fp, sl in ordered:
        try:
            if sl is not None:
                lines = line_cache.setdefault(fp, fp.read_text(encoding="utf-8", errors="replace").splitlines())
                s_l, e_l = sl
                blk_b = len("\n".join(lines[max(0, s_l - 1) : max(0, e_l)]).encode("utf-8")) + 128
            else:
                blk_b = fp.stat().st_size + 128
        except OSError:
            omitted += 1
            continue
        if blk_b > max_ctx_bytes or (kept_files and used_bytes + blk_b > max_ctx_bytes):
            omitted += 1
            continue
        kept_files.append(fp)
        kept_slices.append(sl)
        used_bytes += blk_b
    if not kept_files:
        return (
            f"\n\n[Note: {omitted} oversized reference context file(s) omitted from Pass-2 repair.]"
            if omitted
            else ""
        )
    ctx_assembled, _ = apprentice_engine.assemble_prompt_payload(
        user_prompt="",
        context_files=kept_files,
        repo_root=repo_resolved,
        include_git_diff=False,
        sys_prompt=sys_prompt,
        context_slices=kept_slices,
    )
    ctx_body = ctx_assembled.strip()
    if omitted:
        ctx_body += f"\n[Note: {omitted} additional oversized reference file(s) omitted from Pass-2 repair.]"
    return f"\n\n### AUTHORITATIVE CONTEXT:\n{ctx_body}" if ctx_body else ""


def _apprentice_stage_patch_sync(
    target_filename: str,
    prompt: str,
    context_files: list[str] | None = None,
    repo: str = "",
    compare_against: str = "",
    staging_dir: str = str(apprentice_engine.DEFAULT_STAGING_DIR),
    effort: str | None = None,
    mode: str | None = None,
    invocation_tier: str = "auto",
    max_tokens: int | None = None,
    smoke_test_args: list[str] | None = None,
    async_job: bool = False,
    prev_call_id: str | None = None,
    prev_verdict: str | None = None,
    prev_verdict_note: str = "",
) -> dict[str, Any]:
    """Stage isolated scratch code/patch + py_compile + optional smoke check with dedicated self-heal retry."""
    _ensure_live_process_cwd()
    try:
        prev_res = _maybe_apply_prev_verdict(prev_call_id, prev_verdict, prev_verdict_note)
        effort_norm, req_mode = apprentice_engine.resolve_effort_and_mode(effort, mode)
        tier, max_eta = _resolve_eta_cap(invocation_tier, effort_norm)
        safe_staging = apprentice_engine.validate_staging_dir(Path(staging_dir))
        api_url = apprentice_engine.validate_loopback_url(apprentice_engine.resolve_default_api_url())
        sys_prompt, _ = apprentice_engine.load_system_prompt()
        repo_root = Path(repo) if repo.strip() else None
        repo_resolved = repo_root.resolve(strict=False) if repo_root else None
        validated_files, slice_items, slice_map = apprentice_engine.parse_and_validate_context_items(
            list(context_files or []),
            repo_root=repo_root,
            require_exists=True,
        )
        compare_path = Path(compare_against) if compare_against.strip() else None
        if compare_path is not None:
            apprentice_engine.validate_input_paths([compare_path], repo_root=repo_root, require_exists=True)
        if not prompt.strip():
            raise ValueError("Prompt must be non-empty.")

        srv, effective_mode = apprentice_engine.preflight_live_inference(api_url, apprentice_engine.DEFAULT_MODEL_ID, req_mode)

        if async_job:
            job_info = apprentice_engine.submit_async_job(
                {
                    "kind": "stage_patch",
                    "kwargs": {
                        "target_filename": target_filename,
                        "prompt": prompt,
                        "context_files": list(context_files or []),
                        "repo": repo,
                        "compare_against": compare_against,
                        "staging_dir": staging_dir,
                        "effort": effort_norm,
                        "mode": req_mode,
                        "invocation_tier": tier,
                        "max_tokens": max_tokens,
                        "smoke_test_args": list(smoke_test_args) if smoke_test_args is not None else None,
                        "async_job": False,
                    },
                }
            )
            sc_str = _scorecard_suffix()
            return {
                **job_info,
                "effort": effort_norm,
                "prev_verdict_update": prev_res,
                "scorecard": sc_str,
                "user_notice": (
                    f"[APPRENTICE NOTICE] Launched async stage-patch sprint {job_info['job_id']} "
                    f"for {target_filename} ({effort_norm}/{effective_mode}). | {sc_str}"
                ),
            }

        is_py_target = target_filename.lower().endswith(".py")
        stage_user_prompt = prompt.strip()
        if is_py_target:
            stage_user_prompt += _STAGE_PY_DISCIPLINE_HINT
        if effort_norm == "high":
            stage_user_prompt += CONCISE_HIGH_THINKING_HINT
        assembled, _ = apprentice_engine.assemble_prompt_payload(
            user_prompt=stage_user_prompt,
            context_files=validated_files,
            repo_root=repo_resolved,
            include_git_diff=False,
            sys_prompt=sys_prompt,
            context_slices=slice_items,
        )
        loaded_ctx = srv.get("loaded_context_length")
        max_toks = apprentice_engine.resolve_effective_max_tokens(effective_mode, max_tokens)
        sys_bytes = len(sys_prompt.encode("utf-8"))
        prompt_bytes = sys_bytes + len(assembled.encode("utf-8"))
        eta1 = apprentice_engine._enforce_eta_or_raise(
            mode=effective_mode,
            prompt_bytes=prompt_bytes,
            max_tokens=max_toks,
            max_eta_seconds=max_eta,
            expected_turns=1,
            force_slow=False,
            cmd_name="apprentice_stage_patch",
            invocation_tier=tier,
            has_code_context=True,
            loaded_ctx_override=loaded_ctx,
            calibrated_output=True,
            allow_soft_eta_overrun=(effective_mode != "cpu-bg"),
            sys_prompt_bytes=sys_bytes,
        )
        t_call0 = time.perf_counter()
        try:
            res1 = apprentice_engine.invoke_chat_completion(
                api_url=api_url,
                model_id=apprentice_engine.DEFAULT_MODEL_ID,
                mode=effective_mode,
                system_prompt=sys_prompt,
                user_content=assembled,
                max_tokens=max_toks,
                timeout_s=min(max(max_eta + 120.0, 240.0), 300.0) if effective_mode == "deep" else min(max(max_eta + 60.0, 150.0), 300.0),
                preflight_checked=True,
                loaded_ctx=loaded_ctx,
                est_prompt_tokens=eta1["est_prompt_tokens"],
            )
        except Exception as exc:
            err_dt = round(time.perf_counter() - t_call0, 3)
            apprentice_engine.record_usage_telemetry(
                {
                    "cmd": "apprentice_stage_patch",
                    "effort": eta1["effort"],
                    "invocation_tier": tier,
                    "mode": effective_mode,
                    "est_prompt_tokens": eta1["est_prompt_tokens"],
                    "predicted_eta_s": eta1["predicted_eta_s"],
                    "max_eta_seconds": max_eta,
                    "tripped": False,
                    "soft_eta_exceeded": eta1["soft_eta_exceeded"],
                    "http_error": True,
                    "verdict": "corrected",
                    "elapsed_s": err_dt,
                    "observed_tg_tok_s": None,
                    "finish_reason": "error",
                }
            )
            apprentice_engine.record_call_outcome(
                verdict="corrected",
                cmd="apprentice_stage_patch",
                effort=eta1["effort"],
                mode=effective_mode,
                elapsed_s=err_dt,
                soft_eta_exceeded=eta1["soft_eta_exceeded"],
                note=str(exc)[:180],
            )
            raise

        apprentice_engine.record_usage_telemetry(
            {
                "cmd": "apprentice_stage_patch",
                "effort": eta1["effort"],
                "invocation_tier": tier,
                "mode": effective_mode,
                "est_prompt_tokens": eta1["est_prompt_tokens"],
                "predicted_eta_s": eta1["predicted_eta_s"],
                "max_eta_seconds": max_eta,
                "tripped": False,
                "soft_eta_exceeded": eta1["soft_eta_exceeded"],
                "synthetic_fault": bool(res1.get("synthetic_fault")),
                "prompt_tokens": res1["prompt_tokens"],
                "completion_tokens": res1["completion_tokens"],
                "elapsed_s": res1["elapsed_s"],
                "kv_wait_s": res1.get("kv_wait_s", 0.0),
                "observed_tg_tok_s": res1["observed_tg_tok_s"],
                "finish_reason": res1["finish_reason"],
            }
        )
        fence_err1 = _check_unclosed_code_fence(res1["content"]) or (
            "Response truncated with finish_reason=length." if res1["finish_reason"] != "stop" else None
        )
        receipt = apprentice_engine.stage_code_artifact(
            staging_dir=safe_staging,
            target_filename=target_filename,
            generated_text=res1["content"],
            compare_against=compare_path,
            telemetry={"eta": eta1, **{k: v for k, v in res1.items() if k != "content"}},
        )
        if receipt["py_compile_ok"] is not False and not fence_err1:
            eff_smoke_args1, auto_smoke1 = _resolve_effective_smoke_args(Path(receipt["staged_file"]), smoke_test_args)
            smoke_res = _run_smoke_test(Path(receipt["staged_file"]), safe_staging, eff_smoke_args1)
            if auto_smoke1:
                smoke_res["auto_detected"] = True
        else:
            smoke_res = {"ran": False, "ok": True}

        attempts = 2 if res1.get("reasoning_recovered") else 1
        repair_retried = bool(res1.get("reasoning_recovered"))
        heal_elapsed_s = 0.0
        handed_back_reason: str | None = None
        fence_err2: str | None = None
        res2: dict[str, Any] | None = None
        needs_heal = (receipt["py_compile_ok"] is False) or bool(fence_err1) or (smoke_res.get("ran") and not smoke_res.get("ok"))

        if needs_heal:
            repair_mode = "fast" if effective_mode in ("fast", "deep") else effective_mode
            repair_budget = max(90.0, float(max_eta)) if effective_mode == "deep" else max(60.0, float(max_eta))
            if receipt["py_compile_ok"] is False:
                diag_err = receipt.get("py_compile_error")
            elif fence_err1:
                diag_err = fence_err1
            else:
                diag_err = f"Smoke test failed (exit {smoke_res.get('returncode')}):\n{smoke_res.get('output_tail')}"
                sleep_warn = _detect_sleep_selftest_antipattern(Path(receipt["staged_file"]))
                if sleep_warn:
                    diag_err = f"{diag_err}\n{sleep_warn}"
            faulty_code = apprentice_engine.extract_staged_code(res1["content"])
            repair_ctx_block = _build_stage_repair_context(
                validated_files,
                slice_items,
                repo_resolved=repo_resolved,
                sys_prompt=sys_prompt,
            )
            fence_lang = "python" if is_py_target else ""
            repair_prompt = (
                f"{prompt.strip()}{repair_ctx_block}\n\nPrevious draft failed local validation with:\n{diag_err}\n"
                "Fix the issue cleanly (reconciling implementation and any `--self-test` assertions with the "
                "prompt contract and authoritative context above; prefer deterministic synchronous assertions "
                "or an optional injectable `clock=time.monotonic` callable over private-attribute mutations or "
                "blocking `time.sleep(>=0.1)` races) and return ONLY the complete corrected file in one code fence.\n\n"
                f"Faulty draft:\n```{fence_lang}\n{faulty_code}\n```\n"
            )
            if repair_mode == "deep":
                repair_prompt += CONCISE_HIGH_THINKING_HINT
            repair_prompt += (
                "\n[SURGICAL CODE FIX: Inspect only the failing error/traceback and context contract above, "
                "and emit the complete corrected file immediately.]"
            )
            repair_bytes = sys_bytes + len(repair_prompt.encode("utf-8"))
            repair_eta = apprentice_engine.estimate_eta(
                mode=repair_mode,
                prompt_bytes=repair_bytes,
                max_tokens=max_toks,
                max_eta_seconds=repair_budget,
                expected_turns=1,
                has_code_context=True,
                loaded_ctx_override=loaded_ctx,
                calibrated_output=True,
                cmd_name="apprentice_stage_patch_retry",
                sys_prompt_bytes=sys_bytes,
                target_code_bytes=max(1, len(faulty_code.encode("utf-8"))),
            )
            repair_slack_s = 45.0 if effective_mode == "deep" else 30.0
            repair_timeout_s = 135.0 if repair_mode != "cpu-bg" else 90.0
            if not repair_eta["hard_tripped"] and repair_eta["predicted_eta_s"] <= repair_budget + repair_slack_s:
                attempts = 2
                t_heal0 = time.perf_counter()
                try:
                    res2 = apprentice_engine.invoke_chat_completion(
                        api_url=api_url,
                        model_id=apprentice_engine.DEFAULT_MODEL_ID,
                        mode=repair_mode,
                        system_prompt=sys_prompt,
                        user_content=repair_prompt,
                        max_tokens=max_toks,
                        timeout_s=repair_timeout_s,
                        preflight_checked=True,
                        loaded_ctx=loaded_ctx,
                        est_prompt_tokens=repair_eta["est_prompt_tokens"],
                        allow_high_floor=False,
                    )
                    repair_retried = True
                    heal_elapsed_s = round(time.perf_counter() - t_heal0, 3)
                    apprentice_engine.record_usage_telemetry(
                        {
                            "cmd": "apprentice_stage_patch_retry",
                            "effort": repair_eta["effort"],
                            "invocation_tier": tier,
                            "mode": repair_mode,
                            "est_prompt_tokens": repair_eta["est_prompt_tokens"],
                            "predicted_eta_s": repair_eta["predicted_eta_s"],
                            "max_eta_seconds": repair_budget,
                            "tripped": False,
                            "is_retry": True,
                            "soft_eta_exceeded": repair_eta["soft_eta_exceeded"],
                            "prompt_tokens": res2["prompt_tokens"],
                            "completion_tokens": res2["completion_tokens"],
                            "elapsed_s": res2["elapsed_s"],
                            "kv_wait_s": res2.get("kv_wait_s", 0.0),
                            "observed_tg_tok_s": res2["observed_tg_tok_s"],
                            "finish_reason": res2["finish_reason"],
                        }
                    )
                    fence_err2 = _check_unclosed_code_fence(res2["content"]) or (
                        "Response truncated with finish_reason=length." if res2["finish_reason"] != "stop" else None
                    )
                    consolidated_dt = round(float(res1["elapsed_s"]) + heal_elapsed_s, 3)
                    consolidated_telemetry = {
                        "eta": repair_eta,
                        **{k: v for k, v in res2.items() if k != "content"},
                        "elapsed_s": consolidated_dt,
                        "initial_elapsed_s": float(res1["elapsed_s"]),
                        "prompt_tokens": int(res1.get("prompt_tokens") or 0) + int(res2.get("prompt_tokens") or 0),
                        "completion_tokens": int(res1.get("completion_tokens") or 0) + int(res2.get("completion_tokens") or 0),
                    }
                    receipt = apprentice_engine.stage_code_artifact(
                        staging_dir=safe_staging,
                        target_filename=target_filename,
                        generated_text=res2["content"],
                        compare_against=compare_path,
                        telemetry=consolidated_telemetry,
                    )
                    if receipt["py_compile_ok"] is not False and not fence_err2:
                        eff_smoke_args2, auto_smoke2 = _resolve_effective_smoke_args(Path(receipt["staged_file"]), smoke_test_args)
                        smoke_res = _run_smoke_test(Path(receipt["staged_file"]), safe_staging, eff_smoke_args2)
                        if auto_smoke2:
                            smoke_res["auto_detected"] = True
                    else:
                        smoke_res = {"ran": False, "ok": False}
                except Exception as heal_exc:
                    heal_elapsed_s = round(time.perf_counter() - t_heal0, 3)
                    handed_back_reason = f"Repair retry failed (kept Pass 1 draft): {heal_exc}"
            else:
                handed_back_reason = (
                    f"Initial validation failed and repair ETA ({repair_eta['predicted_eta_s']:.1f}s) "
                    f"exceeded dedicated repair cap ({repair_budget:.1f}s)."
                )

        active_fence_err = fence_err2 if (repair_retried and res2 is not None) else fence_err1
        active_finish = res2["finish_reason"] if (repair_retried and res2 is not None) else res1["finish_reason"]
        final_ok = (
            (receipt["py_compile_ok"] is not False)
            and (not active_fence_err)
            and (active_finish == "stop")
            and (not smoke_res.get("ran") or bool(smoke_res.get("ok")))
        )
        if not final_ok:
            verdict = "corrected"
        elif repair_retried:
            verdict = "healed"
        else:
            verdict = "clean"

        total_dt = round(float(res1["elapsed_s"]) + heal_elapsed_s, 3)
        sc_rec = apprentice_engine.record_call_outcome(
            verdict=verdict,
            cmd="apprentice_stage_patch",
            effort=eta1["effort"],
            mode=effective_mode,
            elapsed_s=total_dt,
            heal_elapsed_s=heal_elapsed_s,
            soft_eta_exceeded=eta1["soft_eta_exceeded"],
            note=handed_back_reason or "",
        )
        sc_fmt = _scorecard_suffix(sc_rec.get("call_id"))
        return {
            "ok": final_ok,
            "call_id": sc_rec.get("call_id"),
            "verdict": verdict,
            "effort": eta1["effort"],
            "invocation_tier": tier,
            "attempts": attempts,
            "repair_retried": repair_retried,
            "elapsed_s": total_dt,
            "heal_elapsed_s": heal_elapsed_s,
            "slow_self_heal": sc_rec.get("slow_self_heal", False),
            "handed_back_reason": handed_back_reason,
            "smoke_test": smoke_res,
            "prev_verdict_update": prev_res,
            **receipt,
            "completion_telemetry": receipt.get("telemetry"),
            "scorecard": sc_fmt,
            "user_notice": (
                f"[APPRENTICE NOTICE] Staged {target_filename} in scratch "
                f"(attempts={attempts}, verdict={verdict}, py_compile_ok={receipt['py_compile_ok']}). | {sc_fmt}"
            ),
        }
    except apprentice_engine.SidecarFirewallError as exc:
        return _firewall_error_response(exc, "Patch staging")
    except apprentice_engine.SidecarEtaTrippedError as exc:
        sc_str = _scorecard_suffix()
        return {
            "ok": False,
            "error_code": "ETA_CIRCUIT_BREAKER_TRIPPED",
            "error": str(exc),
            "eta_estimate": exc.estimate,
            "scorecard": sc_str,
            "user_notice": f"[APPRENTICE NOTICE] Patch staging ETA breaker handed back to frontier thread. | {sc_str}",
        }
    except Exception as exc:
        sc_str = _scorecard_suffix()
        return {
            "ok": False,
            "error_code": "STAGE_ERROR",
            "error": str(exc),
            "scorecard": sc_str,
            "user_notice": f"[APPRENTICE NOTICE] Patch staging error: {exc} | {sc_str}",
        }


@mcp.tool()
async def apprentice_stage_patch(
    target_filename: str,
    prompt: str,
    context_files: list[str] | None = None,
    repo: str = "",
    compare_against: str = "",
    staging_dir: str = str(apprentice_engine.DEFAULT_STAGING_DIR),
    effort: str | None = None,
    mode: str | None = None,
    invocation_tier: str = "auto",
    max_tokens: int | None = None,
    smoke_test_args: list[str] | None = None,
    async_job: bool = False,
    prev_call_id: str | None = None,
    prev_verdict: str | None = None,
    prev_verdict_note: str = "",
) -> dict[str, Any]:
    """Stage isolated scratch code/patch + py_compile + optional smoke check with dedicated 45s self-heal retry."""
    return await _run_mcp_with_sync_guard(
        "stage-patch",
        _apprentice_stage_patch_sync,
        {
            "target_filename": target_filename,
            "prompt": prompt,
            "context_files": context_files,
            "repo": repo,
            "compare_against": compare_against,
            "staging_dir": staging_dir,
            "effort": effort,
            "mode": mode,
            "invocation_tier": invocation_tier,
            "max_tokens": max_tokens,
            "smoke_test_args": smoke_test_args,
            "async_job": async_job,
            "prev_call_id": prev_call_id,
            "prev_verdict": prev_verdict,
            "prev_verdict_note": prev_verdict_note,
        },
    )


_mcp_apprentice_stage_patch_coro = apprentice_stage_patch
apprentice_stage_patch = _apprentice_stage_patch_sync  # type: ignore[assignment]


def run_self_tests() -> dict[str, Any]:
    """Deterministic offline verification of helpers, gates, ETA tiers, and tool registration."""
    checks: list[str] = []

    # 1. Collision-free source filtering + CROSS_ENTITY guard
    with tempfile.TemporaryDirectory() as td:
        td_p = Path(td)
        repo = td_p / "MyRepo"
        nested = repo / "Releases" / "1.2" / "STLs"
        foreign = td_p / "ForeignRepo"
        nested.mkdir(parents=True)
        foreign.mkdir(parents=True)
        (repo / "README.md").write_text("# Root\n", encoding="utf-8")
        (nested / "README.md").write_text("# Nested\n", encoding="utf-8")
        (repo / "BOM.md").write_text("# BOM\n", encoding="utf-8")
        (foreign / "OTHER.md").write_text("# Other\n", encoding="utf-8")

        selected, warns = select_collision_free_sources(
            repo,
            [nested / "README.md", repo / "README.md", repo / "BOM.md", foreign / "OTHER.md"],
        )
        assert [p.relative_to(repo).as_posix() for p in selected] == ["BOM.md", "README.md"]
        assert len(warns) == 2
    checks.append("collision_free_sources_and_cross_entity_guard")

    # 2. Placeholder link sanitizer preserves real links and strips broken placeholders
    sample_md = "See [Guide](README.md#L10-L20) and [Checklist](...) or [Draft](path/to/doc.md)."
    cleaned, n_fixed = sanitize_quarantine_placeholder_links(sample_md)
    assert n_fixed == 2
    assert "[Guide](README.md#L10-L20)" in cleaned
    assert "`Checklist`" in cleaned and "`Draft`" in cleaned and "(...)" not in cleaned
    checks.append("placeholder_link_sanitizer")

    # 3. Confirmation gate & profile validation in apprentice_control
    blocked = apprentice_control(action="start_headless", profile="gpu-daily", user_confirmed=False)
    assert blocked["ok"] is False and blocked["error_code"] == "USER_CONFIRMATION_REQUIRED"
    checks.append("apprentice_control_confirmation_gate")

    # 4. 60s auto vs 90s explicit ETA & firewall integration
    assert _resolve_eta_cap("auto") == ("auto", 60.0)
    assert _resolve_eta_cap("explicit") == ("explicit", 90.0)
    fw_digest = apprentice_digest(prompt="check", context_files=["/home/orin/.gemini/config/mcp_config.json"])
    assert fw_digest["ok"] is False and fw_digest["error_code"] == "SECURITY_FIREWALL_BLOCKED"
    checks.append("eta_tier_and_mcp_firewall_enforcement")

    # 5. Tool discovery check (full MCPServer verification when running in venv)
    tools = _registered_tool_names()
    expected = {"apprentice_control", "apprentice_digest", "apprentice_repo_audit", "apprentice_stage_patch"}
    assert expected.issubset(set(tools)), f"Missing MCP tools: {expected - set(tools)}"
    checks.append("mcp_tool_registration" if _HAS_MCP else "stdlib_fallback_tool_registration")

    # 6 & 7. Mock HTTP server testing unloaded anti-JIT block, cpu-bg auto-clamp, & syntax-repair retry
    import http.server
    import threading

    state_box: dict[str, Any] = {
        "loaded": False,
        "ctx": None,
        "posts": 0,
        "replies": [],
    }

    class _MockMcpBionicHandler(http.server.BaseHTTPRequestHandler):
        def do_GET(self) -> None:  # noqa: N802
            if self.path == "/api/v0/models":
                row = {
                    "id": apprentice_engine.DEFAULT_MODEL_ID,
                    "state": "loaded" if state_box["loaded"] else "not-loaded",
                    "loaded_context_length": state_box["ctx"] if state_box["loaded"] else None,
                }
                body = json.dumps({"data": [row]}).encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
            else:
                self.send_response(404)
                self.end_headers()

        def do_POST(self) -> None:  # noqa: N802
            if self.path == "/v1/chat/completions":
                length = int(self.headers.get("Content-Length") or 0)
                req_body = self.rfile.read(length).decode("utf-8", errors="replace") if length else ""
                state_box["posts"] += 1
                raw_reply = state_box["replies"].pop(0) if state_box["replies"] else "OK"
                if callable(raw_reply):
                    raw_reply = raw_reply(req_body)
                if isinstance(raw_reply, tuple):
                    reply_txt, finish_reason = str(raw_reply[0]), str(raw_reply[1])
                else:
                    reply_txt, finish_reason = str(raw_reply), "stop"
                body = json.dumps(
                    {
                        "id": "mock-cmp",
                        "model": apprentice_engine.DEFAULT_MODEL_ID,
                        "choices": [{"index": 0, "message": {"role": "assistant", "content": reply_txt}, "finish_reason": finish_reason}],
                        "usage": {"prompt_tokens": 60, "completion_tokens": 18},
                        "stats": {"tokens_per_second": 42.0},
                    }
                ).encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
            else:
                self.send_response(404)
                self.end_headers()

        def log_message(self, _fmt: str, *_args: Any) -> None:
            return

    srv = http.server.HTTPServer(("127.0.0.1", 0), _MockMcpBionicHandler)
    th = threading.Thread(target=srv.serve_forever, daemon=True)
    th.start()
    with tempfile.TemporaryDirectory() as td:
        td_p = Path(td)
        old_api = os.environ.get("APPRENTICE_API_URL")
        old_tel = os.environ.get("APPRENTICE_TELEMETRY_LOG")
        old_custom_port = os.environ.get("BIONIC_ALLOW_CUSTOM_LOOPBACK_PORT")
        telemetry_path = td_p / "telemetry.jsonl"
        os.environ["APPRENTICE_API_URL"] = f"http://127.0.0.1:{srv.server_port}/v1"
        os.environ["APPRENTICE_TELEMETRY_LOG"] = str(telemetry_path)
        os.environ["BIONIC_ALLOW_CUSTOM_LOOPBACK_PORT"] = "1"
        try:
            # 6a. UNLOADED blocks apprentice_digest before any POST (anti-JIT)
            unloaded_res = apprentice_digest(prompt="hello", mode="fast", invocation_tier="auto")
            assert unloaded_res["ok"] is False
            assert unloaded_res["error_code"] == "BIONIC_UNLOADED_CONFIRMATION_REQUIRED"
            assert state_box["posts"] == 0

            # 6b. Loaded @ 16384 ctx auto-clamps mode='fast' -> 'cpu-bg' and catches 9.5k prompt guard
            state_box["loaded"] = True
            state_box["ctx"] = 16384
            big_ctx = td_p / "big_ctx.txt"
            big_ctx.write_text(("alpha beta gamma delta epsilon\n" * 1150), encoding="utf-8")
            clamp_res = apprentice_digest(
                prompt="summarize",
                context_files=[str(big_ctx)],
                repo=str(td_p),
                mode="fast",
                invocation_tier="auto",
            )
            assert clamp_res["ok"] is False
            assert clamp_res["error_code"] == "ETA_CIRCUIT_BREAKER_TRIPPED"
            assert state_box["posts"] == 0
            checks.append("mcp_unloaded_anti_jit_and_cpu_bg_autoclamp")

            # 7. Stage patch syntax-repair retry writes telemetry for both attempts
            state_box["ctx"] = 49152
            state_box["replies"] = [
                "```python\ndef broken(:\n    pass\n```\n",
                "```python\ndef ok() -> int:\n    return 42\n```\n",
            ]
            orig_f = td_p / "mod.py"
            orig_f.write_text("def ok() -> int:\n    return 0\n", encoding="utf-8")
            stage_dir = td_p / "stage"
            stage_res = apprentice_stage_patch(
                target_filename="mod.py",
                prompt="update function",
                compare_against=str(orig_f),
                staging_dir=str(stage_dir),
                mode="fast",
                invocation_tier="auto",
            )
            assert stage_res["ok"] is True
            assert stage_res["attempts"] == 2
            assert stage_res["repair_retried"] is True
            assert stage_res["py_compile_ok"] is True
            assert state_box["posts"] == 2
            tel_rows = [json.loads(line) for line in telemetry_path.read_text(encoding="utf-8").splitlines() if line.strip()]
            assert len(tel_rows) == 3
            assert [r["cmd"] for r in tel_rows] == ["apprentice_digest", "apprentice_stage_patch", "apprentice_stage_patch_retry"]
            assert tel_rows[0]["tripped"] is True and tel_rows[0]["mode"] == "cpu-bg"
            assert (telemetry_path.stat().st_mode & 0o777) == 0o600
            assert stage_res["verdict"] == "healed"
            assert isinstance(stage_res.get("completion_telemetry"), dict) and "prompt_tokens" in stage_res["completion_telemetry"]
            assert "Apprentice Calls =" in stage_res["user_notice"]
            checks.append("stage_patch_syntax_retry_and_telemetry")

            # 10. Async MCP tool wrapper verification (coroutine registered on MCPServer, sync callable exposed)
            if _HAS_MCP:
                import inspect
                tool_mgr = getattr(mcp, "_tool_manager", None)
                assert tool_mgr is not None
                for tname in ("apprentice_control", "apprentice_digest", "apprentice_repo_audit", "apprentice_stage_patch"):
                    tobj = tool_mgr._tools[tname]
                    assert inspect.iscoroutinefunction(tobj.fn), f"{tname} MCP tool must be async coroutine"
            checks.append("mcp_async_wrappers_and_sync_python_compat")

            # 11. HIGH effort (>=4096 floor) + #Lstart-Lend slice + apprentice_control verdict downgrade
            slice_file = td_p / "slice_src.py"
            slice_file.write_text("\n".join(f"line_{i} = {i}" for i in range(1, 21)) + "\n", encoding="utf-8")
            state_box["replies"] = ["Slice reviewed cleanly."]
            high_res = apprentice_digest(
                prompt="Review lines",
                context_files=[f"{slice_file}#L5-L10"],
                repo=str(td_p),
                effort="high",
                invocation_tier="explicit",
            )
            assert high_res["ok"] is True
            assert high_res["effort"] == "high"
            assert high_res["eta_estimate"]["effective_max_tokens"] >= 4096
            assert high_res["call_id"]
            assert "Apprentice Calls =" in high_res["user_notice"]

            vd = apprentice_control(action="verdict", call_id=high_res["call_id"], verdict="corrected", note="test_downgrade")
            assert vd["ok"] is True and vd["verdict"] == "corrected"
            jlist = apprentice_control(action="job-list")
            assert jlist["ok"] is True
            checks.append("high_effort_slice_and_verdict_downgrade")

            # 12. Stage patch smoke_test_args self-heal
            state_box["replies"] = [
                "```python\nimport sys\nsys.exit(1)\n```\n",
                "```python\nimport sys\nif '--check' in sys.argv:\n    print('OK')\n```\n",
            ]
            smoke_res = apprentice_stage_patch(
                target_filename="smoke_mod.py",
                prompt="script supporting --check",
                staging_dir=str(stage_dir),
                smoke_test_args=["--check"],
            )
            assert smoke_res["ok"] is True
            assert smoke_res["verdict"] == "healed"
            assert smoke_res["smoke_test"]["ok"] is True
            checks.append("stage_patch_smoke_test_self_heal")

            # 13. Async sprint job submit + job-collect round-trip
            state_box["replies"] = ["Async sprint digest complete."]
            sub_res = apprentice_digest(
                prompt="async summarize",
                effort="standard",
                async_job=True,
            )
            assert sub_res["ok"] is True and sub_res["async_job"] is True
            jid = sub_res["job_id"]
            col_res = apprentice_control(action="job-collect", job_id=jid, wait_seconds=15.0)
            assert col_res["ok"] is True and col_res["status"] == "completed", f"job collect unexpected: {col_res}"
            assert col_res["result"]["completion"]["content"] == "Async sprint digest complete."
            checks.append("async_sprint_submit_and_collect")

            # 14. apprentice_repo_audit fails fast BEFORE subprocess work when server becomes unloaded
            state_box["loaded"] = False
            hom_fake = td_p / "fake_hom"
            mem_fake = td_p / "fake_mem"
            (hom_fake / "scripts").mkdir(parents=True)
            (hom_fake / "scripts" / "memory_gateway.py").write_text("#!/usr/bin/env python3\n", encoding="utf-8")
            (mem_fake / "Projects" / "Demo" / "Quarantine").mkdir(parents=True)
            old_hom_env = os.environ.get("HOMUNCULUS_ROOT")
            old_mem_env = os.environ.get("HOMUNCULUS_MEMORY_ROOT")
            os.environ["HOMUNCULUS_ROOT"] = str(hom_fake)
            os.environ["HOMUNCULUS_MEMORY_ROOT"] = str(mem_fake)
            try:
                fast_fail_audit = apprentice_repo_audit(
                    repo=str(td_p),
                    project="Demo",
                    name="audit_fast_fail",
                    title="Fast Fail",
                    reason="test",
                    prompt="audit",
                )
                assert fast_fail_audit["ok"] is False
                assert fast_fail_audit["error_code"] == "BIONIC_UNLOADED_CONFIRMATION_REQUIRED"
            finally:
                if old_hom_env is None:
                    os.environ.pop("HOMUNCULUS_ROOT", None)
                else:
                    os.environ["HOMUNCULUS_ROOT"] = old_hom_env
                if old_mem_env is None:
                    os.environ.pop("HOMUNCULUS_MEMORY_ROOT", None)
                else:
                    os.environ["HOMUNCULUS_MEMORY_ROOT"] = old_mem_env
            checks.append("repo_audit_fast_preflight_block")

            # 15. V2.3 Digest tail-continuation length heal + compact verify_claims receipt (zero report bloat)
            state_box["loaded"] = True
            state_box["ctx"] = 57344
            bom_t = td_p / "BOM.md"
            bom_t.write_text("| M3x8 SHCS | 4 |\n| M3x12 BHCS | 6 |\n", encoding="utf-8")
            state_box["replies"] = [
                ("- M3x8 SHCS: qty 4 (`BOM.md#L1`)\n- M3x12", "length"),
                ("- M3x12 BHCS: qty 6 (`BOM.md#L2`)\n", "stop"),
            ]
            len_res = apprentice_digest(
                prompt="list fasteners",
                context_files=[str(bom_t)],
                repo=str(td_p),
            )
            assert len_res["ok"] is True, f"digest length heal failed: {len_res}"
            assert len_res["verdict"] == "healed"
            assert "M3x12 BHCS: qty 6" in len_res["completion"]["content"]
            vrf15 = len_res["verify_claims"]
            assert vrf15["ran"] is True and vrf15["returncode"] == 0
            assert "report" not in vrf15 and len(json.dumps(vrf15)) <= 220
            checks.append("v23_digest_length_heal_and_compact_verify_receipt")

            # 16. V2.3 apprentice_repo_audit verify_claims self-scrub heal -> healed, persistent unbacked -> corrected
            audit_repo = td_p / "demo_repo"
            audit_repo.mkdir()
            (audit_repo / "BOM.md").write_text("| M3x8 SHCS | 4 |\n", encoding="utf-8")
            mem_v23 = td_p / "mem_v23"
            (mem_v23 / "Projects" / "Demo" / "Quarantine").mkdir(parents=True)
            (mem_v23 / "Projects" / "Demo" / "Demo.md").write_text(
                "---\nproject: Demo\nentity: Demo_Entity\ncompartment: private\n---\n# Demo\n",
                encoding="utf-8",
            )
            real_hom = os.environ.get("HOMUNCULUS_ROOT") or str(apprentice_engine.DEFAULT_HOMUNCULUS_ROOT)
            os.environ["HOMUNCULUS_ROOT"] = real_hom
            os.environ["HOMUNCULUS_MEMORY_ROOT"] = str(mem_v23)
            try:
                state_box["replies"] = [
                    ("- Fastener: 99 M5x40 SHCS (`BOM.md#L1`)\n", "stop"),
                    ("- Fastener: 4 M3x8 SHCS (`BOM.md#L1`)\n", "stop"),
                ]
                ra_heal = apprentice_repo_audit(
                    repo=str(audit_repo),
                    project="Demo",
                    name="audit_heal",
                    title="Audit Heal",
                    reason="v23 test",
                    prompt="audit fasteners",
                )
                assert ra_heal["ok"] is True and ra_heal["verdict"] == "healed", f"expected healed audit: {ra_heal}"
                assert ra_heal["claims_verified"] is True and ra_heal["elapsed_s"] > 0

                state_box["replies"] = [
                    ("- Fastener: 99 M5x40 SHCS (`BOM.md#L1`)\n", "stop"),
                    ("- Fastener: 88 M5x40 SHCS (`BOM.md#L1`)\n", "stop"),
                ]
                ra_bad = apprentice_repo_audit(
                    repo=str(audit_repo),
                    project="Demo",
                    name="audit_bad",
                    title="Audit Bad",
                    reason="v23 test",
                    prompt="audit fasteners",
                    overwrite=True,
                )
                assert ra_bad["ok"] is True and ra_bad["verdict"] == "corrected", f"expected corrected audit: {ra_bad}"
                assert ra_bad["claims_verified"] is False and ra_bad["elapsed_s"] > 0
            finally:
                if old_hom_env is None:
                    os.environ.pop("HOMUNCULUS_ROOT", None)
                else:
                    os.environ["HOMUNCULUS_ROOT"] = old_hom_env
                if old_mem_env is None:
                    os.environ.pop("HOMUNCULUS_MEMORY_ROOT", None)
                else:
                    os.environ["HOMUNCULUS_MEMORY_ROOT"] = old_mem_env
            checks.append("v23_repo_audit_verify_heal_and_fail_closed_verdict")

            # 17. V2.3 stage_patch auto --self-test AST detection without smoke_test_args
            state_box["replies"] = [
                "```python\nimport sys\nif __name__ == '__main__':\n    if '--self-test' in sys.argv:\n        sys.exit(1)\n```\n",
                "```python\nimport sys\nif __name__ == '__main__':\n    if '--self-test' in sys.argv:\n        sys.exit(0)\n```\n",
            ]
            st_auto = apprentice_stage_patch(
                target_filename="auto_st.py",
                prompt="write cli supporting --self-test",
                staging_dir=str(stage_dir),
            )
            assert st_auto["ok"] is True and st_auto["attempts"] == 2 and st_auto["verdict"] == "healed"
            assert st_auto["smoke_test"]["ran"] is True and st_auto["smoke_test"].get("auto_detected") is True
            assert st_auto["smoke_test"]["ok"] is True
            checks.append("v23_stage_patch_auto_selftest_smoke_heal")

            # 18. V2.3 control scorecard-reset confirmation gate + relative banner
            rs_deny = apprentice_control(action="scorecard-reset", user_confirmed=False)
            assert rs_deny["ok"] is False and rs_deny["error_code"] == "USER_CONFIRMATION_REQUIRED"
            rs_ok = apprentice_control(action="scorecard-reset", epoch_label="v2.3-test", user_confirmed=True)
            assert rs_ok["ok"] is True and "epoch v2.3-test: 0 calls" in rs_ok["scorecard"]
            checks.append("v23_control_scorecard_reset_confirmation_and_delta")

            # 19. V2.3 chunked map-reduce (>36 KB) + Reduce pass + verify_claims receipt
            state_box["loaded"] = True
            state_box["ctx"] = 57344
            big19 = td_p / "big_mod.py"
            big19_lines = ["ALPHA_LIMIT = 42"]
            for idx19 in range(440):
                big19_lines.append(f"def pad_{idx19:03d}():")
                big19_lines.append(f"    return '{'x' * 72}'")
            big19_lines.append("def omega_check(): return 7")
            big19.write_text("\n".join(big19_lines) + "\n", encoding="utf-8")
            n19 = len(big19_lines)
            chunks19 = apprentice_engine.plan_line_preserving_chunks([big19], target_chunk_bytes=22000)
            assert len(chunks19) >= 2, f"expected >=2 chunks, got {len(chunks19)}"

            def _chunk19_reply(req_body: str) -> tuple[str, str]:
                if "Below are verbatim per-slice extracts" in req_body:
                    return (
                        f"- `ALPHA_LIMIT = 42` (`big_mod.py#L1`)\n"
                        f"- `def omega_check(): return 7` (`big_mod.py#L{n19}`)",
                        "stop",
                    )
                if f"big_mod.py#L1-" in req_body:
                    return ("- `ALPHA_LIMIT = 42` (`big_mod.py#L1`)", "stop")
                if f"-L{n19})" in req_body:
                    return (f"- `def omega_check(): return 7` (`big_mod.py#L{n19}`)", "stop")
                return ("NONE", "stop")

            state_box["replies"] = [_chunk19_reply] * (len(chunks19) + 1)
            ch_res19 = apprentice_digest(
                prompt="Find ALPHA_LIMIT and omega_check in big_mod.py",
                context_files=[str(big19)],
                repo=str(td_p),
                effort="standard",
                invocation_tier="explicit",
            )
            assert ch_res19["ok"] is True, f"chunked test failed: {ch_res19}"
            cmr19 = ch_res19.get("chunked_map_reduce") or {}
            assert cmr19.get("enabled") is True and cmr19.get("reduced") is True, f"bad cmr19: {cmr19}"
            assert ch_res19.get("claims_verified") is True, f"chunked claims unverified: {ch_res19}"
            assert ch_res19.get("verdict") == "clean", f"expected clean verdict: {ch_res19}"
            checks.append("v23_chunked_map_reduce_and_verify_receipt")

            # 20. V2.3.1 HIGH-stress fixes: reasoning_content synthesis recovery, job-status wait_seconds, server_version
            def _reasoning_synth_reply(req_body: str) -> Any:
                if "COMPLETED DEEP-REASONING ENGINEERING TRACE FROM PASS 1" in req_body:
                    return ("- `4` M3x8 SHCS (`BOM.md#L1`)\n", "stop")
                return {
                    "choices": [
                        {
                            "index": 0,
                            "message": {
                                "role": "assistant",
                                "content": "",
                                "reasoning_content": "Inspecting BOM.md#L1 carefully... Confirmed quantity is 4 and part is M3x8 SHCS verbatim across table columns. Ready to output.",
                            },
                            "finish_reason": "length",
                        }
                    ],
                    "usage": {"prompt_tokens": 120, "completion_tokens": 8192},
                    "stats": {"tokens_per_second": 42.0},
                }

            class _FlexMockHandler(_MockMcpBionicHandler):
                def do_POST(self) -> None:  # noqa: N802
                    if self.path == "/v1/chat/completions":
                        length = int(self.headers.get("Content-Length") or 0)
                        req_body = self.rfile.read(length).decode("utf-8", errors="replace") if length else ""
                        state_box["posts"] += 1
                        raw_reply = state_box["replies"].pop(0) if state_box["replies"] else "OK"
                        if callable(raw_reply):
                            raw_reply = raw_reply(req_body)
                        if isinstance(raw_reply, dict) and "choices" in raw_reply:
                            body = json.dumps({"id": "mock-cmp", "model": apprentice_engine.DEFAULT_MODEL_ID, **raw_reply}).encode("utf-8")
                        else:
                            if isinstance(raw_reply, tuple):
                                reply_txt, finish_reason = str(raw_reply[0]), str(raw_reply[1])
                            else:
                                reply_txt, finish_reason = str(raw_reply), "stop"
                            body = json.dumps(
                                {
                                    "id": "mock-cmp",
                                    "model": apprentice_engine.DEFAULT_MODEL_ID,
                                    "choices": [{"index": 0, "message": {"role": "assistant", "content": reply_txt}, "finish_reason": finish_reason}],
                                    "usage": {"prompt_tokens": 60, "completion_tokens": 18},
                                    "stats": {"tokens_per_second": 42.0},
                                }
                            ).encode("utf-8")
                        self.send_response(200)
                        self.send_header("Content-Type", "application/json")
                        self.send_header("Content-Length", str(len(body)))
                        self.end_headers()
                        self.wfile.write(body)
                    else:
                        super().do_POST()

            srv.RequestHandlerClass = _FlexMockHandler
            state_box["replies"] = [_reasoning_synth_reply, _reasoning_synth_reply]
            synth_res = apprentice_digest(
                prompt="list M3 fastener from BOM.md",
                context_files=[str(bom_t)],
                repo=str(td_p),
                effort="high",
                invocation_tier="explicit",
            )
            assert synth_res["ok"] is True and synth_res["completion"].get("reasoning_recovered") is True, f"synth recovery failed: {synth_res}"
            assert synth_res["verdict"] == "healed" and synth_res["claims_verified"] is True, f"expected healed verified synth: {synth_res}"

            ctrl_ver = apprentice_control(action="status")
            assert ctrl_ver.get("server_version") == SERVER_VERSION
            assert ctrl_ver.get("server_stale_restart_recommended") is False

            # job-status forwards bounded wait_seconds
            jobs_td = td_p / "jobs_test"
            jobs_td.mkdir()
            (jobs_td / "BJOB-testwait.json").write_text(
                json.dumps({"job_id": "BJOB-testwait", "status": "completed", "submitted_at": "2026-01-01T00:00:00Z", "updated_at": "2026-01-01T00:00:01Z", "worker_pid": 0}),
                encoding="utf-8",
            )
            old_jdir = os.environ.get("BIONIC_SIDECAR_JOBS_DIR")
            os.environ["BIONIC_SIDECAR_JOBS_DIR"] = str(jobs_td)
            try:
                js_wait = apprentice_control(action="job-status", job_id="BJOB-testwait", wait_seconds=1.5)
                assert js_wait["ok"] is True and js_wait["status"] == "completed"
            finally:
                if old_jdir is None:
                    os.environ.pop("BIONIC_SIDECAR_JOBS_DIR", None)
                else:
                    os.environ["BIONIC_SIDECAR_JOBS_DIR"] = old_jdir
            checks.append("v231_reasoning_recovery_version_and_job_status_wait")

            # 21. V2.4 surgical line-level claim repair preserves HIGH metadata & verified bullets
            surg_repo = td_p / "surg_repo"
            surg_repo.mkdir()
            (surg_repo / "BOM.md").write_text(
                "\n".join(
                    [
                        "| Item | Qty |",
                        "| M3x8 SHCS | 4 |",
                        "| M3x12 BHCS | 6 |",
                        "| M5x10 SHCS | 8 |",
                        "| M5x20 BHCS | 2 |",
                        "| M2.5x10 SHCS | 4 |",
                        "| 2GT Pulley 20T | 2 |",
                        "| M5 Roll-In T-Nuts | 10 |",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )
            os.environ["HOMUNCULUS_ROOT"] = str(os.environ.get("HOMUNCULUS_ROOT") or apprentice_engine.DEFAULT_HOMUNCULUS_ROOT)
            os.environ["HOMUNCULUS_MEMORY_ROOT"] = str(td_p / "mem_v23")
            try:
                pass1_bullets = "\n".join(
                    [
                        "- M3x8 SHCS qty `4` (`BOM.md#L2`)",
                        "- M3x12 BHCS qty `6` (`BOM.md#L3`)",
                        "- M5x10 SHCS qty `8` (`BOM.md#L4`)",
                        "- M5x20 BHCS qty `2` (`BOM.md#L5`)",
                        "- M2.5x10 SHCS qty `4` (`BOM.md#L6`)",
                        "- 2GT Pulley 20T qty `2` (`BOM.md#L7`)",
                        "- M5 Roll-In T-Nuts qty `10` (e.g., 0.8mm pitch) (`BOM.md#L8`)",
                    ]
                )
                state_box["replies"] = [
                    (pass1_bullets, "stop"),
                    ("L7: - M5 Roll-In T-Nuts qty `10` `[TBD: pitch]` (`BOM.md#L8`)", "stop"),
                ]
                surg_res = apprentice_digest(
                    prompt="list all parts in BOM.md",
                    context_files=[str(surg_repo / "BOM.md")],
                    repo=str(surg_repo),
                    effort="high",
                    invocation_tier="explicit",
                )
                assert surg_res["ok"] is True and surg_res["verdict"] == "healed", f"surg_res fail: {surg_res}"
                assert surg_res["claims_verified"] is True
                assert surg_res["verify_claims"].get("surgical_repair") is True, f"expected surgical_repair: {surg_res}"
                assert surg_res["completion"]["effort"] == "high" and surg_res["completion"]["mode"] == "deep"
                assert "M2.5x10 SHCS qty `4`" in surg_res["completion"]["content"]
            finally:
                if old_hom_env is None:
                    os.environ.pop("HOMUNCULUS_ROOT", None)
                else:
                    os.environ["HOMUNCULUS_ROOT"] = old_hom_env
                if old_mem_env is None:
                    os.environ.pop("HOMUNCULUS_MEMORY_ROOT", None)
                else:
                    os.environ["HOMUNCULUS_MEMORY_ROOT"] = old_mem_env
            checks.append("v24_surgical_claim_repair_and_metadata_preservation")

            # 22. V2.4 packed multi-file chunk batches compress mapper calls on >36 KB corpora
            pack_dir = td_p / "pack_repo"
            pack_dir.mkdir()
            pack_files = []
            for p_idx in range(4):
                pf = pack_dir / f"part_{p_idx}.md"
                pf.write_text(
                    f"# Part {p_idx}\n"
                    + f"- M3x{8 + p_idx} SHCS qty `{p_idx + 2}`\n"
                    + "\n".join(f"note line {j:03d} " + ("x" * 125) for j in range(72))
                    + "\n",
                    encoding="utf-8",
                )
                pack_files.append(str(pf))
            assert sum(Path(pf).stat().st_size for pf in pack_files) > 36000
            os.environ["HOMUNCULUS_ROOT"] = str(apprentice_engine.DEFAULT_HOMUNCULUS_ROOT)
            os.environ["HOMUNCULUS_MEMORY_ROOT"] = str(td_p / "mem_v23")
            state_box["posts"] = 0

            def _pack_reply(req_body: str) -> tuple[str, str]:
                if "Below are verbatim per-slice extracts" in req_body:
                    return (
                        "- M3x8 SHCS qty `2` (`part_0.md#L2`)\n"
                        "- M3x9 SHCS qty `3` (`part_1.md#L2`)\n"
                        "- M3x10 SHCS qty `4` (`part_2.md#L2`)\n"
                        "- M3x11 SHCS qty `5` (`part_3.md#L2`)",
                        "stop",
                    )
                outs = []
                for p_idx in range(4):
                    if f"part_{p_idx}.md" in req_body:
                        outs.append(f"- M3x{8 + p_idx} SHCS qty `{p_idx + 2}` (`part_{p_idx}.md#L2`)")
                return ("\n".join(outs) or "NONE", "stop")

            state_box["replies"] = [_pack_reply] * 4
            try:
                pack_res = apprentice_digest(
                    prompt="list all fasteners across part_0..part_3",
                    context_files=pack_files,
                    repo=str(pack_dir),
                    effort="standard",
                    invocation_tier="auto",
                )
                assert pack_res["ok"] is True, f"pack_res failed: {pack_res}"
                cmr22 = pack_res.get("chunked_map_reduce") or {}
                assert cmr22.get("enabled") is True
                assert cmr22.get("chunks") == 4
                assert cmr22.get("batches", 99) < 4, f"expected packed batches < 4: {cmr22}"
                assert state_box["posts"] <= 3, f"expected <=3 POSTs, got {state_box['posts']}"
                assert pack_res.get("claims_verified") is True and pack_res.get("verdict") == "clean"
            finally:
                if old_hom_env is None:
                    os.environ.pop("HOMUNCULUS_ROOT", None)
                else:
                    os.environ["HOMUNCULUS_ROOT"] = old_hom_env
                if old_mem_env is None:
                    os.environ.pop("HOMUNCULUS_MEMORY_ROOT", None)
                else:
                    os.environ["HOMUNCULUS_MEMORY_ROOT"] = old_mem_env
            checks.append("v24_packed_multifile_chunk_batches")
        finally:
            if old_api is None:
                os.environ.pop("APPRENTICE_API_URL", None)
            else:
                os.environ["APPRENTICE_API_URL"] = old_api
            if old_tel is None:
                os.environ.pop("APPRENTICE_TELEMETRY_LOG", None)
            else:
                os.environ["APPRENTICE_TELEMETRY_LOG"] = old_tel
            if old_custom_port is None:
                os.environ.pop("BIONIC_ALLOW_CUSTOM_LOOPBACK_PORT", None)
            else:
                os.environ["BIONIC_ALLOW_CUSTOM_LOOPBACK_PORT"] = old_custom_port
            srv.shutdown()
            srv.server_close()

        # 8. _discover_repo_sources skip dirs (even when repo is nested under .cache/) + apprentice_control port firewall
        src_repo = td_p / ".cache" / "src_filter_repo"
        (src_repo / "node_modules" / "pkg").mkdir(parents=True)
        (src_repo / ".venv" / "lib").mkdir(parents=True)
        (src_repo / "node_modules" / "pkg" / "index.py").write_text("x = 1\n", encoding="utf-8")
        (src_repo / ".venv" / "lib" / "site.py").write_text("y = 2\n", encoding="utf-8")
        (src_repo / "main.py").write_text("z = 3\n", encoding="utf-8")
        discovered = _discover_repo_sources(src_repo.resolve())
        assert [p.name for p in discovered] == ["main.py"]

        old_api2 = os.environ.get("APPRENTICE_API_URL")
        old_cp2 = os.environ.get("BIONIC_ALLOW_CUSTOM_LOOPBACK_PORT")
        os.environ["APPRENTICE_API_URL"] = "http://127.0.0.1:2375/v1"
        os.environ.pop("BIONIC_ALLOW_CUSTOM_LOOPBACK_PORT", None)
        try:
            ctrl_bad_port = apprentice_control(action="status")
            assert ctrl_bad_port["ok"] is False
            assert ctrl_bad_port["error_code"] == "SECURITY_FIREWALL_BLOCKED"
        finally:
            if old_api2 is None:
                os.environ.pop("APPRENTICE_API_URL", None)
            else:
                os.environ["APPRENTICE_API_URL"] = old_api2
            if old_cp2 is not None:
                os.environ["BIONIC_ALLOW_CUSTOM_LOOPBACK_PORT"] = old_cp2
        checks.append("discover_sources_skip_dirs_and_control_port_firewall")

        # 9. _ensure_live_process_cwd recovers cleanly from an unlinked plugin working directory
        gone_dir = td_p / "deleted_plugin_dir"
        gone_dir.mkdir()
        try:
            orig_cwd = os.getcwd()
        except OSError:
            orig_cwd = apprentice_engine._safe_subprocess_cwd()
        try:
            os.chdir(gone_dir)
            try:
                gone_dir.rmdir()
                unlinked_ok = True
            except OSError:
                unlinked_ok = False
            if unlinked_ok:
                healed = _ensure_live_process_cwd()
                assert Path(healed).is_dir()
                assert Path(os.getcwd()).is_dir()
        finally:
            os.chdir(orig_cwd)
        checks.append("ensure_live_process_cwd_recovery")

        # 10. V2.4.2 MCP sync-window guard: fast unwrap vs >cap auto-promotion & job-collect clamp
        import http.server
        import threading

        guard_repo = td_p / "guard242_repo"
        guard_repo.mkdir()
        (guard_repo / "BOM.md").write_text("# BOM\n| M3x8 SHCS | 4 |\n", encoding="utf-8")
        guard_jobs = td_p / "guard242_jobs"
        guard_jobs.mkdir()
        guard_state = {"delay": 0.02}

        class _GuardHandler(http.server.BaseHTTPRequestHandler):
            def do_GET(self) -> None:  # noqa: N802
                body = json.dumps(
                    {"data": [{"id": apprentice_engine.DEFAULT_MODEL_ID, "state": "loaded", "loaded_context_length": 57344}]}
                ).encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)

            def do_POST(self) -> None:  # noqa: N802
                length = int(self.headers.get("Content-Length") or 0)
                if length:
                    self.rfile.read(length)
                time.sleep(float(guard_state["delay"]))
                body = json.dumps(
                    {
                        "id": "guard-test",
                        "model": apprentice_engine.DEFAULT_MODEL_ID,
                        "choices": [{"index": 0, "finish_reason": "stop", "message": {"role": "assistant", "content": "- M3x8 SHCS qty `4` (`BOM.md#L2`)"}}],
                        "usage": {"prompt_tokens": 180, "completion_tokens": 16},
                    }
                ).encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)

            def log_message(self, _fmt: str, *_args: Any) -> None:
                return

        srv_g = http.server.HTTPServer(("127.0.0.1", 0), _GuardHandler)
        threading.Thread(target=srv_g.serve_forever, daemon=True).start()
        env_keys = (
            "APPRENTICE_API_URL",
            "BIONIC_ALLOW_CUSTOM_LOOPBACK_PORT",
            "APPRENTICE_TELEMETRY_LOG",
            "BIONIC_SIDECAR_JOBS_DIR",
            "BIONIC_SIDECAR_SCORECARD_PATH",
            "BIONIC_SIDECAR_KV_STATE_PATH",
        )
        saved_env = {k: os.environ.get(k) for k in env_keys}
        saved_cap = globals()["MCP_SYNC_WAIT_CAP_SECONDS"]
        try:
            os.environ["APPRENTICE_API_URL"] = f"http://127.0.0.1:{srv_g.server_port}/v1"
            os.environ["BIONIC_ALLOW_CUSTOM_LOOPBACK_PORT"] = "1"
            os.environ["APPRENTICE_TELEMETRY_LOG"] = str(td_p / "guard242_tel.jsonl")
            os.environ["BIONIC_SIDECAR_JOBS_DIR"] = str(guard_jobs)
            os.environ["BIONIC_SIDECAR_SCORECARD_PATH"] = str(td_p / "guard242_scorecard.json")
            os.environ["BIONIC_SIDECAR_KV_STATE_PATH"] = str(td_p / "guard242_kv.json")

            globals()["MCP_SYNC_WAIT_CAP_SECONDS"] = 3.0
            fast_high = asyncio.run(
                _mcp_apprentice_digest_coro(
                    prompt="list M3 fastener",
                    context_files=[str(guard_repo / "BOM.md")],
                    repo=str(guard_repo),
                    effort="high",
                    invocation_tier="explicit",
                    verify_claims=False,
                )
            )
            assert fast_high["ok"] is True and not fast_high.get("auto_promoted_async"), f"fast unwrap fail: {fast_high}"
            assert "completion" in fast_high, f"missing unwrapped completion: {fast_high}"

            guard_state["delay"] = 1.2
            globals()["MCP_SYNC_WAIT_CAP_SECONDS"] = 0.25
            slow_high = asyncio.run(
                _mcp_apprentice_digest_coro(
                    prompt="list M3 fastener slowly",
                    context_files=[str(guard_repo / "BOM.md")],
                    repo=str(guard_repo),
                    effort="high",
                    invocation_tier="explicit",
                    verify_claims=False,
                )
            )
            assert slow_high["ok"] is True and slow_high.get("auto_promoted_async") is True, f"auto-promote fail: {slow_high}"
            assert slow_high.get("waited_sync_seconds") == 0.25
            promoted_jid = str(slow_high["job_id"])

            # Wait up to 3.0s transiently for worker completion while also testing job-collect wait clamp
            globals()["MCP_SYNC_WAIT_CAP_SECONDS"] = 5.0
            collected = apprentice_control(action="job-collect", job_id=promoted_jid, wait_seconds=500.0)
            assert collected["ok"] is True and collected["status"] == "completed", f"collect fail: {collected}"
            assert collected["waited_seconds"] == 5.0, f"expected wait_seconds clamped to 5.0: {collected}"
            assert collected["result"]["ok"] is True

            # Verify wait_seconds clamp on still-running dummy job without blocking 500s
            (guard_jobs / "BJOB-guardwait.json").write_text(
                json.dumps(
                    {
                        "job_id": "BJOB-guardwait",
                        "status": "running",
                        "submitted_at": "2026-01-01T00:00:00Z",
                        "updated_at": "2026-01-01T00:00:00Z",
                        "worker_pid": os.getpid(),
                    }
                ),
                encoding="utf-8",
            )
            globals()["MCP_SYNC_WAIT_CAP_SECONDS"] = 0.2
            t_c0 = time.perf_counter()
            clamped_run = apprentice_control(action="job-collect", job_id="BJOB-guardwait", wait_seconds=500.0)
            assert (time.perf_counter() - t_c0) < 2.0
            assert clamped_run["waited_seconds"] == 0.2 and clamped_run["status"] == "running"
        finally:
            globals()["MCP_SYNC_WAIT_CAP_SECONDS"] = saved_cap
            for k, v in saved_env.items():
                if v is None:
                    os.environ.pop(k, None)
                else:
                    os.environ[k] = v
            srv_g.shutdown()
            srv_g.server_close()
        checks.append("v242_mcp_sync_guard_auto_async_promotion_and_collect_clamp")

    # 24. V2.4.2 chunked map-reduce reduce length tail-continuation + >36KB STANDARD sync-guard check
    from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
    import threading as _mr_threading

    with tempfile.TemporaryDirectory() as td_mr:
        td_mr_p = Path(td_mr)
        mr_repo = td_mr_p / "mr_repo"
        mr_repo.mkdir()
        big_src = mr_repo / "big_rules.md"
        big_src.write_text(
            "\n".join(f"- Rule {i}: enforce bound_{i} = {10 + i} mm in big_rules.md" for i in range(900)) + "\n",
            encoding="utf-8",
        )
        assert big_src.stat().st_size > 40000
        small_src = mr_repo / "small.md"
        small_src.write_text("- M3 SHCS x 8mm\n", encoding="utf-8")
        assert _is_heavy_chunked_sync_candidate("digest", {"context_files": [str(big_src)], "repo": str(mr_repo)}) is True
        assert _is_heavy_chunked_sync_candidate("digest", {"context_files": [f"{big_src}#L1-L20"], "repo": str(mr_repo)}) is False
        assert _is_heavy_chunked_sync_candidate("digest", {"context_files": [str(small_src)], "repo": str(mr_repo)}) is False

        seen_prompts_24: list[str] = []

        class _ChunkRedLenHandler(BaseHTTPRequestHandler):
            def log_message(self, format: str, *args: Any) -> None:
                return

            def do_GET(self) -> None:
                if self.path == "/api/v0/models":
                    body = json.dumps({"data": [{"id": apprentice_engine.DEFAULT_MODEL_ID, "state": "loaded", "loaded_context_length": 49152}]}).encode("utf-8")
                    self.send_response(200)
                    self.send_header("Content-Type", "application/json")
                    self.send_header("Content-Length", str(len(body)))
                    self.end_headers()
                    self.wfile.write(body)
                else:
                    self.send_response(404)
                    self.end_headers()

            def do_POST(self) -> None:
                if self.path == "/v1/chat/completions":
                    length = int(self.headers.get("Content-Length", "0"))
                    req = json.loads(self.rfile.read(length).decode("utf-8"))
                    u_txt = str((req.get("messages") or [{}, {}])[-1].get("content") or "")
                    seen_prompts_24.append(u_txt)
                    if "Your previous response hit the output token limit" in u_txt:
                        ans = "- Tail item from big_rules.md#L500-L500 (healed)"
                        f_reason = "stop"
                    elif "Below are verbatim per-slice extracts" in u_txt:
                        assert req.get("max_tokens", 0) >= 2048
                        ans = "- Rule 1 from big_rules.md#L1-L1\n- partial trunc"
                        f_reason = "length"
                    else:
                        ans = "- Slice item in big_rules.md#L1-L1"
                        f_reason = "stop"
                    body = json.dumps(
                        {
                            "choices": [{"message": {"content": ans}, "finish_reason": f_reason}],
                            "usage": {"prompt_tokens": 120, "completion_tokens": 40},
                        }
                    ).encode("utf-8")
                    self.send_response(200)
                    self.send_header("Content-Type", "application/json")
                    self.send_header("Content-Length", str(len(body)))
                    self.end_headers()
                    self.wfile.write(body)
                else:
                    self.send_response(404)
                    self.end_headers()

        srv_24 = ThreadingHTTPServer(("127.0.0.1", 0), _ChunkRedLenHandler)
        th_24 = _mr_threading.Thread(target=srv_24.serve_forever, daemon=True)
        th_24.start()
        mr_cache = td_mr_p / "mr_cache"
        mr_cache.mkdir()
        saved_env24 = {k: os.environ.get(k) for k in ("APPRENTICE_API_URL", "BIONIC_ALLOW_CUSTOM_LOOPBACK_PORT", "APPRENTICE_TELEMETRY_LOG", "BIONIC_SIDECAR_SCORECARD_PATH", "BIONIC_SIDECAR_KV_STATE_PATH", "BIONIC_SIDECAR_JOBS_DIR")}
        try:
            os.environ["APPRENTICE_API_URL"] = f"http://127.0.0.1:{srv_24.server_port}/v1"
            os.environ["BIONIC_ALLOW_CUSTOM_LOOPBACK_PORT"] = "1"
            os.environ["APPRENTICE_TELEMETRY_LOG"] = str(mr_cache / "tel.jsonl")
            os.environ["BIONIC_SIDECAR_SCORECARD_PATH"] = str(mr_cache / "sc.json")
            os.environ["BIONIC_SIDECAR_KV_STATE_PATH"] = str(mr_cache / "kv.json")
            os.environ["BIONIC_SIDECAR_JOBS_DIR"] = str(mr_cache / "jobs")
            res24 = _apprentice_digest_sync(
                prompt="Summarize rules in big_rules.md",
                context_files=[str(big_src)],
                repo=str(mr_repo),
                effort="standard",
                invocation_tier="explicit",
                verify_claims=False,
            )
            assert res24["ok"] is True, f"chunk red heal failed: {res24}"
            assert res24["verdict"] == "healed", f"expected healed chunk reduce verdict, got: {res24}"
            assert res24["completion"]["finish_reason"] == "stop"
            assert res24["heal_elapsed_s"] >= 0.0 and "Tail item" in res24["completion"]["content"]
            assert any("Your previous response hit the output token limit" in p and "Below are verbatim per-slice extracts" in p for p in seen_prompts_24)
        finally:
            for k, v in saved_env24.items():
                if v is None:
                    os.environ.pop(k, None)
                else:
                    os.environ[k] = v
            srv_24.shutdown()
            srv_24.server_close()
    checks.append("v242_chunk_reduce_length_continuation_and_heavy_std_guard")

    # 25. V2.4.3 HIGH repair headroom (>=4096), non-regression guard, & multi-slice same-file preservation
    with tempfile.TemporaryDirectory() as td_25:
        td25_p = Path(td_25)
        r25 = td25_p / "repo25"
        r25.mkdir()
        ms25 = r25 / "BOM.md"
        ms25.write_text(
            "# BOM\n- Part A: 12 mm\n- filler 3\n- filler 4\n- filler 5\n- filler 6\n- filler 7\n- Part B: 24 V\n",
            encoding="utf-8",
        )
        seen_25: list[dict[str, Any]] = []
        replies_25 = [
            (
                "- Part A: `12 mm` (`BOM.md#L2-L2`)\n"
                "- Part B: `24 V` (`BOM.md#L8-L8`)\n"
                "- Extra unbacked leak: `99 A` (`BOM.md#L8-L8`)",
                "stop",
            ),
            # Full repair hits length clip -> continuation hop runs and returns still-failing/gutted draft -> guard MUST keep initial!
            ("- Short clipped `88 A`", "length"),
            ("and tail `77 A`", "stop"),
        ]

        class _V25Handler(BaseHTTPRequestHandler):
            def log_message(self, fmt: str, *args: Any) -> None:
                return

            def do_GET(self) -> None:
                if self.path == "/api/v0/models":
                    payload = {"data": [{"id": apprentice_engine.DEFAULT_MODEL_ID, "state": "loaded", "loaded_context_length": 57344}]}
                elif self.path == "/v1/models":
                    payload = {"data": [{"id": apprentice_engine.DEFAULT_MODEL_ID}]}
                else:
                    self.send_response(404)
                    self.end_headers()
                    return
                body = json.dumps(payload).encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)

            def do_POST(self) -> None:
                length = int(self.headers.get("Content-Length", "0"))
                req = json.loads(self.rfile.read(length).decode("utf-8"))
                seen_25.append(req)
                txt, fr = replies_25.pop(0) if replies_25 else ("- Part A: `12 mm` (`BOM.md#L2-L2`)", "stop")
                body = json.dumps(
                    {
                        "choices": [{"index": 0, "message": {"role": "assistant", "content": txt}, "finish_reason": fr}],
                        "usage": {"prompt_tokens": 200, "completion_tokens": 100},
                    }
                ).encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)

        srv25 = ThreadingHTTPServer(("127.0.0.1", 0), _V25Handler)
        import threading as _th25

        th25 = _th25.Thread(target=srv25.serve_forever, daemon=True)
        th25.start()
        cache25 = td25_p / "c25"
        cache25.mkdir()
        saved25 = {
            k: os.environ.get(k)
            for k in (
                "APPRENTICE_API_URL",
                "BIONIC_ALLOW_CUSTOM_LOOPBACK_PORT",
                "APPRENTICE_TELEMETRY_LOG",
                "BIONIC_SIDECAR_SCORECARD_PATH",
                "BIONIC_SIDECAR_KV_STATE_PATH",
                "BIONIC_SIDECAR_JOBS_DIR",
            )
        }
        try:
            os.environ["APPRENTICE_API_URL"] = f"http://127.0.0.1:{srv25.server_port}/v1"
            os.environ["BIONIC_ALLOW_CUSTOM_LOOPBACK_PORT"] = "1"
            os.environ["APPRENTICE_TELEMETRY_LOG"] = str(cache25 / "tel.jsonl")
            os.environ["BIONIC_SIDECAR_SCORECARD_PATH"] = str(cache25 / "sc.json")
            os.environ["BIONIC_SIDECAR_KV_STATE_PATH"] = str(cache25 / "kv.json")
            os.environ["BIONIC_SIDECAR_JOBS_DIR"] = str(cache25 / "jobs")
            res25 = _apprentice_digest_sync(
                prompt="Extract specs from both slices",
                context_files=[f"{ms25}#L1-L2", f"{ms25}#L8-L8"],
                repo=str(r25),
                effort="high",
                invocation_tier="explicit",
                verify_claims=True,
            )
            assert res25["ok"] is True, f"res25 failed: {res25}"
            assert [m["label"] for m in res25["context_files"]] == ["BOM.md#L1-L2", "BOM.md#L8-L8"], f"multi-slice dropped: {res25['context_files']}"
            # Full repair request (2nd call) must get >=4096 tokens under HIGH mode (not clipped 2560!), plus 3rd continuation hop
            assert len(seen_25) == 3 and int(seen_25[1].get("max_tokens") or 0) >= 4096, f"repair max_tokens too small: {seen_25}"
            # Clipped/regressed repair must NOT clobber richer initial draft
            assert "Part A" in res25["completion"]["content"] and "Part B" in res25["completion"]["content"], f"non-regression guard failed: {res25['completion']}"
            assert res25["completion"]["finish_reason"] == "stop"
            assert res25["verdict"] == "corrected"
        finally:
            for k, v in saved25.items():
                if v is None:
                    os.environ.pop(k, None)
                else:
                    os.environ[k] = v
            srv25.shutdown()
            srv25.server_close()
    checks.append("v243_high_repair_headroom_guard_and_multi_slice")

    # 26. V2.4.4 mixed unsliced+sliced auto-chunking (preserving explicit #L slices) + compact verify manifest
    with tempfile.TemporaryDirectory() as td_26:
        td26_p = Path(td_26)
        r26 = td26_p / "repo26"
        r26.mkdir()
        big26 = r26 / "big_mig.patch"
        big26.write_text(
            "\n".join(f"+added_symbol_{i} = {100 + i}  # padding text to push patch >45 KB safely" for i in range(720)) + "\n",
            encoding="utf-8",
        )
        assert big26.stat().st_size > 44000
        sl26 = r26 / "helper.py"
        sl26.write_text(
            "OUTSIDE_BEFORE = 111\n"
            + "\n".join(f"LINE_{k} = {k}" for k in range(2, 120))
            + "\nOUTSIDE_AFTER = 999\n",
            encoding="utf-8",
        )
        assert _is_heavy_chunked_sync_candidate(
            "digest",
            {"context_files": [str(big26), f"{sl26}#L3-L5"], "repo": str(r26)},
        ) is True

        # Compact manifest must preserve all 12 claim anchors even when line_text is huge
        bulky_claims = [
            {
                "line": (i // 3) + 1,
                "type": "UNBACKED_PROVENANCE_REF",
                "claim": f"`claim_target_{i}.md#L{10 + i}`",
                "line_text": f"Verbose line {i} " + ("x" * 600),
            }
            for i in range(12)
        ]
        compact_msg = _format_compact_verify_failures({"unbacked_claims": bulky_claims}, max_chars=2800)
        assert len(compact_msg) < 1500 and "`claim_target_11.md#L21`" in compact_msg, f"manifest failed: {compact_msg}"

        seen_prompts_26: list[str] = []

        class _V26Handler(BaseHTTPRequestHandler):
            def log_message(self, fmt: str, *args: Any) -> None:
                return

            def do_GET(self) -> None:
                if self.path == "/api/v0/models":
                    payload = {"data": [{"id": apprentice_engine.DEFAULT_MODEL_ID, "state": "loaded", "loaded_context_length": 49152}]}
                elif self.path == "/v1/models":
                    payload = {"data": [{"id": apprentice_engine.DEFAULT_MODEL_ID}]}
                else:
                    self.send_response(404)
                    self.end_headers()
                    return
                body = json.dumps(payload).encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)

            def do_POST(self) -> None:
                length = int(self.headers.get("Content-Length", "0"))
                req = json.loads(self.rfile.read(length).decode("utf-8"))
                u_txt = str((req.get("messages") or [{}, {}])[-1].get("content") or "")
                seen_prompts_26.append(u_txt)
                if "Below are verbatim per-slice extracts" in u_txt:
                    ans = "- `LINE_3 = 3` (`helper.py#L3-L3`)\n- `added_symbol_0 = 100` (`big_mig.patch#L1-L1`)"
                elif "helper.py" in u_txt:
                    assert "OUTSIDE_AFTER" not in u_txt, "Explicit #L slice must NOT expand full file when sibling patch chunks!"
                    ans = "- `LINE_3 = 3` (`helper.py#L3-L3`)"
                elif "big_mig.patch#L1-" in u_txt:
                    ans = "- `added_symbol_0 = 100` (`big_mig.patch#L1-L1`)"
                else:
                    ans = "NONE"
                body = json.dumps(
                    {
                        "choices": [{"index": 0, "message": {"role": "assistant", "content": ans}, "finish_reason": "stop"}],
                        "usage": {"prompt_tokens": 180, "completion_tokens": 60},
                    }
                ).encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)

        srv26 = ThreadingHTTPServer(("127.0.0.1", 0), _V26Handler)
        import threading as _th26

        _th26.Thread(target=srv26.serve_forever, daemon=True).start()
        cache26 = td26_p / "c26"
        cache26.mkdir()
        saved26 = {
            k: os.environ.get(k)
            for k in (
                "APPRENTICE_API_URL",
                "BIONIC_ALLOW_CUSTOM_LOOPBACK_PORT",
                "APPRENTICE_TELEMETRY_LOG",
                "BIONIC_SIDECAR_SCORECARD_PATH",
                "BIONIC_SIDECAR_KV_STATE_PATH",
                "BIONIC_SIDECAR_JOBS_DIR",
            )
        }
        try:
            os.environ["APPRENTICE_API_URL"] = f"http://127.0.0.1:{srv26.server_port}/v1"
            os.environ["BIONIC_ALLOW_CUSTOM_LOOPBACK_PORT"] = "1"
            os.environ["APPRENTICE_TELEMETRY_LOG"] = str(cache26 / "tel.jsonl")
            os.environ["BIONIC_SIDECAR_SCORECARD_PATH"] = str(cache26 / "sc.json")
            os.environ["BIONIC_SIDECAR_KV_STATE_PATH"] = str(cache26 / "kv.json")
            os.environ["BIONIC_SIDECAR_JOBS_DIR"] = str(cache26 / "jobs")
            res26 = _apprentice_digest_sync(
                prompt="Audit big_mig.patch and helper.py#L3-L5",
                context_files=[str(big26), f"{sl26}#L3-L5"],
                repo=str(r26),
                effort="high",
                invocation_tier="explicit",
                verify_claims=True,
            )
            assert res26["ok"] is True, f"res26 failed: {res26}"
            cmr26 = res26.get("chunked_map_reduce") or {}
            assert cmr26.get("enabled") is True and cmr26.get("reduced") is True, f"mixed chunking inactive: {cmr26}"
            assert res26.get("claims_verified") is True and res26.get("verdict") == "clean", f"res26 unverified: {res26}"
            assert any(m.get("label") == "helper.py#L3-L5" for m in res26.get("context_files") or []), f"slice meta lost: {res26.get('context_files')}"
        finally:
            for k, v in saved26.items():
                if v is None:
                    os.environ.pop(k, None)
                else:
                    os.environ[k] = v
            srv26.shutdown()
            srv26.server_close()
    checks.append("v244_mixed_chunking_compact_manifest_and_guard_parity")

    # 27. V2.4.5 multi-file explicit #L slice-count map-reduce (>=5 slices across >=3 files) + sync guard
    with tempfile.TemporaryDirectory() as td_27:
        td27_p = Path(td_27)
        r27 = td27_p / "repo27"
        r27.mkdir()
        mod_slices_27: list[str] = []
        for idx27 in range(6):
            mf27 = r27 / f"module_{idx27}.md"
            mf27.write_text(
                f"OUTSIDE_TOP_{idx27}\n"
                f"note {idx27}\n"
                f"- LIMIT_ALPHA_{idx27} = {100 + idx27}\n"
                f"- LIMIT_BETA_{idx27} = {200 + idx27}\n"
                f"OUTSIDE_BOT_{idx27}\n",
                encoding="utf-8",
            )
            mod_slices_27.append(f"{mf27}#L3-L4")
        single_mod_27 = r27 / "single_mod.md"
        single_mod_27.write_text(
            "\n".join(f"- SINGLE_ITEM_{k} = {k}" for k in range(1, 21)) + "\n",
            encoding="utf-8",
        )
        same_file_5_slices = [f"{single_mod_27}#L{1 + k * 2}-L{2 + k * 2}" for k in range(5)]

        assert _is_heavy_chunked_sync_candidate("digest", {"context_files": mod_slices_27, "repo": str(r27)}) is False
        assert _is_heavy_chunked_sync_candidate(
            "digest",
            {"context_files": mod_slices_27 + same_file_5_slices[:3], "repo": str(r27)},
        ) is True

        seen_27: list[dict[str, Any]] = []

        class _V27Handler(BaseHTTPRequestHandler):
            def log_message(self, fmt: str, *args: Any) -> None:
                return

            def do_GET(self) -> None:
                if self.path == "/api/v0/models":
                    payload = {"data": [{"id": apprentice_engine.DEFAULT_MODEL_ID, "state": "loaded", "loaded_context_length": 49152}]}
                elif self.path == "/v1/models":
                    payload = {"data": [{"id": apprentice_engine.DEFAULT_MODEL_ID}]}
                else:
                    self.send_response(404)
                    self.end_headers()
                    return
                body = json.dumps(payload).encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)

            def do_POST(self) -> None:
                length = int(self.headers.get("Content-Length", "0"))
                req = json.loads(self.rfile.read(length).decode("utf-8"))
                u_txt = str((req.get("messages") or [{}, {}])[-1].get("content") or "")
                seen_27.append({"req": req, "user": u_txt})
                if "Below are verbatim per-slice extracts" in u_txt:
                    ans = "\n".join(f"- `LIMIT_ALPHA_{j} = {100 + j}` (`module_{j}.md#L3-L3`)" for j in range(6))
                elif "module_" in u_txt:
                    hits = [f"- `LIMIT_ALPHA_{j} = {100 + j}` (`module_{j}.md#L3-L3`)" for j in range(6) if f"module_{j}.md" in u_txt]
                    ans = "\n".join(hits) if hits else "NONE"
                else:
                    ans = "- `SINGLE_ITEM_1 = 1` (`single_mod.md#L1-L1`)"
                body = json.dumps(
                    {
                        "choices": [{"index": 0, "message": {"role": "assistant", "content": ans}, "finish_reason": "stop"}],
                        "usage": {"prompt_tokens": 160, "completion_tokens": 45},
                    }
                ).encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)

        srv27 = ThreadingHTTPServer(("127.0.0.1", 0), _V27Handler)
        import threading as _th27

        _th27.Thread(target=srv27.serve_forever, daemon=True).start()
        cache27 = td27_p / "c27"
        cache27.mkdir()
        saved27 = {
            k: os.environ.get(k)
            for k in (
                "APPRENTICE_API_URL",
                "BIONIC_ALLOW_CUSTOM_LOOPBACK_PORT",
                "APPRENTICE_TELEMETRY_LOG",
                "BIONIC_SIDECAR_SCORECARD_PATH",
                "BIONIC_SIDECAR_KV_STATE_PATH",
                "BIONIC_SIDECAR_JOBS_DIR",
            )
        }
        try:
            os.environ["APPRENTICE_API_URL"] = f"http://127.0.0.1:{srv27.server_port}/v1"
            os.environ["BIONIC_ALLOW_CUSTOM_LOOPBACK_PORT"] = "1"
            os.environ["APPRENTICE_TELEMETRY_LOG"] = str(cache27 / "tel.jsonl")
            os.environ["BIONIC_SIDECAR_SCORECARD_PATH"] = str(cache27 / "sc.json")
            os.environ["BIONIC_SIDECAR_KV_STATE_PATH"] = str(cache27 / "kv.json")
            os.environ["BIONIC_SIDECAR_JOBS_DIR"] = str(cache27 / "jobs")

            res27_multi = _apprentice_digest_sync(
                prompt="Extract EVERY LIMIT_ALPHA_* across modules",
                context_files=mod_slices_27,
                repo=str(r27),
                effort="standard",
                invocation_tier="explicit",
                verify_claims=True,
            )
            assert res27_multi["ok"] is True and res27_multi["verdict"] == "clean", f"res27_multi failed: {res27_multi}"
            cmr27 = res27_multi.get("chunked_map_reduce") or {}
            assert cmr27.get("enabled") is True and cmr27.get("batches") == 2 and cmr27.get("reduced") is True, f"bad cmr27: {cmr27}"
            for item27 in seen_27:
                if "Below are verbatim" not in item27["user"] and "module_" in item27["user"]:
                    assert "OUTSIDE_TOP" not in item27["user"] and "OUTSIDE_BOT" not in item27["user"], "Map batch leaked lines outside #L3-L4"

            res27_same = _apprentice_digest_sync(
                prompt="Extract SINGLE_ITEM_1",
                context_files=same_file_5_slices,
                repo=str(r27),
                effort="standard",
                invocation_tier="explicit",
                verify_claims=True,
            )
            assert res27_same["ok"] is True and not res27_same.get("chunked_map_reduce"), f"same-file slices should stay unchunked: {res27_same}"

            # 28. V2.4.5 stage_patch Pass-1 .py rules vs .patch, plus fast Pass-2 repair with prioritized #L context & sleep detection
            schema28 = r27 / "schema.py"
            schema28.write_text("SCHEMA_TAG = 'SLICE_V2'\nREQ = ('a', 'b')\ndef ok_bound(): return True\n", encoding="utf-8")
            oversize28 = r27 / "oversize_ref.py"
            oversize28.write_text("\n".join(f"PAD_{k} = {k}  # filler text for >20KB cap" for k in range(600)) + "\n", encoding="utf-8")
            assert oversize28.stat().st_size > 21000

            seen_27.clear()

            class _V28Handler(_V27Handler):
                def do_POST(self) -> None:
                    length = int(self.headers.get("Content-Length", "0"))
                    req = json.loads(self.rfile.read(length).decode("utf-8"))
                    u_txt = str((req.get("messages") or [{}, {}])[-1].get("content") or "")
                    seen_27.append({"req": req, "user": u_txt})
                    call_n = len(seen_27)
                    if call_n == 1:
                        ans = (
                            "```python\nimport sys, time\n"
                            "def run():\n    return 'SLICE_V1'\n"
                            "if __name__ == '__main__':\n    if '--self-test' in sys.argv:\n"
                            "        time.sleep(0.5)\n        assert False, 'bad schema'\n```\n"
                        )
                    elif call_n == 2:
                        ans = (
                            "```python\nimport sys\n"
                            "SCHEMA_TAG = 'SLICE_V2'\n"
                            "if __name__ == '__main__':\n    if '--self-test' in sys.argv:\n"
                            "        assert SCHEMA_TAG == 'SLICE_V2'\n        print('[PASS]')\n```\n"
                        )
                    else:
                        ans = "```diff\n--- a/x.py\n+++ b/x.py\n@@ -1 +1 @@\n-a\n+b\n```\n"
                    body = json.dumps(
                        {
                            "choices": [{"index": 0, "message": {"role": "assistant", "content": ans}, "finish_reason": "stop"}],
                            "usage": {"prompt_tokens": 140, "completion_tokens": 50},
                        }
                    ).encode("utf-8")
                    self.send_response(200)
                    self.send_header("Content-Type", "application/json")
                    self.send_header("Content-Length", str(len(body)))
                    self.end_headers()
                    self.wfile.write(body)

            srv27.RequestHandlerClass = _V28Handler
            stg28 = r27 / "stg28"
            stg28.mkdir()
            res28 = _apprentice_stage_patch_sync(
                target_filename="mod_v245.py",
                prompt="Implement validator matching schema.py#L1-L3 with --self-test",
                context_files=[str(oversize28), f"{schema28}#L1-L3"],
                repo=str(r27),
                staging_dir=str(stg28),
                effort="high",
                invocation_tier="explicit",
            )
            assert res28["ok"] is True and res28["verdict"] == "healed" and res28["attempts"] == 2, f"res28 failed: {res28}"
            assert res28["smoke_test"]["ok"] is True
            assert len(seen_27) == 2, f"expected 2 stage calls, got {len(seen_27)}"
            assert "[PYTHON STAGING RULES:" in seen_27[0]["user"] and "clock=time.monotonic" in seen_27[0]["user"], "Pass-1 .py staging rules missing"
            assert "[HIGH-EFFORT EXECUTION DISCIPLINE:" in seen_27[0]["user"], "Pass-1 HIGH hint missing"
            assert seen_27[1]["req"].get("reasoning_effort") == "none", f"Pass-2 repair must run in fast mode, got: {seen_27[1]['req'].get('reasoning_effort')}"
            assert "SCHEMA_TAG = 'SLICE_V2'" in seen_27[1]["user"] and "schema.py#L1-L3" in seen_27[1]["user"], "Prioritized #L context missing from Pass-2"
            assert "[SMOKE_SLEEP_ANTIPATTERN]" in seen_27[1]["user"], "Sleep antipattern diagnostic missing from Pass-2"
            assert "oversize_ref.py" not in seen_27[1]["user"], "Oversized full file should be omitted from Pass-2 context"
            assert "[HIGH-EFFORT EXECUTION DISCIPLINE:" not in seen_27[1]["user"], "HIGH thinking hint should not pollute fast Pass-2"

            res28_patch = _apprentice_stage_patch_sync(
                target_filename="fix.patch",
                prompt="Generate patch diff",
                staging_dir=str(stg28),
                effort="standard",
            )
            assert res28_patch["ok"] is True and len(seen_27) == 3
            assert "[PYTHON STAGING RULES:" not in seen_27[2]["user"], "Non-.py patch target must not receive .py staging rules"
        finally:
            for k, v in saved27.items():
                if v is None:
                    os.environ.pop(k, None)
                else:
                    os.environ[k] = v
            srv27.shutdown()
            srv27.server_close()
    checks.append("v245_slice_count_mapreduce_and_fast_ctx_stage_repair")

    return {
        "schema_version": "APPRENTICE_MCP_V1",
        "status": "PASS",
        "mcp_library_active": _HAS_MCP,
        "tools_registered": sorted(tools),
        "tests_run": len(checks),
        "checks": checks,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Antigravity MCP Server for Apprentice Multi-Backend Local Sidecar")
    parser.add_argument("--self-test", action="store_true", help="Run deterministic offline MCP server self-tests")
    parser.add_argument("--status", action="store_true", help="Print Bionic control status JSON and exit")
    parser.add_argument("--json", action="store_true", help="Emit indented JSON output")
    args = parser.parse_args(argv)

    if args.self_test:
        try:
            res = run_self_tests()
        except Exception as exc:
            err_payload = {"schema_version": "APPRENTICE_MCP_V1", "status": "FAIL", "error": f"{type(exc).__name__}: {exc}"}
            print(json.dumps(err_payload, indent=2) if args.json else f"[MCP_SELF_TEST_FAIL] {err_payload['error']}", file=sys.stderr)
            return 3
        print(json.dumps(res, indent=2) if args.json else f"[PASS] {res['tests_run']} MCP server tests passed")
        return 0
    if args.status:
        print(json.dumps(apprentice_control(action="status"), indent=2))
        return 0

    mcp.run(transport="stdio")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
