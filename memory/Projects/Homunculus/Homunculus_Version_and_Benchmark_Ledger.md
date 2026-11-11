---
title: "Homunculus Version & Standardized Benchmark Ledger"
project: "Homunculus"
entity: "Alchemical-3D"
compartment: "private"
note_type: "reference"
authoritative: false
status: "NON_AUTHORITATIVE_REFERENCE"
last_synced: "2026-11-11"
---

# 📊 Homunculus Version & Standardized Benchmark Ledger (`v0.Y.Z`)

Part of the [`README.md`](../../README.md) and companion version scorecard for [`Homunculus`](Homunculus.md).

> [!IMPORTANT]
> **NON-AUTHORITATIVE HISTORICAL BENCHMARK LEDGER (`authoritative: false` — DO NOT CITE AS LIVE SPEC)**: Tracks standardized 4-Pillar Spine + Subsystem Profile scorecards across `v0.Y.Z` pre-release development toward the `v1.0.0` public GitHub release (`1. Accuracy & Truth > 2. Efficiency > 3. Data Safety > 4. Speed`). Auto-excluded from `verify_claims.py` `--sources` so historical benchmark figures never pollute live repository verification. Pure Markdown charts only (`Requirement 2A` — graphics generated only on explicit request or system release).

## 1. Version Digit Trigger Laws (`Requirement 4B`)

- **Major (`X.0.0`)**: `0.Y.Z -> 1.0.0` reserved strictly for public GitHub release (`--allow-v1-public-release`).
- **Minor (`0.Y.0`)**: Major architectural overhauls, multi-sprint subsystem builds, new skills/add-ons/adapters, or schema expansions (resets `Z` to `0`; requires `full-system-suite` + RAID deliverable snapshot).
- **Patch (`0.y.Z`)**: Bug fixes, validator FP/FN closures, regex refinements, prose trims, or latency/test updates without schema changes.
- **Candidate (`0.y.z-dev+<tree8>`)**: Automatic uncommitted development tree identifier.

---

## 2. Recorded Version Baselines & Benchmark Runs

### Standardized Benchmark Run: `full-system-suite` (`v0.1.0` vs. Baseline `v0.1.0`) — v0.1.0 Consolidated Foundation Baseline

- **Run ID & Timestamp**: `BMK-20261110_114446-d01a3e92` (`2026-11-10T11:44:46-06:00`)
- **Engine Provenance**: `/home/orin/Projects/Alchemical3D/Homunculus` | Version: `v0.1.0` | `HEAD`: `31aa0cb0a918` | `Tree`: `284d5a57b3c2` (`102` files, `clean`)
- **Overall Verdict**: **`BASELINE_PINNED`** (`Hard Blocks: 0` | `Advisories: 0` | `Wall-Clock: 28.44s`)

#### Part A — Universal 4-Pillar Spine (`12` Locked Metrics)

