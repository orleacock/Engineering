#!/usr/bin/env bash
# Homunculus Universal Git Pre-Commit Boundary & Memory Integrity Gate
# Governed by: 1. Accuracy & Truth -> 2. Efficiency -> 3. Data Safety -> 4. Speed
# Dynamically resolves Homunculus root via .homunculus.json or relative Homunculus/ folder (zero hardcoded paths).
# === DEVELOPER & AI NAVIGATION MAP ===
#   Owning Module : Git Pre-Commit Boundary & Memory Gate (`templates/hooks/pre-commit.sh`)
#   Installed By  : `scripts/build_adapters.py --install-git-hooks` -> `.git/hooks/pre-commit`
#   Callees       : `scripts/audit_data_boundary.py --staged`, `skills/project-memory/scripts/sync_memory.py --audit`
#   Section Index : Repo Root Resolution (#L13-L20) | Python Discovery (#L22-L30) | Homunculus & Memory Root Probe (#L33-L69) | Gate Execution (#L71-L87)
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

# Resolve Homunculus root and memory_dir dynamically via Python stdlib
RESOLVED_PATHS="$("$PYTHON_BIN" - "$REPO_ROOT" << 'PY'
import json, os, sys
from pathlib import Path

repo = Path(sys.argv[1]).resolve()
env_root = os.environ.get("HOMUNCULUS_ROOT", "").strip()
hom_root = ""
mem_dir = os.environ.get("HOMUNCULUS_MEMORY_ROOT", "").strip()

for d in (repo, *repo.parents):
    cfg = d / ".homunculus.json"
    if cfg.is_file():
        try:
            data = json.loads(cfg.read_text(encoding="utf-8"))
            if not mem_dir and data.get("memory_dir"):
                mem_dir = str((d / str(data["memory_dir"])).resolve())
            rel = data.get("homunculus_rel_path", "")
            if rel and not hom_root:
                cand = (d / rel).resolve()
                if (cand / "HOMUNCULUS_START_HERE.md").is_file():
                    hom_root = str(cand)
        except Exception:
            pass
    if not hom_root and (d / "HOMUNCULUS_START_HERE.md").is_file():
        hom_root = str(d)
    if not hom_root and (d / "Homunculus" / "HOMUNCULUS_START_HERE.md").is_file():
        hom_root = str((d / "Homunculus").resolve())

if env_root and Path(env_root).is_dir():
    hom_root = str(Path(env_root).resolve())
if not mem_dir:
    mem_dir = str((repo / "memory").resolve())
print(f"{hom_root}|{mem_dir}")
PY
)"
HOMUNCULUS_ROOT="${RESOLVED_PATHS%%|*}"
MEMORY_ROOT="${RESOLVED_PATHS#*|}"

if [[ -z "$HOMUNCULUS_ROOT" || ! -f "${HOMUNCULUS_ROOT}/scripts/audit_data_boundary.py" ]]; then
    echo "[BLOCKED] Could not resolve Homunculus root from ${REPO_ROOT}. Set HOMUNCULUS_ROOT or run install.sh." >&2
    exit 1
fi

"$PYTHON_BIN" "${HOMUNCULUS_ROOT}/scripts/audit_data_boundary.py" --repo "$REPO_ROOT" --staged

MEMORY_SCRIPT="${HOMUNCULUS_ROOT}/skills/project-memory/scripts/sync_memory.py"
if [[ -f "$MEMORY_SCRIPT" && -d "$MEMORY_ROOT" ]]; then
    if git -C "$REPO_ROOT" -c core.quotePath=false diff --cached --name-only | grep -E '^(memory|rules|skills|addons)/' >/dev/null; then
        if ! mem_out="$("$PYTHON_BIN" "$MEMORY_SCRIPT" --memory-root "$MEMORY_ROOT" --audit 2>&1)"; then
            echo "[BLOCKED] Homunculus pre-commit memory gate failed (run: ${PYTHON_BIN} ${MEMORY_SCRIPT} --memory-root ${MEMORY_ROOT} --audit):" >&2
            echo "$mem_out" >&2
            exit 1
        fi
    fi
fi
