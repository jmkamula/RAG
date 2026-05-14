"""
ArionComply — Control Reference Normalizer

Maps control refs from various formats to canonical form.

ISO 27001:2022 refs appear in the wild as:
  5.18        → A.5.18
  A.5.18      → A.5.18  (already canonical)
  ISO 5.18    → A.5.18
  Clause 5.18 → A.5.18
  A5.18       → A.5.18  (missing dot)

GDPR refs:
  Art. 32     → Art.32
  Article 32  → Art.32
  GDPR 32     → Art.32

ISO 27701:
  6.1         → 6.1  (no A. prefix for 27701)
  P.6.1       → 6.1
"""
from __future__ import annotations
import re
from typing import Optional


# ── ISO 27001:2022 patterns ───────────────────────────────────────────────────

_ISO27001_PATTERN = re.compile(
    r'\b(?:ISO\s*27001\s*(?:Annex\s*A\s*)?|Annex\s*A\s*|A\.?|Clause\s*)?'
    r'([5-9]|10)\s*\.\s*(\d+)(?:\s*\.\s*(\d+))?\b',
    re.IGNORECASE,
)

_GDPR_PATTERN = re.compile(
    r'\b(?:GDPR\s*)?(?:Art(?:icle)?\.?\s*)(\d+)(?:\.(\d+))?\b',
    re.IGNORECASE,
)

_ISO27701_PATTERN = re.compile(
    r'\b(?:ISO\s*27701\s*)?(?:P\.?)?([5-9]|10)\s*\.\s*(\d+)(?:\s*\.\s*(\d+))?\b',
    re.IGNORECASE,
)

# ISO 27001:2022 main clauses (4-10) vs Annex A controls (5-8.x)
_ISO27001_MAIN_CLAUSES = {
    '4', '5', '6', '7', '8', '9', '10'
}
# Annex A controls start at 5.1 (not the same as clause 5)
# Clause 4-10 refs: look like "9.2" — these are real main clauses
# Annex A refs: look like "A.5.18" — these are controls
# Heuristic: if ref is bare "9.2" and 9.x is a main clause → keep as-is
# If ref is "5.18" with high sub-number → likely Annex A → add A.


def normalize_iso27001(ref: str) -> Optional[str]:
    """
    Normalize an ISO 27001 control ref to canonical form.
    Returns None if not recognizable as ISO 27001.

    Examples:
      '5.18'   → 'A.5.18'
      'A.5.18' → 'A.5.18'
      '9.2'    → '9.2'   (main clause, not Annex A)
      'A5.18'  → 'A.5.18'
    """
    if not ref:
        return None

    ref = ref.strip()

    # Already in canonical Annex A format
    if re.match(r'^A\.\d+\.\d+$', ref):
        return ref

    # Already a main clause like "9.2"
    if re.match(r'^(4|5|6|7|8|9|10)\.\d+$', ref):
        clause, sub = ref.split('.')
        # Main clauses have small sub-numbers (1-5 typically)
        # Annex A has larger sub-numbers (5.18 = control 18 in section 5)
        if int(sub) <= 10 and clause in ('4', '6', '7', '9', '10'):
            return ref  # main clause format preserved
        # Otherwise it's likely an Annex A ref without prefix
        return f"A.{ref}"

    # Strip A. prefix variations: "A5.18", "A 5.18", "A.5.18"
    cleaned = re.sub(r'^[Aa]\.?\s*', '', ref)
    if re.match(r'^\d+\.\d+$', cleaned):
        clause, sub = cleaned.split('.')
        if clause in ('5', '6', '7', '8'):
            return f"A.{cleaned}"
        return cleaned

    # Try full pattern match
    m = _ISO27001_PATTERN.match(ref)
    if m:
        clause = m.group(1)
        sub    = m.group(2)
        subsub = m.group(3)
        base   = f"{clause}.{sub}"
        if subsub:
            base = f"{base}.{subsub}"
        if clause in ('5', '6', '7', '8'):
            return f"A.{base}"
        return base

    return None


def normalize_gdpr(ref: str) -> Optional[str]:
    """
    Normalize a GDPR article ref.
    'Art. 32' → 'Art.32', 'Article 32(1)' → 'Art.32.1'
    """
    if not ref:
        return None
    m = _GDPR_PATTERN.match(ref.strip())
    if m:
        article = m.group(1)
        para    = m.group(2)
        if para:
            return f"Art.{article}.{para}"
        return f"Art.{article}"
    return None


