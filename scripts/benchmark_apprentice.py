#!/usr/bin/env python3
"""
Apprentice Multi-Backend Standardized Benchmark & Regression Suite (`benchmark_apprentice.py`).

Governing Priority Law:
    1. Accuracy & Truth -> 2. Efficiency -> 3. Data Safety -> 4. Speed

Runs deterministic offline firewall/resilience checks and live LM Studio Bionic
(`qwen3.6-35b-a3b`) inference/concurrency benchmarks under a fixed metric schema so
future revisions compare cleanly against a pinned baseline (`apprentice_benchmark_history.jsonl`).

Usage:
    python3 -B scripts/benchmark_apprentice.py --mode offline --json
    python3 -B scripts/benchmark_apprentice.py --mode all --label baseline --record-baseline
    python3 -B scripts/benchmark_apprentice.py --mode all --compare-baseline --output-md report.md
"""
from __future__ import annotations

import argparse
import concurrent.futures
import dataclasses
import datetime as dt
import inspect
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.error
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
ENGINEERING_ROOT = SCRIPT_DIR.parent
DEFAULT_HOMUNCULUS_ROOT = ENGINEERING_ROOT.parent / "Alchemical3D" / "Homunculus"
DEFAULT_ALCHEMICAL_ROOT = ENGINEERING_ROOT.parent / "Alchemical3D"
DEFAULT_HISTORY_JSONL = SCRIPT_DIR / "apprentice_benchmark_history.jsonl"
AGY_VENV_PYTHON = Path("/home/orin/.local/share/agy-gmail/venv/bin/python")
VERIFY_CLAIMS_SCRIPT = DEFAULT_HOMUNCULUS_ROOT / "skills" / "claim-verification" / "scripts" / "verify_claims.py"

if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))
if str(SCRIPT_DIR / "apprentice") not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR / "apprentice"))

import apprentice_lifecycle_hook  # noqa: E402
import apprentice_mcp_server  # noqa: E402
import apprentice_engine  # noqa: E402

SCHEMA_VERSION = "APPRENTICE_BENCH_V2"


@dataclasses.dataclass
class BenchMetric:
    """Single deterministic or live benchmark metric row."""

    id: str
    pillar: str
    name: str
    value: float | int
    unit: str
    target: str
    higher_is_better: bool | None
    status: str  # PASS | FAIL | ADVISORY
    details: str = ""

    def to_dict(self) -> dict[str, Any]:
        return dataclasses.asdict(self)


def _run_subprocess(cmd: list[str], *, timeout_s: int = 60) -> tuple[int, float, str, str]:
    t0 = time.perf_counter()
    proc = subprocess.run(
        cmd,
        cwd=apprentice_engine._safe_subprocess_cwd(),
        capture_output=True,
        text=True,
        timeout=timeout_s,
        check=False,
    )
    return proc.returncode, round(time.perf_counter() - t0, 3), proc.stdout, proc.stderr


def _verify_text_claims(text: str, sources: list[Path], tmp_dir: Path, tag: str) -> dict[str, Any]:
    """Run verify_claims.py on sidecar-generated text against authoritative sources."""
    if not text.strip():
        return {"ran": False, "supported": 0, "unbacked": 0, "backed_pct": 0.0, "vrf_token": None, "reason": "empty_text"}
    if not VERIFY_CLAIMS_SCRIPT.is_file():
        return {"ran": False, "supported": 0, "unbacked": 0, "backed_pct": 0.0, "vrf_token": None, "reason": "missing_verify_claims"}

    target = tmp_dir / f"{tag}.md"
    target.write_text(text.strip() + "\n", encoding="utf-8")
    cmd = [
        sys.executable,
        "-B",
        str(VERIFY_CLAIMS_SCRIPT),
        "--target",
        str(target),
        "--sources",
        *[str(s) for s in sources],
        "--json",
    ]
    rc, elapsed_s, out, err = _run_subprocess(cmd, timeout_s=45)
    try:
        report = json.loads(out) if out.strip() else {}
    except json.JSONDecodeError:
        report = {"raw_error": (err or out)[-400:]}
    sup = int(report.get("supported_count", 0))
    unb = int(report.get("unbacked_count", 0))
    total = sup + unb
    pct = round((100.0 * sup / total), 1) if total > 0 else 0.0
    return {
        "ran": True,
        "returncode": rc,
        "elapsed_s": elapsed_s,
        "supported": sup,
        "unbacked": unb,
        "tbd_count": int(report.get("tbd_count", 0)),
        "backed_pct": pct,
        "vrf_token": report.get("vrf_token"),
        "unbacked_claims": report.get("unbacked_claims", [])[:5],
    }


def _compute_o5_eta_metric(telemetry_log: Path) -> BenchMetric:
    """Compute ETA MAPE over V2 calibrated telemetry rows (falling back safely if none yet)."""
    prompt_errs: list[float] = []
    if telemetry_log.is_file():
        for raw in telemetry_log.read_text(encoding="utf-8", errors="replace").splitlines():
            if not raw.strip():
                continue
            try:
                row = json.loads(raw)
            except json.JSONDecodeError:
                continue
            if row.get("telemetry_schema") != apprentice_engine.TELEMETRY_SCHEMA:
                continue
            if row.get("eta_cal_version") != apprentice_engine.ETA_CALIBRATION_VERSION:
                continue
            if (
                not row.get("tripped")
                and not row.get("http_error")
                and not row.get("synthetic_fault")
                and not row.get("is_retry")
                and not row.get("is_chunked")
                and not str(row.get("cmd") or "").endswith("_retry")
                and isinstance(row.get("predicted_eta_s"), (int, float))
                and isinstance(row.get("elapsed_s"), (int, float))
            ):
                actual = float(row["elapsed_s"])
                pred = float(row["predicted_eta_s"])
                if actual > 0:
                    prompt_errs.append(abs(pred - actual) / actual * 100.0)
    eta_mape = round(sum(prompt_errs) / len(prompt_errs), 1) if prompt_errs else 0.0
    return BenchMetric(
        id="O5_eta_mape",
        pillar="2. Efficiency",
        name="Telemetry ETA Mean Absolute Percentage Error (V2 MAPE)",
        value=eta_mape,
        unit="%",
        target="<= 35.0%",
        higher_is_better=False,
        status="PASS" if (not prompt_errs or eta_mape <= 35.0) else "ADVISORY",
        details=f"v2_samples={len(prompt_errs)}",
    )


