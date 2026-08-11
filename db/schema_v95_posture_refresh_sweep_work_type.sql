-- schema_v95 — add 'posture_refresh' to sweep_log.work_type CHECK constraint.
--
-- Ship 58'.u (2026-08-11). The periodic scheduler needs a new work type
-- that refreshes posture_must_verdicts for tenants whose computed_at is
-- older than the staleness threshold (default 24h) OR who have never
-- been populated. Closes the P1 loose-end where long-idle tenants
-- accumulate stale SSoT rows (e.g. freshness_days expiry doesn't
-- surface as `stale=TRUE` until an unrelated write triggers a refresh).
--
-- Follows the same idempotent DROP+ADD pattern as prior work_type
-- additions (schema_v65 initial set; schema_v75/77 later additions).

ALTER TABLE sweep_log DROP CONSTRAINT IF EXISTS sweep_log_work_type_check;

ALTER TABLE sweep_log ADD CONSTRAINT sweep_log_work_type_check
    CHECK (work_type = ANY (ARRAY[
        'fact_recompute'::text,
        'overdue_followups'::text,
        'freshness_expiry'::text,
        'notification_delivery'::text,
        'engine_kick'::text,
        'cite_verification_overdue'::text,
        'api_key_expiring'::text,
        'notification_retention'::text,
        'risk_register_notify'::text,
        'posture_refresh'::text,
        'other'::text
    ]));
