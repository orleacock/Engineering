#!/usr/bin/env bash
# Idempotent workstation bootstrap & symlink verifier for /home/orin/Projects/Engineering (Homunculus + Dual-Mode Memory)
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PROJECTS_DIR="$(dirname "$REPO_ROOT")"
ALCHEMICAL_DIR="${PROJECTS_DIR}/Alchemical3D"
HOMUNCULUS_DIR="${ALCHEMICAL_DIR}/Homunculus"
MEMORY_DIR="${REPO_ROOT}/memory"
GEMINI_CFG="${HOME}/.gemini/config"
OBSIDIAN_CFG="${HOME}/.config/obsidian/obsidian.json"

MODE="apply"
UPDATE_OBSIDIAN=0

for arg in "$@"; do
    case "$arg" in
        --check) MODE="check" ;;
        --update-obsidian) UPDATE_OBSIDIAN=1 ;;
        -h|--help)
            echo "Usage: $(basename "$0") [--check] [--update-obsidian]"
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

ensure_managed_hook_link() {
    local link_path="$1"
    local link_target="$2"
    local expected_real="$3"

    if [[ "$MODE" == "check" ]]; then
        if [[ ! -L "$link_path" ]] || [[ ! -x "$link_path" ]] || [[ "$(realpath -m "$link_path")" != "$(realpath -m "$expected_real")" ]]; then
            echo "[FAIL] Managed hook symlink mismatch or non-executable: $link_path (expected -> $expected_real)" >&2
            errors=$((errors + 1))
        else
            echo "[OK]   $link_path -> $(readlink "$link_path")"
        fi
    else
        mkdir -p "$(dirname "$link_path")"
        if [[ -e "$link_path" && ! -L "$link_path" ]]; then
            if head -n 5 "$link_path" 2>/dev/null | grep -qE '^# Homunculus (Universal Git|Non-Blocking Git)'; then
                rm -f "$link_path"
                ln -sfn "$link_target" "$link_path"
                echo "[MIGRATE-LINK] $link_path -> $link_target"
            else
                echo "[SKIP/WARN] Custom non-Homunculus hook exists at $link_path — refusing to overwrite" >&2
                errors=$((errors + 1))
            fi
            return
        fi
        ln -sfn "$link_target" "$link_path"
        echo "[LINK] $link_path -> $link_target"
    fi
}

echo "=== Engineering Workstation Bootstrap (${MODE^^}) ==="
echo "Repo Root: ${REPO_ROOT}"

# 1. Global Antigravity Rules (~/.gemini/config/rules/*.md) -> Alchemical3D/Homunculus/rules/*.md
for rule_file in "${HOMUNCULUS_DIR}/rules/"*.md; do
    [[ -f "$rule_file" ]] || continue
    rule_name="$(basename "$rule_file")"
    ensure_link "${GEMINI_CFG}/rules/${rule_name}" "../../../Projects/Alchemical3D/Homunculus/rules/${rule_name}" "$rule_file"
done

# 2. Global Antigravity Skills (~/.gemini/config/skills/*) -> Alchemical3D/Homunculus/skills/* + addons/*
for skill_dir in "${HOMUNCULUS_DIR}/skills/"* "${HOMUNCULUS_DIR}/addons/"*; do
    [[ -d "$skill_dir" ]] || continue
    [[ -f "${skill_dir}/SKILL.md" ]] || continue
    skill_name="$(basename "$skill_dir")"
    tier_dir="$(basename "$(dirname "$skill_dir")")"
    [[ "$skill_name" == .* ]] && continue
    ensure_link "${GEMINI_CFG}/skills/${skill_name}" "../../../Projects/Alchemical3D/Homunculus/${tier_dir}/${skill_name}" "$skill_dir"
done

# 2a. Local Workstation-Only MCP Skills (/home/orin/Projects/Engineering/scripts/gmail_mcp/gmail-workspace-assistant)
GMAIL_SKILL_DIR="${REPO_ROOT}/scripts/gmail_mcp/gmail-workspace-assistant"
if [[ -f "${GMAIL_SKILL_DIR}/SKILL.md" ]]; then
    ensure_link "${GEMINI_CFG}/skills/gmail-workspace-assistant" "../../../Projects/Engineering/scripts/gmail_mcp/gmail-workspace-assistant" "$GMAIL_SKILL_DIR"
fi

# 2b. Global Antigravity Lifecycle Hooks (~/.gemini/config/hooks.json — non-destructive JSON parity)
if [[ -f "${HOMUNCULUS_DIR}/hooks/hooks.json" ]]; then
    python3 -B - "$MODE" "${HOMUNCULUS_DIR}/hooks/hooks.json" "${GEMINI_CFG}/hooks.json" << 'PY' || errors=$((errors + 1))
import json
import sys
from pathlib import Path

mode = sys.argv[1]
src = Path(sys.argv[2])
dst = Path(sys.argv[3])

try:
    src_obj = json.loads(src.read_text(encoding="utf-8"))
except (OSError, json.JSONDecodeError) as exc:
    print(f"[FAIL] Could not parse managed source hooks JSON {src}: {exc}", file=sys.stderr)
    sys.exit(1)

if not isinstance(src_obj, dict):
    print(f"[FAIL] Managed source hooks JSON must be a JSON object: {src}", file=sys.stderr)
    sys.exit(1)

