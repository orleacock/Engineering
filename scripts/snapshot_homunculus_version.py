#!/usr/bin/env python3
"""
Homunculus Immutable RAID Version Deliverable Snapshot Builder (`snapshot_homunculus_version.py`).

Governing Priority Law:
    1. Accuracy & Truth -> 2. Efficiency -> 3. Data Safety -> 4. Speed
Supported Operating Systems:
    Linux (Btrfs `--reflink=auto` CoW native) and POSIX workstations (100% Python 3.10+ stdlib).

Responsibilities:
    1. Package complete, self-contained, write-once ("zero edit churn") version deliverables onto
       the Btrfs RAID array (`/run/media/orin/Raid/Backup Documents/Homunculus_Versions/v0.Y.Z_<YYYY-MM-DD>_<slug>/`)
       per `Requirement 5B`.
    2. Capture ALL context, scripts, repositories, and verification receipts:
       - `Homunculus_CleanRoom/` (Single-source `/home/orin/Projects/Alchemical3D/Homunculus`)
       - `memory/` (`/home/orin/Projects/Engineering/memory` Dual-Mode vault)
       - `study_briefs/` (`/home/orin/Projects/Engineering/study_briefs`)
       - `Engineering_Root_and_Scripts/` (`scripts/`, root configs, umbrella `.homunculus.json` files)
       - `Client_Wiring_Snapshot/` (symlink topology manifests, redacted/command-only MCP config & tool schemas)
       - `Git_Snapshots/` (`Homunculus_Alchemical3D.bundle`, `Engineering_Parent.bundle`, provenance JSON)
       - `BENCHMARK_SCORECARD.md` & `benchmark_report.json` (`full-system-suite` comparison vs. baseline)
       - `RECONSTRUCTION_INDEX.md`, executable `restore_version.sh`, and `SHA256SUMS.txt`
    3. Audit staged payload via `audit_data_boundary.py` (`0` live credentials/tokens/keys) and
       recursively lock files `0444` and directories/`restore_version.sh` `0555` so snapshots NEVER see edit churn.

=== DEVELOPER & AI NAVIGATION MAP ===
  Owning Module : Workstation Operations (`scripts/snapshot_homunculus_version.py`)
  Callers       : Developer CLI, Minor/Major Version Release Workflow (`v0.Y.0` / `v1.0.0`)
  Callees       : `version_manager.py`, `benchmark_homunculus.py`, `audit_data_boundary.py`, `git bundle`, `cp --reflink=auto`
  Contract      : `scripts/script_contracts.json` [`snapshot_homunculus_version.py`]
  CLI Flags     : --slug, --label, --raid-root, --homunculus-dir, --engineering-dir, --version-manifest, --allow-dirty, --skip-benchmark, --force-fresh-benchmark, --list, --verify, --dry-run, --json
  Symbol Index  (jump directly via read_file StartLine/EndLine):
    - def sanitize_slug (#L74-L77)                   | def _sha256_file (#L80-L86)
    - def find_latest_same_dev_raid_snapshot (#L89-L114) | def find_verified_benchmark_receipt (#L117-L151)
    - def _force_writable_rmtree (#L154-L173)        | def copy_tree_cow (#L176-L358)
    - def _redact_json_obj (#L361-L373)              | def collect_symlink_manifest (#L376-L394)
    - def stage_client_wiring (#L397-L436)           | def create_git_bundles (#L439-L481)
    - def build_restore_script (#L484-L698)          | def build_reconstruction_index (#L701-L761)
    - def compute_sha256sums (#L764-L776)            | def lock_deliverable_readonly (#L779-L801)
    - def verify_existing_snapshot (#L804-L816)      | def main (#L819-L1121)
=== END NAVIGATION MAP ===
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import re
import shutil
import stat
import subprocess
import sys
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_ENGINEERING_DIR = SCRIPT_DIR.parent
DEFAULT_HOMUNCULUS_DIR = DEFAULT_ENGINEERING_DIR.parent / "Alchemical3D" / "Homunculus"
DEFAULT_VERSION_MANIFEST = SCRIPT_DIR / "homunculus_version.json"
DEFAULT_RAID_VERSIONS_ROOT = Path("/run/media/orin/Raid/Backup Documents/Homunculus_Versions")

FORBIDDEN_SECRET_PATTERNS = re.compile(
    r"(?:^\.env(?:\..+)?$|client_secret.*\.json$|.*token.*\.json$|^id_(?:rsa|ed25519|ecdsa)$|\.(?:pem|key|p12|pfx)$)",
    re.I,
)
SENSITIVE_JSON_KEY_RE = re.compile(r"(?:token|secret|password|api_key|apikey|private_key|authorization|cookie)", re.I)

sys.path.insert(0, str(SCRIPT_DIR))
import version_manager  # noqa: E402


def sanitize_slug(raw_slug: str) -> str:
    """Normalize a human label into a clean filesystem-safe `[a-z0-9_]+` slug."""
    cleaned = re.sub(r"[^a-zA-Z0-9]+", "_", raw_slug.strip().lower()).strip("_")
    return cleaned or "release_snapshot"


def _sha256_file(path: Path) -> str:
    """Compute streaming SHA-256 hex digest for a regular file."""
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def find_latest_same_dev_raid_snapshot(raid_root: Path, exclude_dir: Path) -> Path | None:
    """Locate the newest finalized `v*` deliverable on the same filesystem (`st_dev`) for Btrfs `--reflink=always` seeding."""
    if not raid_root.is_dir():
        return None
    try:
        target_dev = os.stat(raid_root).st_dev
    except OSError:
        return None
    candidates: list[tuple[float, str, Path]] = []
    for entry in raid_root.iterdir():
        if entry == exclude_dir or entry.name.startswith(".") or not entry.name.startswith("v"):
            continue
        if entry.is_symlink() or not entry.is_dir():
            continue
        if not (entry / "SHA256SUMS.txt").is_file():
            continue
        try:
            st = os.stat(entry)
        except OSError:
            continue
        if st.st_dev == target_dev:
            candidates.append((st.st_mtime, entry.name, entry))
    if not candidates:
        return None
    candidates.sort()
    return candidates[-1][2]


def find_verified_benchmark_receipt(
    history_jsonl: Path,
    ver_status: dict[str, Any],
) -> dict[str, Any] | None:
    """Return the newest `PASS` / `BASELINE_PINNED` `full-system-suite` receipt matching live `(HEAD, tree_hash, worktree)`."""
    if not history_jsonl.is_file():
        return None
    want_head = str(ver_status.get("live_head_sha") or "")
    want_tree = str(ver_status.get("live_tree_hash") or "")
    want_wt = str(ver_status.get("worktree") or "")
    if not want_head or not want_tree:
        return None
    lines = history_jsonl.read_text(encoding="utf-8", errors="replace").splitlines()
    for raw in reversed(lines):
        raw = raw.strip()
        if not raw:
            continue
        try:
            rec = json.loads(raw)
        except json.JSONDecodeError:
            continue
        if rec.get("profile") != "full-system-suite":
            continue
        if rec.get("verdict") not in ("PASS", "BASELINE_PINNED"):
            continue
        if int(rec.get("hard_block_count", 1)) != 0:
            continue
        vs = rec.get("version_status") or {}
        if (
            str(vs.get("live_head_sha") or "") == want_head
            and str(vs.get("live_tree_hash") or "") == want_tree
            and str(vs.get("worktree") or "") == want_wt
        ):
            return rec
    return None


def _force_writable_rmtree(target: Path) -> None:
    """Recursively restore `u+w` permissions before `shutil.rmtree` so `0555`/`0444` trees never block cleanup."""
    if not os.path.lexists(target):
        return
    if target.is_symlink() or target.is_file():
        target.unlink(missing_ok=True)
        return
    for rw, dw, fw in os.walk(target, topdown=True):
        try:
            os.chmod(rw, 0o755)
        except OSError:
            pass
        for fn in fw:
            fp = Path(rw) / fn
            if not fp.is_symlink():
                try:
                    os.chmod(fp, 0o644)
                except OSError:
                    pass
    shutil.rmtree(target, ignore_errors=True)


def copy_tree_cow(
    src: Path,
    dst: Path,
    exclude_names: set[str] | None = None,
    seed_src: Path | None = None,
) -> dict[str, int | str]:
    """
    Copy `src` to `dst`, seeding from a same-device `seed_src` via Btrfs `cp -dR --preserve=timestamps --reflink=always`
    when available and reconciling modified/added/deleted files by cryptographic SHA-256 while retaining working-tree `.git/`.
    """
    if os.path.lexists(dst):
        _force_writable_rmtree(dst)
    dst.parent.mkdir(parents=True, exist_ok=True)
    cp_bin = shutil.which("cp")
    seeded = False
    reflink_mode = "none"

    if seed_src is not None and seed_src.is_dir() and cp_bin:
        try:
            same_dev = os.stat(seed_src).st_dev == os.stat(dst.parent).st_dev
        except OSError:
            same_dev = False
        if same_dev:
            p_always = subprocess.run(
                [cp_bin, "-dR", "--preserve=timestamps", "--reflink=always", str(seed_src), str(dst)],
                capture_output=True,
                text=True,
            )
            if p_always.returncode == 0:
                seeded = True
                reflink_mode = "always"
            else:
                _force_writable_rmtree(dst)
                p_auto = subprocess.run(
                    [cp_bin, "-dR", "--preserve=timestamps", "--reflink=auto", str(seed_src), str(dst)],
                    capture_output=True,
                    text=True,
                )
                if p_auto.returncode == 0:
                    seeded = True
                    reflink_mode = "auto_fallback"
                else:
                    _force_writable_rmtree(dst)

    if seeded:
        # Unlock staging copy (`seed_src` on RAID remains 0444/0555 untouched!)
        for root_u, dirs_u, files_u in os.walk(dst):
            os.chmod(root_u, 0o755)
            for fn_u in files_u:
                fp_u = Path(root_u) / fn_u
                if not fp_u.is_symlink():
                    os.chmod(fp_u, 0o644)

        pruned = 0
        for root_d, dirs_d, files_d in os.walk(dst, topdown=False):
            rel_dir = Path(root_d).relative_to(dst)
            src_dir = src / rel_dir
            for fname in files_d:
                dst_fp = Path(root_d) / fname
                src_fp = src_dir / fname
                is_forbidden = (not dst_fp.is_symlink()) and bool(FORBIDDEN_SECRET_PATTERNS.search(fname))
                is_excluded = bool(exclude_names and fname in exclude_names)
                src_missing_or_type_changed = (
                    (not os.path.lexists(src_fp))
                    or (dst_fp.is_symlink() != src_fp.is_symlink())
                    or (not src_fp.is_symlink() and src_fp.is_dir())
                )
                if is_forbidden or is_excluded or src_missing_or_type_changed:
                    dst_fp.unlink(missing_ok=True)
                    pruned += 1
            for dname in dirs_d:
                dst_dp = Path(root_d) / dname
                src_dp = src_dir / dname
                is_excluded_d = dname == "__pycache__" or bool(exclude_names and dname in exclude_names)
                if dst_dp.is_symlink():
                    if is_excluded_d or not src_dp.is_symlink():
                        dst_dp.unlink(missing_ok=True)
                        pruned += 1
                else:
                    if is_excluded_d or not src_dp.is_dir() or src_dp.is_symlink():
                        shutil.rmtree(dst_dp, ignore_errors=True)
                        pruned += 1

        reflink_preserved = 0
        copied_files = 0
        for root_s, dirs_s, files_s in os.walk(src, topdown=True):
            rel_dir = Path(root_s).relative_to(src)
            dst_dir = dst / rel_dir
            dst_dir.mkdir(parents=True, exist_ok=True)
            os.chmod(dst_dir, 0o755)
            for dname in list(dirs_s):
                if dname == "__pycache__" or (exclude_names and dname in exclude_names):
                    dirs_s.remove(dname)
                    continue
                src_dp = Path(root_s) / dname
                if src_dp.is_symlink():
                    dirs_s.remove(dname)
                    dst_dp = dst_dir / dname
                    want_link = os.readlink(src_dp)
                    if os.path.lexists(dst_dp):
                        if dst_dp.is_symlink() and os.readlink(dst_dp) == want_link:
                            continue
                        if dst_dp.is_dir() and not dst_dp.is_symlink():
                            shutil.rmtree(dst_dp, ignore_errors=True)
                        else:
                            dst_dp.unlink(missing_ok=True)
                    os.symlink(want_link, dst_dp)

            for fname in files_s:
                if exclude_names and fname in exclude_names:
                    continue
                src_fp = Path(root_s) / fname
                dst_fp = dst_dir / fname
                if src_fp.is_symlink():
                    want_link = os.readlink(src_fp)
                    if os.path.lexists(dst_fp):
                        if dst_fp.is_symlink() and os.readlink(dst_fp) == want_link:
                            continue
                        dst_fp.unlink(missing_ok=True)
                    os.symlink(want_link, dst_fp)
                    continue
                if FORBIDDEN_SECRET_PATTERNS.search(fname):
                    dst_fp.unlink(missing_ok=True)
                    continue
                if (
                    dst_fp.exists()
                    and not dst_fp.is_symlink()
                    and dst_fp.stat().st_size == src_fp.stat().st_size
                    and _sha256_file(dst_fp) == _sha256_file(src_fp)
                ):
                    os.chmod(dst_fp, 0o644)
                    reflink_preserved += 1
                else:
                    dst_fp.unlink(missing_ok=True)
                    shutil.copy2(src_fp, dst_fp)
                    os.chmod(dst_fp, 0o644)
                    copied_files += 1

        return {
            "reflink_mode": reflink_mode,
            "reflink_preserved_files": reflink_preserved,
            "copied_or_updated_files": copied_files,
            "pruned_entries": pruned,
        }

    used_cp = False
    if cp_bin:
        proc = subprocess.run(
            [cp_bin, "-dR", "--preserve=timestamps", "--reflink=auto", str(src), str(dst)],
            capture_output=True,
            text=True,
        )
        if proc.returncode == 0:
            used_cp = True
            reflink_mode = "direct_auto"
        else:
            _force_writable_rmtree(dst)
    if not used_cp:
        shutil.copytree(src, dst, symlinks=True)

    copied_files = 0
    # Ensure staging tree is writable while assembling (source may contain 0444 locked core/archive files)
    for root_w, dirs_w, files_w in os.walk(dst):
        os.chmod(root_w, 0o755)
        for dname in list(dirs_w):
            if dname == "__pycache__" or (exclude_names and dname in exclude_names):
                shutil.rmtree(Path(root_w) / dname, ignore_errors=True)
                dirs_w.remove(dname)
        for fname in files_w:
            fp = Path(root_w) / fname
            if fp.is_symlink():
                continue
            if FORBIDDEN_SECRET_PATTERNS.search(fname) or (exclude_names and fname in exclude_names):
                fp.unlink(missing_ok=True)
            else:
                os.chmod(fp, 0o644)
                copied_files += 1
    return {
        "reflink_mode": reflink_mode,
        "reflink_preserved_files": 0,
        "copied_or_updated_files": copied_files,
        "pruned_entries": 0,
    }


def _redact_json_obj(obj: Any) -> Any:
    """Recursively redact any secret-bearing key values inside client MCP configuration JSONs."""
    if isinstance(obj, dict):
        out: dict[str, Any] = {}
        for k, v in obj.items():
            if SENSITIVE_JSON_KEY_RE.search(str(k)) and not isinstance(v, (dict, list)):
                out[k] = "<REDACTED_BY_SNAPSHOT_SAFETY_GATE>"
            else:
                out[k] = _redact_json_obj(v)
        return out
    if isinstance(obj, list):
        return [_redact_json_obj(x) for x in obj]
    return obj


def collect_symlink_manifest(scan_roots: list[tuple[str, Path]]) -> list[dict[str, str]]:
    """Record every symbolic link under client config directories without reading secret files."""
    entries: list[dict[str, str]] = []
    for label, root in scan_roots:
        if not root.exists():
            continue
        for p in sorted(root.rglob("*")):
            if p.is_symlink():
                raw_target = os.readlink(p)
                resolved = str(p.resolve()) if p.exists() else f"BROKEN->{raw_target}"
                entries.append(
                    {
                        "scope": label,
                        "link_path": str(p),
                        "raw_target": raw_target,
                        "resolved_target": resolved,
                    }
                )
    return entries


def stage_client_wiring(staging_dir: Path, engineering_dir: Path) -> dict[str, Any]:
    """Populate `Client_Wiring_Snapshot/` with symlink manifests and redacted MCP schemas (`0` secrets)."""
    cw_dir = staging_dir / "Client_Wiring_Snapshot"
    cw_dir.mkdir(parents=True, exist_ok=True)

    home = Path.home()
    gemini_cfg = home / ".gemini" / "config"
    dot_agents = home / ".agents"
    agy_gmail_schemas = home / ".gemini" / "antigravity-cli" / "mcp" / "gmail"

    symlinks = collect_symlink_manifest(
        [
            ("gemini_config", gemini_cfg),
            ("engineering_dot_agents", engineering_dir / ".agents"),
            ("home_dot_agents", dot_agents),
        ]
    )
    (cw_dir / "symlink_topology_manifest.json").write_text(
        json.dumps({"symlink_count": len(symlinks), "symlinks": symlinks}, indent=2) + "\n",
        encoding="utf-8",
    )
    txt_lines = [f"{item['scope']} | {item['link_path']} -> {item['raw_target']} ({item['resolved_target']})" for item in symlinks]
    (cw_dir / "symlink_topology_manifest.txt").write_text("\n".join(txt_lines) + "\n", encoding="utf-8")

    mcp_cfg = gemini_cfg / "mcp_config.json"
    mcp_copied = False
    if mcp_cfg.is_file():
        raw_obj = json.loads(mcp_cfg.read_text(encoding="utf-8"))
        safe_obj = _redact_json_obj(raw_obj)
        (cw_dir / "mcp_config.json").write_text(json.dumps(safe_obj, indent=2) + "\n", encoding="utf-8")
        mcp_copied = True

    if agy_gmail_schemas.is_dir():
        copy_tree_cow(agy_gmail_schemas, cw_dir / "antigravity_mcp_gmail_schemas")

    find_skills = dot_agents / "skills" / "find-skills"
    if find_skills.is_dir():
        copy_tree_cow(find_skills, cw_dir / "dot_agents_skills" / "find-skills")

    return {"symlink_count": len(symlinks), "mcp_config_included": mcp_copied}


def create_git_bundles(staging_dir: Path, homunculus_dir: Path, engineering_dir: Path) -> dict[str, Any]:
    """Create self-contained `.bundle` archives and provenance metadata for both repositories."""
    git_dir = staging_dir / "Git_Snapshots"
    git_dir.mkdir(parents=True, exist_ok=True)

    hom_bundle = git_dir / "Homunculus_Alchemical3D.bundle"
    eng_bundle = git_dir / "Engineering_Parent.bundle"

    subprocess.run(
        ["git", "-C", str(homunculus_dir), "bundle", "create", str(hom_bundle), "--all"],
        check=True,
        capture_output=True,
        text=True,
    )
    subprocess.run(
        ["git", "-C", str(engineering_dir), "bundle", "create", str(eng_bundle), "--all"],
        check=True,
        capture_output=True,
        text=True,
    )

    def _repo_meta(repo: Path) -> dict[str, Any]:
        head = subprocess.check_output(["git", "-C", str(repo), "rev-parse", "HEAD"], text=True).strip()
        branch = subprocess.check_output(["git", "-C", str(repo), "rev-parse", "--abbrev-ref", "HEAD"], text=True).strip()
        tags = subprocess.check_output(["git", "-C", str(repo), "tag", "-l"], text=True).splitlines()
        status = subprocess.check_output(["git", "-C", str(repo), "status", "--short"], text=True).splitlines()
        remotes = subprocess.check_output(["git", "-C", str(repo), "remote", "-v"], text=True).splitlines()
        return {
            "path": str(repo),
            "head_sha": head,
            "branch": branch,
            "tags": tags,
            "dirty_count": len(status),
            "status_short": status,
            "remotes": remotes,
        }

    prov = {
        "homunculus_cleanroom": _repo_meta(homunculus_dir),
        "engineering_parent": _repo_meta(engineering_dir),
    }
    (git_dir / "git_provenance_manifest.json").write_text(json.dumps(prov, indent=2) + "\n", encoding="utf-8")
    return prov


def build_restore_script(version_label: str, folder_name: str) -> str:
    """Generate the self-contained `restore_version.sh` verifier & disaster-recovery tool."""
    return f"""#!/usr/bin/env bash
