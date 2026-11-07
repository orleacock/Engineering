<div align="center">

# 📦 Homunculus Distribution, Discord Store & Release Guide

**How the Discord Store Core Archive, Automatic Buyer Role Unlock, and Public GitHub Manual Work Together**

[**🏠 Main Cover Page**](../README.md) • [**🚀 Quick-Start Guide**](Quick_Start_and_Setup_Guide.md) • [**🧠 Capabilities Guide**](Capabilities_and_Architecture_Guide.md) • [**🗂️ Memory Setup**](Memory_Setup_README.md) • [**📟 Command Deck**](Commands_and_Prompts_Reference.md) • [**❓ FAQ**](FAQ.md)

</div>

---

## 1. Two-Surface Product Architecture (`Model C` Hybrid Distribution)

Homunculus separates **commercial core distribution** from **open documentation, issue tracking, and community extensibility**:

| Surface | Audience & Purpose | Included Files & Directories |
| :--- | :--- | :--- |
| **1. Alchemical-3D Discord Store Archive (`Homunculus-v1.0.0.zip`)** | **Authorized Buyers (`Model C` Part I Commercial Seat License)**: Contains the complete, 100% readable and locally customizable Homunculus Core Engine, client adapters, Python verification oracles, side-loaded add-ons, and test suite. | `HOMUNCULUS_START_HERE.md`, `README.md`, `LICENSE.md`, `install.sh`, `install.ps1`, `rules/`, `skills/`, `scripts/`, `adapters/`, `addons/`, `templates/`, `hooks/`, `docs/`, `tests/` |
| **2. Public GitHub Repository (`github.com/Alchemical-3D/Homunculus`)** | **Prospective Buyers, Active Users & Community Contributors**: Hosts the flagship Cover Page, the complete indexed User Manual (`docs/`), the public **GitHub Issue Tracker**, and the **`MIT`-licensed Community Extension SDK** (`templates/community_sdk/`). | `README.md`, `LICENSE.md`, `docs/*.md`, `templates/community_sdk/**` *(Zero paid Core Engine scripts or rules published to public Git)* |

---

## 2. Buyer Onboarding Flow & Discord Role Unlock

1. **Purchase via the Alchemical-3D Discord Store**:
   - Visit the official [Alchemical-3D Discord](https://discord.gg/aE49DW2xXe) storefront and purchase your **Homunculus** seat.
2. **Automatic Discord Buyer Role Assignment**:
   - Upon purchase completion, Discord automatically assigns your account the **Homunculus Buyer Role**.
   - This role immediately unlocks dedicated buyer-only channels inside the Alchemical-3D Discord server:
     - **`#homunculus-releases`**: Direct download links for the latest `Homunculus-vX.Y.Z.zip` Core Archive and release changelogs.
     - **`#homunculus-support`**: Direct co-engineering support, client adapter troubleshooting, and custom workflow setup help.
     - **`#homunculus-dev`**: Roadmap discussions, early feature previews, and community add-on showcases.
3. **Offering Feedback, Feature Requests & Issue Tracking (`Discord` & `GitHub`)**:
   - **In Discord**: Share workflow feedback, feature ideas, or setup questions directly in the [Alchemical-3D Discord](https://discord.gg/aE49DW2xXe) (`#homunculus-support` and `#homunculus-dev`).
   - **On GitHub**: Open a ticket in the [**GitHub Issue Tracker**](https://github.com/Alchemical-3D/Homunculus/issues) to log bug reports, documentation suggestions, or enhancement requests, and browse the `docs/` directory anytime as your online reference manual.

---

## 3. Maintainer Pre-Release Verification Checklist (`Zero-Leak Gate`)

Before packaging a new `Homunculus-vX.Y.Z.zip` archive for the Discord Store or syncing documentation updates to the public GitHub manual repository, run the 4-gate verification suite from the clean-room `Homunculus/` root:

```bash
# Gate 1: Run the full 24-test unit and cross-script integration suite:
python3 -m unittest discover -s tests -v

# Gate 2: Verify 0 hardcoded OS user paths, 0 personal tokens, and 0 third-party pip imports:
python3 scripts/audit_portability.py --repo .

# Gate 3: Verify 0 clean-room compartment or secret violations across all UTF-8/16/32 files:
python3 scripts/audit_data_boundary.py --repo . --compartment cleanroom --worktree

# Gate 4: Verify 0 skill hygiene defects, 0 broken links, and 0 orphan scripts:
python3 skills/skill-architect/scripts/audit_skill_hygiene.py --root . --audit --strict-structure
```
