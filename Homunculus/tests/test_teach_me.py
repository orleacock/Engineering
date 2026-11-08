#!/usr/bin/env python3
"""Unit and integration tests for Universal Engineering & Technical Learning Engine (`teach-me`).

Verifies:
  1. `teach_brief.py --init-brief` whole-word `<Subject>_on_<Impact>` slugging, stopword/parenthetical stripping,
     project deduplication, hyphen preservation (`teach-me`, `DC-DC`), and `--rename-clean`
  2. Solid-Line Datasheet Card (`┏━━ 🎓 TEACH-ME // BRIEF+ ... ━━┓` / `┗━━ 🔒 QUARANTINED: ... ━━┛`) width parity (`< 80` cols)
  3. Theory-Zone `[CALC]` dimensional math vs. closed-world repository overlap verification (`VRF-<12hex>`)
  4. Fail-closed quarantine & evasion gates (`THEORY_ZONE_EVASION_BLOCKED`, theory-number laundering, `STUDY_BRIEF_SOURCE_REJECTED`)
  5. Explicit `--promote` workflow (`UNPROMOTED_STUDY_BRIEF` -> `PROMOTED_ENGINEERING_BRIEF`)
  6. Umbrella-Org multi-project entity scoping: same-project repo+memory alignment (`0` false positives in any `--sources` order)
     paired with strict fail-closed `CROSS_ENTITY_BORROWING` blocking across sibling projects sharing `entity: "Umbrella-Org"`
Requires ONLY Python 3.10+ standard library.
"""
from __future__ import annotations

from pathlib import Path
import json
import subprocess
import sys
import tempfile
import unittest

REPO_ROOT = Path(__file__).resolve().parent.parent
TEACH_BRIEF = REPO_ROOT / "skills/teach-me/scripts/teach_brief.py"
VERIFY_CLAIMS = REPO_ROOT / "skills/claim-verification/scripts/verify_claims.py"
SANDBOX_RUNNER_DIR = REPO_ROOT / "skills/engineering-sandbox/scripts"


