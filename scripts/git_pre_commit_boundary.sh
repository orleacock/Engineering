#!/usr/bin/env bash
# Homunculus Universal Git Pre-Commit Boundary & Memory Integrity Gate
# Governed by: 1. Accuracy & Truth -> 2. Efficiency -> 3. Data Safety -> 4. Speed
# Dynamically resolves Homunculus root via .homunculus.json or relative Homunculus/ folder (zero hardcoded paths).
# === DEVELOPER & AI NAVIGATION MAP ===
#   Owning Module : Parent Workstation Pre-Commit Boundary, Memory & Matrix Parity Gate (`scripts/git_pre_commit_boundary.sh`)
#   Callees       : `audit_data_boundary.py --staged`, `sync_memory.py`, AST Matrix Parity Gate against `Homunculus_Script_Skill_Interaction_Matrix.md`
#   Section Index : Repo Root (#L12-L20) | Python Discovery (#L21-L30) | Homunculus Root Probe (#L32-L66) | Boundary & Memory Gate (#L73-L114) | AST Matrix Parity (#L117-L225)
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
    if (d / "Alchemical3D" / "Homunculus" / "HOMUNCULUS_START_HERE.md").is_file():
        print((d / "Alchemical3D" / "Homunculus").resolve())
        sys.exit(0)
print("")
PY
)"

if [[ -z "$HOMUNCULUS_ROOT" || ! -f "${HOMUNCULUS_ROOT}/scripts/audit_data_boundary.py" ]]; then
    echo "[BLOCKED] Could not resolve Homunculus root from ${REPO_ROOT}. Set HOMUNCULUS_ROOT or run install.sh." >&2
    exit 1
fi

if [[ -z "${HOMUNCULUS_BOUNDARY_CONFIG:-}" ]]; then
    if [[ -f "${REPO_ROOT}/homunculus_safety.json" ]]; then
        export HOMUNCULUS_BOUNDARY_CONFIG="${REPO_ROOT}/homunculus_safety.json"
    elif [[ -f "${HOMUNCULUS_ROOT}/../homunculus_safety.json" ]]; then
        export HOMUNCULUS_BOUNDARY_CONFIG="$(cd "${HOMUNCULUS_ROOT}/.." && pwd)/homunculus_safety.json"
    elif [[ -f "${HOMUNCULUS_ROOT}/../../Engineering/homunculus_safety.json" ]]; then
        export HOMUNCULUS_BOUNDARY_CONFIG="$(cd "${HOMUNCULUS_ROOT}/../../Engineering" && pwd)/homunculus_safety.json"
    fi
fi

"$PYTHON_BIN" "${HOMUNCULUS_ROOT}/scripts/audit_data_boundary.py" --repo "$REPO_ROOT" --staged

MEMORY_SCRIPT="${HOMUNCULUS_ROOT}/skills/project-memory/scripts/sync_memory.py"
MEMORY_DIR="$("$PYTHON_BIN" - "$REPO_ROOT" << 'PY'
import json, sys
from pathlib import Path
repo = Path(sys.argv[1]).resolve()
cfg = repo / ".homunculus.json"
if cfg.is_file():
    try:
        rel = json.loads(cfg.read_text(encoding="utf-8")).get("memory_dir", "")
        if rel:
            cand = (repo / rel).resolve()
            if cand.is_dir() and repo in (cand, *cand.parents):
                print(cand)
                sys.exit(0)
    except Exception:
        pass
fallback = repo / "memory"
print(fallback if fallback.is_dir() else "")
PY
)"
if [[ -f "$MEMORY_SCRIPT" && -n "$MEMORY_DIR" && -d "$MEMORY_DIR" ]]; then
    MEMORY_REL="${MEMORY_DIR#"${REPO_ROOT}/"}"
    if git -C "$REPO_ROOT" -c core.quotePath=false diff --cached --name-only | grep -E "^${MEMORY_REL}/" >/dev/null; then
        if ! mem_out="$("$PYTHON_BIN" "$MEMORY_SCRIPT" --memory-root "$MEMORY_DIR" --audit 2>&1)"; then
            echo "[BLOCKED] Homunculus pre-commit memory gate failed (run: ${PYTHON_BIN} ${MEMORY_SCRIPT} --memory-root ${MEMORY_DIR} --audit):" >&2
            echo "$mem_out" >&2
            exit 1
        fi
    fi
fi

# Maintainer Script-Skill Interaction Matrix Parity Gate (active when Engineering maintainer matrix exists)
MATRIX_FILE=""
if [[ -f "${REPO_ROOT}/memory/Projects/Homunculus/Homunculus_Script_Skill_Interaction_Matrix.md" ]]; then
    MATRIX_FILE="${REPO_ROOT}/memory/Projects/Homunculus/Homunculus_Script_Skill_Interaction_Matrix.md"
elif [[ "$REPO_ROOT" == "$HOMUNCULUS_ROOT" && -f "${HOMUNCULUS_ROOT}/../../Engineering/memory/Projects/Homunculus/Homunculus_Script_Skill_Interaction_Matrix.md" ]]; then
    MATRIX_FILE="$(cd "${HOMUNCULUS_ROOT}/../../Engineering" && pwd)/memory/Projects/Homunculus/Homunculus_Script_Skill_Interaction_Matrix.md"
fi
if [[ -n "$MATRIX_FILE" && -f "$MATRIX_FILE" && -d "${HOMUNCULUS_ROOT}" ]]; then
    RUN_MATRIX_AUDIT=0
    if [[ "${HOMUNCULUS_FORCE_MATRIX_AUDIT:-0}" == "1" ]]; then
        RUN_MATRIX_AUDIT=1
    elif [[ "$REPO_ROOT" == "$HOMUNCULUS_ROOT" ]] && git -C "$REPO_ROOT" -c core.quotePath=false diff --cached --name-only | grep -E '\.(py|sh|ps1)$' >/dev/null; then
        RUN_MATRIX_AUDIT=1
    elif git -C "$REPO_ROOT" -c core.quotePath=false diff --cached --name-only | grep -E '^memory/Projects/Homunculus/Homunculus_Script_Skill_Interaction_Matrix\.md$' >/dev/null; then
        RUN_MATRIX_AUDIT=1
    fi
    if [[ "$RUN_MATRIX_AUDIT" == "1" ]]; then
        if ! matrix_out="$("$PYTHON_BIN" - "$MATRIX_FILE" "$HOMUNCULUS_ROOT" << 'PY'
import ast, re, sys
from pathlib import Path

matrix_path = Path(sys.argv[1]).resolve()
hom_root = Path(sys.argv[2]).resolve()
text = matrix_path.read_text(encoding="utf-8")
errors = []

# 1. Parse Master Table rows (Section 1 portable dual-bound anchors)
sec1_match = re.search(r"## 1\. Master Script-to-Skill Cross-Reference Summary(.*?)(?:\n---\n|\n## 2\.)", text, re.S)
master_rows = {}
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

# 2. Verify 100% script, hook, installer & test coverage in Master Table
for path in sorted(hom_root.rglob("*")):
    if not path.is_file() or "__pycache__" in path.parts or ".git" in path.parts:
        continue
    if path.suffix not in {".py", ".sh", ".ps1"}:
        continue
    rel_p = path.relative_to(hom_root).as_posix()
    if rel_p not in master_rows:
        errors.append(f"UNLISTED_HOMUNCULUS_SCRIPT: '{rel_p}' is missing from Section 1 of {matrix_path.name}")

# 3. Verify AST cross-script Python imports are reflected in Master Table rows
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
