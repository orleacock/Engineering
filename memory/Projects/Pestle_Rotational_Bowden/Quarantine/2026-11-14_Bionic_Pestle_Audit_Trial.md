---
project: "Pestle_Rotational_Bowden"
entity: "Alchemical-3D"
compartment: "public"
quarantine: true
authoritative: false
status: "unverified_quarantine"
last_synced: "2026-11-14"
reason: "Phase 5 Stage 5.1 local sidecar evaluation trial; unverified until frontier verify_claims.py pass"
---

# Bionic Qwen3.6-35B-A3B Pilot 1 — Pestle Rotational Bowden Discrepancy Audit (`[QUARANTINED — DO NOT CITE AS FACT]`)

> [!CAUTION]
> **STRICT QUARANTINE GATE (`quarantine: true`, `authoritative: false`)**: Stored in `Projects/Pestle_Rotational_Bowden/Quarantine/`.
> **Reason**: Phase 5 Stage 5.1 local sidecar evaluation trial; unverified until frontier verify_claims.py pass

<!-- local_sidecar provenance: schema=LOCAL_SIDECAR_V1 author="LM Studio Bionic (qwen3.6-35b-a3b, fast)" elapsed_s=45.424 prompt_tok=5394 out_tok=1800 tg_tok_s=39.63 -->

### Dimension A — Heat-Set Inserts (`M3x5x4`)

*   **BOM Specification**: The Bill of Materials lists a quantity of 7 heat-set inserts.
    *   `Pestle_Rotational_Bowden/README.md#L65`: "**7** | M3x5x4 Heatsets | Angled exterior texture, not straight"
*   **Assembly Instruction**: The assembly guide explicitly states a total of 6 heat sets are required.
    *   `Pestle_Rotational_Bowden/README.md#L100`: "Locate each heat set location in the Pestle Extruder assembly; there should be a total of 6 heat sets required for assembly: (3) Main Body, (1) Lever, and (2) Transmission Plate."
*   **Discrepancy**: The BOM quantity (7) exceeds the assembly instruction count (6).
    *   `[TBD: CONFLICT — BOM Quantity 7 (Pestle_Rotational_Bowden/README.md#L65) vs Assembly Instruction Total 6 (Pestle_Rotational_Bowden/README.md#L100)]`

### Dimension B — Fastener Head Styles (`SHCS` vs `BHCS`) & Unreferenced / Unquantified Screws

*   **Head Style Mismatches**:
    *   The BOM specifies all listed screws as `SHCS`.
        *   `Pestle_Rotational_Bowden/README.md#L67`: "**1** | M3x16mm SHCS"
        *   `Pestle_Rotational_Bowden/README.md#L68`: "**1** | M3x20mm SHCS"
        *   `Pestle_Rotational_Bowden/README.md#L69`: "**2** | M3x30mm SHCS"
        *   `Pestle_Rotational_Bowden/README.md#L70`: "**2** | M3x35mm SHCS"
        *   `Pestle_Rotational_Bowden/README.md#L71`: "**1** | M5x16mm SHCS"
    *   The assembly instructions specify `BHCS` for the rotational cross brace mounting.
        *   `Pestle_Rotational_Bowden/README.md#L120`: "Add an **M5x16 BHCS** to the Rotational Cross Brace..."
        *   `Pestle_Rotational_Bowden/README.md#L122`: "Secure the brace using **(2) M3x30mm and (2) M3x35mm BHCS** screws."
    *   `[TBD: CONFLICT — BOM specifies SHCS for M3x30mm, M3x35mm, and M5x16mm (Pestle_Rotational_Bowden/README.md#L69-L71) vs Assembly Instructions specify BHCS for same fasteners (Pestle_Rotational_Bowden/README.md#L120, Pestle_Rotational_Bowden/README.md#L122)]`

*   **Unreferenced BOM Fasteners**:
    *   The BOM lists one `M3x16mm SHCS`. No assembly step references an M3x16mm screw.
        *   `Pestle_Rotational_Bowden/README.md#L67`: "**1** | M3x16mm SHCS"
        *   `[TBD: Unreferenced Fastener — M3x16mm SHCS listed in BOM (Pestle_Rotational_Bowden/README.md#L67) but absent from Assembly Steps]`
    *   The BOM lists one `M3x20mm SHCS`. No assembly step references an M3x20mm screw.
        *   `Pestle_Rotational_Bowden/README.md#L68`: "**1** | M3x20mm SHCS"
        *   `[TBD: Unreferenced Fastener — M3x20mm SHCS listed in BOM (Pestle_Rotational_Bowden/README.md#L68) but absent from Assembly Steps]`

*   **Ambiguous/Omitted Assembly Fasteners**:
    *   Step 7 mentions securing a grub screw for the BMG gear but does not specify its size or head style.
        *   `Pestle_Rotational_Bowden/README.md#L114`: "...secure the grub screw to the flat section."
        *   `[TBD: Missing Specification — Grub screw size/head style referenced in Step 7 (Pestle_Rotational_Bowden/README.md#L114) but not defined in BOM or other steps]`

### Dimension C — Thrust Bearing (`F5-12M`) BOM Quantity vs Assembly Placements

