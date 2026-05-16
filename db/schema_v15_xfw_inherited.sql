-- =============================================================================
-- schema_v15_xfw_inherited.sql
--
-- Cross-framework posture inheritance plumbing.
--
-- 1. Allow relationship='implements' in standard_relationships.
-- 2. Seed ISO 27001:2022 -> GDPR:2016/679 implements (Annex A controls
--    implement parts of GDPR Art.32 etc — the bridge already exists at
--    the control-level IMPLEMENTS edges in Neo4j; this is the standards-
--    level signal the tenant_evaluation_scope view needs).
-- 3. Extend tenant_evaluation_scope with an xfw_inherited CTE so a tenant
--    enrolled only in ISO 27001 still has GDPR appear in scope, marked
--    scope_source='xfw_inherited'. Layer 2 in the answer pipeline then
--    inherits posture from the linked primary controls.
-- =============================================================================

BEGIN;

-- 1. Relax the relationship CHECK to add 'implements'
ALTER TABLE standard_relationships
    DROP CONSTRAINT IF EXISTS standard_relationships_relationship_check;

ALTER TABLE standard_relationships
    ADD CONSTRAINT standard_relationships_relationship_check
    CHECK (relationship = ANY (ARRAY[
        'extends'::text,
        'maps_to'::text,
        'requires'::text,
        'satisfies'::text,
        'references'::text,
        'implements'::text
    ]));

-- 2. Seed ISO 27001 -> GDPR 'implements'
INSERT INTO standard_relationships
    (source_id, target_id, relationship, mapping_source, coverage, notes)
VALUES
('ISO27001:2022', 'GDPR:2016/679', 'implements',
 'ISO 27001:2022 Annex A controls (Neo4j IMPLEMENTS edges)', 'partial',
 'ISO 27001 Annex A controls implement parts of GDPR (Art.32 security of processing, Art.28 processor obligations, etc). Control-level mapping lives in Neo4j; this row marks the standards-level relationship so GDPR appears in scope for tenants enrolled only in ISO 27001.')
ON CONFLICT (source_id, target_id, relationship) DO NOTHING;

-- 3. Replace tenant_evaluation_scope view with xfw_inherited CTE
CREATE OR REPLACE VIEW tenant_evaluation_scope AS
WITH
direct AS (
    SELECT
        ts.tenant_id,
        ts.standard_id,
        ts.status,
        s.standard_type,
        s.certifiable,
        'direct'::text  AS scope_source,
        ts.standard_id  AS via_standard,
        NULL::text      AS relationship
    FROM tenant_standards ts
    JOIN standards s ON s.id = ts.standard_id
    WHERE ts.status IN ('implementing','implemented','certified','surveillance')
),
inferred AS (
    SELECT
        d.tenant_id,
        sr.target_id     AS standard_id,
        d.status,
        s.standard_type,
        s.certifiable,
        'inferred'::text AS scope_source,
        d.standard_id    AS via_standard,
        sr.relationship  AS relationship
    FROM direct d
    JOIN standard_relationships sr ON sr.source_id = d.standard_id
    JOIN standards s ON s.id = sr.target_id
    WHERE sr.relationship IN ('maps_to', 'satisfies')
),
xfw_inherited AS (
    -- Control-level coverage: source standard's controls implement target
    -- standard's obligations (e.g. ISO 27001 Annex A implements GDPR Art.32).
    -- Suppressed when 'inferred' already covers the same (tenant, target).
    SELECT
        d.tenant_id,
        sr.target_id          AS standard_id,
        d.status,
        s.standard_type,
        s.certifiable,
        'xfw_inherited'::text AS scope_source,
        d.standard_id         AS via_standard,
        sr.relationship       AS relationship
    FROM direct d
    JOIN standard_relationships sr ON sr.source_id = d.standard_id
    JOIN standards s ON s.id = sr.target_id
    WHERE sr.relationship = 'implements'
      AND sr.target_id <> d.standard_id
      AND NOT EXISTS (
          SELECT 1
          FROM standard_relationships sr2
          WHERE sr2.source_id = d.standard_id
            AND sr2.target_id = sr.target_id
            AND sr2.relationship IN ('maps_to', 'satisfies')
      )
      AND NOT EXISTS (
          SELECT 1 FROM tenant_standards ts2
          WHERE ts2.tenant_id   = d.tenant_id
            AND ts2.standard_id = sr.target_id
            AND ts2.status IN ('implementing','implemented','certified','surveillance')
      )
)
SELECT * FROM direct
UNION ALL
SELECT * FROM inferred
UNION ALL
SELECT * FROM xfw_inherited;

GRANT SELECT ON tenant_evaluation_scope TO arioncomply_app;

COMMIT;
