# Apprentice Sidecar — Portability & System Tuning Guide (`Living Reference`)

> **Purpose**: Portable hardware/model calibration manual packaged with the `apprentice` plugin so a receiving AI agent can profile, size, and safely govern *any* local LLM backend (`LM Studio`, `Ollama`, `llama.cpp`, or OpenAI-compatible loopback servers) across diverse GPU, Unified Memory, and CPU-only systems without repeating prior failure modes.

---

## 1. Pre-Tuning Hardware & Backend Discovery

Before choosing context lengths, parallelism, or effort budgets on a new machine, inspect the target host cleanly:

1. **Compute & Memory Envelope**:
   - **Discrete GPU (Linux ROCm/CUDA / Windows)**: Check dedicated VRAM free/total (Linux sysfs counters such as `/sys/class/drm/card1/device/mem_info_vram_used`, `/sys/class/drm/card1/device/mem_info_vram_total`, or `nvidia-smi`), shared system-RAM spill (`/sys/class/drm/card1/device/mem_info_gtt_used` — keep `< 0.5 GiB` under load to prevent PCIe bandwidth collapse), and whether a desktop compositor shares the GPU (reserve `>= 2.0 GiB` free VRAM if interactive UI runs on the same card; calibrate smaller reserves only on headless hosts `[TBD: headless_vram_reserve_gib]`).
   - **Unified Memory (Apple Silicon / AMD APU)**: Check total wired/free RAM (`sysctl hw.memsize` / `/proc/meminfo`) and set `contextLength` within empirically measured safe wired limits (`[TBD: target_unified_ctx_limit]`).
   - **CPU-Only / Hybrid MoE**: Identify physical cores vs SMT threads and NUMA/CCD topology (`lscpu`). Pin `--cpu-range` (`6-11` in `cpu-bg`) and `cpuThreads` (`8`–`10` for GPU+MoE offload, `6` CCD-pinned threads for `cpu-bg`) so OS/IDE responsiveness stays intact.
2. **Backend Capabilities Probe**:
   - Confirm whether the backend exposes **true loaded model state & active `context_length`** (`/api/v0/models` in LM Studio, `/api/ps` in Ollama) vs `/v1/models`-only (`llama.cpp` / generic OpenAI-compatible). Never trust `/v1/models` alone when anti-JIT protection is available, because unloaded auto-load can hang or spill onto CPU silently.
3. **Live Micro-Benchmark Calibration**:
   - Measure actual **prefill (`pp_tok_s`)** and **decode (`tg_tok_s`)** on a representative prompt/output sample (`[TBD: probe_prompt_tokens]`, `[TBD: probe_output_tokens]`) before trusting ETA breakers.
   - Verified baseline (`16 GiB` VRAM + Hybrid MoE `Qwen3.6-35B-A3B` `Q4_K_M`, `0.52`–`0.65` CPU expert ratio): `890.0 tok/s` prefill (`pp_tok_s`), `40.5`–`43.0 tok/s` decode (`tg_tok_s`) at `49,152`–`57,344` ctx (`--parallel 2`, `q8_0` KV cache). If your target hardware decodes slower (`[TBD: target_tg_tok_s]`), shrink chunk budgets (`target_chunk_bytes` / `max_tokens`) rather than breaching client MCP timeouts (`180s`).

---

## 2. Model-Behavior Rules (Validated Pitfalls to Never Repeat)

1. **Thinking Models (`<think>` / `reasoning_effort`) vs. Direct Instruct Models**:
   - **Never run daily `STANDARD` tasks with deep thinking enabled**: `STANDARD` (`reasoning_effort="none"`, `default_max_tokens=3072`) avoids `<think>` overhead, runs with `<= 2` concurrent async workers, and stays dramatically faster than serialized `HIGH` passes.
   - **Never starve `HIGH` reasoning below `8,192` output tokens**: Live A/B testing proved the legacy reduced output cap on `qwen3.6-35b-a3b` cross-file reduces caused `<think>` exhaustion (`reasoning_recovered: true`), forcing a recovery pass (`172.561`s vs `96.828`s with an `8,192` cap). On reasoning models, keep `HIGH` caps at `8192`–`10240`.
   - **Instruct-Only / Non-Thinking Models**: If porting to a model without hidden `<think>` traces, omit `reasoning_recovered` loops and tune `max_tokens` to observed output sizes (`[TBD: instruct_high_max_tokens]`).
