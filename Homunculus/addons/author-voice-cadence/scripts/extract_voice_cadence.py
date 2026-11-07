#!/usr/bin/env python3
"""
Author Voice & Cadence Deep Stylometric Extractor (extract_voice_cadence.py)
------------------------------------------------------------------------------
Ingests exported Discord history and long-form writing from corpus_inbox/,
supporting both:
  1. Official Discord Account Data Packages (Messages/index.json + c<id>/channel.json
     + c<id>/messages.json or messages.csv, sorted chronologically ascending)
  2. DiscordChatExporter / standalone files (.json, .csv, .txt, .md) in nested folders

Maker Org & Supplier Domain Taxonomy (Zero Gaming/DM Contamination):
  - TIER_1A_BLOG: Primary Author official blog & announcements (2.4x exemplar weight)
  - TIER_1B_ORG_RND: Primary Author engineering, R&D & subsystem channels (1.55x)
  - TIER_2A_MAKER_SUPPLIERS: Hardware suppliers, webstore companies & component vendors
    operating on Discord or community forums (configurable via --tier-config) (1.15x)
  - TIER_2B_MAKER_ORGS: Open-source hardware/firmware orgs & dedicated engineering
    communities (configurable via --tier-config) (1.0x)
  - TIER_3_TECH_LINUX: General Linux / sysadmin communities (excluded in 'maker' scope)
  - EXCLUDED_GAMING_SOCIAL / EXCLUDED_DM_PRIVATE: Gaming servers, private DMs, and
    internal business/admin channels (excluded)

Deep Pass Stylometrics:
  1. Ecosystem & Maker Company/Org breakdown
  2. Sub-register comparison (Blog/Announcements vs. Engineering R&D vs. Maker Suppliers/Orgs)
  3. 5-band sentence length distribution, intra-paragraph beat swing, & positional sentence arc
  4. Paragraph chunking & multi-paragraph post structure
  5. Clause-linking syntax (comma-pivots, sentence-final 'though', causal connectors)
  6. Persona pronoun balance (I/my vs. we/our vs. you/your), conviction boosters & candor hedges
  7. Head-to-head uncontracted vs. contracted ratios + punctuation/ALL-CAPS emphasis profile
  8. Empirical zero-count audit of generic LLM clichés + authentic author idioms/vernacular
  9. Stratified verbatim candidate exemplars across all 5 categories
"""

import argparse
import collections
import csv
import datetime
import json
import os
import re
import statistics
import sys
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

sys.dont_write_bytecode = True

_SKILL_DIR = Path(__file__).resolve().parents[1]
DEFAULT_INBOX = str(_SKILL_DIR / "corpus_inbox")
DEFAULT_OUTPUT = str(_SKILL_DIR / "references" / "cadence_telemetry_report.md")

URL_RE = re.compile(r"https?://\S+")
USER_MENTION_RE = re.compile(r"<@!?\d+>|\[@\w+\]")
DISCORD_TAG_RE = re.compile(r"<[#&]\d+>|<a?:\w+:\d+>|@(?:everyone|here)\b")
FENCED_CODE_RE = re.compile(r"```.*?```", re.DOTALL)
INLINE_CODE_RE = re.compile(r"`[^`\n]+`")
ELLIPSIS_RE = re.compile(r"\.{3,}")
DISCORD_TXT_HEADER_RE = re.compile(
    r"^\[(\d{1,4}[-/]\d{1,2}[-/]\d{1,4}[^\]]*)\]\s+([^\n]+)\n", re.MULTILINE
)
SENTENCE_SPLIT_RE = re.compile(
    r"(?<!\bFig)(?<!\bfig)(?<!\bvs)(?<!\be\.g)(?<!\bi\.e)(?<!\bMr)(?<!\bDr)(?<=[.!?])\s+(?=[A-Z0-9\"'(\[])"
)
DOUBLE_SPACE_AFTER_PUNCT_RE = re.compile(r"[.!?]  +[A-Z0-9\"'(\[]")
WORD_RE = re.compile(r"[A-Za-z0-9']+[-'][A-Za-z0-9']+|[A-Za-z0-9']+")

TECH_ACRONYMS = {
    "ABS", "ASA", "PLA", "PETG", "TPU", "PTFE", "PEEK", "PEI", "CAD", "STL", "STEP",
    "BOM", "MCU", "PCB", "PWM", "LED", "USB", "CAN", "SPI", "UART", "MOSFET", "SSR",
    "VHB", "CFM", "RPM", "DPI", "PNG", "SVG", "PDF", "CSV", "JSON", "DIY", "FYI",
    "WIP", "TBD", "TBA", "FAQ", "GUI", "CLI", "SSH", "CPU", "GPU", "RAM", "PSU",
    "LDO", "VORON", "FXD", "BETA", "ALPHA", "NSFW", "USA", "OEM", "PID",
    "NTC", "PTC", "AWG", "DIN", "ISO", "CNC", "FDM", "FFF", "SLA", "SLS", "SBC",
    "GPIO", "I2C", "DFU", "OTA", "BTT", "EBB", "SB2209", "MGN9H", "MGN12H", "MGN9",
    "MGN12", "GE5C", "F695", "GT2", "2GT", "EPDM", "ACM", "UHMW", "POM", "PC",
    "PA6", "PA12", "PPS", "PPA", "VOC", "HEPA", "VSW", "BMG", "TEC", "LIDAR",
    "MRRF", "RMRRF", "PIF", "RPI", "CHT", "CPAP", "QTY", "TBH", "BTW", "ATM",
    "IMO", "IMHO", "IDK", "LOL", "LMAO", "ROFL", "AFAIK", "IIRC", "TLDR", "ASAP",
    "AKA", "ETC", "DOA", "NDA", "RGB", "RGBW", "WLED", "IPA", "FEP", "DXF", "API",
    "klipper", "KVP", "3DO", "ORB", "LGX", "CW1", "CW2", "TAP", "KLICKY", "AB",
    "XY", "XZ", "YZ", "Z0", "Z1", "Z2", "M3", "M4", "M5", "M2", "SHCS", "BHCS",
    "FHCS", "PSU", "AC", "DC", "VAC", "VDC", "AMP", "AMPS", "WATTS", "SKR", "GCR",
    "ERRF", "CST", "EST", "PST", "MST", "UTC", "EVA", "JST", "HST", "MZE", "SQV",
    "TOF", "EMI", "IRL", "IGUS", "QGL", "NEMA", "TMC", "SPI", "I2C", "UART", "DFM",
    "FEA", "CFD", "CAD", "CAM", "CNC", "RPM", "CFM", "PSI", "KPA", "BAR", "SCFM",
}
ALL_CAPS_WORD_RE = re.compile(r"\b[A-Z]{3,14}\b")

CONTRACTION_RE = re.compile(
    r"\b(?:i'm|i've|i'll|i'd|it's|that's|there's|what's|here's|don't|doesn't|didn't|"
    r"can't|couldn't|won't|wouldn't|shouldn't|isn't|aren't|wasn't|weren't|haven't|hasn't|"
    r"you're|you'll|you've|we're|we've|we'll|they're|they've|let's)\b",
    re.IGNORECASE,
)

# Generic, configurable channel/document tier rules (zero personal or client server names)
PRIVATE_ADMIN_CHANNEL_PATTERNS = (
    "business", "supplier-only", "admin-channel", "admin-command",
    "moderators-chat", "verification", "nsfw", "private", "finance", "credentials",
)

BLOG_CHANNEL_KEYWORDS = {
    "blog", "devlog", "announcements", "release-notes", "changelog", "updates", "articles",
}

RND_CHANNEL_KEYWORDS = {
    "rnd", "r-and-d", "engineering", "architecture", "design", "hardware", "firmware", "software", "testing", "bench",
}

MAKER_SUPPLIER_COMPANIES: Set[str] = set()
OPEN_SOURCE_MAKER_ORGS: Set[str] = set()
MAKER_ORG_SUBSTRINGS = ("engineering", "hardware", "firmware", "robotics", "maker", "dev", "tech")

# Deep Stylometric Lexicons & Patterns
CLAUSE_PIVOT_PATTERNS = [
    (", which", re.compile(r",\s+which\b", re.IGNORECASE)),
    (", while", re.compile(r",\s+while\b", re.IGNORECASE)),
    (", so", re.compile(r",\s+so\b", re.IGNORECASE)),
    (", as", re.compile(r",\s+as\b", re.IGNORECASE)),
    (", since", re.compile(r",\s+since\b", re.IGNORECASE)),
    (", especially", re.compile(r",\s+especially\b", re.IGNORECASE)),
    (", however", re.compile(r",\s+however\b", re.IGNORECASE)),
    (", meaning / allowing", re.compile(r",\s+(?:meaning|allowing|enabling|resulting|giving|making)\b", re.IGNORECASE)),
    ("clause-final 'though'", re.compile(r"\bthough(?=[.!?,;)\n]|$)", re.IGNORECASE)),
    ("mid-clause 'though'", re.compile(r"\bthough\s+\w+", re.IGNORECASE)),
]

CAUSAL_CONNECTOR_PATTERNS = [
    ("because", re.compile(r"\bbecause\b", re.IGNORECASE)),
    ("since (causal/temporal)", re.compile(r"\bsince\b", re.IGNORECASE)),
    ("due to", re.compile(r"\bdue to\b", re.IGNORECASE)),
    ("instead of / instead", re.compile(r"\binstead(?:\s+of)?\b", re.IGNORECASE)),
    ("allow(s) / allowing", re.compile(r"\ballow(?:s|ed|ing)?\b", re.IGNORECASE)),
    ("enable(s) / enabling", re.compile(r"\benabl(?:e|es|ed|ing)\b", re.IGNORECASE)),
    ("this/which means", re.compile(r"\b(?:this|which|that)\s+means\b", re.IGNORECASE)),
    ("in order to", re.compile(r"\bin order to\b", re.IGNORECASE)),
    ("thus / therefore", re.compile(r"\b(?:thus|therefore)\b", re.IGNORECASE)),
]

