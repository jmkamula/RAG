-- schema_v59_notifications.sql — S3t in-app notification surface
--
-- Append-on-event notifications surfaced to tenants. Cascade write
-- sites (posture_loader overdue sweep, sweep_overdue_followups,
-- fire_cascade threshold-crossed + blocker-active) INSERT rows; the
-- frontend bell + inbox page reads.
--
-- Lifecycle: unread -> read -> dismissed. Read and dismissed are
-- recorded by timestamp so the inbox can rank by recency.

BEGIN;

CREATE TABLE IF NOT EXISTS tenant_notification (
    id                     UUID         PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id              UUID         NOT NULL,

    kind                   TEXT         NOT NULL,
    -- 'implication_overdue' | 'followup_overdue' |
    -- 'threshold_crossed'   | 'cascade_blocked'  |
    -- 'auto_resolved'

    title                  TEXT         NOT NULL,
    body                   TEXT,

    severity               TEXT         NOT NULL DEFAULT 'info',
    -- 'critical' | 'high' | 'medium' | 'low' | 'info'

    -- ── Optional links to source entities ──
    related_entity_kind    TEXT,
    -- 'triggered_implication' | 'expected_followup_event' |
    -- 'cascade_suppression_log' | 'external_evidence_verification_log'
    related_entity_id      UUID,
    related_control_ref    TEXT,
    related_event_type     TEXT,

    fired_at               TIMESTAMPTZ  NOT NULL DEFAULT now(),
    read_at                TIMESTAMPTZ,
    dismissed_at           TIMESTAMPTZ,

    CONSTRAINT tenant_notification_kind_chk
        CHECK (kind IN ('implication_overdue',
                        'followup_overdue',
                        'threshold_crossed',
                        'cascade_blocked',
                        'auto_resolved')),
    CONSTRAINT tenant_notification_severity_chk
        CHECK (severity IN ('critical', 'high', 'medium', 'low', 'info'))
);

CREATE INDEX IF NOT EXISTS idx_tenant_notification_tenant_fired
    ON tenant_notification(tenant_id, fired_at DESC);

CREATE INDEX IF NOT EXISTS idx_tenant_notification_unread
    ON tenant_notification(tenant_id, fired_at DESC)
    WHERE read_at IS NULL AND dismissed_at IS NULL;

-- Partial unique to prevent duplicate notifications for the same
-- entity in a short window. Engine de-dups by writing only when no
-- active (unread+undismissed) row exists for (entity_kind, entity_id).
-- Doesn't constrain historical duplicates after dismiss.
CREATE UNIQUE INDEX IF NOT EXISTS tenant_notification_active_unique
    ON tenant_notification(
        tenant_id, kind,
        coalesce(related_entity_id::text, ''),
        coalesce(related_control_ref, '')
    )
    WHERE read_at IS NULL AND dismissed_at IS NULL;

ALTER TABLE tenant_notification ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS tenant_isolation ON tenant_notification;
CREATE POLICY tenant_isolation ON tenant_notification
    USING (tenant_id::text = current_setting('app.tenant_id', TRUE));
GRANT SELECT, INSERT, UPDATE ON tenant_notification TO arioncomply_app;

COMMENT ON TABLE tenant_notification IS
    'Per-tenant in-app notifications. Cascade write sites emit rows; frontend bell + inbox reads. Active-row partial unique prevents per-entity duplicate spam.';

COMMIT;
