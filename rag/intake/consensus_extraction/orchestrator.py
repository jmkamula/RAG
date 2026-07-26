"""
Extraction consensus orchestrator — runs all signals, aggregates,
returns per-candidate verdicts.

Ship 33'.b — shadow-mode ready. Gatekeeper wiring in follow-up.
Ship 44'.c — OTel spans on orchestrator + each signal + aggregator +
arbiter. `arion.*` attribute namespace (no `gen_ai.*` — that's for
LLM-shaped spans, and consensus signals aren't LLM calls except
the arbiter which uses OpenAI SDK auto-instrumentation).
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
    bm25_topk,
    explicit_ref,
    per_protocol_scope,
    semantic_fit_gate,
    content_shape_penalty,
    evidence_uniqueness,
)

from rag.telemetry import get_tracer, capture_content


logger = logging.getLogger(__name__)

_tracer = get_tracer(__name__)


def _run_signal(name: str, signal_module, *args, **kwargs) -> ExtractionSignalOutput:
    """Wrap a signal.compute() call in an OTel span. Span attributes
    capture fired-status + candidate count + selected signal metadata;
    NEVER captures excerpt content (metadata may include per_candidate
    dicts with excerpts on debug tier — filtered here)."""
    with _tracer.start_as_current_span(
        f"arion.consensus.signal.{name}"
    ) as span:
        try:
            result = signal_module.compute(*args, **kwargs)
        except Exception as e:
            try:
                from opentelemetry import trace as _t
                span.set_status(_t.Status(_t.StatusCode.ERROR, str(e)[:200]))
            except Exception:
                pass
            raise
        try:
            span.set_attribute("arion.consensus.signal.name", name)
            span.set_attribute("arion.consensus.signal.fired", bool(result.fired))
            span.set_attribute(
                "arion.consensus.signal.n_candidates",
                len(result.candidates or {}),
            )
            # Attach cheap scalars from metadata (numeric fields only).
            for k, v in (result.metadata or {}).items():
                if k == "per_candidate":
                    continue  # skip content-rich per-candidate dict
                if isinstance(v, (int, float, bool)):
                    span.set_attribute(f"arion.consensus.signal.meta.{k}", v)
        except Exception:
            pass
        return result


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

    with _tracer.start_as_current_span("arion.consensus.run") as run_span:
        # Only capture doc identity + scoped-leaf count as base
        # attributes; downstream span attributes carry per-signal detail.
        doc_name = getattr(doc, "original_name", "<unknown>")
        try:
            run_span.set_attribute("arion.consensus.n_scoped_leaves", len(scoped_leaf_ids))
            if capture_content():
                run_span.set_attribute("arion.consensus.doc_name", doc_name[:500])
        except Exception:
            pass

        # Ship 39'.b — scope widening. must_semantic_topk now emits
        # candidates for ANY Chroma-surfaced MUST (Ship 39 layer-3 fix).
        # For those candidates to receive corroboration from the other
        # signals (fingerprint_keyword, semantic_fit_gate, etc.), the
        # OTHER signals also need to operate on the widened scope.
        sig_must_semantic  = _run_signal("must_semantic_topk", must_semantic_topk, doc, scoped_leaf_ids, cfg)
        # Ship 43'.b — BM25 lexical discovery-mode signal.
        sig_bm25           = _run_signal("bm25_topk", bm25_topk, doc, scoped_leaf_ids, cfg)
        widened_leaf_ids = list({
            *scoped_leaf_ids,
            *(lid for (lid, _mid) in sig_must_semantic.candidates.keys() if lid),
            *(lid for (lid, _mid) in sig_bm25.candidates.keys() if lid),
        })
        try:
            run_span.set_attribute("arion.consensus.n_widened_leaves", len(widened_leaf_ids))
        except Exception:
            pass

        # Round 1: signals that don't depend on other signals (widened scope)
        sig_explicit_ref   = _run_signal("explicit_ref", explicit_ref, doc, widened_leaf_ids, cfg)
        sig_doc_mappings   = _run_signal("doc_mappings_target", doc_mappings_target, doc, widened_leaf_ids, cfg)
        sig_fingerprint    = _run_signal("fingerprint_keyword", fingerprint_keyword, doc, widened_leaf_ids, cfg)
        sig_per_protocol   = _run_signal("per_protocol_scope", per_protocol_scope, doc, widened_leaf_ids, cfg)

        # Round 2: signals that depend on fingerprint_keyword's excerpts
        sig_semantic_fit    = _run_signal(
            "semantic_fit_gate", semantic_fit_gate,
            doc, widened_leaf_ids, cfg, fingerprint_signal=sig_fingerprint,
        )
        sig_content_shape   = _run_signal(
            "content_shape_penalty", content_shape_penalty,
            doc, widened_leaf_ids, cfg, fingerprint_signal=sig_fingerprint,
        )
        # Ship 33'.b v3: cross-candidate signal — penalises multi-attribution
        sig_evidence_uniq   = _run_signal(
            "evidence_uniqueness", evidence_uniqueness,
            doc, widened_leaf_ids, cfg, fingerprint_signal=sig_fingerprint,
        )

        signals = [
            sig_explicit_ref,
            sig_doc_mappings,
            sig_fingerprint,
            sig_must_semantic,
            sig_bm25,
            sig_per_protocol,
            sig_semantic_fit,
            sig_content_shape,
            sig_evidence_uniq,
        ]

        with _tracer.start_as_current_span("arion.consensus.aggregate") as agg_span:
            result = aggregate_extraction(signals, cfg)
            try:
                agg_span.set_attribute("arion.consensus.total_candidates",
                                        result.total_candidates)
                agg_span.set_attribute("arion.consensus.n_accept",   result.n_accept)
                agg_span.set_attribute("arion.consensus.n_arbiter",  result.n_arbiter)
                agg_span.set_attribute("arion.consensus.n_drop",     result.n_drop)
                agg_span.set_attribute("arion.consensus.n_signals_fired",
                                        result.n_signals_fired)
            except Exception:
                pass

        # Ship 33'.c — LLM batched arbiter for candidates in the borderline
        # zone. openai.chat auto-instrumentation (OpenInference) emits
        # gen_ai.* spans for the LLM call itself; we wrap in an outer
        # span so the whole arbitrate() pass gets a coherent group.
        if cfg.llm_arbiter_enabled and result.n_arbiter > 0:
            from rag.intake.consensus_extraction.gatekeeper import arbitrate
            with _tracer.start_as_current_span("arion.consensus.arbitrate") as arb_span:
                try:
                    arb_span.set_attribute("arion.consensus.n_arbiter_zone",
                                            result.n_arbiter)
                except Exception:
                    pass
                arbitrate(
                    doc_name = doc_name,
                    result   = result,
                )
                try:
                    arb_span.set_attribute("arion.consensus.n_llm_accept",
                                            result.n_arbiter_llm_accept)
                    arb_span.set_attribute("arion.consensus.n_llm_reject",
                                            result.n_arbiter_llm_reject)
                except Exception:
                    pass

        result.latency_ms = int((time.time() - t0) * 1000)
        try:
            run_span.set_attribute("arion.consensus.total_candidates",
                                    result.total_candidates)
            run_span.set_attribute("arion.consensus.n_accept", result.n_accept)
            run_span.set_attribute("arion.consensus.n_arbiter", result.n_arbiter)
            run_span.set_attribute("arion.consensus.n_drop", result.n_drop)
            run_span.set_attribute("arion.consensus.latency_ms",
                                    result.latency_ms)
            run_span.set_attribute("arion.consensus.n_signals_fired",
                                    result.n_signals_fired)
        except Exception:
            pass

    logger.info(
        "consensus_extraction for %s: %d candidates → %d accept + %d arbiter + %d drop "
        "(signals fired: %d/%d, %dms)",
        doc_name,
        result.total_candidates,
        result.n_accept, result.n_arbiter, result.n_drop,
        result.n_signals_fired, len(signals),
        result.latency_ms,
    )
    return result
