-- schema_v84_ship12b_iso27000_guidance_enrollment.sql
--
-- Ship 12'.b (2026-07-21) — enroll ISO 27003 / 27004 / 27005 as
-- guidance standards.
--
-- Populates the `standards` registry so downstream code paths
-- (chat citation format, external API standard_id lookups,
-- output-gateway vocabulary, Evidence Package authority strings)
-- recognise these standards even though full MUST-level
-- curation is deferred to Ship 13+ pending source texts.
--
-- No leaves, no nodes, no Neo4j sync — this is registry-only.
-- Ship 12'.c appends `[Guidance: ISO 27005:2022 §X]` citation
-- stubs to existing leaf business_description fields on the
-- 47 leaves enumerated in
-- ship_12_prime_a_iso27000_grounding_audit_2026_07_21.md.

BEGIN;

-- ISO/IEC 27003:2017 — Information security management systems —
-- Guidance.
INSERT INTO standards (
    id, family, version, full_name, short_name,
    standard_type, certifiable, jurisdiction, description,
    loaded_in_graph, role, subject, scope_type
) VALUES (
    'ISO27003:2017',
    'ISO27003',
    '2017',
    'ISO/IEC 27003:2017 — Information security management systems — Guidance',
    'ISO 27003',
    'code_of_practice',
    false,
    'global',
    'Implementation guidance for ISO 27001 management-system clauses (context, leadership, planning, support, operation, evaluation, improvement).',
    false,
    'guidance',
    ARRAY['information_security_management_system'],
    'org_wide'
)
ON CONFLICT (id) DO NOTHING;

-- ISO/IEC 27004:2016 — Monitoring, measurement, analysis and
-- evaluation.
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
    'Guidance on selecting, defining, presenting and using information-security performance metrics + supporting the ISO 27001 9.1 monitoring/measurement clause.',
    false,
    'guidance',
    ARRAY['monitoring_and_measurement'],
    'org_wide'
)
ON CONFLICT (id) DO NOTHING;

-- ISO/IEC 27005:2022 — Information security risk management.
INSERT INTO standards (
    id, family, version, full_name, short_name,
    standard_type, certifiable, jurisdiction, description,
    loaded_in_graph, role, subject, scope_type
) VALUES (
    'ISO27005:2022',
    'ISO27005',
    '2022',
    'ISO/IEC 27005:2022 — Guidance on managing information security risks',
    'ISO 27005',
    'code_of_practice',
    false,
    'global',
    'Guidance on the information-security risk management process supporting ISO 27001 6.1 / 8.2 / 8.3 (risk assessment methodology, treatment options, acceptance criteria, register schema).',
    false,
    'guidance',
    ARRAY['risk_management'],
    'org_wide'
)
ON CONFLICT (id) DO NOTHING;

COMMIT;

-- Verification (run manually):
--   SELECT id, short_name, role, standard_type
--     FROM standards
--    WHERE role = 'guidance'
--    ORDER BY id;
-- Expected: 4 rows — ISO27002:2022 + ISO27003:2017 +
-- ISO27004:2016 + ISO27005:2022.
