---
name: author-voice-cadence
description: Optional side-loaded Drop-In add-on skill. Use whenever ingesting an author's writing/devlog corpus (Discord exports, Markdown blogs, engineering notes), drafting or editing long-form technical content (READMEs, Assembly Guides, devlogs, runbooks, blog posts) to match the author's natural writing voice and cadence, or running the Continuous Edit-Diff Learning loop (/learn) after the author revises a draft.
---

# Author Voice & Cadence Studio (`addons/author-voice-cadence` — Drop-In Add-On)

This module is packaged as a **side-loaded Drop-In Add-On** inside `Homunculus/addons/author-voice-cadence/` because extracting an authentic voice profile requires the installer's own historical writing corpus (blog posts, devlogs, or Discord/forum exports) once they have time to gather it.

> **Priority Invariant (`1. Accuracy & Truth -> 2. Efficiency -> 3. Data Safety -> 4. Speed`)**:
> Factual engineering accuracy (`verifiable-accuracy.md`) always outranks stylistic cadence. Never alter a numeric specification, tolerance, part identifier, or `[TBD: <var>]` marker to make a sentence sound smoother.

---

## 1. Zero-Install Drop-In Activation & Memory Standard Discovery

1. **Drop-In Activation**:
   - Symlink or copy `addons/author-voice-cadence/` into your active client skills directory (e.g., `.gemini/config/skills/author-voice-cadence` or `skills/author-voice-cadence/`), or reference `addons/author-voice-cadence/SKILL.md` directly.
   - Optionally re-run `python3 <HOMUNCULUS_ROOT>/scripts/build_adapters.py --workspace <workspace>` if you want client adapter tables refreshed automatically.
2. **Pre-Flight Voice Standard & Exemplar Discovery (`<memory_root>/Standards_and_Specs/`)**:
   - Inspect `<memory_root>/Standards_and_Specs/Standards_Index.md` for calibrated voice standards:
     - `<memory_root>/Standards_and_Specs/Author_Voice_and_Cadence.md` (quantitative rhythm, clause-linking syntax, asymmetric contractions, and `Instead of X -> Write Y` ledger).
     - `<memory_root>/Standards_and_Specs/Author_Voice_Verbatim_Exemplars.md` (few-shot acoustic anchor passages across 5 discourse categories).
     - `<memory_root>/Standards_and_Specs/Author_Voice_Cadence_Telemetry_Report.md` (stylometric distribution report).
   - When authoring repository documentation (`README.md`, `BOM.md`, `Print_Settings.md`, `Assembly_Guide.md`, `ALPHA_&_DIRECTION.md`), pair this skill with `doc-and-card-studio` (`<HOMUNCULUS_ROOT>/skills/doc-and-card-studio/SKILL.md`) and read `<memory_root>/Projects/<Project>/<Project>.md` + `<Project>_Hardware.md` (without crawling unrelated companion repositories).
   - If no calibrated profile exists yet in `<memory_root>/Standards_and_Specs/`, run Gate 1 ([`extract_voice_cadence.py`](scripts/extract_voice_cadence.py)) on your writing inbox or initialize from [`Voice_Profile_Template.md`](templates/Voice_Profile_Template.md).

---

## 2. Register Calibration Matrix (`Mode A1 / A2 / B1 / B2`)

Before drafting or revising prose, select the target **Register Mode**:

| Register Mode | Target Documents | Quantitative Cadence & Structural Rules |
| :--- | :--- | :--- |
| **Mode A1: Public Blog & Announcements** | Devlog posts, release announcements, `README.md` philosophy sections | **Conversational Engineering Peer (`~19w` median, IQR `13–26w`, `~9.5w` beat-to-beat swing)**: Open with a direct technical premise or bench progress hook; walk through what was tested, what failed, and why the current geometry won; blend `I/my` + `we/our` + `you/your`; include `1–2` natural parenthetical asides `(...)` per 200 words and occasional trailing ellipses `...` or spaced dashes. |
| **Mode A2: Engineering & R&D Deep Dives** | `ALPHA_&_DIRECTION.md`, architecture write-ups, engineering trade-off logs | **Analytical Subsystem Designer (`~23w` median, IQR `15–32w`, `~11.1w` beat-to-beat swing)**: Use multi-clause physical/thermal/kinematic cause-and-effect chains linked via comma-pivots (`, so`, `, as`, `, which`, `, while`) and clause-final `"though"`; pair plainspoken conviction with candid engineering qualifiers (`likely`, `probably`, `for now`, `at the cost of`). |
| **Mode B1: Concise Installation, Print & BOM Guides** | `Assembly_Guide.md`, `Print_Settings.md`, `BOM.md` | **Concise Imperative (`1–2` crisp sentences per routine operation; Paramount-Only Verified Reasoning)**: State standard operations (pressing heat-sets flush, seating screws) in **1–2 crisp sentences**—never expand into multi-step tool baby-tutorials, never add filler `Notes` columns explaining obvious material roles (`"Print in TPU"` needs no elastomer lecture), and never repeat per-step plastic-torque warnings (place global torque/chemical rules once upfront in `> [!CAUTION]`). Include `"why"` reasoning **ONLY when paramount AND verified** in project docs/standards (tight-clearance alignment collisions, seal leaks, thermal/chemical hazards). |
| **Mode B2: Technical Reference & Diagnostic Guides** | Reference catalogs, troubleshooting & calibration guides | **Pragmatic Instructor (`~19w` median, IQR `12–27w`)**: Concisely pair physical/mechanical cause-and-effect with a practical shop-floor verification check where teaching the diagnostic concept is the document's purpose. |