| # | Pillar | Standardized Metric | Baseline (`v0.1.0`) | Previous Run | Candidate (`v0.1.0`) | Delta (vs. Baseline) | Ceiling / Target | Status |
| :---: | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :---: |
| `1` | `Meta` | **Version & Tree Provenance** | `v0.1.0 (31aa0cb0 / 284d5a57)` | `— (initial)` | `v0.1.0 (31aa0cb0 / 284d5a57)` | `0 (baseline)` | `Clean or -dev+<tree8>` | **`PINNED`** |
| `2` | `#1 Accuracy` | **Positive Controls Pass Rate** | `17 / 17 (100.0%)` | `— (initial)` | `17 / 17 (100.0%)` | `0 (baseline)` | `100.0%` | **`PINNED`** |
| `3` | `#1 Accuracy` | **Adversarial +faults Catch Rate** | `14 / 14 (100.0%)` | `— (initial)` | `14 / 14 (100.0%)` | `0 (baseline)` | `100.0%` | **`PINNED`** |
| `4` | `#1 Accuracy` | **False Positives / False Negatives** | `FP: 0 / FN: 0` | `— (initial)` | `FP: 0 / FN: 0` | `0 (baseline)` | `FP: 0 / FN: 0` | **`PINNED`** |
| `5` | `#1 Accuracy` | **Automated Unit Test Suite** | `46 / 46 (100.0%)` | `— (initial)` | `46 / 46 (100.0%)` | `0 (baseline)` | `100.0%` | **`PINNED`** |
| `6` | `#2 Efficiency` | **Always-On 3-Rule Footprint** | `20,459 B / 2548 w (~3440 tok)` | `— (initial)` | `20,459 B / 2548 w (~3440 tok)` | `0 (baseline)` | `<= 21,500 B (~3,600 tok)` | **`PINNED`** |
| `7` | `#2 Efficiency` | **AGENTS.md Ceiling & Headroom** | `21,819 B (headroom: 681 B)` | `— (initial)` | `21,819 B (headroom: 681 B)` | `0 (baseline)` | `<= 22,500 B (24k hard)` | **`PINNED`** |
| `8` | `#2 Efficiency` | **Target Subsystem Context / Packet Tax** | `95,481 B (3 rules + 9 core SKILL.md files)` | `— (initial)` | `95,481 B (3 rules + 9 core SKILL.md files)` | `0 (baseline)` | `<= 115,000 B (modular sum <= 129,500 B)` | **`PINNED`** |
| `9` | `#2 Efficiency` | **Subagent Trajectory (Turns / Tokens / Cache %)** | `n/a (CLI bench)` | `— (initial)` | `n/a (CLI bench)` | `0 (baseline)` | `<= Baseline` | **`PINNED`** |
| `10` | `#3 Safety` | **Live Host Mutations & EROFS Blocks** | `mut: 0 / erofs: 1` | `— (initial)` | `mut: 0 / erofs: 1` | `0 (baseline)` | `mut: 0 / erofs >= 1` | **`PINNED`** |
| `11` | `#3 Safety` | **Boundary, Portability & Governance Seal** | `B:0 / P:0 / G:PASS` | `— (initial)` | `B:0 / P:0 / G:PASS` | `0 (baseline)` | `B:0 / P:0 / G:PASS` | **`PINNED`** |
| `12` | `#4 Speed` | **Execution Latency (p50 / p95 / Total) & Spawns** | `p50: 103ms / p95: 2264ms / 28.44s (49 spawns)` | `— (initial)` | `p50: 103ms / p95: 2264ms / 28.44s (49 spawns)` | `0 (baseline)` | `<= Baseline + 15%` | **`PINNED`** |

#### Part B — Fixed Subsystem Profile: `full-system-suite` (`16` Locked Metrics)

