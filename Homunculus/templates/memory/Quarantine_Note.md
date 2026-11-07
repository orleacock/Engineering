---
project: "{{PROJECT}}"
entity: "{{ENTITY}}"
compartment: "{{COMPARTMENT}}"
quarantine: true
status: "unverified_quarantine"
last_synced: "{{DATE}}"
---

# {{PROJECT}} — Quarantine Holding Zone (`[QUARANTINED — DO NOT CITE AS FACT]`)

> [!CAUTION]
> **STRICT QUARANTINE GATE (`quarantine: true`)**:
> This directory (`Projects/{{PROJECT}}/Quarantine/`) and all files inside it hold **unverified scratch notes, preliminary vendor quotes, rough calculations, and unvetted external specifications**.
> - **AI Assistant & Subagents**: Never cite any number, rating, pinout, or relationship from `Quarantine/` as verified fact in production code, BOMs, or documentation.
> - **Verification Oracle (`verify_claims.py`)**: Automatically rejects or quarantines citations pointing into `Quarantine/`.
> - **Promotion Path**: Once an item below is empirically verified against primary CAD, code, or physical measurement, move it into [`{{PROJECT}}.md`](../{{PROJECT}}.md), `{{PROJECT}}_Hardware.md`, or `{{PROJECT}}_Software.md` with its primary source anchor.

---

## Unverified Scratchpad & Pending Vendor Quotes

- `[TBD: vendor_quote_or_scratch_spec]` — Record preliminary notes here without polluting verified telemetry tables.
