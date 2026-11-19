---
project: "Apprentice"
entity: "Alchemical-3D"
compartment: "public"
telemetry_domain: "software"
local_path: "../../Alchemical3D/Apprentice"
inventory_sha256: "e0fee62ec424"
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
| `apprentice/backends.py` | `Python 3.10+` | Symbols: `ModelProfile()` (`#L48-L67`), `resolve_cache_dir()` (`#L70-L79`), `http_json()` (`#L108-L138`), `parse_param_billions()` (`#L141-L146`), `classify_capability_tier()` (`#L149-L175`), `discover_backend()` (`#L264-L390`), `update_profile_ema()` (`#L393-L428`), `chat_completion()` (`#L431-L500`), `calibrate_profile()` (`#L503-L520`), `run_lifecycle_action()` (`#L523-L559`) | `559` | `2973178015` |
| `apprentice/core.py` | `Python 3.10+` | Symbols: `run_read()` (`#L230-L328`), `run_draft()` (`#L436-L475`), `run_review()` (`#L594-L639`), `run_runtime()` (`#L642-L689`) | `689` | `774b2d5ab2` |
| `apprentice/grounding.py` | `Python 3.10+` | Symbols: `parse_structured_response()` (`#L35-L70`), `verify_grounded_items()` (`#L148-L259`), `extract_fenced_code()` (`#L262-L267`), `validate_staged_file()` (`#L270-L339`), `run_deterministic_review_checks()` (`#L356-L432`) | `432` | `d78be7e4b1` |
| `apprentice/hook.py` | `Python 3.10+` | Symbols: `evaluate_hook_event()` (`#L74-L141`), `run_hook_cli()` (`#L144-L154`) | `154` | `8762325b83` |
| `apprentice/mcp_stdio.py` | `Python 3.10+` | Symbols: `dispatch_tool_call()` (`#L116-L156`), `handle_jsonrpc_message()` (`#L159-L213`), `serve_stdio()` (`#L216-L263`) | `263` | `d47add9287` |
| `apprentice/planner.py` | `Python 3.10+` | Symbols: `ContextChunk()` (`#L27-L35`), `ExecutionPlan()` (`#L39-L52`), `estimate_tokens()` (`#L55-L60`), `compute_context_budgets()` (`#L63-L79`), `format_line_numbered_block()` (`#L82-L110`), `capture_git_diff()` (`#L113-L145`), `build_execution_plan()` (`#L148-L334`) | `334` | `78938765aa` |
| `apprentice/safety.py` | `Python 3.10+` | Symbols: `SafetyFirewallError()` (`#L52-L53`), `validate_loopback_url()` (`#L56-L69`), `is_path_within()` (`#L72-L78`), `load_forbidden_segments()` (`#L81-L107`), `inspect_path_security()` (`#L110-L144`), `parse_context_spec()` (`#L147-L157`), `resolve_context_items()` (`#L160-L192`), `resolve_staging_dir()` (`#L195-L223`), `safe_subprocess_cwd()` (`#L226-L235`) | `235` | `c0ca968566` |
| `apprentice/sprint.py` | `Python 3.10+` | Symbols: `SprintJob()` (`#L27-L36`), `SprintManager()` (`#L39-L145`), `get_sprint_manager()` (`#L151-L152`), `record_telemetry_event()` (`#L159-L171`), `summarize_goal_metrics()` (`#L174-L230`), `format_ledger_status_line()` (`#L233-L246`) | `246` | `91c4c6e018` |
| `scripts/stress_test_v3.py` | `Python 3.10+` | Symbols: `main()` (`#L23-L123`) | `127` | `22d270b313` |
| `tests/test_backends_and_planner.py` | `Python 3.10+` | Symbols: `TestBackendsAndPlanner()` (`#L101-L198`) | `202` | `ff8291d04f` |
| `tests/test_grounding.py` | `Python 3.10+` | Symbols: `TestGroundingAndOracles()` (`#L16-L93`) | `97` | `da8831d93b` |
| `tests/test_mcp_and_hook.py` | `Python 3.10+` | Symbols: `TestMcpAndHook()` (`#L18-L132`) | `136` | `fa25009b56` |
| `tests/test_safety.py` | `Python 3.10+` | Symbols: `TestSafetyFirewalls()` (`#L20-L95`) | `99` | `a8d52bde9a` |
| `tests/test_sprint_and_core.py` | `Python 3.10+` | Symbols: `TestSprintAndCore()` (`#L127-L202`) | `206` | `ea9ad0902a` |
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
| `tests/test_backends_and_planner.py` | `_MockBackendServer`, `TestBackendsAndPlanner` | `4` | `ff8291d04f` |
| `tests/test_grounding.py` | `TestGroundingAndOracles` | `3` | `da8831d93b` |
| `tests/test_mcp_and_hook.py` | `TestMcpAndHook` | `5` | `fa25009b56` |
| `tests/test_safety.py` | `TestSafetyFirewalls` | `5` | `a8d52bde9a` |
| `tests/test_sprint_and_core.py` | `_EndToEndMockLLM`, `TestSprintAndCore` | `3` | `ea9ad0902a` |
<!-- AUTO-SOFTWARE-TESTS:END -->