| # | Pillar | Standardized Metric | Baseline (`v0.1.0`) | Previous Run | Candidate (`v0.1.0`) | Delta (vs. Baseline) | Ceiling / Target | Status |
| :---: | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :---: |
| `1` | `#1 Accuracy` | **True-Positive Hallucinations Caught** | `7 / 7 (100.0%)` | `— (initial)` | `7 / 7 (100.0%)` | `0 (baseline)` | `100.0%` | **`PINNED`** |
| `2` | `#1 Accuracy` | **False-Positive Valid Prose Flagged** | `0` | `— (initial)` | `0` | `0 (baseline)` | `0` | **`PINNED`** |
| `3` | `#3 Safety` | **Runtime Anti-Snoop Gate Triggers** | `PASS (blocked)` | `— (initial)` | `PASS (blocked)` | `0 (baseline)` | `PASS` | **`PINNED`** |
| `4` | `#4 Speed` | **CLI Cold-Start Verification Latency (median)** | `82.13 ms` | `— (initial)` | `82.13 ms` | `0 (baseline)` | `<= Baseline + 15%` | **`PINNED`** |
| `5` | `#1 Accuracy` | **Top-3 Semantic/ID Recall Hit Rate** | `100.0% (5/5)` | `— (initial)` | `100.0% (5/5)` | `0 (baseline)` | `100.0%` | **`PINNED`** |
| `6` | `#1 Accuracy` | **N1 Numeric/Unit Query Weight Leak Rate** | `0.0%` | `— (initial)` | `0.0%` | `0 (baseline)` | `0.0%` | **`PINNED`** |
| `7` | `#2 Efficiency` | **--preflight Decision Packet Tokens (avg / max)** | `avg 562 / max 578 tok` | `— (initial)` | `avg 562 / max 578 tok` | `0 (baseline)` | `<= 600 tok` | **`PINNED`** |
| `8` | `#2 Efficiency` | **Active _Lessons_Learned.md Max Line Count** | `234 L` | `— (initial)` | `234 L` | `0 (baseline)` | `<= 420 L` | **`PINNED`** |
| `9` | `#3 Safety` | **v1.1 Governance Seal & Tamper Block** | `PASS` | `— (initial)` | `PASS` | `0 (baseline)` | `PASS` | **`PINNED`** |
| `10` | `#4 Speed` | **--kickstart Cold-Resume Latency** | `98.09 ms` | `— (initial)` | `98.09 ms` | `0 (baseline)` | `<= Baseline + 15%` | **`PINNED`** |
| `11` | `#2 Efficiency` | **Combined 3-Rule Always-On Turn Tax** | `20,459 B / 2548 w (~3440 tok)` | `— (initial)` | `20,459 B / 2548 w (~3440 tok)` | `0 (baseline)` | `<= 21,500 B (~3,600 tok)` | **`PINNED`** |
| `12` | `#2 Efficiency` | **In-Repo AGENTS.md Byte Size & Headroom** | `21,819 B (headroom: 681 B)` | `— (initial)` | `21,819 B (headroom: 681 B)` | `0 (baseline)` | `<= 22,500 B` | **`PINNED`** |
| `13` | `#2 Efficiency` | **Out-of-Tree Expanded AGENTS.md Byte Size** | `22,524 B (headroom: 1,476 B)` | `— (initial)` | `22,524 B (headroom: 1,476 B)` | `0 (baseline)` | `<= 24,000 B hard cap` | **`PINNED`** |
| `14` | `#2 Efficiency` | **Active Core Skills Footprint** | `9 skills / 8,684 w (~11,723 tok)` | `— (initial)` | `9 skills / 8,684 w (~11,723 tok)` | `0 (baseline)` | `<= 10,500 w (~14,175 tok)` | **`PINNED`** |
| `15` | `#1 Accuracy` | **Markdown Files Audited & Pass Rate** | `56 / 56 (100.0%)` | `— (initial)` | `56 / 56 (100.0%)` | `0 (baseline)` | `100.0%` | **`PINNED`** |
| `16` | `#1 Accuracy` | **Closed 360° Cylinder vs. Open Fillet Filter** | `PASS (Ø3.20mm kept, R1.50mm fillet excluded)` | `— (initial)` | `PASS (Ø3.20mm kept, R1.50mm fillet excluded)` | `0 (baseline)` | `PASS` | **`PINNED`** |

---

### Standardized Benchmark Run: `full-system-suite` (`v0.2.0` vs. Baseline `v0.1.0`) — v0.2.0 Official Pinned Baseline (Gemini Carbon Remediation)

- **Run ID & Timestamp**: `BMK-20261110_163542-4d137907` (`2026-11-10T16:35:42-06:00`)
- **Engine Provenance**: `/home/orin/Projects/Alchemical3D/Homunculus` | Version: `v0.2.0` | `HEAD`: `108b504f4ea7` | `Tree`: `2a8cc775a316` (`102` files, `clean`)
- **Overall Verdict**: **`BASELINE_PINNED`** (`Hard Blocks: 0` | `Advisories: 0` | `Wall-Clock: 15.03s`)

#### Part A — Universal 4-Pillar Spine (`12` Locked Metrics)

