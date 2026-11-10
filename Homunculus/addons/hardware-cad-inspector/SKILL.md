---
name: hardware-cad-inspector
description: Optional Drop-In add-on for one-pass STEP/STL outer envelopes, mesh volumes, STEP-STL parity, and .cfg pinout telemetry while enforcing the CAD Epistemic Boundary.
---

# Deterministic Hardware CAD & Firmware Envelope Inspector (`hardware-cad-inspector`)

This optional side-loaded add-on (`addons/hardware-cad-inspector/`, activatable by copying into `skills/hardware-cad-inspector/`) extracts **base outer dimensional envelopes (`X × Y × Z mm`), mesh volumes (`cm³`), STEP↔STL outer envelope parity, closed `360°` circular surface histograms (`Ø mm`), and firmware (`.cfg`) pinouts** in a single deterministic pass (`~0.18s`) under **`1. Accuracy & Truth -> 2. Efficiency -> 3. Data Safety -> 4. Speed`**.

> [!IMPORTANT]
> **CAD Epistemic Boundary (Structure vs. Human Design Intent)**:
> Raw `.step`/`.stp`, `.stl`, and `.3mf` files record **geometry** (outer bounding boxes, mesh volumes, and surface primitives), **never human engineering intent**. A circular cylinder in CAD may be a fastener clearance hole, heat-set insert pocket, alignment dowel, airflow vent, weight-relief pocket, or cosmetic boss. Never deduce undocumented fastener counts, thread engagement, or part-to-part mating mechanisms from CAD geometry—bind functional assembly claims strictly to `BOM.md` and `Assembly_Guide.md`, or tag **`[TBD: Confirm design intent with engineer]`**.

---

## 1. Pre-Flight Foundation Checks

Before running `inspect_hardware_ecosystem.py` on a hardware or hybrid repository:

1. **Check Project Memory First (`project-memory`)**:
   - Read `<memory_root>/Projects/<Project>/<Project>.md` (`AUTO-TREE`) and `<Project>_Hardware.md` on Turn 1.
   - If `<Project>_Hardware.md` is already present and `inspect_hardware_ecosystem.py --memory-root <memory_root> --project <Project> --check-cache` exits `0` (`CACHE_VALID`), use the cached manifest directly (`0` re-parse turns).
2. **Zero Ad-Hoc CAD Parsing (`ZERO_ADHOC_CAD_PARSING`)**:
   - Never call `read_file`, `grep`, `sed`, `awk`, or custom `python3` scripts on raw `.step`, `.stp`, `.stl`, `.3mf`, `.iges`, or `.fcstd` files.
   - Resolve [`inspect_hardware_ecosystem.py`](scripts/inspect_hardware_ecosystem.py) directly from `<HOMUNCULUS_ROOT>/addons/hardware-cad-inspector/scripts/inspect_hardware_ecosystem.py` (or `skills/hardware-cad-inspector/` when promoted).

---

## 2. Step-by-Step Execution Procedures

### Step 1 — Run Single-Pass Hardware Envelope & Firmware Telemetry
Execute `inspect_hardware_ecosystem.py` once per repository (do **not** export or read `hw_telemetry.json` via `read_file` when `<Project>_Hardware.md` or the stdout summary table is already in context):

```bash
# Read-only stdout summary (safe for subagents and Primary Thread)
python3 <HOMUNCULUS_ROOT>/addons/hardware-cad-inspector/scripts/inspect_hardware_ecosystem.py \
  --repo /path/to/repo \
  [--memory-root ./memory] \
  [--project <Project>]
```

- **Primary Thread Manifest Sync** (when updating `<memory_root>/Projects/<Project>/<Project>_Hardware.md` prior to `pre-commit-gate`):
  ```bash
  python3 <HOMUNCULUS_ROOT>/addons/hardware-cad-inspector/scripts/inspect_hardware_ecosystem.py \
    --repo /path/to/repo \
    --memory-root ./memory \
    --project <Project> \
    --sync-manifest
  ```

### Step 2 — Enforce the One-Pass CAD Stop Gate (`0` Follow-Up CAD Loops)
Once `inspect_hardware_ecosystem.py` prints `[CAD STOP GATE — ONE-PASS TELEMETRY COMPLETE]`:
1. **Report Base Envelopes & Parity Verbatim**: Cite exact outer bounding envelopes (`X × Y × Z mm`), closed mesh volumes (`cm³`), `STEP Sync` status (`MATCH (<=0.2mm)` vs. `DRIFT`), and firmware `.cfg` pins directly from the table.
2. **Do Not Guess Missing Assembly Specs from Diameters**: If `Assembly_Guide.md` or `BOM.md` omits a fastener count, screw length, or mating relationship, do **not** count `Ø3.00mm` / `Ø3.20mm` surfaces in STEP files to invent a fastener BOM row—emit **`[TBD: <missing_fastener_or_mating_spec>]`** inline and ask the engineer.

### Step 3 — End-of-Pass Claim Verification (`claim-verification` & `pre-commit-gate`)
- Whenever authoring or auditing a hardware README, BOM, Assembly Guide, or audit report, validate the drafted `.md` file via `verify_claims.py` (`VRF-<12hex>`):
  ```bash
  python3 <HOMUNCULUS_ROOT>/skills/claim-verification/scripts/verify_claims.py \
    --target <draft.md> \
    --sources /path/to/repo [/path/to/scratch/hw_telemetry.json]
  ```
- Defer memory tree and visual refreshes (`sync_memory.py --sync-trees`) to `pre-commit-gate` (`X -> Y -> Z`) prior to commit, and validate any script/skill modifications via `engineering-sandbox` (`sandbox_runner.py` `OS Dry-Run` / `[SANDBOX-PENDING]`).

---

## 3. Stop & Escalation Conditions

Halt immediately and consult the user if:
1. **Undocumented Design Intent (`Tier-A / [TBD] Escalation`)**: A hardware deliverable requires knowing which holes mate to which components, whether a bore is tapped vs. clearance vs. heat-set, or why a geometric feature exists, and `BOM.md` / `Assembly_Guide.md` does not state it—tag `[TBD: Confirm design intent with engineer]` and ask via `ask_question` rather than guessing from CAD coordinates.
2. **STEP ↔ STL Outer Envelope Drift (`DRIFT_DETECTED`)**: `inspect_hardware_ecosystem.py` detects an outer bounding-box mismatch `> 0.20 mm` between a `.step` source model and its exported `.stl` mesh—surface the exact delta to the engineer before publishing release assets.
3. **Blocked CAD/CFG Extraction (`[EXTRACTION BLOCKED — ABORTED]`)**: Any target repository path or CAD file is unreadable or corrupted.
