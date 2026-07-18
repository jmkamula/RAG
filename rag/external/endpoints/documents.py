"""
Document upload + status + evidence endpoints —
    /api/external/v1/documents (POST + GET/{id})
    /api/external/v1/evidence (GET)

Ship 4'.e — external systems can push documents into the intake
pipeline and read back the evidence bound to specific controls.

Design notes:

  * POST /documents proxies to the same intake pipeline
    (rag/intake/doc_pipeline) as the internal `/api/v1/documents/
    upload`, reusing dedup + series/version handling + background
    processing. Response returns the upload_id immediately;
    processing runs async.

  * GET /documents/{id} returns extraction status + findings
    counts + timing. External clients poll until
    `extraction_status='completed'` (or 'failed').

  * GET /evidence?control_ref=X&standard_id=Y returns all
    document_findings bound to that control across all uploads,
    with per-finding excerpts + inference_source + confidence.
    Auditor-facing shape — "show me every artefact that touches
    A.5.18".

Scopes:
  * external:evidence:read  — GET /evidence + GET /documents/{id}
  * external:evidence:write — POST /documents
"""
from __future__ import annotations

import datetime as _dt
import hashlib as _hl
import logging
import uuid as _uuid
from pathlib import Path
from typing import Optional

from fastapi import (
    APIRouter, BackgroundTasks, Depends, File, Form, HTTPException,
    Query, Request, UploadFile,
)
from pydantic import BaseModel, Field

from rag.external.auth import external_key_with_scope

logger = logging.getLogger(__name__)

router = APIRouter()


# ── Response models ───────────────────────────────────────────────────

class UploadResponse(BaseModel):
    upload_id:          str
    filename:           str
    sha256:             str
    byte_size:          int
    extraction_status:  str = Field(..., description="`pending` immediately; poll GET /documents/{id} for progress.")
    canonical_upload_id: Optional[str] = Field(None, description="Set when the file is a duplicate of a prior upload. `extraction_status` will be `duplicate`.")


class DocumentStatus(BaseModel):
    upload_id:          str
    filename:           str
    uploaded_at:        Optional[str]
    processed_at:       Optional[str]
    extraction_status:  str
    extraction_path:    Optional[str] = Field(None, description="Which pipeline path handled this: `templated_markdown` / `workbook` / `llm_extract` / `duplicate` / `failed`.")
    findings_count:     Optional[int] = None
    doc_type:           Optional[str] = None
    standard_ids:       Optional[list[str]] = None
    error_message:      Optional[str] = None
    token_estimate:     Optional[int] = None
    sha256:             Optional[str] = None
    byte_size:          Optional[int] = None


class EvidenceItem(BaseModel):
    finding_id:         str
    upload_id:          str
    filename:           Optional[str]
    status:             str = Field(..., description="Finding status — e.g. `pending`, `confirmed`.")
    confidence:         str
    excerpt:            Optional[str] = None
    inference_source:   Optional[str] = Field(None, description="How this finding was produced: `templated` / `fingerprint_match` / `workbook` / `leaf_scan` / `extracted` / etc.")
    checklist_item_id:  Optional[str] = None
    extracted_at:       Optional[str] = None
    confirmed_at:       Optional[str] = None


class EvidenceResponse(BaseModel):
    tenant_id:    str
    control_ref:  str
    standard_id:  str
    evidence:     list[EvidenceItem]
    count:        int


# ── POST /documents ───────────────────────────────────────────────────

@router.post("/documents",
             response_model = UploadResponse,
             summary        = "Upload a document for evidence extraction")
