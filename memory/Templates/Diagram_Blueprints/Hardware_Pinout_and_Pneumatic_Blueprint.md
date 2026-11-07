---
title: "Hardware_Pinout_and_Pneumatic_Blueprint"
type: diagram-blueprint
blueprint_id: hardware_pinout_pneumatic
aliases: [hardware-pinout-pneumatic]
entity: "shared"
compartment: "public"
last_synced: "2026-11-05"
---

# 📐 Hardware Wiring, MCU Pinout & Pneumatic Block Blueprint (`hardware_pinout_pneumatic`)

Part of the [`README.md`](../../README.md). Standardized blueprint for **3D printer hardware wiring, MCU pinout diagrams (`PF7`, `PF9`, 24V/5V/GND, CANbus), and pneumatic/fluidic routing maps** (such as `Pneuma_Remote_Air` + `Alembic_Toolhead`) via `/home/orin/Projects/Engineering/Homunculus/skills/visual-studio/scripts/render_diagram.py`.

Compatible with all registered color palettes in `Templates/Color_Palettes/`:
- `Alchemical3D_Color_Template` (`--palette alchemical_dark`)
- `Alchemical3D_Light_Color_Template` (`--palette alchemical_light`)
- `Gruvbox_Local_Color_Template` (`--palette gruvbox_dark`)
- `NetCom_Corporate_Color_Template` (`--palette netcom_corporate`)

---

## 1. When to Use This Archetype
- **Pneumatic & Fluidic Routing Diagrams**: Air pump/compressor $\rightarrow$ pressure regulator $\rightarrow$ PWM MOSFET / solenoid valve $\rightarrow$ `6mm OD` PTFE trunk $\rightarrow$ Y-splitter $\rightarrow$ dual `5mm OD` PTFE toolhead branches (e.g., `Pneuma_Remote_Air` feeding `Alembic_Toolhead`).
- **MCU Board & Toolhead Wiring Maps**: Power distribution (`24V DC`, `5V BEC`, `GND`), Klipper MCU pin headers (`PF7` CPAP PWM, `PF9` tach/aux), heater cartridges, thermistors, and `CANbus` / `USB` umbilical harnesses.
- **Thermal / Desiccant Airflow Loops**: Heater core + blower + thermistor feedback loops for projects like `Retort`.

---

## 2. Structural & Anti-Defect Rules (Locked)
1. **Explicit Port & Pin Terminal Badges**: Every hardware block lists explicit left-side (`inputs`) and right-side (`outputs`) terminal ports with monospace pin/tubing tags (`[PF7]`, `[24V DC]`, `[6mm OD PTFE]`, `[Dual 5mm OD]`).
2. **Color-Coded Physical Mediums**:
   - `primary` (`#FF3985` / Brand Pink or Orange): High-priority control signals (`PWM`, `CANbus`, `Klipper MCU`).
   - `secondary` (`#C90448` / Crimson or Cyan/Aqua): High-velocity pneumatic airflow / pressurized PTFE lines.
   - `warn` (`#FFB800` / Amber): `24V DC` / `5V DC` power rails and thermal/pressure limits.
   - `pass` (`#2ECC71` / Green): Exhaust/nozzle delivery & verified sensor feedback.
3. **Bottom Engineering Spec Bar**: Includes a dedicated bottom callout bar for critical mechanical/firmware constraints (e.g., `cycle_time: 0.005`, `hardware_pwm: False`, PTFE OD reductions, and fastener torque warnings).

---

## 3. Declarative JSON Spec Skeleton (`diagram_spec`)

