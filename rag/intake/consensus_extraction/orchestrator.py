"""
Extraction consensus orchestrator — runs all signals, aggregates,
returns per-candidate verdicts.

Ship 33'.b — shadow-mode ready. Gatekeeper wiring in follow-up.
"""
from __future__ import annotations

import logging
import time
from typing import Any, Optional

from rag.intake.consensus_extraction.types import (
    ExtractionSignalOutput,
    ExtractionConsensusResult,
)
from rag.intake.consensus_extraction.config import (
    ExtractionConsensusConfig,
    default_config,
)
from rag.intake.consensus_extraction.aggregator import aggregate_extraction

from rag.intake.consensus_extraction.signals import (
    fingerprint_keyword,
    doc_mappings_target,
    must_semantic_topk,
    explicit_ref,
    per_protocol_scope,
    semantic_fit_gate,
    content_shape_penalty,
    evidence_uniqueness,
)


logger = logging.getLogger(__name__)


def run_extraction_consensus(
    doc:              Any,             # ParsedDocument
    scoped_leaf_ids:  list[str],
    cfg:              Optional[ExtractionConsensusConfig] = None,
) -> ExtractionConsensusResult:
    """Run the seven signals + aggregate → per-candidate verdicts.

    Order matters because semantic_fit_gate + content_shape_penalty
    depend on fingerprint_keyword's excerpts.
    """
    if cfg is None:
        cfg = default_config()

    t0 = time.time()

    # Round 1: signals that don't depend on other signals
    sig_explicit_ref   = explicit_ref.compute(doc, scoped_leaf_ids, cfg)
    sig_doc_mappings   = doc_mappings_target.compute(doc, scoped_leaf_ids, cfg)
    sig_fingerprint    = fingerprint_keyword.compute(doc, scoped_leaf_ids, cfg)
    sig_must_semantic  = must_semantic_topk.compute(doc, scoped_leaf_ids, cfg)
    sig_per_protocol   = per_protocol_scope.compute(doc, scoped_leaf_ids, cfg)

    # Round 2: signals that depend on fingerprint_keyword's excerpts
    sig_semantic_fit    = semantic_fit_gate.compute(
        doc, scoped_leaf_ids, cfg, fingerprint_signal=sig_fingerprint,
    )
    sig_content_shape   = content_shape_penalty.compute(
        doc, scoped_leaf_ids, cfg, fingerprint_signal=sig_fingerprint,
    )
    # Ship 33'.b v3: cross-candidate signal — penalises multi-attribution
    sig_evidence_uniq   = evidence_uniqueness.compute(
        doc, scoped_leaf_ids, cfg, fingerprint_signal=sig_fingerprint,
    )

    signals = [
        sig_explicit_ref,
        sig_doc_mappings,
        sig_fingerprint,
        sig_must_semantic,
        sig_per_protocol,
        sig_semantic_fit,
        sig_content_shape,
        sig_evidence_uniq,
    ]

    result = aggregate_extraction(signals, cfg)

    # Ship 33'.c — LLM batched arbiter for candidates in the borderline
    # zone (0.40 ≤ score < 0.75). Bounded: cannot invent, cannot override
    # auto-accept or auto-drop. Fail-open: on LLM error, arbiter-zone
    # candidates stay 'arbiter' (caller can decide how to treat).
    if cfg.llm_arbiter_enabled and result.n_arbiter > 0:
        from rag.intake.consensus_extraction.gatekeeper import arbitrate
        arbitrate(
            doc_name = getattr(doc, "original_name", "<unknown>"),
            result   = result,
        )

    result.latency_ms = int((time.time() - t0) * 1000)

    logger.info(
        "consensus_extraction for %s: %d candidates → %d accept + %d arbiter + %d drop "
        "(signals fired: %d/%d, %dms)",
        getattr(doc, "original_name", "<unknown>"),
        result.total_candidates,
        result.n_accept, result.n_arbiter, result.n_drop,
        result.n_signals_fired, len(signals),
        result.latency_ms,
    )
    return result
