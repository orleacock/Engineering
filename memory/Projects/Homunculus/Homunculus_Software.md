---
project: "Homunculus"
entity: "Alchemical-3D"
compartment: "cleanroom"
telemetry_domain: "software"
local_path: "/home/orin/Projects/Alchemical3D/Homunculus"
inventory_sha256: "a113b1c1ae89"
last_synced: "2026-11-11"
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
| `addons/hardware-cad-inspector/scripts/inspect_hardware_ecosystem.py` | `Python 3.10+` | Flags: `--vault`, `--memory-root`, `--project`, `--repo`, `--json-out`, `--all`, `--check-cache`, `--sync-manifest`, `--force-rescan` — Symbols: `normalize_part_stem()` (`#L114-L123`), `detect_step_unit_scale()` (`#L154-L173`), `inspect_step_file()` (`#L176-L379`), `inspect_stl_file()` (`#L382-L485`), `inspect_cfg_file()` (`#L488-L528`), `scan_repo_hardware()` (`#L531-L663`), `render_manifest_markdown()` (`#L700-L893`), `resolve_projects()` (`#L896-L964`), `main()` (`#L967-L1227`) | `1231` | `5f2dd17e32` |
| `scripts/audit_data_boundary.py` | `Python 3.10+` | Flags: `repo_pos`, `--repo`, `--config`, `--compartment`, `--staged`, `--push-stdin`, `--remote-name`, `--remote-url`, `--worktree`, `--all-in-root` — Symbols: `BoundaryPolicy()` (`#L111-L125`), `load_boundary_config()` (`#L136-L235`), `classify_compartment()` (`#L238-L265`), `active_filename_rules()` (`#L268-L274`), `active_content_rules()` (`#L277-L281`), `audit_staged()` (`#L619-L642`), `verify_remote_and_author_for_push()` (`#L645-L696`), `audit_push_stdin()` (`#L699-L760`), `audit_worktree()` (`#L763-L799`), `main()` (`#L802-L868`) | `872` | `e00b6f5793` |
| `scripts/audit_portability.py` | `Python 3.10+` | Flags: `--repo`, `--root`, `--repo-root`, `--forbid-token`, `--json` — Symbols: `audit_repository()` (`#L120-L278`), `main()` (`#L281-L325`) | `329` | `8d54274c04` |
| `scripts/build_adapters.py` | `Python 3.10+` | Flags: `--homunculus-root`, `--workspace`, `--client`, `--harness`, `--build-repo-adapters`, `--prefer-copy`, `--install-git-hooks`, `--package-cowork-zips`, `--global-agy-config-dir`, `--include-agents-md`, `--agy-skills-json`, `--json` — Symbols: `render_agents_md()` (`#L176-L201`), `render_claude_md()` (`#L204-L229`), `render_cursor_mdc_files()` (`#L232-L263`), `build_reference_adapters_in_repo()` (`#L266-L378`), `apply_workspace_adapters()` (`#L420-L653`), `main()` (`#L656-L744`) | `748` | `de6b01929b` |
| `scripts/homunculus_paths.py` | `Python 3.10+` | Flags: `--workspace`, `--homunculus-root`, `--memory-root`, `--init-config`, `--memory-mode`, `--memory-dir`, `--simulate-os`, `--check`, `--ensure-fresh`, `--map`, `--sync-maps`, `--lock-core`, `--unlock-core`, `--quiet`, `--json` — Symbols: `parse_frontmatter_full()` (`#L96-L147`), `parse_frontmatter()` (`#L150-L153`), `strip_yaml_frontmatter()` (`#L156-L159`), `norm_slash_path()` (`#L162-L189`), `enforce_anti_snoop_gate()` (`#L192-L246`), `resolve_homunculus_root()` (`#L309-L336`), `resolve_workspace_config()` (`#L347-L467`), `inspect_python_ast_and_map()` (`#L767-L906`), `sync_script_navigation_map()` (`#L1019-L1076`), `ensure_directory_fresh()` (`#L1159-L1245`), `main()` (`#L1279-L1489`) | `1493` | `d92b473354` |
| `skills/claim-verification/scripts/verify_claims.py` | `Python 3.10+` | Flags: `--target`, `--draft`, `--sources`, `--dump-whitelist`, `--fail-on-tbd`, `--strict-provenance`, `--require-anchors`, `--require-git-clean-sources`, `--memory-root`, `--project-dir`, `--entity`, `--transcript`, `--skip-freshness-check`, `--json` — Symbols: `normalize_counted_noun()` (`#L437-L455`), `canonicalize_unit()` (`#L458-L485`), `parse_num()` (`#L488-L489`), `strip_non_claim_regions()` (`#L492-L555`), `normalize_fastener()` (`#L558-L562`), `GitWorktreeCache()` (`#L673-L751`), `inspect_source_provenance()` (`#L754-L837`), `SourceFileInfo()` (`#L976-L1198`), `SourceIndex()` (`#L1278-L1919`), `verify_calc_marker()` (`#L2021-L2108`), `resolve_subagent_transcript_path()` (`#L2130-L2166`), `audit_target()` (`#L2415-L3412`) | `3726` | `bccfacc53e` |
| `skills/doc-and-card-studio/scripts/audit_repo_docs.py` | `Python 3.10+` | Flags: `target`, `--files`, `--repo-type`, `--repo-root`, `--repo`, `--fail-on-tbd`, `--skip-image-check`, `--brand-config`, `--no-brand-config` — Symbols: `load_brand_config()` (`#L77-L136`), `collect_repo_cad_files()` (`#L267-L281`), `audit_markdown_file()` (`#L284-L686`), `main()` (`#L689-L866`) | `870` | `4114868bb8` |
| `skills/doc-and-card-studio/scripts/format_image.py` | `Python 3.10+` | Flags: `inputs`, `-o`, `--output`, `--combine`, `--no-divider`, `--inspect`, `--bg-color`, `--no-whiten-bg`, `--inner-padding`, `--force-inner-padding`, `--card-size`, `--margin`, `--radius`, `--border-width`, `--border-color`, `--force` — Symbols: `parse_rgba()` (`#L101-L106`), `has_studio_grey_background()` (`#L117-L138`), `is_full_bleed_part_crop()` (`#L141-L162`), `is_already_formatted()` (`#L165-L223`), `strip_existing_card_margin()` (`#L226-L262`), `whiten_studio_background()` (`#L265-L362`), `render_card_with_shadow()` (`#L412-L468`), `format_single_image()` (`#L471-L517`), `format_combined_pair()` (`#L520-L572`), `main()` (`#L575-L730`) | `734` | `2f19180e81` |
| `skills/engineering-sandbox/scripts/sandbox_runner.py` | `Python 3.10+` | Flags: `--mode`, `--target-dir`, `--workspace`, `--writable-dir`, `--cwd`, `--spec`, `--faults`, `--cmd`, `--fault-case`, `--allow-noop-setup`, `--timeout`, `--report-dir`, `--keep-overlay`, `--keep-failed-cow`, `--blind-dir`, `--visible-dir`, `--blind-transcript`, `--visible-transcript`, `--compare-source`, `--repo-root`, `--prepare`, `--json` — Symbols: `sha256_file()` (`#L131-L139`), `snapshot_tree_manifest()` (`#L145-L202`), `diff_manifests()` (`#L205-L218`), `build_unified_diff()` (`#L221-L259`), `clone_cow_directory()` (`#L262-L296`), `run_in_bwrap()` (`#L299-L387`), `check_bwrap_available()` (`#L390-L400`), `resolve_transcript_path()` (`#L428-L463`), `parse_transcript_telemetry()` (`#L466-L608`), `evaluate_ab_comparison()` (`#L754-L983`), `main()` (`#L986-L1761`) | `1765` | `97aa969eee` |
| `skills/project-memory/scripts/sync_memory.py` | `Python 3.10+` | Flags: `--memory-root`, `--vault`, `--init-memory`, `--init-vault`, `--mode`, `--convert-mode`, `--default-entity`, `--eject-templates`, `--init-project`, `--project`, `--section`, `--invariants`, `--add-lesson`, `--reinforce-lesson`, `--add-playbook`, `--update-playbook`, `--playbook-id`, `--title`, `--trigger`, `--steps`, `--verification-gate`, `--force-new`, `--lesson-disposition`, `--verify-checkpoints`, `--lesson-id` *(+54 more)* — Symbols: `today_iso()` (`#L143-L144`), `atomic_write_text()` (`#L147-L170`), `sanitize_entity_filename()` (`#L173-L176`), `parse_stdlib_frontmatter()` (`#L179-L182`), `update_frontmatter_fields()` (`#L185-L213`), `render_template()` (`#L287-L305`), `build_repo_auto_tree()` (`#L420-L442`), `build_ascii_directory_tree()` (`#L445-L487`), `sync_obsidian_visual_brain()` (`#L570-L885`), `resolve_project_repo_state()` (`#L1056-L1136`), `sync_hardware_telemetry()` (`#L1622-L1764`), `sync_software_telemetry()` (`#L1808-L1920`) | `9481` | `f039b4b122` |
| `skills/skill-architect/scripts/audit_skill_hygiene.py` | `Python 3.10+` | Flags: `--audit`, `--check-new`, `--target-skill`, `--root`, `--repo`, `--repo-root`, `--strict-structure`, `--json` — Symbols: `resolve_default_root()` (`#L75-L81`), `parse_frontmatter()` (`#L84-L87`), `strip_markdown_formatting()` (`#L90-L93`), `stem_token()` (`#L96-L105`), `tokenize_words()` (`#L108-L123`), `audit_script_stdlib_compliance()` (`#L303-L382`), `main()` (`#L1449-L1509`) | `1513` | `51c293516f` |
| `skills/teach-me/scripts/teach_brief.py` | `Python 3.10+` | Flags: `--workspace`, `--memory-root`, `--briefs-root`, `--init-brief`, `--subject`, `--impact-on`, `--slug`, `--domain`, `--project`, `--entity`, `--out`, `--rename-clean`, `--verify`, `--auto-slug`, `--require-depth`, `--model-tier`, `--classify-complexity`, `--sources`, `--fail-on-tbd`, `--strict-provenance`, `--list`, `--promote`, `--target`, `--json` — Symbols: `build_brief_slug()` (`#L268-L304`), `build_concise_phrase()` (`#L307-L327`), `format_brief_display_name()` (`#L330-L340`), `format_model_tier_badge()` (`#L365-L376`), `classify_query_complexity()` (`#L379-L442`), `build_chat_rails()` (`#L445-L476`), `build_chat_card_template()` (`#L479-L507`), `resolve_roots()` (`#L510-L533`), `ensure_briefs_root_readme()` (`#L536-L540`), `verify_brief_structure()` (`#L653-L771`), `verify_and_stamp_brief()` (`#L774-L948`), `main()` (`#L1106-L1371`) | `1375` | `9b50b0883e` |
| `skills/visual-studio/scripts/render_diagram.py` | `Python 3.10+` | Flags: `--list-palettes`, `--list-blueprints`, `--memory-root`, `--spec`, `--blueprint`, `--palette`, `--out-dir`, `--basename`, `-o`, `--output`, `--png`, `--preview-png`, `--github-card`, `--svg-only`, `--strict` — Symbols: `esc()` (`#L163-L164`), `extract_frontmatter_aliases()` (`#L167-L180`), `apply_palette_defaults()` (`#L183-L196`), `normalize_key()` (`#L199-L200`), `discover_palettes()` (`#L203-L278`), `render_inline_markup()` (`#L348-L357`), `resolve_style_colors()` (`#L360-L394`), `DiagramBuilder()` (`#L397-L631`), `render_layered_architecture()` (`#L634-L795`), `render_column_dataflow()` (`#L798-L949`), `render_hardware_pinout_pneumatic()` (`#L952-L1183`), `render_comparison_matrix()` (`#L1186-L1319`) | `1791` | `803311e17d` |
| `templates/hooks/post-worktree-sync.sh` | `POSIX Bash` | Executable Script / Source | `69` | `d767ade2b9` |
| `templates/hooks/pre-commit.sh` | `POSIX Bash` | Executable Script / Source | `87` | `b5f801e1eb` |
| `templates/hooks/pre-push.sh` | `POSIX Bash` | Executable Script / Source | `70` | `c83b1020e3` |
| `tests/test_adapters.py` | `Python 3.10+` | Symbols: `TestAdapters()` (`#L23-L362`) | `366` | `aa1303dbfa` |
| `tests/test_claim_verification.py` | `Python 3.10+` | Symbols: `TestClaimVerification()` (`#L31-L765`) | `769` | `74f5f372f6` |
| `tests/test_core_skills.py` | `Python 3.10+` | Symbols: `TestCoreSkills()` (`#L58-L671`) | `675` | `1c82a5b1d4` |
| `tests/test_data_safety.py` | `Python 3.10+` | Symbols: `TestDataSafety()` (`#L30-L148`) | `152` | `d6e15d7905` |
| `tests/test_foundation.py` | `Python 3.10+` | Symbols: `TestFoundation()` (`#L25-L152`) | `156` | `692144d4fd` |
| `tests/test_project_memory.py` | `Python 3.10+` | Symbols: `TestProjectMemory()` (`#L20-L2006`) | `2010` | `ca3158c1a5` |
| `tests/test_teach_me.py` | `Python 3.10+` | Symbols: `TestTeachMe()` (`#L30-L704`) | `708` | `e1bac96d24` |
<!-- AUTO-SOFTWARE-MODULES:END -->