async def upload_document(
    request:                Request,
    background_tasks:       BackgroundTasks,
    file:                   UploadFile          = File(..., description="Document to ingest. Supported: .pdf, .docx, .md, .xlsx, .txt."),
    declared_standard_id:   Optional[str]       = Form(None, description="Framework tag the tenant asserts (e.g. `ISO27001:2022`). Optional — extractor auto-detects."),
    declared_evidence_type: Optional[str]       = Form(None, description="Evidence-class tag (e.g. `policy`, `register`, `review_record`)."),
    key                     = Depends(external_key_with_scope("external:evidence:write")),
):
    """Upload a document via multipart/form-data. Same dedup +
    background-processing contract as the internal endpoint;
    returns `upload_id` immediately.

    Poll `GET /documents/{upload_id}` until
    `extraction_status='completed'` (or `'failed'`) for the results.
    """
    # Lazy import to avoid circular dep
    from api_server import (
        upload_document as _internal_upload,
        APIKeyInfo,
        SUPPORTED_EXTENSIONS,
        MAX_UPLOAD_MB,
        UPLOAD_DIR,
    )

    # Validate extension + size at this layer so we can raise via the
    # external error contract without touching the internal 4xx shape.
    suffix = Path(file.filename or "").suffix.lower()
    if suffix not in SUPPORTED_EXTENSIONS:
        raise HTTPException(
            status_code = 400,
            detail      = f"Unsupported file type: {suffix!r}. Supported: {sorted(SUPPORTED_EXTENSIONS)}",
        )
    contents = await file.read()
    size_mb  = len(contents) / (1024 * 1024)
    if size_mb > MAX_UPLOAD_MB:
        raise HTTPException(
            status_code = 400,
            detail      = f"File too large: {size_mb:.1f}MB. Max: {MAX_UPLOAD_MB}MB",
        )

    file_sha256 = _hl.sha256(contents).hexdigest()
    byte_size   = len(contents)

    # Dedup check — reuse the same predicate as the internal endpoint.
    pool = request.app.state.pg_pool
    conn = pool.getconn()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT set_config('app.tenant_id', %s, TRUE)", (key.tenant_id,))
            cur.execute("""
                SELECT id, filename
                  FROM document_uploads
                 WHERE tenant_id = %s::uuid
                   AND sha256    = %s
                   AND extraction_status NOT IN ('duplicate', 'failed')
                 LIMIT 1
            """, (key.tenant_id, file_sha256))
            existing = cur.fetchone()
    finally:
        pool.putconn(conn)

    if existing:
        existing_id, existing_name = existing
        return UploadResponse(
            upload_id           = str(existing_id),
            filename            = file.filename or existing_name,
            sha256              = file_sha256,
            byte_size           = byte_size,
            extraction_status   = "duplicate",
            canonical_upload_id = str(existing_id),
        )

    upload_id  = str(_uuid.uuid4())
    safe_name  = f"{upload_id}{suffix}"
    tenant_dir = UPLOAD_DIR / key.tenant_id
    tenant_dir.mkdir(parents=True, exist_ok=True)
    file_path  = tenant_dir / safe_name
    file_path.write_bytes(contents)

    # Register + background-process. Reuse the internal handler's
    # DB write logic by inlining the essential INSERT here — the
    # internal handler receives a FastAPI `UploadFile` and re-reads
    # the file, which would conflict with our already-consumed
    # contents. Just do the INSERT + schedule the background task
    # ourselves.
    from rag.intake.doc_pipeline import DocumentPipeline
    conn = pool.getconn()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT set_config('app.tenant_id', %s, TRUE)", (key.tenant_id,))

            # Clear stale failed/duplicate rows for this SHA
            cur.execute("""
                DELETE FROM document_uploads
                 WHERE tenant_id = %s::uuid
                   AND sha256    = %s
                   AND extraction_status IN ('failed', 'duplicate')
            """, (key.tenant_id, file_sha256))

            # Series/version tracking
            cur.execute("""
                SELECT series_id, MAX(version_no)
                  FROM document_uploads
                 WHERE tenant_id = %s::uuid
                   AND filename  = %s
                   AND extraction_status <> 'duplicate'
                   AND series_id IS NOT NULL
                 GROUP BY series_id
                 LIMIT 1
            """, (key.tenant_id, file.filename))
            row = cur.fetchone()
            if row:
                series_id  = str(row[0])
                version_no = int(row[1]) + 1
            else:
                series_id  = str(_uuid.uuid4())
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
                upload_id, key.tenant_id, file.filename or safe_name,
                str(file_path), key.user_id,
                file_sha256, byte_size,
                series_id, version_no,
            ))
        conn.commit()
    finally:
        pool.putconn(conn)

    # Background-process
    def _process_in_background():
        try:
            import os
            db_url    = os.getenv("DATABASE_URL")
            openai_key= os.getenv("OPENAI_API_KEY", "")
            pipeline = DocumentPipeline(db_url=db_url, api_key=openai_key)
            pipeline.run(
                str(file_path),
                tenant_id            = key.tenant_id,
                upload_id            = upload_id,
                original_filename    = file.filename or safe_name,
                user_id              = key.user_id,
                declared_standard_ids  = [declared_standard_id] if declared_standard_id else None,
                declared_evidence_type = declared_evidence_type,
            )
        except Exception as e:
            logger.error(f"external /documents pipeline failed for {upload_id}: {e}", exc_info=True)

    background_tasks.add_task(_process_in_background)

    return UploadResponse(
        upload_id         = upload_id,
        filename          = file.filename or safe_name,
        sha256            = file_sha256,
        byte_size         = byte_size,
        extraction_status = "pending",
    )


# ── GET /documents/{upload_id} ────────────────────────────────────────

@router.get("/documents/{upload_id}",
            response_model = DocumentStatus,
            summary        = "Status + metadata for one upload")
