"""Sample-row value patterns for anchor confirmation.

Used by `workbook_discovery.py` (and later `doc_discovery`) to disambiguate
borderline-confidence fingerprint matches by inspecting actual data values
in the first few rows. A column header "Name" alone is ambiguous — it
becomes anchored only when the values inside say "Joseph Kamula" (person)
or "Acme Inc" (company).

Each pattern is a pure function `(value: str) -> bool`. They're tolerant
of leading/trailing whitespace, mixed case, and basic punctuation —
brittle exact matching would defeat the purpose. The patterns aim for
**high precision** (low false-positive rate when they match) over
recall — when uncertain, return False so the anchor demotes the proposal
rather than risk a false confirmation.

This module deliberately avoids LLM calls. Anchors must be deterministic
so the same workbook bytes produce the same confidence on every run.
"""
from __future__ import annotations

import re
from datetime import datetime
from typing import Callable


# ─────────────────────────────────────────────────────────────────────────────
# Built-in patterns
# ─────────────────────────────────────────────────────────────────────────────


# Person name — at least two capitalised name parts, supports hyphens
# and apostrophes (O'Brien / Smith-Jones). Doesn't require ASCII; \w
# covers Unicode letters under re.UNICODE (default in py3).
_PERSON_NAME_RE = re.compile(
    r"^[A-ZÀ-ÿ][\w'’-]+(\s+[A-ZÀ-ÿ][\w'’-]+){1,4}$"
)


def person_name(value: str) -> bool:
    v = (value or "").strip()
    if not v or len(v) > 80:
        return False
    return bool(_PERSON_NAME_RE.match(v))


# Company / org name — looks for legal-entity suffix or known SaaS/big-
# brand tokens. Tenant-agnostic; the SaaS list is brands that show up in
# many tenants' supplier registers, not Arion-specific.
_COMPANY_SUFFIX_RE = re.compile(
    r"\b("
    r"Inc|Incorporated|Ltd|LLC|LLP|L\.L\.C\.|Corp|Corporation|"
    r"GmbH|AG|SARL|SAS|SA|PLC|"
    r"Limited|Co\.|Company|"
    r"Sp\.?\s*z\s*o\.?o\.?|"  # Polish sp. z o.o.
    r"Pty|Pty Ltd|"
    r"BV|NV|AB|Oy"
    r")\b",
    re.IGNORECASE,
)

_KNOWN_SAAS = {
    "microsoft", "azure", "aws", "amazon", "google", "gcp",
    "atlassian", "jira", "confluence", "github", "gitlab",
    "salesforce", "okta", "auth0", "stripe", "twilio",
    "slack", "zoom", "datadog", "splunk", "pagerduty",
    "snowflake", "databricks", "mongodb", "redis",
    "odoo", "sharepoint", "office365", "m365",
    "ibm", "oracle", "sap",
}


def company_name(value: str) -> bool:
    v = (value or "").strip()
    if not v or len(v) > 120:
        return False
    if _COMPANY_SUFFIX_RE.search(v):
        return True
    v_lower = v.lower()
    return any(brand in v_lower for brand in _KNOWN_SAAS)


# ISO date or common date format — tolerant parser.
_DATE_FORMATS = (
    "%Y-%m-%d", "%Y/%m/%d", "%d/%m/%Y", "%d-%m-%Y",
    "%m/%d/%Y", "%m-%d-%Y", "%d %b %Y", "%d %B %Y",
    "%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S",
)


def iso_date(value: str) -> bool:
    v = (value or "").strip()
    if not v:
        return False
    # ISO short-circuit
    try:
        datetime.fromisoformat(v.split("+")[0])
        return True
    except (ValueError, TypeError):
        pass
    for fmt in _DATE_FORMATS:
        try:
            datetime.strptime(v[:len(fmt) + 5], fmt)
            return True
        except ValueError:
            continue
    return False


_COMPLIANCE_STATUS_VALUES = {
    "compliant", "non-compliant", "noncompliant", "not compliant",
    "in progress", "in-progress", "active", "pending", "expired",
    "completed", "complete", "done", "passed", "failed",
    "approved", "rejected", "draft", "review", "reviewed",
    "implemented", "partial", "not started", "deferred",
    "waived", "n/a", "na", "not applicable",
}


def compliance_status(value: str) -> bool:
    v = (value or "").strip().lower()
    return v in _COMPLIANCE_STATUS_VALUES


_RISK_RATING_VALUES = {
    "low", "medium", "med", "high", "critical", "extreme", "very high",
    "very low", "minor", "moderate", "major", "severe",
    "1", "2", "3", "4", "5", "negligible",
}


def risk_rating(value: str) -> bool:
    v = (value or "").strip().lower()
    return v in _RISK_RATING_VALUES


def numeric_score(value: str) -> bool:
    """Numeric, optionally with % suffix or trailing 'pts'."""
    v = (value or "").strip().rstrip("%").rstrip().removesuffix("pts").strip()
    if not v:
        return False
    try:
        float(v)
        return True
    except ValueError:
        return False


_CONTROL_REF_RE = re.compile(
    r"^(?:A\.\d+(?:\.\d+){0,2}|Art\.\s?\d+(?:\.\d+)?|\d+\.\d+(?:\.\d+)?)$"
)


def control_ref(value: str) -> bool:
    v = (value or "").strip()
    return bool(_CONTROL_REF_RE.match(v))


_EMAIL_RE = re.compile(r"^[\w.+-]+@[\w-]+\.[\w.-]+$")


def email(value: str) -> bool:
    return bool(_EMAIL_RE.match((value or "").strip()))


# Frequency / cadence — common workbook values.
_FREQUENCY_VALUES = {
    "daily", "weekly", "biweekly", "monthly", "quarterly", "semi-annually",
    "annually", "yearly", "ad hoc", "as needed", "when needed",
    "on demand", "continuous", "real-time",
}


def frequency_value(value: str) -> bool:
    v = (value or "").strip().lower()
    return v in _FREQUENCY_VALUES


# ─────────────────────────────────────────────────────────────────────────────
# Registry
# ─────────────────────────────────────────────────────────────────────────────


_PATTERNS: dict[str, Callable[[str], bool]] = {
    "person_name":       person_name,
    "company_name":      company_name,
    "iso_date":          iso_date,
    "compliance_status": compliance_status,
    "risk_rating":       risk_rating,
    "numeric_score":     numeric_score,
    "control_ref":       control_ref,
    "email":             email,
    "frequency_value":   frequency_value,
}


def get_pattern(name: str) -> Callable[[str], bool] | None:
    return _PATTERNS.get(name)


def known_pattern_names() -> list[str]:
    return sorted(_PATTERNS)


def check_anchor(
    values:           list[str],
    pattern_name:     str,
    min_match_ratio:  float = 0.7,
) -> tuple[bool, float]:
    """Return (passes_threshold, actual_ratio) for a column of sample values.

    Empty values are skipped — they don't count either way. If all values
    are empty, returns (False, 0.0): we can't anchor without data.
    """
    pattern = _PATTERNS.get(pattern_name)
    if pattern is None:
        return (False, 0.0)
    sample = [v for v in values if v and v.strip()]
    if not sample:
        return (False, 0.0)
    matches = sum(1 for v in sample if pattern(v))
    ratio = matches / len(sample)
    return (ratio >= min_match_ratio, ratio)
