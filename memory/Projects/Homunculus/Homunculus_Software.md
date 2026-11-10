---
project: "Homunculus"
entity: "Alchemical-3D"
compartment: "cleanroom"
telemetry_domain: "software"
local_path: "/home/orin/Projects/Alchemical3D/Homunculus"
inventory_sha256: "aa8e34d71d3d"
last_synced: "2026-11-10"
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
| `addons/author-voice-cadence/scripts/extract_voice_cadence.py` | `Python 3.10+` | Flags: `--inbox`, `--scope`, `--author`, `--min-words`, `--stitch-minutes`, `--exemplars-per-cat`, `--output` — Symbols: `PostRecord()` (`#L220-L239`), `parse_ts()` (`#L242-L258`), `clean_post_text()` (`#L261-L265`), `strip_code_for_prose_metrics()` (`#L268-L271`), `classify_channel_domain()` (`#L274-L295`), `main()` (`#L1345-L1427`) | `1431` | `383f61544b` |
| `addons/hardware-cad-inspector/scripts/inspect_hardware_ecosystem.py` | `Python 3.10+` | Flags: `--vault`, `--memory-root`, `--project`, `--repo`, `--json-out`, `--all`, `--check-cache`, `--sync-manifest`, `--force-rescan` — Symbols: `parse_frontmatter()` (`#L112-L114`), `normalize_part_stem()` (`#L117-L126`), `classify_bore_diameter()` (`#L129-L150`), `detect_step_unit_scale()` (`#L181-L200`), `inspect_step_file()` (`#L203-L406`), `inspect_stl_file()` (`#L409-L512`), `inspect_cfg_file()` (`#L515-L555`), `scan_repo_hardware()` (`#L558-L690`), `render_manifest_markdown()` (`#L727-L920`), `resolve_projects()` (`#L923-L991`), `main()` (`#L994-L1254`) | `1258` | `d72be2d099` |
| `scripts/audit_data_boundary.py` | `Python 3.10+` | Flags: `repo_pos`, `--repo`, `--config`, `--compartment`, `--staged`, `--push-stdin`, `--remote-name`, `--remote-url`, `--worktree`, `--all-in-root` — Symbols: `BoundaryPolicy()` (`#L111-L125`), `load_boundary_config()` (`#L136-L235`), `classify_compartment()` (`#L238-L265`), `active_filename_rules()` (`#L268-L274`), `active_content_rules()` (`#L277-L281`), `audit_staged()` (`#L583-L606`), `verify_remote_and_author_for_push()` (`#L609-L660`), `audit_push_stdin()` (`#L663-L728`), `audit_worktree()` (`#L731-L767`), `main()` (`#L770-L836`) | `840` | `e7313b7936` |
| `scripts/audit_portability.py` | `Python 3.10+` | Flags: `--repo`, `--root`, `--repo-root`, `--forbid-token`, `--json` — Symbols: `decode_file_text()` (`#L74-L76`), `audit_repository()` (`#L123-L281`), `main()` (`#L284-L328`) | `332` | `2fba011023` |
| `scripts/build_adapters.py` | `Python 3.10+` | Flags: `--homunculus-root`, `--workspace`, `--client`, `--harness`, `--build-repo-adapters`, `--prefer-copy`, `--install-git-hooks`, `--package-cowork-zips`, `--global-agy-config-dir`, `--include-agents-md`, `--json` — Symbols: `render_agents_md()` (`#L178-L203`), `render_claude_md()` (`#L206-L231`), `render_cursor_mdc_files()` (`#L234-L265`), `build_reference_adapters_in_repo()` (`#L268-L380`), `apply_workspace_adapters()` (`#L407-L610`), `main()` (`#L613-L695`) | `699` | `3750b625d0` |
| `scripts/homunculus_paths.py` | `Python 3.10+` | Flags: `--workspace`, `--homunculus-root`, `--memory-root`, `--init-config`, `--memory-mode`, `--memory-dir`, `--simulate-os`, `--check`, `--ensure-fresh`, `--map`, `--sync-maps`, `--lock-core`, `--unlock-core`, `--quiet`, `--json` — Symbols: `parse_frontmatter_full()` (`#L93-L144`), `strip_yaml_frontmatter()` (`#L147-L150`), `decode_file_text()` (`#L153-L174`), `detect_os_tier()` (`#L177-L210`), `resolve_homunculus_root()` (`#L213-L240`), `resolve_workspace_config()` (`#L251-L337`), `inspect_python_ast_and_map()` (`#L543-L666`), `sync_script_navigation_map()` (`#L778-L835`), `ensure_directory_fresh()` (`#L918-L996`), `main()` (`#L1030-L1240`) | `1244` | `963205e19d` |
| `skills/claim-verification/scripts/verify_claims.py` | `Python 3.10+` | Flags: `--target`, `--draft`, `--sources`, `--dump-whitelist`, `--fail-on-tbd`, `--strict-provenance`, `--require-anchors`, `--require-git-clean-sources`, `--memory-root`, `--project-dir`, `--entity`, `--transcript`, `--skip-freshness-check`, `--json` — Symbols: `normalize_counted_noun()` (`#L482-L500`), `canonicalize_unit()` (`#L503-L530`), `parse_num()` (`#L533-L534`), `strip_non_claim_regions()` (`#L537-L600`), `normalize_fastener()` (`#L603-L607`), `GitWorktreeCache()` (`#L718-L796`), `inspect_source_provenance()` (`#L799-L882`), `SourceFileInfo()` (`#L1022-L1244`), `SourceIndex()` (`#L1333-L1953`), `verify_calc_marker()` (`#L2055-L2142`), `audit_target()` (`#L2360-L3347`), `verify_target_inprocess()` (`#L3371-L3395`) | `3666` | `783e1c9a23` |
| `skills/doc-and-card-studio/scripts/audit_repo_docs.py` | `Python 3.10+` | Flags: `target`, `--files`, `--repo-type`, `--repo-root`, `--repo`, `--fail-on-tbd`, `--skip-image-check`, `--brand-config`, `--no-brand-config` — Symbols: `load_brand_config()` (`#L77-L136`), `collect_repo_cad_files()` (`#L214-L228`), `audit_markdown_file()` (`#L231-L570`), `main()` (`#L573-L750`) | `754` | `5375617e42` |
| `skills/doc-and-card-studio/scripts/format_image.py` | `Python 3.10+` | Flags: `inputs`, `-o`, `--output`, `--combine`, `--no-divider`, `--inspect`, `--bg-color`, `--no-whiten-bg`, `--inner-padding`, `--force-inner-padding`, `--card-size`, `--margin`, `--radius`, `--border-width`, `--border-color`, `--force` — Symbols: `parse_rgba()` (`#L101-L106`), `has_studio_grey_background()` (`#L117-L138`), `is_full_bleed_part_crop()` (`#L141-L162`), `is_already_formatted()` (`#L165-L223`), `strip_existing_card_margin()` (`#L226-L262`), `whiten_studio_background()` (`#L265-L362`), `render_card_with_shadow()` (`#L412-L468`), `format_single_image()` (`#L471-L517`), `format_combined_pair()` (`#L520-L572`), `main()` (`#L575-L730`) | `734` | `2f19180e81` |
| `skills/engineering-sandbox/scripts/sandbox_runner.py` | `Python 3.10+` | Flags: `--mode`, `--target-dir`, `--workspace`, `--writable-dir`, `--cwd`, `--spec`, `--faults`, `--cmd`, `--fault-case`, `--allow-noop-setup`, `--timeout`, `--report-dir`, `--keep-overlay`, `--keep-failed-cow`, `--blind-dir`, `--visible-dir`, `--blind-transcript`, `--visible-transcript`, `--compare-source`, `--repo-root`, `--prepare`, `--json` — Symbols: `sha256_file()` (`#L133-L141`), `snapshot_tree_manifest()` (`#L144-L167`), `diff_manifests()` (`#L170-L183`), `build_unified_diff()` (`#L186-L224`), `clone_cow_directory()` (`#L227-L261`), `run_in_bwrap()` (`#L264-L352`), `check_bwrap_available()` (`#L355-L365`), `resolve_transcript_path()` (`#L377-L404`), `parse_transcript_telemetry()` (`#L407-L541`), `evaluate_ab_comparison()` (`#L687-L904`), `main()` (`#L907-L1659`) | `1663` | `dc8dd9a4a6` |
| `skills/project-memory/scripts/sync_memory.py` | `Python 3.10+` | Flags: `--memory-root`, `--vault`, `--init-memory`, `--init-vault`, `--mode`, `--convert-mode`, `--default-entity`, `--init-project`, `--project`, `--section`, `--invariants`, `--add-lesson`, `--reinforce-lesson`, `--add-playbook`, `--update-playbook`, `--playbook-id`, `--title`, `--trigger`, `--steps`, `--verification-gate`, `--force-new`, `--lesson-disposition`, `--verify-checkpoints`, `--lesson-id`, `--symptom` *(+53 more)* — Symbols: `today_iso()` (`#L128-L129`), `sanitize_entity_filename()` (`#L132-L135`), `parse_stdlib_frontmatter()` (`#L138-L141`), `update_frontmatter_fields()` (`#L144-L172`), `replace_marker_block()` (`#L175-L186`), `render_template()` (`#L246-L264`), `build_repo_auto_tree()` (`#L275-L311`), `build_ascii_directory_tree()` (`#L327-L424`), `sync_obsidian_visual_brain()` (`#L505-L820`), `resolve_project_repo_state()` (`#L996-L1076`), `sync_hardware_telemetry()` (`#L1568-L1712`), `sync_software_telemetry()` (`#L1756-L1867`) | `7829` | `e1bd60c472` |
| `skills/skill-architect/scripts/audit_skill_hygiene.py` | `Python 3.10+` | Flags: `--audit`, `--check-new`, `--target-skill`, `--root`, `--repo`, `--repo-root`, `--strict-structure`, `--json` — Symbols: `resolve_default_root()` (`#L75-L81`), `parse_frontmatter()` (`#L84-L87`), `strip_markdown_formatting()` (`#L90-L93`), `stem_token()` (`#L96-L105`), `tokenize_words()` (`#L108-L123`), `audit_script_stdlib_compliance()` (`#L287-L366`), `main()` (`#L1387-L1447`) | `1451` | `473264cc36` |
| `skills/teach-me/scripts/teach_brief.py` | `Python 3.10+` | Flags: `--workspace`, `--memory-root`, `--briefs-root`, `--init-brief`, `--subject`, `--impact-on`, `--slug`, `--domain`, `--project`, `--entity`, `--out`, `--rename-clean`, `--verify`, `--auto-slug`, `--require-depth`, `--model-tier`, `--classify-complexity`, `--sources`, `--fail-on-tbd`, `--strict-provenance`, `--list`, `--promote`, `--target`, `--json` — Symbols: `build_brief_slug()` (`#L316-L352`), `build_concise_phrase()` (`#L355-L375`), `format_brief_display_name()` (`#L378-L388`), `format_model_tier_badge()` (`#L413-L424`), `classify_query_complexity()` (`#L427-L490`), `build_chat_rails()` (`#L493-L524`), `build_chat_card_template()` (`#L527-L555`), `resolve_roots()` (`#L558-L581`), `ensure_briefs_root_readme()` (`#L584-L588`), `verify_brief_structure()` (`#L701-L819`), `verify_and_stamp_brief()` (`#L822-L997`), `main()` (`#L1155-L1420`) | `1424` | `686b76d071` |
| `skills/visual-studio/scripts/render_diagram.py` | `Python 3.10+` | Flags: `--list-palettes`, `--list-blueprints`, `--memory-root`, `--spec`, `--blueprint`, `--palette`, `--out-dir`, `--basename`, `-o`, `--output`, `--png`, `--preview-png`, `--github-card`, `--svg-only`, `--strict` — Symbols: `esc()` (`#L163-L164`), `extract_frontmatter_aliases()` (`#L167-L180`), `apply_palette_defaults()` (`#L183-L196`), `normalize_key()` (`#L199-L200`), `discover_palettes()` (`#L203-L274`), `render_inline_markup()` (`#L344-L353`), `resolve_style_colors()` (`#L356-L390`), `DiagramBuilder()` (`#L393-L627`), `render_layered_architecture()` (`#L630-L791`), `render_column_dataflow()` (`#L794-L945`), `render_hardware_pinout_pneumatic()` (`#L948-L1179`), `render_comparison_matrix()` (`#L1182-L1315`) | `1787` | `04a2cd114a` |
| `templates/hooks/post-worktree-sync.sh` | `POSIX Bash` | Executable Script / Source | `69` | `d767ade2b9` |
| `templates/hooks/pre-commit.sh` | `POSIX Bash` | Executable Script / Source | `87` | `b5f801e1eb` |
| `templates/hooks/pre-push.sh` | `POSIX Bash` | Executable Script / Source | `70` | `c83b1020e3` |
| `tests/test_adapters.py` | `Python 3.10+` | Symbols: `TestAdapters()` (`#L23-L298`) | `302` | `7328946898` |
| `tests/test_claim_verification.py` | `Python 3.10+` | Symbols: `TestClaimVerification()` (`#L29-L630`) | `634` | `e39d333ac5` |
| `tests/test_core_skills.py` | `Python 3.10+` | Symbols: `TestCoreSkills()` (`#L58-L489`) | `493` | `6d5f850862` |
| `tests/test_data_safety.py` | `Python 3.10+` | Symbols: `TestDataSafety()` (`#L30-L148`) | `152` | `d6e15d7905` |
| `tests/test_foundation.py` | `Python 3.10+` | Symbols: `TestFoundation()` (`#L25-L118`) | `122` | `0b07e16f4a` |
| `tests/test_project_memory.py` | `Python 3.10+` | Symbols: `TestProjectMemory()` (`#L20-L1530`) | `1534` | `0ebbfdd22b` |
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
| `scripts/script_contracts.json` | `JSON` | `schema_version`, `description`, `coupling_policy`, `scripts` | `bd3e0e1f1f` |
| `templates/homunculus_safety.example.json` | `JSON` | `schema_version`, `description`, `default_compartment`, `enforce_posix_win_user_paths_in_public`, `compartments` | `7e45cf72a5` |
| `templates/diagrams/Diagram_Palettes.json` | `JSON` | `default_palette`, `palettes` | `8918674dd9` |
<!-- AUTO-SOFTWARE-SCHEMAS:END -->

---

## 3. Deterministic Test & Verification Receipts

| Test Suite / Gate | Command | Last Verified Result | Receipt / Anchor |
| :--- | :--- | :--- | :--- |
| Unit Test Suite (`30` tests across `7` suites) | `python3 -m unittest discover -s tests -v` | `PASS (30/30 tests OK)` | `SBX-20261107_164747-0996f501` |
