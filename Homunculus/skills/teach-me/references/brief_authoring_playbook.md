# `Brief+` Subagent Authoring, `[CALC]` Dimensional Math & Promotion Playbook

> **Audience**: Delegated `teach-me` throw-away subagents (or dedicated standalone study windows).
> **Anti-Snooping Law (`co-engineering-partner.md` Two-Mode `.py` Rule)**: **Never** read, `grep`, or `import` `verify_claims.py` source code to reverse-engineer validator regexes. Rely strictly on `teach_brief.py --help` and `teach_brief.py --verify` CLI diagnostics.

---

## 1. Mode A — Author & Verify a Non-Consumed `Brief+` Lesson

### Step 1: Resolve Roots & Inspect Authoritative Context (`1–3` Sources)
1. Resolve `<memory_root>` and `<study_briefs_root>` automatically via `teach_brief.py` (or `<HOMUNCULUS_ROOT>/scripts/homunculus_paths.py`).
2. Select the `1–3` authoritative source files for the active system (`--sources`):
   - **Mechanical / CAD (`.step`, `.stl`, fasteners, bores)**: Read `<memory_root>/Projects/<Project>/<Project>_Hardware.md` first; if live CAD/config telemetry is needed, run:
     ```bash
     python3 <HOMUNCULUS_ROOT>/skills/subagent-orchestrator/scripts/inspect_hardware_ecosystem.py \
       --repo <path_to_repo>
     ```
     *(Note: the flag is `--repo <dir>`, never `--target`.)*
   - **Electrical / PCBs / Motors / Firmware / Cabling**: Read repository `.cfg` / schematic / BOM docs and `<Project>_Hardware.md`.
   - **Software / Systems**: Read repository source modules and `<Project>_Software.md`.
   - **Strict Read-Only Guarantee**: Never edit repository files or `<memory_root>/` files during `/teach-me`.

### Step 2: Scaffold the `Brief+` File (Smart Whole-Word Naming)
Initialize the brief inside `<study_briefs_root>/<Project_or_General>/` (`teach_brief.py` strips parentheticals/stopwords, deduplicates `<Project>`, preserves hyphens like `teach-me` or `DC-DC`, and snaps on whole words as `YYYY-MM-DD_<Subject>_on_<Impact>.md`):
```bash
python3 <HOMUNCULUS_ROOT>/skills/teach-me/scripts/teach_brief.py \
  --init-brief \
  --subject "<Subject X>" \
  --impact-on "<Subject Y>" \
  --domain <mechanical|electrical|firmware|cabling|software|hybrid> \
  --project "<ProjectName_or_General>" \
  --entity "<EntityName>"
```
*(Optional: pass `--slug "<Concise_Custom_Slug>"` only when an explicit short slug override is desired.)*

### Step 3: Populate the 4-Section `Brief+` Document
1. **Sections 1 & 2 (`Inside <!-- FIRST-PRINCIPLES-THEORY:START/END -->`)**:
   - `## 1. Core Mental Model`: `3–5` concise first-principles bullets covering physical/electrical/mechanical/algorithmic mechanism, governing scaling laws (use LaTeX `$...$` for symbolic equations like $\Delta P \propto D_i^{-4}$), and boundary conditions.
   - **Deterministic `[CALC: <lhs> = <rhs_val> <unit>]` Syntax (Optional — Real Derivations Only)**:
     - Only wrap genuine numerical arithmetic in `[CALC: ...]`; never invent dummy `* 1` equations.
     - Supported unit pairings in `verify_claims.py`:
       - **Same-unit `+`, `-`, and scalar `*` / `/`**: `[CALC: (5 mm - 3 mm) / 2 = 1 mm]`, `[CALC: 55 mm * 2 = 110 mm]`
       - **Electrical (`V`, `A`, `W`, `ohm`)**: `V * A = W`, `W / V = A`, `W / A = V`, `V / ohm = A`, `V / A = ohm`, `A * ohm = V`
       - **Mechanical (`N`, `m`/`mm`, `Nm`)**: `N * m = Nm`, `Nm / m = N`
       - **Geometry & Fluidics (`mm`, `mm2`, `mm3`, `L/min`, `min`, `L`, `m/s`, `s`)**: `mm * mm = mm2`, `mm2 * mm = mm3`, `L/min * min = L`, `m/s * s = m`
   - `## 2. Relational Impact Vector`: Trace the causal chain (`<Subject X> -> Coupling Mechanism -> <Subject Y>`) and complete the **Trade-Off & Failure Envelope** table (`Increase` vs. `Decrease`, primary effect, secondary bottleneck, and failure mode).
