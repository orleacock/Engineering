#!/usr/bin/env python3
"""
Homunculus Development Workstation Version & Rollback Manager (`version_manager.py`).

Governing Priority Law:
    1. Accuracy & Truth -> 2. Efficiency -> 3. Data Safety -> 4. Speed
Supported Operating Systems:
    Linux, macOS, and Windows (100% Python 3.10+ standard library).

Responsibilities:
    1. Manage pre-release `v0.Y.Z` versioning (`v0.1.0` baseline; `v1.0.0` reserved for public GitHub release).
    2. Enforce deterministic `X.Y.Z` digit trigger definitions (`major`, `minor`, `patch`, and `-dev+<tree8>`).
    3. Compute deterministic SHA-256 `engine_tree_hash` across `/home/orin/Projects/Alchemical3D/Homunculus`
       (the single-source Clean-Room repository on the workstation, completely decoupled from `memory/`).
    4. Provide 1-command path-isolated engine rollback (`--rollback <tag> [--dry-run]`) that never mutates
       `/home/orin/Projects/Engineering/memory/`.

=== DEVELOPER & AI NAVIGATION MAP ===
  Owning Module : Workstation Operations (`scripts/version_manager.py`)
  Callers       : `benchmark_homunculus.py`, `snapshot_homunculus_version.py`, Developer CLI
  Callees       : `git` CLI, `bootstrap_workstation.sh`
  Contract      : `scripts/script_contracts.json` [`version_manager.py`]
  CLI Flags     : --homunculus-dir, --manifest, --status, --init-baseline, --sync-manifest, --bump, --reason, --allow-v1-public-release, --rollback, --dry-run, --json
  Symbol Index  (jump directly via read_file StartLine/EndLine):
    - def compute_content_tree_hash (#L79-L105)      | def get_git_state (#L111-L160)
    - def load_or_create_manifest (#L163-L200)       | def resolve_effective_version_status (#L203-L251)
    - def ensure_git_tag (#L254-L277)                | def bump_version (#L280-L352)
    - def rollback_engine (#L355-L414)               | def main (#L417-L556)
=== END NAVIGATION MAP ===
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
ENGINEERING_ROOT = SCRIPT_DIR.parent
DEFAULT_HOMUNCULUS_DIR = ENGINEERING_ROOT.parent / "Alchemical3D" / "Homunculus"
DEFAULT_MANIFEST_PATH = SCRIPT_DIR / "homunculus_version.json"

SEMVER_RE = re.compile(r"^v?(\d+)\.(\d+)\.(\d+)$")

DIGIT_TRIGGER_LAWS: dict[str, dict[str, str]] = {
    "major": {
        "digit": "X (X.0.0)",
        "rule": (
            "0.Y.Z -> 1.0.0 is reserved strictly for public GitHub release of Alchemical-3D/Homunculus "
            "(requires --allow-v1-public-release). Post-1.0.0 major bumps require breaking schema/CLI changes."
        ),
        "required_gate": "Full Profile 6 Benchmark Suite + Compare-Full Subagent Gate + Immutable RAID Deliverable Snapshot.",
    },
    "minor": {
        "digit": "Y (0.Y.0)",
        "rule": (
            "Triggered by major architectural overhauls, multi-sprint subsystem rebuilds, new core skills/add-ons, "
            "new client adapters, or JSON/memory schema expansions. Resets patch Z to 0."
        ),
        "required_gate": "Full Profile 6 Benchmark Suite (0 unresolved regressions vs baseline) + Git Tag v0.Y.0 + Immutable RAID Snapshot.",
    },
    "patch": {
        "digit": "Z (0.y.Z)",
        "rule": (
            "Triggered by targeted bug fixes, false-positive/false-negative validator closures, regex/qualifier refinements, "
            "rule/skill prose trims, single-script latency optimizations, or new unit/+faults tests without schema changes."
        ),
        "required_gate": "Targeted Subsystem Benchmark Profile (0 regressions) + Unit Tests PASS + Git Tag v0.y.Z.",
    },
}


def compute_content_tree_hash(homunculus_dir: Path) -> tuple[str, int]:
    """Compute a deterministic 12-hex full-byte Merkle content_tree_hash over all tracked/non-ignored files in Homunculus."""
    h = hashlib.sha256()
    file_count = 0
    if (homunculus_dir / ".git").exists():
        raw = subprocess.check_output(
            ["git", "-C", str(homunculus_dir), "ls-files", "--cached", "--others", "--exclude-standard", "-z"],
        ).decode("utf-8", errors="surrogateescape")
        rel_files = sorted(f for f in raw.split("\x00") if f)
    else:
        rel_files = sorted(
            p.relative_to(homunculus_dir).as_posix()
            for p in homunculus_dir.rglob("*")
            if p.is_file() and ".git" not in p.parts and "__pycache__" not in p.parts
        )
    for rel in rel_files:
        fp = homunculus_dir / rel
        if not fp.is_file() and not fp.is_symlink():
            continue
        file_count += 1
        h.update(f"FILE:{rel}\0".encode("utf-8"))
        if fp.is_symlink():
            h.update(f"SYMLINK:{os.readlink(fp)}\0".encode("utf-8"))
        else:
            h.update(fp.read_bytes())
            h.update(b"\0")
    return h.hexdigest()[:12], file_count


compute_engine_tree_hash = compute_content_tree_hash


def get_git_state(homunculus_dir: Path) -> dict[str, Any]:
    """Inspect HEAD SHA, branch, dirty status, and version tags of the standalone Homunculus repo."""
    if not (homunculus_dir / ".git").exists():
        return {
            "is_git_repo": False,
            "head_sha": "UNTRACKED",
            "head_sha_full": "UNTRACKED",
            "branch": "none",
            "worktree": "untracked",
            "dirty_files": [],
            "tags": [],
            "head_tags": [],
            "remote_url": "none",
        }

    head_full = subprocess.check_output(
        ["git", "-C", str(homunculus_dir), "rev-parse", "HEAD"], text=True
    ).strip()
    head_short = head_full[:12]
    branch = subprocess.check_output(
        ["git", "-C", str(homunculus_dir), "rev-parse", "--abbrev-ref", "HEAD"], text=True
    ).strip()
    status_out = subprocess.check_output(
        ["git", "-C", str(homunculus_dir), "status", "--porcelain"], text=True
    ).splitlines()
    dirty_files = [ln.strip() for ln in status_out if ln.strip()]
    tags_out = subprocess.check_output(
        ["git", "-C", str(homunculus_dir), "tag", "-l", "--sort=-version:refname"], text=True
    ).splitlines()
    head_tags_out = subprocess.check_output(
        ["git", "-C", str(homunculus_dir), "tag", "--points-at", "HEAD"], text=True
    ).splitlines()
    try:
        remote_url = subprocess.check_output(
            ["git", "-C", str(homunculus_dir), "remote", "get-url", "origin"], text=True
        ).strip()
    except subprocess.CalledProcessError:
        remote_url = "none"

    return {
        "is_git_repo": True,
        "head_sha": head_short,
        "head_sha_full": head_full,
        "branch": branch,
        "worktree": "clean" if not dirty_files else f"dirty ({len(dirty_files)} files)",
        "dirty_files": dirty_files,
        "tags": [t.strip() for t in tags_out if t.strip()],
        "head_tags": [t.strip() for t in head_tags_out if t.strip()],
        "remote_url": remote_url,
    }


def load_or_create_manifest(manifest_path: Path, homunculus_dir: Path) -> dict[str, Any]:
    """Load homunculus_version.json or create default v0.1.0 manifest."""
    if manifest_path.is_file():
        return json.loads(manifest_path.read_text(encoding="utf-8"))
    tree_hash, file_count = compute_engine_tree_hash(homunculus_dir)
    git_info = get_git_state(homunculus_dir)
    default_manifest = {
        "schema_version": "1.0.0",
        "engine_version": "0.1.0",
        "release_stage": "development",
        "public_release_target": "1.0.0",
        "baseline_tag": "v0.1.0",
        "baseline_head_sha": git_info["head_sha"],
        "baseline_tree_hash": tree_hash,
        "baseline_file_count": file_count,
        "contract_schema_version": "1.0",
        "memory_schema_version": "1.1",
        "benchmark_schema_version": "1.0",
        "authoritative_cleanroom_path": str(homunculus_dir),
        "authoritative_remote_url": git_info["remote_url"],
        "updated_at": dt.date.today().isoformat(),
        "digit_trigger_laws": DIGIT_TRIGGER_LAWS,
        "version_history": [
            {
                "version": "0.1.0",
                "tag": "v0.1.0",
                "date": dt.date.today().isoformat(),
                "head_sha": git_info["head_sha"],
                "tree_hash": tree_hash,
                "trigger_type": "initial_baseline",
                "reason": (
                    "Consolidated Single-Source Clean-Room Homunculus baseline on development workstation "
                    "(101 files, Stateful Memory v1.1, 0 duplicate copies)."
                ),
            }
        ],
    }
    return default_manifest


def resolve_effective_version_status(manifest_path: Path, homunculus_dir: Path) -> dict[str, Any]:
    """Compute live version status, detecting whether candidate matches locked v0.Y.Z or is -dev+<tree8>."""
    manifest = load_or_create_manifest(manifest_path, homunculus_dir)
    live_tree, file_count = compute_engine_tree_hash(homunculus_dir)
    git_info = get_git_state(homunculus_dir)

    base_ver = str(manifest.get("engine_version", "0.1.0"))
    base_tree = str(manifest.get("baseline_tree_hash", ""))
    base_sha = str(manifest.get("baseline_head_sha", ""))

    is_exact_baseline = (
        live_tree == base_tree
        and git_info["worktree"] == "clean"
        and (not base_sha or git_info["head_sha"] == base_sha)
    )
    if is_exact_baseline:
        effective_label = f"v{base_ver}"
        candidate_state = "LOCKED_RELEASE_TAG"
    else:
        effective_label = f"v{base_ver}-dev+{live_tree[:8]}"
        candidate_state = "IN_FLIGHT_CANDIDATE"

    return {
        "effective_version": effective_label,
        "candidate_state": candidate_state,
        "base_version": base_ver,
        "baseline_tag": manifest.get("baseline_tag", f"v{base_ver}"),
        "baseline_head_sha": base_sha,
        "baseline_tree_hash": base_tree,
        "baseline_content_tree_hash": base_tree,
        "live_head_sha": git_info["head_sha"],
        "live_tree_hash": live_tree,
        "live_content_tree_hash": live_tree,
        "tree_hash_kind": "full_byte_merkle_content",
        "live_file_count": file_count,
        "worktree": git_info["worktree"],
        "dirty_files": git_info["dirty_files"],
        "branch": git_info["branch"],
        "tags": git_info["tags"],
        "head_tags": git_info["head_tags"],
        "authoritative_cleanroom_path": str(homunculus_dir),
        "remote_url": git_info["remote_url"],
        "schemas": {
            "contract_schema_version": manifest.get("contract_schema_version", "1.0"),
            "memory_schema_version": manifest.get("memory_schema_version", "1.1"),
            "benchmark_schema_version": manifest.get("benchmark_schema_version", "1.0"),
        },
        "version_history_count": len(manifest.get("version_history", [])),
    }


def ensure_git_tag(homunculus_dir: Path, tag_name: str, message: str) -> bool:
    """Create an annotated git tag if it does not already exist."""
    existing = subprocess.check_output(
        ["git", "-C", str(homunculus_dir), "tag", "-l", tag_name], text=True
    ).strip()
    if existing == tag_name:
        return False
    subprocess.check_call(
        [
            "git",
            "-C",
            str(homunculus_dir),
            "-c",
            "user.name=Orin",
            "-c",
            "user.email=109475365+Orin-Alchemical-3D@users.noreply.github.com",
            "tag",
            "-a",
            tag_name,
            "-m",
            message,
        ]
    )
    return True


def bump_version(
    manifest_path: Path,
    homunculus_dir: Path,
    bump_kind: str,
    reason: str,
    allow_v1_public: bool = False,
) -> dict[str, Any]:
    """Increment X.Y.Z according to locked digit trigger laws and tag the standalone Homunculus repo."""
    if not reason.strip():
        raise ValueError("--reason is required when bumping Homunculus version.")
    git_info = get_git_state(homunculus_dir)
    if git_info["worktree"] != "clean":
        raise RuntimeError(
            f"Cannot bump version while Homunculus worktree is {git_info['worktree']}. "
            f"Commit or stash changes inside {homunculus_dir} first."
        )

    manifest = load_or_create_manifest(manifest_path, homunculus_dir)
    cur_ver = str(manifest.get("engine_version", "0.1.0")).lstrip("v")
    m = SEMVER_RE.match(cur_ver)
    if not m:
        raise ValueError(f"Invalid current engine_version in manifest: {cur_ver}")
    major, minor, patch = int(m.group(1)), int(m.group(2)), int(m.group(3))

    if bump_kind == "major":
        if major == 0 and not allow_v1_public:
            raise RuntimeError(
                "Bumping 0.Y.Z -> 1.0.0 is reserved for public GitHub release. "
                "Pass --allow-v1-public-release only when deploying v1.0.0 publicly."
            )
        major += 1
        minor = 0
        patch = 0
    elif bump_kind == "minor":
        minor += 1
        patch = 0
    elif bump_kind == "patch":
        patch += 1
    else:
        raise ValueError(f"Unsupported bump kind: {bump_kind}")

    new_ver = f"{major}.{minor}.{patch}"
    new_tag = f"v{new_ver}"
    live_tree, file_count = compute_engine_tree_hash(homunculus_dir)

    ensure_git_tag(
        homunculus_dir,
        new_tag,
        f"Homunculus {new_tag} ({bump_kind}): {reason.strip()}",
    )

    manifest["engine_version"] = new_ver
    manifest["release_stage"] = "public_release" if major >= 1 else "development"
    manifest["baseline_tag"] = new_tag
    manifest["baseline_head_sha"] = git_info["head_sha"]
    manifest["baseline_tree_hash"] = live_tree
    manifest["baseline_file_count"] = file_count
    manifest["updated_at"] = dt.date.today().isoformat()
    history = list(manifest.get("version_history", []))
    history.append(
        {
            "version": new_ver,
            "tag": new_tag,
            "date": dt.date.today().isoformat(),
            "head_sha": git_info["head_sha"],
            "tree_hash": live_tree,
            "trigger_type": bump_kind,
            "reason": reason.strip(),
        }
    )
    manifest["version_history"] = history
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return resolve_effective_version_status(manifest_path, homunculus_dir)


def rollback_engine(
    manifest_path: Path,
    homunculus_dir: Path,
    target_ref: str,
    dry_run: bool = False,
) -> dict[str, Any]:
    """Roll back only the single-source Clean-Room `Homunculus` repository without touching `memory/`."""
    norm_ref = target_ref.strip()
    if SEMVER_RE.match(norm_ref) and not norm_ref.startswith("v"):
        norm_ref = f"v{norm_ref}"

    # Verify ref exists in Homunculus git repo
    try:
        resolved_sha = subprocess.check_output(
            ["git", "-C", str(homunculus_dir), "rev-parse", "--verify", f"{norm_ref}^{{commit}}"],
            text=True,
            stderr=subprocess.PIPE,
        ).strip()
    except subprocess.CalledProcessError as exc:
        raise RuntimeError(f"Target version/tag '{norm_ref}' not found in {homunculus_dir}: {exc.stderr.strip()}") from exc

    git_pre = get_git_state(homunculus_dir)
    plan = {
        "action": "DRY_RUN_ROLLBACK" if dry_run else "EXECUTED_ROLLBACK",
        "target_ref": norm_ref,
        "target_commit_sha": resolved_sha[:12],
        "previous_head_sha": git_pre["head_sha"],
        "previous_worktree": git_pre["worktree"],
        "memory_vault_touched": False,
        "stash_created": False,
    }
    if dry_run:
        return plan

    # Unlock core files temporarily if locked 0444/0555 so git checkout can update working tree
    hp_script = homunculus_dir / "scripts" / "homunculus_paths.py"
    if hp_script.is_file():
        subprocess.run([sys.executable, str(hp_script), "--unlock-core"], check=False, capture_output=True)

    if git_pre["dirty_files"]:
        stash_msg = f"pre-rollback-auto-stash-{dt.datetime.now().strftime('%Y%m%d_%H%M%S')}"
        subprocess.check_call(
            ["git", "-C", str(homunculus_dir), "stash", "push", "-u", "-m", stash_msg]
        )
        plan["stash_created"] = True
        plan["stash_label"] = stash_msg

    subprocess.check_call(["git", "-C", str(homunculus_dir), "checkout", norm_ref])

    if hp_script.is_file():
        subprocess.run([sys.executable, str(hp_script), "--lock-core"], check=False, capture_output=True)

    bootstrap_sh = ENGINEERING_ROOT / "scripts" / "bootstrap_workstation.sh"
    if bootstrap_sh.is_file():
        b_rc = subprocess.run(["bash", str(bootstrap_sh), "--check"], capture_output=True, text=True)
        plan["bootstrap_check_rc"] = b_rc.returncode

    post_tree, _ = compute_engine_tree_hash(homunculus_dir)
    plan["post_rollback_tree_hash"] = post_tree
    return plan


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Homunculus Development Workstation v0.Y.Z Version & Rollback Manager."
    )
    parser.add_argument(
        "--homunculus-dir",
        default=str(DEFAULT_HOMUNCULUS_DIR),
        help="Path to the single-source Clean-Room Homunculus repository.",
    )
    parser.add_argument(
        "--manifest",
        default=str(DEFAULT_MANIFEST_PATH),
        help="Path to homunculus_version.json manifest.",
    )
    parser.add_argument("--status", action="store_true", help="Display current version and tree provenance.")
    parser.add_argument(
        "--init-baseline",
        action="store_true",
        help="Initialize homunculus_version.json at v0.1.0 and create annotated tag v0.1.0.",
    )
    parser.add_argument(
        "--sync-manifest",
        action="store_true",
        help="Sync baseline_head_sha and baseline_tree_hash in homunculus_version.json with current HEAD.",
    )
    parser.add_argument(
        "--bump",
        choices=("major", "minor", "patch"),
        help="Bump X.Y.Z version digit according to locked trigger laws.",
    )
    parser.add_argument("--reason", default="", help="Engineering reason for version bump.")
    parser.add_argument(
        "--allow-v1-public-release",
        action="store_true",
        help="Explicitly authorize 0.Y.Z -> 1.0.0 transition for public GitHub release.",
    )
    parser.add_argument(
        "--rollback",
        metavar="TAG_OR_VERSION",
        help="Roll back Alchemical3D/Homunculus to a version tag/commit without touching memory/.",
    )
    parser.add_argument("--dry-run", action="store_true", help="Preview rollback plan without mutating files.")
    parser.add_argument("--json", action="store_true", help="Emit JSON output.")
    args = parser.parse_args(argv)

    hom_dir = Path(args.homunculus_dir).expanduser().resolve()
    manifest_path = Path(args.manifest).expanduser().resolve()

    if not hom_dir.is_dir():
        print(f"[BLOCKED] Homunculus directory not found: {hom_dir}", file=sys.stderr)
        return 2

    if args.init_baseline:
        manifest = load_or_create_manifest(manifest_path, hom_dir)
        tag_created = ensure_git_tag(
            hom_dir,
            "v0.1.0",
            "Homunculus v0.1.0 — Consolidated Single-Source Clean-Room Baseline (102 files, Stateful Memory v1.1)",
        )
        live_tree, file_count = compute_engine_tree_hash(hom_dir)
        git_info = get_git_state(hom_dir)
        manifest["baseline_head_sha"] = git_info["head_sha"]
        manifest["baseline_tree_hash"] = live_tree
        manifest["baseline_file_count"] = file_count
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        status = resolve_effective_version_status(manifest_path, hom_dir)
        status["tag_created"] = tag_created
        if args.json:
            print(json.dumps(status, indent=2))
        else:
            print(
                f"[PASS] Initialized Homunculus Baseline: {status['effective_version']} | "
                f"HEAD: {status['live_head_sha']} | Tree: {status['live_tree_hash']} "
                f"({status['live_file_count']} files) | Tag v0.1.0: {'CREATED' if tag_created else 'EXISTS'}"
            )
        return 0

    if args.sync_manifest:
        manifest = load_or_create_manifest(manifest_path, hom_dir)
        live_tree, file_count = compute_engine_tree_hash(hom_dir)
        git_info = get_git_state(hom_dir)
        manifest["baseline_head_sha"] = git_info["head_sha"]
        manifest["baseline_tree_hash"] = live_tree
        manifest["baseline_file_count"] = file_count
        manifest["updated_at"] = dt.date.today().isoformat()
        if manifest.get("version_history"):
            manifest["version_history"][-1]["head_sha"] = git_info["head_sha"]
            manifest["version_history"][-1]["tree_hash"] = live_tree
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    if args.bump:
        try:
            status = bump_version(
                manifest_path,
                hom_dir,
                args.bump,
                args.reason,
                allow_v1_public=args.allow_v1_public_release,
            )
        except Exception as exc:
            print(f"[BLOCKED] Version bump failed: {exc}", file=sys.stderr)
            return 1
        if args.json:
            print(json.dumps(status, indent=2))
        else:
            print(
                f"[PASS] Bumped Homunculus to {status['effective_version']} ({args.bump}) | "
                f"HEAD: {status['live_head_sha']} | Tree: {status['live_tree_hash']}"
            )
        return 0

    if args.rollback:
        try:
            rb_res = rollback_engine(manifest_path, hom_dir, args.rollback, dry_run=args.dry_run)
        except Exception as exc:
            print(f"[BLOCKED] Rollback failed: {exc}", file=sys.stderr)
            return 1
        if args.json:
            print(json.dumps(rb_res, indent=2))
        else:
            print(
                f"[{rb_res['action']}] Target: {rb_res['target_ref']} ({rb_res['target_commit_sha']}) | "
                f"Memory Touched: {rb_res['memory_vault_touched']} | Stash Created: {rb_res['stash_created']}"
            )
        return 0

    status = resolve_effective_version_status(manifest_path, hom_dir)
    if args.json:
        print(json.dumps(status, indent=2))
    else:
        print(
            f"=== Homunculus Version & Provenance Status ===\n"
            f"  Effective Version : {status['effective_version']} ({status['candidate_state']})\n"
            f"  Baseline Tag      : {status['baseline_tag']} (HEAD: {status['baseline_head_sha']} | Content Merkle: {status['baseline_content_tree_hash']})\n"
            f"  Live Engine State : HEAD {status['live_head_sha']} | Content Merkle {status['live_content_tree_hash']} ({status['live_file_count']} files | Worktree: {status['worktree']})\n"
            f"  Single Clean-Room : {status['authoritative_cleanroom_path']}\n"
            f"  Remote Backup     : {status['remote_url']}\n"
            f"  Git Tags          : {', '.join(status['tags']) if status['tags'] else 'none'}"
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