2. **Do Not Chunk Cross-File Audits When Single-Shot Fits (`<= 55296` Bytes / `54 KB` on `49K` Context)**:
   - Live sandbox testing on `BOM.md` + `Assembly_Guide.md` + `Print_Settings.md` proved lossy Map summarization dropped `1` of `4` seeded defects in both legacy (`172.561`s) and `8192`-cap (`96.828`s) Map-Reduce runs, whereas Single-Shot `HIGH` (`8192` cap) caught `4` of `4` in `100.456`s (`100.0%` `verify_claims.py` backing), and chunking a `49,815 B` workload bloated unfiltered Map slices (`36,013 B`) into a `512.291`s Reduce timeout.
   - Reserve chunked Map-Reduce for genuinely oversized payloads (`> 55296` bytes on `49K` context, or `>= 5` slices across `>= 3` files), filter Map rows strictly to query-relevant facts (`max ~24` literal rows per slice: `Item/Rule | Exact Literal/Qty/Spec | Anchor`), keep `max_slices_per_batch=4` and `260`–`300`s Reduce timeouts, and serialize `HIGH` workers `1`-at-a-time FIFO (`acquire_bjob_worker_slot`) while allowing `<= 2` `STANDARD` workers inside free VRAM headroom (`< 0.5 GiB` GTT).
3. **Pair Fast CPU Truth Oracles With Async Semantic Second-Eyes Review (`apprentice_shadow_review`)**:
   - In sandbox testing, `verify_claims.py` ran in `177.9` ms and passed `100.0%` (`VRF-34908258799c`) on a draft repeating corrupted/contradictory repo text—whereas pairing CPU oracles with an async **`apprentice_shadow_review`** semantic critic (`71.22`s) caught the `[!CAUTION]` material violation and hardware mismatches before release.

---

## 3. Baseline Profile & Target Calibration Template

Fill `[TBD: ...]` slots empirically via `benchmark_apprentice.py` on each new host rather than copying another machine's hardware limits:

| Hardware Class | Model Class | Context / `--parallel` | `STANDARD` Budget | `HIGH` Reduce Budget | Chunk Threshold / Max Batch |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **`16 GiB` VRAM + Hybrid MoE** *(Verified Baseline)* | `Qwen3.6-35B-A3B` `Q4_K_M` (`0.52`–`0.65` CPU split) | `49152` (`gpu-daily`) / `57344` (`gpu-max`), `--parallel 2`, `q8_0` | `3072` tok (`none`) | `8192`–`10240` tok (`1` FIFO slot) | `55296` B (`54 KB`) / `4` slices |
| **Lower-VRAM GPU (`<= 12 GiB`)** *(Target Template)* | `[TBD: small_dense_model]` | `[TBD: low_vram_ctx]`, `--parallel 1`, `q8_0` | `[TBD: low_vram_std_tok]` | `[TBD: low_vram_high_tok]` (`1` FIFO slot) | `[TBD: low_vram_chunk_bytes]` / `[TBD: low_vram_batch]` |
| **High-VRAM Dedicated (`>= 24 GiB`)** *(Target Template)* | `[TBD: high_vram_model]` | `[TBD: high_vram_ctx]`, `[TBD: high_vram_parallel]` | `[TBD: high_vram_std_tok]` | `[TBD: high_vram_high_tok]` | `[TBD: high_vram_chunk_bytes]` / `[TBD: high_vram_batch]` |
| **Apple Unified Memory** *(Target Template)* | `[TBD: apple_mlx_or_gguf]` | `[TBD: apple_safe_ctx]` | `[TBD: apple_std_tok]` | `[TBD: apple_high_tok]` | `[TBD: apple_chunk_bytes]` / `[TBD: apple_batch]` |
| **`CPU-Background`** *(Verified Co-Work Profile)* | `Qwen3.6-35B-A3B` (`--device none`, `--cpu-range 6-11`) | `16384` ctx, `cpuThreads=6` | `800` tok (`none`) | Disabled (`98.0 tok/s` pp, `17.4 tok/s` tg) | `prompt_cap=8192` tok |

---

## 4. Portability Checklist for Installing Into a New Ecosystem

1. **Parameterize Environment Overrides**: Configure `APPRENTICE_API_URL`, `APPRENTICE_TELEMETRY_LOG`, `APPRENTICE_SCORECARD_PATH`, `APPRENTICE_JOBS_DIR`, `HOMUNCULUS_ROOT`, and `HOMUNCULUS_MEMORY_ROOT` cleanly instead of hardcoding developer usernames or home directories.
2. **Validate Strict Plugin Integrity**: Run `agy plugin validate <plugin_dir> --strict --json`, `apprentice_engine.py --self-test --json`, `apprentice_mcp_server.py --self-test --json`, and `benchmark_apprentice.py --mode all` on the target box before enabling `effort="auto"`.
3. **Preserve Telemetry Epochs**: When changing hardware profiles, models, or prompt versions on a new host, start a clean scorecard epoch via `apprentice_control(action="scorecard-reset", epoch_label="<host-profile>", user_confirmed=True)` so usable/corrected rates track real behavior cleanly.