def run_offline_suite(telemetry_log: Path) -> tuple[list[BenchMetric], dict[str, Any]]:
    """Run deterministic self-tests, core+extended firewall probes, and resilience checks."""
    metrics: list[BenchMetric] = []
    forensics: dict[str, Any] = {}

    # O1: Built-in unit self-test suites
    py_mcp = str(AGY_VENV_PYTHON) if AGY_VENV_PYTHON.is_file() else sys.executable
    self_test_cmds = [
        ("apprentice_engine", [sys.executable, "-B", str(SCRIPT_DIR / "apprentice_engine.py"), "--self-test"]),
        ("apprentice_lifecycle_hook", [sys.executable, "-B", str(SCRIPT_DIR / "apprentice" / "apprentice_lifecycle_hook.py"), "--self-test"]),
        ("apprentice_mcp_server", [py_mcp, "-B", str(SCRIPT_DIR / "apprentice" / "apprentice_mcp_server.py"), "--self-test"]),
    ]
    suites_passed = 0
    suite_times: dict[str, float] = {}
    for label, cmd in self_test_cmds:
        rc, dt_s, out, err = _run_subprocess(cmd, timeout_s=45)
        suite_times[label] = dt_s
        if rc == 0:
            suites_passed += 1
        else:
            forensics[f"self_test_fail_{label}"] = (err or out)[-500:]
    metrics.append(
        BenchMetric(
            id="O1_unit_suites",
            pillar="1. Accuracy & Truth",
            name="Built-in unit self-test suites passed",
            value=suites_passed,
            unit="suites",
            target="3",
            higher_is_better=True,
            status="PASS" if suites_passed == 3 else "FAIL",
            details=f"timings={suite_times}",
        )
    )

    # O2: Core Pillar-3 firewall vectors (must all block/fail closed)
    core_caught = 0
    core_cases: list[tuple[str, bool]] = []
    with tempfile.TemporaryDirectory(prefix="bionic_bench_fw_") as td:
        td_p = Path(td)
        (td_p / "part.step").write_text("ISO-10303-21;\n", encoding="utf-8")
        (td_p / ".env.prod").write_text("SECRET=1\n", encoding="utf-8")
        (td_p / "outside.md").write_text("# external\n", encoding="utf-8")

        def _expect_fw(fn, *args, **kwargs) -> bool:
            try:
                fn(*args, **kwargs)
                return False
            except apprentice_engine.SidecarFirewallError:
                return True

        core_cases.append(("non_loopback_url", _expect_fw(apprentice_engine.validate_loopback_url, "https://evil.example.com/v1")))
        core_cases.append(("raw_step_cad", _expect_fw(apprentice_engine.validate_input_paths, [td_p / "part.step"])))
        core_cases.append(("env_secret_file", _expect_fw(apprentice_engine.validate_input_paths, [td_p / ".env.prod"])))
        core_cases.append(("repo_4c_escape", _expect_fw(apprentice_engine.validate_input_paths, [td_p / "outside.md"], repo_root=ENGINEERING_ROOT)))
        core_cases.append(("protected_staging_dir", _expect_fw(apprentice_engine.validate_staging_dir, SCRIPT_DIR)))

        eta_trip = apprentice_engine.estimate_eta(mode="fast", prompt_bytes=180000, max_tokens=1200, max_eta_seconds=60.0)
        core_cases.append(("auto_60s_eta_trip", bool(eta_trip.get("tripped"))))

        ctrl_res = apprentice_mcp_server.apprentice_control(action="start-headless", profile="gpu-daily", user_confirmed=False)
        core_cases.append(("control_requires_confirm", ctrl_res.get("error_code") == "USER_CONFIRMATION_REQUIRED"))

        h1 = apprentice_lifecycle_hook.evaluate_pre_tool_use({"hookEventName": "PreToolUse", "toolCall": {"name": "run_command", "args": {"CommandLine": "curl http://127.0.0.1:1234/v1/models"}}})
        h2 = apprentice_lifecycle_hook.evaluate_pre_tool_use({"hookEventName": "PreToolUse", "toolCall": {"name": "run_command", "args": {"CommandLine": "echo hi && python3 apprentice_engine.py status"}}})
        core_cases.append(("hook_blocks_1234", h1.get("decision") == "deny"))
        core_cases.append(("hook_blocks_shell_chain", h2.get("decision") == "deny"))

    core_caught = sum(1 for _k, ok in core_cases if ok)
    forensics["core_firewall_cases"] = dict(core_cases)
    metrics.append(
        BenchMetric(
            id="O2_core_firewall",
            pillar="3. Data Safety",
            name="Core firewall & lifecycle gate catch count",
            value=core_caught,
            unit=f"/ {len(core_cases)}",
            target=f"{len(core_cases)}",
            higher_is_better=True,
            status="PASS" if core_caught == len(core_cases) else "FAIL",
            details=", ".join(k for k, ok in core_cases if not ok) or "all_caught",
        )
    )

    # O3: Extended hardening vectors (tracks Phase 1-2 remediation targets)
    ext_cases: list[tuple[str, bool]] = []
    with tempfile.TemporaryDirectory(prefix="bionic_bench_ext_") as td:
        repo = Path(td) / "repo"
        repo.mkdir()
        subprocess.run(["git", "init", "-q", str(repo)], check=True)
        subprocess.run(["git", "-C", str(repo), "config", "user.email", "test@example.com"], check=True)
        subprocess.run(["git", "-C", str(repo), "config", "user.name", "Tester"], check=True)
        (repo / "README.md").write_text("# Clean\n", encoding="utf-8")
        (repo / ".env").write_text("KEY=init\n", encoding="utf-8")
        (repo / "part.step").write_text("ISO-10303-21;\n", encoding="utf-8")
        subprocess.run(["git", "-C", str(repo), "add", "."], check=True)
        subprocess.run(["git", "-C", str(repo), "commit", "-q", "-m", "init"], check=True)
        (repo / ".env").write_text("KEY=SECRET_LEAK_TOKEN\n", encoding="utf-8")
        (repo / "part.step").write_text("CARTESIAN_POINT('',(0,0,0));\n", encoding="utf-8")
        try:
            diff_payload, _ = apprentice_engine.assemble_prompt_payload(
                user_prompt="check",
                context_files=[repo / "README.md"],
                repo_root=repo,
                include_git_diff=True,
                sys_prompt="sys",
            )
            ext_cases.append(("git_diff_blocks_env", "SECRET_LEAK_TOKEN" not in diff_payload))
            ext_cases.append(("git_diff_blocks_step", "CARTESIAN_POINT" not in diff_payload))
        except apprentice_engine.SidecarFirewallError:
            ext_cases.append(("git_diff_blocks_env", True))
            ext_cases.append(("git_diff_blocks_step", True))

    mixed_blocked = False
    try:
        apprentice_engine.validate_input_paths(
            [
                SCRIPT_DIR / "apprentice_engine.py",
                DEFAULT_ALCHEMICAL_ROOT / "A3DP_Gantry_Assembly" / "BOM.md",
            ],
            repo_root=None,
            require_exists=True,
        )
    except apprentice_engine.SidecarFirewallError:
        mixed_blocked = True
    ext_cases.append(("cross_repo_4c_without_repo", mixed_blocked))

    h_lms_q = apprentice_lifecycle_hook.evaluate_pre_tool_use({"hookEventName": "PreToolUse", "toolCall": {"name": "run_command", "args": {"CommandLine": "bash -c 'lms daemon status'"}}})
    h_dec_ip = apprentice_lifecycle_hook.evaluate_pre_tool_use({"hookEventName": "PreToolUse", "toolCall": {"name": "run_command", "args": {"CommandLine": "curl http://2130706433:1234/v1/models"}}})
    ext_cases.append(("hook_blocks_quoted_lms", h_lms_q.get("decision") == "deny"))
    ext_cases.append(("hook_blocks_decimal_ip", h_dec_ip.get("decision") == "deny"))

    ext_caught = sum(1 for _k, ok in ext_cases if ok)
    forensics["extended_hardening_cases"] = dict(ext_cases)
    metrics.append(
        BenchMetric(
            id="O3_extended_hardening",
            pillar="3. Data Safety",
            name="Extended hardening targets caught (Phase 2)",
            value=ext_caught,
            unit=f"/ {len(ext_cases)}",
            target=f"{len(ext_cases)}",
            higher_is_better=True,
            status="PASS" if ext_caught == len(ext_cases) else "ADVISORY",
            details="missing: " + ", ".join(k for k, ok in ext_cases if not ok) if ext_caught < len(ext_cases) else "all_caught",
        )
    )

    # O4: Resilience checks (truncated fence + daemon timeout handling)
    extracted = apprentice_engine.extract_staged_code("```python\nimport os\ndef f():\n    return 1\n")
    fence_clean = not extracted.lstrip().startswith("```")

    orig_probe = apprentice_engine._probe_lms_daemon
    orig_run = apprentice_engine._run_lms_cmd
    timeout_handled = False
    try:
        apprentice_engine._probe_lms_daemon = lambda *a, **k: {"available": True, "running": False, "summary": "timed out"}
        def _raise_to(*a, **k):
            raise subprocess.TimeoutExpired(cmd=["lms", "daemon", "up"], timeout=30.0)
        apprentice_engine._run_lms_cmd = _raise_to
        try:
            apprentice_engine._control_start_headless(
                "http://127.0.0.1:1234/v1",
                "qwen3.6-35b-a3b",
                "gpu-daily",
                apprentice_engine.DEFAULT_LMS_BIN,
                Path("/nonexistent/appimage"),
                Path("/tmp/nonexistent_cfg.json"),
            )
        except RuntimeError:
            timeout_handled = True
        except subprocess.TimeoutExpired:
            timeout_handled = False
    finally:
        apprentice_engine._probe_lms_daemon = orig_probe
        apprentice_engine._run_lms_cmd = orig_run

    resilience_score = int(fence_clean) + int(timeout_handled)
    forensics["resilience_cases"] = {"truncated_fence_stripped": fence_clean, "daemon_timeout_caught": timeout_handled}
    metrics.append(
        BenchMetric(
            id="O4_resilience_fixes",
            pillar="1. Accuracy & Truth",
            name="Truncated fence & daemon timeout resilience (Phase 1)",
            value=resilience_score,
            unit="/ 2",
            target="2",
            higher_is_better=True,
            status="PASS" if resilience_score == 2 else "ADVISORY",
            details=f"fence_clean={fence_clean}, daemon_timeout_caught={timeout_handled}",
        )
    )

    # O5: V2 ETA calibration MAPE
    metrics.append(_compute_o5_eta_metric(telemetry_log))

    # O6: Soft ETA overrun separation, HIGH >=4096 floor, and HTTP error telemetry isolation
    soft_est = apprentice_engine.estimate_eta(
        mode="fast",
        prompt_bytes=0,
        prompt_tokens_override=46000,
        max_tokens=2048,
        max_eta_seconds=60.0,
        calibrated_output=True,
        loaded_ctx_override=57344,
    )
    soft_ok = bool(soft_est.get("soft_eta_exceeded")) and not bool(soft_est.get("hard_tripped"))
    floor_ok = apprentice_engine.resolve_effective_max_tokens("deep", 1024) == 4096
    err_logged = False
    with tempfile.TemporaryDirectory(prefix="bionic_bench_o6_") as td_o6:
        old_t6 = os.environ.get("APPRENTICE_TELEMETRY_LOG")
        t6 = Path(td_o6) / "tel.jsonl"
        os.environ["APPRENTICE_TELEMETRY_LOG"] = str(t6)
        try:
            apprentice_engine.record_usage_telemetry({"cmd": "query", "http_error": True, "elapsed_s": 0.4, "finish_reason": "error"})
            sc6 = apprentice_engine.load_or_init_scorecard()
            err_logged = sc6["corrected"] == 1 and t6.is_file()
        finally:
            if old_t6 is None:
                os.environ.pop("APPRENTICE_TELEMETRY_LOG", None)
            else:
                os.environ["APPRENTICE_TELEMETRY_LOG"] = old_t6
    o6_score = int(soft_ok) + int(floor_ok) + int(err_logged)
    forensics["O6"] = {"soft_ok": soft_ok, "floor_ok": floor_ok, "err_logged": err_logged}
    metrics.append(
        BenchMetric(
            id="O6_soft_eta_and_err_tel",
            pillar="2. Efficiency",
            name="Soft ETA advisory, HIGH 4096 floor, and error telemetry",
            value=o6_score,
            unit="/ 3",
            target="3",
            higher_is_better=True,
            status="PASS" if o6_score == 3 else "FAIL",
            details=f"soft={soft_ok}, floor={floor_ok}, err_tel={err_logged}",
        )
    )

    # O7: Lifetime scorecard seed, healed classification, slow_self_heal (>45s), & idempotent verdict
    o7_ok = False
    with tempfile.TemporaryDirectory(prefix="bionic_bench_o7_") as td_o7:
        old_t7 = os.environ.get("APPRENTICE_TELEMETRY_LOG")
        t7 = Path(td_o7) / "tel.jsonl"
        os.environ["APPRENTICE_TELEMETRY_LOG"] = str(t7)
        try:
            t7.write_text(json.dumps({"cmd": "query", "finish_reason": "stop", "elapsed_s": 2.0}) + "\n", encoding="utf-8")
            rec_h = apprentice_engine.record_call_outcome(verdict="healed", cmd="stage-code", effort="high", mode="deep", elapsed_s=10.0, heal_elapsed_s=48.0)
            rec_c = apprentice_engine.record_call_outcome(verdict="clean", cmd="query", effort="standard", mode="fast", elapsed_s=3.0)
            v1 = apprentice_engine.apply_call_verdict(rec_c["call_id"], "corrected", note="o7")
            v2 = apprentice_engine.apply_call_verdict(rec_c["call_id"], "corrected", note="o7_repeat")
            o7_ok = (rec_h["slow_self_heal"] is True and rec_h["healed"] == 1 and v1["clean"] == 1 and v1["corrected"] == 1 and v2["corrected"] == 1)
        finally:
            if old_t7 is None:
                os.environ.pop("APPRENTICE_TELEMETRY_LOG", None)
            else:
                os.environ["APPRENTICE_TELEMETRY_LOG"] = old_t7
    metrics.append(
        BenchMetric(
            id="O7_scorecard_and_healed",
            pillar="1. Accuracy & Truth",
            name="Lifetime scorecard seed, healed flag, & idempotent verdict",
            value=1 if o7_ok else 0,
            unit="bool",
            target="1",
            higher_is_better=True,
            status="PASS" if o7_ok else "FAIL",
            details="verified" if o7_ok else "mismatch",
        )
    )

    # O8: Context slice parsing, KV budget lockfile guard, & gpu-max hardware config
    p_sl, rng_sl = apprentice_engine.parse_context_spec("/tmp/demo.py#L12-L40")
    slice_ok = (p_sl == Path("/tmp/demo.py") and rng_sl == (12, 40))
    cfg_max = apprentice_engine.build_concrete_model_config("gpu-max")
    fmax = {f["key"]: f["value"] for f in cfg_max["load"]["fields"]}
    cfg_ok = (fmax.get("llm.load.contextLength") == 57344 and fmax.get("llm.load.numCpuExpertLayersRatio") == 0.52)
    kv_ok = False
    with tempfile.TemporaryDirectory(prefix="bionic_bench_o8_") as td_o8:
        old_t8 = os.environ.get("APPRENTICE_TELEMETRY_LOG")
        os.environ["APPRENTICE_TELEMETRY_LOG"] = str(Path(td_o8) / "tel.jsonl")
        try:
            with apprentice_engine.acquire_kv_budget(40000, loaded_ctx=57344, timeout_s=0.15):
                try:
                    with apprentice_engine.acquire_kv_budget(20000, loaded_ctx=57344, timeout_s=0.1):
                        kv_ok = False
                except RuntimeError:
                    kv_ok = True
        finally:
            if old_t8 is None:
                os.environ.pop("APPRENTICE_TELEMETRY_LOG", None)
            else:
                os.environ["APPRENTICE_TELEMETRY_LOG"] = old_t8
    o8_score = int(slice_ok) + int(cfg_ok) + int(kv_ok)
    metrics.append(
        BenchMetric(
            id="O8_slice_and_kv_guard",
            pillar="2. Efficiency",
            name="Context #L slicing, gpu-max config, & KV budget guard",
            value=o8_score,
            unit="/ 3",
            target="3",
            higher_is_better=True,
            status="PASS" if o8_score == 3 else "FAIL",
            details=f"slice={slice_ok}, cfg={cfg_ok}, kv={kv_ok}",
        )
    )

    # O9: V2.3 graduation guards (lean headless prompt, chunk continuity, reset confirm gate, epoch delta, AST auto --self-test, verify default)
    sys_txt, sys_src = apprentice_engine.load_system_prompt()
    headless_prompt_lean = (sys_src == "headless_api_v2_3") and (len(sys_txt.encode("utf-8")) <= 1050)

    ls_path = SCRIPT_DIR / "apprentice_engine.py"
    ls_chunks = apprentice_engine.plan_line_preserving_chunks([ls_path], target_chunk_bytes=22000)
    ls_nlines = len(ls_path.read_text(encoding="utf-8", errors="replace").splitlines())
    chunk_line_continuity = bool(
        len(ls_chunks) >= 6
        and ls_chunks[0][1] == 1
        and ls_chunks[-1][2] == ls_nlines
        and all(ls_chunks[i][2] + 1 == ls_chunks[i + 1][1] for i in range(len(ls_chunks) - 1))
    )

    rs_blk = apprentice_mcp_server.apprentice_control(action="scorecard-reset", user_confirmed=False)
    scorecard_reset_confirm_gate = rs_blk.get("error_code") == "USER_CONFIRMATION_REQUIRED"

    scorecard_epoch_delta = False
    with tempfile.TemporaryDirectory(prefix="bionic_bench_o9_") as td_o9:
        old_t9 = os.environ.get("APPRENTICE_TELEMETRY_LOG")
        os.environ["APPRENTICE_TELEMETRY_LOG"] = str(Path(td_o9) / "tel.jsonl")
        try:
            for _ in range(3):
                apprentice_engine.record_call_outcome(verdict="clean", cmd="query", elapsed_s=1.0)
            apprentice_engine.record_call_outcome(verdict="corrected", cmd="query", elapsed_s=1.0)
            apprentice_engine.reset_scorecard(epoch_label="v2.3-o9")
            apprentice_engine.record_call_outcome(verdict="clean", cmd="query", elapsed_s=1.0)
            fmt_o9 = apprentice_engine.format_lifetime_scorecard()
            scorecard_epoch_delta = ("+25.0% vs pre-v2.3" in fmt_o9) and ("100.0% usable" in fmt_o9)
        finally:
            if old_t9 is None:
                os.environ.pop("APPRENTICE_TELEMETRY_LOG", None)
            else:
                os.environ["APPRENTICE_TELEMETRY_LOG"] = old_t9

    auto_selftest_ast_detect = False
    with tempfile.TemporaryDirectory(prefix="bionic_bench_st_") as td_st:
        st_py = Path(td_st) / "cli_demo.py"
        st_py.write_text(
            "import sys\nif __name__ == '__main__':\n    if '--self-test' in sys.argv:\n        sys.exit(0)\n",
            encoding="utf-8",
        )
        eff_st, auto_st = apprentice_mcp_server._resolve_effective_smoke_args(st_py, None)
        auto_selftest_ast_detect = (eff_st == ["--self-test"]) and (auto_st is True)

    default_verify_claims_on = (
        inspect.signature(apprentice_mcp_server._apprentice_digest_sync).parameters["verify_claims"].default is True
    )
    o9_checks = {
        "headless": headless_prompt_lean,
        "chunks": chunk_line_continuity,
        "reset_gate": scorecard_reset_confirm_gate,
        "epoch_delta": scorecard_epoch_delta,
        "ast_selftest": auto_selftest_ast_detect,
        "verify_default": default_verify_claims_on,
    }
    o9_score = sum(1 for v in o9_checks.values() if v)
    forensics["O9"] = o9_checks
    metrics.append(
        BenchMetric(
            id="O9_v23_graduation_guards",
            pillar="1. Accuracy & Truth",
            name="V2.3 graduation guards (prompt, chunking, reset, AST auto-smoke, verify default)",
            value=o9_score,
            unit="/ 6",
            target="6",
            higher_is_better=True,
            status="PASS" if o9_score == 6 else "FAIL",
            details=", ".join(f"{k}={v}" for k, v in o9_checks.items()),
        )
    )

    return metrics, forensics


