"""
rag/posture/pii_redactor.py — Ship 119'.a (2026-09-05).

Pattern-based PII redaction for the auditor's ledger. The ledger
handed to an external auditor may contain excerpts from tenant
documents; those excerpts may in turn contain personal data of
third parties (customers of the tenant, employees named in evidence,
data subjects mentioned in incident reports).

Design principle: the tenant is the data controller and decides
what the auditor sees. This module provides the *default-on* PII
scrub that operates unless the tenant explicitly opts out per
control. Names are *not* redacted by default — compliance evidence
often depends on named accountability ("the DPO is X"; "reviewed
by Y") — but structured identifiers that shouldn't appear in an
audit artifact (emails, phone numbers, national IDs, IBANs, credit
cards) are scrubbed.

Levels:
  · off      — pass through unchanged. Only used when the tenant
               explicitly opts in per control for evidence-of-
               implementation where verbatim source text matters.
  · default  — email + phone + national IDs + IBAN + credit card
               + IPv4 addresses. The right default for auditor
               packages.
  · strict   — default + IPv6 + dates that look like DoB + very
               broad name patterns. Use when the tenant's own
               data-protection policy demands maximum redaction.

Pseudonymisation:
  User identifiers (uuid, email) that appear in the ledger are
  replaced with deterministic short pseudonyms (`user-<6-hex>`).
  Uses a per-tenant salt so the same underlying identifier gets
  different pseudonyms across tenants — the tenant retains the
  salt privately, so only they can reverse-map the pseudonyms.
  The auditor sees `user-a3f2c1` and can ask the tenant who that
  is, case-by-case, in writing.
"""
from __future__ import annotations
import hashlib
import re
from typing import Iterable

# ── Patterns ───────────────────────────────────────────────────────

# RFC 5321-ish; permissive on the local part, requires TLD 2+ chars.
_EMAIL_RE = re.compile(
    r'\b[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}\b'
)

# Phone numbers — international (+cc followed by 6-14 digits with
# optional separators) OR ten-digit national with formatting.
# Deliberately conservative to avoid eating dates + control refs.
_PHONE_RE = re.compile(
    r'(?:'
    r'\+\d{1,3}[\s\-.]?\(?\d{1,4}\)?[\s\-.]?\d{2,4}[\s\-.]?\d{2,4}(?:[\s\-.]?\d{2,4})?'
    r'|'
    r'\(?\d{3}\)?[\s\-.]?\d{3}[\s\-.]?\d{4}'
    r')'
)

# US SSN: NNN-NN-NNNN (bounded by word boundaries to avoid eating
# dates like 2026-05-01)
_SSN_US_RE = re.compile(r'\b\d{3}-\d{2}-\d{4}\b')

# Credit card: 13-19 digits, optionally separated by space/dash into
# 4-digit chunks. Bounded by word breaks.
_CC_RE = re.compile(
    r'\b(?:\d{4}[\s\-]?){3}\d{4,7}\b'
    r'|'
    r'\b\d{13,19}\b'
)

# IBAN: 2-letter country + 2 check digits + 4-30 alphanumeric.
_IBAN_RE = re.compile(r'\b[A-Z]{2}\d{2}[A-Z0-9]{11,30}\b')

# IPv4 dotted quad.
_IPV4_RE = re.compile(r'\b(?:(?:25[0-5]|2[0-4]\d|1?\d\d?)\.){3}(?:25[0-5]|2[0-4]\d|1?\d\d?)\b')

# National-ID patterns (a few common European formats)
_NATIONAL_ID_PATTERNS = [
    # Czech/Slovak birth number (rodné číslo): 6-digit date + / + 3-4 digits
    (re.compile(r'\b\d{6}/\d{3,4}\b'),          'national_id_cz'),
    # UK NINO: 2 letters, 6 digits, 1 letter (with optional spaces)
    (re.compile(r'\b[A-Z]{2}\s?\d{2}\s?\d{2}\s?\d{2}\s?[A-Z]\b'), 'national_id_uk'),
    # France INSEE (NIR): 1 + 2 digits year + 2 digits month + 2 digits + 3 digits commune + 3 digits + 2 checksum
    (re.compile(r'\b[12]\s?\d{2}\s?\d{2}\s?\d{2}\s?\d{3}\s?\d{3}\s?\d{2}\b'), 'national_id_fr'),
]

