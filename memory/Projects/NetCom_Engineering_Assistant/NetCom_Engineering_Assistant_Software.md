---
project: "NetCom_Engineering_Assistant"
entity: "NetCom"
compartment: "private"
telemetry_domain: "software"
local_path: "/home/orin/Projects/Engineering/NEA_v2.2.3"
inventory_sha256: "e07c957c0975"
last_synced: "2026-11-05"
---

# NetCom_Engineering_Assistant — Software, CLI & Schema Telemetry (`_Software.md`)

> **Authoritative Software Truth Ledger (`sync_software_telemetry`)**: Populated via `sync_memory.py --sync-software --project NetCom_Engineering_Assistant`. Used by `verify_claims.py` as primary software/CLI/schema ground truth for `NetCom_Engineering_Assistant` (`entity: NetCom`).

---

## 1. Runtime Entrypoints & Module Inventory

<!-- AUTO-SOFTWARE-MODULES:START -->
| Script / Module Path | Language / Runtime | CLI Flags / Public Symbols | Line Count | SHA-256 Prefix |
| :--- | :--- | :--- | :--- | :--- |
| `Scripts/build_copilot_agents.py` | `Python 3.10+` | Symbols: `build_agent_skills()`, `write_deployment_guide()`, `sync_shared_knowledge_files()`, `build_all_agents()`, `verify_deployment_contract()` | `1111` | `6f00b063e6` |
| `Scripts/inspect_nea_workbooks.py` | `Python 3.10+` | Flags: `target_dir`, `--scope`, `--consolidate`, `--template`, `--out`, `--lookup` — Symbols: `parse_xlsx()`, `cell_val()`, `cell_info()`, `fmt_num()`, `excel_serial_to_iso()` | `3998` | `2af31ee888` |
| `Scripts/package_nea_delivery.py` | `Python 3.10+` | Symbols: `clean_stale_downloads()`, `sync_script_mirrors_and_agents()`, `build_package()` | `65` | `e1d8be29a5` |
| `Skills/nea-anti-hallucination/scripts/inspect_nea_workbooks.py` | `Python 3.10+` | Flags: `target_dir`, `--scope`, `--consolidate`, `--template`, `--out`, `--lookup` — Symbols: `parse_xlsx()`, `cell_val()`, `cell_info()`, `fmt_num()`, `excel_serial_to_iso()` | `3998` | `2af31ee888` |
| `Skills/nea-verification-and-receipt/scripts/inspect_nea_workbooks.py` | `Python 3.10+` | Flags: `target_dir`, `--scope`, `--consolidate`, `--template`, `--out`, `--lookup` — Symbols: `parse_xlsx()`, `cell_val()`, `cell_info()`, `fmt_num()`, `excel_serial_to_iso()` | `3998` | `2af31ee888` |
| `Skills/nea-workbook-entry-guard/scripts/inspect_nea_workbooks.py` | `Python 3.10+` | Flags: `target_dir`, `--scope`, `--consolidate`, `--template`, `--out`, `--lookup` — Symbols: `parse_xlsx()`, `cell_val()`, `cell_info()`, `fmt_num()`, `excel_serial_to_iso()` | `3998` | `2af31ee888` |
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

| Test Suite / Gate | Command | Last Verified Result | Receipt / Anchor |
| :--- | :--- | :--- | :--- |
| Unit Test Suite | `python3 -m unittest discover -s tests -v` | `[TBD: test_status]` | `[TBD: receipt_id]` |
