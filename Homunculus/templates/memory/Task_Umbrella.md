---
title: "{{ENTITY}} — Domain Task Umbrella"
entity: "{{ENTITY}}"
compartment: "{{COMPARTMENT}}"
note_type: "task_umbrella"
last_synced: "{{DATE}}"
---

# {{ENTITY}} — Active Engineering Task Umbrella (`Tasks/{{ENTITY_SAFE}}_Tasks.md`)

> **Single-Writer Task Governance (`entity: {{ENTITY}}`)**:
> - All active checkboxes (`- [ ]` / `- [x]`) for projects owned by **`{{ENTITY}}`** live exclusively in this file.
> - Project hub dossiers (`Projects/<Project>/<Project>.md`) link here and never duplicate checkboxes.
> - Tasks for other customers/entities must live in their own `Tasks/<Other_Entity>_Tasks.md` file to prevent cross-entity contamination.

---

<!-- AUTO-ROLLUP:START -->
**Progress Summary**: `0 / 1` Tasks Complete (`0.0%`) | Open: `1`
<!-- AUTO-ROLLUP:END -->

---

## Project Task Sections

<!-- AUTO-PROJECT-TASKS:START -->
### [`{{PROJECT}}`](../Projects/{{PROJECT}}/{{PROJECT}}.md) (`entity: {{ENTITY}}`)
- [ ] Complete initial domain telemetry sync (`sync_memory.py --sync-hardware` or `--sync-software --project {{PROJECT}}`) and review `Projects/{{PROJECT}}/Templates/`.
<!-- AUTO-PROJECT-TASKS:END -->
