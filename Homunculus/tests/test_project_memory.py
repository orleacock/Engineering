#!/usr/bin/env python3
"""Unit tests for Dual-Mode Project Memory, Separate Telemetry Functions & Multi-Customer Containment (`test_project_memory.py`)."""
from __future__ import annotations

import json
import os
import subprocess
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

            # 2. Simulate out-of-band repository file addition between sessions -> DRIFT_DETECTED + Turn-1 Auto-Heal
            (repo_dir / "untracked_hotfix.py").write_text("x = 1\n", encoding="utf-8")
            kick2 = sync_memory.kickstart_project(mem_root, "Core_Engine", repo_dir)
            self.assertEqual(kick2["status"], "DRIFT_DETECTED")
            self.assertTrue(kick2["drift_detected"])
            self.assertTrue(any("TREE_HASH_CHANGED" in r for r in kick2["drift_reasons"]))
            self.assertIn("untracked_hotfix.py", (mem_root / "Projects" / "Core_Engine" / "Core_Engine.md").read_text(encoding="utf-8"))
            self.assertIn("untracked_hotfix.py", (mem_root / "Directory" / "Client_One_Directory.md").read_text(encoding="utf-8"))

            # 3. Verify targeted section reader (--section handoff, tasks, software, invariants, all)
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

            # 4. Verify --add-lesson, --invariants, --kickstart subsystem_invariants, and audit_memory lessons checks
            add_res = sync_memory.add_project_lesson(
                mem_root,
                "Core_Engine",
                symptom="Parser crashed on UTF-16 BOM header",
                root_cause="Opened file with strict ascii codec instead of utf-8-sig",
                guardrail="Use multi-encoding streaming decode with utf-8-sig fallback",
                anchor="[main.py](main.py)",
                subsystem="stream_decoder (`main.py`)",
                must_keep="Keep UTF-8/UTF-16 BOM detection on initial 4KB window.",
                retired_bloat="Never assume raw ASCII input files.",
            )
            self.assertEqual(add_res["status"], "PASS")
            self.assertEqual(add_res["lesson_id"], "LL-02")
            self.assertTrue(add_res["subsystem_updated"])

            inv_all = sync_memory.query_subsystem_invariants(mem_root, "Core_Engine", "all")
            self.assertEqual(inv_all["status"], "PASS")
            self.assertIn("stream_decoder", inv_all["content"])

            inv_sub = sync_memory.query_subsystem_invariants(mem_root, "Core_Engine", "stream_decoder")
            self.assertEqual(inv_sub["status"], "PASS")
            self.assertEqual(inv_sub["matched_invariants"], 1)
            self.assertIn("Keep UTF-8/UTF-16 BOM detection", inv_sub["content"])
            self.assertIn("LL-02", inv_sub["content"])

            kick3 = sync_memory.kickstart_project(mem_root, "Core_Engine", repo_dir)
            self.assertIn("stream_decoder", kick3["subsystem_invariants"])
            self.assertGreaterEqual(kick3["lessons_count"], 2)

            # Inject unpopulated stub marker into Core_Engine_Lessons_Learned.md -> audit_memory must catch
            ll_path = mem_root / "Projects" / "Core_Engine" / "Core_Engine_Lessons_Learned.md"
            orig_ll = ll_path.read_text(encoding="utf-8")
            ll_path.write_text(orig_ll + "\n| `LL-99` | *(Record first observed failure or edge case)* | x | y | z |\n", encoding="utf-8")
            audit_stub = sync_memory.audit_memory(mem_root)
            self.assertEqual(audit_stub["status"], "FAIL")
            self.assertTrue(any(v["code"] == "UNPOPULATED_LESSONS_STUB" for v in audit_stub["violations"]))
            ll_path.write_text(orig_ll, encoding="utf-8")

    def test_ensure_directory_fresh_write_if_changed_and_sandbox_skip(self) -> None:
        import os
        import subprocess
        import homunculus_paths

        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            stamp_cache = base / "stamp_cache"
            mem_root = base / "memory"
            repo_a = base / "repos" / "Alpha_App"
            repo_b = base / "repos" / "Beta_App"
            repo_a.mkdir(parents=True)
            repo_b.mkdir(parents=True)
            (repo_a / "core.py").write_text("x = 1\n", encoding="utf-8")
            (repo_b / "service.py").write_text("y = 2\n", encoding="utf-8")

            sync_memory.init_project(
                mem_root,
                project_name="Alpha_App",
                repo_path=repo_a,
                project_type="software",
                entity="Entity_Alpha",
                compartment="private",
            )
            sync_memory.init_project(
                mem_root,
                project_name="Beta_App",
                repo_path=repo_b,
                project_type="software",
                entity="Entity_Beta",
                compartment="cleanroom",
            )

            old_cache_env = os.environ.get("HOMUNCULUS_TREE_STAMP_CACHE")
            os.environ["HOMUNCULUS_TREE_STAMP_CACHE"] = str(stamp_cache)
            try:
                # 1. Initial stamp seed -> SYNCED, repeat -> FRESH_CACHED (0 disk rewrites)
                r1 = homunculus_paths.ensure_directory_fresh(
                    homunculus_root=REPO_ROOT, memory_root_override=mem_root
                )
                self.assertEqual(r1["status"], "SYNCED")

                alpha_dir_md = mem_root / "Directory" / "Entity_Alpha_Directory.md"
                beta_dir_md = mem_root / "Directory" / "Entity_Beta_Directory.md"
                mtime_before = alpha_dir_md.stat().st_mtime_ns

                r2 = homunculus_paths.ensure_directory_fresh(
                    homunculus_root=REPO_ROOT, memory_root_override=mem_root
                )
                self.assertEqual(r2["status"], "FRESH_CACHED")
                self.assertFalse(r2["synced"])
                self.assertEqual(alpha_dir_md.stat().st_mtime_ns, mtime_before)

                # 2. Pure file content edit (same filename) -> stays FRESH_CACHED & 0 directory file rewrites
                (repo_a / "core.py").write_text("x = 999\n", encoding="utf-8")
                r3 = homunculus_paths.ensure_directory_fresh(
                    homunculus_root=REPO_ROOT, memory_root_override=mem_root
                )
                self.assertEqual(r3["status"], "FRESH_CACHED")
                self.assertEqual(alpha_dir_md.stat().st_mtime_ns, mtime_before)

                # 3. Uncommitted mid-session file creation -> SYNCED & entity-isolated update
                (repo_a / "mid_session_feature.py").write_text("def feat(): pass\n", encoding="utf-8")
                r4 = homunculus_paths.ensure_directory_fresh(
                    homunculus_root=REPO_ROOT, memory_root_override=mem_root
                )
                self.assertEqual(r4["status"], "SYNCED")
                self.assertIn("mid_session_feature.py", alpha_dir_md.read_text(encoding="utf-8"))
                self.assertNotIn("mid_session_feature.py", beta_dir_md.read_text(encoding="utf-8"))

                # 4. File deletion -> removed from Directory/*.md cleanly
                (repo_a / "mid_session_feature.py").unlink()
                r5 = homunculus_paths.ensure_directory_fresh(
                    homunculus_root=REPO_ROOT, memory_root_override=mem_root
                )
                self.assertEqual(r5["status"], "SYNCED")
                self.assertNotIn("mid_session_feature.py", alpha_dir_md.read_text(encoding="utf-8"))

                # 5. Explicit opt-out (`HOMUNCULUS_DISABLE_AUTO_TREE_SYNC=1`) -> SKIPPED_DISABLED
                os.environ["HOMUNCULUS_DISABLE_AUTO_TREE_SYNC"] = "1"
                try:
                    r_sbx = homunculus_paths.ensure_directory_fresh(
                        homunculus_root=REPO_ROOT, memory_root_override=mem_root
                    )
                    self.assertEqual(r_sbx["status"], "SKIPPED_DISABLED")
                finally:
                    os.environ.pop("HOMUNCULUS_DISABLE_AUTO_TREE_SYNC", None)

                # 6. Pre-Sandbox Gate CLI (`sandbox_runner.py --prepare`) refreshes workspace trees cleanly
                homunculus_paths.write_workspace_config(base, REPO_ROOT, memory_mode="headless", memory_dir="memory")
                (repo_b / "pre_sandbox_probe.py").write_text("z = 3\n", encoding="utf-8")
                prep_proc = subprocess.run(
                    [
                        sys.executable,
                        str(REPO_ROOT / "skills" / "engineering-sandbox" / "scripts" / "sandbox_runner.py"),
                        "--prepare",
                        "--target-dir",
                        str(base),
                    ],
                    capture_output=True,
                    text=True,
                    check=False,
                )
                self.assertEqual(prep_proc.returncode, 0, msg=prep_proc.stderr + prep_proc.stdout)
                self.assertIn("[PRE_SANDBOX_GATE]", prep_proc.stdout)
                self.assertIn("pre_sandbox_probe.py", beta_dir_md.read_text(encoding="utf-8"))
            finally:
                if old_cache_env is None:
                    os.environ.pop("HOMUNCULUS_TREE_STAMP_CACHE", None)
                else:
                    os.environ["HOMUNCULUS_TREE_STAMP_CACHE"] = old_cache_env

    def test_stage1_to_3_path_resolution_and_detached_cache_mode(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            mem_root = base / "memory"
            old_ws = base / "old_station" / "AlphaRepo"
            new_ws = base / "new_station" / "AlphaRepo"
            old_ws.mkdir(parents=True)
            new_ws.mkdir(parents=True)
            (old_ws / "main.py").write_text("print('alpha')\n", encoding="utf-8")
            (new_ws / "main.py").write_text("print('alpha_new')\n", encoding="utf-8")

            sync_memory.init_memory_root(mem_root)
            sync_memory.init_project(mem_root, "AlphaRepo", old_ws, "software", "Client_Alpha", "private")

            # Stage 1: Direct station path exists
            _hub, s1_repo, _fm, s1_stage = sync_memory.resolve_project_repo_state(mem_root, "AlphaRepo")
            self.assertEqual(s1_stage, "DIRECT_STATION")
            self.assertIsNotNone(s1_repo)

            # Move repo away from old_ws so only new_ws exists under HOMUNCULUS_WORKSPACE_ROOT
            import shutil as _shutil

            _shutil.rmtree(old_ws)
            old_ws_env = os.environ.get("HOMUNCULUS_WORKSPACE_ROOT")
            try:
                os.environ["HOMUNCULUS_WORKSPACE_ROOT"] = str(base / "new_station")
                _hub, s2_repo, _fm, s2_stage = sync_memory.resolve_project_repo_state(mem_root, "AlphaRepo")
                self.assertEqual(s2_stage, "REANCHORED_WORKSPACE")
                self.assertIsNotNone(s2_repo)
                self.assertEqual(s2_repo.resolve(), new_ws.resolve())
            finally:
                if old_ws_env is None:
                    os.environ.pop("HOMUNCULUS_WORKSPACE_ROOT", None)
                else:
                    os.environ["HOMUNCULUS_WORKSPACE_ROOT"] = old_ws_env

            # Test --rebind-station dry-run followed by live rebind
            rebind_dry = sync_memory.rebind_station_paths(
                mem_root, new_workspace_root=base / "new_station", dry_run=True
            )
            self.assertEqual(len(rebind_dry["rebound_projects"]), 1)
            rebind_live = sync_memory.rebind_station_paths(
                mem_root, new_workspace_root=base / "new_station", dry_run=False
            )
            self.assertEqual(len(rebind_live["rebound_projects"]), 1)
            _hub, after_repo, _fm, after_stage = sync_memory.resolve_project_repo_state(mem_root, "AlphaRepo")
            self.assertEqual(after_stage, "DIRECT_STATION")

            # Stage 3: Remove new_ws too -> DETACHED_CACHE mode (never fabricates fake repo dir)
            _shutil.rmtree(new_ws)
            _hub, s3_repo, _fm, s3_stage = sync_memory.resolve_project_repo_state(mem_root, "AlphaRepo")
            self.assertEqual(s3_stage, "DETACHED_CACHE")
            self.assertIsNone(s3_repo)
            ks_s3 = sync_memory.kickstart_project(mem_root, "AlphaRepo")
            self.assertEqual(ks_s3["status"], "DETACHED_CACHE")
            sw_s3 = sync_memory.sync_software_telemetry(mem_root, "AlphaRepo")
            self.assertEqual(sw_s3.get("status"), "DETACHED_CACHE")

            # Inject malformed worktree tuple and verify audit catches MALFORMED_WORKTREE_TUPLE
            hub_md = mem_root / "Projects" / "AlphaRepo" / "AlphaRepo.md"
            hub_txt = hub_md.read_text(encoding="utf-8")
            hub_md.write_text(
                hub_txt.replace('checkpoint_worktree: "clean"', 'checkpoint_worktree: "(\'clean\', [])"'),
                encoding="utf-8",
            )
            aud = sync_memory.audit_memory(mem_root)
            self.assertTrue(any(v["code"] == "MALFORMED_WORKTREE_TUPLE" for v in aud["violations"]))

    def test_tier0_to_tier5_gravity_store_and_transactional_promotion_demotion(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            mem_root = base / "memory"
            repo = base / "BetaRepo"
            repo.mkdir(parents=True)
            (repo / "engine.py").write_text("def run(): pass\n", encoding="utf-8")

            sync_memory.init_memory_root(mem_root)
            self.assertTrue((mem_root / "Profile" / "Decision_Profile.md").is_file())
            sync_memory.init_project(mem_root, "BetaRepo", repo, "software", "Client_Beta", "private")

            # Add lessons across TIER0 and TIER2; verify filler scrubbing
            r1 = sync_memory.add_project_lesson(
                mem_root,
                "BetaRepo",
                symptom="Initially we thought it was fine; engine.py crashes on empty input",
                root_cause="Missing guard on empty input array",
                guardrail="Validate input array length before processing",
                anchor="[`BetaRepo.md`](BetaRepo.md)",
                subsystem="engine.py",
                must_keep="Empty input array length guard (`LL-02`)",
                retired_bloat="Unchecked array indexing",
                tier="TIER0",
            )
            self.assertEqual(r1["lesson_id"], "LL-02")
            self.assertEqual(r1["tier"], "TIER0")
            ll_path = mem_root / "Projects" / "BetaRepo" / "BetaRepo_Lessons_Learned.md"
            self.assertNotIn("Initially we thought", ll_path.read_text(encoding="utf-8"))

            # Verify TIER0 user pin immunity blocks unconfirmed demotion
            demote_blocked = sync_memory.set_lesson_tier(
                mem_root, "BetaRepo", "LL-02", "TIER3", user_confirmed=False
            )
            self.assertEqual(demote_blocked["code"], "TIER0_USER_PIN_IMMUNITY")

            # Add a mapped TIER2 lesson (LL-03) and an unmapped TIER2 lesson (LL-04)
            sync_memory.add_project_lesson(
                mem_root,
                "BetaRepo",
                symptom="Mapped bug in parser",
                root_cause="Regex greedy match",
                guardrail="Use non-greedy quantifier",
                anchor="[`BetaRepo.md`](BetaRepo.md)",
                subsystem="engine.py",
                must_keep="Non-greedy quantifier (`LL-03`)",
                tier="TIER2",
            )
            sync_memory.add_project_lesson(
                mem_root,
                "BetaRepo",
                symptom="Unmapped bug in helper",
                root_cause="Missing timeout",
                guardrail="Pass timeout=5",
                anchor="[`BetaRepo.md`](BetaRepo.md)",
                tier="TIER2",
            )

            # Compact memory (keep_tier2=0 to force graduation check):
            # LL-03 (mapped in SUBSYSTEM-INVARIANTS) graduates to TIER3 in Archive/;
            # LL-04 (unmapped) is protected via PINNED_UNMAPPED_LESSON and remains in main file;
            # LL-02 (TIER0) remains pinned in main file.
            comp = sync_memory.compact_project_lessons(mem_root, "BetaRepo", keep_tier2=0)
            self.assertIn("LL-03", comp["graduated_to_tier3"])
            self.assertIn("LL-04", comp["pinned_unmapped_lessons"])
            arch_path = mem_root / "Projects" / "BetaRepo" / "Archive" / "BetaRepo_Lessons_Archive.md"
            self.assertTrue(arch_path.is_file())
            self.assertIn("### `LL-03`", arch_path.read_text(encoding="utf-8"))
            self.assertNotIn("### `LL-03`", ll_path.read_text(encoding="utf-8"))
            self.assertIn("### `LL-02`", ll_path.read_text(encoding="utf-8"))

            # Re-promote LL-03 from TIER3 (Archive/) back to TIER2 (Main file) and verify 0 duplicates
            prom = sync_memory.set_lesson_tier(mem_root, "BetaRepo", "LL-03", "TIER2")
            self.assertEqual(prom["status"], "PASS")
            self.assertIn("### `LL-03`", ll_path.read_text(encoding="utf-8"))
            self.assertNotIn("### `LL-03`", arch_path.read_text(encoding="utf-8"))
            aud = sync_memory.audit_memory(mem_root)
            self.assertEqual(aud["violation_count"], 0, msg=str(aud["violations"]))

    def test_tier2_window_quota_and_archive_claim_verification_exclusion(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            mem_root = base / "memory"
            repo = base / "GammaRepo"
            repo.mkdir(parents=True)
            (repo / "app.py").write_text("x = 1\n", encoding="utf-8")

            sync_memory.init_memory_root(mem_root)
            sync_memory.init_project(mem_root, "GammaRepo", repo, "software", "Client_Gamma", "private")

            # Create Archive/GammaRepo_Lessons_Archive.md with historical number "9876 mm"
            arch_dir = mem_root / "Projects" / "GammaRepo" / "Archive"
            arch_dir.mkdir(parents=True, exist_ok=True)
            arch_file = arch_dir / "GammaRepo_Lessons_Archive.md"
            arch_file.write_text("# Archive\n\nRetired dimension was 9876 mm in old prototype.\n", encoding="utf-8")
            target_doc = base / "draft.md"
            target_doc.write_text("# Spec\n\nFrame width is 9876 mm.\n", encoding="utf-8")

            # Verify verify_claims.py auto-excludes *_Lessons_Archive.md so 9876 mm is caught as unbacked
            vc_proc = subprocess.run(
                [
                    sys.executable,
                    str(REPO_ROOT / "skills" / "claim-verification" / "scripts" / "verify_claims.py"),
                    "--target",
                    str(target_doc),
                    "--sources",
                    str(arch_file),
                    str(repo / "app.py"),
                    "--json",
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertNotEqual(vc_proc.returncode, 0)
            vc_json = json.loads(vc_proc.stdout)
            self.assertTrue(
                any("GammaRepo_Lessons_Archive.md" in p for p in vc_json.get("excluded_lessons_learned_sources", []))
            )

    def test_entity_partitioned_hybrid_recall_and_radar_capsules(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            mem_root = base / "memory"
            r_a = base / "RepoA"
            r_b = base / "RepoB"
            r_a.mkdir(parents=True)
            r_b.mkdir(parents=True)
            (r_a / "a.py").write_text("pass\n", encoding="utf-8")
            (r_b / "b.py").write_text("pass\n", encoding="utf-8")

            sync_memory.init_memory_root(mem_root)
            sync_memory.init_project(mem_root, "RepoA", r_a, "software", "Entity_Alpha", "private")
            sync_memory.init_project(mem_root, "RepoB", r_b, "software", "Entity_Beta", "private")

            sync_memory.add_project_lesson(
                mem_root,
                "RepoA",
                symptom="Alpha-only klipper extruder stepper microstep drift",
                root_cause="TMC2209 interpolate setting mismatch",
                guardrail="Set interpolate: False on extruder stepper",
                anchor="[a.py](a.py)",
                subsystem="a.py",
                must_keep="interpolate: False on extruder (`LL-01`)",
                tier="TIER2",
            )
            sync_memory.add_project_lesson(
                mem_root,
                "RepoB",
                symptom="Beta-only Cisco BGP AS-path prepending loop",
                root_cause="Missing route-map filter on peer",
                guardrail="Enforce prefix-list inbound filter",
                anchor="[b.py](b.py)",
                subsystem="b.py",
                must_keep="Inbound prefix-list filter (`LL-01`)",
                tier="TIER2",
            )

            # Verify entity-partitioned index files exist and have 0 cross-entity bleed
            self.assertTrue((mem_root / "Directory" / "Entity_Alpha_memory_index.json").is_file())
            self.assertTrue((mem_root / "Directory" / "Entity_Beta_memory_index.json").is_file())
            self.assertTrue((mem_root / "Directory" / "Entity_Alpha_Decision_Router.md").is_file())

            rec_alpha = sync_memory.recall_project_memory(
                mem_root, "RepoA", "Cisco BGP AS-path prepending loop"
            )
            self.assertEqual(len(rec_alpha["top_matches"]), 0)

            rec_alpha_hit = sync_memory.recall_project_memory(
                mem_root, "RepoA", "klipper extruder TMC2209 microstep"
            )
            self.assertGreaterEqual(len(rec_alpha_hit["top_matches"]), 1)
            self.assertEqual(rec_alpha_hit["top_matches"][0]["id"], "LL-02")
            self.assertLessEqual(rec_alpha_hit["packet_token_estimate"], 450)

            # On-demand --lesson-id full-context pull
            fc = sync_memory.query_lesson_by_id(mem_root, "RepoA", "LL-02")
            self.assertEqual(fc["status"], "PASS")
            self.assertIn("TMC2209 interpolate setting mismatch", fc["content"])

    def test_manual_edit_detection_and_three_signal_friction_promotion(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            mem_root = base / "memory"
            repo = base / "DeltaRepo"
            repo.mkdir(parents=True)
            (repo / "d.py").write_text("pass\n", encoding="utf-8")

            sync_memory.init_memory_root(mem_root)
            sync_memory.init_project(mem_root, "DeltaRepo", repo, "software", "Entity_Delta", "private")
            sync_memory.add_project_lesson(
                mem_root,
                "DeltaRepo",
                symptom="Archive candidate lesson for friction test",
                root_cause="Socket timeout under burst load",
                guardrail="Use exponential backoff on socket retry",
                anchor="[d.py](d.py)",
                subsystem="d.py",
                must_keep="Exponential backoff on socket retry (`LL-02`)",
                tier="TIER3",
            )

            # Passive --recall listing must NOT trigger [TIER_PROMOTION_CANDIDATE]
            for _ in range(4):
                r_passive = sync_memory.recall_project_memory(mem_root, "DeltaRepo", "socket timeout backoff")
                self.assertEqual(len(r_passive["promotion_alerts"]), 0)

            # Repeated active --lesson-id drill-downs (>= 3 hits) MUST trigger SIGNAL_1_REPEATED_DRILLDOWN
            for _ in range(3):
                sync_memory.query_lesson_by_id(mem_root, "DeltaRepo", "LL-02")
            r_active = sync_memory.recall_project_memory(mem_root, "DeltaRepo", "socket timeout backoff")
            self.assertGreaterEqual(len(r_active["promotion_alerts"]), 1)
            self.assertIn("SIGNAL_1_REPEATED_DRILLDOWN", r_active["promotion_alerts"][0])

            # Hand-edit DeltaRepo_Lessons_Learned.md outside sync_memory.py -> [MANUAL_MEMORY_EDIT_DETECTED]
            ll_file = mem_root / "Projects" / "DeltaRepo" / "DeltaRepo_Lessons_Learned.md"
            ll_file.write_text(ll_file.read_text(encoding="utf-8") + "\n<!-- manual note -->\n", encoding="utf-8")
            drift = sync_memory.check_manual_memory_edits(mem_root, "DeltaRepo")
            self.assertTrue(drift["manual_edits_detected"])
            rep = sync_memory.repair_project_memory(mem_root, "DeltaRepo")
            self.assertEqual(rep["status"], "PASS")
            drift_after = sync_memory.check_manual_memory_edits(mem_root, "DeltaRepo")
            self.assertFalse(drift_after["manual_edits_detected"])

    def test_script_contracts_json_and_unified_map_preflight_gate(self) -> None:
        contracts_path = REPO_ROOT / "scripts" / "script_contracts.json"
        self.assertTrue(contracts_path.is_file())
        contracts_data = json.loads(contracts_path.read_text(encoding="utf-8"))
        scripts_map = contracts_data.get("scripts", {})
        self.assertEqual(len(scripts_map), 14)

        # Verify hub-filtered 1-hop coupling: homunculus_paths.py is excluded from verify_claims.py 1-hop list
        vc_contract = scripts_map["verify_claims.py"]
        self.assertNotIn("scripts/homunculus_paths.py", vc_contract["coupled_functional_1hop"])
        self.assertTrue((REPO_ROOT / "templates" / "memory" / "AGENTS.md").is_file())

        # Verify sync_memory.py --preflight emits both <SCRIPT_CONTRACT> and <MEMORY_DECISION_PACKET>
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            mem_root = base / "memory"
            sync_memory.init_memory_root(mem_root)
            self.assertTrue((mem_root / "AGENTS.md").is_file())
            sync_memory.init_project(mem_root, "Homunculus", REPO_ROOT, "software", "Alchemical-3D", "private")
            pf = sync_memory.preflight_script_edit(mem_root, "Homunculus", "verify_claims.py")
            self.assertEqual(pf["status"], "PASS")
            self.assertEqual(pf["script"], "verify_claims.py")
            self.assertIn("pre_edit_blob_sha256", pf["preflight_receipt"])

    def test_governance_seal_stray_edit_protection_tier5_provenance_and_recall_precision(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            mem_root = base / "memory"
            repo = base / "OmegaRepo"
            repo.mkdir(parents=True)
            (repo / "pump_ctrl.py").write_text("def run(): pass\n", encoding="utf-8")

            sync_memory.init_memory_root(mem_root)
            gov_doc = mem_root / "Standards_and_Specs" / "Governance_and_Constraint_Architecture.md"
            gov_doc.parent.mkdir(parents=True, exist_ok=True)
            gov_doc.write_text(
                "---\ntitle: \"Governance\"\nentity: \"shared\"\n---\n\n# Governance Standard\n\nLocked rule text.\n",
                encoding="utf-8",
            )
            sync_memory.init_project(mem_root, "OmegaRepo", repo, "software", "Entity_Omega", "private")

            # 1. Add a noisy TIER0 law, an unrelated TIER2 lesson, an explicit TIER3 lesson in main, and a target TIER3 lesson
            sync_memory.add_project_lesson(
                mem_root,
                "OmegaRepo",
                symptom="General coding style law on pump_ctrl.py",
                root_cause="Missing docstring header",
                guardrail="Include module docstring header",
                anchor="[`OmegaRepo.md`](OmegaRepo.md)",
                subsystem="pump_ctrl.py",
                must_keep="Module docstring (`LL-02`) and solenoid check (`LL-04`)",
                tier="TIER0",
            )
            sync_memory.add_project_lesson(
                mem_root,
                "OmegaRepo",
                symptom="Unrelated logging format tweak on pump_ctrl.py",
                root_cause="Missing ISO timestamp",
                guardrail="Use ISO-8601 UTC timestamps",
                anchor="[`OmegaRepo.md`](OmegaRepo.md)",
                tier="TIER2",
            )
            sync_memory.add_project_lesson(
                mem_root,
                "OmegaRepo",
                lesson_id="LL-04",
                symptom="Single-pump pilot solenoid diversion valve stalls under vacuum differential",
                root_cause="Pilot diaphragm requires positive line backpressure",
                guardrail="Use dual independent diaphragm pumps instead of pilot solenoid valve",
                anchor="[`OmegaRepo.md`](OmegaRepo.md)",
                tier="TIER3",
            )

            # Verify exact TIER3 match ranks #1 instead of being drowned out by TIER0 (10x) / TIER2 (2x) noise floors
            rec = sync_memory.recall_project_memory(
                mem_root,
                "OmegaRepo",
                "single pump pilot solenoid diversion vacuum diaphragm",
                target_files=["OmegaRepo.md"],
            )
            self.assertGreaterEqual(len(rec["top_matches"]), 1)
            self.assertEqual(rec["top_matches"][0]["id"], "LL-04")

            # 2. TIER5 demotion must require a Governing Event (--user-confirmed + --reason) and stamp Retirement Provenance
            blocked_t5 = sync_memory.set_lesson_tier(mem_root, "OmegaRepo", "LL-04", "TIER5")
            self.assertEqual(blocked_t5["status"], "FAIL")
            self.assertEqual(blocked_t5["code"], "GOVERNANCE_EVENT_REQUIRED")

            ok_t5 = sync_memory.set_lesson_tier(
                mem_root,
                "OmegaRepo",
                "LL-04",
                "TIER5",
                reason="Single-pump solenoid prototype permanently retired; superseded by dual-pump design.",
                user_confirmed=True,
            )
            self.assertEqual(ok_t5["status"], "PASS")
            arch_txt = (mem_root / "Projects" / "OmegaRepo" / "Archive" / "OmegaRepo_Lessons_Archive.md").read_text(encoding="utf-8")
            self.assertIn("Retirement Provenance (`TIER5`", arch_txt)
            self.assertIn("superseded by dual-pump design", arch_txt)

            # 3. Seal governance: requires --user-confirmed + --reason, then locks Governance_and_Constraint_Architecture.md (0444)
            unconfirmed_seal = sync_memory.seal_memory_governance(mem_root, reason="", user_confirmed=False)
            self.assertEqual(unconfirmed_seal["code"], "GOVERNANCE_EVENT_REQUIRED")

            sealed = sync_memory.seal_memory_governance(
                mem_root,
                reason="Initial governance seal locking Governance_and_Constraint_Architecture.md",
                user_confirmed=True,
                lock_after=True,
            )
            self.assertEqual(sealed["status"], "PASS")
            aud_initial = sync_memory.audit_memory(mem_root)
            self.assertEqual(aud_initial["violation_count"], 0, msg=str(aud_initial["violations"]))

            if os.name != "nt":
                self.assertEqual(gov_doc.stat().st_mode & 0o222, 0)
                with self.assertRaises(PermissionError):
                    gov_doc.write_text("Bypassed!\n", encoding="utf-8")

            # 4. Simulate an attacker bypassing chmod (0644) and making a stray edit to Governance_and_Constraint_Architecture.md
            gov_doc.chmod(0o644)
            gov_doc.write_text(gov_doc.read_text(encoding="utf-8") + "\nStray unapproved rule edit.\n", encoding="utf-8")
            aud_breach = sync_memory.audit_memory(mem_root)
            self.assertEqual(aud_breach["status"], "FAIL")
            breach_codes = {v["code"] for v in aud_breach["violations"]}
            self.assertIn("MEMORY_RULE_GOVERNANCE_BREACH", breach_codes)
            if os.name != "nt":
                self.assertIn("UNLOCKED_GOVERNANCE_SURFACE", breach_codes)

            rec_breach = sync_memory.recall_project_memory(mem_root, "OmegaRepo", "timestamp")
            self.assertIn("[MEMORY_RULE_GOVERNANCE_BREACH]", rec_breach["content"])

            # Re-seal legitimately after user confirmation and verify clean PASS + 0444 re-engaged
            resealed = sync_memory.seal_memory_governance(
                mem_root,
                reason="Approved governance update",
                user_confirmed=True,
                lock_after=True,
            )
            self.assertEqual(resealed["status"], "PASS")
            aud_initial = sync_memory.audit_memory(mem_root)
            self.assertEqual(aud_initial["violation_count"], 0, msg=str(aud_initial["violations"]))

            # 5. Simulate deleting governance_seal.json while governance_audit_log.jsonl exists -> caught as breach!
            seal_path = mem_root / "Directory" / "governance_seal.json"
            seal_path.chmod(0o644)
            seal_path.unlink()
            aud_deleted_seal = sync_memory.audit_memory(mem_root)
            self.assertEqual(aud_deleted_seal["status"], "FAIL")
            self.assertTrue(any(v["code"] == "MEMORY_RULE_GOVERNANCE_BREACH" for v in aud_deleted_seal["violations"]))
            # Restore permissions for TemporaryDirectory cleanup
            sync_memory.set_memory_rules_lock_state(mem_root, lock=False)


    def test_archive_0444_protection_monotonic_tier5_seal_and_unsealed_tier_log(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            mem_root = base / "memory"
            repo = base / "SealRepo"
            repo.mkdir(parents=True)
            (repo / "ctrl.py").write_text("x = 1\n", encoding="utf-8")

            sync_memory.init_memory_root(mem_root)
            sync_memory.init_project(mem_root, "SealRepo", repo, "software", "Ent_Seal", "private")
            sync_memory.add_project_lesson(
                mem_root,
                "SealRepo",
                lesson_id="LL-SL-01",
                symptom="Legacy resistor divider drift under thermal load",
                root_cause="4700 ohm pullup mismatched ADC curve",
                guardrail="Use calibrated divider table in firmware config",
                files=["ctrl.py"],
                tier="TIER3",
            )
            arch_p = mem_root / "Projects" / "SealRepo" / "Archive" / "SealRepo_Lessons_Archive.md"
            self.assertTrue(arch_p.is_file())
            if os.name != "nt":
                self.assertEqual(arch_p.stat().st_mode & 0o222, 0)

            # Retiring to TIER5 BEFORE sealing writes governance_audit_log.jsonl; audit must NOT false-flag missing seal (F2)
            t5_res = sync_memory.set_lesson_tier(
                mem_root,
                "SealRepo",
                "LL-SL-01",
                "TIER5",
                reason="Retired 4700 ohm divider prototype; superseded by calibrated config.",
                user_confirmed=True,
            )
            self.assertEqual(t5_res["status"], "PASS")
            aud_unsealed = sync_memory.audit_memory(mem_root)
            self.assertEqual(aud_unsealed["violation_count"], 0, msg=str(aud_unsealed["violations"]))

            # Seal v1.1 and verify tampering with TIER5 Retirement Provenance is caught
            seal_res = sync_memory.seal_memory_governance(
                mem_root, reason="Seal v1.1 monotonic TIER5 test", user_confirmed=True, lock_after=True
            )
            self.assertEqual(seal_res["status"], "PASS")
            arch_p.chmod(0o644)
            arch_p.write_text(
                arch_p.read_text(encoding="utf-8").replace("Retired 4700 ohm divider", "Edited provenance"),
                encoding="utf-8",
            )
            arch_p.chmod(0o444)
            aud_tamper = sync_memory.audit_memory(mem_root)
            self.assertTrue(any(v["code"] == "MEMORY_RULE_GOVERNANCE_BREACH" for v in aud_tamper["violations"]))
            sync_memory.set_memory_rules_lock_state(mem_root, lock=False)

    def test_verify_claims_removed_allow_lessons_source_nonauth_hints_and_archive_dump_gate(self) -> None:
        vc_script = REPO_ROOT / "skills" / "claim-verification" / "scripts" / "verify_claims.py"
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            mem_root = base / "memory"
            repo = base / "HintRepo"
            repo.mkdir(parents=True)
            (repo / "spec.md").write_text("# Spec\n\nSupply voltage is 24 V.\n", encoding="utf-8")

            sync_memory.init_memory_root(mem_root)
            sync_memory.init_project(mem_root, "HintRepo", repo, "hardware", "Ent_Hint", "private")
            sync_memory.add_project_lesson(
                mem_root,
                "HintRepo",
                lesson_id="LL-HT-01",
                symptom="Retired pullup resistor caused clipping",
                root_cause="Legacy 4700 ohm resistor saturated input",
                guardrail="Never install 4700 ohm pullup",
                files=["spec.md"],
                tier="TIER3",
            )
            sync_memory.set_lesson_tier(
                mem_root, "HintRepo", "LL-HT-01", "TIER5", reason="Retired 4700 ohm spec", user_confirmed=True
            )
            sync_memory.add_project_lesson(
                mem_root,
                "HintRepo",
                lesson_id="LL-HT-02",
                symptom="Bench note observed 85 kPa line drop",
                root_cause="Unverified regulator setting at 85 kPa",
                guardrail="Verify regulator pressure before publishing",
                files=["spec.md"],
                tier="TIER2",
            )

            # 1. --allow-lessons-source flag must no longer exist (exit code 2)
            p_flag = subprocess.run(
                [sys.executable, str(vc_script), "--allow-lessons-source"],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(p_flag.returncode, 2)

            # 2. LL-* IDs pass as LITERAL_ID, while retired 4700 ohm -> RETIRED_SPEC_RESURRECTION_BLOCKED and 85 kPa -> USER_VERIFICATION_QUERY_REQUIRED
            draft = base / "audit_out.md"
            draft.write_text(
                "# Audit\n\nSupply voltage is 24 V (`LL-HT-01`, `LL-HT-02`). Pullup is 4700 ohm and line is 85 kPa.\n",
                encoding="utf-8",
            )
            p_vc = subprocess.run(
                [
                    sys.executable,
                    str(vc_script),
                    "--target",
                    str(draft),
                    "--sources",
                    str(repo / "spec.md"),
                    str(mem_root / "Projects" / "HintRepo"),
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(p_vc.returncode, 1)
            self.assertNotIn("LITERAL_ID", p_vc.stdout)
            self.assertIn("[RETIRED_SPEC_RESURRECTION_BLOCKED]", p_vc.stdout)
            self.assertIn("[USER_VERIFICATION_QUERY_REQUIRED]", p_vc.stdout)

            # 3. Transcript attestation blocks unwindowed (>30 line) Archive read_file calls
            bad_tr = base / "bad_transcript.jsonl"
            arch_file = mem_root / "Projects" / "HintRepo" / "Archive" / "HintRepo_Lessons_Archive.md"
            bad_tr.write_text(
                json.dumps(
                    {
                        "type": "PLANNER_RESPONSE",
                        "tool_calls": [
                            {"name": "read_file", "arguments": {"Path": str(arch_file)}},
                        ],
                    }
                )
                + "\n"
                + json.dumps({"type": "GENERIC", "content": "Archive contents."})
                + "\n",
                encoding="utf-8",
            )
            clean_draft = base / "clean_out.md"
            clean_draft.write_text("# Audit\n\nSupply voltage is 24 V (`LL-HT-02`).\n", encoding="utf-8")
            p_tr = subprocess.run(
                [
                    sys.executable,
                    str(vc_script),
                    "--target",
                    str(clean_draft),
                    "--sources",
                    str(repo / "spec.md"),
                    str(mem_root / "Projects" / "HintRepo"),
                    "--transcript",
                    str(bad_tr),
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertNotEqual(p_tr.returncode, 0)
            self.assertIn("ARCHIVE_RAW_DUMP_DETECTED", p_tr.stdout + p_tr.stderr)
            sync_memory.set_memory_rules_lock_state(mem_root, lock=False)

    def test_n1_non_numeric_semantic_recall_intact_ids_and_profile_b_ceiling(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            mem_root = base / "memory"
            repo = base / "RecallRepo"
            repo.mkdir(parents=True)
            (repo / "heater.py").write_text("pass\n", encoding="utf-8")

            sync_memory.init_memory_root(mem_root)
            sync_memory.init_project(mem_root, "RecallRepo", repo, "software", "Ent_Rec", "private")
            sync_memory.add_project_lesson(
                mem_root,
                "RecallRepo",
                lesson_id="LL-PTC-05",
                symptom="Thermistor ADC glitches at 115C and 15 mm harness bend",
                root_cause="Unfiltered spike on PB11 input channel",
                guardrail="Require 3 consecutive over-temp samples on PB11 before cutoff",
                files=["heater.py"],
                subsystem="HeaterSafetyLoop",
                must_keep="3-sample debounce on `PB11` (`LL-PTC-05`)",
                tier="TIER2",
            )
            sync_memory.add_project_lesson(
                mem_root,
                "RecallRepo",
                lesson_id="LL-PTC-06",
                symptom="Retired resistor value",
                root_cause="Old 4700 ohm pullup",
                guardrail="Removed old divider",
                files=["heater.py"],
                tier="TIER3",
            )
            sync_memory.set_lesson_tier(
                mem_root, "RecallRepo", "LL-PTC-06", "TIER5", reason="Retired divider", user_confirmed=True
            )

            # Coincidental number + unit query ("115 mm linear rail") must score 0 matches under N1 + F1
            r_num = sync_memory.recall_project_memory(mem_root, "RecallRepo", "115 mm linear rail")
            self.assertEqual(len(r_num["top_matches"]), 0)

            # Exact intact ID + letter-initial pin PB11 + CamelCase subsystem match cleanly under <= 600 tokens
            r_id = sync_memory.recall_project_memory(mem_root, "RecallRepo", "LL-PTC-05 PB11 HeaterSafetyLoop")
            self.assertEqual(r_id["top_matches"][0]["id"], "LL-PTC-05")
            self.assertLessEqual(r_id["packet_token_estimate"], 600)

            # TIER5 suppression emits ID only without leaking "4700"
            r_t5 = sync_memory.recall_project_memory(mem_root, "RecallRepo", "retired pullup resistor divider")
            self.assertIn("LL-PTC-06", r_t5["suppressed_tier5_ids"])
            self.assertNotIn("4700", r_t5["content"])
            sync_memory.set_memory_rules_lock_state(mem_root, lock=False)

    def test_hardware_scalar_cfg_bom_provenance_gate_and_unified_a_portable_anchors(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            mem_root = base / "memory"
            repo = base / "HwRepo"
            repo.mkdir(parents=True)
            subprocess.run(["git", "init", str(repo)], capture_output=True, check=True)
            subprocess.run(["git", "-C", str(repo), "config", "user.email", "t@example.com"], check=True)
            subprocess.run(["git", "-C", str(repo), "config", "user.name", "Tester"], check=True)
            (repo / "thermal.cfg").write_text("[heater_generic ch]\nmax_temp: 115\npullup_resistor: 10000\n", encoding="utf-8")
            (repo / "BOM.md").write_text(
                "# BOM\n\n| Item | Spec | Qty |\n| :--- | :--- | :--- |\n| Screw | M3x8 SHCS | 4 |\n",
                encoding="utf-8",
            )
            subprocess.run(["git", "-C", str(repo), "add", "."], check=True)
            subprocess.run(["git", "-C", str(repo), "commit", "-m", "Initial clean hardware spec"], capture_output=True, check=True)

            sync_memory.init_memory_root(mem_root)
            sync_memory.init_project(mem_root, "HwRepo", repo, "hardware", "Ent_Hw", "private")
            sync_memory.sync_hardware_telemetry(mem_root, "HwRepo")
            hw_txt = (mem_root / "Projects" / "HwRepo" / "HwRepo_Hardware.md").read_text(encoding="utf-8")
            self.assertIn("pullup_resistor", hw_txt)
            self.assertIn("M3x8 SHCS", hw_txt)

            # Dirty BOM.md must withhold AUTO-HARDWARE-BOM promotion
            (repo / "BOM.md").write_text("# BOM\n\n| Item | Spec | Qty |\n| :--- | :--- | :--- |\n| Screw | M3x20 SHCS | 99 |\n", encoding="utf-8")
            sync_memory.sync_hardware_telemetry(mem_root, "HwRepo")
            hw_dirty = (mem_root / "Projects" / "HwRepo" / "HwRepo_Hardware.md").read_text(encoding="utf-8")
            self.assertIn("BOM.md sync withheld", hw_dirty)
            self.assertNotIn("M3x20 SHCS", hw_dirty)

            # 3.3-Unified-A: invalid typo rejected; valid --files formatted as portable internal dual-bound anchor
            bad_f = sync_memory.add_project_lesson(
                mem_root, "HwRepo", symptom="S", root_cause="R", guardrail="G", files=["nonexistent.cfg"]
            )
            self.assertEqual(bad_f["status"], "FAIL")
            self.assertEqual(bad_f["code"], "INVALID_LESSON_FILE")

            ok_f = sync_memory.add_project_lesson(
                mem_root, "HwRepo", symptom="S", root_cause="R", guardrail="G", files=["thermal.cfg"]
            )
            self.assertEqual(ok_f["status"], "PASS")
            ll_txt = (mem_root / "Projects" / "HwRepo" / "HwRepo_Lessons_Learned.md").read_text(encoding="utf-8")
            self.assertIn("`thermal.cfg` ([`HwRepo_Hardware.md`](HwRepo_Hardware.md))", ll_txt)

    def test_option_4d_commit_lesson_gate_reinforce_lesson_and_preflight_disposition(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            mem_root = base / "memory"
            repo = base / "GateRepo"
            repo.mkdir(parents=True)
            subprocess.run(["git", "init", str(repo)], capture_output=True, check=True)
            subprocess.run(["git", "-C", str(repo), "config", "user.email", "t@example.com"], check=True)
            subprocess.run(["git", "-C", str(repo), "config", "user.name", "Tester"], check=True)
            (repo / "src").mkdir()
            (repo / "src" / "controller.py").write_text("SAFE = False\n", encoding="utf-8")
            subprocess.run(["git", "-C", str(repo), "add", "."], check=True)
            subprocess.run(["git", "-C", str(repo), "commit", "-m", "init"], capture_output=True, check=True)

            sync_memory.init_memory_root(mem_root)
            sync_memory.init_project(mem_root, "GateRepo", repo, "software", "Ent_Gate", "private")
            sync_memory.sync_software_telemetry(mem_root, "GateRepo")
            h0 = sync_memory.save_session_handoff(mem_root, "GateRepo", stopped_at="Initial baseline")
            self.assertEqual(h0["status"], "PASS")

            # Preflight src/controller.py by basename (tests disaster-recovery user-repo walk) and mutate it
            pf = sync_memory.preflight_script_edit(mem_root, "GateRepo", "controller.py")
            self.assertEqual(pf["status"], "PASS")
            (repo / "src" / "controller.py").write_text("SAFE = True\n", encoding="utf-8")

            # Audit catches UNLOGGED_PREFLIGHT_MUTATION before lesson/handoff disposition
            aud_pf = sync_memory.audit_memory(mem_root)
            self.assertTrue(any(v["code"] == "UNLOGGED_PREFLIGHT_MUTATION" for v in aud_pf["violations"]))

            subprocess.run(["git", "-C", str(repo), "add", "."], check=True)
            subprocess.run(["git", "-C", str(repo), "commit", "-m", "fix thermal runaway safety bug"], capture_output=True, check=True)
            sync_memory.sync_software_telemetry(mem_root, "GateRepo")

            # 1. Missing lesson + missing disposition -> LESSON_DISPOSITION_REQUIRED
            h_fail1 = sync_memory.save_session_handoff(mem_root, "GateRepo", stopped_at="Updated controller")
            self.assertEqual(h_fail1["code"], "LESSON_DISPOSITION_REQUIRED")

            # 2. NONE disposition on safety/bug fix commit -> DEFECT_FIX_REQUIRES_LESSON_OR_REINFORCE
            h_fail2 = sync_memory.save_session_handoff(
                mem_root, "GateRepo", stopped_at="Updated controller", lesson_disposition="NONE:minor formatting"
            )
            self.assertEqual(h_fail2["code"], "DEFECT_FIX_REQUIRES_LESSON_OR_REINFORCE")

            # 3. Log lesson -> reinforce lesson -> save handoff succeeds & clears UNLOGGED_PREFLIGHT_MUTATION
            add_ok = sync_memory.add_project_lesson(
                mem_root,
                "GateRepo",
                lesson_id="LL-GT-01",
                symptom="Controller defaulted SAFE=False on boot",
                root_cause="Uninitialized fail-safe state",
                guardrail="Initialize SAFE=True before enabling outputs",
                files=["src/controller.py"],
            )
            self.assertEqual(add_ok["status"], "PASS")
            reinf_ok = sync_memory.reinforce_project_lesson(
                mem_root,
                "GateRepo",
                "LL-GT-01",
                files=["src/controller.py"],
                retired_bloat="Booting with SAFE=False",
            )
            self.assertEqual(reinf_ok["status"], "PASS")
            self.assertEqual(reinf_ok["regression_near_misses"], 1)

            h_pass = sync_memory.save_session_handoff(mem_root, "GateRepo", stopped_at="Fixed safety boot state")
            self.assertEqual(h_pass["status"], "PASS")
            aud_clean = sync_memory.audit_memory(mem_root, verify_checkpoints=True)
            self.assertEqual(aud_clean["violation_count"], 0, msg=str(aud_clean["violations"]))

    def test_fresh_machine_sibling_group_and_homunculus_root_disaster_recovery(self) -> None:
        """User Directive #1: Fresh machine layout automatically recognizes sibling org repos and Homunculus root."""
        with tempfile.TemporaryDirectory() as tmp:
            fresh_root = Path(tmp) / "fresh_station"
            mem_root = fresh_root / "Engineering" / "memory"
            sib_repo = fresh_root / "Alchemical3D" / "Widget_Air"
            sib_repo.mkdir(parents=True)
            (sib_repo / "main.py").write_text("pass\n", encoding="utf-8")

            sync_memory.init_memory_root(mem_root)
            # Simulate a vault restored from an old crashed workstation (/old_host/Projects/Alchemical3D/Widget_Air)
            sync_memory.init_project(mem_root, "Widget_Air", sib_repo, "software", "Alchemical-3D", "public")
            hub_w = mem_root / "Projects" / "Widget_Air" / "Widget_Air.md"
            hub_w.write_text(
                sync_memory.update_frontmatter_fields(
                    hub_w.read_text(encoding="utf-8"),
                    {"local_path": "/crashed_machine/Projects/Alchemical3D/Widget_Air"},
                ),
                encoding="utf-8",
            )
            sync_memory.init_project(mem_root, "Homunculus", REPO_ROOT, "software", "Alchemical-3D", "private")
            hub_h = mem_root / "Projects" / "Homunculus" / "Homunculus.md"
            hub_h.write_text(
                sync_memory.update_frontmatter_fields(
                    hub_h.read_text(encoding="utf-8"),
                    {"local_path": "/crashed_machine/Projects/Engineering/Homunculus"},
                ),
                encoding="utf-8",
            )

            # Without any env vars, Stage 2 automatically finds both Widget_Air (via memory_root.parent.parent / parent_group)
            # and Homunculus (via HOMUNCULUS_ROOT), and validates repo-relative --files!
            _hw, rw, _fmw, st_w = sync_memory.resolve_project_repo_state(mem_root, "Widget_Air")
            self.assertEqual(st_w, "REANCHORED_WORKSPACE")
            self.assertEqual(rw.resolve(), sib_repo.resolve())

            _hh, rh, _fmh, st_h = sync_memory.resolve_project_repo_state(mem_root, "Homunculus")
            self.assertEqual(st_h, "REANCHORED_WORKSPACE")
            self.assertEqual(rh.resolve(), REPO_ROOT.resolve())

            ok_l = sync_memory.add_project_lesson(
                mem_root,
                "Homunculus",
                symptom="Disaster recovery path check",
                root_cause="Old machine absolute path no longer mounted",
                guardrail="Stage-2 re-anchoring resolves sibling org folders and HOMUNCULUS_ROOT",
                files=["scripts/homunculus_paths.py", "skills/project-memory/scripts/sync_memory.py"],
            )
            self.assertEqual(ok_l["status"], "PASS")
            aud = sync_memory.audit_memory(mem_root)
            self.assertEqual(aud["violation_count"], 0, msg=str(aud["violations"]))

    def test_option1_same_entity_sibling_recall_and_option2_activity_modifier(self) -> None:
        """Option #1 (Same-Entity Sibling Inheritance, 0% Cross-Entity Bleed) & Option #2 (Renormalization + Activity Boost)."""
        with tempfile.TemporaryDirectory() as tmp:
            mem_root = Path(tmp) / "memory"
            repo_a = Path(tmp) / "Alch_Pump"
            repo_b = Path(tmp) / "Alch_Head"
            repo_c = Path(tmp) / "Beta_Cab"
            for r in (repo_a, repo_b, repo_c):
                r.mkdir(parents=True)
                (r / "cfg.py").write_text("pass\n", encoding="utf-8")

            sync_memory.init_memory_root(mem_root)
            sync_memory.init_project(mem_root, "Alch_Pump", repo_a, "hardware", "Alchemical-3D", "public")
            sync_memory.init_project(mem_root, "Alch_Head", repo_b, "hardware", "Alchemical-3D", "public")
            sync_memory.init_project(mem_root, "Beta_Cab", repo_c, "hardware", "Client_Beta", "client")

            # Add a TIER2 lesson on Alch_Pump and reinforce it (triggers Option #2B activity_mod > 1.0)
            sync_memory.add_project_lesson(
                mem_root,
                "Alch_Pump",
                lesson_id="LL-PMP-01",
                symptom="Diaphragm pump shutdown_speed 1 blasted chamber during MCU fault",
                root_cause="Defaulting part cooling pump to full speed on emergency stop",
                guardrail="Set pump_cool shutdown_speed to 0 while keeping heater_fan at 1",
                files=["cfg.py"],
                tier="TIER2",
            )
            sync_memory.reinforce_project_lesson(
                mem_root,
                "Alch_Pump",
                "LL-PMP-01",
                files=["cfg.py"],
                retired_bloat="Setting pump_warm shutdown_speed to 1",
            )
            # Add a TIER0 pinned law on Alch_Pump (must have 0% decay / activity_mod == 1.0)
            sync_memory.add_project_lesson(
                mem_root,
                "Alch_Pump",
                lesson_id="LL-PMP-02",
                symptom="Speculative heuristic added without engineer confirmation",
                root_cause="Guessing design intent from geometry",
                guardrail="Halt and emit explicit TBD placeholder before coding heuristics",
                files=["cfg.py"],
                tier="TIER0",
            )
            # Add a lesson on Client_Beta (must NEVER bleed into Alchemical-3D)
            sync_memory.add_project_lesson(
                mem_root,
                "Beta_Cab",
                lesson_id="LL-BET-01",
                symptom="Shielded Cat6A patch panel ground loop on rack busbar",
                root_cause="Bonding both ends of drain wire to unisolated racks",
                guardrail="Bond shielded patch panels exclusively at MDF main busbar",
                files=["cfg.py"],
                tier="TIER2",
            )

            # 1. Implicit same-ecosystem recall from Alch_Head inherits LL-PMP-01 from Alch_Pump
            rec_head = sync_memory.recall_project_memory(
                mem_root,
                "Alch_Head",
                query="diaphragm pump_cool shutdown_speed heater_fan emergency stop",
            )
            self.assertTrue(
                any(m["project"] == "Alch_Pump" and m["id"] == "LL-PMP-01" and m["is_sibling"] for m in rec_head["top_matches"]),
                msg=f"Expected Alch_Head to inherit LL-PMP-01 from Alch_Pump: {rec_head['top_matches']}",
            )
            pmp01 = next(m for m in rec_head["top_matches"] if m["id"] == "LL-PMP-01")
            self.assertGreater(pmp01["activity_mod"], 1.0)
            self.assertIn("[ECOSYSTEM SIBLING: Alch_Pump]", pmp01["capsule_1line"])

            # 2. TIER0 immunity check (activity_mod == 1.0)
            rec_t0 = sync_memory.recall_project_memory(
                mem_root,
                "Alch_Pump",
                query="LL-PMP-02 speculative heuristic engineer confirmation",
            )
            pmp02 = next(m for m in rec_t0["top_matches"] if m["id"] == "LL-PMP-02")
            self.assertEqual(pmp02["activity_mod"], 1.0)

            # 3. Cross-entity firewall check: Alch_Head NEVER sees Beta_Cab, Beta_Cab NEVER sees Alch_Pump
            rec_cross1 = sync_memory.recall_project_memory(
                mem_root,
                "Alch_Head",
                query="Shielded Cat6A patch panel ground loop rack busbar Beta_Cab",
            )
            for m in rec_cross1["top_matches"]:
                self.assertNotEqual(m.get("project"), "Beta_Cab")

            rec_cross2 = sync_memory.recall_project_memory(
                mem_root,
                "Beta_Cab",
                query="Alch_Pump diaphragm pump_cool shutdown_speed heater_fan",
            )
            for m in rec_cross2["top_matches"]:
                self.assertNotIn(m.get("project"), ("Alch_Pump", "Alch_Head"))

    def test_option5b_procedural_playbooks_and_option3_prewrite_deduplication(self) -> None:
        """Option #5B (Dedicated Portable <Project>_Playbooks.md) & Option #3-Lite (Pre-Write Deduplication Gate)."""
        vc_script = REPO_ROOT / "skills" / "claim-verification" / "scripts" / "verify_claims.py"
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            mem_root = base / "memory"
            repo_pneuma = base / "Pneuma_Air"
            repo_alembic = base / "Alembic_Head"
            repo_beta = base / "Beta_Switch"
            for r in (repo_pneuma, repo_alembic, repo_beta):
                r.mkdir(parents=True)
                (r / "BOM.md").write_text("# BOM\n\n| Item | Qty |\n| :--- | :--- |\n| M3x8 SHCS | 4 |\n", encoding="utf-8")
                (r / "Assembly_Guide.md").write_text("# Assembly Guide\n\nInstall 4 M3x8 SHCS fasteners.\n", encoding="utf-8")

            sync_memory.init_memory_root(mem_root)
            sync_memory.init_project(mem_root, "Pneuma_Air", repo_pneuma, "hardware", "Alchemical-3D", "public")
            sync_memory.init_project(mem_root, "Alembic_Head", repo_alembic, "hardware", "Alchemical-3D", "public")
            sync_memory.init_project(mem_root, "Beta_Switch", repo_beta, "hardware", "Client_Beta", "cleanroom")

            pb_file = mem_root / "Projects" / "Pneuma_Air" / "Pneuma_Air_Playbooks.md"
            self.assertTrue(pb_file.is_file())

            # 1. Add a procedural playbook PB-ALCH-01 to Pneuma_Air_Playbooks.md
            pb_add = sync_memory.add_project_playbook(
                mem_root,
                "Pneuma_Air",
                playbook_id="PB-ALCH-01",
                trigger="Hardware repository unification, CAD/firmware/BOM reconciliation, and dual-lesson reinforcement",
                steps=(
                    "1. Run inspect_hardware_ecosystem.py and audit_repo_docs.py on the target repository. "
                    "2. Reconcile BOM.md and Assembly_Guide.md fastener tables against primary CAD/CFG telemetry. "
                    "3. Run verify_claims.py across all authored Markdown docs and reinforce domain + Homunculus lessons."
                ),
                verification_gate="verify_claims.py exit 0 (VRF receipt) + audit_repo_docs.py 0 defects + sync_memory.py --audit PASS",
                files=["BOM.md", "Assembly_Guide.md"],
                tier="TIER2",
            )
            self.assertEqual(pb_add["status"], "PASS")
            self.assertEqual(pb_add["playbook_id"], "PB-ALCH-01")

            # 2. #3-Lite: Near-duplicate --add-playbook is blocked and redirected to --update-playbook
            pb_dup = sync_memory.add_project_playbook(
                mem_root,
                "Pneuma_Air",
                trigger="Hardware repository unification, CAD/firmware/BOM reconciliation, and dual-lesson reinforcement",
                steps=(
                    "1. Run inspect_hardware_ecosystem.py and audit_repo_docs.py on the target repository. "
                    "2. Reconcile BOM.md and Assembly_Guide.md fastener tables against primary CAD/CFG telemetry. "
                    "3. Run verify_claims.py across all authored Markdown docs and reinforce domain + Homunculus lessons."
                ),
                verification_gate="verify_claims.py exit 0 + audit_repo_docs.py 0 defects + sync_memory.py --audit PASS",
                files=["BOM.md"],
            )
            self.assertEqual(pb_dup["status"], "FAIL")
            self.assertEqual(pb_dup["code"], "NEAR_DUPLICATE_PLAYBOOK_DETECTED")
            self.assertEqual(pb_dup["matched_playbook_id"], "PB-ALCH-01")

            # 3. Updating PB-ALCH-01 in place via update_project_playbook succeeds without duplicating sections
            pb_upd = sync_memory.update_project_playbook(
                mem_root,
                "Pneuma_Air",
                playbook_id="PB-ALCH-01",
                verification_gate="verify_claims.py exit 0 + audit_repo_docs.py 0 defects + pre-commit-gate Stage X/Y/Z PASS",
                files=["BOM.md", "Assembly_Guide.md"],
            )
            self.assertEqual(pb_upd["status"], "PASS")
            self.assertEqual(pb_upd["regression_near_misses"], 1)

            # 4. #3-Lite: Near-duplicate --add-lesson is blocked and redirected to --reinforce-lesson
            ll1 = sync_memory.add_project_lesson(
                mem_root,
                "Pneuma_Air",
                lesson_id="LL-PNM-02",
                symptom="Press-fit manifold barb leaks 140 kPa air under continuous thermal cycling",
                root_cause="Uncaptured silicone tubing creeps off smooth printed resin barb",
                guardrail="Use threaded M5 push-to-connect bulkhead fittings instead of printed barbs",
                files=["BOM.md"],
                tier="TIER2",
            )
            self.assertEqual(ll1["status"], "PASS")
            ll_dup = sync_memory.add_project_lesson(
                mem_root,
                "Pneuma_Air",
                symptom="Press-fit manifold barb leaks 140 kPa air under continuous thermal cycling",
                root_cause="Uncaptured silicone tubing creeps off smooth printed resin barb",
                guardrail="Use threaded M5 push-to-connect bulkhead fittings instead of printed barbs",
                files=["BOM.md"],
                tier="TIER2",
            )
            self.assertEqual(ll_dup["status"], "FAIL")
            self.assertEqual(ll_dup["code"], "NEAR_DUPLICATE_LESSON_DETECTED")
            self.assertEqual(ll_dup["matched_lesson_id"], "LL-PNM-02")

            # 5. Same-ecosystem sibling recall (Option #1 + Option #5B): Alembic_Head inherits PB-ALCH-01 from Pneuma_Air
            rec_alembic = sync_memory.recall_project_memory(
                mem_root,
                "Alembic_Head",
                query="hardware repository unification CAD firmware BOM reconciliation workflow",
            )
            self.assertTrue(
                any(m["id"] == "PB-ALCH-01" and m["project"] == "Pneuma_Air" and m["is_sibling"] for m in rec_alembic["top_matches"]),
                msg=f"Expected Alembic_Head to inherit PB-ALCH-01: {rec_alembic['top_matches']}",
            )
            pb_cap = next(m for m in rec_alembic["top_matches"] if m["id"] == "PB-ALCH-01")["capsule_1line"]
            self.assertIn("[ECOSYSTEM SIBLING: Pneuma_Air]", pb_cap)
            self.assertIn("[PLAYBOOK]", pb_cap)
            self.assertIn("[LEDGER_MEMORY_LINE]:", rec_alembic["content"])
            self.assertIn("[SIBLING:Pneuma_Air] PB-ALCH-01", rec_alembic["ledger_memory_line"])

            # 6. On-demand --playbook-id drill-down works from both Pneuma_Air and sibling Alembic_Head, but is blocked from Client_Beta
            dd_alembic = sync_memory.query_lesson_by_id(mem_root, "Alembic_Head", "PB-ALCH-01")
            self.assertEqual(dd_alembic["status"], "PASS")
            self.assertIn("Ordered Execution Procedure:", dd_alembic["content"])
            self.assertIn("pre-commit-gate Stage X/Y/Z PASS", dd_alembic["content"])

            dd_beta = sync_memory.query_lesson_by_id(mem_root, "Beta_Switch", "PB-ALCH-01")
            self.assertEqual(dd_beta["status"], "FAIL")

            # 7. verify_claims.py excludes *_Playbooks.md as a quantitative truth source while whitelisting PB-* IDs
            draft_pb = base / "draft_pb.md"
            draft_pb.write_text("# Report\n\nExecuted workflow `PB-ALCH-01` using 4 M3x8 SHCS screws.\n", encoding="utf-8")
            p_vc = subprocess.run(
                [
                    sys.executable,
                    str(vc_script),
                    "--target",
                    str(draft_pb),
                    "--sources",
                    str(repo_pneuma / "BOM.md"),
                    str(pb_file),
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(p_vc.returncode, 0, msg=p_vc.stdout + p_vc.stderr)

            aud = sync_memory.audit_memory(mem_root)
            self.assertEqual(aud["violation_count"], 0, msg=str(aud["violations"]))


if __name__ == "__main__":
    unittest.main()