async def get_document_status(
    upload_id: str,
    request:   Request,
    key        = Depends(external_key_with_scope("external:evidence:read")),
):
    """Fetch the extraction status + findings count + metadata for
    an upload. Poll this while processing runs (typically completes
    in seconds; multi-MB documents may take minutes)."""
    pool = request.app.state.pg_pool
    conn = pool.getconn()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT set_config('app.tenant_id', %s, TRUE)", (key.tenant_id,))
            try:
                cur.execute("""
                    SELECT id::text, filename, uploaded_at, processed_at,
                           extraction_status, extraction_path,
                           findings_count, doc_type, standard_ids,
                           error_message, token_estimate, sha256, byte_size
                      FROM document_uploads
                     WHERE tenant_id = %s::uuid AND id = %s::uuid
                     LIMIT 1
                """, (key.tenant_id, upload_id))
                row = cur.fetchone()
            except Exception as e:
                logger.info("get_document_status bad id %r: %s", upload_id, e)
                raise HTTPException(
                    status_code = 400,
                    detail      = f"upload_id must be a UUID; got: {upload_id!r}",
                )
    finally:
        pool.putconn(conn)

    if row is None:
        raise HTTPException(
            status_code = 404,
            detail      = f"No upload {upload_id!r} for this tenant.",
        )

    (nid, filename, uploaded_at, processed_at, status, path,
     findings_ct, doc_type, standard_ids, error, tokens, sha, byte_size) = row

    return DocumentStatus(
        upload_id         = nid,
        filename          = filename or "",
        uploaded_at       = uploaded_at.isoformat()  if uploaded_at  else None,
        processed_at      = processed_at.isoformat() if processed_at else None,
        extraction_status = status,
        extraction_path   = path,
        findings_count    = int(findings_ct) if findings_ct is not None else None,
        doc_type          = doc_type,
        standard_ids      = list(standard_ids) if standard_ids else None,
        error_message     = error,
        token_estimate    = tokens,
        sha256            = sha,
        byte_size         = byte_size,
    )


# ── GET /evidence ─────────────────────────────────────────────────────

@router.get("/evidence",
            response_model = EvidenceResponse,
            summary        = "All evidence findings for a control")
async def get_evidence(
    request:     Request,
    key          = Depends(external_key_with_scope("external:evidence:read")),
    control_ref: str = Query(..., description="Control ref, e.g. `A.5.18`."),
    standard_id: str = Query(..., description="Framework id, e.g. `ISO27001:2022`. Required — refs like `Art.32` exist across multiple frameworks."),
):
    """Return every `document_findings` row bound to (standard_id,
    control_ref) for this tenant, joined with the upload's filename
    for provenance. Empty list when no evidence exists.

    Auditor-facing shape — "show me every artefact that touches
    this control."
    """
    pool = request.app.state.pg_pool
    conn = pool.getconn()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT set_config('app.tenant_id', %s, TRUE)", (key.tenant_id,))
            # document_findings.document_id can reference either
            # document_uploads (intake pipeline) or client_documents
            # (manual declaration / workbook import). LEFT-JOIN both
            # and COALESCE the filename so external clients get a
            # human label either way.
            cur.execute("""
                SELECT df.id::text,
                       df.document_id::text,
                       COALESCE(du.filename, cd.filename) AS filename,
                       df.status,
                       df.confidence,
                       LEFT(COALESCE(df.excerpt, ''), 500) AS excerpt,
                       df.inference_source,
                       df.checklist_item_id,
                       df.extracted_at,
                       df.confirmed_at
                  FROM document_findings df
                  LEFT JOIN document_uploads du
                    ON du.id = df.document_id
                   AND du.tenant_id = df.tenant_id
                  LEFT JOIN client_documents cd
                    ON cd.id = df.document_id
                   AND cd.tenant_id = df.tenant_id
                 WHERE df.tenant_id  = %s::uuid
                   AND df.control_ref = %s
                   AND df.standard_id = %s
                 ORDER BY df.extracted_at DESC NULLS LAST
            """, (key.tenant_id, control_ref, standard_id))
            rows = cur.fetchall()
    finally:
        pool.putconn(conn)

    items = [
        EvidenceItem(
            finding_id        = fid,
            upload_id         = did,
            filename          = fname,
            status            = fstatus,
            confidence        = conf,
            excerpt           = excerpt or None,
            inference_source  = infsrc,
            checklist_item_id = cid,
            extracted_at      = ext_at.isoformat()  if ext_at  else None,
            confirmed_at      = conf_at.isoformat() if conf_at else None,
        )
        for (fid, did, fname, fstatus, conf, excerpt,
             infsrc, cid, ext_at, conf_at) in rows
    ]

    return EvidenceResponse(
        tenant_id   = key.tenant_id,
        control_ref = control_ref,
        standard_id = standard_id,
        evidence    = items,
        count       = len(items),
    )
