"""
ArionComply — Posture Writer  (Phase 1 — clean rewrite)
Stage 4: Write DocumentFinding objects to the DB.

Design principles:
  1. Separation of concerns — each function does ONE thing
  2. Explicit transaction control — caller owns commit/rollback
  3. Savepoints per finding — one failure never poisons the batch
  4. No silent swallowing — exceptions are logged WITH type and re-raised
     only when they affect the whole batch, not individual findings
  5. Schema constants defined once at top — easy to update
  6. _ensure_client_document() runs BEFORE any transaction opens
  7. Confidence always stored as label (high/medium/low), never numeric

Phase 2 (next): add trace_id, request_trace_log entries, per-stage timing.

DB schema expectations (actual columns as of schema v8):
  document_findings:
    id, tenant_id, document_id (FK→client_documents), control_ref,
    standard_id, status (present/missing/partial), confidence (high/medium/low),
    excerpt, section_number, extracted_at, is_active, retention_class

  posture_controls:
    id, tenant_id, control_ref, standard_id, finding (Comply/NC/OFI/N/A),
    gap_description, confidence (high/medium/low), source, confirmation_status (draft),
    system_finding, system_proposed_at, is_active, retention_class

  client_documents:
    id, tenant_id, filename, document_status (registered/uploaded/processing/active...),
    is_active, is_metadata_only, retention_class

  document_uploads:
    id, tenant_id, extraction_status, findings_count, error_message,
    processed_at, updated_at
"""
from __future__ import annotations

import logging
import re
import uuid
from typing import Optional

from .models import DocumentFinding

logger = logging.getLogger(__name__)

# =============================================================================
# SCHEMA CONSTANTS  — update here if schema changes, nowhere else
# =============================================================================

# document_findings.status allowed values
_DF_STATUS_PRESENT = "present"
_DF_STATUS_MISSING  = "missing"
_DF_STATUS_PARTIAL  = "partial"

# posture_controls.confirmation_status for pipeline writes
_PC_STATUS_DRAFT = "draft"

# client_documents.document_status for auto-created records
_CD_STATUS_REGISTERED = "registered"

# Retention class applied by pipeline
_RETENTION_CLASS = "compliance"

# =============================================================================
# VALUE MAPPERS  — convert between pipeline vocabulary and DB constraints
# =============================================================================

# Pipeline finding → document_findings.status
_FINDING_TO_DF_STATUS: dict[str, str] = {
    "comply": _DF_STATUS_PRESENT,
    "nc":     _DF_STATUS_MISSING,
    "ofi":    _DF_STATUS_PARTIAL,
    "n/a":    _DF_STATUS_PRESENT,  # N/A = not applicable, not a gap
}

# Confidence label priority (higher = stronger signal)
_CONF_NUMERIC: dict[str, float] = {
    "high":   0.9,
    "medium": 0.65,
    "low":    0.4,
}

# Finding priority for aggregation
_FINDING_PRIORITY: dict[str, int] = {
    "NC": 3, "OFI": 2, "Comply": 1, "N/A": 0, "not_addressed": -1
}


def _map_df_status(finding: str) -> str:
    """Map pipeline finding value → document_findings.status constraint."""
    return _FINDING_TO_DF_STATUS.get((finding or "").lower(), _DF_STATUS_PARTIAL)


def _map_confidence(raw: str) -> str:
    """Normalise confidence to lowercase label. Defaults to 'medium'."""
    v = (raw or "medium").lower().strip()
    return v if v in _CONF_NUMERIC else "medium"


def _numeric_to_conf_label(value: float) -> str:
    """Convert averaged numeric confidence back to label for DB insert."""
    if value >= 0.8:
        return "high"
    if value >= 0.5:
        return "medium"
    return "low"


# =============================================================================
# PRE-FLIGHT: ensure client_documents record exists
# Called BEFORE the main transaction opens — uses autocommit-safe pattern.
# =============================================================================

_DOC_REF_PATTERN = re.compile(r'(DOC\d{3})', re.IGNORECASE)
_CD_STATUS_UPLOADED = "uploaded"