# Immutable Homunculus Version Deliverable Verifier & Disaster-Recovery Tool
# Deliverable : {folder_name} (Engine Version: {version_label})
# Architecture: Single-Source Clean-Room (/home/orin/Projects/Alchemical3D/Homunculus) + Decoupled Memory
set -euo pipefail

BACKUP_DIR="$(cd "$(dirname "${{BASH_SOURCE[0]}}")" && pwd)"
HOME_DIR="${{HOMUNCULUS_RESTORE_HOME_OVERRIDE:-/home/orin}}"
PROJECTS_ROOT="${{HOME_DIR}}/Projects"
ENG_ROOT="${{PROJECTS_ROOT}}/Engineering"
CLEANROOM_ROOT="${{PROJECTS_ROOT}}/Alchemical3D/Homunculus"
GEMINI_CFG="${{HOME_DIR}}/.gemini/config"
AGY_MCP_DIR="${{HOME_DIR}}/.gemini/antigravity-cli/mcp/gmail"
DOT_AGENTS="${{HOME_DIR}}/.agents"

MODE=""

for arg in "$@"; do
    case "$arg" in
        --verify-backup) MODE="verify" ;;
        --dry-run) MODE="dry-run" ;;
        --restore-engine-only) MODE="restore-engine" ;;
        --restore-full-workstation) MODE="restore-full" ;;
        -h|--help)
            cat << 'EOF'
