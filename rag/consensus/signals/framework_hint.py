"""
Signal F — framework hint from raw query text.

Word-boundary regex that detects which compliance framework the user
explicitly named. Corroborates the framework inferred by other
signals (retrieval majority, explicit_refs shape).

Role in consensus:
  - When the query says "GDPR" and retrieval top hits are all ISO 27001,
    that's a disagreement worth clarifying.
  - Weight is small (framework_hint_weight=0.20) because the signal
    only names the framework — it doesn't identify specific refs.
  - Contributes framework=<detected>; refs list stays empty (this
    signal has no ref opinion).
"""
from __future__ import annotations

import re

from rag.consensus.types import SignalOutput, ConsensusConfig


# Framework token → canonical standard_id. Order matters for tie-
# breaking when multiple match: more-specific patterns first.
_FRAMEWORK_TOKENS = [
    (re.compile(r"\bISO\s?27701\b",       re.IGNORECASE), "ISO27701:2019"),
    (re.compile(r"\bISO\s?27001\b",       re.IGNORECASE), "ISO27001:2022"),
    (re.compile(r"\bISO\s?27002\b",       re.IGNORECASE), "ISO27001:2022"),  # 27002 = 27001's guidance
    (re.compile(r"\bGDPR\b",              re.IGNORECASE), "GDPR:2016/679"),
    (re.compile(r"\bPIMS\b",              re.IGNORECASE), "ISO27701:2019"),
    (re.compile(r"\bNIS\s?2\b|\bNIS2\b",  re.IGNORECASE), "NIS2:2022"),
    (re.compile(r"\bDORA\b",              re.IGNORECASE), "DORA:2022"),
    (re.compile(r"\bSOC\s?2\b|\bSOC2\b",  re.IGNORECASE), "SOC2"),
    (re.compile(r"\bHIPAA\b",             re.IGNORECASE), "HIPAA"),
]


def framework_hint(query: str, cfg: ConsensusConfig) -> SignalOutput:
    """Detect framework tokens in the query text.

    Returns SignalOutput with framework set when a token matches.
    Multi-framework queries (e.g. "GDPR compliance via ISO 27001")
    return the FIRST matched framework and record the rest in
    metadata for the aggregator's cross-framework disambiguation.
    """
    if not query:
        return SignalOutput(name="framework_hint", fired=False)

    matched: list[tuple[str, str]] = []   # [(matched_text, standard_id)]
    for pattern, standard_id in _FRAMEWORK_TOKENS:
        m = pattern.search(query)
        if m:
            matched.append((m.group(0), standard_id))

    if not matched:
        return SignalOutput(name="framework_hint", fired=False)

    # Deduplicate by standard_id, preserve order
    seen: set[str] = set()
    unique: list[tuple[str, str]] = []
    for txt, sid in matched:
        if sid in seen:
            continue
        seen.add(sid)
        unique.append((txt, sid))

    primary_framework = unique[0][1]
    all_frameworks    = [sid for _, sid in unique]

    return SignalOutput(
        name       = "framework_hint",
        refs       = [],   # this signal doesn't identify refs
        framework  = primary_framework,
        metadata   = {
            "matched_tokens":  [txt for txt, _ in unique],
            "all_frameworks":  all_frameworks,
            "is_multi_framework": len(all_frameworks) > 1,
            "weight":          cfg.framework_hint_weight,
        },
        fired      = True,
    )
