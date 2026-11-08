---
project: "Homunculus"
parent_note: "Homunculus"
entity: "Alchemical-3D"
compartment: "cleanroom"
last_synced: "2026-11-05"
---

# 🧬 Homunculus — Public Positioning, Architecture Talking Points & Adoption Guide

Part of the [`README.md`](../../README.md) and companion positioning reference for [`Homunculus`](Homunculus.md) (`https://github.com/Alchemical-3D/Homunculus`).

> [!NOTE]
> **Purpose of This Document**
> This file captures core positioning, architectural talking points, and practical engineering examples for **Homunculus**. It is structured so individual sections and thesis statements can be adapted directly into the public-facing GitHub `README.md`, companion SDK documentation, release announcements, and workshop materials.

---

## 1. Fast vs. Right: Why Accuracy Finishes Deep Projects Sooner

**Core Hook:** *Do you want a snappy answer right now, or do you want a finished project that actually works?*

When a task is trivial—like writing a five-line regex or formatting a single JSON block—a fast, off-the-cuff chat response is fine. Once a project has real engineering depth to it though, chasing fast responses almost always slows you down.

If an AI guesses a load-bearing detail at Step 1 to look responsive, that unverified assumption gets buried under Steps 2 through 10. You do not discover the crack in the foundation until your assembly fails to align, your schema breaks downstream scripts, or your BOM counts do not match the CAD on disk, which forces hours of destructive rework to tear down and rebuild the upper layers.

**Homunculus** is built around an explicit governing priority law (`1. Accuracy -> 2. Efficiency -> 3. Speed`):
- **Speed Through First-Pass Truth:** We do not trade accuracy away for speed, because eliminating cascading rework on the first pass is the fastest path to a finished product.
- **Pre-Cascade Halts (`Tier A`):** When a missing specification, conflicting source, or unverified interface affects downstream architecture or safety, the system halts immediately before writing dependent code or documentation.
- **End-of-Pass Batching (`Tier B`):** For narrative documentation where missing figures do not corrupt downstream logic, the agent drafts continuously with explicit `[TBD: <specific_missing_variable>]` markers and validates everything in a single pass at the end.

---

## 2. Why Homunculus Beats Raw API Calls & Stateless Chat Apps

**Core Hook:** *A chat box is a conversation window, not an engineering environment.*

Talking directly to a model through a browser chat app or a raw API call means starting from amnesia every morning. A standard chat thread has no persistent state accounting, no structural map of your repository, no memory of why a constraint was locked last week, and no deterministic tooling sitting between the model's claims and your actual files on disk.

You end up burning half your time re-explaining context, pasting file trees into prompts, and manually checking whether the model quietly broke yesterday's fix while solving today's bug.

**Homunculus** turns the AI client into a structured, persistent development environment:
- **Dual-Mode Project Memory (`Headless` vs. `Obsidian`):** Connects the agent to structured project dossiers, pre-indexed `AUTO-TREE` file maps, hardware/system manifests, and single-writer task queues—either in pure CLI/Markdown mode (safe for Git, SharePoint, and OneDrive) or full Obsidian Visual-Brain mode (`.base` portfolio tables and semantic `graph.json` maps).
- **Deterministic Tooling Loop:** Instead of asking the model to eyeball raw files in its context window, `Homunculus` equips the workspace with zero-dependency Python CLIs, copy-on-write OS dry-run sandboxes, and automated pre-commit gates.
- **Multi-Client Portability:** Rather than locking your workflow inside one vendor's chat UI, `Homunculus` binds the same rules, skills, and memory architecture across **Universal `AGENTS.md`**, **Antigravity / Gemini CLI**, **Claude Code**, **Claude Cowork**, and **Cursor** (with dedicated **MS365 / Copilot** packaging evaluated post-core).

---

## 3. Co-Engineering: Being Helpful and Being Truthful Are Not Exclusive

**Core Hook:** *A yes-man is not a partner. In engineering, being truthful is how you are actually helpful.*

