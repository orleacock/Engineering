#!/usr/bin/env python3
"""
Homunculus Workstation Verified Fast-Path Receipt Cache (`verified_fastpath.py`).

Parent-only workstation accelerator (strictly outside clean-room `Homunculus`).
Stores deterministic pure-JSON (`0` `pickle`) SHA-256 verification receipts in
`<repo_root>/.cache/verified_fastpath.json` (`0600` atomic writes, `EROFS` fallback)
so unchanged deliverables, Stage-X memory audits, and multi-file checks short-circuit
in `< 20 ms` while immediately invalidating on any single-byte edit or missing file.

Security & Trust Boundary:
  - `audit_data_boundary.py` is NEVER cached here and ALWAYS executes live.
  - Supports global opt-out via `--force-fresh` or `HOMUNCULUS_DISABLE_FASTPATH=1`.
  - Pure Python 3.10+ standard library (zero third-party packages).

=== DEVELOPER & AI NAVIGATION MAP ===
  Owning Module : Workstation Operations (`scripts/verified_fastpath.py`)
  Callers       : `git_pre_commit_boundary.sh`, developer / parent CLI
  Callees       : Standard library only (`hashlib`, `json`, `tempfile`, `os`, `pathlib`)
  Contract      : `scripts/script_contracts.json` [`verified_fastpath.py`]
  CLI Flags     : --record-memory-audit, --check-memory-audit, --record-vrf, --check, --targets, --sources, --receipt, --memory-root, --homunculus-root, --repo, --force-fresh, --json
  Symbol Index  (jump directly via read_file StartLine/EndLine):
    - def _now_iso (#L60-L61)                        | def _is_fastpath_disabled (#L64-L69)
    - def _default_repo_root (#L72-L73)              | def resolve_homunculus_root (#L76-L114)
    - def _fallback_cache_path (#L117-L119)          | def resolve_cache_path (#L122-L135)
    - def _empty_store (#L138-L143)                  | def _load_store (#L146-L162)
    - def _write_json_atomic_0600 (#L165-L181)       | def _save_store_atomic (#L184-L193)
    - def _sha256_file (#L196-L206)                  | def _extract_frontmatter_local_path (#L209-L225)
    - def _resolve_mounted_repo_dir (#L228-L248)     | def _snapshot_mounted_repos (#L251-L286)
    - def compute_memory_audit_fingerprint (#L289-L343) | def record_memory_audit_fastpath (#L346-L378)
    - def check_memory_audit_fastpath (#L381-L429)   | def _expand_input_paths (#L432-L448)
    - def _vrf_record_key (#L451-L453)               | def _compute_vrf_bundle_sha256 (#L456-L470)
    - def record_vrf_fastpath (#L473-L531)           | def _verify_vrf_record (#L534-L599)
    - def _path_is_within (#L602-L603)               | def check_fastpath (#L606-L717)
    - def main (#L720-L801)
=== END NAVIGATION MAP ===
"""
from __future__ import annotations

import argparse
import datetime as dt
import errno
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Any

SCHEMA_VERSION = "VERIFIED_FASTPATH_V1"
VRF_RECEIPT_RE = re.compile(r"^VRF-[0-9a-fA-F]{12}$")
_SKIP_DIRS = frozenset({".git", "__pycache__", ".cache", ".trash", ".pytest_cache", "node_modules"})
_EROFS_ERRNOS = {errno.EROFS, errno.EACCES, errno.EPERM}


def _now_iso() -> str:
    return dt.datetime.now().astimezone().isoformat(timespec="seconds")


def _is_fastpath_disabled(force_fresh: bool = False) -> tuple[bool, str]:
    if force_fresh:
        return True, "force_fresh"
    if os.environ.get("HOMUNCULUS_DISABLE_FASTPATH", "").strip() == "1":
        return True, "fastpath_disabled"
    return False, ""


def _default_repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


