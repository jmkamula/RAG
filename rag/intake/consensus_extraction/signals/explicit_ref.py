"""
Signal: explicit_ref — doc self-cites this candidate's control_ref.

Reads `doc.explicit_refs` (populated by enricher). For each control_ref
in that list, every candidate under it gets the explicit_ref weight.
Authoritative signal — author's explicit statement of intent.
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
    doc:              Any,
    scoped_leaf_ids:  list[str],
    cfg:              ExtractionConsensusConfig,
) -> ExtractionSignalOutput:
    explicit_refs = set(getattr(doc, "explicit_refs", None) or [])
    if not explicit_refs:
        return ExtractionSignalOutput(name="explicit_ref", fired=False)

    from rag.id_types import leaf_control_ref
    from rag.intake.extractor import _fetch_leaf_musts

    # Group scoped leaves by control_ref, filter to explicitly-cited controls
    cited_leaf_ids: list[str] = []
    for lid in scoped_leaf_ids:
        ctrl = leaf_control_ref(lid)
        if ctrl and ctrl in explicit_refs:
            cited_leaf_ids.append(lid)

    if not cited_leaf_ids:
        return ExtractionSignalOutput(name="explicit_ref", candidates={}, fired=True)

    leaf_musts = _fetch_leaf_musts(cited_leaf_ids) or {}

    # _fetch_leaf_musts returns dict[leaf_id, list[tuple[must_id, must_text]]]
    candidates: dict[CandidateKey, float] = {}
    for leaf_id, items in leaf_musts.items():
        for item in items or []:
            if isinstance(item, tuple) and len(item) >= 1:
                must_id = item[0]
            elif isinstance(item, dict):
                must_id = item.get("id")
            else:
                must_id = None
            if must_id:
                candidates[(leaf_id, must_id)] = cfg.explicit_ref_weight

    return ExtractionSignalOutput(
        name       = "explicit_ref",
        candidates = candidates,
        metadata   = {"n_cited_refs": len(explicit_refs),
                      "n_cited_leaves": len(cited_leaf_ids)},
        fired      = True,
    )
