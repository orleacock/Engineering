#!/usr/bin/env python3
"""
verify_claims.py — Domain-Agnostic Deterministic Claim & [TBD] Verifier
=======================================================================
Decouples neural text/doc generation from symbolic literal verification across
any engineering specialty (mechanical/CAD, electronics/firmware, structured
cabling/BOMs, software, and GitHub/Discord technical writing).

Checks --target against --sources (zero external dependencies):
  1. Dimensioned quantities, percentages, Shore hardnesses, numeric ranges,
     and spelled-out number+unit phrases ("two-meter", "50 to 70 grams").
  2. Engineering designators (metric/imperial fasteners M3x8mm <-> M3x8,
     cabling/fiber Cat6A/OS2/OM4, adhesives Loctite 243, part keys TPN*/BF*).
  3. Backticked file/asset/code/coordinate literals (`*.stl`, `*.xlsx`,
     `*.cfg`, `D33:I34`, `PF7`, `SET_PNEUMA_MODE`).
  4. Explicit `[TBD: ...]` / `[UNVERIFIED ...]` abstention markers (inventoried
     cleanly as Open Offenders rather than hidden) and `[CALC: ...]` AST math.
  5. Source Provenance & Anti-Circularity checks (blocks `--target` == `--sources`
     and flags dirty Git working-tree edits, unreceipted AI prose, or `[TBD]`s
     inside `--sources` so the agent & user choose to Skip vs. Work in Parallel).
  6. Cryptographic SHA-256 Proof-of-Verification Receipt (`VRF-<12hex>`).

Exit codes:
  0 — PASS (0 unbacked claims; open [TBD] markers allowed unless --fail-on-tbd)
  1 — FAIL (1 or more unbacked claims detected, circular source, or missing file)
  2 — TBD_BLOCK (--fail-on-tbd set and >=1 open [TBD] marker remains)
  3 — PROVENANCE_BLOCK (--strict-provenance set and >=1 suspect --sources file)
"""

import argparse
import ast
import hashlib
import json
import os
import re
import subprocess
import sys
from typing import Dict, List, Optional, Set, Tuple

_SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
_HOM_ROOT = os.path.abspath(os.path.join(_SCRIPT_DIR, "..", "..", ".."))
for _p in (_SCRIPT_DIR, os.path.join(_HOM_ROOT, "scripts")):
    if _p not in sys.path:
        sys.path.insert(0, _p)
import homunculus_paths  # noqa: E402

TEXT_EXTENSIONS = {
    ".md", ".txt", ".cfg", ".conf", ".ini", ".toml", ".yaml", ".yml",
    ".json", ".csv", ".tsv", ".py", ".sh", ".js", ".ts", ".c", ".h",
    ".cpp", ".hpp", ".xml", ".html", ".svg",
}

BULK_EXCLUDE_DIRS = {
    "corpus_inbox",
    "study_briefs",
    "node_modules",
    "venv",
    ".venv",
    "dist",
    "build",
    "archive",
    ".trash",
}

WORD_NUMBERS: Dict[str, float] = {
    "zero": 0.0, "one": 1.0, "two": 2.0, "three": 3.0, "four": 4.0,
    "five": 5.0, "six": 6.0, "seven": 7.0, "eight": 8.0, "nine": 9.0,
    "ten": 10.0, "eleven": 11.0, "twelve": 12.0, "thirteen": 13.0,
    "fourteen": 14.0, "fifteen": 15.0, "sixteen": 16.0, "seventeen": 17.0,
    "eighteen": 18.0, "nineteen": 19.0, "twenty": 20.0, "thirty": 30.0,
    "forty": 40.0, "fifty": 50.0, "sixty": 60.0, "seventy": 70.0,
    "eighty": 80.0, "ninety": 90.0, "hundred": 100.0,
}

UNIT_ALIASES: Dict[str, str] = {
    # Length / Area / Volume / Flow
    "nm_len": "nm_len", "um": "um", "µm": "um", "micrometer": "um", "micrometers": "um", "micron": "um", "microns": "um",
    "mm": "mm", "millimeter": "mm", "millimeters": "mm", "millimetre": "mm", "millimetres": "mm",
    "cm": "cm", "centimeter": "cm", "centimeters": "cm",
    "m": "m", "meter": "m", "meters": "m", "metre": "m", "metres": "m",
    "km": "km", "kilometer": "km", "kilometers": "km",
    "mil": "mil", "mils": "mil",
    "in": "in", "inch": "in", "inches": "in",
    "ft": "ft", "foot": "ft", "feet": "ft",
    "yd": "yd", "yard": "yd", "yards": "yd",
    "cm3": "cm3", "cm³": "cm3", "mm3": "mm3", "mm³": "mm3",
    "l": "l", "liter": "l", "liters": "l", "ml": "ml", "milliliter": "ml", "milliliters": "ml",
    "l/min": "l/min", "lpm": "l/min", "cfm": "cfm", "scfm": "scfm",
    # Mass / Force / Torque / Pressure
    "mg": "mg", "milligram": "mg", "milligrams": "mg",
    "g": "g", "gram": "g", "grams": "g",
    "kg": "kg", "kilogram": "kg", "kilograms": "kg",
    "oz": "oz", "ounce": "oz", "ounces": "oz",
    "lb": "lb", "lbs": "lb", "pound": "lb", "pounds": "lb",
    "n": "n", "kn": "kn",
    "nm": "nm", "n·m": "nm", "n-m": "nm",
    "in-lb": "in-lb", "in-lbs": "in-lb", "ft-lb": "ft-lb", "ft-lbs": "ft-lb",
    "pa": "pa", "kpa": "kpa", "mpa": "mpa", "gpa": "gpa",
    "bar": "bar", "mbar": "mbar", "psi": "psi",
    # Thermal / Angle
    "°c": "degc", "degc": "degc", "celsius": "degc",
    "°f": "degf", "degf": "degf", "fahrenheit": "degf",
    "°": "deg", "deg": "deg", "degree": "deg", "degrees": "deg",
    # Electrical / Electronic / RF
    "v": "v", "volt": "v", "volts": "v", "vdc": "v", "vac": "v",
    "mv": "mv", "millivolt": "mv", "millivolts": "mv", "kv": "kv",
    "a": "a", "amp": "a", "amps": "a", "ampere": "a", "amperes": "a",
    "ma": "ma", "milliamp": "ma", "milliamps": "ma", "ua": "ua", "µa": "ua",
    "w": "w", "watt": "w", "watts": "w", "mw": "mw", "kw": "kw", "va": "va",
    "wh": "wh", "mah": "mah", "ah": "ah",
    "Ω": "ohm", "ω": "ohm", "ohm": "ohm", "ohms": "ohm",
    "mΩ": "mohm", "mohm": "mohm", "kΩ": "kohm", "kohm": "kohm", "kohms": "kohm", "MΩ": "megohm", "megohm": "megohm",
    "pf": "pf", "nf": "nf", "uf": "uf", "µf": "uf",
    "uh": "uh", "µh": "uh", "mh": "mh",
    "hz": "hz", "khz": "khz", "mhz": "mhz", "ghz": "ghz",
    "db": "db", "dbm": "dbm", "dbi": "dbi",
    "awg": "awg",
    # Percentage / Time / Speed / Data / Procurement UOM
    "%": "%", "percent": "%",
    "s": "s", "sec": "s", "secs": "s", "second": "s", "seconds": "s",
    "ms": "ms", "millisecond": "ms", "milliseconds": "ms",
    "us": "us", "µs": "us", "ns": "ns",
    "min": "min", "mins": "min", "minute": "min", "minutes": "min",
    "hr": "hr", "hrs": "hr", "hour": "hr", "hours": "hr",
    "d": "d", "day": "d", "days": "d",
    "mm/s": "mm/s",
    "rpm": "rpm",
    "bps": "bps", "kbps": "kbps", "mbps": "mbps", "gbps": "gbps",
    "kb": "kb", "mb": "mb", "gb": "gb",
    "ea": "ea", "kt": "kt", "bx": "bx", "rl": "rl", "pk": "pk",
    "word": "words", "words": "words", "prose word": "words", "prose words": "words",
}

UNIT_DIMENSIONS: Dict[str, str] = {
    # Length
    "mm": "length", "cm": "length", "m": "length", "km": "length",
    "in": "length", "ft": "length", "yd": "length", "mil": "length",
    "um": "length", "nm_len": "length",
    # Volume
    "cm3": "volume", "mm3": "volume", "l": "volume", "ml": "volume",
    # Flow
    "l/min": "flow", "cfm": "flow", "scfm": "flow",
    # Mass
    "mg": "mass", "g": "mass", "kg": "mass", "oz": "mass", "lb": "mass",
    # Force
    "n": "force", "kn": "force",
    # Torque
    "nm": "torque", "in-lb": "torque", "ft-lb": "torque",
    # Pressure
    "pa": "pressure", "kpa": "pressure", "mpa": "pressure", "gpa": "pressure",
    "bar": "pressure", "mbar": "pressure", "psi": "pressure",
    # Thermal / Angle
    "degc": "temperature", "degf": "temperature", "deg": "angle",
    # Electrical
    "v": "voltage", "mv": "voltage", "kv": "voltage",
    "a": "current", "ma": "current", "ua": "current",
    "w": "power", "mw": "power", "kw": "power", "va": "power",
    "wh": "energy", "mah": "energy", "ah": "energy",
    "ohm": "resistance", "mohm": "resistance", "kohm": "resistance", "megohm": "resistance",
    "pf": "capacitance", "nf": "capacitance", "uf": "capacitance",
    "uh": "inductance", "mh": "inductance",
    "hz": "frequency", "khz": "frequency", "mhz": "frequency", "ghz": "frequency",
    "awg": "gauge",
    # Time / Speed / Ratio
    "s": "time", "ms": "time", "us": "time", "ns": "time",
    "min": "time", "hr": "time", "d": "time",
    "mm/s": "speed", "rpm": "speed",
    "bps": "data_rate", "kbps": "data_rate", "mbps": "data_rate", "gbps": "data_rate",
    "kb": "data", "mb": "data", "gb": "data",
    "%": "ratio", "words": "count", "ea": "count", "kt": "count", "bx": "count", "rl": "count", "pk": "count",
}

# Units ordered longest-first for regex alternation
SORTED_UNIT_PATTERNS = sorted(UNIT_ALIASES.keys(), key=len, reverse=True)
UNIT_REGEX_STR = "|".join(re.escape(u) for u in SORTED_UNIT_PATTERNS)

# Note: single-letter units like 'a', 'm', 'v', 'w', 'g', 'l', 'n' require careful boundary rules:
# If separated by whitespace (e.g. "2 a"), 'a' or 'in' could be an English word ("2 in the Rear Cover", "1 a day")!
# Therefore:
# - Attached without space ("20AWG", "2m", "60g", "12V", "100%", "0.20mm", "250°C") -> allow all units.
# - Separated by space ("70 kPa", "5,040 FT", "60 grams", "1.2 Nm", "10 L/min") -> disallow ambiguous English words ("a", "in") unless uppercase ("5 A") or full unit word ("inches", "amps")!
AMBIGUOUS_LOWER_SPACED_UNITS = {"a", "in", "l", "n", "v", "w", "d"}
CASE_SENSITIVE_SPACED_OK = {"A", "V", "W", "N", "L", "S", "D"}

NUM_PAT = r"(?<!\w)[+-]?\d{1,3}(?:,\d{3})*(?:\.\d+)?|[+-]?\d+(?:\.\d+)?"

RANGE_NUM_UNIT_RE = re.compile(
    rf"(?<![A-Za-z0-9_.])([+-]?\d+(?:,\d{{3}})*(?:\.\d+)?)\s*(?:({UNIT_REGEX_STR})\s*)?(?:to|-|–|—)\s*([+-]?\d+(?:,\d{{3}})*(?:\.\d+)?)\s*({UNIT_REGEX_STR})(?![A-Za-z0-9_])",
    re.IGNORECASE,
)

SINGLE_NUM_UNIT_RE = re.compile(
    rf"(?<![A-Za-z0-9_.])([+-]?\d+(?:,\d{{3}})*(?:\.\d+)?)(\s*)({UNIT_REGEX_STR})(?![A-Za-z0-9_/])",
    re.IGNORECASE,
)

WORD_NUM_RE_STR = "|".join(sorted(WORD_NUMBERS.keys(), key=len, reverse=True))
SPELLED_NUM_UNIT_RE = re.compile(
    rf"\b({WORD_NUM_RE_STR})(?:[\s-]+)({UNIT_REGEX_STR})(?![A-Za-z0-9_])",
    re.IGNORECASE,
)

# Shore durometer e.g. 95A, 85A, 98A, 60D (2 digits + A/D, excluding 20A/10A current unless Shore context, wait: 95A/85A/98A/70A/60D)
SHORE_RE = re.compile(r"\b(?:Shore\s*)?(75|80|85|90|95|98)[AD]\b|\bShore\s*\d{2}[AD]\b", re.IGNORECASE)

# Metric fasteners: M3x5x4mm, M3 x 65mm, M3x8mm, M5x12, M5x7x0.3mm
METRIC_FASTENER_RE = re.compile(
    r"\b(M\d+(?:\.\d+)?(?:\s*[x×]\s*\d+(?:\.\d+)?)+(?:\s*mm)?)\b", re.IGNORECASE
)

# Standard technical designators (cabling, jackets, polymers/alloys, IC packages, adhesives, connectors, MCU pins, part prefixes, 4-digit COTS fan/extrusion sizes)
DESIGNATOR_RE = re.compile(
    r"\b(Cat(?:5e|6A?|7|8)|OS[12]|OM[1-5]|CMP|CMR|LSZH|OFNP|OFNR|RJ45|SFP\+|QSFP28|"
    r"PTFE|FEP|PEEK|PEI|Ultem|6061(?:-T6)?|7075(?:-T6)?|"
    r"TO-\d+[A-Z]*|SOT-\d+[A-Z0-9-]*|SOIC-\d+|QFN-\d+|DFN-\d+|D2?PAK|PowerPAK|"
    r"Loctite\s+\d+[A-Z]*|TPN\d+|BF\d+|(?:MB\s+)?P/N\s+[A-Za-z0-9-]+|"
    r"GPIO\d+|P[A-K]\d{1,2}|PC4-M\d+|NEMA\s*\d+|1/8[- ]NPT|"
    r"(?:2510|3010|4010|4020|5015|5020|12032|1515|2020|2040|3030|4040)(?=\s*(?:mm\s+)?(?:fan|blower|axial|extrusion|profile|frame)s?\b))\b",
    re.IGNORECASE,
)

# Indefinite/unmeasured metric fastener callout inside a numbered assembly step (e.g. "using M3 screws" dodging missing length)
UNDERSPECIFIED_STEP_FASTENER_RE = re.compile(
    r"\b(?:using|with|install|insert|seat|thread|fasten|secure\s+with)\s+(?:\(\d+\)\s+|\d+x?\s+)?(M\d+\s+(?:screws?|bolts?|shcs|bhcs|fhcs))\b",
    re.IGNORECASE,
)

# Domain-agnostic qualifier nouns that bind a number+unit to a specific physical meaning on the same source line/row
QUALIFIER_GROUPS: List[Tuple[str, Tuple[str, ...]]] = [
    ("id", ("id", "internal diameter", "inner diameter", "inside diameter", "bore")),
    ("od", ("od", "outer diameter", "outside diameter", "external diameter")),
    ("infill", ("infill",)),
    ("pullup", ("pull-up", "pullup")),
    ("pulldown", ("pull-down", "pulldown")),
    ("gate", ("gate resistor", "vgs")),
    ("magnet", ("magnet", "magnets")),
    ("bearing", ("bearing", "bearings")),
    ("heatset", ("heat-set", "heat-sets", "heatset", "heatsets")),
    ("bowden", ("bowden",)),
    ("rod", ("rod", "rods", "shaft", "shafts")),
    ("nozzle", ("nozzle", "nozzles", "orifice", "orifices")),
    ("belt", ("belt", "belts")),
    ("pulley", ("pulley", "pulleys", "idler", "idlers")),
    ("standoff", ("standoff", "standoffs", "spacer", "spacers")),
    ("spring", ("spring", "springs")),
    ("dowel", ("dowel", "dowels")),
    ("bushing", ("bushing", "bushings")),
    ("oring", ("o-ring", "o-rings", "oring", "orings", "gasket", "gaskets")),
    ("thermistor", ("thermistor", "thermistors")),
    ("heater", ("heater", "heaters", "cartridge", "cartridges")),
    ("fan", ("fan", "fans", "blower", "blowers")),
    ("fuse", ("fuse", "fuses", "breaker", "breakers")),
    ("resistor", ("resistor", "resistors")),
    ("capacitor", ("capacitor", "capacitors")),
    ("inductor", ("inductor", "inductors", "choke", "chokes")),
    ("conduit", ("conduit", "conduits", "raceway", "raceways")),
]
COMPILED_QUALIFIER_GROUPS: List[Tuple[str, re.Pattern]] = [
    (grp, re.compile(rf"\b(?:{'|'.join(re.escape(s) for s in syns)})\b"))
    for grp, syns in QUALIFIER_GROUPS
]

_ALL_QUALIFIER_SYNONYMS_PATTERN = "|".join(
    re.escape(syn).replace(r"\ ", r"\s+")
    for _, syns in QUALIFIER_GROUPS
    for syn in sorted(syns, key=len, reverse=True)
)

QUALIFIED_NUM_UNIT_RE = re.compile(
    rf"(?<![A-Za-z0-9_.])([+-]?\d+(?:,\d{{3}})*(?:\.\d+)?)(\s*)({UNIT_REGEX_STR})\s+"
    rf"({_ALL_QUALIFIER_SYNONYMS_PATTERN})\b",
    re.IGNORECASE,
)

DIGIT_RE = re.compile(r"\d")
QUALIFIER_QUICK_RE = re.compile(
    rf"\b(?:diameter|gate|{_ALL_QUALIFIER_SYNONYMS_PATTERN})\b",
    re.IGNORECASE,
)
DATE_SHA_MASK_RE = re.compile(
    r"\b\d{4}[-/]\d{2}[-/]\d{2}\b|\b[0-9a-f]{7,40}\b|\b(?:date|verified|last_verified):\s*\d{4}\b",
    re.IGNORECASE,
)
SPELLED_QUICK_RE = re.compile(
    r"\b(?:one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen|twenty|thirty|forty|fifty|sixty|seventy|eighty|ninety|hundred)\b"
)

REVERSE_QUALIFIED_RE = re.compile(
    rf"\b({_ALL_QUALIFIER_SYNONYMS_PATTERN})\b[^.\n;|,]{{0,35}}?"
    rf"(?<![A-Za-z0-9_.])([+-]?\d+(?:,\d{{3}})*(?:\.\d+)?)(\s*)({UNIT_REGEX_STR})(?![A-Za-z0-9_/])",
    re.IGNORECASE,
)