def resolve_homunculus_root(
    explicit_root: str | Path | None = None,
    *,
    anchor: Path | None = None,
) -> Path | None:
    """Dynamically locate Homunculus root without hardcoded workstation paths."""
    if explicit_root:
        cand = Path(explicit_root).expanduser().resolve()
        if cand.is_dir():
            return cand
    env_root = os.environ.get("HOMUNCULUS_ROOT", "").strip()
    if env_root:
        cand = Path(env_root).expanduser().resolve()
        if (cand / "HOMUNCULUS_START_HERE.md").is_file():
            return cand
    bases: list[Path] = []
    if anchor is not None:
        bases.extend([anchor.resolve(), *anchor.resolve().parents])
    default_repo = _default_repo_root()
    bases.extend([default_repo, *default_repo.parents])
    seen: set[Path] = set()
    for base in bases:
        if base in seen:
            continue
        seen.add(base)
        cfg = base / ".homunculus.json"
        if cfg.is_file():
            try:
                rel = json.loads(cfg.read_text(encoding="utf-8")).get("homunculus_rel_path", "")
                if rel:
                    cand = (base / rel).resolve()
                    if (cand / "HOMUNCULUS_START_HERE.md").is_file():
                        return cand
            except (OSError, json.JSONDecodeError, TypeError, ValueError):
                pass
        for cand in (base, base / "Homunculus", base / "Alchemical3D" / "Homunculus"):
            if (cand / "HOMUNCULUS_START_HERE.md").is_file():
                return cand.resolve()
    return None


def _fallback_cache_path(primary: Path) -> Path:
    digest12 = hashlib.sha256(str(primary.resolve()).encode("utf-8")).hexdigest()[:12]
    return Path(tempfile.gettempdir()) / f"homunculus_fastpath_{digest12}.json"


def resolve_cache_path(
    *,
    repo_root: Path | None = None,
    memory_root: Path | None = None,
) -> Path:
    """Resolve primary fast-path JSON cache file inside `.cache/verified_fastpath.json`."""
    if repo_root is not None:
        return repo_root.expanduser().resolve() / ".cache" / "verified_fastpath.json"
    default_repo = _default_repo_root()
    if memory_root is not None:
        mem = memory_root.expanduser().resolve()
        if mem != default_repo and default_repo not in mem.parents:
            return mem / ".cache" / "verified_fastpath.json"
    return default_repo / ".cache" / "verified_fastpath.json"


def _empty_store() -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "memory_audits": {},
        "vrf_records": {},
    }