*   **BOM Quantity**: The BOM lists one thrust bearing.
    *   `Pestle_Rotational_Bowden/README.md#L66`: "**1** | Thrust Bearing | 5mm ID x 12mm OD"
*   **Assembly Placements**: The instructions describe two distinct placements for thrust bearings (or shim washers).
    *   Placement 1: Between the M5x16 bolt head and the Rotational Cross Brace.
        *   `Pestle_Rotational_Bowden/README.md#L120`: "...with a thrust bearing (or shim washers) placed between the head of the bolt and the printed Rotational Cross Brace."
    *   Placement 2: Between the Rotational Cross Brace and the mounting solution.
        *   `Pestle_Rotational_Bowden/README.md#L124`: "...with a thrust bearing placed between the rotational cross brace and the mounting solution."
*   **Discrepancy**: The BOM provides 1 unit, while the assembly steps describe placements between the bolt head/cross brace and cross brace/mounting solution.
    *   `[TBD: CONFLICT — BOM Quantity 1 (Pestle_Rotational_Bowden/README.md#L66) vs Assembly Requirement 2 placements (Pestle_Rotational_Bowden/README.md#L120, Pestle_Rotational_Bowden/README.md#L124)]`

### Dimension D — `Releases/1.2/STLs/` Filename & Documentation Coverage

*   **Observed Inventory**:
    *   `[a]_pestle_lever.stl`
    *   `[a]_pestle_rotation_brace.stl`
    *   `pestle_2020_extrusion_mount.stl`
    *   `pestle_3DFused_gantry_mount.stl`
    *   `pestle_main_body.stl`
    *   `pestle_motor_plate.stl`
    *   `pestle_top_plate.stl`

*   **Documentation Coverage**:
    *   The STL directory README defines the naming convention but does not list specific files.
        *   `Releases/1.2/STLs/README.md#L5`: "[a]\_\*.stl | Accent color"
    *   The main README lists parts by function (e.g., "Main Body", "Top Plate") but does not map them to the specific STL filenames provided in the directory inventory.
        *   `Pestle_Rotational_Bowden/README.md#L100`: "(3) Main Body..."
        *   `Pestle_Rotational_Bowden/README.md#L106`: "...into the Top Plate and Bottom Plate..." (Note: "Bottom Plate" is mentioned in assembly but not present in the STL inventory list).
    *   **Missing Part Reference**: The assembly instructions reference a "Bottom Plate".
        *   `Pestle_Rotational_Bowden/README.md#L106`: "Insert (1) MR85ZZ bearing ... into the Top Plate and **Bottom Plate**..."
        *   `[TBD: Missing STL — Assembly Step 3 references a "Bottom Plate" (Pestle_Rotational_Bowden/README.md#L106), but no corresponding file exists in the provided Releases/1.2/STLs/ inventory]`
    *   **Undocumented Mounting Variants**: The STL inventory includes `pestle_2020_extrusion_mount.stl` and `pestle_3DFused_gantry_mount.stl`. These are not referenced in the assembly steps or BOM.
        *   `[TBD: Undocumented Parts — STL files for "2020 Extrusion Mount" and "3D Fused Gantry Mount" exist in directory (Observed Inventory) but are not described in Assembly Steps or BOM]`

### Open `[TBD]` Ledger

*   `[TBD: CONFLICT — BOM Quantity 7 (Pestle_Rotational_Bowden/README.md#L65) vs Assembly Instruction Total 6 (Pestle_Rotational_Bowden/README.md#L100)]`
*   `[TBD: CONFLICT — BOM specifies SHCS for M3x30mm, M3x35mm, and M5x16mm (Pestle_Rotational_Bowden/README.md#L69-L71) vs Assembly Instructions specify BHCS for same fasteners (Pestle_Rotational_Bowden/README.md#L120, Pestle_Rotational_Bowden/README.md#L122)]`
*   `[TBD: Unreferenced Fastener — M3x16mm SHCS listed in BOM (Pestle_Rotational_Bowden/README.md#L67) but absent from Assembly Steps]`
*   `[TBD: Unreferenced Fastener — M3x20mm SHCS listed in BOM (Pestle_Rotational_Bowden/README.md#L68) but absent from Assembly Steps]`
*   `[TBD: Missing Specification — Grub screw size/head style referenced in Step 7 (Pestle_Rotational_Bowden/README.md#L114) but not defined in BOM or other steps]`
*   `[TBD: CONFLICT — BOM Quantity 1 (Pestle_Rotational_Bowden/README.md#L66) vs Assembly Requirement 2 placements (Pestle_Rotational_Bowden/README.md#L120, Pestle_Rotational_Bowden/README.md#L124)]`
*   `[TBD: Missing STL — Assembly Step 3 references a "Bottom Plate" (Pestle_Rotational_Bowden/README.md#L106), but no corresponding file exists in the provided Releases/1.2/STLs/ inventory]`
*   `[TBD: Undocumented Parts — STL files for "2020 Extrusion Mount" and "3D Fused Gantry Mount" exist in directory (Observed Inventory) but are not described in Assembly Steps or BOM]`
