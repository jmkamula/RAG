"""Ship 93'.z.iii — closure trail stamp.

After a document upload produces its findings, walk any pre-existing
`document_findings` rows (from other documents) that were
`status ∈ {partial}` on the same MUST as one of the new present
findings — and stamp their `resolved_by_upload_id` + `resolved_at`
+ `resolution_reason`.

Auditor sees on the resolved partial's history: "resolved by upload
of X.docx on 2026-08-24" — explicit closure chain, not just
"superseded is_active=FALSE".

NOT auto-superseding the resolved partial: Ship 93'.b/f's design is
that both findings coexist (present from doc + partial from workbook
= auditor sees two provenance chains). The closure stamp just adds
the linkage; Stage-1 approve/reject flow on the partial is
unchanged.

Best-effort: errors logged + swallowed. Called from doc_pipeline
after Stage 4 write commits.
"""
from __future__ import annotations

import logging
from typing import Any
from uuid import UUID

logger = logging.getLogger(__name__)


def stamp_closures_from_upload(
    pg,
    tenant_id:          str | UUID,
    client_document_id: str | UUID,
) -> dict:
    """Ship 93'.z.iii — stamp closure trail on findings the new upload closed.

    Rule: for every finding produced by this upload with
    `status='present'` + `checklist_item_id=X`, look up all OTHER
    active findings on the same tenant + same MUST with
    `status='partial'` and NO existing `resolved_by_upload_id` →
    stamp them.

    Returns a stats dict:
      {
        "presents_scanned": int,   # new present findings from this upload
        "prior_partials":   int,   # prior partials found on same MUSTs
        "closures_stamped": int,   # rows updated with resolved_by_upload_id
      }
    """
    result: dict[str, Any] = {
        "presents_scanned": 0,
        "prior_partials":   0,
        "closures_stamped": 0,
        "error":            None,
    }
    tenant_str = str(tenant_id)
    doc_str    = str(client_document_id)

    try:
        with pg.cursor() as cur:
            cur.execute(
                "SELECT set_config('app.tenant_id', %s, TRUE)",
                (tenant_str,),
            )
            # 1. Presents on this upload — the new evidence.
            cur.execute(
                """
                SELECT df.checklist_item_id, df.control_ref
                  FROM document_findings df
                 WHERE df.tenant_id       = %s::uuid
                   AND df.document_id     = %s::uuid
                   AND df.status          = 'present'
                   AND df.is_active       = TRUE
                   AND df.checklist_item_id IS NOT NULL
                """,
                (tenant_str, doc_str),
            )
            presents = cur.fetchall()
            result["presents_scanned"] = len(presents)
            if not presents:
                return result

            # 2. Fetch the uploaded document's filename for the reason
            # narrative.
            cur.execute(
                "SELECT filename FROM client_documents "
                "WHERE id = %s::uuid AND tenant_id = %s::uuid",
                (doc_str, tenant_str),
            )
            row = cur.fetchone()
            source_filename = (row[0] if row else "the uploaded document") or "the uploaded document"

            # We stamped by must_id (not just control_ref) because a
            # MUST is the finest granularity a cite / partial binds
            # to. control_ref would over-stamp (close all partials on
            # the same control even if the doc only evidences one MUST).
            for must_id, control_ref in presents:
                cur.execute(
                    """
                    UPDATE document_findings
                       SET resolved_by_upload_id = (
                             SELECT id FROM document_uploads
                              WHERE id IN (
                                SELECT du.id
                                  FROM document_uploads du
                                  JOIN client_documents cd
                                    ON cd.checksum_sha256 = du.sha256
                                 WHERE cd.id = %s::uuid
                                   AND du.tenant_id = %s::uuid
                              )
                             LIMIT 1
                           ),
                           resolved_at       = NOW(),
                           resolution_reason = %s
                     WHERE tenant_id         = %s::uuid
                       AND checklist_item_id = %s
                       AND status            = 'partial'
                       AND is_active         = TRUE
                       AND document_id      != %s::uuid   -- don't self-stamp
                       AND resolved_by_upload_id IS NULL  -- don't overwrite
                    RETURNING id
                    """,
                    (
                        doc_str, tenant_str,
                        (f"Upload of '{source_filename}' produced present "
                         f"finding on same MUST {must_id}"),
                        tenant_str,
                        must_id,
                        doc_str,
                    ),
                )
                bumped = len(cur.fetchall())
                result["closures_stamped"] += bumped
                if bumped == 0:
                    # Track how many prior partials existed even if no
                    # stamp fired (already stamped or none present).
                    cur.execute(
                        """
                        SELECT COUNT(*) FROM document_findings
                         WHERE tenant_id         = %s::uuid
                           AND checklist_item_id = %s
                           AND status            = 'partial'
                           AND is_active         = TRUE
                           AND document_id      != %s::uuid
                        """,
                        (tenant_str, must_id, doc_str),
                    )
                    result["prior_partials"] += (cur.fetchone()[0] or 0)
                else:
                    result["prior_partials"] += bumped

        pg.commit()
    except Exception as e:
        pg.rollback()
        result["error"] = f"{type(e).__name__}: {e}"
        logger.warning("finding_closure: stamp_closures failed: %s", e)

    return result
