---
project: "Workstation_Operations"
entity: "Orin_Workstation"
compartment: "private"
telemetry_domain: "software"
local_path: "../scripts"
inventory_sha256: "dbadc48a20da"
last_synced: "2026-11-19"
---

# Workstation_Operations — Software, CLI & Schema Telemetry (`_Software.md`)

> **Authoritative Software Truth Ledger (`sync_software_telemetry`)**: Populated via `sync_memory.py --sync-software --project Workstation_Operations`. Used by `verify_claims.py` as primary software/CLI/schema ground truth for `Workstation_Operations` (`entity: Orin_Workstation`).

---

## 1. Runtime Entrypoints & Module Inventory

<!-- AUTO-SOFTWARE-MODULES:START -->
| Script / Module Path | Language / Runtime | CLI Flags / Public Symbols | Line Count | SHA-256 Prefix |
| :--- | :--- | :--- | :--- | :--- |
| `benchmark_homunculus.py` | `Python 3.10+` | Flags: `--profile`, `--quick-pulse`, `--record-pulse`, `--homunculus-dir`, `--homunculus-root`, `--memory-root`, `--version-manifest`, `--history-jsonl`, `--ledger-md`, `--baseline-version`, `--record-baseline`, `--approve-advisory-reason`, `--append-ledger`, `--history-only`, `--output-md`, `--label`, `--transcript`, `--deliverable-dir`, `--sources`, `--model-id`, `--effort`, `--self-test`, `--inject-synthetic-regression`, `--json` — Symbols: `MetricRow()` (`#L91-L108`), `percentile()` (`#L111-L123`), `snapshot_host_hashes()` (`#L126-L163`), `run_cmd_timed()` (`#L166-L189`), `probe_bwrap_erofs()` (`#L192-L227`), `build_universal_spine()` (`#L2128-L2174`), `render_regression_autopsy_md()` (`#L2317-L2405`), `render_markdown_report()` (`#L2450-L2485`), `main()` (`#L2587-L2853`) | `2857` | `33c341c089` |
| `bootstrap_workstation.sh` | `POSIX Bash` | Executable Script / Source | `341` | `eed78aa784` |
| `git_pre_commit_boundary.sh` | `POSIX Bash` | Executable Script / Source | `357` | `1e0d9118c6` |
| `h_sudo.sh` | `POSIX Bash` | Executable Script / Source | `176` | `33464fd019` |
| `pre_push_engineering_guard.sh` | `POSIX Bash` | Executable Script / Source | `77` | `ac977c95b2` |
| `snapshot_homunculus_version.py` | `Python 3.10+` | Flags: `--slug`, `--label`, `--raid-root`, `--homunculus-dir`, `--engineering-dir`, `--version-manifest`, `--allow-dirty`, `--skip-benchmark`, `--force-fresh-benchmark`, `--list`, `--verify`, `--dry-run`, `--json` — Symbols: `sanitize_slug()` (`#L74-L77`), `find_latest_same_dev_raid_snapshot()` (`#L89-L114`), `find_verified_benchmark_receipt()` (`#L117-L151`), `copy_tree_cow()` (`#L176-L358`), `collect_symlink_manifest()` (`#L376-L394`), `build_restore_script()` (`#L477-L684`), `build_reconstruction_index()` (`#L687-L747`), `verify_existing_snapshot()` (`#L790-L802`), `main()` (`#L805-L1107`) | `1111` | `fc6af3c4a4` |
| `verified_fastpath.py` | `Python 3.10+` | Flags: `--record-memory-audit`, `--check-memory-audit`, `--record-vrf`, `--check`, `--targets`, `--sources`, `--receipt`, `--memory-root`, `--homunculus-root`, `--repo`, `--force-fresh`, `--json` — Symbols: `resolve_homunculus_root()` (`#L76-L114`), `resolve_cache_path()` (`#L122-L135`), `compute_memory_audit_fingerprint()` (`#L289-L343`), `record_memory_audit_fastpath()` (`#L346-L378`), `check_memory_audit_fastpath()` (`#L381-L429`), `record_vrf_fastpath()` (`#L473-L531`), `check_fastpath()` (`#L606-L717`), `main()` (`#L720-L801`) | `805` | `d048fd0598` |
| `version_manager.py` | `Python 3.10+` | Flags: `--homunculus-dir`, `--manifest`, `--status`, `--init-baseline`, `--sync-manifest`, `--bump`, `--reason`, `--allow-v1-public-release`, `--rollback`, `--dry-run`, `--json` — Symbols: `compute_content_tree_hash()` (`#L79-L105`), `get_git_state()` (`#L111-L160`), `load_or_create_manifest()` (`#L163-L200`), `resolve_effective_version_status()` (`#L203-L251`), `ensure_git_tag()` (`#L254-L277`), `bump_version()` (`#L280-L352`), `rollback_engine()` (`#L355-L414`), `main()` (`#L417-L556`) | `560` | `5908a68c2a` |
| `gmail_mcp/gmail_mcp_server.py` | `Python 3.10+` | Flags: `--status`, `--import-client-secret`, `--auth`, `--no-browser` — Symbols: `get_config_dir()` (`#L90-L94`), `get_attachment_jail_dir()` (`#L97-L127`), `ensure_secure_dir()` (`#L130-L137`), `verify_secret_file_security()` (`#L140-L156`), `write_secret_json()` (`#L159-L176`), `verify_token_scopes()` (`#L239-L249`), `build_gmail_web_urls()` (`#L473-L481`), `build_draft_payload()` (`#L484-L532`), `resolve_quarantined_attachment_path()` (`#L535-L567`), `main()` (`#L1028-L1045`) | `1049` | `6f37644530` |
<!-- AUTO-SOFTWARE-MODULES:END -->

---

## 2. Configuration Schemas & Data Contracts

<!-- AUTO-SOFTWARE-SCHEMAS:START -->
| Schema / Config File | Format | Top-Level Keys / Contract Version | SHA-256 Prefix |
| :--- | :--- | :--- | :--- |
| `homunculus_version.json` | `JSON` | `schema_version`, `engine_version`, `release_stage`, `public_release_target`, `baseline_tag`, `baseline_head_sha` | `c4bb60b57d` |
| `umbrella_configs/Home.homunculus.json` | `JSON` | `schema_version`, `homunculus_rel_path`, `memory_mode`, `memory_dir`, `study_briefs_dir`, `visual_studio` | `71ee5f6b66` |
| `umbrella_configs/Projects.homunculus.json` | `JSON` | `schema_version`, `homunculus_rel_path`, `memory_mode`, `memory_dir`, `study_briefs_dir`, `visual_studio` | `f2098fe12a` |
<!-- AUTO-SOFTWARE-SCHEMAS:END -->

---

## 3. Deterministic Test & Verification Receipts

<!-- AUTO-SOFTWARE-TESTS:START -->
| Test File | Test Classes | AST test_* Count | SHA-256 Prefix |
| :--- | :--- | :---: | :---: |
| *(No `test_*.py` suites indexed yet)* | — | `0` | — |

**Latest Verified Test Receipt (`2026-11-19`):** SBX-20261119_131004-66e81703 | SBX-20261119_131016-6a8ba167 | 14/14 hook + 31/31 MCP + 8/8 adapters + 5/5 data_safety + 6/6 foundation PASS | VRF-8d593526f4f2
<!-- AUTO-SOFTWARE-TESTS:END -->
