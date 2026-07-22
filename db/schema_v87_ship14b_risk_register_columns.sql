-- schema_v87_ship14b_risk_register_columns.sql
--
-- Ship 14'.b (2026-07-22) — extend `risks` table with 5 columns
-- covering ISO 27005:2022 §8.6.1 treatment-plan elements not
-- present in the schema_v2 original.
--
-- 27005 §8.6.1 lists required treatment-plan elements. Existing
-- columns already cover:
--   ✅ owner              (risk_owner + risk_owner_text)
--   ✅ actions            (treatment_action)
--   ✅ status             (treatment_status)
--   ✅ implementation date (implementation_date)
--   ✅ residual level     (residual_risk_level)
--   ✅ review date        (review_date)
--   ✅ effectiveness      (effectiveness_review)
--
-- Missing coverage this migration adds:
--   ❌ treatment_rationale   — why this option was selected
--   ❌ resources_required    — budget / people / infrastructure
--   ❌ performance_indicators — KPIs per §8.6.1
--   ❌ constraints           — dependencies, timing gates
--   ❌ reporting_cadence     — how often status is reported
--
-- All NULL-permissive so the 35 existing rows on the demo tenant
-- (and any other tenants) don't need backfill. New uploads via
-- the canonical xlsx template populate them; older uploads
-- continue to work.
--
-- Framework role model discipline: this migration is standard-
-- agnostic — the columns describe treatment metadata regardless
-- of which controls (program / extension / obligation) the risk
-- references. `control_refs TEXT[]` already handles the
-- cross-role linkage.
--
-- Guidance-not-normative discipline: these are DATA columns for
-- what a tenant chooses to record about their treatment plan.
-- They are NOT new MUSTs on any leaf — no engine-verdict flip
-- risk.

BEGIN;

ALTER TABLE risks
    ADD COLUMN IF NOT EXISTS treatment_rationale     TEXT,
    ADD COLUMN IF NOT EXISTS resources_required      TEXT,
    ADD COLUMN IF NOT EXISTS performance_indicators  TEXT[],
    ADD COLUMN IF NOT EXISTS constraints             TEXT,
    ADD COLUMN IF NOT EXISTS reporting_cadence       TEXT;

-- Optional: comment the new columns so pg_dump / \d includes
-- their authority pointer.
COMMENT ON COLUMN risks.treatment_rationale IS
    '27005:2022 §8.6.1 — rationale for the selected treatment option, including expected benefits.';
COMMENT ON COLUMN risks.resources_required IS
    '27005:2022 §8.6.1 — resources required for implementation (budget / people / infrastructure).';
COMMENT ON COLUMN risks.performance_indicators IS
    '27005:2022 §8.6.1 — performance indicators (KPIs) that will demonstrate the treatment is effective.';
COMMENT ON COLUMN risks.constraints IS
    '27005:2022 §8.6.1 — dependencies, timing gates, or other constraints on treatment execution.';
COMMENT ON COLUMN risks.reporting_cadence IS
    '27005:2022 §8.6.1 — how often status is reported to risk owner and management.';

COMMIT;

-- Verification:
--   \d risks
-- Expected: 5 new columns visible, all NULL-permissive.

--   SELECT COUNT(*) FROM risks
--     WHERE treatment_rationale IS NOT NULL
--        OR resources_required IS NOT NULL
--        OR array_length(performance_indicators, 1) IS NOT NULL
--        OR constraints IS NOT NULL
--        OR reporting_cadence IS NOT NULL;
-- Expected: 0 (no backfill; new uploads only).
