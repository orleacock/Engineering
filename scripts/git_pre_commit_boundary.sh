#!/usr/bin/env bash
# Homunculus Universal Git Pre-Commit Boundary & Memory Integrity Gate
# Governed by: 1. Accuracy & Truth -> 2. Efficiency -> 3. Data Safety -> 4. Speed
# Dynamically resolves Homunculus root via .homunculus.json or relative Homunculus/ folder (zero hardcoded paths).
# === DEVELOPER & AI NAVIGATION MAP ===
#   Owning Module : Parent Workstation Pre-Commit Boundary, Memory & Matrix Parity Gate (`scripts/git_pre_commit_boundary.sh`)
#   Callees       : `homunculus_paths.py`, `audit_data_boundary.py --staged`, `sync_memory.py`, AST Matrix Parity Gate against `Homunculus_Script_Skill_Interaction_Matrix.md`
#   Section Index : Repo Root (#L12-L19) | Python Discovery (#L21-L29) | Single-Process Gate & AST Matrix Parity (#L32-L249)
# === END NAVIGATION MAP ===
set -euo pipefail

CALLER_DIR="$(cd "$(dirname "$0")" && pwd)"
if [[ "$(basename "$CALLER_DIR")" == "hooks" && "$(basename "$(dirname "$CALLER_DIR")")" == ".git" ]]; then
    REPO_ROOT="$(cd "${CALLER_DIR}/../.." && pwd)"
elif REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null)"; then
    :
else
    REPO_ROOT="$(git -C "$CALLER_DIR" rev-parse --show-toplevel)"
fi

PYTHON_BIN=""
if command -v python3 >/dev/null 2>&1; then
    PYTHON_BIN="python3"
elif command -v python >/dev/null 2>&1; then
    PYTHON_BIN="python"
else
    echo "[BLOCKED] Python 3.10+ is required to run Homunculus pre-commit boundary verification." >&2
    exit 1
fi

# Run boundary, kernel seal, memory audit, and AST Matrix parity inside one Python process
exec "$PYTHON_BIN" - "$REPO_ROOT" "$PYTHON_BIN" << 'PY'
import ast
import contextlib
import io
import json
import os
import re
import subprocess
import sys
from pathlib import Path

repo = Path(sys.argv[1]).resolve()
python_bin = sys.argv[2]

def resolve_homunculus_root() -> Path | None:
    env_root = os.environ.get("HOMUNCULUS_ROOT", "").strip()
    if env_root and Path(env_root).is_dir():
        return Path(env_root).resolve()
    for d in (repo, *repo.parents):
        cfg = d / ".homunculus.json"
        if cfg.is_file():
            try:
                rel = json.loads(cfg.read_text(encoding="utf-8")).get("homunculus_rel_path", "")
                if rel:
                    cand = (d / rel).resolve()
                    if (cand / "HOMUNCULUS_START_HERE.md").is_file():
                        return cand
            except Exception:
                pass
        for cand in (
            d,
            d / "Homunculus",
            d / "Alchemical3D" / "Homunculus",
        ):
            if (cand / "HOMUNCULUS_START_HERE.md").is_file():
                return cand.resolve()
    return None

hom_root = resolve_homunculus_root()
if hom_root is None or not (hom_root / "scripts" / "audit_data_boundary.py").is_file():
    print(f"[BLOCKED] Could not resolve Homunculus root from {repo}. Set HOMUNCULUS_ROOT or run install.sh.", file=sys.stderr)
    sys.exit(1)

lease_file = hom_root / ".cache" / "sudo_lease.json"
if lease_file.is_file():
    print(
        f"[OPEN_SUDO_LEASE_COMMIT_BLOCKED] Active Ring-0 sudo lease detected ({lease_file}). "
        "Seal Ring-0 via 'h-sudo seal' before committing.",
        file=sys.stderr,
    )
    sys.exit(1)

scripts_dir = str(hom_root / "scripts")
if scripts_dir not in sys.path:
    sys.path.insert(0, scripts_dir)

