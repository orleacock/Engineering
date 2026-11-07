<div align="center">

# 🧠 Homunculus Capabilities Overview

**What Is Included in Homunculus—and How It Works Automatically Behind the Scenes**

[**🏠 Main Cover Page**](../README.md) • [**🚀 Quick-Start Guide**](Quick_Start_and_Setup_Guide.md) • [**🗂️ Memory Guide**](Memory_Setup_README.md) • [**📟 Prompts & Command Deck**](Commands_and_Prompts_Reference.md) • [**🛡️ Data Safety**](Developer_Data_Safety_Guidelines.md) • [**❓ FAQ**](FAQ.md)

</div>

---

## 1. Designed for Effortless Day-to-Day Use

The biggest misconception about advanced AI frameworks is that they require you to learn a complex new workflow or constantly run terminal scripts.

**Homunculus is built to run automatically behind the scenes:**
- **You talk to your AI assistant in plain English**, just like you always do.
- **Behind the scenes**, Homunculus gives your AI a structured engineering memory, a set of always-on quality rules, and built-in verification tools that check facts, math, and project state automatically before work is finished.
- **Cross-Platform Out of the Box**: Everything in Homunculus works identically across **Windows, macOS, and Linux** using standard built-in Python—with zero external packages to install and zero internet/cloud dependencies.

```mermaid
%%{init: {"theme": "base", "themeVariables": {"darkMode": true, "background": "#1E1E24", "primaryColor": "#282830", "primaryTextColor": "#F5F5F7", "textColor": "#F5F5F7", "tertiaryTextColor": "#F5F5F7", "primaryBorderColor": "#FF3985", "lineColor": "#808080", "secondaryColor": "#363642", "tertiaryColor": "#141417", "edgeLabelBackground": "#141417"}, "flowchart": {"nodeSpacing": 24, "rankSpacing": 30, "curve": "basis", "padding": 12}}}%%
flowchart LR
    User["You Ask in Plain English"] --> Rules["Core Co-Engineering Rules — Checks Assumptions First"]
    Rules --> Memory["Project Memory — Finds Files & Past Context Instantly"]
    Memory --> Check["Automatic Fact & Hygiene Checks — Verifies Specs & Protects Data"]
    Check --> Output["Clean, Verified Output + Saved Stopping Point"]

    classDef brandPink fill:#282830,stroke:#FF3985,stroke-width:2.5px,color:#FFFFFF;
    classDef brandCrimson fill:#282830,stroke:#C90448,stroke-width:2.5px,color:#F5F5F7;

    class User,Output brandPink;
    class Rules,Memory,Check brandCrimson;
```

---

## 2. Always-On Co-Engineering Guardrails

Every Homunculus session is guided by three core behavioral standards that keep your AI focused on accuracy rather than empty flattery:

| Capability | What Problem It Solves | What It Does for You Automatically |
| :--- | :--- | :--- |
| **1. Co-Engineering Partner & State Ledger** | Stock AI agrees with broken ideas at Step 1 and often breaks Feature A while fixing Bug B. | • **Checks Foundations First**: Verifies key assumptions before writing dependent code.<br>• **Tracks Project State**: Maintains a live ledger of what is locked, what is already solved, and what is still open so new edits don't regress working features.<br>• **Waits for Your Go-Ahead**: Never pushes code or alters shared systems until you confirm you are ready. |
| **2. Verifiable Accuracy & Honest `[TBD]` Tagging** | Stock AI invents "typical" numbers when a spec is missing or writes vague sentences that hide missing details. | • **No Made-Up Numbers**: Every measurement, count, pin, fastener, or setting must trace to your real project files.<br>• **Clear `[TBD]` & `[CONFLICT]` Markers**: If a specification isn't decided yet—or two files disagree—the AI flags it clearly so you can decide, instead of guessing silently. |
| **3. Credential & Project Privacy** | Stock AI can accidentally read local secret files into chat logs or mix up data between different clients. | • **Protects Secrets**: Prevents private keys, `.env` files, and tokens from being read or printed into chat.<br>• **Separates Projects & Clients**: Keeps personal notes, public repos, and separate client projects strictly isolated. |

---

## 3. Project Memory & Multi-Week Session Continuity

When a project spans multiple days, weeks, or repositories, standard AI chat sessions lose the thread. Homunculus includes a structured **Project Memory** system ([`docs/Memory_Setup_README.md`](Memory_Setup_README.md)) that keeps your workspace organized automatically:

1. **Works in Standard Markdown Folders (or Obsidian)**:
   - By default, memory lives in clean, standard Markdown files (`memory/`) that you can read in any code editor on Windows, macOS, or Linux with **zero third-party apps required**.
   - If you enjoy using **Obsidian**, you can switch your memory folder into Obsidian mode with a single command (and switch back anytime).
