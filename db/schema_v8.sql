-- =============================================================================
-- ArionComply — Schema v8
-- Drop dead columns from incidents + refresh v_incidents_open
--
-- Replaces the single `incident_type` text column with the
-- `incident_classifications` model introduced in schema_v7.sql. The two
-- `neo4j_*` columns were reserved for an abandoned design (project Incident
-- to Neo4j); under the locked architecture, :Incident is never projected to
-- Neo4j (instances live in Postgres only).
--
-- The view v_incidents_open expands `i.*`, so dropping any incidents column
-- requires dropping and recreating the view in the same migration. The view
-- itself stays — it remains useful for future dashboards even though no
-- Python code consumes it today.
--
-- Background: see memory/incident_obligations_model.md (locked design).
--
-- Coupled with: db/workbook_importer.py rewrite (same change-set) — the
-- importer now writes incident_classifications rows instead of an
-- incident_type string. Applying this migration without the importer change
-- will break next workbook import.
--
-- Apply:
--   psql arioncomply_compliance -f db/schema_v8.sql
-- =============================================================================

BEGIN;

-- ── Drop the view that pins the column dependencies ─────────────────────────
DROP VIEW IF EXISTS v_incidents_open;

-- ── Drop dead columns ───────────────────────────────────────────────────────
ALTER TABLE incidents DROP COLUMN IF EXISTS incident_type;
ALTER TABLE incidents DROP COLUMN IF EXISTS neo4j_synced;
ALTER TABLE incidents DROP COLUMN IF EXISTS neo4j_node_id;

-- ── Recreate v_incidents_open ───────────────────────────────────────────────
-- Same logical definition as before (deadline-aware projection of open
-- incidents). `i.*` will re-expand against the new column set, so the dropped
-- columns simply no longer appear.

CREATE VIEW v_incidents_open AS
SELECT
    i.*,
    CASE
        WHEN i.deadline_at IS NULL                        THEN NULL
        ELSE EXTRACT(EPOCH FROM (i.deadline_at - NOW())) / 3600
    END AS hours_remaining,
    CASE
        WHEN i.deadline_at IS NULL                        THEN 'no_deadline'
        WHEN i.deadline_at < NOW()                        THEN 'overdue'
        WHEN i.deadline_at < NOW() + INTERVAL '12 hours'  THEN 'critical'
        WHEN i.deadline_at < NOW() + INTERVAL '48 hours'  THEN 'urgent'
        WHEN i.deadline_at < NOW() + INTERVAL '7 days'    THEN 'soon'
        ELSE 'on_track'
    END AS urgency
FROM incidents i
WHERE i.status IN ('open','in_progress');

COMMIT;