def _match_registered_document(
    tenant_id: str,
    filename:  str,
    cur,
) -> Optional[tuple[str, str | None]]:
    """
    Try to match `filename` to a pre-registered client_documents row
    via the agreed resolution order. Returns (doc_id, current_status)
    on hit, None on miss.

    Resolution order (mirrors tools/doc_uploader.py):
      1. external_ref via DOC-prefix in the filename (DOC006_*.pdf → DOC006)
      2. exact filename match
      3. fuzzy title-keyword match (words >3 chars from the filename
         intersect with words >3 chars in document_title)
    """
    # 1. DOC-prefix → external_ref
    m = _DOC_REF_PATTERN.search(filename or "")
    if m:
        ext_ref = m.group(1).upper()
        cur.execute(
            """
            SELECT id, document_status FROM client_documents
            WHERE tenant_id = %s
              AND external_ref = %s
              AND is_active = TRUE
            LIMIT 1
            """,
            (tenant_id, ext_ref),
        )
        row = cur.fetchone()
        if row:
            return (str(row[0]), row[1])

    # 2. Exact filename match on a *registered* row (has external_ref or
    # platform_ref). We deliberately skip orphan rows here so a prior
    # bad upload doesn't shadow the real registry entry.
    cur.execute(
        """
        SELECT id, document_status FROM client_documents
        WHERE tenant_id   = %s
          AND filename    = %s
          AND is_active   = TRUE
          AND (external_ref IS NOT NULL OR platform_ref IS NOT NULL)
        LIMIT 1
        """,
        (tenant_id, filename),
    )
    row = cur.fetchone()
    if row:
        return (str(row[0]), row[1])

    # 3. Fuzzy title-keyword match against registered rows only
    stem      = re.sub(r'\.[A-Za-z0-9]{1,5}$', '', filename or '')
    # Split on non-alphanumerics including '_' — Python \W keeps '_' as a
    # word char, which would leave "Access_Control_Policy" as one token.
    keywords  = {w.lower() for w in re.split(r'[\W_]+', stem) if len(w) > 3}
    if keywords:
        cur.execute(
            """
            SELECT id, document_title, document_status FROM client_documents
            WHERE tenant_id   = %s
              AND is_active   = TRUE
              AND document_title IS NOT NULL
              AND (external_ref IS NOT NULL OR platform_ref IS NOT NULL)
            """,
            (tenant_id,),
        )
        best, best_overlap = None, 0
        for row in cur.fetchall():
            title_words = {w.lower() for w in re.split(r'[\W_]+', row[1] or '') if len(w) > 3}
            overlap     = len(keywords & title_words)
            # Require at least 2 overlapping significant words to avoid
            # generic single-word matches (e.g. "policy")
            if overlap >= 2 and overlap > best_overlap:
                best, best_overlap = row, overlap
        if best:
            return (str(best[0]), best[2])

    # 4. Final fallback — match orphan row by filename so re-uploads
    # of the same file consolidate instead of creating more orphans.
    cur.execute(
        """
        SELECT id, document_status FROM client_documents
        WHERE tenant_id  = %s
          AND filename   = %s
          AND is_active  = TRUE
        LIMIT 1
        """,
        (tenant_id, filename),
    )
    row = cur.fetchone()
    if row:
        return (str(row[0]), row[1])

    return None


