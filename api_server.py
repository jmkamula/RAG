"""
ArionComply — Production API Server
Exposes the full platform via HTTP:

  /health                              — service health
  /api/v1/chat          POST           — RAG pipeline (question → answer)
  /api/v1/documents     POST /upload   — document intake (async)
  /api/v1/documents     GET  /         — list documents
  /api/v1/documents     GET  /{id}/status — intake progress
  /api/v1/review-queue  GET  /         — HITL pending confirmations
  /api/v1/posture/{id}  POST /confirm  — confirm a finding
  /api/v1/posture/{id}  POST /override — override a finding
  /api/v1/posture/bulk-confirm POST    — bulk confirm
  /api/v1/posture       GET  /         — full posture summary

Auth:   X-API-Key header → api_keys table → tenant_id + user_id
Port:   8080
Run:    PYTHONPATH=/data/arioncomply python3 api_server.py
"""
from __future__ import annotations

import asyncio
import hashlib
import logging
import os
import sys
import time
import uuid
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Optional

import psycopg2
import psycopg2.pool
import uvicorn
from fastapi import (
    BackgroundTasks,
    Depends,
    FastAPI,
    File,
    Form,
    Header,
    HTTPException,
    Request,
    UploadFile,
    status,
)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

# Ship 2'.k: FastAPI-side ID-shape validators. Every path param that
# hits a Postgres ::uuid cast is typed via one of the *IdParam aliases
# below — bad shapes return 422 at the door instead of 500 from the
# cast. See rag/api_types.py + [[ship-2-prime-i-id-discipline...]].

# ── Path setup ────────────────────────────────────────────────────────────────
_ROOT = Path(__file__).parent
sys.path.insert(0, str(_ROOT))

# Ship 2'.k: FastAPI path-param types. Imported once at module load
# (after sys.path is set), used across every endpoint below.
from rag.api_types import (
    PostureIdParam, ProposalIdParam, OverrideIdParam, UploadIdParam,
    SystemIdParam, NotifIdParam, ImplicationIdParam, SeriesIdParam,
    ControlRefParam, LeafIdParam, CascadeKindParam, FactKeyParam,
    RiskIdParam,
    build_thread_id, validate_session_id_shape,
)
from fastapi import Query as FastAPIQuery

try:
    from dotenv import load_dotenv
    load_dotenv(_ROOT / ".env")
except ImportError:
    pass

logging.basicConfig(
    format  = "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt = "%H:%M:%S",
    level   = logging.INFO,
)
logger = logging.getLogger("arioncomply.api")

# ── Config ────────────────────────────────────────────────────────────────────
DATABASE_URL   = os.getenv("DATABASE_URL", "")
UPLOAD_DIR     = Path(os.getenv("UPLOAD_DIR", "/data/uploads"))
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
API_PORT       = int(os.getenv("API_PORT", "8080"))
CORS_ORIGINS   = os.getenv("CORS_ORIGINS", "*").split(",")
MAX_UPLOAD_MB  = int(os.getenv("MAX_UPLOAD_MB", "50"))

SUPPORTED_EXTENSIONS = {
    ".pdf", ".docx", ".doc", ".xlsx", ".xlsm", ".xls", ".txt", ".csv", ".md"
}


# =============================================================================
# LIFESPAN — startup / shutdown
# =============================================================================

class _PrePingPool:
    """Wraps psycopg2.pool.ThreadedConnectionPool with a per-checkout
    `SELECT 1` ping. Postgres reaps idle TCP connections (cloud
    middleboxes, idle_in_transaction_session_timeout, etc.); the
    base pool happily returns them. First query then raises
    `OperationalError: the connection is closed`.

    Pre-ping eliminates that by validating each conn before handing
    it out. Stale conns are closed and dropped from the pool; the
    pool refills lazily. ~1-2ms per checkout — acceptable for the
    request volume.

    Drop-in interface (getconn / putconn / closeall) so the rest of
    the codebase uses it unchanged.
    """

    def __init__(self, minconn, maxconn, dsn):
        self._pool = psycopg2.pool.ThreadedConnectionPool(minconn, maxconn, dsn)
        self.maxconn = maxconn

    def getconn(self, key=None):
        last_err = None
        # Bounded retry: in the worst case all pool conns are stale and
        # we replace them all. The pool auto-creates new ones to refill.
        for _ in range(max(self.maxconn, 2)):
            conn = self._pool.getconn(key)
            try:
                if getattr(conn, "closed", 0):
                    raise psycopg2.OperationalError("conn.closed is truthy")
                with conn.cursor() as cur:
                    cur.execute("SELECT 1")
                return conn
            except (psycopg2.OperationalError, psycopg2.InterfaceError) as e:
                last_err = e
                logger.warning(f"pg_pool: discarding stale connection ({type(e).__name__})")
                try:
                    self._pool.putconn(conn, close=True)
                except Exception:
                    pass
        raise psycopg2.OperationalError(
            f"pg_pool: all connections stale after retry: {last_err}"
        )

    def putconn(self, conn, key=None, close=False):
        return self._pool.putconn(conn, key=key, close=close)

    def closeall(self):
        return self._pool.closeall()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialise shared resources once at startup."""
    logger.info("ArionComply API starting up...")
    # Ship 48'.c — capture boot time for /admin/deployment/status uptime.
    app.state.started_at = time.time()

    # ── Postgres connection pool ──────────────────────────────────────────────
    try:
        app.state.pg_pool = _PrePingPool(
            minconn = 2,
            maxconn = 10,
            dsn     = DATABASE_URL,
        )
        logger.info("✓ Postgres pool ready (pre-ping)")
    except Exception as e:
        logger.error(f"✗ Postgres pool failed: {e}")
        app.state.pg_pool = None

    # ── Tenant context cache ──────────────────────────────────────────────────
    try:
        from rag.tenant_context import TenantContextCache
        app.state.tenant_cache = TenantContextCache.from_env(ttl_seconds=60)
        logger.info("✓ Tenant cache ready")
    except Exception as e:
        logger.error(f"✗ Tenant cache failed: {e}")
        app.state.tenant_cache = None

    # ── RAG pipeline (warm on startup) ───────────────────────────────────────
    try:
        from rag.arion_graph       import build_arion_graph
        from rag.orchestrator      import OrchestratorConfig
        from rag.context_assembler import ContextAssembler
        from rag.graph_expander    import GraphExpander
        from rag.llm_answer        import LLMAnswer
        from rag.classifier        import QueryClassifier
        from vector.retriever      import VectorRetriever
        from rag.arion_graph import get_checkpointer, get_async_checkpointer

        cfg       = OrchestratorConfig()
        retriever = VectorRetriever(
            chroma_host = cfg.chroma_host,
            chroma_port = cfg.chroma_port,
        )
        expander = GraphExpander(
            neo4j_uri      = cfg.neo4j_uri,
            neo4j_user     = cfg.neo4j_user,
            neo4j_password = cfg.neo4j_password,
            retriever      = retriever,
            pg_pool        = app.state.pg_pool,   # for incident_obligations reads
        )

        # Load tenant context for pipeline warm-up
        tenant_id = "00000000-0000-0000-0000-000000000001"
        ctx = app.state.tenant_cache.load(tenant_id) if app.state.tenant_cache else None
        tenant  = ctx.profile  if ctx else None
        posture = ctx.posture  if ctx else {}

        app.state.arion_graph = build_arion_graph(
            tenant      = tenant,
            retriever   = retriever,
            expander    = expander,
            assembler   = ContextAssembler(tenant_profile=tenant),
            llm         = LLMAnswer(),
            classifier  = QueryClassifier(
                tenant_profile = tenant,
                retriever      = retriever,
            ),
            posture       = posture,
            checkpointer  = get_checkpointer(),
        )
        # Async graph for streaming — AsyncPostgresSaver for session persistence
        async_checkpointer = await get_async_checkpointer()
        app.state.arion_graph_async = build_arion_graph(
            tenant      = tenant,
            retriever   = retriever,
            expander    = expander,
            assembler   = ContextAssembler(tenant_profile=tenant),
            llm         = LLMAnswer(),
            classifier  = QueryClassifier(
                tenant_profile = tenant,
                retriever      = retriever,
            ),
            posture       = posture,
            checkpointer  = async_checkpointer,
        )
        app.state.retriever     = retriever
        app.state.expander      = expander
        app.state.rag_cfg       = cfg
        logger.info(f"✓ RAG pipeline ready ({len(posture)} posture controls)")
    except Exception as e:
        logger.error(f"✗ RAG pipeline failed: {e}", exc_info=True)
        app.state.arion_graph = None

    yield

    # ── Shutdown ──────────────────────────────────────────────────────────────
    logger.info("ArionComply API shutting down...")
    if app.state.pg_pool:
        app.state.pg_pool.closeall()
    logger.info("✓ Postgres pool closed")


# =============================================================================
# APP
# =============================================================================

app = FastAPI(
    title       = "ArionComply API",
    description = "Compliance RAG platform — chat, document intake, HITL posture management",
    version     = "1.0.0",
    lifespan    = lifespan,
)

# ── OpenTelemetry bootstrap (Ship 44) ────────────────────────────────────────
# Register OTel + FastAPI instrumentation BEFORE middleware + routes so that
# every incoming request gets a server-kind span as trace root. Skipping the
# bootstrap step (OTEL_ENABLED != 1) is a no-op.
try:
    from rag.telemetry import bootstrap_telemetry as _bootstrap_telemetry
    _bootstrap_telemetry(fastapi_app=app)
except Exception as _e:
    logger.warning(f"OTel bootstrap at import failed (non-fatal): {_e}")

# Serve static UI files
_static = Path("/data/arioncomply/static")
_static.mkdir(parents=True, exist_ok=True)
from fastapi.responses import RedirectResponse, FileResponse

# Explicit SPA route MUST be defined BEFORE the StaticFiles mount at
# /ui — otherwise the mount catches the request first. Explicit
# no-cache header so browsers don't serve stale JS after we ship UI
# changes.
@app.get("/ui/arioncomply.html", include_in_schema=False)
async def _serve_spa():
    return FileResponse(
        str(_static / "arioncomply.html"),
        media_type = "text/html; charset=utf-8",
        headers    = {
            "Cache-Control": "no-cache, must-revalidate",
            "Pragma":        "no-cache",
        },
    )

app.mount("/ui", StaticFiles(directory=str(_static), html=True), name="ui")

# Root redirect: chat emits deep-links like `#dashboard?control=A.5.15`
# and legacy deep-links used a leading slash (`/#dashboard?...`) that
# resolved to `http://host:8080/` before the hash. Without this
# handler, that path 404s. Preserve the browser's hash by 302-ing to
# the SPA — the hash never reaches the server, so it survives the
# redirect intact.
@app.get("/", include_in_schema=False)
async def _root_redirect():
    return RedirectResponse(url="/ui/arioncomply.html", status_code=302)

app.add_middleware(
    CORSMiddleware,
    allow_origins     = CORS_ORIGINS,
    allow_credentials = True,
    allow_methods     = ["*"],
    allow_headers     = ["*"],
)


# =============================================================================
# DB HELPERS
# =============================================================================

def get_conn(request: Request):
    """Get a connection from the pool. Always close after use."""
    pool = request.app.state.pg_pool
    if not pool:
        raise HTTPException(503, "Database unavailable")
    conn = pool.getconn()
    try:
        yield conn
    finally:
        pool.putconn(conn)


def set_session(conn, tenant_id: str, user_id: Optional[str] = None):
    """Set RLS session variables on connection."""
    with conn.cursor() as cur:
        cur.execute("SELECT set_config('app.tenant_id', %s, TRUE)", (tenant_id,))
        if user_id:
            cur.execute("SELECT set_config('app.user_id', %s, TRUE)", (user_id,))


# =============================================================================
# AUTH
# =============================================================================

class APIKeyInfo(BaseModel):
    key_id:    str
    tenant_id: str
    user_id:   str
    scopes:    list[str]


def _hash_key(raw_key: str) -> str:
    return hashlib.sha256(raw_key.encode()).hexdigest()


async def require_api_key(
    request:   Request,
    x_api_key: Optional[str] = Header(default=None),
) -> APIKeyInfo:
    """Validate X-API-Key header. Returns key metadata."""
    if not x_api_key:
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail      = "X-API-Key header required",
        )

    key_hash = _hash_key(x_api_key)
    pool     = request.app.state.pg_pool
    if not pool:
        raise HTTPException(503, "Database unavailable")

    conn = pool.getconn()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT id, tenant_id, user_id, scopes
                FROM api_keys
                WHERE key_hash  = %s
                  AND is_active = TRUE
                  AND (expires_at IS NULL OR expires_at > NOW())
            """, (key_hash,))
            row = cur.fetchone()
            if not row:
                raise HTTPException(
                    status_code = status.HTTP_401_UNAUTHORIZED,
                    detail      = "Invalid or expired API key",
                )
            key_id, tenant_id, user_id, scopes = row

            # Update last_used_at (best effort)
            try:
                cur.execute(
                    "UPDATE api_keys SET last_used_at = NOW() WHERE id = %s",
                    (str(key_id),)
                )
                conn.commit()
            except Exception:
                conn.rollback()

        return APIKeyInfo(
            key_id    = str(key_id),
            tenant_id = str(tenant_id),
            user_id   = str(user_id),
            scopes    = scopes or [],
        )
    finally:
        pool.putconn(conn)


def require_scope(scope: str):
    """Dependency factory — checks key has required scope."""
    async def _check(key_info: APIKeyInfo = Depends(require_api_key)) -> APIKeyInfo:
        if scope not in key_info.scopes:
            raise HTTPException(
                status_code = status.HTTP_403_FORBIDDEN,
                detail      = f"API key missing scope: {scope}",
            )
        return key_info
    return _check


# =============================================================================
# REQUEST MIDDLEWARE — trace_id on every request
# =============================================================================

@app.middleware("http")
async def add_trace_id(request: Request, call_next):
    trace_id = request.headers.get("X-Trace-Id", str(uuid.uuid4()))
    request.state.trace_id = trace_id

    # Ship 44'.b — wrap request handling in a server-kind OTel span so
    # every downstream span (LangGraph nodes, DB queries, LLM calls) is
    # a child of this request. Without this wrap, downstream spans
    # become orphan single-span traces in Jaeger. This coexists with
    # OpenTelemetryMiddleware — the ASGI middleware runs deeper but
    # doesn't produce server spans on Starlette 1.x + FastAPI 0.140.
    try:
        from opentelemetry import trace as _otel_trace
        _tracer = _otel_trace.get_tracer("arioncomply.request")
        span_ctx = _tracer.start_as_current_span(
            f"{request.method} {request.url.path}",
            kind=_otel_trace.SpanKind.SERVER,
        )
    except Exception:
        span_ctx = None

    if span_ctx is not None:
        with span_ctx as span:
            try:
                span.set_attribute("http.method", request.method)
                span.set_attribute("http.route", request.url.path)
                span.set_attribute("http.scheme", request.url.scheme)
                span.set_attribute("arion.trace_id", trace_id)
                if "x-tenant-id" in request.headers:
                    span.set_attribute("arion.tenant_id", request.headers["x-tenant-id"])
            except Exception:
                pass
            response = await call_next(request)
            try:
                span.set_attribute("http.status_code", response.status_code)
            except Exception:
                pass
    else:
        response = await call_next(request)

    response.headers["X-Trace-Id"] = trace_id
    return response


# =============================================================================
# HEALTH
# =============================================================================

@app.get("/health", tags=["system"])
async def health(request: Request):
    """Service health check — checks all dependencies."""
    checks = {}

    # Postgres
    try:
        pool = request.app.state.pg_pool
        conn = pool.getconn()
        with conn.cursor() as cur:
            cur.execute("SELECT 1")
        pool.putconn(conn)
        checks["postgres"] = "ok"
    except Exception as e:
        checks["postgres"] = f"error: {e}"

    # Neo4j
    try:
        expander = getattr(request.app.state, "expander", None)
        if expander:
            checks["neo4j"] = "ok"
        else:
            checks["neo4j"] = "not initialised"
    except Exception as e:
        checks["neo4j"] = f"error: {e}"

    # ChromaDB
    try:
        cfg = getattr(request.app.state, "rag_cfg", None)
        if cfg:
            import httpx
            async with httpx.AsyncClient() as client:
                r = await client.get(
                    f"http://{cfg.chroma_host}:{cfg.chroma_port}/api/v2/heartbeat",
                    timeout=2.0,
                )
            checks["chromadb"] = "ok" if r.status_code == 200 else f"status {r.status_code}"
        else:
            checks["chromadb"] = "not initialised"
    except Exception as e:
        checks["chromadb"] = f"error: {e}"

    # RAG pipeline
    checks["rag_pipeline"] = "ok" if request.app.state.arion_graph else "not initialised"

    overall = "ok" if all(v == "ok" for v in checks.values()) else "degraded"
    return {
        "status":  overall,
        "checks":  checks,
        "version": "1.0.0",
    }


# =============================================================================
# CHAT ROUTER
# =============================================================================

class ChatRequest(BaseModel):
    question:   str
    session_id: Optional[str] = None


class ChatResponse(BaseModel):
    answer:     str
    type:       Optional[str] = None
    refs:       list[str]     = []
    trace_id:   str
    latency_ms: int
    # Tier-4 structured templates block for action-oriented queries
    # that cite NC/OFI controls. Payload shape:
    # rag/templates/answer_footer.py:build_templates_block.
    templates:  Optional[dict] = None
    # Ship 18'.b — structured answer payload (intro + actions[] +
    # related[]). Present when the case-file flow parsed the LLM's
    # JSON output successfully; absent when the LLM fell back to prose
    # (frontend falls back to `answer` in that case). Schema:
    # rag/casefile/answer_schema.py::StructuredAnswer.
    answer_structured: Optional[dict] = None


@app.post("/api/v1/chat", response_model=ChatResponse, tags=["chat"])
async def chat(
    body:     ChatRequest,
    request:  Request,
    key_info: APIKeyInfo = Depends(require_scope("chat")),
):
    """
    Submit a compliance question to the RAG pipeline.
    Returns a grounded answer with control references.
    """
    if not request.app.state.arion_graph:
        raise HTTPException(
            503,
            "The answer service is unavailable right now. Please try "
            "again in a moment."
        )

    from rag.arion_state import make_initial_state
    from rag.tenant_context import TenantContextCache
    from rag.ai_trace import set_trace_context

    t_start    = time.time()
    trace_id   = request.state.trace_id
    session_id = body.session_id or f"api_{uuid.uuid4().hex[:8]}"

    # Ship 2'.l: validate session_id shape at the boundary. Malformed
    # ids (SQL fragments, path traversal bytes, oversized strings)
    # get rejected here before they land in the LangGraph checkpoint
    # key. Auto-generated ids always pass; only client-supplied ones
    # are at risk.
    if not validate_session_id_shape(session_id):
        raise HTTPException(
            400,
            "The session id contains characters we don't support. "
            "Please use letters, digits, hyphens, or underscores "
            "(up to 64 characters).",
        )

    # Wave 4c: stamp tenant + session + request into the ai_trace ContextVars
    # so every LLM call fired during this handler auto-tags with them.
    set_trace_context(
        tenant_id  = key_info.tenant_id,
        session_id = session_id,
        request_id = trace_id,
    )
    # Ship 2'.l: FULL tenant UUID (was tenant_id[:8]) — kills the 2^32
    # collision surface. See rag/api_types.build_thread_id.
    thread_id = build_thread_id(key_info.tenant_id, session_id)

    # Refresh tenant context (cached, TTL=60s)
    try:
        cache  = request.app.state.tenant_cache
        ctx    = cache.load(key_info.tenant_id)
        tenant = ctx.profile
    except Exception as e:
        logger.warning(f"Tenant context refresh failed: {e} — using cached")
        tenant = None

    try:
        cfg    = {"configurable": {"thread_id": thread_id}}
        # Use full initial state only on the FIRST turn for this thread.
        # On follow-ups, pass just the new query so the checkpointer's
        # persisted state (turn_count, needs_clarif, taxonomy_options_map,
        # etc.) is preserved instead of being overwritten by defaults.
        graph     = request.app.state.arion_graph
        prior     = await asyncio.get_event_loop().run_in_executor(
            None, lambda: graph.get_state(cfg)
        )
        has_prior = bool(prior and getattr(prior, "values", None))
        state     = ({"query": body.question}
                     if has_prior
                     else make_initial_state(tenant, query=body.question))
        # ContextVar propagation into the executor thread — asyncio's
        # run_in_executor doesn't copy the current async context by
        # default, so ai_trace ContextVars (tenant_id, session_id,
        # request_id) would evaluate to None inside graph.invoke.
        # Use copy_context().run(...) to carry them across.
        import contextvars as _cv
        _ctx = _cv.copy_context()
        result = await asyncio.get_event_loop().run_in_executor(
            None,
            lambda: _ctx.run(graph.invoke, state, cfg),
        )

        answer     = result.get("answer_text", "") or result.get("answer", "")
        # question_type isn't in the ArionState schema (only intent_type
        # is), so LangGraph strips it from graph.invoke() output.
        # intent_type is set to the same value by build_answer_envelope
        # + every chat short-circuit; use it as the primary read.
        qtype      = result.get("intent_type") or result.get("question_type")
        refs       = result.get("cited_refs", [])

        # When pipeline needs clarification, surface the question to the user
        if not answer and result.get("needs_clarif") and result.get("clarif_question"):
            answer = result.get("clarif_question", "")
            qtype  = "clarification"
            refs   = []
        latency_ms = int((time.time() - t_start) * 1000)

        if hasattr(qtype, "value"):
            qtype = qtype.value

        return ChatResponse(
            answer            = answer,
            type              = qtype,
            refs              = refs if isinstance(refs, list) else [],
            trace_id          = trace_id,
            latency_ms        = latency_ms,
            templates         = result.get("templates_block"),
            answer_structured = result.get("answer_structured"),
        )
    except Exception as e:
        logger.error(f"Chat error: {e}", exc_info=True)
        # Full traceback is in the server log; tenant-facing text is a
        # short apology rather than a raw stack-adjacent message.
        raise HTTPException(
            500,
            "Something went wrong while composing your answer. Please "
            "try again in a moment."
        )


# =============================================================================
# CHAT STREAM ROUTER
# =============================================================================

@app.get("/api/v1/chat/stream", tags=["chat"])
async def chat_stream(
    question:   str,
    request:    Request,
    session_id: Optional[str] = None,
    key_info:   APIKeyInfo    = Depends(require_scope("chat")),
):
    """
    Stream compliance answer via Server-Sent Events.
    Events:
      data: {"type": "status",  "text": "Thinking..."}
      data: {"type": "token",   "text": "...answer chunk..."}
      data: {"type": "done",    "refs": [...], "latency_ms": N}
      data: {"type": "error",   "text": "..."}
    """
    from fastapi.responses import StreamingResponse
    from rag.arion_state import make_initial_state
    import json as _json

    if not request.app.state.arion_graph:
        raise HTTPException(
            503,
            "The answer service is unavailable right now. Please try "
            "again in a moment."
        )

    t_start    = time.time()
    sid        = session_id or f"api_{uuid.uuid4().hex[:8]}"
    # Ship 2'.l: validate + build with full tenant UUID.
    if not validate_session_id_shape(sid):
        raise HTTPException(
            400,
            "The session id contains characters we don't support. "
            "Please use letters, digits, hyphens, or underscores "
            "(up to 64 characters).",
        )
    thread_id = build_thread_id(key_info.tenant_id, sid)

    try:
        cache  = request.app.state.tenant_cache
        ctx    = cache.load(key_info.tenant_id)
        tenant = ctx.profile
    except Exception:
        tenant = None

    async def event_generator():
        def sse(data: dict) -> str:
            return "data: " + _json.dumps(data) + "\n\n"

        try:
            yield sse({"type": "status", "text": "Analysing your question..."})

            cfg   = {"configurable": {"thread_id": thread_id}}
            graph = getattr(request.app.state, "arion_graph_async",
                            request.app.state.arion_graph)
            # Use full initial state only on the FIRST turn for this thread.
            # On follow-ups, pass just the new query so the checkpointer's
            # persisted state survives instead of being reset to defaults.
            try:
                prior     = await graph.aget_state(cfg)
                has_prior = bool(prior and getattr(prior, "values", None))
            except Exception:
                has_prior = False
            state = ({"query": question}
                     if has_prior
                     else make_initial_state(tenant, query=question))

            answer_text     = ""
            refs            = []
            qtype           = None
            templates_block = None
            answer_structured: Optional[dict] = None  # Ship 18'.b

            async for event in graph.astream_events(state, cfg, version="v2"):
                kind = event.get("event", "")
                name = event.get("name", "")

                if kind == "on_chain_start" and name == "classify":
                    yield sse({"type": "status", "text": "Understanding your question..."})

                elif kind == "on_chain_start" and name == "retrieve":
                    yield sse({"type": "status", "text": "Looking up the relevant compliance material..."})

                elif kind == "on_chain_end" and not answer_text:
                    # Handles retrieve, clarify, and all short-circuit paths
                    _out = event.get("data", {}).get("output", {})
                    if not isinstance(_out, dict):
                        continue

                    # Get answer from any node that produces one
                    candidate = _out.get("answer_text", "") or _out.get("answer", "")

                    # Clarification check
                    if not candidate and _out.get("needs_clarif") and _out.get("clarif_question"):
                        candidate = _out.get("clarif_question", "")
                        qtype = "clarification"

                    if candidate:
                        answer_text = candidate
                        refs  = _out.get("cited_refs", []) or []
                        # Tier-4 structured templates block (2026-07-02).
                        # Captured here so we can emit it as its own
                        # SSE event after tokens, before 'done'.
                        templates_block = _out.get("templates_block") or None
                        # Ship 18'.b structured answer payload.
                        answer_structured = _out.get("answer_structured") or None
                        if qtype != "clarification":
                            qtype = (_out.get("intent_type")
                                     or _out.get("question_type")
                                     or _out.get("answer_source"))
                        # Strip selection artifacts
                        answer_text = answer_text.lstrip()
                        while answer_text.upper().startswith("SELECTED"):
                            nl = answer_text.find("\n")
                            answer_text = (answer_text[nl+1:] if nl != -1 else "").lstrip()
                        # Stream in chunks
                        for i in range(0, len(answer_text), 50):
                            yield sse({"type": "token", "text": answer_text[i:i+50]})
                            await asyncio.sleep(0)

            # Ship 18'.b — structured answer event emitted BEFORE
            # templates so the client swaps its prose-render for
            # cards, then decorates with any starter downloads.
            if answer_structured:
                yield sse({"type": "answer_structured", "block": answer_structured})

            # Tier-4 templates block — emit as its own event after tokens
            # so the client can render it as a structured card block
            # rather than parsing it out of the answer text.
            if templates_block:
                yield sse({"type": "templates", "block": templates_block})

            latency_ms = int((time.time() - t_start) * 1000)
            if hasattr(qtype, "value"):
                qtype = qtype.value
            yield sse({"type": "done", "refs": refs if isinstance(refs, list) else [],
                       "latency_ms": latency_ms, "answer_type": qtype})

        except Exception as e:
            logger.error(f"Stream error: {e}", exc_info=True)
            # Full traceback is in the server log; tenant-facing text is
            # a short apology rather than a raw stack-adjacent message.
            yield sse({"type": "error",
                       "text": "Something went wrong while composing "
                               "the answer. Please try again in a moment."})


    return StreamingResponse(
        event_generator(),
        media_type = "text/event-stream",
        headers    = {
            "Cache-Control":               "no-cache",
            "X-Accel-Buffering":           "no",
            "Access-Control-Allow-Origin": "*",
        },
    )


# =============================================================================
# DOCUMENTS ROUTER
# =============================================================================

class DocumentFindingSummary(BaseModel):
    """
    Per-finding row surfaced on the intake-completion response so the user
    can see what extraction proposed before approving via the Stage-1 review
    queue ([[hitl-two-stage-approval-design]]). Counts alone aren't enough
    for HITL: the user needs control_ref + extracted status + excerpt to
    judge whether to approve or reject each finding.
    """
    finding_id:    str
    control_ref:   str
    standard_id:   str
    status:        str           # present | missing | partial
    confidence:    str           # high | medium | low
    excerpt:       Optional[str] = None
    review_status: str           # pending | approved | rejected | expired
    # schema_v22 — distinguish native extractions ('extracted') from
    # cross-framework mirrors written by xfw_proposer ('xfw_bridge'). The UI
    # uses this to badge xfw-derived rows in the Stage-1 queue.
    inference_source: str        # extracted | xfw_bridge
    inferred_from_control_ref: Optional[str] = None
    inferred_from_standard_id: Optional[str] = None


class DocumentStatus(BaseModel):
    upload_id:       str
    filename:        str
    status:          str
    doc_type:        Optional[str] = None
    standard_ids:    Optional[str] = None
    token_estimate:  Optional[int] = None
    findings_written: Optional[int] = None
    posture_created:  Optional[int] = None
    posture_updated:  Optional[int] = None
    posture_skipped:  Optional[int] = None
    # Stage 4.5 (xfw_proposer) — populated when the xfw trace row landed
    proposals_written: Optional[int] = None
    proposals_skipped: Optional[int] = None
    xfw_targets:       Optional[list[str]] = None
    total_ms:        Optional[int] = None
    had_error:       Optional[bool] = None
    error_type:      Optional[str] = None
    started_at:      Optional[str] = None
    # Set when the upload was rejected as a duplicate of an existing one
    # (Layer 2 markdown match — Layer 1 byte match returns 409 instead).
    dup_of_upload_id: Optional[str] = None
    # schema_v20 — present on non-duplicate rows. version_no=1 for the first
    # upload of a given filename; subsequent same-filename uploads with new
    # content increment within the same series_id.
    series_id:  Optional[str] = None
    version_no: Optional[int] = None
    # schema_v24 — per-finding enumeration so the chat surface can present
    # the extraction's proposals for Stage-1 batch approval. Empty list when
    # the upload is still processing or produced no findings.
    findings: list[DocumentFindingSummary] = []


def _run_pipeline(
    file_path:              str,
    tenant_id:              str,
    upload_id: UploadIdParam,
    db_url:                 str,
    api_key:                str,
    original_filename:      Optional[str]        = None,
    user_id:                Optional[str]        = None,
    declared_standard_ids:  Optional[list[str]]  = None,
    declared_evidence_type: Optional[str]        = None,
):
    """Run document pipeline in background thread.

    user_id is the X-API-Key holder's UUID — used to attribute
    auto-approved templated findings via document_findings.confirmed_by
    (per the no-Stage-1 path for tenant-authored marker-bearing
    uploads). Other intake lanes leave confirmed_by NULL until
    Stage-1 acts on them.

    declared_standard_ids / declared_evidence_type: tenant-declared
    intent from the upload UI. When present, the enricher uses these
    verbatim instead of running content-keyword detection — closing
    the gap where privacy-relevant docs without the string "PIMS"
    verbatim were missing ISO27701:2019 scope.
    """
    from rag.intake.doc_pipeline import DocumentPipeline
    from rag.ai_trace import set_trace_context
    # Wave 4c — stamp tenant + upload into ai_trace ContextVars so any
    # LLM call during this pipeline auto-tags with them
    set_trace_context(tenant_id=tenant_id, upload_id=upload_id)
    pipeline = DocumentPipeline(
        db_url  = db_url,
        api_key = api_key,
        trace   = True,
    )
    result = pipeline.run(file_path, tenant_id, upload_id,
                          original_filename      = original_filename,
                          user_id                = user_id,
                          declared_standard_ids  = declared_standard_ids,
                          declared_evidence_type = declared_evidence_type)
    logger.info(
        f"Pipeline complete: {result.document_name} "
        f"status={result.status} findings={result.findings_count}"
    )
    # Original is preserved as evidence — auditors will ask for the file that
    # backs each finding, and re-parsing depends on it. Right-to-erasure goes
    # through DELETE /api/v1/documents/{id} (separate workstream).


