#!/usr/bin/env python3
"""Packages NEA v2.2.3 into a clean, travel-proof .zip archive in /home/orin/Downloads/.
NOTE: Run ONLY when preparing a deployment/email release. During normal development iterations,
run Scripts/build_copilot_agents.py directly inside the master repository (/home/orin/Projects/Engineering/NEA_v2.2.3)."""
import glob
import hashlib
import os
import shutil
import subprocess
import sys
import zipfile

NEA_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ARCHIVE_PREFIX = "NEA_v2.2.3"
DOWNLOADS_DIR = "/home/orin/Downloads"
OUT_ZIP = os.path.join(DOWNLOADS_DIR, "NEA_v2.2.3_Delivery.zip")

EXCLUDE_DIRS = {"Historical", "__pycache__", ".git", ".agents"}
EXCLUDE_FILES = {".nea_inspect_cache.json", ".DS_Store"}


def clean_stale_downloads():
    for old_path in sorted(glob.glob(os.path.join(DOWNLOADS_DIR, "NEA_*"))):
        base_n = os.path.basename(old_path)
        if (
            os.path.abspath(old_path) == os.path.abspath(OUT_ZIP)
            or "Fallback" in base_n
            or base_n == "NEA_v2.2.3_Timesheet_Module_Test_Pack.zip"
        ):
            continue
        if os.path.isdir(old_path):
            shutil.rmtree(old_path)
        elif os.path.isfile(old_path):
            os.remove(old_path)


def sync_script_mirrors_and_agents():
    builder = os.path.join(NEA_ROOT, "Scripts", "build_copilot_agents.py")
    subprocess.run([sys.executable, builder], check=True)


def build_package():
    clean_stale_downloads()
    sync_script_mirrors_and_agents()
    files_added = []
    with zipfile.ZipFile(OUT_ZIP, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(NEA_ROOT):
            dirs[:] = sorted(d for d in dirs if d not in EXCLUDE_DIRS)
            for fn in sorted(files):
                if fn in EXCLUDE_FILES or fn.startswith("~$") or fn.endswith(".pyc"):
                    continue
                full_p = os.path.join(root, fn)
                rel_inside = os.path.relpath(full_p, NEA_ROOT)
                arc_p = os.path.join(ARCHIVE_PREFIX, rel_inside)
                zf.write(full_p, arc_p)
                files_added.append(arc_p)

    sha = hashlib.sha256(open(OUT_ZIP, "rb").read()).hexdigest()
    size_kb = os.path.getsize(OUT_ZIP) / 1024.0
    print(f"Packaged {len(files_added)} files under '{ARCHIVE_PREFIX}/' into:")
    print(f"  - {OUT_ZIP} ({size_kb:.1f} KB, SHA256={sha[:12]})")


if __name__ == "__main__":
    build_package()
