#!/usr/bin/env python3
"""
Homunculus Declarative Data-Boundary, Entity-Decontamination & Credential Scanner.

Governed by: 1. Accuracy & Truth -> 2. Efficiency -> 3. Data Safety -> 4. Speed
Requires ONLY Python 3.10+ standard library (zero third-party pip packages).

Enforces multi-compartment firewalls across any repository using either:
  - Zero-Config Defaults (universal credential/key blocking, symlink-escape blocking,
    plus OS user-path and affiliate/clean-room decontamination in 'public'/'cleanroom' modes)
  - Declarative JSON Configuration (--config <path>, HOMUNCULUS_BOUNDARY_CONFIG, or .homunculus.json)

Modes:
  --repo <path> --staged
      Scans git staged index filenames, symlinks, and added diff lines (pre-commit hook mode).
  --repo <path> --push-stdin --remote-name <name> --remote-url <url>
      Verifies remote push target, commit author identity, outgoing tree filenames, and
      outgoing added diff lines from git pre-push stdin (pre-push hook mode).
  --repo <path> --worktree
      Scans all tracked + untracked non-ignored text files (UTF-8/16/32) and filenames in <path>.
  --all-in-root <dir>
      Runs --worktree across every git repository under <dir>.

=== DEVELOPER & AI NAVIGATION MAP ===
  Owning Module : Core Framework (`scripts/`)
  Callers       : `pre-commit.sh`, `pre-push.sh`, `git_pre_commit_boundary.sh`, `pre-commit-gate` (Stage Z3), `test_data_safety.py`, `test_adapters.py`
  Callees       : `homunculus_paths.py` (`CLEANROOM_FORBIDDEN_SHA256`, `ALLOWED_PLACEHOLDER_USERS`, `RE_POSIX_HOME`, `RE_WIN_USERS`)
  Contract      : `scripts/script_contracts.json` [`audit_data_boundary.py`]
  CLI Flags     : repo_pos, --repo, --config, --compartment, --staged, --push-stdin, --remote-name, --remote-url, --worktree, --all-in-root
  Symbol Index  (jump directly via read_file StartLine/EndLine):
    - class BoundaryPolicy (#L111-L125)              | def _reset_policy (#L131-L133)
    - def load_boundary_config (#L136-L235)          | def classify_compartment (#L238-L265)
    - def active_filename_rules (#L268-L274)         | def active_content_rules (#L277-L281)
    - def _should_block_os_user_paths (#L284-L287)   | def _should_block_affiliate_params (#L290-L293)
    - def _active_forbidden_hashes (#L296-L302)      | def redact_snippet (#L305-L315)
    - def scan_filenames (#L318-L326)                | def detect_text_encoding (#L329-L355)
    - def decode_candidate_text_bytes (#L358-L368)   | def scan_raw_bytes_complete (#L371-L407)
    - def check_symlink_escape (#L410-L418)          | def scan_git_tree_entries (#L421-L467)
    - def _find_forbidden_hash_token (#L470-L483)    | def scan_text_lines (#L486-L533)
    - def parse_unified_diff_added_lines (#L536-L560) | def scan_git_binary_flagged_blobs (#L563-L580)
    - def audit_staged (#L583-L606)                  | def verify_remote_and_author_for_push (#L609-L660)
    - def audit_push_stdin (#L663-L728)              | def audit_worktree (#L731-L767)
    - def main (#L770-L836)
=== END NAVIGATION MAP ===
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
from typing import Any, Iterable

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import homunculus_paths  # noqa: E402

ZERO_OID = "0" * 40
MAX_FULL_SCAN_BYTES = 16 * 1024 * 1024
STREAM_WINDOW_BYTES = 4 * 1024 * 1024
STREAM_OVERLAP_BYTES = 4096  # Strictly 4-byte aligned for UTF-16 / UTF-32
STEP_NUMERIC_ENTITY_RE = re.compile(r"^#\d+\s*=\s*[A-Z0-9_]+\([0-9.,E+\-\s#()*]*\);\s*$")

# Allowed placeholder usernames in documentation examples
ALLOWED_PLACEHOLDER_USERS: frozenset[str] = homunculus_paths.ALLOWED_PLACEHOLDER_USERS

# Universal Forbidden Filenames (All Compartments)
UNIVERSAL_BAD_FILENAME_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("oauth_client_secret_file", re.compile(r"(^|/)client_secret[^/]*\.json$", re.IGNORECASE)),
    ("oauth_token_file", re.compile(r"(^|/)token_[^/]*\.json$", re.IGNORECASE)),
    ("ssh_key_file", re.compile(r"(^|/)id_(ed25519|rsa|ecdsa|dsa)([^/.]*)$", re.IGNORECASE)),
    ("private_key_ext", re.compile(r"\.(pem|key|p12|pfx|keystore)$", re.IGNORECASE)),
    ("dotenv_secret_file", re.compile(r"(^|/)\.env(\.(?!example$|template$|sample$)[^/]+)?$", re.IGNORECASE)),
    ("chrome_devtools_port_file", re.compile(r"(^|/)DevToolsActivePort$")),
)

# Universal Secret Content Patterns (All Compartments)
UNIVERSAL_SECRET_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("google_oauth_client_secret", re.compile(r"GOCSPX-[A-Za-z0-9_-]{12,}")),
    ("google_oauth_refresh_token", re.compile(r"(?<![A-Za-z0-9])1//[0-9A-Za-z_-]{25,}")),
    ("google_oauth_access_token", re.compile(r"ya29\.[A-Za-z0-9._-]{25,}")),
    ("google_api_key", re.compile(r"\bAIza[0-9A-Za-z_-]{35}\b")),
    ("json_refresh_or_client_secret", re.compile(r'"(?:refresh_token|client_secret)"\s*:\s*"[A-Za-z0-9._/-]{12,}"')),
    ("github_pat_token", re.compile(r"(?:gh[pousr]_[A-Za-z0-9_]{25,}|github_pat_[A-Za-z0-9_]{25,})")),
    ("api_secret_key", re.compile(r"(?<![A-Za-z0-9])sk-(?:proj-|ant-)?[A-Za-z0-9_-]{24,}")),
    ("aws_access_key", re.compile(r"(?<![A-Z0-9])AKIA[0-9A-Z]{16}(?![A-Z0-9])")),
    ("slack_token", re.compile(r"xox[baprs]-[0-9A-Za-z-]{16,}")),
    ("pem_or_openssh_private_key", re.compile(r"-----BEGIN (?:[A-Z0-9 ]+ )?PRIVATE KEY-----")),
)

RE_POSIX_HOME = homunculus_paths.RE_POSIX_HOME
RE_WIN_USERS = homunculus_paths.RE_WIN_USERS
RE_AFFILIATE_PARAM = re.compile(r"(?:\?|&|\b)(?:affp|dt_id|aff_id|affiliate_id)=[A-Za-z0-9_-]+", re.IGNORECASE)
RE_CANDIDATE_TOKENS = re.compile(r"[A-Za-z0-9._@=-]{6,64}")

CLEANROOM_DEFAULT_BAD_FILENAMES: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("voice_corpus_export", re.compile(r"(^|/)corpus_inbox/(?!README\.md$|\.gitkeep$).+", re.IGNORECASE)),
)

# Upstream clean-room SHA-256 token digests (shared with homunculus_paths.py so zero plaintext identifiers exist in source)
CLEANROOM_FORBIDDEN_SHA256: frozenset[str] = homunculus_paths.CLEANROOM_FORBIDDEN_SHA256


class BoundaryPolicy:
    """Resolved compartment and rule policy for a repository."""

    def __init__(self) -> None:
        self.default_compartment: str = "cleanroom"
        self.compartments: dict[str, dict[str, Any]] = {}
        self.global_extra_content: list[tuple[str, re.Pattern[str]]] = []
        self.global_extra_filenames: list[tuple[str, re.Pattern[str]]] = []
        self.global_forbidden_hashes: set[str] = set()
        # Legacy flat config compatibility fields
        self.legacy_public_root: Path | None = None
        self.legacy_private_root: Path | None = None
        self.legacy_public_author: str = ""
        self.legacy_private_author: str = ""
        self.legacy_private_remote: str = ""


POLICY = BoundaryPolicy()


def _reset_policy() -> None:
    global POLICY
    POLICY = BoundaryPolicy()


def load_boundary_config(config_path: str | Path | None = None, repo_root: Path | None = None) -> None:
    """Load declarative compartment policy from --config, HOMUNCULUS_BOUNDARY_CONFIG, or .homunculus.json."""
    _reset_policy()
    cfg_file = config_path or os.environ.get("HOMUNCULUS_BOUNDARY_CONFIG", "").strip()
    if not cfg_file and repo_root is not None:
        for directory in (repo_root, *repo_root.parents):
            candidate = directory / ".homunculus.json"
            if candidate.is_file():
                try:
                    raw_ws = json.loads(candidate.read_text(encoding="utf-8"))
                    fw = raw_ws.get("compartment_firewall", {})
                    if isinstance(fw, dict):
                        for tok in fw.get("forbidden_tokens", []):
                            if str(tok).strip():
                                POLICY.global_forbidden_hashes.add(
                                    hashlib.sha256(str(tok).strip().lower().encode("utf-8")).hexdigest()
                                )
                        if fw.get("safety_config_path"):
                            cfg_file = str((directory / str(fw["safety_config_path"])).resolve())
                except (OSError, json.JSONDecodeError):
                    pass
                break

    if not cfg_file:
        return

    p = Path(cfg_file).expanduser().resolve()
    if not p.is_file():
        raise FileNotFoundError(f"Boundary config file not found: {p}")

    data: dict[str, Any] = json.loads(p.read_text(encoding="utf-8"))
    if "default_compartment" in data:
        POLICY.default_compartment = str(data["default_compartment"]).strip().lower()

    # Support flat legacy config keys as well as structured "compartments" map
    if "alchemical_root" in data or "public_root" in data:
        raw_pub = data.get("public_root") or data.get("alchemical_root")
        POLICY.legacy_public_root = Path(str(raw_pub)).expanduser().resolve()
    if "engineering_root" in data or "private_root" in data:
        raw_priv = data.get("private_root") or data.get("engineering_root")
        POLICY.legacy_private_root = Path(str(raw_priv)).expanduser().resolve()
    if "alchemical_author_email" in data or "public_author_email" in data:
        POLICY.legacy_public_author = str(data.get("public_author_email") or data.get("alchemical_author_email"))
    if "engineering_author_email" in data or "private_author_email" in data:
        POLICY.legacy_private_author = str(data.get("private_author_email") or data.get("engineering_author_email"))
    if "engineering_remote_url" in data or "private_remote_url" in data:
        POLICY.legacy_private_remote = str(data.get("private_remote_url") or data.get("engineering_remote_url"))

    for item in data.get("extra_content_patterns", []):
        if isinstance(item, dict) and "name" in item and "pattern" in item:
            POLICY.global_extra_content.append(
                (str(item["name"]), re.compile(str(item["pattern"]), re.IGNORECASE))
            )
    for item in data.get("extra_filename_patterns", []):
        if isinstance(item, dict) and "name" in item and "pattern" in item:
            POLICY.global_extra_filenames.append(
                (str(item["name"]), re.compile(str(item["pattern"]), re.IGNORECASE))
            )
    for tok in data.get("forbidden_tokens", []):
        if str(tok).strip():
            POLICY.global_forbidden_hashes.add(
                hashlib.sha256(str(tok).strip().lower().encode("utf-8")).hexdigest()
            )

    comps = data.get("compartments", {})
    if isinstance(comps, dict):
        for comp_name, comp_cfg in comps.items():
            if not isinstance(comp_cfg, dict):
                continue
            key = str(comp_name).strip().lower()
            c_patterns: list[tuple[str, re.Pattern[str]]] = []
            for item in comp_cfg.get("extra_content_patterns", []):
                if isinstance(item, dict) and "name" in item and "pattern" in item:
                    c_patterns.append((str(item["name"]), re.compile(str(item["pattern"]), re.IGNORECASE)))
            f_patterns: list[tuple[str, re.Pattern[str]]] = []
            for item in comp_cfg.get("extra_filename_patterns", []):
                if isinstance(item, dict) and "name" in item and "pattern" in item:
                    f_patterns.append((str(item["name"]), re.compile(str(item["pattern"]), re.IGNORECASE)))
            tok_hashes = {
                hashlib.sha256(str(t).strip().lower().encode("utf-8")).hexdigest()
                for t in comp_cfg.get("forbidden_tokens", [])
                if str(t).strip()
            }
            roots = [
                Path(str(r)).expanduser().resolve()
                for r in comp_cfg.get("root_paths", [])
                if str(r).strip()
            ]
            POLICY.compartments[key] = {
                "root_paths": roots,
                "expected_author_email": str(comp_cfg.get("expected_author_email", "")).strip(),
                "expected_remote_url": str(comp_cfg.get("expected_remote_url", "")).strip(),
                "expected_remote_url_template": str(comp_cfg.get("expected_remote_url_template", "")).strip(),
                "push_locked": bool(comp_cfg.get("push_locked", False)),
                "block_os_user_paths": bool(comp_cfg.get("block_os_user_paths", key in ("public", "cleanroom", "homunculus", "alchemical"))),
                "block_affiliate_params": bool(comp_cfg.get("block_affiliate_params", key in ("cleanroom", "homunculus"))),
                "extra_content_patterns": c_patterns,
                "extra_filename_patterns": f_patterns,
                "forbidden_hashes": tok_hashes,
            }


def classify_compartment(repo_root: Path, override: str | None = None) -> str:
    if override:
        return override.strip().lower()
    resolved = repo_root.resolve()

    # Check declarative compartments (most specific root_path match wins)
    best_match: tuple[int, str] | None = None
    for comp_name, comp_cfg in POLICY.compartments.items():
        for rpath in comp_cfg.get("root_paths", []):
            if resolved == rpath or rpath in resolved.parents:
                depth = len(rpath.parts)
                if best_match is None or depth > best_match[0]:
                    best_match = (depth, comp_name)
    if best_match is not None:
        return best_match[1]

    if POLICY.legacy_public_root is not None:
        if resolved == (POLICY.legacy_public_root / "Homunculus"):
            return "homunculus"
        if resolved.parent == POLICY.legacy_public_root or POLICY.legacy_public_root in resolved.parents:
            return "alchemical"
    if POLICY.legacy_private_root is not None:
        if resolved == POLICY.legacy_private_root or POLICY.legacy_private_root in resolved.parents:
            return "engineering"

    if (resolved / "HOMUNCULUS_START_HERE.md").is_file():
        return "homunculus"
    return POLICY.default_compartment


def active_filename_rules(compartment: str) -> list[tuple[str, re.Pattern[str]]]:
    rules = list(UNIVERSAL_BAD_FILENAME_PATTERNS) + list(POLICY.global_extra_filenames)
    comp_cfg = POLICY.compartments.get(compartment, {})
    rules.extend(comp_cfg.get("extra_filename_patterns", []))
    if compartment in ("homunculus", "cleanroom"):
        rules.extend(CLEANROOM_DEFAULT_BAD_FILENAMES)
    return rules


def active_content_rules(compartment: str) -> list[tuple[str, re.Pattern[str]]]:
    rules = list(UNIVERSAL_SECRET_PATTERNS) + list(POLICY.global_extra_content)
    comp_cfg = POLICY.compartments.get(compartment, {})
    rules.extend(comp_cfg.get("extra_content_patterns", []))
    return rules


def _should_block_os_user_paths(compartment: str) -> bool:
    if compartment in POLICY.compartments:
        return bool(POLICY.compartments[compartment].get("block_os_user_paths", False))
    return compartment in ("public", "cleanroom", "homunculus", "alchemical")


def _should_block_affiliate_params(compartment: str) -> bool:
    if compartment in POLICY.compartments:
        return bool(POLICY.compartments[compartment].get("block_affiliate_params", False))
    return compartment in ("cleanroom", "homunculus")


def _active_forbidden_hashes(compartment: str) -> set[str]:
    hashes = set(POLICY.global_forbidden_hashes)
    if compartment in POLICY.compartments:
        hashes.update(POLICY.compartments[compartment].get("forbidden_hashes", set()))
    if compartment in ("cleanroom", "homunculus"):
        hashes.update(CLEANROOM_FORBIDDEN_SHA256)
    return hashes


def redact_snippet(line: str, match: re.Match[str] | str) -> str:
    val = match.group(0) if isinstance(match, re.Match) else str(match)
    if len(val) > 10:
        masked = val[:4] + "...[REDACTED]..." + val[-3:]
    else:
        masked = val[:2] + "...[REDACTED]"
    if isinstance(match, re.Match):
        replaced = line[: match.start()] + masked + line[match.end() :]
    else:
        replaced = line.replace(val, masked)
    return replaced.strip()[:140]


def scan_filenames(paths: Iterable[str], compartment: str) -> list[str]:
    findings: list[str] = []
    rules = active_filename_rules(compartment)
    for rel in paths:
        norm = rel.replace("\\", "/").lstrip("./")
        for rule_name, rx in rules:
            if rx.search(norm):
                findings.append(f"[FILENAME:{rule_name}] Forbidden file path '{norm}' in compartment '{compartment}'.")
    return findings


def detect_text_encoding(sample: bytes) -> tuple[str | None, int]:
    """Return (encoding_name, bom_len) or (None, 0) for genuine binary."""
    if not sample:
        return ("utf-8", 0)
    if sample.startswith(b"\xff\xfe\x00\x00"):
        return ("utf-32-le", 4)
    if sample.startswith(b"\x00\x00\xfe\xff"):
        return ("utf-32-be", 4)
    if sample.startswith(b"\xff\xfe"):
        return ("utf-16-le", 2)
    if sample.startswith(b"\xfe\xff"):
        return ("utf-16-be", 2)

    head = sample[:8192]
    if b"\x00" not in head:
        return ("utf-8", 0)

    if len(head) >= 4:
        evens = head[0::2]
        odds = head[1::2]
        even_nulls = evens.count(0)
        odd_nulls = odds.count(0)
        if odd_nulls >= max(2, int(len(odds) * 0.4)) and even_nulls == 0:
            return ("utf-16-le", 0)
        if even_nulls >= max(2, int(len(evens) * 0.4)) and odd_nulls == 0:
            return ("utf-16-be", 0)
    return (None, 0)


def decode_candidate_text_bytes(raw: bytes) -> str | None:
    """Decode UTF-8, UTF-16 (with or without BOM), or UTF-32 text; return None for genuine binary."""
    enc, bom_len = detect_text_encoding(raw)
    if enc is None:
        return None
    body = raw[bom_len:]
    if enc.startswith("utf-32") and len(body) % 4 != 0:
        body = body[: len(body) - (len(body) % 4)]
    elif enc.startswith("utf-16") and len(body) % 2 != 0:
        body = body[:-1]
    return body.decode(enc, errors="replace")


def scan_raw_bytes_complete(rel: str, raw_blob: bytes, compartment: str) -> list[str]:
    """Scan an entire byte blob without skipping middle bytes, using 4-byte-aligned overlapping windows when > MAX_FULL_SCAN_BYTES."""
    if len(raw_blob) <= MAX_FULL_SCAN_BYTES:
        decoded = decode_candidate_text_bytes(raw_blob)
        if decoded is None:
            return []
        numbered = list(enumerate(decoded.splitlines(), start=1))
        return scan_text_lines(rel, numbered, compartment)

    enc, bom_len = detect_text_encoding(raw_blob[:8192])
    if enc is None:
        return []
    seen_hits: set[str] = set()
    findings: list[str] = []
    offset = bom_len
    total = len(raw_blob)
    step = STREAM_WINDOW_BYTES - STREAM_OVERLAP_BYTES
    line_base = 1
    while offset < total:
        chunk = raw_blob[offset : min(total, offset + STREAM_WINDOW_BYTES)]
        if enc.startswith("utf-32") and len(chunk) % 4 != 0:
            chunk = chunk[: len(chunk) - (len(chunk) % 4)]
        elif enc.startswith("utf-16") and len(chunk) % 2 != 0:
            chunk = chunk[:-1]
        decoded = chunk.decode(enc, errors="replace")
        lines = decoded.splitlines()
        numbered = list(enumerate(lines, start=line_base))
        for hit in scan_text_lines(rel, numbered, compartment):
            if hit not in seen_hits:
                seen_hits.add(hit)
                findings.append(hit)
        line_base += max(1, len(lines) - 32)
        if offset + STREAM_WINDOW_BYTES >= total:
            break
        offset += step
        offset -= (offset - bom_len) % 4
    return findings


def check_symlink_escape(rel_path: str, target_str: str) -> str | None:
    norm_rel = rel_path.replace("\\", "/").lstrip("./")
    if os.path.isabs(target_str):
        return f"[SYMLINK:external_escape] '{norm_rel}' -> '{target_str}' points to an absolute host path."
    rel_parent = os.path.dirname(norm_rel)
    joined = os.path.normpath(os.path.join(rel_parent, target_str))
    if joined == ".." or joined.startswith("../") or os.path.isabs(joined):
        return f"[SYMLINK:external_escape] '{norm_rel}' -> '{target_str}' escapes repository root."
    return None


def scan_git_tree_entries(
    repo_root: Path, treeish_or_index: str | None
) -> tuple[list[str], dict[str, str]]:
    """Inspect index or tree via NUL-delimited (-z) output; return (symlink_findings, mode100_oid_map)."""
    findings: list[str] = []
    blob_oids: dict[str, str] = {}
    if treeish_or_index is None:
        raw = subprocess.check_output(
            ["git", "-C", str(repo_root), "ls-files", "--stage", "-z"],
        ).decode("utf-8", errors="surrogateescape")
        entries = [e for e in raw.split("\x00") if e]
        for entry in entries:
            meta, rel_path = entry.split("\t", 1)
            parts = meta.split()
            mode, oid = parts[0], parts[1]
            if mode == "120000":
                target = subprocess.check_output(
                    ["git", "-C", str(repo_root), "cat-file", "-p", oid],
                    text=True,
                    errors="replace",
                ).strip()
                err = check_symlink_escape(rel_path, target)
                if err:
                    findings.append(err)
            elif mode.startswith("100"):
                blob_oids[rel_path] = oid
    else:
        raw = subprocess.check_output(
            ["git", "-C", str(repo_root), "ls-tree", "-r", "-z", treeish_or_index],
        ).decode("utf-8", errors="surrogateescape")
        entries = [e for e in raw.split("\x00") if e]
        for entry in entries:
            meta, rel_path = entry.split("\t", 1)
            parts = meta.split()
            mode, oid = parts[0], parts[2]
            if mode == "120000":
                target = subprocess.check_output(
                    ["git", "-C", str(repo_root), "cat-file", "-p", oid],
                    text=True,
                    errors="replace",
                ).strip()
                err = check_symlink_escape(rel_path, target)
                if err:
                    findings.append(err)
            elif mode.startswith("100"):
                blob_oids[rel_path] = oid
    return findings, blob_oids


def _find_forbidden_hash_token(line: str, active_hashes: set[str]) -> str | None:
    if not active_hashes:
        return None
    for match in RE_CANDIDATE_TOKENS.finditer(line):
        raw_tok = match.group(0).strip(".,:;()[]{}<>\"'")
        candidates = {raw_tok.lower()}
        if "/" in raw_tok:
            candidates.update(part.lower() for part in raw_tok.split("/") if len(part) >= 6)
        if "=" in raw_tok and "?" in raw_tok:
            candidates.update(part.lower() for part in raw_tok.split("?") if len(part) >= 6)
        for cand in candidates:
            if hashlib.sha256(cand.encode("utf-8")).hexdigest() in active_hashes:
                return cand
    return None


def scan_text_lines(
    source_label: str,
    lines: Iterable[tuple[int, str]],
    compartment: str,
) -> list[str]:
    findings: list[str] = []
    rules = active_content_rules(compartment)
    block_os_paths = _should_block_os_user_paths(compartment)
    block_affiliate = _should_block_affiliate_params(compartment)
    forbidden_hashes = _active_forbidden_hashes(compartment)
    is_step = source_label.lower().endswith((".step", ".stp"))
    norm_label = source_label.replace("\\", "/").lstrip("./")
    is_self_scanner = norm_label in ("scripts/audit_portability.py", "scripts/audit_data_boundary.py")

    for lineno, text in lines:
        if is_step and STEP_NUMERIC_ENTITY_RE.match(text):
            continue
        if not is_self_scanner:
            for rule_name, rx in rules:
                m = rx.search(text)
                if m:
                    findings.append(
                        f"[CONTENT:{rule_name}] {source_label}:{lineno}: {redact_snippet(text, m)}"
                    )
        if block_os_paths:
            for m_posix in RE_POSIX_HOME.finditer(text):
                if m_posix.group(1).lower() not in ALLOWED_PLACEHOLDER_USERS:
                    findings.append(
                        f"[CONTENT:local_workstation_path] {source_label}:{lineno}: {redact_snippet(text, m_posix)}"
                    )
            for m_win in RE_WIN_USERS.finditer(text):
                if m_win.group(1).lower() not in ALLOWED_PLACEHOLDER_USERS:
                    findings.append(
                        f"[CONTENT:local_workstation_path] {source_label}:{lineno}: {redact_snippet(text, m_win)}"
                    )
        if block_affiliate and not is_self_scanner:
            m_aff = RE_AFFILIATE_PARAM.search(text)
            if m_aff:
                findings.append(
                    f"[CONTENT:vendor_affiliate_tag] {source_label}:{lineno}: {redact_snippet(text, m_aff)}"
                )
        if forbidden_hashes:
            hit_tok = _find_forbidden_hash_token(text, forbidden_hashes)
            if hit_tok is not None:
                findings.append(
                    f"[CONTENT:forbidden_compartment_identifier] {source_label}:{lineno}: {redact_snippet(text, hit_tok)}"
                )
    return findings


def parse_unified_diff_added_lines(diff_text: str) -> list[tuple[str, int, str]]:
    """Return (filepath, new_lineno, line_content) for every added line in a unified git diff."""
    out: list[tuple[str, int, str]] = []
    cur_file = "<unknown>"
    cur_line = 0
    hunk_re = re.compile(r"^@@ -\d+(?:,\d+)? \+(\d+)(?:,\d+)? @@")
    for raw in diff_text.splitlines():
        if raw.startswith("+++ b/"):
            cur_file = raw[6:]
            continue
        if raw.startswith("+++ /dev/null"):
            cur_file = "/dev/null"
            continue
        m = hunk_re.match(raw)
        if m:
            cur_line = int(m.group(1))
            continue
        if raw.startswith("+") and not raw.startswith("+++"):
            if cur_file != "/dev/null":
                out.append((cur_file, cur_line, raw[1:]))
            cur_line += 1
        elif not raw.startswith("-") and not raw.startswith("\\"):
            if cur_line > 0:
                cur_line += 1
    return out


def scan_git_binary_flagged_blobs(
    repo_root: Path,
    candidate_paths: Iterable[str],
    diff_seen_paths: set[str],
    blob_oids: dict[str, str],
    compartment: str,
) -> list[str]:
    """Scan UTF-16/UTF-32 blobs that git diff treated as 'Binary files differ'."""
    findings: list[str] = []
    for rel in candidate_paths:
        if rel in diff_seen_paths:
            continue
        oid = blob_oids.get(rel)
        if not oid:
            continue
        raw_blob = subprocess.check_output(["git", "-C", str(repo_root), "cat-file", "blob", oid])
        findings.extend(scan_raw_bytes_complete(rel, raw_blob, compartment))
    return findings


def audit_staged(repo_root: Path, compartment: str) -> list[str]:
    findings: list[str] = []
    raw_staged = subprocess.check_output(
        ["git", "-C", str(repo_root), "diff", "--cached", "--name-only", "-z", "--diff-filter=ACMR"],
    ).decode("utf-8", errors="surrogateescape")
    staged_files = [f for f in raw_staged.split("\x00") if f]
    findings.extend(scan_filenames(staged_files, compartment))
    sym_findings, blob_oids = scan_git_tree_entries(repo_root, None)
    findings.extend(sym_findings)

    diff_txt = subprocess.check_output(
        ["git", "-C", str(repo_root), "-c", "core.quotePath=false", "diff", "--cached", "-U0", "--diff-filter=ACMR"],
        text=True,
        errors="replace",
    )
    grouped: dict[str, list[tuple[int, str]]] = {}
    for fpath, lineno, content in parse_unified_diff_added_lines(diff_txt):
        grouped.setdefault(fpath, []).append((lineno, content))
    for fpath, entries in grouped.items():
        findings.extend(scan_text_lines(fpath, entries, compartment))
    findings.extend(
        scan_git_binary_flagged_blobs(repo_root, staged_files, set(grouped.keys()), blob_oids, compartment)
    )
    return findings


def verify_remote_and_author_for_push(
    repo_root: Path,
    compartment: str,
    remote_name: str,
    remote_url: str,
    commit_range_args: list[str],
) -> list[str]:
    findings: list[str] = []
    repo_name = repo_root.resolve().name
    comp_cfg = POLICY.compartments.get(compartment, {})

    push_locked = bool(comp_cfg.get("push_locked", compartment == "homunculus"))
    if push_locked:
        findings.append(
            f"[REMOTE:{compartment}_locked] Pushing '{repo_name}' to '{remote_url}' is LOCKED by compartment policy."
        )
        return findings

    expected_url = str(comp_cfg.get("expected_remote_url", "")).strip()
    url_tpl = str(comp_cfg.get("expected_remote_url_template", "")).strip()
    if not expected_url and url_tpl:
        expected_url = url_tpl.format(repo_name=repo_name)
    expected_author = str(comp_cfg.get("expected_author_email", "")).strip()

    if not expected_url and not expected_author:
        if compartment == "alchemical" and POLICY.legacy_public_author:
            expected_author = POLICY.legacy_public_author
        elif compartment == "engineering":
            expected_url = POLICY.legacy_private_remote
            expected_author = POLICY.legacy_private_author

    if expected_url and remote_url != expected_url:
        findings.append(
            f"[REMOTE:url_mismatch] Remote '{remote_name}' URL '{remote_url}' is forbidden for '{repo_name}' "
            f"(expected exact '{expected_url}')."
        )

    if expected_author and commit_range_args:
        log_out = subprocess.check_output(
            ["git", "-C", str(repo_root), "log", *commit_range_args, "--format=%h %ae"],
            text=True,
        ).splitlines()
        for line in log_out:
            if not line.strip():
                continue
            sha, ae = line.split(" ", 1)
            if ae.strip() != expected_author:
                findings.append(
                    f"[AUTHOR:identity_mismatch] Outgoing commit {sha} has author '{ae.strip()}' "
                    f"(expected '{expected_author}')."
                )
    return findings


def audit_push_stdin(
    repo_root: Path,
    compartment: str,
    remote_name: str,
    remote_url: str,
    stdin_lines: Iterable[str],
) -> list[str]:
    findings: list[str] = []
    saw_ref = False
    for line in stdin_lines:
        parts = line.strip().split()
        if len(parts) != 4:
            continue
        _local_ref, local_oid, _remote_ref, remote_oid = parts
        if local_oid == ZERO_OID:
            continue
        saw_ref = True

        is_anc = False
        if remote_oid != ZERO_OID:
            rc = subprocess.run(
                ["git", "-C", str(repo_root), "merge-base", "--is-ancestor", remote_oid, local_oid],
                capture_output=True,
            ).returncode
            is_anc = rc == 0

        if remote_oid == ZERO_OID or not is_anc:
            range_args = [local_oid, "--not", f"--remotes={remote_name}"]
        else:
            range_args = [f"{remote_oid}..{local_oid}"]

        rf = verify_remote_and_author_for_push(repo_root, compartment, remote_name, remote_url, range_args)
        findings.extend(rf)
        if any("_locked]" in item for item in rf):
            continue

        sym_findings, blob_oids = scan_git_tree_entries(repo_root, local_oid)
        raw_tree_names = subprocess.check_output(
            ["git", "-C", str(repo_root), "ls-tree", "-r", "--name-only", "-z", local_oid],
        ).decode("utf-8", errors="surrogateescape")
        tree_files = [f for f in raw_tree_names.split("\x00") if f]
        findings.extend(scan_filenames(tree_files, compartment))
        findings.extend(sym_findings)

        raw_changed_names = subprocess.check_output(
            ["git", "-C", str(repo_root), "log", "--name-only", "-z", "--pretty=format:", *range_args],
        ).decode("utf-8", errors="surrogateescape")
        changed_files = [f for f in raw_changed_names.split("\x00") if f.strip()]

        diff_txt = subprocess.check_output(
            ["git", "-C", str(repo_root), "-c", "core.quotePath=false", "log", "-p", "-U0", *range_args],
            text=True,
            errors="replace",
        )
        grouped: dict[str, list[tuple[int, str]]] = {}
        for fpath, lineno, content in parse_unified_diff_added_lines(diff_txt):
            grouped.setdefault(fpath, []).append((lineno, content))
        for fpath, entries in grouped.items():
            findings.extend(scan_text_lines(fpath, entries, compartment))
        findings.extend(
            scan_git_binary_flagged_blobs(repo_root, changed_files, set(grouped.keys()), blob_oids, compartment)
        )

    if not saw_ref:
        findings.extend(verify_remote_and_author_for_push(repo_root, compartment, remote_name, remote_url, []))
    return findings


def audit_worktree(repo_root: Path, compartment: str) -> list[str]:
    findings: list[str] = []
    if (repo_root / ".git").exists():
        raw_ls = subprocess.check_output(
            ["git", "-C", str(repo_root), "ls-files", "--cached", "--others", "--exclude-standard", "-z"],
        ).decode("utf-8", errors="surrogateescape")
        raw_files = [f for f in raw_ls.split("\x00") if f]
    else:
        raw_files = [
            p.relative_to(repo_root).as_posix()
            for p in sorted(repo_root.rglob("*"))
            if ".git" not in p.relative_to(repo_root).parts and (p.is_file() or p.is_symlink())
        ]
    existing_files = [f for f in raw_files if (repo_root / f).is_symlink() or (repo_root / f).exists()]
    findings.extend(scan_filenames(existing_files, compartment))

    for rel in existing_files:
        full = repo_root / rel
        if full.is_symlink():
            target = os.readlink(full)
            err = check_symlink_escape(rel, target)
            if err:
                findings.append(err)
            continue
        if not full.is_file():
            continue
        try:
            with full.open("rb") as fh:
                head = fh.read(8192)
                if detect_text_encoding(head)[0] is None:
                    continue
                raw_bytes = head + fh.read()
        except OSError as exc:
            findings.append(f"[IO_ERROR] Failed reading {rel}: {exc}")
            continue
        findings.extend(scan_raw_bytes_complete(rel, raw_bytes, compartment))
    return findings


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Homunculus Declarative Data-Boundary, Decontamination & Credential Safety Scanner"
    )
    parser.add_argument("repo_pos", nargs="?", default=None, help="Optional positional repository directory")
    parser.add_argument("--repo", help="Target repository directory")
    parser.add_argument("--config", help="Optional JSON boundary configuration file (homunculus_safety.json)")
    parser.add_argument("--compartment", help="Explicit compartment override (e.g. private, public, cleanroom, homunculus)")
    parser.add_argument("--staged", action="store_true", help="Scan git staged index (pre-commit mode)")
    parser.add_argument("--push-stdin", action="store_true", help="Scan git pre-push refs from stdin")
    parser.add_argument("--remote-name", default="origin", help="Remote name for --push-stdin")
    parser.add_argument("--remote-url", default="", help="Remote URL for --push-stdin")
    parser.add_argument("--worktree", action="store_true", help="Scan tracked + untracked non-ignored files")
    parser.add_argument("--all-in-root", help="Audit all git repositories under the specified parent directory")
    args = parser.parse_args(argv)

    raw_repo_arg = args.repo or args.repo_pos
    target_repo = Path(raw_repo_arg).expanduser().resolve() if raw_repo_arg else (
        Path(args.all_in_root).expanduser().resolve() if args.all_in_root else None
    )
    load_boundary_config(args.config, repo_root=target_repo)

    if args.all_in_root:
        parent_root = Path(args.all_in_root).expanduser().resolve()
        repos = sorted(
            p for p in list(parent_root.iterdir()) if p.is_dir() and (p / ".git").exists()
        )
        if not repos:
            print(f"[ERROR] No git repositories found in {parent_root}", file=sys.stderr)
            return 2
        total_findings = 0
        for r in repos:
            comp = classify_compartment(r, args.compartment)
            f = audit_worktree(r, comp)
            status = "PASS" if not f else f"FAIL ({len(f)})"
            print(f"[{status}] {r.name} (compartment={comp})")
            for item in f:
                print(f"  {item}", file=sys.stderr)
            total_findings += len(f)
        return 1 if total_findings else 0

    if target_repo is None:
        parser.error("--repo is required unless --all-in-root is passed.")

    compartment = classify_compartment(target_repo, args.compartment)

    if args.staged:
        findings = audit_staged(target_repo, compartment)
    elif args.push_stdin:
        findings = audit_push_stdin(target_repo, compartment, args.remote_name, args.remote_url, sys.stdin)
    elif args.worktree:
        findings = audit_worktree(target_repo, compartment)
        if not findings:
            print(f"[PASS] BOUNDARY_CLEAN | repo={target_repo.name} | compartment={compartment}")
    else:
        parser.error("Specify one of --staged, --push-stdin, --worktree, or --all-in-root.")

    if findings:
        print(
            f"[SECURITY / BOUNDARY BLOCKED] {len(findings)} violation(s) in {target_repo.name} (compartment={compartment}):",
            file=sys.stderr,
        )
        for item in findings:
            print(f"  - {item}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
