---
title: "NetCom — Zero-CLI Front-of-Decision Memory Router"
entity: "NetCom"
compartment: "private"
type: "decision-router"
authoritative: false
last_synced: "2026-11-11"
---

# 🧭 `NetCom` — Front-of-Decision Memory Router (`TIER0`–`TIER4`)

> **Zero-CLI & Turn-1 Decision Radar**: Maintained automatically by `sync_memory.py`. Lists `TIER0` pinned laws, `TIER1` subsystem invariants, and `1-Line Radar Capsules` for `NetCom` projects. Use `sync_memory.py --project <P> --recall "<query>"` in CLI sessions or scan this table directly in Zero-CLI web sessions.

---

## 1. `TIER0` Co-Engineering Decision Profile

1. **Accuracy & Truth (`#1`)**: Source-verified facts, dimensional math, and structural integrity supersede all else. Never trade truth or disable `verify_claims.py` for speed.
2. **Token & Turn Efficiency (`#2`)**: Eliminate wasted reads, blind directory scans, and mid-task churn via targeted front-of-decision radar capsules (`<= 450` tokens) and deferred `pre-commit-gate` batching.
3. **Data Safety (`#3`)**: Enforce compartment boundaries (`audit_data_boundary.py`), zero credential exposure, and strict `entity:` isolation.
4. **Execution Speed (`#4`)**: Achieve speed through first-pass accuracy, deterministic CLI oracles, and fast `Model: 'flash'` subagents.
- **Parent Workstation & Post-Install User Stations**: Absolute `local_path` bindings and local station indexes (`Directory/<Entity>_memory_index.json`) are first-class citizens. Never waste local turns scrubbing workstation paths from the private parent memory vault.
- **Shipped Clean-Room Deliverable (`Homunculus`)**: Must ship 100% generic (`0` parent paths, project names, or `LL-xxx` IDs). Only `TIER0` & `TIER1` engine-universal invariants (`scripts/script_contracts.json`, `#L1-L55` `Contract :` pointers, and `tests/test_*.py`) promote from the parent vault into the clean-room deliverable.

---

## 2. Project Lesson Radar Capsules (`TIER0`–`TIER4`)

### [`NetCom_Engineering_Assistant`](../Projects/NetCom_Engineering_Assistant/NetCom_Engineering_Assistant.md)

