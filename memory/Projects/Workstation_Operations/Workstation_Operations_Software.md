---
project: "Workstation_Operations"
entity: "Orin_Workstation"
compartment: "private"
telemetry_domain: "software"
local_path: "../scripts"
inventory_sha256: "764164cb3201"
last_synced: "2026-11-18"
---

# Workstation_Operations — Software, CLI & Schema Telemetry (`_Software.md`)

> **Authoritative Software Truth Ledger (`sync_software_telemetry`)**: Populated via `sync_memory.py --sync-software --project Workstation_Operations`. Used by `verify_claims.py` as primary software/CLI/schema ground truth for `Workstation_Operations` (`entity: Orin_Workstation`).

---

## 1. Runtime Entrypoints & Module Inventory

<!-- AUTO-SOFTWARE-MODULES:START -->
| Script / Module Path | Language / Runtime | CLI Flags / Public Symbols | Line Count | SHA-256 Prefix |
| :--- | :--- | :--- | :--- | :--- |
| `apprentice_engine.py` | `Python 3.10+` | Flags: `--backend`, `--api-url`, `--model`, `--system-prompt`, `--json`, `--self-test`, `--prompt-tokens`, `--homunculus-root`, `--memory-root`, `--project`, `--name`, `--title`, `--reason`, `--overwrite`, `--staging-dir`, `--target-filename`, `--compare-against`, `action`, `--profile`, `--user-confirmed`, `--dry-run`, `--epoch-label`, `--no-archive`, `--job-file`, `--job-id` *(+18 more)* — Symbols: `resolve_backend_adapter()` (`#L162-L186`), `migrate_legacy_bionic_cache()` (`#L189-L251`), `resolve_effort_and_mode()` (`#L403-L417`), `has_cross_audit_intent()` (`#L420-L423`), `classify_hybrid_effort()` (`#L426-L513`), `SidecarFirewallError()` (`#L544-L545`), `SidecarEtaTrippedError()` (`#L548-L553`), `resolve_effective_max_tokens()` (`#L869-L879`), `resolve_default_api_url()` (`#L1449-L1460`), `resolve_max_eta_seconds()` (`#L1818-L1824`), `build_concrete_model_config()` (`#L3304-L3393`), `build_parser()` (`#L5063-L5168`) | `5213` | `61cc679766` |
| `benchmark_apprentice.py` | `Python 3.10+` | Flags: `--mode`, `--label`, `--history-jsonl`, `--telemetry-log`, `--record-baseline`, `--append-history`, `--compare-baseline`, `--output-md`, `--json`, `--self-test` — Symbols: `BenchMetric()` (`#L56-L70`), `run_offline_suite()` (`#L170-L549`), `run_live_suite()` (`#L552-L1183`), `load_baseline()` (`#L1186-L1200`), `render_markdown_report()` (`#L1216-L1267`), `run_self_tests()` (`#L1270-L1291`), `main()` (`#L1294-L1384`) | `1388` | `7cb64f1c18` |
| `benchmark_homunculus.py` | `Python 3.10+` | Flags: `--profile`, `--quick-pulse`, `--record-pulse`, `--homunculus-dir`, `--homunculus-root`, `--memory-root`, `--version-manifest`, `--history-jsonl`, `--ledger-md`, `--baseline-version`, `--record-baseline`, `--approve-advisory-reason`, `--append-ledger`, `--history-only`, `--output-md`, `--label`, `--transcript`, `--deliverable-dir`, `--sources`, `--model-id`, `--effort`, `--self-test`, `--inject-synthetic-regression`, `--json` — Symbols: `MetricRow()` (`#L91-L108`), `percentile()` (`#L111-L123`), `snapshot_host_hashes()` (`#L126-L163`), `run_cmd_timed()` (`#L166-L189`), `probe_bwrap_erofs()` (`#L192-L227`), `build_universal_spine()` (`#L2129-L2175`), `render_regression_autopsy_md()` (`#L2318-L2406`), `render_markdown_report()` (`#L2451-L2486`), `main()` (`#L2588-L2854`) | `2858` | `ea7fcec495` |
| `bootstrap_workstation.sh` | `POSIX Bash` | Executable Script / Source | `347` | `1acd0dc74d` |
| `git_pre_commit_boundary.sh` | `POSIX Bash` | Executable Script / Source | `275` | `195810f3e7` |
| `h_sudo.sh` | `POSIX Bash` | Executable Script / Source | `176` | `33464fd019` |
| `pre_push_engineering_guard.sh` | `POSIX Bash` | Executable Script / Source | `77` | `ac977c95b2` |
| `snapshot_homunculus_version.py` | `Python 3.10+` | Flags: `--slug`, `--label`, `--raid-root`, `--homunculus-dir`, `--engineering-dir`, `--version-manifest`, `--allow-dirty`, `--skip-benchmark`, `--force-fresh-benchmark`, `--list`, `--verify`, `--dry-run`, `--json` — Symbols: `sanitize_slug()` (`#L74-L77`), `find_latest_same_dev_raid_snapshot()` (`#L89-L114`), `find_verified_benchmark_receipt()` (`#L117-L151`), `copy_tree_cow()` (`#L176-L358`), `collect_symlink_manifest()` (`#L376-L394`), `build_restore_script()` (`#L477-L684`), `build_reconstruction_index()` (`#L687-L747`), `verify_existing_snapshot()` (`#L790-L802`), `main()` (`#L805-L1107`) | `1111` | `fc6af3c4a4` |
| `verified_fastpath.py` | `Python 3.10+` | Flags: `--record-memory-audit`, `--check-memory-audit`, `--record-vrf`, `--check`, `--targets`, `--sources`, `--receipt`, `--memory-root`, `--homunculus-root`, `--repo`, `--force-fresh`, `--json` — Symbols: `resolve_homunculus_root()` (`#L76-L114`), `resolve_cache_path()` (`#L122-L135`), `compute_memory_audit_fingerprint()` (`#L289-L343`), `record_memory_audit_fastpath()` (`#L346-L378`), `check_memory_audit_fastpath()` (`#L381-L429`), `record_vrf_fastpath()` (`#L473-L531`), `check_fastpath()` (`#L606-L717`), `main()` (`#L720-L801`) | `805` | `d048fd0598` |
| `version_manager.py` | `Python 3.10+` | Flags: `--homunculus-dir`, `--manifest`, `--status`, `--init-baseline`, `--sync-manifest`, `--bump`, `--reason`, `--allow-v1-public-release`, `--rollback`, `--dry-run`, `--json` — Symbols: `compute_content_tree_hash()` (`#L79-L105`), `get_git_state()` (`#L111-L160`), `load_or_create_manifest()` (`#L163-L200`), `resolve_effective_version_status()` (`#L203-L251`), `ensure_git_tag()` (`#L254-L277`), `bump_version()` (`#L280-L352`), `rollback_engine()` (`#L355-L414`), `main()` (`#L417-L556`) | `560` | `5908a68c2a` |
| `apprentice/apprentice_lifecycle_hook.py` | `Python 3.10+` | Flags: `--self-test`, `--check-command`, `--simulate-event`, `--simulate-state`, `--json` — Symbols: `probe_bionic_state()` (`#L173-L210`), `classify_host_model_tier()` (`#L301-L333`), `evaluate_session_or_invocation()` (`#L355-L492`), `evaluate_pre_tool_use()` (`#L721-L841`), `dispatch_hook_payload()` (`#L844-L850`), `run_self_tests()` (`#L926-L1320`), `main()` (`#L1323-L1379`) | `1383` | `da63fe1541` |
| `apprentice/apprentice_mcp_server.py` | `Python 3.10+` | Flags: `--self-test`, `--status`, `--json` — Symbols: `select_collision_free_sources()` (`#L119-L157`), `sanitize_quarantine_placeholder_links()` (`#L160-L175`), `apprentice_control()` (`#L735-L760`), `apprentice_digest()` (`#L2351-L2385`), `apprentice_repo_audit()` (`#L2944-L2986`), `apprentice_stage_patch()` (`#L3550-L3588`), `apprentice_shadow_review()` (`#L3856-L3890`), `run_self_tests()` (`#L3897-L5526`), `main()` (`#L5529-L5550`) | `5554` | `6cce91b254` |
| `gmail_mcp/gmail_mcp_server.py` | `Python 3.10+` | Flags: `--status`, `--import-client-secret`, `--auth`, `--no-browser` — Symbols: `get_config_dir()` (`#L90-L94`), `get_attachment_jail_dir()` (`#L97-L127`), `ensure_secure_dir()` (`#L130-L137`), `verify_secret_file_security()` (`#L140-L156`), `write_secret_json()` (`#L159-L176`), `verify_token_scopes()` (`#L239-L249`), `build_gmail_web_urls()` (`#L473-L481`), `build_draft_payload()` (`#L484-L532`), `resolve_quarantined_attachment_path()` (`#L535-L567`), `main()` (`#L1028-L1045`) | `1049` | `6f37644530` |
<!-- AUTO-SOFTWARE-MODULES:END -->

