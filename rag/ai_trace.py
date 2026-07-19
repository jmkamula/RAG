"""
AI call tracing — Wave 4b (2026-07-10).

One helper `log_llm_call(...)` — call at the tail of every LLM /
embedding invocation. Writes an `ai_call_log` row with tokens,
cost, latency, purpose, and provenance links. Silent failure on
DB error — never blocks the actual LLM call.

Two entry patterns:

    # Context-manager style (preferred — captures latency + errors)
    with trace_llm_call(purpose="extractor", model="claude-sonnet-4-6",
                         provider="anthropic", upload_id=upload_id) as trace:
        response = anthropic_call(...)
        trace.set_response(response.text, tokens_in=..., tokens_out=...)

    # Manual style (when the call is deep inside SDK closures)
    started_at = time.time()
    try:
        response = openai_call(...)
        log_llm_call(purpose="chat", model="gpt-4o", provider="openai",
                     latency_ms=int((time.time() - started_at) * 1000),
                     tokens_in=response.usage.prompt_tokens,
                     tokens_out=response.usage.completion_tokens,
                     prompt=full_prompt_text, response=response.choices[0].message.content,
                     tenant_id=tenant_id, session_id=session_id)
    except Exception as e:
        log_llm_call(purpose="chat", model="gpt-4o", provider="openai",
                     latency_ms=..., error_type=type(e).__name__, error_detail=str(e))
        raise

Pricing table below is a rolling snapshot — update when providers
publish new rates. cost_usd is best-effort; NULL when the model
isn't in the table.

Prompt + response are stored as SHA256 hashes plus a 500-char
preview. Full content is NOT persisted long-term. The hash lets
duplicate/cache-hit analysis; the preview supports diagnostics.
"""
from __future__ import annotations
import contextlib
import contextvars
import hashlib
import logging
import os
import time
from typing import Optional

logger = logging.getLogger(__name__)

# Context propagation — callsites don't need to thread tenant_id /
# upload_id / session_id / request_id through every layer. The
# request/pipeline entry sets these once; log_llm_call reads them
# via ContextVar as a fallback when the direct arg is None.
_tenant_ctx:  contextvars.ContextVar[Optional[str]] = contextvars.ContextVar("ai_trace.tenant_id",  default=None)
_upload_ctx:  contextvars.ContextVar[Optional[str]] = contextvars.ContextVar("ai_trace.upload_id",  default=None)
_session_ctx: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar("ai_trace.session_id", default=None)
_request_ctx: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar("ai_trace.request_id", default=None)


def set_trace_context(
    *,
    tenant_id:  Optional[str] = None,
    upload_id:  Optional[str] = None,
    session_id: Optional[str] = None,
    request_id: Optional[str] = None,
) -> tuple:
    """Stamp provenance IDs into the current async/thread context.
    Returned tuple of `Token`s can be passed back to `reset_trace_context`
    at request completion. Usually a fire-and-forget set at request
    entry — the context vars auto-scope to the async task."""
    return (
        _tenant_ctx.set(tenant_id)   if tenant_id  else None,
        _upload_ctx.set(upload_id)   if upload_id  else None,
        _session_ctx.set(session_id) if session_id else None,
        _request_ctx.set(request_id) if request_id else None,
    )


def reset_trace_context(tokens: tuple) -> None:
    """Restore ContextVars to their prior values. Optional — the
    async task boundary already isolates."""
    try:
        for cv, tok in zip(
            (_tenant_ctx, _upload_ctx, _session_ctx, _request_ctx),
            tokens,
        ):
            if tok is not None:
                cv.reset(tok)
    except Exception:
        pass


# Ship 6'.e: read-only accessors so downstream log writers can pull
# the ambient session_id / request_id (stamped at request entry by
# `set_trace_context`) without threading them through function
# signatures. `log_llm_call` already reads these; the chat-log and
# consensus-log writers now do too.

def current_session_id() -> Optional[str]:
    return _session_ctx.get()


def current_request_id() -> Optional[str]:
    return _request_ctx.get()


def current_tenant_id() -> Optional[str]:
    return _tenant_ctx.get()

# Per-1M-token USD pricing snapshot 2026-07-10.
# Update as providers publish new rates. Keys are normalized model
# names (lowercase, colon-stripped). Sources: openai.com/pricing,
# anthropic.com/pricing.
_PRICING_USD_PER_M = {
    # OpenAI
    "gpt-4o":                   {"in":  2.50, "out": 10.00},
    "gpt-4o-mini":              {"in":  0.15, "out":  0.60},
    "gpt-4-turbo":              {"in": 10.00, "out": 30.00},
    "text-embedding-3-small":   {"in":  0.02, "out":  0.00},
    "text-embedding-3-large":   {"in":  0.13, "out":  0.00},

    # Anthropic
    "claude-opus-4-7":          {"in": 15.00, "out": 75.00},
    "claude-sonnet-4-6":        {"in":  3.00, "out": 15.00},
    "claude-haiku-4-5":         {"in":  0.80, "out":  4.00},
    "claude-haiku-4-5-20251001":{"in":  0.80, "out":  4.00},
}

# Preview cap — first N chars of prompt / response stored.
_PREVIEW_CAP = 500


def _norm_model(model: str) -> str:
    """Normalize model name for pricing lookup."""
    return (model or "").lower().strip()


