#!/usr/bin/env python3
"""
Homunculus Universal Engineering & Technical Learning Engine (teach_brief.py).

Governed by: 1. Accuracy & Truth -> 2. Efficiency -> 3. Data Safety -> 4. Speed
Requires ONLY Python 3.10+ standard library (zero third-party pip packages).

Manages the lifecycle of multi-domain `Brief+` engineering study briefs
(mechanical/CAD, electrical/PCBs/motors/drivers, firmware/MCUs/Klipper,
structured cabling/RF, and software systems) inside the non-consumed
`<study_briefs_root>/` directory adjacent to `<memory_root>/`:
  1. --init-brief : Scaffold a context-tailored `Brief+` Markdown file in
                    `<study_briefs_root>/<project_or_general>/`.
  2. --verify     : Enforce `Brief+` structural invariants (ensuring Section 3
                    Active Context Overlaps is never hidden inside a theory zone),
                    run `verify_claims.py` against authoritative `--sources`,
                    and stamp the cryptographic `VRF-<12hex>` receipt.
  3. --list       : List study briefs in `<study_briefs_root>/` and their
                    verification/promotion status.
  4. --promote    : Promote a verified (`0` unbacked claims, `0` open `[TBD]`s)
                    brief into `<memory_root>/Standards_and_Specs/` or
                    `<memory_root>/Projects/<Project>/`.

=== DEVELOPER & AI NAVIGATION MAP ===
  Owning Module : `teach-me` (`skills/teach-me/SKILL.md`)
  Callers       : Throw-away `teach-me` subagents, `test_teach_me.py`, `test_core_skills.py`
  Callees       : `homunculus_paths.py` (`resolve_workspace_config`, `ensure_directory_fresh`), `verify_claims.py` (`--json` subprocess)
  Contract      : `scripts/script_contracts.json` [`teach_brief.py`]
  CLI Flags     : --workspace, --memory-root, --briefs-root, --init-brief, --subject, --impact-on, --slug, --domain, --project, --entity, --out, --rename-clean, --verify, --auto-slug, --require-depth, --model-tier, --classify-complexity, --sources, --fail-on-tbd, --strict-provenance, --list, --promote, --target, --json
  Symbol Index  (jump directly via read_file StartLine/EndLine):
    - def _norm_slash_path (#L59-L85)                | def _enforce_anti_snoop_gate (#L93-L138)
    - def _strip_parentheticals (#L223-L227)         | def _normalize_engineering_symbols (#L230-L239)
    - def _tokenize_for_slug (#L242-L262)            | def _dedupe_project_tokens (#L265-L282)
    - def _pack_tokens (#L285-L313)                  | def build_brief_slug (#L316-L352)
    - def build_concise_phrase (#L355-L375)          | def format_brief_display_name (#L378-L388)
    - def format_model_tier_badge (#L413-L424)       | def classify_query_complexity (#L427-L490)
    - def build_chat_rails (#L493-L524)              | def build_chat_card_template (#L527-L555)
    - def resolve_roots (#L558-L581)                 | def ensure_briefs_root_readme (#L584-L588)
    - def _extract_frontmatter_meta (#L591-L594)     | def init_brief (#L597-L698)
    - def verify_brief_structure (#L701-L819)        | def verify_and_stamp_brief (#L822-L997)
    - def rename_brief_clean (#L1000-L1030)          | def list_briefs (#L1033-L1059)
    - def promote_brief (#L1062-L1152)               | def main (#L1155-L1420)
=== END NAVIGATION MAP ===
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
from typing import Any

def _norm_slash_path(p: str, resolve_links: bool = False) -> str:
    s = p.replace("\\", "/")
    if not s.startswith("/") and not (len(s) > 2 and s[1:3] == ":/"):
        s = os.getcwd().replace("\\", "/").rstrip("/") + "/" + s
    parts: list[str] = []
    for seg in s.split("/"):
        if seg in ("", "."):
            continue
        if seg == "..":
            if parts:
                parts.pop()
            continue
        parts.append(seg)
        if resolve_links:
            cur = ("/" if s.startswith("/") else "") + "/".join(parts)
            for _ in range(16):
                try:
                    target = os.readlink(cur).replace("\\", "/")
                except OSError:
                    break
                if target.startswith("/") or (len(target) > 2 and target[1:3] == ":/"):
                    cur = _norm_slash_path(target, resolve_links=False)
                else:
                    parent = ("/" + "/".join(parts[:-1])) if len(parts) > 1 else "/"
                    cur = _norm_slash_path(parent.rstrip("/") + "/" + target, resolve_links=False)
                parts = [x for x in cur.split("/") if x]
    return ("/" if s.startswith("/") else "") + "/".join(parts)


_RAW_FILE = globals().get("__file__", "")
SCRIPT_DIR = Path(_norm_slash_path(_RAW_FILE, resolve_links=True)).parent if _RAW_FILE else Path(".")
HOMUNCULUS_ROOT = SCRIPT_DIR.parent.parent.parent if _RAW_FILE else Path(".")


def _enforce_anti_snoop_gate(script_basename: str, hom_root: str) -> None:
    orig_argv = getattr(sys, "orig_argv", [])
    if any(a in ("-c", "-") for a in orig_argv[1:4]):
        raise SystemExit(
            f"[ANTI-SNOOP GATE — BLOCKED] Executing or importing {script_basename} via `python3 -c` / stdin "
            f"is prohibited. Run `{script_basename}` directly via CLI."
        )
    argv0_base = (sys.argv[0] if sys.argv else "").replace("\\", "/").split("/")[-1]
    if not _RAW_FILE or (__name__ == "__main__" and argv0_base != script_basename):
        raise SystemExit(
            f"[ANTI-SNOOP GATE — BLOCKED] Executing {script_basename} via exec()/runpy inside {argv0_base!r} "
            f"is prohibited. Run `{script_basename}` directly via CLI."
        )
    if __name__ == "__main__":
        return
    hom_prefix = _norm_slash_path(hom_root).rstrip("/") + "/"
    stdlib_dir = _norm_slash_path(os.path.dirname(os.__file__)).rstrip("/") + "/"
    depth = 1
    found_hom_caller = False
    bad_frame = ""
    while True:
        try:
            f = sys._getframe(depth)
        except ValueError:
            break
        fn = f.f_code.co_filename.replace("\\", "/")
        depth += 1
        if "importlib" in fn or fn.startswith("<frozen") or fn.endswith("/" + script_basename):
            continue
        if fn.startswith("<"):
            bad_frame = fn
            break
        abs_fn = _norm_slash_path(fn)
        if abs_fn.startswith(hom_prefix):
            found_hom_caller = True
        elif abs_fn.startswith(stdlib_dir):
            continue
        else:
            bad_frame = fn
            break
    if bad_frame or not found_hom_caller:
        raise SystemExit(
            f"[ANTI-SNOOP GATE — BLOCKED] Importing {script_basename} from ad-hoc/external scripts "
            f"(caller={bad_frame or argv0_base!r}) to inspect source/regexes is prohibited. "
            f"Run `{script_basename}` via CLI."
        )


_enforce_anti_snoop_gate("teach_brief.py", str(HOMUNCULUS_ROOT))
for _p in (str(SCRIPT_DIR), str(HOMUNCULUS_ROOT / "scripts")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import homunculus_paths  # noqa: E402

VALID_DOMAINS = ("mechanical", "electrical", "firmware", "cabling", "software", "hybrid")
VALID_PROMOTE_TARGETS = ("standards", "project_doc", "lessons_learned")

REQUIRED_SECTIONS = (
    "## 1. Core Mental Model",
    "## 2. Relational Impact Vector",
    "## 3. Active Engineering Context Overlaps",
    "## 4. Actionable Engineering Guardrails",
)

STUDY_BRIEFS_README = """# 🧭 Homunculus Study Briefs (`Non-Consumed Learning Quarantine`)