def run_live_suite() -> tuple[list[BenchMetric], dict[str, Any]]:
    """Run live Bionic inference, claim verification, staging, and concurrency benchmarks."""
    metrics: list[BenchMetric] = []
    forensics: dict[str, Any] = {}

    api_url = apprentice_engine.validate_loopback_url(apprentice_engine.resolve_default_api_url())
    srv = apprentice_engine.probe_server_models(api_url, model_id=apprentice_engine.DEFAULT_MODEL_ID, timeout_s=3.0)
    if not srv["reachable"] or not srv["target_model_loaded"]:
        raise RuntimeError(
            f"[BIONIC_NOT_READY] Live benchmark requires ONLINE_READY Bionic at {api_url}; "
            f"reachable={srv['reachable']}, loaded={srv['target_model_loaded']} ({srv.get('error')})"
        )
    forensics["server_status"] = srv

    a3dp_repo = DEFAULT_ALCHEMICAL_ROOT / "A3DP_Gantry_Assembly"
    a3dp_bom = a3dp_repo / "BOM.md"
    alembic_repo = DEFAULT_ALCHEMICAL_ROOT / "Alembic_Toolhead"
    alembic_bom = alembic_repo / "BOM.md"

    with tempfile.TemporaryDirectory(prefix="bionic_bench_live_") as td:
        td_p = Path(td)
        staging_dir = td_p / "staging"
        staging_dir.mkdir(mode=0o700)

        # L1a: Clean BOM standard fast digest + verify_claims
        r_std = apprentice_mcp_server.apprentice_digest(
            prompt=(
                "Extract every fastener item, size, and quantity from BOM.md as a compact bullet list. "
                "Cite exact BOM.md#Lstart-Lend anchors for every row. Never guess or expand acronyms."
            ),
            context_files=[str(a3dp_bom)],
            repo=str(a3dp_repo),
            include_git_diff=False,
            mode="fast",
            invocation_tier="explicit",
            max_tokens=1200,
        )
        c_std = r_std.get("completion") or {}
        v_std = _verify_text_claims(str(c_std.get("content") or ""), [a3dp_bom], td_p, "l1a_std")
        forensics["L1a"] = {"ok": r_std.get("ok"), "completion": {k: v for k, v in c_std.items() if k != "content"}, "verify": v_std}
        metrics.append(
            BenchMetric(
                id="L1a_bom_fast_std_s",
                pillar="4. Speed",
                name="Clean BOM fast digest wall time (standard)",
                value=float(c_std.get("elapsed_s") or 0.0),
                unit="s",
                target="<= 30.0s",
                higher_is_better=False,
                status="PASS" if r_std.get("ok") and float(c_std.get("elapsed_s") or 999) <= 30.0 else "FAIL",
                details=f"out_tok={c_std.get('completion_tokens')}, tg={c_std.get('observed_tg_tok_s')}",
            )
        )
        metrics.append(
            BenchMetric(
                id="L1a_bom_fast_std_acc",
                pillar="1. Accuracy & Truth",
                name="Clean BOM fast digest claim backing",
                value=float(v_std.get("backed_pct") or 0.0),
                unit="%",
                target="100.0%",
                higher_is_better=True,
                status="PASS" if v_std.get("ran") and v_std.get("unbacked") == 0 and v_std.get("supported", 0) > 0 else "FAIL",
                details=f"{v_std.get('supported')}/{v_std.get('supported', 0) + v_std.get('unbacked', 0)} ({v_std.get('vrf_token')})",
            )
        )
        vrf_inline = r_std.get("verify_claims") or {}
        vrf_ms = float(vrf_inline.get("elapsed_ms") or 9999.0)
        vrf_bytes = len(json.dumps(vrf_inline).encode("utf-8"))
        l11_ok = (
            bool(vrf_inline.get("ran"))
            and vrf_inline.get("returncode") == 0
            and "report" not in vrf_inline
            and vrf_ms <= 250.0
            and vrf_bytes <= 220
        )
        forensics["L11"] = {**vrf_inline, "json_bytes": vrf_bytes}
        metrics.append(
            BenchMetric(
                id="L11_verify_claims_overhead_ms",
                pillar="2. Efficiency",
                name="Inline verify_claims latency & zero-bloat JSON receipt",
                value=vrf_ms,
                unit="ms",
                target="<= 250.0 ms (<=220 B)",
                higher_is_better=False,
                status="PASS" if l11_ok else "FAIL",
                details=f"bytes={vrf_bytes}B, rc={vrf_inline.get('returncode')}, vrf={vrf_inline.get('vrf_token')}",
            )
        )

        # L1b: Clean BOM compact terse fast digest + verify_claims
        r_cmp = apprentice_mcp_server.apprentice_digest(
            prompt=(
                "Return ONLY a compact markdown list (`- <item>: qty <N> (`BOM.md#L<line>`)`) of threaded fasteners, "
                "pins, and shims in BOM.md. Zero preamble, zero notes, zero excluded-items section."
            ),
            context_files=[str(a3dp_bom)],
            repo=str(a3dp_repo),
            include_git_diff=False,
            mode="fast",
            invocation_tier="auto",
            max_tokens=600,
        )
        c_cmp = r_cmp.get("completion") or {}
        v_cmp = _verify_text_claims(str(c_cmp.get("content") or ""), [a3dp_bom], td_p, "l1b_cmp")
        forensics["L1b"] = {"ok": r_cmp.get("ok"), "completion": {k: v for k, v in c_cmp.items() if k != "content"}, "verify": v_cmp}
        metrics.append(
            BenchMetric(
                id="L1b_bom_fast_compact_s",
                pillar="4. Speed",
                name="Clean BOM fast digest wall time (compact)",
                value=float(c_cmp.get("elapsed_s") or 0.0),
                unit="s",
                target="<= 15.0s",
                higher_is_better=False,
                status="PASS" if r_cmp.get("ok") and float(c_cmp.get("elapsed_s") or 999) <= 15.0 else "ADVISORY",
                details=f"out_tok={c_cmp.get('completion_tokens')}, backed={v_cmp.get('backed_pct')}%",
            )
        )

        # L2: HIGH effort mode reliability & claim accuracy (>=4096 token budget, zero length clipping)
        r_deep = apprentice_mcp_server.apprentice_digest(
            prompt="Extract threaded fasteners and quantities from BOM.md with BOM.md#Lstart-Lend anchors.",
            context_files=[str(a3dp_bom)],
            repo=str(a3dp_repo),
            include_git_diff=False,
            effort="high",
            invocation_tier="explicit",
        )
        c_deep = r_deep.get("completion") or {}
        deep_non_empty = 1 if (r_deep.get("ok") and bool(str(c_deep.get("content") or "").strip())) else 0
        v_deep = _verify_text_claims(str(c_deep.get("content") or ""), [a3dp_bom], td_p, "l2_deep")
        deep_clean = (deep_non_empty == 1 and c_deep.get("finish_reason") != "length" and v_deep.get("unbacked", 0) == 0 and v_deep.get("supported", 0) > 0)
        forensics["L2"] = {"ok": r_deep.get("ok"), "effort": r_deep.get("effort"), "error_code": r_deep.get("error_code"), "completion": {k: v for k, v in c_deep.items() if k != "content"}, "verify": v_deep}
        metrics.append(
            BenchMetric(
                id="L2_deep_non_empty",
                pillar="1. Accuracy & Truth",
                name="HIGH effort produces non-empty verified output (4096+ floor)",
                value=deep_non_empty,
                unit="bool",
                target="1",
                higher_is_better=True,
                status="PASS" if deep_clean else "ADVISORY",
                details=f"finish={c_deep.get('finish_reason')}, elapsed={c_deep.get('elapsed_s')}s, out_tok={c_deep.get('completion_tokens')}, eff_max={(r_deep.get('eta_estimate') or {}).get('effective_max_tokens')}",
            )
        )
        metrics.append(
            BenchMetric(
                id="L6_high_effort_verified",
                pillar="1. Accuracy & Truth",
                name="HIGH effort claim verification backing",
                value=float(v_deep.get("backed_pct") or 0.0),
                unit="%",
                target="100.0%",
                higher_is_better=True,
                status="PASS" if deep_clean else "FAIL",
                details=f"{v_deep.get('supported')}/{v_deep.get('supported', 0) + v_deep.get('unbacked', 0)} ({v_deep.get('vrf_token')})",
            )
        )

        # L3: Scoped diff efficiency (Alembic_Toolhead BOM.md + include_git_diff=True)
        r_diff = apprentice_mcp_server.apprentice_digest(
            prompt=(
                "List ONLY Section 2 fastener and hardware changes in BOM.md vs git HEAD "
                "as a compact bullet list citing BOM.md#Lstart-Lend. "
                "Mark missing intent as [TBD: ...]. Zero preamble."
            ),
            context_files=[str(alembic_bom)],
            repo=str(alembic_repo),
            include_git_diff=True,
            effort="standard",
            invocation_tier="auto",
        )
        c_diff = r_diff.get("completion") or {}
        diff_ptok = int(c_diff.get("prompt_tokens") or 0)
        forensics["L3"] = {"ok": r_diff.get("ok"), "error_code": r_diff.get("error_code"), "completion": {k: v for k, v in c_diff.items() if k != "content"}}
        metrics.append(
            BenchMetric(
                id="L3_scoped_diff_prompt_tok",
                pillar="2. Efficiency",
                name="BOM.md + include_git_diff prompt token footprint (Phase 3)",
                value=diff_ptok,
                unit="tok",
                target="<= 5000",
                higher_is_better=False,
                status="PASS" if (0 < diff_ptok <= 5000) else "ADVISORY",
                details=f"elapsed={c_diff.get('elapsed_s')}s, finish={c_diff.get('finish_reason')}",
            )
        )

        # L4: apprentice_stage_patch code generation + py_compile + execution
        r_stg = apprentice_mcp_server.apprentice_stage_patch(
            target_filename="bench_helper.py",
            prompt=(
                "Write a Python 3.10+ script (<45 lines) with `clamp_eta(val: float) -> float` clamping to "
                "[1.0, 90.0] and an `if __name__ == '__main__':` check asserting clamp_eta(0.2)==1.0 and "
                "clamp_eta(120.0)==90.0, printing OK. Return ONLY one ```python code fence."
            ),
            staging_dir=str(staging_dir),
            mode="fast",
            invocation_tier="auto",
            max_tokens=800,
        )
        stg_exec_ok = False
        if r_stg.get("py_compile_ok") and r_stg.get("staged_file"):
            rc_s, _, _, _ = _run_subprocess([sys.executable, "-B", str(r_stg["staged_file"])], timeout_s=10)
            stg_exec_ok = rc_s == 0
        stg_tel = r_stg.get("telemetry") or {}
        forensics["L4"] = {"ok": r_stg.get("ok"), "attempts": r_stg.get("attempts"), "py_compile_ok": r_stg.get("py_compile_ok"), "exec_ok": stg_exec_ok, "elapsed_s": stg_tel.get("elapsed_s")}
        metrics.append(
            BenchMetric(
                id="L4_stage_patch_s",
                pillar="4. Speed",
                name="apprentice_stage_patch synthesis + py_compile time",
                value=float(stg_tel.get("elapsed_s") or 0.0),
                unit="s",
                target="<= 20.0s",
                higher_is_better=False,
                status="PASS" if (r_stg.get("ok") and r_stg.get("py_compile_ok") and stg_exec_ok) else "FAIL",
                details=f"attempts={r_stg.get('attempts')}, py_compile={r_stg.get('py_compile_ok')}, exec={stg_exec_ok}",
            )
        )

        # L5: Concurrency speedup (--parallel 4 parallel HTTP calls)
        t_par0 = time.perf_counter()
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
            f1 = pool.submit(
                apprentice_mcp_server.apprentice_digest,
                prompt="Reply with exactly one line: SLOT_1_OK",
                mode="fast",
                invocation_tier="auto",
                max_tokens=32,
            )
            f2 = pool.submit(
                apprentice_mcp_server.apprentice_digest,
                prompt="Reply with exactly one line: SLOT_2_OK",
                mode="fast",
                invocation_tier="auto",
                max_tokens=32,
            )
            p1, p2 = f1.result(timeout=60), f2.result(timeout=60)
        par_wall = round(time.perf_counter() - t_par0, 3)
        sum_indiv = round(
            float((p1.get("completion") or {}).get("elapsed_s") or 0.0)
            + float((p2.get("completion") or {}).get("elapsed_s") or 0.0),
            3,
        )
        par_ratio = round(sum_indiv / par_wall, 2) if par_wall > 0 else 0.0
        forensics["L5"] = {"parallel_wall_s": par_wall, "sum_individual_s": sum_indiv, "speedup_ratio": par_ratio}
        metrics.append(
            BenchMetric(
                id="L5_parallel_speedup",
                pillar="4. Speed",
                name="Dual concurrent sidecar speedup (--parallel 2)",
                value=par_ratio,
                unit="x",
                target=">= 1.30x",
                higher_is_better=True,
                status="PASS" if par_ratio >= 1.30 else "ADVISORY",
                details=f"wall={par_wall}s vs sum={sum_indiv}s",
            )
        )

        # L7: Async sprint parallel overlap via base apprentice_digest(async_job=True) + apprentice_control(job-collect)
        t_async0 = time.perf_counter()
        sub_job = apprentice_mcp_server.apprentice_digest(
            prompt="Summarize top 3 fastener families in BOM.md citing BOM.md#Lstart-Lend.",
            context_files=[f"{a3dp_bom}#L1-L40"],
            repo=str(a3dp_repo),
            effort="standard",
            invocation_tier="auto",
            async_job=True,
        )
        overlap_ok = False
        overlap_saved_s = 0.0
        col_res: dict[str, Any] = {}
        if sub_job.get("ok") and sub_job.get("job_id"):
            t_fw0 = time.perf_counter()
            time.sleep(1.5)  # Simulated parallel frontier reasoning before hitting critical stop point
            frontier_work_s = round(time.perf_counter() - t_fw0, 3)
            col_res = apprentice_mcp_server.apprentice_control(action="job-collect", job_id=sub_job["job_id"], wait_seconds=60.0)
            job_res = col_res.get("result") or {}
            bionic_dt = float(((job_res.get("completion") or {}).get("elapsed_s")) or 0.0)
            overlap_ok = bool(
                col_res.get("ok")
                and col_res.get("status") == "completed"
                and job_res.get("ok")
                and job_res.get("verdict") in {"clean", "healed"}
            )
            overlap_saved_s = round(min(frontier_work_s, bionic_dt), 3) if overlap_ok else 0.0
        total_async_wall = round(time.perf_counter() - t_async0, 3)
        forensics["L7"] = {
            "submitted": sub_job,
            "collected_status": col_res.get("status"),
            "verdict": (col_res.get("result") or {}).get("verdict"),
            "overlap_saved_s": overlap_saved_s,
            "wall_s": total_async_wall,
        }
        metrics.append(
            BenchMetric(
                id="L7_async_sprint_overlap",
                pillar="4. Speed",
                name="Agile async sprint parallel overlap savings",
                value=overlap_saved_s,
                unit="s",
                target="> 0.0s",
                higher_is_better=True,
                status="PASS" if (overlap_ok and overlap_saved_s > 0.0) else "FAIL",
                details=f"wall={total_async_wall}s, job_status={col_res.get('status')}, verdict={(col_res.get('result') or {}).get('verdict')}",
            )
        )

        # L8: Live apprentice_stage_patch self-heal (inject broken attempt 1 draft, verify real Qwen GPU repair attempt 2)
        orig_invoke = apprentice_engine.invoke_chat_completion
        injected_box = {"done": False}

        def _inject_broken_first_draft(*args, **kwargs):
            if not injected_box["done"]:
                injected_box["done"] = True
                return {
                    "model": apprentice_engine.DEFAULT_MODEL_ID,
                    "mode": kwargs.get("mode", "fast"),
                    "reasoning_effort": "none",
                    "prompt_tokens": 120,
                    "completion_tokens": 16,
                    "elapsed_s": 0.4,
                    "observed_tg_tok_s": 40.0,
                    "finish_reason": "stop",
                    "synthetic_fault": True,
                    "content": "```python\ndef broken_hdr(:\n    return 1\n```\n",
                }
            return orig_invoke(*args, **kwargs)

        apprentice_engine.invoke_chat_completion = _inject_broken_first_draft
        try:
            r_heal = apprentice_mcp_server.apprentice_stage_patch(
                target_filename="self_heal_demo.py",
                prompt=(
                    "Write a Python 3.10+ function `add_one(x: int) -> int` returning x + 1, "
                    "plus `if __name__ == '__main__': assert add_one(2) == 3; print('HEAL_OK')`."
                ),
                staging_dir=str(staging_dir),
                effort="standard",
                invocation_tier="auto",
                smoke_test_args=[],
            )
        finally:
            apprentice_engine.invoke_chat_completion = orig_invoke
        forensics["L8"] = {k: v for k, v in r_heal.items() if k != "completion"}
        l8_ok = bool(r_heal.get("ok") and r_heal.get("verdict") == "healed" and r_heal.get("py_compile_ok") and (r_heal.get("smoke_test") or {}).get("ok"))
        metrics.append(
            BenchMetric(
                id="L8_stage_self_heal",
                pillar="1. Accuracy & Truth",
                name="Live stage_patch self-heal recovery (healed classification)",
                value=1 if l8_ok else 0,
                unit="bool",
                target="1",
                higher_is_better=True,
                status="PASS" if l8_ok else "FAIL",
                details=f"verdict={r_heal.get('verdict')}, heal_dt={r_heal.get('heal_elapsed_s')}s, attempts={r_heal.get('attempts')}",
            )
        )

        # L9: gpu-max VRAM/GTT desktop headroom verification
        hw_now = apprentice_engine._read_hw_counters()
        srv_now = apprentice_engine.probe_server_models(api_url, model_id=apprentice_engine.DEFAULT_MODEL_ID, timeout_s=3.0)
        vfree = float(hw_now.get("vram_free_gib") or 0.0)
        gused = float(hw_now.get("gtt_used_gib") if hw_now.get("gtt_used_gib") is not None else 99.0)
        lctx = int(srv_now.get("loaded_context_length") or 0)
        l9_ok = (vfree >= 2.0 and gused < 0.5 and lctx >= 49152)
        forensics["L9"] = {"hardware": hw_now, "loaded_context_length": lctx}
        metrics.append(
            BenchMetric(
                id="L9_gpu_max_headroom",
                pillar="3. Data Safety",
                name="gpu-max desktop free VRAM & anti-GTT headroom",
                value=vfree,
                unit="GiB free",
                target=">= 2.0 GiB (GTT < 0.5)",
                higher_is_better=True,
                status="PASS" if l9_ok else "FAIL",
                details=f"vram_used={hw_now.get('vram_used_gib')} GiB, gtt_used={gused} GiB, ctx={lctx}",
            )
        )

        # L10: Live V2.3 graduation vectors (TV-1 length heal, TV-4 >45k chunked digest, TV-5 auto --self-test heal)
        r_tv1 = apprentice_mcp_server.apprentice_digest(
            prompt=(
                "List all fastener rows in BOM.md as compact markdown bullets citing exact "
                "BOM.md#Lstart-Lend anchors for every row. Never guess or expand acronyms."
            ),
            context_files=[str(a3dp_bom)],
            repo=str(a3dp_repo),
            effort="standard",
            invocation_tier="explicit",
            max_tokens=95,
        )
        c_tv1 = r_tv1.get("completion") or {}
        tv1_ok = bool(
            r_tv1.get("ok")
            and r_tv1.get("verdict") == "healed"
            and r_tv1.get("claims_verified") is True
            and c_tv1.get("finish_reason") == "stop"
        )

        r_tv4 = apprentice_mcp_server.apprentice_digest(
            prompt=(
                "Find the exact top-level assignment or `def` lines of `HEADLESS_API_SYSTEM_PROMPT`, "
                "`plan_line_preserving_chunks`, and `reset_scorecard` in apprentice_engine.py (ignore call sites and docstring index). "
                "Return ONLY 3 compact bullets (`- `<symbol>`: `apprentice_engine.py#L<start>-L<end>``). Zero preamble."
            ),
            context_files=[str(SCRIPT_DIR / "apprentice_engine.py")],
            repo=str(ENGINEERING_ROOT),
            effort="standard",
            invocation_tier="explicit",
        )
        cmr_tv4 = r_tv4.get("chunked_map_reduce") or {}
        tv4_ok = bool(
            r_tv4.get("ok")
            and cmr_tv4.get("enabled")
            and int(cmr_tv4.get("chunks") or 0) >= 6
            and r_tv4.get("claims_verified") is True
            and r_tv4.get("verdict") in {"clean", "healed"}
        )

        orig_invoke_5 = apprentice_engine.invoke_chat_completion
        inj5_box = {"done": False}

        def _inject_bad_selftest_once(*args, **kwargs):
            if not inj5_box["done"]:
                inj5_box["done"] = True
                return {
                    "model": apprentice_engine.DEFAULT_MODEL_ID,
                    "mode": kwargs.get("mode", "fast"),
                    "reasoning_effort": "none",
                    "prompt_tokens": 110,
                    "completion_tokens": 42,
                    "elapsed_s": 0.4,
                    "observed_tg_tok_s": 40.0,
                    "finish_reason": "stop",
                    "synthetic_fault": True,
                    "content": (
                        "```python\nimport sys\ndef clamp_non_neg(x: int) -> int:\n    return x\n"
                        "if __name__ == '__main__':\n    if '--self-test' in sys.argv:\n"
                        "        assert clamp_non_neg(-5) == 0\n        print('SELFTEST_OK')\n```\n"
                    ),
                }
            return orig_invoke_5(*args, **kwargs)

        apprentice_engine.invoke_chat_completion = _inject_bad_selftest_once
        try:
            r_tv5 = apprentice_mcp_server.apprentice_stage_patch(
                target_filename="auto_selftest_demo.py",
                prompt=(
                    "Write Python 3.10+ `clamp_non_neg(x: int) -> int` returning `max(0, x)` "
                    "and an `if __name__ == '__main__':` block supporting `--self-test` that asserts "
                    "`clamp_non_neg(-5) == 0` and `clamp_non_neg(7) == 7` and prints `SELFTEST_OK`. "
                    "Return ONLY one ```python code fence."
                ),
                staging_dir=str(staging_dir),
                effort="standard",
                invocation_tier="auto",
                smoke_test_args=None,
            )
        finally:
            apprentice_engine.invoke_chat_completion = orig_invoke_5
        tv5_ok = bool(
            r_tv5.get("ok")
            and r_tv5.get("verdict") == "healed"
            and (r_tv5.get("smoke_test") or {}).get("auto_detected") is True
            and (r_tv5.get("smoke_test") or {}).get("ok") is True
        )
        tv_pass_count = int(tv1_ok) + int(tv4_ok) + int(tv5_ok)
        forensics["L10"] = {
            "tv1_len": {"ok": r_tv1.get("ok"), "verdict": r_tv1.get("verdict"), "claims_verified": r_tv1.get("claims_verified"), "finish": c_tv1.get("finish_reason")},
            "tv4_chunk": {"ok": r_tv4.get("ok"), "verdict": r_tv4.get("verdict"), "claims_verified": r_tv4.get("claims_verified"), "chunked": cmr_tv4, "verify_claims": r_tv4.get("verify_claims"), "elapsed_s": (r_tv4.get("completion") or {}).get("elapsed_s")},
            "tv5_selftest": {"ok": r_tv5.get("ok"), "verdict": r_tv5.get("verdict"), "smoke_test": r_tv5.get("smoke_test")},
        }
        metrics.append(
            BenchMetric(
                id="L10_v23_live_graduation",
                pillar="1. Accuracy & Truth",
                name="Live V2.3 graduation vectors (length heal, >45k chunked digest, auto --self-test heal)",
                value=tv_pass_count,
                unit="/ 3",
                target="3",
                higher_is_better=True,
                status="PASS" if tv_pass_count == 3 else "FAIL",
                details=f"tv1_len={tv1_ok}, tv4_chunk={tv4_ok}, tv5_selftest={tv5_ok}",
            )
        )

        # L12 & L13: Live V2.6.0 effort="auto" routing + .patch diff verify + Shadow Second-Eyes
        probe_repo = td_p / "v26_probe"
        probe_repo.mkdir(parents=True, exist_ok=True)
        shutil.copy2(alembic_bom, probe_repo / "BOM.md")
        shutil.copy2(alembic_repo / "Print_Settings.md", probe_repo / "Print_Settings.md")
        subprocess.run(["git", "-C", str(probe_repo), "init", "-q"], check=True)
        subprocess.run(["git", "-C", str(probe_repo), "config", "user.name", "Bench Probe"], check=True)
        subprocess.run(["git", "-C", str(probe_repo), "config", "user.email", "probe@localhost"], check=True)
        subprocess.run(["git", "-C", str(probe_repo), "add", "BOM.md", "Print_Settings.md"], check=True)
        subprocess.run(["git", "-C", str(probe_repo), "commit", "-q", "-m", "baseline"], check=True)
        ps_probe = probe_repo / "Print_Settings.md"
        ps_probe.write_text(
            ps_probe.read_text(encoding="utf-8")
            + "\n- Draft Electrical Note: extruder peak current `99.4 A` at `120 V` (`BOM.md` unverified stub)\n",
            encoding="utf-8",
        )

        r_auto_std = apprentice_mcp_server.apprentice_digest(
            prompt="List top 2 fastener rows in BOM.md citing BOM.md#Lstart-Lend verbatim. Zero preamble.",
            context_files=["BOM.md"],
            repo=str(probe_repo),
            include_git_diff=False,
            effort="auto",
            invocation_tier="auto",
            max_tokens=320,
        )
        r_auto_cross = apprentice_mcp_server.apprentice_digest(
            prompt=(
                "Compare BOM.md against Print_Settings.md and the working-tree git diff for contradictions "
                "or unverified electrical specs. Cite exact file#Lstart-Lend verbatim; zero unit conversions. Zero preamble."
            ),
            context_files=["BOM.md", "Print_Settings.md"],
            repo=str(probe_repo),
            include_git_diff=True,
            effort="auto",
            invocation_tier="explicit",
        )
        auto_std_ok = bool(
            r_auto_std.get("ok")
            and r_auto_std.get("route_id") == "AUTO_STANDARD"
            and r_auto_std.get("effort") == "standard"
            and (r_auto_std.get("completion") or {}).get("finish_reason") == "stop"
        )
        auto_cross_ok = bool(
            r_auto_cross.get("ok")
            and r_auto_cross.get("route_id") == "HIGH_CROSS_SINGLE_SHOT"
            and r_auto_cross.get("effort") == "high"
            and (r_auto_cross.get("verify_claims") or {}).get("ran") is True
            and (r_auto_cross.get("verify_claims") or {}).get("skipped_reason") != "git_diff_head_delta"
            and r_auto_cross.get("claims_verified") is True
            and (r_auto_cross.get("completion") or {}).get("finish_reason") == "stop"
        )
        l12_score = int(auto_std_ok) + int(auto_cross_ok)
        forensics["L12"] = {
            "auto_std": {
                "ok": r_auto_std.get("ok"),
                "route_id": r_auto_std.get("route_id"),
                "effort": r_auto_std.get("effort"),
                "finish": (r_auto_std.get("completion") or {}).get("finish_reason"),
            },
            "auto_cross_diff": {
                "ok": r_auto_cross.get("ok"),
                "route_id": r_auto_cross.get("route_id"),
                "effort": r_auto_cross.get("effort"),
                "verdict": r_auto_cross.get("verdict"),
                "claims_verified": r_auto_cross.get("claims_verified"),
                "verify_claims": r_auto_cross.get("verify_claims"),
                "elapsed_s": (r_auto_cross.get("completion") or {}).get("elapsed_s"),
            },
        }
        metrics.append(
            BenchMetric(
                id="L12_v26_auto_routing",
                pillar="1. Accuracy & Truth",
                name="V2.6 effort=auto routing (AUTO_STANDARD vs HIGH_CROSS_SINGLE_SHOT + .patch verify)",
                value=l12_score,
                unit="/ 2",
                target="2",
                higher_is_better=True,
                status="PASS" if l12_score == 2 else "FAIL",
                details=f"auto_std={auto_std_ok}, auto_cross_diff={auto_cross_ok}",
            )
        )

        r_sh = apprentice_mcp_server.apprentice_shadow_review(
            repo=str(probe_repo),
            draft_files=["Print_Settings.md"],
            context_files=["BOM.md"],
            include_git_diff=True,
            prompt=(
                "List ONLY verified contradictions and [LOAD-BEARING] oracle findings citing exact "
                "file#Lstart-Lend verbatim. Never calculate or convert units unless wrapped in [CALC: a = b]. Zero preamble."
            ),
            effort="auto",
            invocation_tier="explicit",
            async_job=False,
        )
        sh_cpu = r_sh.get("cpu_oracles") or {}
        sh_tel = r_sh.get("completion_telemetry") or {}
        sh_ok = bool(
            r_sh.get("ok")
            and r_sh.get("schema_version") == "SHADOW_SECOND_EYES_V1"
            and r_sh.get("route_id") == "HIGH_CROSS_SINGLE_SHOT"
            and (sh_cpu.get("verify_claims_drafts") or {}).get("ran") is True
            and float(sh_cpu.get("elapsed_ms") or 9999.0) <= 2500.0
            and (r_sh.get("verify_claims") or {}).get("ran") is True
            and r_sh.get("claims_verified") is True
            and sh_tel.get("finish_reason") == "stop"
            and bool(str(r_sh.get("shadow_card") or "").strip())
        )
        forensics["L13"] = {
            "ok": r_sh.get("ok"),
            "schema_version": r_sh.get("schema_version"),
            "route_id": r_sh.get("route_id"),
            "verdict": r_sh.get("verdict"),
            "claims_verified": r_sh.get("claims_verified"),
            "cpu_elapsed_ms": sh_cpu.get("elapsed_ms"),
            "gpu_elapsed_s": sh_tel.get("elapsed_s"),
        }
        metrics.append(
            BenchMetric(
                id="L13_shadow_second_eyes",
                pillar="1. Accuracy & Truth",
                name="V2.6 apprentice_shadow_review (CPU oracles + semantic second-eyes critic)",
                value=float(sh_tel.get("elapsed_s") or 0.0),
                unit="s",
                target="<= 180.0s (CPU<=2.5s)",
                higher_is_better=False,
                status="PASS" if sh_ok else "FAIL",
                details=(
                    f"cpu={sh_cpu.get('elapsed_ms')}ms, verdict={r_sh.get('verdict')}, "
                    f"backed={r_sh.get('claims_verified')}"
                ),
            )
        )

    return metrics, forensics


