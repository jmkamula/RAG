-- =============================================================================
-- schema_v30_drop_engine_proposal_bridge.sql
--
-- Phase 1c of the actor-model rework. Retires the
-- posture_controls.engine_proposed_finding + engine_proposal_reason "legacy
-- bridge" columns kept by Phase 1b for pre-1a terminal-lifecycle controls
-- (167-row regression scar on Arion 2026-06-03).
--
-- Phase 1b (commit de9b26e) made posture_assertions the canonical store for
-- engine verdicts: rag/posture_loader._persist_engine_proposals writes via
-- set_assertion(source='engine', status='pending', ...), and the Stage-2
-- readers (rag/posture/stage2_approval_chat + api_server.dashboard_posture)
-- JOIN PA-pending for the verdict. The PC.engine_proposed_* columns were
-- left in place as a read-side bridge for the 167 controls whose engine
-- proposal was already 'approved' at Phase 1a backfill time — those PCs had
-- no corresponding pending PA row because the 1a backfill only captured the
-- 'proposed' subset.
--
-- Phase 1c closes that hole by:
--   1. Backfilling a superseded engine PA row for any terminal-lifecycle PC
--      missing engine PA history (idempotent — on Arion 2026-06-03 the count
--      is zero because the 167-row recovery already wrote PA history).
--   2. Migrating readers/writers off PC.engine_proposed_* (separate code commit).
--   3. DROP COLUMN on the bridge columns.
--
-- Kept on posture_controls: engine_proposal_status (lifecycle), engine_
-- proposed_at (timestamp), engine_approved_by, engine_approved_at. These are
-- the lifecycle markers, not the verdict. The verdict (finding + reason +
-- set_at) lives in posture_assertions from here on.
--
-- Idempotent. Self-committing per [[sql-dry-run-nested-transaction]].
-- =============================================================================

BEGIN;

-- ───────── 1. Backfill safety net ─────────────────────────────────────────
-- For any approved/rejected PC with engine_proposed_finding NOT NULL but
-- NO engine PA row in any status, insert a superseded engine PA row capturing
-- the historical proposal. This makes the readers' "latest engine PA" lookup
-- safe across all tenants regardless of when their backfill ran.
--
-- On Arion: zero rows match (every terminal-lifecycle PC already has engine
-- PA history). On a fresh-from-Phase-1a tenant, this would backfill historical
-- proposals that pre-existed schema_v29.
--
-- Conflict guard: the partial unique indexes on PA active/pending allow only
-- one row per (tenant,control,std,source) in those statuses, but 'superseded'
-- has no uniqueness constraint, so the NOT EXISTS guard is the only thing
-- preventing double-inserts on re-runs.

INSERT INTO posture_assertions (
    tenant_id, control_ref, standard_id, source,
    finding, gap_description, confidence,
    set_by, set_at, status, superseded_at, metadata
)
SELECT
    pc.tenant_id,
    pc.control_ref,
    pc.standard_id,
    'engine'                                          AS source,
    pc.engine_proposed_finding                        AS finding,
    pc.engine_proposal_reason                         AS gap_description,
    pc.confidence,
    'backfill:schema_v30'                             AS set_by,
    COALESCE(pc.engine_proposed_at, pc.engine_approved_at, now()) AS set_at,
    'superseded'                                      AS status,
    COALESCE(pc.engine_approved_at, now())            AS superseded_at,
    jsonb_build_object(
        'posture_controls_id',      pc.id,
        'engine_proposal_status',   pc.engine_proposal_status,
        'live_finding_at_backfill', pc.finding,
        'backfill',                 true,
        'phase',                    '1c'
    )                                                 AS metadata
FROM posture_controls pc
WHERE pc.is_active = TRUE
  AND pc.engine_proposal_status IN ('approved','rejected')
  AND pc.engine_proposed_finding IS NOT NULL
  AND NOT EXISTS (
      SELECT 1 FROM posture_assertions pa
       WHERE pa.tenant_id   = pc.tenant_id
         AND pa.control_ref = pc.control_ref
         AND pa.standard_id = pc.standard_id
         AND pa.source      = 'engine'
  );

-- ───────── 2. Drop the bridge columns ─────────────────────────────────────
-- After this point, PC.engine_proposed_finding and PC.engine_proposal_reason
-- are gone. Any new code attempting to SELECT them will fail at psycopg2
-- query-time, which is the desired failure mode (loud, immediate). The
-- corresponding code migration in rag/posture_loader.py +
-- rag/posture/stage2_approval_chat.py + api_server.py lands in the same
-- commit.
--
-- Kept columns (lifecycle markers):
--   engine_proposal_status  text  -- 'none'|'proposed'|'approved'|'rejected'
--   engine_proposed_at      timestamptz
--   engine_approved_by      uuid
--   engine_approved_at      timestamptz

ALTER TABLE posture_controls
    DROP COLUMN IF EXISTS engine_proposed_finding,
    DROP COLUMN IF EXISTS engine_proposal_reason;

COMMIT;