# Backticked identifiers (1..120 chars so 1-char tokens like `0` or `;` never misalign backtick pairing)
BACKTICK_RE = re.compile(r"`([^`\n]{1,120})`")

# Explicit [TBD...] / [UNVERIFIED...] / [CATALOG ADDITION REQUIRED...] markers
TBD_MARKER_RE = re.compile(
    r"\[(?:TBD|TODO|UNVERIFIED|CATALOG ADDITION REQUIRED)[^\]]*\]",
    re.IGNORECASE,
)
BACKTICKED_OR_RAW_TBD_RE = re.compile(
    r"`\[(?:TBD|TODO|UNVERIFIED|CATALOG ADDITION REQUIRED)[^\]]*\]`|\[(?:TBD|TODO|UNVERIFIED|CATALOG ADDITION REQUIRED)[^\]]*\]",
    re.IGNORECASE,
)
INERT_META_TBD_RE = re.compile(
    r"^\[(?:TBD|TODO|UNVERIFIED|CATALOG ADDITION REQUIRED)"
    r"(?::\s*(?:CONFLICT(?:\s*[—-]\s*(?:\.\.\.|…|<[^>]+>(?:\s+vs\s+<[^>]+>)?|(?:\b(?:source_A|source_B|val|variable|var)\b|<[^>]+>)(?:\s+vs\s+(?:\b(?:source_A|source_B|val|variable|var)\b|<[^>]+>))?))?"
    r"|(?:\.\.\.|…|<[^>]+>|\bvar\b)))?\]$",
    re.IGNORECASE,
)

# Explicit deterministic arithmetic marker: [CALC: 120W / 24V = 5.0A]
CALC_MARKER_RE = re.compile(r"\[CALC:\s*([^\]]+?)\s*\]", re.IGNORECASE)

# Unbackticked inventory/architecture/hardware count phrases & hyphenated count modifiers
COUNT_PREFIX_EXCLUDE_RE = re.compile(
    r"\b(?:layer|step|phase|stage|tier|mode|option|outcome|part|section|sec|row|col|column|"
    r"sheet|workbook|run|gate|rule|pillar|pass|check|block|fault|cmd|item|line|rev|version)\s+#?\s*$",
    re.IGNORECASE,
)
COUNT_MODIFIER_STOPWORDS = {
    "in", "on", "of", "to", "for", "with", "from", "by", "at", "as", "and", "or", "vs", "via",
    "is", "are", "was", "were", "be", "has", "have", "had", "loads", "checks", "runs",
    "verifies", "uses", "stores", "returns", "emits", "tracks", "blocks", "passes", "fails",
}
HYPHENATED_COUNT_RE = re.compile(
    r"(?<![A-Za-z0-9_.#])(\d{1,3}(?:,\d{3})+|\d+)-\s*"
    r"(post|gate|block|layer|tier|token|char|line|step|file|sheet|col|column|row|pin|bore|part|state|domain|stage|phase|channel|way|point)s?\b",
    re.IGNORECASE,
)
COUNTED_NOUN_RE = re.compile(
    r"(?<![A-Za-z0-9_.#])(\d{1,3}(?:,\d{3})+|\d+)[x×]?\s+"
    r"((?:[A-Za-z][A-Za-z0-9/-]*\s+){0,3})"
    r"(skills?|rules?|oracles?|scripts?|subagents?|workers?|blueprints?|palettes?|archetypes?|umbrellas?|"
    r"dossiers?|manifests?|gates?|layers?|workbooks?|worksheets?|sheets?|columns?|rows?|categories|"
    r"workflows?|standards?|files?|repos?|repositories|parts?|fasteners?|screws?|bolts?|nuts?|"
    r"inserts?|heat-sets?|bearings?|magnets?|pins?|ports?|channels?|pumps?|fans?|blowers?|motors?|"
    r"extruders?|nozzles?|belts?|pulleys?|idlers?|cables?|strands?|fibers?|runs?|jacks?|panels?|"
    r"racks?|drops?|posts?|messages?|commits?|checks?|errors?|warnings?|faults?|targets?|step|stl|"
    r"washers?|spacers?|standoffs?|springs?|o-rings?|ferrules?|shims?|terminals?)\b",
    re.IGNORECASE,
)
ALL_COUNTED_NOUN_STEM_RE = re.compile(
    r"\b(post|gate|block|layer|tier|token|char|line|step|file|sheet|col|column|row|pin|bore|"
    r"part|state|domain|stage|phase|channel|way|point|skill|rule|oracle|script|subagent|worker|"
    r"blueprint|palette|archetype|umbrella|dossier|manifest|workbook|worksheet|categories|"
    r"category|workflow|standard|repo|repositories|repository|fastener|screw|bolt|nut|insert|"
    r"heat-set|bearing|magnet|port|pump|fan|blower|motor|extruder|nozzle|belt|pulley|idler|"
    r"cable|strand|fiber|run|jack|panel|rack|drop|message|commit|check|error|warning|fault|target|stl|"
    r"washer|spacer|standoff|spring|o-ring|ferrule|shim|terminal)s?\b",
    re.IGNORECASE,
)


def normalize_counted_noun(raw_noun: str) -> str:
    n = raw_noun.lower().strip()
    if n in ("oracle", "oracles", "script", "scripts"):
        return "script_oracle"
    if n in ("repo", "repos", "repository", "repositories"):
        return "repo"
    if n in ("category", "categories"):
        return "category"
    if n in ("col", "cols", "column", "columns"):
        return "column"
    if n in ("sheet", "sheets", "worksheet", "worksheets"):
        return "sheet"
    if n in ("o-ring", "o-rings", "oring", "orings"):
        return "o-ring"
    if n not in ("step", "stl", "pass") and n.endswith("s"):
        return n[:-1]
    return n


def canonicalize_unit(raw_u: str, sep: str) -> Optional[str]:
    """Map raw unit token to canonical unit, filtering English stop-word collisions."""
    u_low = re.sub(r"\s+", " ", raw_u.lower().strip())
    if u_low not in UNIT_ALIASES:
        # Handle special case Ω / MΩ / mΩ
        if raw_u in UNIT_ALIASES:
            return UNIT_ALIASES[raw_u]
        return None
    # Distinguish lowercase 'w' (words in stylometrics, e.g. '19.0w' / '19.0 w') vs. uppercase 'W' (Watts)
    if raw_u == "w":
        return "words"
    if sep:
        # Spaced number + unit: block "2 in", "1 a", "3 m" lowercase prose collisions
        if u_low in AMBIGUOUS_LOWER_SPACED_UNITS and raw_u not in CASE_SENSITIVE_SPACED_OK:
            return None
    # Distinguish MΩ vs mΩ
    if raw_u == "MΩ":
        return "megohm"
    if raw_u == "mΩ":
        return "mohm"
    # Distinguish "Nm" / "N·m" (torque) vs "nm" (nanometers)
    if raw_u == "nm":
        return "nm_len"
    return UNIT_ALIASES[u_low]


def parse_num(raw_n: str) -> float:
    return float(raw_n.replace(",", ""))


def strip_non_claim_regions(text: str) -> List[Tuple[int, str, List[str]]]:
    """
    Returns list of (line_no, cleaned_line, tbd_hits_on_line).
    Strips YAML frontmatter, Mermaid styling directives, HTML <img> layout tags,
    and external URLs while preserving 1-based line numbers.
    """
    lines = text.replace("\r\n", "\n").split("\n")
    is_standard_doc = bool(
        re.search(
            r"^type:\s*(?:standard|command-reference|architecture-diagram)\b",
            text[:500],
            re.IGNORECASE | re.MULTILINE,
        )
    )
    in_frontmatter = False
    in_mermaid = False
    results: List[Tuple[int, str, List[str]]] = []

    for idx, raw_ln in enumerate(lines):
        line_no = idx + 1
        s = raw_ln.strip()

        if idx == 0 and s == "---":
            in_frontmatter = True
            results.append((line_no, "", []))
            continue
        if in_frontmatter:
            if s == "---":
                in_frontmatter = False
            results.append((line_no, "", []))
            continue

        if s.startswith("```mermaid"):
            in_mermaid = True
            results.append((line_no, "", []))
            continue
        if in_mermaid:
            if s.startswith("```"):
                in_mermaid = False
                results.append((line_no, "", []))
                continue
            if s.startswith("%%{init:") or s.startswith("classDef ") or s.startswith("class ") or s.startswith("style ") or s.startswith("linkStyle "):
                results.append((line_no, "", []))
                continue

        # Extract [TBD...] markers first before masking them (and consume optional surrounding backticks
        # so `` `[TBD: ...]` `` never leaves orphaned `` ` ` `` backticks that misalign the rest of the line).
        tbds = [
            m.group(0)
            for m in TBD_MARKER_RE.finditer(raw_ln)
            if not (is_standard_doc and INERT_META_TBD_RE.match(m.group(0).strip()))
        ]
        cleaned = BACKTICKED_OR_RAW_TBD_RE.sub(" ", raw_ln)

        # Mask URLs so shield badges / query params (?ref=partner_id) aren't parsed as units (preserve closing backticks)
        cleaned = re.sub(r"https?://[^\s)>\"'`]+", " ", cleaned)
        # Mask HTML <img ...> tags (e.g., width="45%" layout attributes)
        cleaned = re.sub(r"<img\b[^>]*>", " ", cleaned, flags=re.IGNORECASE)
        # Mask Markdown image paths ![alt](path) while keeping alt text out of backtick checks
        cleaned = re.sub(r"!\[[^\]]*\]\([^)]+\)", " ", cleaned)

        results.append((line_no, cleaned, tbds))

    return results


def normalize_fastener(raw_f: str) -> str:
    s = re.sub(r"\s+", "", raw_f.lower().replace("×", "x"))
    if s.endswith("mm"):
        s = s[:-2]
    return s


def normalize_designator(raw_d: str) -> str:
    return re.sub(r"[\s-]+", "-", raw_d.lower().strip())


AI_PROVENANCE_RE = re.compile(
    r"\b(?:ai[- ](?:assisted|authored|generated)|ai\s+(?:editorial\s+|drafting\s+|research\s+|writing\s+)?assist(?:ance|ed)|(?:generated|prepared|written|drafted)\s+(?:by|with)\s+ai|ai\s+(?:transparency|disclosure)|llm[- ]generated)\b",
    re.IGNORECASE,
)
PLACEHOLDER_STUB_RE = re.compile(
    r"\b(?:currently a placeholder|placeholder (?:for|document|file|page)|coming soon|under construction)\b",
    re.IGNORECASE,
)
EXEMPT_PROVENANCE_FRONTMATTER_RE = re.compile(
    r"^(?:type:\s*(?:standard|hardware-manifest|moc-hub|engineering-log|task-landing-pad|task-umbrella|command-reference|architecture-diagram)|project:\s+\S+)\b",
    re.IGNORECASE | re.MULTILINE,
)
QUARANTINE_HEADING_RE = re.compile(
    r"^(#{1,6})\s+.*(?:Open\s+\[TBD\]|\[CONFLICT\]\s+Ledger|Unverified(?:\s+Claims)?|Quarantined(?:\s+Claims)?|Discrepanc(?:y|ies)|Assumptions?|Known\s+Issues?|Blockers?|Deprecated|Archived|Quarantine|Obsolete|Superseded|Legacy)",
    re.IGNORECASE,
)
HEADING_LEVEL_RE = re.compile(r"^(#{1,6})\s+")
VRF_RECEIPT_RE = re.compile(r"\bVRF-[0-9a-f]{12}\b", re.IGNORECASE)
WARNING_CONTEXT_RE = re.compile(
    r"(?:>\s*\[!(?:WARNING|CAUTION|DANGER)\]|\b(?:NEVER|DO\s+NOT|PROHIBITED|DEPRECATED|OBSOLETE|HAZARD)\b)",
    re.IGNORECASE,
)
WARNING_ACK_RE = re.compile(
    r"\b(?:warning|caution|danger|hazard|never|avoid|do\s+not|don't|prohibit|deprecated|obsolete|kink|choke|damage|fail|crack|attack|craze|delaminat)\b",
    re.IGNORECASE,
)
AUTO_TREE_ZONE_RE = re.compile(
    r"(<!--\s*BEGIN AUTO-TREE\s*-->)(.*?)(<!--\s*END AUTO-TREE\s*-->)",
    re.DOTALL,
)
AUTO_TREE_ROLLUP_COUNT_RE = re.compile(
    r"\(\+?\d+\s*(?:[A-Za-z0-9_.]+|more)[^)]*\)"
)


_SCRIPT_ENG_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../.."))


def normalize_source_relpath(fp: str) -> str:
    abs_fp = os.path.abspath(fp)
    for base in (
        _SCRIPT_ENG_ROOT,
        os.path.dirname(_SCRIPT_ENG_ROOT),
        os.getcwd(),
        os.path.expanduser("~"),
    ):
        if base and abs_fp == base:
            return os.path.basename(abs_fp)
        if base and abs_fp.startswith(base + os.sep):
            return os.path.relpath(abs_fp, base)
    return os.path.basename(abs_fp)


QUARANTINE_HTML_BLOCK_RE = re.compile(
    r"<!--\s*QUARANTINE-ZONE:START\s*-->.*?<!--\s*QUARANTINE-ZONE:END\s*-->",
    re.DOTALL | re.IGNORECASE,
)
SESSION_HANDOFF_BLOCK_RE = re.compile(
    r"<!--\s*SESSION-HANDOFF:START\s*-->.*?<!--\s*SESSION-HANDOFF:END\s*-->",
    re.DOTALL | re.IGNORECASE,
)
FIRST_PRINCIPLES_THEORY_BLOCK_RE = re.compile(
    r"<!--\s*FIRST-PRINCIPLES-THEORY:START\s*-->.*?<!--\s*FIRST-PRINCIPLES-THEORY:END\s*-->",
    re.DOTALL | re.IGNORECASE,
)


def _blank_preserving_newlines(match: re.Match) -> str:
    return "".join("\n" if ch == "\n" else " " for ch in match.group(0))


def quarantine_unverified_source_zones(text: str) -> str:
    text = QUARANTINE_HTML_BLOCK_RE.sub(_blank_preserving_newlines, text)
    text = SESSION_HANDOFF_BLOCK_RE.sub(_blank_preserving_newlines, text)
    text = FIRST_PRINCIPLES_THEORY_BLOCK_RE.sub(_blank_preserving_newlines, text)
    """
    Strip inline `[TBD: ...]` / `[UNVERIFIED ...]` spans, strip synthetic asset-count
    rollup badges inside `<!-- BEGIN AUTO-TREE -->` blocks (while preserving real file
    and folder names), and quarantine Markdown sections explicitly dedicated to
    Open [TBD] / [CONFLICT] / Unverified ledgers so unverified figures or directory
    file counts never whitelist engineering spec numbers during `--sources` indexing.
    """
    norm_text = text.replace("\r\n", "\n")
    norm_text = AUTO_TREE_ZONE_RE.sub(
        lambda m: m.group(1) + AUTO_TREE_ROLLUP_COUNT_RE.sub(" ", m.group(2)) + m.group(3),
        norm_text,
    )
    kept_lines: List[str] = []
    quarantine_level: Optional[int] = None
    for raw_ln in norm_text.split("\n"):
        hm = HEADING_LEVEL_RE.match(raw_ln.strip())
        if hm:
            lvl = len(hm.group(1))
            if quarantine_level is not None and lvl <= quarantine_level:
                quarantine_level = None
            if QUARANTINE_HEADING_RE.match(raw_ln.strip()):
                quarantine_level = lvl
                continue
        if quarantine_level is not None:
            continue
        kept_lines.append(BACKTICKED_OR_RAW_TBD_RE.sub(" ", raw_ln))
    return "\n".join(kept_lines)


class GitWorktreeCache:
    """Caches git rev-parse and git status --porcelain once per repository root."""
    def __init__(self) -> None:
        self.dir_to_repo: Dict[str, Optional[str]] = {}
        self.repo_statuses: Dict[str, Dict[str, str]] = {}
        self.repo_errors: Dict[str, str] = {}

    def _find_repo_root(self, pdir: str) -> Optional[str]:
        cur = os.path.realpath(pdir)
        traversed: List[str] = []
        repo_root: Optional[str] = None
        while cur and cur != os.path.dirname(cur):
            if cur in self.dir_to_repo:
                repo_root = self.dir_to_repo[cur]
                break
            if os.path.exists(os.path.join(cur, ".git")):
                repo_root = cur
                break
            traversed.append(cur)
            cur = os.path.dirname(cur)

        if repo_root is None and cur not in self.dir_to_repo:
            try:
                proc = subprocess.run(
                    ["git", "-C", pdir, "rev-parse", "--show-toplevel"],
                    capture_output=True,
                    text=True,
                    check=False,
                    timeout=2.0,
                )
                if proc.returncode == 0 and proc.stdout.strip():
                    repo_root = os.path.realpath(proc.stdout.strip())
            except Exception:
                repo_root = None

        self.dir_to_repo[pdir] = repo_root
        for d in traversed:
            self.dir_to_repo[d] = repo_root
        return repo_root

    def get_status_code(self, abs_fp: str) -> Optional[str]:
        real_fp = os.path.realpath(abs_fp)
        pdir = os.path.dirname(real_fp) or "."
        repo_root = self._find_repo_root(pdir)
        if not repo_root:
            return None

        if repo_root not in self.repo_statuses:
            status_map: Dict[str, str] = {}
            try:
                proc = subprocess.run(
                    ["git", "--no-optional-locks", "-C", repo_root, "status", "--porcelain", "-uall"],
                    capture_output=True,
                    text=True,
                    check=False,
                    timeout=5.0,
                )
                if proc.returncode == 0:
                    for line in proc.stdout.splitlines():
                        if len(line) >= 4:
                            code = line[:2].strip()
                            rel = line[3:].strip()
                            if rel.startswith('"') and rel.endswith('"'):
                                rel = rel[1:-1]
                            if " -> " in rel:
                                rel = rel.split(" -> ")[1].strip()
                                if rel.startswith('"') and rel.endswith('"'):
                                    rel = rel[1:-1]
                            full_path = os.path.realpath(os.path.join(repo_root, rel))
                            status_map[full_path] = code
                else:
                    self.repo_errors[repo_root] = "GIT_STATUS_ERROR"
            except Exception:
                self.repo_errors[repo_root] = "GIT_STATUS_ERROR"
            self.repo_statuses[repo_root] = status_map

        if repo_root in self.repo_errors:
            return self.repo_errors[repo_root]
        return self.repo_statuses[repo_root].get(real_fp)