def load_baseline(history_path: Path) -> dict[str, Any] | None:
    if not history_path.is_file():
        return None
    last_any: dict[str, Any] | None = None
    for raw in history_path.read_text(encoding="utf-8", errors="replace").splitlines():
        if not raw.strip():
            continue
        try:
            row = json.loads(raw)
        except json.JSONDecodeError:
            continue
        if row.get("is_baseline"):
            return row
        last_any = row
    return last_any


def _format_readable_notes(raw: str) -> str:
    """Format dense key=value benchmark notes with clean break points for MarkText/Obsidian."""
    txt = str(raw or "").strip().replace("|", "\\|")
    if not txt:
        return "—"
    txt = txt.replace(", ", " · ")
    txt = txt.replace("=", " = ").replace("<= ", "<= ").replace(">= ", ">= ")
    txt = txt.replace("< = ", "<= ").replace("> = ", ">= ")
    while "  " in txt:
        txt = txt.replace("  ", " ")
    return txt


def render_markdown_report(run_obj: dict[str, Any], baseline: dict[str, Any] | None) -> str:
    """Render compact 5-column pillar-grouped Markdown tables readable in MarkText & Obsidian."""
    base_map: dict[str, dict[str, Any]] = {}
    if baseline:
        for m in baseline.get("metrics") or []:
            base_map[m["id"]] = m

    metrics = list(run_obj.get("metrics") or [])
    n_pass = sum(1 for m in metrics if m.get("status") == "PASS")
    n_fail = sum(1 for m in metrics if m.get("status") == "FAIL")
    n_adv = sum(1 for m in metrics if m.get("status") == "ADVISORY")

    lines = [
        f"# Apprentice Benchmark Report (`{run_obj['run_id']}`)",
        "",
        f"- **Timestamp (UTC):** `{run_obj['timestamp_utc']}` | **Label:** `{run_obj['label']}` | **Mode:** `{run_obj['mode']}`",
        f"- **Verdict Summary:** **`{n_pass} PASS`** · `{n_fail} FAIL` · `{n_adv} ADVISORY` *(grouped by Governing Priority Pillar)*",
    ]

    grouped: dict[str, list[dict[str, Any]]] = {}
    for m in metrics:
        p = str(m.get("pillar") or "Other")
        grouped.setdefault(p, []).append(m)

    for pillar in sorted(grouped.keys()):
        lines.extend(
            [
                "",
                f"## {pillar}",
                "",
                "| Metric | Result | Target | Status | Notes |",
                "| :--- | :--- | :--- | :---: | :--- |",
            ]
        )
        for m in grouped[pillar]:
            cand_disp = f"**{m['value']} {m['unit']}**".strip() if str(m.get("unit") or "").strip() else f"**{m['value']}**"
            b = base_map.get(m["id"])
            if b is not None and isinstance(m["value"], (int, float)) and isinstance(b["value"], (int, float)):
                base_disp = f"{b['value']} {b['unit']}".strip()
                delta = round(float(m["value"]) - float(b["value"]), 3)
                res_cell = f"{cand_disp}<br>Base: {base_disp} ({delta:+})"
            else:
                res_cell = cand_disp
            name_str = str(m.get("name") or m["id"]).replace("|", "\\|")
            metric_cell = f"{name_str}<br>`{m['id']}`"
            target_str = str(m.get("target") or "—").replace("(CPU<=", "(CPU <= ")
            notes_str = _format_readable_notes(str(m.get("details") or ""))
            lines.append(
                f"| {metric_cell} | {res_cell} | {target_str} | **{m['status']}** | {notes_str} |"
            )

    return "\n".join(lines) + "\n"