Usage: ./restore_version.sh <--verify-backup | --dry-run | --restore-engine-only | --restore-full-workstation>

Modes:
  --verify-backup             Verify SHA-256 checksums across every regular file in SHA256SUMS.txt,
                              verify both Git bundles, and confirm 0444/0555 write-once immutability
                              (100% read-only; modifies nothing).
  --dry-run                   Verify backup integrity and print the exact restoration plan without
                              mutating any live workstation files.
  --restore-engine-only       Restore ONLY /home/orin/Projects/Alchemical3D/Homunculus from
                              Homunculus_CleanRoom/ and re-bind symlinks via bootstrap_workstation.sh
                              (leaves /home/orin/Projects/Engineering/memory untouched!).
  --restore-full-workstation  Catastrophic full-workstation recovery: restore Alchemical3D/Homunculus,
                              Engineering/{{memory,study_briefs,scripts,configs}}, umbrella configs,
                              client wiring, symlinks, and run all 46 unit tests + safety/hygiene gates.
EOF
            exit 0
            ;;
        *)
            echo "Unknown option: $arg (use --help for usage)" >&2
            exit 2
            ;;
    esac
done

if [[ -z "$MODE" ]]; then
    echo "Error: Must specify --verify-backup, --dry-run, --restore-engine-only, or --restore-full-workstation" >&2
    exit 2
