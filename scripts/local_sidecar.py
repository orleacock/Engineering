#!/usr/bin/env python3
"""
Homunculus LM Studio Bionic Local Sidecar Bridge (`local_sidecar.py`).

Parent-only workstation sidecar harness (strictly outside clean-room `Homunculus`).
Routes vetted, bounded local tasks to LM Studio Bionic (`Qwen3.6-35B-A3B`) over
loopback HTTP (`127.0.0.1:1234/v1`) while enforcing:
  1. Fail-closed loopback URL, secret/NetCom/OAuth, `ZERO_ADHOC_CAD_PARSING`, and
     single-repo (`4C`) path firewalls BEFORE reading or transmitting bytes.
  2. Calibrated Plain-English ETA Circuit Breaker (`60s` auto / `90s` explicit) so heavy
     or multi-turn workloads automatically hand back to the main Antigravity thread.
  3. Quarantined doc routing strictly via `Homunculus/scripts/memory_gateway.py`
     (`MEMORY_SDK_V1`) and isolated scratch code staging (`py_compile` + unified diff).

Pure Python 3.10+ standard library (zero third-party packages).

=== DEVELOPER & AI NAVIGATION MAP ===
  Owning Module : Workstation Operations (`scripts/local_sidecar.py`)
  Callers       : Antigravity main thread, `bionic_mcp_server.py`, `sandbox_runner.py`
  Callees       : Stdlib + `lms` CLI + `Homunculus/scripts/memory_gateway.py`
  Contract      : `scripts/script_contracts.json` [`local_sidecar.py`]
  CLI Flags     : --api-url, --model, --system-prompt, --json, --self-test, --prompt-tokens, --homunculus-root, --memory-root, --project, --name, --title, --reason, --overwrite, --staging-dir, --target-filename, --compare-against, action, --profile, --user-confirmed, --dry-run, --mode, --invocation-tier, --prompt, --prompt-file, --context-file, --repo, --include-git-diff, --max-tokens, --max-eta-seconds, --expected-turns, --force-slow
                  status, check-eta, query, audit-to-quarantine, stage-code, control, self-test
  Symbol Index  (jump directly via read_file StartLine/EndLine):
    - class SidecarFirewallError (#L182-L183)        | class SidecarEtaTrippedError (#L186-L191)
    - def load_system_prompt (#L194-L203)            | def validate_loopback_url (#L206-L234)
    - def _safe_subprocess_cwd (#L237-L260)          | def _safe_abspath (#L263-L269)
    - def _is_path_within (#L272-L277)               | def _inspect_path_security (#L280-L310)
    - def validate_input_paths (#L313-L343)          | def validate_staging_dir (#L346-L409)
    - def estimate_eta (#L412-L475)                  | def _http_json_request (#L478-L498)
    - def assemble_prompt_payload (#L501-L546)       | def resolve_default_api_url (#L549-L551)
    - def invoke_chat_completion (#L554-L604)        | def extract_staged_code (#L607-L611)
    - def _read_prompt_arg (#L614-L621)              | def resolve_max_eta_seconds (#L624-L630)
    - def _resolve_telemetry_log (#L633-L639)        | def record_usage_telemetry (#L642-L663)
    - def summarize_usage_telemetry (#L666-L696)     | def probe_server_models (#L699-L765)
    - def preflight_live_inference (#L768-L782)      | def _enforce_eta_or_raise (#L785-L825)
    - def cmd_status (#L828-L861)                    | def cmd_check_eta (#L864-L907)
    - def cmd_query (#L910-L996)                     | def cmd_audit_to_quarantine (#L999-L1140)
    - def _write_private_staging_file (#L1143-L1152) | def stage_code_artifact (#L1155-L1229)
    - def cmd_stage_code (#L1232-L1322)              | def build_concrete_model_config (#L1331-L1388)
    - def _read_hw_counters (#L1391-L1411)           | def _probe_lms_daemon (#L1414-L1431)
    - def _run_lms_cmd (#L1434-L1444)                | def _has_gui_display_socket (#L1447-L1457)
    - def _control_plan (#L1460-L1490)               | def _control_status (#L1493-L1505)
    - def _control_load (#L1508-L1552)               | def _control_start_headless (#L1555-L1603)
    - def _control_unload (#L1606-L1625)             | def _control_stop_server (#L1628-L1639)
    - def _normalize_control_cli_action (#L1642-L1645) | def cmd_control (#L1648-L1692)
    - def run_self_tests (#L1695-L2043)              | def build_parser (#L2046-L2114)
    - def main (#L2117-L2149)
=== END NAVIGATION MAP ===
"""
from __future__ import annotations

import argparse
import difflib
import http.server
import json
import math
import os
import re
import subprocess
import sys
import tempfile
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SCHEMA_VERSION = "LOCAL_SIDECAR_V1"
DEFAULT_API_URL = "http://127.0.0.1:1234/v1"
DEFAULT_MODEL_ID = "qwen3.6-35b-a3b"
AUTO_MAX_ETA_SECONDS = 60.0
DEFAULT_MAX_ETA_SECONDS = 90.0
DEFAULT_SYSTEM_PROMPT_PATH = Path("/home/orin/.lmstudio/homunculus_sidecar_system_prompt.md")
DEFAULT_HOMUNCULUS_ROOT = Path("/home/orin/Projects/Alchemical3D/Homunculus")
DEFAULT_MEMORY_ROOT = Path("/home/orin/Projects/Engineering/memory")
DEFAULT_STAGING_DIR = Path("/tmp/homunculus_sidecar_staging")
DEFAULT_LMS_BIN = Path("/home/orin/.lmstudio/bin/lms")
DEFAULT_APPIMAGE_PATH = Path("/home/orin/.lmstudio/LM-Studio-Bionic-current.AppImage")
DEFAULT_CONCRETE_CFG_PATH = Path(
    "/home/orin/.lmstudio/apps/bionic/.internal/user-concrete-model-default-config/"
    "lmstudio-community/Qwen3.6-35B-A3B-GGUF/Qwen3.6-35B-A3B-Q4_K_M.gguf.json"
)
DEFAULT_TELEMETRY_LOG = Path.home() / ".cache" / "homunculus_bionic_plugin" / "sidecar_usage_telemetry.jsonl"
VRAM_USED_SYSFS = Path("/sys/class/drm/card1/device/mem_info_vram_used")
PROC_MEMINFO_PATH = Path("/proc/meminfo")

EXIT_SECURITY_FIREWALL = 2
EXIT_RUNTIME_ERROR = 3
EXIT_ETA_TRIPPED = 4

LOOPBACK_HOSTS = frozenset({"127.0.0.1", "localhost", "::1"})

FALLBACK_SYSTEM_PROMPT = (
    "You are the Homunculus local workstation sidecar (Qwen3.6-35B-A3B). "
    "Priority: 1. Accuracy & Truth > 2. Efficiency -> 3. Data Safety > 4. Speed. "
    "Cite relative path#Lstart-Lend verbatim for every factual claim, emit [TBD: <var>] "
    "instead of guessing, preserve units on [CALC: ...], never read or parse .step/.stl/.3mf "
    "(ZERO_ADHOC_CAD_PARSING), never touch secrets or NetCom, and treat all outputs as "
    "quarantined drafts for main-thread verification."
)

# Calibrated from Phase 3 empirical telemetry (phase3_metrics.jsonl / bionic_ab_bench.md)
PROFILES: dict[str, dict[str, Any]] = {
    "fast": {
        "preset": "Qwen3.6-35B-Fast-Sweep",
        "pp_tok_s": 890.0,
        "tg_tok_s": 38.0,
        "max_ctx": 49152,
        "prompt_cap": 40960,
        "reasoning_effort": "none",
        "default_max_tokens": 1200,
        "thinking_overhead_tokens": 0,
    },
    "deep": {
        "preset": "Qwen3.6-35B-Deep-Diff",
        "pp_tok_s": 890.0,
        "tg_tok_s": 35.0,
        "max_ctx": 49152,
        "prompt_cap": 40960,
        "reasoning_effort": "high",
        "default_max_tokens": 2048,
        "thinking_overhead_tokens": 800,
    },
    "cpu-bg": {
        "preset": "Qwen3.6-35B-CPU-Background",
        "pp_tok_s": 98.0,
        "tg_tok_s": 17.4,
        "max_ctx": 16384,
        "prompt_cap": 8192,
        "reasoning_effort": "none",
        "default_max_tokens": 600,
        "thinking_overhead_tokens": 0,
    },
}

FORBIDDEN_DIR_SEGMENTS = frozenset(
    {
        ".ssh",
        "credentials",
        "gmail_mcp",
        "netcom",
        "nea_v2",
        "corpus_inbox",
    }
)

FORBIDDEN_CAD_EXTENSIONS = frozenset(
    {
        ".step",
        ".stp",
        ".stl",
        ".3mf",
        ".iges",
        ".igs",
        ".fcstd",
    }
)

PRIVATE_KEY_PREFIXES = ("id_rsa", "id_ed25519", "id_ecdsa", "id_dsa", "id_xmss")
SECRET_EXTENSIONS = frozenset({".pem", ".key", ".p12", ".pfx", ".kdbx"})
SECRET_JSON_MARKERS = (
    "secret",
    "oauth",
    "token",
    "lmstudio-hub",
    "local-identity",
    "credentials",
    "mcp_config",
    "lms-key",
    "cloud-account",
)
SECRET_FILENAMES = frozenset({"lms-key-2", ".netrc", "_netrc", ".git-credentials", ".npmrc", ".pypirc"})
SECRET_TEXT_EXTENSIONS = frozenset({".json", ".yaml", ".yml", ".toml", ".ini", ".cfg", ".conf", ".txt"})

FENCED_CODE_RE = re.compile(r"```(?:[a-zA-Z0-9_+-]*)\n(.*?)```", re.DOTALL)


class SidecarFirewallError(Exception):
    """Raised when loopback, secret, CAD, repo, or staging containment blocks an action."""


class SidecarEtaTrippedError(Exception):
    """Raised when the calibrated ETA circuit breaker hands work back to the main thread."""

    def __init__(self, message: str, estimate: dict[str, Any]) -> None:
        super().__init__(message)
        self.estimate = estimate


def load_system_prompt(prompt_path: Path = DEFAULT_SYSTEM_PROMPT_PATH) -> tuple[str, str]:
    """Load the compact Homunculus sidecar constitution, falling back if sandbox-hidden."""
    try:
        if prompt_path.is_file():
            text = prompt_path.read_text(encoding="utf-8").strip()
            if text:
                return text, str(prompt_path)
    except OSError:
        pass
    return FALLBACK_SYSTEM_PROMPT, "embedded_fallback"


def validate_loopback_url(api_url: str) -> str:
    """Enforce strictly local loopback HTTP endpoints with no embedded credentials."""
    raw = api_url.strip().rstrip("/")
    parsed = urllib.parse.urlparse(raw)
    if parsed.scheme != "http":
        raise SidecarFirewallError(
            f"[SECURITY_FIREWALL_BLOCKED] Non-http scheme rejected (loopback http only): {api_url}"
        )
    if parsed.username is not None or parsed.password is not None:
        raise SidecarFirewallError(
            f"[SECURITY_FIREWALL_BLOCKED] URL credentials rejected: {api_url}"
        )
    host = (parsed.hostname or "").lower()
    if host not in LOOPBACK_HOSTS:
        raise SidecarFirewallError(
            f"[SECURITY_FIREWALL_BLOCKED] Non-loopback API host '{host}' rejected; only 127.0.0.1/localhost/::1 permitted."
        )
    try:
        port = parsed.port
    except ValueError as exc:
        raise SidecarFirewallError(
            f"[SECURITY_FIREWALL_BLOCKED] Malformed loopback port rejected: {api_url}"
        ) from exc
    allow_custom = os.environ.get("BIONIC_ALLOW_CUSTOM_LOOPBACK_PORT") == "1"
    if port is None or (port != 1234 and not allow_custom):
        raise SidecarFirewallError(
            f"[SECURITY_FIREWALL_BLOCKED] Loopback port '{port}' rejected; only Bionic port 1234 is permitted: {api_url}"
        )
    return raw


