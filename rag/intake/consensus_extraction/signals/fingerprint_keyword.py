"""
Signal: fingerprint_keyword — wraps `_fingerprint_extract_matches`
(Ship 28+29 catalog) and emits per-candidate contributions.

Also carries the excerpt + position as metadata for downstream use
(finding evidence_text derived from here).
"""
from __future__ import annotations

from typing import Any

from rag.intake.consensus_extraction.types import (
    ExtractionSignalOutput,
    CandidateKey,
)
from rag.intake.consensus_extraction.config import (
    ExtractionConsensusConfig,
)


def compute(
    doc:              Any,   # ParsedDocument
    scoped_leaf_ids:  list[str],
    cfg:              ExtractionConsensusConfig,
) -> ExtractionSignalOutput:
    """Run fingerprint matching, apply Ship 16'.b specificity gate
    (kept — it's a valuable pre-filter), emit one (leaf, must) entry
    per surviving match.

    Also captures excerpt + position in metadata['per_candidate'] so
    the aggregator can materialize DocumentFindings.
    """
    from rag.intake.extractor import (
        _fingerprint_extract_matches,
        _extract_quote_around_match,
        _get_token_set_specificity,
        _SPECIFICITY_THRESHOLD,
    )

    if not scoped_leaf_ids:
        return ExtractionSignalOutput(name="fingerprint_keyword", fired=False)

    matches = _fingerprint_extract_matches(scoped_leaf_ids, doc)
    if not matches:
        return ExtractionSignalOutput(name="fingerprint_keyword", candidates={}, fired=True)

    specificity = _get_token_set_specificity()

    candidates: dict[CandidateKey, float] = {}
    per_candidate: dict[CandidateKey, dict] = {}
    seen: set[CandidateKey] = set()

    for m in matches:
        key: CandidateKey = (m["leaf_id"], m["must_id"])
        if key in seen:
            continue
        seen.add(key)

        # Ship 16'.b specificity gate — cheap pre-filter, still worth
        # applying at signal time. Multi-attribution cases will land
        # here; consensus corroboration then decides.
        matched_kw = m.get("matched_kw") or []
        if matched_kw and specificity:
            kw_key = frozenset(str(t).lower() for t in matched_kw)
            leaf_count = specificity.get(kw_key, 1)
            if leaf_count > _SPECIFICITY_THRESHOLD:
                # Skip — over-broad token set, don't even emit
                continue

        quote = _extract_quote_around_match(m, doc)
        if not quote:
            continue

        candidates[key] = cfg.fingerprint_weight
        per_candidate[key] = {
            "excerpt":     quote,
            "position":    m.get("position"),
            "control_ref": m["control_ref"],
            "standard_id": m["standard_id"],
            "matched_kw":  matched_kw,
        }

    return ExtractionSignalOutput(
        name       = "fingerprint_keyword",
        candidates = candidates,
        metadata   = {"per_candidate": per_candidate,
                      "n_matches_raw": len(matches),
                      "n_matches_kept": len(candidates)},
        fired      = True,
    )