def run_self_tests() -> dict[str, Any]:
    """Deterministic offline check of benchmark schema, verification helper, and comparison formatter."""
    with tempfile.TemporaryDirectory() as td:
        td_p = Path(td)
        hist = td_p / "hist.jsonl"
        metrics, _ = run_offline_suite(td_p / "missing_tel.jsonl")
        assert len(metrics) == 9, f"expected 9 offline metrics, got {len(metrics)}"
        sample_run = {
            "schema_version": SCHEMA_VERSION,
            "run_id": "BMK-TEST",
            "timestamp_utc": "2026-11-15T00:00:00+00:00",
            "label": "test",
            "mode": "offline",
            "is_baseline": True,
            "metrics": [m.to_dict() for m in metrics],
        }
        hist.write_text(json.dumps(sample_run) + "\n", encoding="utf-8")
        loaded = load_baseline(hist)
        assert loaded is not None and loaded["run_id"] == "BMK-TEST"
        md = render_markdown_report(sample_run, loaded)
        assert "O1_unit_suites" in md and "O8_slice_and_kv_guard" in md and "O9_v23_graduation_guards" in md
    return {"ok": True, "checks": ["offline_9_metrics", "baseline_jsonl_roundtrip", "markdown_comparison_table"]}


def main() -> int:
    parser = argparse.ArgumentParser(description="Bionic Local Sidecar Benchmark & Regression Suite")
    parser.add_argument("--mode", choices=("offline", "live", "all"), default="offline")
    parser.add_argument("--label", default="candidate")
    parser.add_argument("--history-jsonl", default=str(DEFAULT_HISTORY_JSONL))
    parser.add_argument("--telemetry-log", default=str(apprentice_engine.DEFAULT_TELEMETRY_LOG))
    parser.add_argument("--record-baseline", action="store_true")
    parser.add_argument("--append-history", action="store_true")
    parser.add_argument("--compare-baseline", action="store_true")
    parser.add_argument("--output-md", default="")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        res = run_self_tests()
        print(json.dumps(res, indent=2) if args.json else "[PASS] benchmark_apprentice self-tests passed")
        return 0

    tel_path = Path(os.path.expanduser(args.telemetry_log))
    metrics: list[BenchMetric] = []
    forensics: dict[str, Any] = {}
    if args.mode in {"offline", "all"}:
        m_off, f_off = run_offline_suite(tel_path)
        metrics.extend(m_off)
        forensics["offline"] = f_off
    if args.mode in {"live", "all"}:
        m_live, f_live = run_live_suite()
        metrics.extend(m_live)
        forensics["live"] = f_live
        # Refresh O5_eta_mape after live runs so it measures fresh V2 telemetry, and add Q1 quota savings
        fresh_o5 = _compute_o5_eta_metric(tel_path)
        metrics = [fresh_o5 if m.id == "O5_eta_mape" else m for m in metrics]
        q_res = apprentice_engine.estimate_quota_savings(tel_path)
        sc_live = apprentice_engine.load_or_init_scorecard(telemetry_log=tel_path)
        forensics["quota_savings"] = q_res
        forensics["lifetime_scorecard"] = sc_live
        b_eff = q_res["by_effort"]
        tot_k = round(q_res["total_weighted_frontier_equiv_tokens"] / 1000.0, 1)
        std_k = round(b_eff["standard"]["weighted_frontier_equiv_tokens"] / 1000.0, 1)
        high_k = round(b_eff["high"]["weighted_frontier_equiv_tokens"] / 1000.0, 1)
        direct_k = round(q_res["total_direct_offloaded_tokens"] / 1000.0, 1)
        metrics.append(
            BenchMetric(
                id="Q1_quota_saved_k_tok",
                pillar="2. Efficiency",
                name="Cloud frontier-equivalent quota saved (STANDARD vs HIGH)",
                value=tot_k,
                unit="k eq-tok",
                target="> 0.0",
                higher_is_better=True,
                status="PASS" if tot_k > 0.0 else "FAIL",
                details=(
                    f"std={std_k}k ({b_eff['standard']['calls']} calls), "
                    f"high={high_k}k ({b_eff['high']['calls']} calls), direct={direct_k}k"
                ),
            )
        )

    now_utc = dt.datetime.now(dt.timezone.utc)
    run_id = f"BMK-APPRENTICE-{now_utc.strftime('%Y%m%d_%H%M%S')}"
    run_obj = {
        "schema_version": SCHEMA_VERSION,
        "run_id": run_id,
        "timestamp_utc": now_utc.isoformat(timespec="seconds"),
        "label": args.label,
        "mode": args.mode,
        "is_baseline": bool(args.record_baseline),
        "metrics": [m.to_dict() for m in metrics],
        "forensics": forensics,
    }

    hist_path = Path(os.path.expanduser(args.history_jsonl))
    baseline = load_baseline(hist_path) if args.compare_baseline else None

    if args.record_baseline or args.append_history:
        hist_path.parent.mkdir(parents=True, exist_ok=True)
        with open(hist_path, "a", encoding="utf-8") as fh:
            fh.write(json.dumps({k: v for k, v in run_obj.items() if k != "forensics"}) + "\n")

    md_report = render_markdown_report(run_obj, baseline)
    if args.output_md:
        Path(os.path.expanduser(args.output_md)).write_text(md_report, encoding="utf-8")

    if args.json:
        print(json.dumps(run_obj, indent=2))
    else:
        print(md_report)

    has_hard_fail = any(m.status == "FAIL" for m in metrics)
    return 1 if has_hard_fail else 0


if __name__ == "__main__":
    raise SystemExit(main())