def _compute_cost_usd(model: str, tokens_in: Optional[int], tokens_out: Optional[int]) -> Optional[float]:
    """Best-effort USD cost. Returns None when the model isn't in the
    pricing table — write the row anyway, just without cost."""
    if tokens_in is None and tokens_out is None:
        return None
    price = _PRICING_USD_PER_M.get(_norm_model(model))
    if not price:
        return None
    cost = 0.0
    if tokens_in:
        cost += (tokens_in  / 1_000_000.0) * price["in"]
    if tokens_out:
        cost += (tokens_out / 1_000_000.0) * price["out"]
    return round(cost, 6)


def _sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8", errors="replace")).hexdigest() if text else ""


def _preview(text: Optional[str]) -> Optional[str]:
    if not text:
        return None
    return text[:_PREVIEW_CAP]


def log_llm_call(
    *,
    purpose:       str,
    provider:      str,
    model:         str,
    latency_ms:    Optional[int]   = None,
    tokens_in:     Optional[int]   = None,
    tokens_out:    Optional[int]   = None,
    prompt:        Optional[str]   = None,
    response:      Optional[str]   = None,
    error_type:    Optional[str]   = None,
    error_detail:  Optional[str]   = None,
    tenant_id:     Optional[str]   = None,
    upload_id:     Optional[str]   = None,
    session_id:    Optional[str]   = None,
    request_id:    Optional[str]   = None,
    metadata:      Optional[dict]  = None,
    pg_conn                        = None,
) -> None:
    """Persist one ai_call_log row. Silent failure — never raises.

    When `pg_conn` is None, opens a short-lived connection from
    the env (host/user/db from PGHOST/PGUSER/PGDATABASE or defaults
    matching the app). This lets deep-call-stack sites log without
    threading a pool through every layer.
    """
    # Fill in tenant/upload/session/request from ContextVars when the
    # caller didn't pass them explicitly.
    if tenant_id is None:
        tenant_id = _tenant_ctx.get()
    if upload_id is None:
        upload_id = _upload_ctx.get()
    if session_id is None:
        session_id = _session_ctx.get()
    if request_id is None:
        request_id = _request_ctx.get()
    try:
        import psycopg2
        import json as _json
        if pg_conn is None:
            pg_conn = psycopg2.connect(
                host    = os.getenv("PGHOST", "127.0.0.1"),
                dbname  = os.getenv("PGDATABASE", "arioncomply_compliance"),
                user    = os.getenv("PGUSER", "arioncomply_app"),
                password= os.getenv("PGPASSWORD", ""),
            )
            _owned = True
        else:
            _owned = False
        cost = _compute_cost_usd(model, tokens_in, tokens_out)
        with pg_conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO ai_call_log (
                    tenant_id, purpose, provider, model,
                    latency_ms, tokens_in, tokens_out, cost_usd,
                    prompt_hash, prompt_preview,
                    response_hash, response_preview,
                    error_type, error_detail,
                    upload_id, session_id, request_id,
                    metadata,
                    purge_after
                ) VALUES (
                    %s::uuid, %s, %s, %s,
                    %s, %s, %s, %s,
                    %s, %s,
                    %s, %s,
                    %s, %s,
                    %s::uuid, %s, %s,
                    %s::jsonb,
                    NOW() + INTERVAL '365 days'
                )
                """,
                (
                    tenant_id, purpose, provider, model,
                    latency_ms, tokens_in, tokens_out, cost,
                    _sha256(prompt or ""), _preview(prompt),
                    _sha256(response or ""), _preview(response),
                    error_type, error_detail,
                    upload_id, session_id, request_id,
                    _json.dumps(metadata or {}),
                ),
            )
        if _owned:
            pg_conn.commit()
            pg_conn.close()
    except Exception as e:
        logger.warning("ai_trace.log_llm_call failed: %s", e)


class _TraceContext:
    """Context object returned by trace_llm_call. Caller sets fields
    inside the with-block; log_llm_call fires on __exit__."""
    def __init__(self, kwargs: dict):
        self._kwargs   = kwargs
        self._started  = time.time()
        self._response = None
        self._tokens_in  = None
        self._tokens_out = None

    def set_response(
        self,
        response:  Optional[str] = None,
        tokens_in: Optional[int] = None,
        tokens_out: Optional[int] = None,
    ) -> None:
        self._response = response
        if tokens_in is not None:
            self._tokens_in = tokens_in
        if tokens_out is not None:
            self._tokens_out = tokens_out


@contextlib.contextmanager
def trace_llm_call(**kwargs):
    """Context manager. Wraps an LLM call; captures latency and
    exceptions automatically. Caller fills in response + token counts
    via `.set_response(...)`."""
    ctx = _TraceContext(kwargs)
    err_type: Optional[str]   = None
    err_detail: Optional[str] = None
    try:
        yield ctx
    except Exception as e:
        err_type   = type(e).__name__
        err_detail = str(e)[:500]
        raise
    finally:
        latency_ms = int((time.time() - ctx._started) * 1000)
        log_llm_call(
            latency_ms   = latency_ms,
            tokens_in    = ctx._tokens_in,
            tokens_out   = ctx._tokens_out,
            response     = ctx._response,
            error_type   = err_type,
            error_detail = err_detail,
            **ctx._kwargs,
        )
