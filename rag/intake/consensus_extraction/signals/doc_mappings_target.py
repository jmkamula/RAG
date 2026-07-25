"""
Signal: doc_mappings_target — wraps `_scope_controls_via_doc_mappings`
+ `target_leaves` metadata and emits per-candidate contributions.

When a filename YAML mapping (db/doc_mappings/*.yaml) names a leaf as
a target, every MUST under that leaf gets this signal's weight.
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
    doc:               Any,       # ParsedDocument (post-scope-narrowing)
    scoped_leaf_ids:   list[str],
    cfg:               ExtractionConsensusConfig,
) -> ExtractionSignalOutput:
    """Read `doc.extraction_metrics.target_leaves` (populated by
    `_scope_controls_via_doc_mappings` upstream in extract()).

    For each target leaf, look up its MUSTs (via _fetch_leaf_musts)
    and emit (leaf, must) → doc_mappings_weight for each.
    """
    metrics = getattr(doc, "extraction_metrics", None) or {}
    target_leaves = metrics.get("target_leaves") or []
    if not target_leaves:
        return ExtractionSignalOutput(name="doc_mappings_target", fired=False)

    from rag.intake.extractor import _fetch_leaf_musts

    target_leaf_ids = [t.get("leaf_id") for t in target_leaves if t.get("leaf_id")]
    if not target_leaf_ids:
        return ExtractionSignalOutput(name="doc_mappings_target", fired=False)

    leaf_musts = _fetch_leaf_musts(target_leaf_ids) or {}

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
                candidates[(leaf_id, must_id)] = cfg.doc_mappings_weight

    return ExtractionSignalOutput(
        name       = "doc_mappings_target",
        candidates = candidates,
        metadata   = {"n_target_leaves": len(target_leaf_ids),
                      "n_target_musts":  len(candidates)},
        fired      = True,
    )
