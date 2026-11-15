---
project: "Alembic_Toolhead"
entity: "Alchemical-3D"
compartment: "public"
quarantine: true
authoritative: false
status: "unverified_quarantine"
last_synced: "2026-11-14"
reason: "Phase 5 Stage 5.2 local sidecar evaluation trial; unverified until frontier verify_claims.py pass"
---

# Bionic Qwen3.6-35B-A3B Pilot 2 — Alembic Toolhead Working-Tree Diff & Consistency Audit (`[QUARANTINED — DO NOT CITE AS FACT]`)

> [!CAUTION]
> **STRICT QUARANTINE GATE (`quarantine: true`, `authoritative: false`)**: Stored in `Projects/Alembic_Toolhead/Quarantine/`.
> **Reason**: Phase 5 Stage 5.2 local sidecar evaluation trial; unverified until frontier verify_claims.py pass

<!-- local_sidecar provenance: schema=LOCAL_SIDECAR_V1 author="LM Studio Bionic (qwen3.6-35b-a3b, fast)" elapsed_s=80.138 prompt_tok=20693 out_tok=2025 tg_tok_s=25.27 -->

### 1. Working-Tree Diff Summary (`HEAD 3ff29ce` -> Current Working Tree)

**Document & Content Refinements:**
*   **BOM.md**: Expanded from a basic list to a structured document with `> [!NOTE]` affiliate blocks, detailed part descriptions (e.g., specifying "Voron-spec M3x5x4mm brass inserts"), and added a new section for `[!IMPORTANT] Part Flexibility & CAD Modifications` referencing `STEP_Files/` and Discord support (`BOM.md#L1-L66`).
*   **Assembly_Guide.md**: Significantly expanded from a brief overview to a detailed step-by-step guide. Added specific torque warnings (1.2 Nm / 10.6 in-lbs for aluminum, caution for plastic), threadlocker compatibility warnings, and precise insertion depth calculations for the tubing jig (`Assembly_Guide.md#L1-L149`).
*   **Print_Settings.md**: Added critical material warnings against PLA/PETG due to thermal softening, specific slicer parameters (0.2mm layer height, 4+ walls), and calibration tips for ABS/ASA shrinkage (`Print_Settings.md#L1-L37`).
*   **README.md**: Enhanced philosophical description of the pneumatic architecture ("scalpel vs sledgehammer"), added key specifications table, linked to companion projects (Pneuma, A3DP Gantry), and updated image alt-text (`README.md#L1-L94`).
*   **ALPHA_&_DIRECTION.md**: Updated hardware compatibility list to explicitly mention native fitment for the A3DP Gantry Assembly and refined roadmap descriptions (`ALPHA_&_DIRECTION.md#L1-L52`).

**STL Variant Additions & Options:**
*   The working tree `BOM.md` now explicitly documents variant STL choices in the Printed Parts table:
    *   **Fan Baffle**: `Fan_Baffle_Takoto.stl` *or* `Fan_Baffle_Dragon.stl` (`BOM.md#L21`).
    *   **Sensor Retainer**: `Sensor_Retainer.stl` (Takoto) *or* `Sensor_Retainer_Dragon-MZE.stl` (Dragon/MZE) (`BOM.md#L25`).
    *   **Shims**: `Shim_06mm_BDsensor.stl` (Takoto, 0.6mm offset) *or* `Shim_56_BDsensor_Dragon-MZE.stl` (Dragon/MZE, 5.6mm offset) (`BOM.md#L27`).
*   Binary image files (`alembic_angle_down.png`, `alembic_angle_up.png`, `alembic_face.png`) have been updated in the working tree to reflect new renderings or formatting.

**Hardware Status vs HEAD:**
*   **M3 Heat-Set Inserts**: Retained as ~4 qty, now specified as "Voron-spec M3x5x4mm brass" (`BOM.md#L37`).
*   **M3 Screws**: All sizes (`M3x65mm`, `M3x8mm`, `M3x20mm`, `M3x24mm`) and Grub Screws retained with updated descriptions clarifying their specific roles (e.g., vertical tie-bolts, carriage mount) (`BOM.md#L38-L42`).
*   **O-Ring 9x2**: Retained at Qty 2, description expanded to specify sealing path ("fitting, intake, and manifold") (`BOM.md#L44`).
*   **PC4-M10**: Retained as Qty 1, described as "Straight-through" fitting (`BOM.md#L45`).
*   **M2 Hardware**: Inserts (~2), `M2x10mm BHCS` (~1), and `M2x8mm BHCS` (~1) retained for BDsensor optionality (`BOM.md#L47-L49`).

### 2. Cross-Document Consistency Checks (Working-Tree `BOM.md` vs `Assembly_Guide.md`)

