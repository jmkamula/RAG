"""Ship 92'.a.iii — auto-verify workbook cites on document upload.

When a client_document is uploaded, this resolver looks up all active
external_evidence_source rows for the tenant that have a stored
hyperlink URL, and checks whether the uploaded document matches
(URL basename ILIKE client_documents.filename). For each match, it
also requires that the uploaded document has produced a
document_finding with status='present' on the same MUST as the cite
— evidence-of-what-was-cited, not just filename-collision. If both
conditions hold, the cite is auto-verified: `last_verified_at` set,
`next_review_due` bumped by cadence, and an
`external_evidence_verification_log` row is written for the audit
trail.

Design notes (Ship 92'.a user selections):
  - URL match alone is not enough — requires linked-doc present
    findings on same MUST (auditor-defensible; Ship 89'.b Lesson 98
    stored/cited separation).
  - `changes_detected` records 'auto-matched by URL basename'.
  - `verified_by` uses the uploading user's UUID (the person's
    upload triggered the verification).
  - `sample_upload_id` links back to client_documents.id.

Env gate:
  USE_CITE_AUTO_VERIFY ∈ {"0", "1"} — default "1" (on). Zero blast
  radius when a tenant has no cites; safe to leave on.

Hook: called from doc_pipeline as Stage 4.8, immediately after
workbook_persistence (Stage 4.6) + workbook_arbiter (Stage 4.7, if
enabled). Best-effort — errors are logged and swallowed; never
blocks the upload pipeline.
"""
from __future__ import annotations

import logging
import os
from typing import Any
from urllib.parse import urlparse, unquote
from uuid import UUID

logger = logging.getLogger(__name__)


def _url_basename(url: str) -> str | None:
    """Extract the last path segment of a URL / file link (case-preserved).

    Returns None if no extractable filename. Handles:
      https://.../file.docx?ver=3               → 'file.docx'
      https://.../file.docx#page=2              → 'file.docx'
      \\\\fileshare\\file.docx                  → 'file.docx'
      file.docx (bare)                          → 'file.docx'
      https://landing.example.com/site          → None (no extension)
      mailto:foo@bar                            → None
      ''                                        → None
    """
    if not url:
        return None
    if url.lower().startswith("mailto:"):
        return None
    try:
        parsed = urlparse(url)
        path = parsed.path or url
    except Exception:
        path = url
    path = path.replace("\\", "/").split("?", 1)[0].split("#", 1)[0]
    if not path:
        return None
    last = path.rstrip("/").split("/")[-1]
    if not last:
        return None
    try:
        last = unquote(last)
    except Exception:
        pass
    if "." not in last:
        return None
    return last