def inspect_source_provenance(fp: str, text: str, git_cache: Optional[GitWorktreeCache] = None) -> List[str]:
    """
    Detect suspect or mixed-provenance signals on a candidate `--sources` file:
      - DIRTY_GIT_WORKTREE: uncommitted or untracked changes inside a Git repo
      - AI_AUTHORED_UNRECEIPTED: AI-authored/assisted marker without a valid, verifiable VRF receipt
      - CONTAINS_OPEN_TBD: source file itself contains unresolved [TBD]/[UNVERIFIED]
      - PLACEHOLDER_STUB_SOURCE: source explicitly marks itself as a placeholder stub
    Governing standards (`type: standard`) and deterministic manifests (`type: hardware-manifest`)
    are exempt from AI/TBD prose triggers.
    """
    reasons: List[str] = []
    abs_fp = os.path.abspath(fp)
    parent_dir = os.path.dirname(abs_fp) or "."

    code = git_cache.get_status_code(abs_fp) if git_cache else None
    if code is None and git_cache is None:
        try:
            proc = subprocess.run(
                ["git", "-C", parent_dir, "status", "--porcelain", "--", abs_fp],
                capture_output=True,
                text=True,
                timeout=2.0,
                check=False,
            )
            if proc.returncode == 0 and proc.stdout.strip():
                code = proc.stdout.strip().split()[0]
            elif proc.returncode != 0 and os.path.exists(os.path.join(parent_dir, ".git")):
                code = "GIT_STATUS_ERROR"
        except Exception:
            code = "GIT_STATUS_ERROR"
    if code:
        reasons.append(f"DIRTY_GIT_WORKTREE({code})")

    is_exempt_spec = bool(EXEMPT_PROVENANCE_FRONTMATTER_RE.search(text[:500])) or (
        os.path.basename(abs_fp) == "SKILL.md"
    )
    if not is_exempt_spec:
        if PLACEHOLDER_STUB_RE.search(text):
            reasons.append("PLACEHOLDER_STUB_SOURCE")
        if AI_PROVENANCE_RE.search(text):
            vrf_m = VRF_RECEIPT_RE.search(text)
            if not vrf_m:
                reasons.append("AI_AUTHORED_UNRECEIPTED")
            else:
                m_src_hashes = re.search(r"Source Hashes:\s*([^\n]+)", text)
                if not m_src_hashes:
                    reasons.append("AI_AUTHORED_UNRECEIPTED")
                else:
                    claimed_token = vrf_m.group(0).upper()
                    hash_entries = re.findall(r"([A-Za-z0-9_./-]+)\(([0-9a-f]{10})\)", m_src_hashes.group(1))
                    if not hash_entries:
                        reasons.append("AI_AUTHORED_UNRECEIPTED")
                    else:
                        seed = "|".join(f"{normalize_source_relpath(fn)}:{h}" for fn, h in sorted(hash_entries))
                        computed = "VRF-" + hashlib.sha256(seed.encode("utf-8")).hexdigest()[:12].upper()
                        seed_legacy = "|".join(f"{os.path.basename(fn)}:{h}" for fn, h in sorted(hash_entries))
                        computed_legacy = "VRF-" + hashlib.sha256(seed_legacy.encode("utf-8")).hexdigest()[:12].upper()
                        if claimed_token != computed and claimed_token != computed_legacy:
                            reasons.append("AI_AUTHORED_UNRECEIPTED (forged or mismatched VRF receipt)")
                        else:
                            for fn, h in hash_entries:
                                mem_root = os.environ.get(
                                    "HOMUNCULUS_MEMORY_ROOT",
                                    os.path.join(_SCRIPT_ENG_ROOT, "memory"),
                                )
                                cand_paths = [
                                    os.path.join(parent_dir, fn),
                                    os.path.join(mem_root, fn),
                                    os.path.join(_SCRIPT_ENG_ROOT, fn),
                                    fn if os.path.isabs(fn) else "",
                                ]
                                resolved = next((cp for cp in cand_paths if cp and os.path.isfile(cp)), None)
                                if resolved:
                                    actual_h = hashlib.sha256(open(resolved, "rb").read()).hexdigest()[:10]
                                    if actual_h != h:
                                        reasons.append(f"AI_AUTHORED_UNRECEIPTED (hash mismatch for {fn}: claimed {h} != actual {actual_h})")
                                        break
                                elif os.path.isabs(fn) or "/" in fn:
                                    reasons.append(f"AI_AUTHORED_UNRECEIPTED (referenced source file '{fn}' not found)")
                                    break
        if TBD_MARKER_RE.search(text):
            reasons.append("CONTAINS_OPEN_TBD")

    return reasons


DERIVATIVE_RENDER_EXTENSIONS = {".svg", ".html"}
CODE_SOURCE_EXTENSIONS = {".py", ".sh", ".js", ".ts", ".c", ".h", ".cpp", ".hpp"}


def _is_sibling_derivative_of_target(
    candidate_rp: str,
    target_rp: Optional[str],
    target_dir_stem: Optional[Tuple[str, str]],
) -> bool:
    if not target_rp or not target_dir_stem:
        return False
    cand_dir = os.path.dirname(candidate_rp)
    cand_stem, cand_ext = os.path.splitext(os.path.basename(candidate_rp))
    if cand_ext.lower() not in DERIVATIVE_RENDER_EXTENSIONS:
        return False
    t_dir, t_stem = target_dir_stem
    c_low = cand_stem.lower()
    return cand_dir == t_dir and (c_low == t_stem or c_low == f"{t_stem}_card")


def _is_lessons_learned_source(fp: str) -> bool:
    """Return True if the file is a historical Lessons Learned ledger (`*_Lessons_Learned.md`), explicitly `authoritative: false`, inside `Quarantine/`, or inside `study_briefs/`."""
    bname_low = os.path.basename(fp).lower()
    parts_low = [seg.lower() for seg in os.path.abspath(fp).split(os.sep)]
    if "quarantine" in parts_low or "study_briefs" in parts_low:
        return True
    if bname_low.endswith("_lessons_learned.md") or bname_low == "lessons_learned_template.md":
        return True
    if bname_low.endswith(".md") and os.path.isfile(fp):
        try:
            with open(fp, "rb") as fh:
                head = fh.read(512).decode("utf-8", errors="ignore")
            if head.startswith("---") and re.search(
                r"^(?:authoritative:\s*false|status:\s*['\"]?NON_AUTHORITATIVE_REFERENCE['\"]?)\b",
                head,
                re.IGNORECASE | re.MULTILINE,
            ):
                return True
        except OSError:
            pass
    return False


def collect_source_files(
    paths: List[str],
    target_path: Optional[str] = None,
    allow_lessons_source: bool = False,
) -> Tuple[List[str], List[str], List[str]]:
    collected: List[str] = []
    excluded_circular: List[str] = []
    excluded_lessons: List[str] = []
    seen: Set[str] = set()
    target_rp: Optional[str] = None
    target_dir_stem: Optional[Tuple[str, str]] = None
    if target_path and target_path != "-" and os.path.exists(target_path):
        target_rp = os.path.realpath(target_path)
        target_dir_stem = (
            os.path.dirname(target_rp),
            os.path.splitext(os.path.basename(target_rp))[0].lower(),
        )

    explicit_dirs = {os.path.realpath(p) for p in paths if os.path.isdir(p)}

    for p in paths:
        if not os.path.exists(p):
            raise FileNotFoundError(f"Authoritative source path does not exist: {p}")
        if os.path.isfile(p):
            rp = os.path.realpath(p)
            rp_parts_low = [seg.lower() for seg in rp.split(os.sep)]
            if "quarantine" in rp_parts_low and not allow_lessons_source:
                raise ValueError(
                    f"QUARANTINE_SOURCE_REJECTED: Source file '{p}' resides inside a Quarantine/ "
                    f"directory and cannot be used as authoritative ground truth."
                )
            if "study_briefs" in rp_parts_low and not allow_lessons_source:
                raise ValueError(
                    f"STUDY_BRIEF_SOURCE_REJECTED: Source file '{p}' resides inside an unpromoted study_briefs/ "
                    f"directory and cannot be used as authoritative ground truth until promoted to memory/."
                )
            if target_rp and (
                rp == target_rp
                or _is_sibling_derivative_of_target(rp, target_rp, target_dir_stem)
            ):
                raise ValueError(
                    f"Self-referential circular validation blocked: --target '{target_path}' cannot validate against '{p}'."
                )
            if not allow_lessons_source and _is_lessons_learned_source(p):
                excluded_lessons.append(p)
                continue
            if rp not in seen:
                seen.add(rp)
                collected.append(p)
        elif os.path.isdir(p):
            for root, dirs, files in os.walk(p):
                kept_dirs = []
                for d in dirs:
                    if d.startswith(".") or d == "__pycache__":
                        continue
                    if d in BULK_EXCLUDE_DIRS:
                        subpath = os.path.realpath(os.path.join(root, d))
                        if subpath not in explicit_dirs and not any(exp.startswith(subpath + os.sep) for exp in explicit_dirs):
                            continue
                    kept_dirs.append(d)
                dirs[:] = sorted(kept_dirs)
                for fn in sorted(files):
                    ext = os.path.splitext(fn)[1].lower()
                    if ext in TEXT_EXTENSIONS or fn in ("LICENSE", "CNAME"):
                        fp = os.path.join(root, fn)
                        rp = os.path.realpath(fp)
                        if target_rp and (
                            rp == target_rp
                            or _is_sibling_derivative_of_target(rp, target_rp, target_dir_stem)
                        ):
                            excluded_circular.append(fp)
                            continue
                        if not allow_lessons_source and _is_lessons_learned_source(fp):
                            excluded_lessons.append(fp)
                            continue
                        if rp not in seen:
                            seen.add(rp)
                            collected.append(fp)
    return collected, excluded_circular, excluded_lessons


def map_qualifier_group(raw_q: str) -> Optional[str]:
    ql = re.sub(r"\s+", " ", raw_q.lower().strip())
    for grp, syns in QUALIFIER_GROUPS:
        if ql in syns:
            return grp
    return None


class SourceFileInfo:
    def __init__(self, fp: str, text: str, h10: str) -> None:
        self.fp = fp
        self.abs_fp = os.path.abspath(fp)
        self.h10 = h10
        self.lines = text.splitlines()
        self.line_count = max(1, len(self.lines))
        self.frontmatter_range: Optional[Tuple[int, int]] = None
        if self.lines and self.lines[0].strip() == "---":
            for idx in range(1, len(self.lines)):
                if self.lines[idx].strip() == "---":
                    self.frontmatter_range = (1, idx + 1)
                    break

        self.quarantined_ranges: List[Tuple[int, int, str]] = []
        q_start: Optional[int] = None
        q_lvl: Optional[int] = None
        q_title: str = ""
        marker_start: Optional[int] = None
        marker_title: str = ""
        for idx, ln in enumerate(self.lines):
            line_no = idx + 1
            s_ln = ln.strip()
            if re.search(r"<!--\s*(?:QUARANTINE-ZONE|SESSION-HANDOFF|FIRST-PRINCIPLES-THEORY):START\s*-->", s_ln, re.IGNORECASE):
                marker_start = line_no
                if "SESSION-HANDOFF" in s_ln.upper():
                    marker_title = "SESSION-HANDOFF"
                elif "FIRST-PRINCIPLES-THEORY" in s_ln.upper():
                    marker_title = "FIRST-PRINCIPLES-THEORY"
                else:
                    marker_title = "QUARANTINE-ZONE"
            if marker_start is not None and re.search(r"<!--\s*(?:QUARANTINE-ZONE|SESSION-HANDOFF|FIRST-PRINCIPLES-THEORY):END\s*-->", s_ln, re.IGNORECASE):
                self.quarantined_ranges.append((marker_start, line_no, marker_title))
                marker_start = None
                marker_title = ""
            hm = HEADING_LEVEL_RE.match(s_ln)
            if hm:
                lvl = len(hm.group(1))
                if q_lvl is not None and lvl <= q_lvl:
                    self.quarantined_ranges.append((q_start, line_no - 1, q_title))
                    q_start = None
                    q_lvl = None
                    q_title = ""
                if QUARANTINE_HEADING_RE.match(s_ln):
                    q_start = line_no
                    q_lvl = lvl
                    q_title = s_ln
        if q_start is not None:
            self.quarantined_ranges.append((q_start, len(self.lines), q_title))

        self.customer_entity = ""
        self.raw_customer_token = ""
        m_cust = re.search(
            r"^\s*['\"]?entity['\"]?\s*:\s*['\"\[]?([A-Za-z0-9_-]+)['\"\]]?",
            text[:500],
            re.IGNORECASE | re.MULTILINE,
        )
        if m_cust:
            raw_c = m_cust.group(1).lower().replace("-", "_")
            if raw_c not in ("default_entity", "my_organization", "shared", "none", "unset"):
                self.raw_customer_token = raw_c
                self.customer_entity = _canonicalize_entity_token(raw_c)

        self.entity = self._detect_entity(text)

    def check_warning_context(self, start_line: int, end_line: int, claiming_text: str) -> Optional[str]:
        ext = os.path.splitext(self.abs_fp)[1].lower()
        is_code = ext in CODE_SOURCE_EXTENSIONS
        c_st = max(1, start_line - 5)
        c_en = min(self.line_count, end_line + 5)
        for idx in range(c_st - 1, c_en):
            ln = self.lines[idx]
            if is_code:
                # In executable source code, inspect only comment annotations so regex/identifier literals don't false-trigger
                m_cmt = re.search(r"(?:#|//|/\*)(.*)$", ln)
                if not m_cmt:
                    continue
                ln = m_cmt.group(1)
            wm = WARNING_CONTEXT_RE.search(ln)
            if wm:
                if not WARNING_ACK_RE.search(claiming_text):
                    return f"Source line {idx + 1} contains warning/prohibition context ('{wm.group(0).strip()}') without citation acknowledging hazard/negation"
        return None

    def _detect_entity(self, text: str) -> str:
        bname = os.path.basename(self.abs_fp).lower()
        path_parts = [seg for seg in self.abs_fp.lower().split(os.sep) if seg]
        if (
            "fastener" in bname
            or "style" in bname
            or "standard" in bname
            or "standards_and_specs" in path_parts
            or "templates" in path_parts
            or "engineering_logs" in path_parts
            or "visuals" in path_parts
            or "tasks" in path_parts
        ):
            return "*"
        if re.search(
            r"^type:\s*(?:standard|moc-hub|task-umbrella|task-landing-pad|engineering-log|architecture-diagram|command-reference)\b",
            text[:500],
            re.IGNORECASE | re.MULTILINE,
        ):
            return "*"
        m_proj = re.search(
            r"^\s*['\"]?(?:project|parent_note)['\"]?\s*:\s*['\"\[]?([A-Za-z0-9_-]+)['\"\]]?",
            text[:500],
            re.IGNORECASE | re.MULTILINE,
        )
        if m_proj:
            raw_p = m_proj.group(1).lower().replace("-", "_")
            return _canonicalize_entity_token(raw_p)
        m_ent = re.search(
            r"^\s*['\"]?entity['\"]?\s*:\s*['\"\[]?([A-Za-z0-9_-]+)['\"\]]?",
            text[:500],
            re.IGNORECASE | re.MULTILINE,
        )
        if m_ent:
            raw_e = m_ent.group(1).lower().replace("-", "_")
            if raw_e not in ("default_entity", "my_organization", "shared", "none", "unset"):
                return _canonicalize_entity_token(raw_e)
        for prefix in ("project_alpha", "project_beta", "client_a", "client_b"):
            if prefix in bname:
                return prefix
        # Inspect parent repository directory names from innermost folder outward
        for seg in reversed(path_parts[:-1]):
            if seg in ENTITY_ALIASES:
                return ENTITY_ALIASES[seg]
            for prefix in ("project_alpha", "project_beta", "client_a", "client_b"):
                if re.search(rf"(?:^|[_-]){prefix}(?:$|[_-])", seg):
                    return prefix
        # Walk from innermost parent directory outward so enclosing git repos
        # (e.g., /Projects/<Org>/<Repo>/.git) and leaf project folders win over outer org grouping folders.
        cur_d = os.path.dirname(self.abs_fp)
        prev_non_generic: Optional[str] = None
        while cur_d and cur_d != os.sep:
            d_base = os.path.basename(cur_d).lower().replace("-", "_")
            parent_d = os.path.dirname(cur_d)
            parent_base = os.path.basename(parent_d).lower().replace("-", "_") if parent_d and parent_d != cur_d else ""
            grandparent_d = os.path.dirname(parent_d) if parent_d and parent_d != cur_d else ""
            grandparent_base = (
                os.path.basename(grandparent_d).lower().replace("-", "_")
                if grandparent_d and grandparent_d != parent_d
                else ""
            )
            if d_base and not d_base.startswith(".") and d_base not in GENERIC_NON_ENTITY_SEGMENTS:
                if os.path.exists(os.path.join(cur_d, ".git")):
                    return _canonicalize_entity_token(d_base)
                if re.match(
                    r"^(?:project_[a-z0-9_]+|proj_[a-z0-9_]+|repo_[a-z0-9_]+|[a-z0-9]+_(?:remote_air|toolhead|gantry|bowden|air|extruder|heater|sensor|controller|board|assembly|drybox|rig|module|router))$",
                    d_base,
                ):
                    return _canonicalize_entity_token(d_base)
                if parent_base in ("projects", "repositories", "workspaces"):
                    if grandparent_base in ("memory", "homunculus_memory", "vault") or not prev_non_generic:
                        return _canonicalize_entity_token(d_base)
                    has_repo_root_markers = any(
                        os.path.exists(os.path.join(cur_d, marker))
                        for marker in (
                            "README.md",
                            "pyproject.toml",
                            "package.json",
                            "Cargo.toml",
                            "Makefile",
                            "CMakeLists.txt",
                            ".homunculus.json",
                            "BOM.md",
                            "Assembly_Guide.md",
                        )
                    )
                    chosen = d_base if has_repo_root_markers else prev_non_generic
                    return _canonicalize_entity_token(chosen)
                prev_non_generic = d_base
            if not parent_d or parent_d == cur_d:
                break
            cur_d = parent_d
        m_fn_ent = re.match(r"^([a-z0-9]+(?:_[a-z0-9]+)?)_(?:hardware|bom|spec|manifest|control)\.", bname)
        if m_fn_ent:
            cand_fn = m_fn_ent.group(1)
            if cand_fn not in GENERIC_NON_ENTITY_SEGMENTS:
                return _canonicalize_entity_token(cand_fn)
        return "*"


