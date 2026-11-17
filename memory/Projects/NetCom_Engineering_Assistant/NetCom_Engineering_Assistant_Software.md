---
project: "NetCom_Engineering_Assistant"
entity: "NetCom"
compartment: "private"
telemetry_domain: "software"
local_path: "/home/orin/Projects/Engineering/NEA_v2.2.3"
inventory_sha256: "db1956669ebb"
last_synced: "2026-11-17"
---

# NetCom_Engineering_Assistant — Software, CLI & Schema Telemetry (`_Software.md`)

> **Authoritative Software Truth Ledger (`sync_software_telemetry`)**: Populated via `sync_memory.py --sync-software --project NetCom_Engineering_Assistant`. Used by `verify_claims.py` as primary software/CLI/schema ground truth for `NetCom_Engineering_Assistant` (`entity: NetCom`).

---

## 1. Runtime Entrypoints & Module Inventory

<!-- AUTO-SOFTWARE-MODULES:START -->
| Script / Module Path | Language / Runtime | CLI Flags / Public Symbols | Line Count | SHA-256 Prefix |
| :--- | :--- | :--- | :--- | :--- |
| `Scripts/build_copilot_agents.py` | `Python 3.10+` | Symbols: `build_agent_skills()` (`#L648-L814`), `write_deployment_guide()` (`#L817-L889`), `sync_shared_knowledge_files()` (`#L892-L911`), `build_all_agents()` (`#L914-L1040`), `verify_deployment_contract()` (`#L1043-L1144`) | `1148` | `16aec2d9c9` |
| `Scripts/edit_nea_workbooks.py` | `Python 3.10+` | Flags: `orig_xlsx`, `--manifest`, `--out`, `--dry-run`, `--allow-pending`, `--schema` — Symbols: `apply_workbook_edits()` (`#L778-L885`), `main()` (`#L934-L978`) | `982` | `ee7051c693` |
| `Scripts/inspect_nea_workbooks.py` | `Python 3.10+` | Flags: `target_dir`, `--scope`, `--consolidate`, `--template`, `--out`, `--lookup`, `--verify-write`, `--repair`, `--out-dir`, `--cache-file` — Symbols: `parse_xlsx()` (`#L35-L174`), `cell_val()` (`#L177-L178`), `cell_info()` (`#L181-L191`), `fmt_num()` (`#L194-L199`), `excel_serial_to_iso()` (`#L202-L212`), `SharedStringTable()` (`#L858-L899`), `build_weekly_summary_sheet_xml()` (`#L1172-L1450`), `build_job_summary_sheet_xml()` (`#L1453-L1758`), `main()` (`#L2782-L4087`) | `4091` | `be9cc070fd` |
| `Scripts/package_nea_delivery.py` | `Python 3.10+` | Symbols: `clean_stale_downloads()` (`#L22-L34`), `sync_script_mirrors_and_agents()` (`#L37-L39`), `build_package()` (`#L42-L61`) | `65` | `52e196a3e7` |
| `Skills/nea-anti-hallucination/scripts/inspect_nea_workbooks.py` | `Python 3.10+` | Flags: `target_dir`, `--scope`, `--consolidate`, `--template`, `--out`, `--lookup`, `--verify-write`, `--repair`, `--out-dir`, `--cache-file` — Symbols: `parse_xlsx()` (`#L35-L174`), `cell_val()` (`#L177-L178`), `cell_info()` (`#L181-L191`), `fmt_num()` (`#L194-L199`), `excel_serial_to_iso()` (`#L202-L212`), `SharedStringTable()` (`#L858-L899`), `build_weekly_summary_sheet_xml()` (`#L1172-L1450`), `build_job_summary_sheet_xml()` (`#L1453-L1758`), `main()` (`#L2782-L4087`) | `4091` | `be9cc070fd` |
| `Skills/nea-verification-and-receipt/scripts/inspect_nea_workbooks.py` | `Python 3.10+` | Flags: `target_dir`, `--scope`, `--consolidate`, `--template`, `--out`, `--lookup`, `--verify-write`, `--repair`, `--out-dir`, `--cache-file` — Symbols: `parse_xlsx()` (`#L35-L174`), `cell_val()` (`#L177-L178`), `cell_info()` (`#L181-L191`), `fmt_num()` (`#L194-L199`), `excel_serial_to_iso()` (`#L202-L212`), `SharedStringTable()` (`#L858-L899`), `build_weekly_summary_sheet_xml()` (`#L1172-L1450`), `build_job_summary_sheet_xml()` (`#L1453-L1758`), `main()` (`#L2782-L4087`) | `4091` | `be9cc070fd` |
| `Skills/nea-workbook-entry-guard/scripts/edit_nea_workbooks.py` | `Python 3.10+` | Flags: `orig_xlsx`, `--manifest`, `--out`, `--dry-run`, `--allow-pending`, `--schema` — Symbols: `apply_workbook_edits()` (`#L778-L885`), `main()` (`#L934-L978`) | `982` | `ee7051c693` |
| `Skills/nea-workbook-entry-guard/scripts/inspect_nea_workbooks.py` | `Python 3.10+` | Flags: `target_dir`, `--scope`, `--consolidate`, `--template`, `--out`, `--lookup`, `--verify-write`, `--repair`, `--out-dir`, `--cache-file` — Symbols: `parse_xlsx()` (`#L35-L174`), `cell_val()` (`#L177-L178`), `cell_info()` (`#L181-L191`), `fmt_num()` (`#L194-L199`), `excel_serial_to_iso()` (`#L202-L212`), `SharedStringTable()` (`#L858-L899`), `build_weekly_summary_sheet_xml()` (`#L1172-L1450`), `build_job_summary_sheet_xml()` (`#L1453-L1758`), `main()` (`#L2782-L4087`) | `4091` | `be9cc070fd` |
<!-- AUTO-SOFTWARE-MODULES:END -->

---

## 2. Configuration Schemas & Data Contracts

<!-- AUTO-SOFTWARE-SCHEMAS:START -->
| Schema / Config File | Format | Top-Level Keys / Contract Version | SHA-256 Prefix |
| :--- | :--- | :--- | :--- |
| *(No JSON/config schemas found in repository)* | — | — | — |
<!-- AUTO-SOFTWARE-SCHEMAS:END -->

---

## 3. Deterministic Test & Verification Receipts

<!-- AUTO-SOFTWARE-TESTS:START -->
| Test File | Test Classes | AST test_* Count | SHA-256 Prefix |
| :--- | :--- | :---: | :---: |
| *(No `test_*.py` suites indexed yet)* | — | `0` | — |
<!-- AUTO-SOFTWARE-TESTS:END -->
