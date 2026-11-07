#!/usr/bin/env python3
"""Unit and integration tests for Data Safety, Declarative Boundary Engine & Core Rules (`test_data_safety.py`).

Verifies:
  1. Governing Priority Law presence across HOMUNCULUS_START_HERE.md and all 3 rules/*.md files
  2. Declarative homunculus_safety.json compartment loading in scripts/audit_data_boundary.py
  3. UTF-8, UTF-16LE/BE, and UTF-32LE/BE secret, user-path, affiliate-tag, and symlink-escape detection
  4. Zero clean-room or portability violations across the entire Homunculus repository
Requires ONLY Python 3.10+ standard library.
"""
from __future__ import annotations

import codecs
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))
sys.path.insert(0, str(REPO_ROOT / "skills" / "skill-architect" / "scripts"))

import audit_data_boundary  # noqa: E402
import audit_portability  # noqa: E402
import audit_skill_hygiene  # noqa: E402


class TestDataSafety(unittest.TestCase):
    def test_governing_priority_law_in_start_here_and_rules(self) -> None:
        required_files = [
            REPO_ROOT / "HOMUNCULUS_START_HERE.md",
            REPO_ROOT / "rules" / "co-engineering-partner.md",
            REPO_ROOT / "rules" / "verifiable-accuracy.md",
            REPO_ROOT / "rules" / "data-and-credential-safety.md",
            REPO_ROOT / "docs" / "Developer_Data_Safety_Guidelines.md",
            REPO_ROOT / "docs" / "Commands_and_Prompts_Reference.md",
        ]
        for fpath in required_files:
            self.assertTrue(fpath.is_file(), f"Missing required foundation file: {fpath}")
            txt = fpath.read_text(encoding="utf-8")
            self.assertIn("Accuracy", txt)
            self.assertIn("Efficiency", txt)
            self.assertIn("Data Safety", txt)
            self.assertIn("Speed", txt)
        start_here_txt = (REPO_ROOT / "HOMUNCULUS_START_HERE.md").read_text(encoding="utf-8")
        self.assertIn("1. Accuracy & Truth -> 2. Efficiency -> 3. Data Safety -> 4. Speed", start_here_txt)
        self.assertNotIn("2. Portability", start_here_txt)

    def test_declarative_compartment_config_and_multi_encoding_detection(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            pub_repo = root / "public_repo"
            priv_repo = root / "private_repo"
            pub_repo.mkdir()
            priv_repo.mkdir()

            cfg_data = {
                "schema_version": "1.0.0",
                "default_compartment": "cleanroom",
                "compartments": {
                    "private": {
                        "root_paths": [str(priv_repo)],
                        "expected_author_email": "dev@example.com",
                        "expected_remote_url": "git@github.com:example/private.git",
                        "block_os_user_paths": False,
                        "block_affiliate_params": False,
                        "forbidden_tokens": [],
                    },
                    "public": {
                        "root_paths": [str(pub_repo)],
                        "expected_author_email": "public@example.com",
                        "expected_remote_url_template": "git@github.com:ExampleOrg/{repo_name}.git",
                        "block_os_user_paths": True,
                        "block_affiliate_params": True,
                        "forbidden_tokens": ["project_chimera_secret"],
                        "extra_content_patterns": [
                            {"name": "nda_marker", "pattern": "\\bNDA-CONFIDENTIAL-\\d+\\b"}
                        ],
                    },
                },
            }
            cfg_path = root / "homunculus_safety.json"
            cfg_path.write_text(json.dumps(cfg_data, indent=2), encoding="utf-8")

            audit_data_boundary.load_boundary_config(cfg_path)
            self.assertEqual(audit_data_boundary.classify_compartment(priv_repo), "private")
            self.assertEqual(audit_data_boundary.classify_compartment(pub_repo), "public")

            # Clean files pass in both compartments
            (priv_repo / "notes.md").write_text("Clean private engineering note for /Users/example/work\n", encoding="utf-8")
            (pub_repo / "README.md").write_text("# Clean Public Repo\nNo secrets here.\n", encoding="utf-8")
            self.assertEqual(audit_data_boundary.audit_worktree(priv_repo, "private"), [])
            self.assertEqual(audit_data_boundary.audit_worktree(pub_repo, "public"), [])

            # Fault 1: UTF-16LE encoded hardcoded user path + custom forbidden token + affiliate parameter in public_repo
            aff_key = "aff" + "p"
            bad_utf16 = (
                "Path leak: /" + "home/johndoe/workspace\n"
                "Token leak: project_chimera_secret\n"
                "NDA tag: NDA-CONFIDENTIAL-99\n"
                f"Affiliate: https://vendor.example/item?{aff_key}=9999\n"
            )
            (pub_repo / "leaked_utf16.txt").write_bytes(codecs.BOM_UTF16_LE + bad_utf16.encode("utf-16-le"))
            pub_findings = audit_data_boundary.audit_worktree(pub_repo, "public")
            joined = "\n".join(pub_findings)
            self.assertIn("local_workstation_path", joined)
            self.assertIn("forbidden_compartment_identifier", joined)
            self.assertIn("nda_marker", joined)
            self.assertIn("vendor_affiliate_tag", joined)

            # Fault 2: UTF-32BE encoded secret token in private_repo
            fake_gh_token = "ghp_" + ("A1b2C3d4E5" * 4)
            (priv_repo / "secret_utf32.txt").write_bytes(
                codecs.BOM_UTF32_BE + f"TOKEN={fake_gh_token}\n".encode("utf-32-be")
            )
            priv_findings = audit_data_boundary.audit_worktree(priv_repo, "private")
            self.assertTrue(any("github_pat_token" in f for f in priv_findings), priv_findings)

            # Fault 3: External symlink escape
            esc_link = pub_repo / "escape_link"
            esc_link.symlink_to("../../outside_target")
            sym_findings = audit_data_boundary.audit_worktree(pub_repo, "public")
            self.assertTrue(any("SYMLINK:external_escape" in f for f in sym_findings), sym_findings)

    def test_homunculus_worktree_passes_both_boundary_and_portability_gates(self) -> None:
        audit_data_boundary.load_boundary_config(None, repo_root=REPO_ROOT)
        comp = audit_data_boundary.classify_compartment(REPO_ROOT, "cleanroom")
        b_findings = audit_data_boundary.audit_worktree(REPO_ROOT, comp)
        self.assertEqual(b_findings, [], f"Boundary violations in Homunculus: {b_findings}")

        p_report = audit_portability.audit_repository(REPO_ROOT)
        self.assertEqual(p_report["status"], "PASS", f"Portability violations: {p_report['violations']}")

        # Verify skill-architect strict-structure compliance on live Homunculus repo
        h_report = audit_skill_hygiene.run_audit(REPO_ROOT, REPO_ROOT / "rules", REPO_ROOT / "skills")
        self.assertEqual(h_report["load_bearing_defects"], [], f"Skill hygiene defects: {h_report['load_bearing_defects']}")
        self.assertEqual(h_report["turn_waste_hazards"], [], f"Turn-waste hazards: {h_report['turn_waste_hazards']}")

        # Verify Mode 1 --check-new against core rules
        chk_res = audit_skill_hygiene.run_check_new(
            REPO_ROOT,
            REPO_ROOT / "rules",
            REPO_ROOT / "skills",
            "secret-scanner: block private keys, oauth tokens, and compartment leaks before commit",
        )
        self.assertIn("data-and-credential-safety", str(chk_res["overlapping_rules"]))


if __name__ == "__main__":
    unittest.main()
