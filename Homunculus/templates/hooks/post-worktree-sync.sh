#!/usr/bin/env bash
# Homunculus Non-Blocking Git Working-Tree Directory Sync Hook (post-checkout / post-merge / post-rewrite)
# Governed by: 1. Accuracy & Truth -> 2. Efficiency -> 3. Data Safety -> 4. Speed
# Refreshes <memory_root>/Directory/*.md and AUTO-TREE (write-if-changed, ~1.7ms cached / ~25ms rebuild)
# whenever Git switches branches, merges/pulls, or rebases, without blocking Git operations.
set -uo pipefail

CALLER_DIR="$(cd "$(dirname "$0")" && pwd)"
if [[ "$(basename "$CALLER_DIR")" == "hooks" && "$(basename "$(dirname "$CALLER_DIR")")" == ".git" ]]; then
    REPO_ROOT="$(cd "${CALLER_DIR}/../.." && pwd)"
elif REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null)"; then
    :
else
    exit 0
fi

PYTHON_BIN=""
if command -v python3 >/dev/null 2>&1; then
    PYTHON_BIN="python3"
elif command -v python >/dev/null 2>&1; then
    PYTHON_BIN="python"
else
    exit 0
fi

HOMUNCULUS_ROOT="$("$PYTHON_BIN" - "$REPO_ROOT" << 'PY' 2>/dev/null || true
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
print("")
PY
)"

if [[ -n "$HOMUNCULUS_ROOT" && -f "${HOMUNCULUS_ROOT}/scripts/homunculus_paths.py" ]]; then
    "$PYTHON_BIN" "${HOMUNCULUS_ROOT}/scripts/homunculus_paths.py" \
        --workspace "$REPO_ROOT" --ensure-fresh --quiet >/dev/null 2>&1 || true
fi
exit 0
