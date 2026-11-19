#!/usr/bin/env python3
"""
Apprentice Phase-3 STANDARD Capability & Bug-Pinning Ladder (`benchmark_apprentice_standard.py`).

Governing Priority Law:
    1. Accuracy & Truth -> 2. Efficiency -> 3. Data Safety -> 4. Speed

Isolates `STANDARD` (`mode="fast"`, `reasoning_effort="none"`, `3072` tok, `--parallel 2`) across 8
seeded ground-truth capability vectors (`S1`..`S8`) inside `~/.cache/apprentice_plugin/bench/`
(0 live production scorecard/telemetry mutations):
  - S1_log_coordinate_sieve         : >=10 KB test/sandbox log coordinate sieve (4 seeded failures)
  - S2_version_log_harvest          : Version_Logs archetype candidate harvesting (2 unharvested vs 2 recorded, 0 YAML cites)
  - S3_qualified_bom_and_caution    : Qualified quantities (~2 m, (4)), [!CAUTION] polarity, acronym lock, & [TBD] preservation
  - S4_dense_multislice_mapper      : 6 explicit #L slices across 3 files (STANDARD Slice-Count Map-Reduce feeding HIGH)
  - S5_stage_stdlib_external_oracle : Pure-stdlib stage_patch tested by 10-case external caller oracle vs llm_self_authored
  - S6_stage_contextualized_fixture : #L-contextualized repo module stage_patch (0 mock spoofing, exact kwarg binding)
  - S7_repair_retention_stress      : STANDARD surgical + full repair stress (fix 4 real defects while retaining 5/5 valid bullets)
  - S8_std_2file_contradictions     : Forced STANDARD 2-file contradiction probe (<8 KB boundary vs HIGH escalation)

Usage:
    python3 -B scripts/benchmark_apprentice_standard.py --self-test --json
    python3 -B scripts/benchmark_apprentice_standard.py --list
    python3 -B scripts/benchmark_apprentice_standard.py --vectors S1,S2,S3,S4 --json
    python3 -B scripts/benchmark_apprentice_standard.py --vectors ALL --output-md bench_std_report.md --json
"""
from __future__ import annotations

import argparse
import ast
import datetime as dt
import importlib.util
import json
import os
import re
import sys
import tempfile
import time
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))
if str(SCRIPT_DIR / "apprentice") not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR / "apprentice"))

import apprentice_engine  # noqa: E402
import apprentice_mcp_server  # noqa: E402
import benchmark_apprentice  # noqa: E402

SCHEMA_VERSION = "APPRENTICE_STD_LADDER_V1"
VECTOR_ORDER = ("S1", "S2", "S3", "S4", "S5", "S5B", "S6", "S7", "S8", "S8B", "S8C", "S8D", "S8E")
VECTOR_DESCRIPTIONS: dict[str, str] = {
    "S1": "S1_log_coordinate_sieve — >=10 KB sandbox/test log failure coordinate sieve (4 seeded failures)",
    "S2": "S2_version_log_harvest — #L-anchored Version_Logs unharvested archetype extraction (0 YAML/recorded bleed)",
    "S3": "S3_qualified_bom_and_caution — Qualified quantities (~2 m), [!CAUTION] polarity, SHCS acronym lock, & [TBD]",
    "S4": "S4_dense_multislice_mapper — 6 explicit #L slices across 3 files (STANDARD mapper recall & anchor bounds)",
    "S5": "S5_stage_stdlib_external_oracle — Pure-stdlib stage_patch scored by 10-case external caller oracle",
    "S5B": "S5B_stage_stdlib_explicit_sep_spec — Pure-stdlib stage_patch with explicit :--- alignment separator contract",
    "S6": "S6_stage_contextualized_fixture — #L-contextualized local API stage_patch (exact kwargs, 0 mock spoofing)",
    "S7": "S7_repair_retention_stress — STANDARD surgical+full repair (fix 4 defects while retaining 5/5 valid claims)",
    "S8": "S8_std_2file_contradictions — Forced STANDARD <8 KB 2-file contradiction ceiling probe",
    "S8B": "S8B_std_mid_2file_contradictions — Forced STANDARD ~14 KB multi-section 2-file contradiction probe (4 defects)",
    "S8C": "S8C_std_large_3file_contradictions — Forced STANDARD ~24 KB 3-file cross-domain contradiction ceiling probe (5 defects)",
    "S8D": "S8D_std_42kb_3file_contradictions — Forced STANDARD ~42 KB 3-file high-volume contradiction cliff probe (6 defects)",
    "S8E": "S8E_std_semantic_logic_traps — Forced STANDARD subtle semantic/polarity/multi-hop contradictions (4 non-obvious traps)",
}


# ---------------------------------------------------------------------------
# Deterministic Fixture Builders & Ground-Truth Scorers
# ---------------------------------------------------------------------------


def build_s1_log_fixture(root: Path) -> tuple[Path, dict[str, int]]:
    """Build a >=10 KB multi-suite sandbox log with 4 seeded failures at known line numbers."""
    lines: list[str] = []
    planted: dict[str, int] = {}
    for idx in range(1, 335):
        if idx == 47:
            lines.append("[FAIL] test_boundary_gate (suite_alpha.py): EROFS_BLOCKED_WRITE on /etc/shadow_probe (exit=1)")
            planted["EROFS_BLOCKED_WRITE"] = idx
        elif idx == 128:
            lines.append("AssertionError: step_count mismatch in gantry_homing: expected 1600, observed 800")
            planted["1600"] = idx
        elif idx == 219:
            lines.append("subprocess.TimeoutExpired: Command ['klipper_mcu_sim', '--sync'] timed out after 15.0 seconds")
            planted["TimeoutExpired"] = idx
        elif idx == 294:
            lines.append("[UNBACKED_CLAIM] Line 63: unverified peak current `14.5 A` missing from primary schematic")
            planted["14.5 A"] = idx
        else:
            lines.append(
                f"[PASS] suite_runner_worker_{(idx % 8) + 1:02d} :: check_invariant_{idx:03d} "
                f"completed in 0.{(idx % 9) + 1}2s (crc=0x{idx * 2654435761 & 0xFFFFFFFF:08x}, status=OK)"
            )
    log_path = root / "sandbox_run.log"
    log_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return log_path, planted


def score_s1_output(text: str, planted: dict[str, int], log_path: Path) -> dict[str, Any]:
    low = text.lower()
    recalled: list[str] = []
    missed: list[str] = []
    anchor_hits: list[str] = []
    for key, line_no in planted.items():
        has_tok = key.lower() in low
        # Accept exact line or tight +-2 window around the failure line
        near_anchor = any(
            abs(s_i - line_no) <= 2 or (s_i <= line_no <= e_i and (e_i - s_i) <= 8)
            for _p, s_i, e_i in apprentice_mcp_server._extract_anchor_spans(text)
        )
        if has_tok and near_anchor:
            recalled.append(key)
            anchor_hits.append(f"{key}@L{line_no}")
        else:
            missed.append(f"{key}(tok={has_tok},anchor={near_anchor})")
    false_pass_leak = len(re.findall(r"check_invariant_\d+", text))
    defects = apprentice_mcp_server._detect_citation_format_defects(text, [log_path])
    return {
        "recall_hits": len(recalled),
        "recall_total": len(planted),
        "recall_pct": round(100.0 * len(recalled) / len(planted), 1),
        "false_noise_lines": false_pass_leak,
        "citation_defects": len(defects),
        "missed": missed,
        "passed": len(recalled) == len(planted) and false_pass_leak == 0 and not defects,
    }


def build_s2_worklog_fixture(root: Path) -> Path:
    body = """---
title: "Subsystem Release Worklog v0.9"
project: "Demo_Subsys"
entity: "Alpha_Eng"
compartment: "private"
note_type: "version_worklog"
authoritative: false
last_synced: "2026-11-18"
---

# Subsystem Release Worklog v0.9

## 1. Shipped Milestones & Harvested Notes

1. **Deterministic CRC32 Header Framing (`serial_bus.py`)**:
   - Replaced raw newline framing with `4`-byte `CRC32` packet headers, cutting framing drops from `3.2%` to `0.0%` over `100,000` frames. *(Recorded as LL-011).*
2. **SPI DMA Double-Buffer Dead-End (`spi_ burst.py`)**:
   - Rejected asynchronous `2`-channel DMA chaining because `FIFO` watermark interrupts raced on `64`-byte boundaries at `24 MHz`. *(Recorded as LL-012).*

## 2. Newly Observed Field Findings (Pending Triage)

1. **[TRAP] Inductive Probe `24 V` Back-Feed Without Clamp Diode (`probe_input.cfg`)**:
   - Connecting an NPN inductive probe powered from `24 V` directly to MCU pin `PA8` without a `BAT85` Schottky blocking diode leaked `3.9 V` onto the `3.3 V` rail whenever the pull-up floated.
2. **[TRADE-OFF] `16`-Microstep Interpolated vs `32`-Microstep Non-Interpolated XY Drive (`stepper_xy.cfg`)**:
   - Chose `32` microsteps with `interpolate: False` over `16` interpolated microsteps; Stepper ISR rate doubled to `64 kHz` (`+4%` MCU load) while eliminating `0.04 mm` phase-lag cornering artifacts.
"""
    # Pad benign context notes so file is realistic ~4 KB
    extra = "\n".join(
        f"- Build check #{i:02d}: regression matrix slice `{i}` verified clean (`0` errors)."
        for i in range(1, 36)
    )
    wl = root / "v0.9_Subsystem_Worklog.md"
    wl.write_text(body + "\n## 3. Routine Matrix Checks\n\n" + extra + "\n", encoding="utf-8")
    return wl


def score_s2_output(text: str, wl_path: Path) -> dict[str, Any]:
    low = text.lower()
    has_bat85 = "bat85" in low and ("pa8" in low or "24 v" in low)
    has_microstep = "32" in low and ("interpolate" in low or "0.04 mm" in low)
    leaked_recorded = ("ll-011" in low or "crc32" in low or "ll-012" in low or "24 mhz" in low)
    frontmatter_cite = any(
        s_i <= 9 for _p, s_i, _e_i in apprentice_mcp_server._extract_anchor_spans(text)
    )
    defects = apprentice_mcp_server._detect_citation_format_defects(text, [wl_path])
    hits = int(has_bat85) + int(has_microstep)
    return {
        "recall_hits": hits,
        "recall_total": 2,
        "recall_pct": round(100.0 * hits / 2.0, 1),
        "leaked_already_recorded": leaked_recorded,
        "cited_yaml_frontmatter": frontmatter_cite,
        "citation_defects": len(defects),
        "passed": hits == 2 and not leaked_recorded and not frontmatter_cite and not defects,
    }


def build_s3_bom_caution_fixture(root: Path) -> tuple[Path, Path]:
    bom = root / "BOM.md"
    guide = root / "Assembly_Guide.md"
    bom.write_text(
        """# Bill of Materials (`BOM.md`)

| Category | Part | Spec | Qty | Notes |
| :--- | :--- | :--- | :---: | :--- |
| Fasteners | Carriage Mount Screw | `M3x8mm SHCS` | `(4)` | Stainless A2-70 |
| Fasteners | Rear Cover Screw | `M3 BHCS` | `[TBD: rear_cover_m3_count]` | Pending physical bench count |
| Pneumatics | Feed Tube | `4mm OD x 2.5mm ID PTFE` | `~2 m` | Cut to routing length |
| Electrical | Heater Cartridge | `24 V 60 W` | `1` | High-temp silicone leads |
""",
        encoding="utf-8",
    )
    guide.write_text(
        """# Assembly Guide (`Assembly_Guide.md`)

## Step 4 — Carriage & PTFE Routing

1. Fasten the carriage block using `(4)` `M3x8mm SHCS` fasteners torqued to `1.2 N·m`.
2. Route `~2 m` of `4mm OD x 2.5mm ID PTFE` tubing with a minimum bend radius of `45 mm`.

> [!CAUTION]
> **24 V Inductive Input Hazard**: NEVER wire the `24 V` sensor supply directly to MCU pin `PB6` without an inline `BAT85` blocking diode; direct `24 V` contact destroys the `3.3 V` GPIO bank immediately.
""",
        encoding="utf-8",
    )
    return bom, guide


