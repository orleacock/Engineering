---
project: "Workstation_Operations"
entity: "Orin_Workstation"
compartment: "private"
telemetry_domain: "software"
local_path: "../scripts"
inventory_sha256: "f247dad00a36"
last_synced: "2026-11-10"
---

# Workstation_Operations — Software, CLI & Schema Telemetry (`_Software.md`)

> **Authoritative Software Truth Ledger (`sync_software_telemetry`)**: Populated via `sync_memory.py --sync-software --project Workstation_Operations`. Used by `verify_claims.py` as primary software/CLI/schema ground truth for `Workstation_Operations` (`entity: Orin_Workstation`).

---

## 1. Runtime Entrypoints & Module Inventory

<!-- AUTO-SOFTWARE-MODULES:START -->
| Script / Module Path | Language / Runtime | CLI Flags / Public Symbols | Line Count | SHA-256 Prefix |
| :--- | :--- | :--- | :--- | :--- |
| `benchmark_homunculus.py` | `Python 3.10+` | Flags: `--profile`, `--homunculus-dir`, `--memory-root`, `--version-manifest`, `--history-jsonl`, `--ledger-md`, `--baseline-version`, `--record-baseline`, `--append-ledger`, `--history-only`, `--output-md`, `--label`, `--transcript`, `--deliverable-dir`, `--sources`, `--self-test`, `--inject-synthetic-regression`, `--json` — Symbols: `MetricRow()` (`#L86-L103`), `percentile()` (`#L106-L118`), `snapshot_host_hashes()` (`#L121-L144`), `run_cmd_timed()` (`#L147-L170`), `probe_bwrap_erofs()` (`#L173-L208`), `build_universal_spine()` (`#L1795-L1838`), `render_regression_autopsy_md()` (`#L1981-L2069`), `render_markdown_report()` (`#L2093-L2128`), `main()` (`#L2230-L2425`) | `2429` | `aba02e07ae` |
| `bootstrap_workstation.sh` | `POSIX Bash` | Executable Script / Source | `231` | `69f6ab0862` |
| `git_pre_commit_boundary.sh` | `POSIX Bash` | Executable Script / Source | `227` | `199c8189b5` |
| `pre_push_engineering_guard.sh` | `POSIX Bash` | Executable Script / Source | `80` | `60e13724e7` |
| `snapshot_homunculus_version.py` | `Python 3.10+` | Flags: `--slug`, `--raid-root`, `--homunculus-dir`, `--engineering-dir`, `--version-manifest`, `--allow-dirty`, `--skip-benchmark`, `--list`, `--verify`, `--dry-run`, `--json` — Symbols: `sanitize_slug()` (`#L72-L75`), `copy_tree_cow()` (`#L78-L108`), `collect_symlink_manifest()` (`#L126-L144`), `stage_client_wiring()` (`#L147-L186`), `create_git_bundles()` (`#L189-L231`), `build_restore_script()` (`#L234-L424`), `build_reconstruction_index()` (`#L427-L487`), `compute_sha256sums()` (`#L490-L502`), `lock_deliverable_readonly()` (`#L505-L527`), `verify_existing_snapshot()` (`#L530-L542`), `main()` (`#L545-L798`) | `802` | `9b133aeb0a` |
| `version_manager.py` | `Python 3.10+` | Flags: `--homunculus-dir`, `--manifest`, `--status`, `--init-baseline`, `--sync-manifest`, `--bump`, `--reason`, `--allow-v1-public-release`, `--rollback`, `--dry-run`, `--json` — Symbols: `compute_engine_tree_hash()` (`#L79-L105`), `get_git_state()` (`#L108-L157`), `load_or_create_manifest()` (`#L160-L197`), `resolve_effective_version_status()` (`#L200-L245`), `ensure_git_tag()` (`#L248-L271`), `bump_version()` (`#L274-L346`), `rollback_engine()` (`#L349-L408`), `main()` (`#L411-L550`) | `554` | `66d498b5fb` |
| `gmail_mcp/gmail_mcp_server.py` | `Python 3.10+` | Flags: `--status`, `--import-client-secret`, `--auth`, `--no-browser` — Symbols: `get_config_dir()` (`#L90-L94`), `get_attachment_jail_dir()` (`#L97-L127`), `ensure_secure_dir()` (`#L130-L137`), `verify_secret_file_security()` (`#L140-L156`), `write_secret_json()` (`#L159-L176`), `verify_token_scopes()` (`#L239-L249`), `build_gmail_web_urls()` (`#L473-L481`), `build_draft_payload()` (`#L484-L532`), `resolve_quarantined_attachment_path()` (`#L535-L567`), `main()` (`#L1028-L1045`) | `1049` | `6f37644530` |
<!-- AUTO-SOFTWARE-MODULES:END -->

---

## 2. Configuration Schemas & Data Contracts

<!-- AUTO-SOFTWARE-SCHEMAS:START -->
| Schema / Config File | Format | Top-Level Keys / Contract Version | SHA-256 Prefix |
| :--- | :--- | :--- | :--- |
| `homunculus_version.json` | `JSON` | `schema_version`, `engine_version`, `release_stage`, `public_release_target`, `baseline_tag`, `baseline_head_sha` | `d7bb92210b` |
| `umbrella_configs/Projects.homunculus.json` | `JSON` | `schema_version`, `homunculus_rel_path`, `memory_mode`, `memory_dir`, `study_briefs_dir`, `visual_studio` | `f2098fe12a` |
<!-- AUTO-SOFTWARE-SCHEMAS:END -->

---

## 3. Deterministic Test & Verification Receipts

| Test Suite / Gate | Command | Last Verified Result | Receipt / Anchor |
| :--- | :--- | :--- | :--- |
| Unit Test Suite | `python3 -m unittest discover -s tests -v` | `[TBD: test_status]` | `[TBD: receipt_id]` |
