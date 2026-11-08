---
name: teach-me
description: >-
  Use this skill whenever the user invokes `/teach-me` (e.g., `/teach-me about
  "<Subject X>" impact on "<Subject Y>"`) or requests an on-the-fly engineering
  or technical explanation across mechanical/CAD, electrical/PCBs/motors,
  firmware/MCUs/Klipper, structured cabling/RF, or software systems. Executes
  inside a throw-away subagent to prevent active context contamination, writes a
  verified `Brief+` lesson (with whole-word smart slugging, first-principles
  mental model, relational impact vector, and 1-2 active context overlap
  examples) to the non-consumed `<study_briefs_root>/` directory adjacent to
  `<memory_root>/`, verifies claims via `teach_brief.py` and `verify_claims.py`,
  and returns a visually distinct Solid-Line Datasheet Card (`┏━━ 🎓 TEACH-ME
  // BRIEF+ ... ━━┓`) to the active window.
---

# Universal Engineering & Technical Learning Engine (`teach-me`)

Turns on-the-fly engineering questions (`/teach-me about "<Subject X>" impact on "<Subject Y>"`) into truth-verified **`Brief+`** briefs across mechanical/CAD, electrical/PCBs/motors, firmware/Klipper, cabling/RF, and software systems with **zero main-window research bloat**.

---

## 1. Pre-Flight Foundation Checks

1. **Mandatory Throw-Away Subagent Isolation Gate (`Zero Primary-Thread Context Spillage`)**:
   - **Strict Containment Rule**: When invoked from an active engineering session, the Primary Thread **must never** draft `Brief+` files, run `teach_brief.py --verify`, or execute exploratory `read_file`, CAD, or `grep` calls in the main conversation (nor auto-spawn unrequested `/teach-me` runs). Execute directly **only** when already running inside the delegated `teach-me` throw-away subagent.
   - **Deterministic 4-Trigger Complexity Router (`flash`/`sonnet` Floor vs. `pro`/`opus` Deep)**: Extract a compact **Context Seed** (`subject_x`, `impact_on_y`, `domain`, `project`, `entity`, and **`1–2` authoritative `--sources` files**—`3` max; never instruct the subagent to run shell `git`/`grep` probes whose output is absent from `--sources`, and resolve unseeded project or standards files on Turn 1 via `<memory_root>/Directory/<Entity>_Directory.md` or `<memory_root>/Projects/<Project>/<Project>.md` rather than `ls`/`find`/`os.listdir`). Route subagent model tier via `teach_brief.py --classify-complexity` (`Routing = max(Trigger_Floor, User_Inline_Tag)`):
     - **Tier 3 Deep (`Model: 'pro'` / `'opus'`, `--model-tier pro`)**: Any query matching **(1)** coupled physics, kinematics, or `[CALC]` dimensional math, **(2)** CAD/firmware/AST telemetry sources (`_Hardware.md`, `_Software.md`, `.step`/`.stl`, `.cfg`, `.py`), **(3)** cross-repository (`>= 2` repos) or failure-mode trade-offs, or **(4)** `[deep]`.
     - **Tier 2 Standard Floor (`Model: 'flash'` / `'sonnet'`, `--model-tier flash`)**: Single-doc conceptual or policy overviews (**never** use `'flash_lite'`/`'haiku'`; `BANNED_LITE_MODEL_TIER` fails closed).
   - **Clean Async Handoff**: Emit a 1-line `[DISPATCH]` banner in the **same** turn as `invoke_subagent` (instructing the subagent to follow [`references/brief_authoring_playbook.md`](references/brief_authoring_playbook.md) verbatim with `--require-depth --model-tier <flash|pro>`); when the tool returns, close the turn with a 1-sentence standby acknowledgment and **zero** additional tool calls while waiting for wakeup.
2. **Non-Consumed Quarantine Invariant (`<study_briefs_root>/`)**:
   - Store unpromoted briefs exclusively in `<study_briefs_root>/` (`<memory_root.parent>/study_briefs/`), excluded from `sync_memory.py`, `.cursorignore`/`.claudeignore`/`.geminiignore`, and `verify_claims.py --sources` (`STUDY_BRIEF_SOURCE_REJECTED`) until explicit `--promote`.

---

## 2. Step-by-Step Execution Procedures

1. **Subagent Execution (`Mode A` Fast-Path Create / `Mode B` Promote)**: Batch `read_file` on [`references/brief_authoring_playbook.md`](references/brief_authoring_playbook.md) and **all** `--sources` files together in a single parallel turn (never read `--sources` one file per turn), then execute `write_file` + single-call [`scripts/teach_brief.py`](scripts/teach_brief.py) `--verify --auto-slug` -> `VRF-<12hex>` (`1` shell call total; never run `ls`, `git status`/`diff`, or `python3 -c "open(...).readlines()"` line-number re-reads, and never read `teach_brief.py` or `verify_claims.py` source during routine `Brief+` creation).
2. **Primary-Thread Verbatim Card Relay (`Verification Gate`)**: When the subagent returns its verified `TEACH-ME CHAT CARD TEMPLATE`, relay it **verbatim** as live Markdown (**never** wrap in ```` ```markdown ```` fences so `file://` links remain clickable, and never flatten `┏━━ ... ━━┓` / `▸` / `↳` / `┗━━ ... ━━┛` into `###` headings or `•` bullets).

---

## 3. Stop & Escalation Conditions

1. **Validator Snooping or Theory-Zone Evasion**: Never inspect `verify_claims.py` internals to game checks, and halt on `THEORY_ZONE_EVASION_BLOCKED` if Sections 3–4 enter `FIRST-PRINCIPLES-THEORY`.
2. **Verification or Quarantine Failure**: Halt if `teach_brief.py --verify` reports unbacked claims, `[CALC]` math/dimensional mismatches, `SAFETY_POLARITY_INVERSION`, `STUDY_BRIEF_SOURCE_REJECTED`, or unresolved `[TBD]`s during `--promote`.
