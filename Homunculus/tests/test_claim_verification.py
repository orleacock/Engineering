#!/usr/bin/env python3
"""Unit and integration tests for Claim Verification & Multi-Entity Anti-Hallucination (`claim-verification`).

Verifies:
  1. `verify_claims.py` positive `VRF-<12hex>` receipt generation, unbacked claim detection, and Quarantine Zone exclusion
  2. Cross-script `sync_memory.py` + `inspect_hardware_ecosystem.py` + `verify_claims.py` containment and speculative-trait blocking
  3. Multi-domain `QUALIFIER_GROUPS` (`nozzle`, `pulley`, `standoff`, `heater`, `fuse`, `pullup`) and unspecified-clause suppression
  4. Unattributed umbrella-entity (`--entity Umbrella-Org`) cross-repository smuggling block (`CROSS_ENTITY_BORROWING`)
Requires ONLY Python 3.10+ standard library.
"""
from __future__ import annotations

from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

REPO_ROOT = Path(__file__).resolve().parent.parent
VERIFY_CLAIMS = REPO_ROOT / "skills/claim-verification/scripts/verify_claims.py"
INSPECT_HW = REPO_ROOT / "skills/subagent-orchestrator/scripts/inspect_hardware_ecosystem.py"
SYNC_MEMORY = REPO_ROOT / "skills/project-memory/scripts/sync_memory.py"


