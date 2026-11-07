#!/usr/bin/env python3
"""
Dual-Account Gmail MCP Server & OAuth Bootstrap CLI for Antigravity (`agy`).

Security, Non-Visible Inbox & Isolation Invariants:
1. Read + Drafts ONLY: Requests strictly `gmail.readonly` + `gmail.compose` and
   exposes zero `send`, `delete`, or `trash` tools to prevent prompt-injection
   exfiltration or unsupervised external emails.
2. Strict Account Partitioning: Isolates `personal` (`orleacock@gmail.com`) and
   `alchemical` (`orin@alchemical3d.net`) into separate `0600` non-symlink token
   files inside `0700` `~/.config/agy-gmail/` (outside all Git and Syncthing
   trees), verifies `0600`/`0700` modes and allowed OAuth scopes on every load,
   and verifies profile email parity during `--auth`.
3. Non-Visible Inbox & Draft Visibility Protection:
   - `gmail_status` surfaces hidden unread mail across Category tabs (`Updates`,
     `Promotions`, `Social`), skip-inbox/archived filters, `SPAM`, unsent `DRAFT`
     queues, and verified `Send-As` aliases.
   - `gmail_search_messages` supports `page_token` pagination and automatically
     checks `in:spam`/`in:trash` hit counts whenever a normal search returns `0`
     visible matches so vendor/customer replies in Spam never vanish silently.
   - `gmail_list_drafts` audits pending unsent drafts, and `gmail_create_draft`
     verifies `from_address` against live Gmail `sendAs` aliases (preventing
     silent fallback to private login addresses), warns on duplicate drafts in
     the same thread, and returns a direct clickable `gmail_web_url`.
4. Quarantine-Jailed Attachment Downloads: `gmail_save_attachment` writes ONLY
   inside `~/.cache/agy-gmail/attachments/` (`0700` dir, `0600` non-executable
   `O_EXCL` files), making it structurally impossible for email attachments to
   land inside `/home/orin/Projects/Alchemical3D/*`, dotfiles, or scripts.
"""

from __future__ import annotations

import argparse
import base64
from email.message import EmailMessage
from email.utils import getaddresses
from html.parser import HTMLParser
import json
import os
from pathlib import Path
import re
import stat
import sys
from typing import Any, Literal
from urllib.parse import quote

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from mcp.server import MCPServer

SCOPES: list[str] = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.compose",
]
ALLOWED_SCOPE_SET: frozenset[str] = frozenset(SCOPES)

ACCOUNT_SPECS: dict[str, dict[str, Any]] = {
    "personal": {
        "expected_email": "orleacock@gmail.com",
        "allowed_from_domains": ("gmail.com",),
        "token_filename": "token_personal.json",
        "label": "Personal Gmail (orleacock@gmail.com)",
    },
    "alchemical": {
        "expected_email": "orin@alchemical3d.net",
        "allowed_from_domains": ("alchemical3d.net",),
        "token_filename": "token_alchemical.json",
        "label": "Alchemical-3D Workspace (orin@alchemical3d.net)",
    },
}

AccountKey = Literal["personal", "alchemical"]
_SAFE_ID_RE = re.compile(r"^[A-Za-z0-9_-]{1,512}$")
_SAFE_SUBDIR_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]{0,63}$")
_SAFE_PAGETOKEN_RE = re.compile(r"^[A-Za-z0-9._=-]{1,512}$")


def _reject_symlink_chain(path: Path, label: str) -> None:
    cur = path
    while True:
        if cur.is_symlink():
            raise RuntimeError(f"Refusing symlink in {label} path: {cur}")
        if cur.parent == cur:
            break
        cur = cur.parent


def get_config_dir() -> Path:
    raw = os.environ.get("AGY_GMAIL_CONFIG_DIR", "~/.config/agy-gmail")
    expanded = Path(raw).expanduser()
    _reject_symlink_chain(expanded, "config directory")
    return expanded.resolve()


def get_attachment_jail_dir() -> Path:
    raw = os.environ.get("AGY_GMAIL_ATTACHMENT_DIR", "~/.cache/agy-gmail/attachments")
    expanded = Path(raw).expanduser()
    _reject_symlink_chain(expanded, "attachment directory")
    resolved = expanded.resolve()

    allowed_roots = (
        Path("~/.cache/agy-gmail").expanduser().resolve(),
        Path("/tmp").resolve(),
    )
    if not any(resolved == root or root in resolved.parents for root in allowed_roots):
        raise RuntimeError(
            f"Attachment jail {resolved} must reside strictly inside ~/.cache/agy-gmail or /tmp."
        )

    for forbidden_root in (
        Path("/home/orin/Projects").resolve(),
        Path("~/.ssh").expanduser().resolve(),
        Path("~/.gnupg").expanduser().resolve(),
        Path("~/.gemini").expanduser().resolve(),
        get_config_dir(),
    ):
        if (
            resolved == forbidden_root
            or forbidden_root in resolved.parents
            or resolved in forbidden_root.parents
        ):
            raise RuntimeError(
                f"Attachment jail {resolved} overlaps protected path {forbidden_root}."
            )
    return resolved