@app.post("/api/v1/documents/upload", tags=["documents"])
async def upload_document(
    request:                Request,
    background_tasks:       BackgroundTasks,
    file:                   UploadFile     = File(...),
    declared_standard_id:   Optional[str]  = Form(None),
    declared_evidence_type: Optional[str]  = Form(None),
    key_info:               APIKeyInfo     = Depends(require_scope("documents")),
):
    """
    Upload a compliance document for processing.
    Returns upload_id immediately — processing runs in background.
    Poll GET /api/v1/documents/{upload_id}/status for progress.
    """
    # Validate extension
    suffix = Path(file.filename).suffix.lower()
    if suffix not in SUPPORTED_EXTENSIONS:
        raise HTTPException(
            400,
            f"Unsupported file type: {suffix}. "
            f"Supported: {', '.join(sorted(SUPPORTED_EXTENSIONS))}"
        )

    # Check file size
    contents = await file.read()
    size_mb  = len(contents) / (1024 * 1024)
    if size_mb > MAX_UPLOAD_MB:
        raise HTTPException(
            400,
            f"File too large: {size_mb:.1f}MB. Maximum: {MAX_UPLOAD_MB}MB"
        )

    # Hash the bytes BEFORE we touch disk or the DB. Layer 1 of the dedup
    # contract (schema_v19): if these bytes have already been accepted for
    # this tenant, reject the upload with 409 and point at the canonical
    # upload_id. No file is written, no DB row is created, no background
    # work is queued.
    import hashlib as _hl
    file_sha256 = _hl.sha256(contents).hexdigest()
    byte_size   = len(contents)

    pool = request.app.state.pg_pool
    conn = pool.getconn()
    try:
        set_session(conn, key_info.tenant_id, key_info.user_id)
        with conn.cursor() as cur:
            # 'failed' rows are excluded too — a crashed pipeline produces no
            # findings, so the same bytes should be re-uploadable once the bug
            # is fixed. Predicate mirrored in schema_v33 unique index.
            cur.execute("""
                SELECT id, filename, uploaded_at, extraction_status
                  FROM document_uploads
                 WHERE tenant_id = %s::uuid
                   AND sha256    = %s
                   AND extraction_status NOT IN ('duplicate', 'failed')
                 LIMIT 1
            """, (key_info.tenant_id, file_sha256))
            existing = cur.fetchone()
    finally:
        pool.putconn(conn)

    if existing:
        existing_id, existing_name, existing_at, existing_status = existing
        logger.info(
            f"Upload rejected as duplicate (bytes match): "
            f"new={file.filename} canonical={existing_id} "
            f"tenant={key_info.tenant_id[:8]}"
        )
        raise HTTPException(
            status_code=409,
            detail={
                "error":                "duplicate_upload",
                "message":              "Identical file already uploaded.",
                "canonical_upload_id":  str(existing_id),
                "canonical_filename":   existing_name,
                "canonical_uploaded_at": existing_at.isoformat() if existing_at else None,
                "canonical_status":     existing_status,
                "match_type":           "source_bytes",
            },
        )

    upload_id = str(uuid.uuid4())
    safe_name = f"{upload_id}{suffix}"

    # Tenant-namespace the storage path so cross-tenant traversal is impossible
    # by construction. Originals are kept (not unlinked post-processing) so the
    # findings have a chain-of-custody binary to point back to.
    tenant_dir = UPLOAD_DIR / key_info.tenant_id
    tenant_dir.mkdir(parents=True, exist_ok=True)
    file_path = tenant_dir / safe_name

    # Save to disk
    file_path.write_bytes(contents)

    # Register in document_uploads. (series_id, version_no) come from
    # schema_v20: same filename re-uploaded with different content joins the
    # existing series as the next version. The lookup + insert run in one
    # transaction so concurrent same-filename uploads collide on the
    # uniq_document_uploads_series_version index rather than producing
    # duplicate version_no values.
    series_id  = None
    version_no = None
    conn = pool.getconn()
    try:
        set_session(conn, key_info.tenant_id, key_info.user_id)
        with conn.cursor() as cur:
            # Cascade-on-success cleanup: clear prior 'failed'/'duplicate'
            # rows for this exact SHA so the successful retry doesn't leave
            # audit-log noise. Same txn as the INSERT below — if anything
            # raises before commit, the prior row stays intact.
            cur.execute("""
                DELETE FROM document_uploads
                 WHERE tenant_id = %s::uuid
                   AND sha256    = %s
                   AND extraction_status IN ('failed', 'duplicate')
            """, (key_info.tenant_id, file_sha256))

            cur.execute("""
                SELECT series_id, MAX(version_no)
                  FROM document_uploads
                 WHERE tenant_id = %s::uuid
                   AND filename  = %s
                   AND extraction_status <> 'duplicate'
                   AND series_id IS NOT NULL
                 GROUP BY series_id
                 LIMIT 1
            """, (key_info.tenant_id, file.filename))
            row = cur.fetchone()
            if row:
                series_id  = str(row[0])
                version_no = int(row[1]) + 1
            else:
                series_id  = str(uuid.uuid4())
                version_no = 1

            cur.execute("""
                INSERT INTO document_uploads (
                    id, tenant_id, filename, storage_path,
                    extraction_status, uploaded_by,
                    sha256, byte_size,
                    series_id, version_no
                ) VALUES (%s, %s::uuid, %s, %s, 'pending', %s::uuid, %s, %s,
                          %s::uuid, %s)
                ON CONFLICT (id) DO NOTHING
            """, (
                upload_id,
                key_info.tenant_id,
                file.filename,
                str(file_path),
                key_info.user_id,
                file_sha256,
                byte_size,
                series_id,
                version_no,
            ))
        conn.commit()
    except Exception as e:
        conn.rollback()
        logger.warning(f"document_uploads insert failed: {e} — continuing")
    finally:
        pool.putconn(conn)

    # Parse declared framework + type hints from the upload UI dropdowns.
    #   declared_standard_id values:
    #     - None or "" or "auto"      → auto-detect (current keyword path)
    #     - "multi"                    → apply all enrolled queryable standards
    #     - "ISO27001:2022" / ...      → single-standard scoping
    #   declared_evidence_type values:
    #     - None or "" or "auto"      → auto-detect
    #     - "policy" / "procedure" ..  → declared shape (matches _UPLOAD_HINTS keys)
    _hint_stds: Optional[list[str]] = None
    if declared_standard_id and declared_standard_id not in ("", "auto"):
        if declared_standard_id == "multi":
            # Resolve "multi" here to the tenant's enrolled + graph-loaded
            # standards (same set scope_loader reports as queryable).
            _c = pool.getconn()
            try:
                set_session(_c, key_info.tenant_id, key_info.user_id)
                with _c.cursor() as _cur:
                    _cur.execute("""
                        SELECT ts.standard_id
                          FROM tenant_standards ts
                          JOIN standards s ON s.id = ts.standard_id
                         WHERE ts.tenant_id = %s::uuid
                           AND s.loaded_in_graph = TRUE
                         ORDER BY ts.standard_id
                    """, (key_info.tenant_id,))
                    _hint_stds = [r[0] for r in _cur.fetchall()] or None
            finally:
                pool.putconn(_c)
        else:
            _hint_stds = [declared_standard_id]
    _hint_evtype = declared_evidence_type if (declared_evidence_type and declared_evidence_type not in ("", "auto")) else None

    # Persist declared values on document_uploads for audit + resume paths.
    # doc_type + standard_ids columns already exist — reused for declared intent.
    if _hint_stds or _hint_evtype:
        _conn = pool.getconn()
        try:
            set_session(_conn, key_info.tenant_id, key_info.user_id)
            with _conn.cursor() as _cur:
                _cur.execute(
                    """UPDATE document_uploads
                          SET doc_type     = COALESCE(%s, doc_type),
                              standard_ids = COALESCE(%s, standard_ids)
                        WHERE id = %s::uuid""",
                    (_hint_evtype, _hint_stds, upload_id),
                )
                _conn.commit()
        except Exception as e:
            _conn.rollback()
            logger.warning(f"document_uploads declared-hint update failed: {e} — continuing")
        finally:
            pool.putconn(_conn)

    # Queue background processing
    api_key = os.getenv("ANTHROPIC_API_KEY", "")
    background_tasks.add_task(
        _run_pipeline,
        file_path              = str(file_path),
        tenant_id              = key_info.tenant_id,
        upload_id              = upload_id,
        db_url                 = DATABASE_URL,
        api_key                = api_key,
        original_filename      = file.filename,
        user_id                = key_info.user_id,
        declared_standard_ids  = _hint_stds,
        declared_evidence_type = _hint_evtype,
    )

    logger.info(
        f"Document queued: {file.filename} "
        f"upload_id={upload_id[:8]} tenant={key_info.tenant_id[:8]}"
    )

    return {
        "upload_id":  upload_id,
        "filename":   file.filename,
        "status":     "queued",
        "size_mb":    round(size_mb, 2),
        "series_id":  series_id,
        "version_no": version_no,
        "trace_id":   request.state.trace_id,
        "message":    "Processing started. Poll /status for progress.",
    }


@app.get(
    "/api/v1/documents/{upload_id}/status",
    response_model=DocumentStatus,
    tags=["documents"],
)
async def document_status(
    upload_id: UploadIdParam,
    request:   Request,
    key_info:  APIKeyInfo = Depends(require_scope("documents")),
):
    """Get processing status for an uploaded document."""
    pool = request.app.state.pg_pool
    conn = pool.getconn()
    try:
        set_session(conn, key_info.tenant_id)
        with conn.cursor() as cur:
            # Try v_intake_runs first (has full trace data including xfw stage)
            cur.execute("""
                SELECT
                    upload_id, filename, doc_type, standard_ids,
                    token_estimate,
                    findings_written, posture_created, posture_updated,
                    posture_skipped,
                    proposals_written, proposals_skipped, xfw_targets,
                    total_ms, had_error, error_type,
                    started_at::text
                FROM v_intake_runs
                WHERE upload_id = %s
                  AND tenant_id = %s::uuid
                ORDER BY started_at DESC
                LIMIT 1
            """, (upload_id, key_info.tenant_id))
            row = cur.fetchone()

            if row:
                (uid, fname, doc_type, std_ids, tok_est, fw, pc, pu, ps,
                 prop_written, prop_skipped, xfw_tgts,
                 total_ms, had_error, error_type, started_at) = row
                # Determine status from trace
                if had_error:
                    doc_status = "failed"
                elif fw is not None:
                    doc_status = "completed"
                else:
                    doc_status = "processing"
            else:
                doc_type = std_ids = tok_est = fw = pc = pu = ps = total_ms = None
                prop_written = prop_skipped = None
                xfw_tgts = None
                had_error = error_type = None
                fname = ""
                doc_status = "pending"
                started_at = None

            # Always consult document_uploads for the authoritative status +
            # dup_of pointer. The trace view doesn't know about 'duplicate' or
            # the dup_of_upload_id column, so a v19-rejected upload that never
            # produced a trace row would otherwise appear as 404.
            cur.execute("""
                SELECT extraction_status, filename, uploaded_at::text,
                       dup_of_upload_id::text,
                       series_id::text, version_no
                  FROM document_uploads
                 WHERE id = %s::uuid
                   AND tenant_id = %s::uuid
            """, (upload_id, key_info.tenant_id))
            row2 = cur.fetchone()

            if not row and not row2:
                # Ship 7'.c — scrub bare UUID from the tenant-facing
                # error string; keep the trailing suffix so support
                # can still correlate against server logs.
                from rag.output import humanize as _humanize
                raise HTTPException(
                    404,
                    _humanize(
                        f"We couldn't find that upload ({upload_id}) "
                        f"for your tenant.",
                        surface="error_detail",
                    ),
                )

            dup_of      = None
            series_id   = None
            version_no  = None
            if row2:
                (u_status, u_filename, u_uploaded_at, u_dup_of,
                 u_series_id, u_version_no) = row2
                # extraction_status='duplicate' is the authoritative signal
                # for the rejection path. Override any trace-derived status.
                if u_status == "duplicate":
                    doc_status = "duplicate"
                    dup_of     = u_dup_of
                if not fname and u_filename:
                    fname = u_filename
                if not started_at and u_uploaded_at:
                    started_at = u_uploaded_at
                series_id  = u_series_id
                version_no = u_version_no

            # Per-finding enumeration (schema_v24) — let the UI render the
            # Stage-1 batch-approve queue for this upload. We scope to
            # findings extracted after the upload started (extracted_at >=
            # uploaded_at) because document_findings.document_id points at
            # client_documents.id, not the upload_id — siblings of the same
            # filename would otherwise leak in.
            findings_list: list[DocumentFindingSummary] = []
            if fname and started_at:
                cur.execute("""
                    SELECT df.id::text,
                           df.control_ref,
                           df.standard_id,
                           df.status,
                           df.confidence,
                           df.excerpt,
                           df.review_status,
                           df.inference_source,
                           df.inferred_from_control_ref,
                           df.inferred_from_standard_id
                      FROM document_findings df
                      JOIN client_documents  cd ON cd.id = df.document_id
                     WHERE df.tenant_id   = %s::uuid
                       AND cd.tenant_id   = %s::uuid
                       AND lower(cd.filename) = lower(%s)
                       AND df.is_active   = TRUE
                       AND df.extracted_at >= %s::timestamptz
                     ORDER BY df.control_ref, df.extracted_at
                """, (
                    key_info.tenant_id, key_info.tenant_id,
                    fname, started_at,
                ))
                for r in cur.fetchall():
                    findings_list.append(DocumentFindingSummary(
                        finding_id    = r[0],
                        control_ref   = r[1],
                        standard_id   = r[2],
                        status        = r[3],
                        confidence    = r[4],
                        excerpt       = r[5],
                        review_status = r[6],
                        inference_source = r[7],
                        inferred_from_control_ref = r[8],
                        inferred_from_standard_id = r[9],
                    ))

        return DocumentStatus(
            upload_id        = upload_id,
            filename         = fname or "",
            status           = doc_status,
            doc_type         = doc_type,
            standard_ids     = std_ids,
            token_estimate   = tok_est,
            findings_written = fw,
            posture_created  = pc,
            posture_updated  = pu,
            posture_skipped  = ps,
            proposals_written = prop_written,
            proposals_skipped = prop_skipped,
            xfw_targets       = xfw_tgts,
            total_ms         = total_ms,
            had_error        = had_error,
            error_type       = error_type,
            started_at       = started_at,
            dup_of_upload_id = dup_of,
            series_id        = series_id,
            version_no       = version_no,
            findings         = findings_list,
        )
    finally:
        pool.putconn(conn)


class DocumentVersion(BaseModel):
    upload_id:         str
    version_no:        int
    filename:          str
    uploaded_at:       str
    extraction_status: str
    markdown_sha256:   Optional[str] = None
    findings_count:    Optional[int] = None


@app.get(
    "/api/v1/documents/{series_id}/versions",
    tags=["documents"],
)
async def list_document_versions(
    series_id: SeriesIdParam,
    request:   Request,
    key_info:  APIKeyInfo = Depends(require_scope("documents")),
):
    """
    List the upload history of a document series, oldest version first.

    Series membership is set on upload (schema_v20): same filename, different
    content joins the series as the next version. Duplicate uploads are not
    members — they're tombstones pointing at the canonical upload.
    """
    pool = request.app.state.pg_pool
    conn = pool.getconn()
    try:
        set_session(conn, key_info.tenant_id)
        with conn.cursor() as cur:
            cur.execute("""
                SELECT u.id::text,
                       u.version_no,
                       u.filename,
                       u.uploaded_at::text,
                       u.extraction_status,
                       t.markdown_sha256,
                       u.findings_count
                  FROM document_uploads u
             LEFT JOIN document_text   t ON t.upload_id = u.id
                 WHERE u.series_id = %s::uuid
                   AND u.tenant_id = %s::uuid
                 ORDER BY u.version_no
            """, (series_id, key_info.tenant_id))
            rows = cur.fetchall()

        if not rows:
            # Ship 7'.c — scrub UUID + soften phrasing.
            from rag.output import humanize as _humanize
            raise HTTPException(
                404,
                _humanize(
                    f"We couldn't find that document series ({series_id}).",
                    surface="error_detail",
                ),
            )

        versions = [
            DocumentVersion(
                upload_id         = r[0],
                version_no        = r[1],
                filename          = r[2],
                uploaded_at       = r[3],
                extraction_status = r[4],
                markdown_sha256   = r[5],
                findings_count    = r[6],
            )
            for r in rows
        ]
        return {
            "series_id":     series_id,
            "filename":      versions[0].filename,
            "version_count": len(versions),
            "versions":      [v.model_dump() for v in versions],
        }
    finally:
        pool.putconn(conn)


@app.get("/api/v1/documents", tags=["documents"])
async def list_documents(
    request:  Request,
    key_info: APIKeyInfo = Depends(require_scope("documents")),
    limit:    int = 20,
    offset:   int = 0,
):
    """List documents uploaded by this tenant."""
    pool = request.app.state.pg_pool
    conn = pool.getconn()
    try:
        set_session(conn, key_info.tenant_id)
        with conn.cursor() as cur:
            cur.execute("""
                SELECT
                    id, original_name, doc_type, standard_id,
                    status, findings_count, created_at::text
                FROM document_uploads
                WHERE tenant_id = %s::uuid
                ORDER BY created_at DESC
                LIMIT %s OFFSET %s
            """, (key_info.tenant_id, limit, offset))
            rows = cur.fetchall()
            cols = [d[0] for d in cur.description]
        return {
            "documents": [dict(zip(cols, r)) for r in rows],
            "limit":     limit,
            "offset":    offset,
        }
    finally:
        pool.putconn(conn)


# =============================================================================
# POSTURE TIMELINE
# =============================================================================

class PostureHistoryEntry(BaseModel):
    changed_at:        str
    status_before:     Optional[str] = None
    status_after:      str
    source:            str
    source_upload_id:  Optional[str] = None
    source_filename:   Optional[str] = None
    source_version_no: Optional[int] = None
    evidence_citation: Optional[str] = None
    confidence:        Optional[str] = None


@app.get(
    "/api/v1/posture/{control_ref}/history",
    tags=["documents"],
)
async def posture_history(
    control_ref: ControlRefParam,
    request:     Request,
    key_info:    APIKeyInfo = Depends(require_scope("documents")),
    standard_id: Optional[str] = None,
):
    """
    Return the timeline of status transitions for a control.

    A control_ref can exist under multiple standards (e.g. ISO 27001
    "A.5.18" and a custom framework). If standard_id is omitted, all
    standards are returned interleaved by changed_at; pass standard_id
    to scope to one framework.

    Each entry includes the driving upload's filename + version_no when
    the change came from document intake (schema_v21 source='document').
    """
    pool = request.app.state.pg_pool
    conn = pool.getconn()
    try:
        set_session(conn, key_info.tenant_id)
        with conn.cursor() as cur:
            params: list = [key_info.tenant_id, control_ref]
            sql = """
                SELECT h.changed_at::text,
                       h.status_before, h.status_after,
                       h.source, h.source_upload_id::text,
                       u.filename, u.version_no,
                       h.evidence_citation, h.confidence,
                       h.standard_id
                  FROM posture_status_log h
             LEFT JOIN document_uploads   u ON u.id = h.source_upload_id
                 WHERE h.tenant_id   = %s::uuid
                   AND h.control_ref = %s
            """
            if standard_id:
                sql += " AND h.standard_id = %s"
                params.append(standard_id)
            sql += " ORDER BY h.changed_at"
            cur.execute(sql, params)
            rows = cur.fetchall()

        entries = [
            PostureHistoryEntry(
                changed_at        = r[0],
                status_before     = r[1],
                status_after      = r[2],
                source            = r[3],
                source_upload_id  = r[4],
                source_filename   = r[5],
                source_version_no = r[6],
                evidence_citation = r[7],
                confidence        = r[8],
            )
            for r in rows
        ]
        standards = sorted({r[9] for r in rows})
        return {
            "control_ref":   control_ref,
            "standard_id":   standard_id,
            "standards":     standards,
            "entry_count":   len(entries),
            "entries":       [e.model_dump() for e in entries],
        }
    finally:
        pool.putconn(conn)


# =============================================================================
# HITL ROUTER
# =============================================================================

@app.get("/api/v1/review-queue", tags=["hitl"])
async def review_queue(
    request:     Request,
    key_info:    APIKeyInfo = Depends(require_scope("hitl")),
    finding:     Optional[str] = None,   # filter: NC, OFI, Comply
    source:      Optional[str] = None,   # filter: assessor, document, workbook
    standard_id: Optional[str] = None,
    limit:       int = 50,
    offset:      int = 0,
):
    """
    List posture controls pending consultant review.
    Ordered: NC first, then OFI, then Comply. Within each, by control_ref.
    """
    pool = request.app.state.pg_pool
    conn = pool.getconn()
    try:
        set_session(conn, key_info.tenant_id)
        with conn.cursor() as cur:
            filters = ["tenant_id = %s::uuid"]
            params  = [key_info.tenant_id]

            if finding:
                filters.append("finding = %s")
                params.append(finding)
            if source:
                filters.append("source = %s")
                params.append(source)
            if standard_id:
                filters.append("standard_id = %s")
                params.append(standard_id)

            where = " AND ".join(filters)

            cur.execute(f"""
                SELECT
                    id, control_ref, standard_id, finding,
                    gap_description, confirmation_status, source,
                    confidence, system_finding, system_gap,
                    system_proposed_at::text, hours_in_draft,
                    previously_overridden
                FROM v_posture_review_queue
                WHERE {where}
                LIMIT %s OFFSET %s
            """, params + [limit, offset])

            rows = cur.fetchall()
            cols = [d[0] for d in cur.description]

            cur.execute(f"""
                SELECT COUNT(*) FROM v_posture_review_queue WHERE {where}
            """, params)
            total = cur.fetchone()[0]

        return {
            "controls": [dict(zip(cols, r)) for r in rows],
            "total":    total,
            "limit":    limit,
            "offset":   offset,
        }
    finally:
        pool.putconn(conn)


class ConfirmRequest(BaseModel):
    reason: Optional[str] = None


class OverrideRequest(BaseModel):
    finding:         str   # NC | OFI | Comply | N/A
    gap_description: Optional[str] = None
    reason:          Optional[str] = None


@app.post("/api/v1/posture/{posture_id}/confirm", tags=["hitl"])
async def confirm_posture(
    posture_id: PostureIdParam,
    body:       ConfirmRequest,
    request:    Request,
    key_info:   APIKeyInfo = Depends(require_scope("hitl")),
):
    """Confirm a draft posture finding (draft → confirmed)."""
    pool = request.app.state.pg_pool
    conn = pool.getconn()
    try:
        set_session(conn, key_info.tenant_id, key_info.user_id)
        with conn.cursor() as cur:
            cur.execute("""
                SELECT v_control_ref, v_finding, v_status
                FROM fn_confirm_posture(%s::uuid, %s::uuid, %s::uuid)
            """, (posture_id, key_info.tenant_id, key_info.user_id))
            row = cur.fetchone()
            if not row:
                raise HTTPException(
                    404,
                    f"Posture control {posture_id} not found or not in draft state"
                )
        conn.commit()

        logger.info(
            f"Confirmed: {row[0]} finding={row[1]} "
            f"by user={key_info.user_id[:8]} tenant={key_info.tenant_id[:8]}"
        )

        # Invalidate tenant cache so next chat request gets fresh posture
        cache = request.app.state.tenant_cache
        if cache:
            cache.invalidate(key_info.tenant_id)

        return {
            "control_ref":         row[0],
            "finding":             row[1],
            "confirmation_status": row[2],
            "confirmed_by":        key_info.user_id,
            "trace_id":            request.state.trace_id,
        }
    except HTTPException:
        conn.rollback()
        raise
    except Exception as e:
        conn.rollback()
        logger.error(f"Confirm failed: {e}", exc_info=True)
        raise HTTPException(500, str(e))
    finally:
        pool.putconn(conn)


@app.post("/api/v1/posture/{posture_id}/override", tags=["hitl"])
async def override_posture(
    posture_id: PostureIdParam,
    body:       OverrideRequest,
    request:    Request,
    key_info:   APIKeyInfo = Depends(require_scope("hitl")),
):
    """
    Override a posture finding — consultant changes the finding.
    Preserves system_finding so the original assessment is never lost.
    """
    if body.finding not in ("NC", "OFI", "Comply", "N/A"):
        raise HTTPException(400, "finding must be one of: NC, OFI, Comply, N/A")

    pool = request.app.state.pg_pool
    conn = pool.getconn()
    try:
        set_session(conn, key_info.tenant_id, key_info.user_id)
        with conn.cursor() as cur:
            updates = [
                "confirmation_status = 'overridden'",
                "finding             = %s",
                "confirmed_by        = %s::uuid",
                "confirmed_at        = NOW()",
            ]
            params = [body.finding, key_info.user_id]

            if body.gap_description:
                updates.append("gap_description = %s")
                params.append(body.gap_description)

            params += [posture_id, key_info.tenant_id]

            cur.execute("""
                SELECT v_control_ref, v_finding, v_status
                FROM fn_override_posture(%s::uuid, %s::uuid, %s::uuid, %s, %s)
            """, (posture_id, key_info.tenant_id, key_info.user_id,
                  body.finding, body.gap_description))
            row = cur.fetchone()
            if not row:
                raise HTTPException(
                    404,
                    "We couldn't find that posture entry for your tenant."
                )
        conn.commit()

        logger.info(
            f"Overridden: {row[0]} finding={row[1]} "
            f"by user={key_info.user_id[:8]} tenant={key_info.tenant_id[:8]}"
        )

        cache = request.app.state.tenant_cache
        if cache:
            cache.invalidate(key_info.tenant_id)

        return {
            "control_ref":         row[0],
            "finding":             row[1],
            "confirmation_status": row[2],
            "overridden_by":       key_info.user_id,
            "trace_id":            request.state.trace_id,
        }
    except HTTPException:
        conn.rollback()
        raise
    except Exception as e:
        conn.rollback()
        logger.error(f"Override failed: {e}", exc_info=True)
        raise HTTPException(500, str(e))
    finally:
        pool.putconn(conn)


# =============================================================================
# XFW PROPOSALS — HITL queue from the intake xfw_proposer (commit 01de40e).
# Reads/writes document_findings rows where inference_source='xfw_bridge'.
# Confirm flips confirmed_by/confirmed_at; reject sets is_active=FALSE so the
# row is preserved for audit but no longer surfaces.
# =============================================================================

@app.get("/api/v1/xfw-proposals", tags=["hitl"])
async def list_xfw_proposals(
    request:     Request,
    key_info:    APIKeyInfo  = Depends(require_scope("hitl")),
    standard_id: Optional[str] = None,
    limit:       int           = 50,
    offset:      int           = 0,
):
    """
    List pending cross-framework proposals for the tenant. Each row is a
    document_findings entry written by xfw_proposer with confirmed_by IS NULL.
    """
    pool = request.app.state.pg_pool
    conn = pool.getconn()
    try:
        set_session(conn, key_info.tenant_id)
        with conn.cursor() as cur:
            filters = [
                "df.tenant_id        = %s::uuid",
                "df.inference_source = 'xfw_bridge'",
                "df.confirmed_by IS NULL",
                "df.is_active       = TRUE",
            ]
            params: list = [key_info.tenant_id]
            if standard_id:
                filters.append("df.standard_id = %s")
                params.append(standard_id)
            where = " AND ".join(filters)

            cur.execute(
                f"""
                SELECT df.id, df.standard_id, df.control_ref, df.status,
                       df.confidence,
                       df.inferred_from_standard_id, df.inferred_from_control_ref,
                       df.document_id, cd.document_title, df.extracted_at::text
                  FROM document_findings df
             LEFT JOIN client_documents cd ON cd.id = df.document_id
                 WHERE {where}
                 ORDER BY df.standard_id, df.control_ref
                 LIMIT %s OFFSET %s
                """,
                params + [limit, offset],
            )
            rows = cur.fetchall()

            cur.execute(
                f"SELECT COUNT(*) FROM document_findings df WHERE {where}",
                params,
            )
            total = cur.fetchone()[0]

        proposals = [
            {
                "id":                       str(r[0]),
                "standard_id":              r[1],
                "control_ref":              r[2],
                "status":                   r[3],
                "confidence":               r[4],
                "inferred_from_standard_id": r[5],
                "inferred_from_control_ref": r[6],
                "document_id":              str(r[7]) if r[7] else None,
                "document_title":           r[8],
                "extracted_at":             r[9],
            }
            for r in rows
        ]
        return {"proposals": proposals, "total": total, "limit": limit, "offset": offset}
    finally:
        pool.putconn(conn)


@app.post("/api/v1/xfw-proposals/{proposal_id}/confirm", tags=["hitl"])
async def confirm_xfw_proposal(
    proposal_id: ProposalIdParam,
    request:     Request,
    key_info:    APIKeyInfo = Depends(require_scope("hitl")),
):
    """Confirm a pending xfw proposal — stamps confirmed_by + confirmed_at."""
    pool = request.app.state.pg_pool
    conn = pool.getconn()
    try:
        set_session(conn, key_info.tenant_id, key_info.user_id)
        with conn.cursor() as cur:
            cur.execute(
                """
                UPDATE document_findings
                   SET confirmed_by = %s::uuid,
                       confirmed_at = NOW()
                 WHERE id               = %s::uuid
                   AND tenant_id        = %s::uuid
                   AND inference_source = 'xfw_bridge'
                   AND confirmed_by IS NULL
                   AND is_active       = TRUE
             RETURNING standard_id, control_ref, status
                """,
                (key_info.user_id, proposal_id, key_info.tenant_id),
            )
            row = cur.fetchone()
            if not row:
                raise HTTPException(
                    404,
                    f"Proposal {proposal_id} not found, already confirmed, or not pending."
                )
        conn.commit()
        logger.info(
            f"xfw proposal confirmed: {row[0]}:{row[1]} "
            f"by user={key_info.user_id[:8]} tenant={key_info.tenant_id[:8]}"
        )
        return {
            "id":            proposal_id,
            "standard_id":   row[0],
            "control_ref":   row[1],
            "status":        row[2],
            "confirmed_by":  key_info.user_id,
            "trace_id":      request.state.trace_id,
        }
    except HTTPException:
        conn.rollback()
        raise
    except Exception as e:
        conn.rollback()
        logger.error(f"xfw confirm failed: {e}", exc_info=True)
        raise HTTPException(500, str(e))
    finally:
        pool.putconn(conn)


@app.post("/api/v1/xfw-proposals/{proposal_id}/reject", tags=["hitl"])
async def reject_xfw_proposal(
    proposal_id: ProposalIdParam,
    request:     Request,
    key_info:    APIKeyInfo = Depends(require_scope("hitl")),
):
    """
    Reject a pending xfw proposal — sets is_active=FALSE so it's preserved
    for audit but no longer surfaces in the queue.
    """
    pool = request.app.state.pg_pool
    conn = pool.getconn()
    try:
        set_session(conn, key_info.tenant_id, key_info.user_id)
        with conn.cursor() as cur:
            cur.execute(
                """
                UPDATE document_findings
                   SET is_active       = FALSE,
                       deleted_at      = NOW(),
                       deleted_by      = %s::uuid,
                       deletion_reason = 'xfw_proposal_rejected'
                 WHERE id               = %s::uuid
                   AND tenant_id        = %s::uuid
                   AND inference_source = 'xfw_bridge'
                   AND confirmed_by IS NULL
                   AND is_active       = TRUE
             RETURNING standard_id, control_ref
                """,
                (key_info.user_id, proposal_id, key_info.tenant_id),
            )
            row = cur.fetchone()
            if not row:
                raise HTTPException(
                    404,
                    f"Proposal {proposal_id} not found or not pending."
                )
        conn.commit()
        logger.info(
            f"xfw proposal rejected: {row[0]}:{row[1]} "
            f"by user={key_info.user_id[:8]} tenant={key_info.tenant_id[:8]}"
        )
        return {
            "id":           proposal_id,
            "standard_id":  row[0],
            "control_ref":  row[1],
            "rejected_by":  key_info.user_id,
            "trace_id":     request.state.trace_id,
        }
    except HTTPException:
        conn.rollback()
        raise
    except Exception as e:
        conn.rollback()
        logger.error(f"xfw reject failed: {e}", exc_info=True)
        raise HTTPException(500, str(e))
    finally:
        pool.putconn(conn)


class BulkConfirmRequest(BaseModel):
    standard_id: Optional[str] = None
    source:      Optional[str] = None
    dry_run:     bool          = True


@app.post("/api/v1/posture/bulk-confirm", tags=["hitl"])
async def bulk_confirm(
    body:     BulkConfirmRequest,
    request:  Request,
    key_info: APIKeyInfo = Depends(require_scope("hitl")),
):
    """
    Bulk confirm posture findings, optionally filtered by standard or source.
    Always dry_run=True by default — set dry_run=False to commit.
    """
    pool = request.app.state.pg_pool
    conn = pool.getconn()
    try:
        set_session(conn, key_info.tenant_id, key_info.user_id)
        with conn.cursor() as cur:
            cur.execute("""
                SELECT control_ref, finding, source, action
                FROM fn_bulk_confirm_posture(%s::uuid, %s::uuid, %s, %s, %s)
            """, (
                key_info.tenant_id,
                key_info.user_id,
                body.standard_id,
                body.source,
                body.dry_run,
            ))
            rows = cur.fetchall()

        if not body.dry_run:
            conn.commit()
            cache = request.app.state.tenant_cache
            if cache:
                cache.invalidate(key_info.tenant_id)

        results = [
            {"control_ref": r[0], "finding": r[1], "source": r[2], "action": r[3]}
            for r in rows
        ]
        logger.info(
            f"Bulk confirm: {len(results)} controls "
            f"dry_run={body.dry_run} tenant={key_info.tenant_id[:8]}"
        )

        return {
            "dry_run":  body.dry_run,
            "count":    len(results),
            "controls": results,
            "trace_id": request.state.trace_id,
        }
    except Exception as e:
        conn.rollback()
        logger.error(f"Bulk confirm failed: {e}", exc_info=True)
        raise HTTPException(500, str(e))
    finally:
        pool.putconn(conn)


# ── Stage-1 per-finding approve/reject ────────────────────────────────────────
# REST mirror of the chat surface ([[hitl-two-stage-approval-design]] Stage 1).
# Chat path uses approve_findings_for_control (whole-control); these endpoints
# use approve_findings_by_ids so the UI can act per-finding or in bulk across
# multiple controls. Same posture aggregate logic, recomputed from ALL
# approved+active rows so partial approvals don't overwrite each other.

class FindingActionRequest(BaseModel):
    finding_ids: list[str]
    rationale:   Optional[str] = None   # required for reject


@app.post("/api/v1/findings/approve", tags=["hitl"])
async def findings_approve(
    body:     FindingActionRequest,
    request:  Request,
    key_info: APIKeyInfo = Depends(require_scope("hitl")),
):
    if not body.finding_ids:
        raise HTTPException(
            400,
            "Please select at least one finding to act on."
        )
    from rag.posture.stage1_review_chat import approve_findings_by_ids

    pool = request.app.state.pg_pool
    conn = pool.getconn()
    try:
        set_session(conn, key_info.tenant_id, key_info.user_id)
        result = approve_findings_by_ids(
            conn,
            tenant_id    = key_info.tenant_id,
            finding_ids  = body.finding_ids,
            reviewed_by  = key_info.user_id or "chat_user",
        )
        if result.get("ok"):
            cache = request.app.state.tenant_cache
            if cache:
                cache.invalidate(key_info.tenant_id)
            return result
        if result.get("reason") == "no_pending":
            raise HTTPException(404, "No pending findings match the supplied IDs")
        raise HTTPException(500, result.get("error", "approve failed"))
    finally:
        pool.putconn(conn)


@app.post("/api/v1/findings/reject", tags=["hitl"])
async def findings_reject(
    body:     FindingActionRequest,
    request:  Request,
    key_info: APIKeyInfo = Depends(require_scope("hitl")),
):
    if not body.finding_ids:
        raise HTTPException(
            400,
            "Please select at least one finding to act on."
        )
    if not body.rationale or not body.rationale.strip():
        raise HTTPException(
            400,
            "Please explain why you're rejecting — the reason is recorded "
            "for the audit trail."
        )
    from rag.posture.stage1_review_chat import reject_findings_by_ids

    pool = request.app.state.pg_pool
    conn = pool.getconn()
    try:
        set_session(conn, key_info.tenant_id, key_info.user_id)
        result = reject_findings_by_ids(
            conn,
            tenant_id    = key_info.tenant_id,
            finding_ids  = body.finding_ids,
            rationale    = body.rationale,
            reviewed_by  = key_info.user_id or "chat_user",
        )
        if result.get("ok"):
            return result
        if result.get("reason") == "no_pending":
            raise HTTPException(404, "No pending findings match the supplied IDs")
        raise HTTPException(500, result.get("error", "reject failed"))
    finally:
        pool.putconn(conn)


