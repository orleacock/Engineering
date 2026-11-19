---
project: "Homunculus"
parent_note: "Homunculus_Lessons_Learned"
entity: "Alchemical-3D"
compartment: "cleanroom"
note_type: "lessons_learned_page"
volume: 2
last_synced: "2026-11-19"
---
# Homunculus — Lessons Learned — Volume 02

> **Paginated Continuation of [`Homunculus_Lessons_Learned.md`](../Homunculus_Lessons_Learned.md)**

---

## 2. Active Lessons Continuation (`TIER0` & `TIER2`)

### `LL-052` [TIER2] [TRAP] — Repeated single-target verify_claims runs rebuilt SourceIndex on unchanged sources, top-level Quarantine... (`2026-11-14`)
- **Symptom / Trap:** Repeated single-target verify_claims runs rebuilt SourceIndex on unchanged sources, top-level Quarantine paths lacked a schema or gateway door, boundary scans re-hashed duplicate tokens, and backticked rule examples inflated TBD counts.
- **Root Cause:** verify_claims lacked a pure-JSON SourceIndex cache and multi-target CLI, memory_gateway lacked a per-project quarantine-note writer and TOP_LEVEL_QUARANTINE_FORBIDDEN audit, and sync_memory lacked INERT_META_TBD_RE backtick parity.
- **Verified Resolution & Permanent Guardrail:** Ship fail-closed pure-JSON SourceIndex caching (--no-cache / HOMUNCULUS_DISABLE_FASTPATH=1) + multi-target --target, per-project QUARANTINE_NOTE_V1 + memory_gateway quarantine-note + TOP_LEVEL_QUARANTINE_FORBIDDEN, combined regex/seen_clean_tokens prefilters, and INERT_META_TBD_RE parity. (`skills/claim-verification/scripts/verify_claims.py` ([`Homunculus_Software.md`](../Homunculus_Software.md)), `scripts/memory_gateway.py` ([`Homunculus_Software.md`](../Homunculus_Software.md)), `skills/project-memory/scripts/sync_memory.py` ([`Homunculus_Software.md`](../Homunculus_Software.md)), `skills/skill-architect/scripts/audit_skill_hygiene.py` ([`Homunculus_Software.md`](../Homunculus_Software.md)) (`SBX-20261114_153225-b191d46c`)).

---

### `LL-053` [TIER2] [TRAP] — Remote turnkeys burned before ssh-keygen -Y lease signing, _is_ignored_ring_artifact filtered .cache... (`2026-11-16`)
- **Scope:** `script:homunculus_paths`
- **Symptom / Trap:** Remote turnkeys burned before ssh-keygen -Y lease signing, _is_ignored_ring_artifact filtered .cache ancestor CoW clones via absolute parts, and format_model_receipt_tag hid [medium]/[xhigh] via substring check
- **Root Cause:** _require_interactive_tty_if_needed burned turnkeys before OpenSSH signing, _is_ignored_ring_artifact inspected absolute p.parts instead of p.relative_to(fw_root), and format_model_receipt_tag checked effort not in base instead of f'[{effort}]' not in base
- **Verified Resolution & Permanent Guardrail:** Defer remote turnkey burn until post-sign success via defer_turnkey_burn=True across homunculus_paths.py and seal_memory_governance(), evaluate .cache ignores relative to fw_root, pass resolved_effort into format_model_receipt_tag, and seal BUILTIN_RING1 updates via h-sudo seal (`scripts/homunculus_paths.py` ([`Homunculus_Software.md`](../Homunculus_Software.md)), `skills/engineering-sandbox/scripts/sandbox_runner.py` ([`Homunculus_Software.md`](../Homunculus_Software.md)), `skills/project-memory/scripts/sync_memory.py` ([`Homunculus_Software.md`](../Homunculus_Software.md)), `skills/teach-me/scripts/teach_brief.py` ([`Homunculus_Software.md`](../Homunculus_Software.md)) (`SBX-20261116_152151-07f6b24f / 82/82 OK`)).

---