class TestTeachMe(unittest.TestCase):
    def test_teach_me_brief_plus_naming_card_and_quarantine(self) -> None:
        """Verify teach_brief.py --init-brief, whole-word naming, solid-line card rails, quarantine, and --promote."""
        with tempfile.TemporaryDirectory() as tmp:
            tdir = Path(tmp)
            mem_root = tdir / "memory"
            (mem_root / "Standards_and_Specs").mkdir(parents=True)
            (mem_root / "Projects" / "Actuator_Rig").mkdir(parents=True)
            briefs_root = tdir / "study_briefs"

            hw_src = tdir / "Actuator_Rig_Control.cfg"
            hw_src.write_text(
                "# Actuator Rig Stepper & Bus Telemetry\n"
                "# Supply Voltage: 24 V\n"
                "# Stepper Phase Current: 0.85 A\n"
                "# Umbilical Harness Gauge: 22 AWG\n"
                "# Housing Mount Fasteners: 4x M3x12 SHCS\n"
                "step_pin: PB13\n"
                "run_current: 0.85\n",
                encoding="utf-8",
            )

            # 1. Scaffold Brief+ in non-consumed study_briefs/
            proc_init = subprocess.run(
                [
                    sys.executable,
                    str(TEACH_BRIEF),
                    "--briefs-root",
                    str(briefs_root),
                    "--memory-root",
                    str(mem_root),
                    "--init-brief",
                    "--subject",
                    "TMC2209 Sense Resistor Power Dissipation",
                    "--impact-on",
                    "NEMA14 Stepper Thermal Margin",
                    "--domain",
                    "electrical",
                    "--project",
                    "Actuator_Rig",
                    "--json",
                ],
                capture_output=True,
                text=True,
            )
            self.assertEqual(proc_init.returncode, 0, proc_init.stderr)
            init_data = json.loads(proc_init.stdout)
            brief_path = Path(init_data["brief_path"])
            self.assertTrue(brief_path.is_file())
            self.assertTrue((briefs_root / "README.md").is_file())
            self.assertIn("TMC2209_Sense_Resistor_Power_on_NEMA14_Stepper", brief_path.name)
            self.assertEqual(init_data["display_name"], f"Actuator_Rig/{brief_path.name}")

            # 1b. Verify verbose subject + parentheticals + stopwords + project dedupe snap strictly at whole words
            proc_long = subprocess.run(
                [
                    sys.executable,
                    str(TEACH_BRIEF),
                    "--briefs-root",
                    str(briefs_root),
                    "--memory-root",
                    str(mem_root),
                    "--init-brief",
                    "--subject",
                    "The teach-me Skill (Brief+ and Throw-Away Subagent Engine)",
                    "--impact-on",
                    "Actuator_Rig Architecture, Context Efficiency, and Truth Verification",
                    "--domain",
                    "software",
                    "--project",
                    "Actuator_Rig",
                    "--json",
                ],
                capture_output=True,
                text=True,
            )
            self.assertEqual(proc_long.returncode, 0, proc_long.stderr)
            long_data = json.loads(proc_long.stdout)
            long_p = Path(long_data["brief_path"])
            self.assertTrue(long_p.name.endswith("_teach-me_Skill_on_Architecture_Context_Efficiency.md"), long_p.name)

            # 1c. Verify --rename-clean repairs legacy mid-word truncated filenames in place
            truncated_p = long_p.parent / "2026-11-06_The_teach_me_Skill_Brief_and_Throw_Away_impact_o.md"
            long_p.rename(truncated_p)
            proc_ren = subprocess.run(
                [sys.executable, str(TEACH_BRIEF), "--rename-clean", str(truncated_p), "--json"],
                capture_output=True,
                text=True,
            )
            self.assertEqual(proc_ren.returncode, 0, proc_ren.stderr)
            ren_data = json.loads(proc_ren.stdout)
            self.assertEqual(ren_data["status"], "RENAMED")
            self.assertTrue(Path(ren_data["new_path"]).name.endswith("_teach-me_Skill_on_Architecture_Context_Efficiency.md"))

            # 2. Populate valid Brief+ (First-Principles Theory with textbook 120 Ω [CALC] + Closed-World Repo Overlap)
            valid_brief_text = (
                "---\n"
                'title: "TMC2209 Sense Resistor Power Dissipation — Impact on NEMA14 Stepper Thermal Margin"\n'
                'subject: "TMC2209 Sense Resistor Power Dissipation"\n'
                'impact_on: "NEMA14 Stepper Thermal Margin"\n'
                'domain: "electrical"\n'
                'project: "Actuator_Rig"\n'
                'entity: "Actuator_Rig"\n'
                'type: "study-brief"\n'
                'status: "UNPROMOTED_STUDY_BRIEF"\n'
                "consumed_by_memory: false\n"
                'vrf_receipt: "UNVERIFIED"\n'
                'created_at: "2026-11-06"\n'
                "---\n\n"
                "# 🧠 Engineering Brief+: TMC2209 Sense Resistor Power Dissipation\n\n"
                "> [!NOTE]\n"
                "> - **Verification Receipt**: UNVERIFIED | **Source Hashes**: PENDING\n\n"
                "<!-- FIRST-PRINCIPLES-THEORY:START -->\n"
                "## 1. Core Mental Model (What TMC2209 Sense Resistor Power Dissipation Is & Governing Mechanism)\n"
                "- Standard CAN termination across a differential pair is 120 Ω (`[CALC: 24 V / 120 Ω = 0.2 A]`).\n\n"
                "## 2. Relational Impact Vector (How TMC2209 Sense Resistor Power Dissipation Drives or Constrains NEMA14 Stepper Thermal Margin)\n"
                "- Higher phase current increases PCB sense resistor heat.\n"
                "<!-- FIRST-PRINCIPLES-THEORY:END -->\n\n"
                "## 3. Active Engineering Context Overlaps (Verified Project Examples)\n"
                "### Overlap Example 1: Direct Touchpoint in Actuator_Rig\n"
                "- [VERIFIED FACT] The active rig runs on `24 V` over a `22 AWG` umbilical at `0.85 A` phase current (`run_current: 0.85`) on `PB13` with `4` `M3x12` SHCS fasteners (Source: `Actuator_Rig_Control.cfg#L5-L7`).\n"
                "  Anchor:\n"
                "  ```text\n"
                "  # Housing Mount Fasteners: 4x M3x12 SHCS\n"
                "  step_pin: PB13\n"
                "  run_current: 0.85\n"
                "  ```\n\n"
                "## 4. Actionable Engineering Guardrails (Immediate Application Checklist)\n"
                "1. Keep phase current at or below `0.85 A` on the `24 V` rail.\n"
            )
            brief_path.write_text(valid_brief_text, encoding="utf-8")

            proc_ver = subprocess.run(
                [
                    sys.executable,
                    str(TEACH_BRIEF),
                    "--verify",
                    str(brief_path),
                    "--sources",
                    str(hw_src),
                    "--json",
                ],
                capture_output=True,
                text=True,
            )
            self.assertEqual(proc_ver.returncode, 0, proc_ver.stdout + proc_ver.stderr)
            ver_data = json.loads(proc_ver.stdout)
            self.assertEqual(ver_data["status"], "PASS")
            self.assertTrue(ver_data["vrf_token"].startswith("VRF-"))
            self.assertIn(ver_data["vrf_token"], brief_path.read_text(encoding="utf-8"))
            self.assertIn("┏━━ 🎓 TEACH-ME // BRIEF+", ver_data["chat_rail_top"])
            self.assertIn("[DOMAIN: ELECTRICAL] ━━ [ISOLATED SUBAGENT] ━━┓", ver_data["chat_rail_top"])
            self.assertIn("┗━━ 🔒 QUARANTINED: study_briefs/ (NON-CONSUMED)", ver_data["chat_rail_bottom"])
            self.assertIn(f"[{ver_data['vrf_token']}] ━━┛", ver_data["chat_rail_bottom"])
            self.assertEqual(len(ver_data["chat_rail_top"]), len(ver_data["chat_rail_bottom"]))
            self.assertIn(f"▸ **STUDY BRIEF+**: [Actuator_Rig/{brief_path.name}](file://", ver_data["chat_card_template"])

            # 3. Fault A: Theory-Zone Evasion (wrapping Section 3 inside FIRST-PRINCIPLES-THEORY) must fail closed
            evasion_brief = tdir / "study_briefs" / "evasion.md"
            evasion_brief.write_text(
                valid_brief_text.replace("<!-- FIRST-PRINCIPLES-THEORY:END -->\n\n", "")
                + "\n<!-- FIRST-PRINCIPLES-THEORY:END -->\n",
                encoding="utf-8",
            )
            proc_evade = subprocess.run(
                [sys.executable, str(TEACH_BRIEF), "--verify", str(evasion_brief), "--sources", str(hw_src)],
                capture_output=True,
                text=True,
            )
            self.assertNotEqual(proc_evade.returncode, 0)
            self.assertIn("THEORY_ZONE_EVASION_BLOCKED", proc_evade.stdout)

            # 4. Fault B: Theory-derived number laundering (0.2 A from theory [CALC] used in Section 3) must fail closed
            laundered_brief = tdir / "study_briefs" / "laundered.md"
            laundered_brief.write_text(
                valid_brief_text.replace("at `0.85 A` phase current", "at `0.2 A` phase current"),
                encoding="utf-8",
            )
            proc_launder = subprocess.run(
                [sys.executable, str(TEACH_BRIEF), "--verify", str(laundered_brief), "--sources", str(hw_src)],
                capture_output=True,
                text=True,
            )
            self.assertNotEqual(proc_launder.returncode, 0)
            self.assertIn("[Hint] Sections 3–4 are closed-world audited", proc_launder.stdout)

            # 4b. Fast-Path Single-Call: Direct write_file + --verify --auto-slug ensures README, clean-renames, and stamps VRF
            fast_root = tdir / "fast_study_briefs"
            rough_brief = fast_root / "Actuator_Rig" / "2026-11-06_rough_draft.md"
            rough_brief.parent.mkdir(parents=True, exist_ok=True)
            rough_brief.write_text(valid_brief_text, encoding="utf-8")
            proc_fast = subprocess.run(
                [
                    sys.executable,
                    str(TEACH_BRIEF),
                    "--briefs-root",
                    str(fast_root),
                    "--verify",
                    str(rough_brief),
                    "--auto-slug",
                    "--sources",
                    str(hw_src),
                    "--json",
                ],
                capture_output=True,
                text=True,
            )
            self.assertEqual(proc_fast.returncode, 0, proc_fast.stdout + proc_fast.stderr)
            fast_data = json.loads(proc_fast.stdout)
            self.assertEqual(fast_data["status"], "PASS")
            self.assertTrue((fast_root / "README.md").is_file())
            self.assertFalse(rough_brief.exists())
            snapped_path = Path(fast_data["brief_path"])
            self.assertTrue(snapped_path.is_file())
            self.assertIn("TMC2209_Sense_Resistor_Power_on_NEMA14_Stepper", snapped_path.name)
            self.assertIn(fast_data["vrf_token"], snapped_path.read_text(encoding="utf-8"))
            self.assertIn(f"Actuator_Rig/{snapped_path.name}", fast_data["chat_card_template"])

            # 5. Fault C: Passing a study_briefs/ file as --sources to verify_claims.py must be rejected
            dummy_target = tdir / "dummy_doc.md"
            dummy_target.write_text("# Doc\n- Current: 0.2 A\n", encoding="utf-8")
            proc_reject_src = subprocess.run(
                [sys.executable, str(VERIFY_CLAIMS), "--target", str(dummy_target), "--sources", str(brief_path)],
                capture_output=True,
                text=True,
            )
            self.assertNotEqual(proc_reject_src.returncode, 0)
            self.assertIn("STUDY_BRIEF_SOURCE_REJECTED", proc_reject_src.stderr)

            # 6. Promote verified Brief+ into Standards_and_Specs/
            proc_prom = subprocess.run(
                [
                    sys.executable,
                    str(TEACH_BRIEF),
                    "--memory-root",
                    str(mem_root),
                    "--promote",
                    str(brief_path),
                    "--project",
                    "Actuator_Rig",
                    "--target",
                    "standards",
                    "--sources",
                    str(hw_src),
                    "--json",
                ],
                capture_output=True,
                text=True,
            )
            self.assertEqual(proc_prom.returncode, 0, proc_prom.stdout + proc_prom.stderr)
            prom_data = json.loads(proc_prom.stdout)
            self.assertEqual(prom_data["status"], "PROMOTED")
            self.assertTrue(Path(prom_data["promoted_to"]).is_file())
            self.assertIn('status: "PROMOTED_ENGINEERING_BRIEF"', Path(prom_data["promoted_to"]).read_text(encoding="utf-8"))

    def test_umbrella_org_entity_alignment_and_cross_project_hallucination_block(self) -> None:
        """Ensures sibling repos under a shared Umbrella-Org never alias together or let cross-project hallucinations slip by."""
        with tempfile.TemporaryDirectory() as tmp:
            tdir = Path(tmp)
            mem_root = tdir / "memory"
            alpha_repo = tdir / "Projects" / "UmbrellaOrg" / "Repo_Alpha"
            beta_repo = tdir / "Projects" / "UmbrellaOrg" / "Repo_Beta"
            (alpha_repo / ".git").mkdir(parents=True, exist_ok=True)
            (beta_repo / ".git").mkdir(parents=True, exist_ok=True)

            alpha_guide = alpha_repo / "Assembly_Guide.md"
            alpha_guide.write_text(
                "# Repo_Alpha Assembly\n- Feed Tube Length: 55 mm\n- Mount Fasteners: 4x M3x8 SHCS\n",
                encoding="utf-8",
            )
            beta_cfg = beta_repo / "Control.cfg"
            beta_cfg.write_text(
                "[pressure_sensor manifold]\nsensor_pin: PF7\nmax_pressure: 95 kPa\n",
                encoding="utf-8",
            )

            alpha_mem_hw = mem_root / "Projects" / "Repo_Alpha" / "Repo_Alpha_Hardware.md"
            alpha_mem_hw.parent.mkdir(parents=True, exist_ok=True)
            alpha_mem_hw.write_text(
                '---\nproject: "Repo_Alpha"\nentity: "Umbrella-Org"\ntype: "hardware-dossier"\n---\n'
                "# Repo_Alpha Hardware\n- Extruder Step Pin: `PB4`\n",
                encoding="utf-8",
            )
            beta_mem_hw = mem_root / "Projects" / "Repo_Beta" / "Repo_Beta_Hardware.md"
            beta_mem_hw.parent.mkdir(parents=True, exist_ok=True)
            beta_mem_hw.write_text(
                '---\nproject: "Repo_Beta"\nentity: "Umbrella-Org"\ntype: "hardware-dossier"\n---\n'
                "# Repo_Beta Hardware\n- Manifold Sensor Pin: `PF7` at 95 kPa\n",
                encoding="utf-8",
            )

            # 1. Positive: Same-project repo doc + memory dossier align cleanly in BOTH --sources orders
            alpha_brief = tdir / "study_briefs" / "Repo_Alpha" / "2026-11-06_Feed_Tube_on_Extruder.md"
            alpha_brief.parent.mkdir(parents=True, exist_ok=True)
            alpha_brief_body = (
                "---\n"
                'title: "Feed Tube — Impact on Extruder"\n'
                'subject: "Feed Tube"\n'
                'impact_on: "Extruder"\n'
                'domain: "mechanical"\n'
                'project: "Repo_Alpha"\n'
                'entity: "Umbrella-Org"\n'
                'type: "study-brief"\n'
                'status: "UNPROMOTED_STUDY_BRIEF"\n'
                "consumed_by_memory: false\n"
                'vrf_receipt: "UNVERIFIED"\n'
                'created_at: "2026-11-06"\n'
                "---\n\n"
                "# 🧠 Engineering Brief+: Feed Tube → Extruder\n\n"
                "> [!NOTE]\n"
                "> **Non-Consumed Study Brief (status: UNPROMOTED_STUDY_BRIEF)**\n"
                "> - **Verification Receipt**: UNVERIFIED | **Source Hashes**: PENDING\n\n"
                "<!-- FIRST-PRINCIPLES-THEORY:START -->\n"
                "## 1. Core Mental Model\n"
                "- **Capillary Clearance**: Wall thickness `[CALC: (4 mm - 2 mm) / 2 = 1 mm]`.\n\n"
                "## 2. Relational Impact Vector (Feed Tube -> Extruder)\n"
                "- **Causal Chain**: Feed Tube -> Friction -> Extruder.\n"
                "|Perturbation|Effect|\n|---|---|\n|Longer|More drag|\n"
                "<!-- FIRST-PRINCIPLES-THEORY:END -->\n\n"
                "## 3. Active Engineering Context Overlaps\n"
                f"- [VERIFIED FACT] **UmbrellaOrg Repo_Alpha Tube & Pin**: Uses a 55 mm feed tube with 4x M3x8 SHCS "
                f"(Source: `{alpha_guide}#L2-L3`) and extruder step pin `PB4` (Source: `{alpha_mem_hw}#L7`).\n\n"
                "## 4. Actionable Engineering Guardrails\n"
                "- [ ] Confirm `PB4` step pin assignment against `Repo_Alpha_Hardware.md`.\n"
            )
            for src_pair in ([str(alpha_guide), str(alpha_mem_hw)], [str(alpha_mem_hw), str(alpha_guide)]):
                alpha_brief.write_text(alpha_brief_body, encoding="utf-8")
                proc_pos = subprocess.run(
                    [sys.executable, str(TEACH_BRIEF), "--verify", str(alpha_brief), "--sources", *src_pair],
                    capture_output=True,
                    text=True,
                )
                self.assertEqual(proc_pos.returncode, 0, proc_pos.stdout + proc_pos.stderr)

            # 2. Negative Hallucination Gate #1: Repo_Alpha brief smuggling Repo_Beta's PF7 / 95 kPa under shared Umbrella-Org MUST FAIL
            hallucinated_brief = tdir / "study_briefs" / "Repo_Alpha" / "2026-11-06_Hallucinated_Sibling.md"
            hallucinated_brief.write_text(
                alpha_brief_body.replace(
                    "extruder step pin `PB4`",
                    "extruder step pin `PB4` and UmbrellaOrg manifold pin `PF7` at 95 kPa",
                ),
                encoding="utf-8",
            )
            proc_halluc1 = subprocess.run(
                [
                    sys.executable,
                    str(TEACH_BRIEF),
                    "--verify",
                    str(hallucinated_brief),
                    "--entity",
                    "Umbrella-Org",
                    "--sources",
                    str(alpha_guide),
                    str(alpha_mem_hw),
                    str(beta_cfg),
                    str(beta_mem_hw),
                ],
                capture_output=True,
                text=True,
            )
            self.assertNotEqual(proc_halluc1.returncode, 0, "Cross-repo hallucination under shared Umbrella-Org must fail closed")
            self.assertIn("CROSS_ENTITY_BORROWING", proc_halluc1.stdout)

            # 3. Negative Hallucination Gate #2: Unattributed raw draft with --entity Umbrella-Org across sibling repos MUST FAIL
            unattributed_umb = tdir / "draft_unattributed_umbrella.md"
            unattributed_umb.write_text(
                "# System Overview\n- Sensor Pin: `PF7` rated to 95 kPa.\n",
                encoding="utf-8",
            )
            proc_halluc2 = subprocess.run(
                [
                    sys.executable,
                    str(VERIFY_CLAIMS),
                    "--target",
                    str(unattributed_umb),
                    "--entity",
                    "Umbrella-Org",
                    "--sources",
                    str(alpha_mem_hw),
                    str(beta_cfg),
                ],
                capture_output=True,
                text=True,
            )
            self.assertNotEqual(proc_halluc2.returncode, 0, "Unattributed umbrella-entity draft across sibling repos must fail closed")
            self.assertIn("CROSS_ENTITY_BORROWING", proc_halluc2.stdout)

    def test_sandbox_runner_counts_teach_brief_verification_runs(self) -> None:
        """Verify sandbox_runner telemetry & CONFLICT_TBD_RE distinguish CLI verification vs shell .py snooping."""
        if str(SANDBOX_RUNNER_DIR) not in sys.path:
            sys.path.insert(0, str(SANDBOX_RUNNER_DIR))
        import sandbox_runner  # type: ignore[import-not-found]

        sample_text = (
            "- [TBD: CONFLICT — BOM (SHCS) vs Steps 10–11 (BHCS)]\n"
            "- [TBD: CONFLICT: 1 vs 2 thrust bearings]\n"
            "- [TBD: tpu_shore_hardness]\n"
        )
        self.assertEqual(len(sandbox_runner.TBD_TAG_RE.findall(sample_text)), 3)
        self.assertEqual(len(sandbox_runner.CONFLICT_TBD_RE.findall(sample_text)), 2)

        with tempfile.TemporaryDirectory() as tmp:
            tx_path = Path(tmp) / "transcript.jsonl"
            step = {
                "type": "PLANNER_RESPONSE",
                "created_at": "2026-11-06T22:00:00Z",
                "tool_calls": [
                    {
                        "name": "run_command",
                        "args": {
                            "CommandLine": "python3 Homunculus/skills/teach-me/scripts/teach_brief.py --verify /tmp/b.md --auto-slug --sources /tmp/s.md"
                        },
                    },
                    {
                        "name": "run_command",
                        "args": {
                            "CommandLine": "sed -n '1,40p' Homunculus/skills/teach-me/scripts/teach_brief.py"
                        },
                    },
                    {
                        "name": "run_command",
                        "args": {
                            "CommandLine": "python3 -c \"print(open('Homunculus/skills/claim-verification/scripts/verify_claims.py').read()[:200])\""
                        },
                    },
                    {
                        "name": "run_command",
                        "args": {
                            "CommandLine": "python3 -c \"import os; print(os.listdir('/tmp'))\""
                        },
                    },
                ],
            }
            tx_path.write_text(json.dumps(step) + "\n", encoding="utf-8")
            tel = sandbox_runner.parse_transcript_telemetry(str(tx_path))
            self.assertEqual(tel["verification_cmds"], 1)
            self.assertEqual(tel["py_snoop_cmds"], 2)
            self.assertEqual(tel["ls_find_probes"], 1)

    def test_complexity_router_depth_gate_tier_badge_and_3d_token_safety(self) -> None:
        """Verify Solutions 1, 2, and 3 (--classify-complexity, --require-depth, --model-tier badge) + 2D/3D token safety."""
        with tempfile.TemporaryDirectory() as tmp:
            tdir = Path(tmp)
            repo_a = tdir / "Alchemical3D" / "A3DP_Gantry_Assembly"
            repo_b = tdir / "Alchemical3D" / "Homunculus"
            repo_a.mkdir(parents=True)
            repo_b.mkdir(parents=True)
            (repo_a / ".git").mkdir()
            (repo_b / ".git").mkdir()

            lic_a = repo_a / "LICENSE"
            lic_a.write_text(
                "The GNU General Public License is a free, copyleft license for software and other kinds of works.\n",
                encoding="utf-8",
            )
            lic_b = repo_b / "LICENSE.md"
            lic_b.write_text(
                "# Apache License, Version 2.0 (`Apache-2.0`)\n"
                "Copyright (c) 2026 Alchemical-3D\n"
                "Homunculus is released under `Apache-2.0`.\n",
                encoding="utf-8",
            )

            # Solution 1: Single-doc conceptual query routes to 'flash' / 'sonnet' (and clamps banned 'flash_lite')
            proc_std = subprocess.run(
                [
                    sys.executable,
                    str(TEACH_BRIEF),
                    "--classify-complexity",
                    "--subject",
                    "Apache 2.0 License",
                    "--impact-on",
                    "Open Source Distribution",
                    "--domain",
                    "software",
                    "--sources",
                    str(lic_b),
                    "--model-tier",
                    "flash_lite",
                    "--json",
                ],
                capture_output=True,
                text=True,
            )
            self.assertEqual(proc_std.returncode, 0, proc_std.stderr)
            cls_std = json.loads(proc_std.stdout)
            self.assertEqual(cls_std["complexity_tier"], "standard")
            self.assertEqual(cls_std["antigravity_model"], "flash")
            self.assertEqual(cls_std["claude_model"], "sonnet")
            self.assertEqual(cls_std["rail_badge"], "TIER: FLASH // FAST")
            self.assertIn("CLAMPED_BANNED_LITE_TO_FLASH_FLOOR", cls_std["triggers"])

            # Solution 1b: Coupled physics / cross-repo query routes to 'pro' / 'opus'
            proc_deep = subprocess.run(
                [
                    sys.executable,
                    str(TEACH_BRIEF),
                    "--classify-complexity",
                    "--subject",
                    "Stepper Inductance & Supply Voltage Torque Roll-Off",
                    "--impact-on",
                    "High-Speed Gantry Kinematics vs Resonance",
                    "--domain",
                    "electrical",
                    "--sources",
                    str(lic_a),
                    str(lic_b),
                    "--json",
                ],
                capture_output=True,
                text=True,
            )
            self.assertEqual(proc_deep.returncode, 0, proc_deep.stderr)
            cls_deep = json.loads(proc_deep.stdout)
            self.assertEqual(cls_deep["complexity_tier"], "deep")
            self.assertEqual(cls_deep["antigravity_model"], "pro")
            self.assertEqual(cls_deep["claude_model"], "opus")
            self.assertEqual(cls_deep["rail_badge"], "TIER: PRO // DEEP")

            # Solution 1c: Subject-only pneumatic/durometer/hardware query (without --sources) also routes to 'pro' / 'opus'
            proc_pneuma = subprocess.run(
                [
                    sys.executable,
                    str(TEACH_BRIEF),
                    "--classify-complexity",
                    "--subject",
                    "Dual-Pump Pneumatic Architecture, BOM Fastener/Valve Specs & TPU Shore Hardness",
                    "--impact-on",
                    "Alchemical-3D Pneuma_Remote_Air & Homunculus Apache-2.0 Distribution",
                    "--json",
                ],
                capture_output=True,
                text=True,
            )
            self.assertEqual(proc_pneuma.returncode, 0, proc_pneuma.stderr)
            cls_pneuma = json.loads(proc_pneuma.stdout)
            self.assertEqual(cls_pneuma["complexity_tier"], "deep")
            self.assertEqual(cls_pneuma["antigravity_model"], "pro")
            self.assertEqual(cls_pneuma["rail_badge"], "TIER: PRO // DEEP")

            # Solution 2: Shallow brief or banned lite tier or dropped seed source fails --require-depth
            shallow_brief = tdir / "shallow.md"
            shallow_brief.write_text(
                "---\n"
                'title: "GPL v3"\n'
                'subject: "GPL v3"\n'
                'impact_on: "Alchemical-3D"\n'
                'domain: "software"\n'
                'project: "A3DP_Gantry_Assembly"\n'
                'entity: "Alchemical-3D"\n'
                'type: "study-brief"\n'
                'status: "UNPROMOTED_STUDY_BRIEF"\n'
                "consumed_by_memory: false\n"
                'vrf_receipt: "UNVERIFIED"\n'
                'created_at: "2026-11-08"\n'
                "---\n\n"
                "# 🧠 Engineering Brief+: GPL v3 → Alchemical-3D\n\n"
                "<!-- FIRST-PRINCIPLES-THEORY:START -->\n"
                "## 1. Core Mental Model\n"
                "- Short summary.\n"
                "## 2. Relational Impact Vector\n"
                "- Short impact.\n"
                "<!-- FIRST-PRINCIPLES-THEORY:END -->\n\n"
                "## 3. Active Engineering Context Overlaps\n"
                f"- [VERIFIED FACT] The GNU General Public License is a free, copyleft license for software and other kinds of works (Source: `{lic_a}#L1-L1`).\n"
                "  Anchor:\n"
                "  ```text\n"
                "  The GNU General Public License is a free, copyleft license for software and other kinds of works.\n"
                "  ```\n\n"
                "## 4. Actionable Engineering Guardrails\n"
                "1. Retain license notices.\n",
                encoding="utf-8",
            )
            proc_shallow = subprocess.run(
                [
                    sys.executable,
                    str(TEACH_BRIEF),
                    "--verify",
                    str(shallow_brief),
                    "--require-depth",
                    "--model-tier",
                    "flash_lite",
                    "--sources",
                    str(lic_a),
                    str(lic_b),
                    "--json",
                ],
                capture_output=True,
                text=True,
            )
            self.assertNotEqual(proc_shallow.returncode, 0)
            sh_data = json.loads(proc_shallow.stdout)
            err_blob = "\n".join(sh_data["structural_errors"])
            self.assertIn("BANNED_LITE_MODEL_TIER", err_blob)
            self.assertIn("SHALLOW_THEORY_SYNTHESIS", err_blob)
            self.assertIn("INCOMPLETE_MENTAL_MODEL_PILLARS", err_blob)
            self.assertIn("MISSING_TRADEOFF_ENVELOPE_TABLE", err_blob)
            self.assertIn("UNCITED_SEED_SOURCE", err_blob)

            # Solution 3 + 2D/3D non-collision: Deep brief with both sources, Alchemical-3D in headings/prose, and --model-tier pro passes
            deep_brief = tdir / "deep.md"
            deep_brief.write_text(
                "---\n"
                'title: "GPL v3 — Impact on Alchemical-3D"\n'
                'subject: "GPL v3"\n'
                'impact_on: "Alchemical-3D"\n'
                'domain: "mechanical"\n'
                'project: "A3DP_Gantry_Assembly"\n'
                'entity: "Alchemical-3D"\n'
                'type: "study-brief"\n'
                'status: "UNPROMOTED_STUDY_BRIEF"\n'
                "consumed_by_memory: false\n"
                'vrf_receipt: "UNVERIFIED"\n'
                'created_at: "2026-11-08"\n'
                "---\n\n"
                "# 🧠 Engineering Brief+: GPL v3 → Alchemical-3D 3D CAD Releases\n\n"
                "> [!NOTE]\n"
                "> - **Domain**: mechanical | **Project Context**: A3DP_Gantry_Assembly (entity: Alchemical-3D)\n"
                "> - **Verification Receipt**: UNVERIFIED | **Source Hashes**: PENDING\n\n"
                "<!-- FIRST-PRINCIPLES-THEORY:START -->\n"
                "## 1. Core Mental Model\n"
                "- **First-Principles Mechanism**: Strong reciprocal copyleft uses copyright law to guarantee that any redistributed derivative of a covered work carries the same freedoms downstream across all recipients.\n"
                "- **Governing Scaling / System Law**: Derivative linkage propagates copyleft across combined works, whereas independent outputs generated by a tool remain separate.\n"
                "- **Key Boundary Condition**: One-way license compatibility permits merging permissive code into copyleft assemblies, never the reverse.\n\n"
                "## 2. Relational Impact Vector\n"
                "- **Causal Coupling Chain**: **GPL v3** -> *(Reciprocal source disclosure)* -> **Alchemical-3D**.\n"
                "| Parameter Shift | Primary Effect | Secondary Bottleneck | Failure Mode |\n"
                "| :--- | :--- | :--- | :--- |\n"
                "| **Increase** | Stronger community sharing | Commercial integration friction | License incompatibility |\n"
                "| **Decrease** | Permissive adoption | Proprietary forks | Missing attribution |\n"
                "<!-- FIRST-PRINCIPLES-THEORY:END -->\n\n"
                "## 3. Active Engineering Context Overlaps\n"
                "### Overlap Example 1: Copyleft in A3DP_Gantry_Assembly\n"
                f"- [VERIFIED FACT] The GNU General Public License is a free, copyleft license for software and other kinds of works (Source: `{lic_a}#L1-L1`).\n"
                "  Anchor:\n"
                "  ```text\n"
                "  The GNU General Public License is a free, copyleft license for software and other kinds of works.\n"
                "  ```\n"
                "### Overlap Example 2: Permissive Licensing in Homunculus\n"
                f"- [VERIFIED FACT] Homunculus is released under `Apache-2.0` by Alchemical-3D (Source: `{lic_b}#L2-L3`).\n"
                "  Anchor:\n"
                "  ```text\n"
                "  Copyright (c) 2026 Alchemical-3D\n"
                "  Homunculus is released under `Apache-2.0`.\n"
                "  ```\n\n"
                "## 4. Actionable Engineering Guardrails\n"
                "1. Preserve Alchemical-3D license headers across 2D and 3D engineering deliverables.\n",
                encoding="utf-8",
            )
            proc_ok = subprocess.run(
                [
                    sys.executable,
                    str(TEACH_BRIEF),
                    "--verify",
                    str(deep_brief),
                    "--briefs-root",
                    str(tdir),
                    "--require-depth",
                    "--model-tier",
                    "pro",
                    "--sources",
                    str(lic_a),
                    str(lic_b),
                    "--json",
                ],
                capture_output=True,
                text=True,
            )
            self.assertEqual(proc_ok.returncode, 0, proc_ok.stdout + proc_ok.stderr)
            self.assertFalse((tdir / "README.md").exists())
            ok_data = json.loads(proc_ok.stdout)
            self.assertEqual(ok_data["status"], "PASS")
            self.assertIn("[DOMAIN: MECHANICAL] ━━ [TIER: PRO // DEEP] ━━┓", ok_data["chat_rail_top"])
            self.assertEqual(len(ok_data["chat_rail_top"]), len(ok_data["chat_rail_bottom"]))
            self.assertLessEqual(len(ok_data["chat_rail_top"]), 80)


if __name__ == "__main__":
    unittest.main()
