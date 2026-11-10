---
project: "{{PROJECT}}"
entity: "{{ENTITY}}"
compartment: "{{COMPARTMENT}}"
note_type: "lessons_learned"
last_synced: "{{DATE}}"
---

# {{PROJECT}} — Engineering Lessons Learned & Architectural Decisions

> **Root-Cause Memory Ledger (`entity: {{ENTITY}}`)**: Every foundational flaw discovered during design, fabrication, debugging, or testing is recorded here using the **Symptom $\rightarrow$ Root Cause $\rightarrow$ Permanent Guardrail** protocol so solved problems never regress.

---

## 0. Subsystem Rebuild & Invariant Matrix (`Sectional Rebuild Reference`)

> **Sectional Rebuild Gate**: Before refactoring, de-bloating, or sectionally rebuilding any module or assembly in `{{PROJECT}}`, check this table (`sync_memory.py --project {{PROJECT}} --invariants`) so **Must-Keep Invariants (`Chesterton's Fence`)** are preserved and **Retired Bloat / Anti-Patterns (`Never Re-Add`)** are never re-implemented.

<!-- SUBSYSTEM-INVARIANTS:START -->
| Subsystem / Module | Must-Keep Invariants (`Chesterton's Fence`) | Retired Bloat / Anti-Patterns (`Never Re-Add`) | Canonical Owner |
| :--- | :--- | :--- | :--- |
| `{{PROJECT}}` Core (`{{PROJECT_TYPE}}`) | Enforce `entity: {{ENTITY}}` (`compartment: {{COMPARTMENT}}`) isolation, source-backed quantitative claims (`verify_claims.py`), and `Quarantine/` holding separation. | Guessing undocumented specifications from pretraining defaults or borrowing parameters across distinct entities/materials. | [`{{PROJECT}}.md`]({{PROJECT}}.md) |
<!-- SUBSYSTEM-INVARIANTS:END -->

---

## 1. Lessons Learned Ledger (`Symptom -> Root Cause -> Guardrail`)

| ID | Date | Symptom / Failure Observed | Root Cause | Permanent Guardrail / Rule or Code Fix | Verification Anchor |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `LL-01` | `{{DATE}}` | Initial Dual-Mode Memory onboarding and compartment boundary initialization for `{{PROJECT}}` | Unindexed repositories risk blind `ls`/`find` reconnaissance and unverified specification drift | Scaffolded `{{PROJECT}}` hub dossier, domain telemetry, `Quarantine/`, and `SUBSYSTEM-INVARIANTS` baseline under `entity: {{ENTITY}}` (`{{COMPARTMENT}}`) | [`{{PROJECT}}.md`]({{PROJECT}}.md) |

### `LL-01` [TIER2] — Initial Dual-Mode Memory Onboarding & Compartment Boundary Initialization (`{{DATE}}`)
- **Symptom / Trap:** Initial Dual-Mode Memory onboarding and compartment boundary initialization for `{{PROJECT}}`.
- **Root Cause:** Unindexed repositories risk blind `ls`/`find` reconnaissance and unverified specification drift.
- **Verified Resolution & Permanent Guardrail:** Scaffolded `{{PROJECT}}` hub dossier, domain telemetry, `Quarantine/`, and `SUBSYSTEM-INVARIANTS` baseline under `entity: {{ENTITY}}` (`{{COMPARTMENT}}`; [`{{PROJECT}}.md`]({{PROJECT}}.md)).

---

## 2. Architectural Decision Records (`ADR`)

### `ADR-01`: Initial Project Architecture (`{{DATE}}`)
- **Context**: Initial repository and memory scaffolding for `{{PROJECT}}` (`project_type: {{PROJECT_TYPE}}`).
- **Decision**: Governed under Homunculus Governing Priority Law (`1. Accuracy & Truth -> 2. Efficiency -> 3. Data Safety -> 4. Speed`) with strict `entity: {{ENTITY}}` isolation.
- **Consequences**: All quantitative claims require primary source anchors or explicit `[TBD: ...]` tags; unverified notes remain isolated in [`Quarantine/`](Quarantine/Quarantine_README.md).
