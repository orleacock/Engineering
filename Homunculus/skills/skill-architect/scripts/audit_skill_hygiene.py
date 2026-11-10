#!/usr/bin/env python3
"""
audit_skill_hygiene.py — Deterministic Skill, Rule & Add-On Hygiene, Synergy, and Homunculus Compliance Inspector
Part of `skill-architect` in Homunculus.

Governed by: 1. Accuracy & Truth -> 2. Efficiency -> 3. Data Safety -> 4. Speed
Requires ONLY Python 3.10+ standard library (zero third-party pip packages).

Modes:
  --audit                Non-destructive cleanup, hygiene & Homunculus compliance audit across rules/, skills/, and addons/ (default)
  --check-new "<query>"  Pre-creation overlap & backbone synergy check for a proposed skill or side-loaded add-on
  --target-skill <name>  Filter --audit to a specific skill or add-on name
  --strict-structure     Fail closed (exit 1) on structural defects, broken links/scripts, portability leaks, or accuracy-inverting rules
  --json                 Output machine-readable JSON

=== DEVELOPER & AI NAVIGATION MAP ===
  Owning Module : `skill-architect` (`skills/skill-architect/SKILL.md`)
  Callers       : `pre-commit-gate` (Stage Z4), `sandbox_runner.py` (transcript telemetry), `test_adapters.py`
  Callees       : `homunculus_paths.py` (`parse_frontmatter_full`), `build_adapters.py` (dynamic `ADAPTER_STALE_DRIFT` probe)
  Contract      : `scripts/script_contracts.json` [`audit_skill_hygiene.py`]
  CLI Flags     : --audit, --check-new, --target-skill, --root, --repo, --repo-root, --strict-structure, --json
  Symbol Index  (jump directly via read_file StartLine/EndLine):
    - def resolve_default_root (#L75-L81)            | def parse_frontmatter (#L84-L87)
    - def strip_markdown_formatting (#L90-L93)       | def stem_token (#L96-L105)
    - def tokenize_words (#L108-L123)                | def word_shingles (#L126-L131)
    - def extract_blocks (#L134-L192)                | def _resolve_root_placeholder (#L195-L202)
    - def check_local_links_and_scripts (#L205-L284) | def audit_script_stdlib_compliance (#L287-L366)
    - def scan_turn_waste_and_accuracy_hazards (#L369-L501) | def load_rules (#L504-L533)
    - def load_skills (#L536-L584)                   | def run_audit (#L587-L1174)
    - def run_check_new (#L1177-L1288)               | def print_human_audit (#L1291-L1384)
    - def main (#L1387-L1447)
=== END NAVIGATION MAP ===
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

_SCRIPT_DIR = Path(__file__).resolve().parent
_HOM_ROOT = _SCRIPT_DIR.parents[2]
for _p in (str(_SCRIPT_DIR), str(_HOM_ROOT / "scripts")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import homunculus_paths  # noqa: E402

STOPWORDS = {
    "the", "and", "for", "with", "that", "this", "from", "into", "when", "whenever",
    "use", "skill", "rule", "file", "files", "must", "never", "always", "only",
    "any", "all", "are", "is", "be", "to", "of", "in", "on", "or", "by", "as",
    "an", "a", "at", "it", "its", "via", "before", "after", "without", "than",
    "can", "will", "should", "may", "not", "do", "does", "run", "running", "each",
    "every", "both", "other", "such", "where", "which", "while", "also", "more",
}

ALLOWED_PLACEHOLDER_USERS: frozenset[str] = homunculus_paths.ALLOWED_PLACEHOLDER_USERS
RE_POSIX_HOME = homunculus_paths.RE_POSIX_HOME
RE_WIN_USERS = homunculus_paths.RE_WIN_USERS

MAX_RULE_FILE_BYTES = 24_000
TARGET_AGENTS_MD_BYTES = 22_500
MISNAMED_RULE_FILENAMES: frozenset[str] = frozenset(
    {"Agent.md", "Agents.md", "agents.md", "Gemini.md", "gemini.md"}
)


def resolve_default_root() -> Path:
    """Resolve Homunculus root dynamically relative to this script."""
    script_path = Path(__file__).resolve()
    for candidate in script_path.parents:
        if (candidate / "skills").is_dir() and (candidate / "rules").is_dir():
            return candidate
    return Path.cwd()


def parse_frontmatter(text: str) -> tuple[dict[str, str], int]:
    """Parse YAML frontmatter and return (fields_dict, body_start_line_1based)."""
    fields, _body, start_line = homunculus_paths.parse_frontmatter_full(text)
    return {k: str(v) for k, v in fields.items()}, start_line


def strip_markdown_formatting(text: str) -> str:
    """Strip inline markdown formatting markers while keeping words intact."""
    cleaned = re.sub(r"[*_`~>\[\]()]", " ", text)
    return cleaned


def stem_token(token: str) -> str:
    """Lightweight deterministic stemmer for skill overlap matching."""
    if token.startswith("verif"):
        return "verif"
    for suffix in ("ings", "ing", "ions", "ion", "ments", "ment", "iers", "ier", "ers", "er", "ies", "es", "s"):
        if len(token) > len(suffix) + 2 and token.endswith(suffix):
            if suffix == "ies":
                return token[:-3] + "y"
            return token[: -len(suffix)]
    return token


def tokenize_words(text: str, expand_compounds: bool = False) -> list[str]:
    """Extract lowercase alphanumeric/identifier tokens excluding stopwords."""
    cleaned = strip_markdown_formatting(text.lower())
    raw = re.findall(r"[a-z0-9_/-]{2,}", cleaned)
    tokens: list[str] = []
    for w in raw:
        t = w.strip("/_-")
        if not t or t in STOPWORDS or t.isdigit():
            continue
        if len(t) >= 3 or re.match(r"^m\d+$", t):
            tokens.append(t)
        if expand_compounds and ("-" in t or "_" in t or "/" in t):
            for part in re.split(r"[-_/]+", t):
                if (len(part) >= 3 or re.match(r"^m\d+$", part)) and part not in STOPWORDS and not part.isdigit():
                    tokens.append(part)
    return tokens


def word_shingles(text: str, k: int = 3) -> set[tuple[str, ...]]:
    """Generate k-word content shingles for similarity detection (default 3-grams)."""
    tokens = tokenize_words(text)
    if len(tokens) < k:
        return set()
    return {tuple(tokens[i : i + k]) for i in range(len(tokens) - k + 1)}


def extract_blocks(text: str, start_line: int) -> list[dict[str, Any]]:
    """
    Extract logical top-level bullet or paragraph blocks with 1-based line ranges.
    Consecutive nested sub-bullets (`  - ...`) stay grouped with their parent bullet
    so multi-clause vs. sub-bulleted equivalents compare cleanly.
    """
    lines = text.splitlines()
    blocks: list[dict[str, Any]] = []
    cur_lines: list[str] = []
    cur_start = start_line
    in_fence = False

    def flush(end_line_no: int) -> None:
        nonlocal cur_lines
        if not cur_lines:
            return
        block_text = "\n".join(cur_lines).strip()
        toks = tokenize_words(block_text)
        if len(toks) >= 14:
            blocks.append({
                "start_line": cur_start,
                "end_line": end_line_no,
                "text": block_text,
                "words": len(block_text.split()),
                "tokens": set(toks),
                "shingles": word_shingles(block_text, 3),
            })
        cur_lines = []

    for idx in range(start_line - 1, len(lines)):
        line_no = idx + 1
        line = lines[idx]
        stripped = line.strip()
        if stripped.startswith("```"):
            in_fence = not in_fence
            flush(line_no - 1)
            cur_start = line_no + 1
            continue
        if in_fence:
            continue

        is_top_bullet = bool(re.match(r"^\s{0,3}(?:[-*+]|\d+\.)\s+", line))
        is_heading = stripped.startswith("#")
        is_blank = not stripped

        if is_heading or is_blank or is_top_bullet:
            flush(line_no - 1)
            if is_top_bullet:
                cur_start = line_no
                cur_lines = [line]
            else:
                cur_start = line_no + 1
        else:
            if not cur_lines:
                cur_start = line_no
            cur_lines.append(line)

    flush(len(lines))
    return blocks


def _resolve_root_placeholder(raw_path: str, root: Path) -> str:
    """Expand <HOMUNCULUS_ROOT> or Homunculus/ prefix to the active framework root."""
    s = raw_path.strip()
    if s.startswith("<HOMUNCULUS_ROOT>/"):
        return str(root / s[len("<HOMUNCULUS_ROOT>/") :])
    if s.startswith("Homunculus/"):
        return str(root / s[len("Homunculus/") :])
    return s


def check_local_links_and_scripts(
    root: Path, skill_dir: Path, doc_path: Path, text: str
) -> tuple[list[str], set[Path]]:
    """
    Verify relative markdown links and script paths while skipping inert inline-code
    or fenced-code syntax examples (`![Alt](path.png)`). Supports `<HOMUNCULUS_ROOT>/...`.
    """
    broken: list[str] = []
    referenced_scripts: set[Path] = set()
    lines = text.splitlines()
    in_fence = False
    rel_doc = (
        f"{skill_dir.name}/{doc_path.name}"
        if doc_path.parent == skill_dir
        else f"{skill_dir.name}/references/{doc_path.name}"
    )

    for line_no, line in enumerate(lines, 1):
        stripped = line.strip()
        if stripped.startswith("```"):
            in_fence = not in_fence
            continue

        # 1. Check Markdown links `[label](target)` OUTSIDE code fences and OUTSIDE inline backticks
        if not in_fence:
            line_no_code = re.sub(r"`[^`]*`", "", line)
            for m in re.finditer(r"\[[^\]]+\]\(([^)]+)\)", line_no_code):
                target = m.group(1).strip()
                if target.startswith(("http://", "https://", "mailto:", "conversation://", "#")):
                    continue
                if target.startswith("file://"):
                    clean = target[len("file://") :].split("#")[0]
                    target_path = Path(clean)
                else:
                    clean = target.split("#")[0]
                    expanded = _resolve_root_placeholder(clean, root)
                    if not expanded or "<" in expanded or ">" in expanded or "..." in expanded:
                        continue
                    target_path = (doc_path.parent / expanded).resolve() if not expanded.startswith("/") else Path(expanded)
                    if not target_path.exists() and not expanded.startswith("/"):
                        root_cand_link = (root / expanded).resolve()
                        if root_cand_link.exists():
                            target_path = root_cand_link
                if not target_path.exists():
                    broken.append(f"{doc_path}#L{line_no}-L{line_no}: Broken link in {rel_doc} -> {target}")
                elif target_path.suffix == ".py":
                    referenced_scripts.add(target_path.resolve())

        # 2. Check script path mentions (including <HOMUNCULUS_ROOT>/.../scripts/*.py) and bare script basenames
        for m in re.finditer(
            r"(?<![A-Za-z0-9_./-])((?:<HOMUNCULUS_ROOT>/|Homunculus/|/|\.\.?/|[A-Za-z0-9_.-]+/)?[A-Za-z0-9_./-]*scripts/[A-Za-z0-9_.-]+\.py)",
            line,
        ):
            raw_p = m.group(1)
            expanded_p = _resolve_root_placeholder(raw_p, root)
            if "<" in expanded_p or ">" in expanded_p or "..." in expanded_p:
                continue
            if expanded_p.startswith("/"):
                p = Path(expanded_p)
            else:
                p = (skill_dir / expanded_p).resolve()
                if not p.exists():
                    root_p = (root / expanded_p).resolve()
                    if root_p.exists():
                        p = root_p
            if not p.exists():
                broken.append(f"{doc_path}#L{line_no}-L{line_no}: Missing script path in {rel_doc} -> {raw_p}")
            else:
                referenced_scripts.add(p.resolve())

        for m in re.finditer(r"`([A-Za-z0-9_]+\.py)`", line):
            script_basename = m.group(1)
            local_cand = skill_dir / "scripts" / script_basename
            root_cand = root / "scripts" / script_basename
            if local_cand.exists():
                referenced_scripts.add(local_cand.resolve())
            elif root_cand.exists():
                referenced_scripts.add(root_cand.resolve())

    return broken, referenced_scripts


def audit_script_stdlib_compliance(py_script: Path, local_modules: set[str]) -> list[dict[str, Any]]:
    """Verify a skill or root .py script uses functional naming, zero internal ticket bleed, stdlib imports, and an up-to-date navigation map."""
    defects: list[dict[str, Any]] = []
    if re.search(r"(?:^|[_-])(?:phase|stage|wave|sprint|milestone)[_-]?\d+[a-z]?(?:$|[_.-])", py_script.stem, re.IGNORECASE):
        defects.append({
            "category": "[LOAD-BEARING DEFECT]",
            "code": "NON_FUNCTIONAL_MODULE_NAME",
            "location": f"{py_script}#L1-L1",
            "summary": (
                f"Module `{py_script.name}` uses a build-milestone name instead of a functional capability name."
            ),
        })
    try:
        text = py_script.read_text(encoding="utf-8")
    except OSError as exc:
        defects.append({
            "category": "[LOAD-BEARING DEFECT]",
            "code": "SCRIPT_READ_ERROR",
            "location": f"{py_script}#L1-L1",
            "summary": f"OSError reading `{py_script.name}`: {exc}",
        })
        return defects

    ast_info = homunculus_paths.inspect_python_ast_and_map(
        py_script, local_modules=local_modules, source_text=text
    )
    if ast_info["syntax_error"] is not None:
        err = ast_info["syntax_error"]
        defects.append({
            "category": "[LOAD-BEARING DEFECT]",
            "code": "SCRIPT_SYNTAX_ERROR",
            "location": f"{py_script}#L{err['line']}-L{err['line']}",
            "summary": f"SyntaxError in `{py_script.name}`: {err['msg']}",
        })
        return defects

    for idx, line in enumerate(text.splitlines(), start=1):
        m_bleed = re.search(r"\b(?:PF|INH|CRACK|FEATURE)-\d{1,3}\b|Parent\s+Flaw", line)
        if m_bleed and py_script.name != "audit_skill_hygiene.py":
            defects.append({
                "category": "[LOAD-BEARING DEFECT]",
                "code": "DEV_JOURNAL_CROSS_BLEED",
                "location": f"{py_script}#L{idx}-L{idx}",
                "summary": (
                    f"`{py_script.name}` references internal build/migration tag `{m_bleed.group(0)}` "
                    "(use self-contained functional descriptions in shipped source code)."
                ),
            })

    for imp in ast_info["non_stdlib_imports"]:
        lineno = imp["line"]
        defects.append({
            "category": "[LOAD-BEARING DEFECT]",
            "code": "NON_STDLIB_SKILL_SCRIPT",
            "location": f"{py_script}#L{lineno}-L{lineno}",
            "summary": (
                f"`{py_script.name}` imports non-stdlib package `{imp['stmt']}` at top level "
                "(violates Homunculus Zero-Pip Portability Invariant)."
            ),
        })

    if ast_info["map_present"] and ast_info["map_mismatches"]:
        can_auto_heal = os.access(py_script, os.W_OK) and not any(
            "Removed symbol" in m or "#L999" in m for m in ast_info["map_mismatches"]
        )
        if can_auto_heal:
            heal_res = homunculus_paths.sync_script_navigation_map(py_script, write=True)
            ast_info["map_mismatches"] = heal_res.get("mismatches", [])
        if ast_info["map_mismatches"]:
            first_mismatch = ast_info["map_mismatches"][0]
            defects.append({
                "category": "[LOAD-BEARING DEFECT]",
                "code": "STALE_SCRIPT_NAVIGATION_MAP",
                "location": f"{py_script}#L1-L50",
                "summary": (
                    f"`{py_script.name}` navigation map `#Lstart-Lend` coordinates drifted from AST "
                    f"({first_mismatch}; run `python3 scripts/homunculus_paths.py --sync-maps` to heal)."
                ),
            })
    return defects


def scan_turn_waste_and_accuracy_hazards(
    doc_path: Path, skill_name: str, text: str
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Scan a SKILL.md, reference, or rule for accuracy-inverting bans, portability leaks, dev-journal cross-bleed, and mid-task churn."""
    defects: list[dict[str, Any]] = []
    turn_hazards: list[dict[str, Any]] = []
    lines = text.splitlines()

    for idx, line in enumerate(lines):
        line_no = idx + 1
        low = line.lower()

        # 0. Check for development journal / lesson ticket cross-bleed in operational rules & skills
        # Allow generic `<Project>_Lessons_Learned.md` or `*_Lessons_Learned.md` template references,
        # but block concrete project journal names (e.g. Homunculus_Lessons_Learned) and LL-xxx ticket IDs.
        for m_ll in re.finditer(r"\b([A-Za-z0-9_]+)_Lessons_Learned\b", line):
            prefix = m_ll.group(1)
            if prefix.lower() not in ("project", "project_name", "companion", "companion_project", "name"):
                defects.append({
                    "category": "[LOAD-BEARING DEFECT]",
                    "code": "DEV_JOURNAL_CROSS_BLEED",
                    "location": f"{doc_path}#L{line_no}-L{line_no}",
                    "summary": (
                        f"Operational rule or skill references concrete `{m_ll.group(0)}` ledger "
                        "(violates One-Way Journal -> Core boundary and clean-room portability)."
                    ),
                })
        m_ticket = re.search(r"\b(?:LL-\d{3}|(?:PF|INH|CRACK|FEATURE)-\d{1,3})\b|Parent\s+Flaw", line)
        if m_ticket:
            defects.append({
                "category": "[LOAD-BEARING DEFECT]",
                "code": "DEV_JOURNAL_CROSS_BLEED",
                "location": f"{doc_path}#L{line_no}-L{line_no}",
                "summary": (
                    f"Operational rule or skill references internal build/ticket tag `{m_ticket.group(0)}` "
                    "(violates One-Way Journal -> Core boundary and clean-room portability)."
                ),
            })

        # 0b. Check for hardcoded OS user paths inside rules/skills
        for m_posix in RE_POSIX_HOME.finditer(line):
            if m_posix.group(1).lower() not in ALLOWED_PLACEHOLDER_USERS:
                defects.append({
                    "category": "[LOAD-BEARING DEFECT]",
                    "code": "HARDCODED_USER_PATH_IN_SKILL",
                    "location": f"{doc_path}#L{line_no}-L{line_no}",
                    "summary": (
                        f"Hardcoded POSIX user path `{m_posix.group(0)}` in `{doc_path.name}` "
                        "(use `<HOMUNCULUS_ROOT>` or `<memory_root>` for Cross-OS Portability)."
                    ),
                })
        for m_win in RE_WIN_USERS.finditer(line):
            if m_win.group(1).lower() not in ALLOWED_PLACEHOLDER_USERS:
                defects.append({
                    "category": "[LOAD-BEARING DEFECT]",
                    "code": "HARDCODED_USER_PATH_IN_SKILL",
                    "location": f"{doc_path}#L{line_no}-L{line_no}",
                    "summary": (
                        f"Hardcoded Windows user path `{m_win.group(0)}` in `{doc_path.name}` "
                        "(use `<HOMUNCULUS_ROOT>` or `<memory_root>` for Cross-OS Portability)."
                    ),
                })

        # 1. Check: Blanket ban on reading .py files without porting/diagnostic override
        if (
            re.search(r"never\s+read\b.*\.py\b|do\s+not\s+read\b.*\.py\b", low)
            and "porting" not in low
            and "diagnos" not in low
            and "traceback" not in low
            and "routine" not in low
        ):
            defects.append({
                "category": "[LOAD-BEARING DEFECT]",
                "code": "BLANKET_PY_SOURCE_BAN",
                "location": f"{doc_path}#L{line_no}-L{line_no}",
                "summary": (
                    "Blanket ban on reading `.py` source files without Two-Mode Accuracy Override "
                    "(porting/auditing/diagnosing requires reading `.py` source truth)."
                ),
            })

        # 2. Check: Blanket ban on ls/find across repos without live-disk mutation override
        if (
            re.search(r"never\s+run\s+`?ls`?\s+or\s+`?find`?\s+across\s+repos", low)
            and "live" not in low
        ):
            defects.append({
                "category": "[LOAD-BEARING DEFECT]",
                "code": "UNSCOPED_LS_FIND_BAN",
                "location": f"{doc_path}#L{line_no}-L{line_no}",
                "summary": (
                    "Unscoped ban on `ls`/`find` across repos without Live-Disk Accuracy Override "
                    "when `AUTO-TREE` is deferred until `pre-commit-gate`."
                ),
            })

        # 3. Check: Mid-procedure `--sync-visuals` outside pre-commit-gate
        if "--sync-visuals" in line and skill_name not in ("pre-commit-gate", "skill-architect"):
            window = "\n".join(lines[max(0, idx - 4) : min(len(lines), idx + 5)]).lower()
            if (
                "pre-commit-gate" not in window
                and "prior to `git commit`" not in window
                and "prior to commit" not in window
                and "deferred" not in window
                and "table" not in window
                and "cheat-sheet" not in window
                and "reference" not in window
            ):
                turn_hazards.append({
                    "category": "[TURN-WASTE HAZARD]",
                    "code": "MID_TASK_VISUAL_SYNC",
                    "location": f"{doc_path}#L{line_no}-L{line_no}",
                    "summary": (
                        f"`{skill_name}` ({doc_path.name}) instructs running `--sync-visuals` "
                        "inside a procedure without deferring to `pre-commit-gate` (causes mid-session index/visual churn)."
                    ),
                })

        # 4. Check: Relative `./scripts/*.py` CLI invocations inside SKILL.md that fail when cwd != skill_dir
        if doc_path.name == "SKILL.md" and skill_name != "skill-architect":
            for m_rel in re.finditer(r"(?<![A-Za-z0-9_./-])(\./scripts/[A-Za-z0-9_.-]+\.py)", line):
                rel_script = m_rel.group(1)
                turn_hazards.append({
                    "category": "[TURN-WASTE HAZARD]",
                    "code": "RELATIVE_SCRIPT_PATH_HAZARD",
                    "location": f"{doc_path}#L{line_no}-L{line_no}",
                    "summary": (
                        f"`{skill_name}` invokes relative `{rel_script}` instead of `<HOMUNCULUS_ROOT>/...` canonical path "
                        "(fails when agent `cwd` is a target repo, burning extra recovery turns)."
                    ),
                })

    return defects, turn_hazards


