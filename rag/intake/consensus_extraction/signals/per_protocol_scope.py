"""
Signal: per_protocol_scope — control_ref is in per-standard Chroma
retrieval top-K.

Reads `doc.extraction_metrics.retrieval_scoped_refs` if the extractor
populated it via `_scope_controls_via_retrieval`. Otherwise queries
per-standard collections directly (may be a no-op if not available).
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
    """Read the per-protocol scoped control refs — populated by
    `_scope_controls_via_retrieval` earlier in the extractor pipeline
    (surfaced via `doc.extraction_metrics`). Every candidate whose
    control is in that set gets `per_protocol_weight`.
    """
    # Query per-standard Chroma via extractor's existing helper. The doc's
    # extraction_metrics has `retrieval_scoped_count` but not the refs
    # themselves — so we re-run the scope narrowing here (Chroma-backed,
    # already-cached; cheap).
    from rag.id_types import leaf_control_ref
    from rag.intake.extractor import _fetch_leaf_musts, _scope_controls_via_retrieval

    # Need a controls list to hand to the retrieval scoper. Build it from
    # the doc's declared standards (same shape as the doc_pipeline does).
    tenant_stds = getattr(doc, "standard_ids", None) or []
    if not tenant_stds:
        return ExtractionSignalOutput(name="per_protocol_scope", fired=False)

    controls: list[dict] = []
    seen: set[tuple] = set()
    try:
        from rag.intake.doc_pipeline import DocumentPipeline
        import os as _os
        _pipe = DocumentPipeline(
            db_url=f"host=127.0.0.1 dbname=arioncomply_compliance user=arioncomply",
            api_key=_os.getenv("OPENAI_API_KEY", ""),
        )
        for std in tenant_stds:
            for c in (_pipe._load_controls_from_neo4j(std) or []):
                k = (c.get("ref"), c.get("standard_id"))
                if k not in seen:
                    seen.add(k)
                    controls.append(c)
    except Exception:
        return ExtractionSignalOutput(name="per_protocol_scope", fired=False)

    if not controls:
        return ExtractionSignalOutput(name="per_protocol_scope", fired=False)

    scoped = _scope_controls_via_retrieval(controls, doc) or []
    scoped_refs = {c.get("ref") for c in scoped if c.get("ref")}
    if not scoped_refs:
        return ExtractionSignalOutput(name="per_protocol_scope", candidates={}, fired=True)

    matching_leaf_ids = [
        lid for lid in scoped_leaf_ids
        if (leaf_control_ref(lid) or "") in scoped_refs
    ]
    if not matching_leaf_ids:
        return ExtractionSignalOutput(
            name="per_protocol_scope", candidates={}, fired=True,
            metadata={"n_scoped_refs": len(scoped_refs), "n_scoped_leaves": 0},
        )

    leaf_musts = _fetch_leaf_musts(matching_leaf_ids) or {}

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
                candidates[(leaf_id, must_id)] = cfg.per_protocol_weight

    return ExtractionSignalOutput(
        name       = "per_protocol_scope",
        candidates = candidates,
        metadata   = {"n_scoped_refs": len(scoped_refs),
                      "n_scoped_leaves": len(matching_leaf_ids)},
        fired      = True,
    )