fi

echo "=== Homunculus Deliverable Restore & Integrity Tool ({version_label} // ${{MODE^^}}) ==="
echo "Deliverable Path : ${{BACKUP_DIR}}"
echo "Clean-Room Target: ${{CLEANROOM_ROOT}}"

echo "[1/4] Verifying cryptographic SHA-256 manifest (SHA256SUMS.txt)..."
(
    cd "${{BACKUP_DIR}}"
    sha256sum --check --quiet SHA256SUMS.txt
)
echo "  [OK] Every file in SHA256SUMS.txt passed cryptographic verification."

echo "[2/4] Verifying Git bundle integrity & write-once immutability..."
TMP_GIT_DIR="$(mktemp -d)"
trap 'rm -rf "${{TMP_GIT_DIR}}"' EXIT
git init --bare -q "${{TMP_GIT_DIR}}"
git -C "${{TMP_GIT_DIR}}" bundle verify "${{BACKUP_DIR}}/Git_Snapshots/Homunculus_Alchemical3D.bundle" >/dev/null
git -C "${{TMP_GIT_DIR}}" bundle verify "${{BACKUP_DIR}}/Git_Snapshots/Engineering_Parent.bundle" >/dev/null
WRITABLE_COUNT="$(find "${{BACKUP_DIR}}" -not -type l -perm /0222 | wc -l)"
if [[ "$WRITABLE_COUNT" -ne 0 ]]; then
    echo "  [FAIL] Immutability violation: ${{WRITABLE_COUNT}} writable paths found in deliverable!" >&2
    exit 1
fi
echo "  [OK] Both Git bundles valid and 0 writable files/dirs in deliverable (strict 0444/0555 lock)."

if [[ "$MODE" == "verify" ]]; then
    echo "=== DELIVERABLE VERIFICATION PASSED (0 errors) ==="
    exit 0
fi

if [[ "$MODE" == "dry-run" ]]; then
    echo "[3/4] DRY-RUN Restoration Plan (0 live files will be mutated):"
    echo "  - Engine-Only Mode (--restore-engine-only):"
    echo "      * Replace ${{CLEANROOM_ROOT}} with ${{BACKUP_DIR}}/Homunculus_CleanRoom (preserving live memory/)"
    echo "      * Re-bind symlinks via ${{ENG_ROOT}}/scripts/bootstrap_workstation.sh --update-obsidian --compat-symlinks"
    echo "  - Full-Workstation Mode (--restore-full-workstation):"
    echo "      * Replace ${{CLEANROOM_ROOT}} with ${{BACKUP_DIR}}/Homunculus_CleanRoom"
    echo "      * Replace ${{ENG_ROOT}}/{{memory,study_briefs,scripts}} and root configs"
    echo "      * Restore ${{PROJECTS_ROOT}}/{{.homunculus.json,.geminiignore}} and ${{HOME_DIR}}/.homunculus.json"
    echo "      * Preserve live ${{GEMINI_CFG}}/mcp_config.json (staging redacted template at mcp_config.redacted_reference.json) & non-Homunculus user skills/rules"
    echo "      * Restore client MCP schemas & ~/.agents/skills/find-skills"
    echo "      * Re-bind symlinks & run full 46-test suite + portability, boundary, hygiene, and memory audits"
    echo "=== DRY-RUN COMPLETE (0 live mutations) ==="
    exit 0
fi

unlock_live_tree() {{
    local target="$1"
    if [[ -d "$target" ]]; then
        chmod -R u+w "$target" 2>/dev/null || true
    fi
}}

if [[ "$MODE" == "restore-engine" ]]; then
    echo "[3/4] Restoring Single-Source Clean-Room Engine ONLY (${{CLEANROOM_ROOT}})..."
    mkdir -p "$(dirname "${{CLEANROOM_ROOT}}")"
    unlock_live_tree "${{CLEANROOM_ROOT}}"
    rm -rf "${{CLEANROOM_ROOT}}"
    cp -a --reflink=auto "${{BACKUP_DIR}}/Homunculus_CleanRoom" "${{CLEANROOM_ROOT}}"
    chmod -R u+w "${{CLEANROOM_ROOT}}"
    python3 "${{CLEANROOM_ROOT}}/scripts/homunculus_paths.py" --homunculus-root "${{CLEANROOM_ROOT}}" --lock-core >/dev/null
    echo "[4/4] Re-binding workstation symlinks & running unit tests (memory/ untouched)..."
    HOME="${{HOME_DIR}}" "${{ENG_ROOT}}/scripts/bootstrap_workstation.sh" --update-obsidian --compat-symlinks
    HOME="${{HOME_DIR}}" "${{ENG_ROOT}}/scripts/bootstrap_workstation.sh" --check --update-obsidian --compat-symlinks
    PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s "${{CLEANROOM_ROOT}}/tests" -p "test_*.py"
    echo "=== ENGINE-ONLY RESTORATION COMPLETE & VERIFIED (0 errors; memory/ preserved) ==="
    exit 0
fi

echo "[3/4] Executing Full Catastrophic Workstation Restoration..."
mkdir -p "${{ENG_ROOT}}" "${{PROJECTS_ROOT}}" "$(dirname "${{CLEANROOM_ROOT}}")"
rm -rf "${{ENG_ROOT}}/.agents"
mkdir -p "${{GEMINI_CFG}}/rules" "${{GEMINI_CFG}}/skills"
shopt -s nullglob dotglob
for cfg_sub in "${{GEMINI_CFG}}/rules" "${{GEMINI_CFG}}/skills"; do
    for entry in "${{cfg_sub}}/"*; do
        if [[ -L "$entry" ]]; then
            lnk_t="$(readlink "$entry" || true)"
            if [[ ! -e "$entry" ]] || [[ "$lnk_t" == *"Homunculus/"* ]] || [[ "$lnk_t" == *"Engineering/"* ]]; then
                rm -f "$entry"
            fi
        fi
    done
done
shopt -u nullglob dotglob

for live_d in "${{CLEANROOM_ROOT}}" "${{ENG_ROOT}}/memory" "${{ENG_ROOT}}/study_briefs" "${{ENG_ROOT}}/scripts"; do
    unlock_live_tree "$live_d"
    rm -rf "$live_d"
