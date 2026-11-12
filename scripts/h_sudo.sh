#!/usr/bin/env bash
# Homunculus Workstation Ring-0 Human Turnkey Helper (`h_sudo.sh` / `h-sudo`)
# Governed by: 1. Accuracy & Truth -> 2. Efficiency -> 3. Data Safety -> 4. Speed
#
# Out-of-tree human terminal turnkey for `/home/orin/Projects/Alchemical3D/Homunculus`
# and `/home/orin/Projects/Engineering/memory`. Rejects non-interactive AI pipes.
set -euo pipefail

REAL_SELF="$(python3 -c 'import os,sys; print(os.path.realpath(sys.argv[1]))' "${BASH_SOURCE[0]}")"
SCRIPT_DIR="$(cd "$(dirname "${REAL_SELF}")" && pwd)"
ENG_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
HOMUNCULUS_ROOT="${HOMUNCULUS_ROOT:-$(cd "${ENG_ROOT}/../Alchemical3D/Homunculus" && pwd)}"
MEMORY_ROOT="${HOMUNCULUS_MEMORY_ROOT:-${ENG_ROOT}/memory}"
PATHS_PY="${HOMUNCULUS_ROOT}/scripts/homunculus_paths.py"
SYNC_MEM_PY="${HOMUNCULUS_ROOT}/skills/project-memory/scripts/sync_memory.py"

require_human_tty() {
    if [[ ! -t 0 || ! -t 1 ]]; then
        echo "[HUMAN_TERMINAL_REQUIRED] h-sudo must be executed directly from an interactive human terminal (not an AI subshell pipe)." >&2
        exit 2
    fi
}

usage() {
    cat <<'EOF'
Usage: h-sudo <subcommand> [options]

Ring-0 Kernel Commands (requires interactive human terminal under tty_turnkey):
  status                                     Check Ring-0 kernel_seal.json & active lease status
  unlock --files <f1> [f2...] --reason "..." Grant scoped Ring-0 write lease for explicit files
  seal   --reason "..."                      Re-lock Ring-0/1 (0444/0555), seal kernel_seal.json, close lease
  revoke                                     Close active lease & re-lock leased files without updating seal

Memory Governance Commands (Standards_and_Specs/, AGENTS.md, Decision_Profile.md, Archives):
  unlock-memory                              Unlock memory governance surfaces (0644) for approved edit
  seal-memory --reason "..."                 Re-seal Directory/governance_seal.json & re-lock surfaces (0444)
EOF
}

cmd="${1:-status}"
shift || true

case "$cmd" in
    status)
        python3 "$PATHS_PY" --homunculus-root "$HOMUNCULUS_ROOT" --verify-seal
        ;;
    unlock)
        require_human_tty
        python3 "$PATHS_PY" --homunculus-root "$HOMUNCULUS_ROOT" --sudo-unlock "$@"
        ;;
    seal)
        require_human_tty
        python3 "$PATHS_PY" --homunculus-root "$HOMUNCULUS_ROOT" --sudo-seal "$@"
        ;;
    revoke)
        require_human_tty
        python3 "$PATHS_PY" --homunculus-root "$HOMUNCULUS_ROOT" --sudo-revoke "$@"
        ;;
    unlock-memory)
        require_human_tty
        python3 "$SYNC_MEM_PY" --memory-root "$MEMORY_ROOT" --unlock-memory-rules
        ;;
    seal-memory)
        require_human_tty
        python3 "$SYNC_MEM_PY" --memory-root "$MEMORY_ROOT" --seal-governance --user-confirmed "$@"
        ;;
    -h|--help|help)
        usage
        ;;
    *)
        echo "[FAIL] Unknown h-sudo subcommand: ${cmd}" >&2
        usage >&2
        exit 2
        ;;
esac