| # | Pillar | Standardized Metric | Baseline (`v0.1.0`) | Previous Run | Candidate (`v0.2.0`) | Delta (vs. Baseline) | Ceiling / Target | Status |
| :---: | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :---: |
| `1` | `Meta` | **Version & Tree Provenance** | `v0.1.0 (31aa0cb0 / 284d5a57)` | `v0.1.0 (31aa0cb0 / 284d5a57)` | `v0.2.0 (108b504f / 2a8cc775)` | `—` | `Clean or -dev+<tree8>` | **`PINNED`** |
| `2` | `#1 Accuracy` | **Positive Controls Pass Rate** | `17 / 17 (100.0%)` | `17 / 17 (100.0%)` | `17 / 17 (100.0%)` | `0 (no change)` | `100.0%` | `PASS` |
| `3` | `#1 Accuracy` | **Adversarial +faults Catch Rate** | `14 / 14 (100.0%)` | `14 / 14 (100.0%)` | `14 / 14 (100.0%)` | `0 (no change)` | `100.0%` | `PASS` |
| `4` | `#1 Accuracy` | **False Positives / False Negatives** | `FP: 0 / FN: 0` | `FP: 0 / FN: 0` | `FP: 0 / FN: 0` | `0 (no change)` | `FP: 0 / FN: 0` | `PASS` |
| `5` | `#1 Accuracy` | **Automated Unit Test Suite** | `46 / 46 (100.0%)` | `46 / 46 (100.0%)` | `52 / 52 (100.0%)` | `0 (no change)` | `100.0%` | `PASS` |
| `6` | `#2 Efficiency` | **Always-On 3-Rule Footprint** | `20,459 B / 2548 w (~3440 tok)` | `20,459 B / 2548 w (~3440 tok)` | `20,166 B / 2503 w (~3379 tok)` | `-293 B (-1.4%)` | `<= 21,500 B (~3,600 tok)` | **`IMPROVED`** |
| `7` | `#2 Efficiency` | **AGENTS.md Ceiling & Headroom** | `21,819 B (headroom: 681 B)` | `21,819 B (headroom: 681 B)` | `21,526 B (headroom: 974 B)` | `-293 B (-1.3%)` | `<= 22,500 B (24k hard)` | **`IMPROVED`** |
| `8` | `#2 Efficiency` | **Target Subsystem Context / Packet Tax** | `95,481 B (3 rules + 9 core SKILL.md files)` | `95,481 B (3 rules + 9 core SKILL.md files)` | `95,711 B (3 rules + 9 core SKILL.md files)` | `+230.00 units (+0.2%)` | `<= 115,000 B (modular sum <= 129,500 B)` | `PASS` |
| `9` | `#2 Efficiency` | **Subagent Trajectory (Turns / Tokens / Cache %)** | `n/a (CLI bench)` | `n/a (CLI bench)` | `n/a (CLI bench)` | `—` | `<= Baseline` | **`PINNED`** |
| `10` | `#3 Safety` | **Live Host Mutations & EROFS Blocks** | `mut: 0 / erofs: 1` | `mut: 0 / erofs: 1` | `mut: 0 / erofs: 1` | `0 (no change)` | `mut: 0 / erofs >= 1` | `PASS` |
| `11` | `#3 Safety` | **Boundary, Portability & Governance Seal** | `B:0 / P:0 / G:PASS` | `B:0 / P:0 / G:PASS` | `B:0 / P:0 / G:PASS` | `0 (no change)` | `B:0 / P:0 / G:PASS` | `PASS` |
| `12` | `#4 Speed` | **Execution Latency (p50 / p95 / Total) & Spawns** | `p50: 103ms / p95: 2264ms / 28.44s (49 spawns)` | `p50: 103ms / p95: 2264ms / 28.44s (49 spawns)` | `p50: 93ms / p95: 304ms / 15.03s (45 spawns)` | `-13.41 s (-47.2%)` | `<= Baseline + 15%` | **`IMPROVED`** |

#### Part B — Fixed Subsystem Profile: `full-system-suite` (`16` Locked Metrics)