done

cp -a --reflink=auto "${{BACKUP_DIR}}/Homunculus_CleanRoom" "${{CLEANROOM_ROOT}}"
cp -a --reflink=auto "${{BACKUP_DIR}}/memory" "${{ENG_ROOT}}/memory"
cp -a --reflink=auto "${{BACKUP_DIR}}/study_briefs" "${{ENG_ROOT}}/study_briefs"
cp -a --reflink=auto "${{BACKUP_DIR}}/Engineering_Root_and_Scripts/scripts" "${{ENG_ROOT}}/scripts"

chmod -R u+w "${{CLEANROOM_ROOT}}" "${{ENG_ROOT}}/memory" "${{ENG_ROOT}}/study_briefs" "${{ENG_ROOT}}/scripts"
chmod +x "${{ENG_ROOT}}/scripts/"*.sh "${{ENG_ROOT}}/scripts/"*.py 2>/dev/null || true

for root_cfg in README.md .gitignore .stignore .geminiignore .homunculus.json .homunculus_brand.json homunculus_safety.json; do
    if [[ -f "${{BACKUP_DIR}}/Engineering_Root_and_Scripts/${{root_cfg}}" ]]; then
        cp -af --remove-destination "${{BACKUP_DIR}}/Engineering_Root_and_Scripts/${{root_cfg}}" "${{ENG_ROOT}}/${{root_cfg}}"
        chmod 0644 "${{ENG_ROOT}}/${{root_cfg}}"
    fi
done

for umb_cfg in .homunculus.json .geminiignore; do
    if [[ -f "${{BACKUP_DIR}}/Engineering_Root_and_Scripts/Umbrella_Configs/Projects_${{umb_cfg}}" ]]; then
        cp -af --remove-destination "${{BACKUP_DIR}}/Engineering_Root_and_Scripts/Umbrella_Configs/Projects_${{umb_cfg}}" "${{PROJECTS_ROOT}}/${{umb_cfg}}"
        chmod 0644 "${{PROJECTS_ROOT}}/${{umb_cfg}}"
    fi
done
if [[ -f "${{BACKUP_DIR}}/Engineering_Root_and_Scripts/Umbrella_Configs/home.homunculus.json" ]]; then
    cp -af --remove-destination "${{BACKUP_DIR}}/Engineering_Root_and_Scripts/Umbrella_Configs/home.homunculus.json" "${{HOME_DIR}}/.homunculus.json"
    chmod 0644 "${{HOME_DIR}}/.homunculus.json"
fi

if [[ -d "${{BACKUP_DIR}}/Client_Wiring_Snapshot/dot_agents_skills/find-skills" ]]; then
    mkdir -p "${{DOT_AGENTS}}/skills"
    rm -rf "${{DOT_AGENTS}}/skills/find-skills"
    cp -a "${{BACKUP_DIR}}/Client_Wiring_Snapshot/dot_agents_skills/find-skills" "${{DOT_AGENTS}}/skills/find-skills"
    chmod -R u+w "${{DOT_AGENTS}}/skills/find-skills"
fi
if [[ -f "${{BACKUP_DIR}}/Client_Wiring_Snapshot/mcp_config.json" ]]; then
    mkdir -p "${{GEMINI_CFG}}"
    if [[ -f "${{GEMINI_CFG}}/mcp_config.json" ]]; then
        cp -af --remove-destination "${{BACKUP_DIR}}/Client_Wiring_Snapshot/mcp_config.json" "${{GEMINI_CFG}}/mcp_config.redacted_reference.json"
        chmod 0600 "${{GEMINI_CFG}}/mcp_config.redacted_reference.json"
        echo "  [SAFE-PRESERVE] Preserved live ${{GEMINI_CFG}}/mcp_config.json (redacted snapshot template staged at mcp_config.redacted_reference.json)."
    elif grep -q "<REDACTED_BY_SNAPSHOT_SAFETY_GATE>" "${{BACKUP_DIR}}/Client_Wiring_Snapshot/mcp_config.json"; then
        cp -af --remove-destination "${{BACKUP_DIR}}/Client_Wiring_Snapshot/mcp_config.json" "${{GEMINI_CFG}}/mcp_config.redacted_reference.json"
        chmod 0600 "${{GEMINI_CFG}}/mcp_config.redacted_reference.json"
        echo "  [ACTION REQUIRED] Staged redacted MCP template at ${{GEMINI_CFG}}/mcp_config.redacted_reference.json — populate live credentials and rename to mcp_config.json."
    else
        cp -af --remove-destination "${{BACKUP_DIR}}/Client_Wiring_Snapshot/mcp_config.json" "${{GEMINI_CFG}}/mcp_config.json"
        chmod 0600 "${{GEMINI_CFG}}/mcp_config.json"
    fi
fi
if [[ -d "${{BACKUP_DIR}}/Client_Wiring_Snapshot/antigravity_mcp_gmail_schemas" ]]; then
    mkdir -p "$(dirname "${{AGY_MCP_DIR}}")"
    rm -rf "${{AGY_MCP_DIR}}"
    cp -a "${{BACKUP_DIR}}/Client_Wiring_Snapshot/antigravity_mcp_gmail_schemas" "${{AGY_MCP_DIR}}"
    chmod -R u+w "${{AGY_MCP_DIR}}"
fi

# Re-apply intentional 0444 core & archive locks on live restored trees
python3 "${{CLEANROOM_ROOT}}/scripts/homunculus_paths.py" --homunculus-root "${{CLEANROOM_ROOT}}" --lock-core >/dev/null
python3 "${{CLEANROOM_ROOT}}/skills/project-memory/scripts/sync_memory.py" --memory-root "${{ENG_ROOT}}/memory" --lock-memory-rules >/dev/null

echo "[4/4] Re-binding workstation symlinks and running full verification gates..."
HOME="${{HOME_DIR}}" "${{ENG_ROOT}}/scripts/bootstrap_workstation.sh" --update-obsidian --compat-symlinks
HOME="${{HOME_DIR}}" "${{ENG_ROOT}}/scripts/bootstrap_workstation.sh" --check --update-obsidian --compat-symlinks
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s "${{CLEANROOM_ROOT}}/tests" -p "test_*.py"
PYTHONDONTWRITEBYTECODE=1 python3 "${{CLEANROOM_ROOT}}/skills/skill-architect/scripts/audit_skill_hygiene.py" --repo-root "${{CLEANROOM_ROOT}}" --audit --strict-structure >/dev/null
PYTHONDONTWRITEBYTECODE=1 python3 "${{CLEANROOM_ROOT}}/scripts/audit_portability.py" --repo "${{CLEANROOM_ROOT}}"
PYTHONDONTWRITEBYTECODE=1 python3 "${{CLEANROOM_ROOT}}/scripts/audit_data_boundary.py" --repo "${{CLEANROOM_ROOT}}" --compartment cleanroom --worktree
PYTHONDONTWRITEBYTECODE=1 python3 "${{CLEANROOM_ROOT}}/skills/project-memory/scripts/sync_memory.py" --memory-root "${{ENG_ROOT}}/memory" --audit --verify-checkpoints >/dev/null