def _safe_subprocess_cwd(preferred: Path | None = None) -> str:
    """Return an existing directory path and self-heal an unlinked process cwd."""
    candidates: list[Path] = []
    if preferred is not None:
        pref_exp = Path(os.path.expanduser(str(preferred)))
        if pref_exp.is_absolute():
            candidates.append(pref_exp)
    candidates.extend([Path.home(), Path(tempfile.gettempdir()), Path("/")])
    chosen = Path("/")
    for cand in candidates:
        try:
            if cand.is_dir():
                chosen = cand
                break
        except OSError:
            continue
    try:
        os.getcwd()
    except OSError:
        try:
            os.chdir(chosen)
        except OSError:
            pass
    return str(chosen)


def _safe_abspath(path_obj: Path) -> Path:
    """Normalize and absolutize path_obj without failing on an unlinked process cwd."""
    expanded = Path(os.path.expanduser(str(path_obj)))
    if expanded.is_absolute():
        return Path(os.path.normpath(str(expanded)))
    base_dir = Path(_safe_subprocess_cwd())
    return Path(os.path.normpath(str(base_dir / expanded)))


def _is_path_within(candidate: Path, root: Path) -> bool:
    try:
        candidate.relative_to(root)
        return True
    except ValueError:
        return False


def _inspect_path_security(path_obj: Path) -> str | None:
    """Return block reason if path matches secret, NetCom, or raw CAD rules; else None."""
    expanded = Path(os.path.expanduser(str(path_obj)))
    abs_raw = _safe_abspath(expanded)
    resolved = abs_raw.resolve(strict=False)

    for variant in (expanded, abs_raw, resolved):
        parts_lower = [part.lower() for part in variant.parts]
        for seg in parts_lower:
            if seg in FORBIDDEN_DIR_SEGMENTS:
                return f"Forbidden compartment/secret path segment '{seg}': {path_obj}"

        name_lower = variant.name.lower()
        suffix_lower = variant.suffix.lower()

        if name_lower == ".env" or name_lower.startswith(".env.") or name_lower.endswith(".env"):
            return f"Environment secret file blocked: {path_obj}"
        if name_lower in SECRET_FILENAMES:
            return f"Credential key file blocked: {path_obj}"
        if suffix_lower in SECRET_EXTENSIONS:
            return f"Private key/certificate material blocked: {path_obj}"
        if any(name_lower.startswith(prefix) for prefix in PRIVATE_KEY_PREFIXES) and not name_lower.endswith(".pub"):
            return f"SSH private key blocked: {path_obj}"
        if suffix_lower in SECRET_TEXT_EXTENSIONS and any(marker in name_lower for marker in SECRET_JSON_MARKERS):
            return f"Credential/OAuth/token/MCP config secret file blocked: {path_obj}"
        if suffix_lower in FORBIDDEN_CAD_EXTENSIONS:
            return (
                f"ZERO_ADHOC_CAD_PARSING blocked raw CAD file ({suffix_lower}); "
                f"hardware-cad-inspector sidecar integration is deferred: {path_obj}"
            )
    return None


def validate_input_paths(
    paths: list[Path],
    repo_root: Path | None = None,
    *,
    require_exists: bool = True,
) -> list[Path]:
    """Validate context paths against secret/CAD firewalls and optional --repo boundary."""
    resolved_repo: Path | None = None
    if repo_root is not None:
        repo_reason = _inspect_path_security(repo_root)
        if repo_reason:
            raise SidecarFirewallError(f"[SECURITY_FIREWALL_BLOCKED] {repo_reason}")
        resolved_repo = _safe_abspath(repo_root).resolve(strict=False)

    validated: list[Path] = []
    for raw_path in paths:
        reason = _inspect_path_security(raw_path)
        if reason:
            raise SidecarFirewallError(f"[SECURITY_FIREWALL_BLOCKED] {reason}")
        resolved = _safe_abspath(raw_path).resolve(strict=False)
        if resolved_repo is not None and not _is_path_within(resolved, resolved_repo):
            raise SidecarFirewallError(
                f"[SECURITY_FIREWALL_BLOCKED] Single-repo containment (4C): "
                f"{resolved} escapes --repo boundary {resolved_repo}"
            )
        if require_exists and not resolved.is_file():
            raise SidecarFirewallError(
                f"[SECURITY_FIREWALL_BLOCKED] Context file missing or unreadable: {raw_path}"
            )
        validated.append(resolved)
    return validated


def validate_staging_dir(staging_dir: Path) -> Path:
    """Permit code staging strictly in isolated scratch/temp folders outside repos & configs."""
    reason = _inspect_path_security(staging_dir)
    if reason:
        raise SidecarFirewallError(f"[SECURITY_FIREWALL_BLOCKED] {reason}")

    raw_abs = _safe_abspath(Path(os.path.expanduser(str(staging_dir))))
    resolved = raw_abs.resolve(strict=False)

    home_resolved = Path.home().resolve(strict=False)
    protected_roots = [
        Path("/home/orin/Projects"),
        home_resolved / "Projects",
        Path("/home/orin/.gemini/config"),
        home_resolved / ".gemini" / "config",
        Path("/home/orin/.lmstudio"),
        home_resolved / ".lmstudio",
    ]
    for candidate in (raw_abs, resolved):
        for prot in protected_roots:
            prot_abs = Path(os.path.abspath(str(prot)))
            prot_res = prot.resolve(strict=False)
            if _is_path_within(candidate, prot_abs) or _is_path_within(candidate, prot_res):
                raise SidecarFirewallError(
                    f"[SECURITY_FIREWALL_BLOCKED] stage-code refuses protected repo/Ring-0/config path "
                    f"{candidate} (inside {prot}); use /tmp or brain scratch/."
                )
        for parent in (candidate, *candidate.parents):
            if (parent / ".git").exists():
                raise SidecarFirewallError(
                    f"[SECURITY_FIREWALL_BLOCKED] stage-code refuses git-tracked directory {candidate} "
                    f"(repo root {parent}); use /tmp/<subdir>, ~/.cache/homunculus_bionic_plugin, or brain scratch/."
                )

    tmp_abs = Path(os.path.abspath(tempfile.gettempdir()))
    tmp_res = tmp_abs.resolve(strict=False)
    cache_bases = (
        Path(os.path.abspath(str(home_resolved / ".cache" / "homunculus_bionic_plugin"))),
        (home_resolved / ".cache" / "homunculus_bionic_plugin").resolve(strict=False),
        Path(os.path.abspath("/home/orin/.cache/homunculus_bionic_plugin")),
    )
    brain_bases = (
        Path(os.path.abspath(str(home_resolved / ".gemini" / "antigravity-cli" / "brain"))),
        (home_resolved / ".gemini" / "antigravity-cli" / "brain").resolve(strict=False),
        Path(os.path.abspath("/home/orin/.gemini/antigravity-cli/brain")),
    )

    def _is_allowed_stage_candidate(cand: Path) -> bool:
        if (_is_path_within(cand, tmp_abs) and cand != tmp_abs) or (
            _is_path_within(cand, tmp_res) and cand != tmp_res
        ):
            return True
        if any(_is_path_within(cand, cb) for cb in cache_bases):
            return True
        if any(_is_path_within(cand, bb) and cand != bb for bb in brain_bases) and "scratch" in cand.parts:
            return True
        return False

    if not (_is_allowed_stage_candidate(raw_abs) and _is_allowed_stage_candidate(resolved)):
        raise SidecarFirewallError(
            f"[SECURITY_FIREWALL_BLOCKED] stage-code path {raw_abs} outside allowlist "
            "(/tmp/<subdir>, ~/.cache/homunculus_bionic_plugin, or brain/*/scratch/)."
        )
    return resolved


def estimate_eta(
    *,
    mode: str,
    prompt_bytes: int,
    max_tokens: int | None = None,
    prompt_tokens_override: int | None = None,
    max_eta_seconds: float = DEFAULT_MAX_ETA_SECONDS,
    expected_turns: int = 1,
) -> dict[str, Any]:
    """Compute calibrated prefill + decode ETA and plain-English circuit-breaker verdict."""
    if mode not in PROFILES:
        raise ValueError(f"Unsupported mode: {mode}")
    prof = PROFILES[mode]
    out_budget = int(max_tokens if max_tokens is not None else prof["default_max_tokens"])
    thinking_oh = int(prof["thinking_overhead_tokens"])
    turns = max(1, int(expected_turns))

    if prompt_tokens_override is not None:
        est_prompt_tokens = max(0, int(prompt_tokens_override))
    else:
        est_prompt_tokens = max(1, math.ceil(prompt_bytes / 3.6))

    est_output_tokens = (out_budget + thinking_oh) * turns
    total_prompt_tokens = est_prompt_tokens * turns

    prefill_s = total_prompt_tokens / float(prof["pp_tok_s"])
    decode_s = est_output_tokens / float(prof["tg_tok_s"])
    predicted_eta_s = round(prefill_s + decode_s, 2)

    trip_reasons: list[str] = []
    if est_prompt_tokens + out_budget + thinking_oh > int(prof["max_ctx"]):
        trip_reasons.append(
            f"Single-turn tokens ({est_prompt_tokens + out_budget + thinking_oh}) exceed "
            f"{mode} max_ctx ({prof['max_ctx']})."
        )
    if mode == "cpu-bg" and est_prompt_tokens > int(prof["prompt_cap"]):
        trip_reasons.append(
            f"cpu-bg prompt ({est_prompt_tokens} tok) exceeds 8k CPU guard ({prof['prompt_cap']} tok) — "
            "keeps gaming headroom and avoids >100s CPU prefill."
        )
    if predicted_eta_s > float(max_eta_seconds):
        trip_reasons.append(
            f"Predicted ETA {predicted_eta_s:.1f}s exceeds {float(max_eta_seconds):.1f}s cutoff "
            f"(handoff back to main Antigravity thread)."
        )

    return {
        "schema_version": SCHEMA_VERSION,
        "mode": mode,
        "preset": prof["preset"],
        "reasoning_effort": prof["reasoning_effort"],
        "est_prompt_tokens": est_prompt_tokens,
        "est_output_tokens": est_output_tokens,
        "expected_turns": turns,
        "pp_tok_s_basis": prof["pp_tok_s"],
        "tg_tok_s_basis": prof["tg_tok_s"],
        "prefill_eta_s": round(prefill_s, 2),
        "decode_eta_s": round(decode_s, 2),
        "predicted_eta_s": predicted_eta_s,
        "max_eta_seconds": float(max_eta_seconds),
        "tripped": bool(trip_reasons),
        "verdict": "HANDOFF_TO_MAIN_THREAD" if trip_reasons else "RUN_LOCALLY",
        "reasons": trip_reasons,
    }


def _http_json_request(
    url: str,
    payload: dict[str, Any] | None = None,
    timeout_s: float = 120.0,
) -> dict[str, Any]:
    data: bytes | None = None
    headers = {"Accept": "application/json"}
    method = "GET"
    if payload is not None:
        method = "POST"
        data = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout_s) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"HTTP {exc.code} from {url}: {body[:400]}") from exc
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"Loopback request to {url} failed: {exc}") from exc


