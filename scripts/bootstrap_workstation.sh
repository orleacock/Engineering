#!/usr/bin/env bash
# Idempotent workstation bootstrap & symlink verifier for /home/orin/Projects/Engineering (Homunculus + Dual-Mode Memory)
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PROJECTS_DIR="$(dirname "$REPO_ROOT")"
ALCHEMICAL_DIR="${PROJECTS_DIR}/Alchemical3D"
HOMUNCULUS_DIR="${ALCHEMICAL_DIR}/Homunculus"
MEMORY_DIR="${REPO_ROOT}/memory"
NEA_DIR="${ALCHEMICAL_DIR}/NEA_v2.2.3"
GEMINI_CFG="${HOME}/.gemini/config"
OBSIDIAN_CFG="${HOME}/.config/obsidian/obsidian.json"

MODE="apply"
UPDATE_OBSIDIAN=0
COMPAT_SYMLINKS=0

for arg in "$@"; do
    case "$arg" in
        --check) MODE="check" ;;
        --update-obsidian) UPDATE_OBSIDIAN=1 ;;
        --compat-symlinks) COMPAT_SYMLINKS=1 ;;
        -h|--help)
            echo "Usage: $(basename "$0") [--check] [--update-obsidian] [--compat-symlinks]"
            exit 0
            ;;
        *)
            echo "Unknown option: $arg" >&2
            exit 2
            ;;
    esac
done

errors=0

ensure_link() {
    local link_path="$1"
    local link_target="$2"
    local expected_real="$3"

    if [[ "$MODE" == "check" ]]; then
        if [[ ! -L "$link_path" ]] || [[ "$(realpath -m "$link_path")" != "$(realpath -m "$expected_real")" ]]; then
            echo "[FAIL] Symlink mismatch: $link_path (expected -> $expected_real)" >&2
            errors=$((errors + 1))
        else
            echo "[OK]   $link_path -> $(readlink "$link_path")"
        fi
    else
        mkdir -p "$(dirname "$link_path")"
        if [[ -e "$link_path" && ! -L "$link_path" ]]; then
            echo "[SKIP/WARN] Non-symlink already exists at $link_path — refusing to overwrite" >&2
            errors=$((errors + 1))
            return
        fi
        ln -sfn "$link_target" "$link_path"
        echo "[LINK] $link_path -> $link_target"
    fi
}

echo "=== Engineering Workstation Bootstrap (${MODE^^}) ==="
echo "Repo Root: ${REPO_ROOT}"

# 1. Global Antigravity Rules (~/.gemini/config/rules/*.md) & Portable Workspace .agents/rules/*.md -> Alchemical3D/Homunculus/rules/*.md
for rule_file in "${HOMUNCULUS_DIR}/rules/"*.md; do
    [[ -f "$rule_file" ]] || continue
    rule_name="$(basename "$rule_file")"
    ensure_link "${GEMINI_CFG}/rules/${rule_name}" "../../../Projects/Alchemical3D/Homunculus/rules/${rule_name}" "$rule_file"
    ensure_link "${REPO_ROOT}/.agents/rules/${rule_name}" "../../../Alchemical3D/Homunculus/rules/${rule_name}" "$rule_file"
done

# 2. Global Antigravity Skills (~/.gemini/config/skills/*) & Portable Workspace .agents/skills/* -> Alchemical3D/Homunculus/skills/* + addons/*
for skill_dir in "${HOMUNCULUS_DIR}/skills/"* "${HOMUNCULUS_DIR}/addons/"*; do
    [[ -d "$skill_dir" ]] || continue
    [[ -f "${skill_dir}/SKILL.md" ]] || continue
    skill_name="$(basename "$skill_dir")"
    tier_dir="$(basename "$(dirname "$skill_dir")")"
    [[ "$skill_name" == .* ]] && continue
    ensure_link "${GEMINI_CFG}/skills/${skill_name}" "../../../Projects/Alchemical3D/Homunculus/${tier_dir}/${skill_name}" "$skill_dir"
    ensure_link "${REPO_ROOT}/.agents/skills/${skill_name}" "../../../Alchemical3D/Homunculus/${tier_dir}/${skill_name}" "$skill_dir"
done