CONTRACTION_PAIRS = [
    ("do not vs. don't", re.compile(r"\bdo not\b", re.IGNORECASE), re.compile(r"\bdon'?t\b", re.IGNORECASE)),
    ("does not vs. doesn't", re.compile(r"\bdoes not\b", re.IGNORECASE), re.compile(r"\bdoesn'?t\b", re.IGNORECASE)),
    ("cannot/can not vs. can't", re.compile(r"\b(?:cannot|can not)\b", re.IGNORECASE), re.compile(r"\bcan'?t\b", re.IGNORECASE)),
    ("will not vs. won't", re.compile(r"\bwill not\b", re.IGNORECASE), re.compile(r"\bwon'?t\b", re.IGNORECASE)),
    ("is not vs. isn't", re.compile(r"\bis not\b", re.IGNORECASE), re.compile(r"\bisn'?t\b", re.IGNORECASE)),
    ("are not vs. aren't", re.compile(r"\bare not\b", re.IGNORECASE), re.compile(r"\baren'?t\b", re.IGNORECASE)),
    ("I am vs. I'm", re.compile(r"\bi am\b", re.IGNORECASE), re.compile(r"\bi'm\b", re.IGNORECASE)),
    ("I have vs. I've", re.compile(r"\bi have\b", re.IGNORECASE), re.compile(r"\bi've\b", re.IGNORECASE)),
    ("I will vs. I'll", re.compile(r"\bi will\b", re.IGNORECASE), re.compile(r"\bi'll\b", re.IGNORECASE)),
    ("it is vs. it's", re.compile(r"\bit is\b", re.IGNORECASE), re.compile(r"\bit's\b", re.IGNORECASE)),
]

BANNED_AI_TROPES = [
    ("delve / delving", re.compile(r"\bdelv(?:e|es|ed|ing)\b", re.IGNORECASE)),
    ("tapestry", re.compile(r"\btapestr(?:y|ies)\b", re.IGNORECASE)),
    ("seamlessly", re.compile(r"\bseamless(?:ly)?\b", re.IGNORECASE)),
    ("testament to", re.compile(r"\btestament to\b", re.IGNORECASE)),
    ("meticulously", re.compile(r"\bmeticulous(?:ly)?\b", re.IGNORECASE)),
    ("furthermore", re.compile(r"\bfurthermore\b", re.IGNORECASE)),
    ("moreover", re.compile(r"\bmoreover\b", re.IGNORECASE)),
    ("in conclusion / in summary", re.compile(r"\bin (?:conclusion|summary)\b", re.IGNORECASE)),
    ("game-changer / revolutionary", re.compile(r"\b(?:game[- ]changer|revolutionary|unparalleled)\b", re.IGNORECASE)),
    ("elevate (non-Z-axis)", re.compile(r"\belevat(?:e|es|ed|ing)\b", re.IGNORECASE)),
    ("holistic / synergy", re.compile(r"\b(?:holistic|synerg(?:y|ies))\b", re.IGNORECASE)),
    ("it is important to note", re.compile(r"\bit is important to note\b", re.IGNORECASE)),
]

SIGNATURE_PHRASE_PATTERNS = [
    ("keep in mind (though)", re.compile(r"\bkeep in mind(?:\s+though)?\b", re.IGNORECASE)),
    ("as you can see", re.compile(r"\bas you can see\b", re.IGNORECASE)),
    ("in the mean time / meantime", re.compile(r"\bin the (?:mean time|meantime)\b", re.IGNORECASE)),
    ("at some point", re.compile(r"\bat some point\b", re.IGNORECASE)),
    ("this is why", re.compile(r"\bthis is why\b", re.IGNORECASE)),
    ("out of the box", re.compile(r"\bout of the box\b", re.IGNORECASE)),
    ("on the fly", re.compile(r"\bon the fly\b", re.IGNORECASE)),
    ("down the road", re.compile(r"\bdown the road\b", re.IGNORECASE)),
    ("needless to say", re.compile(r"\bneedless to say\b", re.IGNORECASE)),
    ("in regards to", re.compile(r"\bin regards to\b", re.IGNORECASE)),
    ("at the cost of", re.compile(r"\bat the cost of\b", re.IGNORECASE)),
    ("play(ing) with (prototyping)", re.compile(r"\bplay(?:ing|ed)? with\b", re.IGNORECASE)),
    ("every little bit (helps)", re.compile(r"\bevery little bit\b", re.IGNORECASE)),
    ("for the time being / for now", re.compile(r"\b(?:for the time being|for now)\b", re.IGNORECASE)),
    ("more (will come / to come)", re.compile(r"\bmore (?:will come|to come)\b", re.IGNORECASE)),
    ("in my testing / experience", re.compile(r"\bin my (?:testing|experience)\b", re.IGNORECASE)),
    ("make sure (instructional)", re.compile(r"\bmake sure\b", re.IGNORECASE)),
    ("be sure to", re.compile(r"\bbe sure to\b", re.IGNORECASE)),
]

CONVICTION_WORDS = {
    "very", "really", "quite", "greatly", "extremely", "massive", "huge", "enormous",
    "critical", "completely", "literally", "definitely", "absolutely", "painfully",
    "obviously", "clearly", "never", "always", "pretty", "super", "tons",
}

CANDOR_HEDGE_WORDS = {
    "likely", "probably", "honestly", "frankly", "roughly", "basically", "essentially",
    "hopefully", "originally", "currently", "unfortunately", "potentially", "sans",
    "technically", "ideally", "personally", "apparently", "mostly", "fairly",
}


class PostRecord:
    __slots__ = ("source", "org", "channel", "tier", "weight", "timestamp", "text")

    def __init__(
        self,
        source: str,
        org: str,
        channel: str,
        tier: str,
        weight: float,
        timestamp: str,
        text: str,
    ):
        self.source = source
        self.org = org
        self.channel = channel
        self.tier = tier
        self.weight = weight
        self.timestamp = timestamp
        self.text = text


def parse_ts(raw_ts: str) -> Optional[datetime.datetime]:
    if not raw_ts:
        return None
    s = raw_ts.strip()
    try:
        dt = datetime.datetime.fromisoformat(s.replace("Z", "+00:00"))
        if dt.tzinfo is not None:
            dt = dt.astimezone(datetime.timezone.utc).replace(tzinfo=None)
        return dt
    except ValueError:
        pass
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y/%m/%d %H:%M:%S", "%m/%d/%Y %I:%M %p"):
        try:
            return datetime.datetime.strptime(s, fmt)
        except ValueError:
            continue
    return None


def clean_post_text(raw: str) -> str:
    text = raw.replace("\r\n", "\n").strip()
    text = USER_MENTION_RE.sub("[Collaborator]", text)
    text = DISCORD_TAG_RE.sub("", text)
    return text.strip()


def strip_code_for_prose_metrics(text: str) -> str:
    no_fenced = FENCED_CODE_RE.sub("\n\n", text)
    no_inline = INLINE_CODE_RE.sub("CODE_TOKEN", no_fenced)
    return URL_RE.sub("", no_inline)


def classify_channel_domain(org_name: str, channel: str, ctype: str) -> Tuple[str, float]:
    """Classifies channels or standalone docs into stylometric register tiers using generic keywords."""
    ct_upper = (ctype or "").upper()
    o_low = (org_name or "").strip().lower()
    c_low = (channel or "").strip().lower()

    if ct_upper in ("DM", "GROUP_DM", "GUILD_VOICE", "1", "3"):
        return ("EXCLUDED_DM_PRIVATE", 0.0)

    if any(pat in c_low for pat in PRIVATE_ADMIN_CHANNEL_PATTERNS):
        return ("EXCLUDED_DM_PRIVATE", 0.0)

    if any(k in c_low for k in BLOG_CHANNEL_KEYWORDS) or ct_upper == "GUILD_ANNOUNCEMENT":
        return ("TIER_1A_BLOG", 2.4)

    if any(k in c_low for k in RND_CHANNEL_KEYWORDS):
        return ("TIER_1B_ORG_RND", 1.55)

    if any(sub in o_low for sub in MAKER_ORG_SUBSTRINGS):
        return ("TIER_2B_MAKER_ORGS", 1.0)

    return ("TIER_3_TECH_LINUX", 0.85)


def tier_included_in_scope(tier: str, scope: str) -> bool:
    if scope == "blog-only":
        return tier in ("TIER_1A_BLOG", "TIER_1B_ORG_RND")
    if scope == "maker":
        return tier in (
            "TIER_1A_BLOG",
            "TIER_1B_ORG_RND",
            "TIER_2A_MAKER_SUPPLIERS",
            "TIER_2B_MAKER_ORGS",
        )
    if scope == "maker+tech":
        return tier in (
            "TIER_1A_BLOG",
            "TIER_1B_ORG_RND",
            "TIER_2A_MAKER_SUPPLIERS",
            "TIER_2B_MAKER_ORGS",
            "TIER_3_TECH_LINUX",
        )
    if scope == "all":
        return True
    return False


def stitch_channel_messages(
    ordered_msgs: List[Tuple[Optional[datetime.datetime], int, str, str]],
    is_blog_channel: bool,
    stitch_minutes: float = 8.0,
) -> List[Tuple[str, str]]:
    if not ordered_msgs:
        return []

    max_gap_sec = stitch_minutes * 60.0
    stitched: List[Tuple[Optional[datetime.datetime], str, str]] = []

    for dt, _mid, ts_str, text in ordered_msgs:
        if not text:
            continue

        if stitched:
            prev_dt, prev_ts, prev_text = stitched[-1]
            if text == prev_text and prev_dt and dt and 0 <= (dt - prev_dt).total_seconds() <= 1200:
                continue

            wc_curr = len(text.split())
            if is_blog_channel and wc_curr <= 6 and prev_dt and dt and 0 <= (dt - prev_dt).total_seconds() <= 7200:
                if any(k in text.lower() for k in ("pic", "picture", "photo", "video", "image", "oops")):
                    continue

            gap = (dt - prev_dt).total_seconds() if (prev_dt and dt) else None
            if gap is not None and 0 <= gap <= max_gap_sec:
                wc_prev = len(prev_text.split())
                hit_char_cap = len(prev_text) >= 1750
                prev_open_ended = prev_text[-1:] not in ".!?\"')"
                both_substantial = (wc_prev >= 45 and wc_curr >= 35 and gap <= 300)
                blog_continuation = (is_blog_channel and wc_curr >= 18)

                if blog_continuation or hit_char_cap or (prev_open_ended and wc_prev >= 30 and wc_curr >= 20) or both_substantial:
                    stitched[-1] = (dt, prev_ts, prev_text + "\n\n" + text)
                    continue

        stitched.append((dt, ts_str, text))

    return [(ts_str, txt) for _dt, ts_str, txt in stitched]


