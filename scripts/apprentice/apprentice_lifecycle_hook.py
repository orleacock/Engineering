#!/usr/bin/env python3
"""
Antigravity Lifecycle Hook for Apprentice Multi-Backend Sidecar (`apprentice_lifecycle_hook.py`).

Pure Python 3.10+ stdlib handler for `SessionStart`, `PreInvocation`, and `PreToolUse`:
  - `SessionStart`: Marks `pending_turn1_notice=True` without emitting pre-prompt steps.
  - `PreInvocation`: Fast (<80ms socket timeout) loopback check against `/api/v0/models`
    distinguishing `ONLINE_READY`, `UNLOADED`, and `OFFLINE`. Injects pure `systemMessage`
    Turn-1 / idle-reconnect / transition / explicit-tag steps (without `systemMessage.metadata`
    or `terminationBehavior`) so `agy` renders cleanly without proto reflection panics.
  - `PreToolUse` (`run_command`): Hard-denies raw `:1234` HTTP clients, direct Bionic
    AppImage launches, shell-chained `:1234` smuggling, and raw `lms` lifecycle/chat
    bypasses so `apprentice_engine.py` / `apprentice` MCP governance always applies.
"""
from __future__ import annotations

import argparse
import hashlib
import http.server
import json
import os
import re
import shlex
import sys
import tempfile
import threading
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

DEFAULT_API_URL = "http://127.0.0.1:1234/v1"
DEFAULT_MODEL_ID = "qwen3.6-35b-a3b"
PROBE_TIMEOUT_S = 0.08
IDLE_RENOTIFY_SECONDS = 900
LOOPBACK_HOSTS = frozenset({"127.0.0.1", "localhost", "::1"})

SAFE_READONLY_CMDS = frozenset({"grep", "rg", "sha256sum", "wc", "stat", "cat", "head", "tail", "diff", "ls"})
GIT_SAFE_READONLY_SUBCMDS = frozenset(
    {"grep", "log", "diff", "show", "status", "blame", "ls-files", "rev-parse", "add", "restore"}
)
WRAPPER_CMDS = frozenset({"timeout", "nice", "stdbuf", "env"})
DANGEROUS_ENV_PREFIXES = ("PYTHON", "LD_", "DYLD_")
DANGEROUS_ENV_NAMES = frozenset({"BASH_ENV", "ENV"})
HOOK_SCRIPTS_ROOT = Path(__file__).resolve().parent.parent
TRUSTED_SCRIPT_ROOTS = (
    HOOK_SCRIPTS_ROOT,
    Path("/home/orin/Projects/Engineering/scripts"),
    Path("/home/orin/Projects/Alchemical3D/Homunculus/scripts"),
    Path("/home/orin/Projects/Alchemical3D/Homunculus/skills"),
)
TRUSTED_INVOCATION_ROOTS = TRUSTED_SCRIPT_ROOTS + (
    Path("/home/orin/.gemini/config/skills"),
    Path("/home/orin/.gemini/config/plugins"),
)
GOVERNED_PY_SCRIPTS = frozenset(
    {
        "apprentice_engine.py",
        "apprentice_lifecycle_hook.py",
        "apprentice_mcp_server.py",
        "benchmark_apprentice.py",
        "sandbox_runner.py",
        "audit_data_boundary.py",
        "audit_portability.py",
        "audit_repo_docs.py",
        "audit_skill_hygiene.py",
        "memory_gateway.py",
        "sync_memory.py",
        "verify_claims.py",
    }
)
LMS_BLOCKED_SUBCMDS = frozenset({"daemon", "server", "load", "unload", "chat"})
SHELL_WRAPPER_CMDS = frozenset({"sh", "bash", "zsh", "dash", "ksh", "ash", "fish"})
EXPLICIT_TAG_RE = re.compile(r"\[(local|bionic|apprentice|ollama|llamacpp)\]", re.IGNORECASE)
PORT_1234_RE = re.compile(
    r"(?:(?:(?<![\w.])(?:127\.\d{1,3}\.\d{1,3}\.\d{1,3}|0177(?:\.0*\d{1,3}){3}|localhost|0\.0\.0\.0|::1|::ffff:127\.0\.0\.1|2130706433|0x7f0{0,4}0*1)(?!\w)|\[::1\]|\[::ffff:127\.0\.0\.1\])[^\n]{0,40}?\b(?:0*1234|0x0*4d2)\b|(?:^|[\s'\"=/(\[]):(0*1234|0x0*4d2)\b)",
    re.IGNORECASE,
)
APPIMAGE_RE = re.compile(
    r"(?:(?:lm-studio-bionic|bionic-)[^\s/]*\.appimage\b|/\.lmstudio/apps/bionic/)",
    re.IGNORECASE,
)
LMS_BIN_RE = re.compile(r"(?:^|[/\s'\"(=])lms(?:\s|$|['\")])", re.IGNORECASE)
SIDECAR_SCRIPT_RE = re.compile(
    r"\b(?:apprentice_engine\.py|apprentice_lifecycle_hook\.py|apprentice_mcp_server\.py|benchmark_apprentice\.py)\b",
    re.IGNORECASE,
)


def _read_lifetime_scorecard_banner() -> str:
    """Read lightweight Bionic scorecard banner with relative usability and epoch delta without mutating host files."""
    tel_env = (os.environ.get("APPRENTICE_TELEMETRY_LOG", "") or os.environ.get("BIONIC_SIDECAR_TELEMETRY_LOG", "")).strip()
    cache_dir = Path(os.path.expanduser(tel_env)).parent if tel_env else (Path.home() / ".cache" / "apprentice_plugin")
    sc_path = cache_dir / "apprentice_scorecard.json"
    try:
        if sc_path.is_file():
            obj = json.loads(sc_path.read_text(encoding="utf-8"))
            if isinstance(obj, dict):
                clean = int(obj.get("clean") or 0)
                corr = int(obj.get("corrected") or 0)
                healed = int(obj.get("healed") or 0)
                total = clean + corr + healed
                base = f"Apprentice Calls = {clean}/{corr} (healed={healed})"
                prev = obj.get("prev_epoch") if isinstance(obj.get("prev_epoch"), dict) else None
                if total > 0:
                    usable_pct = round(100.0 * (clean + healed) / total, 1)
                    corr_pct = round(100.0 * corr / total, 1)
                    if prev is not None and "usable_pct" in prev:
                        prev_lbl = str(prev.get("epoch_label") or "prev")
                        delta = round(usable_pct - float(prev["usable_pct"]), 1)
                        return f"{base} [{usable_pct:.1f}% usable, {corr_pct:.1f}% corr | {delta:+.1f}% vs {prev_lbl}]"
                    return f"{base} [{usable_pct:.1f}% usable, {corr_pct:.1f}% corr]"
                if prev is not None and "usable_pct" in prev:
                    prev_lbl = str(prev.get("epoch_label") or "prev")
                    epoch = str(obj.get("epoch") or "lifetime")
                    return f"{base} [epoch {epoch}: 0 calls | {prev_lbl}={float(prev['usable_pct']):.1f}% usable]"
                return base
        tel_path = Path(os.path.expanduser(tel_env)) if tel_env else (cache_dir / "apprentice_usage_telemetry.jsonl")
        if tel_path.is_file():
            clean = 0
            corr = 0
            healed = 0
            for raw in tel_path.read_text(encoding="utf-8", errors="replace").splitlines():
                if not raw.strip():
                    continue
                row = json.loads(raw)
                if (row.get("tripped") or row.get("finish_reason") == "eta_tripped") and not row.get("http_error") and not row.get("elapsed_s"):
                    continue
                cmd_name = str(row.get("cmd") or "")
                if cmd_name.endswith("_retry") or row.get("is_retry") or row.get("synthetic_fault"):
                    continue
                v = str(row.get("verdict") or "").lower()
                if v == "clean" or (not v and row.get("finish_reason") == "stop"):
                    clean += 1
                elif v == "healed":
                    healed += 1
                else:
                    corr += 1
            total = clean + corr + healed
            base = f"Apprentice Calls = {clean}/{corr} (healed={healed})"
            if total > 0:
                usable_pct = round(100.0 * (clean + healed) / total, 1)
                corr_pct = round(100.0 * corr / total, 1)
                return f"{base} [{usable_pct:.1f}% usable, {corr_pct:.1f}% corr]"
            return base
    except (OSError, json.JSONDecodeError, ValueError):
        pass
    return "Apprentice Calls = 0/0 (healed=0)"


