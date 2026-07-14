"""
Signal B — explicit ref extraction via regex.

Uses rag.framework_refs.extract_ref_candidates to pull ref-shaped
tokens (A.5.18, Art.32, B.8.5.6, 9.1 ISMS clauses) directly from
the query text. Zero-cost, 100% precision on hit.

Role in consensus:
  - Hard-anchor. When a user types "is A.5.18 compliant?", the top
    retrieval hit had better be in the A.5.* family. The aggregator
    treats this signal's refs at explicit_ref_weight=1.0 — the
    highest weight of any signal.
  - Sets `framework` when the ref shape uniquely identifies it:
      A.X.X  → ISO27001:2022
      B.X.X  → ISO27701:2019 (processor)
      Art.X  → GDPR:2016/679
      bare N.N (ISMS 4-10) → ISO27001:2022 clauses
"""
from __future__ import annotations

from rag.consensus.types import SignalOutput, ConsensusConfig
from rag.framework_refs import extract_ref_candidates


def _framework_of_ref(ref: str) -> str | None:
    """Infer the standard from ref shape. None if ambiguous."""
    if ref.startswith("Art."):
        return "GDPR:2016/679"
    if ref.startswith("B."):
        # ISO 27701 processor extension. Could technically be ambiguous
        # with future frameworks but nothing else uses "B." today.
        return "ISO27701:2019"
    if ref.startswith("A.7.") and ref.count(".") >= 2:
        # Ambiguous — A.7.x.y is ISO 27701 controller; A.7.x is ISO 27001
        # physical. Report the more specific one.
        parts = ref.split(".")
        if len(parts) >= 4:
            return "ISO27701:2019"
        return "ISO27001:2022"
    if ref.startswith("A."):
        return "ISO27001:2022"
    # Bare ISMS clause "4.3", "9.2", "10.1" — ISO 27001 body
    if "." in ref and ref.split(".")[0].isdigit():
        first = int(ref.split(".")[0])
        if 4 <= first <= 10:
            return "ISO27001:2022"
    return None


def _dominant_framework(refs: list[str]) -> str | None:
    """Majority framework across extracted refs, if any is clearly dominant."""
    if not refs:
        return None
    counts: dict[str, int] = {}
    for r in refs:
        fw = _framework_of_ref(r)
        if fw:
            counts[fw] = counts.get(fw, 0) + 1
    if not counts:
        return None
    # Dominant = strictly more than any other
    ordered = sorted(counts.items(), key=lambda kv: kv[1], reverse=True)
    if len(ordered) == 1:
        return ordered[0][0]
    if ordered[0][1] > ordered[1][1]:
        return ordered[0][0]
    return None   # tie → let aggregator decide from other signals


def explicit_refs(query: str, cfg: ConsensusConfig) -> SignalOutput:
    """Return a SignalOutput carrying refs extracted verbatim from the query.

    - refs weight = cfg.explicit_ref_weight (hard anchor)
    - framework inferred from ref shape when possible
    - fired=False when no refs are found in the query
    """
    if not query:
        return SignalOutput(name="explicit_refs", fired=False)

    extracted = extract_ref_candidates(query)
    if not extracted:
        return SignalOutput(name="explicit_refs", fired=False)

    # De-duplicate while preserving order
    seen = set()
    unique = []
    for r in extracted:
        if r in seen:
            continue
        seen.add(r)
        unique.append(r)

    weight = cfg.explicit_ref_weight
    refs_out = [(r, weight) for r in unique]
    framework = _dominant_framework(unique)

    return SignalOutput(
        name       = "explicit_refs",
        refs       = refs_out,
        framework  = framework,
        metadata   = {
            "extracted_count": len(unique),
            "framework_votes": {r: _framework_of_ref(r) for r in unique},
        },
        fired      = True,
    )