# 2a. Local Workstation-Only MCP Skills (/home/orin/Projects/Engineering/scripts/gmail_mcp/gmail-workspace-assistant)
GMAIL_SKILL_DIR="${REPO_ROOT}/scripts/gmail_mcp/gmail-workspace-assistant"
if [[ -f "${GMAIL_SKILL_DIR}/SKILL.md" ]]; then
    ensure_link "${GEMINI_CFG}/skills/gmail-workspace-assistant" "../../../Projects/Engineering/scripts/gmail_mcp/gmail-workspace-assistant" "$GMAIL_SKILL_DIR"
    ensure_link "${REPO_ROOT}/.agents/skills/gmail-workspace-assistant" "../../scripts/gmail_mcp/gmail-workspace-assistant" "$GMAIL_SKILL_DIR"
fi

# 2b. Global Antigravity Lifecycle Hooks (~/.gemini/config/hooks.json)
if [[ -f "${HOMUNCULUS_DIR}/hooks/hooks.json" ]]; then
    ensure_link "${GEMINI_CFG}/hooks.json" "../../Projects/Alchemical3D/Homunculus/hooks/hooks.json" "${HOMUNCULUS_DIR}/hooks/hooks.json"
fi

# 2bb. Private Engineering Repo Pre-Commit, Pre-Push & Post-Worktree Sync Hooks (.git/hooks/*)
if [[ -d "${REPO_ROOT}/.git/hooks" ]]; then
    if [[ -f "${REPO_ROOT}/scripts/git_pre_commit_boundary.sh" ]]; then
        ensure_link "${REPO_ROOT}/.git/hooks/pre-commit" "../../scripts/git_pre_commit_boundary.sh" "${REPO_ROOT}/scripts/git_pre_commit_boundary.sh"
    fi
    if [[ -f "${REPO_ROOT}/scripts/pre_push_engineering_guard.sh" ]]; then
        ensure_link "${REPO_ROOT}/.git/hooks/pre-push" "../../scripts/pre_push_engineering_guard.sh" "${REPO_ROOT}/scripts/pre_push_engineering_guard.sh"
    fi
    if [[ -f "${HOMUNCULUS_DIR}/templates/hooks/post-worktree-sync.sh" ]]; then
        for wt_hook in post-checkout post-merge post-rewrite; do
            ensure_link "${REPO_ROOT}/.git/hooks/${wt_hook}" "../../../Alchemical3D/Homunculus/templates/hooks/post-worktree-sync.sh" "${HOMUNCULUS_DIR}/templates/hooks/post-worktree-sync.sh"
        done
    fi
fi

# 2bc. Public / Org Alchemical-3D Multi-Repo Boundary Hooks (including Alchemical3D/Homunculus)
if [[ -f "${REPO_ROOT}/scripts/git_pre_commit_boundary.sh" && -f "${REPO_ROOT}/scripts/pre_push_engineering_guard.sh" ]]; then
    shopt -s nullglob dotglob
    for alch_repo in "${ALCHEMICAL_DIR}/"*; do
        repo_base="$(basename "$alch_repo")"
        [[ "$repo_base" == "." || "$repo_base" == ".." ]] && continue
        [[ -d "${alch_repo}/.git/hooks" ]] || continue
        if [[ "$MODE" == "check" ]]; then
            for hname in pre-commit pre-push; do
                if [[ ! -x "${alch_repo}/.git/hooks/${hname}" ]]; then
                    echo "[FAIL] Missing executable hook: ${alch_repo}/.git/hooks/${hname}" >&2
                    errors=$((errors + 1))
                else
                    echo "[OK]   ${alch_repo}/.git/hooks/${hname} (executable)"
                fi
            done
        else
            cp -f "${REPO_ROOT}/scripts/git_pre_commit_boundary.sh" "${alch_repo}/.git/hooks/pre-commit"
            cp -f "${REPO_ROOT}/scripts/pre_push_engineering_guard.sh" "${alch_repo}/.git/hooks/pre-push"
            chmod +x "${alch_repo}/.git/hooks/pre-commit" "${alch_repo}/.git/hooks/pre-push"
            echo "[HOOK] Installed pre-commit & pre-push -> ${alch_repo}/.git/hooks/"
        fi
    done
    shopt -u nullglob dotglob
fi

