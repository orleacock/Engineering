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

1. **Throw-Away Subagent Isolation Gate (`Zero Main-Window Spillage`)**:
   - **In an Active Working Window**: The Primary Thread **must not** run exploratory `read_file`, CAD, or `grep` calls in the main conversation.
   - Extract only a compact **Context Seed** (`subject_x`, `impact_on_y`, `domain`, `project`, `entity`, and `1–3` candidate `<local_path>` or `<memory_root>/Projects/<Project>/` paths) and call `invoke_subagent` (`Model: 'flash'`/`'sonnet'` default; `'pro'`/`'opus'` for `[deep]`) with instructions to read [`references/brief_authoring_playbook.md`](references/brief_authoring_playbook.md).
   - **Clean Async Handoff (No Blank Wait Turn)**: Output a 1-line `[DISPATCH]` notice in the **same** turn as `invoke_subagent`, then end your turn with no additional tool calls and no empty follow-up message while waiting for wakeup.
   - *(Exception: If already running inside the delegated subagent or a dedicated study-only window, read [`references/brief_authoring_playbook.md`](references/brief_authoring_playbook.md) and execute directly without spawning a nested subagent.)*
2. **Non-Consumed Quarantine Invariant (`<study_briefs_root>/`)**:
   - Store unpromoted briefs exclusively in `<study_briefs_root>/` (`<memory_root.parent>/study_briefs/`), excluded from `sync_memory.py`, `.cursorignore`/`.claudeignore`/`.geminiignore`, and `verify_claims.py --sources` (`STUDY_BRIEF_SOURCE_REJECTED`) until explicit `--promote`.

---

## 2. Step-by-Step Execution Procedures

1. **Subagent Execution (`Mode A` Create / `Mode B` Promote)**: The delegated subagent follows [`references/brief_authoring_playbook.md`](references/brief_authoring_playbook.md) and [`scripts/teach_brief.py`](scripts/teach_brief.py) (`--init-brief`, `--verify` -> `VRF-<12hex>`, `--list`, `--rename-clean`, `--promote`).
2. **Primary-Thread Verbatim Card Relay (`Verification Gate`)**: When the subagent returns its verified `TEACH-ME CHAT CARD TEMPLATE`, relay it **verbatim** as live Markdown (**never** wrap in ```` ```markdown ```` fences so `file://` links remain clickable, and never flatten `┏━━ ... ━━┓` / `▸` / `↳` / `┗━━ ... ━━┛` into `###` headings or `•` bullets).

---

## 3. Stop & Escalation Conditions

1. **Validator Snooping or Theory-Zone Evasion**: Never inspect `verify_claims.py` internals to game checks, and halt on `THEORY_ZONE_EVASION_BLOCKED` if Sections 3–4 enter `FIRST-PRINCIPLES-THEORY`.
2. **Verification or Quarantine Failure**: Halt if `teach_brief.py --verify` reports unbacked claims, `[CALC]` math/dimensional mismatches, `SAFETY_POLARITY_INVERSION`, `STUDY_BRIEF_SOURCE_REJECTED`, or unresolved `[TBD]`s during `--promote`.
