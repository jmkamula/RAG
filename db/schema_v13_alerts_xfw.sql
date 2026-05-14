-- ArionComply Schema v13 — document_alerts framework-aware aggregation
-- Safe to run on top of v12.
--
-- Motivation: the document_alerts view aggregates linked_controls as a flat
-- string ("5.15, 5.18, A.5.18") with no standard_id, so the "what's missing?"
-- answer can't distinguish ISO 27001 from GDPR refs in cross-framework cases.
--
-- This migration rebuilds the view with TWO columns:
--   linked_control_refs TEXT[]  — structured STANDARD:VERSION:REF entries,
--                                 for code consumption via
--                                 _group_refs_by_framework
--   linked_controls     TEXT    — legacy field, kept for backward compat;
--                                 now framework-prefixed by default so even
--                                 unmodified consumers get correct info
--
-- alert_message also rendered from the new array so the embedded text is
-- framework-correct.

BEGIN;

DROP VIEW IF EXISTS document_alerts;

CREATE VIEW document_alerts AS
WITH doc_priority AS (
    SELECT
        cd.id,
        cd.tenant_id,
        cd.platform_ref,
        cd.external_ref,
        cd.document_title,
        cd.document_type,
        cd.document_status,
        cd.filename,
        cd.approval_status,
        cd.version,
        cd.owner_name,
        cd.last_reviewed_at,
        cd.review_due_at,
        min(
            CASE pc.finding
                WHEN 'NC'::text     THEN 1
                WHEN 'OFI'::text    THEN 2
                WHEN 'Comply'::text THEN 3
                ELSE 4
            END
        ) AS worst_finding_score,
        string_agg(DISTINCT pc.finding, ', '::text) AS linked_findings,
        -- Structured form: STANDARD:VERSION:REF entries
        array_agg(
            DISTINCT (pc.standard_id || ':' || pc.control_ref)
            ORDER BY (pc.standard_id || ':' || pc.control_ref)
        ) FILTER (WHERE pc.control_ref IS NOT NULL) AS linked_control_refs,
        -- Legacy compat: same data string-joined. Now framework-prefixed
        -- so the inline text is unambiguous.
        string_agg(
            DISTINCT (pc.standard_id || ':' || pc.control_ref),
            ', '::text ORDER BY (pc.standard_id || ':' || pc.control_ref)
        ) FILTER (WHERE pc.control_ref IS NOT NULL) AS linked_controls,
        count(DISTINCT pc.id) AS control_count
    FROM client_documents cd
    LEFT JOIN control_documents ctd
           ON ctd.document_id = cd.id
          AND ctd.tenant_id   = cd.tenant_id
    LEFT JOIN posture_controls pc
           ON pc.id        = ctd.control_id
          AND pc.tenant_id = cd.tenant_id
    GROUP BY
        cd.id, cd.tenant_id, cd.platform_ref, cd.external_ref,
        cd.document_title, cd.document_type, cd.document_status,
        cd.filename, cd.approval_status, cd.version, cd.owner_name,
        cd.last_reviewed_at, cd.review_due_at
)
SELECT
    platform_ref,
    external_ref,
    document_title,
    document_status,
    CASE
        WHEN document_status = 'registered' AND worst_finding_score = 1 THEN 'CRITICAL'
        WHEN document_status = 'registered' AND worst_finding_score = 2 THEN 'WARNING'
        WHEN document_status = 'registered' THEN 'INFO'
        WHEN review_due_at IS NOT NULL AND review_due_at < now() THEN 'WARNING'
        ELSE NULL::text
    END AS alert_type,
    CASE
        WHEN document_status = 'registered' AND worst_finding_score = 1
            THEN 'File not uploaded — required evidence for NC finding on '
                 || COALESCE(linked_controls, 'unknown control')
        WHEN document_status = 'registered' AND worst_finding_score = 2
            THEN 'File not uploaded — referenced by OFI finding on '
                 || COALESCE(linked_controls, 'unknown control')
        WHEN document_status = 'registered'
            THEN 'File not uploaded — registered as metadata only'
        WHEN review_due_at IS NOT NULL AND review_due_at < now()
            THEN 'Review overdue since ' || to_char(review_due_at, 'YYYY-MM-DD')
        ELSE 'No action required'
    END AS alert_message,
    linked_controls,
    linked_control_refs,
    linked_findings,
    control_count,
    worst_finding_score,
    filename,
    version,
    owner_name,
    approval_status,
    last_reviewed_at,
    review_due_at,
    tenant_id
FROM doc_priority;

-- Restore SELECT to the app role (DROP VIEW + CREATE VIEW resets grants)
GRANT SELECT ON document_alerts TO arioncomply_app;

COMMIT;