**O-Ring 9x2 Count & Placement Audit:**
*   **BOM.md Quantity**: Lists `[O-Ring 9x2]` Qty **2** (`BOM.md#L44`).
*   **Assembly_Guide.md Placements**:
    *   Step "Preparation: Heat Set Inserts", Item 2: Seats the **upper** `9x2mm O-ring` on the Intake for the PC4-M10 fitting seal (`Assembly_Guide.md#L45`).
    *   Step 1, Item 2: Seats the **lower** `9x2mm O-ring` between Manifold Frame and Lower Body (`Assembly_Guide.md#L70`).
    *   Step 2 Tip: References the **central** `9x2mm O-ring` seating between Intake and Manifold Frame (`Assembly_Guide.md#L89-L90`).
*   **Consistency**: The guide describes three distinct sealing locations requiring O-rings (Intake top, Lower Body/Manifold interface, Central Intake/Manifold interface). However, the BOM only lists Qty 2. The guide's Step 1 Item 2 and Step 2 Tip appear to describe the *same* central seal location differently or imply a third ring is needed if the "central" one is distinct from the "lower" one.
    *   *Analysis*: Step 1 Item 2 says "between Manifold Frame and Lower Body". Step 2 Tip says "between Intake and Manifold Frame". These are two different interfaces. The Preparation step seats an O-ring on top of the Intake (3rd location).
    *   **Conflict**: BOM Qty is 2, but Assembly Guide explicitly details seating O-rings at three distinct locations: (1) Top of Intake for PC4-M10 (`Assembly_Guide.md#L45`), (2) Between Manifold Frame and Lower Body (`Assembly_Guide.md#L70`), and (3) Central seal between Intake and Manifold Frame (`Assembly_Guide.md#L90`).
    *   `[TBD: CONFLICT — BOM Qty 2 (BOM.md#L44) vs Assembly Guide requiring 3 O-rings for top, central, and lower seals (Assembly_Guide.md#L45, L70, L90)]`

**Fastener Size, Head Style & Quantity Completeness:**
*   **M3 Heat-Set Inserts**: BOM Qty ~4 (`BOM.md#L37`). Guide calls for 2 in Intake (`Assembly_Guide.md#L44`) and 2 in Strain Relief (`Assembly_Guide.md#L46`), totaling 4 inserts, but omits the `M3x5x4mm` sizing in those assembly steps (`audit_repo_docs.py` load-bearing gap).
    *   `[TBD: Missing Fastener Dimension — Assembly_Guide.md#L44 and Assembly_Guide.md#L46 omit M3x5x4mm sizing specified in BOM.md#L37]`
*   **M3x65mm**: BOM Qty ~2 (`BOM.md#L38`). Guide calls for (2) screws in Step 2 (`Assembly_Guide.md#L86`). **Consistent.**
*   **M3x8mm**: BOM Qty ~8 (`BOM.md#L39`). Step 2 (`Assembly_Guide.md#L92`) and Step 4 (`Assembly_Guide.md#L122`) reference `M3x8mm` screws without explicit per-step quantities (`audit_repo_docs.py` load-bearing gap).
    *   `[TBD: Missing Fastener Quantity — Assembly_Guide.md#L92 and Assembly_Guide.md#L122 omit explicit screw counts for M3x8mm screws; BOM.md#L39 lists ~8]`
*   **M3x20mm**: BOM Qty ~2 (`BOM.md#L40`). Guide calls for two screws in Preparation Item 4 (`Assembly_Guide.md#L47`). **Consistent.**
*   **M3x24mm**: BOM Qty ~2 (`BOM.md#L41`). Guide calls for (2) BHCS in Step 3 Item 2 (`Assembly_Guide.md#L107`). **Consistent.**
*   **M3 Grub Screws**: BOM Qty ~2 (`BOM.md#L42`). Guide calls for (2) grub screws in Step 1 Item 3 (`Assembly_Guide.md#L71`). **Consistent.**
*   **M2 Heat-Set Inserts**: BOM Qty ~2 (`BOM.md#L47`). Guide calls for (2) inserts in Optional BDsensor step (`Assembly_Guide.md#L131`). **Consistent.**
*   **M2x10mm BHCS**: BOM Qty ~1 (`BOM.md#L48`). Guide calls for an M2x10mm BHCS in Optional BDsensor step (`Assembly_Guide.md#L131`). **Consistent.**
*   **M2x8mm BHCS**: BOM Qty ~1 (`BOM.md#L49`). Guide calls for an M2x8mm BHCS in Optional BDsensor step (`Assembly_Guide.md#L131`). **Consistent.**

### 3. Open `[TBD]` Ledger

*   `[TBD: CONFLICT — BOM Qty 2 (BOM.md#L44) vs Assembly Guide requiring 3 O-rings for top, central, and lower seals (Assembly_Guide.md#L45, L70, L90)]`
*   `[TBD: Missing Fastener Dimension — Assembly_Guide.md#L44 and Assembly_Guide.md#L46 omit M3x5x4mm sizing specified in BOM.md#L37]`
*   `[TBD: Missing Fastener Quantity — Assembly_Guide.md#L92 and Assembly_Guide.md#L122 omit explicit screw counts for M3x8mm screws; BOM.md#L39 lists ~8]`
