#!/usr/bin/env python3
"""Homunculus Deterministic Clean-Room, Zero-PII & Cross-OS Portability Gate.

Fails closed (exit != 0) if any file inside the Homunculus repository contains:
  1. Hardcoded OS user/account paths (/home/<user>, /Users/<user>, C:\\Users\\<user>, /root/)
  2. Upstream workstation / entity / personal identifiers (matched via SHA-256 token digests
     so zero forbidden plaintext strings ever reside inside this scanner)
  3. Affiliate tracking query parameters (?affp=..., dt_id=..., aff_id=...)
  4. Live credentials, API keys, OAuth client secrets, or private keys
  5. Non-stdlib third-party pip imports inside core Python scripts
  6. Non-template files inside any corpus_inbox/ directory

Decodes files across UTF-8, UTF-16 (LE/BE), and UTF-32 (LE/BE) so multi-byte encoding cannot
bypass inspection. Requires ONLY Python 3.10+ standard library.

=== DEVELOPER & AI NAVIGATION MAP ===
  Owning Module : Core Framework (`scripts/`)
  Callers       : `install.sh`, `install.ps1`, `pre-commit-gate` (Stage Z2), `test_foundation.py`, `test_data_safety.py`, `test_adapters.py`
  Callees       : `homunculus_paths.py` (`CLEANROOM_FORBIDDEN_SHA256`, `ALLOWED_PLACEHOLDER_USERS`, `RE_POSIX_HOME`, `RE_WIN_USERS`, `decode_file_text`)
  Contract      : `scripts/script_contracts.json` [`audit_portability.py`]
  CLI Flags     : --repo, --root, --repo-root, --forbid-token, --json
  Symbol Index  (jump directly via read_file StartLine/EndLine):
    - def decode_file_text (#L74-L76)                | def _check_cleanroom_hashes (#L79-L92)
    - def _audit_python_stdlib_only (#L95-L120)      | def audit_repository (#L123-L281)
    - def main (#L284-L328)
=== END NAVIGATION MAP ===
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import homunculus_paths  # noqa: E402

# SHA-256 lowercase digests of forbidden upstream workstation, personal, partner-personal,
# independent-enterprise, and affiliate identifiers (zero plaintext storage).
FORBIDDEN_TOKEN_SHA256: frozenset[str] = homunculus_paths.CLEANROOM_FORBIDDEN_SHA256

# Allowed placeholder usernames in documentation examples
ALLOWED_PLACEHOLDER_USERS: frozenset[str] = homunculus_paths.ALLOWED_PLACEHOLDER_USERS

# Hardcoded OS user-directory regexes across Linux, macOS, and Windows
RE_POSIX_HOME = homunculus_paths.RE_POSIX_HOME
RE_WIN_USERS = homunculus_paths.RE_WIN_USERS
RE_AFFILIATE_PARAM = re.compile(r"(?:\?|&|\b)(?:affp|dt_id|aff_id|affiliate_id)=[A-Za-z0-9_-]+", re.IGNORECASE)

# Credential and secret patterns
SECRET_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("PRIVATE_KEY_HEADER", re.compile(r"-----BEGIN [A-Z0-9 ]*PRIVATE KEY-----")),
    ("GOOGLE_API_KEY", re.compile(r"\bAIza[0-9A-Za-z_-]{35}\b")),
    ("GOOGLE_OAUTH_SECRET", re.compile(r"\bGOCSPX-[0-9A-Za-z_-]{20,}\b")),
    ("GOOGLE_ACCESS_TOKEN", re.compile(r"\bya29\.[0-9A-Za-z_-]{20,}\b")),
    ("GITHUB_PAT_TOKEN", re.compile(r"\b(?:gh[pousr]_[0-9A-Za-z]{36,}|github_pat_[0-9A-Za-z_]{40,})\b")),
    ("API_BEARER_KEY", re.compile(r"\bsk-(?:proj-|ant-)?[A-Za-z0-9_-]{24,}\b")),
)

# Candidate token extractor for SHA-256 clean-room blocklist matching
RE_CANDIDATE_TOKENS = re.compile(r"[A-Za-z0-9._@=-]{6,64}")

SKIP_DIRS: frozenset[str] = frozenset(
    {".git", "__pycache__", ".pytest_cache", ".venv", "venv", "scratch", "sandbox_runs"}
)


def decode_file_text(raw_bytes: bytes) -> str:
    """Decode text handling UTF-8, UTF-16 (LE/BE), and UTF-32 (LE/BE) BOMs or NUL-interleaved text."""
    return homunculus_paths.decode_file_text(raw_bytes)


def _check_cleanroom_hashes(line: str) -> str | None:
    """Return the offending token if any token or sub-token matches FORBIDDEN_TOKEN_SHA256."""
    for match in RE_CANDIDATE_TOKENS.finditer(line):
        raw_tok = match.group(0).strip(".,:;()[]{}<>\"'")
        candidates = {raw_tok.lower()}
        if "/" in raw_tok:
            candidates.update(part.lower() for part in raw_tok.split("/") if len(part) >= 6)
        if "=" in raw_tok and "?" in raw_tok:
            candidates.update(part.lower() for part in raw_tok.split("?") if len(part) >= 6)
        for cand in candidates:
            digest = hashlib.sha256(cand.encode("utf-8")).hexdigest()
            if digest in FORBIDDEN_TOKEN_SHA256:
                return cand
    return None


def _audit_python_stdlib_only(file_path: Path, rel_path: str, text: str, local_modules: set[str]) -> list[dict[str, Any]]:
    """Verify Python files import only Python 3.10+ stdlib or local Homunculus modules via Unified AST Kernel."""
    findings: list[dict[str, Any]] = []
    info = homunculus_paths.inspect_python_ast_and_map(file_path, local_modules=local_modules, source_text=text)
    if info["syntax_error"] is not None:
        err = info["syntax_error"]
        findings.append(
            {
                "rule": "PYTHON_SYNTAX_ERROR",
                "file": rel_path,
                "line": err["line"],
                "detail": f"SyntaxError: {err['msg']}",
            }
        )
        return findings

    for imp in info["non_stdlib_imports"]:
        findings.append(
            {
                "rule": "NON_STDLIB_PIP_IMPORT",
                "file": rel_path,
                "line": imp["line"],
                "detail": f"External third-party import '{imp['stmt']}' violates zero-pip portability.",
            }
        )
    return findings


def audit_repository(repo_root: Path, extra_forbidden_tokens: list[str] | None = None) -> dict[str, Any]:
    """Scan all files inside repo_root for portability, clean-room, and secret violations."""
    repo_root = repo_root.resolve()
    findings: list[dict[str, Any]] = []
    files_scanned = 0

    extra_hashes = {
        hashlib.sha256(tok.strip().lower().encode("utf-8")).hexdigest()
        for tok in (extra_forbidden_tokens or [])
        if tok.strip()
    }

    # Collect local Python module stem names inside the repository for import checks
    local_py_modules: set[str] = {"scripts", "skills", "adapters", "tests"}
    for py_file in repo_root.rglob("*.py"):
        if not any(part in SKIP_DIRS for part in py_file.relative_to(repo_root).parts):
            local_py_modules.add(py_file.stem)

    for path in sorted(repo_root.rglob("*")):
        rel_parts = path.relative_to(repo_root).parts
        if any(part in SKIP_DIRS for part in rel_parts):
            continue
        if not path.is_file():
            continue

        rel_str = path.relative_to(repo_root).as_posix()
        files_scanned += 1

        # 1. Check corpus_inbox hygiene (only README.md and .gitkeep permitted)
        if "corpus_inbox" in rel_parts and path.name not in ("README.md", ".gitkeep"):
            findings.append(
                {
                    "rule": "NON_TEMPLATE_VOICE_CORPUS",
                    "file": rel_str,
                    "line": 1,
                    "detail": f"Personal corpus artifact '{path.name}' inside corpus_inbox/ is forbidden.",
                }
            )

        # 2. Check forbidden credential filenames
        lower_name = path.name.lower()
        if (
            lower_name.startswith("client_secret")
            or lower_name.endswith((".pem", ".key", ".p12", ".pfx"))
            or lower_name in ("id_rsa", "id_ed25519", "credentials.json", "token.json")
        ):
            findings.append(
                {
                    "rule": "FORBIDDEN_CREDENTIAL_FILE",
                    "file": rel_str,
                    "line": 1,
                    "detail": f"Credential/key filename '{path.name}' is forbidden in Homunculus.",
                }
            )

        try:
            raw_bytes = path.read_bytes()
        except OSError as exc:
            findings.append(
                {
                    "rule": "FILE_READ_ERROR",
                    "file": rel_str,
                    "line": 1,
                    "detail": f"Failed to read file: {exc}",
                }
            )
            continue

        text = decode_file_text(raw_bytes)

        # 3. Line-by-line content inspection
        for lineno, line in enumerate(text.splitlines(), start=1):
            # 3a. Upstream clean-room token SHA-256 check
            hit_token = _check_cleanroom_hashes(line)
            if hit_token is not None:
                findings.append(
                    {
                        "rule": "CLEANROOM_FORBIDDEN_IDENTIFIER",
                        "file": rel_str,
                        "line": lineno,
                        "detail": f"Forbidden upstream/entity identifier matched clean-room blocklist: '{hit_token}'",
                    }
                )

            if extra_hashes:
                for match in RE_CANDIDATE_TOKENS.finditer(line):
                    cand = match.group(0).strip(".,:;()[]{}<>\"'").lower()
                    if hashlib.sha256(cand.encode("utf-8")).hexdigest() in extra_hashes:
                        findings.append(
                            {
                                "rule": "CUSTOM_FORBIDDEN_IDENTIFIER",
                                "file": rel_str,
                                "line": lineno,
                                "detail": f"Custom forbidden identifier matched: '{cand}'",
                            }
                        )

            # 3b. Hardcoded POSIX /home/<user> or /Users/<user>
            for m_posix in RE_POSIX_HOME.finditer(line):
                username = m_posix.group(1)
                if username.lower() not in ALLOWED_PLACEHOLDER_USERS:
                    findings.append(
                        {
                            "rule": "HARDCODED_OS_USER_PATH",
                            "file": rel_str,
                            "line": lineno,
                            "detail": f"Hardcoded POSIX user path '{m_posix.group(0)}' violates cross-OS portability.",
                        }
                    )

            # 3c. Hardcoded Windows C:\Users\<user>
            for m_win in RE_WIN_USERS.finditer(line):
                username = m_win.group(1)
                if username.lower() not in ALLOWED_PLACEHOLDER_USERS:
                    findings.append(
                        {
                            "rule": "HARDCODED_OS_USER_PATH",
                            "file": rel_str,
                            "line": lineno,
                            "detail": f"Hardcoded Windows user path '{m_win.group(0)}' violates cross-OS portability.",
                        }
                    )

            # 3d. Affiliate tracking parameters
            m_aff = RE_AFFILIATE_PARAM.search(line)
            if m_aff and rel_str != "scripts/audit_portability.py":
                findings.append(
                    {
                        "rule": "FORBIDDEN_AFFILIATE_PARAMETER",
                        "file": rel_str,
                        "line": lineno,
                        "detail": f"Affiliate tracking parameter '{m_aff.group(0)}' is forbidden in Homunculus.",
                    }
                )

            # 3e. Secret / API key patterns
            if rel_str != "scripts/audit_portability.py":
                for rule_id, pat in SECRET_PATTERNS:
                    if pat.search(line):
                        findings.append(
                            {
                                "rule": rule_id,
                                "file": rel_str,
                                "line": lineno,
                                "detail": f"Secret/credential pattern '{rule_id}' detected.",
                            }
                        )

        # 4. AST stdlib-only check on Python scripts
        if path.suffix == ".py":
            findings.extend(_audit_python_stdlib_only(path, rel_str, text, local_py_modules))

    return {
        "repo_root": str(repo_root),
        "files_scanned": files_scanned,
        "violation_count": len(findings),
        "status": "PASS" if not findings else "FAIL",
        "violations": findings,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Homunculus Clean-Room, Zero-PII & Cross-OS Portability Auditor."
    )
    parser.add_argument(
        "--repo",
        "--root",
        "--repo-root",
        dest="repo",
        default=str(Path(__file__).resolve().parent.parent),
        help="Target repository directory to audit (default: Homunculus root).",
    )
    parser.add_argument(
        "--forbid-token",
        action="append",
        default=[],
        help="Additional custom identifier token to block (may be specified multiple times).",
    )
    parser.add_argument("--json", action="store_true", help="Output audit report as JSON.")
    args = parser.parse_args(argv)

    repo_root = Path(args.repo).expanduser().resolve()
    if not repo_root.is_dir():
        print(f"[FAIL] Repository path does not exist: {repo_root}", file=sys.stderr)
        return 2

    report = audit_repository(repo_root, extra_forbidden_tokens=args.forbid_token)
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        if report["status"] == "PASS":
            print(
                f"[PASS] Homunculus Clean-Room & Portability Gate | "
                f"Files Scanned: {report['files_scanned']} | Violations: 0"
            )
        else:
            print(
                f"[FAIL] Homunculus Clean-Room & Portability Gate | "
                f"Files Scanned: {report['files_scanned']} | Violations: {report['violation_count']}",
                file=sys.stderr,
            )
            for v in report["violations"]:
                print(f"  - [{v['rule']}] {v['file']}:{v['line']} -> {v['detail']}", file=sys.stderr)

    return 0 if report["status"] == "PASS" else 2


if __name__ == "__main__":
    sys.exit(main())