GENERIC_NON_ENTITY_SEGMENTS: Set[str] = {
    "home", "users", "root", "tmp", "var", "opt", "etc", "usr",
    "projects", "engineering", "workspaces", "repositories",
    "homunculus_memory", "memory", "vault", "quarantine", "study_briefs",
    "standards_and_specs", "templates", "visuals", "tasks", "engineering_logs",
    "rules", "skills", "scripts", "adapters", "docs", "references", "tests",
    "stl_files", "step_files", "cad", "firmware", "images", "assets", "releases",
    "scratch", "sandbox_runs", "brain", "sources", "src", "data", "config",
    "print", "assembly", "main", "rear", "front", "top", "bottom", "system", "repo", "skill",
}

GENERIC_ENTITY_PREFIXES: Set[str] = {
    "the", "new", "my", "our", "custom",
    "project", "proj", "repo", "repository", "workspace",
    "client", "customer", "tenant", "org", "team", "partner", "vendor",
    "system", "subsystem", "module", "board", "pcb", "mcu", "service",
    "app", "lib", "pkg", "node", "unit", "stage", "rig", "pod", "hub",
    "sensor", "motor", "heater", "valve", "pump", "drive", "test", "mock",
}

TRAILING_ROLE_SUFFIX_RE = re.compile(
    r"_(?:remote_air|toolhead|gantry|bowden|air|extruder|heater|sensor|controller|"
    r"board|pcb|assembly|drybox|rig|module|router|bracket|service|system|subsystem|"
    r"hardware|software|firmware|docs|spec|manifest|hub|v\d+|rev\d+|mk\d+)$"
)

ENTITY_ALIASES: Dict[str, str] = {
    "project_alpha": "project_alpha",
    "alpha": "project_alpha",
    "project_beta": "project_beta",
    "beta": "project_beta",
    "client_a": "client_a",
    "customer_a": "client_a",
    "client_b": "client_b",
    "customer_b": "client_b",
    "homunculus": "homunculus",
}


def _canonicalize_entity_token(raw_token: str) -> str:
    clean = raw_token.strip().lower().replace("-", "_")
    if clean in ENTITY_ALIASES:
        return ENTITY_ALIASES[clean]
    first = clean.split("_")[0]
    if first in GENERIC_ENTITY_PREFIXES and "_" in clean:
        return clean
    stripped = TRAILING_ROLE_SUFFIX_RE.sub("", clean)
    if stripped and stripped not in GENERIC_ENTITY_PREFIXES and stripped not in GENERIC_NON_ENTITY_SEGMENTS:
        return ENTITY_ALIASES.get(stripped, stripped)
    return ENTITY_ALIASES.get(clean, clean)


def detect_entities_in_text(
    text: str,
    known_entities: Optional[Set[str]] = None,
    extra_aliases: Optional[Dict[str, str]] = None,
) -> Set[str]:
    t_low = text.lower()
    found: Set[str] = set()
    combined_aliases = dict(ENTITY_ALIASES)
    if extra_aliases:
        combined_aliases.update(extra_aliases)
    for alias, canonical in combined_aliases.items():
        alias_pat = re.escape(alias).replace(r"\_", r"[\s_-]+")
        if re.search(rf"(?<![a-z0-9]){alias_pat}(?![a-z0-9])", t_low):
            if known_entities and canonical not in known_entities and "*" not in known_entities:
                continue
            found.add(canonical)
    if known_entities:
        for ke in known_entities:
            if ke != "*":
                ke_pat = re.escape(ke).replace(r"\_", r"[\s_-]+")
                if re.search(rf"(?<![a-z0-9]){ke_pat}(?![a-z0-9])", t_low):
                    found.add(ke)
    return found


def detect_entity_in_text(
    text: str,
    known_entities: Optional[Set[str]] = None,
    extra_aliases: Optional[Dict[str, str]] = None,
) -> Optional[str]:
    ents = detect_entities_in_text(text, known_entities, extra_aliases=extra_aliases)
    return sorted(ents)[0] if ents else None


class SourceIndex:
    def __init__(
        self,
        source_files: List[str],
        excluded_circular: Optional[List[str]] = None,
        excluded_lessons: Optional[List[str]] = None,
    ) -> None:
        self.file_hashes: List[Tuple[str, str]] = []
        self.provenance_warnings: List[Dict[str, object]] = []
        self.excluded_circular: List[str] = excluded_circular or []
        self.excluded_lessons: List[str] = excluded_lessons or []
        self.file_infos: Dict[str, SourceFileInfo] = {}
        self.num_units: Set[Tuple[float, str]] = set()
        self.entity_num_units: Dict[str, Set[Tuple[float, str]]] = {}
        self.qualified_num_units: Set[Tuple[float, str, str]] = set()
        self.entity_qualified_num_units: Dict[str, Set[Tuple[float, str, str]]] = {}
        self.counted_entities: Set[Tuple[float, str]] = set()
        self.entity_counted_entities: Dict[str, Set[Tuple[float, str]]] = {}
        self.numbers_all: Set[float] = set()
        self.entity_numbers_all: Dict[str, Set[float]] = {}
        self.fasteners: Set[str] = set()
        self.entity_fasteners: Dict[str, Set[str]] = {}
        self.designators: Set[str] = set()
        self.entity_designators: Dict[str, Set[str]] = {}
        self.source_basenames: Set[str] = set()
        self.source_max_lines: Dict[str, int] = {}
        self.source_dirs: Set[str] = set()
        self.raw_lower_chunks: List[str] = []
        self.entity_raw_chunks: Dict[str, List[str]] = {}
        self.entity_raw_blobs: Dict[str, str] = {}
        self.entity_raw_blobs_nocomma: Dict[str, str] = {}
        self.dynamic_aliases: Dict[str, str] = {}
        self.ambiguous_umbrellas: Dict[str, Set[str]] = {}

        git_cache = GitWorktreeCache()
        cust_to_projects: Dict[str, Set[str]] = {}
        prefix_to_projects: Dict[str, Set[str]] = {}

        for fp in source_files:
            raw_bytes = open(fp, "rb").read()
            h10 = hashlib.sha256(raw_bytes).hexdigest()[:10]
            self.file_hashes.append((fp, h10))
            bname_low = os.path.basename(fp).lower()
            abs_fp_low = os.path.abspath(fp).lower()
            self.source_basenames.add(bname_low)
            self.source_dirs.add(os.path.dirname(os.path.abspath(fp)))
            self.raw_lower_chunks.append(bname_low)
            text = raw_bytes.decode("utf-8", errors="replace")
            info = SourceFileInfo(fp, text, h10)
            self.file_infos[bname_low] = info
            self.file_infos[abs_fp_low] = info
            self.source_max_lines[bname_low] = max(self.source_max_lines.get(bname_low, 0), info.line_count)
            prov_reasons = inspect_source_provenance(fp, text, git_cache=git_cache)
            if prov_reasons:
                self.provenance_warnings.append({"file": fp, "reasons": prov_reasons})
            if info.entity != "*":
                for cust_tok in (info.customer_entity, info.raw_customer_token):
                    if cust_tok and cust_tok != info.entity:
                        cust_to_projects.setdefault(cust_tok, set()).add(info.entity)
                        compact_cust = cust_tok.replace("_", "")
                        if compact_cust and compact_cust != info.entity:
                            cust_to_projects.setdefault(compact_cust, set()).add(info.entity)
                if "_" in info.entity:
                    p_first = info.entity.split("_")[0]
                    if p_first not in GENERIC_ENTITY_PREFIXES and p_first not in GENERIC_NON_ENTITY_SEGMENTS:
                        prefix_to_projects.setdefault(p_first, set()).add(info.entity)
            self._index_text(text, info.entity)

        # Register customer_entity -> project_entity ONLY when unambiguous (1-to-1 across indexed sources).
        # Never alias an umbrella owner (e.g. Umbrella-Org) across multiple distinct projects (e.g. project_alpha vs project_beta).
        for cust_tok, proj_set in cust_to_projects.items():
            if len(proj_set) == 1:
                self.dynamic_aliases[cust_tok] = next(iter(proj_set))
            elif len(proj_set) > 1:
                self.ambiguous_umbrellas[cust_tok] = set(proj_set)
        for p_first, proj_set in prefix_to_projects.items():
            if len(proj_set) == 1 and p_first not in self.dynamic_aliases and p_first not in self.ambiguous_umbrellas:
                self.dynamic_aliases[p_first] = next(iter(proj_set))

        self.raw_blob = "\n".join(self.raw_lower_chunks)
        self.raw_blob_nocomma = re.sub(r"(?<=\d),(?=\d{3}\b)", "", self.raw_blob)

        for ent, chunks in self.entity_raw_chunks.items():
            blob = "\n".join(chunks)
            self.entity_raw_blobs[ent] = blob
            self.entity_raw_blobs_nocomma[ent] = re.sub(r"(?<=\d),(?=\d{3}\b)", "", blob)

        # Compute deterministic 12-hex Proof-of-Verification Receipt with normalized relative paths
        receipt_seed = "|".join(
            f"{normalize_source_relpath(fp)}:{h}" for fp, h in sorted(self.file_hashes)
        )
        self.vrf_token = "VRF-" + hashlib.sha256(receipt_seed.encode("utf-8")).hexdigest()[:12]

    def get_file_info(self, ref: str) -> Optional[SourceFileInfo]:
        ref_low = ref.lower()
        if ref_low in self.file_infos:
            return self.file_infos[ref_low]
        bname = os.path.basename(ref_low)
        return self.file_infos.get(bname)

    def _index_text(self, text: str, entity: str) -> None:
        q_text = quarantine_unverified_source_zones(text)
        low = q_text.lower()
        self.raw_lower_chunks.append(low)
        if entity not in self.entity_raw_chunks:
            self.entity_raw_chunks[entity] = []
        self.entity_raw_chunks[entity].append(low)

        if entity not in self.entity_num_units:
            self.entity_num_units[entity] = set()
            self.entity_qualified_num_units[entity] = set()
            self.entity_counted_entities[entity] = set()
            self.entity_fasteners[entity] = set()
            self.entity_designators[entity] = set()
            self.entity_numbers_all[entity] = set()

        for raw_ln in q_text.splitlines():
            if not DIGIT_RE.search(raw_ln):
                continue
            qual_scan_ln = re.sub(
                r"\([^()\n]*\b(?:not\s+specified|unspecified|unknown|undetermined|absent|not\s+defined)\b[^()\n]*\)",
                " ",
                raw_ln,
                flags=re.IGNORECASE,
            )
            if not re.search(
                r"\b(?:is|are|was|were|remains?)\s+not\s+(?:specified|defined|known|determined|provided)\b|\bnot\s+specified\s+in\b",
                qual_scan_ln,
                re.IGNORECASE,
            ):
                if QUALIFIER_QUICK_RE.search(qual_scan_ln) and SINGLE_NUM_UNIT_RE.search(qual_scan_ln):
                    ln_low = re.sub(r"\s+", " ", qual_scan_ln.lower())
                    active_grps = [
                        grp for grp, rx in COMPILED_QUALIFIER_GROUPS
                        if rx.search(ln_low)
                    ]
                    if active_grps:
                        for m in SINGLE_NUM_UNIT_RE.finditer(qual_scan_ln):
                            cu = canonicalize_unit(m.group(3), m.group(2))
                            if cu:
                                v = round(parse_num(m.group(1)), 6)
                                for g in active_grps:
                                    pair_q = (v, cu, g)
                                    self.qualified_num_units.add(pair_q)
                                    self.entity_qualified_num_units[entity].add(pair_q)

            if ALL_COUNTED_NOUN_STEM_RE.search(raw_ln):
                ln_unquoted = re.sub(r"`([+-]?\d[\d,.–—-]*)`", r"\1", raw_ln)
                ln_nouns = {normalize_counted_noun(nm.group(0)) for nm in ALL_COUNTED_NOUN_STEM_RE.finditer(ln_unquoted)}
                if ln_nouns:
                    for nm_num in re.finditer(
                        r"(?<![A-Za-z0-9_.#])(\d{1,3}(?:,\d{3})+|\d+)(?:[x×]\b|(?![A-Za-z0-9_.%]))",
                        ln_unquoted,
                        re.IGNORECASE,
                    ):
                        v_cnt = round(parse_num(nm_num.group(1)), 6)
                        for cn in ln_nouns:
                            pair_c = (v_cnt, cn)
                            self.counted_entities.add(pair_c)
                            self.entity_counted_entities[entity].add(pair_c)

        for m in METRIC_FASTENER_RE.finditer(q_text):
            fastener = normalize_fastener(m.group(1))
            self.fasteners.add(fastener)
            self.entity_fasteners[entity].add(fastener)

        for m in DESIGNATOR_RE.finditer(q_text):
            desig = normalize_designator(m.group(1))
            self.designators.add(desig)
            self.entity_designators[entity].add(desig)

        for m in SHORE_RE.finditer(q_text):
            shore_tok = re.sub(r"^shore\s*", "", m.group(0).lower()).strip()
            self.designators.add(f"shore:{shore_tok}")
            self.entity_designators[entity].add(f"shore:{shore_tok}")

        num_scan_text = re.sub(r"`([+-]?\d[\d,.–—-]*)`", r"\1", q_text)

        for m in RANGE_NUM_UNIT_RE.finditer(num_scan_text):
            n1, u1, n2, u2 = m.group(1), m.group(2), m.group(3), m.group(4)
            cu2 = canonicalize_unit(u2, " ") or ("words" if u2 == "w" else UNIT_ALIASES.get(u2.lower()))
            cu1 = (
                (canonicalize_unit(u1, " ") or ("words" if u1 == "w" else UNIT_ALIASES.get(u1.lower())))
                if u1
                else cu2
            )
            if cu1:
                p1 = (round(parse_num(n1), 6), cu1)
                self.num_units.add(p1)
                self.entity_num_units[entity].add(p1)
            if cu2:
                p2 = (round(parse_num(n2), 6), cu2)
                self.num_units.add(p2)
                self.entity_num_units[entity].add(p2)

        for m in SINGLE_NUM_UNIT_RE.finditer(num_scan_text):
            n_str, sep, u_str = m.group(1), m.group(2), m.group(3)
            cu = canonicalize_unit(u_str, sep)
            if cu:
                val = round(parse_num(n_str), 6)
                p = (val, cu)
                self.num_units.add(p)
                self.entity_num_units[entity].add(p)
                if val < 0:
                    self.num_units.add((abs(val), cu))
                    self.entity_num_units[entity].add((abs(val), cu))

        if SPELLED_QUICK_RE.search(low):
            for m in SPELLED_NUM_UNIT_RE.finditer(q_text):
                w_str, u_str = m.group(1).lower(), m.group(2)
                cu = canonicalize_unit(u_str, "")
                if cu and w_str in WORD_NUMBERS:
                    p = (round(WORD_NUMBERS[w_str], 6), cu)
                    self.num_units.add(p)
                    self.entity_num_units[entity].add(p)

        if "x × y × z (mm)" in low:
            for m_env in re.finditer(r"(\d+\.\d+)\s*×\s*(\d+\.\d+)\s*×\s*(\d+\.\d+)", q_text):
                for grp_i in (1, 2, 3):
                    p = (round(parse_num(m_env.group(grp_i)), 6), "mm")
                    self.num_units.add(p)
                    self.entity_num_units[entity].add(p)
            for m_vol in re.finditer(r"`\d+\.\d+\s*×\s*\d+\.\d+\s*×\s*\d+\.\d+`\s*\|\s*`(\d+\.\d+)`", q_text):
                p = (round(parse_num(m_vol.group(1)), 6), "cm3")
                self.num_units.add(p)
                self.entity_num_units[entity].add(p)

        # Standalone numbers: mask dates and git commit SHAs to prevent date bleed into numbers_all
        num_clean = DATE_SHA_MASK_RE.sub(" ", q_text)
        for m in re.finditer(r"(?<![A-Za-z0-9_.])([+-]?\d+(?:,\d{3})*(?:\.\d+)?)(?:[x×]\b|(?![A-Za-z0-9_.]))", num_clean, re.IGNORECASE):
            try:
                num_v = round(parse_num(m.group(1)), 6)
                self.numbers_all.add(num_v)
                self.entity_numbers_all[entity].add(num_v)
            except ValueError:
                pass

    def has_num_unit(self, val: float, cu: str, entities: Optional[Union[str, Set[str]]] = None, entity: Optional[str] = None) -> Tuple[bool, Optional[str]]:
        rval = round(val, 6)
        pair = (rval, cu)
        ent_set: Set[str] = set()
        if entities is not None:
            ent_set = {entities} if isinstance(entities, str) else set(entities)
        elif entity is not None:
            ent_set = {entity}

        active = {e for e in ent_set if e != "*"}
        if active:
            allowed = set()
            for e in active:
                allowed |= self.entity_num_units.get(e, set())
            allowed |= self.entity_num_units.get("*", set())
            if pair in allowed:
                return True, None
            for other_ent, s in self.entity_num_units.items():
                if other_ent not in active and other_ent != "*" and pair in s:
                    return False, f"CROSS_ENTITY_BORROWING({other_ent} -> {', '.join(sorted(active))})"
            return pair in self.num_units, None
        return pair in self.num_units, None

    def has_counted_entity(self, val: float, noun: str, entities: Optional[Union[str, Set[str]]] = None, entity: Optional[str] = None) -> Tuple[bool, Optional[str]]:
        rval = round(val, 6)
        pair = (rval, noun)
        ent_set: Set[str] = set()
        if entities is not None:
            ent_set = {entities} if isinstance(entities, str) else set(entities)
        elif entity is not None:
            ent_set = {entity}

        active = {e for e in ent_set if e != "*"}
        if active:
            allowed = set()
            for e in active:
                allowed |= self.entity_counted_entities.get(e, set())
            allowed |= self.entity_counted_entities.get("*", set())
            if pair in allowed:
                return True, None
            for other_ent, s in self.entity_counted_entities.items():
                if other_ent not in active and other_ent != "*" and pair in s:
                    return False, f"CROSS_ENTITY_BORROWING({other_ent} -> {', '.join(sorted(active))})"
            return pair in self.counted_entities, None
        return pair in self.counted_entities, None

    def has_qualified_num_unit(self, val: float, cu: str, grp: str, entities: Optional[Union[str, Set[str]]] = None, entity: Optional[str] = None) -> Tuple[bool, Optional[str]]:
        rval = round(val, 6)
        trip = (rval, cu, grp)
        ent_set: Set[str] = set()
        if entities is not None:
            ent_set = {entities} if isinstance(entities, str) else set(entities)
        elif entity is not None:
            ent_set = {entity}

        active = {e for e in ent_set if e != "*"}
        if active:
            allowed = set()
            for e in active:
                allowed |= self.entity_qualified_num_units.get(e, set())
            allowed |= self.entity_qualified_num_units.get("*", set())
            if trip in allowed:
                return True, None
            for other_ent, s in self.entity_qualified_num_units.items():
                if other_ent not in active and other_ent != "*" and trip in s:
                    return False, f"CROSS_ENTITY_BORROWING({other_ent} -> {', '.join(sorted(active))})"
            return trip in self.qualified_num_units, None
        return trip in self.qualified_num_units, None

    def has_fastener(self, raw_f: str, entities: Optional[Union[str, Set[str]]] = None, entity: Optional[str] = None) -> Tuple[bool, Optional[str]]:
        nf = normalize_fastener(raw_f)
        ent_set: Set[str] = set()
        if entities is not None:
            ent_set = {entities} if isinstance(entities, str) else set(entities)
        elif entity is not None:
            ent_set = {entity}

        active = {e for e in ent_set if e != "*"}
        if active:
            allowed = set()
            for e in active:
                allowed |= self.entity_fasteners.get(e, set())
            allowed |= self.entity_fasteners.get("*", set())
            if nf in allowed or self._fastener_in_blob(nf, entities=active):
                return True, None
            for other_ent, s in self.entity_fasteners.items():
                if other_ent not in active and other_ent != "*" and (nf in s or self._fastener_in_blob(nf, entities={other_ent})):
                    return False, f"CROSS_ENTITY_BORROWING({other_ent} -> {', '.join(sorted(active))})"
            return nf in self.fasteners or self._fastener_in_blob(nf), None
        return nf in self.fasteners or self._fastener_in_blob(nf), None

    def _fastener_in_blob(self, nf: str, entities: Optional[Set[str]] = None, entity: Optional[str] = None) -> bool:
        pat = rf"(?<![a-z0-9]){re.escape(nf)}(?![a-z0-9])"
        ent_set: Set[str] = set()
        if entities is not None:
            ent_set = set(entities)
        elif entity is not None:
            ent_set = {entity}
        active = {e for e in ent_set if e != "*"}
        if active:
            blobs = [self.entity_raw_blobs.get(e, "") for e in active]
            blobs.append(self.entity_raw_blobs.get("*", ""))
            joined = "\n".join(blobs)
            return (nf in joined) and bool(re.search(pat, joined))
        return (nf in self.raw_blob) and bool(re.search(pat, self.raw_blob))

    def has_designator(self, raw_d: str, entities: Optional[Union[str, Set[str]]] = None, entity: Optional[str] = None) -> Tuple[bool, Optional[str]]:
        nd = normalize_designator(raw_d)
        ent_set: Set[str] = set()
        if entities is not None:
            ent_set = {entities} if isinstance(entities, str) else set(entities)
        elif entity is not None:
            ent_set = {entity}

        active = {e for e in ent_set if e != "*"}
        if active:
            allowed = set()
            for e in active:
                allowed |= self.entity_designators.get(e, set())
            allowed |= self.entity_designators.get("*", set())
            if nd in allowed or self._designator_in_blob(nd, entities=active):
                return True, None
            for other_ent, s in self.entity_designators.items():
                if other_ent not in active and other_ent != "*" and (nd in s or self._designator_in_blob(nd, entities={other_ent})):
                    return False, f"CROSS_ENTITY_BORROWING({other_ent} -> {', '.join(sorted(active))})"
            return nd in self.designators or self._designator_in_blob(nd), None
        return nd in self.designators or self._designator_in_blob(nd), None

    def _designator_in_blob(self, nd: str, entities: Optional[Set[str]] = None, entity: Optional[str] = None) -> bool:
        alt_space = nd.replace("-", r"[\s-]+")
        pat = rf"(?<![a-z0-9]){alt_space}(?![a-z0-9])"
        ent_set: Set[str] = set()
        if entities is not None:
            ent_set = set(entities)
        elif entity is not None:
            ent_set = {entity}
        active = {e for e in ent_set if e != "*"}
        if active:
            blobs = [self.entity_raw_blobs.get(e, "") for e in active]
            blobs.append(self.entity_raw_blobs.get("*", ""))
            joined = "\n".join(blobs)
            return bool(re.search(pat, joined))
        return bool(re.search(pat, self.raw_blob))

    def has_shore(self, raw_s: str) -> bool:
        shore_tok = re.sub(r"^shore\s*", "", raw_s.lower()).strip()
        return (f"shore:{shore_tok}" in self.designators) or (shore_tok in self.raw_blob)

    def has_backtick_literal(self, tok: str, entities: Optional[Union[str, Set[str]]] = None, entity: Optional[str] = None) -> Tuple[bool, Optional[str]]:
        t = tok.strip()
        t_low = t.lower()
        ent_set: Set[str] = set()
        if entities is not None:
            ent_set = {entities} if isinstance(entities, str) else set(entities)
        elif entity is not None:
            ent_set = {entity}

        if " " in t and not re.search(r"\.(?:stl|step|stp|xlsx|cfg|py|md|json|csv)\b|![A-Z]+\d+", t_low):
            parts = [p.strip("(),") for p in t.split() if p.strip("(),")]
            for p in parts:
                ok, err = self._single_token_in_source(p, entities=ent_set)
                if not ok:
                    return False, err
            return True, None
        return self._single_token_in_source(t, entities=ent_set)

    def _single_token_in_source(self, tok: str, entities: Optional[Set[str]] = None) -> Tuple[bool, Optional[str]]:
        tl = tok.strip("`'\"()[]{}").lower().strip()
        if not tl:
            return True, None
        if "=" in tl and not tl.startswith("="):
            ok1, err1 = self._exact_token_match(tl, entities=entities)
            if ok1:
                return True, None
            lhs, rhs = tl.split("=", 1)
            ok_lhs, err_lhs = self._exact_token_match(lhs, entities=entities)
            ok_rhs, err_rhs = self._exact_token_match(rhs, entities=entities)
            if not ok_lhs:
                return False, err_lhs
            if not ok_rhs:
                return False, err_rhs
            return True, None
        return self._exact_token_match(tl, entities=entities)

    def _exact_token_match(self, tl: str, entities: Optional[Set[str]] = None) -> Tuple[bool, Optional[str]]:
        tl_nocomma = re.sub(r"(?<=\d),(?=\d{3}\b)", "", tl)
        pat1 = rf"(?<![a-z0-9]){re.escape(tl)}(?![a-z0-9])"
        pat2 = rf"(?<![a-z0-9]){re.escape(tl_nocomma)}(?![a-z0-9])"
        active = {e for e in (entities or set()) if e != "*"}
        if active:
            blobs1 = [self.entity_raw_blobs.get(e, "") for e in active] + [self.entity_raw_blobs.get("*", "")]
            blobs2 = [self.entity_raw_blobs_nocomma.get(e, "") for e in active] + [self.entity_raw_blobs_nocomma.get("*", "")]
            b1 = "\n".join(blobs1)
            b2 = "\n".join(blobs2)
            if (tl in b1 and bool(re.search(pat1, b1))) or (tl_nocomma in b2 and bool(re.search(pat2, b2))):
                return True, None
            for other_ent in self.entity_raw_blobs:
                if other_ent not in active and other_ent != "*":
                    ob1 = self.entity_raw_blobs.get(other_ent, "")
                    ob2 = self.entity_raw_blobs_nocomma.get(other_ent, "")
                    if (tl in ob1 and bool(re.search(pat1, ob1))) or (tl_nocomma in ob2 and bool(re.search(pat2, ob2))):
                        return False, f"CROSS_ENTITY_BORROWING({other_ent} -> {', '.join(sorted(active))})"
            in_global = (tl in self.raw_blob and bool(re.search(pat1, self.raw_blob))) or (tl_nocomma in self.raw_blob_nocomma and bool(re.search(pat2, self.raw_blob_nocomma)))
            return in_global, None
        in_global = (tl in self.raw_blob and bool(re.search(pat1, self.raw_blob))) or (tl_nocomma in self.raw_blob_nocomma and bool(re.search(pat2, self.raw_blob_nocomma)))
        return in_global, None