if mode == "check":
    if not dst.exists() or dst.is_symlink():
        print(f"[FAIL] Missing or symlinked hooks.json (expected regular non-destructive JSON file): {dst}", file=sys.stderr)
        sys.exit(1)
    try:
        dst_obj = json.loads(dst.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"[FAIL] Invalid JSON in {dst}: {exc}", file=sys.stderr)
        sys.exit(1)
    if not isinstance(dst_obj, dict):
        print(f"[FAIL] Non-object JSON in {dst}", file=sys.stderr)
        sys.exit(1)
    for k, v in src_obj.items():
        if k not in dst_obj:
            print(f"[FAIL] Missing managed hooks.json key '{k}' in {dst}", file=sys.stderr)
            sys.exit(1)
        if isinstance(v, list) and isinstance(dst_obj[k], list):
            for item in v:
                if item not in dst_obj[k]:
                    print(f"[FAIL] Missing managed hook entry under '{k}' in {dst}", file=sys.stderr)
                    sys.exit(1)
    print(f"[OK]   {dst} (non-destructive JSON in sync)")
    sys.exit(0)

dst.parent.mkdir(parents=True, exist_ok=True)
if dst.is_symlink():
    dst.unlink()
    print(f"[MIGRATE] Unlinked symlink {dst} -> converting to non-destructive regular JSON file")

if not dst.exists():
    dst.write_text(json.dumps(src_obj, indent=2) + "\n", encoding="utf-8")
    print(f"[SYNC] {dst} <- {src} (created regular JSON)")
    sys.exit(0)

try:
    dst_obj = json.loads(dst.read_text(encoding="utf-8"))
except (OSError, json.JSONDecodeError) as exc:
    print(f"[FAIL] Invalid JSON in {dst} (refusing to overwrite): {exc}", file=sys.stderr)
    sys.exit(1)

if not isinstance(dst_obj, dict):
    print(f"[FAIL] Non-object JSON in {dst} (refusing to overwrite)", file=sys.stderr)
    sys.exit(1)

changed = False
for k, v in src_obj.items():
    if k not in dst_obj:
        dst_obj[k] = v
        changed = True
    elif isinstance(dst_obj[k], list) and isinstance(v, list):
        for item in v:
            if item not in dst_obj[k]:
                dst_obj[k].append(item)
                changed = True

if changed:
    dst.write_text(json.dumps(dst_obj, indent=2) + "\n", encoding="utf-8")
    print(f"[SYNC] {dst} (merged managed Homunculus keys non-destructively)")
else:
    print(f"[OK]   {dst} (non-destructive JSON already in sync)")
PY
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

# 2bc. Public / Org Alchemical-3D Multi-Repo Boundary Hooks (symlinked to Engineering & Homunculus)
if [[ -f "${REPO_ROOT}/scripts/git_pre_commit_boundary.sh" && -f "${REPO_ROOT}/scripts/pre_push_engineering_guard.sh" ]]; then
    shopt -s nullglob dotglob
    for alch_repo in "${ALCHEMICAL_DIR}/"*; do
        repo_base="$(basename "$alch_repo")"
        [[ "$repo_base" == "." || "$repo_base" == ".." ]] && continue
        [[ -d "${alch_repo}/.git/hooks" ]] || continue
        ensure_managed_hook_link "${alch_repo}/.git/hooks/pre-commit" "../../../../Engineering/scripts/git_pre_commit_boundary.sh" "${REPO_ROOT}/scripts/git_pre_commit_boundary.sh"
        ensure_managed_hook_link "${alch_repo}/.git/hooks/pre-push" "../../../../Engineering/scripts/pre_push_engineering_guard.sh" "${REPO_ROOT}/scripts/pre_push_engineering_guard.sh"
        if [[ -f "${HOMUNCULUS_DIR}/templates/hooks/post-worktree-sync.sh" ]]; then
            if [[ "$repo_base" == "Homunculus" ]]; then
                wt_rel_target="../../templates/hooks/post-worktree-sync.sh"
            else
                wt_rel_target="../../../Homunculus/templates/hooks/post-worktree-sync.sh"
            fi
            for wt_hook in post-checkout post-merge post-rewrite; do
                ensure_managed_hook_link "${alch_repo}/.git/hooks/${wt_hook}" "$wt_rel_target" "${HOMUNCULUS_DIR}/templates/hooks/post-worktree-sync.sh"
            done
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

# 2c. Retired Workspace .agents Guard & Reverse Dangling Symlink Check / Cleanup
if [[ -e "${REPO_ROOT}/.agents" || -L "${REPO_ROOT}/.agents" ]]; then
    if [[ "$MODE" == "check" ]]; then
        echo "[FAIL] Retired duplicate .agents directory exists: ${REPO_ROOT}/.agents" >&2
        errors=$((errors + 1))
    else
        rm -rf "${REPO_ROOT}/.agents"
        echo "[PRUNE] Removed retired duplicate directory: ${REPO_ROOT}/.agents"
    fi
fi

for scan_dir in "${GEMINI_CFG}/rules" "${GEMINI_CFG}/skills" "${HOME}/.agents/rules" "${HOME}/.agents/skills"; do
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

# 3. Optional Obsidian Vault Registry Path Check
if [[ "$UPDATE_OBSIDIAN" -eq 1 && -f "$OBSIDIAN_CFG" ]]; then
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
fi

if [[ "$errors" -gt 0 ]]; then
    echo "Bootstrap finished with ${errors} error(s)." >&2
    exit 1
fi
echo "Bootstrap ${MODE} completed cleanly (0 errors)."