def score_s3_output(text: str, sources: list[Path]) -> dict[str, Any]:
    low = text.lower()
    kept_tilde_qty = "~2 m" in low or "~2m" in low
    kept_paren_qty = "(4)" in text or "4" in text
    kept_tbd = "[tbd:" in low and "rear_cover_m3_count" in low
    kept_caution_polarity = (
        ("caution" in low or "hazard" in low)
        and ("never" in low or "without" in low or "destroys" in low)
        and "pb6" in low
        and "bat85" in low
    )
    expanded_acronym = "socket head cap" in low or "button head cap" in low
    defects = apprentice_mcp_server._detect_citation_format_defects(text, sources)
    checks = {
        "kept_tilde_2m": kept_tilde_qty,
        "kept_m3x8_shcs": kept_paren_qty and "m3x8mm shcs" in low,
        "kept_tbd_marker": kept_tbd,
        "kept_caution_polarity": kept_caution_polarity,
        "zero_acronym_expansion": not expanded_acronym,
        "zero_citation_defects": len(defects) == 0,
    }
    passed_cnt = sum(1 for v in checks.values() if v)
    return {
        "checks": checks,
        "recall_hits": passed_cnt,
        "recall_total": len(checks),
        "recall_pct": round(100.0 * passed_cnt / len(checks), 1),
        "passed": all(checks.values()),
    }


def build_s4_multislice_fixture(root: Path) -> tuple[list[str], list[Path], dict[str, str]]:
    """Build 3 files with 6 explicit #L slices (including 2 non-overlapping slices in mcu.cfg)."""
    f1 = root / "mcu.cfg"
    f2 = root / "thermals.cfg"
    f3 = root / "motion.cfg"

    f1_lines = [f"# padding line {i}" for i in range(1, 95)]
    f1_lines[9] = "serial_port: /dev/serial/by-id/usb-Klipper_stm32h723xx_29001A"
    f1_lines[10] = "baud_rate: 250000"
    f1_lines[74] = "canbus_uuid: 9f8e7d6c5b4a"
    f1_lines[75] = "canbus_bitrate: 1000000"
    f1.write_text("\n".join(f1_lines) + "\n", encoding="utf-8")

    f2_lines = [f"# thermal comment {i}" for i in range(1, 90)]
    f2_lines[14] = "max_temp_hotend: 315"
    f2_lines[68] = "chamber_cutoff_c: 72"
    f2.write_text("\n".join(f2_lines) + "\n", encoding="utf-8")

    f3_lines = [f"# motion comment {i}" for i in range(1, 90)]
    f3_lines[19] = "max_velocity_mm_s: 550"
    f3_lines[71] = "max_z_accel_mm_s2: 350"
    f3.write_text("\n".join(f3_lines) + "\n", encoding="utf-8")

    specs = [
        "mcu.cfg#L8-L14",
        "mcu.cfg#L72-L79",
        "thermals.cfg#L12-L18",
        "thermals.cfg#L66-L72",
        "motion.cfg#L18-L24",
        "motion.cfg#L69-L76",
    ]
    expected_tokens = {
        "stm32h723xx_29001a": "mcu.cfg#L10",
        "9f8e7d6c5b4a": "mcu.cfg#L75",
        "315": "thermals.cfg#L15",
        "72": "thermals.cfg#L69",
        "550": "motion.cfg#L20",
        "350": "motion.cfg#L72",
    }
    return specs, [f1, f2, f3], expected_tokens


def score_s4_output(text: str, files: list[Path], expected_tokens: dict[str, str]) -> dict[str, Any]:
    low = text.lower()
    found = [tok for tok in expected_tokens if tok in low]
    missed = [f"{tok}({loc})" for tok, loc in expected_tokens.items() if tok not in low]
    defects = apprentice_mcp_server._detect_citation_format_defects(text, files)
    return {
        "recall_hits": len(found),
        "recall_total": len(expected_tokens),
        "recall_pct": round(100.0 * len(found) / len(expected_tokens), 1),
        "missed": missed,
        "citation_defects": len(defects),
        "passed": len(found) == len(expected_tokens) and not defects,
    }


def run_s5_external_oracle(staged_py: Path) -> dict[str, Any]:
    """Load staged `pin_parser.py` and run 10 deterministic caller-owned edge-case assertions."""
    if not staged_py.is_file():
        return {"passed": False, "cases_passed": 0, "cases_total": 10, "errors": ["staged_file_missing"]}
    spec = importlib.util.spec_from_file_location("staged_pin_parser_s5", str(staged_py))
    if spec is None or spec.loader is None:
        return {"passed": False, "cases_passed": 0, "cases_total": 10, "errors": ["spec_load_failed"]}
    mod = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(mod)
    except Exception as exc:
        return {"passed": False, "cases_passed": 0, "cases_total": 10, "errors": [f"import_crash: {exc}"]}

    fn = getattr(mod, "parse_pin_table", None)
    if not callable(fn):
        return {"passed": False, "cases_passed": 0, "cases_total": 10, "errors": ["missing_parse_pin_table"]}

    cases_passed = 0
    errors: list[str] = []

    sample_md = """
# MCU Pinout
| Signal | Pin | Pull |
| :--- | :--- | :--- |
| STEP_X | `PA1` | none |
| ENDSTOP_X | `!^PB4` | pullup |
| ENABLE_X | `^!PC13` | pullup |
| FAN_PWM | `~PD2` | none |
"""
    try:
        rows = fn(sample_md)
        if isinstance(rows, list) and len(rows) == 4:
            cases_passed += 1
        else:
            errors.append(f"c1_len: got {type(rows).__name__} len={len(rows) if isinstance(rows, list) else 'N/A'}")

        by_sig = {r.get("signal"): r for r in rows if isinstance(r, dict)}
        r1 = by_sig.get("STEP_X") or {}
        if r1.get("pin") == "PA1" and r1.get("inverted") is False and r1.get("pullup") is False:
            cases_passed += 1
        else:
            errors.append(f"c2_step_x: {r1}")

        r2 = by_sig.get("ENDSTOP_X") or {}
        if r2.get("pin") == "PB4" and r2.get("inverted") is True and r2.get("pullup") is True:
            cases_passed += 1
        else:
            errors.append(f"c3_endstop_x(!^PB4): {r2}")

        r3 = by_sig.get("ENABLE_X") or {}
        if r3.get("pin") == "PC13" and r3.get("inverted") is True and r3.get("pullup") is True:
            cases_passed += 1
        else:
            errors.append(f"c4_enable_x(^!PC13): {r3}")

        r4 = by_sig.get("FAN_PWM") or {}
        if r4.get("pin") == "PD2" and r4.get("pulldown") is True and r4.get("inverted") is False:
            cases_passed += 1
        else:
            errors.append(f"c5_fan_pwm(~PD2): {r4}")
    except Exception as exc:
        errors.append(f"c1_c5_exc: {exc}")

    # Case 6: Empty / header-only table -> []
    try:
        empty_res = fn("| Signal | Pin | Pull |\n| --- | --- | --- |\n")
        if empty_res == []:
            cases_passed += 1
        else:
            errors.append(f"c6_empty: {empty_res}")
    except Exception as exc:
        errors.append(f"c6_exc: {exc}")

    # Case 7: Duplicate raw pin (`PA1` and `!PA1` collide on physical pin `PA1`) -> ValueError
    try:
        fn("| Signal | Pin | Pull |\n| :--- | :--- | :--- |\n| A | PA1 | none |\n| B | !PA1 | pullup |\n")
        errors.append("c7_dup_pin: expected ValueError on PA1 vs !PA1")
    except ValueError:
        cases_passed += 1
    except Exception as exc:
        errors.append(f"c7_wrong_exc: {type(exc).__name__}: {exc}")

    # Case 8: Conflicting `^` and `~` on same pin (`^~PA2`) -> ValueError
    try:
        fn("| Signal | Pin | Pull |\n| :--- | :--- | :--- |\n| BAD | ^~PA2 | both |\n")
        errors.append("c8_conflict_pull: expected ValueError on ^~PA2")
    except ValueError:
        cases_passed += 1
    except Exception as exc:
        errors.append(f"c8_wrong_exc: {type(exc).__name__}: {exc}")

    # Case 9: Inline `#` comments inside Pin cell stripped cleanly (`!PA9 # probe`)
    try:
        c9 = fn("| Signal | Pin | Pull |\n| :--- | :--- | :--- |\n| PROBE | `!PA9 # opto` | none |\n")
        if len(c9) == 1 and c9[0].get("pin") == "PA9" and c9[0].get("inverted") is True:
            cases_passed += 1
        else:
            errors.append(f"c9_inline_comment: {c9}")
    except Exception as exc:
        errors.append(f"c9_exc: {exc}")

    # Case 10: Preserves row order across multiple valid pins
    try:
        c10 = fn("| Signal | Pin | Pull |\n|---|---|---|\n| Z1 | PE0 | none |\n| Z2 | PE1 | none |\n| Z3 | PE2 | none |\n")
        if [x.get("pin") for x in c10] == ["PE0", "PE1", "PE2"]:
            cases_passed += 1
        else:
            errors.append(f"c10_order: {c10}")
    except Exception as exc:
        errors.append(f"c10_exc: {exc}")

    return {
        "passed": cases_passed == 10,
        "cases_passed": cases_passed,
        "cases_total": 10,
        "errors": errors,
    }


def build_s6_repo_api_fixture(root: Path) -> Path:
    api_py = root / "telemetry_window.py"
    api_py.write_text(
        '''"""Authoritative sensor window evaluator for S6 contextualized stage_patch check."""
from __future__ import annotations

from typing import Any


def evaluate_sensor_window(
    samples: list[float],
    *,
    low_limit: float,
    high_limit: float,
    max_spike_count: int = 0,
) -> dict[str, Any]:
    """Evaluate readings using strict keyword-only bounds (low_limit, high_limit, max_spike_count)."""
    if low_limit >= high_limit:
        raise ValueError("low_limit must be strictly less than high_limit")
    if not samples:
        return {"status": "EMPTY", "in_bounds": 0, "spikes": 0, "mean": None}
    spikes = sum(1 for val in samples if val < low_limit or val > high_limit)
    in_b = len(samples) - spikes
    status = "PASS" if spikes <= max_spike_count else "TRIPPED"
    return {
        "status": status,
        "in_bounds": in_b,
        "spikes": spikes,
        "mean": round(sum(samples) / len(samples), 3),
    }
''',
        encoding="utf-8",
    )
    return api_py


def score_s6_staged_harness(staged_py: Path, repo_dir: Path) -> dict[str, Any]:
    """Verify staged S6 harness imports real telemetry_window without mock/sys.modules spoofing and runs cleanly."""
    if not staged_py.is_file():
        return {"passed": False, "errors": ["staged_file_missing"]}
    src = staged_py.read_text(encoding="utf-8", errors="replace")
    try:
        tree = ast.parse(src)
    except SyntaxError as exc:
        return {"passed": False, "errors": [f"syntax_error: {exc}"]}

    used_mock_spoof = False
    imports_target = False
    calls_kw_exact = False
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for al in node.names:
                if al.name == "telemetry_window":
                    imports_target = True
                if "mock" in al.name:
                    used_mock_spoof = True
        elif isinstance(node, ast.ImportFrom):
            if node.module == "telemetry_window":
                imports_target = True
            if node.module and "mock" in node.module:
                used_mock_spoof = True
        elif isinstance(node, ast.Attribute) and node.attr == "modules":
            used_mock_spoof = True
        elif isinstance(node, ast.Call):
            kw_names = {kw.arg for kw in node.keywords if kw.arg}
            if {"low_limit", "high_limit"}.issubset(kw_names):
                calls_kw_exact = True

    env = os.environ.copy()
    env["PYTHONPATH"] = f"{repo_dir}{os.pathsep}{env.get('PYTHONPATH', '')}".rstrip(os.pathsep)
    rc, dt_s, out, err = benchmark_apprentice._run_subprocess(
        [sys.executable, "-B", str(staged_py), "--self-test"],
        timeout_s=15,
        env=env,
    )
    if rc != 0:
        # Also try plain execution if script runs assertions under __main__ without requiring --self-test
        rc2, dt_s2, out2, err2 = benchmark_apprentice._run_subprocess(
            [sys.executable, "-B", str(staged_py)],
            timeout_s=15,
            env=env,
        )
        if rc2 == 0:
            rc, dt_s, out, err = rc2, dt_s2, out2, err2

    passed = imports_target and calls_kw_exact and not used_mock_spoof and rc == 0
    return {
        "passed": passed,
        "imports_target": imports_target,
        "calls_kw_exact": calls_kw_exact,
        "zero_mock_spoofing": not used_mock_spoof,
        "exec_rc": rc,
        "exec_s": dt_s,
        "output_tail": ((out or "") + "\n" + (err or "")).strip()[-400:],
    }