### `LL-054` [TIER2] [WIN] — Historical lessons risked in-place edits or dead repo anchors across refactors, fallback verify_claims... (`2026-11-18`)
- **Bottleneck / Challenge:** Historical lessons risked in-place edits or dead repo anchors across refactors, fallback verify_claims provenance scanned unindexed memory folders, sandbox_runner counted target repo .py reads as oracle snoops, and audit_portability scanned gitignored .cache runtime files
- **Mechanism & Measured Gain:** Memory lacked a Ring-0 anti-poisoning auditor, 4-archetype lineage supersession, and sanitized Principles/ hub, while verify_claims, sandbox_runner, and audit_portability needed strict folder/path scoping
- **Reusable Pattern & Integration Blueprint:** Enforce Ring-0 skills/memory-hygiene/scripts/audit_memory_hygiene.py (--check-commit and --audit --suggest-promotions), skills/project-memory/scripts/sync_memory.py (atomic read-only chmod permission (0444) TIER5 --supersede-lesson with Historical Context (Inert Origin) and mutual --promote-principle gated by PRINCIPLE_ENTITY_BLEED_BLOCKED and restricted chmod permission (0600) Directory/lineage_registry.json), unindexed memory subdir isolation plus 1-parameter-per-[TBD] in skills/claim-verification/scripts/verify_claims.py, Homunculus-only py_oracles_read filtering in skills/engineering-sandbox/scripts/sandbox_runner.py, and explicit .cache runtime exemptions in scripts/audit_portability.py (`skills/memory-hygiene/scripts/audit_memory_hygiene.py` ([`Homunculus_Software.md`](../Homunculus_Software.md)), `scripts/homunculus_paths.py` ([`Homunculus_Software.md`](../Homunculus_Software.md)), `scripts/memory_gateway.py` ([`Homunculus_Software.md`](../Homunculus_Software.md)), `skills/skill-architect/scripts/audit_skill_hygiene.py` ([`Homunculus_Software.md`](../Homunculus_Software.md)) (`SBX-20261117_220646-3b90c82f / SBX-20261117_221011-142ecbac / 88/88 OK`)).

---