Out of the box, most language models are trained to optimize for conversational comfort. They validate flawed premises (*"Great idea!"*), silently water down difficult requirements so they can hand back a completed checklist, and paper over root-cause bugs with superficial band-aids (like swallowing exceptions or hardcoding fallback values). That feels polite in the chat window, but it's toxic to an engineering project.

**Homunculus** replaces performative agreement with **Co-Engineering Partnership (`Truth > Comfort`)**:
- **Lock the Concept, Audit the Path:** The user's core objective (**The Concept**) is treated as sacred—the agent will never silently dilute a requirement or stub out real logic just to finish a turn. If the proposed *implementation path* has a structural flaw, scaling bottleneck, or interface mismatch though, the agent calls it out immediately with concrete evidence and proposes a viable alternative.
- **Verify Load-Bearing Pillars First:** Before building upper layers, the agent separates verified facts (proven via file reads, AST/CAD telemetry, or test probes) from unverified assumptions.
- **Root-Cause Engineering Over Symptom Patching:** Band-aids that hide structural rot are strictly banned, and the agent traces callers (`Chesterton's Fence`) to understand why an existing constraint exists before modifying it.

---

## 4. Stopping Drift & Scope Creep: The Enemies of Finished Products

**Core Hook:** *Projects rarely die from a single hard problem—they die from regression drift and unchecked scope creep.*

Anyone who has used AI on a multi-week build has watched two failure modes play out. First is **regression drift**: you ask the agent to fix Problem B, and in the process it silently overwrites or breaks Solved Item A from earlier in the build. Second is **scope creep**: you ask for a targeted fix, and the agent refactors unrelated modules, invents single-use abstractions you didn't ask for, and leaves half-finished tasks scattered across multiple markdown files.

**Homunculus** locks down both failure modes structurally:
- **The Project State Ledger:** Every complex workflow maintains a live ledger tracking the locked **Concept**, the protected **Established Protocol & Solved Log** (`[SOLVED]` and `[PROTOCOL]` invariants), and the active **Outstanding Problems Log** (`[LOAD-BEARING]` vs. `[ISOLATED]`). Before making any structural change, the agent runs a mandatory **Blast-Radius & Protocol Threat Check** against every `[SOLVED]` item and halts if a conflict is detected.
- **Single-Writer Task Umbrellas:** Tasks live in canonical domain queues (and transclude into project dossiers via `> **Active Task Queue**: Tracked in `...` *(Single-Writer Task Umbrella)*.` in Obsidian mode) so to-do lists never split or drift out of sync across files.
- **Minimum Viable Code & Surgical Blast Radius:** The framework enforces touching only the lines directly traceable to the request—no unrequested features, no speculative configurability, and no drive-by refactoring churn.

---

## 5. Codified Rules vs. Tacit Engineering Practice

**Core Hook:** *Standard prompts only capture instructions. Homunculus packages tacit engineering intuition into codified infrastructure.*

Every seasoned engineer relies on two layers of knowledge:
1. **Codified Practices:** Explicit formulas, pinout tables, style guides, data schemas, and release checklists that are easy to write down.
2. **Tacit Practices:** The hard-won, unspoken shop-floor and systems judgment built from years of breaking things and fixing them—knowing *which* assumption to test first, *why* a seemingly harmless shortcut will cause a clearance or schema collision three steps later, when to stop digging and ask a question, and how to isolate an untrusted change before letting it touch production.

When people try to use AI through ad-hoc prompting, they have to supply all of that tacit judgment manually on every turn. If you forget to tell the model to check for downstream callers or boundary leaks once, it doesn't check.

**Homunculus** bridges that gap by turning tacit engineering habits into codified, self-enforcing runbooks (`rules/` and `skills/`):
- **Pre-Flight Foundation Checks:** Every skill encodes what must be verified as fact before execution even begins.
- **Step-Level Verification Gates:** The agent must prove each stage succeeded empirically (via test suites, sandbox dry-runs, or claim audits) before advancing to the next step.
- **Explicit Stop & Escalation Conditions:** Rather than improvising a brittle workaround when a tool fails or two sources disagree, the agent hits a hard stop gate (`[EXTRACTION BLOCKED — ABORTED]` or `[TBD: CONFLICT — ...]`) and surfaces the exact discrepancy.