def load_rules(root: Path, rules_dir: Path) -> list[dict[str, Any]]:
    """
    Load all global rules (supporting both flat `rules/*.md` in Homunculus
    and nested `rules/*/*.md`) and their content blocks.
    """
    rules: list[dict[str, Any]] = []
    if not rules_dir.is_dir():
        return rules
    md_paths = sorted(set(rules_dir.glob("*.md")) | set(rules_dir.glob("*/*.md")))
    for md_path in md_paths:
        text = md_path.read_text(encoding="utf-8")
        fm, body_start = parse_frontmatter(text)
        blocks = extract_blocks(text, body_start)
        broken_links, ref_scripts = check_local_links_and_scripts(root, md_path.parent, md_path, text)
        words = len(text.split())
        rules.append({
            "name": md_path.stem,
            "path": md_path,
            "frontmatter": fm,
            "body_start": body_start,
            "text": text,
            "lines": len(text.splitlines()),
            "words": words,
            "est_tokens": int(round(words * 1.35)),
            "blocks": blocks,
            "broken_links": broken_links,
            "referenced_scripts": ref_scripts,
            "all_shingles": word_shingles(text, 3),
        })
    return rules


def load_skills(root: Path, skills_dir: Path, tier_label: str = "skill") -> list[dict[str, Any]]:
    """Load all SKILL.md files, reference files, metadata, scripts, and content blocks from skills_dir or addons_dir."""
    skills: list[dict[str, Any]] = []
    if not skills_dir.is_dir():
        return skills
    for skill_md in sorted(skills_dir.glob("*/SKILL.md")):
        skill_dir = skill_md.parent
        text = skill_md.read_text(encoding="utf-8")
        fm, body_start = parse_frontmatter(text)
        blocks = extract_blocks(text, body_start)
        broken_links, ref_scripts = check_local_links_and_scripts(root, skill_dir, skill_md, text)

        ref_files: list[dict[str, Any]] = []
        ref_dir = skill_dir / "references"
        if ref_dir.is_dir():
            for ref_md in sorted(ref_dir.glob("*.md")):
                ref_text = ref_md.read_text(encoding="utf-8")
                ref_broken, sub_scripts = check_local_links_and_scripts(root, skill_dir, ref_md, ref_text)
                broken_links.extend(ref_broken)
                ref_scripts.update(sub_scripts)
                ref_files.append({
                    "name": ref_md.name,
                    "path": ref_md,
                    "text": ref_text,
                    "words": len(ref_text.split()),
                })

        disk_scripts = sorted((skill_dir / "scripts").glob("*.py")) if (skill_dir / "scripts").is_dir() else []
        ref_words = sum(r["words"] for r in ref_files)
        skills.append({
            "name": fm.get("name", skill_dir.name),
            "tier": tier_label,
            "dir": skill_dir,
            "path": skill_md,
            "frontmatter": fm,
            "body_start": body_start,
            "text": text,
            "lines": len(text.splitlines()),
            "words": len(text.split()),
            "est_tokens": int(round(len(text.split()) * 1.35)),
            "ref_files_count": len(ref_files),
            "ref_words": ref_words,
            "ref_files": ref_files,
            "blocks": blocks,
            "broken_links": broken_links,
            "disk_scripts": disk_scripts,
            "referenced_scripts": ref_scripts,
        })
    return skills


