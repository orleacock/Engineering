#!/usr/bin/env python3
"""
Fused MCP Server for LM Studio Bionic Local Sidecar (`bionic_mcp_server.py`).

Uses `MCPServer` via `importlib.util.find_spec("mcp.server")` when invoked under the
Antigravity MCP venv, with pure Python 3.10+ stdlib compatibility for `--self-test`
and `--status` diagnostics. Shares all firewalls, ETA circuit breakers, telemetry,
and `lms` control paths directly from parent `scripts/local_sidecar.py`.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
SCRIPTS_ROOT = SCRIPT_DIR.parent
if str(SCRIPTS_ROOT) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_ROOT))

import local_sidecar  # noqa: E402

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


PLACEHOLDER_LINK_RE = re.compile(r"(?<!!)\[([^\[\]]+)\]\(([^()]*)\)")
PLACEHOLDER_TARGETS = ("...", "tbd", "todo", "url", "<", "path/to/", "example.com")
LL_WS_12_GUARD = (
    "\n\n[GOVERNED SIDE-CAR AUDIT RULES (LL-WS-12)]:\n"
    "1. Cite ONLY exact existing line numbers (relative path#Lstart-Lend) for lines present verbatim.\n"
    "2. Never cite `#L` line anchors from deleted (`-`) diff lines.\n"
    "3. Never expand hardware/fastener acronyms (e.g., BHCS/SHCS) beyond words written in source files.\n"
    "4. Never emit affiliate query parameters (`?affp=`, `dt_id=`, `aff_id=`) or placeholder `[label](...)` links.\n"
    "5. Insert explicit `[TBD: <specific_missing_spec>]` whenever counts, sizes, or ratings are absent.\n"
)


mcp = MCPServer(
    name="bionic_sidecar",
    instructions=(
        "Governed LM Studio Bionic (Qwen3.6-35B-A3B) sidecar connector for Orin's workstation. "
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

    for raw in candidate_paths:
        sec_reason = local_sidecar._inspect_path_security(raw)
        if sec_reason:
            raise local_sidecar.SidecarFirewallError(f"[SECURITY_FIREWALL_BLOCKED] {sec_reason}")
        res = Path(os.path.expanduser(str(raw))).resolve(strict=False)
        if not local_sidecar._is_path_within(res, repo_res):
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


def _resolve_eta_cap(invocation_tier: str) -> tuple[str, float]:
    tier = (invocation_tier or "explicit").strip().lower()
    if tier not in {"auto", "explicit"}:
        raise ValueError(f"Unsupported invocation_tier '{invocation_tier}'; expected 'auto' or 'explicit'.")
    cap = local_sidecar.AUTO_MAX_ETA_SECONDS if tier == "auto" else local_sidecar.DEFAULT_MAX_ETA_SECONDS
    return tier, cap


def _resolve_homunculus_and_memory() -> tuple[Path, Path]:
    hom_env = os.environ.get("HOMUNCULUS_ROOT", "").strip()
    mem_env = os.environ.get("HOMUNCULUS_MEMORY_ROOT", "").strip()
    hom_root = Path(os.path.expanduser(hom_env)) if hom_env else local_sidecar.DEFAULT_HOMUNCULUS_ROOT
    mem_root = Path(os.path.expanduser(mem_env)) if mem_env else local_sidecar.DEFAULT_MEMORY_ROOT
    return hom_root, mem_root


def _normalize_control_action(action: str) -> str:
    norm = (action or "status").strip().lower().replace("_", "-")
    aliases = {"load-profile": "load"}
    norm = aliases.get(norm, norm)
    if norm not in {"status", "start-headless", "load", "unload", "stop-server"}:
        raise ValueError(f"Unsupported control action: {action}")
    return norm


def _firewall_error_response(exc: Exception, op_label: str) -> dict[str, Any]:
    msg = str(exc)
    if "BIONIC_UNLOADED_CONFIRMATION_REQUIRED" in msg:
        return {
            "ok": False,
            "error_code": "BIONIC_UNLOADED_CONFIRMATION_REQUIRED",
            "error": msg,
            "user_notice": (
                "[BIONIC SIDECAR NOTICE] Bionic is currently UNLOADED; ask user confirmation "
                "before calling bionic_control(action='load_profile', user_confirmed=True)."
            ),
        }
    return {
        "ok": False,
        "error_code": "SECURITY_FIREWALL_BLOCKED",
        "error": msg,
        "user_notice": f"[BIONIC SIDECAR NOTICE] {op_label} blocked by security firewall.",
    }


def _control_action_impl(action: str = "status", profile: str = "gpu-daily", user_confirmed: bool = False) -> dict[str, Any]:
    norm_action = _normalize_control_action(action)
    if profile not in local_sidecar.CONTROL_PROFILES:
        raise ValueError(f"Unsupported profile '{profile}'; expected one of {tuple(local_sidecar.CONTROL_PROFILES.keys())}")
    api_url = local_sidecar.validate_loopback_url(local_sidecar.resolve_default_api_url())
    lms_bin = local_sidecar.DEFAULT_LMS_BIN
    cfg_path = local_sidecar.DEFAULT_CONCRETE_CFG_PATH
    appimage_path = local_sidecar.DEFAULT_APPIMAGE_PATH

    if norm_action == "status":
        res = local_sidecar._control_status(api_url, local_sidecar.DEFAULT_MODEL_ID, lms_bin)
        srv = res["server"]
        state_str = "ONLINE_READY" if srv["target_model_loaded"] else ("UNLOADED" if srv["reachable"] else "OFFLINE")
        return {
            "ok": True,
            "state": state_str,
            **res,
            "user_notice": f"[BIONIC SIDECAR NOTICE] Status={state_str} | ctx={srv['loaded_context_length']} | VRAM={res['hardware']['vram_used_gib']} GiB",
        }

    if not user_confirmed:
        raise local_sidecar.SidecarFirewallError(
            f"[USER_CONFIRMATION_REQUIRED] bionic_control('{norm_action}') refuses autonomous start/load/unload/stop without user_confirmed=True."
        )

    if norm_action == "start-headless":
        res = local_sidecar._control_start_headless(api_url, local_sidecar.DEFAULT_MODEL_ID, profile, lms_bin, appimage_path, cfg_path)
    elif norm_action == "load":
        res = local_sidecar._control_load(api_url, local_sidecar.DEFAULT_MODEL_ID, profile, lms_bin, cfg_path)
    elif norm_action == "unload":
        res = local_sidecar._control_unload(api_url, local_sidecar.DEFAULT_MODEL_ID, lms_bin)
    else:
        res = local_sidecar._control_stop_server(api_url, local_sidecar.DEFAULT_MODEL_ID, lms_bin)

    return {
        "ok": True,
        **res,
        "user_notice": f"[BIONIC SIDECAR NOTICE] Executed control action '{norm_action}' (profile={profile}).",
    }


def _ensure_live_process_cwd() -> str:
    """Ensure the MCP process working directory exists even after plugin upgrades."""
    return local_sidecar._safe_subprocess_cwd()


@mcp.tool()
def bionic_control(action: str = "status", profile: str = "gpu-daily", user_confirmed: bool = False) -> dict[str, Any]:
    """Inspect Bionic status or execute user-confirmed remote lifecycle actions (start-headless, load_profile, unload, stop-server)."""
    _ensure_live_process_cwd()
    try:
        return _control_action_impl(action=action, profile=profile, user_confirmed=bool(user_confirmed))
    except local_sidecar.SidecarFirewallError as exc:
        if "USER_CONFIRMATION_REQUIRED" in str(exc):
            return {
                "ok": False,
                "error_code": "USER_CONFIRMATION_REQUIRED",
                "error": str(exc),
                "user_notice": "[BIONIC SIDECAR NOTICE] Action blocked pending explicit user confirmation.",
            }
        return _firewall_error_response(exc, "Control")
    except Exception as exc:
        return {
            "ok": False,
            "error_code": "CONTROL_ERROR",
            "error": str(exc),
            "user_notice": f"[BIONIC SIDECAR NOTICE] Control error: {exc}",
        }


@mcp.tool()
def bionic_digest(
    prompt: str,
    context_files: list[str] | None = None,
    repo: str = "",
    include_git_diff: bool = False,
    mode: str = "fast",
    invocation_tier: str = "auto",
    max_tokens: int = 1200,
) -> dict[str, Any]:
    """Compress bounded files, logs, or git diffs via local Bionic (60s auto / 90s explicit ETA cap)."""
    _ensure_live_process_cwd()
    try:
        tier, max_eta = _resolve_eta_cap(invocation_tier)
        if mode not in local_sidecar.PROFILES:
            raise ValueError(f"Unsupported mode: {mode}")
        api_url = local_sidecar.validate_loopback_url(local_sidecar.resolve_default_api_url())
        sys_prompt, sys_src = local_sidecar.load_system_prompt()
        repo_root = Path(repo) if repo.strip() else None
        repo_resolved = repo_root.resolve(strict=False) if repo_root else None
        validated_files = local_sidecar.validate_input_paths(
            [Path(p) for p in (context_files or [])],
            repo_root=repo_root,
            require_exists=True,
        )
        if not prompt.strip():
            raise ValueError("Prompt must be non-empty.")

        assembled, file_meta = local_sidecar.assemble_prompt_payload(
            user_prompt=prompt.strip(),
            context_files=validated_files,
            repo_root=repo_resolved,
            include_git_diff=bool(include_git_diff),
            sys_prompt=sys_prompt,
        )
        max_toks = int(max_tokens)
        prompt_bytes = len(sys_prompt.encode("utf-8")) + len(assembled.encode("utf-8"))
        eta = local_sidecar._enforce_eta_or_raise(
            mode=mode,
            prompt_bytes=prompt_bytes,
            max_tokens=max_toks,
            max_eta_seconds=max_eta,
            expected_turns=1,
            force_slow=False,
            cmd_name="bionic_digest",
            invocation_tier=tier,
        )
        _, effective_mode = local_sidecar.preflight_live_inference(api_url, local_sidecar.DEFAULT_MODEL_ID, mode)
        if effective_mode != mode:
            eta = local_sidecar._enforce_eta_or_raise(
                mode=effective_mode,
                prompt_bytes=prompt_bytes,
                max_tokens=max_toks,
                max_eta_seconds=max_eta,
                expected_turns=1,
                force_slow=False,
                cmd_name="bionic_digest",
                invocation_tier=tier,
            )
        res = local_sidecar.invoke_chat_completion(
            api_url=api_url,
            model_id=local_sidecar.DEFAULT_MODEL_ID,
            mode=effective_mode,
            system_prompt=sys_prompt,
            user_content=assembled,
            max_tokens=max_toks,
            timeout_s=max(max_eta + 30.0, 120.0),
            preflight_checked=True,
        )
        local_sidecar.record_usage_telemetry(
            {
                "cmd": "bionic_digest",
                "invocation_tier": tier,
                "mode": effective_mode,
                "est_prompt_tokens": eta["est_prompt_tokens"],
                "predicted_eta_s": eta["predicted_eta_s"],
                "max_eta_seconds": max_eta,
                "tripped": False,
                "elapsed_s": res["elapsed_s"],
                "observed_tg_tok_s": res["observed_tg_tok_s"],
                "finish_reason": res["finish_reason"],
            }
        )
        return {
            "ok": True,
            "schema_version": local_sidecar.SCHEMA_VERSION,
            "invocation_tier": tier,
            "system_prompt_source": sys_src,
            "quarantined_draft_warning": "UNVERIFIED LOCAL SIDECAR OUTPUT — verify claims against primary sources before citing.",
            "eta_estimate": eta,
            "context_files": file_meta,
            "completion": res,
            "user_notice": (
                f"[BIONIC SIDECAR NOTICE] Local Bionic ({effective_mode}, {tier}) ran {res['elapsed_s']}s "
                f"({res['prompt_tokens']} prompt / {res['completion_tokens']} out tok)."
            ),
        }
    except local_sidecar.SidecarFirewallError as exc:
        return _firewall_error_response(exc, "Digest")
    except local_sidecar.SidecarEtaTrippedError as exc:
        return {"ok": False, "error_code": "ETA_CIRCUIT_BREAKER_TRIPPED", "error": str(exc), "eta_estimate": exc.estimate, "user_notice": "[BIONIC SIDECAR NOTICE] ETA breaker handed digest back to frontier thread."}
    except Exception as exc:
        return {"ok": False, "error_code": "DIGEST_ERROR", "error": str(exc), "user_notice": f"[BIONIC SIDECAR NOTICE] Digest error: {exc}"}


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
        if cand.suffix.lower() in exts and not local_sidecar._inspect_path_security(cand):
            out.append(cand)
    return out


@mcp.tool()
def bionic_repo_audit(
    repo: str,
    project: str,
    name: str,
    title: str,
    reason: str,
    prompt: str,
    context_files: list[str] | None = None,
    include_git_diff: bool = False,
    mode: str = "fast",
    invocation_tier: str = "explicit",
    max_tokens: int = 2200,
    overwrite: bool = False,
) -> dict[str, Any]:
    """Fused repo audit: audit_repo_docs pre-pass -> Bionic sweep -> Quarantine note -> collision-free verify_claims Pass 1."""
    _ensure_live_process_cwd()
    try:
        tier, max_eta = _resolve_eta_cap(invocation_tier)
        if mode not in local_sidecar.PROFILES:
            raise ValueError(f"Unsupported mode: {mode}")
        api_url = local_sidecar.validate_loopback_url(local_sidecar.resolve_default_api_url())
        sys_prompt, sys_src = local_sidecar.load_system_prompt()
        repo_root = Path(os.path.expanduser(repo))
        repo_sec = local_sidecar._inspect_path_security(repo_root)
        if repo_sec:
            raise local_sidecar.SidecarFirewallError(f"[SECURITY_FIREWALL_BLOCKED] {repo_sec}")
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

        validated_files = local_sidecar.validate_input_paths(
            [Path(p) for p in (context_files or [])],
            repo_root=repo_resolved,
            require_exists=True,
        )

        # 1. Pre-pass deterministic audit_repo_docs.py (catches missing fastener size/counts & styling gaps)
        audit_docs_res: dict[str, Any] = {"ran": False}
        if audit_docs_path.is_file():
            ad_proc = subprocess.run(
                [sys.executable, "-B", str(audit_docs_path), str(repo_resolved)],
                cwd=local_sidecar._safe_subprocess_cwd(repo_resolved),
                capture_output=True,
                text=True,
                timeout=30,
                check=False,
            )
            audit_docs_res = {
                "ran": True,
                "returncode": ad_proc.returncode,
                "output_tail": (ad_proc.stdout + "\n" + ad_proc.stderr).strip()[-3000:],
            }

        # 2. Prompt assembly with LL-WS-12 guardrails & max_tokens >= 2200 floor
        guarded_prompt = f"{prompt.strip()}{LL_WS_12_GUARD}"
        if audit_docs_res.get("ran") and audit_docs_res.get("output_tail"):
            guarded_prompt += f"\n\n[PRE-PASS audit_repo_docs.py TELEMETRY (exit {audit_docs_res['returncode']})]:\n{audit_docs_res['output_tail'][-1500:]}\n"

        assembled, file_meta = local_sidecar.assemble_prompt_payload(
            user_prompt=guarded_prompt,
            context_files=validated_files,
            repo_root=repo_resolved,
            include_git_diff=bool(include_git_diff),
            sys_prompt=sys_prompt,
        )
        min_tok_floor = 2200 if tier == "explicit" else 1200
        effective_max_toks = max(int(max_tokens), min_tok_floor)
        prompt_bytes = len(sys_prompt.encode("utf-8")) + len(assembled.encode("utf-8"))
        eta = local_sidecar._enforce_eta_or_raise(
            mode=mode,
            prompt_bytes=prompt_bytes,
            max_tokens=effective_max_toks,
            max_eta_seconds=max_eta,
            expected_turns=1,
            force_slow=False,
            cmd_name="bionic_repo_audit",
            invocation_tier=tier,
        )
        _, effective_mode = local_sidecar.preflight_live_inference(api_url, local_sidecar.DEFAULT_MODEL_ID, mode)
        if effective_mode != mode:
            eta = local_sidecar._enforce_eta_or_raise(
                mode=effective_mode,
                prompt_bytes=prompt_bytes,
                max_tokens=effective_max_toks,
                max_eta_seconds=max_eta,
                expected_turns=1,
                force_slow=False,
                cmd_name="bionic_repo_audit",
                invocation_tier=tier,
            )
        res = local_sidecar.invoke_chat_completion(
            api_url=api_url,
            model_id=local_sidecar.DEFAULT_MODEL_ID,
            mode=effective_mode,
            system_prompt=sys_prompt,
            user_content=assembled,
            max_tokens=effective_max_toks,
            timeout_s=max(max_eta + 30.0, 150.0),
            preflight_checked=True,
        )
        local_sidecar.record_usage_telemetry(
            {
                "cmd": "bionic_repo_audit",
                "invocation_tier": tier,
                "mode": effective_mode,
                "est_prompt_tokens": eta["est_prompt_tokens"],
                "predicted_eta_s": eta["predicted_eta_s"],
                "max_eta_seconds": max_eta,
                "tripped": False,
                "elapsed_s": res["elapsed_s"],
                "observed_tg_tok_s": res["observed_tg_tok_s"],
                "finish_reason": res["finish_reason"],
            }
        )

        # 3. Sanitize placeholder links & quarantine via memory_gateway.py
        sanitized_content, links_fixed = sanitize_quarantine_placeholder_links(res["content"])
        body_text = (
            f"<!-- local_sidecar provenance: schema={local_sidecar.SCHEMA_VERSION} "
            f"author=\"LM Studio Bionic ({res['model']}, {res['mode']})\" elapsed_s={res['elapsed_s']} "
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
                cwd=local_sidecar._safe_subprocess_cwd(),
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

        # 4. Collision-free verify_claims.py Pass 1
        raw_sources = validated_files if validated_files else _discover_repo_sources(repo_resolved)
        clean_sources, src_warnings = select_collision_free_sources(repo_resolved, raw_sources)
        note_path = Path(str(gw_result.get("note_file") or quar_candidate))
        vrf_res: dict[str, Any] = {"ran": False}
        proj_mem_dir = mem_root / "Projects" / project
        if verify_claims_path.is_file() and note_path.is_file() and clean_sources:
            vrf_cmd = [
                sys.executable,
                "-B",
                str(verify_claims_path),
                "--target",
                str(note_path),
                "--sources",
                *[str(p) for p in clean_sources],
                "--memory-root",
                str(mem_root),
                "--json",
            ]
            if proj_mem_dir.is_dir():
                vrf_cmd.extend(["--project-dir", str(proj_mem_dir)])
            vp = subprocess.run(
                vrf_cmd,
                cwd=local_sidecar._safe_subprocess_cwd(repo_resolved),
                capture_output=True,
                text=True,
                timeout=45,
                check=False,
            )
            vrf_res = {"ran": True, "returncode": vp.returncode}
            try:
                vrf_res["report"] = json.loads(vp.stdout) if vp.stdout.strip() else None
            except json.JSONDecodeError:
                vrf_res["stdout_tail"] = vp.stdout.strip()[-1500:]

        return {
            "ok": True,
            "schema_version": local_sidecar.SCHEMA_VERSION,
            "invocation_tier": tier,
            "system_prompt_source": sys_src,
            "audit_repo_docs": audit_docs_res,
            "eta_estimate": eta,
            "context_files": file_meta,
            "completion_telemetry": {k: v for k, v in res.items() if k != "content"},
            "placeholder_links_sanitized": links_fixed,
            "source_selection_warnings": src_warnings,
            "gateway_receipt": gw_result,
            "verify_claims_pass1": vrf_res,
            "user_notice": (
                f"[BIONIC SIDECAR NOTICE] Quarantined repo audit '{name}' in {res['elapsed_s']}s "
                f"(verify_claims pass1 rc={vrf_res.get('returncode')})."
            ),
        }
    except local_sidecar.SidecarFirewallError as exc:
        return _firewall_error_response(exc, "Repo audit")
    except local_sidecar.SidecarEtaTrippedError as exc:
        return {"ok": False, "error_code": "ETA_CIRCUIT_BREAKER_TRIPPED", "error": str(exc), "eta_estimate": exc.estimate, "user_notice": "[BIONIC SIDECAR NOTICE] Repo audit ETA breaker handed back to frontier thread."}
    except Exception as exc:
        return {"ok": False, "error_code": "AUDIT_ERROR", "error": str(exc), "user_notice": f"[BIONIC SIDECAR NOTICE] Repo audit error: {exc}"}


@mcp.tool()
def bionic_stage_patch(
    target_filename: str,
    prompt: str,
    context_files: list[str] | None = None,
    repo: str = "",
    compare_against: str = "",
    staging_dir: str = str(local_sidecar.DEFAULT_STAGING_DIR),
    mode: str = "fast",
    invocation_tier: str = "auto",
    max_tokens: int = 1600,
) -> dict[str, Any]:
    """Stage isolated scratch code/patch + py_compile + unified diff with <=1 bounded syntax-repair retry."""
    _ensure_live_process_cwd()
    try:
        tier, max_eta = _resolve_eta_cap(invocation_tier)
        if mode not in local_sidecar.PROFILES:
            raise ValueError(f"Unsupported mode: {mode}")
        safe_staging = local_sidecar.validate_staging_dir(Path(staging_dir))
        api_url = local_sidecar.validate_loopback_url(local_sidecar.resolve_default_api_url())
        sys_prompt, _ = local_sidecar.load_system_prompt()
        repo_root = Path(repo) if repo.strip() else None
        repo_resolved = repo_root.resolve(strict=False) if repo_root else None
        validated_files = local_sidecar.validate_input_paths(
            [Path(p) for p in (context_files or [])],
            repo_root=repo_root,
            require_exists=True,
        )
        compare_path = Path(compare_against) if compare_against.strip() else None
        if compare_path is not None:
            local_sidecar.validate_input_paths([compare_path], repo_root=repo_root, require_exists=True)
        if not prompt.strip():
            raise ValueError("Prompt must be non-empty.")

        assembled, _ = local_sidecar.assemble_prompt_payload(
            user_prompt=prompt.strip(),
            context_files=validated_files,
            repo_root=repo_resolved,
            include_git_diff=False,
            sys_prompt=sys_prompt,
        )
        max_toks = int(max_tokens)
        prompt_bytes = len(sys_prompt.encode("utf-8")) + len(assembled.encode("utf-8"))
        eta1 = local_sidecar._enforce_eta_or_raise(
            mode=mode,
            prompt_bytes=prompt_bytes,
            max_tokens=max_toks,
            max_eta_seconds=max_eta,
            expected_turns=1,
            force_slow=False,
            cmd_name="bionic_stage_patch",
            invocation_tier=tier,
        )
        _, effective_mode = local_sidecar.preflight_live_inference(api_url, local_sidecar.DEFAULT_MODEL_ID, mode)
        if effective_mode != mode:
            eta1 = local_sidecar._enforce_eta_or_raise(
                mode=effective_mode,
                prompt_bytes=prompt_bytes,
                max_tokens=max_toks,
                max_eta_seconds=max_eta,
                expected_turns=1,
                force_slow=False,
                cmd_name="bionic_stage_patch",
                invocation_tier=tier,
            )
        res1 = local_sidecar.invoke_chat_completion(
            api_url=api_url,
            model_id=local_sidecar.DEFAULT_MODEL_ID,
            mode=effective_mode,
            system_prompt=sys_prompt,
            user_content=assembled,
            max_tokens=max_toks,
            timeout_s=max(max_eta + 30.0, 150.0),
            preflight_checked=True,
        )
        local_sidecar.record_usage_telemetry(
            {
                "cmd": "bionic_stage_patch",
                "invocation_tier": tier,
                "mode": effective_mode,
                "est_prompt_tokens": eta1["est_prompt_tokens"],
                "predicted_eta_s": eta1["predicted_eta_s"],
                "max_eta_seconds": max_eta,
                "tripped": False,
                "elapsed_s": res1["elapsed_s"],
                "observed_tg_tok_s": res1["observed_tg_tok_s"],
                "finish_reason": res1["finish_reason"],
            }
        )
        receipt = local_sidecar.stage_code_artifact(
            staging_dir=safe_staging,
            target_filename=target_filename,
            generated_text=res1["content"],
            compare_against=compare_path,
            telemetry={"eta": eta1, **{k: v for k, v in res1.items() if k != "content"}},
        )

        attempts = 1
        repair_retried = False
        handed_back_reason: str | None = None
        if receipt["py_compile_ok"] is False:
            remaining_s = max(0.0, round(max_eta - float(res1["elapsed_s"]), 2))
            repair_prompt = (
                f"{prompt.strip()}\n\nPrevious draft failed `py_compile` with:\n{receipt['py_compile_error']}\n"
                f"Fix the Python syntax error and return ONLY the complete corrected file in one code fence.\n\n"
                f"Faulty draft:\n```python\n{local_sidecar.extract_staged_code(res1['content'])}\n```\n"
            )
            repair_bytes = len(sys_prompt.encode("utf-8")) + len(repair_prompt.encode("utf-8"))
            repair_eta = local_sidecar.estimate_eta(
                mode=effective_mode,
                prompt_bytes=repair_bytes,
                max_tokens=max_toks,
                max_eta_seconds=remaining_s,
                expected_turns=1,
            )
            if not repair_eta["tripped"] and remaining_s >= 5.0:
                repair_retried = True
                attempts = 2
                res2 = local_sidecar.invoke_chat_completion(
                    api_url=api_url,
                    model_id=local_sidecar.DEFAULT_MODEL_ID,
                    mode=effective_mode,
                    system_prompt=sys_prompt,
                    user_content=repair_prompt,
                    max_tokens=max_toks,
                    timeout_s=max(remaining_s + 15.0, 45.0),
                    preflight_checked=True,
                )
                local_sidecar.record_usage_telemetry(
                    {
                        "cmd": "bionic_stage_patch_retry",
                        "invocation_tier": tier,
                        "mode": effective_mode,
                        "est_prompt_tokens": repair_eta["est_prompt_tokens"],
                        "predicted_eta_s": repair_eta["predicted_eta_s"],
                        "max_eta_seconds": remaining_s,
                        "tripped": False,
                        "elapsed_s": res2["elapsed_s"],
                        "observed_tg_tok_s": res2["observed_tg_tok_s"],
                        "finish_reason": res2["finish_reason"],
                    }
                )
                receipt = local_sidecar.stage_code_artifact(
                    staging_dir=safe_staging,
                    target_filename=target_filename,
                    generated_text=res2["content"],
                    compare_against=compare_path,
                    telemetry={"eta": repair_eta, **{k: v for k, v in res2.items() if k != "content"}},
                )
            else:
                handed_back_reason = (
                    f"Initial py_compile failed and remaining {tier} budget ({remaining_s:.1f}s) "
                    f"was below repair ETA ({repair_eta['predicted_eta_s']:.1f}s)."
                )

        return {
            "ok": receipt["py_compile_ok"] is not False,
            "invocation_tier": tier,
            "attempts": attempts,
            "repair_retried": repair_retried,
            "handed_back_reason": handed_back_reason,
            **receipt,
            "user_notice": (
                f"[BIONIC SIDECAR NOTICE] Staged {target_filename} in scratch "
                f"(attempts={attempts}, py_compile_ok={receipt['py_compile_ok']})."
            ),
        }
    except local_sidecar.SidecarFirewallError as exc:
        return _firewall_error_response(exc, "Patch staging")
    except local_sidecar.SidecarEtaTrippedError as exc:
        return {"ok": False, "error_code": "ETA_CIRCUIT_BREAKER_TRIPPED", "error": str(exc), "eta_estimate": exc.estimate, "user_notice": "[BIONIC SIDECAR NOTICE] Patch staging ETA breaker handed back to frontier thread."}
    except Exception as exc:
        return {"ok": False, "error_code": "STAGE_ERROR", "error": str(exc), "user_notice": f"[BIONIC SIDECAR NOTICE] Patch staging error: {exc}"}


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

    # 3. Confirmation gate & profile validation in bionic_control
    blocked = bionic_control(action="start_headless", profile="gpu-daily", user_confirmed=False)
    assert blocked["ok"] is False and blocked["error_code"] == "USER_CONFIRMATION_REQUIRED"
    checks.append("bionic_control_confirmation_gate")

    # 4. 60s auto vs 90s explicit ETA & firewall integration
    assert _resolve_eta_cap("auto") == ("auto", 60.0)
    assert _resolve_eta_cap("explicit") == ("explicit", 90.0)
    fw_digest = bionic_digest(prompt="check", context_files=["/home/orin/.gemini/config/mcp_config.json"])
    assert fw_digest["ok"] is False and fw_digest["error_code"] == "SECURITY_FIREWALL_BLOCKED"
    checks.append("eta_tier_and_mcp_firewall_enforcement")

    # 5. Tool discovery check (full MCPServer verification when running in venv)
    tools = _registered_tool_names()
    expected = {"bionic_control", "bionic_digest", "bionic_repo_audit", "bionic_stage_patch"}
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
                    "id": local_sidecar.DEFAULT_MODEL_ID,
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
                if length:
                    self.rfile.read(length)
                state_box["posts"] += 1
                reply_txt = state_box["replies"].pop(0) if state_box["replies"] else "OK"
                body = json.dumps(
                    {
                        "id": "mock-cmp",
                        "model": local_sidecar.DEFAULT_MODEL_ID,
                        "choices": [{"index": 0, "message": {"role": "assistant", "content": reply_txt}, "finish_reason": "stop"}],
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
        old_api = os.environ.get("BIONIC_SIDECAR_API_URL")
        old_tel = os.environ.get("BIONIC_SIDECAR_TELEMETRY_LOG")
        old_custom_port = os.environ.get("BIONIC_ALLOW_CUSTOM_LOOPBACK_PORT")
        telemetry_path = td_p / "telemetry.jsonl"
        os.environ["BIONIC_SIDECAR_API_URL"] = f"http://127.0.0.1:{srv.server_port}/v1"
        os.environ["BIONIC_SIDECAR_TELEMETRY_LOG"] = str(telemetry_path)
        os.environ["BIONIC_ALLOW_CUSTOM_LOOPBACK_PORT"] = "1"
        try:
            # 6a. UNLOADED blocks bionic_digest before any POST (anti-JIT)
            unloaded_res = bionic_digest(prompt="hello", mode="fast", invocation_tier="auto")
            assert unloaded_res["ok"] is False
            assert unloaded_res["error_code"] == "BIONIC_UNLOADED_CONFIRMATION_REQUIRED"
            assert state_box["posts"] == 0

            # 6b. Loaded @ 16384 ctx auto-clamps mode='fast' -> 'cpu-bg' and catches 9.5k prompt guard
            state_box["loaded"] = True
            state_box["ctx"] = 16384
            big_ctx = td_p / "big_ctx.txt"
            big_ctx.write_text(("alpha beta gamma delta epsilon\n" * 1150), encoding="utf-8")
            clamp_res = bionic_digest(
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
            stage_res = bionic_stage_patch(
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
            assert [r["cmd"] for r in tel_rows] == ["bionic_digest", "bionic_stage_patch", "bionic_stage_patch_retry"]
            assert tel_rows[0]["tripped"] is True and tel_rows[0]["mode"] == "cpu-bg"
            assert (telemetry_path.stat().st_mode & 0o777) == 0o600
            checks.append("stage_patch_syntax_retry_and_telemetry")
        finally:
            if old_api is None:
                os.environ.pop("BIONIC_SIDECAR_API_URL", None)
            else:
                os.environ["BIONIC_SIDECAR_API_URL"] = old_api
            if old_tel is None:
                os.environ.pop("BIONIC_SIDECAR_TELEMETRY_LOG", None)
            else:
                os.environ["BIONIC_SIDECAR_TELEMETRY_LOG"] = old_tel
            if old_custom_port is None:
                os.environ.pop("BIONIC_ALLOW_CUSTOM_LOOPBACK_PORT", None)
            else:
                os.environ["BIONIC_ALLOW_CUSTOM_LOOPBACK_PORT"] = old_custom_port
            srv.shutdown()
            srv.server_close()

        # 8. _discover_repo_sources skip dirs (even when repo is nested under .cache/) + bionic_control port firewall
        src_repo = td_p / ".cache" / "src_filter_repo"
        (src_repo / "node_modules" / "pkg").mkdir(parents=True)
        (src_repo / ".venv" / "lib").mkdir(parents=True)
        (src_repo / "node_modules" / "pkg" / "index.py").write_text("x = 1\n", encoding="utf-8")
        (src_repo / ".venv" / "lib" / "site.py").write_text("y = 2\n", encoding="utf-8")
        (src_repo / "main.py").write_text("z = 3\n", encoding="utf-8")
        discovered = _discover_repo_sources(src_repo.resolve())
        assert [p.name for p in discovered] == ["main.py"]

        old_api2 = os.environ.get("BIONIC_SIDECAR_API_URL")
        old_cp2 = os.environ.get("BIONIC_ALLOW_CUSTOM_LOOPBACK_PORT")
        os.environ["BIONIC_SIDECAR_API_URL"] = "http://127.0.0.1:2375/v1"
        os.environ.pop("BIONIC_ALLOW_CUSTOM_LOOPBACK_PORT", None)
        try:
            ctrl_bad_port = bionic_control(action="status")
            assert ctrl_bad_port["ok"] is False
            assert ctrl_bad_port["error_code"] == "SECURITY_FIREWALL_BLOCKED"
        finally:
            if old_api2 is None:
                os.environ.pop("BIONIC_SIDECAR_API_URL", None)
            else:
                os.environ["BIONIC_SIDECAR_API_URL"] = old_api2
            if old_cp2 is not None:
                os.environ["BIONIC_ALLOW_CUSTOM_LOOPBACK_PORT"] = old_cp2
        checks.append("discover_sources_skip_dirs_and_control_port_firewall")

        # 9. _ensure_live_process_cwd recovers cleanly from an unlinked plugin working directory
        gone_dir = td_p / "deleted_plugin_dir"
        gone_dir.mkdir()
        try:
            orig_cwd = os.getcwd()
        except OSError:
            orig_cwd = local_sidecar._safe_subprocess_cwd()
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

    return {
        "schema_version": "BIONIC_MCP_V1",
        "status": "PASS",
        "mcp_library_active": _HAS_MCP,
        "tools_registered": sorted(tools),
        "tests_run": len(checks),
        "checks": checks,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Antigravity MCP Server for LM Studio Bionic Sidecar")
    parser.add_argument("--self-test", action="store_true", help="Run deterministic offline MCP server self-tests")
    parser.add_argument("--status", action="store_true", help="Print Bionic control status JSON and exit")
    parser.add_argument("--json", action="store_true", help="Emit indented JSON output")
    args = parser.parse_args(argv)

    if args.self_test:
        res = run_self_tests()
        print(json.dumps(res, indent=2) if args.json else f"[PASS] {res['tests_run']} MCP server tests passed")
        return 0
    if args.status:
        print(json.dumps(bionic_control(action="status"), indent=2))
        return 0

    mcp.run(transport="stdio")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
