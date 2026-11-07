#!/usr/bin/env python3
"""Unit and integration tests for Homunculus Foundation (`test_foundation.py`).

Tests Cross-OS path resolution (1. Linux -> 2. macOS -> 3. Windows),
Headless vs. Obsidian memory mode detection, Visual Studio always-on invariant,
and clean-room audit_portability.py verification.
Requires ONLY Python 3.10+ standard library.
"""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import audit_portability  # noqa: E402
import homunculus_paths  # noqa: E402


class TestFoundation(unittest.TestCase):
    def test_os_priority_order_linux_macos_windows(self) -> None:
        linux_meta = homunculus_paths.detect_os_tier("linux")
        macos_meta = homunculus_paths.detect_os_tier("darwin")
        win_meta = homunculus_paths.detect_os_tier("win32")

        self.assertEqual(linux_meta["os_id"], "linux")
        self.assertEqual(linux_meta["priority_order"], 1)
        self.assertEqual(macos_meta["os_id"], "macos")
        self.assertEqual(macos_meta["priority_order"], 2)
        self.assertEqual(win_meta["os_id"], "windows")
        self.assertEqual(win_meta["priority_order"], 3)
        self.assertLess(linux_meta["priority_order"], macos_meta["priority_order"])
        self.assertLess(macos_meta["priority_order"], win_meta["priority_order"])

    def test_headless_vs_obsidian_and_visual_studio_invariant(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            ws = Path(tmp_dir)
            # Default drop-in without .obsidian -> headless mode, Visual Studio still active
            cfg_headless = homunculus_paths.resolve_workspace_config(workspace_dir=ws, homunculus_root=REPO_ROOT)
            self.assertEqual(cfg_headless["deployment_mode"], "drop_in")
            self.assertEqual(cfg_headless["memory_mode"], "headless")
            self.assertTrue(cfg_headless["visual_studio_enabled"])
            self.assertFalse(cfg_headless["obsidian_ui_surfaces_enabled"])

            # Auto-detect .obsidian directory -> obsidian mode, Visual Studio still active
            (ws / "memory" / ".obsidian").mkdir(parents=True)
            cfg_obs = homunculus_paths.resolve_workspace_config(workspace_dir=ws, homunculus_root=REPO_ROOT)
            self.assertEqual(cfg_obs["memory_mode"], "obsidian")
            self.assertTrue(cfg_obs["visual_studio_enabled"])
            self.assertTrue(cfg_obs["obsidian_ui_surfaces_enabled"])

            # Explicit .homunculus.json overrides auto-detection
            homunculus_paths.write_workspace_config(workspace_dir=ws, homunculus_root=REPO_ROOT, memory_mode="headless")
            cfg_explicit = homunculus_paths.resolve_workspace_config(workspace_dir=ws, homunculus_root=REPO_ROOT)
            self.assertEqual(cfg_explicit["deployment_mode"], "configured")
            self.assertEqual(cfg_explicit["memory_mode"], "headless")
            self.assertTrue(cfg_explicit["visual_studio_enabled"])

    def test_live_repository_passes_cleanroom_portability_gate(self) -> None:
        report = audit_portability.audit_repository(REPO_ROOT)
        self.assertEqual(report["status"], "PASS", f"Unexpected violations: {report['violations']}")
        self.assertEqual(report["violation_count"], 0)

    def test_install_sh_check_and_dry_run(self) -> None:
        install_sh = REPO_ROOT / "install.sh"
        res_check = subprocess.run(
            ["bash", str(install_sh), "--check"],
            cwd=str(REPO_ROOT),
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(res_check.returncode, 0, res_check.stderr)

        res_dry = subprocess.run(
            ["bash", str(install_sh), "--dry-run", "--memory-mode", "headless"],
            cwd=str(REPO_ROOT),
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(res_dry.returncode, 0, res_dry.stderr)
        self.assertIn("[DRY-RUN]", res_dry.stdout)

    def test_unified_ast_kernel_and_navigation_maps(self) -> None:
        # 1. Verify all 14 Python scripts have valid, zero-mismatch AST navigation maps
        for sub in ("scripts", "skills", "addons"):
            sdir = REPO_ROOT / sub
            for py_f in sorted(sdir.rglob("*.py")):
                info = homunculus_paths.inspect_python_ast_and_map(py_f)
                self.assertIsNone(info["syntax_error"], f"SyntaxError in {py_f}")
                self.assertTrue(info["map_present"], f"Missing navigation map in {py_f}")
                self.assertEqual(info["map_mismatches"], [], f"Map drift in {py_f}: {info['map_mismatches']}")

        # 2. Verify two-pass sync_script_navigation_map auto-heals shifted line ranges
        with tempfile.TemporaryDirectory() as tmp_dir:
            sample = Path(tmp_dir) / "sample_mod.py"
            sample.write_text(
                '"""Sample docstring.\n\n=== DEVELOPER & AI NAVIGATION MAP ===\n'
                "  Owning Module : Test\n"
                "  CLI Flags     : --old\n"
                "  Symbol Index  (jump directly via read_file StartLine/EndLine):\n"
                "    - def alpha (#L1-L2)\n"
                '=== END NAVIGATION MAP ===\n"""\n\n'
                "def alpha() -> int:\n    return 1\n\ndef beta() -> int:\n    return 2\n",
                encoding="utf-8",
            )
            healed = homunculus_paths.sync_script_navigation_map(sample, write=True)
            self.assertEqual(healed["status"], "UPDATED")
            self.assertEqual(healed["mismatches"], [])
            rechecked = homunculus_paths.inspect_python_ast_and_map(sample)
            self.assertEqual(rechecked["map_mismatches"], [])
            self.assertEqual(len(rechecked["symbols"]), 2)


if __name__ == "__main__":
    unittest.main()
