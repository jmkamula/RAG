"""
Signal: must_semantic_topk — first caller of `semantic_musts_in_scope`.

Queries the `musts_arioncomply` Chroma collection with the doc text;
top-K MUSTs (default 30) receive this signal's weight. Independent
of fingerprint matches — this is the semantic corroboration signal.
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
    """Ask the MUST Chroma collection for the top-K most semantically
    similar MUSTs to this doc. Emit each with `must_semantic_weight`.

    Filters to MUSTs whose parent leaf is in scoped_leaf_ids —
    otherwise the signal would corroborate off-scope MUSTs.
    """
    from rag.intake.must_embedding_lookup import semantic_musts_in_scope

    doc_text = getattr(doc, "markdown", None) or getattr(doc, "full_text", None) or ""
    tenant_stds = getattr(doc, "standard_ids", None) or None
    if not doc_text:
        return ExtractionSignalOutput(name="must_semantic_topk", fired=False)

    must_ids = semantic_musts_in_scope(
        doc_text    = doc_text,
        top_k       = cfg.must_semantic_topk,
        tenant_stds = tenant_stds,
    )
    if not must_ids:
        return ExtractionSignalOutput(name="must_semantic_topk", candidates={}, fired=True)

    # Filter to MUSTs whose parent leaf is in scope. must_id shape:
    # "item:CTRL:slug". leaf_id shape: "req:CTRL:variant". We compute
    # {control_ref: [leaf_ids]} from scoped_leaf_ids for the join.
    from rag.id_types import leaf_control_ref
    ctrl_to_leaves: dict[str, list[str]] = {}
    for lid in scoped_leaf_ids:
        ctrl = leaf_control_ref(lid)
        if ctrl:
            ctrl_to_leaves.setdefault(ctrl, []).append(lid)

    candidates: dict[CandidateKey, float] = {}
    for must_id in must_ids:
        # must_id like "item:A.5.15:rbac" → ctrl "A.5.15"
        parts = (must_id or "").split(":")
        if len(parts) < 3:
            continue
        ctrl = parts[1]
        for leaf_id in ctrl_to_leaves.get(ctrl, []):
            candidates[(leaf_id, must_id)] = cfg.must_semantic_weight

    return ExtractionSignalOutput(
        name       = "must_semantic_topk",
        candidates = candidates,
        metadata   = {"n_must_ids_topk": len(must_ids),
                      "n_candidates_in_scope": len(candidates)},
        fired      = True,
    )