def load_discord_gdpr_package(
    pkg_dir: str, stitch_minutes: float = 8.0
) -> Tuple[List[PostRecord], Dict[str, Dict[str, int]], Dict[str, Dict[str, object]]]:
    index_map: Dict[str, str] = {}
    idx_path = os.path.join(pkg_dir, "index.json")
    if os.path.isfile(idx_path):
        try:
            with open(idx_path, "r", encoding="utf-8", errors="replace") as f:
                raw_idx = json.load(f)
            if isinstance(raw_idx, dict):
                index_map = {str(k): str(v or "") for k, v in raw_idx.items()}
        except Exception as exc:
            print(f"[WARN] Could not parse {idx_path}: {exc}", file=sys.stderr)

    records: List[PostRecord] = []
    domain_summary: Dict[str, Dict[str, int]] = collections.defaultdict(
        lambda: {"channels": 0, "raw_msgs": 0, "stitched_posts": 0, "raw_words": 0}
    )
    org_breakdown: Dict[str, Dict[str, object]] = collections.defaultdict(
        lambda: {"role": "", "channels": 0, "raw_msgs": 0, "long_posts": 0, "raw_words": 0, "long_words": 0}
    )

    for entry in sorted(os.listdir(pkg_dir)):
        sub = os.path.join(pkg_dir, entry)
        if not os.path.isdir(sub):
            continue

        chan_path = os.path.join(sub, "channel.json")
        msg_json_path = os.path.join(sub, "messages.json")
        msg_csv_path = os.path.join(sub, "messages.csv")
        if not os.path.isfile(msg_json_path) and not os.path.isfile(msg_csv_path):
            continue

        cdata: Dict = {}
        if os.path.isfile(chan_path):
            try:
                with open(chan_path, "r", encoding="utf-8", errors="replace") as f:
                    cdata = json.load(f)
            except Exception:
                cdata = {}

        cid = str(cdata.get("id") or entry.lstrip("c"))
        ctype = str(cdata.get("type") or "UNKNOWN")
        idx_label = index_map.get(cid, "")

        if ctype.upper() in ("DM", "GROUP_DM", "1", "3"):
            org_name = f"[{ctype.upper()}]"
            chan_name = idx_label or ctype
        else:
            org_obj = cdata.get("guild")
            if isinstance(org_obj, dict) and org_obj.get("name"):
                org_name = str(org_obj["name"])
            elif "," in idx_label:
                org_name = idx_label.rsplit(",", 1)[1].strip()
            else:
                org_name = "Unknown Org"
            chan_name = str(
                cdata.get("name")
                or (idx_label.split(",", 1)[0].strip() if idx_label else cid)
            )

        tier, weight = classify_channel_domain(org_name, chan_name, ctype)
        is_blog = (tier == "TIER_1A_BLOG")

        raw_items: List[Tuple[Optional[datetime.datetime], int, str, str]] = []
        if os.path.isfile(msg_json_path):
            try:
                with open(msg_json_path, "r", encoding="utf-8", errors="replace") as f:
                    data = json.load(f)
                if isinstance(data, list):
                    for i, m in enumerate(data):
                        if not isinstance(m, dict):
                            continue
                        raw_txt = str(m.get("Contents") if "Contents" in m else m.get("content", "") or "")
                        cleaned = clean_post_text(raw_txt)
                        ts_str = str(m.get("Timestamp") or m.get("timestamp") or f"msg-{i+1}")
                        mid_raw = m.get("ID") or m.get("id") or i
                        try:
                            mid = int(mid_raw)
                        except (ValueError, TypeError):
                            mid = i
                        raw_items.append((parse_ts(ts_str), mid, ts_str, cleaned))
            except Exception as exc:
                print(f"[WARN] Failed reading {msg_json_path}: {exc}", file=sys.stderr)
        elif os.path.isfile(msg_csv_path):
            try:
                with open(msg_csv_path, "r", encoding="utf-8", errors="replace") as f:
                    reader = csv.DictReader(f)
                    for i, row in enumerate(reader):
                        raw_txt = str(row.get("Contents") or row.get("Content") or row.get("content") or "")
                        cleaned = clean_post_text(raw_txt)
                        ts_str = str(row.get("Timestamp") or row.get("Date") or f"row-{i+1}")
                        mid_raw = row.get("ID") or i
                        try:
                            mid = int(mid_raw)
                        except (ValueError, TypeError):
                            mid = i
                        raw_items.append((parse_ts(ts_str), mid, ts_str, cleaned))
            except Exception as exc:
                print(f"[WARN] Failed reading {msg_csv_path}: {exc}", file=sys.stderr)

        raw_items.sort(key=lambda x: (x[0] or datetime.datetime.min, x[1]))

        raw_word_sum = sum(len(x[3].split()) for x in raw_items if x[3])
        ds = domain_summary[tier]
        ds["channels"] += 1
        ds["raw_msgs"] += len(raw_items)
        ds["raw_words"] += raw_word_sum

        stitched_posts = stitch_channel_messages(raw_items, is_blog_channel=is_blog, stitch_minutes=stitch_minutes)
        ds["stitched_posts"] += len(stitched_posts)

        if tier in ("TIER_1A_BLOG", "TIER_1B_ORG_RND", "TIER_2A_MAKER_SUPPLIERS", "TIER_2B_MAKER_ORGS"):
            ob = org_breakdown[org_name]
            if "primary" in org_name.lower() or "blog" in org_name.lower():
                ob["role"] = "Primary Maker Org (Blog, R&D & Community)"
            elif org_name.lower() in MAKER_SUPPLIER_COMPANIES:
                ob["role"] = "Maker Supplier / Webstore Company"
            elif org_name.lower() in OPEN_SOURCE_MAKER_ORGS or any(s in org_name.lower() for s in MAKER_ORG_SUBSTRINGS):
                ob["role"] = "Open-Source Hardware / Firmware Org"
            else:
                ob["role"] = "Dedicated #3d-printing Channel (Mixed Server)"
            ob["channels"] = int(ob["channels"]) + 1
            ob["raw_msgs"] = int(ob["raw_msgs"]) + len(raw_items)
            ob["raw_words"] = int(ob["raw_words"]) + raw_word_sum

        for ts_str, text in stitched_posts:
            src_label = f"{org_name} / #{chan_name} ({ts_str[:10]})"
            wc = len(WORD_RE.findall(strip_code_for_prose_metrics(text)))
            if wc >= 60 and org_name in org_breakdown:
                org_breakdown[org_name]["long_posts"] = int(org_breakdown[org_name]["long_posts"]) + 1
                org_breakdown[org_name]["long_words"] = int(org_breakdown[org_name]["long_words"]) + wc
            records.append(
                PostRecord(
                    source=src_label,
                    org=org_name,
                    channel=chan_name,
                    tier=tier,
                    weight=weight,
                    timestamp=ts_str,
                    text=text,
                )
            )

    return records, domain_summary, org_breakdown


def load_standalone_file(
    filepath: str, author_filter: str = "", stitch_minutes: float = 8.0
) -> List[PostRecord]:
    ext = os.path.splitext(filepath)[1].lower()
    fname = os.path.basename(filepath)
    author_q = author_filter.strip().lower()
    records: List[PostRecord] = []

    if ext == ".json":
        try:
            with open(filepath, "r", encoding="utf-8", errors="replace") as f:
                data = json.load(f)
        except Exception as exc:
            print(f"[WARN] Failed reading standalone JSON {filepath}: {exc}", file=sys.stderr)
            return []
        org_name = ((data.get("guild") or {}).get("name") if isinstance(data, dict) else None) or "Standalone Export"
        chan_name = ((data.get("channel") or {}).get("name") if isinstance(data, dict) else None) or os.path.splitext(fname)[0]
        ctype = ((data.get("channel") or {}).get("type") if isinstance(data, dict) else None) or "GUILD_TEXT"
        tier, weight = classify_channel_domain(org_name, chan_name, str(ctype))
        if tier.startswith("EXCLUDED"):
            tier, weight = ("TIER_2B_MAKER_ORGS", 1.2)

        messages = (
            data.get("messages", [])
            if isinstance(data, dict)
            else (data if isinstance(data, list) else [])
        )
        ordered: List[Tuple[Optional[datetime.datetime], int, str, str]] = []
        for idx, msg in enumerate(messages):
            if not isinstance(msg, dict):
                continue
            if "Contents" in msg and "author" not in msg:
                content = clean_post_text(str(msg.get("Contents") or ""))
                ts = str(msg.get("Timestamp") or f"msg-{idx+1}")
            else:
                auth = msg.get("author", {})
                auth_name = (
                    f"{auth.get('name', '')} {auth.get('nickname', '')}".lower()
                    if isinstance(auth, dict)
                    else str(auth).lower()
                )
                if author_q and author_q not in auth_name:
                    continue
                content = clean_post_text(str(msg.get("content", "")))
                ts = str(msg.get("timestamp", f"msg-{idx+1}"))
            if content:
                ordered.append((parse_ts(ts), idx, ts, content))

        ordered.sort(key=lambda x: (x[0] or datetime.datetime.min, x[1]))
        for ts_str, text in stitch_channel_messages(ordered, is_blog_channel=("blog" in chan_name.lower()), stitch_minutes=stitch_minutes):
            records.append(PostRecord(f"{fname} ({ts_str[:10]})", org_name, chan_name, tier, weight, ts_str, text))

    elif ext == ".csv":
        with open(filepath, "r", encoding="utf-8", errors="replace") as f:
            reader = csv.DictReader(f)
            ordered = []
            for idx, row in enumerate(reader):
                auth_name = str(row.get("Author") or row.get("author") or row.get("Username") or "").lower()
                if author_q and auth_name and author_q not in auth_name:
                    continue
                content = clean_post_text(
                    str(row.get("Contents") or row.get("Content") or row.get("content") or row.get("Message") or "")
                )
                if content:
                    ts = str(row.get("Timestamp") or row.get("Date") or f"row-{idx+1}")
                    ordered.append((parse_ts(ts), idx, ts, content))
        ordered.sort(key=lambda x: (x[0] or datetime.datetime.min, x[1]))
        for ts_str, text in stitch_channel_messages(ordered, is_blog_channel=False, stitch_minutes=stitch_minutes):
            records.append(PostRecord(f"{fname} ({ts_str[:10]})", "Standalone CSV", fname, "TIER_2B_MAKER_ORGS", 1.2, ts_str, text))

    elif ext in (".txt", ".md"):
        with open(filepath, "r", encoding="utf-8", errors="replace") as f:
            raw = f.read().replace("\r\n", "\n")

        header_matches = list(DISCORD_TXT_HEADER_RE.finditer(raw))
        if header_matches:
            for idx, m in enumerate(header_matches):
                ts = m.group(1).strip()
                auth_name = m.group(2).strip().lower()
                start_pos = m.end()
                end_pos = header_matches[idx + 1].start() if idx + 1 < len(header_matches) else len(raw)
                if author_q and author_q not in auth_name:
                    continue
                c = clean_post_text(raw[start_pos:end_pos])
                if c:
                    records.append(PostRecord(f"{fname}:{ts}", "Standalone Log", fname, "TIER_1B_ORG_RND", 1.5, ts, c))
        else:
            chunks = re.split(r"\n\s*---+\s*\n|\n{3,}", raw)
            for idx, chk in enumerate(chunks, 1):
                c = clean_post_text(chk)
                if c:
                    records.append(PostRecord(f"{fname}#block-{idx}", "Standalone Doc", fname, "TIER_1A_BLOG", 2.0, f"block-{idx}", c))

    return records


