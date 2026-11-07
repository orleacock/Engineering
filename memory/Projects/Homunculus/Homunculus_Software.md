---
project: "Homunculus"
entity: "Alchemical-3D"
compartment: "cleanroom"
telemetry_domain: "software"
local_path: "/home/orin/Projects/Alchemical3D/Homunculus"
inventory_sha256: "3a6b2e0dcbff"
last_synced: "2026-11-06"
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
| `addons/author-voice-cadence/scripts/extract_voice_cadence.py` | `Python 3.10+` | Flags: `--inbox`, `--scope`, `--author`, `--min-words`, `--stitch-minutes`, `--exemplars-per-cat` — Symbols: `PostRecord()`, `parse_ts()`, `clean_post_text()`, `strip_code_for_prose_metrics()`, `classify_channel_domain()` | `1413` | `90fa9cefbb` |
| `scripts/audit_data_boundary.py` | `Python 3.10+` | Flags: `--repo`, `--config`, `--compartment`, `--staged`, `--push-stdin`, `--remote-name` — Symbols: `BoundaryPolicy()`, `load_boundary_config()`, `classify_compartment()`, `active_filename_rules()`, `active_content_rules()` | `833` | `78b59506e8` |
| `scripts/audit_portability.py` | `Python 3.10+` | Flags: `--repo`, `--forbid-token`, `--json` — Symbols: `decode_file_text()`, `audit_repository()`, `main()` | `378` | `1b8fcd4bac` |
| `scripts/build_adapters.py` | `Python 3.10+` | Flags: `--homunculus-root`, `--workspace`, `--client`, `--build-repo-adapters`, `--prefer-copy`, `--install-git-hooks` — Symbols: `render_agents_md()`, `render_claude_md()`, `render_cursor_mdc_files()`, `build_reference_adapters_in_repo()`, `apply_workspace_adapters()` | `583` | `e017fe51a8` |
| `scripts/homunculus_paths.py` | `Python 3.10+` | Flags: `--workspace`, `--homunculus-root`, `--init-config`, `--memory-mode`, `--memory-dir`, `--simulate-os` — Symbols: `detect_os_tier()`, `resolve_homunculus_root()`, `resolve_workspace_config()`, `probe_runtime_capabilities()`, `write_workspace_config()` | `325` | `8092c45c40` |
| `skills/claim-verification/scripts/verify_claims.py` | `Python 3.10+` | Flags: `--target`, `--sources`, `--dump-whitelist`, `--fail-on-tbd`, `--strict-provenance`, `--memory-root` — Symbols: `normalize_counted_noun()`, `canonicalize_unit()`, `parse_num()`, `strip_non_claim_regions()`, `normalize_fastener()` | `2804` | `ef13e7cd2a` |
| `skills/doc-and-card-studio/scripts/audit_repo_docs.py` | `Python 3.10+` | Flags: `target`, `--files`, `--repo-type`, `--repo-root`, `--fail-on-tbd`, `--skip-image-check` — Symbols: `load_brand_config()`, `collect_repo_cad_files()`, `audit_markdown_file()`, `main()` | `721` | `d6605fdbf9` |
| `skills/doc-and-card-studio/scripts/format_image.py` | `Python 3.10+` | Flags: `inputs`, `-o`, `--combine`, `--no-divider`, `--inspect`, `--bg-color` — Symbols: `parse_rgba()`, `has_studio_grey_background()`, `is_full_bleed_part_crop()`, `is_already_formatted()`, `strip_existing_card_margin()` | `711` | `4cebf02c6d` |
| `skills/engineering-sandbox/scripts/sandbox_runner.py` | `Python 3.10+` | Flags: `--mode`, `--target-dir`, `--writable-dir`, `--cwd`, `--spec`, `--faults` — Symbols: `sha256_file()`, `snapshot_tree_manifest()`, `diff_manifests()`, `build_unified_diff()`, `clone_cow_directory()` | `1522` | `0572247dac` |
| `skills/project-memory/scripts/sync_memory.py` | `Python 3.10+` | Flags: `--memory-root`, `--init-memory`, `--mode`, `--convert-mode`, `--default-entity`, `--init-project` — Symbols: `today_iso()`, `sanitize_entity_filename()`, `parse_stdlib_frontmatter()`, `update_frontmatter_fields()`, `replace_marker_block()` | `2638` | `ff3dde506a` |
| `skills/skill-architect/scripts/audit_skill_hygiene.py` | `Python 3.10+` | Flags: `--audit`, `--check-new`, `--target-skill`, `--root`, `--strict-structure`, `--json` — Symbols: `resolve_default_root()`, `parse_frontmatter()`, `strip_markdown_formatting()`, `stem_token()`, `tokenize_words()` | `1159` | `2051d73fc5` |
| `skills/subagent-orchestrator/scripts/inspect_hardware_ecosystem.py` | `Python 3.10+` | Flags: `--vault`, `--project`, `--repo`, `--json-out`, `--all`, `--check-cache` — Symbols: `parse_frontmatter()`, `normalize_part_stem()`, `classify_bore_diameter()`, `detect_step_unit_scale()`, `inspect_step_file()` | `1083` | `ee71690099` |
| `skills/visual-studio/scripts/render_diagram.py` | `Python 3.10+` | Flags: `--list-palettes`, `--list-blueprints`, `--memory-root`, `--spec`, `--blueprint`, `--palette` — Symbols: `esc()`, `extract_frontmatter_aliases()`, `apply_palette_defaults()`, `normalize_key()`, `discover_palettes()` | `1771` | `75694f534a` |
| `templates/hooks/pre-commit.sh` | `POSIX Bash` | Executable Script / Source | `76` | `d66debdd77` |
| `templates/hooks/pre-push.sh` | `POSIX Bash` | Executable Script / Source | `64` | `860e71abc6` |
| `tests/test_phase1_foundation.py` | `Python 3.10+` | Symbols: `TestHomunculusPhase1Foundation()` | `92` | `98289cacdf` |
| `tests/test_phase2a_data_safety.py` | `Python 3.10+` | Symbols: `TestHomunculusPhase2ADataSafetyAndRules()` | `152` | `36c3003b3f` |
| `tests/test_phase2b_adapters.py` | `Python 3.10+` | Symbols: `TestPhase2BAdapters()` | `190` | `66d7a2b23b` |
| `tests/test_phase3a_memory.py` | `Python 3.10+` | Symbols: `TestPhase3ADualModeMemory()` | `289` | `a499d40390` |
| `tests/test_phase3b_skills.py` | `Python 3.10+` | Symbols: `TestPhase3BSkills()` | `846` | `eeda536cb3` |
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
