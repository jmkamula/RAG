-- schema_v86_ship13e_iso27004_reenrollment.sql
--
-- Ship 13'.e (2026-07-22) — re-enroll ISO 27004:2016.
--
-- Ship 12'.b (schema_v84) enrolled `ISO27004:2016` as guidance.
-- Ship 13'.a (schema_v85) UN-enrolled it after discovering the
-- available PDF was 2009 first edition (edition mismatch).
-- Today the user landed the actual 2016 second edition PDF at
-- `/data/arioncomply/private/iso27004_2016.pdf`, unblocking the
-- deferred curation. This migration is a straight re-INSERT
-- symmetric to schema_v84's row for 27004 — no schema shape
-- change, purely a registry population.
--
-- Verification:
--   SELECT id, short_name, role FROM standards ORDER BY id;
-- Expected: 4 guidance rows —
--   ISO27002:2022 + ISO27003:2017 + ISO27004:2016 + ISO27005:2022.

BEGIN;

INSERT INTO standards (
    id, family, version, full_name, short_name,
    standard_type, certifiable, jurisdiction, description,
    loaded_in_graph, role, subject, scope_type
) VALUES (
    'ISO27004:2016',
    'ISO27004',
    '2016',
    'ISO/IEC 27004:2016 — Information security management — Monitoring, measurement, analysis and evaluation',
    'ISO 27004',
    'code_of_practice',
    false,
    'global',
    'Guidance on selecting, defining, presenting and using information-security performance and effectiveness metrics; supports ISO 27001 clause 9.1 and monitoring-adjacent Annex A controls.',
    false,
    'guidance',
    ARRAY['monitoring_and_measurement'],
    'org_wide'
)
ON CONFLICT (id) DO NOTHING;

COMMIT;
