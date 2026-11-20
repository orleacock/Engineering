---
project: "Apprentice"
entity: "Alchemical-3D"
compartment: "public"
telemetry_domain: "software"
local_path: "../../Alchemical3D/Apprentice"
inventory_sha256: "ee674cca0517"
last_synced: "2026-11-19"
---

# Apprentice — Software, CLI & Schema Telemetry (`_Software.md`)

> **Authoritative Software Truth Ledger (`sync_software_telemetry`)**: Populated via `sync_memory.py --sync-software --project Apprentice`. Used by `verify_claims.py` as primary software/CLI/schema ground truth for `Apprentice` (`entity: Alchemical-3D`).

---

## 1. Runtime Entrypoints & Module Inventory

<!-- AUTO-SOFTWARE-MODULES:START -->
| Script / Module Path | Language / Runtime | CLI Flags / Public Symbols | Line Count | SHA-256 Prefix |
| :--- | :--- | :--- | :--- | :--- |
| `install.ps1` | `PowerShell` | Executable Script / Source | `41` | `e6e24a758e` |
| `install.sh` | `POSIX Bash` | Executable Script / Source | `47` | `329ff63a6b` |
| `apprentice/__init__.py` | `Python 3.10+` | Module | `6` | `90260c25fb` |
| `apprentice/__main__.py` | `Python 3.10+` | Flags: `--api-url`, `--task`, `--file`, `--repo`, `--include-git-diff`, `--deep`, `--target-file`, `--prompt`, `--context-file`, `--staging-dir`, `--smoke-cmd`, `--no-git-diff`, `--focus` — Symbols: `build_parser()` (`#L14-L55`), `main()` (`#L58-L103`) | `107` | `df5a209248` |
| `apprentice/backends.py` | `Python 3.10+` | Symbols: `ModelProfile()` (`#L49-L75`), `get_effective_slots()` (`#L78-L88`), `resolve_cache_dir()` (`#L91-L100`), `http_json()` (`#L129-L159`), `parse_param_billions()` (`#L162-L167`), `classify_capability_tier()` (`#L170-L194`), `discover_backend()` (`#L283-L378`), `update_profile_ema()` (`#L401-L461`), `record_profile_timeout()` (`#L464-L497`), `chat_completion()` (`#L500-L568`), `calibrate_profile()` (`#L571-L592`), `run_lifecycle_action()` (`#L595-L631`) | `631` | `a8bb1e7563` |
| `apprentice/core.py` | `Python 3.10+` | Symbols: `run_read()` (`#L319-L446`), `run_draft()` (`#L554-L585`), `run_review()` (`#L688-L724`), `run_runtime()` (`#L727-L762`) | `762` | `430fe90892` |
| `apprentice/grounding.py` | `Python 3.10+` | Symbols: `parse_structured_response()` (`#L35-L70`), `verify_grounded_items()` (`#L151-L265`), `extract_fenced_code()` (`#L268-L273`), `validate_staged_file()` (`#L276-L345`), `run_deterministic_review_checks()` (`#L362-L438`) | `438` | `a9b8d26066` |
| `apprentice/hook.py` | `Python 3.10+` | Symbols: `scan_transcript_delta()` (`#L84-L168`), `evaluate_hook_event()` (`#L185-L309`), `run_hook_cli()` (`#L312-L322`) | `322` | `4edacc3def` |
| `apprentice/mcp_stdio.py` | `Python 3.10+` | Symbols: `dispatch_tool_call()` (`#L116-L156`), `handle_jsonrpc_message()` (`#L159-L213`), `serve_stdio()` (`#L216-L263`) | `263` | `d47add9287` |
| `apprentice/planner.py` | `Python 3.10+` | Symbols: `ContextChunk()` (`#L29-L38`), `ExecutionPlan()` (`#L42-L55`), `estimate_tokens()` (`#L58-L63`), `compute_context_budgets()` (`#L66-L81`), `compute_effective_chunk_cap()` (`#L84-L104`), `format_line_numbered_block()` (`#L107-L135`), `discover_changed_files()` (`#L138-L163`), `capture_git_diff()` (`#L166-L203`), `format_diff_with_real_lines()` (`#L206-L238`), `build_execution_plan()` (`#L241-L392`) | `392` | `a5f7b19bab` |
| `apprentice/safety.py` | `Python 3.10+` | Symbols: `SafetyFirewallError()` (`#L52-L53`), `validate_loopback_url()` (`#L56-L69`), `is_path_within()` (`#L72-L78`), `load_forbidden_segments()` (`#L81-L107`), `inspect_path_security()` (`#L110-L144`), `parse_context_spec()` (`#L147-L157`), `resolve_context_items()` (`#L160-L192`), `resolve_staging_dir()` (`#L195-L223`), `safe_subprocess_cwd()` (`#L226-L235`) | `235` | `c0ca968566` |
| `apprentice/sprint.py` | `Python 3.10+` | Symbols: `SprintJob()` (`#L28-L38`), `read_live_active_jobs()` (`#L45-L71`), `SprintManager()` (`#L74-L226`), `get_sprint_manager()` (`#L232-L233`), `parse_utc_iso()` (`#L240-L245`), `record_telemetry_event()` (`#L248-L261`), `summarize_goal_metrics()` (`#L264-L339`), `format_ledger_status_line()` (`#L342-L364`) | `364` | `d6944df36c` |
| `scripts/stress_test_v3.py` | `Python 3.10+` | Symbols: `main()` (`#L23-L123`) | `127` | `22d270b313` |
| `tests/test_backends_and_planner.py` | `Python 3.10+` | Symbols: `TestBackendsAndPlanner()` (`#L111-L261`) | `265` | `da593b5ef1` |
| `tests/test_grounding.py` | `Python 3.10+` | Symbols: `TestGroundingAndOracles()` (`#L16-L118`) | `122` | `c68d5cf749` |
| `tests/test_mcp_and_hook.py` | `Python 3.10+` | Symbols: `TestMcpAndHook()` (`#L18-L210`) | `214` | `5deb33d0bf` |
| `tests/test_safety.py` | `Python 3.10+` | Symbols: `TestSafetyFirewalls()` (`#L20-L95`) | `99` | `a8d52bde9a` |
| `tests/test_sprint_and_core.py` | `Python 3.10+` | Symbols: `TestSprintAndCore()` (`#L127-L253`) | `257` | `0d9b247355` |
<!-- AUTO-SOFTWARE-MODULES:END -->