def assemble_prompt_payload(
    *,
    user_prompt: str,
    context_files: list[Path],
    repo_root: Path | None,
    include_git_diff: bool,
    sys_prompt: str,
) -> tuple[str, list[dict[str, Any]]]:
    """Assemble bounded line-numbered file blocks + optional read-only git diff for inference."""
    sections: list[str] = [user_prompt.strip()]
    file_meta: list[dict[str, Any]] = []

    for fpath in context_files:
        raw_text = fpath.read_text(encoding="utf-8", errors="replace")
        lines = raw_text.splitlines()
        numbered = "\n".join(f"{idx}: {line}" for idx, line in enumerate(lines, 1))
        rel_display = str(fpath.relative_to(repo_root)) if repo_root else fpath.name
        sections.append(f"\n### CONTEXT FILE: {rel_display} ({len(lines)} lines)\n{numbered}\n")
        file_meta.append({"path": str(fpath), "label": rel_display, "lines": len(lines), "bytes": len(raw_text.encode("utf-8"))})

    if include_git_diff:
        if repo_root is None:
            raise SidecarFirewallError(
                "[SECURITY_FIREWALL_BLOCKED] --include-git-diff requires explicit single-repo --repo boundary (4C)."
            )
        diff_proc = subprocess.run(
            ["git", "--no-optional-locks", "-C", str(repo_root), "diff", "--no-ext-diff"],
            cwd=_safe_subprocess_cwd(repo_root),
            capture_output=True,
            text=True,
            check=False,
        )
        if diff_proc.returncode != 0:
            raise RuntimeError(f"git diff failed in {repo_root}: {diff_proc.stderr.strip()}")
        diff_text = diff_proc.stdout.strip()
        if diff_text:
            sections.append(f"\n### GIT WORKING-TREE DIFF ({repo_root.name})\n```diff\n{diff_text}\n```\n")
        else:
            sections.append(f"\n### GIT WORKING-TREE DIFF ({repo_root.name})\n(clean working tree — no unstaged diff)\n")

    full_user_content = "\n".join(s for s in sections if s)
    total_prompt_bytes = len(sys_prompt.encode("utf-8")) + len(full_user_content.encode("utf-8"))
    file_meta_summary = file_meta
    if total_prompt_bytes < 0:  # pragma: no cover
        raise AssertionError("unreachable")
    return full_user_content, file_meta_summary


def resolve_default_api_url() -> str:
    """Resolve optional loopback API URL override from environment or default."""
    return os.environ.get("BIONIC_SIDECAR_API_URL", "").strip() or DEFAULT_API_URL


def invoke_chat_completion(
    *,
    api_url: str,
    model_id: str,
    mode: str,
    system_prompt: str,
    user_content: str,
    max_tokens: int,
    timeout_s: float,
    preflight_checked: bool = False,
) -> dict[str, Any]:
    """Call OpenAI-compatible loopback endpoint using Bionic's verified reasoning_effort mapping."""
    if not preflight_checked:
        _, mode = preflight_live_inference(api_url, model_id, mode)
    prof = PROFILES[mode]
    payload = {
        "model": model_id,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content},
        ],
        "temperature": 0.0,
        "max_tokens": max_tokens,
        "reasoning_effort": prof["reasoning_effort"],
    }
    t0 = time.perf_counter()
    resp = _http_json_request(f"{api_url}/chat/completions", payload=payload, timeout_s=timeout_s)
    elapsed_s = round(max(0.001, time.perf_counter() - t0), 3)

    choice = (resp.get("choices") or [{}])[0]
    msg = choice.get("message") or {}
    content = (msg.get("content") or "").strip()
    reasoning_content = msg.get("reasoning_content") or ""
    usage = resp.get("usage") or {}
    completion_tokens = int(usage.get("completion_tokens") or 0)
    prompt_tokens = int(usage.get("prompt_tokens") or 0)
    stats = resp.get("stats") or {}

    return {
        "model": resp.get("model") or model_id,
        "mode": mode,
        "reasoning_effort": prof["reasoning_effort"],
        "elapsed_s": elapsed_s,
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
        "observed_tg_tok_s": stats.get("tokens_per_second")
        or (round(completion_tokens / elapsed_s, 2) if completion_tokens else None),
        "finish_reason": choice.get("finish_reason"),
        "reasoning_present": bool(reasoning_content),
        "content": content,
    }


def extract_staged_code(raw_content: str) -> str:
    """Extract primary fenced code block if present, otherwise return trimmed content."""
    match = FENCED_CODE_RE.search(raw_content)
    text = match.group(1) if match else raw_content
    return text.rstrip() + "\n"


def _read_prompt_arg(prompt: str | None, prompt_file: str | None) -> str:
    if prompt_file:
        p = Path(prompt_file)
        validate_input_paths([p], repo_root=None, require_exists=True)
        return p.read_text(encoding="utf-8")
    if prompt is not None and prompt.strip():
        return prompt.strip()
    raise RuntimeError("Either --prompt or --prompt-file must be provided.")


def resolve_max_eta_seconds(args: argparse.Namespace) -> float:
    """Resolve explicit --max-eta-seconds or tier cutoff (60s auto vs 90s explicit)."""
    explicit = getattr(args, "max_eta_seconds", None)
    if explicit is not None:
        return float(explicit)
    tier = getattr(args, "invocation_tier", "explicit")
    return AUTO_MAX_ETA_SECONDS if tier == "auto" else DEFAULT_MAX_ETA_SECONDS


def _resolve_telemetry_log(log_path: Path | None = None) -> Path:
    if log_path is not None:
        return log_path
    env_p = os.environ.get("BIONIC_SIDECAR_TELEMETRY_LOG", "").strip()
    if env_p:
        return Path(os.path.expanduser(env_p))
    return DEFAULT_TELEMETRY_LOG


def record_usage_telemetry(entry: dict[str, Any], log_path: Path | None = None) -> None:
    """Append metadata-only usage telemetry with 0700/0600 permissions; ignore EROFS in sandboxes."""
    path = _resolve_telemetry_log(log_path)
    payload = {"ts": datetime.now(timezone.utc).isoformat(timespec="seconds"), **entry}
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.parent.is_symlink() or path.is_symlink():
            return
        try:
            os.chmod(path.parent, 0o700)
        except OSError:
            pass
        flags = os.O_WRONLY | os.O_CREAT | os.O_APPEND | getattr(os, "O_NOFOLLOW", 0)
        fd = os.open(path, flags, 0o600)
        with os.fdopen(fd, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(payload) + "\n")
        try:
            os.chmod(path, 0o600)
        except OSError:
            pass
    except OSError:
        pass


def summarize_usage_telemetry(log_path: Path | None = None) -> dict[str, Any]:
    """Summarize recorded sidecar telemetry counts without exposing prompt contents."""
    path = _resolve_telemetry_log(log_path)
    total = 0
    tripped = 0
    by_tier: dict[str, int] = {"auto": 0, "explicit": 0}
    elapsed_vals: list[float] = []
    if path.is_file():
        try:
            for raw in path.read_text(encoding="utf-8", errors="replace").splitlines()[-50:]:
                if not raw.strip():
                    continue
                row = json.loads(raw)
                total += 1
                if row.get("tripped"):
                    tripped += 1
                tier = str(row.get("invocation_tier") or "explicit")
                if tier in by_tier:
                    by_tier[tier] += 1
                if isinstance(row.get("elapsed_s"), (int, float)):
                    elapsed_vals.append(float(row["elapsed_s"]))
        except (OSError, json.JSONDecodeError):
            pass
    avg_elapsed = round(sum(elapsed_vals) / len(elapsed_vals), 3) if elapsed_vals else None
    return {
        "log_path": str(path),
        "recent_runs": total,
        "tripped_runs": tripped,
        "by_tier": by_tier,
        "recent_elapsed_avg_s": avg_elapsed,
    }


def probe_server_models(
    api_url: str = DEFAULT_API_URL,
    *,
    model_id: str = DEFAULT_MODEL_ID,
    timeout_s: float = 5.0,
) -> dict[str, Any]:
    """Query Bionic /api/v0/models (falling back to /v1/models on 404) for exact loaded state."""
    validated_v1 = validate_loopback_url(api_url)
    root_url = validated_v1[:-3] if validated_v1.endswith("/v1") else validated_v1
    loaded_models: list[str] = []
    downloaded_unloaded_models: list[str] = []
    loaded_context_length: int | None = None
    probe_source = f"{root_url}/api/v0/models"

    def _consume_rows(rows: list[Any], *, default_state: str) -> None:
        nonlocal loaded_context_length
        for item in rows:
            if not isinstance(item, dict) or not item.get("id"):
                continue
            mid = str(item["id"])
            state = str(item.get("state") or default_state).lower()
            if state == "loaded":
                loaded_models.append(mid)
                if mid == model_id and item.get("loaded_context_length") is not None:
                    loaded_context_length = int(item["loaded_context_length"])
            else:
                downloaded_unloaded_models.append(mid)

    try:
        data = _http_json_request(probe_source, timeout_s=timeout_s)
        _consume_rows(list(data.get("data") or []), default_state="not-loaded")
    except RuntimeError as exc:
        if "HTTP 404 " in str(exc):
            probe_source = f"{validated_v1}/models"
            try:
                data = _http_json_request(probe_source, timeout_s=timeout_s)
                _consume_rows(list(data.get("data") or []), default_state="not-loaded")
            except RuntimeError as exc2:
                return {
                    "reachable": False,
                    "error": str(exc2),
                    "probe_source": probe_source,
                    "loaded_models": [],
                    "downloaded_unloaded_models": [],
                    "target_model_loaded": False,
                    "loaded_context_length": None,
                }
        else:
            return {
                "reachable": False,
                "error": str(exc),
                "probe_source": probe_source,
                "loaded_models": [],
                "downloaded_unloaded_models": [],
                "target_model_loaded": False,
                "loaded_context_length": None,
            }

    return {
        "reachable": True,
        "error": None,
        "probe_source": probe_source,
        "loaded_models": loaded_models,
        "downloaded_unloaded_models": downloaded_unloaded_models,
        "target_model_loaded": model_id in loaded_models,
        "loaded_context_length": loaded_context_length,
    }


def preflight_live_inference(api_url: str, model_id: str, requested_mode: str) -> tuple[dict[str, Any], str]:
    """Verify target model is loaded (anti-JIT VRAM guard) and auto-clamp fast/deep -> cpu-bg at <=16k ctx."""
    srv = probe_server_models(api_url, model_id=model_id, timeout_s=3.0)
    if not srv["reachable"]:
        raise RuntimeError(f"[BIONIC_OFFLINE] Loopback server unreachable at {api_url}: {srv['error']}")
    if not srv["target_model_loaded"]:
        raise SidecarFirewallError(
            f"[BIONIC_UNLOADED_CONFIRMATION_REQUIRED] Model '{model_id}' is UNLOADED at {api_url}; "
            "refusing /chat/completions to prevent unconfirmed JIT VRAM allocation. Load explicitly with user confirmation."
        )
    effective_mode = requested_mode
    loaded_ctx = srv.get("loaded_context_length")
    if (loaded_ctx is None or int(loaded_ctx) <= int(PROFILES["cpu-bg"]["max_ctx"])) and requested_mode != "cpu-bg":
        effective_mode = "cpu-bg"
    return srv, effective_mode


