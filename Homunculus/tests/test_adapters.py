#!/usr/bin/env python3
"""Unit tests for Harness-Agnostic Client Adapters & Context-Ignore Bindings (`test_adapters.py`)."""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))
sys.path.insert(0, str(REPO_ROOT / "skills" / "skill-architect" / "scripts"))

import audit_data_boundary  # noqa: E402
import audit_portability  # noqa: E402
import audit_skill_hygiene  # noqa: E402
import build_adapters  # noqa: E402


class TestAdapters(unittest.TestCase):
    def test_reference_repo_adapters_exist_and_contain_governing_priority_law(self) -> None:
        generated = build_adapters.build_reference_adapters_in_repo(REPO_ROOT)
        total_files = sum(len(v) for v in generated.values())
        self.assertGreaterEqual(total_files, 10)

        agents_md = REPO_ROOT / "adapters" / "agents_md" / "AGENTS.md"
        claude_md = REPO_ROOT / "adapters" / "claude_code" / "CLAUDE.md"
        claude_settings = REPO_ROOT / "adapters" / "claude_code" / "settings.json"
        agy_hooks = REPO_ROOT / "adapters" / "antigravity" / "hooks.json"
        cowork_readme = REPO_ROOT / "adapters" / "claude_cowork" / "README.md"
        cursor_rules_dir = REPO_ROOT / "adapters" / "cursor" / "rules"

        for p in (agents_md, claude_md, claude_settings, agy_hooks, cowork_readme):
            self.assertTrue(p.exists(), f"Missing generated adapter file: {p}")

        agents_text = agents_md.read_text(encoding="utf-8")
        claude_text = claude_md.read_text(encoding="utf-8")
        self.assertLessEqual(len(agents_md.read_bytes()), 22_500)
        self.assertEqual(agents_text.count("# Global Rule:"), 3)
        self.assertFalse(agents_text.startswith("---\n"))
        self.assertFalse(claude_text.startswith("---\n"))
        self.assertNotIn("trigger: always_on", agents_text)
        self.assertNotIn("trigger: always_on", claude_text)
        self.assertIn("1. Accuracy & Truth", agents_text)
        self.assertIn("2. Efficiency", agents_text)
        self.assertNotIn("2. Portability", agents_text)
        self.assertIn("addons/", agents_text)

        # Verify pre-commit.sh uses valid sync_memory.py flags (--memory-root ... --audit) and voice addon uses --workspace
        pre_commit_sh = (REPO_ROOT / "templates" / "hooks" / "pre-commit.sh").read_text(encoding="utf-8")
        self.assertIn("--memory-root", pre_commit_sh)
        self.assertIn("--audit", pre_commit_sh)
        self.assertNotIn("--vault", pre_commit_sh)

        voice_skill_path = REPO_ROOT / "addons" / "author-voice-cadence" / "SKILL.md"
        if voice_skill_path.is_file():
            voice_skill = voice_skill_path.read_text(encoding="utf-8")
            self.assertIn("build_adapters.py --workspace", voice_skill)
            self.assertNotIn("build_adapters.py --target", voice_skill)

        settings_payload = json.loads(claude_settings.read_text(encoding="utf-8"))
        self.assertEqual(settings_payload.get("hooks"), {})

        mdc_files = sorted(cursor_rules_dir.glob("homunculus-*.mdc"))
        self.assertEqual(len(mdc_files), 3)
        for mdc in mdc_files:
            content = mdc.read_text(encoding="utf-8")
            self.assertTrue(content.startswith("---\n"))
            self.assertIn("alwaysApply: true", content)
            self.assertNotIn("trigger: always_on", content)

    def test_workspace_adapter_wiring_and_git_hooks(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            ws = Path(tmp) / "workspace"
            (ws / ".git" / "hooks").mkdir(parents=True, exist_ok=True)
            # Pre-seed an older .geminiignore with a custom entry to verify non-destructive upgrade sync
            (ws / ".geminiignore").write_text("# User custom rule\ncustom_secret.dat\n.env\n", encoding="utf-8")

            result = build_adapters.apply_workspace_adapters(
                workspace_dir=ws,
                fw_root=REPO_ROOT,
                clients=list(build_adapters.SUPPORTED_CLIENTS),
                prefer_copy=True,
                install_git_hooks=True,
                package_cowork_zips=True,
            )
            self.assertGreaterEqual(result["installed_count"], 10)
            # Mutual exclusion: workspace AGENTS.md is skipped by default when antigravity is active
            self.assertFalse((ws / "AGENTS.md").exists())
            self.assertTrue((ws / "CLAUDE.md").exists())
            self.assertTrue((ws / ".claude" / "settings.json").exists())
            self.assertTrue((ws / ".cursor" / "rules" / "homunculus-co-engineering-partner.mdc").exists())
            agy_ws_rule = ws / ".agents" / "rules" / "co-engineering-partner.md"
            self.assertTrue(agy_ws_rule.exists())
            self.assertIn("trigger: always_on", agy_ws_rule.read_text(encoding="utf-8"))
            self.assertTrue((ws / ".cursorignore").exists())
            self.assertTrue((ws / ".claudeignore").exists())
            self.assertTrue((ws / ".geminiignore").exists())
            gem_ig = (ws / ".geminiignore").read_text(encoding="utf-8")
            self.assertIn("custom_secret.dat", gem_ig)
            self.assertIn("**/study_briefs/*", gem_ig)
            self.assertIn("!**/study_briefs/README.md", gem_ig)
            self.assertTrue((ws / ".homunculus_cowork_bundles" / "skill-architect.zip").exists())
            self.assertTrue((ws / ".git" / "hooks" / "pre-commit").exists())
            self.assertTrue((ws / ".git" / "hooks" / "pre-push").exists())
            self.assertTrue((ws / ".git" / "hooks" / "post-checkout").exists())
            self.assertTrue((ws / ".git" / "hooks" / "post-merge").exists())
            self.assertTrue((ws / ".git" / "hooks" / "post-rewrite").exists())

            # Explicit include_agents_md=True or standalone clients=["agents_md"] emits AGENTS.md <= 22,500 B
            build_adapters.apply_workspace_adapters(
                workspace_dir=ws,
                fw_root=REPO_ROOT,
                clients=list(build_adapters.SUPPORTED_CLIENTS),
                prefer_copy=True,
                include_agents_md=True,
            )
            self.assertTrue((ws / "AGENTS.md").exists())
            self.assertLessEqual(len((ws / "AGENTS.md").read_bytes()), 22_500)

            # Verify copied .agents/skills/*/scripts/*.py execute standalone under python3 -I
            for skill_folder, script_name in (
                ("claim-verification", "verify_claims.py"),
                ("doc-and-card-studio", "audit_repo_docs.py"),
            ):
                copied_script = ws / ".agents" / "skills" / skill_folder / "scripts" / script_name
                self.assertTrue((copied_script.parent / "homunculus_paths.py").is_file())
                proc_copied = subprocess.run(
                    [sys.executable, "-I", str(copied_script), "--help"],
                    cwd=str(ws),
                    capture_output=True,
                    text=True,
                    check=False,
                )
                self.assertEqual(proc_copied.returncode, 0, msg=proc_copied.stderr + proc_copied.stdout)

            # Verify symlinked .agents/skills/*/scripts/*.py also resolve homunculus_paths under python3 -I
            ws_sym = Path(tmp) / "workspace_symlink"
            build_adapters.apply_workspace_adapters(
                workspace_dir=ws_sym,
                fw_root=REPO_ROOT,
                clients=["antigravity"],
                prefer_copy=False,
            )
            for skill_folder, script_name in (
                ("claim-verification", "verify_claims.py"),
                ("doc-and-card-studio", "audit_repo_docs.py"),
                ("engineering-sandbox", "sandbox_runner.py"),
            ):
                sym_script = ws_sym / ".agents" / "skills" / skill_folder / "scripts" / script_name
                proc_sym = subprocess.run(
                    [sys.executable, "-I", str(sym_script), "--help"],
                    cwd=str(ws_sym),
                    capture_output=True,
                    text=True,
                    check=False,
                )
                self.assertEqual(proc_sym.returncode, 0, msg=proc_sym.stderr + proc_sym.stdout)

            # Verify extracted Cowork .zip bundles execute standalone without repo-level scripts/
            isolated_extract = Path(tmp) / "isolated_cowork"
            isolated_extract.mkdir(parents=True, exist_ok=True)
            for zip_name, script_name in (
                ("skill-architect.zip", "audit_skill_hygiene.py"),
                ("claim-verification.zip", "verify_claims.py"),
            ):
                with zipfile.ZipFile(ws / ".homunculus_cowork_bundles" / zip_name, "r") as zf:
                    zf.extractall(isolated_extract)
                skill_folder = zip_name[:-4]
                script_path = isolated_extract / skill_folder / "scripts" / script_name
                self.assertTrue((isolated_extract / skill_folder / "scripts" / "homunculus_paths.py").is_file())
                proc_zip = subprocess.run(
                    [sys.executable, "-I", str(script_path), "--help"],
                    cwd=str(isolated_extract),
                    capture_output=True,
                    text=True,
                    check=False,
                )
                self.assertEqual(proc_zip.returncode, 0, msg=proc_zip.stderr + proc_zip.stdout)

    def test_install_sh_client_and_hooks_integration(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            ws = Path(tmp) / "ws_cli"
            (ws / ".git" / "hooks").mkdir(parents=True, exist_ok=True)
            proc = subprocess.run(
                [
                    "bash",
                    str(REPO_ROOT / "install.sh"),
                    "--workspace",
                    str(ws),
                    "--client",
                    "cursor",
                    "--prefer-copy",
                    "--install-git-hooks",
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(proc.returncode, 0, msg=proc.stderr + proc.stdout)
            self.assertTrue((ws / ".homunculus.json").exists())
            self.assertTrue((ws / ".cursor" / "rules" / "homunculus-verifiable-accuracy.mdc").exists())
            self.assertTrue((ws / ".git" / "hooks" / "pre-commit").exists())

    def test_repo_portability_data_boundary_and_skill_hygiene_remain_clean(self) -> None:
        port_report = audit_portability.audit_repository(REPO_ROOT)
        self.assertEqual(port_report["status"], "PASS", msg=str(port_report.get("violations")))

        boundary_violations = audit_data_boundary.audit_worktree(REPO_ROOT, "cleanroom")
        self.assertEqual(boundary_violations, [], msg=str(boundary_violations))

        hygiene_report = audit_skill_hygiene.run_audit(
            REPO_ROOT, REPO_ROOT / "rules", REPO_ROOT / "skills"
        )
        self.assertEqual(hygiene_report["load_bearing_defects"], [], msg=str(hygiene_report["load_bearing_defects"]))
        self.assertEqual(hygiene_report["turn_waste_hazards"], [], msg=str(hygiene_report["turn_waste_hazards"]))
        self.assertEqual(hygiene_report["orphan_candidates"], [], msg=str(hygiene_report["orphan_candidates"]))

    def test_optional_addon_removal_resilience_and_cli_normalization(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            import shutil
            fw_copy = Path(tmp) / "HomunculusCopy"
            ws_copy = Path(tmp) / "ConsumerWS"
            ws_copy.mkdir(parents=True, exist_ok=True)
            shutil.copytree(REPO_ROOT / "rules", fw_copy / "rules")
            shutil.copytree(REPO_ROOT / "skills", fw_copy / "skills")
            shutil.copytree(REPO_ROOT / "scripts", fw_copy / "scripts")
            shutil.copytree(REPO_ROOT / "templates", fw_copy / "templates")
            # Intentionally omit addons/ entirely to simulate complete deletion of optional modules
            proc = subprocess.run(
                [
                    sys.executable,
                    str(fw_copy / "scripts" / "build_adapters.py"),
                    "--homunculus-root",
                    str(fw_copy),
                    "--workspace",
                    str(ws_copy),
                    "--harness",
                    "claude-code",
                    "--prefer-copy",
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(proc.returncode, 0, msg=proc.stderr + proc.stdout)
            claude_md = (ws_copy / "CLAUDE.md").read_text(encoding="utf-8")
            self.assertIn("No dormant add-ons currently installed", claude_md)
            self.assertNotIn("addons/author-voice-cadence/SKILL.md", claude_md)

            hygiene_report = audit_skill_hygiene.run_audit(
                fw_copy, fw_copy / "rules", fw_copy / "skills"
            )
            self.assertEqual(hygiene_report["load_bearing_defects"], [])

            # Verify promoting an add-on to skills/ then demoting back to addons/ prunes .agents/skills/
            sample_addon = fw_copy / "addons" / "sample-addon"
            sample_addon.mkdir(parents=True, exist_ok=True)
            (sample_addon / "SKILL.md").write_text("---\nname: sample-addon\ndescription: sample\n---\n# Sample\n", encoding="utf-8")
            shutil.copytree(sample_addon, fw_copy / "skills" / "sample-addon")
            build_adapters.apply_workspace_adapters(
                workspace_dir=ws_copy,
                fw_root=fw_copy,
                clients=["antigravity"],
                prefer_copy=True,
            )
            self.assertTrue((ws_copy / ".agents" / "skills" / "sample-addon").is_dir())
            # Demote by removing from skills/ while keeping in addons/
            shutil.rmtree(fw_copy / "skills" / "sample-addon")
            build_adapters.apply_workspace_adapters(
                workspace_dir=ws_copy,
                fw_root=fw_copy,
                clients=["antigravity"],
                prefer_copy=True,
            )
            self.assertFalse((ws_copy / ".agents" / "skills" / "sample-addon").exists())

            # Verify audit_skill_hygiene.py blocks non-functional milestone names, missing triggers, case-variant Agent.md, and >24KB rules
            bad_script = fw_copy / "scripts" / "phase_3b.py"
            bad_script.write_text("x = 1\n", encoding="utf-8")
            (fw_copy / "Agent.md").write_text("# Wrong case\n", encoding="utf-8")
            (fw_copy / "rules" / "co-engineering-partner.md").write_text(
                "# Missing trigger frontmatter\n" + ("x " * 12_500) + "\n",
                encoding="utf-8",
            )
            bad_report = audit_skill_hygiene.run_audit(fw_copy, fw_copy / "rules", fw_copy / "skills")
            defect_codes = {d["code"] for d in bad_report["load_bearing_defects"]}
            self.assertIn("NON_FUNCTIONAL_MODULE_NAME", defect_codes)
            self.assertIn("MISSING_RULE_TRIGGER_FRONTMATTER", defect_codes)
            self.assertIn("MISNAMED_AGENTS_MD_CASE", defect_codes)
            self.assertIn("RULE_BYTE_CAP_EXCEEDED", defect_codes)


if __name__ == "__main__":
    unittest.main()
