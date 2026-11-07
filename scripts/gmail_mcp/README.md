# Dual-Account Gmail MCP Server (`gmail_mcp`)

Local `stdio` Model Context Protocol server connecting Antigravity (`agy`) to both workstation Google accounts using isolated OAuth 2.0 refresh tokens and strict read/draft safety boundaries:

- **`personal`** $\rightarrow$ `orleacock@gmail.com` (`~/.config/agy-gmail/token_personal.json`, `0600`)
- **`alchemical`** $\rightarrow$ `orin@alchemical3d.net` (`~/.config/agy-gmail/token_alchemical.json`, `0600`)

## Hardened Security & Non-Visible Inbox Safeguards
- **Scopes & Runtime Verification:** `gmail.readonly` + `gmail.compose` only; `load_credentials` verifies `0700` dir / `0600` non-symlink file modes and rejects any token carrying scopes outside the allowlist.
- **Zero Send / Delete Surface (6 Safe Tools):** Exposes `gmail_status`, `gmail_search_messages`, `gmail_list_drafts`, `gmail_get_thread`, `gmail_save_attachment`, and `gmail_create_draft` only—no `messages.send`, `drafts.send`, `trash`, or `delete` tool exists.
- **Non-Visible Inbox & MIME Fidelity:**
  - `gmail_status` reports `visibility_radar` counts across `INBOX`, `UNREAD`, `DRAFT`, `SPAM`, `CATEGORY_PERSONAL`/`UPDATES`/`PROMOTIONS`/`SOCIAL`, `unread_outside_inbox_estimate` (`is:unread -in:inbox -in:spam -in:trash`), and `verified_send_as_aliases`.
  - `gmail_search_messages` supports `page_token` pagination and automatically probes skip-inbox/archived mail + `SPAM`/`TRASH` whenever a search returns `0` visible matches.
  - `gmail_get_thread` preserves HTML table cell boundaries (`\t`), rescues HTML bodies when `text/plain` is an empty/stub placeholder, and walks nested `message/rfc822` forwarded messages without dropping outer text.
  - `gmail_list_drafts` + `gmail_create_draft` verify `from_address` against live `users.settings.sendAs.list()` aliases (blocking silent Gmail `From:` fallback), support `replace_draft_id` updates, warn on duplicate thread drafts / archived threads / `SPAM` targets, and return clickable `gmail_web_urls`.
- **Quarantine-Jailed Attachments (`~/.cache/agy-gmail/attachments/`):** `gmail_save_attachment` cannot write to arbitrary `output_dir` paths (preventing writes into `/home/orin/Projects/Alchemical3D/*`, `/home/orin/Projects/Engineering/*`, `~/.ssh`, or dotfiles); all downloads write as `0600` non-executable `O_EXCL` files inside `~/.cache/agy-gmail/attachments/`.
- **Cross-Account Bind & Header Injection Guards:** `--auth` verifies `users.getProfile().emailAddress` matches the target account before saving tokens; `gmail_create_draft` rejects CR/LF header injection, malformed recipients, and unverified `from_address` overrides.

## Setup & Bootstrap Commands

```bash
# 1. Create isolated virtualenv (outside Git & Syncthing):
python3 -m venv ~/.local/share/agy-gmail/venv
~/.local/share/agy-gmail/venv/bin/pip install -r /home/orin/Projects/Engineering/scripts/gmail_mcp/requirements.txt

# 2. Import downloaded Google Cloud 'Desktop app' OAuth JSON:
~/.local/share/agy-gmail/venv/bin/python /home/orin/Projects/Engineering/scripts/gmail_mcp/gmail_mcp_server.py \
  --import-client-secret ~/Downloads/client_secret.json

# 3. Authenticate each account (passes login_hint automatically, saves 0600 tokens):
~/.local/share/agy-gmail/venv/bin/python /home/orin/Projects/Engineering/scripts/gmail_mcp/gmail_mcp_server.py --auth personal
~/.local/share/agy-gmail/venv/bin/python /home/orin/Projects/Engineering/scripts/gmail_mcp/gmail_mcp_server.py --auth alchemical

# 4. Verify live status & register in Antigravity:
~/.local/share/agy-gmail/venv/bin/python /home/orin/Projects/Engineering/scripts/gmail_mcp/gmail_mcp_server.py --status
agy mcp add gmail ~/.local/share/agy-gmail/venv/bin/python /home/orin/Projects/Engineering/scripts/gmail_mcp/gmail_mcp_server.py
```