> [!IMPORTANT]
> **Three-Layer Anti-Consumption Firewall (`1. Accuracy & Truth -> 2. Efficiency -> 3. Data Safety -> 4. Speed`)**
> Files inside `study_briefs/` are **unpromoted on-the-fly engineering learning briefs (`Brief+`)** generated by `skills/teach-me/`:
> 1. **Excluded from Automatic Memory Sync**: `sync_memory.py` never scans or indexes `study_briefs/`.
> 2. **Excluded from Background IDE Context**: Listed in `.cursorignore`, `.claudeignore`, and `.geminiignore` so active coding/engineering windows stay clean.
> 3. **Excluded from Truth-Oracle Source Whitelists**: `verify_claims.py` rejects `study_briefs/` files as `--sources` (`STUDY_BRIEF_SOURCE_REJECTED`) until explicitly promoted into `memory/` via `teach_brief.py --promote`.
"""


SLUG_STOPWORDS = frozenset(
    {
        "a",
        "an",
        "the",
        "about",
        "how",
        "what",
        "why",
        "when",
        "where",
        "this",
        "that",
        "these",
        "those",
        "is",
        "are",
        "was",
        "were",
        "be",
        "being",
        "been",
        "do",
        "does",
        "did",
        "of",
        "for",
        "in",
        "into",
        "on",
        "onto",
        "to",
        "with",
        "by",
        "from",
        "at",
        "as",
        "and",
        "or",
        "vs",
        "versus",
        "via",
        "its",
        "their",
        "our",
        "your",
        "my",
        "impact",
        "impacts",
        "impacting",
    }
)


def _strip_parentheticals(text: str) -> str:
    """Remove (...) and [...] asides unless stripping leaves the phrase empty."""
    stripped = re.sub(r"\([^)]*\)|\[[^\]]*\]", " ", text)
    stripped = re.sub(r"\s+", " ", stripped).strip(" -—–:;,/")
    return stripped if stripped else text.strip()


def _normalize_engineering_symbols(text: str) -> str:
    out = (
        text.replace("Ω", "Ohm")
        .replace("Ω", "Ohm")
        .replace("μ", "u")
        .replace("µ", "u")
        .replace("Ø", "Dia")
        .replace("ø", "Dia")
    )
    return re.sub(r"(?<=[A-Za-z0-9])\+", "Plus", out)


def _tokenize_for_slug(text: str, keep_stopwords: bool = False) -> list[str]:
    """Extract clean engineering tokens while preserving internal hyphens (e.g., teach-me, DC-DC)."""
    base = _normalize_engineering_symbols(_strip_parentheticals(text))
    raw_tokens = re.findall(r"[A-Za-z0-9]+(?:-[A-Za-z0-9]+)*", base)
    if not raw_tokens:
        raw_tokens = re.findall(
            r"[A-Za-z0-9]+(?:-[A-Za-z0-9]+)*",
            _normalize_engineering_symbols(text),
        )
    if keep_stopwords:
        return raw_tokens

    filtered = [
        tok
        for tok in raw_tokens
        if (len(tok) >= 2 and tok.isupper())
        or any(ch.isdigit() for ch in tok)
        or "-" in tok
        or tok.lower() not in SLUG_STOPWORDS
    ]
    return filtered if filtered else raw_tokens


def _dedupe_project_tokens(tokens: list[str], project: str) -> list[str]:
    """Drop redundant contiguous project-name tokens when file already sits under <project>/."""
    if not project or project.strip().lower() == "general" or not tokens:
        return tokens
    proj_toks = [t.lower() for t in re.findall(r"[A-Za-z0-9]+(?:-[A-Za-z0-9]+)*", project)]
    if not proj_toks:
        return tokens
    plen = len(proj_toks)
    out: list[str] = []
    idx = 0
    while idx < len(tokens):
        window = [t.lower() for t in tokens[idx : idx + plen]]
        if window == proj_toks:
            idx += plen
        else:
            out.append(tokens[idx])
            idx += 1
    return out if out else tokens


def _pack_tokens(tokens: list[str], max_chars: int) -> str:
    """Pack tokens joined by '_' strictly on whole-word boundaries (zero mid-word slicing)."""
    if not tokens:
        return ""
    packed: list[str] = []
    cur_len = 0
    for tok in tokens:
        sep = 1 if packed else 0
        if cur_len + sep + len(tok) <= max_chars:
            packed.append(tok)
            cur_len += sep + len(tok)
        elif not packed:
            # Even if a single hyphenated token exceeds max_chars, snap at hyphen parts rather than mid-word
            if "-" in tok:
                sub_parts: list[str] = []
                sub_len = 0
                for sp in tok.split("-"):
                    s_sep = 1 if sub_parts else 0
                    if sp and sub_len + s_sep + len(sp) <= max_chars:
                        sub_parts.append(sp)
                        sub_len += s_sep + len(sp)
                if sub_parts:
                    packed.append("-".join(sub_parts))
                    break
            packed.append(tok)
            break
        else:
            break
    return "_".join(packed)


def build_brief_slug(
    subject: str,
    impact_on: str = "",
    project: str = "General",
    slug_override: str = "",
    max_total_chars: int = 54,
) -> str:
    """Build a concise, whole-word-snapped engineering filename slug (`<Subject>_on_<Impact>`)."""
    if slug_override.strip():
        override_toks = _tokenize_for_slug(slug_override, keep_stopwords=True)
        packed_override = _pack_tokens(override_toks, max_total_chars)
        return packed_override if packed_override else "Engineering_Brief"

    sub_toks = _tokenize_for_slug(subject)
    if not impact_on.strip():
        packed_only = _pack_tokens(sub_toks, max_total_chars)
        return packed_only if packed_only else "Engineering_Brief"

    imp_toks = _dedupe_project_tokens(_tokenize_for_slug(impact_on), project)
    sub_toks_dedup = _dedupe_project_tokens(sub_toks, project)

    connector = "_on_"
    avail = max(24, max_total_chars - len(connector))
    base_sub = 28
    base_imp = max(16, avail - base_sub)

    full_imp_len = len("_".join(imp_toks))
    sub_budget = max(base_sub, avail - min(base_imp, full_imp_len))
    packed_sub = _pack_tokens(sub_toks_dedup, sub_budget)
    if not packed_sub:
        packed_sub = "Subject"

    imp_budget = max(12, avail - len(packed_sub))
    packed_imp = _pack_tokens(imp_toks, imp_budget)
    if not packed_imp:
        return packed_sub
    return f"{packed_sub}{connector}{packed_imp}"


def build_concise_phrase(text: str, max_chars: int = 44) -> str:
    """Shorten verbose subjects/impacts on whole-word boundaries for readable headings/table columns."""
    clean = _strip_parentheticals(text)
    if len(clean) <= max_chars:
        return clean
    words = clean.split()
    acc: list[str] = []
    cur = 0
    for w in words:
        w_clean = w.rstrip(",;:")
        if not w_clean:
            continue
        if acc and w_clean.lower() in {"and", "or", "with", "for", "across", "including"} and cur >= 18:
            break
        sep = 1 if acc else 0
        if cur + sep + len(w_clean) <= max_chars:
            acc.append(w_clean)
            cur += sep + len(w_clean)
        else:
            break
    return " ".join(acc) if acc else words[0]


def format_brief_display_name(brief_path: Path, briefs_root: Path | None = None) -> str:
    """Return a clean `<Project>/<filename.md>` label for clickable chat links."""
    resolved = brief_path.expanduser().resolve()
    if briefs_root is not None:
        try:
            return resolved.relative_to(briefs_root.expanduser().resolve()).as_posix()
        except ValueError:
            pass
    if resolved.parent.name and resolved.parent.name != "study_briefs":
        return f"{resolved.parent.name}/{resolved.name}"
    return resolved.name


DEEP_COMPLEXITY_KEYWORD_RE = re.compile(
    r"\b(?:torque|inductance|resonance|shaper|buckling|pressure|flow|current|voltage|power|"
    r"thermal|dissipation|impedance|pid|kinematics|deflection|stress|strain|preload|backlash|"
    r"frequency|attenuation|derivation|derive|calculate|equation|formula|euler|capstan|"
    r"reynolds|bernoulli|ohm|kirchhoff|acceleration|deceleration|jerk|stiffness|compliance|"
    r"viscosity|shear|bending|moment|toleranc(?:e|es)|clearance|interference|"
    r"pneumatic|vacuum|hardness|durometer|damping|solenoid|elastomer|modulus)\b|\[calc:",
    re.IGNORECASE,
)

DEEP_TRADE_OFF_RE = re.compile(
    r"\b(?:vs\.?|versus|trade-?offs?|conflicts?|failure\s+modes?|root\s+causes?|"
    r"why\s+does|compare|comparison|interaction|coupling|coupled|bottlenecks?)\b",
    re.IGNORECASE,
)

DEEP_TELEMETRY_SOURCE_RE = re.compile(
    r"(?:_(?:hardware|software)\.md$|(?:^|/)bom\.md$|\.(?:step|stp|stl|cfg|py|rs|c|cpp|h|hpp)$)",
    re.IGNORECASE,
)


def format_model_tier_badge(model_tier: str = "", default_mode: str = "ISOLATED SUBAGENT") -> str:
    """Map an explicit model tier ('flash'/'sonnet'/'pro'/'opus') to a <=19-char header badge."""
    raw = (model_tier or "").strip().lower().strip("[]'\" ")
    if not raw:
        return (default_mode or "ISOLATED SUBAGENT").strip().upper()
    if raw in ("pro", "opus", "deep", "tier3", "tier_3"):
        return "TIER: PRO // DEEP"
    if raw in ("flash", "sonnet", "fast", "standard", "tier2", "tier_2"):
        return "TIER: FLASH // FAST"
    if raw in ("flash_lite", "flash-lite", "haiku", "lite", "tier1", "tier_1"):
        return "TIER: LITE (BANNED)"
    return raw.upper()


def classify_query_complexity(
    subject: str,
    impact_on: str = "",
    domain: str = "hybrid",
    sources: list[str] | None = None,
    query_text: str = "",
    model_override: str = "",
) -> dict[str, Any]:
    """Deterministically route `/teach-me` queries between Tier 2 (`flash`/`sonnet`) and Tier 3 (`pro`/`opus`).

    Enforces `1. Accuracy & Truth > 2. Efficiency > 3. Data Safety > 4. Speed`:
      - `'flash_lite'` / `'haiku'` is strictly banned for `Brief+` synthesis.
      - Any coupled physics/math (`[CALC]`), CAD/firmware/AST telemetry source, or cross-repo/trade-off
        analysis automatically routes to `'pro'` / `'opus'` (`TIER: PRO // DEEP`).
    """
    combined_text = " ".join(p for p in (subject, impact_on, query_text) if p).strip()
    triggers: list[str] = []
    score = 0

    # Trigger 1: Coupled physics, kinematics, or [CALC] dimensional math
    if DEEP_COMPLEXITY_KEYWORD_RE.search(combined_text):
        score += 2
        triggers.append("TRIGGER_1_COUPLED_PHYSICS_OR_CALC_MATH")
    elif (domain or "").strip().lower() in ("mechanical", "electrical", "firmware", "cabling"):
        score += 1
        triggers.append(f"DOMAIN_HARDWARE_FLOOR({domain.strip().lower()})")

    # Trigger 2: CAD geometry, Klipper/firmware .cfg, or _Hardware.md / _Software.md AST telemetry sources
    src_list = [str(s).strip() for s in (sources or []) if str(s).strip()]
    if any(DEEP_TELEMETRY_SOURCE_RE.search(s.replace("\\", "/")) for s in src_list):
        score += 2
        triggers.append("TRIGGER_2_CAD_FIRMWARE_OR_AST_TELEMETRY")

    # Trigger 3: Cross-repository sources (>= 2 distinct parent dirs) or multi-system trade-off/conflict query
    src_dirs = {str(Path(s.replace("\\", "/")).expanduser().resolve().parent) for s in src_list}
    if len(src_dirs) >= 2:
        score += 2
        triggers.append("TRIGGER_3_CROSS_REPO_SOURCES")
    elif DEEP_TRADE_OFF_RE.search(combined_text) or len(src_list) >= 3:
        score += 1
        triggers.append("TRIGGER_3_TRADE_OFF_OR_MULTI_SOURCE")

    # Trigger 4: Explicit inline tag or --model-tier override (clamped at 'flash'/'sonnet' minimum floor)
    ov_raw = (model_override or "").strip().lower().strip("[]'\" ")
    if re.search(r"\[deep\]", combined_text, re.IGNORECASE) or ov_raw in ("pro", "opus", "deep"):
        score = max(score, 2)
        triggers.append("TRIGGER_4_EXPLICIT_DEEP_OVERRIDE")
    elif ov_raw in ("flash_lite", "flash-lite", "haiku", "lite") or re.search(r"\[lite\]", combined_text, re.IGNORECASE):
        triggers.append("CLAMPED_BANNED_LITE_TO_FLASH_FLOOR")

    is_deep = score >= 2 and ov_raw not in ("flash", "sonnet", "fast", "standard")
    complexity_tier = "deep" if is_deep else "standard"
    ag_model = "pro" if is_deep else "flash"
    cl_model = "opus" if is_deep else "sonnet"
    badge = format_model_tier_badge(ag_model)

    return {
        "complexity_tier": complexity_tier,
        "antigravity_model": ag_model,
        "claude_model": cl_model,
        "rail_badge": badge,
        "score": score,
        "triggers": triggers or ["BASELINE_STANDARD_CONCEPTUAL_FLOOR"],
    }


def build_chat_rails(
    domain: str = "hybrid",
    vrf_token: str = "UNVERIFIED",
    status: str = "UNPROMOTED_STUDY_BRIEF",
    execution_mode: str = "ISOLATED SUBAGENT",
    model_tier: str = "",
    min_width: int = 78,
) -> tuple[str, str]:
    """Build pixel-aligned solid-line top and bottom inline-backtick rails (Option 1 + Option 4)."""
    dom_label = (domain or "hybrid").strip().upper()
    mode_label = format_model_tier_badge(model_tier, default_mode=execution_mode)
    vrf_label = (vrf_token or "UNVERIFIED").strip()
    promoted = status.strip().upper() == "PROMOTED_ENGINEERING_BRIEF"

    top_left = "┏━━ 🎓 TEACH-ME // BRIEF+ "
    top_right = f" [DOMAIN: {dom_label}] ━━ [{mode_label}] ━━┓"

    if promoted:
        bot_left = "┗━━ ✅ PROMOTED: memory/ (CONSUMED BEDROCK) "
    else:
        bot_left = "┗━━ 🔒 QUARANTINED: study_briefs/ (NON-CONSUMED) "
    bot_right = f" [{vrf_label}] ━━┛"

    target_len = max(
        min_width,
        len(top_left) + 3 + len(top_right),
        len(bot_left) + 3 + len(bot_right),
    )
    top_fill = "━" * (target_len - len(top_left) - len(top_right))
    bot_fill = "━" * (target_len - len(bot_left) - len(bot_right))

    return f"`{top_left}{top_fill}{top_right}`", f"`{bot_left}{bot_fill}{bot_right}`"


def build_chat_card_template(
    brief_path: Path,
    briefs_root: Path | None = None,
    domain: str = "hybrid",
    vrf_token: str = "UNVERIFIED",
    status: str = "UNPROMOTED_STUDY_BRIEF",
    execution_mode: str = "ISOLATED SUBAGENT",
    model_tier: str = "",
) -> str:
    """Build the Option 1 (`▸` / `↳` clickable layout) + Option 4 (`┏━━` / `┗━━` solid rails) chat card."""
    resolved = brief_path.expanduser().resolve()
    display_name = format_brief_display_name(resolved, briefs_root)
    uri = resolved.as_uri()
    top_rail, bot_rail = build_chat_rails(
        domain=domain,
        vrf_token=vrf_token,
        status=status,
        execution_mode=execution_mode,
        model_tier=model_tier,
    )
    return (
        f"{top_rail}\n\n"
        "▸ **CONCEPT & IMPACT**: <1–2 concise sentences explaining Subject X and its impact on Subject Y>\n"
        "▸ **CONTEXT OVERLAPS**:\n"
        "  ↳ [<file>:<lines>](file:///abs/path/to/file#L1-L5) — <1-line verified project touchpoint>\n"
        "▸ **GUARDRAIL**: <1-line critical failure boundary or operational check>\n"
        f"▸ **STUDY BRIEF+**: [{display_name}]({uri})\n\n"
        f"{bot_rail}"
    )


def resolve_roots(
    workspace: str | None = None,
    memory_root_arg: str | None = None,
    briefs_root_arg: str | None = None,
) -> tuple[Path, Path]:
    """Resolve (memory_root, study_briefs_root) across Windows, macOS, and Linux."""
    cfg = homunculus_paths.resolve_workspace_config(
        workspace_dir=workspace, homunculus_root=HOMUNCULUS_ROOT
    )
    if memory_root_arg:
        mem_root = Path(memory_root_arg.replace("\\", "/")).expanduser().resolve()
    else:
        mem_root = Path(cfg["memory_root"]).resolve()

    if briefs_root_arg:
        briefs_root = Path(briefs_root_arg.replace("\\", "/")).expanduser().resolve()
    elif os.environ.get("HOMUNCULUS_BRIEFS_ROOT", "").strip():
        briefs_root = Path(os.environ["HOMUNCULUS_BRIEFS_ROOT"].replace("\\", "/")).expanduser().resolve()
    elif memory_root_arg:
        briefs_root = (mem_root.parent / "study_briefs").resolve()
    else:
        briefs_root = Path(cfg.get("study_briefs_root") or (mem_root.parent / "study_briefs")).resolve()

    return mem_root, briefs_root


def ensure_briefs_root_readme(briefs_root: Path) -> None:
    briefs_root.mkdir(parents=True, exist_ok=True)
    readme_p = briefs_root / "README.md"
    if not readme_p.exists():
        readme_p.write_text(STUDY_BRIEFS_README, encoding="utf-8")


def _extract_frontmatter_meta(text: str) -> dict[str, str]:
    """Extract flat string fields from YAML frontmatter via shared stdlib parser."""
    fields, _body, _start = homunculus_paths.parse_frontmatter_full(text)
    return {k.strip().lower(): str(v).strip() for k, v in fields.items()}


def init_brief(
    briefs_root: Path,
    subject: str,
    impact_on: str,
    domain: str = "hybrid",
    project: str = "General",
    entity: str = "Default_Entity",
    slug_override: str = "",
    out_path: Path | None = None,
) -> Path:
    """Scaffold a context-tailored `Brief+` Markdown file inside `<study_briefs_root>`."""
    ensure_briefs_root_readme(briefs_root)
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    proj_folder = re.sub(r"[^A-Za-z0-9_-]+", "_", project.strip() or "General")

    if out_path is not None:
        target_p = out_path.expanduser().resolve()
        target_p.parent.mkdir(parents=True, exist_ok=True)
    else:
        sub_slug = build_brief_slug(
            subject=subject,
            impact_on=impact_on,
            project=project,
            slug_override=slug_override,
        )
        target_dir = briefs_root / proj_folder
        target_dir.mkdir(parents=True, exist_ok=True)
        target_p = target_dir / f"{today}_{sub_slug}.md"

    short_sub = build_concise_phrase(subject, max_chars=48)
    impact_label = impact_on if impact_on else "System Performance & Reliability"
    short_imp = build_concise_phrase(impact_label, max_chars=44)
    title_str = f"{subject} — Impact on {impact_on}" if impact_on else subject
    h1_title = f"{short_sub} → {short_imp}" if impact_on else short_sub

    template = f"""---
