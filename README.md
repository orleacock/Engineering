# Engineering Workstation Umbrella (`orleacock/Engineering`)

Private personal engineering umbrella repository backing up the workstation `Homunculus` instance, Dual-Mode Engineering Memory (`memory/`), Dual-Account Gmail MCP server (`scripts/gmail_mcp/`), and enterprise engineering packages (`NEA_v2.2.3/`).

> [!IMPORTANT]
> **Account & Entity Separation (`homunculus_safety.json` 3-Compartment Firewall)**:
> - **Personal Umbrella (`orleacock` — Compartment `private`)**: `/home/orin/Projects/Engineering/` $\rightarrow$ `git@github-orleacock:orleacock/Engineering.git` (author `orleacock@gmail.com`).
> - **Alchemical-3D Organization (`Orin-Alchemical-3D` — Compartment `public`)**: `/home/orin/Projects/Alchemical3D` $\rightarrow$ `git@github-alchemical:Alchemical-3D/{repo_name}.git` (author `109475365+Orin-Alchemical-3D@users.noreply.github.com`).
> - **Commercial Clean-Room (`Homunculus` — Compartment `cleanroom`)**: `/home/orin/Projects/Alchemical3D/Homunculus` (`"push_locked": false`, strict zero-PII / zero-path / zero-vendor gate via `audit_portability.py` + `audit_data_boundary.py`).
> - Directory-scoped Git identities (`~/.gitconfig` `[includeIf]`) and isolated SSH host aliases (`~/.ssh/config`: `github-orleacock` vs. `github-alchemical`) route commits and pushes automatically by directory.

## Directory Layout

| Path | Scope | Description |
| :--- | :--- | :--- |
| `../Alchemical3D/Homunculus/` | Single-Source Clean-Room AI Engine | Canonical `Homunculus` repository (`git@github-alchemical:Alchemical-3D/Homunculus.git`): 3 always-on `rules/` (`co-engineering-partner`, `verifiable-accuracy`, `data-and-credential-safety`), 9 core `skills/` (`skill-architect`, `project-memory`, `claim-verification`, `subagent-orchestrator`, `engineering-sandbox`, `visual-studio`, `doc-and-card-studio`, `pre-commit-gate`, `teach-me`), Drop-In `addons/` (`author-voice-cadence`, `hardware-cad-inspector`), `adapters/`, `scripts/`, and `tests/`. |
| `memory/` | Dual-Mode Memory Vault (`obsidian`) | Self-contained per-project dossiers (`Projects/<Project>/`), Live `Directory/` Spine, Single-Writer Domain Task Umbrellas (`Tasks/*.md`), Locked Standards (`Standards_and_Specs/`), Sparse Override Templates (`Templates/`), and SVG Visual Brain (`Diagrams/`). |
| `study_briefs/` | Non-Consumed Study Root | Sibling holding directory for `/teach-me` `Brief+` artifacts (`README.md` tracked; generated briefs quarantined via `.gitignore`, `.geminiignore`, and `.stignore`). |
| `NEA_v2.2.3/` | NetCom Engineering Assistant | Portable `NEA v2.2.3` M365 Copilot 6-Agent Declarative Suite & OpenXML Inspector/Repair Tool (`Copilot_Agents/`, `Skills/`, `Scripts/inspect_nea_workbooks.py`, `Templates/`). |
| `scripts/` | Workstation Hooks, Release & MCP | `bootstrap_workstation.sh`, `git_pre_commit_boundary.sh`, `pre_push_engineering_guard.sh`, `version_manager.py`, `benchmark_homunculus.py`, `snapshot_homunculus_version.py`, `umbrella_configs/{Projects,Home}.homunculus.json`, and `scripts/gmail_mcp/` (`gmail_mcp_server.py` + workstation-local `gmail-workspace-assistant` skill). |

## Clean-Slate Workstation Restore

```bash
# 1. Clone private umbrella repository via personal SSH alias
git clone git@github-orleacock:orleacock/Engineering.git ~/Projects/Engineering

# 2. Wire Antigravity global rules/skills, parent ~/Projects & ~/.homunculus.json configs, and multi-repo git hooks
~/Projects/Engineering/scripts/bootstrap_workstation.sh --update-obsidian

# 3. Verify symlink parity, hook byte-parity, umbrella configs, and Dual-Mode Memory health
~/Projects/Engineering/scripts/bootstrap_workstation.sh --check --update-obsidian
python3 ~/Projects/Alchemical3D/Homunculus/skills/project-memory/scripts/sync_memory.py --memory-root ~/Projects/Engineering/memory --audit
```

## Offline-Only Local Assets (Excluded from Online Git)

- `../Alchemical3D/Homunculus/addons/author-voice-cadence/corpus_inbox/*` (`~54 MB` raw Discord export; only `.gitkeep` is tracked online — raw archive is backed up on the offline Raid volume).
- `study_briefs/*` (generated disposable `/teach-me` `Brief+` study notes; only `study_briefs/README.md` is tracked online).
- `memory/.obsidian/workspace.json` & `.trash/` (volatile window/tab UI state).
