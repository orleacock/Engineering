# NEA v2.2.3 — Skills Deployment Guide (`<skill-name>.zip` with Bundled `scripts/inspect_nea_workbooks.py`)

In Microsoft 365 Copilot Agent Builder, **Skills** are uploaded directly as `.zip` packages (`Configure` $\rightarrow$ `Skills` $\rightarrow$ `Add skill` $\rightarrow$ upload `<skill-name>.zip`).

Per Microsoft's official Declarative Agent Skills specification, each folder under `Skills/<skill-name>/` contains:
1. **`<skill-name>.zip`**: Pre-packaged archive containing root-level `SKILL.md` plus `scripts/inspect_nea_workbooks.py` so the agent's Code Interpreter environment has direct local access to the deterministic OpenXML inspection, lookup, repair, and receipt engine.
2. **`SKILL.md` & `scripts/inspect_nea_workbooks.py`**: Unpacked copies for local inspection.

```text
<skill-name>.zip
├── SKILL.md
└── scripts/
    └── inspect_nea_workbooks.py
```

## Skill Inventory & Agent Mapping

| Skill Name | Upload Archive Path | Attach To | Size (`SKILL.md`) | Bundled Files in `.zip` |
| :--- | :--- | :--- | :---: | :--- |
| `nea-anti-hallucination` | `Skills/nea-anti-hallucination/nea-anti-hallucination.zip` | All 6 NEA Agents | `7187 / 8,000` chars | `SKILL.md` + `scripts/inspect_nea_workbooks.py` |
| `nea-workbook-entry-guard` | `Skills/nea-workbook-entry-guard/nea-workbook-entry-guard.zip` | 5 Mode-2 Agents (BOM Builder, CRL Builder, Catalog Manager, Repair Tool, Timesheet Consolidator) | `6116 / 8,000` chars | `SKILL.md` + `scripts/inspect_nea_workbooks.py` |
| `nea-verification-and-receipt` | `Skills/nea-verification-and-receipt/nea-verification-and-receipt.zip` | All 6 NEA Agents | `6028 / 8,000` chars | `SKILL.md` + `scripts/inspect_nea_workbooks.py` |

---

## Which Skills Should You Upload to Each Agent?

- **All 6 NEA Agents**:
  - Upload `Skills/nea-anti-hallucination/nea-anti-hallucination.zip` and `Skills/nea-verification-and-receipt/nea-verification-and-receipt.zip`.
- **The 5 Mode-2 Builder / Catalog / Repair / Timesheet Agents** (`NEA BOM Builder`, `NEA CRL Builder`, `NEA Catalog Manager`, `NEA Repair Tool`, and `NEA Timesheet Consolidator`):
  - Also upload `Skills/nea-workbook-entry-guard/nea-workbook-entry-guard.zip`.
