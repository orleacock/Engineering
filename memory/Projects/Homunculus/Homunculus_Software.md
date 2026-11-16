---
project: "Homunculus"
entity: "Alchemical-3D"
compartment: "cleanroom"
telemetry_domain: "software"
local_path: "/home/orin/Projects/Alchemical3D/Homunculus"
inventory_sha256: "733855db023b"
last_synced: "2026-11-16"
---

# Homunculus — Software, CLI & Schema Telemetry (`_Software.md`)

> **Authoritative Software Truth Ledger (`sync_software_telemetry`)**: Populated via `sync_memory.py --sync-software --project Homunculus`. Used by `verify_claims.py` as primary software/CLI/schema ground truth for `Homunculus` (`entity: Alchemical-3D`).

---

## 1. Runtime Entrypoints & Module Inventory

<!-- AUTO-SOFTWARE-MODULES:START -->
| Script / Module Path | Language / Runtime | CLI Flags / Public Symbols | Line Count | SHA-256 Prefix |
| :--- | :--- | :--- | :--- | :--- |
| `install.ps1` | `PowerShell` | Executable Script / Source | `88` | `65f4c1b6e0` |
| `install.sh` | `POSIX Bash` | Executable Script / Source | `132` | `d2c0946d57` |
| `addons/author-voice-cadence/scripts/extract_voice_cadence.py` | `Python 3.10+` | Flags: `--inbox`, `--scope`, `--tier-config`, `--author`, `--min-words`, `--stitch-minutes`, `--exemplars-per-cat`, `--output` — Symbols: `PostRecord()` (`#L220-L239`), `parse_ts()` (`#L242-L258`), `clean_post_text()` (`#L261-L265`), `strip_code_for_prose_metrics()` (`#L268-L271`), `apply_tier_config()` (`#L274-L308`), `main()` (`#L1385-L1483`) | `1487` | `2d99a460b4` |
| `addons/hardware-cad-inspector/scripts/inspect_hardware_ecosystem.py` | `Python 3.10+` | Flags: `--vault`, `--memory-root`, `--project`, `--repo`, `--json-out`, `--all`, `--check-cache`, `--sync-manifest`, `--force-rescan` — Symbols: `normalize_part_stem()` (`#L115-L124`), `detect_step_unit_scale()` (`#L155-L174`), `inspect_step_file()` (`#L177-L380`), `inspect_stl_file()` (`#L383-L486`), `inspect_cfg_file()` (`#L489-L529`), `scan_repo_hardware()` (`#L532-L664`), `render_manifest_markdown()` (`#L701-L894`), `resolve_projects()` (`#L897-L965`), `main()` (`#L968-L1214`) | `1218` | `b2c89cdf16` |
| `scripts/audit_data_boundary.py` | `Python 3.10+` | Flags: `repo_pos`, `--repo`, `--config`, `--compartment`, `--staged`, `--push-stdin`, `--remote-name`, `--remote-url`, `--worktree`, `--all-in-root` — Symbols: `BoundaryPolicy()` (`#L144-L158`), `load_boundary_config()` (`#L171-L270`), `classify_compartment()` (`#L273-L300`), `active_filename_rules()` (`#L303-L309`), `active_content_rules()` (`#L312-L316`), `audit_staged()` (`#L839-L862`), `verify_remote_and_author_for_push()` (`#L865-L916`), `audit_push_stdin()` (`#L919-L980`), `audit_worktree()` (`#L1063-L1126`), `main()` (`#L1129-L1195`) | `1199` | `396b6b7696` |
| `scripts/audit_portability.py` | `Python 3.10+` | Flags: `--repo`, `--root`, `--repo-root`, `--forbid-token`, `--json` — Symbols: `audit_repository()` (`#L152-L333`), `main()` (`#L336-L380`) | `384` | `c8b80deeda` |
| `scripts/build_adapters.py` | `Python 3.10+` | Flags: `--homunculus-root`, `--workspace`, `--client`, `--harness`, `--build-repo-adapters`, `--prefer-copy`, `--install-git-hooks`, `--package-cowork-zips`, `--global-agy-config-dir`, `--include-agents-md`, `--agy-skills-json`, `--json` — Symbols: `render_agents_md()` (`#L205-L230`), `check_out_of_tree_agents_md_budget()` (`#L233-L247`), `render_claude_md()` (`#L250-L275`), `render_cursor_mdc_files()` (`#L278-L309`), `build_reference_adapters_in_repo()` (`#L312-L417`), `apply_workspace_adapters()` (`#L469-L721`), `main()` (`#L724-L812`) | `816` | `352136d02a` |
| `scripts/homunculus_paths.py` | `Python 3.10+` | Flags: `--workspace`, `--homunculus-root`, `--memory-root`, `--init-config`, `--memory-mode`, `--memory-dir`, `--simulate-os`, `--check`, `--ensure-fresh`, `--map`, `--sync-maps`, `--lock-core`, `--unlock-core`, `--verify-seal`, `--sudo-unlock`, `--files`, `--reason`, `--sudo-seal`, `--sudo-revoke`, `--unlock-scope`, `--lock-scope`, `--set-sudo-policy`, `--enforced-roots`, `--protect-builtin-ring1`, `--enroll-seal-signer` *(+10 more)* — Symbols: `parse_frontmatter_full()` (`#L179-L230`), `parse_frontmatter()` (`#L233-L236`), `strip_yaml_frontmatter()` (`#L239-L242`), `norm_slash_path()` (`#L245-L272`), `enforce_anti_snoop_gate()` (`#L275-L329`), `resolve_homunculus_root()` (`#L392-L419`), `resolve_workspace_config()` (`#L430-L550`), `inspect_python_ast_and_map()` (`#L850-L989`), `sync_script_navigation_map()` (`#L1103-L1160`), `ensure_directory_fresh()` (`#L1243-L1329`), `KernelPrivilegeError()` (`#L1332-L1338`), `resolve_sudo_policy()` (`#L1795-L1918`) | `4121` | `47d628aa88` |
| `scripts/memory_gateway.py` | `Python 3.10+` | Flags: `--intent`, `--domain`, `--files`, `--lenses`, `--depth`, `--scope`, `--record-telemetry`, `--items`, `--no-telemetry`, `--addon`, `--no-create`, `--doc`, `--target`, `--sources`, `--name`, `--require-depth`, `--symptom`, `--root-cause`, `--guardrail`, `--trigger`, `--steps`, `--verification-gate`, `--lesson-id`, `--anchor`, `--receipt` *(+23 more)* — Symbols: `MemoryGatewayError()` (`#L93-L99`), `resolve_memory_root()` (`#L195-L247`), `get_context_pack()` (`#L486-L822`), `hydrate_items()` (`#L825-L1072`), `resolve_staging_dir()` (`#L1149-L1207`), `main()` (`#L2127-L2483`) | `2487` | `53706d74d8` |
| `skills/claim-verification/scripts/verify_claims.py` | `Python 3.10+` | Flags: `--target`, `--draft`, `--sources`, `--dump-whitelist`, `--fail-on-tbd`, `--strict-provenance`, `--require-anchors`, `--require-git-clean-sources`, `--memory-root`, `--project-dir`, `--entity`, `--transcript`, `--skip-freshness-check`, `--no-cache`, `--json` — Symbols: `normalize_counted_noun()` (`#L452-L470`), `canonicalize_unit()` (`#L473-L503`), `parse_num()` (`#L506-L507`), `strip_non_claim_regions()` (`#L510-L573`), `normalize_fastener()` (`#L576-L580`), `GitWorktreeCache()` (`#L691-L769`), `inspect_source_provenance()` (`#L772-L876`), `SourceFileInfo()` (`#L1068-L1290`), `SourceIndex()` (`#L1370-L2024`), `verify_calc_marker()` (`#L2465-L2555`), `resolve_subagent_transcript_path()` (`#L2577-L2613`), `audit_target()` (`#L2862-L3941`) | `4448` | `b440407039` |
| `skills/doc-and-card-studio/scripts/audit_repo_docs.py` | `Python 3.10+` | Flags: `target`, `--files`, `--repo-type`, `--repo-root`, `--repo`, `--fail-on-tbd`, `--skip-image-check`, `--brand-config`, `--no-brand-config` — Symbols: `load_brand_config()` (`#L77-L136`), `collect_repo_cad_files()` (`#L267-L281`), `audit_markdown_file()` (`#L284-L686`), `main()` (`#L689-L866`) | `870` | `4114868bb8` |
| `skills/doc-and-card-studio/scripts/format_image.py` | `Python 3.10+` | Flags: `inputs`, `-o`, `--output`, `--combine`, `--no-divider`, `--inspect`, `--bg-color`, `--no-whiten-bg`, `--inner-padding`, `--force-inner-padding`, `--card-size`, `--margin`, `--radius`, `--border-width`, `--border-color`, `--force` — Symbols: `parse_rgba()` (`#L101-L106`), `has_studio_grey_background()` (`#L117-L138`), `is_full_bleed_part_crop()` (`#L141-L162`), `is_already_formatted()` (`#L165-L223`), `strip_existing_card_margin()` (`#L226-L262`), `whiten_studio_background()` (`#L265-L362`), `render_card_with_shadow()` (`#L412-L468`), `format_single_image()` (`#L471-L517`), `format_combined_pair()` (`#L520-L572`), `main()` (`#L575-L730`) | `734` | `2f19180e81` |
| `skills/engineering-sandbox/scripts/sandbox_runner.py` | `Python 3.10+` | Flags: `--mode`, `--model-id`, `--effort`, `--target-dir`, `--workspace`, `--writable-dir`, `--cwd`, `--spec`, `--faults`, `--cmd`, `--fault-case`, `--allow-noop-setup`, `--timeout`, `--report-dir`, `--keep-overlay`, `--keep-failed-cow`, `--blind-dir`, `--visible-dir`, `--blind-transcript`, `--visible-transcript`, `--compare-source`, `--repo-root`, `--prepare`, `--allow-net`, `--json` — Symbols: `extract_model_and_effort_from_steps()` (`#L99-L120`), `format_model_receipt_tag()` (`#L123-L143`), `sha256_file()` (`#L199-L207`), `snapshot_tree_manifest()` (`#L213-L270`), `diff_manifests()` (`#L273-L286`), `build_unified_diff()` (`#L289-L327`), `build_sanitized_sandbox_env()` (`#L396-L422`), `build_bwrap_command()` (`#L439-L494`), `resolve_transcript_path()` (`#L631-L666`), `main()` (`#L1227-L2075`) | `2079` | `61545f823c` |
| `skills/project-memory/scripts/sync_memory.py` | `Python 3.10+` | Flags: `--memory-root`, `--vault`, `--init-memory`, `--init-vault`, `--mode`, `--convert-mode`, `--default-entity`, `--eject-templates`, `--init-project`, `--project`, `--section`, `--invariants`, `--add-lesson`, `--reinforce-lesson`, `--add-playbook`, `--update-playbook`, `--playbook-id`, `--title`, `--trigger`, `--steps`, `--verification-gate`, `--force-new`, `--lesson-disposition`, `--verify-checkpoints`, `--lesson-id` *(+57 more)* — Symbols: `clear_inprocess_memory_caches()` (`#L171-L178`), `today_iso()` (`#L267-L268`), `atomic_write_text()` (`#L271-L301`), `sanitize_entity_filename()` (`#L304-L307`), `parse_stdlib_frontmatter()` (`#L310-L313`), `render_template()` (`#L418-L436`), `build_repo_auto_tree()` (`#L551-L573`), `build_ascii_directory_tree()` (`#L576-L618`), `sync_obsidian_visual_brain()` (`#L701-L1016`), `resolve_project_repo_state()` (`#L1187-L1269`), `sync_hardware_telemetry()` (`#L1755-L1897`), `sync_software_telemetry()` (`#L1941-L2119`) | `11601` | `a8f19bcd77` |
| `skills/skill-architect/scripts/audit_skill_hygiene.py` | `Python 3.10+` | Flags: `--audit`, `--check-new`, `--telemetry-pulse`, `--memory-root`, `--target-skill`, `--root`, `--repo`, `--repo-root`, `--strict-structure`, `--json` — Symbols: `resolve_default_root()` (`#L106-L112`), `parse_frontmatter()` (`#L115-L118`), `strip_markdown_formatting()` (`#L121-L124`), `stem_token()` (`#L127-L136`), `tokenize_words()` (`#L139-L154`), `audit_script_stdlib_compliance()` (`#L338-L417`), `audit_ring12_gateway_compliance()` (`#L551-L712`), `main()` (`#L2055-L2137`) | `2141` | `71e18c36be` |
| `skills/teach-me/scripts/teach_brief.py` | `Python 3.10+` | Flags: `--workspace`, `--memory-root`, `--briefs-root`, `--init-brief`, `--subject`, `--impact-on`, `--query`, `--slug`, `--domain`, `--project`, `--entity`, `--compartment`, `--out`, `--rename-clean`, `--verify`, `--auto-slug`, `--require-depth`, `--model-tier`, `--force-model-tier`, `--classify-complexity`, `--context-seed`, `--routing-only`, `--thread-context`, `--redact-query`, `--attest-subagent` *(+10 more)* — Symbols: `build_brief_slug()` (`#L337-L373`), `build_concise_phrase()` (`#L376-L396`), `format_brief_display_name()` (`#L399-L409`), `format_model_tier_badge()` (`#L484-L495`), `classify_query_complexity()` (`#L498-L578`), `resolve_cold_start_project()` (`#L720-L963`), `build_context_seed()` (`#L1001-L1204`), `build_chat_rails()` (`#L1207-L1238`), `build_chat_card_template()` (`#L1241-L1269`), `resolve_roots()` (`#L1272-L1301`), `ensure_briefs_root_readme()` (`#L1304-L1308`), `verify_brief_structure()` (`#L1679-L1822`) | `3248` | `5f2a616aae` |
| `skills/visual-studio/scripts/render_diagram.py` | `Python 3.10+` | Flags: `--list-palettes`, `--list-blueprints`, `--memory-root`, `--spec`, `--blueprint`, `--palette`, `--out-dir`, `--basename`, `-o`, `--output`, `--png`, `--preview-png`, `--github-card`, `--svg-only`, `--strict` — Symbols: `esc()` (`#L163-L164`), `extract_frontmatter_aliases()` (`#L167-L180`), `apply_palette_defaults()` (`#L183-L196`), `normalize_key()` (`#L199-L200`), `discover_palettes()` (`#L203-L278`), `render_inline_markup()` (`#L348-L357`), `resolve_style_colors()` (`#L360-L394`), `DiagramBuilder()` (`#L397-L631`), `render_layered_architecture()` (`#L634-L795`), `render_column_dataflow()` (`#L798-L949`), `render_hardware_pinout_pneumatic()` (`#L952-L1183`), `render_comparison_matrix()` (`#L1186-L1319`) | `1791` | `803311e17d` |
| `templates/hooks/post-worktree-sync.sh` | `POSIX Bash` | Executable Script / Source | `69` | `d767ade2b9` |
| `templates/hooks/pre-commit.sh` | `POSIX Bash` | Executable Script / Source | `126` | `b8157c58f8` |
| `templates/hooks/pre-push.sh` | `POSIX Bash` | Executable Script / Source | `70` | `c83b1020e3` |
| `tests/test_adapters.py` | `Python 3.10+` | Symbols: `TestAdapters()` (`#L24-L451`) | `455` | `be4425884b` |
| `tests/test_claim_verification.py` | `Python 3.10+` | Symbols: `TestClaimVerification()` (`#L31-L842`) | `846` | `f08bffc373` |
| `tests/test_core_skills.py` | `Python 3.10+` | Symbols: `TestCoreSkills()` (`#L58-L822`) | `826` | `a730b45739` |
| `tests/test_data_safety.py` | `Python 3.10+` | Symbols: `TestDataSafety()` (`#L31-L258`) | `262` | `aa3a8a8e7e` |
| `tests/test_foundation.py` | `Python 3.10+` | Symbols: `TestFoundation()` (`#L25-L152`) | `156` | `692144d4fd` |
| `tests/test_project_memory.py` | `Python 3.10+` | Symbols: `TestProjectMemory()` (`#L20-L2297`) | `2301` | `7b67e5ae47` |
| `tests/test_teach_me.py` | `Python 3.10+` | Symbols: `TestTeachMe()` (`#L30-L1980`) | `1984` | `acefc82480` |
| `tests/test_v030_memory_platform.py` | `Python 3.10+` | Symbols: `TestV030Milestone1ContextFabric()` (`#L38-L277`), `TestV030Milestone2MemoryGateway()` (`#L280-L791`), `TestV030Milestone3Ring0Sudo()` (`#L877-L1221`), `TestV030Milestone4PlaybookAndEndToEnd()` (`#L1224-L1410`), `TestV031Ring0TeachMeAndTurnkeyUpgrades()` (`#L1414-L2303`), `TestV035QuarantineAndTbdParity()` (`#L2306-L2490`) | `2494` | `c6e1b916bc` |
<!-- AUTO-SOFTWARE-MODULES:END -->

