"""Ship 69'.c — dimension extraction from bridge edge rationales.

Bridge edges in Neo4j (IMPLEMENTS / SUPPORTS / ENABLES / GOVERNANCE)
carry curator-authored `rationale` text. Ship 69'.a's audit found
that ~45% of rationales name a specific security dimension or
mechanism — "confidentiality", "encryption", "access rights",
"accountability", etc. — that the mapping is intended to address.

Ship 69'.c surfaces those dimensions in the Evidence Package UX as
a group-level italic sentence under each ↗ MUST label:

    - ↗ **Review date within the planned interval**
      _Related controls address confidentiality, integrity, and
       access management._

Compute-at-read-time design: no schema change, no loader change.
Rationale parsing is a small regex + normalize + dedupe pass; costs
microseconds per bridge. Aligns with Ship 7' vocab-as-data /
opt-in-never-middleware principles.
"""
from __future__ import annotations

import re


# Controlled vocab: raw token → display term. Curators can write any
# common variant in the rationale; this pass normalizes to the
# display term. Grouping keeps the sentence readable — three "access"
# variants collapse to "access management", not three tokens.
_DIMENSION_MAP: dict[str, str] = {
    # Core CIA + adjacent
    "confidentiality":       "confidentiality",
    "integrity":             "integrity",
    "availability":          "availability",
    "resilience":            "resilience",
    "disaster recovery":     "resilience",

    # Mechanisms
    "encryption":            "encryption",
    "pseudonymisation":      "pseudonymisation",
    "pseudonymization":      "pseudonymisation",
    "anonymisation":         "anonymisation",
    "anonymization":         "anonymisation",
    "de-identification":     "pseudonymisation",

    # Access
    "access control":        "access management",
    "access rights":         "access management",
    "authentication":        "authentication",
    "authorisation":         "access management",
    "authorization":         "access management",

    # Ops
    "logging":               "logging",
    "monitoring":            "monitoring",
    "backup":                "backup",
    "recovery":              "recovery",

    # Incident + response
    "incident response":     "incident response",
    "incident notification": "breach notification",
    "breach notification":   "breach notification",

    # Risk / assurance
    "risk assessment":       "risk assessment",
    "risk treatment":        "risk assessment",
    "impact assessment":     "impact assessment",

    # People / third party
    "training":              "training",
    "awareness":             "training",
    "vendor management":     "vendor management",
    "supplier management":   "vendor management",
    "processor":             "processor obligations",

    # GDPR principles
    "data minimisation":     "data minimisation",
    "data minimization":     "data minimisation",
    "purpose limitation":    "purpose limitation",
    "storage limitation":    "storage limitation",
    "accuracy":              "accuracy",
    "lawfulness":            "lawfulness",
    "transparency":          "transparency",
    "accountability":        "accountability",
}

# Compiled matcher — longest tokens first so "access control" wins
# over "access" alone.
_TOKEN_RE = re.compile(
    r"\b(" + "|".join(
        re.escape(t) for t in sorted(_DIMENSION_MAP, key=len, reverse=True)
    ) + r")\b",
    re.IGNORECASE,
)

# When multiple rationales pile up, cap the summary at N terms — the
# top-3-mentioned typically already characterizes the group; more
# starts to feel like a keyword dump.
_MAX_DIMENSIONS_IN_SUMMARY = 4


def extract_dimensions(text: str) -> list[str]:
    """Return display-form dimensions found in text, order of first
    appearance, deduped.

    Empty list when the text carries no controlled tokens (which is
    ~50% of bridge edges — Ship 69'.a `unspecified` bucket)."""
    if not text:
        return []
    seen: dict[str, None] = {}
    for m in _TOKEN_RE.finditer(text):
        raw = m.group(1).lower()
        display = _DIMENSION_MAP.get(raw)
        if display and display not in seen:
            seen[display] = None
    return list(seen)


def aggregate_dimensions(rationales: list[str]) -> list[str]:
    """Merge dimensions extracted across a group of rationales.

    Preserves order of first appearance across the input rationales,
    capped at `_MAX_DIMENSIONS_IN_SUMMARY`. Empty when no rationale
    in the group carried a controlled token."""
    seen: dict[str, None] = {}
    for r in rationales:
        for d in extract_dimensions(r):
            if d not in seen:
                seen[d] = None
                if len(seen) >= _MAX_DIMENSIONS_IN_SUMMARY:
                    return list(seen)
    return list(seen)


def humanize_dimension_list(dims: list[str]) -> str:
    """Render a dimension list as prose (Oxford comma, natural
    conjunction).

    Examples:
      []                              → ""
      ["confidentiality"]              → "confidentiality"
      ["conf", "integ"]                → "confidentiality and integrity"
      ["conf", "integ", "access"]      → "confidentiality, integrity, and access management"
    """
    if not dims:
        return ""
    if len(dims) == 1:
        return dims[0]
    if len(dims) == 2:
        return f"{dims[0]} and {dims[1]}"
    return ", ".join(dims[:-1]) + f", and {dims[-1]}"


def summary_sentence(rationales: list[str]) -> str:
    """Complete UX-ready sentence, or empty string when there are no
    identifiable dimensions across the input.

    Called by the Evidence Package renderer per ↗ MUST group."""
    dims = aggregate_dimensions(rationales)
    if not dims:
        return ""
    return f"Related controls address {humanize_dimension_list(dims)}."
