#!/usr/bin/env python3
"""
Homunculus Harness-Agnostic Client Adapter & Context-Ignore Builder (build_adapters.py).

Governed by: 1. Accuracy & Truth -> 2. Efficiency -> 3. Data Safety -> 4. Speed
Requires ONLY Python 3.10+ standard library (zero third-party pip packages).

Builds and installs portable client bindings across the 5 primary v1.0 harnesses:
  1. agents_md     — Universal AGENTS.md (OpenAI Codex, Windsurf, Aider, Zed, generic harnesses)
  2. antigravity   — Antigravity / Gemini CLI (.gemini/config/{rules,skills,hooks.json} + .agents/skills)
  3. claude_code   — Claude Code (CLAUDE.md + .claude/settings.json + Task subagent dispatch mapping)
  4. claude_cowork — Claude Cowork (designated folder README + self-contained uploadable skill .zip bundles)
  5. cursor        — Cursor IDE (.cursor/rules/homunculus-*.mdc with alwaysApply: true YAML frontmatter)

Also provisions:
  - Context-window egress ignore files (.cursorignore, .claudeignore, .geminiignore)
  - Optional Git pre-commit and pre-push boundary hooks (--install-git-hooks)
  - Windows-safe symlink-with-copy fallback (zero Developer Mode / admin privileges required)
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import shutil
import stat
import sys
import zipfile
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

import homunculus_paths  # noqa: E402

SUPPORTED_CLIENTS = ("agents_md", "antigravity", "claude_code", "claude_cowork", "cursor")
RULE_ORDER = (
    "co-engineering-partner.md",
    "verifiable-accuracy.md",
    "data-and-credential-safety.md",
)


def _strip_yaml_frontmatter(text: str) -> str:
    """Strip leading YAML frontmatter (`--- ... ---`) for harnesses expecting plain Markdown bodies."""
    lines = text.splitlines()
    if lines and lines[0].strip() == "---":
        for idx in range(1, len(lines)):
            if lines[idx].strip() == "---":
                return "\n".join(lines[idx + 1 :]).strip()
    return text.strip()


def _load_ordered_rules(fw_root: Path) -> list[tuple[str, Path, str]]:
    """Return list of (rule_stem, rule_path, frontmatter_stripped_rule_text) in canonical priority order."""
    rules_dir = fw_root / "rules"
    ordered: list[tuple[str, Path, str]] = []
    seen: set[str] = set()
    for fname in RULE_ORDER:
        p = rules_dir / fname
        if p.is_file():
            ordered.append((p.stem, p, _strip_yaml_frontmatter(p.read_text(encoding="utf-8"))))
            seen.add(p.name)
    for p in sorted(rules_dir.glob("*.md")):
        if p.name not in seen:
            ordered.append((p.stem, p, _strip_yaml_frontmatter(p.read_text(encoding="utf-8"))))
    return ordered


def _discover_skills_and_addons(fw_root: Path) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    """Return (active_skills, dormant_addons) metadata dicts."""
    def _scan_dir(base: Path) -> list[dict[str, str]]:
        items: list[dict[str, str]] = []
        if not base.is_dir():
            return items
        for skill_md in sorted(base.glob("*/SKILL.md")):
            s_dir = skill_md.parent
            txt = skill_md.read_text(encoding="utf-8")
            name = s_dir.name
            desc = ""
            lines = txt.splitlines()
            if lines and lines[0].strip() == "---":
                in_desc = False
                for ln in lines[1:]:
                    if ln.strip() == "---":
                        break
                    if ln.startswith("name:"):
                        name = ln.split(":", 1)[1].strip().strip("\"'")
                    elif ln.startswith("description:"):
                        val = ln.split(":", 1)[1].strip()
                        if val not in (">-", ">", "|", "|-"):
                            desc = val.strip("\"'")
                        in_desc = True
                    elif in_desc and (ln.startswith("  ") or ln.startswith("\t")):
                        desc = (desc + " " + ln.strip()).strip()
                    elif in_desc:
                        in_desc = False
            items.append({
                "name": name,
                "folder": s_dir.name,
                "rel_path": skill_md.relative_to(fw_root).as_posix(),
                "description": desc or f"Homunculus {name} runbook.",
            })
        return items

    return _scan_dir(fw_root / "skills"), _scan_dir(fw_root / "addons")


def _render_skill_index_markdown(
    active_skills: list[dict[str, str]],
    dormant_addons: list[dict[str, str]],
    rel_prefix: str = "<HOMUNCULUS_ROOT>",
) -> str:
    lines: list[str] = [
        "## Modular On-Demand Skills & Side-Loaded Add-Ons",
        "",
        "Read the relevant `SKILL.md` runbook before executing specialized workflows (never guess CLI flags):",
        "",
        "### Active Core Skills (`skills/`)",
    ]
    if active_skills:
        for s in active_skills:
            lines.append(f"- **`{s['name']}`** (`{rel_prefix}/{s['rel_path']}`): {s['description']}")
    else:
        lines.append("- *(Core skills populate in `skills/*/SKILL.md`)*")

    lines.extend([
        "",
        "### Dormant Drop-In Add-Ons (`addons/` — Activate by Copying Folder into `skills/`)",
    ])
    if dormant_addons:
        for a in dormant_addons:
            lines.append(f"- **`{a['name']}`** (`{rel_prefix}/{a['rel_path']}`): {a['description']}")
    else:
        lines.append("- *(No dormant add-ons currently installed)*")
    return "\n".join(lines)


def render_agents_md(fw_root: Path, rel_prefix: str = "<HOMUNCULUS_ROOT>") -> str:
    """Render Universal AGENTS.md combining the Governing Priority Law, 3 Core Rules, and Skill Index."""
    rules = _load_ordered_rules(fw_root)
    skills, addons = _discover_skills_and_addons(fw_root)
    parts: list[str] = [
        "# AGENTS.md — Homunculus Co-Engineering & Verification Framework",
        "",
        "> **Supreme Governing Priority Hierarchy (`1. Accuracy & Truth -> 2. Efficiency -> 3. Data Safety -> 4. Speed`)**",
        "> This workspace is governed by **Homunculus**. Every response, code edit, documentation update, and tool invocation must strictly obey the 3 Core Engineering Rules and on-demand Skill Runbooks below.",
        "",
        _render_skill_index_markdown(skills, addons, rel_prefix=rel_prefix),
        "",
        "---",
    ]
    for _stem, _path, text in rules:
        replaced = text.replace("<HOMUNCULUS_ROOT>", rel_prefix)
        parts.append(replaced)
        parts.append("\n---")
    return "\n".join(parts).rstrip() + "\n"


def render_claude_md(fw_root: Path, rel_prefix: str = "<HOMUNCULUS_ROOT>") -> str:
    """Render CLAUDE.md with Claude Code `Task` subagent tier mapping + 3 Core Rules."""
    rules = _load_ordered_rules(fw_root)
    skills, addons = _discover_skills_and_addons(fw_root)
    parts: list[str] = [
        "# CLAUDE.md — Homunculus Co-Engineering & Verification Adapter (Claude Code)",
        "",
        "> **Supreme Governing Priority Hierarchy (`1. Accuracy & Truth -> 2. Efficiency -> 3. Data Safety -> 4. Speed`)**",
        "",
        "## Claude Code Harness Dispatch & Subagent Mapping",
        "- **Subagent Tool Mapping**: Whenever a Homunculus rule or `subagent-orchestrator` instructs spawning a subagent, use Claude Code's native `Task` tool (`subagent_type`).",
        "- **Explicit Model-Tier Mapping (`'inherit'` Banned)**:",
        "  - `[lite]` / `'flash_lite'` (1-fact probe / link check) $\\rightarrow$ Claude **`haiku`**",
        "  - `[fast]` / `'flash'` (default multi-file scout / CLI inspector) $\\rightarrow$ Claude **`sonnet`**",
        "  - `[deep]` / `'pro'` (complex synthesis / Mode A-B1 / adversarial audit) $\\rightarrow$ Claude **`opus`**",
        "- **Zero Per-Edit Hooks**: Do not run `--sync-visuals` or `.svg` diagram renders after intermediate file edits; execute the `pre-commit-gate` (`X -> Y -> Z`) sequence once prior to `git commit`.",
        "",
        _render_skill_index_markdown(skills, addons, rel_prefix=rel_prefix),
        "",
        "---",
    ]
    for _stem, _path, text in rules:
        replaced = text.replace("<HOMUNCULUS_ROOT>", rel_prefix)
        parts.append(replaced)
        parts.append("\n---")
    return "\n".join(parts).rstrip() + "\n"


def render_cursor_mdc_files(fw_root: Path, rel_prefix: str = "<HOMUNCULUS_ROOT>") -> dict[str, str]:
    """Render `.cursor/rules/homunculus-<rule>.mdc` files with `alwaysApply: true` YAML frontmatter."""
    rules = _load_ordered_rules(fw_root)
    mdc_map: dict[str, str] = {}
    descriptions = {
        "co-engineering-partner": (
            "Homunculus Core Rule #1: Co-Engineering Partner, Governing Priority Law "
            "(1. Accuracy & Truth -> 2. Efficiency -> 3. Data Safety -> 4. Speed), "
            "Anti-Bloat Deferred Batching, and Project State Ledger."
        ),
        "verifiable-accuracy": (
            "Homunculus Core Rule #2: Verifiable Engineering Accuracy, Closed-World Parametric Lock, "
            "Explicit [TBD] Abstention, Dimensional [CALC] Math, and Mandatory verify_claims.py Gate."
        ),
        "data-and-credential-safety": (
            "Homunculus Core Rule #3: Data Protection, Zero Secret Read/Egress, "
            "Declarative Multi-Compartment Firewall, and Untrusted Input Prompt-Injection Quarantine."
        ),
    }
    for stem, _path, text in rules:
        desc = descriptions.get(stem, f"Homunculus always-on core rule: {stem}")
        body = text.replace("<HOMUNCULUS_ROOT>", rel_prefix)
        mdc_content = (
            "---\n"
            f"description: {desc}\n"
            "globs: \n"
            "alwaysApply: true\n"
            "---\n\n"
            f"{body}\n"
        )
        mdc_map[f"homunculus-{stem}.mdc"] = mdc_content
    return mdc_map


def build_reference_adapters_in_repo(fw_root: Path) -> dict[str, list[str]]:
    """Populate `Homunculus/adapters/{agents_md,antigravity,claude_code,claude_cowork,cursor}` reference bundles."""
    adapters_root = fw_root / "adapters"
    written: dict[str, list[str]] = {c: [] for c in SUPPORTED_CLIENTS}

    # 1. Universal AGENTS.md
    agents_dir = adapters_root / "agents_md"
    agents_dir.mkdir(parents=True, exist_ok=True)
    agents_md_path = agents_dir / "AGENTS.md"
    agents_md_path.write_text(render_agents_md(fw_root, rel_prefix="Homunculus"), encoding="utf-8")
    agents_readme = agents_dir / "README.md"
    agents_readme.write_text(
        "# Universal `AGENTS.md` Adapter (`adapters/agents_md/`)\n\n"
        "Governed by: **`1. Accuracy & Truth -> 2. Efficiency -> 3. Data Safety -> 4. Speed`**\n\n"
        "## Zero-Install Drop-In Usage\n"
        "Copy [`AGENTS.md`](AGENTS.md) to the root of your project repository (or run "
        "`python3 Homunculus/scripts/build_adapters.py --workspace /path/to/project --client agents_md`). "
        "Any `AGENTS.md`-compatible harness (OpenAI Codex, Windsurf, Aider, Zed, etc.) will automatically load "
        "all 3 Homunculus core rules and the on-demand skill index.\n",
        encoding="utf-8",
    )
    written["agents_md"].extend([str(agents_md_path), str(agents_readme)])

    # 2. Antigravity / Gemini CLI
    agy_dir = adapters_root / "antigravity"
    agy_dir.mkdir(parents=True, exist_ok=True)
    agy_hooks = agy_dir / "hooks.json"
    agy_hooks.write_text("{}\n", encoding="utf-8")
    agy_readme = agy_dir / "README.md"
    agy_readme.write_text(
        "# Antigravity / Gemini CLI Adapter (`adapters/antigravity/`)\n\n"
        "Governed by: **`1. Accuracy & Truth -> 2. Efficiency -> 3. Data Safety -> 4. Speed`**\n\n"
        "## Operating Modes\n"
        "1. **Zero-Install Drop-In Mode (Corporate IT Safe):** Keep `Homunculus/` in your workspace and prompt:\n"
        "   `Read Homunculus/HOMUNCULUS_START_HERE.md and operate under Homunculus rules and skills.`\n"
        "2. **Workspace `.agents/{rules,skills}/` & `~/.gemini/config/` Binding:** Run:\n"
        "   ```bash\n"
        "   python3 Homunculus/scripts/build_adapters.py --workspace /path/to/project --client antigravity\n"
        "   ```\n"
        "   This populates `.agents/rules/*.md` (`trigger: always_on`), `.agents/skills/*`, `.geminiignore`, and "
        "(when `--global-agy-config-dir ~/.gemini/config` is passed) links/copies `rules/*.md`, `skills/*`, and "
        "empty `hooks.json` (`{}`) into `~/.gemini/config/`.\n",
        encoding="utf-8",
    )
    written["antigravity"].extend([str(agy_hooks), str(agy_readme)])

    # 3. Claude Code
    cc_dir = adapters_root / "claude_code"
    cc_dir.mkdir(parents=True, exist_ok=True)
    claude_md_path = cc_dir / "CLAUDE.md"
    claude_md_path.write_text(render_claude_md(fw_root, rel_prefix="Homunculus"), encoding="utf-8")
    cc_settings = cc_dir / "settings.json"
    cc_settings.write_text(
        json.dumps(
            {
                "schema_version": "1.0.0",
                "description": "Homunculus Claude Code settings (zero per-edit PostToolUse hooks; deferred pre-commit-gate).",
                "hooks": {},
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    cc_readme = cc_dir / "README.md"
    cc_readme.write_text(
        "# Claude Code Adapter (`adapters/claude_code/`)\n\n"
        "Governed by: **`1. Accuracy & Truth -> 2. Efficiency -> 3. Data Safety -> 4. Speed`**\n\n"
        "## Zero-Install Drop-In Usage\n"
        "Copy [`CLAUDE.md`](CLAUDE.md) and `templates/ignore/.claudeignore` into your project root "
        "(or run `python3 Homunculus/scripts/build_adapters.py --workspace /path/to/project --client claude_code`).\n",
        encoding="utf-8",
    )
    written["claude_code"].extend([str(claude_md_path), str(cc_settings), str(cc_readme)])

    # 4. Claude Cowork
    cowork_dir = adapters_root / "claude_cowork"
    cowork_dir.mkdir(parents=True, exist_ok=True)
    cowork_readme = cowork_dir / "README.md"
    cowork_readme.write_text(
        "# Claude Cowork Desktop & Skill Zip Adapter (`adapters/claude_cowork/`)\n\n"
        "Governed by: **`1. Accuracy & Truth -> 2. Efficiency -> 3. Data Safety -> 4. Speed`**\n\n"
        "## Operating Modes\n"
        "1. **Designated Local Working Folder (Zero-Install Drop-In):** Place `Homunculus/` inside the local folder "
        "granted to Claude Cowork and instruct Cowork: `Read Homunculus/HOMUNCULUS_START_HERE.md`.\n"
        "2. **Uploadable Skill `.zip` Bundles:** Generate standalone `.zip` skill packages for GUI upload via:\n"
        "   ```bash\n"
        "   python3 Homunculus/scripts/build_adapters.py --workspace /path/to/project --client claude_cowork --package-cowork-zips\n"
        "   ```\n",
        encoding="utf-8",
    )
    written["claude_cowork"].append(str(cowork_readme))

    # 5. Cursor IDE (.cursor/rules/*.mdc)
    cur_dir = adapters_root / "cursor"
    cur_rules_dir = cur_dir / "rules"
    cur_rules_dir.mkdir(parents=True, exist_ok=True)
    for mdc_name, mdc_text in render_cursor_mdc_files(fw_root, rel_prefix="Homunculus").items():
        p = cur_rules_dir / mdc_name
        p.write_text(mdc_text, encoding="utf-8")
        written["cursor"].append(str(p))
    cur_readme = cur_dir / "README.md"
    cur_readme.write_text(
        "# Cursor IDE Adapter (`adapters/cursor/`)\n\n"
        "Governed by: **`1. Accuracy & Truth -> 2. Efficiency -> 3. Data Safety -> 4. Speed`**\n\n"
        "## Zero-Install Drop-In Usage\n"
        "Copy `adapters/cursor/rules/*.mdc` into your project's `.cursor/rules/` directory and copy "
        "`templates/ignore/.cursorignore` to your project root (or run "
        "`python3 Homunculus/scripts/build_adapters.py --workspace /path/to/project --client cursor`).\n",
        encoding="utf-8",
    )
    written["cursor"].append(str(cur_readme))
    return written


def _link_or_copy(src: Path, dst: Path, prefer_copy: bool = False) -> str:
    """Create a symlink if supported and not prefer_copy; otherwise cleanly copy file/directory (Windows-safe)."""
    dst.parent.mkdir(parents=True, exist_ok=True)
    if dst.is_symlink() or dst.exists():
        if dst.is_dir() and not dst.is_symlink():
            shutil.rmtree(dst)
        else:
            dst.unlink()

    if not prefer_copy:
        try:
            rel_target = os.path.relpath(src, dst.parent)
            dst.symlink_to(rel_target, target_is_directory=src.is_dir())
            return "symlink"
        except (OSError, ValueError):
            pass

    if src.is_dir():
        shutil.copytree(src, dst)
    else:
        shutil.copy2(src, dst)
    return "copy"


def apply_workspace_adapters(
    workspace_dir: Path,
    fw_root: Path,
    clients: list[str],
    prefer_copy: bool = False,
    install_git_hooks: bool = False,
    package_cowork_zips: bool = False,
    global_agy_config_dir: Path | None = None,
) -> dict[str, Any]:
    """Install selected client adapters, context-ignore files, and optional Git hooks into workspace_dir."""
    workspace_dir = workspace_dir.resolve()
    fw_root = fw_root.resolve()
    workspace_dir.mkdir(parents=True, exist_ok=True)

    try:
        rel_fw = os.path.relpath(fw_root, workspace_dir).replace("\\", "/")
    except ValueError:
        rel_fw = fw_root.as_posix()
    if rel_fw == ".":
        rel_fw = "Homunculus"

    installed_files: list[str] = []
    ignore_src_dir = fw_root / "templates" / "ignore"

    # Always copy or non-destructively sync context-egress ignore files for active clients
    ignore_targets = {
        "cursor": ".cursorignore",
        "claude_code": ".claudeignore",
        "claude_cowork": ".claudeignore",
        "antigravity": ".geminiignore",
        "agents_md": ".geminiignore",
    }
    seen_ignores: set[str] = set()
    for c in clients:
        ig_name = ignore_targets.get(c)
        if not ig_name or ig_name in seen_ignores:
            continue
        seen_ignores.add(ig_name)
        src_ig = ignore_src_dir / ig_name
        if src_ig.is_file():
            dst_ig = workspace_dir / ig_name
            if not dst_ig.exists():
                shutil.copy2(src_ig, dst_ig)
                installed_files.append(str(dst_ig))
            else:
                dst_text = dst_ig.read_text(encoding="utf-8")
                src_text = src_ig.read_text(encoding="utf-8")
                existing_rules = {
                    ln.strip()
                    for ln in dst_text.splitlines()
                    if ln.strip() and not ln.strip().startswith("#")
                }
                missing_rules: list[str] = []
                for ln in src_text.splitlines():
                    rule = ln.strip()
                    if rule and not rule.startswith("#") and rule not in existing_rules:
                        existing_rules.add(rule)
                        missing_rules.append(rule)
                if missing_rules:
                    prefix = "" if dst_text.endswith("\n") or not dst_text else "\n"
                    dst_ig.write_text(
                        dst_text + prefix + "\n".join(missing_rules) + "\n",
                        encoding="utf-8",
                    )
                    installed_files.append(str(dst_ig))

    if "agents_md" in clients:
        agents_out = workspace_dir / "AGENTS.md"
        agents_out.write_text(render_agents_md(fw_root, rel_prefix=rel_fw), encoding="utf-8")
        installed_files.append(str(agents_out))

    if "claude_code" in clients:
        claude_out = workspace_dir / "CLAUDE.md"
        claude_out.write_text(render_claude_md(fw_root, rel_prefix=rel_fw), encoding="utf-8")
        claude_dir = workspace_dir / ".claude"
        claude_dir.mkdir(parents=True, exist_ok=True)
        settings_out = claude_dir / "settings.json"
        if not settings_out.exists():
            src_settings = fw_root / "adapters" / "claude_code" / "settings.json"
            if src_settings.is_file():
                shutil.copy2(src_settings, settings_out)
            else:
                settings_out.write_text(
                    json.dumps(
                        {
                            "schema_version": "1.0.0",
                            "description": "Homunculus Claude Code settings (zero per-edit PostToolUse hooks; deferred pre-commit-gate).",
                            "hooks": {},
                        },
                        indent=2,
                    )
                    + "\n",
                    encoding="utf-8",
                )
        installed_files.extend([str(claude_out), str(settings_out)])

    if "cursor" in clients:
        cur_rules = workspace_dir / ".cursor" / "rules"
        cur_rules.mkdir(parents=True, exist_ok=True)
        for mdc_name, mdc_text in render_cursor_mdc_files(fw_root, rel_prefix=rel_fw).items():
            out_p = cur_rules / mdc_name
            out_p.write_text(mdc_text, encoding="utf-8")
            installed_files.append(str(out_p))

    if "antigravity" in clients:
        ws_agents_rules = workspace_dir / ".agents" / "rules"
        ws_agents_rules.mkdir(parents=True, exist_ok=True)
        for r_file in sorted((fw_root / "rules").glob("*.md")):
            dst_ws_r = ws_agents_rules / r_file.name
            _link_or_copy(r_file, dst_ws_r, prefer_copy=prefer_copy)
            installed_files.append(str(dst_ws_r))

        ws_agents_skills = workspace_dir / ".agents" / "skills"
        ws_agents_skills.mkdir(parents=True, exist_ok=True)
        active_skill_names = {
            s_dir.name for s_dir in (fw_root / "skills").glob("*") if (s_dir / "SKILL.md").is_file()
        }
        dormant_addon_names = {
            a_dir.name for a_dir in (fw_root / "addons").glob("*") if a_dir.is_dir()
        } if (fw_root / "addons").is_dir() else set()
        # Prune any previously promoted add-on folders that were demoted back to addons/
        for existing in list(ws_agents_skills.iterdir()):
            if existing.name in dormant_addon_names and existing.name not in active_skill_names:
                if existing.is_dir() and not existing.is_symlink():
                    shutil.rmtree(existing)
                else:
                    existing.unlink()
        for skill_dir in sorted((fw_root / "skills").glob("*")):
            if (skill_dir / "SKILL.md").is_file():
                dst = ws_agents_skills / skill_dir.name
                _link_or_copy(skill_dir, dst, prefer_copy=prefer_copy)
                installed_files.append(str(dst))

        if global_agy_config_dir is not None:
            g_cfg = global_agy_config_dir.expanduser().resolve()
            (g_cfg / "rules").mkdir(parents=True, exist_ok=True)
            (g_cfg / "skills").mkdir(parents=True, exist_ok=True)
            for r_file in sorted((fw_root / "rules").glob("*.md")):
                dst_r = g_cfg / "rules" / r_file.name
                _link_or_copy(r_file, dst_r, prefer_copy=prefer_copy)
                installed_files.append(str(dst_r))
            for s_dir in sorted((fw_root / "skills").glob("*")):
                if (s_dir / "SKILL.md").is_file():
                    dst_s = g_cfg / "skills" / s_dir.name
                    _link_or_copy(s_dir, dst_s, prefer_copy=prefer_copy)
                    installed_files.append(str(dst_s))
            if (fw_root / "hooks" / "hooks.json").is_file():
                dst_h = g_cfg / "hooks.json"
                _link_or_copy(fw_root / "hooks" / "hooks.json", dst_h, prefer_copy=prefer_copy)
                installed_files.append(str(dst_h))

    if "claude_cowork" in clients and package_cowork_zips:
        zip_out_dir = workspace_dir / ".homunculus_cowork_bundles"
        zip_out_dir.mkdir(parents=True, exist_ok=True)
        for s_dir in sorted((fw_root / "skills").glob("*")):
            if not (s_dir / "SKILL.md").is_file():
                continue
            z_path = zip_out_dir / f"{s_dir.name}.zip"
            with zipfile.ZipFile(z_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
                for f in sorted(s_dir.rglob("*")):
                    if f.is_file() and "__pycache__" not in f.parts:
                        arcname = f"{s_dir.name}/{f.relative_to(s_dir).as_posix()}"
                        zf.write(f, arcname=arcname)
            installed_files.append(str(z_path))

    if install_git_hooks and (workspace_dir / ".git" / "hooks").is_dir():
        hooks_dst = workspace_dir / ".git" / "hooks"
        for hook_src_name, hook_dst_name in (("pre-commit.sh", "pre-commit"), ("pre-push.sh", "pre-push")):
            src_h = fw_root / "templates" / "hooks" / hook_src_name
            if src_h.is_file():
                dst_h = hooks_dst / hook_dst_name
                shutil.copy2(src_h, dst_h)
                dst_h.chmod(dst_h.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
                installed_files.append(str(dst_h))

    return {
        "workspace": str(workspace_dir),
        "homunculus_root": str(fw_root),
        "clients_configured": clients,
        "installed_count": len(installed_files),
        "installed_files": installed_files,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Homunculus Harness-Agnostic Client Adapter & Context-Ignore Builder"
    )
    parser.add_argument("--homunculus-root", help="Explicit Homunculus framework root directory.")
    parser.add_argument("--workspace", help="Target workspace directory to apply client adapters into.")
    parser.add_argument(
        "--client",
        "--harness",
        dest="client",
        type=lambda s: s.strip().lower().replace("-", "_"),
        choices=("all", *SUPPORTED_CLIENTS),
        default="all",
        help="Target AI client harness to configure (default: all). Accepts hyphens or underscores.",
    )
    parser.add_argument(
        "--build-repo-adapters",
        action="store_true",
        help="Regenerate reference adapter bundles inside Homunculus/adapters/*.",
    )
    parser.add_argument(
        "--prefer-copy",
        action="store_true",
        help="Copy files instead of creating symlinks (corporate Windows / locked-down workstation safe).",
    )
    parser.add_argument(
        "--install-git-hooks",
        action="store_true",
        help="Install pre-commit and pre-push boundary hooks into <workspace>/.git/hooks/.",
    )
    parser.add_argument(
        "--package-cowork-zips",
        action="store_true",
        help="Build self-contained skill .zip bundles for Claude Cowork GUI upload.",
    )
    parser.add_argument(
        "--global-agy-config-dir",
        help="Optional Antigravity config directory (e.g. ~/.gemini/config) to link/copy rules and skills into.",
    )
    parser.add_argument("--json", action="store_true", help="Emit JSON output.")
    args = parser.parse_args(argv)

    if args.homunculus_root and not Path(args.homunculus_root).expanduser().is_dir():
        print(f"[FAIL] Explicit --homunculus-root does not exist: {args.homunculus_root}", file=sys.stderr)
        return 2
    fw_root = homunculus_paths.resolve_homunculus_root(args.homunculus_root)
    clients = list(SUPPORTED_CLIENTS) if args.client == "all" else [args.client]

    if args.build_repo_adapters or not args.workspace:
        built = build_reference_adapters_in_repo(fw_root)
        if not args.workspace:
            if args.json:
                print(json.dumps({"status": "PASS", "repo_adapters": built}, indent=2))
            else:
                total = sum(len(v) for v in built.values())
                print(f"[PASS] Built {total} reference client adapter files across {len(built)} harnesses in {fw_root / 'adapters'}")
            return 0

    ws_dir = Path(args.workspace).expanduser().resolve()
    agy_cfg = Path(args.global_agy_config_dir) if args.global_agy_config_dir else None
    result = apply_workspace_adapters(
        workspace_dir=ws_dir,
        fw_root=fw_root,
        clients=clients,
        prefer_copy=args.prefer_copy,
        install_git_hooks=args.install_git_hooks,
        package_cowork_zips=args.package_cowork_zips,
        global_agy_config_dir=agy_cfg,
    )
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(
            f"[PASS] Configured Homunculus adapters ({', '.join(clients)}) in {ws_dir} "
            f"({result['installed_count']} artifacts wired)."
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