def _validate_loopback(url: str) -> str:
    raw = (url or DEFAULT_API_URL).strip().rstrip("/")
    parsed = urllib.parse.urlparse(raw)
    if parsed.scheme != "http" or (parsed.hostname or "").lower() not in LOOPBACK_HOSTS:
        raise ValueError(f"Non-loopback hook probe URL rejected: {url}")
    return raw


def _http_get_json(url: str, timeout_s: float) -> dict[str, Any]:
    req = urllib.request.Request(url, headers={"Accept": "application/json"}, method="GET")
    with urllib.request.urlopen(req, timeout=timeout_s) as resp:
        return json.loads(resp.read().decode("utf-8"))


def probe_bionic_state(
    api_url: str | None = None,
    *,
    model_id: str = DEFAULT_MODEL_ID,
    timeout_s: float = PROBE_TIMEOUT_S,
) -> dict[str, Any]:
    """Fast loopback state check returning ONLINE_READY, UNLOADED, or OFFLINE."""
    env_url = os.environ.get("BIONIC_HOOK_API_URL", "").strip()
    validated_v1 = _validate_loopback(api_url or env_url or DEFAULT_API_URL)
    root_url = validated_v1[:-3] if validated_v1.endswith("/v1") else validated_v1

    try:
        data = _http_get_json(f"{root_url}/api/v0/models", timeout_s=timeout_s)
        default_state = "not-loaded"
    except urllib.error.HTTPError as exc:
        if exc.code == 404:
            try:
                data = _http_get_json(f"{validated_v1}/models", timeout_s=timeout_s)
                default_state = "not-loaded"
            except Exception as inner_exc:
                return {"state": "OFFLINE", "loaded_context_length": None, "error": str(inner_exc)}
        else:
            return {"state": "OFFLINE", "loaded_context_length": None, "error": f"HTTP {exc.code}"}
    except Exception as exc:
        return {"state": "OFFLINE", "loaded_context_length": None, "error": str(exc)}

    for item in data.get("data") or []:
        if not isinstance(item, dict) or str(item.get("id") or "") != model_id:
            continue
        m_state = str(item.get("state") or default_state).lower()
        if m_state == "loaded":
            ctx_val = item.get("loaded_context_length")
            return {
                "state": "ONLINE_READY",
                "loaded_context_length": int(ctx_val) if ctx_val is not None else None,
                "error": None,
            }
    return {"state": "UNLOADED", "loaded_context_length": None, "error": None}


def _resolve_state_dir() -> Path:
    env_dir = (os.environ.get("APPRENTICE_HOOK_STATE_DIR", "") or os.environ.get("BIONIC_HOOK_STATE_DIR", "")).strip()
    if env_dir:
        return Path(os.path.expanduser(env_dir))
    plugin_data = os.environ.get("PLUGIN_DATA", "").strip()
    if plugin_data:
        return Path(os.path.expanduser(plugin_data)) / "hook_state"
    return Path.home() / ".cache" / "apprentice_plugin" / "hook_state"


def _state_file_path(conversation_id: str) -> Path:
    safe_id = re.sub(r"[^A-Za-z0-9_.-]+", "_", conversation_id or "default").strip("._")[:80] or "default"
    return _resolve_state_dir() / f"{safe_id}.json"


def _load_conv_state(conversation_id: str) -> dict[str, Any] | None:
    path = _state_file_path(conversation_id)
    try:
        if path.is_file():
            obj = json.loads(path.read_text(encoding="utf-8"))
            if isinstance(obj, dict):
                return obj
    except (OSError, json.JSONDecodeError):
        pass
    return None


def _save_conv_state(conversation_id: str, data: dict[str, Any]) -> None:
    path = _state_file_path(conversation_id)
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.parent.is_symlink() or path.is_symlink():
            return
        try:
            os.chmod(path.parent, 0o700)
        except OSError:
            pass
        flags = os.O_WRONLY | os.O_CREAT | os.O_TRUNC | getattr(os, "O_NOFOLLOW", 0)
        fd = os.open(path, flags, 0o600)
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            json.dump(data, fh, indent=2)
            fh.write("\n")
        try:
            os.chmod(path, 0o600)
        except OSError:
            pass
    except OSError:
        pass


def _build_system_step(sys_text: str) -> dict[str, Any]:
    return {"systemMessage": {"systemMessage": sys_text}}


def _parse_iso_utc(raw_ts: Any) -> datetime | None:
    if not isinstance(raw_ts, str) or not raw_ts.strip():
        return None
    try:
        dt = datetime.fromisoformat(raw_ts.strip())
    except ValueError:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def _validate_hook_response_schema(resp: dict[str, Any]) -> None:
    """Reject deprecated/panic-prone proto fields in SessionStart/PreInvocation responses."""
    if "terminationBehavior" in resp:
        raise ValueError("Forbidden hook field 'terminationBehavior' present")
    for step in resp.get("injectSteps") or []:
        if isinstance(step, dict) and isinstance(step.get("systemMessage"), dict):
            if "metadata" in step["systemMessage"]:
                raise ValueError("Forbidden systemMessage field 'metadata' present")


