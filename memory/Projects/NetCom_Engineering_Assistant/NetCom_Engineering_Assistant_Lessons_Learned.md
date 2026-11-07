---
project: "NetCom_Engineering_Assistant"
parent_note: "NetCom_Engineering_Assistant"
entity: "NetCom"
compartment: "private"
note_type: "lessons_learned"
last_synced: "2026-11-05"
---

# 🧠 NetCom Engineering Assistant (`NEA v2.2.3`) — Engineering Lessons Learned & Post-Mortem Ledger (`NetCom_Engineering_Assistant_Lessons_Learned`)

Project-scoped engineering & M365 Copilot architecture post-mortem ledger for [`NetCom_Engineering_Assistant`](NetCom_Engineering_Assistant.md) (`Compartment C — Independent Corporate Entity`), paired with [`NetCom_Engineering_Assistant_Module_Launchpad`](NetCom_Engineering_Assistant_Module_Launchpad.md).

> [!IMPORTANT]
> **Compartment C Isolation, Failed-Attempt Quarantine & Turn-1 Skill Gate**
> 1. **Strict Compartment C Entity Firewall:** **NetCom (`netcom1989.com`)** is an independent enterprise completely separate from **Alchemical-3D** (`data-and-credential-safety.md`). Zero NetCom/NEA lessons, workbook schemas, or identifiers may ever cross into `/home/orin/Projects/Alchemical3D/*` or `Homunculus`.
> 2. **Mandatory Turn-1 NEA Skill Gate:** Before modifying any file in `/home/orin/Projects/Engineering/NEA_v2.2.3`, read `/home/orin/Projects/Engineering/NEA_v2.2.3/.agents/skills/nea-copilot-builder/SKILL.md` and [`NetCom_Engineering_Assistant_Module_Launchpad`](NetCom_Engineering_Assistant_Module_Launchpad.md).
> 3. **Failed-Attempt Quarantine (`verify_claims.py` Auto-Exclusion):** Automatically excluded (`excluded_lessons_learned_sources`) when scanning `--sources`. Canonical `v2.2.3` specs live in [`NetCom_Engineering_Assistant`](NetCom_Engineering_Assistant.md) and `/home/orin/Projects/Engineering/NEA_v2.2.3/NEA_Governance_Register_v2.2.3.md`.

---

## 1. Engineering Post-Mortems & Troubleshooting Entries

### 1.1 Overcoming M365 Copilot OneDrive Graph Latency & Ephemeral Container Boundaries (`Tier 1: NetCom Local`)
- **Symptom / Failed Approach (`Historical / Rejected`):** Connecting live `.xlsx` deliverables via OneDrive/SharePoint Knowledge links caused two severe failures: (1) Excel edits took minutes to hours to propagate through the asynchronous Microsoft Graph search index, and (2) Graph RAG text chunking could not evaluate OpenXML `<f>` (including `<f t="shared" si="..."/>`) vs. cached `<v>` values or 3-tier `XLOOKUP` chains. Additionally, Code Interpreter runs in an isolated Azure container (`16 MB` upload cap) that cannot write back directly to OneDrive.
- **Root Cause:** M365 Copilot separates declarative SharePoint Knowledge indexing (asynchronous semantic search) from Code Interpreter file attachments (synchronous container mount at `/mnt/data/`).
- **Verified Resolution (`GOV-015`, `GOV-017`):** Engineers upload live `.xlsx` deliverables **directly into the Copilot chat turn** (`+ Upload from device`), mounting exact bytes in `/mnt/data/` with `0` indexing latency; Mode 2 edits/repairs run `--verify-write ORIG EDITED` (`NEA-WRT-<12hex>`) inside Code Interpreter and return a downloadable `.xlsx` artifact in chat ([`NetCom_Engineering_Assistant`](NetCom_Engineering_Assistant.md)).

