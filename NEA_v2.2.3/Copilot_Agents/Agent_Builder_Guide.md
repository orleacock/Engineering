# NetCom Engineering Assistant (NEA) v2.2.3 — Integrated Copilot Agent Builder Guide

Version: 2.2.3
Status: Current
Document ID: NEA-COPILOT-GUIDE
Owner: NetCom Technical Services

---

## 1. Quick-Start: Building the 6 NEA Agents in Agent Builder

Open Microsoft 365 Copilot **Agent Builder** and create each of the 6 NEA agents using its corresponding folder in `Copilot_Agents/`:

| Agent Name (`<= 30` chars) | Folder in `Copilot_Agents/` | Config & Starters File | Instructions File | Knowledge Folder (`Ctrl+A` Upload) | Skills to Upload (`.zip` in `Skills/<skill-name>/`) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **`NEA Package Reviewer`** | `NEA_Package_Reviewer/` | `Agent_Config.md` | `Instructions.txt` (`5,330 / 8,000`) | `Knowledge/` (`5` `.txt` files) | `nea-anti-hallucination.zip`, `nea-verification-and-receipt.zip` |
| **`NEA BOM Builder`** | `NEA_BOM_Builder/` | `Agent_Config.md` | `Instructions.txt` (`3,820 / 8,000`) | `Knowledge/` (`6` `.txt` files) | `nea-anti-hallucination.zip`, `nea-workbook-entry-guard.zip`, `nea-verification-and-receipt.zip` |
| **`NEA CRL Builder`** | `NEA_CRL_Builder/` | `Agent_Config.md` | `Instructions.txt` (`3,342 / 8,000`) | `Knowledge/` (`6` `.txt` files) | `nea-anti-hallucination.zip`, `nea-workbook-entry-guard.zip`, `nea-verification-and-receipt.zip` |
| **`NEA Catalog Manager`** | `NEA_Catalog_Manager/` | `Agent_Config.md` | `Instructions.txt` (`3,794 / 8,000`) | `Knowledge/` (`7` `.txt` files) | `nea-anti-hallucination.zip`, `nea-workbook-entry-guard.zip`, `nea-verification-and-receipt.zip` |
| **`NEA Repair Tool`** | `NEA_Repair_Tool/` | `Agent_Config.md` | `Instructions.txt` (`3,607 / 8,000`) | `Knowledge/` (`6` `.txt` files) | `nea-anti-hallucination.zip`, `nea-workbook-entry-guard.zip`, `nea-verification-and-receipt.zip` |
| **`NEA Timesheet Consolidator`** | `NEA_Timesheet_Consolidator/` | `Agent_Config.md` | `Instructions.txt` (`6,206 / 8,000`) | `Knowledge/` (`5` `.txt` files) | `nea-anti-hallucination.zip`, `nea-workbook-entry-guard.zip`, `nea-verification-and-receipt.zip` |

---

## 2. Step-by-Step Procedure for Each Agent Folder

Inside each agent folder (`Copilot_Agents/NEA_Package_Reviewer/`, `NEA_BOM_Builder/`, `NEA_CRL_Builder/`, `NEA_Catalog_Manager/`, `NEA_Repair_Tool/`, and `NEA_Timesheet_Consolidator/`), you will find three clean items:

1. **`Agent_Config.md`**:
   - Contains the exact copy-paste blocks for **Name**, **Description**, **Instructions**, **Capabilities (`Code Interpreter = ON`)**, **Knowledge file checklist**, **Skills to upload**, and all **4 Starter Prompts** (each with its own `Title` and `Prompt` box).
2. **`Instructions.txt`**:
   - Pure raw `Instructions` text with no headers or wrappers. Open `Instructions.txt`, press **`Ctrl+A`** then **`Ctrl+C`**, and paste directly into the Agent Builder **Instructions** box.
3. **`Knowledge/`**:
   - Contains the exact Graph-safe domain Standards & Workflow `.txt` files for that agent (with zero duplicate Skill or Python files). In Agent Builder's **Knowledge** section, open the agent's `Knowledge/` folder, press **`Ctrl+A`** to select all `.txt` files at once, and upload them together.

---

## 3. Uploading Packaged Skill `.zip` Files (`Skills/<skill-name>/<skill-name>.zip`)

In Agent Builder's **Skills** section (`Add skill` $\rightarrow$ upload `.zip`):
- Navigate to `Skills/<skill-name>/` (see [`Skills/Skills_Deployment_Guide.md`](../Skills/Skills_Deployment_Guide.md)).
- Select **`<skill-name>.zip`** (for example, `Skills/nea-verification-and-receipt/nea-verification-and-receipt.zip`).
- Each `<skill-name>.zip` contains **`SKILL.md`** at the root of the archive plus **`scripts/inspect_nea_workbooks.py`**, mounting the deterministic OpenXML inspection, catalog lookup, non-destructive repair, and receipt engine directly inside the skill's packaged filesystem.

---

## 4. Daily Designer Operational Protocol (Zero OneDrive Indexing Latency)

1. **Always Attach Live `.xlsx` Files Directly into the Chat Box (`+` Button)**:
   - Click the **`+` (Attach / Upload from device)** icon inside the Copilot chat input box and select the live `.xlsx` file(s) from File Explorer (`OneDrive - NetCom`). Direct chat attachments mount immediately inside **Code Interpreter** (`/mnt/data/`) with **`0` SharePoint search indexing lag**.
2. **Follow Directional Cross-Duty Handoffs (`🔄 [CROSS-DUTY -> <Agent>]`)**:
   - Whenever `NEA Package Reviewer` detects overwritten formulas or OpenXML validation drift, it emits `🔄 [CROSS-DUTY -> NEA Repair Tool]`. Run the workbook through **`NEA Repair Tool`** (`--repair`) to restore formulas and validations non-destructively before re-running the project review.
