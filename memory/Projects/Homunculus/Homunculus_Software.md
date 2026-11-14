---
project: "Homunculus"
entity: "Alchemical-3D"
compartment: "cleanroom"
telemetry_domain: "software"
local_path: "/home/orin/Projects/Alchemical3D/Homunculus"
inventory_sha256: "16241ef63a01"
last_synced: "2026-11-14"
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
| `scripts/audit_data_boundary.py` | `Python 3.10+` | Flags: `repo_pos`, `--repo`, `--config`, `--compartment`, `--staged`, `--push-stdin`, `--remote-name`, `--remote-url`, `--worktree`, `--all-in-root` — Symbols: `BoundaryPolicy()` (`#L132-L146`), `load_boundary_config()` (`#L157-L256`), `classify_compartment()` (`#L259-L286`), `active_filename_rules()` (`#L289-L295`), `active_content_rules()` (`#L298-L302`), `audit_staged()` (`#L750-L773`), `verify_remote_and_author_for_push()` (`#L776-L827`), `audit_push_stdin()` (`#L830-L891`), `audit_worktree()` (`#L974-L1037`), `main()` (`#L1040-L1106`) | `1110` | `8f0557e304` |
| `scripts/audit_portability.py` | `Python 3.10+` | Flags: `--repo`, `--root`, `--repo-root`, `--forbid-token`, `--json` — Symbols: `audit_repository()` (`#L120-L278`), `main()` (`#L281-L325`) | `329` | `8d54274c04` |
| `scripts/build_adapters.py` | `Python 3.10+` | Flags: `--homunculus-root`, `--workspace`, `--client`, `--harness`, `--build-repo-adapters`, `--prefer-copy`, `--install-git-hooks`, `--package-cowork-zips`, `--global-agy-config-dir`, `--include-agents-md`, `--agy-skills-json`, `--json` — Symbols: `render_agents_md()` (`#L205-L230`), `check_out_of_tree_agents_md_budget()` (`#L233-L247`), `render_claude_md()` (`#L250-L275`), `render_cursor_mdc_files()` (`#L278-L309`), `build_reference_adapters_in_repo()` (`#L312-L417`), `apply_workspace_adapters()` (`#L469-L721`), `main()` (`#L724-L812`) | `816` | `1407735842` |
| `scripts/homunculus_paths.py` | `Python 3.10+` | Flags: `--workspace`, `--homunculus-root`, `--memory-root`, `--init-config`, `--memory-mode`, `--memory-dir`, `--simulate-os`, `--check`, `--ensure-fresh`, `--map`, `--sync-maps`, `--lock-core`, `--unlock-core`, `--verify-seal`, `--sudo-unlock`, `--files`, `--reason`, `--sudo-seal`, `--sudo-revoke`, `--unlock-scope`, `--lock-scope`, `--set-sudo-policy`, `--enforced-roots`, `--protect-builtin-ring1`, `--enroll-seal-signer` *(+10 more)* — Symbols: `parse_frontmatter_full()` (`#L178-L229`), `parse_frontmatter()` (`#L232-L235`), `strip_yaml_frontmatter()` (`#L238-L241`), `norm_slash_path()` (`#L244-L271`), `enforce_anti_snoop_gate()` (`#L274-L328`), `resolve_homunculus_root()` (`#L391-L418`), `resolve_workspace_config()` (`#L429-L549`), `inspect_python_ast_and_map()` (`#L849-L988`), `sync_script_navigation_map()` (`#L1102-L1159`), `ensure_directory_fresh()` (`#L1242-L1328`), `KernelPrivilegeError()` (`#L1331-L1337`), `resolve_sudo_policy()` (`#L1787-L1910`) | `4031` | `09cfb140d7` |
| `scripts/memory_gateway.py` | `Python 3.10+` | Flags: `--intent`, `--domain`, `--files`, `--lenses`, `--depth`, `--scope`, `--record-telemetry`, `--items`, `--no-telemetry`, `--addon`, `--no-create`, `--doc`, `--target`, `--sources`, `--name`, `--require-depth`, `--symptom`, `--root-cause`, `--guardrail`, `--trigger`, `--steps`, `--verification-gate`, `--lesson-id`, `--anchor`, `--receipt` *(+22 more)* — Symbols: `MemoryGatewayError()` (`#L92-L98`), `resolve_memory_root()` (`#L194-L246`), `get_context_pack()` (`#L485-L817`), `hydrate_items()` (`#L820-L1067`), `resolve_staging_dir()` (`#L1144-L1202`), `main()` (`#L2008-L2335`) | `2339` | `5c351dc957` |
| `skills/claim-verification/scripts/verify_claims.py` | `Python 3.10+` | Flags: `--target`, `--draft`, `--sources`, `--dump-whitelist`, `--fail-on-tbd`, `--strict-provenance`, `--require-anchors`, `--require-git-clean-sources`, `--memory-root`, `--project-dir`, `--entity`, `--transcript`, `--skip-freshness-check`, `--json` — Symbols: `normalize_counted_noun()` (`#L446-L464`), `canonicalize_unit()` (`#L467-L497`), `parse_num()` (`#L500-L501`), `strip_non_claim_regions()` (`#L504-L567`), `normalize_fastener()` (`#L570-L574`), `GitWorktreeCache()` (`#L685-L763`), `inspect_source_provenance()` (`#L766-L870`), `SourceFileInfo()` (`#L1062-L1284`), `SourceIndex()` (`#L1364-L2007`), `verify_calc_marker()` (`#L2121-L2211`), `resolve_subagent_transcript_path()` (`#L2233-L2269`), `audit_target()` (`#L2518-L3597`) | `3974` | `1256625ff5` |
| `skills/doc-and-card-studio/scripts/audit_repo_docs.py` | `Python 3.10+` | Flags: `target`, `--files`, `--repo-type`, `--repo-root`, `--repo`, `--fail-on-tbd`, `--skip-image-check`, `--brand-config`, `--no-brand-config` — Symbols: `load_brand_config()` (`#L77-L136`), `collect_repo_cad_files()` (`#L267-L281`), `audit_markdown_file()` (`#L284-L686`), `main()` (`#L689-L866`) | `870` | `4114868bb8` |
| `skills/doc-and-card-studio/scripts/format_image.py` | `Python 3.10+` | Flags: `inputs`, `-o`, `--output`, `--combine`, `--no-divider`, `--inspect`, `--bg-color`, `--no-whiten-bg`, `--inner-padding`, `--force-inner-padding`, `--card-size`, `--margin`, `--radius`, `--border-width`, `--border-color`, `--force` — Symbols: `parse_rgba()` (`#L101-L106`), `has_studio_grey_background()` (`#L117-L138`), `is_full_bleed_part_crop()` (`#L141-L162`), `is_already_formatted()` (`#L165-L223`), `strip_existing_card_margin()` (`#L226-L262`), `whiten_studio_background()` (`#L265-L362`), `render_card_with_shadow()` (`#L412-L468`), `format_single_image()` (`#L471-L517`), `format_combined_pair()` (`#L520-L572`), `main()` (`#L575-L730`) | `734` | `2f19180e81` |
| `skills/engineering-sandbox/scripts/sandbox_runner.py` | `Python 3.10+` | Flags: `--mode`, `--target-dir`, `--workspace`, `--writable-dir`, `--cwd`, `--spec`, `--faults`, `--cmd`, `--fault-case`, `--allow-noop-setup`, `--timeout`, `--report-dir`, `--keep-overlay`, `--keep-failed-cow`, `--blind-dir`, `--visible-dir`, `--blind-transcript`, `--visible-transcript`, `--compare-source`, `--repo-root`, `--prepare`, `--allow-net`, `--json` — Symbols: `sha256_file()` (`#L138-L146`), `snapshot_tree_manifest()` (`#L152-L209`), `diff_manifests()` (`#L212-L225`), `build_unified_diff()` (`#L228-L266`), `clone_cow_directory()` (`#L269-L303`), `build_sanitized_sandbox_env()` (`#L335-L361`), `build_bwrap_command()` (`#L378-L433`), `resolve_transcript_path()` (`#L570-L605`), `main()` (`#L1128-L1917`) | `1921` | `cff8d6e535` |
| `skills/project-memory/scripts/sync_memory.py` | `Python 3.10+` | Flags: `--memory-root`, `--vault`, `--init-memory`, `--init-vault`, `--mode`, `--convert-mode`, `--default-entity`, `--eject-templates`, `--init-project`, `--project`, `--section`, `--invariants`, `--add-lesson`, `--reinforce-lesson`, `--add-playbook`, `--update-playbook`, `--playbook-id`, `--title`, `--trigger`, `--steps`, `--verification-gate`, `--force-new`, `--lesson-disposition`, `--verify-checkpoints`, `--lesson-id` *(+57 more)* — Symbols: `clear_inprocess_memory_caches()` (`#L170-L177`), `today_iso()` (`#L266-L267`), `atomic_write_text()` (`#L270-L300`), `sanitize_entity_filename()` (`#L303-L306`), `parse_stdlib_frontmatter()` (`#L309-L312`), `render_template()` (`#L417-L435`), `build_repo_auto_tree()` (`#L550-L572`), `build_ascii_directory_tree()` (`#L575-L617`), `sync_obsidian_visual_brain()` (`#L700-L1015`), `resolve_project_repo_state()` (`#L1186-L1268`), `sync_hardware_telemetry()` (`#L1754-L1896`), `sync_software_telemetry()` (`#L1940-L2118`) | `11509` | `126ae060d3` |
| `skills/skill-architect/scripts/audit_skill_hygiene.py` | `Python 3.10+` | Flags: `--audit`, `--check-new`, `--telemetry-pulse`, `--memory-root`, `--target-skill`, `--root`, `--repo`, `--repo-root`, `--strict-structure`, `--json` — Symbols: `resolve_default_root()` (`#L105-L111`), `parse_frontmatter()` (`#L114-L117`), `strip_markdown_formatting()` (`#L120-L123`), `stem_token()` (`#L126-L135`), `tokenize_words()` (`#L138-L153`), `audit_script_stdlib_compliance()` (`#L337-L416`), `audit_ring12_gateway_compliance()` (`#L525-L686`), `main()` (`#L2020-L2102`) | `2106` | `dc2b825763` |
| `skills/teach-me/scripts/teach_brief.py` | `Python 3.10+` | Flags: `--workspace`, `--memory-root`, `--briefs-root`, `--init-brief`, `--subject`, `--impact-on`, `--query`, `--slug`, `--domain`, `--project`, `--entity`, `--compartment`, `--out`, `--rename-clean`, `--verify`, `--auto-slug`, `--require-depth`, `--model-tier`, `--force-model-tier`, `--classify-complexity`, `--context-seed`, `--routing-only`, `--thread-context`, `--redact-query`, `--attest-subagent` *(+10 more)* — Symbols: `build_brief_slug()` (`#L337-L373`), `build_concise_phrase()` (`#L376-L396`), `format_brief_display_name()` (`#L399-L409`), `format_model_tier_badge()` (`#L448-L459`), `classify_query_complexity()` (`#L462-L540`), `resolve_cold_start_project()` (`#L682-L925`), `build_context_seed()` (`#L963-L1166`), `build_chat_rails()` (`#L1169-L1200`), `build_chat_card_template()` (`#L1203-L1231`), `resolve_roots()` (`#L1234-L1263`), `ensure_briefs_root_readme()` (`#L1266-L1270`), `verify_brief_structure()` (`#L1641-L1784`) | `3210` | `e09d2772de` |
| `skills/visual-studio/scripts/render_diagram.py` | `Python 3.10+` | Flags: `--list-palettes`, `--list-blueprints`, `--memory-root`, `--spec`, `--blueprint`, `--palette`, `--out-dir`, `--basename`, `-o`, `--output`, `--png`, `--preview-png`, `--github-card`, `--svg-only`, `--strict` — Symbols: `esc()` (`#L163-L164`), `extract_frontmatter_aliases()` (`#L167-L180`), `apply_palette_defaults()` (`#L183-L196`), `normalize_key()` (`#L199-L200`), `discover_palettes()` (`#L203-L278`), `render_inline_markup()` (`#L348-L357`), `resolve_style_colors()` (`#L360-L394`), `DiagramBuilder()` (`#L397-L631`), `render_layered_architecture()` (`#L634-L795`), `render_column_dataflow()` (`#L798-L949`), `render_hardware_pinout_pneumatic()` (`#L952-L1183`), `render_comparison_matrix()` (`#L1186-L1319`) | `1791` | `803311e17d` |
| `templates/hooks/post-worktree-sync.sh` | `POSIX Bash` | Executable Script / Source | `69` | `d767ade2b9` |
| `templates/hooks/pre-commit.sh` | `POSIX Bash` | Executable Script / Source | `126` | `b8157c58f8` |
| `templates/hooks/pre-push.sh` | `POSIX Bash` | Executable Script / Source | `70` | `c83b1020e3` |
| `tests/test_adapters.py` | `Python 3.10+` | Symbols: `TestAdapters()` (`#L24-L451`) | `455` | `be4425884b` |
| `tests/test_claim_verification.py` | `Python 3.10+` | Symbols: `TestClaimVerification()` (`#L31-L765`) | `769` | `74f5f372f6` |
| `tests/test_core_skills.py` | `Python 3.10+` | Symbols: `TestCoreSkills()` (`#L58-L702`) | `706` | `67b71e9d1d` |
| `tests/test_data_safety.py` | `Python 3.10+` | Symbols: `TestDataSafety()` (`#L31-L258`) | `262` | `aa3a8a8e7e` |
| `tests/test_foundation.py` | `Python 3.10+` | Symbols: `TestFoundation()` (`#L25-L152`) | `156` | `692144d4fd` |
| `tests/test_project_memory.py` | `Python 3.10+` | Symbols: `TestProjectMemory()` (`#L20-L2297`) | `2301` | `7b67e5ae47` |
| `tests/test_teach_me.py` | `Python 3.10+` | Symbols: `TestTeachMe()` (`#L30-L1910`) | `1914` | `74bc0d2a05` |
| `tests/test_v030_memory_platform.py` | `Python 3.10+` | Symbols: `TestV030Milestone1ContextFabric()` (`#L37-L276`), `TestV030Milestone2MemoryGateway()` (`#L279-L790`), `TestV030Milestone3Ring0Sudo()` (`#L855-L1196`), `TestV030Milestone4PlaybookAndEndToEnd()` (`#L1199-L1385`), `TestV031Ring0TeachMeAndTurnkeyUpgrades()` (`#L1389-L2278`) | `2282` | `52e8b22ff2` |
<!-- AUTO-SOFTWARE-MODULES:END -->

