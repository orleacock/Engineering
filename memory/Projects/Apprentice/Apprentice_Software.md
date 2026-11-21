---
project: "Apprentice"
entity: "Alchemical-3D"
compartment: "public"
telemetry_domain: "software"
local_path: "../../Alchemical3D/Apprentice"
inventory_sha256: "07bfb5e06448"
last_synced: "2026-11-20"
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
| `apprentice/__main__.py` | `Python 3.10+` | Flags: `--api-url`, `--task`, `--file`, `--repo`, `--include-git-diff`, `--deep`, `--target-file`, `--prompt`, `--context-file`, `--staging-dir`, `--smoke-cmd`, `--no-git-diff`, `--focus` — Symbols: `build_parser()` (`#L14-L55`), `main()` (`#L82-L128`) | `132` | `ddfcdbe36b` |
| `apprentice/backends.py` | `Python 3.10+` | Symbols: `ModelProfile()` (`#L49-L75`), `get_effective_slots()` (`#L78-L88`), `resolve_cache_dir()` (`#L91-L100`), `http_json()` (`#L129-L159`), `parse_param_billions()` (`#L162-L167`), `classify_capability_tier()` (`#L170-L194`), `discover_backend()` (`#L283-L380`), `update_profile_ema()` (`#L403-L472`), `record_profile_timeout()` (`#L475-L508`), `chat_completion()` (`#L511-L579`), `calibrate_profile()` (`#L582-L604`), `run_lifecycle_action()` (`#L607-L643`) | `643` | `14e3cf6976` |
| `apprentice/core.py` | `Python 3.10+` | Symbols: `run_read()` (`#L333-L461`), `run_draft()` (`#L572-L603`), `run_review()` (`#L711-L747`), `run_runtime()` (`#L750-L785`) | `785` | `4384f67554` |
| `apprentice/grounding.py` | `Python 3.10+` | Symbols: `parse_structured_response()` (`#L35-L70`), `verify_grounded_items()` (`#L155-L269`), `extract_fenced_code()` (`#L272-L281`), `validate_staged_file()` (`#L284-L355`), `run_deterministic_review_checks()` (`#L372-L448`) | `448` | `a6c932269e` |
| `apprentice/hook.py` | `Python 3.10+` | Symbols: `scan_transcript_delta()` (`#L136-L234`), `evaluate_hook_event()` (`#L251-L431`), `run_hook_cli()` (`#L434-L443`) | `443` | `c2a9c7e3fc` |
| `apprentice/mcp_stdio.py` | `Python 3.10+` | Symbols: `dispatch_tool_call()` (`#L119-L159`), `handle_jsonrpc_message()` (`#L162-L216`), `serve_stdio()` (`#L237-L287`) | `287` | `a6fa02204b` |
| `apprentice/planner.py` | `Python 3.10+` | Symbols: `ContextChunk()` (`#L29-L38`), `ExecutionPlan()` (`#L42-L55`), `estimate_tokens()` (`#L58-L63`), `compute_context_budgets()` (`#L66-L81`), `compute_effective_chunk_cap()` (`#L84-L120`), `format_line_numbered_block()` (`#L123-L151`), `discover_changed_files()` (`#L154-L179`), `capture_git_diff()` (`#L182-L219`), `format_diff_with_real_lines()` (`#L222-L254`), `build_execution_plan()` (`#L257-L410`) | `410` | `39689bfe58` |
| `apprentice/safety.py` | `Python 3.10+` | Symbols: `SafetyFirewallError()` (`#L52-L53`), `validate_loopback_url()` (`#L56-L69`), `is_path_within()` (`#L72-L78`), `load_forbidden_segments()` (`#L81-L107`), `inspect_path_security()` (`#L110-L144`), `parse_context_spec()` (`#L147-L157`), `resolve_context_items()` (`#L160-L192`), `resolve_staging_dir()` (`#L195-L223`), `safe_subprocess_cwd()` (`#L226-L235`) | `235` | `c0ca968566` |
| `apprentice/sprint.py` | `Python 3.10+` | Symbols: `SprintJob()` (`#L29-L39`), `read_live_active_jobs()` (`#L46-L72`), `SprintManager()` (`#L75-L427`), `get_sprint_manager()` (`#L433-L434`), `parse_utc_iso()` (`#L441-L446`), `record_telemetry_event()` (`#L449-L458`), `summarize_goal_metrics()` (`#L461-L529`), `format_ledger_status_line()` (`#L532-L552`) | `552` | `bc0276dcb5` |
| `tests/test_backends_and_planner.py` | `Python 3.10+` | Symbols: `TestBackendsAndPlanner()` (`#L112-L301`) | `305` | `6f380d28a9` |
| `tests/test_grounding.py` | `Python 3.10+` | Symbols: `TestGroundingAndOracles()` (`#L16-L159`) | `163` | `712d571ff0` |
| `tests/test_mcp_and_hook.py` | `Python 3.10+` | Symbols: `TestMcpAndHook()` (`#L23-L411`) | `415` | `9e698e1e03` |
| `tests/test_safety.py` | `Python 3.10+` | Symbols: `TestSafetyFirewalls()` (`#L20-L95`) | `99` | `a8d52bde9a` |
| `tests/test_sprint_and_core.py` | `Python 3.10+` | Symbols: `TestSprintAndCore()` (`#L127-L555`) | `559` | `2729937b6c` |
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
| `tests/test_backends_and_planner.py` | `_MockBackendServer`, `TestBackendsAndPlanner` | `7` | `6f380d28a9` |
| `tests/test_grounding.py` | `TestGroundingAndOracles` | `5` | `712d571ff0` |
| `tests/test_mcp_and_hook.py` | `TestMcpAndHook` | `7` | `9e698e1e03` |
| `tests/test_safety.py` | `TestSafetyFirewalls` | `5` | `a8d52bde9a` |
| `tests/test_sprint_and_core.py` | `_EndToEndMockLLM`, `TestSprintAndCore` | `9` | `2729937b6c` |
<!-- AUTO-SOFTWARE-TESTS:END -->
