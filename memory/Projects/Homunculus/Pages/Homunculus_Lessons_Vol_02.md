---
project: "Homunculus"
parent_note: "Homunculus_Lessons_Learned"
entity: "Alchemical-3D"
compartment: "cleanroom"
note_type: "lessons_learned_page"
volume: 2
last_synced: "2026-11-18"
---
# Homunculus — Lessons Learned — Volume 02

> **Paginated Continuation of [`Homunculus_Lessons_Learned.md`](../Homunculus_Lessons_Learned.md)**

---

## 2. Active Lessons Continuation (`TIER0` & `TIER2`)

### `LL-053` [TIER2] — Remote turnkeys burned before ssh-keygen -Y lease signing, _is_ignored_ring_artifact filtered .cache... (`2026-11-16`)
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