| ID | Tier | Location | Touched Files | 1-Line Radar Capsule |
| :--- | :---: | :--- | :--- | :--- |
| **`LL-NEA-01`** | `TIER2` | [`NetCom_Engineering_Assistant_Lessons_Learned.md#L35-L38`](../Projects/NetCom_Engineering_Assistant/NetCom_Engineering_Assistant_Lessons_Learned.md#L35-L38) | — | Overcoming M365 Copilot OneDrive Graph Latency & Ephemeral Container Boundaries -> Engineers upload live `.xlsx` deliverables **directly into the Copilot chat turn** (`+ Upload from device`), mounting exact bytes in `/mnt/data/` with `0` indexing latency; Mode 2 edits/repairs run `--verify-write ORIG EDITED` (`NEA-WRT-<12hex>`) inside Code Interpreter and return a downloadable `.xlsx` artifact in chat... |
| **`LL-NEA-02`** | `TIER2` | [`NetCom_Engineering_Assistant_Lessons_Learned.md#L40-L43`](../Projects/NetCom_Engineering_Assistant/NetCom_Engineering_Assistant_Lessons_Learned.md#L40-L43) | `build_copilot_agents.py` | Solving the `8,000`-Char Instruction Cap, `"2.2.3"` Semver Lock & `.txt` Knowledge Indexing -> `Scripts/build_copilot_agents.py` (`NEA-SCR-002`) compiles the **6-Agent Modular Specialist Suite** (`NEA_Package_Reviewer` `5,330` chars `66.6%`, `NEA_BOM_Builder` `3,820` chars `47.8%`, `NEA_CRL_Builder` `3,342` chars `41.8%`, `NEA_Catalog_Manager` `3,794` chars `47.4%`, `NEA_Repair_Tool` `3,607` chars `45.1%`... |
| **`LL-NEA-03`** | `TIER2` | [`NetCom_Engineering_Assistant_Lessons_Learned.md#L45-L48`](../Projects/NetCom_Engineering_Assistant/NetCom_Engineering_Assistant_Lessons_Learned.md#L45-L48) | `SKILL.md`, `build_copilot_agents.py`, `inspect_nea_workbooks.py` | Bundling `scripts/inspect_nea_workbooks.py` Inside Root-Level `<skill-name>.zip` Archives -> `Scripts/build_copilot_agents.py` packages all `9` skills under `Skills/<skill-name>/<skill-name>.zip` with bundled `scripts/inspect_nea_workbooks.py`—verified across `5`-agent parallel cold-start blind swarms and `NEA Timesheet Consolidator` `Blind-Light` (`24831c6b`) with `0` custom OpenXML parser code written... |
| **`LL-NEA-04`** | `TIER2` | [`NetCom_Engineering_Assistant_Lessons_Learned.md#L50-L53`](../Projects/NetCom_Engineering_Assistant/NetCom_Engineering_Assistant_Lessons_Learned.md#L50-L53) | `inspect_nea_workbooks.py` | Preventing `openpyxl.save()` from Stripping Cross-Sheet `<extLst>` DataValidations -> Built `preserve_openxml_extensions()`, `[4E]` OpenXML DataValidation/AutoFilter auditing, `--repair [--out-dir <dir>]`, and `--verify-write ORIG EDITED` (`NEA-WRT-<12hex>`) into `Scripts/inspect_nea_workbooks.py` (`NEA-SCR-001`) and `nea-workbook-entry-guard` (`NEA-SKL-002`; `NetCom_Engineering_Assistant`). |
| **`LL-NEA-05`** | `TIER2` | [`NetCom_Engineering_Assistant_Lessons_Learned.md#L55-L58`](../Projects/NetCom_Engineering_Assistant/NetCom_Engineering_Assistant_Lessons_Learned.md#L55-L58) | `inspect_nea_workbooks.py`, `package_nea_delivery.py` | Context Consolidation (`28` $\rightarrow$ `5` Tier-1 Files), `Downloads/` Lock & Testbed Decontamination -> Consolidated to Tier 1/2 routing + single-turn `inspect_nea_workbooks.py` (`41` $\rightarrow$ `12` turns `-70.7%`, `360,676` cached tokens `-87.7%`), locked `Downloads/` to explicit deployment states (`package_nea_delivery.py`, `.zee` retired, `.agents/` excluded), quarantined `Historical/`, and purged `100%` of `307-2` spoilers (`0`... |
| **`LL-NEA-06`** | `TIER2` | [`NetCom_Engineering_Assistant_Lessons_Learned.md#L60-L63`](../Projects/NetCom_Engineering_Assistant/NetCom_Engineering_Assistant_Lessons_Learned.md#L60-L63) | `NetCom_Engineering_Assistant_Module_Launchpad.md` | Preventing Windows Desktop Excel OpenXML "File is Corrupt" Rejections on Generated Multi-Tab Workbooks -> Replaced `ElementTree` package serialization with deterministic UTF-8 XML builders (`_format_worksheet_xml_bytes()`, `SharedStringTable`, `_sort_sheetdata_rows_and_cells()`, per-sheet `drawing{idx}.xml` + unique `xr:uid`, and `validate_openxml_package_integrity()` inside `run_verify_write()`), verified by `xmllint --noout` and... |
| **`LL-NEA-07`** | `TIER2` | [`NetCom_Engineering_Assistant_Lessons_Learned.md#L65-L68`](../Projects/NetCom_Engineering_Assistant/NetCom_Engineering_Assistant_Lessons_Learned.md#L65-L68) | `inspect_nea_workbooks.py` | Multi-Media Timesheet OCR Staging, Key Normalization & Non-Target Tab/Page Pruning -> Built `Templates/Timesheet_Template.xlsx` (`NEA-TPL-004`, `Expense Report` stripped, `AG35` restored, styled with the NetCom Corporate Color Palette `cellXfs 217..239`), enforced page-level classification and pruning of non-timesheet pages/tabs in `NEA Timesheet Consolidator` (`NEA-AGT-006`), and added... |