# ── Stage-1 read endpoints ────────────────────────────────────────────────────
# REST mirror of `what findings need review?` and `pending findings for X`
# chat surfaces. The UI uses these to render the Stage-1 review tab; the
# write side is /api/v1/findings/{approve,reject} which take finding_ids.

@app.get("/api/v1/stage1/queue", tags=["hitl"])
async def stage1_queue(
    request:  Request,
    key_info: APIKeyInfo = Depends(require_scope("hitl")),
):
    """List controls with pending document_findings, grouped by control_ref."""
    from rag.posture.stage1_review_chat import list_queue

    pool = request.app.state.pg_pool
    conn = pool.getconn()
    try:
        set_session(conn, key_info.tenant_id)
        controls = list_queue(conn, key_info.tenant_id)
        return {"controls": controls, "total": len(controls)}
    finally:
        pool.putconn(conn)


@app.get("/api/v1/stage1/queue/{control_ref}", tags=["hitl"])
async def stage1_queue_for_control(
    control_ref: ControlRefParam,
    request:     Request,
    key_info:    APIKeyInfo = Depends(require_scope("hitl")),
):
    """Per-control pending findings with excerpts, status, confidence."""
    from rag.posture.stage1_review_chat import list_pending_for_control

    pool = request.app.state.pg_pool
    conn = pool.getconn()
    try:
        set_session(conn, key_info.tenant_id)
        findings = list_pending_for_control(conn, key_info.tenant_id, control_ref)
        # Resolve the canonical control summary (title + obligation text)
        # from Neo4j so the detail surface can render "9.2 — Internal audit"
        # instead of just "9.2". Standard_id derived from the first finding
        # when available, otherwise lookup is best-effort across known
        # standards.
        from rag.posture_loader import _build_engine_neo4j_driver
        standard_id = (findings[0].get("inferred_from_standard_id") if findings else None)
        if not standard_id:
            # Look up via posture_controls row for this control
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT standard_id FROM posture_controls "
                    "WHERE tenant_id=%s AND control_ref=%s AND is_active=TRUE LIMIT 1",
                    (key_info.tenant_id, control_ref),
                )
                row = cur.fetchone()
                standard_id = row[0] if row else ""
        control_summary = {"standard_id": standard_id, "control_ref": control_ref,
                           "title": "", "description": ""}
        if standard_id:
            neo = _build_engine_neo4j_driver()
            if neo is not None:
                try:
                    control_summary = _resolve_control_summary(neo, standard_id, control_ref)
                finally:
                    try: neo.close()
                    except Exception: pass
        return {
            "control_ref":     control_ref,
            "control_summary": control_summary,
            "findings":        findings,
            "total":           len(findings),
        }
    finally:
        pool.putconn(conn)


# ── Stage-2 endpoints ─────────────────────────────────────────────────────────
# REST mirror of the Stage-2 engine-verdict approval chat surface. Approving
# here is the only path (besides the chat surface) that mutates
# posture_controls.finding for engine-proposed verdicts — Stage-1 confirms
# evidence only per [[stage1-contract-change-path-a-2026-05-25]].

class Stage2RejectRequest(BaseModel):
    rationale: str


@app.get("/api/v1/stage2/queue", tags=["hitl"])
async def stage2_queue(
    request:  Request,
    key_info: APIKeyInfo = Depends(require_scope("hitl")),
):
    """List posture_controls with engine_proposal_status='proposed'."""
    from rag.posture.stage2_approval_chat import list_pending_proposals

    pool = request.app.state.pg_pool
    conn = pool.getconn()
    try:
        set_session(conn, key_info.tenant_id)
        proposals = list_pending_proposals(conn, key_info.tenant_id)
        return {"proposals": proposals, "total": len(proposals)}
    finally:
        pool.putconn(conn)


@app.get("/api/v1/stage2/queue/{control_ref}", tags=["hitl"])
async def stage2_proposal_detail(
    control_ref: ControlRefParam,
    request:     Request,
    key_info:    APIKeyInfo = Depends(require_scope("hitl")),
):
    """Stage-2 detail: re-evaluate this control's engine verdict so the UI
    can render the derived_from chain (which children are satisfied vs
    pending) and the source framework. Persisted proposal_reason is just a
    short string ("ALL: 1/N satisfied") — the structured tree must be
    recomputed because we don't snapshot it at proposal time."""
    from rag.posture.stage2_approval_chat import get_proposal_for_control
    from rag.posture.engine_runner import evaluate_one_control
    from rag.posture_loader import _build_engine_neo4j_driver

    pool = request.app.state.pg_pool
    conn = pool.getconn()
    try:
        set_session(conn, key_info.tenant_id)
        proposal = get_proposal_for_control(conn, key_info.tenant_id, control_ref)
        if proposal is None:
            raise HTTPException(
                404,
                f"We don't have a posture entry for {control_ref} yet."
            )

        cid = f"{proposal['standard_id']}:{control_ref}"
        verdict = None
        control_summary = {"standard_id": proposal["standard_id"], "control_ref": control_ref,
                           "title": "", "description": ""}
        neo = _build_engine_neo4j_driver()
        if neo is not None:
            try:
                control_summary = _resolve_control_summary(
                    neo, proposal["standard_id"], control_ref,
                )
                v = evaluate_one_control(conn, neo, key_info.tenant_id, cid)
                if v is not None:
                    verdict = _serialize_verdict(v)
                    _enrich_titles(neo, verdict)
                    _enrich_leaf_sources(conn, key_info.tenant_id, verdict)
            finally:
                try: neo.close()
                except Exception: pass

        return {
            "control_ref":     control_ref,
            "standard_id":     proposal["standard_id"],
            "control_summary": control_summary,
            "proposal":        proposal,
            "verdict":         verdict,
        }
    finally:
        pool.putconn(conn)


# Engine reason strings are useful for debugging but read as machine output.
# Rewrite the two common patterns ('ALL: N/M children satisfied', 'N/M MUST
# items recognised; K unrecognised') into UI-friendly form. The structured
# verdict tree carries the same info, so this is purely cosmetic.
import re as _re
_REASON_ALL_RE = _re.compile(r"^ALL: (\d+)/(\d+) children satisfied$")
_REASON_LEAF_RE = _re.compile(r"^(\d+)/(\d+) MUST items recognised; (\d+) unrecognised$")


def _humanize_reason(s: str) -> str:
    if not s:
        return ""
    m = _REASON_ALL_RE.match(s)
    if m:
        sat, tot = int(m.group(1)), int(m.group(2))
        return f"{sat} of {tot} evidence sources satisfied"
    m = _REASON_LEAF_RE.match(s)
    if m:
        rec, tot, unr = int(m.group(1)), int(m.group(2)), int(m.group(3))
        if rec == 0:
            return f"No required items recognised yet ({unr} missing)"
        return f"{rec} of {tot} required items recognised ({unr} missing)"
    return s


def _serialize_verdict(v) -> dict:
    """Flatten a ControlVerdict + immediate derived_from chain into JSON.

    Recurses one level into derived_from so the UI can label each child as
    satisfied/pending without paying the full recursive walk cost. Direct
    leaves are flattened as siblings of derived children — both contribute
    to the parent's composition the same way."""
    children = []
    for leaf in (v.leaves or []):
        recognised = list(leaf.items_recognised or [])
        unrecognised = list(leaf.items_unrecognised or [])
        children.append({
            "kind":          "leaf",
            "evidence_type": leaf.evidence_type,
            "role":          leaf.role or None,
            "leaf_id":       leaf.leaf_id,
            "title":         "",  # filled by _enrich_titles
            "satisfied":     leaf.counts_as_comply,
            "reason":        _humanize_reason(leaf.reason or ""),
            "items_recognised":   recognised,
            "items_unrecognised": unrecognised,
            # Partial = not satisfied yet but at least one MUST is recognised.
            # The UI uses this to render a third state between ✓ and ✗.
            "partial":            (not leaf.counts_as_comply) and bool(recognised),
        })
    frameworks: set[str] = set()
    for role, sub in (v.derived_from or []):
        parts = (sub.control_id or "").rsplit(":", 1)
        sub_std = parts[0] if len(parts) == 2 else ""
        sub_ref = parts[1] if len(parts) == 2 else (sub.control_id or "")
        if sub_std:
            frameworks.add(sub_std)
        children.append({
            "kind":              "derived",
            "role":              role or None,
            "from_control_id":   sub.control_id,
            "from_standard":     sub_std,
            "from_control_ref":  sub_ref,
            "from_posture":      sub.posture,
            "title":             "",  # filled by _enrich_titles
            "satisfied":         sub.posture == "Comply",
            "reason":            _humanize_reason(sub.reason or ""),
        })
    return {
        "control_id":              v.control_id,
        "posture":                 v.posture,
        "applies":                 v.applies,
        "curation_status":         v.curation_status,
        "reason":                  _humanize_reason(v.reason or ""),
        "children":                children,
        "frameworks_derived_from": sorted(frameworks),
    }


# Module-level cache: leaf_id → set of all checklist_item_ids (MUST+SHOULD)
# the leaf owns. Built lazily on first call; same shape as the cache in
# stage1_review_chat.py but indexed reversely for fast per-leaf lookup.
_LEAF_ITEM_IDS_CACHE: Optional[dict[str, set[str]]] = None

def _leaf_item_ids() -> dict[str, set[str]]:
    global _LEAF_ITEM_IDS_CACHE
    if _LEAF_ITEM_IDS_CACHE is None:
        from enrichment.documents.document_requirements import (
            ALL_EVIDENCE_REQUIREMENTS, ALL_DERIVED_SPECS,
        )
        cache: dict[str, set[str]] = {}
        def add(er):
            cache[er.id] = {it.id for it in list(er.must_contain) + list(er.should_contain)}
        for er in ALL_EVIDENCE_REQUIREMENTS:
            add(er)
        for spec in ALL_DERIVED_SPECS:
            for er in spec.direct_evidence:
                add(er)
        _LEAF_ITEM_IDS_CACHE = cache
    return _LEAF_ITEM_IDS_CACHE


def _enrich_leaf_sources(pg_conn, tenant_id: str, verdict: dict) -> None:
    """For each leaf child in the verdict, attach `source_documents`: the
    list of {filename, document_id, evidence_type} for every uploaded
    document whose findings satisfy the leaf.

    Two binding paths are union'd:
      - Phase 2 (per-item): findings with `checklist_item_id` in the leaf's
        MUST+SHOULD set.
      - Phase 1 (coarse): findings on this control_ref whose source doc
        has `cd.evidence_type == leaf.evidence_type`.

    Filter: only 'present' / approved / active findings on current docs.
    Without this, the UI's verdict-tree leaf row shows only the curated
    leaf title (e.g. 'Information Security for Use of Cloud Services
    Policy') with no link to the actual source filename — making it hard
    for the reviewer to spot when one doc has been over-attributed across
    many controls. See [[a523_policy_attribution_2026_06_07]]."""
    if not verdict or not verdict.get("children"):
        return
    control_id = verdict.get("control_id") or ""
    if not control_id or ":" not in control_id:
        return
    # control_id is e.g. "ISO27001:2022:A.5.23"
    parts = control_id.rsplit(":", 1)
    standard_id = parts[0]
    control_ref = parts[1]

    leaf_children = [c for c in verdict["children"] if c.get("kind") == "leaf"]
    if not leaf_children:
        return

    # Collect the union of all leaf MUST+SHOULD item IDs across this control
    # so a single SQL query covers all of them.
    leaf_item_ids = _leaf_item_ids()
    all_item_ids: set[str] = set()
    leaf_id_to_items: dict[str, set[str]] = {}
    for c in leaf_children:
        lid = c.get("leaf_id")
        if lid and lid in leaf_item_ids:
            leaf_id_to_items[lid] = leaf_item_ids[lid]
            all_item_ids.update(leaf_item_ids[lid])

    # Single query per control: every 'present'+'approved' finding on this
    # control_ref with source doc info. Tag each row's matching leaf via
    # checklist_item_id (Phase-2) or cd.evidence_type (Phase-1).
    rows: list[tuple] = []
    try:
        with pg_conn.cursor() as cur:
            cur.execute("SELECT set_config('app.tenant_id', %s, TRUE)", (tenant_id,))
            cur.execute(
                """
                SELECT DISTINCT
                    df.checklist_item_id,
                    cd.id::text         AS doc_id,
                    cd.filename,
                    cd.evidence_type
                  FROM document_findings df
                  JOIN client_documents cd ON cd.id = df.document_id
                 WHERE df.tenant_id     = %s
                   AND df.control_ref   = %s
                   AND df.standard_id   = %s
                   AND df.status        = 'present'
                   AND df.review_status = 'approved'
                   AND df.is_active     = TRUE
                   AND cd.is_active     = TRUE
                   AND cd.is_current    = TRUE
                """,
                (tenant_id, control_ref, standard_id),
            )
            rows = cur.fetchall()
    except Exception:
        return  # best-effort; UI degrades to curated title only

    # Bucket per leaf
    for c in leaf_children:
        lid = c.get("leaf_id")
        leaf_et = c.get("evidence_type") or ""
        item_ids = leaf_id_to_items.get(lid, set())
        seen_doc_ids: set[str] = set()
        sources: list[dict] = []
        for item_id, doc_id, fname, doc_et in rows:
            # Match: per-item (Phase 2) OR coarse evidence_type (Phase 1)
            match = (item_id and item_id in item_ids) or (doc_et and doc_et == leaf_et)
            if not match: continue
            if doc_id in seen_doc_ids: continue
            seen_doc_ids.add(doc_id)
            sources.append({
                "document_id":   doc_id,
                "filename":      fname,
                "evidence_type": doc_et,
            })
        c["source_documents"] = sources


def _resolve_control_summary(neo4j_driver, standard_id: str, control_ref: str) -> dict:
    """Look up RequirementNode title + (where populated) description for a
    control. Used by Stage-1/Stage-2 detail surfaces so the user sees what
    e.g. '9.2' actually means without needing prior context.

    Returns {title, description, standard_id, control_ref}. Best-effort:
    any Neo4j failure returns empty title/description so the UI degrades
    gracefully to the ref-only display."""
    out = {
        "standard_id": standard_id,
        "control_ref": control_ref,
        "title":       "",
        "description": "",
    }
    if neo4j_driver is None:
        return out
    cid = f"{standard_id}:{control_ref}"
    try:
        with neo4j_driver.session() as s:
            row = s.run(
                "MATCH (n) WHERE n.id = $id "
                "RETURN n.title AS title, "
                "       coalesce(n.obligation_text, n.business_description, "
                "                n.description, n.body, '') AS description "
                "LIMIT 1",
                id=cid,
            ).single()
            if row:
                out["title"]       = row["title"] or ""
                out["description"] = row["description"] or ""
    except Exception:
        pass
    return out


def _enrich_titles(neo4j_driver, verdict: dict) -> None:
    """Look up RequirementNode.title and EvidenceRequirement.title for every
    child in the verdict so the UI can render 'A.8.10 — Information deletion'
    instead of just 'A.8.10'. Mutates the verdict dict in place. Best-effort:
    any Neo4j failure leaves titles empty and the UI falls back to refs."""
    if not verdict or not verdict.get("children"):
        return
    ids = []
    for c in verdict["children"]:
        if c["kind"] == "leaf" and c.get("leaf_id"):
            ids.append(c["leaf_id"])
        elif c["kind"] == "derived" and c.get("from_control_id"):
            ids.append(c["from_control_id"])
    if not ids:
        return
    try:
        with neo4j_driver.session() as s:
            rs = s.run(
                "UNWIND $ids AS i "
                "OPTIONAL MATCH (n) WHERE n.id = i "
                "RETURN i AS id, n.title AS title",
                ids=ids,
            )
            titles = {row["id"]: (row["title"] or "") for row in rs}
    except Exception:
        return
    for c in verdict["children"]:
        if c["kind"] == "leaf":
            c["title"] = titles.get(c.get("leaf_id"), "") or ""
        else:
            c["title"] = titles.get(c.get("from_control_id"), "") or ""


@app.post("/api/v1/stage2/{control_ref}/approve", tags=["hitl"])
async def stage2_approve(
    control_ref: ControlRefParam,
    request:     Request,
    key_info:    APIKeyInfo = Depends(require_scope("hitl")),
):
    """Approve the engine verdict for one control. Flips posture_controls.finding
    to engine_proposed_finding, status to engine_confirmed."""
    from rag.posture.stage2_approval_chat import approve_engine_proposal

    pool = request.app.state.pg_pool
    conn = pool.getconn()
    try:
        set_session(conn, key_info.tenant_id, key_info.user_id)
        result = approve_engine_proposal(
            conn,
            tenant_id   = key_info.tenant_id,
            control_ref = control_ref,
            reviewed_by = key_info.user_id or "chat_user",
        )
        if result.get("ok"):
            cache = request.app.state.tenant_cache
            if cache:
                cache.invalidate(key_info.tenant_id)
            return result
        reason = result.get("reason", "unknown")
        if reason in ("no_posture_row", "no_proposal"):
            raise HTTPException(
                404,
                f"There's no pending posture proposal for {control_ref} "
                f"— it may have already been approved or rejected."
            )
        if reason == "already_approved":
            raise HTTPException(
                409,
                f"The posture proposal for {control_ref} has already "
                f"been approved."
            )
        raise HTTPException(
            500,
            "Something went wrong while approving that proposal. Please try again."
        )
    finally:
        pool.putconn(conn)


@app.post("/api/v1/stage2/{control_ref}/reject", tags=["hitl"])
async def stage2_reject(
    control_ref: ControlRefParam,
    body:        Stage2RejectRequest,
    request:     Request,
    key_info:    APIKeyInfo = Depends(require_scope("hitl")),
):
    """Reject the engine verdict for one control. Sets status to 'rejected';
    posture_controls.finding is NOT touched."""
    if not body.rationale or not body.rationale.strip():
        raise HTTPException(
            400,
            "Please explain why you're rejecting — the reason is recorded "
            "for the audit trail."
        )
    from rag.posture.stage2_approval_chat import reject_engine_proposal

    pool = request.app.state.pg_pool
    conn = pool.getconn()
    try:
        set_session(conn, key_info.tenant_id, key_info.user_id)
        result = reject_engine_proposal(
            conn,
            tenant_id   = key_info.tenant_id,
            control_ref = control_ref,
            rationale   = body.rationale,
            reviewed_by = key_info.user_id or "chat_user",
        )
        if result.get("ok"):
            return result
        reason = result.get("reason", "unknown")
        if reason in ("no_posture_row", "no_proposal"):
            raise HTTPException(
                404,
                f"There's no pending posture proposal for {control_ref} "
                f"— it may have already been approved or rejected."
            )
        raise HTTPException(
            500,
            "Something went wrong while rejecting that proposal. Please try again."
        )
    finally:
        pool.putconn(conn)


# =============================================================================
# POSTURE ROUTER
# =============================================================================

@app.get("/api/v1/posture", tags=["posture"])
async def posture_summary(
    request:     Request,
    key_info:    APIKeyInfo = Depends(require_scope("posture")),
    standard_id: Optional[str] = None,
):
    """Full posture summary for the tenant."""
    pool = request.app.state.pg_pool
    conn = pool.getconn()
    try:
        set_session(conn, key_info.tenant_id)
        with conn.cursor() as cur:
            params = [key_info.tenant_id]
            std_filter = ""
            if standard_id:
                std_filter = "AND standard_id = %s"
                params.append(standard_id)

            cur.execute(f"""
                SELECT
                    standard_id,
                    finding,
                    confirmation_status,
                    COUNT(*) as count
                FROM posture_controls
                WHERE tenant_id = %s::uuid
                  AND is_active = TRUE
                  AND finding   != 'Not assessed'
                  {std_filter}
                GROUP BY standard_id, finding, confirmation_status
                ORDER BY standard_id, finding
            """, params)
            rows = cur.fetchall()

        summary: dict = {}
        for std, finding, conf_status, count in rows:
            if std not in summary:
                summary[std] = {
                    "NC": 0, "OFI": 0, "Comply": 0, "N/A": 0,
                    "confirmed": 0, "draft": 0, "overridden": 0,
                }
            summary[std][finding]     = summary[std].get(finding, 0) + count
            summary[std][conf_status] = summary[std].get(conf_status, 0) + count

        return {
            "tenant_id": key_info.tenant_id,
            "standards": summary,
            "trace_id":  request.state.trace_id,
        }
    finally:
        pool.putconn(conn)


_ISO_THEME_PREFIX = (
    ("A.5.", "Organisational (A.5)"),
    ("A.6.", "People (A.6)"),
    ("A.7.", "Physical (A.7)"),
    ("A.8.", "Technological (A.8)"),
)

_STANDARD_DISPLAY = {
    "ISO27001:2022": "ISO 27001:2022",
    "ISO27701:2019": "ISO 27701:2019",
    "GDPR:2016/679": "GDPR (EU 2016/679)",
}


def _iso_theme(control_ref: str) -> str:
    """Bucket an ISO 27001 control_ref into its Annex A theme or body
    clauses. Body clauses (no A. prefix) go to Management."""
    for prefix, label in _ISO_THEME_PREFIX:
        if control_ref.startswith(prefix):
            return label
    return "Management (4–10)"


def _gdpr_theme(control_ref: str) -> str:
    """Bucket a GDPR Art.* ref into a chapter group. Just two buckets
    for v1: Principles (1–11) vs Controller-and-beyond (12+). Articles
    we can't parse fall to 'Other'."""
    try:
        # Art.5.1.a → leading number after 'Art.'
        head = control_ref.split(".")[1]
        num = int("".join(c for c in head if c.isdigit()))
    except (ValueError, IndexError):
        return "Other GDPR articles"
    if num <= 11:
        return "Principles & lawfulness (Art.1–11)"
    return "Controller, transfers & rights (Art.12+)"


def _infer_standard_from_ref(control_ref: str) -> str:
    """Map a bare control_ref to its standard_id when the caller didn't
    supply one. Aligns with rag/intake/extractor._control_ref_to_standard.

    ISO 27701 disambiguation (see [[posture-controls-ref-format]]):
      Art.*         → GDPR
      B.8.*         → 27701 (processor annex)
      A.7.x.y (3+ dots) → 27701 controllers (A.7.2.1, A.7.3.2, ...)
      A.7.x   (2 dots)  → 27001 Annex A physical controls (A.7.1, A.7.4)
      Everything else → 27001 (A.5.*, A.6.*, A.8.*, ISMS body 4.x-10.x)
    """
    if not control_ref:
        return "ISO27001:2022"
    if control_ref.startswith("Art."):
        return "GDPR:2016/679"
    if control_ref.startswith("B.8."):
        return "ISO27701:2019"
    if control_ref.startswith("A.7."):
        tail = control_ref[4:]
        if "." in tail:
            return "ISO27701:2019"
    return "ISO27001:2022"


def _control_sort_key(control_ref: str) -> tuple:
    """Natural sort: A.5.1 < A.5.2 < A.5.10, Art.5 < Art.5.1 < Art.5.1.a."""
    parts = control_ref.replace("A.", "").replace("Art.", "").split(".")
    out = []
    for p in parts:
        if p.isdigit():
            out.append((0, int(p), ""))
        else:
            # Mixed e.g. "1a" — split numeric prefix from suffix
            num = ""
            i = 0
            while i < len(p) and p[i].isdigit():
                num += p[i]
                i += 1
            out.append((0, int(num) if num else 0, p[i:]))
    return tuple(out)


@app.get("/api/v1/dashboard/posture", tags=["posture"])
async def dashboard_posture(
    request:  Request,
    key_info: APIKeyInfo = Depends(require_scope("posture")),
):
    """Tenant-scoped heatmap view: every framework in scope, grouped
    by Annex A theme (ISO 27001) or chapter (GDPR), with per-control
    finding and a short gap excerpt suitable for hover/detail rendering.

    Tenant-agnostic — pulls from posture_controls + scope inference, no
    Arion-specific assumptions. Frameworks not in tenant scope are
    suppressed even if the DB has stray rows."""
    pool = request.app.state.pg_pool
    conn = pool.getconn()
    try:
        set_session(conn, key_info.tenant_id)
        with conn.cursor() as cur:
            cur.execute("""
                SELECT pc.standard_id, pc.control_ref, pc.finding,
                       pc.confirmation_status,
                       LEFT(COALESCE(pc.gap_description,''), 200) AS gap_excerpt,
                       pc.engine_proposal_status,
                       pa.finding                        AS engine_proposed_finding,
                       pa.gap_description                AS engine_proposal_reason,
                       LEFT(COALESCE(pc.action_required,''), 200) AS action_excerpt
                  FROM posture_controls pc
                  LEFT JOIN posture_assertions pa
                    ON pa.tenant_id   = pc.tenant_id
                   AND pa.control_ref = pc.control_ref
                   AND pa.standard_id = pc.standard_id
                   AND pa.source      = 'engine'
                   AND pa.status      = 'pending'
                 WHERE pc.tenant_id = %s::uuid
                   AND pc.is_active = TRUE
                 ORDER BY pc.standard_id, pc.control_ref
            """, [key_info.tenant_id])
            rows = cur.fetchall()

        # ── S3e: cascade pressure overlay ────────────────────────────
        # Read-only aggregation of triggered_implication rows; surfaces
        # alongside each control. Pure observability — does NOT modify
        # the live posture verdict here (the optional posture-flipping
        # overlay runs in load_posture, writes pending PAs through
        # Stage-2 like other engine proposals).
        try:
            from rag.cascade.posture_overlay import compute_cascade_pressure
            cascade_pressure = compute_cascade_pressure(conn, key_info.tenant_id)
        except Exception as ex:
            logger.warning("cascade pressure overlay failed: %s", ex)
            cascade_pressure = {}

        # Bucket controls by (standard, theme).
        by_std: dict = {}
        for (std, ref, finding, conf, gap, eng_status, eng_finding,
             eng_reason, action) in rows:
            entry = by_std.setdefault(std, {"groups": {}, "summary": {
                "NC": 0, "OFI": 0, "Comply": 0, "N/A": 0,
                "Not assessed": 0, "total": 0,
            }})
            theme = _iso_theme(ref) if std.startswith("ISO27001") else (
                _gdpr_theme(ref) if std.startswith("GDPR") else "All controls"
            )
            # gap_description is sparse for engine-derived (GDPR-via-xfw)
            # rows; fall back to the humanized engine reason so the detail
            # panel isn't empty. Comply rows with gap_description prose
            # surface as evidence text (see context_assembler relabel for
            # the chat side).
            display_gap = gap or _humanize_reason(eng_reason or "")
            req_id = f"{std}:{ref}"
            cp = cascade_pressure.get(req_id) or {}
            entry["groups"].setdefault(theme, []).append({
                "control_ref":              ref,
                "finding":                  finding,
                "confirmation_status":      conf,
                "gap_excerpt":              display_gap,
                "action_excerpt":           action or "",
                "engine_proposal_status":   eng_status,
                "engine_proposed_finding":  eng_finding,
                "engine_proposal_reason":   _humanize_reason(eng_reason or ""),
                "cascade_pressure":         {
                    "pending":   cp.get("pending_count",   0),
                    "overdue":   cp.get("overdue_count",   0),
                    "satisfied": cp.get("satisfied_count", 0),
                } if cp else None,
            })
            entry["summary"][finding] = entry["summary"].get(finding, 0) + 1
            entry["summary"]["total"] += 1

        # Order groups: ISO themes in Annex order then Management;
        # GDPR by chapter; others alphabetical.
        _iso_order = [lbl for _, lbl in _ISO_THEME_PREFIX] + ["Management (4–10)"]
        _gdpr_order = [
            "Principles & lawfulness (Art.1–11)",
            "Controller, transfers & rights (Art.12+)",
            "Other GDPR articles",
        ]

        # Load role model metadata (schema_v60): role + subject per
        # standard. Used by the three-lens dashboard restructure
        # (Phase 4b, 2026-07-05) to group frameworks by their compliance-
        # stack position. Silent fallback: role/subject may be None if
        # the standard hasn't been backfilled yet.
        role_meta: dict = {}
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT id, role, subject FROM standards WHERE id = ANY(%s)",
                    ([std for std in by_std.keys()],),
                )
                for sid, role, subject in cur.fetchall():
                    role_meta[sid] = {
                        "role":    role,
                        "subject": list(subject or []),
                    }
        except Exception as ex:
            logger.warning("dashboard role_meta lookup failed: %s", ex)

        frameworks = []
        for std, entry in by_std.items():
            if std.startswith("ISO27001"):
                ordered = _iso_order
            elif std.startswith("GDPR"):
                ordered = _gdpr_order
            else:
                ordered = sorted(entry["groups"].keys())
            groups_out = []
            for label in ordered:
                ctrls = entry["groups"].get(label)
                if not ctrls:
                    continue
                ctrls.sort(key=lambda c: _control_sort_key(c["control_ref"]))
                groups_out.append({"label": label, "controls": ctrls})

            meta = role_meta.get(std, {})
            frameworks.append({
                "standard_id":  std,
                "display_name": _STANDARD_DISPLAY.get(std, std),
                "role":         meta.get("role"),
                "subject":      meta.get("subject", []),
                "summary":      entry["summary"],
                "groups":       groups_out,
            })

        # Order frameworks by role (PROGRAM → EXTENSION → OBLIGATION),
        # then by legacy hardcoded rank for stable ordering within each
        # role. The role model view (three-lens) uses this same order,
        # rendering role-band headers as it scans down the list.
        _role_rank = {"program": 0, "extension": 1, "obligation": 2, "guidance": 3}
        def _std_rank(s):
            if s.startswith("ISO27001"): return 0
            if s.startswith("ISO27701"): return 1
            if s.startswith("GDPR"):     return 2
            return 9
        frameworks.sort(key=lambda f: (
            _role_rank.get(f.get("role"), 9),
            _std_rank(f["standard_id"]),
            f["standard_id"],
        ))

        return {
            "tenant_id":  key_info.tenant_id,
            "frameworks": frameworks,
            "trace_id":   request.state.trace_id,
        }
    finally:
        pool.putconn(conn)


@app.get("/api/v1/dashboard/control/{control_ref}/evidence", tags=["posture"])
async def dashboard_control_evidence(
    control_ref: ControlRefParam,
    request:     Request,
    key_info:    APIKeyInfo = Depends(require_scope("posture")),
):
    """Approved document_findings for one control — the source evidence
    that backs a Comply rating (or pre-decision excerpts for any other
    finding). Lets the Dashboard detail panel answer "why is this
    Comply?" when the posture_controls.gap_description column is empty
    (a common state for older intake rows where no narrative was
    written)."""
    pool = request.app.state.pg_pool
    conn = pool.getconn()
    try:
        set_session(conn, key_info.tenant_id)
        with conn.cursor() as cur:
            cur.execute("""
                SELECT df.status, df.confidence,
                       LEFT(COALESCE(df.excerpt,''), 280) AS excerpt,
                       df.section_number, df.page_number,
                       df.standard_id,
                       cd.document_title, cd.filename, cd.external_ref,
                       df.extracted_at::text
                  FROM document_findings df
                  LEFT JOIN client_documents cd ON cd.id = df.document_id
                 WHERE df.tenant_id     = %s::uuid
                   AND df.control_ref   = %s
                   AND df.is_active     = TRUE
                   AND df.review_status = 'approved'
                 ORDER BY df.extracted_at DESC
            """, [key_info.tenant_id, control_ref])
            cols = [d[0] for d in cur.description]
            findings = [dict(zip(cols, r)) for r in cur.fetchall()]

        # Group by document to deduplicate. If multiple findings cite the
        # same document, return one row per (document, status) pair with
        # the first / best excerpt — the dashboard doesn't need every
        # extraction attempt, just enough to answer "which docs back this?".
        seen = {}
        for f in findings:
            key = (f.get("document_title") or f.get("filename") or "(unknown source)", f["status"])
            if key not in seen:
                seen[key] = f
        unique = list(seen.values())

        return {
            "control_ref": control_ref,
            "findings":    unique,
            "total":       len(unique),
            "trace_id":    request.state.trace_id,
        }
    finally:
        pool.putconn(conn)



@app.get("/api/v1/dashboard/control/{control_ref}/evidence-classes", tags=["posture"])
async def dashboard_control_evidence_classes(
    control_ref: ControlRefParam,
    request:     Request,
    key_info:    APIKeyInfo = Depends(require_scope("posture")),
    standard_id: Optional[str] = None,
):
    """Per-control evidence-class breakdown for the dashboard drill-in.

    Groups the control's leaves by evidence_type (policy / procedure /
    register / review_record / scope_note / ...) and reports per-class
    coverage. Lets the tenant see at a glance:

      "5/8 policy MUSTs covered (Access Control Policy.docx);
       0/12 procedure MUSTs — use the template;
       0/6 register MUSTs — use the form."

    Action: each missing class can drive a template download / form
    open (template_available flag per leaf).

    See [[llm-narrative-under-discovery-audit-2026-06-26]] for the
    audit dive that established this UX as the real product lever.
    """
    if not standard_id:
        standard_id = _infer_standard_from_ref(control_ref)

    pool = request.app.state.pg_pool
    conn = pool.getconn()
    try:
        from rag.posture.advisory import build_evidence_class_breakdown
        data = build_evidence_class_breakdown(
            pg_conn     = conn,
            tenant_id   = key_info.tenant_id,
            control_ref = control_ref,
            standard_id = standard_id,
        )
        return {
            "control_ref": control_ref,
            "standard_id": standard_id,
            "breakdown":   data,
            "trace_id":    request.state.trace_id,
        }
    finally:
        pool.putconn(conn)