---

## 2. Configuration Schemas & Data Contracts

<!-- AUTO-SOFTWARE-SCHEMAS:START -->
| Schema / Config File | Format | Top-Level Keys / Contract Version | SHA-256 Prefix |
| :--- | :--- | :--- | :--- |
| `plugin/plugin.json` | `JSON` | `name`, `version`, `author`, `homepage`, `repository` | `4c7c598a6f` |
<!-- AUTO-SOFTWARE-SCHEMAS:END -->

---

## 3. Deterministic Test & Verification Receipts

<!-- AUTO-SOFTWARE-TESTS:START -->
| Test File | Test Classes | AST test_* Count | SHA-256 Prefix |
| :--- | :--- | :---: | :---: |
| `tests/test_backends_and_planner.py` | `_MockBackendServer`, `TestBackendsAndPlanner` | `6` | `da593b5ef1` |
| `tests/test_grounding.py` | `TestGroundingAndOracles` | `4` | `c68d5cf749` |
| `tests/test_mcp_and_hook.py` | `TestMcpAndHook` | `6` | `5deb33d0bf` |
| `tests/test_safety.py` | `TestSafetyFirewalls` | `5` | `a8d52bde9a` |
| `tests/test_sprint_and_core.py` | `_EndToEndMockLLM`, `TestSprintAndCore` | `4` | `0d9b247355` |
<!-- AUTO-SOFTWARE-TESTS:END -->
