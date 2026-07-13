-- schema_v65_sweep_log.sql
--
-- Periodic sweep scheduler (3b, 2026-07-13). Audit trail for every
-- scheduled sweep — fact recompute, overdue followups, freshness
-- expiration, etc. One row per (tick, work_type). Feeds:
--   - Trace UI: "when did the scheduler last run?"
--   - Health monitoring: are sweeps completing on time?
--   - Debug: what did the last sweep do?
--
-- The scheduler is stateless — cron/systemd fires
-- `python -m rag.scheduler.tick` on a cadence; each invocation
-- writes to this log. No process state to lose across restarts.

BEGIN;

CREATE TABLE IF NOT EXISTS sweep_log (
    id             uuid          PRIMARY KEY DEFAULT gen_random_uuid(),
    tick_id        uuid          NOT NULL,       -- one uuid per tick, groups all work_types from a single run
    work_type      text          NOT NULL,
    started_at     timestamptz   NOT NULL,
    completed_at   timestamptz,
    status         text          NOT NULL,
    -- Volume metrics
    items_scanned  integer,
    items_acted_on integer,
    items_error    integer,
    -- Per-work-type detail (jsonb)
    detail         jsonb         NOT NULL DEFAULT '{}',
    error_type     text,
    error_detail   text,
    CONSTRAINT sweep_log_work_type_check
        CHECK (work_type IN (
            'fact_recompute',
            'overdue_followups',
            'freshness_expiry',
            'notification_delivery',
            'engine_kick',
            'other'
        )),
    CONSTRAINT sweep_log_status_check
        CHECK (status IN ('running', 'completed', 'failed'))
);

CREATE INDEX IF NOT EXISTS idx_sweep_log_tick
    ON sweep_log (tick_id);

CREATE INDEX IF NOT EXISTS idx_sweep_log_type_time
    ON sweep_log (work_type, started_at DESC);

CREATE INDEX IF NOT EXISTS idx_sweep_log_errors
    ON sweep_log (started_at DESC) WHERE status = 'failed';

COMMENT ON TABLE sweep_log IS
'Sweep scheduler audit trail — one row per (tick, work_type). Fed by rag.scheduler.tick. Not tenant-scoped: tick runs across all tenants in one call.';

GRANT SELECT, INSERT, UPDATE ON sweep_log TO arioncomply_app;

COMMIT;
