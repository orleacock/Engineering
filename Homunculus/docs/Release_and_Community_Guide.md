<div align="center">

# 📦 Homunculus Open-Source Release, Community & Maintainer Guide

**How Open-Source GitHub Releases, Community Discord Support, Ko-fi & Maintainer Verification Work Together**

[**🏠 Main Cover Page**](../README.md) • [**🚀 Quick-Start Guide**](Quick_Start_and_Setup_Guide.md) • [**🧠 Capabilities Guide**](Capabilities_and_Architecture_Guide.md) • [**🗂️ Memory Setup**](Memory_Setup_README.md) • [**📟 Command Deck**](Commands_and_Prompts_Reference.md) • [**❓ User FAQ**](FAQ.md)

</div>

---

## 1. Open-Source Architecture & `Apache-2.0` Licensing (`Zero Cost to Entry`)

Homunculus is an **open-source engineering & AI verification framework** ([`LICENSE.md`](../LICENSE.md) — `Apache-2.0`) with **zero cost to entry**:

| Surface | Audience & Purpose | Included Files & Directories |
| :--- | :--- | :--- |
| **1. Public GitHub Repository & Releases (`github.com/Alchemical-3D/Homunculus`)** | **All Users, Engineers, Teams & Contributors (`Apache-2.0`)**: Hosts the complete, 100% readable and locally customizable Homunculus Core Engine, client adapters, Python verification oracles, side-loaded add-ons, Community Extension SDK (`templates/community_sdk/`), user manual (`docs/`), and 30-test verification suite. | `HOMUNCULUS_START_HERE.md`, `README.md`, `LICENSE.md`, `install.sh`, `install.ps1`, `rules/`, `skills/`, `scripts/`, `adapters/`, `addons/`, `templates/`, `hooks/`, `docs/`, `tests/` |
| **2. Alchemical-3D Community Discord (`discord.gg/aE49DW2xXe`) & GitHub Issues** | **Community Collaboration, Feedback & Support**: Open community channels for setup help, release announcements, roadmap discussions, custom skill/add-on sharing, and structured issue tracking. | Open `#homunculus-releases`, `#homunculus-support`, and `#homunculus-dev` Discord channels + [**GitHub Issue Tracker**](https://github.com/Alchemical-3D/Homunculus/issues) |

---

## 2. Getting Homunculus, Community Support, Ko-fi & Consulting

1. **Clone or Download from GitHub (`Free & Open Source`)**:
   - Clone the repository directly (`git clone https://github.com/Alchemical-3D/Homunculus.git`) or download the latest release archive (`Homunculus-v1.0.0.zip`) from [**GitHub Releases**](https://github.com/Alchemical-3D/Homunculus/releases).
2. **Join the Open Alchemical-3D Discord Community**:
   - Join the official [**Alchemical-3D Discord**](https://discord.gg/aE49DW2xXe) to connect in our open Homunculus channels:
     - **`#homunculus-releases`**: Release announcements, changelogs, and upgrade notes.
     - **`#homunculus-support`**: Co-engineering support, client adapter troubleshooting, and custom workflow setup help.
     - **`#homunculus-dev`**: Roadmap discussions, architecture proposals, and community add-on showcases.
3. **Share Feedback, Feature Requests & Bug Reports (`Discord` & `GitHub`)**:
   - **On GitHub**: Open a ticket in the [**GitHub Issue Tracker**](https://github.com/Alchemical-3D/Homunculus/issues) to log bug reports, documentation suggestions, or feature requests.
   - **In Discord**: Share workflow feedback, ideas, or setup questions directly in `#homunculus-support` and `#homunculus-dev`.
4. **Support Ongoing Open-Source Development (`Ko-fi`)**:
   - Homunculus is free for everyone without a paywall. If it saves you time, prevents costly rework, or improves your daily engineering workflow, consider supporting ongoing development on [**Ko-fi (`ko-fi.com/alchemical3d`)**](https://ko-fi.com/alchemical3d).
5. **1-on-1 Consulting, Custom Deployment & Team Workshops**:
   - Need hands-on help tailoring and rolling out Homunculus for your team, engineering custom domain verification rules/templates, or hosting a live workshop? Contact us at **[we@alchemical3d.net](mailto:we@alchemical3d.net)** or reach out in the [**Alchemical-3D Discord**](https://discord.gg/aE49DW2xXe) (`https://alchemical3d.net`).

---

## 3. Maintainer Pre-Release Verification Checklist (Zero-Leak Gate)

Before tagging a new `Homunculus-v1.0.0.zip` release archive or pushing updates to the public GitHub repository, run the 4-gate verification suite from the `Homunculus/` root:

```bash
# Gate 1: Run the full 30-test unit and cross-script integration suite:
python3 -m unittest discover -s tests -v

# Gate 2: Verify 0 hardcoded OS user paths, 0 personal tokens, and 0 third-party pip imports:
python3 scripts/audit_portability.py --repo .

# Gate 3: Verify 0 clean-room compartment or secret violations across all UTF-8, UTF-16, and UTF-32 encodings:
python3 scripts/audit_data_boundary.py --repo . --compartment cleanroom --worktree

# Gate 4: Verify 0 skill hygiene defects, 0 broken links, and 0 stale AST maps:
python3 skills/skill-architect/scripts/audit_skill_hygiene.py --root . --audit --strict-structure
```