class TestClaimVerification(unittest.TestCase):
    def test_verify_claims_pass_unbacked_and_quarantine(self) -> None:
        """Tests verify_claims.py positive VRF pass, unbacked claim detection, and Quarantine Zone exclusion."""
        with tempfile.TemporaryDirectory() as tmp:
            tdir = Path(tmp)
            src_md = tdir / "Project_Alpha_Hardware.md"
            src_md.write_text(
                "---\nentity: Client_Alpha\nproject: Project_Alpha\n---\n"
                "# Alpha Hardware Specs\n"
                "- Fasteners: 4x M3x16 SHCS\n"
                "- Supply Voltage: 24 V\n"
                "- Bore Diameter: 12.5 mm\n"
                "<!-- QUARANTINE-ZONE:START -->\n"
                "- Unverified Rumor: 999 kPa pressure\n"
                "<!-- QUARANTINE-ZONE:END -->\n",
                encoding="utf-8",
            )

            # 1. Valid target backed by source -> exit 0 + VRF receipt
            good_target = tdir / "README_good.md"
            good_target.write_text(
                "# Alpha Assembly\nMount the bracket using 4x M3x16 SHCS and connect the 24 V supply to the 12.5 mm bore housing.\n",
                encoding="utf-8",
            )
            proc_ok = subprocess.run(
                [sys.executable, str(VERIFY_CLAIMS), "--target", str(good_target), "--sources", str(src_md)],
                capture_output=True,
                text=True,
            )
            self.assertEqual(proc_ok.returncode, 0, proc_ok.stdout + proc_ok.stderr)
            self.assertRegex(proc_ok.stdout, r"VRF-[0-9a-fA-F]{12}")

            # 2. Target citing quarantined 999 kPa -> must FAIL (exit 1) because Quarantine HTML zone is stripped
            bad_quarantine_target = tdir / "README_quarantined_num.md"
            bad_quarantine_target.write_text(
                "# Alpha Assembly\nOperating at 999 kPa pressure.\n",
                encoding="utf-8",
            )
            proc_q = subprocess.run(
                [sys.executable, str(VERIFY_CLAIMS), "--target", str(bad_quarantine_target), "--sources", str(src_md)],
                capture_output=True,
                text=True,
            )
            self.assertEqual(proc_q.returncode, 1, "Quarantined number 999 kPa should not whitelist target claim!")
            self.assertIn("999 kPa", proc_q.stdout)

            # 3. Source file inside Quarantine/ folder -> rejected with QUARANTINE_SOURCE_REJECTED
            q_folder = tdir / "Quarantine"
            q_folder.mkdir()
            q_file = q_folder / "unverified_notes.md"
            q_file.write_text("Spec: 500 mm travel\n", encoding="utf-8")
            proc_qdir = subprocess.run(
                [sys.executable, str(VERIFY_CLAIMS), "--target", str(good_target), "--sources", str(q_file)],
                capture_output=True,
                text=True,
            )
            self.assertNotEqual(proc_qdir.returncode, 0)
            self.assertIn("QUARANTINE_SOURCE_REJECTED", proc_qdir.stdout + proc_qdir.stderr)

            # 4. Backward-compatible aliases (--require-anchors, --require-git-clean-sources, --project-dir)
            proc_alias = subprocess.run(
                [
                    sys.executable,
                    str(VERIFY_CLAIMS),
                    "--target",
                    str(good_target),
                    "--sources",
                    str(src_md),
                    "--project-dir",
                    str(tdir),
                    "--require-anchors",
                    "--require-git-clean-sources",
                ],
                capture_output=True,
                text=True,
            )
            self.assertEqual(proc_alias.returncode, 0, proc_alias.stdout + proc_alias.stderr)

    def test_cross_script_memory_verify_claims_and_hardware_sync(self) -> None:
        """Tests cross-script interactions between sync_memory, inspect_hardware_ecosystem, and verify_claims."""
        with tempfile.TemporaryDirectory() as tmp:
            tdir = Path(tmp)
            mem_root = tdir / "memory"
            alpha_repo = tdir / "repos" / "Actuator_Module"
            beta_repo = tdir / "repos" / "Telemetry_Router"
            alpha_repo.mkdir(parents=True)
            beta_repo.mkdir(parents=True)

            # Create STEP (no LENGTH_UNIT, mm coordinates 85x60x32.5 + CIRCLE bores) and CFG (step_pin/dir_pin)
            (alpha_repo / "actuator_housing.step").write_text(
                "ISO-10303-21;\nHEADER;\n"
                "FILE_NAME('actuator_housing.step','2026-11-05T08:00:00',(''),(''),'Onshape','','');\n"
                "ENDSEC;\nDATA;\n"
                "#1=PRODUCT('actuator_housing','actuator_housing','',(#2));\n"
                "#10=CARTESIAN_POINT('',(0.0,0.0,0.0));\n"
                "#11=CARTESIAN_POINT('',(85.0,60.0,32.5));\n"
                "#20=CIRCLE('',#21,1.6);\n"
                "#22=CIRCLE('',#23,2.5);\n"
                "ENDSEC;\nEND-ISO-10303-21;\n",
                encoding="utf-8",
            )
            (alpha_repo / "actuator.cfg").write_text(
                "[stepper_x]\nstep_pin: PB4\ndir_pin: PB5\n[fan_generic cooling_blower]\npin: PA8\n",
                encoding="utf-8",
            )
            (beta_repo / "router.py").write_text("WORKERS = 4\nPORTS = 8\n", encoding="utf-8")

            # Initialize memory and onboard both projects under distinct entities
            subprocess.run(
                [sys.executable, str(SYNC_MEMORY), "--init-memory", "--memory-root", str(mem_root), "--mode", "headless"],
                check=True,
                capture_output=True,
                text=True,
            )
            subprocess.run(
                [
                    sys.executable,
                    str(SYNC_MEMORY),
                    "--memory-root",
                    str(mem_root),
                    "--init-project",
                    "Actuator_Module",
                    "--repo-path",
                    str(alpha_repo),
                    "--entity",
                    "Client_Alpha",
                    "--type",
                    "hardware",
                ],
                check=True,
                capture_output=True,
                text=True,
            )
            subprocess.run(
                [
                    sys.executable,
                    str(SYNC_MEMORY),
                    "--memory-root",
                    str(mem_root),
                    "--init-project",
                    "Telemetry_Router",
                    "--repo-path",
                    str(beta_repo),
                    "--entity",
                    "Client_Beta",
                    "--type",
                    "software",
                ],
                check=True,
                capture_output=True,
                text=True,
            )

            # Populate Section 3 Verified Fasteners in Actuator_Module_Hardware.md
            hw_md = mem_root / "Projects/Actuator_Module/Actuator_Module_Hardware.md"
            hw_txt = hw_md.read_text(encoding="utf-8")
            hw_txt = hw_txt.replace(
                "| `[TBD: sub_assembly]` | `[TBD: fastener_spec]` | `[TBD: qty]` | `[TBD: source_anchor]` | Populate from verified CAD/BOM sources only. |",
                "| Housing | 6x M3x12 SHCS | 6 | `actuator.cfg#L1-L5` | Verified housing fastener schedule. |",
            )
            hw_md.write_text(hw_txt, encoding="utf-8")

            # Run inspect_hardware_ecosystem.py --sync-manifest using relative local_path from a different cwd
            proc_hw = subprocess.run(
                [
                    sys.executable,
                    str(INSPECT_HW),
                    "--memory-root",
                    str(mem_root),
                    "--project",
                    "Actuator_Module",
                    "--sync-manifest",
                ],
                cwd=str(tdir),
                capture_output=True,
                text=True,
            )
            self.assertEqual(proc_hw.returncode, 0, proc_hw.stdout + proc_hw.stderr)
            synced_hw = hw_md.read_text(encoding="utf-8")
            self.assertIn("6x M3x12 SHCS", synced_hw)
            self.assertIn("32.50 × 60.00 × 85.00", synced_hw)
            self.assertIn("Ø3.20mm", synced_hw)
            self.assertIn("`PB4`", synced_hw)
            self.assertIn("`PB5`", synced_hw)
            self.assertNotIn("[[", synced_hw)

            # Save a SESSION-HANDOFF note containing an unverified preliminary discussion spec (4x M3x8 BHCS)
            subprocess.run(
                [
                    sys.executable,
                    str(SYNC_MEMORY),
                    "--memory-root",
                    str(mem_root),
                    "--project",
                    "Actuator_Module",
                    "--save-handoff",
                    "--stopped-at",
                    "Discussed preliminary 4x M3x8 BHCS and 95 kPa test pressure.",
                ],
                check=True,
                capture_output=True,
                text=True,
            )
            beta_md = mem_root / "Projects/Telemetry_Router/Telemetry_Router.md"
            beta_md.write_text(
                beta_md.read_text(encoding="utf-8") + "\n## Verified Router Specs\n- Concurrency: 4 workers across 8 ports.\n",
                encoding="utf-8",
            )

            alpha_hub = mem_root / "Projects/Actuator_Module/Actuator_Module.md"

            # Draft claiming 95 kPa or 4x M3x8 BHCS from SESSION-HANDOFF must FAIL verify_claims.py
            bad_handoff_draft = tdir / "draft_handoff_leak.md"
            bad_handoff_draft.write_text(
                "# Actuator Spec\n- Pressure: 95 kPa\n- Fasteners: 4x M3x8 BHCS\n",
                encoding="utf-8",
            )
            proc_handoff = subprocess.run(
                [
                    sys.executable,
                    str(VERIFY_CLAIMS),
                    "--target",
                    str(bad_handoff_draft),
                    "--sources",
                    str(alpha_hub),
                    str(hw_md),
                    "--entity",
                    "Client_Alpha",
                ],
                capture_output=True,
                text=True,
            )
            self.assertNotEqual(proc_handoff.returncode, 0, "SESSION-HANDOFF specs must not enter verified whitelist")

            # Draft for Client_Alpha borrowing Client_Beta's '4 workers' / '8 ports' must FAIL with CROSS_ENTITY_BORROWING
            bad_cross_draft = tdir / "draft_cross_entity.md"
            bad_cross_draft.write_text(
                "# Actuator Spec\n- Housing Fasteners: 6x M3x12 SHCS\n- Controller: 4 workers across 8 ports\n",
                encoding="utf-8",
            )
            proc_cross = subprocess.run(
                [
                    sys.executable,
                    str(VERIFY_CLAIMS),
                    "--target",
                    str(bad_cross_draft),
                    "--sources",
                    str(alpha_hub),
                    str(hw_md),
                    str(beta_md),
                    "--entity",
                    "Client_Alpha",
                ],
                capture_output=True,
                text=True,
            )
            self.assertNotEqual(proc_cross.returncode, 0, "Cross-entity counted nouns must be blocked")
            self.assertIn("CROSS_ENTITY_BORROWING", proc_cross.stdout)

            # Clean Client_Alpha draft quoting `actuator.cfg#L1-L5` from _Hardware.md must PASS
            clean_alpha_draft = tdir / "draft_clean_alpha.md"
            clean_alpha_draft.write_text(
                "# Actuator Spec\n"
                "- Housing Envelope: 32.50 × 60.00 × 85.00 mm\n"
                "- Housing Fasteners: 6x M3x12 SHCS\n"
                "- Stepper Pins: `PB4`, `PB5` (`actuator.cfg#L1-L5`)\n",
                encoding="utf-8",
            )
            proc_clean_alpha = subprocess.run(
                [
                    sys.executable,
                    str(VERIFY_CLAIMS),
                    "--target",
                    str(clean_alpha_draft),
                    "--sources",
                    str(alpha_hub),
                    str(hw_md),
                    str(beta_md),
                    "--entity",
                    "Client_Alpha",
                ],
                capture_output=True,
                text=True,
            )
            self.assertEqual(proc_clean_alpha.returncode, 0, proc_clean_alpha.stdout + proc_clean_alpha.stderr)
            self.assertIn("VRF-", proc_clean_alpha.stdout)

            # Speculative COTS trait ('3.20mm Magnet' or '2x bearings') against bare Ø3.20mm bore must FAIL
            speculative_draft = tdir / "draft_speculative_magnet.md"
            speculative_draft.write_text(
                "# Actuator Spec\n"
                "- Bore Feature: 4x 3.20mm Magnet pockets and 2x bearings.\n",
                encoding="utf-8",
            )
            proc_speculative = subprocess.run(
                [
                    sys.executable,
                    str(VERIFY_CLAIMS),
                    "--target",
                    str(speculative_draft),
                    "--sources",
                    str(alpha_hub),
                    str(hw_md),
                    "--entity",
                    "Client_Alpha",
                ],
                capture_output=True,
                text=True,
            )
            self.assertNotEqual(proc_speculative.returncode, 0, "Speculative COTS traits must be blocked")
            self.assertIn("QUALIFIED_QUANTITY(MAGNET)", proc_speculative.stdout)
            self.assertIn("COUNTED_ENTITY(BEARING)", proc_speculative.stdout)

            # Expanded multi-domain qualifiers + negation/unspecified clause suppression + backticked Ø quantities
            rig_src = tdir / "rig_telemetry.md"
            rig_src.write_text(
                "# Rig Telemetry\n"
                "- Cylindrical Surfaces: `Ø0.40mm×1, Ø5.00mm×2, Ø6.00mm×4`\n"
                "- Channel A Power Output: `60 W`\n"
                "- Channel B Sense Resistance: `4.7 kΩ` (raw sense channel — pull-up/pull-down topology not specified)\n"
                "- Channel C Protection Rating: `5 A`\n"
                "- Specific thermal element type for the `60 W` channel (`heater cartridge` vs. `silicone pad`) is not specified.\n"
                "- Specific overcurrent device type for the `5 A` rating (`fuse` vs. `breaker`) is not specified.\n",
                encoding="utf-8",
            )
            good_rig_draft = tdir / "good_rig_draft.md"
            good_rig_draft.write_text(
                "# Rig Summary\n"
                "- Cylindrical feature: `Ø0.40 mm × 1`, `Ø5.00 mm`, `Ø6.00 mm`\n"
                "- Power: `60 W`\n"
                "- Sense: `4.7 kΩ` (Pull-up vs. pull-down resistor topology for `4.7 kΩ` is not specified.)\n"
                "- Rating: `5 A`\n",
                encoding="utf-8",
            )
            proc_good_rig = subprocess.run(
                [sys.executable, str(VERIFY_CLAIMS), "--target", str(good_rig_draft), "--sources", str(rig_src)],
                capture_output=True,
                text=True,
            )
            self.assertEqual(proc_good_rig.returncode, 0, proc_good_rig.stdout + proc_good_rig.stderr)

            bad_rig_draft = tdir / "bad_rig_draft.md"
            bad_rig_draft.write_text(
                "# Rig Summary\n"
                "- Fitted with a 0.40mm nozzle, 5.00mm pulley, and 6.00mm standoffs.\n"
                "- Driven by a 60W heater cartridge, protected by a 5A fuse, and uses a 4.7 kΩ pull-up resistor.\n",
                encoding="utf-8",
            )
            proc_bad_rig = subprocess.run(
                [sys.executable, str(VERIFY_CLAIMS), "--target", str(bad_rig_draft), "--sources", str(rig_src)],
                capture_output=True,
                text=True,
            )
            self.assertNotEqual(proc_bad_rig.returncode, 0)
            for expected_tag in (
                "QUALIFIED_QUANTITY(NOZZLE)",
                "QUALIFIED_QUANTITY(PULLEY)",
                "QUALIFIED_QUANTITY(STANDOFF)",
                "QUALIFIED_QUANTITY(HEATER)",
                "QUALIFIED_QUANTITY(FUSE)",
                "QUALIFIED_QUANTITY(PULLUP)",
            ):
                self.assertIn(expected_tag, proc_bad_rig.stdout)


if __name__ == "__main__":
    unittest.main()