def compute_deep_stylometrics(records: List[PostRecord], min_words: int = 60) -> Dict:
    long_posts: List[Tuple[PostRecord, int]] = []
    all_sent_lengths: List[int] = []
    adj_sent_deltas: List[int] = []
    first_sent_lengths: List[int] = []
    mid_sent_lengths: List[int] = []
    last_sent_lengths: List[int] = []

    all_para_sent_counts: List[int] = []
    paras_per_post: List[int] = []

    punct_counts: collections.Counter = collections.Counter()
    clause_counts: collections.Counter = collections.Counter()
    causal_counts: collections.Counter = collections.Counter()
    pronoun_counts: collections.Counter = collections.Counter()
    conviction_counter: collections.Counter = collections.Counter()
    candor_counter: collections.Counter = collections.Counter()
    all_caps_words: collections.Counter = collections.Counter()
    contraction_pair_counts: Dict[str, List[int]] = {label: [0, 0] for label, _, _ in CONTRACTION_PAIRS}
    ai_trope_counts: collections.Counter = collections.Counter()
    sig_phrase_counts: collections.Counter = collections.Counter()
    use_vs_utilize = [0, 0]

    post_opening_moves: collections.Counter = collections.Counter()
    post_closing_moves: collections.Counter = collections.Counter()

    total_words = 0

    for rec in records:
        prose_clean = strip_code_for_prose_metrics(rec.text)
        words = [w for w in WORD_RE.findall(prose_clean) if w != "CODE_TOKEN"]
        w_count = len(words)
        if w_count < min_words:
            continue

        long_posts.append((rec, w_count))
        total_words += w_count

        # Punctuation & emphasis counts
        punct_counts["contractions"] += len(CONTRACTION_RE.findall(prose_clean))
        punct_counts["ellipses_(...)"] += len(ELLIPSIS_RE.findall(prose_clean))
        punct_counts["parentheticals_(...)"] += len(re.findall(r"\([^()\n]{3,140}\)", prose_clean))
        punct_counts["em_or_spaced_dashes"] += len(re.findall(r"—|--|\s-\s", prose_clean))
        punct_counts["bold_spans"] += len(re.findall(r"\*\*[^*\n]+\*\*", prose_clean))
        punct_counts["italic_spans"] += len(re.findall(r"(?<!\*)\*[^*\n]+\*(?!\*)", prose_clean))
        punct_counts["exclamations"] += prose_clean.count("!")
        punct_counts["questions"] += prose_clean.count("?")
        punct_counts["semicolons"] += prose_clean.count(";")
        punct_counts["colons"] += len(re.findall(r":(?=\s)", prose_clean))
        punct_counts["double_space_after_period"] += len(DOUBLE_SPACE_AFTER_PUNCT_RE.findall(prose_clean))

        for cw in ALL_CAPS_WORD_RE.findall(prose_clean):
            if cw not in TECH_ACRONYMS and cw != "CODE" and not cw.isdigit():
                punct_counts["all_caps_emphasis"] += 1
                all_caps_words[cw] += 1

        # Clause & causal connectors
        for label, rx in CLAUSE_PIVOT_PATTERNS:
            clause_counts[label] += len(rx.findall(prose_clean))
        for label, rx in CAUSAL_CONNECTOR_PATTERNS:
            causal_counts[label] += len(rx.findall(prose_clean))

        # Contraction head-to-head pairs
        for label, uncontracted_rx, contracted_rx in CONTRACTION_PAIRS:
            contraction_pair_counts[label][0] += len(uncontracted_rx.findall(prose_clean))
            contraction_pair_counts[label][1] += len(contracted_rx.findall(prose_clean))

        # AI tropes & signature idioms
        for label, rx in BANNED_AI_TROPES:
            ai_trope_counts[label] += len(rx.findall(prose_clean))
        for label, rx in SIGNATURE_PHRASE_PATTERNS:
            sig_phrase_counts[label] += len(rx.findall(prose_clean))

        use_vs_utilize[0] += len(re.findall(r"\bus(?:e|es|ed|ing)\b", prose_clean, re.IGNORECASE))
        use_vs_utilize[1] += len(re.findall(r"\butiliz(?:e|es|ed|ing)\b", prose_clean, re.IGNORECASE))

        # Word-level persona, conviction & candor
        for w in words:
            wl = w.lower()
            if wl in ("i", "my", "me", "myself", "i'm", "i've", "i'll", "i'd"):
                pronoun_counts["first_singular"] += 1
            elif wl in ("we", "our", "us", "ourselves", "we're", "we've", "we'll"):
                pronoun_counts["first_plural"] += 1
            elif wl in ("you", "your", "yours", "yourself", "you're", "you'll", "you've"):
                pronoun_counts["second_person"] += 1

            if wl in CONVICTION_WORDS:
                conviction_counter[wl] += 1
            if wl in CANDOR_HEDGE_WORDS:
                candor_counter[wl] += 1

        # Paragraph & sentence structure
        paragraphs = [
            p.strip()
            for p in re.split(r"\n\s*\n", prose_clean)
            if p.strip() and not p.strip().startswith((">", "#", "- ", "* "))
        ]
        if paragraphs:
            paras_per_post.append(len(paragraphs))

            # Discourse opening move classification on first paragraph
            p0_low = paragraphs[0].lower()
            if re.match(r"^(?:just (?:a|an|wanted|to)|today|finally|quick update|minor update|as many of you|before i left)", p0_low):
                post_opening_moves["Progress / Bench Status Hook ('Just an update...', 'Today was spent...')"] += 1
            elif re.match(r"^(?:as you can see|attached|here is|in this image|you can see)", p0_low):
                post_opening_moves["Visual-First Walkthrough ('As you can see...', 'In this image...')"] += 1
            elif "?" in paragraphs[0].split(".")[0]:
                post_opening_moves["Rhetorical / Framing Question ('Why put it up top...?', 'How are we going to...?')"] += 1
            elif any(k in p0_low[:120] for k in ("issue", "problem", "didn't like", "struggling", "pain", "challenge", "unfortunately", "limitation")):
                post_opening_moves["Problem / Frustration Catalyst ('I didn't like how...', 'Right now X is struggling...')"] += 1
            else:
                post_opening_moves["Direct Technical Premise / Action Statement"] += 1

            # Discourse closing move classification on final paragraph
            plast = paragraphs[-1]
            plast_low = plast.lower()
            if any(k in plast_low[-160:] for k in ("keep an eye", "soon", "future", "next update", "more will come", "more to come", "stay tuned", "cannot wait")):
                post_closing_moves["Forward Roadmap Teaser ('Keep an eye out...', 'more will come on that...')"] += 1
            elif any(k in plast_low[-160:] for k in ("let me know", "feedback", "thoughts", "what do you think", "thanks everyone", "curious")):
                post_closing_moves["Community Feedback Invite / Sign-Off"] += 1
            elif plast.rstrip().endswith("?"):
                post_closing_moves["Conversational Tag / Check Question ('...doesn't it?')"] += 1
            elif "..." in plast[-90:] or "(" in plast[-90:]:
                post_closing_moves["Wry Parenthetical or Trailing Ellipsis Kicker"] += 1
            else:
                post_closing_moves["Practical Engineering Verdict / Takeaway"] += 1

        for p in paragraphs:
            sents = [s.strip() for s in SENTENCE_SPLIT_RE.split(p) if s.strip()]
            valid_lens: List[int] = []
            for s in sents:
                s_words = [w for w in WORD_RE.findall(s) if w != "CODE_TOKEN"]
                if len(s_words) >= 3:
                    valid_lens.append(len(s_words))
                    all_sent_lengths.append(len(s_words))
            if valid_lens:
                all_para_sent_counts.append(len(valid_lens))
                for idx_l in range(len(valid_lens) - 1):
                    adj_sent_deltas.append(abs(valid_lens[idx_l + 1] - valid_lens[idx_l]))
                if len(valid_lens) >= 3:
                    first_sent_lengths.append(valid_lens[0])
                    mid_sent_lengths.extend(valid_lens[1:-1])
                    last_sent_lengths.append(valid_lens[-1])

    return {
        "total_posts_scanned": len(records),
        "qualifying_long_posts": len(long_posts),
        "long_posts": long_posts,
        "total_words": total_words,
        "sent_lengths": all_sent_lengths,
        "adj_sent_deltas": adj_sent_deltas,
        "first_sent_lengths": first_sent_lengths,
        "mid_sent_lengths": mid_sent_lengths,
        "last_sent_lengths": last_sent_lengths,
        "para_sent_counts": all_para_sent_counts,
        "paras_per_post": paras_per_post,
        "punct_counts": punct_counts,
        "clause_counts": clause_counts,
        "causal_counts": causal_counts,
        "pronoun_counts": pronoun_counts,
        "conviction_counter": conviction_counter,
        "candor_counter": candor_counter,
        "all_caps_words": all_caps_words,
        "contraction_pair_counts": contraction_pair_counts,
        "ai_trope_counts": ai_trope_counts,
        "sig_phrase_counts": sig_phrase_counts,
        "use_vs_utilize": use_vs_utilize,
        "post_opening_moves": post_opening_moves,
        "post_closing_moves": post_closing_moves,
    }