---

## 3. Step-Level Verification Gates

### Gate 1 — Extract Stylometric & Cadence Telemetry (`extract_voice_cadence.py`)
Run the pure-stdlib stylometric extractor across your corpus inbox (`Messages/` Discord exports or `.md`/`.txt`/`.json`/`.csv` folders) to measure 5-band sentence length distribution, beat-to-beat burstiness (`|S_{i+1} - S_i|`), paragraph chunking, clause-pivot connectors, contraction ratios, and stratified verbatim exemplars:

```bash
python3 <HOMUNCULUS_ROOT>/addons/author-voice-cadence/scripts/extract_voice_cadence.py \
  --inbox ./voice_inbox \
  --scope maker \
  --min-words 60 \
  --output <memory_root>/Standards_and_Specs/Author_Voice_Cadence_Telemetry_Report.md
```

Present extracted candidate exemplars to the user for clearance before mutating `Author_Voice_and_Cadence.md` or `Author_Voice_Verbatim_Exemplars.md`, then run `<HOMUNCULUS_ROOT>/skills/project-memory/scripts/sync_memory.py --memory-root <memory_root> --audit`.

### Gate 2 — Enforce Cadence, Contraction & Anti-Parroting Guardrails
When drafting or editing long-form prose:
- **Paragraph Chunking & Beat Swing**: Keep `>= 80%` of prose paragraphs to **`1–3` sentences** (immediately split any `4+` sentence wall into two airy `1–3` sentence blocks) and alternate multi-clause causal explanations with brisk `3–17` word declaratives (`~8–12w` beat-to-beat swing).
- **Clause-Linking & Zero Semicolons**: Link physical cause and effect using comma-pivots (`, so`, `, as`, `, which`, `, while`) and natural clause-final `"though"`. **Never use semicolons (`;`)**—replace any `;` with a comma-pivot, dash, or period.
- **Both-Sides Asymmetric Contractions**: Keep **`cannot`**, **`I am`**, **`I will`**, and **`I have`** uncontracted for deliberate emphasis, while actively using conversational **`it's`** and **`doesn't`** (plus natural `don't` / `won't` in Mode A) so prose never reads like stiff robotic text.
- **Strict Anti-Parroting & Anti-AI Lexicon**: Emulate the *acoustic rhythm and sentence structure* of `Author_Voice_Verbatim_Exemplars.md`—**never** copy-paste or recycle specific metaphors, jokes, or verbatim phrases from the exemplar bank into unrelated hardware documents. Prefer `use` over `utilize` (`99%`), and strip all banned LLM clichés (`delve`, `tapestry`, `seamlessly`, `testament to`, `meticulously`, `furthermore`, `moreover`, `in conclusion`, `it is important to note`).

### Gate 3 — Closed-World Truth & Post-Draft Claim Verification (`verify_claims.py`)
- Ground every quantitative spec, COTS designator, material grade, and `[Part] -> [Fastener] -> [Target]` pairing on Tier 1 sources (`Projects/<Project>/<Project>_Hardware.md`, `.cfg` files, locked standards, clean `git HEAD` commits). Never dodge missing specs, borrow `ABS/ASA` settings onto `TPU`, or hide source conflicts—insert explicit `[TBD: <specific_missing_variable>]` or `[TBD: CONFLICT — <source_A> vs <source_B>]` inline.
- Run `<HOMUNCULUS_ROOT>/skills/claim-verification/scripts/verify_claims.py --target <draft_file> --sources <verified_source_files>` (without `--fail-on-tbd` during drafting) to confirm `0` unbacked claims (`VRF-<12hex>`).

### Gate 4 — Continuous Edit-Diff Learning Loop (`/learn`)
Whenever the user revises a draft or corrects phrasing:
1. Diff the original AI draft against the user's revised wording (`git diff` or side-by-side comparison) to identify the concrete phrasing delta.
2. When requested via `/learn`, append the verified rule to Section 4.2 of `<memory_root>/Standards_and_Specs/Author_Voice_and_Cadence.md` (and any standout `>= 60`-word user-written paragraph to `Author_Voice_Verbatim_Exemplars.md`), then run `sync_memory.py --memory-root <memory_root> --audit`.

---

## 4. Stop & Escalation Conditions

- **Empty or Ambiguous Multi-User Corpus**: Halt and ask the user if `--inbox` contains zero qualifying posts (`>= --min-words`) or if a multi-user Discord export lacks an explicit `--author <handle>` filter.
- **Unvetted / Dirty Source Provenance**: If a repository `.md` file being used as a source contains uncommitted dirty edits or unreceipted AI prose, alert the user before trusting its quantitative claims.
- **Accuracy vs. Style Conflict**: If a stylistic rewrite would obscure a required fastener length, head style (`SHCS`/`BHCS`), pin assignment, or `[TBD: ...]` abstention tag, preserve the explicit engineering specification unconditionally.