---

## 6. Subagent Orchestration & Parallel Swarming Mechanics

**Core Hook:** *Stop burning your main context window on directory wandering and repetitive file reads.*

In a standard single-thread agent session, asking a question across three repositories or ten files causes the primary model to run `ls`, `find`, and full-file reads sequentially. By the time it finds the relevant lines, your context window is bloated with raw file dumps, KV-cache costs compound on every turn, and the model's attention on your actual problem degrades.

**Homunculus** uses `subagent-orchestrator` to run **Turn-1 Parallel Scatter-Gather Swarms**:
- **Zero-Discovery Dispatch:** Instead of letting subagents wander around with `ls` or `find`, the primary thread passes pre-indexed `AUTO-TREE` repository maps and hardware/system manifests directly to `2–4` concurrent workers on Turn 1.
- **Anchored Evidence Packets (`Zero Double-Reads`):** Subagents do not dump whole files back into the main thread. They return compact **Anchored Evidence Packets** containing the exact `path#Lstart-Lend` coordinate, a verbatim `1–3` line hunk, and a cryptographic `SHA-256` / `VRF` receipt—allowing the primary thread to cite and patch with **zero double-reads**.
- **Single-Writer Vault & Fail-Closed Shards:** Read-only `research` scouts and pipe-free `self` CLI inspectors tag every finding epistemically (`[VERIFIED FACT]`, `[CLI TELEMETRY]`, `[TBD]`, `[CONFLICT]`) and return `[VAULT_DELTA]` summaries without mutating project memory directly, preventing race conditions across parallel workers.

---

## 7. The "Truth Oracle": Deterministic Verification Over LLM Self-Grading

**Core Hook:** *Asking an LLM to grade its own factual accuracy with more text prediction is circular. You need an external Truth Oracle.*

