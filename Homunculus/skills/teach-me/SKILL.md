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
   - Extract only a compact **Context Seed** (`subject_x`, `impact_on_y`, `domain`, `project`, `entity`, and **`1–2` authoritative `--sources` files**—`3` max; never instruct the subagent to run shell `git`/`grep` probes whose output is absent from `--sources`, and resolve unseeded project or standards files on Turn 1 via `<memory_root>/Directory/<Entity>_Directory.md` or `<memory_root>/Projects/<Project>/<Project>.md` rather than `ls`/`find`/`os.listdir`) and call `invoke_subagent` (`Model: 'flash'`/`'sonnet'` default; `'pro'`/`'opus'` for `[deep]`) with instructions to read [`references/brief_authoring_playbook.md`](references/brief_authoring_playbook.md) and seed sources in **one parallel Turn-1 `read_file` batch**.
   - **Clean Async Handoff**: Emit a 1-line `[DISPATCH]` banner in the **same** turn as `invoke_subagent`; when the tool returns, close the turn with a 1-sentence standby acknowledgment and **zero** additional tool calls while waiting for wakeup.
   - *(Exception: If already running inside the delegated subagent or a dedicated study-only window, read [`references/brief_authoring_playbook.md`](references/brief_authoring_playbook.md) and execute directly without spawning a nested subagent.)*
2. **Non-Consumed Quarantine Invariant (`<study_briefs_root>/`)**:
   - Store unpromoted briefs exclusively in `<study_briefs_root>/` (`<memory_root.parent>/study_briefs/`), excluded from `sync_memory.py`, `.cursorignore`/`.claudeignore`/`.geminiignore`, and `verify_claims.py --sources` (`STUDY_BRIEF_SOURCE_REJECTED`) until explicit `--promote`.

---

## 2. Step-by-Step Execution Procedures

1. **Subagent Execution (`Mode A` Fast-Path Create / `Mode B` Promote)**: The delegated subagent executes [`references/brief_authoring_playbook.md`](references/brief_authoring_playbook.md) and invokes CLI [`scripts/teach_brief.py`](scripts/teach_brief.py) directly (`write_file` + single-call `--verify --auto-slug` -> `VRF-<12hex>`, which executes `verify_claims.py` deterministically under the hood; during routine `Brief+` creation do not read `teach_brief.py` or `verify_claims.py` source via `read_file` or shell `sed`/`python3 -c` unless porting, auditing, or diagnosing a traceback).
2. **Primary-Thread Verbatim Card Relay (`Verification Gate`)**: When the subagent returns its verified `TEACH-ME CHAT CARD TEMPLATE`, relay it **verbatim** as live Markdown (**never** wrap in ```` ```markdown ```` fences so `file://` links remain clickable, and never flatten `┏━━ ... ━━┓` / `▸` / `↳` / `┗━━ ... ━━┛` into `###` headings or `•` bullets).

---

## 3. Stop & Escalation Conditions

1. **Validator Snooping or Theory-Zone Evasion**: Never inspect `verify_claims.py` internals to game checks, and halt on `THEORY_ZONE_EVASION_BLOCKED` if Sections 3–4 enter `FIRST-PRINCIPLES-THEORY`.
2. **Verification or Quarantine Failure**: Halt if `teach_brief.py --verify` reports unbacked claims, `[CALC]` math/dimensional mismatches, `SAFETY_POLARITY_INVERSION`, `STUDY_BRIEF_SOURCE_REJECTED`, or unresolved `[TBD]`s during `--promote`.