def _load_store(primary_path: Path) -> tuple[dict[str, Any], Path]:
    candidates = [primary_path, _fallback_cache_path(primary_path)]
    for cand in candidates:
        if not cand.is_file():
            continue
        try:
            data = json.loads(cand.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if (
            isinstance(data, dict)
            and data.get("schema_version") == SCHEMA_VERSION
            and isinstance(data.get("memory_audits"), dict)
            and isinstance(data.get("vrf_records"), dict)
        ):
            return data, cand
    return _empty_store(), primary_path


def _write_json_atomic_0600(target: Path, payload: dict[str, Any]) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    serialized = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    fd, tmp_name = tempfile.mkstemp(prefix=".vf_", suffix=".tmp", dir=str(target.parent))
    tmp_path = Path(tmp_name)
    try:
        os.chmod(tmp_path, 0o600)
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            fh.write(serialized)
        os.chmod(tmp_path, 0o600)
        os.replace(tmp_path, target)
    except BaseException:
        try:
            tmp_path.unlink(missing_ok=True)
        except OSError:
            pass
        raise


def _save_store_atomic(primary_path: Path, payload: dict[str, Any]) -> Path:
    try:
        _write_json_atomic_0600(primary_path, payload)
        return primary_path
    except OSError as exc:
        if exc.errno in _EROFS_ERRNOS:
            fb = _fallback_cache_path(primary_path)
            _write_json_atomic_0600(fb, payload)
            return fb
        raise


def _sha256_file(path: Path) -> tuple[str, int]:
    h = hashlib.sha256()
    size = 0
    with path.open("rb") as fh:
        while True:
            chunk = fh.read(65536)
            if not chunk:
                break
            size += len(chunk)
            h.update(chunk)
    return h.hexdigest(), size


def _extract_frontmatter_local_path(hub_path: Path) -> str:
    try:
        lines = hub_path.read_text(encoding="utf-8", errors="ignore").splitlines()
    except OSError:
        return ""
    if not lines or lines[0].strip() != "---":
        return ""
    for ln in lines[1:40]:
        s = ln.strip()
        if s == "---":
            break
        if s.lower().startswith("local_path:"):
            val = s.split(":", 1)[1].strip()
            if len(val) >= 2 and val[0] == val[-1] and val[0] in ("'", '"'):
                val = val[1:-1]
            return val.strip().replace("\\", "/")
    return ""


def _resolve_mounted_repo_dir(mem: Path, hub_path: Path, hom: Path | None) -> Path | None:
    raw_lp = _extract_frontmatter_local_path(hub_path)
    if not raw_lp:
        return None
    cand = Path(raw_lp)
    if not cand.is_absolute():
        cand = Path(os.path.normpath(os.path.join(os.fspath(mem), raw_lp)))
    if cand.is_dir() and os.path.realpath(cand) != os.path.realpath(hub_path.parent):
        return cand.resolve()
    raw_parts = [p for p in raw_lp.split("/") if p]
    repo_base = raw_parts[-1] if raw_parts else hub_path.stem
    parent_grp = raw_parts[-2] if len(raw_parts) >= 2 else ""
    if repo_base.lower() == "homunculus" and hom is not None and hom.is_dir():
        return hom.resolve()
    for base in (mem.parent, mem.parent.parent):
        if not base.is_dir():
            continue
        for re_cand in ((base / parent_grp / repo_base) if parent_grp else None, base / repo_base):
            if re_cand is not None and re_cand.is_dir() and re_cand.resolve() not in (hub_path.parent.resolve(), mem):
                return re_cand.resolve()
    return None


def _snapshot_mounted_repos(mem: Path, hom: Path | None) -> dict[str, list[Any]]:
    out: dict[str, list[Any]] = {}
    proj_dir = mem / "Projects"
    if not proj_dir.is_dir():
        return out
    for hub in sorted(proj_dir.glob("*/*.md")):
        if hub.stem != hub.parent.name:
            continue
        key = f"__repo__/{hub.stem}"
        mounted = _resolve_mounted_repo_dir(mem, hub, hom)
        if mounted is None:
            out[key] = ["DETACHED", -1]
            continue
        if not (mounted / ".git").exists():
            out[key] = ["UNTRACKED", 0]
            continue
        try:
            hp = subprocess.run(
                ["git", "-C", str(mounted), "rev-parse", "HEAD"],
                capture_output=True, text=True, timeout=2, check=False,
            )
            sp = subprocess.run(
                ["git", "-C", str(mounted), "status", "--porcelain"],
                capture_output=True, text=True, timeout=2, check=False,
            )
            head = hp.stdout.strip() if hp.returncode == 0 else "NO_HEAD"
            porc_lines = [ln.strip() for ln in sp.stdout.splitlines() if ln.strip()] if sp.returncode == 0 else ["STATUS_ERR"]
            if sp.returncode == 0:
                payload = "\n".join([head, *porc_lines]).encode("utf-8")
                digest = hashlib.sha256(payload).hexdigest()
            else:
                digest = "GIT_ERR"
            out[key] = [digest, len(porc_lines)]
        except (subprocess.SubprocessError, OSError):
            out[key] = ["GIT_ERR", -1]
    return out


def compute_memory_audit_fingerprint(
    memory_root: Path,
    homunculus_root: Path | None = None,
) -> dict[str, Any]:
    """Compute a deterministic Merkle SHA-256 fingerprint across `memory_root/`, validators & mounted repos."""
    mem = memory_root.expanduser().resolve()
    hom = (
        homunculus_root.expanduser().resolve()
        if homunculus_root is not None
        else resolve_homunculus_root(anchor=mem)
    )
    if not mem.is_dir():
        raise FileNotFoundError(f"Memory root does not exist: {mem}")

    file_hashes: dict[str, list[Any]] = {}
    for root_str, dirs, files in os.walk(mem, followlinks=False):
        dirs[:] = sorted(d for d in dirs if d not in _SKIP_DIRS)
        root_p = Path(root_str)
        rel_dir = root_p.relative_to(mem).as_posix()
        for fname in sorted(files):
            if rel_dir == ".obsidian" and fname.startswith("workspace") and fname.endswith(".json"):
                continue
            fpath = root_p / fname
            if fpath.is_symlink() or not fpath.is_file():
                continue
            rel_p = fpath.relative_to(mem).as_posix()
            digest, sz = _sha256_file(fpath)
            file_hashes[rel_p] = [digest, sz]

    sentinel_scripts = {
        "__homunculus__/sync_memory.py": (hom / "skills" / "project-memory" / "scripts" / "sync_memory.py") if hom else None,
        "__homunculus__/homunculus_paths.py": (hom / "scripts" / "homunculus_paths.py") if hom else None,
        "__homunculus__/audit_memory_hygiene.py": (hom / "skills" / "memory-hygiene" / "scripts" / "audit_memory_hygiene.py") if hom else None,
    }
    for key, spath in sentinel_scripts.items():
        if spath is not None and spath.is_file():
            digest, sz = _sha256_file(spath)
            file_hashes[key] = [digest, sz]
        else:
            file_hashes[key] = ["MISSING", -1]

    file_hashes.update(_snapshot_mounted_repos(mem, hom))

    ordered_items = [[k, file_hashes[k][0], file_hashes[k][1]] for k in sorted(file_hashes)]
    tree_sha256 = hashlib.sha256(
        json.dumps(ordered_items, separators=(",", ":"), sort_keys=False).encode("utf-8")
    ).hexdigest()

    return {
        "memory_root": str(mem),
        "homunculus_root": str(hom) if hom else "",
        "file_count": len(file_hashes),
        "tree_sha256": tree_sha256,
        "file_hashes": file_hashes,
    }


def record_memory_audit_fastpath(
    memory_root: Path,
    homunculus_root: Path | None = None,
    repo_root: Path | None = None,
) -> dict[str, Any]:
    """Record a passing Stage-X `sync_memory.py --audit` receipt in the fast-path cache."""
    mem = memory_root.expanduser().resolve()
    hom = (
        homunculus_root.expanduser().resolve()
        if homunculus_root is not None
        else resolve_homunculus_root(anchor=mem)
    )
    fp = compute_memory_audit_fingerprint(mem, hom)
    primary = resolve_cache_path(repo_root=repo_root, memory_root=mem)
    store, _ = _load_store(primary)
    store["memory_audits"][str(mem)] = {
        "memory_root": str(mem),
        "homunculus_root": fp["homunculus_root"],
        "repo_root": str(repo_root.expanduser().resolve()) if repo_root else "",
        "tree_sha256": fp["tree_sha256"],
        "file_count": fp["file_count"],
        "file_hashes": fp["file_hashes"],
        "recorded_at": _now_iso(),
    }
    saved_path = _save_store_atomic(primary, store)
    return {
        "status": "RECORDED",
        "kind": "memory_audit",
        "memory_root": str(mem),
        "tree_sha256": fp["tree_sha256"],
        "file_count": fp["file_count"],
        "cache_file": str(saved_path),
    }


def check_memory_audit_fastpath(
    memory_root: Path,
    homunculus_root: Path | None = None,
    repo_root: Path | None = None,
    force_fresh: bool = False,
) -> dict[str, Any]:
    """Verify whether the recorded Stage-X `sync_memory.py --audit` fingerprint still matches disk."""
    mem = memory_root.expanduser().resolve()
    disabled, why = _is_fastpath_disabled(force_fresh)
    if disabled:
        return {"hit": False, "reason": why, "memory_root": str(mem), "tree_sha256": ""}

    primary = resolve_cache_path(repo_root=repo_root, memory_root=mem)
    store, cache_used = _load_store(primary)
    rec = store.get("memory_audits", {}).get(str(mem))
    if not isinstance(rec, dict):
        return {
            "hit": False,
            "reason": "no_recorded_entry",
            "memory_root": str(mem),
            "cache_file": str(cache_used),
        }

    rec_hom_str = str(rec.get("homunculus_root", "")).strip()
    hom = (
        homunculus_root.expanduser().resolve()
        if homunculus_root is not None
        else (Path(rec_hom_str) if rec_hom_str else resolve_homunculus_root(anchor=mem))
    )
    try:
        fp = compute_memory_audit_fingerprint(mem, hom)
    except OSError as exc:
        return {"hit": False, "reason": f"fingerprint_error:{exc}", "memory_root": str(mem)}

    matched = (
        fp["tree_sha256"] == rec.get("tree_sha256")
        and fp["file_count"] == rec.get("file_count")
        and fp["file_hashes"] == rec.get("file_hashes")
    )
    return {
        "hit": matched,
        "reason": "verified_match" if matched else "hash_drift",
        "memory_root": str(mem),
        "tree_sha256": fp["tree_sha256"],
        "recorded_tree_sha256": rec.get("tree_sha256", ""),
        "file_count": fp["file_count"],
        "recorded_at": rec.get("recorded_at", ""),
        "cache_file": str(cache_used),
    }


def _expand_input_paths(raw_paths: list[str | Path]) -> list[Path]:
    expanded: set[Path] = set()
    for item in raw_paths:
        p = Path(item).expanduser().resolve()
        if p.is_file():
            expanded.add(p)
        elif p.is_dir():
            for root_str, dirs, files in os.walk(p, followlinks=False):
                dirs[:] = sorted(d for d in dirs if d not in _SKIP_DIRS)
                root_p = Path(root_str)
                for fname in sorted(files):
                    fp = root_p / fname
                    if not fp.is_symlink() and fp.is_file():
                        expanded.add(fp.resolve())
        else:
            raise FileNotFoundError(f"Input path does not exist or is not readable: {p}")
    return sorted(expanded)


def _vrf_record_key(target_paths: list[Path]) -> str:
    joined = json.dumps([str(p) for p in sorted(target_paths)], separators=(",", ":"))
    return hashlib.sha256(joined.encode("utf-8")).hexdigest()[:16]


def _compute_vrf_bundle_sha256(
    receipt: str,
    target_hashes: dict[str, str],
    source_hashes: dict[str, str],
    verifier_sha256: str,
) -> str:
    payload = {
        "receipt": receipt.upper(),
        "targets": [[k, target_hashes[k]] for k in sorted(target_hashes)],
        "sources": [[k, source_hashes[k]] for k in sorted(source_hashes)],
        "verifier_sha256": verifier_sha256,
    }
    return hashlib.sha256(
        json.dumps(payload, separators=(",", ":"), sort_keys=False).encode("utf-8")
    ).hexdigest()


def record_vrf_fastpath(
    targets: list[str | Path],
    sources: list[str | Path],
    receipt: str,
    *,
    homunculus_root: Path | None = None,
    repo_root: Path | None = None,
) -> dict[str, Any]:
    """Record a verified `verify_claims.py` `VRF-<12hex>` bundle receipt."""
    clean_receipt = receipt.strip().upper()
    if not VRF_RECEIPT_RE.match(clean_receipt):
        raise ValueError(f"Invalid VRF receipt format (expected VRF-<12hex>): {receipt!r}")
    if not targets:
        raise ValueError("--targets must specify at least one target file")
    if not sources:
        raise ValueError("--sources must specify at least one authoritative source")

    target_paths = _expand_input_paths(targets)
    source_paths = _expand_input_paths(sources)
    if not target_paths or not source_paths:
        raise ValueError("Expanded --targets and --sources must both be non-empty")

    anchor = repo_root or target_paths[0].parent
    hom = homunculus_root.expanduser().resolve() if homunculus_root is not None else resolve_homunculus_root(anchor=anchor)
    verify_script = (hom / "skills" / "claim-verification" / "scripts" / "verify_claims.py") if hom else None
    verifier_sha256 = _sha256_file(verify_script)[0] if verify_script and verify_script.is_file() else ""

    target_hashes = {str(p): _sha256_file(p)[0] for p in target_paths}
    source_hashes = {str(p): _sha256_file(p)[0] for p in source_paths}
    bundle_sha256 = _compute_vrf_bundle_sha256(clean_receipt, target_hashes, source_hashes, verifier_sha256)

    rec_key = _vrf_record_key(target_paths)
    eff_repo = repo_root.expanduser().resolve() if repo_root else _default_repo_root()
    primary = resolve_cache_path(repo_root=eff_repo)
    store, _ = _load_store(primary)
    store["vrf_records"][rec_key] = {
        "record_key": rec_key,
        "receipt": clean_receipt,
        "repo_root": str(eff_repo),
        "homunculus_root": str(hom) if hom else "",
        "verifier_sha256": verifier_sha256,
        "targets": [str(p) for p in target_paths],
        "sources": [str(p) for p in source_paths],
        "target_hashes": target_hashes,
        "source_hashes": source_hashes,
        "bundle_sha256": bundle_sha256,
        "recorded_at": _now_iso(),
    }
    saved_path = _save_store_atomic(primary, store)
    return {
        "status": "RECORDED",
        "kind": "vrf_bundle",
        "record_key": rec_key,
        "receipt": clean_receipt,
        "bundle_sha256": bundle_sha256,
        "target_count": len(target_paths),
        "source_count": len(source_paths),
        "cache_file": str(saved_path),
    }


def _verify_vrf_record(
    rec: dict[str, Any],
    *,
    homunculus_root: Path | None = None,
    expected_sources: list[str | Path] | None = None,
) -> dict[str, Any]:
    receipt = str(rec.get("receipt", "")).upper()
    if not VRF_RECEIPT_RE.match(receipt):
        return {"hit": False, "reason": "invalid_receipt_schema", "receipt": receipt}

    t_hashes = rec.get("target_hashes", {})
    s_hashes = rec.get("source_hashes", {})
    if not isinstance(t_hashes, dict) or not isinstance(s_hashes, dict) or not t_hashes or not s_hashes:
        return {"hit": False, "reason": "corrupt_record_hashes", "receipt": receipt}

    if expected_sources is not None:
        try:
            exp_src_set = {str(p) for p in _expand_input_paths(expected_sources)}
        except FileNotFoundError as exc:
            return {"hit": False, "reason": f"missing_source:{exc}", "receipt": receipt}
        if exp_src_set != set(s_hashes.keys()):
            return {"hit": False, "reason": "source_set_mismatch", "receipt": receipt}

    cur_target_hashes: dict[str, str] = {}
    for path_str, expected_sha in t_hashes.items():
        p = Path(path_str)
        if not p.is_file():
            return {"hit": False, "reason": f"missing_target:{path_str}", "receipt": receipt}
        cur_sha = _sha256_file(p)[0]
        if cur_sha != expected_sha:
            return {"hit": False, "reason": f"target_drift:{path_str}", "receipt": receipt}
        cur_target_hashes[path_str] = cur_sha

    cur_source_hashes: dict[str, str] = {}
    for path_str, expected_sha in s_hashes.items():
        p = Path(path_str)
        if not p.is_file():
            return {"hit": False, "reason": f"missing_source:{path_str}", "receipt": receipt}
        cur_sha = _sha256_file(p)[0]
        if cur_sha != expected_sha:
            return {"hit": False, "reason": f"source_drift:{path_str}", "receipt": receipt}
        cur_source_hashes[path_str] = cur_sha

    rec_verifier_sha = str(rec.get("verifier_sha256", ""))
    cur_verifier_sha = ""
    if rec_verifier_sha:
        rec_hom_str = str(rec.get("homunculus_root", ""))
        hom = homunculus_root or (Path(rec_hom_str) if rec_hom_str else resolve_homunculus_root())
        verify_script = (hom / "skills" / "claim-verification" / "scripts" / "verify_claims.py") if hom else None
        if verify_script is None or not verify_script.is_file():
            return {"hit": False, "reason": "verifier_script_missing", "receipt": receipt}
        cur_verifier_sha = _sha256_file(verify_script)[0]
        if cur_verifier_sha != rec_verifier_sha:
            return {"hit": False, "reason": "verifier_script_drift", "receipt": receipt}

    recomputed_bundle = _compute_vrf_bundle_sha256(receipt, cur_target_hashes, cur_source_hashes, cur_verifier_sha)
    if recomputed_bundle != rec.get("bundle_sha256"):
        return {"hit": False, "reason": "bundle_tamper", "receipt": receipt}

    return {
        "hit": True,
        "reason": "verified_match",
        "receipt": receipt,
        "bundle_sha256": recomputed_bundle,
        "targets": list(cur_target_hashes.keys()),
    }


def _path_is_within(child: Path, parent: Path) -> bool:
    return child == parent or parent in child.parents


def check_fastpath(
    scope_or_repo: str | Path | None = None,
    *,
    targets: list[str | Path] | None = None,
    sources: list[str | Path] | None = None,
    memory_root: Path | None = None,
    homunculus_root: Path | None = None,
    repo_root: Path | None = None,
    force_fresh: bool = False,
) -> dict[str, Any]:
    """Fail-closed check for target VRF receipts and/or scoped repo/memory receipts."""
    disabled, why = _is_fastpath_disabled(force_fresh)
    if disabled:
        return {"hit": False, "reason": why, "checked_count": 0, "entries": []}

    eff_repo = repo_root.expanduser().resolve() if repo_root else None
    if eff_repo is None and scope_or_repo is not None:
        cand = Path(scope_or_repo).expanduser().resolve()
        for base in (cand, *cand.parents):
            if (base / ".cache" / "verified_fastpath.json").is_file() or (base / ".git").exists():
                eff_repo = base
                break

    primary = resolve_cache_path(repo_root=eff_repo, memory_root=memory_root)
    store, cache_used = _load_store(primary)

    if targets:
        try:
            target_paths = _expand_input_paths(targets)
        except FileNotFoundError as exc:
            return {"hit": False, "reason": f"missing_target:{exc}", "checked_count": 0, "entries": []}
        rec_key = _vrf_record_key(target_paths)
        rec = store.get("vrf_records", {}).get(rec_key)
        if not isinstance(rec, dict):
            return {
                "hit": False,
                "reason": "no_recorded_vrf",
                "record_key": rec_key,
                "checked_count": 0,
                "cache_file": str(cache_used),
                "entries": [],
            }
        res = _verify_vrf_record(
            rec,
            homunculus_root=homunculus_root,
            expected_sources=sources if sources else None,
        )
        return {
            "hit": res["hit"],
            "reason": res["reason"],
            "checked_count": 1,
            "cache_file": str(cache_used),
            "entries": [res],
        }

    scope_path = (
        Path(scope_or_repo).expanduser().resolve()
        if scope_or_repo is not None
        else (eff_repo or _default_repo_root())
    )
    entries: list[dict[str, Any]] = []
    all_ok = True

    for rec in store.get("vrf_records", {}).values():
        if not isinstance(rec, dict):
            continue
        t_paths = [Path(p).resolve() for p in rec.get("targets", [])]
        rec_repo = Path(str(rec.get("repo_root", ""))).resolve() if rec.get("repo_root") else None
        if (t_paths and all(_path_is_within(tp, scope_path) for tp in t_paths)) or (rec_repo == scope_path):
            res = _verify_vrf_record(rec, homunculus_root=homunculus_root)
            entries.append({"kind": "vrf_bundle", **res})
            if not res["hit"]:
                all_ok = False

    mem_candidates: list[Path] = []
    if memory_root is not None:
        mem_candidates.append(memory_root.expanduser().resolve())
    for mem_key_str in store.get("memory_audits", {}):
        mk = Path(mem_key_str).resolve()
        if _path_is_within(mk, scope_path):
            if mk not in mem_candidates:
                mem_candidates.append(mk)

    for mc in mem_candidates:
        mres = check_memory_audit_fastpath(
            mc,
            homunculus_root=homunculus_root,
            repo_root=eff_repo,
            force_fresh=force_fresh,
        )
        entries.append({"kind": "memory_audit", **mres})
        if not mres["hit"]:
            all_ok = False

    if not entries:
        return {
            "hit": False,
            "reason": "no_recorded_entries",
            "scope": str(scope_path),
            "checked_count": 0,
            "cache_file": str(cache_used),
            "entries": [],
        }

    return {
        "hit": all_ok,
        "reason": "verified_match" if all_ok else "drift_detected",
        "scope": str(scope_path),
        "checked_count": len(entries),
        "cache_file": str(cache_used),
        "entries": entries,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Workstation-local verified fast-path SHA-256 receipt cache (never caches boundary security scans)."
    )
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--record-memory-audit", action="store_true", help="Record passing Stage-X memory audit tree hash.")
    mode.add_argument("--check-memory-audit", action="store_true", help="Verify Stage-X memory audit tree hash matches cache.")
    mode.add_argument("--record-vrf", action="store_true", help="Record a VRF-<12hex> receipt for targets and sources.")
    mode.add_argument(
        "--check",
        nargs="?",
        const=".",
        default=None,
        metavar="PROJECT_OR_REPO",
        help="Check cached VRF receipts (with --targets) or all entries under PROJECT_OR_REPO.",
    )
    parser.add_argument("--targets", nargs="+", default=[], help="Target deliverable files for VRF recording/checking.")
    parser.add_argument("--sources", nargs="+", default=[], help="Authoritative source files/dirs for VRF recording/checking.")
    parser.add_argument("--receipt", default="", help="Verified VRF-<12hex> receipt token for --record-vrf.")
    parser.add_argument("--memory-root", default="", help="Path to Dual-Mode memory root.")
    parser.add_argument("--homunculus-root", default="", help="Path to Homunculus framework root.")
    parser.add_argument("--repo", default="", help="Repository root containing `.cache/verified_fastpath.json`.")
    parser.add_argument("--force-fresh", action="store_true", help="Force cache miss / bypass fast-path.")
    parser.add_argument("--json", action="store_true", help="Emit JSON result.")

    args = parser.parse_args(argv)
    t0 = time.perf_counter()

    repo_p = Path(args.repo).expanduser().resolve() if args.repo else None
    hom_p = Path(args.homunculus_root).expanduser().resolve() if args.homunculus_root else None
    mem_p = Path(args.memory_root).expanduser().resolve() if args.memory_root else None

    try:
        if args.record_memory_audit:
            if mem_p is None:
                parser.error("--record-memory-audit requires --memory-root")
            res = record_memory_audit_fastpath(mem_p, hom_p, repo_p)
            rc = 0
        elif args.check_memory_audit:
            if mem_p is None:
                parser.error("--check-memory-audit requires --memory-root")
            res = check_memory_audit_fastpath(mem_p, hom_p, repo_p, force_fresh=args.force_fresh)
            rc = 0 if res.get("hit") else 1
        elif args.record_vrf:
            res = record_vrf_fastpath(
                args.targets,
                args.sources,
                args.receipt,
                homunculus_root=hom_p,
                repo_root=repo_p,
            )
            rc = 0
        else:
            scope = None if args.targets else (args.check if args.check != "." or repo_p is None else str(repo_p))
            res = check_fastpath(
                scope,
                targets=args.targets or None,
                sources=args.sources or None,
                memory_root=mem_p,
                homunculus_root=hom_p,
                repo_root=repo_p,
                force_fresh=args.force_fresh,
            )
            rc = 0 if res.get("hit") else 1
    except (FileNotFoundError, ValueError, OSError) as exc:
        err = {"status": "ERROR", "hit": False, "reason": str(exc)}
        if args.json:
            print(json.dumps(err, indent=2))
        else:
            print(f"[FASTPATH ERROR] {exc}", file=sys.stderr)
        return 2

    res["elapsed_ms"] = round((time.perf_counter() - t0) * 1000.0, 2)
    if args.json:
        print(json.dumps(res, indent=2))
    else:
        if "hit" in res:
            tag = "HIT" if res["hit"] else "MISS"
            print(f"[FASTPATH {tag}] reason={res.get('reason')} ({res['elapsed_ms']} ms)")
        else:
            print(f"[FASTPATH {res.get('status', 'OK')}] {res.get('kind')} ({res['elapsed_ms']} ms)")
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