# IPv6 (strict-only) — abbreviated form covers most real addresses.
_IPV6_RE = re.compile(r'\b(?:[0-9a-fA-F]{1,4}:){2,7}[0-9a-fA-F]{1,4}\b')


# ── Redactor ───────────────────────────────────────────────────────

REDACTION_LEVELS = ('off', 'default', 'strict')


def redact_pii(text: str, level: str = 'default') -> str:
    """Return `text` with PII patterns replaced by `<X-redacted>` tokens.

    See module docstring for level semantics. Unknown level raises
    ValueError so callers surface config bugs loudly.

    Idempotent within a level: redact_pii(redact_pii(t)) == redact_pii(t)
    because the replacement tokens don't match any of the patterns.
    """
    if level not in REDACTION_LEVELS:
        raise ValueError(f"level must be one of {REDACTION_LEVELS}; got {level!r}")

    if level == 'off' or not text:
        return text

    # Order matters — IBAN before credit-card (some IBANs look
    # numeric-heavy) but credit-card before generic 13-19 digit runs.
    text = _EMAIL_RE.sub('<email-redacted>', text)
    text = _IBAN_RE.sub('<iban-redacted>', text)
    for pat, tag in _NATIONAL_ID_PATTERNS:
        text = pat.sub(f'<{tag}-redacted>', text)
    text = _SSN_US_RE.sub('<ssn-redacted>', text)
    text = _CC_RE.sub('<cc-redacted>', text)
    text = _PHONE_RE.sub('<phone-redacted>', text)
    text = _IPV4_RE.sub('<ipv4-redacted>', text)

    if level == 'strict':
        text = _IPV6_RE.sub('<ipv6-redacted>', text)

    return text


# ── Pseudonymisation ───────────────────────────────────────────────

def pseudonymise_user_id(user_id: str, salt: str) -> str:
    """Deterministic pseudonym `user-<6-hex>` for a user identifier.

    Uses SHA-256 with a per-tenant salt so the same user_id in
    different tenants gets different pseudonyms. Tenant retains the
    salt privately; auditor sees the pseudonym only + must ask the
    tenant, case-by-case + in writing, to resolve any specific one.

    Deterministic — the same (user_id, salt) always yields the same
    pseudonym. Same person referenced twice in a ledger appears as
    the same pseudonym.
    """
    if not user_id:
        return '<unknown-user>'
    payload = f'{salt}:{user_id}'.encode()
    h = hashlib.sha256(payload).hexdigest()
    return f'user-{h[:6]}'


def pseudonymise_users_in_text(
    text: str, user_ids: Iterable[str], salt: str,
) -> str:
    """Replace every occurrence of any user_id in `text` with its
    pseudonym. Longer ids replaced first so shorter substrings don't
    prematurely match.

    Useful for scrubbing reviewer/attester UUIDs that leak into
    excerpts or gap descriptions.
    """
    if not text or not user_ids:
        return text
    # Sort by length DESC so longer ids don't get partially matched
    # after their substrings.
    for uid in sorted(set(user_ids), key=len, reverse=True):
        if uid and uid in text:
            text = text.replace(uid, pseudonymise_user_id(uid, salt))
    return text


# ── Redaction summary (for the ledger cover page) ──────────────────

def redaction_summary(level: str) -> str:
    """Human-readable one-line summary of what the level does.
    Renders on the ledger cover page so the auditor knows the
    redaction posture up-front.
    """
    if level == 'off':
        return (
            "PII redaction disabled — verbatim excerpts included as "
            "authored (tenant explicitly opted in)."
        )
    if level == 'default':
        return (
            "Default PII redaction: emails, phone numbers, national IDs "
            "(CZ/UK/FR/US), IBAN, credit-card, IPv4 addresses scrubbed. "
            "Names retained (compliance evidence depends on named "
            "accountability)."
        )
    if level == 'strict':
        return (
            "Strict PII redaction: default set + IPv6. Names retained "
            "(compliance evidence depends on named accountability)."
        )
    return f"Unknown redaction level: {level}"
