-- =============================================================================
-- schema_v21_posture_history.sql
--
-- Append-only audit log of posture status transitions — the "timeline"
-- data source for "how did A.5.18 evolve over time?".
--
-- Lives under a NEW name (posture_status_log) rather than the existing
-- posture_history table. The latter is a partitioned snapshot table seeded
-- by past migrations but never wired to live writers — touching it would
-- mean reconciling 93 legacy seed rows, the is_active=true RLS qualifier,
-- and a retention trigger we don't want to perturb. Consolidation can come
-- later if the snapshot side ever gets wired up.
--
-- Scope (Stage 3): document-intake emissions only. Confirm/override and
-- workbook paths are not wired yet — they'll get their own stage.
--
-- No backfill: existing posture_controls rows have an implicit
-- "unknown before now" prior state; future changes get captured cleanly.
-- =============================================================================

BEGIN;

CREATE TABLE IF NOT EXISTS posture_status_log (
    id                 uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id          uuid NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    posture_id         uuid REFERENCES posture_controls(id) ON DELETE SET NULL,
    control_ref        text NOT NULL,
    standard_id        text NOT NULL,
    status_before      text,                 -- NULL on first creation
    status_after       text NOT NULL,
    source             text NOT NULL,        -- 'document' for now (Stage 3 scope)
    source_upload_id   uuid REFERENCES document_uploads(id) ON DELETE SET NULL,
    evidence_citation  text,                 -- short snippet from the driving finding
    confidence         text,
    changed_at         timestamptz NOT NULL DEFAULT now()
);

-- Primary read pattern: "show me the timeline for control X".
CREATE INDEX IF NOT EXISTS idx_posture_status_log_lookup
    ON posture_status_log (tenant_id, control_ref, standard_id, changed_at);

-- Secondary read: "what did this upload change?" — supports a future
-- /uploads/{id}/posture-impact view without another scan.
CREATE INDEX IF NOT EXISTS idx_posture_status_log_upload
    ON posture_status_log (source_upload_id)
    WHERE source_upload_id IS NOT NULL;

-- RLS — same pattern as posture_controls / document_text: arioncomply_app
-- gets the constant-true policy and tenant scoping is enforced at the
-- query layer via set_config('app.tenant_id', ...). Superuser bypasses.
ALTER TABLE posture_status_log ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS app_all_posture_status_log ON posture_status_log;
CREATE POLICY app_all_posture_status_log ON posture_status_log
    FOR ALL
    TO arioncomply_app
    USING (true)
    WITH CHECK (true);

GRANT SELECT, INSERT ON posture_status_log TO arioncomply_app;
-- No UPDATE/DELETE grant — append-only by design. Superuser can still
-- prune for retention if needed.

COMMIT;