2. **Instant Turn-1 Project Map**:
   - Instead of the AI spending the first five minutes of every chat searching folders to find where your code or CAD files live, each project hub keeps an up-to-date map of your files and key specifications.
3. **Dedicated Hardware & Software Indexes**:
   - Software projects track entrypoints, commands, and test suites; hardware and firmware projects track 3D model dimensions, mounting holes, pinouts, and bills of materials—without cluttering pure software repos with hardware tables (or vice versa).
4. **Built-In Brainstorm Quarantine**:
   - Every project includes a dedicated **Quarantine** area for rough ideas, vendor quotes, and early brainstorm notes. Homunculus knows those notes are unverified scratchpad items and will never cite them as finished specifications until you promote them.
5. **Session Handoffs (Pick Up Right Where You Left Off)**:
   - When you finish working for the day, ask your AI to save a **Session Handoff**. It records a detailed summary (`500–800+ words`) of where you stopped, what was verified, and what to discuss next—updating cleanly in place without creating an endless log file.
   - When you come back days or weeks later, Homunculus loads your stopping point and automatically checks whether any files in your repository were edited while you were away.

---

## 4. Built-In Fact & Document Checking

When you are preparing a technical specification, README, bill of materials, or assembly guide, Homunculus includes an automated **Claim & Document Checker** that acts like a second set of engineering eyes:

- **Cross-Checks Specs Against Your Real Files**: Verifies that quantities, dimensions, part callouts, config settings, and line references in your documentation match your actual project files.
- **Checks Unit Math**: Verifies inline engineering calculations (such as power, current, dimensions, or tolerances) so unit conversion mistakes are caught before they reach production.
- **Catches Vague Assembly Instructions**: Flags assembly steps that mention hardware without specifying how many or what size, ensuring your guides are complete and build-ready.
- **Verification Receipts**: Produces a clean verification summary confirming which source files were checked.

---

## 5. Skill Architect & Hygiene Manager

Many users love creating custom AI skills and rules for recurring tasks—but over time, custom prompts often turn into a tangled mess of duplicate instructions that slow down the AI and eat up context space.

Homunculus includes **Skill Architect**, a two-mode assistant for building and maintaining custom AI capabilities:

- **Mode 1 — Smart Skill Builder (`Create & Extend`)**:
  - When you want to teach your AI a new workflow, Skill Architect checks your existing rules and skills first. If a similar skill already exists, it helps you extend that skill cleanly instead of creating overlapping duplicates.
- **Mode 2 — Non-Destructive Hygiene Audit (`Review & Clean Up`)**:
  - Audits your workspace skills for duplicate boilerplate, broken file links, and context-wasting habits.
  - **100% Permission-First**: Skill Architect never deletes your custom workflows behind your back—it presents clear, optional cleanup recommendations and waits for your approval.

---

## 6. Subagents, Safe Testing Sandbox & Visual Studio

### Parallel Subagent Coordinator
- On larger multi-file tasks, Homunculus can delegate focused research or audit tasks to background subagents using your project memory map—saving main-chat context while letting you steer speed vs. depth with simple **`[lite]`**, **`[fast]`**, or **`[deep]`** tags in your prompt.

### Isolated Testing Sandbox
- Before marking complex code, parser, or skill changes complete, Homunculus can test them in an isolated temporary workspace across **Windows, macOS, and Linux**—making sure everything passes (and nothing breaks on your live files) before you commit.

### Visual Studio & Custom Brand Color Themes
- Need a clean system architecture diagram, dataflow chart, wiring/pinout map, or side-by-side comparison card? Homunculus renders crisp `.svg` and high-resolution `300 DPI .png` diagrams offline in fractions of a second.
- **Use Your Own Colors**: While our documentation uses the Alchemical-3D pink and dark-slate palette, you can switch to neutral engineering themes or prompt your own brand colors at any time (see the [Community Extension SDK](../templates/community_sdk/README.md)).

### Optional Author Voice & Cadence Add-On
- Included inside `addons/author-voice-cadence/`, this optional module stays out of your way on Day 1. Whenever you want your AI to draft blog posts, devlogs, or READMEs in your natural writing voice, drop a few samples of your own writing into a local folder and activate the add-on in seconds.

---

<div align="center">

**Next Step:** See how easy it is to run in the [**🚀 Quick-Start Guide**](Quick_Start_and_Setup_Guide.md), browse copy-pasteable prompts in the [**📟 Prompts & Command Deck**](Commands_and_Prompts_Reference.md), or read the [**❓ Buyer & User FAQ**](FAQ.md).

</div>
