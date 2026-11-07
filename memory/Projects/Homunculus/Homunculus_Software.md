---
project: "Homunculus"
entity: "Alchemical-3D"
compartment: "cleanroom"
telemetry_domain: "software"
local_path: "/home/orin/Projects/Alchemical3D/Homunculus"
inventory_sha256: "109f5d0dc24f"
last_synced: "2026-11-07"
---

# Homunculus — Software, CLI & Schema Telemetry (`_Software.md`)

> **Authoritative Software Truth Ledger (`sync_software_telemetry`)**: Populated via `sync_memory.py --sync-software --project Homunculus`. Used by `verify_claims.py` as primary software/CLI/schema ground truth for `Homunculus` (`entity: Alchemical-3D`).

---

## 1. Runtime Entrypoints & Module Inventory

<!-- AUTO-SOFTWARE-MODULES:START -->
| Script / Module Path | Language / Runtime | CLI Flags / Public Symbols | Line Count | SHA-256 Prefix |
| :--- | :--- | :--- | :--- | :--- |
| `install.ps1` | `PowerShell` | Executable Script / Source | `80` | `51662f9f87` |
| `install.sh` | `POSIX Bash` | Executable Script / Source | `124` | `ea41dfbd6c` |
| `addons/author-voice-cadence/scripts/extract_voice_cadence.py` | `Python 3.10+` | Flags: `--inbox`, `--scope`, `--author`, `--min-words`, `--stitch-minutes`, `--exemplars-per-cat` — Symbols: `PostRecord()`, `parse_ts()`, `clean_post_text()`, `strip_code_for_prose_metrics()`, `classify_channel_domain()` | `1413` | `800318e31d` |
| `scripts/audit_data_boundary.py` | `Python 3.10+` | Flags: `--repo`, `--config`, `--compartment`, `--staged`, `--push-stdin`, `--remote-name` — Symbols: `BoundaryPolicy()`, `load_boundary_config()`, `classify_compartment()`, `active_filename_rules()`, `active_content_rules()` | `814` | `4c50eb06cb` |
| `scripts/audit_portability.py` | `Python 3.10+` | Flags: `--repo`, `--forbid-token`, `--json` — Symbols: `decode_file_text()`, `audit_repository()`, `main()` | `339` | `ebd4762313` |
| `scripts/build_adapters.py` | `Python 3.10+` | Flags: `--homunculus-root`, `--workspace`, `--client`, `--build-repo-adapters`, `--prefer-copy`, `--install-git-hooks` — Symbols: `render_agents_md()`, `render_claude_md()`, `render_cursor_mdc_files()`, `build_reference_adapters_in_repo()`, `apply_workspace_adapters()` | `684` | `c6906312e9` |
| `scripts/homunculus_paths.py` | `Python 3.10+` | Flags: `--workspace`, `--homunculus-root`, `--memory-root`, `--init-config`, `--memory-mode`, `--memory-dir` — Symbols: `parse_frontmatter_full()`, `strip_yaml_frontmatter()`, `decode_file_text()`, `detect_os_tier()`, `resolve_homunculus_root()` | `757` | `67cafbfd96` |
| `skills/claim-verification/scripts/verify_claims.py` | `Python 3.10+` | Flags: `--target`, `--sources`, `--dump-whitelist`, `--fail-on-tbd`, `--strict-provenance`, `--memory-root` — Symbols: `normalize_counted_noun()`, `canonicalize_unit()`, `parse_num()`, `strip_non_claim_regions()`, `normalize_fastener()` | `3007` | `56c0657fe7` |
| `skills/doc-and-card-studio/scripts/audit_repo_docs.py` | `Python 3.10+` | Flags: `target`, `--files`, `--repo-type`, `--repo-root`, `--fail-on-tbd`, `--skip-image-check` — Symbols: `load_brand_config()`, `collect_repo_cad_files()`, `audit_markdown_file()`, `main()` | `728` | `622b370e26` |
| `skills/doc-and-card-studio/scripts/format_image.py` | `Python 3.10+` | Flags: `inputs`, `-o`, `--combine`, `--no-divider`, `--inspect`, `--bg-color` — Symbols: `parse_rgba()`, `has_studio_grey_background()`, `is_full_bleed_part_crop()`, `is_already_formatted()`, `strip_existing_card_margin()` | `725` | `466fbfbd08` |
| `skills/engineering-sandbox/scripts/sandbox_runner.py` | `Python 3.10+` | Flags: `--mode`, `--target-dir`, `--writable-dir`, `--cwd`, `--spec`, `--faults` — Symbols: `sha256_file()`, `snapshot_tree_manifest()`, `diff_manifests()`, `build_unified_diff()`, `clone_cow_directory()` | `1597` | `6180cfb53e` |
| `skills/project-memory/scripts/sync_memory.py` | `Python 3.10+` | Flags: `--memory-root`, `--init-memory`, `--mode`, `--convert-mode`, `--default-entity`, `--init-project` — Symbols: `today_iso()`, `sanitize_entity_filename()`, `parse_stdlib_frontmatter()`, `update_frontmatter_fields()`, `replace_marker_block()` | `2991` | `7ec2f162d5` |
| `skills/skill-architect/scripts/audit_skill_hygiene.py` | `Python 3.10+` | Flags: `--audit`, `--check-new`, `--target-skill`, `--root`, `--strict-structure`, `--json` — Symbols: `resolve_default_root()`, `parse_frontmatter()`, `strip_markdown_formatting()`, `stem_token()`, `tokenize_words()` | `1333` | `e0359e4649` |
| `skills/subagent-orchestrator/scripts/inspect_hardware_ecosystem.py` | `Python 3.10+` | Flags: `--vault`, `--project`, `--repo`, `--json-out`, `--all`, `--check-cache` — Symbols: `parse_frontmatter()`, `normalize_part_stem()`, `classify_bore_diameter()`, `detect_step_unit_scale()`, `inspect_step_file()` | `1083` | `c8cedc6df9` |
| `skills/teach-me/scripts/teach_brief.py` | `Python 3.10+` | Flags: `--workspace`, `--memory-root`, `--briefs-root`, `--init-brief`, `--subject`, `--impact-on` — Symbols: `build_brief_slug()`, `build_concise_phrase()`, `format_brief_display_name()`, `build_chat_rails()`, `build_chat_card_template()` | `1086` | `200a897091` |
| `skills/visual-studio/scripts/render_diagram.py` | `Python 3.10+` | Flags: `--list-palettes`, `--list-blueprints`, `--memory-root`, `--spec`, `--blueprint`, `--palette` — Symbols: `esc()`, `extract_frontmatter_aliases()`, `apply_palette_defaults()`, `normalize_key()`, `discover_palettes()` | `1776` | `16b02f2fd8` |
| `templates/hooks/post-worktree-sync.sh` | `POSIX Bash` | Executable Script / Source | `63` | `57cc45f7fe` |
| `templates/hooks/pre-commit.sh` | `POSIX Bash` | Executable Script / Source | `76` | `d66debdd77` |
| `templates/hooks/pre-push.sh` | `POSIX Bash` | Executable Script / Source | `64` | `860e71abc6` |
| `tests/test_adapters.py` | `Python 3.10+` | Symbols: `TestAdapters()` | `298` | `7af2b6c75f` |
| `tests/test_claim_verification.py` | `Python 3.10+` | Symbols: `TestClaimVerification()` | `391` | `bdb269e804` |
| `tests/test_core_skills.py` | `Python 3.10+` | Symbols: `TestCoreSkills()` | `481` | `4f8c6a116f` |
| `tests/test_data_safety.py` | `Python 3.10+` | Symbols: `TestDataSafety()` | `152` | `d6e15d7905` |
| `tests/test_foundation.py` | `Python 3.10+` | Symbols: `TestFoundation()` | `92` | `7629c10437` |
| `tests/test_project_memory.py` | `Python 3.10+` | Symbols: `TestProjectMemory()` | `431` | `3ad73c6f2c` |
| `tests/test_teach_me.py` | `Python 3.10+` | Symbols: `TestTeachMe()` | `471` | `d8e0cf9673` |
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
| Unit Test Suite | `python3 -m unittest discover -s tests -v` | `[TBD: test_status]` | `[TBD: receipt_id]` |