def build_s7_corrupted_draft_fixture(root: Path) -> tuple[Path, Path, str, tuple[str, ...]]:
    """Build sources + a draft with 5 valid bullets and 4 real historical defects for STANDARD repair testing."""
    bom, guide = build_s3_bom_caution_fixture(root)
    # Add extra rows so we have 5 distinct valid facts + 4 defective lines
    bom.write_text(
        bom.read_text(encoding="utf-8")
        + "| Fasteners | Idler Shaft Pin | `5mm x 30mm Dowel` | `2` | Hardened steel |\n"
        + "| Motion | Timing Belt | `GT2 6mm Belt` | `1` | Fiberglass core |\n"
        + "| Sensors | Chamber Thermistor | `NTC 100K B3950` | `1` | Frame clip |\n",
        encoding="utf-8",
    )
    corrupted_draft = "\n".join(
        [
            "- Carriage mount uses `(4)` `M3x8mm SHCS` torqued to `1.2 N·m` (BOM.md#L5, Assembly_Guide.md#L5).",
            "- Rear cover fastener quantity is `[TBD: rear_cover_m3_count]` (`M3 BHCS`) pending count (BOM.md#L6).",
            "- Idler shaft uses `2` `5mm x 30mm Dowel` pins in hardened steel (BOM.md#L9).",
            "- Motion drive uses `1` `GT2 6mm Belt` with fiberglass core (BOM.md#L10).",
            "- Chamber sensor uses `1` `NTC 100K B3950` thermistor (BOM.md#L11).",
            "- Feed tube requires `2 m` of `4mm OD x 2.5mm ID PTFE` (#BOM.md#L7#Assembly_Guide.md#L6).",
            "- Heater cartridge is rated `24 V 60 W` with nozzle clearance (e.g., 0.8mm) [BOM.md:L8].",
            "- Fastener summary `[CALC: Total_Pins = 4 + 2 = 6]` across carriage and idler (BOM.md#L5-L99).",
            "- Sensor note: wire `24 V` supply to pin `PB6` with `BAT85` diode (Assembly_Guide.md#L8-L9).",
        ]
    )
    must_retain_tokens = (
        "m3x8mm shcs",
        "rear_cover_m3_count",
        "5mm x 30mm dowel",
        "gt2 6mm belt",
        "ntc 100k b3950",
    )
    return bom, guide, corrupted_draft, must_retain_tokens


def score_s7_repaired_draft(
    repaired_text: str,
    vrf_after: dict[str, Any],
    must_retain_tokens: tuple[str, ...],
) -> dict[str, Any]:
    low = repaired_text.lower()
    retained = [tok for tok in must_retain_tokens if tok in low]
    dropped = [tok for tok in must_retain_tokens if tok not in low]
    vrf_clean = bool(vrf_after.get("ran") and vrf_after.get("returncode") == 0 and int(vrf_after.get("unbacked", 99)) == 0)
    return {
        "vrf_clean": vrf_clean,
        "retained_valid_bullets": len(retained),
        "retained_total": len(must_retain_tokens),
        "retention_pct": round(100.0 * len(retained) / len(must_retain_tokens), 1),
        "dropped_tokens": dropped,
        "unbacked_remaining": vrf_after.get("unbacked"),
        "passed": vrf_clean and len(retained) == len(must_retain_tokens),
    }


def build_s8_contradiction_fixture(root: Path) -> tuple[Path, Path]:
    bom = root / "BOM.md"
    guide = root / "Assembly_Guide.md"
    bom.write_text(
        """# Bill of Materials (`BOM.md`)

| Part | Specification | Qty |
| :--- | :--- | :---: |
| Extruder Motor Mount Screw | `M3x12mm SHCS` | `4` |
| Hotend Cooling Fan | `24 V 3010 Axial Fan` | `1` |
| Frame Heat-Set Insert | `M3x5x4mm Brass Insert` | `6` |
| Linear Rail | `MGN9H 150mm` | `1` |
""",
        encoding="utf-8",
    )
    guide.write_text(
        """# Assembly Guide (`Assembly_Guide.md`)

## Step 1 — Heat-Set Inserts
Install all `8` `M3x5x4mm Brass Insert` fittings into the main housing bores (`Assembly_Guide.md`).

## Step 2 — Extruder Motor & Fan
1. Secure the extruder motor using `4` `M3x16mm SHCS` screws.
2. Connect the `12 V 3010 Axial Fan` lead to `FAN0` and slide the `MGN9H 150mm` rail into place.
""",
        encoding="utf-8",
    )
    return bom, guide


def score_s8_output(text: str, sources: list[Path]) -> dict[str, Any]:
    low = text.lower()
    c_screw = "m3x12mm" in low and "m3x16mm" in low
    c_fan = "fan" in low and "24 v" in low and "12 v" in low
    c_insert = ("insert" in low or "m3x5x4mm" in low) and ("6" in low and "8" in low)
    false_rail = "150mm" in low and ("conflict" in low.split("150mm")[0][-40:] if "150mm" in low else False)
    defects = apprentice_mcp_server._detect_citation_format_defects(text, sources)
    caught = int(c_screw) + int(c_fan) + int(c_insert)
    return {
        "contradictions_caught": caught,
        "contradictions_total": 3,
        "recall_pct": round(100.0 * caught / 3.0, 1),
        "details": {"screw_len_12_vs_16": c_screw, "fan_24v_vs_12v": c_fan, "inserts_6_vs_8": c_insert},
        "false_rail_conflict": false_rail,
        "citation_defects": len(defects),
        "passed": caught == 3 and not false_rail and not defects,
    }


def build_s8b_mid_contradiction_fixture(root: Path) -> tuple[Path, Path]:
    """Build a ~14 KB 2-file mechanical/electrical spec pair with 4 dispersed contradictions."""
    bom = root / "BOM.md"
    guide = root / "Assembly_Guide.md"
    bom_rows = [
        "# Subsystem Bill of Materials (`BOM.md`)",
        "",
        "| Part | Spec | Qty | Notes |",
        "| :--- | :--- | :---: | :--- |",
        "| Carriage Mount Screw | `M3x8mm SHCS` | `4` | Black oxide steel |",
    ]
    guide_lines = [
        "# Subsystem Assembly Guide (`Assembly_Guide.md`)",
        "",
        "## 1. Frame & Fastener Preparation",
        "1. Align the X carriage using `4` `M3x8mm SHCS` screws torqued cleanly.",
    ]
    for idx in range(1, 55):
        bom_rows.append(f"| Spacer Sleeve S{idx:02d} | `OD 8mm ID 5.1mm L {10 + (idx % 7)}mm Aluminum` | `{2 + (idx % 3)}` | Station {idx:02d} matched |")
        guide_lines.append(f"- Step F{idx:02d}: Seat `{2 + (idx % 3)}` `OD 8mm ID 5.1mm L {10 + (idx % 7)}mm Aluminum` sleeves on station {idx:02d}.")
    # Dispersed contradictions across middle & tail sections
    bom_rows.insert(18, "| Motor Mount Fastener | `M3x14mm SHCS` | `4` | NEMA-17 bracket |")
    bom_rows.insert(34, "| Chamber Heater Relay | `24 V 10 A SSR` | `1` | DIN rail module |")
    bom_rows.append("| Pneumatic Exhaust Port | `6mm OD Push-to-Connect` | `2` | Manifold outlet |")
    bom_rows.append("| Main Power Supply | `24 V 350 W PSU` | `1` | Enclosed supply |")

    guide_lines.insert(22, "## 2. Stepper & Electrical Section\n- Install `4` `M3x20mm SHCS` bolts into the NEMA-17 bracket.")
    guide_lines.insert(40, "- Mount the `12 V 10 A SSR` module onto the lower DIN rail channel.")
    guide_lines.append("## 3. Final Pneumatic & Power Hookup")
    guide_lines.append("- Thread `2` `4mm OD Push-to-Connect` fittings into the manifold outlet ports.")
    guide_lines.append("- Wire the `24 V 200 W PSU` DC bus cleanly before first power-on.")

    bom.write_text("\n".join(bom_rows) + "\n", encoding="utf-8")
    guide.write_text("\n".join(guide_lines) + "\n", encoding="utf-8")
    return bom, guide


def score_s8b_output(text: str, sources: list[Path]) -> dict[str, Any]:
    low = text.lower()
    c_bolt = "m3x14mm" in low and "m3x20mm" in low
    c_ssr = "ssr" in low and "24 v" in low and "12 v" in low
    c_port = ("6mm" in low and "4mm" in low) and ("push" in low or "port" in low or "fitting" in low or "pneumatic" in low)
    c_psu = "350 w" in low and "200 w" in low
    defects = apprentice_mcp_server._detect_citation_format_defects(text, sources)
    caught = int(c_bolt) + int(c_ssr) + int(c_port) + int(c_psu)
    return {
        "contradictions_caught": caught,
        "contradictions_total": 4,
        "recall_pct": round(100.0 * caught / 4.0, 1),
        "details": {"bolt_14_vs_20": c_bolt, "ssr_24v_vs_12v": c_ssr, "port_6mm_vs_4mm": c_port, "psu_350w_vs_200w": c_psu},
        "citation_defects": len(defects),
        "passed": caught == 4 and not defects,
    }


