<div align="center">

# ❓ Homunculus User FAQ

**Answers on Ease of Use, OS Support, Project Memory, Custom Themes, Open-Source Licensing & Discord Support**

[**🏠 Main Cover Page**](../README.md) • [**🚀 Quick-Start Guide**](Quick_Start_and_Setup_Guide.md) • [**🧠 Capabilities Overview**](Capabilities_and_Architecture_Guide.md) • [**🗂️ Memory Guide**](Memory_Setup_README.md) • [**📟 Prompts & Command Deck**](Commands_and_Prompts_Reference.md) • [**🛡️ Data Safety**](Developer_Data_Safety_Guidelines.md)

</div>

---

## 📑 Quick-Jump FAQ Index

1. [Ease of Use & How Homunculus Compares to Stock AI](#1-ease-of-use--how-homunculus-compares-to-stock-ai)
2. [Windows, macOS, Linux & Work-Laptop Compatibility](#2-windows-macos-linux--work-laptop-compatibility)
3. [Project Memory, Obsidian & Picking Up After Breaks](#3-project-memory-obsidian--picking-up-after-breaks)
4. [Fact-Checking, Brainstorm Quarantine & Data Privacy](#4-fact-checking-brainstorm-quarantine--data-privacy)
5. [Custom Brand Colors & Optional Voice Matching](#5-custom-brand-colors--optional-voice-matching)
6. [Open-Source Licensing, Community Support, Ko-fi & Consulting](#6-open-source-licensing-community-support-ko-fi--consulting)
7. [Common Status Messages & Troubleshooting](#7-common-status-messages--troubleshooting)

---

## 1. Ease of Use & How Homunculus Compares to Stock AI

### Q1.1: Do I need to run terminal commands or learn complicated jargon to use Homunculus?
**No.** Homunculus is designed to work **automatically behind the scenes** while you talk to your AI assistant in plain English.
- Once you drop the `Homunculus` folder into your project and point your AI to `HOMUNCULUS_START_HERE.md`, your AI handles the memory lookups, fact-checking, skill organization, and session saving automatically.
- Direct terminal commands are included in the [Prompts & Command Deck](Commands_and_Prompts_Reference.md) purely as an optional bonus for users who like running checks from the command line or automated scripts.

### Q1.2: How is Homunculus different from a single `.cursorrules` or `CLAUDE.md` prompt file?
A single prompt file only asks the AI to "try to be careful." As soon as a conversation gets long or spans multiple files, stock AI models slip back into old habits: agreeing with flawed ideas, making up missing measurements or settings so sentences sound smooth, and forgetting earlier fixes.

Homunculus combines **Always-On Co-Engineering Rules** with **built-in local verification tools** and **structured Project Memory**. Instead of hoping the AI remembered your specs or didn't hallucinate a number, Homunculus actually checks the work against your project files on disk.

### Q1.3: Will Homunculus slow down quick questions or everyday coding?
**No.** Homunculus only loads its lightweight core rules at the start of a chat. Specialized tools (like diagram generation, documentation checking, or sandbox testing) wake up **on demand** only when needed, and heavy wrap-up checks are saved for the end of a milestone so your everyday chat stays fast and responsive.

### Q1.4: Is Homunculus only for 3D printing or hardware projects?
**No—it works equally well for pure software, hardware, firmware, or writing projects.** Homunculus automatically tailors its project memory to match what you are building: software projects track code entrypoints, commands, and tests, while hardware projects track 3D models, pinouts, and bills of materials.

---

## 2. Windows, macOS, Linux & Work-Laptop Compatibility

### Q2.1: Which operating systems and AI tools are supported?
- **Operating Systems**: Works seamlessly across **Windows, macOS, and Linux** using standard built-in Python (3.10+) with zero external packages to install.
- **AI Assistants & IDEs**: Works out of the box with **Cursor**, **Claude Code**, **Claude Cowork**, **Antigravity / Gemini CLI**, **Windsurf**, **Cline**, **Aider**, and any tool that reads `AGENTS.md` or project markdown files.

### Q2.2: Can I use Homunculus on a locked-down work laptop without Admin rights?
**Yes.** That is why **Zero-Install "Drop-In & Point" Mode** is the default way to use Homunculus:
- It requires **no Administrator / `sudo` rights**, **no system installers**, and **no external package downloads (`pip` / `npm`)** that corporate firewalls might block.
- You simply unzip the folder into your project and tell your AI assistant to read `Homunculus/HOMUNCULUS_START_HERE.md`.

---

## 3. Project Memory, Obsidian & Picking Up After Breaks

### Q3.1: Do I need to use Obsidian for the memory system to work?
**No.** By default, Homunculus stores project memory in standard Markdown folders (`memory/`) that open natively in VS Code, Cursor, Claude, GitHub, or any text editor on Windows, macOS, and Linux.
If you *do* use **Obsidian** (or want to try it later), you can switch your memory folder to Obsidian mode anytime with a single command—and switch back whenever you like.

### Q3.2: How does Homunculus help when I pause a project for days or weeks?
Whenever you finish a work session, just tell your AI: *"Save our stopping point for next time."*
1. **Rich Session Handoff**: Homunculus saves a detailed summary (`500–800+ words`) of where you left off, what was verified, any open blockers, and your next discussion points directly inside your project hub—replacing the old handoff cleanly so your file never gets cluttered.
2. **Automatic File-Change Check on Return**: When you return weeks later and ask to pick up where you left off, Homunculus immediately checks if any project files were edited while you were away and briefs you on what changed before resuming work.

### Q3.3: Where can I put rough brainstorm notes so the AI doesn't confuse them with final specs?
Every project folder in memory has a built-in **Quarantine** area. Drop rough ideas, early vendor quotes, or wish-list notes there—Homunculus automatically keeps quarantined notes separate from your verified production specs until you confirm they are ready.

---

## 4. Fact-Checking, Brainstorm Quarantine & Data Privacy

### Q4.1: What happens when a measurement or setting hasn't been decided yet?
Instead of guessing a random number or writing vague instructions that hide the missing detail, Homunculus inserts a clear, searchable **`[TBD]`** tag (or **`[CONFLICT]`** if two files disagree) and gives you a clean checklist of items that still need your decision.

### Q4.2: How does Homunculus protect private credentials and separate client projects?
- **Secret Protection**: Prevents your AI from reading or printing `.env` files, private SSH keys, or API tokens into chat transcripts, and includes ready-made ignore files (`.cursorignore`, `.claudeignore`, `.geminiignore`).
- **Multi-Project & Client Separation**: Keeps different client projects or public/private repositories isolated so specifications or local computer paths from one project never leak into another.
- **100% Offline Execution**: Homunculus makes **zero** external network calls, telemetry pings, or license checks.

---

## 5. Custom Brand Colors & Optional Voice Matching

### Q5.1: Can I change the Alchemical-3D pink/dark-slate color scheme to my own brand colors?
**Yes, easily.** This GitHub manual uses the Alchemical-3D colors simply because Homunculus is our product.
Your own projects are never locked to our theme: Homunculus includes neutral dark and light engineering palettes out of the box, and you can prompt your AI with your own brand hex colors anytime (see the [Community Extension SDK](../templates/community_sdk/README.md)).

### Q5.2: How do the optional side-loaded add-ons (`author-voice-cadence` and `gmail-workspace-assistant`) and `/teach-me` work?
- **`addons/author-voice-cadence/`**: Stays dormant on Day 1 so it never gets in your way. Whenever you want the AI to write devlogs, documentation, or posts in your natural voice, drop writing samples into `corpus_inbox/` and ask the AI to activate the add-on.
- **`addons/gmail-workspace-assistant/`**: Optional side-loaded add-on for multi-account Gmail MCP triage, `visibility_radar` inbox auditing, and safe draft staging.
- **`skills/teach-me/` (`Brief+`)**: Active core skill that runs `/teach-me` queries in a throw-away subagent, saves a verified `Brief+` lesson in the non-consumed `study_briefs/` folder, and returns a compact Datasheet Card to chat.

---

## 6. Open-Source Licensing, Community Support, Ko-fi & Consulting

### Q6.1: Where do I download Homunculus, get support, or share feedback?
- **Download (`Free & Open Source`)**: Clone `https://github.com/Alchemical-3D/Homunculus.git` or download the latest release archive (`Homunculus-v1.0.0.zip`) from [**GitHub Releases**](https://github.com/Alchemical-3D/Homunculus/releases) with zero cost to entry.
- **Open Community Discord**: Join the [**Alchemical-3D Discord**](https://discord.gg/aE49DW2xXe) for open access to support (`#homunculus-support`), release announcements (`#homunculus-releases`), and development (`#homunculus-dev`) channels.
- **Offering Feedback & Reporting Issues (`Discord` or `GitHub Issues`)**: We love hearing how Homunculus is working in your projects! Share feedback, suggest new features, or report issues either in the **[Alchemical-3D Discord](https://discord.gg/aE49DW2xXe)** or directly via this repository's **[GitHub Issue Tracker](https://github.com/Alchemical-3D/Homunculus/issues)**.
- **Supporting Ongoing Development (`Ko-fi`)**: If Homunculus saves you time or prevents rework and you would like to support the project, consider [leaving a tip on Ko-fi](https://ko-fi.com/alchemical3d).

### Q6.2: Can I use Homunculus for commercial, employer, or paid client work?
**Yes.** Under the open-source **Apache License, Version 2.0 (`Apache-2.0` — see [`LICENSE.md`](../LICENSE.md))**:
- You have full rights to use, modify, and customize Homunculus across unlimited personal, academic, employer, commercial, and client projects with zero cost to entry.
- **100% Output Ownership**: Every code file, document, diagram, and deliverable you create with Homunculus belongs 100% to you (or your client/employer) with zero royalties.
- **Simple Attribution Condition**: If you redistribute Homunculus or a modified fork of Homunculus (`rules/`, `skills/`, `adapters/`, `scripts/`, `templates/`), preserve the original `Alchemical-3D` copyright notice and [`LICENSE.md`](../LICENSE.md).

### Q6.3: Do you offer consulting, custom workspace deployment, or workshops for teams and larger organizations?
**Yes.** If you would like hands-on assistance setting up and deploying Homunculus across your workspace, building custom domain skills and templates for your workflow, or hosting live workshops for your engineering or development team, we offer dedicated consulting and training services.
- **Contact Us**: Email **[we@alchemical3d.net](mailto:we@alchemical3d.net)** or message us in the **[Alchemical-3D Discord](https://discord.gg/aE49DW2xXe)**.

---

## 7. Common Status Messages & Troubleshooting

| Message / Situation | What It Means | What to Do |
| :--- | :--- | :--- |
| **`[TBD: <item>]`** | A measurement, count, or setting needed for a document isn't defined in your project files yet. | Fill in the final value in your project files (or leave `[TBD]` until the design is finalized). |
| **`[CONFLICT]`** | Two files in your project list different numbers for the same item. | Confirm which number is authoritative so the AI can update both places cleanly. |
| **`DRIFT_DETECTED` (when resuming a project)** | Files in your repository were edited or committed since your last saved Session Handoff. | Ask your AI to review the recent file changes and refresh the project memory map. |
| **`[EXTRACTION BLOCKED — ABORTED]`** | A file path requested for verification was missing or unreadable. | Check that the file path exists in your workspace. |
| **`python3: command not found` on Windows** | Windows often names the Python command `python` or `py -3`. | Use `python` or `py -3` when running optional terminal commands on Windows. |

---

<div align="center">

**Have another question?** Open a ticket in the **GitHub Issue Tracker** or join us in the [**Alchemical-3D Discord**](https://discord.gg/aE49DW2xXe).

</div>