def evaluate_session_or_invocation(
    payload: dict[str, Any],
    *,
    api_url: str | None = None,
) -> dict[str, Any]:
    """Evaluate SessionStart or PreInvocation and return minimal camelCase injectSteps JSON."""
    event = str(payload.get("hookEventName") or "SessionStart")
    conv_id = str(payload.get("conversationId") or "default")
    last_user_input = str(payload.get("lastUserInput") or "")
    input_sha = hashlib.sha256(last_user_input.encode("utf-8")).hexdigest()[:16] if last_user_input else ""
    has_explicit_tag = bool(EXPLICIT_TAG_RE.search(last_user_input))
    now_utc = datetime.now(timezone.utc)

    prev = _load_conv_state(conv_id)
    if event == "SessionStart":
        _save_conv_state(
            conv_id,
            {
                "state": prev.get("state") if prev else None,
                "loaded_context_length": prev.get("loaded_context_length") if prev else None,
                "pending_turn1_notice": True,
                "last_event": "SessionStart",
                "last_user_input_sha": prev.get("last_user_input_sha", "") if prev else "",
                "updated_at": now_utc.isoformat(timespec="seconds"),
            },
        )
        return {}

    probe = probe_bionic_state(api_url=api_url)
    state = probe["state"]
    ctx = probe["loaded_context_length"]
    ctx_disp = str(ctx) if ctx is not None else "unknown"

    prev_state = prev.get("state") if prev else None
    prev_sha = prev.get("last_user_input_sha", "") if prev else ""
    pending_turn1 = bool(prev.get("pending_turn1_notice")) if prev else False
    prev_dt = _parse_iso_utc(prev.get("updated_at")) if prev else None
    idle_expired = bool(
        prev_dt is not None
        and input_sha != prev_sha
        and state != "ONLINE_READY"
        and (now_utc - prev_dt).total_seconds() >= IDLE_RENOTIFY_SECONDS
    )

    steps: list[dict[str, Any]] = []
    if prev is None or prev_state != state or pending_turn1 or idle_expired:
        if state == "OFFLINE":
            sys_msg = (
                "[MANDATORY USER-VISIBLE NOTICE FOR THIS TURN] "
                "BIONIC_STATE=OFFLINE (127.0.0.1:1234 unreachable, 0 GiB sidecar VRAM). "
                "In your final user-facing reply for this turn (skip only if running as an internal subagent without apprentice_control), "
                "you MUST include a visible callout at the top of your response:\n"
                '> **[APPRENTICE NOTICE]** Local Bionic (`Qwen3.6-35B-A3B`) is currently **OFFLINE** (`127.0.0.1:1234` stopped, `0 GiB` VRAM). '
                'Reply **"turn on Bionic"** (`gpu-daily`, 49k ctx) or **"turn on Bionic cpu-bg"** if you would like me to start it remotely for you.\n'
                "(If calling exit_plan_mode, carry this mandatory notice into the plan's final user response.) "
                "Never auto-start Bionic without explicit user confirmation (user_confirmed=True), even if [bionic]/[local] appears on Turn 1, "
                "and never call 127.0.0.1:1234, AppImage, or lms directly."
            )
            steps.append(_build_system_step(sys_msg))
        elif state == "UNLOADED":
            sys_msg = (
                "[MANDATORY USER-VISIBLE NOTICE FOR THIS TURN] "
                "BIONIC_STATE=UNLOADED (127.0.0.1:1234 server running, qwen3.6-35b-a3b not loaded — 0 GiB model VRAM). "
                "In your final user-facing reply for this turn (skip only if running as an internal subagent without apprentice_control), "
                "you MUST include a visible callout at the top of your response:\n"
                '> **[APPRENTICE NOTICE]** Local Bionic (`Qwen3.6-35B-A3B`) is currently **UNLOADED** (`127.0.0.1:1234` up, `0 GiB` model VRAM). '
                'Reply **"turn on Bionic"** (`gpu-daily`, 49k ctx / ~10 GiB VRAM) or **"turn on Bionic cpu-bg"** if you would like me to load it remotely for you.\n'
                "(If calling exit_plan_mode, carry this mandatory notice into the plan's final user response.) "
                "Never auto-load Bionic without explicit user confirmation (user_confirmed=True), even if [bionic]/[local] appears on Turn 1, "
                "and never call 127.0.0.1:1234, AppImage, or lms directly."
            )
            steps.append(_build_system_step(sys_msg))
        elif prev_state in {"OFFLINE", "UNLOADED"}:
            sc_banner = _read_lifetime_scorecard_banner()
            sys_msg = (
                f"[APPRENTICE STATE TRANSITION] BIONIC_STATE=ONLINE_READY model={DEFAULT_MODEL_ID} ctx={ctx_disp} "
                f"auto_eta=60s explicit_eta=90s | {sc_banner}. Include a 1-line [APPRENTICE NOTICE] confirming Bionic is now "
                f"ONLINE READY (ctx={ctx_disp}, {sc_banner}) in this response. Offload bounded log/diff/file digests & scratch patches "
                "via apprentice MCP tools or apprentice_engine.py; never access 127.0.0.1:1234 or lms directly."
            )
            steps.append(_build_system_step(sys_msg))
        else:
            sc_banner = _read_lifetime_scorecard_banner()
            sys_msg = (
                f"BIONIC_STATE=ONLINE_READY model={DEFAULT_MODEL_ID} ctx={ctx_disp} auto_eta=60s explicit_eta=90s | {sc_banner}. "
                "Offload bounded digests & scratch patches via apprentice MCP tools or apprentice_engine.py; "
                f"never access 127.0.0.1:1234 or lms directly. Include [APPRENTICE NOTICE] ({sc_banner}) whenever Bionic is called."
            )
            steps.append(_build_system_step(sys_msg))
    elif has_explicit_tag and input_sha != prev_sha:
        sc_banner = _read_lifetime_scorecard_banner()
        if state == "ONLINE_READY":
            sys_msg = (
                f"[EXPLICIT APPRENTICE REQUEST] Bionic is ONLINE_READY (ctx={ctx_disp}, {sc_banner}). Use apprentice MCP tools "
                "with invocation_tier='explicit' (90s ETA cap), treat outputs as quarantined drafts, and include "
                f"[APPRENTICE NOTICE] ({sc_banner})."
            )
        else:
            sys_msg = (
                f"[EXPLICIT APPRENTICE REQUEST] Bionic is currently {state}. Inform the user and ask confirmation "
                "before calling apprentice_control(user_confirmed=True)."
            )
        steps.append(_build_system_step(sys_msg))

    _save_conv_state(
        conv_id,
        {
            "state": state,
            "loaded_context_length": ctx,
            "pending_turn1_notice": False,
            "last_event": event,
            "last_user_input_sha": input_sha,
            "updated_at": now_utc.isoformat(timespec="seconds"),
        },
    )

    if not steps:
        return {}
    return {"injectSteps": steps}


def _has_unquoted_shell_chain(cmd: str) -> bool:
    """Detect unquoted shell operators (; && || | $( ` newline) outside '...' or "..."."""
    in_single = False
    in_double = False
    escaped = False
    n = len(cmd)
    i = 0
    while i < n:
        ch = cmd[i]
        if escaped:
            escaped = False
            i += 1
            continue
        if in_single:
            if ch == "'":
                in_single = False
            i += 1
            continue
        if in_double:
            if ch == "\\":
                escaped = True
            elif ch == '"':
                in_double = False
            elif ch == "`" or (ch == "$" and i + 1 < n and cmd[i + 1] == "("):
                return True
            i += 1
            continue
        if ch == "\\":
            escaped = True
        elif ch == "'":
            in_single = True
        elif ch == '"':
            in_double = True
        elif ch in {";", "|", "&", "<", ">", "`", "\n", "\r"}:
            return True
        elif ch == "$" and i + 1 < n and cmd[i + 1] == "(":
            return True
        i += 1
    return False