def build_s8c_large_3file_contradiction_fixture(root: Path) -> tuple[Path, Path, Path]:
    """Build a ~32 KB 3-file cross-domain (BOM.md + Assembly_Guide.md + control.cfg) fixture with 5 subtle mismatches."""
    bom = root / "BOM.md"
    guide = root / "Assembly_Guide.md"
    cfg = root / "control.cfg"

    bom_rows = [
        "# Master Bill of Materials (`BOM.md`)",
        "",
        "| Subassembly | Part | Specification | Qty | Reference |",
        "| :--- | :--- | :--- | :---: | :--- |",
    ]
    guide_lines = [
        "# Complete Assembly Guide (`Assembly_Guide.md`)",
        "",
        "## Section 1 — Structural Frame & Plates",
    ]
    cfg_lines = [
        "# Firmware & Motion Configuration (`control.cfg`)",
        "",
    ]

    for i in range(1, 105):
        bom_rows.append(
            f"| Frame_{i:03d} | Alignment Pin P{i:03d} | `Dowel {4 + (i % 4)}mm x {14 + (i % 5)}mm Hardened` | `{2 + (i % 2)}` | Rev A{i % 3} |"
        )
        guide_lines.append(
            f"- Step {i:03d}: Press `{2 + (i % 2)}` `Dowel {4 + (i % 4)}mm x {14 + (i % 5)}mm Hardened` alignment pins at Station {i:03d}."
        )
        cfg_lines.extend(
            [
                f"[stepper_aux_{i:03d}]",
                f"step_pin: PG{i % 16}",
                f"microsteps: {16 if i % 2 == 0 else 32}",
                f"run_current: {0.65 + 0.05 * (i % 4):.2f}",
                "",
            ]
        )

    # Plant 5 dispersed contradictions (across pairs and 3-way BOM <-> Guide <-> .cfg)
    bom_rows.insert(18, "| Toolhead | Hotend Mounting Bolt | `M3x25mm SHCS` | `2` | Secures heater block |")
    guide_lines.insert(26, "- Torque `2` `M3x30mm SHCS` hotend mounting bolts into the heatsink bridge.")

    bom_rows.insert(52, "| Heated Bed | Thermal Fuse | `125 C One-Shot Cutoff` | `1` | Series safety |")
    guide_lines.insert(61, "- Bond the `150 C One-Shot Cutoff` thermal fuse beneath the aluminum cast bed.")

    bom_rows.insert(84, "| Probe | Inductive Sensor Supply | `24 V DC` | `1` | Pin PB12 w/ diode |")
    cfg_lines.insert(95, "# Inductive sensor logic\n[probe]\npin: !PB12\nvoltage_rail: 12V\n")

    bom_rows.append("| Extruder | Drive Gear Module | `36-Tooth Steel Gear` | `1` | Dual-drive |")
    cfg_lines.append("[extruder]\ngear_ratio: 50:10\nrotation_distance: 22.678\nsensor_type: PT1000\n")
    guide_lines.append("- Configure the extrusion ratio for the `17-Tooth Steel Gear` direct-drive stage.")

    bom_rows.append("| Aux Fan | Part Cooling Blower | `24 V 5015 Blower` | `2` | PWM Controlled |")
    cfg_lines.append("[fan_generic part_blower]\npin: PA6\nshutdown_speed: 1\nmax_power: 0.85\n")
    guide_lines.append("- Verify the `24 V 5015 Blower` safety setting requires `shutdown_speed: 0` on controller fault.")

    bom.write_text("\n".join(bom_rows) + "\n", encoding="utf-8")
    guide.write_text("\n".join(guide_lines) + "\n", encoding="utf-8")
    cfg.write_text("\n".join(cfg_lines) + "\n", encoding="utf-8")
    return bom, guide, cfg


def score_s8c_output(text: str, sources: list[Path]) -> dict[str, Any]:
    low = text.lower()
    c_bolt = "m3x25mm" in low and "m3x30mm" in low
    c_fuse = ("125" in low and "150" in low) and ("fuse" in low or "cutoff" in low)
    c_probe_v = ("pb12" in low or "probe" in low or "inductive" in low) and ("24" in low and "12" in low)
    c_gear = "36" in low and "17" in low and ("gear" in low or "tooth" in low)
    c_shutdown = "shutdown_speed" in low and ("1" in low and "0" in low)
    defects = apprentice_mcp_server._detect_citation_format_defects(text, sources)
    caught = int(c_bolt) + int(c_fuse) + int(c_probe_v) + int(c_gear) + int(c_shutdown)
    return {
        "contradictions_caught": caught,
        "contradictions_total": 5,
        "recall_pct": round(100.0 * caught / 5.0, 1),
        "details": {
            "bolt_25_vs_30": c_bolt,
            "thermal_fuse_125_vs_150": c_fuse,
            "probe_rail_24v_vs_12v": c_probe_v,
            "gear_36_vs_17": c_gear,
            "blower_shutdown_1_vs_0": c_shutdown,
        },
        "citation_defects": len(defects),
        "passed": caught == 5 and not defects,
    }


def build_s8d_42kb_contradiction_fixture(root: Path) -> tuple[Path, Path, Path]:
    """Build a ~42 KB 3-file fixture (~24k+ ptok) with 6 dispersed contradictions across 180+ entries."""
    bom = root / "BOM.md"
    guide = root / "Assembly_Guide.md"
    cfg = root / "control.cfg"

    bom_rows = [
        "# Complete System BOM (`BOM.md`)",
        "",
        "| Subassembly | Part | Specification | Qty | Note |",
        "| :--- | :--- | :--- | :---: | :--- |",
    ]
    guide_lines = [
        "# Complete System Assembly Guide (`Assembly_Guide.md`)",
        "",
        "## Section 1 — Heavy Chassis & Brackets",
    ]
    cfg_lines = [
        "# Complete System Firmware Config (`control.cfg`)",
        "",
    ]

    for i in range(1, 185):
        bom_rows.append(
            f"| Stage_{i:03d} | Structural Standoff ST{i:03d} | `Spacer OD {6 + (i % 4)}mm ID 3.2mm L {8 + (i % 6)}mm Brass` | `{2 + (i % 3)}` | Bin {i % 9} |"
        )
        guide_lines.append(
            f"- Step {i:03d}: Seat `{2 + (i % 3)}` `Spacer OD {6 + (i % 4)}mm ID 3.2mm L {8 + (i % 6)}mm Brass` standoffs at Node {i:03d}."
        )
        cfg_lines.extend(
            [
                f"[stepper_aux_{i:03d}]",
                f"step_pin: PF{i % 16}",
                f"dir_pin: PE{i % 16}",
                f"microsteps: {16 if i % 2 == 0 else 32}",
                f"run_current: {0.60 + 0.05 * (i % 5):.2f}",
                "",
            ]
        )

    bom_rows.insert(24, "| Gantry | Y Carriage Fastener | `M4x18mm SHCS` | `6` | Primary rail |")
    guide_lines.insert(29, "- Fasten Y carriage blocks using `6` `M4x22mm SHCS` screws.")

    bom_rows.insert(88, "| Chamber | Silicone Heater Pad | `120 V 750 W AC Pad` | `1` | SSR switched |")
    guide_lines.insert(94, "- Adhere the `240 V 750 W AC Pad` beneath the cast plate.")

    bom_rows.insert(145, "| Extruder | TMC2209 Run Current | `0.85 A RMS` | `1` | LDO-36STH20 |")
    cfg_lines.insert(160, "# Extruder driver\n[tmc2209 extruder]\nrun_current: 1.25\nsense_resistor: 0.110\n")

    bom_rows.append("| Toolhead | thermistor Pullup | `4.7 kOhm Reference` | `1` | PT1000 header |")
    cfg_lines.append("[extruder]\npullup_resistor: 2200\nsensor_type: PT1000\n")

    bom_rows.append("| PSU | Logic Supply Bus | `5 V 3 A Buck` | `1` | Aux rail |")
    guide_lines.append("- Tap the `12 V 3 A Buck` logic module for controller power.")

    bom_rows.append("| Exhaust | Activated Carbon Cartridge | `120mm x 120mm` | `2` | Rear filter |")
    guide_lines.append("- Slide `4` `120mm x 120mm` Activated Carbon Cartridges into the rear bay.")

    bom.write_text("\n".join(bom_rows) + "\n", encoding="utf-8")
    guide.write_text("\n".join(guide_lines) + "\n", encoding="utf-8")
    cfg.write_text("\n".join(cfg_lines) + "\n", encoding="utf-8")
    return bom, guide, cfg


def score_s8d_output(text: str, sources: list[Path]) -> dict[str, Any]:
    low = text.lower()
    c_bolt = "m4x18mm" in low and "m4x22mm" in low
    c_heater = ("120 v" in low and "240 v" in low) and ("750" in low or "heater" in low or "pad" in low)
    c_curr = ("0.85" in low and "1.25" in low) and ("extruder" in low or "current" in low or "tmc2209" in low)
    c_pullup = ("4.7" in low and "2200" in low) or ("4700" in low and "2200" in low)
    c_buck = ("5 v" in low and "12 v" in low) and ("buck" in low or "logic" in low or "supply" in low)
    c_carbon = ("2" in low and "4" in low) and ("carbon" in low or "cartridge" in low or "120mm" in low)
    defects = apprentice_mcp_server._detect_citation_format_defects(text, sources)
    caught = int(c_bolt) + int(c_heater) + int(c_curr) + int(c_pullup) + int(c_buck) + int(c_carbon)
    return {
        "contradictions_caught": caught,
        "contradictions_total": 6,
        "recall_pct": round(100.0 * caught / 6.0, 1),
        "details": {
            "bolt_18_vs_22": c_bolt,
            "heater_120v_vs_240v": c_heater,
            "extruder_085_vs_125": c_curr,
            "pullup_4700_vs_2200": c_pullup,
            "buck_5v_vs_12v": c_buck,
            "carbon_qty_2_vs_4": c_carbon,
        },
        "citation_defects": len(defects),
        "passed": caught == 6 and not defects,
    }


def build_s8e_semantic_logic_fixture(root: Path) -> tuple[Path, Path, Path]:
    """Build a compact ~10 KB 3-file fixture with 4 non-trivial semantic / polarity / implicit-math contradictions."""
    standards = root / "Material_Rules.md"
    guide = root / "Assembly_Guide.md"
    cfg = root / "control.cfg"

    standards.write_text(
        """# Engineering Standards & Material Rules (`Material_Rules.md`)

> [!CAUTION]
> **Thermoplastic Fastener Lock Rule**: NEVER apply `Loctite 243` (or any anaerobic threadlocker) onto fasteners threaded into `ABS`, `ASA`, or `Polycarbonate` printed housings — anaerobic liquid crazes and fractures thermoplastics within hours.

## Wiring & Thermal Rules
1. Any heated enclosure fan sharing the controller `FAN1` MOSFET (`max 0.5 A` continuous) MUST stay below `0.40 A` continuous load with a `20%` derating margin.
2. Z-axis leadscrew backlash compensation must NOT exceed `0.08 mm` in active firmware configs to avoid Z-banding artifacts.
3. Silicone elastomer (`TPU 95A`) compliance bumpers MUST be installed dry without petroleum grease (mineral oil swells silicone-ester compounds).
""",
        encoding="utf-8",
    )
    guide.write_text(
        """# Build Instructions (`Assembly_Guide.md`)

## Step 1 — Printed Enclosure & Hardware
1. Mount the `ABS` main electronics shroud using `4` `M3x8mm SHCS` screws, applying one drop of `Loctite 243` on each screw thread before seating into the printed bosses.
2. Pack `3` `M3x8mm SHCS` + brass inserts for the toolhead door (`Polycarbonate` housing) dry with zero liquid threadlocker.

## Step 2 — Cooling & Bumpers
1. Wire the dual parallel `24 V 0.25 A` chamber fans (`0.50 A` combined draw) onto output pin `PA3`.
2. Coat the `TPU 95A` compliance bumpers lightly with `White Petroleum Grease` before sliding them into the tensioner slots.
""",
        encoding="utf-8",
    )
    cfg.write_text(
        """# Printer Controller Configuration (`control.cfg`)

[heater_fan chamber_circ]
# Bound to MOSFET header FAN1
pin: PA3
max_power: 1.0

[firmware_retraction]
retract_length: 0.6

[z_thermal_adjust]
temp_coeff: 0.0
# Anti-backlash compensation in mm:
z_backlash_comp: 0.15
""",
        encoding="utf-8",
    )
    return standards, guide, cfg


def score_s8e_output(text: str, sources: list[Path]) -> dict[str, Any]:
    low = text.lower()
    t_loctite = ("loctite" in low or "threadlocker" in low) and "abs" in low
    t_fan_amp = ("0.5" in low or "0.4" in low or "0.25" in low) and ("pa3" in low or "fan1" in low or "fan" in low)
    t_backlash = ("0.08" in low and "0.15" in low) or ("backlash" in low and "0.15" in low)
    t_grease = ("tpu" in low or "grease" in low or "petroleum" in low) and ("dry" in low or "swell" in low or "without" in low or "never" in low or "conflict" in low or "violat" in low or "mismatch" in low)
    defects = apprentice_mcp_server._detect_citation_format_defects(text, sources)
    caught = int(t_loctite) + int(t_fan_amp) + int(t_backlash) + int(t_grease)
    return {
        "contradictions_caught": caught,
        "contradictions_total": 4,
        "recall_pct": round(100.0 * caught / 4.0, 1),
        "details": {
            "loctite_on_abs_caution": t_loctite,
            "dual_fan_050a_exceeds_040a_derating": t_fan_amp,
            "z_backlash_015_exceeds_008": t_backlash,
            "tpu_petroleum_grease_prohibition": t_grease,
        },
        "citation_defects": len(defects),
        "passed": caught == 4 and not defects,
    }