@app.get("/api/v1/dashboard/control/{control_ref}/advisory", tags=["posture"])
async def dashboard_control_advisory(
    control_ref: ControlRefParam,
    request:     Request,
    key_info:    APIKeyInfo = Depends(require_scope("posture")),
    standard_id: Optional[str] = None,
):
    """Per-MUST advisory data for one control — the structured form of
    what the chat appendix renders as markdown. Dashboard drill-in cards
    consume this to show per-leaf coverage with ✓/✗ icons, missing
    fulfilment criteria, and upload hints.

    Returns 200 with `advisory: null` when no advisory is warranted
    (control is Comply / N/A, all MUSTs satisfied, or control not
    multi-leaf curated). Returns 200 with structured data otherwise.

    See [[per-must-advisory-2026-06-14]] for the data path.
    """
    # Infer standard from control_ref shape if not supplied
    if not standard_id:
        standard_id = _infer_standard_from_ref(control_ref)

    pool = request.app.state.pg_pool
    conn = pool.getconn()
    try:
        from rag.posture.advisory import build_per_must_advisory_data
        data = build_per_must_advisory_data(
            pg_conn     = conn,
            tenant_id   = key_info.tenant_id,
            control_ref = control_ref,
            standard_id = standard_id,
        )
        return {
            "control_ref": control_ref,
            "standard_id": standard_id,
            "advisory":    data,
            "trace_id":    request.state.trace_id,
        }
    finally:
        pool.putconn(conn)



@app.get("/api/v1/dashboard/control/{control_ref}/demonstrated-by",
         tags=["posture"])
async def dashboard_control_demonstrated_by(
    control_ref: ControlRefParam,
    request:     Request,
    key_info:    APIKeyInfo = Depends(require_scope("posture")),
    standard_id: Optional[str] = None,
):
    """Framework role model provenance for OBLIGATION controls.

    Returns the list of PROGRAM/EXTENSION controls that contribute to
    demonstrating this obligation, along with their current findings
    and the aggregated `propagated_finding`. Data is populated by
    posture_loader._apply_demonstrates_overlay (Phase 2b/2c) and cached
    in the tenant_context posture dict; this endpoint just surfaces it
    to the UI drill-in.

    Returns 200 with `demonstrated_by: null` when the control is not
    an obligation, has no demonstrators in the tenant's scope, or the
    tenant_context cache is unavailable. Returns 200 with the list
    otherwise.
    """
    if not standard_id:
        standard_id = _infer_standard_from_ref(control_ref)

    cache = request.app.state.tenant_cache
    if cache is None:
        return {
            "control_ref":         control_ref,
            "standard_id":         standard_id,
            "demonstrated_by":     None,
            "propagated_finding":  None,
            "trace_id":            request.state.trace_id,
        }

    ctx    = cache.load(key_info.tenant_id)
    posture = (ctx.posture if ctx else {}) or {}
    node_id = f"{standard_id}:{control_ref}"
    rec     = posture.get(node_id) or {}

    # Ship 52 addendum — enrich each demonstrator with its Neo4j
    # title so the SPA drill-in can render "A.8.24 · Use of
    # cryptography" instead of "A.8.24" alone. Batched to one Cypher
    # round-trip per drill-in regardless of how many demonstrators
    # the obligation has. Best-effort — a Neo4j failure leaves titles
    # empty and the UI degrades to ref-only.
    demonstrated = list(rec.get("demonstrated_by") or [])
    if demonstrated:
        try:
            from rag.posture_loader import _build_engine_neo4j_driver
            neo_drv = _build_engine_neo4j_driver()
        except Exception:
            neo_drv = None
        if neo_drv is not None:
            ids = [d.get("src_id") for d in demonstrated if d.get("src_id")]
            titles: dict[str, str] = {}
            try:
                with neo_drv.session() as s:
                    for row in s.run(
                        "UNWIND $ids AS nid "
                        "MATCH (n) WHERE n.id = nid "
                        "RETURN n.id AS id, n.title AS title",
                        ids=ids,
                    ):
                        titles[row["id"]] = row["title"] or ""
            except Exception:
                titles = {}
            for d in demonstrated:
                d["src_title"] = titles.get(d.get("src_id"), "")

    return {
        "control_ref":         control_ref,
        "standard_id":         standard_id,
        "demonstrated_by":     demonstrated or None,
        "propagated_finding":  rec.get("propagated_finding"),
        "current_finding":     rec.get("finding"),
        "materialised":        rec.get("source") == "demonstrates_propagation",
        "trace_id":            request.state.trace_id,
    }


# ── Ship 54'.b — advisory topic bundles ────────────────────────────────
#
# Topic bundles group per-leaf templates into compliance workflow
# bundles (DSR, incident response, consent, etc.). Data source:
# db/topics/*.yaml → Postgres topics + topic_leaves tables (loaded
# via enrichment/topics/load_to_postgres.py). Per-topic verdict
# roll-up joins topic_leaves ⋈ posture_controls at request time.
#
# Two endpoints:
#   GET /api/v1/advisory/topics       — list with per-topic roll-up
#   GET /api/v1/advisory/topics/{slug} — bundle detail per-leaf status
#
# See db/topics/README.md + docs/memory/ship_54_prime_a for design.

def _classify_framework_role(leaf_id: str) -> str:
    """Derive Program / Extension / Obligation from leaf_id pattern.
    Same derivation used in the Ship 54'.a audit query. Kept as a
    module-level helper so future consumers (chat, SPA, external
    API) share it."""
    if leaf_id.startswith("req:Art."):
        return "obligation"
    if leaf_id.startswith("req:A.7.") or leaf_id.startswith("req:B.8."):
        return "extension"
    if leaf_id.startswith("req:A."):
        return "program"
    # ISO 27001 ISMS body clauses (4.1, 5.2, 6.1.2, ...)
    _rest = leaf_id[4:] if leaf_id.startswith("req:") else leaf_id
    if _rest and _rest[0].isdigit():
        return "program"
    return "other"


def _control_ref_from_leaf_id(leaf_id: str) -> str:
    """Extract the control_ref portion (e.g., 'A.5.15' from
    'req:A.5.15:communication_record'). Mirrors what
    load_posture reads from posture_controls.control_ref."""
    parts = leaf_id.split(":")
    return parts[1] if len(parts) >= 2 else ""


@app.get("/api/v1/advisory/topics", tags=["posture"])
async def advisory_topics_list(
    request:  Request,
    key_info: APIKeyInfo = Depends(require_scope("posture")),
):
    """Return the curated list of topic bundles with per-topic
    verdict roll-up + framework-role composition.

    Data source: `topics` + `topic_leaves` (Ship 54'.a schema_v91).
    Roll-up: LEFT JOIN topic_leaves ⋈ posture_controls with tenant
    RLS applied. Leaves without posture entries count as 'unassessed'.

    Framework-role counts (program / extension / obligation) derived
    from leaf_id pattern per `_classify_framework_role`.
    """
    pool = request.app.state.pg_pool
    conn = pool.getconn()
    try:
        set_session(conn, key_info.tenant_id)
        with conn.cursor() as cur:
            cur.execute("""
                SELECT slug, title, description, primary_framework,
                       auditor_expects, display_order
                  FROM topics
                 ORDER BY display_order, slug
            """)
            topics = cur.fetchall()

            cur.execute("""
                SELECT tl.topic_slug, tl.leaf_id, tl.role, tl.workflow_order,
                       tl.role_note, pc.finding
                  FROM topic_leaves tl
                  LEFT JOIN posture_controls pc
                    ON  pc.tenant_id   = %s::uuid
                    AND pc.control_ref = split_part(tl.leaf_id, ':', 2)
                    AND pc.is_active   = TRUE
                 ORDER BY tl.topic_slug, tl.workflow_order, tl.leaf_id
            """, [key_info.tenant_id])
            leaves = cur.fetchall()

        # Group leaves by topic + roll up
        by_topic: dict[str, dict] = {}
        for (slug, leaf_id, role, workflow_order, role_note, finding) in leaves:
            entry = by_topic.setdefault(slug, {
                "verdict_counts": {
                    "Comply": 0, "OFI": 0, "NC": 0, "N/A": 0, "unassessed": 0,
                },
                "framework_role_counts": {
                    "program": 0, "extension": 0, "obligation": 0, "other": 0,
                },
                "leaf_count": 0,
            })
            entry["leaf_count"] += 1
            entry["verdict_counts"][finding or "unassessed"] = \
                entry["verdict_counts"].get(finding or "unassessed", 0) + 1
            fr = _classify_framework_role(leaf_id)
            entry["framework_role_counts"][fr] = \
                entry["framework_role_counts"].get(fr, 0) + 1

        result = []
        for (slug, title, description, primary_framework,
             auditor_expects, display_order) in topics:
            roll = by_topic.get(slug, {})
            result.append({
                "slug":                  slug,
                "title":                 title,
                "description":           description,
                "primary_framework":     primary_framework,
                "auditor_expects":       auditor_expects,
                "display_order":         display_order,
                "leaf_count":            roll.get("leaf_count", 0),
                "verdict_counts":        roll.get("verdict_counts", {}),
                "framework_role_counts": roll.get("framework_role_counts", {}),
            })

        return {
            "topics":   result,
            "trace_id": request.state.trace_id,
        }
    finally:
        pool.putconn(conn)


@app.get("/api/v1/advisory/topics/{slug}", tags=["posture"])
async def advisory_topic_detail(
    slug:     str,
    request:  Request,
    key_info: APIKeyInfo = Depends(require_scope("posture")),
):
    """Return a topic bundle with per-leaf posture status +
    workflow order. Returns 404 when the slug is unknown.

    Each leaf carries:
      leaf_id           — canonical req:X:Y
      control_ref       — extracted A.5.15 / Art.15 / etc.
      leaf_type         — the third segment (e.g., 'communication_record')
      role              — per-topic role (primary_procedure/register/etc.)
      workflow_order    — 1..N ordering within the topic
      role_note         — optional consultant-authored note
      framework_role    — program / extension / obligation (derived)
      finding           — current posture (NC/OFI/Comply/N/A) or null
      gap_excerpt       — first 200 chars of gap_description (posture)
      template_available — bool (whether a db/templates/req__*.md exists)
    """
    # Slug shape guard — kebab-case slugs only
    import re as _re
    if not _re.match(r"^[a-z][a-z0-9_-]{0,63}$", slug or ""):
        raise HTTPException(status_code=400, detail="invalid topic slug shape")

    pool = request.app.state.pg_pool
    conn = pool.getconn()
    try:
        set_session(conn, key_info.tenant_id)
        with conn.cursor() as cur:
            cur.execute("""
                SELECT title, description, primary_framework, auditor_expects,
                       display_order
                  FROM topics WHERE slug = %s
            """, [slug])
            row = cur.fetchone()
            if not row:
                raise HTTPException(status_code=404, detail="topic not found")
            (title, description, primary_framework, auditor_expects,
             display_order) = row

            cur.execute("""
                SELECT tl.leaf_id, tl.role, tl.workflow_order, tl.role_note,
                       pc.finding,
                       LEFT(COALESCE(pc.gap_description,''), 200) AS gap_excerpt,
                       (t.leaf_id IS NOT NULL)                    AS template_available
                  FROM topic_leaves tl
                  LEFT JOIN posture_controls pc
                    ON  pc.tenant_id   = %s::uuid
                    AND pc.control_ref = split_part(tl.leaf_id, ':', 2)
                    AND pc.is_active   = TRUE
                  LEFT JOIN templates t ON t.leaf_id = tl.leaf_id
                 WHERE tl.topic_slug = %s
                 ORDER BY tl.workflow_order, tl.leaf_id
            """, [key_info.tenant_id, slug])
            leaves_rows = cur.fetchall()

        # Neo4j lookup for leaf titles + control titles (best-effort)
        leaf_ids   = [r[0] for r in leaves_rows]
        node_titles: dict[str, str] = {}
        try:
            from rag.posture_loader import _build_engine_neo4j_driver
            neo_drv = _build_engine_neo4j_driver()
            if neo_drv is not None:
                with neo_drv.session() as s:
                    # Look up EvidenceRequirement titles (leaf-level)
                    for row in s.run(
                        "UNWIND $ids AS lid "
                        "MATCH (er:EvidenceRequirement {id: lid}) "
                        "RETURN er.id AS id, er.title AS title",
                        ids=leaf_ids,
                    ):
                        node_titles[row["id"]] = row["title"] or ""
                    # Look up control-level titles too (for the ref shown
                    # in the UI, e.g., A.5.15 → "Access control")
                    refs = list({_control_ref_from_leaf_id(lid) for lid in leaf_ids})
                    for row in s.run(
                        "UNWIND $refs AS rf "
                        "MATCH (n:RequirementNode {ref: rf}) "
                        "RETURN n.ref AS ref, n.title AS title LIMIT 200",
                        refs=refs,
                    ):
                        # Namespace under a leaf_id-shaped key to avoid
                        # collision with leaf titles
                        node_titles[f"ctrl:{row['ref']}"] = row["title"] or ""
        except Exception as _e:
            logger.debug("topic detail neo4j title lookup failed: %s", _e)

        leaves = []
        for (leaf_id, role, workflow_order, role_note, finding,
             gap_excerpt, template_available) in leaves_rows:
            ctrl_ref = _control_ref_from_leaf_id(leaf_id)
            parts = leaf_id.split(":")
            leaf_type = parts[2] if len(parts) >= 3 else ""
            leaves.append({
                "leaf_id":            leaf_id,
                "control_ref":        ctrl_ref,
                "leaf_type":          leaf_type,
                "leaf_title":         node_titles.get(leaf_id, ""),
                "control_title":      node_titles.get(f"ctrl:{ctrl_ref}", ""),
                "role":               role,
                "workflow_order":     workflow_order,
                "role_note":          role_note,
                "framework_role":     _classify_framework_role(leaf_id),
                "finding":            finding,
                "gap_excerpt":        gap_excerpt or "",
                "template_available": bool(template_available),
            })

        # Roll-up mirrors list endpoint for consistency
        verdict_counts = {"Comply": 0, "OFI": 0, "NC": 0, "N/A": 0, "unassessed": 0}
        framework_role_counts = {"program": 0, "extension": 0, "obligation": 0, "other": 0}
        for lf in leaves:
            verdict_counts[lf["finding"] or "unassessed"] = \
                verdict_counts.get(lf["finding"] or "unassessed", 0) + 1
            framework_role_counts[lf["framework_role"]] = \
                framework_role_counts.get(lf["framework_role"], 0) + 1

        return {
            "slug":                  slug,
            "title":                 title,
            "description":           description,
            "primary_framework":     primary_framework,
            "auditor_expects":       auditor_expects,
            "display_order":         display_order,
            "leaf_count":            len(leaves),
            "verdict_counts":        verdict_counts,
            "framework_role_counts": framework_role_counts,
            "leaves":                leaves,
            "trace_id":              request.state.trace_id,
        }
    finally:
        pool.putconn(conn)


@app.get("/api/v1/posture/{control_ref}", tags=["posture"])
async def posture_control(
    control_ref: ControlRefParam,
    request:     Request,
    key_info:    APIKeyInfo = Depends(require_scope("posture")),
    standard_id: Optional[str] = None,
):
    """Get full detail for a specific control."""
    pool = request.app.state.pg_pool
    conn = pool.getconn()
    try:
        set_session(conn, key_info.tenant_id)
        with conn.cursor() as cur:
            params = [key_info.tenant_id, control_ref]
            std_filter = ""
            if standard_id:
                std_filter = "AND standard_id = %s"
                params.append(standard_id)

            cur.execute(f"""
                SELECT
                    id, control_ref, standard_id, finding,
                    gap_description, action_required, source,
                    confidence, confirmation_status,
                    system_finding, system_gap,
                    confirmed_at::text, updated_at::text
                FROM posture_controls
                WHERE tenant_id = %s::uuid
                  AND control_ref = %s
                  AND is_active   = TRUE
                  {std_filter}
                ORDER BY updated_at DESC
            """, params)
            rows = cur.fetchall()
            cols = [d[0] for d in cur.description]

        if not rows:
            raise HTTPException(404, f"Control not found: {control_ref}")

        return {
            "controls": [dict(zip(cols, r)) for r in rows],
            "trace_id": request.state.trace_id,
        }
    finally:
        pool.putconn(conn)


# =============================================================================
# ADMIN — GRAPH EXPLORER (internal debug, /graph page)
# =============================================================================

class CypherRequest(BaseModel):
    cypher: str
    params: Optional[dict] = None
    limit:  Optional[int]  = 500


_WRITE_KEYWORDS = (
    " CREATE ", " MERGE ", " DELETE ", " SET ", " REMOVE ",
    " DROP ", " DETACH ", " LOAD CSV", " CALL APOC.PERIODIC",
)


# ─── Ship 48'.c — deployment status ─────────────────────────────────
#
# Read-only endpoint returning non-sensitive metadata for support +
# Claude Code operator sessions. Complements scripts/ops/diagnose.sh
# (offline bundle). Scoped to `admin:status`.
#
# Privacy: no tenant names, user emails, evidence text, or raw API
# keys. Only counts, versions, health flags, framework identifiers.

@app.get("/api/v1/admin/deployment/status", tags=["admin"])
async def admin_deployment_status(
    request:  Request,
    key_info: APIKeyInfo = Depends(require_scope("admin:status")),
):
    """Live deployment status: version, uptime, service health,
    aggregate DB/graph/vector counts, tenant + framework summary,
    feature flags. Companion to scripts/ops/diagnose.sh."""
    from rag.admin.deployment_status import collect
    pool       = request.app.state.pg_pool
    started_at = getattr(request.app.state, "started_at", 0.0)
    return collect(pool, started_at)


@app.get("/api/v1/admin/intake/unmatched-patterns", tags=["admin"])
async def admin_unmatched_patterns(
    request:  Request,
    key_info: APIKeyInfo = Depends(require_api_key),
    limit:    int = 20,
    days:     int = 30,
):
    """Group recent uploads where doc_mappings didn't match by tokenized
    filename, return most common patterns as candidate umbrella YAMLs
    to author. Each row is a doc-shape that would benefit from a new
    `db/doc_mappings/*.yaml`.

    Source: intake_trace_log rows with doc_mappings_match_count=0
    in the last `days` days. Filenames are tokenized via the
    workbook_discovery tokenizer (the same one doc_mappings YAMLs
    use), so the returned tuples are valid fingerprint candidates."""
    pool = request.app.state.pg_pool
    conn = pool.getconn()
    try:
        set_session(conn, key_info.tenant_id, key_info.user_id)
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT filename, COUNT(*) AS n
                FROM intake_trace_log
                WHERE tenant_id = %s::uuid
                  AND stage     = 'extract'
                  AND doc_mappings_match_count = 0
                  AND traced_at > NOW() - (%s || ' days')::INTERVAL
                GROUP BY filename
                ORDER BY n DESC
                LIMIT %s
                """,
                (key_info.tenant_id, days, limit * 5),
            )
            rows = cur.fetchall()

        from rag.intake.workbook_discovery import tokenize
        from pathlib import Path
        patterns: dict[tuple, dict] = {}
        for filename, count in rows:
            tokens = tuple(tokenize(Path(filename).stem))
            if not tokens:
                continue
            patterns.setdefault(tokens, {"tokens": list(tokens), "n_uploads": 0, "examples": []})
            patterns[tokens]["n_uploads"] += count
            if filename not in patterns[tokens]["examples"]:
                patterns[tokens]["examples"].append(filename)

        out = sorted(patterns.values(), key=lambda p: -p["n_uploads"])[:limit]
        return {
            "since_days": days,
            "tenant_id":  key_info.tenant_id,
            "count":      len(out),
            "patterns":   out,
        }
    finally:
        pool.putconn(conn)


def _extraction_quality_flag(row: dict) -> tuple[str, str]:
    """Compute a red/yellow/green flag + one-line reason for an extract
    trace_log row. Returns (flag, reason).

    Yield ratio uses `primary_candidate_controls` (schema_v36) — the
    top-confidence doc_mappings match's target list — NOT the union.
    Falls back to `candidate_controls` when primary isn't populated
    (older rows pre-v36). The union still records what reached the
    LLM for cost/perf tracking; it's just not the right denominator
    for "did extraction find what it should have found"."""
    findings = row.get("findings_kept") or 0
    union_candidates = row.get("candidate_controls") or 0
    primary_candidates = row.get("primary_candidate_controls")
    # Use primary when available; otherwise fall back to union.
    candidates = primary_candidates if primary_candidates is not None else union_candidates
    # doc_mappings_match_count = 0 means the legacy _scope_controls fallback
    # fired (no curated mapping matched). The "candidates" then is a broad
    # clause-scope (often the 50-control cap), and yield ratio against it is
    # noise — there's no meaningful "expected" denominator. Surface the gap
    # via /admin/intake/unmatched-patterns instead.
    doc_mapping_matches = row.get("doc_mappings_match_count")
    is_legacy_fallback  = (doc_mapping_matches == 0)
    halluc = row.get("dropped_hallucinated") or 0
    md_chars = row.get("markdown_chars") or 0
    para_chars = row.get("paragraph_chars") or 0
    llm_calls = row.get("llm_calls") or 0
    # schema_v41 — doc-shape filter signals
    toc_reason  = row.get("skipped_as_toc")
    questionnaire = row.get("dropped_questionnaire") or 0
    # schema_v42 — crosscheck signals
    cx_confirmed     = row.get("crosscheck_confirmed") or 0
    cx_disagreements = row.get("crosscheck_disagreements") or 0

    # Per-doc binding rate (joined in admin_uploads_quality). When non-NULL
    # these are the count of active findings on the corresponding
    # client_documents row (matched via sha256). bound_findings is the
    # subset with checklist_item_id != NULL — the only findings that can
    # feed the engine post Phase-1 retirement.
    active_findings = row.get("active_findings")
    bound_findings  = row.get("bound_findings")

    # TOC skip — the filter prevented LLM calls entirely. RED because the
    # upload is wasted: no findings will ever come from it. Operator action
    # is to remove from active queue or re-upload as an actual policy.
    if toc_reason:
        return "red", f"skipped as TOC ({toc_reason})"
    if candidates > 0 and findings == 0:
        return "red", f"0 findings from {candidates} scoped controls"
    # Questionnaire dominance — when most LLM output got dropped as
    # per-question shape, the kept findings are residual descriptive
    # passages. Worth flagging even when yield ratio looks normal.
    if questionnaire > 0 and questionnaire >= max(findings, 1) * 2:
        return "yellow", f"questionnaire drops dominate ({questionnaire} dropped vs {findings} kept)"
    if halluc > findings and findings >= 0:
        return "yellow", f"hallucinated > kept ({halluc} > {findings})"
    # Inert findings — all active findings unbound (no checklist_item_id).
    # Post Phase-1 retirement (2026-06-13) these can't feed the engine,
    # so the upload's evidence value is purely audit-trail. Worth flagging
    # so the operator can see which uploads aren't influencing posture.
    if active_findings is not None and active_findings > 0 and (bound_findings or 0) == 0:
        return "yellow", f"all {active_findings} findings unbound (no checklist_item_id)"
    # Crosscheck disagreement dominance — when the LLM emitted MUST bindings
    # but the catalog fingerprints don't corroborate, the extractor and
    # catalog disagree on what the evidence actually demonstrates. Soft
    # signal (binding kept), tenant should triage.
    if cx_disagreements > 0 and cx_disagreements >= max(cx_confirmed, 1):
        return "yellow", f"crosscheck disagreement ({cx_disagreements} disagree vs {cx_confirmed} confirmed)"
    if candidates > 0 and findings * 5 < candidates and not is_legacy_fallback:
        return "yellow", f"yield ratio < 20% ({findings}/{candidates})"
    if md_chars > para_chars * 3 and md_chars > 2000 and llm_calls < max(1, md_chars // 50000):
        return "yellow", f"markdown ({md_chars}) under-chunked into {llm_calls} calls"
    return "green", "ok"


@app.get("/api/v1/admin/uploads/quality", tags=["admin"])
async def admin_uploads_quality(
    request:  Request,
    key_info: APIKeyInfo = Depends(require_api_key),
    limit:    int = 50,
    flag:     Optional[str] = None,   # red | yellow | None=all
):
    """Recent uploads with extraction-quality flag derived from
    intake_trace_log metrics (schema_v35). Use to spot under-extraction
    or hallucination patterns without reading per-doc logs.

    flag=red    — zero-yield extractions
    flag=yellow — low yield, hallucination, or under-chunked markdown
    omitted     — all rows, sorted worst-first
    """
    pool = request.app.state.pg_pool
    conn = pool.getconn()
    try:
        set_session(conn, key_info.tenant_id, key_info.user_id)
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT
                    itl.upload_id, itl.filename, itl.traced_at,
                    du.extraction_status,
                    itl.llm_calls, itl.findings_raw, itl.findings_kept,
                    itl.candidate_controls, itl.primary_candidate_controls,
                    itl.dropped_low_conf, itl.dropped_short_quote,
                    itl.dropped_hallucinated, itl.dropped_unknown_ref,
                    itl.dropped_questionnaire, itl.skipped_as_toc,
                    itl.crosscheck_confirmed, itl.crosscheck_disagreements,
                    itl.crosscheck_unavailable,
                    itl.markdown_chars, itl.paragraph_chars,
                    itl.total_ms, itl.extraction_path,
                    itl.doc_mappings_match_count,
                    df_agg.active_findings, df_agg.bound_findings
                FROM intake_trace_log itl
                LEFT JOIN document_uploads du ON du.id::text = itl.upload_id
                -- Bridge to client_documents via sha256 + tenant (no direct FK).
                -- Then aggregate active vs per-MUST-bound finding counts so the
                -- quality flag can detect inert-output uploads (findings exist
                -- but none have checklist_item_id → can't feed engine).
                LEFT JOIN client_documents cd
                  ON cd.checksum_sha256 = du.sha256
                 AND cd.tenant_id       = du.tenant_id
                LEFT JOIN LATERAL (
                    SELECT
                        COUNT(*) FILTER (WHERE df.is_active = TRUE) AS active_findings,
                        COUNT(*) FILTER (
                            WHERE df.is_active = TRUE
                              AND df.checklist_item_id IS NOT NULL
                        ) AS bound_findings
                    FROM document_findings df
                    WHERE df.document_id = cd.id
                ) df_agg ON TRUE
                WHERE itl.tenant_id = %s::uuid
                  AND itl.stage    = 'extract'
                ORDER BY itl.traced_at DESC
                LIMIT %s
                """,
                (key_info.tenant_id, max(limit * 3, 50)),
            )
            cols = [d[0] for d in cur.description]
            rows = [dict(zip(cols, r)) for r in cur.fetchall()]

        out: list[dict] = []
        for r in rows:
            f, reason = _extraction_quality_flag(r)
            if flag and f != flag:
                continue
            out.append({
                "upload_id":          r["upload_id"],
                "filename":           r["filename"],
                "extracted_at":       r["traced_at"].isoformat() if r["traced_at"] else None,
                "extraction_status":  r["extraction_status"],
                "extraction_path":    r["extraction_path"],
                "quality_flag":       f,
                "quality_reason":     reason,
                "llm_calls":          r["llm_calls"],
                "candidate_controls": r["candidate_controls"],
                "primary_candidate_controls": r["primary_candidate_controls"],
                "findings_kept":      r["findings_kept"],
                "drops": {
                    "low_conf":         r["dropped_low_conf"],
                    "short_quote":      r["dropped_short_quote"],
                    "hallucinated":     r["dropped_hallucinated"],
                    "unknown_ref":      r["dropped_unknown_ref"],
                    "questionnaire":    r["dropped_questionnaire"],
                },
                "skipped_as_toc":   r["skipped_as_toc"],
                "doc_mappings_match_count": r["doc_mappings_match_count"],
                "active_findings":  r["active_findings"],
                "bound_findings":   r["bound_findings"],
                "crosscheck": {
                    "confirmed":     r["crosscheck_confirmed"],
                    "disagreements": r["crosscheck_disagreements"],
                    "unavailable":   r["crosscheck_unavailable"],
                },
                "markdown_chars":   r["markdown_chars"],
                "paragraph_chars":  r["paragraph_chars"],
                "total_ms":         r["total_ms"],
            })

        # Sort: red first, then yellow, then green; within each flag, newest first.
        flag_rank = {"red": 0, "yellow": 1, "green": 2}
        out.sort(key=lambda x: (flag_rank.get(x["quality_flag"], 3), -(x["extracted_at"] is None), x["extracted_at"] or ""), reverse=False)
        # Within-flag reversal for time: use negative timestamp via secondary sort
        out_sorted: list[dict] = []
        for f in ("red", "yellow", "green"):
            bucket = [x for x in out if x["quality_flag"] == f]
            bucket.sort(key=lambda x: x["extracted_at"] or "", reverse=True)
            out_sorted.extend(bucket)
        out = out_sorted[:limit]
        return {"count": len(out), "uploads": out}
    finally:
        pool.putconn(conn)


# ─────────────────────────────────────────────────────────────────────────────
# Ship 6'.e (2026-07-19): joined LLM decision-trail endpoint.
#
# One row per chat turn joining chat_casefile_log ⋈ chat_consensus_log ⋈
# ai_call_log on request_id. Auditor + engineer surface for tracing a
# full LLM decision trail. Reads the `chat_llm_decision_trail` view
# (schema_v83).
# ─────────────────────────────────────────────────────────────────────────────

@app.get("/api/v1/admin/chat/decision-trail", tags=["admin"])
async def admin_chat_decision_trail(
    request:      Request,
    key_info:     APIKeyInfo         = Depends(require_api_key),
    request_id:   Optional[str]      = None,
    session_id:   Optional[str]      = None,
    hours:        int                = 24,
    limit:        int                = 50,
    only_repaired:      bool         = False,
    only_ungrounded:    bool         = False,
):
    """Recent chat turns with the joined LLM decision trail. Reads
    `chat_llm_decision_trail` (Ship 6'.e).

    Filters:
      request_id      — pin to a specific turn (returns 0 or 1 row)
      session_id      — all turns in a session (chronological)
      hours           — time window (default 24)
      only_repaired   — preservation-check fired ≥1 repair event
      only_ungrounded — case-file emitted a claim event whose ref
                        was NOT in the digest (risky)
    """
    hours = max(1, min(hours, 24 * 90))
    limit = max(1, min(limit, 500))

    where_clauses = ["turn_at > now() - (%s || ' hours')::interval"]
    params: list = [hours]
    if request_id:
        where_clauses.append("request_id = %s")
        params.append(request_id)
    if session_id:
        where_clauses.append("session_id = %s")
        params.append(session_id)
    if only_repaired:
        where_clauses.append("repair_events_count > 0")
    if only_ungrounded:
        # jsonb contains-any: at least one claim_events entry with
        # ref_in_digest = false. Passive scan already writes this flag.
        where_clauses.append(
            "claim_events @> '[{\"ref_in_digest\": false}]'::jsonb"
        )

    sql = f"""
        SELECT
            casefile_log_id, request_id, session_id, turn_at,
            query, question_type,
            consensus_verdict, consensus_top_refs, consensus_top_conf,
            consensus_corroborators, consensus_framework, consensus_llm_fallback,
            prompt_tokens_system, prompt_tokens_digest, prompt_tokens_total,
            repair_events_count, footers_added,
            digest_latency_ms, repair_latency_ms, total_latency_ms,
            claim_events_count, claim_events, answer_len,
            llm_n_calls, llm_tokens_in, llm_tokens_out, llm_cost_usd,
            llm_purposes, llm_models
        FROM chat_llm_decision_trail
        WHERE {' AND '.join(where_clauses)}
        ORDER BY turn_at DESC
        LIMIT %s
    """
    params.append(limit)

    pool = request.app.state.pg_pool
    conn = pool.getconn()
    try:
        set_session(conn, key_info.tenant_id, key_info.user_id)
        with conn.cursor() as cur:
            cur.execute(sql, tuple(params))
            cols = [d[0] for d in cur.description]
            rows = [dict(zip(cols, r)) for r in cur.fetchall()]

        # JSON-safe: cast timestamps + Decimals
        for r in rows:
            if r.get("turn_at") is not None:
                r["turn_at"] = r["turn_at"].isoformat()
            if r.get("llm_cost_usd") is not None:
                r["llm_cost_usd"] = float(r["llm_cost_usd"])

        return {"count": len(rows), "turns": rows}
    finally:
        pool.putconn(conn)


# ─────────────────────────────────────────────────────────────────────────────
# Wave 4c (2026-07-11): tenant trace dashboard endpoints.
#
# Read-only aggregations across the existing trace tables:
#   - ai_call_log         (Wave 4b)  per-LLM-call inventory
#   - intake_trace_log    (schema_v35) per-doc pipeline stages
#   - request_trace_log   per-chat-query classifier/retrieval trace
#   - posture_history     posture change trail
#
# All endpoints are tenant-scoped via the request's API key. The SPA
# `#trace` page consumes these to render the trace timeline.
# ─────────────────────────────────────────────────────────────────────────────

