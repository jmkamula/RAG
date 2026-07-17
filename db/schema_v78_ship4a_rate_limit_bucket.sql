-- schema_v78_ship4a_rate_limit_bucket.sql
--
-- Ship 4'.a (2026-07-17) — external API foundation.
--
-- New table: api_rate_limit_bucket. Fixed-window (1-minute) counter
-- for the /api/external/v1/* namespace. One row per api_key.
--
-- Design choices:
--
--   * Single row per key (PK = key_id) with (window_start, count)
--     that rolls over as time advances. Simpler than a growing log
--     of timestamps; O(1) storage per key regardless of traffic.
--
--   * `window_start` truncates to the minute — same value across the
--     full 60-second window. When a request lands, the app checks:
--     if window_start == date_trunc('minute', NOW()), increment;
--     otherwise reset to 1 with the new window_start.
--
--   * Kept in Postgres rather than Redis because (a) the project
--     already runs Postgres for everything else, and (b) rate-limit
--     traffic at this stage is low enough that atomic INSERT ... ON
--     CONFLICT DO UPDATE handles concurrency fine.
--
--   * Ships 3'.k established the sweep pattern for age-out; this
--     table stays small (one row per active key) so no retention
--     sweep needed today.

BEGIN;

CREATE TABLE IF NOT EXISTS api_rate_limit_bucket (
    key_id       UUID                     PRIMARY KEY REFERENCES api_keys(id) ON DELETE CASCADE,
    window_start TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT date_trunc('minute', NOW()),
    count        INTEGER                  NOT NULL DEFAULT 0,
    updated_at   TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    CONSTRAINT api_rate_limit_bucket_count_non_negative CHECK (count >= 0)
);

COMMENT ON TABLE api_rate_limit_bucket IS
'Ship 4''.a: per-api_key fixed-window (1min) rate-limit counter for /api/external/v1/* endpoints.';

COMMENT ON COLUMN api_rate_limit_bucket.window_start IS
'Start of the current 1-minute window (date_trunc(''minute'',NOW())). Rolls over on next request past the window boundary.';

-- Enable RLS so tenant-scoped reads (if any) are safe by default. The
-- primary consumer is the app role via cross-tenant maintenance, so
-- add a permissive `app_*_all` policy following the pattern from
-- schema_v70 / v72 / v73. Follow the discipline from
-- [[feedback-rls-grant-parity]]: grant DELETE too, so a future
-- retention sweep can clean up stale rows without a schema chase.
ALTER TABLE api_rate_limit_bucket ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS app_api_rate_limit_bucket_all ON api_rate_limit_bucket;
CREATE POLICY app_api_rate_limit_bucket_all ON api_rate_limit_bucket
    AS PERMISSIVE FOR ALL
    TO arioncomply_app
    USING (true) WITH CHECK (true);

GRANT SELECT, INSERT, UPDATE, DELETE ON api_rate_limit_bucket TO arioncomply_app;

COMMIT;