def _has_bionic_target(cmd: str) -> bool:
    return bool(
        PORT_1234_RE.search(cmd)
        or APPIMAGE_RE.search(cmd)
        or LMS_BIN_RE.search(cmd)
        or SIDECAR_SCRIPT_RE.search(cmd)
    )


def _is_within(child: Path, parent: Path) -> bool:
    try:
        child.relative_to(parent)
        return True
    except ValueError:
        return False


def _is_unsafe_env_assign(token: str) -> str | None:
    if not re.match(r"^[A-Za-z_][A-Za-z0-9_]*=.*", token):
        return None
    var_name = token.split("=", 1)[0].upper()
    if var_name.startswith(DANGEROUS_ENV_PREFIXES) or var_name in DANGEROUS_ENV_NAMES:
        return var_name
    return None


def _unwrap_command_tokens(tokens: list[str]) -> tuple[str, str, list[str], str | None]:
    """Unwrap safe CLI wrappers/env assignments while blocking unsafe PYTHON*/LD_* injections."""
    idx = 0
    n = len(tokens)
    saw_wrapper = False
    while idx < n:
        bad_env = _is_unsafe_env_assign(tokens[idx])
        if bad_env:
            return "", "", [], f"[APPRENTICE_UTILITY_REQUIRED] Unsafe environment override '{bad_env}=' blocked on Bionic/governed command."
        if re.match(r"^[A-Za-z_][A-Za-z0-9_]*=.*", tokens[idx]):
            idx += 1
            continue

        tok_orig = tokens[idx]
        exe = Path(tok_orig).name.lower()
        if exe not in WRAPPER_CMDS:
            return exe, tok_orig, tokens[idx + 1 :], None

        saw_wrapper = True
        idx += 1
        if exe == "env":
            while idx < n:
                tok = tokens[idx]
                if tok == "--":
                    idx += 1
                    break
                if (
                    tok in {"-S", "--split-string", "-i", "--ignore-environment"}
                    or tok.startswith(("-S", "--split-string=", "-i"))
                    or (tok.startswith("-") and not tok.startswith("--") and ("S" in tok[1:] or "i" in tok[1:]))
                ):
                    return "", "", [], "[APPRENTICE_UTILITY_REQUIRED] 'env -S'/'env -i' wrapper blocked on Bionic/governed command."
                if tok in {"-u", "--unset", "-C", "--chdir"}:
                    idx += 2
                    continue
                if tok.startswith(("--unset=", "--chdir=")) or tok in {"-0", "--null"}:
                    idx += 1
                    continue
                if tok.startswith("-"):
                    return "", "", [], f"[APPRENTICE_UTILITY_REQUIRED] Unsupported 'env' option '{tok}' blocked."
                bad_inner = _is_unsafe_env_assign(tok)
                if bad_inner:
                    return "", "", [], f"[APPRENTICE_UTILITY_REQUIRED] Unsafe 'env {bad_inner}=' blocked on Bionic/governed command."
                if re.match(r"^[A-Za-z_][A-Za-z0-9_]*=.*", tok):
                    idx += 1
                    continue
                break
        elif exe == "timeout":
            val_flags = {"-k", "--kill-after", "-s", "--signal"}
            while idx < n:
                tok = tokens[idx]
                if tok in val_flags:
                    idx += 2
                    continue
                if tok.startswith(("--kill-after=", "--signal=", "-k", "-s")) or tok in {
                    "--preserve-status",
                    "--foreground",
                    "-v",
                    "--verbose",
                }:
                    idx += 1
                    continue
                if tok.startswith("-"):
                    return "", "", [], f"[APPRENTICE_UTILITY_REQUIRED] Unsupported 'timeout' option '{tok}' blocked."
                break
            if idx >= n or tokens[idx].startswith("-"):
                return "", "", [], "[APPRENTICE_UTILITY_REQUIRED] Incomplete 'timeout' wrapper blocked."
            idx += 1
        elif exe == "nice":
            if idx < n and tokens[idx] in {"-n", "--adjustment"}:
                idx += 2
            elif idx < n and (tokens[idx].startswith(("--adjustment=", "-n")) or re.match(r"^-\d+$", tokens[idx])):
                idx += 1
            elif idx < n and tokens[idx].startswith("-"):
                return "", "", [], f"[APPRENTICE_UTILITY_REQUIRED] Unsupported 'nice' option '{tokens[idx]}' blocked."
        elif exe == "stdbuf":
            while idx < n:
                tok = tokens[idx]
                if tok in {"-i", "--input", "-o", "--output", "-e", "--error"}:
                    idx += 2
                    continue
                if tok.startswith(("--input=", "--output=", "--error=", "-i", "-o", "-e")):
                    idx += 1
                    continue
                if tok.startswith("-"):
                    return "", "", [], f"[APPRENTICE_UTILITY_REQUIRED] Unsupported 'stdbuf' option '{tok}' blocked."
                break

    if idx < n:
        return Path(tokens[idx]).name.lower(), tokens[idx], tokens[idx + 1 :], None
    if saw_wrapper:
        return "", "", [], "[APPRENTICE_UTILITY_REQUIRED] Incomplete wrapper invocation on Bionic target blocked."
    return "", "", [], None


def _git_has_unsafe_exec_flags(rest: list[str]) -> bool:
    """Reject git flags capable of spawning external helpers (e.g., -c diff.external, --ext-diff)."""
    for tok in rest:
        if tok == "--":
            break
        if tok in {"-c", "--config-env", "--exec-path", "--ext-diff", "--upload-pack", "--receive-pack"}:
            return True
        if tok.startswith(("-c", "--config-env=", "--exec-path=", "--upload-pack=", "--receive-pack=")):
            return True
    return False


def _rg_has_unsafe_exec_flags(rest: list[str]) -> bool:
    """Reject ripgrep flags that invoke arbitrary preprocessors."""
    for tok in rest:
        if tok == "--":
            break
        if tok in {"--pre", "--pre-glob"} or tok.startswith(("--pre=", "--pre-glob=")):
            return True
    return False


def _git_subcommand(rest: list[str]) -> str:
    """Return the git subcommand skipping safe global options."""
    value_flags = {"-C", "--git-dir", "--work-tree", "--namespace", "--super-prefix"}
    i = 0
    n = len(rest)
    while i < n:
        tok = rest[i]
        if tok == "--":
            return rest[i + 1].lower() if i + 1 < n else ""
        if tok in value_flags:
            i += 2
            continue
        if tok.startswith("-"):
            i += 1
            continue
        return tok.lower()
    return ""


