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

    ISMS clauses (4-10) collide with Annex A categories (A.5-A.8) at
    the 2-dot level — e.g. "8.2" is both ISMS clause 8.2 (Information
    security risk assessment) AND Annex A.8.2 (Privileged access
    rights). The normalizer cannot disambiguate from format alone, so
    it favours preservation over heuristic prefixing.

    Rules:
      - 3-dot pattern (e.g. "6.1.1", "A.6.1.1") → ISMS clause, never
        Annex A (which is single-subclause only). Strip any A.
        prefix.
      - "A.5.18" (canonical Annex A) → leave alone.
      - "5.18" (bare 2-dot) → leave alone. Callers must pass the
        canonical form (the LLM gets canonical refs in its input list
        from doc_mappings; workbook readers must use the curated
        canonical form). Auto-prefixing was the source of a data-
        corruption bug where ISMS clauses 5.x/6.x/7.x/8.x landed in
        Annex A storage.
      - "9.2", "10.1" → leave alone (unambiguous, ISMS body).
      - "A5.18" / "A 5.18" (no dot after A) → normalise to "A.5.18".

    Examples:
      '5.18'    → '5.18'        (bare, no auto-prefix)
      'A.5.18'  → 'A.5.18'      (canonical Annex A)
      '6.1.1'   → '6.1.1'       (ISMS clause, 3-dot)
      'A.6.1.1' → '6.1.1'       (3-dot can't be Annex A, strip prefix)
      'A5.18'   → 'A.5.18'      (canonicalise spacing)
      '9.2'     → '9.2'         (ISMS body)
    """
    if not ref:
        return None

    ref = ref.strip()

    # 3-dot pattern: always ISMS clause, never Annex A. Strip any A. prefix.
    m3 = re.match(r'^([Aa]\.?\s*)?(\d+\.\d+\.\d+)$', ref)
    if m3:
        return m3.group(2)

    # Already canonical Annex A "A.x.y"
    if re.match(r'^A\.\d+\.\d+$', ref):
        return ref

    # Bare 2-dot — leave alone. Callers must canonicalise upstream.
    if re.match(r'^\d+\.\d+$', ref):
        return ref

    # "A5.18" / "A 5.18" → "A.5.18" (canonicalise spacing only — the
    # caller explicitly wrote A-prefix, just clean the format).
    m_a = re.match(r'^[Aa]\.?\s*(\d+\.\d+)$', ref)
    if m_a:
        return f"A.{m_a.group(1)}"

    # Full multi-part match (e.g. "5.18.2"). Strip A. prefix if any —
    # multi-part is always ISMS body.
    m_full = _ISO27001_PATTERN.match(ref)
    if m_full:
        clause = m_full.group(1)
        sub    = m_full.group(2)
        subsub = m_full.group(3)
        base = f"{clause}.{sub}"
        if subsub:
            base = f"{base}.{subsub}"
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