def ensure_secure_dir(path: Path) -> Path:
    _reject_symlink_chain(path, "secure directory")
    path.mkdir(parents=True, exist_ok=True)
    os.chmod(path, 0o700)
    st = os.lstat(path)
    if not stat.S_ISDIR(st.st_mode) or (st.st_mode & 0o077) != 0:
        raise RuntimeError(f"Directory {path} failed 0700 permission verification.")
    return path


def verify_secret_file_security(path: Path) -> None:
    if path.is_symlink():
        raise RuntimeError(f"Refusing symlinked credential file: {path}")
    if not path.exists():
        raise FileNotFoundError(f"Credential file not found: {path}")
    st = os.lstat(path)
    if stat.S_ISLNK(st.st_mode) or not stat.S_ISREG(st.st_mode):
        raise RuntimeError(f"Refusing symlink or non-regular credential file: {path}")
    if (st.st_mode & 0o077) != 0:
        raise RuntimeError(
            f"Insecure permissions {oct(st.st_mode & 0o777)} on {path}; expected 0600."
        )
    parent_st = os.lstat(path.parent)
    if stat.S_ISLNK(parent_st.st_mode) or (parent_st.st_mode & 0o077) != 0:
        raise RuntimeError(
            f"Insecure permissions {oct(parent_st.st_mode & 0o777)} on credential dir {path.parent}; expected 0700."
        )