---

## 2. Configuration Schemas & Data Contracts

<!-- AUTO-SOFTWARE-SCHEMAS:START -->
| Schema / Config File | Format | Top-Level Keys / Contract Version | SHA-256 Prefix |
| :--- | :--- | :--- | :--- |
| `homunculus_version.json` | `JSON` | `schema_version`, `engine_version`, `release_stage`, `public_release_target`, `baseline_tag`, `baseline_head_sha` | `c9737da642` |
| `apprentice_plugin/hooks.json` | `JSON` | `apprentice-guard` | `d78f19ae9e` |
| `apprentice_plugin/mcp_config.json` | `JSON` | `mcpServers` | `b1329fa2b4` |
| `apprentice_plugin/plugin.json` | `JSON` | `name`, `version` | `5730f6c226` |
| `umbrella_configs/Home.homunculus.json` | `JSON` | `schema_version`, `homunculus_rel_path`, `memory_mode`, `memory_dir`, `study_briefs_dir`, `visual_studio` | `71ee5f6b66` |
| `umbrella_configs/Projects.homunculus.json` | `JSON` | `schema_version`, `homunculus_rel_path`, `memory_mode`, `memory_dir`, `study_briefs_dir`, `visual_studio` | `f2098fe12a` |
<!-- AUTO-SOFTWARE-SCHEMAS:END -->

---

## 3. Deterministic Test & Verification Receipts

<!-- AUTO-SOFTWARE-TESTS:START -->
| Test File | Test Classes | AST test_* Count | SHA-256 Prefix |
| :--- | :--- | :---: | :---: |
| *(No `test_*.py` suites indexed yet)* | — | `0` | — |

**Latest Verified Test Receipt (`2026-11-16`):** SBX-20261116_201657-a1c0f4f0
<!-- AUTO-SOFTWARE-TESTS:END -->