title: "{title_str}"
subject: "{subject}"
impact_on: "{impact_label}"
domain: "{domain}"
project: "{project}"
entity: "{entity}"
type: "study-brief"
status: "UNPROMOTED_STUDY_BRIEF"
consumed_by_memory: false
vrf_receipt: "UNVERIFIED"
created_at: "{today}"
---

# 🧠 Engineering Brief+: {h1_title}

> [!NOTE]
> **Non-Consumed Study Brief (status: UNPROMOTED_STUDY_BRIEF)**
> Stored in study_briefs/ adjacent to memory/. This brief is quarantined from automatic memory indexing and truth-oracle source whitelists until explicitly promoted.
> - **Domain**: {domain} | **Project Context**: {project} (entity: {entity})
> - **Verification Receipt**: UNVERIFIED | **Source Hashes**: PENDING

---

<!-- FIRST-PRINCIPLES-THEORY:START -->
## 1. Core Mental Model

- **First-Principles Mechanism**: Explain the physical, electrical, mechanical, firmware, or algorithmic mechanism of **{short_sub}** in 3–5 concise bullets.
- **Governing Scaling / Physics Law**: State the relationship governing how **{short_sub}** behaves (use `[CALC: <lhs> = <rhs_val> <unit>]` for any numerical derivation so dimensional analysis is verified).
- **Key Boundary Condition**: Identify the threshold where linear/nominal behavior breaks down.

