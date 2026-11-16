---
project: "Workstation_Operations"
entity: "Orin_Workstation"
compartment: "private"
telemetry_domain: "software"
local_path: "../scripts"
inventory_sha256: "d612cbd184da"
last_synced: "2026-11-16"
---

# Workstation_Operations — Software, CLI & Schema Telemetry (`_Software.md`)

> **Authoritative Software Truth Ledger (`sync_software_telemetry`)**: Populated via `sync_memory.py --sync-software --project Workstation_Operations`. Used by `verify_claims.py` as primary software/CLI/schema ground truth for `Workstation_Operations` (`entity: Orin_Workstation`).

---

## 1. Runtime Entrypoints & Module Inventory

<!-- AUTO-SOFTWARE-MODULES:START -->
| Script / Module Path | Language / Runtime | CLI Flags / Public Symbols | Line Count | SHA-256 Prefix |
| :--- | :--- | :--- | :--- | :--- |
| `benchmark_bionic_sidecar.py` | `Python 3.10+` | Flags: `--mode`, `--label`, `--history-jsonl`, `--telemetry-log`, `--record-baseline`, `--append-history`, `--compare-baseline`, `--output-md`, `--json`, `--self-test` — Symbols: `BenchMetric()` (`#L55-L69`), `run_offline_suite()` (`#L169-L548`), `run_live_suite()` (`#L551-L1046`), `load_baseline()` (`#L1049-L1063`), `render_markdown_report()` (`#L1066-L1093`), `run_self_tests()` (`#L1096-L1117`), `main()` (`#L1120-L1210`) | `1214` | `4fa6f16806` |
| `benchmark_homunculus.py` | `Python 3.10+` | Flags: `--profile`, `--quick-pulse`, `--record-pulse`, `--homunculus-dir`, `--homunculus-root`, `--memory-root`, `--version-manifest`, `--history-jsonl`, `--ledger-md`, `--baseline-version`, `--record-baseline`, `--approve-advisory-reason`, `--append-ledger`, `--history-only`, `--output-md`, `--label`, `--transcript`, `--deliverable-dir`, `--sources`, `--model-id`, `--effort`, `--self-test`, `--inject-synthetic-regression`, `--json` — Symbols: `MetricRow()` (`#L91-L108`), `percentile()` (`#L111-L123`), `snapshot_host_hashes()` (`#L126-L163`), `run_cmd_timed()` (`#L166-L189`), `probe_bwrap_erofs()` (`#L192-L227`), `build_universal_spine()` (`#L2129-L2175`), `render_regression_autopsy_md()` (`#L2318-L2406`), `render_markdown_report()` (`#L2430-L2465`), `main()` (`#L2567-L2833`) | `2837` | `04a2f747ab` |
| `bootstrap_workstation.sh` | `POSIX Bash` | Executable Script / Source | `339` | `5822033e58` |
| `git_pre_commit_boundary.sh` | `POSIX Bash` | Executable Script / Source | `275` | `195810f3e7` |
| `h_sudo.sh` | `POSIX Bash` | Executable Script / Source | `176` | `33464fd019` |
| `local_sidecar.py` | `Python 3.10+` | Flags: `--api-url`, `--model`, `--system-prompt`, `--json`, `--self-test`, `--prompt-tokens`, `--homunculus-root`, `--memory-root`, `--project`, `--name`, `--title`, `--reason`, `--overwrite`, `--staging-dir`, `--target-filename`, `--compare-against`, `action`, `--profile`, `--user-confirmed`, `--dry-run`, `--epoch-label`, `--no-archive`, `--job-file`, `--job-id`, `--wait-seconds` *(+17 more)* — Symbols: `resolve_effort_and_mode()` (`#L259-L271`), `parse_context_spec()` (`#L274-L284`), `SidecarFirewallError()` (`#L287-L288`), `SidecarEtaTrippedError()` (`#L291-L296`), `load_system_prompt()` (`#L299-L310`), `resolve_effective_max_tokens()` (`#L599-L609`), `resolve_default_api_url()` (`#L1179-L1181`), `resolve_max_eta_seconds()` (`#L1539-L1545`), `build_concrete_model_config()` (`#L2966-L3055`), `build_parser()` (`#L4451-L4554`), `main()` (`#L4557-L4595`) | `4599` | `ef1393c8db` |
| `pre_push_engineering_guard.sh` | `POSIX Bash` | Executable Script / Source | `77` | `ac977c95b2` |
| `snapshot_homunculus_version.py` | `Python 3.10+` | Flags: `--slug`, `--label`, `--raid-root`, `--homunculus-dir`, `--engineering-dir`, `--version-manifest`, `--allow-dirty`, `--skip-benchmark`, `--force-fresh-benchmark`, `--list`, `--verify`, `--dry-run`, `--json` — Symbols: `sanitize_slug()` (`#L74-L77`), `find_latest_same_dev_raid_snapshot()` (`#L89-L114`), `find_verified_benchmark_receipt()` (`#L117-L151`), `copy_tree_cow()` (`#L176-L358`), `collect_symlink_manifest()` (`#L376-L394`), `build_restore_script()` (`#L477-L684`), `build_reconstruction_index()` (`#L687-L747`), `verify_existing_snapshot()` (`#L790-L802`), `main()` (`#L805-L1107`) | `1111` | `fc6af3c4a4` |
| `verified_fastpath.py` | `Python 3.10+` | Flags: `--record-memory-audit`, `--check-memory-audit`, `--record-vrf`, `--check`, `--targets`, `--sources`, `--receipt`, `--memory-root`, `--homunculus-root`, `--repo`, `--force-fresh`, `--json` — Symbols: `resolve_homunculus_root()` (`#L73-L111`), `resolve_cache_path()` (`#L119-L132`), `compute_memory_audit_fingerprint()` (`#L206-L257`), `record_memory_audit_fastpath()` (`#L260-L292`), `check_memory_audit_fastpath()` (`#L295-L343`), `record_vrf_fastpath()` (`#L387-L445`), `check_fastpath()` (`#L520-L631`), `main()` (`#L634-L715`) | `719` | `7902e75020` |
| `version_manager.py` | `Python 3.10+` | Flags: `--homunculus-dir`, `--manifest`, `--status`, `--init-baseline`, `--sync-manifest`, `--bump`, `--reason`, `--allow-v1-public-release`, `--rollback`, `--dry-run`, `--json` — Symbols: `compute_content_tree_hash()` (`#L79-L105`), `get_git_state()` (`#L111-L160`), `load_or_create_manifest()` (`#L163-L200`), `resolve_effective_version_status()` (`#L203-L251`), `ensure_git_tag()` (`#L254-L277`), `bump_version()` (`#L280-L352`), `rollback_engine()` (`#L355-L414`), `main()` (`#L417-L556`) | `560` | `5908a68c2a` |
| `bionic_sidecar/bionic_lifecycle_hook.py` | `Python 3.10+` | Flags: `--self-test`, `--check-command`, `--simulate-event`, `--simulate-state`, `--json` — Symbols: `probe_bionic_state()` (`#L167-L204`), `evaluate_session_or_invocation()` (`#L283-L401`), `evaluate_pre_tool_use()` (`#L630-L750`), `dispatch_hook_payload()` (`#L753-L759`), `run_self_tests()` (`#L835-L1159`), `main()` (`#L1162-L1218`) | `1222` | `4354e69a68` |
| `bionic_sidecar/bionic_mcp_server.py` | `Python 3.10+` | Flags: `--self-test`, `--status`, `--json` — Symbols: `select_collision_free_sources()` (`#L111-L149`), `sanitize_quarantine_placeholder_links()` (`#L152-L167`), `bionic_control()` (`#L528-L551`), `bionic_digest()` (`#L2064-L2098`), `bionic_repo_audit()` (`#L2639-L2681`), `bionic_stage_patch()` (`#L3134-L3172`), `run_self_tests()` (`#L3179-L4354`), `main()` (`#L4357-L4378`) | `4382` | `60f569dbaf` |
| `gmail_mcp/gmail_mcp_server.py` | `Python 3.10+` | Flags: `--status`, `--import-client-secret`, `--auth`, `--no-browser` — Symbols: `get_config_dir()` (`#L90-L94`), `get_attachment_jail_dir()` (`#L97-L127`), `ensure_secure_dir()` (`#L130-L137`), `verify_secret_file_security()` (`#L140-L156`), `write_secret_json()` (`#L159-L176`), `verify_token_scopes()` (`#L239-L249`), `build_gmail_web_urls()` (`#L473-L481`), `build_draft_payload()` (`#L484-L532`), `resolve_quarantined_attachment_path()` (`#L535-L567`), `main()` (`#L1028-L1045`) | `1049` | `6f37644530` |
<!-- AUTO-SOFTWARE-MODULES:END -->