def _ensure_client_document(
    tenant_id: str,
    filename:  str,
    conn,
) -> str:
    """
    Return the client_documents.id for this upload + tenant.

    Resolution:
      - Try to match a pre-registered row (external_ref → filename → title).
      - On match: update filename + transition document_status to 'uploaded'
        so document_alerts no longer flags it as missing.
      - On miss: create a new row with a platform_ref allocated via
        PlatformRefGenerator (CD-{TENANT_SHORT}-{N}).

    Uses savepoints so a registry update / insert failure cannot poison
    the surrounding findings transaction.
    """
    with conn.cursor() as cur:
        # ── Registry match ────────────────────────────────────────────────
        match = _match_registered_document(tenant_id, filename, cur)
        if match:
            doc_id, current_status = match
            cur.execute("SAVEPOINT sp_cd_update")
            try:
                # Only transition registered→uploaded; never downgrade
                # an already-active doc back to uploaded.
                cur.execute(
                    """
                    UPDATE client_documents
                       SET filename         = COALESCE(NULLIF(filename, ''), %s),
                           document_status  = CASE
                               WHEN document_status = 'registered' THEN %s
                               ELSE document_status
                           END,
                           is_metadata_only = FALSE
                     WHERE id = %s AND tenant_id = %s
                    """,
                    (filename, _CD_STATUS_UPLOADED, doc_id, tenant_id),
                )
                cur.execute("RELEASE SAVEPOINT sp_cd_update")
                logger.info(
                    f"Linked upload to registered doc: {filename} → {doc_id} "
                    f"(was {current_status})"
                )
            except Exception as e:
                cur.execute("ROLLBACK TO SAVEPOINT sp_cd_update")
                cur.execute("RELEASE SAVEPOINT sp_cd_update")
                logger.warning(f"Could not update registered doc {doc_id}: {e}")
            return doc_id

        # ── No registry hit: create a fresh row with platform_ref ────────
        doc_id = str(uuid.uuid4())
        cur.execute("SAVEPOINT sp_client_doc")
        try:
            cur.execute(
                """
                INSERT INTO client_documents (
                    id, tenant_id, filename,
                    document_status, is_active, is_metadata_only, retention_class
                ) VALUES (%s, %s, %s, %s, TRUE, FALSE, %s)
                ON CONFLICT DO NOTHING
                """,
                (doc_id, tenant_id, filename,
                 _CD_STATUS_UPLOADED, _RETENTION_CLASS),
            )
            cur.execute("RELEASE SAVEPOINT sp_client_doc")
            logger.info(f"Created client_documents row: {filename} → {doc_id}")
        except Exception as e:
            cur.execute("ROLLBACK TO SAVEPOINT sp_client_doc")
            cur.execute("RELEASE SAVEPOINT sp_client_doc")
            logger.warning(f"Could not create client_documents for {filename}: {e}")
            # Concurrent insert race — try once more to find it
            cur.execute(
                "SELECT id FROM client_documents WHERE tenant_id=%s AND filename=%s LIMIT 1",
                (tenant_id, filename),
            )
            row = cur.fetchone()
            if row:
                return str(row[0])
            raise RuntimeError(f"Cannot resolve client_document for {filename}") from e

        # Allocate platform_ref for the new row (CD-ARN-NNNN)
        cur.execute("SAVEPOINT sp_cd_platform_ref")
        try:
            from db.ref_generator import PlatformRefGenerator
            cur.execute(
                "SELECT short_code FROM tenants WHERE id = %s",
                (tenant_id,),
            )
            short_row = cur.fetchone()
            short = (short_row[0] if short_row and short_row[0] else "TEN").upper()
            gen = PlatformRefGenerator(conn, tenant_id, tenant_short=short)
            gen.assign("client_documents", doc_id)
            cur.execute("RELEASE SAVEPOINT sp_cd_platform_ref")
        except Exception as e:
            cur.execute("ROLLBACK TO SAVEPOINT sp_cd_platform_ref")
            cur.execute("RELEASE SAVEPOINT sp_cd_platform_ref")
            logger.warning(f"platform_ref allocation skipped for {doc_id}: {e}")

        return doc_id


# =============================================================================
# STAGE 4A: write document_findings (one row per finding)
# Each finding gets its own SAVEPOINT — one failure never poisons the batch.
# =============================================================================

def _write_document_findings(
    findings:  list[DocumentFinding],
    tenant_id: str,
    doc_id:    str,           # client_documents.id
    conn,
) -> int:
    """
    Insert document_findings rows. Returns count of successfully written rows.
    Uses per-row savepoints — failures are logged and skipped, not raised.
    """
    written = 0
    with conn.cursor() as cur:
        for f in findings:
            sp = f"sp_df_{f.id.replace('-', '')[:16]}"
            cur.execute(f"SAVEPOINT {sp}")
            try:
                cur.execute(
                    """
                    INSERT INTO document_findings (
                        id, tenant_id, document_id,
                        control_ref, standard_id,
                        status, confidence, excerpt,
                        section_number, extracted_at,
                        is_active, retention_class
                    ) VALUES (
                        %s, %s, %s,
                        %s, %s,
                        %s, %s, %s,
                        %s, NOW(),
                        TRUE, %s
                    )
                    ON CONFLICT (id) DO NOTHING
                    """,
                    (
                        f.id, tenant_id, doc_id,
                        f.control_ref, f.standard_id,
                        _map_df_status(f.finding),
                        _map_confidence(f.confidence),
                        f.evidence_text[:500] if f.evidence_text else None,
                        f.section,
                        _RETENTION_CLASS,
                    ),
                )
                cur.execute(f"RELEASE SAVEPOINT {sp}")
                written += 1
                logger.debug(f"  ✓ document_finding: {f.control_ref} [{f.finding}]")
            except Exception as e:
                cur.execute(f"ROLLBACK TO SAVEPOINT {sp}")
                cur.execute(f"RELEASE SAVEPOINT {sp}")
                logger.warning(
                    f"  ✗ document_finding {f.control_ref}: "
                    f"{type(e).__name__}: {e}"
                )
    return written