This connects directly back to **Fast vs. Right (Note #1)** and **Truthful Co-Engineering (Note #3)**. Language models are probabilistic engines, which means if a model invents a fastener length, miscalculates a power budget, or cites the wrong port number, asking it *"Are you sure?"* in chat often just produces a more confident hallucination. Worse, when a model doesn't know a required value, its default instinct is **silent qualitative dodging**—writing smooth, vague prose around the missing number (like *"secure with M3 screws"* without specifying the length or head style) so you don't notice the gap until assembly day.

**Homunculus** backs the model with deterministic, zero-dependency Python **Truth Oracles** (`verify_claims.py` and domain telemetry inspectors):
- **Closed-World Parametric Lock (`verify_claims.py`):** Audits every quantitative figure, unit, tolerance, part identifier, pin/port designator, and `#Lstart-Lend` line citation in a draft against authoritative source files on disk.
- **Dimensional Arithmetic Verification (`[CALC: ...]`):** Parses inline engineering calculations and verifies both the math and the physical dimensionality (preventing dimensional alchemy where incompatible units are combined).
- **Anti-Goodhart `[TBD]` Enforcement:** Bans silent qualitative dodging by requiring explicit, machine-searchable `[TBD: <specific_missing_variable>]` or `[TBD: CONFLICT — <source_A> vs <source_B>]` tags whenever a spec is absent or contested—quarantining open `[TBD]` ledgers so the agent is never rewarded for hiding missing data.
- **Black-Box Domain Inspectors & `SHA-256` Receipts:** Rather than reading raw multi-megabyte `.step`/`.stl` CAD files or `.xlsx` OpenXML workbooks into the prompt, agents call deterministic CLI inspectors to extract exact bore diameters, bounding boxes, and workbook formulas, finishing with a tamper-evident `VRF-<12hex>` `SHA-256` verification receipt.

---

## 8. Model Weight Automation: Right-Sizing Compute Across Subagents (and Beyond)

**Core Hook:** *Don't bring a frontier reasoning model to a one-line lookup, and don't trust a lightweight model with a foundational architecture audit.*

Most AI setups force you to pick one model weight for your entire session. If you leave a heavyweight frontier model running for everything, you pay a steep latency and token tax on simple file lookups and formatting checks. If you switch to a lightweight model to save time, it misses subtle cross-file dependencies and introduces structural cracks.

**Homunculus** automates **Model Weight & Tier Routing** across subagent swarms:
- **Deterministic Tier Floor (`Routing = max(Question_2_Floor, Inline_Tag)`):** Blind `'inherit'` model defaults are banned. Tasks are automatically classified—or steered inline via `[lite]`, `[fast]`, and `[deep]` tags—into explicit weight tiers (`flash_lite` for single-fact probes, `flash` for standard multi-file extraction and CLI telemetry, and `pro` for complex cross-shard synthesis, Mode A/B1 authoring, and adversarial audits).
- **Safety Floor Protection:** Even if a prompt includes a casual speed tag, the complexity floor prevents a high-risk architectural or multi-source reconciliation task from downgrading to a model weight that cannot handle it safely.
- **Future Horizon — Main-Thread Weight Automation:** While dynamic model weight routing currently governs subagent dispatches (`subagent-orchestrator`) and sandbox evaluation frames (`Blind-Light` vs. `Blind-Full`), the exact same complexity-floor routing matrix is designed to extend to the **primary thread** as host runtimes open up programmatic mid-session model switching—allowing a session to cruise on fast mid-tier weights during routine execution and automatically shift into deep reasoning weights when a `[LOAD-BEARING]` architectural gate appears.

---

## 9. Deployment Flexibility, Workshops & Enterprise Consulting

**Core Hook:** *Built to drop cleanly onto everything from a custom Linux rig to a locked-down corporate Windows laptop—backed by hands-on training and custom integration.*

A common reason engineering teams abandon AI frameworks is deployment friction: tools assume everyone has root access on Linux or macOS, require complex Python virtual environments, or break immediately inside corporate IT environments that block unsigned scripts, symlinks, and external `pip` registries.

**Homunculus** is engineered for zero-friction adoption across individuals and organizations:
- **Single Cross-OS Archive (`1. Linux -> 2. macOS -> 3. Windows`) with Dual Deployment:**
  - **Track 1 — Automated Installer (`install.sh` / `install.ps1`):** One-command adapter wiring for developer workstations where local permissions allow.
  - **Track 2 — Zero-Install "Drop-In & Point" Mode (`Locked-Down Corporate IT Safe`):** Pure Python standard-library and Markdown architecture (`HOMUNCULUS_START_HERE.md`) that runs by simply unzipping the folder into a workspace—requiring **zero** admin privileges, **zero** script installation, **zero** symlinks, and **zero** `pip` dependencies.
- **Open-Source `Apache-2.0` Licensing (`Zero Cost to Entry` + `Ko-fi` & Consulting):**
  - **Open-Source Core & SDK (`Apache-2.0`):** Ships 100% readable, editable Python and Markdown source code on GitHub with zero cost to entry, permitting unlimited personal, day-job, and client commercial engineering work (unlike `CC BY-NC` licenses that block corporate/day-job adoption) while requiring `Alchemical-3D` copyright attribution on redistribution and providing explicit patent grant protection.
  - **Voluntary Support (`Ko-fi`) & Commercial Services:** Supported by voluntary community contributions at `https://ko-fi.com/alchemical3d` alongside 1-on-1 workspace setup consulting, custom domain skill engineering, and live team workshops (`we@alchemical3d.net`).
- **Hands-On Workshops & Team Enablement:**
  - Structured live workshops walking engineering teams and technical creators through setting up Dual-Mode Memory, building project state ledgers, running parallel subagent swarms, and eliminating hallucinated specs from their documentation and takeoff pipelines.
- **Custom Consulting & Enterprise Onboarding:**
  - Direct consulting engagements to tailor `Homunculus` for specialized company workflows—including custom multi-compartment data/credential firewalls (`data-and-credential-safety`), bespoke domain Truth Oracles (custom CAD, ERP, workbook, or hardware config inspectors), and locked-down enterprise adapter deployments (`Claude Cowork`, `Cursor`, and `MS365 / Copilot` environments).

---

## 10. Synergistic Skill Building, Anti-Bloat & Permission-Based Cleanup (`skill-architect`)

**Core Hook:** *Custom skills should compound your system's strength—not fight your memory architecture or burn turns on redundant work.*

As teams build out their own custom AI skills and rules over time, two quiet failure modes creep in:
1. **Skill Bloat & Friction:** Users write new skills from scratch that accidentally fight the existing framework—creating competing todo lists instead of using single-writer task queues, telling the agent to run `ls`/`find` instead of reading `AUTO-TREE` maps, or repeating generic rules across ten different files.
2. **Mid-Session Churn:** Agents waste turns re-rendering diagrams mid-project before edits are finished, rebuilding indexes on every keystroke, or pushing updates to remote servers before the user is ready.

**Homunculus** prevents skill rot and mid-session bloat without acting like an authoritarian gatekeeper that deletes domain context it doesn't understand:
- **Always-On Anti-Bloat & User-Readiness Discipline (`co-engineering-partner`):** The core rule prohibits mid-project visual/index churn (deferring derived updates to the single `pre-commit-gate` pass at task completion) and blocks external server pushes or shared-state mutations until the user explicitly confirms readiness.
- **Mode 1 — Synergistic Skill Builder (`Create / Extend`):** When you want a new capability, `skill-architect` first checks if an existing skill already covers 70%+ of the job and can simply be extended. When a new skill is warranted, it automatically wires the skill into **Dual-Mode Memory**, **Truth Oracles**, and **`pre-commit-gate`**, authoring only the lean domain-specific delta.
- **Mode 2 — Permission-Based Cleanup Protocol (`Audit / Consolidate`):** Backed by `audit_skill_hygiene.py`, the cleanup protocol audits user-created skills and functions for overlapping triggers, duplicated core rules, and turn-wasting patterns—presenting context-aware, opt-in recommendations (`[KEEP — DOMAIN SPECIFIC]`, `[SUGGESTED TRIM]`, `[CANDIDATE MERGE]`, `[TURN-WASTE HAZARD]`) so you stay in 100% control of your domain workflows.

---

## 📊 Quick Comparison Matrix (For Public README / Pitch Deck Use)

| Capability Dimension | Raw API / Standard Chat App ❌ | Ad-Hoc Prompt Templates ⚠️ | **Homunculus Framework** ✅ |
| :--- | :--- | :--- | :--- |
| **Speed vs. Accuracy** | Fast initial replies followed by cascading rework when guesses fail | Relies on the LLM remembering prompt warnings | **`1. Accuracy -> 2. Efficiency -> 3. Speed`** enforced by pre-cascade halts |
| **Engineering Posture** | Agreeable yes-man that validates flawed premises | Persona prompt that degrades over long sessions | **Co-Engineering Partner (`Truth > Comfort`)** with load-bearing foundation checks |
| **Scope & Regression Control** | Frequent regression of solved items and unrequested refactors | Manual copy-pasting of todo lists | **Project State Ledger (`[SOLVED]` / `[PROTOCOL]` gates)** + Single-Writer Task Umbrellas |
| **Factual & Math Verification** | LLM self-grading (circular text prediction) | Prompt instructions to *"double-check your numbers"* | **Deterministic Python Truth Oracles (`verify_claims.py`)** + `VRF` `SHA-256` receipts |
| **Multi-File Context Handling** | Sequential `ls`/`find` and full-file dumps that bloat context | Manual file selection by the user | **Turn-1 Parallel Subagent Swarms** + Anchored Evidence Packets (`0` double-reads) |
| **Model Compute Routing** | Static single model for the entire conversation | Manual model switching in UI | **Automated Subagent Weight Tiering (`[lite]`/`[fast]`/`[deep]`)** with complexity floors |
| **Custom Skill Hygiene & Anti-Bloat** | Unchecked mid-task churn and premature actions | Overlapping custom prompts that fight each other | **`skill-architect` (Synergistic Builder + Permission-Based Cleanup)** + Deferred `pre-commit-gate` |
| **Enterprise & OS Deployment** | Browser-bound or requires heavy `pip`/admin setup | Copy-pasted markdown snippets | **Cross-OS (`Linux`/`macOS`/`Windows`) Installer + Zero-Install Corporate Drop-In Mode** |
