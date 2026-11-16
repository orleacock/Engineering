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
  CLI Flags     : --api-url, --model, --system-prompt, --json, --self-test, --prompt-tokens, --homunculus-root, --memory-root, --project, --name, --title, --reason, --overwrite, --staging-dir, --target-filename, --compare-against, action, --profile, --user-confirmed, --dry-run, --epoch-label, --no-archive, --job-file, --job-id, --wait-seconds, --timeout-seconds, --limit, --call-id, --verdict, --note, --effort, --mode, --invocation-tier, --prompt, --prompt-file, --context-file, --repo, --include-git-diff, --max-tokens, --max-eta-seconds, --expected-turns, --force-slow
                  status, check-eta, query, audit-to-quarantine, stage-code, control, self-test
  Symbol Index  (jump directly via read_file StartLine/EndLine):
    - def resolve_effort_and_mode (#L258-L270)       | def parse_context_spec (#L273-L283)
    - class SidecarFirewallError (#L286-L287)        | class SidecarEtaTrippedError (#L290-L295)
    - def load_system_prompt (#L298-L309)            | def validate_loopback_url (#L312-L340)
    - def _safe_subprocess_cwd (#L343-L366)          | def _safe_abspath (#L369-L375)
    - def _is_path_within (#L378-L383)               | def _inspect_path_security (#L386-L416)
    - def _find_git_toplevel (#L419-L425)            | def is_code_heavy_payload (#L428-L432)
    - def parse_and_validate_context_items (#L435-L462) | def parse_and_validate_context_specs (#L465-L477)
    - def validate_input_paths (#L480-L529)          | def validate_staging_dir (#L532-L595)
    - def resolve_effective_max_tokens (#L598-L608)  | def estimate_eta (#L611-L749)
    - def _http_json_request (#L752-L772)            | def _deduplicate_full_context_diff (#L775-L852)
    - def plan_line_preserving_chunks (#L855-L916)   | def pack_chunk_batches (#L919-L971)
    - def assemble_prompt_payload (#L974-L1125)      | def resolve_default_api_url (#L1128-L1130)
    - def _resolve_kv_state_path (#L1133-L1142)      | def _pid_alive (#L1145-L1154)
    - def acquire_kv_budget (#L1158-L1266)           | def has_active_exclusive_kv_slot (#L1269-L1287)
    - def invoke_chat_completion (#L1290-L1455)      | def extract_staged_code (#L1458-L1468)
    - def _read_prompt_arg (#L1471-L1478)            | def resolve_max_eta_seconds (#L1481-L1487)
    - def _resolve_telemetry_log (#L1490-L1496)      | def _resolve_scorecard_path (#L1499-L1508)
    - def _resolve_jobs_dir (#L1511-L1520)           | def _write_private_json_atomic (#L1523-L1541)
    - def _resolve_scorecard_archive_path (#L1544-L1550) | def _seed_counts_from_telemetry (#L1553-L1585)
    - def compute_scorecard_metrics (#L1588-L1621)   | def load_or_init_scorecard (#L1624-L1661)
    - def record_call_outcome (#L1664-L1730)         | def apply_call_verdict (#L1733-L1782)
    - def format_lifetime_scorecard (#L1785-L1803)   | def reset_scorecard (#L1806-L1905)
    - def estimate_quota_savings (#L1908-L1968)      | def record_usage_telemetry (#L1971-L1997)
    - def summarize_usage_telemetry (#L2000-L2044)   | def probe_server_models (#L2047-L2113)
    - def preflight_live_inference (#L2116-L2130)    | def _enforce_eta_or_raise (#L2133-L2218)
    - def cmd_status (#L2221-L2257)                  | def cmd_check_eta (#L2260-L2314)
    - def cmd_query (#L2317-L2459)                   | def cmd_audit_to_quarantine (#L2462-L2658)
    - def _write_private_staging_file (#L2661-L2670) | def stage_code_artifact (#L2673-L2752)
    - def cmd_stage_code (#L2755-L2898)              | def build_concrete_model_config (#L2908-L2997)
    - def _read_hw_counters (#L3000-L3039)           | def _probe_lms_daemon (#L3042-L3059)
    - def _run_lms_cmd (#L3062-L3075)                | def _has_gui_display_socket (#L3078-L3088)
    - def _control_plan (#L3091-L3123)               | def _control_status (#L3126-L3142)
    - def _control_load (#L3145-L3209)               | def _control_start_headless (#L3212-L3268)
    - def _control_unload (#L3271-L3293)             | def _control_stop_server (#L3296-L3310)
    - def _safe_job_file (#L3313-L3323)              | def submit_async_job (#L3326-L3364)
    - def _execute_job_worker (#L3367-L3403)         | def get_job_status (#L3406-L3445)
    - def list_jobs (#L3448-L3466)                   | def _normalize_control_cli_action (#L3469-L3472)
    - def cmd_control (#L3475-L3525)                 | def cmd_job_worker (#L3528-L3529)
    - def cmd_job_status (#L3532-L3535)              | def cmd_job_collect (#L3538-L3541)
    - def cmd_job_wait (#L3544-L3547)                | def cmd_job_list (#L3550-L3553)
    - def cmd_verdict (#L3556-L3559)                 | def run_self_tests (#L3562-L4364)
    - def build_parser (#L4367-L4470)                | def main (#L4473-L4511)
=== END NAVIGATION MAP ===
"""
from __future__ import annotations

import argparse
import ast
import contextlib
import difflib
import fcntl
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
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SCHEMA_VERSION = "LOCAL_SIDECAR_V1"
TELEMETRY_SCHEMA = "SIDECAR_TELEMETRY_V2"
ETA_CALIBRATION_VERSION = "ETA_CAL_V2_4_1"
SCORECARD_SCHEMA = "BIONIC_SCORECARD_V1"
DEFAULT_API_URL = "http://127.0.0.1:1234/v1"
DEFAULT_MODEL_ID = "qwen3.6-35b-a3b"
AUTO_MAX_ETA_SECONDS = 60.0
DEFAULT_MAX_ETA_SECONDS = 90.0
HIGH_EFFORT_SOFT_ETA_SECONDS = 180.0
SLOW_SELF_HEAL_THRESHOLD_S = 45.0
KV_SAFETY_GUARD_TOKENS = 1024
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
DEFAULT_CACHE_DIR = Path.home() / ".cache" / "homunculus_bionic_plugin"
DEFAULT_TELEMETRY_LOG = DEFAULT_CACHE_DIR / "sidecar_usage_telemetry.jsonl"
DEFAULT_SCORECARD_PATH = DEFAULT_CACHE_DIR / "bionic_scorecard.json"
DEFAULT_SCORECARD_ARCHIVE_PATH = DEFAULT_CACHE_DIR / "bionic_scorecard_archive.jsonl"
DEFAULT_KV_STATE_PATH = DEFAULT_CACHE_DIR / "kv_pool_state.json"
DEFAULT_JOBS_DIR = DEFAULT_CACHE_DIR / "jobs"
VRAM_USED_SYSFS = Path("/sys/class/drm/card1/device/mem_info_vram_used")
VRAM_TOTAL_SYSFS = Path("/sys/class/drm/card1/device/mem_info_vram_total")
GTT_USED_SYSFS = Path("/sys/class/drm/card1/device/mem_info_gtt_used")
PROC_MEMINFO_PATH = Path("/proc/meminfo")

EXIT_SECURITY_FIREWALL = 2
EXIT_RUNTIME_ERROR = 3
EXIT_ETA_TRIPPED = 4

LOOPBACK_HOSTS = frozenset({"127.0.0.1", "localhost", "::1"})

HEADLESS_API_SYSTEM_PROMPT = (
    "Homunculus workstation sidecar (Qwen3.6-35B-A3B). "
    "Priority: 1. Accuracy & Truth > 2. Efficiency -> 3. Data Safety > 4. Speed. "
    "Cite ONLY exact existing relative/path#Lstart-Lend (StartLine <= EndLine); "
    "never cite deleted '-' diff lines, never invent (e.g., 0.8mm) examples, "
    "prefix Warning:/Caution: when citing [!WARNING]/[!CAUTION] blocks, "
    "quote verbatim where ambiguous, never expand hardware/fastener acronyms (SHCS/BHCS) "
    "beyond source text, emit [TBD: <specific_missing_variable>] or "
    "[TBD: CONFLICT — <source_A_val> vs <source_B_val>] instead of guessing or writing 'likely', "
    "preserve units on [CALC: ...] with literal source numbers only, "
    "never emit ?affp=/dt_id=/aff_id= or placeholder [label](...) links, "
    "never read/parse .step/.stp/.stl/.3mf/.iges/.fcstd (ZERO_ADHOC_CAD_PARSING), "
    "enforce single-repo 4C scope, never touch secrets/.env*/keys/gmail_mcp/NetCom/NEA_v2/corpus_inbox, "
    "output terse `- ` technical bullets with zero preamble unless prose/code is requested, "
    "and treat outputs as quarantined drafts."
)
FALLBACK_SYSTEM_PROMPT = HEADLESS_API_SYSTEM_PROMPT

CONCISE_HIGH_THINKING_HINT = (
    "\n\n[HIGH-EFFORT EXECUTION DISCIPLINE: Keep internal <think> concise and non-repetitive "
    "(<=600 words: map source anchors once, do NOT re-verify checked lines multiple times, "
    "and leave >=45% of max_tokens for final verified output).]"
)

EFFORT_TIERS = ("standard", "high")
EFFORT_TO_MODE = {"standard": "fast", "high": "deep"}

# Calibrated from V1 baseline + V2.3/V2.4 dogfood telemetry (bionic_benchmark_history.jsonl / sidecar_usage_telemetry.jsonl)
# Deliverable & buffer sizing rationale:
#   - fast (STANDARD): default_max_tokens=2048 eliminates mid-sentence audit clipping at 0 cost when stopped early;
#     empirical decode ~40.5 tok/s, soft prompt warn at 12,000 tok.
#   - deep (HIGH): default_max_tokens=8192 (min floor 4096, cap 10240) prevents <think> empty-completion exhaustion,
#     while prompt-scaled output estimates & concise thinking hints eliminate short-prompt over-prediction;
#   - cpu-bg (STANDARD CPU): default_max_tokens=800; preserves 8,192 tok CPU prefill guard.
PROFILES: dict[str, dict[str, Any]] = {
    "fast": {
        "preset": "Qwen3.6-35B-Fast-Sweep",
        "effort": "standard",
        "pp_tok_s": 890.0,
        "tg_tok_s": 40.5,
        "max_ctx": 49152,
        "prompt_cap": 32768,
        "prompt_warn_tokens": 12000,
        "reasoning_effort": "none",
        "default_max_tokens": 2048,
        "typical_output_tokens": 480,
        "thinking_overhead_tokens": 0,
    },
    "deep": {
        "preset": "Qwen3.6-35B-Deep-Diff",
        "effort": "high",
        "pp_tok_s": 890.0,
        "tg_tok_s": 43.0,
        "max_ctx": 49152,
        "prompt_cap": 36864,
        "prompt_warn_tokens": 24000,
        "reasoning_effort": "high",
        "default_max_tokens": 8192,
        "min_max_tokens": 4096,
        "max_tokens_cap": 10240,
        "typical_output_tokens": 4300,
        "thinking_overhead_tokens": 0,
        "soft_eta_seconds": HIGH_EFFORT_SOFT_ETA_SECONDS,
    },
    "cpu-bg": {
        "preset": "Qwen3.6-35B-CPU-Background",
        "effort": "standard",
        "pp_tok_s": 98.0,
        "tg_tok_s": 17.4,
        "max_ctx": 16384,
        "prompt_cap": 8192,
        "prompt_warn_tokens": 6000,
        "reasoning_effort": "none",
        "default_max_tokens": 800,
        "typical_output_tokens": 300,
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

FENCED_CODE_RE = re.compile(r"```(?:[a-zA-Z0-9_+-]*)\r?\n(.*?)```", re.DOTALL)
UNCLOSED_OPEN_FENCE_RE = re.compile(r"^\s*```(?:[a-zA-Z0-9_+-]*)\r?\n")
CONTEXT_SLICE_RE = re.compile(r"^(?P<path>.+?)#L(?P<start>\d+)(?:-L?(?P<end>\d+))?$", re.IGNORECASE)
CODE_CONTEXT_EXTENSIONS = frozenset(
    {".py", ".json", ".sh", ".cfg", ".toml", ".yaml", ".yml", ".js", ".ts", ".c", ".cpp", ".h", ".diff"}
)


def resolve_effort_and_mode(effort: str | None = None, mode: str | None = None) -> tuple[str, str]:
    """Map effort ('standard'|'high') and legacy mode ('fast'|'deep'|'cpu-bg') cleanly."""
    eff_norm = (effort or "").strip().lower()
    if eff_norm and eff_norm not in EFFORT_TIERS:
        raise ValueError(f"Unsupported effort '{effort}'; expected 'standard' or 'high'.")
    mode_norm = (mode or "").strip().lower()
    if mode_norm and mode_norm not in PROFILES:
        raise ValueError(f"Unsupported mode '{mode}'; expected one of {tuple(PROFILES.keys())}.")
    if mode_norm == "cpu-bg":
        return "standard", "cpu-bg"
    if eff_norm == "high" or mode_norm == "deep":
        return "high", "deep"
    return "standard", "fast"


def parse_context_spec(raw: str | Path) -> tuple[Path, tuple[int, int] | None]:
    """Parse optional `#Lstart-Lend` or `#Lline` slice anchor from a context file specification."""
    raw_str = str(raw).strip()
    m = CONTEXT_SLICE_RE.match(raw_str)
    if not m:
        return Path(raw_str), None
    start = int(m.group("start"))
    end = int(m.group("end") or start)
    if start < 1 or end < start:
        raise ValueError(f"Invalid context line range in '{raw_str}' (expected 1 <= start <= end).")
    return Path(m.group("path")), (start, end)


class SidecarFirewallError(Exception):
    """Raised when loopback, secret, CAD, repo, or staging containment blocks an action."""


class SidecarEtaTrippedError(Exception):
    """Raised when the calibrated ETA circuit breaker hands work back to the main thread."""

    def __init__(self, message: str, estimate: dict[str, Any]) -> None:
        super().__init__(message)
        self.estimate = estimate


def load_system_prompt(prompt_path: Path | None = None) -> tuple[str, str]:
    """Return zero-bloat headless prompt by default, or read an explicit custom prompt path."""
    if prompt_path is None:
        return HEADLESS_API_SYSTEM_PROMPT, "headless_api_v2_3"
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


def _find_git_toplevel(path_obj: Path) -> Path | None:
    """Walk parent directories for .git to detect cross-repo mixing when --repo is omitted."""
    cur = _safe_abspath(path_obj).resolve(strict=False)
    for parent in (cur, *cur.parents):
        if (parent / ".git").exists():
            return parent
    return None


def is_code_heavy_payload(context_files: list[Path], include_git_diff: bool = False) -> bool:
    """Return True when context contains source/config/diff files (~2.80 bytes/token vs 3.45 prose)."""
    if include_git_diff:
        return True
    return any(p.suffix.lower() in CODE_CONTEXT_EXTENSIONS for p in context_files)


def parse_and_validate_context_items(
    specs: list[str | Path],
    repo_root: Path | None = None,
    *,
    require_exists: bool = True,
) -> tuple[list[Path], list[tuple[int, int] | None], dict[Path, tuple[int, int]]]:
    """Validate context specs (`#Lstart-Lend`), preserving distinct same-file slices while deduplicating exact repeats."""
    raw_paths: list[Path] = []
    parsed_slices: list[tuple[int, int] | None] = []
    for spec in specs:
        p_obj, sl = parse_context_spec(spec)
        raw_paths.append(p_obj)
        parsed_slices.append(sl)
    validated = validate_input_paths(raw_paths, repo_root=repo_root, require_exists=require_exists)
    dedup_files: list[Path] = []
    dedup_slices: list[tuple[int, int] | None] = []
    seen_pairs: set[tuple[Path, tuple[int, int] | None]] = set()
    slice_map: dict[Path, tuple[int, int]] = {}
    for res_p, sl in zip(validated, parsed_slices):
        pair = (res_p, sl)
        if pair in seen_pairs:
            continue
        seen_pairs.add(pair)
        dedup_files.append(res_p)
        dedup_slices.append(sl)
        if sl is not None:
            slice_map[res_p] = sl
    return dedup_files, dedup_slices, slice_map


def parse_and_validate_context_specs(
    specs: list[str | Path],
    repo_root: Path | None = None,
    *,
    require_exists: bool = True,
) -> tuple[list[Path], dict[Path, tuple[int, int]]]:
    """Validate context specs (supporting `#Lstart-Lend` slices) and return resolved paths + slice map."""
    dedup_files, _slices, slice_map = parse_and_validate_context_items(
        specs,
        repo_root=repo_root,
        require_exists=require_exists,
    )
    return dedup_files, slice_map


def validate_input_paths(
    paths: list[Path],
    repo_root: Path | None = None,
    *,
    require_exists: bool = True,
) -> list[Path]:
    """Validate context paths against secret/CAD firewalls and single-repo (`4C`) boundaries."""
    resolved_repo: Path | None = None
    if repo_root is not None:
        repo_reason = _inspect_path_security(repo_root)
        if repo_reason:
            raise SidecarFirewallError(f"[SECURITY_FIREWALL_BLOCKED] {repo_reason}")
        resolved_repo = _safe_abspath(repo_root).resolve(strict=False)

    validated: list[Path] = []
    git_roots: set[Path] = set()
    for raw_spec in paths:
        raw_path, _ = parse_context_spec(raw_spec)
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
        if resolved_repo is None:
            raw_abs = _safe_abspath(raw_path)
            anchor_top = _find_git_toplevel(raw_abs.parent)
            if anchor_top is not None and not _is_path_within(resolved, anchor_top):
                raise SidecarFirewallError(
                    f"[SECURITY_FIREWALL_BLOCKED] Single-repo containment (4C): "
                    f"{raw_path} resolves to {resolved}, escaping git repository {anchor_top}"
                )
            g_top = _find_git_toplevel(resolved)
            if g_top is not None:
                git_roots.add(g_top)
        validated.append(resolved)

    if resolved_repo is None and len(git_roots) > 1:
        raise SidecarFirewallError(
            "[SECURITY_FIREWALL_BLOCKED] Single-repo containment (4C): cannot mix files from multiple git "
            f"repositories without explicit boundary: {sorted(str(g) for g in git_roots)}"
        )
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


def resolve_effective_max_tokens(mode: str, requested_max_tokens: int | None) -> int:
    """Resolve output token ceiling, enforcing the 4096-tok HIGH-effort floor against reasoning starvation."""
    prof = PROFILES[mode]
    if requested_max_tokens is None:
        return int(prof["default_max_tokens"])
    val = int(requested_max_tokens)
    min_floor = int(prof.get("min_max_tokens") or 1)
    if val < min_floor:
        val = min_floor
    max_cap = int(prof.get("max_tokens_cap") or val)
    return min(val, max_cap)


def estimate_eta(
    *,
    mode: str,
    prompt_bytes: int,
    max_tokens: int | None = None,
    prompt_tokens_override: int | None = None,
    max_eta_seconds: float = DEFAULT_MAX_ETA_SECONDS,
    expected_turns: int = 1,
    has_code_context: bool = False,
    loaded_ctx_override: int | None = None,
    calibrated_output: bool = False,
    cmd_name: str = "",
    sys_prompt_bytes: int = 0,
    include_git_diff: bool = False,
    target_code_bytes: int = 0,
) -> dict[str, Any]:
    """Compute calibrated prefill + decode ETA and plain-English circuit-breaker verdict."""
    if mode not in PROFILES:
        raise ValueError(f"Unsupported mode: {mode}")
    prof = PROFILES[mode]
    out_budget = resolve_effective_max_tokens(mode, max_tokens) if calibrated_output else int(
        max_tokens if max_tokens is not None else prof["default_max_tokens"]
    )
    thinking_oh = int(prof["thinking_overhead_tokens"])
    turns = max(1, int(expected_turns))
    bytes_per_tok = 2.80 if has_code_context else 3.45

    if prompt_tokens_override is not None:
        est_prompt_tokens = max(0, int(prompt_tokens_override))
    else:
        est_prompt_tokens = max(1, math.ceil(prompt_bytes / bytes_per_tok))

    worst_case_out_tokens = (out_budget + thinking_oh) * turns
    if calibrated_output:
        sys_tok_est = round(sys_prompt_bytes / bytes_per_tok) if sys_prompt_bytes > 0 else 0
        body_tok = max(1, est_prompt_tokens - sys_tok_est)
        if mode == "deep":
            cmd_low = cmd_name.lower()
            if "stage" in cmd_low:
                est_deep_tok = 2600 if (target_code_bytes > 0 and target_code_bytes < 4000) else 4100
            elif est_prompt_tokens < 1200:
                est_deep_tok = 1450
            elif est_prompt_tokens < 3000:
                est_deep_tok = 1550
            elif est_prompt_tokens < 6500:
                est_deep_tok = 2800
            else:
                est_deep_tok = 3950
            single_out = min(out_budget, int(prof["typical_output_tokens"]), max(64, est_deep_tok))
        else:
            if out_budget <= 48:
                single_out = max(6, round(out_budget * 0.20))
            elif out_budget <= 160:
                single_out = round(out_budget * 0.85) if body_tok >= 400 else max(12, round(out_budget * 0.45))
            elif include_git_diff and out_budget >= 1000:
                single_out = min(out_budget, 960)
            else:
                ratio = 0.11 if body_tok < 1000 else 0.16
                base_fast_out = min(int(prof["typical_output_tokens"]), max(65, round(body_tok * ratio)))
                single_out = min(out_budget, base_fast_out)
            cmd_low = cmd_name.lower()
            if "stage" in cmd_low:
                user_body_bytes = max(0, prompt_bytes - sys_prompt_bytes)
                if target_code_bytes > 0:
                    est_patch_tok = max(42, round((target_code_bytes / 2.8) * 1.35) + 20)
                    single_out = min(single_out, est_patch_tok)
                elif prompt_bytes > 0 and user_body_bytes <= 500:
                    single_out = min(single_out, max(55, round(user_body_bytes * 0.32)))
                elif est_prompt_tokens < 2000:
                    single_out = min(single_out, 240)
        est_output_tokens = single_out * turns
        sys_cached_tok = round((sys_prompt_bytes / bytes_per_tok) * 0.80) if sys_prompt_bytes > 0 else 0
        uncached_prompt_tokens = max(1, (est_prompt_tokens - sys_cached_tok)) * turns
        prefill_s = uncached_prompt_tokens / float(prof["pp_tok_s"])
        decode_s = est_output_tokens / float(prof["tg_tok_s"])
        overhead_s = 0.65
    else:
        est_output_tokens = worst_case_out_tokens
        total_prompt_tokens = est_prompt_tokens * turns
        prefill_s = total_prompt_tokens / float(prof["pp_tok_s"])
        decode_s = est_output_tokens / float(prof["tg_tok_s"])
        overhead_s = 0.0

    predicted_eta_s = round(prefill_s + decode_s + overhead_s, 2)
    worst_case_eta_s = round(
        ((est_prompt_tokens * turns) / float(prof["pp_tok_s"])) + (worst_case_out_tokens / float(prof["tg_tok_s"])),
        2,
    )

    model_max_ctx = int(loaded_ctx_override if loaded_ctx_override is not None else prof["max_ctx"])
    effective_ctx_cap = max(1024, model_max_ctx - KV_SAFETY_GUARD_TOKENS)

    hard_reasons: list[str] = []
    soft_reasons: list[str] = []
    if est_prompt_tokens + out_budget + thinking_oh > effective_ctx_cap:
        hard_reasons.append(
            f"Single-turn tokens ({est_prompt_tokens + out_budget + thinking_oh}) exceed "
            f"{mode} safe ctx cap ({effective_ctx_cap}, model max={model_max_ctx})."
        )
    if mode == "cpu-bg" and est_prompt_tokens > int(prof["prompt_cap"]):
        hard_reasons.append(
            f"cpu-bg prompt ({est_prompt_tokens} tok) exceeds 8k CPU guard ({prof['prompt_cap']} tok) — "
            "keeps desktop/browser headroom and avoids >100s CPU prefill."
        )
    if predicted_eta_s > float(max_eta_seconds):
        soft_reasons.append(
            f"Predicted ETA {predicted_eta_s:.1f}s exceeds {float(max_eta_seconds):.1f}s target cutoff."
        )

    all_reasons = [*hard_reasons, *soft_reasons]
    warn_tokens = int(prof.get("prompt_warn_tokens") or prof["prompt_cap"])
    prompt_slice_recommended = est_prompt_tokens > warn_tokens

    return {
        "schema_version": SCHEMA_VERSION,
        "effort": prof.get("effort", "standard"),
        "mode": mode,
        "preset": prof["preset"],
        "reasoning_effort": prof["reasoning_effort"],
        "bytes_per_token_basis": bytes_per_tok,
        "est_prompt_tokens": est_prompt_tokens,
        "est_output_tokens": est_output_tokens,
        "effective_max_tokens": out_budget,
        "expected_turns": turns,
        "pp_tok_s_basis": prof["pp_tok_s"],
        "tg_tok_s_basis": prof["tg_tok_s"],
        "prefill_eta_s": round(prefill_s, 2),
        "decode_eta_s": round(decode_s, 2),
        "predicted_eta_s": predicted_eta_s,
        "worst_case_eta_s": worst_case_eta_s,
        "max_eta_seconds": float(max_eta_seconds),
        "effective_ctx_cap": effective_ctx_cap,
        "prompt_slice_recommended": prompt_slice_recommended,
        "hard_tripped": bool(hard_reasons),
        "soft_eta_exceeded": bool(soft_reasons),
        "tripped": bool(all_reasons),
        "verdict": "HANDOFF_TO_MAIN_THREAD" if all_reasons else "RUN_LOCALLY",
        "reasons": all_reasons,
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


def _deduplicate_full_context_diff(
    diff_text: str,
    full_context_rels: set[str],
    full_context_texts: dict[str, str] | None = None,
) -> str:
    """Strip duplicate '+' lines and unchanged link URLs when full file is already above, preserving changed text."""
    if not diff_text or not full_context_rels:
        return diff_text
    out_lines: list[str] = []
    cur_rel: str | None = None
    dedup_file = False
    new_cursor = 1
    plus_start: int | None = None
    plus_count = 0

    def _flush() -> None:
        nonlocal plus_start, plus_count
        if plus_start is not None and plus_count > 0 and cur_rel is not None:
            end_l = plus_start + plus_count - 1
            out_lines.append(f"+[see verbatim {cur_rel}#L{plus_start}-L{end_l} above]")
        plus_start = None
        plus_count = 0

    for line in diff_text.splitlines():
        if line.startswith("diff --git "):
            _flush()
            dedup_file = False
            cur_rel = None
            out_lines.append(line)
            continue
        if line.startswith("+++ "):
            _flush()
            if line.startswith("+++ b/"):
                cur_rel = Path(line[6:].strip()).as_posix()
                dedup_file = cur_rel in full_context_rels
            else:
                cur_rel = None
                dedup_file = False
            out_lines.append(line)
            continue
        if line.startswith("--- "):
            _flush()
            out_lines.append(line)
            continue
        hunk_m = re.match(r"^@@ -\d+(?:,\d+)? \+(\d+)(?:,(\d+))? @@", line)
        if hunk_m:
            _flush()
            new_cursor = int(hunk_m.group(1))
            out_lines.append(line)
            continue

        if dedup_file:
            if line.startswith("+"):
                if plus_start is None:
                    plus_start = new_cursor
                    plus_count = 1
                else:
                    plus_count += 1
                new_cursor += 1
            elif line.startswith(" "):
                _flush()
                new_cursor += 1
                out_lines.append(line)
            else:
                _flush()
                ctx_body = (full_context_texts or {}).get(cur_rel or "", "")
                if line.startswith("-") and ctx_body:
                    line = re.sub(
                        r"\[([^\]]+)\]\((https?://[^)\s]+)\)",
                        lambda m: f"[{m.group(1)}](=)" if m.group(2) in ctx_body else m.group(0),
                        line,
                    )
                out_lines.append(line)
        else:
            out_lines.append(line)

    _flush()
    return "\n".join(out_lines)


def plan_line_preserving_chunks(
    context_files: list[Path],
    *,
    target_chunk_bytes: int = 15000,
    max_total_bytes: int = 260000,
    max_lines_per_chunk: int = 400,
) -> list[tuple[Path, int, int]]:
    """Split large un-sliced files into contiguous 1..N line chunks aligned near def/class/heading breaks."""
    total_bytes = 0
    for fpath in context_files:
        try:
            total_bytes += fpath.stat().st_size
        except OSError:
            total_bytes += len(fpath.read_text(encoding="utf-8", errors="replace").encode("utf-8"))
    if total_bytes > max_total_bytes:
        raise SidecarEtaTrippedError(
            f"[ETA_CIRCUIT_BREAKER_TRIPPED] Total chunked input ({total_bytes} B) exceeds {max_total_bytes} B safe bound.",
            {
                "reason": "oversize_chunk_total",
                "total_bytes": total_bytes,
                "max_total_bytes": max_total_bytes,
                "tripped": True,
                "hard_tripped": True,
            },
        )

    break_prefixes = ("def ", "async def ", "class ", "# ", "## ", "### ")
    chunks: list[tuple[Path, int, int]] = []
    for fpath in context_files:
        all_lines = fpath.read_text(encoding="utf-8", errors="replace").splitlines()
        n_lines = len(all_lines)
        raw_bytes = len("\n".join(all_lines).encode("utf-8"))
        if n_lines <= min(380, max_lines_per_chunk) and raw_bytes <= target_chunk_bytes:
            chunks.append((fpath, 1, max(1, n_lines)))
            continue

        start_idx = 0
        while start_idx < n_lines:
            acc_bytes = 0
            end_idx = start_idx
            while end_idx < n_lines:
                line_b = len(all_lines[end_idx].encode("utf-8")) + 1
                if end_idx > start_idx and (
                    acc_bytes + line_b > target_chunk_bytes or (end_idx - start_idx) >= max_lines_per_chunk
                ):
                    break
                acc_bytes += line_b
                end_idx += 1

            if end_idx < n_lines:
                best_split: int | None = None
                lo_search = max(start_idx + 1, end_idx - 60)
                for cand in range(end_idx, lo_search - 1, -1):
                    if all_lines[cand].startswith(break_prefixes):
                        best_split = cand
                        break
                if best_split is not None and best_split > start_idx:
                    end_idx = best_split

            chunks.append((fpath, start_idx + 1, end_idx))
            start_idx = end_idx
    return chunks


def pack_chunk_batches(
    chunks: list[tuple[Path, int, int]],
    *,
    max_batch_bytes: int = 20000,
    max_batch_lines: int = 420,
    max_slices_per_batch: int = 4,
) -> list[list[tuple[Path, int, int]]]:
    """Pack distinct-file slices into bounded multi-file mapper batches without colliding per-path slice keys."""
    if not chunks:
        return []

    line_cache: dict[Path, list[str]] = {}

    def _slice_stats(fpath: Path, s_line: int, e_line: int) -> tuple[int, int]:
        lines = line_cache.get(fpath)
        if lines is None:
            lines = fpath.read_text(encoding="utf-8", errors="replace").splitlines()
            line_cache[fpath] = lines
        sub = lines[max(0, s_line - 1) : max(0, e_line)]
        s_bytes = len("\n".join(sub).encode("utf-8"))
        return s_bytes, max(1, len(sub))

    batches: list[list[tuple[Path, int, int]]] = []
    cur_batch: list[tuple[Path, int, int]] = []
    cur_paths: set[Path] = set()
    cur_bytes = 0
    cur_lines = 0

    for fpath, s_line, e_line in chunks:
        sl_bytes, sl_lines = _slice_stats(fpath, s_line, e_line)
        can_pack = (
            bool(cur_batch)
            and fpath not in cur_paths
            and len(cur_batch) < max_slices_per_batch
            and (cur_bytes + sl_bytes) <= max_batch_bytes
            and (cur_lines + sl_lines) <= max_batch_lines
        )
        if can_pack:
            cur_batch.append((fpath, s_line, e_line))
            cur_paths.add(fpath)
            cur_bytes += sl_bytes
            cur_lines += sl_lines
        else:
            if cur_batch:
                batches.append(cur_batch)
            cur_batch = [(fpath, s_line, e_line)]
            cur_paths = {fpath}
            cur_bytes = sl_bytes
            cur_lines = sl_lines

    if cur_batch:
        batches.append(cur_batch)
    return batches


def assemble_prompt_payload(
    *,
    user_prompt: str,
    context_files: list[Path],
    repo_root: Path | None,
    include_git_diff: bool,
    sys_prompt: str,
    slice_ranges: dict[Path, tuple[int, int]] | list[tuple[int, int] | None] | None = None,
    context_slices: list[tuple[int, int] | None] | None = None,
    diff_repo_wide: bool = False,
) -> tuple[str, list[dict[str, Any]]]:
    """Assemble bounded line-numbered (and optionally #Lstart-Lend sliced) files + scoped safe git diff."""
    sections: list[str] = [user_prompt.strip()]
    file_meta: list[dict[str, Any]] = []
    raw_by_path: dict[Path, str] = {}
    lines_by_path: dict[Path, list[str]] = {}
    sliced_paths: set[Path] = set()
    full_context_paths: set[Path] = set()

    if context_slices is not None:
        if len(context_slices) != len(context_files):
            raise ValueError("context_slices length must match context_files length")
        item_pairs = list(zip(context_files, context_slices))
    elif isinstance(slice_ranges, list):
        if len(slice_ranges) != len(context_files):
            raise ValueError("slice_ranges list length must match context_files length")
        item_pairs = list(zip(context_files, slice_ranges))
    else:
        slice_map = slice_ranges or {}
        item_pairs = [(fp, slice_map.get(fp)) for fp in context_files]

    for fpath, sl in item_pairs:
        if fpath not in raw_by_path:
            raw_text = fpath.read_text(encoding="utf-8", errors="replace")
            raw_by_path[fpath] = raw_text
            lines_by_path[fpath] = raw_text.splitlines()
        else:
            raw_text = raw_by_path[fpath]
        all_lines = lines_by_path[fpath]
        rel_display = str(fpath.relative_to(repo_root)) if repo_root else fpath.name
        if sl is not None:
            sliced_paths.add(fpath)
            start_l, end_l = sl
            actual_start = min(max(1, start_l), max(1, len(all_lines)))
            sliced = all_lines[actual_start - 1 : end_l]
            actual_end = actual_start + len(sliced) - 1 if sliced else actual_start
            numbered = "\n".join(f"{idx}: {line}" for idx, line in enumerate(sliced, actual_start))
            slice_bytes = len("\n".join(sliced).encode("utf-8"))
            sections.append(
                f"\n### CONTEXT FILE: {rel_display}#L{actual_start}-L{actual_end} "
                f"({len(sliced)} sliced lines of {len(all_lines)} total)\n{numbered}\n"
            )
            file_meta.append(
                {
                    "path": str(fpath),
                    "label": f"{rel_display}#L{actual_start}-L{actual_end}",
                    "slice": [actual_start, actual_end],
                    "lines": len(sliced),
                    "total_lines": len(all_lines),
                    "bytes": slice_bytes,
                }
            )
        else:
            full_context_paths.add(fpath)
            numbered = "\n".join(f"{idx}: {line}" for idx, line in enumerate(all_lines, 1))
            sections.append(f"\n### CONTEXT FILE: {rel_display} ({len(all_lines)} lines)\n{numbered}\n")
            file_meta.append(
                {
                    "path": str(fpath),
                    "label": rel_display,
                    "lines": len(all_lines),
                    "bytes": len(raw_text.encode("utf-8")),
                }
            )

    if include_git_diff:
        if repo_root is None:
            raise SidecarFirewallError(
                "[SECURITY_FIREWALL_BLOCKED] --include-git-diff requires explicit single-repo --repo boundary (4C)."
            )
        names_proc = subprocess.run(
            ["git", "--no-optional-locks", "-C", str(repo_root), "diff", "--name-only"],
            cwd=_safe_subprocess_cwd(repo_root),
            capture_output=True,
            text=True,
            check=False,
        )
        if names_proc.returncode != 0:
            raise RuntimeError(f"git diff failed in {repo_root}: {names_proc.stderr.strip()}")
        changed_rels = [line.strip() for line in names_proc.stdout.splitlines() if line.strip()]
        scoped_rels: set[str] | None = None
        full_context_rels: set[str] = set()
        full_context_texts: dict[str, str] = {}
        if context_files:
            if not diff_repo_wide:
                scoped_rels = {
                    fpath.relative_to(repo_root).as_posix()
                    for fpath in context_files
                    if _is_path_within(fpath, repo_root)
                }
            for fpath in full_context_paths:
                if fpath not in sliced_paths and _is_path_within(fpath, repo_root):
                    rel_pos = fpath.relative_to(repo_root).as_posix()
                    full_context_rels.add(rel_pos)
                    full_context_texts[rel_pos] = raw_by_path.get(fpath, "")
        safe_rels: list[str] = []
        skipped_unsafe = 0
        skipped_unscoped = 0
        for rel in changed_rels:
            cand = repo_root / rel
            if _inspect_path_security(cand) or not _is_path_within(cand.resolve(strict=False), repo_root):
                skipped_unsafe += 1
                continue
            if scoped_rels is not None and Path(rel).as_posix() not in scoped_rels:
                skipped_unscoped += 1
                continue
            safe_rels.append(rel)

        diff_text = ""
        if safe_rels:
            diff_args = ["git", "--no-optional-locks", "-C", str(repo_root), "diff", "--no-ext-diff"]
            if full_context_rels and {Path(r).as_posix() for r in safe_rels}.issubset(full_context_rels):
                diff_args.append("--unified=0")
            diff_args.extend(["--", *safe_rels])
            diff_proc = subprocess.run(
                diff_args,
                cwd=_safe_subprocess_cwd(repo_root),
                capture_output=True,
                text=True,
                check=False,
            )
            if diff_proc.returncode != 0:
                raise RuntimeError(f"git diff failed in {repo_root}: {diff_proc.stderr.strip()}")
            diff_text = diff_proc.stdout.strip()
            if diff_text and full_context_rels:
                diff_text = _deduplicate_full_context_diff(diff_text, full_context_rels, full_context_texts)

        filter_note = ""
        if skipped_unsafe or skipped_unscoped:
            filter_note = f" [filtered: {skipped_unsafe} blocked secret/CAD, {skipped_unscoped} out-of-scope]"
        if diff_text:
            sections.append(f"\n### GIT WORKING-TREE DIFF ({repo_root.name}{filter_note})\n```diff\n{diff_text}\n```\n")
        else:
            sections.append(
                f"\n### GIT WORKING-TREE DIFF ({repo_root.name}{filter_note})\n(clean/no matching safe unstaged diff)\n"
            )

    full_user_content = "\n".join(s for s in sections if s)
    total_prompt_bytes = len(sys_prompt.encode("utf-8")) + len(full_user_content.encode("utf-8"))
    if total_prompt_bytes < 0:  # pragma: no cover
        raise AssertionError("unreachable")
    return full_user_content, file_meta


def resolve_default_api_url() -> str:
    """Resolve optional loopback API URL override from environment or default."""
    return os.environ.get("BIONIC_SIDECAR_API_URL", "").strip() or DEFAULT_API_URL


def _resolve_kv_state_path(kv_path: Path | None = None) -> Path:
    if kv_path is not None:
        return kv_path
    env_p = os.environ.get("BIONIC_SIDECAR_KV_STATE_PATH", "").strip()
    if env_p:
        return Path(os.path.expanduser(env_p))
    tel_env = os.environ.get("BIONIC_SIDECAR_TELEMETRY_LOG", "").strip()
    if tel_env:
        return Path(os.path.expanduser(tel_env)).parent / "kv_pool_state.json"
    return DEFAULT_KV_STATE_PATH


def _pid_alive(pid: int) -> bool:
    if pid <= 0:
        return False
    try:
        os.kill(pid, 0)
        return True
    except ProcessLookupError:
        return False
    except OSError:
        return True


@contextlib.contextmanager
def acquire_kv_budget(
    est_tokens: int,
    loaded_ctx: int | None = None,
    *,
    timeout_s: float = 90.0,
    kv_state_path: Path | None = None,
    exclusive: bool = False,
):
    """Coordinate concurrent calls against Bionic's shared KV pool using an atomic advisory flock."""
    path = _resolve_kv_state_path(kv_state_path)
    pool_cap = min(35500, max(1024, int((loaded_ctx or 49152) * 0.90)))
    slot_id = f"{os.getpid()}-{uuid.uuid4().hex[:8]}"
    lock_path = path.with_suffix(".lock")
    registered = False
    deadline = time.monotonic() + max(0.05, float(timeout_s))

    slot_ttl = max(660.0, float(timeout_s) + 120.0)

    def _prune_slots(rows: list[Any], now_ts: float) -> list[dict[str, Any]]:
        clean: list[dict[str, Any]] = []
        for r in rows:
            if not isinstance(r, dict):
                continue
            ts_val = float(r.get("ts") or 0.0)
            pid_val = int(r.get("pid") or 0)
            if (now_ts - ts_val) <= slot_ttl and _pid_alive(pid_val):
                clean.append(r)
        return clean

    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        try:
            os.chmod(path.parent, 0o700)
        except OSError:
            pass
        if not (path.parent.is_symlink() or path.is_symlink() or lock_path.is_symlink()):
            while True:
                now_ts = time.time()
                with open(lock_path, "a+", encoding="utf-8") as lfh:
                    fcntl.flock(lfh.fileno(), fcntl.LOCK_EX)
                    try:
                        try:
                            raw_obj = json.loads(path.read_text(encoding="utf-8")) if path.is_file() else {}
                        except (OSError, json.JSONDecodeError):
                            raw_obj = {}
                        slots = _prune_slots(list(raw_obj.get("slots") or []), now_ts)
                        active_tokens = sum(int(s.get("est_tokens") or 0) for s in slots)
                        max_slots = (
                            1
                            if (
                                exclusive
                                or any(bool(s.get("exclusive")) for s in slots)
                                or int(est_tokens) >= 24000
                                or any(int(s.get("est_tokens") or 0) >= 24000 for s in slots)
                            )
                            else 2
                        )
                        if active_tokens == 0 or (len(slots) < max_slots and (active_tokens + int(est_tokens)) <= pool_cap):
                            slots.append(
                                {
                                    "slot_id": slot_id,
                                    "pid": os.getpid(),
                                    "est_tokens": int(est_tokens),
                                    "exclusive": bool(exclusive),
                                    "ts": now_ts,
                                }
                            )
                            flags = os.O_WRONLY | os.O_CREAT | os.O_TRUNC | getattr(os, "O_NOFOLLOW", 0)
                            fd = os.open(path, flags, 0o600)
                            with os.fdopen(fd, "w", encoding="utf-8") as sfh:
                                json.dump({"slots": slots}, sfh)
                            registered = True
                            break
                        if time.monotonic() >= deadline:
                            raise RuntimeError(
                                f"[KV_POOL_CAPACITY_EXCEEDED] Active KV slots ({active_tokens} tok) + requested "
                                f"({int(est_tokens)} tok) exceed pool cap ({pool_cap} tok) after {float(timeout_s):.1f}s."
                            )
                    finally:
                        fcntl.flock(lfh.fileno(), fcntl.LOCK_UN)
                time.sleep(0.2)
    except OSError:
        registered = False

    try:
        yield {"slot_id": slot_id, "pool_cap": pool_cap, "registered": registered}
    finally:
        if registered:
            try:
                with open(lock_path, "a+", encoding="utf-8") as lfh:
                    fcntl.flock(lfh.fileno(), fcntl.LOCK_EX)
                    try:
                        try:
                            raw_obj = json.loads(path.read_text(encoding="utf-8")) if path.is_file() else {}
                        except (OSError, json.JSONDecodeError):
                            raw_obj = {}
                        slots = [
                            s
                            for s in _prune_slots(list(raw_obj.get("slots") or []), time.time())
                            if s.get("slot_id") != slot_id
                        ]
                        flags = os.O_WRONLY | os.O_CREAT | os.O_TRUNC | getattr(os, "O_NOFOLLOW", 0)
                        fd = os.open(path, flags, 0o600)
                        with os.fdopen(fd, "w", encoding="utf-8") as sfh:
                            json.dump({"slots": slots}, sfh)
                    finally:
                        fcntl.flock(lfh.fileno(), fcntl.LOCK_UN)
            except OSError:
                pass


def has_active_exclusive_kv_slot(kv_state_path: Path | None = None) -> bool:
    """Return True if an exclusive or large-context KV slot is currently held by a live worker."""
    path = _resolve_kv_state_path(kv_state_path)
    try:
        if path.parent.is_symlink() or path.is_symlink() or not path.is_file():
            return False
        raw_obj = json.loads(path.read_text(encoding="utf-8"))
        now_ts = time.time()
        for row in list(raw_obj.get("slots") or []):
            if not isinstance(row, dict):
                continue
            ts_val = float(row.get("ts") or 0.0)
            pid_val = int(row.get("pid") or 0)
            if (now_ts - ts_val) <= 660.0 and _pid_alive(pid_val):
                if bool(row.get("exclusive")) or int(row.get("est_tokens") or 0) >= 24000:
                    return True
    except (OSError, json.JSONDecodeError, ValueError):
        return False
    return False


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
    loaded_ctx: int | None = None,
    est_prompt_tokens: int | None = None,
    allow_high_floor: bool = True,
    reasoning_effort_override: str | None = None,
) -> dict[str, Any]:
    """Call OpenAI-compatible loopback endpoint with KV pool coordination and empty-output guard."""
    if not preflight_checked:
        srv, mode = preflight_live_inference(api_url, model_id, mode)
        if loaded_ctx is None:
            loaded_ctx = srv.get("loaded_context_length")
    prof = PROFILES[mode]
    eff_max_tokens = resolve_effective_max_tokens(mode, max_tokens) if allow_high_floor else int(max_tokens)
    est_p = (
        int(est_prompt_tokens)
        if est_prompt_tokens is not None
        else max(1, math.ceil((len(system_prompt.encode("utf-8")) + len(user_content.encode("utf-8"))) / 3.0))
    )

    def _once(
        tok_limit: int,
        *,
        req_content: str = user_content,
        req_reasoning: str | None = None,
        req_est_p: int = est_p,
        req_timeout_s: float | None = None,
    ) -> tuple[dict[str, Any], float]:
        eff_req_timeout = float(req_timeout_s if req_timeout_s is not None else timeout_s)
        eff_reasoning = (
            req_reasoning
            if req_reasoning is not None
            else (reasoning_effort_override if reasoning_effort_override is not None else prof["reasoning_effort"])
        )
        send_content = req_content
        if (
            mode == "deep"
            and eff_reasoning != "none"
            and tok_limit >= 1024
            and req_content == user_content
            and "[HIGH-EFFORT EXECUTION DISCIPLINE:" not in send_content
            and "[Thinking budget note:" not in send_content
        ):
            send_content = send_content + CONCISE_HIGH_THINKING_HINT
        payload = {
            "model": model_id,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": send_content},
            ],
            "temperature": 0.0,
            "max_tokens": tok_limit,
            "reasoning_effort": eff_reasoning,
        }
        use_exclusive_slot = mode == "deep" and eff_reasoning != "none" and tok_limit >= 3072
        kv_wait_s = max(eff_req_timeout * 2.5, 660.0) if mode == "deep" else max(eff_req_timeout * 1.5, 300.0)
        with acquire_kv_budget(
            req_est_p + tok_limit,
            loaded_ctx,
            timeout_s=kv_wait_s,
            exclusive=use_exclusive_slot,
        ):
            t0 = time.perf_counter()
            raw_resp = _http_json_request(f"{api_url}/chat/completions", payload=payload, timeout_s=eff_req_timeout)
            dt_s = round(max(0.001, time.perf_counter() - t0), 3)
        return raw_resp, dt_s

    resp, elapsed_s = _once(eff_max_tokens)
    choice = (resp.get("choices") or [{}])[0]
    msg = choice.get("message") or {}
    content = (msg.get("content") or "").strip()
    usage1 = resp.get("usage") or {}
    total_prompt_tokens = int(usage1.get("prompt_tokens") or 0)
    total_completion_tokens = int(usage1.get("completion_tokens") or 0)
    token_bump_retried = False
    reasoning_recovered = False
    had_reasoning_initial = bool((msg.get("reasoning_content") or "").strip())

    if not content and choice.get("finish_reason") == "length":
        rc_tail = (msg.get("reasoning_content") or "").strip()
        if len(rc_tail) >= 120:
            synth_limit = min(4096, max(2048, eff_max_tokens // 2))
            synth_prompt = (
                f"{user_content}\n\n"
                "[COMPLETED DEEP-REASONING ENGINEERING TRACE FROM PASS 1 — DO NOT RE-THINK FROM SCRATCH; "
                "SYNTHESIZE AND EMIT ONLY THE FINAL VERIFIED OUTPUT OR RAW CODE IMMEDIATELY]:\n"
                f"{rc_tail[-12000:]}\n"
            )
            synth_est_p = max(1, math.ceil((len(system_prompt.encode("utf-8")) + len(synth_prompt.encode("utf-8"))) / 3.0))
            resp2, dt2 = _once(
                synth_limit,
                req_content=synth_prompt,
                req_reasoning="none",
                req_est_p=synth_est_p,
                req_timeout_s=max(float(timeout_s), 120.0),
            )
            elapsed_s = round(elapsed_s + dt2, 3)
            token_bump_retried = True
            usage2 = resp2.get("usage") or {}
            total_prompt_tokens += int(usage2.get("prompt_tokens") or 0)
            total_completion_tokens += int(usage2.get("completion_tokens") or 0)
            choice2 = (resp2.get("choices") or [{}])[0]
            msg2 = choice2.get("message") or {}
            if (msg2.get("content") or "").strip():
                resp, choice, msg = resp2, choice2, msg2
                content = (msg.get("content") or "").strip()
                reasoning_recovered = True
        max_cap = int(prof.get("max_tokens_cap") or 10240)
        if not content and eff_max_tokens < max_cap:
            bump_limit = min(max_cap, max(6144, eff_max_tokens + 2048))
            resp2, dt2 = _once(bump_limit)
            elapsed_s = round(elapsed_s + dt2, 3)
            token_bump_retried = True
            eff_max_tokens = bump_limit
            usage2 = resp2.get("usage") or {}
            total_prompt_tokens += int(usage2.get("prompt_tokens") or 0)
            total_completion_tokens += int(usage2.get("completion_tokens") or 0)
            choice2 = (resp2.get("choices") or [{}])[0]
            msg2 = choice2.get("message") or {}
            if (msg2.get("content") or "").strip():
                resp, choice, msg = resp2, choice2, msg2
                content = (msg.get("content") or "").strip()

    if not content:
        raise RuntimeError(
            "[EMPTY_COMPLETION_TOKEN_EXHAUSTION] Bionic returned empty content "
            f"(finish_reason={choice.get('finish_reason')}, max_tokens={eff_max_tokens})."
        )

    reasoning_content = msg.get("reasoning_content") or ""
    completion_tokens = total_completion_tokens or int((resp.get("usage") or {}).get("completion_tokens") or 0)
    prompt_tokens = total_prompt_tokens or int((resp.get("usage") or {}).get("prompt_tokens") or 0)
    stats = resp.get("stats") or {}
    raw_decode_tps = stats.get("tokens_per_second")
    decode_tok_s = round(float(raw_decode_tps), 2) if raw_decode_tps is not None else None
    wall_tok_s = round(completion_tokens / elapsed_s, 2) if completion_tokens and elapsed_s > 0 else None
    eff_reasoning_out = (
        reasoning_effort_override if reasoning_effort_override is not None else prof["reasoning_effort"]
    )

    return {
        "model": resp.get("model") or model_id,
        "effort": prof.get("effort", "standard"),
        "mode": mode,
        "reasoning_effort": eff_reasoning_out,
        "effective_max_tokens": eff_max_tokens,
        "token_bump_retried": token_bump_retried,
        "reasoning_recovered": reasoning_recovered,
        "elapsed_s": elapsed_s,
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
        "decode_tok_s": decode_tok_s,
        "wall_tok_s": wall_tok_s,
        "observed_tg_tok_s": decode_tok_s or wall_tok_s,
        "finish_reason": choice.get("finish_reason"),
        "reasoning_present": bool(reasoning_content) or had_reasoning_initial,
        "content": content,
    }


def extract_staged_code(raw_content: str) -> str:
    """Extract primary fenced code block (handling truncated unclosed fences cleanly)."""
    match = FENCED_CODE_RE.search(raw_content)
    if match:
        text = match.group(1)
    else:
        stripped = UNCLOSED_OPEN_FENCE_RE.sub("", raw_content.lstrip(), count=1)
        if stripped.rstrip().endswith("```"):
            stripped = stripped.rstrip()[:-3]
        text = stripped
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


def _resolve_scorecard_path(scorecard_path: Path | None = None) -> Path:
    if scorecard_path is not None:
        return scorecard_path
    env_p = os.environ.get("BIONIC_SIDECAR_SCORECARD_PATH", "").strip()
    if env_p:
        return Path(os.path.expanduser(env_p))
    tel_env = os.environ.get("BIONIC_SIDECAR_TELEMETRY_LOG", "").strip()
    if tel_env:
        return Path(os.path.expanduser(tel_env)).parent / "bionic_scorecard.json"
    return DEFAULT_SCORECARD_PATH


def _resolve_jobs_dir(jobs_dir: Path | None = None) -> Path:
    if jobs_dir is not None:
        return jobs_dir
    env_p = os.environ.get("BIONIC_SIDECAR_JOBS_DIR", "").strip()
    if env_p:
        return Path(os.path.expanduser(env_p))
    tel_env = os.environ.get("BIONIC_SIDECAR_TELEMETRY_LOG", "").strip()
    if tel_env:
        return Path(os.path.expanduser(tel_env)).parent / "jobs"
    return DEFAULT_JOBS_DIR


def _write_private_json_atomic(path: Path, obj: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.parent.is_symlink() or path.is_symlink():
        return
    try:
        os.chmod(path.parent, 0o700)
    except OSError:
        pass
    tmp_path = path.with_name(f".{path.name}.{os.getpid()}.{uuid.uuid4().hex[:6]}.tmp")
    flags = os.O_WRONLY | os.O_CREAT | os.O_TRUNC | getattr(os, "O_NOFOLLOW", 0)
    fd = os.open(tmp_path, flags, 0o600)
    with os.fdopen(fd, "w", encoding="utf-8") as fh:
        json.dump(obj, fh, indent=2)
        fh.write("\n")
    os.replace(tmp_path, path)
    try:
        os.chmod(path, 0o600)
    except OSError:
        pass


def _resolve_scorecard_archive_path(
    archive_path: Path | None = None,
    scorecard_path: Path | None = None,
) -> Path:
    if archive_path is not None:
        return archive_path
    return _resolve_scorecard_path(scorecard_path).parent / "bionic_scorecard_archive.jsonl"


def _seed_counts_from_telemetry(log_path: Path) -> dict[str, int]:
    """Derive initial clean/corrected/healed counts from historical telemetry rows without retry double-counting."""
    clean = 0
    corrected = 0
    healed = 0
    rows_seen = 0
    if not log_path.is_file():
        return {"clean": 0, "corrected": 0, "healed": 0, "rows_seen": 0}
    try:
        for raw in log_path.read_text(encoding="utf-8", errors="replace").splitlines():
            if not raw.strip():
                continue
            row = json.loads(raw)
            rows_seen += 1
            if (row.get("tripped") or row.get("finish_reason") == "eta_tripped") and not row.get("http_error") and not row.get("elapsed_s"):
                continue
            cmd_name = str(row.get("cmd") or "")
            if cmd_name.endswith("_retry") or row.get("is_retry") or row.get("synthetic_fault"):
                continue
            verdict = str(row.get("verdict") or "").lower()
            if verdict == "clean":
                clean += 1
            elif verdict == "healed":
                healed += 1
            elif verdict == "corrected" or row.get("http_error"):
                corrected += 1
            elif row.get("finish_reason") == "stop":
                clean += 1
            else:
                corrected += 1
    except (OSError, json.JSONDecodeError):
        pass
    return {"clean": clean, "corrected": corrected, "healed": healed, "rows_seen": rows_seen}


def compute_scorecard_metrics(sc: dict[str, Any]) -> dict[str, Any]:
    """Compute relative percentages and developmental gain/loss vs archived previous epoch."""
    clean = int(sc.get("clean") or 0)
    corrected = int(sc.get("corrected") or 0)
    healed = int(sc.get("healed") or 0)
    total = clean + corrected + healed
    usable = clean + healed
    usable_pct = round(100.0 * usable / total, 1) if total > 0 else 0.0
    clean_pct = round(100.0 * clean / total, 1) if total > 0 else 0.0
    healed_pct = round(100.0 * healed / total, 1) if total > 0 else 0.0
    corrected_pct = round(100.0 * corrected / total, 1) if total > 0 else 0.0
    epoch = str(sc.get("epoch") or "lifetime")
    prev = sc.get("prev_epoch") if isinstance(sc.get("prev_epoch"), dict) else None
    delta_usable: float | None = None
    delta_corr: float | None = None
    if prev is not None and "usable_pct" in prev and total > 0:
        delta_usable = round(usable_pct - float(prev["usable_pct"]), 1)
        if "corrected_pct" in prev:
            delta_corr = round(corrected_pct - float(prev["corrected_pct"]), 1)
    return {
        "epoch": epoch,
        "clean": clean,
        "corrected": corrected,
        "healed": healed,
        "total_calls": total,
        "usable_calls": usable,
        "usable_pct": usable_pct,
        "clean_pct": clean_pct,
        "healed_pct": healed_pct,
        "corrected_pct": corrected_pct,
        "prev_epoch": prev,
        "delta_usable_pct_vs_prev": delta_usable,
        "delta_corrected_pct_vs_prev": delta_corr,
    }


def load_or_init_scorecard(
    scorecard_path: Path | None = None,
    telemetry_log: Path | None = None,
) -> dict[str, Any]:
    """Load or atomically initialize persistent Bionic lifetime clean/corrected/healed scorecard."""
    sc_path = _resolve_scorecard_path(scorecard_path)
    tel_path = _resolve_telemetry_log(telemetry_log)
    seed = _seed_counts_from_telemetry(tel_path)
    default_obj: dict[str, Any] = {
        "schema_version": SCORECARD_SCHEMA,
        "updated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "next_seq": seed["rows_seen"] + 1,
        "clean": seed["clean"],
        "corrected": seed["corrected"],
        "healed": seed["healed"],
        "soft_eta_overruns": 0,
        "slow_heal_advisories": 0,
        "seeded_from_telemetry_rows": seed["rows_seen"],
        "recent_calls": {},
    }
    try:
        sc_path.parent.mkdir(parents=True, exist_ok=True)
        lock_path = sc_path.with_suffix(".lock")
        if sc_path.parent.is_symlink() or sc_path.is_symlink() or lock_path.is_symlink():
            return default_obj
        with open(lock_path, "a+", encoding="utf-8") as lfh:
            fcntl.flock(lfh.fileno(), fcntl.LOCK_EX)
            try:
                if sc_path.is_file():
                    loaded = json.loads(sc_path.read_text(encoding="utf-8"))
                    if isinstance(loaded, dict):
                        return loaded
                _write_private_json_atomic(sc_path, default_obj)
                return default_obj
            finally:
                fcntl.flock(lfh.fileno(), fcntl.LOCK_UN)
    except (OSError, json.JSONDecodeError):
        return default_obj


def record_call_outcome(
    *,
    verdict: str,
    cmd: str,
    effort: str = "standard",
    mode: str = "fast",
    elapsed_s: float = 0.0,
    heal_elapsed_s: float = 0.0,
    soft_eta_exceeded: bool = False,
    note: str = "",
    scorecard_path: Path | None = None,
    telemetry_log: Path | None = None,
) -> dict[str, Any]:
    """Record a single completed/failed Bionic call into the locked lifetime scorecard."""
    v_norm = verdict.strip().lower()
    if v_norm not in {"clean", "corrected", "healed"}:
        raise ValueError(f"Unsupported verdict '{verdict}'; expected clean, corrected, or healed.")
    sc_path = _resolve_scorecard_path(scorecard_path)
    tel_path = _resolve_telemetry_log(telemetry_log)
    slow_self_heal = bool(v_norm == "healed" and float(heal_elapsed_s) > SLOW_SELF_HEAL_THRESHOLD_S)

    sc = load_or_init_scorecard(sc_path, tel_path)
    try:
        lock_path = sc_path.with_suffix(".lock")
        with open(lock_path, "a+", encoding="utf-8") as lfh:
            fcntl.flock(lfh.fileno(), fcntl.LOCK_EX)
            try:
                if sc_path.is_file():
                    try:
                        loaded = json.loads(sc_path.read_text(encoding="utf-8"))
                        if isinstance(loaded, dict):
                            sc = loaded
                    except (OSError, json.JSONDecodeError):
                        pass
                seq = int(sc.get("next_seq") or 1)
                call_id = f"BC-{seq:04d}"
                sc["next_seq"] = seq + 1
                sc[v_norm] = int(sc.get(v_norm) or 0) + 1
                if soft_eta_exceeded:
                    sc["soft_eta_overruns"] = int(sc.get("soft_eta_overruns") or 0) + 1
                if slow_self_heal:
                    sc["slow_heal_advisories"] = int(sc.get("slow_heal_advisories") or 0) + 1
                sc["updated_at"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
                recent = dict(sc.get("recent_calls") or {})
                recent[call_id] = {
                    "ts": sc["updated_at"],
                    "cmd": cmd,
                    "effort": effort,
                    "mode": mode,
                    "verdict": v_norm,
                    "elapsed_s": round(float(elapsed_s), 3),
                    "heal_elapsed_s": round(float(heal_elapsed_s), 3),
                    "slow_self_heal": slow_self_heal,
                    "soft_eta_exceeded": bool(soft_eta_exceeded),
                    "note": note[:200],
                }
                if len(recent) > 100:
                    for old_k in list(recent.keys())[: len(recent) - 100]:
                        recent.pop(old_k, None)
                sc["recent_calls"] = recent
                _write_private_json_atomic(sc_path, sc)
                return {"call_id": call_id, "slow_self_heal": slow_self_heal, **sc}
            finally:
                fcntl.flock(lfh.fileno(), fcntl.LOCK_UN)
    except OSError:
        sc[v_norm] = int(sc.get(v_norm) or 0) + 1
        return {"call_id": "BC-0000", "slow_self_heal": slow_self_heal, **sc}


def apply_call_verdict(
    call_id: str,
    new_verdict: str,
    *,
    note: str = "",
    scorecard_path: Path | None = None,
) -> dict[str, Any]:
    """Idempotently update/downgrade a tracked call_id verdict (e.g., clean -> corrected)."""
    v_norm = new_verdict.strip().lower()
    if v_norm not in {"clean", "corrected", "healed"}:
        raise ValueError(f"Unsupported verdict '{new_verdict}'; expected clean, corrected, or healed.")
    sc_path = _resolve_scorecard_path(scorecard_path)
    sc = load_or_init_scorecard(sc_path)
    lock_path = sc_path.with_suffix(".lock")
    with open(lock_path, "a+", encoding="utf-8") as lfh:
        fcntl.flock(lfh.fileno(), fcntl.LOCK_EX)
        try:
            if sc_path.is_file():
                loaded = json.loads(sc_path.read_text(encoding="utf-8"))
                if isinstance(loaded, dict):
                    sc = loaded
            recent = dict(sc.get("recent_calls") or {})
            entry = recent.get(call_id)
            if not isinstance(entry, dict):
                raise KeyError(f"Unknown call_id '{call_id}' in scorecard.")
            old_v = str(entry.get("verdict") or "clean")
            if old_v != v_norm:
                sc[old_v] = max(0, int(sc.get(old_v) or 0) - 1)
                sc[v_norm] = int(sc.get(v_norm) or 0) + 1
                entry["verdict"] = v_norm
                entry["downgraded_from"] = old_v
            if note:
                entry["note"] = note[:200]
            entry["verdict_updated_at"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
            recent[call_id] = entry
            sc["recent_calls"] = recent
            sc["updated_at"] = entry["verdict_updated_at"]
            _write_private_json_atomic(sc_path, sc)
            return {
                "call_id": call_id,
                "previous_verdict": old_v,
                "verdict": v_norm,
                "clean": int(sc.get("clean") or 0),
                "corrected": int(sc.get("corrected") or 0),
                "healed": int(sc.get("healed") or 0),
                "metrics": compute_scorecard_metrics(sc),
                "formatted": format_lifetime_scorecard(sc_obj=sc),
            }
        finally:
            fcntl.flock(lfh.fileno(), fcntl.LOCK_UN)


def format_lifetime_scorecard(
    scorecard_path: Path | None = None,
    telemetry_log: Path | None = None,
    *,
    sc_obj: dict[str, Any] | None = None,
) -> str:
    """Render canonical Bionic scorecard string plus relative usability and epoch delta."""
    sc = sc_obj if isinstance(sc_obj, dict) else load_or_init_scorecard(scorecard_path, telemetry_log)
    m = compute_scorecard_metrics(sc)
    base = f"Bionic Calls = {m['clean']}/{m['corrected']} (healed={m['healed']})"
    if m["total_calls"] > 0:
        if m["delta_usable_pct_vs_prev"] is not None and m["prev_epoch"]:
            prev_lbl = str(m["prev_epoch"].get("epoch_label") or "prev")
            return f"{base} [{m['usable_pct']:.1f}% usable, {m['corrected_pct']:.1f}% corr | {m['delta_usable_pct_vs_prev']:+.1f}% vs {prev_lbl}]"
        return f"{base} [{m['usable_pct']:.1f}% usable, {m['corrected_pct']:.1f}% corr]"
    if m["prev_epoch"] and "usable_pct" in m["prev_epoch"]:
        prev_lbl = str(m["prev_epoch"].get("epoch_label") or "prev")
        return f"{base} [epoch {m['epoch']}: 0 calls | {prev_lbl}={float(m['prev_epoch']['usable_pct']):.1f}% usable]"
    return base


def reset_scorecard(
    *,
    archive: bool = True,
    epoch_label: str = "v2.3",
    scorecard_path: Path | None = None,
    telemetry_log: Path | None = None,
    archive_path: Path | None = None,
) -> dict[str, Any]:
    """Atomically archive the active scorecard epoch and reset counters while preserving monotonic next_seq."""
    sc_path = _resolve_scorecard_path(scorecard_path)
    tel_path = _resolve_telemetry_log(telemetry_log)
    arch_path = _resolve_scorecard_archive_path(archive_path, sc_path)
    old_sc = load_or_init_scorecard(sc_path, tel_path)
    sc_path.parent.mkdir(parents=True, exist_ok=True)
    lock_path = sc_path.with_suffix(".lock")
    if sc_path.parent.is_symlink() or sc_path.is_symlink() or lock_path.is_symlink():
        raise SidecarFirewallError(f"[SECURITY_FIREWALL_BLOCKED] Refusing symlink scorecard path: {sc_path}")

    with open(lock_path, "a+", encoding="utf-8") as lfh:
        fcntl.flock(lfh.fileno(), fcntl.LOCK_EX)
        try:
            if sc_path.is_file():
                try:
                    loaded = json.loads(sc_path.read_text(encoding="utf-8"))
                    if isinstance(loaded, dict):
                        old_sc = loaded
                except (OSError, json.JSONDecodeError):
                    pass
            old_m = compute_scorecard_metrics(old_sc)
            now_iso = datetime.now(timezone.utc).isoformat(timespec="seconds")
            old_epoch_lbl = str(old_sc.get("epoch") or "")
            if not old_epoch_lbl or old_epoch_lbl == "lifetime":
                old_epoch_lbl = "pre-v2.3"
            same_epoch_rehearsal = (
                old_epoch_lbl == epoch_label
                and isinstance(old_sc.get("prev_epoch"), dict)
                and int(old_sc["prev_epoch"].get("total_calls") or 0) > 0
            )
            archive_epoch_lbl = f"{old_epoch_lbl}-rehearsal" if same_epoch_rehearsal else old_epoch_lbl
            if archive:
                if arch_path.parent.is_symlink() or arch_path.is_symlink():
                    raise SidecarFirewallError(f"[SECURITY_FIREWALL_BLOCKED] Refusing symlink archive path: {arch_path}")
                arch_rec = {
                    "archived_at": now_iso,
                    "epoch_label": archive_epoch_lbl,
                    "new_epoch_label": epoch_label,
                    "metrics": old_m,
                    "scorecard": old_sc,
                }
                flags = os.O_WRONLY | os.O_CREAT | os.O_APPEND | getattr(os, "O_NOFOLLOW", 0)
                fd = os.open(arch_path, flags, 0o600)
                with os.fdopen(fd, "a", encoding="utf-8") as afh:
                    afh.write(json.dumps(arch_rec) + "\n")
                try:
                    os.chmod(arch_path, 0o600)
                except OSError:
                    pass

            if same_epoch_rehearsal:
                prev_summary = dict(old_sc["prev_epoch"])
            else:
                prev_summary = {
                    "epoch_label": old_epoch_lbl,
                    "archived_at": now_iso,
                    "clean": old_m["clean"],
                    "corrected": old_m["corrected"],
                    "healed": old_m["healed"],
                    "total_calls": old_m["total_calls"],
                    "usable_pct": old_m["usable_pct"],
                    "corrected_pct": old_m["corrected_pct"],
                    "healed_pct": old_m["healed_pct"],
                }
            new_sc: dict[str, Any] = {
                "schema_version": SCORECARD_SCHEMA,
                "epoch": epoch_label,
                "reset_at": now_iso,
                "updated_at": now_iso,
                "next_seq": int(old_sc.get("next_seq") or 1),
                "clean": 0,
                "corrected": 0,
                "healed": 0,
                "soft_eta_overruns": 0,
                "slow_heal_advisories": 0,
                "seeded_from_telemetry_rows": int(old_sc.get("seeded_from_telemetry_rows") or 0),
                "prev_epoch": prev_summary,
                "recent_calls": {},
            }
            _write_private_json_atomic(sc_path, new_sc)
            return {
                "ok": True,
                "action": "scorecard-reset",
                "epoch": epoch_label,
                "archived": bool(archive),
                "archive_path": str(arch_path) if archive else None,
                "previous_epoch": prev_summary,
                "scorecard": new_sc,
                "formatted": format_lifetime_scorecard(sc_obj=new_sc),
            }
        finally:
            fcntl.flock(lfh.fileno(), fcntl.LOCK_UN)


def estimate_quota_savings(log_path: Path | None = None) -> dict[str, Any]:
    """Estimate onboard-GPU cloud quota tokens saved, pinned explicitly to STANDARD vs HIGH effort modes."""
    path = _resolve_telemetry_log(log_path)
    buckets: dict[str, dict[str, Any]] = {
        "standard": {"calls": 0, "prompt_tokens": 0, "completion_tokens": 0, "direct_tokens": 0, "weighted_frontier_equiv_tokens": 0},
        "high": {"calls": 0, "prompt_tokens": 0, "completion_tokens": 0, "direct_tokens": 0, "weighted_frontier_equiv_tokens": 0},
    }
    legacy_estimated_rows = 0
    if path.is_file():
        try:
            for raw in path.read_text(encoding="utf-8", errors="replace").splitlines():
                if not raw.strip():
                    continue
                row = json.loads(raw)
                if (row.get("tripped") or row.get("finish_reason") == "eta_tripped") and not row.get("elapsed_s"):
                    continue
                if row.get("http_error") or row.get("synthetic_fault"):
                    continue
                mode_val = str(row.get("mode") or "fast").lower()
                eff_val = str(row.get("effort") or ("high" if mode_val == "deep" else "standard")).lower()
                bucket_key = "high" if eff_val == "high" else "standard"
                p_tok = row.get("prompt_tokens")
                c_tok = row.get("completion_tokens")
                if not isinstance(p_tok, int) or p_tok <= 0:
                    p_tok = int(row.get("est_prompt_tokens") or 0)
                    legacy_estimated_rows += 1
                if not isinstance(c_tok, int) or c_tok <= 0:
                    tg = row.get("observed_tg_tok_s")
                    el = row.get("elapsed_s")
                    if isinstance(tg, (int, float)) and isinstance(el, (int, float)):
                        c_tok = max(1, round(float(tg) * float(el)))
                    else:
                        c_tok = 0
                direct = p_tok + c_tok
                avoided_carry = max(0, p_tok - min(p_tok, 450)) * 4
                weighted_equiv = p_tok + round(c_tok * 5.0) + avoided_carry
                b = buckets[bucket_key]
                b["calls"] += 1
                b["prompt_tokens"] += p_tok
                b["completion_tokens"] += c_tok
                b["direct_tokens"] += direct
                b["weighted_frontier_equiv_tokens"] += weighted_equiv
        except (OSError, json.JSONDecodeError):
            pass

    for _k, b in buckets.items():
        n = b["calls"]
        b["avg_weighted_per_call"] = round(b["weighted_frontier_equiv_tokens"] / n, 1) if n else 0.0
        b["projected_50_calls_weighted"] = round(b["avg_weighted_per_call"] * 50)
    total_direct = buckets["standard"]["direct_tokens"] + buckets["high"]["direct_tokens"]
    total_weighted = buckets["standard"]["weighted_frontier_equiv_tokens"] + buckets["high"]["weighted_frontier_equiv_tokens"]
    return {
        "methodology": (
            "Weighted frontier-equivalent quota = prompt_tokens + 5.0 * completion_tokens "
            "(frontier output-to-input weight) + 4x avoided multi-turn raw context carry."
        ),
        "by_effort": buckets,
        "total_direct_offloaded_tokens": total_direct,
        "total_weighted_frontier_equiv_tokens": total_weighted,
        "legacy_estimated_rows": legacy_estimated_rows,
    }


def record_usage_telemetry(entry: dict[str, Any], log_path: Path | None = None) -> None:
    """Append metadata-only usage telemetry with 0700/0600 permissions; ignore EROFS in sandboxes."""
    path = _resolve_telemetry_log(log_path)
    payload = {
        "ts": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "telemetry_schema": TELEMETRY_SCHEMA,
        "eta_cal_version": ETA_CALIBRATION_VERSION,
        **entry,
    }
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
    sc = load_or_init_scorecard(telemetry_log=path)
    sc_m = compute_scorecard_metrics(sc)
    return {
        "log_path": str(path),
        "recent_runs": total,
        "tripped_runs": tripped,
        "by_tier": by_tier,
        "recent_elapsed_avg_s": avg_elapsed,
        "lifetime_scorecard": {
            "epoch": sc.get("epoch", "lifetime"),
            "clean": sc_m["clean"],
            "corrected": sc_m["corrected"],
            "healed": sc_m["healed"],
            "soft_eta_overruns": int(sc.get("soft_eta_overruns") or 0),
            "slow_heal_advisories": int(sc.get("slow_heal_advisories") or 0),
            "metrics": sc_m,
            "prev_epoch": sc.get("prev_epoch"),
            "formatted": format_lifetime_scorecard(sc_obj=sc),
        },
        "quota_savings": estimate_quota_savings(path),
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
    has_code_context: bool = False,
    loaded_ctx_override: int | None = None,
    calibrated_output: bool = True,
    allow_soft_eta_overrun: bool = False,
    sys_prompt_bytes: int = 0,
    include_git_diff: bool = False,
    target_code_bytes: int = 0,
) -> dict[str, Any]:
    eta = estimate_eta(
        mode=mode,
        prompt_bytes=prompt_bytes,
        max_tokens=max_tokens,
        prompt_tokens_override=prompt_tokens_override,
        max_eta_seconds=max_eta_seconds,
        expected_turns=expected_turns,
        has_code_context=has_code_context,
        loaded_ctx_override=loaded_ctx_override,
        calibrated_output=calibrated_output,
        cmd_name=cmd_name,
        sys_prompt_bytes=sys_prompt_bytes,
        include_git_diff=include_git_diff,
        target_code_bytes=target_code_bytes,
    )
    if eta["hard_tripped"]:
        if not force_slow or "exceed" in " ".join(eta["reasons"]).lower() and "max=" in " ".join(eta["reasons"]).lower():
            record_usage_telemetry(
                {
                    "cmd": cmd_name,
                    "effort": eta["effort"],
                    "invocation_tier": invocation_tier,
                    "mode": mode,
                    "est_prompt_tokens": eta["est_prompt_tokens"],
                    "predicted_eta_s": eta["predicted_eta_s"],
                    "max_eta_seconds": max_eta_seconds,
                    "tripped": True,
                    "soft_eta_exceeded": eta["soft_eta_exceeded"],
                    "elapsed_s": None,
                    "observed_tg_tok_s": None,
                    "finish_reason": "eta_tripped",
                }
            )
            reason_str = " | ".join(eta["reasons"])
            raise SidecarEtaTrippedError(
                f"[ETA_CIRCUIT_BREAKER_TRIPPED] {reason_str}",
                eta,
            )

    if eta["soft_eta_exceeded"]:
        if allow_soft_eta_overrun or force_slow:
            eta["soft_eta_advisory"] = True
            eta["verdict"] = "RUN_LOCALLY_WITH_ETA_ADVISORY"
            return eta
        record_usage_telemetry(
            {
                "cmd": cmd_name,
                "effort": eta["effort"],
                "invocation_tier": invocation_tier,
                "mode": mode,
                "est_prompt_tokens": eta["est_prompt_tokens"],
                "predicted_eta_s": eta["predicted_eta_s"],
                "max_eta_seconds": max_eta_seconds,
                "tripped": True,
                "soft_eta_exceeded": True,
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
    eta["soft_eta_advisory"] = False
    return eta


def cmd_status(args: argparse.Namespace) -> int:
    api_url = validate_loopback_url(args.api_url or resolve_default_api_url())
    sys_prompt, sys_src = load_system_prompt(Path(args.system_prompt) if getattr(args, "system_prompt", None) else None)
    probe = probe_server_models(api_url, model_id=args.model, timeout_s=5.0)
    sc_str = format_lifetime_scorecard()

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
        "high_effort_soft_eta_seconds": HIGH_EFFORT_SOFT_ETA_SECONDS,
        "system_prompt_source": sys_src,
        "system_prompt_bytes": len(sys_prompt.encode("utf-8")),
        "profiles": PROFILES,
        "scorecard": sc_str,
    }
    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        state = "ONLINE" if payload["reachable"] else f"OFFLINE ({probe['error']})"
        print(
            f"Bionic Sidecar Status: {state} @ {api_url} | Loaded: {', '.join(probe['loaded_models']) or 'none'} "
            f"| Target Loaded: {probe['target_model_loaded']} (ctx={probe['loaded_context_length']}) | {sc_str}"
        )
        print(
            f"System Prompt: {sys_src} ({payload['system_prompt_bytes']} B) | "
            f"ETA Cutoffs: auto={AUTO_MAX_ETA_SECONDS:.0f}s explicit={DEFAULT_MAX_ETA_SECONDS:.0f}s high={HIGH_EFFORT_SOFT_ETA_SECONDS:.0f}s"
        )
    return 0 if payload["reachable"] else EXIT_RUNTIME_ERROR


def cmd_check_eta(args: argparse.Namespace) -> int:
    sys_prompt, _ = load_system_prompt(Path(args.system_prompt) if getattr(args, "system_prompt", None) else None)
    repo_root = Path(args.repo) if args.repo else None
    repo_resolved = repo_root.resolve(strict=False) if repo_root else None
    validated_files, slice_items, _slice_map = parse_and_validate_context_items(
        list(args.context_files or []), repo_root=repo_root, require_exists=True
    )

    user_prompt = args.prompt or ""
    if args.prompt_file:
        user_prompt = _read_prompt_arg(None, args.prompt_file)

    prompt_bytes = len(sys_prompt.encode("utf-8")) + len(user_prompt.encode("utf-8"))
    if validated_files or args.include_git_diff:
        assembled, _ = assemble_prompt_payload(
            user_prompt=user_prompt,
            context_files=validated_files,
            repo_root=repo_resolved,
            include_git_diff=bool(args.include_git_diff),
            sys_prompt=sys_prompt,
            context_slices=slice_items,
        )
        prompt_bytes = len(sys_prompt.encode("utf-8")) + len(assembled.encode("utf-8"))

    effort_norm, eff_mode = resolve_effort_and_mode(getattr(args, "effort", None), getattr(args, "mode", None))
    max_toks = resolve_effective_max_tokens(eff_mode, args.max_tokens)
    max_eta = resolve_max_eta_seconds(args)
    if args.max_eta_seconds is None and effort_norm == "high":
        max_eta = max(max_eta, HIGH_EFFORT_SOFT_ETA_SECONDS)
    eta = estimate_eta(
        mode=eff_mode,
        prompt_bytes=prompt_bytes,
        max_tokens=max_toks,
        prompt_tokens_override=args.prompt_tokens,
        max_eta_seconds=max_eta,
        expected_turns=args.expected_turns,
        has_code_context=is_code_heavy_payload(validated_files, bool(args.include_git_diff)),
        calibrated_output=True,
        cmd_name="check-eta",
        sys_prompt_bytes=len(sys_prompt.encode("utf-8")),
        include_git_diff=bool(args.include_git_diff),
    )
    eta["invocation_tier"] = getattr(args, "invocation_tier", "explicit")
    if args.json:
        print(json.dumps(eta, indent=2))
    else:
        print(
            f"[{eta['verdict']}] tier={eta['invocation_tier']} effort={eta['effort']} mode={eta['mode']} "
            f"prompt~={eta['est_prompt_tokens']} tok, out~={eta['est_output_tokens']} tok -> "
            f"ETA={eta['predicted_eta_s']}s (target {eta['max_eta_seconds']}s)"
        )
    if eta["tripped"] and not args.force_slow:
        print(f"[ETA_CIRCUIT_BREAKER_TRIPPED] {' | '.join(eta['reasons'])}", file=sys.stderr)
        return EXIT_ETA_TRIPPED
    return 0


def cmd_query(args: argparse.Namespace) -> int:
    api_url = validate_loopback_url(args.api_url or resolve_default_api_url())
    sys_prompt, sys_src = load_system_prompt(Path(args.system_prompt) if getattr(args, "system_prompt", None) else None)
    repo_root = Path(args.repo) if args.repo else None
    repo_resolved = repo_root.resolve(strict=False) if repo_root else None
    validated_files, slice_items, _slice_map = parse_and_validate_context_items(
        list(args.context_files or []), repo_root=repo_root, require_exists=True
    )
    user_prompt = _read_prompt_arg(args.prompt, args.prompt_file)

    assembled, file_meta = assemble_prompt_payload(
        user_prompt=user_prompt,
        context_files=validated_files,
        repo_root=repo_resolved,
        include_git_diff=bool(args.include_git_diff),
        sys_prompt=sys_prompt,
        context_slices=slice_items,
    )
    sys_bytes = len(sys_prompt.encode("utf-8"))
    prompt_bytes = sys_bytes + len(assembled.encode("utf-8"))
    has_code = is_code_heavy_payload(validated_files, bool(args.include_git_diff))
    tier = getattr(args, "invocation_tier", "explicit")
    effort_norm, req_mode = resolve_effort_and_mode(getattr(args, "effort", None), getattr(args, "mode", None))
    requested_max_toks = args.max_tokens
    max_toks = resolve_effective_max_tokens(req_mode, requested_max_toks)
    max_eta = resolve_max_eta_seconds(args)
    if args.max_eta_seconds is None and effort_norm == "high":
        max_eta = max(max_eta, HIGH_EFFORT_SOFT_ETA_SECONDS)

    srv, effective_mode = preflight_live_inference(api_url, args.model, req_mode)
    loaded_ctx = srv.get("loaded_context_length")
    max_toks = resolve_effective_max_tokens(effective_mode, requested_max_toks)
    eta = _enforce_eta_or_raise(
        mode=effective_mode,
        prompt_bytes=prompt_bytes,
        max_tokens=max_toks,
        max_eta_seconds=max_eta,
        expected_turns=args.expected_turns,
        force_slow=args.force_slow,
        cmd_name="query",
        invocation_tier=tier,
        has_code_context=has_code,
        loaded_ctx_override=loaded_ctx,
        calibrated_output=True,
        allow_soft_eta_overrun=(effective_mode != "cpu-bg"),
        sys_prompt_bytes=sys_bytes,
        include_git_diff=bool(args.include_git_diff),
    )
    t_err0 = time.perf_counter()
    try:
        res = invoke_chat_completion(
            api_url=api_url,
            model_id=args.model,
            mode=effective_mode,
            system_prompt=sys_prompt,
            user_content=assembled,
            max_tokens=max_toks,
            timeout_s=min(max(max_eta + 60.0, 180.0), 300.0),
            preflight_checked=True,
            loaded_ctx=loaded_ctx,
            est_prompt_tokens=eta["est_prompt_tokens"],
        )
    except Exception as exc:
        err_dt = round(time.perf_counter() - t_err0, 3)
        record_usage_telemetry(
            {
                "cmd": "query",
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
        record_call_outcome(
            verdict="corrected",
            cmd="query",
            effort=eta["effort"],
            mode=effective_mode,
            elapsed_s=err_dt,
            soft_eta_exceeded=eta["soft_eta_exceeded"],
            note=str(exc)[:180],
        )
        raise

    call_verdict = "clean" if res["finish_reason"] != "length" else "corrected"
    sc_rec = record_call_outcome(
        verdict=call_verdict,
        cmd="query",
        effort=eta["effort"],
        mode=effective_mode,
        elapsed_s=res["elapsed_s"],
        soft_eta_exceeded=eta["soft_eta_exceeded"],
    )
    record_usage_telemetry(
        {
            "cmd": "query",
            "call_id": sc_rec["call_id"],
            "effort": eta["effort"],
            "invocation_tier": tier,
            "mode": effective_mode,
            "est_prompt_tokens": eta["est_prompt_tokens"],
            "prompt_tokens": res["prompt_tokens"],
            "completion_tokens": res["completion_tokens"],
            "predicted_eta_s": eta["predicted_eta_s"],
            "max_eta_seconds": max_eta,
            "tripped": False,
            "soft_eta_exceeded": eta["soft_eta_exceeded"],
            "verdict": call_verdict,
            "elapsed_s": res["elapsed_s"],
            "observed_tg_tok_s": res["observed_tg_tok_s"],
            "finish_reason": res["finish_reason"],
        }
    )
    out_obj = {
        "schema_version": SCHEMA_VERSION,
        "call_id": sc_rec["call_id"],
        "scorecard": format_lifetime_scorecard(),
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
            f"\n[SIDECAR TELEMETRY: effort={eta['effort']} mode={res['mode']} elapsed={res['elapsed_s']}s "
            f"prompt={res['prompt_tokens']}tok out={res['completion_tokens']}tok "
            f"tg={res['observed_tg_tok_s']} tok/s | {out_obj['scorecard']}]",
            file=sys.stderr,
        )
    return 0


def cmd_audit_to_quarantine(args: argparse.Namespace) -> int:
    api_url = validate_loopback_url(args.api_url or resolve_default_api_url())
    sys_prompt, sys_src = load_system_prompt(Path(args.system_prompt) if getattr(args, "system_prompt", None) else None)
    repo_root = Path(args.repo) if args.repo else None
    repo_resolved = repo_root.resolve(strict=False) if repo_root else None
    validated_files, slice_items, _slice_map = parse_and_validate_context_items(
        list(args.context_files or []), repo_root=repo_root, require_exists=True
    )
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
        context_slices=slice_items,
    )
    quar_candidate = Path(args.memory_root) / "Projects" / args.project / "Quarantine" / f"{args.name}.md"
    if not args.overwrite and quar_candidate.exists():
        raise RuntimeError(
            f"Quarantine note already exists (pass --overwrite to replace): {quar_candidate}"
        )

    sys_bytes = len(sys_prompt.encode("utf-8"))
    prompt_bytes = sys_bytes + len(assembled.encode("utf-8"))
    has_code = is_code_heavy_payload(validated_files, bool(args.include_git_diff))
    tier = getattr(args, "invocation_tier", "explicit")
    effort_norm, req_mode = resolve_effort_and_mode(getattr(args, "effort", None), getattr(args, "mode", None))
    requested_max_toks = args.max_tokens
    max_eta = resolve_max_eta_seconds(args)
    if args.max_eta_seconds is None and effort_norm == "high":
        max_eta = max(max_eta, HIGH_EFFORT_SOFT_ETA_SECONDS)

    srv, effective_mode = preflight_live_inference(api_url, args.model, req_mode)
    loaded_ctx = srv.get("loaded_context_length")
    max_toks = resolve_effective_max_tokens(effective_mode, requested_max_toks)
    eta = _enforce_eta_or_raise(
        mode=effective_mode,
        prompt_bytes=prompt_bytes,
        max_tokens=max_toks,
        max_eta_seconds=max_eta,
        expected_turns=args.expected_turns,
        force_slow=args.force_slow,
        cmd_name="audit-to-quarantine",
        invocation_tier=tier,
        has_code_context=has_code,
        loaded_ctx_override=loaded_ctx,
        calibrated_output=True,
        allow_soft_eta_overrun=(effective_mode != "cpu-bg"),
        sys_prompt_bytes=sys_bytes,
        include_git_diff=bool(args.include_git_diff),
    )
    t_err0 = time.perf_counter()
    try:
        res = invoke_chat_completion(
            api_url=api_url,
            model_id=args.model,
            mode=effective_mode,
            system_prompt=sys_prompt,
            user_content=assembled,
            max_tokens=max_toks,
            timeout_s=min(max(max_eta + 60.0, 210.0), 300.0),
            preflight_checked=True,
            loaded_ctx=loaded_ctx,
            est_prompt_tokens=eta["est_prompt_tokens"],
        )
    except Exception as exc:
        err_dt = round(time.perf_counter() - t_err0, 3)
        record_usage_telemetry(
            {
                "cmd": "audit-to-quarantine",
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
        record_call_outcome(
            verdict="corrected",
            cmd="audit-to-quarantine",
            effort=eta["effort"],
            mode=effective_mode,
            elapsed_s=err_dt,
            soft_eta_exceeded=eta["soft_eta_exceeded"],
            note=str(exc)[:180],
        )
        raise

    call_verdict = "clean" if res["finish_reason"] != "length" else "corrected"
    sc_rec = record_call_outcome(
        verdict=call_verdict,
        cmd="audit-to-quarantine",
        effort=eta["effort"],
        mode=effective_mode,
        elapsed_s=res["elapsed_s"],
        soft_eta_exceeded=eta["soft_eta_exceeded"],
    )
    record_usage_telemetry(
        {
            "cmd": "audit-to-quarantine",
            "call_id": sc_rec["call_id"],
            "effort": eta["effort"],
            "invocation_tier": tier,
            "mode": effective_mode,
            "est_prompt_tokens": eta["est_prompt_tokens"],
            "prompt_tokens": res["prompt_tokens"],
            "completion_tokens": res["completion_tokens"],
            "predicted_eta_s": eta["predicted_eta_s"],
            "max_eta_seconds": max_eta,
            "tripped": False,
            "soft_eta_exceeded": eta["soft_eta_exceeded"],
            "verdict": call_verdict,
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
        "call_id": sc_rec["call_id"],
        "scorecard": format_lifetime_scorecard(),
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
        print(f"[QUARANTINED] Wrote {written_loc} via memory_gateway.py ({res['elapsed_s']}s) | {payload['scorecard']}")
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
    """Write staged draft + ast.parse + py_compile + unified diff inside validated 0700/0600 scratch dir."""
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
        try:
            ast.parse(extracted, filename=str(staged_file))
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
        except SyntaxError as exc:
            compile_ok = False
            compile_error = f"SyntaxError at line {exc.lineno}: {exc.msg}"

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
    sys_prompt, _ = load_system_prompt(Path(args.system_prompt) if getattr(args, "system_prompt", None) else None)
    repo_root = Path(args.repo) if args.repo else None
    repo_resolved = repo_root.resolve(strict=False) if repo_root else None
    validated_files, slice_items, _slice_map = parse_and_validate_context_items(
        list(args.context_files or []), repo_root=repo_root, require_exists=True
    )
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
        context_slices=slice_items,
    )
    sys_bytes = len(sys_prompt.encode("utf-8"))
    prompt_bytes = sys_bytes + len(assembled.encode("utf-8"))
    tier = getattr(args, "invocation_tier", "explicit")
    effort_norm, req_mode = resolve_effort_and_mode(getattr(args, "effort", None), getattr(args, "mode", None))
    requested_max_toks = args.max_tokens
    max_eta = resolve_max_eta_seconds(args)
    if args.max_eta_seconds is None and effort_norm == "high":
        max_eta = max(max_eta, HIGH_EFFORT_SOFT_ETA_SECONDS)

    srv, effective_mode = preflight_live_inference(api_url, args.model, req_mode)
    loaded_ctx = srv.get("loaded_context_length")
    max_toks = resolve_effective_max_tokens(effective_mode, requested_max_toks)
    eta = _enforce_eta_or_raise(
        mode=effective_mode,
        prompt_bytes=prompt_bytes,
        max_tokens=max_toks,
        max_eta_seconds=max_eta,
        expected_turns=args.expected_turns,
        force_slow=args.force_slow,
        cmd_name="stage-code",
        invocation_tier=tier,
        has_code_context=True,
        loaded_ctx_override=loaded_ctx,
        calibrated_output=True,
        allow_soft_eta_overrun=(effective_mode != "cpu-bg"),
        sys_prompt_bytes=sys_bytes,
    )
    t_err0 = time.perf_counter()
    try:
        res = invoke_chat_completion(
            api_url=api_url,
            model_id=args.model,
            mode=effective_mode,
            system_prompt=sys_prompt,
            user_content=assembled,
            max_tokens=max_toks,
            timeout_s=min(max(max_eta + 60.0, 180.0), 300.0),
            preflight_checked=True,
            loaded_ctx=loaded_ctx,
            est_prompt_tokens=eta["est_prompt_tokens"],
        )
    except Exception as exc:
        err_dt = round(time.perf_counter() - t_err0, 3)
        record_usage_telemetry(
            {
                "cmd": "stage-code",
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
        record_call_outcome(
            verdict="corrected",
            cmd="stage-code",
            effort=eta["effort"],
            mode=effective_mode,
            elapsed_s=err_dt,
            soft_eta_exceeded=eta["soft_eta_exceeded"],
            note=str(exc)[:180],
        )
        raise

    receipt = stage_code_artifact(
        staging_dir=safe_staging,
        target_filename=args.target_filename,
        generated_text=res["content"],
        compare_against=compare_path,
        telemetry={"eta": eta, **{k: v for k, v in res.items() if k != "content"}},
    )
    call_verdict = "clean" if receipt["py_compile_ok"] is not False else "corrected"
    sc_rec = record_call_outcome(
        verdict=call_verdict,
        cmd="stage-code",
        effort=eta["effort"],
        mode=effective_mode,
        elapsed_s=res["elapsed_s"],
        soft_eta_exceeded=eta["soft_eta_exceeded"],
    )
    record_usage_telemetry(
        {
            "cmd": "stage-code",
            "call_id": sc_rec["call_id"],
            "effort": eta["effort"],
            "invocation_tier": tier,
            "mode": effective_mode,
            "est_prompt_tokens": eta["est_prompt_tokens"],
            "prompt_tokens": res["prompt_tokens"],
            "completion_tokens": res["completion_tokens"],
            "predicted_eta_s": eta["predicted_eta_s"],
            "max_eta_seconds": max_eta,
            "tripped": False,
            "soft_eta_exceeded": eta["soft_eta_exceeded"],
            "verdict": call_verdict,
            "elapsed_s": res["elapsed_s"],
            "observed_tg_tok_s": res["observed_tg_tok_s"],
            "finish_reason": res["finish_reason"],
        }
    )
    receipt["call_id"] = sc_rec["call_id"]
    receipt["scorecard"] = format_lifetime_scorecard()
    if args.json:
        print(json.dumps(receipt, indent=2))
    else:
        print(
            f"[STAGED] {receipt['staged_file']} ({receipt['bytes']} B) | "
            f"py_compile_ok={receipt['py_compile_ok']} | diff={receipt['diff_file']} | {receipt['scorecard']}"
        )
    if receipt["py_compile_ok"] is False:
        print(f"py_compile failed: {receipt['py_compile_error']}", file=sys.stderr)
        return EXIT_RUNTIME_ERROR
    return 0


CONTROL_PROFILES: dict[str, dict[str, Any]] = {
    "gpu-max": {"context_length": 57344, "preset": "Qwen3.6-35B-Workstation-Max"},
    "gpu-daily": {"context_length": 49152, "preset": "Qwen3.6-35B-Fast-Sweep"},
    "cpu-bg": {"context_length": 16384, "preset": "Qwen3.6-35B-CPU-Background"},
}


def build_concrete_model_config(profile: str) -> dict[str, Any]:
    """Return Bionic user-concrete-model-default-config JSON for gpu-max, gpu-daily, or cpu-bg."""
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

    if profile == "gpu-max":
        raw_ratio = os.environ.get("BIONIC_GPU_MAX_CPU_EXPERT_RATIO", "").strip()
        expert_ratio = float(raw_ratio) if raw_ratio else 0.52
        expert_ratio = min(0.70, max(0.25, round(expert_ratio, 3)))
        raw_ctx = os.environ.get("BIONIC_GPU_MAX_CTX", "").strip()
        max_ctx = int(raw_ctx) if raw_ctx else int(CONTROL_PROFILES["gpu-max"]["context_length"])
        op_fields = [
            {"key": "llm.prediction.reasoning.enableThinking", "value": False},
            {"key": "llm.prediction.llama.cpuThreads", "value": 10},
        ]
        load_fields = [
            {"key": "llm.load.llama.autoFit", "value": False},
            {"key": "llm.load.contextLength", "value": max_ctx},
            {"key": "llm.load.llama.acceleration.offloadRatio", "value": "max"},
            {"key": "llm.load.numCpuExpertLayersRatio", "value": expert_ratio},
            {"key": "llm.load.llama.flashAttention", "value": True},
            {"key": "llm.load.offloadKVCacheToGpu", "value": True},
            {"key": "llm.load.llama.kCacheQuantizationType", "value": {"checked": True, "value": "q8_0"}},
            {"key": "llm.load.llama.vCacheQuantizationType", "value": {"checked": True, "value": "q8_0"}},
            {"key": "llm.load.llama.cpuThreadPoolSize", "value": 10},
            {
                "key": "llm.load.llama.argumentsOverride",
                "value": {
                    "enabled": True,
                    "disabledParameters": [],
                    "overrideParameters": [{"key": "--parallel", "value": "2"}],
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
                "overrideParameters": [{"key": "--parallel", "value": "2"}],
                "excludeAllConfig": False,
            },
        },
    ]
    return {"preset": CONTROL_PROFILES[profile]["preset"], "operation": {"fields": op_fields}, "load": {"fields": load_fields}}


def _read_hw_counters() -> dict[str, Any]:
    """Read sysfs VRAM, GTT, and /proc/meminfo counters gracefully inside/outside sandboxes."""
    vram_bytes: int | None = None
    vram_total_bytes: int | None = None
    gtt_bytes: int | None = None
    mem_avail_kib: int | None = None
    try:
        vram_bytes = int(VRAM_USED_SYSFS.read_text(encoding="utf-8").strip())
    except (OSError, ValueError):
        pass
    try:
        vram_total_bytes = int(VRAM_TOTAL_SYSFS.read_text(encoding="utf-8").strip())
    except (OSError, ValueError):
        pass
    try:
        gtt_bytes = int(GTT_USED_SYSFS.read_text(encoding="utf-8").strip())
    except (OSError, ValueError):
        pass
    try:
        for line in PROC_MEMINFO_PATH.read_text(encoding="utf-8").splitlines():
            if line.startswith("MemAvailable:"):
                mem_avail_kib = int(line.split()[1])
                break
    except (OSError, ValueError, IndexError):
        pass
    vram_free_bytes = (
        max(0, vram_total_bytes - vram_bytes)
        if (vram_total_bytes is not None and vram_bytes is not None)
        else None
    )
    return {
        "vram_used_bytes": vram_bytes,
        "vram_used_gib": round(vram_bytes / (1024**3), 3) if vram_bytes is not None else None,
        "vram_total_gib": round(vram_total_bytes / (1024**3), 3) if vram_total_bytes is not None else None,
        "vram_free_gib": round(vram_free_bytes / (1024**3), 3) if vram_free_bytes is not None else None,
        "gtt_used_bytes": gtt_bytes,
        "gtt_used_gib": round(gtt_bytes / (1024**3), 3) if gtt_bytes is not None else None,
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
    try:
        return subprocess.run(
            [str(lms_bin), *argv],
            cwd=_safe_subprocess_cwd(),
            capture_output=True,
            text=True,
            timeout=timeout_s,
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        raise RuntimeError(f"lms {' '.join(argv)} timed out after {timeout_s}s") from exc


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
    elif action_norm == "scorecard-reset":
        planned.append(["archive_and_reset_scorecard", str(_resolve_scorecard_path()), str(_resolve_scorecard_archive_path())])
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
    tel_summary = summarize_usage_telemetry()
    return {
        "schema_version": SCHEMA_VERSION,
        "action": "status",
        "api_url": api_url,
        "model": model_id,
        "daemon": _probe_lms_daemon(lms_bin),
        "server": probe_server_models(api_url, model_id=model_id, timeout_s=3.0),
        "hardware": _read_hw_counters(),
        "telemetry": tel_summary,
        "scorecard": tel_summary.get("lifetime_scorecard"),
        "quota_savings": tel_summary.get("quota_savings"),
        "auto_max_eta_seconds": AUTO_MAX_ETA_SECONDS,
        "default_max_eta_seconds": DEFAULT_MAX_ETA_SECONDS,
        "high_effort_soft_eta_seconds": HIGH_EFFORT_SOFT_ETA_SECONDS,
    }


def _control_load(api_url: str, model_id: str, profile: str, lms_bin: Path, cfg_path: Path) -> dict[str, Any]:
    srv = probe_server_models(api_url, model_id=model_id, timeout_s=3.0)
    if not srv["reachable"]:
        raise RuntimeError(
            f"Bionic HTTP server unreachable at {api_url}; run 'control start-headless --user-confirmed' first ({srv['error']})"
        )
    cfg_payload = build_concrete_model_config(profile)
    target_ctx = CONTROL_PROFILES[profile]["context_length"]
    for lf in (cfg_payload.get("load") or {}).get("fields") or []:
        if lf.get("key") == "llm.load.contextLength":
            target_ctx = int(lf["value"])
            break

    old_cfg: dict[str, Any] | None = None
    try:
        if cfg_path.is_file():
            old_cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        old_cfg = None
    cfg_changed = old_cfg != cfg_payload

    cfg_path.parent.mkdir(parents=True, exist_ok=True)
    cfg_path.write_text(json.dumps(cfg_payload, indent=2) + "\n", encoding="utf-8")

    if srv["target_model_loaded"] and srv["loaded_context_length"] == target_ctx and not cfg_changed:
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
        try:
            ul = _run_lms_cmd(lms_bin, ["unload", model_id], timeout_s=30.0)
        except subprocess.TimeoutExpired as exc:
            raise RuntimeError(f"lms unload timed out before reload: {exc}") from exc
        if ul.returncode != 0:
            raise RuntimeError(f"lms unload failed before reload: {ul.stderr.strip() or ul.stdout.strip()}")

    try:
        ld = _run_lms_cmd(lms_bin, ["load", model_id, "--identifier", model_id, "-y"], timeout_s=180.0)
    except subprocess.TimeoutExpired as exc:
        raise RuntimeError(f"lms load timed out after 180s: {exc}") from exc
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
        "config_changed": cfg_changed,
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
        up_err = ""
        try:
            up = _run_lms_cmd(lms_bin, ["daemon", "up", "--json"], timeout_s=30.0)
            up_err = (up.stderr or up.stdout or "").strip()
        except (subprocess.TimeoutExpired, RuntimeError) as exc:
            up_err = str(exc)
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
            err = up_err or daemon["summary"]
            raise RuntimeError(f"Failed to start Bionic headless daemon: {err}")

    srv = probe_server_models(api_url, model_id=model_id, timeout_s=2.0)
    if not srv["reachable"]:
        port = urllib.parse.urlparse(api_url).port or 1234
        try:
            st = _run_lms_cmd(lms_bin, ["server", "start", "--bind", "127.0.0.1", "--port", str(port)], timeout_s=20.0)
        except subprocess.TimeoutExpired as exc:
            raise RuntimeError(f"lms server start timed out: {exc}") from exc
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
    try:
        ul = _run_lms_cmd(lms_bin, ["unload", model_id], timeout_s=30.0)
    except subprocess.TimeoutExpired as exc:
        raise RuntimeError(f"lms unload timed out: {exc}") from exc
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
    try:
        _run_lms_cmd(lms_bin, ["unload", "--all"], timeout_s=30.0)
        st = _run_lms_cmd(lms_bin, ["server", "stop"], timeout_s=20.0)
    except subprocess.TimeoutExpired as exc:
        raise RuntimeError(f"lms server stop timed out: {exc}") from exc
    after = probe_server_models(api_url, model_id=model_id, timeout_s=2.0)
    if st.returncode != 0 and after["reachable"]:
        raise RuntimeError(f"lms server stop failed: {st.stderr.strip() or st.stdout.strip()}")
    return {
        "schema_version": SCHEMA_VERSION,
        "action": "stop-server",
        "server": after,
        "hardware": _read_hw_counters(),
    }


def _safe_job_file(job_id: str, jobs_dir: Path | None = None) -> Path:
    base = _resolve_jobs_dir(jobs_dir).resolve(strict=False)
    clean_id = Path(job_id).name
    if not clean_id or clean_id != job_id or "/" in job_id or "\\" in job_id or ".." in job_id:
        raise SidecarFirewallError(f"[SECURITY_FIREWALL_BLOCKED] Invalid job_id: {job_id}")
    if not clean_id.endswith(".json"):
        clean_id = f"{clean_id}.json"
    cand = (base / clean_id).resolve(strict=False)
    if not _is_path_within(cand, base):
        raise SidecarFirewallError(f"[SECURITY_FIREWALL_BLOCKED] Job path escape rejected: {cand}")
    return cand


def submit_async_job(job_spec: dict[str, Any], *, jobs_dir: Path | None = None) -> dict[str, Any]:
    """Spawn a detached Bionic background job cleanly inside ~/.cache/homunculus_bionic_plugin/jobs/."""
    jdir = _resolve_jobs_dir(jobs_dir)
    jdir.mkdir(parents=True, exist_ok=True)
    os.chmod(jdir, 0o700)
    job_id = f"BJOB-{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}-{uuid.uuid4().hex[:6]}"
    job_path = _safe_job_file(job_id, jdir)
    now_iso = datetime.now(timezone.utc).isoformat(timespec="seconds")
    record = {
        "schema_version": SCHEMA_VERSION,
        "job_id": job_id,
        "status": "running",
        "submitted_at": now_iso,
        "updated_at": now_iso,
        "spec": job_spec,
        "result": None,
        "error": None,
    }
    _write_private_json_atomic(job_path, record)
    env = os.environ.copy()
    env.setdefault("PYTHONDONTWRITEBYTECODE", "1")
    proc = subprocess.Popen(
        [sys.executable, "-B", str(Path(__file__).resolve()), "job-worker", "--job-file", str(job_path)],
        cwd=_safe_subprocess_cwd(),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        start_new_session=True,
        env=env,
    )
    record["worker_pid"] = proc.pid
    _write_private_json_atomic(job_path, record)
    return {
        "ok": True,
        "async_job": True,
        "job_id": job_id,
        "status": "running",
        "worker_pid": proc.pid,
        "job_file": str(job_path),
    }


def _execute_job_worker(job_file: Path) -> int:
    """Run an async sprint job spec and atomically persist the result."""
    import importlib.util

    raw_rec = json.loads(job_file.read_text(encoding="utf-8"))
    spec = raw_rec.get("spec") or {}
    kind = str(spec.get("kind") or "digest")
    kwargs = dict(spec.get("kwargs") or {})
    kwargs["async_job"] = False

    mcp_path = Path(__file__).resolve().parent / "bionic_sidecar" / "bionic_mcp_server.py"
    try:
        mod_spec = importlib.util.spec_from_file_location("bionic_mcp_server", str(mcp_path))
        if mod_spec is None or mod_spec.loader is None:
            raise RuntimeError(f"Could not load {mcp_path}")
        mcp_mod = importlib.util.module_from_spec(mod_spec)
        mod_spec.loader.exec_module(mcp_mod)
        fn_map = {
            "digest": mcp_mod.bionic_digest,
            "repo_audit": mcp_mod.bionic_repo_audit,
            "stage_patch": mcp_mod.bionic_stage_patch,
        }
        if kind not in fn_map:
            raise ValueError(f"Unsupported async job kind: {kind}")
        result = fn_map[kind](**kwargs)
        raw_rec["status"] = "completed" if result.get("ok") else "failed"
        raw_rec["result"] = result
        raw_rec["error"] = result.get("error") if not result.get("ok") else None
        raw_rec["updated_at"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
        _write_private_json_atomic(job_file, raw_rec)
        return 0 if result.get("ok") else 1
    except Exception as exc:
        raw_rec["status"] = "failed"
        raw_rec["error"] = str(exc)
        raw_rec["updated_at"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
        _write_private_json_atomic(job_file, raw_rec)
        return 1


def get_job_status(
    job_id: str,
    *,
    wait_seconds: float = 0.0,
    include_result: bool = True,
    jobs_dir: Path | None = None,
) -> dict[str, Any]:
    """Inspect or wait cleanly for an async Bionic sprint job at a frontier stop point."""
    jpath = _safe_job_file(job_id, jobs_dir)
    if not jpath.is_file():
        raise FileNotFoundError(f"Unknown Bionic job_id '{job_id}' ({jpath} not found)")
    deadline = time.monotonic() + max(0.0, float(wait_seconds))
    while True:
        rec = json.loads(jpath.read_text(encoding="utf-8"))
        if rec.get("status") != "running":
            break
        wpid = int(rec.get("worker_pid") or 0)
        if wpid and not _pid_alive(wpid):
            time.sleep(0.05)
            rec = json.loads(jpath.read_text(encoding="utf-8"))
            if rec.get("status") == "running":
                rec["status"] = "failed"
                rec["error"] = rec.get("error") or f"Background worker PID {wpid} exited without writing completion state."
            break
        if time.monotonic() >= deadline:
            break
        time.sleep(0.2)

    out = {
        "ok": True,
        "job_id": rec.get("job_id", job_id),
        "status": rec.get("status"),
        "submitted_at": rec.get("submitted_at"),
        "updated_at": rec.get("updated_at"),
        "worker_pid": rec.get("worker_pid"),
        "error": rec.get("error"),
    }
    if include_result:
        out["result"] = rec.get("result")
    return out


def list_jobs(limit: int = 20, *, jobs_dir: Path | None = None) -> dict[str, Any]:
    jdir = _resolve_jobs_dir(jobs_dir)
    rows: list[dict[str, Any]] = []
    if jdir.is_dir():
        for cand in sorted(jdir.glob("BJOB-*.json"), reverse=True)[:limit]:
            try:
                rec = json.loads(cand.read_text(encoding="utf-8"))
                rows.append(
                    {
                        "job_id": rec.get("job_id"),
                        "status": rec.get("status"),
                        "kind": (rec.get("spec") or {}).get("kind"),
                        "submitted_at": rec.get("submitted_at"),
                        "updated_at": rec.get("updated_at"),
                    }
                )
            except (OSError, json.JSONDecodeError):
                continue
    return {"ok": True, "jobs_dir": str(jdir), "jobs": rows}


def _normalize_control_cli_action(action: str) -> str:
    norm = action.strip().lower().replace("_", "-")
    aliases = {"load-profile": "load"}
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
                f"VRAM={hw['vram_used_gib']} GiB (free={hw['vram_free_gib']} GiB, GTT={hw['gtt_used_gib']} GiB) | "
                f"{res['scorecard']['formatted']}"
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
    elif action_norm == "scorecard-reset":
        res = reset_scorecard(
            archive=not bool(getattr(args, "no_archive", False)),
            epoch_label=str(getattr(args, "epoch_label", "v2.3") or "v2.3"),
        )
    else:  # pragma: no cover
        raise ValueError(f"Unsupported control action: {args.action}")

    print(json.dumps(res, indent=2) if args.json else f"[OK] control {action_norm} completed.")
    return 0


def cmd_job_worker(args: argparse.Namespace) -> int:
    return _execute_job_worker(Path(args.job_file))


def cmd_job_status(args: argparse.Namespace) -> int:
    res = get_job_status(args.job_id, wait_seconds=0.0)
    print(json.dumps(res, indent=2) if args.json else f"{res['job_id']}: {res['status']}")
    return 0


def cmd_job_collect(args: argparse.Namespace) -> int:
    res = get_job_status(args.job_id, wait_seconds=float(args.wait_seconds))
    print(json.dumps(res, indent=2) if args.json else f"{res['job_id']}: {res['status']}")
    return 0


def cmd_job_wait(args: argparse.Namespace) -> int:
    res = get_job_status(args.job_id, wait_seconds=float(args.timeout_seconds))
    print(json.dumps(res, indent=2) if args.json else f"{res['job_id']}: {res['status']}")
    return 0


def cmd_job_list(args: argparse.Namespace) -> int:
    res = list_jobs(limit=int(args.limit))
    print(json.dumps(res, indent=2) if args.json else f"jobs={len(res['jobs'])}")
    return 0


def cmd_verdict(args: argparse.Namespace) -> int:
    res = apply_call_verdict(args.call_id, args.verdict, note=args.note or "")
    print(json.dumps(res, indent=2) if args.json else res["formatted"])
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

    # 10. Context slice parsing (#Lstart-Lend), cross-repo 4C without --repo, and unclosed fence extraction
    p_slice, rng_slice = parse_context_spec("/tmp/sample.py#L10-L25")
    assert p_slice == Path("/tmp/sample.py") and rng_slice == (10, 25)
    assert extract_staged_code("```python\nx = 1\n") == "x = 1\n"
    with tempfile.TemporaryDirectory() as td:
        td_p = Path(td)
        git_repo = td_p / "git_a"
        outside = td_p / "outside"
        git_repo.mkdir()
        outside.mkdir()
        subprocess.run(["git", "init", "-q", str(git_repo)], check=True)
        (outside / "leak.txt").write_text("secret\n", encoding="utf-8")
        esc = git_repo / "escape_no_repo.txt"
        esc.symlink_to(outside / "leak.txt")
        try:
            validate_input_paths([esc], repo_root=None, require_exists=True)
            raise AssertionError("Expected cross-repo 4C block even when repo_root=None")
        except SidecarFirewallError:
            pass
    checks.append("context_slice_unclosed_fence_and_auto_repo_4c")

    # 11. Effort resolution, HIGH 4096 floor, and soft-vs-hard ETA separation
    assert resolve_effort_and_mode("standard", None) == ("standard", "fast"), "effort standard mapping"
    assert resolve_effort_and_mode("high", None) == ("high", "deep"), "effort high mapping"
    assert resolve_effective_max_tokens("deep", None) == 8192, "deep default max_tokens"
    assert resolve_effective_max_tokens("deep", 1024) == 4096, "deep min 4096 floor"

    # KV slot/pool cap prevents 3+ heavy concurrent deep slots (>35.5k tok) from saturating GPU decode
    with tempfile.TemporaryDirectory() as td_kv:
        kv_file = Path(td_kv) / "kv_pool_state.json"
        with acquire_kv_budget(18000, 57344, timeout_s=2.0, kv_state_path=kv_file):
            try:
                with acquire_kv_budget(18000, 57344, timeout_s=0.3, kv_state_path=kv_file):
                    raise AssertionError("Expected 35.5k pool / heavy slot cap to block 2nd 18k slot")
            except RuntimeError as kv_exc:
                assert "KV_POOL_CAPACITY_EXCEEDED" in str(kv_exc), f"unexpected kv err: {kv_exc}"
    eta_soft = estimate_eta(
        mode="fast",
        prompt_bytes=0,
        prompt_tokens_override=46000,
        max_tokens=2048,
        max_eta_seconds=60.0,
        calibrated_output=True,
        loaded_ctx_override=57344,
    )
    assert eta_soft["hard_tripped"] is False, f"unexpected hard trip: {eta_soft}"
    assert eta_soft["soft_eta_exceeded"] is True, f"expected soft_eta_exceeded: {eta_soft}"
    assert eta_soft["tripped"] is True, f"expected tripped=True on raw estimate: {eta_soft}"
    with tempfile.TemporaryDirectory() as td_eta:
        old_tlog_eta = os.environ.get("BIONIC_SIDECAR_TELEMETRY_LOG")
        os.environ["BIONIC_SIDECAR_TELEMETRY_LOG"] = str(Path(td_eta) / "tel.jsonl")
        try:
            soft_ok = _enforce_eta_or_raise(
                mode="fast",
                prompt_bytes=0,
                prompt_tokens_override=46000,
                max_tokens=2048,
                max_eta_seconds=60.0,
                expected_turns=1,
                force_slow=False,
                calibrated_output=True,
                allow_soft_eta_overrun=True,
                loaded_ctx_override=57344,
            )
            assert soft_ok.get("soft_eta_advisory") is True, f"expected soft_eta_advisory: {soft_ok}"
            assert soft_ok["verdict"] == "RUN_LOCALLY_WITH_ETA_ADVISORY", f"unexpected verdict: {soft_ok}"
            try:
                _enforce_eta_or_raise(
                    mode="fast",
                    prompt_bytes=0,
                    prompt_tokens_override=60000,
                    max_tokens=2048,
                    max_eta_seconds=60.0,
                    expected_turns=1,
                    force_slow=False,
                    calibrated_output=True,
                    allow_soft_eta_overrun=True,
                    loaded_ctx_override=57344,
                )
                raise AssertionError("Expected hard ctx overflow SidecarEtaTrippedError at 60000 tok")
            except SidecarEtaTrippedError:
                pass
        finally:
            if old_tlog_eta is None:
                os.environ.pop("BIONIC_SIDECAR_TELEMETRY_LOG", None)
            else:
                os.environ["BIONIC_SIDECAR_TELEMETRY_LOG"] = old_tlog_eta
    checks.append("effort_tiers_high_floor_and_soft_eta_overrun")

    # 12. Lifetime scorecard seed, atomic update, slow_self_heal flag, idempotent verdict downgrade, and quota savings
    with tempfile.TemporaryDirectory() as td:
        td_p = Path(td)
        tlog = td_p / "sidecar_usage_telemetry.jsonl"
        old_tlog = os.environ.get("BIONIC_SIDECAR_TELEMETRY_LOG")
        os.environ["BIONIC_SIDECAR_TELEMETRY_LOG"] = str(tlog)
        try:
            tlog.write_text(
                "\n".join(
                    [
                        json.dumps({"cmd": "query", "finish_reason": "stop", "mode": "fast", "elapsed_s": 5.0}),
                        json.dumps({"cmd": "query", "finish_reason": "length", "mode": "fast", "elapsed_s": 6.0}),
                        json.dumps({"cmd": "query", "tripped": True, "mode": "fast", "elapsed_s": 0.0}),
                    ]
                )
                + "\n",
                encoding="utf-8",
            )
            sc = load_or_init_scorecard()
            assert sc["clean"] == 1 and sc["corrected"] == 1 and sc["healed"] == 0, f"bad seed: {sc}"
            rec1 = record_call_outcome(
                verdict="clean",
                cmd="query",
                effort="standard",
                mode="fast",
                elapsed_s=2.5,
            )
            assert rec1["clean"] == 2, f"expected clean=2: {rec1}"
            rec2 = record_call_outcome(
                verdict="healed",
                cmd="stage-code",
                effort="high",
                mode="deep",
                elapsed_s=15.0,
                heal_elapsed_s=50.0,
            )
            assert rec2["healed"] == 1 and rec2["slow_self_heal"] is True, f"expected healed+slow: {rec2}"
            v1 = apply_call_verdict(rec1["call_id"], "corrected", note="unit_downgrade")
            v2 = apply_call_verdict(rec1["call_id"], "corrected", note="unit_downgrade_repeat")
            assert v1["clean"] == 1 and v1["corrected"] == 2, f"v1 mismatch: {v1}"
            assert v2["clean"] == 1 and v2["corrected"] == 2, f"v2 idempotency mismatch: {v2}"
            record_usage_telemetry(
                {
                    "cmd": "stage-code",
                    "effort": "high",
                    "mode": "deep",
                    "prompt_tokens": 2000,
                    "completion_tokens": 500,
                    "elapsed_s": 15.0,
                    "finish_reason": "stop",
                }
            )
            quota = estimate_quota_savings()
            assert quota["by_effort"]["standard"]["calls"] >= 1, f"std quota missing: {quota}"
            assert quota["by_effort"]["high"]["calls"] >= 1, f"high quota missing: {quota}"
            assert quota["total_weighted_frontier_equiv_tokens"] > 0, f"weighted quota <= 0: {quota}"
        finally:
            if old_tlog is None:
                os.environ.pop("BIONIC_SIDECAR_TELEMETRY_LOG", None)
            else:
                os.environ["BIONIC_SIDECAR_TELEMETRY_LOG"] = old_tlog
    checks.append("scorecard_seed_healed_idempotent_verdict_and_quota")

    # 13. KV admission lockfile guard, gpu-max config, and config-change reload detection
    cfg_max = build_concrete_model_config("gpu-max")
    fields_max = {f["key"]: f["value"] for f in cfg_max["load"]["fields"]}
    op_max = {f["key"]: f["value"] for f in cfg_max["operation"]["fields"]}
    assert fields_max["llm.load.contextLength"] == 57344
    assert fields_max["llm.load.numCpuExpertLayersRatio"] == 0.52
    assert fields_max["llm.load.llama.cpuThreadPoolSize"] == 10
    assert op_max["llm.prediction.llama.cpuThreads"] == 10
    assert fields_max["llm.load.offloadKVCacheToGpu"] is True

    with tempfile.TemporaryDirectory() as td:
        td_p = Path(td)
        old_tlog = os.environ.get("BIONIC_SIDECAR_TELEMETRY_LOG")
        os.environ["BIONIC_SIDECAR_TELEMETRY_LOG"] = str(td_p / "tel.jsonl")
        try:
            with acquire_kv_budget(40000, loaded_ctx=57344, timeout_s=0.2):
                try:
                    with acquire_kv_budget(20000, loaded_ctx=57344, timeout_s=0.1):
                        raise AssertionError("Expected KV pool capacity block")
                except RuntimeError:
                    pass
        finally:
            if old_tlog is None:
                os.environ.pop("BIONIC_SIDECAR_TELEMETRY_LOG", None)
            else:
                os.environ["BIONIC_SIDECAR_TELEMETRY_LOG"] = old_tlog

        # Mock _control_load config_changed diff reload
        lms_log = td_p / "lms_calls.log"
        fake_lms2 = td_p / "fake_lms2"
        fake_lms2.write_text(
            f'#!/bin/sh\necho "$@" >> "{lms_log}"\nexit 0\n',
            encoding="utf-8",
        )
        os.chmod(fake_lms2, 0o755)
        cfg_file = td_p / "cfg.json"

        class _ReloadHandler(http.server.BaseHTTPRequestHandler):
            def do_GET(self) -> None:  # noqa: N802
                if self.path == "/api/v0/models":
                    body = json.dumps(
                        {"data": [{"id": DEFAULT_MODEL_ID, "state": "loaded", "loaded_context_length": 57344}]}
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

        srv_rl = http.server.HTTPServer(("127.0.0.1", 0), _ReloadHandler)
        th_rl = threading.Thread(target=srv_rl.serve_forever, daemon=True)
        th_rl.start()
        old_rl_port = os.environ.get("BIONIC_ALLOW_CUSTOM_LOOPBACK_PORT")
        os.environ["BIONIC_ALLOW_CUSTOM_LOOPBACK_PORT"] = "1"
        try:
            rl_api = f"http://127.0.0.1:{srv_rl.server_port}/v1"
            r1 = _control_load(rl_api, DEFAULT_MODEL_ID, "gpu-max", fake_lms2, cfg_file)
            assert r1["reloaded"] is True and r1["config_changed"] is True, f"r1 mismatch: {r1}"
            r2 = _control_load(rl_api, DEFAULT_MODEL_ID, "gpu-max", fake_lms2, cfg_file)
            assert r2["already_loaded"] is True and r2["reloaded"] is False, f"r2 mismatch: {r2}"
            # Mutate cached config externally so cfg_changed trips even with same context length
            cfg_file.write_text(json.dumps({"preset": "stale"}), encoding="utf-8")
            r3 = _control_load(rl_api, DEFAULT_MODEL_ID, "gpu-max", fake_lms2, cfg_file)
            assert r3["reloaded"] is True and r3["config_changed"] is True, f"r3 mismatch: {r3}"
        finally:
            if old_rl_port is None:
                os.environ.pop("BIONIC_ALLOW_CUSTOM_LOOPBACK_PORT", None)
            else:
                os.environ["BIONIC_ALLOW_CUSTOM_LOOPBACK_PORT"] = old_rl_port
            srv_rl.shutdown()
            srv_rl.server_close()
    checks.append("kv_budget_guard_gpu_max_and_config_diff_reload")

    # 14. Async job ID containment firewall
    for bad_jid in ("../escape", "/etc/passwd", "a/b", ""):
        try:
            _safe_job_file(bad_jid)
            raise AssertionError(f"Expected firewall block on job_id={bad_jid!r}")
        except SidecarFirewallError:
            pass
    checks.append("async_job_id_containment_firewall")

    # 15. Lossless full-context diff deduplication & stage ETA V2.1 bounds
    with tempfile.TemporaryDirectory() as td_dedup:
        repo_dd = Path(td_dedup)
        subprocess.run(["git", "init", "-q", str(repo_dd)], check=True)
        subprocess.run(["git", "-C", str(repo_dd), "config", "user.email", "test@example.com"], check=True)
        subprocess.run(["git", "-C", str(repo_dd), "config", "user.name", "Tester"], check=True)
        bom_dd = repo_dd / "BOM.md"
        bom_dd.write_text(
            "# BOM\n"
            "OLD_BOLT_SPEC\n"
            "[Bolt](https://kb-3d.com/store/same-bolt-999.html?affp=6182) | 4 | old desc\n"
            "[Old](https://example.com/removed-link) | 1 | gone\n"
            "SHARED_LINE\n",
            encoding="utf-8",
        )
        subprocess.run(["git", "-C", str(repo_dd), "add", "BOM.md"], check=True)
        subprocess.run(["git", "-C", str(repo_dd), "commit", "-q", "-m", "init"], check=True)
        bom_dd.write_text(
            "# BOM\n"
            "NEW_BOLT_SPEC\n"
            "[Bolt](https://kb-3d.com/store/same-bolt-999.html?affp=6182) | 4 | new desc\n"
            "[New](https://example.com/added-link) | 1 | added\n"
            "SHARED_LINE\n",
            encoding="utf-8",
        )

        dedup_full, _ = assemble_prompt_payload(
            user_prompt="check diff",
            context_files=[bom_dd],
            repo_root=repo_dd,
            include_git_diff=True,
            sys_prompt="sys",
        )
        assert "OLD_BOLT_SPEC" in dedup_full, "HEAD '-' deletion line missing in deduped diff"
        assert "see verbatim BOM.md#L" in dedup_full, "Expected verbatim reference placeholder in deduped diff"
        assert dedup_full.count("NEW_BOLT_SPEC") == 1, "Working-tree addition should appear once (in full file)"
        assert "[Bolt](=)" in dedup_full, "Expected unchanged URL in HEAD '-' line to compact to (=)"
        assert "https://example.com/removed-link" in dedup_full, "Changed/removed URL must remain verbatim"

        dedup_slice, _ = assemble_prompt_payload(
            user_prompt="check slice",
            context_files=[bom_dd],
            repo_root=repo_dd,
            include_git_diff=True,
            sys_prompt="sys",
            slice_ranges={bom_dd: (1, 1)},
        )
        assert "+NEW_BOLT_SPEC" in dedup_slice, "Sliced context should keep full '+' diff hunks verbatim"

    eta_stg_small = estimate_eta(
        mode="fast",
        prompt_bytes=2600,
        sys_prompt_bytes=2350,
        max_tokens=800,
        calibrated_output=True,
        cmd_name="bionic_stage_patch",
    )
    assert eta_stg_small["est_output_tokens"] < 120, f"expected compact stage out <120: {eta_stg_small}"
    eta_retry_small = estimate_eta(
        mode="fast",
        prompt_bytes=2800,
        sys_prompt_bytes=2350,
        max_tokens=2048,
        calibrated_output=True,
        cmd_name="bionic_stage_patch_retry",
        target_code_bytes=30,
    )
    assert eta_retry_small["est_output_tokens"] < 80, f"expected retry out <80: {eta_retry_small}"
    checks.append("full_context_diff_dedup_and_stage_eta_v2_1")

    # 16. V2.3 headless prompt bloat removal, retry seed dedup, scorecard reset + relative metrics, & chunk planner
    hp_text, hp_src = load_system_prompt()
    assert hp_src == "headless_api_v2_3", f"unexpected headless prompt source: {hp_src}"
    assert len(hp_text.encode("utf-8")) <= 1050, f"headless prompt bloat: {len(hp_text.encode('utf-8'))} B"
    for must_have in ("deleted '-' diff lines", "SHCS/BHCS", "?affp=", "ZERO_ADHOC_CAD_PARSING"):
        assert must_have in hp_text, f"headless prompt missing guard: {must_have}"

    with tempfile.TemporaryDirectory() as td_v23:
        td_p23 = Path(td_v23)
        tlog23 = td_p23 / "sidecar_usage_telemetry.jsonl"
        old_t23 = os.environ.get("BIONIC_SIDECAR_TELEMETRY_LOG")
        os.environ["BIONIC_SIDECAR_TELEMETRY_LOG"] = str(tlog23)
        try:
            tlog23.write_text(
                "\n".join(
                    [
                        json.dumps({"cmd": "bionic_stage_patch", "verdict": "healed", "elapsed_s": 2.0}),
                        json.dumps({"cmd": "bionic_stage_patch_retry", "is_retry": True, "finish_reason": "length", "elapsed_s": 1.0}),
                        json.dumps({"cmd": "bionic_digest", "synthetic_fault": True, "finish_reason": "length", "elapsed_s": 0.4}),
                        json.dumps({"cmd": "bionic_digest", "finish_reason": "length", "elapsed_s": 5.0}),
                    ]
                )
                + "\n",
                encoding="utf-8",
            )
            seed23 = _seed_counts_from_telemetry(tlog23)
            assert seed23["clean"] == 0 and seed23["healed"] == 1 and seed23["corrected"] == 1, f"retry/synth seed leak: {seed23}"
            # Reset fails closed without --user-confirmed
            ns_reset_no = argparse.Namespace(
                api_url=DEFAULT_API_URL,
                model=DEFAULT_MODEL_ID,
                action="scorecard-reset",
                profile="gpu-daily",
                user_confirmed=False,
                dry_run=False,
                epoch_label="v2.3",
                no_archive=False,
                json=True,
            )
            try:
                cmd_control(ns_reset_no)
                raise AssertionError("Expected USER_CONFIRMATION_REQUIRED on scorecard-reset")
            except SidecarFirewallError:
                pass
            rst = reset_scorecard(archive=True, epoch_label="v2.3")
            assert rst["ok"] is True and rst["previous_epoch"]["usable_pct"] == 50.0, f"bad archive prev: {rst}"
            assert _resolve_scorecard_archive_path().is_file()
            assert "epoch v2.3: 0 calls" in format_lifetime_scorecard()
            record_call_outcome(verdict="clean", cmd="bionic_digest", elapsed_s=1.5)
            fmt_after = format_lifetime_scorecard()
            assert "100.0% usable, 0.0% corr | +50.0% vs pre-v2.3" in fmt_after, f"bad rel fmt: {fmt_after}"
            rst_same = reset_scorecard(archive=True, epoch_label="v2.3")
            assert rst_same["previous_epoch"]["epoch_label"] == "pre-v2.3", f"same-epoch reset clobbered prev_epoch: {rst_same}"
            assert rst_same["previous_epoch"]["usable_pct"] == 50.0, f"bad prev usable_pct: {rst_same}"
        finally:
            if old_t23 is None:
                os.environ.pop("BIONIC_SIDECAR_TELEMETRY_LOG", None)
            else:
                os.environ["BIONIC_SIDECAR_TELEMETRY_LOG"] = old_t23

        big_py = td_p23 / "big_mod.py"
        big_py.write_text(
            "\n".join(f"def fn_{i}():\n    return '{'x' * 70}'" for i in range(400)) + "\n",
            encoding="utf-8",
        )
        planned = plan_line_preserving_chunks([big_py], target_chunk_bytes=8000)
        assert len(planned) >= 3, f"expected >=3 chunks, got {len(planned)}"
        assert planned[0][1] == 1 and planned[-1][2] == 800, f"bad range: {planned[0]}..{planned[-1]}"
        for prev_c, next_c in zip(planned, planned[1:]):
            assert prev_c[2] + 1 == next_c[1], f"non-contiguous chunks: {prev_c} -> {next_c}"
    checks.append("v2_3_headless_prompt_scorecard_reset_and_chunk_planner")

    # 17. V2.4 packed multi-file chunk batches, ETA_CAL_V2_4_1 deep scaling, and decode/wall tok/s separation
    assert ETA_CALIBRATION_VERSION == "ETA_CAL_V2_4_1"
    with tempfile.TemporaryDirectory() as td_v24:
        td_p24 = Path(td_v24)
        f_a = td_p24 / "a.md"
        f_b = td_p24 / "b.md"
        f_c = td_p24 / "c.md"
        f_big = td_p24 / "big.md"
        f_a.write_text("# A\n" + ("alpha row 1\n" * 60), encoding="utf-8")
        f_b.write_text("# B\n" + ("beta row 2\n" * 60), encoding="utf-8")
        f_c.write_text("# C\n" + ("gamma row 3\n" * 60), encoding="utf-8")
        f_big.write_text("\n".join(f"- item {i}: val {i}" for i in range(440)) + "\n", encoding="utf-8")
        raw_ch24 = plan_line_preserving_chunks([f_a, f_b, f_c, f_big], target_chunk_bytes=18000)
        # 439+ lines splits into >=2 slices; 3 small files pack together, same-file slices stay separated
        big_slices = [c for c in raw_ch24 if c[0] == f_big]
        assert len(big_slices) >= 2, f"expected 440-line file split into >=2 slices: {big_slices}"
        batches24 = pack_chunk_batches(raw_ch24, max_batch_bytes=20000, max_batch_lines=420, max_slices_per_batch=4)
        assert len(batches24) < len(raw_ch24), f"expected multi-file packing: {len(batches24)} vs {len(raw_ch24)}"
        for b24 in batches24:
            paths_in_b = [item[0] for item in b24]
            assert len(paths_in_b) == len(set(paths_in_b)), f"duplicate file in same batch: {b24}"

    eta_deep_short = estimate_eta(mode="deep", prompt_bytes=2200, calibrated_output=True, cmd_name="bionic_digest")
    eta_deep_long = estimate_eta(mode="deep", prompt_bytes=28000, calibrated_output=True, cmd_name="bionic_digest")
    assert eta_deep_short["est_output_tokens"] < eta_deep_long["est_output_tokens"]
    assert eta_deep_short["predicted_eta_s"] < 60.0, f"short deep eta still over-predicted: {eta_deep_short}"
    checks.append("v2_4_chunk_packing_eta_scaling_and_tok_s_fields")

    # 20. V2.4.2 exclusive KV slot serialization for full deep HIGH calls + dual-slot mapper concurrency
    with tempfile.TemporaryDirectory() as td_kv242:
        kv_f = Path(td_kv242) / "kv_pool_state.json"
        assert has_active_exclusive_kv_slot(kv_f) is False
        with acquire_kv_budget(12000, loaded_ctx=57344, timeout_s=0.1, kv_state_path=kv_f, exclusive=True):
            assert has_active_exclusive_kv_slot(kv_f) is True
            try:
                with acquire_kv_budget(4000, loaded_ctx=57344, timeout_s=0.1, kv_state_path=kv_f, exclusive=False):
                    raise AssertionError("Expected exclusive deep KV slot to block second concurrent slot")
            except RuntimeError:
                pass
        assert has_active_exclusive_kv_slot(kv_f) is False
        # Dual-slot mapper parallelism (exclusive=False, <24K tok each) still permits 2 concurrent slots
        with acquire_kv_budget(12000, loaded_ctx=57344, timeout_s=0.2, kv_state_path=kv_f, exclusive=False):
            assert has_active_exclusive_kv_slot(kv_f) is False
            with acquire_kv_budget(12000, loaded_ctx=57344, timeout_s=0.2, kv_state_path=kv_f, exclusive=False):
                assert has_active_exclusive_kv_slot(kv_f) is False
    daily_load = {f["key"]: f["value"] for f in build_concrete_model_config("gpu-daily")["load"]["fields"]}
    daily_par = daily_load["llm.load.llama.argumentsOverride"]["overrideParameters"][0]
    assert daily_par == {"key": "--parallel", "value": "2"}, f"unexpected gpu-daily parallel cfg: {daily_par}"
    checks.append("v242_exclusive_deep_kv_slot_and_mapper_parallelism")

    # 21. V2.4.3 multi-slice same-file preservation + identical-spec deduplication
    with tempfile.TemporaryDirectory() as td_ms:
        ms_file = Path(td_ms) / "multi.py"
        ms_file.write_text("\n".join(f"val_{i} = {i}" for i in range(1, 31)) + "\n", encoding="utf-8")
        ms_files, ms_slices, _ = parse_and_validate_context_items(
            [f"{ms_file}#L2-L5", f"{ms_file}#L2-L5", f"{ms_file}#L18-L21"],
            repo_root=Path(td_ms),
            require_exists=True,
        )
        assert len(ms_files) == 2 and ms_slices == [(2, 5), (18, 21)], f"unexpected slice dedup: {ms_slices}"
        ms_asm, ms_meta = assemble_prompt_payload(
            user_prompt="Inspect both ranges",
            context_files=ms_files,
            repo_root=Path(td_ms),
            include_git_diff=False,
            sys_prompt="sys",
            context_slices=ms_slices,
        )
        assert [m["label"] for m in ms_meta] == ["multi.py#L2-L5", "multi.py#L18-L21"], f"unexpected meta: {ms_meta}"
        assert "val_3 = 3" in ms_asm and "val_19 = 19" in ms_asm, "Both non-overlapping same-file slices must appear"
    checks.append("v243_multi_slice_same_file_preservation")

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
    common.add_argument("--system-prompt", default=None)
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
        p.add_argument("--effort", choices=tuple(EFFORT_TIERS), default=None)
        p.add_argument("--mode", choices=tuple(PROFILES.keys()), default=None)
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
        choices=(
            "status",
            "start-headless",
            "load",
            "load_profile",
            "load-profile",
            "unload",
            "stop-server",
            "scorecard-reset",
            "scorecard_reset",
        ),
    )
    p_ctrl.add_argument("--profile", choices=tuple(CONTROL_PROFILES.keys()), default="gpu-daily")
    p_ctrl.add_argument("--user-confirmed", action="store_true")
    p_ctrl.add_argument("--dry-run", action="store_true")
    p_ctrl.add_argument("--epoch-label", default="v2.3")
    p_ctrl.add_argument("--no-archive", action="store_true")

    p_jw = sub.add_parser("job-worker", parents=[common_sub], help="Internal background sprint job runner")
    p_jw.add_argument("--job-file", required=True)

    p_js = sub.add_parser("job-status", parents=[common_sub], help="Check async Bionic sprint job status")
    p_js.add_argument("--job-id", required=True)

    p_jc = sub.add_parser("job-collect", parents=[common_sub], help="Collect async Bionic sprint job output")
    p_jc.add_argument("--job-id", required=True)
    p_jc.add_argument("--wait-seconds", type=float, default=0.0)

    p_jwait = sub.add_parser("job-wait", parents=[common_sub], help="Wait for async Bionic sprint job")
    p_jwait.add_argument("--job-id", required=True)
    p_jwait.add_argument("--timeout-seconds", type=float, default=120.0)

    p_jlist = sub.add_parser("job-list", parents=[common_sub], help="List recent async Bionic sprint jobs")
    p_jlist.add_argument("--limit", type=int, default=20)

    p_verd = sub.add_parser("verdict", parents=[common_sub], help="Update verdict for a tracked Bionic call_id")
    p_verd.add_argument("--call-id", required=True)
    p_verd.add_argument("--verdict", required=True, choices=("clean", "corrected", "healed"))
    p_verd.add_argument("--note", default="")

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
            "job-worker": cmd_job_worker,
            "job-status": cmd_job_status,
            "job-collect": cmd_job_collect,
            "job-wait": cmd_job_wait,
            "job-list": cmd_job_list,
            "verdict": cmd_verdict,
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
