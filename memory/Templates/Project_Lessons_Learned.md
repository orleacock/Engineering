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

## 1. Lessons Learned Ledger (`Symptom -> Root Cause -> Guardrail`)

| ID | Date | Symptom / Failure Observed | Root Cause | Permanent Guardrail / Rule or Code Fix | Verification Anchor |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `LL-01` | `{{DATE}}` | *(Record first observed failure or edge case)* | *(Underlying structural cause)* | *(Deterministic check, test, or design update added)* | [`{{PROJECT}}.md`]({{PROJECT}}.md) |

---

## 2. Architectural Decision Records (`ADR`)

### `ADR-01`: Initial Project Architecture (`{{DATE}}`)
- **Context**: Initial repository and memory scaffolding for `{{PROJECT}}` (`project_type: {{PROJECT_TYPE}}`).
- **Decision**: Governed under Homunculus Governing Priority Law (`1. Accuracy & Truth -> 2. Efficiency -> 3. Data Safety -> 4. Speed`) with strict `entity: {{ENTITY}}` isolation.
- **Consequences**: All quantitative claims require primary source anchors or explicit `[TBD: ...]` tags; unverified notes remain isolated in [`Quarantine/`](Quarantine/Quarantine_README.md).