@app.get("/api/v1/trace/summary", tags=["trace"])
async def trace_summary(
    request:  Request,
    key_info: APIKeyInfo = Depends(require_api_key),
    hours:    int         = 24,
):
    """KPI rollup for the trace dashboard header. Returns totals for
    the last N hours: AI calls + cost, upload extractions, chat
    requests. Everything is tenant-scoped."""
    pool = request.app.state.pg_pool
    conn = pool.getconn()
    try:
        set_session(conn, key_info.tenant_id, key_info.user_id)
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT
                    count(*)                                              AS ai_calls,
                    coalesce(sum(cost_usd), 0)::numeric(12,4)             AS cost_usd,
                    coalesce(sum(tokens_in), 0)                           AS tokens_in,
                    coalesce(sum(tokens_out), 0)                          AS tokens_out,
                    coalesce(round(avg(latency_ms)), 0)::int              AS avg_latency_ms,
                    count(*) FILTER (WHERE error_type IS NOT NULL)        AS errors
                  FROM ai_call_log
                 WHERE tenant_id = %s::uuid
                   AND called_at > NOW() - make_interval(hours => %s)
                """,
                (key_info.tenant_id, hours),
            )
            r = cur.fetchone() or (0, 0, 0, 0, 0, 0)
            ai = {
                "calls":         int(r[0] or 0),
                "cost_usd":      float(r[1] or 0),
                "tokens_in":     int(r[2] or 0),
                "tokens_out":    int(r[3] or 0),
                "avg_latency_ms": int(r[4] or 0),
                "errors":        int(r[5] or 0),
            }
            # AI calls broken down by purpose
            cur.execute(
                """
                SELECT purpose,
                       count(*)                          AS n,
                       coalesce(sum(cost_usd), 0)::numeric(12,4) AS cost_usd
                  FROM ai_call_log
                 WHERE tenant_id = %s::uuid
                   AND called_at > NOW() - make_interval(hours => %s)
                 GROUP BY purpose
                 ORDER BY n DESC
                """,
                (key_info.tenant_id, hours),
            )
            ai_by_purpose = [
                {"purpose": p, "calls": int(n), "cost_usd": float(c)}
                for p, n, c in cur.fetchall()
            ]
            # Uploads
            cur.execute(
                """
                SELECT count(*), count(*) FILTER (WHERE extraction_status = 'completed')
                  FROM document_uploads
                 WHERE tenant_id = %s::uuid
                   AND uploaded_at > NOW() - make_interval(hours => %s)
                """,
                (key_info.tenant_id, hours),
            )
            u_total, u_ok = cur.fetchone() or (0, 0)
            # Chat requests
            cur.execute(
                """
                SELECT count(*)
                  FROM request_trace_log
                 WHERE tenant_id = %s::uuid
                   AND traced_at > NOW() - make_interval(hours => %s)
                """,
                (key_info.tenant_id, hours),
            )
            chat_n = cur.fetchone()[0] or 0
            # Posture changes
            cur.execute(
                """
                SELECT count(*)
                  FROM posture_history
                 WHERE tenant_id = %s::uuid
                   AND created_at > NOW() - make_interval(hours => %s)
                """,
                (key_info.tenant_id, hours),
            )
            posture_changes = cur.fetchone()[0] or 0
        return {
            "window_hours":   hours,
            "ai":             ai,
            "ai_by_purpose":  ai_by_purpose,
            "uploads_total":  int(u_total or 0),
            "uploads_completed": int(u_ok or 0),
            "chat_requests":  int(chat_n or 0),
            "posture_changes": int(posture_changes or 0),
        }
    finally:
        pool.putconn(conn)


@app.get("/api/v1/trace/ai-calls", tags=["trace"])
async def trace_ai_calls(
    request:  Request,
    key_info: APIKeyInfo = Depends(require_api_key),
    hours:    int          = 24,
    purpose:  Optional[str] = None,
    provider: Optional[str] = None,
    errors_only: bool       = False,
    limit:    int          = 100,
):
    """Recent AI calls, tenant-scoped. Sorted newest-first."""
    pool = request.app.state.pg_pool
    conn = pool.getconn()
    try:
        set_session(conn, key_info.tenant_id, key_info.user_id)
        where = ["tenant_id = %s::uuid",
                 "called_at > NOW() - make_interval(hours => %s)"]
        params: list = [key_info.tenant_id, hours]
        if purpose:
            where.append("purpose = %s")
            params.append(purpose)
        if provider:
            where.append("provider = %s")
            params.append(provider)
        if errors_only:
            where.append("error_type IS NOT NULL")
        with conn.cursor() as cur:
            cur.execute(
                f"""
                SELECT id, called_at, purpose, provider, model,
                       latency_ms, tokens_in, tokens_out, cost_usd::text,
                       error_type, error_detail,
                       upload_id::text, session_id, request_id,
                       prompt_preview, response_preview, metadata
                  FROM ai_call_log
                 WHERE {' AND '.join(where)}
                 ORDER BY called_at DESC
                 LIMIT %s
                """,
                params + [limit],
            )
            rows = cur.fetchall()
        return {
            "count": len(rows),
            "calls": [
                {
                    "id":             str(r[0]),
                    "called_at":      r[1].isoformat() if r[1] else None,
                    "purpose":        r[2],
                    "provider":       r[3],
                    "model":          r[4],
                    "latency_ms":     r[5],
                    "tokens_in":      r[6],
                    "tokens_out":     r[7],
                    "cost_usd":       float(r[8]) if r[8] else None,
                    "error_type":     r[9],
                    "error_detail":   r[10],
                    "upload_id":      r[11],
                    "session_id":     r[12],
                    "request_id":     r[13],
                    "prompt_preview": r[14],
                    "response_preview": r[15],
                    "metadata":       r[16],
                }
                for r in rows
            ],
        }
    finally:
        pool.putconn(conn)


@app.get("/api/v1/trace/intake", tags=["trace"])
async def trace_intake(
    request:  Request,
    key_info: APIKeyInfo = Depends(require_api_key),
    hours:    int          = 24,
    limit:    int          = 100,
):
    """Per-upload pipeline trace — one row per (upload_id, stage).
    Groups by upload_id in the client for a "one upload → its N stages"
    timeline view."""
    pool = request.app.state.pg_pool
    conn = pool.getconn()
    try:
        set_session(conn, key_info.tenant_id, key_info.user_id)
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT
                    upload_id, filename, stage, stage_status, stage_ms,
                    total_ms, token_estimate, page_count, section_count,
                    extraction_path, doc_type, standard_ids,
                    llm_calls, findings_raw, findings_kept,
                    posture_created, posture_updated, posture_skipped,
                    error_type, error_detail,
                    traced_at
                  FROM intake_trace_log
                 WHERE tenant_id = %s::uuid
                   AND traced_at > NOW() - make_interval(hours => %s)
                 ORDER BY traced_at DESC
                 LIMIT %s
                """,
                (key_info.tenant_id, hours, limit),
            )
            rows = cur.fetchall()
        return {
            "count": len(rows),
            "entries": [
                {
                    "upload_id":        r[0],
                    "filename":         r[1],
                    "stage":            r[2],
                    "stage_status":     r[3],
                    "stage_ms":         r[4],
                    "total_ms":         r[5],
                    "token_estimate":   r[6],
                    "page_count":       r[7],
                    "section_count":    r[8],
                    "extraction_path":  r[9],
                    "doc_type":         r[10],
                    "standard_ids":     r[11],
                    "llm_calls":        r[12],
                    "findings_raw":     r[13],
                    "findings_kept":    r[14],
                    "posture_created":  r[15],
                    "posture_updated":  r[16],
                    "posture_skipped":  r[17],
                    "error_type":       r[18],
                    "error_detail":     r[19],
                    "traced_at":        r[20].isoformat() if r[20] else None,
                }
                for r in rows
            ],
        }
    finally:
        pool.putconn(conn)


@app.get("/api/v1/trace/requests", tags=["trace"])
async def trace_requests(
    request:  Request,
    key_info: APIKeyInfo = Depends(require_api_key),
    hours:    int          = 24,
    limit:    int          = 100,
):
    """Chat/RAG request trace — classifier + retrieval outcomes."""
    pool = request.app.state.pg_pool
    conn = pool.getconn()
    try:
        set_session(conn, key_info.tenant_id, key_info.user_id)
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT
                    request_id, traced_at, query_text,
                    classifier_type, taxonomy_type, handler_name, strategy,
                    topic_ref, policy_short_circuit,
                    nodes_primary, nodes_secondary, vector_hits, doc_contexts
                  FROM request_trace_log
                 WHERE tenant_id = %s::uuid
                   AND traced_at > NOW() - make_interval(hours => %s)
                 ORDER BY traced_at DESC
                 LIMIT %s
                """,
                (key_info.tenant_id, hours, limit),
            )
            rows = cur.fetchall()
        return {
            "count": len(rows),
            "entries": [
                {
                    "request_id":    r[0],
                    "traced_at":     r[1].isoformat() if r[1] else None,
                    "query_text":    r[2],
                    "classifier":    r[3],
                    "taxonomy":      r[4],
                    "handler":       r[5],
                    "strategy":      r[6],
                    "topic_ref":     r[7],
                    "short_circuit": r[8],
                    "nodes_primary":   r[9],
                    "nodes_secondary": r[10],
                    "vector_hits":   r[11],
                    "doc_contexts":  r[12],
                }
                for r in rows
            ],
        }
    finally:
        pool.putconn(conn)


@app.get("/api/v1/trace/sweeps", tags=["trace"])
async def trace_sweeps(
    request:  Request,
    key_info: APIKeyInfo = Depends(require_api_key),
    hours:    int = 168,
    limit:    int = 60,
):
    """Recent scheduler sweep_log entries. Not tenant-scoped —
    the sweep runs across all tenants, but access-gated by the
    caller's API key (admin scope in production)."""
    pool = request.app.state.pg_pool
    conn = pool.getconn()
    try:
        set_session(conn, key_info.tenant_id, key_info.user_id)
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT tick_id::text, work_type, status,
                       started_at, completed_at,
                       items_scanned, items_acted_on, items_error,
                       detail, error_type, error_detail
                  FROM sweep_log
                 WHERE started_at > NOW() - make_interval(hours => %s)
                 ORDER BY started_at DESC
                 LIMIT %s
                """,
                (hours, limit),
            )
            rows = cur.fetchall()
        return {
            "count": len(rows),
            "entries": [
                {
                    "tick_id":        r[0],
                    "work_type":      r[1],
                    "status":         r[2],
                    "started_at":     r[3].isoformat() if r[3] else None,
                    "completed_at":   r[4].isoformat() if r[4] else None,
                    "items_scanned":  r[5],
                    "items_acted_on": r[6],
                    "items_error":    r[7],
                    "detail":         r[8],
                    "error_type":     r[9],
                    "error_detail":   r[10],
                }
                for r in rows
            ],
        }
    finally:
        pool.putconn(conn)


# ─────────────────────────────────────────────────────────────────────────────
# Outbound notification delivery (2026-07-13) — admin endpoints.
# Configure per-tenant channels + manually trigger a delivery pass.
# ─────────────────────────────────────────────────────────────────────────────

@app.post("/api/v1/admin/notifications/channels", tags=["admin"])
async def admin_notification_channel_upsert(
    request:  Request,
    channel_kind: str  = Form(...),
    endpoint:     str  = Form(...),
    min_severity: str  = Form("medium"),
    is_active:    bool = Form(True),
    key_info:     APIKeyInfo = Depends(require_api_key),
):
    """Create or update a delivery channel for the calling tenant.
    channel_kind: email | slack | webhook | sms
    endpoint: SMTP recipient(s) or Slack webhook URL, etc."""
    pool = request.app.state.pg_pool
    conn = pool.getconn()
    try:
        set_session(conn, key_info.tenant_id, key_info.user_id)
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO tenant_notification_channel
                     (tenant_id, channel_kind, endpoint, min_severity, is_active)
                     VALUES (%s::uuid, %s, %s, %s, %s)
                     RETURNING id
                """,
                (key_info.tenant_id, channel_kind, endpoint, min_severity, is_active),
            )
            row_id = cur.fetchone()[0]
        conn.commit()
        return {"id": str(row_id), "channel_kind": channel_kind, "endpoint": endpoint}
    finally:
        pool.putconn(conn)


@app.get("/api/v1/admin/notifications/channels", tags=["admin"])
async def admin_notification_channels_list(
    request:  Request,
    key_info: APIKeyInfo = Depends(require_api_key),
):
    """List configured channels for the calling tenant."""
    pool = request.app.state.pg_pool
    conn = pool.getconn()
    try:
        set_session(conn, key_info.tenant_id, key_info.user_id)
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT id, channel_kind, endpoint, min_severity, is_active, updated_at
                  FROM tenant_notification_channel
                 WHERE tenant_id = %s::uuid
                 ORDER BY channel_kind
                """,
                (key_info.tenant_id,),
            )
            rows = cur.fetchall()
        return {
            "count": len(rows),
            "channels": [
                {"id": str(r[0]), "channel_kind": r[1], "endpoint": r[2],
                 "min_severity": r[3], "is_active": r[4],
                 "updated_at": r[5].isoformat() if r[5] else None}
                for r in rows
            ],
        }
    finally:
        pool.putconn(conn)


@app.delete("/api/v1/admin/notifications/channels/{channel_id}", tags=["admin"])
async def admin_notification_channel_delete(
    channel_id: UploadIdParam,   # any UUID — reused UploadIdParam validator
    request:    Request,
    key_info:   APIKeyInfo = Depends(require_api_key),
):
    """Delete a delivery channel for the calling tenant. Idempotent —
    returns 200 with deleted=0 if the channel didn't exist or belongs
    to a different tenant (RLS makes the tenant-scoped check natural).

    Ship 3'.d (2026-07-17) — completes the tenant_notification_channel
    CRUD surface for the frontend UI.
    """
    pool = request.app.state.pg_pool
    conn = pool.getconn()
    try:
        set_session(conn, key_info.tenant_id, key_info.user_id)
        with conn.cursor() as cur:
            cur.execute(
                """
                DELETE FROM tenant_notification_channel
                 WHERE id        = %s::uuid
                   AND tenant_id = %s::uuid
                """,
                (channel_id, key_info.tenant_id),
            )
            deleted = cur.rowcount
        conn.commit()
        return {"deleted": deleted, "channel_id": channel_id}
    finally:
        pool.putconn(conn)


@app.post("/api/v1/admin/notifications/deliver", tags=["admin"])
async def admin_notifications_deliver_now(
    request:  Request,
    dry_run:  bool = False,
    key_info: APIKeyInfo = Depends(require_api_key),
):
    """Manually trigger the delivery worker. Same code the sweep
    scheduler calls; useful for testing after a channel config change."""
    pool = request.app.state.pg_pool
    conn = pool.getconn()
    try:
        set_session(conn, key_info.tenant_id, key_info.user_id)
        from rag.notifications.deliver import deliver_all
        return deliver_all(conn, dry_run=dry_run)
    finally:
        pool.putconn(conn)


# ─────────────────────────────────────────────────────────────────────────────
# UPDATES_FACT admin endpoints — Wave 3a (2026-07-13)
#
# Manual trigger for the fact-recompute worker. Same code path the
# future scheduler (3b) will call periodically. Two endpoints:
#   POST /api/v1/admin/facts/recompute            — all facts for tenant
#   POST /api/v1/admin/facts/recompute/{fact_key} — one fact for tenant
# Both return per-fact results (computed_value, changed, latency, error).
# ─────────────────────────────────────────────────────────────────────────────

@app.post("/api/v1/admin/facts/recompute", tags=["admin"])
async def admin_facts_recompute_all(
    request:  Request,
    key_info: APIKeyInfo = Depends(require_api_key),
):
    """Recompute every configured fact for the calling tenant.
    Returns the per-fact result set. Writes to client_facts on delta
    and to fact_recompute_log on every attempt."""
    pool = request.app.state.pg_pool
    conn = pool.getconn()
    try:
        set_session(conn, key_info.tenant_id, key_info.user_id)
        from rag.facts.recompute import recompute_all_for_tenant
        results = recompute_all_for_tenant(conn, key_info.tenant_id)
        return {
            "tenant_id": key_info.tenant_id,
            "count":     len(results),
            "results": [
                {
                    "fact_key":       r.fact_key,
                    "computed_value": r.computed_value,
                    "prior_value":    r.prior_value,
                    "changed":        r.changed,
                    "source_type":    r.source_type,
                    "latency_ms":     r.latency_ms,
                    "error_type":     r.error_type,
                    "error_detail":   r.error_detail,
                }
                for r in results
            ],
        }
    finally:
        pool.putconn(conn)


@app.post("/api/v1/admin/facts/recompute/{fact_key}", tags=["admin"])
async def admin_facts_recompute_one(
    fact_key: FactKeyParam,
    request:  Request,
    key_info: APIKeyInfo = Depends(require_api_key),
):
    """Recompute a single fact for the calling tenant."""
    pool = request.app.state.pg_pool
    conn = pool.getconn()
    try:
        set_session(conn, key_info.tenant_id, key_info.user_id)
        from rag.facts.recompute import recompute_client_fact
        r = recompute_client_fact(conn, key_info.tenant_id, fact_key)
        return {
            "tenant_id":      key_info.tenant_id,
            "fact_key":       r.fact_key,
            "computed_value": r.computed_value,
            "prior_value":    r.prior_value,
            "changed":        r.changed,
            "source_type":    r.source_type,
            "latency_ms":     r.latency_ms,
            "error_type":     r.error_type,
            "error_detail":   r.error_detail,
        }
    finally:
        pool.putconn(conn)


@app.get("/api/v1/admin/facts/recompute-log", tags=["admin"])
async def admin_facts_recompute_log(
    request:  Request,
    key_info: APIKeyInfo = Depends(require_api_key),
    hours:    int = 168,   # default 7 days
    limit:    int = 50,
    changed_only: bool = False,
):
    """Recent fact_recompute_log entries for the calling tenant.
    Feeds the trace UI. Optional changed_only filter shows only
    deltas — useful for spotting drift."""
    pool = request.app.state.pg_pool
    conn = pool.getconn()
    try:
        set_session(conn, key_info.tenant_id, key_info.user_id)
        with conn.cursor() as cur:
            cur.execute(
                f"""
                SELECT fact_key, computed_value, prior_value, changed,
                       source_type, error_type, error_detail,
                       computed_at, latency_ms
                  FROM fact_recompute_log
                 WHERE tenant_id = %s::uuid
                   AND computed_at > NOW() - make_interval(hours => %s)
                   {"AND changed = TRUE" if changed_only else ""}
                 ORDER BY computed_at DESC
                 LIMIT %s
                """,
                (key_info.tenant_id, hours, limit),
            )
            rows = cur.fetchall()
        return {
            "count": len(rows),
            "entries": [
                {
                    "fact_key":       r[0],
                    "computed_value": r[1],
                    "prior_value":    r[2],
                    "changed":        r[3],
                    "source_type":    r[4],
                    "error_type":     r[5],
                    "error_detail":   r[6],
                    "computed_at":    r[7].isoformat() if r[7] else None,
                    "latency_ms":     r[8],
                }
                for r in rows
            ],
        }
    finally:
        pool.putconn(conn)


@app.post("/api/v1/admin/uploads/{upload_id}/reextract", tags=["admin"])
async def admin_reextract_upload(
    upload_id: UploadIdParam,
    request:                Request,
    background_tasks:       BackgroundTasks,
    declared_standard_id:   Optional[str] = Form(None),
    declared_evidence_type: Optional[str] = Form(None),
    key_info:               APIKeyInfo    = Depends(require_api_key),
):
    """Re-run extraction on an existing upload without requiring re-upload
    of bytes. Use when an extractor improvement ships (filter, prompt,
    reader enhancement, per-MUST binding wiring) and you want existing
    docs to benefit.

    Behavior:
      - Looks up the upload by id (tenant-scoped via RLS)
      - Verifies the original file is still on disk at storage_path
      - Queues `_run_pipeline` on the existing file, reusing the same
        upload_id (the pipeline writes new document_findings rows;
        previously-approved findings on the same client_documents row
        stay active — tenant decides whether to reject the old ones
        via Stage-1 after seeing the new shape)
      - Returns immediately; poll /api/v1/documents/{upload_id}/status

    Limitations (deliberate, MVP):
      - Does NOT auto-supersede prior findings. Two sets coexist until
        tenant triages. Add a `supersede=true` flag here if/when
        operationally needed.
      - Does NOT re-run on duplicate-status uploads (those have no
        independent storage; re-extract their canonical instead).
    """
    pool = request.app.state.pg_pool
    conn = pool.getconn()
    try:
        set_session(conn, key_info.tenant_id, key_info.user_id)
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT id, filename, storage_path, extraction_status,
                       doc_type, standard_ids
                  FROM document_uploads
                 WHERE id        = %s::uuid
                   AND tenant_id = %s::uuid
                """,
                (upload_id, key_info.tenant_id),
            )
            row = cur.fetchone()
    finally:
        pool.putconn(conn)

    if not row:
        raise HTTPException(404, "We couldn't find that upload for your tenant.")
    existing_id, filename, storage_path, status, stored_type, stored_stds = row
    if status == "duplicate":
        raise HTTPException(
            400,
            "This entry is a duplicate copy — please re-run extraction on "
            "the original upload it points to.",
        )
    if not storage_path or not Path(storage_path).exists():
        raise HTTPException(
            404,
            "The original file for this upload is no longer on disk, so we "
            "can't re-run extraction. Please upload the file again.",
        )

    # Resolve declared hints for the re-run:
    #   1. Form-field values from the current click (tenant just picked
    #      the framework/type in the dropdowns and re-clicked)
    #   2. Fall back to whatever was stored on the original upload row
    #   3. If neither, pipeline reverts to keyword detection
    # "multi" resolves against the current tenant scope at request time.
    _hint_stds: Optional[list[str]] = None
    if declared_standard_id and declared_standard_id not in ("", "auto"):
        if declared_standard_id == "multi":
            from rag.scope_loader import load_tenant_scope
            _c = pool.getconn()
            try:
                set_session(_c, key_info.tenant_id, key_info.user_id)
                _scope = load_tenant_scope(_c, key_info.tenant_id)
                seen = set()
                _hint_stds = []
                for sid in _scope.queryable_standards:
                    if sid not in seen:
                        seen.add(sid)
                        _hint_stds.append(sid)
                if not _hint_stds:
                    _hint_stds = None
            finally:
                pool.putconn(_c)
        else:
            _hint_stds = [declared_standard_id]
    elif stored_stds:
        _hint_stds = list(stored_stds)

    _hint_evtype = declared_evidence_type if (declared_evidence_type and declared_evidence_type not in ("", "auto")) else (stored_type or None)

    # If tenant just supplied new hints, persist so a future re-run inherits.
    if (declared_standard_id and declared_standard_id not in ("", "auto")) or (declared_evidence_type and declared_evidence_type not in ("", "auto")):
        _c = pool.getconn()
        try:
            set_session(_c, key_info.tenant_id, key_info.user_id)
            with _c.cursor() as _cur:
                _cur.execute(
                    """UPDATE document_uploads
                          SET doc_type     = COALESCE(%s, doc_type),
                              standard_ids = COALESCE(%s, standard_ids)
                        WHERE id = %s::uuid""",
                    (_hint_evtype, _hint_stds, upload_id),
                )
                _c.commit()
        except Exception as e:
            _c.rollback()
            logger.warning(f"document_uploads reextract-hint update failed: {e}")
        finally:
            pool.putconn(_c)

    api_key = os.getenv("ANTHROPIC_API_KEY", "")
    background_tasks.add_task(
        _run_pipeline,
        file_path              = storage_path,
        tenant_id              = key_info.tenant_id,
        upload_id              = upload_id,
        db_url                 = DATABASE_URL,
        api_key                = api_key,
        original_filename      = filename,
        user_id                = key_info.user_id,
        declared_standard_ids  = _hint_stds,
        declared_evidence_type = _hint_evtype,
    )

    logger.info(
        f"Re-extract queued: {filename} upload_id={upload_id[:8]} "
        f"tenant={key_info.tenant_id[:8]}"
    )
    return {
        "ok":         True,
        "upload_id":  upload_id,
        "filename":   filename,
        "message":    "Re-extraction queued — poll /api/v1/documents/{upload_id}/status",
    }