def extract_stratified_exemplars(
    long_posts: List[Tuple[PostRecord, int]], per_category: int = 6
) -> Dict[str, List[Tuple[float, str, str, int]]]:
    cat_1_terms = {
        "design", "goal", "concept", "project", "working", "philosophy", "approach",
        "direction", "vision", "architecture", "system", "building", "purpose", "idea",
    }
    cat_2_terms = {
        "because", "since", "prevents", "causes", "results", "instead", "thermal",
        "heat", "preload", "torque", "creep", "airflow", "pressure", "stiffness",
        "rigidity", "tolerance", "clearance", "friction", "expansion", "mass",
        "resonance", "kinematic", "belt", "bearing", "chamber", "moisture",
    }
    cat_3_action_terms = {
        "install", "tighten", "loosen", "clean", "lubricate", "lube", "rails",
        "square", "squaring", "tension", "calibrate", "calibration", "tune", "tuning",
        "measure", "adjust", "recommend", "avoid", "careful", "check", "replace",
        "bearings", "seat", "threads", "screw", "wrench", "grease", "alcohol", "ipa",
    }
    cat_3_coaching_markers = (
        "make sure", "be sure to", "you should", "do not", "never", "first", "next",
        "if you", "when you", "stop", "until", "recommend",
    )
    cat_4_terms = {
        "tried", "tested", "testing", "failed", "issue", "downside", "trade-off",
        "tradeoff", "compromise", "iteration", "prototype", "version", "revision",
        "changed", "switched", "scrapped", "reworked", "learned", "originally",
        "unfortunately", "challenge", "bottleneck", "limitation", "versus",
    }
    cat_5_phrases = (
        "like a", "think of", "basically", "essentially", "rabbit hole", "overkill",
        "magic", "magical", "pain", "sanity", "frankly", "honestly", "sledgehammer",
        "scalpel", "nightmare", "beauty", "caveman", "mona lisa", "spreadsheets",
    )

    chat_noise_starts = (
        "yeah", "yep", "yup", "lol", "lmao", "haha", "hey ", "hi ", "oh ", "nah",
        "idk", "imo", "tbh", "bro", "dude", "thanks ", "thank you",
    )

    buckets: Dict[str, List[Tuple[float, str, str, int]]] = {
        "cat1_hooks": [],
        "cat2_physics_why": [],
        "cat3_build_guidance": [],
        "cat4_tradeoffs_iterations": [],
        "cat5_analogies_humor": [],
    }

    for rec, _wc in long_posts:
        text_no_fenced = FENCED_CODE_RE.sub("\n\n", rec.text)
        paras = [p.strip() for p in re.split(r"\n\s*\n", text_no_fenced) if p.strip()]

        for p_idx, p in enumerate(paras):
            if p.startswith((">", "```", "http")):
                continue
            p_no_url = URL_RE.sub("", p).strip()
            pw = WORD_RE.findall(p_no_url)
            pw_len = len(pw)
            if not (70 <= pw_len <= 275):
                continue

            p_low = p_no_url.lower()
            if p_low.startswith(chat_noise_starts):
                continue
            if "[collaborator]" in p_low:
                # Prefer self-contained exemplars that don't depend on external user tags
                collab_penalty = 0.65
            else:
                collab_penalty = 1.0

            sents = [s.strip() for s in SENTENCE_SPLIT_RE.split(p_no_url) if s.strip()]
            if len(sents) < 3:
                continue

            lower_words = [w.lower() for w in pw]
            paren_hits = len(re.findall(r"\([^()\n]{4,140}\)", p_no_url))
            dash_hits = len(re.findall(r"—|--|\s-\s", p_no_url))
            bold_bonus = 1.0 if "**" in p_no_url else 0.0
            w_mult = rec.weight * collab_penalty

            # Category 1: Project Introductions, Hooks & Design Philosophy
            if p_idx == 0 and rec.tier in ("TIER_1A_BLOG", "TIER_1B_ORG_RND"):
                c1_hits = sum(1 for w in lower_words if w in cat_1_terms)
                if c1_hits >= 3:
                    s1 = (c1_hits * 2.2 + paren_hits * 1.2 + bold_bonus) * w_mult
                    buckets["cat1_hooks"].append((s1, rec.source, p_no_url, pw_len))

            # Category 2: Physical / Mechanical / Thermal "Why"
            c2_hits = sum(1 for w in lower_words if w in cat_2_terms)
            if c2_hits >= 4:
                s2 = (c2_hits * 2.4 + paren_hits * 1.5 + bold_bonus) * w_mult
                buckets["cat2_physics_why"].append((s2, rec.source, p_no_url, pw_len))

            # Category 3: Hands-On Build, Calibration, Rail/Belt Prep & Troubleshooting Guidance
            c3_hits = sum(1 for w in lower_words if w in cat_3_action_terms)
            c3_coach = sum(1 for m in cat_3_coaching_markers if m in p_low)
            if c3_hits >= 3 and c3_coach >= 2:
                # Boost Supplier / Community / Tuning hands-on instructional posts so Mode B shines
                mode_b_mult = 1.35 if rec.tier in ("TIER_2A_MAKER_SUPPLIERS", "TIER_2B_MAKER_ORGS") or "tuning" in rec.channel.lower() or "questions" in rec.channel.lower() else 1.0
                s3 = (c3_hits * 2.2 + c3_coach * 2.5 + bold_bonus) * w_mult * mode_b_mult
                buckets["cat3_build_guidance"].append((s3, rec.source, p_no_url, pw_len))

            # Category 4: Engineering Trade-Offs, Iteration Logs & What Failed
            c4_hits = sum(1 for w in lower_words if w in cat_4_terms)
            if c4_hits >= 3:
                s4 = (c4_hits * 2.6 + paren_hits * 1.2 + dash_hits * 0.8) * w_mult
                buckets["cat4_tradeoffs_iterations"].append((s4, rec.source, p_no_url, pw_len))

            # Category 5: Signature Analogies, Parentheticals & Dry Maker Humor
            c5_phrase_hits = sum(1 for ph in cat_5_phrases if ph in p_low)
            ellip_hits = len(ELLIPSIS_RE.findall(p_no_url))
            if (paren_hits >= 1 or ellip_hits >= 1) and (c5_phrase_hits >= 1 or paren_hits >= 2):
                s5 = (paren_hits * 3.0 + c5_phrase_hits * 3.0 + ellip_hits * 1.8 + dash_hits * 1.0) * w_mult
                buckets["cat5_analogies_humor"].append((s5, rec.source, p_no_url, pw_len))

    used_signatures: Set[str] = set()
    final_buckets: Dict[str, List[Tuple[float, str, str, int]]] = {}

    for key in (
        "cat1_hooks",
        "cat2_physics_why",
        "cat3_build_guidance",
        "cat4_tradeoffs_iterations",
        "cat5_analogies_humor",
    ):
        candidates = sorted(buckets[key], key=lambda x: x[0], reverse=True)
        picked: List[Tuple[float, str, str, int]] = []
        for item in candidates:
            sig = " ".join(WORD_RE.findall(item[2].lower())[:14])
            if sig in used_signatures:
                continue
            used_signatures.add(sig)
            picked.append(item)
            if len(picked) >= per_category:
                break
        final_buckets[key] = picked

    return final_buckets


def _fmt_dist(vals: List[int]) -> Tuple[str, str, str, str, str]:
    if not vals:
        return ("N/A", "N/A", "N/A", "N/A", "N/A")
    mean_v = f"{statistics.mean(vals):.1f}"
    med_v = f"{statistics.median(vals):.1f}"
    sd_v = f"{statistics.stdev(vals):.1f}" if len(vals) > 1 else "0.0"
    if len(vals) >= 10:
        qs = statistics.quantiles(vals, n=4)
        decs = statistics.quantiles(vals, n=10)
        iqr_v = f"{qs[0]:.0f}–{qs[2]:.0f}"
        p10_90 = f"{decs[0]:.0f}–{decs[8]:.0f}"
    else:
        iqr_v = f"{min(vals)}–{max(vals)}"
        p10_90 = iqr_v
    return (mean_v, med_v, iqr_v, p10_90, sd_v)


def _sent_band_pcts(vals: List[int]) -> Dict[str, str]:
    n = max(len(vals), 1)
    return {
        "3_9": f"{sum(1 for v in vals if 3 <= v <= 9) * 100.0 / n:.1f}%",
        "10_17": f"{sum(1 for v in vals if 10 <= v <= 17) * 100.0 / n:.1f}%",
        "18_27": f"{sum(1 for v in vals if 18 <= v <= 27) * 100.0 / n:.1f}%",
        "28_39": f"{sum(1 for v in vals if 28 <= v <= 39) * 100.0 / n:.1f}%",
        "40_plus": f"{sum(1 for v in vals if v >= 40) * 100.0 / n:.1f}%",
    }


def _para_len_pcts(vals: List[int]) -> Dict[str, str]:
    n = max(len(vals), 1)
    return {
        "1": f"{sum(1 for v in vals if v == 1) * 100.0 / n:.1f}%",
        "2": f"{sum(1 for v in vals if v == 2) * 100.0 / n:.1f}%",
        "3": f"{sum(1 for v in vals if v == 3) * 100.0 / n:.1f}%",
        "4": f"{sum(1 for v in vals if v == 4) * 100.0 / n:.1f}%",
        "5_plus": f"{sum(1 for v in vals if v >= 5) * 100.0 / n:.1f}%",
    }