def _python_script_arg(rest: list[str]) -> str | None:
    """Return positional Python script path only when no -c/-m/- code execution flag is passed."""
    value_flags = {"-W", "-X", "--check-hash-based-pycs"}
    i = 0
    n = len(rest)
    while i < n:
        tok = rest[i]
        if tok == "--":
            return rest[i + 1] if i + 1 < n else None
        if tok == "-" or tok in {"-c", "-m"} or tok.startswith(("-c", "-m")):
            return None
        if tok.startswith("-") and not tok.startswith("--") and ("c" in tok[1:] or "m" in tok[1:]):
            return None
        if tok in value_flags:
            i += 2
            continue
        if tok.startswith("-"):
            i += 1
            continue
        return tok
    return None


def evaluate_pre_tool_use(payload: dict[str, Any]) -> dict[str, Any]:
    """Enforce governed sidecar utility usage whenever run_command touches Bionic/lms/:1234."""
    tool_call = payload.get("toolCall") or {}
    if str(tool_call.get("name") or "") != "run_command":
        return {"decision": "allow"}
    cmd = str(((tool_call.get("args") or {}).get("CommandLine")) or "").strip()
    if not cmd or not _has_bionic_target(cmd):
        return {"decision": "allow"}

    if _has_unquoted_shell_chain(cmd):
        return {
            "decision": "deny",
            "reason": (
                "[APPRENTICE_UTILITY_REQUIRED] Unchained single-command invocations only when referencing "
                "local backend/:1234/lms; use apprentice MCP tools or apprentice_engine.py directly."
            ),
        }

    try:
        tokens = shlex.split(cmd)
    except ValueError:
        return {
            "decision": "deny",
            "reason": "[APPRENTICE_UTILITY_REQUIRED] Unparseable shell quoting on local backend/:1234/lms command rejected.",
        }
    if not tokens:
        return {"decision": "allow"}

    exe_name, exe_token, rest, unwrap_err = _unwrap_command_tokens(tokens)
    if unwrap_err:
        return {"decision": "deny", "reason": unwrap_err}
    if not exe_name:
        return {"decision": "allow"}

    if exe_name in SAFE_READONLY_CMDS:
        if exe_name == "rg" and _rg_has_unsafe_exec_flags(rest):
            return {
                "decision": "deny",
                "reason": "[APPRENTICE_UTILITY_REQUIRED] 'rg --pre'/'--pre-glob' execution blocked on Bionic target.",
            }
        return {"decision": "allow"}

    if exe_name == "agy" and not PORT_1234_RE.search(cmd):
        return {"decision": "allow"}

    if exe_name == "git":
        if _git_has_unsafe_exec_flags(rest):
            return {
                "decision": "deny",
                "reason": "[APPRENTICE_UTILITY_REQUIRED] Unsafe git config/ext-diff/exec-path flags blocked.",
            }
        if _git_subcommand(rest) in GIT_SAFE_READONLY_SUBCMDS:
            return {"decision": "allow"}

    if re.match(r"^python(?:3(?:\.\d+)?)?$", exe_name):
        script_arg = _python_script_arg(rest)
        if script_arg:
            expanded = os.path.expanduser(script_arg)
            raw_cwd = str(payload.get("cwd") or "").strip()
            if raw_cwd:
                base_cwd = Path(os.path.expanduser(raw_cwd))
            else:
                try:
                    base_cwd = Path(os.getcwd())
                except OSError:
                    base_cwd = Path.home()
            if not base_cwd.is_absolute():
                base_cwd = Path.home() / base_cwd
            cand = Path(expanded) if Path(expanded).is_absolute() else (base_cwd / expanded)
            abs_p = Path(os.path.normpath(str(cand)))
            res_p = abs_p.resolve(strict=False)
            if (
                abs_p.name in GOVERNED_PY_SCRIPTS
                and res_p.name in GOVERNED_PY_SCRIPTS
                and any(
                    _is_within(abs_p, Path(os.path.normpath(str(r)))) or _is_within(abs_p, r.resolve(strict=False))
                    for r in TRUSTED_INVOCATION_ROOTS
                )
                and any(_is_within(res_p, r.resolve(strict=False)) for r in TRUSTED_SCRIPT_ROOTS)
            ):
                if res_p.name == "apprentice_engine.py":
                    return {
                        "decision": "allow",
                        "reason": "[APPRENTICE NOTICE] Governed execution via apprentice_engine.py.",
                    }
                return {"decision": "allow"}

    if APPIMAGE_RE.search(exe_token):
        return {
            "decision": "deny",
            "reason": (
                "[APPRENTICE_UTILITY_REQUIRED] Direct Bionic binary/AppImage execution is blocked; "
                "use apprentice_control / apprentice_engine.py control after user confirmation."
            ),
        }

    if exe_name in SHELL_WRAPPER_CMDS:
        return {
            "decision": "deny",
            "reason": (
                f"[APPRENTICE_UTILITY_REQUIRED] Subshell wrapper '{exe_name}' targeting local backend/:1234/lms is blocked; "
                "use apprentice MCP tools or apprentice_engine.py directly."
            ),
        }

    if exe_name == "lms":
        return {
            "decision": "deny",
            "reason": (
                "[APPRENTICE_UTILITY_REQUIRED] Direct 'lms' CLI invocation is blocked; "
                "use apprentice_control MCP tool or apprentice_engine.py control."
            ),
        }

    return {
        "decision": "deny",
        "reason": (
            "[APPRENTICE_UTILITY_REQUIRED] Direct access to 127.0.0.1:1234 or Bionic binaries is blocked; "
            "route calls through apprentice MCP tools or apprentice_engine.py."
        ),
    }


def dispatch_hook_payload(payload: dict[str, Any], *, api_url: str | None = None) -> dict[str, Any]:
    event = str(payload.get("hookEventName") or "")
    if event == "PreToolUse":
        return evaluate_pre_tool_use(payload)
    if event in {"SessionStart", "PreInvocation"}:
        return evaluate_session_or_invocation(payload, api_url=api_url)
    return {}


def _start_mock_models_server(is_loaded_fn: Any) -> http.server.HTTPServer:
    """Start an ephemeral localhost /api/v0/models HTTP server for offline tests/simulations."""

    class _MockModelsHandler(http.server.BaseHTTPRequestHandler):
        def do_GET(self) -> None:  # noqa: N802
            if self.path == "/api/v0/models":
                loaded_now = bool(is_loaded_fn())
                row = {
                    "id": DEFAULT_MODEL_ID,
                    "state": "loaded" if loaded_now else "not-loaded",
                    "loaded_context_length": 49152 if loaded_now else None,
                }
                body = json.dumps({"data": [row, {"id": "nomic-embed", "state": "loaded"}]}).encode("utf-8")
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

    srv = http.server.HTTPServer(("127.0.0.1", 0), _MockModelsHandler)
    th = threading.Thread(target=srv.serve_forever, daemon=True)
    th.start()
    return srv