def _safe_eval_arith_with_dim(
    node: ast.AST, unit_vars: Dict[str, Tuple[float, Optional[str]]]
) -> Tuple[float, Optional[str]]:
    """Safely evaluate arithmetic (+, -, *, /, **) with physical dimension propagation."""
    if isinstance(node, ast.Expression):
        return _safe_eval_arith_with_dim(node.body, unit_vars)
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)) and not isinstance(node.value, bool):
        return float(node.value), None
    if isinstance(node, ast.Name):
        if node.id in unit_vars:
            return unit_vars[node.id]
        raise ValueError(f"Unknown variable: {node.id}")
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.UAdd, ast.USub)):
        v, d = _safe_eval_arith_with_dim(node.operand, unit_vars)
        return (v if isinstance(node.op, ast.UAdd) else -v), d
    if isinstance(node, ast.BinOp):
        v1, d1 = _safe_eval_arith_with_dim(node.left, unit_vars)
        v2, d2 = _safe_eval_arith_with_dim(node.right, unit_vars)
        if d1 == "count":
            d1 = None
        if d2 == "count":
            d2 = None
        if isinstance(node.op, ast.Add):
            if d1 is not None and d2 is not None and d1 != d2:
                raise ValueError(f"Incompatible dimensions in addition: {d1} vs {d2}")
            return v1 + v2, (d1 or d2)
        if isinstance(node.op, ast.Sub):
            if d1 is not None and d2 is not None and d1 != d2:
                raise ValueError(f"Incompatible dimensions in subtraction: {d1} vs {d2}")
            return v1 - v2, (d1 or d2)
        if isinstance(node.op, ast.Mult):
            res_v = v1 * v2
            if d1 is None:
                return res_v, d2
            if d2 is None:
                return res_v, d1
            if (d1, d2) in (("current", "voltage"), ("voltage", "current")):
                return res_v, "power"
            if (d1, d2) in (("current", "resistance"), ("resistance", "current")):
                return res_v, "voltage"
            if (d1, d2) in (("force", "length"), ("length", "force")):
                return res_v, "torque"
            if (d1, d2) in (("speed", "time"), ("time", "speed")):
                return res_v, "length"
            if (d1, d2) in (("flow", "time"), ("time", "flow")):
                return res_v, "volume"
            if (d1, d2) in (("power", "time"), ("time", "power")):
                return res_v, "energy"
            if (d1, d2) in (("current", "time"), ("time", "current")):
                return res_v, "energy"
            if (d1, d2) in (("area", "length"), ("length", "area")):
                return res_v, "volume"
            if d1 == "length" and d2 == "length":
                return res_v, "area"
            raise ValueError(f"Incompatible dimensions in multiplication: {d1} * {d2}")
        if isinstance(node.op, ast.Div):
            res_v = v1 / v2
            if d2 is None:
                return res_v, d1
            if d1 == d2:
                return res_v, None
            if d1 == "power" and d2 == "voltage":
                return res_v, "current"
            if d1 == "power" and d2 == "current":
                return res_v, "voltage"
            if d1 == "voltage" and d2 == "current":
                return res_v, "resistance"
            if d1 == "voltage" and d2 == "resistance":
                return res_v, "current"
            if d1 == "length" and d2 == "time":
                return res_v, "speed"
            if d1 == "length" and d2 == "speed":
                return res_v, "time"
            if d1 == "volume" and d2 == "time":
                return res_v, "flow"
            if d1 == "volume" and d2 == "flow":
                return res_v, "time"
            if d1 == "energy" and d2 == "power":
                return res_v, "time"
            if d1 == "energy" and d2 == "time":
                return res_v, "power"
            if d1 == "torque" and d2 == "length":
                return res_v, "force"
            if d1 == "torque" and d2 == "force":
                return res_v, "length"
            if d1 == "volume" and d2 == "area":
                return res_v, "length"
            if d1 == "volume" and d2 == "length":
                return res_v, "area"
            if d1 == "area" and d2 == "length":
                return res_v, "length"
            raise ValueError(f"Incompatible dimensions in division: {d1} / {d2}")
        if isinstance(node.op, ast.Pow):
            if d2 is not None:
                raise ValueError("Exponents must be dimensionless scalars")
            return v1 ** v2, d1
    raise ValueError(f"Unsupported arithmetic node: {type(node).__name__}")


def verify_calc_marker(
    calc_body: str, idx: SourceIndex, require_source_operands: bool = True
) -> Tuple[bool, str, Optional[Tuple[float, str]], Optional[float]]:
    """
    Verify `[CALC: <lhs_expr> = <rhs_val><unit>]`:
      1. Every `<num><unit>` operand in `<lhs_expr>` must exist in `idx.num_units` (when require_source_operands=True).
      2. Every bare number in `<lhs_expr>` (excluding `** 2` / `** 3` formula exponents)
         must exist in `idx.numbers_all` (when require_source_operands=True).
      3. Pure arithmetic `<lhs_expr>` must equal `<rhs_val>` within rounding tolerance.
      4. Dimensional physics must hold: units must not suffer dimensional mismatch.
    Returns `(ok, tag, derived_num_unit_pair, derived_rhs_number)`.
    """
    if "=" not in calc_body:
        return False, "CALC_SYNTAX_ERROR", None, None
    lhs_raw, rhs_raw = calc_body.split("=", 1)

    unit_vars: Dict[str, Tuple[float, Optional[str]]] = {}
    lhs_expr = lhs_raw
    lhs_bare_scan = lhs_raw
    unit_matches = list(SINGLE_NUM_UNIT_RE.finditer(lhs_raw))

    for idx_i, m in enumerate(reversed(unit_matches)):
        n_str, sep, u_str = m.group(1), m.group(2), m.group(3)
        cu = canonicalize_unit(u_str, sep) or UNIT_ALIASES.get(re.sub(r"\s+", " ", u_str.lower().strip()))
        if not cu:
            continue
        val = parse_num(n_str)
        if require_source_operands:
            ok_op, _ = idx.has_num_unit(val, cu)
            if not ok_op:
                return False, f"CALC_UNBACKED_OPERAND({m.group(0).strip()})", None, None
        var_name = f"__u{idx_i}__"
        dim = UNIT_DIMENSIONS.get(cu)
        if dim == "count":
            dim = None
        unit_vars[var_name] = (val, dim)
        st, en = m.start(), m.end()
        lhs_expr = lhs_expr[:st] + var_name + lhs_expr[en:]

    for m in unit_matches:
        st, en = m.start(), m.end()
        lhs_bare_scan = lhs_bare_scan[:st] + (" " * (en - st)) + lhs_bare_scan[en:]

    lhs_bare_no_exp = re.sub(r"(?:\*\*|\^)\s*[23]\b", " ", lhs_bare_scan)
    if require_source_operands:
        for m_bare in re.finditer(r"(?<![A-Za-z0-9_.])[+-]?\d+(?:,\d{3})*(?:\.\d+)?(?![A-Za-z0-9_.])", lhs_bare_no_exp):
            bval = round(parse_num(m_bare.group(0)), 6)
            if bval not in idx.numbers_all:
                return False, f"CALC_UNBACKED_NUMBER({m_bare.group(0)})", None, None

    lhs_expr = re.sub(r"(?<=\d),(?=\d{3}\b)", "", lhs_expr)
    lhs_expr = lhs_expr.replace("×", "*").replace("^", "**")

    derived_pair: Optional[Tuple[float, str]] = None
    rhs_dim: Optional[str] = None
    m_rhs_unit = SINGLE_NUM_UNIT_RE.search(rhs_raw)
    if m_rhs_unit:
        rhs_val = parse_num(m_rhs_unit.group(1))
        rhs_cu = canonicalize_unit(m_rhs_unit.group(3), m_rhs_unit.group(2)) or UNIT_ALIASES.get(
            re.sub(r"\s+", " ", m_rhs_unit.group(3).lower().strip())
        )
        if rhs_cu:
            derived_pair = (round(rhs_val, 6), rhs_cu)
            rhs_dim = UNIT_DIMENSIONS.get(rhs_cu)
            if rhs_dim == "count":
                rhs_dim = None
    else:
        m_rhs = re.search(r"[+-]?\d+(?:,\d{3})*(?:\.\d+)?", rhs_raw)
        if not m_rhs:
            return False, "CALC_MISSING_RHS_VALUE", None, None
        rhs_val = parse_num(m_rhs.group(0))

    try:
        tree = ast.parse(lhs_expr.strip(), mode="eval")
        calc_val, calc_dim = _safe_eval_arith_with_dim(tree, unit_vars)
    except Exception as exc:
        return False, f"CALC_EVAL_ERROR({exc})", None, None

    if rhs_dim is not None and calc_dim is not None and calc_dim != rhs_dim:
        return False, f"CALC_DIMENSIONAL_MISMATCH(lhs={calc_dim},rhs={rhs_dim})", None, None
    if rhs_dim is None and calc_dim is not None:
        return False, f"CALC_DROPPED_UNIT(expected_dim={calc_dim})", None, None

    tol = max(0.015, abs(calc_val) * 0.005)
    if abs(calc_val - rhs_val) > tol:
        return False, f"CALC_MATH_MISMATCH(expected={calc_val:.4g},got={rhs_val})", None, None

    return True, "VERIFIED_CALC", derived_pair, round(rhs_val, 6)