def format_deep_report(
    all_maker: Dict,
    blog_only: Dict,
    rnd_only: Dict,
    suppliers_orgs: Dict,
    domain_summary: Dict[str, Dict[str, int]],
    org_breakdown: Dict[str, Dict[str, object]],
    exemplars: Dict[str, List[Tuple[float, str, str, int]]],
    inbox_dir: str,
    scope: str,
    min_words: int,
) -> str:
    b_mean, b_med, b_iqr, b_p1090, b_sd = _fmt_dist(blog_only["sent_lengths"])
    r_mean, r_med, r_iqr, r_p1090, r_sd = _fmt_dist(rnd_only["sent_lengths"])
    s_mean, s_med, s_iqr, s_p1090, s_sd = _fmt_dist(suppliers_orgs["sent_lengths"])
    m_mean, m_med, m_iqr, m_p1090, m_sd = _fmt_dist(all_maker["sent_lengths"])

    b_swing = f"{statistics.mean(blog_only['adj_sent_deltas']):.1f}" if blog_only["adj_sent_deltas"] else "N/A"
    r_swing = f"{statistics.mean(rnd_only['adj_sent_deltas']):.1f}" if rnd_only["adj_sent_deltas"] else "N/A"
    s_swing = f"{statistics.mean(suppliers_orgs['adj_sent_deltas']):.1f}" if suppliers_orgs["adj_sent_deltas"] else "N/A"
    m_swing = f"{statistics.mean(all_maker['adj_sent_deltas']):.1f}" if all_maker["adj_sent_deltas"] else "N/A"

    b_bands = _sent_band_pcts(blog_only["sent_lengths"])
    r_bands = _sent_band_pcts(rnd_only["sent_lengths"])
    s_bands = _sent_band_pcts(suppliers_orgs["sent_lengths"])
    m_bands = _sent_band_pcts(all_maker["sent_lengths"])

    b_pchunk = _para_len_pcts(blog_only["para_sent_counts"])
    r_pchunk = _para_len_pcts(rnd_only["para_sent_counts"])
    s_pchunk = _para_len_pcts(suppliers_orgs["para_sent_counts"])
    m_pchunk = _para_len_pcts(all_maker["para_sent_counts"])

    tw_b = max(blog_only["total_words"], 1)
    tw_r = max(rnd_only["total_words"], 1)
    tw_s = max(suppliers_orgs["total_words"], 1)
    tw_m = max(all_maker["total_words"], 1)

    lines = [
        "# 📊 Deep Author Voice, Tone & Cadence Telemetry Report (Pass 2)",
        "",
        f"- **Corpus Inbox**: `{inbox_dir}`",
        f"- **Active Domain Scope**: `{scope}` *(includes Primary Author Blog/R&D, Maker Suppliers/Webstore Companies, and Open-Source Printer/Firmware Orgs; excludes gaming servers, private DMs, and internal business/admin channels)*",
        f"- **Qualifying Threshold**: `>= {min_words}` prose words per post (after chronological stitching & code/URL stripping)",
        f"- **Total Qualifying Maker Posts**: `{all_maker['qualifying_long_posts']:,}` posts (`{all_maker['total_words']:,}` prose words)",
        f"  - **Sub-Register 1 — Primary Author Blog & Announcements (`Tier 1A`)**: `{blog_only['qualifying_long_posts']:,}` posts (`{blog_only['total_words']:,}` words)",
        f"  - **Sub-Register 2 — Primary Author R&D & Subsystem Engineering (`Tier 1B`)**: `{rnd_only['qualifying_long_posts']:,}` posts (`{rnd_only['total_words']:,}` words)",
        f"  - **Sub-Register 3 — Maker Suppliers, Companies & Open-Source Orgs (`Tier 2A + 2B`)**: `{suppliers_orgs['qualifying_long_posts']:,}` posts (`{suppliers_orgs['total_words']:,}` words)",
        "",
        "---",
        "",
        "## 0. Maker Orgs, Supplier Companies & Domain Filtering Breakdown",
        "",
        "### 0.1 Domain Tier Summary",
        "",
        "| Ecosystem Tier | Status | Channels | Raw Messages | Stitched Posts | Raw Words |",
        "| :--- | :---: | :---: | :---: | :---: | :---: |",
    ]

    tier_labels = [
        ("TIER_1A_BLOG", "Tier 1A: Primary Author Blog & Announcements (`2.4x`)"),
        ("TIER_1B_ORG_RND", "Tier 1B: Primary Author R&D & Subsystem Engineering (`1.55x`)"),
        ("TIER_2A_MAKER_SUPPLIERS", "Tier 2A: Maker Suppliers & Hardware Webstore Companies (`1.15x`)"),
        ("TIER_2B_MAKER_ORGS", "Tier 2B: Open-Source Hardware/Firmware Orgs & Maker Channels (`1.0x`)"),
        ("TIER_3_TECH_LINUX", "Tier 3: General Linux / Sysadmin Communities"),
        ("EXCLUDED_GAMING_SOCIAL", "Filtered Out: Gaming Clans & Casual Social Servers"),
        ("EXCLUDED_DM_PRIVATE", "Filtered Out: Private DMs, Group DMs & Internal Admin/Business"),
    ]
    for t_key, t_title in tier_labels:
        ds = domain_summary.get(t_key, {"channels": 0, "raw_msgs": 0, "stitched_posts": 0, "raw_words": 0})
        if ds["channels"] == 0 and ds["raw_msgs"] == 0:
            continue
        inc = "✅ Included" if tier_included_in_scope(t_key, scope) else "🚫 Excluded"
        lines.append(
            f"| {t_title} | {inc} | `{ds['channels']}` | `{ds['raw_msgs']:,}` | `{ds['stitched_posts']:,}` | `{ds['raw_words']:,}` |"
        )

    lines.extend([
        "",
        "### 0.2 Included Maker Orgs, Hardware Suppliers & Project Communities",
        "",
        "| Organization / Company | Ecosystem Role | Channels | Raw Msgs | Long Posts (`>=60w`) | Long-Form Words | Total Raw Words |",
        "| :--- | :--- | :---: | :---: | :---: | :---: | :---: |",
    ])
    sorted_orgs = sorted(
        org_breakdown.items(),
        key=lambda kv: (int(kv[1]["long_words"]), int(kv[1]["raw_words"])),
        reverse=True,
    )
    for oname, ob in sorted_orgs:
        if int(ob["raw_msgs"]) == 0:
            continue
        lines.append(
            f"| **{oname}** | {ob['role']} | `{ob['channels']}` | `{int(ob['raw_msgs']):,}` | `{int(ob['long_posts']):,}` | `{int(ob['long_words']):,}` | `{int(ob['raw_words']):,}` |"
        )

    # Positional sentence arc in 3+ sentence paragraphs
    f_mean = f"{statistics.mean(all_maker['first_sent_lengths']):.1f}" if all_maker["first_sent_lengths"] else "N/A"
    mid_mean = f"{statistics.mean(all_maker['mid_sent_lengths']):.1f}" if all_maker["mid_sent_lengths"] else "N/A"
    last_mean = f"{statistics.mean(all_maker['last_sent_lengths']):.1f}" if all_maker["last_sent_lengths"] else "N/A"
    bf_mean = f"{statistics.mean(blog_only['first_sent_lengths']):.1f}" if blog_only["first_sent_lengths"] else "N/A"
    bmid_mean = f"{statistics.mean(blog_only['mid_sent_lengths']):.1f}" if blog_only["mid_sent_lengths"] else "N/A"
    blast_mean = f"{statistics.mean(blog_only['last_sent_lengths']):.1f}" if blog_only["last_sent_lengths"] else "N/A"

    lines.extend([
        "",
        "---",
        "",
        "## 1. Multi-Scale Sentence Cadence & Burstiness Across Sub-Registers",
        "",
        "### 1.1 Core Length & Beat-to-Beat Variation",
        "",
        "| Metric | Primary Blog (`1A`) | Engineering R&D (`1B`) | Suppliers & Orgs (`2A+2B`) | All Maker Combined |",
        "| :--- | :---: | :---: | :---: | :---: |",
        f"| **Mean Sentence Length** | `{b_mean}` w | `{r_mean}` w | `{s_mean}` w | `{m_mean}` w |",
        f"| **Median Sentence Length** | `{b_med}` w | `{r_med}` w | `{s_med}` w | `{m_med}` w |",
        f"| **Core Working Band (IQR 25–75%)** | `{b_iqr}` w | `{r_iqr}` w | `{s_iqr}` w | `{m_iqr}` w |",
        f"| **10th–90th Percentile Range** | `{b_p1090}` w | `{r_p1090}` w | `{s_p1090}` w | `{m_p1090}` w |",
        f"| **Sentence Length Std Dev** | `{b_sd}` w | `{r_sd}` w | `{s_sd}` w | `{m_sd}` w |",
        f"| **Beat-to-Beat Swing (`|S_i+1 - S_i|`)** | `{b_swing}` w | `{r_swing}` w | `{s_swing}` w | `{m_swing}` w |",
        f"| **3+ Sent Paragraph Arc (1st -> Mid -> Last)** | `{bf_mean} -> {bmid_mean} -> {blast_mean}` w | — | — | `{f_mean} -> {mid_mean} -> {last_mean}` w |",
        "",
        "### 1.2 Five-Band Sentence Length Distribution (`%` of Sentences)",
        "",
        "| Sentence Length Band | Functional Role in Cadence | Blog (`1A`) | R&D (`1B`) | Suppliers/Orgs (`2A+2B`) | All Maker |",
        "| :--- | :--- | :---: | :---: | :---: | :---: |",
        f"| **Punchy Beats (`3–9` words)** | Brisk openers, verdicts, dry kickers | `{b_bands['3_9']}` | `{r_bands['3_9']}` | `{s_bands['3_9']}` | `{m_bands['3_9']}` |",
        f"| **Crisp Declaratives (`10–17` words)** | Direct actions & status statements | `{b_bands['10_17']}` | `{r_bands['10_17']}` | `{s_bands['10_17']}` | `{m_bands['10_17']}` |",
        f"| **Core Cadence (`18–27` words)** | Primary clause-linked explanations | `{b_bands['18_27']}` | `{r_bands['18_27']}` | `{s_bands['18_27']}` | `{m_bands['18_27']}` |",
        f"| **Deep Causal (`28–39` words)** | Multi-clause physics / trade-off chains | `{b_bands['28_39']}` | `{r_bands['28_39']}` | `{s_bands['28_39']}` | `{m_bands['28_39']}` |",
        f"| **Extended Walkthroughs (`40+` words)** | Unbroken conversational chains | `{b_bands['40_plus']}` | `{r_bands['40_plus']}` | `{s_bands['40_plus']}` | `{m_bands['40_plus']}` |",
        "",
        "---",
        "",
        "## 2. Paragraph Chunking & Multi-Paragraph Discourse Structure",
        "",
        "### 2.1 Sentences per Paragraph Distribution",
        "",
        "| Paragraph Size | Blog (`1A`) | R&D (`1B`) | Suppliers/Orgs (`2A+2B`) | All Maker |",
        "| :--- | :---: | :---: | :---: | :---: |",
        f"| **1-Sentence Punch / Callout Block** | `{b_pchunk['1']}` | `{r_pchunk['1']}` | `{s_pchunk['1']}` | `{m_pchunk['1']}` |",
        f"| **2-Sentence Pair (Setup + Payoff)** | `{b_pchunk['2']}` | `{r_pchunk['2']}` | `{s_pchunk['2']}` | `{m_pchunk['2']}` |",
        f"| **3-Sentence Core Block** | `{b_pchunk['3']}` | `{r_pchunk['3']}` | `{s_pchunk['3']}` | `{m_pchunk['3']}` |",
        f"| **4-Sentence Block** | `{b_pchunk['4']}` | `{r_pchunk['4']}` | `{s_pchunk['4']}` | `{m_pchunk['4']}` |",
        f"| **5+ Sentence Dense Block** | `{b_pchunk['5_plus']}` | `{r_pchunk['5_plus']}` | `{s_pchunk['5_plus']}` | `{m_pchunk['5_plus']}` |",
        "",
        "### 2.2 Post Opening & Closing Rhetorical Moves (Blog `1A` vs. All Maker)",
        "",
        "**How Posts Open (Paragraph 1):**",
    ])
    b_open_tot = max(sum(blog_only["post_opening_moves"].values()), 1)
    m_open_tot = max(sum(all_maker["post_opening_moves"].values()), 1)
    for move, cnt in all_maker["post_opening_moves"].most_common():
        b_cnt = blog_only["post_opening_moves"].get(move, 0)
        lines.append(
            f"- **{move}**: Blog `{b_cnt * 100.0 / b_open_tot:.1f}%` (`{b_cnt}`) | All Maker `{cnt * 100.0 / m_open_tot:.1f}%` (`{cnt}`)"
        )

    lines.append("")
    lines.append("**How Posts Close (Final Paragraph):**")
    b_close_tot = max(sum(blog_only["post_closing_moves"].values()), 1)
    m_close_tot = max(sum(all_maker["post_closing_moves"].values()), 1)
    for move, cnt in all_maker["post_closing_moves"].most_common():
        b_cnt = blog_only["post_closing_moves"].get(move, 0)
        lines.append(
            f"- **{move}**: Blog `{b_cnt * 100.0 / b_close_tot:.1f}%` (`{b_cnt}`) | All Maker `{cnt * 100.0 / m_close_tot:.1f}%` (`{cnt}`)"
        )

    lines.extend([
        "",
        "---",
        "",
        "## 3. Clause-Linking Architecture & Causal Connectors (per 1,000 Words)",
        "",
        "### 3.1 Internal Comma-Pivots & Signature `'though'` Placement",
        "",
        "| Syntactic Connector | Blog (`1A`) `/1k` | R&D (`1B`) `/1k` | Suppliers/Orgs `/1k` | Total Maker Count |",
        "| :--- | :---: | :---: | :---: | :---: |",
    ])
    for label, _ in CLAUSE_PIVOT_PATTERNS:
        cb = blog_only["clause_counts"][label] * 1000.0 / tw_b
        cr = rnd_only["clause_counts"][label] * 1000.0 / tw_r
        cs = suppliers_orgs["clause_counts"][label] * 1000.0 / tw_s
        cm_tot = all_maker["clause_counts"][label]
        lines.append(f"| `{label}` | `{cb:.2f}` | `{cr:.2f}` | `{cs:.2f}` | `{cm_tot:,}` |")

    lines.extend([
        "",
        "### 3.2 Physical / Engineering Cause-and-Effect Connectors",
        "",
        "| Causal / Functional Connector | Blog (`1A`) `/1k` | R&D (`1B`) `/1k` | Suppliers/Orgs `/1k` | Total Maker Count |",
        "| :--- | :---: | :---: | :---: | :---: |",
    ])
    for label, _ in CAUSAL_CONNECTOR_PATTERNS:
        cb = blog_only["causal_counts"][label] * 1000.0 / tw_b
        cr = rnd_only["causal_counts"][label] * 1000.0 / tw_r
        cs = suppliers_orgs["causal_counts"][label] * 1000.0 / tw_s
        cm_tot = all_maker["causal_counts"][label]
        lines.append(f"| `{label}` | `{cb:.2f}` | `{cr:.2f}` | `{cs:.2f}` | `{cm_tot:,}` |")

    lines.extend([
        "",
        "---",
        "",
        "## 4. Persona Balance, Conviction Boosters & Engineering Candor",
        "",
        "### 4.1 Voice Persona Pronouns (per 1,000 Words)",
        "",
        "| Persona Stance | Blog (`1A`) `/1k` | R&D (`1B`) `/1k` | Suppliers/Orgs `/1k` | Role in Author Voice |",
        "| :--- | :---: | :---: | :---: | :--- |",
        f"| **1st-Person Builder (`I / my / me`)** | `{blog_only['pronoun_counts']['first_singular'] * 1000.0 / tw_b:.1f}` | `{rnd_only['pronoun_counts']['first_singular'] * 1000.0 / tw_r:.1f}` | `{suppliers_orgs['pronoun_counts']['first_singular'] * 1000.0 / tw_s:.1f}` | Hands-on bench testing, CAD decisions & personal experience |",
        f"| **1st-Person Org (`we / our / us`)** | `{blog_only['pronoun_counts']['first_plural'] * 1000.0 / tw_b:.1f}` | `{rnd_only['pronoun_counts']['first_plural'] * 1000.0 / tw_r:.1f}` | `{suppliers_orgs['pronoun_counts']['first_plural'] * 1000.0 / tw_s:.1f}` | Primary Author project direction, release roadmap & shared effort |",
        f"| **2nd-Person Maker (`you / your`)** | `{blog_only['pronoun_counts']['second_person'] * 1000.0 / tw_b:.1f}` | `{rnd_only['pronoun_counts']['second_person'] * 1000.0 / tw_r:.1f}` | `{suppliers_orgs['pronoun_counts']['second_person'] * 1000.0 / tw_s:.1f}` | Direct shop-floor coaching, assembly cues & reader walkthroughs |",
        "",
        "### 4.2 Top Conviction Boosters vs. Pragmatic Engineering Hedges",
        "",
    ])
    top_conv = ", ".join(f"`{w}` ({c})" for w, c in all_maker["conviction_counter"].most_common(14))
    top_candor = ", ".join(f"`{w}` ({c})" for w, c in all_maker["candor_counter"].most_common(14))
    top_caps = ", ".join(f"`{w}` ({c})" for w, c in all_maker["all_caps_words"].most_common(15))
    lines.append(f"- **Top Conviction / Emphasis Words**: {top_conv}")
    lines.append(f"- **Top Pragmatic Candor / Qualifier Words**: {top_candor}")
    lines.append(f"- **Top Single-Word ALL-CAPS Emphasis Tokens**: {top_caps}")

    lines.extend([
        "",
        "---",
        "",
        "## 5. Head-to-Head Contraction Habits & Punctuation Profile",
        "",
        "### 5.1 Uncontracted vs. Contracted Habits (All Maker Corpus)",
        "",
        "| Expression Pair | Uncontracted Count | Contracted Count | Uncontracted Share (`%`) | Stylistic Takeaway |",
        "| :--- | :---: | :---: | :---: | :--- |",
    ])
    for label, _, _ in CONTRACTION_PAIRS:
        u_cnt, c_cnt = all_maker["contraction_pair_counts"][label]
        tot_pair = u_cnt + c_cnt
        pct_u = f"{u_cnt * 100.0 / tot_pair:.1f}%" if tot_pair > 0 else "N/A"
        takeaway = (
            "Prefers full uncontracted form for deliberate emphasis"
            if tot_pair > 0 and (u_cnt / tot_pair) >= 0.65
            else ("Balanced natural mix" if tot_pair > 0 and 0.35 <= (u_cnt / tot_pair) < 0.65 else "Prefers conversational contraction")
        )
        lines.append(f"| **{label}** | `{u_cnt:,}` | `{c_cnt:,}` | `{pct_u}` | {takeaway} |")

    lines.extend([
        "",
        "### 5.2 Punctuation & Emphasis Density (per 1,000 Words)",
        "",
        "| Feature | Blog (`1A`) `/1k` | R&D (`1B`) `/1k` | Suppliers/Orgs `/1k` | All Maker Count |",
        "| :--- | :---: | :---: | :---: | :---: |",
    ])
    for k, label in [
        ("contractions", "Conversational Contractions (`it's`, `don't`, `I've`)"),
        ("ellipses_(...)", "Dramatic / Trailing Ellipses (`...`)"),
        ("parentheticals_(...)", "Parenthetical Asides `(...)`"),
        ("em_or_spaced_dashes", "Em-Dashes / Spaced Pivots (`—` / ` - `)"),
        ("all_caps_emphasis", "ALL-CAPS Emphasis Words (`NEVER`, `GREATLY`, `ONE`)"),
        ("bold_spans", "Markdown Bold Spans (`**...**`)"),
        ("italic_spans", "Markdown Italic Spans (`*...*`)"),
        ("colons", "Explanatory Colons (`:`)"),
        ("semicolons", "Semicolons (`;`)"),
        ("questions", "Rhetorical / Direct Questions (`?`)"),
        ("exclamations", "Exclamation Marks (`!`)"),
        ("double_space_after_period", "Raw Double-Space After Sentence End (`.  `)"),
    ]:
        rb = blog_only["punct_counts"][k] * 1000.0 / tw_b
        rr = rnd_only["punct_counts"][k] * 1000.0 / tw_r
        rs = suppliers_orgs["punct_counts"][k] * 1000.0 / tw_s
        cnt_m = all_maker["punct_counts"][k]
        lines.append(f"| {label} | `{rb:.2f}` | `{rr:.2f}` | `{rs:.2f}` | `{cnt_m:,}` |")

    lines.extend([
        "",
        "---",
        "",
        "## 6. Empirical Anti-AI Lexicon Audit & Authentic Author Idioms",
        "",
        "### 6.1 Generic LLM Cliché Count Across `315k+` Author Maker Words",
        "",
        f"- **`use / uses / using / used` vs. `utilize / utilizing`**: **`{all_maker['use_vs_utilize'][0]:,}`** vs. **`{all_maker['use_vs_utilize'][1]:,}`**",
    ])
    for label, _ in BANNED_AI_TROPES:
        lines.append(f"- **`{label}`**: `{all_maker['ai_trope_counts'][label]}` occurrences")

    lines.extend([
        "",
        "### 6.2 Authentic Recurring Author Phrases & Idioms",
        "",
        "| Signature Phrase / Collocation | Total Maker Occurrences | Rate (`/10k` words) |",
        "| :--- | :---: | :---: |",
    ])
    sorted_sigs = sorted(all_maker["sig_phrase_counts"].items(), key=lambda kv: kv[1], reverse=True)
    for label, cnt in sorted_sigs:
        if cnt > 0:
            lines.append(f"| **{label}** | `{cnt:,}` | `{cnt * 10000.0 / tw_m:.2f}` |")

    lines.extend([
        "",
        "---",
        "",
        "## 7. Stratified Candidate Verbatim Exemplars (Across All 5 Categories)",
        "",
    ])

    cat_titles = [
        ("cat1_hooks", "7.1 Category 1: Project Introductions, Hooks & Design Philosophy (Mode A)"),
        ("cat2_physics_why", "7.2 Category 2: Physical / Mechanical / Thermal 'Why' (Modes A & B)"),
        ("cat3_build_guidance", "7.3 Category 3: Hands-On Build, Calibration & Troubleshooting Guidance (Mode B)"),
        ("cat4_tradeoffs_iterations", "7.4 Category 4: Engineering Trade-Offs, Iteration Logs & What Failed (Mode A)"),
        ("cat5_analogies_humor", "7.5 Category 5: Signature Analogies, Parentheticals & Dry Maker Humor"),
    ]
    for c_key, c_heading in cat_titles:
        lines.append(f"### {c_heading}")
        lines.append("")
        items = exemplars.get(c_key, [])
        if not items:
            lines.append("- *(No qualifying passages found for this category)*")
            lines.append("")
            continue
        for idx, (score, src, passage, wc) in enumerate(items, 1):
            lines.append(f"#### Candidate {idx} — `{src}` (`{wc}` words, score `{score:.1f}`)")
            lines.append("> " + passage.replace("\n", "\n> "))
            lines.append("")

    return "\n".join(lines)