### 1.2 Solving the `8,000`-Char Instruction Cap, `"2.2.3"` Semver Lock & `.txt` Knowledge Indexing (`Tier 1: NetCom Local`)
- **Symptom / Failed Approach (`Historical / Rejected`):** A single monolithic prompt exceeded M365 Agent Builder's `8,000`-character hard cap; `.zip` uploads with alphanumeric version `"2.0a"` or unexpanded `$[file('...')]` macros failed M365 schema validation; and raw `.md` or `.py` files in Agent Builder `Knowledge/` were skipped or poorly indexed by Graph.
- **Root Cause:** Agent Builder enforces `Instructions <= 8,000` chars (`Name <= 30`, `Description <= 1,000`), strict numeric `X.Y.Z` semver (`"2.2.3"`), inline string compilation in `declarativeAgent.json`, and native `.txt`/`.docx`/`.pdf`/`.xlsx` indexing.
- **Verified Resolution:** `Scripts/build_copilot_agents.py` (`NEA-SCR-002`) compiles the **6-Agent Modular Specialist Suite** (`NEA_Package_Reviewer` `5,330` chars `66.6%`, `NEA_BOM_Builder` `3,820` chars `47.8%`, `NEA_CRL_Builder` `3,342` chars `41.8%`, `NEA_Catalog_Manager` `3,794` chars `47.4%`, `NEA_Repair_Tool` `3,607` chars `45.1%`, `NEA_Timesheet_Consolidator` `5,220` chars `65.2%`) with directional `🔄 [CROSS-DUTY -> <Agent>]` handoff advisories and auto-synced `.txt` Knowledge packs (`Knowledge/*.txt`; [`NetCom_Engineering_Assistant`](NetCom_Engineering_Assistant.md)).

### 1.3 Bundling `scripts/inspect_nea_workbooks.py` Inside Root-Level `<skill-name>.zip` Archives (`Tier 1: NetCom Local`)
- **Symptom / Failed Approach (`Historical / Rejected`):** Packaging only `SKILL.md` inside `<skill-name>.zip` forced the LLM in Code Interpreter to write ad-hoc `openpyxl` scripts on the fly (burning turns and risking `Row 2` CRL header bugs), while nested subdirectories inside `<skill-name>.zip` or unquoted colons in YAML `description` broke M365 Skill upload validation.
- **Root Cause:** Microsoft's Declarative Agent Skills specification requires root-level `SKILL.md` (`dash_lines == [1, 4]`) + `scripts/inspect_nea_workbooks.py` (`zf.namelist() == ["SKILL.md", "scripts/inspect_nea_workbooks.py"]`).
- **Verified Resolution:** `Scripts/build_copilot_agents.py` packages all `9` skills under `Skills/<skill-name>/<skill-name>.zip` with bundled `scripts/inspect_nea_workbooks.py`—verified across `5`-agent parallel cold-start blind swarms and `NEA Timesheet Consolidator` `Blind-Light` (`24831c6b`) with `0` custom OpenXML parser code written ([`NetCom_Engineering_Assistant`](NetCom_Engineering_Assistant.md)).

### 1.4 Preventing `openpyxl.save()` from Stripping Cross-Sheet `<extLst>` DataValidations (`Tier 1: NetCom Local`)
- **Symptom / Failed Approach (`Historical / Rejected`):** Saving `BOM_Materials_Master_Template.xlsx` or `Cable_Running_List_Template.xlsx` with standard `openpyxl.save()` silently stripped `<extLst>` (`x14:dataValidations` cross-sheet dropdowns referencing `Lists`) and left fragmented `DataValidation` ranges (`Rows 3..1087`) or broken `_FilterDatabase` definitions.
- **Root Cause:** `openpyxl` drops unrecognized `<extLst>` worksheet extension trees during XML re-serialization.
- **Verified Resolution:** Built `preserve_openxml_extensions()`, `[4E]` OpenXML DataValidation/AutoFilter auditing, `--repair [--out-dir <dir>]`, and `--verify-write ORIG EDITED` (`NEA-WRT-<12hex>`) into `Scripts/inspect_nea_workbooks.py` (`NEA-SCR-001`) and `nea-workbook-entry-guard` (`NEA-SKL-002`; [`NetCom_Engineering_Assistant`](NetCom_Engineering_Assistant.md)).

### 1.5 Context Consolidation (`28` $\rightarrow$ `5` Tier-1 Files), `Downloads/` Lock & Testbed Decontamination (`Tier 1: NetCom Local`)
- **Symptom / Failed Approach (`Historical / Rejected`):** (1) `Run #4` baseline required `41` turns and `2,929,063` cached tokens across `28` fragmented `.md` files; (2) touching `/home/orin/Downloads/` mid-iteration caused delivery archive drift; (3) reading `Historical/` reintroduced retired per-row `Cable Run Status`; and (4) leaving `307-2` testbed numbers in `.md`/`.py` files allowed spoiler scraping.
- **Root Cause:** Fragmented multi-file documentation and mixing archived/testbed examples with live operational rules.
- **Verified Resolution:** Consolidated to Tier 1/2 routing + single-turn `inspect_nea_workbooks.py` (`41` $\rightarrow$ `12` turns `-70.7%`, `360,676` cached tokens `-87.7%`), locked `Downloads/` to explicit deployment states (`package_nea_delivery.py`, `.zee` retired, `.agents/` excluded), quarantined `Historical/`, and purged `100%` of `307-2` spoilers (`0` grep matches; [`NetCom_Engineering_Assistant`](NetCom_Engineering_Assistant.md)).