def attest_subagent_transcript(transcript_path: str, target_text: str) -> List[str]:
    errors: List[str] = []
    if transcript_path.startswith("file://"):
        transcript_path = transcript_path[7:]
    transcript_path = os.path.realpath(os.path.expanduser(transcript_path))
    if not os.path.isfile(transcript_path):
        return [f"Transcript file not found: {transcript_path}"]

    if transcript_path.endswith("transcript.jsonl"):
        sibling_full = os.path.join(os.path.dirname(transcript_path), "transcript_full.jsonl")
        if os.path.isfile(sibling_full):
            transcript_path = sibling_full

    executed_commands: List[Tuple[str, int]] = []
    file_reads: Dict[str, List[Dict[str, object]]] = {}
    pending_tool_calls: List[Tuple[str, Dict[str, object]]] = []
    all_generic_tool_outputs: List[str] = []

    with open(transcript_path, "r", encoding="utf-8", errors="replace") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except Exception:
                continue

            rtype = rec.get("type")
            if rtype == "PLANNER_RESPONSE":
                for tc in rec.get("tool_calls", []) or []:
                    raw_tname = str(
                        tc.get("name") or (tc.get("function") or {}).get("name") or ""
                    )
                    tname = raw_tname.replace("default_api:", "")
                    targs = (
                        tc.get("args")
                        or tc.get("arguments")
                        or (tc.get("function") or {}).get("arguments")
                        or {}
                    )
                    if isinstance(targs, str):
                        try:
                            targs = json.loads(targs)
                        except Exception:
                            targs = {}
                    pending_tool_calls.append((tname, targs))
            elif rtype == "assistant" and isinstance(rec.get("message"), dict):
                # Client-agnostic support for Claude Code JSONL transcripts
                for blk in rec["message"].get("content", []) or []:
                    if isinstance(blk, dict) and blk.get("type") == "tool_use":
                        raw_tname = str(blk.get("name") or "")
                        tname = "run_command" if raw_tname.lower() == "bash" else ("read_file" if raw_tname.lower() == "read" else raw_tname)
                        targs = blk.get("input") if isinstance(blk.get("input"), dict) else {}
                        pending_tool_calls.append((tname, targs))
            elif rtype in ("GENERIC", "user"):
                if rtype == "user" and isinstance(rec.get("message"), dict):
                    cnt_blocks = rec["message"].get("content") or []
                    if isinstance(cnt_blocks, list):
                        content = "\n".join(
                            str(b.get("content") or "")
                            for b in cnt_blocks
                            if isinstance(b, dict) and b.get("type") == "tool_result"
                        )
                    else:
                        content = str(cnt_blocks or "")
                else:
                    content = str(rec.get("content") or "")
                stripped_cnt = content.lstrip()
                is_system_injection = (
                    stripped_cnt.startswith("The following is a <SYSTEM_MESSAGE>")
                    or stripped_cnt.startswith("<SYSTEM_MESSAGE>")
                )
                if not is_system_injection:
                    all_generic_tool_outputs.append(content)
                if pending_tool_calls and not is_system_injection:
                    tname, targs = pending_tool_calls.pop(0)
                    if tname == "run_command":
                        cmd = str(targs.get("CommandLine") or targs.get("command") or "").strip('"\' ')
                        rc = -1
                        m_rc = re.search(r"(?:Command exited with code|Exit [Cc]ode:?)\s*(-?\d+)", content)
                        if m_rc:
                            rc = int(m_rc.group(1))
                        elif "Completed At:" in content and not re.search(
                            r"(?:^Error:|timed out|still running in the background)",
                            content,
                            re.IGNORECASE | re.MULTILINE,
                        ):
                            rc = 0
                        executed_commands.append((cmd, rc))
                    elif tname in ("view_file", "read_file"):
                        raw_p = str(
                            targs.get("AbsolutePath")
                            or targs.get("Path")
                            or targs.get("FilePath")
                            or targs.get("file_path")
                            or ""
                        ).strip('"\' ')
                        if raw_p:
                            p = os.path.realpath(os.path.expanduser(raw_p))
                            total_lines = None
                            shown_start = 1
                            shown_end = None

                            m_tot = re.search(r"Total Lines:\s*(\d+)", content)
                            if m_tot:
                                total_lines = int(m_tot.group(1))
                            m_show1 = re.search(r"Showing lines\s*(\d+)\s*to\s*(\d+)", content, re.I)
                            if m_show1:
                                shown_start = int(m_show1.group(1))
                                shown_end = int(m_show1.group(2))

                            m_show2 = re.search(r"Showing lines\s*(\d+)-(\d+)\s*of\s*(\d+)", content, re.I)
                            if m_show2:
                                shown_start = int(m_show2.group(1))
                                shown_end = int(m_show2.group(2))
                                total_lines = int(m_show2.group(3))

                            explicit_end = targs.get("EndLine") is not None
                            explicit_start = targs.get("StartLine") is not None
                            has_offset = bool(targs.get("ContentOffset") or targs.get("ByteOffset"))

                            is_truncated = False
                            if ("Content truncated:" in content) or ("Partial read" in content) or ("46080-byte limit" in content):
                                is_truncated = True
                            elif not explicit_end and total_lines is not None and shown_end is not None and shown_end < total_lines:
                                is_truncated = True

                            if p not in file_reads:
                                file_reads[p] = []
                            file_reads[p].append({
                                "is_truncated": is_truncated,
                                "has_offset": has_offset,
                                "shown_end": shown_end,
                                "total_lines": total_lines,
                                "start_line": int(targs["StartLine"]) if explicit_start else 1,
                            })

    unpaged_truncated = []
    for p, reads in file_reads.items():
        for i, r in enumerate(reads):
            if r["is_truncated"]:
                resolved = False
                cur_end = r.get("shown_end")
                for j in range(i + 1, len(reads)):
                    sub = reads[j]
                    if sub.get("has_offset"):
                        resolved = True
                        break
                    if cur_end is not None:
                        if sub.get("start_line", 1) >= cur_end or (sub.get("shown_end") and sub["shown_end"] > cur_end):
                            resolved = True
                            break
                    elif sub.get("start_line", 1) > 1:
                        resolved = True
                        break
                if not resolved:
                    unpaged_truncated.append(p)
                    break

    if unpaged_truncated:
        errors.append(
            f"UNATTESTED_TRUNCATED_READ: Transcript contains unpaged truncated file reads on: {', '.join(sorted(unpaged_truncated))}"
        )

    for m_oracles in re.finditer(r"Oracles:\s*([^\n|]+)", target_text):
        raw_oracles = m_oracles.group(1).strip()
        if raw_oracles.lower().strip("` ") not in ("n/a", "none", "nil", "-", ""):
            for chunk in raw_oracles.split(","):
                chunk = chunk.strip()
                if "->" in chunk:
                    claimed_cmd = chunk.split("->")[0].strip().strip('"\' ')
                    matching = [rc for c, rc in executed_commands if claimed_cmd in c or c in claimed_cmd]
                    if not matching:
                        errors.append(f"UNATTESTED_ORACLE_COMMAND: '{claimed_cmd}' not found in transcript")
                    elif all(rc != 0 for rc in matching):
                        errors.append(f"FAILED_ORACLE_COMMAND: Claimed oracle command '{claimed_cmd}' exited with non-zero exit code")

    for m_cli in re.finditer(r"\[CLI TELEMETRY\][^\n]*?\(([^)\n]+->[^)\n]+)\)", target_text):
        chunk = m_cli.group(1).strip()
        claimed_cmd = chunk.split("->")[0].strip().strip('"\' ')
        matching = [rc for c, rc in executed_commands if claimed_cmd in c or c in claimed_cmd]
        if not matching:
            errors.append(f"UNATTESTED_ORACLE_COMMAND: '{claimed_cmd}' not found in transcript")
        elif all(rc != 0 for rc in matching):
            errors.append(f"FAILED_ORACLE_COMMAND: Claimed oracle command '{claimed_cmd}' exited with non-zero exit code")

    all_tool_content_blob = "\n".join(all_generic_tool_outputs)
    packet_re = re.compile(r"===\s*Subagent Evidence Packet.*?===(.*?)(?=(?:===\s*Subagent Evidence Packet|\Z))", re.DOTALL | re.IGNORECASE)
    for pm in packet_re.finditer(target_text):
        pkt_text = pm.group(1)
        for vrf_m in re.finditer(r"\bVRF-[0-9a-f]{12}\b", pkt_text, re.IGNORECASE):
            vrf_tok = vrf_m.group(0).upper()
            if vrf_tok not in all_tool_content_blob.upper():
                errors.append(f"UNATTESTED_RECEIPT_TOKEN: Claimed receipt '{vrf_tok}' was not found in any transcript tool output")
        for sha_m in re.finditer(r"(?:inventory_sha256|inventory_sha|receipt):\s*([0-9a-f]{64})\b", pkt_text, re.IGNORECASE):
            sha_tok = sha_m.group(1).lower()
            if sha_tok not in all_tool_content_blob.lower():
                errors.append(f"UNATTESTED_RECEIPT_TOKEN: Claimed inventory receipt '{sha_tok}' was not found in any transcript tool output")

    return errors