def discover_and_load_inbox(
    inbox_dir: str, author_filter: str = "", stitch_minutes: float = 8.0
) -> Tuple[List[PostRecord], Dict[str, Dict[str, int]], Dict[str, Dict[str, object]]]:
    records: List[PostRecord] = []
    combined_domain_summary: Dict[str, Dict[str, int]] = collections.defaultdict(
        lambda: {"channels": 0, "raw_msgs": 0, "stitched_posts": 0, "raw_words": 0}
    )
    combined_org_breakdown: Dict[str, Dict[str, object]] = collections.defaultdict(
        lambda: {"role": "", "channels": 0, "raw_msgs": 0, "long_posts": 0, "raw_words": 0, "long_words": 0}
    )
    handled_dirs: Set[str] = set()

    for root, dirs, files in os.walk(inbox_dir):
        dirs.sort()
        abs_root = os.path.abspath(root)
        if any(abs_root == hd or abs_root.startswith(hd + os.sep) for hd in handled_dirs):
            dirs[:] = []
            continue

        has_channel_subdirs = any(
            d.startswith("c") and os.path.isfile(os.path.join(root, d, "messages.json"))
            for d in dirs[:25]
        ) or any(
            d.startswith("c") and os.path.isfile(os.path.join(root, d, "messages.csv"))
            for d in dirs[:25]
        )
        if has_channel_subdirs:
            pkg_records, pkg_summary, pkg_orgs = load_discord_gdpr_package(root, stitch_minutes=stitch_minutes)
            records.extend(pkg_records)
            for k, v in pkg_summary.items():
                for metric, cnt in v.items():
                    combined_domain_summary[k][metric] += cnt
            for org_k, org_v in pkg_orgs.items():
                ob = combined_org_breakdown[org_k]
                ob["role"] = org_v["role"]
                for m_k in ("channels", "raw_msgs", "long_posts", "raw_words", "long_words"):
                    ob[m_k] = int(ob[m_k]) + int(org_v[m_k])
            handled_dirs.add(abs_root)
            dirs[:] = []
            continue

        for fname in sorted(files):
            if fname.lower() in ("readme.md", "index.json", "channel.json"):
                continue
            if not fname.lower().endswith((".txt", ".md", ".json", ".csv")):
                continue
            fpath = os.path.join(root, fname)
            file_recs = load_standalone_file(fpath, author_filter=author_filter, stitch_minutes=stitch_minutes)
            records.extend(file_recs)
            for r in file_recs:
                ds = combined_domain_summary[r.tier]
                ds["raw_msgs"] += 1
                ds["stitched_posts"] += 1
                ds["raw_words"] += len(r.text.split())
            if file_recs:
                combined_domain_summary[file_recs[0].tier]["channels"] += 1

    return records, combined_domain_summary, combined_org_breakdown


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Deep stylometric & cadence extractor for Maker Orgs, Supplier Companies & Primary Author Blog/R&D."
    )
    parser.add_argument("--inbox", default=DEFAULT_INBOX, help="Directory containing exported Discord files/folders")
    parser.add_argument(
        "--scope",
        choices=["blog-only", "maker", "maker+tech", "all"],
        default="maker",
        help="Domain scope (default: 'maker' — Primary Author Blog/R&D + Maker Suppliers/Companies + Open-Source Orgs)",
    )
    parser.add_argument("--author", default="", help="Optional Discord author handle filter for multi-user exports")
    parser.add_argument("--min-words", type=int, default=60, help="Minimum prose word count for long-form posts (default: 60)")
    parser.add_argument(
        "--stitch-minutes",
        type=float,
        default=8.0,
        help="Max gap in minutes to stitch multi-part split posts in chronological order (default: 8.0)",
    )
    parser.add_argument("--exemplars-per-cat", type=int, default=6, help="Candidate exemplars per category (default: 6)")
    parser.add_argument("--output", default=DEFAULT_OUTPUT, help="Output Markdown telemetry report path")
    args = parser.parse_args()

    if not os.path.isdir(args.inbox):
        print(f"[ERROR] Inbox folder not found: {args.inbox}")
        return 1

    all_records, domain_summary, org_breakdown = discover_and_load_inbox(
        args.inbox, author_filter=args.author, stitch_minutes=args.stitch_minutes
    )

    if not all_records:
        print(f"[INFO] No Discord export records found in {args.inbox} (ignoring README.md).")
        return 0

    scoped_records = [r for r in all_records if tier_included_in_scope(r.tier, args.scope)]
    blog_records = [r for r in scoped_records if r.tier == "TIER_1A_BLOG"]
    rnd_records = [r for r in scoped_records if r.tier == "TIER_1B_ORG_RND"]
    supplier_org_records = [r for r in scoped_records if r.tier in ("TIER_2A_MAKER_SUPPLIERS", "TIER_2B_MAKER_ORGS")]

    all_maker_stats = compute_deep_stylometrics(scoped_records, min_words=args.min_words)
    blog_stats = compute_deep_stylometrics(blog_records, min_words=args.min_words)
    rnd_stats = compute_deep_stylometrics(rnd_records, min_words=args.min_words)
    supplier_org_stats = compute_deep_stylometrics(supplier_org_records, min_words=args.min_words)

    exemplars = extract_stratified_exemplars(all_maker_stats["long_posts"], per_category=args.exemplars_per_cat)

    report_md = format_deep_report(
        all_maker=all_maker_stats,
        blog_only=blog_stats,
        rnd_only=rnd_stats,
        suppliers_orgs=supplier_org_stats,
        domain_summary=domain_summary,
        org_breakdown=org_breakdown,
        exemplars=exemplars,
        inbox_dir=args.inbox,
        scope=args.scope,
        min_words=args.min_words,
    )

    os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as f:
        f.write(report_md)

    excluded_msgs = sum(
        v["raw_msgs"] for k, v in domain_summary.items() if not tier_included_in_scope(k, args.scope)
    )
    included_msgs = sum(
        v["raw_msgs"] for k, v in domain_summary.items() if tier_included_in_scope(k, args.scope)
    )

    print(
        f"[PASS] Deep Pass Complete | Maker/Supplier/Org raw msgs: {included_msgs:,} | "
        f"Filtered Gaming/DM/Admin raw msgs: {excluded_msgs:,}"
    )
    print(
        f"[PASS] Qualifying >= {args.min_words}w posts: Total Maker={all_maker_stats['qualifying_long_posts']:,} "
        f"({all_maker_stats['total_words']:,}w) | Blog={blog_stats['qualifying_long_posts']:,} ({blog_stats['total_words']:,}w) | "
        f"R&D={rnd_stats['qualifying_long_posts']:,} ({rnd_stats['total_words']:,}w) | "
        f"Suppliers & Orgs={supplier_org_stats['qualifying_long_posts']:,} ({supplier_org_stats['total_words']:,}w)"
    )
    print(f"[PASS] Wrote deep telemetry report to: {args.output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