echo "=== FULL WORKSTATION RESTORATION COMPLETE & VERIFIED (0 errors) ==="
"""


def build_reconstruction_index(
    folder_name: str,
    snap_path: Path,
    timestamp_iso: str,
    ver_status: dict[str, Any],
    git_prov: dict[str, Any],
    bench_summary: dict[str, Any],
) -> str:
    """Render `RECONSTRUCTION_INDEX.md` documenting archive contents, provenance, and recovery commands."""
    hom_head = git_prov["homunculus_cleanroom"]["head_sha"]
    eng_head = git_prov["engineering_parent"]["head_sha"]
    b_id = bench_summary.get("run_id", "SKIPPED")
    b_verdict = bench_summary.get("verdict", "SKIPPED")
    eff_ver = ver_status["effective_version"]
    tree_h = ver_status["live_tree_hash"]
    f_cnt = ver_status["live_file_count"]

    return f"""# Immutable Homunculus Version Deliverable (`{folder_name}`)

- **Engine Version**: `{eff_ver}` (`Tree Hash`: `{tree_h}`, `{f_cnt}` Clean-Room files)
- **Snapshot Timestamp**: `{timestamp_iso}`
- **Authoritative Single-Source `Alchemical3D/Homunculus` `HEAD` SHA**: `{hom_head}`
- **Parent `Engineering` Workstation `HEAD` SHA**: `{eng_head}`
- **Standardized Benchmark Receipt**: `{b_id}` (`Verdict: {b_verdict}` — full side-by-side table in `BENCHMARK_SCORECARD.md`)
- **Immutability Lock (`Requirement 5B`)**: Strictly write-once (`0444` files / `0555` directories & `restore_version.sh` — **NEVER edit in place**).
- **Credential Safety**: `0` live OAuth tokens, SSH private keys, or `.env` secrets included (verified via `audit_data_boundary.py` across both `cleanroom` and `private` compartments).

---

## 1. Deliverable Contents (`ALL Context, Scripts, Repos & Verification Artifacts`)

| Path in Deliverable | Live Workstation Source | Description |
| :--- | :--- | :--- |
| `Homunculus_CleanRoom/` | `/home/orin/Projects/Alchemical3D/Homunculus` | Single-source Clean-Room `Homunculus` repository (`{f_cnt}` files + `.git/` + tag `{ver_status['baseline_tag']}`: `rules/`, `skills/`, `addons/`, `adapters/`, `scripts/`, `templates/`, `hooks/`, `docs/`, and `tests/`). |
| `memory/` | `/home/orin/Projects/Engineering/memory` | Complete Dual-Mode (`Headless` + `Obsidian`) engineering memory (`Projects/`, `Directory/`, `Profile/`, `Standards_and_Specs/`, `Tasks/`, `Templates/`, `Diagrams/`, `Homunculus_Version_and_Benchmark_Ledger.md`, and `governance_seal.json`). |
| `study_briefs/` | `/home/orin/Projects/Engineering/study_briefs` | Non-consumed `/teach-me` `Brief+` directory. |
| `Engineering_Root_and_Scripts/` | `/home/orin/Projects/Engineering/{{scripts,*}}` | Workstation governance & MCP scripts (`version_manager.py`, `benchmark_homunculus.py`, `snapshot_homunculus_version.py`, `bootstrap_workstation.sh`, git boundary hooks, `gmail_mcp/`), root configs, and `Umbrella_Configs/` (`/home/orin/Projects/.homunculus.json` + `/home/orin/.homunculus.json`). |
| `Client_Wiring_Snapshot/` | `~/.gemini/config/` & `~/.agents/` | `symlink_topology_manifest.{{json,txt}}`, command-only `mcp_config.json`, `antigravity_mcp_gmail_schemas/`, and `~/.agents/skills/find-skills`. |
| `Git_Snapshots/` | Git repositories | Self-contained `Homunculus_Alchemical3D.bundle` + `Engineering_Parent.bundle` and `git_provenance_manifest.json`. |
| `BENCHMARK_SCORECARD.md` | *(Generated Scorecard)* | Standardized 12-Row Universal Spine + 16-Row Full-System Suite Markdown comparison chart (`benchmark_report.json` alongside). |
| `restore_version.sh` | *(Executable Restore Tool)* | Read-only cryptographic/bundle/immutability verifier (`--verify-backup`), dry-run planner (`--dry-run`), engine-only rollback (`--restore-engine-only`), and catastrophic full-workstation recovery (`--restore-full-workstation`). |
| `SHA256SUMS.txt` | *(Cryptographic Manifest)* | SHA-256 checksums across every regular file in this deliverable. |

---

## 2. Quick Verification & Restoration Commands