def _enforce_eta_or_raise(
    *,
    mode: str,
    prompt_bytes: int,
    max_tokens: int,
    max_eta_seconds: float,
    expected_turns: int,
    force_slow: bool,
    prompt_tokens_override: int | None = None,
    cmd_name: str = "query",
    invocation_tier: str = "explicit",
) -> dict[str, Any]:
    eta = estimate_eta(
        mode=mode,
        prompt_bytes=prompt_bytes,
        max_tokens=max_tokens,
        prompt_tokens_override=prompt_tokens_override,
        max_eta_seconds=max_eta_seconds,
        expected_turns=expected_turns,
    )
    if eta["tripped"] and not force_slow:
        record_usage_telemetry(
            {
                "cmd": cmd_name,
                "invocation_tier": invocation_tier,
                "mode": mode,
                "est_prompt_tokens": eta["est_prompt_tokens"],
                "predicted_eta_s": eta["predicted_eta_s"],
                "max_eta_seconds": max_eta_seconds,
                "tripped": True,
                "elapsed_s": None,
                "observed_tg_tok_s": None,
                "finish_reason": "eta_tripped",
            }
        )
        reason_str = " | ".join(eta["reasons"])
        raise SidecarEtaTrippedError(
            f"[ETA_CIRCUIT_BREAKER_TRIPPED] {reason_str} Pass --force-slow only if you intentionally accept local latency.",
            eta,
        )
    return eta


def cmd_status(args: argparse.Namespace) -> int:
    api_url = validate_loopback_url(args.api_url or resolve_default_api_url())
    sys_prompt, sys_src = load_system_prompt(Path(args.system_prompt))
    probe = probe_server_models(api_url, model_id=args.model, timeout_s=5.0)

    payload = {
        "schema_version": SCHEMA_VERSION,
        "api_url": api_url,
        "reachable": probe["reachable"],
        "loaded_models": probe["loaded_models"],
        "downloaded_unloaded_models": probe["downloaded_unloaded_models"],
        "target_model_loaded": probe["target_model_loaded"],
        "loaded_context_length": probe["loaded_context_length"],
        "probe_source": probe["probe_source"],
        "error": probe["error"],
        "auto_max_eta_seconds": AUTO_MAX_ETA_SECONDS,
        "default_max_eta_seconds": DEFAULT_MAX_ETA_SECONDS,
        "system_prompt_source": sys_src,
        "system_prompt_bytes": len(sys_prompt.encode("utf-8")),
        "profiles": PROFILES,
    }
    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        state = "ONLINE" if payload["reachable"] else f"OFFLINE ({probe['error']})"
        print(
            f"Bionic Sidecar Status: {state} @ {api_url} | Loaded: {', '.join(probe['loaded_models']) or 'none'} "
            f"| Target Loaded: {probe['target_model_loaded']} (ctx={probe['loaded_context_length']})"
        )
        print(
            f"System Prompt: {sys_src} ({payload['system_prompt_bytes']} B) | "
            f"ETA Cutoffs: auto={AUTO_MAX_ETA_SECONDS:.0f}s explicit={DEFAULT_MAX_ETA_SECONDS:.0f}s"
        )
    return 0 if payload["reachable"] else EXIT_RUNTIME_ERROR


def cmd_check_eta(args: argparse.Namespace) -> int:
    sys_prompt, _ = load_system_prompt(Path(args.system_prompt))
    repo_root = Path(args.repo) if args.repo else None
    raw_contexts = [Path(p) for p in (args.context_files or [])]
    validated_files = validate_input_paths(raw_contexts, repo_root=repo_root, require_exists=True)

    user_prompt = args.prompt or ""
    if args.prompt_file:
        user_prompt = _read_prompt_arg(None, args.prompt_file)

    prompt_bytes = len(sys_prompt.encode("utf-8")) + len(user_prompt.encode("utf-8"))
    if validated_files or args.include_git_diff:
        assembled, _ = assemble_prompt_payload(
            user_prompt=user_prompt,
            context_files=validated_files,
            repo_root=repo_root.resolve(strict=False) if repo_root else None,
            include_git_diff=bool(args.include_git_diff),
            sys_prompt=sys_prompt,
        )
        prompt_bytes = len(sys_prompt.encode("utf-8")) + len(assembled.encode("utf-8"))

    max_toks = int(args.max_tokens if args.max_tokens is not None else PROFILES[args.mode]["default_max_tokens"])
    max_eta = resolve_max_eta_seconds(args)
    eta = estimate_eta(
        mode=args.mode,
        prompt_bytes=prompt_bytes,
        max_tokens=max_toks,
        prompt_tokens_override=args.prompt_tokens,
        max_eta_seconds=max_eta,
        expected_turns=args.expected_turns,
    )
    eta["invocation_tier"] = getattr(args, "invocation_tier", "explicit")
    if args.json:
        print(json.dumps(eta, indent=2))
    else:
        print(
            f"[{eta['verdict']}] tier={eta['invocation_tier']} mode={eta['mode']} prompt~={eta['est_prompt_tokens']} tok, "
            f"out~={eta['est_output_tokens']} tok -> ETA={eta['predicted_eta_s']}s "
            f"(limit {eta['max_eta_seconds']}s)"
        )
    if eta["tripped"] and not args.force_slow:
        print(f"[ETA_CIRCUIT_BREAKER_TRIPPED] {' | '.join(eta['reasons'])}", file=sys.stderr)
        return EXIT_ETA_TRIPPED
    return 0


def cmd_query(args: argparse.Namespace) -> int:
    api_url = validate_loopback_url(args.api_url or resolve_default_api_url())
    sys_prompt, sys_src = load_system_prompt(Path(args.system_prompt))
    repo_root = Path(args.repo) if args.repo else None
    repo_resolved = repo_root.resolve(strict=False) if repo_root else None
    raw_contexts = [Path(p) for p in (args.context_files or [])]
    validated_files = validate_input_paths(raw_contexts, repo_root=repo_root, require_exists=True)
    user_prompt = _read_prompt_arg(args.prompt, args.prompt_file)

    assembled, file_meta = assemble_prompt_payload(
        user_prompt=user_prompt,
        context_files=validated_files,
        repo_root=repo_resolved,
        include_git_diff=bool(args.include_git_diff),
        sys_prompt=sys_prompt,
    )
    prompt_bytes = len(sys_prompt.encode("utf-8")) + len(assembled.encode("utf-8"))
    tier = getattr(args, "invocation_tier", "explicit")
    requested_max_toks = args.max_tokens
    max_toks = int(requested_max_toks if requested_max_toks is not None else PROFILES[args.mode]["default_max_tokens"])
    max_eta = resolve_max_eta_seconds(args)
    eta = _enforce_eta_or_raise(
        mode=args.mode,
        prompt_bytes=prompt_bytes,
        max_tokens=max_toks,
        max_eta_seconds=max_eta,
        expected_turns=args.expected_turns,
        force_slow=args.force_slow,
        cmd_name="query",
        invocation_tier=tier,
    )
    _, effective_mode = preflight_live_inference(api_url, args.model, args.mode)
    if effective_mode != args.mode:
        max_toks = int(requested_max_toks if requested_max_toks is not None else PROFILES[effective_mode]["default_max_tokens"])
        eta = _enforce_eta_or_raise(
            mode=effective_mode,
            prompt_bytes=prompt_bytes,
            max_tokens=max_toks,
            max_eta_seconds=max_eta,
            expected_turns=args.expected_turns,
            force_slow=args.force_slow,
            cmd_name="query",
            invocation_tier=tier,
        )
    res = invoke_chat_completion(
        api_url=api_url,
        model_id=args.model,
        mode=effective_mode,
        system_prompt=sys_prompt,
        user_content=assembled,
        max_tokens=max_toks,
        timeout_s=max(max_eta + 30.0, 120.0),
        preflight_checked=True,
    )
    record_usage_telemetry(
        {
            "cmd": "query",
            "invocation_tier": tier,
            "mode": effective_mode,
            "est_prompt_tokens": eta["est_prompt_tokens"],
            "predicted_eta_s": eta["predicted_eta_s"],
            "max_eta_seconds": max_eta,
            "tripped": eta["tripped"],
            "elapsed_s": res["elapsed_s"],
            "observed_tg_tok_s": res["observed_tg_tok_s"],
            "finish_reason": res["finish_reason"],
        }
    )
    out_obj = {
        "schema_version": SCHEMA_VERSION,
        "system_prompt_source": sys_src,
        "invocation_tier": tier,
        "eta_estimate": eta,
        "context_files": file_meta,
        "completion": res,
    }
    if args.json:
        print(json.dumps(out_obj, indent=2))
    else:
        print(res["content"])
        print(
            f"\n[SIDECAR TELEMETRY: mode={res['mode']} elapsed={res['elapsed_s']}s "
            f"prompt={res['prompt_tokens']}tok out={res['completion_tokens']}tok "
            f"tg={res['observed_tg_tok_s']} tok/s]",
            file=sys.stderr,
        )
    return 0


def cmd_audit_to_quarantine(args: argparse.Namespace) -> int:
    api_url = validate_loopback_url(args.api_url or resolve_default_api_url())
    sys_prompt, sys_src = load_system_prompt(Path(args.system_prompt))
    repo_root = Path(args.repo) if args.repo else None
    repo_resolved = repo_root.resolve(strict=False) if repo_root else None
    raw_contexts = [Path(p) for p in (args.context_files or [])]
    validated_files = validate_input_paths(raw_contexts, repo_root=repo_root, require_exists=True)
    user_prompt = _read_prompt_arg(args.prompt, args.prompt_file)

    gateway_path = Path(args.homunculus_root) / "scripts" / "memory_gateway.py"
    if not gateway_path.is_file():
        raise RuntimeError(f"memory_gateway.py not found at {gateway_path}")

    assembled, file_meta = assemble_prompt_payload(
        user_prompt=user_prompt,
        context_files=validated_files,
        repo_root=repo_resolved,
        include_git_diff=bool(args.include_git_diff),
        sys_prompt=sys_prompt,
    )
    quar_candidate = Path(args.memory_root) / "Projects" / args.project / "Quarantine" / f"{args.name}.md"
    if not args.overwrite and quar_candidate.exists():
        raise RuntimeError(
            f"Quarantine note already exists (pass --overwrite to replace): {quar_candidate}"
        )

    prompt_bytes = len(sys_prompt.encode("utf-8")) + len(assembled.encode("utf-8"))
    tier = getattr(args, "invocation_tier", "explicit")
    requested_max_toks = args.max_tokens
    max_toks = int(requested_max_toks if requested_max_toks is not None else PROFILES[args.mode]["default_max_tokens"])
    max_eta = resolve_max_eta_seconds(args)
    eta = _enforce_eta_or_raise(
        mode=args.mode,
        prompt_bytes=prompt_bytes,
        max_tokens=max_toks,
        max_eta_seconds=max_eta,
        expected_turns=args.expected_turns,
        force_slow=args.force_slow,
        cmd_name="audit-to-quarantine",
        invocation_tier=tier,
    )
    _, effective_mode = preflight_live_inference(api_url, args.model, args.mode)
    if effective_mode != args.mode:
        max_toks = int(requested_max_toks if requested_max_toks is not None else PROFILES[effective_mode]["default_max_tokens"])
        eta = _enforce_eta_or_raise(
            mode=effective_mode,
            prompt_bytes=prompt_bytes,
            max_tokens=max_toks,
            max_eta_seconds=max_eta,
            expected_turns=args.expected_turns,
            force_slow=args.force_slow,
            cmd_name="audit-to-quarantine",
            invocation_tier=tier,
        )
    res = invoke_chat_completion(
        api_url=api_url,
        model_id=args.model,
        mode=effective_mode,
        system_prompt=sys_prompt,
        user_content=assembled,
        max_tokens=max_toks,
        timeout_s=max(max_eta + 30.0, 150.0),
        preflight_checked=True,
    )
    record_usage_telemetry(
        {
            "cmd": "audit-to-quarantine",
            "invocation_tier": tier,
            "mode": effective_mode,
            "est_prompt_tokens": eta["est_prompt_tokens"],
            "predicted_eta_s": eta["predicted_eta_s"],
            "max_eta_seconds": max_eta,
            "tripped": eta["tripped"],
            "elapsed_s": res["elapsed_s"],
            "observed_tg_tok_s": res["observed_tg_tok_s"],
            "finish_reason": res["finish_reason"],
        }
    )

    body_text = (
        f"<!-- local_sidecar provenance: schema={SCHEMA_VERSION} author=\"LM Studio Bionic ({res['model']}, {res['mode']})\" "
        f"elapsed_s={res['elapsed_s']} prompt_tok={res['prompt_tokens']} "
        f"out_tok={res['completion_tokens']} tg_tok_s={res['observed_tg_tok_s']} -->\n\n"
        f"{res['content']}\n"
    )

    with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", suffix=".md", delete=False) as tf:
        tf.write(body_text)
        tmp_body_path = Path(tf.name)
    os.chmod(tmp_body_path, 0o600)

    try:
        gw_cmd = [
            sys.executable,
            str(gateway_path),
            "quarantine-note",
            "--homunculus-root",
            str(args.homunculus_root),
            "--memory-root",
            str(args.memory_root),
            "--project",
            args.project,
            "--name",
            args.name,
            "--title",
            args.title,
            "--reason",
            args.reason,
            "--body-file",
            str(tmp_body_path),
            "--json",
        ]
        gw_proc = subprocess.run(
            gw_cmd,
            cwd=_safe_subprocess_cwd(),
            capture_output=True,
            text=True,
            check=False,
        )
        if gw_proc.returncode != 0:
            raise RuntimeError(
                f"memory_gateway.py quarantine-note failed (exit {gw_proc.returncode}): "
                f"{gw_proc.stderr.strip() or gw_proc.stdout.strip()}"
            )
        gw_result = json.loads(gw_proc.stdout)
    finally:
        tmp_body_path.unlink(missing_ok=True)

    payload = {
        "schema_version": SCHEMA_VERSION,
        "system_prompt_source": sys_src,
        "eta_estimate": eta,
        "context_files": file_meta,
        "completion_telemetry": {k: v for k, v in res.items() if k != "content"},
        "gateway_receipt": gw_result,
    }
    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        written_loc = gw_result.get("note_file") or gw_result.get("note_rel")
        print(f"[QUARANTINED] Wrote {written_loc} via memory_gateway.py ({res['elapsed_s']}s)")
    return 0