@app.get("/api/v1/stage1/auto-approved", tags=["hitl"])
async def stage1_auto_approved(
    request:  Request,
    key_info: APIKeyInfo = Depends(require_api_key),
    days:     int = 30,
    limit:    int = 200,
):
    """List recently auto-approved findings.

    Three intake lanes write auto-approved rows because the content
    has no inference uncertainty:

      - `templated` — markdown upload through the marker-bearing
        template (tenant authored under explicit <<MUST X>> markers)
      - `form` — retired 2026-07-04; legacy rows retagged to 'templated'
      - `fingerprint_match` — deterministic MUST-keyword match
        (2026-07-06 LLM-free stage 4-5). Each row carries the winning
        keyword set + char-position + verbatim sentence — reproducible
        without an LLM opinion.

    This endpoint exposes all auto-approved rows for tenant review:
    revert any row that was unintentional. Filters:
      - inference_source ∈ ('templated', 'fingerprint_match')
      - review_status    = 'approved'
      - confirmed_at     within last `days` days (default 30)

    Returns up to `limit` rows (default 200), newest first.
    """
    pool = request.app.state.pg_pool
    conn = pool.getconn()
    try:
        set_session(conn, key_info.tenant_id)
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT df.id::text, df.checklist_item_id, df.control_ref,
                       df.standard_id, df.status, df.confidence,
                       LEFT(df.excerpt, 200) AS excerpt_preview,
                       df.confirmed_by::text, df.confirmed_at,
                       cd.filename, df.inference_source
                  FROM document_findings df
                  JOIN client_documents cd ON cd.id = df.document_id
                 WHERE df.tenant_id        = %s::uuid
                   AND df.is_active        = TRUE
                   AND df.inference_source IN ('templated', 'fingerprint_match')
                   AND df.review_status    = 'approved'
                   AND df.confirmed_at     > now() - (%s * interval '1 day')
                 ORDER BY df.confirmed_at DESC
                 LIMIT %s
                """,
                (key_info.tenant_id, days, limit),
            )
            rows = cur.fetchall()
    finally:
        pool.putconn(conn)

    return {
        "tenant_id": key_info.tenant_id,
        "days":      days,
        "count":     len(rows),
        "findings": [
            {
                "id":              r[0],
                "checklist_item_id": r[1],
                "control_ref":     r[2],
                "standard_id":     r[3],
                "status":          r[4],
                "confidence":      r[5],
                "excerpt_preview": r[6],
                "authored_by":     r[7],
                "confirmed_at":    r[8].isoformat() if r[8] else None,
                "source_filename": r[9],
            }
            for r in rows
        ],
    }


@app.get("/api/v1/journey/state", tags=["journey"])
async def get_journey_state(
    request:  Request,
    key_info: APIKeyInfo = Depends(require_api_key),
):
    """Return the tenant's onboarding journey state.

    Reads-only computation across:
      - templates (the catalogue + version)
      - document_findings (MUSTs satisfied)
      - tenant_must_overrides (N/A MUSTs)
      - client_facts (profile completeness)
      - Neo4j (leaves + MUST item ids per leaf)

    The phase determination:
      profile     — ClientFacts not yet completed
      foundation  — 1+ of the 20 anchor templates incomplete
      operational — all anchors complete; non-anchor templates remain
      annual      — all templates complete; freshness-driven reviews

    `next_actions` is a top-5 recommendation queue for the current
    phase. Each row points at template_url + download_url so the
    client can route the tenant to fill them.
    """
    pool = request.app.state.pg_pool
    conn = pool.getconn()
    try:
        set_session(conn, key_info.tenant_id)
        from rag.posture_loader import _build_engine_neo4j_driver
        neo4j_driver = _build_engine_neo4j_driver()
        from rag.journey.state import compute_journey_state
        try:
            state = compute_journey_state(conn, neo4j_driver, key_info.tenant_id)
        finally:
            if neo4j_driver is not None:
                neo4j_driver.close()
    finally:
        pool.putconn(conn)

    from dataclasses import asdict
    return asdict(state)


@app.get("/api/v1/journey/next", tags=["journey"])
async def get_journey_next(
    request:  Request,
    key_info: APIKeyInfo = Depends(require_api_key),
):
    """Return only the single top recommended next action.

    Convenience endpoint for clients that just need "what should I
    do next?" without the full state payload. Same data source as
    /journey/state — pulls the first row of next_actions and the
    phase context. Returns 200 with empty `recommendation` when
    nothing remains (annual phase with no freshness work).
    """
    pool = request.app.state.pg_pool
    conn = pool.getconn()
    try:
        set_session(conn, key_info.tenant_id)
        from rag.posture_loader import _build_engine_neo4j_driver
        neo4j_driver = _build_engine_neo4j_driver()
        from rag.journey.state import compute_journey_state
        try:
            state = compute_journey_state(conn, neo4j_driver, key_info.tenant_id)
        finally:
            if neo4j_driver is not None:
                neo4j_driver.close()
    finally:
        pool.putconn(conn)

    from dataclasses import asdict
    top = state.next_actions[0] if state.next_actions else None
    return {
        "phase":           state.phase,
        "phase_name":      state.phase_name,
        "phase_message":   state.phase_message,
        "posture_pct":     state.posture_pct,
        "recommendation":  asdict(top) if top else None,
    }


def _template_download_filename(leaf_id: str, ext: str = "md") -> str:
    """req:A.5.15:access_control_policy → A_5_15_access_control_policy.md

    Strip the leading 'req:' prefix and convert remaining colons/dots
    to underscores for filesystem safety. The `ext` argument selects
    the file extension (md / xlsx / future docx).
    """
    base = leaf_id[4:] if leaf_id.startswith("req:") else leaf_id
    safe = base.replace(":", "_").replace(".", "_")
    return f"{safe}.{ext}"


@app.get("/api/v1/templates/{leaf_id}/download", tags=["templates"])
async def download_template(
    leaf_id: LeafIdParam,
    request:  Request,
    key_info: APIKeyInfo = Depends(require_api_key),
    empty:    bool = False,
    format:   Optional[str] = "md",
):
    """Download the rendered template as a file attachment.

    Format options (?format=...):
      - md (default): markdown. Same render pipeline as GET
        /api/v1/templates/{leaf_id}; tenant identity placeholders
        substituted, N/A MUSTs stripped, prior evidence prefilled
        (?empty=true to opt out).
      - xlsx: Excel workbook. Only valid for TABULAR templates
        (those with a TABLE-COLUMNS metadata block — A.5.9 Asset
        Inventory, 10.1 Improvement Action Register, etc.).
        Workbook has Register / Guidance / hidden _arion_meta
        sheets. Returns 400 for non-tabular leaves.

    Filename convention: `{control_ref}_{slug}.{ext}` (colons/dots →
    underscores). e.g. req:A.5.9:asset_inventory → A_5_9_asset_inventory.xlsx

    See [[templates-v2-anchors-complete-2026-06-25]] for the tabular
    templates list and the rationale for native-format downloads.
    """
    fmt = (format or "md").lower()
    if fmt not in ("md", "xlsx", "docx"):
        raise HTTPException(status_code=400, detail=f"Unsupported format: {fmt}")

    pool = request.app.state.pg_pool
    conn = pool.getconn()
    try:
        set_session(conn, key_info.tenant_id)
        from rag.templates.renderer import render_template
        rendered = render_template(
            conn, key_info.tenant_id, leaf_id,
            include_header = True,
            prefill        = not empty,
        )
        if rendered is None:
            raise HTTPException(
                status_code=404,
                detail=f"No template stored for leaf_id={leaf_id!r}.",
            )

        if fmt == "xlsx":
            # Look up the raw on-disk template body for TABLE-COLUMNS extraction.
            # The rendered body_md has had its frontmatter / H1 stripped when
            # include_header=True, but TABLE-COLUMNS markers survive that.
            from rag.templates.xlsx_renderer import render_template_xlsx
            xlsx_bytes = render_template_xlsx(
                pg_conn       = conn,
                tenant_id     = key_info.tenant_id,
                leaf_id       = leaf_id,
                template_body = rendered.body_md,
            )
            if xlsx_bytes is None:
                raise HTTPException(
                    status_code=400,
                    detail=(
                        f"leaf_id={leaf_id!r} is not a tabular template "
                        "(no TABLE-COLUMNS metadata). Use format=md instead."
                    ),
                )
            from fastapi.responses import Response
            return Response(
                content    = xlsx_bytes,
                media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                headers    = {
                    "Content-Disposition":
                        f'attachment; filename="{_template_download_filename(leaf_id, ext="xlsx")}"',
                    "X-Template-Version": str(rendered.template_version),
                    "X-Template-Format":  "xlsx",
                },
            )

        if fmt == "docx":
            # Narrative templates only. Tabular templates have TABLE-COLUMNS
            # metadata; .docx isn't the right format for those — surface a
            # 400 so the tenant gets pointed at .xlsx instead.
            if "TABLE-COLUMNS" in rendered.body_md:
                raise HTTPException(
                    status_code=400,
                    detail=(
                        f"leaf_id={leaf_id!r} is a tabular template; "
                        ".docx is for narrative leaves. Use format=xlsx instead."
                    ),
                )
            from rag.templates.docx_renderer import render_template_docx
            docx_bytes = render_template_docx(
                pg_conn       = conn,
                tenant_id     = key_info.tenant_id,
                leaf_id       = leaf_id,
                template_body = rendered.body_md,
            )
            from fastapi.responses import Response
            return Response(
                content    = docx_bytes,
                media_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                headers    = {
                    "Content-Disposition":
                        f'attachment; filename="{_template_download_filename(leaf_id, ext="docx")}"',
                    "X-Template-Version": str(rendered.template_version),
                    "X-Template-Format":  "docx",
                },
            )
    finally:
        pool.putconn(conn)

    from fastapi.responses import Response
    return Response(
        content    = rendered.body_md,
        media_type = "text/markdown; charset=utf-8",
        headers    = {
            "Content-Disposition":
                f'attachment; filename="{_template_download_filename(leaf_id)}"',
            "X-Template-Version":     str(rendered.template_version),
            "X-Musts-Rendered":       str(rendered.must_rendered),
            "X-Musts-Dropped":        str(rendered.must_dropped),
            "X-Musts-Prefilled":      str(rendered.musts_prefilled),
        },
    )


# ── Tenant profile key catalog ───────────────────────────────────────────────
# Each entry: (key, group, label, description). Drives both the GET
# response and the admin UI form. To add a new placeholder, add a row
# here + (optionally) reference it from one of the templates in
# db/templates/*.md. Renderer accepts any key; this catalog just gives
# the UI human-grade copy for the known set.

_TENANT_PROFILE_KEYS: list[dict] = [
    # People
    {"key": "ceo_name",            "group": "People",
     "label": "CEO name",
     "description": "Chief Executive Officer who signs off on top-level policies."},
    {"key": "ciso_name",           "group": "People",
     "label": "CISO name",
     "description": "Chief Information Security Officer leading security operations."},
    {"key": "dpo_name",            "group": "People",
     "label": "DPO name",
     "description": "Data Protection Officer (or equivalent privacy lead)."},
    {"key": "isms_manager_name",   "group": "People",
     "label": "ISMS Manager",
     "description": "Day-to-day ISMS operator (per Clause 5.3a)."},
    {"key": "isms_owner_name",     "group": "People",
     "label": "ISMS Owner",
     "description": "Top-management accountable owner of the ISMS (often CEO)."},
    {"key": "hr_partner_name",     "group": "People",
     "label": "HR partner",
     "description": "HR contact for personnel-security workflows (A.6 controls)."},
    {"key": "awareness_lead_name", "group": "People",
     "label": "Awareness programme lead",
     "description": "Lead for A.6.3 information-security awareness + training."},

    # Org metadata
    {"key": "registered_address",  "group": "Organisation",
     "label": "Registered office address",
     "description": "Legal registered address — appears in policy headers + privacy notices."},
    {"key": "company_number",      "group": "Organisation",
     "label": "Company number",
     "description": "Registered company / business number (e.g. UK Companies House)."},
    {"key": "tenant_domain",       "group": "Organisation",
     "label": "Primary domain",
     "description": "Public domain used in policy email addresses (dpo@…, ciso@…)."},

    # Business context
    {"key": "product_or_service",  "group": "Business",
     "label": "Primary product / service",
     "description": "Short description used in scope-statements and customer-facing docs."},

    # Dates
    {"key": "approval_date",       "group": "Dates",
     "label": "Default approval date",
     "description": "Default 'approved on' date for newly-rendered policies (override per doc)."},
    {"key": "next_review_date",    "group": "Dates",
     "label": "Default next review date",
     "description": "Default 'next planned review' — typically approval_date + 365d."},
]
_TENANT_PROFILE_KEY_SET = {entry["key"] for entry in _TENANT_PROFILE_KEYS}


def _count_template_references_per_key() -> dict[str, int]:
    """Scan the templates table once per request and count how many
    distinct templates reference each profile_key (via its
    <<UPPER_SNAKE>> placeholder).

    Surfaces the leverage of each profile field: "Used in 7 templates"
    shows the tenant why filling once propagates everywhere. Cheap
    enough (~645 templates × short regex scan) that we don't bother
    caching for now.
    """
    pool = app.state.pg_pool
    conn = pool.getconn()
    try:
        with conn.cursor() as cur:
            # Templates table is global (not tenant-scoped), no RLS dance needed.
            cur.execute("SELECT leaf_id, body_md FROM templates")
            rows = cur.fetchall()
    finally:
        pool.putconn(conn)
    counts: dict[str, int] = {entry["key"]: 0 for entry in _TENANT_PROFILE_KEYS}
    for leaf_id, body in rows:
        if not body:
            continue
        # Find all <<UPPER_SNAKE>> placeholders in this template
        seen_in_this_template: set[str] = set()
        for m in _re.finditer(r"<<([A-Z][A-Z0-9_]*)>>", body):
            seen_in_this_template.add(m.group(1).lower())
        # Increment per known key seen at least once in this template
        for key in seen_in_this_template & _TENANT_PROFILE_KEY_SET:
            counts[key] = counts.get(key, 0) + 1
    return counts


@app.get("/api/v1/tenant/scope", tags=["tenant"])
async def tenant_scope(
    request:  Request,
    key_info: APIKeyInfo = Depends(require_api_key),
):
    """Return the tenant's enrolled standards that are loaded in the graph
    (i.e. queryable + citable). Used by the intake UI to populate the
    declared-framework dropdown so the tenant can override the
    enricher's keyword detection with explicit intent.

    Returns:
      {
        "queryable_standards": ["ISO27001:2022", "ISO27701:2019", "GDPR:2016/679"],
        "direct_standards":    ["ISO27001:2022", "ISO27701:2019"],
        # ↑ what the tenant is directly enrolled in (before graph gate);
        #   included so the UI can show "you subscribe but it isn't
        #   curated yet" states.
      }

    Note: this is a compact projection of scope_loader.load_tenant_scope's
    output — the same data the RAG uses for query routing.
    """
    # Use scope_loader for consistency with the RAG's query routing.
    # This includes inferred standards (e.g. GDPR reachable via 27701's
    # Annex D mapping even when the tenant isn't directly enrolled in
    # GDPR as a primary framework).
    from rag.scope_loader import load_tenant_scope
    pool = request.app.state.pg_pool
    conn = pool.getconn()
    try:
        set_session(conn, key_info.tenant_id)
        scope = load_tenant_scope(conn, key_info.tenant_id)
    finally:
        pool.putconn(conn)

    # Dedupe queryable while preserving order — scope_loader can list a
    # standard more than once when multiple relationship types point at
    # it (satisfies + maps_to + implements).
    seen = set()
    queryable = []
    for sid in scope.queryable_standards:
        if sid not in seen:
            seen.add(sid)
            queryable.append(sid)

    return {
        "queryable_standards": queryable,
        "direct_standards":    [s.id for s in scope.direct_standards],
    }


@app.get("/api/v1/tenant/profile", tags=["templates"])
async def get_tenant_profile(
    request:  Request,
    key_info: APIKeyInfo = Depends(require_api_key),
):
    """Return the tenant's profile key/value pairs used for template
    placeholder substitution (CEO_NAME, DPO_NAME, REGISTERED_ADDRESS,
    APPROVAL_DATE, etc. — see schema_v49 + rag/templates/renderer.py).

    Returns the FULL set of known placeholder keys with human-grade
    label + description + per-key template reference count, so the
    admin UI can render a complete form without merging metadata
    client-side. Keys with no stored value return as empty strings.
    Unknown placeholders in the body stay as `<<NAME>>` literals when
    no profile value exists.

    See [[template-tenant-profile-2026-06-26]] for the key set rationale.
    """
    pool = request.app.state.pg_pool
    conn = pool.getconn()
    try:
        set_session(conn, key_info.tenant_id)
        with conn.cursor() as cur:
            cur.execute(
                "SELECT profile_key, profile_value, updated_at "
                "  FROM tenant_profile WHERE tenant_id = %s::uuid",
                (key_info.tenant_id,),
            )
            stored = {r[0]: {"value": r[1], "updated_at": r[2].isoformat() if r[2] else None}
                      for r in cur.fetchall()}
    finally:
        pool.putconn(conn)

    refs = _count_template_references_per_key()

    # Compose response: known keys (with metadata) followed by extras
    out_rows: list[dict] = []
    for entry in _TENANT_PROFILE_KEYS:
        k = entry["key"]
        out_rows.append({
            "key":         k,
            "value":       stored.get(k, {}).get("value", ""),
            "updated_at":  stored.get(k, {}).get("updated_at"),
            "known":       True,
            "group":       entry["group"],
            "label":       entry["label"],
            "description": entry["description"],
            "reference_count": refs.get(k, 0),
        })
    for k in sorted(stored.keys()):
        if k in _TENANT_PROFILE_KEY_SET:
            continue
        out_rows.append({
            "key":         k,
            "value":       stored[k]["value"],
            "updated_at":  stored[k]["updated_at"],
            "known":       False,
            "group":       "Other",
            "label":       k.replace("_", " ").title(),
            "description": "Custom placeholder (no catalog metadata).",
            "reference_count": 0,
        })
    return {
        "tenant_id": key_info.tenant_id,
        "profile":   out_rows,
    }


@app.put("/api/v1/tenant/profile", tags=["templates"])
async def put_tenant_profile(
    request:  Request,
    payload:  dict,
    key_info: APIKeyInfo = Depends(require_scope("posture")),
):
    """Upsert tenant profile key/value pairs.

    Body shape:
      {
        "profile": [
          {"key": "ceo_name",       "value": "Jane Doe"},
          {"key": "dpo_name",       "value": "Bob Smith"},
          {"key": "approval_date",  "value": "2026-01-15"},
          ...
        ]
      }

    Empty `value` (after strip) deletes the row. Unknown keys are
    permitted — the renderer substitutes any key it finds.

    Tenant-scoped via RLS; caller's user uuid is recorded on the row.
    """
    items = (payload or {}).get("profile", []) or []
    pool = request.app.state.pg_pool
    conn = pool.getconn()
    n_upsert = n_delete = 0
    try:
        set_session(conn, key_info.tenant_id)
        with conn.cursor() as cur:
            for item in items:
                key   = (item.get("key") or "").strip().lower()
                value = (item.get("value") or "").strip()
                if not key:
                    continue
                # Defensive: only allow keys matching the schema's regex
                if not _re.match(r"^[a-z][a-z0-9_]*$", key):
                    continue
                if not value:
                    cur.execute(
                        "DELETE FROM tenant_profile "
                        " WHERE tenant_id = %s::uuid AND profile_key = %s",
                        (key_info.tenant_id, key),
                    )
                    n_delete += 1
                else:
                    cur.execute(
                        """
                        INSERT INTO tenant_profile
                            (tenant_id, profile_key, profile_value, updated_by)
                        VALUES (%s::uuid, %s, %s, %s::uuid)
                        ON CONFLICT (tenant_id, profile_key) DO UPDATE SET
                            profile_value = EXCLUDED.profile_value,
                            updated_at    = now(),
                            updated_by    = EXCLUDED.updated_by
                        """,
                        (key_info.tenant_id, key, value, key_info.user_id),
                    )
                    n_upsert += 1
        conn.commit()
    finally:
        pool.putconn(conn)
    return {"upserted": n_upsert, "deleted": n_delete}


# =============================================================================
# Cite mode — external evidence (schema_v50)
# =============================================================================
# Per [[product-principle-evidence-stored-vs-cited]]: tenants whose evidence
# lives in source systems (Odoo HR / Okta / ServiceNow / OneTrust) cite the
# source rather than upload duplicate data. ArionComply tracks WHERE the
# evidence lives + freshness + verification gates.
#
# Three table groups:
#   1. tenant_external_system   — system registry (one per (tenant, system))
#   2. external_evidence_source  — per-MUST cite rows (one per (tenant, must, system))
#   3. external_evidence_verification_log — append-only verification history
#
# Engine treats fresh cites as evidence-present (see
# rag/posture/leaf_evaluators._fetch_recognised_cites).


# ══════════════════════════════════════════════════════════════════════
# Ship 14'.c — Risk Register internal endpoints
# ══════════════════════════════════════════════════════════════════════

@app.get("/api/v1/tenant/risks", tags=["risks"])
async def list_tenant_risks(
    request:  Request,
    key_info: APIKeyInfo = Depends(require_api_key),
    limit:    int = 100,
    offset:   int = 0,
    status:   Optional[list[str]] = FastAPIQuery(None),
):
    """List the tenant's active risks — flat, paginated.

    Ship 14'.c — first internal API surface for the risks table
    (schema_v2 + schema_v87). Reuses `rag.risk.queries.fetch_risks`
    so the shape stays identical to the external `/api/external/v1/risks`
    endpoint.

    Query params:
      - `limit` (default 100, max 500) + `offset` for pagination
      - `status` (repeatable) — filter by treatment_status. Empty = all.

    Framework role model discipline: each returned risk carries a
    `linked_controls` array where every ref is expanded with role +
    subject + display name. Program / extension / obligation refs
    render as first-class citizens; no primary/xfw split.
    """
    if limit < 1 or limit > 500:
        raise HTTPException(status_code=400, detail="limit must be 1-500")
    if offset < 0:
        raise HTTPException(status_code=400, detail="offset must be >= 0")

    from rag.risk.queries import fetch_risks
    pool = request.app.state.pg_pool
    conn = pool.getconn()
    try:
        set_session(conn, key_info.tenant_id)
        rows, total = fetch_risks(conn, limit=limit, offset=offset, status=status)
    finally:
        pool.putconn(conn)

    return {
        "tenant_id": str(key_info.tenant_id),
        "risks":     [r.model_dump() for r in rows],
        "total_before_pagination": total,
        "limit":     limit,
        "offset":    offset,
    }


@app.get("/api/v1/tenant/risks/summary", tags=["risks"])
async def tenant_risks_summary(
    request:  Request,
    key_info: APIKeyInfo = Depends(require_api_key),
):
    """Dashboard-friendly risk summary for the current tenant.

    Ship 14'.c — feeds the Ship 14'.d dashboard tiles + heatmap.

    Response shape matches `rag.risk.queries.RiskSummary` —
    total / open / overdue / above_threshold / unassigned counts +
    per-option + per-status breakdowns + 5x5 heatmap + top-5 rows.
    Heatmap keys are JSON-safe `L{n}_I{n}` (likelihood x impact).
    """
    from rag.risk.queries import fetch_risk_summary
    pool = request.app.state.pg_pool
    conn = pool.getconn()
    try:
        set_session(conn, key_info.tenant_id)
        summary = fetch_risk_summary(conn)
    finally:
        pool.putconn(conn)

    body = summary.model_dump()
    body["tenant_id"] = str(key_info.tenant_id)
    return body


@app.get("/api/v1/tenant/risks/template", tags=["risks"])
async def download_risk_register_template(
    request:  Request,
    key_info: APIKeyInfo = Depends(require_api_key),
):
    """Download the canonical risk-register xlsx template.

    Ship 14'.b built the static asset at
    `db/templates/risk_register_canonical.xlsx` with 4 sheets:
    Risk Register + Risk Treatment Plan + Guidance + hidden
    _arion_meta (auto_approve marker for the workbook importer).

    Ship 14'.c wires this endpoint to serve it. Any tenant with
    a valid API key can pull the template — it's static content,
    not tenant-specific.
    """
    from pathlib import Path
    template_path = Path("/data/arioncomply/db/templates/risk_register_canonical.xlsx")
    if not template_path.exists():
        raise HTTPException(
            status_code = 500,
            detail = "Canonical risk-register template not found on disk. "
                     "Run scripts/build_risk_register_template.py to rebuild.",
        )
    from fastapi.responses import Response
    return Response(
        content     = template_path.read_bytes(),
        media_type  = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers     = {
            "Content-Disposition": 'attachment; filename="risk_register_canonical.xlsx"',
        },
    )


@app.get("/api/v1/tenant/risks/{risk_id}", tags=["risks"])
async def get_tenant_risk_detail(
    risk_id:  RiskIdParam,
    request:  Request,
    key_info: APIKeyInfo = Depends(require_api_key),
):
    """Drill-in view of a single risk by UUID.

    Ship 14'.c — feeds the Ship 14'.d dashboard drill-in.

    Returns the full RiskDetail shape (all treatment-plan fields
    including the 5 columns added by schema_v87 —
    treatment_rationale / resources_required /
    performance_indicators / constraints / reporting_cadence).

    404 if the risk doesn't exist OR is scoped out by RLS
    (never leak cross-tenant existence).
    """
    from rag.risk.queries import fetch_risk_detail
    pool = request.app.state.pg_pool
    conn = pool.getconn()
    try:
        set_session(conn, key_info.tenant_id)
        detail = fetch_risk_detail(conn, str(risk_id))
    finally:
        pool.putconn(conn)

    if detail is None:
        raise HTTPException(status_code=404, detail=f"Risk not found: {risk_id}")
    return detail.model_dump()


# ══════════════════════════════════════════════════════════════════════
# Ship 15'.a — Risk register write endpoints
#
# Internal-only for now. External writes (partner SIEMs pushing risks)
# would need a new `external:risks:write` scope + external endpoint;
# deferred until a real partner asks. Internal admin/tenant flow uses
# POST / PATCH / DELETE.
# ══════════════════════════════════════════════════════════════════════

@app.post("/api/v1/tenant/risks", tags=["risks"], status_code=201)
async def create_tenant_risk(
    payload:  dict,
    request:  Request,
    key_info: APIKeyInfo = Depends(require_api_key),
):
    """Create a new risk row.

    Ship 15'.a — internal write surface for the risk register.

    Request body: RiskCreate shape. `external_ref` is required
    (tenant-authored id like `R-042`, unique per tenant); every
    other field optional.

    On success (201): returns the created RiskDetail.
    On duplicate external_ref: 409 with structured error.

    Fires `risk_added` notification (severity `low`) via
    `emit_risk_added()` after commit — silent-fail; the API
    response is not affected if the notification insert errors.
    """
    from rag.risk.queries import (
        RiskCreate, create_risk, fetch_risk_detail,
        DuplicateRiskError,
    )
    from rag.risk.notify import emit_risk_added

    try:
        body = RiskCreate(**payload)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid payload: {e}")

    pool = request.app.state.pg_pool
    conn = pool.getconn()
    try:
        set_session(conn, key_info.tenant_id)
        try:
            risk_id, ext_ref = create_risk(conn, str(key_info.tenant_id), body)
            conn.commit()
        except DuplicateRiskError:
            conn.rollback()
            raise HTTPException(
                status_code=409,
                detail=f"A risk with external_ref={body.external_ref!r} "
                       f"already exists for this tenant.",
            )
        except HTTPException:
            raise
        except Exception as e:
            conn.rollback()
            raise HTTPException(status_code=400, detail=f"Insert failed: {e}")

        # Fire write-path notification. Silent-fail — the API
        # response commits to the DB insert regardless.
        try:
            emit_risk_added(conn, str(key_info.tenant_id), ext_ref, body.threat)
            conn.commit()
        except Exception:
            try: conn.rollback()
            except Exception: pass

        # Fetch the freshly-created row for the response body.
        detail = fetch_risk_detail(conn, risk_id)
    finally:
        pool.putconn(conn)

    if detail is None:
        raise HTTPException(status_code=500,
                            detail="Post-insert read failed unexpectedly.")
    return detail.model_dump()


@app.patch("/api/v1/tenant/risks/{risk_id}", tags=["risks"])
async def patch_tenant_risk(
    risk_id:  RiskIdParam,
    payload:  dict,
    request:  Request,
    key_info: APIKeyInfo = Depends(require_api_key),
):
    """Partial update on a risk row.

    Ship 15'.a — accepts RiskPatch shape (every field optional).
    Only sets columns the caller explicitly names; unset fields
    keep their current DB values. `external_ref` is immutable
    and rejected if included.

    Returns the updated RiskDetail. 404 if the risk doesn't
    exist or is scoped out by RLS (never leak cross-tenant
    existence).
    """
    from rag.risk.queries import RiskPatch, update_risk, fetch_risk_detail

    if "external_ref" in payload:
        raise HTTPException(
            status_code=400,
            detail="external_ref is immutable; cannot be changed via PATCH.",
        )
    try:
        body = RiskPatch(**payload)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid payload: {e}")

    pool = request.app.state.pg_pool
    conn = pool.getconn()
    try:
        set_session(conn, key_info.tenant_id)
        try:
            updated_id = update_risk(conn, str(key_info.tenant_id),
                                     str(risk_id), body)
            if updated_id is None:
                raise HTTPException(status_code=404,
                                    detail=f"Risk not found: {risk_id}")
            conn.commit()
        except HTTPException:
            raise
        except Exception as e:
            conn.rollback()
            raise HTTPException(status_code=400, detail=f"Update failed: {e}")
        detail = fetch_risk_detail(conn, str(risk_id))
    finally:
        pool.putconn(conn)
    if detail is None:
        raise HTTPException(status_code=404, detail=f"Risk not found: {risk_id}")
    return detail.model_dump()


@app.delete("/api/v1/tenant/risks/{risk_id}", tags=["risks"], status_code=204)
async def delete_tenant_risk(
    risk_id:  RiskIdParam,
    request:  Request,
    key_info: APIKeyInfo = Depends(require_api_key),
    reason:   Optional[str] = None,
):
    """Soft-delete a risk row (sets `is_active = FALSE`).

    Ship 15'.a — the RLS `tenant_isolation` policy filters
    inactive rows, so subsequent GETs return 404. Row is preserved
    for auditor provenance + can be restored by flipping
    `is_active` back to TRUE (superuser only; no restore endpoint).

    `?reason=...` optional but strongly recommended — persisted
    in `deletion_reason` for the audit trail.

    204 on delete. 404 if the risk doesn't exist.
    """
    from rag.risk.queries import soft_delete_risk
    pool = request.app.state.pg_pool
    conn = pool.getconn()
    try:
        set_session(conn, key_info.tenant_id)
        try:
            deleted = soft_delete_risk(conn, str(key_info.tenant_id),
                                        str(risk_id), reason)
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise HTTPException(status_code=400, detail=f"Delete failed: {e}")
    finally:
        pool.putconn(conn)
    if not deleted:
        raise HTTPException(status_code=404, detail=f"Risk not found: {risk_id}")
    return


@app.get("/api/v1/tenant/external-systems", tags=["templates"])
async def list_external_systems(
    request:  Request,
    key_info: APIKeyInfo = Depends(require_api_key),
):
    """List the tenant's registered external evidence systems.

    Each row: which system, where to look, who owns it, default cadence,
    and which evidence_types it offers for as a cite source.
    """
    pool = request.app.state.pg_pool
    conn = pool.getconn()
    try:
        set_session(conn, key_info.tenant_id)
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT id::text, system_name, system_url,
                       owner_user_id::text, default_cadence_days,
                       covers_evidence_types, created_at, updated_at
                  FROM tenant_external_system
                 WHERE tenant_id = %s::uuid AND is_active = TRUE
                 ORDER BY system_name
                """,
                (key_info.tenant_id,),
            )
            rows = cur.fetchall()
    finally:
        pool.putconn(conn)
    return {
        "tenant_id": key_info.tenant_id,
        "systems": [
            {
                "id":                    r[0],
                "system_name":           r[1],
                "system_url":            r[2] or "",
                "owner_user_id":         r[3],
                "default_cadence_days":  r[4],
                "covers_evidence_types": r[5] or [],
                "created_at":            r[6].isoformat() if r[6] else None,
                "updated_at":            r[7].isoformat() if r[7] else None,
            }
            for r in rows
        ],
    }


@app.put("/api/v1/tenant/external-systems", tags=["templates"])
async def upsert_external_system(
    request:  Request,
    payload:  dict,
    key_info: APIKeyInfo = Depends(require_scope("posture")),
):
    """Create or update an external system entry.

    Body:
      {
        "id":                    null | "<uuid>",   // null = create new
        "system_name":           "Odoo HR",
        "system_url":            "https://odoo.arion.com/hr",
        "owner_user_id":         "<uuid>" | null,
        "default_cadence_days":  365,
        "covers_evidence_types": ["register", "record"]
      }

    Returns the saved row (with `id` populated on create).
    """
    name    = (payload.get("system_name") or "").strip()
    url     = (payload.get("system_url") or "").strip() or None
    owner   = payload.get("owner_user_id") or None
    cadence = int(payload.get("default_cadence_days") or 365)
    covers  = payload.get("covers_evidence_types") or []
    sys_id  = payload.get("id")
    if not name:
        raise HTTPException(status_code=400, detail="system_name is required")
    if not isinstance(covers, list):
        raise HTTPException(status_code=400, detail="covers_evidence_types must be a list")
    cadence = max(1, min(3650, cadence))

    pool = request.app.state.pg_pool
    conn = pool.getconn()
    try:
        set_session(conn, key_info.tenant_id)
        with conn.cursor() as cur:
            if sys_id:
                cur.execute(
                    """
                    UPDATE tenant_external_system
                       SET system_name           = %s,
                           system_url            = %s,
                           owner_user_id         = %s::uuid,
                           default_cadence_days  = %s,
                           covers_evidence_types = %s,
                           updated_at            = now(),
                           updated_by            = %s::uuid
                     WHERE id = %s::uuid AND tenant_id = %s::uuid
                     RETURNING id::text
                    """,
                    (name, url, owner, cadence, covers, key_info.user_id,
                     sys_id, key_info.tenant_id),
                )
            else:
                cur.execute(
                    """
                    INSERT INTO tenant_external_system
                        (tenant_id, system_name, system_url, owner_user_id,
                         default_cadence_days, covers_evidence_types,
                         created_by, updated_by)
                    VALUES (%s::uuid, %s, %s, %s::uuid, %s, %s, %s::uuid, %s::uuid)
                    RETURNING id::text
                    """,
                    (key_info.tenant_id, name, url, owner, cadence, covers,
                     key_info.user_id, key_info.user_id),
                )
            row = cur.fetchone()
        conn.commit()
    finally:
        pool.putconn(conn)
    if not row:
        raise HTTPException(status_code=404, detail="system not found for this tenant")
    return {"id": row[0]}


@app.delete("/api/v1/tenant/external-systems/{system_id}", tags=["templates"])
async def delete_external_system(
    system_id: SystemIdParam,
    request:   Request,
    key_info:  APIKeyInfo = Depends(require_scope("posture")),
):
    """Soft-delete an external system entry. Any cites referencing it
    will also be soft-deleted (so the engine stops counting them)."""
    pool = request.app.state.pg_pool
    conn = pool.getconn()
    try:
        set_session(conn, key_info.tenant_id)
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE tenant_external_system SET is_active = FALSE, "
                "updated_at = now(), updated_by = %s::uuid "
                "WHERE id = %s::uuid AND tenant_id = %s::uuid",
                (key_info.user_id, system_id, key_info.tenant_id),
            )
            cur.execute(
                "UPDATE external_evidence_source SET is_active = FALSE, "
                "updated_at = now(), updated_by = %s::uuid "
                "WHERE system_id = %s::uuid AND tenant_id = %s::uuid",
                (key_info.user_id, system_id, key_info.tenant_id),
            )
            n_cites = cur.rowcount
        conn.commit()
    finally:
        pool.putconn(conn)
    return {"system_id": system_id, "cites_disabled": n_cites}


@app.get("/api/v1/tenant/cites/leaf/{leaf_id:path}", tags=["templates"])
async def list_cites_for_leaf(
    leaf_id: LeafIdParam,
    request:  Request,
    key_info: APIKeyInfo = Depends(require_api_key),
):
    """List external evidence cites for a leaf, grouped by source system.

    Each group: which system, which MUSTs it covers, last verified, next
    review due, current freshness state (fresh / yellow / red).
    """
    pool = request.app.state.pg_pool
    conn = pool.getconn()
    try:
        set_session(conn, key_info.tenant_id)
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT s.id::text, s.system_name, s.system_url,
                       s.default_cadence_days,
                       ees.must_id, ees.cadence_days, ees.per_must_note,
                       ees.last_verified_at, ees.next_review_due
                  FROM external_evidence_source ees
                  JOIN tenant_external_system s ON s.id = ees.system_id
                 WHERE ees.tenant_id = %s::uuid
                   AND ees.leaf_id   = %s
                   AND ees.is_active = TRUE
                   AND s.is_active   = TRUE
                 ORDER BY s.system_name, ees.must_id
                """,
                (key_info.tenant_id, leaf_id),
            )
            rows = cur.fetchall()
    finally:
        pool.putconn(conn)

    # Group by system_id
    from rag.posture.cite_mode import is_cite_fresh
    groups: dict = {}
    for r in rows:
        sid = r[0]
        if sid not in groups:
            groups[sid] = {
                "system_id":            sid,
                "system_name":          r[1],
                "system_url":           r[2] or "",
                "default_cadence_days": r[3],
                "musts":                [],
            }
        groups[sid]["musts"].append({
            "must_id":          r[4],
            "cadence_days":     r[5],
            "per_must_note":    r[6] or "",
            "last_verified_at": r[7].isoformat() if r[7] else None,
            "next_review_due":  r[8].isoformat() if r[8] else None,
            "is_fresh":         is_cite_fresh(r[7], r[5]),
        })
    return {
        "tenant_id": key_info.tenant_id,
        "leaf_id":   leaf_id,
        "groups":    list(groups.values()),
    }


@app.put("/api/v1/tenant/cites/leaf/{leaf_id:path}/source/{system_id}", tags=["templates"])
async def upsert_cites_for_leaf_source(
    leaf_id: LeafIdParam,
    system_id: SystemIdParam,
    request:   Request,
    payload:   dict,
    key_info:  APIKeyInfo = Depends(require_scope("posture")),
):
    """Create or sync cites for (leaf, source). Per-MUST atomic data
    model; UI passes `covered_must_ids[]` from the checkbox form.

    Body:
      {
        "covered_must_ids":  ["item:A.5.18:reg_authoriser", ...],
        "cadence_days":      180,                       // optional override
        "per_must_notes":    {"item:A.5.18:...": "captured in Azure AD"}, // optional
      }

    Backend syncs:
      - For each id in covered_must_ids: insert if missing, update note if changed
      - For each existing active row for (leaf, system) NOT in covered_must_ids:
        soft-delete (tenant unchecked it)
    """
    covered_ids = payload.get("covered_must_ids") or []
    if not isinstance(covered_ids, list):
        raise HTTPException(status_code=400, detail="covered_must_ids must be a list")
    cadence  = payload.get("cadence_days")
    notes    = payload.get("per_must_notes") or {}
    if not isinstance(notes, dict):
        raise HTTPException(status_code=400, detail="per_must_notes must be an object")

    pool = request.app.state.pg_pool
    conn = pool.getconn()
    try:
        set_session(conn, key_info.tenant_id)
        with conn.cursor() as cur:
            # Resolve cadence default from system if not supplied
            if cadence is None:
                cur.execute(
                    "SELECT default_cadence_days FROM tenant_external_system "
                    " WHERE id = %s::uuid AND tenant_id = %s::uuid",
                    (system_id, key_info.tenant_id),
                )
                row = cur.fetchone()
                if not row:
                    raise HTTPException(status_code=404, detail="system not found")
                cadence = int(row[0])
            cadence = max(1, min(3650, int(cadence)))

            # Fetch current active rows for this (leaf, system)
            cur.execute(
                """
                SELECT must_id FROM external_evidence_source
                 WHERE tenant_id = %s::uuid AND leaf_id = %s AND system_id = %s::uuid
                   AND is_active = TRUE
                """,
                (key_info.tenant_id, leaf_id, system_id),
            )
            existing = {r[0] for r in cur.fetchall()}
            wanted   = set(covered_ids)

            to_insert = wanted - existing
            to_remove = existing - wanted
            to_update = wanted & existing

            n_insert = n_update = n_remove = 0

            for mid in to_insert:
                cur.execute(
                    """
                    INSERT INTO external_evidence_source
                        (tenant_id, must_id, leaf_id, system_id,
                         cadence_days, per_must_note, created_by, updated_by)
                    VALUES (%s::uuid, %s, %s, %s::uuid, %s, %s, %s::uuid, %s::uuid)
                    """,
                    (key_info.tenant_id, mid, leaf_id, system_id, cadence,
                     notes.get(mid), key_info.user_id, key_info.user_id),
                )
                n_insert += 1

            for mid in to_update:
                cur.execute(
                    """
                    UPDATE external_evidence_source
                       SET cadence_days  = %s,
                           per_must_note = %s,
                           is_active     = TRUE,
                           updated_at    = now(),
                           updated_by    = %s::uuid
                     WHERE tenant_id = %s::uuid AND must_id = %s AND system_id = %s::uuid
                    """,
                    (cadence, notes.get(mid), key_info.user_id,
                     key_info.tenant_id, mid, system_id),
                )
                n_update += 1

            for mid in to_remove:
                cur.execute(
                    """
                    UPDATE external_evidence_source
                       SET is_active  = FALSE,
                           updated_at = now(),
                           updated_by = %s::uuid
                     WHERE tenant_id = %s::uuid AND must_id = %s AND system_id = %s::uuid
                    """,
                    (key_info.user_id, key_info.tenant_id, mid, system_id),
                )
                n_remove += 1
        conn.commit()
    finally:
        pool.putconn(conn)

    return {
        "leaf_id":   leaf_id,
        "system_id": system_id,
        "inserted":  n_insert,
        "updated":   n_update,
        "removed":   n_remove,
    }


@app.post(
    "/api/v1/tenant/cites/leaf/{leaf_id:path}/source/{system_id}/verify",
    tags=["templates"],
)
async def verify_cites_for_leaf_source(
    leaf_id: LeafIdParam,
    system_id: SystemIdParam,
    request:   Request,
    payload:   dict,
    key_info:  APIKeyInfo = Depends(require_scope("posture")),
):
    """Record a verification attestation for (leaf, source). Updates
    last_verified_at on ALL active cite rows in the group + appends one
    row to external_evidence_verification_log.

    Body:
      {
        "changes_detected":   "5 new employees onboarded; ...",  // REQUIRED
        "note":               "additional free-text",            // optional
        "sample_upload_id":   "<uuid>",                          // optional
        "structured_events": [                                   // optional (S2c)
          {
            "event_type":   "personnel_added",     // REQUIRED, must match
                                                   // known event vocabulary
            "count":        5,                     // REQUIRED, positive int
            "subject_refs": ["emp:101", ...],      // optional
            "metadata":     {...}                  // optional
          },
          ...
        ]
      }

    The `changes_detected` field is the audit-grade payload — forces
    real review rather than rubber-stamp verification. `structured_events`
    is the cascade-engine substrate; if present, the cascade engine (S3)
    will walk the event graph from these emissions.
    """
    changes = (payload.get("changes_detected") or "").strip()
    if not changes:
        raise HTTPException(
            status_code=400,
            detail="changes_detected is required — describe what changed "
                   "since last verification (or 'no changes' explicitly).",
        )
    note   = (payload.get("note") or "").strip() or None
    sample = payload.get("sample_upload_id") or None

    # S2c: validate structured_events if provided.
    raw_events = payload.get("structured_events") or []
    if not isinstance(raw_events, list):
        raise HTTPException(
            status_code=400,
            detail="structured_events must be a list",
        )
    # Lazy import to avoid hard coupling at module load.
    from enrichment.events.event_nodes import ALL_EVENTS
    known_event_types = {e.event_type for e in ALL_EVENTS}
    validated_events: list[dict] = []
    for i, ev in enumerate(raw_events):
        if not isinstance(ev, dict):
            raise HTTPException(400,
                f"structured_events[{i}] must be an object")
        et = ev.get("event_type")
        if not et or et not in known_event_types:
            raise HTTPException(400,
                f"structured_events[{i}].event_type {et!r} unknown — "
                f"must match Event.event_type in the cascade catalog")
        cnt = ev.get("count")
        if not isinstance(cnt, int) or cnt < 1:
            raise HTTPException(400,
                f"structured_events[{i}].count must be a positive integer")
        clean = {"event_type": et, "count": cnt}
        if "subject_refs" in ev:
            sr = ev["subject_refs"]
            if not isinstance(sr, list) or not all(isinstance(x, str) for x in sr):
                raise HTTPException(400,
                    f"structured_events[{i}].subject_refs must be a list of strings")
            if sr:
                clean["subject_refs"] = sr
        if "metadata" in ev:
            md = ev["metadata"]
            if not isinstance(md, dict):
                raise HTTPException(400,
                    f"structured_events[{i}].metadata must be an object")
            if md:
                clean["metadata"] = md
        # S3h: optional occurred_at — when the event actually HAPPENED.
        # Distinct from verified_at (when the tenant attested it). Used
        # by the cascade engine to anchor deadline clocks for scenarios
        # like processor-discovered breach where awareness postdates
        # occurrence. ISO 8601 timestamp string; must not be in the
        # future.
        if "occurred_at" in ev:
            oa_raw = ev["occurred_at"]
            if not isinstance(oa_raw, str) or not oa_raw.strip():
                raise HTTPException(400,
                    f"structured_events[{i}].occurred_at must be an ISO 8601 string")
            from datetime import datetime, timezone
            try:
                oa = datetime.fromisoformat(oa_raw.replace("Z", "+00:00"))
                if oa.tzinfo is None:
                    oa = oa.replace(tzinfo=timezone.utc)
            except ValueError:
                raise HTTPException(400,
                    f"structured_events[{i}].occurred_at not parseable as ISO 8601: {oa_raw!r}")
            if oa > datetime.now(timezone.utc):
                raise HTTPException(400,
                    f"structured_events[{i}].occurred_at cannot be in the future")
            clean["occurred_at"] = oa.isoformat()
        validated_events.append(clean)

    pool = request.app.state.pg_pool
    conn = pool.getconn()
    try:
        set_session(conn, key_info.tenant_id)
        with conn.cursor() as cur:
            # Update last_verified_at + next_review_due on all active cites
            # in this (tenant, leaf, system) group. Compute next_review_due
            # in SQL via interval arithmetic.
            cur.execute(
                """
                UPDATE external_evidence_source
                   SET last_verified_at = now(),
                       next_review_due  = now() + make_interval(days => cadence_days),
                       updated_at       = now(),
                       updated_by       = %s::uuid
                 WHERE tenant_id = %s::uuid
                   AND leaf_id   = %s
                   AND system_id = %s::uuid
                   AND is_active = TRUE
                RETURNING id
                """,
                (key_info.user_id, key_info.tenant_id, leaf_id, system_id),
            )
            updated_ids = cur.fetchall()
            if not updated_ids:
                raise HTTPException(
                    status_code=404,
                    detail="no active cites found for this (leaf, source)",
                )

            # Append the verification log row (with structured_events JSONB)
            import json as _json
            cur.execute(
                """
                INSERT INTO external_evidence_verification_log
                    (tenant_id, system_id, leaf_id, verified_by,
                     changes_detected, sample_upload_id, note,
                     musts_covered_count, structured_events)
                VALUES (%s::uuid, %s::uuid, %s, %s::uuid, %s, %s::uuid, %s, %s, %s::jsonb)
                RETURNING id::text, verified_at
                """,
                (key_info.tenant_id, system_id, leaf_id, key_info.user_id,
                 changes, sample, note, len(updated_ids),
                 _json.dumps(validated_events)),
            )
            log_row = cur.fetchone()

            # ── S3 cascade fire ─────────────────────────────────────────
            # If structured_events were submitted, synchronously walk the
            # cascade graph and write triggered_implication rows. Best-
            # effort: on engine error, log + swallow rather than fail
            # the verification (audit trail still complete via log row).
            implications_written = 0
            followups_written    = 0
            followups_satisfied  = 0
            fact_changes_applied = 0
            fact_changes_logged  = 0
            scope_implications   = 0
            suppressions         = 0
            auto_resolved        = 0
            if validated_events:
                neo_drv = None
                try:
                    from rag.posture_loader import _build_engine_neo4j_driver
                    from rag.cascade.engine import fire_cascade
                    neo_drv = _build_engine_neo4j_driver()
                    if neo_drv is None:
                        logger.warning("cascade engine: Neo4j driver "
                                       "unavailable; skipping cascade for "
                                       "verify %s", log_row[0])
                    else:
                        with neo_drv.session() as neo_session:
                            cascade_result = fire_cascade(
                                cur, neo_session,
                                tenant_id           = key_info.tenant_id,
                                verification_log_id = log_row[0],
                                verified_at         = log_row[1],
                                structured_events   = validated_events,
                            )
                            implications_written = cascade_result["implications"]
                            followups_written    = cascade_result["followups_written"]
                            followups_satisfied  = cascade_result["followups_satisfied"]
                            fact_changes_applied = cascade_result.get("fact_changes_applied", 0)
                            fact_changes_logged  = cascade_result.get("fact_changes_logged",  0)
                            scope_implications   = cascade_result.get("scope_implications",   0)
                            suppressions         = cascade_result.get("suppressions",         0)
                            auto_resolved        = cascade_result.get("auto_resolved",        0)
                except Exception as ex:
                    logger.exception("cascade engine failed for verify %s: %s",
                                     log_row[0], ex)
                    # Continue — log the failure but don't roll back the
                    # verification commit.
                finally:
                    if neo_drv is not None:
                        try: neo_drv.close()
                        except Exception: pass
        conn.commit()
    finally:
        pool.putconn(conn)
    return {
        "verification_log_id":  log_row[0],
        "verified_at":          log_row[1].isoformat(),
        "musts_covered":        len(updated_ids),
        "structured_events":    len(validated_events),
        "implications_written": implications_written,
        "followups_written":    followups_written,
        "followups_satisfied":  followups_satisfied,
        "fact_changes_applied": fact_changes_applied,
        "fact_changes_logged":  fact_changes_logged,
        "scope_implications":   scope_implications,
        "suppressions":         suppressions,
        "auto_resolved":        auto_resolved,
    }


@app.get("/api/v1/tenant/cascade-events/vocabulary", tags=["templates"])
async def cascade_events_vocabulary(
    request: Request,
    key_info: APIKeyInfo = Depends(require_api_key),
):
    """Return the cascade-event vocabulary the verify-dialog UI uses to
    populate the structured-events picker. Reads from
    enrichment/events/event_nodes.py — single source of truth.

    Grouped by category so the UI can render a categorised picker.
    """
    from enrichment.events.event_nodes import ALL_EVENTS
    by_cat: dict[str, list[dict]] = {}
    for ev in ALL_EVENTS:
        cat = ev.category
        by_cat.setdefault(cat, []).append({
            "event_type":  ev.event_type,
            "title":       ev.title,
            "description": ev.description,
        })
    # Sort within each category by event_type for stable ordering.
    for cat in by_cat:
        by_cat[cat].sort(key=lambda e: e["event_type"])
    return {"vocabulary": by_cat}


@app.get("/api/v1/tenant/triggered-implications", tags=["posture"])
async def list_triggered_implications(
    request: Request,
    key_info: APIKeyInfo = Depends(require_api_key),
    status:  str = "pending",
    group_by_verification: bool = True,
):
    """List triggered implications for this tenant.

    Default returns pending (the actionable set). Pass status=satisfied
    or dismissed for historical views. Pass group_by_verification=False
    for a flat list.

    Pending rows past their due_date carry overdue=true in the response
    (computed, not stored).
    """
    if status not in ("pending", "satisfied", "dismissed"):
        raise HTTPException(400, "status must be pending / satisfied / dismissed")

    pool = request.app.state.pg_pool
    conn = pool.getconn()
    try:
        set_session(conn, key_info.tenant_id)
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT id::text,
                       source_verification_id::text,
                       source_event_type,
                       cascade_path,
                       cascade_depth,
                       target_control_ref,
                       target_standard_id,
                       target_requirement_id,
                       expected_action,
                       fired_at,
                       due_date,
                       status,
                       resolved_at,
                       resolved_evidence_kind,
                       dismissed_reason,
                       deadline_string,
                       rationale,
                       scope_kind,
                       clock_anchor
                  FROM triggered_implication
                 WHERE tenant_id = %s::uuid
                   AND status    = %s
                 ORDER BY due_date NULLS LAST, fired_at DESC
                """,
                (key_info.tenant_id, status),
            )
            rows = cur.fetchall()

    finally:
        pool.putconn(conn)

    from datetime import datetime, timezone
    now = datetime.now(timezone.utc)
    items = []
    for r in rows:
        due = r[10]
        items.append({
            "id":                    r[0],
            "source_verification_id": r[1],
            "source_event_type":     r[2],
            "cascade_path":          r[3],
            "cascade_depth":         r[4],
            "target_control_ref":    r[5],
            "target_standard_id":    r[6],
            "target_requirement_id": r[7],
            "expected_action":       r[8],
            "fired_at":              r[9].isoformat() if r[9] else None,
            "due_date":              due.isoformat() if due else None,
            "overdue":               bool(status == "pending" and due and due < now),
            "status":                r[11],
            "resolved_at":           r[12].isoformat() if r[12] else None,
            "resolved_evidence_kind": r[13],
            "dismissed_reason":      r[14],
            "deadline_string":       r[15],
            "rationale":             r[16],
            "scope_kind":            r[17],
            "clock_anchor":          r[18],
        })

    if not group_by_verification:
        return {"items": items, "count": len(items)}

    # Group by source_verification_id; preserve per-group ordering
    groups: dict[str, dict] = {}
    for it in items:
        vid = it["source_verification_id"]
        if vid not in groups:
            groups[vid] = {
                "verification_id":  vid,
                "source_event_types": [],
                "implications":     [],
            }
        groups[vid]["implications"].append(it)
        if it["source_event_type"] not in groups[vid]["source_event_types"]:
            groups[vid]["source_event_types"].append(it["source_event_type"])
    return {
        "groups": list(groups.values()),
        "count":  len(items),
        "group_count": len(groups),
    }