| # | Pillar | Standardized Metric | Baseline (`v0.1.0`) | Previous Run | Candidate (`v0.2.0`) | Delta (vs. Baseline) | Ceiling / Target | Status |
| :---: | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :---: |
| `1` | `#1 Accuracy` | **True-Positive Hallucinations Caught** | `7 / 7 (100.0%)` | `7 / 7 (100.0%)` | `7 / 7 (100.0%)` | `0 (no change)` | `100.0%` | `PASS` |
| `2` | `#1 Accuracy` | **False-Positive Valid Prose Flagged** | `0` | `0` | `0` | `0 (no change)` | `0` | `PASS` |
| `3` | `#3 Safety` | **Runtime Anti-Snoop Gate Triggers** | `PASS (blocked)` | `PASS (blocked)` | `PASS (blocked)` | `0 (no change)` | `PASS` | `PASS` |
| `4` | `#4 Speed` | **CLI Cold-Start Verification Latency (median)** | `82.13 ms` | `82.13 ms` | `86.65 ms` | `+4.52 ms (+5.5%)` | `<= Baseline + 15%` | `PASS` |
| `5` | `#1 Accuracy` | **Top-3 Semantic/ID Recall Hit Rate** | `100.0% (5/5)` | `100.0% (5/5)` | `100.0% (5/5)` | `0 (no change)` | `100.0%` | `PASS` |
| `6` | `#1 Accuracy` | **N1 Numeric/Unit Query Weight Leak Rate** | `0.0%` | `0.0%` | `0.0%` | `0 (no change)` | `0.0%` | `PASS` |
| `7` | `#2 Efficiency` | **--preflight Decision Packet Tokens (avg / max)** | `avg 562 / max 578 tok` | `avg 562 / max 578 tok` | `avg 555 / max 566 tok` | `-12 tok (-2.1%)` | `<= 600 tok` | **`IMPROVED`** |
| `8` | `#2 Efficiency` | **Active _Lessons_Learned.md Max Line Count** | `234 L` | `234 L` | `231 L` | `-3 lines (-1.3%)` | `<= 420 L` | `PASS` |
| `9` | `#3 Safety` | **v1.1 Governance Seal & Tamper Block** | `PASS` | `PASS` | `PASS` | `0 (no change)` | `PASS` | `PASS` |
| `10` | `#4 Speed` | **--kickstart Cold-Resume Latency** | `98.09 ms` | `98.09 ms` | `105.52 ms` | `+7.43 ms (+7.6%)` | `<= Baseline + 15%` | `PASS` |
| `11` | `#2 Efficiency` | **Combined 3-Rule Always-On Turn Tax** | `20,459 B / 2548 w (~3440 tok)` | `20,459 B / 2548 w (~3440 tok)` | `20,166 B / 2503 w (~3379 tok)` | `-293 B (-1.4%)` | `<= 21,500 B (~3,600 tok)` | **`IMPROVED`** |
| `12` | `#2 Efficiency` | **In-Repo AGENTS.md Byte Size & Headroom** | `21,819 B (headroom: 681 B)` | `21,819 B (headroom: 681 B)` | `21,526 B (headroom: 974 B)` | `-293 B (-1.3%)` | `<= 22,500 B` | **`IMPROVED`** |
| `13` | `#2 Efficiency` | **Out-of-Tree Expanded AGENTS.md Byte Size** | `22,524 B (headroom: 1,476 B)` | `22,524 B (headroom: 1,476 B)` | `22,231 B (headroom: 1,769 B)` | `-293 B (-1.3%)` | `<= 24,000 B hard cap` | **`IMPROVED`** |
| `14` | `#2 Efficiency` | **Active Core Skills Footprint** | `9 skills / 8,684 w (~11,723 tok)` | `9 skills / 8,684 w (~11,723 tok)` | `9 skills / 8,744 w (~11,804 tok)` | `+60 words (+0.7%)` | `<= 10,500 w (~14,175 tok)` | `PASS` |
| `15` | `#1 Accuracy` | **Markdown Files Audited & Pass Rate** | `56 / 56 (100.0%)` | `56 / 56 (100.0%)` | `56 / 56 (100.0%)` | `0 (no change)` | `100.0%` | `PASS` |
| `16` | `#1 Accuracy` | **Closed 360° Cylinder vs. Open Fillet Filter** | `PASS (Ø3.20mm kept, R1.50mm fillet excluded)` | `PASS (Ø3.20mm kept, R1.50mm fillet excluded)` | `PASS (Ø3.20mm kept, R1.50mm fillet excluded)` | `0 (no change)` | `PASS` | `PASS` |

---

### Standardized Benchmark Run: `full-system-suite` (`v0.2.1` vs. Baseline `v0.2.0`) — v0.2.1 Official Pinned Baseline (Memory Retrieval & Option A TIER0 Refinement)

- **Run ID & Timestamp**: `BMK-20261111_085728-9fee5ee6` (`2026-11-11T08:57:28-06:00`)
- **Engine Provenance**: `/home/orin/Projects/Alchemical3D/Homunculus` | Version: `v0.2.1` | `HEAD`: `f9c732fa7df3` | `Tree`: `b1242ce694cf` (`102` files, `clean`)
- **Overall Verdict**: **`BASELINE_PINNED`** (`Hard Blocks: 0` | `Advisories: 1` | `Wall-Clock: 16.28s`)

#### Part A — Universal 4-Pillar Spine (`12` Locked Metrics)

