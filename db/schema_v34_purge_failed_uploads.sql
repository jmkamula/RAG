-- schema_v34 — long-tail cleanup of failed document_uploads rows.
--
-- Companion to the cascade-on-success delete in api_server.upload_document
-- (commit landing alongside this migration). That cascade handles failed
-- rows that the user eventually retries. This function handles the long
-- tail — failed-and-never-retried rows that would otherwise accumulate
-- forever.
--
-- document_uploads is NOT enrolled in the is_active / purge_after / nightly
-- fn_purge_expired_records model — it's an audit log of intake attempts,
-- not a soft-deletable business record. We use a separate function with an
-- explicit age threshold instead.
--
-- Default 30 days: gives the operator time to investigate the pipeline
-- failure, fix the bug, and retry the upload. After 30 days, a never-
-- retried failure is presumed abandoned and can be physically deleted.
--
-- Invocation: a separate scripts/purge_failed_uploads.py wraps this for
-- cron-style use. Always run with p_dry_run=TRUE first; the function
-- returns one row per (tenant, age-bucket) showing what would be deleted.

CREATE OR REPLACE FUNCTION fn_purge_failed_uploads(
    p_older_than_days INT     DEFAULT 30,
    p_dry_run         BOOLEAN DEFAULT TRUE
) RETURNS TABLE (
    tenant_id        UUID,
    rows_candidate   BIGINT,
    rows_purged      BIGINT,
    oldest_uploaded  TIMESTAMPTZ,
    newest_uploaded  TIMESTAMPTZ
) AS $$
DECLARE
    v_cutoff TIMESTAMPTZ := NOW() - (p_older_than_days || ' days')::INTERVAL;
BEGIN
    IF p_dry_run THEN
        RETURN QUERY
            SELECT du.tenant_id,
                   COUNT(*)::BIGINT          AS rows_candidate,
                   0::BIGINT                 AS rows_purged,
                   MIN(du.uploaded_at)       AS oldest_uploaded,
                   MAX(du.uploaded_at)       AS newest_uploaded
              FROM document_uploads du
             WHERE du.extraction_status = 'failed'
               AND du.uploaded_at       < v_cutoff
             GROUP BY du.tenant_id;
        RETURN;
    END IF;

    RETURN QUERY
        WITH deleted AS (
            DELETE FROM document_uploads du
             WHERE du.extraction_status = 'failed'
               AND du.uploaded_at       < v_cutoff
            RETURNING tenant_id, uploaded_at
        )
        SELECT tenant_id,
               COUNT(*)::BIGINT,
               COUNT(*)::BIGINT,
               MIN(uploaded_at),
               MAX(uploaded_at)
          FROM deleted
         GROUP BY tenant_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

GRANT EXECUTE ON FUNCTION fn_purge_failed_uploads(INT, BOOLEAN) TO arioncomply_app;
