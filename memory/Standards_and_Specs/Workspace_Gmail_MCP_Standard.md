---
title: "Workspace Dual-Account Gmail MCP & Non-Visible Inbox Safety Standard"
entity: "Orin_Workstation"
compartment: "private"
last_synced: "2026-11-11"
---

# 📬 Workspace Dual-Account Gmail MCP & Non-Visible Inbox Safety Standard

Referenced by [`Standards_Index.md`](Standards_Index.md) and enforced by `/home/orin/Projects/Engineering/scripts/gmail_mcp/gmail-workspace-assistant/SKILL.md` (`~/.gemini/config/skills/gmail-workspace-assistant/SKILL.md`) and `/home/orin/Projects/Engineering/scripts/gmail_mcp/gmail_mcp_server.py`.

---

## 1. Dual-Account Identity & Verified Alias Bindings

- **MCP Server Path**: `/home/orin/Projects/Engineering/scripts/gmail_mcp/gmail_mcp_server.py`
- **Isolated Virtualenv**: `/home/orin/.local/share/agy-gmail/venv/bin/python`
- **Registered MCP Config**: `/home/orin/.gemini/config/mcp_config.json` (`ServerName: "gmail"`)
- **Account Partitioning (`~/.config/agy-gmail/`, `0700` dir / `0600` non-symlink tokens)**:
  1. **`personal`** $\rightarrow$ `orleacock@gmail.com` (`~/.config/agy-gmail/token_personal.json`)
     - Verified Send-As Aliases: `["orleacock@gmail.com"]`
  2. **`alchemical`** $\rightarrow$ `orin@alchemical3d.net` (`~/.config/agy-gmail/token_alchemical.json`)
     - Verified Send-As Aliases: `["orin@alchemical3d.net", "we@alchemical3d.net"]`

---

## 2. Hardened Read + Drafts Safety Invariants

1. **Zero Send / Delete Surface**:
   - Requests strictly `gmail.readonly` + `gmail.compose` and exposes only 6 safe tools: `gmail_status`, `gmail_search_messages`, `gmail_list_drafts`, `gmail_get_thread`, `gmail_save_attachment`, and `gmail_create_draft`.
   - Zero `messages.send`, `drafts.send`, `trash`, or `delete` endpoints exist.
2. **Non-Visible Inbox & Draft Accountability (`visibility_radar`)**:
   - Always inspect `gmail_status` (`visibility_radar`: `CATEGORY_UPDATES`, `CATEGORY_PROMOTIONS`, `CATEGORY_SOCIAL`, `unread_outside_inbox_estimate` from skip-inbox filters, `SPAM` unread, and `DRAFT` counts) plus `gmail_list_drafts` when triaging an inbox.
   - When `gmail_search_messages` returns `0` visible matches, check the returned skip-inbox/archived and `SPAM`/`TRASH` probe counts and paginate via `page_token` when needed.
3. **Verified Alias & Draft-Only Outbound Safety (`gmail_create_draft`)**:
   - Never pass an unverified `from_address` to `gmail_create_draft` (preventing silent Gmail fallback to a private login address).
   - Use `replace_draft_id` when updating an existing draft in a thread to avoid duplicate thread drafts, and always surface clickable `gmail_web_urls` (`draft_compose_url`, `thread_url`) plus any `visibility_warnings`.
4. **Quarantine-Jailed Attachment Downloads (`~/.cache/agy-gmail/attachments/`)**:
   - All attachments download strictly as `0600` non-executable `O_EXCL` files inside `~/.cache/agy-gmail/attachments/`. Never copy email attachments directly into `/home/orin/Projects/Alchemical3D/*` or `/home/orin/Projects/Engineering/*` without explicit user review in chat.