## 2. Relational Impact Vector

- **Causal Coupling Chain**: **{short_sub}** $\\rightarrow$ *(Coupling Mechanism)* $\\rightarrow$ **{short_imp}**.
- **Trade-Off & Failure Envelope**:

| Parameter Shift in {short_sub} | Primary Effect on {short_imp} | Secondary Side-Effect / Bottleneck | Failure Mode if Pushed Past Limit |
| :--- | :--- | :--- | :--- |
| **Increase $\\uparrow$** | Describe direct impact | Describe trade-off | Describe physical/system failure |
| **Decrease $\\downarrow$** | Describe direct impact | Describe trade-off | Describe physical/system failure |
<!-- FIRST-PRINCIPLES-THEORY:END -->

---

## 3. Active Engineering Context Overlaps

> [!IMPORTANT]
> **Closed-World Repo Grounding (Outside Theory Zone)**
> Every quantitative specification, fastener, pin, CAD dimension, or line-range citation in this section is strictly audited against --sources by verify_claims.py.

### Overlap Example 1: Direct Touchpoint in {project}
- [VERIFIED FACT] State the exact component, circuit, CAD feature, config parameter, or code module in {project} where **{short_sub}** impacts **{short_imp}** (Source: `path/to/file#L1-L5`).
  Anchor:
  ```text
  Replace with exact 1-3 line verbatim slice from the source file
  ```
- **Engineering Impact in Context**: Explain how changing **{short_sub}** alters this specific component or parameter in {project}.

---

## 4. Actionable Engineering Guardrails

