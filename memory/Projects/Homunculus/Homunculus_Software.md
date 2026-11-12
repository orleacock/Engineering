---
project: "Homunculus"
entity: "Alchemical-3D"
compartment: "cleanroom"
telemetry_domain: "software"
local_path: "/home/orin/Projects/Alchemical3D/Homunculus"
inventory_sha256: "2f284a59aba4"
last_synced: "2026-11-12"
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
| `scripts/audit_data_boundary.py` | `Python 3.10+` | Flags: `repo_pos`, `--repo`, `--config`, `--compartment`, `--staged`, `--push-stdin`, `--remote-name`, `--remote-url`, `--worktree`, `--all-in-root` — Symbols: `BoundaryPolicy()` (`#L111-L125`), `load_boundary_config()` (`#L136-L235`), `classify_compartment()` (`#L238-L265`), `active_filename_rules()` (`#L268-L274`), `active_content_rules()` (`#L277-L281`), `audit_staged()` (`#L619-L642`), `verify_remote_and_author_for_push()` (`#L645-L696`), `audit_push_stdin()` (`#L699-L760`), `audit_worktree()` (`#L763-L799`), `main()` (`#L802-L868`) | `872` | `e00b6f5793` |
| `scripts/audit_portability.py` | `Python 3.10+` | Flags: `--repo`, `--root`, `--repo-root`, `--forbid-token`, `--json` — Symbols: `audit_repository()` (`#L120-L278`), `main()` (`#L281-L325`) | `329` | `8d54274c04` |
| `scripts/build_adapters.py` | `Python 3.10+` | Flags: `--homunculus-root`, `--workspace`, `--client`, `--harness`, `--build-repo-adapters`, `--prefer-copy`, `--install-git-hooks`, `--package-cowork-zips`, `--global-agy-config-dir`, `--include-agents-md`, `--agy-skills-json`, `--json` — Symbols: `render_agents_md()` (`#L176-L201`), `render_claude_md()` (`#L204-L229`), `render_cursor_mdc_files()` (`#L232-L263`), `build_reference_adapters_in_repo()` (`#L266-L378`), `apply_workspace_adapters()` (`#L430-L690`), `main()` (`#L693-L781`) | `785` | `9a14699982` |
| `scripts/homunculus_paths.py` | `Python 3.10+` | Flags: `--workspace`, `--homunculus-root`, `--memory-root`, `--init-config`, `--memory-mode`, `--memory-dir`, `--simulate-os`, `--check`, `--ensure-fresh`, `--map`, `--sync-maps`, `--lock-core`, `--unlock-core`, `--verify-seal`, `--sudo-unlock`, `--files`, `--reason`, `--sudo-seal`, `--sudo-revoke`, `--unlock-scope`, `--lock-scope`, `--set-sudo-policy`, `--enforced-roots`, `--protect-builtin-ring1`, `--enroll-remote-turnkeys` *(+4 more)* — Symbols: `parse_frontmatter_full()` (`#L147-L198`), `parse_frontmatter()` (`#L201-L204`), `strip_yaml_frontmatter()` (`#L207-L210`), `norm_slash_path()` (`#L213-L240`), `enforce_anti_snoop_gate()` (`#L243-L297`), `resolve_homunculus_root()` (`#L360-L387`), `resolve_workspace_config()` (`#L398-L518`), `inspect_python_ast_and_map()` (`#L818-L957`), `sync_script_navigation_map()` (`#L1070-L1127`), `ensure_directory_fresh()` (`#L1210-L1296`), `KernelPrivilegeError()` (`#L1299-L1305`), `resolve_sudo_policy()` (`#L1478-L1563`) | `2903` | `5ae8efc594` |
| `scripts/memory_gateway.py` | `Python 3.10+` | Flags: `--intent`, `--domain`, `--files`, `--lenses`, `--depth`, `--record-telemetry`, `--items`, `--no-telemetry`, `--addon`, `--no-create`, `--doc`, `--target`, `--sources`, `--name`, `--require-depth`, `--symptom`, `--root-cause`, `--guardrail`, `--trigger`, `--steps`, `--verification-gate`, `--lesson-id`, `--anchor`, `--receipt`, `--subsystem` *(+21 more)* — Symbols: `MemoryGatewayError()` (`#L91-L97`), `resolve_memory_root()` (`#L193-L245`), `get_context_pack()` (`#L484-L812`), `hydrate_items()` (`#L815-L1062`), `resolve_staging_dir()` (`#L1139-L1197`), `main()` (`#L1956-L2275`) | `2279` | `a5acb15cca` |
| `skills/claim-verification/scripts/verify_claims.py` | `Python 3.10+` | Flags: `--target`, `--draft`, `--sources`, `--dump-whitelist`, `--fail-on-tbd`, `--strict-provenance`, `--require-anchors`, `--require-git-clean-sources`, `--memory-root`, `--project-dir`, `--entity`, `--transcript`, `--skip-freshness-check`, `--json` — Symbols: `normalize_counted_noun()` (`#L445-L463`), `canonicalize_unit()` (`#L466-L496`), `parse_num()` (`#L499-L500`), `strip_non_claim_regions()` (`#L503-L566`), `normalize_fastener()` (`#L569-L573`), `GitWorktreeCache()` (`#L684-L762`), `inspect_source_provenance()` (`#L765-L864`), `SourceFileInfo()` (`#L1025-L1247`), `SourceIndex()` (`#L1327-L1968`), `verify_calc_marker()` (`#L2082-L2172`), `resolve_subagent_transcript_path()` (`#L2194-L2230`), `audit_target()` (`#L2479-L3552`) | `3868` | `b3f7e9a0fd` |
| `skills/doc-and-card-studio/scripts/audit_repo_docs.py` | `Python 3.10+` | Flags: `target`, `--files`, `--repo-type`, `--repo-root`, `--repo`, `--fail-on-tbd`, `--skip-image-check`, `--brand-config`, `--no-brand-config` — Symbols: `load_brand_config()` (`#L77-L136`), `collect_repo_cad_files()` (`#L267-L281`), `audit_markdown_file()` (`#L284-L686`), `main()` (`#L689-L866`) | `870` | `4114868bb8` |
| `skills/doc-and-card-studio/scripts/format_image.py` | `Python 3.10+` | Flags: `inputs`, `-o`, `--output`, `--combine`, `--no-divider`, `--inspect`, `--bg-color`, `--no-whiten-bg`, `--inner-padding`, `--force-inner-padding`, `--card-size`, `--margin`, `--radius`, `--border-width`, `--border-color`, `--force` — Symbols: `parse_rgba()` (`#L101-L106`), `has_studio_grey_background()` (`#L117-L138`), `is_full_bleed_part_crop()` (`#L141-L162`), `is_already_formatted()` (`#L165-L223`), `strip_existing_card_margin()` (`#L226-L262`), `whiten_studio_background()` (`#L265-L362`), `render_card_with_shadow()` (`#L412-L468`), `format_single_image()` (`#L471-L517`), `format_combined_pair()` (`#L520-L572`), `main()` (`#L575-L730`) | `734` | `2f19180e81` |
| `skills/engineering-sandbox/scripts/sandbox_runner.py` | `Python 3.10+` | Flags: `--mode`, `--target-dir`, `--workspace`, `--writable-dir`, `--cwd`, `--spec`, `--faults`, `--cmd`, `--fault-case`, `--allow-noop-setup`, `--timeout`, `--report-dir`, `--keep-overlay`, `--keep-failed-cow`, `--blind-dir`, `--visible-dir`, `--blind-transcript`, `--visible-transcript`, `--compare-source`, `--repo-root`, `--prepare`, `--json` — Symbols: `sha256_file()` (`#L131-L139`), `snapshot_tree_manifest()` (`#L145-L202`), `diff_manifests()` (`#L205-L218`), `build_unified_diff()` (`#L221-L259`), `clone_cow_directory()` (`#L262-L296`), `run_in_bwrap()` (`#L299-L387`), `check_bwrap_available()` (`#L390-L400`), `resolve_transcript_path()` (`#L428-L463`), `parse_transcript_telemetry()` (`#L466-L608`), `evaluate_ab_comparison()` (`#L754-L983`), `main()` (`#L986-L1763`) | `1767` | `84677e0ffc` |
| `skills/project-memory/scripts/sync_memory.py` | `Python 3.10+` | Flags: `--memory-root`, `--vault`, `--init-memory`, `--init-vault`, `--mode`, `--convert-mode`, `--default-entity`, `--eject-templates`, `--init-project`, `--project`, `--section`, `--invariants`, `--add-lesson`, `--reinforce-lesson`, `--add-playbook`, `--update-playbook`, `--playbook-id`, `--title`, `--trigger`, `--steps`, `--verification-gate`, `--force-new`, `--lesson-disposition`, `--verify-checkpoints`, `--lesson-id` *(+54 more)* — Symbols: `clear_inprocess_memory_caches()` (`#L164-L171`), `today_iso()` (`#L260-L261`), `atomic_write_text()` (`#L264-L294`), `sanitize_entity_filename()` (`#L297-L300`), `parse_stdlib_frontmatter()` (`#L303-L306`), `render_template()` (`#L411-L429`), `build_repo_auto_tree()` (`#L544-L566`), `build_ascii_directory_tree()` (`#L569-L611`), `sync_obsidian_visual_brain()` (`#L694-L1009`), `resolve_project_repo_state()` (`#L1180-L1262`), `sync_hardware_telemetry()` (`#L1748-L1890`), `sync_software_telemetry()` (`#L1934-L2046`) | `10592` | `031aba7ce8` |
| `skills/skill-architect/scripts/audit_skill_hygiene.py` | `Python 3.10+` | Flags: `--audit`, `--check-new`, `--target-skill`, `--root`, `--repo`, `--repo-root`, `--strict-structure`, `--json` — Symbols: `resolve_default_root()` (`#L100-L106`), `parse_frontmatter()` (`#L109-L112`), `strip_markdown_formatting()` (`#L115-L118`), `stem_token()` (`#L121-L130`), `tokenize_words()` (`#L133-L148`), `audit_script_stdlib_compliance()` (`#L332-L411`), `audit_ring12_gateway_compliance()` (`#L520-L681`), `main()` (`#L1767-L1829`) | `1833` | `d79467a79e` |
| `skills/teach-me/scripts/teach_brief.py` | `Python 3.10+` | Flags: `--workspace`, `--memory-root`, `--briefs-root`, `--init-brief`, `--subject`, `--impact-on`, `--query`, `--slug`, `--domain`, `--project`, `--entity`, `--compartment`, `--out`, `--rename-clean`, `--verify`, `--auto-slug`, `--require-depth`, `--model-tier`, `--force-model-tier`, `--classify-complexity`, `--context-seed`, `--routing-only`, `--thread-context`, `--redact-query`, `--attest-subagent` *(+10 more)* — Symbols: `build_brief_slug()` (`#L336-L372`), `build_concise_phrase()` (`#L375-L395`), `format_brief_display_name()` (`#L398-L408`), `format_model_tier_badge()` (`#L447-L458`), `classify_query_complexity()` (`#L461-L539`), `resolve_cold_start_project()` (`#L681-L924`), `build_context_seed()` (`#L962-L1165`), `build_chat_rails()` (`#L1168-L1199`), `build_chat_card_template()` (`#L1202-L1230`), `resolve_roots()` (`#L1233-L1262`), `ensure_briefs_root_readme()` (`#L1265-L1269`), `verify_brief_structure()` (`#L1631-L1774`) | `3102` | `1f0f38a6bb` |
| `skills/visual-studio/scripts/render_diagram.py` | `Python 3.10+` | Flags: `--list-palettes`, `--list-blueprints`, `--memory-root`, `--spec`, `--blueprint`, `--palette`, `--out-dir`, `--basename`, `-o`, `--output`, `--png`, `--preview-png`, `--github-card`, `--svg-only`, `--strict` — Symbols: `esc()` (`#L163-L164`), `extract_frontmatter_aliases()` (`#L167-L180`), `apply_palette_defaults()` (`#L183-L196`), `normalize_key()` (`#L199-L200`), `discover_palettes()` (`#L203-L278`), `render_inline_markup()` (`#L348-L357`), `resolve_style_colors()` (`#L360-L394`), `DiagramBuilder()` (`#L397-L631`), `render_layered_architecture()` (`#L634-L795`), `render_column_dataflow()` (`#L798-L949`), `render_hardware_pinout_pneumatic()` (`#L952-L1183`), `render_comparison_matrix()` (`#L1186-L1319`) | `1791` | `803311e17d` |
| `templates/hooks/post-worktree-sync.sh` | `POSIX Bash` | Executable Script / Source | `69` | `d767ade2b9` |
| `templates/hooks/pre-commit.sh` | `POSIX Bash` | Executable Script / Source | `96` | `f902d97322` |
| `templates/hooks/pre-push.sh` | `POSIX Bash` | Executable Script / Source | `70` | `c83b1020e3` |
| `tests/test_adapters.py` | `Python 3.10+` | Symbols: `TestAdapters()` (`#L23-L362`) | `366` | `aa1303dbfa` |
| `tests/test_claim_verification.py` | `Python 3.10+` | Symbols: `TestClaimVerification()` (`#L31-L765`) | `769` | `74f5f372f6` |
| `tests/test_core_skills.py` | `Python 3.10+` | Symbols: `TestCoreSkills()` (`#L58-L671`) | `675` | `1c82a5b1d4` |
| `tests/test_data_safety.py` | `Python 3.10+` | Symbols: `TestDataSafety()` (`#L30-L148`) | `152` | `d6e15d7905` |
| `tests/test_foundation.py` | `Python 3.10+` | Symbols: `TestFoundation()` (`#L25-L152`) | `156` | `692144d4fd` |
| `tests/test_project_memory.py` | `Python 3.10+` | Symbols: `TestProjectMemory()` (`#L20-L2013`) | `2017` | `d5c31ad9ac` |
| `tests/test_teach_me.py` | `Python 3.10+` | Symbols: `TestTeachMe()` (`#L30-L1765`) | `1769` | `dc4222734e` |
| `tests/test_v030_memory_platform.py` | `Python 3.10+` | Symbols: `TestV030Milestone1ContextFabric()` (`#L37-L276`), `TestV030Milestone2MemoryGateway()` (`#L279-L790`), `TestV030Milestone3Ring0Sudo()` (`#L855-L1190`), `TestV030Milestone4PlaybookAndEndToEnd()` (`#L1193-L1379`), `TestV031Ring0TeachMeAndTurnkeyUpgrades()` (`#L1383-L1755`) | `1758` | `30f10dcd0f` |
<!-- AUTO-SOFTWARE-MODULES:END -->