| # | Pillar | Standardized Metric | Baseline (`v0.2.0`) | Previous Run | Candidate (`v0.2.1`) | Delta (vs. Baseline) | Ceiling / Target | Status |
| :---: | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :---: |
| `1` | `Meta` | **Version & Tree Provenance** | `v0.2.0 (108b504f / 2a8cc775)` | `v0.2.0 (108b504f / 2a8cc775)` | `v0.2.1 (f9c732fa / b1242ce6)` | `—` | `Clean or -dev+<tree8>` | **`PINNED`** |
| `2` | `#1 Accuracy` | **Positive Controls Pass Rate** | `17 / 17 (100.0%)` | `17 / 17 (100.0%)` | `17 / 17 (100.0%)` | `0 (no change)` | `100.0%` | `PASS` |
| `3` | `#1 Accuracy` | **Adversarial +faults Catch Rate** | `14 / 14 (100.0%)` | `14 / 14 (100.0%)` | `14 / 14 (100.0%)` | `0 (no change)` | `100.0%` | `PASS` |
| `4` | `#1 Accuracy` | **False Positives / False Negatives** | `FP: 0 / FN: 0` | `FP: 0 / FN: 0` | `FP: 0 / FN: 0` | `0 (no change)` | `FP: 0 / FN: 0` | `PASS` |
| `5` | `#1 Accuracy` | **Automated Unit Test Suite** | `52 / 52 (100.0%)` | `52 / 52 (100.0%)` | `53 / 53 (100.0%)` | `0 (no change)` | `100.0%` | `PASS` |
| `6` | `#2 Efficiency` | **Always-On 3-Rule Footprint** | `20,166 B / 2503 w (~3379 tok)` | `20,166 B / 2503 w (~3379 tok)` | `20,166 B / 2503 w (~3379 tok)` | `0 (no change)` | `<= 21,500 B (~3,600 tok)` | `PASS` |
| `7` | `#2 Efficiency` | **AGENTS.md Ceiling & Headroom** | `21,526 B (headroom: 974 B)` | `21,526 B (headroom: 974 B)` | `21,526 B (headroom: 974 B)` | `0 (no change)` | `<= 22,500 B (24k hard)` | `PASS` |
| `8` | `#2 Efficiency` | **Target Subsystem Context / Packet Tax** | `95,711 B (3 rules + 9 core SKILL.md files)` | `95,711 B (3 rules + 9 core SKILL.md files)` | `95,711 B (3 rules + 9 core SKILL.md files)` | `0 (no change)` | `<= 115,000 B (modular sum <= 129,500 B)` | `PASS` |
| `9` | `#2 Efficiency` | **Subagent Trajectory (Turns / Tokens / Cache %)** | `n/a (CLI bench)` | `n/a (CLI bench)` | `n/a (CLI bench)` | `—` | `<= Baseline` | **`PINNED`** |
| `10` | `#3 Safety` | **Live Host Mutations & EROFS Blocks** | `mut: 0 / erofs: 1` | `mut: 0 / erofs: 1` | `mut: 0 / erofs: 1` | `0 (no change)` | `mut: 0 / erofs >= 1` | `PASS` |
| `11` | `#3 Safety` | **Boundary, Portability & Governance Seal** | `B:0 / P:0 / G:PASS` | `B:0 / P:0 / G:PASS` | `B:0 / P:0 / G:PASS` | `0 (no change)` | `B:0 / P:0 / G:PASS` | `PASS` |
| `12` | `#4 Speed` | **Execution Latency (p50 / p95 / Total) & Spawns** | `p50: 93ms / p95: 304ms / 15.03s (45 spawns)` | `p50: 93ms / p95: 304ms / 15.03s (45 spawns)` | `p50: 87ms / p95: 312ms / 16.28s (45 spawns)` | `+1.25 s (+8.3%)` | `<= Baseline + 15%` | `PASS` |

#### Part B — Fixed Subsystem Profile: `full-system-suite` (`16` Locked Metrics)

