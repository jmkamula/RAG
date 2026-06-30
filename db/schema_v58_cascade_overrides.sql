-- schema_v58_cascade_overrides.sql — S3n per-tenant cascade overrides
--
-- Lets a tenant suppress specific cascade behaviours that don't fit
-- their organisation (e.g. "we don't have a formal disciplinary
-- process — mute A.6.4 cascades"). Override rows consulted by the
-- cascade engine before writing implications; matched overrides
-- suppress the implication and log to cascade_suppression_log with
-- suppression_kind='policy_override'.
--
-- Two override kinds at v1:
--   mute_event         — every TRIGGERS_OBLIGATION on the event is suppressed
--   mute_event_target  — only the specific (event, target_control) pair
--
-- Active rows are unique per (tenant, override_kind, event_type,
-- coalesce(target_requirement_id, '')). Soft-delete via is_active.

BEGIN;

CREATE TABLE IF NOT EXISTS tenant_cascade_override (
    id                     UUID         PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id              UUID         NOT NULL,

    override_kind          TEXT         NOT NULL,
    -- 'mute_event' | 'mute_event_target'

    event_type             TEXT         NOT NULL,
    -- e.g. 'phishing_threshold_crossed'

    target_requirement_id  TEXT,
    -- e.g. 'ISO27001:2022:A.6.4'. NULL for mute_event.

    reason                 TEXT,
    -- Auditor-grade explanation.

    is_active              BOOLEAN      NOT NULL DEFAULT TRUE,
    created_at             TIMESTAMPTZ  NOT NULL DEFAULT now(),
    created_by             UUID,
    updated_at             TIMESTAMPTZ  NOT NULL DEFAULT now(),
    updated_by             UUID,

    CONSTRAINT tenant_cascade_override_kind_chk
        CHECK (override_kind IN ('mute_event', 'mute_event_target')),
    CONSTRAINT tenant_cascade_override_consistency_chk CHECK (
        (override_kind = 'mute_event'        AND target_requirement_id IS NULL)
        OR
        (override_kind = 'mute_event_target' AND target_requirement_id IS NOT NULL)
    )
);

CREATE UNIQUE INDEX IF NOT EXISTS tenant_cascade_override_active_unique
    ON tenant_cascade_override(
        tenant_id, override_kind, event_type,
        coalesce(target_requirement_id, '')
    )
    WHERE is_active = TRUE;

CREATE INDEX IF NOT EXISTS idx_tenant_cascade_override_lookup
    ON tenant_cascade_override(tenant_id, event_type)
    WHERE is_active = TRUE;

ALTER TABLE tenant_cascade_override ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS tenant_isolation ON tenant_cascade_override;
CREATE POLICY tenant_isolation ON tenant_cascade_override
    USING (tenant_id::text = current_setting('app.tenant_id', TRUE));

GRANT SELECT, INSERT, UPDATE ON tenant_cascade_override TO arioncomply_app;

COMMENT ON TABLE tenant_cascade_override IS
    'Per-tenant cascade-behaviour overrides. Engine consults these before writing triggered_implication rows; matched rows suppress + log to cascade_suppression_log.';


-- ── Extend cascade_suppression_log enum for policy_override ───────────
ALTER TABLE cascade_suppression_log
    DROP CONSTRAINT IF EXISTS cascade_suppression_log_kind_chk;
ALTER TABLE cascade_suppression_log
    ADD CONSTRAINT cascade_suppression_log_kind_chk
        CHECK (suppression_kind IN ('emits_event', 'blocks_when', 'policy_override'));

ALTER TABLE cascade_suppression_log
    DROP CONSTRAINT IF EXISTS cascade_suppression_log_consistency_chk;
ALTER TABLE cascade_suppression_log
    ADD CONSTRAINT cascade_suppression_log_consistency_chk
        CHECK (
            (suppression_kind = 'emits_event'
              AND target_event_type IS NOT NULL)
            OR
            (suppression_kind = 'blocks_when'
              AND target_requirement_id IS NOT NULL)
            OR
            (suppression_kind = 'policy_override'
              AND (target_event_type IS NOT NULL
                   OR target_requirement_id IS NOT NULL))
        );

COMMIT;
