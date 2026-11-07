---
name: engineering-sandbox
description: Use this skill whenever validating scripts, parsers, validators, data-mutating code, rules, skills, or multi-file repository workflows in an isolated sandbox before marking work complete. Orchestrates Cross-OS Copy-on-Write OS Dry-Run benches alongside Blind-Light (Flash/Haiku), Blind-Full (Pro/Opus), Visible-Light (Flash), Visible-Full (Pro), Compare-Light, and Compare-Full subagent frames with optional +faults adversarial injection and token-lean diagnostic telemetry.
---

# Engineering Sandbox & Adversarial Fault Bench (`engineering-sandbox`)

This skill governs isolated verification of Track-2 deliverables (parsers, validators, data-mutating scripts, rules, and skills) via [`sandbox_runner.py`](scripts/sandbox_runner.py) under **`1. Accuracy & Truth -> 2. Efficiency -> 3. Data Safety -> 4. Speed`**.

---

## 1. Pre-Flight Foundation Checks

1. **Track 1 vs. Track 2 Classification**:
   - **Track 1 (Exempt)**: Read-only research scouts and read-only CLI telemetry runs launch immediately without sandbox gating.
   - **Track 2 (Mandatory Sandbox Gate)**: Any new or modified validator, parser, data-mutating script, rule, or skill must pass a sandbox gate before promotion from `[SANDBOX-PENDING]` to `[SOLVED]`.
2. **Cross-OS Isolation Backend Detection (`Windows, macOS & Linux`)**:
   - **Linux (`bwrap` + CoW)**: `bwrap` (`Bubblewrap`) read-only rootfs bind + Btrfs/XFS `--reflink=auto` Copy-on-Write scratch workspace + `--unshare-pid` + pre/post host SHA-256 verification.
   - **macOS (APFS CoW)**: APFS `cp -c` Copy-on-Write clone (or isolated temp clone) inside an isolated temporary workspace + `HOME`/`TMPDIR` redirection + pre/post host SHA-256 verification.
   - **Windows / Fallback POSIX (Isolated Tempfile Workspace)**: Isolated `tempfile` workspace tree clone + environment containment + pre/post host SHA-256 verification (`Live Host Mutations: 0`).
3. **Manual Subagent Sandbox Trigger Gate**:
   - Run deterministic `OS Dry-Run` (`--mode dry-run`) automatically or on request, but **ask user permission** before launching multi-turn `Blind`, `Visible`, or `Compare` subagent frames to avoid premature token burn while edits are still in flight.

---

## 2. Step-Level Verification Gates (`sandbox_runner.py` CLI)

### Gate 0 — Pre-Sandbox `Directory/` & `AUTO-TREE` Freshness (`--prepare`)
`sandbox_runner.py` automatically runs the `~1.7ms` structural freshness guard (`homunculus_paths.ensure_directory_fresh`) *before* taking `host_pre` SHA-256 baselines (`Live Host Mutations: 0`). Before spawning multi-turn `Blind`, `Visible`, or `Compare-*` subagent frames after uncommitted mid-session file creations/renames, run:

```bash
python3 <HOMUNCULUS_ROOT>/skills/engineering-sandbox/scripts/sandbox_runner.py --prepare --target-dir .
```

### Gate 1 — Deterministic OS Dry-Run + Adversarial `+faults` Injection
Execute positive controls (`--cmd` or `--spec` `controls`) and adversarial fault-injection cases (`--fault-case "<setup> :: <validator>"` or `--spec` `faults` + `--faults`) inside an isolated CoW workspace:

```bash
python3 <HOMUNCULUS_ROOT>/skills/engineering-sandbox/scripts/sandbox_runner.py \
  --mode dry-run \
  --target-dir . \
  --spec /path/to/sandbox_spec.json \
  --faults
```

### Gate 2 — Subagent Sandbox Frames (`Blind`, `Visible`, `Compare`)
When the user approves a subagent sandbox frame (`Blind-Light`, `Blind-Full`, `Visible-Light`, `Visible-Full`, `Compare-Light`, `Compare-Full`), run the isolated CoW bench or differential A/B comparison (`--workspace` and `--keep-failed-cow` are also supported as aliases for `--target-dir` and `--keep-overlay`):

```bash
python3 <HOMUNCULUS_ROOT>/skills/engineering-sandbox/scripts/sandbox_runner.py \
  --mode blind-light \
  --target-dir . \
  --spec /path/to/sandbox_spec.json \
  --faults \
  --keep-overlay
```

### Gate 3 — Verify `SBX-<timestamp>-<hash>` Receipt & Zero Host Mutation
Confirm the diagnostic summary reports:
- `Status: PASS`
- `Controls: N/N passed`
- `+faults: M/M caught` (when validating a checker/validator)
- `Live Host Mutations: 0`
- Valid `SBX-<timestamp>-<8hex>` receipt and forensic bundle (`report.json`, `mutations.diff`, `stdout.log`, `stderr.log`).

---

## 3. Stop & Escalation Conditions

- **`[HOST MUTATION DETECTED — CRITICAL FAIL]`**: If `sandbox_runner.py` detects any pre- vs. post-run SHA-256 drift in the live workspace, halt immediately and inspect the offending command.
- **Uncaught Fault (`FAULT_ESCAPED`)**: If a validator exits `0` on an injected `+faults` case (or catches the wrong error code), halt and fix the validator's detection logic before promoting to `[SOLVED]`.
