---
title: "Homunculus Memory Weight, Scoring & Headroom Reference"
project: "Homunculus"
parent_note: "Homunculus"
entity: "Alchemical-3D"
compartment: "private"
authoritative: false
last_synced: "2026-11-13"
---

# ⚖️ Homunculus — Memory Weight, Scoring & Headroom Reference

> **Maintainer Reference Only (`authoritative: false`)**: Auto-rendered reference chart reflecting active constants in `MEMORY_SCORING_CONFIG` (`skills/project-memory/scripts/sync_memory.py`). Excluded from `verify_claims.py` quantitative whitelists (`authoritative: false`) and parity-checked by `--audit` (`SCORING_DOC_CONFIG_DRIFT`).

---

## 1. Gravity Tier Multipliers & Gates (`TIER0`–`TIER5`)

| Tier | Active Multiplier | Storage Location | Entry / Suppression Gate |
| :--- | :---: | :--- | :--- |
| `TIER0` | `4.0` | `<Project>_Lessons_Learned.md` (`<= 3` sections) | Shown in `[TIER0 Pinned Project Laws]` (`<= 360` chars); enters active match when `r_base >= 0.24` or exact ID queried. |
| `TIER1` | `5.0` | `SUBSYSTEM-INVARIANTS` table | Rendered in `[TIER1 Subsystem Invariants]` (`Rank #1`: `850` / `450` chars; `Rank #2`: `520` / `300` chars). |
| `TIER2` | `1.65` | `<Project>_Lessons_Learned.md` (`<= 9` sections) | Active dev-cycle full-context lessons (`r_base >= 0.13`; `>= 4`-term pure-text boost tapers below `max(bm25_norm, qcov) = 0.80`). |
| `TIER3` | `1.0` | `Archive/<Project>_Lessons_Archive.md` (`0444`) | Graduated invariant-backed lessons (`r_base >= 0.13`). |
| `TIER4` | `0.5` (`0.85` high-evidence) | `Archive/<Project>_Lessons_Archive.md` (`0444`) | Isolated polish / edge-case history (`r_base >= 0.13`). |
| `TIER5` | `0.0` (`0.25` opt-in) | `Archive/<Project>_Lessons_Archive.md` (`0444`, sealed) | Excluded by default; emits zero-value-leak `[TIER5_SUPPRESSED]` ID-only footer when `bm25_sat >= 0.35`. |

---

## 2. Hybrid Retrieval Formula & Duty Char Budgets

| Parameter | Config Key | Locked Value | Purpose |
| :--- | :--- | :---: | :--- |
| Project / Entity IDF Blend | `project_idf_blend` / `entity_idf_blend` | `0.70` / `0.30` | `0.70` project IDF + `0.30` same-entity smoothed IDF. |
| BM25 `k1` / `b` / `sat_k` | `bm25_k1` / `bm25_b` / `bm25_sat_k` | `1.5` / `0.75` / `1.6` | Saturation curve `bm25_sat = raw / (raw + 1.6)`. |
| `R_base` Component Weights | `r_base_*_weight` | `0.50` / `0.30` / `0.20` | BM25 / N-gram / FileGraph (`0.625` / `0.375` when `q_files` empty; floor `0.13`). |
| Same-Entity Sibling Inheritance | `sibling_*_weight` | `0.52` / `0.90` | Intra-ecosystem sibling transfer (`0.52` implicit, `0.90` explicit companion, floor `0.20`). |
| Telemetry Activity Modifier | `activity_mod_*` | `0.85` – `1.25` | `TIER2`–`TIER4` recency (`30.0d` halflife) + reinforcement (`TIER0`/`TIER1` locked at `1.00`). |
| Adaptive Top-K / Hydration | `adaptive_topk_*` / `s6_hydrate_*` | `3`–`6` (`r_base >= 0.33`) | Adaptive Top-K (`rel >= 0.45`); full hydration `r_base >= 0.48` (max `1350` chars; S2 `155` chars). |
| Duty Char Budgets | `duty_char_budgets` | `2200` / `7200` / `12000` chars | Hard char ceilings: `radar <= 2200`, `packet <= 7200`, `cold_load <= 12000` (`--recall`/`--preflight`/`--kickstart`/`--audit`). |
| Capsule Character Budget | `capsule_*_chars` | `110` / `340` / `460` | Guardrail-First 1-line capsule (`Symptom <= 110` -> `Guardrail <= 340`, max `460` chars). |
| Pre-Write Deduplication Gate | `near_duplicate_cosine_gate` | `0.72` | Blocks duplicate `LL-*`/`PB-*` (`Cosine >= 0.72`) and redirects to `--reinforce-lesson` / `--update-playbook`. |
| Lesson / Playbook Word Caps | `lesson_field_max_words` / `playbook_field_max_words` | `120/120/140w` / `100/180/120w` | Active prose field word caps on `--add-lesson` & `--add-playbook` (`authoritative: false` for playbooks). |
| Active Governance Ceilings | `agents_md_max_*` / `decision_profile_max_lines` / `lessons_active_*` | `180w`/`2200B` / `60L` / `320L`/`12` | `memory/AGENTS.md <= 180`w (`2200` B), `Decision_Profile.md <= 60`L, `_Lessons_Learned.md <= 320`L (`<= 12` sections). |