@app.patch("/api/v1/tenant/triggered-implications/{imp_id}", tags=["posture"])
async def update_triggered_implication(
    imp_id: ImplicationIdParam,
    request:  Request,
    payload:  dict,
    key_info: APIKeyInfo = Depends(require_scope("posture")),
):
    """Resolve a triggered implication.

    Body must include status='satisfied' or status='dismissed'. When
    dismissing, dismissed_reason is required (audit-grade). Satisfied
    rows may optionally carry resolved_evidence_kind + resolved_evidence_id.
    """
    new_status = payload.get("status")
    if new_status not in ("satisfied", "dismissed"):
        raise HTTPException(
            400,
            "Please mark the follow-up as either satisfied or dismissed."
        )

    dismissed_reason = (payload.get("dismissed_reason") or "").strip() or None
    if new_status == "dismissed" and not dismissed_reason:
        raise HTTPException(
            400,
            "Please add an auditor-grade explanation of why you're "
            "dismissing this follow-up."
        )

    ev_kind = payload.get("resolved_evidence_kind")
    ev_id   = payload.get("resolved_evidence_id")
    if ev_kind and ev_kind not in ("finding", "cite", "dismissal"):
        raise HTTPException(400,
            "resolved_evidence_kind must be finding / cite / dismissal")

    pool = request.app.state.pg_pool
    conn = pool.getconn()
    try:
        set_session(conn, key_info.tenant_id)
        with conn.cursor() as cur:
            cur.execute(
                """
                UPDATE triggered_implication
                   SET status                 = %s,
                       resolved_at            = now(),
                       resolved_by            = %s::uuid,
                       resolved_evidence_kind = %s,
                       resolved_evidence_id   = %s::uuid,
                       dismissed_reason       = %s
                 WHERE tenant_id = %s::uuid
                   AND id        = %s::uuid
                   AND status    = 'pending'
                RETURNING id::text, status, resolved_at
                """,
                (new_status, key_info.user_id, ev_kind, ev_id,
                 dismissed_reason, key_info.tenant_id, imp_id),
            )
            updated = cur.fetchone()
        conn.commit()
    finally:
        pool.putconn(conn)
    if not updated:
        raise HTTPException(404,
            "implication not found or no longer pending")
    return {
        "id":           updated[0],
        "status":       updated[1],
        "resolved_at":  updated[2].isoformat(),
    }


@app.get("/api/v1/tenant/expected-followups", tags=["posture"])
async def list_expected_followups(
    request: Request,
    key_info: APIKeyInfo = Depends(require_api_key),
    status:  str = "pending",
):
    """List expected followup events for this tenant.

    status: pending | satisfied | overdue. Default pending.
    Overdue rows reflect cascade chains where a downstream event
    was expected within a window but never arrived (e.g. personnel
    offboarded but no privilege_revoked within 24h).
    """
    if status not in ("pending", "satisfied", "overdue"):
        raise HTTPException(400, "status must be pending / satisfied / overdue")

    pool = request.app.state.pg_pool
    conn = pool.getconn()
    try:
        set_session(conn, key_info.tenant_id)
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT id::text, source_verification_id::text,
                       source_event_type, expected_event_type,
                       window_days, fired_at, expires_at, status,
                       resolved_at, resolved_verification_id::text,
                       rationale
                  FROM expected_followup_event
                 WHERE tenant_id = %s::uuid
                   AND status    = %s
                 ORDER BY expires_at
                """,
                (key_info.tenant_id, status),
            )
            rows = cur.fetchall()
    finally:
        pool.putconn(conn)

    from datetime import datetime, timezone
    now = datetime.now(timezone.utc)
    items = []
    for r in rows:
        exp = r[6]
        items.append({
            "id":                       r[0],
            "source_verification_id":   r[1],
            "source_event_type":        r[2],
            "expected_event_type":      r[3],
            "window_days":              r[4],
            "fired_at":                 r[5].isoformat() if r[5] else None,
            "expires_at":               exp.isoformat() if exp else None,
            "status":                   r[7],
            "resolved_at":              r[8].isoformat() if r[8] else None,
            "resolved_verification_id": r[9],
            "rationale":                r[10],
            "days_until_expiry":        (
                int((exp - now).total_seconds() / 86400) if exp and r[7] == "pending" else None
            ),
        })
    return {"items": items, "count": len(items)}


@app.get("/api/v1/tenant/cascade-event/{kind}/{eid}", tags=["posture"])
async def cascade_event_detail(
    kind: CascadeKindParam,
    eid: str,
    request:  Request,
    key_info: APIKeyInfo = Depends(require_api_key),
):
    """Auditor-grade detail for a single cascade-timeline row.

    Returns the focal event plus all related rows chained from the
    same source_verification_id (or — for verifications — every
    implication/followup/suppression that fired from this
    verification).
    """
    if kind not in ("verification", "implication", "followup", "suppression"):
        raise HTTPException(400, "kind must be verification / implication / "
                                  "followup / suppression")

    pool = request.app.state.pg_pool
    conn = pool.getconn()
    try:
        set_session(conn, key_info.tenant_id)
        with conn.cursor() as cur:
            focal = None
            verification_id = None
            if kind == "verification":
                cur.execute(
                    """
                    SELECT id::text, verified_at, leaf_id, system_id::text,
                           structured_events, changes_detected, note,
                           musts_covered_count
                      FROM external_evidence_verification_log
                     WHERE tenant_id = %s::uuid AND id = %s::uuid
                    """,
                    (key_info.tenant_id, eid),
                )
                r = cur.fetchone()
                if r:
                    verification_id = r[0]
                    focal = {
                        "kind":               "verification",
                        "id":                 r[0],
                        "verified_at":        r[1].isoformat() if r[1] else None,
                        "leaf_id":            r[2],
                        "system_id":          r[3],
                        "structured_events":  r[4],
                        "changes_detected":   r[5],
                        "note":               r[6],
                        "musts_covered_count": r[7],
                    }
            elif kind == "implication":
                cur.execute(
                    """
                    SELECT id::text, source_verification_id::text,
                           source_event_type, cascade_path, cascade_depth,
                           target_control_ref, target_standard_id,
                           target_requirement_id, expected_action,
                           fired_at, due_date, status,
                           resolved_at, resolved_by::text, resolved_evidence_kind,
                           resolved_evidence_id::text, dismissed_reason,
                           rationale, deadline_string, scope_kind, clock_anchor
                      FROM triggered_implication
                     WHERE tenant_id = %s::uuid AND id = %s::uuid
                    """,
                    (key_info.tenant_id, eid),
                )
                r = cur.fetchone()
                if r:
                    verification_id = r[1]
                    focal = {
                        "kind":              "implication",
                        "id":                r[0],
                        "source_verification_id": r[1],
                        "source_event_type": r[2],
                        "cascade_path":      r[3],
                        "cascade_depth":     r[4],
                        "target_control_ref": r[5],
                        "target_standard_id": r[6],
                        "target_requirement_id": r[7],
                        "expected_action":   r[8],
                        "fired_at":          r[9].isoformat() if r[9] else None,
                        "due_date":          r[10].isoformat() if r[10] else None,
                        "status":            r[11],
                        "resolved_at":       r[12].isoformat() if r[12] else None,
                        "resolved_by":       r[13],
                        "resolved_evidence_kind": r[14],
                        "resolved_evidence_id":   r[15],
                        "dismissed_reason":  r[16],
                        "rationale":         r[17],
                        "deadline_string":   r[18],
                        "scope_kind":        r[19],
                        "clock_anchor":      r[20],
                    }
            elif kind == "followup":
                cur.execute(
                    """
                    SELECT id::text, source_verification_id::text,
                           source_event_type, expected_event_type,
                           window_days, fired_at, expires_at, status,
                           resolved_at, resolved_verification_id::text,
                           rationale
                      FROM expected_followup_event
                     WHERE tenant_id = %s::uuid AND id = %s::uuid
                    """,
                    (key_info.tenant_id, eid),
                )
                r = cur.fetchone()
                if r:
                    verification_id = r[1]
                    focal = {
                        "kind":                  "followup",
                        "id":                    r[0],
                        "source_verification_id": r[1],
                        "source_event_type":     r[2],
                        "expected_event_type":   r[3],
                        "window_days":           r[4],
                        "fired_at":              r[5].isoformat() if r[5] else None,
                        "expires_at":            r[6].isoformat() if r[6] else None,
                        "status":                r[7],
                        "resolved_at":           r[8].isoformat() if r[8] else None,
                        "resolved_verification_id": r[9],
                        "rationale":             r[10],
                    }
            elif kind == "suppression":
                cur.execute(
                    """
                    SELECT id::text, source_verification_id::text,
                           source_event_type, target_event_type,
                           applies_when, evaluation_context, cascade_path,
                           fired_at, suppression_kind, target_requirement_id
                      FROM cascade_suppression_log
                     WHERE tenant_id = %s::uuid AND id = %s::uuid
                    """,
                    (key_info.tenant_id, eid),
                )
                r = cur.fetchone()
                if r:
                    verification_id = r[1]
                    focal = {
                        "kind":                  "suppression",
                        "id":                    r[0],
                        "source_verification_id": r[1],
                        "source_event_type":     r[2],
                        "target_event_type":     r[3],
                        "applies_when":          r[4],
                        "evaluation_context":    r[5],
                        "cascade_path":          r[6],
                        "fired_at":              r[7].isoformat() if r[7] else None,
                        "suppression_kind":      r[8],
                        "target_requirement_id": r[9],
                    }

            if not focal:
                raise HTTPException(404, f"{kind} {eid} not found")

            # ── Related rows — anchored on verification_id ──────────
            related = {
                "implications": [],
                "followups":    [],
                "suppressions": [],
            }
            if verification_id:
                cur.execute(
                    """
                    SELECT id::text, source_event_type, expected_action,
                           target_control_ref, status, due_date,
                           cascade_depth, rationale, scope_kind
                      FROM triggered_implication
                     WHERE tenant_id              = %s::uuid
                       AND source_verification_id = %s::uuid
                     ORDER BY fired_at
                    """,
                    (key_info.tenant_id, verification_id),
                )
                for r in cur.fetchall():
                    related["implications"].append({
                        "id":                r[0],
                        "source_event_type": r[1],
                        "expected_action":   r[2],
                        "control_ref":       r[3],
                        "status":            r[4],
                        "due_date":          r[5].isoformat() if r[5] else None,
                        "cascade_depth":     r[6],
                        "rationale":         r[7],
                        "scope_kind":        r[8],
                    })
                cur.execute(
                    """
                    SELECT id::text, source_event_type, expected_event_type,
                           window_days, status, expires_at
                      FROM expected_followup_event
                     WHERE tenant_id              = %s::uuid
                       AND source_verification_id = %s::uuid
                     ORDER BY fired_at
                    """,
                    (key_info.tenant_id, verification_id),
                )
                for r in cur.fetchall():
                    related["followups"].append({
                        "id":                  r[0],
                        "source_event_type":   r[1],
                        "expected_event_type": r[2],
                        "window_days":         r[3],
                        "status":              r[4],
                        "expires_at":          r[5].isoformat() if r[5] else None,
                    })
                cur.execute(
                    """
                    SELECT id::text, suppression_kind, source_event_type,
                           target_event_type, target_requirement_id, applies_when
                      FROM cascade_suppression_log
                     WHERE tenant_id              = %s::uuid
                       AND source_verification_id = %s::uuid
                     ORDER BY fired_at
                    """,
                    (key_info.tenant_id, verification_id),
                )
                for r in cur.fetchall():
                    related["suppressions"].append({
                        "id":                    r[0],
                        "suppression_kind":      r[1],
                        "source_event_type":     r[2],
                        "target_event_type":     r[3],
                        "target_requirement_id": r[4],
                        "applies_when":          r[5],
                    })
    finally:
        pool.putconn(conn)

    return {"focal": focal, "related": related}


@app.get("/api/v1/tenant/cascade-timeline", tags=["posture"])
async def cascade_timeline(
    request:      Request,
    key_info:     APIKeyInfo = Depends(require_api_key),
    control_ref:  Optional[str] = None,
    event_type:   Optional[str] = None,
    since_days:   int = 30,
    limit:        int = 200,
):
    """Chronological cascade-events timeline for the auditor view.

    Unions four tables — verifications with structured events,
    triggered implications, expected followups, suppressions — into
    a single time-ordered stream. Each row carries kind +
    descriptive payload + a stable id.

    Filters:
      control_ref: restrict to a single control's events
      event_type:  restrict to a single source_event_type. Tenants can
                   type either the natural form ("personnel offboarded")
                   or the machine slug ("personnel_offboarded"); the
                   filter normalises to underscore form for exact match.
      since_days:  rolling window (default 30)
      limit:       hard cap on returned rows
    """
    # Normalise event_type filter so the UI placeholder can show the
    # natural form without breaking exact-match on the raw slug backing
    # `structured_events[i].event_type`.
    if event_type:
        event_type = event_type.strip().replace(" ", "_").lower()
    pool = request.app.state.pg_pool
    conn = pool.getconn()
    items: list[dict] = []
    try:
        set_session(conn, key_info.tenant_id)
        with conn.cursor() as cur:
            # ── Verifications with structured events ────────────────
            cur.execute(
                """
                SELECT id::text, verified_at, leaf_id, structured_events,
                       changes_detected, system_id::text
                  FROM external_evidence_verification_log
                 WHERE tenant_id   = %s::uuid
                   AND verified_at >= now() - make_interval(days => %s)
                   AND structured_events <> '[]'::jsonb
                 ORDER BY verified_at DESC
                 LIMIT %s
                """,
                (key_info.tenant_id, since_days, max(50, limit)),
            )
            for r in cur.fetchall():
                evts = r[3] or []
                for ev in evts:
                    et = ev.get("event_type", "")
                    if event_type and et != event_type:
                        continue
                    items.append({
                        "kind":              "verification",
                        "id":                r[0],
                        "ts":                r[1].isoformat() if r[1] else None,
                        "event_type":        et,
                        "count":             ev.get("count", 1),
                        "leaf_id":           r[2],
                        "control_ref":       None,
                        "summary":           (r[4] or "")[:240],
                        "metadata":          ev.get("metadata") or {},
                    })

            # ── Implications fired / resolved ───────────────────────
            cur.execute(
                """
                SELECT id::text, fired_at, source_event_type, expected_action,
                       target_control_ref, target_standard_id, cascade_path,
                       cascade_depth, status, resolved_at,
                       resolved_evidence_kind, dismissed_reason,
                       rationale, due_date, clock_anchor, scope_kind
                  FROM triggered_implication
                 WHERE tenant_id = %s::uuid
                   AND fired_at  >= now() - make_interval(days => %s)
                """ + ("   AND target_control_ref = %s\n" if control_ref else "") + """
                """ + ("   AND source_event_type   = %s\n" if event_type   else "") + """
                 ORDER BY fired_at DESC
                 LIMIT %s
                """,
                tuple([key_info.tenant_id, since_days]
                      + ([control_ref] if control_ref else [])
                      + ([event_type]  if event_type  else [])
                      + [max(50, limit)]),
            )
            for r in cur.fetchall():
                items.append({
                    "kind":           "implication",
                    "id":             r[0],
                    "ts":             r[1].isoformat() if r[1] else None,
                    "event_type":     r[2],
                    "expected_action": r[3],
                    "control_ref":    r[4],
                    "standard_id":    r[5],
                    "cascade_path":   r[6],
                    "cascade_depth":  r[7],
                    "status":         r[8],
                    "resolved_at":    r[9].isoformat() if r[9] else None,
                    "resolved_evidence_kind": r[10],
                    "dismissed_reason": r[11],
                    "rationale":      (r[12] or "")[:200],
                    "due_date":       r[13].isoformat() if r[13] else None,
                    "clock_anchor":   r[14],
                    "scope_kind":     r[15],
                })

            # ── Expected followups ──────────────────────────────────
            cur.execute(
                """
                SELECT id::text, fired_at, source_event_type, expected_event_type,
                       window_days, expires_at, status, rationale
                  FROM expected_followup_event
                 WHERE tenant_id = %s::uuid
                   AND fired_at  >= now() - make_interval(days => %s)
                """ + ("   AND source_event_type = %s\n" if event_type else "") + """
                 ORDER BY fired_at DESC
                 LIMIT %s
                """,
                tuple([key_info.tenant_id, since_days]
                      + ([event_type] if event_type else [])
                      + [max(50, limit)]),
            )
            for r in cur.fetchall():
                items.append({
                    "kind":           "followup",
                    "id":             r[0],
                    "ts":             r[1].isoformat() if r[1] else None,
                    "event_type":     r[2],
                    "expected_event_type": r[3],
                    "window_days":    r[4],
                    "expires_at":     r[5].isoformat() if r[5] else None,
                    "status":         r[6],
                    "rationale":      r[7],
                })

            # ── Suppressions ────────────────────────────────────────
            cur.execute(
                """
                SELECT id::text, fired_at, suppression_kind,
                       source_event_type, target_event_type,
                       target_requirement_id, applies_when, cascade_path
                  FROM cascade_suppression_log
                 WHERE tenant_id = %s::uuid
                   AND fired_at  >= now() - make_interval(days => %s)
                """ + ("   AND source_event_type = %s\n" if event_type else "") + """
                 ORDER BY fired_at DESC
                 LIMIT %s
                """,
                tuple([key_info.tenant_id, since_days]
                      + ([event_type] if event_type else [])
                      + [max(50, limit)]),
            )
            for r in cur.fetchall():
                items.append({
                    "kind":             "suppression",
                    "id":               r[0],
                    "ts":               r[1].isoformat() if r[1] else None,
                    "suppression_kind": r[2],
                    "event_type":       r[3],
                    "target_event_type": r[4],
                    "target_requirement_id": r[5],
                    "applies_when":     r[6],
                    "cascade_path":     r[7],
                })
    finally:
        pool.putconn(conn)

    # Optional control filter applies to rows that don't have target
    # filtering at SQL (verifications + suppressions whose tag isn't
    # target_requirement_id).
    if control_ref:
        full_id_suffix = ":" + control_ref
        def matches(item: dict) -> bool:
            cr  = item.get("control_ref")
            trq = item.get("target_requirement_id")
            return (
                cr == control_ref
                or (trq and trq.endswith(full_id_suffix))
                # Verifications are kept regardless — control scoping
                # is best-effort via leaf_id pattern matching, not strict.
                or item.get("kind") == "verification"
            )
        items = [i for i in items if matches(i)]

    items.sort(key=lambda i: i.get("ts") or "", reverse=True)
    items = items[:limit]
    return {
        "items":      items,
        "count":      len(items),
        "since_days": since_days,
        "filters": {
            "control_ref": control_ref,
            "event_type":  event_type,
        },
    }


@app.get("/api/v1/dashboard/leaf/{leaf_id:path}/evidence-package",
         tags=["posture"])
async def dashboard_leaf_evidence_package(
    leaf_id: LeafIdParam,
    request:  Request,
    key_info: APIKeyInfo = Depends(require_api_key),
    fmt:      str = "md",
):
    """Return an auto-generated evidence package for a leaf — auditor-
    ready markdown showing standard obligation + per-MUST coverage
    with source excerpts + citations. Refreshed on every download.

    fmt='md' returns text/markdown (default). Future: docx/pdf.
    """
    if fmt != "md":
        raise HTTPException(400, "only fmt='md' supported at v1")
    pool = request.app.state.pg_pool
    conn = pool.getconn()
    try:
        set_session(conn, key_info.tenant_id)
        from rag.posture.evidence_package import build_evidence_package
        body = build_evidence_package(conn, key_info.tenant_id, leaf_id)
    finally:
        pool.putconn(conn)
    if body is None:
        raise HTTPException(404, f"leaf {leaf_id!r} not found in catalog")
    # Serve as attachment with a stable filename
    safe = leaf_id.replace(":", "_").replace("/", "_")
    fname = f"evidence_package_{safe}.md"
    from fastapi.responses import Response
    return Response(
        content=body,
        media_type="text/markdown; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{fname}"'},
    )


@app.get("/api/v1/dashboard/control/{control_ref}/canonical", tags=["posture"])
async def dashboard_control_canonical(
    control_ref: ControlRefParam,
    request:     Request,
    standard_id: Optional[str] = None,
    key_info:    APIKeyInfo = Depends(require_api_key),
):
    """Return canonical title + obligation text for a control (the
    standard's authoritative statement). Used by the dashboard heatmap
    cell detail panel to surface "what does A.5.15 actually say?".

    standard_id is optional: defaults to ISO27001:2022 when the ref
    starts with A.x or a clause-style number; defaults to GDPR:2016/679
    when the ref starts with Art.
    """
    if standard_id is None:
        standard_id = _infer_standard_from_ref(control_ref)
    neo_drv = None
    try:
        from rag.posture_loader import _build_engine_neo4j_driver
        neo_drv = _build_engine_neo4j_driver()
        summary = _resolve_control_summary(neo_drv, standard_id, control_ref)
    finally:
        if neo_drv is not None:
            try: neo_drv.close()
            except Exception: pass
    return summary


@app.get("/api/v1/dashboard/cascade-kpis", tags=["posture"])
async def cascade_kpis(
    request: Request,
    key_info: APIKeyInfo = Depends(require_api_key),
):
    """Aggregate cascade-output KPIs for the dashboard top tile row.

    Returns counts across the cascade tables for this tenant:
      pending_implications:  total / overdue / by_action
      pending_followups:     total / overdue
      suppressions_30d:      total / by_kind
      auto_resolved_7d:      count of satisfied impls with kind='cite'
      controls_with_pressure: distinct count of target_requirement_id
                              having any pending implication
    """
    pool = request.app.state.pg_pool
    conn = pool.getconn()
    try:
        set_session(conn, key_info.tenant_id)
        with conn.cursor() as cur:
            # ── Implications counts ──────────────────────────────────
            cur.execute(
                """
                SELECT count(*) FILTER (WHERE status = 'pending') AS pending_total,
                       count(*) FILTER (WHERE status = 'pending'
                                          AND due_date IS NOT NULL
                                          AND due_date < now()) AS overdue,
                       count(*) FILTER (WHERE status = 'pending'
                                          AND expected_action = 'evidence_required') AS evidence_pending,
                       count(*) FILTER (WHERE status = 'pending'
                                          AND expected_action = 'review_required') AS review_pending,
                       count(*) FILTER (WHERE status = 'pending'
                                          AND expected_action = 'attestation_required') AS attest_pending,
                       count(DISTINCT target_requirement_id) FILTER (WHERE status = 'pending') AS controls_with_pressure
                  FROM triggered_implication
                 WHERE tenant_id = %s::uuid
                """,
                (key_info.tenant_id,),
            )
            impl_row = cur.fetchone()

            # ── Followups ────────────────────────────────────────────
            cur.execute(
                """
                SELECT count(*) FILTER (WHERE status = 'pending') AS pending,
                       count(*) FILTER (WHERE status = 'overdue') AS overdue
                  FROM expected_followup_event
                 WHERE tenant_id = %s::uuid
                """,
                (key_info.tenant_id,),
            )
            fu_row = cur.fetchone()

            # ── Suppressions in last 30 days ─────────────────────────
            cur.execute(
                """
                SELECT suppression_kind, count(*)
                  FROM cascade_suppression_log
                 WHERE tenant_id = %s::uuid
                   AND fired_at >= now() - interval '30 days'
                 GROUP BY suppression_kind
                """,
                (key_info.tenant_id,),
            )
            supp_rows = cur.fetchall()
            supp_by_kind = {r[0]: int(r[1]) for r in supp_rows}
            supp_total = sum(supp_by_kind.values())

            # ── Auto-resolved in last 7 days ─────────────────────────
            cur.execute(
                """
                SELECT count(*)
                  FROM triggered_implication
                 WHERE tenant_id = %s::uuid
                   AND status = 'satisfied'
                   AND resolved_evidence_kind = 'cite'
                   AND resolved_at >= now() - interval '7 days'
                """,
                (key_info.tenant_id,),
            )
            auto_row = cur.fetchone()

            # ── Recent verifications (counts) ────────────────────────
            cur.execute(
                """
                SELECT count(*),
                       count(*) FILTER (WHERE structured_events <> '[]'::jsonb)
                  FROM external_evidence_verification_log
                 WHERE tenant_id = %s::uuid
                   AND verified_at >= now() - interval '7 days'
                """,
                (key_info.tenant_id,),
            )
            verif_row = cur.fetchone()
    finally:
        pool.putconn(conn)

    return {
        "pending_implications": {
            "total":       int(impl_row[0] or 0),
            "overdue":     int(impl_row[1] or 0),
            "by_action": {
                "evidence_required":     int(impl_row[2] or 0),
                "review_required":       int(impl_row[3] or 0),
                "attestation_required":  int(impl_row[4] or 0),
            },
        },
        "controls_with_pressure":  int(impl_row[5] or 0),
        "pending_followups": {
            "pending": int(fu_row[0] or 0),
            "overdue": int(fu_row[1] or 0),
        },
        "suppressions_30d": {
            "total":   supp_total,
            "by_kind": supp_by_kind,
        },
        "auto_resolved_7d":  int(auto_row[0] or 0),
        "verifications_7d": {
            "total":              int(verif_row[0] or 0),
            "with_structured":    int(verif_row[1] or 0),
        },
    }


@app.get("/api/v1/tenant/notifications", tags=["posture"])
async def list_notifications(
    request:  Request,
    key_info: APIKeyInfo = Depends(require_api_key),
    status:   str = "unread",
    limit:    int = 100,
):
    """List tenant notifications. status: unread | all | dismissed."""
    if status not in ("unread", "all", "dismissed"):
        raise HTTPException(400, "status must be unread / all / dismissed")
    pool = request.app.state.pg_pool
    conn = pool.getconn()
    try:
        set_session(conn, key_info.tenant_id)
        with conn.cursor() as cur:
            where_extra = ""
            if status == "unread":
                where_extra = " AND read_at IS NULL AND dismissed_at IS NULL"
            elif status == "dismissed":
                where_extra = " AND dismissed_at IS NOT NULL"
            cur.execute(
                f"""
                SELECT id::text, kind, title, body, severity,
                       related_entity_kind, related_entity_id::text,
                       related_control_ref, related_event_type,
                       fired_at, read_at, dismissed_at
                  FROM tenant_notification
                 WHERE tenant_id = %s::uuid
                       {where_extra}
                 ORDER BY fired_at DESC
                 LIMIT %s
                """,
                (key_info.tenant_id, max(1, min(int(limit), 500))),
            )
            rows = cur.fetchall()
            # Counts for the bell badge
            cur.execute(
                """
                SELECT count(*) AS unread,
                       count(*) FILTER (WHERE severity IN ('critical','high')) AS urgent
                  FROM tenant_notification
                 WHERE tenant_id = %s::uuid
                   AND read_at IS NULL
                   AND dismissed_at IS NULL
                """,
                (key_info.tenant_id,),
            )
            counts = cur.fetchone()
    finally:
        pool.putconn(conn)
    return {
        "items": [
            {
                "id":                   r[0],
                "kind":                 r[1],
                "title":                r[2],
                "body":                 r[3],
                "severity":             r[4],
                "related_entity_kind":  r[5],
                "related_entity_id":    r[6],
                "related_control_ref":  r[7],
                "related_event_type":   r[8],
                "fired_at":             r[9].isoformat()  if r[9]  else None,
                "read_at":              r[10].isoformat() if r[10] else None,
                "dismissed_at":         r[11].isoformat() if r[11] else None,
            } for r in rows
        ],
        "count":  len(rows),
        "unread": int(counts[0] or 0),
        "urgent": int(counts[1] or 0),
    }


@app.patch("/api/v1/tenant/notifications/{nid}", tags=["posture"])
async def patch_notification(
    nid: NotifIdParam,
    request:  Request,
    payload:  dict,
    key_info: APIKeyInfo = Depends(require_scope("posture")),
):
    """Mark a notification read or dismissed.

    Body: action: 'read' | 'dismiss' (read also accepted for idempotency).
    """
    action = payload.get("action")
    if action not in ("read", "dismiss"):
        raise HTTPException(400, "action must be 'read' or 'dismiss'")
    pool = request.app.state.pg_pool
    conn = pool.getconn()
    try:
        set_session(conn, key_info.tenant_id)
        with conn.cursor() as cur:
            if action == "read":
                cur.execute(
                    """
                    UPDATE tenant_notification
                       SET read_at = coalesce(read_at, now())
                     WHERE tenant_id = %s::uuid
                       AND id        = %s::uuid
                    RETURNING id::text, read_at
                    """,
                    (key_info.tenant_id, nid),
                )
            else:  # dismiss
                cur.execute(
                    """
                    UPDATE tenant_notification
                       SET dismissed_at = coalesce(dismissed_at, now()),
                           read_at      = coalesce(read_at, now())
                     WHERE tenant_id = %s::uuid
                       AND id        = %s::uuid
                    RETURNING id::text, dismissed_at
                    """,
                    (key_info.tenant_id, nid),
                )
            updated = cur.fetchone()
        conn.commit()
    finally:
        pool.putconn(conn)
    if not updated:
        raise HTTPException(404, "notification not found")
    return {"id": updated[0], "action": action,
            "ts": updated[1].isoformat() if updated[1] else None}


@app.post("/api/v1/tenant/notifications/mark-all-read", tags=["posture"])
async def mark_all_notifications_read(
    request:  Request,
    key_info: APIKeyInfo = Depends(require_scope("posture")),
):
    """Mark every unread notification as read for this tenant."""
    pool = request.app.state.pg_pool
    conn = pool.getconn()
    try:
        set_session(conn, key_info.tenant_id)
        with conn.cursor() as cur:
            cur.execute(
                """
                UPDATE tenant_notification
                   SET read_at = now()
                 WHERE tenant_id = %s::uuid
                   AND read_at IS NULL
                RETURNING id
                """,
                (key_info.tenant_id,),
            )
            rows = cur.fetchall()
        conn.commit()
    finally:
        pool.putconn(conn)
    return {"marked_read": len(rows)}


@app.post("/api/v1/tenant/triggered-implications/bulk", tags=["posture"])
async def bulk_resolve_implications(
    request:  Request,
    payload:  dict,
    key_info: APIKeyInfo = Depends(require_scope("posture")),
):
    """Bulk-resolve all pending implications from a single verification.

    Body:
      source_verification_id: UUID — required, the verification whose
        implications to act on.
      action: 'satisfy' | 'dismiss' — required.
      dismissed_reason: required when action='dismiss'.

    Resolves only currently-pending rows. Returns the count affected.
    """
    src_vid = payload.get("source_verification_id")
    action  = payload.get("action")
    reason  = (payload.get("dismissed_reason") or "").strip() or None
    if not src_vid:
        raise HTTPException(400, "source_verification_id is required")
    if action not in ("satisfy", "dismiss"):
        raise HTTPException(400, "action must be 'satisfy' or 'dismiss'")
    if action == "dismiss" and not reason:
        raise HTTPException(400,
            "dismissed_reason is required when action='dismiss'")

    new_status = "satisfied" if action == "satisfy" else "dismissed"
    pool = request.app.state.pg_pool
    conn = pool.getconn()
    try:
        set_session(conn, key_info.tenant_id)
        with conn.cursor() as cur:
            cur.execute(
                """
                UPDATE triggered_implication
                   SET status                 = %s,
                       resolved_at            = now(),
                       resolved_by            = %s::uuid,
                       dismissed_reason       = %s
                 WHERE tenant_id              = %s::uuid
                   AND source_verification_id = %s::uuid
                   AND status                 = 'pending'
                RETURNING id
                """,
                (new_status, key_info.user_id, reason,
                 key_info.tenant_id, src_vid),
            )
            rows = cur.fetchall()
        conn.commit()
    finally:
        pool.putconn(conn)
    return {
        "action":           action,
        "affected":         len(rows),
        "verification_id":  src_vid,
        "status":           new_status,
    }


@app.get("/api/v1/tenant/cascade-overrides", tags=["posture"])
async def list_cascade_overrides(
    request: Request,
    key_info: APIKeyInfo = Depends(require_api_key),
    include_inactive: bool = False,
):
    """List per-tenant cascade policy overrides."""
    pool = request.app.state.pg_pool
    conn = pool.getconn()
    try:
        set_session(conn, key_info.tenant_id)
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT id::text, override_kind, event_type,
                       target_requirement_id, reason, is_active,
                       created_at, updated_at
                  FROM tenant_cascade_override
                 WHERE tenant_id = %s::uuid
                """ + ("" if include_inactive else " AND is_active = TRUE") + """
                 ORDER BY created_at DESC
                """,
                (key_info.tenant_id,),
            )
            rows = cur.fetchall()
    finally:
        pool.putconn(conn)
    return {
        "items": [
            {
                "id":                     r[0],
                "override_kind":          r[1],
                "event_type":             r[2],
                "target_requirement_id":  r[3],
                "reason":                 r[4],
                "is_active":              r[5],
                "created_at":             r[6].isoformat() if r[6] else None,
                "updated_at":             r[7].isoformat() if r[7] else None,
            } for r in rows
        ],
        "count": len(rows),
    }