1. **Pre-Change Check**: Verify the governing constraint in the active design before adjusting **{short_sub}**.
2. **Validation Probe**: Specify the measurement, test, or CLI oracle check required to confirm **{short_imp}** remains within safe margins.
"""
    target_p.write_text(template, encoding="utf-8")
    return target_p


def verify_brief_structure(
    text: str,
    brief_path: Path,
    require_depth: bool = False,
    sources: list[str] | None = None,
    model_tier: str = "",
) -> list[str]:
    """Validate `Brief+` structural invariants, synthesis depth, and anti-evasion boundaries."""
    errors: list[str] = []
    fm_meta = _extract_frontmatter_meta(text)
    effective_tier = (model_tier or fm_meta.get("model_tier", "")).strip().lower().strip("[]'\" ")
    if effective_tier in ("flash_lite", "flash-lite", "haiku", "lite", "tier1", "tier_1"):
        errors.append(
            f"BANNED_LITE_MODEL_TIER: Model tier '{effective_tier}' is banned for Brief+ synthesis; use 'flash'/'sonnet' (Standard) or 'pro'/'opus' (Deep)."
        )

    if not text.startswith("---\n"):
        errors.append("MISSING_FRONTMATTER: Brief+ must start with YAML frontmatter (`---`).")
    else:
        fm_end = text.find("\n---", 4)
        if fm_end == -1:
            errors.append("UNCLOSED_FRONTMATTER: YAML frontmatter is missing closing `---`.")
        else:
            fm_block = text[4:fm_end]
            if not re.search(r"^type:\s*['\"]?study-brief['\"]?\s*$", fm_block, re.MULTILINE):
                errors.append("INVALID_FRONTMATTER_TYPE: Frontmatter must declare `type: \"study-brief\"`.")
            if not re.search(
                r"^status:\s*['\"]?(?:UNPROMOTED_STUDY_BRIEF|PROMOTED_ENGINEERING_BRIEF)['\"]?\s*$",
                fm_block,
                re.MULTILINE,
            ):
                errors.append(
                    "INVALID_FRONTMATTER_STATUS: Frontmatter must declare `status: \"UNPROMOTED_STUDY_BRIEF\"` (or `PROMOTED_ENGINEERING_BRIEF`)."
                )

    for req_sec in REQUIRED_SECTIONS:
        if req_sec not in text:
            errors.append(f"MISSING_REQUIRED_SECTION: Missing `{req_sec}` heading.")

    starts = list(re.finditer(r"<!--\s*FIRST-PRINCIPLES-THEORY:START\s*-->", text, re.IGNORECASE))
    ends = list(re.finditer(r"<!--\s*FIRST-PRINCIPLES-THEORY:END\s*-->", text, re.IGNORECASE))
    if len(starts) != len(ends) or len(starts) == 0:
        errors.append(
            "UNBALANCED_THEORY_MARKERS: Brief+ must contain balanced `<!-- FIRST-PRINCIPLES-THEORY:START -->` and `<!-- FIRST-PRINCIPLES-THEORY:END -->` markers around Sections 1–2."
        )
    else:
        sec3_pos = text.find("## 3. Active Engineering Context Overlaps")
        sec4_pos = text.find("## 4. Actionable Engineering Guardrails")
        for s_m, e_m in zip(starts, ends):
            if s_m.start() >= e_m.start():
                errors.append("INVERTED_THEORY_MARKERS: `FIRST-PRINCIPLES-THEORY:START` appears after `END`.")
            if sec3_pos != -1 and s_m.start() <= sec3_pos <= e_m.end():
                errors.append(
                    "THEORY_ZONE_EVASION_BLOCKED: `## 3. Active Engineering Context Overlaps` is inside `FIRST-PRINCIPLES-THEORY` (Section 3 must remain outside the theory zone so repo claims are verified against `--sources`)."
                )
            if sec4_pos != -1 and s_m.start() <= sec4_pos <= e_m.end():
                errors.append(
                    "THEORY_ZONE_EVASION_BLOCKED: `## 4. Actionable Engineering Guardrails` is inside `FIRST-PRINCIPLES-THEORY`."
                )
            if require_depth and s_m.end() < e_m.start():
                theory_body = text[s_m.end() : e_m.start()]
                theory_words = re.findall(r"[A-Za-z0-9_]+", theory_body)
                if len(theory_words) < 60:
                    errors.append(
                        f"SHALLOW_THEORY_SYNTHESIS: Sections 1–2 contain only {len(theory_words)} words (minimum 60 words required for first-principles synthesis)."
                    )
                for req_pillar in ("First-Principles Mechanism", "Governing Scaling", "Key Boundary Condition"):
                    if req_pillar.lower() not in theory_body.lower():
                        errors.append(
                            f"INCOMPLETE_MENTAL_MODEL_PILLARS: Section 1 is missing `{req_pillar}` bullet."
                        )
                if "causal coupling chain" not in theory_body.lower() or not re.search(r"^\s*\|.*\|", theory_body, re.MULTILINE):
                    errors.append(
                        "MISSING_TRADEOFF_ENVELOPE_TABLE: Section 2 must include `Causal Coupling Chain` and a Markdown Trade-Off & Failure Envelope table."
                    )

    # Check Section 3 has real overlap content and not unmodified scaffold text
    sec3_pos = text.find("## 3. Active Engineering Context Overlaps")
    sec4_pos = text.find("## 4. Actionable Engineering Guardrails")
    if sec3_pos != -1 and sec4_pos != -1 and sec4_pos > sec3_pos:
        sec3_body = text[sec3_pos:sec4_pos]
        if "Replace with exact 1-3 line verbatim slice from the source file" in sec3_body:
            errors.append(
                "UNFILLED_SCAFFOLD_TEMPLATE: Section 3 still contains default template placeholder text."
            )
        has_overlap_marker = bool(
            re.search(
                r"(?:\[(?:VERIFIED FACT|CAD TELEMETRY|CLI TELEMETRY|CONTEXT ANALOGY|TBD:[^\]]+)\]|###\s+Overlap\s+Example)",
                sec3_body,
                re.IGNORECASE,
            )
        )
        if not has_overlap_marker:
            errors.append(
                "MISSING_CONTEXT_OVERLAP_EXAMPLE: Section 3 must contain at least 1 concrete overlap example (`[VERIFIED FACT]`, `[CAD TELEMETRY]`, `[CLI TELEMETRY]`, or `[CONTEXT ANALOGY]`)."
            )
        if require_depth and sources and 1 <= len(sources) <= 3:
            sec3_low = sec3_body.lower().replace("\\", "/")
            for raw_src in sources:
                src_p = Path(str(raw_src).replace("\\", "/")).expanduser().resolve()
                if not src_p.is_file():
                    continue
                bname_low = src_p.name.lower()
                parent_bname_low = f"{src_p.parent.name.lower()}/{bname_low}"
                # Check if either the full/parent-qualified path or basename (when unique) is cited in Section 3
                same_basename_cnt = sum(
                    1 for s in sources if Path(str(s).replace("\\", "/")).name.lower() == bname_low
                )
                matched_src = (
                    (parent_bname_low in sec3_low)
                    if same_basename_cnt > 1
                    else (bname_low in sec3_low or parent_bname_low in sec3_low)
                )
                if not matched_src:
                    errors.append(
                        f"UNCITED_SEED_SOURCE: Seed source `{src_p}` was not cited in Section 3 (`Active Engineering Context Overlaps`); ground every seeded `--sources` file rather than silently dropping it."
                    )

    return errors


def verify_and_stamp_brief(
    brief_path: Path,
    sources: list[str],
    entity: str = "",
    fail_on_tbd: bool = False,
    strict_provenance: bool = False,
    briefs_root: Path | None = None,
    auto_slug: bool = False,
    slug_override: str = "",
    require_depth: bool = False,
    model_tier: str = "",
) -> dict[str, Any]:
    """Verify `Brief+` structure and claims via `verify_claims.py`, then stamp VRF receipt."""
    brief_path = brief_path.expanduser().resolve()
    if not brief_path.is_file():
        return {
            "status": "FAIL",
            "structural_errors": [f"Brief file not found: {brief_path}"],
            "claim_report": None,
        }

    if briefs_root is not None:
        resolved_root = briefs_root.expanduser().resolve()
        try:
            brief_path.relative_to(resolved_root)
            if "study_briefs" in resolved_root.name.lower() or brief_path.parent != resolved_root:
                ensure_briefs_root_readme(resolved_root)
        except ValueError:
            pass

    if auto_slug:
        ren = rename_brief_clean(brief_path, slug_override=slug_override)
        if ren.get("status") != "FAIL" and ren.get("new_path"):
            brief_path = Path(ren["new_path"]).resolve()

    text = brief_path.read_text(encoding="utf-8")
    struct_errors = verify_brief_structure(
        text,
        brief_path,
        require_depth=require_depth,
        sources=sources,
        model_tier=model_tier,
    )
    fm_meta = _extract_frontmatter_meta(text)

    verify_script = HOMUNCULUS_ROOT / "skills" / "claim-verification" / "scripts" / "verify_claims.py"
    resolved_sources = [str(Path(s.replace("\\", "/")).expanduser().resolve()) for s in sources]
    claim_report: dict[str, Any] = {}
    vc_exit_code = 0

    # Pairing B: Dual-Mode In-Process Fast-Path (~2.66x faster) with automatic Subprocess Fallback
    inproc_ok = False
    if verify_script.is_file():
        try:
            vc_dir = str(verify_script.parent)
            if vc_dir not in sys.path:
                sys.path.insert(0, vc_dir)
            import verify_claims as _vc_mod  # noqa: E402

            claim_report = dict(
                _vc_mod.verify_target_inprocess(
                    target_path=str(brief_path),
                    sources=resolved_sources,
                    entity=entity,
                )
            )
            has_forged = any(
                any("forged" in str(r) or "hash mismatch" in str(r) for r in pw.get("reasons", []))
                for pw in claim_report.get("provenance_warnings", [])
            )
            if has_forged:
                vc_exit_code = 3
            elif int(claim_report.get("unbacked_count", 0)) > 0:
                vc_exit_code = 1
            elif strict_provenance and int(claim_report.get("provenance_warning_count", 0)) > 0:
                vc_exit_code = 3
            elif fail_on_tbd and int(claim_report.get("tbd_count", 0)) > 0:
                vc_exit_code = 2
            inproc_ok = True
        except Exception:
            inproc_ok = False

    if not inproc_ok:
        cmd = [
            sys.executable,
            str(verify_script),
            "--target",
            str(brief_path),
            "--sources",
            *resolved_sources,
            "--skip-freshness-check",
            "--json",
        ]
        if entity:
            cmd.extend(["--entity", entity])
        if fail_on_tbd:
            cmd.append("--fail-on-tbd")
        if strict_provenance:
            cmd.append("--strict-provenance")

        proc = subprocess.run(cmd, capture_output=True, text=True, check=False)
        vc_exit_code = proc.returncode
        if proc.stdout.strip():
            try:
                claim_report = json.loads(proc.stdout)
            except json.JSONDecodeError:
                struct_errors.append(f"VERIFY_CLAIMS_JSON_ERROR: {proc.stdout.strip()[:200]}")
        if proc.returncode != 0 and not claim_report:
            struct_errors.append(f"VERIFY_CLAIMS_ERROR: {proc.stderr.strip() or proc.stdout.strip()}")

    unbacked_cnt = int(claim_report.get("unbacked_count", 0)) if claim_report else 1
    tbd_cnt = int(claim_report.get("tbd_count", 0)) if claim_report else 0
    prov_cnt = int(claim_report.get("provenance_warning_count", 0)) if claim_report else 0
    vrf_token = str(claim_report.get("vrf_token", "")) if claim_report else ""

    passed = (
        len(struct_errors) == 0
        and vc_exit_code == 0
        and unbacked_cnt == 0
        and (not fail_on_tbd or tbd_cnt == 0)
        and (not strict_provenance or prov_cnt == 0)
    )

    if passed and vrf_token:
        src_hashes = claim_report.get("source_hashes", [])
        src_hash_str = ", ".join(
            f"{ os.path.basename(str(sh['file'])) }({sh['sha256_10']})" for sh in src_hashes
        )
        updated = re.sub(
            r'^vrf_receipt:\s*".*"$',
            f'vrf_receipt: "{vrf_token}"',
            text,
            flags=re.MULTILINE,
        )
        updated = re.sub(
            r"- \*\*Verification Receipt\*\*:\s*[^\n|]+\|\s*\*\*Source Hashes\*\*:\s*[^\n]+",
            f"- **Verification Receipt**: {vrf_token} | **Source Hashes**: {src_hash_str}",
            updated,
        )
        if updated != text:
            brief_path.write_text(updated, encoding="utf-8")

    dom_val = fm_meta.get("domain", "hybrid") or "hybrid"
    status_val = fm_meta.get("status", "UNPROMOTED_STUDY_BRIEF") or "UNPROMOTED_STUDY_BRIEF"
    eff_tier = (model_tier or fm_meta.get("model_tier", "")).strip()
    display_name = format_brief_display_name(brief_path, briefs_root)
    rail_top, rail_bot = build_chat_rails(
        domain=dom_val,
        vrf_token=vrf_token or "UNVERIFIED",
        status=status_val,
        model_tier=eff_tier,
    )
    card_template = build_chat_card_template(
        brief_path=brief_path,
        briefs_root=briefs_root,
        domain=dom_val,
        vrf_token=vrf_token or "UNVERIFIED",
        status=status_val,
        model_tier=eff_tier,
    )

    return {
        "status": "PASS" if passed else "FAIL",
        "brief_path": str(brief_path),
        "brief_uri": brief_path.as_uri(),
        "display_name": display_name,
        "vrf_token": vrf_token,
        "chat_rail_top": rail_top,
        "chat_rail_bottom": rail_bot,
        "chat_card_template": card_template,
        "structural_errors": struct_errors,
        "unbacked_count": unbacked_cnt,
        "tbd_count": tbd_cnt,
        "provenance_warning_count": prov_cnt,
        "claim_report": claim_report,
    }


def rename_brief_clean(brief_path: Path, slug_override: str = "") -> dict[str, Any]:
    """Rename a brief file in place using smart whole-word slugging derived from its YAML frontmatter."""
    src_p = brief_path.expanduser().resolve()
    if not src_p.is_file():
        return {"status": "FAIL", "reason": f"Brief file not found: {src_p}"}
    txt = src_p.read_text(encoding="utf-8", errors="replace")
    fm = _extract_frontmatter_meta(txt)
    date_prefix = fm.get("created_at", "").strip()
    if not re.match(r"^\d{4}-\d{2}-\d{2}$", date_prefix):
        m = re.match(r"^(\d{4}-\d{2}-\d{2})_", src_p.stem)
        date_prefix = m.group(1) if m else datetime.now(timezone.utc).strftime("%Y-%m-%d")

    subject = fm.get("subject", "") or src_p.stem
    impact_on = fm.get("impact_on", "")
    project = fm.get("project", "") or src_p.parent.name or "General"

    clean_slug = build_brief_slug(
        subject=subject,
        impact_on=impact_on,
        project=project,
        slug_override=slug_override,
    )
    dst_p = src_p.parent / f"{date_prefix}_{clean_slug}.md"
    if dst_p != src_p:
        src_p.rename(dst_p)
    return {
        "status": "RENAMED" if dst_p != src_p else "UNCHANGED",
        "old_path": str(src_p),
        "new_path": str(dst_p),
        "clean_slug": clean_slug,
    }


def list_briefs(briefs_root: Path, project_filter: str = "") -> list[dict[str, str]]:
    """List all Markdown study briefs in `<study_briefs_root>`."""
    items: list[dict[str, str]] = []
    if not briefs_root.is_dir():
        return items
    for md_p in sorted(briefs_root.rglob("*.md")):
        if md_p.name.lower() == "readme.md":
            continue
        txt = md_p.read_text(encoding="utf-8", errors="replace")
        meta: dict[str, str] = {
            "path": str(md_p),
            "rel_path": md_p.relative_to(briefs_root).as_posix(),
            "title": md_p.stem,
            "subject": "",
            "impact_on": "",
            "domain": "",
            "project": "",
            "status": "UNPROMOTED_STUDY_BRIEF",
            "vrf_receipt": "UNVERIFIED",
        }
        for k, v in _extract_frontmatter_meta(txt).items():
            if k in meta:
                meta[k] = v
        if project_filter and meta["project"].lower() != project_filter.strip().lower():
            continue
        items.append(meta)
    return items


def promote_brief(
    brief_path: Path,
    mem_root: Path,
    project: str,
    target_kind: str,
    sources: list[str],
    entity: str = "",
) -> dict[str, Any]:
    """Verify a study brief (failing closed on unbacked claims or open [TBD]s) and promote into `<memory_root>`."""
    ver = verify_and_stamp_brief(
        brief_path=brief_path,
        sources=sources,
        entity=entity,
        fail_on_tbd=True,
        strict_provenance=False,
    )
    if ver["status"] != "PASS":
        return {
            "status": "BLOCKED",
            "reason": "Brief failed pre-promotion verification (`0` structural errors, `0` unbacked claims, and `0` open `[TBD]`s required).",
            "verification": ver,
        }

    text = brief_path.read_text(encoding="utf-8")
    promoted_text = re.sub(
        r'^status:\s*"UNPROMOTED_STUDY_BRIEF"$',
        'status: "PROMOTED_ENGINEERING_BRIEF"',
        text,
        flags=re.MULTILINE,
    )
    promoted_text = re.sub(
        r"^consumed_by_memory:\s*false$",
        "consumed_by_memory: true",
        promoted_text,
        flags=re.MULTILINE,
    )
    brief_path.write_text(promoted_text, encoding="utf-8")

    norm_target = target_kind.strip().lower().replace("-", "_")
    if norm_target == "standards":
        dst_dir = mem_root / "Standards_and_Specs"
        dst_dir.mkdir(parents=True, exist_ok=True)
        dst_path = dst_dir / brief_path.name
        shutil.copy2(brief_path, dst_path)
    elif norm_target == "project_doc":
        if not project or project.lower() == "general":
            return {
                "status": "BLOCKED",
                "reason": "--project <ProjectName> is required when promoting to 'project-doc'.",
            }
        dst_dir = mem_root / "Projects" / project
        if not dst_dir.is_dir():
            return {
                "status": "BLOCKED",
                "reason": f"Project directory does not exist in memory: {dst_dir}",
            }
        dst_path = dst_dir / brief_path.name
        shutil.copy2(brief_path, dst_path)
    elif norm_target == "lessons_learned":
        if not project or project.lower() == "general":
            return {
                "status": "BLOCKED",
                "reason": "--project <ProjectName> is required when promoting to 'lessons-learned'.",
            }
        ll_path = mem_root / "Projects" / project / f"{project}_Lessons_Learned.md"
        if not ll_path.is_file():
            return {
                "status": "BLOCKED",
                "reason": f"Lessons Learned file not found: {ll_path}",
            }
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        vrf = ver["vrf_token"]
        append_block = (
            f"\n### Promoted Engineering Brief ({today}): {brief_path.stem} (`{vrf}`)\n"
            f"- **Source Brief**: `{brief_path.name}` (`status: PROMOTED_ENGINEERING_BRIEF`, Receipt: `{vrf}`)\n"
        )
        with open(ll_path, "a", encoding="utf-8") as f:
            f.write(append_block)
        dst_path = ll_path
    else:
        return {
            "status": "BLOCKED",
            "reason": f"Unsupported --target '{target_kind}'. Choose from {VALID_PROMOTE_TARGETS}.",
        }

    return {
        "status": "PROMOTED",
        "source_brief": str(brief_path),
        "promoted_to": str(dst_path),
        "vrf_token": ver["vrf_token"],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Homunculus Universal Engineering & Technical Learning Engine (teach_brief.py)."
    )
    parser.add_argument("--workspace", help="Workspace directory (default: CWD).")
    parser.add_argument("--memory-root", help="Explicit memory root directory.")
    parser.add_argument(
        "--briefs-root",
        help="Explicit non-consumed study_briefs directory (default: <memory_root.parent>/study_briefs).",
    )
    parser.add_argument(
        "--init-brief",
        action="store_true",
        help="Scaffold a new `Brief+` Markdown file inside <study_briefs_root>.",
    )
    parser.add_argument("--subject", default="", help="Primary engineering subject <X> to teach.")
    parser.add_argument(
        "--impact-on",
        default="",
        help="Target engineering system/component/parameter <Y> impacted by <X>.",
    )
    parser.add_argument(
        "--slug",
        default="",
        help="Optional concise custom filename slug override (snapped on whole-word boundaries).",
    )
    parser.add_argument(
        "--domain",
        type=lambda s: s.strip().lower().replace("-", "_"),
        choices=VALID_DOMAINS,
        default="hybrid",
        help="Engineering domain classification (mechanical, electrical, firmware, cabling, software, hybrid).",
    )
    parser.add_argument("--project", default="General", help="Project context name (default: General).")
    parser.add_argument("--entity", default="Default_Entity", help="Owner/client entity tag.")
    parser.add_argument("--out", help="Optional explicit output path for --init-brief.")
    parser.add_argument(
        "--rename-clean",
        metavar="BRIEF_PATH",
        help="Rename an existing brief file in place using clean whole-word slugging.",
    )
    parser.add_argument("--verify", metavar="BRIEF_PATH", help="Verify a `Brief+` file and stamp VRF receipt.")
    parser.add_argument(
        "--auto-slug",
        action="store_true",
        help="Snap the target brief filename to clean whole-word YYYY-MM-DD_<Subject>_on_<Impact>.md during --verify.",
    )
    parser.add_argument(
        "--require-depth",
        action="store_true",
        help="Enforce anti-shallow synthesis checks (all 3 mental-model pillars, trade-off table, >=60 theory words, and full --sources coverage).",
    )
    parser.add_argument(
        "--model-tier",
        default="",
        help="Model tier used by the subagent ('flash'/'sonnet' or 'pro'/'opus') for header rail badge and anti-lite enforcement.",
    )
    parser.add_argument(
        "--classify-complexity",
        action="store_true",
        help="Deterministically classify `/teach-me` query complexity and output required subagent model tier ('flash'/'sonnet' vs. 'pro'/'opus').",
    )
    parser.add_argument(
        "--sources",
        nargs="+",
        default=[],
        help="Authoritative repo/memory source files or directories for --verify / --promote / --classify-complexity.",
    )
    parser.add_argument("--fail-on-tbd", action="store_true", help="Fail verification if open [TBD] markers remain.")
    parser.add_argument(
        "--strict-provenance",
        action="store_true",
        help="Fail verification if any --sources file has suspect provenance.",
    )
    parser.add_argument("--list", action="store_true", help="List study briefs in <study_briefs_root>.")
    parser.add_argument(
        "--promote",
        metavar="BRIEF_PATH",
        help="Promote a verified `Brief+` file into <memory_root>.",
    )
    parser.add_argument(
        "--target",
        type=lambda s: s.strip().lower().replace("-", "_"),
        choices=VALID_PROMOTE_TARGETS,
        default="standards",
        help="Promotion destination inside <memory_root>: standards, project-doc, or lessons-learned.",
    )
    parser.add_argument("--json", action="store_true", help="Emit JSON output.")

    args = parser.parse_args(argv)
    if args.classify_complexity:
        res_cls = classify_query_complexity(
            subject=args.subject.strip(),
            impact_on=args.impact_on.strip(),
            domain=args.domain,
            sources=args.sources,
            model_override=args.model_tier,
        )
        if args.json:
            print(json.dumps(res_cls, indent=2))
        else:
            print(
                f"[ROUTING] Complexity: {res_cls['complexity_tier'].upper()} | "
                f"Antigravity: '{res_cls['antigravity_model']}' | "
                f"Claude: '{res_cls['claude_model']}' | "
                f"Badge: [{res_cls['rail_badge']}] | "
                f"Triggers: {', '.join(res_cls['triggers'])}"
            )
        return 0

    mem_root, briefs_root = resolve_roots(
        workspace=args.workspace,
        memory_root_arg=args.memory_root,
        briefs_root_arg=args.briefs_root,
    )
    homunculus_paths.ensure_directory_fresh(
        workspace_dir=args.workspace,
        homunculus_root=HOMUNCULUS_ROOT,
        memory_root_override=mem_root,
    )

    if args.init_brief:
        if not args.subject.strip():
            parser.error("--init-brief requires --subject <Subject X>")
        out_p = Path(args.out.replace("\\", "/")) if args.out else None
        created = init_brief(
            briefs_root=briefs_root,
            subject=args.subject.strip(),
            impact_on=args.impact_on.strip(),
            domain=args.domain,
            project=args.project.strip(),
            entity=args.entity.strip(),
            slug_override=args.slug.strip(),
            out_path=out_p,
        )
        disp = format_brief_display_name(created, briefs_root)
        if args.json:
            print(
                json.dumps(
                    {
                        "status": "INITIALIZED",
                        "brief_path": str(created),
                        "brief_uri": created.as_uri(),
                        "display_name": disp,
                    },
                    indent=2,
                )
            )
        else:
            print(f"[OK] Initialized non-consumed Study Brief+ ({disp}): {created}")
        return 0

    if args.rename_clean:
        res = rename_brief_clean(
            brief_path=Path(args.rename_clean.replace("\\", "/")),
            slug_override=args.slug.strip(),
        )
        if args.json:
            print(json.dumps(res, indent=2))
        else:
            if res["status"] == "FAIL":
                print(f"[FAIL] {res['reason']}", file=sys.stderr)
            else:
                print(f"[{res['status']}] {res['old_path']} -> {res['new_path']}")
        return 0 if res["status"] != "FAIL" else 1

    if args.verify:
        if not args.sources:
            parser.error("--verify requires --sources <source_file_or_dir ...>")
        res = verify_and_stamp_brief(
            brief_path=Path(args.verify.replace("\\", "/")),
            sources=args.sources,
            entity=args.entity if args.entity != "Default_Entity" else "",
            fail_on_tbd=args.fail_on_tbd,
            strict_provenance=args.strict_provenance,
            briefs_root=briefs_root,
            auto_slug=args.auto_slug,
            slug_override=args.slug.strip(),
            require_depth=args.require_depth,
            model_tier=args.model_tier.strip(),
        )
        if args.json:
            print(json.dumps(res, indent=2))
        else:
            print(
                f"[{res['status']}] Brief+ Verification: {res['display_name']} | "
                f"Path: {res['brief_path']} | "
                f"Receipt: {res['vrf_token'] or 'NONE'} | "
                f"Structural Errors: {len(res['structural_errors'])} | "
                f"Unbacked Claims: {res['unbacked_count']}"
            )
            for se in res["structural_errors"]:
                print(f"  [!] {se}")
            if res.get("claim_report") and res["claim_report"].get("unbacked_claims"):
                unbacked_list = res["claim_report"]["unbacked_claims"]
                for uc in unbacked_list:
                    print(f"  [!] Line {uc['line']} [{uc['type']}]: {uc['claim']}")
                uc_types = {str(uc.get("type", "")) for uc in unbacked_list}
                if uc_types & {"LITERAL_ID", "QUANTITY_UNIT"}:
                    print(
                        "  [Hint] Sections 3–4 are closed-world audited against --sources: keep generic CLI commands, "
                        "textbook figures, and unrecorded runtime output inside Sections 1–2 (FIRST-PRINCIPLES-THEORY), "
                        "tag missing specs as [TBD: <var>], and only backtick exact --sources literals in Sections 3–4."
                    )
                if "QUARANTINED_ZONE_CITATION" in uc_types:
                    print(
                        "  [Hint] Cite verified architecture/parameter sections or _Hardware.md/_Software.md—never "
                        "quarantined SESSION-HANDOFF, QUARANTINE-ZONE, or Open [TBD] ledger blocks."
                    )
                if "WARNING_CONTEXT_CITATION" in uc_types:
                    print(
                        "  [Hint] When citing near a source [!WARNING]/[!CAUTION] or prohibition ('do not'/'never'), "
                        "include an explicit hazard/negation keyword (warning, caution, hazard, never, do not, avoid, "
                        "damage, strip, crack) in the claiming bullet so safety warnings are never neutralized."
                    )
                if any("COUNTED_ENTITY" in t for t in uc_types):
                    print(
                        "  [Hint] Numbers adjacent to hardware nouns (e.g. '12 fasteners') are audited against --sources "
                        "counts; rephrase step references ('Steps 10–11 specify BHCS hardware') or tag missing counts as [TBD: <var>]."
                    )
            if res["status"] == "PASS":
                print("\n--- TEACH-ME CHAT CARD TEMPLATE (RELAY VERBATIM WITH FILLED FIELDS) ---")
                print(res["chat_card_template"])
        return 0 if res["status"] == "PASS" else 1

    if args.promote:
        if not args.sources:
            parser.error("--promote requires --sources <source_file_or_dir ...>")
        res = promote_brief(
            brief_path=Path(args.promote.replace("\\", "/")),
            mem_root=mem_root,
            project=args.project.strip(),
            target_kind=args.target,
            sources=args.sources,
            entity=args.entity if args.entity != "Default_Entity" else "",
        )
        if args.json:
            print(json.dumps(res, indent=2))
        else:
            if res["status"] == "PROMOTED":
                print(
                    f"[PROMOTED] {res['source_brief']} -> {res['promoted_to']} "
                    f"(Receipt: {res['vrf_token']})"
                )
            else:
                print(f"[BLOCKED] {res['reason']}", file=sys.stderr)
                ver = res.get("verification") or {}
                for se in ver.get("structural_errors", []):
                    print(f"  [!] {se}", file=sys.stderr)
        return 0 if res["status"] == "PROMOTED" else 1

    if args.list:
        items = list_briefs(briefs_root, project_filter=args.project if args.project != "General" else "")
        if args.json:
            print(json.dumps({"study_briefs_root": str(briefs_root), "count": len(items), "briefs": items}, indent=2))
        else:
            print(f"=== Study Briefs ({len(items)}) in {briefs_root} ===")
            for it in items:
                print(
                    f"  - [{it['status']}] {it['rel_path']} | "
                    f"Domain: {it['domain']} | Receipt: {it['vrf_receipt']}"
                )
        return 0

    parser.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
