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
    Header,
    HTTPException,
    Request,
    UploadFile,
    status,
)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

# ── Path setup ────────────────────────────────────────────────────────────────
_ROOT = Path(__file__).parent
sys.path.insert(0, str(_ROOT))

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
    ".pdf", ".docx", ".doc", ".xlsx", ".xls", ".txt", ".csv", ".md"
}


# =============================================================================
# LIFESPAN — startup / shutdown
# =============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialise shared resources once at startup."""
    logger.info("ArionComply API starting up...")

    # ── Postgres connection pool ──────────────────────────────────────────────
    try:
        app.state.pg_pool = psycopg2.pool.ThreadedConnectionPool(
            minconn = 2,
            maxconn = 10,
            dsn     = DATABASE_URL,
        )
        logger.info("✓ Postgres pool ready")
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

# Serve static UI files
_static = Path("/data/arioncomply/static")
_static.mkdir(parents=True, exist_ok=True)
app.mount("/ui", StaticFiles(directory=str(_static), html=True), name="ui")

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
        raise HTTPException(503, "RAG pipeline not available")

    from rag.arion_state import make_initial_state
    from rag.tenant_context import TenantContextCache

    t_start    = time.time()
    trace_id   = request.state.trace_id
    # Prefix thread_id with tenant_id — prevents cross-tenant session collision
    session_id = body.session_id or f"api_{uuid.uuid4().hex[:8]}"
    # Prefix with tenant_id — prevents cross-tenant session collision
    thread_id  = f"{key_info.tenant_id[:8]}:{session_id}"
    thread_id  = f"{key_info.tenant_id[:8]}:{session_id}"

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
        result = await asyncio.get_event_loop().run_in_executor(
            None,
            lambda: graph.invoke(state, cfg),
        )

        answer     = result.get("answer_text", "") or result.get("answer", "")
        qtype      = result.get("question_type")
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
            answer     = answer,
            type       = qtype,
            refs       = refs if isinstance(refs, list) else [],
            trace_id   = trace_id,
            latency_ms = latency_ms,
        )
    except Exception as e:
        logger.error(f"Chat error: {e}", exc_info=True)
        raise HTTPException(500, f"Pipeline error: {e}")


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
        raise HTTPException(503, "RAG pipeline not available")

    t_start    = time.time()
    sid        = session_id or f"api_{uuid.uuid4().hex[:8]}"
    thread_id  = f"{key_info.tenant_id[:8]}:{sid}"

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

            answer_text = ""
            refs        = []
            qtype       = None

            async for event in graph.astream_events(state, cfg, version="v2"):
                kind = event.get("event", "")
                name = event.get("name", "")

                if kind == "on_chain_start" and name == "classify":
                    yield sse({"type": "status", "text": "Classifying intent..."})

                elif kind == "on_chain_start" and name == "retrieve":
                    yield sse({"type": "status", "text": "Retrieving compliance context..."})

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
                        if qtype != "clarification":
                            qtype = _out.get("question_type") or _out.get("answer_source")
                        # Strip selection artifacts
                        answer_text = answer_text.lstrip()
                        while answer_text.upper().startswith("SELECTED"):
                            nl = answer_text.find("\n")
                            answer_text = (answer_text[nl+1:] if nl != -1 else "").lstrip()
                        # Stream in chunks
                        for i in range(0, len(answer_text), 50):
                            yield sse({"type": "token", "text": answer_text[i:i+50]})
                            await asyncio.sleep(0)

            latency_ms = int((time.time() - t_start) * 1000)
            if hasattr(qtype, "value"):
                qtype = qtype.value
            yield sse({"type": "done", "refs": refs if isinstance(refs, list) else [],
                       "latency_ms": latency_ms, "answer_type": qtype})

        except Exception as e:
            logger.error(f"Stream error: {e}", exc_info=True)
            yield sse({"type": "error", "text": str(e)})


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

