"""
POST /api/external/v1/query — structured RAG answer.

Same underlying pipeline as `/api/v1/chat` (internal UI) but with:
  * OpenAPI-typed request + response models (Pydantic)
  * Structured citations array (ref + posture + standard) instead of
    a bare list of ref strings
  * request_id, session_id, latency_ms, needs_clarification surfaced
    as first-class fields

The LangGraph invocation (arion_graph) is shared with the internal
chat endpoint; only response shaping differs. If the internal
handler ever gets refactored into a helper, this file should
adopt it — for now duplication is contained to a small block.
"""
from __future__ import annotations

import asyncio
import contextvars as _cv
import logging
import time
import uuid as _uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field

from rag.external.auth import external_key_with_scope

logger = logging.getLogger(__name__)

router = APIRouter()


# ── Request / response models ─────────────────────────────────────────

class QueryRequest(BaseModel):
    question: str = Field(
        ...,
        min_length  = 1,
        max_length  = 4000,
        description = "Natural-language question to submit to the RAG pipeline. "
                      "Same shape as the internal chat endpoint.",
    )
    session_id: Optional[str] = Field(
        None,
        max_length  = 64,
        description = "Optional session id for multi-turn conversations. "
                      "Server generates one when omitted. Must be "
                      "letters/digits/hyphens/underscores, up to 64 chars.",
    )


class Citation(BaseModel):
    ref:      str                = Field(..., description="Control ref (e.g. `A.5.18`) or article ref (`Art.32`).")
    standard: Optional[str]      = Field(None, description="Standard id, e.g. `ISO27001:2022`.")
    posture:  Optional[str]      = Field(None, description="Live posture finding for this ref, if the tenant has one (NC / OFI / Comply / N/A).")


class QueryResponse(BaseModel):
    answer:                 str            = Field(..., description="The RAG-composed answer prose.")
    question_type:          Optional[str]  = Field(None, description="Classifier's intent decision (`gap_analysis`, `implementation`, `posture_check`, ...).")
    citations:              list[Citation] = Field(default_factory=list, description="Refs cited in the answer, enriched with live posture when available.")
    session_id:             str            = Field(..., description="Session id for this conversation thread. Echo of the input or a server-generated one.")
    request_id:             str            = Field(..., description="Correlates with server logs. Same value as `X-Trace-Id` request header (if provided) or a generated UUID.")
    latency_ms:             int            = Field(..., description="End-to-end latency for this query.")
    needs_clarification:    bool           = Field(False, description="True when the pipeline needs a follow-up before answering. `answer` will contain the clarification prompt.")
    clarification_question: Optional[str]  = Field(None, description="When `needs_clarification` is true, this mirrors the clarification prompt as a separate field for programmatic consumers.")


# ── Handler ───────────────────────────────────────────────────────────

_SESSION_ID_RE = None


def _validate_session_id_shape(session_id: str) -> bool:
    # Reuse the internal validator — imported lazily to avoid import
    # cycles with api_server.
    from api_server import validate_session_id_shape
    return validate_session_id_shape(session_id)


def _build_thread_id(tenant_id: str, session_id: str) -> str:
    from api_server import build_thread_id
    return build_thread_id(tenant_id, session_id)


@router.post("/query",
             response_model = QueryResponse,
             summary        = "Ask the RAG a compliance question")
async def post_query(
    body:     QueryRequest,
    request:  Request,
    key       = Depends(external_key_with_scope("external:query")),
):
    """Submit a compliance question to the RAG pipeline and receive a
    structured answer with typed citations and posture context.

    Multi-turn support: pass the previous response's `session_id`
    to continue the same conversation thread. The server will
    persist state via the LangGraph checkpointer.
    """
    if not request.app.state.arion_graph:
        raise HTTPException(
            status_code = 503,
            detail      = "The answer service is unavailable right now. Please try again in a moment.",
        )

    from rag.arion_state import make_initial_state
    from rag.ai_trace import set_trace_context

    t_start    = time.time()
    trace_id   = request.state.trace_id
    session_id = body.session_id or f"ext_{_uuid.uuid4().hex[:8]}"

    if not _validate_session_id_shape(session_id):
        raise HTTPException(
            status_code = 400,
            detail      = "The session_id contains characters we don't support. "
                          "Use letters, digits, hyphens, or underscores (max 64).",
        )

    set_trace_context(
        tenant_id  = key.tenant_id,
        session_id = session_id,
        request_id = trace_id,
    )
    thread_id = _build_thread_id(key.tenant_id, session_id)

    # Refresh tenant context (cached)
    try:
        cache  = request.app.state.tenant_cache
        ctx    = cache.load(key.tenant_id)
        tenant = ctx.profile
    except Exception as e:
        logger.warning(f"tenant context refresh failed: {e} — using cached / None")
        tenant = None

    if tenant is None:
        raise HTTPException(
            status_code = 503,
            detail      = "Tenant context unavailable. Please try again in a moment.",
        )

    try:
        cfg   = {"configurable": {"thread_id": thread_id}}
        graph = request.app.state.arion_graph

        prior = await asyncio.get_event_loop().run_in_executor(
            None, lambda: graph.get_state(cfg),
        )
        has_prior = bool(prior and getattr(prior, "values", None))
        state = ({"query": body.question}
                 if has_prior
                 else make_initial_state(tenant, query=body.question))

        _ctx = _cv.copy_context()
        result = await asyncio.get_event_loop().run_in_executor(
            None,
            lambda: _ctx.run(graph.invoke, state, cfg),
        )
    except Exception as e:
        logger.error(f"external /query pipeline error: {e}", exc_info=True)
        raise HTTPException(
            status_code = 500,
            detail      = "Something went wrong composing your answer. Please try again in a moment.",
        )

    answer     = result.get("answer_text", "") or result.get("answer", "")
    qtype      = result.get("intent_type") or result.get("question_type")
    if hasattr(qtype, "value"):
        qtype = qtype.value
    refs       = result.get("cited_refs") or []
    posture_by = result.get("posture_findings") or {}
    needs_clarif = bool(result.get("needs_clarif"))
    clarif_q     = result.get("clarif_question") or None

    if not answer and needs_clarif and clarif_q:
        answer = clarif_q

    # Build enriched citations. posture_findings is dict-shaped —
    # keyed by ref (or ref-composite). Try direct hit first, then
    # fall back to leniently matching a ref suffix.
    citations = []
    for ref in refs if isinstance(refs, list) else []:
        posture_entry = posture_by.get(ref) if isinstance(posture_by, dict) else None
        finding  = None
        standard = None
        if isinstance(posture_entry, dict):
            finding  = posture_entry.get("finding") or posture_entry.get("posture")
            standard = posture_entry.get("standard_id")
        citations.append(Citation(
            ref      = str(ref),
            standard = standard,
            posture  = finding,
        ))

    latency_ms = int((time.time() - t_start) * 1000)

    return QueryResponse(
        answer                  = answer,
        question_type           = qtype,
        citations               = citations,
        session_id              = session_id,
        request_id              = trace_id,
        latency_ms              = latency_ms,
        needs_clarification     = needs_clarif,
        clarification_question  = clarif_q,
    )