---

## 2. Configuration Schemas & Data Contracts

<!-- AUTO-SOFTWARE-SCHEMAS:START -->
| Schema / Config File | Format | Top-Level Keys / Contract Version | SHA-256 Prefix |
| :--- | :--- | :--- | :--- |
| `adapters/antigravity/hooks.json` | `JSON` | `{}` (empty object) | `ca3d163bab` |
| `adapters/claude_code/settings.json` | `JSON` | `schema_version`, `description`, `permissions`, `hooks` | `afa6950342` |
| `hooks/hooks.json` | `JSON` | `{}` (empty object) | `ca3d163bab` |
| `scripts/kernel_seal.json` | `JSON` | `schema_version`, `ring`, `sealed_at`, `reason`, `entry_count`, `seal_digest` | `6a4391de23` |
| `scripts/script_contracts.json` | `JSON` | `schema_version`, `description`, `coupling_policy`, `scripts` | `ead3aab4d8` |
| `templates/homunculus_safety.example.json` | `JSON` | `schema_version`, `description`, `default_compartment`, `enforce_posix_win_user_paths_in_public`, `compartments` | `7e45cf72a5` |
| `templates/diagrams/Diagram_Palettes.json` | `JSON` | `default_palette`, `palettes` | `8918674dd9` |
<!-- AUTO-SOFTWARE-SCHEMAS:END -->