```json diagram_spec
{
  "archetype": "hardware_pinout_pneumatic",
  "title": "PNEUMA × ALEMBIC — PNEUMATIC COOLING & KLIPPER WIRING TOPOLOGY",
  "subtitle": "Remote High-Pressure Part Cooling | Klipper MCU PWM Control (PF7 / PF9) | 6mm-to-5mm OD PTFE Manifold Routing",
  "badge": "HARDWARE + PNEUMATIC SPEC",
  "width": 1680,
  "stages": [
    {
      "id": "stg_control",
      "header": "STAGE 1: KLIPPER MCU & POWER",
      "blocks": [
        {
          "id": "blk_psu",
          "title": "Printer 24V / 48V DC Power Supply",
          "subtitle": "Main Power Bus & Fuse Block",
          "badge": "POWER",
          "style": "warn",
          "specs": [
            "• 24V DC Primary Rail (Pump / Blower Supply)",
            "• Common Signal GND tied to MCU GND",
            "• Dedicated inline blade fuse recommended"
          ],
          "ports_out": [
            {"id": "p_24v", "label": "24V DC + GND"}
          ]
        },
        {
          "id": "blk_mcu",
          "title": "Klipper Mainboard (MCU)",
          "subtitle": "Pneuma.cfg — [fan_generic] / [output_pin]",
          "badge": "FIRMWARE",
          "style": "primary",
          "specs": [
            "• Pin PF7: Primary Pump / CPAP PWM Signal",
            "• Pin PF9: Aux Solenoid / Status Control",
            "• cycle_time: 0.005 (200 Hz) | hardware_pwm: False",
            "• off_below: 0.12 (prevents pump stall at low duty)"
          ],
          "ports_out": [
            {"id": "p_pf7", "label": "PF7 (PWM 200Hz)"},
            {"id": "p_pf9", "label": "PF9 (Aux Ctrl)"}
          ]
        }
      ]
    },
    {
      "id": "stg_pneuma",
      "header": "STAGE 2: PNEUMA REMOTE AIR UNIT",
      "blocks": [
        {
          "id": "blk_pump",
          "title": "Pneuma Pump & Driver Module",
          "subtitle": "Remote Stationary Air Source (Off-Gantry)",
          "badge": "PNEUMA",
          "style": "primary",
          "specs": [
            "• Eliminates heavy blower mass from moving X-beam",
            "• High static pressure overcomes tubing restriction",
            "• Intake filter + acoustic isolation mount"
          ],
          "ports_in": [
            {"id": "in_24v", "label": "24V Power"},
            {"id": "in_pf7", "label": "PF7 PWM"},
            {"id": "in_pf9", "label": "PF9 Aux"}
          ],
          "ports_out": [
            {"id": "out_6mm", "label": "6mm OD PTFE Trunk"}
          ]
        },
        {
          "id": "blk_splitter",
          "title": "6mm → Dual 5mm OD Y-Splitter",
          "subtitle": "Whip-Reduction Transition Manifold",
          "badge": "MANIFOLD",
          "style": "secondary",
          "specs": [
            "• Trunk: 6mm OD (4mm ID) low-loss supply line",
            "• Branches: Dual 5mm OD flexible umbilical lines",
            "• Minimizes gantry drag & umbilical whip at high Accel"
          ],
          "ports_in": [
            {"id": "in_trunk", "label": "6mm OD In"}
          ],
          "ports_out": [
            {"id": "out_5mm_L", "label": "5mm OD Left"},
            {"id": "out_5mm_R", "label": "5mm OD Right"}
          ]
        }
      ]
    },
    {
      "id": "stg_alembic",
      "header": "STAGE 3: ALEMBIC TOOLHEAD DELIVERY",
      "blocks": [
        {
          "id": "blk_alembic",
          "title": "Alembic Ultra-Light Toolhead",
          "subtitle": "Dual-Inlet Compressed Air Part Cooling",
          "badge": "TOOLHEAD",
          "style": "pass",
          "specs": [
            "• Dual 5mm OD push-to-connect / collet inlets",
            "• Symmetric high-velocity nozzle air curtain",
            "• M3x5x4mm Voron-spec heat-set inserts throughout",
            "• Zero CPAP blower pendulum weight on X-carriage"
          ],
          "ports_in": [
            {"id": "in_alembic_L", "label": "Left 5mm Inlet"},
            {"id": "in_alembic_R", "label": "Right 5mm Inlet"}
          ]
        }
      ]
    }
  ],
  "links": [
    {
      "from_port": "p_24v",
      "to_port": "in_24v",
      "label": "24V DC Bus",
      "style": "warn"
    },
    {
      "from_port": "p_pf7",
      "to_port": "in_pf7",
      "label": "PWM (PF7)",
      "style": "primary"
    },
    {
      "from_port": "p_pf9",
      "to_port": "in_pf9",
      "label": "Aux (PF9)",
      "style": "tertiary"
    },
    {
      "from_port": "out_6mm",
      "to_port": "in_trunk",
      "label": "6mm OD PTFE",
      "style": "secondary"
    },
    {
      "from_port": "out_5mm_L",
      "to_port": "in_alembic_L",
      "label": "5mm OD (L)",
      "style": "pass"
    },
    {
      "from_port": "out_5mm_R",
      "to_port": "in_alembic_R",
      "label": "5mm OD (R)",
      "style": "pass"
    }
  ],
  "callout_title": "CRITICAL ENGINEERING & ASSEMBLY NOTES",
  "callout_items": [
    "1. TUBING GEOMETRY: Run 6mm OD PTFE from the stationary Pneuma pump to the frame-mounted Y-splitter; run dual 5mm OD PTFE along the umbilical to Alembic to prevent X-beam whip.",
    "2. KLIPPER PWM: Set cycle_time: 0.005 and hardware_pwm: False on PF7 in Pneuma.cfg. Verify minimum start duty (off_below) to prevent brushless driver brownout."
  ],
  "footer_left": "Alchemical-3D Technical Diagram Studio • Blueprint: hardware_pinout_pneumatic",
  "footer_right": "Projects: Pneuma_Remote_Air × Alembic_Toolhead"
}
```