### 1.6 Preventing Windows Desktop Excel OpenXML "File is Corrupt" Rejections on Generated Multi-Tab Workbooks (`Tier 1: NetCom Local`)
- **Symptom / Failed Approach (`Historical / Rejected`):** Initial `Week_of_10-25_to_10-31.xlsx` workbooks generated by cloning `Timesheet_Template.xlsx` passed basic Python `ET.fromstring()` checks, yet Windows Desktop Excel refused to open them (`"The file is corrupt and cannot be opened"`).
- **Root Cause:** Six ECMA-376 OpenXML serialization defects produced by Python's `xml.etree.ElementTree.tostring()` and zip cloning: (1) `ET.tostring()` stripped `xmlns:x14ac`/`xmlns:xr`/`xmlns:xr2`/`xmlns:xr3` declared inside `mc:Ignorable="..."` on `<worksheet>` and stripped `xmlns:x14`/`xmlns:x15` from `<ext uri="...">` blocks in `xl/styles.xml`; (2) `ET.tostring()` injected `<ns0:Types>` and `<ns0:Relationships>` prefixes into `[Content_Types].xml` and `xl/_rels/workbook.xml.rels`; (3) `<definedNames>` retained dangling references to the deleted `'Expense Report'` tab; (4) cloned employee tabs shared a single `xl/drawings/drawing1.xml`, identical `xr:uid`, and `codeName="Sheet13"`; (5) dynamically appended cells (`C10`, `B25`) were appended at the end of `<row>` out of ascending column order; and (6) passing stale `ZipInfo` objects from `zin.infolist()` to `zout.writestr(item, data)` preserved stale CRC/size headers.
- **Verified Resolution (`GOV-018`):** Replaced `ElementTree` package serialization with deterministic UTF-8 XML builders (`_format_worksheet_xml_bytes()`, `SharedStringTable`, `_sort_sheetdata_rows_and_cells()`, per-sheet `drawing{idx}.xml` + unique `xr:uid`, and `validate_openxml_package_integrity()` inside `run_verify_write()`), verified by `xmllint --noout` and confirmed opening cleanly in Windows Desktop Excel ([`NetCom_Engineering_Assistant_Module_Launchpad`](NetCom_Engineering_Assistant_Module_Launchpad.md)).

### 1.7 Multi-Media Timesheet OCR Staging, Key Normalization & Non-Target Tab/Page Pruning (`Tier 1: NetCom Local`)
- **Symptom / Failed Approach (`Historical / Rejected`):** Field timesheet submissions arrive as mixed digital `.xlsx` files (containing a second `Expense Report` tab and a missing `AG35` Job Slot 10 `REG` formula), multi-page scanned `.pdf` packets (interleaving employee timesheets with mileage sheets, Home Depot receipts, and vendor invoices), and photos—where minor LLM JSON key variations (`"job"` vs. `"job_name"`, `"days"` vs. `"hours"`, `"Tues"` vs. `"tue"`) during manifest staging risked dropping job hours.
- **Root Cause:** Unfiltered multi-page PDF ingestion and rigid JSON key expectations between the LLM OCR pass and the deterministic OpenXML writer.
- **Verified Resolution (`GOV-018`):** Built `Templates/Timesheet_Template.xlsx` (`NEA-TPL-004`, `Expense Report` stripped, `AG35` restored, styled with the NetCom Corporate Color Palette `cellXfs 217..239`), enforced page-level classification and pruning of non-timesheet pages/tabs in `NEA Timesheet Consolidator` (`NEA-AGT-006`), and added `normalize_timesheet_emp_record()` in `Scripts/inspect_nea_workbooks.py` (`--consolidate`)—verified in Cold-Start `Blind-Light` (`24831c6b`) and `Blind-Light+faults` (`1/1` injected formula corruption caught; [`NetCom_Engineering_Assistant`](NetCom_Engineering_Assistant.md)).
