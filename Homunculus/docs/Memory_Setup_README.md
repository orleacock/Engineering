<div align="center">

# 🗂️ Homunculus Project Memory & Session Handoff Guide

**How Homunculus Organizes Your Projects, Isolates Brainstorm Notes & Picks Up After Long Breaks**

[**🏠 Main Cover Page**](../README.md) • [**🚀 Quick-Start Guide**](Quick_Start_and_Setup_Guide.md) • [**🧠 Capabilities Overview**](Capabilities_and_Architecture_Guide.md) • [**📟 Prompts & Command Deck**](Commands_and_Prompts_Reference.md) • [**🛡️ Data Safety**](Developer_Data_Safety_Guidelines.md) • [**❓ FAQ**](FAQ.md)

</div>

---

> [!TIP]
> **Works Automatically in the Background Across Windows, macOS & Linux**
> Once project memory is initialized, you do **not** have to update these files by hand. Your AI assistant reads and updates your project memory automatically during your normal chat sessions.

---

## 1. Overview: Standard Markdown or Obsidian (`Your Choice`)

Homunculus gives your AI a structured, file-backed memory folder so it knows where your files live on Turn 1, keeps verified specs separate from early rough notes, and remembers where you stopped between sessions.

You can use the exact same memory folder in two ways—and switch between them anytime:
1. **Standard Markdown Mode (`headless`, Default)**:
   - Uses clean, standard Markdown files (`memory/`) that open natively in VS Code, Cursor, Claude, Antigravity, or GitHub on **Windows, macOS, and Linux** with **zero third-party apps needed**.
2. **Obsidian Mode (`obsidian`)**:
   - Uses the exact same folder layout and adds optional **Obsidian** graph and table views for users who enjoy visual note-taking.
   - Switch between Standard Markdown and Obsidian anytime without losing a single note.

---

## 2. Folder Layout (`Clean & Self-Contained`)

Every project gets its own self-contained folder inside `memory/Projects/<Project>/`:

```text
memory/
├── README.md                                     # Workspace overview & project index
├── Projects/                                     # Self-contained per-project folders
│   └── <Project>/
│       ├── <Project>.md                          # Project Hub (File Map, Session Handoff, State Ledger)
│       ├── <Project>_Hardware.md                 # Hardware/CAD/Firmware summary (for hardware projects)
│       ├── <Project>_Software.md                 # Software/CLI/Schema summary (for software projects)
│       ├── <Project>_Lessons_Learned.md          # Key decisions & past bug fixes
│       ├── Templates/                            # Project-specific document templates (BOMs, quotes, checklists)
│       └── Quarantine/                           # Rough brainstorm notes & unverified vendor quotes
├── Tasks/                                        # Active task checklists organized by owner/client
├── Standards_and_Specs/                          # Shared standards & reference specs
├── Templates/                                    # Starter templates for new projects
└── Diagrams/                                     # Generated .svg and .png architecture diagrams
```

---

## 3. How the Memory System Helps You Day to Day

### A. Tailored to Software, Hardware, or Hybrid Projects
Instead of forcing every project into the same template, Homunculus keeps only the summaries your project actually needs:
- **Software Projects (`_Software.md`)**: Tracks code entrypoints, command-line options, data schemas, and test suites.
- **Hardware & Firmware Projects (`_Hardware.md`)**: Tracks 3D CAD dimensions, mounting holes, firmware pinouts, and verified bills of materials.
- **Hybrid Projects**: Tracks both side by side.

### B. Built-In Brainstorm Quarantine (`Keep Rough Ideas Separate from Final Specs`)
When you are early in a design, you often have rough ideas, wish-list features, or unconfirmed vendor quotes.
- Drop any unconfirmed notes into the project's **Quarantine** area.
- Homunculus automatically knows that quarantined notes are rough scratchpad items—preventing your AI from ever citing an unconfirmed brainstorm number as a finished specification until you verify and promote it.

### C. Multi-Client & Multi-Project Separation
If you work on multiple client projects or separate product lines on the same computer:
- Each project can be tagged with its owner or client (`entity:`).
- Homunculus keeps task lists and specifications strictly separated so details from `Client A` are never accidentally borrowed into `Client B`'s documentation.

### D. Session Handoffs (`Pick Up Weeks Later Without Context Loss`)
Real projects often pause for days or weeks at a time. Instead of losing your place or scrolling through an endless chat history:
- **Save Your Stopping Point**: At the end of a session, tell your AI: *"Save our stopping point for next time."* Homunculus records a rich summary (`500–800+ words`) of where you stopped, what was verified, any open blockers, and your next discussion points right inside `<Project>.md`—updating cleanly in place so the file never bloats.
- **Automatic File-Change Check When You Return**: When you come back weeks later and say *"Kickstart our project from memory,"* Homunculus loads your stopping summary and automatically checks if any files in your repository were edited while you were away.

### E. Reusable Project Templates
Whenever you create a recurring document layout for a project (such as a release checklist, customer quote sheet, or test card), your AI can save it in `Projects/<Project>/Templates/` so future drafts follow the exact same structure automatically.

---

## 4. Setting Up Project Memory (`Plain English` or `Terminal`)

### Option 1: Just Ask Your AI in Plain English (Recommended)
Paste this into your AI chat:
```text
Initialize Homunculus project memory at ./memory and set up a project folder for this repository.
```

### Option 2: Run Directly from Your Terminal (`Windows, macOS & Linux`)

**Windows (`PowerShell`):**
```powershell
# 1. Create the memory folder:
python Homunculus\skills\project-memory\scripts\sync_memory.py `
  --memory-root .\memory --init-memory --mode headless --default-entity "My_Team"

# 2. Add your project (choose software, hardware, or hybrid):
python Homunculus\skills\project-memory\scripts\sync_memory.py `
  --memory-root .\memory --init-project "My_Project" `
  --repo-path . --type software --entity "My_Team"
```

**macOS & Linux (`Terminal`):**
```bash
# 1. Create the memory folder:
python3 Homunculus/skills/project-memory/scripts/sync_memory.py \
  --memory-root ./memory --init-memory --mode headless --default-entity "My_Team"

# 2. Add your project (choose software, hardware, or hybrid):
python3 Homunculus/skills/project-memory/scripts/sync_memory.py \
  --memory-root ./memory --init-project "My_Project" \
  --repo-path . --type software --entity "My_Team"
```
