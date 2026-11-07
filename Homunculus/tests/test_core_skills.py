#!/usr/bin/env python3
"""Unit and integration tests for Core Engineering Skills & Side-Loaded Add-Ons (`test_core_skills.py`).

Tests:
  1. Core skill & optional add-on file inventory (`subagent-orchestrator`, `engineering-sandbox`, `visual-studio`,
     `doc-and-card-studio`, `pre-commit-gate`, `claim-verification`, `teach-me`, `addons/author-voice-cadence`)
  2. Zero top-level third-party imports (no top-level `PIL`, `numpy`, or `yaml`)
  3. `inspect_hardware_ecosystem.py` STL/STEP/CFG telemetry & `--sync-manifest` entity preservation
  4. `render_diagram.py` SVG rendering, palettes, and blueprints
  5. `audit_repo_docs.py`, stdlib PNG fallback (`format_image._inspect_png_stdlib`), and `.homunculus_brand.json`
  6. `extract_voice_cadence.py` clean-room stylometric extraction
  7. `sandbox_runner.py` CoW dry-run, `--faults`, and `WRONG_FAULT_SIGNATURE` fail-closed gate
Requires ONLY Python 3.10+ standard library.
"""
from __future__ import annotations

from pathlib import Path
import ast
import json
import struct
import subprocess
import sys
import tempfile
import unittest
import zlib

REPO_ROOT = Path(__file__).resolve().parent.parent
VERIFY_CLAIMS = REPO_ROOT / "skills/claim-verification/scripts/verify_claims.py"
INSPECT_HW = REPO_ROOT / "skills/subagent-orchestrator/scripts/inspect_hardware_ecosystem.py"
SANDBOX_RUNNER = REPO_ROOT / "skills/engineering-sandbox/scripts/sandbox_runner.py"
RENDER_DIAGRAM = REPO_ROOT / "skills/visual-studio/scripts/render_diagram.py"
FORMAT_IMAGE = REPO_ROOT / "skills/doc-and-card-studio/scripts/format_image.py"
AUDIT_DOCS = REPO_ROOT / "skills/doc-and-card-studio/scripts/audit_repo_docs.py"
TEACH_BRIEF = REPO_ROOT / "skills/teach-me/scripts/teach_brief.py"
EXTRACT_VOICE = (
    REPO_ROOT / "skills/author-voice-cadence/scripts/extract_voice_cadence.py"
    if (REPO_ROOT / "skills/author-voice-cadence").is_dir()
    else REPO_ROOT / "addons/author-voice-cadence/scripts/extract_voice_cadence.py"
)


def _make_minimal_rgba_png(width: int = 80, height: int = 80) -> bytes:
    """Creates a valid minimal RGBA PNG byte payload using pure Python stdlib."""
    def _chunk(ctype: bytes, data: bytes) -> bytes:
        crc = zlib.crc32(ctype + data) & 0xFFFFFFFF
        return struct.pack(">I", len(data)) + ctype + data + struct.pack(">I", crc)

    ihdr = struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0)
    raw_rows = b"".join(b"\x00" + (b"\xff\xff\xff\xff" * width) for _ in range(height))
    idat = zlib.compress(raw_rows)
    return b"\x89PNG\r\n\x1a\n" + _chunk(b"IHDR", ihdr) + _chunk(b"IDAT", idat) + _chunk(b"IEND", b"")


