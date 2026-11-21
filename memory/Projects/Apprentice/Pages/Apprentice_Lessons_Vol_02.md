---
project: "Apprentice"
parent_note: "Apprentice_Lessons_Learned"
entity: "Alchemical-3D"
compartment: "public"
note_type: "lessons_learned_page"
volume: 2
last_synced: "2026-11-20"
---
# Apprentice — Lessons Learned — Volume 02

> **Paginated Continuation of [`Apprentice_Lessons_Learned.md`](../Apprentice_Lessons_Learned.md)**: Overflow book page (`<= 22 KB` / `<= 12` entries per page).

---

## 2. Active Lessons Continuation (`TIER0` & `TIER2`)

### `LL-08` [TIER2] [TRAP] — Post-patch live benchmark VRF dropped from 97.9% to 76-83% (S2 planner.py 0/2, S3 core.py 7/15) after... (`2026-11-20`)
- **Symptom / Trap:** Post-patch live benchmark VRF dropped from 97.9% to 76-83% (S2 planner.py 0/2, S3 core.py 7/15) after reformatting compact single-line function signatures into PEP-8 multi-line signatures.
- **Root Cause:** grounding._normalize_ws() collapsed newline-indented multi-line signatures into '( arg, )' with spaces inside brackets and trailing commas, causing valid single-line quotes '(arg)' to fail substring matching; READ_SYSTEM_PROMPT had also dropped 'from those lines'.
- **Verified Resolution & Permanent Guardrail:** Keep bracket-padding normalization (r'([(\[{])\s+' and r',?\s+([)\]}])') in grounding._normalize_ws() (without touching identifiers, numbers, or operators) and preserve 'from those lines' in READ_SYSTEM_PROMPT/REVIEW_SYSTEM_PROMPT (verified 10/10 100.0% live S1-S3 VRF, 33/33 unit tests). (apprentice/grounding.py, apprentice/core.py, tests/test_grounding.py (01438d33b485)).
