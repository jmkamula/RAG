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
from fastapi.responses import FileResponse, JSONResponse
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
    ".pdf", ".docx", ".doc", ".xlsx", ".xlsm", ".xls", ".txt", ".csv", ".md"
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
    # Original is preserved as evidence — auditors will ask for the file that
    # backs each finding, and re-parsing depends on it. Right-to-erasure goes
    # through DELETE /api/v1/documents/{id} (separate workstream).


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
                raise HTTPException(404, f"Upload not found: {upload_id}")

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
    series_id: str,
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
            raise HTTPException(404, f"Series not found: {series_id}")

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
    control_ref: str,
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
        raise HTTPException(400, "finding_ids is required")
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
        raise HTTPException(400, "finding_ids is required")
    if not body.rationale or not body.rationale.strip():
        raise HTTPException(400, "rationale is required for reject")
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
    control_ref: str,
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
    control_ref: str,
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
            raise HTTPException(404, f"No posture_controls row for {control_ref}")

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
    control_ref: str,
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
            raise HTTPException(404, f"No pending engine proposal for {control_ref}")
        if reason == "already_approved":
            raise HTTPException(409, f"Engine proposal for {control_ref} already approved")
        raise HTTPException(500, result.get("error", "approve failed"))
    finally:
        pool.putconn(conn)


@app.post("/api/v1/stage2/{control_ref}/reject", tags=["hitl"])
async def stage2_reject(
    control_ref: str,
    body:        Stage2RejectRequest,
    request:     Request,
    key_info:    APIKeyInfo = Depends(require_scope("hitl")),
):
    """Reject the engine verdict for one control. Sets status to 'rejected';
    posture_controls.finding is NOT touched."""
    if not body.rationale or not body.rationale.strip():
        raise HTTPException(400, "rationale is required for reject")
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
            raise HTTPException(404, f"No pending engine proposal for {control_ref}")
        raise HTTPException(500, result.get("error", "reject failed"))
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
            entry["groups"].setdefault(theme, []).append({
                "control_ref":              ref,
                "finding":                  finding,
                "confirmation_status":      conf,
                "gap_excerpt":              display_gap,
                "action_excerpt":           action or "",
                "engine_proposal_status":   eng_status,
                "engine_proposed_finding":  eng_finding,
                "engine_proposal_reason":   _humanize_reason(eng_reason or ""),
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

            frameworks.append({
                "standard_id":  std,
                "display_name": _STANDARD_DISPLAY.get(std, std),
                "summary":      entry["summary"],
                "groups":       groups_out,
            })

        # Stable display order: ISO 27001 first, then GDPR, then anything
        # else alphabetically. Tenants that only have GDPR see GDPR first.
        def _std_rank(s):
            if s.startswith("ISO27001"): return 0
            if s.startswith("ISO27701"): return 1
            if s.startswith("GDPR"):     return 2
            return 9
        frameworks.sort(key=lambda f: (_std_rank(f["standard_id"]), f["standard_id"]))

        return {
            "tenant_id":  key_info.tenant_id,
            "frameworks": frameworks,
            "trace_id":   request.state.trace_id,
        }
    finally:
        pool.putconn(conn)


@app.get("/api/v1/dashboard/control/{control_ref}/evidence", tags=["posture"])
async def dashboard_control_evidence(
    control_ref: str,
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
    halluc = row.get("dropped_hallucinated") or 0
    md_chars = row.get("markdown_chars") or 0
    para_chars = row.get("paragraph_chars") or 0
    llm_calls = row.get("llm_calls") or 0

    if candidates > 0 and findings == 0:
        return "red", f"0 findings from {candidates} scoped controls"
    if halluc > findings and findings >= 0:
        return "yellow", f"hallucinated > kept ({halluc} > {findings})"
    if candidates > 0 and findings * 5 < candidates:
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
                    itl.markdown_chars, itl.paragraph_chars,
                    itl.total_ms, itl.extraction_path
                FROM intake_trace_log itl
                LEFT JOIN document_uploads du ON du.id::text = itl.upload_id
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