class TestCoreSkills(unittest.TestCase):
    def test_all_skill_and_addon_files_exist(self) -> None:
        expected = [
            REPO_ROOT / "skills/claim-verification/SKILL.md",
            VERIFY_CLAIMS,
            REPO_ROOT / "skills/subagent-orchestrator/SKILL.md",
            REPO_ROOT / "skills/subagent-orchestrator/references/oracle_cli_cheatsheet.md",
            REPO_ROOT / "skills/subagent-orchestrator/references/orchestration_playbooks.md",
            INSPECT_HW,
            REPO_ROOT / "skills/engineering-sandbox/SKILL.md",
            REPO_ROOT / "skills/engineering-sandbox/references/frame_playbooks.md",
            SANDBOX_RUNNER,
            REPO_ROOT / "skills/visual-studio/SKILL.md",
            RENDER_DIAGRAM,
            REPO_ROOT / "templates/diagrams/Diagram_Palettes.json",
            REPO_ROOT / "templates/diagrams/Diagram_Blueprints/Layered_Architecture_Blueprint.md",
            REPO_ROOT / "templates/diagrams/Diagram_Blueprints/Column_DataFlow_Blueprint.md",
            REPO_ROOT / "templates/diagrams/Diagram_Blueprints/Hardware_Pinout_and_Pneumatic_Blueprint.md",
            REPO_ROOT / "templates/diagrams/Diagram_Blueprints/Engineering_Comparison_Card_Blueprint.md",
            REPO_ROOT / "templates/diagrams/Diagram_Blueprints/Spatial_Topology_Blueprint.md",
            REPO_ROOT / "skills/doc-and-card-studio/SKILL.md",
            REPO_ROOT / "skills/doc-and-card-studio/references/doc_templates.md",
            FORMAT_IMAGE,
            AUDIT_DOCS,
            REPO_ROOT / "skills/pre-commit-gate/SKILL.md",
            REPO_ROOT / "skills/teach-me/SKILL.md",
            REPO_ROOT / "skills/teach-me/references/brief_authoring_playbook.md",
            TEACH_BRIEF,
        ]
        if (REPO_ROOT / "addons" / "author-voice-cadence").is_dir():
            expected.extend([
                REPO_ROOT / "addons/author-voice-cadence/SKILL.md",
                REPO_ROOT / "addons/author-voice-cadence/templates/Voice_Profile_Template.md",
                REPO_ROOT / "addons/author-voice-cadence/templates/Cadence_Report_Template.md",
                EXTRACT_VOICE,
            ])
        for p in expected:
            self.assertTrue(p.is_file(), f"Missing expected core skill/add-on file: {p}")

    def test_zero_toplevel_third_party_imports(self) -> None:
        """Verifies format_image.py, audit_repo_docs.py, and teach_brief.py have zero top-level PIL/numpy/yaml imports."""
        for script_path in (FORMAT_IMAGE, AUDIT_DOCS, TEACH_BRIEF):
            tree = ast.parse(script_path.read_text(encoding="utf-8"))
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        root_mod = alias.name.split(".")[0]
                        self.assertNotIn(root_mod, ("PIL", "numpy", "yaml"), f"Forbidden import {root_mod} in {script_path.name}")
                elif isinstance(node, ast.ImportFrom) and node.module:
                    root_mod = node.module.split(".")[0]
                    self.assertNotIn(root_mod, ("PIL", "numpy", "yaml"), f"Forbidden from-import {root_mod} in {script_path.name}")

    def test_inspect_hardware_ecosystem_stl_and_cfg(self) -> None:
        """Tests inspect_hardware_ecosystem.py on a synthetic ASCII STL, firmware .cfg, --json-out, and --sync-manifest entity preservation."""
        with tempfile.TemporaryDirectory() as tmp:
            tdir = Path(tmp)
            repo = tdir / "Sample_Hardware_Repo"
            (repo / "STL_Files").mkdir(parents=True)
            stl_file = repo / "STL_Files" / "[a]_sample_bracket-mze.stl"
            stl_file.write_text(
                "solid bracket\n"
                "  facet normal 0 0 1\n"
                "    outer loop\n"
                "      vertex 0.0 0.0 0.0\n"
                "      vertex 40.0 0.0 0.0\n"
                "      vertex 40.0 25.0 10.0\n"
                "    endloop\n"
                "  endfacet\n"
                "endsolid bracket\n",
                encoding="utf-8",
            )
            step_file = repo / "Sample_Rev1 - bracket-mze.step"
            step_file.write_text(
                "ISO-10303-21;\n"
                "HEADER;\n"
                "FILE_NAME('Sample_Rev1 - bracket-mze.step','2026-10-14T00:00:00',(''),(''),'Onshape','','');\n"
                "ENDSEC;\n"
                "DATA;\n"
                "#1=( LENGTH_UNIT() NAMED_UNIT(*) SI_UNIT(.MILLI.,.METRE.) );\n"
                "#2=CARTESIAN_POINT('',(0.0,0.0,0.0));\n"
                "#3=CARTESIAN_POINT('',(40.0,25.0,10.0));\n"
                "#4=VERTEX_POINT('',#2);\n"
                "#5=VERTEX_POINT('',#3);\n"
                "#6=CYLINDRICAL_SURFACE('',#2,3.0);\n"
                "#7=PRODUCT('bracket-mze','bracket-mze','',(#8));\n"
                "ENDSEC;\n"
                "END-ISO-10303-21;\n",
                encoding="utf-8",
            )
            cfg_file = repo / "control.cfg"
            cfg_file.write_text(
                "[stepper_x]\nstep_pin: PA1\ndir_pin: !PA2\nrotation_distance: 40\n",
                encoding="utf-8",
            )
            mem_root = tdir / "memory"
            proj_dir = mem_root / "Projects" / "Sample_Hardware_Repo"
            proj_dir.mkdir(parents=True)
            (proj_dir / "Sample_Hardware_Repo.md").write_text(
                "---\nproject: Sample_Hardware_Repo\nentity: Client_Beta\ncompartment: private\nmode: headless\nlocal_path: "
                + str(repo)
                + "\n---\n# Sample_Hardware_Repo\n",
                encoding="utf-8",
            )
            json_out = tdir / "hw_telemetry.json"
            proc = subprocess.run(
                [
                    sys.executable,
                    str(INSPECT_HW),
                    "--repo",
                    str(repo),
                    "--memory-root",
                    str(mem_root),
                    "--project",
                    "Sample_Hardware_Repo",
                    "--sync-manifest",
                    "--json-out",
                    str(json_out),
                    "--force-rescan",
                ],
                capture_output=True,
                text=True,
            )
            self.assertEqual(proc.returncode, 0, proc.stderr)
            self.assertTrue(json_out.is_file())
            hw_md = (proj_dir / "Sample_Hardware_Repo_Hardware.md").read_text(encoding="utf-8")
            self.assertIn("Client_Beta", hw_md)
            self.assertIn("<!-- AUTO-HARDWARE-CAD:START -->", hw_md)
            self.assertIn("<!-- AUTO-HARDWARE-CFG:START -->", hw_md)
            self.assertIn("[a]_sample_bracket-mze.stl", hw_md)
            self.assertIn("MATCH (<=0.2mm)", hw_md)
            self.assertIn("`Ø6.00mm`×1", hw_md)
            self.assertNotIn("Project_Alphatic", hw_md)
            self.assertNotIn("Magnet", hw_md)
            self.assertIn("control.cfg", hw_md)

    def test_render_diagram_svg(self) -> None:
        """Tests render_diagram.py SVG generation across a sample column_dataflow spec."""
        with tempfile.TemporaryDirectory() as tmp:
            tdir = Path(tmp)
            spec_path = tdir / "spec.json"
            svg_path = tdir / "out.svg"
            spec = {
                "archetype": "column_dataflow",
                "title": "TEST PIPELINE",
                "subtitle": "Unit Test Spec",
                "columns": [
                    {
                        "header": "STAGE 1",
                        "nodes": [{"id": "n1", "title": "Input Node", "lines": ["24 V DC Input"]}],
                    },
                    {
                        "header": "STAGE 2",
                        "nodes": [{"id": "n2", "title": "Output Node", "lines": ["5 V Regulated"]}],
                    },
                ],
                "connectors": [{"from_node": "n1", "to_node": "n2", "label": "Buck Bus"}],
            }
            spec_path.write_text(json.dumps(spec), encoding="utf-8")
            proc = subprocess.run(
                [
                    sys.executable,
                    str(RENDER_DIAGRAM),
                    "--spec",
                    str(spec_path),
                    "--palette",
                    "default_dark",
                    "--output",
                    str(svg_path),
                ],
                capture_output=True,
                text=True,
            )
            self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
            self.assertTrue(svg_path.is_file())
            svg_txt = svg_path.read_text(encoding="utf-8")
            self.assertIn("<svg", svg_txt)
            self.assertIn("TEST PIPELINE", svg_txt)
            self.assertIn("#38BDF8", svg_txt, "Expected clean-room cyan accent from Diagram_Palettes.json")

            proc_list = subprocess.run(
                [sys.executable, str(RENDER_DIAGRAM), "--list-palettes"],
                capture_output=True,
                text=True,
            )
            self.assertEqual(proc_list.returncode, 0, proc_list.stderr)
            self.assertIn("Engineering Dark Slate", proc_list.stdout)
            self.assertIn("gruvbox_dark", proc_list.stdout)

            proc_bp = subprocess.run(
                [sys.executable, str(RENDER_DIAGRAM), "--list-blueprints"],
                capture_output=True,
                text=True,
            )
            self.assertEqual(proc_bp.returncode, 0, proc_bp.stderr)
            for arch in (
                "layered_architecture",
                "column_dataflow",
                "hardware_pinout_pneumatic",
                "comparison_matrix",
                "spatial_topology",
            ):
                self.assertIn(arch, proc_bp.stdout)

            mem_root = tdir / "custom_memory"
            pal_dir = mem_root / "Templates" / "Color_Palettes"
            pal_dir.mkdir(parents=True)
            (pal_dir / "Custom_Brand_Palette.md").write_text(
                "---\npalette_id: custom_brand\naliases: [brand_test]\n---\n"
                "```json palette_tokens\n"
                '{"palette_id": "custom_brand", "palette_name": "Custom Test Brand", "mode": "dark", "primary_accent": "#123456"}\n'
                "```\n",
                encoding="utf-8",
            )
            bp_svg = tdir / "bp_out.svg"
            proc_render_bp = subprocess.run(
                [
                    sys.executable,
                    str(RENDER_DIAGRAM),
                    "--memory-root",
                    str(mem_root),
                    "--blueprint",
                    "spatial_topology",
                    "--palette",
                    "brand_test",
                    "--output",
                    str(bp_svg),
                    "--strict",
                ],
                capture_output=True,
                text=True,
            )
            self.assertEqual(proc_render_bp.returncode, 0, proc_render_bp.stdout + proc_render_bp.stderr)
            self.assertIn("#123456", bp_svg.read_text(encoding="utf-8"))

    def test_audit_repo_docs_and_stdlib_png_helper(self) -> None:
        """Tests audit_repo_docs.py (--skip-image-check), format_image._inspect_png_stdlib, and .homunculus_brand.json."""
        with tempfile.TemporaryDirectory() as tmp:
            tdir = Path(tmp)
            png_path = tdir / "sample.png"
            png_path.write_bytes(_make_minimal_rgba_png(80, 80))

            sys.path.insert(0, str(FORMAT_IMAGE.parent))
            import format_image  # type: ignore
            ok, reason = format_image._inspect_png_stdlib(str(png_path))
            self.assertTrue(ok, reason)
            self.assertIn("80x80", reason)

            readme = tdir / "README.md"
            readme.write_text(
                "# Clean Module\n\n> [!NOTE]\n> Verified module documentation.\n",
                encoding="utf-8",
            )
            proc = subprocess.run(
                [
                    sys.executable,
                    str(AUDIT_DOCS),
                    str(readme),
                    "--repo-type",
                    "software",
                    "--skip-image-check",
                ],
                capture_output=True,
                text=True,
            )
            self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
            self.assertIn("Isolated Warnings: 0", proc.stdout)

            brand_cfg = tdir / ".homunculus_brand.json"
            brand_cfg.write_text(
                json.dumps(
                    {
                        "organization": "ExampleOrg",
                        "canonical_discord": "https://discord.gg/canonical123",
                        "deprecated_repo_urls": {
                            "github.com/ExampleOrg/OldRepo": "https://github.com/ExampleOrg/NewRepo"
                        },
                        "required_affiliate_params": {
                            "vendor.example.com/store/": "ref=partner99"
                        },
                    }
                ),
                encoding="utf-8",
            )
            branded_md = tdir / "Branded_BOM.md"
            branded_md.write_text(
                "# Branded BOM\n"
                "- [Join Discord](https://discord.gg/wrong999)\n"
                "- [Old Repo](https://github.com/ExampleOrg/OldRepo)\n"
                "- [Buy Fasteners](https://vendor.example.com/store/m3-kit)\n",
                encoding="utf-8",
            )
            proc_brand = subprocess.run(
                [
                    sys.executable,
                    str(AUDIT_DOCS),
                    str(branded_md),
                    "--repo-type",
                    "software",
                    "--skip-image-check",
                    "--brand-config",
                    str(brand_cfg),
                ],
                capture_output=True,
                text=True,
            )
            self.assertEqual(proc_brand.returncode, 0, proc_brand.stdout + proc_brand.stderr)
            self.assertIn("Non-canonical ExampleOrg Discord link", proc_brand.stdout)
            self.assertIn("Outdated short repo URL", proc_brand.stdout)
            self.assertIn("missing affiliate tag `ref=partner99`", proc_brand.stdout)

    @unittest.skipUnless(
        (REPO_ROOT / "addons" / "author-voice-cadence").is_dir()
        or (REPO_ROOT / "skills" / "author-voice-cadence").is_dir(),
        "Optional author-voice-cadence add-on is not installed",
    )
    def test_extract_voice_cadence_cleanroom(self) -> None:
        """Tests addons/author-voice-cadence/scripts/extract_voice_cadence.py stylometric extraction."""
        with tempfile.TemporaryDirectory() as tmp:
            tdir = Path(tmp)
            inbox = tdir / "inbox"
            inbox.mkdir()
            sample_post = (
                "Today was spent testing the new manifold geometry because the previous revision showed "
                "excessive pressure drop across the rear plenum. That was a real bottleneck. "
                "When you route a tight bend right after the impeller outlet, boundary-layer separation "
                "chokes the effective cross-section, which means the blower works twice as hard for half the airflow. "
                "We widened the transition radius and re-tested on the bench, and static pressure recovery improved immediately.\n\n---\n\n"
                "Just a quick update on the firmware state machine. Originally I tried polling the sensor over I2C "
                "inside the main loop, though bus contention caused jitter during high-speed stepping. "
                "Make sure you bind the interrupt pin directly before enabling the heater loop so thermal faults trip deterministically."
            )
            (inbox / "devlog_samples.md").write_text(sample_post, encoding="utf-8")
            out_report = tdir / "Cadence_Report.md"
            proc = subprocess.run(
                [
                    sys.executable,
                    str(EXTRACT_VOICE),
                    "--inbox",
                    str(inbox),
                    "--scope",
                    "all",
                    "--min-words",
                    "40",
                    "--output",
                    str(out_report),
                ],
                capture_output=True,
                text=True,
            )
            self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
            self.assertTrue(out_report.is_file())
            rep_txt = out_report.read_text(encoding="utf-8")
            self.assertIn("Multi-Scale Sentence Cadence", rep_txt)

    def test_sandbox_runner_spec_workspace_and_faults(self) -> None:
        """Tests sandbox_runner.py live execution via --workspace, --spec, and --faults."""
        with tempfile.TemporaryDirectory() as tmp:
            tdir = Path(tmp)
            ws = tdir / "ws"
            ws.mkdir()
            (ws / "sample.txt").write_text("clean baseline\n", encoding="utf-8")
            spec_file = tdir / "sandbox_spec.json"
            spec_file.write_text(
                json.dumps(
                    {
                        "name": "unit_test_spec",
                        "controls": [
                            {"id": "c1", "cmd": "test -f sample.txt"}
                        ],
                        "faults": [
                            {
                                "id": "f1",
                                "setup_cmd": "printf 'corrupted\\n' > sample.txt",
                                "validator_cmd": "grep -q 'clean baseline' sample.txt",
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )
            proc = subprocess.run(
                [
                    sys.executable,
                    str(SANDBOX_RUNNER),
                    "--mode",
                    "dry-run",
                    "--workspace",
                    str(ws),
                    "--cwd",
                    str(ws),
                    "--spec",
                    str(spec_file),
                    "--faults",
                ],
                capture_output=True,
                text=True,
            )
            self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
            self.assertIn("Status: PASS", proc.stdout)
            self.assertIn("Controls: 1/1 passed", proc.stdout)
            self.assertIn("+faults: 1/1 caught", proc.stdout)
            self.assertIn("Live Host Mutations: 0", proc.stdout)
            self.assertEqual((ws / "sample.txt").read_text(encoding="utf-8"), "clean baseline\n")

            proc_bad_sig = subprocess.run(
                [
                    sys.executable,
                    str(SANDBOX_RUNNER),
                    "--mode",
                    "dry-run",
                    "--workspace",
                    str(ws),
                    "--cwd",
                    str(ws),
                    "--cmd",
                    "test -f sample.txt",
                    "--fault-case",
                    "printf 'corrupted\\n' > sample.txt :: grep -q 'clean baseline' sample.txt @@ EXPECTED_SIGNATURE_MISSING",
                ],
                capture_output=True,
                text=True,
            )
            self.assertNotEqual(proc_bad_sig.returncode, 0, "Expected WRONG_FAULT_SIGNATURE to fail closed")
            self.assertIn("WRONG_FAULT_SIGNATURE", proc_bad_sig.stdout)


if __name__ == "__main__":
    unittest.main()