def audit_target(
    target_text: str,
    idx: SourceIndex,
    target_dir: Optional[str] = None,
    default_entity: Optional[str] = None,
) -> Dict[str, object]:
    is_standard_doc = bool(
        re.search(
            r"^type:\s*(?:standard|command-reference|architecture-diagram|project-companion)\b",
            target_text[:500],
            re.IGNORECASE | re.MULTILINE,
        )
    )
    cleaned_lines = strip_non_claim_regions(target_text)
    supported: List[Dict[str, object]] = []
    unbacked: List[Dict[str, object]] = []
    tbd_offenders: List[Dict[str, object]] = []
    derived_num_units: Set[Tuple[float, str]] = set()
    derived_numbers: Set[float] = set()

    # 1. Parse Subagent Evidence Packets for Missing Anchors & Absent Sources
    packet_pattern = re.compile(
        r"===\s*Subagent Evidence Packet.*?===(.*?)(?=(?:===\s*Subagent Evidence Packet|\Z))",
        re.DOTALL | re.IGNORECASE,
    )
    for pm in packet_pattern.finditer(target_text):
        pkt_text = pm.group(1)
        pkt_offset = pm.start(1)
        bullet_re = re.compile(
            r"^[ \t]*-[ \t]+(\[(?:VERIFIED FACT|CAD TELEMETRY|CLI TELEMETRY|SPATIAL / DFM ADVISORY|TBD|CONFLICT)[^\]]*\].*?)(?=(?:^[ \t]*-[ \t]+\[|\Z))",
            re.MULTILINE | re.DOTALL,
        )
        for bm in bullet_re.finditer(pkt_text):
            b_chunk = bm.group(1)
            b_line = target_text[: pkt_offset + bm.start()].count("\n") + 1
            first_line = b_chunk.splitlines()[0].strip()

            is_fact_or_cad = bool(re.match(r"^\[(?:VERIFIED FACT|CAD TELEMETRY)\]", first_line, re.IGNORECASE))
            if is_fact_or_cad:
                has_source = bool(re.search(r"(?:Source:\s*|[\(\[][A-Za-z0-9_./-]+#(?:L)?\d+)", b_chunk, re.IGNORECASE))
                has_anchor = bool(re.search(r"Anchor:\s*\n\s*```", b_chunk, re.IGNORECASE))
                if not (has_source and has_anchor):
                    unbacked.append({
                        "line": b_line,
                        "type": "MISSING_EVIDENCE_ANCHOR",
                        "claim": f"{first_line} inside Evidence Packet missing Source: and Anchor: hunk",
                    })

            if re.match(r"^\[TBD", first_line, re.IGNORECASE):
                m_abs = re.search(r"Source:\s*([A-Za-z0-9_./-]+)\s*(?:\(ABSENT\)|\[ABSENT\])", b_chunk, re.IGNORECASE)
                if m_abs:
                    abs_path = m_abs.group(1)
                    info = idx.get_file_info(abs_path)
                    if not info:
                        unbacked.append({
                            "line": b_line,
                            "type": "ANCHOR_SOURCE_NOT_FOUND",
                            "claim": f"Cited absent source file `{abs_path}` not found in --sources",
                        })
                    else:
                        m_anc_abs = re.search(r"Anchor:\s*(?:`?\[ABSENT_IN_SOURCE\]`?|ABSENT_IN_SOURCE)", b_chunk, re.IGNORECASE)
                        if m_anc_abs:
                            supported.append({
                                "line": b_line,
                                "type": "VERIFIED_ABSENT_SOURCE",
                                "claim": f"`{abs_path}` (ABSENT)",
                            })
                        else:
                            unbacked.append({
                                "line": b_line,
                                "type": "MISSING_EVIDENCE_ANCHOR",
                                "claim": f"Missing Anchor: [ABSENT_IN_SOURCE] for absent source `{abs_path}`",
                            })

    # 2. Anchor Hunk Verification pass & Local Claim-to-Anchor Token Binding
    anchor_re = re.compile(
        r"(?:(?:Source:\s*|[\(\[])(?P<path>[A-Za-z0-9_./-]+(?:\.[A-Za-z0-9]+)?)(?:#L|:)(?P<start>\d+)(?:[-–—](?:L)?(?P<end>\d+))?[\)\]]?)"
        r"[^\n]*\n\s*Anchor:\s*\n\s*```[^\n]*\n(?P<hunk>.*?\n)\s*```",
        re.DOTALL | re.IGNORECASE,
    )
    for am in anchor_re.finditer(target_text):
        anc_line_no = target_text[: am.start()].count("\n") + 1
        c_path = am.group("path")
        c_st = int(am.group("start"))
        c_en = int(am.group("end")) if am.group("end") else c_st
        c_hunk = am.group("hunk")
        info = idx.get_file_info(c_path)
        if not info:
            unbacked.append({"line": anc_line_no, "type": "ANCHOR_SOURCE_NOT_FOUND", "claim": f"Cited anchor file `{c_path}` not found in --sources"})
            continue
        if c_st > c_en:
            unbacked.append({"line": anc_line_no, "type": "INVERTED_LINE_RANGE", "claim": f"`{c_path}#L{c_st}-L{c_en}` (start {c_st} > end {c_en})"})
            continue
        if c_st < 1 or c_en > info.line_count:
            unbacked.append({"line": anc_line_no, "type": "ANCHOR_LINE_OUT_OF_BOUNDS", "claim": f"`{c_path}#L{c_st}-L{c_en}` exceeds file length ({info.line_count} lines)"})
            continue
        if info.frontmatter_range and (
            (c_st >= info.frontmatter_range[0] and c_st <= info.frontmatter_range[1])
            or (c_en >= info.frontmatter_range[0] and c_en <= info.frontmatter_range[1])
        ):
            unbacked.append({"line": anc_line_no, "type": "FRONTMATTER_CITATION_BLOCKED", "claim": f"Anchor `{c_path}#L{c_st}-L{c_en}` cites YAML frontmatter"})
            continue
        in_quarantine = False
        for q_st, q_en, q_title in info.quarantined_ranges:
            if not (c_en < q_st or c_st > q_en):
                unbacked.append({"line": anc_line_no, "type": "QUARANTINED_ZONE_CITATION", "claim": f"Anchor `{c_path}#L{c_st}-L{c_en}` cites quarantined zone '{q_title}'"})
                in_quarantine = True
                break
        if in_quarantine:
            continue
        warn_err = info.check_warning_context(c_st, c_en, c_hunk + " " + target_text[am.start():am.end()])
        if warn_err:
            unbacked.append({"line": anc_line_no, "type": "WARNING_CONTEXT_CITATION", "claim": f"Anchor `{c_path}#L{c_st}-L{c_en}`: {warn_err}"})
            continue
        disk_slice = info.lines[c_st - 1 : c_en]
        norm_disk = "\n".join(re.sub(r"\s+", " ", l).strip() for l in disk_slice if l.strip())
        norm_hunk = "\n".join(re.sub(r"\s+", " ", l).strip() for l in c_hunk.splitlines() if l.strip())
        if norm_disk != norm_hunk:
            unbacked.append({"line": anc_line_no, "type": "DOCTORED_ANCHOR_MISMATCH", "claim": f"Anchor hunk does not match actual disk slice in `{c_path}#L{c_st}-L{c_en}`"})
        else:
            preceding_text = target_text[: am.start()]
            pre_lines = preceding_text.splitlines()
            claim_lines = []
            for l in reversed(pre_lines):
                l_str = l.strip()
                if not l_str:
                    if claim_lines:
                        break
                    continue
                claim_lines.append(l_str)
                if l_str.startswith("- ") or l_str.startswith("* ") or re.match(r"^\d+\.", l_str):
                    break
            claim_lines.reverse()
            claim_text = " ".join(claim_lines)

            claim_fasteners = [m.group(1) for m in METRIC_FASTENER_RE.finditer(claim_text)]
            claim_designators = []
            for m in DESIGNATOR_RE.finditer(claim_text):
                tok = m.group(1)
                if len(tok) >= 2 and tok.upper() not in ("OD", "ID", "PTFE", "CAD", "ABS", "ASA", "PC", "TPU"):
                    claim_designators.append(tok)
            claim_num_units = []
            for m in SINGLE_NUM_UNIT_RE.finditer(claim_text):
                v = parse_num(m.group(1))
                cu = canonicalize_unit(m.group(3), m.group(2))
                if cu:
                    claim_num_units.append((round(v, 6), cu, m.group(0).strip()))
            claim_backticks = []
            for m in BACKTICK_RE.finditer(claim_text):
                lit = m.group(1).strip()
                if (
                    not lit
                    or "#L" in lit
                    or re.search(r"\.[a-zA-Z0-9]{1,5}$", lit)
                    or lit.startswith("[TBD")
                    or lit.startswith("http")
                    or not re.search(r"[A-Za-z0-9]", lit)
                ):
                    continue
                claim_backticks.append(lit)

            disk_slice_text = " ".join(disk_slice) + " " + os.path.basename(c_path)
            disk_slice_low = disk_slice_text.lower()
            unbound_tokens = []

            for f in claim_fasteners:
                nf = normalize_fastener(f)
                if nf not in disk_slice_low.replace("×", "x") and f.lower() not in disk_slice_low:
                    unbound_tokens.append(f)

            for d in claim_designators:
                nd = normalize_designator(d)
                pat_d = rf"(?<![a-z0-9]){re.escape(nd)}(?![a-z0-9])"
                if not re.search(pat_d, disk_slice_low):
                    unbound_tokens.append(d)

            for v, cu, orig_str in claim_num_units:
                num_pat = rf"(?<![a-z0-9]){re.escape(f'{v:g}')}(?![a-z0-9])"
                found_unit = False
                if orig_str.lower() in disk_slice_low:
                    found_unit = True
                elif re.search(num_pat, disk_slice_text):
                    u_pats = [re.escape(cu)]
                    for u_raw, u_can in UNIT_ALIASES.items():
                        if u_can == cu:
                            u_pats.append(re.escape(u_raw))
                    unit_rx = rf"(?:^|[^a-z0-9])(?:{'|'.join(set(u_pats))})(?:$|[^a-z0-9])"
                    if re.search(unit_rx, disk_slice_low):
                        found_unit = True
                if not found_unit:
                    unbound_tokens.append(orig_str)

            for btok in claim_backticks:
                btok_low = btok.lower().strip("`'\"")
                pat_b = rf"(?<![a-z0-9_]){re.escape(btok_low)}(?![a-z0-9_])"
                if not re.search(pat_b, disk_slice_low):
                    unbound_tokens.append(f"`{btok}`")

            if unbound_tokens:
                unbacked.append({
                    "line": anc_line_no,
                    "type": "ANCHOR_CLAIM_UNBOUND",
                    "claim": f"Token(s) {', '.join(unbound_tokens)} claimed in bullet not found in disk slice `{c_path}#L{c_st}-L{c_en}`",
                })
            else:
                supported.append({"line": anc_line_no, "type": "VERIFIED_ANCHOR_HUNK", "claim": f"`{c_path}#L{c_st}-L{c_en}`"})

    current_heading_entities: Optional[Set[str]] = None
    in_evidence_packet = False
    in_theory_zone = False
    is_study_brief = bool(
        re.search(
            r"^(?:type:\s*study-brief|status:\s*['\"]?(?:UNPROMOTED_STUDY_BRIEF|PROMOTED_ENGINEERING_BRIEF)['\"]?)\b",
            target_text[:600],
            re.IGNORECASE | re.MULTILINE,
        )
    )
    idx_known_entities: Set[str] = (
        set(idx.entity_num_units.keys())
        | set(idx.entity_fasteners.keys())
        | set(idx.entity_designators.keys())
        | set(idx.entity_raw_chunks.keys())
    ) - {"*"}
    default_active_entities: Optional[Set[str]] = None
    ambiguous_umbrella_projects: Optional[Set[str]] = None
    raw_def_ent = (default_entity or "").strip().strip("'\"")
    fm_proj_raw = ""
    fm_ent_raw = ""
    if target_text.startswith("---"):
        fm_m = re.match(r"\A---\s*\n(.*?)\n---", target_text, flags=re.DOTALL)
        if fm_m:
            fm_p = re.search(r"^(?:project|parent_note)\s*:\s*(.+)$", fm_m.group(1), flags=re.MULTILINE | re.I)
            fm_e = re.search(r"^entity\s*:\s*(.+)$", fm_m.group(1), flags=re.MULTILINE | re.I)
            if fm_p:
                fm_proj_raw = fm_p.group(1).strip().strip("'\"")
            if fm_e:
                fm_ent_raw = fm_e.group(1).strip().strip("'\"")

    def _resolve_candidate_entities(cand_raw: str) -> Optional[Set[str]]:
        if not cand_raw:
            return None
        det_c = detect_entities_in_text(cand_raw, idx_known_entities, extra_aliases=idx.dynamic_aliases)
        if det_c:
            return det_c
        norm_c = cand_raw.lower().replace("-", "_").replace(" ", "_")
        canon_c = (
            idx.dynamic_aliases.get(norm_c)
            or idx.dynamic_aliases.get(norm_c.replace("_", ""))
            or ENTITY_ALIASES.get(norm_c, _canonicalize_entity_token(norm_c))
        )
        if canon_c in idx_known_entities:
            return {canon_c}
        return None

    for cand in (raw_def_ent, fm_proj_raw, fm_ent_raw):
        resolved_def = _resolve_candidate_entities(cand)
        if resolved_def:
            default_active_entities = resolved_def
            break
    if default_active_entities is None:
        for cand in (raw_def_ent, fm_ent_raw):
            if not cand:
                continue
            norm_u = cand.lower().replace("-", "_").replace(" ", "_")
            umb = idx.ambiguous_umbrellas.get(norm_u) or idx.ambiguous_umbrellas.get(norm_u.replace("_", ""))
            if umb:
                ambiguous_umbrella_projects = umb
                raw_def_ent = cand
                break

    for line_no, ln, tbds in cleaned_lines:
        line_sup_start = len(supported)
        for t in tbds:
            tbd_offenders.append({"line": line_no, "marker": t})
        if not ln.strip():
            continue

        if is_study_brief:
            if re.search(r"<!--\s*FIRST-PRINCIPLES-THEORY:START\s*-->", ln, re.IGNORECASE):
                in_theory_zone = True
                continue
            if re.search(r"<!--\s*FIRST-PRINCIPLES-THEORY:END\s*-->", ln, re.IGNORECASE):
                in_theory_zone = False
                continue

        if "=== Subagent Evidence Packet" in ln:
            in_evidence_packet = True
        elif ln.strip().startswith("==="):
            in_evidence_packet = False

        hm = HEADING_LEVEL_RE.match(ln.strip())
        if hm:
            h_ents = detect_entities_in_text(ln, idx_known_entities, extra_aliases=idx.dynamic_aliases)
            if h_ents:
                current_heading_entities = h_ents
            elif len(hm.group(1)) <= 2:
                current_heading_entities = None

        line_entities = detect_entities_in_text(ln, idx_known_entities, extra_aliases=idx.dynamic_aliases)
        if is_standard_doc and not in_evidence_packet:
            active_entities = None
        else:
            if line_entities:
                active_entities = line_entities
            elif current_heading_entities:
                active_entities = current_heading_entities
            elif default_active_entities:
                active_entities = default_active_entities
            else:
                active_entities = None
        active_ent = sorted(active_entities)[0] if active_entities else None

        # Polarity / Safety Inversion Check
        has_loctite = bool(re.search(r"\b(loctite(?:\s+\d+[a-z]*)?|threadlocker)\b", ln, re.I))
        has_incompatible_plastic = bool(re.search(r"\b(abs|asa|pc|polycarbonate|acrylic|pmma|printed\s+(?:parts?|plastic|components?|threads?))\b", ln, re.I))
        has_red_threadlocker = bool(re.search(r"\b(red\s+threadlocker|loctite\s*(?:262|271|272|277|290))\b", ln, re.I))
        has_plastic = bool(re.search(r"\b(abs|asa|pc|polycarbonate|printed\s+plastic)\b", ln, re.I))
        has_metal_torque = bool(re.search(r"\b(torque|tighten)\b", ln, re.I)) and bool(re.search(r"\b(metal\s+specs?|1\.[0-5]\s*nm|1\.2\s*nm|3\.[0-9]\s*nm|4\.[0-5]\s*nm)\b", ln, re.I))
        has_negation = bool(
            re.search(
                r"\b(never|do not|don't|not|avoid|incompatible|prohibit\w*|forbid\w*|disallow\w*|block\w*|prevent\w*|reject\w*|restrict\w*|precaution\w*|safeguard\w*|ban(?:s|ned|ning)?|isolat\w*|hazard\w*|danger\w*|caution|warning|keep\s+away|destroy\w*|fail\w*|crack\w*|attack\w*|damag\w*|craz\w*|delaminat\w*)\b",
                ln,
                re.I,
            )
        )
        if has_loctite and has_incompatible_plastic and not has_negation:
            unbacked.append({
                "line": line_no,
                "type": "SAFETY_POLARITY_INVERSION",
                "claim": f"Prohibited application of anaerobic threadlocker onto printed polymer ({ln.strip()})",
            })
        elif has_red_threadlocker and not has_negation:
            unbacked.append({
                "line": line_no,
                "type": "SAFETY_POLARITY_INVERSION",
                "claim": f"Prohibited application of high-strength / red threadlocker ({ln.strip()})",
            })
        elif has_plastic and has_metal_torque and not has_negation:
            unbacked.append({
                "line": line_no,
                "type": "SAFETY_POLARITY_INVERSION",
                "claim": f"Prohibited torquing fasteners into printed polymer to metal specs ({ln.strip()})",
            })

        # 0. Deterministic Arithmetic Calculations (`[CALC: 120W / 24V = 5.0A]`)
        calc_spans: List[Tuple[int, int]] = []
        for m in CALC_MARKER_RE.finditer(ln):
            calc_spans.append(m.span())
            raw_calc = m.group(1).strip()
            if (not re.search(r"\d", raw_calc) and (raw_calc in ("...", "…") or "<" in raw_calc or "…" in raw_calc or "..." in raw_calc)) or (
                is_standard_doc and (raw_calc in ("...", "…") or "<" in raw_calc or "…" in raw_calc or "..." in raw_calc)
            ):
                continue
            ok, tag, d_pair, d_num = verify_calc_marker(
                raw_calc, idx, require_source_operands=not in_theory_zone
            )
            if ok and not in_theory_zone:
                if d_pair is not None:
                    derived_num_units.add(d_pair)
                if d_num is not None:
                    derived_numbers.add(d_num)
            rec = {"line": line_no, "type": tag, "claim": m.group(0)}
            (supported if ok else unbacked).append(rec)
        if calc_spans:
            chars = list(ln)
            for st, en in calc_spans:
                for i in range(st, en):
                    chars[i] = " "
            ln = "".join(chars)

        if in_theory_zone:
            continue

        # 1. Backticked Identifiers (`*.stl`, `*.cfg`, `PF7`, `D33:I34`, etc.)
        id_backtick_spans: List[Tuple[int, int]] = []
        unquoted_chars = list(ln)
        for m in BACKTICK_RE.finditer(ln):
            lit = m.group(1).strip()
            if (
                not lit
                or lit.startswith("[TBD")
                or re.match(
                    r"^\[(?:VERIFIED FACT|CAD TELEMETRY|CLI TELEMETRY|CONTEXT ANALOGY|SPATIAL / DFM ADVISORY|CONFLICT)\]$",
                    lit,
                    re.IGNORECASE,
                )
                or not re.search(r"[A-Za-z0-9]", lit)
            ):
                id_backtick_spans.append(m.span())
                continue
            if (lit.startswith('"') and lit.endswith('"')) or (lit.startswith("'") and lit.endswith("'")):
                id_backtick_spans.append(m.span())
                continue

            # Backticked bare counts (`578x`, `437`, `73,893`)
            m_cnt = re.match(r"^([+-]?\d+(?:,\d{3})*(?:\.\d+)?)x?$", lit, re.IGNORECASE)
            if m_cnt:
                id_backtick_spans.append(m.span())
                cval = round(parse_num(m_cnt.group(1)), 6)
                ok_cnt = (cval in idx.numbers_all) or (cval in derived_numbers)
                rec_cnt = {"line": line_no, "type": "NUMERIC_COUNT", "claim": f"`{lit}`"}
                (supported if ok_cnt else unbacked).append(rec_cnt)
                continue

            # Backticked bare numeric ranges (`13–26`, `3–17`, `1–2`)
            m_brng = re.match(
                r"^([+-]?\d+(?:,\d{3})*(?:\.\d+)?)\s*(?:to|-|–|—)\s*([+-]?\d+(?:,\d{3})*(?:\.\d+)?)$",
                lit,
                re.IGNORECASE,
            )
            if m_brng:
                id_backtick_spans.append(m.span())
                v1 = round(parse_num(m_brng.group(1)), 6)
                v2 = round(parse_num(m_brng.group(2)), 6)
                ok_br = ((v1 in idx.numbers_all) or (v1 in derived_numbers)) and (
                    (v2 in idx.numbers_all) or (v2 in derived_numbers)
                )
                rec_br = {"line": line_no, "type": "NUMERIC_RANGE", "claim": f"`{lit}`"}
                (supported if ok_br else unbacked).append(rec_br)
                continue

            # Backticked file/line provenance citations (`README.md:10-14`, `BOM.md#L46`, `System_Control.cfg#L11-L16`)
            m_prov = re.match(
                r"^(?:HEAD:)?([A-Za-z0-9_./-]+(?:\.[A-Za-z0-9]+|/)|(?:[A-Za-z0-9_./-]+/)?(?:LICENSE|CNAME))(?::(\d[\d,-]*)|#L(\d[\d,L-]*))?$",
                lit,
            )
            if m_prov:
                cited_rel = m_prov.group(1)
                line_spec = m_prov.group(2) or m_prov.group(3) or ""
                if cited_rel.endswith("/"):
                    ok_dir = any(
                        os.path.isdir(os.path.join(sd, cited_rel.rstrip("/")))
                        or os.path.isdir(os.path.join(os.path.dirname(sd), cited_rel.rstrip("/")))
                        for sd in idx.source_dirs
                    ) or idx.has_backtick_literal(lit)[0]
                    if ok_dir:
                        id_backtick_spans.append(m.span())
                        supported.append({"line": line_no, "type": "PROVENANCE_DIR", "claim": f"`{lit}`"})
                        continue
                elif ":" in lit or "#L" in lit or lit.startswith("HEAD:") or "/" in cited_rel or cited_rel in ("LICENSE", "CNAME"):
                    bname_low = os.path.basename(cited_rel).lower()
                    ok_cit = (
                        (bname_low in idx.source_basenames)
                        or any(
                            os.path.exists(os.path.join(sd, cited_rel))
                            or os.path.exists(os.path.join(os.path.dirname(sd), cited_rel))
                            for sd in idx.source_dirs
                        )
                        or idx.has_backtick_literal(lit, entities=active_entities)[0]
                    )
                    if ok_cit and line_spec:
                        m_rng = re.match(r"^L?(\d+)(?:[-–—]L?(\d+))?$", line_spec, re.IGNORECASE)
                        if m_rng:
                            st_ln = int(m_rng.group(1))
                            en_ln = int(m_rng.group(2)) if m_rng.group(2) else st_ln
                            if st_ln > en_ln:
                                ok_cit = False
                                id_backtick_spans.append(m.span())
                                unbacked.append({"line": line_no, "type": "INVERTED_LINE_RANGE", "claim": f"`{lit}` (start {st_ln} > end {en_ln})"})
                                continue
                        else:
                            cited_lns = [int(n) for n in re.findall(r"\d+", line_spec)]
                            st_ln = min(cited_lns) if cited_lns else 1
                            en_ln = max(cited_lns) if cited_lns else 1

                        info = idx.get_file_info(cited_rel) or idx.get_file_info(bname_low)
                        if not info:
                            ok_cit, _ = idx.has_backtick_literal(lit, entities=active_entities)
                        else:
                            if st_ln < 1 or en_ln > info.line_count:
                                ok_cit = False
                            elif info.frontmatter_range and (
                                (st_ln >= info.frontmatter_range[0] and st_ln <= info.frontmatter_range[1])
                                or (en_ln >= info.frontmatter_range[0] and en_ln <= info.frontmatter_range[1])
                            ):
                                ok_cit = False
                                id_backtick_spans.append(m.span())
                                unbacked.append({
                                    "line": line_no,
                                    "type": "FRONTMATTER_CITATION_BLOCKED",
                                    "claim": f"`{lit}` (lines {st_ln}..{en_ln} fall within YAML frontmatter {info.frontmatter_range[0]}..{info.frontmatter_range[1]})",
                                })
                                continue
                            else:
                                for q_st, q_en, q_title in info.quarantined_ranges:
                                    if not (en_ln < q_st or st_ln > q_en):
                                        ok_cit = False
                                        id_backtick_spans.append(m.span())
                                        unbacked.append({
                                            "line": line_no,
                                            "type": "QUARANTINED_ZONE_CITATION",
                                            "claim": f"`{lit}` (lines {st_ln}..{en_ln} fall within quarantined ledger '{q_title}')",
                                        })
                                        break
                                if not ok_cit:
                                    continue
                                warn_err = info.check_warning_context(st_ln, en_ln, ln)
                                if warn_err:
                                    ok_cit = False
                                    id_backtick_spans.append(m.span())
                                    unbacked.append({
                                        "line": line_no,
                                        "type": "WARNING_CONTEXT_CITATION",
                                        "claim": f"`{lit}`: {warn_err}",
                                    })
                                    continue

                    if ok_cit:
                        id_backtick_spans.append(m.span())
                        supported.append({"line": line_no, "type": "PROVENANCE_REF", "claim": f"`{lit}`"})
                        continue
                    else:
                        id_backtick_spans.append(m.span())
                        unbacked.append({"line": line_no, "type": "UNBACKED_PROVENANCE_REF", "claim": f"`{lit}`"})
                        continue

            # Backticked companion media/diagram filenames (`Diagram.png`, `Topology.svg`) sitting alongside --target
            if (
                target_dir
                and re.match(r"^[A-Za-z0-9_.-]+\.(?:png|svg|jpg|jpeg|webp|pdf)$", lit, re.IGNORECASE)
                and os.path.isfile(os.path.join(target_dir, lit))
            ):
                id_backtick_spans.append(m.span())
                supported.append({"line": line_no, "type": "COMPANION_ASSET_REF", "claim": f"`{lit}`"})
                continue

            # Backticked local filesystem paths (`/workspace/...`)
            if lit.startswith("/") and lit.count("/") >= 2 and " " not in lit:
                id_backtick_spans.append(m.span())
                ok_fp = os.path.exists(lit.rstrip("/")) or idx.has_backtick_literal(lit)[0]
                rec_fp = {"line": line_no, "type": "FILESYSTEM_PATH", "claim": f"`{lit}`"}
                (supported if ok_fp else unbacked).append(rec_fp)
                continue

            if re.match(r"^[<>≤≥~≈±Øø⌀]?\s*\d", lit) and (SINGLE_NUM_UNIT_RE.search(lit) or RANGE_NUM_UNIT_RE.search(lit)):
                unquoted_chars[m.start()] = " "
                unquoted_chars[m.end() - 1] = " "
                continue

            id_backtick_spans.append(m.span())
            ok, err_code = idx.has_backtick_literal(lit, entities=active_entities)
            rec = {"line": line_no, "type": err_code or "LITERAL_ID", "claim": f"`{lit}`"}
            (supported if ok else unbacked).append(rec)

        for st, en in id_backtick_spans:
            for i in range(st, en):
                unquoted_chars[i] = " "
        prose_ln = "".join(unquoted_chars)

        # 2. Metric Fasteners (M3x5x4mm, M3x8mm, M5x12)
        fastener_spans: List[Tuple[int, int]] = []
        for m in METRIC_FASTENER_RE.finditer(prose_ln):
            f_tok = m.group(1)
            fastener_spans.append(m.span())
            ok, err_f = idx.has_fastener(f_tok, entities=active_entities)
            rec = {"line": line_no, "type": err_f or "FASTENER_SPEC", "claim": f_tok}
            (supported if ok else unbacked).append(rec)

        if fastener_spans:
            chars = list(prose_ln)
            for st, en in fastener_spans:
                for i in range(st, en):
                    chars[i] = " "
            prose_ln = "".join(chars)

        # 2b. Underspecified Fastener Callouts in Numbered Assembly Steps
        if re.match(r"^\s*\d+\.\s+", ln) and not tbds:
            for m_uf in UNDERSPECIFIED_STEP_FASTENER_RE.finditer(prose_ln):
                unbacked.append(
                    {
                        "line": line_no,
                        "type": "UNDERSPECIFIED_FASTENER_DODGE",
                        "claim": m_uf.group(0).strip(),
                    }
                )

        # 3. Shore Durometer (95A, 85A, 60D)
        shore_spans: List[Tuple[int, int]] = []
        for m in SHORE_RE.finditer(prose_ln):
            s_tok = m.group(0)
            shore_spans.append(m.span())
            ok = idx.has_shore(s_tok)
            rec = {"line": line_no, "type": "SHORE_HARDNESS", "claim": s_tok}
            (supported if ok else unbacked).append(rec)
        if shore_spans:
            chars = list(prose_ln)
            for st, en in shore_spans:
                for i in range(st, en):
                    chars[i] = " "
            prose_ln = "".join(chars)

        # 4. Technical Designators (Cat6A, OS2, Loctite 243, 1/8 NPT, TPN##, etc.)
        desig_spans: List[Tuple[int, int]] = []
        for m in DESIGNATOR_RE.finditer(prose_ln):
            d_tok = m.group(1)
            desig_spans.append(m.span())
            ok, err_d = idx.has_designator(d_tok, entities=active_entities)
            rec = {"line": line_no, "type": err_d or "DESIGNATOR", "claim": d_tok}
            (supported if ok else unbacked).append(rec)
        if desig_spans:
            chars = list(prose_ln)
            for st, en in desig_spans:
                for i in range(st, en):
                    chars[i] = " "
            prose_ln = "".join(chars)

        # 5. Numeric Ranges + Units ("50 to 70 grams", "1.0 to 1.5 Nm")
        range_spans: List[Tuple[int, int]] = []
        for m in RANGE_NUM_UNIT_RE.finditer(prose_ln):
            n1, u1, n2, u2 = m.group(1), m.group(2), m.group(3), m.group(4)
            cu2 = canonicalize_unit(u2, " ") or UNIT_ALIASES.get(re.sub(r"\s+", " ", u2.lower().strip()))
            cu1 = (
                canonicalize_unit(u1, " ") or UNIT_ALIASES.get(re.sub(r"\s+", " ", u1.lower().strip()))
            ) if u1 else cu2
            if cu1 and cu2:
                range_spans.append(m.span())
                v1, v2 = parse_num(n1), parse_num(n2)
                ok1 = idx.has_num_unit(v1, cu1, entities=active_entities)[0] or ((round(v1, 6), cu1) in derived_num_units)
                ok2 = idx.has_num_unit(v2, cu2, entities=active_entities)[0] or ((round(v2, 6), cu2) in derived_num_units)
                rec = {"line": line_no, "type": "RANGE_QUANTITY", "claim": m.group(0).strip()}
                (supported if (ok1 and ok2) else unbacked).append(rec)
        if range_spans:
            chars = list(prose_ln)
            for st, en in range_spans:
                for i in range(st, en):
                    chars[i] = " "
            prose_ln = "".join(chars)

        # 6. Spelled-Out Number + Unit ("two-meter", "sixty grams")
        for m in SPELLED_NUM_UNIT_RE.finditer(prose_ln):
            w_str, u_str = m.group(1).lower(), m.group(2)
            cu = canonicalize_unit(u_str, "")
            if cu and w_str in WORD_NUMBERS:
                v_w = WORD_NUMBERS[w_str]
                ok = idx.has_num_unit(v_w, cu, entities=active_entities)[0] or ((round(v_w, 6), cu) in derived_num_units)
                rec = {"line": line_no, "type": "SPELLED_QUANTITY", "claim": m.group(0).strip()}
                (supported if ok else unbacked).append(rec)

        # 6b. Qualified Number + Unit ("100% infill", "4mm internal diameter", "Infill: 40%")
        is_unspecified_stmt = bool(
            re.search(
                r"\b(?:is|are|was|were|remains?)\s+not\s+(?:specified|defined|known|determined|provided)\b|\bnot\s+specified\s+in\b",
                prose_ln,
                re.IGNORECASE,
            )
        )
        qual_spans: List[Tuple[int, int]] = []
        if not is_unspecified_stmt:
            for m in QUALIFIED_NUM_UNIT_RE.finditer(prose_ln):
                n_str, sep, u_str, q_str = m.group(1), m.group(2), m.group(3), m.group(4)
                cu = canonicalize_unit(u_str, sep)
                grp = map_qualifier_group(q_str)
                if cu and grp:
                    qual_spans.append(m.span())
                    ok, err_q = idx.has_qualified_num_unit(parse_num(n_str), cu, grp, entities=active_entities)
                    rec = {"line": line_no, "type": err_q or f"QUALIFIED_QUANTITY({grp.upper()})", "claim": m.group(0).strip()}
                    (supported if ok else unbacked).append(rec)

        if qual_spans:
            chars = list(prose_ln)
            for st, en in qual_spans:
                for i in range(st, en):
                    chars[i] = " "
            prose_ln = "".join(chars)

        rev_spans: List[Tuple[int, int]] = []
        if not is_unspecified_stmt:
            for m in REVERSE_QUALIFIED_RE.finditer(prose_ln):
                q_str, n_str, sep, u_str = m.group(1), m.group(2), m.group(3), m.group(4)
                cu = canonicalize_unit(u_str, sep)
                grp = map_qualifier_group(q_str)
                if cu and grp:
                    rev_spans.append(m.span())
                    ok, err_rq = idx.has_qualified_num_unit(parse_num(n_str), cu, grp, entities=active_entities)
                    rec = {"line": line_no, "type": err_rq or f"QUALIFIED_QUANTITY({grp.upper()})", "claim": m.group(0).strip()}
                    (supported if ok else unbacked).append(rec)

        if rev_spans:
            chars = list(prose_ln)
            for st, en in rev_spans:
                for i in range(st, en):
                    chars[i] = " "
            prose_ln = "".join(chars)

        # 7. Single Number + Unit ("70 kPa", "0.20mm", "250°C", "5,040 FT", "20AWG")
        single_unit_spans: List[Tuple[int, int]] = []
        for m in SINGLE_NUM_UNIT_RE.finditer(prose_ln):
            n_str, sep, u_str = m.group(1), m.group(2), m.group(3)
            cu = canonicalize_unit(u_str, sep)
            if not cu:
                continue
            single_unit_spans.append(m.span())
            val = parse_num(n_str)
            ok, err_u = idx.has_num_unit(val, cu, entities=active_entities)
            if not ok and ((round(val, 6), cu) in derived_num_units):
                ok = True
                err_u = None
            rec = {"line": line_no, "type": err_u or "QUANTITY_UNIT", "claim": m.group(0).strip()}
            (supported if ok else unbacked).append(rec)
        if single_unit_spans:
            chars = list(prose_ln)
            for st, en in single_unit_spans:
                for i in range(st, en):
                    chars[i] = " "
            prose_ln = "".join(chars)

        # 8. Unbackticked Count Phrases & Hyphenated Count Modifiers ("7 Custom Skills", "2,947-post", "11-Gate")
        hyph_spans: List[Tuple[int, int]] = []
        for m in HYPHENATED_COUNT_RE.finditer(prose_ln):
            if COUNT_PREFIX_EXCLUDE_RE.search(prose_ln[: m.start()]):
                continue
            hyph_spans.append(m.span())
            cval = round(parse_num(m.group(1)), 6)
            cnoun = normalize_counted_noun(m.group(2))
            ok_hc, err_hc = idx.has_counted_entity(cval, cnoun, entities=active_entities)
            if not ok_hc and (cval in derived_numbers) and not err_hc:
                ok_hc = True
            rec_hc = {"line": line_no, "type": err_hc or f"COUNTED_MODIFIER({cnoun.upper()})", "claim": m.group(0).strip()}
            (supported if ok_hc else unbacked).append(rec_hc)
        if hyph_spans:
            chars = list(prose_ln)
            for st, en in hyph_spans:
                for i in range(st, en):
                    chars[i] = " "
            prose_ln = "".join(chars)

        for m in COUNTED_NOUN_RE.finditer(prose_ln):
            if COUNT_PREFIX_EXCLUDE_RE.search(prose_ln[: m.start()]):
                continue
            mods = [w.lower() for w in m.group(2).split() if w.strip()]
            if any(w in COUNT_MODIFIER_STOPWORDS for w in mods):
                continue
            cval = round(parse_num(m.group(1)), 6)
            cnoun = normalize_counted_noun(m.group(3))
            ok_cn, err_cn = idx.has_counted_entity(cval, cnoun, entities=active_entities)
            if not ok_cn and (cval in derived_numbers) and not err_cn:
                ok_cn = True
            rec_cn = {
                "line": line_no,
                "type": err_cn or f"COUNTED_ENTITY({cnoun.upper()})",
                "claim": re.sub(r"\s+", " ", m.group(0).strip()),
            }
            (supported if ok_cn else unbacked).append(rec_cn)

        if (
            ambiguous_umbrella_projects
            and active_entities is None
            and not is_standard_doc
            and len(supported) > line_sup_start
        ):
            scoped_claims = [
                rec
                for rec in supported[line_sup_start:]
                if rec["type"] in ("LITERAL_ID", "FASTENER_SPEC", "QUANTITY_UNIT", "RANGE_UNIT")
                or str(rec["type"]).startswith(("QUALIFIED_", "COUNTED_"))
            ]
            if scoped_claims:
                unbacked.append(
                    {
                        "line": line_no,
                        "type": "CROSS_ENTITY_BORROWING",
                        "claim": (
                            f"Ambiguous umbrella entity '{raw_def_ent}' spans multiple indexed projects "
                            f"{sorted(ambiguous_umbrella_projects)}; attribute project explicitly on claim/heading "
                            f"({scoped_claims[0]['claim']})"
                        ),
                    }
                )

    return {
        "vrf_token": idx.vrf_token,
        "sources_checked": len(idx.file_hashes),
        "source_hashes": [{"file": fp, "sha256_10": h} for fp, h in idx.file_hashes],
        "excluded_circular_sources": idx.excluded_circular,
        "excluded_lessons_learned_sources": idx.excluded_lessons,
        "provenance_warning_count": len(idx.provenance_warnings),
        "provenance_warnings": idx.provenance_warnings,
        "supported_count": len(supported),
        "unbacked_count": len(unbacked),
        "tbd_count": len(tbd_offenders),
        "unbacked_claims": unbacked,
        "tbd_offenders": tbd_offenders,
        "supported_claims": supported,
    }


