---
project: "Homunculus"
parent_note: "Homunculus_Lessons_Learned"
entity: "Alchemical-3D"
compartment: "cleanroom"
note_type: "lessons_archive"
authoritative: false
volume: 5
last_synced: "2026-11-19"
---
# Homunculus — Archive — Volume 05

> **Paginated Continuation of [`Homunculus_Lessons_Archive.md`](Homunculus_Lessons_Archive.md)**

---

## 1. Archived Full-Context Post-Mortems (`TIER3`–`TIER5`)

### `LL-037` [TIER3] — Round 5 Dueling Sandbox Victory (`37` Turns vs. `Stock R5` `47`; `0` Unbacked Claims vs. `45`), `[TBD_SPECULATIVE_GUESS]` Smuggling Closure, `[Line Text]` + Parallel `edit_file` Batching, & Option C5 Multi-Vector Red-Team Hardening
- **Symptom / Trap:**
  1. **Round 5 Trajectory & Remaining Friction (`758f3ad8` vs. `43314937`):** After applying `LL-034`, `LL-035`, and `LL-036`, `Homunculus R5` beat `Stock R5` across every accuracy, turn, fresh-token, and wall-clock metric (`37` turns vs `47`, `8m 17s` vs `11m 41s`, `163.8k` vs `210.4k` fresh input tokens, `0` snoops, `0` ad-hoc CAD scripts, `0` unbacked claims with `319` supported vs `Stock R5`'s `45` unbacked claims). However, inspecting `Homunculus R5`'s 37-turn trajectory and red-teaming the validators exposed three subtle failure modes and deeper bypass vectors:
  2. **Area A (`[TBD: ...]` Bracket-Interior Pretraining Smuggling):** Because `verify_claims.py` stripped `[TBD: ...]` tags before scanning claims, `Homunculus R5` smuggled unbacked TPU recommendations *inside* the brackets (`[TBD: TPU Shore hardness rating (recommend 95A for grommets and feet)]`, `[TBD: TPU foot infill percentage (recommend 30–40% gyroid infill)]`). Worse, a keyword-only check (`recommend|typically`) could be bypassed simply by dropping the word `"recommend"` (`[TBD: TPU Shore hardness (95A)]`, `[TBD: ASA nozzle temp (245–260 °C)]`).
  3. **Area B (`12`-Turn Post-Draft Read/Edit Serial Sequence):** Because `verify_claims.py` Pass 1 printed `Line 66 [QUANTITY_UNIT]: 12V` without printing the exact line text from the target file, the subagent spent `3` `read_file` turns re-reading its own `400`-line report plus `9` serial `edit_file` turns (`12` turns = `32%` of the entire run) to replace flagged claims.
  4. **Area C (`Option C5` Multi-Vector Red-Team Findings):**
     - **Git Commit SHA Double-Bug (`C1`):** Previously, `verify_claims.py` rejected **real** all-digit 7-char git commit SHAs (`2706629` in a target hardware repo) as unbacked `[NUMERIC_COUNT]`s, while silently ignoring **hallucinated** hex commit SHAs (`1a2b3c4`, `deadbeef`) because hex tokens with letters did not match `SINGLE_NUM_UNIT_RE`!
     - **PNG Image Pixel Dimensions (`C2`):** `audit_repo_docs.py` inspected PNG headers via `_inspect_png_stdlib` (`1532×882 px`) without printing `(WxH px, mode)` in its diagnostic line, and `verify_claims.py` did not index 24-byte PNG `IHDR` `(w_px, h_px)` into `(val, "px")`.
     - **Deep `_enforce_anti_snoop_gate()` Bypass Vectors (`C3`):** Checking only `sys.argv[0]` or only the first stack frame (`depth=1`) or allowing an `os.environ["HOMUNCULUS_DIAGNOSTIC_MODE"] == "1"` bypass could be defeated inside `python3 -c` or `/tmp/ext_snoop.py` via `os.environ` spoofing, `sys.orig_argv=[]`, `exec(compile('import verify_claims', '/home/.../tests/test_claim_verification.py', 'exec'))`, `os.path.realpath` monkey-patching, or `exec(open('.../verify_claims.py').read())` (`NameError: __file__`).
- **Hardened Solution:**
  1. **Area A (`_is_speculative_tbd` — Keyworded + Keywordless Smuggling Closure):** In `verify_claims.py`, inspect every non-`CONFLICT`, non-inert `[TBD: ...]` tag against both speculative keywords (`recommend\w*`, `typically`, `usually`, `suggest\w*`, `approx\w*`, `likely`, `nominal\w*`, etc.) **and** unbacked `SHORE_RE`, `METRIC_FASTENER_RE`, `RANGE_NUM_UNIT_RE`, and `SINGLE_NUM_UNIT_RE` tokens against `idx` (`active_entities`), while allowing source-backed component references (`[TBD: Missing current rating for 24 V rail]`).
  2. **Area B (`[Line Text]` Verbatim Output & Parallel `edit_file` Batching):** Added `[Line Text]: <exact_target_line>` below every flagged line in `verify_claims.py` and instructed agents in `[2-PASS CEILING]` and `co-engineering-partner.md` to emit all `edit_file` replacements in parallel in a single turn without re-reading the target draft.
  3. **Option C5 (`C1 + C2 + C3 + C4` — Red-Team Hardened):**
     - **`C1` (Isolated `git rev-list --all` SHA Verification):** Index repository 40-char commit SHAs into isolated `self.git_full_shas` / `self.entity_git_shas` sets (`check_git_sha()`, never mixing SHAs into `numbers_all` or `num_units`). Real commits (`2706629`, `02d872f`) pass as `GIT_COMMIT_SHA`; fake hex/digit SHAs (`1a2b3c4`, `9999999`, `revision #deadbeef`) fail as `UNVERIFIED_GIT_COMMIT_SHA`; cross-entity SHAs fail as `CROSS_ENTITY_BORROWING`; numeric bleed (`2706629 mm`) fails closed; English hex words (`acceded`, `defaced`, `effaced`) are ignored in prose.
     - **`C2` & `C4` (24-Byte PNG `IHDR` `(val, "px")` Indexing, Enriched Oracle Telemetry & `[COVERAGE_RECEIPT]`):** Index non-symlinked PNG `IHDR` dimensions (`1 <= w, h <= 32768`) strictly under unit `"px"` (`1532 mm` bleed fails closed), report `(WxH px, mode)` in `audit_repo_docs.py`, report `[GIT_PROVENANCE]` recent commits in `inspect_hardware_ecosystem.py`, and append `[COVERAGE_RECEIPT]` footers to both oracles.
     - **`C3` (Full-Stack Pure-String `_enforce_anti_snoop_gate`):** Removed all `os.environ` bypasses, checked C-level `sys.orig_argv[1:4]` for `"-c"`/`"-"`, used `_RAW_FILE = globals().get("__file__", "")` + pure-string/readlink `_norm_slash_path(..., resolve_links=True)` (immune to `os.path.realpath`/`abspath` monkey-patching while preserving `.agents/skills` symlink resolution), and walked **all** stack frames (`depth = 1..N`) to block any `<string>`/`<stdin>` or external `/tmp/*.py` frame even under `compile(..., fake_path, 'exec')`.

---

### `LL-038` [TIER3] — 5-Sprint Stateful Memory Rebuild: 3-Stage Station/Detached Resolution, `TIER0`–`TIER5` Gravity Store, Entity-Partitioned Hybrid Recall, & `script_contracts.json` Preflight Gate (`2026-11-09`)
- **Symptom / Trap:** Monolithic `504`-line `Homunculus_Lessons_Learned.md` (`~12,500` tokens), naive substring `--invariants` lookup (`q_low in s.lower()`), stringified `checkpoint_worktree: "('clean', [])"` tuples across `10` project hubs, and missing script-to-contract coupling caused context bloat and risked unpreflighted core script edits.
- **Root Cause:** Absence of `TIER0`–`TIER5` importance/lifecycle tiering, entity-partitioned hybrid BM25 + character N-gram indexing, `<=450`-token 1-line radar capsules, cooperative manual-edit detection, and a dedicated clean-room `scripts/script_contracts.json` preflight gate.
- **Verified Resolution & Permanent Guardrail:** Implemented 3-Stage repo resolution (`DIRECT_STATION` $\rightarrow$ `REANCHORED_WORKSPACE` + `--rebind-station` $\rightarrow$ `DETACHED_CACHE`), `TIER0`–`TIER5` gravity window (`<=3 TIER0 + <=7 TIER2` in main, `TIER3`–`TIER5` in `Archive/` with auto-exclusion in `verify_claims.py`), entity-partitioned hybrid recall (`<=450`-token 1-line capsules + 3-signal friction detector + `--repair-memory`), directory-scoped `memory/AGENTS.md` (`<=150` words), and `scripts/script_contracts.json` + unified `--map`/`--preflight` receipt gate ([`Homunculus_Stateful_Memory_Deployment_Plan.md`](../Homunculus_Stateful_Memory_Deployment_Plan.md); verified across `37/37` unit tests and `SBX-20261109_120538-a29c8228` `5/5 +faults`).

---

### `LL-039` [TIER3] — 5-Slot Governance Architecture, `0444` Memory Rule Seal (`governance_seal.json`), `TIER5` Provenance & Recall/Link Hardening (`2026-11-09`)
- **Symptom / Trap:** Live memory sandbox testing across `79` lessons exposed `TIER0`/`TIER2` 3-gram cosine noise-floor monopoly in `--recall`, broadcast `touched_files` (`LL-034`), positional `[TIER3]` overwrite in `--compact-memory`, broken backticked-label link rewriting in `_adjust_relative_links`, directory-qualified path bypass in `verify_claims.py`, and unsealed memory rule files.
- **Root Cause:** Unthresholded cosine/overlap multipliers drowned out exact `TIER3` matches, `re.split` on inline backticks sliced backticked Markdown link labels in half, `verify_claims.py` checked `os.path.basename()` instead of bare tool names, and memory governance docs lacked `0444` OS locks and SHA-256 hash seals.
- **Verified Resolution & Permanent Guardrail:** Authored [`Governance_and_Constraint_Architecture.md`](../../../Standards_and_Specs/Governance_and_Constraint_Architecture.md) (`5`-Slot Base Protection Format + `EXT-01..NN` Expansion Registry), added `--lock-memory-rules` (`0444`) + `--seal-governance` (`Directory/governance_seal.json` + hash-chained `Directory/governance_audit_log.jsonl`), enforced `GOVERNANCE_EVENT_REQUIRED` + inline `Retirement Provenance` on `TIER5` demotions, calibrated recall scoring, fixed backtick-safe relative link rewriting, and restricted `verify_claims.py` tool exemptions to bare installed basenames (`38/38` unit tests `PASS`).

---

### `LL-040` [TIER3] — Compare-Full and pre-deployment sandboxes exposed --allow-lessons-source laundering, unwindowed Archive... (`2026-11-10`)
- **Symptom / Trap:** Compare-Full and pre-deployment sandboxes exposed --allow-lessons-source laundering, unwindowed Archive dumps, numeric/unit BM25 collisions, scalar .cfg gaps, and station-coupled ../../../Homunculus links.
- **Root Cause:** verify_claims exposed --allow-lessons-source; Archive/ lacked 0444 and <=30L read caps; BM25 kept numbers and unit words; sync_hardware filtered .cfg keys; companion notes used ../../../ links.
- **Verified Resolution & Permanent Guardrail:** Removed --allow-lessons-source, enforced 0444 Archive/ + <=30L transcript cap + v1.1 monotonic TIER5 hashes, N1 non-numeric recall, 3.3-Unified-A portable anchors, Stage-2 disaster recovery, and Option 4D commit-lesson gate. (`skills/project-memory/scripts/sync_memory.py` ([`Homunculus_Software.md`](../Homunculus_Software.md)), `skills/claim-verification/scripts/verify_claims.py` ([`Homunculus_Software.md`](../Homunculus_Software.md)), `addons/hardware-cad-inspector/scripts/inspect_hardware_ecosystem.py` ([`Homunculus_Software.md`](../Homunculus_Software.md)), `scripts/homunculus_paths.py` ([`Homunculus_Software.md`](../Homunculus_Software.md)) (`SBX-20261109_202707-75056003`)).

---

### `LL-043` [TIER3] — Composite Turn-1 --kickstart + --preflight duplicated SUBSYSTEM-INVARIANTS; adapters lacked Antigravity... (`2026-11-10`)
- **Symptom / Trap:** Composite Turn-1 --kickstart + --preflight duplicated SUBSYSTEM-INVARIANTS; adapters lacked Antigravity Carbon .agents/skills.json and non-destructive hooks.json preservation; audit_skill_hygiene missed named Carbon PostToolUse hooks and broken docs/ links
- **Root Cause:** kickstart_project lacked [LEDGER_MEMORY_LINE] and composite dedup; build_adapters overwrote workspace hooks.json without .agents/skills.json support; audit_skill_hygiene checked only Claude hooks.PostToolUse and skipped docs/*.md link checks
- **Verified Resolution & Permanent Guardrail:** Added composite --kickstart dedup, banned Model:inherit across all subagents with Workspace:branch for mutating frames, renamed voice /learn to /voice-learn, added --agy-skills-json + non-destructive hooks.json sync, and added Carbon PostToolUse + BROKEN_DOC_LINK_OR_SCRIPT checks (SBX-20261110_162015-7ddf774e) (`build_adapters.py` ([`Homunculus_Software.md`](../Homunculus_Software.md)), `audit_skill_hygiene.py` ([`Homunculus_Software.md`](../Homunculus_Software.md)), `audit_portability.py` ([`Homunculus_Software.md`](../Homunculus_Software.md))).

---

### `LL-046` [TIER3] — Eager memory template ejection and pre-created empty project template directories drifted behind canonical... (`2026-11-11`)
- **Symptom / Trap:** Eager memory template ejection and pre-created empty project template directories drifted behind canonical engine templates and poisoned Turn-One read-only task triage instructions while render_diagram scanned a missing Color_Palettes folder and extract_voice_cadence lacked declarative guild tier loading
- **Root Cause:** init_memory_root copied all built-in templates unconditionally into memory Templates, init_project pre-created empty per-project Templates folders with stale task stubs, render_diagram pointed at an unshipped Color_Palettes directory instead of Diagram_Palettes.json, and extract_voice_cadence left supplier and maker guild sets empty by default
- **Verified Resolution & Permanent Guardrail:** Made memory Templates sparse by default behind opt-in --eject-templates, switched per-project Templates creation to lazy on-demand --create-project-template, aligned templates/memory/AGENTS.md with zero-shell read_file Turn-One task triage, pointed render_diagram at Diagram_Palettes.json override discovery, and added fail-closed --tier-config loading to extract_voice_cadence (`skills/project-memory/scripts/sync_memory.py` ([`Homunculus_Software.md`](../Homunculus_Software.md)), `skills/visual-studio/scripts/render_diagram.py` ([`Homunculus_Software.md`](../Homunculus_Software.md)), `addons/author-voice-cadence/scripts/extract_voice_cadence.py` ([`Homunculus_Software.md`](../Homunculus_Software.md)), `scripts/build_adapters.py` ([`Homunculus_Software.md`](../Homunculus_Software.md))).

---

### `LL-041` [TIER3] — Multi-surface Antigravity transcripts risked silent truncation; verify_claims spawned eager git rev-list... (`2026-11-10`)
- **Symptom / Trap:** Multi-surface Antigravity transcripts risked silent truncation; verify_claims spawned eager git rev-list --all (2s timeout risk); sync_memory _parse_step_metrics still held legacy circle regexes; EROFS_RE matched lowercase erofs:1 counters
- **Root Cause:** Transcript discovery checked one brain dir without truncated_fields guards; SourceIndex ran git rev-list upfront instead of on-demand rev-parse; _parse_step_metrics duplicated STEP parsing; EROFS_RE lacked negative lookahead for numeric counters
- **Verified Resolution & Permanent Guardrail:** Added multi-surface transcript_full.jsonl discovery + [TRUNCATED_TRANSCRIPT_FIELD] fail-closed gate, on-demand git rev-parse --verify SHA checks, VERTEX_POINT bbox-only fallback + unconditional inspect_hardware_ecosystem delegation, and EROFS_RE numeric-counter guard (SBX-20261110_141516-73c9069d, SBX-20261110_143655-1ecf0fa7) (`verify_claims.py` ([`Homunculus_Software.md`](../Homunculus_Software.md)), `sandbox_runner.py` ([`Homunculus_Software.md`](../Homunculus_Software.md)), `inspect_hardware_ecosystem.py` ([`Homunculus_Software.md`](../Homunculus_Software.md)), `teach_brief.py` ([`Homunculus_Software.md`](../Homunculus_Software.md))).

---

### `LL-042` [TIER3] — Tracked _memory_index.json bloated to 1.34MB with BM25/3-gram vectors; cold bwrap runs re-walked AST/stamp... (`2026-11-10`)
- **Symptom / Trap:** Tracked _memory_index.json bloated to 1.34MB with BM25/3-gram vectors; cold bwrap runs re-walked AST/stamp trees; sync_memory re-walked vaults per check; pre-push boundary scans ran duplicate git ls-tree passes
- **Root Cause:** Scoring vectors were serialized inside tracked entity indexes; AST/stamp caches lacked v3:{content_sha} keys and RO-cage host cache seeding; audit_memory loaded full vectors and re-walked directories
- **Verified Resolution & Permanent Guardrail:** Moved vectors to gitignored .cache/*_scoring_vectors.json (-92.3% tracked JSON) with transparent cold hydration, added atomic_write_text + unified structural tree hashing, cached ASTs by v3:{content_sha} with RO host seeding, and hoisted directory/blob scans for 2.1x-4.8x speedups (SBX-20261110_150832-70629ecd, SBX-20261110_154951-9079d30f) (`sync_memory.py` ([`Homunculus_Software.md`](../Homunculus_Software.md)), `homunculus_paths.py` ([`Homunculus_Software.md`](../Homunculus_Software.md)), `audit_data_boundary.py` ([`Homunculus_Software.md`](../Homunculus_Software.md))).

---

### `LL-044` [TIER3] — A 59-probe memory stress benchmark exposed 6 zero-hit blind spots (compound words, accented tokens... (`2026-11-11`)
- **Symptom / Trap:** A 59-probe memory stress benchmark exposed 6 zero-hit blind spots (compound words, accented tokens, typos), 45.3% Top-1 misses on multi-memory collisions, 47 blind-context packets omitting matched terms, TIER0 file-order slot cannibalization, and 1-line archive rows falsely tripping the 320-line bloat cap.
- **Root Cause:** Flat 1.0x BM25 treated body filler equally to headings, character 3-gram cosine suffered length dilution, unconditional TIER0 injection stole Top-K slots and truncated past two entries, --preflight weighted neighbor scripts equally, and HOT_MEMORY_BLOAT_CEILING counted 1-line archived table rows alongside active sections.
- **Verified Resolution & Permanent Guardrail:** Deployed 17_Combo_C9_HeldT0 + Option A TIER0 Two-Lane in sync_memory.py (BM25F 2.5x/1.5x/1.0x, word-trigram Dice>=0.52, strict 0.0 numeric weight, relevance-sorted TIER0[:3] with ID-only unmatched line + --kickstart TIER0 capsules, S3 Adaptive Top-K 3..6, S5 submodular MMR, S6_Budgeted <=1,350c GUARDRAIL CONTEXT ONLY hydration, D-3A duty_char_budgets (2,200c radar, 7,200c recall packet, 12,000c cold kickstart), active-only bloat cap <=12 sections/<=320 active lines) and Check #7c [BARE_NUMERIC_SHORTHAND_NOUN_MISSING] in audit_repo_docs.py (SBX-20261111_082207-2d5504ac, VRF-f899f601bef3). (`skills/project-memory/scripts/sync_memory.py` ([`Homunculus_Software.md`](../Homunculus_Software.md)), `skills/doc-and-card-studio/scripts/audit_repo_docs.py` ([`Homunculus_Software.md`](../Homunculus_Software.md)), `scripts/script_contracts.json` ([`Homunculus_Software.md`](../Homunculus_Software.md)), `tests/test_project_memory.py` ([`Homunculus_Software.md`](../Homunculus_Software.md))).

---

### `LL-045` [TIER3] — Cold-start Turn-1 read-only task portfolio triage triggered multi-turn shell permission loops because CWD... (`2026-11-11`)
- **Symptom / Trap:** Cold-start Turn-1 read-only task portfolio triage triggered multi-turn shell permission loops because CWD outside the engineering umbrella missed .homunculus.json and AUTO-ROLLUP tables lacked git checkpoints and handoff pulses
- **Root Cause:** resolve_workspace_config stopped at the first .homunculus.json without umbrella fallback when memory_dir was absent, query_project_section only emitted 3-column task counts, and co-engineering-partner routed read-only portfolio triage through shell CLI calls
- **Verified Resolution & Permanent Guardrail:** Added multi-level .homunculus.json umbrella fallback preserving standalone client non-hijack in homunculus_paths.py, expanded entity-isolated AUTO-ROLLUP tables in sync_memory.py with live checkpoints plus entity-safe relative link rewriting, and split zero-shell read_file Turn-1 portfolio triage from --kickstart project work within rule byte caps (`scripts/homunculus_paths.py` ([`Homunculus_Software.md`](../Homunculus_Software.md)), `skills/project-memory/scripts/sync_memory.py` ([`Homunculus_Software.md`](../Homunculus_Software.md)), `rules/co-engineering-partner.md` ([`Homunculus.md`](../Homunculus.md)), `skills/project-memory/SKILL.md` ([`Homunculus.md`](../Homunculus.md)) (`SBX-20261111_110421-e810b0f0`)).

---

### `LL-047` [TIER3] — Consumer skill and add-on iterations risked splash-unlocking core memory scripts out of convenience... (`2026-11-11`)
- **Symptom / Trap:** Consumer skill and add-on iterations risked splash-unlocking core memory scripts out of convenience, non-sync subcommands in memory_gateway.py initially deferred kernel seal checks until sync_memory loading, and extension-based executable chmod locking dirtied git fileMode status.
- **Root Cause:** Blanket core unlock mechanics lived in always-on prompts without privilege ring separation or a multi-lens extension SDK, gateway seal verification only ran inside _load_sync_memory, and _set_file_lock_mode forced executable bits onto non-executable Python scripts.
- **Verified Resolution & Permanent Guardrail:** Enforce Three-Ring isolation with kernel_seal.json and sudo-only Ring-Zero leases, execute _enforce_gateway_kernel_seal across main and resolve_memory_root in memory_gateway.py, block direct Ring-One and Ring-Two sync_memory imports or vault writes via AST BYPASSED_MEMORY_GATEWAY in audit_skill_hygiene.py, and preserve existing executable bits in _set_file_lock_mode. (`scripts/homunculus_paths.py` ([`Homunculus_Software.md`](../Homunculus_Software.md)), `scripts/memory_gateway.py` ([`Homunculus_Software.md`](../Homunculus_Software.md)), `skills/skill-architect/scripts/audit_skill_hygiene.py` ([`Homunculus_Software.md`](../Homunculus_Software.md)), `skills/project-memory/scripts/sync_memory.py` ([`Homunculus_Software.md`](../Homunculus_Software.md)) (`SBX-20261111_191946-190fb4b6`)).

---

### `LL-048` [TIER3] — Direct <memory_root> file writes in teach_brief.py bypassed MEMORY_SDK_V1 AST gates, read-only flags... (`2026-11-12`)
- **Symptom / Trap:** Direct <memory_root> file writes in teach_brief.py bypassed MEMORY_SDK_V1 AST gates, read-only flags recreated Directory/, flash tags downgraded score>=2 queries, and compound modifiers truncated trailing head nouns.
- **Root Cause:** Pre-v0.3.0 teach_brief.py wrote raw Markdown to Standards_and_Specs/ and Lessons_Learned.md without memory_gateway.py, called ensure_directory_fresh() unconditionally in main(), omitted --query, and broke _pack_tokens() on compound modifiers.
- **Verified Resolution & Permanent Guardrail:** Route all teach-me promotions and context seeds exclusively through memory_gateway.py (MEMORY_SDK_V1) with atomic rollback, gate Directory/ sync to promote_document, enforce max(Trigger_Floor, Inline_Tag) + require_depth=True, slice 60-word theory strictly from H2 Section 1, and snap >=14-char compound modifiers before trailing nouns. (`skills/teach-me/scripts/teach_brief.py` ([`Homunculus_Software.md`](../Homunculus_Software.md)), `skills/teach-me/SKILL.md` ([`Homunculus.md`](../Homunculus.md)), `skills/teach-me/references/brief_authoring_playbook.md` ([`Homunculus.md`](../Homunculus.md)), `tests/test_teach_me.py` ([`Homunculus_Software.md`](../Homunculus_Software.md)) (`SBX-20261112_074727-9c5fafef`)).

- **Scope:** `skill:teach-me`
---