def _simulate_event_cli(event: str, sim_state: str, *, pretty: bool) -> int:
    """Run SessionStart/PreInvocation against an ephemeral loopback mock in a temp state dir."""
    with tempfile.TemporaryDirectory() as td:
        old_state_dir = os.environ.get("BIONIC_HOOK_STATE_DIR")
        os.environ["BIONIC_HOOK_STATE_DIR"] = td
        try:
            payload = {
                "hookEventName": event,
                "conversationId": "sim-conv-1",
                "lastUserInput": "" if event == "SessionStart" else "simulate status check",
            }
            if sim_state == "OFFLINE":
                sock_srv = http.server.HTTPServer(("127.0.0.1", 0), http.server.BaseHTTPRequestHandler)
                closed_port = sock_srv.server_port
                sock_srv.server_close()
                out = dispatch_hook_payload(payload, api_url=f"http://127.0.0.1:{closed_port}/v1")
            else:
                loaded_flag = sim_state == "ONLINE_READY"
                srv = _start_mock_models_server(lambda: loaded_flag)
                try:
                    out = dispatch_hook_payload(payload, api_url=f"http://127.0.0.1:{srv.server_port}/v1")
                finally:
                    srv.shutdown()
                    srv.server_close()
        finally:
            if old_state_dir is None:
                os.environ.pop("BIONIC_HOOK_STATE_DIR", None)
            else:
                os.environ["BIONIC_HOOK_STATE_DIR"] = old_state_dir

    out_json = json.dumps(out, indent=2 if pretty else None)
    try:
        _validate_hook_response_schema(out)
        if '"metadata"' in out_json or '"terminationBehavior"' in out_json:
            raise ValueError("Forbidden key in serialized hook JSON stdout")
    except ValueError:
        print(out_json)
        return 2
    print(out_json)
    return 0