def format_whitelist_summary(idx: SourceIndex) -> Dict[str, object]:
    file_entities = [
        {"file": os.path.basename(fp), "entity": idx.file_infos[os.path.abspath(fp).lower()].entity, "sha256_10": h}
        for fp, h in idx.file_hashes
        if os.path.abspath(fp).lower() in idx.file_infos
    ]
    return {
        "vrf_token": idx.vrf_token,
        "sources_checked": len(idx.file_hashes),
        "source_entities": file_entities,
        "excluded_lessons_learned_sources": idx.excluded_lessons,
        "provenance_warning_count": len(idx.provenance_warnings),
        "provenance_warnings": idx.provenance_warnings,
        "fasteners": sorted(idx.fasteners),
        "designators": sorted(idx.designators)[:150],
        "dimensioned_quantities": [f"{v:g} {u}" for v, u in sorted(idx.num_units)][:150],
        "qualified_quantities": [f"{v:g} {u} [{q}]" for v, u, q in sorted(idx.qualified_num_units)][:100],
        "counted_entities": [f"{v:g} {n}" for v, n in sorted(idx.counted_entities)][:100],
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Deterministic domain-agnostic engineering claim & [TBD] verifier."
    )
    parser.add_argument(
        "--target",
        "--draft",
        dest="target",
        required=False,
        default="",
        help="Draft/output file to verify (or '-' for stdin). Optional when --dump-whitelist is set.",
    )
    parser.add_argument(
        "--sources", nargs="+", required=True, help="Authoritative source files or directories."
    )
    parser.add_argument(
        "--dump-whitelist",
        action="store_true",
        help="Index --sources and print verified pre-draft vocabulary (entities, fasteners, designators, quantities) without auditing a --target.",
    )
    parser.add_argument(
        "--fail-on-tbd",
        action="store_true",
        help="Return exit code 2 if any open [TBD: ...] markers exist.",
    )
    parser.add_argument(
        "--strict-provenance",
        "--require-anchors",
        "--require-git-clean-sources",
        dest="strict_provenance",
        action="store_true",
        help="Return exit code 3 if any --sources file has suspect provenance (dirty Git, unreceipted AI prose, or [TBD]). Also aliased as --require-anchors and --require-git-clean-sources.",
    )
    parser.add_argument(
        "--memory-root",
        default="",
        help="Optional explicit memory root directory (also settable via HOMUNCULUS_MEMORY_ROOT).",
    )
    parser.add_argument(
        "--project-dir",
        default="",
        help="Optional project memory directory (e.g., <memory_root>/Projects/<Project>) for entity-context resolution.",
    )
    parser.add_argument(
        "--entity",
        default="",
        help="Optional explicit entity or project context to enforce against --sources (e.g., Client_Alpha or Actuator_Module).",
    )
    parser.add_argument(
        "--allow-lessons-source",
        action="store_true",
        help="Opt-in override allowing *_Lessons_Learned.md files to be indexed as quantitative sources (auto-excluded by default so failed historical attempts never whitelist false specs).",
    )
    parser.add_argument(
        "--transcript",
        help="Optional subagent transcript.jsonl to attest oracle execution and detect read truncations.",
    )
    parser.add_argument(
        "--json", action="store_true", help="Emit JSON output."
    )
    args = parser.parse_args()
    if args.memory_root:
        os.environ["HOMUNCULUS_MEMORY_ROOT"] = str(Path(args.memory_root.replace("\\", "/")).expanduser().resolve())

    if not args.dump_whitelist and not args.target:
        parser.error("the following arguments are required: --target (unless --dump-whitelist is passed)")

    try:
        target_text = ""
        target_label = "<whitelist>"
        if not args.dump_whitelist:
            if args.target == "-":
                target_text = sys.stdin.read()
                target_label = "<stdin>"
            else:
                if not os.path.isfile(args.target):
                    print(f"[EXTRACTION BLOCKED — ABORTED] Target file not found: {args.target}", file=sys.stderr)
                    return 1
                with open(args.target, "r", encoding="utf-8", errors="replace") as f:
                    target_text = f.read()
                target_label = args.target

        source_files, excluded_circular, excluded_lessons = collect_source_files(
            args.sources,
            args.target if args.target else None,
            allow_lessons_source=bool(args.allow_lessons_source),
        )
        if not source_files:
            print("[EXTRACTION BLOCKED — ABORTED] Zero readable non-circular source files found.", file=sys.stderr)
            return 1
    except Exception as exc:
        print(f"[EXTRACTION BLOCKED — ABORTED] {exc}", file=sys.stderr)
        return 1

    idx = SourceIndex(
        source_files,
        excluded_circular=excluded_circular,
        excluded_lessons=excluded_lessons,
    )

    if args.dump_whitelist:
        wl = format_whitelist_summary(idx)
        if args.json:
            print(json.dumps(wl, indent=2))
        else:
            print(f"=== Pre-Draft Verified Whitelist | Receipt: {wl['vrf_token']} | Sources: {wl['sources_checked']} ===")
            ent_str = ", ".join(f"{e['file']}[entity={e['entity']}]" for e in wl["source_entities"][:12])
            if len(wl["source_entities"]) > 12:
                ent_str += f", +{len(wl['source_entities']) - 12} more"
            print(f"Indexed Sources: {ent_str}")
            if wl["fasteners"]:
                print(f"Fasteners ({len(wl['fasteners'])}): {', '.join(wl['fasteners'])}")
            if wl["designators"]:
                print(f"Designators ({len(wl['designators'])}): {', '.join(wl['designators'])}")
            if wl["qualified_quantities"]:
                print(f"Qualified Quantities ({len(wl['qualified_quantities'])}): {', '.join(wl['qualified_quantities'])}")
            if wl["dimensioned_quantities"]:
                print(f"Dimensioned Quantities ({len(wl['dimensioned_quantities'])}): {', '.join(wl['dimensioned_quantities'])}")
            if wl["counted_entities"]:
                print(f"Counted Entities ({len(wl['counted_entities'])}): {', '.join(wl['counted_entities'])}")
            if wl["provenance_warnings"]:
                print("\n[~] SOURCE PROVENANCE ADVISORIES:")
                for pw in wl["provenance_warnings"]:
                    print(f"  - {pw['file']}: {', '.join(pw['reasons'])}")
        if args.strict_provenance and wl["provenance_warning_count"] > 0:
            return 3
        return 0
    t_dir = os.path.dirname(os.path.abspath(args.target)) if (args.target and args.target != "-") else None
    if t_dir and os.path.basename(t_dir) != "Directory":
        homunculus_paths.ensure_directory_fresh(workspace_dir=t_dir, homunculus_root=_HOM_ROOT)
    def_ent = args.entity or (os.path.basename(os.path.normpath(args.project_dir)) if args.project_dir else "")
    report = audit_target(target_text, idx, target_dir=t_dir, default_entity=def_ent)

    if args.transcript:
        transcript_errs = attest_subagent_transcript(args.transcript, target_text)
        report["transcript_attestation_errors"] = transcript_errs
        for terr in transcript_errs:
            report["unbacked_claims"].append({"line": 0, "type": "TRANSCRIPT_ATTESTATION_ERROR", "claim": terr})
        report["unbacked_count"] += len(transcript_errs)

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        status = "PASS" if report["unbacked_count"] == 0 else "FAIL — UNBACKED CLAIMS DETECTED"
        if report["unbacked_count"] == 0 and args.strict_provenance and report["provenance_warning_count"] > 0:
            status = "BLOCKED — UNVETTED SOURCE PROVENANCE"
        elif report["unbacked_count"] == 0 and args.fail_on_tbd and report["tbd_count"] > 0:
            status = "BLOCKED — UNRESOLVED [TBD] OFFENDERS"
        print(f"=== Claim Verification Audit: {target_label} ===")
        print(f"Status: {status} | Receipt: {report['vrf_token']} | Sources: {report['sources_checked']}")
        print(
            f"Supported Claims: {report['supported_count']} | "
            f"Unbacked Claims: {report['unbacked_count']} | "
            f"Open [TBD] Offenders: {report['tbd_count']} | "
            f"Provenance Advisories: {report['provenance_warning_count']}"
        )
        src_summary = ", ".join(
            f"{os.path.basename(s['file'])}({s['sha256_10']})" for s in report["source_hashes"][:8]
        )
        if len(report["source_hashes"]) > 8:
            src_summary += f", +{len(report['source_hashes']) - 8} more"
        print(f"Source Hashes: {src_summary}")

        if report["excluded_circular_sources"]:
            print(
                f"Auto-Excluded Self-Target from Directory Scan: "
                f"{', '.join(report['excluded_circular_sources'])}"
            )
        if report.get("excluded_lessons_learned_sources"):
            print(
                f"Auto-Excluded Lessons-Learned Ledgers (Failed-Attempt Quarantine): "
                f"{', '.join(os.path.basename(fp) for fp in report['excluded_lessons_learned_sources'])}"
            )

        if report["provenance_warnings"]:
            print(
                "\n[~] SOURCE PROVENANCE ADVISORIES "
                "(Alert user -> decide to SKIP source OR WORK IN PARALLEL to separate core truth):"
            )
            for pw in report["provenance_warnings"]:
                print(f"  - {pw['file']}: {', '.join(pw['reasons'])}")

        if report["unbacked_claims"]:
            print("\n[!] UNBACKED CLAIMS (Must bind to source, replace with [TBD: ...], or remove):")
            for item in report["unbacked_claims"]:
                print(f"  - Line {item['line']} [{item['type']}]: {item['claim']}")

        if report["tbd_offenders"]:
            print("\n[?] OPEN [TBD] OFFENDERS (Tracked explicitly for user resolution):")
            for item in report["tbd_offenders"]:
                print(f"  - Line {item['line']}: {item['marker']}")

    has_forged_vrf = any(
        any("forged" in str(r) or "hash mismatch" in str(r) for r in pw.get("reasons", []))
        for pw in report.get("provenance_warnings", [])
    )
    if has_forged_vrf:
        return 3
    if report["unbacked_count"] > 0:
        return 1
    if args.strict_provenance and report["provenance_warning_count"] > 0:
        return 3
    if args.fail_on_tbd and report["tbd_count"] > 0:
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
