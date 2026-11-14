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
  unlock [--with-memory] --files <f1> [f2...] --reason "..."
                                             Grant scoped Ring-0 write lease (and optionally unlock memory governance)
  unlock-all --files <f1> [f2...] --reason "..."
                                             Alias for `unlock --with-memory`
  seal   [--with-memory] --reason "..."      Re-lock Ring-0/1 (0444/0555), seal kernel_seal.json (and memory governance first if --with-memory)
  seal-all --reason "..."                    Alias for `seal --with-memory`
  revoke                                     Close active lease & re-lock leased files without updating seal
  enroll-turnkeys [COUNT] [--turnkey-ttl-minutes 45]
                                             Enroll single-use CSPRNG remote turnkeys in 0600 sudo_turnkeys.json
  enroll-signer --signing-key <PUB> [--seal-signing required|optional|off] [--signature-storage local_config|inline] [--signer-principal <NAME>]
                                             Enroll opt-in OpenSSH ssh-keygen -Y seal signer (public key only)
  policy <tty_turnkey|scoped_lease> [--protect-builtin-ring1] [--enforced-roots ...]
                                             Update workstation sudo_policy.json

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
    unlock|unlock-all)
        require_human_tty
        with_mem=0
        if [[ "$cmd" == "unlock-all" ]]; then
            with_mem=1
        fi
        declare -a forward_args=()
        for arg in "$@"; do
            if [[ "$arg" == "--with-memory" ]]; then
                with_mem=1
            else
                forward_args+=("$arg")
            fi
        done
        python3 "$PATHS_PY" --homunculus-root "$HOMUNCULUS_ROOT" --sudo-unlock ${forward_args[@]+"${forward_args[@]}"}
        if [[ "$with_mem" == "1" ]]; then
            python3 "$SYNC_MEM_PY" --memory-root "$MEMORY_ROOT" --unlock-memory-rules
        fi
        ;;
    seal|seal-all)
        require_human_tty
        with_mem=0
        if [[ "$cmd" == "seal-all" ]]; then
            with_mem=1
        fi
        mem_reason=""
        declare -a forward_args=()
        declare -a mem_extra_args=()
        expect_reason=0
        for arg in "$@"; do
            if [[ "$expect_reason" == "1" ]]; then
                mem_reason="$arg"
                forward_args+=("$arg")
                expect_reason=0
                continue
            fi
            case "$arg" in
                --with-memory)
                    with_mem=1
                    ;;
                --reason)
                    expect_reason=1
                    forward_args+=("$arg")
                    ;;
                --reason=*)
                    mem_reason="${arg#--reason=}"
                    forward_args+=("$arg")
                    ;;
                --json)
                    forward_args+=("$arg")
                    mem_extra_args+=("--json")
                    ;;
                *)
                    forward_args+=("$arg")
                    ;;
            esac
        done
        if [[ "$with_mem" == "1" ]]; then
            if [[ -z "${mem_reason// /}" ]]; then
                echo "[FAIL] --reason \"...\" is required when sealing with memory governance." >&2
                exit 2
            fi
            python3 "$SYNC_MEM_PY" --memory-root "$MEMORY_ROOT" --seal-governance --user-confirmed --reason "$mem_reason" ${mem_extra_args[@]+"${mem_extra_args[@]}"}
        fi
        python3 "$PATHS_PY" --homunculus-root "$HOMUNCULUS_ROOT" --sudo-seal ${forward_args[@]+"${forward_args[@]}"}
        ;;
    revoke)
        require_human_tty
        python3 "$PATHS_PY" --homunculus-root "$HOMUNCULUS_ROOT" --sudo-revoke "$@"
        ;;
    enroll-turnkeys|gen-remote-codes)
        require_human_tty
        if [[ $# -gt 0 && "$1" =~ ^[0-9]+$ ]]; then
            cnt="$1"
            shift
            python3 "$PATHS_PY" --homunculus-root "$HOMUNCULUS_ROOT" --enroll-remote-turnkeys "$cnt" "$@"
        else
            python3 "$PATHS_PY" --homunculus-root "$HOMUNCULUS_ROOT" --enroll-remote-turnkeys "$@"
        fi
        ;;
    enroll-signer)
        require_human_tty
        python3 "$PATHS_PY" --homunculus-root "$HOMUNCULUS_ROOT" --memory-root "$MEMORY_ROOT" --enroll-seal-signer "$@"
        ;;
    policy)
        require_human_tty
        pol_val="${1:-}"
        if [[ -z "$pol_val" ]]; then
            echo "[FAIL] Usage: h-sudo policy <tty_turnkey|scoped_lease> [--protect-builtin-ring1] [--enforced-roots ...]" >&2
            exit 2
        fi
        shift
        pol_cfg="${HOME}/.config/homunculus/sudo_policy.json"
        relock_pol=0
        if [[ -f "$pol_cfg" && ! -w "$pol_cfg" ]]; then
            chmod 0600 "$pol_cfg"
            relock_pol=1
        fi
        python3 "$PATHS_PY" --homunculus-root "$HOMUNCULUS_ROOT" --set-sudo-policy "$pol_val" "$@"
        if [[ "$relock_pol" == "1" || -f "$pol_cfg" ]]; then
            chmod 0444 "$pol_cfg"
        fi
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
