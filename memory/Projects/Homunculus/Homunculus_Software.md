---
project: "Homunculus"
entity: "Alchemical-3D"
compartment: "cleanroom"
telemetry_domain: "software"
local_path: "/home/orin/Projects/Alchemical3D/Homunculus"
inventory_sha256: "e38a78619ffb"
last_synced: "2026-11-08"
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
| `addons/author-voice-cadence/scripts/extract_voice_cadence.py` | `Python 3.10+` | Flags: `--inbox`, `--scope`, `--author`, `--min-words`, `--stitch-minutes`, `--exemplars-per-cat`, `--output` — Symbols: `PostRecord()` (`#L219-L238`), `parse_ts()` (`#L241-L257`), `clean_post_text()` (`#L260-L264`), `strip_code_for_prose_metrics()` (`#L267-L270`), `classify_channel_domain()` (`#L273-L294`), `main()` (`#L1344-L1426`) | `1430` | `6ff66488f7` |
| `scripts/audit_data_boundary.py` | `Python 3.10+` | Flags: `--repo`, `--config`, `--compartment`, `--staged`, `--push-stdin`, `--remote-name`, `--remote-url`, `--worktree` — Symbols: `BoundaryPolicy()` (`#L110-L124`), `load_boundary_config()` (`#L135-L234`), `classify_compartment()` (`#L237-L264`), `active_filename_rules()` (`#L267-L273`), `active_content_rules()` (`#L276-L280`), `audit_staged()` (`#L582-L605`), `verify_remote_and_author_for_push()` (`#L608-L659`), `audit_push_stdin()` (`#L662-L727`), `audit_worktree()` (`#L730-L766`), `main()` (`#L769-L831`) | `835` | `35d2e81337` |
| `scripts/audit_portability.py` | `Python 3.10+` | Flags: `--repo`, `--root`, `--repo-root`, `--forbid-token`, `--json` — Symbols: `decode_file_text()` (`#L73-L75`), `audit_repository()` (`#L122-L280`), `main()` (`#L283-L327`) | `331` | `f14cacbc59` |
| `scripts/build_adapters.py` | `Python 3.10+` | Flags: `--homunculus-root`, `--workspace`, `--client`, `--harness`, `--build-repo-adapters`, `--prefer-copy`, `--install-git-hooks`, `--package-cowork-zips` — Symbols: `render_agents_md()` (`#L177-L202`), `render_claude_md()` (`#L205-L230`), `render_cursor_mdc_files()` (`#L233-L264`), `build_reference_adapters_in_repo()` (`#L267-L379`), `apply_workspace_adapters()` (`#L406-L609`), `main()` (`#L612-L694`) | `698` | `99382b22ae` |
| `scripts/homunculus_paths.py` | `Python 3.10+` | Flags: `--workspace`, `--homunculus-root`, `--memory-root`, `--init-config`, `--memory-mode`, `--memory-dir`, `--simulate-os`, `--check` — Symbols: `parse_frontmatter_full()` (`#L90-L141`), `strip_yaml_frontmatter()` (`#L144-L147`), `decode_file_text()` (`#L150-L171`), `detect_os_tier()` (`#L174-L207`), `resolve_homunculus_root()` (`#L210-L237`), `resolve_workspace_config()` (`#L248-L334`), `inspect_python_ast_and_map()` (`#L540-L663`), `sync_script_navigation_map()` (`#L681-L728`), `ensure_directory_fresh()` (`#L811-L889`), `main()` (`#L892-L1049`) | `1053` | `705f04f35b` |
| `skills/claim-verification/scripts/verify_claims.py` | `Python 3.10+` | Flags: `--target`, `--draft`, `--sources`, `--dump-whitelist`, `--fail-on-tbd`, `--strict-provenance`, `--require-anchors`, `--require-git-clean-sources` — Symbols: `normalize_counted_noun()` (`#L378-L394`), `canonicalize_unit()` (`#L397-L424`), `parse_num()` (`#L427-L428`), `strip_non_claim_regions()` (`#L431-L494`), `normalize_fastener()` (`#L497-L501`), `GitWorktreeCache()` (`#L612-L690`), `inspect_source_provenance()` (`#L693-L776`), `SourceFileInfo()` (`#L911-L1102`), `SourceIndex()` (`#L1191-L1633`), `verify_calc_marker()` (`#L1735-L1822`), `audit_target()` (`#L2028-L2832`), `verify_target_inprocess()` (`#L2856-L2880`) | `3130` | `65238ab4fc` |
| `skills/doc-and-card-studio/scripts/audit_repo_docs.py` | `Python 3.10+` | Flags: `target`, `--files`, `--repo-type`, `--repo-root`, `--repo`, `--fail-on-tbd`, `--skip-image-check`, `--brand-config` — Symbols: `load_brand_config()` (`#L76-L135`), `collect_repo_cad_files()` (`#L213-L227`), `audit_markdown_file()` (`#L230-L555`), `main()` (`#L558-L735`) | `739` | `9e51b7b0ae` |
| `skills/doc-and-card-studio/scripts/format_image.py` | `Python 3.10+` | Flags: `inputs`, `-o`, `--output`, `--combine`, `--no-divider`, `--inspect`, `--bg-color`, `--no-whiten-bg` — Symbols: `parse_rgba()` (`#L100-L105`), `has_studio_grey_background()` (`#L116-L137`), `is_full_bleed_part_crop()` (`#L140-L161`), `is_already_formatted()` (`#L164-L222`), `strip_existing_card_margin()` (`#L225-L261`), `whiten_studio_background()` (`#L264-L361`), `render_card_with_shadow()` (`#L411-L467`), `format_single_image()` (`#L470-L516`), `format_combined_pair()` (`#L519-L571`), `main()` (`#L574-L736`) | `740` | `bb452b6e94` |
| `skills/engineering-sandbox/scripts/sandbox_runner.py` | `Python 3.10+` | Flags: `--mode`, `--target-dir`, `--workspace`, `--writable-dir`, `--cwd`, `--spec`, `--faults`, `--cmd` — Symbols: `sha256_file()` (`#L124-L132`), `snapshot_tree_manifest()` (`#L135-L158`), `diff_manifests()` (`#L161-L174`), `build_unified_diff()` (`#L177-L215`), `clone_cow_directory()` (`#L218-L252`), `run_in_bwrap()` (`#L255-L343`), `check_bwrap_available()` (`#L346-L356`), `resolve_transcript_path()` (`#L368-L395`), `parse_transcript_telemetry()` (`#L398-L515`), `evaluate_ab_comparison()` (`#L661-L878`), `main()` (`#L881-L1633`) | `1637` | `47b42b3aab` |
| `skills/project-memory/scripts/sync_memory.py` | `Python 3.10+` | Flags: `--memory-root`, `--vault`, `--init-memory`, `--init-vault`, `--mode`, `--convert-mode`, `--default-entity`, `--init-project` — Symbols: `today_iso()` (`#L99-L100`), `sanitize_entity_filename()` (`#L103-L106`), `parse_stdlib_frontmatter()` (`#L109-L112`), `update_frontmatter_fields()` (`#L115-L143`), `replace_marker_block()` (`#L146-L157`), `render_template()` (`#L217-L235`), `build_repo_auto_tree()` (`#L246-L282`), `build_ascii_directory_tree()` (`#L298-L395`), `sync_obsidian_visual_brain()` (`#L462-L777`), `sync_hardware_telemetry()` (`#L1310-L1434`), `sync_software_telemetry()` (`#L1476-L1577`), `sync_project_tree()` (`#L1580-L1606`) | `3018` | `72e9030ee8` |
| `skills/skill-architect/scripts/audit_skill_hygiene.py` | `Python 3.10+` | Flags: `--audit`, `--check-new`, `--target-skill`, `--root`, `--repo`, `--repo-root`, `--strict-structure`, `--json` — Symbols: `resolve_default_root()` (`#L73-L79`), `parse_frontmatter()` (`#L82-L85`), `strip_markdown_formatting()` (`#L88-L91`), `stem_token()` (`#L94-L103`), `tokenize_words()` (`#L106-L121`), `audit_script_stdlib_compliance()` (`#L285-L357`), `main()` (`#L1292-L1352`) | `1356` | `d93d1277e5` |
| `skills/subagent-orchestrator/scripts/inspect_hardware_ecosystem.py` | `Python 3.10+` | Flags: `--vault`, `--memory-root`, `--project`, `--repo`, `--json-out`, `--all`, `--check-cache`, `--sync-manifest` — Symbols: `parse_frontmatter()` (`#L91-L93`), `normalize_part_stem()` (`#L96-L105`), `classify_bore_diameter()` (`#L108-L129`), `detect_step_unit_scale()` (`#L160-L182`), `inspect_step_file()` (`#L185-L333`), `inspect_stl_file()` (`#L336-L432`), `inspect_cfg_file()` (`#L435-L460`), `scan_repo_hardware()` (`#L463-L601`), `render_manifest_markdown()` (`#L638-L823`), `resolve_projects()` (`#L826-L895`), `main()` (`#L898-L1096`) | `1100` | `49a2f48ae2` |
| `skills/teach-me/scripts/teach_brief.py` | `Python 3.10+` | Flags: `--workspace`, `--memory-root`, `--briefs-root`, `--init-brief`, `--subject`, `--impact-on`, `--slug`, `--domain` — Symbols: `build_brief_slug()` (`#L233-L269`), `build_concise_phrase()` (`#L272-L292`), `format_brief_display_name()` (`#L295-L305`), `format_model_tier_badge()` (`#L330-L341`), `classify_query_complexity()` (`#L344-L407`), `build_chat_rails()` (`#L410-L441`), `build_chat_card_template()` (`#L444-L472`), `resolve_roots()` (`#L475-L498`), `ensure_briefs_root_readme()` (`#L501-L505`), `verify_brief_structure()` (`#L618-L736`), `verify_and_stamp_brief()` (`#L739-L914`), `main()` (`#L1072-L1337`) | `1341` | `fd9f3c22fc` |
| `skills/visual-studio/scripts/render_diagram.py` | `Python 3.10+` | Flags: `--list-palettes`, `--list-blueprints`, `--memory-root`, `--spec`, `--blueprint`, `--palette`, `--out-dir`, `--basename` — Symbols: `esc()` (`#L162-L163`), `extract_frontmatter_aliases()` (`#L166-L179`), `apply_palette_defaults()` (`#L182-L195`), `normalize_key()` (`#L198-L199`), `discover_palettes()` (`#L202-L273`), `render_inline_markup()` (`#L343-L352`), `resolve_style_colors()` (`#L355-L389`), `DiagramBuilder()` (`#L392-L626`), `render_layered_architecture()` (`#L629-L790`), `render_column_dataflow()` (`#L793-L944`), `render_hardware_pinout_pneumatic()` (`#L947-L1178`), `render_comparison_matrix()` (`#L1181-L1314`) | `1789` | `7cc5b8e8c1` |
| `templates/hooks/post-worktree-sync.sh` | `POSIX Bash` | Executable Script / Source | `69` | `d767ade2b9` |
| `templates/hooks/pre-commit.sh` | `POSIX Bash` | Executable Script / Source | `87` | `b5f801e1eb` |
| `templates/hooks/pre-push.sh` | `POSIX Bash` | Executable Script / Source | `70` | `c83b1020e3` |
| `tests/test_adapters.py` | `Python 3.10+` | Symbols: `TestAdapters()` (`#L23-L294`) | `298` | `7af2b6c75f` |
| `tests/test_claim_verification.py` | `Python 3.10+` | Symbols: `TestClaimVerification()` (`#L25-L387`) | `391` | `bdb269e804` |
| `tests/test_core_skills.py` | `Python 3.10+` | Symbols: `TestCoreSkills()` (`#L54-L477`) | `481` | `4f8c6a116f` |
| `tests/test_data_safety.py` | `Python 3.10+` | Symbols: `TestDataSafety()` (`#L30-L148`) | `152` | `d6e15d7905` |
| `tests/test_foundation.py` | `Python 3.10+` | Symbols: `TestFoundation()` (`#L25-L118`) | `122` | `0b07e16f4a` |
| `tests/test_project_memory.py` | `Python 3.10+` | Symbols: `TestProjectMemory()` (`#L18-L427`) | `431` | `3ad73c6f2c` |
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
| `templates/homunculus_safety.example.json` | `JSON` | `schema_version`, `description`, `default_compartment`, `enforce_posix_win_user_paths_in_public`, `compartments` | `7e45cf72a5` |
| `templates/diagrams/Diagram_Palettes.json` | `JSON` | `default_palette`, `palettes` | `8918674dd9` |
<!-- AUTO-SOFTWARE-SCHEMAS:END -->

---

## 3. Deterministic Test & Verification Receipts

| Test Suite / Gate | Command | Last Verified Result | Receipt / Anchor |
| :--- | :--- | :--- | :--- |
| Unit Test Suite (`30` tests across `7` suites) | `python3 -m unittest discover -s tests -v` | `PASS (30/30 tests OK)` | `SBX-20261107_164747-0996f501` |