# 2bd. Parent Projects & Home Umbrella Configs (${PROJECTS_DIR}/.homunculus.json, ${HOME}/.homunculus.json & ${PROJECTS_DIR}/.geminiignore)
UMBRELLA_HOMUNCULUS_SRC="${REPO_ROOT}/scripts/umbrella_configs/Projects.homunculus.json"
HOME_HOMUNCULUS_SRC="${REPO_ROOT}/scripts/umbrella_configs/Home.homunculus.json"
HOME_HOMUNCULUS_DST="${HOMUNCULUS_HOME_CFG_DST:-${HOME}/.homunculus.json}"
UMBRELLA_GEMINIIGNORE_SRC="${REPO_ROOT}/.geminiignore"
if [[ -d "$PROJECTS_DIR" && -f "$UMBRELLA_HOMUNCULUS_SRC" && -f "$HOME_HOMUNCULUS_SRC" && -f "$UMBRELLA_GEMINIIGNORE_SRC" ]]; then
    for pair in "${UMBRELLA_HOMUNCULUS_SRC}:${PROJECTS_DIR}/.homunculus.json" "${HOME_HOMUNCULUS_SRC}:${HOME_HOMUNCULUS_DST}" "${UMBRELLA_GEMINIIGNORE_SRC}:${PROJECTS_DIR}/.geminiignore"; do
        src_cfg="${pair%%:*}"
        dst_cfg="${pair##*:}"
        if [[ "$MODE" == "check" ]]; then
            if [[ ! -f "$dst_cfg" ]] || ! cmp -s "$src_cfg" "$dst_cfg"; then
                echo "[FAIL] Umbrella config missing or out of sync: $dst_cfg (expected parity with $src_cfg)" >&2
                errors=$((errors + 1))
            else
                echo "[OK]   $dst_cfg (in sync)"
            fi
        else
            cp -f "$src_cfg" "$dst_cfg"
            echo "[SYNC] $dst_cfg <- $src_cfg"
        fi
    done
fi

# 2c. Reverse Dangling Symlink Check / Cleanup
for scan_dir in "${GEMINI_CFG}/rules" "${GEMINI_CFG}/skills" "${REPO_ROOT}/.agents/rules" "${REPO_ROOT}/.agents/skills"; do
    [[ -d "$scan_dir" ]] || continue
    shopt -s nullglob dotglob
    for entry in "${scan_dir}/"*; do
        if [[ -L "$entry" && ! -e "$entry" ]]; then
            dead_target="$(readlink "$entry" || true)"
            if [[ "$MODE" == "check" ]]; then
                echo "[FAIL] Dangling symlink: $entry -> $dead_target"
                errors=$((errors + 1))
            else
                rm -f "$entry"
                echo "[PRUNE] Removed dangling symlink: $entry -> $dead_target"
            fi
        fi
    done
    shopt -u nullglob dotglob
done

# 3. Optional Compatibility Symlinks
if [[ "$COMPAT_SYMLINKS" -eq 1 ]]; then
    if [[ -d "$NEA_DIR" ]]; then
        ensure_link "${HOME}/Downloads/NEA_v2.2.3" "${NEA_DIR}" "${NEA_DIR}"
    fi
fi

# 4. Optional Obsidian Vault Registry Path Sync
if [[ "$UPDATE_OBSIDIAN" -eq 1 && -f "$OBSIDIAN_CFG" ]]; then
    if [[ "$MODE" == "check" ]]; then
        python3 - "$OBSIDIAN_CFG" "$MEMORY_DIR" << 'PY' || errors=$((errors + 1))
import json, sys
cfg_path, vault_dir = sys.argv[1], sys.argv[2]
data = json.loads(open(cfg_path, encoding="utf-8").read())
paths = [v.get("path") for v in data.get("vaults", {}).values()]
if vault_dir in paths:
    print(f"[OK]   Obsidian vault registered at {vault_dir}")
else:
    print(f"[FAIL] Obsidian vault path {vault_dir} not found in {cfg_path}: {paths}", file=sys.stderr)
    sys.exit(1)
PY
    else
        python3 - "$OBSIDIAN_CFG" "$MEMORY_DIR" << 'PY'
import json, os, sys
cfg_path, vault_dir = sys.argv[1], sys.argv[2]
with open(cfg_path, encoding="utf-8") as f:
    data = json.load(f)
vaults = data.get("vaults", {})
stale_keys = [k for k, v in vaults.items() if str(v.get("path", "")).endswith("/Obsidian_Notes")]
for k in stale_keys:
    del vaults[k]
if stale_keys:
    tmp = cfg_path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, separators=(",", ":"))
    os.replace(tmp, cfg_path)
    print(f"[SYNC] Pruned stale Obsidian_Notes entry; active vault is {vault_dir}")
else:
    print(f"[OK]   Obsidian vault path already aligned ({vault_dir})")
PY
    fi
fi

if [[ "$errors" -gt 0 ]]; then
    echo "Bootstrap finished with ${errors} error(s)." >&2
    exit 1
fi
echo "Bootstrap ${MODE} completed cleanly (0 errors)."
