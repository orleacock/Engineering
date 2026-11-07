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