```bash
# 1. Read-only cryptographic + Git bundle + 0444/0555 immutability verification (modifies nothing)
"{snap_path}/restore_version.sh" --verify-backup

# 2. Preview exact restoration plans without touching live files
"{snap_path}/restore_version.sh" --dry-run

# 3. Restore ONLY the Clean-Room Homunculus engine (leaves live Engineering/memory untouched)
"{snap_path}/restore_version.sh" --restore-engine-only

# 4. Catastrophic full-workstation restoration (Engine + Memory + Scripts + Client Wiring + 46 Tests)
"{snap_path}/restore_version.sh" --restore-full-workstation
```
"""


def compute_sha256sums(staging_dir: Path) -> int:
    """Compute SHA-256 digests for every regular file in `staging_dir` (excluding `SHA256SUMS.txt` itself)."""
    manifest_lines: list[str] = []
    for p in sorted(staging_dir.rglob("*")):
        if p.is_symlink() or not p.is_file():
            continue
        rel = p.relative_to(staging_dir).as_posix()
        if rel == "SHA256SUMS.txt":
            continue
        digest = hashlib.sha256(p.read_bytes()).hexdigest()
        manifest_lines.append(f"{digest}  {rel}")
    (staging_dir / "SHA256SUMS.txt").write_text("\n".join(manifest_lines) + "\n", encoding="utf-8")
    return len(manifest_lines)


def lock_deliverable_readonly(snap_dir: Path) -> tuple[int, int]:
    """Recursively lock regular files to `0444` (`restore_version.sh` `0555`) and directories to `0555`."""
    file_cnt = 0
    dir_cnt = 0
    # Walk bottom-up so files are locked before their parent directories become 0555!
    for root_w, dirs_w, files_w in os.walk(snap_dir, topdown=False):
        for fname in files_w:
            fp = Path(root_w) / fname
            if fp.is_symlink():
                continue
            if fname == "restore_version.sh":
                os.chmod(fp, 0o555)
            else:
                os.chmod(fp, 0o444)
            file_cnt += 1
        for dname in dirs_w:
            dp = Path(root_w) / dname
            if not dp.is_symlink():
                os.chmod(dp, 0o555)
                dir_cnt += 1
    os.chmod(snap_dir, 0o555)
    dir_cnt += 1
    return file_cnt, dir_cnt


def verify_existing_snapshot(snap_dir: Path) -> dict[str, Any]:
    """Invoke `restore_version.sh --verify-backup` on a finalized RAID deliverable."""
    restore_sh = snap_dir / "restore_version.sh"
    if not restore_sh.is_file():
        return {"status": "FAIL", "reason": f"Missing restore_version.sh in {snap_dir}"}
    proc = subprocess.run([str(restore_sh), "--verify-backup"], capture_output=True, text=True)
    return {
        "status": "PASS" if proc.returncode == 0 else "FAIL",
        "returncode": proc.returncode,
        "snapshot_dir": str(snap_dir),
        "stdout": proc.stdout.strip(),
        "stderr": proc.stderr.strip(),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Homunculus Immutable RAID Version Deliverable Snapshot Builder."
    )
    parser.add_argument("--slug", "--label", dest="slug", default="release_snapshot", help="Descriptive slug appended to v0.Y.Z_<YYYY-MM-DD>_<slug>.")
    parser.add_argument("--raid-root", default=str(DEFAULT_RAID_VERSIONS_ROOT), help="RAID versions root directory.")
    parser.add_argument("--homunculus-dir", default=str(DEFAULT_HOMUNCULUS_DIR), help="Path to single-source Alchemical3D/Homunculus.")
    parser.add_argument("--engineering-dir", default=str(DEFAULT_ENGINEERING_DIR), help="Path to Engineering parent root.")
    parser.add_argument("--version-manifest", default=str(DEFAULT_VERSION_MANIFEST), help="Path to homunculus_version.json.")
    parser.add_argument("--allow-dirty", action="store_true", help="Allow cutting a `-dev+<tree8>` candidate snapshot when Homunculus worktree is dirty.")
    parser.add_argument("--skip-benchmark", action="store_true", help="Skip running `benchmark_homunculus.py --profile full-system-suite` during staging.")
    parser.add_argument("--force-fresh-benchmark", action="store_true", help="Always execute a fresh `full-system-suite` run even when a matching `(HEAD, tree_hash)` receipt exists.")
    parser.add_argument("--list", action="store_true", help="List existing immutable version deliverables on RAID.")
    parser.add_argument("--verify", default="", help="Verify an existing RAID deliverable directory (name or full path).")
    parser.add_argument("--dry-run", action="store_true", help="Print snapshot plan without writing to RAID.")
    parser.add_argument("--json", action="store_true", help="Emit structured JSON summary.")
    args = parser.parse_args(argv)

    raid_root = Path(args.raid_root).expanduser().resolve()
    hom_dir = Path(args.homunculus_dir).expanduser().resolve()
    eng_dir = Path(args.engineering_dir).expanduser().resolve()
    ver_manifest = Path(args.version_manifest).expanduser().resolve()

    if args.list:
        snaps = sorted([p.name for p in raid_root.iterdir() if p.is_dir() and not p.name.startswith(".")]) if raid_root.is_dir() else []
        payload = {"raid_root": str(raid_root), "count": len(snaps), "snapshots": snaps}
        print(json.dumps(payload, indent=2) if args.json else "\n".join([f"RAID Root: {raid_root}", *[f"  - {s}" for s in snaps]]))
        return 0

    if args.verify:
        cand = Path(args.verify).expanduser()
        if not cand.is_abs():
            cand = raid_root / args.verify
        res = verify_existing_snapshot(cand.resolve())
        print(json.dumps(res, indent=2) if args.json else (res["stdout"] + ("\n" + res["stderr"] if res["stderr"] else "")))
        return 0 if res["status"] == "PASS" else 1

    if not raid_root.parent.is_dir():
        print(f"[BLOCKED] RAID mount parent directory is unavailable: {raid_root.parent}", file=sys.stderr)
        return 1

    ver_status = version_manager.resolve_effective_version_status(ver_manifest, hom_dir)
    if ver_status["worktree"] != "clean" and not args.allow_dirty:
        print(
            f"[BLOCKED] Homunculus Clean-Room worktree is dirty ({ver_status['dirty_files']}). "
            "Commit cleanly or pass --allow-dirty for a `-dev` candidate snapshot.",
            file=sys.stderr,
        )
        return 1

    eff_ver = str(ver_status["effective_version"]).replace("+", "_")
    if not eff_ver.startswith("v"):
        eff_ver = f"v{eff_ver}"
    today = dt.date.today().isoformat()
    slug = sanitize_slug(args.slug)
    folder_name = f"{eff_ver}_{today}_{slug}"
    final_dir = raid_root / folder_name

    if final_dir.exists():
        print(
            f"[IMMUTABILITY LOCK] Deliverable already exists at '{final_dir}'. "
            "RAID version snapshots NEVER see edit churn — bump version or choose a distinct slug.",
            file=sys.stderr,
        )
        return 1

    if args.dry_run:
        plan = {
            "status": "DRY_RUN",
            "target_deliverable": str(final_dir),
            "effective_version": ver_status["effective_version"],
            "homunculus_dir": str(hom_dir),
            "engineering_dir": str(eng_dir),
            "immutability_permissions": {"files": "0444", "dirs_and_restore_sh": "0555"},
        }
        print(json.dumps(plan, indent=2) if args.json else f"[DRY-RUN] Would create immutable deliverable: {final_dir}")
        return 0

    raid_root.mkdir(parents=True, exist_ok=True)
    staging_dir = raid_root / f".staging_{folder_name}_{os.getpid()}"
    if staging_dir.exists():
        shutil.rmtree(staging_dir, ignore_errors=True)
    staging_dir.mkdir(parents=True, exist_ok=True)

    try:
        # 1. Reuse cryptographically matching `full-system-suite` receipt if available, else run fresh (blocks on HARD_BLOCK_REGRESSION)
        bench_summary: dict[str, Any] = {"run_id": "SKIPPED", "verdict": "SKIPPED"}
        bench_reused = False
        if not args.skip_benchmark:
            history_jsonl = SCRIPT_DIR / "benchmark_history.jsonl"
            if not history_jsonl.is_file():
                history_jsonl = eng_dir / "memory" / "Projects" / "Homunculus" / "benchmark_history.jsonl"
            cached_rec = None if args.force_fresh_benchmark else find_verified_benchmark_receipt(history_jsonl, ver_status)
            scorecard_md = staging_dir / "BENCHMARK_SCORECARD.md"
            if cached_rec is not None:
                import benchmark_homunculus  # local workstation companion module

                bench_summary = cached_rec
                bench_reused = True
                scorecard_md.write_text(
                    benchmark_homunculus.render_markdown_report(
                        cached_rec, str(cached_rec.get("autopsy_markdown") or "")
                    ),
                    encoding="utf-8",
                )
                (staging_dir / "benchmark_report.json").write_text(
                    json.dumps(bench_summary, indent=2) + "\n",
                    encoding="utf-8",
                )
            else:
                bench_script = SCRIPT_DIR / "benchmark_homunculus.py"
                p_bench = subprocess.run(
                    [
                        sys.executable,
                        str(bench_script),
                        "--profile",
                        "full-system-suite",
                        "--homunculus-dir",
                        str(hom_dir),
                        "--memory-root",
                        str(eng_dir / "memory"),
                        "--version-manifest",
                        str(ver_manifest),
                        "--output-md",
                        str(scorecard_md),
                        "--label",
                        f"RAID Deliverable Gate ({folder_name})",
                        "--json",
                    ],
                    capture_output=True,
                    text=True,
                )
                if p_bench.returncode == 1:
                    print(
                        "[BLOCKED] Full-system benchmark detected HARD_BLOCK_REGRESSION (`exit 1`). "
                        "Resolve regressions before cutting a RAID deliverable snapshot!",
                        file=sys.stderr,
                    )
                    if p_bench.stdout:
                        try:
                            bad_obj = json.loads(p_bench.stdout)
                            print(bad_obj.get("autopsy_markdown", ""), file=sys.stderr)
                        except Exception:
                            pass
                    return 1
                bench_summary = json.loads(p_bench.stdout)
                (staging_dir / "benchmark_report.json").write_text(
                    json.dumps(bench_summary, indent=2) + "\n",
                    encoding="utf-8",
                )
        else:
            (staging_dir / "BENCHMARK_SCORECARD.md").write_text(
                f"# Benchmark Skipped (`--skip-benchmark`)\n\nDeliverable: `{folder_name}`\n",
                encoding="utf-8",
            )

        # 2. Stage Clean-Room Homunculus, Memory, Study Briefs, and Engineering Root/Scripts via Same-Device Btrfs CoW Seeding
        seed_snap = find_latest_same_dev_raid_snapshot(raid_root, final_dir)
        cow_stats: dict[str, Any] = {}
        cow_stats["Homunculus_CleanRoom"] = copy_tree_cow(
            hom_dir,
            staging_dir / "Homunculus_CleanRoom",
            seed_src=(seed_snap / "Homunculus_CleanRoom") if seed_snap else None,
        )
        cow_stats["memory"] = copy_tree_cow(
            eng_dir / "memory",
            staging_dir / "memory",
            seed_src=(seed_snap / "memory") if seed_snap else None,
        )
        if (eng_dir / "study_briefs").is_dir():
            cow_stats["study_briefs"] = copy_tree_cow(
                eng_dir / "study_briefs",
                staging_dir / "study_briefs",
                seed_src=(seed_snap / "study_briefs") if seed_snap else None,
            )
        else:
            (staging_dir / "study_briefs").mkdir(parents=True, exist_ok=True)

        ers_dir = staging_dir / "Engineering_Root_and_Scripts"
        ers_dir.mkdir(parents=True, exist_ok=True)
        cow_stats["scripts"] = copy_tree_cow(
            eng_dir / "scripts",
            ers_dir / "scripts",
            seed_src=(seed_snap / "Engineering_Root_and_Scripts" / "scripts") if seed_snap else None,
        )
        for cfg_name in (
            "README.md",
            ".gitignore",
            ".stignore",
            ".geminiignore",
            ".homunculus.json",
            ".homunculus_brand.json",
            "homunculus_safety.json",
        ):
            src_cfg = eng_dir / cfg_name
            if src_cfg.is_file():
                shutil.copy2(src_cfg, ers_dir / cfg_name)
                os.chmod(ers_dir / cfg_name, 0o644)

        umb_dir = ers_dir / "Umbrella_Configs"
        umb_dir.mkdir(parents=True, exist_ok=True)
        for umb_name in (".homunculus.json", ".geminiignore"):
            p_umb = eng_dir.parent / umb_name
            if p_umb.is_file():
                shutil.copy2(p_umb, umb_dir / f"Projects_{umb_name}")
                os.chmod(umb_dir / f"Projects_{umb_name}", 0o644)
        home_hom = Path.home() / ".homunculus.json"
        if home_hom.is_file():
            shutil.copy2(home_hom, umb_dir / "home.homunculus.json")
            os.chmod(umb_dir / "home.homunculus.json", 0o644)

        # 3. Stage Client Wiring & Git Bundles
        wiring_info = stage_client_wiring(staging_dir, eng_dir)
        git_prov = create_git_bundles(staging_dir, hom_dir, eng_dir)

        # 4. Write `restore_version.sh` and `RECONSTRUCTION_INDEX.md`
        now_iso = dt.datetime.now().astimezone().isoformat(timespec="seconds")
        restore_path = staging_dir / "restore_version.sh"
        restore_path.write_text(build_restore_script(ver_status["effective_version"], folder_name), encoding="utf-8")
        os.chmod(restore_path, 0o755)

        recon_md = build_reconstruction_index(
            folder_name, final_dir, now_iso, ver_status, git_prov, bench_summary
        )
        (staging_dir / "RECONSTRUCTION_INDEX.md").write_text(recon_md, encoding="utf-8")

        # 5. Run Data-Boundary Decontamination Gate BEFORE finalizing!
        boundary_script = hom_dir / "scripts" / "audit_data_boundary.py"
        safety_cfg = eng_dir / "homunculus_safety.json"
        env_b = dict(os.environ)
        if safety_cfg.is_file():
            env_b["HOMUNCULUS_BOUNDARY_CONFIG"] = str(safety_cfg)

        p_b_clean = subprocess.run(
            [sys.executable, str(boundary_script), "--repo", str(staging_dir / "Homunculus_CleanRoom"), "--compartment", "cleanroom", "--worktree"],
            capture_output=True,
            text=True,
            env=env_b,
        )
        if p_b_clean.returncode != 0:
            raise RuntimeError(f"CleanRoom boundary check failed:\n{p_b_clean.stdout}\n{p_b_clean.stderr}")

        for priv_sub in ("memory", "study_briefs", "Engineering_Root_and_Scripts", "Client_Wiring_Snapshot"):
            p_b_priv = subprocess.run(
                [sys.executable, str(boundary_script), "--repo", str(staging_dir / priv_sub), "--compartment", "private", "--worktree"],
                capture_output=True,
                text=True,
                env=env_b,
            )
            if p_b_priv.returncode != 0:
                raise RuntimeError(f"Private boundary check failed in {priv_sub}:\n{p_b_priv.stdout}\n{p_b_priv.stderr}")

        # 6. Compute cryptographic SHA256SUMS.txt across every regular file in deliverable
        hashed_files = compute_sha256sums(staging_dir)

        # 7. Atomically promote staging dir -> final_dir and lock 0444/0555 write-once!
        staging_dir.rename(final_dir)
        locked_files, locked_dirs = lock_deliverable_readonly(final_dir)

        # 8. Self-verify finalized deliverable via `restore_version.sh --verify-backup`
        ver_res = verify_existing_snapshot(final_dir)
        if ver_res["status"] != "PASS":
            raise RuntimeError(f"Post-lock self-verification failed: {ver_res}")

        result = {
            "status": "PASS",
            "deliverable_dir": str(final_dir),
            "folder_name": folder_name,
            "effective_version": ver_status["effective_version"],
            "engine_head_sha": ver_status["live_head_sha"],
            "engine_tree_hash": ver_status["live_tree_hash"],
            "benchmark_run_id": bench_summary.get("run_id"),
            "benchmark_verdict": bench_summary.get("verdict"),
            "benchmark_receipt_reused": bench_reused,
            "cow_seed_snapshot": seed_snap.name if seed_snap else None,
            "cow_sync_stats": cow_stats,
            "sha256_files_indexed": hashed_files,
            "locked_files_0444": locked_files,
            "locked_dirs_0555": locked_dirs,
            "client_symlinks_captured": wiring_info["symlink_count"],
            "self_verification": "PASS",
        }
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print(f"[PASS] Immutable RAID Deliverable Created & Verified: {final_dir}")
            print(f"  - Engine Version     : {result['effective_version']} (HEAD: {result['engine_head_sha']} | Tree: {result['engine_tree_hash']})")
            print(f"  - Benchmark Receipt  : {result['benchmark_run_id']} ({result['benchmark_verdict']})")
            print(f"  - SHA256SUMS Indexed : {hashed_files} files")
            print(f"  - Immutability Lock  : {locked_files} files (0444/0555) across {locked_dirs} directories (0555)")
        return 0

    except Exception as exc:
        if staging_dir.exists():
            for rw, dw, fw in os.walk(staging_dir, topdown=False):
                os.chmod(rw, 0o755)
                for fn in fw:
                    fp = Path(rw) / fn
                    if not fp.is_symlink():
                        os.chmod(fp, 0o644)
            shutil.rmtree(staging_dir, ignore_errors=True)
        print(f"[SNAPSHOT FAILED] {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