def resolve_cites_on_document_upload(
    pg,
    tenant_id:          str | UUID,
    client_document_id: str | UUID,
    user_id:            str | UUID | None,
) -> dict:
    """Ship 92'.a.iii entry point — called after successful doc upload.

    Args:
      pg:                 open psycopg2 connection
      tenant_id:          tenant UUID
      client_document_id: the freshly-uploaded client_documents.id
      user_id:            uploading user's UUID (used as verified_by)

    Returns a stats dict:
      {
        "cites_scanned":       int,   # active cites with hyperlink_url
        "url_matches":         int,   # basename matched client_documents
        "must_matches":        int,   # url_matches + linked-doc has present
        "verified":            int,   # verification_log rows written
        "target_document":     str,
        "target_filename":     str,
      }

    Best-effort: on internal error, returns partial stats + logs
    warning. Never raises to caller.
    """
    result: dict[str, Any] = {
        "cites_scanned": 0, "url_matches": 0,
        "must_matches": 0, "verified": 0,
        "target_document": str(client_document_id),
        "target_filename": None,
        "error": None,
    }
    if (os.getenv("USE_CITE_AUTO_VERIFY") or "1") == "0":
        result["error"] = "USE_CITE_AUTO_VERIFY=0"
        return result

    tenant_str = str(tenant_id)
    doc_str    = str(client_document_id)

    try:
        with pg.cursor() as cur:
            cur.execute(
                "SELECT set_config('app.tenant_id', %s, TRUE)",
                (tenant_str,),
            )
            # 1. Get the uploaded document's filename.
            cur.execute(
                """
                SELECT filename FROM client_documents
                 WHERE id = %s::uuid AND tenant_id = %s::uuid
                   AND is_active = TRUE
                 LIMIT 1
                """,
                (doc_str, tenant_str),
            )
            row = cur.fetchone()
            if not row:
                result["error"] = "client_document not found or not active"
                return result
            target_filename = (row[0] or "").strip()
            result["target_filename"] = target_filename
            if not target_filename:
                return result

            # 2. Fetch active cites with a stored hyperlink_url.
            cur.execute(
                """
                SELECT ees.id::text, ees.must_id, ees.leaf_id,
                       ees.system_id::text, ees.hyperlink_url,
                       ees.cadence_days, ees.last_verified_at
                  FROM external_evidence_source ees
                 WHERE ees.tenant_id     = %s::uuid
                   AND ees.is_active     = TRUE
                   AND ees.hyperlink_url IS NOT NULL
                """,
                (tenant_str,),
            )
            cites = cur.fetchall()
            result["cites_scanned"] = len(cites)
            if not cites:
                return result

            target_lower = target_filename.lower()

            for cite_id, must_id, leaf_id, system_id, url, cadence_days, last_verified in cites:
                basename = _url_basename(url or "")
                if not basename:
                    continue
                if basename.lower() != target_lower:
                    continue
                result["url_matches"] += 1

                # 3. Require: uploaded doc has present findings on same MUST.
                cur.execute(
                    """
                    SELECT 1 FROM document_findings
                     WHERE tenant_id         = %s::uuid
                       AND document_id       = %s::uuid
                       AND checklist_item_id = %s
                       AND status            = 'present'
                       AND is_active         = TRUE
                     LIMIT 1
                    """,
                    (tenant_str, doc_str, must_id),
                )
                if cur.fetchone() is None:
                    continue
                result["must_matches"] += 1

                # 4. Write verification_log + update cite.
                # verified_by is NOT NULL — use uploading user; if
                # None (rare), fall back to a synthetic sentinel-uuid
                # constant. The upload path always has a user_id in
                # practice; this defence-in-depth handles admin CLI.
                _verified_by = str(user_id) if user_id else "00000000-0000-0000-0000-000000000000"
                cur.execute(
                    """
                    INSERT INTO external_evidence_verification_log (
                        tenant_id, system_id, leaf_id,
                        verified_by, changes_detected,
                        sample_upload_id, note,
                        musts_covered_count
                    ) VALUES (
                        %s::uuid, %s::uuid, %s,
                        %s::uuid, %s,
                        %s::uuid, %s,
                        1
                    )
                    """,
                    (
                        tenant_str, system_id, leaf_id,
                        _verified_by,
                        "auto-matched by URL basename",
                        doc_str,
                        (f"Ship 92'.a auto-verify — cite URL basename "
                         f"'{basename}' matched uploaded document "
                         f"'{target_filename}'; document has present "
                         f"finding on {must_id}"),
                    ),
                )
                # Update the cite row itself.
                cur.execute(
                    """
                    UPDATE external_evidence_source
                       SET last_verified_at = NOW(),
                           next_review_due  = NOW() + make_interval(days => %s),
                           updated_at       = NOW(),
                           updated_by       = %s::uuid
                     WHERE id = %s::uuid
                    """,
                    (cadence_days, _verified_by, cite_id),
                )
                result["verified"] += 1

        pg.commit()
    except Exception as e:
        pg.rollback()
        result["error"] = f"{type(e).__name__}: {e}"
        logger.warning("cite_resolver: resolve_cites failed: %s", e)

    return result
