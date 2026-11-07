#!/usr/bin/env bash
# Homunculus Universal Git Pre-Commit Boundary & Memory Integrity Gate
# Governed by: 1. Accuracy & Truth -> 2. Efficiency -> 3. Data Safety -> 4. Speed
# Dynamically resolves Homunculus root via .homunculus.json or relative Homunculus/ folder (zero hardcoded paths).
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

# Resolve Homunculus root dynamically via Python stdlib
HOMUNCULUS_ROOT="$("$PYTHON_BIN" - "$REPO_ROOT" << 'PY'
import json, os, sys
from pathlib import Path

repo = Path(sys.argv[1]).resolve()
env_root = os.environ.get("HOMUNCULUS_ROOT", "").strip()
if env_root and Path(env_root).is_dir():
    print(Path(env_root).resolve())
    sys.exit(0)

for d in (repo, *repo.parents):
    cfg = d / ".homunculus.json"
    if cfg.is_file():
        try:
            data = json.loads(cfg.read_text(encoding="utf-8"))
            rel = data.get("homunculus_rel_path", "")
            if rel:
                cand = (d / rel).resolve()
                if (cand / "HOMUNCULUS_START_HERE.md").is_file():
                    print(cand)
                    sys.exit(0)
        except Exception:
            pass
    if (d / "HOMUNCULUS_START_HERE.md").is_file():
        print(d)
        sys.exit(0)
    if (d / "Homunculus" / "HOMUNCULUS_START_HERE.md").is_file():
        print((d / "Homunculus").resolve())
        sys.exit(0)
    if (d / "Engineering" / "Homunculus" / "HOMUNCULUS_START_HERE.md").is_file():
        print((d / "Engineering" / "Homunculus").resolve())
        sys.exit(0)
print("")
PY
)"

if [[ -z "$HOMUNCULUS_ROOT" || ! -f "${HOMUNCULUS_ROOT}/scripts/audit_data_boundary.py" ]]; then
    echo "[BLOCKED] Could not resolve Homunculus root from ${REPO_ROOT}. Set HOMUNCULUS_ROOT or run install.sh." >&2
    exit 1
fi

if [[ -z "${HOMUNCULUS_BOUNDARY_CONFIG:-}" && -f "${HOMUNCULUS_ROOT}/../homunculus_safety.json" ]]; then
    export HOMUNCULUS_BOUNDARY_CONFIG="$(cd "${HOMUNCULUS_ROOT}/.." && pwd)/homunculus_safety.json"
fi

"$PYTHON_BIN" "${HOMUNCULUS_ROOT}/scripts/audit_data_boundary.py" --repo "$REPO_ROOT" --staged

MEMORY_SCRIPT="${HOMUNCULUS_ROOT}/skills/project-memory/scripts/sync_memory.py"
if [[ -f "$MEMORY_SCRIPT" && -d "${REPO_ROOT}/memory" ]]; then
    if git -C "$REPO_ROOT" -c core.quotePath=false diff --cached --name-only | grep -E '^(memory|(Homunculus/)?(rules|skills|addons))/' >/dev/null; then
        if ! mem_out="$("$PYTHON_BIN" "$MEMORY_SCRIPT" --memory-root "${REPO_ROOT}/memory" --audit 2>&1)"; then
            echo "[BLOCKED] Homunculus pre-commit memory gate failed (run: ${PYTHON_BIN} ${MEMORY_SCRIPT} --memory-root ${REPO_ROOT}/memory --audit):" >&2
            echo "$mem_out" >&2
            exit 1
        fi
    fi
fi

# Maintainer Script-Skill Interaction Matrix Parity Gate (active only when Engineering maintainer matrix exists)
MATRIX_FILE="${REPO_ROOT}/memory/Projects/Homunculus/Homunculus_Script_Skill_Interaction_Matrix.md"
if [[ -f "$MATRIX_FILE" && -d "${REPO_ROOT}/Homunculus" ]]; then
    if [[ "${HOMUNCULUS_FORCE_MATRIX_AUDIT:-0}" == "1" ]] || git -C "$REPO_ROOT" -c core.quotePath=false diff --cached --name-only | grep -E '^(Homunculus/|memory/Projects/Homunculus/Homunculus_Script_Skill_Interaction_Matrix\.md$)' >/dev/null; then
        if ! matrix_out="$("$PYTHON_BIN" - "$REPO_ROOT" "$MATRIX_FILE" << 'PY'
import ast, re, sys
from pathlib import Path

repo_root = Path(sys.argv[1]).resolve()
matrix_path = Path(sys.argv[2]).resolve()
hom_root = repo_root / "Homunculus"
text = matrix_path.read_text(encoding="utf-8")
errors = []

# 1. Verify every relative link pointing into Homunculus/ resolves on disk
link_re = re.compile(r"\]\((\.\./\.\./\.\./Homunculus/[^)#\s]+)")
linked_rel_paths = set()
for m in link_re.finditer(text):
    rel_target = m.group(1)
    resolved = (matrix_path.parent / rel_target).resolve()
    if not resolved.exists():
        errors.append(f"DEAD_MATRIX_LINK: {rel_target} does not exist on disk")
    else:
        try:
            linked_rel_paths.add(resolved.relative_to(hom_root).as_posix())
        except ValueError:
            pass

# 2. Parse Master Table rows (Section 1)
sec1_match = re.search(r"## 1\. Master Script-to-Skill Cross-Reference Summary(.*?)(?:\n---\n|\n## 2\.)", text, re.S)
master_rows = {}
if not sec1_match:
    errors.append("MISSING_MASTER_TABLE: Section 1 Master Script-to-Skill table not found")
else:
    for line in sec1_match.group(1).splitlines():
        row_m = re.match(r"^\|\s*\[`([^`]+)`\]\(\.\./\.\./\.\./Homunculus/([^)]+)\)\s*\|([^|]*)\|([^|]*)\|([^|]*)\|", line.strip())
        if row_m:
            rel_p = row_m.group(2).strip()
            master_rows[rel_p] = {
                "role": row_m.group(3).strip(),
                "owner": row_m.group(4).strip().strip("`"),
                "callers": row_m.group(5).strip(),
            }

# 3. Verify 100% script, hook, installer & test coverage in Master Table
for path in sorted(hom_root.rglob("*")):
    if not path.is_file() or "__pycache__" in path.parts or ".git" in path.parts:
        continue
    if path.suffix not in {".py", ".sh", ".ps1"}:
        continue
    rel_p = path.relative_to(hom_root).as_posix()
    if rel_p not in master_rows:
        errors.append(f"UNLISTED_HOMUNCULUS_SCRIPT: '{rel_p}' is missing from Section 1 of {matrix_path.name}")

# 4. Verify AST cross-script Python imports are reflected in Master Table rows
module_to_rel = {}
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
    imported_stems = set()
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
    for e in errors:
        print(f"  - {e}")
    sys.exit(1)
PY
        )"; then
            echo "[BLOCKED] Homunculus Maintainer Script-Skill Matrix is out of sync (${MATRIX_FILE}):" >&2
            echo "$matrix_out" >&2
            exit 1
        fi
    fi
fi