# =============================================================================
# STAGE 4B: aggregate findings → posture_controls (one row per control)
# =============================================================================

def _write_posture_controls(
    groups:    dict[tuple, list[DocumentFinding]],
    tenant_id: str,
    conn,
) -> tuple[int, int]:
    """
    Upsert posture_controls from aggregated findings.
    Returns (posture_updated, posture_created).
    """
    updated = 0
    created = 0
    skipped = 0

    with conn.cursor() as cur:
        for (control_ref, standard_id), group in groups.items():
            agg = _aggregate_findings(group)
            if not agg:
                continue

            finding    = agg["finding"]
            gap_desc   = agg["gap_description"]
            confidence = _numeric_to_conf_label(agg["confidence"])

            sp = f"sp_pc_{control_ref.replace('.', '').replace(' ', '')}"
            cur.execute(f"SAVEPOINT {sp}")
            try:
                # Check for existing posture row
                cur.execute(
                    """
                    SELECT id, finding, source, confirmation_status
                    FROM posture_controls
                    WHERE tenant_id   = %s
                      AND control_ref = %s
                      AND standard_id = %s
                      AND is_active   = TRUE
                    LIMIT 1
                    """,
                    (tenant_id, control_ref, standard_id),
                )
                existing = cur.fetchone()

                if existing:
                    ex_id, ex_finding, ex_source, ex_status = existing

                    # Never overwrite confirmed findings
                    if ex_status == "confirmed" or ex_source in ("workbook", "assessor", "audit"):
                        logger.info(f"  ⊘ {control_ref} protected — source={ex_source} status={ex_status} ({ex_finding}) — skipped")
                        cur.execute(f"RELEASE SAVEPOINT {sp}")
                        skipped += 1
                        continue

                    # Preserve workbook assessment alongside document finding
                    if ex_source == "workbook" and ex_finding != finding:
                        gap_desc = (
                            f"[Document: {finding}] {gap_desc}\n"
                            f"[Workbook: {ex_finding}]"
                        )

                    cur.execute(
                        """
                        UPDATE posture_controls
                        SET finding             = %s,
                            gap_description     = %s,
                            confidence          = %s,
                            source              = 'document',
                            system_finding      = %s,
                            system_proposed_at  = NOW(),
                            confirmation_status = %s
                        WHERE id = %s
                        """,
                        (finding, gap_desc[:1000], confidence,
                         finding, _PC_STATUS_DRAFT, ex_id),
                    )
                    cur.execute(f"RELEASE SAVEPOINT {sp}")
                    updated += 1
                    logger.info(f"  ↻ posture_controls: {control_ref} → {finding} (was {ex_finding})")

                else:
                    posture_id = str(uuid.uuid4())
                    cur.execute(
                        """
                        INSERT INTO posture_controls (
                            id, tenant_id, control_ref, standard_id,
                            finding, gap_description, confidence,
                            source, confirmation_status,
                            system_finding, system_proposed_at,
                            is_active, retention_class
                        ) VALUES (
                            %s, %s, %s, %s,
                            %s, %s, %s,
                            'document', %s,
                            %s, NOW(),
                            TRUE, %s
                        )
                        """,
                        (
                            posture_id, tenant_id, control_ref, standard_id,
                            finding, gap_desc[:1000], confidence,
                            _PC_STATUS_DRAFT,
                            finding, _RETENTION_CLASS,
                        ),
                    )
                    cur.execute(f"RELEASE SAVEPOINT {sp}")
                    created += 1
                    logger.info(f"  + posture_controls: {control_ref} → {finding}")

            except Exception as e:
                cur.execute(f"ROLLBACK TO SAVEPOINT {sp}")
                cur.execute(f"RELEASE SAVEPOINT {sp}")
                logger.warning(
                    f"  ✗ posture_controls {control_ref}: "
                    f"{type(e).__name__}: {e}"
                )

    return updated, created, skipped


# =============================================================================
# PUBLIC API
# =============================================================================

