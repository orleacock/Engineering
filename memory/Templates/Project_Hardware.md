---
project: "{{PROJECT}}"
entity: "{{ENTITY}}"
compartment: "{{COMPARTMENT}}"
telemetry_domain: "hardware"
local_path: "{{LOCAL_PATH}}"
inventory_sha256: "{{INVENTORY_SHA256}}"
last_synced: "{{DATE}}"
---

# {{PROJECT}} — Hardware, CAD & Firmware Telemetry (`_Hardware.md`)

> **Authoritative Hardware Truth Ledger (`sync_hardware_telemetry`)**: Populated via `sync_memory.py --sync-hardware --project {{PROJECT}}` (and `inspect_hardware_ecosystem.py`). Used by `verify_claims.py` as primary physical/electronic ground truth for `{{PROJECT}}` (`entity: {{ENTITY}}`).

---

## 1. CAD Geometry & Bounding-Box Inventory (`.step` / `.stl` / `.3mf`)

<!-- AUTO-HARDWARE-CAD:START -->
| File Path | Format | Bounding Box (`X x Y x Z mm`) | Cylindrical Bore / Feature Summary | SHA-256 Prefix |
| :--- | :--- | :--- | :--- | :--- |
| *(No CAD files indexed yet)* | — | — | — | — |
<!-- AUTO-HARDWARE-CAD:END -->

---

## 2. Firmware, Pinout & Electronics Configuration (`.cfg` / `.kicad_pcb` / `.sch`)

<!-- AUTO-HARDWARE-CFG:START -->
| Config / Schematic File | Section / Component | Parameter / Pin | Verified Value | Line Anchor |
| :--- | :--- | :--- | :--- | :--- |
| *(No hardware config files indexed yet)* | — | — | — | — |
<!-- AUTO-HARDWARE-CFG:END -->

---

## 3. Verified Fasteners, Inserts & BOM Schedule

<!-- AUTO-HARDWARE-BOM:START -->
| Sub-Assembly / Category | Fastener / Component Spec | Verified Qty | Source Anchor (`path#Lstart-Lend`) | Notes |
| :--- | :--- | :--- | :--- | :--- |
| *(No verified BOM.md table synced yet — run `--sync-hardware` once `BOM.md` is clean)* | — | — | — | — |
<!-- AUTO-HARDWARE-BOM:END -->