def normalize_ref(ref: str, standard_id: str) -> Optional[str]:
    """
    Normalize a control ref for a given standard.
    Returns None if the ref cannot be normalized.
    """
    if not ref or not standard_id:
        return None

    ref = ref.strip().rstrip('.,;:)')

    std = standard_id.upper()

    if 'ISO27001' in std or 'ISO 27001' in std:
        return normalize_iso27001(ref)
    if 'GDPR' in std:
        return normalize_gdpr(ref)
    if 'ISO27701' in std or 'ISO 27701' in std:
        # ISO 27701 uses 6.x.x format, no A. prefix
        m = re.match(r'^(?:P\.?)?(\d+\.\d+(?:\.\d+)?)$', ref.strip())
        if m:
            return m.group(1)
        return None

    # Unknown standard — return as-is if it looks like a ref
    if re.match(r'^[A-Z0-9.]+$', ref):
        return ref
    return None


def extract_refs_from_text(text: str, standard_id: str) -> list[str]:
    """
    Extract and normalize all control refs found in a block of text.
    Used for the pre-flight explicit reference scan.
    """
    if not text or not standard_id:
        return []

    found = set()
    std   = standard_id.upper()

    if 'ISO27001' in std or 'ISO 27001' in std:
        # Match patterns like A.5.18, 5.18, A5.18, clause 5.18
        pattern = re.compile(
            r'\b(?:[Aa]\.?\s*)?([5-8])\s*\.\s*(\d+)\b',
            re.IGNORECASE,
        )
        for m in pattern.finditer(text):
            clause = m.group(1)
            sub    = m.group(2)
            ref    = normalize_iso27001(f"{clause}.{sub}")
            if ref:
                found.add(ref)

        # Also match main clauses 4-10
        main_pattern = re.compile(r'\bclause\s+(4|5|6|7|8|9|10)\.(\d+)\b', re.IGNORECASE)
        for m in main_pattern.finditer(text):
            ref = f"{m.group(1)}.{m.group(2)}"
            found.add(ref)

    if 'GDPR' in std:
        for m in _GDPR_PATTERN.finditer(text):
            ref = normalize_gdpr(m.group(0))
            if ref:
                found.add(ref)

    return sorted(found)


def get_clause_group(control_ref: str, standard_id: str) -> Optional[str]:
    """
    Return the top-level clause group for a control ref.
    Used for scoping the control list passed to the LLM.

    Examples:
      'A.5.18' → 'A.5'
      'A.8.3'  → 'A.8'
      '9.2'    → '9'
    """
    if not control_ref:
        return None

    m = re.match(r'^A\.(\d+)', control_ref)
    if m:
        return f"A.{m.group(1)}"

    m = re.match(r'^(\d+)\.\d+', control_ref)
    if m:
        return m.group(1)

    return None


# ── Doc type → likely control clause groups ──────────────────────────────────

DOC_TYPE_CLAUSE_MAP = {
    "policy": {
        "ISO27001:2022": ["A.5", "A.6", "A.7", "A.8"],
        "GDPR:2016/679": ["Art.5", "Art.6", "Art.7", "Art.24", "Art.25", "Art.32"],
        "ISO27701:2019": ["6", "7", "8"],
    },
    "procedure": {
        "ISO27001:2022": ["A.5", "A.8"],
        "GDPR:2016/679": ["Art.30", "Art.32", "Art.33", "Art.35"],
    },
    "risk_register": {
        "ISO27001:2022": ["6", "8"],
        "GDPR:2016/679": ["Art.32", "Art.35"],
    },
    "audit_report": {
        "ISO27001:2022": ["A.5", "A.6", "A.7", "A.8", "9", "10"],
    },
    "evidence": {
        "ISO27001:2022": ["A.5", "A.6", "A.8"],
    },
    "asset_inventory": {
        "ISO27001:2022": ["A.5.9", "A.5.10", "A.8.1", "A.8.3"],
    },
}


def get_clause_scope(doc_type: str, standard_id: str) -> list[str]:
    """Return the likely clause groups for a given doc_type + standard."""
    return DOC_TYPE_CLAUSE_MAP.get(doc_type, {}).get(standard_id, [])