---

## 2. Configuration Schemas & Data Contracts

<!-- AUTO-SOFTWARE-SCHEMAS:START -->
| Schema / Config File | Format | Top-Level Keys / Contract Version | SHA-256 Prefix |
| :--- | :--- | :--- | :--- |
| `adapters/antigravity/hooks.json` | `JSON` | `{}` (empty object) | `ca3d163bab` |
| `adapters/claude_code/settings.json` | `JSON` | `schema_version`, `description`, `hooks` | `49415adbe3` |
| `hooks/hooks.json` | `JSON` | `{}` (empty object) | `ca3d163bab` |
| `scripts/script_contracts.json` | `JSON` | `schema_version`, `description`, `coupling_policy`, `scripts` | `bf8a5b78fa` |
| `templates/homunculus_safety.example.json` | `JSON` | `schema_version`, `description`, `default_compartment`, `enforce_posix_win_user_paths_in_public`, `compartments` | `7e45cf72a5` |
| `templates/diagrams/Diagram_Palettes.json` | `JSON` | `default_palette`, `palettes` | `8918674dd9` |
<!-- AUTO-SOFTWARE-SCHEMAS:END -->

---

## 3. Deterministic Test & Verification Receipts

| Test Suite / Gate | Command | Last Verified Result | Receipt / Anchor |
| :--- | :--- | :--- | :--- |
| Unit Test Suite (`52` tests across `7` suites) | `python3 -m unittest discover -s tests -v` | `PASS (52/52 tests OK)` | `SBX-20261110_162015-7ddf774e` |
