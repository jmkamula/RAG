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

import json
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


# Ship 6'.b: map `inference_source` → the auditor-facing
# `grounding_method` column added in schema_v81. See
# [[ship-6-prime-b-grounding-provenance-2026-07-18]].
_INFERENCE_TO_GROUNDING: dict[str, str] = {
    "extracted":         "extractor_verbatim",   # LLM + verbatim-substring check (extractor.py:_evidence_grounded)
    "templated":         "template",             # <<MUST item:X>> markers — deterministic
    "workbook":          "workbook",             # workbook YAML row-matcher
    "fingerprint_match": "fingerprint",          # 2-of-N corroboration gate
    "leaf_scan":         "leaf_scan",            # back-bind to unmet MUSTs (HITL-only)
    "form":              "form",                 # retired 2026-07-04
    "xfw_bridge":        "unknown",              # xfw is not evidence itself
}


def _grounding_method(inference_source: str) -> str:
    """Return the canonical grounding_method for a given
    inference_source. Defaults to 'unknown' — future new sources
    should add themselves to _INFERENCE_TO_GROUNDING explicitly
    rather than fall through."""
    return _INFERENCE_TO_GROUNDING.get(
        (inference_source or "extracted").lower(),
        "unknown",
    )


def _numeric_to_conf_label(value: float) -> str:
    """Convert averaged numeric confidence back to label for DB insert."""
    if value >= 0.8:
        return "high"
    if value >= 0.5:
        return "medium"
    return "low"


# =============================================================================
# Ship 42'.b — evidence_group_id computation for per-doc dedup at write time.
#
# Rows sharing the same (document_id, control_ref, normalized_excerpt) get
# the same evidence_group_id. Surface layers (Stage-1, advisory, evidence
# package, chat) filter DISTINCT ON to display 1 row per group. Engine
# per-MUST recognition (leaf_evaluators._fetch_recognised_items) reads
# checklist_item_id = ANY(...) unchanged and sees all N rows.
#
# See docs/memory/ship_42_prime_a_dedup_design_2026_07_26.md.
# =============================================================================

import hashlib

_EXCERPT_ESCAPE_RE = re.compile(r"\\([\\\-\(\)\.])")
_EXCERPT_WS_RE = re.compile(r"\s+")


def _normalize_excerpt(text: Optional[str]) -> str:
    """Whitespace-collapse, case-fold, strip common markdown escapes.
    Bounded at 500 chars for safety (matches document_findings.excerpt cap)."""
    if not text:
        return ""
    t = _EXCERPT_ESCAPE_RE.sub(r"\1", text)
    t = _EXCERPT_WS_RE.sub(" ", t).strip().lower()
    return t[:500]