@app.put("/api/v1/tenant/cascade-overrides", tags=["posture"])
async def upsert_cascade_override(
    request:  Request,
    payload:  dict,
    key_info: APIKeyInfo = Depends(require_scope("posture")),
):
    """Create or update a cascade override. Required body fields:
      override_kind: 'mute_event' | 'mute_event_target'
      event_type:    e.g. 'phishing_threshold_crossed'
      target_requirement_id: required when kind=mute_event_target
      reason: auditor-grade explanation (required)
    """
    kind     = payload.get("override_kind")
    event_t  = payload.get("event_type") or ""
    target   = payload.get("target_requirement_id")
    reason   = (payload.get("reason") or "").strip()
    if kind not in ("mute_event", "mute_event_target"):
        raise HTTPException(
            400,
            "Please pick either 'Mute this event for one specific control' "
            "or 'Mute this event across every control it fires on'."
        )
    if not event_t:
        raise HTTPException(400, "Please pick the event you want to mute.")
    if kind == "mute_event_target" and not target:
        raise HTTPException(
            400,
            "This scope needs a specific target control (e.g. "
            "'ISO27001:2022:A.6.4') — please fill it in."
        )
    if kind == "mute_event" and target:
        raise HTTPException(
            400,
            "The 'mute across every control' scope doesn't take a target "
            "control — leave the target field empty or switch scope."
        )
    if not reason:
        raise HTTPException(
            400,
            "Please add an auditor-grade explanation of why this cascade "
            "doesn't apply to you."
        )
    # Validate event_type is known
    from enrichment.events.event_nodes import ALL_EVENTS
    if event_t not in {e.event_type for e in ALL_EVENTS}:
        raise HTTPException(
            400,
            f"We don't recognise the event '{event_t}'. Please pick one "
            f"from the dropdown."
        )

    pool = request.app.state.pg_pool
    conn = pool.getconn()
    try:
        set_session(conn, key_info.tenant_id)
        with conn.cursor() as cur:
            # Supersede any existing active row for this (kind, event, target)
            cur.execute(
                """
                UPDATE tenant_cascade_override
                   SET is_active  = FALSE,
                       updated_at = now(),
                       updated_by = %s::uuid
                 WHERE tenant_id     = %s::uuid
                   AND override_kind = %s
                   AND event_type    = %s
                   AND coalesce(target_requirement_id, '') = coalesce(%s, '')
                   AND is_active     = TRUE
                """,
                (key_info.user_id, key_info.tenant_id, kind, event_t, target),
            )
            cur.execute(
                """
                INSERT INTO tenant_cascade_override
                    (tenant_id, override_kind, event_type,
                     target_requirement_id, reason,
                     created_by, updated_by)
                VALUES (%s::uuid, %s, %s, %s, %s, %s::uuid, %s::uuid)
                RETURNING id::text
                """,
                (key_info.tenant_id, kind, event_t, target, reason,
                 key_info.user_id, key_info.user_id),
            )
            new_id = cur.fetchone()[0]
        conn.commit()
    finally:
        pool.putconn(conn)
    return {"id": new_id, "override_kind": kind, "event_type": event_t,
            "target_requirement_id": target, "reason": reason}


@app.delete("/api/v1/tenant/cascade-overrides/{override_id}", tags=["posture"])
async def delete_cascade_override(
    override_id: OverrideIdParam,
    request:  Request,
    key_info: APIKeyInfo = Depends(require_scope("posture")),
):
    """Soft-delete a cascade override (sets is_active=FALSE)."""
    pool = request.app.state.pg_pool
    conn = pool.getconn()
    try:
        set_session(conn, key_info.tenant_id)
        with conn.cursor() as cur:
            cur.execute(
                """
                UPDATE tenant_cascade_override
                   SET is_active  = FALSE,
                       updated_at = now(),
                       updated_by = %s::uuid
                 WHERE tenant_id = %s::uuid
                   AND id        = %s::uuid
                   AND is_active = TRUE
                RETURNING id::text
                """,
                (key_info.user_id, key_info.tenant_id, override_id),
            )
            updated = cur.fetchone()
        conn.commit()
    finally:
        pool.putconn(conn)
    if not updated:
        raise HTTPException(404, "override not found or already inactive")
    return {"id": updated[0], "is_active": False}


@app.get("/api/v1/tenant/cascade-suppressions", tags=["posture"])
async def list_cascade_suppressions(
    request: Request,
    key_info: APIKeyInfo = Depends(require_api_key),
    limit:   int = 50,
):
    """Audit log of EMITS_EVENT edges suppressed by applies_when
    evaluation. Auditor view of "cascades that were considered and
    consciously skipped because the condition didn't hold".
    """
    pool = request.app.state.pg_pool
    conn = pool.getconn()
    try:
        set_session(conn, key_info.tenant_id)
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT id::text,
                       source_verification_id::text,
                       source_event_type,
                       target_event_type,
                       applies_when,
                       evaluation_context,
                       cascade_path,
                       fired_at,
                       suppression_kind,
                       target_requirement_id
                  FROM cascade_suppression_log
                 WHERE tenant_id = %s::uuid
                 ORDER BY fired_at DESC
                 LIMIT %s
                """,
                (key_info.tenant_id, max(1, min(int(limit), 500))),
            )
            rows = cur.fetchall()
    finally:
        pool.putconn(conn)
    return {
        "items": [
            {
                "id":                     r[0],
                "source_verification_id": r[1],
                "source_event_type":      r[2],
                "target_event_type":      r[3],
                "applies_when":           r[4],
                "evaluation_context":     r[5],
                "cascade_path":           r[6],
                "fired_at":               r[7].isoformat() if r[7] else None,
                "suppression_kind":       r[8],
                "target_requirement_id":  r[9],
            } for r in rows
        ],
        "count": len(rows),
    }


@app.get("/api/v1/tenant/client-facts/changes", tags=["posture"])
async def list_client_fact_changes(
    request: Request,
    key_info: APIKeyInfo = Depends(require_api_key),
    limit:   int = 50,
):
    """Append-only audit log of cascade-fired ClientFact mutations.
    Returns newest first. Each row carries the source verification,
    operation, old/new value, and whether the change was applied
    (false for v1 'recompute' which is observational).
    """
    pool = request.app.state.pg_pool
    conn = pool.getconn()
    try:
        set_session(conn, key_info.tenant_id)
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT id::text, fact_id, operation,
                       old_value, new_value, applied,
                       source_verification_id::text, source_event_type,
                       rationale, fired_at
                  FROM client_fact_change_log
                 WHERE tenant_id = %s::uuid
                 ORDER BY fired_at DESC
                 LIMIT %s
                """,
                (key_info.tenant_id, max(1, min(int(limit), 500))),
            )
            rows = cur.fetchall()
    finally:
        pool.putconn(conn)
    return {
        "items": [
            {
                "id":                     r[0],
                "fact_id":                r[1],
                "operation":              r[2],
                "old_value":              r[3],
                "new_value":              r[4],
                "applied":                r[5],
                "source_verification_id": r[6],
                "source_event_type":      r[7],
                "rationale":              r[8],
                "fired_at":               r[9].isoformat() if r[9] else None,
            } for r in rows
        ],
        "count": len(rows),
    }


@app.post("/api/v1/tenant/expected-followups/sweep", tags=["posture"])
async def run_followup_sweep(
    request:  Request,
    key_info: APIKeyInfo = Depends(require_scope("posture")),
):
    """Mark pending followups whose window elapsed as 'overdue', and
    write triggered_implication rows on the controls whose MUSTs the
    missing event would have satisfied (S3f SLA-breach propagation).

    Returns counts: {overdue_marked, sla_implications_written}.
    """
    pool = request.app.state.pg_pool
    conn = pool.getconn()
    neo_drv = None
    try:
        set_session(conn, key_info.tenant_id)
        from rag.cascade.engine import sweep_overdue_followups
        from rag.posture_loader import _build_engine_neo4j_driver
        neo_drv = _build_engine_neo4j_driver()
        with conn.cursor() as cur:
            if neo_drv is None:
                result = sweep_overdue_followups(cur, tenant_id=key_info.tenant_id)
            else:
                with neo_drv.session() as neo_session:
                    result = sweep_overdue_followups(
                        cur, tenant_id=key_info.tenant_id,
                        neo_session=neo_session,
                    )
        conn.commit()
    finally:
        if neo_drv is not None:
            try: neo_drv.close()
            except Exception: pass
        pool.putconn(conn)
    return result


@app.get("/api/v1/tenant/cites/leaf/{leaf_id:path}/source/{system_id}/log", tags=["templates"])
async def list_verification_log(
    leaf_id: LeafIdParam,
    system_id: SystemIdParam,
    request:   Request,
    key_info:  APIKeyInfo = Depends(require_api_key),
    limit:     int = 20,
):
    """Audit trail of verifications for (leaf, source), newest first."""
    pool = request.app.state.pg_pool
    conn = pool.getconn()
    try:
        set_session(conn, key_info.tenant_id)
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT id::text, verified_at, verified_by::text,
                       changes_detected, note, sample_upload_id::text,
                       musts_covered_count
                  FROM external_evidence_verification_log
                 WHERE tenant_id = %s::uuid
                   AND leaf_id   = %s
                   AND system_id = %s::uuid
                 ORDER BY verified_at DESC
                 LIMIT %s
                """,
                (key_info.tenant_id, leaf_id, system_id, limit),
            )
            rows = cur.fetchall()
    finally:
        pool.putconn(conn)
    return {
        "leaf_id":   leaf_id,
        "system_id": system_id,
        "entries": [
            {
                "id":               r[0],
                "verified_at":      r[1].isoformat() if r[1] else None,
                "verified_by":      r[2],
                "changes_detected": r[3],
                "note":             r[4] or "",
                "sample_upload_id": r[5],
                "musts_covered":    r[6],
            }
            for r in rows
        ],
    }


@app.get("/api/v1/dashboard/cites/needs-verification", tags=["posture"])
async def dashboard_cites_needs_verification(
    request:  Request,
    key_info: APIKeyInfo = Depends(require_api_key),
    upcoming_window_days: int = 7,
):
    """Surface cites that need tenant attention, bucketed by urgency.

    Buckets (by `next_review_due` vs now):
      - red       — past grace (cite is STALE; engine no longer counts it).
                    Verify NOW.
      - yellow    — past next_review_due but within grace
                    (min(cadence × 10%, 30 days)). Engine still counts
                    them but they're amber on the panel.
      - upcoming  — due within `upcoming_window_days` (default 7).
                    Heads-up so the tenant can plan.

    Grouped by (leaf_id, system_id) so the dashboard card shows
    one row per (leaf × source) — same grouping as the per-leaf
    cited lane.
    """
    pool = request.app.state.pg_pool
    conn = pool.getconn()
    try:
        set_session(conn, key_info.tenant_id)
        with conn.cursor() as cur:
            # Single query — bucket-bydefault using SQL CASE for clarity.
            # Computes whether a cite is past grace (red), in grace
            # (yellow), or due soon (upcoming) per its own cadence_days.
            cur.execute(
                """
                WITH cite_state AS (
                  SELECT ees.leaf_id,
                         s.id::text         AS system_id,
                         s.system_name,
                         ees.must_id,
                         ees.last_verified_at,
                         ees.next_review_due,
                         ees.cadence_days,
                         -- grace in days: min(cadence x 10pct, 30); floor 1.
                         LEAST(GREATEST(ees.cadence_days / 10, 1), 30) AS grace_days,
                         CASE
                           WHEN ees.last_verified_at IS NULL THEN 'red'
                           WHEN now() > ees.last_verified_at
                                     + make_interval(days =>
                                         ees.cadence_days
                                       + LEAST(GREATEST(ees.cadence_days / 10, 1), 30))
                             THEN 'red'
                           WHEN now() > ees.next_review_due
                             THEN 'yellow'
                           WHEN ees.next_review_due <= now() + make_interval(days => %s)
                             THEN 'upcoming'
                           ELSE 'fresh'
                         END AS bucket
                    FROM external_evidence_source ees
                    JOIN tenant_external_system s ON s.id = ees.system_id
                   WHERE ees.tenant_id = %s::uuid
                     AND ees.is_active = TRUE
                     AND s.is_active   = TRUE
                )
                SELECT leaf_id, system_id, system_name, bucket,
                       count(*) AS must_count,
                       MAX(last_verified_at) AS last_verified_at,
                       MIN(next_review_due) AS next_review_due
                  FROM cite_state
                 WHERE bucket IN ('red', 'yellow', 'upcoming')
                 GROUP BY leaf_id, system_id, system_name, bucket
                 ORDER BY
                   CASE bucket WHEN 'red' THEN 0 WHEN 'yellow' THEN 1 ELSE 2 END,
                   MIN(next_review_due) NULLS FIRST,
                   leaf_id
                """,
                (upcoming_window_days, key_info.tenant_id),
            )
            rows = cur.fetchall()
    finally:
        pool.putconn(conn)

    buckets: dict[str, list[dict]] = {"red": [], "yellow": [], "upcoming": []}
    for r in rows:
        leaf_id, sys_id, sys_name, bucket, n, lv, ndd = r
        # Days overdue / until: positive when overdue, negative when upcoming.
        from datetime import datetime, timezone
        now = datetime.now(timezone.utc)
        if ndd:
            delta = (now - ndd).days
        else:
            delta = None
        from rag.id_types import leaf_control_ref, leaf_evidence_type
        buckets[bucket].append({
            "leaf_id":          leaf_id,
            "leaf_label":       leaf_evidence_type(leaf_id).replace("_", " "),
            "control_ref":      leaf_control_ref(leaf_id),
            "system_id":        sys_id,
            "system_name":      sys_name,
            "must_count":       n,
            "last_verified_at": lv.isoformat() if lv else None,
            "next_review_due":  ndd.isoformat() if ndd else None,
            "days_overdue":     delta,   # positive = overdue; negative = upcoming
        })
    return {
        "tenant_id":            key_info.tenant_id,
        "upcoming_window_days": upcoming_window_days,
        "counts": {
            "red":      len(buckets["red"]),
            "yellow":   len(buckets["yellow"]),
            "upcoming": len(buckets["upcoming"]),
        },
        "buckets": buckets,
    }


@app.get("/api/v1/templates/{leaf_id}", tags=["templates"])
async def get_template(
    leaf_id: LeafIdParam,
    request:  Request,
    key_info: APIKeyInfo = Depends(require_api_key),
    empty:    bool = False,
):
    """Render a leaf's template scaffold scoped to the calling tenant.

    Transformations applied at render time:
      - MUST sections corresponding to `tenant_must_overrides.applies =
        FALSE` for this tenant are stripped (e.g. Arion cloud-only:
        A.5.15:physical_rules removed from the template)
      - Identity placeholders <<TENANT_NAME>>, <<TENANT_SECTOR>>,
        <<TENANT_COUNTRY>>, <<TENANT_SHORT>>, <<TENANT_INDUSTRY>>,
        <<GENERATED_DATE>> substituted from the `tenants` row
      - <<TEXT>> fill-in placeholders and <<MUST item:X>> /
        <<SHOULD item:X>> markers are preserved — the markers bind the
        upload-side extractor when the tenant uploads back

    Returns JSON. For markdown-file download, use the sibling
    `/api/v1/templates/{leaf_id}/download` endpoint (Content-Disposition
    attachment).

    leaf_id format: `req:<control_ref>:<slug>` — colons in URL paths
    are accepted by FastAPI directly or via %3A encoding.

    By default, the rendered template is PREFILLED with the tenant's
    prior approved evidence per MUST (sources: templated > form >
    workbook > extracted > leaf_scan; xfw_bridge surfaced as footer).
    Pass `?empty=true` for a blank scaffold instead.
    """
    pool = request.app.state.pg_pool
    conn = pool.getconn()
    try:
        set_session(conn, key_info.tenant_id)
        from rag.templates.renderer import render_template
        rendered = render_template(
            conn, key_info.tenant_id, leaf_id,
            prefill = not empty,
        )
    finally:
        pool.putconn(conn)

    if rendered is None:
        raise HTTPException(
            status_code=404,
            detail=f"No template stored for leaf_id={leaf_id!r}. "
                   f"Run enrichment/templates/load_to_postgres.py to populate.",
        )

    from dataclasses import asdict
    return {
        "leaf_id":             rendered.leaf_id,
        "template_version":    rendered.template_version,
        "body_md":             rendered.body_md,
        "must_total":          rendered.must_total,
        "must_rendered":       rendered.must_rendered,
        "must_dropped_for_tenant": rendered.must_dropped,
        "placeholders_filled": rendered.placeholders_filled,
        "musts_prefilled":     rendered.musts_prefilled,
        "prefill_sources":     [asdict(s) for s in rendered.prefill_sources],
    }


def _is_write_cypher(cypher: str) -> bool:
    upper = " " + cypher.upper().replace("\n", " ") + " "
    return any(kw in upper for kw in _WRITE_KEYWORDS)


@app.post("/api/v1/admin/cypher", tags=["admin"])
async def admin_cypher(
    body:     CypherRequest,
    request:  Request,
    key_info: APIKeyInfo = Depends(require_api_key),
):
    """
    Read-only Cypher passthrough for the /graph debug explorer.
    Returns {nodes, edges, rows} — graph elements are deduped, rows
    preserves the per-record shape for tabular results.
    """
    expander = getattr(request.app.state, "expander", None)
    if not expander:
        raise HTTPException(503, "Neo4j not available")

    cypher = body.cypher.strip()
    if not cypher:
        raise HTTPException(400, "Empty cypher")
    if _is_write_cypher(cypher):
        raise HTTPException(400, "Read-only endpoint — write keywords detected")

    try:
        from neo4j.graph import Node, Relationship, Path
    except ImportError:
        raise HTTPException(500, "neo4j driver not available")

    driver       = expander._get_driver()
    nodes_by_id: dict = {}
    edges_by_id: dict = {}
    rows:        list = []
    limit             = max(1, min(int(body.limit or 500), 2000))

    def _capture_node(n):
        if n is None:
            return
        nodes_by_id[n.element_id] = {
            "id":     n.element_id,
            "labels": list(n.labels),
            "props":  dict(n),
        }

    def _capture_edge(r):
        if r is None:
            return
        _capture_node(r.start_node)
        _capture_node(r.end_node)
        edges_by_id[r.element_id] = {
            "id":     r.element_id,
            "source": r.start_node.element_id if r.start_node else None,
            "target": r.end_node.element_id   if r.end_node   else None,
            "type":   r.type,
            "props":  dict(r),
        }

    def _serialize(val):
        if isinstance(val, Node):
            _capture_node(val)
            return {"_kind": "node", "id": val.element_id}
        if isinstance(val, Relationship):
            _capture_edge(val)
            return {"_kind": "edge", "id": val.element_id}
        if isinstance(val, Path):
            for n in val.nodes:
                _capture_node(n)
            for r in val.relationships:
                _capture_edge(r)
            return {"_kind": "path", "length": len(val)}
        if isinstance(val, list):
            return [_serialize(v) for v in val]
        if isinstance(val, dict):
            return {k: _serialize(v) for k, v in val.items()}
        if hasattr(val, "isoformat"):
            try:
                return val.isoformat()
            except Exception:
                pass
        return val

    try:
        with driver.session() as session:
            result = session.run(cypher, body.params or {})
            for i, record in enumerate(result):
                if i >= limit:
                    break
                rows.append({k: _serialize(v) for k, v in record.items()})
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(400, f"Cypher error: {e}")

    return {
        "nodes":     list(nodes_by_id.values()),
        "edges":     list(edges_by_id.values()),
        "rows":      rows,
        "row_count": len(rows),
        "trace_id":  request.state.trace_id,
    }


@app.get("/graph", include_in_schema=False)
async def graph_page():
    """Serve the /graph debug explorer page."""
    return FileResponse(_static / "graph.html")


# =============================================================================
# Ship 4'.g: TENANT-FACING API-KEY MANAGEMENT
# =============================================================================
# Create / list / revoke external API keys via the Profile page.
# Keys are stored SHA256-hashed; the raw key value is returned ONCE
# at creation and can never be recovered from the server.
#
# Scoped under existing api_keys row for the tenant's admin user.
# Auth: any existing key on the tenant (via require_api_key), so
# the initial dev key can bootstrap new keys.

_EXTERNAL_SCOPES_ALLOWED = [
    "external:status",
    "external:query",
    "external:posture:read",
    "external:notifications:read",
    "external:evidence:read",
    "external:evidence:write",
    "external:cascade:read",
    "external:xfw:read",
    "external:risks:read",   # Ship 14'.c — risk register bulk + drill-in
]


class ApiKeyCreateRequest(BaseModel):
    name:       str = Field(..., min_length=1, max_length=200,
                            description="Human label for the key (e.g. `SIEM production`).")
    scopes:     list[str] = Field(..., min_length=1,
                                  description="One or more `external:*` scopes.")
    expires_in_days: Optional[int] = Field(None, ge=1, le=3650,
                                           description="Auto-expire after this many days. None = never.")


class ApiKeyCreated(BaseModel):
    id:          str
    key:         str = Field(..., description="Raw API key — copy now; not recoverable.")
    key_prefix:  str
    name:        str
    scopes:      list[str]
    created_at:  str
    expires_at:  Optional[str] = None


class ApiKeyRow(BaseModel):
    id:            str
    name:          str
    key_prefix:    str
    scopes:        list[str]
    is_active:     bool
    created_at:    str
    last_used_at:  Optional[str] = None
    expires_at:    Optional[str] = None


class ApiKeysList(BaseModel):
    tenant_id: str
    keys:      list[ApiKeyRow]


@app.post("/api/v1/tenant/api-keys",
          response_model = ApiKeyCreated,
          tags = ["api_keys"])
async def api_keys_create(
    body:     ApiKeyCreateRequest,
    request:  Request,
    key_info: APIKeyInfo = Depends(require_api_key),
):
    """Create a new API key. Returns the raw key value ONCE — the
    tenant must copy it now; the server stores only the SHA256 hash.
    """
    bad = [s for s in body.scopes if s not in _EXTERNAL_SCOPES_ALLOWED]
    if bad:
        raise HTTPException(
            status_code = 400,
            detail      = f"Unknown scope(s): {bad}. Allowed: {_EXTERNAL_SCOPES_ALLOWED}",
        )

    # Generate a raw key with an easily-recognisable prefix
    import secrets
    raw = "arion_ext_" + secrets.token_urlsafe(32)
    key_hash   = _hash_key(raw)
    key_prefix = raw[:12]

    expires_at = None
    if body.expires_in_days:
        import datetime as _dt
        expires_at = _dt.datetime.now(_dt.timezone.utc) + _dt.timedelta(days=body.expires_in_days)

    pool = request.app.state.pg_pool
    conn = pool.getconn()
    try:
        set_session(conn, key_info.tenant_id, key_info.user_id)
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO api_keys (
                    tenant_id, user_id, key_hash, key_prefix,
                    name, scopes, is_active, expires_at
                ) VALUES (
                    %s::uuid, %s::uuid, %s, %s,
                    %s, %s, TRUE, %s
                )
                RETURNING id::text, created_at
                """,
                (key_info.tenant_id, key_info.user_id, key_hash, key_prefix,
                 body.name, body.scopes, expires_at),
            )
            new_id, created_at = cur.fetchone()
        conn.commit()
    finally:
        pool.putconn(conn)

    return ApiKeyCreated(
        id         = new_id,
        key        = raw,
        key_prefix = key_prefix,
        name       = body.name,
        scopes     = body.scopes,
        created_at = created_at.isoformat() if created_at else "",
        expires_at = expires_at.isoformat() if expires_at else None,
    )


@app.get("/api/v1/tenant/api-keys",
         response_model = ApiKeysList,
         tags = ["api_keys"])
async def api_keys_list(
    request:  Request,
    key_info: APIKeyInfo = Depends(require_api_key),
):
    """List all API keys for the tenant. Raw key values are NEVER
    returned — only prefix + metadata."""
    pool = request.app.state.pg_pool
    conn = pool.getconn()
    try:
        set_session(conn, key_info.tenant_id, key_info.user_id)
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT id::text, name, key_prefix, scopes, is_active,
                       created_at, last_used_at, expires_at
                  FROM api_keys
                 WHERE tenant_id = %s::uuid
                 ORDER BY created_at DESC
                """,
                (key_info.tenant_id,),
            )
            rows = cur.fetchall()
    finally:
        pool.putconn(conn)

    return ApiKeysList(
        tenant_id = key_info.tenant_id,
        keys      = [
            ApiKeyRow(
                id           = r[0],
                name         = r[1] or "",
                key_prefix   = r[2] or "",
                scopes       = list(r[3] or []),
                is_active    = bool(r[4]),
                created_at   = r[5].isoformat() if r[5] else "",
                last_used_at = r[6].isoformat() if r[6] else None,
                expires_at   = r[7].isoformat() if r[7] else None,
            ) for r in rows
        ],
    )


@app.delete("/api/v1/tenant/api-keys/{key_id}",
            tags = ["api_keys"])
async def api_keys_revoke(
    key_id:   str,
    request:  Request,
    key_info: APIKeyInfo = Depends(require_api_key),
):
    """Revoke (soft-delete) an API key by setting is_active=false.
    The row stays in the DB for audit history."""
    # Prevent revoking the current auth key — would 401 the next
    # request. Refuse and require the tenant to use a different key.
    if key_id == key_info.key_id:
        raise HTTPException(
            status_code = 400,
            detail      = "Cannot revoke the key you are currently authenticated with. "
                          "Use a different key to revoke this one.",
        )
    pool = request.app.state.pg_pool
    conn = pool.getconn()
    try:
        set_session(conn, key_info.tenant_id, key_info.user_id)
        with conn.cursor() as cur:
            try:
                cur.execute(
                    """
                    UPDATE api_keys SET is_active = FALSE
                     WHERE tenant_id = %s::uuid AND id = %s::uuid
                     RETURNING id::text
                    """,
                    (key_info.tenant_id, key_id),
                )
                row = cur.fetchone()
            except Exception:
                raise HTTPException(
                    status_code = 400,
                    detail      = f"key_id must be a UUID; got: {key_id!r}",
                )
        conn.commit()
    finally:
        pool.putconn(conn)

    if row is None:
        raise HTTPException(
            status_code = 404,
            detail      = f"No key {key_id!r} for this tenant.",
        )
    return {"id": row[0], "is_active": False}


# =============================================================================
# Ship 4'.a: EXTERNAL API — /api/external/v1/*
# =============================================================================
# Scoped API keys + fixed-window rate limit + structured error
# contract. Registered LATE so all internal routes are defined first
# (order-independent in practice, but keeps grep-ability).
#
# See rag/external/__init__.py for the surface + rag/external/errors.py
# for the response contract.

from fastapi.exceptions import RequestValidationError as _RequestValidationError
from rag.external import external_router as _external_router
from rag.external.errors import (
    external_http_exception_handler         as _external_http_exception_handler,
    external_validation_exception_handler   as _external_validation_exception_handler,
)

app.include_router(_external_router)
app.add_exception_handler(HTTPException,             _external_http_exception_handler)
app.add_exception_handler(_RequestValidationError,   _external_validation_exception_handler)


# =============================================================================
# ENTRY POINT
# =============================================================================

if __name__ == "__main__":
    logger.info(f"Starting ArionComply API on port {API_PORT}")
    uvicorn.run(
        "api_server:app",
        host        = "0.0.0.0",
        port        = API_PORT,
        reload      = False,
        workers     = 1,       # single worker — LangGraph state is process-local
        log_level   = "info",
        access_log  = True,
    )
