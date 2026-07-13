-- schema_v66_notification_delivery.sql
--
-- Outbound notification delivery (2026-07-13) — closes the temporal-
-- arcs loop. Currently tenant_notification rows land in-DB and stay
-- there; nothing external is triggered. This adds:
--
--   tenant_notification_channel      per-tenant delivery config
--   notification_delivery_attempt    per-(notification, channel) audit
--
-- The delivery worker (rag.notifications.deliver) reads
-- tenant_notification for undelivered rows, iterates the tenant's
-- active channels, delivers per channel type, records the attempt.
-- Sweep tick's notification_delivery work_type invokes the worker.

BEGIN;

-- Channel config — one row per (tenant, channel type). Endpoint
-- format varies by kind: email → recipient(s), slack → webhook URL.
CREATE TABLE IF NOT EXISTS tenant_notification_channel (
    id             uuid          PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id      uuid          NOT NULL REFERENCES tenants(id),
    channel_kind   text          NOT NULL,
    endpoint       text          NOT NULL,       -- email address / webhook URL / etc.
    is_active      boolean       NOT NULL DEFAULT TRUE,
    -- Filter: minimum severity to deliver via this channel. 'info'
    -- delivers everything; 'high' only delivers high+critical.
    min_severity   text          NOT NULL DEFAULT 'medium',
    -- Optional metadata (SMTP creds by-reference / Slack workspace / etc.)
    config         jsonb         NOT NULL DEFAULT '{}',
    created_at     timestamptz   NOT NULL DEFAULT NOW(),
    updated_at     timestamptz   NOT NULL DEFAULT NOW(),
    CONSTRAINT nc_kind_check     CHECK (channel_kind IN ('email','slack','webhook','sms')),
    CONSTRAINT nc_severity_check CHECK (min_severity IN ('info','low','medium','high','critical'))
);

CREATE INDEX IF NOT EXISTS idx_nc_tenant_kind
    ON tenant_notification_channel (tenant_id, channel_kind) WHERE is_active = TRUE;

COMMENT ON TABLE tenant_notification_channel IS
'Per-tenant outbound delivery configuration. Delivery worker iterates active channels for each undelivered tenant_notification.';

-- Per-notification per-channel delivery attempt log. Success rows
-- have delivered_at populated; failed rows have error_type + error_detail.
-- The worker uses this to (a) skip already-delivered pairs, (b)
-- implement backoff retry for failed attempts.
CREATE TABLE IF NOT EXISTS notification_delivery_attempt (
    id                  uuid          PRIMARY KEY DEFAULT gen_random_uuid(),
    notification_id     uuid          NOT NULL,   -- tenant_notification.id
    tenant_id           uuid          NOT NULL,
    channel_id          uuid          NOT NULL REFERENCES tenant_notification_channel(id),
    channel_kind        text          NOT NULL,
    endpoint            text          NOT NULL,
    attempted_at        timestamptz   NOT NULL DEFAULT NOW(),
    delivered_at        timestamptz,
    error_type          text,
    error_detail        text,
    latency_ms          integer,
    retry_count         integer       NOT NULL DEFAULT 0
);

CREATE INDEX IF NOT EXISTS idx_nda_notification
    ON notification_delivery_attempt (notification_id);
CREATE INDEX IF NOT EXISTS idx_nda_tenant_time
    ON notification_delivery_attempt (tenant_id, attempted_at DESC);
CREATE INDEX IF NOT EXISTS idx_nda_failed
    ON notification_delivery_attempt (tenant_id, attempted_at DESC)
 WHERE error_type IS NOT NULL AND delivered_at IS NULL;

COMMENT ON TABLE notification_delivery_attempt IS
'One row per (notification, channel, attempt). Success = delivered_at populated. Failed rows drive backoff retry.';

GRANT SELECT, INSERT, UPDATE ON tenant_notification_channel TO arioncomply_app;
GRANT SELECT, INSERT   ON notification_delivery_attempt    TO arioncomply_app;

COMMIT;