---

## 2. Configuration Schemas & Data Contracts

<!-- AUTO-SOFTWARE-SCHEMAS:START -->
| Schema / Config File | Format | Top-Level Keys / Contract Version | SHA-256 Prefix |
| :--- | :--- | :--- | :--- |
| `adapters/antigravity/hooks.json` | `JSON` | `{}` (empty object) | `ca3d163bab` |
| `adapters/claude_code/settings.json` | `JSON` | `schema_version`, `description`, `permissions`, `hooks` | `afa6950342` |
| `hooks/hooks.json` | `JSON` | `{}` (empty object) | `ca3d163bab` |
| `scripts/kernel_seal.json` | `JSON` | `schema_version`, `ring`, `sealed_at`, `reason`, `entry_count`, `seal_digest` | `b4992c19db` |
| `scripts/script_contracts.json` | `JSON` | `schema_version`, `description`, `coupling_policy`, `scripts` | `c9de62084e` |
| `templates/homunculus_safety.example.json` | `JSON` | `schema_version`, `description`, `default_compartment`, `enforce_posix_win_user_paths_in_public`, `compartments` | `7e45cf72a5` |
| `templates/diagrams/Diagram_Palettes.json` | `JSON` | `default_palette`, `palettes` | `8918674dd9` |
<!-- AUTO-SOFTWARE-SCHEMAS:END -->

