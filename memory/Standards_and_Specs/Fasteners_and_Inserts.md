---
title: "Fasteners and Inserts"
entity: "shared"
compartment: "public"
last_synced: "2026-11-05"
---

# 🔩 Fasteners, Heat-Set Inserts & Torque Standards

Referenced by [`README.md`](../README.md) and all hardware project notes (`Alembic_Toolhead`, `Pneuma_Remote_Air`, `A3DP_Gantry_Assembly`, `Pestle_Rotational_Bowden`).

---

## 1. Heat-Set Inserts
- **Standard Spec:** Voron-standard **M3x5x4mm** brass threaded heat-set inserts (5mm OD x 4mm Length).
- **Installation:** Press squarely with a soldering iron set near the filament printing temperature until flush with the surrounding plastic surface.

## 2. Fastener Torque Limits (Metal vs. Printed Plastic)
- **M3 into Milled Aluminum:** `~1.0 to 1.5 Nm` (`~1.2 Nm` / `10.6 in-lbs` nominal).
- **M5 into Milled Aluminum:** `~3.0 to 4.5 Nm`.
- **Fasteners into 3D-Printed Plastic (ABS/ASA/PC):** **Do not torque to metal specs.** Stop turning immediately once the plastic begins to compress to prevent layer delamination or thread stripping.

## 3. Threadlocker Selection & Chemical Safety
- **M5 and Larger (Metal-to-Metal):** Medium-strength **Loctite 243 (Blue)**.
- **M3 / M4 and Smaller (Metal-to-Metal):** Low-strength **Loctite 222MS (Purple)**.
- **Never Use Red Threadlocker:** High-strength permanent threadlocker requires heat/excessive torque that will destroy surrounding printed components.
- **Plastic Chemical Hazard:** Never allow anaerobic threadlocker (liquid or vapor) to contact **ABS, ASA, or PC** printed parts—it causes rapid stress-cracking and brittle failure.