def _write_private_staging_file(raw_path: Path, resolved_path: Path, text: str) -> None:
    if raw_path.is_symlink() or resolved_path.is_symlink():
        raise SidecarFirewallError(f"[SECURITY_FIREWALL_BLOCKED] Staging refuses symlink target: {raw_path}")
    flags = os.O_WRONLY | os.O_CREAT | os.O_TRUNC | getattr(os, "O_NOFOLLOW", 0)
    try:
        fd = os.open(resolved_path, flags, 0o600)
    except OSError as exc:
        raise SidecarFirewallError(f"[SECURITY_FIREWALL_BLOCKED] Staging write rejected ({exc}): {raw_path}") from exc
    with os.fdopen(fd, "w", encoding="utf-8") as fh:
        fh.write(text)


def stage_code_artifact(
    *,
    staging_dir: Path,
    target_filename: str,
    generated_text: str,
    compare_against: Path | None = None,
    telemetry: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Write staged draft + optional py_compile + unified diff inside validated 0700/0600 scratch dir."""
    safe_dir = validate_staging_dir(staging_dir)
    if Path(target_filename).name != target_filename or "/" in target_filename or "\\" in target_filename:
        raise SidecarFirewallError(
            f"[SECURITY_FIREWALL_BLOCKED] --target-filename must be a basename only: {target_filename}"
        )
    safe_dir.mkdir(parents=True, exist_ok=True)
    os.chmod(safe_dir, 0o700)
    raw_staged = safe_dir / target_filename
    staged_file = raw_staged.resolve(strict=False)
    if not _is_path_within(staged_file, safe_dir):
        raise SidecarFirewallError(f"[SECURITY_FIREWALL_BLOCKED] Path escape rejected: {staged_file}")

    extracted = extract_staged_code(generated_text)
    _write_private_staging_file(raw_staged, staged_file, extracted)

    compile_ok: bool | None = None
    compile_error: str | None = None
    if staged_file.suffix == ".py":
        comp = subprocess.run(
            [sys.executable, "-m", "py_compile", str(staged_file)],
            cwd=_safe_subprocess_cwd(safe_dir),
            capture_output=True,
            text=True,
            check=False,
        )
        compile_ok = comp.returncode == 0
        if not compile_ok:
            compile_error = comp.stderr.strip() or comp.stdout.strip()

    diff_path: Path | None = None
    diff_lines = 0
    if compare_against is not None:
        validate_input_paths([compare_against], repo_root=None, require_exists=True)
        old_lines = compare_against.read_text(encoding="utf-8", errors="replace").splitlines(keepends=True)
        new_lines = extracted.splitlines(keepends=True)
        udiff = list(
            difflib.unified_diff(
                old_lines,
                new_lines,
                fromfile=str(compare_against),
                tofile=str(staged_file),
            )
        )
        raw_diff = safe_dir / f"{target_filename}.diff"
        diff_path = raw_diff.resolve(strict=False)
        if not _is_path_within(diff_path, safe_dir):
            raise SidecarFirewallError(f"[SECURITY_FIREWALL_BLOCKED] Diff path escape rejected: {diff_path}")
        _write_private_staging_file(raw_diff, diff_path, "".join(udiff))
        diff_lines = len(udiff)

    raw_receipt = safe_dir / f"{target_filename}.receipt.json"
    receipt_path = raw_receipt.resolve(strict=False)
    if not _is_path_within(receipt_path, safe_dir):
        raise SidecarFirewallError(f"[SECURITY_FIREWALL_BLOCKED] Receipt path escape rejected: {receipt_path}")
    receipt = {
        "schema_version": SCHEMA_VERSION,
        "staged_file": str(staged_file),
        "bytes": len(extracted.encode("utf-8")),
        "py_compile_ok": compile_ok,
        "py_compile_error": compile_error,
        "diff_file": str(diff_path) if diff_path else None,
        "diff_lines": diff_lines,
        "telemetry": telemetry or {},
    }
    _write_private_staging_file(raw_receipt, receipt_path, json.dumps(receipt, indent=2) + "\n")
    return receipt


def cmd_stage_code(args: argparse.Namespace) -> int:
    # Validate staging target and firewall BEFORE calling loopback inference (fail closed offline!)
    safe_staging = validate_staging_dir(Path(args.staging_dir))
    api_url = validate_loopback_url(args.api_url or resolve_default_api_url())
    sys_prompt, _ = load_system_prompt(Path(args.system_prompt))
    repo_root = Path(args.repo) if args.repo else None
    repo_resolved = repo_root.resolve(strict=False) if repo_root else None
    raw_contexts = [Path(p) for p in (args.context_files or [])]
    validated_files = validate_input_paths(raw_contexts, repo_root=repo_root, require_exists=True)
    compare_path = Path(args.compare_against) if args.compare_against else None
    if compare_path is not None:
        validate_input_paths([compare_path], repo_root=repo_root, require_exists=True)
    user_prompt = _read_prompt_arg(args.prompt, args.prompt_file)

    assembled, _ = assemble_prompt_payload(
        user_prompt=user_prompt,
        context_files=validated_files,
        repo_root=repo_resolved,
        include_git_diff=bool(args.include_git_diff),
        sys_prompt=sys_prompt,
    )
    prompt_bytes = len(sys_prompt.encode("utf-8")) + len(assembled.encode("utf-8"))
    tier = getattr(args, "invocation_tier", "explicit")
    requested_max_toks = args.max_tokens
    max_toks = int(requested_max_toks if requested_max_toks is not None else PROFILES[args.mode]["default_max_tokens"])
    max_eta = resolve_max_eta_seconds(args)
    eta = _enforce_eta_or_raise(
        mode=args.mode,
        prompt_bytes=prompt_bytes,
        max_tokens=max_toks,
        max_eta_seconds=max_eta,
        expected_turns=args.expected_turns,
        force_slow=args.force_slow,
        cmd_name="stage-code",
        invocation_tier=tier,
    )
    _, effective_mode = preflight_live_inference(api_url, args.model, args.mode)
    if effective_mode != args.mode:
        max_toks = int(requested_max_toks if requested_max_toks is not None else PROFILES[effective_mode]["default_max_tokens"])
        eta = _enforce_eta_or_raise(
            mode=effective_mode,
            prompt_bytes=prompt_bytes,
            max_tokens=max_toks,
            max_eta_seconds=max_eta,
            expected_turns=args.expected_turns,
            force_slow=args.force_slow,
            cmd_name="stage-code",
            invocation_tier=tier,
        )
    res = invoke_chat_completion(
        api_url=api_url,
        model_id=args.model,
        mode=effective_mode,
        system_prompt=sys_prompt,
        user_content=assembled,
        max_tokens=max_toks,
        timeout_s=max(max_eta + 30.0, 150.0),
        preflight_checked=True,
    )
    record_usage_telemetry(
        {
            "cmd": "stage-code",
            "invocation_tier": tier,
            "mode": effective_mode,
            "est_prompt_tokens": eta["est_prompt_tokens"],
            "predicted_eta_s": eta["predicted_eta_s"],
            "max_eta_seconds": max_eta,
            "tripped": eta["tripped"],
            "elapsed_s": res["elapsed_s"],
            "observed_tg_tok_s": res["observed_tg_tok_s"],
            "finish_reason": res["finish_reason"],
        }
    )
    receipt = stage_code_artifact(
        staging_dir=safe_staging,
        target_filename=args.target_filename,
        generated_text=res["content"],
        compare_against=compare_path,
        telemetry={"eta": eta, **{k: v for k, v in res.items() if k != "content"}},
    )
    if args.json:
        print(json.dumps(receipt, indent=2))
    else:
        print(
            f"[STAGED] {receipt['staged_file']} ({receipt['bytes']} B) | "
            f"py_compile_ok={receipt['py_compile_ok']} | diff={receipt['diff_file']}"
        )
    if receipt["py_compile_ok"] is False:
        print(f"py_compile failed: {receipt['py_compile_error']}", file=sys.stderr)
        return EXIT_RUNTIME_ERROR
    return 0


CONTROL_PROFILES: dict[str, dict[str, Any]] = {
    "gpu-daily": {"context_length": 49152, "preset": "Qwen3.6-35B-Fast-Sweep"},
    "cpu-bg": {"context_length": 16384, "preset": "Qwen3.6-35B-CPU-Background"},
}


def build_concrete_model_config(profile: str) -> dict[str, Any]:
    """Return Bionic user-concrete-model-default-config JSON for gpu-daily or cpu-bg."""
    if profile not in CONTROL_PROFILES:
        raise ValueError(f"Unsupported control profile: {profile}")
    if profile == "cpu-bg":
        op_fields = [
            {"key": "llm.prediction.reasoning.enableThinking", "value": False},
            {"key": "llm.prediction.llama.cpuThreads", "value": 6},
        ]
        load_fields: list[dict[str, Any]] = [
            {"key": "llm.load.llama.autoFit", "value": False},
            {"key": "llm.load.contextLength", "value": 16384},
            {"key": "llm.load.llama.acceleration.offloadRatio", "value": "off"},
            {"key": "llm.load.llama.flashAttention", "value": False},
            {"key": "llm.load.offloadKVCacheToGpu", "value": False},
            {"key": "llm.load.llama.cpuThreadPoolSize", "value": 6},
            {
                "key": "llm.load.llama.argumentsOverride",
                "value": {
                    "enabled": True,
                    "disabledParameters": [],
                    "overrideParameters": [
                        {"key": "--device", "value": "none"},
                        {"key": "--cpu-range", "value": "6-11"},
                        {"key": "--cpu-strict", "value": "1"},
                        {"key": "--prio", "value": "-1"},
                    ],
                    "excludeAllConfig": False,
                },
            },
        ]
        return {"preset": CONTROL_PROFILES[profile]["preset"], "operation": {"fields": op_fields}, "load": {"fields": load_fields}}

    op_fields = [
        {"key": "llm.prediction.reasoning.enableThinking", "value": False},
        {"key": "llm.prediction.llama.cpuThreads", "value": 8},
    ]
    load_fields = [
        {"key": "llm.load.llama.autoFit", "value": False},
        {"key": "llm.load.contextLength", "value": 49152},
        {"key": "llm.load.llama.acceleration.offloadRatio", "value": "max"},
        {"key": "llm.load.numCpuExpertLayersRatio", "value": 0.65},
        {"key": "llm.load.llama.flashAttention", "value": True},
        {"key": "llm.load.offloadKVCacheToGpu", "value": True},
        {"key": "llm.load.llama.kCacheQuantizationType", "value": {"checked": True, "value": "q8_0"}},
        {"key": "llm.load.llama.vCacheQuantizationType", "value": {"checked": True, "value": "q8_0"}},
        {"key": "llm.load.llama.cpuThreadPoolSize", "value": 8},
        {
            "key": "llm.load.llama.argumentsOverride",
            "value": {
                "enabled": True,
                "disabledParameters": [],
                "overrideParameters": [{"key": "--parallel", "value": "4"}],
                "excludeAllConfig": False,
            },
        },
    ]
    return {"preset": CONTROL_PROFILES[profile]["preset"], "operation": {"fields": op_fields}, "load": {"fields": load_fields}}


def _read_hw_counters() -> dict[str, Any]:
    """Read sysfs VRAM and /proc/meminfo counters gracefully inside/outside sandboxes."""
    vram_bytes: int | None = None
    mem_avail_kib: int | None = None
    try:
        vram_bytes = int(VRAM_USED_SYSFS.read_text(encoding="utf-8").strip())
    except (OSError, ValueError):
        pass
    try:
        for line in PROC_MEMINFO_PATH.read_text(encoding="utf-8").splitlines():
            if line.startswith("MemAvailable:"):
                mem_avail_kib = int(line.split()[1])
                break
    except (OSError, ValueError, IndexError):
        pass
    return {
        "vram_used_bytes": vram_bytes,
        "vram_used_gib": round(vram_bytes / (1024**3), 3) if vram_bytes is not None else None,
        "mem_available_kib": mem_avail_kib,
        "mem_available_gib": round(mem_avail_kib / (1024**2), 2) if mem_avail_kib is not None else None,
    }


def _probe_lms_daemon(lms_bin: Path = DEFAULT_LMS_BIN) -> dict[str, Any]:
    """Check headless lms daemon status without failing if daemon or sandbox blocks IPC."""
    if not lms_bin.is_file():
        return {"available": False, "running": False, "summary": f"missing lms binary: {lms_bin}"}
    try:
        proc = subprocess.run(
            [str(lms_bin), "daemon", "status"],
            cwd=_safe_subprocess_cwd(),
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )
        raw = (proc.stdout or proc.stderr or "").strip()
        running = proc.returncode == 0 and ("is running" in raw.lower() and "not running" not in raw.lower())
        return {"available": True, "running": running, "summary": raw or f"exit {proc.returncode}"}
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {"available": True, "running": False, "summary": f"probe error: {exc}"}


def _run_lms_cmd(lms_bin: Path, argv: list[str], *, timeout_s: float = 60.0) -> subprocess.CompletedProcess[str]:
    if not lms_bin.is_file():
        raise RuntimeError(f"lms binary missing at {lms_bin}")
    return subprocess.run(
        [str(lms_bin), *argv],
        cwd=_safe_subprocess_cwd(),
        capture_output=True,
        text=True,
        timeout=timeout_s,
        check=False,
    )


def _has_gui_display_socket() -> bool:
    uid = os.getuid()
    if os.environ.get("WAYLAND_DISPLAY") or os.environ.get("DISPLAY"):
        return True
    for glob_dir, pattern in ((Path(f"/run/user/{uid}"), "wayland-*"), (Path("/tmp/.X11-unix"), "X*")):
        try:
            if glob_dir.is_dir() and any(glob_dir.glob(pattern)):
                return True
        except OSError:
            pass
    return False


def _control_plan(action: str, profile: str, model_id: str, lms_bin: Path, cfg_path: Path, api_url: str) -> dict[str, Any]:
    """Build deterministic --dry-run preview for remote lifecycle actions."""
    action_norm = _normalize_control_cli_action(action)
    port = urllib.parse.urlparse(api_url).port or 1234
    planned: list[list[str]] = []
    if action_norm == "start-headless":
        planned.extend(
            [
                [str(lms_bin), "daemon", "up", "--json"],
                [str(lms_bin), "server", "start", "--bind", "127.0.0.1", "--port", str(port)],
            ]
        )
    if action_norm in {"start-headless", "load"}:
        planned.append([str(lms_bin), "load", model_id, "--identifier", model_id, "-y"])
    elif action_norm == "unload":
        planned.append([str(lms_bin), "unload", model_id])
    elif action_norm == "stop-server":
        planned.extend([[str(lms_bin), "unload", "--all"], [str(lms_bin), "server", "stop"]])
    res: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "status": "DRY_RUN_OK",
        "action": action_norm,
        "profile": profile,
        "api_url": api_url,
        "model": model_id,
        "concrete_config_path": str(cfg_path),
        "planned_commands": planned,
    }
    if action_norm in {"start-headless", "load"}:
        res["concrete_config"] = build_concrete_model_config(profile)
    return res


def _control_status(api_url: str, model_id: str, lms_bin: Path) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "action": "status",
        "api_url": api_url,
        "model": model_id,
        "daemon": _probe_lms_daemon(lms_bin),
        "server": probe_server_models(api_url, model_id=model_id, timeout_s=3.0),
        "hardware": _read_hw_counters(),
        "telemetry": summarize_usage_telemetry(),
        "auto_max_eta_seconds": AUTO_MAX_ETA_SECONDS,
        "default_max_eta_seconds": DEFAULT_MAX_ETA_SECONDS,
    }


def _control_load(api_url: str, model_id: str, profile: str, lms_bin: Path, cfg_path: Path) -> dict[str, Any]:
    srv = probe_server_models(api_url, model_id=model_id, timeout_s=3.0)
    if not srv["reachable"]:
        raise RuntimeError(
            f"Bionic HTTP server unreachable at {api_url}; run 'control start-headless --user-confirmed' first ({srv['error']})"
        )
    target_ctx = CONTROL_PROFILES[profile]["context_length"]
    cfg_payload = build_concrete_model_config(profile)
    cfg_path.parent.mkdir(parents=True, exist_ok=True)
    cfg_path.write_text(json.dumps(cfg_payload, indent=2) + "\n", encoding="utf-8")

    if srv["target_model_loaded"] and srv["loaded_context_length"] == target_ctx:
        return {
            "schema_version": SCHEMA_VERSION,
            "action": "load",
            "profile": profile,
            "already_loaded": True,
            "reloaded": False,
            "concrete_config_path": str(cfg_path),
            "server": srv,
            "hardware": _read_hw_counters(),
        }

    if srv["target_model_loaded"]:
        ul = _run_lms_cmd(lms_bin, ["unload", model_id], timeout_s=30.0)
        if ul.returncode != 0:
            raise RuntimeError(f"lms unload failed before reload: {ul.stderr.strip() or ul.stdout.strip()}")

    ld = _run_lms_cmd(lms_bin, ["load", model_id, "--identifier", model_id, "-y"], timeout_s=180.0)
    if ld.returncode != 0:
        raise RuntimeError(f"lms load failed (exit {ld.returncode}): {ld.stderr.strip() or ld.stdout.strip()}")

    after = probe_server_models(api_url, model_id=model_id, timeout_s=5.0)
    if not after["target_model_loaded"]:
        raise RuntimeError(f"Model {model_id} not reported loaded after lms load: {after}")
    return {
        "schema_version": SCHEMA_VERSION,
        "action": "load",
        "profile": profile,
        "already_loaded": False,
        "reloaded": True,
        "concrete_config_path": str(cfg_path),
        "server": after,
        "hardware": _read_hw_counters(),
    }


def _control_start_headless(
    api_url: str,
    model_id: str,
    profile: str,
    lms_bin: Path,
    appimage_path: Path,
    cfg_path: Path,
) -> dict[str, Any]:
    daemon = _probe_lms_daemon(lms_bin)
    if not daemon["running"]:
        up = _run_lms_cmd(lms_bin, ["daemon", "up", "--json"], timeout_s=30.0)
        daemon = _probe_lms_daemon(lms_bin)
        if not daemon["running"] and appimage_path.is_file() and _has_gui_display_socket():
            subprocess.Popen(
                [str(appimage_path), "--run-as-service"],
                cwd=_safe_subprocess_cwd(),
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True,
            )
            deadline = time.monotonic() + 12.0
            while time.monotonic() < deadline:
                time.sleep(0.5)
                daemon = _probe_lms_daemon(lms_bin)
                if daemon["running"]:
                    break
        if not daemon["running"]:
            err = (up.stderr or up.stdout or daemon["summary"]).strip()
            raise RuntimeError(f"Failed to start Bionic headless daemon: {err}")

    srv = probe_server_models(api_url, model_id=model_id, timeout_s=2.0)
    if not srv["reachable"]:
        port = urllib.parse.urlparse(api_url).port or 1234
        st = _run_lms_cmd(lms_bin, ["server", "start", "--bind", "127.0.0.1", "--port", str(port)], timeout_s=20.0)
        if st.returncode != 0:
            raise RuntimeError(f"lms server start failed: {st.stderr.strip() or st.stdout.strip()}")
        deadline = time.monotonic() + 8.0
        while time.monotonic() < deadline:
            srv = probe_server_models(api_url, model_id=model_id, timeout_s=2.0)
            if srv["reachable"]:
                break
            time.sleep(0.25)
        if not srv["reachable"]:
            raise RuntimeError(f"Bionic server failed to answer at {api_url} after lms server start")

    loaded = _control_load(api_url, model_id, profile, lms_bin, cfg_path)
    loaded["action"] = "start-headless"
    loaded["daemon"] = _probe_lms_daemon(lms_bin)
    return loaded


def _control_unload(api_url: str, model_id: str, lms_bin: Path) -> dict[str, Any]:
    pre = probe_server_models(api_url, model_id=model_id, timeout_s=3.0)
    ul = _run_lms_cmd(lms_bin, ["unload", model_id], timeout_s=30.0)
    if ul.returncode != 0 and pre["target_model_loaded"]:
        raise RuntimeError(f"lms unload failed: {ul.stderr.strip() or ul.stdout.strip()}")
    deadline = time.monotonic() + 5.0
    after = pre
    while time.monotonic() < deadline:
        after = probe_server_models(api_url, model_id=model_id, timeout_s=2.0)
        if not after["reachable"] or not after["target_model_loaded"]:
            break
        time.sleep(0.2)
    return {
        "schema_version": SCHEMA_VERSION,
        "action": "unload",
        "model": model_id,
        "was_loaded": pre["target_model_loaded"],
        "server": after,
        "hardware": _read_hw_counters(),
    }


def _control_stop_server(api_url: str, model_id: str, lms_bin: Path) -> dict[str, Any]:
    _run_lms_cmd(lms_bin, ["unload", "--all"], timeout_s=30.0)
    st = _run_lms_cmd(lms_bin, ["server", "stop"], timeout_s=20.0)
    after = probe_server_models(api_url, model_id=model_id, timeout_s=2.0)
    if st.returncode != 0 and after["reachable"]:
        raise RuntimeError(f"lms server stop failed: {st.stderr.strip() or st.stdout.strip()}")
    return {
        "schema_version": SCHEMA_VERSION,
        "action": "stop-server",
        "server": after,
        "hardware": _read_hw_counters(),
    }


def _normalize_control_cli_action(action: str) -> str:
    norm = action.strip()
    aliases = {"load_profile": "load", "load-profile": "load"}
    return aliases.get(norm, norm)


def cmd_control(args: argparse.Namespace) -> int:
    action_norm = _normalize_control_cli_action(args.action)
    api_url = validate_loopback_url(args.api_url or resolve_default_api_url())
    lms_bin = Path(getattr(args, "lms_bin", str(DEFAULT_LMS_BIN)))
    cfg_path = Path(getattr(args, "concrete_cfg_path", str(DEFAULT_CONCRETE_CFG_PATH)))
    appimage_path = DEFAULT_APPIMAGE_PATH

    if action_norm == "status":
        res = _control_status(api_url, args.model, lms_bin)
        if args.json:
            print(json.dumps(res, indent=2))
        else:
            srv = res["server"]
            hw = res["hardware"]
            print(
                f"Daemon running={res['daemon']['running']} | Server reachable={srv['reachable']} | "
                f"Target loaded={srv['target_model_loaded']} (ctx={srv['loaded_context_length']}) | "
                f"VRAM={hw['vram_used_gib']} GiB"
            )
        return 0

    if not getattr(args, "user_confirmed", False):
        raise SidecarFirewallError(
            f"[USER_CONFIRMATION_REQUIRED] Mutating action 'control {action_norm}' refuses autonomous "
            "VRAM/process changes without explicit user approval (--user-confirmed)."
        )

    if getattr(args, "dry_run", False):
        plan = _control_plan(action_norm, args.profile, args.model, lms_bin, cfg_path, api_url)
        print(json.dumps(plan, indent=2) if args.json else f"[DRY_RUN_OK] control {action_norm} profile={args.profile}")
        return 0

    if action_norm == "start-headless":
        res = _control_start_headless(api_url, args.model, args.profile, lms_bin, appimage_path, cfg_path)
    elif action_norm == "load":
        res = _control_load(api_url, args.model, args.profile, lms_bin, cfg_path)
    elif action_norm == "unload":
        res = _control_unload(api_url, args.model, lms_bin)
    elif action_norm == "stop-server":
        res = _control_stop_server(api_url, args.model, lms_bin)
    else:  # pragma: no cover
        raise ValueError(f"Unsupported control action: {args.action}")

    print(json.dumps(res, indent=2) if args.json else f"[OK] control {action_norm} completed.")
    return 0


def run_self_tests() -> dict[str, Any]:
    """Deterministic offline unit suite validating firewalls, ETA circuit breaker, staging, and control."""
    checks: list[str] = []

    # 1. Loopback allow / reject
    assert validate_loopback_url("http://127.0.0.1:1234/v1") == "http://127.0.0.1:1234/v1"
    assert validate_loopback_url("http://localhost:1234/v1") == "http://localhost:1234/v1"
    for bad_url in (
        "http://192.168.1.25:1234/v1",
        "https://127.0.0.1:1234/v1",
        "http://user:pass@127.0.0.1:1234/v1",
        "http://127.0.0.1:2375/v1",
        "http://127.0.0.1/v1",
        "http://127.0.0.1:99999/v1",
    ):
        try:
            validate_loopback_url(bad_url)
            raise AssertionError(f"Expected firewall block on {bad_url}")
        except SidecarFirewallError:
            pass
    checks.append("loopback_url_firewall")

    # 2. Secret, mcp_config, NetCom, CAD, and repo-escape firewalls
    cad_suffix = "." + "st" + "ep"
    stl_suffix = "." + "st" + "l"
    blocked_samples = [
        Path("/tmp/test.env"),
        Path("/tmp/.env.local"),
        Path("/tmp/.netrc"),
        Path("/tmp/secrets.yaml"),
        Path("/tmp/token.txt"),
        Path("/home/orin/.ssh/id_ed25519"),
        Path("/tmp/client_secret_123.json"),
        Path("/home/orin/.gemini/config/mcp_config.json"),
        Path("/tmp/lms-key-2"),
        Path("/tmp/cloud-account.json"),
        Path("/home/orin/Projects/NetCom/notes.md"),
        Path(f"/tmp/housing{cad_suffix}"),
        Path(f"/tmp/carriage{stl_suffix}"),
    ]
    for sample in blocked_samples:
        try:
            validate_input_paths([sample], repo_root=None, require_exists=False)
            raise AssertionError(f"Expected firewall block on {sample}")
        except SidecarFirewallError:
            pass
    with tempfile.TemporaryDirectory() as td:
        td_p = Path(td)
        repo_a = td_p / "RepoA"
        repo_b = td_p / "RepoB"
        repo_a.mkdir()
        repo_b.mkdir()
        (repo_b / "secret.md").write_text("hi\n", encoding="utf-8")
        esc_link = repo_a / "escape.md"
        esc_link.symlink_to(repo_b / "secret.md")
        try:
            validate_input_paths([esc_link], repo_root=repo_a, require_exists=True)
            raise AssertionError("Expected 4C symlink escape block")
        except SidecarFirewallError:
            pass
    checks.append("input_path_secret_cad_4c_firewall")

    # 3. Staging directory firewall & scratch staging + py_compile + unified diff
    for bad_stage in (
        Path("/home/orin/Projects/Alchemical3D/Homunculus/scripts"),
        Path("/home/orin/Projects/Engineering/scripts"),
        Path("/home/orin/.lmstudio"),
        Path("/home/orin"),
        Path(tempfile.gettempdir()),
    ):
        try:
            validate_staging_dir(bad_stage)
            raise AssertionError(f"Expected staging block on {bad_stage}")
        except SidecarFirewallError:
            pass

    with tempfile.TemporaryDirectory() as td:
        td_p = Path(td)
        orig = td_p / "orig.py"
        orig.write_text("def add(a: int, b: int) -> int:\n    return a + b\n", encoding="utf-8")
        stage_dir = td_p / "stage"
        receipt = stage_code_artifact(
            staging_dir=stage_dir,
            target_filename="orig.py",
            generated_text="```python\ndef add(a: int, b: int) -> int:\n    return a + b + 0\n```\n",
            compare_against=orig,
            telemetry={"mock": True},
        )
        assert receipt["py_compile_ok"] is True
        assert receipt["diff_lines"] > 0
        assert Path(receipt["diff_file"]).is_file()
        checks.append("staging_isolation_py_compile_diff")

        assert (stage_dir.stat().st_mode & 0o777) == 0o700
        for p_check in (
            Path(receipt["staged_file"]),
            Path(receipt["diff_file"]),
            stage_dir / "orig.py.receipt.json",
        ):
            assert (p_check.stat().st_mode & 0o777) == 0o600
        sym_path = stage_dir / "sym.py"
        sym_path.symlink_to(orig)
        try:
            stage_code_artifact(
                staging_dir=stage_dir,
                target_filename="sym.py",
                generated_text="x = 1\n",
            )
            raise AssertionError("Expected symlink target block in staging")
        except SidecarFirewallError:
            pass
        checks.append("staging_0700_0600_and_symlink_rejection")

    # 4. Calibrated ETA circuit breaker (60s auto vs 90s explicit)
    eta_auto_trip = estimate_eta(
        mode="fast",
        prompt_bytes=0,
        prompt_tokens_override=20693,
        max_tokens=2025,
        max_eta_seconds=AUTO_MAX_ETA_SECONDS,
    )
    assert eta_auto_trip["tripped"] and eta_auto_trip["predicted_eta_s"] > 60.0
    eta_exp_ok = estimate_eta(
        mode="fast",
        prompt_bytes=0,
        prompt_tokens_override=20693,
        max_tokens=2025,
        max_eta_seconds=DEFAULT_MAX_ETA_SECONDS,
    )
    assert not eta_exp_ok["tripped"] and eta_exp_ok["verdict"] == "RUN_LOCALLY"
    eta_trip = estimate_eta(mode="deep", prompt_bytes=0, prompt_tokens_override=38000, max_tokens=2500, max_eta_seconds=90.0)
    assert eta_trip["tripped"] and eta_trip["verdict"] == "HANDOFF_TO_MAIN_THREAD"
    eta_cpu_trip = estimate_eta(mode="cpu-bg", prompt_bytes=0, prompt_tokens_override=12000, max_tokens=300, max_eta_seconds=300.0)
    assert eta_cpu_trip["tripped"]
    checks.append("eta_circuit_breaker_calibration")

    # 5. Ephemeral loopback HTTP probe for /api/v0/models loaded vs not-loaded + anti-JIT & cpu-bg auto-clamp
    mock_rows: list[dict[str, Any]] = [
        {"id": DEFAULT_MODEL_ID, "state": "not-loaded"},
        {"id": "text-embedding-nomic-embed-text-v1.5", "state": "loaded"},
    ]
    post_calls = 0

    class _MockModelsHandler(http.server.BaseHTTPRequestHandler):
        def do_GET(self) -> None:  # noqa: N802
            if self.path == "/api/v0/models":
                body = json.dumps({"data": mock_rows, "object": "list"}).encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
            else:
                self.send_response(404)
                self.end_headers()

        def do_POST(self) -> None:  # noqa: N802
            nonlocal post_calls
            if self.path == "/v1/chat/completions":
                length = int(self.headers.get("Content-Length") or 0)
                if length:
                    self.rfile.read(length)
                post_calls += 1
                body = json.dumps(
                    {
                        "id": "mock",
                        "model": DEFAULT_MODEL_ID,
                        "choices": [{"index": 0, "message": {"role": "assistant", "content": "ok"}, "finish_reason": "stop"}],
                        "usage": {"prompt_tokens": 10, "completion_tokens": 2},
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

    srv = http.server.HTTPServer(("127.0.0.1", 0), _MockModelsHandler)
    srv_thread = threading.Thread(target=srv.serve_forever, daemon=True)
    srv_thread.start()
    old_custom_port = os.environ.get("BIONIC_ALLOW_CUSTOM_LOOPBACK_PORT")
    os.environ["BIONIC_ALLOW_CUSTOM_LOOPBACK_PORT"] = "1"
    try:
        mock_api = f"http://127.0.0.1:{srv.server_port}/v1"
        unloaded_probe = probe_server_models(mock_api, model_id=DEFAULT_MODEL_ID, timeout_s=2.0)
        assert unloaded_probe["reachable"] is True
        assert unloaded_probe["target_model_loaded"] is False
        assert DEFAULT_MODEL_ID in unloaded_probe["downloaded_unloaded_models"]
        assert unloaded_probe["loaded_models"] == ["text-embedding-nomic-embed-text-v1.5"]

        try:
            invoke_chat_completion(
                api_url=mock_api,
                model_id=DEFAULT_MODEL_ID,
                mode="fast",
                system_prompt="sys",
                user_content="hello",
                max_tokens=32,
                timeout_s=2.0,
            )
            raise AssertionError("Expected BIONIC_UNLOADED_CONFIRMATION_REQUIRED block")
        except SidecarFirewallError as exc:
            assert "BIONIC_UNLOADED_CONFIRMATION_REQUIRED" in str(exc)
        assert post_calls == 0

        mock_rows[0] = {"id": DEFAULT_MODEL_ID, "state": "loaded", "loaded_context_length": 16384}
        _, clamped_mode = preflight_live_inference(mock_api, DEFAULT_MODEL_ID, "fast")
        assert clamped_mode == "cpu-bg"

        mock_rows[0] = {"id": DEFAULT_MODEL_ID, "state": "loaded", "loaded_context_length": 49152}
        loaded_probe = probe_server_models(mock_api, model_id=DEFAULT_MODEL_ID, timeout_s=2.0)
        assert loaded_probe["target_model_loaded"] is True
        assert loaded_probe["loaded_context_length"] == 49152
        _, daily_mode = preflight_live_inference(mock_api, DEFAULT_MODEL_ID, "fast")
        assert daily_mode == "fast"
    finally:
        if old_custom_port is None:
            os.environ.pop("BIONIC_ALLOW_CUSTOM_LOOPBACK_PORT", None)
        else:
            os.environ["BIONIC_ALLOW_CUSTOM_LOOPBACK_PORT"] = old_custom_port
        srv.shutdown()
        srv.server_close()
    checks.append("api_v0_models_loaded_vs_unloaded_probe")
    checks.append("anti_jit_unloaded_inference_block_and_cpu_bg_autoclamp")

    # 6. Control confirmation gate & dry-run plan validation
    ns_unconf = argparse.Namespace(
        api_url=DEFAULT_API_URL,
        model=DEFAULT_MODEL_ID,
        action="start-headless",
        profile="gpu-daily",
        user_confirmed=False,
        dry_run=True,
        json=True,
    )
    try:
        cmd_control(ns_unconf)
        raise AssertionError("Expected USER_CONFIRMATION_REQUIRED block")
    except SidecarFirewallError:
        pass
    dry = _control_plan("start-headless", "gpu-daily", DEFAULT_MODEL_ID, DEFAULT_LMS_BIN, DEFAULT_CONCRETE_CFG_PATH, DEFAULT_API_URL)
    assert dry["status"] == "DRY_RUN_OK"
    assert dry["concrete_config"]["preset"] == "Qwen3.6-35B-Fast-Sweep"
    assert len(dry["planned_commands"]) == 3
    checks.append("control_confirmation_and_dry_run")

    # 7. /v1/models 404 fail-closed + unknown loaded_context_length cpu-bg auto-clamp
    v1_mode = {"fallback": True}

    class _FallbackModelsHandler(http.server.BaseHTTPRequestHandler):
        def do_GET(self) -> None:  # noqa: N802
            if not v1_mode["fallback"] and self.path == "/api/v0/models":
                body = json.dumps({"data": [{"id": DEFAULT_MODEL_ID, "state": "loaded"}]}).encode("utf-8")
                self.send_response(200)
            elif v1_mode["fallback"] and self.path == "/v1/models":
                body = json.dumps({"data": [{"id": DEFAULT_MODEL_ID}]}).encode("utf-8")
                self.send_response(200)
            else:
                self.send_response(404)
                self.end_headers()
                return
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, _fmt: str, *_args: Any) -> None:
            return

    srv_fb = http.server.HTTPServer(("127.0.0.1", 0), _FallbackModelsHandler)
    th_fb = threading.Thread(target=srv_fb.serve_forever, daemon=True)
    th_fb.start()
    old_fb_port = os.environ.get("BIONIC_ALLOW_CUSTOM_LOOPBACK_PORT")
    os.environ["BIONIC_ALLOW_CUSTOM_LOOPBACK_PORT"] = "1"
    try:
        fb_api = f"http://127.0.0.1:{srv_fb.server_port}/v1"
        fb_probe = probe_server_models(fb_api, model_id=DEFAULT_MODEL_ID, timeout_s=2.0)
        assert fb_probe["target_model_loaded"] is False
        v1_mode["fallback"] = False
        _, unknown_ctx_mode = preflight_live_inference(fb_api, DEFAULT_MODEL_ID, "fast")
        assert unknown_ctx_mode == "cpu-bg"
    finally:
        if old_fb_port is None:
            os.environ.pop("BIONIC_ALLOW_CUSTOM_LOOPBACK_PORT", None)
        else:
            os.environ["BIONIC_ALLOW_CUSTOM_LOOPBACK_PORT"] = old_fb_port
        srv_fb.shutdown()
        srv_fb.server_close()
    checks.append("v1_models_404_fail_closed_and_unknown_ctx_clamp")

    # 8. Control CLI load_profile alias parity
    ns_alias = build_parser().parse_args(
        ["control", "load_profile", "--profile", "cpu-bg", "--user-confirmed", "--dry-run", "--json"]
    )
    assert ns_alias.action == "load_profile"
    plan_alias = _control_plan(
        ns_alias.action, "cpu-bg", DEFAULT_MODEL_ID, DEFAULT_LMS_BIN, DEFAULT_CONCRETE_CFG_PATH, DEFAULT_API_URL
    )
    assert plan_alias["action"] == "load"
    assert len(plan_alias["planned_commands"]) == 1

    import contextlib
    import io

    ns_pre_flag = build_parser().parse_args(["--api-url", "http://127.0.0.1:2375/v1", "control", "status", "--json"])
    assert ns_pre_flag.api_url == "http://127.0.0.1:2375/v1"
    with contextlib.redirect_stderr(io.StringIO()):
        assert main(["--api-url", "http://127.0.0.1:2375/v1", "control", "status", "--json"]) == EXIT_SECURITY_FIREWALL
    checks.append("control_load_profile_alias_parity")

    # 9. Unlinked process cwd resilience across lms probes, subprocesses, and relative paths
    with tempfile.TemporaryDirectory() as td:
        td_p = Path(td)
        gone_dir = td_p / "deleted_plugin_cwd"
        gone_dir.mkdir()
        fake_lms = td_p / "fake_lms"
        fake_lms.write_text('#!/bin/sh\npwd >/dev/null && echo "Bionic v1.2.0 is running"\n', encoding="utf-8")
        os.chmod(fake_lms, 0o755)
        try:
            orig_cwd = os.getcwd()
        except OSError:
            orig_cwd = _safe_subprocess_cwd()
        try:
            os.chdir(gone_dir)
            try:
                gone_dir.rmdir()
                unlinked_ok = True
            except OSError:
                unlinked_ok = False
            if unlinked_ok:
                assert _probe_lms_daemon(fake_lms)["running"] is True
                assert _run_lms_cmd(fake_lms, ["status"]).returncode == 0
                assert _inspect_path_security(Path("relative_doc.md")) is None
        finally:
            os.chdir(orig_cwd)
    checks.append("unlinked_cwd_lms_and_path_resilience")

    return {
        "schema_version": SCHEMA_VERSION,
        "status": "PASS",
        "tests_run": len(checks),
        "checks": checks,
    }


def build_parser() -> argparse.ArgumentParser:
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--api-url", default=None)
    common.add_argument("--model", default=DEFAULT_MODEL_ID)
    common.add_argument("--system-prompt", default=str(DEFAULT_SYSTEM_PROMPT_PATH))
    common.add_argument("--json", action="store_true")

    common_sub = argparse.ArgumentParser(add_help=False)
    common_sub.add_argument("--api-url", default=argparse.SUPPRESS)
    common_sub.add_argument("--model", default=argparse.SUPPRESS)
    common_sub.add_argument("--system-prompt", default=argparse.SUPPRESS)
    common_sub.add_argument("--json", action="store_true", default=argparse.SUPPRESS)

    parser = argparse.ArgumentParser(
        description="Homunculus LM Studio Bionic Local Sidecar Bridge",
        parents=[common],
    )
    parser.add_argument("--self-test", action="store_true", help="Run deterministic offline self-test suite")
    sub = parser.add_subparsers(dest="cmd", required=False)

    sub.add_parser("status", parents=[common_sub], help="Inspect loopback endpoint & loaded Bionic model")
    sub.add_parser("self-test", parents=[common_sub], help="Run deterministic offline self-test suite")

    def add_eta_args(p: argparse.ArgumentParser) -> None:
        p.add_argument("--mode", choices=tuple(PROFILES.keys()), default="fast")
        p.add_argument("--invocation-tier", choices=("auto", "explicit"), default="explicit")
        p.add_argument("--prompt", default=None)
        p.add_argument("--prompt-file", default=None)
        p.add_argument("--context-file", dest="context_files", action="append", default=[])
        p.add_argument("--repo", default=None)
        p.add_argument("--include-git-diff", action="store_true")
        p.add_argument("--max-tokens", type=int, default=None)
        p.add_argument("--max-eta-seconds", type=float, default=None)
        p.add_argument("--expected-turns", type=int, default=1)
        p.add_argument("--force-slow", action="store_true")

    p_eta = sub.add_parser("check-eta", parents=[common_sub], help="Evaluate ETA circuit breaker offline")
    add_eta_args(p_eta)
    p_eta.add_argument("--prompt-tokens", type=int, default=None)

    p_query = sub.add_parser("query", parents=[common_sub], help="Run bounded local sidecar inference")
    add_eta_args(p_query)

    p_quar = sub.add_parser("audit-to-quarantine", parents=[common_sub], help="Run local audit -> memory_gateway quarantine-note")
    add_eta_args(p_quar)
    p_quar.add_argument("--homunculus-root", default=str(DEFAULT_HOMUNCULUS_ROOT))
    p_quar.add_argument("--memory-root", default=str(DEFAULT_MEMORY_ROOT))
    p_quar.add_argument("--project", required=True)
    p_quar.add_argument("--name", required=True)
    p_quar.add_argument("--title", required=True)
    p_quar.add_argument("--reason", required=True)
    p_quar.add_argument("--overwrite", action="store_true")

    p_stage = sub.add_parser("stage-code", parents=[common_sub], help="Stage code draft in scratch/ + py_compile + unified diff")
    add_eta_args(p_stage)
    p_stage.add_argument("--staging-dir", default=str(DEFAULT_STAGING_DIR))
    p_stage.add_argument("--target-filename", required=True)
    p_stage.add_argument("--compare-against", default=None)

    p_ctrl = sub.add_parser("control", parents=[common_sub], help="Inspect or safely manage headless Bionic lifecycle")
    p_ctrl.add_argument(
        "action",
        choices=("status", "start-headless", "load", "load_profile", "load-profile", "unload", "stop-server"),
    )
    p_ctrl.add_argument("--profile", choices=tuple(CONTROL_PROFILES.keys()), default="gpu-daily")
    p_ctrl.add_argument("--user-confirmed", action="store_true")
    p_ctrl.add_argument("--dry-run", action="store_true")

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        if args.self_test or args.cmd == "self-test":
            res = run_self_tests()
            print(json.dumps(res, indent=2) if args.json else f"[PASS] {res['tests_run']} self-tests passed: {', '.join(res['checks'])}")
            return 0
        if not args.cmd:
            parser.print_help()
            return 2

        dispatch = {
            "status": cmd_status,
            "check-eta": cmd_check_eta,
            "query": cmd_query,
            "audit-to-quarantine": cmd_audit_to_quarantine,
            "stage-code": cmd_stage_code,
            "control": cmd_control,
        }
        return dispatch[args.cmd](args)
    except SidecarFirewallError as exc:
        print(str(exc), file=sys.stderr)
        return EXIT_SECURITY_FIREWALL
    except SidecarEtaTrippedError as exc:
        print(str(exc), file=sys.stderr)
        if getattr(args, "json", False):
            print(json.dumps(exc.estimate, indent=2))
        return EXIT_ETA_TRIPPED
    except Exception as exc:  # pragma: no cover - fail-closed surface
        print(f"[SIDECAR_ERROR] {exc}", file=sys.stderr)
        return EXIT_RUNTIME_ERROR


if __name__ == "__main__":
    raise SystemExit(main())