def run_self_tests() -> dict[str, Any]:
    """Deterministic self-tests for Turn-1 notices, state transitions, and PreToolUse enforcement."""
    checks: list[str] = []

    with tempfile.TemporaryDirectory() as td:
        old_state_dir = os.environ.get("BIONIC_HOOK_STATE_DIR")
        os.environ["BIONIC_HOOK_STATE_DIR"] = td
        try:
            # 1. OFFLINE notice deferred from SessionStart -> first PreInvocation (zero metadata/terminationBehavior)
            sock_srv = http.server.HTTPServer(("127.0.0.1", 0), http.server.BaseHTTPRequestHandler)
            closed_port = sock_srv.server_port
            sock_srv.server_close()
            closed_api = f"http://127.0.0.1:{closed_port}/v1"

            r_s0 = dispatch_hook_payload(
                {"hookEventName": "SessionStart", "conversationId": "conv-offline-1"},
                api_url=closed_api,
            )
            _validate_hook_response_schema(r_s0)
            assert r_s0 == {}, f"Expected empty SessionStart response, got {r_s0}"

            r_off = dispatch_hook_payload(
                {"hookEventName": "PreInvocation", "conversationId": "conv-offline-1", "lastUserInput": "hello"},
                api_url=closed_api,
            )
            _validate_hook_response_schema(r_off)
            steps_off = r_off.get("injectSteps") or []
            assert len(steps_off) == 1
            msg_off = steps_off[0]["systemMessage"]["systemMessage"]
            assert "[MANDATORY USER-VISIBLE NOTICE FOR THIS TURN]" in msg_off
            assert "BIONIC_STATE=OFFLINE" in msg_off
            checks.append("session_start_defers_to_pre_invocation_offline_notice")

            # Steady-state repeat turn returns {}
            r_steady = dispatch_hook_payload(
                {"hookEventName": "PreInvocation", "conversationId": "conv-offline-1", "lastUserInput": "hello again"},
                api_url=closed_api,
            )
            assert r_steady == {}
            checks.append("steady_state_zero_token_silence")

            # Idle expiry >= IDLE_RENOTIFY_SECONDS re-emits notice on new prompt while not ONLINE_READY
            st_path = _state_file_path("conv-offline-1")
            st_obj = json.loads(st_path.read_text(encoding="utf-8"))
            st_obj["updated_at"] = (datetime.now(timezone.utc) - timedelta(seconds=IDLE_RENOTIFY_SECONDS + 300)).isoformat(
                timespec="seconds"
            )
            st_path.write_text(json.dumps(st_obj), encoding="utf-8")
            r_idle = dispatch_hook_payload(
                {"hookEventName": "PreInvocation", "conversationId": "conv-offline-1", "lastUserInput": "back after break"},
                api_url=closed_api,
            )
            _validate_hook_response_schema(r_idle)
            assert "BIONIC_STATE=OFFLINE" in r_idle["injectSteps"][0]["systemMessage"]["systemMessage"]
            checks.append("idle_expiry_renotifies_offline_and_unloaded")

            # 2. Ephemeral HTTP server testing UNLOADED -> ONLINE_READY transition + [bionic] tag
            mode_box = {"loaded": False}
            srv = _start_mock_models_server(lambda: mode_box["loaded"])
            try:
                live_api = f"http://127.0.0.1:{srv.server_port}/v1"
                # Resumed remote Web App session sees UNLOADED on PreInvocation
                r_unl = dispatch_hook_payload(
                    {"hookEventName": "PreInvocation", "conversationId": "conv-webapp-2", "lastUserInput": "check status"},
                    api_url=live_api,
                )
                _validate_hook_response_schema(r_unl)
                msg_unl = r_unl["injectSteps"][0]["systemMessage"]["systemMessage"]
                assert "[MANDATORY USER-VISIBLE NOTICE FOR THIS TURN]" in msg_unl
                assert "BIONIC_STATE=UNLOADED" in msg_unl
                checks.append("resumed_webapp_unloaded_notice_no_metadata")

                # State transition UNLOADED -> ONLINE_READY
                mode_box["loaded"] = True
                r_up = dispatch_hook_payload(
                    {"hookEventName": "PreInvocation", "conversationId": "conv-webapp-2", "lastUserInput": "now check"},
                    api_url=live_api,
                )
                _validate_hook_response_schema(r_up)
                msg_up = r_up["injectSteps"][0]["systemMessage"]["systemMessage"]
                assert "BIONIC_STATE=ONLINE_READY" in msg_up
                assert "ctx=49152" in msg_up
                assert "[APPRENTICE NOTICE]" in msg_up
                checks.append("state_flip_unloaded_to_online_ready")

                # Explicit [bionic] tag on steady ONLINE_READY injects reminder once per input
                r_tag = dispatch_hook_payload(
                    {"hookEventName": "PreInvocation", "conversationId": "conv-webapp-2", "lastUserInput": "[bionic] summarize log"},
                    api_url=live_api,
                )
                _validate_hook_response_schema(r_tag)
                assert "EXPLICIT APPRENTICE REQUEST" in r_tag["injectSteps"][0]["systemMessage"]["systemMessage"]
                r_tag_repeat = dispatch_hook_payload(
                    {"hookEventName": "PreInvocation", "conversationId": "conv-webapp-2", "lastUserInput": "[bionic] summarize log"},
                    api_url=live_api,
                )
                assert r_tag_repeat == {}
                checks.append("explicit_bionic_tag_single_turn_hint")

                # Turn-1 SessionStart -> PreInvocation(invocationNum=1) -> tool loop inv 2 -> next turn
                mode_box["loaded"] = False
                r_s1 = dispatch_hook_payload(
                    {"hookEventName": "SessionStart", "conversationId": "conv-dedup-3", "lastUserInput": ""},
                    api_url=live_api,
                )
                _validate_hook_response_schema(r_s1)
                assert r_s1 == {}
                r_p1 = dispatch_hook_payload(
                    {
                        "hookEventName": "PreInvocation",
                        "conversationId": "conv-dedup-3",
                        "invocationNum": 1,
                        "lastUserInput": "[bionic] check repo",
                    },
                    api_url=live_api,
                )
                _validate_hook_response_schema(r_p1)
                assert "BIONIC_STATE=UNLOADED" in r_p1["injectSteps"][0]["systemMessage"]["systemMessage"]
                r_p1_loop = dispatch_hook_payload(
                    {
                        "hookEventName": "PreInvocation",
                        "conversationId": "conv-dedup-3",
                        "invocationNum": 2,
                        "lastUserInput": "[bionic] check repo",
                    },
                    api_url=live_api,
                )
                assert r_p1_loop == {}, f"Expected intra-turn dedup {{}}, got {r_p1_loop}"
                r_p2 = dispatch_hook_payload(
                    {
                        "hookEventName": "PreInvocation",
                        "conversationId": "conv-dedup-3",
                        "invocationNum": 3,
                        "lastUserInput": "[bionic] check repo again",
                    },
                    api_url=live_api,
                )
                _validate_hook_response_schema(r_p2)
                assert "EXPLICIT APPRENTICE REQUEST" in r_p2["injectSteps"][0]["systemMessage"]["systemMessage"]
                checks.append("turn1_session_start_pre_invocation_dedup")

                # Resumed SessionStart on UNLOADED schedules notice for next PreInvocation
                r_s2 = dispatch_hook_payload(
                    {"hookEventName": "SessionStart", "conversationId": "conv-dedup-3", "lastUserInput": ""},
                    api_url=live_api,
                )
                assert r_s2 == {}
                r_p3 = dispatch_hook_payload(
                    {"hookEventName": "PreInvocation", "conversationId": "conv-dedup-3", "lastUserInput": "resume check"},
                    api_url=live_api,
                )
                _validate_hook_response_schema(r_p3)
                assert "BIONIC_STATE=UNLOADED" in r_p3["injectSteps"][0]["systemMessage"]["systemMessage"]
            finally:
                srv.shutdown()
                srv.server_close()

            # 2b. /v1/models 404 fallback must fail closed as UNLOADED
            class _V1OnlyHandler(http.server.BaseHTTPRequestHandler):
                def do_GET(self) -> None:  # noqa: N802
                    if self.path == "/v1/models":
                        body = json.dumps({"data": [{"id": DEFAULT_MODEL_ID}]}).encode("utf-8")
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

            srv_v1 = http.server.HTTPServer(("127.0.0.1", 0), _V1OnlyHandler)
            th_v1 = threading.Thread(target=srv_v1.serve_forever, daemon=True)
            th_v1.start()
            try:
                v1_probe = probe_bionic_state(api_url=f"http://127.0.0.1:{srv_v1.server_port}/v1")
                assert v1_probe["state"] == "UNLOADED", f"Expected UNLOADED on /v1/models fallback, got {v1_probe}"
            finally:
                srv_v1.shutdown()
                srv_v1.server_close()
            checks.append("resumed_session_start_re_emits_and_v1_models_fail_closed")

            # 3. PreToolUse enforcement vectors & spoof defense
            deny_vectors = [
                "curl -s http://127.0.0.1:1234/v1/models",
                "curl -s http://127.0.0.1:01234/v1/models",
                "/home/orin/.lmstudio/LM-Studio-Bionic-current.AppImage --ozone-platform-hint=auto",
                "timeout 30 /home/orin/.lmstudio/LM-Studio-Bionic-current.AppImage --headless",
                "python3 /home/orin/Projects/Engineering/scripts/apprentice_engine.py status && curl http://localhost:1234/v1/models",
                "python3 /home/orin/Projects/Engineering/scripts/apprentice_engine.py status & curl http://127.0.0.1:1234/v1/models",
                "bash -c 'cat </dev/tcp/127.0.0.1/1234'",
                "/home/orin/.lmstudio/bin/lms load qwen3.6-35b-a3b -y",
            ]
            spoof_deny_vectors = [
                "python3 -c \"import urllib.request; urllib.request.urlopen('http://127.0.0.1:1234/v1/models')\" # /apprentice_engine.py",
                "python3 -c'import urllib.request' # 127.0.0.1:1234",
                "python3 -c \"connect(('127.0.0.1', 1234))\"",
                "python3 -c \"import urllib.request; urllib.request.urlopen('http://127.0.0.1:1234/v1/models')\"",
                "python3 -Bc \"print(1)\" http://127.0.0.1:1234",
                "bash -c 'lms daemon status'",
                "sh -c \"/home/orin/.lmstudio/bin/lms ps\"",
                "curl -s http://2130706433:1234/v1/models",
                "curl -s http://0x7f000001:1234/v1/models",
                "curl -s http://127.0.0.1:0x4d2/v1/models",
                "python3 /tmp/apprentice_engine.py status",
                "PYTHONPATH=/tmp python3 /home/orin/Projects/Engineering/scripts/apprentice_engine.py status",
                "env PYTHONPATH=/tmp python3 /home/orin/Projects/Engineering/scripts/apprentice_engine.py status",
                "env -S 'curl http://127.0.0.1:1234/v1/models'",
                "nc 127.0.0.1 1234",
                "nc 127.0.0.2 -p 8888 1234",
                "/home/orin/.lmstudio/bin/lms ps",
                "/home/orin/.lmstudio/apps/bionic/lm-studio",
                "git clone http://127.0.0.1:1234/repo /tmp/x",
                "git -C /home/orin/Projects/Engineering -c diff.external=/tmp/evil.sh diff 127.0.0.1:1234",
                "git --exec-path=/tmp status 127.0.0.1:1234",
                "rg --pre sh -e 127.0.0.1:1234 /home/orin/Projects/Engineering/scripts/apprentice_engine.py",
            ]
            for dcmd in deny_vectors + spoof_deny_vectors:
                d_res = evaluate_pre_tool_use({"toolCall": {"name": "run_command", "args": {"CommandLine": dcmd}}})
                assert d_res["decision"] == "deny", f"Expected deny on {dcmd}"

            allow_vectors = [
                "python3 /home/orin/Projects/Engineering/scripts/apprentice_engine.py status --json",
                "python3 -B /home/orin/Projects/Engineering/scripts/apprentice_engine.py control status --json",
                "python3 -B /home/orin/Projects/Engineering/scripts/benchmark_apprentice.py --self-test --json",
                "timeout 30 python3 /home/orin/Projects/Engineering/scripts/apprentice_engine.py status --json",
                "nice -n 10 python3 /home/orin/Projects/Engineering/scripts/apprentice_engine.py status --json",
                "grep 127.0.0.1:1234 /home/orin/Projects/Engineering/scripts/apprentice_engine.py",
                "cat /home/orin/Projects/Engineering/scripts/apprentice_engine.py",
                "pytest test.py:1234",
                "git -C /home/orin/Projects/Engineering status --short",
                "git -C /home/orin/Projects/Engineering log -n 1 --grep 127.0.0.1:1234",
                "git -C /home/orin/Projects/Engineering add /home/orin/Projects/Engineering/scripts/apprentice_engine.py",
            ]
            for acmd in allow_vectors:
                a_res = evaluate_pre_tool_use({"toolCall": {"name": "run_command", "args": {"CommandLine": acmd}}})
                assert a_res["decision"] == "allow", f"Expected allow on {acmd}"
            checks.append("pre_tool_use_bypass_enforcement")
            checks.append("python_flag_and_trusted_root_spoof_defense")
            checks.append("wrapper_env_rg_git_and_port_evasion_defense")

            # 4. Lifetime scorecard banner in ONLINE_READY PreInvocation with zero forbidden schema keys
            tel_tmp = Path(td) / "tel.jsonl"
            old_tel = os.environ.get("BIONIC_SIDECAR_TELEMETRY_LOG")
            os.environ["BIONIC_SIDECAR_TELEMETRY_LOG"] = str(tel_tmp)
            try:
                tel_tmp.write_text(
                    json.dumps({"cmd": "query", "finish_reason": "stop", "elapsed_s": 1.2}) + "\n",
                    encoding="utf-8",
                )
                class _ReadyHandler(http.server.BaseHTTPRequestHandler):
                    def do_GET(self) -> None:  # noqa: N802
                        body = json.dumps({"data": [{"id": DEFAULT_MODEL_ID, "state": "loaded", "loaded_context_length": 57344}]}).encode("utf-8")
                        self.send_response(200)
                        self.send_header("Content-Type", "application/json")
                        self.send_header("Content-Length", str(len(body)))
                        self.end_headers()
                        self.wfile.write(body)

                    def log_message(self, _fmt: str, *_args: Any) -> None:
                        return

                srv_on = http.server.HTTPServer(("127.0.0.1", 0), _ReadyHandler)
                th_on = threading.Thread(target=srv_on.serve_forever, daemon=True)
                th_on.start()
                try:
                    out_on = evaluate_session_or_invocation(
                        {
                            "hookEventName": "PreInvocation",
                            "conversationId": "conv-scorecard",
                            "lastUserInput": "hello",
                        },
                        api_url=f"http://127.0.0.1:{srv_on.server_port}/v1",
                    )
                    _validate_hook_response_schema(out_on)
                    msg = out_on["injectSteps"][0]["systemMessage"]["systemMessage"]
                    assert "Apprentice Calls = 1/0 (healed=0)" in msg, f"missing scorecard banner: {msg}"
                finally:
                    srv_on.shutdown()
                    srv_on.server_close()
            finally:
                if old_tel is None:
                    os.environ.pop("BIONIC_SIDECAR_TELEMETRY_LOG", None)
                else:
                    os.environ["BIONIC_SIDECAR_TELEMETRY_LOG"] = old_tel
            checks.append("online_ready_scorecard_banner")

            # 13. Symlinked ~/.gemini/config governed scripts allowed; /tmp symlink spoofs denied
            gemini_sync = Path("/home/orin/.gemini/config/skills/project-memory/scripts/sync_memory.py")
            if gemini_sync.exists() and any(
                _is_within(gemini_sync.resolve(strict=False), r.resolve(strict=False)) for r in TRUSTED_SCRIPT_ROOTS
            ):
                g_res = evaluate_pre_tool_use(
                    {
                        "toolCall": {
                            "name": "run_command",
                            "args": {"CommandLine": f"python3 -B {gemini_sync} --audit --files apprentice_engine.py"},
                        }
                    }
                )
                assert g_res["decision"] == "allow", f"Expected allow on symlinked skill script: {g_res}"
            tmp_link = Path(td) / "sync_memory.py"
            real_sync = Path("/home/orin/Projects/Alchemical3D/Homunculus/skills/project-memory/scripts/sync_memory.py")
            if real_sync.exists():
                tmp_link.symlink_to(real_sync)
                s_res = evaluate_pre_tool_use(
                    {
                        "toolCall": {
                            "name": "run_command",
                            "args": {"CommandLine": f"python3 -B {tmp_link} --audit --files apprentice_engine.py"},
                        }
                    }
                )
                assert s_res["decision"] == "deny", f"Expected deny on /tmp symlink spoof: {s_res}"
            checks.append("symlinked_gemini_config_governed_scripts_allowed_tmp_denied")
        finally:
            if old_state_dir is None:
                os.environ.pop("BIONIC_HOOK_STATE_DIR", None)
            else:
                os.environ["BIONIC_HOOK_STATE_DIR"] = old_state_dir

    return {"schema_version": "APPRENTICE_HOOK_V1", "status": "PASS", "tests_run": len(checks), "checks": checks}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Antigravity Lifecycle Hook for LM Studio Bionic Sidecar")
    parser.add_argument("--self-test", action="store_true", help="Run deterministic offline hook self-tests")
    parser.add_argument("--check-command", default=None, help="Evaluate PreToolUse decision on a synthetic run_command string")
    parser.add_argument(
        "--simulate-event",
        choices=["SessionStart", "PreInvocation"],
        default=None,
        help="Simulate SessionStart/PreInvocation offline with an ephemeral loopback server and temp state dir",
    )
    parser.add_argument(
        "--simulate-state",
        choices=["OFFLINE", "UNLOADED", "ONLINE_READY"],
        default="UNLOADED",
        help="Simulated Bionic server state used with --simulate-event",
    )
    parser.add_argument("--json", action="store_true", help="Emit indented JSON output for CLI checks")
    args = parser.parse_args(argv)

    if args.self_test:
        try:
            res = run_self_tests()
        except Exception as exc:
            err_payload = {"schema_version": "APPRENTICE_HOOK_V1", "status": "FAIL", "error": str(exc)}
            print(json.dumps(err_payload, indent=2) if args.json else f"[FAIL] {exc}", file=sys.stderr)
            return 2
        print(json.dumps(res, indent=2) if args.json else f"[PASS] {res['tests_run']} hook tests passed")
        return 0

    if args.simulate_event is not None:
        return _simulate_event_cli(args.simulate_event, args.simulate_state, pretty=args.json)

    if args.check_command is not None:
        decision = evaluate_pre_tool_use({"toolCall": {"name": "run_command", "args": {"CommandLine": args.check_command}}})
        print(json.dumps(decision, indent=2))
        return 2 if decision.get("decision") == "deny" else 0

    raw_stdin = sys.stdin.read().strip()
    if not raw_stdin:
        print("{}")
        return 0
    try:
        payload = json.loads(raw_stdin)
    except json.JSONDecodeError:
        print("{}")
        return 0

    event = str(payload.get("hookEventName") or "")
    try:
        out = dispatch_hook_payload(payload)
    except Exception as exc:
        if event == "PreToolUse":
            out = {"decision": "deny", "reason": f"[APPRENTICE_UTILITY_REQUIRED] Hook internal error: {exc}"}
        else:
            out = {}
    print(json.dumps(out))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
