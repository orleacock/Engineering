# Bionic Local Sidecar Routing

- Never call `127.0.0.1:1234`, Bionic AppImage, or `lms` lifecycle commands directly; route via `bionic-sidecar` MCP tools (`bionic_control`, `bionic_digest`, `bionic_repo_audit`, `bionic_stage_patch`) or `local_sidecar.py`, and include a 1-line `[BIONIC SIDECAR NOTICE]` whenever Bionic is opened, loaded, or called.
- Whenever a `<SYSTEM_MESSAGE>` reports `BIONIC_STATE=OFFLINE` or `BIONIC_STATE=UNLOADED`, you MUST include the `[BIONIC SIDECAR NOTICE]` banner in your user-facing response for that turn stating Bionic is not currently loaded/online and offering to turn it on remotely via `bionic_control` upon user confirmation.
- Auto-offload bounded digests & scratch patches (`invocation_tier="auto"`, `<=60s` ETA) when `ONLINE_READY`; use `<=90s` ETA on `[local]` / `[bionic]`.
- Never start/load Bionic without explicit user confirmation (`user_confirmed=True`); verify outputs before promoting past `Quarantine/`.
