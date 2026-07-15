"""
Freeform payload builder — fallback for queries that don't fit a
taxonomy. Ship 2's explicit non-goal is to scaffold freeform prose;
freeform queries continue to flow through today's rank_and_answer
LLM path, with the payload as loose structured context.

Reasons a query lands in freeform:
  - question_type is None / unknown (consensus insufficient)
  - question_type has no dedicated builder yet (during migration)
  - explicit request for open-ended discussion
"""
from __future__ import annotations

import time
from typing import Optional

from rag.answer.types import FreeformPayload, RefRecord


def build(
    intent,
    tenant_context,
    resolver,
    neo_driver=None,
    chroma_retriever=None,
) -> FreeformPayload:
    """Build a FreeformPayload from whatever data we have. Never
    fails — the fallback lane is designed to always produce something
    the downstream can pass through."""
    t0 = time.time()

    query          = getattr(intent, "raw_query", "") or ""
    question_type  = "unknown"
    if intent is not None and getattr(intent, "question_type", None) is not None:
        qt = intent.question_type
        question_type = getattr(qt, "value", str(qt)).lower()

    tenant_id      = ""
    tenant_name    = ""
    frameworks     = []
    if tenant_context is not None:
        tenant_id   = str(getattr(tenant_context, "tenant_id", "") or "")
        tenant_name = str(getattr(tenant_context, "tenant_name", "") or "")
        scope       = getattr(tenant_context, "scope", None)
        if scope is not None:
            frameworks = list(getattr(scope, "queryable_standards", []) or [])

    subject_refs: list[RefRecord] = []
    if intent is not None:
        for r in (getattr(intent, "cited_refs", []) or []):
            if not r:
                continue
            subject_refs.append(RefRecord(
                ref       = r,
                framework = _infer_framework(r),
                title     = "",
                node_id   = "",
            ))

    reason = "no dedicated builder for this taxonomy"

    payload = FreeformPayload(
        question_type      = question_type,
        query              = query,
        tenant_id          = tenant_id,
        tenant_name        = tenant_name,
        framework_primary  = _dominant_framework([r.framework for r in subject_refs])
                              or (frameworks[0] if frameworks else ""),
        frameworks_scope   = frameworks,
        subject_refs       = subject_refs,
        signals_provenance = ["freeform_fallback"],
        retrieved_nodes    = [],
        reason_fallback    = reason,
        build_latency_ms   = int((time.time() - t0) * 1000),
    )
    return payload


def _infer_framework(ref: str) -> str:
    """Best-effort framework inference from ref shape."""
    if ref.startswith("Art."):
        return "GDPR:2016/679"
    if ref.startswith("B."):
        return "ISO27701:2019"
    if ref.startswith("A.7.") and ref.count(".") >= 3:
        return "ISO27701:2019"
    if ref.startswith("A."):
        return "ISO27001:2022"
    if "." in ref and ref.split(".")[0].isdigit():
        first = int(ref.split(".")[0])
        if 4 <= first <= 10:
            return "ISO27001:2022"
    return ""


def _dominant_framework(fws: list[str]) -> Optional[str]:
    """Majority framework across a list, else None on tie or empty."""
    counts: dict[str, int] = {}
    for f in fws:
        if f:
            counts[f] = counts.get(f, 0) + 1
    if not counts:
        return None
    ordered = sorted(counts.items(), key=lambda kv: kv[1], reverse=True)
    if len(ordered) == 1 or ordered[0][1] > ordered[1][1]:
        return ordered[0][0]
    return None
