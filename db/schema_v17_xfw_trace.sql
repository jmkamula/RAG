-- =============================================================================
-- schema_v17_xfw_trace.sql
--
-- Trace the Stage 4.5 (xfw_proposer) hook so the upload-progress UI can
-- render it as a fifth stage and the status endpoint can surface counts.
--
-- 1. Add proposals_written/proposals_skipped/xfw_targets to intake_trace_log.
--    Existing trace rows have NULL for these — backward compatible.
-- 2. Recreate v_intake_runs to aggregate the new 'xfw' stage row's metrics
--    alongside the existing read/enrich/extract/write rollups.
-- =============================================================================

BEGIN;

ALTER TABLE intake_trace_log
    ADD COLUMN IF NOT EXISTS proposals_written integer,
    ADD COLUMN IF NOT EXISTS proposals_skipped integer,
    ADD COLUMN IF NOT EXISTS xfw_targets       text[];

DROP VIEW IF EXISTS v_intake_runs;

CREATE VIEW v_intake_runs AS
SELECT
    trace_id,
    tenant_id,
    upload_id,
    filename,
    max(CASE WHEN stage = 'enrich'  THEN doc_type             END) AS doc_type,
    max(CASE WHEN stage = 'enrich'  THEN standard_ids::text   END) AS standard_ids,
    max(CASE WHEN stage = 'enrich'  THEN extraction_path      END) AS extraction_path,
    max(CASE WHEN stage = 'read'    THEN token_estimate       END) AS token_estimate,
    max(CASE WHEN stage = 'extract' THEN findings_kept        END) AS findings_extracted,
    max(CASE WHEN stage = 'write'   THEN findings_written     END) AS findings_written,
    max(CASE WHEN stage = 'write'   THEN posture_created      END) AS posture_created,
    max(CASE WHEN stage = 'write'   THEN posture_updated      END) AS posture_updated,
    max(CASE WHEN stage = 'write'   THEN posture_skipped      END) AS posture_skipped,
    max(CASE WHEN stage = 'xfw'     THEN proposals_written    END) AS proposals_written,
    max(CASE WHEN stage = 'xfw'     THEN proposals_skipped    END) AS proposals_skipped,
    max(CASE WHEN stage = 'xfw'     THEN xfw_targets          END) AS xfw_targets,
    max(total_ms)                                                  AS total_ms,
    max(error_type)                                                AS error_type,
    max(error_detail)                                              AS error_detail,
    bool_or(stage_status = 'error')                                AS had_error,
    min(traced_at)                                                 AS started_at,
    max(traced_at)                                                 AS completed_at
FROM intake_trace_log
GROUP BY trace_id, tenant_id, upload_id, filename;

GRANT SELECT ON v_intake_runs TO arioncomply_app;

COMMIT;