if (hom_root / "scripts" / "kernel_seal.json").is_file():
    import homunculus_paths
    rc = homunculus_paths.main(["--homunculus-root", str(hom_root), "--verify-seal", "--quiet"])
    if rc:
        sys.exit(int(rc))

if not os.environ.get("HOMUNCULUS_BOUNDARY_CONFIG", "").strip():
    for cand in (
        repo / "homunculus_safety.json",
        hom_root.parent / "homunculus_safety.json",
        hom_root.parent.parent / "Engineering" / "homunculus_safety.json",
    ):
        if cand.is_file():
            os.environ["HOMUNCULUS_BOUNDARY_CONFIG"] = str(cand.resolve())
            break

import audit_data_boundary
rc = audit_data_boundary.main(["--repo", str(repo), "--staged"])
if rc:
    sys.exit(int(rc))

staged = subprocess.check_output(
    ["git", "-C", str(repo), "-c", "core.quotePath=false", "diff", "--cached", "--name-only"],
    text=True,
    errors="replace",
).splitlines()

# Memory Integrity Gate
mem_script = hom_root / "skills" / "project-memory" / "scripts" / "sync_memory.py"
mem_dir: Path | None = None
cfg_file = repo / ".homunculus.json"
if cfg_file.is_file():
    try:
        rel_mem = json.loads(cfg_file.read_text(encoding="utf-8")).get("memory_dir", "")
        if rel_mem:
            cand_m = (repo / rel_mem).resolve()
            if cand_m.is_dir() and repo in (cand_m, *cand_m.parents):
                mem_dir = cand_m
    except Exception:
        pass
if mem_dir is None and (repo / "memory").is_dir():
    mem_dir = (repo / "memory").resolve()

if mem_script.is_file() and mem_dir is not None and mem_dir.is_dir():
    mem_rel = mem_dir.relative_to(repo).as_posix().rstrip("/")
    if any(p.startswith(f"{mem_rel}/") for p in staged):
        mem_scripts_dir = str(mem_script.parent)
        if mem_scripts_dir not in sys.path:
            sys.path.insert(0, mem_scripts_dir)
        import sync_memory
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
            mem_rc = sync_memory.main(["--memory-root", str(mem_dir), "--audit"])
        if mem_rc:
            print(
                f"[BLOCKED] Homunculus pre-commit memory gate failed (run: {python_bin} {mem_script} --memory-root {mem_dir} --audit):",
                file=sys.stderr,
            )
            out = buf.getvalue().rstrip()
            if out:
                print(out, file=sys.stderr)
            sys.exit(1)

# Maintainer Script-Skill Interaction Matrix Parity Gate (active when Engineering maintainer matrix exists)
matrix_path: Path | None = None
env_mx = os.environ.get("HOMUNCULUS_MATRIX_PATH", "").strip()
cand_repo_mx = repo / "memory" / "Projects" / "Homunculus" / "Homunculus_Script_Skill_Interaction_Matrix.md"
cand_eng_mx = hom_root.parent.parent / "Engineering" / "memory" / "Projects" / "Homunculus" / "Homunculus_Script_Skill_Interaction_Matrix.md"
if env_mx and Path(env_mx).is_file():
    matrix_path = Path(env_mx).resolve()
elif cand_repo_mx.is_file():
    matrix_path = cand_repo_mx.resolve()
elif repo == hom_root and cand_eng_mx.is_file():
    matrix_path = cand_eng_mx.resolve()