2. **Sections 3 & 4 (`Outside Theory Zone — 100% Closed-World Repo Verified`)**:
   - `## 3. Active Engineering Context Overlaps`: `1–2` concrete project touchpoints tagged `[VERIFIED FACT]`, `[CAD TELEMETRY]`, or `[CLI TELEMETRY]` with exact `(Source: /abs/or/rel/path#Lstart-Lend)` and verbatim `1–3` line `Anchor:` blocks. Use `[TBD: <missing_spec>]` or `[CONTEXT ANALOGY]` if a value is absent from `--sources`.
   - `## 4. Actionable Engineering Guardrails`: `2–4` concrete checklist items (respecting polymer/threadlocker safety polarity—never prescribe anaerobic threadlocker or metal torque specs on `ABS/ASA/PC` without explicit negation).

### Step 4: Deterministic Verification Gate (`teach_brief.py --verify`)
```bash
python3 <HOMUNCULUS_ROOT>/skills/teach-me/scripts/teach_brief.py \
  --verify <path_to_generated_brief.md> \
  --sources <authoritative_source_files...>
```
- Require `Status: PASS`, `Structural Errors: 0`, `Unbacked Claims: 0`, and a stamped `VRF-<12hex>` receipt.

### Step 5: Return ONLY the Solid-Line Datasheet Card
Copy the exact pre-aligned `TEACH-ME CHAT CARD TEMPLATE` printed by `teach_brief.py --verify`, fill the `▸` / `↳` fields with clickable `file:///abs/path#Lstart-Lend` links (**never** wrap the card in a multi-line ```` ```markdown ```` code fence), and return **nothing before or after the card**:

````markdown
`┏━━ 🎓 TEACH-ME // BRIEF+ ━━━━━━━ [DOMAIN: HYBRID] ━━ [ISOLATED SUBAGENT] ━━┓`

▸ **CONCEPT & IMPACT**: <1–2 concise sentences explaining Subject X and its impact on Subject Y>
▸ **CONTEXT OVERLAPS**:
  ↳ [<file>:<lines>](file:///abs/path/to/file#Lstart-Lend) — <1-line verified project touchpoint>
  ↳ [<file>:<lines>](file:///abs/path/to/file#Lstart-Lend) — <1-line verified project touchpoint>
▸ **GUARDRAIL**: <1-line critical failure boundary or operational check>
▸ **STUDY BRIEF+**: [<Project>/<clean_filename.md>](file:///abs/path/to/brief.md)

`┗━━ 🔒 QUARANTINED: study_briefs/ (NON-CONSUMED) ━━━━━━━ [VRF-b3385dc0ccec] ━━┛`
````

---

## 2. Mode B — List, Clean-Rename, or Promote (`Explicit User Request Only`)

```bash
# List unpromoted/promoted briefs:
python3 <HOMUNCULUS_ROOT>/skills/teach-me/scripts/teach_brief.py --list

# Repair a legacy filename to clean whole-word <Subject>_on_<Impact> format:
python3 <HOMUNCULUS_ROOT>/skills/teach-me/scripts/teach_brief.py --rename-clean <path_to_brief.md>

# Promote into <memory_root>/ (enforces --fail-on-tbd + 0 unbacked claims):
python3 <HOMUNCULUS_ROOT>/skills/teach-me/scripts/teach_brief.py \
  --promote <path_to_brief.md> \
  --project "<ProjectName>" \
  --target <standards|project-doc|lessons-learned> \
  --sources <authoritative_sources...>
```