# ---------------------------------------------------------------------------
# Live STANDARD Vector Executor
# ---------------------------------------------------------------------------


def execute_live_standard_vectors(selected: list[str]) -> dict[str, Any]:
    api_url = apprentice_engine.validate_loopback_url(apprentice_engine.resolve_default_api_url())
    srv = apprentice_engine.probe_server_models(api_url, model_id=apprentice_engine.DEFAULT_MODEL_ID, timeout_s=3.0)
    if not srv["reachable"] or not srv["target_model_loaded"]:
        raise RuntimeError(
            f"[BIONIC_NOT_READY] Live STANDARD ladder requires ONLINE_READY Bionic at {api_url}; "
            f"reachable={srv['reachable']}, loaded={srv['target_model_loaded']} ({srv.get('error')})"
        )

    hom_root, mem_root = apprentice_mcp_server._resolve_homunculus_and_memory()
    verify_claims_path = hom_root / "skills" / "claim-verification" / "scripts" / "verify_claims.py"
    sys_prompt, _ = apprentice_engine.load_system_prompt()
    loaded_ctx = srv.get("loaded_context_length")

    results: list[dict[str, Any]] = []

    with tempfile.TemporaryDirectory(prefix="apprentice_std_ladder_") as td:
        td_p = Path(td)

        if "S1" in selected:
            d1 = td_p / "s1"
            d1.mkdir()
            log_p, planted = build_s1_log_fixture(d1)
            r1 = apprentice_mcp_server.apprentice_digest(
                prompt=(
                    "Extract ONLY the failing/error/unbacked lines from sandbox_run.log as terse `- ` bullets "
                    "citing exact `sandbox_run.log#Lstart-Lend` anchors and verbatim failure tokens. "
                    "Ignore all `[PASS]` lines. Zero preamble."
                ),
                context_files=[str(log_p)],
                repo=str(d1),
                effort="standard",
                invocation_tier="explicit",
                verify_claims=True,
            )
            txt1 = str((r1.get("completion") or {}).get("content") or "")
            sc1 = score_s1_output(txt1, planted, log_p)
            results.append(
                {
                    "id": "S1",
                    "name": "Log Coordinate Sieve (>=10 KB)",
                    "ok": r1.get("ok"),
                    "verdict": r1.get("verdict"),
                    "first_pass_clean": r1.get("verdict") == "clean",
                    "claims_verified": r1.get("claims_verified"),
                    "elapsed_s": (r1.get("completion") or {}).get("elapsed_s"),
                    "heal_elapsed_s": r1.get("heal_elapsed_s"),
                    "prompt_tokens": (r1.get("completion") or {}).get("prompt_tokens"),
                    "completion_tokens": (r1.get("completion") or {}).get("completion_tokens"),
                    "score": sc1,
                    "passed": bool(r1.get("ok") and r1.get("verdict") in {"clean", "healed"} and sc1["passed"]),
                    "draft_preview": txt1[:900],
                }
            )

        if "S2" in selected:
            d2 = td_p / "s2"
            d2.mkdir()
            wl_p = build_s2_worklog_fixture(d2)
            r2 = apprentice_mcp_server.apprentice_digest(
                prompt=(
                    "Harvest ONLY the UNRECORDED engineering findings in v0.9_Subsystem_Worklog.md that do NOT "
                    "already have a `*(Recorded as LL-...)*` marker. Emit terse `- ` bullets with exact "
                    "`v0.9_Subsystem_Worklog.md#Lstart-Lend` anchors (never cite YAML frontmatter). Zero preamble."
                ),
                context_files=[str(wl_p)],
                repo=str(d2),
                effort="standard",
                invocation_tier="explicit",
                verify_claims=True,
            )
            txt2 = str((r2.get("completion") or {}).get("content") or "")
            sc2 = score_s2_output(txt2, wl_p)
            results.append(
                {
                    "id": "S2",
                    "name": "Version_Logs Unharvested Archetype Sieve",
                    "ok": r2.get("ok"),
                    "verdict": r2.get("verdict"),
                    "first_pass_clean": r2.get("verdict") == "clean",
                    "claims_verified": r2.get("claims_verified"),
                    "elapsed_s": (r2.get("completion") or {}).get("elapsed_s"),
                    "heal_elapsed_s": r2.get("heal_elapsed_s"),
                    "prompt_tokens": (r2.get("completion") or {}).get("prompt_tokens"),
                    "completion_tokens": (r2.get("completion") or {}).get("completion_tokens"),
                    "score": sc2,
                    "passed": bool(r2.get("ok") and r2.get("verdict") in {"clean", "healed"} and sc2["passed"]),
                    "draft_preview": txt2[:900],
                }
            )

        if "S3" in selected:
            d3 = td_p / "s3"
            d3.mkdir()
            bom3, guide3 = build_s3_bom_caution_fixture(d3)
            r3 = apprentice_mcp_server.apprentice_digest(
                prompt=(
                    "Summarize all BOM rows (preserving exact qualifiers like `~2 m`, `(4)`, `[TBD: ...]`, and exact "
                    "fastener acronyms without expansion) plus any `[!CAUTION]` hazard in Assembly_Guide.md. "
                    "Cite separate `BOM.md#Lstart-Lend` and `Assembly_Guide.md#Lstart-Lend` anchors. Zero preamble."
                ),
                context_files=["BOM.md", "Assembly_Guide.md"],
                repo=str(d3),
                effort="standard",
                invocation_tier="explicit",
                verify_claims=True,
            )
            txt3 = str((r3.get("completion") or {}).get("content") or "")
            sc3 = score_s3_output(txt3, [bom3, guide3])
            results.append(
                {
                    "id": "S3",
                    "name": "Qualified Quantities, [TBD], & [!CAUTION] Polarity",
                    "ok": r3.get("ok"),
                    "verdict": r3.get("verdict"),
                    "first_pass_clean": r3.get("verdict") == "clean",
                    "claims_verified": r3.get("claims_verified"),
                    "elapsed_s": (r3.get("completion") or {}).get("elapsed_s"),
                    "heal_elapsed_s": r3.get("heal_elapsed_s"),
                    "prompt_tokens": (r3.get("completion") or {}).get("prompt_tokens"),
                    "completion_tokens": (r3.get("completion") or {}).get("completion_tokens"),
                    "score": sc3,
                    "passed": bool(r3.get("ok") and r3.get("verdict") in {"clean", "healed"} and sc3["passed"]),
                    "draft_preview": txt3[:900],
                }
            )

        if "S4" in selected:
            d4 = td_p / "s4"
            d4.mkdir()
            specs4, files4, exp4 = build_s4_multislice_fixture(d4)
            r4 = apprentice_mcp_server.apprentice_digest(
                prompt=(
                    "Extract every active non-comment configuration parameter and value across all 6 slices as "
                    "terse `- ` bullets with exact `<file>#L<start>-L<end>` anchors. Zero preamble."
                ),
                context_files=specs4,
                repo=str(d4),
                effort="standard",
                invocation_tier="explicit",
                verify_claims=True,
            )
            txt4 = str((r4.get("completion") or {}).get("content") or "")
            sc4 = score_s4_output(txt4, files4, exp4)
            results.append(
                {
                    "id": "S4",
                    "name": "6-Slice Multi-File Mapper Recall (STANDARD Map-Reduce)",
                    "ok": r4.get("ok"),
                    "verdict": r4.get("verdict"),
                    "first_pass_clean": r4.get("verdict") == "clean",
                    "chunked_map_reduce": r4.get("chunked_map_reduce"),
                    "claims_verified": r4.get("claims_verified"),
                    "elapsed_s": (r4.get("completion") or {}).get("elapsed_s"),
                    "heal_elapsed_s": r4.get("heal_elapsed_s"),
                    "prompt_tokens": (r4.get("completion") or {}).get("prompt_tokens"),
                    "completion_tokens": (r4.get("completion") or {}).get("completion_tokens"),
                    "score": sc4,
                    "passed": bool(r4.get("ok") and r4.get("verdict") in {"clean", "healed"} and sc4["passed"]),
                    "draft_preview": txt4[:900],
                }
            )

        if "S5" in selected:
            stg5 = td_p / "staging_s5"
            stg5.mkdir(mode=0o700)
            r5 = apprentice_mcp_server.apprentice_stage_patch(
                target_filename="pin_parser.py",
                prompt=(
                    "Write a pure-stdlib Python 3.10+ module defining `parse_pin_table(md_text: str) -> list[dict[str, object]]`.\n"
                    "Specification:\n"
                    "1. Parse Markdown pipe tables whose header row is `| Signal | Pin | Pull |` (skipping non-table text, header row, and `| --- |` separator rows).\n"
                    "2. Strip backticks and any trailing `# ...` inline comment inside cells.\n"
                    "3. In the `Pin` cell, parse optional prefix modifiers in any order before the pin name (e.g. `!^PB4`, `^!PC13`, `~PD2`, `PA1`):\n"
                    "   - `!` sets `'inverted': True` (default `False`)\n"
                    "   - `^` sets `'pullup': True` (default `False`)\n"
                    "   - `~` sets `'pulldown': True` (default `False`)\n"
                    "   - Raise `ValueError` if both `^` and `~` are present on the same pin.\n"
                    "4. Track physical stripped pin names (case-insensitive) across the table and raise `ValueError` on duplicate physical pins (e.g. `PA1` and `!PA1`).\n"
                    "5. Return a list of dicts in row order: `{'signal': <str>, 'pin': <stripped_pin_str>, 'inverted': <bool>, 'pullup': <bool>, 'pulldown': <bool>}`.\n"
                    "6. Include an `if __name__ == '__main__':` `--self-test` CLI block."
                ),
                staging_dir=str(stg5),
                effort="standard",
                invocation_tier="explicit",
                max_tokens=2048,
            )
            ext5 = run_s5_external_oracle(Path(r5["staged_file"])) if r5.get("staged_file") else {"passed": False, "cases_passed": 0, "cases_total": 10}
            code5 = Path(r5["staged_file"]).read_text(encoding="utf-8", errors="replace") if r5.get("staged_file") and Path(r5["staged_file"]).is_file() else ""
            results.append(
                {
                    "id": "S5",
                    "name": "Pure-Stdlib stage_patch vs 10-Case External Oracle",
                    "ok": r5.get("ok"),
                    "verdict": r5.get("verdict"),
                    "attempts": r5.get("attempts"),
                    "first_pass_clean": r5.get("verdict") == "clean" and r5.get("attempts") == 1,
                    "smoke_test": r5.get("smoke_test"),
                    "elapsed_s": r5.get("elapsed_s"),
                    "heal_elapsed_s": r5.get("heal_elapsed_s"),
                    "external_oracle": ext5,
                    "passed": bool(r5.get("ok") and ext5.get("passed")),
                    "staged_code": code5[:3500],
                }
            )

        if "S5B" in selected:
            stg5b = td_p / "staging_s5b"
            stg5b.mkdir(mode=0o700)
            r5b = apprentice_mcp_server.apprentice_stage_patch(
                target_filename="pin_parser.py",
                prompt=(
                    "Write a pure-stdlib Python 3.10+ module defining `parse_pin_table(md_text: str) -> list[dict[str, object]]`.\n"
                    "Specification:\n"
                    "1. Parse Markdown pipe tables whose header row has columns `| Signal | Pin | Pull |` (skipping non-table prose, header row, and alignment/separator rows such as `| --- | --- | --- |`, `| :--- | :--- | :---: |`, or `|---|---|---|`).\n"
                    "2. Strip backticks and any trailing `# ...` inline comment inside cells.\n"
                    "3. In the `Pin` cell, parse optional prefix modifiers in any order before the pin name (e.g. `!^PB4`, `^!PC13`, `~PD2`, `PA1`):\n"
                    "   - `!` sets `'inverted': True` (default `False`)\n"
                    "   - `^` sets `'pullup': True` (default `False`)\n"
                    "   - `~` sets `'pulldown': True` (default `False`)\n"
                    "   - Raise `ValueError` if both `^` and `~` are present on the same pin.\n"
                    "4. Track physical stripped pin names (case-insensitive) across the table and raise `ValueError` on duplicate physical pins (e.g. `PA1` and `!PA1`).\n"
                    "5. Return a list of dicts in row order: `{'signal': <str>, 'pin': <stripped_pin_str>, 'inverted': <bool>, 'pullup': <bool>, 'pulldown': <bool>}`.\n"
                    "6. Include an `if __name__ == '__main__':` `--self-test` CLI block."
                ),
                staging_dir=str(stg5b),
                effort="standard",
                invocation_tier="explicit",
                max_tokens=2048,
            )
            ext5b = run_s5_external_oracle(Path(r5b["staged_file"])) if r5b.get("staged_file") else {"passed": False, "cases_passed": 0, "cases_total": 10}
            code5b = Path(r5b["staged_file"]).read_text(encoding="utf-8", errors="replace") if r5b.get("staged_file") and Path(r5b["staged_file"]).is_file() else ""
            results.append(
                {
                    "id": "S5B",
                    "name": "Pure-Stdlib stage_patch w/ Explicit Alignment Spec",
                    "ok": r5b.get("ok"),
                    "verdict": r5b.get("verdict"),
                    "attempts": r5b.get("attempts"),
                    "first_pass_clean": r5b.get("verdict") == "clean" and r5b.get("attempts") == 1,
                    "smoke_test": r5b.get("smoke_test"),
                    "elapsed_s": r5b.get("elapsed_s"),
                    "heal_elapsed_s": r5b.get("heal_elapsed_s"),
                    "external_oracle": ext5b,
                    "passed": bool(r5b.get("ok") and ext5b.get("passed")),
                    "staged_code": code5b[:3500],
                }
            )

        if "S6" in selected:
            d6 = td_p / "s6_repo"
            d6.mkdir()
            api6 = build_s6_repo_api_fixture(d6)
            stg6 = td_p / "staging_s6"
            stg6.mkdir(mode=0o700)
            r6 = apprentice_mcp_server.apprentice_stage_patch(
                target_filename="test_telemetry_window_fixture.py",
                prompt=(
                    "Write a Python 3.10+ verification script importing `evaluate_sensor_window` directly from "
                    "`telemetry_window` (do NOT use `unittest.mock` or `sys.modules` stubs). "
                    "Under `if __name__ == '__main__':` (supporting `--self-test`), assert:\n"
                    "1) empty sample list returns `status == 'EMPTY'` and `mean is None`,\n"
                    "2) `[10.0, 12.0, 15.0]` with exact keyword arguments `low_limit=9.0, high_limit=16.0` returns `status == 'PASS'` and `spikes == 0`,\n"
                    "3) `[8.0, 12.0, 19.0]` with `low_limit=9.0, high_limit=16.0, max_spike_count=1` returns `status == 'TRIPPED'` and `spikes == 2`,\n"
                    "4) `low_limit >= high_limit` raises `ValueError`."
                ),
                context_files=[f"{api6}#L1-L30"],
                repo=str(d6),
                staging_dir=str(stg6),
                effort="standard",
                invocation_tier="explicit",
                max_tokens=1600,
            )
            sc6 = score_s6_staged_harness(Path(r6["staged_file"]), d6) if r6.get("staged_file") else {"passed": False}
            results.append(
                {
                    "id": "S6",
                    "name": "#L-Contextualized Local API stage_patch (Zero Mock Spoof)",
                    "ok": r6.get("ok"),
                    "verdict": r6.get("verdict"),
                    "attempts": r6.get("attempts"),
                    "first_pass_clean": r6.get("verdict") == "clean" and r6.get("attempts") == 1,
                    "smoke_test": r6.get("smoke_test"),
                    "elapsed_s": r6.get("elapsed_s"),
                    "heal_elapsed_s": r6.get("heal_elapsed_s"),
                    "external_oracle": sc6,
                    "passed": bool(r6.get("ok") and sc6.get("passed")),
                }
            )

        if "S7" in selected:
            d7 = td_p / "s7"
            d7.mkdir()
            bom7, guide7, bad_draft7, must_keep7 = build_s7_corrupted_draft_fixture(d7)
            clean_srcs7 = [bom7, guide7]
            vrf_init7 = apprentice_mcp_server._run_verify_claims_check(
                bad_draft7,
                clean_srcs7,
                verify_claims_path,
                mem_root,
                d7,
            )
            t7_0 = time.perf_counter()
            eta_dummy7 = {"effort": "standard", "predicted_eta_s": 8.0}
            surg7 = apprentice_mcp_server._surgical_repair_unbacked_lines(
                draft_text=bad_draft7,
                vrf_res=vrf_init7,
                context_sources=clean_srcs7,
                clean_sources=clean_srcs7,
                repo_resolved=d7,
                verify_claims_path=verify_claims_path,
                mem_root=mem_root,
                cwd_check=d7,
                api_url=api_url,
                sys_prompt=sys_prompt,
                loaded_ctx=loaded_ctx,
                tier="explicit",
                eta=eta_dummy7,
                cmd_name_prefix="apprentice_digest",
            )
            repaired_txt7 = bad_draft7
            vrf_after7 = vrf_init7
            used_full_fallback7 = False
            if surg7 is not None and surg7.get("verified"):
                repaired_txt7 = surg7["content"]
                vrf_after7 = surg7["vrf_after"]
            else:
                used_full_fallback7 = True
                cur_draft7 = surg7["content"] if (surg7 and int(surg7["vrf_after"].get("unbacked", 99)) < int(vrf_init7.get("unbacked", 99))) else bad_draft7
                cur_vrf7 = surg7["vrf_after"] if (surg7 and cur_draft7 != bad_draft7) else vrf_init7
                assembled7, _ = apprentice_engine.assemble_prompt_payload(
                    user_prompt="Summarize BOM and Assembly Guide facts accurately.",
                    context_files=clean_srcs7,
                    repo_root=d7,
                    include_git_diff=False,
                    sys_prompt=sys_prompt,
                )
                fail_det7 = apprentice_mcp_server._format_compact_verify_failures(cur_vrf7, max_chars=2800)
                rep_p7 = (
                    f"{assembled7}\n\nYour previous draft failed deterministic claim verification:\n{fail_det7}\n"
                    "CRITICAL REPAIR RULES:\n"
                    "1. Keep ALL valid source-backed bullets intact while fixing ONLY the defective citations/quantities/qualifiers.\n"
                    "2. Never concatenate `#file1#L1#file2#L2` or `[file:L1]`; write separate `file.md#Lstart-Lend` anchors within line bounds.\n"
                    "3. Preserve exact qualifiers (`~2 m`), explicit `Caution:` / `NEVER` hazard polarity, and pure numeric `[CALC: 4 + 2 = 6]`.\n\n"
                    f"Previous draft:\n{cur_draft7}\n"
                )
                rep_out7 = apprentice_mcp_server._run_full_repair_with_guard(
                    repair_prompt=rep_p7,
                    draft_for_heal=cur_draft7,
                    vrf_for_heal=cur_vrf7,
                    base_res={"content": cur_draft7, "prompt_tokens": 0, "completion_tokens": 0, "finish_reason": "stop"},
                    effective_mode="fast",
                    effort_norm="standard",
                    max_budget=3072,
                    api_url=api_url,
                    sys_prompt=sys_prompt,
                    loaded_ctx=loaded_ctx,
                    clean_sources=clean_srcs7,
                    verify_claims_path=verify_claims_path,
                    mem_root=mem_root,
                    cwd_check=d7,
                    tier="explicit",
                    eta=eta_dummy7,
                    telemetry_cmd="apprentice_digest_verify_retry",
                )
                repaired_txt7 = rep_out7["content"]
                vrf_after7 = rep_out7["vrf_after"]

            dt7 = round(time.perf_counter() - t7_0, 3)
            sc7 = score_s7_repaired_draft(repaired_txt7, vrf_after7, must_keep7)
            results.append(
                {
                    "id": "S7",
                    "name": "STANDARD Repair Engine (Fix 4 Defects + Retain 5/5 Valid Bullets)",
                    "initial_unbacked": vrf_init7.get("unbacked"),
                    "surgical_verified_alone": bool(surg7 and surg7.get("verified")),
                    "used_full_fallback": used_full_fallback7,
                    "elapsed_s": dt7,
                    "score": sc7,
                    "passed": sc7["passed"],
                    "draft_preview": repaired_txt7[:900],
                }
            )

        if "S8" in selected:
            d8 = td_p / "s8"
            d8.mkdir()
            bom8, guide8 = build_s8_contradiction_fixture(d8)
            r8 = apprentice_mcp_server.apprentice_digest(
                prompt=(
                    "Compare BOM.md and Assembly_Guide.md line-by-line and list ONLY genuine specification or "
                    "quantity contradictions between the two files. Cite separate `BOM.md#Lstart-Lend` and "
                    "`Assembly_Guide.md#Lstart-Lend` anchors verbatim on each bullet. Ignore matching items. Zero preamble."
                ),
                context_files=["BOM.md", "Assembly_Guide.md"],
                repo=str(d8),
                effort="standard",
                invocation_tier="explicit",
                verify_claims=True,
            )
            txt8 = str((r8.get("completion") or {}).get("content") or "")
            sc8 = score_s8_output(txt8, [bom8, guide8])
            results.append(
                {
                    "id": "S8",
                    "name": "Forced STANDARD <8 KB 2-File Contradiction Ceiling Probe",
                    "ok": r8.get("ok"),
                    "route_id": r8.get("route_id"),
                    "verdict": r8.get("verdict"),
                    "first_pass_clean": r8.get("verdict") == "clean",
                    "claims_verified": r8.get("claims_verified"),
                    "elapsed_s": (r8.get("completion") or {}).get("elapsed_s"),
                    "heal_elapsed_s": r8.get("heal_elapsed_s"),
                    "prompt_tokens": (r8.get("completion") or {}).get("prompt_tokens"),
                    "completion_tokens": (r8.get("completion") or {}).get("completion_tokens"),
                    "score": sc8,
                    "passed": bool(r8.get("ok") and r8.get("verdict") in {"clean", "healed"} and sc8["passed"]),
                    "draft_preview": txt8[:900],
                }
            )

        if "S8B" in selected:
            d8b = td_p / "s8b"
            d8b.mkdir()
            bom8b, guide8b = build_s8b_mid_contradiction_fixture(d8b)
            r8b = apprentice_mcp_server.apprentice_digest(
                prompt=(
                    "Compare BOM.md and Assembly_Guide.md line-by-line and list ONLY genuine specification or "
                    "quantity contradictions between the two files. Include part names + conflicting numbers + "
                    "separate `BOM.md#Lstart-Lend` and `Assembly_Guide.md#Lstart-Lend` anchors on each bullet. Zero preamble."
                ),
                context_files=["BOM.md", "Assembly_Guide.md"],
                repo=str(d8b),
                effort="standard",
                invocation_tier="explicit",
                verify_claims=True,
            )
            txt8b = str((r8b.get("completion") or {}).get("content") or "")
            sc8b = score_s8b_output(txt8b, [bom8b, guide8b])
            results.append(
                {
                    "id": "S8B",
                    "name": "Forced STANDARD ~14 KB Multi-Section 2-File Contradiction Probe",
                    "ok": r8b.get("ok"),
                    "route_id": r8b.get("route_id"),
                    "verdict": r8b.get("verdict"),
                    "first_pass_clean": r8b.get("verdict") == "clean",
                    "claims_verified": r8b.get("claims_verified"),
                    "elapsed_s": (r8b.get("completion") or {}).get("elapsed_s"),
                    "heal_elapsed_s": r8b.get("heal_elapsed_s"),
                    "prompt_tokens": (r8b.get("completion") or {}).get("prompt_tokens"),
                    "completion_tokens": (r8b.get("completion") or {}).get("completion_tokens"),
                    "score": sc8b,
                    "passed": bool(r8b.get("ok") and r8b.get("verdict") in {"clean", "healed"} and sc8b["passed"]),
                    "draft_preview": txt8b[:1100],
                }
            )

        if "S8C" in selected:
            d8c = td_p / "s8c"
            d8c.mkdir()
            bom8c, guide8c, cfg8c = build_s8c_large_3file_contradiction_fixture(d8c)
            raw_bytes_8c = bom8c.stat().st_size + guide8c.stat().st_size + cfg8c.stat().st_size
            r8c = apprentice_mcp_server.apprentice_digest(
                prompt=(
                    "Compare BOM.md, Assembly_Guide.md, and control.cfg across all sections and list ONLY genuine "
                    "contradictions (dimensions, temperatures, voltage rails, gear counts, shutdown_speed). Include exact "
                    "values and separate `<file>#L<start>-L<end>` anchors on every bullet. Zero preamble."
                ),
                context_files=["BOM.md", "Assembly_Guide.md", "control.cfg"],
                repo=str(d8c),
                effort="standard",
                invocation_tier="explicit",
                verify_claims=True,
            )
            txt8c = str((r8c.get("completion") or {}).get("content") or "")
            sc8c = score_s8c_output(txt8c, [bom8c, guide8c, cfg8c])
            results.append(
                {
                    "id": "S8C",
                    "name": f"Forced STANDARD ~{round(raw_bytes_8c / 1024.0, 1)} KB 3-File Cross-Domain Ceiling Probe",
                    "ok": r8c.get("ok"),
                    "raw_bytes": raw_bytes_8c,
                    "route_id": r8c.get("route_id"),
                    "verdict": r8c.get("verdict"),
                    "first_pass_clean": r8c.get("verdict") == "clean",
                    "claims_verified": r8c.get("claims_verified"),
                    "elapsed_s": (r8c.get("completion") or {}).get("elapsed_s"),
                    "heal_elapsed_s": r8c.get("heal_elapsed_s"),
                    "prompt_tokens": (r8c.get("completion") or {}).get("prompt_tokens"),
                    "completion_tokens": (r8c.get("completion") or {}).get("completion_tokens"),
                    "score": sc8c,
                    "passed": bool(r8c.get("ok") and r8c.get("verdict") in {"clean", "healed"} and sc8c["passed"]),
                    "draft_preview": txt8c[:1400],
                }
            )

        if "S8D" in selected:
            d8d = td_p / "s8d"
            d8d.mkdir()
            bom8d, guide8d, cfg8d = build_s8d_42kb_contradiction_fixture(d8d)
            raw_bytes_8d = bom8d.stat().st_size + guide8d.stat().st_size + cfg8d.stat().st_size
            r8d = apprentice_mcp_server.apprentice_digest(
                prompt=(
                    "Compare BOM.md, Assembly_Guide.md, and control.cfg across all sections and list ONLY genuine "
                    "contradictions (fasteners, voltages, currents, pullup resistors, quantities). Include exact values "
                    "and separate `<file>#L<start>-L<end>` anchors on every bullet. Zero preamble."
                ),
                context_files=["BOM.md", "Assembly_Guide.md", "control.cfg"],
                repo=str(d8d),
                effort="standard",
                invocation_tier="explicit",
                verify_claims=True,
            )
            txt8d = str((r8d.get("completion") or {}).get("content") or "")
            sc8d = score_s8d_output(txt8d, [bom8d, guide8d, cfg8d])
            results.append(
                {
                    "id": "S8D",
                    "name": f"Forced STANDARD ~{round(raw_bytes_8d / 1024.0, 1)} KB 3-File Cliff Probe",
                    "ok": r8d.get("ok"),
                    "raw_bytes": raw_bytes_8d,
                    "route_id": r8d.get("route_id"),
                    "verdict": r8d.get("verdict"),
                    "first_pass_clean": r8d.get("verdict") == "clean",
                    "claims_verified": r8d.get("claims_verified"),
                    "elapsed_s": (r8d.get("completion") or {}).get("elapsed_s"),
                    "heal_elapsed_s": r8d.get("heal_elapsed_s"),
                    "prompt_tokens": (r8d.get("completion") or {}).get("prompt_tokens"),
                    "completion_tokens": (r8d.get("completion") or {}).get("completion_tokens"),
                    "score": sc8d,
                    "passed": bool(r8d.get("ok") and r8d.get("verdict") in {"clean", "healed"} and sc8d["passed"]),
                    "draft_preview": txt8d[:1500],
                }
            )

        if "S8E" in selected:
            d8e = td_p / "s8e"
            d8e.mkdir()
            std8e, guide8e, cfg8e = build_s8e_semantic_logic_fixture(d8e)
            r8e = apprentice_mcp_server.apprentice_digest(
                prompt=(
                    "Audit Assembly_Guide.md and control.cfg against Material_Rules.md. Flag ONLY safety/caution "
                    "violations, summed current overruns, backlash ceiling breaches, or chemical incompatibilities with "
                    "separate `<file>#L<start>-L<end>` anchors. Zero preamble."
                ),
                context_files=["Material_Rules.md", "Assembly_Guide.md", "control.cfg"],
                repo=str(d8e),
                effort="standard",
                invocation_tier="explicit",
                verify_claims=True,
            )
            txt8e = str((r8e.get("completion") or {}).get("content") or "")
            sc8e = score_s8e_output(txt8e, [std8e, guide8e, cfg8e])
            results.append(
                {
                    "id": "S8E",
                    "name": "Forced STANDARD Cross-File Semantic/Polarity/Sum-Limit Traps",
                    "ok": r8e.get("ok"),
                    "route_id": r8e.get("route_id"),
                    "verdict": r8e.get("verdict"),
                    "first_pass_clean": r8e.get("verdict") == "clean",
                    "claims_verified": r8e.get("claims_verified"),
                    "elapsed_s": (r8e.get("completion") or {}).get("elapsed_s"),
                    "heal_elapsed_s": r8e.get("heal_elapsed_s"),
                    "prompt_tokens": (r8e.get("completion") or {}).get("prompt_tokens"),
                    "completion_tokens": (r8e.get("completion") or {}).get("completion_tokens"),
                    "score": sc8e,
                    "passed": bool(r8e.get("ok") and r8e.get("verdict") in {"clean", "healed"} and sc8e["passed"]),
                    "draft_preview": txt8e[:1500],
                }
            )

    passed_cnt = sum(1 for item in results if item.get("passed"))
    return {
        "schema_version": SCHEMA_VERSION,
        "timestamp_utc": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        "server_status": srv,
        "vectors_run": len(results),
        "vectors_passed": passed_cnt,
        "results": results,
    }