if matrix_path is not None and hom_root.is_dir():
    run_matrix = False
    if os.environ.get("HOMUNCULUS_FORCE_MATRIX_AUDIT", "0") == "1":
        run_matrix = True
    elif repo == hom_root and any(p.endswith((".py", ".sh", ".ps1")) for p in staged):
        run_matrix = True
    elif "memory/Projects/Homunculus/Homunculus_Script_Skill_Interaction_Matrix.md" in staged:
        run_matrix = True

    if run_matrix:
        text = matrix_path.read_text(encoding="utf-8")
        errors: list[str] = []
        sec1_match = re.search(r"## 1\. Master Script-to-Skill Cross-Reference Summary(.*?)(?:\n---\n|\n## 2\.)", text, re.S)
        master_rows: dict[str, dict[str, str]] = {}
        if not sec1_match:
            errors.append("MISSING_MASTER_TABLE: Section 1 Master Script-to-Skill table not found")
        else:
            for line in sec1_match.group(1).splitlines():
                s_ln = line.strip()
                row_p6 = re.match(
                    r"^\|\s*`([^`]+)`\s*\(\[`Homunculus(?:_Software|_Hardware)?\.md`\]\(Homunculus(?:_Software|_Hardware)?\.md\)\)\s*\|([^|]*)\|([^|]*)\|([^|]*)\|([^|]*)\|",
                    s_ln,
                )
                if row_p6 and ("#L" in row_p6.group(4) or "N/A" in row_p6.group(4)):
                    rel_p = row_p6.group(1).strip()
                    if not (hom_root / rel_p).exists():
                        errors.append(f"DEAD_MATRIX_SCRIPT_PATH: {rel_p} does not exist inside {hom_root}")
                    master_rows[rel_p] = {
                        "role": row_p6.group(2).strip(),
                        "owner": row_p6.group(3).strip().strip("`"),
                        "map_header": row_p6.group(4).strip(),
                        "callers": row_p6.group(5).strip(),
                    }

        for path in sorted(hom_root.rglob("*")):
            if not path.is_file() or "__pycache__" in path.parts or ".git" in path.parts:
                continue
            if path.suffix not in {".py", ".sh", ".ps1"}:
                continue
            rel_p = path.relative_to(hom_root).as_posix()
            if rel_p not in master_rows:
                errors.append(f"UNLISTED_HOMUNCULUS_SCRIPT: '{rel_p}' is missing from Section 1 of {matrix_path.name}")

        module_to_rel: dict[str, tuple[str, str, str]] = {}
        for rel_p, info in master_rows.items():
            p = Path(rel_p)
            if p.suffix == ".py" and not rel_p.startswith("tests/"):
                module_to_rel[p.stem] = (rel_p, p.name, info["owner"])

        for rel_p, info in master_rows.items():
            p = hom_root / rel_p
            if p.suffix != ".py" or rel_p.startswith("tests/") or not p.is_file():
                continue
            try:
                tree = ast.parse(p.read_text(encoding="utf-8"), filename=str(p))
            except SyntaxError as exc:
                errors.append(f"SYNTAX_ERROR: {rel_p}: {exc}")
                continue
            imported_stems: set[str] = set()
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imported_stems.add(alias.name.split(".")[0])
                elif isinstance(node, ast.ImportFrom) and node.module:
                    imported_stems.add(node.module.split(".")[0])
            for stem in sorted(imported_stems):
                if stem not in module_to_rel or module_to_rel[stem][0] == rel_p:
                    continue
                tgt_rel, tgt_base, tgt_owner = module_to_rel[stem]
                src_base = p.name
                src_owner = info["owner"]
                if tgt_base not in info["callers"] and tgt_owner not in info["callers"]:
                    errors.append(
                        f"MISSING_IMPORT_EDGE: '{rel_p}' imports '{tgt_base}', but '{rel_p}' Master Table row does not list '{tgt_base}' or '{tgt_owner}'"
                    )
                tgt_callers = master_rows[tgt_rel]["callers"]
                if src_base not in tgt_callers and src_owner not in tgt_callers:
                    errors.append(
                        f"MISSING_REVERSE_EDGE: '{rel_p}' imports '{tgt_base}', but '{tgt_rel}' Master Table row does not list '{src_base}' or '{src_owner}'"
                    )

        if errors:
            print(f"[BLOCKED] Homunculus Maintainer Script-Skill Matrix is out of sync ({matrix_path}):", file=sys.stderr)
            for e in errors:
                print(f"  - {e}", file=sys.stderr)
            sys.exit(1)
PY