---

## 3. Deterministic Test & Verification Receipts

<!-- AUTO-SOFTWARE-TESTS:START -->
| Test File | Test Classes | AST test_* Count | SHA-256 Prefix |
| :--- | :--- | :---: | :---: |
| `tests/test_adapters.py` | `TestAdapters` | `8` | `be4425884b` |
| `tests/test_claim_verification.py` | `TestClaimVerification` | `5` | `f08bffc373` |
| `tests/test_core_skills.py` | `TestCoreSkills` | `10` | `a730b45739` |
| `tests/test_data_safety.py` | `TestDataSafety` | `5` | `aa3a8a8e7e` |
| `tests/test_foundation.py` | `TestFoundation` | `6` | `692144d4fd` |
| `tests/test_project_memory.py` | `TestProjectMemory` | `26` | `7b67e5ae47` |
| `tests/test_teach_me.py` | `TestTeachMe` | `8` | `acefc82480` |
| `tests/test_v030_memory_platform.py` | `TestV030Milestone1ContextFabric`, `TestV030Milestone2MemoryGateway`, `TestV030Milestone3Ring0Sudo`, `TestV030Milestone4PlaybookAndEndToEnd`, `TestV031Ring0TeachMeAndTurnkeyUpgrades`, `TestV035QuarantineAndTbdParity` | `14` | `c6e1b916bc` |

**Latest Verified Test Receipt (`2026-11-16`):** 82/82 unittest OK (37.433s, SBX-20261116_152151-07f6b24f)
<!-- AUTO-SOFTWARE-TESTS:END -->