---

## 2. Configuration Schemas & Data Contracts

<!-- AUTO-SOFTWARE-SCHEMAS:START -->
| Schema / Config File | Format | Top-Level Keys / Contract Version | SHA-256 Prefix |
| :--- | :--- | :--- | :--- |
| `homunculus_version.json` | `JSON` | `schema_version`, `engine_version`, `release_stage`, `public_release_target`, `baseline_tag`, `baseline_head_sha` | `e37ff407dd` |
| `bionic_sidecar_plugin/hooks.json` | `JSON` | `bionic-sidecar-guard` | `7fa4d284c4` |
| `bionic_sidecar_plugin/mcp_config.json` | `JSON` | `mcpServers` | `f1523c1e1a` |
| `bionic_sidecar_plugin/plugin.json` | `JSON` | `name`, `version` | `08f7d5f24e` |
| `umbrella_configs/Home.homunculus.json` | `JSON` | `schema_version`, `homunculus_rel_path`, `memory_mode`, `memory_dir`, `study_briefs_dir`, `visual_studio` | `71ee5f6b66` |
| `umbrella_configs/Projects.homunculus.json` | `JSON` | `schema_version`, `homunculus_rel_path`, `memory_mode`, `memory_dir`, `study_briefs_dir`, `visual_studio` | `f2098fe12a` |
<!-- AUTO-SOFTWARE-SCHEMAS:END -->

---

## 3. Deterministic Test & Verification Receipts

<!-- AUTO-SOFTWARE-TESTS:START -->
| Test File | Test Classes | AST test_* Count | SHA-256 Prefix |
| :--- | :--- | :---: | :---: |
| *(No `test_*.py` suites indexed yet)* | — | `0` | — |

**Latest Verified Test Receipt (`2026-11-14`):** 76/76 Homunculus unittest OK (v0.3.4 3996460a1e68)
<!-- AUTO-SOFTWARE-TESTS:END -->