---

## 3. Deterministic Test & Verification Receipts

<!-- AUTO-SOFTWARE-TESTS:START -->
| Test File | Test Classes | AST test_* Count | SHA-256 Prefix |
| :--- | :--- | :---: | :---: |
| `tests/test_adapters.py` | `TestAdapters` | `8` | `be4425884b` |
| `tests/test_claim_verification.py` | `TestClaimVerification` | `4` | `74f5f372f6` |
| `tests/test_core_skills.py` | `TestCoreSkills` | `9` | `67b71e9d1d` |
| `tests/test_data_safety.py` | `TestDataSafety` | `5` | `aa3a8a8e7e` |
| `tests/test_foundation.py` | `TestFoundation` | `6` | `692144d4fd` |
| `tests/test_project_memory.py` | `TestProjectMemory` | `26` | `7b67e5ae47` |
| `tests/test_teach_me.py` | `TestTeachMe` | `7` | `74bc0d2a05` |
| `tests/test_v030_memory_platform.py` | `TestV030Milestone1ContextFabric`, `TestV030Milestone2MemoryGateway`, `TestV030Milestone3Ring0Sudo`, `TestV030Milestone4PlaybookAndEndToEnd`, `TestV031Ring0TeachMeAndTurnkeyUpgrades` | `11` | `52e8b22ff2` |

**Latest Verified Test Receipt (`2026-11-14`):** 76/76 unittest OK (36.414s, v0.3.4 3996460a1e68)
<!-- AUTO-SOFTWARE-TESTS:END -->
