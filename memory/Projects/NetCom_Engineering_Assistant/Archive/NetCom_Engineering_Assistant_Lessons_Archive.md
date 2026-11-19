---
project: "NetCom_Engineering_Assistant"
parent_note: "NetCom_Engineering_Assistant_Lessons_Learned"
entity: "NetCom"
compartment: "private"
note_type: "lessons_archive"
authoritative: false
last_synced: "2026-11-19"
---

# 🗄️ NetCom_Engineering_Assistant — Graduated & Historical Lessons Archive (`TIER3`–`TIER5`)

> **Single-Source Tiered Archive**: Companion to [`NetCom_Engineering_Assistant_Lessons_Learned.md`](../NetCom_Engineering_Assistant_Lessons_Learned.md). Stores full-context narratives for stabilized `TIER3`, isolated-polish `TIER4`, and retired `TIER5` lessons so the active `<Project>_Lessons_Learned.md` window stays compact (`<= 3 TIER0 + <= 7 TIER2` sections). Query any entry on demand via `sync_memory.py --project NetCom_Engineering_Assistant --lesson-id <LL-xxx>` or promote back to active memory via `--set-tier <LL-xxx> TIER2`.

---

## 1. Archived Full-Context Post-Mortems (`TIER3`–`TIER5`)

### `LL-NEA-05` [TIER3] — Context Consolidation (`28` $\rightarrow$ `5` Tier-1 Files), `Downloads/` Lock & Testbed Decontamination
- **Symptom / Failed Approach (`Historical / Rejected`):** (1) `Run #4` baseline required `41` turns and `2,929,063` cached tokens across `28` fragmented `.md` files; (2) touching `/home/orin/Downloads/` mid-iteration caused delivery archive drift; (3) reading `Historical/` reintroduced retired per-row `Cable Run Status`; and (4) leaving `307-2` testbed numbers in `.md`/`.py` files allowed spoiler scraping.
- **Root Cause:** Fragmented multi-file documentation and mixing archived/testbed examples with live operational rules.
- **Verified Resolution:** Consolidated to Tier 1/2 routing + single-turn `inspect_nea_workbooks.py` (`41` $\rightarrow$ `12` turns `-70.7%`, `360,676` cached tokens `-87.7%`), locked `Downloads/` to explicit deployment states (`package_nea_delivery.py`, `.zee` retired, `.agents/` excluded), quarantined `Historical/`, and purged `100%` of `307-2` spoilers (`0` grep matches; [`NetCom_Engineering_Assistant`](../NetCom_Engineering_Assistant.md)).

### `LL-NEA-03` [TIER5] — Bundling `scripts/inspect_nea_workbooks.py` Inside Root-Level `<skill-name>.zip` Archives
- **Retirement Provenance (`TIER5` — `2026-11-17`):** Bundling scripts/inspect_nea_workbooks.py inside root <skill-name>.zip worked, but packaging all 9 skills (3 core + 6 per-agent role zips) failed in Windows/M365 deployment because
      role skills duplicated Instructions.txt + Knowledge/*.txt + inspect_nea_workbooks.py and confused upload assembly. Superseded by LL-NEA-08 (3 Core Guardrail Skills ONLY: NEA-SKL-001..003).
- **Symptom / Failed Approach (`Historical / Rejected`):** Packaging only `SKILL.md` inside `<skill-name>.zip` forced the LLM in Code Interpreter to write ad-hoc `openpyxl` scripts on the fly (burning turns and risking `Row 2` CRL header bugs), while nested subdirectories inside `<skill-name>.zip` or unquoted colons in YAML `description` broke M365 Skill upload validation.
- **Root Cause:** Microsoft's Declarative Agent Skills specification requires root-level `SKILL.md` (`dash_lines == [1, 4]`) + `scripts/inspect_nea_workbooks.py` (`zf.namelist() == ["SKILL.md", "scripts/inspect_nea_workbooks.py"]`).
- **Verified Resolution:** `Scripts/build_copilot_agents.py` packages all `9` skills under `Skills/<skill-name>/<skill-name>.zip` with bundled `scripts/inspect_nea_workbooks.py`—verified across `5`-agent parallel cold-start blind swarms and `NEA Timesheet Consolidator` `Blind-Light` (`24831c6b`) with `0` custom OpenXML parser code written ([`NetCom_Engineering_Assistant`](../NetCom_Engineering_Assistant.md)).