class DocumentStatus(BaseModel):
    upload_id:       str
    filename:        str
    status:          str
    doc_type:        Optional[str] = None
    standard_ids:    Optional[str] = None
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


def _run_pipeline(
    file_path:         str,
    tenant_id:         str,
    upload_id:         str,
    db_url:            str,
    api_key:           str,
    original_filename: Optional[str] = None,
):
    """Run document pipeline in background thread."""
    from rag.intake.doc_pipeline import DocumentPipeline
    pipeline = DocumentPipeline(
        db_url  = db_url,
        api_key = api_key,
        trace   = True,
    )
    result = pipeline.run(file_path, tenant_id, upload_id,
                          original_filename=original_filename)
    logger.info(
        f"Pipeline complete: {result.document_name} "
        f"status={result.status} findings={result.findings_count}"
    )
    # Clean up temp file
    try:
        Path(file_path).unlink(missing_ok=True)
    except Exception:
        pass


@app.post("/api/v1/documents/upload", tags=["documents"])
async def upload_document(
    request:          Request,
    background_tasks: BackgroundTasks,
    file:             UploadFile = File(...),
    key_info:         APIKeyInfo = Depends(require_scope("documents")),
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

    upload_id = str(uuid.uuid4())
    safe_name = f"{upload_id}{suffix}"
    file_path = UPLOAD_DIR / safe_name

    # Save to disk
    file_path.write_bytes(contents)

    # Register in document_uploads
    pool = request.app.state.pg_pool
    conn = pool.getconn()
    try:
        set_session(conn, key_info.tenant_id, key_info.user_id)
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO document_uploads (
                    id, tenant_id, filename, storage_path,
                    extraction_status, uploaded_by
                ) VALUES (%s, %s::uuid, %s, %s, 'pending', %s::uuid)
                ON CONFLICT (id) DO NOTHING
            """, (
                upload_id,
                key_info.tenant_id,
                file.filename,
                str(file_path),
                key_info.user_id,
            ))
        conn.commit()
    except Exception as e:
        conn.rollback()
        logger.warning(f"document_uploads insert failed: {e} — continuing")
    finally:
        pool.putconn(conn)

    # Queue background processing
    api_key = os.getenv("ANTHROPIC_API_KEY", "")
    background_tasks.add_task(
        _run_pipeline,
        file_path         = str(file_path),
        tenant_id         = key_info.tenant_id,
        upload_id         = upload_id,
        db_url            = DATABASE_URL,
        api_key           = api_key,
        original_filename = file.filename,
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
        "trace_id":   request.state.trace_id,
        "message":    "Processing started. Poll /status for progress.",
    }


@app.get(
    "/api/v1/documents/{upload_id}/status",
    response_model=DocumentStatus,
    tags=["documents"],
)
async def document_status(
    upload_id: str,
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
                (uid, fname, doc_type, std_ids, fw, pc, pu, ps,
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
                # Fall back to document_uploads table
                cur.execute("""
                    SELECT status, original_name, created_at::text
                    FROM document_uploads
                    WHERE id = %s AND tenant_id = %s::uuid
                """, (upload_id, key_info.tenant_id))
                row2 = cur.fetchone()
                if not row2:
                    raise HTTPException(404, f"Upload not found: {upload_id}")
                doc_status, fname, started_at = row2
                doc_type = std_ids = fw = pc = pu = ps = total_ms = None
                prop_written = prop_skipped = None
                xfw_tgts = None
                had_error = error_type = None

        return DocumentStatus(
            upload_id        = upload_id,
            filename         = fname or "",
            status           = doc_status,
            doc_type         = doc_type,
            standard_ids     = std_ids,
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
        )
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
    posture_id: str,
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
    posture_id: str,
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
                raise HTTPException(404, f"Posture control {posture_id} not found")
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
    proposal_id: str,
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
    proposal_id: str,
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


@app.get("/api/v1/posture/{control_ref}", tags=["posture"])
async def posture_control(
    control_ref: str,
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