def write_secret_json(path: Path, payload: str | dict[str, Any]) -> None:
    ensure_secure_dir(path.parent)
    if path.is_symlink():
        raise RuntimeError(f"Refusing to overwrite symlink: {path}")
    text = payload if isinstance(payload, str) else json.dumps(payload, indent=2) + "\n"
    tmp_path = path.with_suffix(path.suffix + f".{os.getpid()}.tmp")
    if tmp_path.is_symlink() or tmp_path.exists():
        tmp_path.unlink()
    fd = os.open(str(tmp_path), os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(text)
    except Exception:
        if tmp_path.exists():
            tmp_path.unlink()
        raise
    os.replace(str(tmp_path), str(path))
    os.chmod(path, 0o600)


def validate_account_key(account: str) -> dict[str, Any]:
    if account not in ACCOUNT_SPECS:
        valid = ", ".join(sorted(ACCOUNT_SPECS))
        raise ValueError(f"Unknown account {account!r}; expected one of: {valid}")
    return ACCOUNT_SPECS[account]


def validate_gmail_resource_id(value: str, field_name: str) -> str:
    cleaned = value.strip()
    if not _SAFE_ID_RE.match(cleaned):
        raise ValueError(f"Invalid {field_name}: {value!r}")
    return cleaned


def validate_page_token(value: str) -> str:
    cleaned = value.strip()
    if not cleaned:
        return ""
    if not _SAFE_PAGETOKEN_RE.match(cleaned):
        raise ValueError(f"Invalid page_token: {value!r}")
    return cleaned


def reject_header_newlines(value: str, field_name: str) -> str:
    if "\r" in value or "\n" in value or "\x00" in value:
        raise ValueError(f"Header injection characters rejected in {field_name}.")
    return value.strip()


def validate_recipient_list(raw: str, field_name: str, required: bool = False) -> str:
    cleaned = reject_header_newlines(raw, field_name)
    if not cleaned:
        if required:
            raise ValueError(f"Recipient field {field_name!r} is required.")
        return ""
    parsed = getaddresses([cleaned])
    if not parsed:
        raise ValueError(f"No valid email address found in {field_name!r}.")
    for _, addr in parsed:
        if "@" not in addr or " " in addr or addr.startswith("@") or addr.endswith("@"):
            raise ValueError(f"Malformed email address {addr!r} in {field_name!r}.")
    return cleaned


def validate_client_secret_file(path: Path, enforce_mode: bool = False) -> dict[str, Any]:
    if path.is_symlink():
        raise RuntimeError(f"Refusing symlinked OAuth client secret file: {path}")
    if enforce_mode:
        verify_secret_file_security(path)
    elif not path.is_file():
        raise FileNotFoundError(f"OAuth client secret file not found: {path}")
    data = json.loads(path.read_text(encoding="utf-8"))
    block = data.get("installed")
    if not isinstance(block, dict) or not block.get("client_id") or not block.get("client_secret"):
        raise ValueError(
            "Invalid OAuth JSON: expected a Google Cloud 'Desktop app' ('installed') client secret file."
        )
    return data


def verify_token_scopes(token_path: Path) -> None:
    raw = json.loads(token_path.read_text(encoding="utf-8"))
    scopes = raw.get("scopes")
    if not isinstance(scopes, list) or not scopes:
        raise RuntimeError(f"Missing or malformed 'scopes' list in {token_path}.")
    unexpected = set(scopes) - ALLOWED_SCOPE_SET
    if unexpected:
        raise RuntimeError(
            f"Over-privileged OAuth scopes rejected in {token_path}: {sorted(unexpected)}. "
            f"Allowed scopes: {sorted(ALLOWED_SCOPE_SET)}"
        )


def load_credentials(account: str) -> Credentials:
    spec = validate_account_key(account)
    cfg_dir = get_config_dir()
    token_path = cfg_dir / spec["token_filename"]
    if not token_path.is_symlink() and not token_path.exists():
        raise RuntimeError(
            f"Account {account!r} ({spec['expected_email']}) is not authenticated yet. "
            f"Run: {sys.executable} {Path(__file__).resolve()} --auth {account}"
        )
    verify_secret_file_security(token_path)
    verify_token_scopes(token_path)

    creds = Credentials.from_authorized_user_file(str(token_path), SCOPES)
    if not creds.valid:
        if creds.expired and creds.refresh_token:
            creds.refresh(Request())
            write_secret_json(token_path, creds.to_json())
        else:
            raise RuntimeError(
                f"Stored token for {account!r} is expired/invalid and cannot refresh. "
                f"Re-authenticate via: {sys.executable} {Path(__file__).resolve()} --auth {account}"
            )
    return creds


def get_gmail_service(account: str) -> Any:
    creds = load_credentials(account)
    return build("gmail", "v1", credentials=creds, cache_discovery=False)


class _HTMLTextExtractor(HTMLParser):
    """Extracts readable plain text from HTML emails while preserving table cell boundaries."""

    _BLOCK_TAGS = frozenset(("br", "p", "div", "li", "tr", "h1", "h2", "h3", "h4", "h5", "h6", "blockquote", "hr"))
    _CELL_TAGS = frozenset(("td", "th"))

    def __init__(self) -> None:
        super().__init__()
        self._chunks: list[str] = []
        self._skip_depth = 0
        self._in_row_cells = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in ("script", "style", "head"):
            self._skip_depth += 1
            return
        if self._skip_depth > 0:
            return
        if tag == "tr":
            self._in_row_cells = 0
            self._chunks.append("\n")
        elif tag in self._CELL_TAGS:
            if self._in_row_cells > 0:
                self._chunks.append("\t")
            self._in_row_cells += 1
        elif tag in self._BLOCK_TAGS:
            self._chunks.append("\n")

    def handle_endtag(self, tag: str) -> None:
        if tag in ("script", "style", "head") and self._skip_depth > 0:
            self._skip_depth -= 1

    def handle_data(self, data: str) -> None:
        if self._skip_depth == 0:
            self._chunks.append(data)

    def get_text(self) -> str:
        raw = "".join(self._chunks)
        raw = re.sub(r"[ \t]*\n[ \t]*", "\n", raw)
        return re.sub(r"\n{3,}", "\n\n", raw).strip()


def _decode_b64url(data: str) -> bytes:
    padded = data + "=" * (-len(data) % 4)
    return base64.urlsafe_b64decode(padded.encode("ascii"))


def _extract_headers(payload: dict[str, Any]) -> dict[str, str]:
    result: dict[str, str] = {}
    for item in payload.get("headers", []) or []:
        name = (item.get("name") or "").strip()
        val = (item.get("value") or "").strip()
        if name:
            result[name.lower()] = val
    return result


def _parse_mime_and_charset(raw_mime: str) -> tuple[str, str]:
    parts = [p.strip() for p in (raw_mime or "").split(";")]
    base_mime = parts[0].lower() if parts else ""
    charset = "utf-8"
    for param in parts[1:]:
        if "=" in param:
            k, v = param.split("=", 1)
            if k.strip().lower() == "charset" and v.strip().strip("\"'"):
                charset = v.strip().strip("\"'")
    return base_mime, charset


def _decode_part_text(b64_data: str, charset: str) -> str:
    raw = _decode_b64url(b64_data)
    try:
        return raw.decode(charset, errors="replace")
    except LookupError:
        return raw.decode("utf-8", errors="replace")


def _extract_body_and_attachments(
    message_id: str, payload: dict[str, Any]
) -> tuple[str, list[dict[str, Any]]]:
    attachments: list[dict[str, Any]] = []

    def walk(part: dict[str, Any]) -> list[str]:
        base_mime, charset = _parse_mime_and_charset(part.get("mimeType") or "")
        filename = (part.get("filename") or "").strip()
        body = part.get("body") or {}
        att_id = body.get("attachmentId")
        data = body.get("data")
        subparts = part.get("parts", []) or []

        if filename or att_id:
            attachments.append(
                {
                    "message_id": message_id,
                    "attachment_id": att_id or "",
                    "filename": filename or "unnamed_attachment",
                    "mime_type": base_mime or "application/octet-stream",
                    "size_bytes": int(body.get("size") or 0),
                }
            )
            # Stop recursion only on leaf binary attachments; continue walking nested message/rfc822 parts
            if att_id and not subparts:
                return []

        if data and base_mime == "text/plain":
            txt = _decode_part_text(data, charset).strip()
            return [txt] if txt else []
        if data and base_mime == "text/html":
            parser = _HTMLTextExtractor()
            parser.feed(_decode_part_text(data, charset))
            htxt = parser.get_text().strip()
            return [htxt] if htxt else []

        if base_mime == "multipart/alternative" and subparts:
            alt_plain: list[str] = []
            alt_html: list[str] = []
            alt_other: list[str] = []
            for sub in subparts:
                smime, _ = _parse_mime_and_charset(sub.get("mimeType") or "")
                segs = walk(sub)
                if smime == "text/plain":
                    alt_plain.extend(segs)
                elif smime in ("text/html", "multipart/related"):
                    alt_html.extend(segs)
                else:
                    alt_other.extend(segs)
            plain_joined = "\n\n".join(alt_plain).strip()
            html_joined = "\n\n".join(alt_html).strip()
            chosen: list[str] = []
            if plain_joined and html_joined and len(plain_joined) < 80 and len(html_joined) > max(200, len(plain_joined) * 4):
                chosen.append(f"{plain_joined}\n\n[HTML body fallback]\n{html_joined}")
            elif plain_joined:
                chosen.append(plain_joined)
            elif html_joined:
                chosen.append(html_joined)
            chosen.extend(alt_other)
            return chosen

        collected: list[str] = []
        for sub in subparts:
            collected.extend(walk(sub))
        return collected

    segments = walk(payload)
    body_text = "\n\n".join(s for s in segments if s)
    return body_text, attachments


def validate_from_address(
    account: str,
    from_address: str,
    verified_send_as: set[str] | None = None,
) -> tuple[str, str]:
    """Validate optional From override against domain rules and live Gmail sendAs aliases."""
    spec = validate_account_key(account)
    cleaned = reject_header_newlines(from_address, "from_address")
    if not cleaned:
        return "", ""
    parsed = getaddresses([cleaned])
    if len(parsed) != 1 or "," in cleaned or ";" in cleaned:
        raise ValueError(f"from_address must contain exactly one email address: {from_address!r}")
    _, addr = parsed[0]
    if "@" not in addr or " " in addr or addr.startswith("@") or addr.endswith("@"):
        raise ValueError(f"Invalid from_address {from_address!r}")
    addr_lower = addr.lower()
    domain = addr_lower.rsplit("@", 1)[1]
    if domain not in spec["allowed_from_domains"]:
        raise ValueError(
            f"from_address {addr!r} is not permitted for account={account!r} "
            f"(allowed domain(s): {spec['allowed_from_domains']})."
        )
    if verified_send_as is not None and addr_lower not in verified_send_as:
        raise ValueError(
            f"from_address {addr!r} is NOT registered as a verified Send-As alias on {spec['expected_email']!r} "
            f"(active aliases: {sorted(verified_send_as)}). Gmail would silently overwrite From: back to "
            f"{spec['expected_email']!r}; configure the alias in Gmail Settings -> Accounts first."
        )
    return cleaned, addr_lower


def fetch_verified_send_as_set(svc: Any) -> set[str]:
    entries = svc.users().settings().sendAs().list(userId="me").execute().get("sendAs", []) or []
    allowed: set[str] = set()
    for item in entries:
        email_addr = (item.get("sendAsEmail") or "").strip().lower()
        status = (item.get("verificationStatus") or "").lower()
        if email_addr and (item.get("isPrimary") or status in ("accepted", "")):
            allowed.add(email_addr)
    return allowed


def build_gmail_web_urls(account_email: str, thread_id: str = "", draft_message_id: str = "") -> dict[str, str]:
    auth_param = quote(account_email, safe="@.")
    base = f"https://mail.google.com/mail/u/?authuser={auth_param}"
    urls: dict[str, str] = {"drafts_folder_url": f"{base}#drafts"}
    if thread_id:
        urls["thread_url"] = f"{base}#all/{thread_id}"
    if draft_message_id:
        urls["draft_compose_url"] = f"{base}#drafts?compose={draft_message_id}"
    return urls


def build_draft_payload(
    *,
    account: str,
    to: str,
    subject: str,
    body: str,
    cc: str = "",
    bcc: str = "",
    from_address: str = "",
    thread_id: str = "",
    in_reply_to: str = "",
    references: str = "",
    verified_send_as: set[str] | None = None,
) -> dict[str, Any]:
    validate_account_key(account)
    clean_to = validate_recipient_list(to, "to", required=True)
    clean_cc = validate_recipient_list(cc, "cc", required=False)
    clean_bcc = validate_recipient_list(bcc, "bcc", required=False)
    validated_from, _ = validate_from_address(account, from_address, verified_send_as=verified_send_as)
    clean_subject = reject_header_newlines(subject, "subject")
    clean_reply_to = reject_header_newlines(in_reply_to, "in_reply_to")
    clean_refs = reject_header_newlines(references, "references")
    clean_thread_id = validate_gmail_resource_id(thread_id, "thread_id") if thread_id.strip() else ""

    msg = EmailMessage()
    msg["To"] = clean_to
    if validated_from:
        msg["From"] = validated_from
    if clean_cc:
        msg["Cc"] = clean_cc
    if clean_bcc:
        msg["Bcc"] = clean_bcc

    final_subject = clean_subject
    if clean_reply_to and final_subject and not final_subject.lower().startswith("re:"):
        final_subject = f"Re: {final_subject}"
    msg["Subject"] = final_subject

    if clean_reply_to:
        msg["In-Reply-To"] = clean_reply_to
        refs = f"{clean_refs} {clean_reply_to}".strip() if clean_refs else clean_reply_to
        msg["References"] = refs

    msg.set_content(body)
    encoded = base64.urlsafe_b64encode(msg.as_bytes()).decode("ascii")
    message_obj: dict[str, Any] = {"raw": encoded}
    if clean_thread_id:
        message_obj["threadId"] = clean_thread_id
    return {"message": message_obj}


def resolve_quarantined_attachment_path(filename: str, subdir: str = "") -> Path:
    if "\x00" in filename or "\r" in filename or "\n" in filename:
        raise ValueError("Control characters rejected in attachment filename.")
    safe_name = os.path.basename(filename.strip())
    safe_name = safe_name.lstrip(".")
    if not safe_name or safe_name in (".", ".."):
        raise ValueError(f"Invalid attachment filename: {filename!r}")

    jail_root = ensure_secure_dir(get_attachment_jail_dir())
    target_dir = jail_root
    if subdir.strip():
        clean_sub = subdir.strip()
        if not _SAFE_SUBDIR_RE.match(clean_sub):
            raise ValueError(
                f"Invalid attachment subdir {subdir!r}; must match ^[A-Za-z0-9][A-Za-z0-9_-]{{0,63}}$ inside quarantine jail."
            )
        candidate_dir = jail_root / clean_sub
        if candidate_dir.is_symlink():
            raise RuntimeError(f"Refusing symlinked attachment subdir: {candidate_dir}")
        target_dir = ensure_secure_dir(candidate_dir)

    if os.path.commonpath([str(jail_root), str(target_dir)]) != str(jail_root):
        raise ValueError("Attachment destination escaped quarantine jail.")

    stem, ext = os.path.splitext(safe_name)
    for idx in range(0, 1000):
        candidate_name = safe_name if idx == 0 else f"{stem}_{idx}{ext}"
        dest = target_dir / candidate_name
        if not dest.is_symlink() and not dest.exists():
            if dest.resolve().parent != target_dir:
                raise ValueError("Path traversal blocked in attachment destination.")
            return dest
    raise RuntimeError("Too many attachment filename collisions in quarantine directory.")


mcp = MCPServer(
    name="gmail",
    instructions=(
        "Dual-account Gmail connector for Orin's workstation ('personal' = orleacock@gmail.com, "
        "'alchemical' = orin@alchemical3d.net). Strictly read + create-draft only (never sends or deletes); "
        "surfaces non-visible mail (Category tabs, skip-inbox filters, Spam counts, unsent Drafts) and "
        "saves attachments exclusively into ~/.cache/agy-gmail/attachments/ quarantine."
    ),
)


@mcp.tool()
def gmail_status() -> dict[str, Any]:
    """Check OAuth readiness AND non-visible inbox radar (Categories, Skip-Inbox unread, Spam, unsent Drafts, Send-As aliases)."""
    cfg_dir = get_config_dir()
    secret_path = cfg_dir / "client_secret.json"
    secret_ok = False
    if not secret_path.is_symlink() and secret_path.exists():
        try:
            validate_client_secret_file(secret_path, enforce_mode=True)
            secret_ok = True
        except Exception:
            secret_ok = False
    accounts_out: dict[str, Any] = {}
    radar_labels = (
        "INBOX",
        "UNREAD",
        "DRAFT",
        "SPAM",
        "CATEGORY_PERSONAL",
        "CATEGORY_UPDATES",
        "CATEGORY_PROMOTIONS",
        "CATEGORY_SOCIAL",
    )
    for key, spec in ACCOUNT_SPECS.items():
        tok_path = cfg_dir / spec["token_filename"]
        entry: dict[str, Any] = {
            "expected_email": spec["expected_email"],
            "token_present": (not tok_path.is_symlink()) and tok_path.is_file(),
            "ready": False,
        }
        if entry["token_present"]:
            try:
                svc = get_gmail_service(key)
                prof = svc.users().getProfile(userId="me").execute()
                entry["authenticated_email"] = prof.get("emailAddress")
                entry["messages_total"] = prof.get("messagesTotal")
                entry["threads_total"] = prof.get("threadsTotal")
                entry["ready"] = prof.get("emailAddress", "").lower() == spec["expected_email"].lower()

                visibility: dict[str, Any] = {}
                for lid in radar_labels:
                    try:
                        lb = svc.users().labels().get(userId="me", id=lid).execute()
                        visibility[lid] = {
                            "messages_total": lb.get("messagesTotal", 0),
                            "messages_unread": lb.get("messagesUnread", 0),
                        }
                    except Exception:
                        visibility[lid] = None
                skipped = (
                    svc.users()
                    .messages()
                    .list(userId="me", q="is:unread -in:inbox -in:spam -in:trash", maxResults=5)
                    .execute()
                )
                visibility["unread_outside_inbox_estimate"] = skipped.get("resultSizeEstimate", 0)
                entry["visibility_radar"] = visibility
                entry["verified_send_as_aliases"] = sorted(fetch_verified_send_as_set(svc))
            except Exception as exc:
                entry["error"] = str(exc)
        accounts_out[key] = entry
    return {
        "config_dir": str(cfg_dir),
        "attachment_quarantine_dir": str(get_attachment_jail_dir()),
        "client_secret_present": secret_ok,
        "mode": "read_and_draft_only",
        "accounts": accounts_out,
    }


@mcp.tool()
def gmail_search_messages(
    account: AccountKey,
    query: str = "",
    max_results: int = 15,
    page_token: str = "",
    include_spam_trash: bool = False,
) -> dict[str, Any]:
    """Search messages in 'personal' or 'alchemical' with pagination and automatic Spam/Trash miss detection."""
    svc = get_gmail_service(account)
    capped = max(1, min(int(max_results), 50))
    clean_pt = validate_page_token(page_token)
    list_kwargs: dict[str, Any] = {
        "userId": "me",
        "q": query,
        "maxResults": capped,
        "includeSpamTrash": include_spam_trash,
    }
    if clean_pt:
        list_kwargs["pageToken"] = clean_pt

    resp = svc.users().messages().list(**list_kwargs).execute()
    items = resp.get("messages", []) or []
    results: list[dict[str, Any]] = []
    for stub in items:
        msg = (
            svc.users()
            .messages()
            .get(
                userId="me",
                id=stub["id"],
                format="metadata",
                metadataHeaders=["Date", "From", "To", "Cc", "Subject"],
            )
            .execute()
        )
        hdrs = _extract_headers(msg.get("payload") or {})
        results.append(
            {
                "id": msg.get("id"),
                "thread_id": msg.get("threadId"),
                "date": hdrs.get("date", ""),
                "from": hdrs.get("from", ""),
                "to": hdrs.get("to", ""),
                "cc": hdrs.get("cc", ""),
                "subject": hdrs.get("subject", ""),
                "snippet": msg.get("snippet", ""),
                "labels": msg.get("labelIds", []),
            }
        )

    next_token = resp.get("nextPageToken", "")
    out: dict[str, Any] = {
        "account": account,
        "query": query,
        "count": len(results),
        "result_size_estimate": resp.get("resultSizeEstimate", len(results)),
        "has_more": bool(next_token),
        "next_page_token": next_token,
        "messages": results,
    }

    # Non-visible Archive/Skip-Inbox & Spam/Trash miss detector when visible search returns 0 hits
    if not results and query.strip() and not clean_pt:
        inbox_clause_re = re.compile(r"(?<![-\w])(?:in|label):inbox\b", re.IGNORECASE)
        had_inbox_filter = bool(inbox_clause_re.search(query))
        broad_query = inbox_clause_re.sub("", query).strip() if had_inbox_filter else query.strip()
        notices: list[str] = []

        if had_inbox_filter and broad_query:
            archive_probe = (
                svc.users()
                .messages()
                .list(userId="me", q=f"({broad_query}) -in:inbox", includeSpamTrash=False, maxResults=5)
                .execute()
            )
            outside_hits = len(archive_probe.get("messages", []) or [])
            out["hidden_outside_inbox_matches"] = outside_hits
            if outside_hits > 0:
                notices.append(
                    f"{outside_hits}+ match(es) exist outside INBOX (skip-inbox filter or archived); re-run without 'in:inbox'."
                )

        if not include_spam_trash and broad_query:
            spam_probe = (
                svc.users()
                .messages()
                .list(
                    userId="me",
                    q=f"({broad_query}) (in:spam OR in:trash)",
                    includeSpamTrash=True,
                    maxResults=5,
                )
                .execute()
            )
            hidden_hits = len(spam_probe.get("messages", []) or [])
            out["hidden_spam_or_trash_matches"] = hidden_hits
            if hidden_hits > 0:
                notices.append(
                    f"{hidden_hits}+ match(es) exist inside SPAM/TRASH; re-run without 'in:inbox' and with include_spam_trash=True to inspect safely."
                )

        if notices:
            out["visibility_notice"] = "0 matches for current filter, but " + " ".join(notices)
    return out


@mcp.tool()
def gmail_list_drafts(
    account: AccountKey,
    max_results: int = 20,
) -> dict[str, Any]:
    """List pending unsent Gmail Drafts in 'personal' or 'alchemical' so staged replies never get lost."""
    spec = validate_account_key(account)
    svc = get_gmail_service(account)
    capped = max(1, min(int(max_results), 50))
    resp = svc.users().drafts().list(userId="me", maxResults=capped).execute()
    draft_stubs = resp.get("drafts", []) or []
    drafts_out: list[dict[str, Any]] = []
    for stub in draft_stubs:
        did = stub.get("id", "")
        detail = svc.users().drafts().get(userId="me", id=did, format="metadata").execute()
        msg = detail.get("message") or {}
        hdrs = _extract_headers(msg.get("payload") or {})
        mid = msg.get("id", "")
        tid = msg.get("threadId", "")
        urls = build_gmail_web_urls(spec["expected_email"], thread_id=tid, draft_message_id=mid)
        drafts_out.append(
            {
                "draft_id": did,
                "message_id": mid,
                "thread_id": tid,
                "date": hdrs.get("date", ""),
                "from": hdrs.get("from", ""),
                "to": hdrs.get("to", ""),
                "subject": hdrs.get("subject", ""),
                "snippet": msg.get("snippet", ""),
                "gmail_web_urls": urls,
            }
        )
    return {
        "account": account,
        "count": len(drafts_out),
        "drafts": drafts_out,
    }


@mcp.tool()
def gmail_get_thread(
    account: AccountKey,
    thread_id: str,
    max_body_chars: int = 12000,
) -> dict[str, Any]:
    """Fetch full message bodies, headers, and attachment metadata for a Gmail thread_id."""
    spec = validate_account_key(account)
    clean_tid = validate_gmail_resource_id(thread_id, "thread_id")
    svc = get_gmail_service(account)
    thread = svc.users().threads().get(userId="me", id=clean_tid, format="full").execute()
    messages_out: list[dict[str, Any]] = []
    char_cap = max(500, min(int(max_body_chars), 50000))
    for msg in thread.get("messages", []) or []:
        payload = msg.get("payload") or {}
        hdrs = _extract_headers(payload)
        body_text, attachments = _extract_body_and_attachments(msg.get("id", ""), payload)
        total_chars = len(body_text)
        truncated = total_chars > char_cap
        if truncated:
            body_text = body_text[:char_cap] + f"\n...[truncated at {char_cap}/{total_chars} chars]..."
        messages_out.append(
            {
                "id": msg.get("id"),
                "date": hdrs.get("date", ""),
                "from": hdrs.get("from", ""),
                "to": hdrs.get("to", ""),
                "cc": hdrs.get("cc", ""),
                "subject": hdrs.get("subject", ""),
                "rfc_message_id": hdrs.get("message-id", ""),
                "labels": msg.get("labelIds", []),
                "body": body_text,
                "body_total_chars": total_chars,
                "body_truncated": truncated,
                "attachments": attachments,
            }
        )
    tid = thread.get("id", clean_tid)
    return {
        "account": account,
        "thread_id": tid,
        "thread_web_url": build_gmail_web_urls(spec["expected_email"], thread_id=tid).get("thread_url", ""),
        "message_count": len(messages_out),
        "messages": messages_out,
    }


@mcp.tool()
def gmail_save_attachment(
    account: AccountKey,
    message_id: str,
    attachment_id: str,
    filename: str,
    subdir: str = "",
) -> dict[str, Any]:
    """Download a Gmail attachment strictly into ~/.cache/agy-gmail/attachments/[subdir] (0600, O_EXCL non-overwriting)."""
    clean_mid = validate_gmail_resource_id(message_id, "message_id")
    clean_aid = validate_gmail_resource_id(attachment_id, "attachment_id")
    dest = resolve_quarantined_attachment_path(filename, subdir=subdir)
    svc = get_gmail_service(account)
    att = (
        svc.users()
        .messages()
        .attachments()
        .get(userId="me", messageId=clean_mid, id=clean_aid)
        .execute()
    )
    raw_bytes = _decode_b64url(att.get("data", ""))
    fd = os.open(str(dest), os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, "wb") as handle:
        handle.write(raw_bytes)
    return {
        "account": account,
        "saved_path": str(dest),
        "size_bytes": len(raw_bytes),
    }


@mcp.tool()
def gmail_create_draft(
    account: AccountKey,
    to: str,
    subject: str,
    body: str,
    cc: str = "",
    bcc: str = "",
    reply_to_message_id: str = "",
    from_address: str = "",
    replace_draft_id: str = "",
) -> dict[str, Any]:
    """Create or update a Gmail Draft (NEVER sends live email). Verifies Send-As aliases and returns direct Gmail Web URLs."""
    spec = validate_account_key(account)
    svc = get_gmail_service(account)
    verified_aliases = fetch_verified_send_as_set(svc) if from_address.strip() else None

    thread_id = ""
    in_reply_to = ""
    references = ""
    thread_in_inbox = True
    risky_reply_labels: list[str] = []
    if reply_to_message_id.strip():
        clean_rmid = validate_gmail_resource_id(reply_to_message_id, "reply_to_message_id")
        orig = (
            svc.users()
            .messages()
            .get(
                userId="me",
                id=clean_rmid,
                format="metadata",
                metadataHeaders=["Message-ID", "References", "Subject"],
            )
            .execute()
        )
        thread_id = orig.get("threadId", "")
        orig_labels = set(orig.get("labelIds") or [])
        thread_in_inbox = "INBOX" in orig_labels
        risky_reply_labels = sorted(orig_labels & {"SPAM", "TRASH"})
        hdrs = _extract_headers(orig.get("payload") or {})
        in_reply_to = hdrs.get("message-id", "")
        references = hdrs.get("references", "")
        if not subject.strip():
            subject = hdrs.get("subject", "")

    draft_body = build_draft_payload(
        account=account,
        to=to,
        subject=subject,
        body=body,
        cc=cc,
        bcc=bcc,
        from_address=from_address,
        thread_id=thread_id,
        in_reply_to=in_reply_to,
        references=references,
        verified_send_as=verified_aliases,
    )

    existing_same_thread: list[str] = []
    if thread_id and not replace_draft_id.strip():
        cur_drafts = svc.users().drafts().list(userId="me", maxResults=50).execute().get("drafts", []) or []
        for dstub in cur_drafts:
            dmsg = dstub.get("message") or {}
            if dmsg.get("threadId") == thread_id and dstub.get("id"):
                existing_same_thread.append(dstub["id"])

    if replace_draft_id.strip():
        clean_did = validate_gmail_resource_id(replace_draft_id, "replace_draft_id")
        saved = svc.users().drafts().update(userId="me", id=clean_did, body=draft_body).execute()
        action_status = "DRAFT_UPDATED_NOT_SENT"
    else:
        saved = svc.users().drafts().create(userId="me", body=draft_body).execute()
        action_status = "DRAFT_CREATED_NOT_SENT"

    msg_meta = saved.get("message") or {}
    mid = msg_meta.get("id", "")
    tid = msg_meta.get("threadId", thread_id)
    urls = build_gmail_web_urls(spec["expected_email"], thread_id=tid, draft_message_id=mid)

    warnings: list[str] = []
    if risky_reply_labels:
        warnings.append(
            f"SECURITY WARNING: Target message carries {risky_reply_labels}; verify sender authenticity before sending any reply."
        )
    if existing_same_thread:
        warnings.append(
            f"Thread {tid} already had {len(existing_same_thread)} unsent draft(s) ({existing_same_thread}); "
            "pass replace_draft_id to update an existing draft instead of stacking duplicates."
        )
    if reply_to_message_id.strip() and not thread_in_inbox:
        warnings.append(
            "Target conversation is outside INBOX (archived/filtered/spam); open draft_compose_url or Gmail's Drafts folder directly to review and send."
        )

    result: dict[str, Any] = {
        "account": account,
        "status": action_status,
        "draft_id": saved.get("id"),
        "message_id": mid,
        "thread_id": tid,
        "to": to,
        "subject": subject,
        "gmail_web_urls": urls,
    }
    if warnings:
        result["visibility_warnings"] = warnings
    return result


def cli_import_client_secret(src_path: str) -> int:
    src = Path(src_path).expanduser().resolve()
    data = validate_client_secret_file(src, enforce_mode=False)
    dest = get_config_dir() / "client_secret.json"
    write_secret_json(dest, data)
    print(f"[OK] Installed validated Desktop OAuth client secret -> {dest} (0600)")
    return 0


def cli_authenticate(account: str, open_browser: bool = True) -> int:
    spec = validate_account_key(account)
    cfg_dir = ensure_secure_dir(get_config_dir())
    secret_path = cfg_dir / "client_secret.json"
    validate_client_secret_file(secret_path, enforce_mode=True)

    print(f"=== Authenticating {spec['label']} ===")
    print(f"Please sign in and approve ONLY as: {spec['expected_email']}")
    flow = InstalledAppFlow.from_client_secrets_file(str(secret_path), SCOPES)
    creds = flow.run_local_server(
        port=0,
        open_browser=open_browser,
        access_type="offline",
        prompt="consent",
        login_hint=spec["expected_email"],
    )
    svc = build("gmail", "v1", credentials=creds, cache_discovery=False)
    profile = svc.users().getProfile(userId="me").execute()
    actual_email = (profile.get("emailAddress") or "").strip()
    if actual_email.lower() != spec["expected_email"].lower():
        print(
            f"[ERROR] Identity mismatch! Expected {spec['expected_email']!r}, "
            f"but Google returned {actual_email!r}. Refusing to save cross-bound token.",
            file=sys.stderr,
        )
        return 2

    token_path = cfg_dir / spec["token_filename"]
    write_secret_json(token_path, creds.to_json())
    print(f"[OK] Verified {actual_email} and saved isolated token -> {token_path} (0600)")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Antigravity Dual-Account Gmail MCP Server & OAuth CLI")
    parser.add_argument("--status", action="store_true", help="Print JSON health/visibility status and exit")
    parser.add_argument("--import-client-secret", metavar="JSON_PATH", help="Validate and install Google Desktop OAuth JSON")
    parser.add_argument("--auth", choices=sorted(ACCOUNT_SPECS), help="Run interactive browser OAuth login for an account")
    parser.add_argument("--no-browser", action="store_true", help="Print OAuth URL without auto-opening browser")
    args = parser.parse_args(argv)

    if args.import_client_secret:
        return cli_import_client_secret(args.import_client_secret)
    if args.auth:
        return cli_authenticate(args.auth, open_browser=not args.no_browser)
    if args.status:
        print(json.dumps(gmail_status(), indent=2))
        return 0

    mcp.run(transport="stdio")
    return 0


if __name__ == "__main__":
    sys.exit(main())
