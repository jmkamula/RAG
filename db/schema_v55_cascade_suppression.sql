-- schema_v55_cascade_suppression.sql — S3d applies_when audit
--
-- When an EMITS_EVENT edge has an applies_when condition that
-- evaluates to FALSE against the structured-event metadata, the
-- engine suppresses the downstream cascade walk. This table logs
-- every such suppression so the auditor can see WHICH cascades did
-- NOT fire and WHY (the meta-cascade equivalent of "this was
-- considered and consciously skipped").
--
-- Append-only. Source-of-truth pairing with the verification log
-- row that triggered the cascade.

BEGIN;

CREATE TABLE IF NOT EXISTS cascade_suppression_log (
    id                     UUID         PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id              UUID         NOT NULL,

    source_verification_id UUID         NOT NULL
        REFERENCES external_evidence_verification_log(id) ON DELETE CASCADE,

    source_event_type      TEXT         NOT NULL,
    -- The event whose EMITS_EVENT edge was evaluated. (May be the
    -- top-level structured event OR an intermediate event reached
    -- via prior EMITS_EVENT hops.)

    target_event_type      TEXT         NOT NULL,
    -- The would-be-emitted event (the suppressed downstream).

    applies_when           TEXT         NOT NULL,
    -- The exact condition string evaluated.

    evaluation_context     JSONB        NOT NULL DEFAULT '{}'::jsonb,
    -- Copy of the metadata dict the condition was evaluated against
    -- (so a re-evaluation can be done against historical context).

    cascade_path           JSONB        NOT NULL DEFAULT '[]'::jsonb,
    -- The path up to the suppression point.

    fired_at               TIMESTAMPTZ  NOT NULL DEFAULT now(),

    CONSTRAINT cascade_suppression_log_applies_when_nonempty
        CHECK (length(trim(applies_when)) > 0)
);

CREATE INDEX IF NOT EXISTS idx_cascade_suppression_tenant_fired
    ON cascade_suppression_log(tenant_id, fired_at DESC);

CREATE INDEX IF NOT EXISTS idx_cascade_suppression_source
    ON cascade_suppression_log(source_verification_id);

ALTER TABLE cascade_suppression_log ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS tenant_isolation ON cascade_suppression_log;
CREATE POLICY tenant_isolation ON cascade_suppression_log
    USING (tenant_id::text = current_setting('app.tenant_id', TRUE));

GRANT SELECT, INSERT ON cascade_suppression_log TO arioncomply_app;

COMMENT ON TABLE cascade_suppression_log IS
    'Append-only log of EMITS_EVENT edges whose applies_when evaluated false. Captures the path that was considered and consciously skipped, for auditor explanation of why a downstream cascade did not fire.';

COMMIT;
