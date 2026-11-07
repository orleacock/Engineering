#!/usr/bin/env bash
# Homunculus Optional Setup Wrapper for Linux and macOS.
# Note: Homunculus also supports 100% Zero-Install Drop-In mode via HOMUNCULUS_START_HERE.md
# for locked-down workstations where running setup scripts is not permitted.
# === DEVELOPER & AI NAVIGATION MAP ===
#   Owning Module : Core Framework POSIX Installer (`install.sh`)
#   Callers       : End-user / CI setup (`bash ./install.sh`), `test_foundation.py`, `test_adapters.py`
#   Callees       : `scripts/audit_portability.py`, `scripts/homunculus_paths.py`, `scripts/build_adapters.py`
#   CLI Flags     : --workspace, --memory-mode, --client, --no-adapters, --prefer-copy, --install-git-hooks, --dry-run, --check, -h/--help
#   Section Index : Defaults (#L14-L22) | usage() (#L24-L44) | CLI Arg Loop (#L46-L90) | Python Discovery (#L92-L100) | Execution (#L102-L132)
# === END NAVIGATION MAP ===
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_DIR="$(pwd)"
MEMORY_MODE="headless"
CLIENT_TARGET="all"
NO_ADAPTERS=0
PREFER_COPY=0
INSTALL_GIT_HOOKS=0
DRY_RUN=0
CHECK_ONLY=0

usage() {
  cat <<'EOF'
Usage: bash ./install.sh [OPTIONS]

Optional non-root workspace initializer for Homunculus (Linux & macOS).
If script execution is restricted on your workstation, skip this script and point
your AI assistant directly to HOMUNCULUS_START_HERE.md (Zero-Install Drop-In Mode).

Options:
  --workspace <dir>               Target project workspace directory (default: current directory)
  --memory-mode <headless|obsidian> Memory architecture mode (default: headless)
  --client <all|agents_md|antigravity|claude_code|claude_cowork|cursor>
                                  Generate client harness adapters and context-ignore files in workspace
  --no-adapters                   Initialize .homunculus.json without generating client harness adapters
  --prefer-copy                   Copy rule/skill files instead of symlinking when applying client adapters
  --install-git-hooks             Install portable pre-commit & pre-push data-boundary hooks into workspace/.git/hooks
  --dry-run                       Print planned actions without writing files
  --check                         Verify portability and runtime readiness only
  -h, --help                      Show this help message
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --workspace)
      WORKSPACE_DIR="$2"
      shift 2
      ;;
    --memory-mode)
      MEMORY_MODE="$2"
      shift 2
      ;;
    --client)
      CLIENT_TARGET="$2"
      shift 2
      ;;
    --no-adapters)
      NO_ADAPTERS=1
      shift
      ;;
    --prefer-copy)
      PREFER_COPY=1
      shift
      ;;
    --install-git-hooks)
      INSTALL_GIT_HOOKS=1
      shift
      ;;
    --dry-run)
      DRY_RUN=1
      shift
      ;;
    --check)
      CHECK_ONLY=1
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "[FAIL] Unknown argument: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

PYTHON_BIN=""
if command -v python3 >/dev/null 2>&1; then
  PYTHON_BIN="python3"
elif command -v python >/dev/null 2>&1; then
  PYTHON_BIN="python"
else
  echo "[WARN] Python 3.10+ not found on PATH. Use Zero-Install Drop-In Mode via HOMUNCULUS_START_HERE.md." >&2
  exit 2
fi

if [[ "${CHECK_ONLY}" -eq 1 ]]; then
  "${PYTHON_BIN}" "${SCRIPT_DIR}/scripts/audit_portability.py" --repo "${SCRIPT_DIR}"
  "${PYTHON_BIN}" "${SCRIPT_DIR}/scripts/homunculus_paths.py" --homunculus-root "${SCRIPT_DIR}" --workspace "${WORKSPACE_DIR}" --check
  exit 0
fi

if [[ "${DRY_RUN}" -eq 1 ]]; then
  echo "[DRY-RUN] Would initialize Homunculus in workspace: ${WORKSPACE_DIR} (memory_mode=${MEMORY_MODE}, client=${CLIENT_TARGET:-none})"
  "${PYTHON_BIN}" "${SCRIPT_DIR}/scripts/homunculus_paths.py" --homunculus-root "${SCRIPT_DIR}" --workspace "${WORKSPACE_DIR}" --check
  exit 0
fi

mkdir -p "${WORKSPACE_DIR}"
"${PYTHON_BIN}" "${SCRIPT_DIR}/scripts/audit_portability.py" --repo "${SCRIPT_DIR}"
"${PYTHON_BIN}" "${SCRIPT_DIR}/scripts/homunculus_paths.py" \
  --homunculus-root "${SCRIPT_DIR}" \
  --workspace "${WORKSPACE_DIR}" \
  --init-config \
  --memory-mode "${MEMORY_MODE}" \
  --check

if [[ "${NO_ADAPTERS}" -eq 0 && ( -n "${CLIENT_TARGET}" || "${INSTALL_GIT_HOOKS}" -eq 1 ) ]]; then
  ADAPTER_ARGS=(--homunculus-root "${SCRIPT_DIR}" --workspace "${WORKSPACE_DIR}" --client "${CLIENT_TARGET:-all}")
  if [[ "${PREFER_COPY}" -eq 1 ]]; then
    ADAPTER_ARGS+=(--prefer-copy)
  fi
  if [[ "${INSTALL_GIT_HOOKS}" -eq 1 ]]; then
    ADAPTER_ARGS+=(--install-git-hooks)
  fi
  "${PYTHON_BIN}" "${SCRIPT_DIR}/scripts/build_adapters.py" "${ADAPTER_ARGS[@]}"
fi