---

## 2. Configuration Schemas & Data Contracts

<!-- AUTO-SOFTWARE-SCHEMAS:START -->
| Schema / Config File | Format | Top-Level Keys / Contract Version | SHA-256 Prefix |
| :--- | :--- | :--- | :--- |
| `adapters/antigravity/hooks.json` | `JSON` | `{}` (empty object) | `ca3d163bab` |
| `adapters/claude_code/settings.json` | `JSON` | `schema_version`, `description`, `hooks` | `49415adbe3` |
| `hooks/hooks.json` | `JSON` | `{}` (empty object) | `ca3d163bab` |
| `scripts/kernel_seal.json` | `JSON` | `schema_version`, `ring`, `sealed_at`, `reason`, `entry_count`, `seal_digest` | `b838b5a7c7` |
| `scripts/script_contracts.json` | `JSON` | `schema_version`, `description`, `coupling_policy`, `scripts` | `128d08e00f` |
| `templates/homunculus_safety.example.json` | `JSON` | `schema_version`, `description`, `default_compartment`, `enforce_posix_win_user_paths_in_public`, `compartments` | `7e45cf72a5` |
| `templates/diagrams/Diagram_Palettes.json` | `JSON` | `default_palette`, `palettes` | `8918674dd9` |
<!-- AUTO-SOFTWARE-SCHEMAS:END -->

---

## 3. Deterministic Test & Verification Receipts

| Test Suite / Gate | Command | Last Verified Result | Receipt / Anchor |
| :--- | :--- | :--- | :--- |
| Unit Test Suite (`52` tests across `7` suites) | `python3 -m unittest discover -s tests -v` | `PASS (52/52 tests OK)` | `SBX-20261110_162015-7ddf774e` |
