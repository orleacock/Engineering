#!/usr/bin/env python3
"""
Apprentice Phase-3 HIGH Reasoning & Shadow Second-Eyes Evaluation Suite (`benchmark_apprentice_high.py`).

Governing Priority Law:
    1. Accuracy & Truth -> 2. Efficiency -> 3. Data Safety -> 4. Speed

Isolates `HIGH` (`mode="deep"`, `reasoning_effort="high"`, `>=4096/8192` tok, FIFO exclusive KV slot)
and `apprentice_shadow_review` across 5 seeded comparison vectors (`H1`..`H5`) inside `~/.cache/apprentice_plugin/bench/`:
  - H1_high_stage_edge_case      : Re-runs S5B parser spec under effort="high" (does <think> cure .strip('`~')?)
  - H2_high_47kb_single_shot     : Re-runs S8D (~47.3 KB 3-file cliff) under HIGH_CROSS_SINGLE_SHOT
  - H3_high_semantic_negations   : Re-runs S8E (negated prose + sum-limit traps) under HIGH — checks false positives!
  - H4_oversized_hybrid_map_red  : ~64 KB 4-file cross-audit (>54 KB ceiling) testing HYBRID_MAP_STD_REDUCE_HIGH
  - H5_shadow_review_shootout    : Paired H5_clean vs H5_trap apprentice_shadow_review (CPU oracles + LLM critic SNR)

Usage:
    python3 -B scripts/benchmark_apprentice_high.py --self-test --json
    python3 -B scripts/benchmark_apprentice_high.py --vectors H1,H3 --json
    python3 -B scripts/benchmark_apprentice_high.py --vectors ALL --output-md bench_high_report.md --json
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import subprocess
import sys
import tempfile
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
import benchmark_apprentice_standard as std_bench  # noqa: E402

SCHEMA_VERSION = "APPRENTICE_HIGH_LADDER_V1"
VECTOR_ORDER = ("H1", "H2", "H3", "H4", "H5")
VECTOR_DESCRIPTIONS: dict[str, str] = {
    "H1": "H1_high_stage_edge_case — S5B parser synthesis under effort='high' vs STANDARD failure",
    "H2": "H2_high_47kb_single_shot — S8D (~47.3 KB 3-file cliff) under HIGH_CROSS_SINGLE_SHOT",
    "H3": "H3_high_semantic_negations — S8E negated-prose + sum-limit traps under HIGH (false-positive check)",
    "H4": "H4_oversized_hybrid_map_red — >60 KB 4-file cross-audit testing HYBRID_MAP_STD_REDUCE_HIGH (8192 cap)",
    "H5": "H5_shadow_review_shootout — Clean commit vs Seeded semantic trap commit under apprentice_shadow_review",
}


def build_h4_oversized_64kb_fixture(root: Path) -> tuple[list[Path], int]:
    """Build a >60 KB 4-file payload forcing HYBRID_MAP_STD_REDUCE_HIGH with 4 dispersed contradictions."""
    bom = root / "BOM.md"
    guide = root / "Assembly_Guide.md"
    cfg = root / "control.cfg"
    notes = root / "Wiring_Notes.md"

    bom_rows = [
        "# Mega Subsystem BOM (`BOM.md`)",
        "",
        "| Subassembly | Part | Spec | Qty | Note |",
        "| :--- | :--- | :--- | :---: | :--- |",
    ]
    guide_lines = ["# Mega Assembly Guide (`Assembly_Guide.md`)", ""]
    cfg_lines = ["# Mega Firmware Config (`control.cfg`)", ""]
    notes_lines = ["# Mega Wiring Notes (`Wiring_Notes.md`)", ""]

    for i in range(1, 210):
        bom_rows.append(
            f"| Bay_{i:03d} | Hex Standoff H{i:03d} | `Spacer OD {7 + (i % 3)}mm ID 3.2mm L {9 + (i % 5)}mm Steel` | `{2 + (i % 3)}` | Tray {i % 7} |"
        )
        guide_lines.append(
            f"- Step {i:03d}: Torque `{2 + (i % 3)}` `Spacer OD {7 + (i % 3)}mm ID 3.2mm L {9 + (i % 5)}mm Steel` hex standoffs in Bay {i:03d}."
        )
        cfg_lines.extend(
            [
                f"[stepper_aux_{i:03d}]",
                f"step_pin: PD{i % 16}",
                f"microsteps: {16 if i % 2 == 0 else 32}",
                f"run_current: {0.60 + 0.05 * (i % 4):.2f}",
                "",
            ]
        )
        notes_lines.append(f"- Harness Trunk T{i:03d}: `22 AWG Silicone` Pair -> Pin `P{i:03d}` (`24 V` Logic Safe).")

    bom_rows.insert(20, "| Frame | Linear Rail Carriage Bolt | `M3x10mm SHCS` | `8` | Y rail blocks |")
    guide_lines.insert(25, "- Anchor Y rail blocks with `8` `M3x14mm SHCS` fasteners.")

    bom_rows.insert(95, "| Electrical | Primary Heater SSR | `24 V 25 A SSR` | `1` | AC bed relay |")
    notes_lines.insert(110, "- Connect the `12 V 25 A SSR` control coil to terminal `TB4`.")

    bom_rows.insert(165, "| Motion | Z Drive Stepper Current | `1.10 A RMS` | `1` | Dual Z motor |")
    cfg_lines.insert(190, "# Dual Z driver\n[tmc2209 stepper_z]\nrun_current: 1.65\nsense_resistor: 0.110\n")

    bom_rows.append("| Safety | Exhaust Fan Shutdown | `shutdown_speed: 0` | `1` | Fail-safe stop |")
    cfg_lines.append("[fan_generic exhaust_main]\npin: PE9\nshutdown_speed: 1\n")

    for fp, content in ((bom, bom_rows), (guide, guide_lines), (cfg, cfg_lines), (notes, notes_lines)):
        fp.write_text("\n".join(content) + "\n", encoding="utf-8")

    files = [bom, guide, cfg, notes]
    total_b = sum(f.stat().st_size for f in files)
    return files, total_b


def score_h4_output(text: str, sources: list[Path]) -> dict[str, Any]:
    low = text.lower()
    c_bolt = "m3x10mm" in low and "m3x14mm" in low
    c_ssr = "ssr" in low and "24 v" in low and "12 v" in low
    c_zcurr = ("1.10" in low or "1.1" in low) and "1.65" in low and ("z" in low or "tmc2209" in low or "current" in low)
    c_shut = "shutdown_speed" in low and ("0" in low and "1" in low)
    defects = apprentice_mcp_server._detect_citation_format_defects(text, sources)
    caught = int(c_bolt) + int(c_ssr) + int(c_zcurr) + int(c_shut)
    return {
        "contradictions_caught": caught,
        "contradictions_total": 4,
        "recall_pct": round(100.0 * caught / 4.0, 1),
        "details": {"bolt_10_vs_14": c_bolt, "ssr_24v_vs_12v": c_ssr, "z_curr_110_vs_165": c_zcurr, "shutdown_0_vs_1": c_shut},
        "citation_defects": len(defects),
        "passed": caught == 4 and not defects,
    }


def build_h5_shadow_repos(root: Path) -> tuple[Path, Path]:
    """Create paired Clean git repo + Seeded Semantic Trap git repo (working-tree diff)."""
    clean_repo = root / "h5_clean_repo"
    clean_repo.mkdir(parents=True)
    (clean_repo / "BOM.md").write_text(
        "# BOM (`BOM.md`)\n\n"
        "| Part | Spec | Qty |\n"
        "| :--- | :--- | :---: |\n"
        "| Main Mount Screw | `M3x8mm SHCS` | `4` |\n"
        "| Blower Fan | `24 V 5015` | `1` |\n",
        encoding="utf-8",
    )
    (clean_repo / "Guide.md").write_text(
        "# Assembly Guide (`Guide.md`)\n\n"
        "1. Fasten main mount with `4` `M3x8mm SHCS` screws.\n"
        "2. Wire the `24 V 5015` fan to `FAN0` (`shutdown_speed: 0`).\n",
        encoding="utf-8",
    )
    for cmd in (
        ["git", "-C", str(clean_repo), "init", "-q"],
        ["git", "-C", str(clean_repo), "config", "user.name", "Bench"],
        ["git", "-C", str(clean_repo), "config", "user.email", "bench@localhost"],
        ["git", "-C", str(clean_repo), "add", "BOM.md", "Guide.md"],
        ["git", "-C", str(clean_repo), "commit", "-q", "-m", "baseline"],
    ):
        subprocess.run(cmd, check=True)
    # Harmless working-tree clarification edit (should NOT raise false CRITICAL alarms)
    (clean_repo / "Guide.md").write_text(
        "# Assembly Guide (`Guide.md`)\n\n"
        "1. Fasten main mount with `4` `M3x8mm SHCS` screws (confirm clean threads).\n"
        "2. Wire the `24 V 5015` fan to `FAN0` (`shutdown_speed: 0`).\n",
        encoding="utf-8",
    )

    trap_repo = root / "h5_trap_repo"
    trap_repo.mkdir(parents=True)
    (trap_repo / "Standards.md").write_text(
        "# Safety Standards (`Standards.md`)\n\n"
        "> [!CAUTION]\n"
        "> NEVER apply `Loctite 243` to `ABS` printed parts — anaerobic liquid crazes thermoplastics.\n"
        "> Any heater-bay fan (`heater_fan`) MUST use `shutdown_speed: 0`? Wait — hotend cooling `[heater_fan]` stays at full speed `shutdown_speed: 1`, whereas print/exhaust fans require `shutdown_speed: 0` on fault.\n",
        encoding="utf-8",
    )
    (trap_repo / "BOM.md").write_text(
        "# BOM (`BOM.md`)\n\n"
        "| Part | Spec | Qty |\n"
        "| :--- | :--- | :---: |\n"
        "| Shroud Fastener | `M3x10mm SHCS` | `4` |\n"
        "| Print Cooling Fan | `24 V 5015 Blower` | `1` |\n",
        encoding="utf-8",
    )
    (trap_repo / "printer.cfg").write_text(
        "# Firmware Config (`printer.cfg`)\n\n"
        "[fan]\n"
        "pin: PA6\n"
        "shutdown_speed: 0\n",
        encoding="utf-8",
    )
    (trap_repo / "Guide.md").write_text(
        "# Assembly Guide (`Guide.md`)\n\n"
        "1. Mount `ABS` shroud dry with `4` `M3x10mm SHCS` screws.\n"
        "2. Install the `24 V 5015 Blower` on pin `PA6`.\n",
        encoding="utf-8",
    )
    for cmd in (
        ["git", "-C", str(trap_repo), "init", "-q"],
        ["git", "-C", str(trap_repo), "config", "user.name", "Bench"],
        ["git", "-C", str(trap_repo), "config", "user.email", "bench@localhost"],
        ["git", "-C", str(trap_repo), "add", "Standards.md", "BOM.md", "printer.cfg", "Guide.md"],
        ["git", "-C", str(trap_repo), "commit", "-q", "-m", "baseline"],
    ):
        subprocess.run(cmd, check=True)
    # Inject 2 regex-invisible traps in dirty working tree:
    # (1) Guide.md now tells installer to apply Loctite 243 to ABS shroud (inverted [!CAUTION])
    # (2) printer.cfg changes print cooling fan shutdown_speed: 1 and swaps BOM M3x10mm -> M3x16mm in Guide
    (trap_repo / "Guide.md").write_text(
        "# Assembly Guide (`Guide.md`)\n\n"
        "1. Apply one drop of `Loctite 243` to `4` `M3x16mm SHCS` screws before threading into the `ABS` shroud.\n"
        "2. Install the `24 V 5015 Blower` on pin `PA6`.\n",
        encoding="utf-8",
    )
    (trap_repo / "printer.cfg").write_text(
        "# Firmware Config (`printer.cfg`)\n\n"
        "[fan]\n"
        "pin: PA6\n"
        "shutdown_speed: 1\n",
        encoding="utf-8",
    )
    return clean_repo, trap_repo


def score_h3_semantic_output(text: str, sources: list[Path]) -> dict[str, Any]:
    """Score S8E under HIGH: must catch 4 real traps AND have ZERO false positive on Polycarbonate dry line."""
    base = std_bench.score_s8e_output(text, sources)
    poly_false_pos = any(
        "polycarbonate" in ln.lower() and ("violat" in ln.lower() or "caution" in ln.lower() or "apply" in ln.lower())
        for ln in text.splitlines()
        if "loctite" in ln.lower()
    )
    return {
        **base,
        "zero_polycarbonate_false_positive": not poly_false_pos,
        "passed": base["passed"] and not poly_false_pos,
    }


def score_h5_shadow_cards(clean_card: str, trap_card: str) -> dict[str, Any]:
    clean_low = clean_card.lower()
    trap_low = trap_card.lower()
    trap_loctite = ("loctite" in trap_low and "abs" in trap_low)
    trap_screw = ("m3x10mm" in trap_low and "m3x16mm" in trap_low)
    trap_shutdown = "shutdown_speed" in trap_low and ("1" in trap_low or "0" in trap_low)
    clean_false_alarm = any(
        kw in clean_low for kw in ("critical mismatch", "contradiction:", "error:", "hazard:", "fail")
    ) and ("none" not in clean_low and "no contradiction" not in clean_low and "no semantic" not in clean_low and "no issues" not in clean_low)
    caught = int(trap_loctite) + int(trap_screw) + int(trap_shutdown)
    return {
        "trap_catches": caught,
        "trap_total": 3,
        "trap_details": {"loctite_abs": trap_loctite, "screw_10_vs_16": trap_screw, "fan_shutdown": trap_shutdown},
        "clean_commit_false_alarm": clean_false_alarm,
        "passed": caught == 3 and not clean_false_alarm,
    }


def execute_live_high_vectors(selected: list[str]) -> dict[str, Any]:
    api_url = apprentice_engine.validate_loopback_url(apprentice_engine.resolve_default_api_url())
    srv = apprentice_engine.probe_server_models(api_url, model_id=apprentice_engine.DEFAULT_MODEL_ID, timeout_s=3.0)
    if not srv["reachable"] or not srv["target_model_loaded"]:
        raise RuntimeError(
            f"[BIONIC_NOT_READY] Live HIGH ladder requires ONLINE_READY Bionic at {api_url}; "
            f"reachable={srv['reachable']}, loaded={srv['target_model_loaded']} ({srv.get('error')})"
        )

    results: list[dict[str, Any]] = []
    with tempfile.TemporaryDirectory(prefix="apprentice_high_ladder_") as td:
        td_p = Path(td)

        if "H1" in selected:
            stg_h1 = td_p / "staging_h1"
            stg_h1.mkdir(mode=0o700)
            r_h1 = apprentice_mcp_server.apprentice_stage_patch(
                target_filename="pin_parser.py",
                prompt=(
                    "Write a pure-stdlib Python 3.10+ module defining `parse_pin_table(md_text: str) -> list[dict[str, object]]`.\n"
                    "Specification:\n"
                    "1. Parse Markdown pipe tables whose header row has columns `| Signal | Pin | Pull |` (skipping non-table prose, header row, and alignment/separator rows such as `| --- | --- | --- |`, `| :--- | :--- | :---: |`, or `|---|---|---|`).\n"
                    "2. Strip backticks and any trailing `# ...` inline comment inside cells (preserve literal `~`/`^`/`!` pin prefixes!).\n"
                    "3. In the `Pin` cell, parse optional prefix modifiers in any order before the pin name (e.g. `!^PB4`, `^!PC13`, `~PD2`, `PA1`):\n"
                    "   - `!` sets `'inverted': True` (default `False`)\n"
                    "   - `^` sets `'pullup': True` (default `False`)\n"
                    "   - `~` sets `'pulldown': True` (default `False`)\n"
                    "   - Raise `ValueError` if both `^` and `~` are present on the same pin.\n"
                    "4. Track physical stripped pin names (case-insensitive) across the table and raise `ValueError` on duplicate physical pins (e.g. `PA1` and `!PA1`).\n"
                    "5. Return a list of dicts in row order: `{'signal': <str>, 'pin': <stripped_pin_str>, 'inverted': <bool>, 'pullup': <bool>, 'pulldown': <bool>}`.\n"
                    "6. Include an `if __name__ == '__main__':` `--self-test` CLI block."
                ),
                staging_dir=str(stg_h1),
                effort="high",
                invocation_tier="explicit",
            )
            ext_h1 = std_bench.run_s5_external_oracle(Path(r_h1["staged_file"])) if r_h1.get("staged_file") else {"passed": False, "cases_passed": 0, "cases_total": 10}
            results.append(
                {
                    "id": "H1",
                    "name": "HIGH stage_patch Edge-Case Parser (vs STANDARD S5B Failure)",
                    "ok": r_h1.get("ok"),
                    "verdict": r_h1.get("verdict"),
                    "attempts": r_h1.get("attempts"),
                    "elapsed_s": r_h1.get("elapsed_s"),
                    "heal_elapsed_s": r_h1.get("heal_elapsed_s"),
                    "external_oracle": ext_h1,
                    "passed": bool(r_h1.get("ok") and ext_h1.get("passed")),
                }
            )

        if "H2" in selected:
            d_h2 = td_p / "h2"
            d_h2.mkdir()
            b2, g2, c2 = std_bench.build_s8d_42kb_contradiction_fixture(d_h2)
            raw_b2 = b2.stat().st_size + g2.stat().st_size + c2.stat().st_size
            r_h2 = apprentice_mcp_server.apprentice_digest(
                prompt=(
                    "Compare BOM.md, Assembly_Guide.md, and control.cfg across all sections and list ONLY genuine "
                    "contradictions (fasteners, voltages, currents, pullup resistors, quantities). Include exact values "
                    "and separate `file.ext#Lstart-Lend` anchors on every bullet (no `<` `>` brackets). Zero preamble."
                ),
                context_files=["BOM.md", "Assembly_Guide.md", "control.cfg"],
                repo=str(d_h2),
                effort="auto",
                invocation_tier="explicit",
                verify_claims=True,
            )
            txt_h2 = str((r_h2.get("completion") or {}).get("content") or "")
            sc_h2 = std_bench.score_s8d_output(txt_h2, [b2, g2, c2])
            results.append(
                {
                    "id": "H2",
                    "name": f"HIGH_CROSS_SINGLE_SHOT ~{round(raw_b2 / 1024.0, 1)} KB (vs STANDARD S8D 5/6)",
                    "ok": r_h2.get("ok"),
                    "route_id": r_h2.get("route_id"),
                    "verdict": r_h2.get("verdict"),
                    "claims_verified": r_h2.get("claims_verified"),
                    "elapsed_s": (r_h2.get("completion") or {}).get("elapsed_s"),
                    "heal_elapsed_s": r_h2.get("heal_elapsed_s"),
                    "prompt_tokens": (r_h2.get("completion") or {}).get("prompt_tokens"),
                    "completion_tokens": (r_h2.get("completion") or {}).get("completion_tokens"),
                    "score": sc_h2,
                    "passed": bool(r_h2.get("ok") and r_h2.get("verdict") in {"clean", "healed"} and sc_h2["passed"]),
                    "draft_preview": txt_h2[:1200],
                }
            )

        if "H3" in selected:
            d_h3 = td_p / "h3"
            d_h3.mkdir()
            s3, g3, c3 = std_bench.build_s8e_semantic_logic_fixture(d_h3)
            r_h3 = apprentice_mcp_server.apprentice_digest(
                prompt=(
                    "Audit Assembly_Guide.md and control.cfg against Material_Rules.md. Flag ONLY genuine safety/caution "
                    "violations, summed current overruns, backlash ceiling breaches, or chemical incompatibilities with "
                    "separate `file.ext#Lstart-Lend` anchors (no `<` `>` brackets). Do NOT flag steps that explicitly follow dry/non-threadlocker rules. Zero preamble."
                ),
                context_files=["Material_Rules.md", "Assembly_Guide.md", "control.cfg"],
                repo=str(d_h3),
                effort="high",
                invocation_tier="explicit",
                verify_claims=True,
            )
            txt_h3 = str((r_h3.get("completion") or {}).get("content") or "")
            sc_h3 = score_h3_semantic_output(txt_h3, [s3, g3, c3])
            results.append(
                {
                    "id": "H3",
                    "name": "HIGH Semantic Negation & Sum-Limit Audit (vs STANDARD S8E False Pos)",
                    "ok": r_h3.get("ok"),
                    "route_id": r_h3.get("route_id"),
                    "verdict": r_h3.get("verdict"),
                    "claims_verified": r_h3.get("claims_verified"),
                    "elapsed_s": (r_h3.get("completion") or {}).get("elapsed_s"),
                    "heal_elapsed_s": r_h3.get("heal_elapsed_s"),
                    "prompt_tokens": (r_h3.get("completion") or {}).get("prompt_tokens"),
                    "completion_tokens": (r_h3.get("completion") or {}).get("completion_tokens"),
                    "score": sc_h3,
                    "passed": bool(r_h3.get("ok") and r_h3.get("verdict") in {"clean", "healed"} and sc_h3["passed"]),
                    "draft_preview": txt_h3[:1200],
                }
            )

        if "H4" in selected:
            d_h4 = td_p / "h4"
            d_h4.mkdir()
            files_h4, raw_b4 = build_h4_oversized_64kb_fixture(d_h4)
            r_h4 = apprentice_mcp_server.apprentice_digest(
                prompt=(
                    "Compare BOM.md, Assembly_Guide.md, control.cfg, and Wiring_Notes.md across all sections and list ONLY "
                    "genuine specification or value contradictions (bolts, SSR coils, stepper currents, shutdown_speed). "
                    "Include exact values and separate `file.ext#Lstart-Lend` anchors (no `<` `>` brackets). Zero preamble."
                ),
                context_files=[f.name for f in files_h4],
                repo=str(d_h4),
                effort="auto",
                invocation_tier="explicit",
                verify_claims=True,
            )
            txt_h4 = str((r_h4.get("completion") or {}).get("content") or "")
            sc_h4 = score_h4_output(txt_h4, files_h4)
            results.append(
                {
                    "id": "H4",
                    "name": f"Oversized ~{round(raw_b4 / 1024.0, 1)} KB HYBRID_MAP_STD_REDUCE_HIGH",
                    "ok": r_h4.get("ok"),
                    "route_id": r_h4.get("route_id"),
                    "chunked_map_reduce": r_h4.get("chunked_map_reduce"),
                    "verdict": r_h4.get("verdict"),
                    "claims_verified": r_h4.get("claims_verified"),
                    "elapsed_s": (r_h4.get("completion") or {}).get("elapsed_s"),
                    "heal_elapsed_s": r_h4.get("heal_elapsed_s"),
                    "prompt_tokens": (r_h4.get("completion") or {}).get("prompt_tokens"),
                    "completion_tokens": (r_h4.get("completion") or {}).get("completion_tokens"),
                    "score": sc_h4,
                    "passed": bool(r_h4.get("ok") and r_h4.get("verdict") in {"clean", "healed"} and sc_h4["passed"]),
                    "draft_preview": txt_h4[:1200],
                }
            )

        if "H5" in selected:
            clean_repo, trap_repo = build_h5_shadow_repos(td_p)
            r_h5_clean = apprentice_mcp_server.apprentice_shadow_review(
                repo=str(clean_repo),
                draft_files=["Guide.md"],
                context_files=["BOM.md"],
                include_git_diff=True,
                prompt="Report ONLY genuine verified contradictions or safety violations in the diff against BOM.md; say NO CONTRADICTIONS FOUND if clean.",
                effort="auto",
                invocation_tier="explicit",
                async_job=False,
            )
            r_h5_trap = apprentice_mcp_server.apprentice_shadow_review(
                repo=str(trap_repo),
                draft_files=["Guide.md", "printer.cfg"],
                context_files=["Standards.md", "BOM.md"],
                include_git_diff=True,
                prompt="Report ONLY genuine verified contradictions and [!CAUTION]/safety violations introduced in the working-tree diff citing exact `file.ext#Lstart-Lend` anchors verbatim (no `<` `>` brackets).",
                effort="auto",
                invocation_tier="explicit",
                async_job=False,
            )
            sc_h5 = score_h5_shadow_cards(str(r_h5_clean.get("shadow_card") or ""), str(r_h5_trap.get("shadow_card") or ""))
            results.append(
                {
                    "id": "H5",
                    "name": "apprentice_shadow_review Clean vs Semantic-Trap Shootout",
                    "clean_arm": {
                        "ok": r_h5_clean.get("ok"),
                        "verdict": r_h5_clean.get("verdict"),
                        "route_id": r_h5_clean.get("route_id"),
                        "cpu_ms": (r_h5_clean.get("cpu_oracles") or {}).get("elapsed_ms"),
                        "llm_s": (r_h5_clean.get("completion_telemetry") or {}).get("elapsed_s"),
                        "claims_verified": r_h5_clean.get("claims_verified"),
                        "card_preview": str(r_h5_clean.get("shadow_card") or "")[:600],
                    },
                    "trap_arm": {
                        "ok": r_h5_trap.get("ok"),
                        "verdict": r_h5_trap.get("verdict"),
                        "route_id": r_h5_trap.get("route_id"),
                        "cpu_ms": (r_h5_trap.get("cpu_oracles") or {}).get("elapsed_ms"),
                        "llm_s": (r_h5_trap.get("completion_telemetry") or {}).get("elapsed_s"),
                        "claims_verified": r_h5_trap.get("claims_verified"),
                        "card_preview": str(r_h5_trap.get("shadow_card") or "")[:800],
                    },
                    "score": sc_h5,
                    "passed": bool(r_h5_clean.get("ok") and r_h5_trap.get("ok") and sc_h5["passed"]),
                }
            )

    passed_cnt = sum(1 for r in results if r.get("passed"))
    return {
        "schema_version": SCHEMA_VERSION,
        "timestamp_utc": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        "server_status": srv,
        "vectors_run": len(results),
        "vectors_passed": passed_cnt,
        "results": results,
    }


def run_self_tests() -> dict[str, Any]:
    snap_before = benchmark_apprentice._snapshot_live_prod_files()
    checks: list[str] = []
    with tempfile.TemporaryDirectory(prefix="high_ladder_st_") as td:
        td_p = Path(td)
        d3 = td_p / "h3"
        d3.mkdir()
        s3, g3, c3 = std_bench.build_s8e_semantic_logic_fixture(d3)
        good_h3 = (
            "- Caution: Loctite 243 applied to `ABS` (`Material_Rules.md#L4`, `Assembly_Guide.md#L4`)\n"
            "- Fan overrun `0.50 A` > `0.40 A` on `PA3` (`Material_Rules.md#L7`, `Assembly_Guide.md#L8`, `control.cfg#L5`)\n"
            "- `z_backlash_comp: 0.15` > `0.08 mm` (`control.cfg#L14`, `Material_Rules.md#L8`)\n"
            "- `TPU 95A` dry vs `White Petroleum Grease` (`Material_Rules.md#L9`, `Assembly_Guide.md#L9`)\n"
        )
        assert score_h3_semantic_output(good_h3, [s3, g3, c3])["passed"] is True
        fp_h3 = good_h3 + "- Caution: Loctite 243 applied to Polycarbonate housing (`Assembly_Guide.md#L5`)\n"
        assert score_h3_semantic_output(fp_h3, [s3, g3, c3])["passed"] is False
        checks.append("h3_semantic_negation_anti_fp_scorer")

        d4 = td_p / "h4"
        d4.mkdir()
        files4, raw4 = build_h4_oversized_64kb_fixture(d4)
        assert raw4 > 55296, f"expected >54KB H4 fixture, got {raw4}"
        good_h4 = (
            "- Bolt: `M3x10mm` vs `M3x14mm`\n"
            "- SSR: `24 V` vs `12 V`\n"
            "- Z current: `1.10` vs `1.65` (`tmc2209 stepper_z`)\n"
            "- Exhaust `shutdown_speed`: `0` vs `1`\n"
        )
        assert score_h4_output(good_h4, files4)["passed"] is True
        checks.append("h4_oversized_64kb_fixture_and_scorer")

        c_repo, t_repo = build_h5_shadow_repos(td_p)
        assert (c_repo / ".git").is_dir() and (t_repo / ".git").is_dir()
        sc5 = score_h5_shadow_cards(
            "- NO CONTRADICTIONS FOUND (`BOM.md`, `Guide.md`).",
            "- Caution: Loctite 243 on ABS (`Guide.md#L3`); screw `M3x10mm` vs `M3x16mm`; fan `shutdown_speed: 1` (`printer.cfg#L5`).",
        )
        assert sc5["passed"] is True
        assert score_h5_shadow_cards("- CRITICAL MISMATCH found!", "- Loctite on ABS")["passed"] is False
        checks.append("h5_shadow_repos_and_shootout_scorer")

    benchmark_apprentice._assert_live_prod_untouched(snap_before, benchmark_apprentice._snapshot_live_prod_files())
    return {"schema_version": SCHEMA_VERSION, "status": "PASS", "tests_run": len(checks), "checks": checks}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Apprentice Phase-3 HIGH Reasoning & Shadow Shootout Suite")
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--list", action="store_true")
    parser.add_argument("--vectors", default="ALL")
    parser.add_argument("--telemetry-log", default=str(apprentice_engine.DEFAULT_BENCH_TELEMETRY_LOG))
    parser.add_argument("--output-json", default="")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    try:
        if args.self_test:
            res = run_self_tests()
            print(json.dumps(res, indent=2) if args.json else f"[PASS] {res['tests_run']} HIGH ladder tests passed")
            return 0
        if args.list:
            print(json.dumps({"schema_version": SCHEMA_VERSION, "vectors": VECTOR_DESCRIPTIONS}, indent=2))
            return 0
        raw_sel = [tok.strip().upper() for tok in args.vectors.split(",") if tok.strip()]
        selected = list(VECTOR_ORDER) if (not raw_sel or raw_sel == ["ALL"]) else raw_sel
        unknown = [v for v in selected if v not in VECTOR_ORDER]
        if unknown:
            raise ValueError(f"Unknown vector ID(s) {unknown}; expected {VECTOR_ORDER}")

        tel_path = Path(os.path.expanduser(args.telemetry_log))
        snap_before = benchmark_apprentice._snapshot_live_prod_files()
        with benchmark_apprentice._isolated_bench_env(tel_path) as bench_env:
            report = execute_live_high_vectors(selected)
            report["bench_cache_env"] = bench_env
        benchmark_apprentice._assert_live_prod_untouched(snap_before, benchmark_apprentice._snapshot_live_prod_files())

        if args.output_json:
            Path(args.output_json).write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(report, indent=2))
        return 0 if report["vectors_passed"] == report["vectors_run"] else 1
    except (ValueError, RuntimeError) as exc:
        print(str(exc), file=sys.stderr)
        return 3


if __name__ == "__main__":
    raise SystemExit(main())