def render_ladder_markdown(report: dict[str, Any]) -> str:
    lines = [
        f"# Apprentice Phase-3 `STANDARD` Capability Ladder Report (`{report['timestamp_utc']}`)",
        "",
        f"- **Model / Context**: `{report['server_status'].get('loaded_models')}` (ctx=`{report['server_status'].get('loaded_context_length')}`)",
        f"- **Vectors Passed**: **`{report['vectors_passed']} / {report['vectors_run']}`**",
        "",
        "| Vector | Verdict | 1st-Pass Clean | Latency | Result | Diagnostic Summary |",
        "| :--- | :---: | :---: | :---: | :---: | :--- |",
    ]
    for r in report["results"]:
        vid = r["id"]
        verd = r.get("verdict") or ("surgical" if r.get("surgical_verified_alone") else "full_repair")
        fpc = "YES" if r.get("first_pass_clean") else "—"
        el = f"{r.get('elapsed_s')}s"
        res_str = "PASS" if r.get("passed") else "FAIL"
        sc = r.get("score") or r.get("external_oracle") or {}
        lines.append(f"| **{vid}** — {r['name']} | `{verd}` | `{fpc}` | `{el}` | **{res_str}** | `{json.dumps(sc)[:180]}` |")
    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------
# Offline Deterministic Self-Tests (Fixtures + Positive & Negative Scorers)
# ---------------------------------------------------------------------------


