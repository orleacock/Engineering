#!/usr/bin/env python3
"""Unit tests for Dual-Mode Project Memory, Separate Telemetry Functions & Multi-Customer Containment (`test_project_memory.py`)."""
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))
sys.path.insert(0, str(REPO_ROOT / "skills" / "project-memory" / "scripts"))

import sync_memory  # noqa: E402


class TestProjectMemory(unittest.TestCase):
    def test_headless_and_obsidian_mode_initialization_and_conversion(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            mem_root = Path(tmp) / "memory"
            res = sync_memory.init_memory_root(mem_root, mode="headless", default_entity="Acme_Engineering")
            self.assertEqual(res["status"], "PASS")
            self.assertTrue((mem_root / "README.md").is_file())
            self.assertTrue((mem_root / "Templates" / "Project_Hub.md").is_file())
            self.assertFalse((mem_root / "Projects" / "Projects_Directory.base").exists())

            # Convert to Obsidian mode
            conv_obs = sync_memory.convert_memory_mode(mem_root, "obsidian")
            self.assertEqual(conv_obs["converted_to"], "obsidian")
            self.assertTrue((mem_root / "Projects" / "Projects_Directory.base").is_file())

            # Convert back to Headless mode
            conv_hl = sync_memory.convert_memory_mode(mem_root, "headless")
            self.assertEqual(conv_hl["converted_to"], "headless")
            self.assertFalse((mem_root / "Projects" / "Projects_Directory.base").exists())

    def test_separate_hardware_and_software_telemetry_functions(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            mem_root = base / "memory"
            hw_repo = base / "repos" / "Mech_Bracket"
            sw_repo = base / "repos" / "CLI_Service"
            hw_repo.mkdir(parents=True)
            sw_repo.mkdir(parents=True)

            # Populate synthetic STEP (both mm-scaled and meter-scaled Onshape) + CFG in hw_repo
            (hw_repo / "bracket.step").write_text(
                "ISO-10303-21;\n"
                "#10=CARTESIAN_POINT('',(0.0,0.0,0.0));\n"
                "#11=CARTESIAN_POINT('',(40.0,25.0,10.0));\n"
                "#12=CIRCLE('',#10,1.6);\n",
                encoding="utf-8",
            )
            (hw_repo / "bracket_metre.step").write_text(
                "ISO-10303-21;\n"
                "#1=( LENGTH_UNIT() NAMED_UNIT(*) SI_UNIT($,.METRE.) );\n"
                "#10=CARTESIAN_POINT('',(0.0,0.0,0.0));\n"
                "#11=CARTESIAN_POINT('',(0.050,0.030,0.015));\n"
                "#12=CYLINDRICAL_SURFACE('',#10,0.003);\n",
                encoding="utf-8",
            )
            (hw_repo / "board.cfg").write_text(
                "[stepper_x]\nstep_pin: PA1\nrotation_distance: 40\n",
                encoding="utf-8",
            )

            # Populate synthetic Python + JSON schema in sw_repo
            (sw_repo / "app.py").write_text(
                "import argparse\n"
                "def run_service():\n"
                "    p = argparse.ArgumentParser()\n"
                "    p.add_argument('--port')\n"
                "    p.add_argument('--strict')\n",
                encoding="utf-8",
            )
            (sw_repo / "schema.json").write_text(
                json.dumps({"version": "1.0", "endpoints": []}),
                encoding="utf-8",
            )

            # 1. Onboard pure hardware project -> only _Hardware.md created
            sync_memory.init_project(
                mem_root,
                project_name="Mech_Bracket",
                repo_path=hw_repo,
                project_type="hardware",
                entity="Client_Alpha",
                compartment="private",
            )
            hw_proj_dir = mem_root / "Projects" / "Mech_Bracket"
            self.assertTrue((hw_proj_dir / "Mech_Bracket_Hardware.md").is_file())
            self.assertFalse((hw_proj_dir / "Mech_Bracket_Software.md").exists())
            self.assertTrue((hw_proj_dir / "Quarantine" / "Quarantine_README.md").is_file())
            self.assertTrue((hw_proj_dir / "Templates").is_dir())

            hw_res = sync_memory.sync_hardware_telemetry(mem_root, "Mech_Bracket", hw_repo)
            self.assertEqual(hw_res["cad_files_indexed"], 2)
            self.assertEqual(hw_res["cfg_files_indexed"], 1)
            hw_md = (hw_proj_dir / "Mech_Bracket_Hardware.md").read_text(encoding="utf-8")
            self.assertIn("40.00 x 25.00 x 10.00 mm", hw_md)
            self.assertIn("50.00 x 30.00 x 15.00 mm", hw_md)
            self.assertIn("Ø3.20mm", hw_md)
            self.assertIn("Ø6.00mm", hw_md)
            self.assertIn("step_pin", hw_md)

            # 2. Onboard pure software project -> only _Software.md created
            sync_memory.init_project(
                mem_root,
                project_name="CLI_Service",
                repo_path=sw_repo,
                project_type="software",
                entity="Client_Beta",
                compartment="cleanroom",
            )
            sw_proj_dir = mem_root / "Projects" / "CLI_Service"
            self.assertTrue((sw_proj_dir / "CLI_Service_Software.md").is_file())
            self.assertFalse((sw_proj_dir / "CLI_Service_Hardware.md").exists())

            sw_res = sync_memory.sync_software_telemetry(mem_root, "CLI_Service", sw_repo)
            self.assertEqual(sw_res["modules_indexed"], 1)
            self.assertEqual(sw_res["schemas_indexed"], 1)
            sw_md = (sw_proj_dir / "CLI_Service_Software.md").read_text(encoding="utf-8")
            self.assertIn("--port", sw_md)
            self.assertIn("run_service()", sw_md)
            self.assertIn("schema.json", sw_md)

            # 3. Verify custom project template creation
            tmpl_res = sync_memory.create_project_template(mem_root, "CLI_Service", "Release_Checklist")
            self.assertTrue(Path(tmpl_res["template_path"]).is_file())

            # 4. Verify separate per-entity Task Umbrellas, --tasks query, and clean audit
            self.assertTrue((mem_root / "Tasks" / "Client_Alpha_Tasks.md").is_file())
            self.assertTrue((mem_root / "Tasks" / "Client_Beta_Tasks.md").is_file())
            tasks_all = sync_memory.query_open_tasks(mem_root, "all")
            self.assertEqual(tasks_all["status"], "PASS")
            self.assertEqual(tasks_all["total_open"], 2)
            tasks_alpha = sync_memory.query_open_tasks(mem_root, "Client_Alpha")
            self.assertEqual(tasks_alpha["status"], "PASS")
            self.assertEqual(tasks_alpha["total_open"], 1)
            self.assertEqual(tasks_alpha["umbrellas"][0]["entity"], "Client_Alpha")

            # Verify --tbd-ledger across all projects and filtered by entity
            tbd_all = sync_memory.query_tbd_ledger(mem_root, umbrella_filter="all")
            self.assertEqual(tbd_all["status"], "PASS")
            self.assertEqual(tbd_all["projects_scanned"], 2)
            self.assertGreaterEqual(tbd_all["total_open_tbd"], 2)
            tbd_beta = sync_memory.query_tbd_ledger(mem_root, umbrella_filter="Client_Beta")
            self.assertEqual(tbd_beta["status"], "PASS")
            self.assertEqual(tbd_beta["projects_scanned"], 1)
            self.assertEqual(tbd_beta["projects"][0]["project"], "CLI_Service")

            # Verify batch --sync-trees and CLI aliases (--vault, --check)
            batch_res = sync_memory.sync_all_project_trees(mem_root)
            self.assertEqual(batch_res["status"], "PASS")
            self.assertEqual(batch_res["projects_checked"], 2)
            self.assertEqual(len(batch_res["skipped_missing_repos"]), 0)

            rc_alias = sync_memory.main(["--vault", str(mem_root), "--sync-trees", "--check", "--json"])
            self.assertEqual(rc_alias, 0)

            # Verify dynamic Obsidian Visual-Brain (.base, graph.json, and --export-canvas)
            vis_res = sync_memory.sync_obsidian_visual_brain(mem_root, export_canvas=True)
            self.assertEqual(vis_res["status"], "PASS")
            self.assertEqual(vis_res["entities_indexed"], 2)
            self.assertEqual(vis_res["projects_indexed"], 2)
            base_txt = (mem_root / "Projects" / "Projects_Directory.base").read_text(encoding="utf-8")
            self.assertIn('Entity: Client_Alpha', base_txt)
            self.assertIn('Entity: Client_Beta', base_txt)
            graph_data = json.loads((mem_root / ".obsidian" / "graph.json").read_text(encoding="utf-8"))
            self.assertTrue(any('Client_Alpha' in g["query"] for g in graph_data["colorGroups"]))
            canvas_data = json.loads(Path(vis_res["canvas_file"]).read_text(encoding="utf-8"))
            node_ids = {n["id"] for n in canvas_data["nodes"]}
            self.assertIn("grp-entity-client_alpha", node_ids)
            self.assertIn("grp-entity-client_beta", node_ids)
            self.assertIn("nd-proj-mech_bracket", node_ids)
            self.assertIn("nd-proj-cli_service", node_ids)

            audit_clean = sync_memory.audit_memory(mem_root)
            self.assertEqual(audit_clean["status"], "PASS", msg=str(audit_clean["violations"]))

            # 5. Verify Directory/ box-tree lookup files + strict multi-customer entity isolation
            dir_idx = mem_root / "Directory" / "Directory_Index.md"
            alpha_dir = mem_root / "Directory" / "Client_Alpha_Directory.md"
            beta_dir = mem_root / "Directory" / "Client_Beta_Directory.md"
            self.assertTrue(dir_idx.is_file())
            self.assertTrue(alpha_dir.is_file())
            self.assertTrue(beta_dir.is_file())
            alpha_txt = alpha_dir.read_text(encoding="utf-8")
            beta_txt = beta_dir.read_text(encoding="utf-8")
            self.assertIn("--- DIRECTORY STRUCTURE ---", alpha_txt)
            self.assertIn("├── ", alpha_txt)
            self.assertIn("Mech_Bracket", alpha_txt)
            self.assertNotIn("CLI_Service", alpha_txt)
            self.assertIn("CLI_Service", beta_txt)
            self.assertNotIn("Mech_Bracket", beta_txt)

            # Inject cross-entity link into Client_Alpha_Directory.md -> audit_memory must block
            alpha_dir.write_text(
                alpha_txt + "\nCross leak: [Beta](Client_Beta_Directory.md)\n",
                encoding="utf-8",
            )
            audit_dir_leak = sync_memory.audit_memory(mem_root)
            self.assertEqual(audit_dir_leak["status"], "FAIL")
            self.assertTrue(
                any(v["code"] == "CROSS_ENTITY_CONTAMINATION" for v in audit_dir_leak["violations"]),
                msg=str(audit_dir_leak["violations"]),
            )

    def test_multi_customer_cross_entity_contamination_and_checkbox_gates(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            mem_root = Path(tmp) / "memory"
            sync_memory.init_project(
                mem_root,
                project_name="Prod_A",
                project_type="software",
                entity="Customer_One",
                compartment="private",
            )
            sync_memory.init_project(
                mem_root,
                project_name="Prod_B",
                project_type="software",
                entity="Customer_Two",
                compartment="private",
            )

            # Inject a cross-customer link + illegal hub checkbox into Prod_A.md
            hub_a = mem_root / "Projects" / "Prod_A" / "Prod_A.md"
            text_a = hub_a.read_text(encoding="utf-8")
            text_a += (
                "\n## Illegal Cross-Customer Leak\n"
                "- [ ] Task leaked into hub dossier\n"
                "See other client spec at [Prod_B](../Prod_B/Prod_B.md).\n"
            )
            hub_a.write_text(text_a, encoding="utf-8")

            audit_res = sync_memory.audit_memory(mem_root)
            self.assertEqual(audit_res["status"], "FAIL")
            codes = {v["code"] for v in audit_res["violations"]}
            self.assertIn("CROSS_ENTITY_CONTAMINATION", codes)
            self.assertIn("CHECKBOX_IN_PROJECT_HUB", codes)

    def test_session_handoff_500_word_context_and_kickstart_drift_detection(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            mem_root = base / "memory"
            repo_dir = base / "repos" / "Core_Engine"
            repo_dir.mkdir(parents=True)
            (repo_dir / "main.py").write_text("def run():\n    return 42\n", encoding="utf-8")

            sync_memory.init_project(
                mem_root,
                project_name="Core_Engine",
                repo_path=repo_dir,
                project_type="software",
                entity="Client_One",
                compartment="cleanroom",
            )

            # Build a rich 520+ word stopping context (including accidental checkboxes to verify auto-sanitization)
            detailed_context = (
                "Completed full multi-module architecture verification across 78 files. "
                + ("Verified deterministic telemetry and cross-OS path resolution. " * 65)
                + "\n- [x] Completed unit test suite\n- [ ] Pending final README review"
            )
            save_res = sync_memory.save_session_handoff(
                mem_root,
                "Core_Engine",
                repo_override=repo_dir,
                stopped_at=detailed_context,
                receipt="SBX-20261105-01 / VRF-abcdef123456",
                blockers="[SANDBOX-PENDING-01]: Run dry-run gate before release tag.",
                next_steps="1. Finalize README.md placeholders | 2. Run claim-verification receipt gate | 3. Tag release v1.0.0",
                discussion="Confirm whether to enable Obsidian .base views by default when .obsidian/ is present.",
            )
            self.assertEqual(save_res["status"], "PASS")
            self.assertGreaterEqual(save_res["handoff_word_count"], 500)

            # Verify audit_memory passes (zero CHECKBOX_IN_PROJECT_HUB leaks despite checkboxes in input)
            audit_ok = sync_memory.audit_memory(mem_root)
            self.assertEqual(audit_ok["status"], "PASS", msg=str(audit_ok["violations"]))

            # 1. Immediate kickstart -> VERIFIED_MATCH
            kick1 = sync_memory.kickstart_project(mem_root, "Core_Engine", repo_dir)
            self.assertEqual(kick1["status"], "VERIFIED_MATCH")
            self.assertFalse(kick1["drift_detected"])
            self.assertIn("SBX-20261105-01", kick1["session_handoff"])
            self.assertIn("[DONE] Completed unit test suite", kick1["session_handoff"])

            # 2. Simulate out-of-band repository file addition between sessions -> DRIFT_DETECTED
            (repo_dir / "untracked_hotfix.py").write_text("x = 1\n", encoding="utf-8")
            kick2 = sync_memory.kickstart_project(mem_root, "Core_Engine", repo_dir)
            self.assertEqual(kick2["status"], "DRIFT_DETECTED")
            self.assertTrue(kick2["drift_detected"])
            self.assertTrue(any("TREE_HASH_CHANGED" in r for r in kick2["drift_reasons"]))

            # 3. Verify targeted section reader (--section handoff, tasks, software, all)
            sec_handoff = sync_memory.query_project_section(mem_root, "Core_Engine", "handoff")
            self.assertEqual(sec_handoff["status"], "PASS")
            self.assertIn("SBX-20261105-01", sec_handoff["content"])

            sec_tasks = sync_memory.query_project_section(mem_root, "Core_Engine", "tasks")
            self.assertEqual(sec_tasks["status"], "PASS")
            self.assertIn("Core_Engine", sec_tasks["content"])

            sec_sw = sync_memory.query_project_section(mem_root, "Core_Engine", "software")
            self.assertEqual(sec_sw["status"], "PASS")
            self.assertIn("Core_Engine_Software.md", sec_sw["source_file"])

            sec_all = sync_memory.query_project_section(mem_root, "core_engine", "all")
            self.assertEqual(sec_all["status"], "PASS")
            self.assertIn("Transcluded from Tasks/Client_One_Tasks.md#Core_Engine", sec_all["content"])


if __name__ == "__main__":
    unittest.main()