### `LL-055` [TIER0] [TRAP] — Introducing a middle Agent.md tier, exceeding the 24,000-byte AGENTS.md cap via out-of-tree rel_prefix... (`2026-11-18`)
- **Historical Context (Inert Origin):** Matured from LL-027 (2-Tier Single-Source Rule Architecture vs. 24,000-byte AGENTS.md cliff & symlink realpath resolution) to replace legacy shorthand skill paths.
- **Lineage:** Derived from `LL-027` ([`Archive/Homunculus_Lessons_Archive.md#L461-L476`](../Archive/Homunculus_Lessons_Archive.md#L461-L476))
- **Symptom / Trap:** Introducing a middle Agent.md tier, exceeding the 24,000-byte AGENTS.md cap via out-of-tree rel_prefix inflation, double-injecting .agents/rules/ + AGENTS.md, or using os.path.abspath(__file__) on symlinked skills broke adapter parity and rule loading.
- **Root Cause:** Adapter byte caps (22,500 B in-repo / 24,000 B hard cap), symlink os.path.realpath(__file__) resolution, prefer_copy/.zip homunculus_paths.py co-bundling, and pre-draft template slot retention were not previously enforced as fail-closed structural invariants.
- **Verified Resolution, Guardrail & Applicability Boundary:** Preserve the 2-Tier Single-Source Rule Architecture (AGENTS.md <= 22,500 B via RULE_BYTE_CAP_EXCEEDED, MISNAMED_AGENTS_MD_CASE, and ADAPTER_STALE_DRIFT in skills/skill-architect/scripts/audit_skill_hygiene.py and scripts/build_adapters.py), use Path(__file__).resolve() + homunculus_paths.py co-bundling across symlinks/copies/.zips, and retain pre-draft template rows + inline [TBD: CONFLICT — ...] tags in skills/doc-and-card-studio/SKILL.md (`rules/co-engineering-partner.md` ([`Homunculus.md`](../Homunculus.md)), `scripts/homunculus_paths.py` ([`Homunculus_Software.md`](../Homunculus_Software.md)), `scripts/build_adapters.py` ([`Homunculus_Software.md`](../Homunculus_Software.md)), `skills/doc-and-card-studio/SKILL.md` ([`Homunculus.md`](../Homunculus.md)) (`SBX-20261107_115321-71b82997`)).

### `LL-060` [TIER2] [WIN] — Unscoped lesson caps saturated per-project TIER2 windows and mixed host-runtime rules into project or... (`2026-11-18`)
- **Bottleneck / Challenge:** Unscoped lesson caps saturated per-project TIER2 windows and mixed host-runtime rules into project or clean-room Principles ledgers.
- **Mechanism & Measured Gain:** Fixed 9-lesson ceilings and single-file ledgers forced premature retirement or mixed host-specific tool constraints with project-agnostic Principles.
- **Reusable Pattern & Integration Blueprint:** Ship Two-Shelf Option D+ paginated books (Principles/ Shelf 1A, Host_Runtime/ Shelf 1B, Pages/*_Vol_NN.md Shelf 2), tapered TIER2 gravity caps (12 unscoped / 6 per-scope / 30 total), design_intent MMR, Stage Z1 Host_Runtime/ source exclusion, and deterministic --migrate-option-d-plus migration. (`skills/project-memory/scripts/sync_memory.py` ([`Homunculus_Software.md`](../Homunculus_Software.md)), `skills/memory-hygiene/scripts/audit_memory_hygiene.py` ([`Homunculus_Software.md`](../Homunculus_Software.md)), `skills/skill-architect/scripts/audit_skill_hygiene.py` ([`Homunculus_Software.md`](../Homunculus_Software.md)), `skills/claim-verification/scripts/verify_claims.py` ([`Homunculus_Software.md`](../Homunculus_Software.md)) (`SBX-20261118_203920-eda0e867 / Compare-Light SBX-20261118_202914-134a8559`)).

### `LL-061` [TIER2] [TRAP] — Linking optional Host_Runtime in starter README breaks clean-init memory audits before --init-host-runtime... (`2026-11-19`)
- **Scope:** `script:sync_memory`
- **Symptom / Trap:** Linking optional Host_Runtime in starter README breaks clean-init memory audits before --init-host-runtime runs, add_project_lesson risks ID collisions and schema/metadata-bullet corruption against Option D+ pages, and add_host_runtime_lesson lacks a direct CLI flag.
- **Root Cause:** Memory_Map_README linked an optional file absent until Host_Runtime init, add_project_lesson did not scan Host_Runtime Migrated-From prefixes or detect 4-column slim tables, _slim_quick_lookup_table scraped metadata bullets into capsules, promote_cross_cutting_principle checked only Vol 1 files instead of paginated Pages/, and main() exposed only --init-host-runtime.
- **Verified Resolution & Permanent Guardrail:** Keep Host_Runtime unlinked in Memory_Map_README while linking conditionally in Directory_Index.md, scan Host_Runtime IDs and skip metadata bullets across Vol 1/Pages slim tables in sync_memory.py, and queue direct CLI write exposure for add_host_runtime_lesson so new host entries avoid waiting for --migrate-option-d-plus. (`templates/memory/Memory_Map_README.md` ([`Homunculus.md`](../Homunculus.md)), `skills/project-memory/scripts/sync_memory.py` ([`Homunculus_Software.md`](../Homunculus_Software.md)), `skills/project-memory/SKILL.md` ([`Homunculus.md`](../Homunculus.md)) (`SBX-20261118_203920-eda0e867`)).

### `LL-062` [TIER2] [TRADE-OFF] — Adding gemini-4-neon-high alongside carbon and banning auto-selection or fallback to... (`2026-11-19`)
- **Scope:** `skill:subagent-orchestrator`
- **Decision Context & Options:** Adding gemini-4-neon-high alongside carbon and banning auto-selection or fallback to gemini-pro-orchestrator* increased always-on rules and AGENTS.md by +221 B, while bwrap sandboxes mask host sudo_policy.json so --verify-seal reports seal_signing off inside isolated shells.
- **Why Chosen Path Won (& Cost Paid):** Gemini 4 Neon frontier escalation and non-Orchestrator portability constraints require explicit rule and skill guardrails, whereas standard sandboxes isolate host user-config directories that hold seal-signing policies.
- **Transferable Rule & Invalidation Boundary:** Keep always-on Neon and non-Orchestrator guardrails compact within the 22,500 B AGENTS.md cap (+221 B advisory tracked for Window 1 benchmark trim or Course D pin) and run homunculus_paths.py --verify-seal unsandboxed on host when verifying required OpenSSH signatures. (`rules/co-engineering-partner.md` ([`Homunculus.md`](../Homunculus.md)), `skills/subagent-orchestrator/SKILL.md` ([`Homunculus.md`](../Homunculus.md)), `skills/engineering-sandbox/SKILL.md` ([`Homunculus.md`](../Homunculus.md)), `scripts/homunculus_paths.py` ([`Homunculus_Software.md`](../Homunculus_Software.md)) (`94/94 unittest OK`)).

### `LL-063` [TIER2] [TRAP] — Same-basename files collided in SourceIndex across cold and JSON-cached lookups, unclosed open().read()... (`2026-11-19`)
- **Symptom / Trap:** Same-basename files collided in SourceIndex across cold and JSON-cached lookups, unclosed open().read() calls leaked ResourceWarnings, Vol-1-only promote skipped Pages volumes, and masked sandboxes overwrote seal_root_sha256 without OpenSSH signing
- **Root Cause:** SourceIndex.__init__ and _deserialize_source_index keyed only basename/abspath without trailing POSIX suffixes, promote_cross_cutting_principle ignored _iter_project_lesson_files(), _append_governance_audit_entry stripped ssh_signature before checking seal_signing mode, and add_project_lesson wrote Pages before Vol 1
- **Verified Resolution & Permanent Guardrail:** Register trailing POSIX path suffixes identically in SourceIndex.__init__ and _deserialize_source_index() with context-managed file opens; expose --add-host-runtime-lesson CLI; guard _append_governance_audit_entry() when seal_signing is off on signed seals; and roll back Pages on Vol 1 write failure (`skills/claim-verification/scripts/verify_claims.py` ([`Homunculus_Software.md`](../Homunculus_Software.md)), `skills/project-memory/scripts/sync_memory.py` ([`Homunculus_Software.md`](../Homunculus_Software.md)) (`SBX-20261119_115533-c88288ca`)).

### `LL-064` [TIER2] [TRADE-OFF] — Legacy flash model fallbacks routed subagents to sunsetting gemini-3.8-flash-tiered while swarm omitted... (`2026-11-19`)
- **Decision Context & Options:** Legacy flash model fallbacks routed subagents to sunsetting gemini-3.8-flash-tiered while swarm omitted lazy MCP tools and PreInvocation hooks and AGENTS.md carried a +221 B post-v0.3.7 byte delta
- **Why Chosen Path Won (& Cost Paid):** teach_brief.py and build_adapters.py still emitted or documented flash/pro tags, swarm workers lacked call_mcp_tool and PreInvocation injection, and co-engineering-partner.md held redundant routing phrasing
- **Transferable Rule & Invalidation Boundary:** Switch all routing, teach_brief.py outputs, badges ([TIER: HYD/NEON/CARB // *]), and swarm nesting checks off flash onto canonical Gemini 4 Hydrogen/Neon/Carbon IDs while keeping legacy flash/pro read-only input upgrades; document swarm (no MCP/hooks) vs invoke_subagent/agy -p tradeoffs; and apply Course B trim holding AGENTS.md at 15,102 B (13,656 B combined rules) (`rules/co-engineering-partner.md` ([`Homunculus.md`](../Homunculus.md)), `scripts/build_adapters.py` ([`Homunculus_Software.md`](../Homunculus_Software.md)), `skills/teach-me/scripts/teach_brief.py` ([`Homunculus_Software.md`](../Homunculus_Software.md)), `skills/subagent-orchestrator/SKILL.md` ([`Homunculus.md`](../Homunculus.md))).

### `LL-065` [TIER2] [TRAP] — Clean-room portability flagged multi-file Python packages lacking stem matches, while Entity_Directory.md... (`2026-11-19`)
- **Scope:** `subsys:audit_portability`
- **Symptom / Trap:** Clean-room portability flagged multi-file Python packages lacking stem matches, while Entity_Directory.md box trees exposed sibling-entity diagrams from shared Diagrams/ folders.
- **Root Cause:** audit_portability.py collected only .py file stems instead of package directory names holding __init__.py, and sync_directory_trees() filtered Projects/, Tasks/, and Directory/ but omitted Diagrams/ companion .md entity scoping.
- **Verified Resolution & Permanent Guardrail:** Include rel_parts[:-1] when __init__.py is present in audit_portability.py, and filter Diagrams/ in sync_directory_trees() via companion .md entity frontmatter. (scripts/audit_portability.py, skills/project-memory/scripts/sync_memory.py (SBX-20261119_161403-4dd809bf / 97/97 unittest OK) (`SBX-20261119_161403-4dd809bf; 97/97 unittest OK; portability 0 violations; kernel_seal verified`)).
