# NetCom Engineering Assistant (`NEA v2.2.3`) — Engineer User Manual, Copilot Build Guide & DevOps Reference

- **Version**: `2.2.3`
- **Status**: `Current (Human Operational & DevOps Reference)`
- **Document ID**: `NEA-MAN-001`
- **Owner**: `NetCom Technical Services`
- **System Lead & Maintainer**: `Orin Leacock | Designer` (`oleacock@netcom1989.com` | `557-250-0254`)

> [!IMPORTANT]
> **Human Reference Only — Do Not Upload to Copilot Knowledge or Skills**:
> This manual is written for **NetCom engineers, project designers, and DevOps administrators**. It ships inside the `NEA_v2.2.3` deliverable package as your day-to-day operational guide and setup runbook. Do **not** upload this file into an agent's `Knowledge` or `Skills` slots in Microsoft 365 Copilot Agent Builder.

---

## Table of Contents

1. [System Overview & Core Philosophy ("Paper Truth")](#1-system-overview--core-philosophy-paper-truth)
2. [Part 1 — How to Build or Update an NEA Agent in Microsoft 365 Copilot](#2-part-1--how-to-build-or-update-an-nea-agent-in-microsoft-365-copilot)
3. [Part 2 — How to Interact with NEA & Daily Engineer Workflow](#3-part-2--how-to-interact-with-nea--daily-engineer-workflow)
4. [Part 3 — Copy-Paste Prompt & Command Reference Sheet](#4-part-3--copy-paste-prompt--command-reference-sheet)
5. [Part 4 — Expanding Capabilities, Adding Workbooks & Contacting DevOps](#5-part-4--expanding-capabilities-adding-workbooks--contacting-devops)

---

## 1. System Overview & Core Philosophy ("Paper Truth")

The **NetCom Engineering Assistant (`NEA v2.2.3`)** is a 6-Agent Microsoft 365 Copilot suite backed by a deterministic Python OpenXML inspection, repair, and consolidation engine (`inspect_nea_workbooks.py`). It is designed to help NetCom engineers and operations staff build, cross-check, repair, and release structured-cabling project spreadsheet packages and consolidate weekly multi-media Missouri Timesheets without formula corruption or part-number guesswork.

### Why NEA Uses 6 Specialist Agents
Rather than cramming every rule into a single overloaded chatbot, NEA divides engineering and operations work into **6 specialized agents**:

| Agent Name in Copilot | Mode | Primary Responsibility | When You Use It |
| :--- | :---: | :--- | :--- |
| **`NEA Package Reviewer`** | **Mode 1** *(Read-Only)* | Audits `Cover Sheet`, `Project BOM`, and `Cable Running List` (`.xlsx`), reconciles `CRL <-> BOM` takeoffs, and issues the 6-section **Release Readiness Report**. | Before releasing a package to installation, or after making revisions to verify zero blocking defects remain. |
| **`NEA BOM Builder`** | **Mode 2** *(Builder)* | Searches the 3-tier material catalog (`tblMaterials`, `Fiber Assemblies`, `Cable Harness`), rolls up `CRL` quantities, and populates `Project BOM` (`Cols B, C, J`) without overwriting `XLOOKUP` formulas (`Cols A, D:I`). | When starting a new Project BOM, converting a CRL into a material list, or adding/updating BOM line items. |
| **`NEA CRL Builder`** | **Mode 2** *(Builder)* | Builds, normalizes, and validates the 16-column `Cable Running List` (`Cols A:P`), checks `Run ID` sequence continuity, flags duplicate `NE/FE` ports, and generates takeoff summaries. | When building a cable schedule from floorplans/field notes or cleaning up an existing CRL. |
| **`NEA Catalog Manager`** | **Mode 2** *(Catalog)* | Audits and maintains the 3-tier catalog in `BOM_Materials_Master_Template.xlsx`, onboards new vendor parts, promotes `TPN##` keys, and protects the `Lists!H1` dynamic `VSTACK` dropdown spill. | When a project requires a part number not yet in `Materials Master`, or when deduplicating/updating catalog records. |
| **`NEA Repair Tool`** | **Mode 2** *(Repair)* | Non-destructively restores overwritten `Project BOM` (`A8:I155`), `Cover Sheet` (`B30:C30`), and `Timesheet` (`AG17:AK38`) formulas, fixes `tblMaterials`/`Lists!H1` zero-spill ranges, and heals broken Excel dropdowns/AutoFilters while keeping `100%` of your project data intact. | Whenever `NEA Package Reviewer` or a Builder displays a `🔄 [CROSS-DUTY -> NEA Repair Tool]` alert, or when a spreadsheet's dropdowns/formulas break. |
| **`NEA Timesheet Consolidator`** | **Mode 2** *(Timesheet)* | Consolidates digital `.xlsx`, scanned multi-page `.pdf` packets, and `.png`/`.jpg` photos of NetCom Missouri Timesheets into `Week_of_MM-DD_to_MM-DD.xlsx` (`Weekly Summary` Tab 1 + alphabetical `Last, First` employee tabs) while ignoring `Expense Report` tabs, store receipts, and vendor invoices. | Every week when consolidating office and field employee timesheets into a single payroll/operations workbook. |

---

## 2. Part 1 — How to Build or Update an NEA Agent in Microsoft 365 Copilot

NetCom's Microsoft 365 Copilot environment uses the integrated **Agent Builder** interface (`Configure` tab). Each agent is built cleanly in **2–3 minutes** using its matching folder inside `Copilot_Agents/`.

### 2.1 Overview of Agent Folders & Required Uploads

| Agent Name (`<= 30` chars) | Folder inside `Copilot_Agents/` | Instructions File (`Ctrl+A` Copy) | Knowledge Files (`Ctrl+A` Batch Upload) | Skill `.zip` Packages to Upload (`Skills/<skill-name>/`) |
| :--- | :--- | :--- | :--- | :--- |
| **`NEA Package Reviewer`** | `NEA_Package_Reviewer/` | `Instructions.txt` (`5,330 / 8,000` chars) | `Knowledge/*.txt` (`5` files) | 1. `nea-anti-hallucination.zip`<br>2. `nea-verification-and-receipt.zip` |
| **`NEA BOM Builder`** | `NEA_BOM_Builder/` | `Instructions.txt` (`3,820 / 8,000` chars) | `Knowledge/*.txt` (`6` files) | 1. `nea-anti-hallucination.zip`<br>2. `nea-workbook-entry-guard.zip`<br>3. `nea-verification-and-receipt.zip` |
| **`NEA CRL Builder`** | `NEA_CRL_Builder/` | `Instructions.txt` (`3,342 / 8,000` chars) | `Knowledge/*.txt` (`6` files) | 1. `nea-anti-hallucination.zip`<br>2. `nea-workbook-entry-guard.zip`<br>3. `nea-verification-and-receipt.zip` |
| **`NEA Catalog Manager`** | `NEA_Catalog_Manager/` | `Instructions.txt` (`3,794 / 8,000` chars) | `Knowledge/*.txt` (`7` files) | 1. `nea-anti-hallucination.zip`<br>2. `nea-workbook-entry-guard.zip`<br>3. `nea-verification-and-receipt.zip` |
| **`NEA Repair Tool`** | `NEA_Repair_Tool/` | `Instructions.txt` (`3,607 / 8,000` chars) | `Knowledge/*.txt` (`6` files) | 1. `nea-anti-hallucination.zip`<br>2. `nea-workbook-entry-guard.zip`<br>3. `nea-verification-and-receipt.zip` |
| **`NEA Timesheet Consolidator`** | `NEA_Timesheet_Consolidator/` | `Instructions.txt` (`6,206 / 8,000` chars) | `Knowledge/*.txt` (`5` files) | 1. `nea-anti-hallucination.zip`<br>2. `nea-workbook-entry-guard.zip`<br>3. `nea-verification-and-receipt.zip` |

---

### 2.2 Step-by-Step Build Procedure in M365 Copilot Agent Builder

Follow these **7 steps** for each agent you want to deploy:

#### Step 1 — Open Agent Builder & the Agent's Local Folder
1. In Microsoft 365 Copilot (`m365.cloud.microsoft` or Teams/Desktop Copilot), click **Create agent** (or **Build an agent**) in the right-hand pane and switch to the **Configure** tab.
2. On your computer, open the unzipped `NEA_v2.2.3/Copilot_Agents/<Agent_Folder>/` directory and open **`Agent_Config.md`** for reference.

#### Step 2 — Enter Name & Description
1. Copy the **Name** block from `Agent_Config.md` (for example, `NEA Package Reviewer`) and paste it into the **Name** field.
2. Copy the **Description** block from `Agent_Config.md` and paste it into the **Description** field.

#### Step 3 — Paste `Instructions.txt`
1. In File Explorer, open **`Copilot_Agents/<Agent_Folder>/Instructions.txt`** in Notepad or any text editor.
2. Press **`Ctrl+A`** (Select All) then **`Ctrl+C`** (Copy).
   - *Note*: `Instructions.txt` contains pure raw instruction text with zero wrapper headers, so selecting all is completely safe.
3. Paste (`Ctrl+V`) directly into the **Instructions** box in Agent Builder.

#### Step 4 — Enable Code Interpreter
1. Scroll to the **Capabilities** section in Agent Builder.
2. Toggle **Code Interpreter** (*"Create documents, charts, and code"*) to **ON**.
3. Leave **Web content / Web search** **OFF** so the agent operates strictly on NetCom's closed-world spreadsheets and standards.

#### Step 5 — Batch-Upload the Agent's `Knowledge/` Files (`Ctrl+A`)
1. In Agent Builder's **Knowledge** section, click to upload files from your device.
2. Browse to **`Copilot_Agents/<Agent_Folder>/Knowledge/`**.
3. Inside that `Knowledge/` folder, press **`Ctrl+A`** to highlight all `.txt` files at once (`5` to `7` files depending on the agent) and click **Open**.
   - *Why this is fast and clean*: Every file inside `Knowledge/` is already filtered for that specific agent with zero duplicate skill or script files.

#### Step 6 — Upload the Packaged Skill `.zip` Archives (`Skills/<skill-name>/<skill-name>.zip`)
1. Scroll to the **Skills** section in Agent Builder and click **`Add skill` $\rightarrow$ `Upload skill`**.
2. Browse to **`NEA_v2.2.3/Skills/<skill-name>/`** and select **`<skill-name>.zip`**:
   - For **`NEA Package Reviewer`**, upload:
     - `Skills/nea-anti-hallucination/nea-anti-hallucination.zip`
     - `Skills/nea-verification-and-receipt/nea-verification-and-receipt.zip`
   - For **`NEA BOM Builder`**, **`NEA CRL Builder`**, **`NEA Catalog Manager`**, **`NEA Repair Tool`**, and **`NEA Timesheet Consolidator`**, upload:
     - `Skills/nea-anti-hallucination/nea-anti-hallucination.zip`
     - `Skills/nea-workbook-entry-guard/nea-workbook-entry-guard.zip`
     - `Skills/nea-verification-and-receipt/nea-verification-and-receipt.zip`
3. **Why You Upload the `.zip` File Here**: Each `<skill-name>.zip` contains both `SKILL.md` at the root of the archive and `scripts/inspect_nea_workbooks.py` in `scripts/`. Uploading the `.zip` mounts the deterministic Python inspection and repair script directly inside the skill's packaged filesystem so the agent never has to write ad-hoc Python from scratch.

#### Step 7 — Add Starter Prompts & Publish
1. Scroll to **Starter prompts** at the bottom of `Agent_Config.md`.
2. Copy each **`Title`** and **`Prompt`** pair into Agent Builder's Starter Prompts fields (`4` starters per agent).
3. Click **Create** (or **Update** / **Publish**) in the top-right corner.

---

### 2.3 Updating a Single Agent Module Without Touching the Others
Each of the 6 NEA agents runs in its own isolated container. If a future update only adds a new spreadsheet comparison to **`NEA Package Reviewer`**:
- You **only** need to update **`NEA Package Reviewer`** in M365 Copilot Agent Builder (replace its `Instructions.txt`, re-upload its `Knowledge/*.txt` files, and re-upload its updated skill `.zip`).
- The other 5 agents (`BOM Builder`, `CRL Builder`, `Catalog Manager`, `Repair Tool`, `Timesheet Consolidator`) will continue functioning normally without interruption or errors.

---

## 3. Part 2 — How to Interact with NEA & Daily Engineer Workflow

### 3.1 Rule #1: Always Attach `.xlsx` Files Directly into the Chat Box (`+` Button)
> [!CAUTION]
> **Do Not Rely on Cloud File Links Alone — Attach `.xlsx` Files via `+ Upload from device`**:
> When starting a review, build, or repair session, always click the **`+` (Attach / Upload from device)** icon inside the Copilot chat box and select your live `.xlsx` workbooks (`BOM_Materials_Master.xlsx`, `Cable_Running_List.xlsx`, `Project_Cover_Sheet.xlsx`) from File Explorer.
> - **Why**: Attaching files directly in the chat turn mounts them immediately inside the **Code Interpreter** sandbox (`/mnt/data/`) with **zero OneDrive/SharePoint indexing delay**, ensuring the Python engine inspects your exact up-to-the-second save.

---

### 3.2 Typical End-to-End Engineering Workflow

```text
  [1. Build / Edit Schedules]               [2. Self-Review Package]              [3. Fix Mechanics / Catalog]
 ┌───────────────────────────┐            ┌──────────────────────────┐           ┌────────────────────────────┐
 │ • NEA CRL Builder         │  .xlsx     │ • NEA Package Reviewer   │  If       │ • NEA Repair Tool          │
 │   (16-col Cable Schedule) ├───────────►│   (Runs read-only audit, ├──────────►│   (Auto-heals formulas &   │
 │ • NEA BOM Builder         │  attached  │    CRL<->BOM takeoff, &  │  flagged  │    dropdowns, 0 data loss) │
 │   (3-tier Catalog + BOM)  │  in chat   │    6-Section Report)     │           │ • NEA Catalog Manager      │
 └───────────────────────────┘            └────────────┬─────────────┘           └────────────────────────────┘
                                                       │
                                                       ▼  Zero AR-## Findings
                                          ┌──────────────────────────┐
                                          │  RELEASED "PAPER TRUTH"  │
                                          │  Handoff to Installation │
                                          └──────────────────────────┘
```

1. **Build / Update the Schedules**:
   - Use **`NEA CRL Builder`** to normalize cable runs into the 16-column NetCom CRL format and verify there are no missing fiber strand counts or duplicate `NE/FE` rack/port assignments.
   - Use **`NEA BOM Builder`** to roll up the CRL cable footages and connector counts into `Project BOM` using verified `MB P/N` keys from the 3-tier catalog.
2. **Run a Pre-Release Audit**:
   - Open **`NEA Package Reviewer`**, attach your `.xlsx` files via **`+`**, and click the **`Run Full Deliverable Review`** starter prompt.
3. **Resolve Findings & Cross-Duty Advisories**:
   - **Section 4 & Section 5 (`Engineer Closeout Punch List`)** list any project engineering items that need your attention:
     - **`AR-##` (`Action Required`)**: Must be resolved before release (e.g., `"Not found"` part number, blank quantity, omitted cable type on BOM, missing Fiber Count in `Col M`, or ordering `300 BX` of 1,000-pack cable ties instead of `1 BX`).
     - **`RR-##` (`Review Recommended`)**: Confirm engineering intent before release (e.g., `Classification = Unknown`, `OFNR` Riser comment vs `Plenum` requirement, `Verify` / `(optional)` notes in `Col J`, or duplicate `NE/FE` ports).
     - **`ADV-##` (`Advisory`)** & **`INF-##` (`Informational`)**: Non-blocking observations (e.g., blank row spacing `> 5` rows, active `TPN##` temporary part numbers, per-run fiber room notes).
   - **Section 6 (`Cross-Duty Agent Advisories`)** tells you if a spreadsheet needs mechanical or catalog maintenance:
     - If you see **`🔄 [CROSS-DUTY -> NEA Repair Tool]`**, attach the workbook to **`NEA Repair Tool`** and click **`Auto-Repair Workbook Formulas & XML`**. It will repair overwritten formulas and dropdowns automatically and hand you back a clean `.xlsx` file with zero changes to your project data.
     - If you see **`🔄 [CROSS-DUTY -> NEA Catalog Manager]`**, attach the BOM workbook to **`NEA Catalog Manager`** to onboard new parts or clean up catalog entries.

---

### 3.3 Understanding Verification Receipts (`NEA-VRF` & `NEA-WRT`)
Every NEA response includes a cryptographic verification token at the top of the report so you can trust that the agent actually ran the deterministic Python engine on your files:
- **`NEA-VRF-<12hex>` (`Review Receipt`)**: Confirms `scripts/inspect_nea_workbooks.py` parsed your `.xlsx` files in read-only mode and verified **`Pre/Post SHA-256` immutability (`0 bytes modified`)**.
- **`NEA-WRT-<12hex>` (`Write / Repair Receipt`)**: Confirms a Builder or Repair agent ran `--verify-write` comparing the original `.xlsx` against the edited `.xlsx`, proving that **zero formula-locked columns were lost** and **cross-sheet `<extLst>` dropdown validations remain intact**.
- **`[EXTRACTION BLOCKED — REVIEW ABORTED]`**: If you forget to attach an `.xlsx` file, the agent will immediately halt and display this banner rather than guessing or making up findings.

---

## 4. Part 3 — Copy-Paste Prompt & Command Reference Sheet

You can click any agent's built-in **Starter Prompts** or copy-paste the specialized prompts below directly into chat (remember to attach your `.xlsx` files with **`+`** first).

---

### 4.1 `NEA Package Reviewer` Prompts *(Mode 1 Read-Only Audit)*

| Goal | Copy-Paste Prompt |
| :--- | :--- |
| **Full Multi-Workbook Package Review** *(Cover + BOM + CRL)* | `Inspect the attached project workbooks (.xlsx) using Code Interpreter and generate the complete 6-section NEA v2.2.3 Engineering Review Report with live NEA-VRF and SHA-256 verification.` |
| **Single-Workbook Project BOM Audit** | `Run a read-only NEA v2.2.3 audit on the attached BOM workbook (.xlsx), checking Cover Sheet metadata, Project BOM formula locks (Cols A & D:I), blank quantities, UOM=BX box multiplier anomalies, and 3-tier catalog lookups.` |
| **Single-Workbook Cable Running List (CRL) Audit** | `Audit the attached Cable Running List (.xlsx) for 16-column schema compliance, Run ID sequence continuity, missing Fiber Counts in Column M, intra-row contradictions, and duplicate NE/FE rack/port endpoints.` |
| **Cross-Document Takeoff Check Only (`CRL <-> BOM`)** | `Compare the attached Cable Running List (.xlsx) against the attached Project BOM (.xlsx) in Code Interpreter and generate Section 3 (Cross-Document Material & Cable Takeoff Reconciliation) showing all footage and connector variances.` |
| **Post-Revision Delta Re-Check** | `Re-inspect the updated project workbooks (.xlsx) in Code Interpreter, verify whether all prior Action Required (AR-##) and Review Recommended (RR-##) items are resolved, and output the updated Release Readiness Report.` |

---

### 4.2 `NEA BOM Builder` Prompts *(Mode 2 Guided BOM Build & Takeoff)*

| Goal | Copy-Paste Prompt |
| :--- | :--- |
| **Roll Up Attached CRL into Project BOM** | `Using Code Interpreter, calculate the required copper cable footage, fiber runs, and termination hardware from the attached Cable Running List (.xlsx), match each item to verified MB P/Ns in the attached BOM workbook, and populate Project BOM Columns B, C, and J.` |
| **Search the 3-Tier Catalog for Part Numbers** | `Search the attached BOM workbook's 3-tier catalog (tblMaterials, Fiber Assemblies, and Cable Harness) in Code Interpreter to find matching active MB P/Ns, UOMs, and descriptions for: [list your items or keywords here, e.g., Cat6A Plenum Blue, 24-strand OS2, 48-port patch panel].` |
| **Add or Update Specific BOM Rows Safely** | `Update the attached BOM workbook (.xlsx) in Code Interpreter by adding the following items to Project BOM (Columns B, C, and J only) while preserving all Column A and Columns D:I XLOOKUP formulas and cross-sheet dropdowns: [paste your MB P/Ns, Quantities, and Notes].` |
| **Update BOM Cover Sheet Metadata** | `Update the Cover Sheet metadata cells (D10 Project Name, D12 Project Number, D14 Customer, D16 Contact, D18 Building, D20 PM, D22 Designer, D24 Issue Date, H24 Revision) in the attached BOM workbook (.xlsx) with the following project details while keeping B30:C30 formulas intact: [paste details].` |
| **Verify BOM Formula Locks & Unit Summary** | `Inspect the attached BOM workbook (.xlsx) in Code Interpreter to confirm 100% of Project BOM Rows 8-155 preserve their Column A and Columns D:I XLOOKUP formulas, zero 'Not found' errors exist, and generate a unit-segregated summary (FT vs EA/KT/BX).` |

---

### 4.3 `NEA CRL Builder` Prompts *(Mode 2 Guided Cable Schedule Build)*

| Goal | Copy-Paste Prompt |
| :--- | :--- |
| **Populate or Normalize Cable Runs (`Cols A:P`)** | `Using Code Interpreter, populate or normalize the cable runs in the attached Cable_Running_List (.xlsx) according to the 16-column NEA v2.2.3 CRL schema (Columns A:P), preserve all <extLst> dropdowns, and return the updated downloadable .xlsx workbook with a NEA-WRT receipt.` |
| **Audit CRL for Missing Fiber Counts & Duplicate Ports** | `Inspect the attached Cable Running List (.xlsx) in Code Interpreter for missing Fiber Counts (Col M), duplicate NE/FE rack and port assignments (CRL-DATA-003), Run ID sequence gaps, and pathway fire-rating contradictions.` |
| **Generate a BOM Takeoff Summary Table from CRL** | `Analyze the attached Cable Running List (.xlsx) in Code Interpreter and generate a complete, unit-segregated Material & Termination Takeoff table (Bulk Copper FT by type/color, Bulk Fiber FT by strand count, Station Jumpers EA, and NE/FE Connectors) ready for Project BOM entry.` |
| **Append New Cable Runs to an Existing Schedule** | `Append the following cable runs to the next available active row block in the attached Cable Running List (.xlsx) in Code Interpreter, continuing the sequential Run ID numbering and verifying all 16 columns: [paste run details].` |

---

### 4.4 `NEA Catalog Manager` Prompts *(Mode 2 Catalog Hygiene & Onboarding)*

| Goal | Copy-Paste Prompt |
| :--- | :--- |
| **Full 3-Tier Catalog Health Audit** | `Inspect the attached BOM_Materials_Master (.xlsx) in Code Interpreter across tblMaterials, Fiber Assemblies, and Cable Harness for duplicate MB P/N keys, duplicate (Manufacturer, MFG Part Number) pairs, UOM/Category misclassifications, and Lists!H1 spill health.` |
| **Onboard New Materials into `tblMaterials`** | `Help me normalize and onboard the following new material records into tblMaterials in the attached BOM workbook (.xlsx), assigning the next sequential MB P/N in the appropriate category series, resizing table1.xml ref to the exact last row, and verifying Lists!H1 spill integrity: [paste Manufacturer, MFG P/N, Category, UOM, Description].` |
| **Promote Temporary Part Numbers (`TPN##`) to Official `MB P/N`s** | `Inspect the attached BOM workbook (.xlsx) for active Temporary Part Numbers (TPN##) on the Project BOM, onboard them as permanent Active records in tblMaterials with official MB P/Ns, and update the corresponding Project BOM Column B entries.` |
| **Assign `MB P/N`s to Pending `Cable Harness` Variants** | `Inspect the Cable Harness worksheet ($A$3:$H$1258) in the attached BOM workbook (.xlsx), list Pending variants needing an MB P/N, and help me assign unique MB P/Ns and update their Status to Active.` |

---

### 4.5 `NEA Repair Tool` Prompts *(Mode 2 Non-Destructive Workbook Auto-Repair)*

| Goal | Copy-Paste Prompt |
| :--- | :--- |
| **One-Click Full Workbook Auto-Repair (`--repair`)** | `Run the NEA Repair Tool (--repair) in Code Interpreter on the attached .xlsx workbook(s) to non-destructively restore any overwritten Cover Sheet (B30:C30) or Project BOM (A8:I155) formulas, fix tblMaterials/Lists!H1 zero-spill bounds, and heal OpenXML DataValidation/AutoFilter ranges, then return the verified downloadable .xlsx file(s) with a NEA-WRT receipt.` |
| **Restore Overwritten `Project BOM` `XLOOKUP` Formulas** | `Inspect the attached BOM_Materials_Master (.xlsx) workbook in Code Interpreter and restore any missing or overwritten Column A (Line) and Columns D:I 3-tier XLOOKUP formulas across Rows 8-155 while keeping my Columns B, C, and J inputs 100% untouched.` |
| **Heal Broken `CRL` Dropdowns & AutoFilter** | `Repair any fragmented or split-column DataValidation rules (<dataValidation> and <x14:dataValidation>) and normalize the _FilterDatabase AutoFilter across Rows 3..1087 in the attached Cable Running List (.xlsx) without altering any cable run data.` |

---

### 4.6 `NEA Timesheet Consolidator` Prompts *(Mode 2 Multi-Media Weekly Timesheet Consolidation)*

| Goal | Copy-Paste Prompt |
| :--- | :--- |
| **Consolidate Mixed Weekly Timesheets** *(Excel `.xlsx`, Scanned `.pdf`, Photos `.png`/`.jpg`)* | `Consolidate all attached weekly timesheets (.xlsx, .pdf, and/or images) with Templates/Timesheet_Template.xlsx in Code Interpreter into Week_of_MM-DD_to_MM-DD.xlsx with a front Weekly Summary tab and alphabetically sorted Last, First employee tabs. Ignore all Expense Report tabs, mileage sheets, hardware store receipts, and vendor invoices, and return the downloadable .xlsx workbook with a NEA-WRT receipt.` |
| **Consolidate a Multi-Page Scanned Field PDF Packet** | `Extract every employee Missouri Timesheet page from the attached scanned PDF packet (ignoring any interleaved Expense Report pages, Home Depot/True Value receipts, or vendor invoices), verify daily and weekly hour totals, and consolidate all employees into Week_of_MM-DD_to_MM-DD.xlsx using Templates/Timesheet_Template.xlsx.` |
| **Append Additional Employee Timesheets to an Existing Weekly Workbook** | `Append the newly attached employee timesheets (.xlsx, .pdf, or photo) into the attached Week_of_MM-DD_to_MM-DD.xlsx workbook, re-sort employee tabs alphabetically in Last, First order after Weekly Summary, refresh the Weekly Summary roll-up, and verify with a NEA-WRT receipt.` |
| **Pre-Check Handwritten / Scanned Timesheets Before Writing** | `Inspect all attached scanned or photographed timesheets, cross-check each employee's daily hours (SUN-SAT) against the printed/written TOTAL HOURS columns and Row 38 grand totals, and display the OCR/Vision Verification Table for confirmation before writing the consolidated workbook.` |

---

### 4.7 Local Terminal CLI Commands *(For DevOps & Workstation Testing)*

If you have Python 3 installed locally, you can also run the bundled OpenXML engine directly from a terminal inside `NEA_v2.2.3/`:

```bash
# 1. Full read-only deliverable review telemetry (Cover + BOM + CRL):
python3 Scripts/inspect_nea_workbooks.py Templates --scope review

# 2. Inspect Missouri Timesheet templates or consolidated weekly workbooks:
python3 Scripts/inspect_nea_workbooks.py Templates --scope timesheet

# 3. Consolidate extracted weekly timesheet JSON manifest into Week_of_MM-DD_to_MM-DD.xlsx:
python3 Scripts/inspect_nea_workbooks.py --consolidate timesheet_manifest.json --template Templates/Timesheet_Template.xlsx --out Week_of_10-25_to_10-31.xlsx

# 4. Fast 3-tier catalog search by keyword, manufacturer, or MB P/N:
python3 Scripts/inspect_nea_workbooks.py Templates --lookup "Cat6A"
python3 Scripts/inspect_nea_workbooks.py Templates --lookup "OS2"

# 5. Non-destructive automated workbook repair (writes repaired copies to out_dir):
python3 Scripts/inspect_nea_workbooks.py Templates --repair --out-dir ./Repaired_Workbooks

# 6. Verify an edited workbook against its original baseline (generates NEA-WRT receipt):
python3 Scripts/inspect_nea_workbooks.py --verify-write Templates/BOM_Materials_Master_Template.xlsx ./Repaired_Workbooks/BOM_Materials_Master_Template.xlsx

# 7. Recompile all 6 Copilot Agent folders and all 3 core guardrail <skill-name>.zip packages after a rule/script update:
python3 Scripts/build_copilot_agents.py
```

---

## 5. Part 4 — Expanding Capabilities, Adding Workbooks & Contacting DevOps

### 5.1 How NEA Is Designed to Grow
The NEA architecture is modular by design:
- **Role-Based Workbook Discovery**: `scripts/inspect_nea_workbooks.py` identifies spreadsheets by their internal worksheet tab structure rather than hardcoded filenames.
- **Ample Instruction Headroom**: All 5 agents sit well below Microsoft's `8,000`-character instruction limit (`41%–66%` utilization), leaving room for additional spreadsheet types and validation rules.
- **Independent Module Updates**: New workbook types—such as **Equipment Schedules**, **Rack Elevation Schedules**, **Fiber Assignment / Splice Schedules**, **Patch Panel Port Maps**, or **Field Test Logs**—can be added to `NEA Package Reviewer` first to test cross-document comparisons (`New Schedule <-> Project BOM <-> CRL`) before rolling builder or repair capabilities out to the rest of the suite.

### 5.2 What to Prepare When Requesting a New Feature or Spreadsheet Type
When reaching out to add a new workbook, expand the catalog schema, or adjust an engineering review rule, please include:
1. **Sample `.xlsx` Workbook / Template**: Attach a representative `.xlsx` file showing the exact tab names and header rows.
2. **Column Lock Map**: Note which columns/cells the engineer types into versus which columns contain formulas or dropdown lists that NEA must protect.
3. **Cross-Document Comparison Rules**: Explain what needs to match across files (for example, *"Every switch or patch panel listed on the Rack Elevation sheet must have a matching part number and quantity on the Project BOM"*).
4. **Severity Preference**: Let us know whether a mismatch should block package release (**`Action Required` `AR-##`**) or flag for engineer confirmation (**`Review Recommended` `RR-##`**).

---

### 5.3 Primary Contact for NEA Updates, Expansion & DevOps Support

For all questions, bug reports, template additions, catalog expansions, or new agent capabilities, please reach out directly to:

- **Name & Title**: **Orin Leacock | Designer**
- **Organization**: **NetCom Technical Services**
- **Email**: [`oleacock@netcom1989.com`](mailto:oleacock@netcom1989.com)
- **Phone**: **`557-250-0254`**

---

*Document Maintenance Rule (`NEA-MAN-001`)*: This manual is a controlled human-reference artifact shipped in the root of every `NEA` release package. Whenever agents, skills, starter prompts, workbook schemas, or CLI flags are updated in future versions of NEA, this document must be updated in lockstep prior to packaging.
