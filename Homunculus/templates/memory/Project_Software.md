---
project: "{{PROJECT}}"
entity: "{{ENTITY}}"
compartment: "{{COMPARTMENT}}"
telemetry_domain: "software"
local_path: "{{LOCAL_PATH}}"
inventory_sha256: "{{INVENTORY_SHA256}}"
last_synced: "{{DATE}}"
---

# {{PROJECT}} — Software, CLI & Schema Telemetry (`_Software.md`)

> **Authoritative Software Truth Ledger (`sync_software_telemetry`)**: Populated via `sync_memory.py --sync-software --project {{PROJECT}}`. Used by `verify_claims.py` as primary software/CLI/schema ground truth for `{{PROJECT}}` (`entity: {{ENTITY}}`).

---

## 1. Runtime Entrypoints & Module Inventory

<!-- AUTO-SOFTWARE-MODULES:START -->
| Script / Module Path | Language / Runtime | CLI Flags / Public Symbols | Line Count | SHA-256 Prefix |
| :--- | :--- | :--- | :--- | :--- |
| *(No software modules indexed yet)* | — | — | — | — |
<!-- AUTO-SOFTWARE-MODULES:END -->

---

## 2. Configuration Schemas & Data Contracts

<!-- AUTO-SOFTWARE-SCHEMAS:START -->
| Schema / Config File | Format | Top-Level Keys / Contract Version | SHA-256 Prefix |
| :--- | :--- | :--- | :--- |
| *(No configuration schemas indexed yet)* | — | — | — |
<!-- AUTO-SOFTWARE-SCHEMAS:END -->

---

## 3. Deterministic Test & Verification Receipts

| Test Suite / Gate | Command | Last Verified Result | Receipt / Anchor |
| :--- | :--- | :--- | :--- |
| *(No verified test receipt recorded yet)* | `python3 -m unittest discover -s tests -v` | — | — |
