---
title: "Homunculus Memory Weight, Scoring & Headroom Reference"
project: "Homunculus"
parent_note: "Homunculus"
entity: "Alchemical-3D"
compartment: "private"
authoritative: false
last_synced: "2026-11-09"
---

# ⚖️ Homunculus — Memory Weight, Scoring & Headroom Reference

> **Maintainer Reference Only (`authoritative: false`)**: Human-oriented reference chart documenting all active constants in `MEMORY_SCORING_CONFIG` inside `sync_memory.py` (`Projects/Homunculus/Homunculus.md`). Automatically excluded from `verify_claims.py` quantitative whitelists (`authoritative: false`) and parity-checked by `test_project_memory.py`.

---

## 1. Gravity Tier Multipliers & Gates (`TIER0`–`TIER5`)

| Tier | Active Multiplier | Storage Location | Entry / Suppression Gate |
| :--- | :---: | :--- | :--- |
| `TIER0` | `4.0` | `<Project>_Lessons_Learned.md` (`<= 3` sections) | Always shown in `[TIER0 Pinned Project Laws]` (`<= 300` chars); enters `Top-3` only when `bm25_sat >= 0.45` or exact ID queried. |
| `TIER1` | `5.0` | `SUBSYSTEM-INVARIANTS` table | Rendered directly in `[TIER1 Subsystem Invariants]` (`Rank #1`: `850` / `450` chars; `Rank #2`: `420` / `260` chars). |
| `TIER2` | `2.0` | `<Project>_Lessons_Learned.md` (`<= 7` sections) | Active dev-cycle full-context lessons (`R_base >= 0.08`). |
| `TIER3` | `1.0` | `Archive/<Project>_Lessons_Archive.md` (`0444`) | Graduated invariant-backed lessons (`R_base >= 0.08`). |
| `TIER4` | `0.5` | `Archive/<Project>_Lessons_Archive.md` (`0444`) | Isolated polish / edge-case history (`R_base >= 0.08`). |
| `TIER5` | `0.0` (`0.25` opt-in) | `Archive/<Project>_Lessons_Archive.md` (`0444`, sealed) | Excluded by default; emits zero-value-leak `[TIER5_SUPPRESSED]` ID-only footer when `bm25_sat >= 0.35`. |

---

## 2. Hybrid Retrieval Formula & `N1` Non-Numeric Law

| Parameter | Config Key | Locked Value | Purpose |
| :--- | :--- | :---: | :--- |
| Project IDF Blend | `project_idf_blend` | `0.70` | Preserves project-local specificity (`70%` project IDF). |
| Entity IDF Blend | `entity_idf_blend` | `0.30` | Smooths rare terms across same-entity projects (`30%` entity IDF). |
| BM25 `k1` / `b` / `sat_k` | `bm25_k1` / `bm25_b` / `bm25_sat_k` | `1.5` / `0.75` / `1.6` | Saturation curve `bm25_sat = raw / (raw + 1.6)` immune to single-outlier denominator spikes. |
| `R_base` Component Weights | `r_base_*_weight` | `0.50` / `0.30` / `0.20` | `0.50 * BM25_comp + 0.30 * Cosine_ngram + 0.20 * FileGraphOverlap` (`0.625 / 0.375` when `q_files` empty; `floor = 0.08`). |
| Same-Entity Sibling Inheritance | `sibling_*_weight` | `0.65` / `0.90` | Intra-ecosystem sibling transfer (`0.65x` implicit, `0.90x` explicit companion project, `r_base >= 0.22`; `0%` cross-entity bleed). |
| Telemetry Activity Modifier | `activity_mod_*` | `0.85` – `1.25` | `TIER2`–`TIER4` recency (`30d` halflife) + `near_misses`/`drilldowns` tie-breaker (`TIER0` & `TIER1` locked at `1.00` / `0%` decay). |
| Numeric Query Weight (`N1`) | `numeric_query_weight` | `0.0` | Strips bare numbers, ISO dates, and digit-initial magnitudes (`115C`, `24V`, `80%`); keeps letter-initial designators (`PB11`, `M3`, `LL-*`). |
| Decision Packet Ceiling | `packet_token_ceiling` | `600` | Hard `<= 600` token cap (`avg ~183` tokens; trims `Rank #2` before `Rank #1 Must-Keep`). |
| Capsule Character Budget | `capsule_*_chars` | `75` / `280` | Guardrail-First 1-line capsule (`Symptom <= 75` chars `->` `Guardrail <= 280` chars). |
| Pre-Write Deduplication Gate | `near_duplicate_cosine_gate` | `0.72` | Blocks duplicate `LL-xx`/`PB-xx` (`Cosine >= 0.72`) and redirects to `--reinforce-lesson` / `--update-playbook` (`--force-new` override). |
| Procedural Playbook Ceilings | `playbook_field_max_words` | `100` / `180` / `120`w | `<Project>_Playbooks.md` (`authoritative: false`; `Trigger <= 100w`, `Procedure <= 180w`, `Gate <= 120w`). |
| Active File Ceilings | `agents_md_max_words` / `lessons_active_max_lines` | `180`w / `420`L | `memory/AGENTS.md <= 180` words (`2200` B); `_Lessons_Learned.md <= 420` lines (`<= 10` active sections). |