| # | Pillar | Standardized Metric | Baseline (`v0.2.0`) | Previous Run | Candidate (`v0.2.1`) | Delta (vs. Baseline) | Ceiling / Target | Status |
| :---: | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :---: |
| `1` | `#1 Accuracy` | **True-Positive Hallucinations Caught** | `7 / 7 (100.0%)` | `7 / 7 (100.0%)` | `7 / 7 (100.0%)` | `0 (no change)` | `100.0%` | `PASS` |
| `2` | `#1 Accuracy` | **False-Positive Valid Prose Flagged** | `0` | `0` | `0` | `0 (no change)` | `0` | `PASS` |
| `3` | `#3 Safety` | **Runtime Anti-Snoop Gate Triggers** | `PASS (blocked)` | `PASS (blocked)` | `PASS (blocked)` | `0 (no change)` | `PASS` | `PASS` |
| `4` | `#4 Speed` | **CLI Cold-Start Verification Latency (median)** | `86.65 ms` | `86.65 ms` | `85.94 ms` | `-0.71 ms (-0.8%)` | `<= Baseline + 15%` | `PASS` |
| `5` | `#1 Accuracy` | **Top-3 Semantic/ID Recall Hit Rate** | `100.0% (5/5)` | `100.0% (5/5)` | `100.0% (5/5)` | `0 (no change)` | `100.0%` | `PASS` |
| `6` | `#1 Accuracy` | **N1 Numeric/Unit Query Weight Leak Rate** | `0.0%` | `0.0%` | `0.0%` | `0 (no change)` | `0.0%` | `PASS` |
| `7` | `#2 Efficiency` | **--preflight Decision Packet Tokens (avg / max)** | `avg 555 / max 566 tok` | `avg 555 / max 566 tok` | `avg 1464 / max 1517 tok` | `+951 tok (+168.0%)` | `<= 1,800 tok` | **`ADVISORY`** |
| `8` | `#2 Efficiency` | **Active _Lessons_Learned.md Max Line Count** | `231 L` | `231 L` | `221 L` | `-10 lines (-4.3%)` | `<= 420 L` | **`IMPROVED`** |
| `9` | `#3 Safety` | **v1.1 Governance Seal & Tamper Block** | `PASS` | `PASS` | `PASS` | `0 (no change)` | `PASS` | `PASS` |
| `10` | `#4 Speed` | **--kickstart Cold-Resume Latency** | `105.52 ms` | `105.52 ms` | `111.80 ms` | `+6.28 ms (+6.0%)` | `<= Baseline + 15%` | `PASS` |
| `11` | `#2 Efficiency` | **Combined 3-Rule Always-On Turn Tax** | `20,166 B / 2503 w (~3379 tok)` | `20,166 B / 2503 w (~3379 tok)` | `20,166 B / 2503 w (~3379 tok)` | `0 (no change)` | `<= 21,500 B (~3,600 tok)` | `PASS` |
| `12` | `#2 Efficiency` | **In-Repo AGENTS.md Byte Size & Headroom** | `21,526 B (headroom: 974 B)` | `21,526 B (headroom: 974 B)` | `21,526 B (headroom: 974 B)` | `0 (no change)` | `<= 22,500 B` | `PASS` |
| `13` | `#2 Efficiency` | **Out-of-Tree Expanded AGENTS.md Byte Size** | `22,231 B (headroom: 1,769 B)` | `22,231 B (headroom: 1,769 B)` | `22,231 B (headroom: 1,769 B)` | `0 (no change)` | `<= 24,000 B hard cap` | `PASS` |
| `14` | `#2 Efficiency` | **Active Core Skills Footprint** | `9 skills / 8,744 w (~11,804 tok)` | `9 skills / 8,744 w (~11,804 tok)` | `9 skills / 8,744 w (~11,804 tok)` | `0 (no change)` | `<= 10,500 w (~14,175 tok)` | `PASS` |
| `15` | `#1 Accuracy` | **Markdown Files Audited & Pass Rate** | `56 / 56 (100.0%)` | `56 / 56 (100.0%)` | `56 / 56 (100.0%)` | `0 (no change)` | `100.0%` | `PASS` |
| `16` | `#1 Accuracy` | **Closed 360° Cylinder vs. Open Fillet Filter** | `PASS (Ø3.20mm kept, R1.50mm fillet excluded)` | `PASS (Ø3.20mm kept, R1.50mm fillet excluded)` | `PASS (Ø3.20mm kept, R1.50mm fillet excluded)` | `0 (no change)` | `PASS` | `PASS` |

#### Run-Specific Forensic Notes *(Decoupled from Standardized Metric Rows)*

- [COURSE_D_APPROVED_TRADEOFF] Approved v0.2.1 #1 Accuracy > #2 Efficiency trade-off: expanded memory decision packet ceiling from 600 to <=1,800 tokens for S6_Budgeted guardrail auto-hydration and Adaptive Top-K 3..6

---