def write_findings(
    findings:  list[DocumentFinding],
    tenant_id: str,
    upload_id: str,
    conn,
) -> dict:
    """
    Stage 4 entry point. Write all findings to document_findings and
    aggregate to posture_controls.

    Transaction discipline:
      - Caller opens the connection and calls commit()/rollback()
      - This function uses savepoints for per-row fault isolation
      - _ensure_client_document() runs inside savepoint before batch
      - update_upload_status() must be called separately by caller

    Returns summary dict.
    """
    if not findings:
        return {"written": 0, "posture_updated": 0, "posture_created": 0,
                "controls_assessed": []}

    # Stamp IDs
    for f in findings:
        f.tenant_id = tenant_id
        f.upload_id = upload_id
        if not f.id:
            f.id = str(uuid.uuid4())

    # ── Pre-flight: resolve client_documents.id ───────────────────────────
    # Use the filename from the first finding's document_name
    filename = findings[0].document_name if findings else "unknown"
    doc_id   = _ensure_client_document(tenant_id, filename, conn)
    logger.debug(f"client_documents.id = {doc_id}")

    # ── Stage 4A: document_findings ───────────────────────────────────────
    written = _write_document_findings(findings, tenant_id, doc_id, conn)

    # ── Stage 4B: posture_controls ────────────────────────────────────────
    groups: dict[tuple, list[DocumentFinding]] = {}
    for f in findings:
        if f.finding not in ("not_addressed", None):
            groups.setdefault((f.control_ref, f.standard_id), []).append(f)

    posture_updated, posture_created, posture_skipped = _write_posture_controls(groups, tenant_id, conn)

    summary = {
        "written":           written,
        "posture_updated":   posture_updated,
        "posture_created":   posture_created,
        "posture_skipped":   posture_skipped,
        "controls_assessed": [ref for ref, _ in groups.keys()],
    }
    logger.info(
        f"Stage 4 complete: {written} findings written, "
        f"{posture_updated} posture updated, {posture_created} posture created, "
        f"{posture_skipped} skipped (source guard)"
    )
    return summary


def update_upload_status(
    upload_id:      str,
    status:         str,
    findings_count: int,
    conn,
    error:          Optional[str] = None,
) -> None:
    """
    Update document_uploads tracking row.
    Called by the pipeline orchestrator in a finally block.
    Uses its own savepoint so a prior transaction error doesn't block this.
    """
    with conn.cursor() as cur:
        cur.execute("SAVEPOINT sp_upload_status")
        try:
            cur.execute(
                """
                UPDATE document_uploads
                SET extraction_status = %s,
                    findings_count    = %s,
                    processed_at      = NOW(),
                    error_message     = %s,
                    updated_at        = NOW()
                WHERE id = %s
                """,
                (status, findings_count, error, upload_id),
            )
            cur.execute("RELEASE SAVEPOINT sp_upload_status")
            logger.debug(f"document_uploads {upload_id} → {status}")
        except Exception as e:
            cur.execute("ROLLBACK TO SAVEPOINT sp_upload_status")
            cur.execute("RELEASE SAVEPOINT sp_upload_status")
            logger.warning(f"Could not update document_uploads {upload_id}: {e}")


# =============================================================================
# AGGREGATION  (pure function — no DB access)
# =============================================================================

def _aggregate_findings(findings: list[DocumentFinding]) -> Optional[dict]:
    """
    Aggregate multiple findings for the same control into one verdict.
    Priority: NC > OFI > Comply > N/A
    Returns None if all findings are not_addressed.
    """
    active = [
        f for f in findings
        if f.finding not in ("not_addressed", None)
    ]
    if not active:
        return None

    best = max(active, key=lambda f: _FINDING_PRIORITY.get(f.finding, 0))

    # Concatenate unique evidence, cap at 3 pieces
    seen:   set[str]  = set()
    parts:  list[str] = []
    for f in active:
        txt = (f.evidence_text or "").strip()
        if txt and txt not in seen:
            seen.add(txt)
            loc = f" [{f.section}]" if f.section else (
                  f" [p.{f.page_number}]" if f.page_number else "")
            parts.append(f"{txt}{loc}")
        if len(parts) >= 3:
            break

    conf_values = [_CONF_NUMERIC.get(_map_confidence(f.confidence), 0.65) for f in active]
    avg_conf    = sum(conf_values) / len(conf_values)

    return {
        "finding":         best.finding,
        "gap_description": " | ".join(parts),
        "confidence":      round(avg_conf, 2),
        "standard_id":     best.standard_id,
    }