def run_self_tests() -> dict[str, Any]:
    snap_before = benchmark_apprentice._snapshot_live_prod_files()
    checks: list[str] = []

    with tempfile.TemporaryDirectory(prefix="std_ladder_selftest_") as td:
        td_p = Path(td)
        with benchmark_apprentice._isolated_bench_env(td_p / "bench" / "tel.jsonl"):
            # S1 positive & negative scorer checks
            log_p, planted1 = build_s1_log_fixture(td_p)
            assert log_p.stat().st_size >= 10000, f"S1 log < 10KB: {log_p.stat().st_size}"
            good_s1 = (
                "- `EROFS_BLOCKED_WRITE` on `/etc/shadow_probe` (`sandbox_run.log#L47`)\n"
                "- `AssertionError` gantry homing expected `1600` observed `800` (`sandbox_run.log#L128`)\n"
                "- `TimeoutExpired` after `15.0` seconds (`sandbox_run.log#L219`)\n"
                "- `[UNBACKED_CLAIM]` peak current `14.5 A` (`sandbox_run.log#L294`)\n"
            )
            assert score_s1_output(good_s1, planted1, log_p)["passed"] is True
            assert score_s1_output("- EROFS_BLOCKED_WRITE (`sandbox_run.log#L47`)\n", planted1, log_p)["passed"] is False
            checks.append("s1_log_fixture_and_scorer")

            # S2 positive & negative checks
            wl_p = build_s2_worklog_fixture(td_p)
            good_s2 = (
                "- Inductive probe `24 V` back-feed to `PA8` without `BAT85` diode (`v0.9_Subsystem_Worklog.md#L25-L26`)\n"
                "- `32` microsteps `interpolate: False` eliminating `0.04 mm` lag (`v0.9_Subsystem_Worklog.md#L27-L28`)\n"
            )
            assert score_s2_output(good_s2, wl_p)["passed"] is True
            assert score_s2_output(good_s2 + "- CRC32 framing (`v0.9_Subsystem_Worklog.md#L15`)\n", wl_p)["passed"] is False
            assert score_s2_output("- Frontmatter (`v0.9_Subsystem_Worklog.md#L3`)\n" + good_s2, wl_p)["passed"] is False
            checks.append("s2_worklog_fixture_and_scorer")

            # S3 positive & negative checks
            bom3, guide3 = build_s3_bom_caution_fixture(td_p)
            good_s3 = (
                "- Carriage Mount Screw: `(4)` `M3x8mm SHCS` (`BOM.md#L5`)\n"
                "- Rear Cover Screw: `[TBD: rear_cover_m3_count]` `M3 BHCS` (`BOM.md#L6`)\n"
                "- Feed Tube: `~2 m` `4mm OD x 2.5mm ID PTFE` (`BOM.md#L7`)\n"
                "- Caution: NEVER wire `24 V` directly to `PB6` without `BAT85` diode (`Assembly_Guide.md#L8-L9`)\n"
            )
            assert score_s3_output(good_s3, [bom3, guide3])["passed"] is True
            assert score_s3_output(good_s3.replace("~2 m", "2 m"), [bom3, guide3])["passed"] is False
            assert score_s3_output(good_s3.replace("SHCS", "SHCS (Socket Head Cap Screw)"), [bom3, guide3])["passed"] is False
            checks.append("s3_qualified_bom_caution_scorer")

            # S4 positive & negative checks
            specs4, files4, exp4 = build_s4_multislice_fixture(td_p)
            assert len(specs4) == 6
            good_s4 = (
                "- `stm32h723xx_29001A` (`mcu.cfg#L10`)\n"
                "- `9f8e7d6c5b4a` (`mcu.cfg#L75`)\n"
                "- `315` (`thermals.cfg#L15`)\n"
                "- `72` (`thermals.cfg#L69`)\n"
                "- `550` (`motion.cfg#L20`)\n"
                "- `350` (`motion.cfg#L72`)\n"
            )
            assert score_s4_output(good_s4, files4, exp4)["passed"] is True
            assert score_s4_output("- `315` (`thermals.cfg#L15`)\n", files4, exp4)["passed"] is False
            checks.append("s4_multislice_mapper_scorer")

            # S5 10-case external oracle positive & negative checks
            ref_pin_py = td_p / "ref_pin_parser.py"
            ref_pin_py.write_text(
                '''def parse_pin_table(md_text: str) -> list[dict[str, object]]:
    out = []
    seen = set()
    for raw in md_text.splitlines():
        s = raw.strip()
        if not (s.startswith("|") and s.endswith("|")):
            continue
        cells = [c.strip().strip("`").split("#", 1)[0].strip() for c in s.strip("|").split("|")]
        if len(cells) < 3:
            continue
        if cells[0].lower() == "signal" or all(set(c) <= {"-", ":", " "} for c in cells):
            continue
        sig, raw_pin, _pull = cells[0], cells[1], cells[2]
        inv = False
        pu = False
        pd = False
        idx = 0
        while idx < len(raw_pin) and raw_pin[idx] in "!^~":
            ch = raw_pin[idx]
            if ch == "!":
                inv = True
            elif ch == "^":
                pu = True
            elif ch == "~":
                pd = True
            idx += 1
        if pu and pd:
            raise ValueError("Conflicting pullup and pulldown")
        pin = raw_pin[idx:].strip()
        if not pin or pin.upper() in seen:
            raise ValueError(f"Invalid or duplicate pin: {pin}")
        seen.add(pin.upper())
        out.append({"signal": sig, "pin": pin, "inverted": inv, "pullup": pu, "pulldown": pd})
    return out
''',
                encoding="utf-8",
            )
            s5_good = run_s5_external_oracle(ref_pin_py)
            assert s5_good["passed"] is True and s5_good["cases_passed"] == 10, s5_good
            bad_pin_py = td_p / "bad_pin_parser.py"
            bad_pin_py.write_text("def parse_pin_table(md_text: str):\n    return []\n", encoding="utf-8")
            assert run_s5_external_oracle(bad_pin_py)["passed"] is False
            checks.append("s5_external_10_case_oracle")

            # S6 contextualized repo fixture check (catches unittest.mock spoofing)
            d6 = td_p / "s6"
            d6.mkdir()
            build_s6_repo_api_fixture(d6)
            good_s6 = td_p / "good_s6.py"
            good_s6.write_text(
                "from telemetry_window import evaluate_sensor_window\n"
                "assert evaluate_sensor_window([], low_limit=1.0, high_limit=5.0)['status'] == 'EMPTY'\n"
                "assert evaluate_sensor_window([2.0, 3.0], low_limit=1.0, high_limit=5.0)['status'] == 'PASS'\n",
                encoding="utf-8",
            )
            assert score_s6_staged_harness(good_s6, d6)["passed"] is True
            mock_s6 = td_p / "mock_s6.py"
            mock_s6.write_text(
                "import unittest.mock\nfrom telemetry_window import evaluate_sensor_window\n"
                "assert evaluate_sensor_window([], low_limit=1.0, high_limit=5.0)['status'] == 'EMPTY'\n",
                encoding="utf-8",
            )
            assert score_s6_staged_harness(mock_s6, d6)["passed"] is False
            checks.append("s6_contextualized_anti_mock_oracle")

            # S7 retention check (blocks lazy bullet deletion during repair)
            d7 = td_p / "s7"
            d7.mkdir()
            _b7, _g7, _draft7, keep7 = build_s7_corrupted_draft_fixture(d7)
            full_keep_txt = "\n".join(f"- {k}" for k in keep7)
            assert score_s7_repaired_draft(full_keep_txt, {"ran": True, "returncode": 0, "unbacked": 0}, keep7)["passed"] is True
            assert score_s7_repaired_draft("- m3x8mm shcs\n", {"ran": True, "returncode": 0, "unbacked": 0}, keep7)["passed"] is False
            checks.append("s7_repair_retention_guard")

            # S8 contradiction scorer
            d8 = td_p / "s8"
            d8.mkdir()
            b8, g8 = build_s8_contradiction_fixture(d8)
            good_s8 = (
                "- Extruder screw conflict: `M3x12mm SHCS` (`BOM.md#L5`) vs `M3x16mm SHCS` (`Assembly_Guide.md#L7`)\n"
                "- Hotend fan conflict: `24 V 3010 Axial Fan` (`BOM.md#L6`) vs `12 V 3010 Axial Fan` (`Assembly_Guide.md#L8`)\n"
                "- Heat-set insert count: `6` `M3x5x4mm` (`BOM.md#L7`) vs `8` `M3x5x4mm` (`Assembly_Guide.md#L4`)\n"
            )
            assert score_s8_output(good_s8, [b8, g8])["passed"] is True
            assert score_s8_output("- Only fan `24 V` vs `12 V` 3010 (`BOM.md#L6`)\n", [b8, g8])["passed"] is False
            checks.append("s8_contradiction_scorer")

            d8b = td_p / "s8b"
            d8b.mkdir()
            b8b, g8b = build_s8b_mid_contradiction_fixture(d8b)
            good_s8b = (
                "- Motor bolt: `M3x14mm SHCS` (`BOM.md#L18`) vs `M3x20mm SHCS` (`Assembly_Guide.md#L22`)\n"
                "- SSR voltage: `24 V 10 A SSR` (`BOM.md#L34`) vs `12 V 10 A SSR` (`Assembly_Guide.md#L40`)\n"
                "- Exhaust port: `6mm` push-to-connect (`BOM.md#L60`) vs `4mm` (`Assembly_Guide.md#L60`)\n"
                "- PSU wattage: `350 W` (`BOM.md#L61`) vs `200 W` (`Assembly_Guide.md#L61`)\n"
            )
            assert score_s8b_output(good_s8b, [b8b, g8b])["passed"] is True
            assert score_s8b_output("- PSU `350 W` vs `200 W` (`BOM.md#L61`)\n", [b8b, g8b])["passed"] is False
            checks.append("s8b_mid_contradiction_scorer")

            d8c = td_p / "s8c"
            d8c.mkdir()
            b8c, g8c, c8c = build_s8c_large_3file_contradiction_fixture(d8c)
            good_s8c = (
                "- Bolt: `M3x25mm` (`BOM.md#L18`) vs `M3x30mm` (`Assembly_Guide.md#L26`)\n"
                "- Thermal fuse: `125 C Cutoff` (`BOM.md#L53`) vs `150 C Cutoff` (`Assembly_Guide.md#L62`)\n"
                "- Probe rail: `24 V DC` (`BOM.md#L86`) vs `12V` `PB12` (`control.cfg#L98`)\n"
                "- Gear teeth: `36-Tooth` (`BOM.md#L107`) vs `17-Tooth` (`Assembly_Guide.md#L108`)\n"
                "- Blower safety: `shutdown_speed: 1` (`control.cfg#L424`) vs `shutdown_speed: 0` (`Assembly_Guide.md#L109`)\n"
            )
            assert score_s8c_output(good_s8c, [b8c, g8c, c8c])["passed"] is True
            assert score_s8c_output("- Bolt `M3x25mm` vs `M3x30mm`\n", [b8c, g8c, c8c])["passed"] is False
            checks.append("s8c_large_3file_contradiction_scorer")

            d8d = td_p / "s8d"
            d8d.mkdir()
            b8d, g8d, c8d = build_s8d_42kb_contradiction_fixture(d8d)
            good_s8d = (
                "- Bolt: `M4x18mm` (`BOM.md#L25`) vs `M4x22mm` (`Assembly_Guide.md#L30`)\n"
                "- Heater pad: `120 V 750 W` (`BOM.md#L89`) vs `240 V 750 W` (`Assembly_Guide.md#L95`)\n"
                "- Extruder current: `0.85 A` (`BOM.md#L146`) vs `1.25` (`control.cfg#L163`)\n"
                "- Pullup: `4.7 kOhm` vs `2200` (`control.cfg#L920`)\n"
                "- Buck supply: `5 V` (`BOM.md#L190`) vs `12 V` (`Assembly_Guide.md#L190`)\n"
                "- Carbon cartridges: `2` vs `4` (`Assembly_Guide.md#L191`)\n"
            )
            assert score_s8d_output(good_s8d, [b8d, g8d, c8d])["passed"] is True
            checks.append("s8d_42kb_contradiction_scorer")

            d8e = td_p / "s8e"
            d8e.mkdir()
            s8e, g8e, c8e = build_s8e_semantic_logic_fixture(d8e)
            good_s8e = (
                "- Caution: NEVER apply `Loctite 243` on `ABS` (`Material_Rules.md#L4`) vs step (`Assembly_Guide.md#L4`)\n"
                "- Dual `0.25 A` fans = `0.50 A` on `PA3` (`FAN1`) exceeds `0.40 A` continuous (`Material_Rules.md#L7`, `Assembly_Guide.md#L8`, `control.cfg#L5`)\n"
                "- `z_backlash_comp: 0.15` (`control.cfg#L13`) exceeds `0.08 mm` ceiling (`Material_Rules.md#L8`)\n"
                "- `TPU 95A` must stay dry without `White Petroleum Grease` (`Material_Rules.md#L9`, `Assembly_Guide.md#L9`)\n"
            )
            assert score_s8e_output(good_s8e, [s8e, g8e, c8e])["passed"] is True
            checks.append("s8e_semantic_logic_scorer")

    benchmark_apprentice._assert_live_prod_untouched(snap_before, benchmark_apprentice._snapshot_live_prod_files())
    return {"schema_version": SCHEMA_VERSION, "status": "PASS", "tests_run": len(checks), "checks": checks}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Apprentice Phase-3 STANDARD Capability & Bug-Pinning Ladder")
    parser.add_argument("--self-test", action="store_true", help="Run deterministic offline fixture & scorer self-tests")
    parser.add_argument("--list", action="store_true", help="List available STANDARD capability vectors (S1..S8)")
    parser.add_argument("--vectors", default="ALL", help="Comma-separated vector IDs (e.g. S1,S2,S3 or ALL)")
    parser.add_argument("--telemetry-log", default=str(apprentice_engine.DEFAULT_BENCH_TELEMETRY_LOG))
    parser.add_argument("--output-json", default="")
    parser.add_argument("--output-md", default="")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    try:
        if args.self_test:
            res = run_self_tests()
            print(json.dumps(res, indent=2) if args.json else f"[PASS] {res['tests_run']} STANDARD ladder self-tests passed")
            return 0
        if args.list:
            payload = {"schema_version": SCHEMA_VERSION, "vectors": VECTOR_DESCRIPTIONS}
            if args.json:
                print(json.dumps(payload, indent=2))
            else:
                for k, desc in VECTOR_DESCRIPTIONS.items():
                    print(f"  {k}: {desc}")
            return 0

        raw_sel = [tok.strip().upper() for tok in args.vectors.split(",") if tok.strip()]
        if not raw_sel or raw_sel == ["ALL"]:
            selected = list(VECTOR_ORDER)
        else:
            unknown = [v for v in raw_sel if v not in VECTOR_ORDER]
            if unknown:
                raise ValueError(f"Unknown vector ID(s) {unknown}; expected subset of {VECTOR_ORDER} or ALL")
            selected = raw_sel

        tel_path = Path(os.path.expanduser(args.telemetry_log))
        snap_before = benchmark_apprentice._snapshot_live_prod_files()
        with benchmark_apprentice._isolated_bench_env(tel_path) as bench_env:
            report = execute_live_standard_vectors(selected)
            report["bench_cache_env"] = bench_env
        benchmark_apprentice._assert_live_prod_untouched(snap_before, benchmark_apprentice._snapshot_live_prod_files())

        if args.output_json:
            Path(args.output_json).write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        md_text = render_ladder_markdown(report)
        if args.output_md:
            Path(args.output_md).write_text(md_text, encoding="utf-8")
        print(json.dumps(report, indent=2) if args.json else md_text)
        return 0 if report["vectors_passed"] == report["vectors_run"] else 1
    except (ValueError, RuntimeError) as exc:
        print(str(exc), file=sys.stderr)
        return 3


if __name__ == "__main__":
    raise SystemExit(main())
