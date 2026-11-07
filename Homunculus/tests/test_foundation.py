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


if __name__ == "__main__":
    unittest.main()