def run_audit(
    root: Path,
    rules_dir: Path,
    skills_dir: Path,
    target_skill: str | None = None,
) -> dict[str, Any]:
    """Execute Mode 2 non-destructive hygiene, redundancy, synergy, and Homunculus compliance audit."""
    rules = load_rules(root, rules_dir)
    addons_dir = root / "addons"
    all_skills = load_skills(root, skills_dir, tier_label="skill") + load_skills(root, addons_dir, tier_label="addon")
    skills = [s for s in all_skills if not target_skill or s["name"] == target_skill or s["dir"].name == target_skill]

    load_bearing_defects: list[dict[str, Any]] = []
    turn_waste_hazards: list[dict[str, Any]] = []
    rule_to_rule_overlaps: list[dict[str, Any]] = []
    core_rule_overlaps: list[dict[str, Any]] = []
    cross_skill_overlaps: list[dict[str, Any]] = []
    orphan_candidates: list[dict[str, Any]] = []
    rule_summaries: list[dict[str, Any]] = []
    skill_summaries: list[dict[str, Any]] = []

    if not rules:
        load_bearing_defects.append({
            "category": "[LOAD-BEARING DEFECT]",
            "code": "EMPTY_RULES_ROOT",
            "location": f"{rules_dir}#L1-L1",
            "summary": f"Zero rule files discovered in `{rules_dir}`.",
        })
    if not skills:
        load_bearing_defects.append({
            "category": "[LOAD-BEARING DEFECT]",
            "code": "EMPTY_SKILLS_ROOT",
            "location": f"{skills_dir}#L1-L1",
            "summary": f"Zero matching skill files discovered in `{skills_dir}`.",
        })

    # Collect local Python module stems for zero-pip stdlib checks
    local_py_modules: set[str] = {"scripts", "skills", "addons", "adapters", "tests"}
    for py_file in root.rglob("*.py"):
        local_py_modules.add(py_file.stem)

    # Check hooks/hooks.json for per-edit PostToolUse hooks
    hooks_json = root / "hooks" / "hooks.json"
    if hooks_json.is_file():
        try:
            hooks_data = json.loads(hooks_json.read_text(encoding="utf-8"))
            if hooks_data.get("hooks", {}).get("PostToolUse") or hooks_data.get("PostToolUse"):
                turn_waste_hazards.append({
                    "category": "[TURN-WASTE HAZARD]",
                    "code": "ACTIVE_POST_TOOL_HOOK",
                    "location": f"{hooks_json}#L1-L10",
                    "summary": "Active `PostToolUse` hook registered in `hooks.json` (causes per-edit latency/churn).",
                })
        except Exception as exc:
            load_bearing_defects.append({
                "category": "[LOAD-BEARING DEFECT]",
                "code": "INVALID_HOOKS_JSON",
                "location": f"{hooks_json}#L1-L1",
                "summary": f"Failed to parse `hooks.json`: {exc}",
            })

    # Audit rules for broken links, accuracy-inverting defects, footprint & Rule-to-Rule overlaps
    all_known_scripts = sorted(
        set(skills_dir.glob("*/scripts/*.py"))
        | (set(addons_dir.glob("*/scripts/*.py")) if addons_dir.is_dir() else set())
        | (set((root / "scripts").glob("*.py")) if (root / "scripts").is_dir() else set())
    )
    all_referenced_scripts: set[Path] = set()
    for r in rules:
        r_bytes = len(r["text"].encode("utf-8"))
        if r_bytes > MAX_RULE_FILE_BYTES:
            load_bearing_defects.append({
                "category": "[LOAD-BEARING DEFECT]",
                "code": "RULE_BYTE_CAP_EXCEEDED",
                "location": f"{r['path']}#L1-L5",
                "summary": (
                    f"Global rule `{r['name']}` is {r_bytes} UTF-8 bytes, exceeding the "
                    f"{MAX_RULE_FILE_BYTES}-byte platform truncation cap."
                ),
            })
        if not r["frontmatter"].get("trigger"):
            load_bearing_defects.append({
                "category": "[LOAD-BEARING DEFECT]",
                "code": "MISSING_RULE_TRIGGER_FRONTMATTER",
                "location": f"{r['path']}#L1-L5",
                "summary": (
                    f"Global rule `{r['name']}` is missing YAML frontmatter `trigger: always_on` "
                    "(required for Antigravity `.agents/rules/` and `~/.gemini/config/rules/` auto-injection)."
                ),
            })
        r_defects, r_hazards = scan_turn_waste_and_accuracy_hazards(r["path"], r["name"], r["text"])
        load_bearing_defects.extend(r_defects)
        turn_waste_hazards.extend(r_hazards)
        for broken in r["broken_links"]:
            load_bearing_defects.append({
                "category": "[LOAD-BEARING DEFECT]",
                "code": "BROKEN_RULE_LINK_OR_SCRIPT",
                "location": broken.split(": ")[0],
                "summary": broken.split(": ", 1)[1],
            })
        for ks in all_known_scripts:
            if ks.name in r["text"]:
                r["referenced_scripts"].add(ks.resolve())
        all_referenced_scripts.update(r["referenced_scripts"])
        rule_summaries.append({
            "rule": r["name"],
            "path": str(r["path"]),
            "trigger": r["frontmatter"].get("trigger", "always_on"),
            "bytes": r_bytes,
            "lines": r["lines"],
            "words": r["words"],
            "est_tokens": r["est_tokens"],
            "scripts_referenced": len(r["referenced_scripts"]),
        })

    # Audit case-exact filenames, byte caps, frontmatter polarity, and adapter sync drift
    adapters_dir = root / "adapters"
    case_scan_dirs: list[Path] = [root]
    if adapters_dir.is_dir():
        for dirpath, _dirnames, _filenames in os.walk(adapters_dir):
            case_scan_dirs.append(Path(dirpath))
    for c_dir in case_scan_dirs:
        try:
            dir_entries = sorted(os.listdir(c_dir))
        except OSError:
            continue
        for fname in dir_entries:
            if fname in MISNAMED_RULE_FILENAMES:
                bad_case_path = c_dir / fname
                load_bearing_defects.append({
                    "category": "[LOAD-BEARING DEFECT]",
                    "code": "MISNAMED_AGENTS_MD_CASE",
                    "location": f"{bad_case_path}#L1-L1",
                    "summary": (
                        f"Case-variant rule file `{fname}` fails case-sensitive loader discovery "
                        "(must be uppercase `AGENTS.md` or `GEMINI.md`)."
                    ),
                })

    for root_rule_name in ("AGENTS.md", "GEMINI.md"):
        root_rule_path = root / root_rule_name
        if root_rule_path.is_file():
            rr_bytes = len(root_rule_path.read_bytes())
            if rr_bytes > MAX_RULE_FILE_BYTES:
                load_bearing_defects.append({
                    "category": "[LOAD-BEARING DEFECT]",
                    "code": "RULE_BYTE_CAP_EXCEEDED",
                    "location": f"{root_rule_path}#L1-L5",
                    "summary": (
                        f"Workspace `{root_rule_name}` is {rr_bytes} UTF-8 bytes, exceeding the "
                        f"{MAX_RULE_FILE_BYTES}-byte platform truncation cap."
                    ),
                })

    if adapters_dir.is_dir():
        adapter_agents_md = adapters_dir / "agents_md" / "AGENTS.md"
        adapter_claude_md = adapters_dir / "claude_code" / "CLAUDE.md"
        adapter_cursor_dir = adapters_dir / "cursor" / "rules"

        if adapter_agents_md.is_file():
            ag_bytes = len(adapter_agents_md.read_bytes())
            if ag_bytes > TARGET_AGENTS_MD_BYTES:
                load_bearing_defects.append({
                    "category": "[LOAD-BEARING DEFECT]",
                    "code": "RULE_BYTE_CAP_EXCEEDED",
                    "location": f"{adapter_agents_md}#L1-L5",
                    "summary": (
                        f"Generated `adapters/agents_md/AGENTS.md` is {ag_bytes} UTF-8 bytes, exceeding the "
                        f"{TARGET_AGENTS_MD_BYTES}-byte safety ceiling ({MAX_RULE_FILE_BYTES}-byte hard cap)."
                    ),
                })

        for plain_adapter in (adapter_agents_md, adapter_claude_md):
            if plain_adapter.is_file():
                p_text = plain_adapter.read_text(encoding="utf-8", errors="replace")
                if p_text.lstrip().startswith("---"):
                    load_bearing_defects.append({
                        "category": "[LOAD-BEARING DEFECT]",
                        "code": "INVALID_ADAPTER_FRONTMATTER_POLARITY",
                        "location": f"{plain_adapter}#L1-L5",
                        "summary": (
                            f"`{plain_adapter.relative_to(root).as_posix()}` starts with YAML frontmatter `---` "
                            "(plain Markdown body required for AGENTS.md / CLAUDE.md)."
                        ),
                    })

        if adapter_cursor_dir.is_dir():
            for mdc_file in sorted(adapter_cursor_dir.glob("*.mdc")):
                mdc_text = mdc_file.read_text(encoding="utf-8", errors="replace")
                mdc_fm, _ = parse_frontmatter(mdc_text)
                if not mdc_text.startswith("---") or str(mdc_fm.get("alwaysApply", "")).lower() != "true":
                    load_bearing_defects.append({
                        "category": "[LOAD-BEARING DEFECT]",
                        "code": "INVALID_ADAPTER_FRONTMATTER_POLARITY",
                        "location": f"{mdc_file}#L1-L6",
                        "summary": (
                            f"Cursor rule `{mdc_file.name}` is missing leading YAML frontmatter with `alwaysApply: true`."
                        ),
                    })

        build_adapters_py = root / "scripts" / "build_adapters.py"
        if build_adapters_py.is_file() and not target_skill:
            try:
                spec = importlib.util.spec_from_file_location("_homunculus_adapter_drift_probe", build_adapters_py)
                if spec is not None and spec.loader is not None:
                    ba_mod = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(ba_mod)
                    expected_pairs: list[tuple[Path, str]] = []
                    try:
                        expected_pairs.append((adapter_agents_md, ba_mod.render_agents_md(root, rel_prefix="Homunculus")))
                    except ValueError as exc:
                        load_bearing_defects.append({
                            "category": "[LOAD-BEARING DEFECT]",
                            "code": "RULE_BYTE_CAP_EXCEEDED",
                            "location": f"{adapter_agents_md}#L1-L5",
                            "summary": f"`render_agents_md()` failed byte-cap check: {exc}",
                        })
                    expected_pairs.append((adapter_claude_md, ba_mod.render_claude_md(root, rel_prefix="Homunculus")))
                    for mdc_name, mdc_expected in ba_mod.render_cursor_mdc_files(root, rel_prefix="Homunculus").items():
                        expected_pairs.append((adapter_cursor_dir / mdc_name, mdc_expected))

                    for disk_path, expected_content in expected_pairs:
                        if not disk_path.is_file() or disk_path.read_text(encoding="utf-8", errors="replace") != expected_content:
                            load_bearing_defects.append({
                                "category": "[LOAD-BEARING DEFECT]",
                                "code": "ADAPTER_STALE_DRIFT",
                                "location": f"{disk_path}#L1-L1",
                                "summary": (
                                    f"Adapter `{disk_path.relative_to(root).as_posix()}` is missing or out of sync with `rules/` "
                                    "(re-run `python3 scripts/build_adapters.py --build-repo-adapters`)."
                                ),
                            })
            except Exception as exc:
                load_bearing_defects.append({
                    "category": "[LOAD-BEARING DEFECT]",
                    "code": "ADAPTER_STALE_DRIFT",
                    "location": f"{build_adapters_py}#L1-L1",
                    "summary": f"Failed to verify adapter parity via `build_adapters.py`: {exc}",
                })

    # Rule-to-Rule overlap check (highest priority since always_on rules burn tokens on every turn)
    for i in range(len(rules)):
        for j in range(i + 1, len(rules)):
            ra = rules[i]
            rb = rules[j]
            for ba in ra["blocks"]:
                if ba["words"] < 30 or not ba["shingles"]:
                    continue
                for bb in rb["blocks"]:
                    if bb["words"] < 30 or not bb["shingles"]:
                        continue
                    shared = ba["shingles"] & bb["shingles"]
                    token_jaccard = len(ba["tokens"] & bb["tokens"]) / max(1, len(ba["tokens"] | bb["tokens"]))
                    if len(shared) >= 6 or (len(shared) >= 4 and token_jaccard >= 0.25):
                        rule_to_rule_overlaps.append({
                            "category": "[ALWAYS-ON RULE DUPLICATION — HIGHEST TOKEN TAX]",
                            "rule_a": ra["name"],
                            "location_a": f"{ra['path']}#L{ba['start_line']}-L{ba['end_line']}",
                            "rule_b": rb["name"],
                            "location_b": f"{rb['path']}#L{bb['start_line']}-L{bb['end_line']}",
                            "shared_3grams": len(shared),
                            "token_jaccard_pct": round(token_jaccard * 100, 1),
                            "rationale": (
                                f"Always-on rules `{ra['name']}` ({ba['words']}w) and `{rb['name']}` ({bb['words']}w) "
                                f"share {len(shared)} 3-gram phrases ({round(token_jaccard * 100, 1)}% vocab overlap). "
                                "Because `always_on` rules load on 100% of turns, deduplicating overlap here yields permanent every-turn token savings."
                            ),
                        })

    # Audit each skill & side-loaded add-on
    for s in skills:
        s_path = s["path"]
        s_name = s["name"]
        s_text = s["text"]

        if re.search(r"(?:^|[_-])(?:phase|stage|wave|sprint|milestone)[_-]?\d+[a-z]?(?:$|[_.-])", s_name, re.IGNORECASE):
            load_bearing_defects.append({
                "category": "[LOAD-BEARING DEFECT]",
                "code": "NON_FUNCTIONAL_MODULE_NAME",
                "location": f"{s_path}#L1-L1",
                "summary": f"Skill `{s_name}` uses a build-milestone directory/skill name instead of a functional capability name.",
            })

        # 1. Frontmatter & required Foundation-First sections
        if not s["frontmatter"].get("name") or not s["frontmatter"].get("description"):
            load_bearing_defects.append({
                "category": "[LOAD-BEARING DEFECT]",
                "code": "MISSING_FRONTMATTER",
                "location": f"{s_path}#L1-L10",
                "summary": f"`{s_name}` is missing YAML frontmatter `name` or `description`.",
            })

        low_text = s_text.lower()
        for req_label, req_pattern in (
            ("Pre-Flight Foundation Checks", r"pre-flight|foundation\s+check"),
            ("Step-Level Verification Gates", r"verification\s+gate|verification\s+criterion|success\s+criterion|step-level|end-of-pass.*gate"),
            ("Stop & Escalation Conditions", r"stop\s*[/&]\s*escalation|stop\s+(?:and|or)\s+escalation|stop\s+condition"),
        ):
            if not re.search(req_pattern, low_text):
                load_bearing_defects.append({
                    "category": "[LOAD-BEARING DEFECT]",
                    "code": "MISSING_FOUNDATION_SECTION",
                    "location": f"{s_path}#L{s['body_start']}-L{s['lines']}",
                    "summary": f"`{s_name}` is missing required Foundation-First section: `{req_label}`.",
                })

        # 2. Broken links & script AST + zero-pip stdlib checks
        for broken in s["broken_links"]:
            load_bearing_defects.append({
                "category": "[LOAD-BEARING DEFECT]",
                "code": "BROKEN_SKILL_LINK_OR_SCRIPT",
                "location": broken.split(": ")[0],
                "summary": broken.split(": ", 1)[1],
            })

        for py_script in s["disk_scripts"]:
            load_bearing_defects.extend(audit_script_stdlib_compliance(py_script, local_py_modules))
            if py_script.resolve() not in s["referenced_scripts"]:
                orphan_candidates.append({
                    "category": "[ORPHAN CANDIDATE — CONFIRM EXTERNAL USAGE]",
                    "location": str(py_script),
                    "summary": f"Script `{py_script.name}` in `{s_name}/scripts/` is not referenced in `{s_name}/SKILL.md` or `references/*.md`.",
                })
        all_referenced_scripts.update(s["referenced_scripts"])

        # 3. Turn-waste & accuracy hazards across SKILL.md and references/*.md
        s_defects, s_hazards = scan_turn_waste_and_accuracy_hazards(s_path, s_name, s_text)
        load_bearing_defects.extend(s_defects)
        turn_waste_hazards.extend(s_hazards)
        for rf in s["ref_files"]:
            rf_defects, rf_hazards = scan_turn_waste_and_accuracy_hazards(rf["path"], s_name, rf["text"])
            load_bearing_defects.extend(rf_defects)
            turn_waste_hazards.extend(rf_hazards)

        # 4. Compare skill blocks against Always-On Global Rules (Bidirectional Directionality Check)
        if s_name != "skill-architect":
            for blk in s["blocks"]:
                if blk["words"] < 40 or not blk["shingles"]:
                    continue
                for r in rules:
                    shared = blk["shingles"] & r["all_shingles"]
                    overlap_ratio = len(shared) / max(1, len(blk["shingles"]))
                    if len(shared) >= 10 or overlap_ratio >= 0.25:
                        rule_delegates_to_skill = s_name in r["text"]
                        blk_cli_flags = set(re.findall(r"--[a-z0-9-]+", blk["text"]))
                        rule_cli_flags = set(re.findall(r"--[a-z0-9-]+", r["text"]))
                        unique_cli_flags = sorted(blk_cli_flags - rule_cli_flags)

                        blk_diag_codes = set(re.findall(r"\b[A-Z][A-Z0-9_]{5,}\b", blk["text"])) - {"README", "SKILL", "COMMIT", "PYTHON"}
                        rule_diag_codes = set(re.findall(r"\b[A-Z][A-Z0-9_]{5,}\b", r["text"]))
                        unique_diag_codes = sorted(blk_diag_codes - rule_diag_codes)

                        has_domain_binding = bool(
                            re.search(
                                r"Mode\s+[AB][12]?|Hardware\.md|Fasteners_and_Inserts|audit_repo_docs|format_image|render_diagram|"
                                r"Anchored Evidence|Tier [123]|4\+1|narrative flow|slicer values",
                                blk["text"],
                            )
                        )
                        if rule_delegates_to_skill:
                            advisory_tag = "[KEEP IN SKILL / CHECK ALWAYS-ON RULE FOOTPRINT]"
                            rationale_suffix = (
                                f"Always-on rule `{r['name']}` explicitly references `{s_name}` (`{s_name}` is the canonical runbook). "
                                f"Keep full detail in `{s_name}` and ensure `{r['name']}` only carries the Turn-1 trigger + load-bearing safety overrides."
                            )
                        elif unique_cli_flags or unique_diag_codes:
                            advisory_tag = "[KEEP — OPERATIONAL CLI / FLAG ANCHOR]"
                            preserved_items = ", ".join(unique_cli_flags + unique_diag_codes[:4])
                            rationale_suffix = (
                                f"Contains operational CLI flags/diagnostic tokens (`{preserved_items}`) absent from `{r['name']}`. "
                                "Trimming to a rule pointer destroys CLI invocation flags and causes `Blind` subagent regressions."
                            )
                        elif has_domain_binding:
                            advisory_tag = "[KEEP — ACTION-SITE DOMAIN INSTANTIATION]"
                            rationale_suffix = (
                                "Translates abstract rule into concrete domain/negative constraints at the point of action "
                                "(prevents `Blind-Light` qualitative dodging on fastener counts/modifiers)."
                            )
                        else:
                            advisory_tag = "[SUGGESTED TRIM — ALREADY IN CORE RULES]"
                            rationale_suffix = "Purely generic rule repetition with zero unique CLI flags or domain instantiations; safe to condense into a 1-line rule pointer."

                        core_rule_overlaps.append({
                            "category": advisory_tag,
                            "skill": s_name,
                            "location": f"{s_path}#L{blk['start_line']}-L{blk['end_line']}",
                            "overlaps_rule": r["name"],
                            "shared_3grams": len(shared),
                            "block_words": blk["words"],
                            "rationale": f"Shares {len(shared)} 3-gram phrases ({blk['words']} words) with always-on rule `{r['name']}`. {rationale_suffix}",
                        })

        # 5. Backbone Synergy Wiring Summary
        synergy = {
            "memory_dossier_or_tree": bool(re.search(r"Projects/<Project>|AUTO-TREE|sync_memory|project-memory|memory_root", s_text)),
            "claim_verification": bool(re.search(r"verify_claims\.py|claim-verification", s_text)),
            "sandbox_gate": bool(re.search(r"sandbox_runner\.py|engineering-sandbox|SANDBOX-PENDING", s_text)),
            "pre_commit_gate": bool(re.search(r"pre-commit-gate", s_text)),
        }
        skill_summaries.append({
            "skill": s_name,
            "tier": s["tier"],
            "path": str(s_path),
            "lines": s["lines"],
            "words": s["words"],
            "est_tokens": s["est_tokens"],
            "ref_files_count": s["ref_files_count"],
            "ref_words": ref_words if (ref_words := s["ref_words"]) else 0,
            "scripts_count": len(s["disk_scripts"]),
            "synergy_hooks": synergy,
        })

    # 6. Check top-level root/scripts/*.py and tests/*.py for functional naming, AST syntax, zero-pip stdlib, and references
    extra_root_texts: list[str] = []
    for root_doc in sorted(set(root.glob("*.md")) | set(root.glob("docs/*.md")) | set(root.glob("tests/*.py"))):
        if root_doc.is_file():
            try:
                extra_root_texts.append(root_doc.read_text(encoding="utf-8"))
            except Exception:
                pass
    tests_dir = root / "tests"
    if tests_dir.is_dir():
        for test_py in sorted(tests_dir.glob("*.py")):
            load_bearing_defects.extend(audit_script_stdlib_compliance(test_py, local_py_modules))
    all_corpus_text = "\n".join([r["text"] for r in rules] + [s["text"] for s in all_skills] + extra_root_texts)
    root_scripts_dir = root / "scripts"
    if root_scripts_dir.is_dir():
        for py_script in sorted(root_scripts_dir.glob("*.py")):
            load_bearing_defects.extend(audit_script_stdlib_compliance(py_script, local_py_modules))
            if py_script.resolve() not in all_referenced_scripts and py_script.name not in all_corpus_text:
                orphan_candidates.append({
                    "category": "[ORPHAN CANDIDATE — CONFIRM EXTERNAL USAGE]",
                    "location": str(py_script),
                    "summary": f"Top-level script `{py_script.name}` in `scripts/` is not referenced in any rule or skill.",
                })

    # 7. Cross-Skill Block & Trigger Overlap (coalesced per source block to prevent 1-to-N noise)
    raw_cross_pairs: list[dict[str, Any]] = []
    for i in range(len(all_skills)):
        for j in range(i + 1, len(all_skills)):
            sa = all_skills[i]
            sb = all_skills[j]
            if "skill-architect" in (sa["name"], sb["name"]):
                continue
            if target_skill and sa["name"] != target_skill and sb["name"] != target_skill:
                continue

            for ba in sa["blocks"]:
                if ba["words"] < 40 or not ba["shingles"]:
                    continue
                best_match: dict[str, Any] | None = None
                for bb in sb["blocks"]:
                    if bb["words"] < 40 or not bb["shingles"]:
                        continue
                    shared_shingles = ba["shingles"] & bb["shingles"]
                    shared_tokens = ba["tokens"] & bb["tokens"]
                    token_jaccard = len(shared_tokens) / max(1, len(ba["tokens"] | bb["tokens"]))
                    if len(shared_shingles) >= 8 or (len(shared_shingles) >= 5 and token_jaccard >= 0.28):
                        smaller_words = min(ba["words"], bb["words"])
                        inline_est_tokens = int(round(smaller_words * 1.35))
                        companion_skill = sb if ba["words"] <= bb["words"] else sa
                        companion_full_tokens = companion_skill["est_tokens"]
                        net_pointer_hop_delta = companion_full_tokens - inline_est_tokens

                        if smaller_words <= 140 and companion_full_tokens >= 3 * inline_est_tokens:
                            cross_category = "[KEEP INLINE — PREVENTS POINTER-HOP TOKEN INVERSION]"
                            cross_rationale = (
                                f"`{sa['name']}` ({ba['words']}w) and `{sb['name']}` ({bb['words']}w) share "
                                f"{len(shared_shingles)} 3-gram phrases ({round(token_jaccard * 100, 1)}% vocab overlap). "
                                f"However, the inline excerpt is only ~{inline_est_tokens} tokens while `{companion_skill['name']}/SKILL.md` "
                                f"is ~{companion_full_tokens} tokens: replacing the inline excerpt with a `#Heading` pointer forces "
                                f"an extra `read_file` tool call (+1 turn) and loads +{net_pointer_hop_delta} net tokens into the KV-cache."
                            )
                        else:
                            cross_category = "[CANDIDATE MERGE / POINTER]"
                            cross_rationale = (
                                f"`{sa['name']}` ({ba['words']}w) and `{sb['name']}` ({bb['words']}w) share "
                                f"{len(shared_shingles)} 3-gram phrases ({round(token_jaccard * 100, 1)}% vocabulary overlap). "
                                "Keep full block in the canonical owner skill and replace the duplicate in the companion skill "
                                "with a `#Heading` pointer (after verifying cold-start subagent impact)."
                            )

                        candidate = {
                            "category": cross_category,
                            "skill_a": sa["name"],
                            "location_a": f"{sa['path']}#L{ba['start_line']}-L{ba['end_line']}",
                            "skill_b": sb["name"],
                            "location_b": f"{sb['path']}#L{bb['start_line']}-L{bb['end_line']}",
                            "shared_3grams": len(shared_shingles),
                            "token_jaccard_pct": round(token_jaccard * 100, 1),
                            "words_a": ba["words"],
                            "words_b": bb["words"],
                            "rationale": cross_rationale,
                        }
                        if best_match is None or candidate["shared_3grams"] > best_match["shared_3grams"]:
                            best_match = candidate
                if best_match is not None:
                    raw_cross_pairs.append(best_match)
    cross_skill_overlaps.extend(raw_cross_pairs)

    core_engine_modified_files: list[str] = []
    unpreflighted_core_scripts: list[str] = []
    try:
        git_proc = subprocess.run(
            ["git", "-C", str(root), "status", "--porcelain", "--", "rules", "skills", "addons", "scripts"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if git_proc.returncode == 0 and git_proc.stdout.strip():
            for ln in git_proc.stdout.splitlines():
                if len(ln) > 3:
                    core_engine_modified_files.append(ln[3:].strip())
    except Exception:
        pass

    if core_engine_modified_files:
        import datetime as _dt
        import hashlib as _hl

        today_s = _dt.date.today().isoformat()
        pf_receipts: dict[str, Any] = {}
        cand_pf_files = [
            root / ".cache" / "preflight_state.json",
            homunculus_paths._resolve_tree_stamp_cache_dir() / "preflight_state.json",
        ]
        auto_mem = homunculus_paths._resolve_memory_root_fast()
        if auto_mem is not None:
            cand_pf_files.append(auto_mem / ".cache" / "preflight_state.json")
        for pf_file in cand_pf_files:
            if pf_file.is_file():
                try:
                    pf_data = json.loads(pf_file.read_text(encoding="utf-8"))
                    pf_receipts.update(pf_data.get("receipts", {}))
                except Exception:
                    pass

        for mod_rel in core_engine_modified_files:
            if not mod_rel.endswith(".py"):
                continue
            mod_rel_clean = mod_rel.removeprefix("Homunculus/")
            mod_abs = root / mod_rel_clean if (root / mod_rel_clean).is_file() else root / mod_rel
            if not mod_abs.is_file():
                continue
            bname = os.path.basename(mod_rel_clean)
            rec = pf_receipts.get(mod_rel_clean) or pf_receipts.get(mod_rel) or pf_receipts.get(bname)
            if not rec or rec.get("session_date") != today_s:
                unpreflighted_core_scripts.append(mod_rel)
                continue
            # Verify blob SHA matches either current file or git HEAD pre-edit blob
            live_sha = _hl.sha256(mod_abs.read_bytes()).hexdigest()[:16]
            head_sha = live_sha
            try:
                h_proc = subprocess.run(
                    ["git", "-C", str(root), "show", f"HEAD:{mod_rel}"],
                    capture_output=True,
                    timeout=2.0,
                    check=False,
                )
                if h_proc.returncode == 0 and h_proc.stdout:
                    head_sha = _hl.sha256(h_proc.stdout).hexdigest()[:16]
            except Exception:
                pass
            rec_pre = rec.get("pre_edit_blob_sha256", "")
            rec_head = rec.get("git_head_blob_sha256", "")
            if rec_pre not in (live_sha, head_sha) and rec_head != head_sha:
                unpreflighted_core_scripts.append(mod_rel)

    return {
        "root": str(root),
        "rules_scanned": len(rules),
        "total_rule_words": sum(r["words"] for r in rules),
        "total_rule_est_tokens": sum(r["est_tokens"] for r in rules),
        "skills_scanned": len(skills),
        "total_skill_words": sum(s["words"] for s in skills),
        "total_est_tokens": sum(s["est_tokens"] for s in skills),
        "total_ref_words": sum(s["ref_words"] for s in skills),
        "load_bearing_defects": load_bearing_defects,
        "turn_waste_hazards": turn_waste_hazards,
        "rule_to_rule_overlaps": rule_to_rule_overlaps,
        "core_rule_overlaps": core_rule_overlaps,
        "cross_skill_overlaps": cross_skill_overlaps,
        "orphan_candidates": orphan_candidates,
        "core_engine_modified_files": core_engine_modified_files,
        "unpreflighted_core_scripts": unpreflighted_core_scripts,
        "rule_summaries": rule_summaries,
        "skill_summaries": skill_summaries,
    }


def run_check_new(root: Path, rules_dir: Path, skills_dir: Path, query: str) -> dict[str, Any]:
    """
    Execute Mode 1 pre-creation overlap and backbone synergy check for a proposed skill/rule.
    Evaluates overlap against always-on `rules/`, on-demand `skills/`, and dormant `addons/`.
    """
    rules = load_rules(root, rules_dir)
    addons_dir = root / "addons"
    skills = load_skills(root, skills_dir, tier_label="skill") + load_skills(root, addons_dir, tier_label="addon")
    intent_text = query.split(":", 1)[1].strip() if ":" in query else query
    q_stems = {stem_token(t) for t in tokenize_words(intent_text, expand_compounds=True)}

    rule_matches: list[dict[str, Any]] = []
    for r in rules:
        desc_stems = {
            stem_token(t)
            for t in tokenize_words(r["frontmatter"].get("description", "") + " " + r["name"], expand_compounds=True)
        }
        body_stems = {stem_token(t) for t in tokenize_words(r["text"], expand_compounds=True)}
        shared_desc = sorted(q_stems & desc_stems)
        shared_body = sorted(q_stems & body_stems)
        desc_score = len(shared_desc) / max(1, len(q_stems))
        body_score = len(shared_body) / max(1, len(q_stems))
        combined = round((0.35 * desc_score + 0.65 * body_score) * 100, 1)
        if combined >= 20.0 or body_score >= 0.40:
            rule_matches.append({
                "rule": r["name"],
                "path": str(r["path"]),
                "overlap_score_pct": combined,
                "body_coverage_pct": round(body_score * 100, 1),
                "shared_body_stems": shared_body[:12],
            })
    rule_matches.sort(key=lambda x: x["body_coverage_pct"], reverse=True)

    matches: list[dict[str, Any]] = []
    for s in skills:
        desc_stems = {
            stem_token(t)
            for t in tokenize_words(s["frontmatter"].get("description", "") + " " + s["name"], expand_compounds=True)
        }
        full_text = s["text"] + "\n" + "\n".join(rf["text"] for rf in s["ref_files"])
        body_stems = {stem_token(t) for t in tokenize_words(full_text, expand_compounds=True)}
        shared_desc = sorted(q_stems & desc_stems)
        shared_body = sorted(q_stems & body_stems)
        desc_score = len(shared_desc) / max(1, len(q_stems))
        body_score = len(shared_body) / max(1, len(q_stems))
        combined = round((0.45 * desc_score + 0.55 * body_score) * 100, 1)
        if combined >= 20.0 or len(shared_desc) >= 2:
            matches.append({
                "skill": s["name"],
                "tier": s["tier"],
                "path": str(s["path"]),
                "overlap_score_pct": combined,
                "body_coverage_pct": round(body_score * 100, 1),
                "shared_trigger_stems": shared_desc,
                "shared_body_stems": shared_body[:12],
            })

    matches.sort(key=lambda x: x["overlap_score_pct"], reverse=True)
    top_rule_cov = rule_matches[0]["body_coverage_pct"] if rule_matches else 0.0
    top_score = matches[0]["overlap_score_pct"] if matches else 0.0
    top_body = matches[0]["body_coverage_pct"] if matches else 0.0

    # Check multi-module composite coverage across top 2 skills + top rule
    union_stems: set[str] = set()
    composite_owners: list[str] = []
    for m in matches[:2]:
        if m["overlap_score_pct"] >= 30.0 or len(m["shared_trigger_stems"]) >= 2:
            union_stems.update(m["shared_body_stems"])
            union_stems.update(m["shared_trigger_stems"])
            composite_owners.append(m["skill"])
    for rm in rule_matches[:1]:
        if rm["body_coverage_pct"] >= 45.0:
            union_stems.update(rm["shared_body_stems"])
            composite_owners.append(f"rule:{rm['rule']}")
    composite_coverage_pct = round((len(q_stems & union_stems) / max(1, len(q_stems))) * 100, 1)

    if top_rule_cov >= 65.0 and top_score < 55.0:
        recommendation = (
            f"ALREADY_IN_CORE_RULE ({rule_matches[0]['rule']}) — "
            "Covered by an always-on global rule; extend the rule or script rather than spawning a redundant skill"
        )
    elif top_score >= 45.0 or top_body >= 65.0:
        recommendation = f"EXTEND_EXISTING ({matches[0]['skill']} [{matches[0]['tier']}])"
        if top_rule_cov >= 60.0:
            recommendation += f" + coordinates with always-on rule ({rule_matches[0]['rule']})"
    elif len(composite_owners) >= 2 and composite_coverage_pct >= 75.0:
        recommendation = (
            f"COMPOSITE_ALREADY_COVERED ({' + '.join(composite_owners)}: {composite_coverage_pct}% union coverage) — "
            "Orchestrate existing skills/rules rather than creating a wrapper skill"
        )
    else:
        recommendation = "CREATE_DELTA_SKILL (with Backbone Synergy & Homunculus Compliance Wiring)"

    return {
        "proposed_query": query,
        "recommendation": recommendation,
        "top_rule_coverage_pct": top_rule_cov,
        "overlapping_rules": rule_matches[:3],
        "top_overlap_score_pct": top_score,
        "composite_coverage_pct": composite_coverage_pct,
        "overlapping_skills": matches[:4],
        "always_on_rules_already_active": [r["name"] for r in rules],
        "mandatory_synergy_checklist": [
            "1. Governing Priority Law: Enforce `1. Accuracy & Truth -> 2. Efficiency -> 3. Data Safety -> 4. Speed`.",
            "2. Portability & Cross-OS Config: Use 100% Python 3.10+ stdlib, resolve `<memory_root>` via `HOMUNCULUS_MEMORY_ROOT` -> `.homunculus.json` -> `./memory`, normalize `\\` to `/`, and catch `(OSError, ValueError)` on Windows cross-drive `relpath`.",
            "3. Optional Add-On Isolation (`skills/` vs `addons/`): Never hardcode dependencies on `addons/<name>/` in core scripts, adapters, or unguarded tests (`unittest.skipUnless`); re-run `build_adapters.py --workspace <ws> --client all` after moving/adding modules.",
            "4. Memory Synergy: Route via `<memory_root>/Projects/<Project>/<Project>.md` (`AUTO-TREE` + live disk check when mutating) and write tasks only to `Tasks/*.md` umbrellas.",
            "5. Verification Synergy: Wire `verify_claims.py` (`VRF-<12hex>`) for any spec/doc/diagram outputs instead of custom prompt warnings.",
            "6. Deferred Side-Effects: Defer `--sync-visuals` and diagram re-renders to `pre-commit-gate` (`X -> Y -> Z`).",
            "7. Delta-Only Authoring: Do NOT repeat generic rules already enforced by `co-engineering-partner.md`, `verifiable-accuracy.md`, or `data-and-credential-safety.md`.",
        ],
    }


def print_human_audit(report: dict[str, Any]) -> None:
    """Format Mode 2 audit report as scannable engineering telemetry."""
    print(f"=== Skill Architect Hygiene & Synergy Audit ({report['root']}) ===")
    print(
        f"Always-On Rules ({report['rules_scanned']}): {report['total_rule_words']}w (~{report['total_rule_est_tokens']} tok/turn) | "
        f"Skills & Add-Ons ({report['skills_scanned']}): {report['total_skill_words']}w (~{report['total_est_tokens']} tok) | "
        f"References: {report['total_ref_words']}w"
    )
    print(
        f"Load-Bearing Defects: {len(report['load_bearing_defects'])} | "
        f"Turn-Waste Hazards: {len(report['turn_waste_hazards'])} | "
        f"Rule-to-Rule Overlaps: {len(report['rule_to_rule_overlaps'])} | "
        f"Core-Rule Overlaps: {len(report['core_rule_overlaps'])} | "
        f"Cross-Skill Overlaps: {len(report['cross_skill_overlaps'])} | "
        f"Orphan Script Candidates: {len(report['orphan_candidates'])}"
    )

    print("\n--- 0. Always-On Global Rules Footprint (Loaded Every Turn — 100% Turn Tax) ---")
    for r in report["rule_summaries"]:
        print(
            f"  - {r['rule']:<26} | {r['lines']:>3}L / {r['words']:>4}w (~{r['est_tokens']:>4} tok/turn) | "
            f"trigger: {r['trigger']} | scripts_ref: {r['scripts_referenced']}"
        )

    print("\n--- 1. On-Demand Skill & Side-Loaded Add-On Footprint & Backbone Synergy Matrix ---")
    for s in report["skill_summaries"]:
        hooks = [k for k, v in s["synergy_hooks"].items() if v]
        hooks_str = ", ".join(hooks) if hooks else "standalone"
        print(
            f"  - {s['skill']:<26} [{s['tier']:<5}] | {s['lines']:>3}L / {s['words']:>4}w (~{s['est_tokens']:>4} tok) | "
            f"refs: {s['ref_files_count']} ({s['ref_words']:>4}w) | scripts: {s['scripts_count']} | synergy: [{hooks_str}]"
        )

    if report["load_bearing_defects"]:
        print("\n--- 2. [LOAD-BEARING DEFECTS] (Fix Required — Accuracy / Portability / Structural Integrity) ---")
        for item in report["load_bearing_defects"]:
            print(f"  [!] {item['code']} @ {item['location']}")
            print(f"      {item['summary']}")

    if report["turn_waste_hazards"]:
        print("\n--- 3. [TURN-WASTE HAZARDS] (High-Value Fix — Deferred Side-Effects / Anti-Bloat) ---")
        for item in report["turn_waste_hazards"]:
            print(f"  [~] {item['code']} @ {item['location']}")
            print(f"      {item['summary']}")

    if report["rule_to_rule_overlaps"]:
        print("\n--- 3B. Rule-to-Rule Overlap Triage (Highest Priority — 100% Turn Tax) ---")
        for item in report["rule_to_rule_overlaps"]:
            print(
                f"  * {item['category']} | {item['rule_a']} <-> {item['rule_b']} "
                f"({item['shared_3grams']} shared 3-grams, {item['token_jaccard_pct']}% vocab)"
            )
            print(f"    Rule A: {item['location_a']}")
            print(f"    Rule B: {item['location_b']}")
            print(f"    Note: {item['rationale']}")

    if report["core_rule_overlaps"]:
        print("\n--- 4. Core-Rule Overlap Triage (Advisory — Permission First) ---")
        for item in report["core_rule_overlaps"]:
            print(f"  * {item['category']} | {item['skill']} <-> {item['overlaps_rule']} ({item['shared_3grams']} shared 3-grams)")
            print(f"    Location: {item['location']}")
            print(f"    Note: {item['rationale']}")

    if report["cross_skill_overlaps"]:
        print("\n--- 5. Cross-Skill Duplication Triage (Advisory — Permission First) ---")
        for item in report["cross_skill_overlaps"]:
            print(
                f"  * {item['category']} | {item['skill_a']} <-> {item['skill_b']} "
                f"({item['shared_3grams']} shared 3-grams, {item['token_jaccard_pct']}% vocab overlap)"
            )
            print(f"    Skill A: {item['location_a']}")
            print(f"    Skill B: {item['location_b']}")
            print(f"    Note: {item['rationale']}")

    if report.get("core_engine_modified_files"):
        mod_list = ", ".join(report["core_engine_modified_files"][:6])
        more_cnt = max(0, len(report["core_engine_modified_files"]) - 6)
        suffix = f" (+{more_cnt} more)" if more_cnt else ""
        print(
            f"\n[CORE_ENGINE_MODIFIED_WARNING] {len(report['core_engine_modified_files'])} core file(s) modified "
            f"({mod_list}{suffix}) — verify Pre-Mutation Change Advisory Gate (Chesterton's Fence + Options/Repercussions) "
            "and <Project>_Lessons_Learned.md (Subsystem Rebuild & Invariant Matrix + LL entry) were reviewed/updated."
        )
    if report.get("unpreflighted_core_scripts"):
        for up_script in report["unpreflighted_core_scripts"]:
            print(
                f"  [!] [UNPREFLIGHTED_CORE_SCRIPT_EDIT] `{up_script}` modified without a preflight receipt in `.cache/preflight_state.json`. "
                f"Run `python3 scripts/homunculus_paths.py --map {os.path.basename(up_script)}` or `sync_memory.py --preflight {os.path.basename(up_script)}`."
            )

    if report["orphan_candidates"]:
        print("\n--- 6. Orphan Script Candidates (Confirm External Usage Before Touching) ---")
        for item in report["orphan_candidates"]:
            print(f"  [?] {item['location']}: {item['summary']}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Deterministic Skill, Rule & Add-On Hygiene and Synergy Auditor")
    parser.add_argument("--audit", action="store_true", help="Run Mode 2 non-destructive hygiene audit (default)")
    parser.add_argument("--check-new", type=str, default=None, help="Run Mode 1 pre-creation overlap check for a proposed skill")
    parser.add_argument("--target-skill", type=str, default=None, help="Filter audit to a single skill or add-on name")
    parser.add_argument(
        "--root",
        "--repo",
        "--repo-root",
        dest="root",
        type=str,
        default=None,
        help="Override Homunculus framework root directory",
    )
    parser.add_argument("--strict-structure", action="store_true", help="Exit 1 if any load-bearing structural/link/portability/accuracy defect is found")
    parser.add_argument("--json", action="store_true", help="Emit JSON output")
    args = parser.parse_args(argv)

    root = Path(args.root).resolve() if args.root else resolve_default_root()
    rules_dir = root / "rules"
    skills_dir = root / "skills"

    if args.check_new:
        res = run_check_new(root, rules_dir, skills_dir, args.check_new)
        if args.json:
            print(json.dumps(res, indent=2))
        else:
            print("=== Skill Architect Pre-Creation Check ===")
            print(f"Query: {res['proposed_query']}")
            print(
                f"Recommendation: {res['recommendation']} "
                f"(Top Rule Coverage: {res['top_rule_coverage_pct']}% | Top Skill Score: {res['top_overlap_score_pct']}%)"
            )
            if res["overlapping_rules"]:
                print("\nOverlapping Always-On Global Rules (100% Turn Tax — Check First):")
                for rm in res["overlapping_rules"]:
                    print(
                        f"  - {rm['rule']} (body_coverage={rm['body_coverage_pct']}%, combined={rm['overlap_score_pct']}%): "
                        f"shared_stems={rm['shared_body_stems']}"
                    )
            if res["overlapping_skills"]:
                print("\nOverlapping On-Demand Skills / Side-Loaded Add-Ons:")
                for m in res["overlapping_skills"]:
                    print(
                        f"  - {m['skill']} [{m['tier']}] (combined={m['overlap_score_pct']}%, body_coverage={m['body_coverage_pct']}%): "
                        f"shared_triggers={m['shared_trigger_stems']}"
                    )
            print("\nMandatory Backbone Synergy Checklist:")
            for line in res["mandatory_synergy_checklist"]:
                print(f"  {line}")
        return 0

    report = run_audit(root, rules_dir, skills_dir, target_skill=args.target_skill)
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print_human_audit(report)

    if args.strict_structure and (report["load_bearing_defects"] or report["turn_waste_hazards"]):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