def _evidence_group_id(document_id: str, control_ref: str,
                       excerpt: Optional[str]) -> Optional[str]:
    """Return 16-char sha1 prefix of (document_id, control_ref,
    normalized_excerpt). Returns None if excerpt is empty — engine still
    sees the row, but surface layers won't collapse groupless rows."""
    normalized = _normalize_excerpt(excerpt)
    if not normalized:
        return None
    key = f"{document_id}|{control_ref}|{normalized}"
    return hashlib.sha1(key.encode()).hexdigest()[:16]


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

    # Step 3 (fuzzy title-keyword overlap) REMOVED 2026-06-12.
    # The "≥ 2 overlapping significant words" rule was unprincipled
    # and caused real-world conflations — e.g. "ISMS Change Management
    # Process.docx" and "ISMS Policy and Process Documents
    # Acknowledgment.xlsx" matched on {isms, process}, two different
    # docs got tied to the same client_documents row, and the engine
    # silently mis-bound evidence_type. Replaced by deterministic
    # rules only: explicit DOC-prefix (step 1), exact filename match
    # against registered rows (step 2), and orphan-filename fallback
    # (step 4). Tenants who want consolidation across renames use
    # external_ref / platform_ref or rename the upload to match the
    # registered title exactly.

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
                       SET filename         = CASE
                               -- Registry seeds DOC###_Title.pdf placeholders that lie
                               -- about the actual file extension. When matched, replace
                               -- the placeholder with the upload's real filename.
                               WHEN filename ~ '^DOC[0-9]+_.*\\.pdf$' THEN %s
                               ELSE COALESCE(NULLIF(filename, ''), %s)
                           END,
                           document_status  = CASE
                               WHEN document_status = 'registered' THEN %s
                               ELSE document_status
                           END,
                           is_metadata_only = FALSE
                     WHERE id = %s AND tenant_id = %s
                    """,
                    (filename, filename, _CD_STATUS_UPLOADED, doc_id, tenant_id),
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
    findings:    list[DocumentFinding],
    tenant_id:   str,
    doc_id:      str,           # client_documents.id
    conn,
    *,
    uploaded_by:       Optional[str]       = None,
    target_controls:   Optional[set[str]]  = None,
    semantic_controls: Optional[set[str]]  = None,
    explicit_refs:     Optional[set[str]]  = None,
    llm_extracted:     Optional[set[str]]  = None,
) -> int:
    """
    Insert document_findings rows. Returns count of successfully written rows.
    Uses per-row savepoints — failures are logged and skipped, not raised.
    """
    written = 0

    # Signal-fusion Wave 3 (2026-07-09): N-of-M consensus for fingerprint_match
    # auto-approval. Four independent corroboration signals — each a
    # different view of "is this control in scope for this doc?":
    #   1. target_controls   — filename+topic-token match via doc_mappings
    #   2. semantic_controls — body-content semantic match via musts_arioncomply
    #                          top-K embedding lookup
    #   3. explicit_refs     — doc self-cites the control ref (regex extract)
    #   4. llm_extracted     — LLM produced any 'extracted' finding on the
    #                          control in this batch
    # Rule: ≥2 of the AVAILABLE signals must agree. When 0-1 signals are
    # available (legacy caller, all sources returned None), the rule
    # degrades to "auto-approve" so the previous behavior is preserved as
    # the floor — Wave 3 can only make the gate STRICTER than before,
    # never looser. Wave 1 was doc_mappings-only; Wave 2 added semantic
    # as EITHER-OR; Wave 3 tightens to ≥2 with LLM + explicit as
    # additional inputs.

    with conn.cursor() as cur:
        # Supersede prior extract batches for this document before writing the
        # new one. Without this, re-extracts pile up duplicate findings (see
        # multipath_data_cleanup_2026_06_23 retrospective). Gated on findings
        # being non-empty so a 0-finding extract doesn't wipe prior evidence.
        # Covers both 'extracted' (LLM path) and 'templated' (no-LLM
        # fast-path) — re-extracts may flip between the two paths.
        if findings:
            cur.execute(
                """
                UPDATE document_findings
                SET is_active = FALSE,
                    review_status = 'rejected',
                    rejection_reason = 'superseded_by_extract_batch:' || NOW()::text,
                    reviewed_at = COALESCE(reviewed_at, now())
                WHERE document_id = %s
                  AND inference_source IN ('extracted', 'templated')
                  AND is_active = TRUE
                """,
                (doc_id,),
            )
        for f in findings:
            sp = f"sp_df_{f.id.replace('-', '')[:16]}"
            cur.execute(f"SAVEPOINT {sp}")
            try:
                # inference_source: honour the field on DocumentFinding when
                # set (templated upload fast-path sets 'templated'); otherwise
                # rely on the DB column default ('extracted').
                src = getattr(f, "inference_source", None)

                # Auto-approve discipline (signal-fusion Wave 1, 2026-07-09):
                #   'templated'        — tenant authored via <<MUST X>>
                #                        markers. Zero inference uncertainty.
                #                        Always auto-approve.
                #   'fingerprint_match' — auto-approve ONLY when the LLM
                #                        ('extracted') path ALSO landed a
                #                        finding on the same control_ref
                #                        in this batch. Two independent
                #                        signals must agree the doc is about
                #                        this control. Single-signal
                #                        fingerprint hits land pending
                #                        Stage-1 so loose-token false-
                #                        positives don't slip through.
                #   Everything else    — pending Stage-1.
                if src == "templated":
                    review_status = "approved"
                    confirmed_by  = uploaded_by
                elif src == "fingerprint_match":
                    # Wave 3 (N-of-M) + Wave 4a (precision-weighted).
                    # Signal roles differ:
                    #   BASE signals (target_controls, semantic_controls,
                    #     explicit_refs) — each has an INDEPENDENT view of
                    #     "is this control in scope?" on the whole doc.
                    #     Their absence is meaningful (the source ran and
                    #     didn't see this control), so they count toward
                    #     BOTH `available` and `agreeing`.
                    #   BONUS signal (llm_extracted) — the LLM is often
                    #     specifically EXCLUDED from fingerprint-covered
                    #     leaves, so LLM's silence on a fingerprint-hit
                    #     control isn't a signal at all. Only its
                    #     AGREEMENT counts (as an extra vote). Its
                    #     absence never tightens the rule.
                    _agreeing_names: list[str] = []
                    base_available = 0
                    base_agrees    = 0
                    for name, scope_set in (
                        ("target_controls",   target_controls),
                        ("semantic_controls", semantic_controls),
                        ("explicit_refs",     explicit_refs),
                    ):
                        if not scope_set:
                            continue
                        base_available += 1
                        if f.control_ref in scope_set:
                            base_agrees += 1
                            _agreeing_names.append(name)
                    # LLM bonus — adds to agrees only when it fires on
                    # the same control. Doesn't push base_available.
                    if llm_extracted and f.control_ref in llm_extracted:
                        _agreeing_names.append("llm_extracted")
                    # Wave 4a — precision-weighted agreement (last-90d
                    # per-signal approve/reject rate on THIS tenant +
                    # framework). Cold-start (< 5 samples) → 1.0
                    # neutral (Wave 3 behavior).
                    from rag.intake.signal_precision import compute_signal_precision
                    precisions = compute_signal_precision(
                        conn, tenant_id, standard_id=f.standard_id, window_days=90,
                    )
                    weighted_agreement = sum(
                        precisions.get(n, 1.0) for n in _agreeing_names
                    )
                    if base_available == 0:
                        auto_approve = True   # legacy floor
                    elif base_available == 1:
                        auto_approve = weighted_agreement >= 1.0
                    else:
                        auto_approve = weighted_agreement >= 2.0
                    f.corroborating_signals = _agreeing_names
                    if auto_approve:
                        review_status = "approved"
                        confirmed_by  = uploaded_by
                    else:
                        review_status = "pending"
                        confirmed_by  = None
                else:
                    review_status = "pending"
                    confirmed_by  = None

                # Ship 42'.b — evidence_group_id stamp for per-doc dedup.
                # Same excerpt on same control gets same group_id; surface
                # layers collapse to 1 row per group.
                evidence_excerpt = (
                    f.evidence_text[:500] if f.evidence_text else None
                )
                group_id = _evidence_group_id(
                    doc_id, f.control_ref, evidence_excerpt,
                )

                if src:
                    cur.execute(
                        """
                        INSERT INTO document_findings (
                            id, tenant_id, document_id,
                            control_ref, standard_id, checklist_item_id,
                            status, confidence, excerpt,
                            section_number, extracted_at,
                            is_active, retention_class,
                            inference_source, grounding_method,
                            review_status, confirmed_by, confirmed_at,
                            corroborating_signals, evidence_group_id
                        ) VALUES (
                            %s, %s, %s,
                            %s, %s, %s,
                            %s, %s, %s,
                            %s, NOW(),
                            TRUE, %s,
                            %s, %s,
                            %s, %s::uuid,
                            CASE WHEN %s = 'approved' THEN NOW() ELSE NULL END,
                            %s, %s
                        )
                        ON CONFLICT (id) DO NOTHING
                        """,
                        (
                            f.id, tenant_id, doc_id,
                            f.control_ref, f.standard_id, f.checklist_item_id,
                            _map_df_status(f.finding),
                            _map_confidence(f.confidence),
                            evidence_excerpt,
                            f.section,
                            _RETENTION_CLASS,
                            src, _grounding_method(src),
                            review_status, confirmed_by, review_status,
                            getattr(f, "corroborating_signals", None) or [],
                            group_id,
                        ),
                    )
                else:
                    # No inference_source override → DB default 'extracted',
                    # default review_status 'pending'. Grounding method is
                    # 'extractor_verbatim' because the LLM path is the only
                    # writer that leaves inference_source unset.
                    cur.execute(
                        """
                        INSERT INTO document_findings (
                            id, tenant_id, document_id,
                            control_ref, standard_id, checklist_item_id,
                            status, confidence, excerpt,
                            section_number, extracted_at,
                            is_active, retention_class,
                            grounding_method, evidence_group_id
                        ) VALUES (
                            %s, %s, %s,
                            %s, %s, %s,
                            %s, %s, %s,
                            %s, NOW(),
                            TRUE, %s,
                            'extractor_verbatim', %s
                        )
                        ON CONFLICT (id) DO NOTHING
                        """,
                        (
                            f.id, tenant_id, doc_id,
                            f.control_ref, f.standard_id, f.checklist_item_id,
                            _map_df_status(f.finding),
                            _map_confidence(f.confidence),
                            evidence_excerpt,
                            f.section,
                            _RETENTION_CLASS,
                            group_id,
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

def _log_status_change(
    cur,
    *,
    tenant_id:         str,
    posture_id:        str,
    control_ref:       str,
    standard_id:       str,
    status_before:     Optional[str],
    status_after:      str,
    confidence:        Optional[str],
    evidence:          Optional[str],
    source_upload_id:  Optional[str],
    change_kind:       str = "extraction",
) -> None:
    """
    Append one row to posture_status_log (schema_v21 + v24).

    Called inside the per-control savepoint, so a logging failure rolls back
    the parent posture_controls write too — keeps the audit trail and the
    state in sync. Caller is responsible for short-circuiting when
    status_before == status_after (we don't log non-transitions).

    change_kind tags the audit row per schema_v24:
      extraction      — document-intake proposed/promoted finding
      engine          — fulfilment engine proposed/promoted finding
      assessor        — manual override
      acknowledgement — gap acknowledgement
    """
    cur.execute(
        """
        INSERT INTO posture_status_log (
            tenant_id, posture_id, control_ref, standard_id,
            status_before, status_after,
            source, source_upload_id,
            evidence_citation, confidence,
            change_kind
        ) VALUES (
            %s::uuid, %s::uuid, %s, %s,
            %s, %s,
            'document', %s::uuid,
            %s, %s,
            %s
        )
        """,
        (
            tenant_id, posture_id, control_ref, standard_id,
            status_before, status_after,
            source_upload_id,
            (evidence or "")[:500] or None,
            confidence,
            change_kind,
        ),
    )

    # Ship 3'.c: fire a tenant_notification when a live posture
    # transitions INTO NC from a non-NC state. Dedup via the
    # partial unique index in tenant_notification (unread rows
    # keyed by tenant + kind + related_entity_id + related_control_ref).
    if status_after == "NC" and status_before != "NC":
        try:
            from rag.cascade.notify import notify as _notify
            _notify(
                cur,
                tenant_id           = tenant_id,
                kind                = "nc_surfaced",
                title               = f"New non-conformity on {control_ref}",
                body                = (
                    f"A non-conformity was identified on "
                    f"{control_ref} (was: {status_before or 'unassessed'}). "
                    f"Review the finding + evidence in the queue and "
                    f"decide on remediation."
                ),
                severity            = "high",
                related_entity_kind = "posture_control",
                related_entity_id   = posture_id,
                related_control_ref = control_ref,
                related_event_type  = "nc_surfaced",
            )
        except Exception as _e:
            # Never let a notification failure break the audit log
            # write. Best-effort by contract.
            import logging as _lg
            _lg.getLogger("rag.intake.posture_writer").debug(
                "nc_surfaced notify skipped: %s", _e,
            )

    # Ship 3'.i: mirror of the nc_surfaced hook — fire a positive-news
    # notification when a live posture transitions INTO Comply from
    # any non-Comply state (NC, OFI, or unassessed). Severity 'low'
    # by default — this is auditor-neutral good news, not something
    # the tenant needs to act on. Skips when status_before was already
    # Comply (idempotent re-writes) or when the transition is from
    # 'Not assessed' straight to Comply on a fresh doc upload (still
    # notify — that IS remediation progress worth surfacing).
    if status_after == "Comply" and status_before != "Comply":
        try:
            from rag.cascade.notify import notify as _notify
            _from = status_before or "unassessed"
            _notify(
                cur,
                tenant_id           = tenant_id,
                kind                = "posture_flip_to_comply",
                title               = f"{control_ref} is now Comply",
                body                = (
                    f"Live finding for {control_ref} moved to Comply "
                    f"(was: {_from}). Remediation evidence is in place."
                ),
                severity            = "low",
                related_entity_kind = "posture_control",
                related_entity_id   = posture_id,
                related_control_ref = control_ref,
                related_event_type  = "posture_flip_to_comply",
            )
        except Exception as _e:
            import logging as _lg
            _lg.getLogger("rag.intake.posture_writer").debug(
                "posture_flip_to_comply notify skipped: %s", _e,
            )


def _write_posture_controls(
    groups:    dict[tuple, list[DocumentFinding]],
    tenant_id: str,
    conn,
    upload_id: Optional[str] = None,
) -> tuple[int, int, int]:
    """
    Stage extraction proposals into posture_controls.system_finding. The live
    posture_controls.finding is *not* touched — Stage-1 batch approval
    ([[hitl-two-stage-approval-design]]) promotes the proposal to the live
    finding once the user approves the extraction's per-finding list.

    Append a posture_status_log row on every create or system_finding change
    (schema_v21 + v24, change_kind='extraction').

    Source guard: extracted findings never overwrite assessor/workbook/audit
    rows, nor any row in a *_confirmed state (confirmed, document_confirmed,
    engine_confirmed) — the user has spoken, so a fresh extraction does not
    silently retract that decision. Re-proposal on a confirmed row arrives
    through the digest-driven invalidation path (separate workstream), not
    through the writer.

    Returns (posture_updated, posture_created, posture_skipped).
    """
    updated = 0
    created = 0
    skipped = 0

    from rag.framework_refs import normalize_control_ref

    # All *_confirmed states must be preserved by an extraction sweep.
    # Listed explicitly so a new confirmation state can't be added without
    # a deliberate review of this guard.
    _PROTECTED_STATES = ("confirmed", "document_confirmed", "engine_confirmed")
    _PROTECTED_SOURCES = ("workbook", "assessor", "audit")

    with conn.cursor() as cur:
        for (raw_ref, standard_id), group in groups.items():
            agg = _aggregate_findings(group)
            if not agg:
                continue

            # Canonical form: ISO 27001 Annex A always uses 'A.' prefix.
            # Prevents the "5.18 vs A.5.18" duplicate-row bug.
            control_ref = normalize_control_ref(raw_ref, standard_id) or raw_ref

            finding    = agg["finding"]
            gap_desc   = agg["gap_description"]
            confidence = _numeric_to_conf_label(agg["confidence"])

            sp = f"sp_pc_{control_ref.replace('.', '').replace(' ', '')}"
            cur.execute(f"SAVEPOINT {sp}")
            try:
                cur.execute(
                    """
                    SELECT id, finding, source, confirmation_status, system_finding
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
                    ex_id, ex_finding, ex_source, ex_status, ex_system = existing

                    if ex_status in _PROTECTED_STATES or ex_source in _PROTECTED_SOURCES:
                        logger.info(
                            f"  ⊘ {control_ref} protected — "
                            f"source={ex_source} status={ex_status} "
                            f"({ex_finding}) — skipped"
                        )
                        cur.execute(f"RELEASE SAVEPOINT {sp}")
                        skipped += 1
                        continue

                    # Stage proposal only — live `finding` stays untouched.
                    # `source='document'` is informational on the proposal
                    # track; the active assessment lineage is set on
                    # Stage-1 promotion (commit 3).
                    cur.execute(
                        """
                        UPDATE posture_controls
                        SET gap_description     = %s,
                            confidence          = %s,
                            source              = 'document',
                            system_finding      = %s,
                            system_proposed_at  = NOW()
                        WHERE id = %s
                        """,
                        (gap_desc[:1000], confidence, finding, ex_id),
                    )
                    if ex_system != finding:
                        _log_status_change(
                            cur,
                            tenant_id        = tenant_id,
                            posture_id       = ex_id,
                            control_ref      = control_ref,
                            standard_id      = standard_id,
                            status_before    = ex_system,
                            status_after     = finding,
                            confidence       = confidence,
                            evidence         = gap_desc,
                            source_upload_id = upload_id,
                            change_kind      = "extraction",
                        )
                    cur.execute(f"RELEASE SAVEPOINT {sp}")
                    updated += 1
                    logger.info(
                        f"  ↻ posture_controls: {control_ref} "
                        f"system_finding={finding} (live={ex_finding}, awaiting Stage-1)"
                    )

                else:
                    # New control: live `finding` stays at the schema default
                    # 'Not assessed'. The extraction proposal lives in
                    # system_finding until Stage-1 promotion.
                    posture_id = str(uuid.uuid4())
                    cur.execute(
                        """
                        INSERT INTO posture_controls (
                            id, tenant_id, control_ref, standard_id,
                            gap_description, confidence,
                            source, confirmation_status,
                            system_finding, system_proposed_at,
                            is_active, retention_class
                        ) VALUES (
                            %s, %s, %s, %s,
                            %s, %s,
                            'document', %s,
                            %s, NOW(),
                            TRUE, %s
                        )
                        """,
                        (
                            posture_id, tenant_id, control_ref, standard_id,
                            gap_desc[:1000], confidence,
                            _PC_STATUS_DRAFT,
                            finding, _RETENTION_CLASS,
                        ),
                    )
                    _log_status_change(
                        cur,
                        tenant_id        = tenant_id,
                        posture_id       = posture_id,
                        control_ref      = control_ref,
                        standard_id      = standard_id,
                        status_before    = None,
                        status_after     = finding,
                        confidence       = confidence,
                        evidence         = gap_desc,
                        source_upload_id = upload_id,
                        change_kind      = "extraction",
                    )
                    cur.execute(f"RELEASE SAVEPOINT {sp}")
                    created += 1
                    logger.info(
                        f"  + posture_controls: {control_ref} "
                        f"system_finding={finding} (live=Not assessed, awaiting Stage-1)"
                    )

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

def _persist_document_metadata(
    tenant_id: str,
    doc_id:    str,
    metadata:  dict,
    conn,
) -> None:
    """
    Stamp file + content metadata on the client_documents row after intake.
    Sets uploaded_at = NOW() so the registry-import timestamp no longer
    masquerades as the actual upload time. All fields are COALESCEd into
    existing values when the new value is NULL, so this is idempotent
    across re-uploads.

    Expected metadata keys (all optional):
      file_size_bytes, mime_type, checksum_sha256,
      page_count, evidence_type, control_refs (list[str])
    """
    if not metadata:
        return
    control_refs = metadata.get("control_refs")
    if control_refs is not None and not isinstance(control_refs, list):
        control_refs = list(control_refs)

    with conn.cursor() as cur:
        cur.execute("SAVEPOINT sp_cd_metadata")
        try:
            cur.execute(
                """
                UPDATE client_documents
                   SET file_size_bytes = COALESCE(%s, file_size_bytes),
                       mime_type       = COALESCE(%s, mime_type),
                       checksum_sha256 = COALESCE(%s, checksum_sha256),
                       page_count      = COALESCE(%s, page_count),
                       evidence_type   = COALESCE(%s, evidence_type),
                       control_refs    = COALESCE(%s, control_refs),
                       uploaded_at     = NOW()
                 WHERE id = %s AND tenant_id = %s
                """,
                (
                    metadata.get("file_size_bytes"),
                    metadata.get("mime_type"),
                    metadata.get("checksum_sha256"),
                    metadata.get("page_count"),
                    metadata.get("evidence_type"),
                    control_refs,
                    doc_id, tenant_id,
                ),
            )
            cur.execute("RELEASE SAVEPOINT sp_cd_metadata")
            logger.debug(
                f"Stamped metadata on {doc_id}: "
                f"type={metadata.get('evidence_type')} "
                f"pages={metadata.get('page_count')} "
                f"ctrls={len(control_refs or [])}"
            )
        except Exception as e:
            cur.execute("ROLLBACK TO SAVEPOINT sp_cd_metadata")
            cur.execute("RELEASE SAVEPOINT sp_cd_metadata")
            logger.warning(
                f"client_documents metadata stamp failed for {doc_id}: "
                f"{type(e).__name__}: {e}"
            )


def write_findings(
    findings:          list[DocumentFinding],
    tenant_id:         str,
    upload_id:         str,
    conn,
    *,
    metadata:          Optional[dict]       = None,
    uploaded_by:       Optional[str]        = None,
    tabular_rows:      Optional[list[dict]] = None,
    target_controls:   Optional[set[str]]   = None,
    semantic_controls: Optional[set[str]]   = None,
    explicit_refs:     Optional[set[str]]   = None,
    llm_extracted:     Optional[set[str]]   = None,
) -> dict:
    """
    Stage 4 entry point. Write all findings to document_findings and
    aggregate to posture_controls.

    Transaction discipline:
      - Caller opens the connection and calls commit()/rollback()
      - This function uses savepoints for per-row fault isolation
      - _ensure_client_document() runs inside savepoint before batch
      - update_upload_status() must be called separately by caller

    Args:
      metadata: optional dict of file/content metadata to stamp on
                client_documents (file_size_bytes, mime_type, checksum_sha256,
                page_count, evidence_type, control_refs). When present,
                uploaded_at is also refreshed to NOW().

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

    # ── Stamp file/content metadata + actual uploaded_at ──────────────────
    if metadata:
        _persist_document_metadata(tenant_id, doc_id, metadata, conn)

    # ── Stage 4A: document_findings ───────────────────────────────────────
    written = _write_document_findings(
        findings, tenant_id, doc_id, conn,
        uploaded_by       = uploaded_by,
        target_controls   = target_controls,
        semantic_controls = semantic_controls,
        explicit_refs     = explicit_refs,
        llm_extracted     = llm_extracted,
    )

    # ── Stage 4A2: tabular_evidence_rows (per-row capture) ────────────────
    # Schema_v47 — captures the full multi-row content of templated table
    # zones so the renderer can replay all rows on round-trip (continuity
    # across annual refresh) and future advisory can surface per-row
    # completeness. Engine semantics (document_findings → posture) stay
    # unchanged. See [[tabular-evidence-rows-2026-06-26]].
    n_rows_persisted = 0
    if tabular_rows:
        with conn.cursor() as cur:
            # Supersede prior rows for this document. Re-extract sweeps wipe
            # the per-row history for this document_id so we don't accumulate
            # stale rows. (Same supersession discipline as document_findings.)
            cur.execute(
                """
                UPDATE tabular_evidence_rows
                   SET is_active = FALSE
                 WHERE document_id = %s::uuid AND is_active = TRUE
                """,
                (doc_id,),
            )
            for r in tabular_rows:
                leaf_id   = r.get("leaf_id")
                row_index = r.get("row_index")
                cols      = r.get("column_values") or {}
                if not leaf_id or row_index is None or not cols:
                    continue
                cur.execute(
                    """
                    INSERT INTO tabular_evidence_rows (
                        tenant_id, document_id, leaf_id,
                        row_index, column_values, is_active
                    ) VALUES (
                        %s::uuid, %s::uuid, %s,
                        %s, %s::jsonb, TRUE
                    )
                    ON CONFLICT (document_id, leaf_id, row_index) DO UPDATE SET
                        column_values = EXCLUDED.column_values,
                        is_active     = TRUE,
                        extracted_at  = now()
                    """,
                    (tenant_id, doc_id, leaf_id, row_index, json.dumps(cols)),
                )
                n_rows_persisted += 1
        logger.info(f"tabular_evidence_rows: {n_rows_persisted} rows persisted")

    # ── Stage 4B: posture_controls ────────────────────────────────────────
    groups: dict[tuple, list[DocumentFinding]] = {}
    for f in findings:
        if f.finding not in ("not_addressed", None):
            groups.setdefault((f.control_ref, f.standard_id), []).append(f)

    posture_updated, posture_created, posture_skipped = _write_posture_controls(
        groups, tenant_id, conn, upload_id=upload_id,
    )

    summary = {
        "written":           written,
        "posture_updated":   posture_updated,
        "posture_created":   posture_created,
        "posture_skipped":   posture_skipped,
        "controls_assessed": [ref for ref, _ in groups.keys()],
        "doc_id":            doc_id,
        "tabular_rows":      n_rows_persisted,
    }
    logger.info(
        f"Stage 4 complete: {written} findings written, "
        f"{posture_updated} posture updated, {posture_created} posture created, "
        f"{posture_skipped} skipped (source guard)"
    )

    # Ship 3'.c: fire one tenant_notification per upload summarising
    # what landed. Dedup keyed on doc_id (via related_entity_id) so a
    # retry write doesn't spawn a second notification.
    if written > 0 and doc_id:
        try:
            from rag.cascade.notify import notify as _notify
            n_controls = len(summary["controls_assessed"])
            filename = (metadata or {}).get("filename") or "your document"
            title = (
                f"Document processed: {written} findings across "
                f"{n_controls} control{'' if n_controls == 1 else 's'}"
            )
            body = (
                f"We extracted {written} finding{'' if written == 1 else 's'} "
                f"from {filename}. "
                f"{posture_updated} posture{'' if posture_updated == 1 else 's'} "
                f"updated, {posture_created} created. "
                f"Review the pending items in the Stage-1 queue."
            )
            with conn.cursor() as _c:
                _notify(
                    _c,
                    tenant_id           = tenant_id,
                    kind                = "upload_processed",
                    title               = title,
                    body                = body,
                    severity            = "info",
                    related_entity_kind = "client_document",
                    related_entity_id   = doc_id,
                    related_event_type  = "extraction_completed",
                )
        except Exception as _e:
            logger.debug("upload_processed notify skipped: %s", _e)

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
